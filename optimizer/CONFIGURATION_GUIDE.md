# Z-Beam Optimizer Configuration Guide

## Overview

The Z-Beam Optimizer uses a hierarchical configuration system that allows flexible customization while maintaining sensible defaults. This guide covers all configuration options and best practices.

## Automatic Configuration Discovery

🎯 **Most services support automatic configuration loading** - you can initialize services without explicitly providing configuration:

```python
# ✅ Automatic configuration loading (recommended)
service = AIDetectionOptimizationService()  # Loads config automatically
workflow = IterativeWorkflowService()       # Loads config automatically

# ✅ Explicit configuration (for custom setups)
service = AIDetectionOptimizationService(my_config)
```

### Configuration Discovery Order

Services automatically discover configuration in this priority order:

1. **Explicitly provided ServiceConfiguration** (highest priority)
2. **Service-specific config files** (e.g., `ai_detection_service_config.yaml`)
3. **Environment variables** (prefixed with service name)
4. **Default configuration values** (built-in fallbacks)
5. **Raises ConfigurationError** if none found (lowest priority)

### Service-Specific Config Loading Functions

Each service has its own config loader:

```python
# Available automatic config loaders
from optimizer.services.ai_detection_optimization import get_ai_detection_service_config
from optimizer.services.iterative_workflow import get_workflow_service_config
from optimizer.services.quality_assessment import get_quality_service_config

# These are called automatically when config=None
ai_config = get_ai_detection_service_config()        # Auto-loaded
workflow_config = get_workflow_service_config()      # Auto-loaded
```

## Configuration Hierarchy

```
1. Default Values (hardcoded in code)
2. Environment Variables
3. Configuration Files (YAML/JSON)
4. Runtime Configuration (API parameters)
```

Higher levels override lower levels, allowing progressive customization.

## Core Configuration

### Service Configuration

All optimizer services use the standard `ServiceConfiguration` format:

```python
from optimizer.services import ServiceConfiguration

config = ServiceConfiguration(
    name="service_name",
    version="1.0.0",
    enabled=True,
    settings={
        # Service-specific settings
    }
)
```

## Service Initialization Patterns

### ✅ **Recommended: Automatic Configuration**

```python
# 🎯 Best Practice - Let services load their own configuration
from optimizer.services.ai_detection_optimization import AIDetectionOptimizationService
from optimizer.services.iterative_workflow import IterativeWorkflowService

# These automatically load appropriate configuration
ai_service = AIDetectionOptimizationService()    # ✅ Simple & reliable
workflow = IterativeWorkflowService()           # ✅ Simple & reliable
```

### ⚠️ **Advanced: Custom Configuration**

```python
# 🔧 Advanced - For custom setups or testing
from optimizer.services import ServiceConfiguration

custom_config = ServiceConfiguration(
    name="custom_ai_detection",
    settings={"target_score": 85.0, "max_iterations": 5}
)

ai_service = AIDetectionOptimizationService(custom_config)  # ✅ Custom behavior
```

### 🚫 **Common Mistake: Assuming Config is Required**

```python
# ❌ DON'T DO THIS - Unnecessary complexity
config = get_ai_detection_service_config()  # Manual loading
service = AIDetectionOptimizationService(config)  # Redundant

# ✅ DO THIS INSTEAD - Automatic loading  
service = AIDetectionOptimizationService()  # Handles config automatically
```

### **Base Class Behavior vs Subclass Behavior**

**Critical Understanding:**

- **SimplifiedService base class**: Requires configuration, throws `ConfigurationError` if None
- **Service subclasses**: Provide configuration fallbacks, rarely throw errors

```python
# Base class behavior (SimplifiedService)
def __init__(self, config: Optional[ServiceConfiguration] = None):
    if config is None:
        raise ConfigurationError("Service configuration is required")  # ❌ Strict

# Subclass behavior (AIDetectionOptimizationService)  
def __init__(self, config: Optional[ServiceConfiguration] = None):
    super().__init__(config or get_ai_detection_service_config())  # ✅ Provides fallback
```

### AI Detection Service Configuration

```python
ai_config = ServiceConfiguration(
    name="ai_detection_service",
    settings={
        # Provider settings
        "providers": {
            "winston": {
                "type": "winston",
                "enabled": True,
                "target_score": 70.0,
                "max_iterations": 5,
            },
            "mock": {
                "type": "mock",
                "enabled": False,  # Only for testing
            }
        },

        # Global settings
        "target_score": 70.0,
        "max_iterations": 5,
        "improvement_threshold": 3.0,
        "cache_ttl_hours": 1,
        "max_workers": 4,
        "detection_threshold": 0.7,
        "confidence_threshold": 0.8,
        "allow_mocks_for_testing": False,  # Production: False
    }
)
```

