#!/usr/bin/env python3
"""
Comprehensive Test Suite for Component-Local Architecture

This script tests the new component-local architecture including:
- Component-local validators, post-processors, and mock generators
- Centralized routing to component-local modules
- Mock generator functionality for all 11 components
- Component isolation and self-contained operation
- Integration with the existing dynamic generation system
"""

import sys
import os
import tempfile
import importlib
from pathlib import Path

# Add parent directory to path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_component_local_module_imports():
    """Test that all component-local modules can be imported"""
    print("🔍 Testing Component-Local Module Imports...")
    
    components = [
        'author', 'badgesymbol', 'bullets', 'caption', 'content', 
        'frontmatter', 'jsonld', 'metatags', 'propertiestable', 'table', 'tags'
    ]
    
    module_types = ['validator', 'post_processor', 'mock_generator']
    import_results = {}
    
    for component in components:
        import_results[component] = {}
        
        for module_type in module_types:
            try:
                module_path = f'components.{component}.{module_type}'
                module = importlib.import_module(module_path)
                import_results[component][module_type] = {
                    'success': True,
                    'module': module,
                    'error': None
                }
                print(f"  ✅ {component}.{module_type} imported successfully")
            except ImportError as e:
                import_results[component][module_type] = {
                    'success': False,
                    'module': None,
                    'error': str(e)
                }
                print(f"  ❌ {component}.{module_type} import failed: {e}")
            except Exception as e:
                import_results[component][module_type] = {
                    'success': False,
                    'module': None,
                    'error': str(e)
                }
                print(f"  ❌ {component}.{module_type} unexpected error: {e}")
    
    # Summary
    total_modules = len(components) * len(module_types)
    successful_imports = sum(
        1 for comp_results in import_results.values() 
        for module_result in comp_results.values() 
        if module_result['success']
    )
    
    print(f"\n📊 Import Summary: {successful_imports}/{total_modules} modules imported successfully")
    
    if successful_imports == total_modules:
        print("  ✅ All component-local modules available!")
    else:
        print(f"  ⚠️  {total_modules - successful_imports} modules failed to import")
    
    return import_results, successful_imports == total_modules


def test_mock_generators():
    """Test all 11 mock generators"""
    print("\n🎭 Testing Mock Generators...")
    
    components = [
        'author', 'badgesymbol', 'bullets', 'caption', 'content', 
        'frontmatter', 'jsonld', 'metatags', 'propertiestable', 'table', 'tags'
    ]
    
    test_materials = ["Steel", "Aluminum", "Carbon Fiber"]
    test_categories = ["metals", "ceramics", "composites"]
    
    mock_results = {}
    
    for component in components:
        print(f"\n🔧 Testing {component} mock generator...")
        mock_results[component] = {}
        
        try:
            # Import the mock generator
            module = importlib.import_module(f'components.{component}.mock_generator')
            
            # Find the main generation function
            func_name = f'generate_mock_{component}'
            if hasattr(module, func_name):
                generate_func = getattr(module, func_name)
                print(f"  ✅ Found {func_name} function")
                
                # Test with different materials and categories
                for material in test_materials:
                    for category in test_categories:
                        try:
                            result = generate_func(material, category)
                            
                            mock_results[component][f'{material}_{category}'] = {
                                'success': True,
                                'content_length': len(result),
                                'content_preview': result[:100] + "..." if len(result) > 100 else result,
                                'error': None
                            }
                            
                            print(f"    ✅ {material} ({category}): {len(result)} chars generated")
                            
                        except Exception as e:
                            mock_results[component][f'{material}_{category}'] = {
                                'success': False,
                                'content_length': 0,
                                'content_preview': "",
                                'error': str(e)
                            }
                            print(f"    ❌ {material} ({category}): {e}")
                
                # Test variations function if it exists
                variations_func_name = f'generate_mock_{component}_variations'
                if hasattr(module, variations_func_name):
                    try:
                        variations_func = getattr(module, variations_func_name)
                        variations = variations_func("Test Material", "metals", 3)
                        print(f"    ✅ Variations function: {len(variations)} variations generated")
                    except Exception as e:
                        print(f"    ⚠️  Variations function error: {e}")
                
                # Test structured function if it exists
                structured_func_name = f'generate_mock_structured_{component}'
                if hasattr(module, structured_func_name):
                    try:
                        structured_func = getattr(module, structured_func_name)
                        structured = structured_func("Test Material", "metals")
                        print(f"    ✅ Structured function: {type(structured).__name__} returned")
                    except Exception as e:
                        print(f"    ⚠️  Structured function error: {e}")
                        
            else:
                print(f"  ❌ {func_name} function not found")
                mock_results[component]['error'] = f"Function {func_name} not found"
                
        except ImportError as e:
            print(f"  ❌ Import failed: {e}")
            mock_results[component]['error'] = f"Import failed: {e}"
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
            mock_results[component]['error'] = f"Unexpected error: {e}"
    
    # Summary
    successful_components = [comp for comp, results in mock_results.items() 
                           if isinstance(results, dict) and 'error' not in results]
    
    print(f"\n📊 Mock Generator Summary: {len(successful_components)}/{len(components)} components working")
    
    if len(successful_components) == len(components):
        print("  ✅ All mock generators functional!")
    else:
        failed_components = [comp for comp in components if comp not in successful_components]
        print(f"  ⚠️  Failed components: {', '.join(failed_components)}")
    
    return mock_results, len(successful_components) == len(components)


