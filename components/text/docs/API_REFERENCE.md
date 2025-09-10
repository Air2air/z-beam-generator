# Text Component API Reference

## Quick Start

```python
from components.text.generator import TextComponentGenerator

# Create generator instance
generator = TextComponentGenerator()

# Generate content
result = generator.generate(
    material_name="alabaster",
    material_data=material_data,
    api_client=api_client,
    author_info={'id': 2},  # Italy author
    frontmatter_data=frontmatter_data
)

if result.success:
    print(result.content)
else:
    print(f"Error: {result.error_message}")
```

## API Documentation

### TextComponentGenerator

#### Constructor
```python
TextComponentGenerator()
```
Creates a new text generator instance. No parameters required.

#### generate() Method
```python
def generate(self, material_name: str, material_data: Dict,
            api_client=None, author_info: Optional[Dict] = None,
            frontmatter_data: Optional[Dict] = None,
            schema_fields: Optional[Dict] = None) -> ComponentResult:
```

**Parameters:**
- `material_name` (str): Name of the material (e.g., "alabaster")
- `material_data` (Dict): Complete material data including formula and properties
- `api_client`: API client instance (required, no fallbacks)
- `author_info` (Optional[Dict]): Author information with 'id' field
- `frontmatter_data` (Optional[Dict]): Enhanced frontmatter from previous generation
- `schema_fields` (Optional[Dict]): Dynamic schema fields for customization

**Returns:**
- `ComponentResult`: Result object with content, success status, and metadata

**Raises:**
- `GenerationError`: When required parameters missing or invalid
- `ConfigurationError`: When configuration files missing or corrupt

### FailFastContentGenerator

#### Constructor
```python
def create_fail_fast_generator(max_retries: int = 3, retry_delay: float = 1.0,
                             enable_scoring: bool = True, human_threshold: float = 75.0) -> FailFastContentGenerator:
```

**Parameters:**
- `max_retries` (int): Maximum retry attempts for retryable errors (default: 3)
- `retry_delay` (float): Delay between retries in seconds (default: 1.0)
- `enable_scoring` (bool): Enable quality scoring system (default: True)
- `human_threshold` (float): Minimum human believability score (default: 75.0)

**Returns:**
- `FailFastContentGenerator`: Configured generator instance

#### generate() Method
```python
def generate(self, material_name: str, material_data: Dict,
            api_client=None, author_info: Optional[Dict] = None,
            frontmatter_data: Optional[Dict] = None,
            schema_fields: Optional[Dict] = None) -> GenerationResult:
```

Same parameters as ContentComponentGenerator, but returns `GenerationResult` with additional quality scoring data.

## Data Structures

### ComponentResult
```python
@dataclass
class ComponentResult:
    component_type: str     # Always "text"
    content: str           # Generated markdown with frontmatter
    success: bool          # True if generation succeeded
    error_message: Optional[str] = None  # Error details if failed
```

### GenerationResult
```python
class GenerationResult:
    success: bool          # Generation success status
    content: str          # Generated content
    error_message: str    # Error details if failed
    metadata: Dict        # Generation metadata
    quality_score: Any    # Quality scoring data (if enabled)
```

### Author Information
```python
author_info = {
    'id': int,           # Required: 1=Taiwan, 2=Italy, 3=Indonesia, 4=USA
    'name': str,         # Optional: Will be loaded from authors.json
    'country': str,      # Optional: Will be loaded from authors.json
    'expertise': str     # Optional: Will be loaded from authors.json
}
```

### Material Data Structure
```python
material_data = {
    'name': str,                    # Required: Material name
    'data': {
        'formula': str,             # Required: Chemical formula
        'author_id': int,           # Optional: Default author
        'category': str,            # Optional: Material category
        'properties': Dict,         # Optional: Physical properties
        # ... additional material properties
    },
    'article_type': str,            # Optional: For schema field selection
    # ... additional fields
}
```

### Frontmatter Data Structure
```python
frontmatter_data = {
    'chemicalProperties': {
        'formula': str,             # Chemical formula
        'symbol': str,              # Material symbol
        'materialType': str,        # Type classification
    },
    'properties': {
        'density': str,             # Density value with units
        'thermalConductivity': str, # Thermal conductivity
        'meltingPoint': str,        # Melting point
        # ... additional properties
    },
    'category': str,                # Material category
    'technicalSpecifications': {
        'tensileStrength': str,     # Tensile strength
        # ... additional specs
    },
    # ... additional frontmatter fields
}
```

## Configuration Files

### Base Content Prompt
**File:** `components/text/prompts/base_content_prompt.yaml`

**Required Sections:**
- `overall_subject`: Primary content guidance questions
- `author_expertise_areas`: Author specializations and word limits
- `author_configurations`: Detailed author settings
- `application_focus`: Country-specific applications
- `content_structure`: Required sections and guidelines

### Author Personas
**Files:** `components/text/prompts/personas/{country}_persona.yaml`

**Required Sections:**
- `author_id`: Numeric author identifier
- `name`: Author's full name
- `country`: Author's country
- `writing_style`: Writing approach and characteristics
- `language_patterns`: Signature phrases and linguistic nuances
- `technical_focus`: Expertise areas and specializations

### Formatting Configuration
**Files:** `components/text/prompts/formatting/{country}_formatting.yaml`

**Required Sections:**
- `markdown_formatting`: Markdown style preferences
  - `headers`: Header style preferences
  - `emphasis`: Bold/italic usage patterns
  - `lists`: List style preferences

