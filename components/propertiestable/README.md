# PropertiesTable Component

## Overview

The PropertiesTable component generates structured property tables for materials using a **4-field standardized format**. This component was recently updated (September 2025) to provide a streamlined, consistent structure across all materials.

## 4-Field Structure (Current Standard)

The PropertiesTable now generates exactly **4 fields** for every material:

| Field | Description | Notes |
|-------|-------------|-------|
| **Density** | Material density | Format: "X.X g/cm³" |
| **Melting Point** | Thermal behavior | "X°C" for melting, "Decomposes at X°C" for decomposition |
| **Conductivity** | Thermal conductivity | Format: "X W/m·K" |
| **Formula** | Chemical formula | Chemical composition or description |

## 🔧 Configuration

```yaml
# Component configuration
propertiestable:
  enabled: true
  api_provider: none
  data_source: frontmatter_data
  mode: static
```

## 📝 Usage

```python
from components.propertiestable.generator import PropertiestableComponentGenerator

generator = PropertiestableComponentGenerator()
result = generator.generate(
    material_name="aluminum",
    material_data=material_data,
    frontmatter_data=frontmatter_data
)
```

### Command Line Usage

```bash
# Generate propertiestable for specific material
python3 run.py --material "aluminum" --components propertiestable

# Regenerate all propertiestable files 
python3 run.py --all --components propertiestable

# Deploy propertiestable to production
python3 run.py --all --deploy
```

## 📊 Output Format

Generates a markdown table with exactly 4 rows:

```markdown
| Property | Value |
|----------|-------|
| Density | 2.7 g/cm³ |
| Melting Point | 660°C |
| Conductivity | 237 W/m·K |
| Formula | Al |
```

## Thermal Behavior Support

The component intelligently handles different thermal behaviors:

- **Melting Materials**: Display "Melting Point: 1085°C"
- **Decomposition Materials**: Display "Decomposes at 300-400°C"

## Legacy Fields (Removed in 4-Field Update)

❌ **Removed Fields:**
- Laser Type
- Wavelength  
- Fluence Range
- Thermal Cond. (replaced with "Conductivity")

## 🧪 Testing

Run component tests:
```bash
python3 -m pytest components/propertiestable/testing/ -v
```

### Test Coverage
- ✅ 4-field structure validation
- ✅ Thermal behavior detection
- ✅ Frontmatter data validation
- ✅ Table format compliance
- ✅ Legacy field removal verification

## Compliance Verification

Verify 4-field compliance across all files:

```bash
# Check for forbidden laser properties (should return 0)
grep -l 'Laser Type\|Wavelength\|Fluence Range' content/components/propertiestable/*-laser-cleaning.md

# Check for old thermal label (should return 0)
grep -l 'Thermal Cond\.' content/components/propertiestable/*-laser-cleaning.md

# Verify correct Conductivity label (should return 109)
grep -l '| Conductivity |' content/components/propertiestable/*-laser-cleaning.md
```

## 🔗 Dependencies

- **Frontmatter Data**: Primary source for property values
- **Material Schema**: Provides property definitions and validation
- **Versioning System**: Adds generation timestamps
- **Component Factory**: Enables dynamic generation

## Recent Updates (September 2025)

- **4-Field Standardization**: Reduced to exactly 4 fields per material
- **Thermal Behavior Support**: Intelligent melting vs decomposition detection
- **Label Standardization**: "Thermal Cond." → "Conductivity"
- **Deployment Integration**: Full `--deploy` command support
- **Enhanced Testing**: Comprehensive compliance verification</content>
<parameter name="filePath">/Users/todddunning/Desktop/Z-Beam/z-beam-generator/components/propertiestable/README.md
