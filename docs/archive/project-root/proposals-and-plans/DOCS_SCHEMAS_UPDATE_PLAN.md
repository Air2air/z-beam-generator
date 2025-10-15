# Property Data Structure Documentation Update

**Date**: October 15, 2025  
**Related**: Priority 2 Research Automation, Generator Pattern Awareness Update  
**Files to Update**: 5

---

## Summary

Documentation and schemas need updates to reflect the new property data patterns introduced by Priority 2 research automation. Current docs describe only the legacy format, but 224 properties across 91 materials now use advanced patterns (pulse-specific, wavelength-specific).

---

## Required Updates

### 1. DATA_ARCHITECTURE.md ⚠️ NEEDS UPDATE

**Current State**: Only describes legacy format  
**Missing**: 3 new property patterns (pulse-specific, wavelength-specific, authoritative)

**Add Section**:
```markdown
## Property Data Patterns (as of Oct 2025)

### Pattern Evolution

The system supports 4 property data patterns, reflecting the evolution from AI-generated to research-backed authoritative data:

#### 1. Legacy Format (Original)
```yaml
ablationThreshold:
  value: 0.8
  unit: "J/cm²"
  confidence: 80
  description: "Laser ablation threshold"
  min: null
  max: null
```
- **Used by**: ~800 properties in 122 materials
- **Source**: Original AI generation
- **Confidence**: 70-85%

#### 2. Pulse-Specific Format (Priority 2 Authoritative)
```yaml
ablationThreshold:
  nanosecond:
    min: 2.0
    max: 8.0
    unit: "J/cm²"
  picosecond:
    min: 0.1
    max: 2.0
    unit: "J/cm²"
  femtosecond:
    min: 0.14
    max: 1.7
    unit: "J/cm²"
  source: "Marks et al. 2022, Precision Engineering"
  confidence: 90
  measurement_context: "Varies by pulse duration (ns/ps/fs)"
```
- **Used by**: 45 properties (36 metals, 7 ceramics, 2 glasses)
- **Source**: Peer-reviewed research (Priority 2 automation)
- **Confidence**: 90%
- **Properties**: ablationThreshold

#### 3. Wavelength-Specific Format (Priority 2 Authoritative)
```yaml
reflectivity:
  at_1064nm:
    min: 85
    max: 98
    unit: "%"
  at_532nm:
    min: 70
    max: 95
    unit: "%"
  at_355nm:
    min: 55
    max: 85
    unit: "%"
  at_10640nm:
    min: 95
    max: 99
    unit: "%"
  source: "Handbook of Optical Constants (Palik)"
  confidence: 85
  measurement_context: "Varies by laser wavelength"
```
- **Used by**: 35 properties (metals only)
- **Source**: Handbook of Optical Constants (Palik)
- **Confidence**: 85%
- **Properties**: reflectivity

#### 4. Authoritative Format (Priority 2 Enhanced Legacy)
```yaml
thermalConductivity:
  value: 401
  unit: "W/(m·K)"
  confidence: 85
  description: "Thermal conductivity of pure copper at 20°C"
  min: 15
  max: 400
  source: "MatWeb Materials Database"
  notes: "Typical range for metal materials at room temperature"
```
- **Used by**: ~144 properties across ~60 materials
- **Source**: Research databases (NIST, ASM, MatWeb, etc.)
- **Confidence**: 75-90%
- **Properties**: thermalConductivity, porosity, oxidationResistance, surfaceRoughness

### Pattern Detection

Generators use `_detect_property_pattern()` to identify format:
- Checks for `nanosecond/picosecond/femtosecond` keys → pulse-specific
- Checks for `at_1064nm/at_532nm/at_355nm/at_10640nm` keys → wavelength-specific
- Checks for `source` + high confidence (>85%) → authoritative
- Checks for `source` or `notes` → legacy-sourced
- Default → legacy

### Value Extraction

Generators use `_extract_property_value()` for pattern-aware extraction:
- Pulse-specific: Returns average of preferred pulse duration (default: nanosecond)
- Wavelength-specific: Returns average of preferred wavelength (default: 1064nm)
- Legacy: Returns `value` field or min/max average
- Fallback: Returns 0

### Generator Compatibility

**Updated Generators**:
- ✅ `streamlined_generator.py` - Pattern-aware value extraction
- ✅ Preserves authoritative structures during tag generation
- ✅ Handles all 4 patterns transparently

**Preservation Logic**:
Generators should NOT overwrite pulse-specific or wavelength-specific patterns during regeneration. Check pattern before regenerating any property.
```

