# Word Count in Prompts Policy

**Status**: MANDATORY  
**Effective**: December 29, 2025  
**Enforcement**: Automated verification, code review

---

## Policy Statement

**ALL word count specifications MUST be defined in prompt templates stored in the prompt catalog (`prompts/registry/prompt_catalog.yaml`, under `catalog.byPath` entries like `prompts/{domain}/*.txt`). Zero tolerance for word counts in configuration files.**

---

## Rationale

### Single Source of Truth
- Content requirements and word counts belong together
- No synchronization issues between config and prompts
- Easier to maintain and update
- Clear ownership: domain experts own their prompts

### Content-Aware Specification
- Word count is a content requirement, not a technical parameter
- Varies by content type and purpose
- Domain-specific needs (FAQ vs health_effects vs description)
- Better context when reviewing/editing prompts

### Simplified Architecture
- Removes `component_lengths` dictionary from generation config
- No need to look up lengths in multiple places
- Prompt file is complete specification

---

## Implementation Rules

### ✅ REQUIRED Format

**Every text generation prompt MUST include:**

```plaintext
WORD LENGTH: X-Y words

Additional notes (optional):
- (vary naturally for diversity)
- (per answer for multi-part content)
- (strict maximum for SEO)
```

**Examples:**

```plaintext
# FAQ Prompt
WORD LENGTH: 50-150 words per answer

# Description Prompt
WORD LENGTH: 40-180 words (vary length naturally for diversity)

# SEO Description
WORD LENGTH: 50-160 characters (strict maximum for SEO)

# Page Title
WORD LENGTH: 8-12 words for page_title (50-55 characters)

# Micro Content
WORD LENGTH: 80-240 words
```

### ❌ PROHIBITED

**Never define word counts in:**
- `generation/config.yaml`
- `domains/*/config.yaml`
- Python code (generators, adapters)
- Domain-specific configuration files

**Exception**: Research fields that return structured data (not prose) may omit word length if appropriate.

---

## Standard Word Count Ranges

### Text Components (Human-Readable Prose)

| Component | Range | Notes |
|-----------|-------|-------|
| **FAQ answers** | 50-150 words per answer | 3 answers per item |
| **Material descriptions** | 50-150 words | Technical subtitles |
| **Contaminant descriptions** | 40-180 words | Vary naturally |
| **Settings descriptions** | 65-195 words | Operational guidance |
| **Micro content** | 80-240 words | Before/after imagery |
| **Excerpts** | 80-240 words | Summary text (DEPRECATED) |
| **Health effects** | 165-495 words | Detailed safety |
| **Compound sections** | 165-495 words | Emergency response, regulatory, etc. |

### SEO Components

| Component | Range | Notes |
|-----------|-------|-------|
| **Page title** | 8-12 words | 50-55 characters |
| **Meta description** | 25-35 words | 155-160 characters |
| **SEO description** | 50-160 characters | Strict maximum |

### Research Components (Structured Data)

| Component | Range | Notes |
|-----------|-------|-------|
| **Power intensity** | 5-10 words | Numerical range only |
| **Context metadata** | 10-30 words | Structured format |
| **Appearance** | 100-300 words | Visual details |
| **Compounds list** | 50-150 words | Chemical composition |
| **Recommendations** | 200-600 words | Structured guidance |

---

## Variation Guidelines

### Natural Variation (Content Diversity)
- Use 3x ranges for maximum variation (e.g., 40-180 = 4.5x)
- Encourages structural diversity across batch generations
- Prevents uniform output lengths
- Example: "40-180 words (vary length naturally for diversity)"

### Per-Unit Specifications
- Multi-part content (FAQs, lists) specifies "per answer" or "per item"
- Example: "50-150 words per answer" for 3-FAQ set
- Total: 150-450 words for complete FAQ

### Strict Limits (SEO)
- Character-based limits for search engine compliance
- Example: "50-160 characters (strict maximum for SEO)"
- No flexibility - search engines truncate beyond limits

---

## Migration Status

### ✅ COMPLETE (Dec 29, 2025)

**Config Cleaned:**
- Removed `component_lengths` from `generation/config.yaml`
- Added deprecation notice with historical context
- Documented where to find word counts (in prompts)

**Prompts Updated:**
- 43 prompts already had WORD LENGTH specifications ✅
- Added word counts to 8 files that were missing them
- Standardized format across all 51 text generation prompts

