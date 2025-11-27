# Visual Appearance Research - ALL Material Categories

**Date**: November 26, 2025  
**Status**: ✅ Implementation Complete - All 159 Materials Supported

---

## 🌍 Full Material Coverage

The enhanced visual appearance research system now supports **ALL 159 materials across 10 categories** from Materials.yaml:

### Material Categories (Total: 159 materials)

| Category | Count | Examples |
|----------|-------|----------|
| **Metal** | 45 | Aluminum, Steel, Copper, Brass, Titanium, Bronze, Cast Iron, Stainless Steel, Gold, Silver... |
| **Wood** | 21 | Oak, Maple, Pine, Cherry, Walnut, Mahogany, Teak, Cedar, Bamboo, MDF... |
| **Stone** | 20 | Granite, Marble, Limestone, Sandstone, Slate, Travertine, Basalt, Quartzite... |
| **Ceramic** | 13 | Alumina, Silicon Carbide, Porcelain, Stoneware, Zirconia, Boron Carbide... |
| **Composite** | 13 | Carbon Fiber, Fiberglass, Kevlar, Epoxy Composites, Metal Matrix Composites... |
| **Plastic** | 13 | Acrylic (PMMA), Polycarbonate, ABS, Nylon, PET, PTFE, PEEK... |
| **Glass** | 12 | Borosilicate, Tempered, Soda-Lime, Quartz, Sapphire, Pyrex, Gorilla Glass... |
| **Rare-Earth** | 8 | Neodymium, Lanthanum, Cerium, Yttrium, Dysprosium... |
| **Masonry** | 7 | Brick, Concrete, Cement, Mortar, Plaster, Stucco, Terracotta |
| **Semiconductor** | 7 | Silicon, Gallium Arsenide, Germanium, Silicon Carbide... |

---

## 🚀 Usage

### Script Location
```bash
scripts/research/populate_visual_appearances_all_categories.py
```

### Basic Commands

**1. List All Categories**
```bash
python3 scripts/research/populate_visual_appearances_all_categories.py --list-categories
```

**2. Single Pattern - ALL Materials (ALL Categories)**
```bash
# Research how oil-grease looks on ALL 159 materials
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern oil-grease
```

**3. Single Pattern - Specific Category**
```bash
# Research oil-grease on metals only (45 materials)
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern oil-grease --category metal

# Research rust-oxidation on stones only (20 materials)
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern rust-oxidation --category stone

# Research paint-coating on woods only (21 materials)
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern paint-coating --category wood
```

**4. Single Pattern - Multiple Categories**
```bash
# Research on metals AND ceramics (45 + 13 = 58 materials)
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern oil-grease --category metal,ceramic

# Research on glass AND stone (12 + 20 = 32 materials)
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern water-mineral --category glass,stone
```

**5. All Patterns - ALL Materials**
```bash
# Research EVERY contamination pattern on ALL 159 materials
python3 scripts/research/populate_visual_appearances_all_categories.py --all
```

**6. All Patterns - Specific Category**
```bash
# Research all patterns on ceramics only
python3 scripts/research/populate_visual_appearances_all_categories.py --all --category ceramic
```

**7. Force Re-research**
```bash
# Re-research existing data
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern oil-grease --force
```

---

## 📊 Research Scope Examples

### Example 1: Oil-Grease on ALL Materials
```bash
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern oil-grease
```

**Result**: Researches how oil and grease contamination appears on:
- **45 metals** (Aluminum, Steel, Copper, Brass, Titanium, Gold, Silver, etc.)
- **21 woods** (Oak, Maple, Pine, Cherry, Walnut, etc.)
- **20 stones** (Granite, Marble, Limestone, Sandstone, etc.)
- **13 ceramics** (Alumina, Silicon Carbide, Porcelain, etc.)
- **13 composites** (Carbon Fiber, Fiberglass, Kevlar, etc.)
- **13 plastics** (Acrylic, Polycarbonate, ABS, Nylon, etc.)
- **12 glasses** (Borosilicate, Tempered, Quartz, etc.)
- **8 rare-earths** (Neodymium, Lanthanum, Cerium, etc.)
- **7 masonry** (Brick, Concrete, Cement, etc.)
- **7 semiconductors** (Silicon, Gallium Arsenide, etc.)

**Total**: 159 material-specific visual descriptions

### Example 2: Rust-Oxidation on Metals Only
```bash
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern rust-oxidation --category metal
```

