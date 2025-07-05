"""
Repository interfaces for prompt optimization.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from datetime import datetime

from generator.core.domain.prompt_optimization import (
    PromptPerformanceProfile,
    PromptUsage,
    SelectionContext,
    OptimizationReport,
    PromptPerformanceLevel,
)


class IPromptPerformanceRepository(ABC):
    """Repository interface for prompt performance data."""

    @abstractmethod
    async def save_usage(self, usage: PromptUsage) -> None:
        """Save a single prompt usage record."""
        pass

    @abstractmethod
    async def get_performance_profile(
        self, prompt_name: str, detection_type: str
    ) -> Optional[PromptPerformanceProfile]:
        """Get performance profile for a specific prompt."""
        pass

    @abstractmethod
    async def get_all_profiles(
        self, detection_type: Optional[str] = None
    ) -> List[PromptPerformanceProfile]:
        """Get all performance profiles, optionally filtered by detection type."""
        pass

    @abstractmethod
    async def get_top_performers(
        self, detection_type: str, limit: int = 5, min_usage_count: int = 10
    ) -> List[PromptPerformanceProfile]:
        """Get top performing prompts for detection type."""
        pass

    @abstractmethod
    async def get_usage_history(
        self,
        prompt_name: Optional[str] = None,
        detection_type: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[PromptUsage]:
        """Get usage history with optional filters."""
        pass

    @abstractmethod
    async def get_performance_trends(
        self, detection_type: str, days: int = 30
    ) -> Dict[str, List[tuple]]:
        """Get performance trends over time (prompt_name -> [(date, success_rate), ...])."""
        pass

    @abstractmethod
    async def delete_old_usage_records(self, older_than: datetime) -> int:
        """Delete usage records older than specified date. Returns count deleted."""
        pass


class IPromptSelectionStrategy(ABC):
    """Interface for prompt selection strategies."""

    @abstractmethod
    async def select_prompt(
        self,
        context: SelectionContext,
        available_prompts: List[str],
        performance_repo: IPromptPerformanceRepository,
    ) -> str:
        """Select the best prompt for the given context."""
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of this selection strategy."""
        pass


class IOptimizationAnalyzer(ABC):
    """Interface for analyzing prompt performance and generating insights."""

    @abstractmethod
    async def analyze_performance(
        self, detection_type: str, performance_repo: IPromptPerformanceRepository
    ) -> OptimizationReport:
        """Analyze performance and generate optimization report."""
        pass

    @abstractmethod
    async def generate_prompt_recommendations(
        self, detection_type: str, performance_repo: IPromptPerformanceRepository
    ) -> List[str]:
        """Generate actionable recommendations for prompt optimization."""
        pass


class IPromptGenerator(ABC):
    """Interface for generating new optimized prompts."""

    @abstractmethod
    async def generate_optimized_prompt(
        self,
        detection_type: str,
        performance_profiles: List[PromptPerformanceProfile],
        target_performance: PromptPerformanceLevel = PromptPerformanceLevel.EXCELLENT,
    ) -> tuple[str, str]:
        """
        Generate optimized prompt based on performance data.
        Returns (prompt_content, suggested_filename).
        """
        pass

    @abstractmethod
    async def refine_existing_prompt(
        self,
        original_prompt: str,
        performance_profile: PromptPerformanceProfile,
        target_improvements: List[str],
    ) -> str:
        """Refine an existing prompt based on performance insights."""
        pass


class IPromptOptimizationService(ABC):
    """Interface for the main prompt optimization service."""

    @abstractmethod
    async def select_prompt(
        self, available_prompts: List[str], context: str = ""
    ) -> str:
        """Select the best prompt from available options."""
        pass

    @abstractmethod
    async def record_usage(
        self,
        prompt_name: str,
        context: str = "",
        success: bool = True,
        ai_score: Optional[float] = None,
        human_score: Optional[float] = None,
        execution_time: float = 0.0,
        provider: str = "unknown",
    ) -> None:
        """Record usage of a prompt."""
        pass

    @abstractmethod
    async def get_performance_profile(
        self, prompt_name: str, context: str = ""
    ) -> Optional[PromptPerformanceProfile]:
        """Get performance profile for a specific prompt."""
        pass

    @abstractmethod
    async def get_all_profiles(
        self, context: str = ""
    ) -> List[PromptPerformanceProfile]:
        """Get all performance profiles."""
        pass

    @abstractmethod
    async def get_top_performers(
        self, context: str = "", limit: int = 10
    ) -> List[PromptPerformanceProfile]:
        """Get top performing prompts."""
        pass

    @abstractmethod
    async def get_performance_analytics(self, context: str = "") -> Dict[str, any]:
        """Get performance analytics and insights."""
        pass

    @abstractmethod
    async def generate_comprehensive_report(self) -> str:
        """Generate a comprehensive performance report."""
        pass