**Files Updated (prompt catalog entries):**
- `prompts/materials/page_title.txt` - Added 8-12 words spec
- `prompts/materials/meta_description.txt` - Added 25-35 words spec
- `prompts/materials/power_intensity.txt` - Added 5-10 words spec
- `prompts/materials/context.txt` - Added 10-30 words spec
- `prompts/settings/recommendations.txt` - Added 200-600 words spec
- `prompts/contaminants/context.txt` - Added 10-30 words spec
- `prompts/contaminants/appearance.txt` - Added 100-300 words spec
- `prompts/contaminants/compounds.txt` - Added 50-150 words spec

**Config Parameters Removed:**
- `length_variation_range` (was: 10 → ±60%) - DEPRECATED, ranges now in prompts
- `word_count_variation` (was: 0.70 → ±70%) - DEPRECATED, ranges now in prompts

**Rationale for Removal**: Created duplication and confusion. Prompt catalog entries now contain COMPLETE range specifications with sufficient natural variation (3x-4x multipliers common). No additional calculation needed.

**Backward Compatibility**: Legacy code accessing these parameters will receive default values (50% variation) to prevent breakage. Code should be migrated to read ranges from prompt files directly.

**Image prompts excluded:** Image generation prompt systems in `domains/materials/image/research/` and `shared/image/utils/` are not text generation and correctly don't need word counts.

---

## Verification

### Automated Tests

**Test Requirements:**
```python
def test_all_text_prompts_have_word_length():
    """Verify WORD LENGTH specification in all text generation prompts."""
    text_prompt_dirs = [
        'prompts/materials',
        'prompts/contaminants', 
        'prompts/compounds',
        'prompts/settings'
    ]
    
    for prompt_dir in text_prompt_dirs:
        for prompt_file in Path(prompt_dir).glob('*.txt'):
            # Skip research prompts that return structured data
            if 'recommendations' in prompt_file.name or 'context' in prompt_file.name:
                continue  # Optional for structured output
                
            with open(prompt_file) as f:
                content = f.read()
                assert 'WORD LENGTH:' in content, \
                    f"{prompt_file} missing WORD LENGTH specification"

def test_no_word_counts_in_config():
    """Ensure word counts removed from configuration files."""
    with open('generation/config.yaml') as f:
        content = f.read()
        # Should NOT have component_lengths active section
        assert 'component_lengths:' not in content or \
               'DEPRECATED' in content[:content.find('component_lengths')], \
            "component_lengths still active in config.yaml"
```

### Manual Review Checklist

**Before merging prompt changes:**
- [ ] WORD LENGTH line present in prompt file
- [ ] Range appropriate for content type (see Standard Ranges table)
- [ ] Notes included if special requirements (per answer, vary naturally, strict maximum)
- [ ] Config files DO NOT contain word count specifications

---

## Benefits Realized

### Developer Experience
- ✅ **Single source of truth** - No config/prompt synchronization
- ✅ **Content-aware** - Word counts next to content requirements
- ✅ **Easy updates** - Change prompt file only
- ✅ **Clear ownership** - Domain experts own their prompts

### System Quality
- ✅ **Consistency** - All prompts follow same format
- ✅ **Transparency** - Word limits visible in prompt files
- ✅ **Maintainability** - Fewer files to update
- ✅ **Testability** - Simple verification checks

### Content Quality
- ✅ **Appropriate ranges** - Content-specific word counts
- ✅ **Natural variation** - Wide ranges encourage diversity
- ✅ **SEO compliance** - Character limits enforced
- ✅ **User expectations** - Predictable content length

---

## Related Policies

- **Prompt Purity Policy** (`PROMPT_PURITY_POLICY.md`) - Content instructions only in prompts
- **Content Instruction Policy** (`CONTENT_INSTRUCTION_POLICY.md`) - Separation of concerns
- **Template-Only Policy** (`TEMPLATE_ONLY_POLICY.md`) - Zero component-specific code

---

## Enforcement

**Grade**: F violation if word counts found in config files  
**Automated**: Pre-commit hooks verify prompt format  
**Review**: Required approval for prompt file changes  

---

## Domain Config Cleanup (December 29, 2025)

### Comprehensive Config Cleanup

**Policy Enforcement Milestone**: Achieved 100% compliance across all domain configs.

### Summary
- **Violations Found**: 42 across 4 domain config files
- **Lines Removed**: 323 total (-39.7% reduction)
- **Result**: 6/6 configs now policy-compliant

### Violations by Type

