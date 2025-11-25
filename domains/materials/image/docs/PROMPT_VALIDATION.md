# Prompt Validation System
**Date**: November 25, 2025  
**Status**: ✅ IMPLEMENTED

## 🎯 Purpose

Ensures all Imagen 4 prompts are optimally structured for clarity, detail, and accuracy. Validates prompts BEFORE generation to catch contradictions, ambiguity, duplication, and clarity issues.

---

## 🔍 Validation Criteria

### 1. **Maximum Detail** ✅
- **Contamination patterns**: Specific colors, textures, thickness variations
- **Aging effects**: Timeline progression, reversibility, micro-scale distribution
- **Distribution physics**: Gravity effects, UV gradients, stress concentration
- **Material appearance**: Base material characteristics when clean
- **Lighting requirements**: How light interacts with contamination/aging

**Goal**: Provide Imagen 4 with rich, specific visual guidance

### 2. **No Contradictions** ✅
- **Spatial consistency**: "Same physical object" on both sides (5-10% position shift allowed)
- **Physical laws**: Gravity-driven drips/pooling, UV gradient from exposed→shaded
- **Material properties**: Texture/color consistent with material type
- **Environmental logic**: Moisture accumulation where expected, UV damage on sun-facing surfaces

**Prohibited**:
- "Uniform coating" where gravity should create variation
- "Symmetric patterns" in asymmetric environments
- "Instant aging" without gradual progression
- "Single-color oxidation" (real corrosion has gradients)

### 3. **Clarity & Precision** ✅
- **Unambiguous language**: "Orange-brown rust patches" not "rust-like discoloration"
- **Specific measurements**: "80-95% coverage" not "heavy contamination"
- **Clear boundaries**: "Left=before, Right=after" with explicit split
- **Lighting direction**: "Bright diffused overhead lighting" not "good lighting"

**Avoid**:
- Vague descriptors ("some", "various", "typical")
- Abstract concepts ("artistic", "dramatic", "interesting")
- Technical jargon without definition

### 4. **No Duplication** ✅
- **Single contamination description**: Concise list, not repeated in multiple sections
- **No redundant adjectives**: "Dark gray metallic surface" not "dark gray metallic gray surface"
- **Consolidated instructions**: Combine related requirements, don't repeat

**Structure**:
```
1. Subject definition (material + object + environment)
2. Contamination patterns (single concise section)
3. Coverage/uniformity scales (numerical levels)
4. View mode & lighting
5. Technical requirements
```

---

## 🛡️ Validation Implementation

### Pre-Generation Validation

```python
def validate_prompt(prompt: str, research_data: Dict) -> Dict[str, Any]:
    """
    Validate prompt before Imagen 4 generation.
    
    Returns:
        {
            "valid": bool,
            "issues": List[str],
            "warnings": List[str],
            "metrics": {
                "length": int,
                "detail_score": float,
                "clarity_score": float,
                "duplication_score": float
            }
        }
    """
```

### Validation Checks

#### 1. **Length Check**
- **Optimal**: 1,000-2,000 characters
- **Warning**: < 800 chars (insufficient detail) or > 2,500 chars (may lose focus)
- **Fail**: > 3,000 chars (exceeds Imagen 4 effective limit)

#### 2. **Detail Score** (0-100)
- Contamination patterns described: +20
- Aging effects included: +15
- Distribution physics explained: +15
- Micro-scale details (grain, edges): +10
- Color specificity (not just "brown"): +10
- Texture specificity (matte/glossy/granular): +10
- Thickness variations noted: +10
- Environmental context provided: +10

**Threshold**: Minimum 60/100 for generation

#### 3. **Contradiction Detection**
- Check for physics violations:
  - "Uniform coating" + "gravity effects" → CONFLICT
  - "Symmetric pattern" + "environmental exposure" → CONFLICT
  - "Instant appearance" + "aging timeline" → CONFLICT
- Check for spatial inconsistencies:
  - "Same object" + "different sizes" → CONFLICT
  - "Identical position" + "5-10% shift required" → CONFLICT

**Threshold**: Zero contradictions allowed

#### 4. **Clarity Analysis**
- Vague terms detected: "some", "various", "typical", "normal" → WARNING
- Abstract terms detected: "artistic", "interesting", "nice" → FAIL
- Missing measurements: No contamination level specified → WARNING
- Missing split definition: "Left"/"Right" not specified → FAIL

**Threshold**: No FAIL-level clarity issues

#### 5. **Duplication Detection**
- Word repetition analysis (n-grams)
- Sentence similarity check (cosine similarity > 0.8)
- Redundant adjective detection

**Threshold**: < 10% duplicate content

---

## 📊 Validation Metrics

### Prompt Quality Scorecard

