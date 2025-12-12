# Component Configuration Reference

**📚 Complete component configuration and parameter reference**  
**🎯 Scope**: All component parameters, configurations, and options  
**🛠️ Format**: Reference guide for developers and users  

---

## 📋 Component Configuration Overview

### Configuration Sources

1. **Material Data**: `data/Materials.yaml` - Material properties and metadata
2. **Component Configs**: Individual component configuration files
3. **API Configuration**: `api/config.py` - API client settings
4. **Runtime Parameters**: Command-line arguments and environment variables

### Configuration Hierarchy

```
Runtime Parameters (highest priority)
├── Command-line arguments
├── Environment variables
└── Configuration files
    ├── Component-specific configs
    ├── API configuration
    └── Material data (lowest priority)
```

---

## 🧩 Component-Specific Configurations

### Frontmatter Component

#### Configuration File: `components/frontmatter/config.yaml`

```yaml
frontmatter:
  # Content structure settings
  include_properties: true
  include_author: true
  include_categories: true
  include_keywords: true
  
  # YAML formatting
  indent_size: 2
  quote_strings: false
  preserve_quotes: true
  
  # Content limits
  max_title_length: 100
  max_description_length: 300
  max_keywords: 10
  
  # Author selection
  author_pool_size: 4
  author_selection_method: "random_weighted"
  expertise_matching: true
  
  # Property inclusion rules
  required_properties:
    - density
    - melting_point
    - thermal_conductivity
  optional_properties:
    - hardness
    - electrical_conductivity
    - corrosion_resistance
```

#### API Parameters

```python
class FrontmatterConfig:
    """Frontmatter component configuration."""
    
    # Prompt construction
    base_prompt_template: str = "frontmatter_base.txt"
    property_template: str = "frontmatter_properties.txt"
    author_template: str = "frontmatter_author.txt"
    
    # Content generation
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 0.9
    
    # Validation rules
    required_fields = ['title', 'material', 'author_object', 'properties']
    yaml_validation: bool = True
    author_validation: bool = True
```

#### Runtime Parameters

```bash
# Command-line overrides
python run.py aluminum --frontmatter-config custom_frontmatter.yaml
python run.py aluminum --frontmatter-author-pool 6
python run.py aluminum --frontmatter-temp 0.5
```

### Text Component

#### Configuration File: `components/text/config.yaml`

```yaml
text:
  # Content generation settings
  word_count_range:
    minimum: 250
    maximum: 450
    target: 350
  
  # Author personas
  personas:
    enabled: true
    use_frontmatter_author: true
    fallback_author: "Technical Writer"
  
  # Prompt system
  prompt_layers:
    - base_guidance
    - author_persona
    - formatting_rules
  
  # Quality control
  quality_scoring:
    enabled: true
    min_score: 0.7
    dimensions:
      - technical_accuracy
      - readability
      - human_believability
      - completeness
      - engagement
  
  # Optimization settings
  max_retries: 3
  retry_delay: 2
  optimization_rounds: 2
  
  # Content structure
  sections:
    introduction: true
    technical_details: true
    applications: true
    benefits: true
    conclusion: true
```

#### Author Persona Configuration

```yaml
```yaml
authors:
  1:
    name: "Dr. Yi-Chun Lin"
    country: "Taiwan"
    expertise: "Laser Materials Processing"
    style:
      tone: "technical_precise"
      vocabulary: "academic_systematic"
      structure: "methodical_analytical"
      cultural_markers:
        - "precision_focus"
        - "systematic_approach"
        - "measurement_emphasis"
  
  2:
    name: "Dr. Alessandro Moretti"
    country: "Italy"
    expertise: "Laser-Based Additive Manufacturing"
    style:
      tone: "expressive_technical"
      vocabulary: "technical_elegant"
      structure: "complex_sophisticated"
      cultural_markers:
        - "aesthetic_awareness"
        - "expressive_language"
        - "quality_emphasis"
  
  3:
    name: "Dr. Ikmanda Roswati"
    country: "Indonesia"
    expertise: "Ultrafast Laser Physics and Material Interactions"
    style:
      tone: "accessible_technical"
      vocabulary: "straightforward_practical"
      structure: "direct_clear"
      cultural_markers:
        - "accessibility_focus"
        - "practical_emphasis"
        - "clear_communication"
  
  4:
    name: "Todd Dunning"
    country: "United States (California)"
    expertise: "Optical Materials for Laser Systems"
    style:
      tone: "innovative_pragmatic"
      vocabulary: "technical_action_oriented"
      structure: "efficient_results_focused"
      cultural_markers:
        - "innovation_emphasis"
        - "practical_application"
        - "efficiency_focus"
