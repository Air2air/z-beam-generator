# Recovery System Organization

The validation and recovery system has been organized into a dedicated `recovery/` package for better maintainability and modularity.

## Package Structure

```
recovery/
├── __init__.py              # Package exports and version info
├── validator.py             # Content validation and quality scoring
├── recovery_runner.py       # Direct component recovery system
├── recovery_system.py       # Main recovery coordination system
└── cli.py                   # Command-line interface module
```

## Legacy Compatibility Scripts

For backward compatibility, several legacy scripts are provided in the project root:

```
validate_legacy.py          # Compatible with old validate.py interface
direct_recovery_legacy.py   # Compatible with old direct_recovery.py interface
recovery_cli.py             # New CLI entry point
```

## Usage

### New Module Interface (Recommended)

```bash
# Validate materials using the new module system
python3 -m recovery.cli validate "Tempered Glass"

# Scan all materials
python3 -m recovery.cli validate --scan-all

# Auto-recover failures
python3 -m recovery.cli validate --scan-all --auto-recover

# Recover specific components
python3 -m recovery.cli recover "Tempered Glass" --components frontmatter metatags
```

### Legacy Interface (Backward Compatible)

```bash
# Old validate.py interface still works
python3 validate_legacy.py "Tempered Glass"
python3 validate_legacy.py --recover

# Old direct_recovery.py interface still works  
python3 direct_recovery_legacy.py "Tempered Glass" --components frontmatter
```

### Programmatic Interface

```python
# Import from the recovery package
from recovery import MaterialRecoverySystem, DirectRecoveryRunner
from recovery.validator import ContentValidator

# Use the classes directly
recovery_system = MaterialRecoverySystem()
reports = recovery_system.scan_materials()

# Direct recovery
runner = DirectRecoveryRunner()
results = runner.recover_components("Subject", ["frontmatter", "metatags"])
```

## Module Responsibilities

### `validator.py`
- Content quality analysis and scoring
- Component-specific validation rules
- File existence and structure checking
- Issue identification and categorization

### `recovery_runner.py`  
- Direct generator invocation without run.py
- Component configuration management
- Retry logic and error handling
- Output path management

### `recovery_system.py`
- High-level recovery coordination
- Material scanning and discovery
- Validation report generation
- Recovery command generation

### `cli.py`
- Command-line interface implementation
- Argument parsing and validation
- User-friendly output formatting
- Integration between validation and recovery

## Benefits of Organization

1. **Modularity** - Each component has a clear, focused responsibility
2. **Testability** - Individual modules can be tested in isolation
3. **Maintainability** - Changes to one aspect don't affect others
4. **Reusability** - Components can be imported and used independently
5. **Extensibility** - New validation rules or recovery methods can be added easily
6. **Compatibility** - Legacy interfaces ensure existing workflows continue to work

## Migration Guide

### From Old Scripts to New Module

**Old Way:**
```bash
python3 validate.py "Subject"
python3 direct_recovery.py "Subject" --components frontmatter
```

**New Way:**
```bash
python3 -m recovery.cli validate "Subject"
python3 -m recovery.cli recover "Subject" --components frontmatter
```

**Programmatic Migration:**
```python
# Old imports (if you had them)
from recovery_system import MaterialRecoverySystem
from direct_recovery import DirectRecoveryRunner

# New imports  
from recovery import MaterialRecoverySystem, DirectRecoveryRunner
from recovery.validator import ContentValidator
```

### Advantages of New Interface

1. **Namespace Protection** - All recovery functionality is under the `recovery` namespace
2. **Import Clarity** - Clear separation between validation, recovery, and CLI components
3. **Package Management** - Easier to manage dependencies and versions
4. **Documentation** - Better organization for API documentation
5. **Testing** - Easier to write comprehensive unit tests

The new organization maintains full backward compatibility while providing a more professional and maintainable codebase structure.
