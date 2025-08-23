# Z-Beam Cleanup System

This directory contains all cleanup-related functionality for the Z-Beam project.

## Files

- **`test_cleanup.py`**: Main cleanup system with comprehensive test suite and CleanupManager class
- **`test_cleanup_new.py`**: Additional/experimental cleanup tests
- **`test_cleanup_old.py`**: Legacy cleanup tests (kept for reference)
- **`__init__.py`**: Package initialization with CleanupManager export

## Features

### CleanupManager Class
The main cleanup orchestrator that provides:

- **Dead File Detection**: Identifies orphaned and unused files
- **Temporary File Cleanup**: Finds `.tmp`, `.bak`, and other temporary files
- **Empty Directory Detection**: Locates empty directories for cleanup
- **Misplaced File Detection**: Finds test files and documentation in wrong locations
- **Dry-run Safety**: All operations default to identification-only mode

### Test Categories
1. **Dead Files**: Orphaned files no longer referenced
2. **Unused Component Files**: Component files not being used
3. **Temporary Files**: Various temporary file patterns
4. **Empty Directories**: Directories with no useful content
5. **Outdated Generated Content**: Old generated files
6. **Broken Symlinks**: Invalid symbolic links
7. **Misplaced Test Files**: Test files in wrong directories
8. **Misplaced Documentation**: Doc files in root that should be in docs/

## Usage

### From Command Line
```bash
# Run cleanup scan (dry-run only)
python3 run.py --cleanup-scan

# Generate detailed cleanup report
python3 run.py --cleanup-report

# Run cleanup tests only
python3 -m tests --cleanup
```

### From Python Code
```python
from cleanup import CleanupManager

# Initialize with dry-run safety
cleanup_manager = CleanupManager(project_root, dry_run=True)

# Run comprehensive scan
results = cleanup_manager.run_cleanup()

# Review results before any action
for category, items in results.items():
    print(f"{category}: {len(items) if isinstance(items, list) else items}")
```

## Safety Features

- **Dry-run Default**: All operations are read-only by default
- **Comprehensive Exclusions**: System files and directories are protected
- **Pattern-based Detection**: Uses safe glob patterns for file identification
- **No Automatic Deletion**: Requires explicit user review and action
- **Detailed Reporting**: Provides full context for all detected items

## Configuration

The cleanup system uses pattern-based configuration for:
- File exclusions (`.git/`, `__pycache__/`, etc.)
- Temporary file patterns (`*.tmp`, `*.bak`, etc.)
- Misplaced file detection
- Documentation file identification

## Integration

The cleanup system is integrated with:
- Main CLI interface (`run.py`)
- Test runner (`tests/__main__.py`)
- Project maintenance workflows

## Safety Note

⚠️ **IMPORTANT**: The cleanup system is designed for identification and reporting only. No files are automatically deleted. All cleanup operations require explicit user review and manual action.
