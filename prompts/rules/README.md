# Universal Rules

**Universal constraints defining WHAT TO AVOID in all generated content.**

---

## 📋 Purpose

Rule files enforce **universal constraints** that apply to ALL content generation, regardless of component type or author voice. They define:
- AI detection patterns to avoid
- Grammatical structures that feel unnatural
- Linguistic markers that signal machine-generated text
- Writing patterns that reduce content quality

**Key Principle**: Rules are NEGATIVE constraints (what NOT to do), while component prompts are POSITIVE specifications (what TO do).

---

## 📁 Available Rule Files

### anti_ai_rules.txt (2,192 chars)
**Purpose**: Prevent AI detection by avoiding machine-learning patterns

**Critical Rules**:
1. **No Formulaic Structures**
   - ❌ "X does Y while preserving Z"
   - ❌ "This enables A, facilitating B, and ensuring C"
   - ❌ "Key advantages include: X, Y, and Z"

2. **No Abstract Transitions**
   - ❌ "Results suggest...", "Data indicate..."
   - ❌ "Studies show...", "Research confirms..."
   - ❌ "Evidence demonstrates...", "Analysis reveals..."

3. **Vary Opening Words**
   - ❌ Starting multiple sentences with "The", "This", "These"
   - ✅ Mix sentence starters naturally
   - ✅ Use varied grammatical constructions

4. **Mix Sentence Lengths**
   - ❌ All sentences 15-20 words
   - ✅ Short punchy sentences (5-8 words)
   - ✅ Longer explanatory sentences (20-25 words)
   - ✅ Natural variation in rhythm

5. **Add Specific Details**
   - ❌ Generic descriptions ("excellent properties")
   - ✅ Concrete examples ("2.7 g/cm³ density")
   - ✅ Specific measurements and data points

6. **Use Natural Flow**
   - ❌ Robotic, mechanical transitions
   - ✅ Conversational, human-like progression
   - ✅ Occasional imperfections (natural for ESL authors)

**Applied To**: Every single generation, every component type, every author voice

---

### grammar_rules.txt (1,847 chars)
**Purpose**: Enforce linguistic patterns that feel natural and human

**Critical Rules**:
1. **Article Flexibility** (ESL Pattern)
   - Occasional article omission ("Material shows properties" vs "The material shows properties")
   - Natural for non-native English speakers
   - Adds authenticity to ESL author voices

2. **Sentence Structure Variation**
   - Mix active and passive voice
   - Vary clause complexity
   - Natural syntactic diversity

3. **Punctuation Patterns**
   - Use commas for natural pauses
   - Avoid excessive semicolons (AI tendency)
   - Embrace dashes for informal breaks

4. **Vocabulary Choices**
   - Prefer concrete over abstract
   - Choose specific over general
   - Use technical terms appropriately

**Applied To**: Every generation, layered on top of anti-AI rules

---

## 🔍 Rule Format

Rules are written in **natural language instructions** for the AI model:

```
DO NOT use formulaic structures like:
- "X does Y while preserving Z"
- "This enables A, facilitating B, and ensuring C"

INSTEAD, use varied, natural phrasing:
- Direct statements: "X improves Y"
- Specific examples: "Density of 2.7 g/cm³ enables aerospace applications"
- Mixed structures: Short sentences. Longer explanatory clauses when needed.

AVOID:
- Abstract transitions ("results suggest")
- Repeated sentence starters
- Uniform sentence lengths
- Generic descriptions

EMBRACE:
- Concrete details
- Natural variation
- Occasional imperfections (ESL authors)
- Conversational flow
```

---

## 🔧 How Rules Are Applied

Rules are **automatically injected** into every generation prompt:

1. **Component Prompt** (`prompts/components/*.txt`)
   - Defines WHAT to generate (task specification)

2. **Author Voice** (`prompts/personas/*.yaml`)
   - Defines HOW to write (voice patterns)

3. **+ Universal Rules** (`prompts/rules/*.txt`)
   - Defines WHAT TO AVOID (constraints)

**Assembly**: `processing/generation/prompt_builder.py` combines all three layers into unified prompt sent to API.

**Example Prompt Structure**:
```
[Component Instructions: "Generate 15-word subtitle..."]
[Author Voice: "Write as Italian author with technical precision..."]
[Anti-AI Rules: "Avoid formulaic structures like X does Y..."]
[Grammar Rules: "Use article flexibility and varied syntax..."]
```