## Error Handling

### Exception Types

#### ConfigurationError
**When Raised:**
- Missing configuration files
- Invalid YAML syntax
- Missing required configuration sections
- Author not found in authors.json

**Example:**
```python
try:
    result = generator.generate(material_name, material_data, api_client)
except ConfigurationError as e:
    print(f"Configuration issue: {e}")
    # Fix configuration files before retrying
```

#### GenerationError
**When Raised:**
- Missing API client
- Invalid author information
- Insufficient material data
- Non-retryable generation failures

**Example:**
```python
try:
    result = generator.generate(material_name, material_data, None)  # No API client
except GenerationError as e:
    print(f"Generation failed: {e}")
    # Provide required dependencies
```

#### RetryableError
**When Raised:**
- API timeout or connection issues
- Word count violations >20%
- Quality score below threshold
- Temporary API failures

**Handling:**
- Automatically retried up to `max_retries` times
- Uses exponential backoff with `retry_delay`
- Converts to GenerationError after max retries exceeded

## Quality Scoring

### Enabling Quality Scoring
```python
# Enable with default settings
generator = create_fail_fast_generator(enable_scoring=True, human_threshold=75.0)

# Disable for faster generation
generator = create_fail_fast_generator(enable_scoring=False)
```

### Quality Metrics
```python
quality_score = {
    'overall_score': float,        # 0-100 overall quality
    'human_believability': float,  # 0-100 believability score
    'technical_accuracy': float,   # 0-100 technical correctness
    'author_authenticity': float,  # 0-100 author voice authenticity
    'readability_score': float,    # 0-100 readability
    'passes_human_threshold': bool, # Meets minimum threshold
    'retry_recommended': bool,     # Should content be regenerated
    'word_count': int,            # Actual word count
}
```

### Quality Thresholds
- **Human Believability:** Default minimum 75.0
- **Retry Trigger:** Score below threshold triggers automatic retry
- **Word Count:** Enforced per author (250-450 words)

## Best Practices

### 1. API Client Management
```python
# Always provide real API client
from api.client import APIClient
api_client = APIClient(api_key="your-key")

# Never use None or mocks in production
result = generator.generate(material_name, material_data, api_client)
```

### 2. Error Handling
```python
try:
    result = generator.generate(material_name, material_data, api_client, author_info)
    if result.success:
        return result.content
    else:
        logger.error(f"Generation failed: {result.error_message}")
        return None
except (ConfigurationError, GenerationError) as e:
    logger.error(f"Content generation error: {e}")
    raise
```

### 3. Author Selection
```python
# Use specific authors for different materials
author_map = {
    'semiconductor': {'id': 1},  # Taiwan - semiconductor expertise
    'heritage': {'id': 2},       # Italy - heritage preservation
    'marine': {'id': 3},         # Indonesia - marine applications
    'biomedical': {'id': 4},     # USA - biomedical applications
}

author_info = author_map.get(material_category, {'id': 1})  # Default to Taiwan
```

### 4. Performance Optimization
```python
# Cache generator instances
content_generator = ContentComponentGenerator()

# Reuse for multiple materials
for material in materials:
    result = content_generator.generate(material['name'], material, api_client)
    # Process result...
```

### 5. Quality Monitoring
```python
# Enable scoring for production monitoring
generator = create_fail_fast_generator(
    enable_scoring=True,
    human_threshold=80.0,  # Higher threshold for production
    max_retries=2         # Limit retries for performance
)

# Log quality metrics
if result.quality_score:
    logger.info(f"Quality: {result.quality_score.overall_score:.1f}/100")
```

## Integration Examples

### With DynamicGenerator
```python
from generators.dynamic_generator import DynamicGenerator

generator = DynamicGenerator(api_client=api_client)
result = generator.generate_component('alabaster', 'content')
```

### With ComponentGeneratorFactory
```python
from generators.component_generators import ComponentGeneratorFactory

text_gen = ComponentGeneratorFactory.create_generator('text')
result = text_gen.generate(material_name, material_data, api_client)
```

### Custom Quality Scoring
```python
# Create generator with custom scoring settings
generator = create_fail_fast_generator(
    enable_scoring=True,
    human_threshold=85.0,      # Higher standard
    max_retries=1,             # Faster failure
    retry_delay=0.5            # Quicker retries
)
```

## Troubleshooting

### Common Issues

#### "API client is required"
**Cause:** No API client provided to generate() method
**Solution:** Always provide a real API client instance

#### "Author configuration not found"
**Cause:** Invalid author_id or missing authors.json
**Solution:** Use valid author IDs (1-4) and ensure authors.json exists

#### "Base content prompt not found"
**Cause:** Missing base_content_prompt.yaml file
**Solution:** Ensure all configuration files are present and valid

#### "Content exceeds word limit"
**Cause:** Generated content too long for author
**Solution:** System automatically retries with stricter constraints

#### "Quality score below threshold"
**Cause:** Content quality insufficient
**Solution:** System automatically retries with refined prompts

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed logging
generator = create_fail_fast_generator(enable_scoring=True)
result = generator.generate(material_name, material_data, api_client)
```

### Configuration Validation
```python
# Validate configurations before generation
try:
    generator = create_fail_fast_generator()
    print("✅ All configurations valid")
except ConfigurationError as e:
    print(f"❌ Configuration error: {e}")
```
