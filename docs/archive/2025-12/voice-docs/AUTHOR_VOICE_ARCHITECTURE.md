# Author & Voice Architecture Documentation
**Date**: December 15, 2025  
**Status**: Production Architecture  
**Version**: 1.0.0

---

## Overview

The Z-Beam system maintains a **normalized author architecture** with clear separation between author identity data, voice characteristics, and persona behavior.

**Key Principle**: **Single Source of Truth** - Author data stored once in `Authors.yaml`, referenced everywhere by ID.

---

## Architecture Components

### 1. Author Data (Identity & Credentials)

**Location**: `data/authors/Authors.yaml`  
**Purpose**: Single source of truth for author identity, credentials, contact info  
**Access**: via `shared/data/author_loader.py`

**Structure**:
```yaml
authors:
  1:
    id: 1
    name: "Yi-Chun Lin"
    country: "Taiwan"
    country_display: "Taiwan"
    title: "Ph.D."
    sex: "f"
    jobTitle: "Laser Processing Engineer"
    expertise:
      - "Laser Materials Processing"
    affiliation:
      name: "National Taiwan University"
      type: "EducationalOrganization"
    credentials:
      - "Ph.D. Materials Engineering, National Taiwan University, 2018"
      - "Post-Ph.D. fellowship at TSMC's laser fab lab, 2018-2020"
      - "3+ years in laser processing R&D"
      - "Assisted in projects on ultrafast laser applications"
    email: "info@z-beam.com"
    image: "/images/author/yi-chun-lin.jpg"
    imageAlt: "Yi-Chun Lin, Ph.D., ..."
    url: "https://z-beam.com/authors/yi-chun-lin"
    sameAs:
      - "https://scholar.google.com/citations?user=ghi789"
      - "https://linkedin.com/in/yi-chun-lin-engineer"
    persona_file: "taiwan_persona.yaml"  # Reference to voice profile
    formatting_file: "taiwan_formatting.yaml"
```

**Total Authors**: 4 (Yi-Chun Lin, Alessandro Moretti, Ikmanda Roswati, Todd Dunning)

---

### 2. Voice Profiles (Linguistic Patterns & Style)

**Location**: `shared/voice/profiles/`  
**Purpose**: Define linguistic patterns, voice instructions, writing style  
**Format**: YAML files (one per author)

**Structure** (Example: `taiwan_persona.yaml`):
```yaml
persona:
  name: "Yi-Chun Lin"
  nationality: "Taiwan"
  native_language: "Mandarin (Taiwan)"
  efl_background: true
  
voice_characteristics:
  sentence_structure:
    - "Topic-comment patterns"
    - "Article omission (when clear from context)"
    - "Temporal markers (after, before, following)"
  
  word_choice:
    - "Technical precision"
    - "Formal vocabulary"
    - "Fewer phrasal verbs than native English"
  
  common_patterns:
    - "This property, it demonstrates..."
    - "Following adjustment, surface reveals..."
    - "Process yields result"  # (Article omitted)

generation_constraints:
  avoid:
    - "Overly casual language"
    - "Idiomatic expressions"
  prefer:
    - "Clear technical terminology"
    - "Precise descriptions"
```

**Referenced by**: `Authors.yaml` → `persona_file` field

---

### 3. Data Flow & References

```
┌─────────────────────────────────────────────┐
│ AUTHORS.YAML (Single Source of Truth)      │
│ - Identity, credentials, contact           │
│ - Reference to voice profile (persona_file)│
└──────────────┬──────────────────────────────┘
               │
               ├─→ Materials.yaml: {author: {id: 1}}
               ├─→ Contaminants.yaml: {author: {id: 1}}
               └─→ Settings.yaml: {author: {id: 1}}
                   
                   (Normalized reference - just ID)
                   
┌─────────────────────────────────────────────┐
│ VOICE PROFILES (shared/voice/profiles/)    │
│ - Linguistic patterns                       │
│ - Voice instructions                        │
│ - Style guidelines                          │
└──────────────┬──────────────────────────────┘
               │
               └─→ Generator loads voice per author_id
                   
┌─────────────────────────────────────────────┐
│ FRONTMATTER (Deployment Format)             │
│ - Full author object (hydrated from        │
│   Authors.yaml during export)               │
│ - Includes all 18 fields                    │
│ - Used for website display                  │
└─────────────────────────────────────────────┘
```

---

## Loading Pattern

### In Generation Code

```python
# Load material with normalized author reference
material_data = load_material("Aluminum")
# → material_data['author'] = {'id': 4}

# Hydrate author for generation
from shared.data.author_loader import get_author
author_full = get_author(material_data['author']['id'])
# → author_full = {full 18-field author object}

# Load voice profile
persona_file = author_full['persona_file']  # 'us_persona.yaml'
voice_profile = load_voice_profile(persona_file)
```

### In Exporter

```python
# Materials.yaml has: author: {id: 4}

# Export process:
from shared.data.author_loader import get_author

author_id = material_data['author']['id']
author_full = get_author(author_id)  # Hydrate from Authors.yaml

frontmatter['author'] = author_full.copy()  # Full object in frontmatter
# → Frontmatter now has all 18 author fields for website use
```

---

## Data Savings

**Before Normalization** (Hypothetical full duplication):
- 251 items × 932 bytes/author = **228 KB** of duplicate data

**After Normalization**:
- Authors.yaml: ~4 KB (4 authors × 1 KB each)
- References: 251 items × 8 bytes = ~2 KB
- **Total: ~6 KB**

