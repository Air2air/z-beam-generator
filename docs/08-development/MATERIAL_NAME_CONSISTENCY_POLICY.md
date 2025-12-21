# Material Name Consistency Across Domains Policy

**Date**: December 20, 2025  
**Scope**: All domains (Materials, Settings, Contaminants, Compounds, Associations)  
**Priority**: TIER 1 - System-Breaking (cross-domain lookups fail if violated)

---

## 🎯 Core Principle

**ALL domains MUST use consistent material naming conventions based on their role. Materials.yaml is the single source of truth for material identities.**

**Violation Impact**: Grade F - Broken associations, failed lookups, incorrect frontmatter generation

---

## 📊 Domain-Specific Format Requirements

### MANDATORY Formats by Domain

| Domain | Dictionary Key Format | Example | Rationale |
|--------|----------------------|---------|-----------|
| **Materials.yaml** | `{slug}-laser-cleaning` | `aluminum-laser-cleaning` | Source of truth, URL-friendly with domain suffix |
| **Settings.yaml** | `{slug}` (base only) | `aluminum` | Matches material without domain suffix |
| **Contaminants.yaml** | `Display Name` | `Aluminum` | Human-readable in valid_materials lists |
| **Compounds.yaml** | `{slug}` (base only) | `aluminum` | Lookup compatibility |
| **DomainAssociations.yaml** | `{slug}` (base only) | `aluminum` | Universal lookup keys |

### Format Specifications

#### Materials.yaml Format
```yaml
materials:
  aluminum-laser-cleaning:  # Full slug with suffix
    category: metal
    # ... properties
  stainless-steel-316-laser-cleaning:  # Alloys include designation
    category: metal
    # ... properties
  acrylic-pmma-laser-cleaning:  # Compounds include abbreviation
    category: plastic
    # ... properties
```

**Rules**:
- ✅ Always lowercase
- ✅ Hyphen-separated words
- ✅ Always ends with `-laser-cleaning`
- ✅ Include material designation/grade (316, 304, etc.)
- ✅ Include abbreviations for compounds (PMMA, ABS, PVC)

#### Settings.yaml Format
```yaml
settings:
  aluminum:  # Base slug, no suffix
    machine_settings:
      # ... settings
  stainless-steel-316:  # Alloys include designation
    machine_settings:
      # ... settings
  acrylic-pmma:  # Compounds include abbreviation
    machine_settings:
      # ... settings
```

**Rules**:
- ✅ Always lowercase
- ✅ Hyphen-separated words
- ✅ NO `-laser-cleaning` suffix
- ✅ Match Materials.yaml base slug exactly

#### Contaminants.yaml Format
```yaml
contamination_patterns:
  rust-oxidation-contamination:
    valid_materials:
      - Aluminum  # Display name, title case
      - Steel
      - Stainless Steel 316  # Include designation
      - Bronze
    prohibited_materials:
      - Acrylic (PMMA)  # Abbreviations in parentheses
      - Plastics
```

**Rules**:
- ✅ Title case (capitalize each word)
- ✅ Space-separated words
- ✅ Abbreviations in parentheses: `Acrylic (PMMA)`
- ✅ Designations after name: `Stainless Steel 316`
- ✅ Special value: `ALL` (all uppercase) for universal patterns

#### DomainAssociations.yaml Format
```yaml
associations:
  - source_domain: materials
    source_id: aluminum  # Base slug
    target_domain: contaminants
    target_id: rust-oxidation-contamination
    relationship_type: can_have_contamination
```

**Rules**:
- ✅ Always base slug (no suffix)
- ✅ Materials use base: `aluminum` not `aluminum-laser-cleaning`
- ✅ Contaminants use full: `rust-oxidation-contamination`
- ✅ Lowercase, hyphen-separated

---

## 🔄 Format Conversion Functions

### Implementation Patterns

```python
from shared.utils.core.slug_utils import create_material_slug

class MaterialNameMapper:
    """Convert between domain-specific material name formats."""
    
    @staticmethod
    def full_to_base(full_slug: str) -> str:
        """Materials.yaml → Settings.yaml / Associations"""
        return full_slug.replace('-laser-cleaning', '')
        # aluminum-laser-cleaning → aluminum
    
    @staticmethod
    def full_to_display(full_slug: str) -> str:
        """Materials.yaml → Contaminants.yaml"""
        base = full_slug.replace('-laser-cleaning', '')
        words = base.split('-')
        # Handle acronyms and special cases
        display_words = []
        for word in words:
            if word.upper() in ['ABS', 'PMMA', 'PC', 'PVC', 'PET']:
                display_words.append(f'({word.upper()})')
            elif word.isdigit():
                display_words.append(word)
            else:
                display_words.append(word.capitalize())
        return ' '.join(display_words)
        # aluminum-laser-cleaning → Aluminum
        # stainless-steel-316-laser-cleaning → Stainless Steel 316
        # acrylic-pmma-laser-cleaning → Acrylic (PMMA)
    
    @staticmethod
    def display_to_base(display_name: str) -> str:
        """Contaminants.yaml → Settings.yaml / Associations"""
        # Remove parentheses and their content
        name = re.sub(r'\s*\([^)]+\)', '', display_name)
        # Lowercase and replace spaces with hyphens
        return name.lower().replace(' ', '-')
        # Aluminum → aluminum
        # Stainless Steel 316 → stainless-steel-316
        # Acrylic (PMMA) → acrylic
    
    @staticmethod
    def base_to_display(base_slug: str) -> str:
        """Settings.yaml → Contaminants.yaml"""
        words = base_slug.split('-')
        return ' '.join(word.capitalize() for word in words)
        # aluminum → Aluminum
        # stainless-steel-316 → Stainless Steel 316
```

