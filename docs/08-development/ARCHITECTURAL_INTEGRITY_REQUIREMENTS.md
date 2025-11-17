# Architectural Integrity Requirements

**Purpose**: Define the core architectural behaviors that MUST be validated by integrity checks to prevent bugs.

## Critical Architectural Patterns

### 1. Self-Learning Must Be Iterative
**Requirement**: PromptOptimizer must run on EVERY generation attempt, not just the first.

**Why**: The system learns from Winston feedback. If it only runs once, subsequent attempts can't benefit from what was just learned.

**Validation**:
```python
# BAD - Only runs once
if self.prompt_optimizer and attempt == 1:
    optimize_prompt()

# GOOD - Runs every attempt
if self.prompt_optimizer:
    optimize_prompt()
```

**Integrity Check**: `Learning: DynamicGenerator Integration` must verify no `attempt == 1` condition exists.

---

### 2. Fail-Fast on Missing Dependencies
**Requirement**: System must fail immediately with clear errors if required components are missing.

**Why**: Silent degradation leads to broken systems that appear to work but produce invalid results.

**Validation**:
```python
# BAD - Silently degrades
optimizer = PromptOptimizer() if exists else None

# GOOD - Fails fast
if not exists:
    raise ConfigurationError("PromptOptimizer required")
optimizer = PromptOptimizer()
```

**Integrity Check**: Must verify no `or None`, `or {}`, `or 0.0` fallbacks in production code.

---

### 3. Data Flows Through Single Source of Truth
**Requirement**: Materials.yaml is the ONLY source for generation and validation.

**Why**: Multiple data sources create consistency issues and make learning unreliable.

**Validation**:
- All AI generation writes to Materials.yaml
- All validation reads from Materials.yaml
- Frontmatter is export-only (no reverse flow)

**Integrity Check**: Verify no generation or validation logic reads from frontmatter files.

---

### 4. Learning Data Must Persist Immediately
**Requirement**: Every Winston detection result must be logged to database before continuing.

**Why**: System learns from historical data. Lost data = lost learning.

**Validation**:
```python
# BAD - May lose data on crash
results.append(detection)
# ... later ...
db.log_all(results)

# GOOD - Persists immediately
detection_id = db.log_detection(result)
```

**Integrity Check**: Verify database logging happens in try/except with error logging.

---

### 5. Configuration Values Must Be Dynamic
**Requirement**: No hardcoded penalties, temperatures, or thresholds in production code.

**Why**: The system adapts parameters based on learning. Hardcoded values defeat this.

**Validation**:
```python
# BAD - Hardcoded
temperature = 0.7
frequency_penalty = 0.5

# GOOD - Dynamic
temperature = dynamic_config.calculate_temperature()
penalties = dynamic_config.calculate_penalties()
```

**Integrity Check**: Detect hardcoded numeric literals in critical paths.

---

## Integrity Checker Responsibilities

### Must Validate BEHAVIOR, Not Just Presence

**Wrong Approach**:
```python
def check_optimizer():
    has_import = 'PromptOptimizer' in code
    has_call = 'optimize_prompt' in code
    return has_import and has_call  # ✗ Only checks existence
```

**Correct Approach**:
```python
def check_optimizer():
    has_import = 'PromptOptimizer' in code
    has_call = 'optimize_prompt' in code
    is_iterative = 'attempt == 1' not in optimizer_section  # ✓ Validates behavior
    return has_import and has_call and is_iterative
```

### Categories of Checks

1. **Structural Checks**: Components exist and are imported
2. **Integration Checks**: Components are properly connected
3. **Behavioral Checks**: Components behave according to architecture (NEW)
4. **Data Flow Checks**: Information flows through correct paths (NEW)
5. **Learning Checks**: System can learn and adapt (NEW)

---

## Test Requirements

### Unit Tests: Test Individual Components
- PatternLearner extracts patterns correctly
- PromptOptimizer enhances prompts
- TemperatureAdvisor recommends temps