**Savings**: **222 KB** (97% reduction)

---

## Maintenance Guide

### Adding a New Author

1. **Add to Authors.yaml**:
```yaml
authors:
  5:
    id: 5
    name: "New Author"
    country: "Germany"
    # ... (all 18 fields)
    persona_file: "germany_persona.yaml"
```

2. **Create voice profile**:
```bash
cp shared/voice/profiles/us_persona.yaml shared/voice/profiles/germany_persona.yaml
# Edit germany_persona.yaml with linguistic patterns
```

3. **Assign to content**:
```yaml
# In Materials.yaml or contaminants.yaml:
materials:
  "New Material":
    author: {id: 5}  # Just the ID reference
```

4. **Export**:
```bash
python3 export/core/trivial_exporter.py
```

Frontmatter will automatically include full author data.

---

### Updating Author Credentials

**CORRECT** (Single location):
```bash
# Edit data/authors/Authors.yaml
vim data/authors/Authors.yaml
# Update credentials for author ID 1

# Re-export frontmatter
python3 export/core/trivial_exporter.py
```

All 153 materials and 98 contaminants with author ID 1 now show updated credentials.

**INCORRECT** (Don't do this):
```bash
# ❌ Editing individual frontmatter files
vim frontmatter/materials/aluminum.yaml  # WRONG!
```

Changes will be overwritten on next export.

---

### Updating Voice Characteristics

Voice profiles are **independent** of author data:

```bash
# Edit voice profile
vim shared/voice/profiles/taiwan_persona.yaml

# Changes affect generation immediately
# No need to re-export frontmatter
```

---

## Boundary Between Author & Voice

| Aspect | Location | Purpose |
|--------|----------|---------|
| **Identity** | Authors.yaml | Who the author is |
| **Credentials** | Authors.yaml | Education, experience, affiliations |
| **Contact** | Authors.yaml | Email, URLs, social links |
| **Voice Instructions** | Voice Profiles | How the author writes |
| **Linguistic Patterns** | Voice Profiles | Grammar, syntax, word choice |
| **Style Guidelines** | Voice Profiles | Formal vs casual, technical depth |

**Rule**: If it's **about the person**, it's in Authors.yaml. If it's **about the writing style**, it's in voice profiles.

---

## Common Issues & Solutions

### Issue: "Author not found" error during generation

**Cause**: Material references author ID that doesn't exist in Authors.yaml

**Solution**:
```python
# Check available authors
from shared.data.author_loader import load_all_authors
authors = load_all_authors()
print(authors.keys())  # [1, 2, 3, 4]

# Update material to valid author ID
```

---

### Issue: Truncated credentials in frontmatter

**Example**: `"3+ years in laser process"` (should be "processing R&D")

**Cause**: Data corruption during manual editing or import

**Solution**:
```bash
# Fix in Authors.yaml (single location)
vim data/authors/Authors.yaml
# Find and fix truncated credential

# Re-export
python3 export/core/trivial_exporter.py
```

---

### Issue: Voice doesn't match persona file

**Cause**: Mismatch between `author['persona_file']` reference and actual file

**Solution**:
```bash
# Check persona file reference
grep -A 20 "id: 1" data/authors/Authors.yaml | grep persona_file
# → persona_file: "taiwan_persona.yaml"

# Verify file exists
ls shared/voice/profiles/taiwan_persona.yaml

# If mismatch, update Authors.yaml reference
```

---

## Testing

### Verify Author Loader

```python
from shared.data.author_loader import get_author

author = get_author(1)
assert author['name'] == "Yi-Chun Lin"
assert 'credentials' in author
assert len(author) == 17 or len(author) == 18  # Should have all fields
```

### Verify Exporter Hydration

```bash
# Export one material
python3 export/core/trivial_exporter.py

# Check frontmatter
python3 << 'EOF'
import yaml
with open('frontmatter/materials/aluminum.yaml', 'r') as f:
    fm = yaml.safe_load(f)
author = fm['author']
assert len(author) >= 17  # Should have full author data
assert 'credentials' in author
assert 'email' in author
print("✅ Author hydration working")
EOF
```

---

## Future Enhancements

### Potential: Multi-Author Content

Currently 1:1 (one author per material). Could extend to multiple authors:

```yaml
materials:
  "Collaborative Material":
    authors: [1, 3]  # Co-authors
    primary_author: 1
```

Would require exporter updates to merge/prioritize voices.

---

### Potential: Dynamic Author Assignment

Currently manual assignment. Could add logic:

```python
def assign_author_by_category(material_category):
    """Assign author based on expertise"""
    author_expertise = {
        'metal': 4,  # Todd Dunning (US)
        'wood': 2,   # Alessandro Moretti (Italy)
        'plastic': 3, # Ikmanda Roswati (Indonesia)
        'ceramic': 1  # Yi-Chun Lin (Taiwan)
    }
    return author_expertise.get(material_category, 4)
```

---

## References

- **Implementation**: `shared/data/author_loader.py`
- **Export Hydration**: `export/core/trivial_exporter.py` (line 712-735)
- **Voice Loading**: `shared/voice/loader.py`
- **Data File**: `data/authors/Authors.yaml`
- **Voice Profiles**: `shared/voice/profiles/*.yaml`

---

**Last Updated**: December 15, 2025  
**Maintainer**: GitHub Copilot (Claude Sonnet 4.5)  
**Status**: ✅ Production Ready