### Workflow Service Configuration

```python
workflow_config = ServiceConfiguration(
    name="iterative_workflow_service",
    settings={
        "max_iterations": 10,
        "quality_threshold": 0.9,
        "time_limit_seconds": 300,
        "convergence_threshold": 0.01,
        "backoff_factor": 2.0,
        "min_delay": 0.1,
        "max_delay": 10.0,
    }
)
```

## Optimization Configuration

### Basic Optimization Config

```python
from optimizer.optimization_orchestrator import OptimizationConfig

config = OptimizationConfig(
    target_score=75.0,        # Target AI detection score
    max_iterations=5,         # Maximum optimization attempts
    improvement_threshold=3.0, # Minimum improvement per iteration
    time_limit_seconds=None,   # No time limit
)
```

### Advanced Optimization Config

```python
config = OptimizationConfig(
    target_score=80.0,        # Higher quality target
    max_iterations=7,         # More attempts for difficult content
    improvement_threshold=5.0, # Require larger improvements
    time_limit_seconds=600,   # 10 minute limit
)
```

## Environment Variables

### AI Detection Settings

```bash
# Winston.ai API settings
export WINSTON_API_KEY="your_api_key_here"
export WINSTON_TIMEOUT="30"
export WINSTON_MAX_RETRIES="3"

# AI detection thresholds
export AI_DETECTION_TARGET_SCORE="75.0"
export AI_DETECTION_MAX_ITERATIONS="5"
export AI_DETECTION_IMPROVEMENT_THRESHOLD="3.0"

# Caching settings
export AI_DETECTION_CACHE_TTL_HOURS="1"
export AI_DETECTION_MAX_WORKERS="4"
```

### Workflow Settings

```bash
# Workflow limits
export WORKFLOW_MAX_ITERATIONS="10"
export WORKFLOW_TIME_LIMIT_SECONDS="300"
export WORKFLOW_QUALITY_THRESHOLD="0.9"

# Iteration strategy
export WORKFLOW_ITERATION_STRATEGY="adaptive"
export WORKFLOW_CONVERGENCE_THRESHOLD="0.01"
export WORKFLOW_BACKOFF_FACTOR="2.0"
```

### General Settings

```bash
# Test mode detection
export TEST_MODE="false"
export PYTEST_CURRENT_TEST=""

# Logging level
export OPTIMIZER_LOG_LEVEL="INFO"

# Performance settings
export OPTIMIZER_MAX_CONCURRENT="4"
export OPTIMIZER_MEMORY_LIMIT_MB="512"
```

## Configuration Files

### YAML Configuration

Create `config/optimizer.yaml`:

```yaml
# AI Detection Service
ai_detection_service:
  enabled: true
  settings:
    providers:
      winston:
        type: winston
        enabled: true
        target_score: 70.0
        max_iterations: 5
      mock:
        type: mock
        enabled: false
    target_score: 70.0
    max_iterations: 5
    improvement_threshold: 3.0
    cache_ttl_hours: 1
    max_workers: 4
    detection_threshold: 0.7
    confidence_threshold: 0.8
    allow_mocks_for_testing: false

# Iterative Workflow Service
iterative_workflow_service:
  enabled: true
  settings:
    max_iterations: 10
    quality_threshold: 0.9
    time_limit_seconds: 300
    convergence_threshold: 0.01
    backoff_factor: 2.0
    min_delay: 0.1
    max_delay: 10.0

# Text Optimization Settings
text_optimization:
  dynamic_prompts:
    enabled: true
    enhancement_flags:
      conversational_boost: true
      natural_language_patterns: true
      cultural_adaptation: true
      sentence_variability: true
      ai_detection_focus: true

  quality_scorer:
    human_threshold: 75.0
    technical_accuracy_weight: 0.3
    author_authenticity_weight: 0.3
    readability_weight: 0.2
    human_believability_weight: 0.2

# Author Personas
personas:
  taiwan:
    word_limit: 380
    language_patterns:
      signature_phrases:
        - "systematic approach enables"
        - "careful analysis shows"
        - "methodical investigation reveals"
  italy:
    word_limit: 450
    language_patterns:
      signature_phrases:
        - "precision meets innovation"
        - "technical elegance"
        - "meticulous approach"
  indonesia:
    word_limit: 250
    language_patterns:
      signature_phrases:
        - "practical applications"
        - "efficient solutions"
        - "renewable energy focus"
  usa:
    word_limit: 320
    language_patterns:
      signature_phrases:
        - "innovative solutions"
        - "efficient processes"
        - "conversational expertise"
```

