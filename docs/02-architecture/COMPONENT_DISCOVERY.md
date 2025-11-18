# Dynamic Component Discovery Architecture

**Date**: November 16, 2025  
**Status**: Implemented  
**Policy**: ZERO hardcoded component types in `/processing` system

---

## Core Principle

**Components are defined ONLY in two places:**
1. **`prompts/{component}.txt`** - Content instructions and generation guidelines
2. **`processing/config.yaml`** - Component lengths and structural configuration

**The `/processing` system discovers components dynamically at runtime.**

---

## Architecture

### Component Discovery Flow

```
1. Application requests component (e.g., "caption")
   ↓
2. ComponentRegistry._discover_components()
   ↓
3. Scans prompts/*.txt files
   ↓
4. For each .txt file (excluding system prompts):
   - Component type = filename without .txt
   - Prompt file = prompts/{filename}.txt
   ↓
5. Loads lengths from config.yaml
   ↓
6. Returns ComponentSpec with:
   - name: from filename
   - lengths: from config.yaml
   - prompt_file: from discovery
   - punctuation: from config or default
```

### File Structure

```
z-beam-generator/
├── prompts/
│   ├── caption.txt          # Defines 'caption' component
│   ├── subtitle.txt         # Defines 'subtitle' component  
│   ├── description.txt      # Defines 'description' component
│   ├── faq.txt              # Defines 'faq' component
│   └── {custom}.txt         # Add any new component here
│
├── processing/
│   ├── config.yaml          # Component lengths only
│   │   component_lengths:
│   │     caption: 25
│   │     subtitle: 15
│   │     description: 150
│   │
│   └── generation/
│       └── component_specs.py  # NO hardcoded components!
│
└── tests/
    └── e2e/
        └── test_processing_pipeline.py  # Validates discovery
```

---

## Adding New Components

### Step 1: Create Prompt File

Create `prompts/{component_name}.txt`:

```txt
You are generating a {component_name} for laser cleaning materials.

[Content instructions here - focus, format, style, examples]

TARGET: {target_length} words
```

### Step 2: Add Length Configuration

Add to `processing/config.yaml`:

```yaml
component_lengths:
  {component_name}: 50  # default word count
```

### Step 3: Done!

The component is now available system-wide:
```python
from processing.generation.component_specs import ComponentRegistry

spec = ComponentRegistry.get_spec('my_new_component')
# Automatically discovered, no code changes needed!
```

---

## Testing Requirements

### Test 1: Component Discovery

```python
def test_component_discovery_from_prompts():
    """Verify components discovered from prompts/ directory"""
    types = ComponentRegistry.list_types()
    
    # Count prompt files
    prompts_dir = Path('prompts')
    prompt_files = [
        f.stem for f in prompts_dir.glob('*.txt')
        if not f.stem.startswith('_')
    ]
    
    assert len(types) == len(prompt_files)
```

### Test 2: No Hardcoded Components

```python
def test_no_hardcoded_components():
    """Verify no hardcoded component types in /processing"""
    
    # Search for hardcoded component names
    processing_files = Path('processing').rglob('*.py')
    
    for file in processing_files:
        content = file.read_text()
        
        # Should NOT find hardcoded component strings like:
        # if component_type == 'caption':
        # SPEC_DEFINITIONS = {'caption': ...}
        
        assert 'caption' not in content or is_allowed_usage(content)
```

### Test 3: Prompt Files Exist

```python
def test_prompt_files_exist():
    """Every discovered component must have prompt file"""
    types = ComponentRegistry.list_types()
    
    for component_type in types:
        spec = ComponentRegistry.get_spec(component_type)
        prompt_file = Path(spec.prompt_template_file)
        assert prompt_file.exists()
```

---

## Documentation Requirements

### For Developers

**When adding features to `/processing`:**

1. ✅ **DO**: Use `component_type` as a parameter/variable
2. ✅ **DO**: Iterate over `ComponentRegistry.list_types()`
3. ✅ **DO**: Load component specs dynamically
4. ❌ **DON'T**: Hardcode component names (`'caption'`, `'subtitle'`, etc.)
5. ❌ **DON'T**: Create if/else chains for specific components
6. ❌ **DON'T**: Store component specs in Python code

**Example - Wrong:**
```python
# ❌ WRONG - Hardcoded component
if component_type == 'caption':
    length = 25
elif component_type == 'subtitle':
    length = 15
```

**Example - Right:**
```python
# ✅ RIGHT - Dynamic discovery
spec = ComponentRegistry.get_spec(component_type)
length = spec.default_length
```

### For Content Creators

**When creating new content types:**

1. Create `prompts/{name}.txt` with content instructions
2. Add `{name}: {length}` to `config.yaml` component_lengths
3. Test with `python3 run.py --{name} "MaterialName"`

No code changes needed!

---

## Migration Checklist

If you find hardcoded components in `/processing`, fix them:

- [ ] Remove `SPEC_DEFINITIONS` dictionary
- [ ] Replace with `_discover_components()` method
- [ ] Update docstrings to remove component examples
- [ ] Change `'caption'` references to `component_type` variable
- [ ] Update tests to verify dynamic discovery
- [ ] Add test for "no hardcoded components"
- [ ] Document in `COMPONENT_DISCOVERY.md`

---

## Benefits

1. **Extensibility**: Add new components without code changes
2. **Maintainability**: Single source of truth (prompts/ and config.yaml)
3. **Testability**: Can verify no hardcoding via automated tests
4. **Clarity**: Clear separation between content (prompts) and structure (processing)
5. **Flexibility**: Different projects can have different components

---

## Enforcement

### Automated Tests

Run test suite to verify compliance:
```bash
pytest tests/e2e/test_processing_pipeline.py::TestComponentRegistry -v
```

### Code Review Checklist

Before merging PRs touching `/processing`:
- [ ] No hardcoded component names in new code
- [ ] Uses `ComponentRegistry.list_types()` for iteration
- [ ] Uses `ComponentRegistry.get_spec()` for component info
- [ ] Updated tests pass
- [ ] Documentation updated if needed

---

## See Also

- `processing/generation/component_specs.py` - Implementation
- `tests/e2e/test_processing_pipeline.py` - Test suite
- `docs/proposals/GENERIC_LEARNING_ARCHITECTURE.md` - Related generic design
- `.github/copilot-instructions.md` - AI coding guidelines
