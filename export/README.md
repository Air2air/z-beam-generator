# Frontmatter Component v9.1.0 - Trivial Export Architecture + Breadcrumb Navigation

The frontmatter component exports Materials.yaml data to frontmatter YAML files using **trivial YAML-to-YAML copy operation**. No API calls, no validation, no generation - just instant export.

## 🎯 CRITICAL - New Architecture (October 25, 2025)

### **ALL Generation/Validation Happens on Materials.yaml**

- ✅ **AI Text Generation** → Materials.yaml (micros, descriptions, etc.)
- ✅ **Property Research** → Materials.yaml (AI discovery, ranges, values)
- ✅ **Completeness Validation** → Materials.yaml (100% data coverage)
- ✅ **Quality Scoring** → Materials.yaml (thresholds, human believability)
- ✅ **Schema Validation** → Materials.yaml (structure, types, required fields)

### **Frontmatter Export is Trivial (Seconds, Not Minutes)**

- ✅ **Simple Field Mapping**: Copy Materials.yaml → frontmatter structure
- ✅ **Breadcrumb Navigation**: Auto-generated hierarchical navigation (Home → Materials → Category → Subcategory → Material)
- ✅ **Categories.yaml Metadata**: Add category metadata for reference only
- ✅ **NO API Calls**: All content already generated in Materials.yaml
- ✅ **NO Validation**: Already validated in Materials.yaml
- ✅ **NO Fallback Ranges**: Zero tolerance - Materials.yaml must have 100% data
- ✅ **Performance**: 132 materials in ~10 seconds (was minutes/hours)

### **Zero Fallback Ranges Policy**

**CRITICAL**: System has ZERO fallback ranges anywhere.

- ❌ NO category-level fallback ranges
- ❌ NO default property values
- ❌ NO template fallbacks
- ❌ NO "use category range if material missing"
- ✅ Materials.yaml MUST have 100% complete data
- ✅ Export fails if data incomplete (fail-fast)
- ✅ Categories.yaml provides metadata only, NOT fallback values

## 🔄 Data Storage Policy

**ALL frontmatter files are OUTPUT ONLY - never data storage.**

- ✅ **Materials.yaml** - Single source of truth (ALL operations happen here)
- ✅ **Categories.yaml** - Category metadata (reference only, NO fallbacks)
- ❌ **Frontmatter files** - OUTPUT ONLY (trivial export, no persistence)
- **Data Flow**: Materials.yaml (100% complete) → Frontmatter (simple copy)
- **See**: `docs/data/DATA_STORAGE_POLICY.md` for complete policy

## �🚀 Production Status (September 26, 2025)

### ✅ **PRODUCTION READY**
- **123 Materials Supported**: Full production database with comprehensive material coverage
- **Categories.yaml v2.2.1**: Streamlined templates with verbosity reduction for cleaner output
- **Batch Processing**: Tested and validated for production-scale generation
- **Performance Optimized**: ~450 character reduction per frontmatter improves generation speed
- **Quality Assurance**: Comprehensive test validation for all material categories

### **Production Material Coverage**
```
9 Material Categories (123 total materials):
- METAL: 35 materials - Industrial metals and alloys
- WOOD: 20 materials - Natural and engineered wood products
- STONE: 18 materials - Natural stone and engineered stone
- COMPOSITE: 13 materials - Fiber-reinforced composites
- GLASS: 11 materials - Specialty glass and optical materials
- CERAMIC: 9 materials - Technical and structural ceramics
- MASONRY: 7 materials - Construction masonry materials
- PLASTIC: 6 materials - Engineering plastics
- SEMICONDUCTOR: 4 materials - Electronic substrate materials
```

### **Real System Commands**
```bash
# Generate frontmatter for all 123 materials (real command)
python3 run.py --all --components "frontmatter"

# Generate specific material frontmatter
python3 run.py --material "aluminum" --components "frontmatter"

# Test frontmatter generation
python3 run.py --material "copper" --components "frontmatter" --test

# Validate system functionality
python3 -c "from components.frontmatter.core.streamlined_generator import StreamlinedFrontmatterGenerator; print('✅ Component ready')"
```

## 🔄 Version 7.0.0 Features (Categories.yaml v2.2.1)

### Regulatory Standards Organization Enrichment (November 7, 2025)
The frontmatter exporter now automatically enriches regulatory standards metadata during export:

