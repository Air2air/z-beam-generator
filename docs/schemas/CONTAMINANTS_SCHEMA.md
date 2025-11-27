# Contaminants.yaml Schema Documentation

**Purpose**: Define valid contamination patterns and their material compatibility  
**Location**: `data/contaminants/Contaminants.yaml`  
**Last Updated**: November 27, 2025

---

## 📋 Schema Structure

```yaml
contamination_patterns:
  [pattern_id]:                      # Unique identifier (kebab-case)
    # === REQUIRED FIELDS ===
    name: string                     # Display name
    description: string              # What this contamination is
    valid_materials: [list]          # Materials this can contaminate
    laser_properties: {...}          # Laser interaction data
    
    # === OPTIONAL FIELDS (varies by pattern) ===
    id: string                       # Alternative identifier (10 patterns)
    category: string                 # Contamination category (10 patterns)
    scientific_name: string          # Scientific terminology (4 patterns)
    chemical_formula: string         # Chemical composition (3 patterns)
    composition: string              # Material composition (90 patterns)
    
    # === VISUAL APPEARANCE (10 patterns) ===
    visual_appearance:
      color_range: [list]            # Color variations
      texture: string                # Surface texture description
      thickness: string              # Layer thickness description
    
    # === AI-GENERATED CONTENT (10 patterns) ===
    caption: string                  # Short description
    faq: string                      # Frequently asked questions
    title: string                    # Display title
    author: string                   # Content author
    eeat: object                     # E-E-A-T metrics
    realism_notes: string            # Realism assessment
    
    # === MATERIAL RESTRICTIONS ===
    prohibited_materials: [list]     # Materials incompatible (90 patterns)
    invalid_materials: [list]        # Alternative restriction format (4 patterns)
    
    # === CONTEXT & RULES ===
    formation_conditions: string     # How contamination forms (8 patterns)
    required_elements: object        # Required conditions (4 patterns)
    valid_material_categories: [list] # Valid categories (3 patterns)
    valid_contexts: [list]           # Valid usage contexts (1 pattern)
    invalid_without_context: [list]  # Context requirements (1 pattern)
    context_required: bool           # Needs context flag (1 pattern)
    context_notes: string            # Context explanations (3 patterns)
    conditional_rules: string        # Special conditions (1 pattern)
    material_specific_notes: string  # Material notes (1 pattern)
    
    # === METADATA ===
    research_timestamp: string       # Research date (1 pattern)
    research_version: string         # Research version (1 pattern)
```

---

## 🎯 Field Locations Quick Reference

### **WHERE IS visual_appearance?**

```yaml
# ❌ NOT HERE (Materials.yaml)
materials:
  Aluminum:
    name: "Aluminum"
    # visual_appearance does NOT exist at this level

# ✅ HERE (Contaminants.yaml - nested)
contamination_patterns:
  copper-patina:
    visual_appearance:        # ← Nested under contamination pattern
      color_range: [...]
      texture: "..."
      thickness: "..."
```

**Key Points**:
- `visual_appearance` is a NESTED field in Contaminants.yaml
- It describes how a contamination LOOKS on a surface
- Only 10/100 patterns have this field (mostly organic/chemical contaminants)
- Does NOT exist in Materials.yaml

---

## 📊 Field Coverage Statistics

| Field Category | Coverage | Notes |
|---------------|----------|-------|
| **Core Fields** | 100% | name, description, valid_materials, laser_properties |
| **Composition** | 90% | Most patterns have material composition data |
| **Visual Appearance** | 10% | Only detailed organic/chemical contaminants |
| **AI Content** | 10% | caption, faq, title (10 enriched patterns) |
| **Context Rules** | 1-10% | Various conditional/contextual fields |

---

## 🔄 Recent Changes

### November 27, 2025
- **Field Renamed**: `visual_characteristics` → `visual_appearance`
- **Reason**: Align with research infrastructure naming (`VisualAppearanceResearcher`)
- **Affected**: 10 contamination patterns
- **Impact**: Zero breaking changes (internal field only)

---

## 💡 Usage Examples

### Example 1: Simple Contamination Pattern
```yaml
rust-oxidation:
  name: "Rust and Oxidation"
  description: "Iron oxide formation on ferrous metals"
  composition: "Iron oxides (Fe2O3, Fe3O4)"
  valid_materials:
    - Steel
    - Iron
    - Cast Iron
  prohibited_materials:
    - Aluminum
    - Copper
  laser_properties:
    absorption_characteristics: "..."
    removal_difficulty: "moderate"
```

### Example 2: Pattern with Visual Appearance
```yaml
copper-patina:
  id: "copper-patina"
  name: "Copper Patina"
  category: "oxidation"
  description: "Green copper carbonate layer"
  scientific_name: "Copper(II) carbonate"
  
  visual_appearance:
    color_range: ["green", "blue-green", "turquoise", "teal"]
    texture: "smooth to powdery, matte finish"
    thickness: "thin to medium surface layer"
  
  valid_materials:
    - Copper
    - Bronze
    - Brass
```

---

## 🚨 Common Pitfalls

### ❌ Wrong: Looking for visual_appearance at wrong level
```python
# This will NOT find visual_appearance
for material in materials_data['materials']:
    visual = material.get('visual_appearance')  # ❌ Doesn't exist here
```

### ✅ Correct: Access nested structure
```python
# This WILL find visual_appearance
for pattern_id, pattern_data in contaminants['contamination_patterns'].items():
    if 'visual_appearance' in pattern_data:
        visual = pattern_data['visual_appearance']  # ✅ Correct location
```

---

## 📚 Related Documentation

- **Field Locations**: `docs/schemas/DATA_FIELD_LOCATIONS.md`
- **Hybrid Architecture**: `HYBRID_CONTAMINATION_ARCHITECTURE.md`
- **Research Infrastructure**: `domains/contaminants/research/visual_appearance_researcher.py`
- **Data Architecture**: `docs/DATA_ARCHITECTURE.md`

---

## 🔧 For Developers

**Before adding new fields**:
1. Check this schema for field precedent
2. Decide: Top-level or nested under contamination_patterns?
3. Update this documentation
4. Add to completeness checker if required field

**Field Naming Conventions**:
- Use snake_case
- Be descriptive (avoid abbreviations)
- Match research infrastructure naming
- Maintain consistency with existing patterns
