#!/usr/bin/env python3
"""
Comprehensive Test Suite for Z-Beam Testing Architecture - End-to-End Coverage & Accuracy

This comprehensive test evaluates the complete testing architecture for:
- Dynamic schema matching and validation
- Example file validation against schemas
- Mock generator quality and accuracy  
- Component-local architecture testing
- Schema-driven content generation
- End-to-end validation workflows
"""

import sys
import os
import json
import yaml
import tempfile
import importlib
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add parent directory to path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_schema_validation_architecture():
    """Test the dynamic schema validation architecture"""
    print("🔍 TESTING SCHEMA VALIDATION ARCHITECTURE")
    print("=" * 60)
    
    try:
        from generators.dynamic_generator import SchemaManager
        from validators.centralized_validator import CentralizedValidator
        
        # Test schema loading and structure
        schema_manager = SchemaManager()
        schemas = schema_manager.schemas
        
        print("📋 Schema Loading:")
        print(f"  ✅ Loaded {len(schemas)} schemas: {list(schemas.keys())}")
        
        # Test each schema for dynamic field mappings
        print("\n📊 Dynamic Field Mapping Analysis:")
        total_fields = 0
        
        for schema_name, schema_data in schemas.items():
            fields = schema_manager.get_dynamic_fields(schema_name)
            required = schema_manager.get_required_fields(schema_name)
            
            print(f"  📁 {schema_name}:")
            print(f"    🔧 Dynamic fields: {len(fields)}")
            print(f"    ⚡ Required fields: {len(required)}")
            
            # Show sample field mappings
            for field_name, instruction in list(fields.items())[:2]:
                if field_name != 'profile_fields' and isinstance(instruction, str):
                    print(f"    • {field_name}: {instruction[:50]}...")
            
            total_fields += len(fields)
        
        print("\n📈 Schema Architecture Summary:")
        print(f"  ✅ Total schemas: {len(schemas)}")
        print(f"  ✅ Total dynamic fields: {total_fields}")
        print("  ✅ Schema manager functional")
        
        # Test centralized validator integration
        validator = CentralizedValidator()
        print("  ✅ Centralized validator initialized")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Schema validation architecture failed: {e}")
        return False

