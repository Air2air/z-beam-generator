#!/usr/bin/env python3
"""
Author System Tests

Comprehensive testing for author loading, validation, and usage throughout the system.

Tests:
- Author data loading and parsing
- Author schema validation
- Author lookup functionality
- Author data integrity
- Author field usage in components
"""

import sys
import json
import unittest
from pathlib import Path

# Add parent directory to path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from run import load_authors, get_author_by_id


class TestAuthorSystem(unittest.TestCase):
    """Test suite for the author system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.authors_file = Path("components/author/authors.json")
        self.schema_file = Path("schemas/author.json")
        
    def test_authors_file_exists(self):
        """Test that authors.json file exists"""
        self.assertTrue(
            self.authors_file.exists(), 
            f"Authors file not found: {self.authors_file}"
        )
        
    def test_author_schema_exists(self):
        """Test that author schema file exists"""
        self.assertTrue(
            self.schema_file.exists(), 
            f"Author schema file not found: {self.schema_file}"
        )
        
    def test_authors_file_valid_json(self):
        """Test that authors.json is valid JSON"""
        try:
            with open(self.authors_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.assertIsInstance(data, dict, "Authors file should contain a JSON object")
        except json.JSONDecodeError as e:
            self.fail(f"Authors file contains invalid JSON: {e}")
            
    def test_author_schema_valid_json(self):
        """Test that author schema is valid JSON"""
        try:
            with open(self.schema_file, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            self.assertIsInstance(schema, dict, "Author schema should contain a JSON object")
        except json.JSONDecodeError as e:
            self.fail(f"Author schema contains invalid JSON: {e}")
            
    def test_load_authors_function(self):
        """Test load_authors function returns list"""
        authors = load_authors()
        self.assertIsInstance(authors, list, "load_authors should return a list")
        self.assertGreater(len(authors), 0, "Authors list should not be empty")
        
    def test_author_data_structure(self):
        """Test that each author has required fields"""
        authors = load_authors()
        required_fields = ["id", "name", "title", "country", "expertise", "image"]
        
        for author in authors:
            with self.subTest(author=author.get("name", "Unknown")):
                self.assertIsInstance(author, dict, "Each author should be a dictionary")
                
                # Check all required fields exist
                for field in required_fields:
                    self.assertIn(field, author, f"Author missing required field: {field}")
                    self.assertIsNotNone(author[field], f"Author field {field} should not be None")
                    self.assertNotEqual(author[field], "", f"Author field {field} should not be empty")
                    
    def test_author_id_uniqueness(self):
        """Test that author IDs are unique"""
        authors = load_authors()
        author_ids = [author["id"] for author in authors]
        unique_ids = set(author_ids)
        
        self.assertEqual(
            len(author_ids), 
            len(unique_ids), 
            f"Author IDs are not unique: {author_ids}"
        )
        
    def test_author_id_types(self):
        """Test that author IDs are integers"""
        authors = load_authors()
        
        for author in authors:
            with self.subTest(author=author.get("name", "Unknown")):
                self.assertIsInstance(
                    author["id"], 
                    int, 
                    f"Author ID should be integer, got {type(author['id'])}"
                )
                self.assertGreater(
                    author["id"], 
                    0, 
                    f"Author ID should be positive, got {author['id']}"
                )
                
    def test_author_image_paths(self):
        """Test that author image paths follow expected format"""
        authors = load_authors()
        expected_prefix = "public/images/author/"
        expected_suffix = ".jpg"
        
        for author in authors:
            with self.subTest(author=author.get("name", "Unknown")):
                image_path = author["image"]
                self.assertTrue(
                    image_path.startswith(expected_prefix),
                    f"Image path should start with '{expected_prefix}', got '{image_path}'"
                )
                self.assertTrue(
                    image_path.endswith(expected_suffix),
                    f"Image path should end with '{expected_suffix}', got '{image_path}'"
                )
                
    def test_get_author_by_id_function(self):
        """Test get_author_by_id function"""
        authors = load_authors()
        
        # Test with valid IDs
        for author in authors:
            author_id = author["id"]
            retrieved_author = get_author_by_id(author_id)
            
            with self.subTest(author_id=author_id):
                self.assertIsNotNone(retrieved_author, f"Could not retrieve author with ID {author_id}")
                self.assertEqual(
                    retrieved_author["id"], 
                    author_id, 
                    f"Retrieved author ID mismatch: expected {author_id}, got {retrieved_author['id']}"
                )
                self.assertEqual(
                    retrieved_author["name"], 
                    author["name"], 
                    f"Retrieved author name mismatch for ID {author_id}"
                )
                
    def test_get_author_by_invalid_id(self):
        """Test get_author_by_id with invalid IDs"""
        # Test with non-existent ID
        invalid_author = get_author_by_id(999)
        self.assertIsNone(invalid_author, "Should return None for non-existent author ID")
        
        # Test with negative ID
        negative_author = get_author_by_id(-1)
        self.assertIsNone(negative_author, "Should return None for negative author ID")
        
        # Test with zero ID
        zero_author = get_author_by_id(0)
        self.assertIsNone(zero_author, "Should return None for zero author ID")
        
    def test_author_countries_are_valid(self):
        """Test that author countries are meaningful"""
        authors = load_authors()
        expected_countries = ["Taiwan", "Italy", "Indonesia", "United States (California)"]
        
        for author in authors:
            with self.subTest(author=author.get("name", "Unknown")):
                country = author["country"]
                self.assertIn(
                    country, 
                    expected_countries, 
                    f"Unexpected country '{country}' for author {author['name']}"
                )
                
    def test_author_titles_are_consistent(self):
        """Test that author titles follow expected format"""
        authors = load_authors()
        expected_title = "Ph.D."
        
        for author in authors:
            with self.subTest(author=author.get("name", "Unknown")):
                title = author["title"]
                self.assertEqual(
                    title, 
                    expected_title, 
                    f"Expected title '{expected_title}', got '{title}' for author {author['name']}"
                )
                
    def test_author_expertise_consistency(self):
        """Test that author expertise fields are consistent"""
        authors = load_authors()
        expected_expertise = "Materials Science and Laser Technology"
        
        for author in authors:
            with self.subTest(author=author.get("name", "Unknown")):
                expertise = author["expertise"]
                self.assertEqual(
                    expertise, 
                    expected_expertise, 
                    f"Expected expertise '{expected_expertise}', got '{expertise}' for author {author['name']}"
                )
                
    def test_author_names_are_properly_formatted(self):
        """Test that author names are properly formatted"""
        authors = load_authors()
        
        for author in authors:
            with self.subTest(author=author.get("name", "Unknown")):
                name = author["name"]
                
                # Should contain at least first and last name
                name_parts = name.split()
                self.assertGreaterEqual(
                    len(name_parts), 
                    2, 
                    f"Author name should have at least 2 parts, got '{name}'"
                )
                
                # Should be title case
                for part in name_parts:
                    self.assertTrue(
                        part[0].isupper(), 
                        f"Name part '{part}' should be title case in '{name}'"
                    )
                    
    def test_schema_version_and_metadata(self):
        """Test schema metadata is correct"""
        with open(self.schema_file, 'r', encoding='utf-8') as f:
            schema = json.load(f)
            
        # Test schema metadata
        self.assertEqual(schema["name"], "authorSchema", "Schema name should be 'authorSchema'")
        self.assertEqual(schema["version"], "2.0", "Schema version should be '2.0'")
        self.assertEqual(schema["schemaType"], "AuthorSchema", "Schema type should be 'AuthorSchema'")
        
        # Test required fields in schema
        author_properties = schema["author"]["properties"]
        required_fields = ["id", "name", "title", "country", "expertise", "image"]
        
        for field in required_fields:
            self.assertIn(field, author_properties, f"Schema missing required field: {field}")
            self.assertTrue(
                author_properties[field].get("required", False),
                f"Schema field {field} should be required"
            )


class TestAuthorIntegration(unittest.TestCase):
    """Test author system integration with other components"""
    
    def test_author_system_in_dynamic_generator(self):
        """Test that author system integrates with dynamic generator"""
        try:
            from generators.dynamic_generator import DynamicGenerator
            
            # Test that DynamicGenerator can be imported and has author methods
            generator = DynamicGenerator()
            self.assertTrue(hasattr(generator, 'set_author'), "DynamicGenerator should have set_author method")
            self.assertTrue(hasattr(generator, 'author_info'), "DynamicGenerator should have author_info attribute")
            
        except ImportError as e:
            self.fail(f"Could not import DynamicGenerator: {e}")
            
    def test_author_template_variables(self):
        """Test that author data can be used in template variables"""
        try:
            from generators.dynamic_generator import DynamicGenerator
            
            generator = DynamicGenerator()
            
            # Test with a real author
            authors = load_authors()
            test_author = authors[0] if authors else None
            
            if test_author:
                generator.set_author(test_author)
                
                # Simulate getting template variables
                template_vars = {}
                if generator.author_info:
                    template_vars['author_name'] = generator.author_info.get('name', 'Expert Author')
                    template_vars['author_title'] = generator.author_info.get('title', 'Technical Expert')
                    template_vars['author_expertise'] = generator.author_info.get('expertise', 'Laser Processing')
                
                # Test that template variables are populated correctly
                self.assertEqual(template_vars['author_name'], test_author['name'])
                self.assertEqual(template_vars['author_title'], test_author['title'])
                self.assertEqual(template_vars['author_expertise'], test_author['expertise'])
                
        except ImportError as e:
            self.skipTest(f"Could not import DynamicGenerator: {e}")


def run_tests():
    """Run all author tests and return results"""
    print("🧪 AUTHOR SYSTEM TESTS")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAuthorSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthorIntegration))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 AUTHOR TEST RESULTS")
    print("=" * 60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📈 TEST STATISTICS:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failures}")
    print(f"   🔥 Errors: {errors}")
    print(f"   📊 Success Rate: {success_rate:.1f}%")
    
    if result.failures:
        print(f"\n❌ FAILURES:")
        for test, failure in result.failures:
            print(f"   • {test}: {failure.split('AssertionError: ')[-1].split('\\n')[0]}")
            
    if result.errors:
        print(f"\n🔥 ERRORS:")
        for test, error in result.errors:
            print(f"   • {test}: {error.split('\\n')[-2]}")
    
    # Overall assessment
    if success_rate == 100:
        print(f"\n🎉 EXCELLENT! All author tests passed.")
        print("   The author system is fully functional and ready for use.")
    elif success_rate >= 80:
        print(f"\n✅ GOOD! Most author tests passed.")
        print("   The author system is largely functional with minor issues.")
    else:
        print(f"\n⚠️  ISSUES DETECTED! Some author tests failed.")
        print("   The author system needs attention before production use.")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
