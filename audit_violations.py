#!/usr/bin/env python3
"""
Comprehensive violation detection and enforcement for Z-Beam simplicity standards.
Enforces all rules from DEVELOPMENT.md and reports actionable violations.
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple


class SimplicityAuditor:
    """Detects and reports violations of simplicity standards."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.violations = []
        
    def audit_all(self) -> Dict[str, List[str]]:
        """Run all audits and return categorized violations."""
        violations = {
            'file_count': self.audit_file_count(),
            'file_size': self.audit_file_size(),
            'imports': self.audit_imports(),
            'function_length': self.audit_function_length(),
            'hardcoding': self.audit_hardcoding(),
            'abstractions': self.audit_abstractions(),
            'merge_opportunities': self.audit_merge_opportunities()
        }
        return violations
    
    def get_python_files(self) -> List[Path]:
        """Get all project Python files, excluding venv and cache."""
        files = []
        for file in self.project_root.rglob("*.py"):
            if ('.venv' not in str(file) and 
                '__pycache__' not in str(file)):
                files.append(file)
        return files
    
    def audit_file_count(self) -> List[str]:
        """Check if we exceed ≤10 Python files target."""
        files = self.get_python_files()
        violations = []
        
        if len(files) > 10:
            violations.append(f"❌ File count: {len(files)}/10 files (VIOLATION)")
            violations.append("   ACTION: Merge small modules into larger ones")
            
            # Suggest specific merges
            small_files = []
            for file in files:
                lines = len(file.read_text().splitlines())
                if lines < 100 and 'modules/' in str(file):
                    small_files.append(f"{file.name} ({lines} lines)")
            
            if small_files:
                violations.append(f"   MERGE CANDIDATES: {', '.join(small_files)}")
        else:
            violations.append(f"✅ File count: {len(files)}/10 files")
            
        return violations
    
    def audit_file_size(self) -> List[str]:
        """Check if files have obvious bloat (removed arbitrary limits)."""
        violations = []
        
        # Only flag truly problematic files, not arbitrary line counts
        extremely_large_files = []
        
        for file in self.get_python_files():
            lines = len(file.read_text().splitlines())
            # Only flag files over 1000 lines as truly problematic
            if lines > 1000:
                extremely_large_files.append((file, lines))
        
        if extremely_large_files:
            violations.append(f"⚠️  Extremely large files found (>1000 lines):")
            for file, lines in extremely_large_files:
                violations.append(f"   {file.relative_to(self.project_root)}: {lines} lines")
                violations.append(f"   CONSIDER: Breaking into logical modules if natural")
        else:
            violations.append("✅ No extremely large files detected")
            
        return violations
    
    def audit_imports(self) -> List[str]:
        """Check for unjustified imports (replaced ≤5 import rule)."""
        violations = []
        problematic_imports = []
        
        for file in self.get_python_files():
            content = file.read_text()
            
            # Look for obviously unused imports
            import_lines = re.findall(r'^(from .+? import .+?|import .+?)$', content, re.MULTILINE)
            
            # Simple heuristic: if import count is very high (>10), flag for review
            if len(import_lines) > 10:
                problematic_imports.append((file, len(import_lines)))
        
        if problematic_imports:
            violations.append(f"⚠️  Files with many imports (review for unused):")
            for file, count in problematic_imports:
                violations.append(f"   {file.relative_to(self.project_root)}: {count} imports")
                violations.append(f"   ACTION: Review each import for necessity")
        else:
            violations.append("✅ Import counts reasonable (no arbitrary limits)")
            
        return violations
    
    def audit_function_length(self) -> List[str]:
        """Check for extremely long functions (removed arbitrary 20-line limit)."""
        violations = []
        long_functions = []
        
        for file in self.get_python_files():
            content = file.read_text()
            functions = self._extract_functions(content)
            
            for func_name, func_lines in functions:
                # Only flag truly excessive functions (>100 lines)
                if func_lines > 100:
                    long_functions.append((file, func_name, func_lines))
        
        if long_functions:
            violations.append("⚠️  Extremely long functions found (>100 lines):")
            for file, func_name, lines in long_functions[:10]:  # Show top 10
                violations.append(f"   {file.relative_to(self.project_root)}::{func_name}: {lines} lines")
            if len(long_functions) > 10:
                violations.append(f"   ... and {len(long_functions) - 10} more")
            violations.append("   CONSIDER: Breaking into logical sub-functions if natural")
        else:
            violations.append("✅ No extremely long functions")
            
        return violations
    
    def audit_hardcoding(self) -> List[str]:
        """Check for hardcoded values that should use GlobalConfigManager."""
        violations = []
        hardcoded_values = []
        
        # Patterns that suggest hardcoding
        hardcode_patterns = [
            (r'temperature\s*=\s*[\d.]+', 'temperature values'),
            (r'max_tokens\s*=\s*\d+', 'token limits'),  
            (r'"https?://[^\s"\']+["\']', 'URLs in strings'),
            (r'url_template["\']?\s*:\s*["\']https?://[^"\']+', 'API URL templates'),
            (r'api_key\s*=\s*["\'][^"\']+["\']', 'API keys'),
            (r'timeout\s*=\s*\d+', 'timeout values'),
            (r'sleep\(\s*\d+', 'sleep durations'),
            (r'retry.*=\s*\d+', 'retry counts'),
            (r'iterations.*=\s*\d+', 'iteration limits'),
        ]
        
        for file in self.get_python_files():
            content = file.read_text()
            for pattern, description in hardcode_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    hardcoded_values.append((file, description, len(matches)))
        
        if hardcoded_values:
            violations.append(f"❌ Potential hardcoded values found:")
            for file, description, count in hardcoded_values:
                violations.append(f"   {file.relative_to(self.project_root)}: {count} {description}")
            violations.append(f"   ACTION: Use GlobalConfigManager for all config values")
        else:
            violations.append("✅ No obvious hardcoded values detected")
            
        return violations
    
    def audit_abstractions(self) -> List[str]:
        """Check for unnecessary abstractions."""
        violations = []
        abstractions = []
        
        # Look for abstraction patterns
        abstraction_patterns = [
            (r'class\s+\w*Base\w*', 'base classes'),
            (r'class\s+\w*Abstract\w*', 'abstract classes'),
            (r'class\s+\w*Interface\w*', 'interface classes'),
            (r'def\s+_[a-z_]+\([^)]*\):', 'private helper methods'),
        ]
        
        for file in self.get_python_files():
            content = file.read_text()
            for pattern, description in abstraction_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    abstractions.append((file, description, len(matches)))
        
        if abstractions:
            violations.append(f"⚠️  Potential abstractions found:")
            for file, description, count in abstractions:
                violations.append(f"   {file.relative_to(self.project_root)}: {count} {description}")
            violations.append(f"   ACTION: Evaluate if these can be inlined or simplified")
        else:
            violations.append("✅ No obvious abstractions detected")
            
        return violations
    
    def audit_merge_opportunities(self) -> List[str]:
        """Identify files that could be merged."""
        violations = []
        merge_candidates = []
        
        files = self.get_python_files()
        module_files = [f for f in files if 'modules/' in str(f)]
        
        # Find small files that could be merged
        small_modules = []
        for file in module_files:
            lines = len(file.read_text().splitlines())
            if lines < 150:
                small_modules.append((file, lines))
        
        if len(small_modules) >= 2:
            violations.append(f"🔄 Merge opportunities found:")
            for file, lines in small_modules:
                violations.append(f"   {file.name}: {lines} lines")
            violations.append(f"   ACTION: Consider merging into content_generator.py or api_client.py")
        else:
            violations.append("✅ No obvious merge opportunities")
            
        return violations
    
    def _extract_functions(self, content: str) -> List[Tuple[str, int]]:
        """Extract function names and line counts."""
        functions = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if re.match(r'^\s*def\s+\w+', line):
                func_name = re.search(r'def\s+(\w+)', line).group(1)
                
                # Count lines until next function or class
                func_lines = 1
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    if (re.match(r'^\s*def\s+\w+', next_line) or 
                        re.match(r'^\s*class\s+\w+', next_line) or
                        (next_line.strip() and not next_line.startswith(' ') and not next_line.startswith('\t'))):
                        break
                    if next_line.strip():  # Count non-empty lines
                        func_lines += 1
                    j += 1
                
                functions.append((func_name, func_lines))
        
        return functions
    
    def print_report(self):
        """Print a comprehensive violation report."""
        print("=" * 80)
        print("🔍 Z-BEAM SIMPLICITY AUDIT REPORT")
        print("=" * 80)
        
        all_violations = self.audit_all()
        
        for category, violations in all_violations.items():
            print(f"\n📋 {category.upper().replace('_', ' ')}")
            print("-" * 40)
            for violation in violations:
                print(violation)
        
        # Summary
        total_violations = sum(1 for violations in all_violations.values() 
                             for v in violations if v.startswith('❌'))
        
        print(f"\n📊 SUMMARY")
        print("-" * 40)
        print(f"Total violations: {total_violations}")
        print(f"Status: {'🚨 NEEDS ATTENTION' if total_violations > 0 else '✅ COMPLIANT'}")
        
        if total_violations > 0:
            print("\n🎯 PRIORITY ACTIONS:")
            print("1. Review and fix actual violations (not arbitrary limits)")
            print("2. Use GlobalConfigManager for user/runtime config")
            print("3. Remove unused imports")
            print("4. Inline helper methods if simpler")


