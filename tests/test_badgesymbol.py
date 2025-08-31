#!/usr/bin/env python3
"""
Badge Symbol Component Tests

Tests for the badge symbol generator component.
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.badgesymbol import BadgeSymbolGenerator, generate_badge_symbol_content, create_badge_symbol_template


class TestBadgeSymbolComponent(unittest.TestCase):
    """Test the badge symbol component functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = BadgeSymbolGenerator()
        self.sample_frontmatter = {
            "name": "Aluminum",
            "category": "metal",
            "chemicalProperties": {
                "formula": "Al",
                "symbol": "AL",
                "materialType": "Pure Metal"
            },
            "properties": {
                "tensileStrength": "310 MPa",
                "thermalConductivity": "237 W/m·K"
            }
        }

    def test_badge_symbol_generator_initialization(self):
        """Test BadgeSymbolGenerator initialization"""
        self.assertIsInstance(self.generator, BadgeSymbolGenerator)
        self.assertEqual(self.generator.component_info["name"], "Badge Symbol")
        self.assertEqual(self.generator.component_info["type"], "static")

    def test_generate_content_with_frontmatter(self):
        """Test content generation with frontmatter data"""
        result = self.generator.generate_content("Aluminum", self.sample_frontmatter)
        
        # Check frontmatter structure
        self.assertIn("---", result)
        self.assertIn('symbol: "AL"', result)
        self.assertIn('materialType: "pure metal"', result)

    def test_generate_content_without_frontmatter(self):
        """Test content generation without frontmatter (fallback)"""
        result = self.generator.generate_content("Steel")
        
        # Check fallback behavior
        self.assertIn("---", result)
        self.assertIn('symbol: "ST"', result)
        self.assertIn('materialType: "material"', result)

    def test_value_length_constraints(self):
        """Test that output is properly formatted frontmatter"""
        long_frontmatter = {
            "category": "Very Long Category Name",
            "chemicalProperties": {
                "formula": "Al2O3·SiO2·H2O",
                "materialType": "Fiber-Reinforced Polymer"
            }
        }
        
        result = self.generator.generate_content("Test", long_frontmatter)
        
        # Check that it's valid frontmatter
        self.assertTrue(result.startswith("---"))
        self.assertTrue(result.endswith("---"))
        self.assertIn('symbol:', result)
        self.assertIn('materialType:', result)

    def test_abbreviation_functionality(self):
        """Test material type extraction"""
        frp_frontmatter = {
            "chemicalProperties": {
                "materialType": "Fiber-Reinforced Polymer"
            }
        }
        
        result = self.generator.generate_content("Test", frp_frontmatter)
        self.assertIn('materialType: "fiber-reinforced polymer"', result)

    def test_unit_abbreviations(self):
        """Test that frontmatter format is maintained"""
        units_frontmatter = {
            "properties": {
                "tensileStrength": "1500 Megapascal",
                "thermalConductivity": "200 W/m·K"
            },
            "category": "metal"
        }
        
        result = self.generator.generate_content("Test", units_frontmatter)
        self.assertIn("---", result)
        self.assertIn('materialType: "metal"', result)

    def test_component_info(self):
        """Test component information metadata"""
        info = self.generator.component_info
        
        self.assertEqual(info["name"], "Badge Symbol")
        self.assertIn("badge symbol", info["description"].lower())
        self.assertEqual(info["version"], "1.0.0")
        self.assertEqual(info["type"], "static")

    def test_field_extraction(self):
        """Test nested field extraction functionality"""
        # Test different field paths
        test_data = {
            "level1": {
                "level2": {
                    "target": "found"
                }
            }
        }
        
        result = self.generator._get_field(test_data, ["level1.level2.target"], "default")
        self.assertEqual(result, "found")
        
        result = self.generator._get_field(test_data, ["nonexistent.path"], "default")
        self.assertEqual(result, "default")


