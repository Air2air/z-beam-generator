# Image Generation Implementation Checklist

**Date**: November 26, 2025  
**Status**: 📋 REQUIREMENTS DOCUMENTED  
**Priority**: HIGH - Core functionality for image generation

---

## ✅ Already Implemented

### Shared Infrastructure
- ✅ `shared/image/utils/prompt_builder.py` - Template loading
- ✅ `shared/image/utils/prompt_optimizer.py` - Imagen limit enforcement
- ✅ `shared/image/learning/image_generation_logger.py` - Generation tracking
- ✅ `shared/validation/contamination_validator.py` - Material compatibility validation
- ✅ `shared/types/contamination_levels.py` - Contamination level descriptions

### Materials Domain
- ✅ `domains/materials/image/material_generator.py` - Image generation orchestration
- ✅ `domains/materials/image/research/shape_researcher.py` - Material/shape research
- ✅ `domains/materials/image/research/contamination_pattern_selector.py` - Category/material pattern research
- ✅ `domains/materials/image/material_config.py` - Configuration dataclass

### Contaminants Domain
- ✅ `domains/contaminants/models.py` - Data models (ContaminantPattern, VisualCharacteristics)
- ✅ `domains/contaminants/library.py` - Pattern library and loading
- ✅ `domains/contaminants/validator.py` - Material-contaminant validation
- ✅ `data/contaminants/Contaminants.yaml` - Contamination pattern data

---

## 🚧 To Be Implemented

### Phase 1: Material-Contaminant Associations (REQUIRED)

**1.1 Extend Materials.yaml Structure**

**File**: `data/materials/Materials.yaml`

Add `common_contaminants` field to each material:

```yaml
materials:
  Aluminum:
    properties:
      # ... existing properties ...
    
    # NEW FIELD: Associated contaminants for image generation
    common_contaminants:
      - oil-grease
      - dust-dirt
      - paint-coating
      - carbon-deposits
      - water-stains
    
    # Explicitly prohibited contaminants (physically impossible)
    prohibited_contaminants:
      - rust-oxidation  # No iron in aluminum
      - wood-rot        # Not organic material
```

**Estimated Work**: 2-3 hours to add for all materials

---

**1.2 Populate Common Contaminants**

**Script**: `scripts/research/populate_material_contaminants.py` (NEW)

Create script to research and populate common contaminants for each material:

```python
#!/usr/bin/env python3
"""
Populate Material Contaminants

Research and populate common_contaminants field for each material
using Gemini API to identify realistic contamination patterns.
"""

from domains.materials.data_loader import load_materials_data, save_materials_data
import google.generativeai as genai

def research_common_contaminants(material_name: str, properties: dict) -> list:
    """
    Research common contaminants for a material using AI.
    
    Returns list of contaminant IDs from Contaminants.yaml
    """
    # Query Gemini for realistic contaminants based on:
    # - Material properties
    # - Industrial applications
    # - Environmental exposure
    pass

def populate_all_materials():
    """Populate common_contaminants for all materials"""
    materials = load_materials_data()
    
    for material_name, material_data in materials['materials'].items():
        if 'common_contaminants' not in material_data:
            contaminants = research_common_contaminants(
                material_name, 
                material_data.get('properties', {})
            )
            material_data['common_contaminants'] = contaminants
    
    save_materials_data(materials)
```

**Estimated Work**: 4-6 hours

---

### Phase 2: Visual Appearance Descriptions (REQUIRED)

**2.1 Extend Contaminants.yaml Structure**

**File**: `data/contaminants/Contaminants.yaml`

Add material-specific visual descriptions:

```yaml
contamination_patterns:
  oil-grease:
    id: oil-grease
    name: "Oil & Grease Contamination"
    
    # ... existing fields ...
    
    visual_characteristics:
      color_range:
        - "Translucent amber"
        - "Dark brown"
        - "Black (aged)"
      texture: "Glossy, wet-looking when fresh; matte and grimy when aged"
      thickness: "Thin film to thick coating (0.1mm-3mm)"
      
      # NEW: Time-based evolution
      evolution: "Fresh: glossy/liquid → Aged: dark/sticky → Old: matte/crusty"
      
      # NEW: Material-specific appearances
      appearance_on_materials:
        aluminum:
          description: "Dark patches with rainbow sheen, collects in crevices"
          common_patterns: "Drip marks, fingerprints, splash patterns"
          aged_appearance: "Darkened areas with dust adhesion"
          lighting_effects: "Shows iridescent colors under direct light"
        
        steel:
          description: "Black streaks, promotes rust formation underneath"
          common_patterns: "Tool marks filled with grease, machinery residue"
          aged_appearance: "Brown-black mix with rust bleeding through"
          lighting_effects: "Matte finish, minimal reflection"
        
        copper:
          description: "Dark brown coating, inhibits patina formation"
          common_patterns: "Fingerprints, handling marks, pooled areas"
          aged_appearance: "Nearly black, thick and tacky"
          lighting_effects: "No sheen, absorbs light"
```

