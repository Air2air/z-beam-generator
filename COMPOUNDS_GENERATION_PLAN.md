# Compounds Content Generation Plan
**Date**: December 15, 2025  
**Status**: Ready for Execution  
**Total Work**: 19 compounds × 5 content types = **95 generations**

---

## 📊 Executive Summary

**Current State**:
- ✅ Metadata: 100% complete (chemical formulas, exposure limits, sources)
- ❌ Content: 0% complete (all 5 content fields are `null`)

**Infrastructure Status**:
- ✅ Domain setup complete (coordinator, data_loader, config)
- ✅ 5 prompt templates ready
- ✅ Exporter functional
- ✅ Author assignments distributed (4 authors)

**Estimated Time**: 30-45 minutes for full generation (with API rate limits)

---

## 🎯 Priority Tiers

### **TIER 1: Carcinogens (Highest Priority)** 🔴
**Count**: 7 compounds × 5 types = **35 generations**  
**Rationale**: Most dangerous, regulatory focus, litigation risk

1. **Formaldehyde** (formaldehyde) - Author 1
   - Category: carcinogen/aldehyde
   - Hazard: carcinogenic
   - Known: Nasopharyngeal cancer, leukemia

2. **Benzene** (benzene) - Author 2
   - Category: carcinogen/aromatic_hydrocarbon
   - Hazard: carcinogenic
   - Known: Bone marrow damage, leukemia

3. **PAHs** (pahs) - Author 3
   - Category: carcinogen/polycyclic_aromatic
   - Hazard: carcinogenic
   - Known: Lung cancer, skin cancer

4. **Acetaldehyde** (acetaldehyde) - Author 1
   - Category: carcinogen/aldehyde
   - Hazard: probable_carcinogen
   - Known: Respiratory carcinogen

5. **Acrolein** (acrolein) - Author 2
   - Category: carcinogen/aldehyde
   - Hazard: probable_carcinogen
   - Known: Severe irritant, possible carcinogen

6. **Toluene** (toluene) - Author 3
   - Category: carcinogen/aromatic_hydrocarbon
   - Hazard: neurotoxic
   - Known: CNS effects, reproductive toxin

7. **Styrene** (styrene) - Author 4
   - Category: carcinogen/aromatic_hydrocarbon
   - Hazard: probable_carcinogen
   - Known: Neurotoxic, possible carcinogen

---

### **TIER 2: Toxic Gases (High Priority)** 🟠
**Count**: 6 compounds × 5 types = **30 generations**  
**Rationale**: Immediate danger, monitoring required, acute toxicity

1. **Carbon Monoxide** (carbon-monoxide) - Author 4
   - Category: toxic_gas/asphyxiant
   - Hazard: toxic
   - Known: Asphyxiation, fatal at high doses

2. **Hydrogen Cyanide** (hydrogen-cyanide) - Author 1
   - Category: toxic_gas/cyanide
   - Hazard: extremely_toxic
   - Known: Rapid asphyxiation, fatal

3. **Nitrogen Oxides** (nitrogen-oxides) - Author 2
   - Category: toxic_gas/oxide
   - Hazard: toxic
   - Known: Respiratory damage, acid formation

4. **Sulfur Dioxide** (sulfur-dioxide) - Author 3
   - Category: toxic_gas/oxide
   - Hazard: toxic
   - Known: Respiratory irritant, acid formation

5. **Ammonia** (ammonia) - Author 4
   - Category: toxic_gas/base
   - Hazard: toxic
   - Known: Severe irritant, caustic

6. **VOCs** (vocs) - Author 1
   - Category: toxic_gas/volatile_organic
   - Hazard: varied
   - Known: Mixed toxicity profile

---

### **TIER 3: Corrosive Gases (High Priority)** 🟡
**Count**: 2 compounds × 5 types = **10 generations**  
**Rationale**: Immediate tissue damage, PPE critical

1. **Hydrogen Chloride** (hydrogen-chloride) - Author 2
   - Category: corrosive_gas/acid
   - Hazard: corrosive
   - Known: Severe burns, inhalation hazard

2. **Phosgene** (phosgene) - Author 3
   - Category: corrosive_gas/reactive
   - Hazard: extremely_toxic
   - Known: Delayed pulmonary edema, WWI chemical weapon

