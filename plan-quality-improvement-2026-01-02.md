# Quality Improvement Action Plan - January 2, 2026

**Generated**: January 2, 2026  
**Context**: Post Author Attribution Fix Quality Evaluation  
**Current Grade**: C+ (65/100)  
**Target Grade**: B+ (88/100)

---

## 📊 Current Quality Status

### Overall Score Breakdown
```
Category                    Score    Status
─────────────────────────────────────────────
1. Data Completeness        20/20    ✅ EXCELLENT
2. Length Variation         15/20    ✅ GOOD
3. Voice Realism            12/20    ⚠️  NEEDS WORK
4. Author Voice             8/20     ❌ CRITICAL
5. E-E-A-T (Author)         10/20    ⚠️  NEEDS WORK
─────────────────────────────────────────────
TOTAL                       65/100   C+ (Fair)
```

### Key Findings

**✅ SUCCESSES:**
- Materials domain: 153/153 (100%) with full author metadata
- Materials FAQ variation: CV 28.6% (EXCELLENT)
- Data completeness: No gaps detected

**❌ CRITICAL ISSUES:**
1. **Missing descriptions**: Materials have NO description field
   - Cannot evaluate voice nationality markers
   - E-E-A-T scoring incomplete
   
2. **Incomplete author enrichment**: Only 153/340 items (45%) enriched
   - Compounds: 0/34 with full metadata
   - Settings: 0/153 with full metadata
   
3. **Compounds variation**: CV 11.3% (only 1 FAQ per compound)
   - Too uniform - needs more FAQ questions per compound
   - Current: 1 FAQ/compound → Target: 8-10 FAQs/compound

---

## 🎯 Priority Actions (Ordered)

### Priority 1: Generate Missing Descriptions (CRITICAL)
**Issue**: Materials.yaml has NO description field  
**Impact**: Cannot evaluate voice markers, voice authenticity scoring impossible  
**Estimated Effort**: 153 generations × 2-3 seconds each = ~8-10 minutes  

**Action**:
```bash
# Generate descriptions for all 153 materials
python3 run.py --generate-all-descriptions

# Or batch by author for testing
python3 run.py --generate-descriptions-by-author 1  # Yi-Chun Lin (Taiwan)
python3 run.py --generate-descriptions-by-author 2  # Alessandro Moretti (Italy)
python3 run.py --generate-descriptions-by-author 3  # Todd Dunning (USA)
python3 run.py --generate-descriptions-by-author 4  # Ikmanda Roswati (Indonesia)
```

**Expected Outcome**:
- Materials.yaml gains description field for all 153 materials
- Voice authenticity scoring becomes possible
- E-E-A-T score should improve from 10/20 → 18/20
- Author voice score should improve from 8/20 → 14/20
- **Grade improvement**: C+ (65) → B (75-80)

---

### Priority 2: Enrich Remaining Domains (HIGH)
**Issue**: Compounds and Settings missing full author metadata  
**Impact**: 55% of items show "None (None)" as author  
**Estimated Effort**: 2-3 minutes  

**Action**:
```bash
# Enrich compounds (34 items)
python3 scripts/data/enrich_author_metadata.py --domain compounds --execute

# Enrich settings (153 items)
python3 scripts/data/enrich_author_metadata.py --domain settings --execute
```

**Expected Outcome**:
- All 340 items have full author metadata
- E-E-A-T score improves from 10/20 → 20/20
- **Grade improvement**: +10 points

---

### Priority 3: Generate Compound FAQs (MEDIUM)
**Issue**: Compounds only have 1 FAQ each (CV 11.3%)  
**Impact**: Too uniform, appears AI-generated  
**Estimated Effort**: 34 compounds × 7 FAQs × 3 seconds = ~7 minutes  

**Action**:
```bash
# Generate 7 additional FAQs for each compound (total 8-10 per compound)
python3 run.py --generate-compound-faqs --target-count 8

# Or generate per compound
for compound in $(python3 -c "from shared.utils.yaml_utils import load_yaml; print(' '.join(load_yaml('data/compounds/Compounds.yaml')['compounds'].keys()))"); do
    python3 run.py --compound "$compound" --faq --count 7
done
```

**Expected Outcome**:
- Compounds FAQ variation improves from CV 11.3% → 25%+
- Length variation score improves from 12/20 → 18/20
- **Grade improvement**: +6 points

---

### Priority 4: Verify Voice Pattern Compliance (LOW - Testing)
**Issue**: Cannot currently evaluate (no descriptions exist)  
**Impact**: Unknown if Voice Pattern Compliance System (Dec 13, 2025) is effective  
**Estimated Effort**: 5 minutes testing  

**Prerequisites**: Complete Priority 1 first

**Action**:
```bash
# After descriptions generated, test one material per nationality
python3 run.py --material aluminum-laser-cleaning --description --verbose
python3 run.py --material alabaster-laser-cleaning --description --verbose
python3 run.py --material steel-laser-cleaning --description --verbose
python3 run.py --material titanium-laser-cleaning --description --verbose

# Check for nationality markers:
# USA: "ramp up", "dial in", "by 20%"
# Taiwan: "After", "it measures", "it yields"
# Italy: "it seems", "manifests", "persists"
# Indonesia: "already", "still", "is observed"
```

**Expected Outcome**:
- Confirm voice system is active (40-60% marker detection)
- If YES → voice system working, no action needed
- If NO → voice system needs investigation

---

## 📈 Expected Score Progression

