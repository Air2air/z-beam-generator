"""Validation Result Dataclass"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class ValidationResult:
    """Complete validation result for pipeline"""
    
    # Identification
    material_name: str
    component_type: str
    attempt: int
    
    # Content
    content: str
    content_length: int = 0
    
    # Validation state
    success: bool = False
    all_gates_passed: bool = False
    
    # Results from passes
    quality_results: Optional[Dict[str, Any]] = None
    gate_results: Optional[Dict[str, Any]] = None
    adjustments: Optional[Dict[str, Any]] = None
    
    # Timing
    total_duration_ms: float = 0.0
    step_durations: Dict[str, float] = field(default_factory=dict)
    
    # Error tracking
    failure_reason: Optional[str] = None
    failed_step: Optional[str] = None
    
    def __post_init__(self):
        if self.content:
            self.content_length = len(self.content)
