# Archived Legacy Code

**Date**: November 19, 2025  
**Reason**: Superseded by modern architecture

## generator.py (1,474 lines)

**Original Location**: `generation/core/legacy/generator.py`  
**Archived**: November 19, 2025  
**Reason**: Superseded by FrontmatterOrchestrator + SimpleGenerator

### What It Was
- `DynamicGenerator`: Monolithic generator with generation + validation + retry + learning
- Combined all concerns in single 1,474-line class
- Used by `--material` command via non-existent `generate_component()` method (broken)

### Why It Was Removed
1. **Modern architecture** separates concerns:
   - **Generation**: `SimpleGenerator` (single-pass, no validation)
   - **Validation**: `ValidationOrchestrator` (ultra-modular, 19 steps)
   - **Export**: `FrontmatterOrchestrator` (multi-domain coordinator)
2. **Non-functional**: Called `generate_component()` method that didn't exist
3. **Monolithic**: Mixed generation + validation + retry logic (anti-pattern)
4. **Duplicate**: SimpleGenerator + ValidationOrchestrator handle this better

### Replacement Flow

**Old Way** (broken):
```python
generator = DynamicGenerator()
result = generator.generate_component(...)  # Method doesn't exist!
```

**New Way** (working):
```python
# For content generation
from domains.materials.coordinator import UnifiedMaterialsGenerator
generator = UnifiedMaterialsGenerator(api_client)
content = generator.generate(material_name, 'caption')

# For validation
from postprocessing.orchestrator import ValidationOrchestrator
orchestrator = ValidationOrchestrator(...)
result = orchestrator.validate_and_improve(content, ...)

# For frontmatter export
from export.core.orchestrator import FrontmatterOrchestrator
orchestrator = FrontmatterOrchestrator(api_client)
result = orchestrator.generate('material', material_name)
```

### Commands Affected
- `--material "Aluminum"`: Now uses FrontmatterOrchestrator (no longer broken)
- `--caption "Aluminum"`: Already using UnifiedMaterialsGenerator ✅
- `--material-description "Aluminum"`: Already using UnifiedMaterialsGenerator ✅
- `--faq "Aluminum"`: Already using UnifiedMaterialsGenerator ✅

### Cleanup Statistics
- **Code removed**: 1,474 lines (DynamicGenerator)
- **Total cleanup (Nov 19)**: 2,098 lines removed (474 validation + 150 fallbacks + 1,474 generator)
- **Architecture**: Ultra-modular (19-step validation, clean separation of concerns)
