"""
Generation Chain Verification System

Ensures that all critical modules in the generation pipeline are executed
and prevents accidental skipping of validation, enrichment, or learning steps.

This system uses decorators and a central registry to track execution flow.
"""

import logging
import functools
from typing import Dict, Set, Callable, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


class ChainPhase(Enum):
    """Generation pipeline phases"""
    INITIALIZATION = "initialization"
    DATA_LOADING = "data_loading"
    ENRICHMENT = "enrichment"
    VOICE_INJECTION = "voice_injection"
    PROMPT_BUILDING = "prompt_building"
    TEMPERATURE_ADAPTATION = "temperature_adaptation"
    API_GENERATION = "api_generation"
    AI_DETECTION = "ai_detection"
    READABILITY_VALIDATION = "readability_validation"
    CONTENT_EXTRACTION = "content_extraction"
    DATA_PERSISTENCE = "data_persistence"
    LEARNING_FEEDBACK = "learning_feedback"


@dataclass
class ChainExecution:
    """Tracks a single generation chain execution"""
    session_id: str
    identifier: str  # material/region/application name
    component_type: str
    started_at: datetime
    completed_phases: Set[ChainPhase] = field(default_factory=set)
    skipped_phases: Set[ChainPhase] = field(default_factory=set)
    errors: Dict[ChainPhase, str] = field(default_factory=dict)
    completed_at: Optional[datetime] = None
    success: bool = False


