#!/usr/bin/env python3
"""
Centralized compliance rules for PROJECT_GUIDE.md validation
"""

from pathlib import Path
from typing import List, Dict, Any
import re

class ValidationRules:
    """Centralized rules for PROJECT_GUIDE compliance checking"""
    
    # Expected file structure per PROJECT_GUIDE
    EXPECTED_FILES = [
        "run.py",
        "main.py", 
        "config/global_config.py",
        "modules/content_generator.py",
        "modules/api_client.py",
        "modules/ai_detector.py",
        "compliance/audit_violations.py",
        "compliance/show_config.py",
        "compliance/validation_rules.py",
        "tests/simple_test.py",
        "tests/comprehensive_test.py"
    ]
    
    # Forbidden concepts per PROJECT_GUIDE
    FORBIDDEN_CONCEPTS = [
        "extensible",
        "scalable", 
        "future-proof",
        "just in case",
        "better architecture",
        "base classes",
        "interfaces",
        "design patterns"
    ]
    
    # Required GlobalConfigManager methods
    REQUIRED_CONFIG_METHODS = [
        "get_generation_provider",
        "get_content_temperature",
        "get_optimization_temperature",
        "get_output_directory",
        "get_prompts_directory"
    ]
    
    # Allowed constants in code
    ALLOWED_CONSTANTS = [
        "FILE_EXTENSION",
        "DEFAULT_ENCODING", 
        "HTTP_SUCCESS",
        "CHUNK_SIZE"
    ]
    
    @staticmethod
    def check_file_structure() -> List[str]:
        """Check if file structure matches PROJECT_GUIDE"""
        violations = []
        
        # Check for expected files
        for file_path in ValidationRules.EXPECTED_FILES:
            if not Path(file_path).exists():
                violations.append(f"MISSING: {file_path}")
        
        # Check modules/ directory for unexpected files
        modules_dir = Path("modules")
        if modules_dir.exists():
            expected_module_files = {
                "content_generator.py",
                "api_client.py", 
                "ai_detector.py",
                "__init__.py"  # Allow __init__.py
            }
            
            for item in modules_dir.iterdir():
                if item.is_file() and item.name not in expected_module_files:
                    violations.append(f"UNEXPECTED FILE: {item}")
        
        return violations
    
    @staticmethod
    def check_forbidden_concepts() -> List[str]:
        """Check for forbidden concepts in code and docs"""
        violations = []
        
        # Check Python files
        for py_file in Path(".").rglob("*.py"):
            if "compliance/" in str(py_file):
                continue  # Skip compliance files
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    for concept in ValidationRules.FORBIDDEN_CONCEPTS:
                        if concept in content:
                            violations.append(f"FORBIDDEN CONCEPT '{concept}' in {py_file}")
            except Exception:
                continue
        
        # Check documentation files
        for doc_file in Path(".").rglob("*.md"):
            if str(doc_file).endswith("PROJECT_GUIDE.md"):
                continue  # Skip PROJECT_GUIDE itself
                
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    for concept in ValidationRules.FORBIDDEN_CONCEPTS:
                        if concept in content:
                            violations.append(f"FORBIDDEN CONCEPT '{concept}' in {doc_file}")
            except Exception:
                continue
        
        return violations
    
    @staticmethod
    def check_global_config_usage() -> List[str]:
        """Check if GlobalConfigManager is properly used"""
        violations = []
        
        # Check if GlobalConfigManager exists
        global_config_path = Path("config/global_config.py")
        if not global_config_path.exists():
            violations.append("MISSING: GlobalConfigManager (config/global_config.py)")
            return violations
        
        # Check run.py for direct config usage
        run_py_path = Path("run.py")
        if run_py_path.exists():
            try:
                with open(run_py_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "config = {" in content:
                        violations.append("DIRECT CONFIG DICT in run.py (use GlobalConfigManager)")
                    if "\"generation_provider\":" in content:
                        violations.append("HARDCODED CONFIG in run.py (use GlobalConfigManager)")
            except Exception:
                pass
        
        # Check if GlobalConfigManager has required methods
        try:
            with open(global_config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for method in ValidationRules.REQUIRED_CONFIG_METHODS:
                    if f"def {method}" not in content:
                        violations.append(f"MISSING CONFIG METHOD: {method}")
        except Exception:
            violations.append("ERROR: Cannot read GlobalConfigManager")
        
        return violations
    
    @staticmethod
    def check_simplicity_violations() -> List[str]:
        """Check for violations of simplicity commandments"""
        violations = []
        
        # Check for abstraction layers
        abstraction_patterns = [
            "class.*manager",
            "class.*factory", 
            "class.*builder",
            "class.*handler",
            "class.*processor"
        ]
        
        for py_file in Path(".").rglob("*.py"):
            if "compliance/" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in abstraction_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            violations.append(f"ABSTRACTION LAYER: {pattern} in {py_file}")
            except Exception:
                continue
        
        return violations
    
    @staticmethod
    def get_compliance_score() -> Dict[str, Any]:
        """Calculate overall compliance score"""
        all_violations = []
        
        # Run all checks
        all_violations.extend(ValidationRules.check_file_structure())
        all_violations.extend(ValidationRules.check_forbidden_concepts())
        all_violations.extend(ValidationRules.check_global_config_usage())
        all_violations.extend(ValidationRules.check_simplicity_violations())
        
        total_checks = len(ValidationRules.EXPECTED_FILES) + len(ValidationRules.FORBIDDEN_CONCEPTS) + len(ValidationRules.REQUIRED_CONFIG_METHODS)
        violation_count = len(all_violations)
        
        compliance_percentage = max(0, (total_checks - violation_count) / total_checks * 100)
        
        return {
            "violations": all_violations,
            "violation_count": violation_count,
            "compliance_percentage": compliance_percentage,
            "status": "COMPLIANT" if violation_count == 0 else "VIOLATIONS FOUND"
        }
    
    # Check if hardcoded value is in a legitimate constant definition
    @staticmethod
    def is_legitimate_constant(line: str, pattern: str) -> bool:
        """Check if pattern match is part of a legitimate constant"""
        constant_indicators = [
            r'[A-Z_]+\s*=',  # UPPERCASE_CONSTANT = 
            r'FILE_EXTENSION\s*=',
            r'DEFAULT_ENCODING\s*='
        ]
        
        for indicator in constant_indicators:
            if re.search(indicator, line):
                return True
        return False
    
    @staticmethod
    def check_hardcoded_values() -> List[str]:
        """Check for hardcoded values that should be constants"""
        violations = []
        
        # Patterns for common hardcoded values
        hardcoded_patterns = [
            r'(?<!FILE_EXTENSION\s=\s)["\']\.mdx["\']',  # Exclude FILE_EXTENSION constant
            r'(?<!DEFAULT_ENCODING\s=\s)["\']utf-8["\']' # Exclude DEFAULT_ENCODING constant
        ]
        
        for py_file in Path(".").rglob("*.py"):
            if "compliance/" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in hardcoded_patterns:
                        if re.search(pattern, content):
                            violations.append(f"HARDCODED VALUE: {pattern} in {py_file}")
            except Exception:
                continue
        
        return violations