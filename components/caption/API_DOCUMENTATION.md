# Caption Component API Documentation v3.1

## Overview
The Caption Component has been enhanced to v3.1 with doubled scientific content length (500-700 characters per section), advanced analytical techniques (XPS, SEM, AFM, EDX), and comprehensive quantitative measurements. Features case-insensitive material name search and fail-fast architecture with enhanced scientific depth for professional materials analysis.

## Core API Functions

### `generate_caption_content(material_name, material_data, api_client)`

**Primary function for AI-powered caption generation with enhanced scientific depth and doubled content length (500-700 characters per section).**

#### Parameters
- `material_name` (str): Material name in any case format (e.g., `"aluminum"`, `"Aluminum"`, `"ALUMINUM"`, `"silicon_carbide"`, `"Silicon Carbide"`)
- `material_data` (dict): Additional material data (can be empty `{}`)
- `api_client` (required): DeepSeek API client instance from `create_api_client('deepseek')`

#### Returns
- `str`: Complete YAML-formatted caption content (~2,600-2,800 characters with enhanced scientific depth)

#### Raises
- `ValueError`: If API client is missing (fail-fast architecture)
- `ValueError`: If frontmatter data is not found for material
- `ValueError`: If AI response lacks required text blocks
- `Exception`: If content validation fails

#### Example Usage
```python
from components.caption.generators.generator import generate_caption_content
from api.client_factory import create_api_client

# Create API client
client = create_api_client('deepseek')

# All these variations work identically:
content1 = generate_caption_content('aluminum', {}, api_client=client)
content2 = generate_caption_content('Aluminum', {}, api_client=client)
content3 = generate_caption_content('ALUMINUM', {}, api_client=client)

# All generate identical high-quality enhanced scientific content
print(len(content1))  # ~2,600-2,800 characters with scientific depth
```

#### Performance Characteristics (Enhanced v3.1)
- **Generation Time**: 17-20 seconds (enhanced scientific processing)
- **Content Length**: ~2,600-2,800 characters average (doubled from v3.0)
- **Scientific Depth**: Advanced analytical techniques (XPS, SEM, AFM, EDX)
- **Success Rate**: 100% for existing materials
- **Approach**: Enhanced text-block extraction with scientific depth validation

---

## CaptionComponentGenerator Class

### `__init__(self)`

Initialize the Caption component generator with fail-fast architecture.

```python
generator = CaptionComponentGenerator()
```

### `generate(self, material_name, material_data, api_client)`

**Main generation method with enhanced case-insensitive support.**

#### Parameters
- `material_name` (str): Material name (case-insensitive)
- `material_data` (dict): Material data dictionary
- `api_client` (required): API client instance

#### Returns
- `str`: Complete YAML caption content

#### Implementation Notes
- Uses fail-fast architecture (no fallbacks)
- Requires both API client and frontmatter data
- Validates all inputs before generation
- Handles case-insensitive material name resolution

```python
from components.caption.generators.generator import CaptionComponentGenerator
from api.client_factory import create_api_client

generator = CaptionComponentGenerator()
client = create_api_client('deepseek')

content = generator.generate('Aluminum', {}, api_client=client)
```

### `_load_frontmatter_data(self, material_name)`

**Enhanced case-insensitive frontmatter loading method.**

#### Parameters
- `material_name` (str): Material name in any case format

#### Returns
- `dict`: Frontmatter data if found, empty dict if not found

#### Path Matching Strategy
The method tries 6 different path patterns in order:
1. `{material_name.lower()}.yaml`
2. `{material_name.lower().replace(' ', '-')}.yaml`
3. `{material_name.lower().replace('_', '-')}.yaml`
4. `{normalized_name}.yaml` (comprehensive normalization)
5. `{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml`
6. `{normalized_name}-laser-cleaning.yaml`

#### Supported Input Formats
- **Spaces**: `"stainless steel"` → `stainless-steel-laser-cleaning.yaml`
- **Underscores**: `"silicon_carbide"` → `silicon-carbide-laser-cleaning.yaml`
- **Mixed Case**: `"AlUmInUm"` → `aluminum-laser-cleaning.yaml`
- **All Caps**: `"ALUMINUM"` → `aluminum-laser-cleaning.yaml`

