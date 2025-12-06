# Author Personas

**Author voice profiles defining HOW to write - linguistic patterns, cultural nuances, and writing styles.**

---

## 📋 Purpose

Persona files define **authentic author voices** that make generated content feel human-written. Each persona represents a real-world English-as-Second-Language (ESL) author with:
- Regional linguistic patterns
- Cultural communication styles  
- Technical writing approaches
- Natural imperfections and quirks

**Key Principle**: Personas capture the subtle ways non-native English speakers write technical content - NOT stereotypes, but linguistic authenticity.

---

## 🌍 Available Personas

### united_states.yaml
**Profile**: American academic/technical writer  
**English**: Native speaker  
**Style**: Formal, balanced, methodical

**Characteristics**:
- Clean, direct technical prose
- Balanced active/passive voice usage
- Academic structure with clear organization
- Precise vocabulary choices
- Occasional contractions in conversational contexts

**Best For**: Materials requiring authoritative, formal technical documentation

---

### italy.yaml  
**Profile**: Italian engineer/researcher  
**English**: EFL (English as Foreign Language)  
**Style**: Technical precision with subtle European markers

**Characteristics**:
- High technical accuracy (engineering background)
- Slight formality in sentence structure
- Occasional article flexibility (0.3-0.5 per paragraph)
- European punctuation preferences (spacing around colons)
- Complex sentence constructions (Romance language influence)

**ESL Patterns** (Authentic, Not Errors):
- "Material demonstrates properties" (article omission)
- "Process requires temperature of 800°C" (of + measurement)
- Slightly formal phrasing ("one observes" vs "you see")

**Best For**: Materials needing technical depth with international perspective

---

### indonesia.yaml
**Profile**: Indonesian technical writer  
**English**: ESL (Southeast Asian education system)  
**Style**: Natural accessibility with light regional markers

**Characteristics**:
- Clear, practical explanations
- Friendly, approachable tone
- Occasional preposition variation
- Topic-prominent sentence structures (Asian language influence)
- Focus on real-world applications

**ESL Patterns** (Authentic, Not Errors):
- "For cleaning aluminum, technique uses..." (topic-first)
- "Process can achieve good result" (article variation)
- "Material is suitable for industrial application" (singular/plural flexibility)

**Best For**: Materials requiring practical, user-friendly explanations

---

### taiwan.yaml
**Profile**: Taiwanese technical professional  
**English**: ESL (East Asian technical education)  
**Style**: Concise technical with formal undertones

**Characteristics**:
- Economical word usage (Chinese influence)
- High information density
- Formal technical register
- Precise numerical data emphasis
- Structured, logical progression

**ESL Patterns** (Authentic, Not Errors):
- "System achieves 95% efficiency" (direct, no articles)
- "Material provides benefit in application" (concise phrasing)
- Topic-prominent constructions
- Passive voice preference in technical contexts

**Best For**: Materials needing concise, data-driven technical content

---

## 📝 File Format

Persona files use **YAML** with abstract pattern notation:

```yaml
name: "Author Name"
country: "Country"
esl_level: "native" | "fluent_efl" | "fluent_esl"
style_notes: |
  High-level description of writing approach and philosophy.
  
linguistic_patterns:
  - category: "Pattern Category"
    description: "What this pattern represents"
    examples:
      - "Concrete example of the pattern"
      - "Another example showing variation"
    frequency: "how_often"  # rarely, occasionally, moderate, frequent
    
  - category: "Another Category"
    ...

voice_instructions: |
  Direct instructions for applying this voice during generation.
  Written as if instructing a writer to adopt this style.
  
  - Specific guidance on sentence structure
  - Vocabulary preferences
  - Tone and formality level
  - ESL patterns to naturally incorporate
```

---

## 🔍 Abstract Pattern Notation

Patterns use **abstract notation** to describe linguistic structures without hardcoding specific text:

| Notation | Meaning | Example |
|----------|---------|---------|
| `X does Y` | Subject-verb-object structure | "Material exhibits properties" |
| `{measurement}` | Numeric data placeholder | "2.7 g/cm³", "800°C" |
| `[article] + noun` | Optional article pattern | "[the] material", "process" |
| `A while B` | Conjunction pattern | "heating while maintaining" |

