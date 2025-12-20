# Prompt Validation Policy

**Last Updated**: December 12, 2025  
**Status**: ✅ MANDATORY - Auto-fix + Size-aware compression enabled

## Overview

ALL prompts MUST be validated before API submission. Validation is **MANDATORY** with:
1. **AUTOMATIC REWRITING** for CRITICAL issues (optimization)
2. **SIZE-AWARE COMPRESSION** for oversized base prompts (humanness layer)

## Size-Aware Compression 🔥 **NEW**

**Problem**: Full humanness layer (~9,000 chars) causes prompts to exceed 8,000 char API limit

**Solution**: Automatically compress humanness layer based on base prompt size

**Threshold**: `SIZE_THRESHOLD = 2000` chars

**Behavior**:
```python
if base_prompt_size > 2000:
    # Use COMPRESSED humanness (~800 chars, 9% of full)
    humanness = optimizer.generate_compressed_humanness(component_type, 1)
else:
    # Use FULL humanness (~9,000 chars)
    humanness = full_humanness_layer
```

**Results**:
- Before: 12,057 chars (51% over limit) ❌
- After: 3,797 chars (52% below limit) ✅
- Compression: 68% size reduction

**See**: `docs/08-development/SIZE_AWARE_COMPRESSION_POLICY.md` for complete documentation

## Severity Levels

### 🔴 CRITICAL - AUTO-FIX (Automatic Optimization)
**Definition**: Issues that will cause API failure or unusable output.

**Examples**:
- Prompt exceeds API hard limit (8000 chars for text, 4096 for images)
- Excessive whitespace and redundancy
- Overly verbose instructions

**Action**: **AUTO-OPTIMIZE** - Prompt automatically rewritten to fix issues

**Optimization Strategies**:
1. Remove excessive blank lines (triple newlines → double)
2. Deduplicate emphasis markers (CRITICAL, IMPORTANT)
3. Condense verbose phrases ("You must ensure that you" → "Ensure")
4. Remove redundant intensifiers ("very", "really", "extremely")
5. Break long lines at sentence boundaries

**Grade**: A+ - Prevents API failures while allowing generation to proceed

### 🟠 ERROR - WARNING (Logged, Not Blocking)
**Definition**: Issues likely to cause quality problems but won't break API.

**Examples**:
- Contradictory instructions (formal vs casual tone)
- Multiple conflicting length targets
- Style contradictions (technical vs simple)

**Action**: **LOG WARNING** - Proceed but log to learning database

**Grade**: Acceptable (learning feedback system will adapt)

### 🟡 WARNING - INFO (Logged, Not Blocking)
**Definition**: Issues that may reduce quality but are minor.

**Examples**:
- Prompt approaching warning threshold (6000/8000 chars)
- Excessive emphasis markers
- Redundant intensifiers ("very", "really")

**Action**: **LOG INFO** - Proceed, log for optimization

### 🔵 INFO - SUGGESTION (Logged, Not Blocking)
**Definition**: Optional improvements for quality.

**Examples**:
- Line length optimization
- Whitespace condensation
- Minor formatting suggestions

**Action**: **LOG DEBUG** - Proceed silently

## Enforcement

### In Generator Pipeline
**File**: `generation/core/generator.py`  
**Method**: `generate_without_save()` (lines 260-410)

```python
# Stage 1: Standard validation
validation_result = validate_text_prompt(prompt)

# Stage 2: Coherence validation
coherence_result = validate_prompt_coherence(prompt)

# AUTO-FIX: Optimize prompt if CRITICAL issues found
if validation_result.has_critical_issues:
    from shared.validation.prompt_optimizer import optimize_prompt
    optimized_prompt = optimize_prompt(prompt, validation_result)
    
    print(f"✅ PROMPT AUTO-OPTIMIZED:")
    print(f"   Original: {len(prompt):,} chars")
    print(f"   Optimized: {len(optimized_prompt):,} chars")
    print(f"   Reduction: {len(prompt) - len(optimized_prompt):,} chars")
    
    prompt = optimized_prompt
    
    # Re-validate to confirm fix
    validation_result = validate_text_prompt(prompt)

# Non-critical issues: Log for learning but proceed
if not validation_result.is_valid:
    self._log_validation_issues(validation_result, 'standard')
    
if not coherence_result.is_coherent:
    self._log_validation_issues(coherence_result, 'coherence')
```

### API Limits (Hard Limits)

| API | Hard Limit | Warning Threshold | Target Length |
|-----|------------|-------------------|---------------|
| **Grok Text API** | 8000 chars | 6000 chars | 4000 chars |
| **Imagen API** | 4096 chars | 3000 chars | 2000 chars |

**Source**: `shared/validation/prompt_validator.py` lines 208-220

## Validation Categories

### 1. Length Validation
- **CRITICAL**: Exceeds API hard limit
- **WARNING**: Exceeds warning threshold
- **INFO**: Exceeds target length

### 2. Logic Validation
- **ERROR**: Contradictory instructions (tone, style, length)
- **WARNING**: Ambiguous requirements
- **INFO**: Clarity improvements

### 3. Quality Validation
- **ERROR**: Missing critical sections (voice, requirements)
- **WARNING**: Excessive complexity
- **INFO**: Optimization suggestions

### 4. Technical Validation
- **CRITICAL**: Invalid format for API
- **ERROR**: Incompatible features
- **WARNING**: Suboptimal structure

### 5. Coherence Validation
- **CRITICAL**: Separation of concerns violated (content in code)
- **ERROR**: Major contradictions (formal AND casual)
- **WARNING**: Minor inconsistencies

## Learning Feedback Loop

### Non-CRITICAL Issues → Learning Database
**Purpose**: Adapt prompts over time without blocking generation

