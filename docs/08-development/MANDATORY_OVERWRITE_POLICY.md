# Mandatory Overwrite Policy

**Status**: ✅ IMPLEMENTED (January 13, 2026) / ✅ EXPANDED (February 2026)

**Purpose**: Ensure structural variety and distinctive properties are consistently applied.

## Overview

ALL backfill text generation MUST overwrite existing content, regardless of whether fields are already populated. This is mandatory for:

1. **Structural Variety**: Applying randomized structural patterns to prevent repetitive openings
2. **Distinctive Properties**: Incorporating material-specific quantitative values
3. **Quality Improvements**: Replacing generic placeholder text with rich content

## Scope Expansion (February 2026)

Mandatory overwrite now applies to coordinator-driven and postprocess text generation paths, not only backfill.

- `shared/domain/base_coordinator.py`
  - `generate_content()` now always regenerates/saves text, even when a component already has content.
  - Legacy `force_regenerate` parameter remains for compatibility but does not gate generation.
- `shared/commands/postprocess.py`
  - Existing text is always regenerated through the pipeline.
  - Best regenerated attempt is always persisted (no keep-original short-circuit when field is populated).

This enforces a single policy across text generation workflows: populated text fields must not block regeneration and overwrite.

## The Problem This Solves

### Before Mandatory Overwrite

```yaml
# Materials.yaml after first generation
materials:
  aluminum-laser-cleaning:
    properties:
      materialCharacteristics:
        description: "Generic placeholder text about material properties"
```

When regenerating with structural patterns:
- ❌ Skip logic checked if field exists
- ❌ Saw "Generic placeholder text" present
- ❌ Skipped generation: "already populated"
- ❌ Result: Old generic text persists, structural patterns never applied

### After Mandatory Overwrite

```yaml
# Materials.yaml after regeneration
materials:
  aluminum-laser-cleaning:
    properties:
      materialCharacteristics:
        description: "Due to its low density (2.7 g/cm³) and zero porosity, aluminum requires..."
```

When regenerating:
- ✅ NO skip logic
- ✅ ALWAYS regenerate
- ✅ Apply structural patterns + distinctive properties
- ✅ Result: Fresh content with variety and specifics

## Architecture

### Code Implementation

**File**: `generation/backfill/universal_text_generator.py`

```python
def populate(self, item_data: dict) -> dict:
    """
    Generate text content using schema-based prompts.
    
    MANDATORY: Always overwrite existing text (structural variation requirement)
    This ensures distinctive properties and structural patterns are applied.
    """
    for mapping in self.field_mappings:
        field = mapping['field']
        component_type = mapping['component_type']
        
        # NO SKIP LOGIC HERE - always regenerate
        
        result = self.generator.generate(
            material_name=material_name,
            component_type=component_type,
            author_id=item_data.get('author', {}).get('id', 1)
        )
        
        if result.success and result.content:
            # Always set the field (handles nested paths)
            self._set_nested_field(item_data, field, result.content)
```

### What Was Removed

**Lines 117-120 (DELETED)**:
```python
# OLD CODE - REMOVED:
if self.mode == 'multi':
    existing_value = _get_nested_field(item_data, field)
    if existing_value:
        logger.info(f"    ⏭️  {field}: already populated, skipping")
        continue  # Skip if field already populated
```

This skip logic prevented:
- Structural pattern application
- Distinctive property integration
- Generic text replacement

## Requirements

### For Backfill Generators

1. **NO skip-if-populated logic** - Delete any checks for existing content
2. **ALWAYS call generator** - Even if field has value
3. **ALWAYS write result** - Overwrite existing content every time
4. **Handle nested paths** - Use `_set_nested_field()` for dot-notation paths

### For Tests

All tests must verify:
- [ ] Generator called for ALL items (not just empty ones)
- [ ] Existing content replaced (not preserved)
- [ ] No skip logic in source code
- [ ] Structural patterns applied on regeneration

## Test Coverage

**File**: `tests/test_mandatory_overwrite.py`

### Test 1: Overwrites Existing Description
```python
def test_overwrites_existing_description(self, tmp_path):
    """Verify that existing materialCharacteristics description is overwritten"""
    # Create YAML with OLD content
    test_data = {
        'materials': {
            'test-material': {
                'properties': {
                    'materialCharacteristics': {
                        'description': 'OLD GENERIC TEXT THAT SHOULD BE REPLACED'
                    }
                }
            }
        }
    }
    
    # Run backfill
    generator.backfill_all()
    
    # Verify content REPLACED (not skipped)
    assert new_description == 'NEW CONTENT WITH STRUCTURAL VARIETY'
    assert new_description != 'OLD GENERIC TEXT'
```

