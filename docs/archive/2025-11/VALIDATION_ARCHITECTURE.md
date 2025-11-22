# Validation Architecture

**Ultra-Modular 6-Pass Pipeline with 19 Discrete Steps**  
**Created**: November 19, 2025  
**Status**: ✅ Active (replaces legacy ValidationAndImprovementPipeline)

---

## 🎯 Overview

The validation system runs **AFTER** content generation to assess quality, apply learning systems, and regenerate if needed. It uses an ultra-modular architecture with 19 independent steps organized into 6 coordinated passes.

### Why Ultra-Modular?

**OLD SYSTEM (Monolithic - 474 lines)**:
- ❌ Single class with 12 methods
- ❌ Mixed concerns (validation + learning + recording + regeneration)
- ❌ Difficult to test (one massive integration test)
- ❌ Difficult to debug (errors buried in 474 lines)
- ❌ No per-step timing or profiling
- ❌ Hard to replace individual components

**NEW SYSTEM (Ultra-Modular - 757 lines across 22 files)**:
- ✅ 19 discrete steps (30-60 lines each, single responsibility)
- ✅ Independently testable (19 focused unit tests)
- ✅ Clear debugging ("Step 2.3 ReadabilityChecker failed")
- ✅ Automatic per-step timing
- ✅ Easy step replacement (swap implementation, no coordinator changes)
- ✅ Error isolation (one step's failure doesn't cascade)
- ✅ Parallel execution ready (Pass 2 can run 4 quality checks simultaneously)

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                   VALIDATION ORCHESTRATOR                       │
│              (Lightweight Coordinator - Zero Logic)             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ├─► PASS 1: LOAD (2 steps)
                              │   ├─ 1.1 ContentLoader
                              │   └─ 1.2 ContentValidator
                              │
                              ├─► PASS 2: QUALITY ASSESSMENT (5 steps)
                              │   ├─ 2.1 WinstonDetector
                              │   ├─ 2.2 RealismEvaluator
                              │   ├─ 2.3 ReadabilityChecker
                              │   ├─ 2.4 SubjectiveChecker
                              │   └─ 2.5 CompositeScorer (Winston 60% + Realism 40%)
                              │
                              ├─► PASS 3: GATE CHECKS (5 steps)
                              │   ├─ 3.1 WinstonGateChecker (< 33% AI threshold)
                              │   ├─ 3.2 RealismGateChecker (≥ 7.0 threshold)
                              │   ├─ 3.3 ReadabilityGateChecker (must pass)
                              │   ├─ 3.4 SubjectiveGateChecker (zero violations)
                              │   └─ 3.5 CompositeGateChecker (all gates must pass)
                              │
                              ├─► PASS 4: LEARNING (5 steps)
                              │   ├─ 4.1 SweetSpotRetriever (historical optimal ranges)
                              │   ├─ 4.2 TemperatureCalculator (Winston-based)
                              │   ├─ 4.3 RealismAdjuster (failure adjustments)
                              │   ├─ 4.4 PatternAdjuster (learned patterns)
                              │   └─ 4.5 AdjustmentMerger (priority: sweet_spot → temp → realism → pattern)
                              │
                              ├─► PASS 5: RECORDING (2 steps)
                              │   ├─ 5.1 PatternRecorder (updates learned_patterns.yaml)
                              │   └─ 5.2 DatabaseLogger (logs to Winston feedback DB)
                              │
                              └─► PASS 6: REGENERATION (1 step)
                                  └─ 6.1 ContentRegenerator (calls SimpleGenerator with adjustments)
```

---

## 🔧 Component Details

### BaseStep Framework

All 19 steps inherit from `BaseStep` abstract class:

```python
from postprocessing.steps.base_step import BaseStep

