# Copilot Generation Guide

**For AI Assistants:** This guide explains how to handle user requests to generate content (subtitles, micros, FAQs, etc.)

---

## 🎯 User Request Patterns

When the user says:
- "Generate a subtitle for Aluminum"
- "Create micro for Steel"
- "Generate FAQ for Brass"
- "Make a description for Copper"
- "Regenerate Aluminum"

**You should automatically execute the appropriate command.**

## 🔄 **CRITICAL: Complete Section Regeneration**

**EVERY generation request completely regenerates:**
1. **Page title and description** - Material-specific content
2. **Each section title and description** - All relationship sections, properties, applications

**Not just the requested field** - The entire material profile is refreshed with AI-generated, material-specific content replacing any generic schema descriptions.

**This means:** A single `--micro "Aluminum"` command will regenerate micro text PLUS all section metadata throughout the material's data.

---

## 📁 System Architecture

### Prompt Locations
All component prompt templates are in `/prompts/`:

```
prompts/
├── subtitle.txt           # 15-word subtitle prompts
├── micro.txt            # 25-word micro prompts
├── description.txt        # 150-word description prompts
├── faq.txt               # FAQ generation prompts
├── troubleshooter.txt    # Troubleshooting guide prompts
└── voice_rules.txt       # Voice enhancement rules

# Note: Anti-AI rules are now in prompts/core/base.txt
```

### Processing Configuration
Slider controls in `/processing/config.yaml`:

```yaml
# USER CONFIGS - 10 sliders control ALL generation
author_voice_intensity: 50        # Regional voice patterns
personality_intensity: 40          # Personal opinions
engagement_style: 35               # Reader engagement
technical_language_intensity: 50   # Technical density
context_specificity: 55            # Detail level
sentence_rhythm_variation: 80      # Structure variety (KEY)
imperfection_tolerance: 80         # Human-like quirks (KEY)
structural_predictability: 45      # Template adherence
ai_avoidance_intensity: 50         # Pattern variation
length_variation_range: 50         # Length flexibility
```

---

## ⚡ Quick Commands Reference

### Generate Individual Components

```bash
# Subtitles (15 words)
python3 run.py # Micros (25 words)
python3 run.py --micro "Steel"

# FAQs (2-8 questions, variable length answers)
python3 run.py --faq "Brass"

# Complete workflow (generate → voice → export)
python3 run.py --run "Copper"
```

### View Current Settings

```bash
# Check slider settings
python3 -m processing.intensity.intensity_cli status

# Test prompt instructions
python3 -m processing.intensity.intensity_cli test
```

### Adjust Generation Parameters

```bash
# Increase human realism
python3 -m processing.intensity.intensity_cli set rhythm 75
python3 -m processing.intensity.intensity_cli set imperfection 65

# More technical content
python3 -m processing.intensity.intensity_cli set technical 65

# More author personality
python3 -m processing.intensity.intensity_cli set personality 55
```

---

## 🤖 How to Handle Generation Requests

### Step-by-Step Process

When user requests generation:

1. **Identify the component type:**
   - subtitle → `--subtitle`
   - micro → `--micro`
   - faq → `--faq`
   - description → (use unified workflow `--run`)

2. **Identify the material name:**
   - Extract from user's request (e.g., "Aluminum", "Steel")
   - Must match entry in `data/materials/Materials.yaml`

3. **Execute the command:**
   ```python
   run_in_terminal(
       command='python3 run.py ',
       explanation='Generating subtitle for Aluminum',
       isBackground=False
   )
   ```

