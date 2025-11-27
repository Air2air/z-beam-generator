# Image Prompt Payload Validator - Integration Guide

**Date**: November 26, 2025  
**Status**: ✅ Complete and Ready for Integration

## Overview

The `ImagePromptPayloadValidator` is a comprehensive validation system that checks prompts **before** they're submitted to the Imagen API. It detects logic issues, impossible contaminations, physics violations, length problems, and quality anti-patterns.

## Quick Start

```python
from shared.image.validation.payload_validator import ImagePromptPayloadValidator

# Create validator instance
validator = ImagePromptPayloadValidator()

# Validate prompt
result = validator.validate(
    prompt="Steel surface with oil contamination showing dark patches",
    material="Steel",
    contaminant="oil-grease"
)

# Check result
if result.is_valid:
    print("✅ Prompt is valid - safe to submit to Imagen")
else:
    print("❌ Validation failed:")
    print(result.format_report())
```

## Validation Categories

### 1. **Logic Validation**
Detects contradictions and confusion:

**Contradictions Detected**:
- Color: "dark" + "bright", "black" + "white"
- Texture: "smooth" + "rough", "glossy" + "matte"
- State: "fresh" + "aged", "new" + "weathered"

**Example**:
```python
# ❌ FAILS - Color contradiction
prompt = "Show dark black surface with bright white highlights"
```

**Confusion Patterns**:
- Ambiguous terms: "maybe", "somewhat", "possibly"
- Vague quantifiers: "some", "various", "several"

**Example**:
```python
# ⚠️ WARNS - Ambiguous language
prompt = "Maybe show some kind of contamination that might be present"
```

### 2. **Contamination Validation**
Prevents impossible material-contaminant combinations:

**Impossible Combinations**:
- Rust on aluminum, copper, brass, plastic
- Dirt/soil on any material (forbidden)

**Example**:
```python
# ❌ FAILS - Impossible contamination
validator.validate(
    prompt="Aluminum surface with rust oxidation",
    material="Aluminum",
    contaminant="rust-oxidation"
)
```

### 3. **Physics Validation**
Detects physics violations:

**Violations Detected**:
- Upward flow: "flowing upward", "drips going up"
- Floating: "floating above surface", "suspended in air"

**Example**:
```python
# ❌ FAILS - Physics violation
prompt = "Oil contamination flowing upward from bottom to top"
```

### 4. **Length Validation**
Ensures prompt stays within Imagen API limits:

**Limits**:
- **Hard limit**: 4096 characters (CRITICAL error if exceeded)
- **Warning**: 3800 characters (should optimize)
- **Target**: 3500 characters (ideal)

**Example**:
```python
# ❌ FAILS - Exceeds limit
prompt = "A" * 5000  # 5000 characters
result = validator.validate(prompt)
# result.has_critical_issues == True
```

### 5. **Quality Validation**
Flags quality anti-patterns:

**Anti-patterns**:
- Intensifiers: "very", "really", "extremely"
- Hedging: "somewhat", "relatively", "fairly"
- Excessive punctuation: "!!!", "???"

**Example**:
```python
# ⚠️ WARNS - Quality issues
prompt = "Very dark surface with really heavy contamination!!!"
```

### 6. **Duplication Validation**
Detects repeated content:

**Detects**:
- Duplicate sentences (exact matches)
- Repeated phrases (>3 occurrences)

**Example**:
```python
# ⚠️ WARNS - Duplication
prompt = "Show the surface. Show the surface. Show the surface."
```

### 7. **Technical Validation**
API compatibility checks:

**Checks**:
- Excessive blank lines (>2 consecutive)
- Very long lines (>500 characters)
- Invalid characters

## ValidationResult Structure

```python
@dataclass
class ValidationResult:
    is_valid: bool                    # Overall pass/fail
    issues: List[ValidationIssue]     # List of all issues
    prompt_length: int                # Character count
    contradiction_count: int          # Number of contradictions
    duplication_count: int            # Number of duplications
    has_critical_issues: bool         # Any CRITICAL severity issues
    has_errors: bool                  # Any ERROR severity issues
    has_warnings: bool                # Any WARNING severity issues
    
    # Methods
    def get_summary() -> str:         # Brief summary
    def format_report() -> str:       # Detailed colored report
```

## ValidationIssue Structure

```python
@dataclass
class ValidationIssue:
    message: str                      # Description of issue
    severity: ValidationSeverity      # CRITICAL/ERROR/WARNING/INFO
    category: ValidationCategory      # LOGIC/CONTAMINATION/PHYSICS/etc
    details: Optional[Dict]           # Additional context
```

## Severity Levels

| Severity | Meaning | Action Required |
|----------|---------|----------------|
| `CRITICAL` | Blocks submission | **Must fix** - will fail at API |
| `ERROR` | Major issue | **Should fix** - may fail or produce bad results |
| `WARNING` | Quality issue | **Consider fixing** - suboptimal but may work |
| `INFO` | Suggestion | Optional improvement |

## Integration into SharedPromptBuilder

**File**: `shared/image/prompts/prompt_builder.py`

