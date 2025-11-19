# ADR-002: Fail-Fast vs Runtime Recovery

**Status**: Accepted (Established early, clarified November 18, 2025)

## Context

The system has two types of issues:
1. **Configuration Issues**: Missing files, invalid config, wrong API keys
2. **Runtime Issues**: API timeouts, network errors, transient failures

Need to decide: When should the system fail immediately vs when should it retry?

## The Confusion

The docs say "fail-fast architecture" but also have retry logic. AI assistants were confused:
- "Should I remove retry logic to be more fail-fast?"
- "Is retry logic a 'fallback' that violates fail-fast?"
- "When is it okay to retry vs when must it fail?"

## Decision

**Fail-fast applies to SETUP/CONFIGURATION, not RUNTIME ERRORS.**

### Fail-Fast: Configuration & Setup Issues

**Fail immediately on**:
- Missing configuration files
- Invalid API keys (if not found in .env)
- Required dependencies not installed
- Missing templates or prompt files
- Invalid data structures
- Schema violations

**Why**: These are programming errors that should be fixed, not worked around.

**Example**:
```python
# ✅ CORRECT: Fail-fast on missing config
if not os.path.exists(config_file):
    raise ConfigurationError(f"Config file required: {config_file}")

# ❌ WRONG: Default value that bypasses validation
config = load_config() or {"default": "values"}  # NO!
```

### Runtime Recovery: Transient Issues

**DO retry on**:
- API timeouts (network issues)
- Rate limiting (429 errors)
- Temporary service unavailability (503 errors)
- Connection resets
- Winston API transient failures

**Why**: These are operational issues that resolve themselves. Retrying is the correct behavior.

**Example**:
```python
# ✅ CORRECT: Retry transient API failures
for attempt in range(max_retries):
    try:
        response = api_client.generate(request)
        break
    except APITimeout:
        if attempt < max_retries - 1:
            time.sleep(backoff_delay)
            continue
        raise
```

### Quality-Based Iteration: Not Retry, Not Fallback

**DO iterate on**:
- Winston score too high (>30% AI detection)
- Realism score too low (<7.0/10)
- Subjective validation failures
- Readability issues

**Why**: This is the learning loop working as designed. The system tries different parameters to pass quality gates.

**Example**:
```python
# ✅ CORRECT: Parameter adjustment based on quality feedback
for attempt in range(max_attempts):
    content = generate(params)
    
    if passes_quality_gates(content):
        return content
    
    # Learn from failure, adjust parameters
    params = adjust_parameters_based_on_feedback(params, feedback)
```

## Consequences

### Clear Guidelines for AI Assistants

1. **Removing retry logic for API calls**: ❌ WRONG - this is runtime recovery
2. **Removing parameter adjustment loops**: ❌ WRONG - this is the learning system
3. **Adding default config values**: ❌ WRONG - this bypasses fail-fast validation
4. **Adding retry for missing files**: ❌ WRONG - fix the configuration instead

### When Someone Says "Make It More Fail-Fast"

**Ask**: "Is this a configuration issue or a runtime issue?"
- Configuration → Fail immediately with clear error
- Runtime → Keep retry logic, it's correct

## The Three Categories

| Category | Examples | Behavior | Reason |
|----------|----------|----------|---------|
| **Configuration** | Missing files, invalid config, wrong schema | **FAIL FAST** | Programming error - must be fixed |
| **Runtime** | API timeout, network error, rate limit | **RETRY** | Transient - will resolve itself |
| **Quality** | High AI score, low realism, violations | **ITERATE** | Learning - adjust parameters |

## Alternatives Considered

### Alternative 1: Retry Everything
**Rejected because**:
- Masks configuration errors
- System runs in degraded state
- Harder to debug issues
- Violates fail-fast principle

### Alternative 2: Fail on Any Error
**Rejected because**:
- Too brittle for production
- Network issues cause total failure
- No resilience to transient problems
- Learning loop can't function

### Alternative 3: Separate "Strict Mode"
**Rejected because**:
- Adds complexity
- Developers might use wrong mode
- Better to have clear rules that always apply

## Related Decisions

- System architecture established this pattern early
- See: `.github/copilot-instructions.md` "Core Principles"

## For AI Assistants

**When you see retry logic**:
1. ✅ Check what it's retrying
2. ✅ API calls → Keep the retry, it's correct
3. ✅ Quality checks → Keep the iteration, it's the learning loop
4. ❌ Configuration loading → This should fail-fast
5. ❌ Missing files → This should fail-fast

**When adding new code**:
1. ✅ Configuration issues → raise specific exceptions immediately
2. ✅ Runtime issues → implement retry with backoff
3. ✅ Quality issues → iterate with parameter adjustment
4. ❌ Never use default values to bypass validation
5. ❌ Never catch exceptions and continue silently