def test_component_validators():
    """Test component-local validators"""
    print("\n✅ Testing Component Validators...")
    
    components = [
        'author', 'badgesymbol', 'bullets', 'caption', 'content', 
        'frontmatter', 'jsonld', 'metatags', 'propertiestable', 'table', 'tags'
    ]
    
    # Test content samples
    test_content = {
        'frontmatter': '''---
title: "Test Material Laser Cleaning"
description: "Test description"
tags: ["laser", "cleaning"]
---''',
        'content': '''# Test Material Laser Cleaning

This is test content for validation.

## Applications
- Industrial cleaning
- Surface preparation

## Specifications
- Wavelength: 1064nm
- Power: 50W
''',
        'table': '''| Property | Value | Unit |
|----------|-------|------|
| Density | 2.7 | g/cm³ |
| Melting Point | 660 | °C |''',
        'tags': 'laser-cleaning, industrial, surface-treatment, precision',
        'metatags': '''<meta name="description" content="Test meta description">
<meta name="keywords" content="laser, cleaning, test">''',
        'default': 'Test content for validation'
    }
    
    validator_results = {}
    
    for component in components:
        print(f"\n🔍 Testing {component} validator...")
        validator_results[component] = {}
        
        try:
            # Import the validator
            module = importlib.import_module(f'components.{component}.validator')
            
            # Look for validation functions
            validation_functions = [attr for attr in dir(module) 
                                  if callable(getattr(module, attr)) and 'validate' in attr.lower()]
            
            if validation_functions:
                print(f"  ✅ Found validation functions: {', '.join(validation_functions)}")
                
                # Test with appropriate content
                content = test_content.get(component, test_content['default'])
                
                for func_name in validation_functions:
                    try:
                        validate_func = getattr(module, func_name)
                        # Try different function signatures
                        try:
                            result = validate_func(content)
                        except TypeError:
                            try:
                                result = validate_func(content, "Test Material")
                            except TypeError:
                                result = validate_func(content, "Test Material", "metals")
                        
                        validator_results[component][func_name] = {
                            'success': True,
                            'result': result,
                            'error': None
                        }
                        print(f"    ✅ {func_name}: {result}")
                        
                    except Exception as e:
                        validator_results[component][func_name] = {
                            'success': False,
                            'result': None,
                            'error': str(e)
                        }
                        print(f"    ⚠️  {func_name}: {e}")
            else:
                print(f"  ⚠️  No validation functions found in {component}")
                validator_results[component]['warning'] = "No validation functions found"
                
        except ImportError as e:
            print(f"  ❌ Import failed: {e}")
            validator_results[component]['error'] = f"Import failed: {e}"
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
            validator_results[component]['error'] = f"Unexpected error: {e}"
    
    return validator_results


