# Comprehensive Dynamic Duplication Detection System

**Created**: October 29, 2025  
**Location**: `validation/duplication_detector.py`  
**Status**: ✅ Operational - Ready for integration

---

## 🎯 Overview

A sophisticated, multi-dimensional duplication detection system that catches formulaic patterns, repetitive structures, and robotic writing that simple word matching misses.

### **The Problem with Simple Rules**

Previous approach:
```python
# TOO SIMPLE - Only catches obvious repetition
if text.count("this") > 5:
    return "FAIL"
```

This misses:
- ❌ Formulaic patterns like `[Action] + This [benefit]`
- ❌ Uniform word counts (e.g., all 30-32 words)
- ❌ Repetitive sentence structures
- ❌ Overused bigrams/trigrams
- ❌ Low structural diversity

---

## 🔬 Detection Dimensions

### **1. Connector Overuse Detection**
Catches excessive use of AI-typical connectors:

```python
AI_CONNECTORS = [
    'this', 'these', 'those', 'such',
    'additionally', 'furthermore', 'moreover',
    'however', 'therefore', 'thus', 'hence',
    'consequently', 'accordingly', 'subsequently'
]
```

**Example Violation**:
```
Aluminum: "this" in 78% of answers (max 35%)
❌ FAIL: Robotic connector overuse
```

**Scoring**: -15 points per violation, -5 per warning

---

### **2. Word Count Uniformity**
Detects robotic consistency in answer lengths using **Coefficient of Variation (CV)**:

```python
CV = (standard_deviation / mean) * 100

# Human writing: CV > 12% (natural variation)
# Robot writing: CV < 10% (mechanical consistency)
```

**Example Violation**:
```
Brass: All answers 18-23 words (5w range, CV 9.4%)
❌ FAIL: Too uniform - robotic consistency
```

**Thresholds**:
- CV < 12% = FAIL (-15 points)
- Range < 15 words = FAIL (-10 points)

---

### **3. N-Gram Repetition**
Analyzes bigrams (2-word) and trigrams (3-word) phrase repetition:

**Example Violation**:
```
Granite: "laser cleaning" repeated in 57% of answers
Bronze: "800 mpa" repeated in 38% of answers
❌ FAIL: Phrase overuse
```

**Thresholds**:
- Bigram > 30% = FAIL (-10 points)
- Trigram > 25% = FAIL (-10 points)

---

### **4. Sentence Structure Patterns**
Creates structural signatures for each sentence:

```python
# Structure = [TYPE]_[LENGTH]_[COMMAS]
"This non-contact method..." → DEMONSTRATIVE_6_0
"Laser cleaning removes..." → OTHER_5_0
"Additionally, it ensures..." → CONNECTOR_7_2
```

Calculates **diversity score**:
```python
diversity = unique_structures / total_structures

# Good: diversity > 0.6 (60% unique)
# Bad: diversity < 0.6 (too repetitive)
```

**Example Violation**:
```
Aluminum: 0.53 diversity (min 0.6)
❌ FAIL: Low structural diversity
```

---

### **5. Formulaic Pattern Detection**
Uses regex to catch mechanical writing patterns:

```python
FORMULAIC_PATTERNS = [
    r'^(employ|apply|utilize|use)\s+\w+.*\.\s+this\s+\w+',  # [Action] + This
    r'^(laser|pulsed|regular)\s+\w+.*\.\s+(this|it)\s+\w+',  # [Subject] + This/It
    r'^\w+\s+\w+\s+\w+.*\.\s+this\s+(ensures|supports|sustains)',  # Pattern + This [verb]
]
```

**Example Violation**:
```
Aluminum FAQ:
  "Employ pulsed bursts. This supports oxidation..."
  "Laser cleaning removes... This sustains tensile strength..."
  "Use non-contact technique. This ensures removal..."
  
  ❌ FAIL: Formula detected 3 times (Action + This [verb])
```

