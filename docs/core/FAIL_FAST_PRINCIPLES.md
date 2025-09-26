# Fail-Fast Design Principles

**📋 Core design philosophy and architectural constraints for Z-Beam Generator**  
**🎯 Philosophy**: Explicit failure over silent degradation  
**🏗️ Architecture**: No mocks, no fallbacks, no defaults for critical dependencies  

---

## 🏛️ Fundamental Principles

### Principle 1: Explicit Dependencies, No Hidden Fallbacks

**Rule**: All required components must be explicitly provided or the system fails immediately.

```python
# ✅ CORRECT: Explicit dependency requirement
def generate_content(material_data, api_client, frontmatter_data):
    if not api_client:
        raise ConfigurationError("API client is required - no fallbacks available")
    if not frontmatter_data:
        raise ConfigurationError("Frontmatter data is required - fail-fast architecture")
    
    return api_client.generate(material_data, frontmatter_data)

# ❌ WRONG: Silent fallback to defaults
def generate_content(material_data, api_client=None, frontmatter_data=None):
    if not api_client:
        api_client = MockAPIClient()  # Silent fallback
    if not frontmatter_data:
        frontmatter_data = {}  # Empty default
        
    return api_client.generate(material_data, frontmatter_data)
```

**Rationale**: Silent fallbacks mask configuration problems and lead to unexpected behavior in production.

### Principle 2: No Mock Objects in Production Code

**Rule**: Mock objects exist only in test suites, never in production code paths.

```python
# ✅ CORRECT: Real API clients only
class ContentGenerator:
    def __init__(self, api_client):
        if not isinstance(api_client, (DeepSeekClient, GrokClient)):
            raise ConfigurationError(f"Invalid API client type: {type(api_client)}")
        self.api_client = api_client

# ❌ WRONG: Mock allowed in production
class ContentGenerator:
    def __init__(self, api_client):
        # Accepts MockAPIClient in production
        self.api_client = api_client or MockAPIClient()
```

**Rationale**: Production systems should never run with mock dependencies that produce fake data.

### Principle 3: Configuration Validation at Startup

**Rule**: Validate all configuration and dependencies before processing any data.

```python
# ✅ CORRECT: Upfront validation
def initialize_system():
    # Validate API keys exist
    api_keys = load_api_keys()
    if not api_keys.get('deepseek'):
        raise ConfigurationError("DEEPSEEK_API_KEY required in .env file")
    
    # Test API connectivity
    client = create_api_client('deepseek', api_keys['deepseek'])
    if not test_connection(client):
        raise ConnectionError("DeepSeek API unreachable - check network and keys")
    
    # Validate material data
    materials = load_materials()
    if not materials:
        raise ConfigurationError("Materials database empty or corrupted")
    
    return SystemState(api_clients, materials)

# ❌ WRONG: Lazy validation during processing
def generate_content(material_name):
    try:
        api_key = os.getenv('DEEPSEEK_API_KEY', 'fallback-key')  # Silent default
        client = create_client(api_key)
        material = materials.get(material_name, {})  # Empty default
        return client.generate(material)
    except Exception:
        return "Error occurred"  # Swallows errors
```

**Rationale**: Early validation prevents cascade failures and provides clear error messages.

### Principle 4: Explicit Error Propagation

**Rule**: Errors should propagate with clear context, not be swallowed or masked.

```python
# ✅ CORRECT: Explicit error handling
def generate_component(component_type, material_data, dependencies):
    try:
        generator = ComponentGeneratorFactory.create_generator(component_type)
        if not generator:
            raise ComponentError(f"No generator found for component type: {component_type}")
        
        result = generator.generate(material_data, **dependencies)
        if not result.success:
            raise GenerationError(f"Component generation failed: {result.error_message}")
        
        return result
    except APIError as e:
        raise GenerationError(f"API failure during {component_type} generation: {e}")
    except Exception as e:
        raise SystemError(f"Unexpected error in {component_type} generation: {e}")

# ❌ WRONG: Error swallowing
def generate_component(component_type, material_data, dependencies):
    try:
        generator = ComponentGeneratorFactory.create_generator(component_type)
        result = generator.generate(material_data, **dependencies)
        return result
    except:
        return None  # Swallows all errors
```