### JSON Configuration

Create `config/optimizer.json`:

```json
{
  "ai_detection_service": {
    "enabled": true,
    "settings": {
      "providers": {
        "winston": {
          "type": "winston",
          "enabled": true,
          "target_score": 70.0,
          "max_iterations": 5
        }
      },
      "target_score": 70.0,
      "max_iterations": 5,
      "cache_ttl_hours": 1
    }
  },
  "iterative_workflow_service": {
    "enabled": true,
    "settings": {
      "max_iterations": 10,
      "quality_threshold": 0.9,
      "time_limit_seconds": 300
    }
  }
}
```

## Runtime Configuration

### Programmatic Configuration

```python
from optimizer.optimization_orchestrator import ContentOptimizationOrchestrator, OptimizationConfig

# Create custom config
config = OptimizationConfig(
    target_score=85.0,
    max_iterations=8,
    improvement_threshold=5.0
)

# Initialize with custom config
orchestrator = ContentOptimizationOrchestrator()
result = await orchestrator.optimize_content(
    content="Content to optimize...",
    material_name="silicon_nitride",
    config=config
)
```

### Service-Specific Configuration

```python
from optimizer.services.ai_detection_optimization import AIDetectionOptimizationService
from optimizer.services import ServiceConfiguration

# Custom AI detection config
ai_config = ServiceConfiguration(
    name="ai_detection_service",
    settings={
        "target_score": 80.0,
        "max_iterations": 6,
        "cache_ttl_hours": 2,
        "providers": {
            "winston": {
                "enabled": True,
                "target_score": 80.0
            }
        }
    }
)

# Initialize service with custom config
ai_service = AIDetectionOptimizationService(ai_config)
```

## Configuration Best Practices

### 1. Environment-Specific Settings

```python
# config/production.yaml
ai_detection_service:
  settings:
    allow_mocks_for_testing: false
    cache_ttl_hours: 2
    max_workers: 8

# config/testing.yaml
ai_detection_service:
  settings:
    allow_mocks_for_testing: true
    cache_ttl_hours: 0  # No caching in tests
    max_workers: 2
```

### 2. Progressive Configuration

```python
# Start with defaults
config = OptimizationConfig()

# Override for specific use case
config.target_score = 80.0
config.max_iterations = 7

# Use environment variables for deployment-specific settings
import os
if os.getenv("HIGH_QUALITY_MODE"):
    config.target_score = 85.0
    config.max_iterations = 10
```

### 3. Configuration Validation

```python
def validate_config(config: OptimizationConfig) -> bool:
    """Validate optimization configuration."""
    if not (0 <= config.target_score <= 100):
        raise ValueError("Target score must be between 0 and 100")

    if config.max_iterations < 1:
        raise ValueError("Max iterations must be at least 1")

    if config.improvement_threshold < 0:
        raise ValueError("Improvement threshold must be non-negative")

    return True

# Validate before use
config = OptimizationConfig(target_score=85.0, max_iterations=5)
validate_config(config)
```

## Common Configuration Patterns

### High-Quality Optimization

```python
high_quality_config = OptimizationConfig(
    target_score=85.0,
    max_iterations=8,
    improvement_threshold=5.0,
    time_limit_seconds=900  # 15 minutes
)
```

### Fast Optimization

```python
fast_config = OptimizationConfig(
    target_score=70.0,
    max_iterations=3,
    improvement_threshold=2.0,
    time_limit_seconds=180  # 3 minutes
)
```

### Conservative Optimization

```python
conservative_config = OptimizationConfig(
    target_score=75.0,
    max_iterations=5,
    improvement_threshold=3.0,
    time_limit_seconds=600  # 10 minutes
)
```

## Configuration Loading Utilities

### Load from File

```python
import yaml
from pathlib import Path

def load_optimizer_config(config_path: str) -> Dict[str, Any]:
    """Load optimizer configuration from YAML file."""
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

# Load configuration
config_data = load_optimizer_config("config/optimizer.yaml")
```

### Environment Variable Override

```python
import os

def apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides to configuration."""
    overrides = {
        "AI_DETECTION_TARGET_SCORE": ("ai_detection_service.settings.target_score", float),
        "WORKFLOW_MAX_ITERATIONS": ("iterative_workflow_service.settings.max_iterations", int),
        "TEST_MODE": ("test_mode", lambda x: x.lower() in ("true", "1", "yes")),
    }

    for env_var, (config_path, type_converter) in overrides.items():
        if env_var in os.environ:
            value = type_converter(os.environ[env_var])
            set_nested_config_value(config, config_path, value)

    return config

def set_nested_config_value(config: Dict[str, Any], path: str, value: Any):
    """Set a nested configuration value using dot notation."""
    keys = path.split('.')
    current = config
    for key in keys[:-1]:
        current = current.setdefault(key, {})
    current[keys[-1]] = value
```

