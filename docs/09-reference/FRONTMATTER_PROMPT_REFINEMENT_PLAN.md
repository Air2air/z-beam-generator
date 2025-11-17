# Frontmatter Prompt Refinement Plan
**Created:** October 2, 2025  
**Priority:** Medium  
**Status:** Planning Phase  
**Estimated Effort:** 4-6 hours  

---

## 🎯 **Objective**

Refine the frontmatter generator prompts to produce richer, more comprehensive application data while maintaining the structured format and increasing application counts from 6-7 to the target range of 8-10 applications per material.

---

## 📊 **Current State Analysis**

### **What's Working ✅**
- Generation completes successfully for all materials
- Image paths are correct (`/images/material/` format)
- Material properties are comprehensive (12-16 properties per material)
- Tag integration works (4-10 tag range enforced)
- Pipeline validation functioning

### **What Needs Improvement ⚠️**

#### **1. Application Count Issues**
- **Current:** 46.3% of materials have <8 applications
- **Target:** 90%+ materials with 8-10 applications
- **Problem:** Regeneration doesn't increase application count significantly
  - Alabaster: 6 apps → 7 apps (expected 8-9)
  - Limestone: 6 apps → 6 apps (no improvement)

#### **2. Application Format Regression**
**Before Regeneration:**
```yaml
applications:
  - industry: "Aerospace"
    description: "Removal of protective coatings and oxidation from titanium components"
    cleaningTypes: ["Coating Removal", "Oxidation Removal"]
    contaminantTypes: ["Protective Coatings", "Oxidation"]
```

**After Regeneration:**
```yaml
applications:
  - 'Restoration: Gentle cleaning for restoration and conservation applications'
  - 'Jewelry: Precision cleaning and polishing of precious metal jewelry'
```

**Issue:** Lost structured format with industry/description/cleaningTypes/contaminantTypes

#### **3. Missing Data Richness**
- No `cleaningTypes` array
- No `contaminantTypes` array  
- No industry-specific details
- Simplified descriptions

---

## 🔍 **Root Cause Analysis**

### **Prompt Structure Issues**

1. **Location to Check:**
   - `components/frontmatter/generators/` (if exists)
   - `components/frontmatter/prompt.yaml` (if exists)
   - Generator code in `components/frontmatter/`

2. **Suspected Issues:**
   - Prompt may not explicitly request structured application format
   - Missing guidance on minimum application count (8-10)
   - No examples showing the structured format
   - Prompt may not reference Categories.yaml application types
   - Temperature/token settings may be limiting output

3. **API Configuration:**
   ```python
   "frontmatter": {
       "max_tokens": 4000,
       "temperature": 0.3,
   }
   ```
   - Temperature 0.3 is good (conservative)
   - 4000 tokens should be sufficient
   - Need to verify actual token usage

---

## 🛠️ **Refinement Tasks**

### **Phase 1: Investigation** (1-2 hours)

#### **Task 1.1: Locate Prompt Files**
```bash
# Find all frontmatter-related prompts
find components/frontmatter -name "*.yaml" -o -name "*prompt*"
find components/frontmatter -name "*.py" | xargs grep -l "prompt\|system_prompt"
```

**Deliverable:** Document current prompt structure and location

#### **Task 1.2: Analyze Current Prompts**
- [ ] Review system prompts
- [ ] Review user prompts
- [ ] Check for structured format examples
- [ ] Verify Categories.yaml integration
- [ ] Check application count guidance

**Deliverable:** Current prompt analysis document

#### **Task 1.3: Review Token Usage**
```python
# Add logging to track actual token usage
# Check if we're hitting 4000 token limit
# Analyze if applications section gets truncated
```

**Deliverable:** Token usage report

---

### **Phase 2: Prompt Enhancement** (2-3 hours)

#### **Task 2.1: Update Application Structure Guidance**

**Add Explicit Structure Requirements:**
```yaml
# Example prompt addition
application_format:
  required_fields:
    - industry: "Industry sector name"
    - description: "Detailed cleaning application description"
    - cleaningTypes: ["Type 1", "Type 2"]
    - contaminantTypes: ["Contaminant 1", "Contaminant 2"]
  
  count_requirements:
    minimum: 8
    target: 10
    focus: "Diverse industries and use cases"
```

#### **Task 2.2: Add Structured Examples**

