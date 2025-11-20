# Archived Scripts

**Date**: November 19, 2025  
**Reason**: Duplicate functionality

## Batch Test Scripts

### test_batch_caption.py (3,711 bytes)
**Archived**: November 19, 2025  
**Reason**: Duplicate of `batch_test_runner.py`  
**Functionality**: Batch caption testing  
**Replacement**: Use `batch_test_runner.py` or `batch_caption_test.py`

### test_batch_caption_clean.py (4,496 bytes)
**Archived**: November 19, 2025  
**Reason**: Duplicate of `batch_test_runner.py`  
**Functionality**: Clean batch caption testing  
**Replacement**: Use `batch_test_runner.py` or `batch_caption_test.py`

## Why These Were Archived

**Problem**: Three scripts with similar names performing overlapping batch caption testing:
- `test_batch_caption.py`
- `test_batch_caption_clean.py`
- `batch_test_runner.py`

**Solution**: Keep the most generic (`batch_test_runner.py`) and the most comprehensive (`batch_caption_test.py`). Archive the redundant variants.

**Space Saved**: 8,207 bytes

## Recovery

If you need these scripts, they're preserved here. To restore:
```bash
mv scripts/archive/[script_name] scripts/
```
