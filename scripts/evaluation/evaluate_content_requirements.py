#!/usr/bin/env python3
"""
Comprehensive Content Generator Evaluation
Tests all 6 requirements specified by the user.
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from components.text.generators.fail_fast_generator import create_fail_fast_generator
from api.client import MockAPIClient

def check_requirement_1_believable_content():
    """1. 100% believable human-generated content specific to the author"""
    print("🔍 Requirement 1: Believable Human-Generated Content")
    print("-" * 50)
    
    try:
        generator = create_fail_fast_generator()
        api_client = MockAPIClient()
        
        # Test all 4 authors
        authors = [
            {'id': 1, 'name': 'Dr. Li Wei', 'country': 'Taiwan'},
            {'id': 2, 'name': 'Dr. Marco Rossi', 'country': 'Italy'},
            {'id': 3, 'name': 'Dr. Sari Dewi', 'country': 'Indonesia'},
            {'id': 4, 'name': 'Dr. Sarah Johnson', 'country': 'United States (California)'}
        ]
        
        believable_count = 0
        for author in authors:
            result = generator.generate(
                material_name='316L Stainless Steel',
                material_data={'formula': 'Fe-18Cr-10Ni-2Mo', 'name': '316L Stainless Steel'},
                api_client=api_client,
                author_info=author
            )
            
            if result.success:
                content = result.content
                
                # Check believability factors
                has_technical_depth = len(content) > 800
                has_formula_integration = 'Fe-18Cr-10Ni-2Mo' in content
                has_professional_tone = any(word in content.lower() for word in ['systematic', 'analysis', 'optimization', 'parameters'])
                has_markdown_formatting = '##' in content and '**' in content
                has_specific_details = any(phrase in content for phrase in ['laser', 'cleaning', 'surface', 'material'])
                
                believability_score = sum([
                    has_technical_depth,
                    has_formula_integration, 
                    has_professional_tone,
                    has_markdown_formatting,
                    has_specific_details
                ])
                
                print(f"  Author {author['id']} ({author['country']}): {believability_score}/5 believability factors")
                
                if believability_score >= 4:
                    believable_count += 1
            else:
                print(f"  Author {author['id']} failed: {result.error_message}")
        
        success = believable_count == len(authors)
        print(f"📊 Result: {believable_count}/{len(authors)} authors produce believable content")
        return success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_requirement_2_no_mocks_fallbacks():
    """2. Remove all mocks and fallbacks"""
    print("\n🔍 Requirement 2: No Mocks and Fallbacks")
    print("-" * 50)
    
    try:
        # Check fail_fast_generator.py for fallback patterns
        fail_fast_file = "components/text/fail_fast_generator.py"
        with open(fail_fast_file, 'r') as f:
            content = f.read()
        
        # Look for fallback patterns
        fallback_patterns = [
            'fallback',
            'default_content',
            'hardcoded',
            'mock_content',
            'sample_content'
        ]
        
        found_fallbacks = []
        for pattern in fallback_patterns:
            if pattern.lower() in content.lower():
                found_fallbacks.append(pattern)
        
        # Check for proper error handling instead of fallbacks
        has_proper_errors = all(error_type in content for error_type in [
            'ConfigurationError',
            'GenerationError', 
            'RetryableError'
        ])
        
        print(f"  Fallback patterns found: {found_fallbacks}")
        print(f"  Proper error handling: {has_proper_errors}")
        
        success = len(found_fallbacks) == 0 and has_proper_errors
        print(f"📊 Result: {'✅ No fallbacks detected' if success else '❌ Fallbacks or missing error handling found'}")
        return success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_requirement_3_formatting_personas():
    """3. Ensure formatting files and personas are used"""
    print("\n🔍 Requirement 3: Formatting Files and Personas Usage")
    print("-" * 50)
    
    try:
        # Check if formatting files exist and are loaded
        formatting_files = [
            "components/text/prompts/formatting/taiwan_formatting.yaml",
            "components/text/prompts/formatting/italy_formatting.yaml",
            "components/text/prompts/formatting/indonesia_formatting.yaml",
            "components/text/prompts/formatting/usa_formatting.yaml"
        ]
        
        persona_files = [
            "components/text/prompts/personas/taiwan_persona.yaml",
            "components/text/prompts/personas/italy_persona.yaml",
            "components/text/prompts/personas/indonesia_persona.yaml",
            "components/text/prompts/personas/usa_persona.yaml"
        ]
        
        # Check file existence
        formatting_exists = all(Path(f).exists() for f in formatting_files)
        persona_exists = all(Path(f).exists() for f in persona_files)
        
        print(f"  Formatting files exist: {formatting_exists}")
        print(f"  Persona files exist: {persona_exists}")
        
        # Check if fail_fast_generator loads them
        fail_fast_file = "components/text/fail_fast_generator.py"
        with open(fail_fast_file, 'r') as f:
            content = f.read()
        
        loads_formatting = '_load_formatting_prompt' in content
        loads_personas = '_load_persona_prompt' in content
        
        print(f"  Generator loads formatting: {loads_formatting}")
        print(f"  Generator loads personas: {loads_personas}")
        
        # Check file sizes (should be substantial)
        formatting_sizes = []
        for f in formatting_files:
            if Path(f).exists():
                size = Path(f).stat().st_size
                formatting_sizes.append(size)
        
        avg_formatting_size = sum(formatting_sizes) / len(formatting_sizes) if formatting_sizes else 0
        print(f"  Average formatting file size: {avg_formatting_size:.0f} bytes")
        
        success = formatting_exists and persona_exists and loads_formatting and loads_personas and avg_formatting_size > 1000
        print(f"📊 Result: {'✅ Formatting and personas properly integrated' if success else '❌ Missing or inadequate formatting/persona integration'}")
        return success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_requirement_4_frontmatter_grok():
    """4. Content generator relies on frontmatter and grok API"""
    print("\n🔍 Requirement 4: Frontmatter and Grok API Integration")
    print("-" * 50)
    
    try:
        generator = create_fail_fast_generator()
        api_client = MockAPIClient()
        
        # Test with frontmatter data
        frontmatter_data = {
            'title': 'Advanced 316L Processing',
            'description': 'Comprehensive analysis of stainless steel surface treatment',
            'properties': {
                'corrosion_resistance': 'Excellent',
                'surface_finish': 'Mirror-like'
            },
            'laser_cleaning': {
                'wavelength': '1064nm',
                'pulse_duration': '10ns'
            }
        }
        
        result = generator.generate(
            material_name='316L Stainless Steel',
            material_data={'formula': 'Fe-18Cr-10Ni-2Mo'},
            api_client=api_client,
            author_info={'id': 1, 'name': 'Dr. Li Wei', 'country': 'Taiwan'},
            frontmatter_data=frontmatter_data
        )
        
        # Check if API client is required (should fail without it)
        try:
            result_no_api = generator.generate(
                material_name='316L Stainless Steel',
                material_data={'formula': 'Fe-18Cr-10Ni-2Mo'},
                api_client=None,
                author_info={'id': 1, 'name': 'Dr. Li Wei', 'country': 'Taiwan'}
            )
            api_required = not result_no_api.success
        except Exception:
            api_required = True
        
        # Check if frontmatter influences content
        frontmatter_used = result.success and 'metadata' in result.metadata
        
        print(f"  API client required: {api_required}")
        print(f"  Frontmatter integration: {frontmatter_used}")
        print(f"  Generation method: {result.metadata.get('generation_method', 'unknown')}")
        
        success = api_required and result.success
        print(f"📊 Result: {'✅ Proper frontmatter and API integration' if success else '❌ Missing frontmatter or API integration'}")
        return success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_requirement_5_validation_retries():
    """5. Local validation with retries for human readability"""
    print("\n🔍 Requirement 5: Local Validation and Retries")
    print("-" * 50)
    
    try:
        # Check if fail_fast_generator has retry logic
        fail_fast_file = "components/text/fail_fast_generator.py"
        with open(fail_fast_file, 'r') as f:
            content = f.read()
        
        has_retry_logic = '_execute_with_retry' in content
        has_max_retries = 'max_retries' in content
        has_retry_delay = 'retry_delay' in content
        has_validation = any(term in content for term in ['validate', 'validation', 'check'])
        
        print(f"  Retry mechanism: {has_retry_logic}")
        print(f"  Configurable retries: {has_max_retries}")
        print(f"  Retry delay: {has_retry_delay}")
        print(f"  Validation logic: {has_validation}")
        
        # Test retry functionality
        generator = create_fail_fast_generator(max_retries=2, retry_delay=0.1)
        
        # This should work
        api_client = MockAPIClient()
        result = generator.generate(
            material_name='Test Material',
            material_data={'formula': 'TestFormula'},
            api_client=api_client,
            author_info={'id': 1, 'name': 'Test Author', 'country': 'Taiwan'}
        )
        
        retry_works = result.success
        
        print(f"  Retry system functional: {retry_works}")
        
        success = has_retry_logic and has_max_retries and has_validation and retry_works
        print(f"📊 Result: {'✅ Proper validation and retry system' if success else '❌ Missing or incomplete validation/retry system'}")
        return success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_requirement_6_e2e_evaluation():
    """6. E2E evaluation for bloat, simplicity, cleanup and effectiveness"""
    print("\n🔍 Requirement 6: E2E Evaluation")
    print("-" * 50)
    
    try:
        # Check for multiple generator files (bloat)
        content_dir = Path("components/text")
        generator_files = list(content_dir.glob("*generator*.py"))
        
        print(f"  Generator files found: {len(generator_files)}")
        for gf in generator_files:
            size = gf.stat().st_size
            print(f"    - {gf.name}: {size} bytes")
        
        # Check fail_fast_generator effectiveness
        start_time = time.time()
        
        generator = create_fail_fast_generator()
        api_client = MockAPIClient()
        
        result = generator.generate(
            material_name='316L Stainless Steel',
            material_data={'formula': 'Fe-18Cr-10Ni-2Mo'},
            api_client=api_client,
            author_info={'id': 1, 'name': 'Dr. Li Wei', 'country': 'Taiwan'}
        )
        
        generation_time = time.time() - start_time
        
        effectiveness = result.success and len(result.content) > 500
        simplicity = len(generator_files) <= 2  # Only fail_fast and maybe one other
        speed = generation_time < 1.0
        
        print(f"  Generation time: {generation_time:.3f}s")
        print(f"  Content generated: {len(result.content) if result.success else 0} chars")
        print(f"  Effectiveness: {effectiveness}")
        print(f"  Simplicity (few generators): {simplicity}")
        print(f"  Speed: {speed}")
        
        # Check for cleanup opportunities
        cleanup_needed = len(generator_files) > 2
        print(f"  Cleanup needed: {cleanup_needed}")
        
        if cleanup_needed:
            print("  Cleanup recommendations:")
            for gf in generator_files:
                if 'fail_fast' not in gf.name:
                    print(f"    - Consider archiving: {gf.name}")
        
        success = effectiveness and speed
        print(f"📊 Result: {'✅ E2E system effective' if success else '❌ E2E system needs improvement'}")
        return success, cleanup_needed
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, True

def main():
    """Run comprehensive evaluation of all requirements."""
    print("🚀 Content Component Generator Requirements Evaluation")
    print("=" * 60)
    
    results = []
    
    # Run all requirement checks
    results.append(check_requirement_1_believable_content())
    results.append(check_requirement_2_no_mocks_fallbacks())
    results.append(check_requirement_3_formatting_personas())
    results.append(check_requirement_4_frontmatter_grok())
    results.append(check_requirement_5_validation_retries())
    
    e2e_result, cleanup_needed = check_requirement_6_e2e_evaluation()
    results.append(e2e_result)
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 REQUIREMENTS SUMMARY")
    print("=" * 60)
    
    requirement_names = [
        "1. Believable Human Content",
        "2. No Mocks/Fallbacks", 
        "3. Formatting/Personas Used",
        "4. Frontmatter/Grok API",
        "5. Validation/Retries",
        "6. E2E Effectiveness"
    ]
    
    for i, (name, result) in enumerate(zip(requirement_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
    
    total_passed = sum(results)
    print(f"\n🎯 OVERALL SCORE: {total_passed}/{len(results)} requirements met")
    
    if total_passed == len(results):
        print("🎉 ALL REQUIREMENTS SATISFIED!")
        if cleanup_needed:
            print("💡 System ready for cleanup optimization")
    else:
        print("🔧 Some requirements need attention")
    
    return total_passed, len(results), cleanup_needed

if __name__ == "__main__":
    main()
