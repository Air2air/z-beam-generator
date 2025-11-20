# Generation Phase Architecture

**Last Updated**: November 19, 2025  
**Status**: Active Policy

---

## 🎯 Core Principle

**ONE MATERIAL = ONE API REQUEST (no retries in generation phase)**

The generation phase produces initial content with a single API call per material. Quality validation, iteration, and refinement happen in subsequent stages (postprocessing, evaluation).

---

## 📋 Generation Phase Rules

### ✅ What Generation Phase DOES
1. **Single-pass content creation** - One API request per material
2. **Basic format validation** - Ensure valid structure (e.g., two paragraphs for captions)
3. **Length targeting** - Apply global variation range from config
4. **Save to Materials.yaml** - Persist generated content immediately

### ❌ What Generation Phase DOES NOT DO
1. **No retries** - If generation fails, report error and move on
2. **No quality iteration** - Winston/Realism scoring happens later
3. **No parameter adjustment** - Use base parameters from config only
4. **No learning feedback** - Learning happens in postprocessing

---

## 🔄 Multi-Stage Pipeline

```
Stage 1: GENERATION (this phase)
├─ One API call per material
├─ Apply length variation
├─ Basic format check
└─ Save to Materials.yaml

Stage 2: VALIDATION (postprocessing)
├─ Winston AI detection
├─ Realism evaluation
├─ Readability check
└─ Subjective language validation

Stage 3: ITERATION (if needed)
├─ Parameter adjustment
├─ Retry with feedback
├─ Learning integration
└─ Quality improvement
```

---

## ⚙️ Configuration

### generation/config.yaml
```yaml
simple_mode:
  max_attempts: 1                        # Single-pass (no retries)
  temperature_increase_per_retry: 0.0    # N/A - no retries
```

### Key Settings
- `max_attempts: 1` - Enforces single-pass generation
- No retry logic in generation code
- Validation/iteration happens in separate stages

---

## 💡 Rationale

**Why single-pass generation?**

1. **Speed**: Faster initial generation (no waiting for retries)
2. **Separation of Concerns**: Generation = create, Validation = assess, Iteration = improve
3. **Learning Efficiency**: Collect data from all materials before adjusting parameters
4. **Cost Control**: Avoid burning API credits on early retries before learning kicks in
5. **Clarity**: Each stage has a clear, focused responsibility

**Quality Control**: Still maintained through subsequent validation and iteration stages.

---

## 📊 Performance Impact

### Before (multi-attempt generation)
- 3 materials × 3-5 attempts = 9-15 API calls
- Average time: 60-90 seconds
- Mixed quality (some retries worse than first attempt)

### After (single-pass generation)
- 3 materials × 1 attempt = 3 API calls
- Average time: 15-20 seconds
- Consistent baseline for validation stage

---

## 🔍 Related Documentation

- **Processing Pipeline**: [docs/02-architecture/PROCESSING_PIPELINE.md](PROCESSING_PIPELINE.md)
- **Quality Validation**: [docs/08-development/REALISM_QUALITY_GATE.md](../08-development/REALISM_QUALITY_GATE.md)
- **Learning Integration**: [docs/06-ai-systems/LEARNING_INTEGRATION.md](../06-ai-systems/LEARNING_INTEGRATION.md)

---

## ✅ Compliance

- ✅ **No retries in generation code** - Enforced by `max_attempts: 1`
- ✅ **Single API call per material** - Verified by monitoring
- ✅ **No quality iteration** - Validation happens in postprocessing
- ✅ **Clear stage separation** - Generation → Validation → Iteration