```
  
  3:
    name: "Ikmanda Roswati"
    country: "Indonesia"
    expertise: "Ultrafast Laser Physics"
    style:
      tone: "warm_technical"
      vocabulary: "accessible_expert"
      structure: "engaging_practical"
      cultural_markers:
        - "community_focused"
        - "practical_applications"
        - "inclusive_expertise"
  
  4:
    name: "Dr. Priya Sharma"
    country: "India"
    expertise: "Surface Engineering"
    style:
      tone: "analytical_collaborative"
      vocabulary: "precise_inclusive"
      structure: "logical_comprehensive"
      cultural_markers:
        - "analytical_depth"
        - "collaborative_spirit"
        - "innovation_tradition"
```

#### API Parameters

```python
class TextConfig:
    """Text component configuration."""
    
    # Content generation
    temperature: float = 0.8
    max_tokens: int = 2000
    top_p: float = 0.95
    frequency_penalty: float = 0.1
    presence_penalty: float = 0.1
    
    # Prompt construction
    base_prompt_path: str = "prompts/text_base.txt"
    persona_prompt_path: str = "prompts/text_personas.txt"
    formatting_prompt_path: str = "prompts/text_formatting.txt"
    
    # Quality control
    min_quality_score: float = 0.7
    max_optimization_rounds: int = 3
    quality_weights = {
        'technical_accuracy': 0.25,
        'readability': 0.20,
        'human_believability': 0.25,
        'completeness': 0.15,
        'engagement': 0.15
    }
```

### Table Component

#### Configuration File: `components/table/config.yaml`

```yaml
table:
  # Table structure
  format: "yaml"
  include_units: true
  include_ranges: true
  include_comparisons: true
  
  # Property categories
  categories:
    physical:
      - density
      - melting_point
      - boiling_point
      - thermal_expansion
    thermal:
      - thermal_conductivity
      - specific_heat
      - thermal_diffusivity
    mechanical:
      - elastic_modulus
      - yield_strength
      - hardness
    electrical:
      - electrical_conductivity
      - resistivity
  
  # Value formatting
  decimal_places: 2
  scientific_notation: false
  unit_display: "abbreviated"
  
  # Calculations
  calculate_ranges: true
  range_percentage: 10  # ±10% for min/max
  include_comparisons: true
  comparison_materials:
    - aluminum
    - steel
    - copper
```

#### API Parameters

```python
class TableConfig:
    """Table component configuration."""
    
    # Content generation
    temperature: float = 0.3  # Lower for factual content
    max_tokens: int = 1500
    
    # Property handling
    required_properties: List[str] = [
        'density', 'melting_point', 'thermal_conductivity'
    ]
    optional_properties: List[str] = [
        'hardness', 'electrical_conductivity', 'elastic_modulus'
    ]
    
    # Formatting
    decimal_precision: int = 2
    unit_system: str = "metric"
    include_uncertainty: bool = True
```

### Author Component

#### Configuration File: `components/author/config.yaml`

```yaml
author:
  # Data source
  source: "frontmatter"  # Extract from frontmatter only
  fallback_enabled: false  # No fallbacks - fail-fast
  
  # Output format
  format: "yaml"
  include_metadata: true
  include_expertise: true
  include_publications: false  # Not generated by API
  
  # Validation
  required_fields:
    - id
    - name
    - expertise
  validate_expertise: true
  validate_name_format: true
```

