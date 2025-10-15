# Multi-Provider AI Detection Architecture Proposal

## Overview
Extend the current Winston.ai composite scoring to include multiple AI detection services for more robust bias correction.

## Proposed Architecture

### Current State
```
Content → Winston.ai → Composite Scoring → 59.5%
Content → External Tools → 17% (still poor)
```

### Proposed State
```
Content → Multi-Provider Detection → Ensemble Scoring → 70-85%
├── Winston.ai (with composite scoring)
├── GPTZero API
├── Originality.ai API
├── Copyleaks API
└── Custom ML Model (trained on technical content)
```

## Implementation Plan

### Phase 1: Multi-Provider Detection Service
**File**: `optimizer/ai_detection/providers/multi_provider.py`

```python
class MultiProviderDetector:
    def __init__(self):
        self.providers = {
            'winston': WinstonProvider(),
            'gptzero': GPTZeroProvider(),
            'originality': OriginalityProvider(),
            'copyleaks': CopyleaksProvider()
        }
        self.ensemble_weights = {
            'winston': 0.3,  # Reduced due to known bias
            'gptzero': 0.25,
            'originality': 0.25,
            'copyleaks': 0.2
        }
    
    def analyze_with_ensemble(self, content):
        results = {}
        for name, provider in self.providers.items():
            try:
                result = provider.analyze_text(content)
                results[name] = result
            except Exception as e:
                logger.warning(f"Provider {name} failed: {e}")
        
        return self.calculate_ensemble_score(results)
```

### Phase 2: Intelligent Score Fusion
**Algorithm**: Weighted ensemble with bias correction

```python
def calculate_ensemble_score(self, provider_results):
    # Apply provider-specific bias corrections
    corrected_scores = {}
    
    for provider, result in provider_results.items():
        if provider == 'winston' and self.is_technical_content(result.content):
            # Apply our existing composite scoring
            corrected_scores[provider] = self.apply_winston_composite(result)
        elif provider == 'gptzero' and result.score < 30:
            # GPTZero tends to over-detect technical content
            corrected_scores[provider] = min(result.score + 15, 100)
        else:
            corrected_scores[provider] = result.score
    
    # Calculate weighted ensemble
    ensemble_score = sum(
        corrected_scores[provider] * self.ensemble_weights[provider]
        for provider in corrected_scores
    )
    
    return ensemble_score
```

## Benefits
1. **Reduced Single-Point Bias**: No reliance on one detector
2. **Robust Scoring**: Multiple perspectives on content quality
3. **Adaptive Weighting**: Adjust weights based on content type
4. **Graceful Degradation**: Works even if some providers fail