**Result**: Researches rust appearance on 45 metals:
- Aluminum, Steel, Copper, Brass, Titanium
- Bronze, Cast Iron, Stainless Steel, Galvanized Steel
- Gold, Silver, Platinum, Zinc, Nickel
- And 30 more metals

### Example 3: Water-Mineral Deposits on Glass & Stone
```bash
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern water-mineral --category glass,stone
```

**Result**: Researches mineral deposits on 32 materials:
- **12 glasses**: Borosilicate, Tempered, Soda-Lime, Quartz, etc.
- **20 stones**: Granite, Marble, Limestone, Sandstone, etc.

---

## 🎯 Material-Specific Descriptions

### Why This Matters

**Before**: Generic contamination descriptions
```yaml
visual_characteristics:
  color: "Dark brown to black"
  texture: "Greasy"
  # Same description for ALL materials
```

**After**: Material-specific scientific accuracy
```yaml
visual_characteristics:
  appearance_on_materials:
    aluminum:
      description: "Oil on aluminum appears as dark patches with rainbow iridescence..."
      color_variations: "Fresh: Amber with rainbow sheen. Aged: Nearly black..."
      texture_details: "Fresh: Glossy liquid. Aged: Matte, crusty..."
      # ... 5 more detailed fields
    
    oak:
      description: "Oil on oak wood absorbs into grain, darkening significantly..."
      color_variations: "Fresh: Light amber in grain. Aged: Deep brown saturation..."
      texture_details: "Penetrates grain structure, creates raised grain when aged..."
      # ... 5 more detailed fields
    
    granite:
      description: "Oil on granite creates darker patches that emphasize mineral variations..."
      color_variations: "Fresh: Slight darkening of grays. Aged: Significant staining..."
      texture_details: "Pools in rough areas, penetrates porous regions..."
      # ... 5 more detailed fields
```

### Visual Description Fields (8 per material)

For EACH material, the system generates:

1. **description** - Overall visual appearance (2-3 sentences)
2. **color_variations** - Fresh to aged color changes
3. **texture_details** - Surface texture characteristics
4. **common_patterns** - Distribution patterns (drips, pools, spots, etc.)
5. **aged_appearance** - How it evolves over time
6. **lighting_effects** - Appearance under different lighting conditions
7. **thickness_range** - Typical thickness measurements (mm)
8. **distribution_factors** - Environmental factors affecting accumulation

---

## 📈 Research Statistics

### Single Pattern Research

**Metals Only** (45 materials):
- API calls: 45
- Time: ~5-7 minutes
- Cost: Minimal (Gemini free tier)

**ALL Categories** (159 materials):
- API calls: 159
- Time: ~15-20 minutes
- Cost: Minimal (within free tier)

### Batch Research (All Patterns)

**Assuming 15 contamination patterns**:

**Metals Only**:
- API calls: 15 × 45 = 675
- Time: ~1.5 hours
- Cost: Minimal (within Gemini rate limits)

**ALL Categories**:
- API calls: 15 × 159 = 2,385
- Time: ~4-5 hours
- Cost: Within Gemini free tier daily limits

**Rate Limits (Gemini Free Tier)**:
- 60 requests per minute
- 2 million tokens per day
- Script automatically handles rate limiting

---

## 🔬 Technical Implementation

### Dynamic Material Discovery

