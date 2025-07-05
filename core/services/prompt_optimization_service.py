"""
Improved prompt optimization service with proper dependency injection.
"""

from typing import List, Optional
from datetime import datetime, timedelta

from generator.core.domain.models import GenerationContext
from generator.core.domain.prompt_optimization import (
    PromptUsage,
    SelectionContext,
    SelectionResult,
    OptimizationReport,
    PromptPerformanceProfile,
)
from generator.core.interfaces.prompt_optimization import (
    IPromptPerformanceRepository,
    IPromptSelectionStrategy,
    IOptimizationAnalyzer,
    IPromptGenerator,
)
from generator.modules.logger import get_logger

logger = get_logger("prompt_optimization_service")


class PromptOptimizationService:
    """
    Domain service for prompt optimization with proper dependency injection.

    This service coordinates between different optimization components while
    maintaining clean separation of concerns and testability.
    """

    def __init__(
        self,
        performance_repository: IPromptPerformanceRepository,
        selection_strategy: IPromptSelectionStrategy,
        analyzer: Optional[IOptimizationAnalyzer] = None,
        prompt_generator: Optional[IPromptGenerator] = None,
    ):
        """Initialize with injected dependencies."""
        self._performance_repo = performance_repository
        self._selection_strategy = selection_strategy
        self._analyzer = analyzer
        self._prompt_generator = prompt_generator

    async def select_prompt(
        self, available_prompts: List[str], context: str = ""
    ) -> str:
        """Select the best prompt from available options."""
        selection_context = SelectionContext(
            detection_type=context, iteration=1, section_name="", content_type="article"
        )

        selected_prompt = await self._selection_strategy.select_prompt(
            selection_context, available_prompts, self._performance_repo
        )
        return selected_prompt

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
        # Convert scores to integer range 0-100
        score = (
            int(ai_score)
            if ai_score is not None
            else (int(human_score) if human_score is not None else 50)
        )

        usage = PromptUsage(
            prompt_name=prompt_name,
            detection_type=context,
            score=score,
            success=success,
            iteration=1,
            section_name="",
            content_type="article",
            material_type=None,
            timestamp=datetime.now(),
            response_time_ms=int(execution_time * 1000) if execution_time else None,
        )

        await self._performance_repo.save_usage(usage)

    async def get_performance_profile(
        self, prompt_name: str, context: str = ""
    ) -> Optional[PromptPerformanceProfile]:
        """Get performance profile for a specific prompt."""
        return await self._performance_repo.get_performance_profile(
            prompt_name, context
        )

    async def get_all_profiles(
        self, context: str = ""
    ) -> List[PromptPerformanceProfile]:
        """Get all performance profiles."""
        return await self._performance_repo.get_all_profiles(
            context if context else None
        )

    async def get_top_performers(
        self, context: str = "", limit: int = 10
    ) -> List[PromptPerformanceProfile]:
        """Get top performing prompts."""
        return await self._performance_repo.get_top_performers(
            detection_type=context,
            limit=limit,
            min_usage_count=1,  # Lower threshold for testing
        )

    async def get_performance_analytics(self, context: str = "") -> dict:
        """Get performance analytics and insights."""
        profiles = await self.get_all_profiles(context)

        if not profiles:
            return {
                "total_prompts": 0,
                "total_usage": 0,
                "avg_success_rate": 0.0,
                "avg_score": 0.0,
                "top_performer": None,
            }

        total_usage = sum(p.metrics.usage_count for p in profiles)
        avg_success_rate = sum(p.metrics.success_rate for p in profiles) / len(profiles)
        avg_score = sum(p.metrics.average_score for p in profiles) / len(profiles)

        top_performer = max(profiles, key=lambda p: p.metrics.success_rate)

        return {
            "total_prompts": len(profiles),
            "total_usage": total_usage,
            "avg_success_rate": avg_success_rate,
            "avg_score": avg_score,
            "top_performer": top_performer.prompt_name,
        }

    async def generate_comprehensive_report(self) -> str:
        """Generate a comprehensive performance report."""
        all_profiles = await self.get_all_profiles()

        if not all_profiles:
            return "No performance data available."

        report_lines = [
            "=== Prompt Optimization Performance Report ===",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"Total Prompts: {len(all_profiles)}",
        ]

        # Group by context
        context_groups = {}
        for profile in all_profiles:
            context = profile.detection_type or "default"
            if context not in context_groups:
                context_groups[context] = []
            context_groups[context].append(profile)

        for context, profiles in context_groups.items():
            report_lines.extend(
                [
                    f"\n--- Context: {context} ---",
                    f"Prompts: {len(profiles)}",
                ]
            )

            # Sort by performance
            sorted_profiles = sorted(
                profiles, key=lambda p: p.metrics.success_rate, reverse=True
            )

            for i, profile in enumerate(sorted_profiles[:5], 1):  # Top 5
                report_lines.append(
                    f"{i}. {profile.prompt_name}: "
                    f"{profile.metrics.success_rate:.1%} success, "
                    f"{profile.metrics.usage_count} uses, "
                    f"avg score: {profile.metrics.average_score:.1f}"
                )

        return "\n".join(report_lines)

    async def track_prompt_usage(
        self,
        prompt_name: str,
        detection_type: str,
        score: int,
        success: bool,
        iteration: int,
        context: GenerationContext,
        response_time_ms: Optional[int] = None,
    ) -> None:
        """
        Track prompt usage with comprehensive context.

        Args:
            prompt_name: Name of the prompt used
            detection_type: 'ai' or 'human'
            score: Detection score (0-100)
            success: Whether the score met the threshold
            iteration: Iteration number in the detection process
            context: Generation context with material, section, etc.
            response_time_ms: API response time in milliseconds
        """
        try:
            usage = PromptUsage(
                prompt_name=prompt_name,
                detection_type=detection_type,
                score=score,
                success=success,
                iteration=iteration,
                section_name=context.get_variable("section_name", "unknown"),
                content_type=context.content_type,
                material_type=context.material,
                timestamp=datetime.now(),
                context_hash=self._generate_context_hash(context),
                response_time_ms=response_time_ms,
            )

            await self._performance_repo.save_usage(usage)

            logger.debug(
                f"Tracked usage: {prompt_name} ({detection_type}) - "
                f"Score: {score}, Success: {success}, Iteration: {iteration}"
            )

        except Exception as e:
            logger.error(f"Failed to track prompt usage: {e}")
            # Don't fail the main operation if tracking fails

    async def select_optimal_prompt(
        self,
        detection_type: str,
        iteration: int,
        context: GenerationContext,
        available_prompts: List[str],
    ) -> SelectionResult:
        """
        Select the optimal prompt for the given context.

        Returns:
            SelectionResult with chosen prompt and reasoning
        """
        selection_context = SelectionContext(
            detection_type=detection_type,
            iteration=iteration,
            section_name=context.get_variable("section_name", "unknown"),
            content_type=context.content_type,
            material_type=context.material,
        )

        try:
            selected_prompt = await self._selection_strategy.select_prompt(
                selection_context, available_prompts, self._performance_repo
            )

            # Get performance data for confidence calculation
            profile = await self._performance_repo.get_performance_profile(
                selected_prompt, detection_type
            )

            confidence = self._calculate_selection_confidence(profile)
            reasoning = self._generate_selection_reasoning(
                selected_prompt, profile, selection_context
            )

            result = SelectionResult(
                selected_prompt=selected_prompt,
                selection_strategy=self._selection_strategy.get_strategy_name(),
                confidence=confidence,
                reasoning=reasoning,
                alternatives_considered=available_prompts,
            )

            logger.info(f"Selected prompt: {result}")
            return result

        except Exception as e:
            logger.error(f"Prompt selection failed: {e}")
            # Fallback to first available prompt
            fallback_prompt = available_prompts[0] if available_prompts else "default"
            return SelectionResult(
                selected_prompt=fallback_prompt,
                selection_strategy="fallback",
                confidence=0.1,
                reasoning=f"Fallback due to selection error: {e}",
            )

    async def get_optimization_report(
        self, detection_type: Optional[str] = None
    ) -> OptimizationReport:
        """
        Generate comprehensive optimization report.

        Args:
            detection_type: Optional filter for specific detection type

        Returns:
            OptimizationReport with analysis and recommendations
        """
        try:
            if detection_type:
                return await self._analyzer.analyze_performance(
                    detection_type, self._performance_repo
                )
            else:
                # Generate combined report for all detection types
                ai_report = await self._analyzer.analyze_performance(
                    "ai", self._performance_repo
                )
                # TODO: Implement proper report merging for multiple detection types
                return ai_report

        except Exception as e:
            logger.error(f"Failed to generate optimization report: {e}")
            # Return empty report rather than failing
            return OptimizationReport(
                detection_type=detection_type or "all",
                generated_at=datetime.now(),
                total_prompts_analyzed=0,
                total_usage_records=0,
                top_performers=[],
                insights=[],
                recommendations=[f"Error generating report: {e}"],
            )

    async def generate_optimized_prompt(self, detection_type: str) -> tuple[str, str]:
        """
        Generate new optimized prompt based on performance data.

        Returns:
            Tuple of (prompt_content, suggested_filename)
        """
        try:
            # Get top performing prompts for analysis
            top_performers = await self._performance_repo.get_top_performers(
                detection_type, limit=5, min_usage_count=5
            )

            if not top_performers:
                logger.warning(f"No performance data for {detection_type} prompts")
                # Return basic template
                return await self._prompt_generator.generate_optimized_prompt(
                    detection_type, []
                )

            return await self._prompt_generator.generate_optimized_prompt(
                detection_type, top_performers
            )

        except Exception as e:
            logger.error(f"Failed to generate optimized prompt: {e}")
            raise

    async def cleanup_old_data(self, days_to_keep: int = 90) -> int:
        """
        Clean up old usage records to maintain performance.

        Args:
            days_to_keep: Number of days of data to retain

        Returns:
            Number of records deleted
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)

        try:
            deleted_count = await self._performance_repo.delete_old_usage_records(
                cutoff_date
            )
            logger.info(f"Cleaned up {deleted_count} old usage records")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return 0

    def _generate_context_hash(self, context: GenerationContext) -> str:
        """Generate hash for grouping similar contexts."""
        import hashlib

        content = (
            f"{context.content_type}:"
            f"{context.material}:"
            f"{context.get_variable('section_name', 'unknown')}"
        )

        return hashlib.md5(content.encode()).hexdigest()[:8]

    def _calculate_selection_confidence(
        self, profile: Optional[PromptPerformanceProfile]
    ) -> float:
        """Calculate confidence in selection based on performance data."""
        if not profile:
            return 0.3  # Low confidence for unknown prompts

        metrics = profile.metrics

        # Base confidence on reliability score
        confidence = metrics.reliability_score

        # Boost confidence for excellent performers
        if metrics.performance_level.value == "excellent":
            confidence = min(1.0, confidence + 0.2)

        # Reduce confidence for poor performers
        elif metrics.performance_level.value == "poor":
            confidence = max(0.1, confidence - 0.3)

        return confidence

    def _generate_selection_reasoning(
        self,
        selected_prompt: str,
        profile: Optional[PromptPerformanceProfile],
        context: SelectionContext,
    ) -> str:
        """Generate human-readable reasoning for prompt selection."""
        if not profile:
            return f"Selected {selected_prompt} (no historical data available)"

        metrics = profile.metrics

        reasons = []

        # Performance level reasoning
        if metrics.performance_level.value == "excellent":
            reasons.append(
                f"excellent performance ({metrics.success_rate:.1%} success rate)"
            )
        elif metrics.performance_level.value == "good":
            reasons.append(
                f"good performance ({metrics.success_rate:.1%} success rate)"
            )
        elif metrics.performance_level.value == "insufficient_data":
            reasons.append(f"limited data ({metrics.usage_count} uses)")
        else:
            reasons.append(
                f"moderate performance ({metrics.success_rate:.1%} success rate)"
            )

        # Trend reasoning
        if metrics.trend_direction.value == "improving":
            reasons.append("improving trend")
        elif metrics.trend_direction.value == "declining":
            reasons.append("declining trend")

        # Context reasoning
        if context.iteration == 1:
            reasons.append("first iteration (using best performer)")
        else:
            reasons.append(f"iteration {context.iteration} (ensuring diversity)")

        reason_text = ", ".join(reasons)
        return f"Selected {selected_prompt}: {reason_text}"
