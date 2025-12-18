#!/bin/bash
# Rename domain_linkages to relationships across the entire codebase

echo "🔄 Renaming 'domain_linkages' to 'relationships' throughout codebase..."

# Python files
find . -type f -name "*.py" ! -path "./venv/*" ! -path "./.git/*" -exec sed -i '' "s/domain_linkages/relationships/g" {} \;

# YAML files
find . -type f -name "*.yaml" ! -path "./venv/*" ! -path "./.git/*" -exec sed -i '' "s/domain_linkages/relationships/g" {} \;

# Markdown files
find . -type f -name "*.md" ! -path "./venv/*" ! -path "./.git/*" -exec sed -i '' "s/domain_linkages/relationships/g" {} \;

# Config files
find export/config -type f -name "*.yaml" -exec sed -i '' "s/domain_linkages/relationships/g" {} \;

# Test files
find tests -type f -name "*.py" -exec sed -i '' "s/domain_linkages/relationships/g" {} \;

# Schema files
find data/schemas -type f -name "*.yaml" -exec sed -i '' "s/domain_linkages/relationships/g" {} \;

# Data files
find data -type f -name "*.yaml" -exec sed -i '' "s/domain_linkages/relationships/g" {} \;

# Frontmatter files (in production location)
if [ -d "/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter" ]; then
    find /Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter -type f -name "*.yaml" -exec sed -i '' "s/domain_linkages/relationships/g" {} \;
fi

echo "✅ Renamed all occurrences of 'domain_linkages' to 'relationships'"
echo ""
echo "📝 Updated files in:"
echo "   - Python source files (*.py)"
echo "   - YAML config and data files (*.yaml)"
echo "   - Markdown documentation (*.md)"
echo "   - Test files"
echo "   - Schema definitions"
echo "   - Frontmatter files (production)"
echo ""
echo "⚠️  Note: This also renames related terms:"
echo "   - DomainLinkagesService → RelationshipsService"
echo "   - domain_linkages_generator.py → relationships_generator.py"
echo "   - domain_linkages_enricher.py → relationships_enricher.py"
echo "   - etc."