The script automatically:
1. Loads Materials.yaml
2. Extracts all materials organized by category
3. Allows filtering by category
4. Researches each material with Gemini API
5. Saves results incrementally (won't lose progress)

### Code Structure

```python
# Load materials by category
materials_by_category = {
    'metal': ['Aluminum', 'Steel', 'Copper', ...],
    'ceramic': ['Alumina', 'Silicon Carbide', ...],
    'glass': ['Borosilicate', 'Tempered', ...],
    # ... all 10 categories
}

# Get materials for specific categories
materials = get_materials_for_categories(['metal', 'ceramic'])
# Returns: 58 materials (45 + 13)

# Research each material
for material in materials:
    appearance = researcher.research_appearance_on_material(
        contaminant_id='oil-grease',
        contaminant_name='Oil & Grease Contamination',
        material_name=material,
        chemical_composition='Hydrocarbon chains, mineral oils'
    )
    # Returns: 8 detailed visual fields
```

---

## 💡 Practical Examples

### Use Case 1: Laser Cleaning Equipment Images

**Goal**: Generate realistic images showing oil contamination on different materials

**Command**:
```bash
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern oil-grease
```

**Result**: 159 material-specific descriptions enable AI to generate:
- Oil on aluminum (metallic rainbow sheen)
- Oil on oak wood (absorbed into grain)
- Oil on granite (darkened mineral patterns)
- Oil on acrylic plastic (surface coating with light diffusion)
- Each scientifically accurate and visually distinct

### Use Case 2: Rust Oxidation Study

**Goal**: Document rust appearance on all metals

**Command**:
```bash
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern rust-oxidation --category metal
```

**Result**: 45 metal-specific rust descriptions:
- Steel: Red-brown iron oxide, flaking, pitting
- Aluminum: White powdery aluminum oxide
- Copper: Green-blue patina (copper carbonate)
- Brass: Green patina with yellow undertones
- Each with detailed aging progression

### Use Case 3: Paint Contamination on Woods

**Goal**: Research paint appearance on different wood types

**Command**:
```bash
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern paint-coating --category wood
```

**Result**: 21 wood-specific paint descriptions:
- Oak: Paint pools in grain, creates texture
- Maple: Smooth uniform coating
- Pine: Absorbs into soft wood, uneven
- Cherry: Rich undertones visible through paint
- Each with removal characteristics

---

## 🚦 Progress Tracking

### Incremental Save Feature

The script saves progress after **each pattern**, so if interrupted:
- Already-researched patterns are saved
- Re-run continues from where it left off
- No duplicate API calls (unless `--force`)

**Example Output**:
```
[1/159] Researching Aluminum... ✅
[2/159] Researching Steel... ✅
[3/159] Researching Copper... ✅
...
💾 Progress saved (1/15 patterns complete)

[1/159] Researching Aluminum... ✅
...
💾 Progress saved (2/15 patterns complete)
```

### Skip-Existing Logic

```bash
# First run: Researches all materials
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern oil-grease

# Second run: Skips (already has data)
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern oil-grease
# Output: ⏭️  Skipping oil-grease (already has 159 materials)

# Force re-research
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern oil-grease --force
```

---

## 📝 Output Format

### Contaminants.yaml Structure

```yaml
contamination_patterns:
  - id: oil-grease
    name: "Oil & Grease Contamination"
    visual_characteristics:
      appearance_on_materials:
        # METALS (45)
        aluminum:
          description: "..."
          color_variations: "..."
          texture_details: "..."
          common_patterns: "..."
          aged_appearance: "..."
          lighting_effects: "..."
          thickness_range: "..."
          distribution_factors: "..."
        steel:
          description: "..."
          # ... 8 fields
        copper:
          description: "..."
          # ... 8 fields
        # ... 42 more metals
        
        # WOODS (21)
        oak:
          description: "..."
          # ... 8 fields
        maple:
          description: "..."
          # ... 8 fields
        # ... 19 more woods
        
        # STONES (20)
        granite:
          description: "..."
          # ... 8 fields
        marble:
          description: "..."
          # ... 8 fields
        # ... 18 more stones
        
        # CERAMICS (13)
        alumina:
          description: "..."
          # ... 8 fields
        # ... 12 more ceramics
        
        # ... All 159 materials
```

---

## 🎨 Impact on Image Generation

### Enhanced Prompt Building

**Before** (generic):
```python
prompt = f"Photo of {material} with oil contamination"
# Result: Generic stock photo
```

**After** (material-specific):
```python
# Lookup material-specific appearance
appearance = contaminant['appearance_on_materials'][material.lower()]

prompt = f"""
High-resolution photo of {material} with oil contamination:

Visual Appearance:
- {appearance['description']}
- Color: {appearance['color_variations']}
- Texture: {appearance['texture_details']}
- Pattern: {appearance['common_patterns']}
- Lighting: {appearance['lighting_effects']}

Style: Industrial photography, macro lens, scientific accuracy
"""
# Result: Photo-realistic, material-specific image
```

### Example Prompts Generated

**Oil on Aluminum**:
```
High-resolution photo of aluminum with oil contamination:
- Dark irregular patches with rainbow iridescence under direct light
- Fresh: Translucent amber. Aged: Nearly black with matte finish
- Glossy liquid-like fresh deposits, matte crusty aged deposits
- Drip marks, fingerprints, pools in crevices
```

**Oil on Oak Wood**:
```
High-resolution photo of oak with oil contamination:
- Deep absorption into grain structure, significant darkening
- Fresh: Light amber following grain. Aged: Deep brown saturation
- Raised grain texture when aged, penetrates porous areas
- Concentrates in end grain, spreads along grain lines
```

**Oil on Granite**:
```
High-resolution photo of granite with oil contamination:
- Darker patches emphasizing mineral color variations
- Fresh: Slight darkening. Aged: Significant brown-black staining
- Pools in rough textured areas, penetrates porous regions
- Highlights existing color variations, creates patchy appearance
```

---

## ⚙️ Configuration

### API Setup

**Required**: Gemini API key
```bash
export GEMINI_API_KEY="your_api_key_here"
```

**Or**: Provide inline
```bash
python3 scripts/research/populate_visual_appearances_all_categories.py \
  --pattern oil-grease \
  --api-key "your_api_key_here"
```

### API Settings

**Model**: `gemini-2.0-flash-exp`  
**Temperature**: `0.3` (factual accuracy)  
**Max Tokens**: `2048`  
**Response Format**: JSON

---

## 🔄 Migration from Original Script

### Old Script (Metal Only)
```bash
# Limited to default metals
python3 scripts/research/populate_visual_appearances.py --pattern oil-grease
# Researches: 6 default metals
```

### New Script (All Categories)
```bash
# ALL materials or filtered by category
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern oil-grease
# Researches: 159 materials (all categories)

python3 scripts/research/populate_visual_appearances_all_categories.py --pattern oil-grease --category metal
# Researches: 45 metals
```

**Backward Compatible**: Old script still works for metal-only research

---

## 📊 Summary

### Capabilities

✅ **159 Materials** across 10 categories  
✅ **Dynamic Material Discovery** from Materials.yaml  
✅ **Category Filtering** (metal, ceramic, glass, stone, etc.)  
✅ **Multi-Category Selection** (metal,ceramic,glass)  
✅ **ALL Materials Mode** (default when no category specified)  
✅ **Incremental Save** (won't lose progress)  
✅ **Skip-Existing Logic** (no duplicate research)  
✅ **Force Re-research** (--force flag)  
✅ **Progress Tracking** (X/Y materials, X/Y patterns)  
✅ **Auto-Backup** (creates .yaml.backup)  

### Categories Supported

| Category | Materials | Common Use Cases |
|----------|-----------|------------------|
| Metal | 45 | Industrial equipment, machinery, metal structures |
| Wood | 21 | Furniture, flooring, architectural elements |
| Stone | 20 | Buildings, monuments, countertops |
| Ceramic | 13 | Industrial components, medical devices |
| Composite | 13 | Aerospace, automotive, sports equipment |
| Plastic | 13 | Consumer products, packaging, medical |
| Glass | 12 | Windows, optical components, containers |
| Rare-Earth | 8 | Electronics, magnets, catalysts |
| Masonry | 7 | Buildings, infrastructure |
| Semiconductor | 7 | Electronics, solar panels |

---

## 🚀 Next Steps

### 1. Execute Research

**Start Small** (test with single category):
```bash
export GEMINI_API_KEY="your_key_here"
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern oil-grease --category metal
```

**Scale Up** (all materials):
```bash
python3 scripts/research/populate_visual_appearances_all_categories.py --pattern oil-grease
```

**Go Big** (all patterns, all materials):
```bash
python3 scripts/research/populate_visual_appearances_all_categories.py --all
```

### 2. Verify Results

```bash
# Check populated materials
grep -A 5 "appearance_on_materials:" domains/contaminants/Contaminants.yaml | head -50
```

### 3. Update Prompt Builder

Modify `SharedPromptBuilder` to use material-specific data:
```python
# File: shared/image/prompts/prompt_builder.py
def build_generation_prompt(self, material_name, contaminant_id):
    appearance = self._get_material_specific_appearance(material_name, contaminant_id)
    # Build prompt with 8 detailed visual fields
```

### 4. Integration Testing

```bash
pytest tests/image/test_image_generation_workflow.py -v
```

---

## 📚 Documentation References

- **Setup Guide**: `VISUAL_APPEARANCE_RESEARCH_SETUP.md`
- **Implementation Summary**: `VISUAL_APPEARANCE_RESEARCH_COMPLETE.md`
- **Architecture**: `docs/08-development/IMAGE_GENERATION_ARCHITECTURE.md`
- **Implementation Checklist**: `docs/08-development/IMAGE_GENERATION_IMPLEMENTATION_CHECKLIST.md`

---

**Status**: ✅ Ready to execute research across ALL 159 materials  
**Action**: Set GEMINI_API_KEY and run research commands above
