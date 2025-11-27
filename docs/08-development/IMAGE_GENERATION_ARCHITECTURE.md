# Image Generation Architecture

**Date**: November 26, 2025  
**Status**: ✅ IMPLEMENTED  
**API**: Google Imagen 4

---

## 🎯 Overview

The Z-Beam system generates context-relevant, photo-realistic images for laser cleaning documentation using Google's Imagen 4 API. Images represent materials, contaminants, or material-contaminant combinations with strict realism requirements.

**Key Challenge**: Generating scientifically accurate images that depict how specific contaminants appear on specific materials requires detailed visual descriptions beyond basic chemical formulas.

---

## 📐 System Architecture

### High-Level Flow

```
1. Material Selection
   ↓
2. Contaminant Lookup (from Material data)
   ↓
3. Visual Description Research (from Contaminants data)
   ↓
4. Dynamic Prompt Construction
   ↓
5. Imagen 4 API Call
   ↓
6. Image Generation & Validation
```

### Component Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    SHARED INFRASTRUCTURE                     │
├─────────────────────────────────────────────────────────────┤
│  • shared/image/                                            │
│    - prompts/prompt_builder.py (template loading)          │
│    - prompts/prompt_optimizer.py (Imagen limits)           │
│    - learning/image_generation_logger.py (tracking)        │
│    - prompts/image_pipeline_monitor.py (failure analysis)  │
└─────────────────────────────────────────────────────────────┘
          ↓                                    ↓
┌──────────────────────────┐    ┌───────────────────────────┐
│   MATERIALS DOMAIN       │    │  CONTAMINANTS DOMAIN      │
├──────────────────────────┤    ├───────────────────────────┤
│ • domains/materials/     │    │ • domains/contaminants/   │
│   image/                 │    │   - models.py             │
│   - material_generator.py│    │   - library.py            │
│   - material_config.py   │    │   - validator.py          │
│   - prompts/             │    │   - Contaminants.yaml     │
│     * material_researcher│    │                           │
│     * category_researcher│    │ DATA:                     │
│                          │    │ • Visual characteristics  │
│ DATA:                    │    │ • Formation conditions    │
│ • Material properties    │    │ • Material compatibility  │
│ • Associated contaminants│    │ • Appearance descriptions │
└──────────────────────────┘    └───────────────────────────┘
          ↓                                    ↓
          └────────────────┬───────────────────┘
                          ↓
              ┌─────────────────────────┐
              │   IMAGEN 4 API          │
              │   imagen-4.0-generate   │
              └─────────────────────────┘
```

---

## 🔬 Data Architecture

### 1. Materials Data (`data/materials/Materials.yaml`)

**Purpose**: Store material properties and associated contaminants

```yaml
materials:
  Aluminum:
    properties:
      hardness: "2.5-3 Mohs"
      melting_point: "660°C"
      color: "Silver-white metallic"
    
    # Associated contaminants for image generation
    common_contaminants:
      - rust-oxidation      # ❌ Physically impossible (no iron)
      - oil-grease          # ✅ Valid
      - dust-dirt           # ✅ Valid
      - paint-coating       # ✅ Valid
```

**Key Point**: Materials reference contaminants by ID, but don't describe how they look.

---

### 2. Contaminants Data (`data/contaminants/Contaminants.yaml`)

**Purpose**: Store contamination patterns with visual appearance descriptions

```yaml
contamination_patterns:
  oil-grease:
    id: oil-grease
    name: "Oil & Grease Contamination"
    category: contamination
    
    # Physical properties
    composition:
      - "Hydrocarbon chains"
      - "Mineral oils"
    
    # Visual appearance (CRITICAL for image generation)
    visual_characteristics:
      color_range:
        - "Translucent amber"
        - "Dark brown"
        - "Black (aged)"
      texture: "Glossy, wet-looking when fresh; matte and grimy when aged"
      thickness: "Thin film to thick coating (0.1mm-3mm)"
      evolution: "Fresh: glossy/liquid → Aged: dark/sticky → Old: matte/crusty"
      
      # Material-specific appearance modifiers
      appearance_on_materials:
        aluminum:
          description: "Dark patches with rainbow sheen, collects in crevices"
          common_patterns: "Drip marks, fingerprints, splash patterns"
          aged_appearance: "Darkened areas with dust adhesion"
        
        steel:
          description: "Black streaks, promotes rust formation underneath"
          common_patterns: "Tool marks filled with grease, machinery residue"
          aged_appearance: "Brown-black mix with rust bleeding through"
    
    # Material compatibility
    valid_materials:
      - Aluminum
      - Steel
      - Copper
      - Brass
    
    invalid_materials:
      - Glass  # Would just wipe off
      - Ceramics  # Non-porous
    
    # Context requirements
    context_required: true
    valid_contexts:
      - machinery
      - industrial_equipment
      - automotive
    
    # Laser properties (for technical docs)
    laser_properties:
      absorption_coefficient:
        wavelength_1064nm: 3500
      removal_efficiency:
        single_pass: 0.75
