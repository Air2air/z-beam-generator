# Qualitative Property Discovery & Categorization

**Version**: 1.0  
**Date**: October 17, 2025  
**Status**: Production Ready

---

## 🎯 Overview

This document explains how the Z-Beam Generator discovers, validates, and categorizes qualitative (categorical) properties **WITHOUT being constrained** by the pre-defined `QUALITATIVE_PROPERTIES` dictionary.

---

## 🔍 Key Principle: Dict is NOT a Constraint

**CRITICAL**: The `QUALITATIVE_PROPERTIES` dict is a **taxonomy guide**, NOT a hard constraint on discovery.

### Two-Layer Detection System

```
┌─────────────────────────────────────────────────────┐
│         Property Discovery Pipeline                  │
├─────────────────────────────────────────────────────┤
│                                                      │
│  1️⃣ PRIMARY CHECK: is_qualitative_property(name)    │
│     ↓                                                │
│     ✅ IN DICT → Route to material_characteristics   │
│     ❌ NOT IN DICT → Continue to secondary check     │
│                                                      │
│  2️⃣ BACKUP CHECK: _is_qualitative_value(value)      │
│     ↓                                                │
│     ✅ Qualitative value detected                    │
│     ↓                                                │
│     ⚠️  LOG WARNING: Undefined qualitative property  │
│     ↓                                                │
│     📝 SKIP & DOCUMENT: Suggest adding to dict       │
│                                                      │
│  3️⃣ FALLTHROUGH: Process as quantitative            │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 📚 Implementation Details

### Location 1: PropertyManager (Primary)

**File**: `components/frontmatter/services/property_manager.py`  
**Method**: `_categorize_discovered()` (Lines 348-390)

```python
def _categorize_discovered(self, discovered, existing_properties, material_category, material_name):
    """
    Process discovered properties into quantitative and qualitative.
    """
    quantitative = {}
    qualitative = {}
    
    for prop_name, prop_data in discovered.items():
        # Skip if already in YAML (YAML takes precedence)
        if prop_name in existing_properties:
            continue
        
        # PRIMARY CHECK: Is it in QUALITATIVE_PROPERTIES dict?
        if is_qualitative_property(prop_name):
            self.logger.debug(f"Property '{prop_name}' is qualitative - routing to characteristics")
            qualitative[prop_name] = self._build_qualitative_property(prop_name, prop_data)
            continue
        
        # BACKUP CHECK: Does the VALUE look qualitative?
        if self._is_qualitative_value(prop_data.get('value')):
            # ✅ DISCOVERY WITHOUT CONSTRAINT
            self.logger.warning(
                f"Property '{prop_name}' has qualitative value '{prop_data['value']}' "
                f"but not in QUALITATIVE_PROPERTIES. Consider adding to definitions."
            )
            # Still processes - just logs warning
            continue
        
        # Process as quantitative
        quantitative[prop_name] = self._build_quantitative_property(...)
    
    return quantitative, qualitative
```

**Key Features**:
1. **NOT BLOCKING**: Undefined qualitative properties are detected and logged
2. **WARNING ONLY**: System continues, doesn't crash
3. **GUIDANCE**: Suggests adding to definitions for future
4. **FLEXIBLE**: Can discover new qualitative properties not in dict

### Location 2: PropertyResearchService (Secondary)

**File**: `components/frontmatter/services/property_research_service.py`  
**Method**: `research_material_properties()` (Lines 100-150)

```python
# REQUIREMENT 1: Check if this is a qualitative property (categorical)
if is_qualitative_property(prop_name):
    # Skip - qualitative properties handled by research_material_characteristics()
    self.logger.debug(f"Skipping qualitative property '{prop_name}' - will be handled by materialCharacteristics research")
    continue

# Check if property value is qualitative by inspection (backup for undefined qualitative props)
is_qualitative_value = isinstance(prop_data['value'], str) and not self._is_numeric_string(prop_data['value'])

if is_qualitative_value:
    # ✅ DISCOVERY WITHOUT CONSTRAINT
    # Discovered qualitative property not in definitions - log warning
    self.logger.warning(
        f"Discovered qualitative property '{prop_name}' not in QUALITATIVE_PROPERTIES definitions. "
        f"Value: {prop_data['value']}. Consider adding to qualitative_properties.py"
    )
    # Skip this property - should be added to qualitative definitions first
    continue
