# Intensity Controls - Quick Reference

**10-Slider System for Maximum Human Realism**

## 📊 View Current Settings
```bash
python3 -m processing.intensity.intensity_cli status
```

## 🎛️ The 10 Sliders (0-100 scale)

### **Core Content Controls (1-4)**

| # | Slider | What It Controls | Sweet Spot |
|---|--------|------------------|------------|
| **1** | `voice` | Author voice characteristics, regional patterns | 50-60 |
| **2** | `technical` | Technical jargon, measurements, data density | 45-55 |
| **3** | `length` | Length variation tolerance (±% from target) | 40-60 |
| **4** | `ai` | AI pattern avoidance, variation intensity | 50-65 |

### **Human Realism Controls (5-10)**

| # | Slider | What It Controls | Sweet Spot |
|---|--------|------------------|------------|
| **5** | `rhythm` | Sentence length variation (KEY human marker) | 50-70 |
| **6** | `imperfection` | Allow human-like quirks and flaws | 45-60 |
| **7** | `personality` | Opinion/preference/experience markers | 35-50 |
| **8** | `context` | Concrete scenarios vs abstract principles | 50-65 |
| **9** | `structural` | Template-breaking, organic flow | 40-55 |
| **10** | `engagement` | Reader-awareness, direct address | 30-40 |

---

## ⚡ Quick Commands

### Change Individual Sliders
```bash
# Boost human realism markers
python3 -m processing.intensity.intensity_cli set rhythm 70
python3 -m processing.intensity.intensity_cli set imperfection 60
python3 -m processing.intensity.intensity_cli set personality 55

# Increase author voice authenticity
python3 -m processing.intensity.intensity_cli set voice 65

# Reduce AI-like patterns
python3 -m processing.intensity.intensity_cli set ai 75
python3 -m processing.intensity.intensity_cli set structural 60
```

### Test Current Settings
```bash
python3 -m processing.intensity.intensity_cli test
```

---

## 🎯 Presets by Use Case

### **For Subtitles (15-30 words)**
**Goal:** Punchy, memorable, human-authentic
```bash
python3 -m processing.intensity.intensity_cli set rhythm 70        # Varied sentence structure
python3 -m processing.intensity.intensity_cli set personality 60   # Evaluative language
python3 -m processing.intensity.intensity_cli set imperfection 55  # Slight quirks OK
python3 -m processing.intensity.intensity_cli set voice 55         # Noticeable voice
python3 -m processing.intensity.intensity_cli set structural 60    # Break templates
```

**Example output at these settings:**
> "Notably, precision laser work distinctly preserves Alabaster's delicate texture—essential for long-term integrity where mechanical methods typically fail."

### **For Descriptions (150 words)**
**Goal:** Informative, technical, but human
```bash
python3 -m processing.intensity.intensity_cli set technical 60     # More data
python3 -m processing.intensity.intensity_cli set context 65       # Specific scenarios
python3 -m processing.intensity.intensity_cli set rhythm 55        # Natural flow
python3 -m processing.intensity.intensity_cli set personality 45   # Subtle opinions
python3 -m processing.intensity.intensity_cli set engagement 40    # Professional-friendly
```

### **For Maximum Human Authenticity**
**Goal:** Pass AI detection with flying colors
```bash
python3 -m processing.intensity.intensity_cli set rhythm 75        # High variation
python3 -m processing.intensity.intensity_cli set imperfection 65  # Visible quirks
python3 -m processing.intensity.intensity_cli set personality 60   # Strong voice
python3 -m processing.intensity.intensity_cli set structural 65    # Organic flow
python3 -m processing.intensity.intensity_cli set ai 80            # Aggressive avoidance
python3 -m processing.intensity.intensity_cli set voice 70         # Authentic regional
```

### **For Clean, Professional Content**
**Goal:** Polished but still human
```bash
python3 -m processing.intensity.intensity_cli set imperfection 35  # Minimal quirks
python3 -m processing.intensity.intensity_cli set personality 30   # Neutral tone
python3 -m processing.intensity.intensity_cli set engagement 25    # Detached
python3 -m processing.intensity.intensity_cli set voice 45         # Light voice
python3 -m processing.intensity.intensity_cli set rhythm 45        # Moderate variation
```

---

## 🔍 Understanding the Scales

### 0-30: **LOW** - Minimal effect
- More AI-like, polished, consistent
- Use for: formal documentation, specifications

### 31-60: **MODERATE** - Balanced (DEFAULT)
- Natural human writing, professional
- Use for: most technical content

### 61-100: **HIGH** - Pronounced effect
- Maximum authenticity, character
- Use for: content that must pass AI detection

---

## 💡 Pro Tips

### For Subtitle Generation:
**Most Important Sliders (in order):**
1. **Rhythm (5)** - Single biggest AI tell in short content
2. **Personality (7)** - Evaluative language makes it memorable
3. **Imperfection (6)** - Slight quirks = authenticity
4. **Voice (1)** - Author personality shines through
5. **Structural (9)** - Break predictable patterns

### Red Flags to Avoid:
- ❌ All sliders at 50 (too uniform = AI-like)
- ❌ Rhythm below 40 (robotic sentence structure)
- ❌ Imperfection at 0 (perfect = suspicious)
- ❌ Personality at 0 (no human would write this neutrally)

