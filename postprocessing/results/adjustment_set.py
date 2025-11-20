"""Adjustment Set Dataclass"""

from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class AdjustmentSet:
    """Parameter adjustments from learning systems"""
    
    # Adjustments from each system
    sweet_spot_adjustments: Dict[str, float] = field(default_factory=dict)
    temperature_adjustments: Dict[str, float] = field(default_factory=dict)
    realism_adjustments: Dict[str, float] = field(default_factory=dict)
    pattern_adjustments: Dict[str, float] = field(default_factory=dict)
    
    # Merged final adjustments (with priority applied)
    final_adjustments: Dict[str, float] = field(default_factory=dict)
    
    # Metadata
    adjustment_count: int = 0
    sources: List[str] = field(default_factory=list)
    priority_order: List[str] = field(default_factory=lambda: [
        'sweet_spot', 'temperature', 'realism', 'pattern'
    ])
    
    def __post_init__(self):
        if self.final_adjustments:
            self.adjustment_count = len(self.final_adjustments)
