#!/bin/bash

# Script to update all propertiestable files with new shorter labels

echo "🔄 Updating propertiestable files with new labels..."

# Directory containing the files
DIR="content/components/propertiestable"

# Counter for updated files
count=0

# Loop through all .md files in the propertiestable directory
for file in "$DIR"/*.md; do
    if [ -f "$file" ]; then
        # Use sed to replace the old labels with new ones
        sed -i '' \
            -e 's/| Chemical Formula |/| Formula |/g' \
            -e 's/| Material Symbol |/| Symbol |/g' \
            -e 's/| Material Type |/| Material |/g' \
            -e 's/| Tensile Strength |/| Tensile |/g' \
            -e 's/| Thermal Conductivity |/| Thermal |/g' \
            "$file"
        
        ((count++))
        echo "  ✅ Updated: $(basename "$file")"
    fi
done

echo "📊 Updated $count propertiestable files with new labels"
echo "🎉 All propertiestable files now use shorter, cleaner labels!"
