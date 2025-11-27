# Prompts Domain Separation Analysis
**Date**: November 26, 2025  
**Question**: "Look for prompts that should be in settings"

---

## 🎯 Executive Summary

**Finding**: `settings_description` prompt is correctly located but **duplicated**.

**Current State**:
- ✅ `prompts/components/settings_description.txt` - Root level (correct for generation)
- ⚠️ `domains/materials/prompts/settings_description.txt` - Domain level (incorrect - settings not materials)
- ❌ `domains/settings/prompts/` - Does NOT exist (settings domain has no prompts folder)

**Issue**: Settings-related prompt exists in **materials domain** instead of **settings domain**.

---

## 📊 Findings

### 1. Settings Description Prompt Locations

| Location | Status | Purpose |
|----------|--------|---------|
| `prompts/components/settings_description.txt` | ✅ CORRECT | Root-level prompt for generation layer |
| `domains/materials/prompts/settings_description.txt` | ❌ WRONG DOMAIN | Should be in settings, not materials |
| `domains/settings/prompts/` | ❌ MISSING | Settings domain has no prompts folder |

### 2. Content Comparison

**Root Prompt** (`prompts/components/settings_description.txt`):
```
You are {author}, writing about special settings and requirements 
for laser cleaning {material}.

CONTENT FOCUS:
- Material's strengths/weaknesses for laser cleaning
- What makes this material DIFFERENT
- PITFALLS to avoid and settings adjustments
- Practical guidance: "Start with lower power to avoid..."
```

**Materials Domain Prompt** (`domains/materials/prompts/settings_description.txt`):
```
You are {author}, writing about {material}.

CONTENT FOCUS:
- PRIMARY physical properties (density, thermal, laser interaction)
- KEY laser cleaning challenges
- CRITICAL parameters for successful cleaning
- Quantitative data with precise measurements
```

**Observation**: Two DIFFERENT prompts with same name but different content!
- Root prompt: Practical operator guidance (settings focus)
- Materials prompt: Technical material properties (materials focus)

---

## 🔍 Analysis

### Issue 1: Prompt Belongs in Wrong Domain

**Current**:
```
domains/materials/prompts/settings_description.txt  # ❌ WRONG
```

**Should Be**:
```
domains/settings/prompts/settings_description.txt   # ✅ CORRECT
```

**Why It's Wrong**:
- Settings domain owns `settings_description` field (stored in Settings.yaml)
- Materials domain should not have settings-related prompts
- Violates domain separation (settings content in materials domain)

---

### Issue 2: Two Different Prompts, Same Name

**Root Prompt Philosophy**: 
- Practical operator guidance
- "How to work with this material"
- Settings adjustments and pitfalls

**Materials Prompt Philosophy**:
- Technical material properties
- Physical characteristics
- Quantitative measurements

**Problem**: Name collision creates confusion about which prompt is used

---

### Issue 3: Settings Domain Has No Prompts Folder

**Current Structure**:
```
domains/settings/
├── __init__.py
├── data_loader.py
├── settings_cache.py
└── modules/
    └── settings_module.py
# NO prompts/ folder
```

**Should Have**:
```
domains/settings/
├── __init__.py
├── data_loader.py
├── settings_cache.py
├── modules/
│   └── settings_module.py
└── prompts/              # NEW
    └── settings_description.txt
```

---

## 🎯 Recommendations

### Option A: Move to Settings Domain ✅ RECOMMENDED

**Actions**:
1. Create `domains/settings/prompts/` directory
2. Move `domains/materials/prompts/settings_description.txt` → `domains/settings/prompts/`
3. Update generation code to look in settings domain for settings prompts
4. Keep root `prompts/components/settings_description.txt` for backward compatibility

**Pros**:
- ✅ Correct domain separation
- ✅ Settings owns settings prompts
- ✅ Clear ownership

**Cons**:
- ⚠️ Requires updating generation layer to look in multiple domains
- ⚠️ More complex prompt loading logic

**Time**: 30 minutes

---

### Option B: Consolidate to Root Only ⚠️ SIMPLER

**Actions**:
1. Delete `domains/materials/prompts/settings_description.txt`
2. Keep only `prompts/components/settings_description.txt`
3. Generation layer uses root prompts only

