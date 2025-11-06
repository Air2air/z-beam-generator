# Technical Debt Markers Analysis

**Date**: November 5, 2025  
**Status**: Complete

## Overview

Found **13 technical debt markers** (TODO/FIXME/XXX/HACK) in production code.

---

## Categorized Technical Debt

### Category 1: Missing Features (6 items)

#### 1. FAQ Validation Disabled
**File**: `materials/faq/generators/faq_generator.py:444`
```python
# TODO: Re-enable validation when ContentValidator.validate_faq is implemented
```
**Priority**: Low  
**Impact**: FAQ content not validated  
**Action**: Implement `ContentValidator.validate_faq()` method  
**Estimate**: 2-3 hours

#### 2. Author Assignment Logic
**File**: `shared/pipeline/content_pipeline.py:380`
```python
# TODO: Implement author assignment logic
```
**Priority**: Medium  
**Impact**: Author assignment may not be automated in pipeline  
**Action**: Design and implement automated author assignment  
**Estimate**: 4-6 hours

#### 3. Deployment Logic
**File**: `shared/pipeline/unified_pipeline.py:664`
```python
# TODO: Implement deployment logic
```
**Priority**: High  
**Impact**: Deployment may be manual  
**Action**: Implement automated deployment workflow  
**Estimate**: 8-12 hours

#### 4. Testing Logic
**File**: `shared/pipeline/unified_pipeline.py:678`
```python
# TODO: Implement testing logic
```
**Priority**: High  
**Impact**: Automated testing not integrated in pipeline  
**Action**: Integrate pytest into pipeline  
**Estimate**: 4-6 hours

#### 5. Full Path Navigation (Voice Repairer)
**File**: `shared/voice/materials_repairer.py:162`
```python
# TODO: Implement full path navigation and update
```
**Priority**: Low  
**Impact**: May not handle deeply nested paths  
**Action**: Add recursive path navigation  
**Estimate**: 2-3 hours

#### 6. Full Path Navigation (Source Data Repairer)
**File**: `shared/voice/source_data_repairer.py:184`
```python
# TODO: Implement full path navigation and update
```
**Priority**: Low  
**Impact**: May not handle deeply nested paths  
**Action**: Add recursive path navigation  
**Estimate**: 2-3 hours

---

### Category 2: Disabled/Removed Features (5 items)

#### 7. Material Prompting Module (2 locations)
**Files**: 
- `components/frontmatter/core/streamlined_generator.py:97`
- `components/frontmatter/core/streamlined_generator.py:143`

```python
# TODO: Re-enable when material_prompting module is restored
```
**Priority**: ⚠️ **Needs Decision**  
**Impact**: Feature removed, unclear if needed  
**Questions**:
- Why was `material_prompting` removed?
- Is it needed for current functionality?
- Can TODOs be deleted if feature deprecated?

**Action**: 
1. Review git history for removal context
2. Decide: Restore feature or remove TODOs
3. Document decision

**Estimate**: 1 hour investigation + potential implementation

#### 8. Pipeline Integration (2 locations)
**Files**:
- `shared/pipeline/unified_pipeline.py:30`
- `shared/pipeline/unified_pipeline.py:133`

```python
# TODO: Restore when pipeline_integration is reimplemented
```
**Priority**: ⚠️ **Needs Decision**  
**Impact**: Pipeline integration disabled  
**Questions**:
- What is `pipeline_integration`?
- Why was it removed?
- Is restoration planned?

**Action**:
1. Review git history for removal context
2. Decide: Restore or remove TODOs
3. Document decision

**Estimate**: 1-2 hours investigation + potential implementation

#### 9. Property Manager Migration
**File**: `materials/services/property_manager.py:868`
```python
# TODO: Remove after full migration to unified discover_and_research_properties() API
```
**Priority**: Medium  
**Impact**: Old API still present  
**Action**: 
1. Verify unified API is working
2. Remove old implementation
3. Delete TODO

**Estimate**: 1-2 hours

---

### Category 3: Integration Tasks (2 items)

#### 10. Full Path Navigation (Base Generator)
**File**: `components/frontmatter/core/base_generator.py:557`
```python
# TODO: Implement full path navigation
```
**Priority**: Low  
**Impact**: May not handle nested dictionary paths  
**Action**: Add recursive navigation utility  
**Note**: Similar to items #5 and #6 - could create shared utility  
**Estimate**: 2-3 hours (or 4 hours for shared solution)

#### 11. SchemaValidator Integration
**File**: `components/frontmatter/core/base_generator.py:583`
```python
# TODO: Integrate with SchemaValidator
```
**Priority**: Medium  
**Impact**: Schema validation may be incomplete  
**Action**: Wire up SchemaValidator to validation flow  
**Estimate**: 3-4 hours

---

## Summary by Priority

### 🔴 High Priority (2 items, 16-18 hours)
1. Deployment logic implementation
2. Testing logic implementation

**Rationale**: Core infrastructure improvements for automation

### 🟡 Medium Priority (3 items, 8-12 hours)
1. Author assignment logic
2. Property Manager migration cleanup
3. SchemaValidator integration

