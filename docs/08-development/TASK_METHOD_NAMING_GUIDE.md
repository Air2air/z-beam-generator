# Task Method Naming Guide
**Date**: January 3, 2026  
**Status**: Active  
**Applies To**: All task methods in `export/generation/universal_content_generator.py`

## Purpose

This guide defines a controlled vocabulary for naming task methods to ensure consistency, clarity, and maintainability across the codebase.

---

## Naming Pattern

**Format**: `_task_<action>_<target>`

- **action**: From controlled vocabulary (see below)
- **target**: What the action operates on (e.g., `compounds`, `relationships`, `metadata`)

**Examples**:
```python
_task_normalize_compounds         # Action: normalize, Target: compounds
_task_enrich_relationships         # Action: enrich, Target: relationships
_task_generate_section_metadata   # Action: generate, Target: section_metadata
_task_group_relationships          # Action: group, Target: relationships
```

---

## Controlled Vocabulary

### 1. `normalize_*` - Restructure/Move Content
**Purpose**: Move content from one location to another, change organization/structure

**Use When**:
- Moving scattered fields into relationships
- Reorganizing data structure
- Converting between formats (but see `transform_*`)

**Examples**:
```python
def _task_normalize_compounds(self, frontmatter, config):
    """Normalizes compound structure by moving scattered fields to relationships.
    
    Moves 6 top-level fields (health_effects, exposure_guidelines, etc.) into
    proper subject areas (safety, detection, operational).
    
    Action: normalize (restructuring organization)
    Target: compounds
    """
```

**Anti-Pattern**:
```python
❌ _task_restructure_compounds()  # Use normalize_ instead
❌ _task_move_fields()             # Too vague, what fields?
```

---

### 2. `enrich_*` - Add Metadata to Existing Items
**Purpose**: Add contextual metadata/properties to existing items

**Use When**:
- Adding frequency/severity to relationship items
- Adding metadata fields to existing structures
- Augmenting data without changing structure

**Examples**:
```python
def _task_enrich_relationships(self, frontmatter, config):
    """Enriches relationship items with frequency and severity metadata.
    
    Adds contextual metadata to relationship items:
    - frequency: common | occasional | rare
    - severity: high | moderate | low
    
    Action: enrich (adding metadata to existing items)
    Target: relationships
    """
```

**Anti-Pattern**:
```python
❌ _task_add_metadata()           # Too vague, use enrich_*
❌ _task_update_relationships()   # Ambiguous, updating how?
```

---

### 3. `generate_*` - Create New Content/Sections
**Purpose**: Create entirely new content that didn't exist before

**Use When**:
- Creating new sections
- Generating sectionMetadata blocks
- Producing new fields from scratch

**Examples**:
```python
def _task_generate_section_metadata(self, frontmatter, config):
    """Generates sectionMetadata blocks for relationship sections.
    
    Creates complete metadata including:
    - title, description, icon, order, variant
    
    Action: generate (creating new content)
    Target: section_metadata
    """
```

**Anti-Pattern**:
```python
❌ _task_add_section_metadata()   # Use generate_ for new content
❌ _task_create_metadata()        # Use generate_ consistently
```

---

### 4. `group_*` - Categorize/Organize Items
**Purpose**: Organize items into categories, groups, or hierarchies

**Use When**:
- Grouping relationships by type
- Categorizing items
- Creating hierarchical structures

**Examples**:
```python
def _task_group_relationships(self, frontmatter, config):
    """Groups relationship items by type or category.
    
    Organizes relationships into groups:
    - contamination_by_type
    - removal_by_method
    
    Action: group (categorizing items)
    Target: relationships
    """
```

**Anti-Pattern**:
```python
❌ _task_categorize_items()       # Use group_ for consistency
❌ _task_organize_relationships() # Too vague
```

---

### 5. `transform_*` - Convert Format/Data Type
**Purpose**: Change data format or type without changing meaning

**Use When**:
- Converting arrays to objects
- Changing data types (string → number)
- Format conversions (flat → nested)

**Examples**:
```python
def _task_transform_faq(self, frontmatter, config):
    """Transforms FAQ from flat array to collapsible structure.
    
    Converts:
      faq: ["Q: ...", "A: ..."]
    To:
      expert_answers:
        presentation_type: collapsible
        items: [{question: "...", answer: "..."}]
    
    Action: transform (format conversion)
    Target: faq
    """
```

**Anti-Pattern**:
```python
❌ _task_convert_faq()            # Use transform_ for consistency
❌ _task_change_format()          # Too vague
```

---

## Decision Tree

Use this tree to choose the correct action verb:

```
Are you moving content between locations?
├─ YES → normalize_*
│
└─ NO → Are you adding new fields to EXISTING items?
    ├─ YES → enrich_*
    │
    └─ NO → Are you creating ENTIRELY NEW content?
        ├─ YES → generate_*
        │
        └─ NO → Are you organizing items into groups?
            ├─ YES → group_*
            │
            └─ NO → Are you converting format/data type?
                ├─ YES → transform_*
                │
                └─ UNCLEAR? → Ask for clarification
```

---

## Real Examples from Codebase

### normalize_compounds (Lines 1045-1233)
**Action**: `normalize_` (moving scattered fields)  
**Target**: `compounds`

**What it does**: Moves 6 top-level fields into relationship subject areas
- health_effects → safety.health_impacts
- exposure_guidelines → safety.exposure_guidance
- etc.

**Why normalize**: Content is being MOVED/REORGANIZED, not created or enriched

---