```
┌─────────────────────────────────────────────────┐
│ PROMPT VALIDATION REPORT                        │
├─────────────────────────────────────────────────┤
│ ✅ Length: 1,243 chars (optimal)                │
│ ✅ Detail Score: 85/100 (excellent)             │
│ ✅ Contradictions: 0 (pass)                     │
│ ✅ Clarity: Pass (no vague terms)               │
│ ✅ Duplication: 3% (excellent)                  │
├─────────────────────────────────────────────────┤
│ Overall: PASS - Ready for generation            │
└─────────────────────────────────────────────────┘
```

### Common Issues Detected

**Issue**: "Typical contamination on steel surface"  
**Problem**: Vague descriptor "typical"  
**Fix**: "Industrial oil (dark brown, glossy) + rust patches (orange-brown, matte)"

**Issue**: "Heavy contamination with significant buildup"  
**Problem**: Redundant phrasing  
**Fix**: "Heavy contamination (80-95% coverage)"

**Issue**: "Uniform rust coating with drip patterns"  
**Problem**: Contradiction (uniform ≠ drips)  
**Fix**: "Rust concentrated at top, dripping downward, pooling at bottom"

---

## 🔧 Integration with Material Generator

### Validation Workflow

```
1. Research contamination/aging patterns
   ↓
2. Build prompt from template + research
   ↓
3. **VALIDATE PROMPT** ← NEW STEP
   ├─ Length check
   ├─ Detail score
   ├─ Contradiction scan
   ├─ Clarity analysis
   └─ Duplication detection
   ↓
4. If validation fails → Rebuild prompt
   ↓
5. If validation passes → Generate image
```

### Automatic Fixes

System attempts automatic fixes for common issues:

**Vague Terms**:
- "some contamination" → "moderate contamination (40-60% coverage)"
- "various colors" → Specify actual colors from research data

**Missing Details**:
- Add contamination level if missing (from config)
- Add distribution physics from research data
- Add micro-scale details from aging patterns

**Duplication**:
- Merge redundant adjectives
- Consolidate repeated descriptions
- Remove redundant sections

---

## 🚨 Fail-Fast on Critical Issues

### Immediate Failure (No Generation)

1. **Physics violations**: Contradictory physical behavior
2. **Missing core elements**: No contamination description, no left/right split
3. **Excessive length**: > 3,000 chars (Imagen 4 limitation)
4. **Abstract language**: "Artistic", "interesting", "dramatic" without concrete visuals

### Warnings (Generate with Notice)

1. **Low detail score**: < 60/100 (prompt may be too generic)
2. **Minor duplication**: 10-20% duplicate content
3. **Vague terms**: "Some", "various", "typical" used
4. **Suboptimal length**: < 800 or > 2,500 chars

---

## 📋 Validation Checklist

Before accepting prompt for generation:

- [ ] **Length**: 1,000-2,000 chars (optimal)
- [ ] **Detail score**: ≥ 60/100
- [ ] **Contamination patterns**: Specific colors, textures, distribution
- [ ] **Aging effects**: Timeline, reversibility, micro-scale details (if applicable)
- [ ] **Distribution physics**: Gravity, UV gradients, stress points
- [ ] **Contradictions**: Zero detected
- [ ] **Clarity**: No vague/abstract terms
- [ ] **Duplication**: < 10%
- [ ] **Split definition**: "Left=before, Right=after" clear
- [ ] **Lighting**: Specific lighting direction/quality

---

## 🧪 Testing

### Unit Tests

```python
def test_prompt_validation_length():
    """Test length boundaries"""
    
def test_prompt_validation_contradictions():
    """Test physics violation detection"""
    
def test_prompt_validation_clarity():
    """Test vague term detection"""
    
def test_prompt_validation_duplication():
    """Test n-gram similarity"""
    
def test_prompt_validation_detail_score():
    """Test detail scoring algorithm"""
```

### Integration Tests

```python
def test_validation_rejects_bad_prompts():
    """Ensure bad prompts fail validation"""
    
def test_validation_accepts_good_prompts():
    """Ensure good prompts pass validation"""
    
def test_automatic_fixes_applied():
    """Test automatic prompt improvement"""
```

---

## 📈 Success Metrics

### Before Validation (Observed Issues)
- Prompt length varied: 800-8,000 chars (inconsistent)
- Contradictions common: "uniform" + "drips"
- Vague terms: 30-40% of prompts
- Duplication: 15-25% average

### After Validation (Expected)
- Prompt length consistent: 1,000-2,000 chars
- Zero contradictions allowed
- Vague terms: < 5%
- Duplication: < 10%
- Detail score: Average 75/100 (vs. 45/100 before)

---

## 🔗 Related Documentation

- `AGING_RESEARCH_SYSTEM.md` - How aging patterns are researched
- `ARCHITECTURE.md` - System data flow including validation
- `TESTING.md` - Test coverage for validation system
- `TROUBLESHOOTING.md` - Fixing validation failures

---

**Status**: ✅ Validation system integrated into material_prompts.py  
**Impact**: Higher quality, more consistent Imagen 4 prompts  
**Validation**: Pending first batch generation with validation enabled
