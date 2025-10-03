# Z-Beam Generator Validation System

**Version**: 2.0  
**Last Updated**: October 2, 2025  
**Status**: Production-Ready

## Table of Contents

1. [Overview](#overview)
2. [Validation Philosophy](#validation-philosophy)
3. [Validation Rules](#validation-rules)
4. [Quality Scoring](#quality-scoring)
5. [Fail-Fast Principles](#fail-fast-principles)
6. [Validation Tools](#validation-tools)
7. [Common Issues](#common-issues)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The Z-Beam Generator validation system ensures **high-quality, consistent content** through:

- **Pre-generation validation**: Config and dependency checks
- **Post-generation validation**: Content structure and format checks
- **Quality scoring**: AI-powered quality assessment
- **Compliance verification**: Batch validation for all materials

### Validation Layers

```
1. Configuration Validation
   └─> API keys present, config files exist, dependencies available
   
2. Input Validation
   └─> Material exists, valid component type, required fields present
   
3. Content Validation
   └─> Structure correct, required fields present, format valid
   
4. Quality Validation
   └─> Winston AI scoring, threshold checks, human believability
   
5. Compliance Validation
   └─> Batch verification, consistency checks, format compliance
```

---

## Validation Philosophy

### Fail-Fast Design

**Core Principle**: **Fail immediately when problems are detected, don't continue with invalid state.**

```python
# ❌ BAD: Continue with potentially invalid data
def load_material(name):
    material = find_material(name)
    if not material:
        logger.warning(f"Material not found: {name}")
        material = {}  # Empty dict as fallback
    return material

# ✅ GOOD: Fail fast with clear error
def load_material(name):
    material = find_material(name)
    if not material:
        raise ValueError(f"Material not found: {name}")
    return material
```

**Benefits**:
- Clear error messages
- No silent failures
- Easier debugging
- Prevents bad content generation

### No Silent Fallbacks

**Rule**: Never use default values or fallbacks for critical data.

```python
# ❌ BAD: Silent fallback to default
api_key = config.get('api_key', 'default_key')

# ✅ GOOD: Explicit failure
api_key = config.get('api_key')
if not api_key:
    raise ConfigurationError("API key not configured")
```

### Explicit Over Implicit

**Rule**: Make validation explicit and visible.

```python
# ❌ BAD: Implicit validation
def generate(material_name):
    material = get_material(material_name)
    return api_generate(material)

# ✅ GOOD: Explicit validation
def generate(material_name):
    # Validate input
    if not material_name:
        raise ValueError("Material name is required")
    
    # Validate material exists
    material = get_material(material_name)
    if not material:
        raise ValueError(f"Material not found: {material_name}")
    
    # Validate required fields
    validate_material_structure(material)
    
    # Generate
    return api_generate(material)
```

---

## Validation Rules

### Frontmatter Validation

**File**: `pipeline_integration.py::validate_and_improve_frontmatter()`

#### Applications

**Format**: Simple strings with colon separator

```yaml
# ✅ VALID: Simple string format
applications:
  - 'Aerospace: Precision cleaning of aerospace components and assemblies'
  - 'Electronics: Cleaning electronic components and circuit boards'
  - 'Manufacturing: Industrial surface preparation and coating removal'

# ❌ INVALID: Old structured format
applications:
  - industry: Aerospace
    detail: Precision cleaning
    cleaningTypes: [rust, oxidation]
```

**Validation Rules**:
```python
def validate_applications(applications):
    # Type check
    assert isinstance(applications, list), "Applications must be a list"
    
    # Count check
    assert len(applications) >= 2, "Minimum 2 applications required"
    
    # Format check
    for app in applications:
        assert isinstance(app, str), "Each application must be a string"
        assert ':' in app, "Application must have format 'Industry: Description'"
        
        # Length checks
        industry, description = app.split(':', 1)
        assert len(industry.strip()) >= 3, "Industry name too short"
        assert len(description.strip()) >= 20, "Description too short"
```

#### Caption

**Format**: CamelCase keys, full structure

```yaml
# ✅ VALID: CamelCase format
images:
  caption:
    beforeText: 'At 500x magnification, the surface shows heavy oxidation'
    afterText: 'Following laser cleaning, the surface reveals pristine metal'
    description: 'Microscopic comparison of material surface'
    alt: 'Before and after laser cleaning comparison'
    technicalAnalysis: 'Surface roughness reduced from Ra 3.2 to Ra 0.8'
    microscopy: '500x magnification using digital microscope'
    generation: 'Generated using AI-powered analysis'
    author: 'todd-dunning'
    materialProperties: 'High reflectivity, moderate hardness'
    imageUrl: '/images/materials/aluminum-before-after.jpg'

# ❌ INVALID: snake_case format (old)
images:
  caption:
    before_text: 'At 500x magnification...'
    after_text: 'Following laser cleaning...'
```

**Validation Rules**:
```python
def validate_caption(caption):
    # Required fields (camelCase)
    required_fields = [
        'beforeText', 'afterText', 'description', 'alt',
        'technicalAnalysis', 'microscopy', 'generation',
        'author', 'materialProperties', 'imageUrl'
    ]
    
    for field in required_fields:
        assert field in caption, f"Missing required caption field: {field}"
    
    # Check for old snake_case format
    old_format_fields = ['before_text', 'after_text']
    for field in old_format_fields:
        assert field not in caption, f"Use camelCase, not snake_case: {field} → beforeText/afterText"
    
    # Length checks
    assert len(caption['beforeText']) >= 20, "beforeText too short"
    assert len(caption['afterText']) >= 20, "afterText too short"
```

#### Tags

**Format**: 4-10 items, includes category + industries + processes

```yaml
# ✅ VALID: 10 tags with good distribution
tags:
  - metal                    # 1 category
  - aerospace                # 3 industries
  - electronics
  - manufacturing
  - reflective               # 2 characteristics
  - conductive
  - laser-cleaning           # 2 processes
  - surface-prep
  - industrial               # 1 context
  - todd-dunning             # 1 author

# ❌ INVALID: Too few tags
tags:
  - metal
  - aerospace

# ❌ INVALID: Missing required fields
# (no tags field at all)
```

**Validation Rules**:
```python
def validate_tags(tags):
    # Presence check
    assert tags is not None, "Tags field is required"
    
    # Type check
    assert isinstance(tags, list), "Tags must be a list"
    
    # Count check
    assert 4 <= len(tags) <= 10, f"Tags must be 4-10 items, got {len(tags)}"
    
    # Content check
    for tag in tags:
        assert isinstance(tag, str), "Each tag must be a string"
        assert len(tag) >= 3, "Tag too short"
        assert tag.islower() or '-' in tag, "Tags should be lowercase or hyphenated"
```

#### Required Fields

**All frontmatter must include**:

```python
REQUIRED_FRONTMATTER_FIELDS = [
    'material',              # Material name
    'category',              # Material category (metal, wood, etc.)
    'properties',            # Material properties object
    'applications',          # List of applications
    'machineSettings',       # Laser machine settings
    'safetyConsiderations',  # Safety information
    'images',                # Image data with caption
    'tags',                  # SEO tags
]

def validate_required_fields(frontmatter):
    for field in REQUIRED_FRONTMATTER_FIELDS:
        if field not in frontmatter:
            raise ValidationError(f"Missing required field: {field}")
```

### Text Validation

**File**: `components/text/generators/fail_fast_generator.py`

#### Word Count

**Rule**: Author-specific limits

```python
AUTHOR_WORD_LIMITS = {
    'todd-dunning': (250, 450),    # USA author
    'emma-clarke': (300, 500),      # UK author
    'luca-moretti': (280, 480),     # Italy author
    'yuki-tanaka': (260, 450),      # Japan author
}

def validate_word_count(text, author):
    word_count = len(text.split())
    min_words, max_words = AUTHOR_WORD_LIMITS[author]
    
    if word_count < min_words:
        raise ValidationError(f"Text too short: {word_count} < {min_words}")
    
    if word_count > max_words:
        raise ValidationError(f"Text too long: {word_count} > {max_words}")
```

#### Quality Score

**Rule**: Human believability ≥ 70

```python
def validate_quality_score(text):
    score = winston_ai_score(text)
    
    if score['human_believability'] < 70:
        raise QualityThresholdError(
            f"Human believability too low: {score['human_believability']} < 70"
        )
    
    # Additional checks
    if score['accuracy'] < 80:
        logger.warning(f"Accuracy below target: {score['accuracy']}")
    
    if score['coherence'] < 75:
        logger.warning(f"Coherence below target: {score['coherence']}")
```

#### Author Voice

**Rule**: Must contain author-specific linguistic markers

```python
def validate_author_voice(text, author):
    markers = AUTHOR_MARKERS[author]
    
    # Check for author-specific phrases
    found_markers = sum(1 for marker in markers if marker in text.lower())
    
    if found_markers < 3:
        logger.warning(
            f"Text lacks author voice markers for {author} "
            f"(found {found_markers} of {len(markers)})"
        )
```

---

## Quality Scoring

### Winston AI Integration

**Provider**: Winston AI  
**Purpose**: Multi-dimensional content quality assessment

#### Score Dimensions

```python
@dataclass
class QualityScore:
    """Winston AI quality score."""
    
    coherence: float           # 0-100: Logical flow
    engagement: float          # 0-100: Reader interest
    accuracy: float            # 0-100: Factual correctness
    style: float               # 0-100: Writing quality
    human_believability: float # 0-100: Natural language (critical)
    
    overall: float             # Average of all dimensions
```

#### Quality Thresholds

```python
QUALITY_THRESHOLDS = {
    'human_believability': 70,  # CRITICAL: Minimum for publication
    'accuracy': 80,             # HIGH: Must be factually correct
    'coherence': 75,            # HIGH: Must flow logically
    'engagement': 65,           # MEDIUM: Should be interesting
    'style': 70,                # MEDIUM: Should be well-written
}

def check_quality_thresholds(score: QualityScore):
    """Check if score meets all thresholds."""
    
    failures = []
    
    for dimension, threshold in QUALITY_THRESHOLDS.items():
        actual = getattr(score, dimension)
        
        if actual < threshold:
            failures.append(
                f"{dimension}: {actual:.1f} < {threshold} (threshold)"
            )
    
    if failures:
        raise QualityThresholdError(
            f"Quality thresholds not met:\n" + "\n".join(failures)
        )
```

#### Scoring Process

```
1. Generate Content
   └─> DeepSeek API generates text
   
2. Submit to Winston AI
   └─> POST /api/score with text content
   
3. Receive Score
   └─> 5-dimensional score + overall
   
4. Validate Thresholds
   └─> Check each dimension against threshold
   
5. Decision
   ├─> Pass: All thresholds met → Accept content
   └─> Fail: Any threshold not met → Reject or regenerate
```

### Quality Improvement

**File**: `pipeline_integration.py::validate_and_improve_frontmatter()`

```python
def validate_and_improve_frontmatter(material_name, frontmatter):
    """Validate and suggest improvements."""
    
    issues = []
    improvements = []
    
    # Validate applications
    if len(frontmatter['applications']) < 8:
        issues.append("Insufficient applications")
        improvements.append("Add more industry-specific applications")
    
    # Validate caption
    caption = frontmatter.get('images', {}).get('caption', {})
    if 'beforeText' not in caption:
        issues.append("Missing caption.beforeText")
        improvements.append("Add beforeText to caption")
    
    # Validate tags
    if 'tags' not in frontmatter:
        issues.append("Missing tags field")
        improvements.append("Generate tags from industries and processes")
    
    return {
        'validation_passed': len(issues) == 0,
        'issues_detected': issues,
        'improvements': improvements,
        'material': material_name,
        'validation_result': {
            'validation_passed': len(issues) == 0,
            'issues_detected': issues,
        }
    }
```

---

## Fail-Fast Principles

### Configuration Validation

**When**: On system startup, before any generation

```python
def validate_configuration():
    """Validate all required configuration."""
    
    # Check API keys
    required_keys = ['DEEPSEEK_API_KEY', 'WINSTON_API_KEY']
    for key in required_keys:
        if not os.getenv(key):
            raise ConfigurationError(f"Missing required API key: {key}")
    
    # Check config files
    required_files = [
        'data/materials.yaml',
        'data/Categories.yaml',
        'config/pipeline_config.yaml',
    ]
    for file in required_files:
        if not Path(file).exists():
            raise ConfigurationError(f"Missing required config file: {file}")
    
    # Check dependencies
    try:
        import yaml
        import requests
    except ImportError as e:
        raise ConfigurationError(f"Missing required dependency: {e}")
```

### Input Validation

**When**: Before starting generation

```python
def validate_generation_input(material_name, component_type):
    """Validate generation inputs."""
    
    # Validate material exists
    materials = load_materials()
    if material_name not in materials:
        raise ValueError(
            f"Material not found: {material_name}\n"
            f"Available materials: {', '.join(list(materials.keys())[:10])}..."
        )
    
    # Validate component type
    valid_components = [
        'frontmatter', 'text', 'author', 'caption', 
        'tags', 'categories', 'jsonld', 'metatags'
    ]
    if component_type not in valid_components:
        raise ValueError(
            f"Invalid component type: {component_type}\n"
            f"Valid types: {', '.join(valid_components)}"
        )
```

### Generation Validation

**When**: After content generation, before saving

```python
def validate_generated_content(content, component_type):
    """Validate generated content."""
    
    # Type check
    if content is None:
        raise GenerationError("Generated content is None")
    
    # Component-specific validation
    if component_type == 'frontmatter':
        validate_frontmatter(content)
    elif component_type == 'text':
        validate_text(content)
    
    # Quality check
    score = get_quality_score(content)
    validate_quality_thresholds(score)
```

---

## Validation Tools

### 1. Quick Validation Script

**File**: `scripts/tools/test_copper_quick.py`

```bash
# Validate a single material
python3 scripts/tools/test_copper_quick.py

# Output:
# ✅ Applications: Simple strings (8 items)
# ✅ Caption: CamelCase (beforeText, afterText)
# ✅ Tags: Present (10 items)
```

### 2. Compliance Verification

**File**: `scripts/tools/verify_frontmatter_compliance.py`

```bash
# Check all 121 materials
python3 scripts/tools/verify_frontmatter_compliance.py

# Output:
# Total materials: 121
# ✅ Compliant: 17 (14.0%)
# ❌ Non-compliant: 104 (86.0%)
#
# Top Issues:
#   [84] Caption uses snake_case (should be camelCase)
#   [69] Missing required field: tags
#   [30] Insufficient applications (< 2)

# Detailed mode
python3 scripts/tools/verify_frontmatter_compliance.py --details

# Export report
python3 scripts/tools/verify_frontmatter_compliance.py --export report.txt
```

### 3. Pipeline Validation

**Built-in**: Runs automatically during generation

```python
# In run.py
result = generate_frontmatter(material_name)

# Automatic validation
validation = validate_and_improve_frontmatter(material_name, result)

if not validation['validation_passed']:
    print(f"⚠️ Validation issues detected:")
    for issue in validation['issues_detected']:
        print(f"  - {issue}")
```

### 4. Pre-Flight Checks

**File**: `scripts/tools/batch_regenerate_frontmatter.py`

```bash
# Dry-run to check what would be processed
python3 scripts/tools/batch_regenerate_frontmatter.py --dry-run

# Output:
# Would process 121 materials:
#   Alabaster: ⚠️ needs regen (missing tags)
#   Aluminum: ⚠️ needs regen (snake_case caption)
#   Bamboo: ✅ up-to-date
#   ...
```

---

## Common Issues

### Issue 1: Applications Wrong Format

**Symptom**: `ValidationError: Applications must be simple strings`

**Cause**: Old structured format used instead of simple strings

**Fix**:
```python
# ❌ WRONG
applications:
  - industry: Aerospace
    detail: Precision cleaning

# ✅ CORRECT
applications:
  - 'Aerospace: Precision cleaning of aerospace components'
```

### Issue 2: Caption Uses snake_case

**Symptom**: `ValidationError: Caption must use camelCase`

**Cause**: Old snake_case format (before_text/after_text)

**Fix**:
```yaml
# ❌ WRONG
caption:
  before_text: 'At 500x magnification...'
  after_text: 'Following laser cleaning...'

# ✅ CORRECT
caption:
  beforeText: 'At 500x magnification...'
  afterText: 'Following laser cleaning...'
```

### Issue 3: Missing Tags

**Symptom**: `ValidationError: Missing required field: tags`

**Cause**: Tags generation disabled or not called

**Fix**: Ensure tags generation is enabled in generator
```python
# In streamlined_generator.py
self._add_tags_section()  # Make sure this is called
```

### Issue 4: Quality Score Too Low

**Symptom**: `QualityThresholdError: Human believability: 65 < 70`

**Cause**: AI-generated text too mechanical or unnatural

**Fix**:
1. Regenerate with different author persona
2. Adjust prompt to emphasize natural language
3. Review author-specific linguistic markers

### Issue 5: Insufficient Applications

**Symptom**: `ValidationError: Insufficient applications: 3 (need at least 8)`

**Cause**: Generation didn't produce enough applications

**Fix**:
1. Check prompt for application generation
2. Ensure unified industry data is complete
3. Verify material has multiple relevant industries

---

## Troubleshooting

### Debug Validation Failures

**Step 1: Enable debug logging**
```bash
export LOG_LEVEL=DEBUG
python3 run.py --material "Aluminum" --components frontmatter
```

**Step 2: Check validation output**
```python
# In pipeline_integration.py
logger.debug(f"Validating applications: {applications}")
logger.debug(f"Applications count: {len(applications)}")
logger.debug(f"First application: {applications[0] if applications else 'None'}")
```

**Step 3: Validate manually**
```python
import yaml
from pipeline_integration import validate_and_improve_frontmatter

with open('content/components/frontmatter/aluminum-laser-cleaning.yaml') as f:
    frontmatter = yaml.safe_load(f)

result = validate_and_improve_frontmatter('Aluminum', frontmatter)
print(f"Validation passed: {result['validation_passed']}")
print(f"Issues: {result['issues_detected']}")
```

### Fix Common Validation Errors

**Error**: `KeyError: 'validation_result'`

**Cause**: Old version of `pipeline_integration.py`

**Fix**: Update to latest version (includes `validation_result` in both paths)

---

**Error**: `AssertionError: Applications must be simple strings`

**Cause**: Using old structured format

**Fix**: Convert to simple strings
```python
# Quick fix script
for app in old_applications:
    new_format = f"{app['industry']}: {app['detail']}"
    new_applications.append(new_format)
```

---

**Error**: `ValidationError: Caption missing beforeText`

**Cause**: Old snake_case format or incomplete caption

**Fix**: Regenerate caption or manually convert
```python
# Manual conversion
caption['beforeText'] = caption.pop('before_text')
caption['afterText'] = caption.pop('after_text')
```

---

## Summary

### Validation Best Practices

1. **Fail Fast**: Validate configuration before generation
2. **Explicit Rules**: Clear, testable validation criteria
3. **Quality First**: Use Winston AI scoring for quality assurance
4. **Comprehensive Checks**: Validate structure, format, content, and quality
5. **Tooling**: Use automated tools for batch validation

### Validation Workflow

```
1. Pre-Generation
   ├─> Validate configuration
   ├─> Validate input material exists
   └─> Validate component type valid

2. During Generation
   ├─> Generate content via API
   └─> Log progress and errors

3. Post-Generation
   ├─> Validate content structure
   ├─> Check format compliance
   ├─> Score quality (Winston AI)
   └─> Verify thresholds

4. Before Save
   ├─> Final validation pass
   ├─> Check required fields
   └─> Confirm quality meets standards

5. Batch Validation
   ├─> Run compliance verification
   ├─> Identify non-compliant files
   └─> Generate regeneration list
```

### Quality Standards

- **Applications**: ≥2 items, simple strings "Industry: Description"
- **Caption**: CamelCase, 10 required fields, ≥20 chars each
- **Tags**: 4-10 items, includes category + industries + processes
- **Text**: 250-450 words, human believability ≥70
- **Overall**: All required fields present, formats correct

---

**Next Steps**:
1. Run compliance verification: `python3 scripts/tools/verify_frontmatter_compliance.py`
2. Fix non-compliant files: `python3 scripts/tools/batch_regenerate_frontmatter.py --resume`
3. Verify completion: 121/121 materials compliant

**See Also**:
- `docs/architecture/SYSTEM_ARCHITECTURE.md` - Overall system design
- `docs/development/TESTING.md` - Test framework
- `docs/operations/DEPLOYMENT_CHECKLIST.md` - Pre-deployment validation