- **Automatic Organization Detection**: Detects SEMI, ASTM, EPA, USDA, FSC, UNESCO, CITES in standard descriptions
- **Metadata Enrichment**: Populates proper organization name, official URLs, and organization-specific logos
- **Zero Manual Work**: All 132 materials automatically enriched - no "Unknown" organizations in production
- **12 Organizations Supported**: SEMI, ASTM, EPA, USDA, FSC, UNESCO, CITES, FDA, ANSI, IEC, ISO, OSHA

**Enrichment Examples:**
```yaml
# BEFORE (Materials.yaml)
regulatory_standards:
  - name: Unknown
    description: SEMI M1 - Specification for Polished Single Crystal Silicon Wafers
    url: ''
    image: /images/logo/logo-org-generic.png

# AFTER (Frontmatter export)
regulatory_standards:
  - name: SEMI
    description: SEMI M1 - Specification for Polished Single Crystal Silicon Wafers
    url: https://store-us.semi.org/products/semi-m1
    image: /images/logo/logo-org-semi.png
```

**Organization URL Patterns:**
- **SEMI**: `https://store-us.semi.org/products/semi-{id}` (e.g., semi-m1)
- **ASTM**: `https://store.astm.org/{id}.html` (e.g., f1188.html, c848.html)
- **EPA Clean Air Act**: `https://www.epa.gov/clean-air-act-overview`
- **EPA 40 CFR**: `https://www.ecfr.gov/current/title-40/part-{number}`
- **USDA Food Safety**: `https://www.usda.gov/topics/food-and-nutrition/food-safety`
- **FSC Forestry**: `https://fsc.org/en/forest-management-certification`
- **UNESCO Heritage**: `https://whc.unesco.org/en/conservation/`
- **CITES**: `https://cites.org/`

**Test Coverage**: See `tests/frontmatter/test_regulatory_standards_enrichment.py` (16/16 tests passing)

### Enhanced Verbosity Reduction (Production Validated)
- **Streamlined Templates**: Removed verbose fields while preserving essential information across all 123 materials
- **Cleaner Output**: Reduced frontmatter verbosity by ~450 characters per material for improved performance
- **Essential Information Preserved**: All critical data maintained in concise format - production tested
- **Faster Processing**: Optimized generation pipeline handles batch processing of all material categories
- **Quality Metrics**: Production validation shows 95%+ essential data retention with 25% size reduction

### Abbreviation Template System (New)
- **Standardized Abbreviations**: Professional formatting for materials with industry-standard abbreviations (FRPU, GFRP, CFRP, etc.)
- **Consistent Presentation**: Unified template for name, subcategory, and title fields
- **8 Supported Materials**: FRPU, GFRP, CFRP, MMCs, CMCs, MDF, PVC, PTFE with standardized formatting
- **Documentation**: See [ABBREVIATION_TEMPLATE.md](docs/ABBREVIATION_TEMPLATE.md) for complete details

### Materials.yaml-Only Generation (October 2025)
- **Zero AI Dependencies**: No API calls, no costs, no variability
- **Template-Based Subtitles**: Deterministic subtitle generation using material name and specifications
- **Performance**: 10-15x faster generation (1-3 seconds vs 15-45 seconds)
- **Reliability**: No network dependencies, timeout issues, or API failures
- **Consistency**: Same input always produces identical output
- **Cost**: $0.00 per generation (was $0.002-0.008)

### Key Migration from Materials.yaml to Categories.yaml
- **Standardized Descriptions**: Machine settings and material properties now use standardized descriptions from Categories.yaml v2.2.1
- **Environmental Impact**: Automated generation of environmental benefit sections using concise standardized templates  
- **Application Types**: Consistent application category definitions with streamlined quality metrics and industry mappings
- **Outcome Metrics**: Standardized measurement frameworks for cleaning effectiveness validation
- **Verbose Field Elimination**: Removed `regulatory_advantages`, `typical_savings`, `efficiency_metrics`, `health_benefits`, `workplace_safety`, `preservation_focus`, `specialized_requirements`, etc.

### New Frontmatter Sections (Concise)
```yaml
environmentalImpact:
  - benefit: "Chemical Waste Elimination"
    description: "Eliminates hazardous chemical waste streams"
    applicableIndustries: ["Semiconductor", "Electronics", "Medical", "Nuclear"]
    quantifiedBenefits: "Up to 100% reduction in chemical cleaning agents"

applicationTypes:
  - type: "Precision Cleaning" 
    description: "High-precision removal of microscopic contaminants and residues"
    industries: ["Semiconductor", "MEMS", "Optics", "Medical Devices"]
    qualityMetrics: ["Particle count reduction", "Surface roughness maintenance", "Chemical purity"]
    typicalTolerances: "Sub-micron accuracy with minimal substrate impact"

outcomeMetrics:
  - metric: "Contaminant Removal Efficiency"
    description: "Percentage of target contaminants successfully removed from surface"
    measurementMethods: ["Before/after microscopy", "Chemical analysis", "Mass spectrometry"]
    typicalRanges: "95-99.9% depending on application and material"
    factorsAffecting: ["Contamination type", "Adhesion strength", "Surface geometry"]
```