---

## ✏️ Editing Rules

### To Update Existing Rules:
1. **Edit the rule file directly**:
   ```bash
   vim prompts/rules/anti_ai_rules.txt
   ```

2. **Test changes** with a generation:
   ```bash
   python3 run.py --material "Aluminum" --component subtitle
   ```

3. **Validate AI detection**:
   - Check Winston AI score in output
   - Target: < 0.10 (less than 10% AI detected)
   - Ideal: 0.000 (no AI patterns detected)

4. **No deployment needed** - changes apply immediately

### To Add New Rules:
1. **Identify the pattern** you want to avoid
2. **Write clear instructions** with examples
3. **Add to appropriate file**:
   - AI detection patterns → `anti_ai_rules.txt`
   - Grammar/linguistic patterns → `grammar_rules.txt`
4. **Test with multiple materials** to verify effectiveness

---

## 🚫 What NOT to Include

**NEVER put these in rule files**:
- ❌ API parameters (temperature, penalties)
- ❌ Component-specific instructions (word counts, formats)
- ❌ Author voice patterns (those belong in personas/)
- ❌ Code logic or implementation details
- ❌ Positive content instructions (use component prompts)

**WHY**: Rules are universal constraints that apply everywhere. Specific instructions belong in component prompts or persona files.

---

## 📊 Rule Effectiveness

Measured by **AI detection scores** from Winston AI:

| Metric | Target | Current Performance |
|--------|--------|---------------------|
| AI Detection Score | < 0.10 | 0.000 consistently |
| Human Score | > 90% | 98%+ average |
| Success Rate | 100% first attempt | ✅ Achieved |
| Detection Method | Ensemble | 70% advanced + 30% simple |

**Validation**: `processing/detection/ensemble.py` runs both detection methods and combines results.

---

## 🎯 Best Practices

1. **Be Specific**: Provide concrete examples
   - ❌ "Avoid AI-like writing"
   - ✅ "Avoid formulaic structures like 'X does Y while Z'"

2. **Show Both Sides**: What NOT to do AND what TO do instead
   - ❌ "Don't use abstract transitions"
   - ✅ "Avoid: 'Results suggest' → Use: 'Tests show' or direct statements"

3. **Test Thoroughly**: Rules affect ALL content
   - Generate multiple materials
   - Test all component types
   - Verify all author voices

4. **Keep It Universal**: Rules should apply broadly
   - Not specific to one component
   - Not tied to one author voice
   - Not dependent on material type

5. **Update Based on Detection**: If AI scores rise, strengthen rules
   - Analyze flagged content
   - Identify new patterns
   - Add targeted rules

---

## 🔗 Related Documentation

- **Parent**: `prompts/README.md` - Overview of entire prompt system
- **Components**: `prompts/components/README.md` - Task specifications (what to generate)
- **Personas**: `prompts/personas/README.md` - Author voices (how to write)
- **Detection**: `processing/detection/patterns/ai_detection_patterns.txt` - Technical detection logic
- **Code**: `processing/generation/prompt_builder.py` - Prompt assembly logic

---

## 🚀 Quick Commands

**View current rules**:
```bash
cat prompts/rules/anti_ai_rules.txt
cat prompts/rules/grammar_rules.txt
```

**Edit rules**:
```bash
vim prompts/rules/anti_ai_rules.txt  # or use your preferred editor
```

**Test rule changes**:
```bash
python3 run.py --material "Aluminum" --component subtitle
# Check AI detection score in output
```

**Validate across multiple materials**:
```bash
python3 scripts/processing/regenerate_subtitles_with_processing.py --test
# Generates 10 random materials, shows AI scores
```

**Check rule effectiveness**:
```bash
# Run E2E tests with AI detection validation
python3 processing/tests/test_e2e_pipeline.py
```

---

## 📈 Rule Evolution

Rules are continuously refined based on:
1. **AI Detection Results**: Patterns that trigger detection get new rules
2. **Human Evaluation**: Content that feels "robotic" gets targeted rules
3. **Author Voice Feedback**: ESL patterns that need preservation
4. **Generation Failures**: Edge cases that need explicit constraints

**History**: See git log for `prompts/rules/*.txt` to track rule evolution over time.