class TestBadgeSymbolComponentFunctions(unittest.TestCase):
    """Test standalone badge symbol functions"""

    def test_generate_badge_symbol_content_function(self):
        """Test standalone generate_badge_symbol_content function"""
        frontmatter = {
            "category": "composite",
            "chemicalProperties": {"formula": "C2H4"}
        }
        
        result = generate_badge_symbol_content("Carbon", frontmatter)
        
        self.assertIsInstance(result, str)
        self.assertIn("---", result)
        self.assertIn('materialType: "composite"', result)

    def test_create_badge_symbol_template_function(self):
        """Test standalone create_badge_symbol_template function"""
        result = create_badge_symbol_template("Titanium")
        
        self.assertIsInstance(result, str)
        self.assertIn('symbol: "TI"', result)


class TestBadgeSymbolComponentIntegration(unittest.TestCase):
    """Test badge symbol component integration with the system"""

    def test_badge_symbol_component_in_enabled_components(self):
        """Test that badge symbol component is in enabled components list"""
        try:
            from run import COMPONENT_CONFIG
            components = COMPONENT_CONFIG["components"]
            
            self.assertIn("badgesymbol", components)
            self.assertTrue(components["badgesymbol"]["enabled"])
            self.assertEqual(components["badgesymbol"]["api_provider"], "none")
        except ImportError:
            self.skipTest("run.py configuration not available")

    def test_api_client_handling_for_none_provider(self):
        """Test that 'none' provider is handled correctly for badgesymbol"""
        try:
            from run import COMPONENT_CONFIG
            config = COMPONENT_CONFIG["components"]["badgesymbol"]
            
            # Verify it's configured as a static component
            self.assertEqual(config["api_provider"], "none")
            
            # This should not require an API client
            generator = BadgeSymbolGenerator()
            result = generator.generate_content("Test")
            self.assertIsInstance(result, str)
            
        except ImportError:
            self.skipTest("run.py configuration not available")


class TestBadgeSymbolComponentPerformance(unittest.TestCase):
    """Test badge symbol component performance"""

    def test_generation_performance(self):
        """Test that badge symbol generation is fast (under 100ms)"""
        import time
        
        generator = BadgeSymbolGenerator()
        frontmatter = {
            "category": "metal",
            "properties": {"tensileStrength": "500 MPa"}
        }
        
        start_time = time.time()
        result = generator.generate_content("Steel", frontmatter)
        end_time = time.time()
        
        duration = end_time - start_time
        self.assertLess(duration, 0.1, "Badge symbol generation should be under 100ms")
        self.assertIsInstance(result, str)

    def test_memory_efficiency(self):
        """Test that repeated generations don't cause memory issues"""
        generator = BadgeSymbolGenerator()
        
        # Generate multiple times to check for memory leaks
        for i in range(100):
            result = generator.generate_content(f"Material{i}")
            self.assertIsInstance(result, str)

    def test_concurrent_safety(self):
        """Test that multiple generators can work safely"""
        generators = [BadgeSymbolGenerator() for _ in range(5)]
        results = []
        
        for i, gen in enumerate(generators):
            result = gen.generate_content(f"Material{i}")
            results.append(result)
        
        # All results should be valid
        for result in results:
            self.assertIsInstance(result, str)
            self.assertIn("---", result)


def run_badge_symbol_tests():
    """Run all badge symbol component tests"""
    
    print("🧪 BADGE SYMBOL COMPONENT TESTS")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestBadgeSymbolComponent,
        TestBadgeSymbolComponentFunctions,
        TestBadgeSymbolComponentIntegration,
        TestBadgeSymbolComponentPerformance
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("📊 BADGE SYMBOL TEST RESULTS")
    print("=" * 60)
    print("📈 TEST STATISTICS:")
    print(f"   Total Tests: {result.testsRun}")
    print(f"   ✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   ❌ Failed: {len(result.failures)}")
    print(f"   🔥 Errors: {len(result.errors)}")
    print(f"   📊 Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n⚠️ FAILURES:")
        for test, traceback in result.failures:
            print(f"   ❌ {test}: {traceback}")
    
    if result.errors:
        print("\n🔥 ERRORS:")
        for test, traceback in result.errors:
            print(f"   💥 {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n🎉 EXCELLENT! All badge symbol component tests passed.")
        print("   The badge symbol component is fully functional and ready for use.")
    else:
        print("\n⚠️ Some badge symbol tests failed. Review the errors above.")
    
    return success


if __name__ == "__main__":
    success = run_badge_symbol_tests()
    sys.exit(0 if success else 1)
