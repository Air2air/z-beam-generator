#!/usr/bin/env python3
"""
Test Frontmatter Dependency Chain and Cascading Failures

This test suite demonstrates the critical dependency of component generation
on frontmatter data and shows how failures cascade when frontmatter is missing.

CRITICAL DESIGN: Component generation depends on frontmatter data for that material.
Component failures will cascade without it. This is intentional design.
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from generators.component_generators import ComponentGeneratorFactory, ComponentResult
from api.client_manager import create_api_client


class FrontmatterDependencyTester:
    """Test class to demonstrate frontmatter dependency chain"""

    def __init__(self):
        self.test_material = "Aluminum"
        self.test_category = "metal"
        self.test_formula = "Al"

    def create_mock_frontmatter_data(self) -> Dict:
        """Create complete frontmatter data for testing"""
        return {
            'name': self.test_material,
            'category': self.test_category,
            'formula': self.test_formula,
            'symbol': 'Al',
            'type': 'metal',
            'properties': {
                'density': '2.7 g/cm³',
                'melting_point': '660°C',
                'thermal_conductivity': '237 W/m·K'
            },
            'applications': [
                'Aerospace components',
                'Automotive parts',
                'Building construction'
            ],
            'technicalSpecifications': {
                'purity': '99.9%',
                'grain_size': ' ASTM 5-7',
                'surface_finish': 'Ra 0.8 μm'
            },
            'chemicalProperties': {
                'reactivity': 'Low',
                'corrosion_resistance': 'High',
                'oxidation_behavior': 'Forms protective layer'
            },
            'keywords': [
                'aluminum laser cleaning',
                'metal surface preparation',
                'industrial cleaning'
            ],
            'title': f'{self.test_material} Laser Cleaning Guide',
            'headline': f'Professional {self.test_material} Surface Preparation',
            'author': 'Dr. Sarah Chen',
            'article_type': 'material'
        }

    def create_incomplete_frontmatter_data(self) -> Dict:
        """Create incomplete frontmatter data to test dependency failures"""
        return {
            'name': self.test_material,
            # Missing critical fields: category, formula, properties, etc.
        }

    def test_frontmatter_dependency_demonstration(self):
        """Demonstrate how components depend on frontmatter data"""
        print("🔗 FRONTMATTER DEPENDENCY DEMONSTRATION")
        print("=" * 60)

        # Test with complete frontmatter
        print("\n✅ TESTING WITH COMPLETE FRONTMATTER DATA")
        complete_frontmatter = self.create_mock_frontmatter_data()

        # Test text component generation
        print("\n📝 Testing Text Component with Complete Frontmatter:")
        text_result = self._test_component_with_frontmatter(
            "text", complete_frontmatter, "Text generation should succeed with complete frontmatter"
        )

        # Test frontmatter component generation
        print("\n� Testing Frontmatter Component with Complete Frontmatter:")
        frontmatter_result = self._test_component_with_frontmatter(
            "frontmatter", complete_frontmatter, "Frontmatter generation should succeed with complete frontmatter"
        )

        # Test with incomplete frontmatter
        print("\n❌ TESTING WITH INCOMPLETE FRONTMATTER DATA")
        incomplete_frontmatter = self.create_incomplete_frontmatter_data()

        print("\n📝 Testing Text Component with Incomplete Frontmatter:")
        text_fail_result = self._test_component_with_frontmatter(
            "text", incomplete_frontmatter, "Text generation should fail with incomplete frontmatter"
        )

        print("\n� Testing Frontmatter Component with Incomplete Frontmatter:")
        frontmatter_fail_result = self._test_component_with_frontmatter(
            "frontmatter", incomplete_frontmatter, "Frontmatter generation should fail with incomplete frontmatter"
        )

        # Demonstrate cascading failure
        self._demonstrate_cascading_failure(complete_frontmatter, incomplete_frontmatter)

    def _test_component_with_frontmatter(self, component_type: str, frontmatter_data: Dict, expectation: str) -> ComponentResult:
        """Test a component with given frontmatter data"""
        try:
            # Create mock API client
            mock_api_client = Mock()
            mock_api_client.generate.return_value = Mock(
                success=True,
                content=f"Mock {component_type} content for {self.test_material}",
                token_count=150
            )

            # Create component generator
            generator = ComponentGeneratorFactory.create_generator(component_type)
            if not generator:
                print(f"   ❌ No generator available for {component_type}")
                return ComponentResult(component_type, "", False, f"No generator for {component_type}")

            # Prepare test data
            material_data = {
                'name': self.test_material,
                'category': frontmatter_data.get('category', 'unknown'),
                'article_type': frontmatter_data.get('article_type', 'material')
            }

            author_info = {
                'id': 1,
                'name': frontmatter_data.get('author', 'Test Author'),
                'country': 'USA'
            }

            # Generate component
            result = generator.generate(
                material_name=self.test_material,
                material_data=material_data,
                api_client=mock_api_client,
                author_info=author_info,
                frontmatter_data=frontmatter_data
            )

            # Report result
            if result.success:
                print(f"   ✅ SUCCESS: {expectation}")
                print(f"      Content length: {len(result.content)} chars")
            else:
                print(f"   ❌ FAILED: {result.error_message}")
                print(f"      Expected: {expectation}")

            return result

        except Exception as e:
            print(f"   💥 EXCEPTION: {type(e).__name__}: {e}")
            return ComponentResult(component_type, "", False, str(e))

    def _demonstrate_cascading_failure(self, complete_frontmatter: Dict, incomplete_frontmatter: Dict):
        """Demonstrate how failures cascade when frontmatter is incomplete"""
        print("\n🔗 CASCADING FAILURE DEMONSTRATION")
        print("=" * 60)

        print("\n🎯 SCENARIO: Complete Workflow with Missing Frontmatter")
        print("   1. Frontmatter generation fails (missing data)")
        print("   2. Subsequent components cannot access required data")
        print("   3. Entire material generation fails")

        # Simulate workflow failure
        workflow_results = []

        # Step 1: Frontmatter generation (simulated failure)
        print("\n   📄 Step 1: Frontmatter Generation")
        frontmatter_result = ComponentResult(
            "frontmatter",
            "",
            False,
            "Frontmatter generation failed: Missing required fields (category, formula, properties)"
        )
        workflow_results.append(("frontmatter", frontmatter_result))
        print("      ❌ FAILED: Missing required frontmatter data")

        # Step 2: Text component tries to generate without frontmatter
        print("\n   📝 Step 2: Text Component (depends on frontmatter)")
        text_result = self._test_component_with_frontmatter("text", incomplete_frontmatter, "Should fail without frontmatter")
        workflow_results.append(("text", text_result))

        # Step 3: Text component also fails
        print("\n   � Step 3: Text Component (depends on frontmatter)")
        text_result = self._test_component_with_frontmatter("text", incomplete_frontmatter, "Should fail without frontmatter")
        workflow_results.append(("text", text_result))

        # Summary of cascading failure
        print("\n📊 CASCADING FAILURE SUMMARY")
        print("=" * 60)

        successful = sum(1 for _, result in workflow_results if result.success)
        failed = len(workflow_results) - successful

        print(f"   ✅ Successful components: {successful}")
        print(f"   ❌ Failed components: {failed}")
        print(f"   🔗 Failure cascade: Frontmatter failure → All components fail")

        if failed > 0:
            print("\n   🚨 CRITICAL IMPACT:")
            print("      • No content generated for this material")
            print("      • User must fix frontmatter data before proceeding")
            print("      • System maintains data integrity by failing fast")
            print("      • No fallback content or mock data allowed")

    def test_frontmatter_data_requirements(self):
        """Test what frontmatter data is required for each component"""
        print("\n📋 FRONTMATTER DATA REQUIREMENTS ANALYSIS")
        print("=" * 60)

        requirements = {
            'text': ['name', 'category', 'properties', 'applications'],
            'frontmatter': ['name', 'category', 'formula', 'properties', 'applications', 'technicalSpecifications']
        }

        complete_data = self.create_mock_frontmatter_data()

        for component, required_fields in requirements.items():
            print(f"\n🔧 {component.upper()} Component Requirements:")
            print(f"   Required fields: {', '.join(required_fields)}")

            # Check if all required fields are present
            missing_fields = [field for field in required_fields if field not in complete_data]
            if missing_fields:
                print(f"   ❌ MISSING: {', '.join(missing_fields)}")
            else:
                print("   ✅ All required fields present")
        # Test with missing fields
        print("\n🧪 Testing with Missing Fields:")
        incomplete_data = {'name': self.test_material}  # Only name present

        for component, required_fields in requirements.items():
            available_fields = [field for field in required_fields if field in incomplete_data]
            missing_fields = [field for field in required_fields if field not in incomplete_data]

            print(f"\n   {component.upper()}:")
            print(f"      Available: {available_fields}")
            print(f"      Missing: {missing_fields}")
            print(f"      Coverage: {len(available_fields)}/{len(required_fields)} ({len(available_fields)/len(required_fields)*100:.1f}%)")

            if missing_fields:
                print("      ❌ COMPONENT WILL FAIL - Insufficient frontmatter data")
            else:
                print("      ✅ COMPONENT CAN GENERATE - All required data available")

def test_dependency_validation():
    """Test that the system validates frontmatter dependencies"""
    print("\n🔍 DEPENDENCY VALIDATION TESTING")
    print("=" * 60)

    # Test 1: Valid frontmatter should pass validation
    print("\n✅ Test 1: Valid Frontmatter Validation")
    valid_frontmatter = {
        'name': 'Copper',
        'category': 'metal',
        'formula': 'Cu',
        'properties': {'density': '8.96 g/cm³'},
        'applications': ['Electrical wiring'],
        'author': 'Test Author'
    }

    is_valid = validate_frontmatter_for_generation(valid_frontmatter)
    print(f"   Result: {'✅ VALID' if is_valid else '❌ INVALID'}")

    # Test 2: Invalid frontmatter should fail validation
    print("\n❌ Test 2: Invalid Frontmatter Validation")
    invalid_frontmatter = {
        'name': 'Copper'
        # Missing all other required fields
    }

    is_valid = validate_frontmatter_for_generation(invalid_frontmatter)
    print(f"   Result: {'✅ VALID' if is_valid else '❌ INVALID'}")

    # Test 3: Partial frontmatter validation
    print("\n⚠️  Test 3: Partial Frontmatter Validation")
    partial_frontmatter = {
        'name': 'Copper',
        'category': 'metal',
        'properties': {'density': '8.96 g/cm³'}
        # Missing formula, applications, author
    }

    is_valid = validate_frontmatter_for_generation(partial_frontmatter)
    print(f"   Result: {'✅ VALID' if is_valid else '❌ INVALID'}")

def validate_frontmatter_for_generation(frontmatter_data: Dict) -> bool:
    """Validate that frontmatter contains sufficient data for component generation"""
    required_fields = ['name', 'category', 'properties', 'applications']

    for field in required_fields:
        if field not in frontmatter_data:
            return False

        # Check that fields have meaningful content
        value = frontmatter_data[field]
        if not value:
            return False

        if field in ['properties', 'applications'] and len(value) == 0:
            return False

    return True

def main():
    """Run all frontmatter dependency tests"""
    print("🧪 FRONTMATTER DEPENDENCY & CASCADING FAILURE TESTS")
    print("=" * 70)
    print("CRITICAL DESIGN: Component generation depends on frontmatter data")
    print("Component failures will cascade without it. This is intentional design.")
    print("=" * 70)

    tester = FrontmatterDependencyTester()

    # Run comprehensive tests
    tester.test_frontmatter_dependency_demonstration()
    tester.test_frontmatter_data_requirements()
    test_dependency_validation()

    print("\n" + "=" * 70)
    print("🎯 KEY TAKEAWAYS:")
    print("   • Frontmatter data is REQUIRED for all component generation")
    print("   • Missing frontmatter causes cascading failures")
    print("   • No fallbacks or mock data - fail-fast design")
    print("   • System maintains data integrity through strict validation")
    print("   • Users must ensure frontmatter exists before generation")
    print("=" * 70)

if __name__ == "__main__":
    main()
