# Grok API Limitations

**Date**: November 15, 2025  
**Status**: Active constraint on production system

---

## Overview

The X.AI Grok API has specific parameter limitations that affect how the z-beam-generator system implements dynamic content generation.

## Unsupported Parameters

### ❌ Frequency Penalty
**Parameter**: `frequency_penalty`  
**Status**: NOT SUPPORTED  
**Error**: `Model grok-4-fast does not support parameter frequencyPenalty`  
**HTTP Status**: 400 Bad Request

### ❌ Presence Penalty
**Parameter**: `presence_penalty`  
**Status**: NOT SUPPORTED  
**Error**: `Model grok-4-fast does not support parameter presencePenalty`  
**HTTP Status**: 400 Bad Request

## System Design Response

### Why We Calculate Penalties Anyway

Even though Grok doesn't accept penalty parameters, the system **still calculates them**. This design serves multiple purposes:

1. **Research & Learning**: Parameters are logged to `winston_feedback.db` for correlation analysis
2. **Future Provider Switching**: OpenAI, Anthropic, and other providers DO support penalties
3. **ML Training Data**: Builds dataset for understanding parameter effects across providers
4. **Architecture Consistency**: Maintains uniform parameter flow regardless of provider

### Implementation Strategy

```python
# In shared/api/client.py (line 350-357):
if "grok" not in self.model.lower():
    # Only send penalties to non-Grok providers
    payload["frequency_penalty"] = request.frequency_penalty
    payload["presence_penalty"] = request.presence_penalty
# Grok requests omit these fields entirely
```

### What Actually Works with Grok

✅ **Supported Parameters**:
- `temperature` (0.0 - 2.0)
- `max_tokens` (1 - 131,072)
- `top_p` (0.0 - 1.0)
- System prompt modifications
- Dynamic prompt engineering

## Workarounds

Since penalties aren't available, the system relies on:

1. **Dynamic Prompts**: Adjust prompt structure based on humanness_intensity
2. **Temperature Variation**: Use temperature (0.5 - 1.1) as primary humanization lever
3. **Structural Anti-AI Patterns**: Inject variety through prompt instructions
4. **Voice Parameter Mixing**: Vary author voice traits dynamically

## Provider Comparison

| Feature | Grok | OpenAI | Anthropic |
|---------|------|--------|-----------|
| Frequency Penalty | ❌ | ✅ | ✅ |
| Presence Penalty | ❌ | ✅ | ✅ |
| Temperature | ✅ | ✅ | ✅ |
| Max Tokens | ✅ | ✅ | ✅ |
| Top P | ✅ | ✅ | ✅ |

## Future Considerations

### Provider Switching
To fully utilize penalty-based humanization:
```python
# In shared/config/settings.py, change default provider:
DEFAULT_PROVIDER = "openai"  # Instead of "grok"
```

### Multi-Provider Strategy
Potential architecture for testing penalties:
- **Grok**: Fast, low-cost generation (production)
- **OpenAI**: Penalty-enabled generation (research/testing)
- **Comparison**: A/B test penalty effectiveness

## Testing

### Test Coverage
Location: `tests/test_method_chain_robustness.py`

```python
def test_api_penalties_calculated_for_logging(self):
    """
    Verify penalties are calculated even though Grok doesn't support them.
    Design allows future provider switching and ML research.
    """
    config = DynamicConfig()
    all_params = config.get_all_generation_params('micro')
    
    assert 'penalties' in all_params['api_params']
    # Penalties calculated but NOT sent to Grok
```

## References

- **API Client**: `shared/api/client.py` (lines 350-357)
- **Generator**: `generation/core/generator.py` (single-pass generation)
- **Database Schema**: `postprocessing/detection/winston_feedback_db.py` (generation_parameters table)
- **X.AI Documentation**: https://docs.x.ai/api

## Related Issues

- Dynamic penalties implementation: November 14-15, 2025
- Parameter logging: 100% coverage achieved November 15, 2025
- Grok limitation discovered: November 15, 2025 (during batch testing)

---

**Key Takeaway**: Penalties are calculated and logged for research purposes, but correctly filtered out before sending to Grok API. This maintains architecture consistency while respecting provider limitations.
