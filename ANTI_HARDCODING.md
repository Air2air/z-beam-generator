# 🚨 ANTI-HARDCODING GUIDE

## ⚠️ **THE PROBLEM**

Claude (and developers) often hardcode configuration values deep in the application:
```python
# ❌ BAD - Hardcoded values
temperature = 0.3
ai_threshold = 25
iterations = 3
timeout = 60
```

This breaks user control and makes the system inflexible.

## ✅ **THE SOLUTION**

Use the **Global Configuration Manager** for ALL config values:

```python
# ✅ GOOD - Use global config
from config.global_config import get_config

config = get_config()
temperature = config.get_detection_temperature()
ai_threshold = config.get_ai_detection_threshold()
iterations = config.get_iterations_per_section()
timeout = config.get_api_timeout()
```

## 🛠️ **TOOLS TO PREVENT HARDCODING**

### 1. Detection Tool
```bash
cd generator
python3 scripts/detect_hardcoding.py
```
Scans all files and reports hardcoded values.

### 2. Auto-Fix Tool
```bash
cd generator
python3 scripts/fix_hardcoding.py
```
Automatically fixes common hardcoding violations.

### 3. Workflow Commands
```bash
python3 workflow.py check-config    # Detect hardcoded values
python3 workflow.py fix-config      # Auto-fix common issues
```

## 📋 **RULES FOR DEVELOPERS**

### ✅ **DO:**
- Import: `from config.global_config import get_config`
- Use: `get_config().get_*()` for ALL configuration values
- Add `@requires_config` decorator to functions needing config
- Run detection tool before committing changes

### ❌ **DON'T:**
- Never hardcode temperatures, thresholds, timeouts, or iterations
- Don't use magic numbers in function parameters
- Don't create "default" values in function signatures
- Don't assume configuration values

## 🎯 **AVAILABLE CONFIG METHODS**

```python
config = get_config()

# Thresholds
config.get_ai_detection_threshold()      # AI detection threshold
config.get_natural_voice_threshold()     # Natural voice threshold

# Temperatures
config.get_content_temperature()         # Content generation
config.get_detection_temperature()       # Detection calls
config.get_improvement_temperature()     # Improvement iterations
config.get_summary_temperature()         # Summary generation
config.get_metadata_temperature()        # Metadata generation

# Limits & Timing
config.get_iterations_per_section()      # Max iterations per section
config.get_max_article_words()          # Article word limit
config.get_api_timeout()                # API call timeout

# Content Settings
config.get_material()                   # Current material
config.get_generator_provider()         # AI provider
config.get_detection_provider()         # Detection provider

# Generic getter
config.get("any_key", default_value)    # Any config value
```

## 🚀 **WORKFLOW INTEGRATION**

### When Making Changes:
1. **Write code** using `get_config()` methods
2. **Check for hardcoding**: `python3 workflow.py check-config`
3. **Auto-fix issues**: `python3 workflow.py fix-config`
4. **Test changes**: `python3 run.py`
5. **Commit clean code**

### When Claude Makes Changes:
1. **Review generated code** for hardcoded values
2. **Run auto-fixer**: `python3 workflow.py fix-config`
3. **Verify fixes** with detection tool
4. **Test functionality**

## 💡 **WHY THIS MATTERS**

- **User Control**: All settings come from `run.py`
- **Consistency**: Same values used throughout application
- **Flexibility**: Easy to change behavior without code edits
- **Maintainability**: Single source of truth for configuration
- **Testing**: Easy to test with different configurations

## 🔧 **EXAMPLE FIXES**

### Before (❌ Bad):
```python
def detect_ai_patterns(content, temperature=0.3, timeout=60):
    if score > 25:  # hardcoded threshold
        return False
```

### After (✅ Good):
```python
from config.global_config import get_config, requires_config

@requires_config
def detect_ai_patterns(content, temperature=None, timeout=None):
    config = get_config()
    temp = temperature or config.get_detection_temperature()
    timeout = timeout or config.get_api_timeout()
    threshold = config.get_ai_detection_threshold()
    
    if score > threshold:
        return False
```

## 🏗️ **ARCHITECTURAL RULES**

### Generator Project Structure
All generator project files must be organized properly:

- ✅ **Allowed in Root**: `run.py`, `train.py`, `workflow.py`, `show_config.py`
- ❌ **Not Allowed in Root**: Any other generator Python files
- ✅ **Must be in /generator**: All other generator code, modules, services, etc.

### Examples:
```
✅ CORRECT:
/run.py                    # User config only
/train.py                 # Training entry point
/workflow.py              # Workflow commands
/generator/               # All generator code
  ├── main.py
  ├── core/
  ├── modules/
  └── infrastructure/

❌ WRONG:
/run.py
/interactive_training.py  # Should be in /generator
/detection/               # Should be in /generator
/modules/                 # Should be in /generator
```

This keeps the root clean and separates user-facing files from implementation.

## 🎯 **REMEMBER**

**Every configuration value should come from `run.py` through the Global Config Manager!**

No exceptions! 🚫
