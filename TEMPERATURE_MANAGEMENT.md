# Temperature Management in Z-Beam

This document provides an overview of how temperature is managed in the Z-Beam content generation system. Temperature is a critical parameter that controls the randomness/creativity in AI responses.

## Temperature Configuration

The system uses a centralized `TemperatureConfig` class to manage different temperature settings for different contexts:

```python
@dataclass(frozen=True)
class TemperatureConfig:
    """Configuration for temperature settings in different contexts."""
    
    content_temp: float      # For generating article content
    detection_temp: float    # For detection analysis
    improvement_temp: float = None  # For improvement iterations
    summary_temp: float = None      # For summary generation
    metadata_temp: float = None     # For structured metadata
```

## Temperature Ranges and Effects

- **Low (0.1-0.3)**: More predictable, consistent, and analytical content. Good for:
  - Detection tasks (`detection_temp`)
  - Structured metadata (`metadata_temp`)
  - Technical specifications

- **Medium (0.4-0.7)**: Balanced creativity and consistency. Good for:
  - Main content generation (`content_temp`)
  - Summaries (`summary_temp`)

- **High (0.8+)**: More creative, varied, but potentially less focused. Good for:
  - Creative improvements (`improvement_temp`)
  - Brainstorming alternative approaches

## Implementation Details

### Centralized Configuration

All temperature settings are centralized in `run.py` where you can configure the system:

```python
# Define centralized temperature configuration
TEMP_CONFIG = TemperatureConfig(
    content_temp=0.6,     # Main content generation temperature
    detection_temp=0.3,   # Detection calls temperature
    improvement_temp=0.7, # Slightly higher temperature for improvement passes
    summary_temp=0.4,     # Lower temperature for predictable summaries
    metadata_temp=0.2,    # Very low temperature for structured metadata
)
```

### Backward Compatibility

For backward compatibility, legacy temperature fields are maintained:

```python
USER_CONFIG = dict(
    # ...
    temperature=0.6,           # LEGACY: Maintained for backward compatibility
    detection_temperature=0.3, # LEGACY: Maintained for backward compatibility
    temperature_config=TEMP_CONFIG,  # NEW: Centralized temperature configuration
    # ...
)
```

### Usage in Services

Services now use the appropriate temperature for each task:

- Content service: Uses `temperature_config.content_temp` for initial content generation
- Detection service: Uses `temperature_config.detection_temp` for AI/human detection
- Content improvement: Uses `temperature_config.improvement_temp` for refining content

## Best Practices

1. **Content Generation**: Use medium temperatures (0.4-0.7) for balanced creativity and consistency
2. **Detection**: Use lower temperatures (0.2-0.4) for more consistent detection results
3. **Improvement**: Use slightly higher temperatures (0.6-0.8) than your content temperature to introduce creative improvements
4. **Metadata**: Use very low temperatures (0.1-0.3) for structured, predictable metadata

## Configuration Validation

The `TemperatureConfig` class validates all temperature values to ensure they are within the valid range (0.0-2.0):

```python
# Validate all temperatures are in valid range
for name, value in [
    ("content_temp", self.content_temp),
    ("detection_temp", self.detection_temp),
    ("improvement_temp", self.improvement_temp),
    ("summary_temp", self.summary_temp),
    ("metadata_temp", self.metadata_temp)
]:
    if not 0.0 <= value <= 2.0:
        raise ValueError(f"Temperature {name} must be between 0.0 and 2.0, got {value}")
```

This ensures the system fails fast on invalid configurations rather than silently using incorrect values.
