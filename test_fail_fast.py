#!/usr/bin/env python3
"""
Test Fail-Fast Content Generator
Validates fail-fast behavior and retry mechanisms.
"""

import sys
from pathlib import Path

# Add project root to path  
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from components.content.fail_fast_generator import (
    create_fail_fast_generator, 
    ConfigurationError, 
    GenerationError
)
from api.client import MockAPIClient

def test_configuration_validation():
    """Test that generator fails fast on missing configurations."""
    print("🔍 TESTING CONFIGURATION VALIDATION")
    print("-" * 40)
    
    # Test 1: Valid configuration (should succeed)
    print("1. Testing valid configuration...")
    try:
        generator = create_fail_fast_generator()
        print("   ✅ Generator created successfully with valid config")
    except ConfigurationError as e:
        print(f"   ❌ Configuration validation failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False
    
    # Test 2: Missing base prompt (simulate by temporarily renaming)
    print("\n2. Testing missing base prompt...")
    base_prompt_file = Path("components/content/prompts/base_content_prompt.yaml")
    backup_name = "base_content_prompt.yaml.backup"
    
    try:
        if base_prompt_file.exists():
            base_prompt_file.rename(backup_name)
        
        try:
            _ = create_fail_fast_generator()
            print("   ❌ Should have failed with missing base prompt")
            return False
        except ConfigurationError as e:
            print(f"   ✅ Correctly failed: {e}")
        
    finally:
        # Restore file
        if Path(backup_name).exists():
            Path(backup_name).rename(base_prompt_file)
    
    # Test 3: Invalid authors file (simulate by creating invalid JSON)
    print("\n3. Testing invalid authors configuration...")
    authors_file = Path("components/author/authors.json")
    backup_authors = None
    
    try:
        if authors_file.exists():
            with open(authors_file, 'r') as f:
                backup_authors = f.read()
            
            # Write invalid JSON
            with open(authors_file, 'w') as f:
                f.write("{ invalid json")
        
        try:
            _ = create_fail_fast_generator()
            print("   ❌ Should have failed with invalid authors file")
            return False
        except ConfigurationError as e:
            print(f"   ✅ Correctly failed: {e}")
    
    finally:
        # Restore file
        if backup_authors:
            with open(authors_file, 'w') as f:
                f.write(backup_authors)
    
    return True

def test_fail_fast_generation():
    """Test fail-fast behavior during content generation."""
    print("\n🚀 TESTING FAIL-FAST GENERATION")
    print("-" * 40)
    
    try:
        generator = create_fail_fast_generator(max_retries=2, retry_delay=0.1)
        mock_client = MockAPIClient()
        
        # Test 1: Missing API client (should fail fast)
        print("1. Testing missing API client...")
        try:
            result = generator.generate(
                material_name="Test Material",
                material_data={'name': 'Test', 'formula': 'Test'},
                api_client=None,  # Missing API client
                author_info={'id': 1, 'name': 'Test Author'}
            )
            print("   ❌ Should have failed without API client")
            return False
        except GenerationError as e:
            print(f"   ✅ Correctly failed fast: {e}")
        
        # Test 2: Invalid author info (should fail fast)
        print("\n2. Testing invalid author info...")
        try:
            result = generator.generate(
                material_name="Test Material",
                material_data={'name': 'Test', 'formula': 'Test'},
                api_client=mock_client,
                author_info={'name': 'Test Author'}  # Missing 'id' field
            )
            print("   ❌ Should have failed with invalid author info")
            return False
        except GenerationError as e:
            print(f"   ✅ Correctly failed fast: {e}")
        
        # Test 3: Non-existent author ID (should fail fast)
        print("\n3. Testing non-existent author ID...")
        try:
            result = generator.generate(
                material_name="Test Material",
                material_data={'name': 'Test', 'formula': 'Test'},
                api_client=mock_client,
                author_info={'id': 999, 'name': 'Non-existent Author'}  # Invalid ID
            )
            print("   ❌ Should have failed with non-existent author")
            return False
        except GenerationError as e:
            print(f"   ✅ Correctly failed fast: {e}")
        
        # Test 4: Valid generation (should succeed)
        print("\n4. Testing valid generation...")
        try:
            result = generator.generate(
                material_name="Stainless Steel 316L",
                material_data={'name': 'Stainless Steel 316L', 'formula': 'Fe-18Cr-10Ni-2Mo'},
                api_client=mock_client,
                author_info={'id': 1, 'name': 'Yi-Chun Lin', 'country': 'Taiwan'}
            )
            
            if result.success:
                print(f"   ✅ Generation successful: {len(result.content)} chars")
                print(f"   📊 Metadata: {result.metadata.get('generation_method', 'unknown')}")
            else:
                print(f"   ❌ Generation failed: {result.error_message}")
                return False
                
        except Exception as e:
            print(f"   ❌ Generation error: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        return False

class FailingAPIClient:
    """Mock API client that always fails for testing retry logic."""
    
    def __init__(self, fail_count: int = 2):
        self.fail_count = fail_count
        self.attempt_count = 0
    
    def generate(self, prompt: str):
        self.attempt_count += 1
        
        if self.attempt_count <= self.fail_count:
            # Simulate different types of failures
            if self.attempt_count == 1:
                raise Exception("Connection timeout")
            elif self.attempt_count == 2:
                raise Exception("API rate limit exceeded")
            else:
                raise Exception("Server error")
        
        # Success after failures
        return MockAPIClient().generate(prompt)

def test_retry_mechanism():
    """Test retry logic for retryable errors."""
    print("\n🔄 TESTING RETRY MECHANISM")
    print("-" * 40)
    
    try:
        generator = create_fail_fast_generator(max_retries=3, retry_delay=0.1)
        
        # Test 1: Retryable errors that eventually succeed
        print("1. Testing retryable errors with eventual success...")
        failing_client = FailingAPIClient(fail_count=2)  # Fail 2 times, then succeed
        
        try:
            result = generator.generate(
                material_name="Test Material",
                material_data={'name': 'Test', 'formula': 'Test'},
                api_client=failing_client,
                author_info={'id': 1, 'name': 'Yi-Chun Lin', 'country': 'Taiwan'}
            )
            
            if result.success:
                print(f"   ✅ Generation succeeded after {failing_client.attempt_count} attempts")
            else:
                print(f"   ❌ Generation failed: {result.error_message}")
                return False
                
        except Exception as e:
            print(f"   ❌ Retry test failed: {e}")
            return False
        
        # Test 2: Too many failures (should exhaust retries)
        print("\n2. Testing retry exhaustion...")
        failing_client = FailingAPIClient(fail_count=5)  # Always fail
        
        try:
            result = generator.generate(
                material_name="Test Material",
                material_data={'name': 'Test', 'formula': 'Test'},
                api_client=failing_client,
                author_info={'id': 1, 'name': 'Yi-Chun Lin', 'country': 'Taiwan'}
            )
            print("   ❌ Should have failed after exhausting retries")
            return False
            
        except GenerationError as e:
            print(f"   ✅ Correctly exhausted retries: {e}")
            print(f"   📊 Attempted {failing_client.attempt_count} times")
        
        return True
        
    except Exception as e:
        print(f"❌ Retry test setup failed: {e}")
        return False

def test_no_fallbacks():
    """Test that no hardcoded fallbacks are used."""
    print("\n🚫 TESTING NO FALLBACKS")
    print("-" * 40)
    
    try:
        generator = create_fail_fast_generator()
        
        # Test: Empty API response (should not fallback to hardcoded content)
        class EmptyAPIClient:
            def generate(self, prompt: str):
                return ""  # Empty response
        
        print("1. Testing empty API response (no fallbacks)...")
        empty_client = EmptyAPIClient()
        
        try:
            _ = generator.generate(
                material_name="Test Material",
                material_data={'name': 'Test', 'formula': 'Test'},
                api_client=empty_client,
                author_info={'id': 1, 'name': 'Yi-Chun Lin', 'country': 'Taiwan'}
            )
            print("   ❌ Should have failed on empty response")
            return False
            
        except GenerationError as e:
            print(f"   ✅ Correctly failed without fallback: {e}")
        
        # Test: Malformed configuration (should not use hardcoded defaults)
        print("\n2. Testing malformed persona configuration...")
        persona_file = Path("components/content/prompts/personas/taiwan_persona.yaml")
        backup_content = None
        
        try:
            if persona_file.exists():
                with open(persona_file, 'r') as f:
                    backup_content = f.read()
                
                # Write malformed YAML
                with open(persona_file, 'w') as f:
                    f.write("malformed: yaml: content: [")
            
            # Clear cache to force reload
            generator._load_persona_prompt.cache_clear()
            
            try:
                _ = generator.generate(
                    material_name="Test Material",
                    material_data={'name': 'Test', 'formula': 'Test'},
                    api_client=MockAPIClient(),
                    author_info={'id': 1, 'name': 'Yi-Chun Lin', 'country': 'Taiwan'}
                )
                print("   ❌ Should have failed on malformed configuration")
                return False
                
            except (GenerationError, ConfigurationError) as e:
                print(f"   ✅ Correctly failed without fallback: {e}")
        
        finally:
            # Restore file
            if backup_content:
                with open(persona_file, 'w') as f:
                    f.write(backup_content)
            generator._load_persona_prompt.cache_clear()
        
        return True
        
    except Exception as e:
        print(f"❌ No fallbacks test failed: {e}")
        return False

def main():
    """Run comprehensive fail-fast tests."""
    print("🚫 FAIL-FAST CONTENT GENERATOR TESTS")
    print("="*60)
    print("Goal: No hardcoded fallbacks, clean error handling, retry logic")
    print("Approach: Fail fast on configuration errors, retry on API errors")
    
    tests = [
        ("Configuration Validation", test_configuration_validation),
        ("Fail-Fast Generation", test_fail_fast_generation),
        ("Retry Mechanism", test_retry_mechanism),
        ("No Fallbacks", test_no_fallbacks),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("-"*30)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Fail-fast approach implemented successfully")
        print("✅ No hardcoded fallbacks detected")
        print("✅ Retry mechanism working correctly")
        print("✅ Configuration validation robust")
    else:
        print(f"\n⚠️  {len(results) - passed} tests failed")
        print("❌ Some issues need to be addressed")

if __name__ == "__main__":
    main()
