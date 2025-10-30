#!/usr/bin/env python3
"""
Fix Frontmatter YAML Formatting Issues
======================================

Fixes the JSON-style formatting issues introduced during caption generation:
1. Removes excessive quoted strings (keys and values)
2. Removes unnecessary YAML type tags (!!float, !!int, !!null)
3. Fixes quoted null values
4. Normalizes to clean YAML format matching the project standard

This script loads YAML, normalizes it, and re-saves with proper formatting.
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class YAMLNormalizer:
    """
    Custom YAML dumper that produces clean, unquoted YAML output
    matching the project's standard formatting.
    """
    
    @staticmethod
    def represent_none(dumper, data):
        """Represent None as null without quotes"""
        return dumper.represent_scalar('tag:yaml.org,2002:null', 'null')
    
    @staticmethod
    def represent_str(dumper, data):
        """Represent strings without quotes when possible"""
        if '\n' in data or ':' in data or data.startswith((' ', '-')):
            # Use quoted style for multi-line or special strings
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)
    
    @staticmethod
    def represent_bool(dumper, data):
        """Represent booleans as true/false"""
        return dumper.represent_scalar('tag:yaml.org,2002:bool', 
                                      'true' if data else 'false')


class FrontmatterYAMLFixer:
    """Fix YAML formatting issues in frontmatter files"""
    
    def __init__(self):
        self.processed_count = 0
        self.fixed_count = 0
        self.error_count = 0
        self.errors = []
        
        # Configure custom YAML dumper
        self.setup_yaml_dumper()
    
    def setup_yaml_dumper(self):
        """Setup custom YAML dumper with clean formatting"""
        # Create custom dumper class
        class CleanYAMLDumper(yaml.SafeDumper):
            pass
        
        # Register custom representers
        CleanYAMLDumper.add_representer(type(None), YAMLNormalizer.represent_none)
        CleanYAMLDumper.add_representer(str, YAMLNormalizer.represent_str)
        CleanYAMLDumper.add_representer(bool, YAMLNormalizer.represent_bool)
        
        self.dumper = CleanYAMLDumper
    
    def fix_all_frontmatter(self, 
                           frontmatter_dir: str = "content/components/frontmatter",
                           dry_run: bool = False) -> Dict[str, Any]:
        """Fix all frontmatter files in the specified directory"""
        print("🔧 Starting YAML formatting fix for frontmatter files...")
        print(f"📂 Directory: {frontmatter_dir}")
        
        if dry_run:
            print("🔍 DRY RUN MODE - No files will be modified")
        
        frontmatter_path = Path(frontmatter_dir)
        if not frontmatter_path.exists():
            print(f"❌ Frontmatter directory not found: {frontmatter_dir}")
            return {"success": False, "error": "Directory not found"}
        
        # Find all YAML frontmatter files
        frontmatter_files = list(frontmatter_path.glob("*-laser-cleaning.yaml"))
        total_files = len(frontmatter_files)
        
        print(f"📋 Found {total_files} frontmatter files to process\n")
        
        # Process each file
        for i, file_path in enumerate(sorted(frontmatter_files), 1):
            material_name = file_path.stem.replace("-laser-cleaning", "").replace("-", " ").title()
            print(f"[{i:3d}/{total_files}] {material_name:40s} ", end="")
            
            try:
                result = self.fix_file(file_path, dry_run=dry_run)
                if result["fixed"]:
                    self.fixed_count += 1
                    print("✅ Fixed")
                else:
                    print("✓ Already clean")
                self.processed_count += 1
                
            except Exception as e:
                self.error_count += 1
                error_msg = f"{material_name}: {str(e)}"
                self.errors.append(error_msg)
                print(f"❌ Error: {e}")
        
        # Print summary
        print("\n" + "="*70)
        self.print_summary(dry_run)
        
        return {
            "success": True,
            "total": total_files,
            "processed": self.processed_count,
            "fixed": self.fixed_count,
            "errors": self.error_count,
            "error_details": self.errors
        }
    
    def fix_file(self, file_path: Path, dry_run: bool = False) -> Dict[str, Any]:
        """Fix formatting in a single frontmatter file"""
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Check if file has formatting issues
        has_issues = self.detect_formatting_issues(original_content)
        
        if not has_issues:
            return {"fixed": False, "reason": "No formatting issues detected"}
        
        try:
            # Parse YAML (this will strip all the !! tags and quotes)
            data = yaml.safe_load(original_content)
            
            if not data:
                return {"fixed": False, "reason": "No data loaded"}
            
            # Generate clean YAML
            clean_yaml = yaml.dump(
                data,
                Dumper=self.dumper,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
                width=120,  # Reasonable line width
                indent=2
            )
            
            # Post-process to ensure perfect formatting
            clean_yaml = self.post_process_yaml(clean_yaml)
            
            # Write back if not dry run
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(clean_yaml)
            
            return {"fixed": True, "reason": "Formatting normalized"}
            
        except yaml.YAMLError as e:
            raise ValueError(f"YAML parsing error: {e}")
        except Exception as e:
            raise ValueError(f"Unexpected error: {e}")
    
    def detect_formatting_issues(self, content: str) -> bool:
        """Detect if content has formatting issues that need fixing"""
        issues = [
            '!!float' in content,
            '!!int' in content,
            '!!null' in content,
            '!!bool' in content,
            '": "' in content,  # Quoted keys and values
            '"value":' in content,  # Quoted property names
            '"name":' in content,
            '"unit":' in content,
        ]
        return any(issues)
    
    def post_process_yaml(self, yaml_content: str) -> str:
        """Post-process YAML to ensure perfect formatting"""
        lines = yaml_content.split('\n')
        processed_lines = []
        
        for line in lines:
            # Ensure null values are unquoted
            line = line.replace("'null'", "null")
            line = line.replace('"null"', "null")
            
            # Fix percentage formatting
            if 'unit:' in line and "'%'" not in line and '"%"' in line:
                line = line.replace('"%"', "'%'")
            
            processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def print_summary(self, dry_run: bool = False):
        """Print processing summary"""
        print("🎉 YAML Formatting Fix Complete!")
        print(f"📊 Statistics:")
        print(f"   Total files processed: {self.processed_count}")
        print(f"   Files fixed: {self.fixed_count}")
        print(f"   Already clean: {self.processed_count - self.fixed_count}")
        print(f"   Errors: {self.error_count}")
        
        if dry_run:
            print("\n⚠️  DRY RUN - No files were modified")
        
        if self.errors:
            print(f"\n❌ Errors encountered:")
            for error in self.errors:
                print(f"   • {error}")


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fix YAML formatting issues in frontmatter files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview changes without modifying files
  python3 scripts/tools/fix_frontmatter_yaml_formatting.py --dry-run
  
  # Fix all frontmatter files
  python3 scripts/tools/fix_frontmatter_yaml_formatting.py
  
  # Fix a specific directory
  python3 scripts/tools/fix_frontmatter_yaml_formatting.py --dir content/components/frontmatter
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    
    parser.add_argument(
        '--dir',
        type=str,
        default='content/components/frontmatter',
        help='Directory containing frontmatter files (default: content/components/frontmatter)'
    )
    
    args = parser.parse_args()
    
    # Create fixer and run
    fixer = FrontmatterYAMLFixer()
    
    try:
        result = fixer.fix_all_frontmatter(
            frontmatter_dir=args.dir,
            dry_run=args.dry_run
        )
        
        if result["success"]:
            sys.exit(0)
        else:
            print(f"\n❌ Processing failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