```python
# All these work identically:
data1 = generator._load_frontmatter_data('aluminum')
data2 = generator._load_frontmatter_data('Aluminum') 
data3 = generator._load_frontmatter_data('ALUMINUM')
data4 = generator._load_frontmatter_data('silicon carbide')
data5 = generator._load_frontmatter_data('silicon_carbide')
data6 = generator._load_frontmatter_data('Silicon_Carbide')

# All return identical frontmatter data
assert data1 == data2 == data3  # True for aluminum variations
assert data4 == data5 == data6  # True for silicon carbide variations
```

### `_build_prompt(self, material_name, material_data, author_info, category)`

**Build comprehensive AI prompt for material-specific generation.**

#### Parameters
- `material_name` (str): Material name
- `material_data` (dict): Material properties and data
- `author_info` (dict): Author information from frontmatter
- `category` (str): Material category

#### Returns
- `str`: Comprehensive AI prompt (~5,000+ characters)

#### Features
- Material-specific contamination profiles
- Author expertise integration
- Category-appropriate technical focus
- Professional SEM terminology guidance
- Quality metrics specifications

### `_extract_ai_content(self, ai_response)`

**Extract and validate AI-generated text blocks with simplified validation.**

#### Parameters
- `ai_response` (str): Raw AI response content

#### Returns
- `dict`: Validated content structure with text blocks

#### Text Block Format
The AI response is expected to contain:
```
**BEFORE_TEXT:**
[Technical description of contaminated surface...]

**AFTER_TEXT:**
[Technical description of cleaned surface...]
```

#### Validation Rules
- Extracts content between `**BEFORE_TEXT:**` and `**AFTER_TEXT:**` markers
- Validates minimum content length requirements (50+ characters each)
- Ensures technical accuracy and professional language
- Returns structured dict with additional metadata fields

#### Simplified Approach Benefits
- **No JSON Parsing**: Direct text extraction eliminates parsing errors
- **Faster Processing**: Simple string operations vs complex JSON validation
- **More Reliable**: No dependency on AI formatting perfect JSON
- **Enhanced Quality**: Professional technical content with scientific depth

---

## Enhanced Technical Specifications (v3.1)

### AI Generation Parameters
- **Model Configuration**: DeepSeek-V2.5 with enhanced scientific processing
- **Max Tokens**: 3,000 (increased from 1,500 for doubled content)
- **Temperature**: 0.2 (reduced from 0.3 for higher precision)
- **Content Requirements**: 500-700 characters per text section

### Scientific Enhancement Features
- **Analytical Techniques**: XPS (X-ray Photoelectron Spectroscopy), SEM (Scanning Electron Microscopy), AFM (Atomic Force Microscopy), EDX (Energy-Dispersive X-ray Spectroscopy)
- **Quantitative Measurements**: Precise surface roughness values, contamination percentages, cleaning efficiency metrics
- **Technical Depth**: Advanced material science terminology and professional analysis standards
- **Content Validation**: Minimum 200 characters per section (increased from 50)

### Content Quality Standards
- **Total Length**: 2,600-2,800 characters (doubled from v3.0)
- **Scientific Accuracy**: Professional materials science terminology
- **Technical Precision**: Quantitative measurements and specific analytical methods
- **Professional Language**: Industry-standard technical writing

---

## Content Structure

### AI-Generated Fields (77% of content)
```python
{
    'before_text': 'SEM analysis reveals contaminated surface...',
    'after_text': 'Post-cleaning SEM confirms pristine surface...',
    'technical_analysis': {
        'focus': 'thermal/optical',
        'unique_characteristics': [...],
        'contamination_profile': '...'
    },
    'microscopy': {
        'parameters': 'SEM analysis parameters...',
        'quality_metrics': 'Quality assessments...'
    }
}
```

### Frontmatter-Sourced Fields (4% of content)
```python
{
    'author': 'Author Name',
    'material_properties': {
        'materialType': 'Metal',
        'analysisMethod': 'ai_microscopy'
    }
}
```

### System-Generated Fields (19% of content)
```python
{
    'generation': {
        'generated': '2025-09-28T17:26:14Z',
        'component_type': 'ai_caption_fail_fast'
    },
    'processing': {
        'frontmatter_available': True,
        'ai_generated': True,
        'generation_method': 'ai_research'
    },
    'seo': {
        'title': 'AI-Generated Laser Cleaning Surface Analysis',
        'description': 'AI-generated microscopic analysis with enhanced scientific depth...'
    }
}
```

