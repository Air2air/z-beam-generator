# Generation vs Display Terminology Guide

**Date**: January 7, 2026  
**Status**: ✅ ACTIVE REFERENCE

## Purpose

Clarify the distinction between generation-layer and display-layer terminology to prevent confusion.

---

## Core Concepts

### 1. Generation Layer: `component_type`

**What**: Identifies which content component is being generated  
**Used by**: Generation system, prompt templates, CLI  
**Location**: Python code, generation config files

**Values**:
- `pageDescription` - Main page description
- `pageTitle` - SEO page title  
- `micro` - Image micros (before/after)
- `faq` - Frequently asked questions
- And other generated content types

**Example Usage**:
```python
# Python code
result = generator.generate(
    material_name="Aluminum",
    component_type="pageDescription",  # ← Generation identifier
    author_id=2
)

# CLI
python3 run.py --field pageDescription --material "Aluminum"
```

**Files Using component_type**:
- `generation/core/evaluated_generator.py`
- `generation/field_router.py`
- `generation/config/dynamic_config.py`
- `prompts/{domain}/*.txt` (template files named by component_type)

---

### 2. Display Layer: `presentation`

**What**: Determines how relationship data is displayed in the UI  
**Used by**: Frontmatter export, website rendering  
**Location**: Data YAML files (at relationship level)

**Values**:
- `card` - Card-based layout (visual cards)
- `list` - Simple list format
- `table` - Tabular data display
- `descriptive` - Prose description format
- `collapsible` - Expandable/collapsible sections

**Example Usage**:
```yaml
# Materials.yaml
relationships:
  safety:
    regulatory_standards:
      presentation: card  # ← Display format
      items:
        - name: FDA
          description: "..."
```

**Files Using presentation**:
- `data/materials/Materials.yaml`
- `data/compounds/Compounds.yaml`
- `data/settings/Settings.yaml`
- `data/contaminants/Contaminants.yaml`
- Frontmatter exports (read from source data)

---

## ✅ Correct Usage

### Generation Context
```python
# ✅ CORRECT - Use component_type for generation
def generate_content(self, material: str, component_type: str):
    """Generate content for a specific component type."""
    template = self._load_prompt_template(component_type)
    result = self.api_client.generate(template)
    return result
```

### Display Context
```yaml
# ✅ CORRECT - Use presentation for UI display
relationships:
  technical:
    related_compounds:
      presentation: card  # How to display
      items: [...]
```

---

## ❌ Deprecated Usage

### presentation_type (REMOVED January 7, 2026)
```yaml
# ❌ WRONG - presentation_type was redundant
sectionMetadata:
  notes: "Internal notes"
  presentation_type: card  # ← REMOVED (redundant with presentation)

# ✅ CORRECT - Use presentation at relationship level
some_relationship:
  presentation: card  # ← Authoritative
  items: [...]
  _section:
    sectionMetadata:
      notes: "Internal notes"
      # No presentation_type here
```

**Why Removed**: `presentation_type` in sectionMetadata duplicated the `presentation` field at the relationship level, creating redundancy and confusion.

---

## Quick Reference Table

| Term | Layer | Purpose | Example Values | Location |
|------|-------|---------|----------------|----------|
| **component_type** | Generation | What's being generated | pageDescription, micro, faq | Python code, CLI flags |
| **presentation** | Display | How to display data | card, list, table, collapsible | YAML data files |
| **~~presentation_type~~** | ~~Deprecated~~ | ~~Redundant duplicate~~ | ~~N/A~~ | ~~Removed Jan 7, 2026~~ |

---

## Common Patterns

### Pattern 1: Generating Content
```python
# When generating content, use component_type
for component_type in ['pageDescription', 'micro', 'faq']:
    result = generator.generate(material, component_type)
    save_to_yaml(material, component_type, result.content)
```

### Pattern 2: Exporting to Frontmatter
```python
# When exporting, read presentation from data
relationship = data['relationships']['safety']['regulatory_standards']
presentation_format = relationship['presentation']  # Read from data
# Use presentation_format for UI rendering logic
```

### Pattern 3: Dynamic Configuration
```python
# Generation parameters based on component_type
temperature = dynamic_config.calculate_temperature(component_type)
max_tokens = dynamic_config.calculate_max_tokens(component_type)
```

---

## Migration Notes

### If You See presentation_type
1. **In sectionMetadata**: Remove it (redundant)
2. **In relationship definitions**: Change to `presentation`
3. **In code**: Should not exist in production code

### Example Migration
```yaml
# BEFORE (incorrect)
regulatory_standards:
  presentation: card
  items: [...]
  _section:
    sectionMetadata:
      presentation_type: card  # ← Redundant!

# AFTER (correct)
regulatory_standards:
  presentation: card  # ← Single source of truth
  items: [...]
  _section:
    sectionMetadata:
      notes: "Compliance requirements"
      # No presentation_type
```

---

## Related Documentation

- **Overlap Resolution**: [COMPONENT_VS_PRESENTATION_TYPE_RESOLUTION_JAN7_2026.md](../../COMPONENT_VS_PRESENTATION_TYPE_RESOLUTION_JAN7_2026.md)
- **Component Discovery**: [COMPONENT_DISCOVERY.md](../02-architecture/COMPONENT_DISCOVERY.md)
- **Export Configuration**: [export/config/schema.yaml](../../export/config/schema.yaml)

---

## FAQ

**Q: When should I use component_type?**  
A: When working with the generation system - identifying what content is being generated.

**Q: When should I use presentation?**  
A: When defining how relationship data should be displayed in the UI.

**Q: What happened to presentation_type?**  
A: Removed January 7, 2026 - it was redundant with the presentation field.

**Q: Can I use presentation in generation code?**  
A: No - generation code uses component_type. The presentation field is for UI display only.

**Q: Where is the single source of truth for UI display format?**  
A: The `presentation` field at the relationship level in source YAML files.

---

**Last Updated**: January 7, 2026  
**Maintained By**: Architecture Team
