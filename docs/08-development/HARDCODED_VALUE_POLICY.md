# Hardcoded Value Policy

**Status**: Active  
**Last Updated**: November 15, 2025  
**Enforcement**: Automatic via Integrity Checker

---

## 🎯 Policy Overview

**ALL configuration values MUST come from config files or dynamic calculation.**

The system uses a fully dynamic configuration architecture where user-facing sliders (1-10 scale) automatically calculate all technical parameters. Hardcoding values bypasses this system and creates:

1. **Configuration drift** - Code values diverge from config
2. **Maintenance burden** - Multiple places to update
3. **Debugging difficulty** - Hidden values that aren't tracked
4. **System fragility** - Changes don't propagate correctly

---

## 🚫 Prohibited Patterns

### 1. Hardcoded API Penalties

❌ **WRONG**:
```python
frequency_penalty = 0.0
presence_penalty = 0.5

api_params = {
    'frequency_penalty': 0.0,
    'presence_penalty': 0.0
}
```

✅ **CORRECT**:
```python
penalties = dynamic_config.calculate_penalties()
frequency_penalty = penalties['frequency_penalty']
presence_penalty = penalties['presence_penalty']

api_params = {
    'penalties': dynamic_config.calculate_penalties()
}
```

### 2. Hardcoded Thresholds

❌ **WRONG**:
```python
# Static threshold that never learns
WINSTON_AI_THRESHOLD = 0.33
if ai_score > WINSTON_AI_THRESHOLD:
    print("Failed detection")

threshold = 7.0  # Hardcoded
if realism_score < threshold:
    retry()
```

✅ **CORRECT** (Dynamic Learning):
```python
# Threshold learns from database success patterns
from learning.threshold_manager import ThresholdManager

threshold_manager = ThresholdManager(db_path='z-beam.db')
winston_threshold = threshold_manager.get_winston_threshold(use_learned=True)
if ai_score > winston_threshold:
    print("Failed detection")

realism_threshold = threshold_manager.get_realism_threshold(use_learned=True)
if realism_score < realism_threshold:
    retry()
```

**Why this matters**: Thresholds now adapt based on 75th percentile of successful content.
As system improves, quality standards automatically tighten. Database fallback to config defaults
ensures system always has sensible values.

### 3. Hardcoded Temperatures

❌ **WRONG**:
```python
temperature = 0.8

response = api.call(
    prompt=prompt,
    temperature=0.7
)
```

✅ **CORRECT**:
```python
temperature = dynamic_config.calculate_temperature(component_type)

response = api.call(
    prompt=prompt,
    temperature=temperature
)
```

### 4. Fallback Defaults Bypassing Config

❌ **WRONG**:
```python
# These silently fail instead of alerting to missing config
penalties = config.get('penalties', {'frequency_penalty': 0.0})
threshold = params.get('threshold', 0.7)
temperature = api_params.get('temperature') or 0.8
max_tokens = config.get('max_tokens', {})
```

✅ **CORRECT**:
```python
# Fail-fast if config is missing
penalties = config['penalties']  # KeyError if missing
threshold = dynamic_config.calculate_detection_threshold()  # Always works

# OR with explicit validation
temperature = api_params.get('temperature')
if temperature is None:
    raise ConfigurationError("Temperature not configured")
```

### 5. Magic Numbers

❌ **WRONG**:
```python
for i in range(5):  # Why 5?
    attempt = generate()

if word_count > 100:  # Why 100?
    truncate()
```

✅ **CORRECT**:
```python
max_attempts = config.get_max_attempts()
for i in range(max_attempts):
    attempt = generate()

max_words = dynamic_config.calculate_target_length_range(component_type)['max']
if word_count > max_words:
    truncate()
```

---

## ✅ Allowed Use Cases

### Configuration Constants

These are OK because they're not technical parameters:
```python
DEFAULT_COMPONENT_TYPE = 'subtitle'  # User-facing default
FILE_EXTENSION = '.yaml'  # System constant
API_TIMEOUT_SECONDS = 120  # Infrastructure constant
```

### Test Code

Mocks and hardcoded values are **ALLOWED in test code**:
```python
# tests/test_generator.py
def test_temperature_calculation():
    # OK - this is test code
    mock_config = {'temperature': 0.8}
    result = calculate_something(mock_config)
```

### Documentation Examples

Hardcoded values in docstrings and comments:
```python
def calculate_temperature(component_type: str) -> float:
    """
    Calculate temperature for component.
    
    Example:
        >>> calculate_temperature('subtitle')
        0.628  # This hardcoded example is OK
    """
```

---

## 🔍 Enforcement

### Automatic Detection

The integrity checker automatically scans production code for:

1. **Penalty patterns**: `frequency_penalty=0.0`, `'presence_penalty': 0.5`
2. **Temperature patterns**: `temperature = 0.8`
3. **Threshold patterns**: `threshold = 30`, `if score > 0.7:`
4. **Fallback patterns**: `.get('key', 0.0)`, `or 0.0`, `or {}`

Run check:
```bash
python3 -c "
from generation.integrity import IntegrityChecker
checker = IntegrityChecker()
results = checker.run_quick_checks()
"
```

Preferred CLI command:
```bash
python3 run.py --integrity-check --quick
```

### Pre-Generation Validation

The integrity check runs automatically before every generation:
```bash
python3 run.py --micro "Aluminum"
# 🔍 Running pre-generation integrity check...
# ❌ Integrity check FAILED - Found 36 hardcoded values
```

