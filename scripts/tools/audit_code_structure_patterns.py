#!/usr/bin/env python3
"""
Audit all Python code for material property access patterns.

Identifies code that may still expect nested 'properties' structure.
"""

import re
from pathlib import Path
from collections import defaultdict

def audit_file(filepath):
    """Find all material property access patterns in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return []
    
    findings = []
    lines = content.split('\n')
    
    # Patterns to check
    patterns = [
        # Direct 'properties' key access
        (r"\.get\(['\"]properties['\"]", "WRONG: .get('properties') - expects nested wrapper"),
        (r"\[['\"]properties['\"]\]", "WRONG: ['properties'] - expects nested wrapper"),
        
        # Category access patterns
        (r"material_characteristics\.get\(['\"]properties", "WRONG: MC.get('properties')"),
        (r"laser_material_interaction\.get\(['\"]properties", "WRONG: LMI.get('properties')"),
        
        # Correct flat access (for comparison)
        (r"material_characteristics\.get\(['\"](?!properties|label|description|percentage)", "OK: Direct property access in MC"),
        (r"laser_material_interaction\.get\(['\"](?!properties|label|description|percentage)", "OK: Direct property access in LMI"),
        
        # Metadata keys (should be allowed)
        (r"\.get\(['\"]label['\"]", "OK: Metadata key 'label'"),
        (r"\.get\(['\"]description['\"]", "OK: Metadata key 'description'"),
        (r"\.get\(['\"]percentage['\"]", "WARN: 'percentage' being removed"),
    ]
    
    for i, line in enumerate(lines, 1):
        for pattern, description in patterns:
            if re.search(pattern, line):
                findings.append({
                    'line': i,
                    'code': line.strip(),
                    'pattern': description,
                    'severity': 'WRONG' if 'WRONG' in description else ('WARN' if 'WARN' in description else 'OK')
                })
    
    return findings

def main():
    root = Path(".")
    
    # Files to check
    python_files = [
        *root.glob("shared/**/*.py"),
        *root.glob("materials/**/*.py"),
        *root.glob("components/**/*.py"),
        *root.glob("scripts/**/*.py"),
        *root.glob("tests/**/*.py"),
    ]
    
    # Exclude migrations and backups
    python_files = [f for f in python_files if 'migration' not in str(f) and 'backup' not in str(f) and '__pycache__' not in str(f)]
    
    print("=" * 80)
    print("CODE STRUCTURE PATTERN AUDIT")
    print("=" * 80)
    print(f"Checking {len(python_files)} Python files...")
    print()
    
    issues_by_file = defaultdict(list)
    total_wrong = 0
    total_warn = 0
    
    for filepath in sorted(python_files):
        findings = audit_file(filepath)
        
        for finding in findings:
            if finding['severity'] == 'WRONG':
                issues_by_file[filepath].append(finding)
                total_wrong += 1
            elif finding['severity'] == 'WARN':
                issues_by_file[filepath].append(finding)
                total_warn += 1
    
    if issues_by_file:
        print("🔍 FILES WITH ISSUES:")
        print("-" * 80)
        print()
        
        for filepath, findings in sorted(issues_by_file.items()):
            wrong_count = sum(1 for f in findings if f['severity'] == 'WRONG')
            warn_count = sum(1 for f in findings if f['severity'] == 'WARN')
            
            if wrong_count > 0:
                print(f"❌ {filepath.relative_to('.')} - {wrong_count} WRONG patterns")
            elif warn_count > 0:
                print(f"⚠️  {filepath.relative_to('.')} - {warn_count} WARN patterns")
            
            for finding in findings:
                if finding['severity'] in ['WRONG', 'WARN']:
                    print(f"   Line {finding['line']}: {finding['pattern']}")
                    print(f"   Code: {finding['code'][:80]}")
                    print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Files checked: {len(python_files)}")
    print(f"Files with WRONG patterns: {len([f for f in issues_by_file if any(x['severity'] == 'WRONG' for x in issues_by_file[f])])}")
    print(f"Total WRONG patterns: {total_wrong}")
    print(f"Total WARN patterns: {total_warn}")
    print()
    
    if total_wrong == 0:
        print("✅ NO WRONG PATTERNS FOUND - All code uses flat structure!")
    else:
        print(f"❌ {total_wrong} code locations need updating to flat structure")
    
    return total_wrong == 0

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
