# Text Component Generation Architecture

## Overview

The text component is the core of the Z-Beam laser cleaning content generation system. It produces basic technical articles about laser cleaning for specific materials using a simple prompt system and strict fail-fast architecture.

## System Architecture

### Core Components

#### A. TextComponentGenerator (Wrapper)
**File:** `components/text/generator.py`

- **Purpose:** Lightweight wrapper for ComponentGeneratorFactory integration
- **Role:** Bridges the component factory system with the fail_fast_generator
- **Features:**
  - Strict fail-fast validation (no API client = immediate failure)
  - No fallbacks or mocks allowed
  - Returns standardized ComponentResult objects

```python
class TextComponentGenerator:
    def generate(self, material_name: str, material_data: Dict, 
                api_client=None, author_info: Optional[Dict] = None,
                frontmatter_data: Optional[Dict] = None,
                schema_fields: Optional[Dict] = None) -> ComponentResult:
```

#### B. FailFastContentGenerator (Core Engine)
**File:** `components/text/generators/fail_fast_generator.py`

- **Purpose:** Main content generation engine with simple prompting
- **Size:** Streamlined for basic generation
- **Key Features:**
  - Simple prompt construction using base content only
  - Comprehensive error handling with retry logic
  - Basic content validation and formatting

## Generation Process Flow

### Phase 1: Validation
```
1. Validate API client exists (fail-fast if missing)
2. Validate author information provided
3. Validate material data completeness
4. Confirm base_content_prompt.yaml exists and is valid
```

### Phase 2: Configuration Loading
```
1. Load base content prompt → Primary guidance
2. Validate configuration structure
```

### Phase 3: Simple Prompt Construction
The system builds a basic prompt using only the base content guidance:

#### Base Content Integration
```yaml
overall_subject: |
  A detailed technical analysis of the {material}, emphasizing its physicochemical properties, engineering applications, and the intricate mechanisms involved in laser cleaning processes.
```

#### Simple Prompt Building
```python
prompt_parts = []
if 'overall_subject' in base_config:
    content = base_config['overall_subject'].format(material=subject)
    prompt_parts.append(f"## Content Requirements\n{content}")

prompt_parts.append(f"""
## Content Generation Task

Write a comprehensive article about laser cleaning {subject}.

**Subject:** {subject}
**Target Audience:** Industry professionals and researchers interested in laser cleaning applications

Focus on technical accuracy, practical applications, and engineering insights.
""")
```

### Phase 4: API Generation & Validation
```
1. Call API with constructed prompt
2. Validate response length and quality
3. Basic content validation
4. Return formatted result
```

### Phase 5: Basic Post-Processing
```
1. Apply simple formatting
2. Generate basic metadata
3. Return structured ComponentResult
```

## Prompt System Details

### Base Content Prompt (`base_content_prompt.yaml`)
**Purpose:** Primary guidance for all content generation

**Key Sections:**
- `overall_subject`: Core questions that guide content focus

**Example:**
```yaml
overall_subject: |
  A detailed technical analysis of the {material}, emphasizing its physicochemical properties, engineering applications, and the intricate mechanisms involved in laser cleaning processes. This content aims to equip engineers, researchers, and materials scientists with in-depth insights into the material's role in high-performance systems, potential degradation modes, and how optimized laser cleaning parameters can mitigate surface contaminants while preserving structural integrity and extending service life.

  - What distinctive material properties influence the efficacy of laser cleaning?
  - What are the primary industrial applications of this {material}?
  - What technical challenges are encountered during laser cleaning?
  - What measurable indicators signify successful laser cleaning?
```

## Error Handling & Retry Logic

### Error Types

#### ConfigurationError (No Retry)
- Missing base_content_prompt.yaml
- Invalid YAML syntax
- Missing required configuration sections

#### GenerationError (No Retry)
- Missing API client
- Invalid author information
- Insufficient material data

#### RetryableError (Retry Enabled)
- API timeout or connection issues
- Temporary API failures

### Retry Strategy
```python
max_retries: int = 3        # Default retry attempts
retry_delay: float = 1.0    # Delay between retries
```

**Retry Logic:**
1. Exponential backoff for API errors
2. Maximum retry limits to prevent infinite loops

## Integration Points

### ComponentGeneratorFactory Integration
```python
# Factory discovery
ComponentGeneratorFactory.create_generator("text")

# Returns TextComponentGenerator instance
# Integrates with broader component system
```

### Basic Generation Flow
```python
# Simple generation without optimization
generator = TextComponentGenerator()
result = generator.generate(material_name, material_data, api_client)
```

## Output Format

### ComponentResult Structure
```python
@dataclass
class ComponentResult:
    component_type: str = "text"
    content: str           # Generated markdown
    success: bool          # Generation success status
    error_message: Optional[str] = None  # Error details if failed
```

### Generated Content Structure
```markdown
# Laser Cleaning of Alabaster: Technical Analysis

[Generated content based on base prompt guidance...]
```

## CLAUDE_INSTRUCTIONS.md Compliance

### Fail-Fast Principles ✅
- **No Mocks:** System fails immediately if API client missing
- **No Fallbacks:** All dependencies must be explicitly provided
- **Explicit Dependencies:** Base content prompt required and validated
- **Immediate Validation:** Configuration checked on startup

### Error Handling ✅
- **Specific Exceptions:** ConfigurationError, GenerationError, RetryableError
- **No Silent Failures:** All errors logged and propagated
- **No Default Values:** Critical dependencies must be provided

## Performance Considerations

### Resource Management
- **File I/O:** Minimal file operations
- **API Calls:** Single API call per generation
- **Memory Usage:** Efficient prompt building

## Future Enhancements

### Planned Features
1. **Enhanced Error Handling:** Improved error reporting and recovery
2. **Performance Optimization:** Faster generation cycles
3. **Configuration Validation:** Enhanced startup checks

This architecture provides a solid foundation for basic content generation while maintaining strict adherence to fail-fast principles and clean error handling.

**Note:** For advanced optimization features including AI detection, persona management, and quality enhancement, see the optimizer documentation at `optimizer/text_optimization/docs/`.
