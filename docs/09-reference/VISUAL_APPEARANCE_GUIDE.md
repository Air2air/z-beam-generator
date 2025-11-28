# Visual Appearance Research - Setup Guide

**Status**: ✅ Implementation Complete  
**Date**: November 26, 2025

## Overview

The Visual Appearance Research system uses **Gemini 2.0 Flash API** to generate detailed, material-specific descriptions of how contamination patterns look on different metals. This enables photo-realistic AI image generation.

## What Was Implemented

### 1. Core Research Engine
**File**: `domains/contaminants/research/visual_appearance_researcher.py`

```python
class VisualAppearanceResearcher:
    """
    AI-powered research for visual contamination characteristics.
    
    Uses Gemini 2.0 Flash to generate 8 detailed visual aspects:
    - description: Overall appearance
    - color_variations: Fresh to aged color changes
    - texture_details: Surface texture (glossy, matte, rough, etc.)
    - common_patterns: Distribution patterns (drips, pools, streaks)
    - aged_appearance: Time-based evolution
    - lighting_effects: Appearance under different lighting
    - thickness_range: Measurements (0.05mm to 5mm)
    - distribution_factors: What affects accumulation
    """
```

**Features**:
- ✅ Gemini 2.0 Flash integration (temperature=0.3 for accuracy)
- ✅ LRU cache (256 entries) for efficiency
- ✅ JSON-structured responses
- ✅ Batch processing support
- ✅ Error handling with fallback
- ✅ YAML formatting for direct insertion

### 2. CLI Research Script
**File**: `scripts/research/populate_visual_appearances.py`

```bash
# Single pattern research
python3 scripts/research/populate_visual_appearances.py --pattern oil-grease

# All patterns
python3 scripts/research/populate_visual_appearances.py --all

# Custom materials
python3 scripts/research/populate_visual_appearances.py \
  --pattern rust-oxidation \
  --materials "Steel,Iron,Cast Iron"

# Force re-research existing data
python3 scripts/research/populate_visual_appearances.py --pattern oil-grease --force
```