## 🧭 Breadcrumb Navigation (v9.1.0 - November 6, 2025)

### Hierarchical Navigation Structure

All material frontmatter files now include breadcrumb navigation with a 5-level hierarchy:

**Home → Materials → Category → Subcategory → Material**

### Breadcrumb Format

```yaml
breadcrumb:
  - label: "Home"
    href: "/"
  - label: "Materials"
    href: "/materials"
  - label: "{Category}"              # e.g., "Metal", "Stone", "Wood"
    href: "/materials/{category}"    # e.g., "/materials/metal"
  - label: "{Subcategory}"           # e.g., "Non Ferrous", "Hardwood"
    href: "/materials/{category}/{subcategory}"
  - label: "{Material Name}"         # e.g., "Aluminum"
    href: "/materials/{slug}"        # e.g., "/materials/aluminum-laser-cleaning"
```

### Examples by Category

| Material | Category | Subcategory | Full Path |
|----------|----------|-------------|-----------|
| Aluminum | Metal | Non Ferrous | Home → Materials → Metal → Non Ferrous → Aluminum |
| Granite | Stone | Igneous | Home → Materials → Stone → Igneous → Granite |
| Oak | Wood | Hardwood | Home → Materials → Wood → Hardwood → Oak |
| Polycarbonate | Plastic | Thermoplastic | Home → Materials → Plastic → Thermoplastic → Polycarbonate |
| Fiberglass | Composite | Fiber Reinforced | Home → Materials → Composite → Fiber Reinforced → Fiberglass |
| Brick | Masonry | General | Home → Materials → Masonry → General → Brick |

### URL Structure

- **Home**: `/`
- **Materials Index**: `/materials`
- **Category Pages**: `/materials/{category}` (e.g., `/materials/metal`)
- **Subcategory Pages**: `/materials/{category}/{subcategory}` (e.g., `/materials/metal/non-ferrous`)
- **Material Detail**: `/materials/{slug}` (e.g., `/materials/aluminum-laser-cleaning`)

### Implementation

Breadcrumbs are auto-generated during frontmatter export by `TrivialFrontmatterExporter._generate_breadcrumb()`:

```python
def _generate_breadcrumb(self, material_data: Dict, slug: str) -> list:
    """Generate breadcrumb navigation for materials."""
    breadcrumb = [{"label": "Home", "href": "/"}]
    breadcrumb.append({"label": "Materials", "href": "/materials"})
    
    category = material_data.get('category', '').title()
    if category:
        breadcrumb.append({
            "label": category,
            "href": f"/materials/{category.lower()}"
        })
    
    subcategory = material_data.get('subcategory', '')
    if subcategory:
        breadcrumb.append({
            "label": subcategory.replace('-', ' ').title(),
            "href": f"/materials/{category.lower()}/{subcategory.lower()}"
        })
    
    name = material_data.get('name', '')
    if name:
        breadcrumb.append({
            "label": name,
            "href": f"/materials/{slug}"
        })
    
    return breadcrumb
```

### Coverage

- ✅ **132/132 materials** have breadcrumb navigation (100%)
- ✅ **All categories** covered (Metal, Stone, Wood, Plastic, Composite, Glass, Ceramic, Masonry, Semiconductor)
- ✅ **All subcategories** included in navigation hierarchy
- ✅ **Tested**: See `tests/frontmatter/test_breadcrumb.py` for comprehensive test suite (12/12 tests passing)

### Testing

```bash
# Run breadcrumb tests
python3 -m pytest tests/frontmatter/test_breadcrumb.py -v

# Verify breadcrumb in specific material
head -n 18 frontmatter/materials/aluminum-laser-cleaning.yaml
```

## 🏗️ Hierarchical Architecture

### Core Principle
Frontmatter uses a **hierarchical structure** with `properties` and `laserProcessing` instead of flat `properties`/`machine_settings`.

