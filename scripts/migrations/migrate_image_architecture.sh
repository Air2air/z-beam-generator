#!/bin/bash
set -e

echo "🚀 Starting Image Architecture Migration (Option A)"
echo "=================================================="

# Phase 1: Create new directories
echo ""
echo "📁 Phase 1: Creating new directory structure..."

mkdir -p shared/image/utils
mkdir -p shared/image/templates
mkdir -p domains/materials/image/templates
mkdir -p domains/materials/image/research

echo "   ✅ Created shared/image/utils/"
echo "   ✅ Created shared/image/templates/"
echo "   ✅ Created domains/materials/image/templates/"
echo "   ✅ Created domains/materials/image/research/"

# Phase 2: Move shared utilities
echo ""
echo "🔧 Phase 2: Moving shared utilities..."

if [ -f "shared/image/prompts/prompt_builder.py" ]; then
    mv shared/image/prompts/prompt_builder.py shared/image/utils/
    echo "   ✅ Moved prompt_builder.py → shared/image/utils/"
fi

if [ -f "shared/image/prompts/prompt_optimizer.py" ]; then
    mv shared/image/prompts/prompt_optimizer.py shared/image/utils/
    echo "   ✅ Moved prompt_optimizer.py → shared/image/utils/"
fi

if [ -f "shared/image/prompts/image_pipeline_monitor.py" ]; then
    mv shared/image/prompts/image_pipeline_monitor.py shared/image/utils/
    echo "   ✅ Moved image_pipeline_monitor.py → shared/image/utils/"
fi

if [ -f "shared/image/prompts/__init__.py" ]; then
    mv shared/image/prompts/__init__.py shared/image/utils/__init__.py
    echo "   ✅ Moved __init__.py → shared/image/utils/"
fi

# Phase 3: Move shared templates
echo ""
echo "📄 Phase 3: Moving shared templates..."

if [ -d "shared/image/prompts/shared" ]; then
    # Move contents of shared/prompts/shared/ to shared/templates/
    cp -r shared/image/prompts/shared/* shared/image/templates/ 2>/dev/null || echo "   ⚠️  No shared templates to move"
    echo "   ✅ Moved shared template content → shared/image/templates/"
fi

# Phase 4: Move materials templates
echo ""
echo "📄 Phase 4: Moving materials templates..."

if [ -f "domains/materials/image/prompts/base_prompt.txt" ]; then
    mv domains/materials/image/prompts/base_prompt.txt domains/materials/image/templates/contamination.txt
    echo "   ✅ Moved base_prompt.txt → domains/materials/image/templates/contamination.txt"
fi

# Phase 5: Move materials research utilities
echo ""
echo "🔧 Phase 5: Moving materials research utilities..."

if [ -f "domains/materials/image/prompts/material_researcher.py" ]; then
    mv domains/materials/image/prompts/material_researcher.py domains/materials/image/research/
    echo "   ✅ Moved material_researcher.py → domains/materials/image/research/"
fi

if [ -f "domains/materials/image/prompts/category_contamination_researcher.py" ]; then
    mv domains/materials/image/prompts/category_contamination_researcher.py domains/materials/image/research/
    echo "   ✅ Moved category_contamination_researcher.py → domains/materials/image/research/"
fi

if [ -f "domains/materials/image/prompts/persistent_research_cache.py" ]; then
    mv domains/materials/image/prompts/persistent_research_cache.py domains/materials/image/research/
    echo "   ✅ Moved persistent_research_cache.py → domains/materials/image/research/"
fi

if [ -f "domains/materials/image/prompts/material_prompts.py" ]; then
    mv domains/materials/image/prompts/material_prompts.py domains/materials/image/research/
    echo "   ✅ Moved material_prompts.py → domains/materials/image/research/"
fi

if [ -f "domains/materials/image/prompts/payload_monitor.py" ]; then
    mv domains/materials/image/prompts/payload_monitor.py domains/materials/image/research/
    echo "   ✅ Moved payload_monitor.py → domains/materials/image/research/"
fi

if [ -f "domains/materials/image/prompts/__init__.py" ]; then
    mv domains/materials/image/prompts/__init__.py domains/materials/image/research/__init__.py
    echo "   ✅ Moved __init__.py → domains/materials/image/research/"
fi

# Phase 6: Rename other domain prompt directories to templates
echo ""
echo "📄 Phase 6: Renaming domain prompt directories to templates..."

for domain in contaminants applications regions thesaurus; do
    if [ -d "domains/$domain/image/prompts" ]; then
        mv "domains/$domain/image/prompts" "domains/$domain/image/templates"
        echo "   ✅ Renamed domains/$domain/image/prompts → templates"
    fi
done

# Phase 7: Clean up old directories
echo ""
echo "🧹 Phase 7: Cleaning up old directories..."

if [ -d "shared/image/prompts" ] && [ -z "$(ls -A shared/image/prompts 2>/dev/null)" ]; then
    rmdir shared/image/prompts
    echo "   ✅ Removed empty shared/image/prompts/"
fi

if [ -d "domains/materials/image/prompts" ] && [ -z "$(ls -A domains/materials/image/prompts 2>/dev/null)" ]; then
    rmdir domains/materials/image/prompts
    echo "   ✅ Removed empty domains/materials/image/prompts/"
fi

echo ""
echo "=================================================="
echo "✅ Migration Phase 1 Complete!"
echo ""
echo "Next steps:"
echo "  1. Update Python imports (Phase 2)"
echo "  2. Update config.yaml files (Phase 3)"
echo "  3. Run tests to verify"