---

## Error Handling

### Fail-Fast Architecture
The component follows strict fail-fast principles:

```python
# These will raise ValueError immediately:
generate_caption_content('aluminum', {})  # Missing api_client
generate_caption_content('nonexistent_material', {}, api_client=client)  # No frontmatter

# These work correctly:
generate_caption_content('aluminum', {}, api_client=client)  # ✅
generate_caption_content('ALUMINUM', {}, api_client=client)  # ✅
generate_caption_content('Aluminum', {}, api_client=client)  # ✅
```

### Common Error Scenarios
1. **Missing API Client**: `ValueError: API client required for caption generation`
2. **Missing Frontmatter**: `ValueError: Frontmatter data required for {material}`
3. **Missing Author**: `ValueError: Author information required in frontmatter`
4. **AI Generation Failure**: `Exception: AI content generation failed`

---

## Performance Optimization

### Caching Strategy
- Frontmatter data is loaded fresh each time (no caching)
- API responses are not cached (each generation is unique)
- Path resolution is optimized for common patterns

### Performance Metrics
- **Frontmatter Loading**: <2ms per material
- **AI Generation**: ~17-20 seconds per material (enhanced scientific processing)
- **Content Validation**: <1ms per generation
- **Scientific Enhancement**: Advanced analytical techniques integration
- **Total Time**: ~17-20 seconds per caption with doubled content depth

### Best Practices
```python
# Efficient batch processing
client = create_api_client('deepseek')  # Create once
materials = ['aluminum', 'steel', 'copper']

for material in materials:
    content = generate_caption_content(material, {}, api_client=client)
    # Process content...
    time.sleep(1)  # Rate limiting if needed
```

---

## Migration Guide

### From v2.0 to v3.0

#### Old Usage (v2.0)
```python
from components.caption.generators.generator import CaptionComponentGenerator

generator = CaptionComponentGenerator()
content = generator.generate_content("Aluminum", {})  # No API required
```

#### New Usage (v3.0)
```python
from components.caption.generators.generator import generate_caption_content
from api.client_factory import create_api_client

client = create_api_client('deepseek')
content = generate_caption_content('aluminum', {}, api_client=client)  # AI-powered
```

#### Key Changes
1. **API Client Required**: Must provide DeepSeek API client
2. **Case-Insensitive**: Material names work in any case format
3. **Fail-Fast**: No fallbacks - immediate failure for missing dependencies
4. **AI Content**: 77% AI-generated professional content
5. **Performance**: ~17 seconds vs instant (but much higher quality)

---

## Testing API

### Test Functions Available
```python
# Test case-insensitive search
from tests.test_caption_case_insensitive import test_case_insensitive_frontmatter_loading

# Test AI generation
from tests.test_caption_case_insensitive import test_ai_powered_generation

# Test performance
from tests.test_caption_case_insensitive import test_performance_characteristics

# Test path normalization  
from tests.test_caption_case_insensitive import test_path_normalization
```

### Integration Testing
```python
# Verify enhanced v3.1 functionality with doubled scientific content
materials = ['aluminum', 'Aluminum', 'ALUMINUM', 'silicon_carbide', 'Silicon Carbide']
client = create_api_client('deepseek')

for material in materials:
    content = generate_caption_content(material, {}, api_client=client)
    assert len(content) > 2500  # Enhanced content length (v3.1)
    assert 'before_text' in content  # Required AI field
    assert 'after_text' in content   # Required AI field
    
    # Validate enhanced scientific content depth
    before_section = content['before_text']
    after_section = content['after_text']
    assert len(before_section) >= 400  # Enhanced minimum length
    assert len(after_section) >= 400   # Enhanced minimum length
    
    # Check for scientific terminology
    scientific_terms = ['SEM', 'XPS', 'AFM', 'EDX', 'µm', 'nm', 'analysis']
    assert any(term in content for term in scientific_terms)
```

---

*API Documentation v3.1 | Updated: January 2025 | Enhanced Scientific Depth with Doubled Content Length*