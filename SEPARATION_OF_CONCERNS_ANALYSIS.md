# Separation of Concerns Analysis: /data vs /domains

**Date**: November 25, 2025  
**Issue**: Mixed concerns between data storage (/data) and domain logic (/domains)

---

## 🎯 Correct Architecture Pattern

### `/data` - Pure Data Storage
**Purpose**: YAML files only - source of truth for static data
**Should contain**:
- ✅ YAML configuration files
- ✅ Database files (SQLite, etc.)
- ✅ Data backups/archives
- ✅ README documentation
**Should NOT contain**:
- ❌ Python code (.py files)
- ❌ Data loaders
- ❌ Business logic
- ❌ Research modules

### `/domains` - Business Logic & Processing
**Purpose**: Domain-specific code that operates on data
**Should contain**:
- ✅ Python modules (.py files)
- ✅ Data loaders (read YAML from /data)
- ✅ Research services
- ✅ Validation logic
- ✅ Utilities and helpers
- ✅ Schema definitions

---

## 🔍 Current Violations

### ❌ `/data/materials` - Contains Python Code

**Problem**: Has 3 Python files that should be in `/domains/materials`

1. **`/data/materials/loader.py` (1054 lines)**
   - Purpose: Loads and merges YAML files
   - Should be: `/domains/materials/data_loader.py`
   - Used by: 9 files across codebase
   - Dependencies: imports from domains/materials

2. **`/data/materials/materials.py` (370 lines)**
   - Purpose: Cached materials loader with O(1) lookups
   - Should be: `/domains/materials/materials_cache.py`
   - Used by: Research modules, validators
   - Dependencies: imports from data.materials.loader

3. **`/data/materials/__init__.py` (minimal)**
   - Purpose: Makes directory a Python package
   - Should be: Removed (not needed for pure data)

**Impact**: 1,424 lines of code in wrong location

---

## 📊 Current Structure Comparison

### `/data/materials` (CURRENT - MIXED)
```
data/materials/
├── Materials.yaml           ✅ DATA (correct)
├── Categories.yaml          ✅ DATA (correct)
├── MaterialProperties.yaml  ✅ DATA (correct)
├── Settings.yaml           ✅ DATA (correct)
├── PropertyDefinitions.yaml ✅ DATA (correct)
├── loader.py               ❌ CODE (wrong location)
├── materials.py            ❌ CODE (wrong location)
├── __init__.py             ❌ CODE (wrong location)
├── research/               ✅ DATA (AI research notes - correct)
│   ├── metals/
│   ├── stone/
│   ├── wood/
│   └── other/
├── content/                ✅ DATA (generated content - correct)
│   ├── Captions.yaml
│   ├── FAQs.yaml
│   └── RegulatoryStandards.yaml
├── categories/             ✅ DATA (category data - correct)
│   └── property_system.yaml
├── archive/                ✅ DATA (backups - correct)
└── backups/                ✅ DATA (backups - correct)
```

### `/domains/materials` (CURRENT - CORRECT)
```
domains/materials/
├── category_loader.py      ✅ CODE (correct)
├── coordinator.py          ✅ CODE (correct)
├── schema.py              ✅ CODE (correct)
├── research/              ✅ CODE (correct)
│   ├── base.py
│   ├── factory.py
│   ├── category_range_researcher.py
│   ├── machine_settings_researcher.py
│   └── services/
├── utils/                 ✅ CODE (correct)
│   ├── property_helpers.py
│   ├── category_property_cache.py
│   └── unit_extractor.py
├── validation/            ✅ CODE (correct)
├── image/                 ✅ CODE (correct)
└── modules/               ✅ CODE (correct)
```

---

## ✅ Proposed Cleanup Plan

### Phase 1: Move Python Code from /data to /domains

#### 1.1 Move `loader.py` → `/domains/materials/data_loader.py`
```bash
# Move file
mv data/materials/loader.py domains/materials/data_loader.py

# Update 9 import statements:
# OLD: from data.materials.loader import ...
# NEW: from domains.materials.data_loader import ...
```

