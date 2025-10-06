# AI-Evasion Testing Quick Reference

## Quick Commands

### Test All 4 Authors
```bash
python3 scripts/test_ai_evasion.py --all
```

### Test Specific Material
```bash
python3 scripts/test_ai_evasion.py --material Bamboo
python3 scripts/test_ai_evasion.py --material Bronze
python3 scripts/test_ai_evasion.py --material Alumina
python3 scripts/test_ai_evasion.py --material Aluminum
```

### Verbose Mode (Show Caption Samples)
```bash
python3 scripts/test_ai_evasion.py --all --verbose
```

---

## Metrics Explained

### 📏 Sentence Length Distribution
**What it measures:** Variety in sentence lengths (anti-monotony)

**Targets:**
- Very Short (5-8 words): 15-20%
- Medium (10-18 words): 30-40%
- Long (20-28 words): 30-40%
- Very Long (30+ words): 10-20%

**Status Levels:**
- ✓ PASS: Medium sentences <50% (good variety)
- ⚠ WARN: Medium sentences 50-70% (too uniform)
- ❌ FAIL: Medium sentences >70% (monotonous)

### 🎭 AI-Evasion Markers
**What it measures:** Natural human writing imperfections

**Includes:**
- Hesitation markers (—, "or", "perhaps", "approximately")
- Parenthetical asides (additional information)
- Comma splices (informal punctuation)

**Status Levels:**
- ✓ PASS: 3+ markers total
- ⚠ WARN: 1-2 markers
- ❌ FAIL: 0 markers

### 📚 Lexical Variety
**What it measures:** Vocabulary richness (unique words / total words)

**Targets:**
- Taiwan/Indonesia/USA: ≥60%
- Italy: ≥70% (sophisticated vocabulary)

**Status Levels:**
- ✓ PASS: ≥65%
- ⚠ WARN: 60-64%
- ❌ FAIL: <60%

### 🗣️ Author-Specific Patterns

**Taiwan:**
- Topic-comment count (≥2 instances)
- Article omissions (≥70% of opportunities)

**Indonesia:**
- Emphatic repetition (very-very patterns)
- Demonstrative starts (≥50% sentences start with "This")

**Italy:**
- Passive voice (≥3 instances in caption)
- Nested clauses (high comma density)

**USA:**
- Phrasal verbs (≥3 instances)
- Active voice dominance (≥85%)

---

## Reading the Output

### Sample Output
```
BAMBOO - Taiwan (Yi-Chun Lin)
================================================================================

📊 BASIC METRICS:
  Total Sentences: 8
  Total Words: 117
  Avg Sentence Length: 15.4 words

📏 SENTENCE LENGTH DISTRIBUTION:
  Very Short 5 8: 0/8 (0.0%)        ← Need more variety
  Medium 10 18: 4/8 (50.0%)         ← Too many medium
  Long 20 28: 2/8 (25.0%)
  Very Long 30Plus: 0/8 (0.0%)      ← Need some long sentences

🎭 AI-EVASION MARKERS:
  Hesitation Markers: 0              ← NEEDS IMPROVEMENT
  Parentheticals: 0                  ← NEEDS IMPROVEMENT
  Comma Splices: 2                   ← Good

📚 LEXICAL VARIETY:
  Unique/Total: 87/117
  Ratio: 74.36%                      ← EXCELLENT

🗣️ AUTHOR-SPECIFIC PATTERNS (TAIWAN):
  Topic Comment Count: 2             ← GOOD
  Article Omissions: 1               ← Needs improvement (target 70%)

✅ TARGET EVALUATION:
  Sentence Variation: ⚠ WARN - Too many medium sentences
  Lexical Variety: ✓ PASS - Excellent variety
  Evasion Markers: ❌ FAIL - No natural markers
  No Emotives: ✓ PASS - Zero emotives
  Taiwan Patterns: ✓ PASS - Topic-comment present
```

### What to Fix
1. **❌ FAIL** items are critical - must be addressed
2. **⚠ WARN** items should be improved
3. **✓ PASS** items are meeting targets

---

## Common Issues & Fixes

### Issue: "Too many medium sentences"
**Cause:** AI generates uniform 15-20 word sentences  
**Fix:** Add sentence length variation rules to prompt  
**Target:** Mix of 5-8, 10-18, 20-28, 30+ word sentences

### Issue: "No natural markers"
**Cause:** AI writes too cleanly without human imperfections  
**Fix:** Add hesitation markers and parentheticals to prompt  
**Target:** 1.5 markers per 200 words

### Issue: "Low [author pattern]"
**Cause:** Voice instructions not strong enough  
**Fix:** Increase frequency parameter for that author  
**Example:** Indonesia demonstrative_clustering_rate: 50% → 60%

