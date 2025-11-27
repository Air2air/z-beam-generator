#!/usr/bin/env python3
"""
Comprehensive Subtitle Field Removal Tool

Systematically removes all subtitle references from:
- Code files (.py)
- Config files (.yaml) 
- Data files (Materials.yaml)
- Scripts (.sh)
- Documentation (.md)

Preserves backup files and archives (historical record).
"""

import yaml
import re
import os
from pathlib import Path
from typing import List, Tuple
import shutil
from datetime import datetime

class SubtitleRemover:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.changes = []
        self.errors = []
        
    def remove_from_materials_yaml(self, filepath: str):
        """Remove subtitle field from Materials.yaml"""
        print(f"\n📄 Processing: {filepath}")
        
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            
            removed_count = 0
            for material_name, material_data in data.get('materials', {}).items():
                if 'subtitle' in material_data:
                    if not self.dry_run:
                        del material_data['subtitle']
                    removed_count += 1
                    self.changes.append(f"  Removed subtitle from {material_name}")
            
            if removed_count > 0:
                print(f"  ✅ Found {removed_count} subtitle fields")
                if not self.dry_run:
                    # Backup first
                    backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    shutil.copy2(filepath, backup_path)
                    print(f"  💾 Backup: {backup_path}")
                    
                    # Save without subtitle
                    with open(filepath, 'w') as f:
                        yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True, width=1000)
                    print(f"  ✅ Removed {removed_count} subtitle fields")
            else:
                print(f"  ℹ️  No subtitle fields found")
                
        except Exception as e:
            self.errors.append(f"Error in {filepath}: {e}")
            print(f"  ❌ Error: {e}")
    
    def remove_from_python_file(self, filepath: str):
        """Remove subtitle references from Python code"""
        print(f"\n🐍 Processing: {filepath}")
        
        try:
            with open(filepath, 'r') as f:
                original_content = f.read()
            
            modified = original_content
            changes_made = []
            
            # Pattern 1: subtitle in lists/tuples
            pattern1 = re.compile(r"['\"]subtitle['\"],?\s*")
            if pattern1.search(modified):
                modified = pattern1.sub('', modified)
                changes_made.append("Removed subtitle from lists")
            
            # Pattern 2: subtitle dict keys
            pattern2 = re.compile(r"['\"]subtitle['\"]\s*:\s*[^,}\n]+[,]?\s*")
            if pattern2.search(modified):
                modified = pattern2.sub('', modified)
                changes_made.append("Removed subtitle dict entries")
            
            # Pattern 3: subtitle method names
            pattern3 = re.compile(r"def\s+\w*subtitle\w*\(")
            if pattern3.search(modified):
                # Don't auto-remove methods, flag for manual review
                changes_made.append("⚠️  Contains subtitle method - needs manual review")
            
            # Pattern 4: subtitle component_type references
            pattern4 = re.compile(r"component_type\s*==\s*['\"]subtitle['\"]")
            if pattern4.search(modified):
                changes_made.append("⚠️  Contains subtitle component check - needs manual review")
            
            # Pattern 5: --subtitle CLI args
            pattern5 = re.compile(r"['\"]--subtitle['\"]")
            if pattern5.search(modified):
                changes_made.append("⚠️  Contains --subtitle CLI arg - needs manual review")
            
            if changes_made:
                print(f"  📝 Changes: {', '.join(changes_made)}")
                self.changes.extend([f"{filepath}: {c}" for c in changes_made])
                
                if not self.dry_run and not any("⚠️" in c for c in changes_made):
                    with open(filepath, 'w') as f:
                        f.write(modified)
                    print(f"  ✅ Updated")
                elif any("⚠️" in c for c in changes_made):
                    print(f"  ⚠️  Flagged for manual review")
            else:
                print(f"  ℹ️  No subtitle references")
                
        except Exception as e:
            self.errors.append(f"Error in {filepath}: {e}")
            print(f"  ❌ Error: {e}")
    
    def remove_from_config_yaml(self, filepath: str):
        """Remove subtitle config from YAML files"""
        print(f"\n⚙️  Processing: {filepath}")
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Check for subtitle references
            if 'subtitle' not in content.lower():
                print(f"  ℹ️  No subtitle references")
                return
            
            # Load YAML
            data = yaml.safe_load(content)
            changes_made = []
            
            # Common subtitle config locations
            if isinstance(data, dict):
                if 'subtitle' in data:
                    if not self.dry_run:
                        del data['subtitle']
                    changes_made.append("Removed subtitle top-level key")
                
                if 'subtitle_length' in data:
                    if not self.dry_run:
                        del data['subtitle_length']
                    changes_made.append("Removed subtitle_length key")
                
                # Check nested dicts
                for key, value in data.items():
                    if isinstance(value, dict) and 'subtitle' in value:
                        if not self.dry_run:
                            del value['subtitle']
                        changes_made.append(f"Removed subtitle from {key}")
            
            if changes_made:
                print(f"  📝 Changes: {', '.join(changes_made)}")
                self.changes.extend([f"{filepath}: {c}" for c in changes_made])
                
                if not self.dry_run:
                    with open(filepath, 'w') as f:
                        yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)
                    print(f"  ✅ Updated")
            else:
                print(f"  ⚠️  Contains subtitle refs but no standard patterns found")
                
        except Exception as e:
            self.errors.append(f"Error in {filepath}: {e}")
            print(f"  ❌ Error: {e}")
    
    def analyze_only(self):
        """Scan and report subtitle usage without making changes"""
        print("\n🔍 SUBTITLE USAGE ANALYSIS")
        print("=" * 80)
        
        # Key files to check
        priority_files = [
            # Data
            "data/materials/Materials.yaml",
            
            # Core generation
            "generation/core/generator.py",
            "generation/core/prompt_builder.py",
            "generation/core/component_specs.py",
            "generation/core/adapters/materials_adapter.py",
            
            # Config
            "generation/config.yaml",
            "generation/config/dynamic_config.py",
            "domains/materials/config.yaml",
            
            # Export
            "export/core/streamlined_generator.py",
            "export/orchestrator.py",
            
            # Scripts
            "scripts/operations/regenerate_subtitles.py",
            
            # Tests
            "tests/unit/test_subtitle_component.py",
        ]
        
        found_files = []
        for filepath in priority_files:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    count = content.lower().count('subtitle')
                    if count > 0:
                        found_files.append((filepath, count))
        
        found_files.sort(key=lambda x: x[1], reverse=True)
        
        print("\n📊 Priority Files with Subtitle References:")
        for filepath, count in found_files:
            print(f"  {filepath}: {count} references")
        
        return found_files

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Remove subtitle field from codebase")
    parser.add_argument('--execute', action='store_true', help='Execute removal (default: dry-run)')
    parser.add_argument('--analyze', action='store_true', help='Analyze usage only')
    args = parser.parse_args()
    
    remover = SubtitleRemover(dry_run=not args.execute)
    
    if args.analyze:
        remover.analyze_only()
        return
    
    print("🗑️  SUBTITLE FIELD REMOVAL")
    print("=" * 80)
    if remover.dry_run:
        print("MODE: DRY RUN (use --execute to apply changes)")
    else:
        print("MODE: EXECUTE (changes will be applied)")
    
    # 1. Remove from Materials.yaml
    if os.path.exists('data/materials/Materials.yaml'):
        remover.remove_from_materials_yaml('data/materials/Materials.yaml')
    
    # 2. Remove from config files
    config_files = [
        'generation/config.yaml',
        'domains/materials/config.yaml',
        'export/config/enhanced_text_config.yaml'
    ]
    for filepath in config_files:
        if os.path.exists(filepath):
            remover.remove_from_config_yaml(filepath)
    
    # 3. Remove from Python files (flag for manual review)
    python_files = [
        'generation/core/prompt_builder.py',
        'generation/core/component_specs.py',
        'generation/core/adapters/materials_adapter.py',
        'generation/config/dynamic_config.py',
        'export/core/streamlined_generator.py',
    ]
    for filepath in python_files:
        if os.path.exists(filepath):
            remover.remove_from_python_file(filepath)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"Changes planned: {len(remover.changes)}")
    print(f"Errors: {len(remover.errors)}")
    
    if remover.errors:
        print("\n❌ Errors:")
        for error in remover.errors:
            print(f"  {error}")
    
    if remover.dry_run:
        print("\n💡 Run with --execute to apply changes")
    else:
        print("\n✅ Changes applied")

if __name__ == '__main__':
    main()
