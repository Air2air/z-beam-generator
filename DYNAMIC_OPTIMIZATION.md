# Dynamic Optimization Configuration

## Overview

The Z-Beam generator now uses **dynamic optimization configuration** instead of hardcoded values in `run.py`. This enables the system to automatically adjust optimization parameters based on training insights and performance data.

## What Changed

### ❌ Before (Hardcoded in run.py)
```python
USER_CONFIG = {
    "ai_detection_threshold": 25,      # Fixed threshold
    "natural_voice_threshold": 25,    # Fixed threshold  
    "content_temp": 0.6,              # Fixed temperature
    "detection_temp": 0.3,            # Fixed temperature
    "improvement_temp": 0.7,          # Fixed temperature
    "summary_temp": 0.4,              # Fixed temperature
    "metadata_temp": 0.2,             # Fixed temperature
    # ...
}
```

### ✅ After (Dynamic Management)
```python
USER_CONFIG = {
    # Only essential user preferences remain
    "material": "Bronze", 
    "generator_provider": "DEEPSEEK",
    "iterations_per_section": 5,
    # Note: Optimization values now managed dynamically
}
```

## Dynamic Configuration System

### GlobalConfigManager Enhancement
The `GlobalConfigManager` now provides:

1. **Intelligent Defaults**: Optimal values when not specified
2. **Dynamic Updates**: Training can adjust values automatically  
3. **Runtime Validation**: Ensures values stay within safe ranges
4. **Centralized Access**: All code uses `get_config()` - no hardcoding

### Default Values Applied
```python
optimization_defaults = {
    "ai_detection_threshold": 25,      # 25% max AI detection
    "natural_voice_threshold": 25,    # 25% max for natural voice
    "content_temp": 0.6,              # Balanced creativity
    "detection_temp": 0.3,            # Low variance for consistency
    "improvement_temp": 0.7,          # Higher creativity for improvements
    "summary_temp": 0.4,              # Moderate for summaries
    "metadata_temp": 0.2,             # Very consistent for metadata
}
```

## How Dynamic Updates Work

### 1. Training Insights
When training detects patterns:
```python
# Example: Users rate content as natural but system flags it as AI
config.update_ai_detection_threshold(30)  # Increase (be more lenient)

# Example: Users rate content as fake but system misses it  
config.update_natural_voice_threshold(20)  # Decrease (be more strict)
```

### 2. Temperature Adjustments
```python
# If content consistently rated as too robotic
config.update_temperature("content", 0.7)  # Increase creativity

# If detection is inconsistent
config.update_temperature("detection", 0.2)  # Increase consistency
```

### 3. Automatic Application
```bash
# After training session:
python3 workflow.py apply-training

# System automatically:
# - Analyzes user feedback patterns
# - Identifies optimization opportunities  
# - Applies threshold/temperature adjustments
# - Updates prompts with learned patterns
```

## Benefits

### ✅ Adaptive System
- **Learns from feedback**: Human ratings improve AI behavior
- **Self-optimizing**: No manual parameter tuning required
- **Context-aware**: Adjusts based on content type and user preferences

### ✅ Anti-Hardcoding  
- **No magic numbers**: All values come from config manager
- **Centralized control**: Single source of truth prevents inconsistency
- **Training-driven**: Values evolve based on actual performance data

### ✅ User-Friendly
- **Sensible defaults**: Works well out of the box
- **Transparent updates**: Changes are logged and explainable
- **Manual override**: Users can still set specific values if needed

## Commands & Usage

### View Current Settings
```bash
python3 show_config.py
```
Output:
```
🎛️  Current Optimization Settings
🎯 Detection Thresholds:
   AI Detection: 25% (lower = stricter)
   Natural Voice: 25% (lower = stricter)
🌡️  Temperature Settings:
   Content Generation: 0.6 (creativity)
   Detection Calls: 0.3 (consistency)
   # etc...
```

### Training Integration
```bash
# 1. Train with feedback
python3 train.py

# 2. Apply insights automatically  
python3 workflow.py apply-training

# 3. See what changed
python3 show_config.py
python3 workflow.py show-recommendations
```

### Check for Hardcoding
```bash
python3 workflow.py detect     # Find hardcoded values
python3 workflow.py autofix    # Fix common violations
```

## Migration Impact

### For Users
- **No breaking changes**: System works with existing workflows
- **Better performance**: Optimization values evolve and improve
- **Less configuration**: Fewer values to manually tune

### For Developers  
- **Use get_config()**: Always access values through config manager
- **No hardcoding**: Detection tools prevent configuration violations
- **Dynamic updates**: Values can change during runtime based on training

## Configuration Hierarchy

1. **User Values**: Explicitly set in `USER_CONFIG` (highest priority)
2. **Dynamic Updates**: Applied by training integration
3. **Intelligent Defaults**: Applied by GlobalConfigManager
4. **Fallback Values**: Hardcoded defaults as last resort

## Example Training Scenario

### Initial State
```
AI Detection Threshold: 25%
Natural Voice Threshold: 25% 
Content Temperature: 0.6
```

### Training Session
User provides feedback:
- "This sounds too robotic" → Content rated as fake
- "System missed obvious AI text" → Detection threshold too high

### Automatic Adjustments
```
AI Detection Threshold: 20% (stricter detection)
Natural Voice Threshold: 22% (slightly stricter)
Content Temperature: 0.7 (more creative content)
```

### Production Impact
Next content generation uses improved settings:
- Better AI detection (fewer false negatives)
- More natural-sounding content
- Calibrated to user preferences

## Future Enhancements

### Short-Term
- **A/B Testing**: Compare different optimization values
- **Material-Specific**: Different settings for different materials
- **Performance Metrics**: Track optimization effectiveness

### Long-Term  
- **ML-Driven**: Use machine learning for parameter optimization
- **Real-Time**: Adjust parameters during generation based on intermediate results
- **User Profiles**: Personalized optimization for different users

## Technical Details

### GlobalConfigManager API
```python
# Reading values
config.get_ai_detection_threshold()
config.get_content_temperature()
config.get_optimization_summary()

# Dynamic updates  
config.update_ai_detection_threshold(new_value)
config.update_temperature("content", new_temp)

# Validation
config.validate_thresholds()
config.validate_temperatures()
```

### Training Integration API
```python
# Apply all training insights
service.apply_training_insights()

# Get recommendations
recommendations = service.get_recommendations()

# Manual adjustments
service.adjust_threshold("ai_detection", 20)
service.adjust_temperature("content", 0.7)
```

The dynamic optimization system ensures that **every training session makes the production system better** by automatically applying learned insights to the optimization parameters that control content generation quality.