4. **Report results to user:**
   - Show terminal output (it's formatted nicely)
   - Confirm success or explain errors
   - Show word count, AI detection scores if present

---

## 📝 Example Interactions

### Example 1: Simple Subtitle Request

**User:** "Generate a subtitle for Aluminum"

**Copilot Action:**
```python
run_in_terminal(
    command='python3 run.py ',
    explanation='Generating 15-word subtitle for Aluminum',
    isBackground=False
)
```

**Expected Output:**
```
================================================================================
📝 SUBTITLE GENERATION: Aluminum
================================================================================

🔧 Initializing Grok API client...
✅ Grok client ready

🔧 Initializing UnifiedMaterialsGenerator...
✅ Generator ready

🤖 Generating AI-powered subtitle...
   • Target: 8-15 word professional tagline
   • Style: Technical, clear, professional
   • Audience: Technical professionals and decision-makers
   • Note: Voice enhancement happens in post-processing

✅ Subtitle generated and saved successfully!

📊 Statistics:
   • Length: 87 characters
   • Word count: 13 words

📝 FULL GENERATED TEXT:
────────────────────────────────────────────────────────────────────────────────
Removes oxide layers while preserving aluminum's natural finish
────────────────────────────────────────────────────────────────────────────────

💾 Saved to: materials/data/Materials.yaml → subtitle
✨ Subtitle generation complete!
```

**Copilot Response to User:**
```
✅ Generated subtitle for Aluminum (13 words):
"Removes oxide layers while preserving aluminum's natural finish"

Saved to Materials.yaml. Next step: Apply voice enhancement with voice/enhance_materials_voice.py
```

---

### Example 2: Caption Request

**User:** "Create a caption for Steel"

**Copilot Action:**
```python
run_in_terminal(
    command='python3 run.py --micro "Steel"',
    explanation='Generating 25-word caption for Steel',
    isBackground=False
)
```

---

### Example 3: Multiple Components

**User:** "Generate subtitle and caption for Brass"

**Copilot Action:**
```python
# Generate subtitle first
run_in_terminal(
    command='python3 run.py ',
    explanation='Generating subtitle for Brass',
    isBackground=False
)

# Then generate caption
run_in_terminal(
    command='python3 run.py --micro "Brass"',
    explanation='Generating caption for Brass',
    isBackground=False
)
```

**Copilot Response:**
```
✅ Generated both components for Brass:

Subtitle (13 words): [show generated text]
Caption (24 words): [show generated text]

Both saved to Materials.yaml.
```

---

### Example 4: Complete Workflow

**User:** "Generate everything for Copper"

**Copilot Action:**
```python
run_in_terminal(
    command='python3 run.py --run "Copper"',
    explanation='Running complete workflow for Copper (generate → voice → export)',
    isBackground=False
)
```

This runs:
1. ✅ Generate AI content → Materials.yaml
2. ✅ Apply voice enhancement → Materials.yaml
3. ✅ Export to frontmatter → frontmatter/materials/

---

## 🎛️ Adjusting Generation Parameters

### When User Wants Different Style

**User:** "Make the subtitles more varied and natural"

**Copilot Action:**
```python
# Increase rhythm variation and imperfection tolerance
run_in_terminal(
    command='python3 -m processing.intensity.intensity_cli set rhythm 80',
    explanation='Increasing sentence rhythm variation',
    isBackground=False
)

run_in_terminal(
    command='python3 -m processing.intensity.intensity_cli set imperfection 70',
    explanation='Allowing more human-like imperfections',
    isBackground=False
)
```

**Then regenerate:**
```python
run_in_terminal(
    command='python3 run.py ',
    explanation='Regenerating subtitle with new settings',
    isBackground=False
)
```

---

### When User Wants More Technical Content

**User:** "Make captions more technical"

**Copilot Action:**
```python
run_in_terminal(
    command='python3 -m processing.intensity.intensity_cli set technical 70',
    explanation='Increasing technical language intensity',
    isBackground=False
)

run_in_terminal(
    command='python3 -m processing.intensity.intensity_cli set context 65',
    explanation='Increasing context specificity',
    isBackground=False
)

# Then regenerate
run_in_terminal(
    command='python3 run.py --micro "Steel"',
    explanation='Regenerating caption with increased technical depth',
    isBackground=False
)
```

---

## 🔍 Checking Results

### View Generated Content

Generated content is saved to `data/materials/Materials.yaml`:

```yaml
Aluminum:
  subtitle: "Removes oxide layers while preserving aluminum's natural finish"
  micro: "Laser cleaning targets aluminum oxide at 1064nm wavelength..."
  faq:
    - question: "Why choose laser cleaning for aluminum?"
      answer: "Laser cleaning removes contaminants without chemicals..."
```

**To verify:**
```python
read_file(
    filePath='/Users/todddunning/Desktop/Z-Beam/z-beam-generator/data/materials/Materials.yaml',
    offset=<line_number>,
    limit=50
)
```

---

## 🚨 Error Handling

### Material Not Found

**Error:** "Material 'Aluminium' not found"

**Copilot Action:**
1. Check available materials:
   ```python
   run_in_terminal(
       command='python3 run.py --list-materials',
       explanation='Listing available materials',
       isBackground=False
   )
   ```

2. Suggest correct spelling to user

---

### API Connection Issues

**Error:** "Failed to initialize API client"

**Copilot Action:**
1. Check API configuration:
   ```python
   run_in_terminal(
       command='python3 run.py --test-api',
       explanation='Testing API connections',
       isBackground=False
   )
   ```

2. Report specific API issue to user

---

## 📊 Understanding Terminal Output

### Success Indicators:
- ✅ Green checkmarks
- "Generation complete!"
- Word count statistics
- Saved location confirmation

### What to Report to User:
1. **Success/Failure status**
2. **Generated text** (show the actual content)
3. **Word count** (verify it meets target)
4. **Where saved** (Materials.yaml path)
5. **Next steps** (voice enhancement, export)

---

## 🎯 Best Practices

### DO:
✅ Always use `run_in_terminal` with `isBackground=False` to see output
✅ Show terminal output to user (it's formatted for readability)
✅ Confirm material name matches Materials.yaml entries
✅ Report actual generated text to user
✅ Suggest next steps (voice enhancement, export)

### DON'T:
❌ Don't run generation in background (need to see results)
❌ Don't assume success without checking terminal output
❌ Don't modify Materials.yaml directly (use generation commands)
❌ Don't skip showing results to user

---

## 🔗 Related Files

### For Generation:
- `/run.py` - Main entry point for all commands
- `/shared/commands/generation.py` - Generation logic
- `/materials/unified_generator.py` - Content generator
- `/processing/orchestrator.py` - Processing pipeline

### For Configuration:
- `/processing/config.yaml` - 10-slider system
- `/processing/intensity/intensity_cli.py` - CLI interface
- `/prompts/*.txt` - Component prompt templates

### For Voice Enhancement:
- `/scripts/voice/enhance_materials_voice.py` - Voice processor
- `/data/authors/*.yaml` - Author personality profiles

---

## 💡 Quick Reference Card

```bash
# GENERATION
python3 run.py # 15 words
python3 run.py --micro "Material"     # 25 words
python3 run.py --faq "Material"         # 2-8 Q&As
python3 run.py --run "Material"         # Complete workflow

# SETTINGS
python3 -m processing.intensity.intensity_cli status
python3 -m processing.intensity.intensity_cli set rhythm 70

# VALIDATION
python3 run.py --test-api               # Check APIs
python3 run.py --list-materials         # Show materials
python3 run.py --validate               # Validate data

# DEPLOYMENT
python3 run.py --deploy                 # Export to Next.js
```

---

**Remember:** When user asks for generation, just execute the command and show them the results. The system handles all the complexity automatically.
