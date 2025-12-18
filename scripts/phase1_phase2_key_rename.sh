#!/bin/bash
# Phase 1 + 2: Fix camelCase keys AND remove redundant prefixes

echo "🔄 Phase 1 + 2: Renaming keys for consistency and clarity..."
echo ""

# Phase 1 + 2 Combined (camelCase → snake_case AND remove redundant prefixes)
echo "📝 Materials.yaml changes:"
echo "   materialCharacteristics → characteristics"
echo "   materialProperties → properties"
echo "   material_metadata → metadata"
echo "   material_description → description"
echo "   regulatoryStandards → regulatory_standards"
echo ""

echo "📝 Settings.yaml changes:"
echo "   machineSettings → machine_settings"
echo "   material_challenges → challenges"
echo ""

# Python files
find . -type f -name "*.py" ! -path "./venv/*" ! -path "./.git/*" ! -path "./__pycache__/*" -exec sed -i '' \
  -e "s/materialCharacteristics/characteristics/g" \
  -e "s/materialProperties/properties/g" \
  -e "s/material_metadata/metadata/g" \
  -e "s/material_description/description/g" \
  -e "s/regulatoryStandards/regulatory_standards/g" \
  -e "s/machineSettings/machine_settings/g" \
  -e "s/material_challenges/challenges/g" \
  {} \;

# YAML files
find . -type f -name "*.yaml" ! -path "./venv/*" ! -path "./.git/*" -exec sed -i '' \
  -e "s/materialCharacteristics/characteristics/g" \
  -e "s/materialProperties/properties/g" \
  -e "s/material_metadata/metadata/g" \
  -e "s/material_description/description/g" \
  -e "s/regulatoryStandards/regulatory_standards/g" \
  -e "s/machineSettings/machine_settings/g" \
  -e "s/material_challenges/challenges/g" \
  {} \;

# Markdown files
find . -type f -name "*.md" ! -path "./venv/*" ! -path "./.git/*" -exec sed -i '' \
  -e "s/materialCharacteristics/characteristics/g" \
  -e "s/materialProperties/properties/g" \
  -e "s/material_metadata/metadata/g" \
  -e "s/material_description/description/g" \
  -e "s/regulatoryStandards/regulatory_standards/g" \
  -e "s/machineSettings/machine_settings/g" \
  -e "s/material_challenges/challenges/g" \
  {} \;

# Frontmatter files (production location)
if [ -d "/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter" ]; then
    find /Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter -type f -name "*.yaml" -exec sed -i '' \
      -e "s/materialCharacteristics/characteristics/g" \
      -e "s/materialProperties/properties/g" \
      -e "s/material_metadata/metadata/g" \
      -e "s/material_description/description/g" \
      -e "s/regulatoryStandards/regulatory_standards/g" \
      -e "s/machineSettings/machine_settings/g" \
      -e "s/material_challenges/challenges/g" \
      {} \;
fi

echo "✅ Phase 1 + 2 complete!"
echo ""
echo "📊 Changes applied:"
echo "   - Fixed camelCase → snake_case (4 keys)"
echo "   - Removed redundant 'material' prefixes (4 keys)"
echo "   - Total: 7 key renames across entire codebase"
echo ""
echo "🔍 Verification commands:"
echo "   grep -r 'materialCharacteristics' . | wc -l  # Should be 0"
echo "   grep -r 'materialProperties' . | wc -l       # Should be 0"
echo "   grep -r 'material_metadata' . | wc -l        # Should be 0"
echo "   grep -r 'material_description' . | wc -l     # Should be 0"
echo "   grep -r 'regulatoryStandards' . | wc -l      # Should be 0"
echo "   grep -r 'machineSettings' . | wc -l          # Should be 0"
echo "   grep -r 'material_challenges' . | wc -l      # Should be 0"
