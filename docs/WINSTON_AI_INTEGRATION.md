# Winston.ai AI Detection Integration

## Overview
Winston.ai has been integrated as the primary AI detection provider for the Z-Beam content generation system. This replaces the previous GPTZero integration with Winston.ai's more advanced detection capabilities.

## Setup Instructions

### 1. Get Winston.ai API Key
1. Sign up for a Winston.ai account at [https://gowinston.ai](https://gowinston.ai)
2. Navigate to your API settings to get your API key
3. The API key should look like: `winston-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`

### 2. Configure API Key
You can set the Winston.ai API key in two ways:

#### Option A: Environment Variable (Recommended)
```bash
export WINSTON_API_KEY="your-winston-api-key-here"
```

#### Option B: Configuration File
Update `config/ai_detection.yaml`:
```yaml
winston:
  api_key: "your-winston-api-key-here"
  base_url: "https://api.gowinston.ai"
```

### 3. Verify Configuration
Run the test to verify everything is working:
```bash
python3 tests/test_winston_provider.py
```

## API Features

### Request Format
```json
{
  "text": "Your content to analyze (minimum 300 characters)",
  "sentences": true,
  "language": "en"
}
```

### Important Notes
- **Minimum Text Length**: Winston.ai requires at least 300 characters for analysis
- **Sentence Analysis**: Set `sentences: true` to get per-sentence scoring
- **Credit Usage**: Each API call consumes credits based on text length

### Response Format
```json
{
  "status": 200,
  "score": 45.67,
  "sentences": [
    {
      "text": "Sample sentence",
      "score": 42.3
    }
  ],
  "readability_score": 78.5,
  "credits_used": 1,
  "credits_remaining": 999,
  "attack_detected": {
    "zero_width_space": false,
    "homoglyph_attack": false
  }
}
```

## Integration Points

### Content Component
The Winston.ai provider is automatically used by the content component's quality scoring system:

```python
# In FailFastContentGenerator
if self.enable_scoring and self.content_scorer:
    quality_score = self.content_scorer.score_content(
        content, material_data, author_info, frontmatter_data
    )
```

### Configuration

### Dynamic AI Detection Configuration System
The system now uses a dynamic configuration system that calculates optimal parameters based on content characteristics and author information, replacing the old static `AI_DETECTION_CONFIG`. This provides intelligent, adaptive configuration that adjusts to different content types and writing styles.

#### Dynamic Configuration Features
- **Content-Type Intelligence**: Automatically classifies content as technical, marketing, educational, or creative
- **Author Country Tuning**: Adjusts parameters based on author location (Italy: +2.0 expressiveness, Taiwan: -1.0 formality, etc.)
- **Adaptive Thresholds**: Calculates optimal target scores and human thresholds based on content length and type
- **Real-time Optimization**: Uses DeepSeek API for configuration optimization when enabled

#### Dynamic Configuration Generation
The `create_dynamic_ai_detection_config()` function in `run.py` generates configuration parameters using 20+ calculation functions:

```python
# Example dynamic configuration generation
config = create_dynamic_ai_detection_config(
    content_type="technical",  # inferred from material and context
    author_country="italy",    # from author information
    content_length=1200,       # estimated content length
    material_name="stainless_steel"
)

# Returns adaptive configuration like:
{
    "target_score": 72.5,           # Adjusted for technical content + Italy author
    "human_threshold": 77.8,        # Content-type specific threshold
    "max_iterations": 4,            # Optimized for content length
    "word_count_limits": {          # Country-specific limits
        "max": 450,
        "target_range": "400-450"
    }
    # ... 15+ additional adaptive parameters
}
```

#### Key Dynamic Parameters

- **target_score**: Calculated based on content type and author country
  - Technical content: Base 70.0 + adjustments
  - Marketing content: Base 75.0 + adjustments
  - Educational content: Base 68.0 + adjustments
  - Creative content: Base 72.0 + adjustments

- **human_threshold**: Content-type specific thresholds
  - Technical: 75.0-80.0 range
  - Marketing: 78.0-83.0 range
  - Educational: 73.0-78.0 range
  - Creative: 76.0-81.0 range

- **max_iterations**: Optimized based on content length
  - Short content (< 500 chars): 3 iterations
  - Medium content (500-1500 chars): 4-5 iterations
  - Long content (> 1500 chars): 5-6 iterations

- **word_count_limits**: Author country-specific limits
  - Taiwan: 340-380 words (formal, concise)
  - Italy: 400-450 words (expressive, detailed)
  - Indonesia: 350-400 words (balanced approach)
  - USA: 280-320 words (direct, efficient)

#### Configuration Calculation Functions
The system includes 20+ specialized calculation functions:

- `_calculate_optimal_target_score()`: Content type + author adjustments
- `_calculate_human_threshold()`: Content-specific human thresholds
- `_infer_content_type()`: Automatic content classification
- `_estimate_content_length()`: Content length prediction
- `_calculate_max_iterations()`: Iteration optimization
- `_adjust_for_author_country()`: Country-specific parameter tuning
- `_calculate_fallback_scores()`: Adaptive fallback scoring

#### Configuration Validation
Run the dynamic configuration test to validate the system:
```bash
python3 tests/test_dynamic_ai_detection_config.py
```

Expected output:
```
🔧 Testing Dynamic AI Detection Configuration...
✅ Dynamic config generation successful
✅ Content type inference working
✅ Author country adjustments applied
✅ All calculation functions validated
✅ Configuration values within expected ranges
✅ DeepSeek optimization integration verified

🎉 ALL DYNAMIC CONFIG TESTS PASSED!
```

## Scoring Interpretation

- **Score Range**: 0-100 (lower = more AI-like)
- **Classification**:
  - `< 30`: "human"
  - `30-70`: "unclear"
  - `> 70`: "ai"
- **Confidence**: Based on distance from 50 (neutral point)

## Error Handling

The provider includes comprehensive error handling for:
- API timeouts
- Authentication failures
- Rate limiting
- Network issues
- Invalid responses

## Testing

Run the Winston.ai provider test:
```bash
python3 tests/test_winston_provider.py
```

Expected output when API key is not configured:
```
✅ Winston.ai provider initialized successfully
⚠️  Winston.ai service is not available (API key may not be configured)
```

Expected output when API key is configured and service is available:
```
✅ Winston.ai provider initialized successfully
✅ Winston.ai service is available
✅ Text analysis successful
   Score: 36.72
   Classification: unclear
   Confidence: 0.27
   Processing time: 0.82s
   Provider: winston
   Additional details:
     Readability score: 25.76
     Credits used: 103
```
