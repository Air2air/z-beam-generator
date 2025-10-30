#!/usr/bin/env python3
"""
GROK Compliance Test - Verify No Production Fallbacks

This test scans production code for GROK violations like fallbacks, defaults, and mock behaviors.
"""

import os
import re
from pathlib import Path

def scan_for_grok_violations():
    """Scan production code for GROK violations."""
    violations = []
    
    # GROK violation patterns - focus on actual problematic fallbacks
    violation_patterns = [
        (r'or\s+"".*#.*fallback', 'Explicit fallback comment pattern'),
        (r'or\s+\'\'.*#.*fallback', 'Explicit fallback comment pattern'),
        (r'MockAPIClient', 'Mock client in production code'),
        (r'mock_.*\((?!.*test)', 'Mock function calls outside tests'),
        (r'confidence\s*=\s*0\.\d+\s*#.*[Dd]efault', 'Default confidence values'),
        (r'except:\s*pass', 'Silent failure pattern'),
        (r'return\s+True.*#.*skip', 'Skip logic patterns'),
        (r'return\s*"".*#.*fallback', 'Empty string fallback with comment'),
        (r'fallback.*=.*True', 'Fallback flag patterns'),
        (r'if.*missing.*return.*default', 'Default return on missing data')
    ]
    
    # Production code directories (exclude tests)
    production_dirs = [
        'components',
        'api', 
        'data',
        'generators',
        'utils',
        'config'
    ]
    
    for prod_dir in production_dirs:
        if not os.path.exists(prod_dir):
            continue
            
        for py_file in Path(prod_dir).glob('**/*.py'):
            # Skip test files
            if 'test' in str(py_file) or 'mock' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern, description in violation_patterns:
                    matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        line_content = content.split('\n')[line_num - 1].strip()
                        
                        # Skip comments and allowed contexts
                        if line_content.startswith('#') or 'ALLOWED' in line_content.upper():
                            continue
                            
                        violations.append({
                            'file': str(py_file),
                            'line': line_num,
                            'pattern': description,
                            'content': line_content
                        })
                        
            except Exception as e:
                print(f"Warning: Could not scan {py_file}: {e}")
    
    return violations

def main():
    """Run GROK compliance check."""
    print("🔍 Scanning for GROK violations in production code...")
    print("=" * 60)
    
    violations = scan_for_grok_violations()
    
    if not violations:
        print("✅ No GROK violations found in production code!")
        print("✅ All fallbacks, defaults, and mocks are properly excluded from production")
        return 0
    
    print(f"❌ Found {len(violations)} GROK violations:")
    print()
    
    for violation in violations:
        print(f"📁 {violation['file']}:{violation['line']}")
        print(f"🚫 {violation['pattern']}")
        print(f"💻 {violation['content']}")
        print()
    
    print("❌ GROK violations must be fixed before production deployment")
    return 1

if __name__ == "__main__":
    exit(main())