# Frontmatter Source of Truth Policy

**Version**: 1.1  
**Date**: December 24, 2025  
**Status**: MANDATORY - CRITICAL ARCHITECTURAL POLICY

---

## 🚨 **CRITICAL PRINCIPLE**

**Frontmatter files are GENERATED OUTPUT, not source data.**

**NEVER edit frontmatter files directly. ALL changes MUST be made in source data or export configurations.**

## ✅ **MANDATORY RULE: SOURCE + GENERATOR ONLY (Feb 23, 2026)**

**All updates must be made in source data and generators, NOT exporters.**

- ✅ **Update content and structure in source data** (`data/*.yaml`)
- ✅ **Update generation logic in generators** (`generation/`, `domains/*`, `export/generation/*` tasks)
- ❌ **Do NOT update exporter logic to fix data issues** (`export/core/*`, `export/config/*`)
- ❌ **Do NOT add missing fields at export time** (exporters are transform-only)

**Rationale**: Exporters must remain presentation-only. Any data corrections belong in source data or generation logic, or they will be overwritten and violate Core Principle 0.6 (No Build-Time Data Enhancement).

## ✅ **MANDATORY RULE: SOURCE DATA MUST BE FULLY POPULATED (Feb 28, 2026)**

This is a **global policy across all domains and all required fields**.

Required content must already exist in source YAML before generation/export operations. Generation-time paths may route or format fields, but must not synthesize missing required content.

- ✅ Source records must carry canonical required fields for their schema paths
- ✅ Validation/tests must fail fast when required source fields are missing or placed in legacy keys
- ✅ If a source record includes `_section`, both `sectionTitle` and `sectionDescription` must be non-empty in source data
- ❌ Do NOT rely on generation-time enhancers to create required `sectionTitle` / `sectionDescription`
- ❌ Do NOT place required semantic content in deprecated convenience keys when canonical nested paths exist

**Applications relationship canonical example**:
- `relationships.discovery.relatedMaterials._section.sectionTitle`
- `relationships.discovery.relatedMaterials._section.sectionDescription`
- `relationships.interactions.contaminatedBy._section.sectionTitle`
- `relationships.interactions.contaminatedBy._section.sectionDescription`

## ⚠️ **POSTPROCESSING MANDATORY POLICY (December 24, 2025)**

**Postprocessing MUST work on source data ONLY:**
- ✅ Read from `data/*.yaml` files (source data)
- ✅ Write to `data/*.yaml` files (source data)  
- ❌ NEVER read from `frontmatter/*.yaml` files
- ❌ NEVER write to `frontmatter/*.yaml` files
- ✅ User runs `--export` after postprocessing to update frontmatter

**Grade**: F violation if postprocessing touches frontmatter files directly.

## ✅ **MANDATORY PARITY VERIFICATION (Feb 27, 2026)**

After any generator/export/config change that affects frontmatter output, run all three steps:

1. `python3 run.py --export-all --no-parallel`
2. `python3 scripts/check_field_order.py`
3. `python3 scripts/validation/validate_frontmatter_schema.py --strict`

Validator role split:
- `check_field_order.py` verifies ordering parity across domains.
- `validate_frontmatter_schema.py --strict` verifies schema shape/completeness.

CI enforcement:
- `.github/workflows/data-validation.yml` includes `validate-frontmatter-parity` job to run this gate on push/PR.

---

## 📐 **Three-Layer Architecture**

### Layer 1: Source Data (EDIT HERE)
**Location**: `data/*/`
- `data/materials/Materials.yaml`
- `data/contaminants/Contaminants.yaml`
- `data/compounds/Compounds.yaml`
- `data/settings/Settings.yaml`
- `data/associations/DomainAssociations.yaml`

**Purpose**: Single source of truth for all entity data

**When to Edit**:
- ✅ Adding/modifying entity properties
- ✅ Updating content (descriptions, names, values)
- ✅ Changing relationships between entities
- ✅ Correcting data errors or inconsistencies

### Layer 2: Export Configuration (EDIT HERE)
**Location**: `export/config/*.yaml`
- `export/config/materials.yaml`
- `export/config/contaminants.yaml`
- `export/config/compounds.yaml`
- `export/config/settings.yaml`

**Purpose**: Define how source data transforms into frontmatter

**When to Edit**:
- ✅ Adding _section metadata to relationships
- ✅ Configuring enrichers (presentation, icons, order, variant)
- ✅ Modifying field transformations or enrichments
- ✅ Changing export structure or formatting

### Layer 3: Frontmatter Files (NEVER EDIT)
**Location**: `../z-beam/frontmatter/*/`
- `../z-beam/frontmatter/materials/*.yaml`
- `../z-beam/frontmatter/contaminants/*.yaml`
- `../z-beam/frontmatter/compounds/*.yaml`
- `../z-beam/frontmatter/settings/*.yaml`

**Purpose**: Generated output for frontend consumption

**⛔ NEVER EDIT DIRECTLY**:
- ❌ These files are REGENERATED on every export
- ❌ Manual edits WILL BE OVERWRITTEN
- ❌ Changes here DO NOT persist
- ❌ Scripts that modify these files are WRONG

---

## 🔄 **Correct Workflow for Changes**

### Example 1: Adding _section Metadata to Relationships

**❌ WRONG Approach** (will fail):
```bash
# DON'T DO THIS - Changes will be overwritten!
sed -i '' 's/produces_compounds:/produces_compounds:\n  _section:/' frontmatter/contaminants/*.yaml
```

