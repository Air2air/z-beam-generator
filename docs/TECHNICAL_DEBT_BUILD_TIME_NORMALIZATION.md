# Technical Debt: Build-Time Normalization Tasks

**Created**: January 5, 2026  
**Type**: Architecture compliance  
**Severity**: Medium (documented exception)  
**Status**: 🟡 APPROVED EXCEPTION (Grandfather Clause)

---

## 📋 Issue

Three export tasks violate Core Principle 0.6 by creating/enhancing data structure during build time:

1. **`normalize_applications`**: Converts simple list → collapsible structure
2. **`normalize_expert_answers`**: Converts FAQ (Q&A) → collapsible expert_answers structure  
3. **`normalize_safety_standards`**: Converts card presentation → collapsible structure

**Policy Requirement**:
> "ALL data enhancement (structure, metadata, relationships) MUST happen during generation, NOT at build/export time."

---

## 📊 Scope

### Affected Data

| Domain | Field | Items | Current Format | Required Format |
|--------|-------|-------|----------------|-----------------|
| Materials | `operational.industry_applications` | 153 | List of strings | Collapsible items |
| Materials | `operational.expert_answers` | 153 | FAQ (Q&A pairs) | Collapsible items |
| Materials | `safety.regulatory_standards` | 153 | Card items | Collapsible items |
| Compounds | `operational.expert_answers` | 34 | FAQ (Q&A pairs) | Collapsible items |
| Contaminants | `safety.regulatory_standards` | 98 | Card items (empty) | Collapsible items |

**Total**: 591 fields across 438 items require format conversion

### Why Not Bulk Regenerate?

- **Volume**: 591 fields would require hours of API calls
- **Cost**: Significant API usage for format-only change
- **Risk**: Potential data loss or quality regression
- **Value**: Low benefit (existing exports work correctly)

---

## ✅ Resolution

**Approved**: Grandfather Clause Exception (January 5, 2026)

### What Stays:
- Export normalization tasks remain **ACTIVE** for existing data
- Tasks perform format-only transformations (no data creation)
- Pre-Jan 5, 2026 data continues using tasks

### What Changes:
- **NEW content** (generated after Jan 5, 2026) **MUST** write collapsible format to source YAML
- Generation updated to output complete structures
- Natural migration as content regenerated

### Migration Timeline:
- **Phase 1** (Jan 5, 2026): Document exception ✅ COMPLETE
- **Phase 2** (Jan 5-6, 2026): Update generation logic  
- **Phase 3** (Ongoing): Natural migration as content regenerated
- **Phase 4** (Future, optional): Bulk migration if needed

---

## 🔧 Implementation Status

### Phase 1: Documentation ✅ COMPLETE
- [x] Grandfather clause added to `.github/copilot-instructions.md`
- [x] Technical debt document created (`docs/TECHNICAL_DEBT_BUILD_TIME_NORMALIZATION.md`)
- [x] Fix plan documented (`BUILD_TIME_VIOLATION_FIX_PLAN_JAN5_2026.md`)

### Phase 2: Fix Going Forward 🚧 IN PROGRESS
- [ ] Update `generation/core/adapters/domain_adapter.py` with collapsible conversion
- [ ] Add `_convert_to_collapsible()` method for applications, FAQs, standards
- [ ] Test with one material to verify format
- [ ] Update generation scripts to use collapsible format

### Phase 3: Natural Migration 📅 ONGOING
- [ ] All new materials use collapsible format
- [ ] All regenerated FAQs use collapsible format
- [ ] All regenerated applications use collapsible format
- [ ] Migration tracking (count of migrated vs legacy items)

---

## 📝 Task Details

### normalize_applications
**Location**: `export/generation/universal_content_generator.py` (lines 728-900)  
**Purpose**: Convert simple application list → collapsible structure  
**Status**: Active for pre-Jan 5 data

**Current Input** (Materials.yaml):
```yaml
operational:
  industry_applications:
    - Cultural Heritage
    - Aerospace
    - Medical
    - Electronics
```

**Current Output** (Frontmatter):
```yaml
operational:
  industryApplications:
    presentation: collapsible
    items:
      - title: Cultural Heritage
        content: "Cultural Heritage industry applications..."
        metadata:
          category: 'Industrial Applications'
          commonality: 'common'
        _display:
          _open: true
          order: 1
```

