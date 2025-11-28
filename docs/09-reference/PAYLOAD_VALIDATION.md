# Payload Validator Quick Reference

**Purpose**: Validate Imagen prompts BEFORE API submission  
**File**: `shared/image/validation/payload_validator.py`  
**Status**: ✅ Complete and ready to use

## 30-Second Quick Start

```python
from shared.image.validation.payload_validator import ImagePromptPayloadValidator

validator = ImagePromptPayloadValidator()
result = validator.validate(
    prompt="Your prompt here",
    material="Aluminum",
    contaminant="oil-grease"
)

if result.has_critical_issues:
    print("❌ CANNOT SUBMIT:", result.get_summary())
elif result.has_errors:
    print("⚠️ HAS ERRORS:", result.format_report())
elif result.has_warnings:
    print("⚠️ WARNINGS:", result.format_report())
else:
    print("✅ Valid - safe to submit to Imagen")
```

## 7 Validation Categories

| Category | What It Checks | Severity |
|----------|----------------|----------|
| **Logic** | Contradictions (color, texture, state), ambiguous language | ERROR/WARNING |
| **Contamination** | Impossible combinations (rust on aluminum, dirt) | CRITICAL |
| **Physics** | Gravity violations (upward flow, floating) | CRITICAL |
| **Length** | Imagen 4096 char limit (target: 3500) | CRITICAL/WARNING/INFO |
| **Quality** | Anti-patterns (intensifiers, hedging, "!!!") | WARNING |
| **Duplication** | Repeated sentences/phrases | WARNING |
| **Technical** | API compatibility (blank lines, encoding) | WARNING |

## Common Failures

| Issue | Example | Severity |
|-------|---------|----------|
| **Rust on aluminum** | "Aluminum with rust oxidation" | CRITICAL ❌ |
| **Upward flow** | "Oil flowing upward from bottom" | CRITICAL ❌ |
| **Dirt contamination** | "Surface with dirt and soil" | CRITICAL ❌ |
| **Over 4096 chars** | Very long prompt | CRITICAL ❌ |
| **Color contradiction** | "Dark surface with bright highlights" | ERROR ❌ |
| **Texture contradiction** | "Smooth glossy with rough matte" | ERROR ❌ |
| **Ambiguous language** | "Maybe show some contamination" | WARNING ⚠️ |
| **Intensifiers** | "Very really extremely dark!!!" | WARNING ⚠️ |

## ValidationResult Quick Guide

```python
result.is_valid              # bool - Overall pass/fail
result.has_critical_issues   # bool - MUST fix (blocks API)
result.has_errors            # bool - SHOULD fix (may fail)
result.has_warnings          # bool - CONSIDER fixing (suboptimal)

result.get_summary()         # str - Brief summary
result.format_report()       # str - Detailed colored report

result.prompt_length         # int - Character count
result.contradiction_count   # int - Number of contradictions
result.duplication_count     # int - Number of duplications
result.issues                # List[ValidationIssue] - All issues
```

## Integration Pattern

```python
# In prompt builder
def build_prompt(...):
    prompt = construct_prompt(...)
    
    result = validator.validate(prompt, material, contaminant)
    
    if result.has_critical_issues:
        raise ValueError(f"Validation failed: {result.get_summary()}")
    
    if result.has_errors:
        logger.warning(result.format_report())
    
    return prompt
```

## Common Patterns

### Pattern 1: Validate Then Submit
```python
result = validator.validate(prompt, material, contaminant)
if result.is_valid and not result.has_errors:
    submit_to_imagen(prompt)
```

### Pattern 2: Fail Fast on Critical
```python
result = validator.validate(prompt, material, contaminant)
if result.has_critical_issues:
    raise ValueError(f"Cannot submit: {result.get_summary()}")
```

### Pattern 3: Log Warnings
```python
result = validator.validate(prompt, material, contaminant)
if result.has_warnings:
    logger.warning(f"Prompt quality issues:\n{result.format_report()}")
```

## Testing

```bash
# Run all tests
pytest tests/image/test_payload_validator.py -v

# Run demonstration
python3 scripts/image/demo_payload_validator.py
```

## Documentation

- **Integration Guide**: `PAYLOAD_VALIDATOR_INTEGRATION_GUIDE.md` (396 lines)
- **Implementation Summary**: `PAYLOAD_VALIDATOR_COMPLETE_NOV26_2025.md`
- **Tests**: `tests/image/test_payload_validator.py` (40+ test cases)
- **Demo**: `scripts/image/demo_payload_validator.py` (11 scenarios)

## Key Benefits

✅ Catch errors before wasting API credits  
✅ Prevent impossible requests (rust on aluminum)  
✅ Ensure length compliance (4096 char limit)  
✅ Improve prompt quality (detect anti-patterns)  
✅ Save money (don't submit bad prompts)  
✅ Debug aid (detailed issue reports)

---

**Status**: ✅ Complete - Ready to integrate  
**Performance**: ~10-50ms per validation  
**Thread-safe**: Yes
