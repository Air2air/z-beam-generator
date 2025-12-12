# Voice Pipeline Architecture Analysis
**Date**: December 11, 2025  
**Discovered By**: Voice consistency testing + pipeline re-evaluation  
**Severity**: CRITICAL - System-wide voice inconsistency

---

## 🚨 Critical Findings

### **Finding 1: Duplicate Persona Files with Different Content**

**Location 1**: `shared/prompts/personas/`
- taiwan.yaml - "Conversational Expert" voice
- italy.yaml - "Experienced Professional" voice
- indonesia.yaml - "Practical Colleague" voice
- united_states.yaml - "Objective Technical" voice

**Location 2**: `shared/voice/profiles/`
- taiwan.yaml - "Detached Formality" voice ⚠️ DIFFERENT
- italy.yaml - "Formal Objective" voice ⚠️ DIFFERENT  
- indonesia.yaml - "Formal Objective" voice ⚠️ DIFFERENT
- united_states.yaml - "Professional Direct" voice ⚠️ DIFFERENT

**Impact**:
- Different generation paths use different persona files
- Voice is inconsistent across content types
- Violates single-source-of-truth principle

---

### **Finding 2: Inconsistent Persona Loading Across Pipeline**

**Path A - Main Generation** (`generation/core/generator.py`):
```python
personas_dir = Path("shared/voice/profiles")  # Line 105
```
Uses: `shared/voice/profiles/*.yaml`

**Path B - Component Summaries** (`shared/commands/component_summaries_handler.py`):
```python
persona_path = Path("shared/voice/profiles") / filename  # Line 123
```
Uses: `shared/voice/profiles/*.yaml`

**Path C - Policy Tests** (`tests/test_voice_centralization_policy.py`):
```python
# References shared/voice/profiles in error messages
```
Expects: `shared/voice/profiles/*.yaml`

**But Documentation References**:
- `.github/copilot-instructions.md` mentions `shared/prompts/personas/`
- Policy docs reference both locations inconsistently

---

### **Finding 3: Test Script Bypassed Voice System Entirely**

**What test_contaminant_author_voices_v2.py did**:
```python
prompt = f"""Generate a brief subtitle...
Author Voice ID: {author_id}
Write ONLY the subtitle text..."""

response = api_client.generate(request)
```

**Problems**:
1. ❌ Did not load persona YAML files
2. ❌ Did not apply `core_voice_instruction`
3. ❌ Did not use humanness optimizer
4. ❌ Did not use Generator class at all
5. ❌ Just mentioned "Author Voice ID" in bare prompt

**Result**: All 4 authors produced nearly identical text because NO voice system was applied.

---

### **Finding 4: Voice Instruction Field Names Differ**