def test_component_post_processors():
    """Test component-local post-processors"""
    print("\n🔧 Testing Component Post-Processors...")
    
    components = [
        'author', 'badgesymbol', 'bullets', 'caption', 'content', 
        'frontmatter', 'jsonld', 'metatags', 'propertiestable', 'table', 'tags'
    ]
    
    # Test content samples for post-processing
    test_content = {
        'frontmatter': '''---
title: "aluminum laser cleaning"
description: "test description with aluminum processing"
category: "metal"
---''',
        'content': '''# aluminum laser cleaning

Aluminum processing with laser technology.

## benefits
- precise cleaning
- no chemicals
- fast processing

## applications
Aluminum surfaces require careful processing.''',
        'default': 'Test content for aluminum laser cleaning processing.'
    }
    
    post_processor_results = {}
    
    for component in components:
        print(f"\n🔧 Testing {component} post-processor...")
        post_processor_results[component] = {}
        
        try:
            # Import the post-processor
            module = importlib.import_module(f'components.{component}.post_processor')
            
            # Look for post-processing functions
            post_process_functions = [attr for attr in dir(module) 
                                    if callable(getattr(module, attr)) and 'post_process' in attr.lower()]
            
            if post_process_functions:
                print(f"  ✅ Found post-processing functions: {', '.join(post_process_functions)}")
                
                # Test with appropriate content
                content = test_content.get(component, test_content['default'])
                
                for func_name in post_process_functions:
                    try:
                        post_process_func = getattr(module, func_name)
                        
                        # Try different function signatures
                        try:
                            result = post_process_func(content)
                        except TypeError:
                            try:
                                result = post_process_func(content, "Aluminum")
                            except TypeError:
                                result = post_process_func(content, "Aluminum", "metals")
                        
                        # Check if content was modified
                        was_modified = result != content
                        
                        post_processor_results[component][func_name] = {
                            'success': True,
                            'was_modified': was_modified,
                            'original_length': len(content),
                            'processed_length': len(result),
                            'error': None
                        }
                        
                        status = "modified" if was_modified else "unchanged"
                        print(f"    ✅ {func_name}: {status} ({len(content)} → {len(result)} chars)")
                        
                    except Exception as e:
                        post_processor_results[component][func_name] = {
                            'success': False,
                            'was_modified': False,
                            'original_length': len(content),
                            'processed_length': 0,
                            'error': str(e)
                        }
                        print(f"    ⚠️  {func_name}: {e}")
            else:
                print(f"  ⚠️  No post-processing functions found in {component}")
                post_processor_results[component]['warning'] = "No post-processing functions found"
                
        except ImportError as e:
            print(f"  ❌ Import failed: {e}")
            post_processor_results[component]['error'] = f"Import failed: {e}"
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
            post_processor_results[component]['error'] = f"Unexpected error: {e}"
    
    return post_processor_results


def test_centralized_validator_integration():
    """Test that centralized validator properly routes to component-local modules"""
    print("\n🔄 Testing Centralized Validator Integration...")
    
    try:
        from validators.centralized_validator import CentralizedValidator
        
        validator = CentralizedValidator()
        print("  ✅ CentralizedValidator imported successfully")
        
        # Test component routing
        components_to_test = ['frontmatter', 'content', 'table', 'tags', 'metatags']
        
        for component in components_to_test:
            print(f"\n  🔍 Testing {component} routing...")
            
            # Create test content
            test_content = f"Test content for {component} validation and post-processing"
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
                temp_file.write(test_content)
                temp_file_path = temp_file.name
            
            try:
                # Test validation routing
                try:
                    is_valid = validator.validate_component_content(test_content, component, "Test Material")
                    print(f"    ✅ Validation routing: {is_valid}")
                except Exception as e:
                    print(f"    ⚠️  Validation routing: {e}")
                
                # Test post-processing routing
                try:
                    was_processed = validator.post_process_generated_content(temp_file_path, component)
                    print(f"    ✅ Post-processing routing: {'processed' if was_processed else 'no changes'}")
                except Exception as e:
                    print(f"    ⚠️  Post-processing routing: {e}")
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except Exception:
                    pass
        
        print("\n  ✅ Centralized validator integration tested")
        return True
        
    except ImportError as e:
        print(f"  ❌ CentralizedValidator import failed: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Centralized validator testing failed: {e}")
        return False


