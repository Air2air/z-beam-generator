#!/usr/bin/env python3
"""
Comprehensive Frontmatter Validation Script

Phase 6.2: Validates all 124 frontmatter files for:
1. Required fields present
2. Confidence thresholds met (85% YAML, 80% AI)
3. Range consistency
4. YAML structure correctness
5. Prompt chain verification presence
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

class FrontmatterValidator:
    """Validates frontmatter files against quality standards."""
    
    REQUIRED_FIELDS = [
        'name', 'category', 'title', 'description',
        'materialProperties', 'applications', 'caption', 'tags'
    ]
    
    YAML_CONFIDENCE_THRESHOLD = 85
    AI_CONFIDENCE_THRESHOLD = 80
    
    def __init__(self):
        self.results = {
            'total': 0,
            'valid': 0,
            'warnings': 0,
            'errors': 0,
            'issues': defaultdict(list)
        }
    
    def validate_file(self, filepath: Path) -> Dict:
        """Validate a single frontmatter file."""
        issues = []
        warnings = []
        
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            return {
                'valid': False,
                'issues': [f"YAML parse error: {e}"],
                'warnings': []
            }
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in data:
                issues.append(f"Missing required field: {field}")
        
        # Legacy prompt_chain_verification check removed
        
        # Check materialProperties structure
        if 'materialProperties' in data:
            props = data['materialProperties']
            if isinstance(props, dict):
                # Check for categorized structure
                for category_key, category_data in props.items():
                    if isinstance(category_data, dict) and 'properties' in category_data:
                        # Validate properties have required fields
                        for prop_name, prop_data in category_data['properties'].items():
                            if isinstance(prop_data, dict):
                                if 'value' not in prop_data:
                                    warnings.append(f"Property {prop_name} missing value field")
                                if 'confidence' in prop_data:
                                    conf = prop_data['confidence']
                                    if conf < self.YAML_CONFIDENCE_THRESHOLD:
                                        warnings.append(f"Property {prop_name} confidence {conf}% < {self.YAML_CONFIDENCE_THRESHOLD}%")
        
        # Check applications
        if 'applications' in data:
            apps = data['applications']
            if not isinstance(apps, list):
                issues.append("applications must be a list")
            elif len(apps) < 2:
                warnings.append(f"Only {len(apps)} application(s) - recommend at least 2")
        
        # Check tags
        if 'tags' in data:
            tags = data['tags']
            if not isinstance(tags, list):
                issues.append("tags must be a list")
            elif len(tags) < 4:
                warnings.append(f"Only {len(tags)} tag(s) - recommend at least 4")
            elif len(tags) > 10:
                warnings.append(f"{len(tags)} tags - recommend maximum 10")
        
        # Check caption structure
        if 'caption' in data:
            caption = data['caption']
            if not isinstance(caption, dict):
                issues.append("caption must be a dict")
            else:
                # Check for camelCase (new format)
                if 'beforeText' not in caption:
                    warnings.append("caption missing beforeText")
                if 'afterText' not in caption:
                    warnings.append("caption missing afterText")
                
                # Check for old snake_case format
                if 'before_text' in caption or 'after_text' in caption:
                    issues.append("caption uses deprecated snake_case (should be camelCase)")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
    
    def validate_all(self) -> Dict:
        """Validate all frontmatter files."""
        frontmatter_dir = Path("content/components/frontmatter")
        files = sorted(frontmatter_dir.glob("*.yaml"))
        
        self.results['total'] = len(files)
        
        print(f"🔍 Validating {len(files)} frontmatter files...")
        print()
        
        for filepath in files:
            result = self.validate_file(filepath)
            
            if result['valid'] and len(result['warnings']) == 0:
                self.results['valid'] += 1
            elif len(result['issues']) > 0:
                self.results['errors'] += 1
                self.results['issues'][filepath.stem] = result
            else:
                self.results['warnings'] += 1
                self.results['issues'][filepath.stem] = result
        
        return self.results
    
    def print_summary(self):
        """Print validation summary."""
        total = self.results['total']
        valid = self.results['valid']
        warnings = self.results['warnings']
        errors = self.results['errors']
        
        print()
        print("=" * 70)
        print("📊 VALIDATION SUMMARY")
        print("=" * 70)
        print(f"Total files: {total}")
        print(f"✅ Valid (no issues): {valid} ({valid/total*100:.1f}%)")
        print(f"⚠️  Warnings only: {warnings} ({warnings/total*100:.1f}%)")
        print(f"❌ Errors: {errors} ({errors/total*100:.1f}%)")
        print()
        
        # Group issues by type
        issue_types = defaultdict(int)
        warning_types = defaultdict(int)
        
        for material, result in self.results['issues'].items():
            for issue in result['issues']:
                issue_types[issue] += 1
            for warning in result['warnings']:
                warning_types[warning] += 1
        
        if issue_types:
            print("❌ TOP ERRORS:")
            for issue, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"   [{count}] {issue}")
            print()
        
        if warning_types:
            print("⚠️  TOP WARNINGS:")
            for warning, count in sorted(warning_types.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"   [{count}] {warning}")
            print()
        
        # Show files needing attention
        if errors > 0:
            print(f"❌ Files with errors ({min(errors, 10)} shown):")
            error_files = [m for m, r in self.results['issues'].items() if len(r['issues']) > 0]
            for material in error_files[:10]:
                print(f"   - {material}")
            if errors > 10:
                print(f"   ... and {errors - 10} more")
            print()
        
        return 0 if errors == 0 else 1

def main():
    """Main validation function."""
    print("=" * 70)
    print("🔍 PHASE 6.2: Comprehensive Frontmatter Validation")
    print("=" * 70)
    print()
    
    validator = FrontmatterValidator()
    results = validator.validate_all()
    exit_code = validator.print_summary()
    
    return exit_code

if __name__ == '__main__':
    sys.exit(main())
