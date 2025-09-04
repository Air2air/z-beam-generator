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

### Centralized AI Detection Configuration
The system uses a centralized `AI_DETECTION_CONFIG` in `run.py` that contains all AI detection thresholds and parameters:

```python
AI_DETECTION_CONFIG = {
    # Core AI Detection Thresholds
    "target_score": 70.0,                    # Winston.ai target score for human-like content (≥70 = human-like)
    "max_iterations": 5,                     # Maximum iterative improvement attempts
    "improvement_threshold": 3.0,            # Minimum score improvement to continue iterations
    "human_threshold": 75.0,                 # General human-like content threshold
    
    # Content Length Thresholds
    "min_text_length_winston": 300,          # Minimum characters for Winston.ai analysis
    "short_content_threshold": 400,          # Threshold for short content handling
    "min_content_length": 50,                # Minimum content length for validation
    
    # Fallback Scores (when AI detection fails or content is too short)
    "fallback_score_first_iteration": 60.0,  # Baseline score for first iteration
    "fallback_score_short_content": 55.0,    # Score for moderately short content
    "fallback_score_very_short": 40.0,       # Score for very short content
    "fallback_score_error": 50.0,            # Score when AI detection fails
    
    # Status Update Configuration
    "status_update_interval": 10,            # Seconds between status updates
    "iteration_status_frequency": 5,         # Show status every Nth iteration
    
    # Word Count Validation
    "word_count_tolerance": 1.5,             # Allow 50% tolerance over word limits (1.5x multiplier)
    
    # Country-Specific Word Count Limits
    "word_count_limits": {
        "taiwan": {"max": 380, "target_range": "340-380"},
        "italy": {"max": 450, "target_range": "400-450"},
        "indonesia": {"max": 400, "target_range": "350-400"},
        "usa": {"max": 320, "target_range": "280-320"}
    },
    
    # API Timeouts and Limits
    "winston_timeout_cap": 15,               # Maximum timeout for Winston.ai requests
    "max_tokens": 3000,                      # Maximum tokens for API requests
    "retry_delay": 0.5,                     # Delay between retries
    
    # Winston.ai Scoring Ranges
    "winston_human_range": (70, 100),       # Scores indicating human-written content
    "winston_unclear_range": (30, 70),      # Scores indicating unclear/uncertain content
    "winston_ai_range": (0, 30),            # Scores indicating AI-generated content
    
    # Early Exit Conditions
    "min_iterations_before_exit": 3,         # Minimum iterations before allowing early exit
    "early_exit_score_threshold": 10,        # Lenient threshold for early iterations (target - this value)
    
    # Configuration Optimization
    "deepseek_optimization_enabled": True,   # Enable DeepSeek-based configuration optimization
    "config_backup_enabled": True,           # Create backups before config changes
    
    # Logging and Debugging
    "enable_detailed_logging": True,         # Enable detailed AI detection logging
    "max_sentence_details": 5,               # Maximum sentence-level details to include in frontmatter
}
```

### Key Configuration Parameters

- **target_score**: The primary target for Winston.ai scores (default: 70.0)
- **winston_human_range**: Scores considered human-like (70-100)
- **winston_unclear_range**: Scores that are unclear/uncertain (30-70)
- **winston_ai_range**: Scores considered AI-generated (0-30)
- **min_text_length_winston**: Minimum characters required for analysis (300)
- **status_update_interval**: How often to show progress updates (10 seconds)
- **word_count_limits**: Country-specific word count limits for different authors

### Configuration Validation
Run the configuration test to validate all settings:
```bash
python3 test_ai_detection_config.py
```

Expected output:
```
🔧 Testing AI_DETECTION_CONFIG centralization...
✅ AI_DETECTION_CONFIG imported successfully
✅ All required configuration keys present
✅ All configuration values are valid
✅ Word count limits properly structured for all countries
✅ Winston.ai scoring ranges properly configured
✅ Configuration values are within reasonable ranges

🔧 Testing AI_DETECTION_CONFIG usage in components...
✅ Component import tests completed

🎉 ALL AI_DETECTION_CONFIG TESTS PASSED!
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
