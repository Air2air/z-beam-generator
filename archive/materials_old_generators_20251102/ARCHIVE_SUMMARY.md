# Materials Generator Consolidation - Archive

**Date**: November 2, 2025
**Reason**: Replaced by UnifiedMaterialsGenerator

## What Was Archived

This archive contains the old separate generator classes that have been replaced by a single unified generator:

### Old Generators (1,202 lines total)
- `caption/` - CaptionComponentGenerator (384 lines)
- `faq/` - FAQComponentGenerator (489 lines)  
- `subtitle/` - SubtitleComponentGenerator (329 lines)
- `modules_backup_20251102_154049/` - Previous backup

### New Unified Approach (479 lines total)
- `materials/unified_generator.py` (379 lines)
- `materials/prompts/caption.txt` (28 lines)
- `materials/prompts/faq.txt` (52 lines)
- `materials/prompts/subtitle.txt` (20 lines)

## Code Reduction
**Net Savings**: 723 lines removed (60% reduction)

## Benefits of Unified Generator
1. ✅ **No Code Duplication** - Shared API client, validation, error handling
2. ✅ **Visible Prompts** - Edit .txt files instead of Python code
3. ✅ **Same Data Structures** - Backward compatible with existing pipeline
4. ✅ **Voice Compatible** - Works seamlessly with VoicePostProcessor
5. ✅ **Easier Maintenance** - Single class for all material content types

## Integration Status
- ✅ Wired into `run.py` via `shared/commands/generation.py`
- ✅ Tested with Bronze material (caption, subtitle, FAQ)
- ✅ Voice post-processing works identically
- ✅ All three content types generate correct data structures

## Commands Still Work
```bash
python3 run.py --caption "MaterialName"
python3 run.py --subtitle "MaterialName"
python3 run.py --faq "MaterialName"
```

## Recovery
If needed, these old generators can be restored from this archive, but the unified generator is the recommended approach going forward.
