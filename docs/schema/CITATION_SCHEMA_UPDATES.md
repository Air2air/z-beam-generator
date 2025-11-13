# Citation Schema Updates

**Status**: Implementation Ready  
**Date**: November 12, 2025  
**Purpose**: Enable comprehensive citation architecture across Materials.yaml and Categories.yaml

---

## 🎯 Overview

This document defines schema updates required to support the citation architecture from OPTIMAL_FRONTMATTER_ARCHITECTURE.md, following the zero-fallback policy.

---

## 📋 Materials.yaml Schema Updates

### Current Structure (materialCharacteristics)
```yaml
materialCharacteristics:
  density:
    value: 2.7
    unit: g/cm³
    source: ai_research  # ❌ VAGUE - needs replacement
```

### NEW Structure (with Citations)
```yaml
materialCharacteristics:
  density:
    # Primary value (REQUIRED - no null allowed without needs_research flag)
    value: 2.7
    unit: g/cm³
    
    # Citation fields (REQUIRED for all non-null values)
    source: scientific_literature  # Changed from 'ai_research'
    source_type: reference_handbook  # journal_article | industry_standard | government_database | ai_research | textbook
    source_name: "CRC Handbook of Chemistry and Physics"
    citation: "ISBN 978-1-138-56163-2 (104th Edition, 2023), Section 4: Properties of the Elements and Inorganic Compounds"
    
    # Context (REQUIRED)
    context: "Pure aluminum (99.999% purity), at 25°C (298 K), measured via pycnometry method"
    confidence: 98  # 0-100 scale
    
    # Research metadata
    researched_date: "2025-11-07T12:51:40.387793"
    needs_validation: false  # true if AI-generated, false if from authoritative source
    
    # NULL HANDLING: If value is null
    value: null
    unit: g/cm³
    needs_research: true  # ✅ REQUIRED flag for null values
    research_priority: high  # high | medium | low
    last_research_attempt: "2025-11-07T12:51:40.387793"
```

### Field Definitions

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `value` | float/string | Yes* | Property value | `2.7` |
| `unit` | string | Yes | Unit of measurement | `g/cm³` |
| `source` | string | Yes | Source category | `scientific_literature` |
| `source_type` | string | Yes | Specific source type | `reference_handbook` |
| `source_name` | string | Yes | Full source name | `CRC Handbook of Chemistry` |
| `citation` | string | Yes | Complete citation | `ISBN 978-1-138-56163-2` |
| `context` | string | Yes | Measurement context | `Pure aluminum at 25°C` |
| `confidence` | int | Yes | 0-100 confidence score | `98` |
| `researched_date` | ISO8601 | Yes | When researched | `2025-11-07T12:51:40Z` |
| `needs_validation` | bool | Yes | Requires manual review | `false` |
| `needs_research` | bool | Conditional** | True if value is null | `true` |
| `research_priority` | string | Conditional** | Priority level | `high` |

\* **Value can be null ONLY if `needs_research: true` is set**  
\*\* **Required if value is null**

---

## 📋 Categories.yaml Schema Updates

### Current Structure (category_ranges)
```yaml
category_ranges:
  density:
    min: 2.3
    max: 16.0
    unit: g/cm³
    adjustment_note: "Tungsten carbide is 15.63 g/cm³"
```

### NEW Structure (with Citations and Material-Specific Fields)
```yaml
category_ranges:
  density:
    # Range values (REQUIRED)
    min: 2.3
    max: 16.0
    unit: g/cm³
    
    # Citation fields (REQUIRED for all ranges)
    source: materials_database
    source_type: reference_database
    source_name: "MatWeb Materials Database"
    citation: "MatWeb LLC. 'Ceramic Materials Properties.' Accessed via http://www.matweb.com (2023)"
    
    # Research methodology
    range_determination_method: "statistical_analysis"  # statistical_analysis | literature_review | expert_consensus
    sample_size: 15  # Number of materials analyzed for this range
    confidence: 85  # 0-100 scale
    
    # Metadata
    last_updated: "2025-10-15T14:19:43.867144"
    researched_by: "PropertyRangeResearcher"
    needs_validation: false
    
    # Adjustment tracking (if range was refined)
    adjustment_note: "Tungsten carbide is 15.63 g/cm³"
    adjustment_date: "2025-10-15"
    adjustment_source: "materials_science_research"
    
    # Material-specific citations (NEW SECTION)
    material_citations:
      "Alumina":
        value: 3.95
        unit: g/cm³
        source_name: "ASM Handbook - Ceramics"
        citation: "ASM International, Volume 4A: Steel Heat Treating Fundamentals (2013)"
        confidence: 95
      "Tungsten Carbide":
        value: 15.63
        unit: g/cm³
        source_name: "MatWeb - Tungsten Carbide"
        citation: "MatWeb LLC. 'Tungsten Carbide WC.' http://www.matweb.com"
        confidence: 98
      "Zirconia":
        value: 6.05
        unit: g/cm³
        source_name: "CRC Handbook"
        citation: "CRC Handbook of Chemistry and Physics (104th Ed., 2023)"
        confidence: 97
    
    # NULL HANDLING: If range is incomplete
    min: null
    max: null
    unit: TBD
    needs_research: true  # ✅ REQUIRED flag for null ranges
    research_priority: high
```