```

**Key Additions for Image Generation**:
1. **`visual_characteristics`** - Detailed appearance descriptions
2. **`appearance_on_materials`** - Material-specific visual variations
3. **`evolution`** - How appearance changes over time
4. **`common_patterns`** - Typical distribution patterns

---

### 3. Research Library (NEW REQUIREMENT)

**Location**: `domains/contaminants/research/visual_appearance_researcher.py`

**Purpose**: Use AI (Gemini) to research and populate visual descriptions

```python
class VisualAppearanceResearcher:
    """
    Research how contaminants visually appear on materials.
    
    Uses Gemini API to gather detailed visual descriptions from:
    - Scientific literature
    - Industrial documentation  
    - Photo references
    - Material science databases
    """
    
    def research_contaminant_appearance(
        self,
        contaminant_id: str,
        material_name: str
    ) -> Dict[str, str]:
        """
        Research detailed visual appearance of contaminant on material.
        
        Returns:
            {
                "description": "How it looks on this specific material",
                "color_variations": ["color1", "color2", ...],
                "texture_details": "Detailed texture description",
                "distribution_patterns": "How it spreads/accumulates",
                "aging_progression": "How appearance changes over time",
                "lighting_effects": "How it appears under different lighting"
            }
        """
```

---

## 🔄 Image Generation Workflow

### Step-by-Step Process

**1. Material Selection**
```python
material_name = "Aluminum"
```

**2. Load Material Data**
```python
from domains.materials.data_loader import load_material

material_data = load_material("Aluminum")
# Returns: properties, common_contaminants list
```

**3. Select Contaminant(s)**
```python
contaminants = material_data.get('common_contaminants', [])
# e.g., ['oil-grease', 'dust-dirt', 'paint-coating']

selected = contaminants[0]  # or random selection
```

**4. Load Contaminant Visual Data**
```python
from domains.contaminants.library import get_library

contamination_lib = get_library()
pattern = contamination_lib.get_pattern('oil-grease')

# Get material-specific appearance
appearance = pattern.visual_characteristics.appearance_on_materials.get(
    'aluminum',
    pattern.visual_characteristics  # fallback to generic
)
```

**5. Validate Combination**
```python
from shared.validation.contamination_validator import ContaminationValidator

validator = ContaminationValidator()
result = validator.validate_single_pattern(
    material_name="Aluminum",
    contaminant_id="oil-grease",
    context="machinery"
)

if not result.is_valid:
    raise ValueError(f"Invalid combination: {result.issues}")
```

**6. Build Dynamic Prompt**
```python
from shared.image.prompts.prompt_builder import SharedPromptBuilder

builder = SharedPromptBuilder()

prompt = builder.build_generation_prompt(
    material_name="Aluminum",
    material_properties=material_data['properties'],
    contaminant_data={
        'name': pattern.name,
        'appearance': appearance,
        'visual_characteristics': pattern.visual_characteristics
    },
    config={
        'contamination_level': 3,  # 1-5 scale
        'uniformity': 2,            # 1-5 scale
        'view_mode': 'Contextual',  # or 'Isolated'
        'environment_wear': 3        # 1-5 scale
    }
)
```

**7. Optimize for Imagen Limits**
```python
from shared.image.prompts.prompt_optimizer import PromptOptimizer

optimizer = PromptOptimizer()
optimized_prompt = optimizer.optimize(prompt)

# Ensures:
# - Under 4096 character limit
# - Preserves critical details
# - Maintains scientific accuracy
```

**8. Generate Image**
```python
from shared.api.imagen_client import ImagenClient

client = ImagenClient()
image = client.generate(
    prompt=optimized_prompt,
    aspect_ratio="1:1",
    person_generation="allow_adult",
    safety_filter_level="block_some"
)
```

**9. Log for Learning**
```python
from shared.image.learning import create_logger

