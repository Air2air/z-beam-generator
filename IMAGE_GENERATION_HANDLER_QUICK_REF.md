# Copilot Image Generation - Quick Reference

**File**: `shared/commands/image_generation_handler.py`  
**Purpose**: Handle natural language image generation requests  
**Date**: November 26, 2025

## 🎯 Quick Start

```python
from shared.commands.image_generation_handler import ImageGenerationHandler

handler = ImageGenerationHandler(gemini_api_key="your_key")

# Generate image
result = handler.generate("Make me a Bismuth Hero image")
```

## 📝 Request Formats

| Request Example | What It Does |
|----------------|--------------|
| `"Make me a Bismuth Hero image"` | Generates hero image for Bismuth |
| `"Generate Aluminum oil contamination"` | Aluminum with oil contamination (before/after) |
| `"Create Steel rust before/after split"` | Steel with rust in split view |
| `"Show me a Copper oxide micro image"` | Copper microscopic image with oxidation |
| `"Titanium laser cleaning"` | Titanium hero image (default) |

## 🔍 What Gets Automatically Detected

### 1. **Material Name** (from Materials.yaml)
- Searches `material_index` for exact match
- Supports 159 materials across 10 categories
- Case-insensitive matching

### 2. **Image Type**
- **Hero**: Default, main image for material page
- **Micro**: Microscopic (500x magnification) view
- **Contamination**: Before/after split with contamination

Detection keywords:
- `hero`, `main`, `primary` → Hero image
- `micro`, `microscop`, `500x` → Microscopic image
- `contamination`, `before`, `after`, `split` → Contamination image

### 3. **Category** (Automatic Lookup)
- Pulled from `material_index` in Materials.yaml
- metal, ceramic, wood, stone, composite, plastic, glass, rare-earth, masonry, semiconductor

### 4. **Contamination Pattern** (from Contaminants.yaml)
- Detected from keywords: `rust`, `oil`, `oxide`, `grease`, etc.
- Checks against `contamination_patterns`
- Validates material-contaminant compatibility

### 5. **Output Path** (Automatic)
```
Materials domain:
  Hero: /images/materials/bismuth-laser-cleaning.png
  Micro: /images/materials/bismuth-laser-cleaning-micro.png
  Contamination: /images/materials/bismuth-oil-contamination.png
```

## ✅ Validation Steps

### 1. Material-Contaminant Compatibility
```python
# Checks prohibited_materials in Contaminants.yaml
# Example: Rust cannot occur on Aluminum
patterns = {
    'rust-oxidation': {
        'prohibited_materials': ['Aluminum', 'Copper', 'Brass', ...]
    }
}
```

### 2. Payload Validation (7 Categories)
- Logic: Contradictions, confusion
- Contamination: Impossible combinations
- Physics: Gravity violations
- Length: Imagen 4096 char limit
- Quality: Anti-patterns
- Duplication: Repeated content
- Technical: API compatibility

## 🎨 Generation Process

```
1. Parse Request
   ├─ Extract material name (Bismuth)
   ├─ Detect image type (hero)
   ├─ Detect contaminant (optional)
   └─ Build output path

2. Lookup Material Data
   ├─ Get category from material_index
   ├─ Load material properties
   └─ Validate contaminant compatibility

3. Generate Prompt
   ├─ MaterialImageGenerator.generate_complete()
   ├─ Include contamination research
   ├─ Apply learned feedback
   └─ Build negative prompt

4. Validate Prompt
   ├─ PayloadValidator.validate()
   ├─ Check for critical issues
   └─ Flag warnings

5. Generate Image (if not dry_run)
   ├─ GeminiImageClient.generate_image()
   ├─ Save to output_path
   └─ Return result
```

## 🛠️ Usage Examples

### Example 1: Dry Run (No API Call)
```python
handler = ImageGenerationHandler()  # No API key
result = handler.generate("Make me a Bismuth Hero image", dry_run=True)

# Shows what would be generated without calling Imagen API
# Prints: Prompt preview, output path, validation results
```