### 2. schemas/active/datametrics.json ⚠️ NEEDS UPDATE

**Current State**: Only defines legacy single-value format  
**Missing**: Support for pulse-specific and wavelength-specific structures

**Update Required**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "DataMetric Schema",
  "description": "Schema for property values - supports legacy, pulse-specific, and wavelength-specific formats",
  "oneOf": [
    {
      "$ref": "#/definitions/LegacyDataMetric"
    },
    {
      "$ref": "#/definitions/PulseSpecificDataMetric"
    },
    {
      "$ref": "#/definitions/WavelengthSpecificDataMetric"
    }
  ],
  "definitions": {
    "LegacyDataMetric": {
      "type": "object",
      "description": "Legacy format with single value",
      "required": ["value", "unit", "confidence"],
      "properties": {
        "value": {"type": "number"},
        "unit": {"type": "string"},
        "min": {"type": ["number", "null"]},
        "max": {"type": ["number", "null"]},
        "confidence": {"type": "number", "minimum": 0, "maximum": 100},
        "description": {"type": "string"},
        "source": {"type": "string"},
        "notes": {"type": "string"}
      }
    },
    "PulseSpecificDataMetric": {
      "type": "object",
      "description": "Pulse-specific format (ns/ps/fs)",
      "required": ["confidence"],
      "properties": {
        "nanosecond": {
          "type": "object",
          "required": ["min", "max", "unit"],
          "properties": {
            "min": {"type": "number"},
            "max": {"type": "number"},
            "unit": {"type": "string"}
          }
        },
        "picosecond": {
          "type": "object",
          "required": ["min", "max", "unit"],
          "properties": {
            "min": {"type": "number"},
            "max": {"type": "number"},
            "unit": {"type": "string"}
          }
        },
        "femtosecond": {
          "type": "object",
          "required": ["min", "max", "unit"],
          "properties": {
            "min": {"type": "number"},
            "max": {"type": "number"},
            "unit": {"type": "string"}
          }
        },
        "source": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 100},
        "measurement_context": {"type": "string"}
      }
    },
    "WavelengthSpecificDataMetric": {
      "type": "object",
      "description": "Wavelength-specific format (1064/532/355/10640nm)",
      "required": ["confidence"],
      "properties": {
        "at_1064nm": {
          "type": "object",
          "required": ["min", "max", "unit"],
          "properties": {
            "min": {"type": "number"},
            "max": {"type": "number"},
            "unit": {"type": "string"}
          }
        },
        "at_532nm": {
          "type": "object",
          "required": ["min", "max", "unit"],
          "properties": {
            "min": {"type": "number"},
            "max": {"type": "number"},
            "unit": {"type": "string"}
          }
        },
        "at_355nm": {
          "type": "object",
          "required": ["min", "max", "unit"],
          "properties": {
            "min": {"type": "number"},
            "max": {"type": "number"},
            "unit": {"type": "string"}
          }
        },
        "at_10640nm": {
          "type": "object",
          "required": ["min", "max", "unit"],
          "properties": {
            "min": {"type": "number"},
            "max": {"type": "number"},
            "unit": {"type": "string"}
          }
        },
        "source": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 100},
        "measurement_context": {"type": "string"}
      }
    }
  }
}
```

### 3. schemas/SCHEMA_INDEX.md ⚠️ NEEDS UPDATE

**Add Section**:
```markdown
## Property Data Patterns (Oct 2025 Update)

As of October 2025, property data supports 4 distinct patterns:

