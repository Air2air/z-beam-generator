# Optimizer Testing Guide

## Testing Philosophy

Following the GROK_INSTRUCTIONS.md guidelines, this testing approach ensures:
- ✅ **Mocks and fallbacks ARE ALLOWED in test code** for proper testing
- 🚫 **ZERO tolerance for mocks/fallbacks in production code**
- 🔍 **Testing includes verification** that production code contains no mocks
- ⚡ **Fail-fast validation** while preserving runtime error recovery

## Test Categories

### 1. Unit Tests
**Purpose**: Test individual components in isolation using mocks where appropriate

```bash
# Run unit tests with mocks allowed
pytest optimizer/tests/unit/ -v --cov=optimizer
```

**Mock Usage Policy for Unit Tests**:
- ✅ Mock external API calls (Winston.ai, DeepSeek)
- ✅ Mock file system operations
- ✅ Mock database connections
- ✅ Use MockAPIClient for isolated testing
- ✅ Mock ComponentResult objects for iterative optimizer testing

#### Iterative Learning Optimizer Unit Tests
```python
def test_component_result_handling():
    """Test proper ComponentResult object handling"""
    from generators.component_generators import ComponentResult
    
    # Mock ComponentResult with success/content properties
    mock_result = ComponentResult(
        component_type="text",
        content="Generated content",
        success=True,
        error_message=None
    )
    
    # Test extraction logic matches new integration
    assert mock_result.success == True
    assert mock_result.content == "Generated content"
    assert not hasattr(mock_result, 'get')  # Ensure no dict methods

def test_enhancement_flag_learning():
    """Test enhancement flag prioritization"""
    learning_db = LearningDatabase()
    
    # Test strategic flags are applied for persona-heavy content
    config = learning_db.get_smart_config_for_material("copper", 0.0)
    
    # Verify persona intensity reduction is highest priority
    assert config['enhancement_flags'].get('reduce_persona_intensity') == True
    assert config['enhancement_flags'].get('professional_tone') == True
```

### 2. Integration Tests  
**Purpose**: Test component interactions with controlled scenarios

```bash
# Run integration tests
pytest optimizer/tests/integration/ -v
```

**Integration Test Guidelines**:
- ✅ Use test fixtures with known data
- ✅ Mock external services for predictable results
- ✅ Test error handling with simulated failures
- 🚫 Never use production API keys in automated tests

#### Content Flow Pipeline Integration Tests
```python
def test_iterative_content_generation_flow():
    """Test complete content generation and analysis pipeline"""
    # Mock text generator with ComponentResult
    mock_generator = Mock()
    mock_generator.generate.return_value = ComponentResult(
        component_type="text",
        content="Professional technical content without casual language",
        success=True
    )
    
    # Mock Winston.ai progression (0.0 -> improvement)
    mock_ai_responses = [
        MockAIResult(score=0.0, classification="ai"),
        MockAIResult(score=25.5, classification="unclear"),
        MockAIResult(score=67.8, classification="human")
    ]
    
    # Test iterative improvement
    result = run_optimization_iteration(material="copper", 
                                       generator=mock_generator,
                                       ai_responses=mock_ai_responses)
    
    assert result.improvement > 0
    assert result.final_score > result.initial_score

def test_learning_database_persistence():
    """Test learning database stores and retrieves enhancement strategies"""
    # Test that successful optimizations are recorded
    # Test that strategies are applied in subsequent runs
    # Test enhancement flag effectiveness tracking
```

### 3. Enhancement Flags Integration Tests
**Purpose**: Verify learned parameters flow to content generation

```python
def test_enhancement_flags_connectivity():
    """Test enhancement flags flow from learning database to text generator"""
    from optimizer.content_optimization.iterative_optimizer import LearningDatabase
    from components.text.ai_detection.prompt_chain import get_ai_detection_prompt
    
    # Test flags are loaded from database
    db = LearningDatabase()
    config = db.get_smart_config_for_material('copper', 14.14)
    assert len(config['enhancement_flags']) >= 5  # Default flags loaded
    assert 'reduce_persona_intensity' in config['enhancement_flags']
    
    # Test flags modify AI detection prompts
    prompt_without = get_ai_detection_prompt()
    prompt_with = get_ai_detection_prompt(config['enhancement_flags'])
    assert len(prompt_with) > len(prompt_without)  # Enhancement applied
    assert 'ENABLED ENHANCEMENTS' in prompt_with  # Flags included in prompt
    
def test_text_generator_accepts_enhancement_flags():
    """Test text generator accepts and processes enhancement flags"""
    # Test generator.generate() accepts enhancement_flags parameter
    # Test fail_fast_generator.generate() accepts enhancement_flags parameter
    # Test enhancement flags are passed to AI detection prompt chain
```

