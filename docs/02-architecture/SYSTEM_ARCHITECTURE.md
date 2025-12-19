# Z-Beam Generator System Architecture

> ⚠️ **UPDATE (Dec 19, 2025)**: Several referenced files have been removed:
> - `streamlined_generator.py` (replaced by `UniversalFrontmatterExporter`)
> - `trivial_exporter.py` (replaced by `UniversalFrontmatterExporter`)
> - `schema_validator.py` (use `shared.validation.SchemaValidator` directly)
>
> See `EXPORTERS_UPDATED_DEC19_2025.md` for current architecture.

**Version**: 2.0 (Post-Flattening)  
**Last Updated**: October 2, 2025  
**Status**: Production-Ready

## Table of Contents

1. [System Overview](#system-overview)
2. [Core Principles](#core-principles)
3. [Architecture Layers](#architecture-layers)
4. [Component System](#component-system)
5. [Data Flow](#data-flow)
6. [API Integration](#api-integration)
7. [Generation Pipeline](#generation-pipeline)
8. [Quality Assurance](#quality-assurance)
9. [Error Handling](#error-handling)
10. [Performance Characteristics](#performance-characteristics)

---

## System Overview

Z-Beam Generator is a **laser cleaning content generation system** built on a **strict fail-fast architecture** with **no mocks or fallbacks**. It generates comprehensive, high-quality content for laser cleaning applications across 121 materials in 9 categories.

### Key Characteristics

- **Fail-Fast Design**: System fails immediately if dependencies are missing
- **Component Architecture**: Modular generators with factory pattern
- **AI-Powered**: DeepSeek API for content, Winston AI for quality, Perplexity for research
- **Quality-First**: Multi-dimensional scoring with human believability thresholds
- **Data-Driven**: Flattened YAML structure for O(1) material lookups

### System Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                    Z-Beam Generator                          │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   CLI Entry  │  │   Pipeline   │  │  Components  │      │
│  │    run.py    │→ │ Integration  │→ │  Generators  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         ↓                  ↓                  ↓              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Data Layer (Materials.yaml)              │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         API Layer (DeepSeek, Winston, Perplexity)    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Principles

### 1. Fail-Fast Architecture

**Philosophy**: Fail immediately and explicitly rather than continue with degraded functionality.

```python
# ❌ BAD: Silent fallback
def get_api_client():
    try:
        return RealAPIClient()
    except:
        return MockAPIClient()  # Silent degradation

# ✅ GOOD: Explicit failure
def get_api_client():
    if not api_key_configured():
        raise ConfigurationError("API key not configured")
    return RealAPIClient()
```

**Benefits**:
- No silent failures or degraded content
- Clear error messages for debugging
- Prevents shipping incomplete/incorrect content

### 2. No Mocks or Fallbacks

**Rule**: Production code must never use mock APIs or fallback values.

**Exceptions**:
- `MockAPIClient` for testing only (in `tests/` directory)
- Must be explicitly enabled via test fixtures
- Never imported in production code paths

### 3. Explicit Dependencies

**Rule**: All required components must be explicitly provided.

```python
# ❌ BAD: Implicit default
def __init__(self, client=None):
    self.client = client or DefaultClient()

# ✅ GOOD: Explicit requirement
def __init__(self, client):
    if client is None:
        raise ValueError("Client is required")
    self.client = client
```

### 4. Component Modularity

**Pattern**: Each content type has its own generator with standard interface.

```python
class ComponentGenerator(ABC):
    @abstractmethod
    def generate(self, material_name: str) -> ComponentResult:
        """Generate component content for material."""
        pass
```

---

## Architecture Layers

### Layer 1: CLI Entry Point

**File**: `run.py`  
**Responsibility**: Command-line interface, argument parsing, orchestration

```
User Input → CLI Parser → Material Validation → Component Selection → Generation
```

**Key Functions**:
- Parse command-line arguments (`--material`, `--components`, `--all`)
- Validate material names against `Materials.yaml`
- Select which components to generate
- Orchestrate generation pipeline
- Handle errors and display results

### Layer 2: Pipeline Integration

**File**: `pipeline_integration.py`  
**Responsibility**: Validation, quality control, content improvement

```
Generated Content → Validation → Quality Scoring → Improvement → Final Content
```

**Key Functions**:
- `validate_and_improve_frontmatter()`: Validate frontmatter structure
- `validate_and_improve_text()`: Check text quality and length
- Quality scoring integration (Winston AI)
- Content improvement suggestions

**Validation Rules**:
- **Applications**: Minimum 2, simple strings "Industry: Description"
- **Micro**: CamelCase keys (beforeText, afterText), full structure
- **Tags**: 4-10 items, includes category + industries + processes
- **Properties**: Required fields present, valid values

### Layer 3: Component Generators

**Directory**: `components/[component]/`  
**Responsibility**: Generate specific content types

#### Component Types

1. **frontmatter**: YAML metadata (applications, properties, machine settings)
2. **text**: Long-form blog content with author personas
3. **author**: Author profiles and biographies
4. **micro**: Before/after image micros
5. **tags**: SEO and categorization tags
6. **categories**: Industry and application categories
7. **jsonld**: Structured data (JSON-LD)
8. **metatags**: HTML meta tags
9. **table**: Comparison tables
10. **badgesymbol**: Visual badges

#### Generator Pattern

```python
class ComponentGenerator:
    def __init__(self, client, config):
        self.client = client  # API client (required)
        self.config = config  # Configuration (required)
    
    def generate(self, material_name: str) -> ComponentResult:
        # 1. Load material data
        material = get_material_by_name(material_name)
        
        # 2. Generate content via API
        content = self._generate_content(material)
        
        # 3. Validate and score
        score = self._score_quality(content)
        
        # 4. Return result
        return ComponentResult(
            success=True,
            content=content,
            quality_score=score
        )
```

### Layer 4: Data Layer

**Files**: `data/Materials.yaml`, `data/materials.py`  
**Responsibility**: Material data storage and access

#### Flattened Structure (v2.0)

```yaml
materials:
  Aluminum:
    category: metal
    properties:
      hardness: 2.75
      density: 2.70
      # ... more properties
    
  Copper:
    category: metal
    properties:
      # ...
```

**Access Pattern**:
```python
# O(1) direct lookup
material = materials['Aluminum']

# Category embedded
category = material['category']  # 'metal'
```

**Benefits**:
- Simple O(1) lookups (no nested traversal)
- Easier AI navigation (flat namespace)
- Reduced code complexity (129 lines removed from materials.py)

### Layer 5: API Integration

**Directory**: `api/`  
**Responsibility**: External API communication

#### API Clients

1. **DeepSeek API** (`api/deepseek.py`)
   - Purpose: Content generation
   - Usage: Text, applications, descriptions
   - Performance: ~3 minutes per material
   - Error Handling: Retry on transient failures

2. **Winston AI** (`api/winston.py`)
   - Purpose: Quality scoring
   - Usage: Human believability assessment
   - Threshold: Score ≥ 70 for publication

3. **Perplexity API** (`api/perplexity.py`)
   - Purpose: Research and factual queries
   - Usage: Technical details, industry research

#### Client Management

```python
# Factory pattern for client creation
client = ClientFactory.create(
    provider='deepseek',
    api_key=api_key,
    config=config
)

# Caching for performance
@lru_cache(maxsize=128)
def get_cached_client(provider: str):
    return ClientFactory.create(provider)
```

---

## Component System

### Component Discovery

**File**: `components/frontmatter/core/component_generator_factory.py`

```python
class ComponentGeneratorFactory:
    @staticmethod
    def create_generator(component_type: str) -> ComponentGenerator:
        """Create generator for component type."""
        
        # Discover generator module
        module_path = f"components.{component_type}.generators"
        
        # Load generator class
        generator_class = import_generator(module_path)
        
        # Instantiate with dependencies
        return generator_class(
            client=get_api_client(),
            config=load_config()
        )
```

### Component Result

Standard return type for all generators:

```python
@dataclass
class ComponentResult:
    success: bool
    content: Any
    quality_score: float
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]
```

### Component Integration

**Wrapper Pattern**: Integrate specialized generators into component system.

```python
class TextComponentGenerator(ComponentGenerator):
    """Lightweight wrapper for fail_fast_generator."""
    
    def __init__(self, client, config):
        self.generator = FailFastGenerator(client, config)
    
    def generate(self, material_name: str) -> ComponentResult:
        # Delegate to specialized generator
        result = self.generator.generate(material_name)
        
        # Wrap in ComponentResult
        return ComponentResult(
            success=True,
            content=result['text'],
            quality_score=result['score']
        )
```

---

## Data Flow

### Single Material Generation

```
1. User Input
   └─> python3 run.py --material "Aluminum" --components frontmatter

2. CLI Validation
   └─> Validate "Aluminum" exists in Materials.yaml
   └─> Validate "frontmatter" is valid component

3. Material Loading
   └─> materials = load_materials()
   └─> material = materials['Aluminum']  # O(1) lookup

4. Component Generation
   └─> generator = ComponentGeneratorFactory.create_generator('frontmatter')
   └─> result = generator.generate('Aluminum')

5. Content Generation
   └─> API Call: DeepSeek (generate applications)
   └─> API Call: DeepSeek (generate properties)
   └─> API Call: DeepSeek (generate machine settings)

6. Validation
   └─> validate_and_improve_frontmatter('Aluminum', result.content)
   └─> Check: applications (simple strings, min 2)
   └─> Check: micro (camelCase, full structure)
   └─> Check: tags (4-10 items)

7. Quality Scoring
   └─> API Call: Winston AI (score quality)
   └─> Threshold check: score ≥ 70

8. Output
   └─> Write: content/components/frontmatter/aluminum-laser-cleaning.yaml
   └─> Display: Success message with quality score
```

### Batch Generation

```
1. User Input
   └─> python3 scripts/tools/batch_regenerate_frontmatter.py --resume

2. Material Discovery
   └─> Load all materials from Materials.yaml (121 items)
   └─> Check existing files for compliance

3. Status Assessment
   └─> For each material:
       ├─> Check if frontmatter file exists
       ├─> Validate format (applications, micro, tags)
       └─> Mark: ✅ up-to-date or ⚠️ needs regen

4. Batch Processing
   └─> For each material needing regeneration:
       ├─> Generate frontmatter (same as single material)
       ├─> Update progress: [45/104] Processing: Copper (ETA: 2h 15m)
       ├─> Log success/failure
       └─> Continue on errors (resilient)

5. Resume Capability
   └─> Skip already-compliant materials
   └─> Safe to interrupt (Ctrl+C)
   └─> Re-run to continue from last point

6. Final Report
   └─> Total processed: 104
   └─> Successful: 102
   └─> Failed: 2 (with error details)
   └─> Time taken: 5h 12m
```

---

## API Integration

### Request Flow

```
Generator → API Client → Request Builder → HTTP Layer → External API
                ↓
          Response Parser → Validation → Cache → Return
```

### Error Handling Strategy

#### 1. Transient Errors (Retry)

```python
@retry(max_attempts=3, backoff=exponential)
def call_api(endpoint, data):
    response = requests.post(endpoint, json=data)
    
    if response.status_code in [429, 503]:
        raise RetryableError("Rate limit or service unavailable")
    
    return response.json()
```

**Retryable Errors**:
- 429 Rate Limit
- 503 Service Unavailable
- Network timeouts
- Connection errors

#### 2. Permanent Errors (Fail Fast)

```python
if response.status_code == 401:
    raise ConfigurationError("Invalid API key")

if response.status_code == 400:
    raise GenerationError(f"Bad request: {response.text}")
```

**Non-Retryable Errors**:
- 401 Unauthorized (bad API key)
- 400 Bad Request (invalid input)
- 404 Not Found (missing resource)

### API Caching

**Purpose**: Reduce redundant API calls, improve performance

```python
@lru_cache(maxsize=128)
def get_material_properties(material_name: str):
    """Cache material property lookups."""
    return api.fetch_properties(material_name)
```

**Cache Strategy**:
- Material data: Cache indefinitely (static)
- Generated content: No cache (always fresh)
- API clients: Cache per session
- Configuration: Cache with TTL (5 minutes)

---

## Generation Pipeline

### Frontmatter Pipeline

**File**: `components/frontmatter/core/streamlined_generator.py` (1,556 lines)

**⚠️ CRITICAL REQUIREMENT**: Stage 0 (AI Research) MUST be completed before ANY generation.

```
Input: Material Name
  ↓
0. AI RESEARCH & DATA COMPLETION (MANDATORY)
   ⚡ ABSOLUTE REQUIREMENT - NO EXCEPTIONS
   - Check material completeness in Materials.yaml
   - Identify missing property values (635 gaps as of Oct 2025)
   - Run AI research to fill ALL missing properties
   - Validate category ranges complete (100% required)
   - Ensure ZERO NULL values before proceeding
   - Tools: PropertyValueResearcher, CategoryRangeResearcher
   - Command: python3 run.py --data-gaps
   ⚠️  FAIL-FAST: Generation blocked if properties incomplete
  ↓
1. Load Material Data
   - Get material from Materials.yaml
   - Extract properties, characteristics
   - Identify category and industries
  ↓
2. Generate Applications (Simple Strings)
   - API Call: DeepSeek
   - Format: "Industry: Description"
   - Count: 8-15 applications
   - Example: "Aerospace: Precision cleaning of aerospace components"
  ↓
3. Generate Caption (CamelCase)
   - API Call: DeepSeek
   - Keys: beforeText, afterText, description, alt, etc.
   - Structure: Full micro object
   - Format: CamelCase (NOT snake_case)
  ↓
4. Generate Tags (10 items)
   - Extract: 1 category + 3 industries + 3 processes
   - Add: 2 characteristics + 1 author
   - Example: ['metal', 'aerospace', 'electronics', 'jewelry', ...]
  ↓
5. Generate Properties
   - Mechanical properties
   - Thermal properties
   - Electrical properties
  ↓
6. Generate Machine Settings
   - Power settings
   - Speed settings
   - Safety parameters
  ↓
7. Assemble YAML
   - Combine all sections
   - Validate structure
   - Format consistently
  ↓
Output: YAML file
```

### Text Pipeline

**File**: `components/text/generators/fail_fast_generator.py` (25,679 bytes)

```
Input: Material Name
  ↓
1. Select Author Persona
   - 4 personas: Todd Dunning (USA), Yi-Chun Lin (Taiwan), 
                 Alessandro Moretti (Italy), Ikmanda Roswati (Indonesia)
   - Consistent assignment by material
   - Load author-specific prompts
  ↓
2. Build Prompt (12-step Layered)
   - Base guidance (tone, structure)
   - Author persona (writing style, linguistic nuances)
   - Formatting rules (word count, sections)
   - Material context (properties, applications)
  ↓
3. Generate Content
   - API Call: DeepSeek
   - Target: 250-450 words (author-specific)
   - Style: Author's voice and cultural elements
  ↓
4. Quality Scoring (5 dimensions)
   - Coherence: Logical flow
   - Engagement: Reader interest
   - Accuracy: Technical correctness
   - Style: Writing quality
   - Human Believability: ≥ 70 threshold
  ↓
5. Validate Output
   - Word count within range
   - No AI detection markers
   - Authentic voice
  ↓
Output: Markdown file
```

---

## Quality Assurance

### Multi-Dimensional Scoring

**Provider**: Winston AI

#### Score Dimensions

1. **Coherence** (0-100)
   - Logical flow
   - Argument structure
   - Transitions

2. **Engagement** (0-100)
   - Reader interest
   - Hook quality
   - Pacing

3. **Accuracy** (0-100)
   - Factual correctness
   - Technical precision
   - Source reliability

4. **Style** (0-100)
   - Writing quality
   - Grammar
   - Tone consistency

5. **Human Believability** (0-100)
   - Natural language
   - No AI markers
   - Authentic voice

#### Quality Thresholds

```python
# Minimum scores for publication
THRESHOLDS = {
    'human_believability': 70,  # Critical
    'accuracy': 80,             # High priority
    'coherence': 75,            # High priority
    'engagement': 65,           # Medium priority
    'style': 70,                # Medium priority
}
```

### Validation Rules

#### Frontmatter Validation

```python
def validate_frontmatter(data):
    # Applications: Simple strings
    assert all(
        isinstance(app, str) and ':' in app
        for app in data['applications']
    ), "Applications must be simple strings 'Industry: Description'"
    
    # Micro: CamelCase
    caption = data['images']['micro']
    assert 'beforeText' in micro, "Caption must use camelCase"
    assert 'afterText' in micro, "Caption must use camelCase"
    
    # Tags: 4-10 items
    assert 4 <= len(data['tags']) <= 10, "Tags must be 4-10 items"
    
    # Required fields
    required = ['material', 'category', 'properties', 'applications']
    assert all(field in data for field in required)
```

#### Text Validation

```python
def validate_text(content, author):
    # Word count
    word_count = len(content.split())
    min_words, max_words = AUTHOR_LIMITS[author]
    assert min_words <= word_count <= max_words
    
    # Quality score
    score = winston_score(content)
    assert score['human_believability'] >= 70
    
    # Author voice
    assert has_author_markers(content, author)
```

---

## Error Handling

### Exception Hierarchy

```
BaseException
└─ ZBeamError (base for all Z-Beam errors)
   ├─ ConfigurationError (missing/invalid config)
   │  ├─ MissingAPIKeyError
   │  ├─ InvalidConfigFileError
   │  └─ MissingDependencyError
   │
   ├─ GenerationError (content generation failures)
   │  ├─ APICallError
   │  ├─ ValidationError
   │  └─ QualityThresholdError
   │
   └─ RetryableError (temporary failures)
      ├─ RateLimitError
      ├─ ServiceUnavailableError
      └─ NetworkError
```

### Error Handling Strategy

```python
def generate_content(material_name):
    try:
        # 1. Validate configuration
        validate_config()  # Fail fast on missing config
        
        # 2. Load material
        material = get_material_by_name(material_name)
        if not material:
            raise GenerationError(f"Material not found: {material_name}")
        
        # 3. Generate content
        content = api_generate(material)
        
        # 4. Validate output
        if not validate_content(content):
            raise ValidationError("Generated content failed validation")
        
        return content
        
    except ConfigurationError as e:
        # Permanent error - log and exit
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
        
    except RetryableError as e:
        # Transient error - retry
        logger.warning(f"Retryable error: {e}, attempting retry...")
        return retry_generate(material_name)
        
    except GenerationError as e:
        # Generation failed - log and continue
        logger.error(f"Generation failed: {e}")
        return None
```

---

## Performance Characteristics

### Timing Analysis

#### Single Material Generation

| Component | Time | API Calls |
|-----------|------|-----------|
| Frontmatter | ~3 minutes | 4-6 calls |
| Text | ~3 minutes | 2-3 calls |
| Caption | ~1 minute | 1-2 calls |
| Tags | ~30 seconds | 1 call |

**Total**: ~7-8 minutes per material for complete generation

#### Batch Generation

**121 materials × 3 minutes = ~6 hours**

Performance considerations:
- Sequential processing (no parallel API calls to avoid rate limits)
- Resume capability for interrupted batches
- Progress tracking with ETA
- Error resilience (continues despite individual failures)

### Optimization Opportunities

1. **Caching**
   - Material data (static)
   - API client instances
   - Configuration files

2. **Parallel Generation**
   - Multiple materials simultaneously
   - Requires rate limit management
   - Risk of API throttling

3. **Incremental Updates**
   - Only regenerate changed materials
   - Skip up-to-date content
   - Currently implemented in batch scripts

---

## Summary

### System Strengths

1. **Fail-Fast Architecture**: Clear errors, no silent failures
2. **Component Modularity**: Easy to add new generators
3. **Quality-First**: Multi-dimensional scoring ensures high quality
4. **Data-Driven**: Flattened structure for simple access
5. **Production-Ready**: Comprehensive error handling and validation

### System Constraints

1. **API Dependency**: Requires external APIs (DeepSeek, Winston)
2. **Generation Time**: ~3 minutes per material (API latency)
3. **Sequential Processing**: No parallel generation (rate limits)
4. **No Fallbacks**: System fails if dependencies unavailable

### Design Decisions

| Decision | Rationale |
|----------|-----------|
| Fail-fast over degraded | Ensures quality, prevents bad content |
| No mocks in production | Forces proper error handling |
| Flattened data structure | Simpler AI navigation, O(1) lookups |
| Component factory pattern | Extensible, discoverable generators |
| Simple string applications | Easier to generate, validate, read |
| CamelCase micros | Consistent with JSON conventions |
| 10-tag generation | Optimal for SEO and categorization |

---

**Version History**:
- v1.0: Initial nested structure
- v2.0: Flattened structure (October 2, 2025)

**Next Review**: After batch regeneration completes
