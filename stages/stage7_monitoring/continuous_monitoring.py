#!/usr/bin/env python3
"""
Stage 7: Continuous Monitoring
Implements ongoing monitoring and alerting for material property data quality.
"""

import yaml
import json
import time
import schedule
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import statistics
import hashlib

class ContinuousMonitor:
    """
    Provides continuous monitoring of material property data quality,
    detecting changes, anomalies, and degradation over time.
    """
    
    def __init__(self):
        self.frontmatter_dir = Path("content/components/frontmatter")
        self.config_file = Path("config/pipeline_config.yaml")
        self.monitoring_dir = Path("monitoring")
        self.alerts_dir = Path("monitoring/alerts")
        self.metrics_dir = Path("monitoring/metrics")
        self.reports_dir = Path("monitoring/reports")
        
        # Create monitoring directories
        self._setup_monitoring_directories()
        
        # Load monitoring configuration
        self.monitoring_config = self._load_monitoring_config()
        
        # Monitoring state
        self.baseline_metrics = {}
        self.current_metrics = {}
        self.alert_history = []
        self.monitoring_active = False
        
        # Load existing baseline if available
        self._load_baseline_metrics()
        
        # Statistics tracking
        self.monitoring_stats = {
            'monitoring_cycles': 0,
            'alerts_generated': 0,
            'anomalies_detected': 0,
            'files_monitored': 0,
            'last_monitoring_run': None,
            'errors': []
        }
    
    def _setup_monitoring_directories(self):
        """Create monitoring directory structure"""
        
        self.monitoring_dir.mkdir(exist_ok=True)
        self.alerts_dir.mkdir(exist_ok=True)
        self.metrics_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
    
    def _load_monitoring_config(self) -> Dict[str, Any]:
        """Load monitoring configuration"""
        
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            return config.get('continuous_monitoring', {
                'monitoring_intervals': {
                    'quick_check': '15m',
                    'full_scan': '4h',
                    'quality_assessment': '24h',
                    'trend_analysis': '7d'
                },
                'alert_thresholds': {
                    'quality_score_drop': 0.1,
                    'property_variance_increase': 0.2,
                    'missing_files_threshold': 1,
                    'schema_violations': 1,
                    'anomaly_score_threshold': 0.8
                },
                'monitoring_scope': {
                    'track_quality_trends': True,
                    'detect_data_drift': True,
                    'monitor_completeness': True,
                    'watch_for_anomalies': True,
                    'performance_monitoring': True
                },
                'notification_settings': {
                    'alert_channels': ['file', 'log'],
                    'alert_levels': ['critical', 'warning', 'info'],
                    'consolidation_window': '1h'
                }
            })
            
        except Exception as e:
            print(f"⚠️  Could not load monitoring config: {e}")
            return self._get_default_monitoring_config()
    
    def _get_default_monitoring_config(self) -> Dict[str, Any]:
        """Default monitoring configuration"""
        
        return {
            'monitoring_intervals': {
                'quick_check': '15m',
                'full_scan': '4h',
                'quality_assessment': '24h',
                'trend_analysis': '7d'
            },
            'alert_thresholds': {
                'quality_score_drop': 0.1,
                'property_variance_increase': 0.2,
                'missing_files_threshold': 1,
                'schema_violations': 1,
                'anomaly_score_threshold': 0.8
            },
            'monitoring_scope': {
                'track_quality_trends': True,
                'detect_data_drift': True,
                'monitor_completeness': True,
                'watch_for_anomalies': True,
                'performance_monitoring': True
            },
            'notification_settings': {
                'alert_channels': ['file', 'log'],
                'alert_levels': ['critical', 'warning', 'info'],
                'consolidation_window': '1h'
            }
        }
    
    def start_monitoring(self, run_once: bool = False) -> Dict[str, Any]:
        """
        Start continuous monitoring of material property data.
        
        Args:
            run_once: If True, run monitoring once and exit. If False, run continuously.
            
        Returns:
            Monitoring results and status
        """
        
        print("🔍 Starting continuous monitoring system...")
        
        if run_once:
            return self._run_monitoring_cycle()
        else:
            return self._start_continuous_monitoring()
    
    def _start_continuous_monitoring(self) -> Dict[str, Any]:
        """Start continuous monitoring with scheduled intervals"""
        
        # Schedule monitoring tasks
        schedule.every(15).minutes.do(self._quick_check)
        schedule.every(4).hours.do(self._full_scan)
        schedule.every(24).hours.do(self._quality_assessment)
        schedule.every(7).days.do(self._trend_analysis)
        
        self.monitoring_active = True
        
        print("🔍 Continuous monitoring started with scheduled intervals:")
        print("  📊 Quick check: every 15 minutes")
        print("  🔍 Full scan: every 4 hours")  
        print("  🎯 Quality assessment: every 24 hours")
        print("  📈 Trend analysis: every 7 days")
        
        monitoring_summary = {
            'status': 'monitoring_started',
            'monitoring_active': True,
            'scheduled_tasks': {
                'quick_check': 'every 15 minutes',
                'full_scan': 'every 4 hours',
                'quality_assessment': 'every 24 hours',
                'trend_analysis': 'every 7 days'
            },
            'start_timestamp': datetime.now().isoformat()
        }
        
        # Run initial monitoring cycle
        initial_results = self._run_monitoring_cycle()
        monitoring_summary['initial_results'] = initial_results
        
        # Main monitoring loop (in practice, this would run as a service)
        print("🔄 Monitoring loop started (press Ctrl+C to stop)")
        try:
            while self.monitoring_active:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            self.monitoring_active = False
            monitoring_summary['status'] = 'monitoring_stopped'
            monitoring_summary['stop_timestamp'] = datetime.now().isoformat()
        
        return monitoring_summary
    
    def _run_monitoring_cycle(self) -> Dict[str, Any]:
        """Run a complete monitoring cycle"""
        
        cycle_start = datetime.now()
        
        print(f"🔍 Running monitoring cycle at {cycle_start.isoformat()}")
        
        cycle_results = {
            'cycle_timestamp': cycle_start.isoformat(),
            'monitoring_components': {},
            'alerts_generated': [],
            'metrics_collected': {},
            'anomalies_detected': [],
            'summary': {}
        }
        
        try:
            # Collect current metrics
            current_metrics = self._collect_current_metrics()
            cycle_results['metrics_collected'] = current_metrics
            
            # Update baseline if first run
            if not self.baseline_metrics:
                self.baseline_metrics = current_metrics
                self._save_baseline_metrics()
                print("📊 Baseline metrics established")
            
            # Run monitoring components
            if self.monitoring_config['monitoring_scope']['track_quality_trends']:
                quality_monitoring = self._monitor_quality_trends(current_metrics)
                cycle_results['monitoring_components']['quality_trends'] = quality_monitoring
                cycle_results['alerts_generated'].extend(quality_monitoring.get('alerts', []))
            
            if self.monitoring_config['monitoring_scope']['detect_data_drift']:
                drift_monitoring = self._detect_data_drift(current_metrics)
                cycle_results['monitoring_components']['data_drift'] = drift_monitoring
                cycle_results['alerts_generated'].extend(drift_monitoring.get('alerts', []))
            
            if self.monitoring_config['monitoring_scope']['monitor_completeness']:
                completeness_monitoring = self._monitor_completeness(current_metrics)
                cycle_results['monitoring_components']['completeness'] = completeness_monitoring
                cycle_results['alerts_generated'].extend(completeness_monitoring.get('alerts', []))
            
            if self.monitoring_config['monitoring_scope']['watch_for_anomalies']:
                anomaly_monitoring = self._detect_anomalies(current_metrics)
                cycle_results['monitoring_components']['anomalies'] = anomaly_monitoring
                cycle_results['alerts_generated'].extend(anomaly_monitoring.get('alerts', []))
                cycle_results['anomalies_detected'] = anomaly_monitoring.get('anomalies', [])
            
            # Process alerts
            if cycle_results['alerts_generated']:
                self._process_alerts(cycle_results['alerts_generated'])
            
            # Update monitoring statistics
            self.monitoring_stats['monitoring_cycles'] += 1
            self.monitoring_stats['alerts_generated'] += len(cycle_results['alerts_generated'])
            self.monitoring_stats['anomalies_detected'] += len(cycle_results['anomalies_detected'])
            self.monitoring_stats['last_monitoring_run'] = cycle_start.isoformat()
            
            # Generate cycle summary
            cycle_results['summary'] = self._generate_cycle_summary(cycle_results)
            
            # Save monitoring results
            self._save_monitoring_results(cycle_results)
            
            print(f"✅ Monitoring cycle complete: {len(cycle_results['alerts_generated'])} alerts, {len(cycle_results['anomalies_detected'])} anomalies")
            
        except Exception as e:
            error_msg = f"Error in monitoring cycle: {e}"
            self.monitoring_stats['errors'].append(error_msg)
            cycle_results['error'] = error_msg
            print(f"❌ {error_msg}")
        
        return cycle_results
    
    def _collect_current_metrics(self) -> Dict[str, Any]:
        """Collect current metrics from material property data"""
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'file_metrics': {},
            'property_metrics': {},
            'quality_metrics': {},
            'system_metrics': {}
        }
        
        # File-level metrics
        material_files = list(self.frontmatter_dir.glob("*.yaml"))
        metrics['file_metrics'] = {
            'total_files': len(material_files),
            'file_sizes': {},
            'file_checksums': {},
            'last_modified': {}
        }
        
        # Property-level metrics
        all_properties = set()
        property_counts = {}
        property_values = {}
        
        for yaml_file in material_files:
            try:
                material_name = yaml_file.stem.replace("-laser-cleaning", "")
                
                # File metrics
                file_stat = yaml_file.stat()
                metrics['file_metrics']['file_sizes'][material_name] = file_stat.st_size
                metrics['file_metrics']['last_modified'][material_name] = file_stat.st_mtime
                metrics['file_metrics']['file_checksums'][material_name] = self._calculate_file_checksum(yaml_file)
                
                # Load material data
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                # Property metrics
                properties = data.get('materialProperties', {})
                for prop_name, prop_data in properties.items():
                    all_properties.add(prop_name)
                    property_counts[prop_name] = property_counts.get(prop_name, 0) + 1
                    
                    if isinstance(prop_data, dict) and 'value' in prop_data:
                        if prop_name not in property_values:
                            property_values[prop_name] = []
                        try:
                            value = float(prop_data['value'])
                            property_values[prop_name].append(value)
                        except (ValueError, TypeError):
                            pass
                
                self.monitoring_stats['files_monitored'] += 1
                
            except Exception as e:
                self.monitoring_stats['errors'].append(f"Error processing {yaml_file}: {e}")
        
        # Calculate property statistics
        metrics['property_metrics'] = {
            'unique_properties': len(all_properties),
            'property_usage_counts': property_counts,
            'property_statistics': {}
        }
        
        for prop_name, values in property_values.items():
            if len(values) >= 2:
                metrics['property_metrics']['property_statistics'][prop_name] = {
                    'count': len(values),
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'std_dev': statistics.stdev(values),
                    'min': min(values),
                    'max': max(values),
                    'variance': statistics.variance(values)
                }
        
        # Quality metrics (simplified)
        metrics['quality_metrics'] = {
            'completeness_rate': self._calculate_completeness_rate(),
            'consistency_score': self._calculate_consistency_score(),
            'average_confidence': self._calculate_average_confidence()
        }
        
        # System metrics
        metrics['system_metrics'] = {
            'monitoring_uptime': self.monitoring_stats['monitoring_cycles'],
            'total_alerts': self.monitoring_stats['alerts_generated'],
            'error_count': len(self.monitoring_stats['errors'])
        }
        
        return metrics
    
    def _monitor_quality_trends(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor quality trends over time"""
        
        monitoring_result = {
            'component': 'quality_trends',
            'status': 'healthy',
            'alerts': [],
            'trends': {},
            'analysis': {}
        }
        
        if not self.baseline_metrics:
            monitoring_result['status'] = 'no_baseline'
            return monitoring_result
        
        # Compare quality metrics
        current_quality = current_metrics.get('quality_metrics', {})
        baseline_quality = self.baseline_metrics.get('quality_metrics', {})
        
        alert_threshold = self.monitoring_config['alert_thresholds']['quality_score_drop']
        
        for metric_name, current_value in current_quality.items():
            baseline_value = baseline_quality.get(metric_name, current_value)
            
            if isinstance(current_value, (int, float)) and isinstance(baseline_value, (int, float)):
                change = current_value - baseline_value
                change_percent = (change / baseline_value) if baseline_value != 0 else 0
                
                monitoring_result['trends'][metric_name] = {
                    'current': current_value,
                    'baseline': baseline_value,
                    'change': change,
                    'change_percent': change_percent
                }
                
                # Check for significant drops
                if change < -alert_threshold:
                    alert = {
                        'type': 'quality_degradation',
                        'severity': 'warning' if abs(change) < 0.2 else 'critical',
                        'metric': metric_name,
                        'current_value': current_value,
                        'baseline_value': baseline_value,
                        'change': change,
                        'message': f"Quality metric {metric_name} dropped by {abs(change):.3f} ({change_percent:.1%})",
                        'timestamp': datetime.now().isoformat()
                    }
                    monitoring_result['alerts'].append(alert)
                    monitoring_result['status'] = 'degradation_detected'
        
        return monitoring_result
    
    def _detect_data_drift(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Detect data drift in property values"""
        
        monitoring_result = {
            'component': 'data_drift',
            'status': 'stable',
            'alerts': [],
            'drift_analysis': {},
            'property_changes': {}
        }
        
        if not self.baseline_metrics:
            monitoring_result['status'] = 'no_baseline'
            return monitoring_result
        
        current_prop_stats = current_metrics.get('property_metrics', {}).get('property_statistics', {})
        baseline_prop_stats = self.baseline_metrics.get('property_metrics', {}).get('property_statistics', {})
        
        variance_threshold = self.monitoring_config['alert_thresholds']['property_variance_increase']
        
        for prop_name, current_stats in current_prop_stats.items():
            if prop_name not in baseline_prop_stats:
                continue
            
            baseline_stats = baseline_prop_stats[prop_name]
            
            # Check for variance changes
            current_variance = current_stats.get('variance', 0)
            baseline_variance = baseline_stats.get('variance', 0)
            
            if baseline_variance > 0:
                variance_change = (current_variance - baseline_variance) / baseline_variance
                
                monitoring_result['property_changes'][prop_name] = {
                    'variance_change': variance_change,
                    'mean_shift': current_stats.get('mean', 0) - baseline_stats.get('mean', 0),
                    'count_change': current_stats.get('count', 0) - baseline_stats.get('count', 0)
                }
                
                if variance_change > variance_threshold:
                    alert = {
                        'type': 'data_drift',
                        'severity': 'warning',
                        'property': prop_name,
                        'variance_change': variance_change,
                        'message': f"Property {prop_name} shows increased variance ({variance_change:.1%})",
                        'timestamp': datetime.now().isoformat()
                    }
                    monitoring_result['alerts'].append(alert)
                    monitoring_result['status'] = 'drift_detected'
        
        return monitoring_result
    
    def _monitor_completeness(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor data completeness"""
        
        monitoring_result = {
            'component': 'completeness',
            'status': 'complete',
            'alerts': [],
            'completeness_analysis': {},
            'missing_data': []
        }
        
        # Check file count changes
        current_file_count = current_metrics.get('file_metrics', {}).get('total_files', 0)
        baseline_file_count = self.baseline_metrics.get('file_metrics', {}).get('total_files', current_file_count)
        
        missing_files = baseline_file_count - current_file_count
        missing_threshold = self.monitoring_config['alert_thresholds']['missing_files_threshold']
        
        if missing_files > missing_threshold:
            alert = {
                'type': 'missing_files',
                'severity': 'critical',
                'missing_count': missing_files,
                'current_count': current_file_count,
                'baseline_count': baseline_file_count,
                'message': f"{missing_files} material files are missing from baseline",
                'timestamp': datetime.now().isoformat()
            }
            monitoring_result['alerts'].append(alert)
            monitoring_result['status'] = 'incomplete'
        
        # Check property completeness
        current_completeness = current_metrics.get('quality_metrics', {}).get('completeness_rate', 1.0)
        baseline_completeness = self.baseline_metrics.get('quality_metrics', {}).get('completeness_rate', current_completeness)
        
        completeness_drop = baseline_completeness - current_completeness
        
        if completeness_drop > 0.05:  # 5% drop threshold
            alert = {
                'type': 'completeness_degradation',
                'severity': 'warning',
                'current_rate': current_completeness,
                'baseline_rate': baseline_completeness,
                'drop': completeness_drop,
                'message': f"Data completeness dropped by {completeness_drop:.1%}",
                'timestamp': datetime.now().isoformat()
            }
            monitoring_result['alerts'].append(alert)
            monitoring_result['status'] = 'degraded'
        
        monitoring_result['completeness_analysis'] = {
            'current_file_count': current_file_count,
            'baseline_file_count': baseline_file_count,
            'current_completeness_rate': current_completeness,
            'baseline_completeness_rate': baseline_completeness
        }
        
        return monitoring_result
    
    def _detect_anomalies(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies in current data"""
        
        monitoring_result = {
            'component': 'anomaly_detection',
            'status': 'normal',
            'alerts': [],
            'anomalies': [],
            'anomaly_scores': {}
        }
        
        # Simple anomaly detection based on statistical outliers
        property_stats = current_metrics.get('property_metrics', {}).get('property_statistics', {})
        anomaly_threshold = self.monitoring_config['alert_thresholds']['anomaly_score_threshold']
        
        for prop_name, stats in property_stats.items():
            if stats.get('count', 0) < 5:  # Need enough data points
                continue
            
            mean = stats.get('mean', 0)
            std_dev = stats.get('std_dev', 0)
            
            if std_dev == 0:
                continue
            
            # Calculate z-scores for min/max values
            min_val = stats.get('min', mean)
            max_val = stats.get('max', mean)
            
            min_z_score = abs((min_val - mean) / std_dev) if std_dev > 0 else 0
            max_z_score = abs((max_val - mean) / std_dev) if std_dev > 0 else 0
            
            max_z_score = max(min_z_score, max_z_score)
            
            monitoring_result['anomaly_scores'][prop_name] = max_z_score
            
            if max_z_score > 3.0:  # 3-sigma rule
                anomaly = {
                    'property': prop_name,
                    'anomaly_type': 'statistical_outlier',
                    'z_score': max_z_score,
                    'extreme_value': max_val if max_z_score == (max_val - mean) / std_dev else min_val,
                    'timestamp': datetime.now().isoformat()
                }
                monitoring_result['anomalies'].append(anomaly)
                
                if max_z_score > 4.0:  # Very extreme
                    alert = {
                        'type': 'anomaly_detected',
                        'severity': 'warning',
                        'property': prop_name,
                        'z_score': max_z_score,
                        'message': f"Statistical anomaly detected in {prop_name} (z-score: {max_z_score:.1f})",
                        'timestamp': datetime.now().isoformat()
                    }
                    monitoring_result['alerts'].append(alert)
                    monitoring_result['status'] = 'anomalies_detected'
        
        return monitoring_result
    
    def _process_alerts(self, alerts: List[Dict[str, Any]]):
        """Process and handle generated alerts"""
        
        for alert in alerts:
            # Add alert to history
            self.alert_history.append(alert)
            
            # Save alert to file
            self._save_alert(alert)
            
            # Log alert
            severity = alert.get('severity', 'info')
            message = alert.get('message', 'Unknown alert')
            timestamp = alert.get('timestamp', datetime.now().isoformat())
            
            print(f"🚨 [{severity.upper()}] {timestamp}: {message}")
    
    def _save_alert(self, alert: Dict[str, Any]):
        """Save alert to alert file"""
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d")
            alert_file = self.alerts_dir / f"alerts_{timestamp}.json"
            
            # Load existing alerts
            alerts = []
            if alert_file.exists():
                with open(alert_file, 'r') as f:
                    alerts = json.load(f)
            
            # Add new alert
            alerts.append(alert)
            
            # Save updated alerts
            with open(alert_file, 'w') as f:
                json.dump(alerts, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  Error saving alert: {e}")
    
    def _quick_check(self):
        """Perform quick monitoring check"""
        print("⚡ Running quick check...")
        # Simplified monitoring for frequent checks
        pass
    
    def _full_scan(self):
        """Perform full monitoring scan"""
        print("🔍 Running full scan...")
        self._run_monitoring_cycle()
    
    def _quality_assessment(self):
        """Perform comprehensive quality assessment"""
        print("🎯 Running quality assessment...")
        # More detailed quality analysis
        pass
    
    def _trend_analysis(self):
        """Perform trend analysis"""
        print("📈 Running trend analysis...")
        # Analyze trends over longer periods
        pass
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum for a file"""
        
        hash_sha256 = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return "error_calculating_checksum"
    
    def _calculate_completeness_rate(self) -> float:
        """Calculate overall data completeness rate"""
        
        total_properties = 0
        complete_properties = 0
        
        for yaml_file in self.frontmatter_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                properties = data.get('materialProperties', {})
                for prop_name, prop_data in properties.items():
                    total_properties += 1
                    
                    if isinstance(prop_data, dict):
                        required_fields = ['value', 'unit', 'min', 'max']
                        if all(field in prop_data and prop_data[field] is not None for field in required_fields):
                            complete_properties += 1
                    
            except Exception:
                continue
        
        return complete_properties / total_properties if total_properties > 0 else 0.0
    
    def _calculate_consistency_score(self) -> float:
        """Calculate overall data consistency score"""
        
        # Simplified consistency calculation
        # In practice, this would be more sophisticated
        return 0.85  # Placeholder
    
    def _calculate_average_confidence(self) -> float:
        """Calculate average confidence score"""
        
        confidences = []
        
        for yaml_file in self.frontmatter_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                properties = data.get('materialProperties', {})
                for prop_name, prop_data in properties.items():
                    if isinstance(prop_data, dict) and 'confidence' in prop_data:
                        confidence = prop_data['confidence']
                        if isinstance(confidence, (int, float)):
                            confidences.append(confidence)
                    
            except Exception:
                continue
        
        return statistics.mean(confidences) if confidences else 0.5
    
    def _load_baseline_metrics(self):
        """Load existing baseline metrics"""
        
        baseline_file = self.monitoring_dir / "baseline_metrics.json"
        
        try:
            if baseline_file.exists():
                with open(baseline_file, 'r') as f:
                    self.baseline_metrics = json.load(f)
                print("📊 Loaded existing baseline metrics")
        except Exception as e:
            print(f"⚠️  Error loading baseline metrics: {e}")
            self.baseline_metrics = {}
    
    def _save_baseline_metrics(self):
        """Save baseline metrics"""
        
        baseline_file = self.monitoring_dir / "baseline_metrics.json"
        
        try:
            with open(baseline_file, 'w') as f:
                json.dump(self.baseline_metrics, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving baseline metrics: {e}")
    
    def _save_monitoring_results(self, results: Dict[str, Any]):
        """Save monitoring results"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.metrics_dir / f"monitoring_results_{timestamp}.json"
        
        try:
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
        except Exception as e:
            print(f"⚠️  Error saving monitoring results: {e}")
    
    def _generate_cycle_summary(self, cycle_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary for monitoring cycle"""
        
        return {
            'cycle_duration': 'calculated_duration',
            'components_run': len(cycle_results.get('monitoring_components', {})),
            'alerts_generated': len(cycle_results.get('alerts_generated', [])),
            'anomalies_detected': len(cycle_results.get('anomalies_detected', [])),
            'overall_status': 'healthy' if not cycle_results.get('alerts_generated') else 'needs_attention',
            'next_monitoring_cycle': 'scheduled'
        }

def main():
    """Test the continuous monitoring functionality"""
    
    monitor = ContinuousMonitor()
    
    # Run single monitoring cycle for testing
    results = monitor.start_monitoring(run_once=True)
    
    # Save results
    results_dir = Path("pipeline_results")
    results_dir.mkdir(exist_ok=True)
    
    with open(results_dir / "stage7_continuous_monitoring_results.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n" + "="*60)
    print("🔍 CONTINUOUS MONITORING STAGE COMPLETE")
    print("="*60)
    print(f"Monitoring cycle completed")
    print(f"Alerts generated: {len(results.get('alerts_generated', []))}")
    print(f"Anomalies detected: {len(results.get('anomalies_detected', []))}")
    print(f"Files monitored: {monitor.monitoring_stats['files_monitored']}")
    
    if results.get('alerts_generated'):
        print("\nAlerts generated:")
        for alert in results['alerts_generated']:
            severity = alert.get('severity', 'info')
            message = alert.get('message', 'Unknown alert')
            print(f"  🚨 [{severity.upper()}] {message}")

if __name__ == "__main__":
    main()