"""
Word Budget Manager for efficient content generation.
Manages word allocation across sections and prevents excessive API usage.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from generator.modules.logger import get_logger

logger = get_logger("word_budget_manager")


@dataclass
class SectionBudget:
    """Word budget allocation for a section."""

    name: str
    target_words: int
    percentage: float  # Percentage of total article words
    priority: float = 1.0  # Higher priority gets more words if available


@dataclass
class ContentMetrics:
    """Metrics for generated content."""

    word_count: int
    character_count: int
    within_budget: bool
    utilization: float  # percentage of target words used


class WordBudgetManager:
    """Manages word budgets across article sections to optimize API usage."""

    def __init__(self, total_article_words: int = 1200):
        self.total_article_words = total_article_words
        self.section_budgets: Dict[str, SectionBudget] = {}
        self.allocated_words = 0
        self.logger = logger

        # Default section priorities and allocations (as percentages)
        self.default_allocations = {
            "introduction": 0.15,  # 15% of total article
            "material_research": 0.20,  # 20% of total article
            "contaminants": 0.15,  # 15% of total article
            "substrates": 0.15,  # 15% of total article
            "comparison": 0.20,  # 20% of total article
            "conclusion": 0.10,  # 10% of total article
            "table": 0.05,  # 5% of total article (data tables)
            "chart": 0.05,  # 5% of total article (charts)
        }

    def allocate_budgets(self, sections: List[str]) -> Dict[str, SectionBudget]:
        """Allocate word budgets to sections based on percentages of total article words."""
        self.logger.info(
            f"Allocating {self.total_article_words} words across {len(sections)} sections"
        )

        # Calculate total allocation percentage for provided sections
        total_allocation = sum(
            self.default_allocations.get(section, 0.1) for section in sections
        )

        # If sections don't match defaults, distribute evenly
        if total_allocation == 0:
            allocation_per_section = 1.0 / len(sections)
            self.logger.warning(
                f"No default allocations found, distributing evenly: {allocation_per_section:.2%} per section"
            )
        else:
            # Normalize allocations to 100%
            allocation_per_section = None

        for section in sections:
            if total_allocation > 0:
                section_percentage = (
                    self.default_allocations.get(section, 0.1) / total_allocation
                )
            else:
                section_percentage = allocation_per_section

            target_words = int(self.total_article_words * section_percentage)

            budget = SectionBudget(
                name=section,
                target_words=target_words,
                percentage=section_percentage,
                priority=self.default_allocations.get(section, 0.1),
            )

            self.section_budgets[section] = budget
            self.allocated_words += target_words

            self.logger.info(
                f"Section '{section}': {target_words} words ({section_percentage:.1%} of total)"
            )

        return self.section_budgets

    def get_section_budget(self, section_name: str) -> Optional[SectionBudget]:
        """Get the budget for a specific section."""
        return self.section_budgets.get(section_name)

    def calculate_max_tokens(self, section_name: str) -> int:
        """Calculate appropriate max_tokens for API call based on word budget."""
        budget = self.get_section_budget(section_name)
        if not budget:
            # Fallback for unknown sections
            self.logger.warning(
                f"No budget found for section '{section_name}', using default"
            )
            return 2000

        # Rough estimate: 1 word ≈ 1.3 tokens, add 30% buffer for API overhead
        # Use target_words as the limit (no separate max_words)
        estimated_tokens = int(budget.target_words * 1.3 * 1.3)

        # Ensure reasonable bounds
        max_tokens = max(500, min(estimated_tokens, 8000))

        self.logger.debug(
            f"Section '{section_name}': {budget.target_words} target words → {max_tokens} max tokens"
        )
        return max_tokens

    def analyze_content(self, content: str, section_name: str) -> ContentMetrics:
        """Analyze content against section budget."""
        word_count = len(content.split())
        character_count = len(content)

        budget = self.get_section_budget(section_name)
        if not budget:
            # No budget set, assume it's within limits
            return ContentMetrics(
                word_count=word_count,
                character_count=character_count,
                within_budget=True,
                utilization=0.0,
            )

        # Consider content "within budget" if it's within 30% of target
        # (no strict min/max ranges, just target-based evaluation)
        target_tolerance = 0.3  # 30% tolerance
        lower_bound = budget.target_words * (1 - target_tolerance)
        upper_bound = budget.target_words * (1 + target_tolerance)
        within_budget = lower_bound <= word_count <= upper_bound

        utilization = (
            word_count / budget.target_words if budget.target_words > 0 else 0.0
        )

        metrics = ContentMetrics(
            word_count=word_count,
            character_count=character_count,
            within_budget=within_budget,
            utilization=utilization,
        )

        self.logger.info(
            f"Section '{section_name}': {word_count} words "
            f"(target: {budget.target_words}, {budget.percentage:.1%} of total) "
            f"- {'✅' if within_budget else '⚠️'} {utilization:.1%} utilization"
        )

        return metrics

    def should_skip_detection(
        self, content: str, section_name: str, iteration: int
    ) -> bool:
        """Determine if detection should be skipped to save API calls."""
        metrics = self.analyze_content(content, section_name)

        # For optimization mode, be less aggressive about skipping detection
        # Only skip if content is way over budget (needs length reduction first)

        if metrics.utilization > 2.0:  # 100% over budget (was 1.5/50%)
            self.logger.info(
                f"Skipping detection for '{section_name}' - content too long ({metrics.utilization:.1%} of target)"
            )
            return True

        # Remove the "iteration > 2 and within_budget" skip for better optimization
        # This was preventing detection optimization from running

        if metrics.word_count < 50:  # Very short content (reduced from 100)
            self.logger.info(
                f"Skipping detection for '{section_name}' - content too short for meaningful detection"
            )
            return True

        return False

    def get_budget_summary(self) -> Dict[str, any]:
        """Get summary of all section budgets."""
        return {
            "total_article_words": self.total_article_words,
            "allocated_words": self.allocated_words,
            "sections": {
                name: {
                    "target_words": budget.target_words,
                    "priority": budget.priority,
                    "percentage": f"{(budget.target_words / self.total_article_words) * 100:.1f}%",
                }
                for name, budget in self.section_budgets.items()
            },
        }

    def adjust_prompt_for_budget(self, prompt: str, section_name: str) -> str:
        """Inject word count constraints into the prompt."""
        budget = self.get_section_budget(section_name)
        if not budget:
            return prompt

        # Add word count constraint to the prompt (target words as maximum guidance)
        word_constraint = f"\n\nIMPORTANT: Keep your response to approximately {budget.target_words} words maximum. This section should aim for {budget.target_words} words or fewer as part of a {self.total_article_words}-word article."

        return prompt + word_constraint

    def log_iteration_stats(
        self,
        section_name: str,
        iteration: int,
        content: str,
        ai_score=None,
        human_score=None,
        previous_content: str = None,
    ) -> None:
        """Log detailed iteration statistics including improvements and metrics."""
        metrics = self.analyze_content(content, section_name)
        budget = self.get_section_budget(section_name)

        # Calculate content changes if previous content provided
        content_change_info = ""
        if previous_content:
            prev_word_count = len(previous_content.split())
            word_change = metrics.word_count - prev_word_count
            if word_change != 0:
                change_indicator = "↑" if word_change > 0 else "↓"
                content_change_info = (
                    f" (changed: {change_indicator}{abs(word_change)} words)"
                )

        # Format the iteration header
        self.logger.info(f"📊 ITERATION {iteration} STATS - {section_name.upper()}")
        self.logger.info(
            f"   📏 Words: {metrics.word_count}"
            + (f"/{budget.target_words}" if budget else "")
            + content_change_info
        )

        if budget:
            self.logger.info(
                f"   🎯 Budget: {metrics.utilization:.1%} utilization "
                + ("✅ within target" if metrics.within_budget else "⚠️ outside target")
            )

        if ai_score and human_score:
            self.logger.info(
                f"   🤖 AI Score: {ai_score.score}% | 👤 Human Score: {human_score.score}%"
            )

        self.logger.info(f"   📈 Characters: {metrics.character_count}")

    def log_section_summary(
        self,
        section_name: str,
        final_content: str,
        iterations_completed: int,
        threshold_met: bool = False,
    ) -> None:
        """Log final section generation summary."""
        metrics = self.analyze_content(final_content, section_name)
        budget = self.get_section_budget(section_name)

        status = "✅ SUCCESS" if threshold_met else "⚠️ COMPLETED"
        self.logger.info(f"🎉 {status} - {section_name.upper()} FINAL SUMMARY")
        self.logger.info(
            f"   📊 Final word count: {metrics.word_count}"
            + (f"/{budget.target_words}" if budget else "")
        )
        if budget:
            self.logger.info(
                f"   🎯 Budget utilization: {metrics.utilization:.1%} "
                + ("(within target)" if metrics.within_budget else "(outside target)")
            )
        self.logger.info(f"   🔄 Iterations used: {iterations_completed}")
        self.logger.info(f"   📈 Final length: {metrics.character_count} characters")
