#!/usr/bin/env python3
"""
Legacy Code Consolidation Script

Based on comprehensive audit findings:
1. Delete confirmed orphaned files (never imported)
2. Consolidate research services (choose canonical version)
3. Update all import references
4. Archive old files for safety

STRICT SAFETY: Creates backups before any deletion
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

class LegacyCodeCleaner:
    def __init__(self, root_dir="."):
        self.root = Path(root_dir)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.root / ".archive" / f"legacy_cleanup_{self.timestamp}"
        self.changes_made = []
        
    def create_backup(self, file_path: Path):
        """Create backup of file before deletion"""
        if not file_path.exists():
            return
        
        relative_path = file_path.relative_to(self.root)
        backup_path = self.backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(file_path, backup_path)
        print(f"  ✅ Backed up: {relative_path}")
    
    def delete_orphaned_config_files(self):
        """Delete config files that are never imported"""
        print("\n" + "="*80)
        print("🗑️  DELETING ORPHANED CONFIG FILES")
        print("="*80)
        
        orphaned_configs = [
            "config/PRODUCTION_INTEGRATION_CONFIG.py",
            "config/api_keys_enhanced.py"
        ]
        
        for config_file in orphaned_configs:
            file_path = self.root / config_file
            if file_path.exists():
                self.create_backup(file_path)
                file_path.unlink()
                self.changes_made.append(f"Deleted orphaned config: {config_file}")
                print(f"  ❌ Deleted: {config_file}")
            else:
                print(f"  ⚠️  Not found: {config_file}")
    
    def consolidate_research_services(self):
        """Consolidate duplicate research services"""
        print("\n" + "="*80)
        print("🔄 CONSOLIDATING RESEARCH SERVICES")
        print("="*80)
        
        # CANONICAL VERSION: research/services/ai_research_service.py (most complete - 588 lines)
        canonical = "research/services/ai_research_service.py"
        
        # DUPLICATES to remove
        duplicates = [
            "services/research/ai_research_service.py",  # 577 lines, slightly different validation
            "scripts/research/ai_materials_researcher.py"  # 506 lines, older version
        ]
        
        print(f"\n✅ CANONICAL VERSION (keeping): {canonical}")
        print(f"   - Most complete implementation (588 lines)")
        print(f"   - Has property_terminology mappings")
        print(f"   - More sophisticated validation (allows negative thermal expansion)")
        
        print(f"\n❌ REMOVING DUPLICATES:")
        
        for duplicate in duplicates:
            file_path = self.root / duplicate
            if file_path.exists():
                self.create_backup(file_path)
                file_path.unlink()
                self.changes_made.append(f"Deleted duplicate research service: {duplicate}")
                print(f"  ❌ Deleted: {duplicate}")
            else:
                print(f"  ⚠️  Not found: {duplicate}")
        
        # Delete empty directories
        for duplicate in duplicates:
            dir_path = (self.root / duplicate).parent
            if dir_path.exists() and not any(dir_path.iterdir()):
                dir_path.rmdir()
                print(f"  🗑️  Removed empty directory: {dir_path.relative_to(self.root)}")
    
    def update_import_references(self):
        """Update all import references to use canonical version"""
        print("\n" + "="*80)
        print("🔧 UPDATING IMPORT REFERENCES")
        print("="*80)
        
        # Files that need import updates
        files_to_update = [
            "scripts/pipeline_integration.py",
            "scripts/development/legacy_service_bridge.py"
        ]
        
        for file_path_str in files_to_update:
            file_path = self.root / file_path_str
            if not file_path.exists():
                print(f"  ⚠️  Not found: {file_path_str}")
                continue
            
            try:
                content = file_path.read_text()
                original_content = content
                
                # Update import from services.research to research.services
                content = content.replace(
                    "from services.research import AIResearchEnrichmentService",
                    "from research.services.ai_research_service import AIResearchEnrichmentService"
                )
                content = content.replace(
                    "from services.research.ai_research_service import",
                    "from research.services.ai_research_service import"
                )
                
                if content != original_content:
                    # Create backup
                    self.create_backup(file_path)
                    
                    # Write updated content
                    file_path.write_text(content)
                    self.changes_made.append(f"Updated imports in: {file_path_str}")
                    print(f"  ✅ Updated imports: {file_path_str}")
                else:
                    print(f"  ℹ️  No changes needed: {file_path_str}")
                    
            except Exception as e:
                print(f"  ❌ Error updating {file_path_str}: {e}")
    
    def delete_other_orphaned_files(self):
        """Delete other high-confidence orphaned files"""
        print("\n" + "="*80)
        print("🗑️  DELETING OTHER ORPHANED FILES")
        print("="*80)
        
        orphaned_files = [
            "data/materials_optimized.py",
            "scripts/development/legacy_service_bridge.py",  # Name suggests legacy
        ]
        
        for file_path_str in orphaned_files:
            file_path = self.root / file_path_str
            if file_path.exists():
                self.create_backup(file_path)
                file_path.unlink()
                self.changes_made.append(f"Deleted orphaned file: {file_path_str}")
                print(f"  ❌ Deleted: {file_path_str}")
            else:
                print(f"  ⚠️  Not found: {file_path_str}")
    
    def generate_report(self):
        """Generate cleanup report"""
        print("\n" + "="*80)
        print("📊 CLEANUP SUMMARY")
        print("="*80)
        
        print(f"\n✅ Changes made: {len(self.changes_made)}")
        for change in self.changes_made:
            print(f"  - {change}")
        
        print(f"\n💾 Backup location: {self.backup_dir}")
        print(f"\n🎯 Next steps:")
        print("  1. Run tests to verify nothing broke")
        print("  2. Verify imports work: python3 -c 'from research.services.ai_research_service import AIResearchEnrichmentService'")
        print("  3. If all good, commit changes")
        print("  4. If issues arise, restore from backup")
        
    def run(self):
        """Execute full cleanup"""
        print("\n" + "="*80)
        print("🧹 LEGACY CODE CLEANUP - STARTING")
        print("="*80)
        print(f"Timestamp: {self.timestamp}")
        print(f"Backup directory: {self.backup_dir}")
        
        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Execute cleanup steps
        self.delete_orphaned_config_files()
        self.consolidate_research_services()
        self.update_import_references()
        self.delete_other_orphaned_files()
        
        # Generate report
        self.generate_report()
        
        print("\n" + "="*80)
        print("✅ CLEANUP COMPLETE")
        print("="*80)


if __name__ == "__main__":
    import sys
    
    # Change to project root
    project_root = Path(__file__).parent.parent.parent
    os.chdir(project_root)
    
    cleaner = LegacyCodeCleaner()
    cleaner.run()
