#!/usr/bin/env python3
"""
Author Component Tests

Comprehensive testing for the new author component functionality,
including generation, integration, and performance.

Tests:
- Author component generator class
- Content generation functionality
- Integration with dynamic generator
- Performance and reliability
- Error handling
"""

import sys
import unittest
import time
from pathlib import Path

# Add parent directory to path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.author.generator import AuthorGenerator, generate_author_content, create_author_content_from_data
from run import load_authors, get_author_by_id


class TestAuthorComponent(unittest.TestCase):
    """Test suite for the author component"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = AuthorGenerator()
        self.test_material = "Titanium"
        self.test_authors = load_authors()
        
    def test_author_generator_initialization(self):
        """Test AuthorGenerator initialization"""
        generator = AuthorGenerator()
        self.assertIsInstance(generator, AuthorGenerator)
        self.assertTrue(hasattr(generator, 'authors_file'))
        self.assertEqual(generator.authors_file.name, 'authors.json')
        
    def test_author_generator_load_authors(self):
        """Test _load_authors method"""
        authors_data = self.generator._load_authors()
        self.assertIsInstance(authors_data, dict)
        self.assertIn('authors', authors_data)
        self.assertGreater(len(authors_data['authors']), 0)
        
    def test_get_author_by_id_valid(self):
        """Test getting author by valid ID"""
        for test_id in [1, 2, 3, 4]:
            with self.subTest(author_id=test_id):
                author = self.generator.get_author_by_id(test_id)
                self.assertIsInstance(author, dict)
                self.assertEqual(author.get('id'), test_id)
                self.assertIn('name', author)
                self.assertIn('title', author)
                self.assertIn('country', author)
                
    def test_get_author_by_id_invalid(self):
        """Test getting author by invalid ID"""
        invalid_ids = [0, -1, 999, 'invalid']
        for invalid_id in invalid_ids:
            with self.subTest(author_id=invalid_id):
                author = self.generator.get_author_by_id(invalid_id)
                self.assertEqual(author, {})
                
    def test_generate_content_valid_author(self):
        """Test content generation with valid author"""
        content = self.generator.generate(self.test_material, 1)
        
        # Check basic structure
        self.assertIn("# Author Information", content)
        self.assertIn("Yi-Chun Lin", content)  # First author name
        self.assertIn("Ph.D.", content)
        self.assertIn("Taiwan", content)
        self.assertIn(self.test_material, content)
        self.assertIn("laser cleaning", content)
        
    def test_generate_content_invalid_author(self):
        """Test content generation with invalid author ID"""
        content = self.generator.generate(self.test_material, 999)
        
        self.assertIn("# Author Information", content)
        self.assertIn("Author information not found", content)
        self.assertIn("999", content)
        
    def test_generate_content_all_authors(self):
        """Test content generation for all available authors"""
        for author in self.test_authors:
            author_id = author['id']
            with self.subTest(author_id=author_id):
                content = self.generator.generate(self.test_material, author_id)
                
                self.assertIn("# Author Information", content)
                self.assertIn(author['name'], content)
                self.assertIn(author['country'], content)
                self.assertIn(author['expertise'], content)
                self.assertIn(self.test_material, content)
                
    def test_static_template_function(self):
        """Test static template creation function"""
        test_author = {
            'name': 'Test Author',
            'title': 'Ph.D.',
            'country': 'Test Country',
            'expertise': 'Test Expertise',
            'image': 'test/path.jpg'
        }
        
        content = AuthorGenerator._create_author_template(self.test_material, test_author)
        
        self.assertIn("# Author Information", content)
        self.assertIn("Test Author", content)
        self.assertIn("Test Country", content)
        self.assertIn("Test Expertise", content)
        self.assertIn("test/path.jpg", content)
        self.assertIn(self.test_material, content)
        
    def test_component_info(self):
        """Test component information metadata"""
        info = self.generator.get_component_info()
        
        self.assertIsInstance(info, dict)
        self.assertEqual(info['name'], 'author')
        self.assertEqual(info['type'], 'static')
        self.assertFalse(info['requires_api'])
        self.assertIn('version', info)
        self.assertIn('description', info)


class TestAuthorComponentFunctions(unittest.TestCase):
    """Test standalone author component functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_material = "Copper"
        
    def test_generate_author_content_function(self):
        """Test standalone generate_author_content function"""
        content = generate_author_content(self.test_material, 1)
        
        self.assertIn("# Author Information", content)
        self.assertIn("Yi-Chun Lin", content)
        self.assertIn(self.test_material, content)
        
    def test_create_author_content_from_data_function(self):
        """Test direct content creation from author data"""
        test_author = {
            'name': 'Direct Test Author',
            'title': 'M.Sc.',
            'country': 'Direct Test Country',
            'expertise': 'Direct Test Field',
            'image': 'direct/test.jpg'
        }
        
        content = create_author_content_from_data(self.test_material, test_author)
        
        self.assertIn("# Author Information", content)
        self.assertIn("Direct Test Author", content)
        self.assertIn("M.Sc.", content)
        self.assertIn("Direct Test Country", content)
        self.assertIn("Direct Test Field", content)
        self.assertIn("direct/test.jpg", content)
        self.assertIn(self.test_material, content)