#### Parameters

```python
class AuthorConfig:
    """Author component configuration."""
    
    # No API parameters - data-only component
    api_required: bool = False
    
    # Data extraction
    frontmatter_required: bool = True
    author_object_key: str = "author_object"
    
    # Validation rules
    required_fields = ['id', 'name', 'expertise']
    valid_expertise_domains = [
        'Precision Manufacturing',
        'Advanced Materials',
        'Ultrafast Laser Physics',
        'Surface Engineering'
    ]
```

### Meta Components (Metatags, JSON-LD, Tags)

#### Configuration File: `components/meta/config.yaml`

```yaml
meta:
  # SEO settings
  metatags:
    include_og_tags: true
    include_twitter_tags: true
    include_schema_tags: true
    max_description_length: 160
    max_title_length: 60
  
  # JSON-LD schema
  jsonld:
    schema_type: "Article"
    organization: "Z-Beam Technologies"
    publisher: "Laser Cleaning Systems"
    include_breadcrumbs: true
    include_faq: false
  
  # Tagging system
  tags:
    max_tags: 8
    min_tags: 3
    categories:
      - material_types
      - processes
      - applications
      - benefits
    tag_format: "lowercase_hyphenated"
```

### Bullets Component

#### Configuration File: `components/bullets/config.yaml`

```yaml
bullets:
  # Content structure
  bullet_count:
    minimum: 5
    maximum: 8
    target: 6
  
  # Categories
  categories:
    advantages: 2-3
    applications: 2-3
    technical_features: 1-2
  
  # Formatting
  format: "yaml_list"
  include_categories: true
  bullet_length:
    minimum: 10
    maximum: 50
    target: 30
```

### Micro Component

#### Configuration File: `components/micro/config.yaml`

```yaml
micro:
  # Micro types
  types:
    - process_image
    - equipment_image
    - before_after
    - microscopic
    - industrial_application
  
  # Content requirements
  length:
    minimum: 20
    maximum: 100
    target: 60
  
  # Style
  tone: "technical_descriptive"
  include_technical_details: true
  include_safety_info: true
```

---

## 🔧 API Configuration Reference

### API Client Configuration

#### File: `api/config.py`

```python
class APIConfig:
    """Central API configuration for all components."""
    
    # Provider settings
    primary_provider: str = "deepseek"
    fallback_provider: str = "grok"
    
    # Rate limiting
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    
    # Retry configuration
    max_retries: int = 3
    retry_delay: float = 1.0
    exponential_backoff: bool = True
    
    # Timeout settings
    request_timeout: float = 30.0
    connection_timeout: float = 10.0
    
    # Caching
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour
    cache_size: int = 1000
```

### Provider-Specific Configuration

#### DeepSeek Configuration

```python
class DeepSeekConfig:
    """DeepSeek API specific configuration."""
    
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    
    # Default parameters
    temperature: float = 0.7
    max_tokens: int = 4000
    top_p: float = 0.95
    
    # Headers
    user_agent: str = "Z-Beam-Generator/1.0"
    
    # Specific overrides per component
    component_overrides = {
        'frontmatter': {'temperature': 0.6, 'max_tokens': 1000},
        'text': {'temperature': 0.8, 'max_tokens': 2000},
        'table': {'temperature': 0.3, 'max_tokens': 1500},
        'bullets': {'temperature': 0.7, 'max_tokens': 800},
        'metatags': {'temperature': 0.5, 'max_tokens': 500},
        'jsonld': {'temperature': 0.4, 'max_tokens': 1000},
        'tags': {'temperature': 0.6, 'max_tokens': 300},
        'micro': {'temperature': 0.7, 'max_tokens': 400},
    }
```

#### Grok Configuration