**Estimated Work**: 8-12 hours to extend all patterns

---

**2.2 Visual Appearance Research Library**

**File**: `domains/contaminants/research/visual_appearance_researcher.py` (NEW)

Create AI-powered research library:

```python
#!/usr/bin/env python3
"""
Visual Appearance Researcher

Uses Gemini API to research detailed visual descriptions of how
contaminants appear on specific materials.

Gathers information from:
- Scientific literature
- Industrial documentation
- Photo references
- Material science databases
"""

import google.generativeai as genai
from typing import Dict
from functools import lru_cache

class VisualAppearanceResearcher:
    """Research visual appearance of contaminants on materials"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    @lru_cache(maxsize=256)
    def research_appearance_on_material(
        self,
        contaminant_id: str,
        contaminant_name: str,
        material_name: str,
        material_properties: Dict
    ) -> Dict[str, str]:
        """
        Research how contaminant appears on specific material.
        
        Returns:
            {
                "description": "Detailed visual description",
                "common_patterns": "How it distributes/accumulates",
                "aged_appearance": "How it looks after aging",
                "lighting_effects": "Appearance under different lighting",
                "texture_details": "Fine-grained texture information",
                "color_variations": "Color range specific to this material"
            }
        """
        
        prompt = f"""
        Research the visual appearance of {contaminant_name} on {material_name}.
        
        Material properties: {material_properties}
        
        Provide detailed visual description including:
        1. Overall appearance (color, texture, sheen)
        2. Common distribution patterns (drips, stains, uniform coating, etc.)
        3. How appearance changes with age/time
        4. How it looks under different lighting conditions
        5. Fine texture details visible at close inspection
        6. Color variations specific to this material combination
        
        Focus on photo-realistic details needed for AI image generation.
        Use concrete, visual language. Avoid abstract descriptions.
        """
        
        # Call Gemini API
        response = self.model.generate_content(prompt)
        
        # Parse and structure response
        # ... implementation ...
        
        return result
```

**Estimated Work**: 6-8 hours

---

**2.3 Population Script**

**File**: `scripts/research/populate_visual_appearances.py` (NEW)

```python
#!/usr/bin/env python3
"""
Populate Visual Appearances

Use VisualAppearanceResearcher to populate appearance_on_materials
for all contaminant-material combinations.
"""

from domains.contaminants.library import get_library
from domains.contaminants.research.visual_appearance_researcher import VisualAppearanceResearcher
from domains.materials.data_loader import load_materials_data
import yaml

def populate_all_appearances():
    """Research and populate visual appearances for all combinations"""
    
    researcher = VisualAppearanceResearcher(api_key=os.getenv("GEMINI_API_KEY"))
    lib = get_library()
    materials = load_materials_data()
    
    # Load contaminants data
    with open('data/contaminants/Contaminants.yaml', 'r') as f:
        contaminants_data = yaml.safe_load(f)
    
    # For each contaminant pattern
    for pattern_id, pattern_data in contaminants_data['contamination_patterns'].items():
        valid_materials = pattern_data.get('valid_materials', [])
        
        # Research appearance on each valid material
        for material_name in valid_materials:
            material_props = materials['materials'].get(material_name, {}).get('properties', {})
            
            appearance = researcher.research_appearance_on_material(
                contaminant_id=pattern_id,
                contaminant_name=pattern_data['name'],
                material_name=material_name,
                material_properties=material_props
            )
            
            # Add to contaminants data
            if 'appearance_on_materials' not in pattern_data['visual_characteristics']:
                pattern_data['visual_characteristics']['appearance_on_materials'] = {}
            
            pattern_data['visual_characteristics']['appearance_on_materials'][material_name.lower()] = appearance
            
            print(f"✅ Researched: {pattern_data['name']} on {material_name}")
    
    # Save updated data
    with open('data/contaminants/Contaminants.yaml', 'w') as f:
        yaml.dump(contaminants_data, f, default_flow_style=False, allow_unicode=True)
```

**Estimated Work**: 3-4 hours

---

### Phase 3: Prompt Construction Enhancements (OPTIONAL)

**3.1 Material-Specific Prompt Templates**

**Prompt catalog entry**: `prompts/shared/generation/material_specific_layer.txt` (in `prompts/registry/prompt_catalog.yaml`)

Create template that uses material-specific appearance data:

```
CONTAMINATION APPEARANCE ON {MATERIAL_NAME}:
- Base description: {APPEARANCE_DESCRIPTION}
- Distribution: {COMMON_PATTERNS}
- Aging effects: {AGED_APPEARANCE}
- Under lighting: {LIGHTING_EFFECTS}
- Texture details: {TEXTURE_DETAILS}
- Color variations: {COLOR_VARIATIONS}
```

