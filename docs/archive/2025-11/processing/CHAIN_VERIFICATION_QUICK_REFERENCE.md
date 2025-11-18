# Chain Verification Quick Reference

**For**: Developers integrating chain verification  
**File**: `processing/chain_verification.py`  
**Doc**: `processing/docs/CHAIN_VERIFICATION_GUIDE.md`

---

## ⚡ Quick Integration (5 Steps)

### Step 1: Import
```python
from processing.chain_verification import (
    ChainPhase, ChainRegistry, track_phase, ChainIncompleteError
)
```

### Step 2: Start Tracking in `generate()`
```python
def generate(self, identifier, component_type):
    session_id = f"{identifier}-{component_type}-{uuid.uuid4().hex[:8]}"
    self._current_session_id = session_id
    
    registry = ChainRegistry()
    registry.start_execution(session_id, identifier, component_type)
```

### Step 3: Add Decorators to Methods
```python
@track_phase(ChainPhase.DATA_LOADING)
def _load_data(self, identifier):
    return self.adapter.get_item_data(identifier)

@track_phase(ChainPhase.ENRICHMENT)
def _enrich_data(self, facts):
    return self.enricher.enrich(facts)

@track_phase(ChainPhase.API_GENERATION)
def _call_api(self, prompt):
    return self.client.generate(prompt)
```

### Step 4: Mark Optional Skips
```python
if not self.config.readability_validation:
    registry.mark_phase_skipped(
        self._current_session_id,
        ChainPhase.READABILITY_VALIDATION,
        "disabled in config"
    )
```

### Step 5: Complete with Verification
```python
try:
    result = self._generate_internal(identifier, component_type)
    registry.complete_execution(session_id, result.success)
    return result

except ChainIncompleteError as e:
    logger.error(f"❌ CRITICAL: {e}")
    raise
```

---

## 🎯 12 Chain Phases

### Required (5 phases)
- `ChainPhase.DATA_LOADING` ⭐
- `ChainPhase.ENRICHMENT` ⭐
- `ChainPhase.PROMPT_BUILDING` ⭐
- `ChainPhase.API_GENERATION` ⭐
- `ChainPhase.AI_DETECTION` ⭐

### Optional (7 phases)
- `ChainPhase.INITIALIZATION`
- `ChainPhase.VOICE_INJECTION`
- `ChainPhase.TEMPERATURE_ADAPTATION`
- `ChainPhase.READABILITY_VALIDATION`
- `ChainPhase.CONTENT_EXTRACTION`
- `ChainPhase.DATA_PERSISTENCE`
- `ChainPhase.LEARNING_FEEDBACK`

---

## 🔍 Monitoring

### Generate Report
```python
from processing.chain_verification import generate_chain_verification_report

generate_chain_verification_report()
```

### Check Statistics
```python
registry = ChainRegistry()
stats = registry.get_statistics()

print(f"Success rate: {stats['success_rate']:.1%}")
for phase, rate in stats['phase_completion_rates'].items():
    print(f"{phase}: {rate:.1%}")
```

### Get Execution Details
```python
execution = registry.get_execution(session_id)
print(f"Completed: {execution.completed_phases}")
print(f"Skipped: {execution.skipped_phases}")
print(f"Errors: {execution.errors}")
```

---

## ⚠️ Error Handling

### ChainIncompleteError
**Raised when**: Required phases missing  
**Indicates**: Critical bug in orchestrator  
**Action**: Fix immediately - do NOT catch silently

```python
# ❌ WRONG - silently catching critical error
try:
    result = orchestrator.generate("Steel", "caption")
except ChainIncompleteError:
    return None  # BAD!

# ✅ RIGHT - log and re-raise
try:
    result = orchestrator.generate("Steel", "caption")
except ChainIncompleteError as e:
    logger.error(f"Chain incomplete: {e}")
    raise  # Must propagate
```

### Phase Errors
**Raised when**: Individual phase fails  
**Indicates**: Transient or recoverable error  
**Action**: Recorded in registry, orchestrator decides retry

```python
@track_phase(ChainPhase.API_GENERATION)
def _call_api(self, prompt):
    try:
        return self.client.generate(prompt)
    except APIError as e:
        # Error recorded in registry automatically
        logger.warning(f"API error: {e}")
        raise  # Or handle with retry logic
```

---

## 📊 Expected Rates

### Healthy System
- ✅ Required phases: **100%**
- ✅ API generation: **>95%** (transient errors ok)
- ✅ AI detection: **>95%**
- ⚠️ Readability validation: **>80%** (can be disabled)

### Unhealthy System
- ❌ Any required phase < 100%
- ❌ Frequent ChainIncompleteError exceptions
- ❌ High error rates in critical phases

---

## 🔧 Troubleshooting

### "ChainIncompleteError: Missing required phases"
**Cause**: Required phase not executed  
**Fix**: 
1. Check if phase method called in orchestrator
2. Verify `@track_phase` decorator present
3. Check session_id propagation to decorator

### "No session_id for phase X"
**Cause**: Decorator can't find session ID  
**Fix**:
1. Ensure `self._current_session_id` set
2. Or pass `session_id` as kwarg
3. Check decorator has access to instance (`args[0]`)

### Phase completion rate < 100% for required phase
**Cause**: Phase failing or being skipped intermittently  
**Fix**:
1. Check logs for phase errors
2. Review phase logic for conditional execution
3. Verify no early returns bypassing phase

---

## ✅ Checklist for Integration

- [ ] Imported chain verification classes
- [ ] Added session tracking to `generate()`
- [ ] Decorated all phase methods with `@track_phase`
- [ ] Marked optional skips explicitly
- [ ] Added `complete_execution()` with verification
- [ ] Handle `ChainIncompleteError` (log + re-raise)
- [ ] Run integration tests
- [ ] Generate verification report
- [ ] Verify required phases at 100%

---

## 📚 Full Documentation

See `processing/docs/CHAIN_VERIFICATION_GUIDE.md` for:
- Complete integration examples
- All 12 phases explained
- Migration strategy
- Best practices
- Troubleshooting guide
- Test examples

---

## 🧪 Testing

```bash
# Run chain verification tests
python3 -m pytest processing/tests/test_chain_verification.py -v

# Expected: 18/18 tests passing
```

---

## 🎯 Remember

1. ✅ **Required phases MUST complete** - No exceptions
2. ✅ **Optional phases marked explicitly** - Prevents false errors
3. ✅ **ChainIncompleteError is CRITICAL** - Never catch silently
4. ✅ **Monitor statistics regularly** - Catch degradation early
5. ✅ **Report after each batch** - Verify chain health