**Files to update**:
- export/core/trivial_exporter.py (2 imports)
- scripts/validation/fail_fast_materials_validator.py (1 import)
- shared/commands/global_evaluation.py (1 import)
- shared/commands/deployment.py (1 import)
- scripts/research/populate_deep_research.py (1 import)
- domains/materials/category_loader.py (1 import)
- domains/materials/coordinator.py (1 import)
- domains/materials/research/category_range_researcher.py (1 import)

#### 1.2 Move `materials.py` → `/domains/materials/materials_cache.py`
```bash
# Move file
mv data/materials/materials.py domains/materials/materials_cache.py

# Update imports (check usage first)
```

**Files to check**:
- Any file importing `from data.materials.materials import ...`
- Update to: `from domains.materials.materials_cache import ...`

#### 1.3 Remove `/data/materials/__init__.py`
```bash
rm data/materials/__init__.py
rm -rf data/materials/__pycache__
```

### Phase 2: Verify Data-Only Structure

After cleanup, `/data/materials` should contain ONLY:
```
data/materials/
├── Materials.yaml              # ✅ Core material metadata
├── Categories.yaml             # ✅ Category taxonomy
├── CategoryTaxonomy.yaml       # ✅ Category structure
├── MaterialProperties.yaml     # ✅ Properties data
├── Settings.yaml              # ✅ Machine settings
├── PropertyDefinitions.yaml    # ✅ Property definitions
├── ParameterDefinitions.yaml   # ✅ Parameter definitions
├── RegulatoryStandards.yaml   # ✅ Standards data
├── MachineSettings.yaml       # ✅ Legacy settings
├── IndustryApplications.yaml  # ✅ Industry metadata
├── PropertyResearch.yaml      # ✅ Research tracking
├── SettingResearch.yaml       # ✅ Research tracking
├── frontmatter_template.yaml  # ✅ Template
├── research/                  # ✅ AI research notes (no .py)
├── content/                   # ✅ Generated content YAMLs
├── categories/                # ✅ Category data
├── archive/                   # ✅ Archived files
├── backups/                   # ✅ Backup files
├── README.md                  # ✅ Documentation
├── BACKUP_RETENTION_POLICY.md # ✅ Documentation
└── REGULATORY_STANDARDS_ARCHITECTURE.md # ✅ Documentation
```

### Phase 3: Update Documentation

1. Update `/data/materials/README.md`:
   - Remove references to loader.py
   - Add note: "Python code moved to /domains/materials"
   - Document data-only architecture

2. Update `/domains/materials/README.md`:
   - Document new data_loader.py location
   - Document materials_cache.py location
   - Update import examples

---

## 🔧 Implementation Steps

### Step 1: Pre-Change Verification
```bash
# Count current Python files in data/materials
find data/materials -name "*.py" | wc -l
# Expected: 3 files (loader.py, materials.py, __init__.py)

# Find all imports to update
grep -r "from data.materials.loader import" --include="*.py" | wc -l
grep -r "from data.materials.materials import" --include="*.py" | wc -l
grep -r "from data.materials import" --include="*.py" | wc -l
```

### Step 2: Execute Move (with backup)
```bash
# Create backup
cp data/materials/loader.py data/materials/loader.py.backup
cp data/materials/materials.py data/materials/materials.py.backup

# Move files
mv data/materials/loader.py domains/materials/data_loader.py
mv data/materials/materials.py domains/materials/materials_cache.py

# Update internal imports in moved files
# loader.py imports nothing from data.materials
# materials.py imports from data.materials.loader → update to domains.materials.data_loader
```

### Step 3: Update Import Statements (All Files)

**Tool-assisted approach**:
```python
# Script to update imports
import os
import re

def update_imports(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Update imports
    content = content.replace(
        'from data.materials.loader import',
        'from domains.materials.data_loader import'
    )
    content = content.replace(
        'from data.materials.materials import',
        'from domains.materials.materials_cache import'
    )
    content = content.replace(
        'from data.materials import load_materials_data',
        'from domains.materials.data_loader import load_materials_data'
    )
    
    with open(file_path, 'w') as f:
        f.write(content)

# Apply to all Python files
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.py'):
            update_imports(os.path.join(root, file))
```

### Step 4: Update Internal References