---

### **TIER 4: Metal Fumes (Medium Priority)** 🟢
**Count**: 3 compounds × 5 types = **15 generations**  
**Rationale**: Occupational exposure, chronic effects

1. **Zinc Oxide** (zinc-oxide) - Author 4
   - Category: metal_fume/oxide
   - Hazard: metal_fume_fever
   - Known: Flu-like symptoms, reversible

2. **Iron Oxide** (iron-oxide) - Author 1
   - Category: metal_fume/oxide
   - Hazard: mild
   - Known: Siderosis (benign)

3. **Chromium VI** (chromium-vi) - Author 2
   - Category: metal_fume/hexavalent
   - Hazard: carcinogenic
   - Known: Lung cancer, respiratory sensitization

---

### **TIER 5: Asphyxiants (Lower Priority)** 🔵
**Count**: 1 compound × 5 types = **5 generations**  
**Rationale**: Displacement hazard, less toxic

1. **Carbon Dioxide** (carbon-dioxide) - Author 3
   - Category: asphyxiant/simple
   - Hazard: asphyxiant
   - Known: Oxygen displacement

---

## 📋 Execution Strategies

### **Strategy A: Tier-by-Tier (Recommended)**
**Pros**: Prioritizes most dangerous, allows early deployment  
**Cons**: Switching contexts between compound types  
**Time**: 3-4 sessions (TIER 1, TIER 2, TIER 3+4+5)

```bash
# Session 1: TIER 1 - Carcinogens (35 generations)
python3 scripts/compounds/generate_tier1.py

# Session 2: TIER 2 - Toxic Gases (30 generations)
python3 scripts/compounds/generate_tier2.py

# Session 3: TIER 3-5 - Remaining (30 generations)
python3 scripts/compounds/generate_tier3_5.py
```

---

### **Strategy B: Content-Type-First**
**Pros**: Consistent voice per content type, efficient prompting  
**Cons**: No early deployment of high-priority compounds  
**Time**: 5 sessions (one per content type)

```bash
# Session 1: All descriptions (19 compounds)
python3 scripts/compounds/generate_all_descriptions.py

# Session 2: All health_effects (19 compounds)
python3 scripts/compounds/generate_all_health_effects.py

# Session 3: All exposure_guidelines (19 compounds)
python3 scripts/compounds/generate_all_exposure_guidelines.py

# Session 4: All detection_methods (19 compounds)
python3 scripts/compounds/generate_all_detection_methods.py

# Session 5: All first_aid (19 compounds)
python3 scripts/compounds/generate_all_first_aid.py
```

---

### **Strategy C: Hybrid (Best Quality)**
**Pros**: Complete high-priority compounds first, efficient for remaining  
**Cons**: More complex execution  
**Time**: 4-5 sessions

```bash
# Session 1: Complete TIER 1 carcinogens (7 × 5 = 35)
for compound in formaldehyde benzene pahs acetaldehyde acrolein toluene styrene; do
  python3 run.py --compound $compound --description
  python3 run.py --compound $compound --health-effects
  python3 run.py --compound $compound --exposure-guidelines
  python3 run.py --compound $compound --detection-methods
  python3 run.py --compound $compound --first-aid
done

# Session 2: Complete TIER 2 toxic gases (6 × 5 = 30)
# Session 3: Descriptions + health_effects for remaining (12 × 2 = 24)
# Session 4: Guidelines + detection + first-aid for remaining (12 × 3 = 36)
```

---

## 🔧 Technical Implementation

### **Command Patterns**

**Individual Generation**:
```bash
python3 run.py --compound formaldehyde --description
python3 run.py --compound formaldehyde --health-effects
python3 run.py --compound formaldehyde --exposure-guidelines
python3 run.py --compound formaldehyde --detection-methods
python3 run.py --compound formaldehyde --first-aid
```

**Batch Generation Script** (to be created):
```python
# scripts/compounds/batch_generate.py
import subprocess
from pathlib import Path

TIER_1 = ['formaldehyde', 'benzene', 'pahs', 'acetaldehyde', 
          'acrolein', 'toluene', 'styrene']

CONTENT_TYPES = ['description', 'health-effects', 'exposure-guidelines',
                 'detection-methods', 'first-aid']

for compound in TIER_1:
    for content_type in CONTENT_TYPES:
        cmd = f"python3 run.py --compound {compound} --{content_type}"
        subprocess.run(cmd, shell=True)
```