### Integration Tests: Test Component Interactions
- Generator calls PromptOptimizer
- PromptOptimizer queries database
- Database returns correct patterns

### Behavioral Tests: Test Architectural Patterns (NEW)
- PromptOptimizer runs on ALL attempts
- System fails fast on missing dependencies
- Learning data persists immediately
- No hardcoded values in generation path

### E2E Tests: Test Full Generation Flow
- Generate content with fresh material (no training data)
- Generate content with trained material (45+ samples)
- Verify improvement between attempts
- Verify database growth after generation

---

## Documentation Requirements

### Architecture Decisions Must Be Explicit

Every major architectural pattern must have documentation explaining:

1. **What**: Describe the pattern
2. **Why**: Explain the reasoning
3. **How**: Show implementation
4. **Validation**: How to verify it's working
5. **Consequences**: What breaks if violated

### Example: Iterative Learning

**What**: PromptOptimizer runs on every generation attempt.

**Why**: System learns from Winston feedback between attempts. If it only runs once, it can't adapt to failures.

**How**: 
```python
# In generation loop
for attempt in range(1, max_attempts + 1):
    if self.prompt_optimizer:  # No attempt check
        prompt = self.prompt_optimizer.optimize_prompt(...)
```

**Validation**: 
- Integrity check: Verify no `attempt == 1` condition
- Behavioral test: Generate with 5 attempts, verify optimizer runs 5 times
- E2E test: Check logs show "🧠 Attempt X:" for all attempts

**Consequences**: If violated, system can't improve between attempts, success rate stays at baseline (~0%), learning system becomes useless.

---

## Enforcement Strategy

### Pre-Commit Hooks
- Run integrity checks on every commit
- Block commit if architectural violations detected
- Show clear error messages with fix instructions

### CI/CD Pipeline
- Run full test suite including behavioral tests
- Run E2E generation tests with sample materials
- Verify database growth after test runs
- Check documentation is up-to-date

### Code Review Checklist
- [ ] No `attempt == 1` conditions near PromptOptimizer
- [ ] No `.get(key, default)` in critical paths (use fail-fast)
- [ ] No hardcoded numeric literals (use config)
- [ ] Database logging happens immediately, not batched
- [ ] Changes match architectural patterns in docs

---

## Priority Architectural Patterns

**HIGHEST PRIORITY** (System breaks if violated):
1. Iterative learning (optimizer runs every attempt)
2. Fail-fast on missing dependencies
3. Immediate data persistence

**HIGH PRIORITY** (System degrades if violated):
4. Single source of truth (Materials.yaml)
5. Dynamic configuration (no hardcoded values)

**MEDIUM PRIORITY** (System works but harder to maintain):
6. Consistent error handling
7. Comprehensive logging
8. Clear abstraction boundaries

---

## How to Add New Architectural Requirements

1. **Document the pattern** in this file
2. **Add integrity check** in `processing/integrity/integrity_checker.py`
3. **Add behavioral test** in `tests/test_architectural_behavior.py`
4. **Update CI/CD** to run new checks
5. **Update code review checklist**

---

## Lessons Learned

### Bug: PromptOptimizer Only Ran on Attempt 1

**What went wrong**: 
- Code had `if self.prompt_optimizer and attempt == 1:`
- Integrity checker only verified presence, not behavior
- Bug existed for hours causing 0% success rate

**Root cause**:
- AI assistant made optimization assumption
- Integrity checker didn't validate iterative behavior
- No behavioral test existed

**Fix**:
- Removed `attempt == 1` condition
- Added behavioral validation to integrity checker
- Success rate improved from 0% to 3.1%

**Prevention**:
- Document iterative requirement explicitly
- Add behavioral test: verify optimizer runs N times for N attempts
- Integrity check: fail if `attempt == 1` exists near PromptOptimizer

---

**Last Updated**: November 15, 2025  
**Next Review**: When adding major architectural changes
