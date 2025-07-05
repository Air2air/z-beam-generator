"""
Implementation of prompt selection strategies.
"""

import random
from typing import List
from generator.core.domain.prompt_optimization import SelectionContext
from generator.core.interfaces.prompt_optimization import (
    IPromptSelectionStrategy,
    IPromptPerformanceRepository,
)
from generator.modules.logger import get_logger

logger = get_logger("prompt_selection_strategies")


class PerformanceBasedSelectionStrategy(IPromptSelectionStrategy):
    """
    Selection strategy that prioritizes high-performing prompts.

    Uses performance data to select the best prompt for iteration 1,
    then ensures diversity in subsequent iterations.
    """

    def __init__(self, exploration_rate: float = 0.1):
        """
        Initialize strategy.

        Args:
            exploration_rate: Probability of exploring sub-optimal prompts (0.0-1.0)
        """
        self.exploration_rate = max(0.0, min(1.0, exploration_rate))

    async def select_prompt(
        self,
        context: SelectionContext,
        available_prompts: List[str],
        performance_repo: IPromptPerformanceRepository,
    ) -> str:
        """Select prompt based on performance data and context."""
        if not available_prompts:
            raise ValueError("No available prompts provided")

        # For first iteration, use performance-based selection
        if context.iteration == 1:
            return await self._select_best_performer(
                context, available_prompts, performance_repo
            )

        # For later iterations, ensure diversity while avoiding poor performers
        return await self._select_diverse_prompt(
            context, available_prompts, performance_repo
        )

    async def _select_best_performer(
        self,
        context: SelectionContext,
        available_prompts: List[str],
        performance_repo: IPromptPerformanceRepository,
    ) -> str:
        """Select the best performing prompt based on historical data."""

        # Get performance profiles for all available prompts
        prompt_scores = []
        for prompt_name in available_prompts:
            profile = await performance_repo.get_performance_profile(
                prompt_name, context.detection_type
            )

            if profile and profile.metrics.usage_count >= 3:
                # Calculate combined score: success rate + reliability
                score = (
                    profile.metrics.success_rate * 0.7
                    + profile.metrics.reliability_score * 0.3
                )
                prompt_scores.append((prompt_name, score, profile.metrics.usage_count))
            else:
                # Unknown or insufficiently tested prompts get medium priority
                prompt_scores.append((prompt_name, 0.5, 0))

        if not prompt_scores:
            return available_prompts[0]

        # Sort by score, then by usage count for tie-breaking
        prompt_scores.sort(key=lambda x: (x[1], x[2]), reverse=True)

        # Exploration vs exploitation
        if random.random() < self.exploration_rate:
            # Explore: choose randomly from top 50%
            top_half_size = max(1, len(prompt_scores) // 2)
            selected_prompt = random.choice(prompt_scores[:top_half_size])[0]
            logger.debug(f"Exploration: selected {selected_prompt}")
        else:
            # Exploit: choose best performer
            selected_prompt = prompt_scores[0][0]
            logger.debug(
                f"Exploitation: selected {selected_prompt} (score: {prompt_scores[0][1]:.3f})"
            )

        return selected_prompt

    async def _select_diverse_prompt(
        self,
        context: SelectionContext,
        available_prompts: List[str],
        performance_repo: IPromptPerformanceRepository,
    ) -> str:
        """Select prompt ensuring diversity and avoiding poor performers."""

        # Filter out consistently poor performers
        viable_prompts = []
        for prompt_name in available_prompts:
            profile = await performance_repo.get_performance_profile(
                prompt_name, context.detection_type
            )

            # Include prompt if:
            # 1. No data available (give it a chance)
            # 2. Success rate >= 20% (not terrible)
            # 3. Insufficient data but not consistently failing
            if (
                not profile
                or profile.metrics.usage_count < 5
                or profile.metrics.success_rate >= 0.2
            ):
                viable_prompts.append(prompt_name)

        if not viable_prompts:
            # If all prompts are poor, use all available (something's wrong)
            viable_prompts = available_prompts
            logger.warning("All prompts appear to be poor performers")

        # Select based on iteration to ensure variety
        selection_index = (context.iteration - 1) % len(viable_prompts)
        selected_prompt = viable_prompts[selection_index]

        logger.debug(
            f"Diversity selection: iteration {context.iteration}, "
            f"selected {selected_prompt} from {len(viable_prompts)} viable prompts"
        )

        return selected_prompt

    def get_strategy_name(self) -> str:
        """Get strategy name."""
        return "performance_based"


class RoundRobinSelectionStrategy(IPromptSelectionStrategy):
    """
    Simple round-robin selection strategy for testing and comparison.
    """

    async def select_prompt(
        self,
        context: SelectionContext,
        available_prompts: List[str],
        performance_repo: IPromptPerformanceRepository,
    ) -> str:
        """Select prompt using round-robin approach."""
        if not available_prompts:
            raise ValueError("No available prompts provided")

        # Simple round-robin based on iteration
        selection_index = (context.iteration - 1) % len(available_prompts)
        selected_prompt = available_prompts[selection_index]

        logger.debug(
            f"Round-robin: iteration {context.iteration}, selected {selected_prompt}"
        )
        return selected_prompt

    def get_strategy_name(self) -> str:
        """Get strategy name."""
        return "round_robin"


class RandomSelectionStrategy(IPromptSelectionStrategy):
    """
    Random selection strategy for baseline comparison.
    """

    async def select_prompt(
        self,
        context: SelectionContext,
        available_prompts: List[str],
        performance_repo: IPromptPerformanceRepository,
    ) -> str:
        """Select prompt randomly."""
        if not available_prompts:
            raise ValueError("No available prompts provided")

        selected_prompt = random.choice(available_prompts)
        logger.debug(f"Random selection: {selected_prompt}")
        return selected_prompt

    def get_strategy_name(self) -> str:
        """Get strategy name."""
        return "random"