```python
from shared.image.validation.payload_validator import ImagePromptPayloadValidator

class SharedPromptBuilder:
    def __init__(self):
        self.validator = ImagePromptPayloadValidator()
    
    def build_generation_prompt(
        self,
        material_name: str,
        contaminant_id: str,
        config: Dict
    ) -> str:
        # ... build prompt ...
        
        # VALIDATE BEFORE RETURNING
        result = self.validator.validate(
            prompt=final_prompt,
            material=material_name,
            contaminant=contaminant_id
        )
        
        # Log issues
        if not result.is_valid:
            logger.warning(f"Prompt validation failed:\n{result.format_report()}")
            
            # Decide how to handle failures
            if result.has_critical_issues:
                raise ValueError(f"Prompt validation failed critically: {result.get_summary()}")
            elif result.has_errors:
                logger.error("Prompt has errors but continuing...")
        
        return final_prompt
```

## Integration into Image Generation Workflow

**File**: `shared/image/generation/image_generator.py`

```python
from shared.image.validation.payload_validator import ImagePromptPayloadValidator

class ImageGenerator:
    def __init__(self):
        self.validator = ImagePromptPayloadValidator()
    
    def generate_image(
        self,
        prompt: str,
        material: str,
        contaminant: str
    ) -> ImageResult:
        # VALIDATE BEFORE API CALL
        validation_result = self.validator.validate(
            prompt=prompt,
            material=material,
            contaminant=contaminant
        )
        
        if validation_result.has_critical_issues:
            return ImageResult(
                success=False,
                error_message=f"Prompt validation failed: {validation_result.get_summary()}"
            )
        
        # Warn about errors/warnings
        if validation_result.has_errors:
            logger.warning(f"Prompt has errors:\n{validation_result.format_report()}")
        
        # Submit to Imagen API
        response = self.imagen_client.generate(prompt)
        
        return ImageResult(success=True, image=response.image)
```

## Testing

**Run tests**:
```bash
# Run all validator tests
pytest tests/image/test_payload_validator.py -v

# Run specific test class
pytest tests/image/test_payload_validator.py::TestLogicValidation -v

# Run single test
pytest tests/image/test_payload_validator.py::TestLogicValidation::test_color_contradiction -v
```

**Run demonstration**:
```bash
python3 scripts/image/demo_payload_validator.py
```

## Example Use Cases

### Use Case 1: Pre-Generation Validation
```python
# Before generating image, validate the prompt
validator = ImagePromptPayloadValidator()

result = validator.validate(
    prompt=user_prompt,
    material="Aluminum",
    contaminant="oil-grease"
)

if not result.is_valid:
    print(f"Cannot generate - validation failed:\n{result.format_report()}")
    return
```

### Use Case 2: Prompt Refinement Loop
```python
validator = ImagePromptPayloadValidator()

for attempt in range(max_attempts):
    result = validator.validate(prompt)
    
    if result.is_valid and not result.has_errors:
        break  # Good enough
    
    # Refine prompt based on issues
    prompt = refine_prompt_based_on_issues(prompt, result.issues)
```

### Use Case 3: Batch Validation
```python
validator = ImagePromptPayloadValidator()

for material, contaminant, prompt in prompt_queue:
    result = validator.validate(prompt, material, contaminant)
    
    if result.is_valid:
        submit_to_imagen(prompt)
    else:
        log_validation_failure(material, contaminant, result)
```

## Performance

- **Validation time**: ~10-50ms per prompt (depends on length)
- **Memory**: Minimal (<1MB per validator instance)
- **Thread-safe**: Yes (no shared state)

## Best Practices

### ✅ DO:
- Validate **before** submitting to Imagen API
- Check `result.has_critical_issues` first (blocks submission)
- Log warnings for manual review
- Use validator as early as possible (during prompt construction)

### ❌ DON'T:
- Skip validation to "save time" (wastes API credits)
- Ignore CRITICAL issues (will fail at API)
- Validate after API submission (too late)
- Create new validator for each validation (reuse instance)

## Troubleshooting

### Issue: Validator reports false positives

**Cause**: Overly strict patterns  
**Solution**: Review patterns in `payload_validator.py`, adjust if needed

### Issue: Validation too slow

**Cause**: Very long prompts (>10K characters)  
**Solution**: Pre-check length before running full validation

### Issue: Contradictions not detected

**Cause**: Non-standard phrasing  
**Solution**: Add new patterns to `CONTRADICTION_PATTERNS` dict

## Next Steps

1. **Integration**: Add validator to `SharedPromptBuilder.build_generation_prompt()`
2. **Pipeline**: Add validator to `ImageGenerator.generate_image()`
3. **Monitoring**: Log validation failures for analysis
4. **Refinement**: Adjust patterns based on real-world usage
5. **Documentation**: Add to `IMAGE_GENERATION_ARCHITECTURE.md`

## Related Documentation

- `IMAGE_GENERATION_ARCHITECTURE.md` - Overall image generation workflow
- `CONTAMINATION_VALIDATOR_GUIDE.md` - Material-contaminant compatibility
- `PROMPT_OPTIMIZATION.md` - Prompt length optimization strategies

---

**Status**: ✅ Complete - Ready for integration  
**Tests**: 40+ test cases covering all validation categories  
**Demo**: `scripts/image/demo_payload_validator.py` shows all features
