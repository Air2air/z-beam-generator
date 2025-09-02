#!/usr/bin/env python3
"""
Component Template Tests

Tests for template components that use author data and other dynamic variables.

Tests:
- Template variable substitution
- Author data integration in templates
- Component prompt validation
- Template rendering accuracy
"""

import sys
import yaml
import unittest
from pathlib import Path

# Add parent directory to path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from run import load_authors, get_author_by_id


class TestComponentTemplates(unittest.TestCase):
    """Test suite for component templates and author integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.components_dir = Path("components")
        self.test_author = get_author_by_id(1)  # Use first author for testing
        
    def test_frontmatter_template_has_author_field(self):
        """Test that frontmatter template includes author field"""
        frontmatter_prompt = self.components_dir / "frontmatter" / "prompt.yaml"
        
        if frontmatter_prompt.exists():
            with open(frontmatter_prompt, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for author field placeholder
            self.assertIn("author: {author_name}", content, 
                         "Frontmatter template should include author field")
            self.assertIn("{author_name}", content,
                         "Frontmatter template should use author_name variable")
                         
    def test_tags_template_includes_author(self):
        """Test that tags template includes author name"""
        tags_prompt = self.components_dir / "tags" / "prompt.yaml"
        
        if tags_prompt.exists():
            with open(tags_prompt, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for author slug inclusion in tags (tags uses author_slug not author_name)
            self.assertIn("{author_slug}", content,
                         "Tags template should include author_slug variable")
                         
    def test_metatags_template_has_author_meta(self):
        """Test that metatags template includes author meta tag"""
        metatags_prompt = self.components_dir / "metatags" / "prompt.yaml"
        
        if metatags_prompt.exists():
            with open(metatags_prompt, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for author meta tag
            self.assertIn("name: author", content,
                         "Metatags template should include author meta tag")
            self.assertIn("{author_name}", content,
                         "Metatags template should use author_name variable")
                         
    def test_jsonld_template_includes_author(self):
        """Test that JSON-LD template includes author information"""
        jsonld_prompt = self.components_dir / "jsonld" / "prompt.yaml"
        
        if jsonld_prompt.exists():
            with open(jsonld_prompt, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for author field in JSON-LD format
            self.assertIn('"author": {', content,
                         "JSON-LD template should include author object")
            self.assertIn("{author_name}", content,
                         "JSON-LD template should use author_name variable")
                         
    def test_component_prompt_files_exist(self):
        """Test that all component directories have prompt.yaml files or appropriate prompt structure"""
        expected_components = [
            "frontmatter", "tags", "metatags", "jsonld", 
            "content", "bullets", "caption", "table"
        ]
        
        for component in expected_components:
            component_dir = self.components_dir / component
            prompt_file = component_dir / "prompt.yaml"
            
            with self.subTest(component=component):
                self.assertTrue(component_dir.exists(), 
                               f"Component directory should exist: {component}")
                
                # Content component uses a different architecture with prompts subdirectory
                if component == "content":
                    prompts_dir = component_dir / "prompts"
                    self.assertTrue(prompts_dir.exists(),
                                   f"Content component should have prompts directory: {component}/prompts")
                    # Check that there are some prompt files in the prompts directory
                    prompt_files = list(prompts_dir.glob("*.yaml"))
                    self.assertGreater(len(prompt_files), 0,
                                     f"Content component should have prompt files in prompts directory")
                else:
                    self.assertTrue(prompt_file.exists(),
                                   f"Prompt file should exist: {component}/prompt.yaml")
                               
    def test_prompt_files_are_valid_yaml(self):
        """Test that all prompt.yaml files contain valid YAML"""
        for component_dir in self.components_dir.iterdir():
            if component_dir.is_dir():
                component_name = component_dir.name
                
                # Handle content component's different structure
                if component_name == "content":
                    prompts_dir = component_dir / "prompts"
                    if prompts_dir.exists():
                        for prompt_file in prompts_dir.glob("*.yaml"):
                            with self.subTest(component=f"{component_name}/{prompt_file.name}"):
                                try:
                                    with open(prompt_file, 'r', encoding='utf-8') as f:
                                        yaml.safe_load(f)
                                except yaml.YAMLError as e:
                                    self.fail(f"Invalid YAML in {component_name}/prompts/{prompt_file.name}: {e}")
                else:
                    prompt_file = component_dir / "prompt.yaml"
                    
                    if prompt_file.exists():
                        with self.subTest(component=component_name):
                            try:
                                with open(prompt_file, 'r', encoding='utf-8') as f:
                                    yaml.safe_load(f)
                            except yaml.YAMLError as e:
                                self.fail(f"Invalid YAML in {component_name}/prompt.yaml: {e}")
                            
    def test_template_variables_consistency(self):
        """Test that author-related template variables are consistently named"""
        author_variables = ["{author_name}", "{author_title}", "{author_expertise}"]
        
        for component_dir in self.components_dir.iterdir():
            if component_dir.is_dir():
                prompt_file = component_dir / "prompt.yaml"
                
                if prompt_file.exists():
                    with open(prompt_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # If any author variable is used, check naming consistency
                    if any(var in content for var in author_variables):
                        with self.subTest(component=component_dir.name):
                            # Should use {author_name} not variations like {author} or {authorName}
                            self.assertNotIn("{author}", content,
                                           f"Use {{author_name}} instead of {{author}} in {component_dir.name}")
                            self.assertNotIn("{authorName}", content,
                                           f"Use {{author_name}} instead of {{authorName}} in {component_dir.name}")
                            self.assertNotIn("{Author}", content,
                                           f"Use {{author_name}} instead of {{Author}} in {component_dir.name}")


class TestGeneratedContent(unittest.TestCase):
    """Test generated content for author data integrity"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.content_dir = Path("content/components")
        self.authors = load_authors()
        
    def test_generated_files_contain_author_names(self):
        """Test that generated files contain valid author names"""
        if not self.content_dir.exists():
            self.skipTest("No generated content directory found")
            
        author_names = [author["name"] for author in self.authors]
        
        # Check various component types for author references
        component_types = ["frontmatter", "jsonld", "metatags"]
        
        for component_type in component_types:
            component_dir = self.content_dir / component_type
            
            if component_dir.exists():
                for content_file in component_dir.glob("*.md"):
                    with self.subTest(file=content_file.name, component=component_type):
                        with open(content_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Check if any author name appears in the content
                        found_author = False
                        for author_name in author_names:
                            if author_name in content:
                                found_author = True
                                break
                                
                        if not found_author and "author" in content.lower():
                            # If the word "author" appears but no valid author name found
                            self.fail(f"File {content_file.name} mentions author but doesn't contain valid author name")


def run_tests():
    """Run all component template tests and return results"""
    print("🧪 COMPONENT TEMPLATE TESTS")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestComponentTemplates))
    suite.addTests(loader.loadTestsFromTestCase(TestGeneratedContent))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEMPLATE TEST RESULTS")
    print("=" * 60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    
    print("📈 TEST STATISTICS:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failures}")
    print(f"   🔥 Errors: {errors}")
    print(f"   📊 Success Rate: {success_rate:.1f}%")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, failure in result.failures:
            print(f"   • {test}: {failure.split('AssertionError: ')[-1].split('\\n')[0]}")
            
    if result.errors:
        print("\n🔥 ERRORS:")
        for test, error in result.errors:
            print(f"   • {test}: {error.split('\\n')[-2]}")
    
    # Overall assessment
    if success_rate == 100:
        print("\n🎉 EXCELLENT! All template tests passed.")
        print("   Component templates are properly configured for author integration.")
    elif success_rate >= 80:
        print("\n✅ GOOD! Most template tests passed.")
        print("   Component templates are largely functional with minor issues.")
    else:
        print("\n⚠️  ISSUES DETECTED! Some template tests failed.")
        print("   Component templates need attention before production use.")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
