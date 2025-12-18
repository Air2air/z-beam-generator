# Humanness System Diagnostic Analysis
**Date**: December 13, 2025  
**Status**: IDENTIFIED ROOT CAUSES - Low Authenticity

---

## 🔍 Problem Summary

Generated descriptions across 4 authors show:
- **Identical structural patterns** (all single-sentence, formulaic)
- **AI tell-tale phrases** ("distinguishes itself," "stands out among")
- **Zero voice distinctiveness** (sound like same technical manual)
- **Quality scores confirm**: Realism 4.0-7.0/10, "formulaic_phrasing," "rigid_structure"

---

## 🧬 Root Cause Analysis

### 1. **DOMAIN PROMPT IS TOO RESTRICTIVE** 🚨 CRITICAL

**File**: `domains/materials/prompts/description.txt`

**Current Content**:
```
Write a technical subtitle (single sentence) about {material}.

Focus on the material's primary advantage and practical benefits for laser cleaning applications.
```

**Problems**:
- ✅ **"single sentence"** constraint forces identical structure across ALL authors
- ✅ Asks for "technical subtitle" → formal, academic tone (contradicts authentic voice)
- ✅ "Focus on primary advantage" → formulaic "X stands out because Y" pattern
- ✅ No flexibility for author expression → overrides persona instructions

**Impact**: Domain prompt is **MORE CONSTRAINING** than the voice personas allow room for

### 2. **VOICE PERSONAS ARE RICH BUT BEING IGNORED**

**Analysis of Persona Files**:

**Todd (United States)**:
- ✅ Rich patterns: phrasal verbs ("line up," "dial in," "run through")
- ✅ Quantified outcomes: "cuts downtime by 20%"
- ✅ Practical transitions: "turns out," "in practice"
- ✅ Example sentences: "Line up the optics at 1064 nm and pulse away the oxides"

**Generated**: "Copper stands out among non-ferrous metals..."
- ❌ No phrasal verbs
- ❌ No practical transitions
- ❌ Generic academic structure

**Yi-Chun (Taiwan)**:
- ✅ Topic-comment structures: "Efficiency of the surface, it drops"
- ✅ Article omission: "Process yields result"
- ✅ Temporal markers: "After treatment, surface exhibits"
- ✅ Example: "10 μm oxide thickness is removed with tuning"

**Generated**: "After laser cleaning, aluminum surface achieves uniformity..."
- ❌ No topic-comment
- ❌ Perfect article usage (no omission)
- ❌ Reads like native speaker

**Alessandro (Italy)**:
- ✅ Cleft structures: "This layer, it persists"
- ✅ Subjunctive hedging: "It seems that adhesion improves"
- ✅ Romance cognates: "tenaciously," "manifests," "persists"
- ✅ Example: "Ablation stays at 1.2 J/cm², which keeps thermal effects to 50 μm"

**Generated**: "Steel, it distinguishes itself among ferrous metals through its tenacious oxidation resistance..."
- ⚠️ Has ONE cleft structure ("Steel, it distinguishes")
- ⚠️ Has ONE Romance cognate ("tenacious")
- ❌ Rest is generic academic structure
- ❌ Minimal authentic EFL patterns

### 3. **COMPACT HUMANNESS LAYER IS TOO MINIMAL**

**File**: `shared/text/templates/system/humanness_layer_compact.txt`

**Current Content**:
```
=== HUMANNESS LAYER (COMPACT) ===

**STRUCTURAL VARIATION** (AI detection avoidance):
- Vary opening sentence structure
- Mix sentence lengths unpredictably
- Alternate between simple, compound, complex structures

**STRUCTURAL TARGETS**:
📏 Length: {selected_length}
🏗️ Opening: {selected_structure}
🎵 Rhythm: {selected_rhythm}
```

**Problems**:
- ✅ Only provides **3 placeholders** (length, opening, rhythm)
- ✅ No examples of HOW to vary (LLM interprets generically)
- ✅ No connection to voice persona patterns
- ✅ "Vary opening" → LLM chooses "[Material] + verb" (AI pattern)