logger = create_logger()
logger.log_generation_attempt(
    material_name="Aluminum",
    contaminant_id="oil-grease",
    prompt=optimized_prompt,
    success=True,
    image_path=image.path
)
```

---

## 📝 Prompt Construction Details

### Template Structure

**Location**: `shared/image/prompts/shared/generation/`

**Files**:
1. `base_prompt.txt` - Core realism requirements
2. `material_layer.txt` - Material-specific details
3. `contamination_layer.txt` - Contaminant appearance
4. `lighting_layer.txt` - Lighting and photography
5. `composition_layer.txt` - Framing and context

### Variable Substitution

**From Materials**:
- `{MATERIAL_NAME}` - e.g., "Aluminum"
- `{MATERIAL_COLOR}` - e.g., "Silver-white metallic"
- `{MATERIAL_TEXTURE}` - e.g., "Brushed metal finish"
- `{MATERIAL_HARDNESS}` - e.g., "2.5-3 Mohs"

**From Contaminants**:
- `{CONTAMINANT_NAME}` - e.g., "Oil & Grease"
- `{CONTAMINANT_COLORS}` - e.g., "Translucent amber to dark brown"
- `{CONTAMINANT_TEXTURE}` - e.g., "Glossy when fresh, matte when aged"
- `{CONTAMINANT_PATTERN}` - e.g., "Drip marks and fingerprints"
- `{DISTRIBUTION}` - e.g., "Collects in crevices and low spots"

**From Config**:
- `{CONTAMINATION_LEVEL}` - 1-5 (coverage percentage)
- `{UNIFORMITY}` - 1-5 (single type vs diverse)
- `{VIEW_MODE}` - Contextual (3D) vs Isolated (2D)
- `{ENVIRONMENT_WEAR}` - 1-5 (pristine to heavily used)

### Example Assembled Prompt

```
CONTEXT: Industrial laser cleaning before/after documentation

SUBJECT: Aluminum component with oil and grease contamination

MATERIAL DETAILS:
- Base material: Aluminum, silver-white metallic color
- Surface finish: Brushed metal with directional grain
- Hardness: 2.5-3 Mohs (relatively soft metal)
- Typical use: Machinery housing, industrial equipment

CONTAMINATION:
- Type: Oil & Grease (hydrocarbon-based)
- Appearance on aluminum: Dark patches with rainbow sheen
- Color: Translucent amber to dark brown, aged areas nearly black
- Texture: Glossy/wet-looking in fresh areas, matte and grimy where aged
- Distribution: Collects in crevices, drip marks, fingerprint patterns
- Coverage: 40-60% of visible surface (moderate contamination)
- Age indicators: Some areas dark/sticky, others show dust adhesion

VISUAL REQUIREMENTS:
- Photo-realistic industrial photography style
- Diffuse natural lighting showing contamination clearly
- Sharp focus on contaminated surface details
- Show both fresh (glossy) and aged (matte) contamination areas
- Include typical machinery context (bolts, edges, tool marks)
- Before/after split view showing laser-cleaned vs contaminated areas

COMPOSITION:
- 3D perspective view (contextual mode)
- Object in typical industrial environment
- Background shows moderate wear (level 3/5)
- Natural shadows and depth
- Realistic scale and proportions

TECHNICAL:
- High resolution, professional quality
- Accurate color representation
- Scientific documentation style
- No artistic filters or effects
```

---

## 🧪 Testing Requirements

### Unit Tests

**Location**: `tests/image/test_image_generation_workflow.py`

```python
def test_material_contaminant_lookup():
    """Test looking up associated contaminants from material data"""
    material = load_material("Aluminum")
    assert 'common_contaminants' in material
    assert len(material['common_contaminants']) > 0

def test_contaminant_visual_data():
    """Test loading visual characteristics from contaminants data"""
    lib = get_library()
    pattern = lib.get_pattern('oil-grease')
    
    assert pattern.visual_characteristics is not None
    assert len(pattern.visual_characteristics.color_range) > 0
    assert pattern.visual_characteristics.texture != ""

def test_material_specific_appearance():
    """Test material-specific appearance descriptions"""
    lib = get_library()
    pattern = lib.get_pattern('oil-grease')
    
    aluminum_appearance = pattern.visual_characteristics.appearance_on_materials.get('aluminum')
    assert aluminum_appearance is not None
    assert 'description' in aluminum_appearance

def test_validation_prevents_impossible_combinations():
    """Test that validator rejects physically impossible combinations"""
    validator = ContaminationValidator()
    
    # Rust on aluminum should fail
    result = validator.validate_single_pattern(
        material_name="Aluminum",
        contaminant_id="rust-oxidation",
        context="industrial"
    )
    
    assert not result.is_valid
    assert any(issue.severity == ValidationSeverity.ERROR for issue in result.issues)

def test_prompt_construction():
    """Test dynamic prompt building with material and contaminant data"""
    builder = SharedPromptBuilder()
    
    prompt = builder.build_generation_prompt(
        material_name="Aluminum",
        material_properties={'color': 'silver-white'},
        contaminant_data={'name': 'Oil & Grease', 'appearance': {...}},
        config={'contamination_level': 3}
    )
    
    assert 'Aluminum' in prompt
    assert 'Oil & Grease' in prompt
    assert len(prompt) < 4096  # Imagen limit

def test_imagen_limits_compliance():
    """Test prompt optimizer keeps prompts under Imagen limits"""
    optimizer = PromptOptimizer()
    
    long_prompt = "x" * 5000  # Exceeds limit
    optimized = optimizer.optimize(long_prompt)
    
    assert len(optimized) < 4096
