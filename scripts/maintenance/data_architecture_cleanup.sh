#!/bin/bash
# Data Architecture Cleanup Script
# Based on E2E Data Architecture Evaluation (Dec 19, 2025)
# Estimated time: 5 minutes
# Recoverable space: 3.2 MB

set -e  # Exit on error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "════════════════════════════════════════════════════════════════"
echo "DATA ARCHITECTURE CLEANUP"
echo "Based on: E2E_DATA_ARCHITECTURE_EVALUATION_DEC19_2025.md"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track stats
DELETED_COUNT=0
DELETED_SIZE=0
ARCHIVED_COUNT=0
ARCHIVED_SIZE=0

echo "🔍 STEP 1: Analyzing temporary files..."
echo "────────────────────────────────────────────────────────────────"

# Check for temporary files
TEMP_FILES=(
    "data/materials/tmpoxw4bv9n.yaml"
    "data/contaminants/tmp1ussiti8.yaml"
)

for file in "${TEMP_FILES[@]}"; do
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        size_bytes=$(du -b "$file" | cut -f1)
        echo -e "${YELLOW}   Found:${NC} $file ($size)"
        DELETED_COUNT=$((DELETED_COUNT + 1))
        DELETED_SIZE=$((DELETED_SIZE + size_bytes))
    fi
done

echo ""
echo "🗂️  STEP 2: Analyzing backup files..."
echo "────────────────────────────────────────────────────────────────"

# Check for backup files
BACKUP_FILES=(
    "data/compounds/Compounds.yaml.backup"
    "data/compounds/Compounds.yaml.pre-migration-backup"
    "data/associations/ExtractedLinkages.yaml.old"
)

for file in "${BACKUP_FILES[@]}"; do
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        size_bytes=$(du -b "$file" | cut -f1)
        echo -e "${YELLOW}   Found:${NC} $file ($size)"
        ARCHIVED_COUNT=$((ARCHIVED_COUNT + 1))
        ARCHIVED_SIZE=$((ARCHIVED_SIZE + size_bytes))
    fi
done

echo ""
echo "🗄️  STEP 3: Analyzing legacy files..."
echo "────────────────────────────────────────────────────────────────"

# Check for legacy files
LEGACY_FILES=(
    "data/materials/MachineSettings.yaml"
)

for file in "${LEGACY_FILES[@]}"; do
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        size_bytes=$(du -b "$file" | cut -f1)
        echo -e "${YELLOW}   Found:${NC} $file ($size) - Replaced by Settings.yaml"
        DELETED_COUNT=$((DELETED_COUNT + 1))
        DELETED_SIZE=$((DELETED_SIZE + size_bytes))
    fi
done

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📊 CLEANUP SUMMARY"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Convert bytes to MB
deleted_mb=$(echo "scale=2; $DELETED_SIZE / 1048576" | bc)
archived_mb=$(echo "scale=2; $ARCHIVED_SIZE / 1048576" | bc)
total_mb=$(echo "scale=2; ($DELETED_SIZE + $ARCHIVED_SIZE) / 1048576" | bc)

echo "   Files to delete:  $DELETED_COUNT ($deleted_mb MB)"
echo "   Files to archive: $ARCHIVED_COUNT ($archived_mb MB)"
echo "   Total savings:    $total_mb MB"
echo ""

# Ask for confirmation
read -p "Proceed with cleanup? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Cleanup cancelled.${NC}"
    exit 0
fi

echo ""
echo "🗑️  STEP 4: Deleting temporary files..."
echo "────────────────────────────────────────────────────────────────"

for file in "${TEMP_FILES[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo -e "${GREEN}   ✅ Deleted:${NC} $file"
    fi
done

for file in "${LEGACY_FILES[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo -e "${GREEN}   ✅ Deleted:${NC} $file"
    fi
done

echo ""
echo "📦 STEP 5: Archiving backup files..."
echo "────────────────────────────────────────────────────────────────"

# Create backups directory
mkdir -p data/backups/

for file in "${BACKUP_FILES[@]}"; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        mv "$file" "data/backups/$filename"
        echo -e "${GREEN}   ✅ Archived:${NC} $file → data/backups/"
    fi
done

echo ""
echo "════════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ CLEANUP COMPLETE${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Results:"
echo "   • Deleted $DELETED_COUNT files ($deleted_mb MB)"
echo "   • Archived $ARCHIVED_COUNT files ($archived_mb MB)"
echo "   • Total space saved: $total_mb MB"
echo ""
echo "Next steps:"
echo "   1. Review E2E_DATA_ARCHITECTURE_EVALUATION_DEC19_2025.md"
echo "   2. Add schema_version to Materials.yaml (manual edit)"
echo "   3. Run association count verification"
echo ""