**NEW Generation** (after Phase 2):
Materials.yaml will contain the collapsible format directly.

---

### normalize_expert_answers
**Location**: `export/generation/universal_content_generator.py` (lines 1070-1217)  
**Purpose**: Convert FAQ Q&A → collapsible expert answers  
**Status**: Active for pre-Jan 5 data

**Current Input** (Materials.yaml):
```yaml
faq:
  - question: "What makes laser cleaning effective?"
    answer: "Laser cleaning provides precise control..."
```

**Current Output** (Frontmatter):
```yaml
operational:
  expertAnswers:
    presentation: collapsible
    items:
      - title: "What makes laser cleaning effective?"
        content: "Laser cleaning provides precise control..."
        metadata:
          category: 'Technical'
          difficulty: 'intermediate'
        _display:
          _open: true
          order: 1
```

**NEW Generation** (after Phase 2):
Materials.yaml will contain `operational.expert_answers` in collapsible format.

---

### normalize_safety_standards
**Location**: `export/generation/universal_content_generator.py` (lines 1219-1400)  
**Purpose**: Convert card presentation → collapsible structure  
**Status**: Active for pre-Jan 5 data

**Current Input** (Materials.yaml):
```yaml
safety:
  regulatory_standards:
    presentation: card
    items:
      - name: FDA
        longName: Food and Drug Administration
        description: "FDA 21 CFR 1040.10..."
        url: "https://..."
        image: "/images/logo/logo-org-fda.png"
```

**Current Output** (Frontmatter):
```yaml
safety:
  regulatoryStandards:
    presentation: collapsible
    items:
      - title: "FDA - Food and Drug Administration"
        content: "FDA 21 CFR 1040.10..."
        metadata:
          organization: 'FDA'
          category: 'laser-safety'
          url: "https://..."
          image: "/images/logo/logo-org-fda.png"
        _display:
          _open: true
          order: 1
```

**NEW Generation** (after Phase 2):
Materials.yaml will contain `safety.regulatory_standards` in collapsible format.

---

## 🎯 Compliance Status

### Current State (Jan 5, 2026):
- ⚠️ **VIOLATION DOCUMENTED**: Three tasks create structure during export
- ✅ **EXCEPTION APPROVED**: Grandfather clause for pre-Jan 5 data
- 🚧 **FIX IN PROGRESS**: Generation update for new content

### Target State (Post Phase 2):
- ✅ **COMPLIANT**: New content uses collapsible format at generation
- ✅ **DOCUMENTED**: Legacy data uses export tasks (approved exception)
- 📊 **TRACKED**: Migration progress monitored

---

## 🔍 Monitoring & Metrics

### Migration Tracking
Track percentage of items using native collapsible format vs legacy format:

```bash
# Count items with collapsible format in source YAML
python3 scripts/tools/count_collapsible_native.py

# Expected output:
# Materials:
#   industry_applications: 0/153 (0%) native collapsible
#   expert_answers: 0/153 (0%) native collapsible  
#   regulatory_standards: 0/153 (0%) native collapsible
#
# Compounds:
#   expert_answers: 0/34 (0%) native collapsible
#
# Contaminants:
#   regulatory_standards: 0/98 (0%) native collapsible
#
# TOTAL: 0/591 (0%) using native collapsible format
```

### Success Criteria:
- [ ] New materials (post-Jan 5): 100% native collapsible
- [ ] Regenerated content: 100% native collapsible
- [ ] Overall migration: >50% within 6 months (stretch goal)

---

## 📚 Related Documentation

- **Policy**: `.github/copilot-instructions.md` - Core Principle 0.6 + Grandfather Clause
- **Fix Plan**: `BUILD_TIME_VIOLATION_FIX_PLAN_JAN5_2026.md` (root)
- **Implementation**: `export/generation/universal_content_generator.py` (normalization tasks)
- **Generation**: `generation/core/adapters/domain_adapter.py` (write_component method)

---

## ✅ Approval

**Status**: APPROVED (January 5, 2026)  
**Decision**: Option C (Hybrid Approach)  
**Rationale**: Pragmatic solution balancing compliance with practical constraints

- ✅ Existing data continues working (no breaking changes)
- ✅ New content compliant (no new violations)
- ✅ Natural migration path (gradual improvement)
- ✅ Documented exception (transparent about technical debt)

**Next Review**: June 2026 (6 months) - Assess migration progress
