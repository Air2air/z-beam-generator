#!/usr/bin/env python3
"""
Automatic Version Bumper for AI Detection Prompts
Integrates with the iterative optimization system to automatically version changes.
"""

import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the version manager directly
sys.path.append(str(Path(__file__).parent))
from .version_manager import AIDetectionVersionManager

logger = logging.getLogger(__name__)


class AutoVersionBumper:
    """Automatically manages versioning during iterative optimization."""

    def __init__(self, config_path: str = "components/text/prompts/ai_detection.yaml"):
        self.version_manager = AIDetectionVersionManager(config_path)
        self.last_version = self.version_manager.get_current_version()

    def check_and_bump_version(
        self, iteration_data: dict, winston_score: float, previous_score: float = None
    ) -> bool:
        """
        Check if version should be bumped based on iteration results.

        Args:
            iteration_data: Data from the current iteration
            winston_score: Current Winston AI detection score
            previous_score: Previous iteration's score

        Returns:
            True if version was bumped, False otherwise
        """
        try:
            # Determine if this is a significant improvement
            significant_improvement = False
            if previous_score is not None:
                improvement = (
                    previous_score - winston_score
                )  # Lower score = better (less AI-like)
                if improvement >= 15:  # 15+ point improvement
                    significant_improvement = True
                    logger.info(
                        f"📈 Significant improvement detected: +{improvement:.1f} points"
                    )

            # Check for major pattern changes
            major_changes = self._detect_major_changes(iteration_data)

            # Determine bump type
            if major_changes:
                bump_type = "minor"
                changelog = f"Major pattern changes: {', '.join(major_changes)}"
            elif significant_improvement:
                bump_type = "patch"
                changelog = f"Performance improvement: {winston_score:.1f} score"
            else:
                return False  # No version bump needed

            # Bump the version
            success = self.version_manager.bump_version(
                bump_type=bump_type,
                changelog_entry=changelog,
                author="Iterative Optimization System",
            )

            if success:
                new_version = self.version_manager.get_current_version()
                logger.info(f"🔖 Auto-bumped version to {new_version}: {changelog}")
                self.last_version = new_version

            return success

        except Exception as e:
            logger.warning(f"Failed to auto-bump version: {e}")
            return False

    def _detect_major_changes(self, iteration_data: dict) -> list:
        """Detect major changes that warrant a version bump."""
        major_changes = []

        # Check for new enhancement types
        enhancements_applied = iteration_data.get("enhancements_applied", [])
        if "paragraph_structure" in enhancements_applied:
            major_changes.append("paragraph structure optimization")
        if "lexical_diversity" in enhancements_applied:
            major_changes.append("lexical diversity enhancement")
        if "sentence_variability" in enhancements_applied:
            major_changes.append("sentence variability patterns")

        # Check for significant content changes
        content_change_percent = iteration_data.get("content_change_percent_words", 0)
        if content_change_percent > 50:  # Major content restructuring
            major_changes.append("major content restructuring")

        # Check for DeepSeek optimization
        if iteration_data.get("deepseek_response"):
            major_changes.append("DeepSeek optimization applied")

        return major_changes

    def get_version_info(self) -> dict:
        """Get current version information."""
        return {
            "current_version": self.version_manager.get_current_version(),
            "last_updated": self.version_manager.get_current_date(),
            "version_history": self.version_manager.get_version_history(),
        }


def integrate_with_optimization(
    auto_bumper: AutoVersionBumper,
    iteration_data: dict,
    winston_score: float,
    previous_score: float = None,
):
    """
    Integration function for the iterative optimization system.

    Call this function at the end of each iteration to automatically manage versioning.
    """
    try:
        version_bumped = auto_bumper.check_and_bump_version(
            iteration_data=iteration_data,
            winston_score=winston_score,
            previous_score=previous_score,
        )

        if version_bumped:
            logger.info("✅ Version automatically updated based on iteration results")
        else:
            logger.debug("ℹ️ No version change needed for this iteration")

    except Exception as e:
        logger.warning(f"Version auto-bumping failed: {e}")


# Example usage in the generator.py file:
"""
# At the end of each iteration in generator.py, add:

from components.text.prompts.auto_version_bumper import AutoVersionBumper

# Initialize bumper (do this once at the start)
auto_bumper = AutoVersionBumper()

# At the end of each iteration:
iteration_data_copy = iteration_data.copy()  # Make a copy to avoid modifying original
integrate_with_optimization(
    auto_bumper=auto_bumper,
    iteration_data=iteration_data_copy,
    winston_score=current_score,
    previous_score=previous_score
)
"""

if __name__ == "__main__":
    # Test the auto version bumper
    bumper = AutoVersionBumper()

    # Test with mock iteration data
    test_iteration_data = {
        "enhancements_applied": ["paragraph_structure", "sentence_variability"],
        "content_change_percent_words": 25.0,
        "deepseek_response": "Optimization applied",
    }

    print("Testing auto version bumping...")
    success = bumper.check_and_bump_version(
        iteration_data=test_iteration_data, winston_score=45.0, previous_score=60.0
    )

    if success:
        print("✅ Version bump test successful")
    else:
        print("ℹ️ No version bump needed (test)")

    # Show current version info
    info = bumper.get_version_info()
    print(f"Current Version: {info['current_version']}")
    print(f"Last Updated: {info['last_updated']}")
