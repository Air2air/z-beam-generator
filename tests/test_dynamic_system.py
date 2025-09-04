#!/usr/bin/env python3
"""
Comprehensive Test Suite for Z-Beam Dynamic Prompt System

This script tests the complete dynamic prompt generation system including:
- DynamicPromptSystem for intelligent prompt evolution
- WinstonAnalyzer for improvement detection and prioritization
- PromptEvolutionManager for history and analytics tracking
- Integration with TextComponentGenerator
- Template variable substitution and file management
"""

import sys
import os
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_dynamic_prompt_system_initialization():
    """Test that the dynamic prompt system initializes properly"""
    print("🔍 Testing Dynamic Prompt System Initialization...")

    try:
        from components.text.dynamic_prompt_system import DynamicPromptSystem

        # Test dynamic prompt system
        system = DynamicPromptSystem()

        # Check that all components loaded
        stats = system.get_current_stats()

        print(f"  ✅ System initialized with version {stats['current_version']}")
        print(f"  ✅ Evolution history: {stats['total_evolutions']} records")
        print("  ✅ Dynamic prompt system initialization successful")

    except Exception as e:
        print(f"  ❌ Dynamic prompt system initialization failed: {e}")
        pytest.fail(f"Dynamic prompt system initialization failed: {e}")

def test_winston_analyzer_functionality():
    """Test WinstonAnalyzer for improvement detection"""
    print("\n🧠 Testing Winston Analyzer...")

    try:
        from components.text.dynamic_prompt_system.winston_analyzer import WinstonAnalyzer

        analyzer = WinstonAnalyzer()

        # Test different score scenarios
        test_cases = [
            (25.0, "critical", True),   # Very low score
            (45.0, "high", True),       # Low score
            (65.0, "medium", True),     # Medium score
            (85.0, "none", False)       # High score
        ]

        for score, expected_priority, needs_improvement in test_cases:
            winston_result = {
                'overall_score': score,
                'classification': 'ai',
                'analysis': {'sentences': []}
            }

            content = "Test content for analysis."
            iteration_context = {'target_score': 70}

            analysis = analyzer.analyze_improvement_needs(
                winston_result, content, iteration_context
            )

            assert analysis['priority_level'] == expected_priority, f"Expected {expected_priority}, got {analysis['priority_level']}"
            assert analysis['needs_improvement'] == needs_improvement, f"Expected {needs_improvement}, got {analysis['needs_improvement']}"

            if needs_improvement:
                assert len(analysis['target_sections']) > 0, "Should have target sections when improvement needed"

        print("  ✅ Winston analyzer working correctly for all score ranges")
        print("  ✅ Winston analyzer test completed successfully")

    except Exception as e:
        print(f"  ❌ Winston analyzer failed: {e}")
        pytest.fail(f"Winston analyzer failed: {e}")

def test_prompt_evolution_manager():
    """Test PromptEvolutionManager functionality"""
    print("\n📊 Testing Prompt Evolution Manager...")

    try:
        from components.text.dynamic_prompt_system.prompt_evolution_manager import PromptEvolutionManager

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create temporary prompts file
            prompts_file = os.path.join(temp_dir, "ai_detection.yaml")
            with open(prompts_file, 'w') as f:
                f.write("test: content\n")

            manager = PromptEvolutionManager(prompts_file)

            # Test recording evolutions
            test_evolutions = [
                (35.0, True, ['cognitive_variability']),
                (45.0, True, ['human_authenticity_enhancements']),
                (55.0, False, ['conversational_flow']),
                (65.0, True, ['cultural_humanization'])
            ]

            for score, applied, sections in test_evolutions:
                winston_result = {'overall_score': score, 'classification': 'ai'}
                improvements = {section: 'test_data' for section in sections}
                manager.record_evolution(winston_result, improvements, applied)

            # Test statistics
            stats = manager.get_evolution_stats()
            assert stats['total_evolutions'] == 4
            assert stats['applied_evolutions'] == 3
            assert stats['success_rate'] == 75.0

            # Test section-specific queries
            cognitive_evolutions = manager.get_evolution_by_section('cognitive_variability')
            assert len(cognitive_evolutions) == 1

            # Test score improvements
            improvements = manager.get_score_improvements()
            assert len(improvements) > 0  # Should find some improvements

            print(f"  ✅ Recorded {stats['total_evolutions']} evolutions")
            print(f"  ✅ Success rate: {stats['success_rate']}%")
            print("  ✅ Prompt evolution manager test completed successfully")

    except Exception as e:
        print(f"  ❌ Prompt evolution manager failed: {e}")
        pytest.fail(f"Prompt evolution manager failed: {e}")

