# Generation Chain Verification System

## Overview

The chain verification system ensures that all critical phases of the generation pipeline are executed and prevents accidental skipping of validation, enrichment, or learning steps.

**Key Features:**
- 🔍 **Automatic tracking** - No manual logging required
- 🛡️ **Fail-fast** - Raises exception if required phases skipped
- 📊 **Statistics** - Track phase completion rates over time
- 🎯 **Session-based** - Tracks individual generation executions
- 🔗 **Decorator-based** - Simple integration with `@track_phase`

---

## Quick Start

### 1. Basic Integration

```python
from processing.chain_verification import (
    ChainPhase, 
    ChainRegistry, 
    track_phase,
    ChainIncompleteError
)

class MyOrchestrator:
    def generate(self, identifier, component_type):
        # Start tracking
        import uuid
        session_id = f"{identifier}-{component_type}-{uuid.uuid4().hex[:8]}"
        self._current_session_id = session_id
        
        registry = ChainRegistry()
        registry.start_execution(session_id, identifier, component_type)
        
        try:
            # Your generation logic with tracked phases
            result = self._generate_internal()
            
            # Complete tracking
            registry.complete_execution(session_id, success=True)
            return result
            
        except ChainIncompleteError as e:
            # Critical error - chain incomplete!
            logger.error(f"Generation chain incomplete: {e}")
            raise
        
        except Exception as e:
            registry.complete_execution(session_id, success=False)
            raise
    
    @track_phase(ChainPhase.DATA_LOADING)
    def _load_data(self):
        # Your data loading logic
        pass
    
    @track_phase(ChainPhase.ENRICHMENT)
    def _enrich_data(self, facts):
        # Your enrichment logic
        pass
    
    @track_phase(ChainPhase.AI_DETECTION)
    def _detect_ai(self, text):
        # Your AI detection logic
        pass
```

### 2. Integration with UnifiedOrchestrator

The recommended integration pattern preserves existing code while adding verification:

```python
# In processing/unified_orchestrator.py

from processing.chain_verification import (
    ChainPhase, ChainRegistry, track_phase, ChainIncompleteError
)

class UnifiedOrchestrator:
    def generate(self, identifier: str, component_type: str, **kwargs):
        """Generate with chain verification"""
        import uuid
        
        # Start chain tracking
        session_id = f"{identifier}-{component_type}-{uuid.uuid4().hex[:8]}"
        self._current_session_id = session_id
        
        registry = ChainRegistry()
        registry.start_execution(session_id, identifier, component_type)
        
        try:
            # Call existing generation logic
            result = self._generate_internal(identifier, component_type, **kwargs)
            
            # Verify chain completeness
            registry.complete_execution(session_id, result.success)
            
            return result
            
        except ChainIncompleteError as e:
            # Log and fail - critical phases were skipped
            logger.error(f"❌ CRITICAL: {e}")
            raise
        
        except Exception as e:
            registry.complete_execution(session_id, success=False)
            raise
    
    def _generate_internal(self, identifier, component_type, **kwargs):
        """Existing generation logic (now tracked)"""
        # 1. Load data
        data = self._tracked_load_data(identifier)
        
        # 2. Enrich
        enriched = self._tracked_enrich(data)
        
        # 3. Build prompt
        prompt = self._tracked_build_prompt(enriched, component_type)
        
        # 4. Generate
        text = self._tracked_generate_text(prompt)
        
        # 5. Detect AI
        ai_score = self._tracked_detect_ai(text)
        
        # 6. Validate
        if self.config.readability_validation:
            self._tracked_validate_readability(text)
        else:
            # Intentionally skipped - mark it
            registry = ChainRegistry()
            registry.mark_phase_skipped(
                self._current_session_id,
                ChainPhase.READABILITY_VALIDATION,
                "disabled in config"
            )
        
        # 7. Persist
        self._tracked_persist(identifier, component_type, text)
        
        return ComponentResult(success=True, text=text)
    
    @track_phase(ChainPhase.DATA_LOADING)
    def _tracked_load_data(self, identifier):
        """Load data with tracking"""
        return self.adapter.get_item_data(identifier)
    
    @track_phase(ChainPhase.ENRICHMENT)
    def _tracked_enrich(self, data):
        """Enrich with tracking"""
        return self.enricher.enrich(data)
    
    @track_phase(ChainPhase.PROMPT_BUILDING)
    def _tracked_build_prompt(self, enriched, component_type):
        """Build prompt with tracking"""
        return self.prompt_builder.build(enriched, component_type)
    
    @track_phase(ChainPhase.API_GENERATION)
    def _tracked_generate_text(self, prompt):
        """Generate with tracking"""
        return self._call_api(prompt)
    
    @track_phase(ChainPhase.AI_DETECTION)
    def _tracked_detect_ai(self, text):
        """Detect AI with tracking"""
        return self.winston.detect_and_log(text)
    
    @track_phase(ChainPhase.READABILITY_VALIDATION)
    def _tracked_validate_readability(self, text):
        """Validate readability with tracking"""
        return self.readability_validator.validate(text)
    
    @track_phase(ChainPhase.DATA_PERSISTENCE)
    def _tracked_persist(self, identifier, component_type, text):
        """Persist with tracking"""
        return self.adapter.write_component(identifier, component_type, text)
```

