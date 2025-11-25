# Configuration Guide
**Date**: November 25, 2025  
**Status**: ✅ PRODUCTION READY

## 🎛️ Overview

MaterialImageConfig controls all aspects of image generation: contamination intensity, pattern variety, presentation style, and environmental wear.

---

## 📋 Configuration Parameters

### `material` (Required)

**Type**: `str`  
**Purpose**: Specifies the material to generate an image for  
**Validation**: Must exist in category mapping

**Examples**:
```python
material="Oak"
material="Steel"
material="Aluminum"
material="Concrete"
```

**Supported Materials** (74 total):

**Wood**:
- Hardwood: Oak, Maple, Birch, Walnut, Cherry, Mahogany, Teak
- Softwood: Pine, Spruce, Cedar, Fir

**Metals**:
- Ferrous: Steel, Iron, Stainless Steel, Cast Iron
- Non-ferrous: Aluminum, Copper, Brass, Bronze, Zinc, Titanium

**Polymers**:
- Plastics: Polypropylene, ABS, HDPE, LDPE, PVC, Polycarbonate
- Rubber: Natural Rubber, Silicone, EPDM

**Ceramics**:
- Traditional: Porcelain, Stoneware, Earthenware, Terracotta
- Technical: Alumina, Zirconia, Silicon Carbide

**Composites**:
- Carbon Fiber, Fiberglass, Reinforced Concrete

**Stone**:
- Granite, Marble, Limestone, Sandstone, Slate

---

### `contamination_level` (Optional)

**Type**: `int`  
**Default**: `3`  
**Range**: 1-5  
**Purpose**: Controls overall contamination/aging intensity

#### Level Descriptions

**Level 1 - Minimal**
- Almost pristine condition
- Slight surface dust or very light oxidation
- Barely visible wear
- **Use cases**: New equipment demos, minimal baseline

**Level 2 - Light**
- Noticeable but limited contamination
- Light dust, fingerprints, minor oxidation
- Fresh aging signs (weeks to months)
- **Use cases**: Recently used equipment, light-duty applications

**Level 3 - Moderate** ⭐ **DEFAULT**
- Balanced contamination/aging
- Clear patterns but not overwhelming
- Months to years of exposure
- **Use cases**: Standard industrial equipment, typical field conditions

**Level 4 - Heavy**
- Significant buildup and degradation
- Multiple overlapping patterns
- Years of exposure
- **Use cases**: Long-term outdoor exposure, harsh environments

**Level 5 - Extreme**
- Severe degradation
- Thick buildup, deep corrosion, structural effects
- Decades of exposure or extreme conditions
- **Use cases**: Abandoned equipment, worst-case scenarios

#### Examples

```python
# Minimal contamination
config = MaterialImageConfig(
    material="Aluminum",
    contamination_level=1  # Almost pristine
)

# Heavy corrosion
config = MaterialImageConfig(
    material="Steel",
    contamination_level=4  # Significant rust
)
```

---

### `contamination_uniformity` (Optional)

**Type**: `int`  
**Default**: `3`  
**Range**: 1-5  
**Purpose**: Controls pattern variety and distribution complexity

#### Uniformity Descriptions

**Level 1 - Single Uniform**
- One pattern type only
- Even distribution across surface
- Minimal variation
- **Use cases**: Controlled contamination, single-source exposure

**Level 2 - Limited Variety**
- 1-2 pattern types
- Mostly uniform with slight variation
- **Use cases**: Consistent environment, limited exposure types

**Level 3 - Balanced** ⭐ **DEFAULT**
- 2-3 pattern types
- Some variation in distribution
- **Use cases**: Standard field conditions, mixed environment

**Level 4 - High Variety**
- 3-4 pattern types
- Varied distribution (gravity effects, edge accumulation)
- **Use cases**: Complex environment, multiple contamination sources

**Level 5 - Complex Multi-Pattern**
- 4+ pattern types
- Complex overlapping distributions
- Micro-scale variation
- **Use cases**: Long-term outdoor exposure, industrial settings

#### Examples

```python
# Single rust pattern
config = MaterialImageConfig(
    material="Steel",
    contamination_uniformity=1  # Uniform rust only
)

# Complex aging (UV + fungal + water + deposits)
config = MaterialImageConfig(
    material="Oak",
    contamination_uniformity=5  # Multiple overlapping patterns
)
```

#### Interaction with contamination_level

| Level | Uniformity=1 | Uniformity=3 | Uniformity=5 |
|-------|--------------|--------------|--------------|
| **1 (Minimal)** | Light dust (uniform) | Light dust + fingerprints | Light dust + fingerprints + condensation |
| **3 (Moderate)** | Moderate oxidation (uniform) | Oxidation + deposits + light wear | Oxidation + deposits + wear + staining |
| **5 (Extreme)** | Heavy rust (uniform) | Heavy rust + thick deposits | Heavy rust + deposits + pitting + biological growth |

---

### `view_mode` (Optional)

**Type**: `str`  
**Default**: `"Contextual"`  
**Options**: `"Contextual"` or `"Isolated"`  
**Purpose**: Controls object presentation style

#### View Mode Descriptions

**"Contextual"**
- Object shown in realistic environment
- Background provides usage context (workshop, outdoor, industrial)
- Object has purpose and placement
- **Use cases**: Demonstration of real-world conditions, storytelling

**"Isolated"**
- Object against neutral/white background
- Studio-like presentation
- Focus on contamination details
- **Use cases**: Technical documentation, clean comparisons

#### Examples