**Why Abstract**: Patterns describe STRUCTURE, not content. This allows the AI to generate varied text following the pattern without repetition.

**Example**:
```yaml
examples:
  - "Material demonstrates {property} in {application}"
  - "Process achieves {result} through {method}"
  - "[the] technique provides {benefit} for {use_case}"
```

These generate infinite variations like:
- "Steel demonstrates hardness in construction"
- "Laser achieves precision through controlled energy"
- "Technique provides efficiency for industrial cleaning"

---

## 🎯 ESL Authenticity vs Errors

**IMPORTANT**: ESL patterns are **authentic linguistic features**, NOT mistakes to correct.

### ✅ Authentic ESL Patterns (Keep These):
- Article flexibility: "Material shows properties" 
- Preposition variation: "suitable for application"
- Formal phrasing: "one observes that..."
- Topic-prominent: "For aluminum, process uses..."

### ❌ Actual Errors (Fix These):
- Subject-verb agreement: "material show" ❌
- Tense errors: "material will shows" ❌
- Word order: "properties material of" ❌
- Incorrect vocabulary: "material mades" ❌

**Goal**: Write like a **fluent non-native speaker**, not a beginner making grammar mistakes.

---

## 🔧 How Personas Are Applied

Personas are **automatically loaded** based on material's assigned author:

1. **Material Assignment**: Each material in `Materials.yaml` has `author.id` (1-4)
   ```yaml
   name: Aluminum
   author:
     id: 2  # Maps to Italy
   ```

2. **Persona Loading**: `processing/voice/store.py` loads corresponding persona
   ```python
   author_id = material['author']['id']  # 2
   persona = load_persona(author_id)     # italy.yaml
   ```

3. **Voice Injection**: `processing/generation/prompt_builder.py` injects voice instructions
   ```
   {voice_instructions} → Full voice_instructions field from YAML
   ```

4. **API Generation**: Combined prompt (component + voice + rules) sent to API

**Result**: Generated content naturally reflects author's linguistic patterns.

---

## ➕ Adding New Personas

To create a new author persona:

1. **Create YAML file** in `prompts/personas/`:
   ```bash
   touch prompts/personas/new_country.yaml
   ```

2. **Define persona structure**:
   ```yaml
   name: "Author Name"
   country: "Country"
   esl_level: "fluent_esl"  # or "native", "fluent_efl"
   
   style_notes: |
     Overall writing philosophy and approach.
   
   linguistic_patterns:
     - category: "Sentence Structure"
       description: "How this author constructs sentences"
       examples:
         - "Abstract pattern example"
       frequency: "moderate"
   
   voice_instructions: |
     Write as [description of author].
     - Specific instruction 1
     - Specific instruction 2
   ```

3. **Assign to materials** in `Materials.yaml`:
   ```yaml
   name: SomeMaterial
   author:
     id: 5  # New persona ID
     name: "New Author Name"
     country: "New Country"
   ```

4. **Test generation**:
   ```bash
   python3 run.py --material "SomeMaterial" --component subtitle
   ```

---

## ✏️ Editing Personas

### To Update Existing Persona:
1. **Edit YAML file**:
   ```bash
   vim prompts/personas/italy.yaml
   ```

2. **Test with assigned materials**:
   ```bash
   # Find materials assigned to this author
   grep -A 3 '"id": 2' data/materials/Materials.yaml | head -20
   
   # Test generation
   python3 run.py --material "Aluminum" --component subtitle
   ```

3. **Validate voice consistency**:
   - Does output reflect the voice changes?
   - Are ESL patterns appearing naturally?
   - Is AI detection still passing (< 0.10)?

4. **No deployment needed** - changes apply immediately

### Common Edits:
- **Adjust ESL frequency**: Change from "occasional" to "rare" for subtler patterns
- **Add new patterns**: Expand linguistic_patterns with new categories
- **Refine instructions**: Make voice_instructions more specific
- **Update style notes**: Document voice evolution

---

## 🚫 What NOT to Include