---

## Chain Phases

The system tracks 12 critical phases:

```python
class ChainPhase(Enum):
    INITIALIZATION = "initialization"           # Orchestrator setup
    DATA_LOADING = "data_loading"              # Load from Materials.yaml
    ENRICHMENT = "enrichment"                  # Add extra facts
    VOICE_INJECTION = "voice_injection"        # Apply author voice
    PROMPT_BUILDING = "prompt_building"        # Construct final prompt
    TEMPERATURE_ADAPTATION = "temperature_adaptation"  # Adaptive temp
    API_GENERATION = "api_generation"          # Call LLM API
    AI_DETECTION = "ai_detection"              # Winston/ensemble
    READABILITY_VALIDATION = "readability_validation"  # Check quality
    CONTENT_EXTRACTION = "content_extraction"  # Parse response
    DATA_PERSISTENCE = "data_persistence"      # Write to Materials.yaml
    LEARNING_FEEDBACK = "learning_feedback"    # Update pattern learner
```

**Required phases** (must complete or be explicitly skipped):
- DATA_LOADING
- ENRICHMENT
- PROMPT_BUILDING
- API_GENERATION
- AI_DETECTION

**Optional phases** (can be skipped with reason):
- READABILITY_VALIDATION (if disabled in config)
- LEARNING_FEEDBACK (if learning disabled)
- TEMPERATURE_ADAPTATION (if using fixed temperature)

---

## Handling Optional Phases

When a phase is intentionally skipped (e.g., readability validation disabled), mark it explicitly:

```python
registry = ChainRegistry()

if not self.config.readability_validation:
    registry.mark_phase_skipped(
        self._current_session_id,
        ChainPhase.READABILITY_VALIDATION,
        "disabled in config"
    )
else:
    self._tracked_validate_readability(text)
```

This prevents false positives when verifying chain completeness.

---

## Error Handling

### ChainIncompleteError

Raised when required phases are missing:

```python
try:
    result = orchestrator.generate("Aluminum", "subtitle")
except ChainIncompleteError as e:
    # CRITICAL: Required phases were not executed
    logger.error(f"Generation failed: {e}")
    # This indicates a BUG in the orchestrator
    # Missing phases must be investigated immediately
```

### Phase Errors

Individual phase errors are recorded but don't stop execution:

```python
@track_phase(ChainPhase.AI_DETECTION)
def _detect_ai(self, text):
    try:
        return self.winston.detect(text)
    except WinstonAPIError as e:
        # Error recorded in registry
        # Orchestrator can decide whether to continue or fail
        logger.warning(f"AI detection failed: {e}")
        return None  # Or re-raise
```

---

## Statistics and Monitoring

### Generate Report

```python
from processing.chain_verification import generate_chain_verification_report

# After running generations
generate_chain_verification_report()
```

**Output:**
```
============================================================
GENERATION CHAIN VERIFICATION REPORT
============================================================

Total executions: 132
Successful: 127
Success rate: 96.2%

Phase Completion Rates:
  ✅ data_loading: 100.0%
  ✅ enrichment: 100.0%
  ✅ prompt_building: 100.0%
  ✅ api_generation: 98.5%
  ✅ ai_detection: 97.7%
  ⚠️  readability_validation: 85.6%
  ✅ data_persistence: 96.2%
  ⚠️  learning_feedback: 89.4%
============================================================
```

### Programmatic Access