def test_dynamic_prompt_evolution_workflow():
    """Test complete dynamic prompt evolution workflow"""
    print("\n🔄 Testing Dynamic Prompt Evolution Workflow...")

    try:
        from components.text.dynamic_prompt_system import DynamicPromptSystem

        system = DynamicPromptSystem()

        # Test data
        winston_result = {
            'overall_score': 45.0,
            'classification': 'ai',
            'sentence_analysis': {'low_score_percentage': 15.0}
        }

        content = """
        Laser cleaning is an innovative technology that uses high-powered lasers to remove contaminants from surfaces.
        This method provides precise control and is environmentally friendly compared to traditional cleaning techniques.
        """

        iteration_context = {
            'iteration_history': [{'score': 40.0, 'classification': 'ai'}],
            'current_score': 45.0,
            'target_score': 70.0,
            'material_name': 'laser_cleaning'
        }

        # Mock the API client to avoid real API calls during testing
        with patch('components.text.dynamic_prompt_system.dynamic_prompt_generator.create_api_client') as mock_create_client:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.content = '{"improvements": [{"type": "add", "target": "test_section", "content": "test improvement"}], "expected_impact": "Test impact"}'
            mock_client.generate_simple.return_value = mock_response
            mock_create_client.return_value = mock_client

            # Test evolution workflow
            result = system.analyze_and_evolve(winston_result, content, iteration_context)

            assert result['success'] == True
            assert 'improvements_generated' in result
            assert 'improvements_applied' in result
            assert 'analysis' in result

            print("  ✅ Evolution workflow completed successfully")
            print(f"  ✅ Generated {result['improvements_generated']} improvements")
            print(f"  ✅ Applied {result['improvements_applied']} improvements")

            # Test evolution history
            history = system.get_evolution_history()
            assert len(history) >= 1

            print(f"  ✅ Evolution history: {len(history)} records")
            print("  ✅ Dynamic prompt evolution workflow test completed successfully")

    except Exception as e:
        print(f"  ❌ Dynamic prompt evolution workflow failed: {e}")
        pytest.fail(f"Dynamic prompt evolution workflow failed: {e}")

def test_template_variable_substitution():
    """Test template variable substitution in prompts"""
    print("\n🔧 Testing Template Variable Substitution...")

    try:
        from components.text.dynamic_prompt_system.dynamic_prompt_generator import DynamicPromptGenerator

        # Create a temporary prompts file with template variables
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_file = os.path.join(temp_dir, "ai_detection.yaml")
            template_content = """
target_score: ${target_score}
human_range: ${winston_human_range[0]}-${winston_human_range[1]}
ai_range: ${winston_ai_range[0]}-${winston_ai_range[1]}
test_section:
  - "Score should be above ${target_score}"
  - "Human-like range: ${winston_human_range[0]} to ${winston_human_range[1]}"
"""
            with open(prompts_file, 'w') as f:
                f.write(template_content)

            generator = DynamicPromptGenerator(prompts_file)

            # Test loading with template substitution
            prompts = generator._load_current_prompts()

            # Verify template variables were substituted
            assert 'target_score' in prompts
            assert isinstance(prompts['target_score'], (str, int, float))  # Can be string, int, or float
            assert 'human_range' in prompts
            assert isinstance(prompts['human_range'], str)
            assert '70-100' in prompts['human_range']  # Default range

            print("  ✅ Template variables substituted correctly")
            print("  ✅ Template variable substitution test completed successfully")

    except Exception as e:
        print(f"  ❌ Template variable substitution failed: {e}")
        pytest.fail(f"Template variable substitution failed: {e}")