### 4. Production Code Validation Tests
**Purpose**: Verify ZERO presence of mocks/fallbacks in production code

```bash
# Verify no production mocks
python optimizer/tests/production_validation/verify_no_mocks.py
```

**Validation Checks**:
- Static analysis to detect mock usage in non-test files
- Search for forbidden patterns like `or "default"`, `except: pass`
- Verify no MockAPIClient imports in production modules
- Check for placeholder return values

### 4. Learning System Tests
**Purpose**: Test iterative optimizer learning capabilities

```bash
# Test learning database functionality
pytest optimizer/tests/learning/ -v
```

**Learning Test Coverage**:
- ✅ Database persistence and recovery
- ✅ Material-specific strategy adaptation
- ✅ Enhancement flag effectiveness tracking
- ✅ Historical data analysis accuracy

## Test Structure

```
optimizer/tests/
├── unit/                          # Isolated component tests
│   ├── test_iterative_optimizer.py   # Learning optimizer tests
│   ├── test_content_analyzer.py      # Content analysis tests
│   └── test_ai_detection.py          # AI detection tests
├── integration/                   # Component interaction tests
│   ├── test_optimization_flow.py     # End-to-end optimization
│   └── test_learning_integration.py  # Learning system integration
├── production_validation/         # Production code validation
│   ├── verify_no_mocks.py           # Mock detection script
│   └── test_fail_fast_behavior.py   # Fail-fast validation
└── learning/                      # Learning system tests
    ├── test_learning_database.py     # Database operations
    └── test_adaptive_config.py       # Configuration adaptation
```

## Mock Usage Examples (Test Code Only)

### ✅ Acceptable Test Mocks

```python
# test_iterative_optimizer.py
import pytest
from unittest.mock import Mock, patch
from optimizer.content_optimization.iterative_optimizer import optimize

@pytest.fixture
def mock_winston_api():
    """Mock Winston.ai for predictable test results"""
    mock = Mock()
    mock.analyze_text.return_value = Mock(
        score=75.5,
        classification="human",
        confidence=0.85
    )
    return mock

@patch('optimizer.ai_detection.service.initialize_ai_detection_service')
def test_optimization_with_mock_api(mock_service, mock_winston_api):
    """Test optimization logic with mocked API responses"""
    mock_service.return_value = mock_winston_api
    
    # Test the optimization logic without real API calls
    results = await optimize("text")
    assert results["materials_processed"] > 0
```

### ✅ Acceptable Test Fixtures

```python
# test_learning_database.py
@pytest.fixture
def temp_learning_db():
    """Temporary learning database for testing"""
    import tempfile
    import json
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            "created_at": "2025-09-14T10:00:00",
            "total_runs": 0,
            "materials": {},
            "successful_strategies": {},
            "best_practices": {}
        }, f)
        yield f.name
    
    # Cleanup
    import os
    os.unlink(f.name)
```

## Production Code Validation

### Static Analysis Script

```python
# optimizer/tests/production_validation/verify_no_mocks.py
"""
Verify that production code contains no mocks or fallbacks.
This script enforces the GROK_INSTRUCTIONS zero tolerance policy.
"""

import ast
import os
from pathlib import Path

FORBIDDEN_PATTERNS = [
    'MockAPIClient',
    'mock.Mock',
    'unittest.mock',
    'or "default"',
    'except: pass',
    'return True  # Skip',
    'return {}  # Empty fallback'
]

PRODUCTION_PATHS = [
    'optimizer/content_optimization/',
    'optimizer/ai_detection/',
    'optimizer/text_optimization/',
    'optimizer/services/'
]

def check_file_for_mocks(file_path):
    """Check a Python file for forbidden mock patterns"""
    violations = []
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in content:
                violations.append(f"Found forbidden pattern '{pattern}' in {file_path}")
                
    except Exception as e:
        violations.append(f"Error reading {file_path}: {e}")
    
    return violations

def main():
    """Main validation function"""
    all_violations = []
    
    for prod_path in PRODUCTION_PATHS:
        if os.path.exists(prod_path):
            for py_file in Path(prod_path).rglob("*.py"):
                if not str(py_file).endswith('test_'):  # Skip test files
                    violations = check_file_for_mocks(py_file)
                    all_violations.extend(violations)
    
    if all_violations:
        print("🚫 PRODUCTION CODE VALIDATION FAILED")
        print("Found mocks/fallbacks in production code:")
        for violation in all_violations:
            print(f"  ❌ {violation}")
        return 1
    else:
        print("✅ PRODUCTION CODE VALIDATION PASSED")
        print("No mocks or fallbacks found in production code")
        return 0

if __name__ == "__main__":
    exit(main())
```

