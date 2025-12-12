#!/bin/bash
# Domains Cleanup Script - Phase 2: Investigation
# Date: December 11, 2025
# Risk: LOW - Investigation only, no deletions

cd "$(dirname "$0")/../.."

echo "🔍 DOMAINS CLEANUP - PHASE 2: INVESTIGATION"
echo "==========================================="
echo ""

OUTPUT_DIR="output/cleanup_investigation"
mkdir -p "$OUTPUT_DIR"

# 1. Check OLD data_loader imports
echo "1️⃣  Checking OLD data_loader.py imports..."
grep -r "from domains\\..*\\.data_loader import" --include="*.py" . 2>/dev/null | \
    grep -v "_v2" > "$OUTPUT_DIR/old_loader_imports.txt"

import_count=$(wc -l < "$OUTPUT_DIR/old_loader_imports.txt" | tr -d ' ')
echo "   Found: $import_count imports to OLD loaders"
if [ "$import_count" -gt 0 ]; then
    echo "   ⚠️  Review: $OUTPUT_DIR/old_loader_imports.txt"
else
    echo "   ✅ No OLD loader imports found - safe to delete OLD versions"
fi
echo ""

# 2. Check orphaned file imports
echo "2️⃣  Checking potentially orphaned files..."
orphaned_files=(
    "contamination_levels"
    "generator"
    "validator"
    "coordinator"
    "pattern_loader"
    "library"
)

echo "" > "$OUTPUT_DIR/orphaned_file_imports.txt"
for file in "${orphaned_files[@]}"; do
    echo "Checking: $file" >> "$OUTPUT_DIR/orphaned_file_imports.txt"
    grep -r "from domains.*$file import\|import domains.*$file" --include="*.py" . 2>/dev/null >> "$OUTPUT_DIR/orphaned_file_imports.txt" || echo "  No imports found" >> "$OUTPUT_DIR/orphaned_file_imports.txt"
    echo "" >> "$OUTPUT_DIR/orphaned_file_imports.txt"
done

echo "   Results saved to: $OUTPUT_DIR/orphaned_file_imports.txt"
echo ""

# 3. Check material_description.txt in contaminants
echo "3️⃣  Checking misplaced prompt template..."
if [ -f "domains/contaminants/prompts/material_description.txt" ]; then
    grep -r "material_description" domains/contaminants/ --include="*.py" > "$OUTPUT_DIR/material_description_usage.txt" 2>/dev/null
    usage_count=$(wc -l < "$OUTPUT_DIR/material_description_usage.txt" | tr -d ' ')
    if [ "$usage_count" -eq 0 ]; then
        echo "   ⚠️  material_description.txt found in contaminants but not used"
        echo "   Consider: Moving to materials domain or renaming"
    else
        echo "   ✅ material_description.txt is used in contaminants"
    fi
else
    echo "   ℹ️  No material_description.txt in contaminants"
fi
echo ""

# 4. Summary
echo "📊 INVESTIGATION SUMMARY"
echo "========================"
echo ""
echo "Results saved to: $OUTPUT_DIR/"
echo ""
echo "Review files:"
echo "  - old_loader_imports.txt"
echo "  - orphaned_file_imports.txt"
echo "  - material_description_usage.txt"
echo ""
echo "Next steps:"
echo "  1. Review investigation results"
echo "  2. Run phase3_cleanup_script.sh for automated cleanup"
echo "  or manually deprecate files as needed"