---

### **6. Sentence Starter Analysis**
Tracks first word/phrase distribution:

**Example Violation**:
```
Aluminum: "This" starts 58% of sentences (max 35%)
Granite: "Laser" starts 38% of sentences (max 35%)
❌ FAIL: Sentence starter overuse
```

---

### **7. Parallel Structure Detection**
Detects when sentences follow same length/punctuation patterns:

```python
# Pattern signature: Length_bucket + Commas + Type
"Short sentence." → L1_C0_S
"Short question?" → L1_C0_Q
"Medium sentence with comma." → L2_C1_S
```

**Example Violation**:
```
Bronze: Variation score 0.38 (min 0.5)
⚠️ WARNING: Excessive parallel structures
```

---

## 📊 Real-World Results

### **Test Run on 5 Materials**:

| Material | Score | CV% | Range | "This"% | Violations | Grade |
|----------|-------|-----|-------|---------|------------|-------|
| **Aluminum** | 2.0 | 7.3% | 6w | 78% | 8 | **F** |
| **Bronze** | 15.0 | 7.1% | 8w | 50% | 8 | **F** |
| **Brass** | 75.0 | 9.4% | 5w | 0% | 2 | **C** |
| **Steel** | 50.0 | 6.6% | 6w | 38% | 4 | **D** |
| **Granite** | 52.0 | 14.0% | 9w | 0% | 10 | **D** |

**Key Findings**:
- ❌ **Aluminum**: 78% "This" usage, formulaic pattern 3x
- ❌ **Bronze**: 50% "This" usage, bigram repetition (800 mpa)
- ❌ **Brass**: Extreme uniformity (5w range, 9.4% CV)
- ❌ **Steel**: 38% "This" usage, formulaic pattern 2x
- ❌ **Granite**: Phrase overuse ("laser cleaning" 57%)

---

## 🔧 Configuration

### **Strict Mode** (Default):
```python
detector = DuplicationDetector(strict_mode=True)

# Strict thresholds:
connector_max_pct = 35%    # vs 40% in normal mode
word_cv_min = 12%          # vs 10% in normal mode
sentence_start_max_pct = 30%  # vs 35% in normal mode
```

### **Adjustable Thresholds**:
```python
DuplicationDetector.THRESHOLDS = {
    'connector_max_pct': 40,      # Max % using same connector
    'word_cv_min': 10,            # Min word count variation
    'word_range_min': 15,         # Min word range
    'bigram_max_pct': 30,         # Max bigram repetition
    'trigram_max_pct': 25,        # Max trigram repetition
    'sentence_start_max_pct': 35, # Max sentence starter usage
    'structure_diversity_min': 0.6, # Min structural diversity
}
```

---

## 💡 Actionable Recommendations

The system generates specific, actionable fixes:

### **Example Output**:
```
💡 RECOMMENDATIONS:
  • Reduce 'this' usage. Try alternatives: 'Additionally', 
    'Furthermore', 'For example', 'In contrast', 'Specifically'
    
  • Vary answer lengths: Mix short (20-25w), medium (30-40w), 
    and longer (45-50w) responses
    
  • Vary sentence structures: Mix simple, compound, and complex 
    sentences. Start with different word types
    
  • Avoid formulaic patterns like '[Action] + This [benefit]'. 
    Use natural, spontaneous writing
    
  • Reduce phrase repetition. Use synonyms and vary phrasing naturally
```

---

## 🚀 Integration

### **Usage in Validation Pipeline**:

```python
from validation.duplication_detector import validate_duplication

# Validate FAQ
result = validate_duplication(
    items=faq_questions,
    component_type='faq',
    strict_mode=True
)

if not result.passed:
    print(f"❌ FAIL: Score {result.score}/100")
    for violation in result.violations:
        print(f"   • {violation}")
    
    print("\n💡 Fix recommendations:")
    for rec in result.recommendations:
        print(f"   • {rec}")
```

