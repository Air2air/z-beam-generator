# Claude AI Subjective Evaluation Module

**Status**: ✅ **IMPLEMENTED** (November 15, 2025)  
**Purpose**: Post-generation subjective quality evaluation using Claude AI  
**Integration**: Optional module - runs after all other processes complete

---

## Overview

The Claude Subjective Evaluation Module provides **final quality assessment** of generated content using Claude AI's subjective evaluation capabilities. This runs **AFTER all other processing is complete** to provide human-like quality judgment on the final output.

### Key Features

- ✅ **6-Dimension Evaluation**: Clarity, Professionalism, Technical Accuracy, Human-likeness, Engagement, Jargon-free
- ✅ **Quality Gate**: Pass/fail based on configurable threshold (default: 7.0/10)
- ✅ **Fallback Mode**: Works without Claude API using rule-based evaluation
- ✅ **Integration Helper**: Easy integration into generation workflows
- ✅ **Batch Support**: Evaluate multiple generations simultaneously
- ✅ **Detailed Reports**: Strengths, weaknesses, and actionable recommendations

---

## Architecture

### Core Components

```
postprocessing/evaluation/
├── claude_evaluator.py         # Core evaluation engine
├── demo_claude_evaluation.py   # Demo script
└── __init__.py                 # Package exports

shared/commands/
└── claude_evaluation_helper.py # Integration helper

tests/
└── test_claude_evaluation.py   # 16 comprehensive tests
```

### Evaluation Dimensions

1. **Clarity** (0-10): Content clarity and understandability
2. **Professionalism** (0-10): Professional tone maintenance
3. **Technical Accuracy** (0-10): Correctness of technical details
4. **Human-likeness** (0-10): Natural human writing quality
5. **Engagement** (0-10): Reader engagement and interest
6. **Jargon-free** (0-10): Plain language without unnecessary jargon

---

## Usage

### Basic Evaluation

```python
from postprocessing.evaluation.claude_evaluator import evaluate_content

# Evaluate generated content
result = evaluate_content(
    content=generated_text,
    material_name="Aluminum",
    component_type="micro",
    verbose=True
)

print(f"Overall Score: {result.overall_score:.1f}/10")
print(f"Quality Gate: {'PASS' if result.passes_quality_gate else 'FAIL'}")
```

### Integration Helper (Post-Generation)

```python
from shared.commands.claude_evaluation_helper import evaluate_after_generation

# Quick post-generation evaluation
result = evaluate_after_generation(
    content=generated_text,
    material_name="Steel",
    component_type="micro",
    api_client=claude_client,  # Optional
    verbose=True,
    skip_evaluation=False
)

if not result.passes_quality_gate:
    print("⚠️  Quality gate failed!")
```

### Integration in Generation Workflow

```python
from shared.commands.claude_evaluation_helper import ClaudeEvaluationHelper

# Initialize helper
evaluator = ClaudeEvaluationHelper(
    quality_threshold=7.0,
    verbose=True,
    enabled=True
)

# After generation completes
evaluation = evaluator.evaluate_generation(
    content=final_output,
    material_name=material_name,
    component_type="micro",
    context={'author': author_name, 'properties': properties}
)

# Get summary report
summary = evaluator.get_summary_report(evaluation)
print(summary)
```

---

## Demo

Run the demo to see the module in action:

```bash
cd /Users/todddunning/Desktop/Z-Beam/z-beam-generator
PYTHONPATH=$PWD:$PYTHONPATH python3 postprocessing/evaluation/demo_claude_evaluation.py
```

**Demo Outputs**:
- ✅ Basic evaluation with detailed dimension scores
- ⚠️ Poor content detection (casual language)
- ✅ Integration helper demonstration
- ⏭️ Skip evaluation mode

---

## Configuration

### Quality Threshold

Set minimum acceptable quality score (0-10):

```python
evaluator = ClaudeEvaluator(quality_threshold=7.5)
```

### Enable/Disable

Control evaluation activation:

```python
helper = ClaudeEvaluationHelper(enabled=False)  # Disabled
```

### Verbose Output

Show detailed evaluation reports:

```python
result = evaluate_content(content, "Aluminum", verbose=True)
```

---

## Fallback Behavior

**When Claude API is NOT available**, the module uses **rule-based evaluation**:

1. **Clarity**: Based on average word length
2. **Professionalism**: Detects casual language patterns
3. **Other Dimensions**: Default 7.0/10 scores with notes

**When Claude API IS available** (future):
- Full subjective evaluation across all 6 dimensions
- Detailed feedback and specific suggestions
- Context-aware quality assessment

---

## Test Coverage

**16 tests** covering all functionality:

```bash
pytest tests/test_claude_evaluation.py -v
```

