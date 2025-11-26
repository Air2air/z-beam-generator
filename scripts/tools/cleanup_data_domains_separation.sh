#!/bin/bash
# Cleanup script for data/domains separation of concerns
# Moves Python code from data/materials to domains/materials

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo "=========================================="
echo "Data/Domains Separation Cleanup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Phase 0: Pre-flight checks
echo "📋 Phase 0: Pre-flight Checks"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if files exist
echo "Checking for files to migrate..."
if [ ! -f "data/materials/loader.py" ]; then
    echo -e "${RED}❌ data/materials/loader.py not found${NC}"
    exit 1
fi
if [ ! -f "data/materials/materials.py" ]; then
    echo -e "${RED}❌ data/materials/materials.py not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ All files found${NC}"
echo ""

# Count Python files in data/materials
PY_COUNT=$(find data/materials -maxdepth 1 -name "*.py" | wc -l | tr -d ' ')
echo "Python files in data/materials: $PY_COUNT"
echo ""

# Count imports to update
LOADER_IMPORTS=$(grep -r "from data\.materials\.loader import" --include="*.py" | wc -l | tr -d ' ')
MATERIALS_IMPORTS=$(grep -r "from data\.materials\.materials import" --include="*.py" | wc -l | tr -d ' ')
GENERIC_IMPORTS=$(grep -r "from data\.materials import load_materials_data" --include="*.py" | wc -l | tr -d ' ')

echo "Import statements to update:"
echo "  • data.materials.loader: $LOADER_IMPORTS"
echo "  • data.materials.materials: $MATERIALS_IMPORTS"
echo "  • data.materials (generic): $GENERIC_IMPORTS"
echo "  • Total: $((LOADER_IMPORTS + MATERIALS_IMPORTS + GENERIC_IMPORTS))"
echo ""

# Confirm with user
echo -e "${YELLOW}⚠️  This script will:${NC}"
echo "  1. Create backups of Python files"
echo "  2. Move loader.py → domains/materials/data_loader.py"
echo "  3. Move materials.py → domains/materials/materials_cache.py"
echo "  4. Update all import statements"
echo "  5. Remove __init__.py and __pycache__"
echo ""
read -p "Continue? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ] && [ "$CONFIRM" != "y" ]; then
    echo -e "${RED}❌ Aborted by user${NC}"
    exit 0
fi
echo ""

# Phase 1: Create backups
echo "📦 Phase 1: Create Backups"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

BACKUP_DIR="data/materials/backups/migration_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

cp data/materials/loader.py "$BACKUP_DIR/loader.py"
cp data/materials/materials.py "$BACKUP_DIR/materials.py"
if [ -f "data/materials/__init__.py" ]; then
    cp data/materials/__init__.py "$BACKUP_DIR/__init__.py"
fi

echo -e "${GREEN}✅ Backups created in $BACKUP_DIR${NC}"
echo ""

# Phase 2: Move files
echo "📂 Phase 2: Move Python Files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Moving loader.py → domains/materials/data_loader.py"
mv data/materials/loader.py domains/materials/data_loader.py
echo -e "${GREEN}✅ loader.py moved${NC}"

echo "Moving materials.py → domains/materials/materials_cache.py"
mv data/materials/materials.py domains/materials/materials_cache.py
echo -e "${GREEN}✅ materials.py moved${NC}"

echo ""

# Phase 3: Update internal imports in moved files
echo "🔧 Phase 3: Update Internal Imports"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Updating domains/materials/materials_cache.py..."
# Update the import in materials_cache.py
sed -i '' 's/from data\.materials\.loader import/from domains.materials.data_loader import/g' domains/materials/materials_cache.py
echo -e "${GREEN}✅ materials_cache.py imports updated${NC}"
echo ""

# Phase 4: Update all import statements across codebase
echo "🔄 Phase 4: Update Import Statements"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Running import update script..."
python3 scripts/tools/update_materials_imports.py
echo ""

# Phase 5: Remove Python package infrastructure
echo "🗑️  Phase 5: Remove Python Package Infrastructure"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -f "data/materials/__init__.py" ]; then
    echo "Removing data/materials/__init__.py"
    rm data/materials/__init__.py
    echo -e "${GREEN}✅ __init__.py removed${NC}"
fi

if [ -d "data/materials/__pycache__" ]; then
    echo "Removing data/materials/__pycache__/"
    rm -rf data/materials/__pycache__
    echo -e "${GREEN}✅ __pycache__ removed${NC}"
fi

echo ""

# Phase 6: Verification
echo "✅ Phase 6: Verification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Count Python files remaining in data/materials
REMAINING_PY=$(find data/materials -maxdepth 1 -name "*.py" | wc -l | tr -d ' ')
echo "Python files remaining in data/materials: $REMAINING_PY"

if [ "$REMAINING_PY" -eq 0 ]; then
    echo -e "${GREEN}✅ SUCCESS: No Python files in data/materials${NC}"
else
    echo -e "${RED}⚠️  WARNING: $REMAINING_PY Python files still in data/materials${NC}"
    find data/materials -maxdepth 1 -name "*.py"
fi
echo ""

# Check moved files exist
echo "Verifying moved files exist..."
if [ -f "domains/materials/data_loader.py" ]; then
    echo -e "${GREEN}✅ domains/materials/data_loader.py exists${NC}"
else
    echo -e "${RED}❌ domains/materials/data_loader.py NOT found${NC}"
fi

if [ -f "domains/materials/materials_cache.py" ]; then
    echo -e "${GREEN}✅ domains/materials/materials_cache.py exists${NC}"
else
    echo -e "${RED}❌ domains/materials/materials_cache.py NOT found${NC}"
fi
echo ""

# Phase 7: Test imports
echo "🧪 Phase 7: Test Imports"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Testing data_loader import..."
python3 -c "from domains.materials.data_loader import load_materials_data; print('✅ data_loader import successful')" 2>&1
echo ""

echo "Testing materials_cache import..."
python3 -c "from domains.materials.materials_cache import get_material_by_name_cached; print('✅ materials_cache import successful')" 2>&1
echo ""

echo "Testing materials data loading..."
python3 -c "from domains.materials.data_loader import load_materials_data; data = load_materials_data(); print(f'✅ Loaded {len(data.get(\"materials\", {}))} materials')" 2>&1
echo ""

# Summary
echo "=========================================="
echo "✅ CLEANUP COMPLETE"
echo "=========================================="
echo ""
echo "📊 Summary:"
echo "  • Files moved: 2 (loader.py, materials.py)"
echo "  • Files removed: __init__.py, __pycache__/"
echo "  • Import statements updated: $((LOADER_IMPORTS + MATERIALS_IMPORTS + GENERIC_IMPORTS))"
echo "  • Backups saved to: $BACKUP_DIR"
echo ""
echo -e "${GREEN}✅ data/materials now contains ONLY data files${NC}"
echo -e "${GREEN}✅ Python code moved to domains/materials${NC}"
echo ""
echo "Next steps:"
echo "  1. Run test suite: python3 run.py --test"
echo "  2. Test functionality: python3 run.py --material Steel"
echo "  3. Check for broken imports: grep -r 'from data.materials' --include='*.py'"
echo ""
