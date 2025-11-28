# Copilot Image Generation - Usage Examples

**Date**: November 26, 2025  
**Handler**: `shared/commands/image_generation_handler.py`

## ✅ Complete! What You Can Do Now

When you tell Copilot: **"Make me a Bismuth Hero image"**

Copilot will automatically:
1. ✅ Parse "Bismuth" → Look up in Materials.yaml  
2. ✅ Find category: `metal`  
3. ✅ Detect image type: `hero` (default)  
4. ✅ Build output path: `/images/materials/bismuth-laser-cleaning.png`  
5. ✅ Validate material-contaminant compatibility  
6. ✅ Generate prompt with contamination research  
7. ✅ Validate prompt (7-category validation)  
8. ✅ Generate image via Imagen API  
9. ✅ Save to correct location

## 📝 Example Requests You Can Use

### Materials Domain (Hero Images)

```
"Make me a Bismuth Hero image"
"Generate Aluminum hero image"
"Create Copper laser cleaning image"
"Show me a Titanium main image"
```

**What happens**:
- Material: Automatically looked up in Materials.yaml
- Category: Automatically determined (metal, ceramic, wood, etc.)
- Output: `/images/materials/{material}-laser-cleaning.png`
- Type: Hero image (before/after split with laser cleaning)

### Contamination Images (Before/After Splits)

```
"Make me an Aluminum oil contamination image"
"Generate Steel rust before/after"
"Create Copper oxide contamination split"
"Show me Brass tarnish comparison"
```

**What happens**:
- Material: Aluminum, Steel, Copper, Brass
- Contaminant: oil-grease, rust-oxidation, oxide, tarnish
- Validation: Checks if contaminant can occur on material
  - ✅ Oil on Aluminum → VALID
  - ❌ Rust on Aluminum → BLOCKED (impossible)
- Output: `/images/materials/{material}-{contaminant}-before-after.png`

### Microscopic Images

```
"Generate Aluminum micro image"
"Show me Steel microscopic view at 500x"
"Create Titanium microstructure image"
```

**What happens**:
- Type: Microscopic (500x magnification)
- Output: `/images/materials/{material}-laser-cleaning-micro.png`
- Shows: Detailed surface structure and laser cleaning effects

## 🚫 Automatic Validation

### Impossible Combinations (Blocked)

```
"Make Aluminum rust image" 
❌ BLOCKED: Rust cannot form on aluminum (non-ferrous metal)

"Generate plastic rust contamination"
❌ BLOCKED: Rust only forms on ferrous metals

"Create wood rust before/after"
❌ BLOCKED: Impossible material-contaminant combination
```

### Prompt Quality Issues (Detected)

```
"Very dark aluminum with really heavy contamination!!!"
⚠️  WARNING: Intensifiers detected (very, really)
⚠️  WARNING: Excessive punctuation (!!!)
```

### Physics Violations (Caught)

```
Prompt: "Oil flowing upward from bottom to top"
❌ CRITICAL: Physics violation - defies gravity
```

## 🎯 How Copilot Will Execute

### Behind the Scenes
```python
# What Copilot does when you say "Make me a Bismuth Hero image":

from shared.commands.image_generation_handler import ImageGenerationHandler
import os

# Get API key from environment
api_key = os.getenv('GEMINI_API_KEY')

# Initialize handler
handler = ImageGenerationHandler(gemini_api_key=api_key)

# Generate image
result = handler.generate("Make me a Bismuth Hero image")

# Show result
if result['success']:
    print(f"✅ Image saved to: {result['output_path']}")
    print(f"   Size: {len(result['image_data'])} bytes")
else:
    print(f"❌ Failed: {result['error']}")
```

### What You'll See
```
================================================================================
📸 IMAGE GENERATION REQUEST
================================================================================
Request: Make me a Bismuth Hero image

✅ Parsed Request:
   • Material: Bismuth
   • Category: metal
   • Image Type: hero
   • Domain: materials
   • Output: /Users/todddunning/Desktop/Z-Beam/z-beam-generator/public/images/materials/bismuth-laser-cleaning.png

✅ Prompt Generated (3456 chars)

🔍 Validating prompt...
   ✅ Prompt validated successfully

🎨 Generating image...

✅ Image generated successfully!
   💾 Saved to: /Users/todddunning/Desktop/Z-Beam/z-beam-generator/public/images/materials/bismuth-laser-cleaning.png
```

