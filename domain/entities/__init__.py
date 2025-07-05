"""
Domain entities for the Z-Beam content generation system.
These represent the core business concepts with their invariants and behavior.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from domain.value_objects.content_specs import SectionSpec, WordBudget
from domain.value_objects.generation_settings import GenerationSettings
from domain.value_objects.detection_result import DetectionResult


@dataclass
class ContentGenerationRequest:
    """Core business entity representing a content generation request."""
    
    material: str
    sections: List[SectionSpec]
    word_budget: WordBudget
    settings: GenerationSettings
    created_at: datetime = field(default_factory=datetime.now)
    request_id: str = field(default="")
    
    def __post_init__(self):
        """Validate business rules after initialization."""
        if not self.request_id:
            self.request_id = f"{self.material.lower()}_{self.created_at.strftime('%Y%m%d_%H%M%S')}"
        self.validate()
    
    def validate(self) -> None:
        """Validate business rules for content generation request."""
        if not self.material or not self.material.strip():
            raise ValueError("Material cannot be empty")
        
        if not self.sections:
            raise ValueError("At least one section must be specified")
        
        if self.word_budget.total_words <= 0:
            raise ValueError("Total word budget must be positive")
        
        # Validate section word budgets sum correctly
        allocated_words = sum(spec.word_budget for spec in self.sections)
        if allocated_words != self.word_budget.total_words:
            raise ValueError(
                f"Section word budgets ({allocated_words}) must equal total budget ({self.word_budget.total_words})"
            )
    
    def get_section_by_name(self, name: str) -> Optional[SectionSpec]:
        """Get a section specification by name."""
        return next((section for section in self.sections if section.name == name), None)
    
    def get_total_expected_iterations(self) -> int:
        """Calculate total expected iterations across all sections."""
        return sum(spec.max_iterations for spec in self.sections)


@dataclass
class ContentGenerationResult:
    """Entity representing the complete result of content generation."""
    
    request_id: str
    material: str
    sections: Dict[str, str]  # section_name -> content
    metadata: Dict[str, Any]
    generation_stats: Dict[str, Any]
    detection_results: Dict[str, DetectionResult]  # section_name -> detection_result
    created_at: datetime = field(default_factory=datetime.now)
    success: bool = True
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """Validate the generation result."""
        self.validate()
    
    def validate(self) -> None:
        """Validate the generation result."""
        if not self.request_id:
            raise ValueError("Request ID cannot be empty")
        
        if self.success and not self.sections:
            raise ValueError("Successful result must have at least one section")
        
        if not self.success and not self.error_message:
            raise ValueError("Failed result must have an error message")
    
    def get_total_word_count(self) -> int:
        """Calculate total word count across all sections."""
        return sum(len(content.split()) for content in self.sections.values())
    
    def get_section_word_count(self, section_name: str) -> int:
        """Get word count for a specific section."""
        content = self.sections.get(section_name, "")
        return len(content.split()) if content else 0
    
    def get_average_ai_score(self) -> float:
        """Calculate average AI detection score across all sections."""
        if not self.detection_results:
            return 0.0
        
        total_score = sum(result.ai_score for result in self.detection_results.values())
        return total_score / len(self.detection_results)
    
    def get_average_human_score(self) -> float:
        """Calculate average human-like score across all sections."""
        if not self.detection_results:
            return 0.0
        
        total_score = sum(result.human_score for result in self.detection_results.values())
        return total_score / len(self.detection_results)
    
    def passes_quality_thresholds(self, ai_threshold: float, human_threshold: float) -> bool:
        """Check if all sections pass the quality thresholds."""
        return all(
            result.ai_score <= ai_threshold and result.human_score >= human_threshold
            for result in self.detection_results.values()
        )


@dataclass
class GenerationSession:
    """Entity representing an active generation session with state management."""
    
    session_id: str
    request: ContentGenerationRequest
    current_section: Optional[str] = None
    completed_sections: List[str] = field(default_factory=list)
    section_attempts: Dict[str, int] = field(default_factory=dict)
    section_results: Dict[str, str] = field(default_factory=dict)
    section_detection_results: Dict[str, DetectionResult] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize session state."""
        if not self.session_id:
            self.session_id = f"session_{self.started_at.strftime('%Y%m%d_%H%M%S')}"
    
    def start_section(self, section_name: str) -> None:
        """Start processing a new section."""
        if section_name not in [spec.name for spec in self.request.sections]:
            raise ValueError(f"Section '{section_name}' not found in request")
        
        self.current_section = section_name
        if section_name not in self.section_attempts:
            self.section_attempts[section_name] = 0
    
    def complete_section(self, section_name: str, content: str, detection_result: DetectionResult) -> None:
        """Mark a section as completed with its content and detection result."""
        if section_name != self.current_section:
            raise ValueError(f"Cannot complete section '{section_name}' - not currently active")
        
        self.section_results[section_name] = content
        self.section_detection_results[section_name] = detection_result
        self.completed_sections.append(section_name)
        self.current_section = None
    
    def increment_section_attempt(self, section_name: str) -> int:
        """Increment and return the attempt count for a section."""
        if section_name not in self.section_attempts:
            self.section_attempts[section_name] = 0
        self.section_attempts[section_name] += 1
        return self.section_attempts[section_name]
    
    def is_section_completed(self, section_name: str) -> bool:
        """Check if a section has been completed."""
        return section_name in self.completed_sections
    
    def is_complete(self) -> bool:
        """Check if the entire session is complete."""
        all_sections = [spec.name for spec in self.request.sections]
        return all(self.is_section_completed(name) for name in all_sections)
    
    def complete_session(self) -> ContentGenerationResult:
        """Complete the session and return the final result."""
        if not self.is_complete():
            raise ValueError("Cannot complete session - not all sections are finished")
        
        self.completed_at = datetime.now()
        
        # Calculate generation stats
        generation_stats = {
            "total_sections": len(self.request.sections),
            "total_attempts": sum(self.section_attempts.values()),
            "average_attempts_per_section": sum(self.section_attempts.values()) / len(self.request.sections),
            "duration_seconds": (self.completed_at - self.started_at).total_seconds(),
            "sections_on_first_try": sum(1 for attempts in self.section_attempts.values() if attempts == 1),
        }
        
        return ContentGenerationResult(
            request_id=self.request.request_id,
            material=self.request.material,
            sections=self.section_results.copy(),
            metadata={
                "session_id": self.session_id,
                "request": self.request,
            },
            generation_stats=generation_stats,
            detection_results=self.section_detection_results.copy(),
            created_at=self.completed_at,
        )
    
    def get_remaining_sections(self) -> List[str]:
        """Get list of sections that haven't been completed yet."""
        all_sections = [spec.name for spec in self.request.sections]
        return [name for name in all_sections if not self.is_section_completed(name)]
    
    def get_next_section(self) -> Optional[str]:
        """Get the next section to process, or None if all are complete."""
        remaining = self.get_remaining_sections()
        return remaining[0] if remaining else None
