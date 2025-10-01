# Root Folders Cleanup Analysis

**Date**: October 1, 2025
**Total Project Size**: 38MB

## Executive Summary
Analysis of 19 root-level directories identified **7.1MB of cleanup opportunities** (18.7% of project size).

## Cleanup Opportunities

### 🔴 HIGH PRIORITY - Delete Immediately (5.9MB)

#### 1. **htmlcov/** - 5.9MB, 91 files
- **Purpose**: HTML coverage reports from pytest-cov
- **Status**: Generated artifact, not source code
- **Action**: DELETE - Can be regenerated anytime with `pytest --cov`
- **Impact**: 15.5% size reduction

### 🟡 MEDIUM PRIORITY - Review & Clean (1.2MB)

#### 2. **logs/** - 260KB, 11 files
- **Contents**: 
  - `batch_caption_generation_*.json` (4 files, 213KB)
  - `batch_research_progress.json`
  - `frontmatter_regeneration.log`
  - `terminal_errors.json`
  - `quality_history/` subdirectory
  - `validation_reports/` subdirectory
- **Status**: Historical logs from September 2025
- **Action**: REVIEW - Keep recent logs (last 7 days), delete older ones
- **Recommendation**: Delete batch caption logs from Sept 30 and Sept 18

#### 3. **backups/** - 0B, 0 files
- **Status**: Empty directory
- **Action**: DELETE - No content, serves no purpose

#### 4. **stages/** - 228KB, 8 files
- **Contents**: Pipeline stage scripts
  - `stage1_discovery/discover_properties.py`
  - `stage2_standardization/standardize_properties.py`
  - `stage3_research/research_properties.py`
  - `stage4_cross_validation/cross_validate_properties.py`
  - `stage5_quality_assurance/quality_assurance.py`
  - `stage6_production/production_integration.py`
  - `stage7_monitoring/continuous_monitoring.py`
  - `shared/pipeline_utilities.py`
- **Status**: Appears to be an alternative pipeline architecture
- **Action**: REVIEW - Determine if actively used or superseded by current pipeline
- **Question**: Are these scripts used by `run.py` or are they deprecated?

### 🟢 LOW PRIORITY - Keep (30.9MB)