### enrich_material_relationships (Lines 1235-1318)
**Action**: `enrich_` (adding metadata to existing items)  
**Target**: `material_relationships`

**What it does**: Adds frequency/severity to existing relationship items
```python
{id: "rust"} → {id: "rust", frequency: "common", severity: "moderate"}
```

**Why enrich**: Metadata is being ADDED to existing items, structure unchanged

---

### normalize_expert_answers (Existing)
**Action**: `normalize_` (restructuring content)  
**Target**: `expert_answers`

**What it does**: Converts flat FAQ to structured collapsible
- Moves from top-level to relationships
- Changes format from array to object

**Why normalize**: Content is being MOVED AND RESTRUCTURED

---

## Guidelines for New Tasks

### Before Creating a Task Method

1. **Define the action clearly**: What is the PRIMARY operation?
   - Moving content? → `normalize_`
   - Adding metadata? → `enrich_`
   - Creating new content? → `generate_`
   - Organizing items? → `group_`
   - Converting format? → `transform_`

2. **Define the target clearly**: What does it operate on?
   - Be specific: `compounds`, not `data`
   - Use singular or plural based on convention
   - Match field names where possible

3. **Write the docstring first**:
   ```python
   def _task_<action>_<target>(self, frontmatter, config):
       """[Action description] [target] by [method].
       
       [Detailed explanation of what changes]
       
       Action: [action] ([why this action])
       Target: [target]
       """
   ```

4. **Register in handler map**:
   ```python
   # In __init__
   self._task_handlers = {
       'normalize_compounds': self._task_normalize_compounds,
       'enrich_relationships': self._task_enrich_relationships,
   }
   ```

---

## Enforcement

### Code Review Checklist

When reviewing new task methods:
- [ ] Does the action verb come from controlled vocabulary?
- [ ] Is the target specific and clear?
- [ ] Does the docstring explain the action classification?
- [ ] Is the task registered in the handler map?
- [ ] Does the implementation match the action verb?
  - `normalize_` should move/restructure
  - `enrich_` should add metadata
  - `generate_` should create new content
  - `group_` should categorize
  - `transform_` should convert format

### Bad Examples to Reject

```python
❌ _task_add_metadata_to_items()       # Vague, use enrich_relationships
❌ _task_update_compounds()            # Ambiguous, updating how?
❌ _task_fix_structure()               # Too vague
❌ _task_improve_data()                # Not descriptive
❌ _task_handle_relationships()        # What does "handle" mean?
❌ _task_do_normalization()            # Redundant "do"
```

### Good Examples to Approve

```python
✅ _task_normalize_safety_data()      # Clear: moving safety fields
✅ _task_enrich_contamination_items()  # Clear: adding metadata
✅ _task_generate_toc()                # Clear: creating table of contents
✅ _task_group_by_severity()           # Clear: categorizing by severity
✅ _task_transform_nested_lists()      # Clear: format conversion
```

---

## Migration Guide for Existing Tasks

If you find an existing task that doesn't follow this convention:

### Step 1: Identify Correct Action
Use the decision tree to determine the correct action verb.

### Step 2: Propose Rename
Document the proposed change:
```markdown
**Current**: `_task_add_section_metadata`
**Proposed**: `_task_generate_section_metadata`
**Reason**: Creates new content from scratch (generate_ not add_)
```

### Step 3: Update References
1. Rename method in `universal_content_generator.py`
2. Update handler map
3. Update config.yaml task names
4. Run tests to verify
5. Update documentation

### Step 4: Update Docstring
Add action classification to docstring:
```python
"""Generates sectionMetadata blocks...

Action: generate (creating new content)
Target: section_metadata
"""
```

---

## Examples by Category

### normalize_* (Restructure/Move)
- `_task_normalize_compounds` ✅ (implemented)
- `_task_normalize_expert_answers` ✅ (implemented)
- `_task_normalize_relationships` (hypothetical)
- `_task_normalize_safety_data` (hypothetical)

### enrich_* (Add Metadata)
- `_task_enrich_material_relationships` ✅ (implemented)
- `_task_enrich_relationship_items` ✅ (implemented)
- `_task_enrich_with_context` (hypothetical)

### generate_* (Create Content)
- `_task_generate_section_metadata` (hypothetical)
- `_task_generate_toc` (hypothetical)
- `_task_generate_breadcrumbs` (hypothetical)

### group_* (Categorize)
- `_task_group_relationships` (hypothetical)
- `_task_group_by_severity` (hypothetical)
- `_task_group_by_type` (hypothetical)

### transform_* (Convert Format)
- `_task_transform_faq` (hypothetical)
- `_task_transform_nested_lists` (hypothetical)
- `_task_transform_to_collapsible` (hypothetical)

---

## Summary

**Use this guide when**:
- Creating new task methods
- Reviewing task method pull requests
- Refactoring existing tasks
- Documenting task functionality

**Key Principles**:
1. Action verbs come from controlled vocabulary
2. Targets are specific and clear
3. Docstrings explain action classification
4. One action per task (single responsibility)
5. Consistency over creativity

**Benefits**:
- ✅ Predictable naming across codebase
- ✅ Clear action-target relationship
- ✅ Easy to find similar tasks
- ✅ Reduced cognitive load
- ✅ Better code review discussions

---

## See Also

- `docs/08-development/NAMING_CONVENTIONS_STANDARDIZATION_JAN3_2026.md` - Complete naming proposal
- `export/generation/universal_content_generator.py` - Implementation examples
- `.github/copilot-instructions.md` - Simplify Naming policy