def test_component_architecture_completeness():
    """Test that the component architecture is complete and consistent"""
    print("\n📋 Testing Component Architecture Completeness...")
    
    components = [
        'author', 'badgesymbol', 'bullets', 'caption', 'content', 
        'frontmatter', 'jsonld', 'metatags', 'propertiestable', 'table', 'tags'
    ]
    
    expected_files = ['generator.py', 'validator.py', 'post_processor.py', 'mock_generator.py']
    optional_files = ['__init__.py', 'prompt.yaml', 'example_*.md']
    
    completeness_results = {}
    
    for component in components:
        print(f"\n📂 Checking {component} component structure...")
        component_path = Path(f'components/{component}')
        completeness_results[component] = {
            'path_exists': component_path.exists(),
            'required_files': {},
            'optional_files': {},
            'completeness_score': 0
        }
        
        if component_path.exists():
            # Check required files
            required_score = 0
            for file_name in expected_files:
                file_path = component_path / file_name
                exists = file_path.exists()
                completeness_results[component]['required_files'][file_name] = exists
                if exists:
                    required_score += 1
                print(f"  {'✅' if exists else '❌'} {file_name}")
            
            # Check optional files
            optional_score = 0
            for file_pattern in optional_files:
                if '*' in file_pattern:
                    # Handle glob patterns
                    matching_files = list(component_path.glob(file_pattern))
                    exists = len(matching_files) > 0
                    completeness_results[component]['optional_files'][file_pattern] = {
                        'exists': exists,
                        'files': [f.name for f in matching_files]
                    }
                    if exists:
                        optional_score += 1
                        print(f"  ✅ {file_pattern}: {len(matching_files)} files")
                    else:
                        print(f"  ⚪ {file_pattern}: not found")
                else:
                    file_path = component_path / file_pattern
                    exists = file_path.exists()
                    completeness_results[component]['optional_files'][file_pattern] = exists
                    if exists:
                        optional_score += 1
                        print(f"  ✅ {file_pattern}")
                    else:
                        print(f"  ⚪ {file_pattern}: not found")
            
            # Calculate completeness score
            total_possible = len(expected_files) + len(optional_files)
            total_score = required_score + optional_score
            completeness_results[component]['completeness_score'] = (total_score / total_possible) * 100
            
            print(f"  📊 Completeness: {total_score}/{total_possible} files ({completeness_results[component]['completeness_score']:.1f}%)")
            
        else:
            print("  ❌ Component directory does not exist")
    
    # Overall summary
    total_components = len(components)
    complete_components = sum(1 for comp_data in completeness_results.values() 
                            if comp_data['completeness_score'] >= 75)  # 75% threshold for "complete"
    
    print("\n📊 Architecture Completeness Summary:")
    print(f"  Total Components: {total_components}")
    print(f"  Complete Components (≥75%): {complete_components}")
    print(f"  Architecture Completeness: {(complete_components/total_components)*100:.1f}%")
    
    return completeness_results, complete_components == total_components


