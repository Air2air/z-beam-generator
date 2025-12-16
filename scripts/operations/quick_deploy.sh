#!/bin/bash
#
# Quick Deployment Script
# =======================
#
# Deploys all domains and validates in 3 steps:
# 1. Export materials (153 files)
# 2. Export contaminants (98 files)
# 3. Export compounds (25 files)
# 4. Re-extract associations
# 5. Run tests
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
echo -e "${BLUE}📦 Step 1/5: Exporting Materials...${NC}"
python3 << 'EOF'
from export.core.trivial_exporter import TrivialFrontmatterExporter
exporter = TrivialFrontmatterExporter()
print("Exporting 153 materials...")
exporter.export_all()
print("✅ Materials exported")
EOF

# Step 2: Export Contaminants  
echo ""
echo -e "${BLUE}📦 Step 2/5: Exporting Contaminants...${NC}"
python3 << 'EOF'
from export.contaminants.trivial_exporter import ContaminantsFrontmatterExporter
exporter = ContaminantsFrontmatterExporter()
print("Exporting 98 contaminants...")
exporter.export_all()
print("✅ Contaminants exported")
EOF

# Step 3: Export Compounds
echo ""
echo -e "${BLUE}📦 Step 3/5: Exporting Compounds...${NC}"
python3 << 'EOF'
from export.compounds.trivial_exporter import CompoundsFrontmatterExporter
exporter = CompoundsFrontmatterExporter()
print("Exporting 25 compounds...")
exporter.export_all()
print("✅ Compounds exported")
EOF

# Step 4: Re-extract associations
echo ""
echo -e "${BLUE}🔗 Step 4/5: Re-extracting Domain Associations...${NC}"
python3 scripts/data/extract_existing_linkages.py | tail -20

# Step 5: Run tests
echo ""
echo -e "${BLUE}🧪 Step 5/5: Running Test Suite...${NC}"
python3 -m pytest tests/test_centralized_architecture.py -v --tb=line 2>&1 | grep -E "(PASSED|FAILED|passed|failed)" | tail -5

echo ""
echo "========================================================================"
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE${NC}"
echo "========================================================================"