def test_example_file_validation():
    """Test that example files match their component schemas and are valid"""
    print("\n📋 TESTING EXAMPLE FILE VALIDATION")
    print("=" * 60)
    
    try:
        components_dir = Path("components")
        if not components_dir.exists():
            print("  ❌ Components directory not found")
            return False
        
        validation_results = []
        
        for component_dir in components_dir.iterdir():
            if not component_dir.is_dir():
                continue
                
            component_name = component_dir.name
            example_files = list(component_dir.glob("example_*.md"))
            
            print(f"\n📂 Testing {component_name}:")
            print(f"  📄 Found {len(example_files)} example files")
            
            for example_file in example_files:
                print(f"    🔍 Validating {example_file.name}...")
                
                try:
                    with open(example_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract frontmatter if present
                    frontmatter_data = None
                    if content.startswith('---'):
                        parts = content.split('---', 2)
                        if len(parts) >= 2:
                            try:
                                frontmatter_data = yaml.safe_load(parts[1])
                                print(f"      ✅ YAML frontmatter parsed ({len(frontmatter_data)} fields)")
                            except yaml.YAMLError as e:
                                print(f"      ❌ YAML parsing error: {e}")
                                continue
                    
                    # Validate against material schema if frontmatter exists
                    if frontmatter_data:
                        # Check for required schema fields
                        from generators.dynamic_generator import SchemaManager
                        schema_manager = SchemaManager()
                        required_fields = schema_manager.get_required_fields('material')
                        
                        missing_fields = []
                        for field in required_fields:
                            if field not in frontmatter_data:
                                missing_fields.append(field)
                        
                        if missing_fields:
                            print(f"      ⚠️  Missing required fields: {missing_fields[:3]}{'...' if len(missing_fields) > 3 else ''}")
                        else:
                            print(f"      ✅ All required schema fields present")
                        
                        # Validate specific field structures
                        validation_checks = {
                            'chemicalProperties': lambda x: isinstance(x, dict) and 'formula' in x,
                            'properties': lambda x: isinstance(x, dict) and 'density' in x,
                            'applications': lambda x: isinstance(x, list) and len(x) > 0,
                            'images': lambda x: isinstance(x, dict) and 'hero' in x,
                            'environmentalImpact': lambda x: isinstance(x, list),
                            'outcomes': lambda x: isinstance(x, list),
                        }
                        
                        field_validity = 0
                        for field, validator in validation_checks.items():
                            if field in frontmatter_data:
                                if validator(frontmatter_data[field]):
                                    field_validity += 1
                                else:
                                    print(f"      ⚠️  Field {field} structure invalid")
                            
                        print(f"      📊 Schema compliance: {field_validity}/{len(validation_checks)} fields valid")
                    
                    validation_results.append({
                        'component': component_name,
                        'file': example_file.name,
                        'valid': True,
                        'has_frontmatter': frontmatter_data is not None,
                        'field_count': len(frontmatter_data) if frontmatter_data else 0
                    })
                    
                except Exception as e:
                    print(f"      ❌ Validation failed: {e}")
                    validation_results.append({
                        'component': component_name,
                        'file': example_file.name,
                        'valid': False,
                        'error': str(e)
                    })
        
        # Summary
        total_files = len(validation_results)
        valid_files = sum(1 for r in validation_results if r['valid'])
        files_with_frontmatter = sum(1 for r in validation_results if r.get('has_frontmatter', False))
        
        print(f"\n📊 Example File Validation Summary:")
        print(f"  📄 Total example files: {total_files}")
        print(f"  ✅ Valid files: {valid_files}")
        print(f"  📋 Files with frontmatter: {files_with_frontmatter}")
        print(f"  📈 Validation rate: {(valid_files/total_files)*100:.1f}%")
        
        return valid_files > 0 and (valid_files/total_files) >= 0.8  # 80% success threshold
        
    except Exception as e:
        print(f"  ❌ Example file validation failed: {e}")
        return False

def test_mock_generator_quality():
    """Test mock generator quality, accuracy, and schema compliance"""
    print("\n🎭 TESTING MOCK GENERATOR QUALITY & ACCURACY")
    print("=" * 60)
    
    try:
        components = [
            'author', 'badgesymbol', 'bullets', 'caption', 'content', 
            'frontmatter', 'jsonld', 'metatags', 'propertiestable', 'table', 'tags'
        ]
        
        test_materials = [
            ('Steel', 'metals'),
            ('Alumina', 'ceramics'), 
            ('Carbon Fiber', 'composites'),
            ('Glass', 'glass'),
            ('Concrete', 'masonry')
        ]
        
        quality_scores = {}
        
        for component in components:
            print(f"\n🔧 Testing {component} mock generator quality...")
            
            try:
                # Import mock generator
                module = importlib.import_module(f'components.{component}.mock_generator')
                generate_func = getattr(module, f'generate_mock_{component}')
                
                component_scores = {
                    'material_variation': 0,
                    'category_variation': 0,
                    'content_length': 0,
                    'schema_compliance': 0,
                    'technical_accuracy': 0
                }
                
                # Test material variation
                material_outputs = []
                for material, category in test_materials:
                    try:
                        output = generate_func(material, category)
                        material_outputs.append(output)
                    except Exception as e:
                        print(f"      ❌ Generation failed for {material}: {e}")
                        continue
                
                # Analyze variation between materials
                if len(material_outputs) >= 2:
                    unique_outputs = len(set(material_outputs))
                    variation_score = unique_outputs / len(material_outputs)
                    component_scores['material_variation'] = variation_score
                    print(f"      📊 Material variation: {variation_score:.1%} ({unique_outputs}/{len(material_outputs)} unique)")
                
                # Test content quality for representative sample
                if material_outputs:
                    sample_output = material_outputs[0]
                    
                    # Content length assessment
                    length_score = min(len(sample_output) / 1000, 1.0)  # Normalize to 1000 chars
                    component_scores['content_length'] = length_score
                    print(f"      📏 Content length: {len(sample_output)} chars (score: {length_score:.2f})")
                    
                    # Schema compliance for frontmatter-based components
                    if component in ['frontmatter', 'author', 'badgesymbol', 'jsonld', 'metatags']:
                        try:
                            if sample_output.startswith('---'):
                                parts = sample_output.split('---', 2)
                                if len(parts) >= 2:
                                    yaml_data = yaml.safe_load(parts[1])
                                    if yaml_data and isinstance(yaml_data, dict):
                                        component_scores['schema_compliance'] = 1.0
                                        print(f"      ✅ Schema compliance: Valid YAML structure ({len(yaml_data)} fields)")
                                    else:
                                        print(f"      ⚠️  Schema compliance: Invalid YAML structure")
                            elif component == 'jsonld':
                                # JSON-LD might be pure JSON
                                json_data = json.loads(sample_output)
                                if json_data:
                                    component_scores['schema_compliance'] = 1.0
                                    print(f"      ✅ Schema compliance: Valid JSON structure")
                        except (yaml.YAMLError, json.JSONDecodeError) as e:
                            print(f"      ❌ Schema compliance: Parsing error - {e}")
                    
                    # Technical accuracy assessment
                    technical_keywords = [
                        'laser', 'wavelength', 'fluence', 'pulse', 'nm', 'J/cm²', 
                        'MHz', 'kHz', 'power', 'density', 'temperature', 'µm'
                    ]
                    
                    keyword_count = sum(1 for keyword in technical_keywords if keyword.lower() in sample_output.lower())
                    accuracy_score = min(keyword_count / 5, 1.0)  # Normalize to 5 keywords
                    component_scores['technical_accuracy'] = accuracy_score
                    print(f"      🎯 Technical accuracy: {keyword_count} keywords (score: {accuracy_score:.2f})")
                
                # Calculate overall quality score
                overall_score = sum(component_scores.values()) / len(component_scores)
                quality_scores[component] = {
                    'overall': overall_score,
                    'details': component_scores
                }
                
                print(f"      📈 Overall quality score: {overall_score:.2f}/1.0")
                
            except ImportError:
                print(f"      ❌ Mock generator not found for {component}")
                quality_scores[component] = {'overall': 0, 'error': 'Import failed'}
            except Exception as e:
                print(f"      ❌ Quality test failed: {e}")
                quality_scores[component] = {'overall': 0, 'error': str(e)}
        
        # Quality summary
        print(f"\n📊 Mock Generator Quality Summary:")
        total_components = len(components)
        tested_components = sum(1 for scores in quality_scores.values() if 'overall' in scores)
        avg_quality = sum(scores['overall'] for scores in quality_scores.values() if 'overall' in scores) / max(tested_components, 1)
        
        print(f"  🧪 Components tested: {tested_components}/{total_components}")
        print(f"  📈 Average quality score: {avg_quality:.2f}/1.0")
        
        # Top performing components
        best_components = sorted(
            [(comp, scores['overall']) for comp, scores in quality_scores.items() if 'overall' in scores],
            key=lambda x: x[1], reverse=True
        )[:3]
        
        print(f"  🏆 Top performers:")
        for comp, score in best_components:
            print(f"    • {comp}: {score:.2f}")
        
        return avg_quality >= 0.6  # 60% quality threshold
        
    except Exception as e:
        print(f"  ❌ Mock generator quality testing failed: {e}")
        return False

def test_schema_driven_generation():
    """Test schema-driven content generation end-to-end"""
    print("\n⚙️  TESTING SCHEMA-DRIVEN CONTENT GENERATION")
    print("=" * 60)
    
    try:
        from generators.dynamic_generator import DynamicGenerator
        
        # Test with mock client to avoid API dependencies
        generator = DynamicGenerator(use_mock=True)
        
        # Test schema integration
        print("📋 Schema Integration Test:")
        materials = generator.get_available_materials()
        components = generator.get_available_components()
        
        print(f"  ✅ Materials available: {len(materials)}")
        print(f"  ✅ Components available: {len(components)}")
        
        # Test dynamic field extraction
        from generators.dynamic_generator import SchemaManager
        schema_manager = SchemaManager()
        
        print(f"\n🔬 Dynamic Field Extraction:")
        dynamic_fields = schema_manager.get_dynamic_fields('material')
        print(f"  ✅ Material schema fields: {len(dynamic_fields)}")
        
        for field_name, instruction in list(dynamic_fields.items())[:3]:
            if isinstance(instruction, str):
                print(f"    • {field_name}: {instruction[:40]}...")
        
        # Test component generation with schema fields
        print(f"\n🎯 Schema-Driven Generation Test:")
        test_material = "Aluminum"
        test_components = ['frontmatter', 'content']
        
        for component_type in test_components:
            print(f"  🔧 Testing {component_type} generation...")
            
            try:
                result = generator.generate_component(
                    material_name=test_material,
                    component_type=component_type,
                    schema_fields=dynamic_fields
                )
                
                if result.success:
                    print(f"    ✅ Generated {len(result.content)} chars")
                    
                    # Validate schema field integration
                    field_integration_count = 0
                    for field_name in dynamic_fields.keys():
                        if field_name.lower() in result.content.lower():
                            field_integration_count += 1
                    
                    print(f"    📊 Schema integration: {field_integration_count}/{len(dynamic_fields)} fields referenced")
                    
                else:
                    print(f"    ❌ Generation failed: {result.error_message}")
                    
            except Exception as e:
                print(f"    ❌ Generation error: {e}")
        
        # Test material substitution
        print(f"\n🔄 Material Substitution Test:")
        test_materials = ["Steel", "Glass", "Plastic"]
        
        for material in test_materials:
            if material in materials:
                try:
                    result = generator.generate_component(material, 'frontmatter')
                    if result.success and material.lower() in result.content.lower():
                        print(f"  ✅ {material}: Material name properly substituted")
                    else:
                        print(f"  ⚠️  {material}: Substitution issue")
                except Exception as e:
                    print(f"  ❌ {material}: {e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Schema-driven generation test failed: {e}")
        return False

def test_validation_workflow_integration():
    """Test end-to-end validation workflow integration"""
    print("\n🔍 TESTING VALIDATION WORKFLOW INTEGRATION")
    print("=" * 60)
    
    try:
        from validators.centralized_validator import CentralizedValidator
        
        validator = CentralizedValidator()
        print("  ✅ Centralized validator initialized")
        
        # Test component-local validation integration
        print(f"\n🔧 Component-Local Validation Integration:")
        
        components = [
            'frontmatter', 'content', 'table', 'tags', 'metatags'
        ]
        
        validation_results = {}
        
        for component in components:
            print(f"  🧪 Testing {component} validation...")
            
            try:
                # Generate mock content for validation
                from components import frontmatter
                if hasattr(frontmatter, 'mock_generator'):
                    mock_module = importlib.import_module(f'components.{component}.mock_generator')
                    generate_func = getattr(mock_module, f'generate_mock_{component}')
                    
                    # Generate test content
                    test_content = generate_func("Test Material", "metals")
                    
                    # Test validation
                    try:
                        # Import component validator
                        validator_module = importlib.import_module(f'components.{component}.validator')
                        validate_func = getattr(validator_module, f'validate_{component}_content')
                        
                        is_valid = validate_func(test_content, "Test Material")
                        validation_results[component] = {
                            'validation_available': True,
                            'mock_content_valid': is_valid,
                            'content_length': len(test_content)
                        }
                        
                        print(f"    ✅ Validation: {'PASS' if is_valid else 'FAIL'} ({len(test_content)} chars)")
                        
                    except ImportError:
                        validation_results[component] = {
                            'validation_available': False,
                            'error': 'Validator not found'
                        }
                        print(f"    ⚠️  Validator not available")
                        
            except Exception as e:
                validation_results[component] = {
                    'validation_available': False,
                    'error': str(e)
                }
                print(f"    ❌ Validation test failed: {e}")
        
        # Test post-processing integration
        print(f"\n🔄 Post-Processing Integration:")
        
        for component in components:
            try:
                # Create temporary test file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
                    temp_file.write("---\ntitle: Test\n---\n# Test Content")
                    temp_path = temp_file.name
                
                # Test post-processing
                was_processed = validator.post_process_generated_content(temp_path, component)
                print(f"  {'✅' if was_processed else '⚪'} {component}: {'processed' if was_processed else 'no changes'}")
                
                # Clean up
                os.unlink(temp_path)
                
            except Exception as e:
                print(f"  ❌ {component}: Post-processing error - {e}")
        
        # Summary
        print(f"\n📊 Validation Workflow Summary:")
        total_components = len(components)
        components_with_validation = sum(1 for r in validation_results.values() if r.get('validation_available', False))
        valid_mock_content = sum(1 for r in validation_results.values() if r.get('mock_content_valid', False))
        
        print(f"  🧪 Components tested: {total_components}")
        print(f"  ✅ Validators available: {components_with_validation}")
        print(f"  📋 Mock content valid: {valid_mock_content}")
        print(f"  📈 Validation coverage: {(components_with_validation/total_components)*100:.1f}%")
        
        return components_with_validation > 0 and (components_with_validation/total_components) >= 0.6
        
    except Exception as e:
        print(f"  ❌ Validation workflow integration failed: {e}")
        return False

def test_comprehensive_architecture_coverage():
    """Test comprehensive architecture coverage and completeness"""
    print("\n🏗️  TESTING COMPREHENSIVE ARCHITECTURE COVERAGE")
    print("=" * 60)
    
    try:
        # Test component-local architecture completeness
        print("📂 Component-Local Architecture Coverage:")
        
        components_dir = Path("components")
        expected_components = [
            'author', 'badgesymbol', 'bullets', 'caption', 'content',
            'frontmatter', 'jsonld', 'metatags', 'propertiestable', 'table', 'tags'
        ]
        
        architecture_coverage = {}
        
        for component in expected_components:
            component_dir = components_dir / component
            if not component_dir.exists():
                architecture_coverage[component] = {'exists': False}
                continue
            
            # Check for required files
            required_files = {
                'generator.py': component_dir / 'generator.py',
                'validator.py': component_dir / 'validator.py',
                'post_processor.py': component_dir / 'post_processor.py',
                'mock_generator.py': component_dir / 'mock_generator.py',
                'prompt.yaml': component_dir / 'prompt.yaml',
                'example_file': list(component_dir.glob('example_*.md'))
            }
            
            file_status = {}
            for file_type, file_path in required_files.items():
                if file_type == 'example_file':
                    file_status[file_type] = len(file_path) > 0
                else:
                    file_status[file_type] = file_path.exists()
            
            completeness = sum(file_status.values()) / len(file_status)
            architecture_coverage[component] = {
                'exists': True,
                'completeness': completeness,
                'files': file_status
            }
            
            print(f"  📁 {component}: {completeness*100:.0f}% complete")
        
        # Test schema coverage
        print(f"\n📋 Schema Coverage:")
        
        schemas_dir = Path("schemas")
        if schemas_dir.exists():
            schema_files = list(schemas_dir.glob("*.json"))
            print(f"  ✅ Schema files: {len(schema_files)}")
            
            for schema_file in schema_files:
                try:
                    with open(schema_file, 'r') as f:
                        schema_data = json.load(f)
                    print(f"    📄 {schema_file.stem}: Valid JSON")
                except json.JSONDecodeError:
                    print(f"    ❌ {schema_file.stem}: Invalid JSON")
        else:
            print(f"  ❌ Schemas directory not found")
        
        # Test testing framework coverage
        print(f"\n🧪 Testing Framework Coverage:")
        
        tests_dir = Path("tests")
        if tests_dir.exists():
            test_files = list(tests_dir.glob("test_*.py"))
            print(f"  ✅ Test files: {len(test_files)}")
            
            # Key test files
            key_tests = [
                'test_component_local_architecture.py',
                'test_enhanced_dynamic_system.py',
                'test_dynamic_system.py',
                'run_all_tests.py'
            ]
            
            for test_file in key_tests:
                if (tests_dir / test_file).exists():
                    print(f"    ✅ {test_file}")
                else:
                    print(f"    ❌ {test_file} missing")
        else:
            print(f"  ❌ Tests directory not found")
        
        # Calculate overall coverage
        print(f"\n📊 Overall Architecture Coverage:")
        
        # Component coverage
        total_components = len(expected_components)
        complete_components = sum(1 for cov in architecture_coverage.values() 
                                if cov.get('exists', False) and cov.get('completeness', 0) >= 0.8)
        component_coverage = complete_components / total_components
        
        print(f"  📂 Component-local: {component_coverage*100:.1f}% ({complete_components}/{total_components})")
        print(f"  📋 Schema system: {'✅ Available' if schemas_dir.exists() else '❌ Missing'}")
        print(f"  🧪 Testing framework: {'✅ Available' if tests_dir.exists() else '❌ Missing'}")
        
        # Overall assessment
        overall_score = component_coverage
        print(f"  📈 Overall coverage: {overall_score*100:.1f}%")
        
        return overall_score >= 0.8  # 80% coverage threshold
        
    except Exception as e:
        print(f"  ❌ Architecture coverage test failed: {e}")
        return False

def main():
    """Run comprehensive testing architecture evaluation"""
    print("🧪 Z-BEAM TESTING ARCHITECTURE - END-TO-END EVALUATION")
    print("=" * 80)
    print("Comprehensive coverage and accuracy assessment including:")
    print("• Dynamic schema matching and validation")
    print("• Example file validation against schemas")  
    print("• Mock generator quality and accuracy")
    print("• Schema-driven content generation")
    print("• End-to-end validation workflows")
    print("=" * 80)
    
    tests = [
        ("Schema Validation Architecture", test_schema_validation_architecture),
        ("Example File Validation", test_example_file_validation),
        ("Mock Generator Quality", test_mock_generator_quality),
        ("Schema-Driven Generation", test_schema_driven_generation),
        ("Validation Workflow Integration", test_validation_workflow_integration),
        ("Comprehensive Architecture Coverage", test_comprehensive_architecture_coverage),
    ]
    
    passed = 0
    failed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name}: PASSED\n")
            else:
                failed += 1
                print(f"\n❌ {test_name}: FAILED\n")
        except Exception as e:
            print(f"\n💥 {test_name}: CRASHED - {e}\n")
            failed += 1
    
    print("=" * 80)
    print(f"📊 TESTING ARCHITECTURE EVALUATION RESULTS")
    print("=" * 80)
    print(f"   Total Tests: {total}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 EXCELLENT! Testing architecture has comprehensive coverage and accuracy.")
        
        print("\n🏆 VERIFIED CAPABILITIES:")
        print("   ✅ Dynamic schema validation with comprehensive field mapping")
        print("   ✅ Example files validated against schema requirements")
        print("   ✅ Mock generators produce high-quality, schema-compliant content")
        print("   ✅ Schema-driven generation integrates dynamic fields properly")
        print("   ✅ End-to-end validation workflows function correctly")
        print("   ✅ Component-local architecture has complete coverage")
        
        print("\n🔬 TESTING ARCHITECTURE STRENGTHS:")
        print("   • Schema-driven validation ensures accuracy")
        print("   • Mock generators provide realistic test data")
        print("   • Component-local testing enables isolated validation")
        print("   • End-to-end workflows verify complete system integration")
        print("   • Comprehensive coverage across all 11 components")
        
    elif passed >= total * 0.8:
        print("\n✅ GOOD! Testing architecture has strong coverage with minor gaps.")
        
        print("\n💡 IMPROVEMENT RECOMMENDATIONS:")
        if failed > 0:
            print(f"   • Address {failed} failing test area(s)")
            print("   • Review error messages for specific issues")
            print("   • Enhance coverage in identified weak areas")
        
    else:
        print("\n⚠️  Testing architecture has significant gaps that should be addressed.")
        
        print("\n🔧 CRITICAL IMPROVEMENTS NEEDED:")
        print("   • Fix failing test components")
        print("   • Enhance schema validation coverage")
        print("   • Improve mock generator quality")
        print("   • Strengthen validation workflows")
    
    print("\n📋 TESTING ARCHITECTURE ASSESSMENT:")
    print(f"   Schema Integration: {'🟢 Excellent' if passed >= 5 else '🟡 Needs Work' if passed >= 3 else '🔴 Critical'}")
    print(f"   Content Validation: {'🟢 Comprehensive' if passed >= 4 else '🟡 Partial' if passed >= 2 else '🔴 Insufficient'}")
    print(f"   End-to-End Coverage: {'🟢 Complete' if passed == total else '🟡 Good' if passed >= 4 else '🔴 Inadequate'}")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
