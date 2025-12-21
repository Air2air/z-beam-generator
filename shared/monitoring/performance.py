"""
Performance Monitoring

Tracks operation timing and resource usage for the Z-Beam Generator.
Provides insights into bottlenecks and optimization opportunities.

Usage:
    from shared.monitoring.performance import PerformanceMonitor
    
    # Context manager (automatic timing)
    with PerformanceMonitor("export_materials") as pm:
        exporter.export_all()
    
    # Manual control
    pm = PerformanceMonitor("complex_operation")
    pm.start()
    # ... operation ...
    pm.checkpoint("phase_1_complete")
    # ... more work ...
    pm.stop()
    pm.print_report()

Created: December 20, 2025
"""

import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@dataclass
class Checkpoint:
    """Performance checkpoint"""
    name: str
    timestamp: float
    elapsed_from_start: float
    elapsed_from_previous: float
    memory_mb: Optional[float] = None


@dataclass
class PerformanceMetrics:
    """Complete performance metrics for an operation"""
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    total_duration: Optional[float] = None
    checkpoints: List[Checkpoint] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> float:
        """Total duration in seconds"""
        if self.total_duration is not None:
            return self.total_duration
        if self.end_time is not None:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    @property
    def is_complete(self) -> bool:
        """Whether operation has completed"""
        return self.end_time is not None


class PerformanceMonitor:
    """
    Performance monitoring context manager.
    
    Tracks operation timing, checkpoints, and resource usage.
    """
    
    def __init__(self, operation_name: str, auto_log: bool = True):
        """
        Initialize performance monitor.
        
        Args:
            operation_name: Name of operation being monitored
            auto_log: Whether to automatically log results
        """
        self.operation_name = operation_name
        self.auto_log = auto_log
        self.metrics: Optional[PerformanceMetrics] = None
        self._last_checkpoint_time: Optional[float] = None
    
    def start(self):
        """Start monitoring"""
        self.metrics = PerformanceMetrics(
            operation_name=self.operation_name,
            start_time=time.time()
        )
        self._last_checkpoint_time = self.metrics.start_time
        
        logger.debug(f"Performance monitoring started: {self.operation_name}")
    
    def checkpoint(self, name: str, metadata: Optional[Dict] = None):
        """
        Record a checkpoint.
        
        Args:
            name: Checkpoint name
            metadata: Additional metadata
        """
        if self.metrics is None:
            raise RuntimeError("Monitor not started. Call start() first.")
        
        now = time.time()
        elapsed_from_start = now - self.metrics.start_time
        elapsed_from_previous = now - self._last_checkpoint_time
        
        # Try to get memory usage
        memory_mb = None
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
        except:
            pass
        
        checkpoint = Checkpoint(
            name=name,
            timestamp=now,
            elapsed_from_start=elapsed_from_start,
            elapsed_from_previous=elapsed_from_previous,
            memory_mb=memory_mb
        )
        
        self.metrics.checkpoints.append(checkpoint)
        self._last_checkpoint_time = now
        
        if metadata:
            self.metrics.metadata.update(metadata)
        
        logger.debug(f"Checkpoint '{name}': +{elapsed_from_previous:.2f}s (total: {elapsed_from_start:.2f}s)")
    
    def stop(self):
        """Stop monitoring"""
        if self.metrics is None:
            raise RuntimeError("Monitor not started. Call start() first.")
        
        self.metrics.end_time = time.time()
        self.metrics.total_duration = self.metrics.end_time - self.metrics.start_time
        
        logger.info(f"Performance monitoring complete: {self.operation_name} ({self.metrics.total_duration:.2f}s)")
        
        if self.auto_log:
            self.print_report()
    
    def print_report(self, show_memory: bool = False):
        """
        Print performance report.
        
        Args:
            show_memory: Whether to show memory usage
        """
        if self.metrics is None:
            print("⚠️  No metrics recorded")
            return
        
        print(f"\n{'='*80}")
        print(f"📊 PERFORMANCE REPORT: {self.operation_name}")
        print(f"{'='*80}")
        print(f"⏱️  Total Duration: {self.metrics.duration_seconds:.2f}s")
        
        if self.metrics.checkpoints:
            print(f"\n📍 Checkpoints:")
            for cp in self.metrics.checkpoints:
                memory_str = f" | {cp.memory_mb:.1f} MB" if show_memory and cp.memory_mb else ""
                print(f"  {cp.name:30s} +{cp.elapsed_from_previous:6.2f}s (total: {cp.elapsed_from_start:6.2f}s){memory_str}")
        
        if self.metrics.metadata:
            print(f"\n📋 Metadata:")
            for key, value in self.metrics.metadata.items():
                print(f"  {key}: {value}")
        
        print(f"{'='*80}\n")
    
    def get_metrics(self) -> PerformanceMetrics:
        """Get metrics object"""
        if self.metrics is None:
            raise RuntimeError("Monitor not started. Call start() first.")
        return self.metrics
    
    # Context manager methods
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False


# Global performance tracker
_performance_tracker: Dict[str, List[PerformanceMetrics]] = {}


def track_performance(operation_name: str, metrics: PerformanceMetrics):
    """Add metrics to global tracker"""
    if operation_name not in _performance_tracker:
        _performance_tracker[operation_name] = []
    _performance_tracker[operation_name].append(metrics)


def get_performance_history(operation_name: str) -> List[PerformanceMetrics]:
    """Get performance history for an operation"""
    return _performance_tracker.get(operation_name, [])


def get_performance_summary() -> Dict:
    """Get summary of all tracked operations"""
    summary = {}
    
    for op_name, metrics_list in _performance_tracker.items():
        if not metrics_list:
            continue
        
        durations = [m.duration_seconds for m in metrics_list if m.is_complete]
        if not durations:
            continue
        
        summary[op_name] = {
            'count': len(durations),
            'total_time': sum(durations),
            'avg_time': sum(durations) / len(durations),
            'min_time': min(durations),
            'max_time': max(durations)
        }
    
    return summary


def print_performance_summary():
    """Print summary of all tracked operations"""
    summary = get_performance_summary()
    
    if not summary:
        print("No performance data recorded")
        return
    
    print(f"\n{'='*80}")
    print("📊 PERFORMANCE SUMMARY")
    print(f"{'='*80}")
    
    for op_name in sorted(summary.keys()):
        stats = summary[op_name]
        print(f"\n{op_name}:")
        print(f"  Count: {stats['count']}")
        print(f"  Total: {stats['total_time']:.2f}s")
        print(f"  Average: {stats['avg_time']:.2f}s")
        print(f"  Min: {stats['min_time']:.2f}s")
        print(f"  Max: {stats['max_time']:.2f}s")
    
    print(f"{'='*80}\n")


@contextmanager
def monitor_performance(operation_name: str, auto_log: bool = True, track: bool = True):
    """
    Convenience context manager for performance monitoring.
    
    Args:
        operation_name: Name of operation
        auto_log: Whether to automatically log results
        track: Whether to add to global tracker
    
    Usage:
        with monitor_performance("export_materials"):
            exporter.export_all()
    """
    pm = PerformanceMonitor(operation_name, auto_log=auto_log)
    pm.start()
    
    try:
        yield pm
    finally:
        pm.stop()
        
        if track:
            track_performance(operation_name, pm.get_metrics())