# === CLAUDE COMPLIANCE VALIDATION (merged from validate_claude_compliance.py) ===

class ClaudeComplianceValidator:
    """Validates that Claude followed PROJECT_GUIDE.md rules."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.violations = []
    
    def validate_response(self, claude_response: str) -> bool:
        """Validate Claude's response against PROJECT_GUIDE rules with enhanced detection."""
        violations = []
        
        # Enhanced forbidden phrases with context
        forbidden_patterns = [
            (r"create\s+(?:a\s+)?new\s+file", "creating new files"),
            (r"add\s+(?:a\s+)?(?:configuration|config)\s+file", "adding config files"), 
            (r"make\s+this\s+more\s+flexible", "flexibility suggestions"),
            (r"better\s+architecture", "architecture improvements"),
            (r"could\s+be\s+extended", "extensibility suggestions"),
            (r"might\s+need\s+later", "future-proofing"),
            (r"create\s+documentation", "documentation additions"),
            (r"add\s+(?:a\s+)?readme", "readme additions"),
            (r"separate\s+concerns", "separation of concerns"),
            (r"abstract\s+this", "abstraction suggestions"),
            (r"for\s+future\s+use", "future use planning"),
            (r"base\s+class", "base class patterns"),
            (r"interface", "interface patterns"),
            (r"design\s+pattern", "design patterns"),
            (r"dependency\s+injection", "DI patterns"),
            (r"factory\s+pattern", "factory patterns"),
            (r"singleton", "singleton patterns"),
            (r"more\s+maintainable", "maintainability claims"),
            (r"scalable", "scalability claims"),
            (r"extensible", "extensibility claims"),
        ]
        
        response_lower = claude_response.lower()
        for pattern, description in forbidden_patterns:
            if re.search(pattern, response_lower):
                violations.append(f"❌ FORBIDDEN: {description} detected - '{pattern}'")
        
        # Check for file creation suggestions
        file_creation_patterns = [
            r"create.*\.py",
            r"add.*\.py", 
            r"new.*\.py",
            r"create.*\.md",
            r"add.*\.md",
            r"create.*\.json",
            r"create.*\.yaml",
        ]
        
        for pattern in file_creation_patterns:
            if re.search(pattern, response_lower):
                violations.append(f"❌ FILE CREATION: Suggests creating files - '{pattern}'")
        
        # Check for hardcoding violations
        hardcode_patterns = [
            r"temperature\s*=\s*[\d.]+",
            r"max_tokens\s*=\s*\d+",
            r"timeout\s*=\s*\d+",
        ]
        
        for pattern in hardcode_patterns:
            if re.search(pattern, claude_response):
                violations.append(f"❌ HARDCODING: Direct config values - '{pattern}'")
        
        # Check for missing compliance statement
        has_compliance = re.search(r"CLAUDE\s+COMPLIANCE\s+CHECK:", claude_response, re.IGNORECASE)
        if not has_compliance:
            violations.append("❌ MISSING: Required CLAUDE COMPLIANCE CHECK statement")
        
        # Check for reference to other docs
        doc_references = re.findall(r'\b\w+\.md\b', claude_response)
        invalid_refs = [ref for ref in doc_references if ref.lower() not in ['project_guide.md', 'readme.md']]
        if invalid_refs:
            violations.append(f"❌ INVALID DOCS: Referenced non-existent docs: {invalid_refs}")
        
        # Check for complexity suggestions
        complexity_patterns = [
            r"class.*Base",
            r"class.*Interface", 
            r"class.*Abstract",
            r"inheritance",
            r"polymorphism",
            r"composition",
        ]
        
        for pattern in complexity_patterns:
            if re.search(pattern, claude_response, re.IGNORECASE):
                violations.append(f"❌ COMPLEXITY: Object-oriented complexity - '{pattern}'")
        
        self.violations = violations
        return len(violations) == 0
    
    def validate_project_guide(self) -> bool:
        """Validate PROJECT_GUIDE.md for brevity and contradictions."""
        guide_path = self.project_root / "PROJECT_GUIDE.md"
        if not guide_path.exists():
            self.violations.append("❌ PROJECT_GUIDE.md not found")
            return False
        
        content = guide_path.read_text()
        lines = content.split('\n')
        
        violations = []
        
        # Check line count
        if len(lines) > 400:
            violations.append(f"❌ PROJECT_GUIDE.md too long: {len(lines)} lines (target: <400)")
        
        # Check for contradictions (basic pattern matching)
        contradictions = [
            ("single-pass", "iteration"),
            ("no feedback", "feedback loop"),
            ("fail-fast", "graceful"),
            ("simplest", "flexible"),
        ]
        
        content_lower = content.lower()
        for concept1, concept2 in contradictions:
            if concept1 in content_lower and concept2 in content_lower:
                violations.append(f"⚠️  Potential contradiction: '{concept1}' and '{concept2}' both present")
        
        # Check for redundant sections
        sections = re.findall(r'^#{1,3}\s+(.+)$', content, re.MULTILINE)
        if len(sections) > 15:
            violations.append(f"❌ Too many sections: {len(sections)} (target: <15)")
        
        self.violations.extend(violations)
        return len(violations) == 0
    
    def validate_file_count(self) -> bool:
        """Validate that file count hasn't increased."""
        python_files = list(self.project_root.glob("**/*.py"))
        python_files = [f for f in python_files if '.venv' not in str(f) and '__pycache__' not in str(f)]
        
        if len(python_files) > 14:  # Current count from audit
            self.violations.append(f"❌ File count increased: {len(python_files)} files")
            return False
        
        return True
    
    def validate_documentation_count(self) -> bool:
        """Validate that only PROJECT_GUIDE.md and README.md exist."""
        md_files = list(self.project_root.glob("*.md"))
        md_files = [f.name for f in md_files]
        
        allowed_files = ['PROJECT_GUIDE.md', 'README.md']
        extra_files = [f for f in md_files if f not in allowed_files]
        
        if extra_files:
            self.violations.append(f"❌ Unauthorized documentation files: {extra_files}")
            return False
        
        return True
    
    def run_full_validation(self) -> bool:
        """Run all validation checks."""
        validations = [
            self.validate_project_guide(),
            self.validate_file_count(),
            self.validate_documentation_count()
        ]
        
        return all(validations)
    
    def print_report(self):
        """Print validation report."""
        print("=" * 60)
        print("🔍 CLAUDE COMPLIANCE VALIDATION REPORT")
        print("=" * 60)
        
        if not self.violations:
            print("✅ ALL VALIDATIONS PASSED")
            print("✅ Claude appears to be following PROJECT_GUIDE.md rules")
        else:
            print("🚨 COMPLIANCE VIOLATIONS DETECTED:")
            for violation in self.violations:
                print(f"  {violation}")
            
            print(f"\n📋 CORRECTIVE ACTIONS REQUIRED:")
            print(f"1. Review PROJECT_GUIDE.md rules")
            print(f"2. Fix violations before proceeding")
            print(f"3. Re-run validation")
        
        print(f"\nValidation completed: {len(self.violations)} violations found")