**✅ CORRECT Approach** (persists):
```bash
# 1. Edit export config to add section metadata
vim export/config/contaminants.yaml

# Add to sections:
produces_compounds:
  presentation: card
  title: "Hazardous Compounds"
  description: "Compounds released during removal"
  sectionMetadata: "Developer purpose: defines how this section should cover compound-generation risks and context."
  icon: "flame"
  order: 16
  variant: "danger"

# 2. Regenerate frontmatter
python3 run.py --export --domain contaminants

# 3. Changes now persist in all future exports
```

### Example 2: Fixing Data Error in Material Description

**❌ WRONG**:
```bash
# Editing frontmatter directly
vim ../z-beam/frontmatter/materials/aluminum-laser-cleaning.yaml
```

**✅ CORRECT**:
```bash
# 1. Edit source data
vim data/materials/Materials.yaml

# 2. Regenerate
python3 run.py --export --domain materials
```

### Example 3: Normalizing Relationship Format

**❌ WRONG**:
```bash
# Script that modifies frontmatter files
python3 scripts/tools/normalize_frontmatter_files.py  # WRONG!
```

**✅ CORRECT**:
```bash
# 1. Update export enricher configuration
vim export/config/contaminants.yaml

# 2. Enhance enricher to handle new format
vim export/enrichers/metadata/section_metadata_enricher.py

# 3. Regenerate ALL domains
python3 run.py --export --domain all
```

---

## 🚫 **Prohibited Patterns**

### Pattern 1: Direct Frontmatter Modification Scripts
```python
# ❌ WRONG - This will not persist
def fix_frontmatter_files():
    for file in Path("../z-beam/frontmatter/").rglob("*.yaml"):
        data = yaml.safe_load(file)
        data['relationships']['new_field'] = {...}  # WRONG!
        yaml.dump(data, file)
```

**Why Wrong**: Next export overwrites these changes.

### Pattern 2: Manual Frontmatter Editing
```bash
# ❌ WRONG
vim ../z-beam/frontmatter/materials/steel-laser-cleaning.yaml
# Make changes, save, commit...
# Next export: ALL CHANGES LOST
```

### Pattern 3: Treating Frontmatter as Source
```bash
# ❌ WRONG - Using frontmatter as reference for data updates
python3 scripts/sync_from_frontmatter_to_source.py  # BACKWARDS!
```

**Why Wrong**: Frontmatter IS the output, not the input.

---

## ✅ **Verification Checklist**

Before making ANY changes to frontmatter-related code:

- [ ] **Am I editing source data** (`data/*.yaml`)?
  - ✅ YES: Proceed
  - ❌ NO: Go to next question

- [ ] **Am I editing export config** (`export/config/*.yaml`)?
  - ✅ YES: Proceed
  - ❌ NO: Go to next question

- [ ] **Am I editing enricher/generator code** (`export/enrichers/`, `export/generation/`)?
  - ✅ YES: Proceed (architectural change)
  - ❌ NO: Go to next question

- [ ] **Am I editing frontmatter files directly** (`../z-beam/frontmatter/`)?
  - ⛔ **STOP** - This is WRONG
  - Identify what you're trying to change
  - Make change in Layer 1 or Layer 2 instead

---

## 🧪 **Testing Persistence**

To verify a change persists:

```bash
# 1. Make your change (in source or config)

# 2. Export domain
python3 run.py --export --domain contaminants

# 3. Verify change appears in frontmatter
cat ../z-beam/frontmatter/contaminants/rust-contamination.yaml | grep "your_change"

# 4. Export AGAIN (this is the real test)
python3 run.py --export --domain contaminants

# 5. Verify change STILL appears (not overwritten)
cat ../z-beam/frontmatter/contaminants/rust-contamination.yaml | grep "your_change"

# ✅ If still present: Change persists (CORRECT)
# ❌ If missing: Change doesn't persist (WRONG - made in wrong layer)
```

---

## 📚 **Related Documentation**

- **Export Architecture**: `docs/02-architecture/export-system.md`
- **Frontmatter Generation Guide**: `docs/FRONTMATTER_GENERATION_GUIDE.md`
- **Enricher Development**: `export/enrichers/README.md`
- **Domain Configuration**: `export/config/README.md`

---

## 🎓 **Common Scenarios**

### Scenario: "I need to add a new field to all materials"

**Wrong**: Edit 153 frontmatter files manually  
**Correct**: 
1. Add field to `data/materials/Materials.yaml` (one place)
2. Run export
3. Field appears in all 153 generated frontmatter files

### Scenario: "Relationships need _section metadata"

**Wrong**: Script that adds `_section:` blocks to frontmatter files  
**Correct**: Configure `SectionMetadataEnricher` in `export/config/*.yaml`

### Scenario: "Fix typo in entity name"

**Wrong**: Edit frontmatter file  
**Correct**: Fix in `data/*/` source file

### Scenario: "Change relationship presentation style"

**Wrong**: Edit frontmatter `presentation:` fields  
**Correct**: Update `sections:` config in `export/config/*.yaml`

---

## ⚖️ **Policy Enforcement**

**Automated Checks**:
- Pre-commit hooks warn if frontmatter files modified
- CI/CD fails if frontmatter changes detected without source changes
- Code review checklist includes "Source of Truth" verification

**Manual Review Required**:
- Any PR touching `../z-beam/frontmatter/` files
- Scripts that operate on frontmatter directory
- Documentation claiming frontmatter is editable

**Grade**: F violation for ANY script or process that modifies frontmatter files directly without going through export pipeline.

---

## 📝 **Summary**

| Question | Answer | Action |
|----------|--------|--------|
| Where is the data? | `data/*.yaml` | Edit here for data changes |
| How is it transformed? | `export/config/*.yaml` | Edit here for structure changes |
| Where is the output? | `../z-beam/frontmatter/*.yaml` | **NEVER EDIT** - regenerated automatically |

**Remember**: Frontmatter files are like compiled binaries - you don't edit the `.exe`, you edit the source code and recompile.