### Format Example
```yaml
# Modern Hierarchical Structure
name: Aluminum

# Breadcrumb Navigation (v9.1.0 - November 6, 2025)
breadcrumb:
  - label: "Home"
    href: "/"
  - label: "Materials"
    href: "/materials"
  - label: "Metal"
    href: "/materials/metal"
  - label: "Non Ferrous"
    href: "/materials/metal/non-ferrous"
  - label: "Aluminum"
    href: "/materials/aluminum-laser-cleaning"

properties:
  chemical:
    formula: "Al"                    # Chemical composition
    symbol: "Al"                     # Chemical symbol
    chemicalFormula: "Al"            # Alternative notation
  physical:
    density: 2.7                     # Pure numeric (float)
    densityUnit: "g/cm³"            # Unit in separate field
    densityMin: 0.53                # Min range numeric
    densityMax: 22.59               # Max range numeric
  mechanical:
    tensileStrength: 310            # Pure numeric (int)
    tensileStrengthUnit: "MPa"      # Unit in separate field
    tensileStrengthMin: 70          # Min range numeric
    tensileStrengthMax: 2000        # Max range numeric
  thermal:
    thermalConductivity: 237        # Pure numeric (int)
    thermalConductivityUnit: "W/m·K" # Unit in separate field

laserProcessing:
  recommended:
    powerRange: 150.0               # Pure numeric (float)
    powerRangeUnit: "W"             # Unit in separate field
    powerRangeMin: 20.0             # Min range numeric
    powerRangeMax: 500.0            # Max range numeric
    wavelength: 1064.0              # Pure numeric (float)
    wavelengthUnit: "nm"            # Unit in separate field
    beamProfile: "Gaussian TEM00"   # Standard settings
    beamProfileOptions: 
      - "Gaussian TEM00"
      - "Top-hat"
      - "Donut"
      - "Multi-mode"
    safetyClass: "Class 4 (requires full enclosure)"

# New v6.2.0 Standardized Sections
environmentalImpact:
  - benefit: "Chemical Waste Elimination"
    description: "Laser cleaning eliminates hazardous chemical waste streams"
    applicableIndustries: ["Semiconductor", "Electronics", "Medical"]
    quantifiedBenefits: "Up to 100% reduction in chemical cleaning agents"

applicationTypes:
  - type: "Precision Cleaning"
    description: "High-precision removal of microscopic contaminants and residues"
    industries: ["Semiconductor", "MEMS", "Optics", "Medical Devices"]
    qualityMetrics: ["Particle count reduction", "Surface roughness maintenance"]

outcomeMetrics:
  - metric: "Contaminant Removal Efficiency" 
    description: "Percentage of target contaminants successfully removed from surface"
    measurementMethods: ["Before/after microscopy", "Chemical analysis"]
    typicalRanges: "95-99.9% depending on application and material"
```

## 🏗️ Key Components

### StreamlinedFrontmatterGenerator

**Dual-Source Architecture**: Materials.yaml for properties, Settings.yaml for machine settings. No AI API calls, completely deterministic output.

- **properties**: Extracted directly from Materials.yaml `properties` section
- **machine_settings**: Extracted from Settings.yaml `machine_settings` section
- **environmentalImpact**: Sourced from Materials.yaml `environmentalImpact` field
- **applications**: Uses Materials.yaml `applications` data
- **author**: Extracted from Materials.yaml `author` field

### Core Generation Methods

1. **`_generate_from_yaml(material_name, material_data)`** → Complete frontmatter
   - Extracts all data directly from Materials.yaml
   - Uses template values for missing machine settings
   - Generates deterministic subtitle from material name
   - No API calls, completely self-contained

2. **`_generate_machine_settings_with_ranges(material_data, material_name)`** → machine_settings  
   - Uses Settings.yaml `machine_settings` section
   - Template fallback: Standard laser parameters (1064nm wavelength, 50-200W power, etc.)
   - No AI calculation, uses proven template values

3. **`_generate_author(material_data)`** → Author information
   - Extracts author directly from Materials.yaml `author` field
   - Template fallback: Default technical expert profile
   - No external author system dependencies

4. **`_generate_images_section(material_name)`** → Image URLs
   - Template-based image URL generation using material name
   - Consistent URL patterns for hero images
   - No external image processing
Core generator with hierarchical structure and real system capabilities:

```python
from components.frontmatter.core.streamlined_generator import StreamlinedFrontmatterGenerator

# Single material generation (real method)
generator = StreamlinedFrontmatterGenerator()
result = generator.generate("Aluminum")

# Check if generator is working
if result:
    print(f"✅ Generated frontmatter for Aluminum: {len(result)} characters")
else:
    print("❌ Generation failed")
```

