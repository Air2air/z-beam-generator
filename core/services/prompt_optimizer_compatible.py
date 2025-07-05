"""
Backward compatible wrapper for the new prompt optimization system.
This provides the same interface as the old PromptOptimizer while using the improved architecture.
"""

from typing import List, Optional, Dict, Tuple
from datetime import datetime
import asyncio

from generator.core.domain.prompt_optimization import (
    PromptUsage,
    SelectionContext,
    PromptPerformanceProfile,
    PromptMetrics,
)
from generator.core.services.prompt_selection_strategies import (
    PerformanceBasedSelectionStrategy,
)
from generator.modules.logger import get_logger

logger = get_logger("prompt_optimizer_compatible")


class InMemoryPerformanceRepo:
    """Simple in-memory implementation of IPromptPerformanceRepository."""

    def __init__(self, performance_profiles: Dict[str, PromptPerformanceProfile]):
        """Initialize with provided performance profiles."""
        self._performance_profiles = performance_profiles

    async def get_performance_profile(self, prompt_name: str, detection_type: str):
        """Get the performance profile for a prompt and detection type."""
        key = f"{prompt_name}_{detection_type}"
        return self._performance_profiles.get(key)

    async def save_performance_profile(self, profile):
        """Save a performance profile."""
        key = f"{profile.prompt_name}_{profile.detection_type}"
        self._performance_profiles[key] = profile

    async def list_performance_profiles(self):
        """List all performance profiles."""
        return list(self._performance_profiles.values())


