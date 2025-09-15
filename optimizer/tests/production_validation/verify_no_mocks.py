#!/usr/bin/env python3
"""
Production Code Validation Script

Enforces GROK_INSTRUCTIONS.md zero tolerance policy for mocks/fallbacks in production code.
This script ensures that production code maintains fail-fast behavior without silent failures.

Usage:
    python3 optimizer/tests/production_validation/verify_no_mocks.py
    
Exit Codes:
    0: No violations found - production code is clean
    1: Violations found - production code contains forbidden patterns
"""

import ast
import os
import re
from pathlib import Path
from typing import List, Tuple

# Forbidden patterns that indicate mocks or fallbacks in production code
FORBIDDEN_PATTERNS = [
    # Mock imports and usage
    r'MockAPIClient',
    r'mock\.Mock',
    r'unittest\.mock',
    r'from.*mock import',
    
    # Fallback patterns
    r'or\s+"default"',
    r'or\s+""',
    r'or\s+\{\}',
    r'or\s+\[\]',
    
    # Silent failure patterns
    r'except:\s*pass',
    r'except\s+\w+:\s*pass',
    
    # Skip/bypass patterns
    r'return True\s*#.*[Ss]kip',
    r'return\s+\{\}\s*#.*fallback',
    r'return\s+".*"\s*#.*default',
    
    # Placeholder patterns
    r'# TODO.*mock',
    r'# FIXME.*fallback',
    r'NotImplemented.*mock',
]

# Allowed production patterns (legitimate code that might trigger false positives)
ALLOWED_PATTERNS = [
    # ComponentResult integration (legitimate production code)
    r'ComponentResult',
    r'\.success',
    r'\.content', 
    r'\.error_message',
    
    # Learning database operations (legitimate production code)
    r'learning_db\.get_smart_config',
    r'enhancement_flags',
    r'record_optimization_attempt',
    r'LearningDatabase',
    
    # Fail-fast validation (legitimate production code)
    r'fail_fast_generator',
    r'create_fail_fast_generator',
]

# Production code paths to validate
PRODUCTION_PATHS = [
    'optimizer/content_optimization/',
    'optimizer/ai_detection/',
    'optimizer/text_optimization/',
    'optimizer/services/',
    'components/text/',  # Text component is critical production code
    'generators/',       # Core generation logic
    'api/',             # API client code
]

# Files to exclude from validation (test files, documentation, etc.)
EXCLUDED_PATTERNS = [
    r'test_.*\.py$',
    r'.*_test\.py$',
    r'tests/.*\.py$',
    r'docs/.*',
    r'README\.md$',
    r'__pycache__',
    r'\.pyc$',
]

class ProductionCodeValidator:
    """Validates that production code contains no mocks or fallbacks."""
    
    def __init__(self):
        self.violations: List[Tuple[str, str, int]] = []
        self.checked_files = 0
        
    def is_excluded_file(self, file_path: str) -> bool:
        """Check if file should be excluded from validation."""
        for pattern in EXCLUDED_PATTERNS:
            if re.search(pattern, file_path):
                return True
        return False
    
    def check_file_content(self, file_path: Path) -> List[Tuple[str, int]]:
        """Check file content for forbidden patterns."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                for pattern in FORBIDDEN_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Check if this matches an allowed pattern
                        is_allowed = False
                        for allowed_pattern in ALLOWED_PATTERNS:
                            if re.search(allowed_pattern, line, re.IGNORECASE):
                                is_allowed = True
                                break
                        
                        if not is_allowed:
                            violations.append((pattern, line_num))
                        
        except UnicodeDecodeError:
            # Skip binary files
            pass
        except Exception as e:
            violations.append((f"Error reading file: {e}", 0))
            
        return violations
    
    def check_ast_patterns(self, file_path: Path) -> List[Tuple[str, int]]:
        """Check Python AST for mock patterns."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse AST to detect mock usage
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Check for mock imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if 'mock' in alias.name.lower():
                            violations.append(
                                (f"Mock import: {alias.name}", getattr(node, 'lineno', 0))
                            )
                
                # Check for mock usage in function calls
                if isinstance(node, ast.Call) and hasattr(node.func, 'attr'):
                    if 'mock' in node.func.attr.lower():
                        violations.append(
                            (f"Mock usage: {node.func.attr}", getattr(node, 'lineno', 0))
                        )
                        
        except SyntaxError:
            # File might not be valid Python, skip AST check
            pass
        except Exception as e:
            violations.append((f"AST parsing error: {e}", 0))
            
        return violations
    
    def validate_file(self, file_path: Path) -> None:
        """Validate a single file for production code compliance."""
        if self.is_excluded_file(str(file_path)):
            return
            
        self.checked_files += 1
        
        # Check content patterns
        content_violations = self.check_file_content(file_path)
        
        # Check AST patterns for Python files
        if file_path.suffix == '.py':
            ast_violations = self.check_ast_patterns(file_path)
            content_violations.extend(ast_violations)
        
        # Record violations
        for pattern, line_num in content_violations:
            self.violations.append((str(file_path), pattern, line_num))
    
    def validate_directory(self, dir_path: str) -> None:
        """Validate all files in a directory recursively."""
        if not os.path.exists(dir_path):
            print(f"⚠️  Directory not found: {dir_path}")
            return
            
        for file_path in Path(dir_path).rglob("*"):
            if file_path.is_file():
                self.validate_file(file_path)
    
    def run_validation(self) -> bool:
        """Run complete validation on all production paths."""
        print("🔍 Starting production code validation...")
        print("Checking for mocks, fallbacks, and silent failures...")
        print()
        
        for prod_path in PRODUCTION_PATHS:
            print(f"Checking: {prod_path}")
            self.validate_directory(prod_path)
        
        print(f"\n📊 Validation Summary:")
        print(f"Files checked: {self.checked_files}")
        print(f"Violations found: {len(self.violations)}")
        
        if self.violations:
            print(f"\n🚫 PRODUCTION CODE VALIDATION FAILED")
            print("Found mocks/fallbacks in production code:")
            print()
            
            for file_path, pattern, line_num in self.violations:
                if line_num > 0:
                    print(f"❌ {file_path}:{line_num}")
                    print(f"   Pattern: {pattern}")
                else:
                    print(f"❌ {file_path}")
                    print(f"   Issue: {pattern}")
                print()
            
            print("🔧 Required Actions:")
            print("1. Remove all mock usage from production code")
            print("2. Replace fallback patterns with proper error handling")
            print("3. Ensure fail-fast behavior on configuration errors")
            print("4. Move any mocks to test files only")
            
            return False
        else:
            print(f"\n✅ PRODUCTION CODE VALIDATION PASSED")
            print("No mocks or fallbacks found in production code")
            print("System maintains proper fail-fast behavior")
            
            return True

def main():
    """Main validation function."""
    validator = ProductionCodeValidator()
    
    print("="*60)
    print("Z-Beam Production Code Validation")
    print("Enforcing GROK_INSTRUCTIONS.md compliance")
    print("="*60)
    
    success = validator.run_validation()
    
    print("="*60)
    
    if success:
        print("🎉 All production code compliance checks passed!")
        return 0
    else:
        print("💥 Production code compliance violations detected!")
        print("Fix violations before proceeding with deployment.")
        return 1

if __name__ == "__main__":
    exit(main())