**Rationale**: Clear error messages enable faster debugging and prevent silent failures.

---

## 🔧 Implementation Patterns

### API Client Management

#### Correct Implementation
```python
class APIClientManager:
    def __init__(self):
        self.clients = {}
        self._validate_configuration()
    
    def _validate_configuration(self):
        """Validate all API configuration at startup."""
        required_keys = ['DEEPSEEK_API_KEY', 'WINSTON_API_KEY']
        missing_keys = [key for key in required_keys if not os.getenv(key)]
        
        if missing_keys:
            raise ConfigurationError(
                f"Missing required API keys: {missing_keys}. "
                f"Add them to .env file or environment variables."
            )
    
    def get_client(self, provider_name):
        """Get API client with explicit error handling."""
        if provider_name not in self.clients:
            client = self._create_client(provider_name)
            if not self._test_client_connection(client):
                raise ConnectionError(
                    f"Cannot connect to {provider_name} API. "
                    f"Check network connectivity and API key validity."
                )
            self.clients[provider_name] = client
        
        return self.clients[provider_name]
    
    def _test_client_connection(self, client):
        """Test client connection with explicit timeout."""
        try:
            return client.test_connection(timeout=10)
        except Exception as e:
            logger.error(f"Client connection test failed: {e}")
            return False
```

### Component Generator Factory

#### Correct Implementation
```python
class ComponentGeneratorFactory:
    """Factory for creating component generators with strict validation."""
    
    _generators = {
        'frontmatter': FrontmatterGenerator,
        'text': TextGenerator,
        'table': TableGenerator,
        'author': AuthorGenerator,
        # ... other generators
    }
    
    @classmethod
    def create_generator(cls, component_type):
        """Create generator with explicit validation."""
        if component_type not in cls._generators:
            available_types = ', '.join(cls._generators.keys())
            raise ComponentError(
                f"No generator found for component type: '{component_type}'. "
                f"Available types: {available_types}"
            )
        
        generator_class = cls._generators[component_type]
        
        try:
            generator = generator_class()
            cls._validate_generator(generator)
            return generator
        except Exception as e:
            raise ComponentError(
                f"Failed to create {component_type} generator: {e}"
            )
    
    @classmethod
    def _validate_generator(cls, generator):
        """Validate generator implements required interface."""
        if not hasattr(generator, 'generate'):
            raise ComponentError(
                f"Generator {type(generator)} missing required 'generate' method"
            )
```

### Dependency Injection

#### Correct Implementation
```python
class TextGenerator:
    """Text generator with explicit dependency requirements."""
    
    def __init__(self, api_client=None):
        if api_client is None:
            raise ConfigurationError(
                "TextGenerator requires explicit API client - no fallbacks available"
            )
        
        if not self._validate_api_client(api_client):
            raise ConfigurationError(
                f"Invalid API client type: {type(api_client)}. "
                f"Expected: DeepSeekClient or GrokClient"
            )
        
        self.api_client = api_client
    
    def generate(self, material_name, material_data, frontmatter_data=None):
        """Generate text content with explicit validation."""
        if not material_name:
            raise ValidationError("Material name is required")
        
        if not material_data:
            raise ValidationError("Material data is required")
        
        if frontmatter_data is None:
            raise ValidationError(
                "Frontmatter data is required - fail-fast architecture requires "
                "frontmatter component to be generated first"
            )
        
        # Proceed with generation...
        return self._generate_content(material_name, material_data, frontmatter_data)
```

---

## ⚠️ Anti-Patterns to Avoid

### Anti-Pattern 1: Silent Defaults

```python
# ❌ BAD: Silent default that masks missing configuration
def load_materials(file_path=None):
    if file_path is None:
        file_path = "data/Materials.yaml"  # Silent default
    
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}  # Silent failure

# ✅ GOOD: Explicit requirement with clear error
def load_materials(file_path):
    if not file_path:
        raise ConfigurationError("Materials file path is required")
    
    if not os.path.exists(file_path):
        raise ConfigurationError(f"Materials file not found: {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            materials = yaml.safe_load(f)
            if not materials:
                raise ConfigurationError(f"Materials file is empty: {file_path}")
            return materials
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in materials file: {e}")
```

