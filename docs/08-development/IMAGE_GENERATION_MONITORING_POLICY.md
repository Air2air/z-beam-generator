# Image Generation Monitoring Policy

**Date**: November 30, 2025  
**Status**: MANDATORY  
**Scope**: All image generation operations

---

## Policy Statement

**ALL image generation operations MUST have active terminal logging end-to-end, and AI assistants MUST monitor this output for bottlenecks during generation.**

---

## Requirements

### 1. Real-Time Terminal Logging (MANDATORY)

Every stage of image generation MUST print progress to terminal:

```
================================================================================
🔬 MATERIAL IMAGE GENERATION: [Material Name]
================================================================================
📊 Configuration:
   • Category: [category]
   • Context: [context description]
   • Shape Override: [shape]

✅ Early validation passed
🔬 Researching contamination data...

📦 Loading contamination patterns from Contaminants.yaml...
📋 Selected [N] patterns for [Material]: [pattern-ids]
   ✅ Selected [N] patterns (ZERO API calls)
   📊 [N]/[N] have rich appearance data

🔧 Researching assembly components for complex part...
   📋 Assembly research [loaded from cache / calling API]
   ✅ Found [N] assembly components

🧠 Loaded learned feedback for [category]
📝 Loaded user feedback: [N] chars
📐 Prompt optimized: [before] → [after] chars

================================================================================
🎨 ATTEMPT [N]/[MAX]
================================================================================
🎨 [GEMINI] Generating image...
✅ Image saved to: [path]
   • Size: [N] KB

🔍 Validating image with Gemini Vision...

📊 VALIDATION RESULTS:
   • Realism Score: [N]/100
   • Text/Labels: [✅ None / ❌ DETECTED]
   • Position Shift: [✅ Appropriate / ❌ Identical]
   • Status: [✅ PASSED / ❌ FAILED]
```

### 2. Bottleneck Monitoring (MANDATORY for AI Assistants)

AI assistants MUST:

1. **Watch for slow stages** - If any stage takes >30 seconds without output, investigate
2. **Identify API timeouts** - Note if Imagen or Gemini calls exceed expected times
3. **Report hanging operations** - If no output for 60+ seconds, alert user
4. **Track typical timings**:
   - Contamination pattern loading: <1 second
   - Assembly research (cached): <1 second
   - Assembly research (API): 5-15 seconds
   - Imagen generation: 15-45 seconds
   - Validation: 5-15 seconds
   - **Total expected**: 30-90 seconds

### 3. Stage Timestamps (RECOMMENDED)

Add timestamps to key stages for performance tracking:

```python
import time
start = time.time()
# ... operation ...
print(f"✅ Operation complete ({time.time() - start:.1f}s)")
```

### 4. Error Visibility (MANDATORY)

All errors MUST:
- Print to terminal immediately (not just log files)
- Include stack trace for debugging
- Show which stage failed

```python
except Exception as e:
    print(f"❌ [STAGE] Failed: {e}")
    import traceback
    traceback.print_exc()
    raise
```

---

## AI Assistant Responsibilities

When running image generation, AI assistants MUST:

1. **Run with full output** - Never truncate or hide terminal output
2. **Monitor actively** - Watch for stalls, errors, or unexpected behavior
3. **Report issues immediately** - Don't wait for command to complete if clearly hung
4. **Note performance** - Track if generation is slower than expected
5. **Ask about hangs** - If operation exceeds 2 minutes without progress, check with user

---

## Implementation Checklist

- [ ] `generate.py` - Full stage logging with timing
- [ ] `material_generator.py` - Research stage logging
- [ ] `assembly_researcher.py` - API call logging with timing
- [ ] `contamination_pattern_selector.py` - Pattern selection logging
- [ ] `validator.py` - Validation stage logging
- [ ] `gemini_client.py` - API call timing

---

## Anti-Patterns

❌ **Silent operations** - No output during long-running tasks  
❌ **Log-only output** - Writing to files without terminal display  
❌ **Batch output** - Collecting all output and showing at end  
❌ **Truncated output** - Using `tail` or `head` on generation output  
❌ **Background execution** - Running generation without monitoring  

---

## Enforcement

- All image generation code must comply with this policy
- Code reviews should verify terminal logging is present
- AI assistants failing to monitor output should be corrected
- Performance regressions should be investigated

---

## Related Policies

- `TERMINAL_LOGGING_POLICY.md` - General terminal logging requirements
- `PROMPT_CHAINING_POLICY.md` - Multi-stage operation logging
