# Prompt Redundancy Analysis and Consolidation Opportunities

Based on analysis of the centralized prompt structure, I've identified several key areas for consolidation and redundancy elimination:

## 🎯 **IDENTIFIED REDUNDANCIES**

### 1. **Repeated Boilerplate Across Component Templates**

**Current Redundancy**: Every component template contains identical elements:
```
# Component Template: [Name] Section
# Purpose: [varies]
# Target: [X] words
# Focus: [varies]

Generate title and description for THIS ITEM'S [domain].

Title should be concise (3-5 words) and item-specific.

Description must [specific requirements vary]...

Use the material facts provided and write naturally without AI-typical phrases.
```

**Consolidation Opportunity**: Extract common structure into shared template with variable substitution.

### 2. **Duplicated Anti-AI Guidelines**

**Current Redundancy**: 
- `prompts/core/base.txt` has comprehensive AI detection avoidance
- `prompts/core/humanness_layer.txt` has overlapping AI pattern warnings
- `prompts/quality/evaluation.txt` has similar AI detection criteria
- Component templates have "write naturally without AI-typical phrases"

**Consolidation Opportunity**: Centralize AI avoidance rules in shared include.

### 3. **Schema vs Template File Duplication**

**Current Issue**: Many sections in `section_display_schema.yaml` still contain full prompts even though template files exist.

**Example from schema**:
```yaml
prompt: "Generate title and description for THIS ITEM'S appearance. Title should be concise (3-5 words) and item-specific..."
```

**While template file exists**: `prompts/components/` files

### 4. **Voice Instructions Scattered**

**Current State**:
- Core templates mention writing style
- Component templates reference "natural writing"
- Voice profiles contain detailed instructions
- Humanness layer has style guidance

## 🔧 **CONSOLIDATION RECOMMENDATIONS**

### **Priority 1: Create Shared Template Infrastructure**

Create `prompts/shared/` directory with:

1. **`common_structure.txt`** - Base template structure
2. **`anti_ai_rules.txt`** - Centralized AI avoidance rules  
3. **`natural_writing.txt`** - Common writing guidelines
4. **`title_requirements.txt`** - Standard title formatting rules

### **Priority 2: Template Composition System**

Transform component templates from full text to composition:

```yaml
# Example: prompts/components/identifiers.yaml
template_composition:
  - shared/common_structure.txt
  - shared/title_requirements.txt
  - identifiers_specific.txt
  - shared/anti_ai_rules.txt

variables:
  purpose: "Generate identification information for materials/contaminants"
  target_words: 150
  focus_areas: "Names, classifications, and identification systems"
  specific_requirements: |
    Description must include THIS item's CAS number, molecular formula, 
    IUPAC name, common trade names, historical names, and industry terms...
```

### **Priority 3: Schema Cleanup**

Update `section_display_schema.yaml` to reference template files consistently:

```yaml
# Instead of inline prompts
prompt_file: "prompts/components/identifiers.txt"
# OR
prompt_composition: "prompts/components/identifiers.yaml"
```

### **Priority 4: Unified AI Detection**

Consolidate AI detection rules:

```
prompts/shared/anti_ai_rules.txt:
- All banned words and phrases
- Structural patterns to avoid
- Natural writing requirements

prompts/quality/evaluation.txt:
- Reference shared rules
- Add evaluation-specific criteria
```

## 📊 **ESTIMATED REDUCTION**

**Current State**: 12 template files, ~8,500 total characters with significant overlap

**After Consolidation**: 
- 4-5 shared template components
- 8 component-specific files (50% smaller)
- ~5,000 total characters (40% reduction)
- Zero duplication of common elements

**Maintenance Benefits**:
- ✅ Single source for anti-AI rules
- ✅ Consistent formatting across all components  
- ✅ Easy updates to shared guidelines
- ✅ Clear separation of component-specific vs universal content

## 🚀 **IMPLEMENTATION APPROACH**

1. **Extract Common Elements** → Create shared template files
2. **Create Composition System** → YAML-based template assembly 
3. **Update Component Templates** → Reference shared components
4. **Clean Schema** → Remove inline prompts, reference template files
5. **Update PromptBuilder** → Support template composition system

This consolidation would eliminate ~40% of redundant content while maintaining full functionality and making the system much more maintainable.