### Test 2: No Skip Logic
```python
def test_no_skip_logic_for_populated_fields(self):
    """Verify there's no skip logic checking for existing content"""
    source = inspect.getsource(UniversalTextGenerator.populate)
    
    # Should NOT contain skip logic
    assert 'already populated' not in source.lower()
    assert 'skip if field' not in source.lower()
```

### Test 3: Always Calls Generator
```python
def test_always_calls_generator(self, tmp_path):
    """Verify generator is ALWAYS called regardless of existing content"""
    # 3 materials: one with content, one empty, one missing field
    generator.backfill_all()
    
    # Verify generator was called 3 times (ALL materials)
    assert mock_generator.generate.call_count == 3
```

### Test 4: Structural Variation Applied
```python
def test_structural_variation_applied_on_regeneration(self, tmp_path):
    """Verify that structural patterns are applied when regenerating"""
    # Material with old description
    test_data['description'] = 'Old aluminum description'
    
    # Regenerate
    generator.backfill_all()
    
    # Verify new content has structural variety
    assert 'Due to' in new_desc or 'low density' in new_desc
    assert new_desc != 'Old aluminum description'
```

## Usage

### Regenerate Single Material

```bash
python3 run.py --backfill \
    --domain materials \
    --generator multi_field_text \
    --item aluminum-laser-cleaning
```

Result:
- ✅ ALWAYS regenerates all configured fields
- ✅ Overwrites existing content
- ✅ Applies structural patterns + distinctive properties
- ✅ Replaces generic text with rich content

### Regenerate All Materials

```bash
python3 run.py --backfill \
    --domain materials \
    --generator multi_field_text
```

Result:
- ✅ Processes ALL 153 materials
- ✅ Regenerates EVERY field for EVERY material
- ✅ Applies variety across full dataset
- ✅ No materials skipped

## Verification

### Check Generated Content

```bash
# View specific field
python3 -c "
import yaml
d = yaml.safe_load(open('data/materials/Materials.yaml'))
print(d['materials']['aluminum-laser-cleaning']['properties']['materialCharacteristics']['description'])
"
```

Expected output:
```
Due to its low density (2.7 g/cm³) and zero porosity, aluminum requires 
precise wavelength calibration to prevent thermal damage during laser cleaning.
```

Should include:
- ✅ Structural variety (not "Material's X, Y, and Z...")
- ✅ Distinctive properties (specific values: 2.7 g/cm³, zero porosity)
- ✅ Rich, detailed content (not generic placeholders)

### Compare Multiple Materials

```bash
# Extract 3 materials for comparison
python3 -c "
import yaml
d = yaml.safe_load(open('data/materials/Materials.yaml'))
for mat in ['aluminum-laser-cleaning', 'steel-laser-cleaning', 'copper-laser-cleaning']:
    desc = d['materials'][mat]['properties']['materialCharacteristics']['description']
    opening = desc.split('.')[0]
    print(f'{mat}: {opening}...')
"
```

Expected result:
- ✅ Each material has DIFFERENT opening structure
- ✅ No repetition of "Material's property X, Y, and Z..."
- ✅ Distinctive properties mentioned (different values per material)

## Anti-Patterns

### ❌ WRONG: Adding Skip Logic

```python
# ❌ DO NOT DO THIS:
def populate(self, item_data: dict) -> dict:
    existing_value = item_data.get('properties', {}).get('materialCharacteristics', {}).get('description')
    if existing_value:
        logger.info("Field already populated, skipping...")
        return item_data  # BAD - prevents overwrite
    
    result = self.generator.generate(...)
```

**Grade**: F violation - Prevents structural variety and distinctive properties

### ❌ WRONG: Conditional Generation

```python
# ❌ DO NOT DO THIS:
def populate(self, item_data: dict) -> dict:
    for field in fields:
        if not item_data.get(field):  # Only generate if empty
            result = self.generator.generate(...)  # BAD - only runs on empty fields
```

**Grade**: F violation - Old content never updated with patterns

### ✅ CORRECT: Always Generate

```python
# ✅ DO THIS:
def populate(self, item_data: dict) -> dict:
    for field in fields:
        # NO skip logic - always generate
        result = self.generator.generate(...)
        
        if result.success and result.content:
            # Always overwrite existing content
            self._set_nested_field(item_data, field, result.content)
```

**Grade**: A - Consistently applies structural variety

## Benefits

### 1. Structural Variety

