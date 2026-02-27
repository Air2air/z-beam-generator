# Naming Conventions Standardization Proposal
**Date**: January 3, 2026  
**Status**: Proposed  
**Grade**: Standardization needed (Current: C, Target: A)

## Executive Summary

This document proposes standardized naming conventions across the Z-Beam Generator codebase to improve consistency, readability, and maintainability.

**Current State**: Mixed conventions (ALL_CAPS docs, PascalCase data, inconsistent verbs)  
**Proposed State**: Consistent patterns across all file types and code elements  
**Migration**: Gradual adoption for new code, optional refactoring for existing

---

## 1. Documentation File Naming

### Current Issues
```
❌ FRONTEND_GUIDE_IMPLEMENTATION_JAN3_2026.md     (ALL_CAPS, inconsistent date)
❌ SECTION_ORGANIZATION_ASSESSMENT_JAN3_2026.md   (ALL_CAPS, inconsistent date)
❌ E2E_DATA_ARCHITECTURE_EVALUATION_DEC15_2025.md (ALL_CAPS, E2E ambiguous)
```

### Proposed Standard
**Pattern**: `<category>-<description>-YYYY-MM-DD.md`

**Categories**:
- `guide-` - User/developer guides
- `assessment-` - System evaluations
- `proposal-` - Architecture proposals
- `implementation-` - Implementation reports
- `analysis-` - Technical analysis

**Examples**:
```
✅ guide-frontend-implementation-2026-01-03.md
✅ assessment-section-organization-2026-01-03.md
✅ analysis-data-architecture-comprehensive-2025-12-15.md
✅ proposal-naming-conventions-2026-01-03.md
```

**Rationale**:
- Kebab-case is standard for documentation (GitHub, most projects)
- ISO date format (YYYY-MM-DD) is sortable and unambiguous
- Category prefix enables grouping and filtering
- Lowercase is easier to type and read

---

## 2. Python Class Naming

### Current Issues
```python
❌ class UniversalContentGenerator:     # "Universal" adds noise
❌ class UniversalExporter:              # Is there a non-universal exporter?
```

### Proposed Standard
**Pattern**: Remove redundant prefixes like "Universal", "Simple", "Basic"

**Examples**:
```python
✅ class ContentGenerator:       # Clear, concise
✅ class Exporter:                # Primary implementation
✅ class MaterialsCoordinator:   # Domain-specific

# Keep prefixes when meaningful distinction exists:
✅ class BatchContentGenerator:  # Distinguishes from single
✅ class AsyncExporter:           # Distinguishes from sync
```

