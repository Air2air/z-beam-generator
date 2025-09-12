"""
AI Detection Configuration Validator

Handles configuration validation, backup creation, and file operations
for AI detection configuration optimization.
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import yaml

logger = logging.getLogger(__name__)


class ConfigValidator:
    """Handles configuration validation and file operations."""

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.backup_dir = config_path.parent / "backups"
        self.backup_dir.mkdir(exist_ok=True)

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate the configuration dictionary for correctness.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        try:
            # Basic structure validation
            if not isinstance(config, dict):
                logger.error("Configuration is not a dictionary")
                return False

            # Validate that boolean flags are actually boolean
            for key, value in config.items():
                # Skip metadata fields
                if key.startswith("_"):
                    continue
                    
                # Check that enhancement flags are boolean
                if not isinstance(value, bool):
                    logger.error(f"Configuration flag '{key}' must be boolean, got {type(value)}")
                    return False

            # Additional validation for specific known issues
            if not self._validate_flag_combinations(config):
                return False

            logger.info("Configuration validation passed")
            return True

        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False

    def _validate_flag_combinations(self, config: Dict[str, Any]) -> bool:
        """Validate that flag combinations make sense."""
        try:
            # Example validation: Check for conflicting combinations
            # These are hypothetical conflicts - adjust based on actual requirements
            
            # Check if too many flags are enabled (could indicate parsing error)
            enabled_flags = sum(1 for key, value in config.items() 
                              if not key.startswith("_") and value is True)
            
            if enabled_flags > 20:  # Arbitrary threshold
                logger.warning(f"Many flags enabled ({enabled_flags}), this might indicate an issue")
                # Don't fail validation, just warn
                
            return True
            
        except Exception as e:
            logger.error(f"Flag combination validation failed: {e}")
            return False

    def create_backup(self) -> None:
        """Create a timestamped backup of the current configuration."""
        try:
            if not self.config_path.exists():
                logger.warning("No existing configuration file to backup")
                return

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"ai_detection_backup_{timestamp}.yaml"
            backup_path = self.backup_dir / backup_filename

            shutil.copy2(self.config_path, backup_path)
            logger.info(f"Created configuration backup: {backup_path}")

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")

    def save_config(self, config: Dict[str, Any]) -> None:
        """
        Save the configuration to file.
        
        Args:
            config: Configuration dictionary to save
        """
        try:
            # Ensure parent directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Clean up metadata before saving
            clean_config = {k: v for k, v in config.items() if not k.startswith("_")}

            with open(self.config_path, "w") as f:
                yaml.dump(clean_config, f, default_flow_style=False, sort_keys=True)

            logger.info(f"Saved configuration to {self.config_path}")

        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise

    def rollback_config(self) -> bool:
        """
        Rollback to the most recent backup configuration.
        
        Returns:
            bool: True if rollback successful, False otherwise
        """
        try:
            # Find the most recent backup
            backup_files = list(self.backup_dir.glob("ai_detection_backup_*.yaml"))
            
            if not backup_files:
                logger.warning("No backup files found for rollback")
                return False

            # Sort by modification time (most recent first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            most_recent_backup = backup_files[0]

            # Copy the backup to the main config location
            shutil.copy2(most_recent_backup, self.config_path)
            
            logger.info(f"Successfully rolled back configuration from {most_recent_backup}")
            return True

        except Exception as e:
            logger.error(f"Failed to rollback configuration: {e}")
            return False

    def get_backup_history(self) -> list:
        """
        Get list of available backup files with timestamps.
        
        Returns:
            list: List of backup file information
        """
        try:
            backup_files = list(self.backup_dir.glob("ai_detection_backup_*.yaml"))
            
            backup_info = []
            for backup_file in backup_files:
                backup_info.append({
                    "filename": backup_file.name,
                    "path": str(backup_file),
                    "modified": backup_file.stat().st_mtime,
                    "size": backup_file.stat().st_size
                })
            
            # Sort by modification time (most recent first)
            backup_info.sort(key=lambda x: x["modified"], reverse=True)
            
            return backup_info

        except Exception as e:
            logger.error(f"Failed to get backup history: {e}")
            return []

    def clean_old_backups(self, keep_count: int = 10) -> None:
        """
        Clean up old backup files, keeping only the most recent ones.
        
        Args:
            keep_count: Number of backup files to keep
        """
        try:
            backup_files = list(self.backup_dir.glob("ai_detection_backup_*.yaml"))
            
            if len(backup_files) <= keep_count:
                return
            
            # Sort by modification time (oldest first for deletion)
            backup_files.sort(key=lambda x: x.stat().st_mtime)
            
            # Delete excess backups
            files_to_delete = backup_files[:-keep_count]
            for backup_file in files_to_delete:
                backup_file.unlink()
                logger.info(f"Deleted old backup: {backup_file.name}")
            
            logger.info(f"Cleaned up {len(files_to_delete)} old backup files")

        except Exception as e:
            logger.error(f"Failed to clean old backups: {e}")
