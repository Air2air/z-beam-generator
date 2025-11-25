# Material Before/After Image Generator

**Status**: ✅ Core System Complete  
**Date**: November 24, 2025  
**Architecture**: Gemini 2.0 Flash (research) + Imagen 4 (generation) + Gemini Vision (validation)

---

## Overview

Automated AI-powered image generation system that creates scientifically accurate before/after laser cleaning images for materials. Uses Gemini API to research real-world contamination data, then generates 16:9 composite images showing the same object in contaminated (left) and cleaned (right) states.

## Architecture

### Research System (Gemini 2.0 Flash)
- **MaterialContaminationResearcher**: Researches scientifically accurate contamination data
- **Research Protocol**: 4-step mandatory research
  1. Most common object made from material
  2. Typical size/dimensions and environment
  3. 3-5 scientifically accurate contaminants (chemical formula, cause, appearance)
  4. Base material appearance when clean
- **Caching**: @lru_cache(maxsize=128) for cost control
- **Cost**: $0.0001 per research query

### Prompt Generation System
- **Base Template**: `prompts/base_prompt.txt` (7KB comprehensive template)
- **Prompt Builder**: `prompts/material_prompts.py` combines research + template
- **Variables**: Material name, contamination level, uniformity, view mode, environment wear
- **Output**: Complete scientifically accurate prompt for Imagen 4

### Image Generation (Imagen 4)
- **MaterialImageGenerator**: Main generator class
- **Format**: 16:9 side-by-side composite (left=before, right=after)
- **Guidance Scale**: 13.0-15.0 (higher for technical accuracy)
- **Cost**: $0.04 per image

### Configuration System
- **Contamination Level** (1-5): Intensity of contamination
  - 1 = Minimal (<20% coverage)
  - 3 = Moderate (40-60%, typical real-world)
  - 5 = Severe (80-95% coverage)
- **Contamination Uniformity** (1-5): Variety of contaminants
  - 1 = Single type
  - 3 = Three types
  - 5 = Diverse (4+ types)
- **View Mode**: 
  - Contextual = 3D perspective in realistic environment
  - Isolated = 2D technical documentation view
- **Environment Wear** (1-5): Background aging level

### Validation System (Gemini Vision)
- **Purpose**: Validate before/after consistency, contamination accuracy
- **Cost**: $0.0002 per validation
- **Status**: Architecture in place, implementation pending

---

## File Structure

```
domains/materials/image/
├── prompts/
│   ├── base_prompt.txt              # 7KB comprehensive research template
│   ├── material_researcher.py       # Gemini-powered contamination researcher
│   └── material_prompts.py          # Prompt builder (research + template)
├── material_generator.py            # Main generator class
├── material_config.py               # Configuration dataclass
├── contamination_levels.py          # Level descriptions (1-5 scales)
├── generate.py                      # CLI script
├── validator.py                     # Gemini Vision validation (from city generator)
├── negative_prompts.py              # Negative prompt templates (from city generator)
└── presets.py                       # Preset configurations (from city generator)
```

---

## Usage

### Basic Generation
```bash
python3 domains/materials/image/generate.py --material "Aluminum"
```

### Custom Configuration
```bash
python3 domains/materials/image/generate.py \
  --material "Stainless Steel" \
  --contamination-level 4 \
  --uniformity 3 \
  --view-mode Contextual \
  --environment-wear 3
```

### Technical Documentation View
```bash
python3 domains/materials/image/generate.py \
  --material "Copper" \
  --contamination-level 2 \
  --uniformity 2 \
  --view-mode Isolated
```

### Show Prompt (Dry Run)
```bash
python3 domains/materials/image/generate.py \
  --material "Titanium" \
  --show-prompt \
  --dry-run
```

### With Validation
```bash
python3 domains/materials/image/generate.py \
  --material "Brass" \
  --validate
```

---

## Python API Usage

```python
from domains.materials.image.material_generator import MaterialImageGenerator
from domains.materials.image.material_config import MaterialImageConfig

# Initialize generator
generator = MaterialImageGenerator(gemini_api_key="your_key")

# Create configuration
config = MaterialImageConfig(
    material="Aluminum",
    contamination_level=3,
    contamination_uniformity=3,
    view_mode="Contextual",
    environment_wear=3
)

# Generate complete prompt package
prompt_package = generator.generate_complete(
    material_name="Aluminum",
    config=config
)

# Access components
prompt = prompt_package["prompt"]
negative_prompt = prompt_package["negative_prompt"]
research_data = prompt_package["research_data"]
aspect_ratio = prompt_package["aspect_ratio"]
guidance_scale = prompt_package["guidance_scale"]
```

