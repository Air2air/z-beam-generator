# 🎯 Quick Start: Using Copilot for Content Generation

**Date:** November 14, 2025  
**Status:** Ready to Use ✅

---

## 🚀 The Simple Way

Just ask Copilot naturally:

> "Generate a subtitle for Aluminum"

Copilot will automatically:
1. ✅ Run `python3 run.py --subtitle "Aluminum"`
2. ✅ Show you the terminal output
3. ✅ Report the generated text
4. ✅ Confirm where it was saved

**No manual commands needed!**

---

## 📝 What You Can Ask For

### Generate Individual Components

```
"Generate a subtitle for Steel"
"Create a micro for Brass"
"Make an FAQ for Copper"
"Write a description for Aluminum"
```

### Adjust Settings First

```
"Make the content more natural and varied"
"Increase technical language"
"Add more personality to the writing"
```

### Complete Workflows

```
"Generate everything for Titanium"
"Run the full workflow for Stainless Steel"
```

---

## 🎛️ Understanding the System

### Where Prompts Are Stored

```
prompts/
├── subtitle.txt        ← 21-63 word subtitle instructions
├── micro.txt         ← 25-word caption instructions
├── description.txt     ← 60-word base target (actual: ~120-180 words)
├── faq.txt            ← FAQ generation instructions
└── troubleshooter.txt ← Troubleshooting guide instructions
```

### Where Settings Are Controlled

```
processing/config.yaml  ← 10 sliders control ALL generation

author_voice_intensity: 50      # How strong the regional voice
sentence_rhythm_variation: 80   # How varied the sentence structure
imperfection_tolerance: 80      # How natural/human-like
technical_language_intensity: 50 # How technical the content
# ... 6 more sliders
```

### Where Output Goes

```
data/materials/Materials.yaml   ← Generated content saved here

Aluminum:
  subtitle: "Generated subtitle appears here"
  micro: "Generated caption appears here"
  faq:
    - question: "Generated question"
      answer: "Generated answer"
```

---

## 💡 Real Examples

### Example 1: Basic Subtitle Generation

**You ask:**
> "Generate a subtitle for Aluminum"

**Copilot does:**
```bash
python3 run.py --subtitle "Aluminum"
```

**Terminal shows:**
```
================================================================================
📝 SUBTITLE GENERATION: Aluminum
================================================================================

🔧 Initializing Grok API client...
✅ Grok client ready

🤖 Generating AI-powered subtitle...
   • Target: 8-15 word professional tagline
   • Style: Technical, clear, professional

✅ Subtitle generated and saved successfully!

📊 Statistics:
   • Length: 87 characters
   • Word count: 13 words

📝 FULL GENERATED TEXT:
────────────────────────────────────────────────────────────────────────────────
Removes oxide layers while preserving aluminum's natural finish
────────────────────────────────────────────────────────────────────────────────

💾 Saved to: data/materials/Materials.yaml → subtitle
✨ Subtitle generation complete!
```

**Copilot tells you:**
```
✅ Generated subtitle for Aluminum (13 words):
"Removes oxide layers while preserving aluminum's natural finish"

Saved to Materials.yaml at materials.Aluminum.subtitle
```

---

### Example 2: Adjusting Style First

**You ask:**
> "Make the subtitles more varied and natural, then generate one for Steel"

**Copilot does:**
```bash
# Step 1: Adjust settings
python3 -m processing.intensity.intensity_cli set rhythm 75
python3 -m processing.intensity.intensity_cli set imperfection 65

# Step 2: Generate
python3 run.py --subtitle "Steel"
```

**You get:**
- More sentence variety (rhythm 75)
- More natural human-like writing (imperfection 65)
- Subtitle specifically for Steel

---

### Example 3: Multiple Components

**You ask:**
> "Generate subtitle, micro, and FAQ for Brass"

**Copilot does:**
```bash
python3 run.py --subtitle "Brass"
python3 run.py --micro "Brass"
python3 run.py --faq "Brass"
```

**You get:**
- All three components generated
- All saved to Materials.yaml under `Brass:`
- Word counts and stats for each

---

## 🎨 Customizing Generation

### Make it More Technical

**You ask:**
> "Increase technical language for the next generation"