def test_integration_with_text_component_generator():
    """Test integration with TextComponentGenerator"""
    print("\n🔗 Testing Integration with TextComponentGenerator...")

    try:
        from components.text.generator import TextComponentGenerator
        from components.text.dynamic_prompt_system import DynamicPromptSystem

        # Mock AI detection service
        mock_ai_service = MagicMock()
        mock_ai_service.is_available.return_value = False

        # Create text component generator
        text_generator = TextComponentGenerator(ai_detection_service=mock_ai_service)

        # Verify it has the expected attributes
        assert hasattr(text_generator, 'ai_detection_service')
        assert hasattr(text_generator, 'ai_detection_config')
        assert text_generator.component_type == "text"

        # Test that dynamic prompt system can be imported and used
        dynamic_system = DynamicPromptSystem()
        stats = dynamic_system.get_current_stats()

        assert 'current_version' in stats
        assert 'total_evolutions' in stats

        print("  ✅ TextComponentGenerator integration working")
        print("  ✅ Dynamic prompt system integration working")
        print("  ✅ Integration test completed successfully")

    except Exception as e:
        print(f"  ❌ Integration test failed: {e}")
        pytest.fail(f"Integration test failed: {e}")

def test_file_operations_and_persistence():
    """Test file operations and data persistence"""
    print("\n📁 Testing File Operations and Persistence...")

    try:
        from components.text.dynamic_prompt_system.prompt_evolution_manager import PromptEvolutionManager

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create temporary files
            prompts_file = os.path.join(temp_dir, "ai_detection.yaml")
            with open(prompts_file, 'w') as f:
                f.write("test: content\n")

            manager = PromptEvolutionManager(prompts_file)

            # Test evolution recording and persistence
            winston_result = {'overall_score': 45.0, 'classification': 'ai'}
            improvements = {'test_section': 'test_data'}

            manager.record_evolution(winston_result, improvements, True)

            # Create new manager instance to test persistence
            manager2 = PromptEvolutionManager(prompts_file)
            history = manager2.get_history()

            assert len(history) == 1
            assert history[0]['winston_score'] == 45.0
            assert history[0]['improvements_applied'] == True

            print("  ✅ Evolution data persisted correctly")
            print("  ✅ File operations working properly")
            print("  ✅ File operations and persistence test completed successfully")

    except Exception as e:
        print(f"  ❌ File operations test failed: {e}")
        pytest.fail(f"File operations test failed: {e}")

def test_error_handling_and_edge_cases():
    """Test error handling and edge cases"""
    print("\n⚠️  Testing Error Handling and Edge Cases...")

    try:
        from components.text.dynamic_prompt_system import DynamicPromptSystem

        system = DynamicPromptSystem()

        # Test with invalid winston result
        invalid_winston = {'invalid': 'data'}
        content = "Test content"
        iteration_context = {'target_score': 70}

        result = system.analyze_and_evolve(invalid_winston, content, iteration_context)

        # Should handle gracefully
        assert 'success' in result
        assert 'message' in result

        # Test with empty content
        empty_content = ""
        result2 = system.analyze_and_evolve(invalid_winston, empty_content, iteration_context)

        assert 'success' in result2

        # Test with missing iteration context
        incomplete_context = {}
        result3 = system.analyze_and_evolve(invalid_winston, content, incomplete_context)

        assert 'success' in result3

        print("  ✅ Error handling working correctly")
        print("  ✅ Edge cases handled gracefully")
        print("  ✅ Error handling and edge cases test completed successfully")

    except Exception as e:
        print(f"  ❌ Error handling test failed: {e}")
        pytest.fail(f"Error handling test failed: {e}")