**Key Methods:**
- `_extract_property_data()`: Unified extraction for values, ranges, and units
- `_generate_from_materials_data()`: Creates hierarchical properties/laserProcessing structure
- `generate()`: Main entry point returning ComponentResult with YAML content

### Hierarchical Structure Benefits
- **Organized**: Properties grouped by category (chemical, physical, mechanical, thermal)
- **Extensible**: Easy to add new property categories or laser processing sections
- **Clear**: Logical separation between material properties and processing parameters
- **Schema-compliant**: Matches modern frontmatter.json schema requirements

### PropertyEnhancementService
Processes and enhances properties while preserving numeric format:

```python
from components.frontmatter.enhancement.unified_property_enhancement_service import PropertyEnhancementService

# Apply enhancement while preserving Min/Max/Unit structure
PropertyEnhancementService.add_properties(frontmatter, preserve_min_max=True)
```

**Key Features:**
- Processes Min/Max fields containing units
- Preserves existing numeric values
- Extracts units into separate fields
- Maintains schema compliance

## 📋 Supported Fields

### Properties
- **Main Values**: `density`, `meltingPoint`, `thermalConductivity`, `tensileStrength`, `hardness`, `youngsModulus`
- **Min/Max Ranges**: All main values have corresponding `*Min` and `*Max` fields
- **Units**: All main values have corresponding `*Unit` fields

### Machine Settings
- **Main Values**: `powerRange`, `wavelength`, `pulseDuration`, `spotSize`, `repetitionRate`, `fluenceRange`
- **Min/Max Ranges**: All main values have corresponding `*Min` and `*Max` fields
- **Units**: All main values have corresponding `*Unit` fields

## 🧪 Testing

### Unit Value Separation Tests
```bash
python -m pytest components/frontmatter/tests/test_unit_value_separation.py -v
```

**Test Coverage:**
- Numeric value generation
- Min/Max field processing
- Schema validation
- Enhancement service behavior

### Schema Validation Tests
```bash
python -m pytest tests/validation/test_schema_validation.py -v
```

**Test Coverage:**
- Schema enforcement of numeric types
- Validation of generated content
- Rejection of invalid string values
- Unit field type validation

## 🔧 Configuration

### Materials Data
The component uses `data/Materials.yaml` as the primary data source:

```yaml
materials:
  metal:
    items:
      - name: "Copper"
        density: 8.96
        melting_point: 1085
        thermalConductivity: 401
        # ... more properties
```

### Category Ranges
Min/Max ranges are defined in materials configuration:
```yaml
category_ranges:
  metal:
    density:
      min: 0.53
      max: 22.59
      unit: "g/cm³"
```

## 🚀 Usage Examples

### Basic Generation
```python
from components.frontmatter.core.streamlined_generator import StreamlinedFrontmatterGenerator

generator = StreamlinedFrontmatterGenerator()
result = generator.generate("Bronze", use_api=False)

if result.success:
    print(f"Generated {len(result.content)} characters")
    # Save to file
    with open("bronze-frontmatter.yaml", "w") as f:
        f.write(result.content)
```

### Validation
```python
import yaml
import json
import jsonschema

# Parse generated content
content = result.content.strip()
yaml_content = content.split('---', 2)[1]
frontmatter_data = yaml.safe_load(yaml_content)

# Load and validate against schema
with open("schemas/frontmatter.json", "r") as f:
    schema = json.load(f)

jsonschema.validate(frontmatter_data, schema)
print("✅ Schema validation passed!")
```

### Check Numeric Format
```python
properties = frontmatter_data.get('properties', {})
machine_settings = frontmatter_data.get('machine_settings', {})

# Count numeric values
numeric_props = [k for k, v in properties.items() 
                 if isinstance(v, (int, float)) and not k.endswith('Unit')]
numeric_machine = [k for k, v in machine_settings.items() 
                   if isinstance(v, (int, float)) and not k.endswith('Unit')]

print(f"Properties: {len(numeric_props)} numeric values")
print(f"Machine Settings: {len(numeric_machine)} numeric values")
```

## 🔄 Migration from Old Format

If you have frontmatter files with the old format (units in values), they can be regenerated:

```bash
# Regenerate all materials with new format
python run.py --material "Copper" --regenerate
python run.py --material "Bronze" --regenerate
```

## 📊 Benefits