**Copilot does:**
```bash
python3 -m processing.intensity.intensity_cli set technical 70
python3 -m processing.intensity.intensity_cli set context 65
```

### Make it More Natural/Human

**You ask:**
> "Make it sound more human and less AI-like"

**Copilot does:**
```bash
python3 -m processing.intensity.intensity_cli set rhythm 80
python3 -m processing.intensity.intensity_cli set imperfection 70
python3 -m processing.intensity.intensity_cli set personality 55
```

### Check Current Settings

**You ask:**
> "What are the current generation settings?"

**Copilot does:**
```bash
python3 -m processing.intensity.intensity_cli status
```

**Shows you:**
```
╔══════════════════════════════════════════════════════════════╗
║           INTENSITY MANAGER - 10 SLIDER SYSTEM               ║
╠══════════════════════════════════════════════════════════════╣
║ 1. Author Voice:                        50/100         ║
║    █████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░ ║
║ 2. Technical Language:                  50/100         ║
║    █████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░ ║
║ 5. Sentence Rhythm:                     80/100         ║
║    ████████████████████████████████████████░░░░░░░░░░ ║
║ 6. Imperfection Tolerance:              80/100         ║
║    ████████████████████████████████████████░░░░░░░░░░ ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 🔍 Verifying Results

### Check What Was Generated

**You ask:**
> "Show me the subtitle that was generated for Aluminum"

**Copilot reads:**
```yaml
# From data/materials/Materials.yaml

Aluminum:
  subtitle: "Removes oxide layers while preserving aluminum's natural finish"
```

---

## 🚨 If Something Goes Wrong

### Material Name Not Found

**Error:** "Material 'Aluminium' not found"

**Copilot helps:**
- Suggests correct spelling: "Did you mean 'Aluminum'?"
- Shows available materials similar to your request

### API Connection Issue

**Error:** "Failed to initialize API client"

**Copilot checks:**
```bash
python3 run.py --test-api
```

Reports specific issue and suggests fix.

---

## 📚 Behind the Scenes

When you ask to "generate a subtitle for Aluminum", here's what happens:

1. **Copilot reads** `.github/COPILOT_GENERATION_GUIDE.md`
2. **Identifies** component type (subtitle) and material (Aluminum)
3. **Runs command** `python3 run.py --subtitle "Aluminum"`
4. **System loads**:
   - Prompt template from `prompts/subtitle.txt`
   - Settings from `processing/config.yaml`
   - Material data from `data/materials/Materials.yaml`
5. **Grok API** generates content based on instructions
6. **System validates**:
   - Word count (8-15 words for subtitle)
   - AI detection score (must be < threshold)
   - Human-like qualities
7. **Saves to** `Materials.yaml` under `Aluminum.subtitle`
8. **Reports** results to terminal (you see everything)

---

## ✨ Key Benefits

### For You:
- 🗣️ **Natural language requests** - Just ask in plain English
- 📊 **Automatic reporting** - See exactly what was generated
- 🎛️ **Easy customization** - Adjust style with simple requests
- ✅ **Confidence** - System validates everything automatically

### For the System:
- 📁 **Organized prompts** - All templates in `/prompts/`
- ⚙️ **Centralized config** - 10 sliders control everything
- 🎯 **Single source of truth** - Materials.yaml for all data
- 🔄 **Complete workflow** - Generate → Voice → Export

---

## 🎯 Ready to Use!

Just start asking Copilot to generate content. Examples:

```
"Generate a subtitle for Titanium"
"Create a micro for Stainless Steel"
"Make an FAQ for Copper"
"Increase technical language then generate subtitle for Aluminum"
"Show me current settings"
```

**That's it!** The system handles everything else automatically.

---

## 📖 More Information

- **For Copilot**: Read `.github/COPILOT_GENERATION_GUIDE.md`
- **System Architecture**: Read `processing/docs/ARCHITECTURE.md`
- **Slider System**: Read `processing/docs/INTENSITY_CONTROLS.md`
- **All Commands**: Run `python3 run.py --help`

---

**Last Updated:** November 14, 2025  
**Status:** Production-Ready ✅  
**Next Step:** Just ask Copilot to generate something!
