# Materials.yaml Field Normalization - Action Plan

**Date**: October 25, 2025  
**Status**: Ready to Execute  
**Priority**: HIGH - Required before frontmatter regeneration

---

## Issues Discovered

### 1. Caption Structure Inconsistency ⚠️ CRITICAL

**Problem**: 7 materials use legacy `ai_text_fields.caption_*` structure instead of modern `caption` structure

**Materials Affected**:
1. Aluminum
2. Brass  
3. Copper
4. Gold
5. Nickel
6. Platinum
7. Silver

**Current Legacy Structure**:
```yaml
Aluminum:
  ai_text_fields:
    caption_beforeText:
      content: "Text..."
      generated: "..."
      method: "ai_research"
    caption_afterText:
      content: "Text..."
```

**Required Modern Structure**:
```yaml
Aluminum:
  caption:
    beforeText: "Text..."
    afterText: "Text..."
    author: "Author Name"
    generated: "2025-10-25T..."
    generation_method: "ai_research"
    word_count:
      before: 25
      after: 33
    character_count:
      before: 199
      after: 245
```

**Impact**: 
- Inconsistent data structure makes processing complex
- Frontmatter generator has special handling for both structures
- Caption regeneration populated modern structure, but legacy fields still exist

**Solution**: Migrate 7 materials from legacy → modern structure, remove `ai_text_fields.caption_*`

---

### 2. Applications Field Mapping ✅ VERIFIED

**Status**: All 132 materials have `applications` field in Materials.yaml

**Current**: Applications exist but NOT mapped to frontmatter files

**Required**: Add `applications` field to frontmatter generation

**Example**:
```yaml
# Materials.yaml
Brick:
  applications:
    - Cultural Heritage
    - Construction and Restoration
    - Industrial Manufacturing
    
# Should map to frontmatter:
applications:
  - Cultural Heritage
  - Construction and Restoration  
  - Industrial Manufacturing
```

---

### 3. Text Fields for Author Voice

**Currently Using Author Voice**:
1. ✅ `caption.beforeText` - Microscopic before description
2. ✅ `caption.afterText` - Microscopic after description

**Candidates for Future Voice Integration**:
3. `environmentalImpact[].description` - Environmental benefit descriptions (template text)
4. `outcomeMetrics[].description` - Outcome metric descriptions (template text)
5. FAQ answers (NEW component - not yet created)

**NOT Suitable for Voice** (Technical/Data):
- `properties.*.description` - Technical specifications
- `machineSettings.*.description` - Parameter descriptions
- `category_info.description` - Category definitions

---

## Action Plan

### Phase 1: Normalize Materials.yaml Structure (IMMEDIATE)

#### Task 1.1: Migrate Legacy Caption Structure
**Priority**: CRITICAL  
**Affected**: 7 materials  
**Estimated Time**: 5 minutes

**Steps**:
1. Read Materials.yaml
2. For each of 7 materials with `ai_text_fields.caption_*`:
   - Extract content from `caption_beforeText.content` → `caption.beforeText`
   - Extract content from `caption_afterText.content` → `caption.afterText`
   - Copy metadata (author, generated, etc.) from existing `caption` section if present
   - Remove `ai_text_fields.caption_beforeText` and `caption_afterText`
3. Save Materials.yaml with normalized structure
4. Verify all 132 materials now have consistent `caption` structure

**Script**: Create `scripts/normalize_caption_structure.py`

#### Task 1.2: Remove Escaped Line Breaks (if any)
**Priority**: MEDIUM  
**Estimated Time**: 5 minutes

**Steps**:
1. Search Materials.yaml for `\` escape sequences in text fields
2. Remove unnecessary escapes (line continuations, etc.)
3. Preserve intentional formatting
4. Save cleaned Materials.yaml

**Script**: Create `scripts/remove_yaml_escapes.py`

---

### Phase 2: Update Frontmatter Generator (IMMEDIATE)

#### Task 2.1: Add Applications Field Mapping
**Priority**: HIGH  
**File**: `components/frontmatter/core/streamlined_generator.py`  
**Estimated Time**: 10 minutes

**Change**:
```python
# In _generate_from_yaml() method, add after basic metadata:

# Add applications list
if 'applications' in material_data:
    frontmatter['applications'] = material_data['applications']
    self.logger.info(f"✅ Added {len(material_data['applications'])} applications")