### Issue: "Too repetitive"
**Cause:** Low lexical variety (reusing same words)  
**Fix:** Increase lexical_variety_target  
**Target:** >65% unique words

---

## Interpreting Summary Table

```
Material    Country      Sentences  Lexical    Emotives
Bamboo      Taiwan       8          74.36%     ✓ PASS
Bronze      Indonesia    8          80.88%     ✓ PASS
Alumina     Italy        7          71.77%     ✓ PASS
Aluminum    USA          7          76.47%     ✓ PASS
```

**Key columns:**
- **Sentences:** Caption length (7-10 is typical)
- **Lexical:** Vocabulary richness (higher = better)
- **Emotives:** Must be PASS (zero emotives required)

---

## What Makes a Good Caption?

### ✅ Must Have (Critical)
1. Zero emotives (remarkable, innovative, elegant, etc.)
2. Lexical variety >60%
3. Technical accuracy (measurements present)
4. Author voice recognizable

### ✅ Should Have (Important)
1. Sentence length variation (not all medium)
2. AI-evasion markers (hesitations, parentheticals)
3. Author-specific patterns present
4. Measurement precision variation

### ⚠️ Nice to Have (Optional)
1. Comma splices (1 per 100 words)
2. Very long sentences (30+ words)
3. Multiple hesitation types

---

## Benchmarks

### Current Baseline (Pre-Enhancement)
- **Emotives:** 100% pass rate ✅
- **Lexical variety:** 100% pass rate ✅
- **Sentence variation:** 25% pass rate ⚠️
- **AI-evasion markers:** 25% pass rate ⚠️
- **Author patterns:** 50-75% pass rate ⚠️

### Target (Post-Enhancement)
- **Emotives:** 100% pass rate ✅
- **Lexical variety:** 100% pass rate ✅
- **Sentence variation:** 75%+ pass rate ✅
- **AI-evasion markers:** 75%+ pass rate ✅
- **Author patterns:** 90%+ pass rate ✅

---

## Testing Workflow

### Before Making Changes
```bash
# Establish baseline
python3 scripts/test_ai_evasion.py --all > baseline.txt
```

### After Making Changes
```bash
# Test new captions
python3 scripts/test_ai_evasion.py --all > after_changes.txt

# Compare
diff baseline.txt after_changes.txt
```

### For Specific Author
```bash
# Generate new caption
python3 scripts/generate_caption_to_frontmatter.py --material Bamboo

# Test it immediately
python3 scripts/test_ai_evasion.py --material Bamboo
```

---

## Quick Checks

### Is the caption too AI-like?
```bash
# Check for these warning signs:
python3 scripts/test_ai_evasion.py --material Bamboo | grep "FAIL"
```

### Are all authors working?
```bash
# Test all 4 materials
python3 scripts/test_ai_evasion.py --all | grep "Emotives"
```

### What's the overall quality?
```bash
# Check summary table
python3 scripts/test_ai_evasion.py --all | tail -10
```

---

## Files Referenced

### Voice Profiles (with ai_evasion_parameters)
- `voice/profiles/taiwan.yaml`
- `voice/profiles/indonesia.yaml`
- `voice/profiles/italy.yaml`
- `voice/profiles/united_states.yaml`

### Testing
- `scripts/test_ai_evasion.py` - Main testing tool
- `tests/test_voice_integration.py` - Unit tests

### Documentation
- `voice/ENHANCEMENT_RULES_SEO_AI_DETECTION.md` - Full rules
- `voice/IMPLEMENTATION_GUIDE.md` - Step-by-step guide
- `voice/IMPLEMENTATION_COMPLETE.md` - Implementation summary
- `voice/QUICK_REFERENCE_TESTING.md` - This document

---

## Troubleshooting

### Script won't run
```bash
# Make sure it's executable
chmod +x scripts/test_ai_evasion.py

# Run with python3 explicitly
python3 scripts/test_ai_evasion.py --all
```

### "File not found" error
```bash
# Check if frontmatter file exists
ls content/components/frontmatter/ | grep bamboo

# Generate it first if missing
python3 scripts/generate_caption_to_frontmatter.py --material Bamboo
```

### Results look strange
```bash
# Check if caption exists in file
grep -A 5 "beforeText:" content/components/frontmatter/bamboo-laser-cleaning.yaml

# Verify YAML is valid
python3 -c "import yaml; yaml.safe_load(open('content/components/frontmatter/bamboo-laser-cleaning.yaml'))"
```

---

**Quick Start:** `python3 scripts/test_ai_evasion.py --all`  
**For Help:** `python3 scripts/test_ai_evasion.py --help`