---

## 📊 Progress Tracking

### **Completion Matrix** (Update as you go)

| Compound | Desc | Health | Exposure | Detection | First Aid | Total |
|----------|------|--------|----------|-----------|-----------|-------|
| Formaldehyde | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 0/5 |
| Benzene | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 0/5 |
| PAHs | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 0/5 |
| Carbon Monoxide | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 0/5 |
| ... (15 more) | | | | | | |

**Progress Script**:
```bash
python3 << 'ENDSCRIPT'
import yaml
with open('data/compounds/Compounds.yaml') as f:
    data = yaml.safe_load(f)
fields = ['description', 'health_effects', 'exposure_guidelines', 
          'detection_methods', 'first_aid']
completed = sum(1 for c in data['compounds'].values() 
                for f in fields if c.get(f))
total = len(data['compounds']) * len(fields)
print(f"Progress: {completed}/{total} ({completed/total*100:.1f}%)")
ENDSCRIPT
```

---

## ⚠️ Quality Gates

Each generated content must pass:
1. **Winston AI Detection**: 69%+ human score
2. **Readability**: Pass status
3. **Realism Score**: 7.0/10 minimum
4. **Word Count Compliance**:
   - description: 120-180 words
   - health_effects: 200-300 words
   - exposure_guidelines: 150-250 words
   - detection_methods: 120-180 words
   - first_aid: 150-250 words

**Postprocessing Available**: Use `--postprocess` for quality improvement

---

## 🚀 Recommended Execution Plan

### **Phase 1: Prove the System (Day 1, 30 minutes)**
✅ Generate complete content for **1 TIER 1 compound** (Formaldehyde)
- Validates all 5 prompt templates
- Tests quality gates
- Verifies export functionality
- Provides sample for review

```bash
# Test with formaldehyde (5 generations, ~5-10 minutes)
python3 run.py --compound formaldehyde --description
python3 run.py --compound formaldehyde --health-effects
python3 run.py --compound formaldehyde --exposure-guidelines
python3 run.py --compound formaldehyde --detection-methods
python3 run.py --compound formaldehyde --first-aid

# Export and review
python3 -c "from export.compounds.trivial_exporter import CompoundExporter; CompoundExporter().export_all()"
```

### **Phase 2: Complete TIER 1 (Day 1-2, 2-3 hours)**
✅ Generate all carcinogens (7 compounds × 5 = 35 generations)
- Most critical for safety/liability
- Can deploy these immediately

### **Phase 3: Complete TIER 2 (Day 2-3, 2 hours)**
✅ Generate all toxic gases (6 compounds × 5 = 30 generations)
- Second-highest priority
- Common in laser cleaning operations

### **Phase 4: Complete Remaining (Day 3-4, 2 hours)**
✅ TIER 3-5 (6 compounds × 5 = 30 generations)
- Lower priority but still important
- Completes the full dataset

---

## 📈 Success Metrics

**After Phase 1**:
- ✓ 1 compound 100% complete (5/5 content types)
- ✓ All prompt templates validated
- ✓ Quality gates verified working
- ✓ Export to frontmatter successful

**After Phase 2**:
- ✓ 7 compounds 100% complete (35/95 content pieces)
- ✓ All carcinogens documented
- ✓ 37% overall completion

**After Phase 3**:
- ✓ 13 compounds 100% complete (65/95 content pieces)
- ✓ All high-priority compounds done
- ✓ 68% overall completion

**After Phase 4**:
- ✓ 19 compounds 100% complete (95/95 content pieces)
- ✓ Full domain operational
- ✓ 100% completion

---

## 🎯 Next Steps

1. **Review this plan** - Confirm strategy choice
2. **Execute Phase 1** - Validate system with formaldehyde
3. **Review output quality** - Check generated content
4. **Proceed to Phase 2** - Complete TIER 1 carcinogens
5. **Continue systematically** - Follow phases 3-4

**Ready to start?** Run:
```bash
python3 run.py --compound formaldehyde --description
```
