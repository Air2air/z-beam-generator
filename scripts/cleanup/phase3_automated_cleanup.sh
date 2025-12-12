#!/bin/bash
# Domains Cleanup Script - Phase 3: Automated Cleanup
# Date: December 11, 2025
# Risk: MEDIUM - Creates backups before any deletion

cd "$(dirname "$0")/../.."

echo "🤖 DOMAINS CLEANUP - PHASE 3: AUTOMATED CLEANUP"
echo "==============================================="
echo ""

# Safety check
read -p "⚠️  This will archive potentially unused files. Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Create archive folder
ARCHIVE_DIR="domains/archive/deprecated_dec2025"
mkdir -p "$ARCHIVE_DIR"

echo "📦 Creating backups in: $ARCHIVE_DIR"
echo ""

# Track what we're archiving
ARCHIVED_COUNT=0

# 1. Archive OLD data_loader.py files (if investigation confirms safe)
echo "1️⃣  Archiving OLD data_loader.py files..."
for loader in domains/contaminants/data_loader.py domains/materials/data_loader.py domains/settings/data_loader.py; do
    if [ -f "$loader" ]; then
        # Check if it's imported anywhere (excluding v2 files)
        import_count=$(grep -r "from $(dirname $loader | sed 's|/|\\.|g').data_loader import" --include="*.py" . 2>/dev/null | grep -v "_v2" | wc -l)
        if [ "$import_count" -eq 0 ]; then
            echo "   Moving: $loader"
            mv "$loader" "$ARCHIVE_DIR/"
            ((ARCHIVED_COUNT++))
        else
            echo "   ⚠️  Skipping $loader - still imported ($import_count places)"
        fi
    fi
done
echo ""

# 2. Archive prompt backups
echo "2️⃣  Archiving prompt backups..."
VERBOSE_DIR="domains/materials/image/prompts/shared/generation/original_verbose"
if [ -d "$VERBOSE_DIR" ]; then
    mkdir -p "$ARCHIVE_DIR/prompt_backups"
    mv "$VERBOSE_DIR" "$ARCHIVE_DIR/prompt_backups/"
    echo "   ✅ Archived original_verbose prompts"
    ((ARCHIVED_COUNT+=5))
else
    echo "   ℹ️  No original_verbose folder found"
fi
echo ""

# 3. Handle potentially orphaned files (conservative approach)
echo "3️⃣  Checking orphaned files (conservative)..."
orphaned_candidates=(
    "domains/contaminants/contamination_levels.py"
    "domains/contaminants/generator.py"
    "domains/contaminants/validator.py"
    "domains/materials/coordinator.py"
)

for file in "${orphaned_candidates[@]}"; do
    if [ -f "$file" ]; then
        filename=$(basename "$file" .py)
        # Check if imported anywhere
        import_count=$(grep -r "from.*$filename import\|import.*$filename" --include="*.py" . 2>/dev/null | wc -l)
        if [ "$import_count" -eq 0 ]; then
            echo "   ⚠️  $file appears unused (0 imports)"
            echo "   Manual review recommended before deletion"
            # Don't auto-delete, just report
        else
            echo "   ✅ $file is used ($import_count imports) - keeping"
        fi
    fi
done
echo ""

# 4. Create archive documentation
echo "4️⃣  Creating archive documentation..."
cat > "$ARCHIVE_DIR/README.md" << 'EOF'
# Deprecated Files Archive
**Date**: December 11, 2025  
**Reason**: Files superseded by unified generation pipeline and v2 data loaders

## Archived Files

### OLD Data Loaders
- `data_loader.py` (contaminants) - Replaced by `data_loader_v2.py`
- `data_loader.py` (materials) - Replaced by `data_loader_v2.py`
- `data_loader.py` (settings) - Replaced by `data_loader_v2.py`

### Prompt Backups
- `original_verbose/` - Historical verbose prompt templates

## Restoration

If needed, files can be restored from this archive:
```bash
# Restore a specific file
cp domains/archive/deprecated_dec2025/<file> domains/<destination>/

# Restore all
cp -r domains/archive/deprecated_dec2025/* domains/
```

## Safe to Delete?

This archive can be deleted after confirming system works correctly:
```bash
rm -rf domains/archive/deprecated_dec2025/
```

## Investigation Results

See: output/cleanup_investigation/ for details on what was checked.
EOF

echo "   ✅ Archive documentation created"
echo ""

# 5. Summary
echo "📊 CLEANUP SUMMARY"
echo "=================="
echo ""
echo "Archived files: $ARCHIVED_COUNT"
echo "Archive location: $ARCHIVE_DIR"
echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Next steps:"
echo "  1. Test system: python3 run.py --help"
echo "  2. Run tests: pytest tests/"
echo "  3. If all working, delete archive: rm -rf $ARCHIVE_DIR"
echo ""
echo "Investigation results: output/cleanup_investigation/"
