# Removed Code Archive - November 18, 2025

## Files Removed

### 1. processing/unified_orchestrator.py (1,120 lines)
**Reason**: Dead code - only referenced in test files, never used in production

**Original Purpose**: Attempted consolidation of orchestrator.py and generator.py into single unified generator

**Why Removed**: 
- No production code imports or uses UnifiedOrchestrator
- Only 8 test files referenced it
- Consolidation effort was never completed/adopted
- System successfully uses two separate generators:
  * `orchestrator.py` for subtitle generation
  * `generator.py` (DynamicGenerator) for caption/FAQ generation via UnifiedMaterialsGenerator wrapper

**Verification**: Full production path trace confirmed zero production usage

### 2. shared/generators/dynamic_generator.py (~50 lines)
**Reason**: Redundant alias - production code imports directly from processing.generator

**Original Purpose**: Convenience wrapper/alias for processing.generator.DynamicGenerator

**Why Removed**:
- Production code imports directly: `from processing.generator import DynamicGenerator`
- Alias layer provides no value
- No production references found

## Removal Impact

**Lines Removed**: 1,170 lines total
**Production Code Changed**: 0 (no production dependencies)
**Test Files to Update**: 8 test files (optional - can be archived)

## Final Architecture

**Two Active Generators**:

1. **processing/orchestrator.py** (682 lines)
   - Purpose: Winston-integrated content generator
   - Used By: Subtitle generation (--subtitle command)
   - Path: `run.py → shared/commands/generation.py → Orchestrator`

2. **processing/generator.py** (1,202 lines)  
   - Purpose: Dynamic content generator with learning
   - Used By: Caption + FAQ generation (--caption, --faq commands)
   - Path: `run.py → shared/commands/generation.py → UnifiedMaterialsGenerator → DynamicGenerator`

## Rollback Instructions

If issues arise, restore files:

```bash
cd /Users/todddunning/Desktop/Z-Beam/z-beam-generator
cp docs/archive/removed_code/nov18_2025/unified_orchestrator.py processing/
cp docs/archive/removed_code/nov18_2025/dynamic_generator.py shared/generators/
```

Or via git:
```bash
git revert <commit-hash>
```

## Verification Commands

```bash
# Run test suite
pytest tests/

# Run integrity check
python3 processing/integrity/integrity_checker.py

# Test all component types
python3 run.py --caption "Steel"
python3 run.py --subtitle "Aluminum"
python3 run.py --faq "Bamboo"
```

## Related Documents

- **Phase 1 Analysis**: `PHASE1_VERIFICATION_COMPLETE_NOV18_2025.md`
- **Original Evaluation**: `E2E_BLOAT_EVALUATION_NOV18_2025.md`
- **Production Path Traces**: See Phase 1 document, sections "PATH 1", "PATH 2", "PATH 3"

## Date Removed

November 18, 2025

## Removed By

AI Assistant (with user approval after Phase 1 verification)
