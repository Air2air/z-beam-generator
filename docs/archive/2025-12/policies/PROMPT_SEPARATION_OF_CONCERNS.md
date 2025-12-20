# Prompt Separation of Concerns Policy

**Date**: November 18, 2025  
**Status**: Active Policy  
**Enforcement**: Mandatory for all content generation

---

## 🎯 Core Principle

**AI models do not reliably follow specific numeric constraints (word counts, measurements, percentages) embedded in prompts.**

**Solution**: Separate content instructions (WHAT to write) from validation constraints (HOW MUCH to write).

---

## 📋 Policy Rules

### Rule 1: Prompts Define WHAT, Not HOW MUCH

❌ **WRONG** - Embedding constraints in prompts:
```
Write EXACTLY 85 words about aluminum.
Include 3 technical specifications.
Use 50% formal and 50% conversational tone.
```

✅ **CORRECT** - Prompts focus on content:
```
Describe aluminum's laser cleaning characteristics.
Include relevant technical specifications.
Use professional but accessible language.
```

### Rule 2: Validation Enforces HOW MUCH

✅ **Implement strict post-generation validation**:
```python
# Generate content
content = api_client.generate(prompt)

# THEN validate constraints
word_count = len(content.split())
if word_count < min_words or word_count > max_words:
    raise ValueError(f"Word count {word_count} outside range {min_words}-{max_words}")
    # System will retry with adjusted parameters
```

### Rule 3: AI Behavior Patterns

**Observed**: Grok, Claude, GPT models default to "natural" content length (~30-40 words/paragraph) regardless of explicit numeric instructions.

**Implication**: 
- ❌ Cannot rely on AI to hit specific word counts
- ✅ Must use validation + retry loops
- ✅ Adjust generation parameters (temperature, penalties) on retry

---

## 🏗️ Implementation Pattern

### Standard Generation Flow

```python
def generate_with_validation(
    prompt: str,
    target_length: int,
    tolerance: float = 0.30
) -> str:
    """
    Generate content with strict length validation.
    
    Args:
        prompt: Content instructions (WHAT to write)
        target_length: Target word count (HOW MUCH)
        tolerance: Acceptable deviation (±30% default)
    """
    min_acceptable = int(target_length * (1 - tolerance))
    max_acceptable = int(target_length * (1 + tolerance))
    
    for attempt in range(max_attempts):
        # Generate content
        content = api_client.generate(prompt)
        
        # Validate word count
        word_count = len(content.split())
        
        if min_acceptable <= word_count <= max_acceptable:
            return content  # SUCCESS
        
        # FAILED - retry with adjusted parameters
        logger.warning(
            f"Attempt {attempt+1}: {word_count} words "
            f"(target: {min_acceptable}-{max_acceptable})"
        )
        # Adjust temperature/penalties for next attempt
    
    raise ValueError(f"Failed to generate content in range after {max_attempts} attempts")
```

---

## 📊 Real-World Evidence

### Case Study: Caption Generation (November 18, 2025)

**Configuration**:
- Target range: 20-120 words per section
- Random selection: Correctly picking diverse targets (34w, 67w, 115w, etc.)

**Prompt instructions tested**:
1. `"Word count: {target} words (±30 tolerance)"` → AI ignored, clustered at 32-41w
2. `"Word count: {target} words (flexible)"` → AI ignored, clustered at 30-40w  
3. `"Write EXACTLY {target} words"` → AI ignored, clustered at 33-37w

**Conclusion**: Grok AI defaults to ~35 words regardless of instruction.

**Solution implemented**: Strict validation + retry loop forces compliance.

---

## ✅ Compliance Checklist

**Before implementing new content generation**:

- [ ] Prompts contain ONLY content instructions (topics, style, tone)
- [ ] NO numeric constraints in prompts (word counts, percentages, ratios)
- [ ] Validation logic enforces numeric constraints
- [ ] Retry loop adjusts parameters when validation fails
- [ ] Tolerance values loaded from config (not hardcoded)
- [ ] Error messages include actual vs expected ranges

---

## 🔗 Related Documentation

- `PROMPT_PURITY_POLICY.md` - No hardcoded prompts in code
- `CONTENT_INSTRUCTION_POLICY.md` - Content instructions only in prompts/*.txt
- `HARDCODED_VALUE_POLICY.md` - No hardcoded thresholds/tolerances
- `GROK_QUICK_REF.md` - Pre-change checklist

---

## 📝 Summary

**Key Insight**: AI models are creative content generators, not precise measurement tools.

**Design Pattern**: 
1. Prompts → Content quality (WHAT)
2. Validation → Quantitative constraints (HOW MUCH)
3. Retry loops → Compliance enforcement

**Result**: Reliable wide-ranging content variation within defined bounds.