### For Developers
- **Type Safety**: Numeric values enable direct mathematical operations
- **Consistency**: All files follow the same numeric-only format
- **Validation**: Schema ensures data integrity
- **Processing**: No need to parse units from values

### For Data Processing
- **Direct Calculations**: `density * volume` works immediately
- **Range Validation**: `value >= densityMin and value <= densityMax`
- **Unit Conversion**: Units accessible for conversion logic
- **Database Storage**: Clean numeric types for database fields

### For Maintenance
- **Clear Separation**: Values vs units are obviously separated
- **Schema Enforcement**: Invalid formats are rejected
- **Test Coverage**: Comprehensive validation ensures reliability
- **Documentation**: Clear examples and usage patterns

## 🐛 Troubleshooting

### Common Issues

**Issue**: Missing new standardized sections in generated frontmatter
```yaml
# Missing sections
# environmentalImpact: (missing)
# applicationTypes: (missing)
# outcomeMetrics: (missing)
```

**Solution**: Ensure Categories.yaml is version 2.2.1 or higher and contains the streamlined standardized description sections.

**Issue**: Verbose fields still present in frontmatter sections
```yaml
# Old verbose format (should not appear)
environmentalImpact:
  - regulatory_advantages: "..."
    workplace_safety: "..."
    typical_savings: "..."
```

**Solution**: Regenerate the material with the updated v6.2.1 generator which uses streamlined templates from Categories.yaml v2.2.1.

**Issue**: Min/Max fields contain strings with units
```yaml
# Wrong
meltingMax: "2800°C"

# Right  
meltingMax: 2800
meltingPointUnit: "°C"
```

**Solution**: Regenerate the material with the updated generator.

**Issue**: Schema validation fails
```
ValidationError: 'string value' is not of type 'number'
```

**Solution**: Check that all value fields are numeric, not strings.

**Issue**: Environmental impact section is empty or malformed
```yaml
environmentalImpact: []  # Empty
```

**Solution**: Verify Categories.yaml v2.2.1 contains environmentalImpactTemplates section with concise templates.

## 📈 Version History

- **v9.2.0**: Regulatory Standards Organization Enrichment (November 7, 2025)
  - ✅ **Automatic metadata enrichment** for 12 regulatory organizations
  - ✅ **SEMI, ASTM, EPA, USDA, FSC, UNESCO, CITES** detection and URL generation
  - ✅ **Zero "Unknown" organizations** in production (100% enrichment)
  - ✅ **Organization-specific logos** and official URLs
  - ✅ **Comprehensive test coverage** (16/16 tests passing)
  - ✅ **Intelligent pattern matching** for CFR numbers, standard IDs, acts
  - 📄 Test Suite: `tests/frontmatter/test_regulatory_standards_enrichment.py`

- **v9.1.0**: Breadcrumb Navigation (November 6, 2025)
  - ✅ **Auto-generated breadcrumbs** for all 132 materials
  - ✅ **5-level hierarchy** (Home → Materials → Category → Subcategory → Material)
  - ✅ **Progressive URL structure** for navigation
  - ✅ **100% test coverage** with comprehensive test suite
  - ✅ **Schema integration** - breadcrumb field added to MaterialContent

- **v9.0.0**: Trivial Export Architecture (October 25, 2025)
  - Major architectural shift: ALL operations on Materials.yaml
  - Frontmatter export reduced to trivial YAML-to-YAML copy
  - Zero fallback ranges policy implemented
  - Performance: 132 materials in ~10 seconds

- **v8.0.0**: Materials.yaml-Only Generation (October 21, 2025)
  - ❌ **Removed ALL AI API dependencies** - zero API calls
  - ✅ **100% Materials.yaml-based** - deterministic output
  - ✅ **10-15x performance improvement** (1-3s vs 15-45s)
  - ✅ **Zero costs** ($0.00 vs $0.002-0.008 per generation)
  - ✅ **Template fallbacks** for missing data (machine settings, author)
  - ✅ **Reliability** - no network dependencies, timeouts, or failures
  - ✅ **Consistency** - same input always produces identical output

- **v7.0.0**: AI-Enhanced Generation (deprecated)
- **v6.2.1**: Categories.yaml v2.2.1 verbosity reduction
- **v6.2.0**: Categories.yaml v2.2.0 integration
- **v6.1.0**: Unit/value separation implementation
- **v6.0.0**: Pure AI research system (deprecated)
- **v3.0.0**: Root-level frontmatter architecture
- **v2.0.0**: Streamlined generator implementation