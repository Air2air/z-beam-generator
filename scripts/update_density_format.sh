#!/bin/bash

# Update all properties table files to replace "Material" with "Density"
# This script updates the property label from "Material" to "Density"

echo "🔄 Updating properties table files to new format with Density..."
echo "================================================="

# Directory containing the properties table files
PROPS_DIR="content/components/propertiestable"

# Check if directory exists
if [ ! -d "$PROPS_DIR" ]; then
    echo "❌ Error: Directory $PROPS_DIR not found"
    exit 1
fi

# Count total files
TOTAL_FILES=$(find "$PROPS_DIR" -name "*.md" | wc -l)
echo "📊 Found $TOTAL_FILES properties table files to update"

# Update each file
UPDATED_COUNT=0
for file in "$PROPS_DIR"/*.md; do
    if [ -f "$file" ]; then
        # Replace "| Material |" with "| Density |" in the header row
        sed -i '' 's/| Material |/| Density |/g' "$file"
        
        # For now, set density values to "N/A" - these will be populated by the generator in future runs
        # We're only updating the header label here to maintain consistency
        
        UPDATED_COUNT=$((UPDATED_COUNT + 1))
        
        # Show progress every 20 files
        if [ $((UPDATED_COUNT % 20)) -eq 0 ]; then
            echo "✅ Updated $UPDATED_COUNT/$TOTAL_FILES files..."
        fi
    fi
done

echo "================================================="
echo "✅ Successfully updated $UPDATED_COUNT properties table files"
echo "🔧 Changed 'Material' label to 'Density' in all files"
echo "📝 Note: Density values will be populated when materials are regenerated"
echo ""
echo "🧪 Testing with a sample file..."
head -10 "$PROPS_DIR/steel-laser-cleaning.md"