**NEVER put these in persona files**:
- ❌ Component-specific instructions (word counts, formats) → Use `prompts/components/`
- ❌ Universal rules (anti-AI patterns) → Use `prompts/rules/`
- ❌ API parameters (temperature, penalties) → Use `processing/config.yaml`
- ❌ Material-specific content → Use `Materials.yaml`
- ❌ Hardcoded text to copy → Use abstract patterns

**WHY**: Personas define HOW to write (voice/style), not WHAT to write (content/rules).

---

## 📊 Persona Validation

Persona effectiveness measured by:

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| AI Detection | < 0.10 | Winston AI ensemble scoring |
| Voice Consistency | Distinctive | Human evaluation of author recognizability |
| ESL Authenticity | Natural | Linguistic pattern frequency analysis |
| Technical Accuracy | High | Expert review of generated content |

**Tools**:
- `processing/detection/ensemble.py` - AI detection scoring
- `processing/tests/test_e2e_pipeline.py` - Automated voice validation

---

## 🎯 Best Practices

1. **Research Real Patterns**: Base ESL features on actual non-native speaker writing
   - Read technical papers from authors in that region
   - Note authentic linguistic patterns
   - Avoid stereotypes or caricatures

2. **Balance Authenticity & Clarity**: ESL patterns should feel natural, not hinder comprehension
   - ✅ Subtle article flexibility
   - ❌ Confusing grammar that obscures meaning

3. **Use Abstract Notation**: Describe patterns, don't hardcode text
   - ✅ "Material shows {property}" (template)
   - ❌ "Steel shows hardness" (specific text)

4. **Test Across Components**: Voice should work for ALL content types
   - Subtitle (15 words)
   - Caption (25 words)
   - Description (150 words)
   - FAQ (100 words)

5. **Maintain Distinctiveness**: Each persona should be recognizable
   - Different enough to feel like different authors
   - Consistent enough to feel like one author across materials

---

## 🔗 Related Documentation

- **Parent**: `prompts/README.md` - Overview of entire prompt system
- **Components**: `prompts/components/README.md` - Task specifications (what to generate)
- **Rules**: `prompts/rules/README.md` - Universal constraints (what to avoid)
- **Code**: `processing/voice/store.py` - Persona loading logic
- **Assignment**: `data/materials/Materials.yaml` - Material-author mappings

---

## 🚀 Quick Commands

**View a persona**:
```bash
cat prompts/personas/italy.yaml
```

**Edit a persona**:
```bash
vim prompts/personas/italy.yaml  # or use your preferred editor
```

**Find materials assigned to author**:
```bash
# Author ID 2 (Italy)
grep -A 3 '"id": 2' data/materials/Materials.yaml | grep 'name:' | head -10
```

**Test persona changes**:
```bash
python3 run.py --material "Aluminum" --component subtitle
```

**Compare all 4 authors**:
```bash
# Generate same component for materials with different authors
python3 run.py --material "Steel" --component caption      # USA
python3 run.py --material "Aluminum" --component caption   # Italy
python3 run.py --material "Copper" --component caption     # Indonesia
python3 run.py --material "Titanium" --component caption   # Taiwan
```

**Validate voice consistency**:
```bash
# Run E2E tests across all authors
python3 processing/tests/test_e2e_pipeline.py
```

---

## 📈 Persona Evolution

Personas are refined based on:
1. **AI Detection Results**: If scores rise, adjust patterns for more authenticity
2. **Voice Distinctiveness**: Ensure authors feel different from each other
3. **ESL Research**: Incorporate newly discovered authentic patterns
4. **User Feedback**: Real-world usage reveals what feels natural

**History**: See git log for `prompts/personas/*.yaml` to track persona evolution.

---

## 🌍 Cultural Sensitivity

**Guidelines for Authentic Personas**:
- ✅ **Base on Linguistic Research**: Real patterns from technical writing in that region
- ✅ **Respect Fluency**: Authors are highly educated technical professionals
- ✅ **Celebrate Diversity**: Different communication styles are valuable, not deficient
- ❌ **Avoid Stereotypes**: Don't exaggerate or caricature regional speech
- ❌ **No "Broken English"**: Authors are fluent, just with different patterns

**Goal**: Authentic representation of how skilled technical professionals write in English as a second language.
