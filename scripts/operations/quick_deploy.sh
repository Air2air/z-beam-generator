#!/bin/bash
#
# Quick Deployment Script
# =======================
#
# Deploys all domains and validates in 4 steps:
# 1-4. Export all domains (materials, settings, contaminants, compounds) via orchestrator
# 5. Re-extract associations
# 6. Run tests
#
# ⚠️ MANDATORY REQUIREMENT: All exporters MUST have ZERO API calls
# - Uses scripts/operations/deploy_all.py for orchestrated export
# - All exporters: Simple YAML-to-YAML copy (NO API calls)
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

# Steps 1-4: Export All Domains (using orchestrator)
echo -e "${BLUE}📦 Steps 1-4/6: Exporting All Domains (NO API)...${NC}"
python3 scripts/operations/deploy_all.py --skip-tests

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
