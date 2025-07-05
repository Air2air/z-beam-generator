"""
Command objects for the Z-Beam application layer.
These represent user intentions and use cases.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

from domain import DetectionMode, Provider


@dataclass(frozen=True)
class GenerateContentCommand:
    """Command to generate content for an article."""
    
    material: str
    sections: List[str]  # Section names to generate
    total_word_budget: int
    max_iterations_per_section: int = 5
    provider: Provider = Provider.GEMINI
    detection_mode: DetectionMode = DetectionMode.COMPREHENSIVE
    ai_threshold: float = 25.0
    human_threshold: float = 25.0
    force_regenerate: bool = False
    custom_settings: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate the command."""
        if not self.material or not self.material.strip():
            raise ValueError("Material cannot be empty")
        
        if not self.sections:
            raise ValueError("At least one section must be specified")
        
        if self.total_word_budget <= 0:
            raise ValueError("Word budget must be positive")
        
        if self.max_iterations_per_section <= 0:
            raise ValueError("Max iterations must be positive")
        
        if not 0 <= self.ai_threshold <= 100:
            raise ValueError("AI threshold must be between 0 and 100")
        
        if not 0 <= self.human_threshold <= 100:
            raise ValueError("Human threshold must be between 0 and 100")


@dataclass(frozen=True)
class OptimizePromptCommand:
    """Command to optimize prompts based on performance data."""
    
    prompt_name: str
    content_samples: List[str]
    target_ai_score: float = 25.0
    target_human_score: float = 75.0
    optimization_iterations: int = 3
    test_provider: Provider = Provider.GEMINI
    
    def __post_init__(self):
        """Validate the command."""
        if not self.prompt_name or not self.prompt_name.strip():
            raise ValueError("Prompt name cannot be empty")
        
        if not self.content_samples:
            raise ValueError("Content samples cannot be empty")
        
        if not 0 <= self.target_ai_score <= 100:
            raise ValueError("Target AI score must be between 0 and 100")
        
        if not 0 <= self.target_human_score <= 100:
            raise ValueError("Target human score must be between 0 and 100")


@dataclass(frozen=True)
class AnalyzeContentCommand:
    """Command to analyze existing content for AI detection patterns."""
    
    content: str
    analysis_type: str = "comprehensive"  # comprehensive, ai_only, human_only
    provider: Provider = Provider.GEMINI
    include_suggestions: bool = True
    
    def __post_init__(self):
        """Validate the command."""
        if not self.content or not self.content.strip():
            raise ValueError("Content cannot be empty")
        
        valid_types = ["comprehensive", "ai_only", "human_only"]
        if self.analysis_type not in valid_types:
            raise ValueError(f"Analysis type must be one of: {valid_types}")


@dataclass(frozen=True)
class TrainDetectorCommand:
    """Command to train detection models with feedback."""
    
    training_samples: List[Dict[str, Any]]  # content, expected_ai_score, expected_human_score
    model_type: str = "ai_detection"  # ai_detection, human_detection
    training_epochs: int = 10
    validation_split: float = 0.2
    
    def __post_init__(self):
        """Validate the command."""
        if not self.training_samples:
            raise ValueError("Training samples cannot be empty")
        
        valid_types = ["ai_detection", "human_detection"]
        if self.model_type not in valid_types:
            raise ValueError(f"Model type must be one of: {valid_types}")
        
        if self.training_epochs <= 0:
            raise ValueError("Training epochs must be positive")
        
        if not 0 < self.validation_split < 1:
            raise ValueError("Validation split must be between 0 and 1")


@dataclass(frozen=True)
class ConfigureSystemCommand:
    """Command to update system configuration."""
    
    configuration_updates: Dict[str, Any]
    apply_immediately: bool = True
    backup_current_config: bool = True
    
    def __post_init__(self):
        """Validate the command."""
        if not self.configuration_updates:
            raise ValueError("Configuration updates cannot be empty")


@dataclass(frozen=True)
class GenerateReportCommand:
    """Command to generate performance and analytics reports."""
    
    report_type: str  # performance, usage, quality, costs
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_details: bool = True
    format: str = "json"  # json, csv, pdf
    
    def __post_init__(self):
        """Validate the command."""
        valid_types = ["performance", "usage", "quality", "costs"]
        if self.report_type not in valid_types:
            raise ValueError(f"Report type must be one of: {valid_types}")
        
        valid_formats = ["json", "csv", "pdf"]
        if self.format not in valid_formats:
            raise ValueError(f"Format must be one of: {valid_formats}")
        
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("Start date must be before end date")