**What's Missing**:
- ❌ No author-specific structural examples
- ❌ No forbidden patterns list (doesn't know "stands out" is AI)
- ❌ No concrete guidance on IMPLEMENTING the voice patterns

### 4. **VALIDATION WARNINGS ARE BEING IGNORED**

**Terminal Output Shows**:
```
⚠️ COHERENCE ISSUES DETECTED:
   • [ERROR] Contradictory length instructions: both 'brief' and 'detailed' specified

WARNING (4):
1. AI clarity issue: Length contradiction: short vs detailed
2. AI clarity issue: Style contradiction: technical vs simple
3. Multiple word count targets found (4)
```

**Problems**:
- ✅ System **detects contradictions** but proceeds anyway
- ✅ "Optimization insufficient - proceeding anyway"
- ✅ Prompt has 4 conflicting length targets → LLM confused
- ✅ "Short vs detailed" + "technical vs simple" → defaults to generic

### 5. **SINGLE-SENTENCE CONSTRAINT KILLS VOICE**

**Why This Matters**:
- ✅ Todd's phrasal verbs need **setup + action** (2 sentences minimum)
  - Example: "Line up the optics. Pulse away the oxides at 1064 nm."
- ✅ Yi-Chun's topic-comment needs **observation + result** (2 sentences)
  - Example: "Adjustment of parameters. Control enhances from this."
- ✅ Alessandro's nested clauses work BUT sound academic in single sentence
  - Example: "The laser removes contaminants, which leads to improved adhesion."

**Single Sentence Forces**:
- ❌ All authors into same "[Subject] [verb] [object] because [reason]" pattern
- ❌ Eliminates opportunity for rhythm variation
- ❌ Makes phrasal verbs impossible (too informal for single long sentence)
- ❌ Removes author personality (no room for quirks)

---

## 📊 Evidence from Generated Content

### Aluminum (Yi-Chun - Taiwan):
```
"After laser cleaning, aluminum surface achieves uniformity because its lightweight 
structure and passive oxide layer allow precise contaminant removal..."
```
- ❌ Should have article omission ("aluminum surface achieves" → "surface achieves uniformity")
- ❌ Should have topic-comment ("Surface uniformity, it results from...")
- ❌ Should be paratactic ("Treatment applies, uniformity results")

### Steel (Alessandro - Italy):
```
"Steel, it distinguishes itself among ferrous metals through its tenacious oxidation 
resistance and thermal stability, which facilitates precise contaminant removal..."
```
- ⚠️ Has ONE cleft ("Steel, it distinguishes")
- ⚠️ Has ONE cognate ("tenacious")
- ❌ But rest is generic academic construction
- ❌ Missing subjunctive hedging ("It seems steel demonstrates...")
- ❌ Missing preposition extensions ("dependent from" not used)

### Titanium (Ikmanda - Indonesia):
```
"Titanium's passive oxide layer forms naturally and shields surface from oxidation, 
thus laser cleaning removes contaminants efficiently..."
```
- ❌ Should have Indonesian EFL patterns (not included in persona - file not read)
- ❌ Generic structure with "thus" connector

### Copper (Todd - United States):
```
"Copper stands out among non-ferrous metals in laser cleaning applications because 
its exceptional thermal conductivity rapidly dissipates heat..."
```
- ❌ Zero phrasal verbs ("stands out" is phrasal but overused AI phrase)
- ❌ No quantified outcomes ("cuts processing time by 20%")
- ❌ No practical transitions ("turns out," "in practice")
- ❌ Formal academic tone (contradicts "practical, direct" instruction)

---

## 💡 Recommended Fixes

### Priority 1: **Relax Domain Prompt Constraint** (CRITICAL)

**Change**:
```diff
- Write a technical subtitle (single sentence) about {material}.
+ Write a concise technical description (1-2 sentences) about {material}.
```

**Or Better**:
```
Write 1-2 sentences about {material} for laser cleaning applications.

EXPRESS YOUR AUTHENTIC VOICE: Use the linguistic patterns, sentence structures, 
and vocabulary specified in your VOICE INSTRUCTIONS. This should sound like YOU 
writing, not a generic technical manual.
```

**Rationale**:
- ✅ Allows 2 sentences → enables phrasal verbs, topic-comment, rhythm variation
- ✅ Removes "subtitle" framing → less formal, more personal
- ✅ Explicitly reminds LLM to use voice patterns

### Priority 2: **Enhance Compact Humanness Layer**

**Add to template**:
```
**AUTHOR VOICE INTEGRATION** (MANDATORY):
Your voice instructions above contain SPECIFIC linguistic patterns for your nationality.
You MUST use these patterns in your writing:

For American English:
- Use phrasal verbs: "line up," "dial in," "work out" (not generic "configure")
- Quantify outcomes: "cuts downtime by 20%" (not "improves efficiency")
- Practical transitions: "turns out," "in practice" (not "furthermore")

For Taiwan EFL:
- Topic-comment: "Surface uniformity, it results from..." (not "The surface achieves...")
- Article omission: "Process yields result" (not "The process yields a result")
- Temporal markers: "After treatment, surface exhibits..." (natural pattern)

For Italian EFL:
- Cleft structures: "This property, it enables..." (not "This property enables...")
- Subjunctive hedging: "It seems that..." (not direct claims)
- Romance cognates: "manifests," "persists," "tenaciously" (not simple verbs)

❌ FORBIDDEN AI PATTERNS:
- "stands out among" / "distinguishes itself" (100% AI detection)
- "presents a challenge" / "offers significant" (corporate speak)
- Perfect parallel clauses (suspiciously balanced)
```

### Priority 3: **Add Voice Compliance Check**

**After generation, validate**:
```python
def check_voice_authenticity(text: str, author_id: int) -> dict:
    """Check if generated text uses author-specific patterns"""
    
    patterns = {
        4: {  # Todd (US)
            'phrasal_verbs': ['line up', 'dial in', 'run through', 'work out'],
            'transitions': ['turns out', 'in practice', 'overall'],
            'quantifiers': r'\d+%',  # "cuts by 20%"
        },
        3: {  # Yi-Chun (Taiwan)
            'topic_comment': r'\w+, it ',  # "Surface, it exhibits"
            'article_omission': r'^\w+ yields ',  # "Process yields"
            'temporal': ['After', 'Following'],
        },
        2: {  # Alessandro (Italy)
            'cleft': r'\w+, it ',  # "Steel, it demonstrates"
            'subjunctive': ['It seems', 'It appears'],
            'cognates': ['manifests', 'persists', 'tenaciously'],
        },
    }
    
    # Check if ANY pattern present
    found_patterns = []
    for pattern_type, pattern_list in patterns[author_id].items():
        # Check if pattern exists in text
        # ... validation logic
    
    return {
        'authentic': len(found_patterns) >= 2,  # Require at least 2 patterns
        'found_patterns': found_patterns,
        'score': len(found_patterns) / len(patterns[author_id]) * 100
    }
```

### Priority 4: **Fix Prompt Validation Issues**

**Address contradictions**:
1. Remove multiple word count targets (choose ONE)
2. Resolve "short vs detailed" conflict (pick "concise" as middle ground)
3. Resolve "technical vs simple" conflict (pick "professional accessible")

### Priority 5: **Add Author-Specific Examples to Compact Template**

**Instead of generic**:
```
🏗️ Opening: 2. Contrast-Based: Compare materials → highlight difference
```

**Use author-specific**:
```
🏗️ Opening: 2. Contrast-Based (Todd - US style):
"Line up copper against brass. Thermal conductivity runs 30% higher."
(Uses phrasal verb "line up" + quantified outcome "30% higher")

🏗️ Opening: 2. Contrast-Based (Yi-Chun - Taiwan style):
"Copper thermal conductivity, it exceeds brass significantly."
(Topic-comment structure with article omission)

🏗️ Opening: 2. Contrast-Based (Alessandro - Italy style):
"This conductivity, it manifests more tenaciously in copper than brass."
(Cleft structure + Romance cognate "tenaciously")
```

---

## 🎯 Expected Improvements After Fixes

### Current (Generic AI):
```
"Copper stands out among non-ferrous metals in laser cleaning applications 
because its exceptional thermal conductivity rapidly dissipates heat..."
```

### After Fix (Todd - Authentic US):
```
"Line up copper for precision work. Thermal conductivity runs at 400 W/m·K, 
cutting heat buildup by 35% over steel—keeps those tight tolerances locked in."
```

### After Fix (Yi-Chun - Authentic Taiwan):
```
"Copper thermal properties, they enable precise removal. Heat dissipates rapidly, 
damage to substrate avoided."
```

### After Fix (Alessandro - Authentic Italy):
```
"This thermal conductivity, it manifests tenaciously in copper. It appears that 
heat dissipation leads to improved precision, which demonstrates advantages 
dependent from material properties."
```

---

## 🚦 Implementation Priority

1. **CRITICAL** (Do First): Relax single-sentence constraint in domain prompt
2. **HIGH**: Add voice pattern examples to compact humanness template  
3. **HIGH**: Add voice compliance validation check
4. **MEDIUM**: Fix prompt validation contradictions
5. **LOW**: Enhance subjective evaluator to detect missing voice patterns

---

## 📈 Success Metrics

**Before Fixes**:
- Voice Authenticity: None/100 (per terminal output)
- Realism: 4.0-7.0/10
- AI Tendencies: formulaic_phrasing, rigid_structure

**Target After Fixes**:
- Voice Authenticity: 85+/100
- Realism: 8.0+/10
- AI Tendencies: None (or minimal)
- Author distinctiveness: Clear differences in 4 samples