def main():
    auditor = SimplicityAuditor("/Users/todddunning/Desktop/Z-Beam/z-beam-generator")
    auditor.print_report()
    validate_claude_compliance()


def validate_claude_compliance():
    """Run Claude compliance validation."""
    validator = ClaudeComplianceValidator("/Users/todddunning/Desktop/Z-Beam/z-beam-generator")
    validator.run_full_validation()
    validator.print_report()


def validate_claude_realtime(response_text: str):
    """Real-time validation of Claude responses for immediate feedback."""
    print("🔍 REAL-TIME CLAUDE COMPLIANCE CHECK")
    print("=" * 50)
    
    validator = ClaudeComplianceValidator("/Users/todddunning/Desktop/Z-Beam/z-beam-generator")
    is_compliant = validator.validate_response(response_text)
    
    if is_compliant:
        print("✅ CLAUDE RESPONSE COMPLIANT")
        print("✅ All PROJECT_GUIDE.md rules followed")
    else:
        print("🚨 CLAUDE COMPLIANCE VIOLATIONS DETECTED:")
        for violation in validator.violations:
            print(f"  {violation}")
        print("\n❌ RESPONSE REJECTED - Fix violations and try again")
    
    return is_compliant


def monitor_file_changes():
    """Monitor for unauthorized file creation during Claude interactions."""
    import os
    import time
    
    print("🔍 MONITORING FILE SYSTEM FOR VIOLATIONS...")
    
    # Get baseline file count
    baseline_files = set(os.listdir("/Users/todddunning/Desktop/Z-Beam/z-beam-generator"))
    
    time.sleep(1)  # Brief pause
    
    # Check for new files
    current_files = set(os.listdir("/Users/todddunning/Desktop/Z-Beam/z-beam-generator"))
    new_files = current_files - baseline_files
    
    if new_files:
        print(f"🚨 UNAUTHORIZED FILE CREATION DETECTED: {list(new_files)}")
        print("❌ Claude violated 'no new files' rule")
        return False
    else:
        print("✅ No unauthorized file creation detected")
        return True


if __name__ == "__main__":
    main()