### Field Definitions

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `min` | float | Yes* | Minimum value | `2.3` |
| `max` | float | Yes* | Maximum value | `16.0` |
| `unit` | string | Yes | Unit of measurement | `g/cm³` |
| `source` | string | Yes | Source category | `materials_database` |
| `source_type` | string | Yes | Specific source type | `reference_database` |
| `source_name` | string | Yes | Full source name | `MatWeb Materials Database` |
| `citation` | string | Yes | Complete citation | `MatWeb LLC. 'Ceramic...'` |
| `range_determination_method` | string | Yes | How range was determined | `statistical_analysis` |
| `sample_size` | int | Recommended | Materials analyzed | `15` |
| `confidence` | int | Yes | 0-100 confidence score | `85` |
| `last_updated` | ISO8601 | Yes | When updated | `2025-10-15T14:19:43Z` |
| `material_citations` | dict | Optional | Material-specific values | See above |
| `needs_research` | bool | Conditional** | True if range is null | `true` |

\* **min/max can be null ONLY if `needs_research: true` is set**  
\*\* **Required if min/max is null**

---

## 🚫 Forbidden Patterns (Zero Tolerance)

### ❌ NEVER Allow These

```yaml
# BAD: Vague source attribution
source: "literature"
source: "estimated"
source: "typical"
source: "ai_research"  # Without full citation details

# BAD: Missing citation fields
value: 2.7
unit: g/cm³
source: "CRC Handbook"  # ❌ No citation, context, confidence

# BAD: Null values without needs_research flag
value: null
unit: TBD
# ❌ Missing needs_research: true

# BAD: Category fallback in Materials.yaml
# Materials.yaml should NEVER reference category ranges as fallback
```

### ✅ CORRECT Patterns

```yaml
# GOOD: Complete citation for researched value
value: 2.7
unit: g/cm³
source: scientific_literature
source_type: reference_handbook
source_name: "CRC Handbook of Chemistry and Physics"
citation: "ISBN 978-1-138-56163-2 (104th Edition, 2023)"
context: "Pure aluminum at 25°C via pycnometry"
confidence: 98
researched_date: "2025-11-07T12:51:40Z"
needs_validation: false

# GOOD: Explicit needs_research for missing data
value: null
unit: TBD
needs_research: true
research_priority: high
last_research_attempt: "2025-11-07T12:51:40Z"
```

---

## 📊 Source Type Taxonomy

### Valid source_type Values

| source_type | Description | Example |
|-------------|-------------|---------|
| `journal_article` | Peer-reviewed journal | Journal of Laser Applications |
| `reference_handbook` | Technical handbook | CRC Handbook, ASM Handbook |
| `industry_standard` | Standards organization | ASTM, ISO, ANSI |
| `government_database` | Government data | USGS, NIST |
| `materials_database` | Commercial database | MatWeb, Granta Design |
| `ai_research` | AI-generated research | DeepSeek AI research |
| `textbook` | Academic textbook | Materials Science textbook |
| `manufacturer_spec` | Manufacturer datasheet | Manufacturer technical data |

---

## 🔧 Schema Validation Rules

### Materials.yaml Validation

```python
def validate_material_property(property_data: dict) -> Tuple[bool, List[str]]:
    """
    Validate material property follows citation schema.
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    # Check for null value
    if property_data.get('value') is None:
        if not property_data.get('needs_research'):
            errors.append("Null value MUST have needs_research: true")
        if not property_data.get('research_priority'):
            errors.append("Null value MUST have research_priority")
        return len(errors) == 0, errors
    
    # Non-null value MUST have complete citations
    required_fields = [
        'value', 'unit', 'source', 'source_type', 'source_name',
        'citation', 'context', 'confidence', 'researched_date'
    ]
    
    for field in required_fields:
        if field not in property_data:
            errors.append(f"Missing required field: {field}")
    
    # Check forbidden patterns
    forbidden_sources = ['literature', 'estimated', 'typical']
    if property_data.get('source') in forbidden_sources:
        errors.append(f"Forbidden vague source: {property_data.get('source')}")
    
    # Validate confidence range
    confidence = property_data.get('confidence', 0)
    if not 0 <= confidence <= 100:
        errors.append(f"Confidence must be 0-100, got {confidence}")
    
    return len(errors) == 0, errors
```

### Categories.yaml Validation

```python
def validate_category_range(range_data: dict) -> Tuple[bool, List[str]]:
    """
    Validate category range follows citation schema.
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    # Check for null range
    if range_data.get('min') is None or range_data.get('max') is None:
        if not range_data.get('needs_research'):
            errors.append("Null range MUST have needs_research: true")
        return len(errors) == 0, errors
    
    # Non-null range MUST have citations
    required_fields = [
        'min', 'max', 'unit', 'source', 'source_type', 'source_name',
        'citation', 'range_determination_method', 'confidence', 'last_updated'
    ]
    
    for field in required_fields:
        if field not in range_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate range logic
    if range_data.get('min', 0) > range_data.get('max', 0):
        errors.append(f"Invalid range: min ({range_data.get('min')}) > max ({range_data.get('max')})")
    
    return len(errors) == 0, errors
```

