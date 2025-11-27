# Contamination Data Accuracy Improvement Proposal

**Date**: November 26, 2025  
**Current Accuracy**: 45.3% (237/523 entries reference specific materials)  
**Target Accuracy**: 85%+ (445+/523 entries)

---

## 📊 Current State Analysis

### Coverage
- ✅ **100%** of patterns have `valid_materials` defined
- ✅ **90%** of patterns have `prohibited_materials` defined
- ✅ Average 3.2 valid materials per pattern

### Accuracy Breakdown
- **45.3%** (237) - Specific materials in Materials.yaml ✅
- **37.5%** (196) - Generic category terms ⚠️
- **17.2%** (90) - Materials NOT in Materials.yaml ❌

### Root Causes
1. **Generic Terms**: "Metal", "Plastics", "Glass" (196 occurrences)
2. **Missing Materials**: "Carbon Steel", "Aluminum Alloys", "Tile" (87 occurrences)
3. **Case Mismatches**: Minor issue, easily fixable
4. **Ambiguous References**: "ALL", "Thin Metals", "Soft Metals"

---

## 🎯 Proposed 3-Phase Solution

### **Phase 1: Material Mapping & Expansion** (HIGH PRIORITY)
**Objective**: Eliminate missing material references

#### Actions:
1. **Add Missing Common Materials** to Materials.yaml:
   ```yaml
   # Add 15 commonly referenced materials
   - Carbon Steel (5 references)
   - Wrought Iron (2 references)
   - Aluminum Alloys (2 references)
   - PVC (1 reference)
   - Galvanized Steel (2 references)
   - Chrome-Plated Steel (2 references)
   - Tile (4 references)
   - Textiles (2 references)
   - Paper (2 references)
   - PCB (2 references)
   ```

2. **Create Material Aliases** in Contaminants.yaml:
   ```yaml
   material_aliases:
     "Carbon Steel": ["Steel", "Low Carbon Steel", "Mild Steel"]
     "Stainless Steel": ["Stainless", "SS304", "SS316"]
     "Aluminum Alloys": ["Aluminum", "6061", "7075"]
   ```

3. **Update Pattern References**:
   - Replace "Steel" → specific types based on context
   - Example: rust-oxidation → "Carbon Steel", "Cast Iron" (not "Steel")

**Expected Impact**: Reduces missing materials from 17.2% → 5%

---

### **Phase 2: Generic Term Resolution** (HIGH PRIORITY)
**Objective**: Replace generic category terms with specific materials

#### Strategy: Category-Aware Expansion

For each pattern with generic terms:
1. **Analyze chemistry** - What materials can this actually affect?
2. **Expand to specifics** - Replace "Metal" with actual metal list
3. **Validate scientifically** - Ensure chemical compatibility

#### Examples:

**BEFORE** (generic):
```yaml
rust-oxidation:
  valid_materials:
    - Steel
    - Iron
    - Metal  # ❌ Too generic
```

**AFTER** (specific):
```yaml
rust-oxidation:
  valid_materials:
    - Carbon Steel
    - Cast Iron
    - Wrought Iron
    - Tool Steel
    # Removed "Metal" - replaced with ferrous-specific materials
```

**BEFORE** (generic):
```yaml
industrial-oil:
  valid_materials:
    - ALL  # ❌ Too generic
```

**AFTER** (specific):
```yaml
industrial-oil:
  valid_materials:
    # Metals (high affinity)
    - Steel
    - Aluminum
    - Copper
    - Brass
    - Stainless Steel
    
    # Ceramics (moderate)
    - Alumina
    - Silicon Carbide
    
    # Glass (low but possible)
    - Float Glass
    - Borosilicate Glass
    
    # Others
    - Concrete
    - Stone
    
  prohibited_materials:
    - Porous Wood (absorbs oil)
```

**Expected Impact**: Reduces generic terms from 37.5% → 10%

---

### **Phase 3: Automated Validation** (MEDIUM PRIORITY)
**Objective**: Prevent regression, maintain quality

#### Implementation:

**1. Validation Script**: `scripts/validation/validate_contamination_accuracy.py`

```python
def validate_contamination_data():
    """
    Validates contamination pattern accuracy.
    
    Checks:
    - All materials exist in Materials.yaml
    - No generic category terms used
    - Chemical compatibility makes sense
    - No duplicate entries
    
    Returns:
        accuracy_score: float (0-100)
        issues: List[str]
    """
    
    issues = []
    
    # Check 1: Material existence
    for pattern in patterns:
        for material in valid_materials + prohibited_materials:
            if material not in materials_yaml:
                if material in GENERIC_TERMS:
                    issues.append(f"Generic term '{material}' in {pattern}")
                else:
                    issues.append(f"Missing material '{material}' in {pattern}")
    
    # Check 2: Chemical compatibility
    for pattern in patterns:
        chemistry = pattern.get('chemical_formula')
        for material in valid_materials:
            if not is_chemically_compatible(chemistry, material):
                issues.append(f"Chemical mismatch: {pattern} on {material}")
    
    # Calculate accuracy
    total_refs = count_all_material_references()
    valid_refs = total_refs - len(issues)
    accuracy = (valid_refs / total_refs) * 100
    
    return accuracy, issues
```