**Rationale**:
- "Universal" implies there are non-universal versions (there aren't)
- Shorter names reduce cognitive load
- Prefixes only useful when distinguishing between variants
- See: `.github/copilot-instructions.md` Simplify Naming policy

---

## 3. Task Method Naming

### Current Issues
```python
❌ _task_normalize_compounds         # "normalize" = restructure
❌ _task_enrich_relationships         # "enrich" = add metadata
❌ _task_add_section_metadata         # "add" = populate
❌ _task_restructure_relationships    # "restructure" = reorganize
```

**Problem**: Four different verbs for similar operations (adding/modifying data)

### Proposed Standard
**Pattern**: `_task_<action>_<target>` where action is from controlled vocabulary

**Controlled Vocabulary**:
- `normalize_` - Move/restructure content (changes organization)
- `enrich_` - Add metadata/context (adds fields to existing items)
- `generate_` - Create new content (creates new sections/fields)
- `group_` - Organize items (categorization/grouping)
- `transform_` - Change format (data type conversions)

**Examples**:
```python
✅ _task_normalize_compounds         # Moves content to relationships
✅ _task_enrich_relationships         # Adds frequency/severity metadata
✅ _task_generate_section_metadata   # Creates _section blocks including developer-purpose sectionMetadata text
✅ _task_group_relationships          # Categorizes by type
✅ _task_transform_faq                # Converts array → collapsible
```

**Decision Tree**:
```
Are you moving content between locations?
├─ YES → normalize_*
└─ NO → Are you adding new fields to existing items?
    ├─ YES → enrich_*
    └─ NO → Are you creating entirely new content?
        ├─ YES → generate_*
        └─ NO → Are you reorganizing items?
            ├─ YES → group_*
            └─ NO → transform_*
```

---

## 4. Data File Naming

### Current Issues
```
❌ Materials.yaml      (PascalCase - source data)
❌ Settings.yaml       (PascalCase - source data)
✓  materials.yaml      (lowercase - config)
✓  compounds.yaml      (lowercase - config)
```

**Problem**: Same domain, different case depending on file type

### Proposed Standard
**Pattern**: All YAML files use lowercase + domain + type suffix

**Examples**:
```
✅ materials-data.yaml      # Source data (replaces Materials.yaml)
✅ materials-config.yaml    # Export config
✅ settings-data.yaml       # Source data (replaces Settings.yaml)
✅ settings-config.yaml     # Export config
```

**OR** (Simpler - directory distinguishes type):
```
data/materials/materials.yaml          # Lowercase in data/
export/config/materials.yaml           # Lowercase in config/
```

**Rationale**:
- Consistent casing reduces errors
- Suffix clarifies purpose when files are out of context
- Most projects use lowercase for data files
- Directory structure already provides type context

**Recommendation**: Use directory-based approach (simpler, less refactoring)

---

## 5. Action Verb Standardization Summary

### Current Usage Analysis
```python
# Across codebase, we use these action verbs:
normalize_*     (4 uses)  - Restructure/move content
enrich_*        (2 uses)  - Add metadata
add_*           (3 uses)  - Create fields
restructure_*   (1 use)   - Reorganize
generate_*      (5 uses)  - Create content
transform_*     (0 uses)  - Convert format
group_*         (1 use)   - Categorize
```

### Proposed Consolidation
```python
# KEEP (clear, distinct meanings):
✅ normalize_*   - Move content to proper locations
✅ enrich_*      - Add metadata to existing items
✅ generate_*    - Create new content/sections
✅ group_*       - Categorize/organize items

# REPLACE:
❌ add_*         → generate_* (creating new content)
❌ restructure_* → normalize_* (reorganizing structure)
❌ create_*      → generate_* (consistent with generate)

# NEW (if needed):
✅ transform_*   - Format conversions (array → collapsible)
```

---

## 6. Migration Plan

### Phase 1: Documentation (Low Risk)
**Timeline**: 1 week  
**Impact**: Zero code changes

1. Rename recent ALL_CAPS docs to kebab-case
2. Update references in README.md
3. Add naming guide to docs/08-development/

**Files to Rename**:
```bash
# Recent documentation (2025-12 to 2026-01)
FRONTEND_GUIDE_IMPLEMENTATION_JAN3_2026.md
  → guide-frontend-implementation-2026-01-03.md

SECTION_ORGANIZATION_ASSESSMENT_JAN3_2026.md
  → assessment-section-organization-2026-01-03.md

E2E_DATA_ARCHITECTURE_EVALUATION_DEC15_2025.md
  → analysis-data-architecture-comprehensive-2025-12-15.md

E2E_PARAMETER_FLOW.md
  → analysis-parameter-flow-complete.md
```

**Archive Strategy**:
- Keep old files in `docs/archive/old-naming/` for 30 days
- Add redirect notes in README.md
- Update all internal links

### Phase 2: Python Classes (Medium Risk)
**Timeline**: 2 weeks  
**Impact**: Import statement changes

1. Rename `UniversalContentGenerator` → `ContentGenerator`
2. Rename `UniversalExporter` → `Exporter`
3. Update all imports
4. Run full test suite

**Verification**:
```bash
# Find all imports
grep -r "from.*UniversalContentGenerator" .
grep -r "import.*UniversalExporter" .

# Update and test
pytest tests/
```

### Phase 3: Task Methods (Low Risk)
**Timeline**: 1 week  
**Impact**: Config file changes only

1. Standardize verb usage in new tasks
2. Add task naming guide to documentation
3. Optionally rename existing tasks (no breaking changes)

**New tasks MUST follow standard**:
- Use controlled vocabulary (normalize, enrich, generate, group, transform)
- Include action + target in name
- Document decision in task handler

### Phase 4: Data Files (High Risk - OPTIONAL)
**Timeline**: 4 weeks  
**Impact**: Massive refactoring

**Recommendation**: **DEFER** - Too much risk for cosmetic benefit

**Rationale**:
- Materials.yaml referenced in 50+ files
- Settings.yaml referenced in 40+ files
- High risk of breaking production
- Directory structure already provides context
- Lowercase only benefit is consistency

**IF pursued**:
1. Create lowercase versions (materials-data.yaml)
2. Update all references (massive find/replace)
3. Deprecated warnings for 3 months
4. Remove PascalCase files after migration
5. Full regression testing

---

## 7. Enforcement Strategy

### For New Code (Mandatory)
1. **Documentation**: Use kebab-case + ISO dates + category prefix
2. **Classes**: No "Universal" prefix unless meaningful distinction
3. **Tasks**: Use controlled vocabulary (normalize, enrich, generate, group, transform)
4. **Data files**: Follow existing convention (defer standardization)

### For Existing Code (Optional)
1. **Phase 1**: Rename recent docs (low risk, high visibility)
2. **Phase 2**: Rename Python classes (medium risk, medium benefit)
3. **Phase 3**: Standardize task verbs (low risk, low priority)
4. **Phase 4**: Defer data file renaming (high risk, low benefit)

### Code Review Checklist
```markdown
- [ ] Documentation uses kebab-case-YYYY-MM-DD.md format
- [ ] No "Universal" prefix on classes (unless justified)
- [ ] Task methods use controlled vocabulary verbs
- [ ] Action verbs are consistent with purpose
```

---

## 8. Implementation Examples

### Example 1: New Documentation
```bash
# ❌ OLD PATTERN (rejected):
touch FEATURE_IMPLEMENTATION_JAN5_2026.md

# ✅ NEW PATTERN (required):
touch implementation-feature-name-2026-01-05.md
```

### Example 2: New Class
```python
# ❌ OLD PATTERN (rejected):
class UniversalRelationshipBuilder:
    pass

# ✅ NEW PATTERN (required):
class RelationshipBuilder:
    pass

# ✅ ACCEPTABLE (meaningful distinction):
class BatchRelationshipBuilder:  # Distinguishes from single
    pass
```

### Example 3: New Task
```python
# ❌ OLD PATTERN (inconsistent):
def _task_add_metadata_to_items(self, frontmatter, config):
    """Adds metadata."""
    pass

# ✅ NEW PATTERN (controlled vocabulary):
def _task_enrich_relationship_items(self, frontmatter, config):
    """Enriches relationship items with frequency/severity metadata.
    
    Action: enrich (adding metadata to existing items)
    Target: relationship_items
    """
    pass
```

### Example 4: Documentation Reference
```python
# In code comments:
# ❌ OLD: See FRONTEND_GUIDE_IMPLEMENTATION_JAN3_2026.md
# ✅ NEW: See docs/guides/guide-frontend-implementation-2026-01-03.md

# In docstrings:
"""
Normalizes compound structure by moving scattered fields to relationships.

See Also:
    docs/guides/guide-frontend-implementation-2026-01-03.md
    Schema version: 5.0.0
"""
```

---

## 9. Benefits of Standardization

### Improved Discoverability
```bash
# Current (hard to filter):
ls docs/*.md | grep -i implementation
# Mixed: IMPLEMENTATION, Implementation, implementation

# Proposed (easy to filter):
ls docs/*implementation*.md
# Consistent: all lowercase, predictable pattern
```

### Reduced Cognitive Load
```python
# Current (what's the difference?):
UniversalContentGenerator  # Is there a BasicContentGenerator?
UniversalExporter           # vs PartialExporter?

# Proposed (clear):
ContentGenerator            # Primary implementation
BatchContentGenerator       # Batch variant (clear distinction)
```

### Better Tooling Support
```bash
# Git log sorting (current):
git log --oneline -- docs/*.md
# Dates out of order: JAN3_2026, DEC15_2025, NOV22_2025

# Git log sorting (proposed):
git log --oneline -- docs/*.md
# Dates in order: 2025-11-22, 2025-12-15, 2026-01-03
```

---

## 10. Decision

**Approval Required**:
- [ ] Phase 1 (Documentation renaming) - Approved / Rejected
- [ ] Phase 2 (Class renaming) - Approved / Rejected / Defer
- [ ] Phase 3 (Task verb standardization) - Approved / Rejected / Defer
- [ ] Phase 4 (Data file renaming) - Approved / Rejected / **Defer Recommended**

**Recommendation**:
- ✅ **APPROVE Phase 1** (low risk, high visibility, easy to implement)
- ✅ **APPROVE Phase 2** (medium risk, medium benefit, worthwhile)
- ✅ **APPROVE Phase 3** (low risk, improves clarity)
- ❌ **DEFER Phase 4** (high risk, low benefit, not worth effort)

**Next Steps** (if approved):
1. User confirms which phases to implement
2. Create migration script for Phase 1 (doc renaming)
3. Update imports for Phase 2 (class renaming)
4. Document controlled vocabulary for Phase 3 (task verbs)
5. Add naming guidelines to `.github/copilot-instructions.md`

---

## Grade: Standardization Proposal

**Current Naming Consistency**: C (60/100)
- Multiple conventions coexist
- No documented standard
- Inconsistent verb usage

**With Phase 1-3 Implementation**: A (90/100)
- Consistent documentation naming
- Clear class naming (no noise words)
- Standardized action vocabulary
- Documented guidelines

**Effort Required**:
- Phase 1: 2-3 hours (rename + update links)
- Phase 2: 4-6 hours (rename classes + update imports + test)
- Phase 3: 1-2 hours (document guidelines + enforce in reviews)
- **Total**: 1-2 days of work

**User Decision Required**: Approve phases to proceed with implementation.