**Include 2-3 Complete Examples:**
```yaml
example_applications:
  - industry: "Automotive"
    description: "Removal of rust, paint, and protective coatings from vehicle frames and body panels during restoration and manufacturing processes"
    cleaningTypes: 
      - "Rust Removal"
      - "Paint Stripping"
      - "Coating Removal"
    contaminantTypes:
      - "Rust"
      - "Paint"
      - "Protective Coatings"
      - "Manufacturing Residues"
```

#### **Task 2.3: Integrate Categories.yaml Application Types**

**Reference Existing Data:**
```python
# Load applicationTypeDefinitions from Categories.yaml
# Include relevant types in prompt
# Guide AI to use standard terminology
```

**From Categories.yaml:**
- Coating Removal
- Oxide Removal  
- Rust Removal
- Grease/Oil Removal
- Paint Stripping
- Carbon Deposit Removal
- Biological Growth Removal
- etc.

#### **Task 2.4: Add Diversity Requirements**

**Prompt Addition:**
```text
Application Diversity Requirements:
1. Cover at least 5 different industry sectors
2. Include at least 3 different cleaning types per application
3. Specify 2-4 contaminant types per application
4. Vary descriptions - avoid repetition
5. Include both common and specialized applications
6. Reference material-specific use cases from Materials.yaml
```

#### **Task 2.5: Add Validation Instructions**

**Prompt Addition:**
```text
Before finalizing, verify:
- Minimum 8 applications provided
- All applications have: industry, description, cleaningTypes, contaminantTypes
- No duplicate industries
- Descriptions are detailed (30+ words each)
- cleaningTypes and contaminantTypes are relevant to the material
```

---

### **Phase 3: Implementation** (1 hour)

#### **Task 3.1: Update Prompt Files**
- [ ] Backup current prompts
- [ ] Apply enhancements
- [ ] Test with 3-5 materials
- [ ] Compare output quality

#### **Task 3.2: Adjust API Settings** (if needed)
```python
"frontmatter": {
    "max_tokens": 5000,  # Increase if applications getting truncated
    "temperature": 0.3,   # Keep conservative
}
```

#### **Task 3.3: Update Pipeline Validation**

**Enhance `pipeline_integration.py`:**
```python
def validate_and_improve_frontmatter(material_name: str, frontmatter_content: dict) -> dict:
    # Check application structure
    if 'applications' in frontmatter_content:
        apps = frontmatter_content['applications']
        if isinstance(apps, list):
            for app in apps:
                if isinstance(app, str):
                    issues_detected.append("Applications should be structured objects, not strings")
                    break
                if isinstance(app, dict):
                    required_fields = ['industry', 'description', 'cleaningTypes', 'contaminantTypes']
                    missing = [f for f in required_fields if f not in app]
                    if missing:
                        issues_detected.append(f"Application missing fields: {missing}")
```

---

### **Phase 4: Testing & Validation** (1 hour)

#### **Task 4.1: Test with Problem Materials**

**Materials to Test (currently have 6-7 apps):**
- Alabaster
- Bluestone
- Limestone
- Marble
- Onyx
- Plaster
- Quartz Glass
- Quartzite
- Sandstone
- Schist

**Success Criteria:**
- [ ] All test materials have 8-10 applications
- [ ] All applications have structured format
- [ ] Industry diversity (5+ different industries)
- [ ] No string-based applications
- [ ] Descriptions are detailed (30+ words)

#### **Task 4.2: Batch Test**

**Run subset regeneration:**
```bash
# Test 20 materials with refined prompts
python3 scripts/test_frontmatter_prompts.py --materials 20
```

**Validation Checks:**
- [ ] Application count distribution
- [ ] Format consistency
- [ ] Data richness maintained
- [ ] No regressions

#### **Task 4.3: Quality Comparison**

**Metrics to Track:**
```python
metrics = {
    "application_count": {
        "before": 6.8,  # Average
        "after": 9.2,   # Target
        "improvement": "+35%"
    },
    "structured_format": {
        "before": "100%",
        "after": "100%",
        "status": "maintained"
    },
    "avg_description_length": {
        "before": "45 words",
        "after": "52 words",
        "improvement": "+16%"
    }
}
```

---

## 📋 **Implementation Checklist**

### **Pre-Implementation**
- [ ] Review current prompt files
- [ ] Document current application format
- [ ] Backup existing prompts
- [ ] Create test materials list
- [ ] Set success criteria

### **Implementation**
- [ ] Update system prompts with structure requirements
- [ ] Add structured examples (2-3 complete applications)
- [ ] Integrate Categories.yaml application types
- [ ] Add diversity requirements
- [ ] Add validation instructions
- [ ] Update API token limits if needed
- [ ] Enhance pipeline validation

