# Root Directory Cleanup Guide

## Overview

The `--cleanup-root` command organizes files in the root directory by moving them to appropriate subdirectories based on their type and purpose.

## Usage

```bash
python3 run.py --cleanup-root
```

## What It Does

### Files Moved to `tests/`
- `test_*.py` - Test files with test prefix
- `*_test.py` - Test files with test suffix
- `test.py` - Main test file
- `*verification*.py` - Verification scripts
- `debug_*.py` - Debug scripts

### Files Moved to `scripts/`
- `*_material.py` - Material management scripts
- `update_*.py` - Update utilities
- `*_labels.py` - Label management scripts
- `*enhancement*.py` - Enhancement utilities
- `*.sh` - Shell scripts

### Files Moved to `cleanup/`
- `cleanup_*.py` - Cleanup utilities
- `*cleanup*.py` - Cleanup-related scripts

### Files Moved to `docs/`
- `*.md` files (except README.md which stays in root)

### Files Kept in Root
- `run.py` - Main interface script
- `z_beam_generator.py` - Main generator
- `README.md` - Project documentation

### Files Deleted
- `*.pyc`, `*.pyo` - Python bytecode
- `__pycache__/` - Python cache directories
- `.pytest_cache/` - Pytest cache
- `*.tmp`, `*.temp`, `*~` - Temporary files
- `.DS_Store` - macOS system files
- `cleanup_report.json` - Old reports (regenerated in cleanup/ folder)

## Example Output

```
🧹 ROOT DIRECTORY CLEANUP
==================================================
Organizing root directory files into appropriate subdirectories...
==================================================
   📦 Moved: test.py → tests/test_1.py
   📦 Moved: final_verification.py → tests/final_verification.py
   📦 Moved: remove_material.py → scripts/remove_material.py
   📦 Moved: update_labels.py → scripts/update_labels.py

📊 ROOT CLEANUP SUMMARY
==================================================
📁 tests/ (Test and debug files): 2 files
📁 scripts/ (Utility, maintenance and shell scripts): 2 files
⏭️  Skipped: 1 files
   • README.md (excluded)

🎯 SUMMARY:
   Total actions performed: 4
   ✅ Minor cleanup completed
```

## Safety Features

- **Name Conflict Handling**: If a file already exists in the destination, it adds a numeric suffix
- **Exclusion Lists**: Important files like `run.py`, `z_beam_generator.py`, and `README.md` are never moved
- **Dry-run Reporting**: Shows exactly what will be moved before moving
- **Error Handling**: Continues processing other files if one fails

## Integration with Other Commands

After running `--cleanup-root`, you can:

1. **Verify no issues remain**: `python3 run.py --cleanup-scan`
2. **Generate detailed report**: `python3 run.py --cleanup-report`
3. **Clean generated content**: `python3 run.py --clean`

## File Organization Result

```
z-beam-generator/
├── run.py                    # Main interface (kept)
├── z_beam_generator.py       # Main generator (kept)
├── README.md                 # Documentation (kept)
├── tests/                    # Test files
│   ├── test.py
│   ├── final_verification.py
│   └── ...
├── scripts/                  # Utility scripts
│   ├── remove_material.py
│   ├── update_labels.py
│   ├── update_density_format.sh
│   └── ...
├── docs/                     # Documentation
│   ├── API_SETUP.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   └── ...
└── cleanup/                  # Cleanup utilities
    ├── cleanup_manager.py
    └── ...
```

This organization follows Python project best practices and makes the repository much cleaner and easier to navigate.
