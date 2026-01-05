# Build-Time Policy Violation Fix Plan
**Date**: January 5, 2026  
**Status**: 🚨 VIOLATION CONFIRMED - Phased Fix Approved

---

## 🚨 Violation Summary

**Core Principle 0.6 Violated**: "ALL data enhancement (structure, metadata, relationships) MUST happen during generation, NOT at build/export time."

**Current Behavior** (VIOLATES POLICY):
```
Generation → Simple Format → Materials.yaml
                              ↓
Export → Transforms to Collapsible → Frontmatter
         ❌ VIOLATION: Adding structure at export time
```

**Required Behavior** (COMPLIANT):
```
Generation → Collapsible Format → Materials.yaml
                                   ↓
Export → Just Reads & Formats → Frontmatter
         ✅ COMPLIANT: No structure creation
```

---

## 📊 Impact Analysis

### Affected Data

| Domain | Field | Items | Status |
|--------|-------|-------|--------|
| Materials | `operational.industry_applications` | 153 | ❌ List → needs collapsible |
| Materials | `operational.expert_answers` | 153 | ❌ FAQ → needs collapsible |
| Materials | `safety.regulatory_standards` | 153 | ❌ Card → needs collapsible |
| Compounds | `operational.expert_answers` | 34 | ❌ FAQ → needs collapsible |
| Contaminants | `safety.regulatory_standards` | 98 | ❌ Card → needs collapsible |

**Total**: 591 fields across 438 items need format conversion

---

## ✅ APPROVED SOLUTION: Option C (Hybrid Approach)

### Phase 1: Document Current State (IMMEDIATE)
**Timeline**: 15 minutes  
**Action**: Create policy exception document

1. Add grandfather clause to Core Principle 0.6:
   ```markdown
   **GRANDFATHER CLAUSE** (Jan 5, 2026):
   - Existing data (pre-Jan 5, 2026) may use build-time normalization tasks
   - Tasks affected: normalize_applications, normalize_expert_answers, normalize_safety_standards
   - Reason: 591 fields across 438 items - regeneration not feasible
   - Migration: New content MUST use collapsible format at generation time
   ```

2. Update `.github/copilot-instructions.md` with exception
3. Create `docs/TECHNICAL_DEBT_BUILD_TIME_NORMALIZATION.md`

### Phase 2: Fix Going Forward (1 HOUR)
**Timeline**: 1 hour  
**Action**: Update generation to output collapsible format for NEW content

#### Changes Required:

**1. Update DomainAdapter.write_component()** (`generation/core/adapters/domain_adapter.py`)
```python
def write_component(self, identifier: str, component_type: str, content: Any):
    """
    Write component to source YAML in final presentation format.
    
    For collapsible components (applications, expert_answers, regulatory_standards),
    content MUST be in collapsible format with title/content/metadata/_display.
    """
    # Map component types to collapsible format
    COLLAPSIBLE_COMPONENTS = {
        'industry_applications': {
            'target_field': 'operational.industry_applications',
            'format': 'collapsible'
        },
        'faq': {
            'target_field': 'operational.expert_answers',
            'format': 'collapsible'
        },
        'regulatory_standards': {
            'target_field': 'safety.regulatory_standards',
            'format': 'collapsible'
        }
    }
    
    if component_type in COLLAPSIBLE_COMPONENTS:
        # Convert to collapsible format BEFORE saving
        content = self._convert_to_collapsible(content, component_type)
    
    # Save to source YAML
    # ... existing save logic
```

**2. Add Collapsible Conversion Method**
```python
def _convert_to_collapsible(self, content: Any, component_type: str) -> Dict:
    """
    Convert component content to unified collapsible structure.
    
    Returns:
    {
        'presentation': 'collapsible',
        'items': [
            {
                'title': 'Display text when collapsed',
                'content': 'Full text when expanded',
                'metadata': {domain-specific fields},
                '_display': {'_open': bool, 'order': int}
            }
        ]
    }
    """
    if component_type == 'faq':
        # Convert FAQ list to collapsible
        items = []
        for idx, faq in enumerate(content):
            items.append({
                'title': faq['question'],
                'content': faq['answer'],
                'metadata': {
                    'category': 'Technical',
                    'difficulty': 'intermediate'
                },
                '_display': {
                    '_open': idx == 0,  # First item open
                    'order': idx + 1
                }
            })
        return {'presentation': 'collapsible', 'items': items}
    
    # ... similar logic for applications, regulatory_standards
```

