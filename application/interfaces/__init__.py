"""
Application service interfaces that define use case contracts.
These orchestrate domain services and repositories to fulfill business requirements.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

from domain.entities import ContentGenerationRequest, ContentGenerationResult, GenerationSession
from domain.value_objects import DetectionResult, GenerationSettings
from application.commands import (
    GenerateContentCommand,
    OptimizePromptCommand,
    AnalyzeContentCommand,
    TrainDetectorCommand,
    ConfigureSystemCommand,
    GenerateReportCommand
)


class IContentGenerationService(ABC):
    """Application service for content generation orchestration."""
    
    @abstractmethod
    async def generate_content(self, command: GenerateContentCommand) -> ContentGenerationResult:
        """Generate content based on the command specifications."""
        pass
    
    @abstractmethod
    async def generate_section(
        self,
        session_id: str,
        section_name: str,
        settings: GenerationSettings
    ) -> str:
        """Generate content for a specific section within a session."""
        pass
    
    @abstractmethod
    async def improve_content(
        self,
        content: str,
        detection_result: DetectionResult,
        target_improvements: List[str]
    ) -> str:
        """Improve existing content based on detection feedback."""
        pass
    
    @abstractmethod
    async def create_session(self, request: ContentGenerationRequest) -> GenerationSession:
        """Create a new generation session."""
        pass
    
    @abstractmethod
    async def resume_session(self, session_id: str) -> GenerationSession:
        """Resume an existing generation session."""
        pass


class IDetectionService(ABC):
    """Application service for AI detection and analysis."""
    
    @abstractmethod
    async def analyze_content(self, command: AnalyzeContentCommand) -> Dict[str, Any]:
        """Analyze content for AI detection patterns."""
        pass
    
    @abstractmethod
    async def detect_ai_likelihood(
        self,
        content: str,
        settings: GenerationSettings,
        iteration: int = 1
    ) -> DetectionResult:
        """Detect AI-like characteristics in content."""
        pass
    
    @abstractmethod
    async def detect_human_likelihood(
        self,
        content: str,
        settings: GenerationSettings,
        iteration: int = 1
    ) -> DetectionResult:
        """Detect human-like characteristics in content."""
        pass
    
    @abstractmethod
    async def comprehensive_detection(
        self,
        content: str,
        settings: GenerationSettings,
        iteration: int = 1
    ) -> Dict[str, DetectionResult]:
        """Run comprehensive detection (both AI and human analysis)."""
        pass


class IPromptOptimizationService(ABC):
    """Application service for prompt optimization and management."""
    
    @abstractmethod
    async def optimize_prompt(self, command: OptimizePromptCommand) -> Dict[str, Any]:
        """Optimize a prompt based on performance data."""
        pass
    
    @abstractmethod
    async def select_best_prompt(
        self,
        available_prompts: List[str],
        context: str,
        performance_history: Dict[str, Any]
    ) -> str:
        """Select the best prompt from available options."""
        pass
    
    @abstractmethod
    async def record_prompt_performance(
        self,
        prompt_name: str,
        performance_data: Dict[str, Any]
    ) -> None:
        """Record performance data for a prompt."""
        pass
    
    @abstractmethod
    async def get_prompt_analytics(
        self,
        prompt_name: str = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """Get analytics for prompt performance."""
        pass


class ITrainingService(ABC):
    """Application service for model training and improvement."""
    
    @abstractmethod
    async def train_detector(self, command: TrainDetectorCommand) -> Dict[str, Any]:
        """Train detection models with provided samples."""
        pass
    
    @abstractmethod
    async def evaluate_model_performance(
        self,
        model_type: str,
        test_samples: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Evaluate model performance on test samples."""
        pass
    
    @abstractmethod
    async def update_model_weights(
        self,
        model_type: str,
        feedback_data: List[Dict[str, Any]]
    ) -> None:
        """Update model weights based on feedback."""
        pass


class ISystemConfigurationService(ABC):
    """Application service for system configuration management."""
    
    @abstractmethod
    async def configure_system(self, command: ConfigureSystemCommand) -> Dict[str, Any]:
        """Update system configuration."""
        pass
    
    @abstractmethod
    async def get_current_configuration(self) -> Dict[str, Any]:
        """Get current system configuration."""
        pass
    
    @abstractmethod
    async def validate_configuration(self, config_updates: Dict[str, Any]) -> List[str]:
        """Validate configuration updates and return any issues."""
        pass
    
    @abstractmethod
    async def backup_configuration(self) -> str:
        """Create a backup of current configuration and return backup ID."""
        pass
    
    @abstractmethod
    async def restore_configuration(self, backup_id: str) -> None:
        """Restore configuration from a backup."""
        pass


class IReportingService(ABC):
    """Application service for analytics and reporting."""
    
    @abstractmethod
    async def generate_report(self, command: GenerateReportCommand) -> Dict[str, Any]:
        """Generate a report based on the command specifications."""
        pass
    
    @abstractmethod
    async def get_performance_metrics(
        self,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """Get system performance metrics."""
        pass
    
    @abstractmethod
    async def get_usage_analytics(
        self,
        start_date: datetime = None,
        end_date: datetime = None,
        group_by: str = "day"
    ) -> Dict[str, Any]:
        """Get usage analytics."""
        pass
    
    @abstractmethod
    async def get_quality_trends(
        self,
        material: str = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """Get content quality trends over time."""
        pass
    
    @abstractmethod
    async def get_cost_analysis(
        self,
        start_date: datetime = None,
        end_date: datetime = None,
        by_provider: bool = True
    ) -> Dict[str, Any]:
        """Get cost analysis for API usage."""
        pass


class IWorkflowOrchestrationService(ABC):
    """Application service for orchestrating complex workflows."""
    
    @abstractmethod
    async def execute_full_generation_workflow(
        self,
        command: GenerateContentCommand
    ) -> ContentGenerationResult:
        """Execute the complete content generation workflow."""
        pass
    
    @abstractmethod
    async def execute_iterative_improvement_workflow(
        self,
        content: str,
        target_quality: Dict[str, float],
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """Execute iterative content improvement workflow."""
        pass
    
    @abstractmethod
    async def execute_bulk_generation_workflow(
        self,
        commands: List[GenerateContentCommand],
        parallel_limit: int = 3
    ) -> List[ContentGenerationResult]:
        """Execute bulk content generation with concurrency control."""
        pass