```python
# Contextual presentation
config = MaterialImageConfig(
    material="Steel",
    view_mode="Contextual"  # Show in industrial setting
)

# Isolated presentation
config = MaterialImageConfig(
    material="Aluminum",
    view_mode="Isolated"  # White background, focus on oxidation
)
```

#### Visual Differences

**Contextual Example (Oak bench)**:
- Background: Park setting with trees, grass
- Object: Weathered wooden bench
- Lighting: Natural outdoor lighting
- Story: Years of outdoor exposure

**Isolated Example (Oak plank)**:
- Background: Pure white, no context
- Object: Flat oak plank
- Lighting: Studio lighting, even illumination
- Focus: UV graying and fungal patterns

---

### `environment_wear` (Optional)

**Type**: `int`  
**Default**: `3`  
**Range**: 1-5  
**Purpose**: Controls environmental interaction visibility

#### Environment Wear Descriptions

**Level 1 - Clean Setting**
- Minimal environmental exposure
- Indoor, controlled conditions
- **Use cases**: Laboratory samples, clean room equipment

**Level 2 - Light Exposure**
- Light environmental effects
- Protected outdoor or warehouse storage
- **Use cases**: Covered equipment, indoor-outdoor transitions

**Level 3 - Moderate Effects** ⭐ **DEFAULT**
- Clear environmental interaction
- Standard outdoor or industrial exposure
- **Use cases**: Typical field equipment, uncovered storage

**Level 4 - Heavy Wear**
- Significant environmental damage
- Long-term outdoor exposure
- **Use cases**: Marine environments, harsh climates

**Level 5 - Extreme Damage**
- Severe environmental degradation
- Decades of exposure or extreme conditions
- **Use cases**: Coastal installations, abandoned equipment

#### Material-Specific Effects

**Wood**:
- Level 1-2: Light UV graying
- Level 3-4: Cracking, checking, deep graying
- Level 5: Structural degradation, rot

**Metals**:
- Level 1-2: Light oxidation
- Level 3-4: Corrosion pitting, flaking
- Level 5: Deep pitting, structural loss

**Polymers**:
- Level 1-2: Slight discoloration
- Level 3-4: UV chalking, cracking
- Level 5: Brittleness, delamination

#### Examples

```python
# Protected indoor equipment
config = MaterialImageConfig(
    material="Steel",
    environment_wear=2  # Light oxidation only
)

# Marine environment
config = MaterialImageConfig(
    material="Aluminum",
    environment_wear=5  # Severe saltwater corrosion
)
```

---

## 🎯 Configuration Recipes

### Recipe 1: New Equipment Demo (Minimal)

```python
config = MaterialImageConfig(
    material="Aluminum",
    contamination_level=1,      # Almost pristine
    contamination_uniformity=1,  # Single pattern
    view_mode="Isolated",       # Clean presentation
    environment_wear=1           # No environmental damage
)
```

**Result**: Almost pristine material with slight surface dust

---

### Recipe 2: Standard Industrial Equipment (Moderate)

```python
config = MaterialImageConfig(
    material="Steel",
    contamination_level=3,      # Moderate
    contamination_uniformity=3,  # Balanced variety
    view_mode="Contextual",     # Show real-world setting
    environment_wear=3           # Standard exposure
)
```

**Result**: Typical industrial equipment with balanced contamination

---

### Recipe 3: Heavy Outdoor Aging (Extreme Organic)

```python
config = MaterialImageConfig(
    material="Oak",
    contamination_level=5,      # Extreme
    contamination_uniformity=5,  # Complex multi-pattern
    view_mode="Contextual",     # Outdoor setting
    environment_wear=5           # Severe weathering
)
```

**Result**: Severely weathered wood with UV degradation, fungal decay, water damage

---

### Recipe 4: Marine Corrosion (Extreme Metal)

```python
config = MaterialImageConfig(
    material="Steel",
    contamination_level=5,      # Extreme
    contamination_uniformity=4,  # High variety
    view_mode="Isolated",       # Focus on corrosion
    environment_wear=5           # Saltwater damage
)
```

**Result**: Severe saltwater corrosion with multiple rust types

---

### Recipe 5: Light Use Equipment (Clean Demo)

```python
config = MaterialImageConfig(
    material="Copper",
    contamination_level=2,      # Light
    contamination_uniformity=2,  # Limited variety
    view_mode="Isolated",       # Clean background
    environment_wear=2           # Minimal wear
)
```

**Result**: Light tarnish, great for before/after demos

---

## ⚙️ Advanced Configuration

### Validation

MaterialImageConfig validates inputs automatically:

```python
try:
    config = MaterialImageConfig(
        material="Oak",
        contamination_level=10  # Invalid (> 5)
    )
except ValueError as e:
    print(f"Validation error: {e}")
```

### Dataclass Access

```python
config = MaterialImageConfig(material="Steel")

# Access fields
print(config.material)              # "Steel"
print(config.contamination_level)   # 3 (default)
print(config.view_mode)             # "Contextual" (default)

# Convert to dict
config_dict = {
    "material": config.material,
    "contamination_level": config.contamination_level,
    # ...
}
```

---

## 🔗 Related Documentation

- `API_USAGE.md` - Full Python API examples
- `ARCHITECTURE.md` - System architecture and data flow
- `PROMPT_VALIDATION.md` - Validation system details
- `TROUBLESHOOTING.md` - Common configuration issues

---

**Status**: ✅ Configuration documented and validated  
**Last Updated**: November 25, 2025