### Usage Examples

```python
# ✅ CORRECT: Loading from Materials.yaml
materials_data = load_yaml('data/materials/Materials.yaml')
for material_slug, material_data in materials_data['materials'].items():
    # material_slug = 'aluminum-laser-cleaning'
    base_slug = material_slug.replace('-laser-cleaning', '')
    # base_slug = 'aluminum'
    
    # Get matching settings
    setting = settings_data['settings'][base_slug]
    
    # Get display name for contaminants
    display_name = MaterialNameMapper.full_to_display(material_slug)
    # display_name = 'Aluminum'

# ✅ CORRECT: Working with Contaminants.yaml
pattern_data = contaminants_data['contamination_patterns']['rust-oxidation-contamination']
for material_display in pattern_data['valid_materials']:
    # material_display = 'Aluminum'
    base_slug = MaterialNameMapper.display_to_base(material_display)
    # base_slug = 'aluminum'
    
    # Look up in Settings.yaml
    setting = settings_data['settings'][base_slug]
    
    # Look up in Materials.yaml
    full_slug = f"{base_slug}-laser-cleaning"
    material = materials_data['materials'][full_slug]

# ❌ WRONG: Mixing formats
materials_data['materials']['Aluminum'] = {...}  # Display name in Materials
pattern_data['valid_materials'] = ['aluminum-laser-cleaning']  # Slug in Contaminants
settings_data['settings']['aluminum-laser-cleaning'] = {...}  # Full slug in Settings
```

---

## 🛠️ Normalization Tools

### Automated Consistency Check

```bash
# Check all domains for naming consistency
python3 scripts/tools/normalize_all_domains.py --check

# Output:
# ✅ Materials.yaml: 153 materials (SOURCE OF TRUTH)
# ✅ Settings.yaml: 153 entries, all consistent
# ❌ Contaminants.yaml: 12 invalid references found
# ✅ DomainAssociations.yaml: All valid
```

### Automated Fix

```bash
# Dry-run (show changes without applying)
python3 scripts/tools/normalize_all_domains.py --fix --dry-run

# Apply fixes
python3 scripts/tools/normalize_all_domains.py --fix
```

---

## 📋 Validation Requirements

### Pre-Commit Checks

```python
def validate_material_references(domain: str, data: dict) -> List[str]:
    """Validate material name format for domain."""
    errors = []
    
    if domain == 'materials':
        # Check all keys end with -laser-cleaning
        for key in data['materials'].keys():
            if not key.endswith('-laser-cleaning'):
                errors.append(f"Materials.yaml: '{key}' missing -laser-cleaning suffix")
            if key != key.lower():
                errors.append(f"Materials.yaml: '{key}' not lowercase")
            if ' ' in key:
                errors.append(f"Materials.yaml: '{key}' contains spaces")
    
    elif domain == 'settings':
        # Check keys are base slugs (no suffix)
        for key in data['settings'].keys():
            if key.endswith('-laser-cleaning'):
                errors.append(f"Settings.yaml: '{key}' has -laser-cleaning suffix (should be base slug)")
            if key != key.lower():
                errors.append(f"Settings.yaml: '{key}' not lowercase")
            if ' ' in key:
                errors.append(f"Settings.yaml: '{key}' contains spaces")
    
    elif domain == 'contaminants':
        # Check valid_materials uses display names
        patterns = data.get('contamination_patterns', {})
        for pattern_id, pattern_data in patterns.items():
            for material in pattern_data.get('valid_materials', []):
                if material == 'ALL':
                    continue
                if '-' in material and material[0].islower():
                    errors.append(f"Contaminants.yaml [{pattern_id}]: '{material}' looks like slug, should be display name")
    
    return errors
```

### Integration Tests

