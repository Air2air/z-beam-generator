# Output Monitoring Guide

## Where to See Regular Updates

### 1. **Terminal Output (Real-Time)**
All generation progress appears in your terminal as it happens:

```bash
python3 test_progressive_retry.py
```

**What you'll see:**
```
📊 Step 1/3: Researching Titanium composition and applications...
✅ Research complete: 5 applications identified
🔍 Step 2/3: Identifying positive and negative aspects...
✅ Aspects identified: 6 positive, 4 negative
📝 Step 3/3: Crafting FAQ questions and answers...
🎭 Applying Taiwan voice enhancement...
✅ FAQ generated: 7 questions
```

**Retry messages (if quality fails):**
```
🔄 Retry attempt 2/3 due to quality failure...
   📈 Increasing creativity: temperature=0.8, tokens +20%
```

---

### 2. **Capture Full Log to File**
To save all output for later review:

```bash
python3 test_progressive_retry.py 2>&1 | tee output.log
```

- Terminal shows real-time progress
- `output.log` saves everything for analysis

---

### 3. **Progressive Settings per Attempt**

| Attempt | Temperature | Tokens (Step 1) | Tokens (Step 2) | Tokens (Step 3) |
|---------|-------------|-----------------|-----------------|-----------------|
| **1**   | 0.7         | 1000            | 800             | 4000            |
| **2**   | 0.8         | 1200 (+20%)     | 960 (+20%)      | 4800 (+20%)     |
| **3**   | 0.9         | 1400 (+40%)     | 1120 (+40%)     | 5600 (+40%)     |

**Why this works:**
- Higher temperature = more creative/varied outputs (reduces repetition)
- More tokens = longer, more detailed answers (improves quality)

---

### 4. **Key Messages to Watch For**

#### Success on First Try:
```
✅ SUCCESS on attempt 1
📊 Quality Score: 85/100
```

#### Quality Failure Triggering Retry:
```
⚠️  QUALITY VALIDATION FAILED - Attempt 1/3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Quality Score: 45/100 (min: 60)
❌ Errors (3):
   1. CRITICAL: 'systematic' appears in 100% of answers (robotic)
   2. LOW VARIATION: Only 14% unique sentence structures
   3. EXCESSIVE: 'methodology' appears in 86% of answers
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 Retrying... (2 attempts remaining)
```

#### Retry with Adjusted Settings:
```
🔄 Retry attempt 2/3 due to quality failure...
   📈 Increasing creativity: temperature=0.8, tokens +20%
📊 Step 1/3: Researching Titanium composition and applications...
```

#### Final Failure (All Attempts Exhausted):
```
❌ GENERATION FAILED - All 3 attempts exhausted
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Unable to generate quality content
Consider:
  • Adjusting technical intensity
  • Reducing voice intensity
  • Reviewing material-specific constraints
```

---

### 5. **API Client Logging**
You'll also see detailed API calls:

```
🚀 [API CLIENT] Starting request to grok-4-fast
📤 [API CLIENT] Sending prompt (1523 chars) with system prompt (145 chars)
⚙️ [API CLIENT] Config: max_tokens=1200, temperature=0.8
📥 [API CLIENT] Received response (Status: 200)
⏱️ [API CLIENT] Response time: 4.23s
📊 [API CLIENT] Tokens used: 1156 total
```

**Notice on retries:**
- `max_tokens` increases: 1000 → 1200 → 1400
- `temperature` increases: 0.7 → 0.8 → 0.9

---

### 6. **Materials.yaml Updates**
After successful generation:

```bash
# Check what was saved
python3 -c "
import yaml
data = yaml.safe_load(open('data/Materials.yaml'))
titanium = data['materials']['Titanium']
print(f'FAQ count: {len(titanium.get(\"faq\", []))}')
print(f'First question: {titanium[\"faq\"][0][\"question\"]}')
"
```

---

## Quick Test Commands

### Test with Output Capture:
```bash
python3 test_progressive_retry.py 2>&1 | tee retry_test.log
```

### Test Specific Material:
```bash
# Edit test_progressive_retry.py, change line 53:
material_name = "Granite"  # Or any material
```

### Watch Live (macOS):
```bash
python3 test_progressive_retry.py 2>&1 | tee >(tail -f)
```

---

## Understanding the Flow

1. **Attempt 1** runs with default settings (temp=0.7)
2. **Validation** checks quality (word count, repetition, variation)
3. **If fails:** Retry with temp=0.8, tokens +20%
4. **If fails again:** Final try with temp=0.9, tokens +40%
5. **Success OR exhaustion** → return result

The terminal shows **every step** in real-time with emojis and clear formatting.