**3. Update Generation Scripts**
- `scripts/research/populate_compound_gaps.py`: Save FAQ as collapsible
- Any backfill scripts: Update to collapsible format

#### Testing:
```bash
# Test with ONE material
python3 run.py --material "Alabaster" --faq

# Verify Materials.yaml has collapsible structure
python3 -c "
import yaml
with open('data/materials/Materials.yaml') as f:
    data = yaml.safe_load(f)
    
faq = data['materials']['alabaster-laser-cleaning']['operational'].get('expert_answers')
print('✅ Collapsible format' if isinstance(faq, dict) and 'presentation' in faq else '❌ Old format')
"

# Export and verify no transformation happens
python3 run.py --export --domain materials --limit 1
```

### Phase 3: Gradual Migration (ONGOING)
**Timeline**: Natural attrition  
**Action**: Migrate as content is regenerated

1. **Priority 1**: New materials/compounds/contaminants
   - All new generation uses collapsible format
   - Verified at creation time

2. **Priority 2**: Content updates
   - When FAQ regenerated → saves collapsible
   - When applications updated → saves collapsible
   - When standards updated → saves collapsible

3. **Priority 3**: Bulk migration (optional, future)
   - If/when needed, run one-time conversion script
   - Not required - natural migration acceptable

---

## 📝 Documentation Updates Required

### 1. Core Principle 0.6 Amendment
**File**: `.github/copilot-instructions.md`

Add after existing principle:
```markdown
### **GRANDFATHER CLAUSE** (January 5, 2026)

Existing data created before January 5, 2026 uses build-time normalization:
- **Tasks**: normalize_applications, normalize_expert_answers, normalize_safety_standards
- **Scope**: 591 fields across 438 items (153 materials, 34 compounds, 98 contaminants)
- **Reason**: Regeneration not feasible; export transformations are read-only format conversions
- **NEW CONTENT**: Must use collapsible format at generation time (MANDATORY)

**Migration Strategy**:
- ✅ Keep normalization tasks for pre-Jan 5 data
- ✅ Update generation to output collapsible format for new content
- ✅ Natural migration as content regenerated
- ❌ Bulk regeneration not required
```

### 2. Technical Debt Document
**File**: `docs/TECHNICAL_DEBT_BUILD_TIME_NORMALIZATION.md`

```markdown
# Technical Debt: Build-Time Normalization Tasks

**Created**: January 5, 2026  
**Type**: Architecture compliance  
**Severity**: Medium (documented exception)

## Issue

Three export tasks violate Core Principle 0.6 by adding structure during build time:
- `normalize_applications`: Converts list → collapsible
- `normalize_expert_answers`: Converts FAQ → collapsible
- `normalize_safety_standards`: Converts card → collapsible

## Scope

- 591 fields across 438 items
- Pre-existing data (created before Jan 5, 2026)

## Resolution

**Approved**: Grandfather clause exception
- Tasks remain active for existing data
- New generation outputs collapsible format
- Natural migration over time

## Compliance

- ✅ Documented exception
- ✅ Fix-going-forward implemented
- ✅ No new violations permitted
```

### 3. Export Task Documentation
**File**: `export/generation/universal_content_generator.py` (docstrings)

Add to each normalization task:
```python
def _task_normalize_applications(...):
    """
    GRANDFATHER CLAUSE (Jan 5, 2026):
    This task transforms existing pre-Jan 5 data.
    NEW content generated after Jan 5, 2026 should already be in collapsible format.
    
    ... rest of docstring
    """
```

---

## ✅ Success Criteria

### Phase 1 (Immediate):
- [ ] Grandfather clause added to copilot-instructions.md
- [ ] Technical debt document created
- [ ] Export task docstrings updated

### Phase 2 (1 hour):
- [ ] `_convert_to_collapsible()` method implemented
- [ ] `write_component()` updated to use conversion
- [ ] Test material generated with collapsible format
- [ ] Export verified to skip transformation for new data

### Phase 3 (Ongoing):
- [ ] All new materials use collapsible format
- [ ] All regenerated content uses collapsible format
- [ ] Migration tracking added to technical debt doc

---

## 🎯 APPROVED BY: User (Jan 5, 2026)
**Status**: Proceed with Option C (Hybrid Approach)

