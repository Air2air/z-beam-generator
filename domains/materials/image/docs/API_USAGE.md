# API Usage Guide
**Date**: November 25, 2025  
**Status**: ✅ PRODUCTION READY

## 🚀 Quick Start

### Basic Usage

```python
from domains.materials.image.material_generator import MaterialImageGenerator
from domains.materials.image.material_config import MaterialImageConfig

# Initialize generator
generator = MaterialImageGenerator(gemini_api_key="your_api_key_here")

# Create configuration
config = MaterialImageConfig(
    material="Oak",
    contamination_level=3,
    contamination_uniformity=3,
    view_mode="Contextual",
    environment_wear=3
)

# Generate prompt package
result = generator.generate_complete("Oak", config=config)

# Access results
print(f"Prompt: {result['prompt']}")
print(f"Research: {result['research_data']}")
print(f"Validation: {result['validation']}")
```

---

## 📋 MaterialImageConfig Options

### Required Parameters

**`material`** (str)
- Material name (e.g., "Oak", "Steel", "Aluminum")
- Must match a material in the system's category map
- **Example**: `material="Oak"`

### Optional Parameters

**`contamination_level`** (int, default=3)
- Controls overall contamination/aging intensity
- Range: 1-5
  - **1**: Minimal (pristine with slight wear)
  - **2**: Light (noticeable but limited)
  - **3**: Moderate (balanced contamination)
  - **4**: Heavy (significant buildup)
  - **5**: Extreme (severe degradation)
- **Example**: `contamination_level=4`

**`contamination_uniformity`** (int, default=3)
- Controls pattern variety and distribution
- Range: 1-5
  - **1**: Single uniform pattern
  - **2**: 1-2 patterns, mostly uniform
  - **3**: 2-3 patterns, some variation
  - **4**: 3-4 patterns, varied distribution
  - **5**: Complex multi-pattern coverage
- **Example**: `contamination_uniformity=4`

**`view_mode`** (str, default="Contextual")
- Controls object presentation
- Options:
  - **"Contextual"**: Object shown in realistic environment
  - **"Isolated"**: Object against neutral/white background
- **Example**: `view_mode="Isolated"`

**`environment_wear`** (int, default=3)
- Controls environmental interaction visibility
- Range: 1-5
  - **1**: Clean, controlled setting
  - **2**: Light environmental exposure
  - **3**: Moderate environmental effects
  - **4**: Heavy environmental wear
  - **5**: Extreme environmental damage
- **Example**: `environment_wear=4`

---

## 🔧 API Methods

### `MaterialImageGenerator.generate_complete(material_name, config)`

Generates complete prompt package with research, prompt, and validation.

**Parameters**:
- `material_name` (str): Material to generate for
- `config` (MaterialImageConfig): Configuration object

**Returns** (dict):
```python
{
    "prompt": str,           # Complete validated prompt (1,000-2,000 chars)
    "research_data": dict,   # Category research with patterns
    "config": dict,          # Applied configuration
    "validation": dict       # Validation results
}
```

**Raises**:
- `ValueError`: If config is None or material unknown
- `RuntimeError`: If research fails or API error

**Example**:
```python
result = generator.generate_complete("Steel", config=config)
prompt = result['prompt']
```

---

### `MaterialImageGenerator.generate_prompt(material_name, config)`

Generates prompt only (no validation).

**Parameters**:
- `material_name` (str): Material to generate for
- `config` (MaterialImageConfig): Configuration object

**Returns** (str):
- Complete prompt text

**Example**:
```python
prompt = generator.generate_prompt("Aluminum", config=config)
```

---

## 🎯 Common Use Cases

### Use Case 1: Heavy Aging for Organic Material

```python
# Oak with extreme UV degradation and fungal decay
config = MaterialImageConfig(
    material="Oak",
    contamination_level=5,      # Extreme
    contamination_uniformity=4,  # Multiple patterns
    view_mode="Contextual",
    environment_wear=5           # Severe environmental damage
)

result = generator.generate_complete("Oak", config=config)
```

**Expected Patterns**: UV graying, fungal decay, surface chalking, water staining

---

### Use Case 2: Industrial Corrosion on Metal

```python
# Steel with heavy rust and industrial deposits
config = MaterialImageConfig(
    material="Steel",
    contamination_level=4,      # Heavy
    contamination_uniformity=3,  # Balanced variety
    view_mode="Isolated",       # Clean background
    environment_wear=4           # Heavy industrial exposure
)

result = generator.generate_complete("Steel", config=config)
```

**Expected Patterns**: Iron oxide rust, oil/grease, particulate accumulation

---

### Use Case 3: Minimal Contamination for Clean Demo