### Anti-Pattern 2: Exception Swallowing

```python
# ❌ BAD: Swallows exceptions and returns None
def generate_frontmatter(material_data):
    try:
        return api_client.generate_frontmatter(material_data)
    except:
        return None  # Loses error context

# ✅ GOOD: Explicit error handling with context
def generate_frontmatter(material_data):
    try:
        result = api_client.generate_frontmatter(material_data)
        if not result:
            raise GenerationError("API returned empty frontmatter content")
        return result
    except APIError as e:
        raise GenerationError(f"API failure during frontmatter generation: {e}")
    except Exception as e:
        raise SystemError(f"Unexpected error in frontmatter generation: {e}")
```

### Anti-Pattern 3: Fallback Chains

```python
# ❌ BAD: Complex fallback chain that masks real issues
def get_api_client():
    try:
        return DeepSeekClient()
    except:
        try:
            return GrokClient()
        except:
            try:
                return OpenAIClient()
            except:
                return MockClient()  # Never fail, but produces fake data

# ✅ GOOD: Explicit client selection with clear failures
def get_api_client(provider_name):
    if not provider_name:
        raise ConfigurationError("API provider name is required")
    
    if provider_name == 'deepseek':
        return DeepSeekClient()
    elif provider_name == 'grok':
        return GrokClient()
    else:
        available_providers = ['deepseek', 'grok']
        raise ConfigurationError(
            f"Unknown provider: {provider_name}. "
            f"Available: {available_providers}"
        )
```

---

## 🎯 Error Handling Strategy

### Error Types and Responses

#### Configuration Errors
```python
class ConfigurationError(Exception):
    """Missing or invalid configuration that prevents system startup."""
    pass

# Usage
if not api_key:
    raise ConfigurationError(
        "DEEPSEEK_API_KEY required in .env file. "
        "Copy .env.example to .env and add your API key."
    )
```

#### Validation Errors
```python
class ValidationError(Exception):
    """Invalid input data that cannot be processed."""
    pass

# Usage
if not material_name:
    raise ValidationError("Material name cannot be empty")
```

#### Generation Errors
```python
class GenerationError(Exception):
    """Content generation failure that should stop processing."""
    pass

# Usage
if api_response.status_code != 200:
    raise GenerationError(
        f"API call failed with status {api_response.status_code}: "
        f"{api_response.text}"
    )
```

#### System Errors
```python
class SystemError(Exception):
    """Unexpected system error that indicates a bug."""
    pass

# Usage
if result is None and no_error_occurred:
    raise SystemError("Unexpected None result from successful API call")
```

### Error Message Guidelines

#### Clear, Actionable Messages
```python
# ✅ GOOD: Clear cause and solution
raise ConfigurationError(
    "DEEPSEEK_API_KEY not found in environment. "
    "Add DEEPSEEK_API_KEY=your_key_here to .env file. "
    "Get API key from https://platform.deepseek.com"
)

# ❌ BAD: Vague error message
raise Exception("Configuration error")
```

#### Context-Rich Errors
```python
# ✅ GOOD: Includes context for debugging
raise GenerationError(
    f"Failed to generate {component_type} for material '{material_name}'. "
    f"API provider: {provider_name}. "
    f"Error: {api_error_message}"
)

# ❌ BAD: No context provided
raise Exception("Generation failed")
```

---

## 🔬 Testing Philosophy

### Test Real Dependencies

```python
# ✅ CORRECT: Test with real API clients (controlled environment)
def test_content_generation():
    # Use real API client with test API key
    api_client = DeepSeekClient(api_key=TEST_API_KEY)
    generator = TextGenerator(api_client)
    
    # Test with real data
    result = generator.generate("aluminum", test_material_data, test_frontmatter)
    
    # Verify real behavior
    assert result.success
    assert "aluminum" in result.content.lower()

# ❌ WRONG: Mock everything (masks integration issues)
def test_content_generation():
    mock_client = MockAPIClient()
    mock_client.generate.return_value = "fake content"
    
    generator = TextGenerator(mock_client)
    result = generator.generate("aluminum", {}, {})
    
    assert result == "fake content"  # Meaningless test
```

