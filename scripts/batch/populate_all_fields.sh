#!/bin/bash
# Populate ALL missing fields across ALL domains using QualityEvaluatedGenerator
# This script uses the existing --postprocess command which:
# - Researches and generates if field is empty
# - Uses Winston AI detection for quality validation
# - Includes learning system and voice compliance
# - NO fallbacks/defaults (fail-fast architecture)

echo "════════════════════════════════════════════════════════════════════════════════"
echo "🚀 BATCH FIELD POPULATION - ALL DOMAINS"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "This will populate ALL missing fields using AI research with quality validation:"
echo "  • Materials: description (153), power_intensity (153), context (153)"
echo "  • Contaminants: description (98), micro (88), compounds (98), appearance (98), context (98)"
echo "  • Compounds: description (34)"
echo "  • Settings: description (153), recommendations (153)"
echo ""
echo "Total fields to generate: ~1,200"
echo "Estimated time: 3-6 hours (depending on API speed)"
echo ""
echo "Quality validation: Winston AI detection, voice compliance, learning system"
echo "Architecture: QualityEvaluatedGenerator (NO fallbacks, fail-fast)"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."
echo ""

# Materials domain
echo "════════════════════════════════════════════════════════════════════════════════"
echo "📦 DOMAIN: MATERIALS (153 items)"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

echo "🔄 Generating descriptions..."
python3 run.py --postprocess --domain materials --field description --all
echo ""

echo "🔄 Generating power_intensity values..."
python3 run.py --postprocess --domain materials --field power_intensity --all
echo ""

echo "🔄 Generating context metadata..."
python3 run.py --postprocess --domain materials --field context --all
echo ""

# Contaminants domain
echo "════════════════════════════════════════════════════════════════════════════════"
echo "🧪 DOMAIN: CONTAMINANTS (98 items)"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

echo "🔄 Generating descriptions..."
python3 run.py --postprocess --domain contaminants --field description --all
echo ""

echo "🔄 Generating micro captions..."
python3 run.py --postprocess --domain contaminants --field micro --all
echo ""

echo "🔄 Generating compound compositions..."
python3 run.py --postprocess --domain contaminants --field compounds --all
echo ""

echo "🔄 Generating visual appearance..."
python3 run.py --postprocess --domain contaminants --field appearance --all
echo ""

echo "🔄 Generating context metadata..."
python3 run.py --postprocess --domain contaminants --field context --all
echo ""

# Compounds domain
echo "════════════════════════════════════════════════════════════════════════════════"
echo "⚗️  DOMAIN: COMPOUNDS (34 items)"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

echo "🔄 Generating descriptions..."
python3 run.py --postprocess --domain compounds --field description --all
echo ""

# Settings domain
echo "════════════════════════════════════════════════════════════════════════════════"
echo "⚙️  DOMAIN: SETTINGS (153 items)"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

echo "🔄 Generating descriptions..."
python3 run.py --postprocess --domain settings --field settings_description --all
echo ""

echo "🔄 Generating recommendations..."
python3 run.py --postprocess --domain settings --field recommendations --all
echo ""

# Final summary
echo "════════════════════════════════════════════════════════════════════════════════"
echo "✅ ALL DOMAINS COMPLETE"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Verify field population: python3 scripts/validation/check_data_completeness.py"
echo "2. Export to frontmatter: python3 run.py --export-all"
echo "3. Check export quality: python3 scripts/validation/validate_frontmatter.py"
echo ""