Bypass is development-only and explicitly gated:
```bash
ALLOW_INTEGRITY_BYPASS=1 python3 run.py --micro "Aluminum" --skip-integrity-check
```

### Continuous Integration

Tests verify zero hardcoded values:
```bash
pytest tests/test_hardcoded_value_detection.py
```

---

## ✅ Recent Compliance Fixes

### Dynamic Threshold Learning (November 20, 2025) 🔥 **MAJOR UPDATE**

**Issue**: All quality thresholds were static - Grok (0.33), Realism (7.0), etc.
Sweet spot analyzer collected learning data but it was **never used**.

**Fix Applied** (Commit: 50244080):

1. **Created ThresholdManager** (`learning/threshold_manager.py`):
   - Learns Grok threshold from 75th percentile of successful content
   - Learns realism threshold from 75th percentile of quality scores
   - Falls back to defaults only when <10 samples
   - Saves learned values to `learned_thresholds` table

2. **Updated ValidationConstants**:
   ```python
   # BEFORE (❌ HARDCODED):
   WINSTON_AI_THRESHOLD = 0.33
   
   # AFTER (✅ DYNAMIC):
   @classmethod
   def get_winston_threshold(cls, use_learned=True):
       manager = cls._get_threshold_manager()
       return manager.get_winston_threshold(use_learned)
   ```

3. **Integrated sweet spot parameters** into generation:
   - Temperature, penalties, voice parameters now use learned values
   - Falls back to config only if insufficient learning data
   - **Closes the learning loop**: Sweet spot → Parameters → Generation

**Benefits**:
- ✅ Thresholds adapt based on actual success patterns
- ✅ System genuinely self-improving (not just collecting unused data)
- ✅ Zero hardcoded thresholds in production
- ✅ Database-driven quality standards
- ✅ Continuous improvement through 75th percentile learning

**See**: `docs/decisions/ADR-005-dynamic-threshold-learning.md`

### SubjectiveEvaluator Temperature Fix (November 17, 2025)

### SubjectiveEvaluator Temperature Fix

**Issue**: Hardcoded `temperature=0.2` in subjective evaluation API calls violated policy.

**Fix Applied** (Commit: c5aa1d6c):
```python
# BEFORE (❌ VIOLATION):
request = GenerationRequest(
    prompt=prompt,
    system_prompt="...",
    temperature=0.2  # ❌ Hardcoded
)

# AFTER (✅ COMPLIANT):
class SubjectiveEvaluator:
    def __init__(self, api_client, quality_threshold=7.0, 
                 verbose=False, evaluation_temperature=0.2):
        self.evaluation_temperature = evaluation_temperature
    
    def evaluate(self, content, context):
        request = GenerationRequest(
            prompt=prompt,
            system_prompt="...",
            temperature=self.evaluation_temperature  # ✅ Configurable
        )
```

**Benefits**:
- ✅ Temperature now configurable via constructor parameter
- ✅ Can be connected to dynamic_config for adaptive learning
- ✅ Maintains sensible default (0.2 for consistency)
- ✅ Complies with policy without breaking existing code

---

## 🛠️ Migration Guide

### Step 1: Identify Hardcoded Values

Run the integrity checker:
```bash
python3 -c "
from generation.integrity import IntegrityChecker
checker = IntegrityChecker()
results = checker._check_hardcoded_values()
for v in results[0].details.get('violations', []):
    print(v)
"
```

### Step 2: Replace with Config/Dynamic Calculation

For each violation:

1. **API penalties** → `dynamic_config.calculate_penalties()`
2. **Thresholds** → `dynamic_config.calculate_detection_threshold()`
3. **Temperature** → `dynamic_config.calculate_temperature(component_type)`
4. **Max tokens** → `dynamic_config.calculate_max_tokens(component_type)`
5. **Retry behavior** → `dynamic_config.calculate_retry_behavior()`

### Step 3: Verify Fix

Run tests and integrity check:
```bash
pytest tests/test_hardcoded_value_detection.py
python3 -c "from generation.integrity import IntegrityChecker; IntegrityChecker().run_quick_checks()"
```

---

## 📋 Checklist for Code Review

Before merging any PR:

- [ ] No `frequency_penalty=0.0` or `presence_penalty=0.5` in production code
- [ ] No `temperature = 0.X` assignments outside config/dynamic_config
- [ ] No `threshold = X` assignments bypassing config
- [ ] No `.get('key', default_value)` in critical paths (use fail-fast)
- [ ] No `or default_value` patterns bypassing validation
- [ ] All configuration values trace back to config.yaml or dynamic calculation
- [ ] Integrity check passes with zero hardcoded value violations
- [ ] Tests pass: `pytest tests/test_hardcoded_value_detection.py`

---

## 🔗 Related Documentation

- **Integrity Checker**: `generation/integrity/integrity_checker.py`
- **Dynamic Config**: `generation/config/dynamic_config.py`
- **Config Loader**: `generation/config/config_loader.py`
- **Fail-Fast Policy**: `.github/copilot-instructions.md`
- **Test Suite**: `tests/test_hardcoded_value_detection.py`

---

## 📞 Questions?

If you're unsure whether a value should be hardcoded:

1. Ask: "Could this value ever change based on user settings?"
2. If YES → Use dynamic_config
3. If NO → Ask: "Is this a technical parameter that affects generation quality?"
4. If YES → Use config.yaml
5. If NO → Hardcoded constant is OK (but document why)

**When in doubt, use dynamic config.**