```python
# Aluminum with light oxidation only
config = MaterialImageConfig(
    material="Aluminum",
    contamination_level=2,      # Light
    contamination_uniformity=1,  # Single uniform pattern
    view_mode="Isolated",
    environment_wear=2           # Minimal environmental effects
)

result = generator.generate_complete("Aluminum", config=config)
```

**Expected Patterns**: Light aluminum oxide layer

---

### Use Case 4: Complex Multi-Pattern Scenario

```python
# Copper with multiple aging/contamination types
config = MaterialImageConfig(
    material="Copper",
    contamination_level=4,      # Heavy
    contamination_uniformity=5,  # Complex multi-pattern
    view_mode="Contextual",
    environment_wear=4           # Heavy environmental wear
)

result = generator.generate_complete("Copper", config=config)
```

**Expected Patterns**: Patina (green), tarnish (brown), sulfide films, deposits

---

## 🔍 Accessing Results

### Prompt Access

```python
result = generator.generate_complete("Oak", config=config)

# Get complete prompt
prompt = result['prompt']

# Check prompt length
print(f"Length: {len(prompt)} chars")
```

### Research Data Access

```python
# Get all researched patterns
research = result['research_data']
patterns = research['patterns']

for pattern in patterns:
    print(f"Pattern: {pattern['name']}")
    print(f"Type: {pattern['type']}")  # aging|contamination|combined
    print(f"Visual: {pattern['visual_characteristics']}")
    print()
```

### Validation Results Access

```python
validation = result['validation']

print(f"Valid: {validation['valid']}")
print(f"Issues: {validation['issues']}")
print(f"Warnings: {validation['warnings']}")

# Check detail score
metrics = validation['metrics']
print(f"Detail Score: {metrics['detail_score']}/100")
print(f"Length: {metrics['length']} chars")
```

---

## ⚠️ Error Handling

### Handle Missing Configuration

```python
try:
    result = generator.generate_complete("Oak", config=None)
except ValueError as e:
    print(f"Configuration error: {e}")
    # Create valid config and retry
```

### Handle Research Failures

```python
try:
    result = generator.generate_complete("UnknownMaterial", config=config)
except RuntimeError as e:
    print(f"Research failed: {e}")
    # Check material name or API connectivity
```

### Handle Validation Warnings

```python
result = generator.generate_complete("Steel", config=config)

validation = result['validation']
if not validation['valid']:
    print("⚠️ Validation issues detected:")
    for issue in validation['issues']:
        print(f"  • {issue}")
    
    # Prompt is still usable, but may need refinement
```

---

## 🧪 Testing & Debugging

### Prompt-Only Generation (Fast)

```python
# Skip validation for quick testing
from domains.materials.image.research.material_prompts import build_material_cleaning_prompt

prompt = build_material_cleaning_prompt(
    material_name="Oak",
    research_data={...},
    contamination_level=3,
    contamination_uniformity=3,
    view_mode="Contextual",
    environment_wear=3,
    validate=False  # Skip validation
)
```

### Inspect Validation Details

```python
from domains.materials.image.research.material_prompts import validate_prompt

validation = validate_prompt(prompt, research_data)

print(f"Length: {validation['metrics']['length']}")
print(f"Detail: {validation['metrics']['detail_score']}/100")
print(f"Clarity: {validation['metrics']['clarity_score']}/100")
print(f"Duplication: {validation['metrics']['duplication_score']}%")
```

### Cache Inspection

```python
# Check if category is cached
from domains.materials.image.research.contamination_pattern_selector import ContaminationPatternSelector

# This will use selector caching if available
selector = ContaminationPatternSelector()
research = selector.get_patterns_for_image_gen("Oak")

# Force cache refresh (not recommended in production)
selector._data = None
```

---

## 📊 Performance Optimization

### Batch Processing

```python
# Generate multiple materials efficiently
materials = ["Oak", "Maple", "Birch", "Walnut"]
configs = [MaterialImageConfig(material=m) for m in materials]

results = []
for material, config in zip(materials, configs):
    result = generator.generate_complete(material, config=config)
    results.append(result)

# All use cached "wood_hardwood" research (fast)
```

### Pre-warm Cache

```python
# Pre-research common categories
categories = ["wood_hardwood", "metals_ferrous", "metals_non_ferrous"]

for category in categories:
    research_category_contamination(category)

# Now all materials in these categories are instant
```

---

## 🔗 Related Documentation

- `ARCHITECTURE.md` - System architecture and data flow
- `CONFIGURATION.md` - Detailed configuration guide
- `PROMPT_VALIDATION.md` - Validation system details
- `TROUBLESHOOTING.md` - Common issues and solutions

---

**Status**: ✅ API documented and production-ready  
**Last Updated**: November 25, 2025
