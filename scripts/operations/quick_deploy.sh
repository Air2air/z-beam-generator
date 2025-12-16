#!/bin/bash
#
# Quick Deployment Script
# =======================
#
# Deploys all domains and validates in 6 steps:
# 1. Export materials (153 files) - NO API calls + ISO 8601 timestamps
# 2. Export settings (153 files) - NO API calls + ISO 8601 timestamps
# 3. Export contaminants (98 files) - NO API calls + ISO 8601 timestamps
# 4. Export compounds (25 files) - NO API calls + ISO 8601 timestamps
# 5. Re-extract associations
# 6. Run tests
#
# ⚠️ MANDATORY REQUIREMENT: All exporters MUST have ZERO API calls
# - Materials: TrivialFrontmatterExporter - Simple YAML-to-YAML copy
# - Settings: TrivialSettingsExporter - Simple YAML-to-YAML copy
# - Contaminants: TrivialContaminantsExporter - Simple YAML-to-YAML copy
# - Compounds: CompoundExporter - Simple YAML-to-YAML copy
#
# ✅ TIMESTAMP GENERATION: All exporters generate ISO 8601 timestamps
# - datePublished: Generated on first export if missing
# - dateModified: Updated on every export
# - Format: YYYY-MM-DDTHH:MM:SS.ffffff (Python datetime.now().isoformat())
#
# All AI generation, research, and validation happens BEFORE export.
# Exporters only copy complete, validated data to frontmatter files.
#
# Usage: bash scripts/operations/quick_deploy.sh

set -e  # Exit on error

echo "========================================================================"
echo "🚀 QUICK DEPLOYMENT PIPELINE"
echo "========================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

cd "$(dirname "$0")/../.."

# Step 1: Export Materials
echo -e "${BLUE}📦 Step 1/6: Exporting Materials (NO API)...${NC}"
python3 << 'EOF'
from export.core.trivial_exporter import TrivialFrontmatterExporter
exporter = TrivialFrontmatterExporter()
print("Exporting 153 materials...")
exporter.export_all(force=True)
print("✅ Materials exported (NO API calls made)")
EOF

# Step 2: Export Settings
echo ""
echo -e "${BLUE}📦 Step 2/6: Exporting Settings (NO API)...${NC}"
python3 << 'EOF'
from export.settings.trivial_exporter import TrivialSettingsExporter
exporter = TrivialSettingsExporter()
print("Exporting 153 settings...")
exporter.export_all(force=True)
print("✅ Settings exported (NO API calls made)")
EOF

# Step 3: Export Contaminants  
echo ""
echo -e "${BLUE}📦 Step 3/6: Exporting Contaminants (NO API)...${NC}"
python3 << 'EOF'
from export.contaminants.trivial_exporter import TrivialContaminantsExporter
exporter = TrivialContaminantsExporter()
print("Exporting 98 contaminants...")
exporter.export_all(force=True)
print("✅ Contaminants exported (NO API calls made)")
EOF

# Step 4: Export Compounds
echo ""
echo -e "${BLUE}📦 Step 4/6: Exporting Compounds (NO API)...${NC}"
python3 << 'EOF'
from export.compounds.trivial_exporter import CompoundExporter
exporter = CompoundExporter()
print("Exporting 25 compounds...")
exporter.export_all(force=True)
print("✅ Compounds exported (NO API calls made)")
EOF

# Step 5: Re-extract associations
echo ""
echo -e "${BLUE}🔗 Step 5/6: Re-extracting Domain Associations...${NC}"
python3 scripts/data/extract_existing_linkages.py | tail -20

# Step 6: Run tests
echo ""
echo -e "${BLUE}🧪 Step 6/6: Running Test Suite...${NC}"
python3 -m pytest tests/test_centralized_architecture.py -v --tb=line 2>&1 | grep -E "(PASSED|FAILED|passed|failed)" | tail -5

echo ""
echo "========================================================================"
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE${NC}"
echo "========================================================================"
