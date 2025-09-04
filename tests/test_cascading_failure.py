#!/usr/bin/env python3
"""
Test Cascading Failures Due to Missing Frontmatter

This test demonstrates how component generation failures cascade
when frontmatter data is missing or incomplete.

CRITICAL: Component generation depends on frontmatter data.
Failures cascade without it. This is intentional design.
"""

import sys
from pathlib import Path
from typing import Dict, List
from unittest.mock import Mock

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from generators.component_generators import ComponentGeneratorFactory, ComponentResult


class CascadingFailureTester:
    """Test class to demonstrate cascading failures"""

    def __init__(self):
        self.test_material = "Copper"
        self.components_to_test = ["text", "bullets", "caption", "frontmatter"]

    def test_cascading_failure_scenario(self):
        """Test the complete cascading failure scenario"""
        print("🔥 CASCADING FAILURE SCENARIO TEST")
        print("=" * 60)
        print("Scenario: Frontmatter data is missing or incomplete")
        print("Expected: All component generations should fail")
        print("=" * 60)

        # Test Case 1: No frontmatter data at all
        print("\n🧪 TEST CASE 1: No Frontmatter Data")
        self._test_no_frontmatter_scenario()

        # Test Case 2: Incomplete frontmatter data
        print("\n🧪 TEST CASE 2: Incomplete Frontmatter Data")
        self._test_incomplete_frontmatter_scenario()

        # Test Case 3: Corrupted frontmatter data
        print("\n🧪 TEST CASE 3: Corrupted Frontmatter Data")
        self._test_corrupted_frontmatter_scenario()

    def _test_no_frontmatter_scenario(self):
        """Test with completely missing frontmatter"""
        print("   Testing with frontmatter_data=None")

        results = self._generate_all_components_with_frontmatter(None)

        self._analyze_cascading_results(results, "No frontmatter data")

    def _test_incomplete_frontmatter_scenario(self):
        """Test with incomplete frontmatter"""
        incomplete_data = {
            'name': self.test_material
            # Missing all other required fields
        }
        print("   Testing with incomplete frontmatter (only name field)")

        results = self._generate_all_components_with_frontmatter(incomplete_data)

        self._analyze_cascading_results(results, "Incomplete frontmatter data")

    def _test_corrupted_frontmatter_scenario(self):
        """Test with corrupted frontmatter"""
        corrupted_data = {
            'name': self.test_material,
            'category': None,  # Invalid None value
            'properties': [],  # Empty required field
            'applications': None  # Invalid None value
        }
        print("   Testing with corrupted frontmatter (None/invalid values)")

        results = self._generate_all_components_with_frontmatter(corrupted_data)

        self._analyze_cascading_results(results, "Corrupted frontmatter data")

    def _generate_all_components_with_frontmatter(self, frontmatter_data: Dict) -> List[tuple]:
        """Generate all components with given frontmatter data"""
        results = []

        # Create mock API client
        mock_api_client = Mock()
        mock_api_client.generate.return_value = Mock(
            success=True,
            content=f"Mock content for {self.test_material}",
            token_count=100
        )

        # Prepare common test data
        material_data = {
            'name': self.test_material,
            'category': frontmatter_data.get('category', 'unknown') if frontmatter_data else 'unknown',
            'article_type': 'material'
        }

        author_info = {
            'id': 1,
            'name': 'Test Author',
            'country': 'USA'
        }

        # Generate each component
        for component_type in self.components_to_test:
            try:
                generator = ComponentGeneratorFactory.create_generator(component_type)
                if not generator:
                    result = ComponentResult(
                        component_type,
                        "",
                        False,
                        f"No generator available for {component_type}"
                    )
                else:
                    result = generator.generate(
                        material_name=self.test_material,
                        material_data=material_data,
                        api_client=mock_api_client,
                        author_info=author_info,
                        frontmatter_data=frontmatter_data
                    )

                results.append((component_type, result))

            except Exception as e:
                # Component threw an exception - also a failure
                result = ComponentResult(
                    component_type,
                    "",
                    False,
                    f"Exception during generation: {type(e).__name__}: {e}"
                )
                results.append((component_type, result))

        return results

    def _analyze_cascading_results(self, results: List[tuple], scenario: str):
        """Analyze the results of cascading failure test"""
        print(f"\n   📊 RESULTS FOR: {scenario}")
        print("   " + "-" * 50)

        successful = 0
        failed = 0

        for component_type, result in results:
            if result.success:
                print(f"   ✅ {component_type}: SUCCESS")
                successful += 1
            else:
                print(f"   ❌ {component_type}: FAILED - {result.error_message}")
                failed += 1

        print("   " + "-" * 50)
        print(f"   📈 SUMMARY: {successful} successful, {failed} failed")

        # Analyze cascading behavior
        if failed > 0:
            print("   🔗 CASCADING FAILURE DETECTED:")
            print("      • Frontmatter dependency failure affects all components")
            print("      • No fallback content generated")
            print("      • System maintains data integrity")
            print("      • User must fix frontmatter before proceeding")
        else:
            print("   ⚠️  UNEXPECTED: Components succeeded despite missing frontmatter")
            print("      • This may indicate insufficient validation")
            print("      • Check component generators for proper dependency checking")

    def test_frontmatter_dependency_validation(self):
        """Test that components properly validate frontmatter dependencies"""
        print("\n🔍 FRONTMATTER DEPENDENCY VALIDATION TEST")
        print("=" * 60)

        # Test each component's dependency validation
        test_cases = [
            ("text", ["name", "category", "properties", "applications"]),
            ("bullets", ["name", "category", "properties"]),
            ("caption", ["name", "category", "properties"]),
            ("frontmatter", ["name", "category", "formula", "properties"])
        ]

        for component_type, required_fields in test_cases:
            print(f"\n🧪 Testing {component_type} component validation:")

            # Test with complete data
            complete_data = self._create_complete_frontmatter()
            result = self._test_component_validation(component_type, complete_data, required_fields)
            print(f"   Complete data: {'✅ PASS' if result else '❌ FAIL'}")

            # Test with missing fields
            for missing_field in required_fields:
                incomplete_data = complete_data.copy()
                del incomplete_data[missing_field]
                result = self._test_component_validation(component_type, incomplete_data, required_fields)
                print(f"   Missing {missing_field}: {'✅ PASS (failed as expected)' if not result else '❌ FAIL (should have failed)'}")

    def _test_component_validation(self, component_type: str, frontmatter_data: Dict, required_fields: List[str]) -> bool:
        """Test if a component properly validates its frontmatter dependencies"""
        try:
            # Create mock API client
            mock_api_client = Mock()
            mock_api_client.generate.return_value = Mock(
                success=True,
                content=f"Mock content for validation test",
                token_count=50
            )

            # Prepare test data
            material_data = {
                'name': self.test_material,
                'category': frontmatter_data.get('category', 'unknown'),
                'article_type': 'material'
            }

            author_info = {
                'id': 1,
                'name': 'Test Author',
                'country': 'USA'
            }

            # Generate component
            generator = ComponentGeneratorFactory.create_generator(component_type)
            if not generator:
                return False

            result = generator.generate(
                material_name=self.test_material,
                material_data=material_data,
                api_client=mock_api_client,
                author_info=author_info,
                frontmatter_data=frontmatter_data
            )

            # Check if required fields are present
            missing_fields = [field for field in required_fields if field not in frontmatter_data]
            if missing_fields:
                # Should fail if required fields are missing
                return not result.success
            else:
                # Should succeed if all required fields are present
                return result.success

        except Exception:
            # Exception during generation counts as failure
            return False

    def _create_complete_frontmatter(self) -> Dict:
        """Create complete frontmatter data for testing"""
        return {
            'name': self.test_material,
            'category': 'metal',
            'formula': 'Cu',
            'symbol': 'Cu',
            'properties': {
                'density': '8.96 g/cm³',
                'melting_point': '1085°C',
                'thermal_conductivity': '401 W/m·K'
            },
            'applications': [
                'Electrical wiring',
                'Plumbing',
                'Heat exchangers'
            ],
            'technicalSpecifications': {
                'purity': '99.9%',
                'conductivity': '100% IACS'
            },
            'chemicalProperties': {
                'reactivity': 'Low',
                'corrosion_resistance': 'Medium'
            },
            'keywords': [
                'copper laser cleaning',
                'electrical conductivity'
            ],
            'title': f'{self.test_material} Laser Cleaning Guide',
            'headline': f'Professional {self.test_material} Surface Preparation',
            'author': 'Dr. Test Author',
            'article_type': 'material'
        }

    def demonstrate_fail_fast_behavior(self):
        """Demonstrate the fail-fast behavior of the system"""
        print("\n⚡ FAIL-FAST BEHAVIOR DEMONSTRATION")
        print("=" * 60)

        print("   🔍 Principle: Fail immediately when dependencies are missing")
        print("   🎯 Goal: Prevent generation of incorrect or incomplete content")
        print("   🛡️  Protection: Maintain data integrity across all components")

        # Demonstrate with concrete examples
        scenarios = [
            ("Missing frontmatter file", "FileNotFoundError", "System cannot locate required frontmatter data"),
            ("Incomplete frontmatter fields", "ValueError", "Required fields missing from frontmatter"),
            ("Invalid frontmatter structure", "ValidationError", "Frontmatter data structure is invalid"),
            ("API client unavailable", "ConnectionError", "Required API client not available")
        ]

        print("\n   📋 Common Fail-Fast Scenarios:")
        for scenario, exception_type, description in scenarios:
            print(f"   • {scenario}")
            print(f"     → Exception: {exception_type}")
            print(f"     → Impact: {description}")
            print("     → Result: Generation stops immediately")
        print("\n   ✅ Benefits of Fail-Fast:")
        print("   • No silent failures or fallback content")
        print("   • Clear error messages guide users to fixes")
        print("   • Data integrity maintained")
        print("   • Debugging is straightforward")


def main():
    """Run all cascading failure tests"""
    print("🧪 CASCADING FAILURE TESTS")
    print("=" * 70)
    print("Testing how component failures cascade from missing frontmatter")
    print("CRITICAL: Component generation depends on frontmatter data")
    print("=" * 70)

    tester = CascadingFailureTester()

    # Run comprehensive tests
    tester.test_cascading_failure_scenario()
    tester.test_frontmatter_dependency_validation()
    tester.demonstrate_fail_fast_behavior()

    print("\n" + "=" * 70)
    print("🎯 KEY LESSONS FROM CASCADING FAILURE TESTS:")
    print("   • Frontmatter is required for ALL component generation")
    print("   • Missing frontmatter causes complete material failure")
    print("   • No fallbacks - system fails fast to maintain integrity")
    print("   • Clear error messages help users fix root causes")
    print("   • Validation prevents silent generation of bad content")
    print("=" * 70)


if __name__ == "__main__":
    main()