**1. Word Count Fields (33 violations)**
- **Location**: `domains/compounds/config.yaml`
- **Issue**: Each component had `default_length`, `min_length`, `max_length`
- **Resolution**: Removed all 11 components × 3 fields = 33 lines
- **Impact**: 225 → 194 lines (-13.8%)

**2. Embedded Prompts (9 violations)**

**settings/config.yaml** (177 lines removed, -71.2%)
- `component_summary_base`: Full prompt template for individual summaries
- `component_summaries`: Monolithic bulk generation template
- `settings_description`: Settings page description template

**materials/config.yaml** (105 lines removed, -50.5%)
- `micro`: Full micro prompt with voice and format instructions
- `faq`: Complete FAQ generation template
- `description`: Material subtitle generation template

**contaminants/config.yaml** (26 lines removed, -12.8%)
- `description`: Contamination description generation template

### Verification Results

```bash
# Word count fields: ZERO violations
grep -c "default_length|min_length|max_length" domains/*/config.yaml
# Result: 0 matches in all 4 configs ✅

# Embedded prompts: ZERO violations
grep -c "You are|TASK:" domains/*/config.yaml
# Result: 0 matches in all 4 configs ✅

# All prompt catalog entries exist
grep -c "^\s\+prompts/" prompts/registry/prompt_catalog.yaml
# Result: 51+ prompt entries verified ✅
```

### Policy Compliance Status

| Config File | Before | After | Status |
|-------------|--------|-------|--------|
| `generation/config.yaml` | 230 | 157 | ✅ Already compliant |
| `materials/image/config.yaml` | 50 | 50 | ✅ Already compliant |
| `compounds/config.yaml` | 225 | 194 | ✅ Cleaned |
| `settings/config.yaml` | 243 | 70 | ✅ Cleaned |
| `materials/config.yaml` | 198 | 98 | ✅ Cleaned |
| `contaminants/config.yaml` | 148 | 129 | ✅ Cleaned |
| **TOTAL** | **1,094** | **698** | **✅ 6/6 compliant** |

### Architectural Separation Achieved

**PROMPTS (prompt catalog `catalog.byPath` entries like `prompts/{domain}/*.txt`)**
- ✅ WHAT to generate (content instructions)
- ✅ HOW to format (style, structure, tone)
- ✅ Word count ranges (`WORD LENGTH: 50-150 words`)
- ✅ Examples and forbidden patterns

**CONFIGS (`domains/*/config.yaml`)**
- ✅ WHERE to find prompts (`prompt_template: "description.txt"`)
- ✅ WHEN to generate (`enabled: true`)
- ✅ System behavior (`extraction_strategy`, `display_name`)
- ✅ Zero content instructions

### Session Impact

**December 29, 2025 Cleanup Total:**
```
generation/config.yaml:        -73 lines
generation/ folder:         -1,712 lines
domains/data_loader.py:       -207 lines
domains/*/config.yaml:        -323 lines
───────────────────────────────────────
TOTAL REMOVED:              -2,315 lines (21.7% reduction)
```

### Testing

All 5 policy verification tests passing:

```bash
pytest tests/test_word_count_in_prompts_policy.py -v
# ✅ test_all_text_prompts_have_word_length
# ✅ test_prompt_word_length_coverage
# ✅ test_no_word_counts_in_generation_config
# ✅ test_no_word_counts_in_domain_configs
# ✅ test_word_length_format_valid
```

---

## Questions & Clarifications

**Q: Where do dynamic calculations happen?**  
A: They don't anymore (removed Dec 29, 2025). Prompt files contain COMPLETE range specifications (e.g., "50-150 words"). No additional variation applied. The wide ranges in prompts (3x-4x multipliers) already provide natural diversity.

**Q: What happened to `length_variation_range` and `word_count_variation`?**  
A: **REMOVED (Dec 29, 2025)**. These parameters created duplication and confusion. Prompts now define complete ranges with sufficient natural variation. For backward compatibility, legacy code defaults to 50% variation if accessing these parameters.

**Q: What about temperature and penalties?**  
A: Those remain in config/dynamic_config - they're API parameters, not content requirements.

**Q: Can I use config for quick experiments?**  
A: No. Update the prompt file. Config-based word counts create synchronization issues.

**Q: What if I need different lengths per domain?**  
A: Perfect - create domain-specific prompts with appropriate ranges. That's the point!

---

**Last Updated**: December 29, 2025  
**Policy Owner**: Architecture Team  
**Enforcement**: Automated + Code Review