### Fail-Fast Test Validation

```python
# ✅ CORRECT: Test that system fails appropriately
def test_missing_api_key_fails_fast():
    with pytest.raises(ConfigurationError, match="DEEPSEEK_API_KEY required"):
        TextGenerator(api_client=None)

def test_invalid_material_fails_fast():
    generator = TextGenerator(api_client=test_client)
    with pytest.raises(ValidationError, match="Material name is required"):
        generator.generate("", {}, {})

# ✅ CORRECT: Test that dependencies are validated
def test_missing_frontmatter_fails_fast():
    generator = TextGenerator(api_client=test_client)
    with pytest.raises(ValidationError, match="Frontmatter data is required"):
        generator.generate("aluminum", test_material_data, frontmatter_data=None)
```

---

## 📋 Code Review Guidelines

### Must-Have Checks

#### 1. No Silent Defaults
```python
# ❌ REJECT: Silent default parameter
def generate(material_data, api_client=MockAPIClient()):
    pass

# ✅ APPROVE: Explicit requirement
def generate(material_data, api_client):
    if not api_client:
        raise ConfigurationError("API client is required")
```

#### 2. No Exception Swallowing
```python
# ❌ REJECT: Bare except clause
try:
    result = process_data()
except:
    return None

# ✅ APPROVE: Explicit exception handling
try:
    result = process_data()
except SpecificError as e:
    raise ProcessingError(f"Data processing failed: {e}")
```

#### 3. Clear Error Messages
```python
# ❌ REJECT: Vague error
raise Exception("Error")

# ✅ APPROVE: Actionable error message
raise ConfigurationError(
    "Missing required API key. Add PROVIDER_API_KEY to .env file."
)
```

#### 4. Validation Before Processing
```python
# ❌ REJECT: Processing without validation
def generate_content(material_name):
    return api_call(material_name)

# ✅ APPROVE: Upfront validation
def generate_content(material_name):
    if not material_name:
        raise ValidationError("Material name is required")
    if material_name not in valid_materials:
        raise ValidationError(f"Unknown material: {material_name}")
    
    return api_call(material_name)
```

---

## 🏗️ Architecture Benefits

### Predictable Behavior
- **No Surprises**: System behavior is explicit and predictable
- **Clear Failures**: Problems surface immediately with clear messages
- **Easy Debugging**: Error messages point directly to root causes

### Production Reliability
- **No Silent Degradation**: System fails fast rather than producing bad data
- **Clear Dependencies**: All requirements are explicit and validated
- **Maintainable**: No hidden fallbacks or magic defaults to maintain

### Development Velocity
- **Fast Feedback**: Configuration problems caught immediately
- **Clear Contracts**: Component interfaces are explicit and validated
- **Confident Refactoring**: Explicit dependencies make changes safer

---

## 📊 Metrics and Monitoring

### Fail-Fast Metrics

#### Error Classification
```python
# Track error types to identify configuration issues
error_metrics = {
    'configuration_errors': count_configuration_errors(),
    'validation_errors': count_validation_errors(),
    'api_errors': count_api_errors(),
    'system_errors': count_system_errors()
}
```

#### Time to Error
```python
# Measure how quickly system fails (should be < 5 seconds)
startup_time = measure_startup_validation_time()
assert startup_time < 5.0, "Fail-fast validation too slow"
```

#### Error Message Quality
```python
# Ensure error messages are actionable
def validate_error_message(error_msg):
    # Must contain specific error cause
    assert len(error_msg) > 20, "Error message too generic"
    
    # Should suggest solution or next step
    assert any(word in error_msg.lower() for word in 
               ['add', 'check', 'verify', 'ensure', 'install'])
```

---

**🎯 Fail-Fast Philosophy**: Explicit failure over silent degradation  
**🏗️ Architecture Benefit**: Predictable, maintainable, production-ready systems  
**🔍 Key Insight**: Fast, clear failures prevent cascade issues and accelerate debugging
