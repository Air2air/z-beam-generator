#!/usr/bin/env python3
"""
Z-Beam Dead Code Cleanup Script

This script identifies and removes dead code, unused files, and legacy components
that are not part of the new clean architecture.

SAFE TO DELETE:
- Old complex run.py and variants
- Legacy test files for old system
- Complex API modules we replaced
- Old generators and processors
- Complex validation systems
- Dead documentation files

MUST KEEP:
- New system: z_beam_generator.py, simple_generator.py, api_client.py
- Legacy assets: components/*/prompt.yaml, schemas/*.json, lists/materials.yaml
- Generated content: content/
- Tests: test_architecture.py, test_requirements.py
"""

import os
import shutil
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DeadCodeCleaner:
    """Identifies and removes dead code safely."""
    
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.deleted_files = []
        self.deleted_dirs = []
        
    def log_action(self, action_type, item):
        """Log what would be or was deleted."""
        prefix = "[DRY RUN] " if self.dry_run else "[DELETED] "
        logger.info(f"{prefix}{action_type}: {item}")
    
    def delete_file(self, filepath):
        """Delete a file (or log if dry run)."""
        self.log_action("FILE", filepath)
        if not self.dry_run:
            try:
                os.remove(filepath)
                self.deleted_files.append(str(filepath))
            except Exception as e:
                logger.error(f"Failed to delete {filepath}: {e}")
    
    def delete_directory(self, dirpath):
        """Delete a directory (or log if dry run)."""
        self.log_action("DIRECTORY", dirpath)
        if not self.dry_run:
            try:
                shutil.rmtree(dirpath)
                self.deleted_dirs.append(str(dirpath))
            except Exception as e:
                logger.error(f"Failed to delete {dirpath}: {e}")
    
    def cleanup_legacy_python_files(self):
        """Remove legacy Python files that are no longer needed."""
        logger.info("🧹 Cleaning up legacy Python files...")
        
        # Legacy files to remove
        legacy_files = [
            "run.py",                           # Old complex main runner
            "run_lightweight.py",               # Unused variant
            "test_realistic_prompt.py",         # Legacy test
            "test_json_parsing.py",             # Legacy test  
            "test_basecomponent_integration.py", # Legacy test
            "test_timeout.py",                  # Legacy test
            "test_debug_logging.py",            # Legacy test
            "test_progress_demo.py",            # Legacy test
            "test_managed_api.py",              # Legacy test
            "test_progress_reporter.py",        # Legacy test
            "test_integrated_progress.py",     # Legacy test
            "test_deepseek_api.py",             # Legacy test
            "test_image_paths.py"               # Legacy test
        ]
        
        for filename in legacy_files:
            filepath = Path(filename)
            if filepath.exists():
                self.delete_file(filepath)
    
    def cleanup_legacy_directories(self):
        """Remove entire legacy directory structures."""
        logger.info("🧹 Cleaning up legacy directories...")
        
        legacy_dirs = [
            "api",                    # Old complex API system (replaced by api_client.py)
            "generators",             # Old generator system (replaced by simple_generator.py)
            "processors",             # Old processing system (not needed)
            "recovery",               # Old recovery system (not needed)
            "aggregate",              # Old aggregation system (not needed) 
            "validators",             # Old complex validation (replaced by simple validation)
            "__pycache__"             # Python cache files
        ]
        
        for dirname in legacy_dirs:
            dirpath = Path(dirname)
            if dirpath.exists() and dirpath.is_dir():
                self.delete_directory(dirpath)
    
    def cleanup_legacy_documentation(self):
        """Remove outdated documentation files."""
        logger.info("🧹 Cleaning up legacy documentation...")
        
        legacy_docs = [
            "BASECOMPONENT_INTEGRATION_COMPLETE.md",
            "TIMEOUT_SOLUTIONS_SUMMARY.md", 
            "DEAD_CODE_CLEANUP_SUMMARY.md",
            "validation_fix_instructions.yaml"
        ]
        
        for filename in legacy_docs:
            filepath = Path(filename)
            if filepath.exists():
                self.delete_file(filepath)
    
    def cleanup_logs(self):
        """Clean up old log files but keep the logs directory."""
        logger.info("🧹 Cleaning up old logs...")
        
        logs_dir = Path("logs")
        if logs_dir.exists():
            for log_file in logs_dir.glob("*.log"):
                # Keep recent z_beam logs, remove old ones
                if "z_beam" not in log_file.name:
                    self.delete_file(log_file)
    
    def identify_dead_component_files(self):
        """Identify unused files in components directory."""
        logger.info("🧹 Cleaning up dead component files...")
        
        components_dir = Path("components")
        if not components_dir.exists():
            return
        
        for component_dir in components_dir.iterdir():
            if not component_dir.is_dir():
                continue
                
            # Keep prompt.yaml files and __init__.py, remove everything else
            for file in component_dir.iterdir():
                if file.name not in ["prompt.yaml", "__init__.py"]:
                    if file.is_file():
                        self.delete_file(file)
                    elif file.is_dir():
                        self.delete_directory(file)
    
    def cleanup_package_files(self):
        """Remove unnecessary package files."""
        logger.info("🧹 Cleaning up package files...")
        
        # These were likely used for old system
        package_files = [
            "package.json",
            "requirements_old.txt"
        ]
        
        for filename in package_files:
            filepath = Path(filename)
            if filepath.exists():
                # Keep requirements.txt but remove others
                if filename != "requirements.txt":
                    self.delete_file(filepath)
    
    def run_cleanup(self):
        """Run the complete cleanup process."""
        logger.info("🚀 Starting dead code cleanup...")
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'ACTUAL DELETION'}")
        
        self.cleanup_legacy_python_files()
        self.cleanup_legacy_directories() 
        self.cleanup_legacy_documentation()
        self.cleanup_logs()
        self.identify_dead_component_files()
        self.cleanup_package_files()
        
        # Summary
        total_files = len(self.deleted_files) if not self.dry_run else "N/A (dry run)"
        total_dirs = len(self.deleted_dirs) if not self.dry_run else "N/A (dry run)"
        
        logger.info("✅ Cleanup completed!")
        logger.info(f"📊 Files processed: {total_files}")
        logger.info(f"📊 Directories processed: {total_dirs}")
        
        if self.dry_run:
            logger.info("🔄 This was a dry run. Use --execute to actually delete files.")


def main():
    """Main cleanup function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up dead code from Z-Beam generator")
    parser.add_argument("--execute", action="store_true", help="Actually delete files (default is dry run)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Warning for actual execution
    if args.execute:
        response = input("⚠️  This will permanently delete files. Are you sure? (yes/no): ")
        if response.lower() != "yes":
            logger.info("❌ Cleanup cancelled.")
            return
    
    # Run cleanup
    cleaner = DeadCodeCleaner(dry_run=not args.execute)
    cleaner.run_cleanup()


if __name__ == "__main__":
    main()