## Troubleshooting Configuration

### Common Issues

#### 1. Service Not Found
```python
# Check service registration
from optimizer.service_initializer import get_optimizer_status
status = get_optimizer_status()
print("Available services:", list(status['services'].keys()))
```

#### 2. Configuration Not Applied
```python
# Verify configuration loading
from optimizer.services import ServiceConfiguration
config = ServiceConfiguration(name="test", settings={"test": True})
print("Config loaded:", config.settings)
```

#### 3. Service Initialization Errors

**ConfigurationError: Service configuration is required**

This error means the service couldn't load any configuration. Check:

```python
# ✅ Debug configuration discovery
from optimizer.services.ai_detection_optimization import get_ai_detection_service_config

try:
    config = get_ai_detection_service_config()
    print("✅ Config loaded successfully:", config.name)
except Exception as e:
    print("❌ Config loading failed:", str(e))
    
# ✅ Test service initialization
try:
    from optimizer.services.ai_detection_optimization import AIDetectionOptimizationService
    service = AIDetectionOptimizationService()
    print("✅ Service initialized successfully")
except Exception as e:
    print("❌ Service initialization failed:", str(e))
```

**Common Solutions:**
- Ensure config files exist in expected locations
- Check file permissions on configuration files  
- Verify environment variables are set correctly
- Use explicit configuration as fallback

```python
# 🔧 Fallback pattern for problematic environments
try:
    service = AIDetectionOptimizationService()  # Try automatic
except ConfigurationError:
    # Manual fallback configuration
    from optimizer.services import ServiceConfiguration
    fallback_config = ServiceConfiguration(
        name="ai_detection_fallback",
        settings={"target_score": 75.0}
    )
    service = AIDetectionOptimizationService(fallback_config)
```

#### 4. Environment Variables Not Working
```python
# Check environment variables
import os
print("AI_DETECTION_TARGET_SCORE:", os.getenv("AI_DETECTION_TARGET_SCORE"))
print("WORKFLOW_MAX_ITERATIONS:", os.getenv("WORKFLOW_MAX_ITERATIONS"))
```

### Debug Configuration

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug logging for configuration
logger = logging.getLogger("optimizer")
logger.setLevel(logging.DEBUG)

# This will show configuration loading and application
from optimizer.service_initializer import initialize_optimizer_services
result = initialize_optimizer_services()
```

## Configuration Templates

### Production Template

```yaml
# Production configuration - high reliability, performance optimized
ai_detection_service:
  enabled: true
  settings:
    allow_mocks_for_testing: false
    cache_ttl_hours: 2
    max_workers: 8
    providers:
      winston:
        enabled: true
        target_score: 75.0
        max_iterations: 5

iterative_workflow_service:
  enabled: true
  settings:
    max_iterations: 8
    time_limit_seconds: 600
    quality_threshold: 0.9
```

### Development Template

```yaml
# Development configuration - faster iteration, more logging
ai_detection_service:
  enabled: true
  settings:
    allow_mocks_for_testing: true  # Allow mocks for testing
    cache_ttl_hours: 0  # Disable caching
    max_workers: 2
    providers:
      winston:
        enabled: false  # Use mock instead
      mock:
        enabled: true

iterative_workflow_service:
  enabled: true
  settings:
    max_iterations: 3  # Fewer iterations for faster testing
    time_limit_seconds: 120  # Shorter timeout
    quality_threshold: 0.7  # Lower threshold for testing
```

### Testing Template

```yaml
# Testing configuration - deterministic, fast
ai_detection_service:
  enabled: true
  settings:
    allow_mocks_for_testing: true
    cache_ttl_hours: 0
    max_workers: 1
    providers:
      mock:
        enabled: true
        deterministic: true  # Consistent test results

iterative_workflow_service:
  enabled: true
  settings:
    max_iterations: 2
    time_limit_seconds: 60
    quality_threshold: 0.5
```

This configuration guide provides comprehensive coverage of all optimizer configuration options, making it easy to customize the system for different use cases and environments.</content>
<parameter name="filePath">/Users/todddunning/Desktop/Z-Beam/z-beam-generator/optimizer/CONFIGURATION_GUIDE.md
