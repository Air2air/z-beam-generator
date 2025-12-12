#!/bin/bash
# Domains Cleanup Script - Phase 1: Safe Deletions
# Date: December 11, 2025
# Risk: ZERO - All files regenerated automatically

cd "$(dirname "$0")"

echo "🧹 DOMAINS CLEANUP - PHASE 1: SAFE DELETIONS"
echo "=============================================="
echo ""

# 1. Cache files
echo "1️⃣  Deleting cache files..."
if [ -d "domains/cache" ]; then
    du -sh domains/cache 2>/dev/null
    rm -rf domains/cache/*
    echo "   ✅ Cache deleted"
else
    echo "   ℹ️  No cache folder found"
fi
echo ""

# 2. Python bytecode
echo "2️⃣  Deleting Python bytecode..."
pycache_count=$(find domains -type d -name __pycache__ 2>/dev/null | wc -l | tr -d ' ')
echo "   Found: $pycache_count __pycache__ folders"
find domains -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
echo "   ✅ Bytecode deleted"
echo ""

# 3. macOS metadata
echo "3️⃣  Deleting macOS metadata..."
ds_count=$(find domains -name .DS_Store 2>/dev/null | wc -l | tr -d ' ')
echo "   Found: $ds_count .DS_Store files"
find domains -name .DS_Store -delete 2>/dev/null
echo "   ✅ Metadata deleted"
echo ""

echo "✨ Phase 1 complete!"
echo ""
echo "Storage saved: ~15-20MB"
echo "Next: Run phase2_investigate.sh"
