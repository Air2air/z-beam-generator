# Motion Blur in Historical Photography

## Overview
Motion blur effects have been added to enhance historical authenticity by mimicking the long exposure times of period cameras.

## Implementation
**File**: `regions/image/prompts/city_image_prompts.py`

### Motion Blur Effects Applied:
1. **Moving vehicles**: Slight blur and ghosting from long exposure times
2. **Pedestrians in motion**: Slight blur characteristic of period photography
3. **Rotating wheels**: Rotational motion blur on vehicle wheels
4. **Static elements**: Buildings and storefronts remain sharp

### Era-Appropriate Context
The motion blur description includes the decade context (e.g., "typical of 1930s cameras") to ensure the AI generates period-appropriate blur characteristics, not modern motion blur effects.

## Negative Prompt Updates
**File**: `regions/image/negative_prompts.py`

Updated to **allow** motion blur on moving elements while **preventing**:
- Motion blur on static buildings
- Motion blur on stationary objects
- Excessive motion blur that obscures the subject
- Unrealistic motion blur patterns

## Why This Matters for Historical Accuracy

### 1920s-1940s Camera Technology
- Typical shutter speeds: 1/25 to 1/100 second
- Moving vehicles at 20-30 mph would show noticeable blur
- Pedestrians walking would have slight ghosting
- Rotating wheels would show motion trails

### Visual Authenticity
This creates the characteristic look of street photography from the era where:
- Subject (buildings) is sharp and in focus
- Moving elements capture "frozen motion" with blur
- Overall effect feels genuine rather than artificially sharp

## Example Prompt Fragment
```
Period-appropriate motion blur: moving vehicles show slight blur and ghosting 
from long exposure times typical of 1930s cameras, any pedestrians in motion 
have slight blur, wheels show rotational motion blur, but static buildings 
and storefronts remain sharp.
```

## Testing
Test with any city generation command:
```bash
python3 regions/image/generate.py --city "Oakland" --county "Alameda County" --preset "aged_1930s"
```

The motion blur will automatically be included in all generated images, providing historically accurate photographic characteristics.

## Technical Notes
- Motion blur is subtle, not excessive
- Enhances realism without compromising clarity
- Era-specific (adapts to decade from config)
- Balanced with sharp focus on main subject (buildings/street)
