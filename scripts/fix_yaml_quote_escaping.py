#!/usr/bin/env python3
"""
Fix YAML Quote Escaping Issues
=====================================

Fixes malformed YAML files where single-quoted strings containing internal
single quotes have been incorrectly escaped or line-wrapped, causing parse errors.

This script:
1. Identifies files with YAML parsing errors
2. Re-saves them with proper double-quote formatting
3. Prevents future issues by using width=1000 to avoid line wrapping
4. Uses default_style='"' for consistent, safe quoting

Affected files (from validation):
- aluminum-laser-cleaning.yaml
- steel-laser-cleaning.yaml
- platinum-laser-cleaning.yaml
- gold-laser-cleaning.yaml
- copper-laser-cleaning.yaml
- brass-laser-cleaning.yaml
- silver-laser-cleaning.yaml
- nickel-laser-cleaning.yaml
- bronze-laser-cleaning.yaml

Usage:
    python3 scripts/fix_yaml_quote_escaping.py [--dry-run]
"""

import sys
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class YAMLQuoteEscapingFixer:
    """Fixes YAML files with quote escaping and line wrapping issues"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.stats = {
            'total_files': 0,
            'fixed': 0,
            'already_valid': 0,
            'errors': 0,
            'files_processed': []
        }
    
    def get_affected_files(self) -> List[Path]:
        """Get list of files with known YAML formatting issues"""
        frontmatter_dir = Path("content/components/frontmatter")
        
        # Files identified by validation as having errors
        problem_files = [
            "aluminum-laser-cleaning.yaml",
            "steel-laser-cleaning.yaml",
            "platinum-laser-cleaning.yaml",
            "gold-laser-cleaning.yaml",
            "copper-laser-cleaning.yaml",
            "brass-laser-cleaning.yaml",
            "silver-laser-cleaning.yaml",
            "nickel-laser-cleaning.yaml",
            "bronze-laser-cleaning.yaml"
        ]
        
        paths = []
        for filename in problem_files:
            path = frontmatter_dir / filename
            if path.exists():
                paths.append(path)
            else:
                print(f"⚠️  File not found: {filename}")
        
        return paths
    
    def test_yaml_validity(self, file_path: Path) -> tuple[bool, str]:
        """Test if YAML file can be parsed successfully"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse
            yaml.safe_load(content)
            return True, "Valid YAML"
            
        except yaml.YAMLError as e:
            return False, f"YAML parse error: {str(e)}"
        except Exception as e:
            return False, f"Read error: {str(e)}"
    
    def load_yaml_file(self, file_path: Path) -> tuple[Dict[Any, Any] | None, str]:
        """Load YAML file, handling various parsing strategies"""
        
        # Strategy 1: Try normal parse
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            data = yaml.safe_load(content)
            return data, "standard_parse"
        except yaml.YAMLError:
            pass
        
        # Strategy 2: Fix problematic apostrophes in quoted strings
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix the specific issue: doubled single quotes (YAML escape) that
            # may have been broken by line wrapping
            import re
            
            # Replace doubled single quotes with single quotes
            # This handles the escape sequence: '' -> '
            fixed_content = content.replace("''", "'")
            
            # Also try to fix single quotes that broke across lines
            # Pattern: 'text continues\n more text' -> should be 'text continues more text'
            fixed_content = re.sub(r"'\s*\n\s+", "' ", fixed_content)
            
            data = yaml.safe_load(fixed_content)
            return data, "quote_fix_parse"
        except yaml.YAMLError:
            pass
        except Exception:
            pass
        
        # Strategy 3: Try unsafe load as last resort
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            data = yaml.unsafe_load(content)
            return data, "unsafe_parse"
        except yaml.YAMLError:
            pass
        
        # Strategy 4: Load using ruamel.yaml which is more forgiving
        try:
            from ruamel.yaml import YAML
            yaml_loader = YAML()
            yaml_loader.preserve_quotes = True
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml_loader.load(f)
            
            # Convert to regular dict if needed
            if hasattr(data, 'items'):
                data = dict(data)
            
            return data, "ruamel_parse"
        except Exception:
            pass
        
        return None, "parse_failed"
    
    def save_yaml_file(self, file_path: Path, data: Dict[Any, Any]) -> bool:
        """Save YAML file with safe formatting"""
        try:
            # Detect if file uses frontmatter format (starts with ---)
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                is_frontmatter_format = first_line == '---'
            
            # Create backup
            if not self.dry_run:
                backup_path = file_path.with_suffix(f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml')
                import shutil
                shutil.copy2(file_path, backup_path)
                print(f"   📋 Backup: {backup_path.name}")
            
            # Save with safe formatting
            if not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    if is_frontmatter_format:
                        f.write("---\n")
                    
                    # Use double-quote style and prevent line wrapping
                    yaml_content = yaml.dump(
                        data,
                        default_flow_style=False,
                        sort_keys=False,
                        allow_unicode=True,
                        width=1000,  # Prevent line wrapping issues
                        default_style='"'  # Use double quotes for safer escaping
                    )
                    f.write(yaml_content)
                    
                    if is_frontmatter_format:
                        f.write("---\n")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error saving: {e}")
            return False
    
    def process_file(self, file_path: Path) -> bool:
        """Process a single file for YAML formatting fixes"""
        print(f"\n📄 Processing: {file_path.name}")
        
        # Test current validity
        is_valid, message = self.test_yaml_validity(file_path)
        
        if is_valid:
            print(f"   ✅ Already valid: {message}")
            self.stats['already_valid'] += 1
            return True
        
        print(f"   ⚠️  Current state: {message}")
        
        # Load with fallback strategies
        data, strategy = self.load_yaml_file(file_path)
        
        if data is None:
            print(f"   ❌ Could not parse file with any strategy")
            self.stats['errors'] += 1
            return False
        
        print(f"   🔄 Loaded using: {strategy}")
        
        # Save with safe formatting
        if self.save_yaml_file(file_path, data):
            if self.dry_run:
                print(f"   🔍 Would fix (dry-run mode)")
            else:
                print(f"   ✅ Fixed and saved")
                
                # Re-verify
                is_valid_now, _ = self.test_yaml_validity(file_path)
                if is_valid_now:
                    print(f"   ✅ Verified: YAML now parses correctly")
                else:
                    print(f"   ⚠️  Warning: Still has parsing issues")
            
            self.stats['fixed'] += 1
            self.stats['files_processed'].append(file_path.name)
            return True
        else:
            self.stats['errors'] += 1
            return False
    
    def run(self):
        """Main execution"""
        print("🔧 YAML Quote Escaping Fixer")
        print("=" * 60)
        
        if self.dry_run:
            print("🔍 DRY RUN MODE - No files will be modified")
            print()
        
        # Get affected files
        files = self.get_affected_files()
        self.stats['total_files'] = len(files)
        
        print(f"\n📊 Found {len(files)} files to check")
        
        # Process each file
        for file_path in files:
            self.process_file(file_path)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Summary")
        print("=" * 60)
        print(f"Total files:      {self.stats['total_files']}")
        print(f"Fixed:            {self.stats['fixed']}")
        print(f"Already valid:    {self.stats['already_valid']}")
        print(f"Errors:           {self.stats['errors']}")
        
        if self.stats['files_processed']:
            print(f"\n✅ Files processed:")
            for filename in self.stats['files_processed']:
                print(f"   • {filename}")
        
        if self.dry_run:
            print("\n🔍 Dry run complete - run without --dry-run to apply fixes")
        else:
            print("\n✅ YAML formatting fixes complete!")

def main():
    parser = argparse.ArgumentParser(
        description="Fix YAML quote escaping and line wrapping issues in frontmatter files"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Show what would be fixed without making changes"
    )
    
    args = parser.parse_args()
    
    fixer = YAMLQuoteEscapingFixer(dry_run=args.dry_run)
    fixer.run()

if __name__ == "__main__":
    main()