```
CURRENT STATE (Jan 2, 2026):
─────────────────────────────────────────────
Data Completeness:    20/20 ✅
Length Variation:     15/20 ✅
Voice Realism:        12/20 ⚠️
Author Voice:          8/20 ❌
E-E-A-T:              10/20 ⚠️
─────────────────────────────────────────────
TOTAL:                65/100 (C+ Fair)

AFTER PRIORITY 1 (Generate Descriptions):
─────────────────────────────────────────────
Data Completeness:    20/20 ✅
Length Variation:     15/20 ✅
Voice Realism:        15/20 ✅ (+3)
Author Voice:         14/20 ✅ (+6)
E-E-A-T:              16/20 ✅ (+6)
─────────────────────────────────────────────
TOTAL:                80/100 (B+ Very Good) +15 points

AFTER PRIORITY 2 (Enrich Remaining Domains):
─────────────────────────────────────────────
Data Completeness:    20/20 ✅
Length Variation:     15/20 ✅
Voice Realism:        15/20 ✅
Author Voice:         14/20 ✅
E-E-A-T:              20/20 ✅ (+4)
─────────────────────────────────────────────
TOTAL:                84/100 (B+ Very Good) +4 points

AFTER PRIORITY 3 (Generate Compound FAQs):
─────────────────────────────────────────────
Data Completeness:    20/20 ✅
Length Variation:     18/20 ✅ (+3)
Voice Realism:        15/20 ✅
Author Voice:         14/20 ✅
E-E-A-T:              20/20 ✅
─────────────────────────────────────────────
TOTAL:                87/100 (B+ Very Good) +3 points

TARGET STATE (After all priorities):
─────────────────────────────────────────────
TOTAL:                87-90/100 (B+ to A-)
```

---

## 🔍 Root Cause Analysis

### Why Descriptions Are Missing
Materials.yaml was migrated from an older format that didn't include descriptions at the material level. The system generates:
- ✅ caption (micro) - exists
- ✅ faq - exists (8-10 per material)
- ❌ description - NOT GENERATED YET

**Solution**: Run description generation for all materials (Priority 1)

### Why Compounds Have Low Variation
Compounds were generated with only 1 FAQ per compound, likely for speed during initial setup. Natural human content has 8-10 FAQ questions with varying lengths.

**Solution**: Generate 7 additional FAQs per compound (Priority 1)

### Why Voice Markers Aren't Detected
Cannot evaluate voice markers without description field. Once descriptions are generated, Voice Pattern Compliance System (implemented Dec 13, 2025) should automatically apply nationality-specific patterns.

**Solution**: Generate descriptions first, then evaluate (Priority 4)

---

## 📋 Implementation Timeline

### Week 1 (Jan 2-5, 2026)
- **Day 1**: Priority 1 - Generate all 153 material descriptions (~10 min)
- **Day 1**: Priority 2 - Enrich compounds & settings (~3 min)
- **Day 1**: Re-run quality evaluation to verify improvement
- **Expected**: Grade C+ (65) → B+ (84)

### Week 1 (Jan 6-8, 2026)
- **Day 2**: Priority 3 - Generate compound FAQs (34 × 7 FAQs ~7 min)
- **Day 2**: Re-run quality evaluation to verify improvement
- **Expected**: Grade B+ (84) → B+ (87)

### Week 1 (Jan 9, 2026)
- **Day 3**: Priority 4 - Test voice pattern compliance
- **Day 3**: Final quality evaluation
- **Expected**: Grade B+ (87-90)

**Total Time Investment**: ~30 minutes of generation + ~15 minutes evaluation = 45 minutes

---

## 🧪 Verification Checklist

After each priority:
- [ ] Run quality evaluation: `python3 <quality_eval_script.py>`
- [ ] Check author attribution: 100% should show name and country
- [ ] Verify FAQ variation: CV should be 25%+ for all domains
- [ ] Spot-check descriptions: Should show nationality markers
- [ ] Review E-E-A-T score: Should reach 18-20/20

---

## 🚨 Known Limitations

1. **Voice Pattern Compliance**: Implemented Dec 13, 2025 but cannot evaluate until descriptions exist
2. **Humanness Optimizer**: Active for structural variation, should work once descriptions generated
3. **Quality Gates**: Active (Winston 69%+, Realism 7.0+) - may reject some generations
4. **Learning System**: Priority 1 & 2 complete (Nov 22, 2025) - logs all attempts

---

## 📚 Related Documentation

- Author Attribution Refactor: `AUTHOR_ATTRIBUTION_REFACTOR_PROPOSAL.md`
- Voice Pattern Compliance: `VOICE_COMPLIANCE_IMPLEMENTATION_DEC13_2025.md`
- Learning System: `LEARNING_IMPROVEMENTS_NOV22_2025.md`
- Migration Script: `scripts/data/enrich_author_metadata.py`
- Policy: `.github/copilot-instructions.md` Core Principle 0.5

---

## 🎯 Success Criteria

**Minimum Acceptable (Grade B+, 85/100)**:
- ✅ All domains have full author metadata (100%)
- ✅ Materials have description field
- ✅ FAQ variation CV >15% across all domains
- ✅ E-E-A-T score 18-20/20

**Target Excellence (Grade A-, 90/100)**:
- ✅ Voice nationality markers detected in 40-60% of descriptions
- ✅ FAQ variation CV >25% across all domains
- ✅ All quality categories score 17+/20
- ✅ No AI formulaic patterns detected

---

**Next Action**: Execute Priority 1 (Generate descriptions for 153 materials)