def test_performance_and_scalability():
    """Test performance and scalability aspects"""
    print("\n⚡ Testing Performance and Scalability...")

    try:
        from components.text.dynamic_prompt_system.prompt_evolution_manager import PromptEvolutionManager

        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_file = os.path.join(temp_dir, "ai_detection.yaml")
            with open(prompts_file, 'w') as f:
                f.write("test: content\n")

            manager = PromptEvolutionManager(prompts_file)

            # Test with many evolutions
            import time
            start_time = time.time()

            # Add 100 evolutions
            for i in range(100):
                winston_result = {'overall_score': 40.0 + i * 0.3, 'classification': 'ai'}
                improvements = {'section_' + str(i % 5): 'data'}
                manager.record_evolution(winston_result, improvements, i % 2 == 0)

            end_time = time.time()
            duration = end_time - start_time

            # Test statistics calculation
            stats = manager.get_evolution_stats()

            assert stats['total_evolutions'] == 100
            assert duration < 5.0  # Should complete in reasonable time

            print(f"  ✅ Processed 100 evolutions in {duration:.2f} seconds")
            print(f"  ✅ Statistics calculated: {stats['total_evolutions']} total, {stats['success_rate']}% success rate")
            print("  ✅ Performance and scalability test completed successfully")

    except Exception as e:
        print(f"  ❌ Performance test failed: {e}")
        pytest.fail(f"Performance test failed: {e}")

def main():
    """Run all dynamic prompt system tests"""
    print("🧪 Z-BEAM DYNAMIC PROMPT SYSTEM COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    tests = [
        ("Dynamic Prompt System Initialization", test_dynamic_prompt_system_initialization),
        ("Winston Analyzer Functionality", test_winston_analyzer_functionality),
        ("Prompt Evolution Manager", test_prompt_evolution_manager),
        ("Dynamic Prompt Evolution Workflow", test_dynamic_prompt_evolution_workflow),
        ("Template Variable Substitution", test_template_variable_substitution),
        ("Integration with TextComponentGenerator", test_integration_with_text_component_generator),
        ("File Operations and Persistence", test_file_operations_and_persistence),
        ("Error Handling and Edge Cases", test_error_handling_and_edge_cases),
        ("Performance and Scalability", test_performance_and_scalability)
    ]

    passed = 0
    failed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"  ❌ {test_name} crashed: {e}")
            failed += 1

    print("\n" + "=" * 70)
    print(f"📊 DYNAMIC PROMPT SYSTEM TEST RESULTS")
    print(f"   Total Tests: {total}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success Rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("\n🎉 ALL DYNAMIC PROMPT SYSTEM TESTS PASSED!")
        print("\n📋 SYSTEM CAPABILITIES VERIFIED:")
        print("   ✅ Intelligent Winston analysis and improvement detection")
        print("   ✅ Modular architecture with focused components")
        print("   ✅ Comprehensive evolution history and statistics")
        print("   ✅ Template variable substitution and file management")
        print("   ✅ Integration with TextComponentGenerator")
        print("   ✅ Error handling and edge case management")
        print("   ✅ Performance and scalability for production use")

        print("\n🚀 QUICK START:")
        print("   from components.text.dynamic_prompt_system import DynamicPromptSystem")
        print("   system = DynamicPromptSystem()")
        print("   result = system.analyze_and_evolve(winston_result, content, context)")

    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the errors above.")
        print("\n🔧 TROUBLESHOOTING:")
        print("   1. Check that all dynamic prompt system modules are properly installed")
        print("   2. Verify file permissions for prompt files")
        print("   3. Ensure API keys are configured for full functionality")
        print("   4. Review error messages for specific issues")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
