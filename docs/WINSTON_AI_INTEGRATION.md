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
The system is configured to use Winston.ai by default in `config/ai_detection.yaml`:
```yaml
provider: "winston"
```

## Scoring Interpretation

- **Score Range**: 0-100 (higher = more AI-like)
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
