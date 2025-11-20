# Legacy Generator Code

**Created**: November 19, 2025  
**Status**: Archived but functional  
**Reason**: Architectural simplification

## What's Here

### `generator.py` (DynamicGenerator)
The original unified generator that combined:
- Content generation
- Quality validation (Winston AI, Realism, Readability, Subjective)
- Retry loops with parameter adjustment
- Learning system integration
- Direct writing to Materials.yaml

**Size**: ~1,461 lines  
**Complexity**: High (280+ lines of retry/validation logic)

## Why It Was Replaced

### The Problem
Mixing generation and validation in one class violated single responsibility:
- Generation concerns (API calls, prompt building) mixed with validation concerns (quality checks, retry logic)
- Hard to test individual components
- Retry loops scattered throughout generation code
- Documentation drift (docs said "single-pass" but code had complex retry loops)

### The Solution (November 19, 2025)
Split into two focused modules:

1. **SimpleGenerator** (`generation/core/simple_generator.py`)
   - ONE API call per material
   - NO validation loops
   - NO retry logic
   - Clean, focused: ~287 lines

2. **ValidationAndImprovementPipeline** (`postprocessing/validate_and_improve.py`)
   - All 7 learning systems
   - All quality gates (Winston, Realism, Readability, Subjective)
   - Retry loops with parameter adjustment
   - Learning database logging
   - Focused: ~395 lines

**Result**: 280 lines of scattered complexity → Two clean, testable modules

## Where It's Still Used

### `run.py` - Legacy --material Command
The old `--material` command still uses DynamicGenerator for backward compatibility:

```python
# LEGACY: Using DynamicGenerator for backward compatibility with --material command
# New commands use SimpleGenerator (see --caption, --subtitle, --faq)
from generation.core.legacy.generator import DynamicGenerator
generator = DynamicGenerator()
```

### Test/Validation Scripts
Some validation scripts still reference DynamicGenerator:
- `scripts/validate_dual_objective.py` - Tests learning system integration

## Migration Path

### If You Need to Use Old Behavior
```python
from generation.core.legacy.generator import DynamicGenerator

generator = DynamicGenerator(api_client)
result = generator.generate(material_name, component_type)
# Returns dict with: success, content, ai_score, human_score, attempts, etc.
```

### Recommended: New Architecture
```python
# Step 1: Generate (single-pass)
from generation.core.simple_generator import SimpleGenerator

generator = SimpleGenerator(api_client)
result = generator.generate(material_name, component_type)
# Returns dict with: content, length, word_count, saved, temperature

# Step 2: Validate & Improve (post-processing)
from postprocessing.validate_and_improve import ValidationAndImprovementPipeline

pipeline = ValidationAndImprovementPipeline(api_client)
validation_result = pipeline.validate_and_improve(material_name, component_type)
# Returns dict with: success, final_score, attempts, logged, reason
```

## Future

This code may be removed entirely once:
1. The --material command is migrated to use SimpleGenerator
2. All validation scripts are updated
3. No dependencies remain in the codebase

For now, it's preserved for reference and backward compatibility.

## Related Documentation

- `docs/02-architecture/GENERATION_PHASE.md` - New single-pass generation architecture
- `docs/02-architecture/VALIDATION_STAGE.md` - Post-processing validation (TODO)
- `.github/copilot-instructions.md` - Core architectural principles