class MyStep(BaseStep):
    def _validate_inputs(self, context: Dict[str, Any]):
        # Validate required inputs exist
        if 'required_key' not in context:
            raise ValueError("Missing required_key")
    
    def _execute_logic(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Single responsibility logic here
        result = do_something(context['input'])
        return {'output': result}
```

**Automatic Features**:
- ✅ Timing (milliseconds precision)
- ✅ Error handling with StepResult contract
- ✅ Logging (✅/❌ with duration)
- ✅ Input validation before execution

### Pass 1: Load (70 lines, 2 steps)

**Purpose**: Load content from Materials.yaml and validate integrity

| Step | File | Responsibility | Inputs | Outputs |
|------|------|----------------|--------|---------|
| 1.1 | `content_loader.py` | Load from Materials.yaml | material_name, component_type | content |
| 1.2 | `content_validator.py` | Validate not empty/corrupted | content | validated_content |

### Pass 2: Quality Assessment (185 lines, 5 steps)

**Purpose**: Run all quality checks and calculate composite score

| Step | File | Responsibility | Inputs | Outputs |
|------|------|----------------|--------|---------|
| 2.1 | `winston_detector.py` | Winston AI detection | content | ai_score, human_score |
| 2.2 | `realism_evaluator.py` | Grok realism scoring | content | realism_score |
| 2.3 | `readability_checker.py` | Readability validation | content | readability_pass |
| 2.4 | `subjective_checker.py` | Subjective language check | content | subjective_pass |
| 2.5 | `composite_scorer.py` | Composite score calculation | all scores | composite_score (60% Winston + 40% Realism) |

**Winston API Note**: Simplified to Winston-only (no fallback detectors). Fails fast if Winston unavailable.

### Pass 3: Gate Checks (157 lines, 5 steps)

**Purpose**: Enforce quality thresholds

| Step | File | Threshold | Pass Condition |
|------|------|-----------|----------------|
| 3.1 | `winston_gate.py` | AI < 33% (configurable) | Must be below threshold |
| 3.2 | `realism_gate.py` | Score ≥ 7.0 | Must meet minimum |
| 3.3 | `readability_gate.py` | Must pass | Validation successful |
| 3.4 | `subjective_gate.py` | Zero violations | No subjective language |
| 3.5 | `composite_gate.py` | All gates pass | Checks gates 3.1-3.4 |

### Pass 4: Learning (201 lines, 5 steps)

**Purpose**: Calculate parameter adjustments using 7 learning systems

| Step | File | Learning System | Output |
|------|------|-----------------|--------|
| 4.1 | `sweet_spot_retriever.py` | SweetSpotAnalyzer | Historical optimal ranges |
| 4.2 | `temperature_calculator.py` | TemperatureAdvisor | Winston-based temperature |
| 4.3 | `realism_adjuster.py` | RealismOptimizer | Realism failure adjustments |
| 4.4 | `pattern_adjuster.py` | PatternLearner | Learned pattern adjustments |
| 4.5 | `adjustment_merger.py` | Priority merger | Final adjustments |

**Adjustment Priority** (last wins):
1. Sweet spot (lowest priority)
2. Temperature
3. Realism
4. Pattern (highest priority - overrides others)

### Pass 5: Recording (90 lines, 2 steps)

**Purpose**: Update learning databases with results

| Step | File | Responsibility | Updates |
|------|------|----------------|---------|
| 5.1 | `pattern_recorder.py` | Update learned patterns | `prompts/evaluation/learned_patterns.yaml` |
| 5.2 | `database_logger.py` | Log to database | Winston feedback SQLite DB |

### Pass 6: Regeneration (42 lines, 1 step)

**Purpose**: Regenerate content with adjusted parameters

| Step | File | Responsibility | Inputs | Outputs |
|------|------|----------------|--------|---------|
| 6.1 | `content_regenerator.py` | Call SimpleGenerator | adjustments | new_content |

---

## 📋 Result Dataclasses

### ValidationResult
```python
@dataclass
class ValidationResult:
    material_name: str
    component_type: str
    content: str
    quality_results: Optional[QualityResults] = None
    gate_results: Optional[GateResults] = None
    adjustments: Optional[AdjustmentSet] = None
    attempts: int = 1
    success: bool = False
    final_score: float = 0.0
    timing: Dict[str, float] = field(default_factory=dict)
```

### QualityResults
```python
@dataclass
class QualityResults:
    winston_score: float
    realism_score: float
    readability_pass: bool
    subjective_pass: bool
    composite_score: float  # 60% Winston + 40% Realism
```

### GateResults
```python
@dataclass
class GateResults:
    winston_pass: bool
    realism_pass: bool
    readability_pass: bool
    subjective_pass: bool
    all_pass: bool
    failed_gates: List[str]
```

### AdjustmentSet
```python
@dataclass
class AdjustmentSet:
    temperature: Optional[float] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    priority: str = "pattern"  # sweet_spot | temperature | realism | pattern
```

---

## 🔄 Execution Flow

### Happy Path (Content Passes)

```
1. Load content from Materials.yaml
2. Run quality assessment (Winston, Realism, Readability, Subjective)
3. Check gates (all pass ✅)
4. Record results to databases
5. Return success
```

### Retry Path (Content Fails)

```
1. Load content from Materials.yaml
2. Run quality assessment
3. Check gates (some fail ❌)
4. Calculate adjustments (sweet spot, temperature, realism, pattern)
5. Merge adjustments with priority order
6. Regenerate content with adjusted parameters
7. Loop back to step 2 (max 5 attempts)
```

### Example Retry Sequence

```
Attempt 1: Winston 45% (fail) → Temperature adjuster lowers temp from 0.8 to 0.6
Attempt 2: Winston 38% (fail) → Pattern learner adds restraint parameters
Attempt 3: Winston 29% (pass) → Success! Record to databases
```

---

## 🧪 Testing Strategy

### Unit Tests (19 independent tests)

Each step has its own focused unit test:

```python
# tests/test_winston_detector.py
def test_winston_detector_pass():
    mock_client = MockWinstonClient(ai_score=0.25)
    detector = WinstonDetector(mock_client)
    
    result = detector.execute({'content': 'test content'})
    
    assert result.success
    assert result.data['ai_score'] == 0.25
    assert result.duration_ms > 0
```

### Integration Test (1 end-to-end test)

```python
# tests/test_validation_orchestrator.py
def test_complete_validation_workflow():
    orchestrator = ValidationOrchestrator(mock_api, mock_winston, mock_generator)
    
    result = orchestrator.validate_and_improve('Aluminum', 'caption')
    
    assert result['success']
    assert result['attempts'] >= 1
    assert 'final_score' in result
```

---

## 📈 Performance Metrics

### Per-Step Timing

The orchestrator automatically tracks timing for each step:

```
Pass 1 (Load): 12ms
  ├─ 1.1 ContentLoader: 8ms
  └─ 1.2 ContentValidator: 4ms

Pass 2 (Quality): 1,240ms
  ├─ 2.1 WinstonDetector: 850ms
  ├─ 2.2 RealismEvaluator: 320ms
  ├─ 2.3 ReadabilityChecker: 45ms
  ├─ 2.4 SubjectiveChecker: 18ms
  └─ 2.5 CompositeScorer: 7ms

Pass 3 (Gates): 6ms
Pass 4 (Learning): 95ms
Pass 5 (Recording): 42ms
Pass 6 (Regeneration): 2,180ms (if needed)
```

### Bottleneck Identification

With per-step timing, bottlenecks are immediately obvious:
- Winston API: ~850ms (external service)
- Realism evaluation: ~320ms (Grok API)
- Content regeneration: ~2,180ms (DeepSeek/Grok API)

---

## 🔧 Usage

### Basic Usage

```python
from postprocessing.orchestrator import ValidationOrchestrator
from shared.api.client_factory import create_api_client
from generation.core.simple_generator import SimpleGenerator
from postprocessing.detection.ensemble import AIDetectorEnsemble

# Initialize dependencies
api_client = create_api_client('grok')
detector = AIDetectorEnsemble(winston_client=api_client)
generator = SimpleGenerator(api_client)

# Create orchestrator
orchestrator = ValidationOrchestrator(
    api_client=api_client,
    winston_client=detector,
    simple_generator=generator
)

# Run validation
result = orchestrator.validate_and_improve(
    material_name='Aluminum',
    component_type='caption',
    max_attempts=5
)

if result['success']:
    print(f"✅ Validation passed after {result['attempts']} attempts")
    print(f"Final score: {result['final_score']}")
else:
    print(f"❌ Validation failed: {result['reason']}")
```

### Command Line

```bash
# Validate existing content
python3 run.py --validate-content Aluminum caption

# Output shows per-step progress:
# 🔍 VALIDATE & IMPROVE: caption for Aluminum
# ✅ Pass 1: Load (12ms)
# ✅ Pass 2: Quality (1,240ms)
# ❌ Pass 3: Gates failed (Winston: 45% > 33% threshold)
# ✅ Pass 4: Learning (95ms) - Adjusted temperature: 0.8 → 0.6
# ✅ Pass 6: Regeneration (2,180ms)
# [Retry loop continues...]
```

---

## 🏗️ Architecture Benefits

### Maintainability

**Each step is 30-60 lines** → Easy to understand completely in one reading  
**Single responsibility** → Clear what each step does  
**Independent files** → No risk of breaking unrelated code

### Testability

**19 focused unit tests** → Fast, specific test failures  
**Mock individual steps** → No need to mock entire system  
**Test step in isolation** → Verify exact behavior

### Debuggability

**Clear step identification** → "Step 2.3 ReadabilityChecker failed"  
**Per-step timing** → Identify bottlenecks immediately  
**Error isolation** → One step's exception doesn't crash pipeline

### Flexibility

**Replace any step** → Swap implementation without touching coordinator  
**Add new steps** → Insert into pass without refactoring  
**Parallel execution** → Run Pass 2 steps simultaneously (future)  
**Different workflows** → Reorder/skip passes for different use cases

---

## 📚 Related Documentation

- `postprocessing/orchestrator.py` - Main coordinator implementation
- `postprocessing/steps/base_step.py` - Base step framework
- `postprocessing/steps/*/` - Individual step implementations
- `postprocessing/results/` - Result dataclass definitions
- `postprocessing/legacy/validate_and_improve.py` - Old monolithic system (deprecated)
- `docs/02-architecture/GENERATION_PHASE.md` - Single-pass generation architecture
- `.github/copilot-instructions.md` - Core architectural principles

---

## 🔍 Comparison: Old vs New

| Aspect | OLD (Monolithic) | NEW (Ultra-Modular) |
|--------|------------------|---------------------|
| **Files** | 1 file (474 lines) | 22 files (757 lines) |
| **Methods** | 12 methods in 1 class | 19 independent steps |
| **Testability** | 1 integration test | 19 unit tests + 1 integration |
| **Debugging** | Error buried in 474 lines | "Step 2.3 failed" |
| **Timing** | No per-operation timing | Automatic per-step timing |
| **Profiling** | Manual instrumentation | Built-in performance metrics |
| **Modification** | Risk breaking unrelated code | Isolated changes |
| **Understanding** | Read all 474 lines | Read 1 step (30-60 lines) |
| **Bottlenecks** | Unclear where time spent | Exact step timing shown |
| **Parallel Execution** | Not possible | Pass 2 can run in parallel |

---

## 🚀 Future Enhancements

### Phase 1 (Current)
- ✅ Ultra-modular architecture
- ✅ Winston-only detection (simplified)
- ✅ Per-step timing
- ✅ 19 discrete steps

### Phase 2 (Planned)
- ⏳ Parallel execution for Pass 2 quality steps
- ⏳ Step-level caching (skip redundant checks)
- ⏳ Configurable pass orchestration (skip/reorder passes)
- ⏳ Real-time progress streaming (websocket updates)

### Phase 3 (Future)
- ⏳ Machine learning for threshold optimization
- ⏳ A/B testing different step implementations
- ⏳ Auto-scaling based on workload
- ⏳ Distributed execution across multiple machines

---

**Last Updated**: November 19, 2025  
**Status**: ✅ Production Ready  
**Maintainer**: System Architecture Team
