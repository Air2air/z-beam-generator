"""Gate Results Dataclass"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class GateResults:
    """Results from quality gate checks"""
    
    winston_passed: bool
    realism_passed: bool
    readability_passed: bool
    subjective_passed: bool
    
    all_passed: bool = False
    
    failed_gates: List[str] = None
    gate_details: Dict[str, Dict] = None
    
    def __post_init__(self):
        # Calculate all_passed
        self.all_passed = all([
            self.winston_passed,
            self.realism_passed,
            self.readability_passed,
            self.subjective_passed
        ])
        
        # Track failed gates
        if not self.failed_gates:
            self.failed_gates = []
            if not self.winston_passed:
                self.failed_gates.append('winston')
            if not self.realism_passed:
                self.failed_gates.append('realism')
            if not self.readability_passed:
                self.failed_gates.append('readability')
            if not self.subjective_passed:
                self.failed_gates.append('subjective')