## Fail-Fast Behavior Tests

```python
# optimizer/tests/production_validation/test_fail_fast_behavior.py
"""
Test that production code fails fast on configuration issues
while preserving runtime error recovery mechanisms.
"""

import pytest
from optimizer.content_optimization.iterative_optimizer import optimize

def test_fail_fast_on_missing_api_keys():
    """Verify system fails fast when API keys are missing"""
    import os
    
    # Temporarily remove API keys
    original_key = os.environ.get('WINSTON_API_KEY')
    if original_key:
        del os.environ['WINSTON_API_KEY']
    
    try:
        # Should fail fast on initialization
        with pytest.raises(Exception) as exc_info:
            await optimize("text")
        
        # Verify it's a configuration error, not silent failure
        assert "api" in str(exc_info.value).lower() or "key" in str(exc_info.value).lower()
        
    finally:
        # Restore API key
        if original_key:
            os.environ['WINSTON_API_KEY'] = original_key

def test_fail_fast_on_invalid_config():
    """Verify system fails fast on invalid configuration"""
    # Test with invalid material data
    with pytest.raises(Exception):
        # Should fail immediately, not return default values
        await optimize("nonexistent_component")

def test_preserves_runtime_error_recovery():
    """Verify that runtime error recovery is preserved"""
    # This test would verify that API retries and error recovery
    # mechanisms are still in place for transient failures
    pass  # Implementation depends on specific retry mechanisms
```

## Test Execution Commands

### Full Test Suite
```bash
# Run all tests including production validation
python -m pytest optimizer/tests/ -v --cov=optimizer

# Verify production code has no mocks
python optimizer/tests/production_validation/verify_no_mocks.py

# Test fail-fast behavior
python -m pytest optimizer/tests/production_validation/test_fail_fast_behavior.py -v
```

### Specific Test Categories
```bash
# Unit tests only (mocks allowed)
python -m pytest optimizer/tests/unit/ -v

# Integration tests only
python -m pytest optimizer/tests/integration/ -v

# Learning system tests
python -m pytest optimizer/tests/learning/ -v

# Production validation only
python -m pytest optimizer/tests/production_validation/ -v
```

### Continuous Integration
```bash
# CI pipeline command that enforces all requirements
python -m pytest optimizer/tests/ -v --cov=optimizer --cov-fail-under=80 && \
python optimizer/tests/production_validation/verify_no_mocks.py
```

## Test Data Management

### Test Fixtures
- ✅ Use temporary files for database tests
- ✅ Create isolated test environments
- ✅ Clean up test data after execution
- 🚫 Never modify production data during tests

### Mock Data
- ✅ Create realistic mock responses for API testing
- ✅ Use consistent test data across test suites
- ✅ Include edge cases and error conditions
- 🚫 Never use production API responses in version control

## Compliance Verification

### Before Each Release
1. ✅ Run full test suite with coverage
2. ✅ Verify no mocks in production code
3. ✅ Test fail-fast behavior on configuration errors
4. ✅ Validate learning system persistence
5. ✅ Check integration with existing optimizer components

### Development Workflow
1. ✅ Write tests with appropriate mocks for isolation
2. ✅ Verify production code has no fallbacks
3. ✅ Test both success and failure scenarios
4. ✅ Validate learning database operations
5. ✅ Ensure backward compatibility with existing optimizers

This testing approach ensures robust, reliable optimization while strictly adhering to the GROK_INSTRUCTIONS principle of zero tolerance for production mocks while allowing appropriate test mocking for thorough validation.
