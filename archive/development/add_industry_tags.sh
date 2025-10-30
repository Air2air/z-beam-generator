#!/bin/bash
# Script to add industryTags to Phase 1A materials in Materials.yaml

cd /Users/todddunning/Desktop/Z-Beam/z-beam-generator

echo "================================================================================"
echo "ADDING INDUSTRY TAGS TO PHASE 1A MATERIALS"
echo "================================================================================"
echo ""

# Backup
cp data/Materials.yaml data/Materials.yaml.backup_before_tags
echo "✅ Backup created: data/Materials.yaml.backup_before_tags"
echo ""

# Add Titanium to material_index
echo "1️⃣  Adding Titanium to material_index..."
sed -i.tmp1 '/^  Tin: metal$/a\
  Titanium: metal' data/Materials.yaml
echo "✅ Added Titanium to material_index"
echo ""

# Function to add industryTags to a material
add_industry_tags() {
    local material="$1"
    local line_num="$2"
    shift 2
    local tags=("$@")
    
    echo "Adding industryTags to $material at line ~$line_num..."
    
    # Create temporary file with the industryTags
    cat > /tmp/industry_tags_$material.txt << 'TAGEND'
    material_metadata:
      industryTags:
TAGEND
    
    # Add each tag
    for tag in "${tags[@]}"; do
        echo "      - $tag" >> /tmp/industry_tags_$material.txt
    done
    
    # Find the last property line for this material (before next material starts)
    # Insert the material_metadata section before the next material
    local next_line=$((line_num + 200))  # Search window
    local insert_line=$(awk -v start="$line_num" -v end="$next_line" '
        NR > start && NR < end {
            # Look for the end of the current material (next material or end of properties)
            if (/^  [A-Z]/ && NR > start + 10) {
                print NR-1
                exit
            }
        }
    ' data/Materials.yaml)
    
    if [ -n "$insert_line" ]; then
        sed -i.tmp2 "${insert_line} r /tmp/industry_tags_$material.txt" data/Materials.yaml
        echo "✅ Added industryTags to $material"
    else
        echo "⚠️  Could not find insertion point for $material"
    fi
}

echo "2️⃣  Adding industryTags to materials..."
echo ""

# Aluminum (9 tags)
add_industry_tags "Aluminum" 7282 \
    "Aerospace" "Automotive" "Construction" "Electronics Manufacturing" \
    "Food and Beverage Processing" "Marine" "Packaging" "Rail Transport" \
    "Renewable Energy"

# Steel (6 tags)
add_industry_tags "Steel" 12331 \
    "Automotive" "Construction" "Manufacturing" "Oil & Gas" \
    "Rail Transport" "Shipbuilding"

# Copper (8 tags)
add_industry_tags "Copper" 8565 \
    "Architecture" "Electronics Manufacturing" "HVAC Systems" "Marine" \
    "Plumbing" "Power Generation" "Renewable Energy" "Telecommunications"

# Brass (6 tags)
add_industry_tags "Brass" 8009 \
    "Architecture" "Hardware Manufacturing" "Marine" "Musical Instruments" \
    "Plumbing" "Valves and Fittings"

# Bronze (6 tags)
add_industry_tags "Bronze" 8198 \
    "Architecture" "Art and Sculpture" "Bearings" "Marine" \
    "Memorial and Monument" "Musical Instruments"

# Nickel (6 tags)
add_industry_tags "Nickel" 10717 \
    "Aerospace" "Chemical Processing" "Electronics Manufacturing" \
    "Energy Storage" "Medical Devices" "Oil & Gas"

# Zinc (5 tags)
add_industry_tags "Zinc" 13419 \
    "Automotive" "Construction" "Die Casting" "Galvanizing" \
    "Hardware Manufacturing"

# Clean up temp files
rm -f /tmp/industry_tags_*.txt
rm -f data/Materials.yaml.tmp1 data/Materials.yaml.tmp2

echo ""
echo "================================================================================"
echo "✅ UPDATE COMPLETE"
echo "================================================================================"
echo ""
echo "Verifying..."
python3 -c "
from data.materials import load_materials
m = load_materials()
print(f'Total materials: {len(m[\"materials\"])}')
print(f'Titanium exists: {\"Titanium\" in m[\"materials\"]}')
tags_count = sum(1 for mat in m['materials'].values() 
                 if isinstance(mat, dict) and 
                 mat.get('material_metadata', {}).get('industryTags'))
print(f'Materials with industryTags: {tags_count}')
"
