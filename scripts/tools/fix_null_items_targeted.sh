#!/bin/bash
#
# Fix Null/Empty Relationship Items - Targeted Approach
# Removes items with {id: null} and empty items arrays from source data
#
# Usage:
#   ./fix_null_items_targeted.sh --dry-run   # Preview changes
#   ./fix_null_items_targeted.sh             # Apply fixes
#

cd /Users/todddunning/Desktop/Z-Beam/z-beam-generator

DRY_RUN=false
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
fi

echo "================================================================================"
echo "FIX NULL/EMPTY RELATIONSHIP ITEMS - Targeted Approach"
echo "================================================================================"
if [ "$DRY_RUN" = true ]; then
    echo "🔍 DRY RUN MODE - No changes will be saved"
else
    echo "⚠️  LIVE MODE - Changes will be applied to source files"
fi
echo ""

# Function to remove null items from a file
fix_null_items() {
    local file="$1"
    local basename=$(basename "$file")
    
    # Pattern 1: Remove items with only null id and presentation
    # Match:  - id: null\n    presentation: card
    if grep -q "id: null" "$file"; then
        echo "  Processing: $basename"
        
        if [ "$DRY_RUN" = true ]; then
            echo "    Would remove null id items"
        else
            # Use perl for multiline replacement
            perl -i -pe '
                BEGIN { $/ = undef; }
                s/      - id: null\n        presentation: card\n//g;
                s/      - id: null\n        presentation: cardCompact\n//g;
                s/      - id: null\n//g;
            ' "$file"
            echo "    ✅ Removed null id items"
        fi
    fi
    
    # Pattern 2: Remove empty items arrays
    # Match: items: []
    if grep -q "items: \[\]" "$file"; then
        if [ "$DRY_RUN" = true ]; then
            echo "    Would remove empty items arrays"
        else
            sed -i '' 's/      items: \[\]$//' "$file"
            echo "    ✅ Removed empty items arrays"
        fi
    fi
    
    # Pattern 3: Remove standalone items: [] lines
    if grep -q "^      items:$" "$file"; then
        # Check if next line is empty or different field
        if [ "$DRY_RUN" = true ]; then
            echo "    Would remove standalone empty items"
        else
            perl -i -pe '
                BEGIN { $/ = undef; }
                s/      items:\n      (      )/      $1/g;
            ' "$file"
            echo "    ✅ Cleaned standalone empty items"
        fi
    fi
}

# Process each source data file
echo "📄 Processing Materials.yaml..."
fix_null_items "data/materials/Materials.yaml"

echo ""
echo "📄 Processing Contaminants.yaml..."
fix_null_items "data/contaminants/Contaminants.yaml"

echo ""
echo "📄 Processing Settings.yaml..."
fix_null_items "data/settings/Settings.yaml"

echo ""
echo "📄 Processing Compounds.yaml..."
fix_null_items "data/compounds/Compounds.yaml"

echo ""
echo "================================================================================"
if [ "$DRY_RUN" = true ]; then
    echo "✅ DRY RUN COMPLETE - No files were modified"
    echo ""
    echo "To apply these changes, run:"
    echo "  ./scripts/tools/fix_null_items_targeted.sh"
else
    echo "✅ FIXES APPLIED"
    echo ""
    echo "Next steps:"
    echo "  1. Re-export all domains:"
    echo "     python3 run.py --export --domain materials"
    echo "     python3 run.py --export --domain contaminants"
    echo "     python3 run.py --export --domain settings"
    echo "     python3 run.py --export --domain compounds"
    echo ""
    echo "  2. Verify fixes with null scan script"
fi
echo "================================================================================"
