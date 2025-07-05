# Anti-Hardcoding Refactoring Guide

This guide explains how to complete the anti-hardcoding refactor for the Z-Beam generator.

## Current Status

✅ **Completed:**
- GlobalConfigManager implemented and integrated
- Anti-hardcoding detection and auto-fix tools created
- Major workflow restructuring (moved to /generator)
- AI detection service updated to use config manager
- 8 automatic fixes applied (105 → 90 violations remaining)

🔄 **In Progress:**
- Refactoring remaining 90 hardcoded configuration values
- Adding get_config() imports where needed
- Testing all modules after refactoring

## Quick Start

### 1. Run Detection
```bash
python3 generator/scripts/detect_hardcoding.py
```

### 2. Apply Auto-Fixes
```bash
python3 generator/scripts/fix_hardcoding.py
```

### 3. Manual Fixes
Follow the patterns below for remaining violations.

## Common Refactoring Patterns

### Temperature Values
```python
# ❌ Before
temperature=0.3
temperature=0.6  
temperature=0.7

# ✅ After
from config.global_config import get_config

temperature=get_config().get_detection_temperature()
temperature=get_config().get_content_temperature()
temperature=get_config().get_improvement_temperature()
```

### Thresholds
```python
# ❌ Before
ai_threshold=25
human_threshold=25
natural_voice_threshold=25

# ✅ After
ai_threshold=get_config().get_ai_detection_threshold()
human_threshold=get_config().get_natural_voice_threshold()
natural_voice_threshold=get_config().get_natural_voice_threshold()
```

### API Configuration
```python
# ❌ Before
provider="anthropic"
model="claude-3-5-sonnet"
base_url="https://api.anthropic.com"
timeout=60

# ✅ After
provider=get_config().get_provider()
model=get_config().get_model()
base_url=get_config().get_api_url()
timeout=get_config().get_api_timeout()
```

### Iterations and Limits
```python
# ❌ Before
iterations_per_section=3
max_article_words=1200
max_iterations=5

# ✅ After
iterations_per_section=get_config().get_iterations_per_section()
max_article_words=get_config().get_max_article_words()
max_iterations=get_config().get_iterations_per_section()
```

### Function Parameters
```python
# ❌ Before (interface definitions)
def detect_ai_likelihood(
    self,
    content: str,
    temperature: float = 0.3,
    timeout: int = 60,
):

# ✅ After (use Optional and document config usage)
def detect_ai_likelihood(
    self,
    content: str,
    temperature: Optional[float] = None,  # Uses get_config().get_detection_temperature()
    timeout: Optional[int] = None,       # Uses get_config().get_api_timeout()
):
```

### Implementation Pattern
```python
# ✅ Implementation should handle None values
def detect_ai_likelihood(
    self,
    content: str,
    temperature: Optional[float] = None,
    timeout: Optional[int] = None,
):
    if temperature is None:
        temperature = get_config().get_detection_temperature()
    if timeout is None:
        timeout = get_config().get_api_timeout()
    
    # Use the values...
```

## Files Requiring Manual Attention

### High Priority (Core Logic)
1. `core/interfaces/services.py` - Interface definitions
2. `core/domain/models.py` - Data models with defaults
3. `core/services/detection_service.py` - Core detection logic
4. `infrastructure/api/client.py` - API client
5. `modules/api_client.py` - Legacy API client

### Medium Priority (Business Logic)
1. `core/services/content_service.py` - Content generation
2. `modules/content_generator.py` - Legacy content generator
3. `modules/runner.py` - Module runner
4. `core/application.py` - Application logic

### Lower Priority (Configuration)
1. `config/enhanced_settings.py` - Settings validation
2. `core/services/detection_scoring_system.py` - Scoring algorithms
3. Test files and utilities

## Special Cases

### Constants and Enums
```python
# ❌ Before
GEMINI = "GEMINI"
OPENAI = "OPENAI"

# ✅ After - Use enum or get from config
class ProviderType(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai" 
    GOOGLE = "google"
    GROQ = "groq"

# Or get dynamically
provider_type = get_config().get_provider().upper()
```

### Validation Logic
```python
# ❌ Before
if not 0 <= self.ai_detection_threshold <= 100:
    raise ValueError("AI threshold must be 0-100")

# ✅ After
min_threshold, max_threshold = get_config().get_threshold_bounds()
if not min_threshold <= self.ai_detection_threshold <= max_threshold:
    raise ValueError(f"AI threshold must be {min_threshold}-{max_threshold}")
```

### Legacy Compatibility
```python
# ✅ For backward compatibility in data models
@dataclass
class GenerationConfig:
    temperature: float = field(default_factory=lambda: get_config().get_content_temperature())
    timeout: int = field(default_factory=lambda: get_config().get_api_timeout())
```

## Testing Changes

### 1. Run Detection Again
```bash
python3 generator/scripts/detect_hardcoding.py
```

### 2. Test Basic Functionality
```bash
python3 workflow.py check-config
python3 workflow.py test
```

### 3. Test Generation
```bash
python3 run.py  # Should work without errors
```

## Import Requirements

Add this import to any file using config:
```python
from config.global_config import get_config
```

For type hints:
```python
from typing import Optional
```

## Goals

- **Zero hardcoded configuration values** outside of config files
- **All config access through get_config()** calls
- **No magic numbers** in business logic
- **Consistent API** for configuration access
- **Easy testing** with config overrides

## Benefits

✅ **Single source of truth** for all configuration  
✅ **Easy to change** provider/model/settings  
✅ **Prevents Claude** from hardcoding values  
✅ **Better testability** with config mocking  
✅ **Runtime validation** of configuration  
✅ **Type safety** with proper interfaces  

## Next Steps

1. **Continue manual refactoring** following the patterns above
2. **Run detection tool** regularly to track progress  
3. **Test thoroughly** after each major change
4. **Add CI checks** to prevent future hardcoding
5. **Update documentation** as needed

The goal is to get from 90 violations to 0 violations while maintaining full functionality.