**In `domains/materials/data_loader.py`**:
- No changes needed (doesn't import from data.materials)

**In `domains/materials/materials_cache.py`**:
```python
# OLD:
from data.materials.loader import load_materials_data

# NEW:
from domains.materials.data_loader import load_materials_data
```

### Step 5: Remove Python Package Infrastructure
```bash
rm data/materials/__init__.py
rm -rf data/materials/__pycache__
```

### Step 6: Verify No Python Code in /data
```bash
# Should return 0
find data/materials -name "*.py" | wc -l

# Should return ONLY .yaml, .md, and directories
ls -la data/materials/
```

### Step 7: Test System
```bash
# Run test suite
python3 run.py --test

# Test specific functionality
python3 -c "from domains.materials.data_loader import load_materials_data; data = load_materials_data(); print(f'Loaded {len(data.get(\"materials\", {}))} materials')"

# Test cached loader
python3 -c "from domains.materials.materials_cache import get_material_by_name_cached; steel = get_material_by_name_cached('Steel'); print(f'Steel category: {steel.get(\"category\")}')"
```

---

## 📈 Expected Results

### Before Cleanup
- `/data/materials`: 3 Python files (1,424 lines of code)
- Mixed concerns: data + code in same directory
- Confusing import paths: `from data.materials.loader`

### After Cleanup
- `/data/materials`: 0 Python files (pure data)
- Clear separation: data storage only
- Logical imports: `from domains.materials.data_loader`
- Better maintainability
- Follows standard Python project structure

---

## ⚠️ Risk Assessment

### Low Risk
- **File moves**: Simple rename/move operations
- **Import updates**: Mechanical find-replace
- **No logic changes**: Code remains identical

### Mitigation
- ✅ Create backups before moving
- ✅ Use tool-assisted import updates
- ✅ Test after each phase
- ✅ Can rollback easily (backups exist)

### Testing Strategy
1. Unit tests (existing test suite)
2. Integration tests (material loading)
3. Import verification (no broken imports)
4. Functionality verification (run.py commands)

---

## 🎯 Success Criteria

- [ ] Zero Python files in `/data/materials`
- [ ] All imports updated successfully
- [ ] All tests passing
- [ ] System functionality verified
- [ ] Documentation updated
- [ ] No broken imports detected

---

## 📚 Additional Cleanup Opportunities

### Other domains to review:
1. `/data/contaminants` - Check for Python code (should be in `/domains/contaminants`)
2. `/data/regions` - Check for Python code (should be in `/domains/regions`)
3. `/data/applications` - Check for Python code (should be in `/domains/applications`)
4. `/data/thesaurus` - Check for Python code (should be in `/domains/thesaurus`)

### Pattern to follow:
- **`/data/{domain}/`** = YAML files only
- **`/domains/{domain}/`** = Python code that operates on data

---

## 💡 Long-Term Architecture

### Ideal Structure
```
z-beam-generator/
├── data/               # PURE DATA STORAGE
│   ├── materials/     # ✅ YAML only
│   ├── contaminants/  # ✅ YAML only
│   ├── regions/       # ✅ YAML only
│   ├── applications/  # ✅ YAML only
│   └── thesaurus/     # ✅ YAML only
│
├── domains/           # BUSINESS LOGIC
│   ├── materials/     # ✅ Python code
│   ├── contaminants/  # ✅ Python code
│   ├── regions/       # ✅ Python code
│   ├── applications/  # ✅ Python code
│   └── thesaurus/     # ✅ Python code
│
├── shared/            # SHARED UTILITIES
├── generation/        # CONTENT GENERATION
├── export/            # FRONTMATTER EXPORT
└── scripts/           # CLI TOOLS
```

### Benefits
- **Clear ownership**: Data vs logic separation
- **Better maintainability**: Know where to find things
- **Testability**: Mock data layer easily
- **Scalability**: Add new domains cleanly
- **Standard structure**: Follows Python conventions

---

## 🚀 Recommendation

**Execute cleanup in 3 phases**:
1. **Phase 1 (Today)**: Move Python files from /data/materials to /domains/materials
2. **Phase 2 (Today)**: Update all imports and test
3. **Phase 3 (Future)**: Apply same pattern to other domains

**Time estimate**: 1-2 hours for complete cleanup + testing

**Risk level**: LOW (simple moves + mechanical updates)

**Impact**: HIGH (cleaner architecture, better maintainability)

