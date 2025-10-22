# Data Completeness Policy

**Version**: 1.0  
**Date**: October 17, 2025  
**Status**: Active

---

## 🎯 Overview

This document defines the **100% Data Completeness** requirements for Z-Beam frontmatter generation. The system enforces comprehensive data coverage to ensure all generated content meets quality standards.

---

## 📊 Completeness Requirements

### 1. **All Essential Properties Must Be Present**

Every material must have all essential properties for its category:

#### **Metal** (11 required properties)
- Thermal: `thermalDestructionPoint`, `meltingPoint`, `thermalConductivity`
- Physical: `density`, `hardness`, `elasticModulus`, `tensileStrength`
- Optical: `reflectivity`, `absorptionCoefficient`
- Surface: `surfaceRoughness`
- Laser Interaction: `ablationThreshold`

#### **Ceramic** (10 required properties)
- `sinteringPoint`, `thermalConductivity`, `density`, `hardness`
- `elasticModulus`, `compressiveStrength`, `reflectivity`
- `absorptionCoefficient`, `ablationThreshold`, `surfaceRoughness`

#### **Plastic** (10 required properties)
- `degradationPoint`, `meltingPoint`, `thermalConductivity`, `density`
- `tensileStrength`, `elasticModulus`, `reflectivity`
- `absorptionCoefficient`, `ablationThreshold`, `surfaceRoughness`

#### **Composite** (9 required properties)
- `degradationPoint`, `thermalConductivity`, `density`
- `tensileStrength`, `elasticModulus`, `reflectivity`
- `absorptionCoefficient`, `ablationThreshold`, `surfaceRoughness`

#### **Wood** (8 required properties)
- `thermalDestructionPoint`, `density`, `thermalConductivity`
- `hardness`, `moistureContent`, `reflectivity`
- `absorptionCoefficient`, `ablationThreshold`

#### **Stone** (9 required properties)
- `thermalDegradationPoint`, `density`, `hardness`
- `compressiveStrength`, `thermalConductivity`, `reflectivity`
- `absorptionCoefficient`, `ablationThreshold`, `surfaceRoughness`

#### **Glass** (9 required properties)
- `softeningPoint`, `thermalConductivity`, `density`
- `hardness`, `elasticModulus`, `reflectivity`
- `absorptionCoefficient`, `ablationThreshold`, `surfaceRoughness`

#### **Semiconductor** (9 required properties)
- `thermalDestructionPoint`, `thermalConductivity`, `density`
- `hardness`, `bandGap`, `reflectivity`
- `absorptionCoefficient`, `ablationThreshold`, `surfaceRoughness`

#### **Masonry** (8 required properties)
- `thermalDegradationPoint`, `density`, `hardness`
- `compressiveStrength`, `thermalConductivity`, `reflectivity`
- `absorptionCoefficient`, `ablationThreshold`

### 2. **No Empty Sections Allowed**

Both `materialProperties` and `machineSettings` must be populated:

```yaml
# ❌ INVALID - Empty sections
materialProperties: {}
machineSettings: {}

# ✅ VALID - Populated sections
materialProperties:
  laser_material_interaction:
    properties:
      reflectivity: {...}
machineSettings:
  powerRange: {...}
```

### 3. **Essential Machine Settings Required**

All 7 machine settings must be present:
- `powerRange` - Laser power specification
- `wavelength` - Operating wavelength (typically 1064 nm)
- `pulseWidth` - Pulse duration (ns, ps, fs)
- `repetitionRate` - Pulse frequency (kHz)
- `scanSpeed` - Scanning velocity (mm/s)
- `spotSize` - Beam diameter (μm)
- `fluenceThreshold` - Ablation threshold (J/cm²)

### 4. **All Values Must Be Validated**

Every property requires:
- **Value**: Numerical or qualitative data
- **Unit**: Measurement unit (except dimensionless)
- **Confidence**: AI research confidence score (0-100)
- **Description**: Human-readable explanation
- **Min/Max**: Range bounds where applicable

```yaml
# ✅ VALID - Complete property
density:
  value: 2.70
  unit: g/cm³
  confidence: 98
  description: Density at room temperature (20°C)
  min: 2.68
  max: 2.72
```

### 5. **Qualitative Properties Must Be Categorized**

Qualitative properties (corrosionResistance, weldability, machinability, etc.) must be in `material_characteristics` category, **NOT** in technical categories like `laser_material_interaction`.

**System automatically migrates legacy qualitative properties** during generation.

---

## 🔧 Implementation

### Invisible Pipeline Integration

Completeness validation runs **automatically** during frontmatter generation:

```python
def generate(self, material_name: str, **kwargs):
    # ... generation logic ...
    
    # Completeness validation (invisible to user)
    ordered_content = self._apply_completeness_validation(
        ordered_content, material_name, material_category
    )
    
    # ... continue generation ...
```

### Validation Steps (Automatic)

1. **Detect Empty Sections** → Trigger auto-remediation
2. **Migrate Legacy Qualitative Properties** → Re-categorize automatically
3. **Validate Essential Properties** → Check coverage
4. **Validate Confidence Scores** → Ensure all values researched
5. **Report Status** → Log warnings or errors