## 📊 Supported Materials

### All 159 Materials Supported

**Metal (45 materials)**:
- Aluminum, Bismuth, Brass, Bronze, Copper, Gold, Iron, Lead, Nickel, Silver, Steel, Stainless Steel, Titanium, Zinc, etc.

**Ceramic (13 materials)**:
- Alumina, Porcelain, Silicon Carbide, Silicon Nitride, Stoneware, Terracotta, Titanium Carbide, Tungsten Carbide, etc.

**Wood (21 materials)**:
- Ash, Bamboo, Beech, Birch, Cedar, Cherry, Fir, Hickory, Mahogany, Maple, Oak, Pine, Redwood, Teak, Walnut, etc.

**Stone (20 materials)**:
- Alabaster, Basalt, Bluestone, Calcite, Granite, Limestone, Marble, Quartzite, Sandstone, Slate, Travertine, etc.

**Composite (13 materials)**:
- Carbon Fiber, Fiberglass, Kevlar, Rubber, etc.

**Plastic (13 materials)**:
- ABS, Acrylic, Nylon, Polycarbonate, Polyethylene, PVC, PTFE, etc.

**Glass (12 materials)**:
- Borosilicate, Crown Glass, Float Glass, Fused Silica, Gorilla Glass, Lead Crystal, Pyrex, Sapphire Glass, Tempered Glass, etc.

**Rare-Earth (8 materials)**:
- Cerium, Dysprosium, Europium, Lanthanum, Neodymium, Praseodymium, Terbium, Yttrium

**Semiconductor (7 materials)**:
- Gallium Arsenide, Germanium, Silicon, Silicon Germanium, etc.

**Masonry (7 materials)**:
- Brick, Cement, Concrete, Mortar, Stucco, Terracotta

## 🔬 Supported Contamination Patterns

From `Contaminants.yaml`:
- **rust-oxidation**: Iron oxide (ferrous metals only)
- **oil-grease**: Hydrocarbon-based (most materials)
- **oxide**: General oxidation (many metals)
- **biological-growth**: Algae, mold, lichen
- **chemical-residue**: Industrial chemicals
- **paint-coatings**: Surface coatings
- **tarnish**: Metal surface oxidation
- ... and more

## 💡 Tips for Best Results

### ✅ DO:
- Use exact material names from Materials.yaml (case-insensitive OK)
- Specify contamination type for better results
- Let automatic validation catch issues

### ❌ DON'T:
- Use materials not in Materials.yaml
- Request impossible contaminations (will be blocked)
- Override validation errors (system prevents bad combinations)

## 🛠️ Advanced Usage

### Dry Run (Preview Only)
```python
result = handler.generate("Make me a Bismuth Hero image", dry_run=True)
# Shows what would be generated without calling API
# Useful for testing requests
```

### Validate Only (Check Before Generating)
```python
result = handler.generate("Aluminum oil contamination", validate_only=True)
# Validates prompt but doesn't generate image
# Useful for checking compatibility before spending credits
```

### Show Material Info
```python
handler.show_material_info("Bismuth")
# Shows:
# - Category (metal)
# - Available properties
# - Compatible contamination patterns
```

### List Materials by Category
```python
handler.list_materials("metal")  # Shows all 45 metal materials
handler.list_materials()          # Shows all 159 materials
```

## 🎉 That's It!

Just tell Copilot:
- **"Make me a [Material] [ImageType] image"**
- **"Generate [Material] [Contaminant] contamination"**
- **"Create [Material] before/after split"**

Everything else happens automatically! ✨

---

**Status**: ✅ Complete and ready to use  
**Materials**: 159 materials across 10 categories  
**Validation**: Automatic material-contaminant compatibility + 7-category prompt validation  
**Output**: Correct domain paths (materials/, contaminants/, regions/)