### **Integration Points**:

1. **Post-Generation** (FAQ, Caption, Subtitle):
   ```python
   # In faq_generator.py, caption/generator.py, subtitle_generator.py
   from validation.duplication_detector import validate_duplication
   
   result = validate_duplication(faq_items, 'faq', strict_mode=True)
   if not result.passed:
       logger.warning(f"Duplication issues: {result.violations}")
       # Trigger regeneration with variation instructions
   ```

2. **Pre-Export Validation**:
   ```python
   # Before exporting to frontmatter
   detector = DuplicationDetector(strict_mode=True)
   result = detector.analyze(material_faq, 'faq')
   
   if not result.passed:
       raise ValidationError(
           f"Material {name} failed duplication check: {result.violations}"
       )
   ```

3. **Batch Validation**:
   ```python
   # Check all materials
   for material_name, material_data in materials.items():
       result = validate_duplication(
           material_data['faq']['questions'],
           'faq'
       )
       print(f"{material_name}: {result.score}/100")
   ```

---

## 📈 Scoring System

**Total Score**: 0-100 (starts at 100, deductions applied)

| Violation Type | Deduction |
|----------------|-----------|
| Connector overuse | -15 points |
| Word CV too low | -15 points |
| Word range too narrow | -10 points |
| N-gram repetition | -10 points |
| Low structural diversity | -20 points |
| Formulaic pattern | -10 points per pattern |
| Sentence starter overuse | -8 points |
| Parallel structures | -5 points (warning) |

**Pass Threshold**: Score ≥ 70 AND zero violations

---

## 🎯 Success Metrics

**After Integration** (Expected Results):

| Metric | Before | After |
|--------|--------|-------|
| Avg Score | 38.8/100 | >75/100 |
| Pass Rate | 0% (0/5) | >80% (4/5) |
| "This" Usage | 33.2% avg | <25% avg |
| Word CV | 8.5% avg | >12% avg |
| Word Range | 6.8w avg | >15w avg |

---

## 🔍 Why This Works

### **Multi-Dimensional Analysis**:
- Single-metric rules miss patterns
- 7 different detection methods catch everything
- Statistical analysis (CV, diversity scores) = objective

### **Dynamic Thresholds**:
- Not hardcoded "count('this') > 5"
- Percentage-based (adapts to content length)
- Configurable for different quality standards

### **Actionable Output**:
- Not just "FAIL" - explains WHY
- Specific recommendations for fixing
- Shows exact patterns to avoid

### **Comprehensive Coverage**:
- Catches surface patterns (connectors, starters)
- Catches deep structure (diversity, formulas)
- Catches statistical anomalies (uniformity, CV)

---

## 📚 References

**Test File**: `test_duplication_detector.py`  
**Documentation**: This file  
**Original Issue**: Cross-author duplication analysis (October 29, 2025)  
**Related Reports**: 
- `ALUMINUM_FAQ_DUPLICATION_REPORT.md`
- `CROSS_AUTHOR_DUPLICATION_ANALYSIS.md`

---

## ✅ Next Steps

1. **Integrate into FAQ Generator**:
   - Add `validate_duplication()` call after generation
   - Auto-regenerate if score < 70
   - Pass recommendations to prompt for variation

2. **Add to Caption/Subtitle Generators**:
   - Currently NO validation in these components
   - Apply same duplication detection

3. **Update Prompts**:
   - Add explicit variation requirements based on recommendations
   - Specify: "Use 'This' in <20% of answers"
   - Require: "Vary lengths: 20-50w range minimum"

4. **Monitor Metrics**:
   - Track avg score over time
   - Set quality gate: No export if score < 70
   - Report on pass rate improvements

---

**Bottom Line**: This system catches what simple word counting misses. It's dynamic, comprehensive, and actionable - exactly what we need to eliminate robotic duplication across all authors.