**Pros**:
- ✅ Simple (one prompt location)
- ✅ Works with current architecture
- ✅ No changes to generation layer

**Cons**:
- ⚠️ Domains don't control their own prompts
- ⚠️ Less clear domain ownership

**Time**: 5 minutes

---

### Option C: Rename Materials Prompt 🤔 CLARIFY

**Actions**:
1. Rename `domains/materials/prompts/settings_description.txt` to `material_properties_description.txt`
2. Update code to use new name
3. Keep root `prompts/components/settings_description.txt` unchanged

**Pros**:
- ✅ Clarifies that materials prompt is about properties, not settings
- ✅ Removes name collision
- ✅ Both prompts can coexist

**Cons**:
- ⚠️ Requires code changes
- ⚠️ Still has settings-related content in materials domain

**Time**: 20 minutes

---

## 📋 Current Usage Analysis

### Where settings_description is Generated

```python
# generation/core/simple_generator.py
if component_type == 'settings_description':
    self._save_to_settings_yaml(material_name, content, component_type)
```

**Saves To**: `data/settings/Settings.yaml`  
**Prompt Used**: `prompts/components/settings_description.txt` (root level)

**Observation**: Generation layer already uses ROOT prompt, not domain prompt!

### Where Domain Prompt is Used

```bash
grep -r "domains/materials/prompts/settings_description" . 2>/dev/null
# Result: NO MATCHES FOUND
```

**Finding**: Domain prompt appears **UNUSED** by generation system!

---

## ✅ Final Recommendation

### Recommended Action: **Option B (Consolidate to Root)**

**Reasoning**:
1. **Domain prompt is unused** - Generation already uses root prompt
2. **Simpler architecture** - One prompt location per component
3. **Zero code changes** - Just delete unused file
4. **Already works** - System uses root prompts correctly

**Action Plan**:
1. Delete `domains/materials/prompts/settings_description.txt` (unused file)
2. Keep `prompts/components/settings_description.txt` (active prompt)
3. Document in settings domain that prompts live at root level

**Rationale**:
- Generation layer is cross-domain (uses orchestrator pattern)
- Prompts are part of generation layer, not domain data
- Root-level prompts serve all domains equally
- Domain-specific prompt folders add complexity without benefit

---

## 💡 Key Insight: Prompts vs Domain Data

**Prompts Are Generation Layer Concern**:
- Used by generation/ code (cross-domain)
- Not domain-specific data
- Serve orchestration, not single domain

**Domain Data Is Domain Concern**:
- Materials.yaml - materials domain
- Settings.yaml - settings domain
- Contaminants.yaml - contaminants domain

**Conclusion**: Prompts belong in **generation layer** (root `prompts/`), not **domain folders**.

---

## 🚫 What NOT to Do

❌ **Don't move root prompt to settings domain**
- Generation layer needs access to all prompts
- Would create cross-domain import for prompts
- Violates domain independence

❌ **Don't create settings/prompts/ folder**
- Adds complexity without benefit
- Prompts are generation layer concern
- Domains should focus on data, not generation

❌ **Don't keep duplicate prompts**
- Confusing which one is used
- Maintenance burden (update both?)
- Current system ignores domain prompt anyway

---

## ✅ Action Items

### Immediate (5 minutes)
- [ ] Delete `domains/materials/prompts/settings_description.txt` (unused)
- [ ] Verify generation still works (uses root prompt)
- [ ] Document prompt location in settings domain README

### Documentation (10 minutes)
- [ ] Add comment in generation code: "Prompts are in root prompts/ folder"
- [ ] Update DOMAIN_INDEPENDENCE_POLICY.md: "Prompts are generation layer, not domain data"
- [ ] Create prompts/README.md explaining architecture

---

## 📊 Summary

| Question | Answer |
|----------|--------|
| Should prompts be in settings domain? | **NO** - Prompts are generation layer concern |
| Is settings_description in wrong place? | **NO** - Root location is correct |
| Should domain prompts exist? | **NO** - Unnecessary complexity |
| What needs to change? | Delete unused domain prompt, document architecture |

**Grade**: Current root-level approach is **CORRECT** (A)

---

**Status**: Analysis complete  
**Recommendation**: Delete unused domain prompt, document that prompts live at root level  
**Time Required**: 15 minutes (5 min cleanup + 10 min documentation)