```

#### Task 2.2: Verify Caption Field Mapping
**Priority**: HIGH  
**Status**: Currently working, but verify after normalization

**Current Logic**:
```python
# _get_caption_from_ai_fields() handles BOTH structures
# After normalization, this should ONLY use modern structure
```

**Verification**: 
- Test frontmatter generation after caption normalization
- Ensure caption section appears correctly in all 132 frontmatter files

---

### Phase 3: Frontmatter Regeneration (POST-NORMALIZATION)

#### Task 3.1: Regenerate All 132 Frontmatter Files
**Priority**: HIGH  
**Estimated Time**: 20-30 minutes  
**Prerequisite**: Complete Phase 1 & 2

**Command**:
```bash
python3 run.py --all  # Regenerate all frontmatter
```

**Expected Changes**:
1. ✅ All 132 materials get micro images with enhanced alt text
2. ✅ All 132 materials get applications field
3. ✅ Consistent caption structure across all files
4. ✅ All Materials.yaml fields properly mapped

---

### Phase 4: FAQ Component Design (FUTURE)

#### Task 4.1: Create FAQ Component Specification
**Priority**: MEDIUM  
**Estimated Time**: 2 hours design + 4 hours implementation

**Requirements**:
1. Generate 5-7 material-specific FAQs per material
2. Questions cover:
   - Material properties ("What makes [Material] suitable for laser cleaning?")
   - Laser parameters ("What wavelength works best for [Material]?")
   - Applications ("What industries use laser cleaning for [Material]?")
   - Safety ("Is laser cleaning safe for [Material]?")
   - Performance ("What contaminants can be removed from [Material]?")
3. Answers use author voice (Taiwan, Italy, Indonesia, USA styles)
4. Absolute material specificity - no template text
5. Data sources: machineSettings, properties, applications, outcomeMetrics

**Structure**:
```yaml
faq:
  - question: "What makes Aluminum suitable for laser cleaning?"
    answer: "Aluminum's moderate reflectivity of 36.2% at 1064nm wavelength..."
    category: "Material Properties"
    sources: ["properties.laserReflectivity", "properties.thermalConductivity"]
```

**Components Needed**:
- `components/faq/core/faq_generator.py` - Main generator
- `components/faq/prompts/` - Question templates and answer prompts
- `components/faq/voice/` - Voice integration
- Integration with existing voice transformation system

---

## Execution Order

### Today (October 25, 2025):

1. ✅ **COMPLETE**: Caption regeneration (132/132) ✅
2. ⏳ **NEXT**: Normalize caption structure in Materials.yaml (7 materials)
3. ⏳ **NEXT**: Update frontmatter generator to include applications
4. ⏳ **NEXT**: Regenerate all 132 frontmatter files

### Next Session:

5. ⏳ Design FAQ component architecture
6. ⏳ Implement FAQ generator with voice integration
7. ⏳ Add FAQ field to frontmatter structure

---

## Verification Checklist

### After Phase 1 (Materials.yaml Normalization):
- [ ] All 132 materials have `caption.beforeText` and `caption.afterText`
- [ ] Zero materials have `ai_text_fields.caption_*` fields
- [ ] No escaped line breaks (`\`) in text content
- [ ] All 132 materials have `applications` field

### After Phase 2 (Frontmatter Generator Update):
- [ ] `streamlined_generator.py` includes applications mapping
- [ ] Caption extraction simplified (no legacy structure handling needed)
- [ ] Test generation works for 1 sample material

### After Phase 3 (Frontmatter Regeneration):
- [ ] All 132 frontmatter files have `applications` field
- [ ] All 132 frontmatter files have `images.micro` with enhanced alt text
- [ ] All 132 frontmatter files have consistent `caption` structure
- [ ] No generation errors in logs

---

## Risk Assessment

**LOW RISK**:
- Caption normalization: Well-defined, affects only 7 materials
- Applications mapping: Simple field copy, no transformation needed
- Frontmatter regeneration: Proven process, just ran 132 captions successfully

**MEDIUM RISK**:
- Escaped line breaks: May need manual review if edge cases found

**HIGH RISK**: 
- None identified for current phases

---

## Files to Modify

### Scripts to Create:
1. `scripts/normalize_caption_structure.py` - Migrate 7 materials
2. `scripts/remove_yaml_escapes.py` - Clean escaped characters (if needed)

### Files to Edit:
1. `components/frontmatter/core/streamlined_generator.py` - Add applications mapping
2. `data/Materials.yaml` - Normalize caption structure (automated by script)

### Files to Regenerate:
1. `content/frontmatter/*.yaml` - All 132 frontmatter files

---

## Success Criteria

**Phase 1 Complete** when:
- ✅ All 132 materials use `caption.beforeText/afterText` structure
- ✅ Zero materials use `ai_text_fields.caption_*` structure
- ✅ Materials.yaml validates without errors

**Phase 2 Complete** when:
- ✅ Frontmatter generator includes applications field
- ✅ Test generation produces correct frontmatter structure

**Phase 3 Complete** when:
- ✅ All 132 frontmatter files have micro images
- ✅ All 132 frontmatter files have applications
- ✅ All frontmatter files validate against schema

**Phase 4 Complete** (Future) when:
- ✅ FAQ component generates material-specific questions
- ✅ FAQ answers use author voice transformation
- ✅ All 132 materials have 5-7 FAQs in frontmatter