**Estimated Work**: 2-3 hours

---

**3.2 Update SharedPromptBuilder**

**File**: `shared/image/utils/prompt_builder.py`

Enhance to use material-specific appearance data:

```python
def build_generation_prompt(
    self,
    material_name: str,
    material_properties: Dict,
    contaminant_data: Dict,
    config: Dict
) -> str:
    """
    Build dynamic prompt from material and contaminant data.
    
    NEW: Uses appearance_on_materials if available
    """
    
    # Load base template
    template = self._load_template('generation/base_prompt.txt')
    
    # Get material-specific appearance if available
    contaminant_id = contaminant_data.get('id')
    material_name_lower = material_name.lower()
    
    appearance = contaminant_data.get('visual_characteristics', {}).get(
        'appearance_on_materials', {}
    ).get(material_name_lower, {})
    
    # Use material-specific appearance, fallback to generic
    if appearance:
        appearance_desc = appearance.get('description')
        patterns = appearance.get('common_patterns')
        aged = appearance.get('aged_appearance')
        lighting = appearance.get('lighting_effects')
    else:
        # Fallback to generic visual characteristics
        vc = contaminant_data.get('visual_characteristics', {})
        appearance_desc = f"Colors: {', '.join(vc.get('color_range', []))}, Texture: {vc.get('texture', '')}"
        patterns = "General contamination patterns"
        aged = "Darkens and accumulates over time"
        lighting = "Typical contamination appearance"
    
    # Build prompt with substitutions
    # ... rest of implementation ...
```

**Estimated Work**: 3-4 hours

---

### Phase 4: Testing & Validation (REQUIRED)

**4.1 Run Workflow Tests**

```bash
pytest tests/image/test_image_generation_workflow.py -v
```

**Expected Results**:
- All material-contaminant lookups pass
- Visual data loading works
- Validation prevents impossible combinations
- Prompts construct properly with material-specific data
- Imagen limits enforced

**Estimated Work**: 2-3 hours

---

**4.2 Integration Testing**

Test complete workflow for representative materials:
- Aluminum + oil-grease
- Steel + rust-oxidation  
- Copper + patina
- Plastic + UV-chalking

**Estimated Work**: 2-3 hours

---

## 📊 Total Effort Estimate

| Phase | Description | Hours | Priority |
|-------|-------------|-------|----------|
| 1.1 | Extend Materials.yaml | 2-3 | P0 - Required |
| 1.2 | Populate contaminants script | 4-6 | P0 - Required |
| 2.1 | Extend Contaminants.yaml | 8-12 | P0 - Required |
| 2.2 | Visual research library | 6-8 | P0 - Required |
| 2.3 | Population script | 3-4 | P0 - Required |
| 3.1 | Material-specific templates | 2-3 | P1 - Nice to have |
| 3.2 | Enhance prompt builder | 3-4 | P1 - Nice to have |
| 4.1 | Workflow testing | 2-3 | P0 - Required |
| 4.2 | Integration testing | 2-3 | P0 - Required |
| **TOTAL** | **All phases** | **33-46 hours** | **~1 week** |

---

## 🎯 Minimum Viable Implementation

**Required for basic functionality** (25-31 hours):
1. Phase 1: Material-contaminant associations (6-9 hours)
2. Phase 2: Visual appearance descriptions (17-24 hours)
3. Phase 4: Testing (4-6 hours)

**Can defer** (8-15 hours):
- Phase 3: Prompt construction enhancements (use generic fallbacks initially)

---

## 📋 Implementation Order

1. ✅ **Documentation** - COMPLETE (this file + architecture doc)
2. 🔄 **Phase 1.1** - Extend Materials.yaml structure
3. 🔄 **Phase 2.1** - Extend Contaminants.yaml structure
4. 🔄 **Phase 2.2** - Build visual research library
5. 🔄 **Phase 1.2** - Populate material contaminants
6. 🔄 **Phase 2.3** - Populate visual appearances
7. 🔄 **Phase 3.2** - Update prompt builder to use new data
8. 🔄 **Phase 4** - Test complete workflow

---

## 🚀 Quick Start

**To implement Phase 1.1**:
```bash
# Edit data/materials/Materials.yaml
# Add common_contaminants field to each material
```

**To implement Phase 2.2**:
```bash
# Create new file
touch domains/contaminants/research/visual_appearance_researcher.py

# Implement VisualAppearanceResearcher class
# Test with single material-contaminant pair
python3 -c "from domains.contaminants.research.visual_appearance_researcher import VisualAppearanceResearcher; ..."
```

---

**Last Updated**: November 26, 2025  
**Next Review**: After Phase 1 completion
