#!/usr/bin/env python3
"""
Comprehensive Frontmatter Verification Script

Validates all 121 frontmatter files against the new standard:
- Simple string applications (format: "Industry: Description")
- CamelCase caption keys (beforeText, afterText, not snake_case)
- Tags array with 4-10 items
- All required fields present

Outputs:
- Summary statistics
- List of non-compliant files
- Detailed validation report (optional)
"""

import yaml
from pathlib import Path
from typing import Dict, List, Tuple
import sys

class FrontmatterVerifier:
    def __init__(self, frontmatter_dir: str = "content/components/frontmatter"):
        self.frontmatter_dir = Path(frontmatter_dir)
        self.results = {
            "total": 0,
            "compliant": 0,
            "non_compliant": 0,
            "missing": 0,
            "issues": []
        }
        
    def verify_file(self, material_name: str) -> Tuple[bool, List[str]]:
        """
        Verify a single frontmatter file.
        
        Returns:
            (is_compliant, list_of_issues)
        """
        filename = f"{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml"
        filepath = self.frontmatter_dir / filename
        
        issues = []
        
        # Check file exists
        if not filepath.exists():
            return False, [f"File does not exist: {filepath}"]
        
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            return False, [f"Failed to parse YAML: {e}"]
        
        # Check required fields
        required_fields = ['name', 'category', 'title', 'description', 
                          'materialProperties', 'applications', 'caption', 'tags']
        for field in required_fields:
            if field not in data:
                issues.append(f"Missing required field: {field}")
        
        # Check applications format (simple strings)
        if 'applications' in data:
            apps = data['applications']
            if not isinstance(apps, list):
                issues.append("applications must be a list")
            elif len(apps) < 2:
                issues.append(f"Insufficient applications: {len(apps)} (need at least 2)")
            else:
                # Check if they're strings (new format) or objects (old format)
                for idx, app in enumerate(apps):
                    if isinstance(app, dict):
                        issues.append(f"Application {idx+1} is dict (old format) - should be simple string")
                        break
                    elif isinstance(app, str):
                        # Applications should be simple industry names (no descriptions)
                        if ':' in app:
                            issues.append(f"Application {idx+1} contains colon (old format) - use industry names only")
                        elif len(app.strip()) < 3:
                            issues.append(f"Application {idx+1} name too short")
        
        # Check caption format (camelCase keys)
        if 'caption' in data:
            caption = data['caption']
            if not isinstance(caption, dict):
                issues.append("caption must be a dict")
            else:
                # Check for snake_case (old format)
                if 'before_text' in caption or 'after_text' in caption:
                    issues.append("Caption uses snake_case (old format) - should be camelCase")
                
                # Check for camelCase (new format)
                if 'beforeText' not in caption:
                    issues.append("Caption missing 'beforeText' field")
                if 'afterText' not in caption:
                    issues.append("Caption missing 'afterText' field")
                
                # Check other required caption fields
                required_caption_fields = ['description', 'alt']
                for field in required_caption_fields:
                    if field not in caption:
                        issues.append(f"Caption missing required field: {field}")
        
        # Check tags
        if 'tags' in data:
            tags = data['tags']
            if not isinstance(tags, list):
                issues.append("tags must be a list")
            elif len(tags) < 4:
                issues.append(f"Insufficient tags: {len(tags)} (need at least 4)")
            elif len(tags) > 10:
                issues.append(f"Too many tags: {len(tags)} (maximum 10)")
            else:
                # Check all tags are strings
                non_strings = [idx for idx, tag in enumerate(tags) if not isinstance(tag, str)]
                if non_strings:
                    issues.append(f"Non-string tags at positions: {non_strings}")
        
        # Check materialProperties
        if 'materialProperties' in data:
            props = data['materialProperties']
            if not isinstance(props, dict):
                issues.append("materialProperties must be a dict")
            elif len(props) < 5:
                issues.append(f"Insufficient materialProperties: {len(props)} (need at least 5)")
        
        is_compliant = len(issues) == 0
        return is_compliant, issues
    
    def verify_all(self, materials: List[str] = None) -> Dict:
        """Verify all materials."""
        if materials is None:
            # Get all materials from materials.yaml
            materials_file = Path("data/materials.yaml")
            with open(materials_file, 'r') as f:
                data = yaml.safe_load(f)
            materials = list(data.get('materials', {}).keys())
            materials.sort()
        
        self.results['total'] = len(materials)
        
        print("🔍 FRONTMATTER VERIFICATION")
        print("="*70)
        print(f"Checking {len(materials)} materials...\n")
        
        compliant_files = []
        non_compliant_files = []
        
        for material in materials:
            is_compliant, issues = self.verify_file(material)
            
            if is_compliant:
                self.results['compliant'] += 1
                compliant_files.append(material)
            else:
                self.results['non_compliant'] += 1
                non_compliant_files.append(material)
                self.results['issues'].append({
                    'material': material,
                    'issues': issues
                })
        
        return {
            'compliant': compliant_files,
            'non_compliant': non_compliant_files
        }
    
    def print_summary(self, show_details: bool = False):
        """Print verification summary."""
        total = self.results['total']
        compliant = self.results['compliant']
        non_compliant = self.results['non_compliant']
        
        print("\n" + "="*70)
        print("📊 VERIFICATION SUMMARY")
        print("="*70)
        print(f"Total materials: {total}")
        print(f"✅ Compliant (new format): {compliant} ({compliant/total*100:.1f}%)")
        print(f"❌ Non-compliant: {non_compliant} ({non_compliant/total*100:.1f}%)")
        print()
        
        if non_compliant > 0:
            print("❌ NON-COMPLIANT FILES:")
            print("-"*70)
            
            # Group issues by type
            issue_types = {}
            for item in self.results['issues']:
                for issue in item['issues']:
                    if issue not in issue_types:
                        issue_types[issue] = []
                    issue_types[issue].append(item['material'])
            
            # Show most common issues first
            sorted_issues = sorted(issue_types.items(), key=lambda x: len(x[1]), reverse=True)
            
            for issue, materials in sorted_issues[:10]:  # Top 10 issues
                count = len(materials)
                print(f"  [{count}] {issue}")
                if show_details:
                    for mat in materials[:5]:
                        print(f"      - {mat}")
                    if len(materials) > 5:
                        print(f"      ... and {len(materials)-5} more")
                print()
            
            if len(sorted_issues) > 10:
                print(f"  ... and {len(sorted_issues)-10} more issue types\n")
        
        if compliant == total:
            print("🎉 ALL FILES COMPLIANT! System ready for deployment.")
            return 0
        else:
            print(f"⚠️  {non_compliant} files need attention.")
            print(f"💡 Run: python3 scripts/tools/batch_regenerate_frontmatter.py --resume")
            return 1
    
    def export_report(self, filename: str = "verification_report.txt"):
        """Export detailed report to file."""
        with open(filename, 'w') as f:
            f.write("FRONTMATTER VERIFICATION REPORT\n")
            f.write(f"Generated: {Path(filename).stat().st_mtime}\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Total: {self.results['total']}\n")
            f.write(f"Compliant: {self.results['compliant']}\n")
            f.write(f"Non-compliant: {self.results['non_compliant']}\n\n")
            
            f.write("NON-COMPLIANT FILES:\n")
            f.write("-"*70 + "\n")
            
            for item in self.results['issues']:
                f.write(f"\n{item['material']}:\n")
                for issue in item['issues']:
                    f.write(f"  - {issue}\n")
        
        print(f"\n📄 Detailed report exported to: {filename}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Verify all frontmatter files meet new standards'
    )
    parser.add_argument(
        '--details',
        action='store_true',
        help='Show detailed issues for each non-compliant file'
    )
    parser.add_argument(
        '--export',
        metavar='FILENAME',
        help='Export detailed report to file'
    )
    parser.add_argument(
        '--materials',
        nargs='+',
        help='Verify specific materials only'
    )
    
    args = parser.parse_args()
    
    verifier = FrontmatterVerifier()
    
    try:
        files = verifier.verify_all(materials=args.materials)
        exit_code = verifier.print_summary(show_details=args.details)
        
        if args.export:
            verifier.export_report(args.export)
        
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()