**2. Pre-commit Hook**:
```bash
#!/bin/bash
# .git/hooks/pre-commit

python3 scripts/validation/validate_contamination_accuracy.py

if [ $? -ne 0 ]; then
    echo "❌ Contamination data validation failed"
    echo "   Run: python3 scripts/validation/validate_contamination_accuracy.py --verbose"
    exit 1
fi
```

**3. CI/CD Integration**:
```yaml
# .github/workflows/validate-data.yml
name: Validate Contamination Data

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate contamination accuracy
        run: |
          python3 scripts/validation/validate_contamination_accuracy.py
          accuracy=$(python3 -c "import yaml; print(yaml.safe_load(open('validation_report.yaml'))['accuracy'])")
          if (( $(echo "$accuracy < 85" | bc -l) )); then
            echo "❌ Accuracy ${accuracy}% below 85% threshold"
            exit 1
          fi
```

**Expected Impact**: Maintains 85%+ accuracy long-term

---

## 🔧 Implementation Tools

### **Tool 1: Material Resolver**
**Purpose**: Find best material matches for generic terms

```python
# scripts/tools/resolve_generic_materials.py

def resolve_generic_term(generic_term: str, pattern_chemistry: str) -> List[str]:
    """
    Resolves generic term to specific materials.
    
    Example:
        resolve_generic_term("Metal", "Fe₂O₃") 
        → ["Carbon Steel", "Cast Iron", "Wrought Iron"]
    
        resolve_generic_term("Plastics", "UV")
        → ["PVC", "Polypropylene", "Polyethylene", "PMMA"]
    """
    
    category_map = {
        'Metal': materials_by_category['metal'],
        'Ceramic': materials_by_category['ceramic'],
        'Plastics': materials_by_category['plastic'],
        # ...
    }
    
    candidates = category_map.get(generic_term, [])
    
    # Filter by chemical compatibility
    if pattern_chemistry:
        candidates = [m for m in candidates 
                     if is_compatible(m, pattern_chemistry)]
    
    return candidates[:10]  # Top 10 most relevant
```

### **Tool 2: Contamination Pattern Expander**
**Purpose**: Bulk update patterns with specific materials

```python
# scripts/tools/expand_contamination_patterns.py

def expand_pattern(pattern_id: str, dry_run: bool = True):
    """
    Expands generic terms in pattern to specific materials.
    
    Example:
        Before: valid_materials: ["Metal", "Glass"]
        After:  valid_materials: ["Steel", "Aluminum", "Copper", 
                                   "Float Glass", "Borosilicate Glass"]
    """
    
    pattern = load_pattern(pattern_id)
    
    expanded_valid = []
    for material in pattern['valid_materials']:
        if material in GENERIC_TERMS:
            # Resolve to specifics
            specifics = resolve_generic_term(material, pattern['composition'])
            expanded_valid.extend(specifics)
            print(f"   Expanded '{material}' → {len(specifics)} materials")
        else:
            expanded_valid.append(material)
    
    if not dry_run:
        pattern['valid_materials'] = expanded_valid
        save_pattern(pattern)
```

### **Tool 3: Accuracy Reporter**
**Purpose**: Generate accuracy reports with fix suggestions

```bash
# Usage
python3 scripts/tools/contamination_accuracy_report.py

# Output:
📊 Contamination Data Accuracy Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current Accuracy: 45.3%
Target Accuracy:  85.0%
Gap:             39.7% (207 entries to fix)

🔍 Top Issues:
   1. Generic "Plastics" (44 occurrences)
      → Suggested: PVC, Polypropylene, Polyethylene, PMMA
   
   2. Generic "Metal" (26 occurrences)
      → Analyze pattern chemistry to determine specific metals
   
   3. Missing "Carbon Steel" (5 occurrences)
      → Add to Materials.yaml or use "Steel" alias

💡 Quick Fixes:
   Run: python3 scripts/tools/expand_contamination_patterns.py --all --dry-run
```

---

## 📅 Implementation Timeline

### **Week 1: Phase 1 - Material Expansion**
- **Day 1-2**: Add 15 missing materials to Materials.yaml
- **Day 3**: Create material aliases system
- **Day 4-5**: Update high-priority patterns (rust, oil, oxidation)
- **Deliverable**: Accuracy 45% → 60%

### **Week 2: Phase 2 - Generic Resolution**
- **Day 1**: Build material resolver tool
- **Day 2**: Build pattern expander tool
- **Day 3-4**: Expand top 20 patterns with generic terms
- **Day 5**: Expand remaining 80 patterns
- **Deliverable**: Accuracy 60% → 85%

### **Week 3: Phase 3 - Validation**
- **Day 1-2**: Build validation script
- **Day 3**: Add pre-commit hooks
- **Day 4**: CI/CD integration
- **Day 5**: Documentation and training
- **Deliverable**: Automated quality gates in place