### **Testing**
- [ ] Test with 5 problem materials
- [ ] Verify structured format maintained
- [ ] Check application counts (8-10 target)
- [ ] Validate industry diversity
- [ ] Run batch test (20 materials)
- [ ] Compare before/after metrics

### **Deployment**
- [ ] Document changes
- [ ] Update PIPELINE_IMPROVEMENTS_ANALYSIS.md
- [ ] Commit prompt changes
- [ ] Run full regeneration (121 materials)
- [ ] Deploy to production
- [ ] Monitor results

---

## 🎯 **Expected Outcomes**

### **Quantitative Improvements**
| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| Avg Applications | 6.8 | 9.2 | +35% |
| Materials with 8+ apps | 53.7% | 90%+ | +36.3pp |
| Materials with <8 apps | 46.3% | <10% | -36.3pp |
| Structured Format | 100% | 100% | Maintained |

### **Qualitative Improvements**
- ✅ Richer application descriptions
- ✅ Better industry diversity (5+ industries per material)
- ✅ Standardized cleaning types from Categories.yaml
- ✅ Detailed contaminant specifications
- ✅ Material-specific use cases
- ✅ Professional, detailed descriptions

---

## 💰 **Cost Estimate**

### **Development Time**
- Investigation: 1-2 hours
- Enhancement: 2-3 hours
- Implementation: 1 hour
- Testing: 1 hour
- **Total:** 5-7 hours

### **Regeneration Cost**
- Test run (20 materials): ~$0.03
- Full run (121 materials): ~$0.20
- **Total API Cost:** ~$0.25

---

## 🚀 **Next Steps**

### **Immediate Actions**
1. Schedule prompt refinement session (5-7 hours)
2. Assign developer/researcher
3. Create test environment
4. Set success metrics

### **Sequence**
1. **Week 1:** Investigation + Enhancement (Tasks 1-2)
2. **Week 2:** Implementation + Testing (Tasks 3-4)
3. **Week 3:** Full regeneration + Deployment

### **Dependencies**
- ✅ Pipeline integration fixed (completed)
- ✅ Tag system optimized (completed)
- ✅ Image paths verified (completed)
- ⏳ Prompt files located and documented
- ⏳ Test environment prepared

---

## 📚 **Resources**

### **Files to Review**
```
components/frontmatter/
├── generators/
│   └── generator.py (main generator logic)
├── prompts/ (if exists)
│   └── system_prompt.yaml
│   └── user_prompt.yaml
├── examples/ (if exists)
└── README.md
```

### **Reference Documents**
- `data/Categories.yaml` - Application type definitions
- `data/Materials.yaml` - Material-specific data
- `PIPELINE_IMPROVEMENTS_ANALYSIS.md` - Current state analysis
- `components/tags/README.md` - Example of good component documentation

### **Tools**
```bash
# Test prompt changes
python3 run.py --material "Test" --components frontmatter --test

# Compare outputs
diff old_alabaster.yaml new_alabaster.yaml

# Batch validation
python3 scripts/validation/validate_frontmatter_structure.py
```

---

## ⚠️ **Risk Mitigation**

### **Potential Risks**
1. **Token limit exceeded** → Increase max_tokens to 5000
2. **Format regression** → Add strict validation in pipeline
3. **Cost overrun** → Test with 20 materials first
4. **Time overrun** → Prioritize high-impact materials first

### **Rollback Plan**
```bash
# If refinement fails, rollback to current state
git checkout main components/frontmatter/prompts/
python3 run.py --deploy  # Deploy current stable version
```

---

## 📊 **Success Metrics**

### **Must Have** ✅
- [ ] 90%+ materials with 8+ applications
- [ ] 100% structured format (no string-based applications)
- [ ] All applications have industry/description/cleaningTypes/contaminantTypes
- [ ] No regressions in existing data quality

### **Should Have** 🎯
- [ ] 5+ different industries per material
- [ ] 30+ word descriptions
- [ ] 3+ cleaning types per application
- [ ] 2-4 contaminant types per application

### **Nice to Have** ⭐
- [ ] Material-specific use cases referenced
- [ ] Industry-standard terminology used
- [ ] Cross-references to Materials.yaml properties

---

## 📝 **Notes**

- This is a refinement task, not a critical fix
- Current system is stable and production-ready
- Focus on quality improvement, not emergency fixes
- Test thoroughly before full deployment
- Document all changes for future reference

---

**Status:** Ready for implementation when scheduled  
**Owner:** TBD  
**Reviewer:** TBD  
**Target Completion:** TBD
