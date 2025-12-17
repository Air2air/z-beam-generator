#!/bin/bash
#
# Quick Deployment Script
# =======================
#
# Deploys all domains and validates in 6 steps:
# 1-4. Export all domains (materials, settings, contaminants, compounds) via orchestrator
# 5. Re-extract associations
# 6. Copy frontmatter to production (z-beam directory)
# 7. Run tests
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

# Steps 1-6: Export All Domains, Extract Associations, Copy to Production
echo -e "${BLUE}📦 Steps 1-6/7: Full Deployment (Export + Extract + Production Copy)...${NC}"
python3 scripts/operations/deploy_all.py --skip-tests

# Step 7: Run tests
echo ""
echo -e "${BLUE}🧪 Step 7/7: Running Test Suite...${NC}"
python3 -m pytest tests/test_centralized_architecture.py -v --tb=line 2>&1 | grep -E "(PASSED|FAILED|passed|failed)" | tail -5

echo ""
echo "========================================================================"
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE${NC}"
echo "========================================================================"