**Features**:
- ✅ Auto-backup before modifications (`.yaml.backup`)
- ✅ Incremental save (won't lose progress if interrupted)
- ✅ Skip-existing logic (won't re-research unless `--force`)
- ✅ Progress tracking (X/Y successful)
- ✅ Error recovery (continues on failure)
- ✅ Multiple operation modes (single, batch, custom)

### 3. Demo Script
**File**: `scripts/research/demo_visual_appearance_research.py`

```bash
# See what the research produces (no API key needed)
python3 scripts/research/demo_visual_appearance_research.py
```

Shows:
- Example input (pattern + material)
- Research process steps
- Example output (8 visual fields)
- YAML format for Contaminants.yaml
- Impact on image generation

---

## Setup Instructions

### Step 1: Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)

### Step 2: Set Environment Variable

**Temporary (current terminal session only)**:
```bash
export GEMINI_API_KEY="your_api_key_here"
```

**Permanent (add to ~/.bash_profile or ~/.zshrc)**:
```bash
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.bash_profile
source ~/.bash_profile
```

**Verify**:
```bash
echo $GEMINI_API_KEY
# Should output: your_api_key_here
```

### Step 3: Test Research (Single Pattern)

```bash
# Research oil-grease on valid materials
python3 scripts/research/populate_visual_appearances.py --pattern oil-grease
```

**Expected Output**:
```
🔍 Loading Contaminants.yaml...
✅ Loaded 15 contamination patterns

📋 Researching pattern: oil-grease
   Materials: Aluminum, Steel, Copper, Brass, Titanium

[1/5] Researching appearance on Aluminum...
   🔬 Querying Gemini API...
   ✅ Success - 8 visual aspects documented

[2/5] Researching appearance on Steel...
   🔬 Querying Gemini API...
   ✅ Success - 8 visual aspects documented

...

✅ Research complete: 5/5 successful
💾 Saving to domains/contaminants/Contaminants.yaml
✅ Saved successfully

✨ Next: Check Contaminants.yaml for populated appearance_on_materials data
```

### Step 4: Verify Results

```bash
# Check that appearance_on_materials was populated
grep -A 20 "appearance_on_materials:" domains/contaminants/Contaminants.yaml
```

**Expected Structure**:
```yaml
visual_characteristics:
  appearance_on_materials:
    aluminum:
      description: "Oil and grease on aluminum appears as dark..."
      color_variations: "Fresh: Translucent amber to light brown..."
      texture_details: "Fresh oil is smooth and glossy..."
      common_patterns: "Forms drip marks from vertical surfaces..."
      aged_appearance: "Fresh (hours-days): Glossy, liquid-like..."
      lighting_effects: "Under direct sunlight: Shows prominent..."
      thickness_range: "Thin film: 0.05-0.2mm (barely visible)..."
      distribution_factors: "Gravity causes dripping and pooling..."
    steel:
      description: "..."
      # ... (8 fields per material)
```

### Step 5: Run Batch Research (All Patterns)

```bash
# Research ALL contamination patterns
python3 scripts/research/populate_visual_appearances.py --all
```

**This will**:
- Research all patterns in Contaminants.yaml
- Skip patterns that already have appearance_on_materials data
- Save incrementally (won't lose progress)
- Create backup before modifications
- Take 5-10 minutes (depends on number of patterns × materials)

---

## Usage Examples

### Research Specific Pattern
```bash
python3 scripts/research/populate_visual_appearances.py \
  --pattern rust-oxidation
```

### Research With Custom Materials
```bash
python3 scripts/research/populate_visual_appearances.py \
  --pattern paint-coating \
  --materials "Aluminum,Steel,Galvanized Steel"
```

### Force Re-research Existing Data
```bash
python3 scripts/research/populate_visual_appearances.py \
  --pattern oil-grease \
  --force
```

### Research With Inline API Key
```bash
python3 scripts/research/populate_visual_appearances.py \
  --pattern oil-grease \
  --api-key "your_api_key_here"
```

---

## Data Structure

### Input: Contamination Pattern (from Contaminants.yaml)
```yaml
- id: oil-grease
  name: "Oil & Grease Contamination"
  chemical_composition:
    primary_compounds:
      - Hydrocarbon chains
      - Mineral oils
  # ... other fields
```

### Output: Material-Specific Visual Descriptions
```yaml
- id: oil-grease
  name: "Oil & Grease Contamination"
  visual_characteristics:
    appearance_on_materials:
      aluminum:
        description: "Oil and grease on aluminum appears as dark, irregular patches with a distinctive rainbow sheen under direct light. Fresh contamination is translucent amber to brown, while aged deposits darken to near-black."
        
        color_variations: "Fresh: Translucent amber to light brown with rainbow iridescence. Moderately aged (weeks): Dark brown with reduced sheen. Heavily aged (months): Nearly black with matte finish."
        
        texture_details: "Fresh oil is smooth and glossy with liquid-like appearance. As it ages, it becomes increasingly sticky and tacky to touch. Old deposits are matte, grimy, and may feel waxy or crusty."
        
        common_patterns: "Forms drip marks from vertical surfaces, pooling at edges and in recessed areas. Fingerprints and handling marks are clearly visible."
        
        aged_appearance: "Fresh (hours-days): Glossy, liquid-like, amber to brown, strong rainbow sheen. Moderate age (weeks): Darker brown, reduced gloss, slightly tacky. Heavy age (months+): Nearly black, completely matte, crusty edges."
        
        lighting_effects: "Under direct sunlight: Shows prominent rainbow iridescence (fresh oil) or dull matte black (aged). Under fluorescent lighting: Fresh appears glossy with less pronounced colors."
        
        thickness_range: "Thin film: 0.05-0.2mm (barely visible, slight darkening). Moderate: 0.2-1mm (clearly visible, drip marks). Heavy: 1-5mm (thick pools, crusty edges)."
        
        distribution_factors: "Gravity causes dripping and pooling in low areas. Mechanical contact deposits oil via tools and handling. Heat from machinery causes oil to flow and spread."
      
      steel:
        # ... (8 fields for steel)
      
      copper:
        # ... (8 fields for copper)
```

---

## Integration With Image Generation

### Before Research
```python
# Generic prompt (not material-specific)
prompt = "Show oil and grease contamination"
# Result: Generic, unrealistic image
```

### After Research
```python
# Material-specific prompt
prompt = f"""
Photo of aluminum surface with oil contamination:
- Color: Dark brown with rainbow iridescence
- Texture: Glossy liquid-like fresh deposits
- Pattern: Drip marks from top, fingerprints visible
- Distribution: Pools in crevices and corners
- Lighting: Rainbow sheen under direct light
"""
# Result: Photo-realistic, scientifically accurate image
```

---

## Troubleshooting

### Error: `GEMINI_API_KEY not set`
**Solution**: Export API key as environment variable
```bash
export GEMINI_API_KEY="your_key_here"
```

### Error: `API quota exceeded`
**Solution**: Wait or upgrade Gemini API plan  
- Free tier: 60 requests/minute
- Check quota: [Google AI Studio](https://aistudio.google.com/app/apikey)

### Error: `Pattern 'xyz' not found`
**Solution**: Check pattern exists in Contaminants.yaml
```bash
grep "id:" domains/contaminants/Contaminants.yaml
```

### Error: `Invalid material 'xyz'`
**Solution**: Use valid materials from Materials.yaml
```bash
grep "^- name:" data/materials/Materials.yaml
```

### Incomplete Research (interrupted)
**Solution**: Re-run with same command - script skips existing data
```bash
python3 scripts/research/populate_visual_appearances.py --all
# Will skip patterns that already have appearance_on_materials
```

### Want to Re-research Existing Data
**Solution**: Use `--force` flag
```bash
python3 scripts/research/populate_visual_appearances.py --pattern oil-grease --force
```

---

## Next Steps

### 1. Execute Research ⏳
```bash
# Test with single pattern
python3 scripts/research/populate_visual_appearances.py --pattern oil-grease

# Then run full batch
python3 scripts/research/populate_visual_appearances.py --all
```

### 2. Populate Materials.yaml ⏳
Add `common_contaminants` field to each material:
```yaml
- name: Aluminum
  common_contaminants:
    - oil-grease
    - paint-coating
    - adhesive-residue
```

**Script**: Need to create `scripts/research/populate_material_contaminants.py`  
**Estimated**: 4-6 hours (documented in IMAGE_GENERATION_IMPLEMENTATION_CHECKLIST.md)

### 3. Update Prompt Builder ⏳
Modify `shared/image/prompts/prompt_builder.py` to use material-specific appearance data:
```python
def build_generation_prompt(self, material_name, contaminant_id):
    # Check for material-specific appearance
    if contaminant_id in appearance_on_materials:
        if material_name in appearance_on_materials[contaminant_id]:
            appearance = appearance_on_materials[contaminant_id][material_name]
            # Use detailed description
        else:
            # Fallback to generic visual_characteristics
    # ...
```

**Estimated**: 3-4 hours

### 4. Integration Testing ⏳
Run complete workflow tests:
```bash
pytest tests/image/test_image_generation_workflow.py -v
```

**Expected**: All 45 tests pass with populated data

---

## Files Reference

### Implementation Files
- `domains/contaminants/research/visual_appearance_researcher.py` - Core research engine (313 lines)
- `scripts/research/populate_visual_appearances.py` - CLI script (286 lines)
- `scripts/research/demo_visual_appearance_research.py` - Demo workflow (no API key needed)

### Documentation Files
- `docs/08-development/IMAGE_GENERATION_ARCHITECTURE.md` - Complete system architecture (25 pages)
- `docs/08-development/IMAGE_GENERATION_IMPLEMENTATION_CHECKLIST.md` - 4-phase implementation plan (33-46 hours)
- `tests/image/test_image_generation_workflow.py` - 45 test cases

### Data Files
- `domains/contaminants/Contaminants.yaml` - Input/output (gets populated with appearance_on_materials)
- `data/materials/Materials.yaml` - Valid materials list

---

## API Configuration

### Model Settings
- **Model**: `gemini-2.0-flash-exp`
- **Temperature**: `0.3` (factual accuracy)
- **Max Tokens**: `2048`
- **Response Format**: JSON

### Rate Limits (Free Tier)
- **Requests**: 60 per minute
- **Tokens**: 2 million per day
- **Storage**: None (stateless)

### Upgrade Options
- **Pay-as-you-go**: Higher rate limits
- **Check pricing**: [Google AI Pricing](https://ai.google.dev/pricing)

---

## Summary

✅ **Implementation Complete**: Both research engine and CLI script ready  
⏳ **API Key Needed**: Set `GEMINI_API_KEY` environment variable  
⏳ **Ready to Execute**: Run test research, then batch populate  

**Immediate Action**:
```bash
export GEMINI_API_KEY="your_key_here"
python3 scripts/research/populate_visual_appearances.py --pattern oil-grease
```

This will populate detailed, photo-realistic visual descriptions for AI image generation.