```python
class GrokConfig:
    """Grok API specific configuration."""
    
    base_url: str = "https://api.x.ai"
    model: str = "grok-beta"
    
    # Default parameters
    temperature: float = 0.7
    max_tokens: int = 4000
    top_p: float = 0.9
    
    # Grok-specific parameters
    stream: bool = False
    stop_sequences: List[str] = ["</output>", "---END---"]
    
    # Component overrides
    component_overrides = {
        'frontmatter': {'temperature': 0.5, 'max_tokens': 1200},
        'text': {'temperature': 0.75, 'max_tokens': 2500},
        'table': {'temperature': 0.2, 'max_tokens': 1800},
        'bullets': {'temperature': 0.6, 'max_tokens': 1000},
        'metatags': {'temperature': 0.4, 'max_tokens': 600},
        'jsonld': {'temperature': 0.3, 'max_tokens': 1200},
        'tags': {'temperature': 0.5, 'max_tokens': 400},
        'micro': {'temperature': 0.65, 'max_tokens': 500},
    }
```

---

## 📊 Material Data Configuration

### Material Properties Schema

#### File: `data/Materials.yaml`

```yaml
materials:
  aluminum:
    # Basic properties
    name: "Aluminum"
    symbol: "Al"
    atomic_number: 13
    category: "metal"
    
    # Physical properties
    density: 2.70  # g/cm³
    melting_point: 660.3  # °C
    boiling_point: 2519  # °C
    
    # Thermal properties
    thermal_conductivity: 237  # W/m·K
    specific_heat: 0.897  # kJ/kg·K
    thermal_expansion: 23.1  # μm/m·K
    
    # Mechanical properties
    elastic_modulus: 70  # GPa
    yield_strength: 40  # MPa (pure aluminum)
    hardness: 25  # HB
    
    # Electrical properties
    electrical_conductivity: 3.5e7  # S/m
    resistivity: 2.82e-8  # Ω·m
    
    # Laser cleaning properties
    absorption_coefficient: 0.1  # for 1064nm
    damage_threshold: 0.5  # J/cm²
    optimal_fluence: 0.3  # J/cm²
    
    # Applications
    applications:
      - aerospace
      - automotive
      - construction
      - electronics
    
    # Industry categories
    industries:
      - manufacturing
      - transportation
      - construction
      - electronics
```

### Dynamic Property Calculation

```python
class MaterialPropertyCalculator:
    """Calculate derived properties and ranges."""
    
    def calculate_property_ranges(self, base_value: float, 
                                tolerance_percent: float = 10) -> dict:
        """Calculate min/max ranges for properties."""
        tolerance = base_value * (tolerance_percent / 100)
        return {
            'value': base_value,
            'min': round(base_value - tolerance, 2),
            'max': round(base_value + tolerance, 2),
            'tolerance': f"±{tolerance_percent}%"
        }
    
    def get_comparison_data(self, material_name: str, 
                          property_name: str) -> dict:
        """Get comparative data for property."""
        materials = ['aluminum', 'steel', 'copper', 'titanium']
        comparison = {}
        
        for material in materials:
            if material != material_name:
                value = self.get_material_property(material, property_name)
                comparison[material] = value
        
        return comparison
```

---

## 🎯 Runtime Configuration

### Command-Line Parameters

```bash
# Basic generation
python run.py <material> [--components <list>]

# Configuration overrides
python run.py aluminum --config custom_config.yaml
python run.py aluminum --frontmatter-temp 0.5
python run.py aluminum --text-word-count 400
python run.py aluminum --api-provider grok

# Batch processing
python run.py --batch materials.txt --components frontmatter,text,table
python run.py --all-materials --output-dir /custom/path

# Debug and validation
python run.py aluminum --debug --validate-only
python run.py aluminum --dry-run --show-prompts
```

### Environment Variables

```bash
# API configuration
export DEEPSEEK_API_KEY="your_deepseek_key"
export GROK_API_KEY="your_grok_key"
export Z_BEAM_DEFAULT_PROVIDER="deepseek"

# Paths
export Z_BEAM_CONFIG_DIR="/custom/config"
export Z_BEAM_OUTPUT_DIR="/custom/output"
export Z_BEAM_CACHE_DIR="/custom/cache"

# Behavior
export Z_BEAM_FAIL_FAST="true"
export Z_BEAM_CACHE_ENABLED="true"
export Z_BEAM_DEBUG_MODE="false"
```