---

## 🎯 Success Metrics

### Primary KPI
- **Accuracy Score**: 45.3% → 85%+ (187% improvement)

### Secondary KPIs
- **Specific Material %**: 45.3% → 85%
- **Generic Term %**: 37.5% → 10%
- **Missing Material %**: 17.2% → 5%
- **Patterns with Issues**: 100 → <20

### Quality Gates
- ✅ No new generic terms added
- ✅ All materials exist in Materials.yaml
- ✅ Chemical compatibility validated
- ✅ Accuracy maintained above 85%

---

## 🚀 Quick Start: Immediate Improvements

### **Fix the Top 5 Offenders** (1-2 hours)

1. **industrial-oil** (ALL → specific list)
2. **environmental-dust** (ALL → specific list)
3. **uv-chalking** (Plastics → specific polymers)
4. **paint-residue** (Metals → specific metals)
5. **rust-oxidation** (Steel → Carbon Steel, Cast Iron, etc.)

**Commands**:
```bash
# Run accuracy analysis
python3 scripts/tools/contamination_accuracy_report.py

# Expand top 5 patterns (dry-run)
python3 scripts/tools/expand_contamination_patterns.py \
    --patterns industrial-oil environmental-dust uv-chalking paint-residue rust-oxidation \
    --dry-run

# Apply changes
python3 scripts/tools/expand_contamination_patterns.py \
    --patterns industrial-oil environmental-dust uv-chalking paint-residue rust-oxidation \
    --apply
```

**Expected Impact**: 45.3% → 55% accuracy in 2 hours

---

## 💡 Alternative: AI-Powered Resolution

### **Option: Use Gemini for Automatic Expansion**

```python
def ai_expand_pattern(pattern_id: str):
    """
    Use Gemini AI to intelligently expand generic terms
    based on pattern chemistry and contamination type.
    """
    
    pattern = load_pattern(pattern_id)
    
    prompt = f"""
    Contamination Pattern: {pattern['name']}
    Chemical Composition: {pattern.get('composition', 'Not specified')}
    Description: {pattern['description']}
    
    Current Materials:
    - Valid: {pattern.get('valid_materials', [])}
    - Prohibited: {pattern.get('prohibited_materials', [])}
    
    Task: Replace ANY generic terms (Metal, Plastics, Glass, etc.) 
    with SPECIFIC material names from the following list:
    {list(all_materials.keys())}
    
    Requirements:
    - Chemical compatibility with contamination composition
    - Physical/practical likelihood of occurrence
    - Return ONLY materials that exist in the provided list
    - Return JSON: {{valid_materials: [...], prohibited_materials: [...]}}
    """
    
    response = gemini_model.generate_content(prompt)
    return parse_json_response(response.text)
```

**Pros**: Fast, intelligent, contextual
**Cons**: Requires manual review, API costs
**Timeline**: Could complete all 100 patterns in 1 day

---

## 📖 Maintenance Best Practices

### **Adding New Contamination Patterns**

1. **Use Specific Materials Only**
   - ✅ "Aluminum", "Copper", "Steel"
   - ❌ "Metal", "Plastics", "ALL"

2. **Reference Materials.yaml**
   - Check material exists before adding
   - Use exact name (case-sensitive)

3. **Validate Chemically**
   - Can this contamination actually occur on this material?
   - Example: Rust only on ferrous metals

4. **Run Validation**
   ```bash
   python3 scripts/validation/validate_contamination_accuracy.py
   ```

### **Adding New Materials**

1. **Update Materials.yaml** first
2. **Then update Contaminants.yaml** references
3. **Run validation** to catch issues
4. **Update category mappings** if new category

---

## 🎓 Training & Documentation

### **Developer Guide**
- How to add contamination patterns correctly
- How to resolve generic terms
- How to validate changes

### **Data Quality Guide**
- Understanding accuracy metrics
- Running validation reports
- Interpreting results

### **Contribution Guidelines**
- PR checklist includes accuracy validation
- Examples of good vs bad patterns
- Common pitfalls to avoid

---

## ✅ Approval & Next Steps

**Recommendation**: Start with Phase 1 (Material Expansion) immediately.

**Estimated Effort**:
- Phase 1: 3-5 days
- Phase 2: 5-7 days
- Phase 3: 3-5 days
- **Total**: 2-3 weeks to reach 85%+ accuracy

**ROI**: 
- Better image generation (more accurate contamination visuals)
- More reliable laser parameter recommendations
- Reduced manual corrections needed
- Future-proof data quality

**Decision Required**:
- [ ] Approve full 3-phase approach
- [ ] Start with Phase 1 only (quick wins)
- [ ] Prefer AI-powered resolution (faster but requires review)
- [ ] Other (specify)

---

**Questions?** Let me know if you'd like me to:
1. Start implementing Phase 1 immediately
2. Build the validation/expansion tools first
3. Run AI-powered resolution on top 10 patterns as a proof of concept
4. Something else
