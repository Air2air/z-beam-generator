"""
AI Detection Prompt Optimizer

This module extends the AIDetectionConfigOptimizer to automatically update
the ai_detection.yaml prompt file based on Winston AI analysis results.
Updates are targeted and incremental to avoid bloat.
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from api.client_manager import create_api_client

from .ai_detection_config_optimizer import AIDetectionConfigOptimizer

logger = logging.getLogger(__name__)


class AIDetectionPromptOptimizer(AIDetectionConfigOptimizer):
    """Extends AIDetectionConfigOptimizer to update prompt files."""

    def __init__(self, config_path: str = "config/ai_detection.yaml"):
        super().__init__(config_path)
        self.prompts_path = Path("components/text/prompts/ai_detection.yaml")

    def update_prompts_based_on_results(self, winston_results: Dict[str, Any]) -> bool:
        """Update prompts based on Winston AI analysis results."""
        try:
            # Load current prompts
            if not self.prompts_path.exists():
                logger.warning(f"Prompts file not found: {self.prompts_path}")
                return False

            with open(self.prompts_path, "r", encoding="utf-8") as f:
                prompts = yaml.safe_load(f)

            # Analyze results and update prompts
            updated_prompts = self._optimize_prompts_for_results(
                prompts, winston_results
            )

            # Convert config values back to template variables
            yaml_content = yaml.dump(
                updated_prompts,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            )

            # For now, save to the core file (this is a limitation of the current approach)
            # A more sophisticated implementation would update individual modular components
            core_path = Path("components/text/prompts/ai_detection_core.yaml")
            with open(core_path, "w", encoding="utf-8") as f:
                f.write(yaml_content)

            logger.info(
                f"Saved updated prompts to {core_path} (modular components not updated)"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save updated prompts: {e}")
            return False

    def _optimize_prompts_for_results(
        self, prompts: Dict[str, Any], results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize prompts based on analysis results."""
        # This is a placeholder implementation
        # In a real implementation, this would analyze the results and make targeted updates
        return prompts

    def restore_backup(self, backup_timestamp: Optional[str] = None) -> bool:
        """Restore prompts from backup."""
        try:
            if backup_timestamp:
                backup_path = self.prompts_path.with_suffix(
                    f".backup_{backup_timestamp}.yaml"
                )
            else:
                # Find the most recent backup
                backup_files = list(
                    self.prompts_path.parent.glob(
                        f"{self.prompts_path.stem}.backup_*.yaml"
                    )
                )
                if not backup_files:
                    logger.warning("No prompt backup files found")
                    return False
                backup_path = max(backup_files, key=lambda p: p.stat().st_mtime)

            if backup_path.exists():
                backup_content = backup_path.read_text(encoding="utf-8")
                self.prompts_path.write_text(backup_content, encoding="utf-8")
                logger.info(f"Restored prompts from backup: {backup_path}")
                return True
            else:
                logger.warning(f"Backup file not found: {backup_path}")
                return False

        except Exception as e:
            logger.error(f"Failed to restore prompts backup: {e}")
            return False