```python
def test_cross_domain_material_consistency():
    """Verify material names are consistent across domains."""
    # Load all data
    materials = load_yaml('data/materials/Materials.yaml')
    settings = load_yaml('data/settings/Settings.yaml')
    contaminants = load_yaml('data/contaminants/Contaminants.yaml')
    
    # Build reference sets
    material_base_slugs = {
        key.replace('-laser-cleaning', '')
        for key in materials['materials'].keys()
    }
    
    setting_keys = set(settings['settings'].keys())
    
    # Assert Settings.yaml matches Materials.yaml base slugs
    assert material_base_slugs == setting_keys, \
        "Settings.yaml keys must match Materials.yaml base slugs"
    
    # Assert Contaminants.yaml references are valid
    mapper = MaterialNameMapper()
    patterns = contaminants['contamination_patterns']
    for pattern_id, pattern_data in patterns.items():
        for material in pattern_data.get('valid_materials', []):
            if material == 'ALL':
                continue
            base_slug = mapper.display_to_base(material)
            assert base_slug in material_base_slugs, \
                f"Pattern {pattern_id}: Unknown material '{material}'"
```

---

## 🚨 Common Mistakes and Fixes

### Mistake 1: Using Display Name in Materials.yaml

```yaml
# ❌ WRONG
materials:
  Aluminum:  # Display name
    category: metal

# ✅ CORRECT
materials:
  aluminum-laser-cleaning:  # Full slug
    category: metal
```

### Mistake 2: Using Full Slug in Settings.yaml

```yaml
# ❌ WRONG
settings:
  aluminum-laser-cleaning:  # Full slug with suffix
    machine_settings: {...}

# ✅ CORRECT
settings:
  aluminum:  # Base slug
    machine_settings: {...}
```

### Mistake 3: Using Slug in Contaminants.yaml

```yaml
# ❌ WRONG
contamination_patterns:
  rust-oxidation-contamination:
    valid_materials:
      - aluminum-laser-cleaning  # Slug
      - steel

# ✅ CORRECT
contamination_patterns:
  rust-oxidation-contamination:
    valid_materials:
      - Aluminum  # Display name
      - Steel
```

### Mistake 4: Inconsistent Case

```yaml
# ❌ WRONG
valid_materials:
  - aluminum  # Lowercase
  - STEEL  # Uppercase
  - Bronze  # Mixed case

# ✅ CORRECT (Contaminants.yaml)
valid_materials:
  - Aluminum  # Title case
  - Steel  # Title case
  - Bronze  # Title case

# ✅ CORRECT (Settings.yaml)
settings:
  aluminum:  # Lowercase
  steel:  # Lowercase
  bronze:  # Lowercase
```

---

## 📚 Related Documentation

- **Slug Utilities**: `shared/utils/core/slug_utils.py`
- **Normalization Script**: `scripts/tools/normalize_all_domains.py`
- **ADR-006**: `docs/decisions/ADR-006-id-normalization.md`
- **Data Architecture**: `docs/data/DATA_ARCHITECTURE.md`

---

## ✅ Compliance Checklist

Before committing changes that touch material names:

- [ ] Materials.yaml uses `{slug}-laser-cleaning` format
- [ ] Settings.yaml uses `{slug}` (base only) format
- [ ] Contaminants.yaml uses `Display Name` format
- [ ] DomainAssociations.yaml uses `{slug}` (base only) format
- [ ] All slugs are lowercase with hyphens
- [ ] All display names use title case with spaces
- [ ] Special abbreviations in parentheses: `Acrylic (PMMA)`
- [ ] Run `normalize_all_domains.py --check` passes
- [ ] Integration tests pass

---

## 🎓 Learning Examples

### Example 1: Adding New Material

```python
# 1. Add to Materials.yaml (source of truth)
materials_data['materials']['titanium-alloy-ti-6al-4v-laser-cleaning'] = {
    'category': 'metal',
    'properties': {...}
}

# 2. Add to Settings.yaml (base slug)
settings_data['settings']['titanium-alloy-ti-6al-4v'] = {
    'machine_settings': {...}
}

# 3. Reference in Contaminants.yaml (display name)
pattern_data['valid_materials'].append('Titanium Alloy Ti-6Al-4V')

# 4. Use in DomainAssociations.yaml (base slug)
associations.append({
    'source_domain': 'materials',
    'source_id': 'titanium-alloy-ti-6al-4v',  # Base slug
    'target_domain': 'contaminants',
    'target_id': 'metal-oxidation-contamination'
})
```

### Example 2: Querying Cross-Domain

```python
from shared.utils.core.slug_utils import create_material_slug

# User provides display name
user_input = "Stainless Steel 316"

# Convert to base slug for lookups
base_slug = user_input.lower().replace(' ', '-')  # stainless-steel-316

# Look up settings
setting = settings_data['settings'][base_slug]

# Look up in Materials.yaml
full_slug = f"{base_slug}-laser-cleaning"
material = materials_data['materials'][full_slug]

# Display back to user
display_name = ' '.join(word.capitalize() for word in base_slug.split('-'))
print(f"Settings for {display_name}: {setting}")
```

---

**Grade**: TIER 1 - System-breaking if violated. Cross-domain lookups will fail.
