# Comprehensive Cleanup Plan

## Phase 1: Archive Consolidation ✅

### Move to Single Archive Location
```bash
# Consolidate all archives into .archive/
mv backups .archive/backups_20251024
mv audit_reports .archive/audit_reports_20251024
mv voice/archive .archive/voice_docs_20251024
mv scripts/.archive .archive/scripts_20251024

# Move old logs
mkdir -p .archive/logs_20251024
mv research_*.log .archive/logs_20251024/
mv caption_batch_output.log .archive/logs_20251024/
mv caption_batch_log.txt .archive/logs_20251024/

# Keep only essential logs
touch research_progress.log  # Current working log
```

## Phase 2: Documentation Consolidation 📚

### Current Issues
- 131 markdown files in docs/
- Duplicate/overlapping content
- No clear hierarchy

### Proposed Structure
```
docs/
├── README.md                  # Main entry point
├── ARCHITECTURE.md            # System architecture
├── GETTING_STARTED.md         # Quick start guide
├── api/                       # API documentation
├── components/                # Component-specific docs
│   ├── caption/
│   ├── frontmatter/
│   └── voice/
├── development/               # Dev guides
│   ├── TESTING.md
│   ├── CONTRIBUTING.md
│   └── TROUBLESHOOTING.md
└── reference/                 # Technical reference
    ├── DATA_ARCHITECTURE.md
    ├── VALIDATION_STRATEGY.md
    └── ERROR_HANDLING.md
```

## Phase 3: Test Consolidation 🧪

### Move Component Tests
```bash
# Ensure all component tests are in proper locations
components/caption/tests/
components/frontmatter/tests/
components/voice/tests/
```

## Phase 4: Dead Code Removal ❌

### Files to Remove
- Old batch scripts (already in .archive/scripts/)
- Duplicate voice documentation (keep only active files)
- Temporary research logs (move to archive)

## Phase 5: Active Files ✅

### Keep in Root
- run.py (main entry point)
- requirements.txt
- pytest.ini
- Makefile
- README.md
- QUICK_COMMANDS_REFERENCE.md
- prod_config.yaml

### Keep batch_generate_captions.py?
- Currently in root, should move to scripts/batch/ or archive

## Execution Order

1. **Archive consolidation** (safe, reversible)
2. **Documentation audit** (identify duplicates)
3. **Documentation restructure** (consolidate)
4. **Test consolidation** (move to proper locations)
5. **Dead code removal** (final cleanup)
6. **Git commit** (checkpoint)

## Size Impact
- Current: ~5MB in archives/backups
- After: All in .archive/, single location
- Reduction: Cleaner root, easier navigation
