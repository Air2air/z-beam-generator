# FAQ Output Validation Script

## Overview

Comprehensive validation script that incorporates all project requirements for FAQ generation quality assurance.

**Location**: `scripts/validation/validate_faq_output.py`

## Features

### 1. **Word Count Validation**
- ✅ Enforces 20-50 words per answer range
- ✅ Detects answers too short or too long
- ✅ Calculates average and warns if far from target (35 words)
- ✅ Shows min/max/avg statistics

### 2. **Question Count Validation**
- ✅ Enforces 5-10 questions per FAQ
- ✅ Detects too few or too many questions

### 3. **Technical Intensity Validation**
- ✅ Validates Level 3 (Moderate) technical terminology
- ✅ Counts moderate technical terms (substrate, corrosion, etc.)
- ✅ Detects overly advanced terms (chemical formulas, etc.)
- ✅ Warns if technical content too low (<1 term/answer)

### 4. **Voice Marker Validation** ⭐ **KEY FEATURE**
- ✅ Validates country-specific voice markers
- ✅ Detects over-used markers (>50% usage = CRITICAL ERROR)
- ✅ Checks marker diversity (should use 3+ different markers)
- ✅ Supports all 4 countries: Italy, Taiwan, Indonesia, USA

### 5. **Repetition Detection** ⭐ **KEY FEATURE**
- ✅ Detects over-repeated phrases (>50% = CRITICAL ERROR)
- ✅ Identifies monotonous sentence structures
- ✅ Calculates variation score
- ✅ Flags identical sentence openings

### 6. **Material Specificity**
- ✅ Ensures questions mention material name
- ✅ Detects generic questions (not material-specific)
- ✅ Calculates specificity score

## Usage

### Basic Usage
```bash
# Validate without voice checking
python3 scripts/validation/validate_faq_output.py Steel

# Validate with voice profile
python3 scripts/validation/validate_faq_output.py Granite --author Taiwan
python3 scripts/validation/validate_faq_output.py Steel --author Italy

# Quiet mode (minimal output)
python3 scripts/validation/validate_faq_output.py Granite --author Taiwan --quiet

# Fail-fast mode (exit on first error)
python3 scripts/validation/validate_faq_output.py Granite --author Taiwan --fail-fast
```

### Author Options
- `--author Italy` - Italian voice (craftsmanship-focused)
- `--author Taiwan` - Taiwan voice (research-focused)
- `--author Indonesia` - Indonesian voice (balance-focused)
- `--author "United States"` - USA voice (innovation-focused)

## Validation Results

### Steel FAQ (Italy) - Score: 55/100 ❌
**Errors:**
- ❌ Over-used voice markers: meticulous (86%), precision (57%)

**Warnings:**
- ⚠️ Average word count (23.6) deviates from target (35)

**Passed:**
- ✅ Question count (7)
- ✅ Technical intensity (1.0 terms/answer)
- ✅ No phrase repetition
- ✅ 100% material specificity

### Granite FAQ (Taiwan) - Score: 0/100 ❌ **CRITICAL ISSUES**
**Errors:**
- ❌ Q5: Too short (19 words)
- ❌ Q6: Too short (18 words)
- ❌ **CRITICAL: Over-used voice markers: systematic (100%), precise (100%), methodology (86%)**
- ❌ **CRITICAL: Over-repeated phrases: "systematic methodology" (57%), "laser cleaning" (57%)**

**Warnings:**
- ⚠️ Average word count (20.9) deviates from target (35)
- ⚠️ Low technical content (0.4 terms/answer, expected 1-2)

**Passed:**
- ✅ Question count (7)
- ✅ 100% material specificity

## Configuration

### Quality Thresholds
```python
MIN_WORDS = 20
MAX_WORDS = 50
TARGET_AVG_WORDS = 35

MIN_QUESTIONS = 5
MAX_QUESTIONS = 10

MAX_SINGLE_MARKER_USAGE = 0.50  # 50% maximum per marker
IDEAL_MARKER_RANGE = (0.20, 0.40)  # 20-40% is ideal
MAX_PHRASE_REPETITION = 0.50  # 50% maximum phrase repetition

MIN_QUALITY_SCORE = 70  # Out of 100
```

### Scoring System
- **Critical Errors**: -20 points each
- **Warnings**: -5 points each
- **Minimum Passing Score**: 70/100

## Voice Profiles

### Italy (Craftsmanship-focused)
**Markers**: meticulous, precision, finesse, artisan, craftsmanship, refined, elegant, delicate, excellence, preserving, integrity

**Character**: Refined execution with attention to detail

### Taiwan (Research-focused)
**Markers**: systematic, methodology, research-based, framework, comprehensive, precise, calibration, ensures, rigorous

**Character**: Systematic approach with methodological rigor

### Indonesia (Balance-focused)
**Markers**: harmonious, balanced, thoughtful, considerate, sustainable, mindful, respectful, careful

**Character**: Sustainability and balance emphasis

### United States (Innovation-focused)
**Markers**: innovative, performance, advanced, cutting-edge, breakthrough, optimize, maximize, superior, state-of-the-art

**Character**: Performance and innovation emphasis

## Key Findings

### ✅ What Works Well
1. Material specificity (100% in both FAQs)
2. Question count compliance
3. Sentence structure variation (unique openings)

### ❌ Critical Issues Detected
1. **Voice marker over-use** - Taiwan profile has 100% usage (should be 20-40%)
2. **Phrase repetition** - "systematic methodology" in 57% of answers
3. **Low technical content** - Granite FAQ has only 0.4 terms/answer (needs 1-2)
4. **Word count** - Both FAQs averaging low (20-24 words vs target 35)

### 🔧 Recommended Fixes
1. **Reduce voice enhancement intensity** for Taiwan profile
2. **Increase word count targets** to hit 30-40 word average
3. **Add more technical terminology** to Granite FAQ
4. **Improve marker distribution** - use more variety, less repetition

## Integration with Project

This validation script enforces:
- ✅ Project word count requirements (FAQ_WORD_COUNT_RANGE)
- ✅ Technical intensity settings (FAQ_TECHNICAL_INTENSITY)
- ✅ Voice intensity guidelines (FAQ_VOICE_INTENSITY)
- ✅ Quality standards from GROK_INSTRUCTIONS.md
- ✅ Fail-fast architecture (zero tolerance for critical errors)

## Exit Codes
- `0` - Validation passed (score >= 70/100, no errors)
- `1` - Validation failed (score < 70/100 or errors present)