class ChainRegistry:
    """
    Central registry tracking generation chain executions.
    
    Ensures all critical phases are executed and flags any skipped steps.
    """
    
    _instance = None
    _executions: Dict[str, ChainExecution] = {}
    _required_phases: Set[ChainPhase] = {
        ChainPhase.DATA_LOADING,
        ChainPhase.ENRICHMENT,
        ChainPhase.PROMPT_BUILDING,
        ChainPhase.API_GENERATION,
        ChainPhase.AI_DETECTION,
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def start_execution(
        self,
        session_id: str,
        identifier: str,
        component_type: str
    ) -> ChainExecution:
        """Start tracking a new generation execution"""
        execution = ChainExecution(
            session_id=session_id,
            identifier=identifier,
            component_type=component_type,
            started_at=datetime.now()
        )
        self._executions[session_id] = execution
        logger.info(f"🔗 [CHAIN] Started tracking: {identifier}.{component_type} (session: {session_id})")
        return execution
    
    def mark_phase_complete(self, session_id: str, phase: ChainPhase):
        """Mark a phase as completed"""
        if session_id not in self._executions:
            logger.warning(f"⚠️  [CHAIN] Unknown session: {session_id}")
            return
        
        execution = self._executions[session_id]
        execution.completed_phases.add(phase)
        logger.debug(f"✓ [CHAIN] {phase.value} completed")
    
    def mark_phase_skipped(self, session_id: str, phase: ChainPhase, reason: str):
        """Mark a phase as intentionally skipped"""
        if session_id not in self._executions:
            return
        
        execution = self._executions[session_id]
        execution.skipped_phases.add(phase)
        logger.warning(f"⏭️  [CHAIN] {phase.value} skipped: {reason}")
    
    def mark_phase_error(self, session_id: str, phase: ChainPhase, error: str):
        """Record an error in a phase"""
        if session_id not in self._executions:
            return
        
        execution = self._executions[session_id]
        execution.errors[phase] = error
        logger.error(f"❌ [CHAIN] {phase.value} failed: {error}")
    
    def complete_execution(self, session_id: str, success: bool):
        """Complete tracking and verify chain completeness"""
        if session_id not in self._executions:
            logger.error(f"❌ [CHAIN] Cannot complete unknown session: {session_id}")
            return
        
        execution = self._executions[session_id]
        execution.completed_at = datetime.now()
        execution.success = success
        
        # Verify all required phases were executed
        missing_phases = self._required_phases - execution.completed_phases - execution.skipped_phases
        
        if missing_phases:
            logger.error(
                f"❌ [CHAIN] INCOMPLETE EXECUTION for {execution.identifier}.{execution.component_type}! "
                f"Missing phases: {[p.value for p in missing_phases]}"
            )
            
            # This is a critical error - raise exception
            raise ChainIncompleteError(
                f"Generation chain incomplete for {execution.identifier}.{execution.component_type}. "
                f"Missing required phases: {[p.value for p in missing_phases]}"
            )
        
        # Log summary
        duration = (execution.completed_at - execution.started_at).total_seconds()
        logger.info(
            f"✅ [CHAIN] Completed: {execution.identifier}.{execution.component_type} "
            f"({len(execution.completed_phases)} phases, {duration:.1f}s)"
        )
        
        if execution.skipped_phases:
            logger.info(f"   Skipped phases: {[p.value for p in execution.skipped_phases]}")
        
        if execution.errors:
            logger.warning(f"   Phases with errors: {list(execution.errors.keys())}")
    
    def get_execution(self, session_id: str) -> Optional[ChainExecution]:
        """Get execution details"""
        return self._executions.get(session_id)
    
    def get_statistics(self) -> Dict:
        """Get overall chain statistics"""
        total = len(self._executions)
        successful = sum(1 for e in self._executions.values() if e.success)
        
        phase_completion_rates = {}
        for phase in ChainPhase:
            completed = sum(1 for e in self._executions.values() if phase in e.completed_phases)
            phase_completion_rates[phase.value] = completed / total if total > 0 else 0
        
        return {
            'total_executions': total,
            'successful': successful,
            'success_rate': successful / total if total > 0 else 0,
            'phase_completion_rates': phase_completion_rates
        }


class ChainIncompleteError(Exception):
    """Raised when a generation chain is missing required phases"""
    pass


def track_phase(phase: ChainPhase, required: bool = True):
    """
    Decorator to track phase execution in the generation chain.
    
    Usage:
        @track_phase(ChainPhase.ENRICHMENT)
        def enrich_data(self, session_id, material_name):
            ...
    
    Args:
        phase: The chain phase this function represents
        required: Whether this phase is required (default: True)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract session_id from args or kwargs
            session_id = kwargs.get('session_id')
            if not session_id and len(args) > 0:
                # Try to find session_id in instance attributes
                if hasattr(args[0], '_current_session_id'):
                    session_id = args[0]._current_session_id
            
            if not session_id:
                logger.warning(f"⚠️  [CHAIN] No session_id for {phase.value} - skipping tracking")
                return func(*args, **kwargs)
            
            registry = ChainRegistry()
            
            try:
                result = func(*args, **kwargs)
                registry.mark_phase_complete(session_id, phase)
                return result
            
            except Exception as e:
                registry.mark_phase_error(session_id, phase, str(e))
                raise
        
        return wrapper
    return decorator


def allow_skip_phase(phase: ChainPhase, reason: str):
    """
    Mark a phase as intentionally skipped (e.g., readability validation disabled).
    
    Usage:
        if not readability_enabled:
            allow_skip_phase(ChainPhase.READABILITY_VALIDATION, "disabled in config")
    """
    # This is a helper function that components can call
    # when they intentionally skip a phase
    pass


# Example integration into UnifiedOrchestrator
class ChainVerifiedOrchestrator:
    """
    Example showing how to integrate chain verification into UnifiedOrchestrator.
    
    This is a mixin or can be integrated directly into the orchestrator.
    """
    
    def generate(self, identifier: str, component_type: str, **kwargs):
        """Generate with chain verification"""
        import uuid
        
        # Start chain tracking
        session_id = f"{identifier}-{component_type}-{uuid.uuid4().hex[:8]}"
        self._current_session_id = session_id
        
        registry = ChainRegistry()
        registry.start_execution(session_id, identifier, component_type)
        
        try:
            # Call actual generation
            result = self._generate_with_tracking(session_id, identifier, component_type, **kwargs)
            
            # Mark as complete
            registry.complete_execution(session_id, result.get('success', False))
            
            return result
        
        except Exception as e:
            registry.complete_execution(session_id, success=False)
            raise
    
    @track_phase(ChainPhase.DATA_LOADING)
    def _load_data(self, session_id: str, identifier: str):
        """Load data with phase tracking"""
        # Actual data loading logic
        pass
    
    @track_phase(ChainPhase.ENRICHMENT)
    def _enrich_data(self, session_id: str, facts):
        """Enrich with phase tracking"""
        # Actual enrichment logic
        pass
    
    @track_phase(ChainPhase.AI_DETECTION)
    def _detect_ai(self, session_id: str, text):
        """AI detection with phase tracking"""
        # Actual detection logic
        pass


def generate_chain_verification_report():
    """Generate a report of chain executions"""
    registry = ChainRegistry()
    stats = registry.get_statistics()
    
    print("\n" + "=" * 60)
    print("GENERATION CHAIN VERIFICATION REPORT")
    print("=" * 60)
    
    print(f"\nTotal executions: {stats['total_executions']}")
    print(f"Successful: {stats['successful']}")
    print(f"Success rate: {stats['success_rate']:.1%}")
    
    print("\nPhase Completion Rates:")
    for phase, rate in sorted(stats['phase_completion_rates'].items()):
        status = "✅" if rate >= 0.95 else "⚠️" if rate >= 0.80 else "❌"
        print(f"  {status} {phase}: {rate:.1%}")
    
    print("=" * 60)


# Export public API
__all__ = [
    'ChainPhase',
    'ChainRegistry',
    'ChainExecution',
    'ChainIncompleteError',
    'track_phase',
    'allow_skip_phase',
    'generate_chain_verification_report'
]