### Auto-Remediation

If `materialProperties` is empty:
1. **Trigger PropertyManager** for discovery
2. **Research missing properties** via AI
3. **Apply category ranges** automatically
4. **Re-validate** completeness

---

## 🚀 Usage

### Normal Mode (Default)

Logs warnings for incomplete data but continues generation:

```bash
python3 run.py --material "Aluminum" --components frontmatter
```

**Output**:
```
🔍 Validating 100% data completeness for Aluminum...
✅ Migrated 3 legacy qualitative properties
✅ 100% data completeness validated for Aluminum
✅ frontmatter generated successfully
```

### Strict Mode (Enforce Completeness)

**Fails generation** if data incomplete:

```bash
python3 run.py --material "Aluminum" --components frontmatter --enforce-completeness
```

**Output** (if incomplete):
```
🔍 Validating 100% data completeness for Aluminum...
❌ STRICT MODE: Data completeness validation failed for Aluminum:
  - Missing properties: 5
  - Missing: thermalDestructionPoint, meltingPoint, tensileStrength, ...
  
ERROR: STRICT MODE: Incomplete data for Aluminum. 
Run with --data-gaps to see research priorities.
```

---

## 📋 Validation Result Structure

```python
@dataclass
class CompletenessResult:
    is_complete: bool                        # Overall pass/fail
    missing_properties: List[str]            # Missing essential props
    empty_sections: List[str]                # Empty sections (materialProperties, machineSettings)
    legacy_qualitative: Dict[str, List[str]] # Qualitative props in wrong category
    unvalidated_values: List[str]            # Properties without confidence scores
    error_messages: List[str]                # Critical errors
    warnings: List[str]                      # Non-critical issues
```

---

## 🧪 Testing

Comprehensive test suite validates all requirements:

```bash
# Run completeness tests
pytest tests/test_data_completeness.py -v

# Run specific test
pytest tests/test_data_completeness.py::TestCompletenessValidator::test_complete_data_passes_validation -v
```

**Test Coverage**:
- ✅ Empty section detection
- ✅ Missing essential properties
- ✅ Legacy qualitative property detection
- ✅ Unvalidated value detection
- ✅ Strict mode enforcement
- ✅ Automatic migration
- ✅ Category-specific requirements
- ✅ Machine settings validation

---

## 📊 Completeness Metrics

### Essential Properties by Category

| Category | Essential Properties | Coverage Required |
|----------|---------------------|-------------------|
| **Metal** | 11 properties | 100% |
| **Ceramic** | 10 properties | 100% |
| **Plastic** | 10 properties | 100% |
| **Composite** | 9 properties | 100% |
| **Wood** | 8 properties | 100% |
| **Stone** | 9 properties | 100% |
| **Glass** | 9 properties | 100% |
| **Semiconductor** | 9 properties | 100% |
| **Masonry** | 8 properties | 100% |

### Machine Settings

| Setting | Required | Unit |
|---------|----------|------|
| `powerRange` | ✅ | W |
| `wavelength` | ✅ | nm |
| `pulseWidth` | ✅ | ns/ps/fs |
| `repetitionRate` | ✅ | kHz |
| `scanSpeed` | ✅ | mm/s |
| `spotSize` | ✅ | μm |
| `fluenceThreshold` | ✅ | J/cm² |

---

## 🔍 Troubleshooting

### "Empty materialProperties section"

**Cause**: No properties researched or loaded from YAML  
**Solution**: System auto-remediates by triggering PropertyManager research

### "Missing essential properties"

**Cause**: Material lacks required properties for its category  
**Solution**: 
- Use `--data-gaps` to see research priorities
- Run AI research: `python3 run.py --data=critical`

### "STRICT MODE: Incomplete data"

**Cause**: --enforce-completeness flag set and data incomplete  
**Solutions**:
1. Remove `--enforce-completeness` flag for normal mode
2. Research missing properties first
3. Fix data quality issues in Materials.yaml

### "Found legacy qualitative properties"

**Cause**: Qualitative properties in wrong category (pre-existing data)  
**Solution**: System automatically migrates during generation (no action needed)

---

## 📖 Related Documentation

- **PropertyManager** - Property discovery and research pipeline
- **PropertyProcessor** - Property categorization and processing
- **CompletenessValidator** - Validation implementation
- **GROK_INSTRUCTIONS.md** - Fail-fast principles and GROK compliance

---

## 🎯 Success Criteria

**100% Data Completeness Achieved When**:
1. ✅ All essential properties present for category
2. ✅ No empty sections (materialProperties, machineSettings)
3. ✅ All properties have confidence scores
4. ✅ Qualitative properties correctly categorized
5. ✅ All 7 machine settings present and researched
6. ✅ Validation passes with zero errors

---

## 📝 Version History

**v1.0** (October 17, 2025)
- Initial policy definition
- Comprehensive essential properties per category
- Auto-remediation pipeline
- Strict mode enforcement
- Legacy property migration
- Complete test coverage

---

**Author**: Z-Beam Development Team  
**Maintainer**: AI Assistant  
**Last Updated**: October 17, 2025
