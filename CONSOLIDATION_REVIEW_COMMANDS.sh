#!/bin/bash
# Documentation Consolidation Review Commands
# Run these commands to review the consolidation plan before approval

echo "=================================================="
echo "📚 DOCUMENTATION CONSOLIDATION REVIEW COMMANDS"
echo "=================================================="
echo ""

# 1. View the detailed consolidation plan
echo "1️⃣  View detailed consolidation plan:"
echo "   cat DOCUMENTATION_CONSOLIDATION_PLAN.md"
echo ""

# 2. See all completion/summary docs to be archived
echo "2️⃣  See 60 completion/summary docs to be archived:"
echo "   find docs/ -name '*COMPLETE*.md' -o -name '*SUMMARY*.md' -o -name '*REPORT*.md' | sort"
echo ""

# 3. See proposal docs
echo "3️⃣  See 11 proposal docs:"
echo "   find docs/ -name '*PROPOSAL*.md' | sort"
echo ""

# 4. See architecture docs
echo "4️⃣  See 17 architecture docs:"
echo "   find docs/ -name '*ARCHITECTURE*.md' | sort"
echo ""

# 5. See frontmatter docs
echo "5️⃣  See 16 frontmatter docs:"
echo "   find docs/ -name '*FRONTMATTER*.md' | sort"
echo ""

# 6. See testing docs
echo "6️⃣  See 18 testing docs:"
echo "   find docs/ -name '*TEST*.md' | sort"
echo ""

# 7. See current directory structure
echo "7️⃣  See current docs directory structure:"
echo "   tree -L 2 docs/ | head -50"
echo ""

# 8. See file count and size
echo "8️⃣  See current documentation stats:"
echo "   echo 'Files:' && find docs/ -name '*.md' | wc -l"
echo "   echo 'Size:' && du -sh docs/"
echo ""

# 9. Preview consolidation impact
echo "9️⃣  Preview consolidation impact:"
echo "   echo 'Current: 233 files (2.20 MB)'"
echo "   echo 'Target: ~50 files (1.5 MB)'"
echo "   echo 'Reduction: 78% fewer files, 32% smaller'"
echo ""

# 10. Check recent modifications
echo "🔟 See recently modified docs (last 7 days):"
echo "   find docs/ -name '*.md' -mtime -7 -ls | sort -k11"
echo ""

echo "=================================================="
echo "🎯 QUICK DECISION GUIDE"
echo "=================================================="
echo ""
echo "✅ APPROVE if you want to:"
echo "   • Reduce 233 → ~50 documentation files"
echo "   • Archive 60 completion/summary docs into single file"
echo "   • Consolidate overlapping architecture/testing/API docs"
echo "   • Create cleaner, more navigable documentation structure"
echo "   • Preserve all historical content in docs/archive/"
echo ""
echo "❌ REJECT if you want to:"
echo "   • Keep current documentation as-is"
echo "   • Review specific files before consolidation"
echo "   • Modify the consolidation plan first"
echo ""
echo "⚠️  SAFEGUARDS IN PLACE:"
echo "   • Git commit before each phase (easy rollback)"
echo "   • NO DELETIONS - only moves to archive/"
echo "   • Phase-by-phase execution with user checkpoints"
echo "   • Content verification before any changes"
echo ""
echo "=================================================="
echo "📋 TO APPROVE AND PROCEED:"
echo "=================================================="
echo ""
echo "Reply with: 'Approved - proceed with Phase 1'"
echo "or: 'Approved - proceed with all phases'"
echo "or: 'Review [specific category] first'"
echo ""