### Configuration File Overrides

#### Custom Configuration: `custom_config.yaml`

```yaml
# Override default settings
api:
  primary_provider: "grok"
  fallback_provider: "deepseek"
  request_timeout: 45.0

components:
  text:
    word_count_range:
      target: 400
    temperature: 0.75
  
  frontmatter:
    max_keywords: 12
    author_selection_method: "expertise_weighted"
  
  table:
    decimal_places: 3
    include_uncertainty: true

output:
  directory: "/custom/output"
  format: "yaml"
  backup_enabled: true
```

---

## 🔍 Validation Configuration

### Input Validation Rules

```python
class ValidationConfig:
    """Configuration validation rules."""
    
    # Material validation
    valid_materials: List[str] = [
        'aluminum', 'steel', 'copper', 'titanium', 'brass', 'bronze'
    ]
    
    # Component validation
    valid_components: List[str] = [
        'frontmatter', 'text', 'table', 'author', 'bullets',
        'metatags', 'jsonld', 'tags', 'micro'
    ]
    
    # API validation
    valid_providers: List[str] = ['deepseek', 'grok']
    
    # Parameter ranges
    parameter_ranges = {
        'temperature': (0.0, 2.0),
        'max_tokens': (100, 8000),
        'top_p': (0.0, 1.0),
        'word_count': (100, 1000),
        'quality_score': (0.0, 1.0)
    }
    
    def validate_parameter(self, param_name: str, value: Any) -> bool:
        """Validate parameter value against defined ranges."""
        if param_name in self.parameter_ranges:
            min_val, max_val = self.parameter_ranges[param_name]
            return min_val <= value <= max_val
        return True
```

### Configuration Schema Validation

```python
# Configuration schema for validation
CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "api": {
            "type": "object",
            "properties": {
                "primary_provider": {"type": "string", "enum": ["deepseek", "grok"]},
                "temperature": {"type": "number", "minimum": 0, "maximum": 2},
                "max_tokens": {"type": "integer", "minimum": 100, "maximum": 8000}
            },
            "required": ["primary_provider"]
        },
        "components": {
            "type": "object",
            "patternProperties": {
                "^(frontmatter|text|table|author|bullets|metatags|jsonld|tags|micro)$": {
                    "type": "object"
                }
            }
        }
    },
    "required": ["api"]
}
```

---

## 📈 Performance Configuration

### Caching Configuration

```python
class CacheConfig:
    """Caching system configuration."""
    
    # Cache levels
    memory_cache_enabled: bool = True
    disk_cache_enabled: bool = True
    distributed_cache_enabled: bool = False
    
    # Cache sizing
    memory_cache_size: int = 1000  # Number of entries
    disk_cache_size: str = "1GB"   # Maximum disk usage
    
    # TTL settings
    api_response_ttl: int = 3600    # 1 hour
    material_data_ttl: int = 86400  # 24 hours
    config_cache_ttl: int = 1800    # 30 minutes
    
    # Cache keys
    cache_key_format: str = "{component}:{material}:{config_hash}"
    
    # Eviction policy
    eviction_policy: str = "LRU"  # Least Recently Used
```

### Batch Processing Configuration

```python
class BatchConfig:
    """Batch processing configuration."""
    
    # Concurrency
    max_concurrent_requests: int = 10
    max_concurrent_materials: int = 5
    
    # Throttling
    request_delay: float = 0.1  # Seconds between requests
    batch_delay: float = 1.0    # Seconds between batches
    
    # Error handling
    max_batch_errors: int = 5
    continue_on_error: bool = True
    error_threshold: float = 0.2  # 20% error rate threshold
    
    # Progress tracking
    progress_reporting: bool = True
    progress_interval: int = 10  # Report every 10 items
```

---

**📚 Configuration Reference**: Complete parameter and option documentation  
**🔧 Customization**: Override any setting via CLI, environment, or config files  
**✅ Validation**: All parameters validated against defined schemas and ranges
