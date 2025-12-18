# Additional Normalization Opportunities Analysis
**Date**: December 11, 2025  
**Status**: Analysis In Progress  
**Context**: Post-author normalization analysis

---

## 🎯 Summary

Beyond author object normalization, the codebase has several additional areas requiring standardization:

---

## 🔍 NORMALIZATION OPPORTUNITY #1: Configuration File Patterns

### Current State
- 356 YAML files across the project
- Mixed purposes: data, config, frontmatter, schemas
- No consistent naming convention
- Some use `config.yaml`, others use `data.yaml`, `settings.yaml`

### Issue
```
generation/config.yaml        # Generation configuration
domains/materials/config.yaml # Domain configuration
domains/contaminants/data.yaml # Domain data (should be config.yaml)
data/materials/Materials.yaml  # Actual data
data/settings/Settings.yaml    # Actual data
```

### Recommendation
**Establish file naming convention**:
- **`config.yaml`**: Configuration/settings for code behavior
- **`data.yaml`**: Static reference data for domain
- **`{Entity}.yaml`**: Actual entity data (Materials.yaml, Contaminants.yaml, Settings.yaml)
- **`{entity}-schema.yaml`**: JSON schemas for validation

### Action
1. Rename `domains/contaminants/data.yaml` → `domains/contaminants/config.yaml` (if it's configuration)
2. Create naming policy document
3. Audit all 356 YAML files for naming consistency

---

## 🔍 NORMALIZATION OPPORTUNITY #2: Domain Structure Consistency

### Current State Analysis Needed
Check if all domains follow same structure:
```
domains/
├── materials/
│   ├── config.yaml
│   ├── coordinator.py
│   ├── data_loader.py
│   ├── generator.py
│   ├── prompts/
│   └── modules/
├── contaminants/
│   ├── data.yaml  ← Different name
│   ├── generator.py
│   ├── data_loader.py     ✅ NORMALIZED (was pattern_loader.py)
│   └── prompts/
└── settings/
    ├── config.yaml
    ├── coordinator.py
    ├── data_loader.py
    └── modules/
```

### Issues
1. **✅ FIXED: File naming normalized**: All domains now use `data_loader.py`
2. **Missing files**: Contaminants domain missing `coordinator.py`
3. **Config naming**: `data.yaml` vs `config.yaml`

### Recommendation
**Establish mandatory domain structure**:
```
domains/{domain}/
├── config.yaml          # Domain configuration (REQUIRED)
├── coordinator.py       # Domain orchestration (REQUIRED)
├── data_loader.py       # Data loading utilities (REQUIRED)
├── generator.py         # Frontmatter generator (REQUIRED)
├── prompts/             # Domain prompt templates (REQUIRED)
│   ├── description.txt
│   ├── micro.txt
│   └── faq.txt
└── modules/             # Optional modular components
    ├── metadata_module.py
    └── properties_module.py
```

### Action
1. ✅ DONE: Renamed `contaminants/pattern_loader.py` → `contaminants/data_loader.py`
2. Rename `contaminants/data.yaml` → `contaminants/config.yaml`
3. Create `contaminants/coordinator.py` (if needed)
4. Document mandatory structure in `docs/02-architecture/DOMAIN_STRUCTURE_POLICY.md`

---

## 🔍 NORMALIZATION OPPORTUNITY #3: Import Statement Patterns

### Current State
```python
# Multiple ways to import from data layer
from data.authors.registry import get_author
from data.materials.data_loader import MaterialsDataLoader
import yaml  # Direct YAML loading
```

### Issue
- Some domains use dedicated data loaders
- Others load YAML directly
- Inconsistent abstraction levels

### Recommendation
**Standardize data access patterns**:
```python
# ✅ CORRECT: Use domain data loaders
from domains.materials.data_loader import MaterialsDataLoader
from domains.contaminants.data_loader import ContaminantsDataLoader
from domains.settings.data_loader import SettingsDataLoader

# ✅ CORRECT: Use registry for cross-cutting concerns
from data.authors.registry import resolve_author_for_generation

# ❌ WRONG: Direct YAML loading in domain code
import yaml
with open('data/materials/Materials.yaml') as f:
    data = yaml.safe_load(f)
```

### Action
1. Create abstract `BaseDataLoader` class
2. Ensure all domains use loader pattern
3. Add policy: "NO direct YAML loading in domain code"
4. Enforcement: Grep search for `yaml.safe_load` in domains/

---

## 🔍 NORMALIZATION OPPORTUNITY #4: Error Handling Patterns

### Investigation Needed
Check consistency of exception types across domains:
```python
# Do all domains use same exceptions?
raise ConfigurationError(...)
raise GenerationError(...)  
raise MaterialDataError(...)
```

### Check
```bash
grep -r "raise " domains/ --include="*.py" | cut -d: -f2 | \
  grep -oE "raise [A-Z][a-zA-Z]*" | sort | uniq -c | sort -rn
```

### Expected Standardization
- All domains should use same exception types
- Defined in `shared/validation/errors.py`
- No custom exception types per domain

---

## 🔍 NORMALIZATION OPPORTUNITY #5: Component Type Discovery

### Current State
Already normalized in recent work:
- ✅ Components discovered from `prompts/*.txt` files
- ✅ No hardcoded component lists in code
- ✅ Generic processing code

### Verification
Check if ALL domains follow this pattern or if any still have hardcoded components.

---

## 🔍 NORMALIZATION OPPORTUNITY #6: Frontmatter Structure

### Investigation Needed
Check if all frontmatter exports follow same structure:
```yaml
# Do ALL domains export these fields consistently?
layout: {type}
title: ...
author:
  id: N
  name: ...
  [14 total fields]
_metadata:
  generator: ...
  version: ...
  content_type: ...
```

### Check
```bash
# Sample frontmatter from each domain
head -50 frontmatter/materials/*.yaml | head -30
head -50 frontmatter/contaminants/*.yaml | head -30
head -50 frontmatter/settings/*.yaml | head -30
```

### Expected Standardization
- All frontmatter files have same metadata fields
- Author object structure identical (14 fields)
- _metadata structure consistent

---

## 🔍 NORMALIZATION OPPORTUNITY #7: Logging Patterns

### Investigation Needed
Check logging consistency:
```python
# Are loggers initialized consistently?
logger = logging.getLogger(__name__)  # Correct pattern

# Or mixed patterns?
logger = logging.getLogger('domain.module')
self.logger = logging.getLogger(...)
```

### Check
```bash
grep -r "logging.getLogger" --include="*.py" | \
  grep -oE "getLogger\([^)]+\)" | sort | uniq -c | sort -rn
```

### Expected Standardization
- All files use `logger = logging.getLogger(__name__)`
- No hardcoded logger names
- Consistent log level usage (INFO, DEBUG, ERROR, WARNING)

---

## 🔍 NORMALIZATION OPPORTUNITY #8: API Client Initialization

### Current State
Multiple patterns for API client creation:
```python
# Pattern 1: Direct instantiation
from shared.api.deepseek import DeepSeekClient
client = DeepSeekClient(api_key=..., model=..., base_url=..., timeout=...)

# Pattern 2: Factory function
from shared.api.deepseek import create_deepseek_client
client = create_deepseek_client(api_key=..., model=..., ...)

# Pattern 3: From config
client = create_deepseek_client(**config)
```

### Recommendation
**Standardize to single pattern**:
```python
# ✅ CORRECT: Factory function with explicit parameters
from shared.api.deepseek import create_deepseek_client
import os

client = create_deepseek_client(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    model='deepseek-chat',
    base_url='https://api.deepseek.com/v1',
    timeout=120
)
```

### Action
1. Document recommended pattern in `docs/07-api/CLIENT_INITIALIZATION.md`
2. Update all scripts to use factory function
3. Deprecate direct DeepSeekClient() instantiation

---

## 🔍 NORMALIZATION OPPORTUNITY #9: Test File Naming

### Current State
Mixed naming conventions:
```
test_contaminant_authors.py
test_contaminant_generation.py
test_contaminant_simple.py
test_contaminant_bash.sh
tests/test_*.py
```

### Issue
- Root directory has test files (should be in tests/)
- Mixed naming: `test_*.py` vs `*_test.py`
- Shell scripts mixed with Python tests

### Recommendation
**Standardize test organization**:
```
tests/
├── unit/
│   ├── test_author_normalization.py
│   ├── test_data_loader.py
│   └── test_generators.py
├── integration/
│   ├── test_4author_generation.py
│   └── test_frontmatter_export.py
└── fixtures/
    └── test_data.yaml

# Root directory: NO test files (only run.py, setup.py, etc.)
```

### Action
1. Move all test_*.py from root to tests/
2. Organize by type (unit, integration, e2e)
3. Move shell scripts to scripts/testing/
4. Document in `docs/08-development/TESTING_POLICY.md`

---

## 🔍 NORMALIZATION OPPORTUNITY #10: Prompt Template Format

### Investigation Needed
Check if all prompt templates use consistent format:
```
domains/materials/prompts/description.txt
domains/materials/prompts/micro.txt
domains/contaminants/prompts/description.txt
shared/prompts/personas/*.yaml
```

### Questions
1. Do all domains have same component types?
2. Are prompt template formats identical?
3. Do they all use same placeholder variables?

### Check
```bash
# List all prompt files
find domains/ -name "*.txt" -path "*/prompts/*"

# Check placeholder consistency
grep -h "{" domains/*/prompts/*.txt | sort | uniq
```

### Expected Standardization
- All domains have same core components (description, micro, faq)
- Domain-specific components documented
- Placeholder variables standardized ({material_name}, {voice_instruction}, etc.)

---

## 📊 Priority Ranking

### 🔴 HIGH PRIORITY (Do Now)
1. **Domain Structure** (#2) - Affects architecture
2. **Import Patterns** (#3) - Affects maintainability
3. **Frontmatter Structure** (#6) - User-facing consistency

### 🟡 MEDIUM PRIORITY (Do Soon)
4. **Configuration Naming** (#1) - 356 files, low risk
5. **API Client Init** (#8) - Frequently used pattern
6. **Test Organization** (#9) - Clean root directory

### 🟢 LOW PRIORITY (Do Eventually)
7. **Error Handling** (#4) - Already mostly standardized
8. **Logging Patterns** (#7) - Internal consistency
9. **Prompt Templates** (#10) - Already working well
10. **Component Discovery** (#5) - Already normalized

---

## 🚀 Recommended Next Steps

1. **Complete author normalization** (current task)
2. **Domain structure audit** - Create DOMAIN_STRUCTURE_POLICY.md
3. **Rename inconsistent files**:
   - ✅ `contaminants/data_loader.py` (normalized from pattern_loader.py)
   - `contaminants/data.yaml` → `config.yaml`
4. **Move test files** from root to tests/
5. **Document import patterns** in architecture docs

---

## 📚 New Policy Documents Needed

1. `docs/02-architecture/DOMAIN_STRUCTURE_POLICY.md`
2. `docs/08-development/FILE_NAMING_CONVENTIONS.md`
3. `docs/08-development/IMPORT_PATTERNS_POLICY.md`
4. `docs/08-development/TESTING_POLICY.md`
5. `docs/07-api/CLIENT_INITIALIZATION.md`

---

**Status**: ⏸️ Analysis Complete - Awaiting user priorities  
**Next Action**: User selects which normalizations to implement  
**Estimated Time**: Each normalization ~30-60 minutes
