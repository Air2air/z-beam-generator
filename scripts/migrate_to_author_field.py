#!/usr/bin/env python3
"""
Author Field Migration Script

Migrates all author-related fields to use consistent 'author' key:
1. Renames 'author_object' → 'author' in frontmatter files
2. Renames 'authorInfo' → 'author' in author component files

CRITICAL: This script implements the fail-fast architecture
- No fallbacks or defaults
- Comprehensive backup system  
- Complete validation and error reporting
"""

import logging
import shutil
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

class AuthorFieldMigrator:
    """Migrates author field names across all component files"""
    
    def __init__(self):
        self.backup_dir = None
        self.frontmatter_files_processed = 0
        self.author_files_processed = 0
        self.frontmatter_files_modified = 0  
        self.author_files_modified = 0
        self.errors: List[str] = []
        
    def create_backup(self) -> str:
        """Create timestamped backup directory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"author_field_migration_{timestamp}"
        backup_path = Path("backups") / backup_name
        backup_path.mkdir(parents=True, exist_ok=True)
        
        self.backup_dir = str(backup_path)
        logger.info(f"📁 Created backup directory: {self.backup_dir}")
        return self.backup_dir
        
    def backup_file(self, file_path: str) -> bool:
        """Backup individual file before modification"""
        try:
            if not self.backup_dir:
                raise ValueError("Backup directory not initialized")
                
            source_path = Path(file_path)
            relative_path = source_path.relative_to(Path.cwd())
            backup_file_path = Path(self.backup_dir) / relative_path
            
            # Create parent directories
            backup_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_path, backup_file_path)
            return True
            
        except Exception as e:
            logger.error(f"Failed to backup {file_path}: {e}")
            return False
            
    def migrate_frontmatter_file(self, file_path: str) -> bool:
        """Migrate author_object → author in frontmatter file"""
        try:
            self.frontmatter_files_processed += 1
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            if not isinstance(data, dict):
                logger.warning(f"Skipping non-dict file: {file_path}")
                return True
                
            # Check if migration needed
            if 'author_object' not in data:
                logger.debug(f"No author_object found in {file_path}")
                return True
                
            # Backup file before modification
            if not self.backup_file(file_path):
                self.errors.append(f"Failed to backup {file_path}")
                return False
                
            # Perform migration
            author_data = data.pop('author_object')
            data['author'] = author_data
            
            # Write updated file
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, width=1000)
                
            self.frontmatter_files_modified += 1
            logger.info(f"✅ Migrated frontmatter: {Path(file_path).name}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to migrate frontmatter file {file_path}: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
            
    def migrate_author_component_file(self, file_path: str) -> bool:
        """Migrate authorInfo → author in author component file"""
        try:
            self.author_files_processed += 1
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            if not isinstance(data, dict):
                logger.warning(f"Skipping non-dict file: {file_path}")
                return True
                
            # Check if migration needed  
            if 'authorInfo' not in data:
                logger.debug(f"No authorInfo found in {file_path}")
                return True
                
            # Backup file before modification
            if not self.backup_file(file_path):
                self.errors.append(f"Failed to backup {file_path}")
                return False
                
            # Perform migration
            author_info = data.pop('authorInfo')
            data['author'] = author_info
            
            # Write updated file
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, width=1000)
                
            self.author_files_modified += 1
            logger.info(f"✅ Migrated author component: {Path(file_path).name}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to migrate author component file {file_path}: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
            
    def find_frontmatter_files(self) -> List[str]:
        """Find all frontmatter YAML files"""
        frontmatter_dir = Path("content/components/frontmatter")
        if not frontmatter_dir.exists():
            logger.warning(f"Frontmatter directory not found: {frontmatter_dir}")
            return []
            
        files = list(frontmatter_dir.glob("*.yaml"))
        logger.info(f"📁 Found {len(files)} frontmatter files")
        return [str(f) for f in files]
        
    def find_author_component_files(self) -> List[str]:
        """Find all author component YAML files"""
        author_dir = Path("content/components/author")
        if not author_dir.exists():
            logger.warning(f"Author component directory not found: {author_dir}")
            return []
            
        files = list(author_dir.glob("*.yaml"))
        logger.info(f"📁 Found {len(files)} author component files")
        return [str(f) for f in files]
        
    def validate_migration(self) -> bool:
        """Validate that migration was successful"""
        logger.info("🔍 Validating migration results...")
        
        # Check for any remaining author_object references
        frontmatter_files = self.find_frontmatter_files()
        author_object_found = False
        
        for file_path in frontmatter_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'author_object' in content:
                        logger.error(f"❌ Still found author_object in {file_path}")
                        author_object_found = True
            except Exception as e:
                logger.error(f"Failed to validate {file_path}: {e}")
                
        # Check for any remaining authorInfo references
        author_files = self.find_author_component_files()
        author_info_found = False
        
        for file_path in author_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'authorInfo' in content:
                        logger.error(f"❌ Still found authorInfo in {file_path}")
                        author_info_found = True
            except Exception as e:
                logger.error(f"Failed to validate {file_path}: {e}")
                
        validation_success = not (author_object_found or author_info_found)
        
        if validation_success:
            logger.info("✅ Migration validation passed - no old field names found")
        else:
            logger.error("❌ Migration validation failed - old field names still present")
            
        return validation_success
        
    def run_migration(self) -> bool:
        """Execute complete migration process"""
        logger.info("🚀 Starting Author Field Migration")
        logger.info("=" * 60)
        
        # Create backup
        self.create_backup()
        
        # Find files to migrate
        frontmatter_files = self.find_frontmatter_files()
        author_files = self.find_author_component_files()
        
        if not frontmatter_files and not author_files:
            logger.error("❌ No files found to migrate")
            return False
            
        logger.info(f"📊 Migration plan:")
        logger.info(f"   Frontmatter files: {len(frontmatter_files)}")
        logger.info(f"   Author component files: {len(author_files)}")
        logger.info("")
        
        # Migrate frontmatter files
        logger.info("📝 Migrating frontmatter files (author_object → author)...")
        success = True
        
        for file_path in frontmatter_files:
            if not self.migrate_frontmatter_file(file_path):
                success = False
                
        # Migrate author component files  
        logger.info("👤 Migrating author component files (authorInfo → author)...")
        
        for file_path in author_files:
            if not self.migrate_author_component_file(file_path):
                success = False
                
        # Validate migration
        validation_success = self.validate_migration()
        
        # Print summary
        logger.info("")
        logger.info("📊 Migration Summary:")
        logger.info(f"   Frontmatter files processed: {self.frontmatter_files_processed}")
        logger.info(f"   Frontmatter files modified: {self.frontmatter_files_modified}")
        logger.info(f"   Author component files processed: {self.author_files_processed}")
        logger.info(f"   Author component files modified: {self.author_files_modified}")
        logger.info(f"   Total errors: {len(self.errors)}")
        logger.info(f"   Backup location: {self.backup_dir}")
        
        if self.errors:
            logger.error("")
            logger.error("❌ Errors encountered:")
            for error in self.errors:
                logger.error(f"   - {error}")
                
        final_success = success and validation_success and len(self.errors) == 0
        
        if final_success:
            logger.info("")
            logger.info("🎉 Author field migration completed successfully!")
            logger.info("✅ All author_object fields renamed to author")
            logger.info("✅ All authorInfo fields renamed to author") 
            logger.info("")
            logger.info("📝 Next steps:")
            logger.info("1. Test component generation: python3 run.py --material 'Aluminum' --components author")
            logger.info("2. Run validation: python3 run.py --validate")
            logger.info("3. Deploy changes: python3 run.py --deploy")
        else:
            logger.error("")
            logger.error("❌ Migration failed or incomplete!")
            logger.error("📋 Check error messages above and manual review required")
            
        return final_success


def main():
    """Main execution function"""
    try:
        migrator = AuthorFieldMigrator()
        success = migrator.run_migration()
        
        if not success:
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.error("❌ Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()