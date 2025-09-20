#!/usr/bin/env python3
"""
Frontmatter Migration Script
Migrates frontmatter from frontmatter/materials/ to root-level frontmatter/
with comprehensive validation and backup capabilities.
"""

import shutil
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import json
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FrontmatterMigrator:
    """Handles migration of frontmatter files to new root-level structure"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.project_root = self._find_project_root()
        self.old_frontmatter_dir = self.project_root / "content" / "components" / "frontmatter"
        self.new_frontmatter_dir = self.project_root / "frontmatter"
        self.new_materials_dir = self.new_frontmatter_dir / "materials"
        self.backup_dir = self.project_root / "backups" / f"frontmatter_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Migration statistics
        self.stats = {
            'total_files': 0,
            'migrated_files': 0,
            'failed_files': 0,
            'backed_up_files': 0
        }
        
        # Files that need path updates
        self.files_to_update = []
        
    def _find_project_root(self) -> Path:
        """Find project root by looking for key files"""
        current = Path.cwd()
        while current != current.parent:
            if (current / "run.py").exists() or (current / "requirements.txt").exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def validate_prerequisites(self) -> bool:
        """Validate that migration can proceed"""
        logger.info("🔍 Validating migration prerequisites...")
        
        if not self.old_frontmatter_dir.exists():
            logger.error(f"❌ Source directory does not exist: {self.old_frontmatter_dir}")
            return False
        
        frontmatter_files = list(self.old_frontmatter_dir.glob("*-laser-cleaning.md"))
        if not frontmatter_files:
            logger.warning("⚠️  No frontmatter files found in source directory")
            return False
        
        self.stats['total_files'] = len(frontmatter_files)
        logger.info(f"✅ Found {self.stats['total_files']} frontmatter files to migrate")
        
        # Check if target directory already exists
        if self.new_materials_dir.exists() and list(self.new_materials_dir.glob("*-laser-cleaning.md")):
            logger.warning(f"⚠️  Target directory already contains frontmatter files: {self.new_materials_dir}")
            response = input("Continue with migration? (y/N): ")
            if response.lower() != 'y':
                return False
        
        return True
    
    def create_backup(self) -> bool:
        """Create backup of existing frontmatter"""
        if self.dry_run:
            logger.info(f"🔄 [DRY RUN] Would create backup at: {self.backup_dir}")
            return True
        
        try:
            logger.info(f"📦 Creating backup at: {self.backup_dir}")
            self.backup_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(self.old_frontmatter_dir, self.backup_dir)
            
            backup_files = list(self.backup_dir.glob("*-laser-cleaning.md"))
            self.stats['backed_up_files'] = len(backup_files)
            logger.info(f"✅ Backup created successfully ({self.stats['backed_up_files']} files)")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create backup: {e}")
            return False
    
    def setup_new_structure(self) -> bool:
        """Create new frontmatter directory structure"""
        if self.dry_run:
            logger.info("🔄 [DRY RUN] Would create new directory structure")
            return True
        
        try:
            logger.info("🏗️  Setting up new frontmatter structure...")
            self.new_frontmatter_dir.mkdir(exist_ok=True)
            self.new_materials_dir.mkdir(exist_ok=True)
            (self.new_frontmatter_dir / "schemas").mkdir(exist_ok=True)
            (self.new_frontmatter_dir / "management").mkdir(exist_ok=True)
            (self.new_frontmatter_dir / "templates").mkdir(exist_ok=True)
            
            logger.info("✅ New directory structure created")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create directory structure: {e}")
            return False
    
    def migrate_files(self) -> bool:
        """Migrate frontmatter files to new location"""
        logger.info("🚚 Migrating frontmatter files...")
        
        frontmatter_files = list(self.old_frontmatter_dir.glob("*-laser-cleaning.md"))
        
        for file_path in frontmatter_files:
            try:
                new_file_path = self.new_materials_dir / file_path.name
                
                if self.dry_run:
                    logger.info(f"🔄 [DRY RUN] Would migrate: {file_path.name}")
                else:
                    shutil.copy2(file_path, new_file_path)
                    logger.debug(f"✅ Migrated: {file_path.name}")
                
                self.stats['migrated_files'] += 1
                
            except Exception as e:
                logger.error(f"❌ Failed to migrate {file_path.name}: {e}")
                self.stats['failed_files'] += 1
        
        if not self.dry_run:
            logger.info(f"✅ Migration completed: {self.stats['migrated_files']} files migrated, {self.stats['failed_files']} failed")
        
        return self.stats['failed_files'] == 0
    
    def find_files_needing_updates(self) -> List[Tuple[Path, str]]:
        """Find all files that reference the old frontmatter path"""
        logger.info("🔍 Scanning for files that need path updates...")
        
        files_to_check = []
        
        # Python files
        files_to_check.extend(self.project_root.rglob("*.py"))
        
        # Config files
        files_to_check.extend(self.project_root.rglob("*.yaml"))
        files_to_check.extend(self.project_root.rglob("*.yml"))
        files_to_check.extend(self.project_root.rglob("*.json"))
        
        # Shell scripts
        files_to_check.extend(self.project_root.rglob("*.sh"))
        
        old_path_patterns = [
            "frontmatter/materials",
            "content\\\\components\\\\frontmatter",  # Windows paths
            "frontmatter_dir.glob",
            "frontmatter/*-laser-cleaning.md"
        ]
        
        files_needing_updates = []
        
        for file_path in files_to_check:
            if file_path.is_file() and not any(exclude in str(file_path) for exclude in ['.git', '__pycache__', '.pytest_cache', 'backups']):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    for pattern in old_path_patterns:
                        if pattern in content:
                            files_needing_updates.append((file_path, pattern))
                            break
                            
                except Exception:
                    continue  # Skip files that can't be read
        
        logger.info(f"📋 Found {len(files_needing_updates)} files that need path updates")
        return files_needing_updates
    
    def generate_update_script(self, files_needing_updates: List[Tuple[Path, str]]) -> Path:
        """Generate a script to update file paths"""
        update_script_path = self.project_root / "frontmatter_path_updates.py"
        
        script_content = '''#!/usr/bin/env python3
"""
Automated path update script for frontmatter migration.
Generated by frontmatter migration tool.
"""

import re
from pathlib import Path

def update_file_paths():
    """Update file paths from old to new frontmatter structure"""
    
    updates = [
        # Path updates
        (r'frontmatter/materials', 'frontmatter/materials'),
        (r'content\\\\components\\\\frontmatter', 'frontmatter/materials'),
        
        # Import updates for new frontmatter manager
        (r'from components\\.frontmatter', 'from frontmatter.management'),
        
        # Variable name updates
        (r'frontmatter_dir = .*frontmatter/materials.*', 
         'frontmatter_dir = Path("frontmatter/materials")'),
    ]
    
    files_to_update = [
'''
        
        for file_path, pattern in files_needing_updates:
            script_content += f'        Path("{file_path.relative_to(self.project_root)}"),\\n'
        
        script_content += '''    ]
    
    for file_path in files_to_update:
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                for old_pattern, new_pattern in updates:
                    content = re.sub(old_pattern, new_pattern, content)
                
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ Updated: {file_path}")
                else:
                    print(f"ℹ️  No changes needed: {file_path}")
                    
            except Exception as e:
                print(f"❌ Error updating {file_path}: {e}")

if __name__ == "__main__":
    update_file_paths()
    print("\\n🎉 Path updates completed!")
'''
        
        if not self.dry_run:
            with open(update_script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            update_script_path.chmod(0o755)  # Make executable
        
        return update_script_path
    
    def create_migration_report(self, files_needing_updates: List[Tuple[Path, str]]) -> Dict:
        """Create comprehensive migration report"""
        report = {
            'migration_summary': {
                'timestamp': datetime.now().isoformat(),
                'dry_run': self.dry_run,
                'project_root': str(self.project_root),
                'source_directory': str(self.old_frontmatter_dir),
                'target_directory': str(self.new_materials_dir),
                'backup_directory': str(self.backup_dir) if not self.dry_run else None
            },
            'statistics': self.stats,
            'files_needing_updates': [
                {
                    'file': str(file_path.relative_to(self.project_root)),
                    'pattern_found': pattern
                }
                for file_path, pattern in files_needing_updates
            ],
            'next_steps': [
                "1. Review migration results",
                "2. Run the generated path update script",
                "3. Update component generators to use new FrontmatterManager",
                "4. Test all functionality with new structure",
                "5. Remove old frontmatter directory when confident"
            ]
        }
        
        return report
    
    def run_migration(self) -> bool:
        """Execute the complete migration process"""
        logger.info("🚀 Starting frontmatter migration...")
        
        if self.dry_run:
            logger.info("🔍 Running in DRY RUN mode - no files will be modified")
        
        # Step 1: Validate prerequisites
        if not self.validate_prerequisites():
            logger.error("❌ Prerequisites validation failed")
            return False
        
        # Step 2: Create backup
        if not self.create_backup():
            logger.error("❌ Backup creation failed")
            return False
        
        # Step 3: Setup new structure
        if not self.setup_new_structure():
            logger.error("❌ Directory structure setup failed")
            return False
        
        # Step 4: Migrate files
        if not self.migrate_files():
            logger.error("❌ File migration failed")
            return False
        
        # Step 5: Find files needing updates
        files_needing_updates = self.find_files_needing_updates()
        
        # Step 6: Generate update script
        update_script_path = self.generate_update_script(files_needing_updates)
        
        # Step 7: Create migration report
        report = self.create_migration_report(files_needing_updates)
        
        # Save report
        report_path = self.project_root / "frontmatter_migration_report.json"
        if not self.dry_run:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
        
        # Print summary
        logger.info("\\n" + "="*60)
        logger.info("📊 MIGRATION SUMMARY")
        logger.info("="*60)
        logger.info(f"📁 Total files: {self.stats['total_files']}")
        logger.info(f"✅ Migrated: {self.stats['migrated_files']}")
        logger.info(f"❌ Failed: {self.stats['failed_files']}")
        logger.info(f"📦 Backed up: {self.stats['backed_up_files']}")
        logger.info(f"🔧 Files needing path updates: {len(files_needing_updates)}")
        
        if not self.dry_run:
            logger.info(f"\\n📋 Report saved to: {report_path}")
            logger.info(f"🔧 Update script created: {update_script_path}")
            logger.info("\\n🎯 Next steps:")
            logger.info("1. Review the migration report")
            logger.info("2. Run: python3 frontmatter_path_updates.py")
            logger.info("3. Test the new frontmatter system")
            logger.info("4. Update component generators")
        else:
            logger.info("\\n🔍 This was a dry run. Use --execute to perform the actual migration.")
        
        return True

def main():
    """Main migration entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate frontmatter to root-level structure")
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--execute', action='store_true', help='Execute the migration')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        logger.info("Please specify either --dry-run or --execute")
        return 1
    
    migrator = FrontmatterMigrator(dry_run=args.dry_run)
    success = migrator.run_migration()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