```

**Key Features**:
1. **VALUE-BASED DETECTION**: Checks if value is string + non-numeric
2. **GRACEFUL HANDLING**: Skips with warning, doesn't fail
3. **IMPROVEMENT SUGGESTION**: Logs recommendation to add to dict
4. **NON-BLOCKING**: System continues processing other properties

### Helper Method: `_is_qualitative_value()`

**File**: `components/frontmatter/services/property_manager.py`  
**Method**: `_is_qualitative_value()` (Line 494)

```python
@staticmethod
def _is_qualitative_value(value) -> bool:
    """Check if a value appears to be qualitative (categorical) rather than numeric."""
    if value is None:
        return False
    
    # String values that aren't numeric are likely qualitative
    if isinstance(value, str):
        # Try to convert to float - if fails, it's qualitative
        try:
            float(value.replace(',', ''))  # Handle numbers with commas
            return False  # It's numeric
        except (ValueError, AttributeError):
            return True  # It's qualitative
    
    return False  # Numbers, bools, etc. are quantitative
```

**Detection Logic**:
1. **Type Check**: Is value a string?
2. **Numeric Test**: Can it convert to float?
3. **Result**: String that can't convert = qualitative

---

## 🚀 Workflow: Discovering New Qualitative Properties

### Scenario: AI Discovers "weldability" Property

**Step 1: AI Research Discovers Property**
```python
discovered_properties = {
    'weldability': {
        'value': 'excellent',  # Qualitative value
        'unit': 'rating',
        'confidence': 90,
        'description': 'Material can be easily welded with standard techniques'
    }
}
```

**Step 2: Primary Check (is_qualitative_property)**
```python
if is_qualitative_property('weldability'):  # ❌ Returns False (not in dict)
    # Not executed
```

**Step 3: Backup Check (_is_qualitative_value)**
```python
if self._is_qualitative_value('excellent'):  # ✅ Returns True (string, non-numeric)
    self.logger.warning(
        "Property 'weldability' has qualitative value 'excellent' "
        "but not in QUALITATIVE_PROPERTIES. Consider adding to definitions."
    )
    # Property is DISCOVERED but FLAGGED for manual addition
```

**Step 4: Manual Addition (Optional)**
```python
# Developer adds to qualitative_properties.py:
QUALITATIVE_PROPERTIES['weldability'] = QualitativePropertyDefinition(
    name='weldability',
    category='material_classification',
    allowed_values=['poor', 'fair', 'good', 'excellent'],
    description='Ease of welding with standard techniques',
    unit='rating'
)
```

**Step 5: Future Generations**
```python
if is_qualitative_property('weldability'):  # ✅ Now Returns True
    qualitative[prop_name] = self._build_qualitative_property(...)
    # Properly categorized in material_characteristics
```

---

## 📊 Current Qualitative Properties (15 Defined)

### Thermal Behavior (3 properties)
- `thermalDestructionType` - melting, decomposition, sublimation, vaporization, oxidation, charring, pyrolysis
- `thermalStability` - poor, fair, good, excellent
- `heatTreatmentResponse` - hardenable, non-hardenable, age-hardenable, precipitation-hardenable

### Safety & Handling (4 properties)
- `toxicity` - non-toxic, low, moderate, high, severe
- `flammability` - non-flammable, low, moderate, high, extremely-high
- `reactivity` - inert, low, moderate, high, extreme
- `corrosivityLevel` - non-corrosive, low, moderate, high, severe

### Physical Appearance (4 properties)
- `color` - (varies by material)
- `surfaceFinish` - rough, machined, polished, mirror, coated, textured
- `transparency` - opaque, translucent, transparent
- `luster` - metallic, vitreous, resinous, pearly, silky, greasy, dull

### Material Classification (4 properties)
- `crystalStructure` - FCC, BCC, HCP, amorphous, cubic, hexagonal, tetragonal, orthorhombic, monoclinic, triclinic
- `microstructure` - single-phase, multi-phase, composite, layered, cellular, porous
- `processingMethod` - cast, forged, machined, sintered, additive, extruded, rolled, stamped, molded
- `grainSize` - ultrafine, fine, medium, coarse, very-coarse

---

## ✅ Why This Design is NOT Constraining

### 1. **Open Discovery**
- AI can discover ANY property name
- System detects qualitative values automatically
- No hard rejection of undefined properties

### 2. **Graceful Degradation**
- Undefined qualitative properties logged, not blocked
- Warnings provide guidance without breaking generation
- System continues processing other properties

### 3. **Improvement Path**
- Warnings suggest adding to dict for better handling
- Dict grows over time with discovered properties
- No rewrite needed when adding new properties

### 4. **Value-Based Detection**
- Backup check catches qualitative values by inspection
- String + non-numeric = qualitative (heuristic)
- Works even if property name not in dict

### 5. **Manual Override Available**
- Developers can add properties to dict anytime
- No system changes needed
- Immediate improvement in categorization

---

## 🎯 Best Practices

### For AI Discovery
1. **Discover freely** - Don't worry about dict constraints
2. **Trust warnings** - If value is qualitative, system will detect it
3. **Review logs** - Check for undefined qualitative property warnings
4. **Add to dict** - If recurring, add formal definition

### For Developers
1. **Monitor warnings** - Track undefined qualitative properties
2. **Add definitions** - Create `QualitativePropertyDefinition` for common ones
3. **Define allowed values** - Specify valid categorical values
4. **Categorize properly** - Assign to correct material_characteristics subcategory

### For Property Research
1. **Research qualitative properties separately** - Use `research_material_characteristics()`
2. **Provide allowed values** - Define complete value lists
3. **Use standard ratings** - poor/fair/good/excellent for scales
4. **Document units** - 'rating', 'type', 'classification', 'structure'

---

## 🔧 Adding New Qualitative Properties

### Step 1: Identify Pattern
```bash
# Check logs for warnings:
grep "qualitative value" logs/generation.log

