# No Cache Policy

**Date**: November 18, 2025  
**Status**: ACTIVE

## Policy Statement

**ALL API response caching is DISABLED** to ensure fresh evaluations with every generation.

## Rationale

### Critical Tone Testing
When testing the subjective evaluation fix (removing hardcoded system prompts), cached responses would show OLD evaluation results instead of the NEW critical tone from templates.

### Fresh Evaluations Required
Every generation must hit the actual API to:
- ✅ Use current template instructions (critical tone)
- ✅ Reflect latest learned patterns
- ✅ Show real-time parameter adjustments
- ✅ Validate fixes immediately

## Configuration Changes

### shared/config/settings.py

```python
"RESPONSE_CACHE": {
    "enabled": False,  # DISABLED for fresh evaluations
    "storage_location": "/tmp/z-beam-response-cache",
    "ttl_seconds": 86400,
    "max_size_mb": 1000,
    "key_strategy": "prompt_hash_with_model",
}
```

```python
"pipeline_integration": {
    "cache_validations": False,  # DISABLED for fresh validations
    # ... other settings
}
```

## Impact

### Performance
- **Slower**: Every generation makes fresh API calls
- **Cost**: Higher API usage (no cache hits)
- **Trade-off**: Accurate results worth the cost

### Benefits
- ✅ **Immediate feedback**: See fixes take effect instantly
- ✅ **No stale data**: Every evaluation uses current configuration
- ✅ **Testing reliability**: Confident that results reflect current code
- ✅ **Learning accuracy**: True learning loop without cached interference

## When to Re-Enable

Caching can be re-enabled AFTER:
1. ✅ Critical tone fix is verified working
2. ✅ All subjective evaluation changes are tested
3. ✅ System is stable and production-ready
4. ✅ Cost optimization becomes priority

## Cache Clearing

To clear existing cached responses:
```bash
rm -rf /tmp/z-beam-response-cache/*
```

## Testing Impact

### Before (With Cache)
```
Generation 1: Fresh API call → Evaluation: "authentically human" (old tone)
Generation 2: Cache hit → Evaluation: "authentically human" (stale)
Generation 3: Cache hit → Evaluation: "authentically human" (stale)
```

### After (No Cache)
```
Generation 1: Fresh API call → Evaluation: "borders on problematic" (new critical tone)
Generation 2: Fresh API call → Evaluation: "questionable phrasing" (new critical tone)
Generation 3: Fresh API call → Evaluation: "could tip into AI-like" (new critical tone)
```

## Monitoring

Watch for these indicators that caching should be re-enabled:
- 🟡 API costs exceeding budget
- 🟡 Generation times too slow (>2 minutes per micro)
- 🟡 Rate limiting issues from providers
- 🟢 All fixes validated and stable

## Related Documents

- `docs/08-development/PROMPT_PURITY_POLICY.md` - Why we removed hardcoded prompts
- `docs/08-development/TERMINAL_OUTPUT_POLICY.md` - Real-time logging requirements
- `REALISM_GATE_IMPLEMENTATION_NOV18_2025.md` - Critical tone implementation