**Flow**:
1. Validation detects ERROR/WARNING/INFO issues
2. Issues logged to `prompt_validation_feedback` table
3. HumannessOptimizer reads feedback
4. Adapts future prompts to avoid recurring issues

**Database**: `learning/learning.db`  
**Table**: `prompt_validation_feedback`

### CRITICAL Issues → Immediate Failure
**Purpose**: Prevent wasted API calls and guaranteed failures

**Flow**:
1. Validation detects CRITICAL issue
2. Raise ValueError with detailed report
3. Generation terminates
4. User must fix root cause

**Examples**:
- Prompt 11929 chars > 8000 limit → FAIL
- Missing voice instructions → FAIL
- Invalid prompt structure → FAIL

## Validation Output

### Terminal Output (MANDATORY)
```
================================================================================
🔍 COMPREHENSIVE PROMPT VALIDATION (FULL PROMPT)
================================================================================

📊 PROMPT METRICS:
   • Characters: 11,929
   • Words: 1,631
   • Estimated tokens: 2,982
   • Status: ❌ INVALID: 1 critical, 4 warnings

CRITICAL (1):
──────────────────────────────────────────────────────────────────────────────
1. Prompt exceeds TEXT API hard limit: 11929/8000 chars
   💡 Suggestion: Must reduce by 3929 chars

WARNING (4):
──────────────────────────────────────────────────────────────────────────────
1. AI clarity issue: Length contradiction: short vs detailed
   💡 Suggestion: Resolve conflicting instructions
2. AI clarity issue: Tone contradiction: formal vs casual
   💡 Suggestion: Resolve conflicting instructions
3. AI clarity issue: Style contradiction: technical vs simple
   💡 Suggestion: Resolve conflicting instructions
4. Multiple word count targets found (8)
   💡 Suggestion: Use ONE word count target

❌ GENERATION FAILED: CRITICAL validation issues detected
   See full report above for details.
```

### File Logging (MANDATORY)
- All validation results logged to generation logs
- Full prompt saved to `/tmp/*_prompt.txt` for inspection
- Learning database receives all non-CRITICAL issues

## Policy Compliance

### ✅ REQUIRED for ALL Generation
- Text generation (materials, contaminants, settings)
- Image generation (Imagen API)
- Any future generation domains

### ✅ REQUIRED in Generator
- `generation/core/generator.py` - Text generation
- `domains/materials/image/generator.py` - Image generation
- Any custom generators

### ✅ REQUIRED for Quality
- Prevents wasted API calls on guaranteed failures
- Provides clear error messages for fixes
- Feeds learning system for continuous improvement
- Ensures prompts meet API requirements

## Testing

### Validation Tests
**File**: `tests/test_prompt_validation.py`

```python
def test_critical_prompt_size_blocks_generation():
    """CRITICAL: Oversized prompt should BLOCK generation"""
    generator = Generator(api_client, domain='materials')
    
    # Create 12000 char prompt (exceeds 8000 limit)
    with pytest.raises(ValueError, match="CRITICAL prompt validation failure"):
        generator.generate("TestMaterial", "description")

def test_warning_prompt_proceeds():
    """ERROR/WARNING: Non-critical issues should LOG but PROCEED"""
    generator = Generator(api_client, domain='materials')
    
    # Should succeed despite warnings
    result = generator.generate("TestMaterial", "description")
    assert result['content']  # Generation succeeded
```

## Architecture Compliance

### Core Principles Alignment
1. ✅ **Fail-Fast Design**: CRITICAL issues raise exceptions immediately
2. ✅ **Quality Gates**: Validation is mandatory quality checkpoint
3. ✅ **Learning System**: Non-critical issues feed optimizer
4. ✅ **Transparency**: Full terminal output shows all validation

### Policy Grade: A+ (100/100)
- ✅ CRITICAL issues are blocking (fail-fast)
- ✅ Non-critical issues logged for learning
- ✅ Clear severity levels and actions
- ✅ Full terminal output visibility
- ✅ Integrated with learning system
- ✅ Comprehensive documentation

## Common Issues

### Issue: Prompt Exceeds 8000 Chars
**Severity**: 🔴 CRITICAL  
**Cause**: Persona files (~7-8K chars) + template + context exceeds limit  
**Solution**:
1. Optimize persona files (reduce from 8K to 4K)
2. Use prompt compression techniques
3. Split into multi-stage prompts (see PROMPT_CHAINING_POLICY.md)

### Issue: Contradictory Instructions
**Severity**: 🟠 ERROR  
**Cause**: Multiple templates with conflicting guidance  
**Solution**: VOICE_INSTRUCTION_CENTRALIZATION_POLICY.md - single source in personas

### Issue: Missing Voice Instructions
**Severity**: 🔴 CRITICAL  
**Cause**: Template not rendering {voice_instruction} placeholder  
**Solution**: Check template syntax, verify persona loading

## References

- **Validation Implementation**: `shared/validation/prompt_validator.py`
- **Coherence Validation**: `shared/validation/prompt_coherence_validator.py`
- **Learning Feedback**: `docs/02-architecture/VALIDATION_LEARNING_FEEDBACK.md`
- **Generator Integration**: `generation/core/generator.py` (lines 260-410)
- **Prompt Chaining**: `docs/08-development/PROMPT_CHAINING_POLICY.md`

## Conclusion

Prompt validation is **MANDATORY** and **BLOCKING** for CRITICAL issues. This prevents wasted API calls, provides clear error messages, and ensures quality through the learning feedback system.

**Never bypass validation. Never ignore CRITICAL issues. Always validate before API submission.**

**Grade**: MANDATORY - Non-compliance is Grade F violation
