#!/bin/bash
set -e

echo "🚀 Text Architecture Migration - Matching Image Pattern"
echo "========================================================"
echo ""

# Phase 1: Create new directory structure
echo "📁 Phase 1: Creating new directory structure..."

# Shared text utilities
mkdir -p shared/text/utils
mkdir -p shared/text/templates/system
mkdir -p shared/text/templates/rules
mkdir -p shared/text/templates/evaluation
mkdir -p shared/text/validation
mkdir -p shared/text/learning

# Domain text structures (matching image pattern)
for domain in materials contaminants applications regions thesaurus; do
    mkdir -p domains/$domain/text/templates
done

echo "   ✅ Created shared/text/ structure"
echo "   ✅ Created domains/*/text/templates/ structure"
echo ""

# Phase 2: Move shared utilities (Python code)
echo "📦 Phase 2: Moving shared utilities to shared/text/utils/..."

# Core generation utilities
mv generation/core/prompt_builder.py shared/text/utils/
mv generation/core/length_manager.py shared/text/utils/
mv generation/core/sentence_calculator.py shared/text/utils/
mv generation/core/component_specs.py shared/text/utils/

echo "   ✅ Moved 4 utilities to shared/text/utils/"
echo ""

# Phase 3: Move validation utilities
echo "🔍 Phase 3: Moving validation utilities..."

mv generation/validation/* shared/text/validation/

echo "   ✅ Moved validation/ to shared/text/validation/"
echo ""

# Phase 4: Move learning utilities
echo "�� Phase 4: Moving learning utilities..."

if [ -d "generation/learning" ]; then
    mv generation/learning/* shared/text/learning/
fi

# Move specific learning files
if [ -d "processing/learning" ]; then
    cp processing/learning/realism_optimizer.py shared/text/learning/ 2>/dev/null || true
    cp processing/learning/subjective_pattern_learner.py shared/text/learning/ 2>/dev/null || true
fi

echo "   ✅ Moved learning utilities"
echo ""

# Phase 5: Move shared templates (content files)
echo "📄 Phase 5: Moving shared templates..."

# System prompts
mv prompts/system/* shared/text/templates/system/

# Rules
mv prompts/rules/* shared/text/templates/rules/

# Evaluation
mv prompts/evaluation/* shared/text/templates/evaluation/

echo "   ✅ Moved shared templates to shared/text/templates/"
echo ""

# Phase 6: Move domain-specific templates
echo "🌍 Phase 6: Moving domain-specific templates..."

for domain in materials contaminants applications regions thesaurus; do
    if [ -d "domains/$domain/prompts" ]; then
        mv domains/$domain/prompts/* domains/$domain/text/templates/
        echo "   ✅ Moved $domain templates"
    fi
done

echo ""

# Phase 7: Rename component prompts to templates
echo "🔄 Phase 7: Moving component templates..."

if [ -d "prompts/components" ]; then
    # These become shared component templates
    mkdir -p shared/text/templates/components
    mv prompts/components/* shared/text/templates/components/
    echo "   ✅ Moved component templates to shared/text/templates/components/"
fi

echo ""

# Phase 8: Clean up empty directories
echo "🧹 Phase 8: Cleaning up empty directories..."

for domain in materials contaminants applications regions thesaurus; do
    if [ -d "domains/$domain/prompts" ] && [ -z "$(ls -A domains/$domain/prompts)" ]; then
        rmdir domains/$domain/prompts
        echo "   ✅ Removed empty domains/$domain/prompts/"
    fi
done

if [ -d "prompts/system" ] && [ -z "$(ls -A prompts/system)" ]; then
    rmdir prompts/system
fi

if [ -d "prompts/rules" ] && [ -z "$(ls -A prompts/rules)" ]; then
    rmdir prompts/rules
fi

if [ -d "prompts/evaluation" ] && [ -z "$(ls -A prompts/evaluation)" ]; then
    rmdir prompts/evaluation
fi

if [ -d "prompts/components" ] && [ -z "$(ls -A prompts/components)" ]; then
    rmdir prompts/components
fi

echo "   ✅ Cleaned up empty directories"
echo ""

echo "✨ Migration complete!"
echo ""
echo "New structure:"
echo "  shared/text/utils/          - Python utilities"
echo "  shared/text/templates/      - Shared content"
echo "  shared/text/validation/     - Validation utilities"
echo "  shared/text/learning/       - Learning utilities"
echo "  domains/*/text/templates/   - Domain-specific content"