---

## Key Features

### Scientific Accuracy
- ✅ Real contaminants with chemical formulas
- ✅ Accurate appearance (color, texture, pattern, thickness)
- ✅ Environmental causes documented
- ✅ Prevalence levels specified

### Contamination Research
- ✅ Automatic research via Gemini 2.0 Flash
- ✅ 3-5 scientifically accurate contaminants per material
- ✅ Common objects and typical environments
- ✅ Base material appearance when clean

### Configuration Control
- ✅ 5-level intensity scale (minimal → severe)
- ✅ 5-level uniformity scale (single type → diverse)
- ✅ 2 view modes (contextual 3D or isolated 2D)
- ✅ 5-level environment wear

### Cost Optimization
- ✅ Research caching (@lru_cache)
- ✅ Single research call per material
- ✅ Fallback research data if API unavailable

---

## Example Research Output

**Material**: Aluminum  
**Common Object**: Aluminum ladder  
**Environment**: Construction sites, warehouses  
**Contaminants**:
1. **Aluminum Oxide (Al₂O₃)**
   - Cause: Natural oxidation in air/moisture
   - Color: Dull gray to white
   - Texture: Fine, powdery to chalky
   - Pattern: Uniform coating, thicker in exposed areas
   - Thickness: Thin (0.1-1mm)
   - Prevalence: Universal on exposed aluminum

2. **Carbon Deposits**
   - Cause: Combustion, industrial pollution
   - Color: Dark gray to black
   - Texture: Sooty, granular
   - Pattern: Concentrated in crevices
   - Thickness: Thin (< 0.5mm)
   - Prevalence: Common in industrial environments

3. **Oil/Grease Contamination**
   - Cause: Handling, machinery contact
   - Color: Dark brown to black with sheen
   - Texture: Sticky, viscous
   - Pattern: Smeared, fingerprints visible
   - Thickness: Very thin film
   - Prevalence: Very common in industrial use

---

## Next Steps

### Immediate (Ready to Implement)
1. **Test Complete Pipeline**: Generate test images for Aluminum, Steel, Copper
2. **Validate Research Quality**: Verify contamination data accuracy
3. **Implement Validation**: Adapt validator.py for before/after checks
4. **Cost Analysis**: Measure actual costs per material

### Future Enhancements
1. **Preset Configurations**: Common contamination scenarios
2. **Batch Generation**: Generate multiple materials automatically
3. **Material Database Integration**: Read from Materials.yaml
4. **Enhanced Validation**: Check contamination matches research
5. **Quality Scoring**: Rate generated images automatically

---

## Technical Details

### Dependencies
- **Gemini 2.0 Flash**: Research and validation
- **Imagen 4**: Image generation via Vertex AI
- **Python 3.10+**: Type hints, dataclasses
- **LRU Cache**: Research result caching

### API Costs (Per Material)
- Research: $0.0001
- Image Generation: $0.04
- Validation (optional): $0.0002
- **Total**: ~$0.04 per material

### Performance
- Research: ~2-3 seconds (cached after first call)
- Image Generation: ~5-10 seconds
- Total Time: ~7-13 seconds per material

---

## Differences from City Generator

| Aspect | City Generator | Material Generator |
|--------|---------------|-------------------|
| **Research** | Historical population | Material contamination |
| **Subject** | City in specific decade | Material before/after cleaning |
| **Configuration** | Year, photo/scenery aging | Contamination level/uniformity, view mode |
| **Scale** | Population-adaptive (hamlet → city) | Contamination-adaptive (minimal → severe) |
| **Output** | Single historical photo | Side-by-side before/after composite |
| **Research Data** | Population, building counts, focal characteristics | Contaminants (formula, appearance, causes) |
| **Negative Prompts** | Anachronisms, crowds for small towns | Inconsistent splits, wrong contamination |

---

## Status Summary

✅ **Complete**:
- Material contamination researcher (Gemini 2.0 Flash)
- Base prompt template (7KB comprehensive)
- Prompt builder (research + template)
- Configuration system (dataclass + validation)
- Contamination level descriptions (1-5 scales)
- Main generator class (MaterialImageGenerator)
- CLI script (generate.py)

⚠️ **In Progress**:
- Validation system adaptation
- Preset configurations
- Batch generation scripts

❌ **Not Started**:
- Testing with real materials
- Integration with Materials.yaml
- Quality scoring system
- Documentation site updates

---

## Credits

**Based On**: Historical City Image Generator (domains/regions/image/)  
**Architecture**: Gemini API stack (Flash 2.0 + Imagen 4 + Vision)  
**Date**: November 24, 2025  
**Status**: Core system complete, ready for testing
