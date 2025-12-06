#!/bin/bash
# Batch research thermal properties for all materials
# Processes materials in groups to show progress

echo "=================================="
echo "BATCH THERMAL PROPERTIES RESEARCH"
echo "=================================="
echo ""
echo "This will research thermal properties for ~151 materials"
echo "Estimated time: 10-15 minutes"
echo "Estimated API cost: ~151 requests × $0.001 = $0.15"
echo ""

# Confirm once at the start
read -p "Continue with batch research? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled"
    exit 1
fi

echo ""
echo "✅ Starting batch research..."
echo "💾 Automatic backup will be created"
echo ""

# Get all materials that need thermal properties
python3 << 'EOFPYTHON'
import yaml
from pathlib import Path

materials_file = Path('data/materials/Materials.yaml')
with open(materials_file, 'r') as f:
    data = yaml.safe_load(f)

materials = data['materials']
target_props = ['thermalConductivity', 'thermalDiffusivity', 'ablationThreshold']

materials_needed = []
for mat_name, mat_data in materials.items():
    mat_props = mat_data.get('materialProperties', {})
    lmi = mat_props.get('laser_material_interaction', {})
    
    missing = []
    for prop in target_props:
        if prop not in lmi or lmi[prop] is None:
            missing.append(prop)
    
    if missing:
        # Escape material names with special characters
        escaped_name = mat_name.replace("'", "'\\''")
        materials_needed.append(escaped_name)

# Print all materials as command-line args
print(' '.join(f'"{m}"' for m in materials_needed))
EOFPYTHON

# Store the materials list
MATERIALS=$(python3 << 'EOFPYTHON'
import yaml
from pathlib import Path

materials_file = Path('data/materials/Materials.yaml')
with open(materials_file, 'r') as f:
    data = yaml.safe_load(f)

materials = data['materials']
target_props = ['thermalConductivity', 'thermalDiffusivity', 'ablationThreshold']

materials_needed = []
for mat_name, mat_data in materials.items():
    mat_props = mat_data.get('materialProperties', {})
    lmi = mat_props.get('laser_material_interaction', {})
    
    missing = []
    for prop in target_props:
        if prop not in lmi or lmi[prop] is None:
            missing.append(prop)
    
    if missing:
        materials_needed.append(mat_name)

# Print all materials as command-line args
print('\n'.join(materials_needed))
EOFPYTHON
)

# Convert to array
readarray -t MATERIALS_ARRAY <<< "$MATERIALS"
TOTAL=${#MATERIALS_ARRAY[@]}

echo "📊 Total materials to process: $TOTAL"
echo ""

# Process all at once (script handles rate limiting internally)
echo "🚀 Starting research for all materials..."
echo ""

# Build command with all material names
CMD="python3 scripts/research_thermal_properties.py"
for material in "${MATERIALS_ARRAY[@]}"; do
    CMD="$CMD \"$material\""
done

# Execute
eval $CMD

EXIT_CODE=$?

echo ""
echo "=================================="
echo "BATCH RESEARCH COMPLETE"
echo "=================================="

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Success! Check Materials.yaml for updated properties"
    echo "💾 Backup created in data/materials/"
else
    echo "⚠️  Process ended with code $EXIT_CODE"
    echo "Check output above for errors"
fi

exit $EXIT_CODE
