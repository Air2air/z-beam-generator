"""
Value objects for content specifications in the Z-Beam domain.
These are immutable objects that represent important business concepts.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class SectionType(Enum):
    """Enumeration of supported section types."""
    INTRODUCTION = "introduction"
    COMPARISON = "comparison"
    CONTAMINANTS = "contaminants"
    SUBSTRATES = "substrates"
    CHART = "chart"
    TABLE = "table"
    MATERIAL_RESEARCH = "material_research"
    CONCLUSION = "conclusion"


@dataclass(frozen=True)
class SectionSpec:
    """Value object representing a section specification."""
    
    name: str
    section_type: SectionType
    word_budget: int
    max_iterations: int
    priority: int = 1  # 1 = high, 2 = medium, 3 = low
    requirements: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate the section specification."""
        if not self.name or not self.name.strip():
            raise ValueError("Section name cannot be empty")
        
        if self.word_budget <= 0:
            raise ValueError("Word budget must be positive")
        
        if self.max_iterations <= 0:
            raise ValueError("Max iterations must be positive")
        
        if self.priority not in [1, 2, 3]:
            raise ValueError("Priority must be 1 (high), 2 (medium), or 3 (low)")
    
    def is_high_priority(self) -> bool:
        """Check if this section is high priority."""
        return self.priority == 1
    
    def get_requirement(self, key: str, default=None):
        """Get a specific requirement value."""
        if not self.requirements:
            return default
        return self.requirements.get(key, default)


@dataclass(frozen=True)
class WordBudget:
    """Value object representing word budget allocation."""
    
    total_words: int
    section_allocations: Dict[str, int]
    buffer_percentage: float = 0.1  # 10% buffer for variance
    
    def __post_init__(self):
        """Validate the word budget."""
        if self.total_words <= 0:
            raise ValueError("Total words must be positive")
        
        if not self.section_allocations:
            raise ValueError("Section allocations cannot be empty")
        
        allocated_total = sum(self.section_allocations.values())
        if allocated_total != self.total_words:
            raise ValueError(
                f"Section allocations ({allocated_total}) must equal total words ({self.total_words})"
            )
        
        if not 0 <= self.buffer_percentage <= 0.5:
            raise ValueError("Buffer percentage must be between 0 and 50%")
    
    def get_section_budget(self, section_name: str) -> int:
        """Get the word budget for a specific section."""
        return self.section_allocations.get(section_name, 0)
    
    def get_section_budget_with_buffer(self, section_name: str) -> int:
        """Get the word budget for a section including buffer."""
        base_budget = self.get_section_budget(section_name)
        buffer = int(base_budget * self.buffer_percentage)
        return base_budget + buffer
    
    def get_total_with_buffer(self) -> int:
        """Get total word budget including buffer."""
        return int(self.total_words * (1 + self.buffer_percentage))
    
    def is_within_budget(self, section_name: str, actual_words: int) -> bool:
        """Check if actual word count is within budget for a section."""
        budget_with_buffer = self.get_section_budget_with_buffer(section_name)
        return actual_words <= budget_with_buffer
    
    def get_utilization_percentage(self, section_name: str, actual_words: int) -> float:
        """Calculate utilization percentage for a section."""
        budget = self.get_section_budget(section_name)
        if budget == 0:
            return 0.0
        return (actual_words / budget) * 100
    
    @classmethod
    def create_balanced_allocation(cls, total_words: int, section_names: List[str]) -> 'WordBudget':
        """Create a balanced word budget allocation across sections."""
        if not section_names:
            raise ValueError("Section names cannot be empty")
        
        words_per_section = total_words // len(section_names)
        remainder = total_words % len(section_names)
        
        allocations = {}
        for i, name in enumerate(section_names):
            allocations[name] = words_per_section + (1 if i < remainder else 0)
        
        return cls(total_words=total_words, section_allocations=allocations)
    
    @classmethod
    def create_weighted_allocation(
        cls, 
        total_words: int, 
        section_weights: Dict[str, float]
    ) -> 'WordBudget':
        """Create a weighted word budget allocation based on section importance."""
        if not section_weights:
            raise ValueError("Section weights cannot be empty")
        
        total_weight = sum(section_weights.values())
        if total_weight <= 0:
            raise ValueError("Total weight must be positive")
        
        allocations = {}
        allocated_words = 0
        
        # Allocate words based on weights
        section_items = list(section_weights.items())
        for i, (name, weight) in enumerate(section_items[:-1]):
            words = int((weight / total_weight) * total_words)
            allocations[name] = words
            allocated_words += words
        
        # Give remaining words to the last section to ensure exact total
        last_section = section_items[-1][0]
        allocations[last_section] = total_words - allocated_words
        
        return cls(total_words=total_words, section_allocations=allocations)
