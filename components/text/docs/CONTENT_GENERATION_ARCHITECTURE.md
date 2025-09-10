# Text Component Generation Architecture

## Overview

The text component is the core of the Z-Beam laser cleaning content generation system. It produces basic technical articles about laser cleaning for specific materials using a **hybrid data integration approach** that combines material properties from `data/materials.yaml` with template guidance from `components/text/prompts/base_content_prompt.yaml`.

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
4. Confirm materials.yaml and base_content_prompt.yaml exist and are valid
```

### Phase 2: Hybrid Data Loading
```
1. Load material data from materials.yaml → Material properties and metadata
2. Load base content prompt → Template structure and guidance
3. Resolve author information → Author details for context
4. Load frontmatter data → Consistency with other components
```

### Phase 3: Hybrid Prompt Construction
The system builds a comprehensive prompt by integrating multiple data sources:

#### Material Data Integration
```python
# Extract material properties
material_name = material_data.get('name', subject)
material_formula = material_data.get('formula')
material_category = material_data.get('category')
laser_params = material_data.get('laser_parameters', {})
```

#### Template Variable Substitution
```python
# Replace variables in base prompt
if 'overall_subject' in base_config:
    content = base_config['overall_subject'].format(material=material_name)
    prompt_parts.append(f"## Content Requirements\n{content}")
```

#### Context Integration
```python
# Include author and material context
sections.append(f"AUTHOR: {author_info.get('name')}")
sections.append(f"COUNTRY: {author_info.get('country', 'USA').title()}")
sections.append(f"MATERIAL: {material_name}")
sections.append(f"MATERIAL DATA: {json.dumps(material_data, indent=2)}")
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

### Hybrid Data Integration System

The text component uses a sophisticated hybrid approach that combines:

#### 1. Material Data Source (`data/materials.yaml`)
**Purpose:** Provides comprehensive material properties and metadata

**Key Properties:**
- `name`: Material name (e.g., "alabaster")
- `formula`: Chemical formula (e.g., "CaSO₄·2H₂O")
- `category`: Material category (e.g., "mineral")
- `laser_parameters`: Cleaning-specific parameters
- `author_id`: Links to author information

#### 2. Template System (`base_content_prompt.yaml`)
**Purpose:** Structured guidance with variable substitution

**Key Sections:**
- `overall_subject`: Core questions with {material} variable substitution

**Variable Replacement:**
```python
# Template variable substitution
subject = base_config['overall_subject'].format(material=material_name)
```

#### 3. Author Integration
**Purpose:** Provides author context and credibility

**Integration:**
```python
author_name = author_info.get('name')
author_country = author_info.get('country', 'USA').title()
```

#### 4. Frontmatter Context
**Purpose:** Maintains consistency with other components

**Usage:**
```python
if frontmatter_data:
    sections.append(f"CONTEXT: {json.dumps(frontmatter_data, indent=2)}")
```

### Complete Prompt Assembly

The final prompt combines all data sources:

```python
def _construct_prompt(self, base_prompt_data, material_name, material_data, author_info, frontmatter_data):
    sections = []
    
    # Author context
    sections.append(f"AUTHOR: {author_info.get('name')}")
    sections.append(f"COUNTRY: {author_info.get('country', 'USA').title()}")
    
    # Material integration
    sections.append(f"MATERIAL: {material_name}")
    sections.append(f"MATERIAL DATA: {json.dumps(material_data, indent=2)}")
    
    # Frontmatter context
    if frontmatter_data:
        sections.append(f"CONTEXT: {json.dumps(frontmatter_data, indent=2)}")
    
    # Template with variable substitution
    if "overall_subject" in base_prompt_data:
        subject = base_prompt_data["overall_subject"].format(material=material_name)
        sections.append(f"TASK:\nWrite about laser cleaning of {material_name}.\n\n{subject}")
    
    return "\n\n".join(sections)
```

### Base Content Prompt Example
```yaml
overall_subject: |
  A detailed technical analysis of the {material}, emphasizing its physicochemical properties, engineering applications, and the intricate mechanisms involved in laser cleaning processes...

  - What distinctive material properties influence the efficacy of laser cleaning?
  - What are the primary industrial applications of this {material}?
  - What technical challenges are encountered during laser cleaning?
  - What measurable indicators signify successful laser cleaning?
```

## Error Handling & Retry Logic

### Error Types

#### ConfigurationError (No Retry)
- Missing base_content_prompt.yaml
- Missing materials.yaml
- Invalid YAML syntax in configuration files
- Missing required configuration sections

#### GenerationError (No Retry)
- Missing API client
- Invalid author information
- Insufficient material data completeness
- Missing required material properties

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