1. **Legacy Format**: Single value with min/max (~800 properties)
2. **Pulse-Specific**: Nanosecond/picosecond/femtosecond ranges (45 properties)
3. **Wavelength-Specific**: 1064/532/355/10640nm ranges (35 properties)
4. **Authoritative**: Legacy + source attribution (144 properties)

See `schemas/active/datametrics.json` for validation rules and `docs/DATA_ARCHITECTURE.md` for usage examples.

### Validation Considerations

- Validators should accept any of the 4 patterns
- Pattern detection logic in `streamlined_generator.py`
- Backward compatibility maintained - legacy format still valid
```

### 4. docs/QUICK_REFERENCE.md ⚠️ NEEDS UPDATE

**Add Section**:
```markdown
## Property Data Formats

**Q**: What property data formats are supported?

**A**: Four formats (as of Oct 2025):

1. **Legacy** - Single value: `{value, unit, min, max, confidence, description}`
2. **Pulse-specific** - NS/PS/FS: `{nanosecond: {min, max, unit}, picosecond: {...}, ...}`
3. **Wavelength-specific** - 4 wavelengths: `{at_1064nm: {min, max, unit}, at_532nm: {...}, ...}`
4. **Authoritative** - Legacy + source: `{value, unit, min, max, source, notes, confidence}`

See `FRONTMATTER_NORMALIZATION_REPORT.md` for detailed analysis.

**Q**: How do generators handle different property formats?

**A**: Generators use pattern-aware extraction:
- `_detect_property_pattern()` identifies format type
- `_extract_property_value()` extracts appropriate value
- Pulse/wavelength patterns preserved during regeneration
- See `GENERATOR_PATTERN_AWARENESS_UPDATE.md`
```

### 5. docs/components/frontmatter/README.md ⚠️ CHECK IF EXISTS

If exists, add:
```markdown
## Property Data Evolution

### Pattern Types

Frontmatter properties support 4 data patterns (Oct 2025):

1. **Legacy** (~800 properties)
2. **Pulse-Specific** (45 ablation thresholds)
3. **Wavelength-Specific** (35 reflectivity values)
4. **Authoritative** (144 sourced properties)

### Generator Support

`streamlined_generator.py` includes pattern-aware methods:
- `_detect_property_pattern(prop_data)` - Identifies format
- `_extract_property_value(prop_data)` - Extracts values

### Testing

Run `python3 -m pytest tests/test_property_pattern_detection.py -v` to verify pattern handling (15 tests).
```

---

## Implementation Checklist

- [ ] Update `docs/DATA_ARCHITECTURE.md` - Add property patterns section
- [ ] Update `schemas/active/datametrics.json` - Add oneOf with 3 pattern definitions
- [ ] Update `schemas/SCHEMA_INDEX.md` - Add property patterns note
- [ ] Update `docs/QUICK_REFERENCE.md` - Add FAQ about property formats
- [ ] Check/update `docs/components/frontmatter/README.md` if exists
- [ ] Update `docs/INDEX.md` - Add links to new sections
- [ ] Commit all documentation updates

---

## Validation

After updates, verify:

1. Schema validates all 4 patterns:
```bash
# Test pulse-specific
python3 -c "import json, jsonschema, yaml
with open('schemas/active/datametrics.json', 'r') as f:
    schema = json.load(f)
test_data = {'nanosecond': {'min': 2, 'max': 8, 'unit': 'J/cm²'}, 'confidence': 90}
jsonschema.validate(test_data, schema)
print('✅ Pulse-specific validates')
"
```

2. Documentation cross-references work:
- DATA_ARCHITECTURE.md links to FRONTMATTER_NORMALIZATION_REPORT.md
- QUICK_REFERENCE.md links to GENERATOR_PATTERN_AWARENESS_UPDATE.md
- INDEX.md includes new sections

3. Generators still work with all patterns:
```bash
python3 -m pytest tests/test_property_pattern_detection.py -v
```

---

## Timeline

**Estimated Time**: 1-2 hours
- Schema updates: 30 minutes
- Documentation updates: 30-60 minutes
- Testing/verification: 30 minutes

**Priority**: MEDIUM (system works without these updates, but docs are incomplete)
