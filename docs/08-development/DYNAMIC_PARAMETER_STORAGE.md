# Dynamic Parameter Storage Architecture

**Date**: November 15, 2025  
**Status**: Proposed Solution  
**Purpose**: Eliminate hardcoded values by proper parameter propagation

---

## 🎯 Problem Statement

**Current Issue**: 36 hardcoded values exist because parameters aren't properly stored and propagated through the generation pipeline.

**Root Cause**: Parameters are calculated in `DynamicConfig` but then stored in multiple places with hardcoded fallbacks:
- `api_penalties` defaulting to `{'frequency_penalty': 0.0, 'presence_penalty': 0.0}`
- `.get()` calls with hardcoded defaults throughout the pipeline
- No single source of truth for runtime parameters

**Impact**: 
- Winston detects 100% AI because penalties are always 0.0
- Config slider changes don't affect generation
- Debugging is impossible (can't tell what values were actually used)

---

## 💡 Proposed Solution: GenerationParameters Class

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    DynamicConfig                            │
│  • Reads config.yaml sliders (1-10)                        │
│  • Calculates all technical parameters                     │
│  • Returns GenerationParameters object                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│             GenerationParameters (Immutable)                │
│  • Stores ALL parameters in typed fields                   │
│  • No defaults, no fallbacks, no .get()                    │
│  • Validates completeness on creation                      │
│  • Serializable for logging/debugging                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   DynamicGenerator                          │
│  • Receives GenerationParameters object                    │
│  • Adapts parameters based on learning/retries             │
│  • Creates new GenerationParameters (immutable pattern)    │
│  • Passes to API client                                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     API Client                              │
│  • Receives GenerationParameters                           │
│  • Extracts needed fields directly (no .get())             │
│  • Logs exact parameters used                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Implementation: GenerationParameters Class

### File: `processing/config/generation_parameters.py`

```python
"""
Generation Parameters - Single Source of Truth

Immutable data class that holds ALL parameters for a single generation attempt.
Replaces scattered dicts and hardcoded defaults throughout the codebase.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional
import json


@dataclass(frozen=True)
class APIParameters:
    """API-specific parameters"""
    temperature: float
    max_tokens: int
    frequency_penalty: float
    presence_penalty: float
    
    def __post_init__(self):
        """Validate ranges on creation"""
        if not (0.3 <= self.temperature <= 1.1):
            raise ValueError(f"Temperature {self.temperature} not in range 0.3-1.1")
        if not (0.0 <= self.frequency_penalty <= 2.0):
            raise ValueError(f"Frequency penalty {self.frequency_penalty} not in range 0.0-2.0")
        if not (0.0 <= self.presence_penalty <= 2.0):
            raise ValueError(f"Presence penalty {self.presence_penalty} not in range 0.0-2.0")
        if self.max_tokens < 50:
            raise ValueError(f"Max tokens {self.max_tokens} too low")


@dataclass(frozen=True)
class VoiceParameters:
    """Voice and style parameters"""
    trait_frequency: float
    opinion_rate: float
    reader_address_rate: float
    colloquialism_frequency: float
    structural_predictability: float
    emotional_tone: float
    imperfection_tolerance: float
    sentence_rhythm_variation: float
    
    def __post_init__(self):
        """Validate all in 0.0-1.0 range"""
        for field_name, value in asdict(self).items():
            if not (0.0 <= value <= 1.0):
                raise ValueError(f"{field_name} {value} not in range 0.0-1.0")


@dataclass(frozen=True)
class EnrichmentParameters:
    """Data enrichment parameters"""
    technical_intensity: int  # 1-3
    context_detail_level: int  # 1-3
    fact_formatting_style: str  # 'formal' | 'balanced' | 'conversational'
    engagement_level: int  # 1-3
    
    def __post_init__(self):
        """Validate ranges"""
        if self.technical_intensity not in [1, 2, 3]:
            raise ValueError(f"Technical intensity must be 1-3, got {self.technical_intensity}")
        if self.context_detail_level not in [1, 2, 3]:
            raise ValueError(f"Context detail level must be 1-3, got {self.context_detail_level}")
        if self.engagement_level not in [1, 2, 3]:
            raise ValueError(f"Engagement level must be 1-3, got {self.engagement_level}")
        if self.fact_formatting_style not in ['formal', 'balanced', 'conversational']:
            raise ValueError(f"Invalid fact formatting style: {self.fact_formatting_style}")


@dataclass(frozen=True)
class ValidationParameters:
    """Validation and quality parameters"""
    detection_threshold: float
    readability_min: float
    readability_max: float
    grammar_strictness: float
    confidence_high: float
    confidence_medium: float
    
    def __post_init__(self):
        """Validate ranges"""
        if not (0.0 <= self.detection_threshold <= 100.0):
            raise ValueError(f"Detection threshold {self.detection_threshold} not in range 0-100")
        if not (0.0 <= self.grammar_strictness <= 1.0):
            raise ValueError(f"Grammar strictness {self.grammar_strictness} not in range 0.0-1.0")


@dataclass(frozen=True)
class RetryBehavior:
    """Retry behavior parameters"""
    max_attempts: int
    retry_temperature_increase: float
    
    def __post_init__(self):
        """Validate ranges"""
        if self.max_attempts < 1 or self.max_attempts > 10:
            raise ValueError(f"Max attempts {self.max_attempts} not in range 1-10")
        if not (0.0 <= self.retry_temperature_increase <= 0.3):
            raise ValueError(f"Retry temp increase {self.retry_temperature_increase} not in range 0.0-0.3")


@dataclass(frozen=True)
class GenerationParameters:
    """
    Complete parameter set for one generation attempt.
    
    Immutable (frozen=True) - adaptations create new instances.
    No defaults - all fields must be provided.
    Validated on creation - fail-fast if invalid.
    """
    api: APIParameters
    voice: VoiceParameters
    enrichment: EnrichmentParameters
    validation: ValidationParameters
    retry: RetryBehavior
    component_type: str
    material_name: str
    attempt: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for logging/serialization"""
        return {
            'api': asdict(self.api),
            'voice': asdict(self.voice),
            'enrichment': asdict(self.enrichment),
            'validation': asdict(self.validation),
            'retry': asdict(self.retry),
            'component_type': self.component_type,
            'material_name': self.material_name,
            'attempt': self.attempt
        }
    
    def to_json(self) -> str:
        """Serialize to JSON for logging"""
        return json.dumps(self.to_dict(), indent=2)
    
    def adapt(self, **changes) -> 'GenerationParameters':
        """
        Create new parameters with changes (immutable pattern).
        
        Example:
            new_params = params.adapt(
                api=APIParameters(
                    temperature=0.8,
                    max_tokens=params.api.max_tokens,
                    frequency_penalty=params.api.frequency_penalty,
                    presence_penalty=params.api.presence_penalty
                )
            )
        """
        current = self.to_dict()
        
        # Update with changes
        for key, value in changes.items():
            if key in ['api', 'voice', 'enrichment', 'validation', 'retry']:
                current[key] = asdict(value)
            else:
                current[key] = value
        
        # Recreate from dict
        return GenerationParameters(
            api=APIParameters(**current['api']),
            voice=VoiceParameters(**current['voice']),
            enrichment=EnrichmentParameters(**current['enrichment']),
            validation=ValidationParameters(**current['validation']),
            retry=RetryBehavior(**current['retry']),
            component_type=current['component_type'],
            material_name=current['material_name'],
            attempt=current['attempt']
        )
    
    def with_attempt(self, attempt: int) -> 'GenerationParameters':
        """Convenience method to create params for next retry attempt"""
        return self.adapt(attempt=attempt)
    
    def with_temperature(self, temperature: float) -> 'GenerationParameters':
        """Convenience method to adjust temperature"""
        new_api = APIParameters(
            temperature=temperature,
            max_tokens=self.api.max_tokens,
            frequency_penalty=self.api.frequency_penalty,
            presence_penalty=self.api.presence_penalty
        )
        return self.adapt(api=new_api)
    
    def __str__(self) -> str:
        """Human-readable summary"""
        return (
            f"GenerationParameters("
            f"temp={self.api.temperature:.3f}, "
            f"penalties={self.api.frequency_penalty:.2f}/{self.api.presence_penalty:.2f}, "
            f"tokens={self.api.max_tokens}, "
            f"attempt={self.attempt}, "
            f"component={self.component_type})"
        )
```

---

## 🔄 Migration Plan

### Phase 1: Create GenerationParameters Class (30 min)

✅ **Actions**:
1. Create `processing/config/generation_parameters.py` with classes above
2. Add comprehensive validation in `__post_init__` methods
3. Add unit tests: `tests/test_generation_parameters.py`

**Test Coverage**:
- Valid parameter creation
- Range validation (temperatures, penalties, etc.)
- Immutability enforcement
- Serialization (to_dict, to_json)
- Adaptation (adapt, with_temperature, with_attempt)

### Phase 2: Update DynamicConfig to Return GenerationParameters (45 min)

✅ **Changes to `processing/config/dynamic_config.py`**:

```python
from processing.config.generation_parameters import (
    GenerationParameters, APIParameters, VoiceParameters,
    EnrichmentParameters, ValidationParameters, RetryBehavior
)

class DynamicConfig:
    def get_all_generation_params(self, 
                                   component_type: str,
                                   material_name: str = '',
                                   attempt: int = 1) -> GenerationParameters:
        """
        Get complete parameter set as validated, immutable object.
        
        Args:
            component_type: Component being generated
            material_name: Material name for logging
            attempt: Attempt number for retry logic
            
        Returns:
            GenerationParameters object (validated, immutable)
        """
        # Calculate penalties from humanness_intensity
        humanness = self.base_config.get_humanness_intensity()
        
        if humanness <= 3:
            frequency_penalty = 0.0
            presence_penalty = 0.0
        elif humanness <= 7:
            frequency_penalty = (humanness - 3) / 4.0 * 0.6
            presence_penalty = (humanness - 3) / 4.0 * 0.6
        else:
            frequency_penalty = 0.6 + (humanness - 7) / 3.0 * 0.6
            presence_penalty = 0.6 + (humanness - 7) / 3.0 * 0.6
        
        # Create API parameters
        api_params = APIParameters(
            temperature=self.calculate_temperature(component_type),
            max_tokens=self.calculate_max_tokens(component_type),
            frequency_penalty=round(frequency_penalty, 2),
            presence_penalty=round(presence_penalty, 2)
        )
        
        # Create voice parameters
        voice_calcs = self.calculate_voice_parameters()
        voice_params = VoiceParameters(
            trait_frequency=voice_calcs['trait_frequency'],
            opinion_rate=voice_calcs['opinion_rate'],
            reader_address_rate=voice_calcs['reader_address_rate'],
            colloquialism_frequency=voice_calcs['colloquialism_frequency'],
            structural_predictability=voice_calcs['structural_predictability'],
            emotional_tone=voice_calcs['emotional_tone'],
            imperfection_tolerance=voice_calcs.get('imperfection_tolerance', 0.5),
            sentence_rhythm_variation=voice_calcs.get('sentence_rhythm_variation', 0.5)
        )
        
        # Create enrichment parameters
        enrich_calcs = self.calculate_enrichment_params()
        enrichment_params = EnrichmentParameters(
            technical_intensity=enrich_calcs['technical_intensity'],
            context_detail_level=enrich_calcs['context_detail_level'],
            fact_formatting_style=enrich_calcs['fact_formatting_style'],
            engagement_level=enrich_calcs['engagement_level']
        )
        
        # Create validation parameters
        read_thresh = self.calculate_readability_thresholds()
        conf_thresh = self.calculate_confidence_thresholds()
        validation_params = ValidationParameters(
            detection_threshold=self.calculate_detection_threshold(),
            readability_min=read_thresh['min'],
            readability_max=read_thresh['max'],
            grammar_strictness=self.calculate_grammar_strictness(),
            confidence_high=conf_thresh['high'],
            confidence_medium=conf_thresh['medium']
        )
        
        # Create retry behavior
        retry_calcs = self.calculate_retry_behavior()
        retry_params = RetryBehavior(
            max_attempts=retry_calcs['max_attempts'],
            retry_temperature_increase=retry_calcs['retry_temperature_increase']
        )
        
        # Return complete, validated parameter set
        return GenerationParameters(
            api=api_params,
            voice=voice_params,
            enrichment=enrichment_params,
            validation=validation_params,
            retry=retry_params,
            component_type=component_type,
            material_name=material_name,
            attempt=attempt
        )
```

### Phase 3: Update DynamicGenerator to Use GenerationParameters (1 hour)

✅ **Changes to `processing/generator.py`**:

**Method: `_get_adapted_parameters`**:
```python
def _get_adapted_parameters(
    self, 
    material_name: str,
    component_type: str,
    attempt: int,
    last_winston_result: Optional[Dict] = None
) -> GenerationParameters:
    """
    Get adapted parameters for current attempt.
    
    Returns:
        GenerationParameters object (immutable, validated)
    """
    # Get baseline parameters
    params = self.dynamic_config.get_all_generation_params(
        component_type=component_type,
        material_name=material_name,
        attempt=attempt
    )
    
    # BEST PRACTICE 1: Cross-session learning
    try:
        learned_temp = self.temperature_advisor.recommend_temperature(
            material=material_name,
            component_type=component_type,
            attempt=attempt,
            fallback_temp=params.api.temperature
        )
        
        if learned_temp != params.api.temperature:
            self.logger.info(f"📊 Learned temperature: {learned_temp:.3f}")
            params = params.with_temperature(learned_temp)
    except Exception as e:
        self.logger.warning(f"Failed to get learned temperature: {e}")
    
    # BEST PRACTICE 2: Failure-type-specific retry strategies
    if last_winston_result and attempt > 1:
        params = self._adapt_for_failure(params, last_winston_result)
    
    # BEST PRACTICE 3: Exploration (15% random variation)
    if attempt > 1 and random.random() < 0.15:
        params = self._explore_parameter_space(params)
    
    return params


def _adapt_for_failure(
    self,
    params: GenerationParameters,
    winston_result: Dict
) -> GenerationParameters:
    """Adapt parameters based on failure analysis"""
    failure_analysis = self.analyzer.analyze_failure(winston_result)
    failure_type = failure_analysis['failure_type']
    
    if failure_type == 'uniform':
        # All sentences bad: increase randomness
        new_temp = min(1.0, params.api.temperature + 0.15)
        return params.with_temperature(new_temp)
    
    elif failure_type == 'borderline':
        # Close to passing: fine-tune
        new_temp = max(0.5, params.api.temperature - 0.03)
        return params.with_temperature(new_temp)
    
    elif failure_type == 'partial':
        # Some sentences human: moderate boost
        new_temp = min(1.0, params.api.temperature + 0.08)
        return params.with_temperature(new_temp)
    
    else:
        # Standard progression
        new_temp = min(1.0, params.api.temperature + 
                       params.retry.retry_temperature_increase)
        return params.with_temperature(new_temp)
```

**Method: `_generate_with_api`**:
```python
def _generate_with_api(
    self,
    prompt: str,
    params: GenerationParameters,  # <-- Changed from scattered args
    system_prompt: Optional[str] = None
) -> str:
    """
    Generate content via API using provided parameters.
    
    Args:
        prompt: Generation prompt
        params: Complete parameter set (validated, immutable)
        system_prompt: Optional system prompt
        
    Returns:
        Generated content
    """
    # Log parameters (exact values that will be used)
    self.logger.info(f"🌡️  Temperature: {params.api.temperature:.3f}, Max tokens: {params.api.max_tokens}")
    self.logger.info(f"⚖️  Penalties: frequency={params.api.frequency_penalty:.2f}, presence={params.api.presence_penalty:.2f}")
    
    # Create API request (NO .get() calls, NO defaults)
    from shared.api.client import GenerationRequest
    request = GenerationRequest(
        prompt=prompt,
        system_prompt=system_prompt,
        max_tokens=params.api.max_tokens,
        temperature=params.api.temperature,
        frequency_penalty=params.api.frequency_penalty,  # <-- NO fallback
        presence_penalty=params.api.presence_penalty     # <-- NO fallback
    )
    
    response = self.api_client.generate(request)
    
    if not response.success:
        raise RuntimeError(f"API call failed: {response.error}")
    
    # Log exact parameters used (for debugging/learning)
    self.feedback_db.log_generation_params(params.to_dict())
    
    return response.content.strip()
```

### Phase 4: Remove All Hardcoded Values (30 min)

✅ **Find and replace patterns**:

❌ **BEFORE**:
```python
api_penalties = base_params.get('api_params', {}).get('penalties', {
    'frequency_penalty': 0.0,
    'presence_penalty': 0.0
})

frequency_penalty = api_penalties.get('frequency_penalty', 0.0)
presence_penalty = api_penalties.get('presence_penalty', 0.0)
```

✅ **AFTER**:
```python
# params is GenerationParameters object - no .get() needed
frequency_penalty = params.api.frequency_penalty
presence_penalty = params.api.presence_penalty
```

### Phase 5: Add Parameter Logging to Database (15 min)

✅ **Add to `processing/detection/winston_feedback_db.py`**:

```python
def log_generation_params(self, params: Dict[str, Any]) -> int:
    """
    Log exact parameters used for generation attempt.
    
    Enables analysis of what parameter combinations work best.
    
    Args:
        params: Parameters dict from GenerationParameters.to_dict()
        
    Returns:
        Row ID of inserted record
    """
    conn = self._get_connection()
    cursor = conn.execute("""
        INSERT INTO generation_params_log (
            timestamp,
            material_name,
            component_type,
            attempt,
            temperature,
            frequency_penalty,
            presence_penalty,
            max_tokens,
            detection_threshold,
            params_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        params.get('material_name', ''),
        params.get('component_type', ''),
        params.get('attempt', 1),
        params['api']['temperature'],
        params['api']['frequency_penalty'],
        params['api']['presence_penalty'],
        params['api']['max_tokens'],
        params['validation']['detection_threshold'],
        json.dumps(params)
    ))
    conn.commit()
    return cursor.lastrowid
```

---

## ✅ Benefits

### Before (Current State)
- ❌ 36 hardcoded values scattered throughout code
- ❌ Parameters lost/mutated during propagation
- ❌ `.get()` calls with silent defaults everywhere
- ❌ Impossible to debug what parameters were used
- ❌ Winston always sees frequency_penalty=0.0
- ❌ Config changes don't affect generation

### After (With GenerationParameters)
- ✅ **Zero hardcoded values** - all from config/dynamic calculation
- ✅ **Complete parameter tracking** - know exactly what was used
- ✅ **Fail-fast validation** - invalid params caught immediately
- ✅ **Immutable pattern** - adaptations create new objects
- ✅ **Serializable** - can log/analyze parameter effectiveness
- ✅ **Type-safe** - IDE autocomplete, compile-time checks
- ✅ **Debuggable** - params.to_json() shows exact state

---

## 📊 Expected Results

After implementation:

1. **Integrity Check**: 0 violations (was 36)
2. **Winston Detection**: Properly uses penalties → more human-like output
3. **Config Responsiveness**: Slider changes immediately affect generation
4. **Debugging**: `params.to_json()` shows exact parameters used
5. **Learning**: Database tracks which parameter combinations succeed

---

## 🚀 Next Steps

1. ✅ Create `GenerationParameters` class with tests
2. ✅ Update `DynamicConfig.get_all_generation_params()` 
3. ✅ Update `DynamicGenerator` methods to use `GenerationParameters`
4. ✅ Remove all `.get()` calls with hardcoded defaults
5. ✅ Add parameter logging to database
6. ✅ Run integrity check → verify 0 violations
7. ✅ Test caption generation → verify Winston detection works

**Estimated Total Time**: 2.5 hours