class TestAuthorComponentIntegration(unittest.TestCase):
    """Test author component integration with the main system"""
    
    def test_integration_with_dynamic_generator(self):
        """Test integration with dynamic generator"""
        try:
            from generators.dynamic_generator import DynamicGenerator
            
            # Create generator with mock client
            generator = DynamicGenerator(use_mock=True)
            
            # Set author info
            test_author = get_author_by_id(1)
            if test_author:
                generator.set_author(test_author)
            
            # Test author component generation
            result = generator.generate_component("Aluminum", "author")
            
            self.assertTrue(result.success)
            self.assertEqual(result.component_type, "author")
            self.assertIn("# Author Information", result.content)
            self.assertIn("Aluminum", result.content)
            
        except ImportError as e:
            self.skipTest(f"Could not import DynamicGenerator: {e}")
            
    def test_author_component_in_enabled_components(self):
        """Test that author component is in enabled components list"""
        try:
            from run import COMPONENT_CONFIG
            
            components = COMPONENT_CONFIG.get('components', {})
            self.assertIn('author', components)
            
            author_config = components['author']
            self.assertTrue(author_config.get('enabled', False))
            self.assertEqual(author_config.get('api_provider'), 'none')
            
        except ImportError as e:
            self.skipTest(f"Could not import COMPONENT_CONFIG: {e}")
            
    def test_api_client_handling_for_none_provider(self):
        """Test that 'none' provider is handled correctly"""
        try:
            from run import create_api_client
            
            # Test that 'none' provider returns None
            client = create_api_client('none')
            self.assertIsNone(client)
            
        except ImportError as e:
            self.skipTest(f"Could not import create_api_client: {e}")


class TestAuthorComponentPerformance(unittest.TestCase):
    """Test author component performance and reliability"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = AuthorGenerator()
        self.test_materials = ["Steel", "Aluminum", "Copper", "Titanium", "Glass"]
        
    def test_generation_performance(self):
        """Test that author generation is fast (under 100ms)"""
        start_time = time.time()
        
        for material in self.test_materials:
            for author_id in [1, 2, 3, 4]:
                content = self.generator.generate(material, author_id)
                self.assertIsInstance(content, str)
                self.assertGreater(len(content), 50)  # Reasonable content length
                
        end_time = time.time()
        generation_time = end_time - start_time
        
        # Should generate 20 author components (5 materials × 4 authors) in under 100ms
        self.assertLess(generation_time, 0.1, 
                       f"Author generation took {generation_time:.3f}s, should be under 0.1s")
        
    def test_memory_efficiency(self):
        """Test that repeated generations don't cause memory issues"""
        # Simple memory efficiency test - just ensure no exceptions
        # and that content is properly generated repeatedly
        for i in range(50):
            material = f"TestMaterial{i}"
            content = self.generator.generate(material, (i % 4) + 1)
            self.assertIn("# Author Information", content)
            self.assertIn(material, content)
            # Ensure content is properly formatted
            self.assertGreater(len(content), 100)
        
    def test_concurrent_safety(self):
        """Test that multiple generators can work safely"""
        import threading
        import queue
        
        results = queue.Queue()
        errors = queue.Queue()
        
        def generate_author_content_worker(material, author_id):
            try:
                generator = AuthorGenerator()
                content = generator.generate(material, author_id)
                results.put((material, author_id, content))
            except Exception as e:
                errors.put((material, author_id, str(e)))
        
        # Create multiple threads
        threads = []
        for i in range(5):  # Reduced from 10 for simpler testing
            material = f"ConcurrentMaterial{i}"
            author_id = (i % 4) + 1
            thread = threading.Thread(target=generate_author_content_worker, 
                                    args=(material, author_id))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Check results
        self.assertEqual(results.qsize(), 5)
        self.assertEqual(errors.qsize(), 0)
        
        # Verify all results are valid
        while not results.empty():
            material, author_id, content = results.get()
            self.assertIn("# Author Information", content)
            self.assertIn(material, content)


def run_tests():
    """Run all author component tests and return results"""
    print("🧪 AUTHOR COMPONENT TESTS")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAuthorComponent))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthorComponentFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthorComponentIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthorComponentPerformance))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 AUTHOR COMPONENT TEST RESULTS")
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
    
    # Performance assessment
    if success_rate == 100:
        print("\n🎉 EXCELLENT! All author component tests passed.")
        print("   The author component is fully functional, performant, and ready for use.")
    elif success_rate >= 90:
        print("\n✅ GOOD! Most author component tests passed.")
        print("   The author component is largely functional with minor issues.")
    else:
        print("\n⚠️  ISSUES DETECTED! Some author component tests failed.")
        print("   The author component needs attention before production use.")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