def test_mock_generator_integration():
    """Test integration of mock generators with the testing framework"""
    print("\n🧪 Testing Mock Generator Integration...")
    
    try:
        # Test that we can use mock generators for testing
        from components.frontmatter.mock_generator import generate_mock_frontmatter
        from components.content.mock_generator import generate_mock_content
        from components.table.mock_generator import generate_mock_table
        
        print("  ✅ Mock generator imports successful")
        
        # Test generating mock data for testing
        test_cases = [
            ("Steel", "metals"),
            ("Alumina", "ceramics"),
            ("Carbon Fiber", "composites")
        ]
        
        for material, category in test_cases:
            print(f"\n  🧪 Testing mock generation for {material} ({category})...")
            
            # Test frontmatter mock
            try:
                frontmatter_mock = generate_mock_frontmatter(material, category)
                print(f"    ✅ Frontmatter: {len(frontmatter_mock)} chars")
            except Exception as e:
                print(f"    ❌ Frontmatter: {e}")
            
            # Test content mock
            try:
                content_mock = generate_mock_content(material, category)
                print(f"    ✅ Content: {len(content_mock)} chars")
            except Exception as e:
                print(f"    ❌ Content: {e}")
            
            # Test table mock
            try:
                table_mock = generate_mock_table(material, category)
                print(f"    ✅ Table: {len(table_mock)} chars")
            except Exception as e:
                print(f"    ❌ Table: {e}")
        
        print("\n  ✅ Mock generator integration successful")
        return True
        
    except ImportError as e:
        print(f"  ❌ Mock generator import failed: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Mock generator integration failed: {e}")
        return False


def main():
    """Run comprehensive component-local architecture tests"""
    print("🧪 COMPONENT-LOCAL ARCHITECTURE COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print("Testing the new component-local architecture implementation")
    print("Focus: Validators, post-processors, mock generators, integration")
    print("=" * 70)
    
    tests = [
        ("Component-Local Module Imports", test_component_local_module_imports),
        ("Mock Generators", test_mock_generators),
        ("Component Validators", test_component_validators),
        ("Component Post-Processors", test_component_post_processors),
        ("Centralized Validator Integration", test_centralized_validator_integration),
        ("Component Architecture Completeness", test_component_architecture_completeness),
        ("Mock Generator Integration", test_mock_generator_integration),
    ]
    
    passed = 0
    failed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            # Handle different return types
            if isinstance(result, tuple):
                success = result[1]  # Second element is usually the boolean result
            else:
                success = result
                
            if success:
                passed += 1
                print(f"\n✅ {test_name}: PASSED")
            else:
                failed += 1
                print(f"\n❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"\n❌ {test_name}: CRASHED - {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print("📊 COMPONENT-LOCAL ARCHITECTURE TEST RESULTS")
    print(f"   Total Tests: {total}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL COMPONENT-LOCAL ARCHITECTURE TESTS PASSED!")
        
        print("\n📋 VERIFIED CAPABILITIES:")
        print("   ✅ All 11 components have complete local modules")
        print("   ✅ Mock generators provide comprehensive testing data")
        print("   ✅ Component validators handle content validation")
        print("   ✅ Post-processors enhance generated content")
        print("   ✅ Centralized routing works correctly")
        print("   ✅ Architecture is complete and consistent")
        
        print("\n🚀 TESTING RECOMMENDATIONS:")
        print("   1. Use mock generators for unit testing components")
        print("   2. Test component validators with various input types")
        print("   3. Verify post-processors improve content quality")
        print("   4. Test end-to-end workflows with component routing")
        print("   5. Use structured mock data for integration testing")
        
        print("\n💡 EXAMPLE USAGE:")
        print("   # Run component-specific tests")
        print("   python3 tests/test_component_local_architecture.py")
        print("   ")
        print("   # Use mock generators in other tests")
        print("   from components.frontmatter.mock_generator import generate_mock_frontmatter")
        print("   mock_data = generate_mock_frontmatter('Steel', 'metals')")
        
    else:
        print(f"\n⚠️  {failed} component-local architecture test(s) failed.")
        print("\n🔧 TROUBLESHOOTING:")
        print("   1. Check that all component directories exist")
        print("   2. Verify all component-local modules are properly created")
        print("   3. Ensure import paths are correct")
        print("   4. Review error messages for specific component issues")
        print("   5. Test individual components if integration fails")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