### Optimal Combinations:
- ✅ Vary your settings slightly between generations
- ✅ Keep rhythm 10-20 points higher than other sliders
- ✅ Balance imperfection with context specificity
- ✅ Higher personality = lower engagement (don't double up)

---

## 📈 What Each Slider Actually Does

### 1. Voice (author_voice_intensity)
**Parameters controlled:**
- Regional trait frequency (0.1-0.7 per paragraph)
- Cultural quirks (0.05-0.30 per 200 words)
- Formality level (75-95%)
- Vocabulary uniqueness (65-90%)

**Effect:** Low = standard English; High = authentic regional voice

---

### 2. Technical (technical_language_intensity)
**Parameters controlled:**
- Units per sentence (0.2-1.0)
- Jargon level (minimal/moderate/full)
- Sentence complexity (12-24 words avg)
- Active voice % (50-80%)
- Data density (low/medium/high)

**Effect:** Low = accessible; High = expert-level dense content

---

### 3. Length (length_variation_range)
**Parameters controlled:**
- Tolerance % (±5% to ±50%)
- Enforcement (strict/moderate/relaxed)

**Effect:** Low = tight word count; High = content over length constraints

---

### 4. AI Avoidance (ai_avoidance_intensity)
**Parameters controlled:**
- Base temperature (0.7-1.0)
- Detection threshold (0.25-0.40)
- Max retries (3-7)

**Effect:** Low = natural patterns OK; High = aggressive variation

---

### 5. Rhythm (sentence_rhythm_variation) ⭐ KEY
**Parameters controlled:**
- Coefficient of variation (15-60%)
- Sentence mix (short/medium/long ratio)
- Breathing room frequency (0-1)
- Consecutive similar penalty

**Effect:** Low = uniform rhythm (robotic); High = dramatic variation (human)

**Why it matters:** Single biggest differentiator between human and AI writing

---

### 6. Imperfection (imperfection_tolerance) ⭐ KEY
**Parameters controlled:**
- Redundancy tolerance (0-0.4)
- Hedging frequency (0-0.25)
- Awkward phrasing allowance
- Minor repetition OK
- Occasional passive voice OK

**Effect:** Low = perfect (AI-like); High = authentic quirks (human)

**Why it matters:** Perfect text = dead giveaway

---

### 7. Personality (personality_intensity)
**Parameters controlled:**
- Evaluative frequency (0-0.36)
- Experience markers (yes/no)
- Comparative preferences
- Subjective assessments
- Implied judgment

**Effect:** Low = neutral observer; High = strong opinions

**Examples at high settings:**
- "Surprisingly effective"
- "Far exceeds traditional methods"
- "In my experience, this approach..."

---

### 8. Context (context_specificity)
**Parameters controlled:**
- Specific scenario frequency (0.1-0.8)
- Named application contexts
- Practical limitations
- Concrete numbers vs. vague
- Edge case depth

**Effect:** Low = abstract principles; High = concrete scenarios

**Examples at high settings:**
- "On aircraft aluminum at 85% humidity..."
- "Except when substrate thickness exceeds 3mm..."

---

### 9. Structural (structural_predictability)
**Parameters controlled:**
- Template adherence (0.2-0.8)
- Opening variety
- Topic sentence flexibility
- Transition diversity
- Single-sentence paragraphs OK
- Information order randomization

**Effect:** Low = formulaic templates; High = organic flow

**Why it matters:** AI loves templates, humans break them

---

### 10. Engagement (engagement_style)
**Parameters controlled:**
- Direct address frequency (0-0.35)
- Rhetorical questions
- Imperative mood ("Consider...")
- Anticipatory phrasing ("As expected...")
- Reader context assumptions

**Effect:** Low = detached exposition; High = conversational

**Examples at high settings:**
- "You'll find that..."
- "Consider the implications when..."
- "As you might expect..."

---

## 🧪 Testing Your Settings

After adjusting sliders, test them:

```bash
# See the prompt instructions that will be sent to AI
python3 -m processing.intensity.intensity_cli test

# Generate actual content to verify
python3 run.py --material "Aluminum" --component subtitle

# Check the output characteristics
# - Count sentence lengths (rhythm)
# - Look for evaluative language (personality)
# - Check for minor quirks (imperfection)
# - Verify author voice patterns (voice)
```

---

## 🔧 Configuration File

All settings stored in: `/processing/config.yaml`

You can edit directly if preferred:
```yaml
author_voice_intensity: 50
technical_language_intensity: 50
length_variation_range: 50
ai_avoidance_intensity: 50
sentence_rhythm_variation: 50
imperfection_tolerance: 50
personality_intensity: 40
context_specificity: 55
structural_predictability: 45
engagement_style: 35
```

---

## 📚 Further Reading

- Full documentation: `/processing/INTENSITY_CONTROLS.md`
- Implementation details: `/processing/intensity_manager.py`
- CLI source: `/processing/intensity_cli.py`

---

## 🆘 Troubleshooting

**Output too robotic?**
→ Increase: rhythm (60+), imperfection (55+), structural (55+)

**Output too informal?**
→ Decrease: personality (35), engagement (25), imperfection (40)

**Not enough technical depth?**
→ Increase: technical (65+), context (65+)

**Too much variation/inconsistent?**
→ Decrease: rhythm (40), imperfection (40), ai (40)

**AI detection flagging content?**
→ Increase: rhythm (70+), imperfection (60+), ai (75+), structural (60+)