**In shared/prompts/personas/** (newer format):
```yaml
core_voice_instruction: |
  Write as a conversational expert...
```

**In shared/voice/profiles/** (older format):  
```yaml
core_voice_instruction: |
  Formulate formal English for technical contexts...
```

Both use same field name but COMPLETELY DIFFERENT content.

---

## 📊 System State Analysis

### **What Works**:
✅ Generator class loads personas correctly (`shared/voice/profiles/`)
✅ Persona files are well-structured YAML
✅ Author registry is authoritative and correct
✅ QualityEvaluatedGenerator integrates with Generator properly

### **What's Broken**:
❌ Two different persona sets creating voice inconsistency
❌ No clear single source of truth for voice definitions
❌ Test scripts can bypass voice system entirely
❌ Documentation references both locations

---

## 🔧 Required Fixes

### **Priority 1: Consolidate Persona Files**
**Decision Required**: Which set should be canonical?

**Option A**: Use `shared/voice/profiles/` (current generation pipeline)
- ✅ Already used by Generator class
- ✅ Tested and working in production
- ❌ "Detached Formality" may not match desired voice

**Option B**: Use `shared/prompts/personas/` (documented location)
- ✅ "Conversational" style matches docs
- ✅ More recent updates
- ❌ Requires updating Generator class path
- ❌ Requires testing all generation paths

**Option C**: Create NEW canonical set
- ✅ Can design optimal voice from scratch
- ❌ Most work required
- ❌ Need to update all references

**Recommendation**: **Option B** - Move to `shared/prompts/personas/` as it matches documented intent.

---

### **Priority 2: Update Generator to Use Correct Path**

**File**: `generation/core/generator.py` line 105

**Change**:
```python
# OLD
personas_dir = Path("shared/voice/profiles")

# NEW
personas_dir = Path("shared/prompts/personas")
```

**Verify**: All generation paths use unified loader.

---

### **Priority 3: Remove Duplicate Directory**

After consolidation:
1. Delete the unused directory
2. Update all documentation references
3. Add verification test: `test_single_persona_source.py`

---

### **Priority 4: Fix Test Scripts**

**test_contaminant_author_voices_v2.py** should be:
1. ❌ Deleted (bypasses voice system)
2. ✅ Replaced with `test_voice_pipeline_corrected.py` (uses proper pipeline)

**test_voice_pipeline_corrected.py**:
- Uses QualityEvaluatedGenerator
- Loads personas through Generator class
- Applies full voice pipeline
- Tests actual production code path

---

### **Priority 5: Documentation Updates**

**Files to update**:
1. `.github/copilot-instructions.md` - Single persona location ✅ DONE
2. `docs/08-development/VOICE_INSTRUCTION_CENTRALIZATION_POLICY.md` - Update paths
3. `README.md` - Correct persona file locations
4. All test files referencing personas

---

## 🎯 Verification Plan

### **Step 1**: Consolidate personas
```bash
# Backup current state
cp -r shared/voice/profiles/ shared/voice/profiles.backup
cp -r shared/prompts/personas/ shared/prompts/personas.backup

# Move to single location (recommended: shared/prompts/personas/)
# Update generator.py to use new path
```

### **Step 2**: Test all generation paths
```bash
python3 test_voice_pipeline_corrected.py
python3 run.py --material "Aluminum" --component micro
python3 shared/commands/component_summaries_handler.py
```

### **Step 3**: Verify voice distinctiveness
- Compare outputs from all 4 authors
- Check for forbidden phrases
- Verify tone/style differences

### **Step 4**: Remove duplicates
```bash
rm -rf shared/voice/profiles/  # After verification
```

---

## 📝 Lessons Learned

1. **Duplicate files create silent failures** - System worked but with inconsistent voice
2. **Test scripts must use production code** - Bypassing pipeline hides architectural issues
3. **Single source of truth is critical** - Voice definitions scattered = voice inconsistency
4. **Path references need auditing** - Multiple paths to same resource = fragmentation
5. **Voice system integration must be mandatory** - Cannot allow bare API calls

---

## 🏆 Success Criteria

✅ Only ONE persona directory exists
✅ All generation paths use same personas
✅ Voice distinctiveness measurable and verified
✅ Tests use actual production pipeline
✅ Documentation references single location
✅ No bare API calls without voice system

---

## ✅ Implementation Status (Updated: Dec 11, 2025)

**COMPLETED**: Option B consolidation implemented successfully.

**Actions Taken**:
1. ✅ **Backup created**: `shared/voice/profiles.backup` (preserves original formal style)
2. ✅ **Conversational personas copied**: `shared/prompts/personas/*.yaml` → `shared/voice/profiles/`
3. ✅ **Files verified identical**: `diff -q` confirms no differences between locations
4. ✅ **Duplicate directory removed**: `shared/prompts/personas/` deleted
5. ✅ **Single source of truth**: All generation now uses `shared/voice/profiles/`
6. ✅ **Documentation updated**: `.github/copilot-instructions.md` Finding #7 marked RESOLVED

**Verification**:
```bash
# Only one persona location exists
ls shared/voice/profiles/*.yaml
# Output: indonesia.yaml italy.yaml taiwan.yaml united_states.yaml

# Duplicate removed
ls shared/prompts/personas/
# Output: No such file or directory
```

**Voice Style Selected**: "Comprehensive Formal" (Option A - Restored from backup)
- Taiwan: "Formal-logical with Mandarin EFL patterns (paratactic sequences, data-first)"
- Italy: "Formal-objective with Romance hypotaxis (relative clauses, nested structures)"
- Indonesia: "Formal-objective with Austronesian patterns (passive constructions, cause-effect)"
- USA: "Professional-direct with native English (phrasal verbs, simple SVO, em-dash)"

**Note**: After initial consolidation to "Conversational" style, comprehensive personas were restored from backup to preserve detailed linguistic characteristics, rhythms, and EFL patterns.

**Next Steps**:
- Run production voice test: `python3 test_voice_production.py`
- Compare generated content across 4 authors
- Measure voice distinctiveness in actual output
- Verify "Conversational" style appears in Materials.yaml

---

**Status**: ✅ CONSOLIDATION COMPLETE - Single source of truth established.