Without overwrite:
```
Aluminum: "Aluminum's low density, high conductivity, and zero porosity create..."
Steel: "Steel's high density, moderate conductivity, and minimal porosity create..."
Copper: "Copper's moderate density, excellent conductivity, and zero porosity create..."
```
❌ Identical structure → AI-detectable pattern

With mandatory overwrite + structural patterns:
```
Aluminum: "Due to its exceptionally low density (2.7 g/cm³) and zero porosity..."
Steel: "High hardness (1.47 GPa) presents cleaning challenges that require..."
Copper: "Unlike ferrous metals, copper's unique combination of 8.96 g/cm³ density..."
```
✅ Varied structures → human-like diversity

### 2. Distinctive Properties Integration

Without overwrite:
```
"Generic intrinsic properties affecting cleaning outcomes"
```
❌ No specific values, generic description

With mandatory overwrite:
```
"Due to its low density (2.7 g/cm³), excellent thermal conductivity (237 W/m·K), 
and zero porosity, aluminum requires precise wavelength calibration..."
```
✅ Specific quantitative values, distinctive characteristics

### 3. Content Quality Improvement

Without overwrite:
```
First generation: "Generic placeholder text about properties"
Structural patterns added to system
Regeneration attempt: ⏭️ "already populated, skipping"
Result: Generic text PERSISTS
```
❌ System improvements never applied to existing content

With mandatory overwrite:
```
First generation: "Generic placeholder text about properties"
Structural patterns added to system
Regeneration: ✅ "Generated (287 chars, quality: 8.5/10)"
Result: Rich content with patterns APPLIED
```
✅ All content benefits from system improvements

## Integration with Other Systems

### Structural Patterns

**File**: `data/schemas/section_display_schema.yaml`

```yaml
property_pools:
  materialCharacteristics_description:
    structural_patterns:
      - id: comparative_opening
        weight: 20
        instruction: "Start by comparing THIS material to its category average"
      - id: consequence_first
        weight: 20
        instruction: "Begin with the practical outcome, then explain which properties cause it"
      # ... 4 more patterns
```

Mandatory overwrite ensures:
- ✅ Patterns selected randomly each generation
- ✅ Different structure per material (no repetition)
- ✅ Variety applied across full dataset

### Distinctive Properties

**File**: `scripts/backfill/populate_distinctive_properties.py`

```python
# Backfills _distinctive_materialCharacteristics_description with specific values
_distinctive_materialCharacteristics_description:
  - name: density
    value: 2.7
    unit: 'g/cm³'
  - name: thermal_conductivity
    value: 237
    unit: 'W/m·K'
  - name: porosity
    value: 0
    unit: '%'
```

Mandatory overwrite ensures:
- ✅ Properties referenced in generated text
- ✅ Specific values mentioned (not just "low density")
- ✅ Quantitative grounding across all materials

## Enforcement

### Pre-Commit Checks

```bash
# Check for skip logic violations
grep -r "already populated\|skip if field" generation/backfill/*.py
# Should return: NO MATCHES

# Check for skip-if-exists patterns
grep -r "if existing_value\|if.*get.*field" generation/backfill/*.py | grep skip
# Should return: NO MATCHES
```

### Test Suite

```bash
# Run mandatory overwrite tests
python3 -m pytest tests/test_mandatory_overwrite.py -v

# Expected: 4 tests PASS
#   test_overwrites_existing_description: PASS
#   test_no_skip_logic_for_populated_fields: PASS  
#   test_always_calls_generator: PASS
#   test_structural_variation_applied_on_regeneration: PASS
```

### Code Review Checklist

Before merging ANY backfill generator changes:
- [ ] No skip logic added
- [ ] Generator ALWAYS called
- [ ] Result ALWAYS written (if success)
- [ ] Handles nested field paths correctly
- [ ] Tests verify overwrite behavior
- [ ] Documentation updated

## Grade

**Compliance**: Mandatory - violations = Grade F

**Current Status**: ✅ FULLY COMPLIANT (January 13, 2026)
- Skip logic removed (lines 117-120 deleted)
- Documentation updated (base.py, universal_text_generator.py)
- Tests passing (4/4 tests verified)
- Nested field handling implemented

## References

- **Implementation**: `generation/backfill/universal_text_generator.py`
- **Tests**: `tests/test_mandatory_overwrite.py`
- **Structural Patterns**: `data/schemas/section_display_schema.yaml`
- **Distinctive Properties**: `scripts/backfill/populate_distinctive_properties.py`
- **Related Policy**: `.github/copilot-instructions.md` Core Principle 0.6

---

**Last Updated**: January 13, 2026  
**Status**: ✅ IMPLEMENTED AND TESTED  
**Test Coverage**: 4 automated tests verifying compliance