---

## 🔄 Migration Strategy

### Phase 1: Update Schema Definitions (This Document)
✅ Define citation fields for Materials.yaml  
✅ Define citation fields for Categories.yaml  
✅ Define validation rules  
✅ Define forbidden patterns  

### Phase 2: Update Python Schema Classes
Update `materials/schema.py`:
```python
@dataclass
class MaterialPropertyValue:
    """Schema for material property with citations"""
    value: Optional[float]
    unit: str
    source: str
    source_type: str
    source_name: str
    citation: str
    context: str
    confidence: int
    researched_date: str
    needs_validation: bool
    needs_research: bool = False  # True if value is null
    research_priority: Optional[str] = None
```

### Phase 3: Update Validators
- Update `CitationValidator` to use new schema
- Add schema validation to `MaterialsDataLoader`
- Add validation to frontmatter export

### Phase 4: Migrate Existing Data
- Run `integrate_research_citations.py` to extract citations from PropertyResearch.yaml
- Update all `source: ai_research` entries with full citations
- Add `needs_research: true` to all null values

### Phase 5: Enforce in Generation Pipeline
- Update PropertyManager to save with new schema
- Update CategoryRangeResearcher to use new schema
- Update frontmatter generators to read new schema

---

## 📝 Example: Complete Material Entry

```yaml
materials:
  Aluminum:
    name: Aluminum
    category: metal
    subcategory: non-ferrous
    
    materialCharacteristics:
      density:
        value: 2.7
        unit: g/cm³
        source: scientific_literature
        source_type: reference_handbook
        source_name: "CRC Handbook of Chemistry and Physics"
        citation: "ISBN 978-1-138-56163-2 (104th Edition, 2023), Section 4"
        context: "Pure aluminum (99.999% purity), 25°C, pycnometry method"
        confidence: 98
        researched_date: "2025-11-07T12:51:40Z"
        needs_validation: false
      
      thermal_conductivity:
        value: 237
        unit: W/(m·K)
        source: scientific_literature
        source_type: reference_handbook
        source_name: "ASM Handbook - Properties and Selection"
        citation: "ASM International, Volume 2 (10th Ed., 1990), ISBN 978-0-87170-376-2"
        context: "Commercially pure aluminum at 25°C, steady-state method"
        confidence: 95
        researched_date: "2025-11-07T12:53:15Z"
        needs_validation: false
      
      laser_absorption:
        value: null
        unit: dimensionless
        needs_research: true
        research_priority: high
        last_research_attempt: "2025-11-07T12:57:00Z"
        notes: "Wavelength-dependent, requires spectroscopy data"
```

---

## 📝 Example: Complete Category Entry

```yaml
categories:
  ceramic:
    name: Ceramic Materials
    
    category_ranges:
      density:
        min: 2.3
        max: 16.0
        unit: g/cm³
        source: materials_database
        source_type: reference_database
        source_name: "MatWeb Materials Database"
        citation: "MatWeb LLC. 'Ceramic Materials Properties.' http://www.matweb.com (2023)"
        range_determination_method: statistical_analysis
        sample_size: 15
        confidence: 85
        last_updated: "2025-10-15T14:19:43Z"
        researched_by: "PropertyRangeResearcher"
        needs_validation: false
        
        material_citations:
          Alumina:
            value: 3.95
            unit: g/cm³
            source_name: "ASM Handbook - Ceramics"
            citation: "ASM International, Volume 4A (2013)"
            confidence: 95
          "Tungsten Carbide":
            value: 15.63
            unit: g/cm³
            source_name: "MatWeb - Tungsten Carbide"
            citation: "MatWeb LLC. http://www.matweb.com"
            confidence: 98
```

---

## 🎯 Success Criteria

After implementation, the system should have:

✅ **100% citation coverage** for all non-null property values  
✅ **Zero vague sources** ("literature", "estimated", "typical")  
✅ **Explicit needs_research flags** for all null values  
✅ **Material-specific citations** in Categories.yaml ranges  
✅ **Complete validation** catching all forbidden patterns  
✅ **Automated testing** verifying zero-fallback policy  

---

## 📊 Implementation Checklist

- [ ] Update `materials/schema.py` with new dataclasses
- [ ] Update `CitationValidator` validation logic
- [ ] Update `PropertyManager` to save with new schema
- [ ] Update `CategoryRangeResearcher` to use new schema
- [ ] Run `integrate_research_citations.py` to migrate data
- [ ] Add `needs_research: true` to all null values in Materials.yaml
- [ ] Add material_citations to Categories.yaml ranges
- [ ] Update frontmatter generators to read new schema
- [ ] Add schema validation tests
- [ ] Update documentation

---

**Last Updated**: November 12, 2025  
**Schema Version**: 4.0.0  
**Status**: Ready for Implementation