class PromptOptimizerCompatible:
    """
    Backward compatible wrapper for the new prompt optimization system.

    This class maintains the same interface as the original PromptOptimizer
    while internally using the improved domain models and architecture.
    """

    def __init__(self, storage_path: str = None):
        """Initialize with backward compatibility."""
        self.storage_path = storage_path or "generator/cache/prompt_performance.json"
        self._selection_strategy = PerformanceBasedSelectionStrategy()

        # In-memory storage for backward compatibility
        # In production, this would be replaced with proper repository
        self._performance_profiles: Dict[str, PromptPerformanceProfile] = {}

        # Load existing data if available
        self._load_legacy_data()

    def _load_legacy_data(self) -> None:
        """Load existing performance data from JSON file."""
        try:
            import json
            import os

            if os.path.exists(self.storage_path):
                with open(self.storage_path, "r") as f:
                    legacy_data = json.load(f)

                # Convert legacy format to new domain models
                for key, perf_data in legacy_data.items():
                    profile = self._convert_legacy_performance_data(key, perf_data)
                    if profile:
                        self._performance_profiles[key] = profile

                logger.info(
                    f"Loaded {len(self._performance_profiles)} performance profiles"
                )
        except Exception as e:
            logger.warning(f"Failed to load legacy performance data: {e}")

    def _convert_legacy_performance_data(
        self, key: str, legacy_data: Dict
    ) -> Optional[PromptPerformanceProfile]:
        """Convert legacy performance data to new domain model."""
        try:
            # Extract usage history
            usage_history = []
            if "scores" in legacy_data and "iterations" in legacy_data:
                scores = legacy_data["scores"]
                iterations = legacy_data["iterations"]
                sections = legacy_data.get("sections", ["unknown"] * len(scores))

                for i, (score, iteration) in enumerate(zip(scores, iterations)):
                    section = sections[i] if i < len(sections) else "unknown"
                    success = score <= 50  # Legacy success criteria

                    usage = PromptUsage(
                        prompt_name=legacy_data["prompt_name"],
                        detection_type=legacy_data["detection_type"],
                        score=score,
                        success=success,
                        iteration=iteration,
                        section_name=section,
                        content_type="article_section",
                        material_type=None,
                        timestamp=datetime.fromisoformat(
                            legacy_data.get("last_used", datetime.now().isoformat())
                        ),
                    )
                    usage_history.append(usage)

            # Create metrics
            metrics = PromptMetrics(
                success_rate=legacy_data.get("success_rate", 0.0),
                average_score=legacy_data.get("avg_score", 0.0),
                usage_count=legacy_data.get("uses", 0),
                last_10_scores=legacy_data.get("scores", [])[-10:],
            )

            # Create profile
            profile = PromptPerformanceProfile(
                prompt_name=legacy_data["prompt_name"],
                detection_type=legacy_data["detection_type"],
                metrics=metrics,
                usage_history=usage_history,
                created_at=datetime.fromisoformat(
                    legacy_data.get("created", datetime.now().isoformat())
                ),
                last_updated=datetime.fromisoformat(
                    legacy_data.get("last_used", datetime.now().isoformat())
                ),
            )

            return profile

        except Exception as e:
            logger.error(f"Failed to convert legacy data for {key}: {e}")
            return None

    def track_performance(
        self,
        prompt_name: str = None,
        detection_type: str = "",
        score: int = 0,
        iteration: int = 1,
        success: bool = True,
        section_name: str = None,
        context: Dict = None,
        execution_time: float = 0.0,
    ) -> None:
        """Track performance with backward compatible interface."""
        # Handle different parameter formats for backward compatibility
        if prompt_name is None:
            prompt_name = "unknown_prompt"

        # Create usage record
        usage = PromptUsage(
            prompt_name=prompt_name,
            detection_type=detection_type,
            score=score,
            success=success,
            iteration=iteration,
            section_name=section_name or "unknown",
            content_type="article_section",
            material_type=context.get("material") if context else None,
            timestamp=datetime.now(),
        )

        # Update or create performance profile
        key = f"{prompt_name}_{detection_type}"

        if key in self._performance_profiles:
            # Update existing profile
            self._performance_profiles[key] = self._performance_profiles[key].add_usage(
                usage
            )
        else:
            # Create new profile
            metrics = PromptMetrics(
                success_rate=1.0 if success else 0.0,
                average_score=float(score),
                usage_count=1,
                last_10_scores=[score],
            )

            self._performance_profiles[key] = PromptPerformanceProfile(
                prompt_name=prompt_name,
                detection_type=detection_type,
                metrics=metrics,
                usage_history=[usage],
            )

        # Save to file for persistence
        self._save_to_legacy_format()

        logger.debug(f"Tracked performance: {key} - Score: {score}, Success: {success}")

    def select_prompt(self, available_prompts: List[str], context: str = "") -> str:
        """Select the best prompt from available options."""
        return self.get_optimal_prompt(
            detection_type=context, available_prompts=available_prompts
        )

    def record_performance(
        self,
        prompt_name: str,
        context: str = "",
        success: bool = True,
        ai_score: Optional[float] = None,
        human_score: Optional[float] = None,
        execution_time: float = 0.0,
        provider: str = "unknown",
    ) -> None:
        """Record performance using the new interface (alias for track_performance)."""
        score = ai_score if ai_score is not None else (human_score or 0.0)
        self.track_performance(
            detection_type=context,
            prompt_name=prompt_name,
            score=score,
            success=success,
            execution_time=execution_time,
        )

    def generate_report(self) -> str:
        """Generate a performance report (alias for backward compatibility)."""
        return self.get_performance_report()

    def get_optimal_prompt(
        self,
        detection_type: str,
        iteration: int = 1,
        section_name: str = None,
        available_prompts: List[str] = None,
    ) -> str:
        """Get optimal prompt with backward compatible interface."""
        if not available_prompts:
            # Default prompts
            available_prompts = [
                f"{detection_type}_detection_prompt_minimal",
                f"{detection_type}_detection_v1",
                f"{detection_type}_detection_v2",
                f"{detection_type}_detection_v3",
                f"{detection_type}_detection_v4",
            ]

        # Use async selection in sync context
        try:
            # Create proper selection context
            selection_ctx = SelectionContext(
                detection_type=detection_type,
                iteration=iteration,
                section_name=section_name or "",
                content_type="article",
            )

            # Run async selection strategy (run in thread to avoid event loop conflict)
            import concurrent.futures

            # Create an InMemoryPerformanceRepo instance
            in_memory_repo = InMemoryPerformanceRepo(self._performance_profiles)

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    self._selection_strategy.select_prompt(
                        selection_ctx, available_prompts, in_memory_repo
                    ),
                )
                result = future.result(timeout=10)  # 10 second timeout
                return result

        except Exception as e:
            logger.error(f"Selection failed: {e}")
            # Fallback to simple selection
            return self._fallback_selection(
                detection_type, iteration, available_prompts
            )

    def _fallback_selection(
        self, detection_type: str, iteration: int, available_prompts: List[str]
    ) -> str:
        """Fallback selection when async selection fails."""
        if iteration == 1:
            # Try to find best performer
            best_prompt = None
            best_score = -1

            for prompt in available_prompts:
                key = f"{prompt}_{detection_type}"
                if key in self._performance_profiles:
                    profile = self._performance_profiles[key]
                    if profile.metrics.usage_count >= 3:
                        score = profile.metrics.success_rate
                        if score > best_score:
                            best_score = score
                            best_prompt = prompt

            if best_prompt:
                logger.info(f"Fallback: selected best performer {best_prompt}")
                return best_prompt

        # Default rotation
        index = (iteration - 1) % len(available_prompts)
        selected = available_prompts[index]
        logger.debug(f"Fallback: rotation selected {selected}")
        return selected

    def analyze_prompt_patterns(self, detection_type: str = None) -> Dict:
        """Analyze patterns with backward compatible interface."""
        analysis = {
            "top_performers": [],
            "worst_performers": [],
            "trends": {},
            "recommendations": [],
        }

        # Filter profiles by detection type
        relevant_profiles = []
        for profile in self._performance_profiles.values():
            if detection_type is None or profile.detection_type == detection_type:
                relevant_profiles.append(profile)

        if not relevant_profiles:
            return analysis

        # Sort by performance
        sorted_profiles = sorted(
            relevant_profiles,
            key=lambda p: (p.metrics.success_rate, -p.metrics.average_score),
            reverse=True,
        )

        # Top performers (with sufficient data)
        analysis["top_performers"] = [
            {
                "prompt": p.prompt_name,
                "type": p.detection_type,
                "success_rate": p.metrics.success_rate,
                "avg_score": p.metrics.average_score,
                "uses": p.metrics.usage_count,
            }
            for p in sorted_profiles[:3]
            if p.metrics.usage_count >= 2
        ]

        # Worst performers
        analysis["worst_performers"] = [
            {
                "prompt": p.prompt_name,
                "type": p.detection_type,
                "success_rate": p.metrics.success_rate,
                "avg_score": p.metrics.average_score,
                "uses": p.metrics.usage_count,
            }
            for p in sorted_profiles[-3:]
            if p.metrics.usage_count >= 2
        ]

        # Generate recommendations
        if analysis["top_performers"]:
            best = analysis["top_performers"][0]
            analysis["recommendations"].append(
                f"Use '{best['prompt']}' as primary {best['type']} detection prompt "
                f"(success rate: {best['success_rate']:.1%})"
            )

        return analysis

    def generate_optimized_prompt(self, detection_type: str) -> Tuple[str, str]:
        """Generate optimized prompt with backward compatible interface."""
        # Simple template-based generation for compatibility
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")

        if detection_type == "ai":
            content = """Rate this text's AI generation likelihood (0-100%):

Key indicators: formal language, generic phrasing, perfect structure

{content}

Format:
Percentage: X%
Summary: Brief analysis of key indicators
"""
            filename = f"ai_detection_optimized_{timestamp}.txt"
        else:
            content = """Rate this text's "trying too hard to be human" likelihood (0-100%):

Red flags: forced casualness, fake emotions, inappropriate informality

{content}

Format:
Percentage: X%
Summary: Issues identified
"""
            filename = f"human_detection_optimized_{timestamp}.txt"

        return content, filename

    def get_performance_report(self) -> str:
        """Generate performance report with backward compatible interface."""
        if not self._performance_profiles:
            return "No performance data available yet."

        report = ["🎯 Prompt Performance Report", "=" * 50, ""]

        # Statistics
        total_uses = sum(
            p.metrics.usage_count for p in self._performance_profiles.values()
        )
        ai_profiles = [
            p for p in self._performance_profiles.values() if p.detection_type == "ai"
        ]
        human_profiles = [
            p
            for p in self._performance_profiles.values()
            if p.detection_type == "human"
        ]

        report.extend(
            [
                f"Total prompt uses: {total_uses}",
                f"AI detection prompts tracked: {len(ai_profiles)}",
                f"Human detection prompts tracked: {len(human_profiles)}",
                "",
            ]
        )

        # Top performers by type
        for det_type in ["ai", "human"]:
            analysis = self.analyze_prompt_patterns(det_type)
            report.append(f"🏆 Top {det_type.upper()} Detection Prompts:")

            if analysis["top_performers"]:
                for i, perf in enumerate(analysis["top_performers"], 1):
                    report.append(
                        f"  {i}. {perf['prompt']} - "
                        f"Success: {perf['success_rate']:.1%}, "
                        f"Avg Score: {perf['avg_score']:.1f}, "
                        f"Uses: {perf['uses']}"
                    )
            else:
                report.append("  No sufficient data yet")
            report.append("")

        # Recommendations
        ai_analysis = self.analyze_prompt_patterns("ai")
        human_analysis = self.analyze_prompt_patterns("human")

        all_recommendations = (
            ai_analysis["recommendations"] + human_analysis["recommendations"]
        )
        if all_recommendations:
            report.append("💡 Recommendations:")
            for rec in all_recommendations:
                report.append(f"  • {rec}")

        return "\n".join(report)

    def _save_to_legacy_format(self) -> None:
        """Save data in legacy JSON format for backward compatibility."""
        try:
            import json
            import os

            legacy_data = {}

            for key, profile in self._performance_profiles.items():
                legacy_data[key] = {
                    "prompt_name": profile.prompt_name,
                    "detection_type": profile.detection_type,
                    "uses": profile.metrics.usage_count,
                    "total_score": int(
                        profile.metrics.average_score * profile.metrics.usage_count
                    ),
                    "successes": int(
                        profile.metrics.success_rate * profile.metrics.usage_count
                    ),
                    "avg_score": profile.metrics.average_score,
                    "success_rate": profile.metrics.success_rate,
                    "scores": profile.metrics.last_10_scores,
                    "iterations": [u.iteration for u in profile.usage_history[-10:]],
                    "sections": [u.section_name for u in profile.usage_history[-10:]],
                    "last_used": profile.last_updated.isoformat(),
                    "created": profile.created_at.isoformat(),
                }

            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, "w") as f:
                json.dump(legacy_data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save legacy format: {e}")

    # Async repository interface methods for compatibility with new selection strategies
    async def get_performance_profile(
        self, prompt_name: str, detection_type: str
    ) -> Optional[PromptPerformanceProfile]:
        """Get performance profile (async interface for new strategies)."""
        key = f"{prompt_name}_{detection_type}"
        return self._performance_profiles.get(key)

    async def get_top_performers(
        self, detection_type: str, limit: int = 5, min_usage_count: int = 10
    ) -> List[PromptPerformanceProfile]:
        """Get top performers (async interface for new strategies)."""
        relevant_profiles = [
            p
            for p in self._performance_profiles.values()
            if p.detection_type == detection_type
            and p.metrics.usage_count >= min_usage_count
        ]

        # Sort by performance
        sorted_profiles = sorted(
            relevant_profiles,
            key=lambda p: (p.metrics.success_rate, -p.metrics.average_score),
            reverse=True,
        )

        return sorted_profiles[:limit]