#### Essential Directories (Keep)
1. **content/** - 3.9MB, 604 files - Generated frontmatter content (ESSENTIAL)
2. **data/** - 2.1MB, 4 files - Core data files (ESSENTIAL)
3. **docs/** - 1.6MB, 142 files - Documentation (ESSENTIAL)
4. **tests/** - 1.2MB, 122 files - Test suite (ESSENTIAL)
5. **components/** - 1.0MB, 92 files - Core components (ESSENTIAL)
6. **scripts/** - 1.0MB, 86 files - Utility scripts (ESSENTIAL)
7. **utils/** - 308KB, 31 files - Utility modules (ESSENTIAL)
8. **material_prompting/** - 248KB, 20 files - Prompting system (ESSENTIAL)
9. **schemas/** - 216KB, 15 files - Schema definitions (ESSENTIAL)
10. **api/** - 144KB, 13 files - API clients (ESSENTIAL)
11. **research/** - 116KB, 5 files - Research modules (ESSENTIAL)
12. **config/** - 88KB, 11 files - Configuration files (ESSENTIAL)
13. **generators/** - 64KB, 5 files - Content generators (ESSENTIAL)
14. **cli/** - 64KB, 5 files - CLI interface (ESSENTIAL)
15. **validation/** - 36KB, 2 files - Validation modules (ESSENTIAL)

## Recommended Cleanup Actions

### Immediate Actions (Safe to Execute)
```bash
# 1. Delete HTML coverage reports (regeneratable)
rm -rf htmlcov/

# 2. Delete empty backups directory
rmdir backups/

# 3. Delete old batch caption logs
rm logs/batch_caption_generation_20250930_*.json
rm logs/frontmatter_regeneration.log

# 4. Update .gitignore to exclude these patterns
echo -e "\n# Generated coverage reports\nhtmlcov/\n.coverage\n*.cover\n\n# Log files\nlogs/*.json\nlogs/*.log" >> .gitignore
```

### Actions Requiring Review

#### 1. **stages/** Directory
**Investigation needed**: 
- Are these stage scripts currently used by the main pipeline?
- Check if `run.py` imports or references any stage scripts
- Verify if this is an old/deprecated pipeline architecture

**Command to check usage**:
```bash
grep -r "from stages" . --include="*.py"
grep -r "import stages" . --include="*.py"
```

**Recommendation**: If unused, delete entire `stages/` directory (228KB)

#### 2. **logs/** Retention Policy
**Current state**: Logs from September 2025
**Recommendation**: Implement log rotation policy
- Keep logs from last 7 days
- Archive or delete older logs
- Consider adding logrotate configuration

## Size Impact Summary

| Action | Size Freed | % of Project |
|--------|------------|--------------|
| Delete htmlcov/ | 5.9MB | 15.5% |
| Delete backups/ | 0KB | 0% |
| Clean logs/ | ~213KB | 0.6% |
| Delete stages/ (if unused) | 228KB | 0.6% |
| **TOTAL** | **6.3MB** | **16.6%** |

## Post-Cleanup Project Size
- **Current**: 38MB
- **After Cleanup**: ~31.7MB
- **Reduction**: 6.3MB (16.6%)

## Git Configuration Updates

### Update .gitignore
Add these patterns to prevent future bloat:
```gitignore
# Generated coverage reports
htmlcov/
.coverage
*.cover
.pytest_cache/
*.py[cod]

# Log files
logs/*.json
logs/*.log
*.log

# Test artifacts
.tox/
.nox/
```

## Maintenance Recommendations

### 1. Automated Cleanup
Create a cleanup script: `scripts/cleanup_generated_files.sh`
```bash
#!/bin/bash
# Clean generated coverage reports
rm -rf htmlcov/ .coverage .pytest_cache/

# Clean old logs (older than 7 days)
find logs/ -name "*.json" -mtime +7 -delete
find logs/ -name "*.log" -mtime +7 -delete

echo "✅ Cleanup complete"
```

### 2. Pre-commit Hook
Add to `.git/hooks/pre-commit` to prevent committing generated files:
```bash
#!/bin/bash
if git diff --cached --name-only | grep -q "htmlcov/"; then
    echo "Error: Attempting to commit htmlcov/ directory"
    exit 1
fi
```

### 3. CI/CD Integration
Ensure CI generates coverage reports but doesn't commit them back to repo.

## Directory Health Score

| Directory | Health | Notes |
|-----------|--------|-------|
| api/ | ✅ Healthy | Core functionality |
| backups/ | ⚠️ Empty | Delete |
| cli/ | ✅ Healthy | CLI interface |
| components/ | ✅ Healthy | Core components |
| config/ | ✅ Healthy | Configuration |
| content/ | ✅ Healthy | Generated content (keep) |
| data/ | ✅ Healthy | Core data |
| docs/ | ✅ Healthy | Documentation |
| generators/ | ✅ Healthy | Content generation |
| htmlcov/ | ❌ Bloat | Delete immediately |
| logs/ | ⚠️ Review | Clean old logs |
| material_prompting/ | ✅ Healthy | Prompting system |
| research/ | ✅ Healthy | Research modules |
| schemas/ | ✅ Healthy | Schema definitions |
| scripts/ | ✅ Healthy | Utility scripts |
| stages/ | ⚠️ Review | Verify if used |
| tests/ | ✅ Healthy | Test suite |
| utils/ | ✅ Healthy | Utilities |
| validation/ | ✅ Healthy | Validation |

## Next Steps

1. ✅ Execute immediate cleanup actions (htmlcov/, backups/, old logs)
2. ⏳ Investigate stages/ directory usage
3. ⏳ Implement .gitignore updates
4. ⏳ Create cleanup automation script
5. ⏳ Document log retention policy
6. ⏳ Commit and push cleanup changes

## Questions for Review

1. **stages/ directory**: Is this pipeline architecture currently in use?
2. **logs/ retention**: What's the desired log retention policy?
3. **Coverage reports**: Should htmlcov/ be added to .gitignore permanently?
4. **Backup strategy**: Is the empty backups/ directory needed for future use?