```python
registry = ChainRegistry()
stats = registry.get_statistics()

# Check if any phase is under-performing
for phase, rate in stats['phase_completion_rates'].items():
    if rate < 0.95:
        logger.warning(f"Phase {phase} completion rate low: {rate:.1%}")
```

---

## Integration Testing

### Test Chain Completeness

```python
# tests/test_chain_verification.py

import pytest
from processing.chain_verification import ChainRegistry, ChainIncompleteError
from processing.unified_orchestrator import UnifiedOrchestrator

def test_complete_chain_execution():
    """Verify all required phases execute"""
    orchestrator = UnifiedOrchestrator(
        adapter=MaterialsAdapter(),
        config_path="processing/config.yaml"
    )
    
    # Generate
    result = orchestrator.generate("Aluminum", "subtitle")
    
    # Verify chain completeness
    assert result.success
    
    # Check registry
    registry = ChainRegistry()
    stats = registry.get_statistics()
    
    # All required phases should have 100% completion
    required_phases = [
        'data_loading',
        'enrichment',
        'prompt_building',
        'api_generation',
        'ai_detection'
    ]
    
    for phase in required_phases:
        assert stats['phase_completion_rates'][phase] == 1.0

def test_incomplete_chain_raises_error():
    """Verify exception when phases skipped"""
    orchestrator = BrokenOrchestrator()  # Missing AI detection
    
    with pytest.raises(ChainIncompleteError) as exc_info:
        orchestrator.generate("Steel", "caption")
    
    assert "ai_detection" in str(exc_info.value)
```

---

## Migration Strategy

### Phase 1: Add Tracking (Non-Breaking)

1. Add chain verification import to `unified_orchestrator.py`
2. Add session tracking to `generate()` method
3. Wrap existing methods with `@track_phase` decorators
4. Add explicit skip marking for optional phases
5. Test with existing test suite (should pass)

### Phase 2: Enable Verification (Breaking)

1. Add `complete_execution()` call with verification
2. Run full test suite
3. Fix any ChainIncompleteError exceptions (bugs in orchestrator)
4. Verify all 132 materials generate successfully

### Phase 3: Monitor (Production)

1. Add chain statistics logging
2. Monitor phase completion rates
3. Alert on rates < 95%
4. Investigate any incomplete chains

---

## Best Practices

### DO ✅

- **Use `@track_phase` on all pipeline methods** - Ensures automatic tracking
- **Mark intentional skips explicitly** - Prevents false positives
- **Monitor statistics regularly** - Catch degradation early
- **Investigate ChainIncompleteError immediately** - Indicates serious bug
- **Keep phases granular** - Better visibility into pipeline

### DON'T ❌

- **Don't catch ChainIncompleteError silently** - This is critical
- **Don't skip required phases without marking** - Will cause exception
- **Don't add phases retroactively** - May break existing chains
- **Don't use for performance-critical code** - Small overhead from tracking
- **Don't modify registry directly** - Use provided methods

---

## Troubleshooting

### "ChainIncompleteError: Missing required phases"

**Cause:** Required phases not executed or not tracked

**Fix:**
1. Check orchestrator code - is phase actually executed?
2. Verify `@track_phase` decorator present
3. Check session_id propagation
4. For optional phases, add explicit skip marking

### "No session_id for phase X - skipping tracking"

**Cause:** Session ID not available to decorator

**Fix:**
1. Ensure `self._current_session_id` set in orchestrator
2. Pass `session_id` as kwarg if not using instance attribute
3. Check decorator has access to orchestrator instance (`args[0]`)

### Phase completion rate < 100% for required phase

**Cause:** Phase failing or being skipped intermittently

**Fix:**
1. Check logs for phase errors
2. Review phase logic for conditional execution
3. Verify no early returns bypassing phase
4. Add retry logic if transient failures

---

## Example: Full Integration

See `processing/unified_orchestrator.py` for complete integration example with:
- Session tracking
- Phase decoration
- Skip marking
- Error handling
- Statistics reporting

---

## Summary

The chain verification system provides:

1. ✅ **Automatic phase tracking** via decorators
2. ✅ **Fail-fast on incomplete chains** via ChainIncompleteError
3. ✅ **Statistics and monitoring** via ChainRegistry
4. ✅ **Explicit skip handling** for optional phases
5. ✅ **Integration tests** to verify completeness

This ensures that **no module is accidentally skipped** in the generation pipeline, addressing the user's requirement for chain completeness verification.
