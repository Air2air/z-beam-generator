#!/usr/bin/env python3
"""
Comprehensive YAML validation test script for Z-Beam Generator
Tests all generators, examples, and prompt files for valid YAML syntax
"""

import sys
import yaml
import json
from pathlib import Path
from typing import List, Tuple


class YAMLValidationTester:
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.results = {
            'generator_tests': [],
            'example_tests': [],
            'prompt_tests': [],
            'frontmatter_tests': [],
            'total_passed': 0,
            'total_failed': 0,
            'errors': []
        }
    
    def test_yaml_content(self, file_path: Path, content: str = None) -> Tuple[bool, str]:
        """Test if content is valid YAML"""
        try:
            if content is None:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # Extract YAML frontmatter if it exists
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 2:
                    yaml_content = parts[1].strip()
                else:
                    yaml_content = content
            else:
                yaml_content = content
            
            # Try to parse YAML
            yaml.safe_load(yaml_content)
            return True, "Valid YAML"
            
        except yaml.YAMLError as e:
            return False, f"YAML Error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def test_json_content(self, content: str) -> Tuple[bool, str]:
        """Test if content is valid JSON"""
        try:
            json.loads(content)
            return True, "Valid JSON"
        except json.JSONDecodeError as e:
            return False, f"JSON Error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def check_bracket_syntax(self, content: str) -> List[str]:
        """Check for problematic bracket syntax that might cause YAML issues"""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Look for bracket patterns that might be problematic in YAML
            if '[' in line and ']' in line:
                # Check for patterns like [value] that should be "value"
                import re
                bracket_pattern = r'\[[^\]]*[°C|°F|K|MPa|GPa|W|cm|mm|kg|m³|%][^\]]*\]'
                if re.search(bracket_pattern, line):
                    issues.append(f"Line {i}: Potential YAML bracket issue: {line.strip()}")
        
        return issues
    
    def test_generator_files(self):
        """Test all generator.py files"""
        print("🔍 Testing generator files...")
        generator_files = list(self.workspace_root.rglob("*/generator.py"))
        
        for gen_file in generator_files:
            try:
                # Basic syntax check by importing
                spec = self._import_python_file(gen_file)
                if spec:
                    result = {
                        'file': str(gen_file.relative_to(self.workspace_root)),
                        'status': 'PASS',
                        'message': 'Python syntax valid'
                    }
                    self.results['total_passed'] += 1
                else:
                    result = {
                        'file': str(gen_file.relative_to(self.workspace_root)),
                        'status': 'FAIL',
                        'message': 'Python import failed'
                    }
                    self.results['total_failed'] += 1
                    
            except Exception as e:
                result = {
                    'file': str(gen_file.relative_to(self.workspace_root)),
                    'status': 'FAIL',
                    'message': f'Error: {str(e)}'
                }
                self.results['total_failed'] += 1
            
            self.results['generator_tests'].append(result)
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"  {status_icon} {result['file']}: {result['message']}")
    
    def _import_python_file(self, file_path: Path):
        """Safely import a Python file"""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("test_module", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return spec
        except Exception:
            return None
    
    def test_example_files(self):
        """Test all example files in validators/examples/"""
        print("\n🔍 Testing example files...")
        examples_dir = self.workspace_root / "validators" / "examples"
        
        if not examples_dir.exists():
            print("  ⚠️  No examples directory found")
            return
        
        example_files = list(examples_dir.glob("*.md"))
        
        for example_file in example_files:
            try:
                with open(example_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for bracket syntax issues
                bracket_issues = self.check_bracket_syntax(content)
                
                # Test YAML if present
                if content.startswith('---'):
                    is_valid, message = self.test_yaml_content(example_file, content)
                    status = 'PASS' if is_valid and not bracket_issues else 'FAIL'
                    
                    if bracket_issues:
                        message += f" | Bracket issues: {len(bracket_issues)}"
                else:
                    status = 'PASS' if not bracket_issues else 'FAIL'
                    message = "No YAML frontmatter" + (f" | Bracket issues: {len(bracket_issues)}" if bracket_issues else "")
                
                result = {
                    'file': str(example_file.relative_to(self.workspace_root)),
                    'status': status,
                    'message': message,
                    'bracket_issues': bracket_issues
                }
                
                if status == 'PASS':
                    self.results['total_passed'] += 1
                else:
                    self.results['total_failed'] += 1
                    if bracket_issues:
                        self.results['errors'].extend(bracket_issues)
                        
            except Exception as e:
                result = {
                    'file': str(example_file.relative_to(self.workspace_root)),
                    'status': 'FAIL',
                    'message': f'Error: {str(e)}',
                    'bracket_issues': []
                }
                self.results['total_failed'] += 1
            
            self.results['example_tests'].append(result)
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"  {status_icon} {result['file']}: {result['message']}")
    
    def test_prompt_files(self):
        """Test all prompt.yaml files"""
        print("\n🔍 Testing prompt files...")
        prompt_files = list(self.workspace_root.rglob("*/prompt.yaml"))
        
        for prompt_file in prompt_files:
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Test YAML validity
                is_valid, yaml_message = self.test_yaml_content(prompt_file, content)
                
                # Check for bracket syntax issues
                bracket_issues = self.check_bracket_syntax(content)
                
                status = 'PASS' if is_valid and not bracket_issues else 'FAIL'
                message = yaml_message
                
                if bracket_issues:
                    message += f" | Bracket issues: {len(bracket_issues)}"
                
                result = {
                    'file': str(prompt_file.relative_to(self.workspace_root)),
                    'status': status,
                    'message': message,
                    'bracket_issues': bracket_issues
                }
                
                if status == 'PASS':
                    self.results['total_passed'] += 1
                else:
                    self.results['total_failed'] += 1
                    if bracket_issues:
                        self.results['errors'].extend(bracket_issues)
                        
            except Exception as e:
                result = {
                    'file': str(prompt_file.relative_to(self.workspace_root)),
                    'status': 'FAIL',
                    'message': f'Error: {str(e)}',
                    'bracket_issues': []
                }
                self.results['total_failed'] += 1
            
            self.results['prompt_tests'].append(result)
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"  {status_icon} {result['file']}: {result['message']}")
    
    def test_frontmatter_files(self):
        """Test frontmatter files for YAML validity"""
        print("\n🔍 Testing frontmatter files...")
        frontmatter_dir = self.workspace_root / "content" / "components" / "frontmatter"
        
        if not frontmatter_dir.exists():
            print("  ⚠️  No frontmatter directory found")
            return
        
        frontmatter_files = list(frontmatter_dir.glob("*.md"))
        
        for fm_file in frontmatter_files:
            try:
                with open(fm_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Test YAML validity
                is_valid, yaml_message = self.test_yaml_content(fm_file, content)
                
                # Check for bracket syntax issues
                bracket_issues = self.check_bracket_syntax(content)
                
                status = 'PASS' if is_valid and not bracket_issues else 'FAIL'
                message = yaml_message
                
                if bracket_issues:
                    message += f" | Bracket issues: {len(bracket_issues)}"
                
                result = {
                    'file': str(fm_file.relative_to(self.workspace_root)),
                    'status': status,
                    'message': message,
                    'bracket_issues': bracket_issues
                }
                
                if status == 'PASS':
                    self.results['total_passed'] += 1
                else:
                    self.results['total_failed'] += 1
                    if bracket_issues:
                        self.results['errors'].extend(bracket_issues)
                        
            except Exception as e:
                result = {
                    'file': str(fm_file.relative_to(self.workspace_root)),
                    'status': 'FAIL',
                    'message': f'Error: {str(e)}',
                    'bracket_issues': []
                }
                self.results['total_failed'] += 1
            
            self.results['frontmatter_tests'].append(result)
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"  {status_icon} {result['file']}: {result['message']}")
    
    def run_all_tests(self):
        """Run all validation tests"""
        print("🧪 Starting comprehensive YAML validation tests...\n")
        
        self.test_generator_files()
        self.test_example_files()
        self.test_prompt_files()
        self.test_frontmatter_files()
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        total_tests = self.results['total_passed'] + self.results['total_failed']
        pass_rate = (self.results['total_passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print("\n📊 VALIDATION SUMMARY")
        print(f"={'=' * 50}")
        print(f"Total Tests:    {total_tests}")
        print(f"✅ Passed:      {self.results['total_passed']}")
        print(f"❌ Failed:      {self.results['total_failed']}")
        print(f"📈 Pass Rate:   {pass_rate:.1f}%")
        
        # Breakdown by category
        categories = [
            ('Generator Files', self.results['generator_tests']),
            ('Example Files', self.results['example_tests']),
            ('Prompt Files', self.results['prompt_tests']),
            ('Frontmatter Files', self.results['frontmatter_tests'])
        ]
        
        print("\n📋 CATEGORY BREAKDOWN")
        print(f"{'=' * 50}")
        for category_name, category_results in categories:
            if category_results:
                passed = sum(1 for r in category_results if r['status'] == 'PASS')
                total = len(category_results)
                rate = (passed / total * 100) if total > 0 else 0
                print(f"{category_name:<20} {passed:>3}/{total:<3} ({rate:>5.1f}%)")
        
        # Show errors if any
        if self.results['errors']:
            print("\n⚠️  ISSUES FOUND")
            print(f"{'=' * 50}")
            for error in self.results['errors'][:10]:  # Show first 10 errors
                print(f"  • {error}")
            if len(self.results['errors']) > 10:
                print(f"  ... and {len(self.results['errors']) - 10} more issues")
        
        # Final status
        if self.results['total_failed'] == 0:
            print("\n🎉 ALL TESTS PASSED! Ready for production.")
        else:
            print(f"\n⚠️  {self.results['total_failed']} tests failed. Review issues above.")
        
        return self.results['total_failed'] == 0


def main():
    """Main test runner"""
    workspace_root = "/Users/todddunning/Desktop/Z-Beam/z-beam-generator"
    
    tester = YAMLValidationTester(workspace_root)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