### Example 2: Validate Only
```python
handler = ImageGenerationHandler(gemini_api_key="key")
result = handler.generate("Aluminum oil contamination", validate_only=True)

# Validates prompt but doesn't generate image
# Useful for checking if request is valid before spending credits
```

### Example 3: Full Generation
```python
handler = ImageGenerationHandler(gemini_api_key="key")
result = handler.generate("Steel rust before/after split")

if result['success']:
    print(f"✅ Image saved to: {result['output_path']}")
else:
    print(f"❌ Failed: {result['error']}")
```

### Example 4: Show Material Info
```python
handler = ImageGenerationHandler()
handler.show_material_info("Bismuth")

# Prints:
# - Category: metal
# - Available properties
# - Compatible contamination patterns
```

### Example 5: List Materials
```python
handler = ImageGenerationHandler()

# All materials
handler.list_materials()

# Filter by category
handler.list_materials("metal")  # Shows 45 metal materials
```

## 📊 Return Value Structure

```python
{
    'success': bool,                    # True if generation succeeded
    'request': ImageRequest,            # Parsed request object
    'prompt': str,                      # Generated prompt text
    'negative_prompt': str,             # Negative prompt text
    'validation': ValidationResult,     # Payload validation result
    'output_path': Path,                # Where image is saved
    'image_data': bytes,                # Image data (if generated)
    'error': str                        # Error message (if failed)
}
```

## 🚨 Common Errors

### Error: Material Not Found
```
❌ Material not found in request: 'Make me a Titanium image'
Available materials: Alabaster, Alumina, Aluminum, ...
```

**Solution**: Check spelling, use exact material name from Materials.yaml

### Error: Invalid Material-Contaminant
```
❌ rust-oxidation cannot occur on Aluminum
Prohibited materials: Aluminum, Copper, Brass, ...
```

**Solution**: Choose compatible contaminant for material

### Error: Prompt Validation Failed
```
❌ Validation FAILED (critical issues):
• Prompt exceeds Imagen limit (5000 chars > 4096)
• Physics violation: Upward flow detected
```

**Solution**: Review validation report, adjust request

## 🎯 Copilot Integration Pattern

When you tell Copilot: **"Make me a Bismuth Hero image"**

Copilot will:
1. Import `ImageGenerationHandler`
2. Initialize with your Gemini API key
3. Call `handler.generate("Make me a Bismuth Hero image")`
4. Display results

```python
# What Copilot executes behind the scenes:
from shared.commands.image_generation_handler import ImageGenerationHandler
import os

api_key = os.getenv('GEMINI_API_KEY')
handler = ImageGenerationHandler(gemini_api_key=api_key)
result = handler.generate("Make me a Bismuth Hero image")

if result['success']:
    print(f"✅ Image saved to: {result['output_path']}")
```

## 📋 CLI Usage

```bash
# Set API key
export GEMINI_API_KEY="your_key_here"

# Generate image
python3 shared/commands/image_generation_handler.py "Make me a Bismuth Hero image"

# Show material info
python3 shared/commands/image_generation_handler.py --info Bismuth

# List all materials
python3 shared/commands/image_generation_handler.py --list-materials

# List materials by category
python3 shared/commands/image_generation_handler.py --list-materials metal
```

## 🔧 Configuration

The handler automatically creates `MaterialImageConfig` with:
- **contamination_uniformity**: 3 (moderate diversity)
- **view_mode**: "Contextual" (3D perspective)
- **guidance_scale**: 15.0 (balanced)

To customize, modify the config in `generate()` method.

## 📚 Related Documentation

- `PAYLOAD_VALIDATOR_QUICK_REF.md` - Payload validation details
- `IMAGE_GENERATION_ARCHITECTURE.md` - Overall image generation workflow
- `domains/materials/image/material_generator.py` - Core generator
- `data/materials/Materials.yaml` - Material data structure
- `data/contaminants/Contaminants.yaml` - Contamination patterns

---

**Status**: ✅ Complete and ready to use  
**Works with**: Any material in Materials.yaml (159 materials)  
**Validates**: Material-contaminant compatibility + prompt quality  
**Outputs to**: Correct domain path (materials, contaminants, regions)