```

### Integration Tests

**Location**: `tests/integration/test_end_to_end_image_generation.py`

```python
def test_full_workflow_aluminum_with_oil():
    """Test complete workflow from material selection to image generation"""
    # 1. Load material
    material = load_material("Aluminum")
    
    # 2. Select contaminant
    contaminant_id = material['common_contaminants'][0]
    
    # 3. Load visual data
    lib = get_library()
    pattern = lib.get_pattern(contaminant_id)
    
    # 4. Validate
    validator = ContaminationValidator()
    result = validator.validate_single_pattern(
        material_name="Aluminum",
        contaminant_id=contaminant_id,
        context="machinery"
    )
    assert result.is_valid
    
    # 5. Build prompt
    builder = SharedPromptBuilder()
    prompt = builder.build_generation_prompt(
        material_name="Aluminum",
        material_properties=material['properties'],
        contaminant_data=pattern,
        config={'contamination_level': 3}
    )
    
    # 6. Optimize
    optimizer = PromptOptimizer()
    optimized = optimizer.optimize(prompt)
    
    # 7. Generate (mock in tests)
    # client = ImagenClient()
    # image = client.generate(optimized)
    
    assert len(optimized) < 4096
    assert 'Aluminum' in optimized
```

---

## 📚 Documentation Requirements

### 1. Contaminants Data Schema

**Location**: `docs/05-data/CONTAMINANTS_SCHEMA.md`

Document the extended schema for visual appearance data:
- `visual_characteristics.appearance_on_materials`
- `visual_characteristics.evolution`
- `visual_characteristics.common_patterns`

### 2. Image Generation API

**Location**: `docs/07-api/IMAGE_GENERATION_API.md`

Document the public API for image generation:
- `MaterialImageGenerator.generate_prompt()`
- `ContaminationLibrary.get_pattern()`
- `ContaminationValidator.validate_single_pattern()`
- `SharedPromptBuilder.build_generation_prompt()`

### 3. Research Library Usage

**Location**: `docs/08-development/VISUAL_APPEARANCE_RESEARCH.md`

Document how to use the research library to populate visual descriptions:
- Running visual appearance research
- Populating Contaminants.yaml with results
- Quality validation of descriptions

---

## 🔐 Security & Safety

### Imagen API Safety

```python
# Safety settings in config
safety_filter_level: "block_some"  # Block harmful content
person_generation: "allow_adult"   # Allow industrial workers
```

### Validation Gates

1. **Material Compatibility** - Prevent physically impossible combinations
2. **Context Validation** - Ensure contamination matches environment
3. **Chemical Safety** - Flag toxic/hazardous combinations
4. **Prompt Safety** - Filter inappropriate content from prompts

### Error Handling

```python
class ImageGenerationError(Exception):
    """Base exception for image generation failures"""

class InvalidContaminantError(ImageGenerationError):
    """Contaminant not valid for this material"""

class PromptTooLongError(ImageGenerationError):
    """Prompt exceeds Imagen character limit"""

class ValidationFailedError(ImageGenerationError):
    """Material-contaminant validation failed"""
```

---

## 📈 Performance Considerations

### Caching Strategy

1. **Material Data** - Cache loaded materials (LRU cache, maxsize=128)
2. **Contaminant Patterns** - Cache library on startup
3. **Prompt Templates** - Load once, reuse for all generations
4. **Research Results** - Persist to database, avoid re-research

### Optimization

1. **Prompt Optimization** - Automatically truncate while preserving details
2. **Batch Generation** - Queue multiple images, process in parallel
3. **Research Reuse** - Share research across materials in same category

---

## 🚀 Future Enhancements

### Phase 1: Visual Research Library ✅ (Required Now)
- Implement `VisualAppearanceResearcher`
- Populate `appearance_on_materials` for all patterns
- Add material-specific visual variations

### Phase 2: Learning System
- Track successful prompts and configurations
- A/B test different prompt structures
- Optimize based on human feedback

### Phase 3: Multi-Contaminant Images
- Support 2-5 contaminants on one material
- Research interaction effects (rust + oil, etc.)
- Complex layering and distribution

### Phase 4: Animation/Video
- Before/after transition animations
- Laser cleaning process visualization
- Time-lapse contamination formation

---

## 📞 Related Documentation

- `IMAGE_GENERATION_API.md` - Public API reference
- `CONTAMINANTS_SCHEMA.md` - Data structure details
- `VISUAL_APPEARANCE_RESEARCH.md` - Research library guide
- `DOMAIN_INDEPENDENCE_POLICY.md` - Architecture boundaries
- `DATA_STORAGE_POLICY.md` - Where data lives

---

**Last Updated**: November 26, 2025  
**Maintained By**: AI Assistant  
**Review Frequency**: After major image generation changes