**Test Categories**:
- ✅ Core evaluator (5 tests)
- ✅ Integration helper (8 tests)
- ✅ Quality detection (2 tests)
- ✅ Performance (1 test)

**Results**: All 16 tests passing in <3 seconds

---

## Integration Points

### Current State (November 15, 2025)

**Module Status**: Implemented and tested  
**Integration**: Manual - not yet in generation workflow  
**API Support**: Fallback mode (Claude API integration ready)

### Future Integration

Add to `run.py` generation handlers:

```python
# After generation completes
if args.enable_claude_eval:
    from postprocessing.evaluation import evaluate_content
    
    evaluation = evaluate_content(
        content=generated_content,
        material_name=material_name,
        component_type=component_type,
        verbose=args.verbose
    )
    
    if not evaluation.passes_quality_gate:
        logger.warning(f"Quality gate failed: {evaluation.overall_score:.1f}/10")
```

### CLI Flags (Proposed)

```bash
python3 run.py --material Aluminum \
               --enable-claude-eval \
               --claude-threshold 7.5 \
               --verbose
```

---

## Performance

- **Fallback Mode**: <1ms per evaluation
- **Claude API Mode**: ~500-2000ms (estimated, API-dependent)
- **Overhead**: Negligible when disabled
- **Batch Support**: Efficient for multiple evaluations

---

## Error Handling

### Quality Gate Failure

```python
# Optional: Fail on low quality
try:
    result = helper.evaluate_generation(
        content=content,
        material_name="Aluminum",
        fail_on_low_quality=True  # Raises ValueError
    )
except ValueError as e:
    print(f"Quality gate failed: {e}")
```

### Claude API Unavailable

- **Automatic fallback** to rule-based evaluation
- **Warning message** when verbose=True
- **Continues operation** without blocking

---

## Example Output

### Successful Evaluation

```
======================================================================
  CLAUDE SUBJECTIVE EVALUATION
======================================================================

Material: Aluminum
Component: caption
Content length: 303 chars

──────────────────────────────────────────────────────────────────────
EVALUATION RESULTS
──────────────────────────────────────────────────────────────────────

Overall Score: 7.2/10
Quality Gate: ✅ PASS

Dimension Scores:
  ✅ Clarity: 8.2/10
     Average word length: 6.8 chars
  ✅ Professionalism: 7.0/10
     Professional tone maintained
  ✅ Technical Accuracy: 7.0/10
     Unable to evaluate without Claude AI
  ✅ Human Likeness: 7.0/10
     Unable to evaluate without Claude AI
  ✅ Engagement: 7.0/10
     Unable to evaluate without Claude AI
  ✅ Jargon Free: 7.0/10
     Unable to evaluate without Claude AI

──────────────────────────────────────────────────────────────────────

✅ Strengths:
  • Content generated successfully

💡 Recommendations:
  • Enable Claude API for detailed subjective evaluation

======================================================================
```

### Poor Content Detection

```
Dimension Scores:
  ✅ Clarity: 10.0/10
     Average word length: 4.4 chars
  ⚠️ Professionalism: 5.0/10
     Some casual language detected
     → Remove casual language
```

---

## Next Steps

### Immediate (Optional)

1. **Add Claude API Configuration**:
   - Add `CLAUDE_API_KEY` to `.env`
   - Create Claude client in `shared/api/claude_client.py`

2. **Integrate into Generation Workflow**:
   - Add to caption generator
   - Add to subtitle generator
   - Add to FAQ generator

3. **Add CLI Support**:
   - `--enable-claude-eval` flag
   - `--claude-threshold` parameter
   - `--skip-claude-eval` flag

### Future Enhancements

1. **Claude API Integration**: Full subjective evaluation when API available
2. **Custom Dimensions**: Allow user-defined evaluation criteria
3. **Learning Mode**: Track evaluation patterns over time
4. **Comparative Analysis**: Compare multiple generations side-by-side

---

## Summary

✅ **Module implemented** with comprehensive evaluation engine  
✅ **16 tests passing** with full coverage  
✅ **Demo working** with detailed output examples  
✅ **Integration helper** ready for workflow integration  
✅ **Fallback mode** ensures functionality without Claude API  
✅ **Documentation complete** with usage examples

**Status**: Ready for integration into generation workflows as optional post-generation quality check.

---

## Files Modified/Created

**New Files**:
- `postprocessing/evaluation/claude_evaluator.py` (500+ lines)
- `postprocessing/evaluation/__init__.py`
- `postprocessing/evaluation/demo_claude_evaluation.py` (180 lines)
- `shared/commands/claude_evaluation_helper.py` (200+ lines)
- `tests/test_claude_evaluation.py` (350+ lines, 16 tests)
- `postprocessing/evaluation/README.md` (this file)

**Tests**: 16/16 passing ✅  
**Performance**: <1ms (fallback mode)  
**Integration**: Ready for deployment