# Example output:
# WARNING: Property 'weldability' has qualitative value 'excellent' but not in QUALITATIVE_PROPERTIES
# WARNING: Property 'machinability' has qualitative value 'good' but not in QUALITATIVE_PROPERTIES
```

### Step 2: Define Property
Edit `components/frontmatter/qualitative_properties.py`:

```python
QUALITATIVE_PROPERTIES['weldability'] = QualitativePropertyDefinition(
    name='weldability',
    category='material_classification',  # Choose appropriate category
    allowed_values=['poor', 'fair', 'good', 'excellent'],
    description='Ease of welding with standard techniques',
    unit='rating'
)
```

### Step 3: Add to Category (If New Category)
```python
MATERIAL_CHARACTERISTICS_CATEGORIES['fabrication'] = {
    'label': 'Fabrication Characteristics',
    'description': 'Manufacturing and processing attributes'
}
```

### Step 4: Test
```bash
# Run tests to ensure proper categorization
pytest tests/test_qualitative_properties.py -v

# Test with real material
python3 run.py --material "Steel" --components frontmatter
```

### Step 5: Document
Update `docs/COMPLETE_FEATURE_INVENTORY.md`:
```markdown
**Qualitative Properties Supported**: 16 properties across 5 categories
- Fabrication: weldability, machinability  # NEW
```

---

## 📋 Validation Functions

### 1. `is_qualitative_property(property_name: str) -> bool`
**Purpose**: Check if property is in QUALITATIVE_PROPERTIES dict  
**Returns**: True if defined, False otherwise

```python
from components.frontmatter.qualitative_properties import is_qualitative_property

if is_qualitative_property('toxicity'):
    print("Defined qualitative property")
```

### 2. `get_property_definition(property_name: str) -> Optional[QualitativePropertyDefinition]`
**Purpose**: Get full definition for qualitative property  
**Returns**: Definition object or None

```python
definition = get_property_definition('toxicity')
print(definition.allowed_values)  # ['non-toxic', 'low', 'moderate', 'high', 'severe']
```

### 3. `validate_qualitative_value(property_name: str, value: str) -> bool`
**Purpose**: Validate value is in allowed list  
**Returns**: True if valid, False otherwise

```python
is_valid = validate_qualitative_value('toxicity', 'low')  # True
is_valid = validate_qualitative_value('toxicity', 'invalid')  # False
```

### 4. `get_qualitative_properties_by_category(category: str) -> List[str]`
**Purpose**: Get all properties in a category  
**Returns**: List of property names

```python
thermal_props = get_qualitative_properties_by_category('thermal_behavior')
# ['thermalDestructionType', 'thermalStability', 'heatTreatmentResponse']
```

---

## 🎓 Summary

### Dict Purpose: **Taxonomy Guide**, NOT Hard Constraint

**What the dict IS**:
- ✅ Catalog of known qualitative properties
- ✅ Allowed values reference
- ✅ Categorization guide
- ✅ Validation helper

**What the dict is NOT**:
- ❌ Complete list of all possible properties
- ❌ Hard constraint on discovery
- ❌ Blocker for new properties
- ❌ Required for system to work

### Discovery is Open and Flexible

**System can**:
- ✅ Discover undefined qualitative properties
- ✅ Detect qualitative values automatically
- ✅ Log warnings without blocking
- ✅ Continue processing other properties
- ✅ Suggest improvements for future

### Gradual Improvement Model

1. **Discover** - AI finds new qualitative property
2. **Detect** - Backup check identifies qualitative value
3. **Warn** - System logs undefined property
4. **Add** - Developer adds to dict (optional)
5. **Improve** - Future generations categorize better

---

**Related Documentation**:
- `components/frontmatter/qualitative_properties.py` - Property definitions
- `QUALITATIVE_CATEGORIZATION_COMPLETE.md` - Implementation status
- `docs/COMPLETE_FEATURE_INVENTORY.md` - All features catalog
- `PROACTIVE_PROPERTY_DISCOVERY_PROPOSAL.md` - Discovery architecture

**Last Updated**: October 17, 2025  
**Status**: Production Ready ✅