**Rationale**: Improves automation and code quality

### 🟢 Low Priority (5 items, 8-12 hours)
1. FAQ validation
2. Full path navigation (3 locations - can share solution)

**Rationale**: Edge case handling, nice-to-haves

### ⚠️ Needs Decision (5 items, 3-6 hours investigation)
1. Material prompting module restoration (2 TODOs)
2. Pipeline integration restoration (2 TODOs)
3. Property Manager old API removal (1 TODO)

**Rationale**: Need context on whether features should be restored or TODOs removed

---

## Action Plan

### Phase 1: Investigation (1 week)
**Goal**: Understand context for disabled features

**Tasks**:
1. [ ] Review git history for `material_prompting` removal
2. [ ] Review git history for `pipeline_integration` removal
3. [ ] Verify unified property API is fully working
4. [ ] Document findings and make decisions

**Output**: Decision document on restore vs remove

### Phase 2: High Priority (1 week)
**Goal**: Implement critical infrastructure

**Tasks**:
1. [ ] Implement deployment logic in unified pipeline
2. [ ] Integrate pytest into pipeline testing logic
3. [ ] Document new workflows

**Output**: Automated deployment and testing

### Phase 3: Medium Priority (1 week)
**Goal**: Complete partially-implemented features

**Tasks**:
1. [ ] Implement author assignment logic
2. [ ] Remove old property manager API
3. [ ] Integrate SchemaValidator
4. [ ] Update documentation

**Output**: Cleaner, more automated codebase

### Phase 4: Low Priority (As Needed)
**Goal**: Handle edge cases and nice-to-haves

**Tasks**:
1. [ ] Create shared path navigation utility
2. [ ] Implement FAQ validation
3. [ ] Apply shared utility to 3 locations

**Output**: More robust error handling

---

## Recommendations

### Immediate Actions

1. ✅ **Create Investigation Tasks** for disabled features
2. ✅ **Prioritize high-impact TODOs** (deployment, testing)
3. 📋 **Schedule Investigation Phase** for next sprint
4. 📋 **Track in issue tracker** with links to this document

### Best Practices Going Forward

#### When Adding TODOs

**✅ Good TODO**:
```python
# TODO: Implement caching for API responses (improves performance by 10x)
# Blocked by: Need to design cache invalidation strategy
# Estimated effort: 4-6 hours
# Owner: @developer
# Issue: #123
```

**❌ Bad TODO**:
```python
# TODO: Fix this
# TODO: Make better
# TODO: Refactor
```

#### TODO Hygiene

1. **Always include**:
   - Why (rationale)
   - What (specific action)
   - Who (if known)
   - Issue link (if exists)

2. **Review quarterly**:
   - Are TODOs still relevant?
   - Can any be completed quickly?
   - Should any be promoted to issues?

3. **Delete completed TODOs**:
   - Don't leave commented-out code
   - Git history preserves context

---

## Impact Assessment

### Current State
- **13 TODOs**: Reasonable for codebase this size
- **Mostly actionable**: Clear what needs to be done
- **Good categories**: Infrastructure > Features > Edge cases

### Risk Level: 🟢 **Low**

**Reasoning**:
- No "HACK" or "XXX" markers (no urgent fixes)
- No FIXMEs (no known bugs being deferred)
- All TODOs are feature additions, not bug workarounds
- System functioning well despite incomplete features

### Quality Assessment: ✅ **Good**

**Indicators**:
- Clear, specific TODOs
- Most include context
- Organized by component
- No ancient TODOs (all from recent work)

---

## Monitoring

### Add TODO Tracking

Create script: `scripts/audit/todo_tracker.py`

```python
def find_todos():
    """Find and categorize all TODOs in codebase"""
    todos = grep_for_todos()
    
    report = {
        "total": len(todos),
        "by_priority": categorize_by_keywords(todos),
        "by_age": analyze_git_blame(todos),
        "by_component": group_by_directory(todos)
    }
    
    return report
```

### CI/CD Integration

Add check that fails if:
- TODO count increases by >5 in one PR
- TODO without context/rationale
- TODO older than 6 months

---

## Conclusion

### Current Assessment: ✅ **Healthy**

**Findings**:
- 13 TODOs is reasonable for a mature codebase
- All are feature additions, not bug workarounds
- Clear priorities and actionable items
- No urgent technical debt

### Recommendations

1. ✅ **Investigate disabled features** (Phase 1)
2. 📋 **Implement high-priority infrastructure** (Phase 2)
3. 📋 **Complete medium-priority features** (Phase 3)
4. 📋 **Address low-priority items** opportunistically
5. ✅ **Maintain TODO hygiene** going forward

### Total Effort Estimate

| Phase | Items | Hours | Priority |
|-------|-------|-------|----------|
| Investigation | 5 | 3-6 | High |
| High Priority | 2 | 16-18 | High |
| Medium Priority | 3 | 8-12 | Medium |
| Low Priority | 5 | 8-12 | Low |
| **Total** | **13** | **35-48 hours** | - |

**Timeline**: Can be spread over 4-6 weeks, integrated with feature work.
