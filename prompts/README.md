# Text Generation Prompts

**Central repository for ALL text generation prompts used by the Z-Beam system.**

---

## 📁 Organized Folder Structure

```
prompts/                           # Root-level prompts directory
├── README.md                      # This file
│
├── components/                    # WHAT to generate (task specifications)
│   ├── README.md                  # Component prompt documentation
│   ├── subtitle.txt               # Subtitle generation (15 words)
│   ├── caption.txt                # Caption generation (25 words)
│   ├── description.txt            # Description generation (150 words)
│   ├── faq.txt                    # FAQ answer generation (100 words)
│   └── troubleshooter.txt         # Troubleshooting guide (120 words)
│
├── rules/                         # WHAT TO AVOID (universal constraints)
│   ├── README.md                  # Rule system documentation
│   ├── anti_ai_rules.txt          # AI pattern avoidance rules
│   └── grammar_rules.txt          # Grammar and linguistic patterns
│
├── personas/                      # HOW to write (author voice patterns)
│   ├── README.md                  # Persona system documentation
│   ├── united_states.yaml         # US author: formal academic style
│   ├── italy.yaml                 # Italian author: technical with EFL traits
│   ├── indonesia.yaml             # Indonesian author: natural accessibility
│   └── taiwan.yaml                # Taiwanese author: concise technical
│
└── archive/                       # Deprecated/legacy files (reference only)
    ├── README.md                  # Archive documentation
    ├── voice_rules.txt            # Deprecated: Replaced by personas/
    ├── component_specs.yaml       # Deprecated: Violates content policy
    └── unified_template.txt       # Legacy: Old template system
```

**Separation of Concerns**:
- **components/** = Task specifications (WHAT to generate)
- **rules/** = Universal constraints (WHAT TO AVOID)
- **personas/** = Author voices (HOW to write)
- **archive/** = Deprecated files (DO NOT USE)

---

## 🔄 Two Workflows

### 1. New Content Generation ✨

**Use Case**: Generate brand new subtitles, captions, descriptions, etc.

**Command**:
```bash
# Generate new subtitle for a material
python3 run.py --material "Aluminum" --component subtitle

# Or ask GitHub Copilot:
"Generate subtitle for Aluminum"
```

**Flow**:
1. Copilot reads component prompt from `prompts/components/` (e.g., `subtitle.txt`)
2. Loads material facts from `data/materials/Materials.yaml`
3. Gets author voice from material's `author.id` (loads from `prompts/personas/`)
4. Injects shared rules from `prompts/rules/` (`anti_ai_rules.txt`, `grammar_rules.txt`)
5. Calls processing system (Orchestrator → PromptBuilder → API → Detection)
6. Saves result to `Materials.yaml`

**Best for**: New materials, missing content, first-time generation

---

### 2. Content Regeneration 🔄

**Use Case**: Refresh existing subtitles/captions with better quality or updated rules

**Command**:
```bash
# Test mode (10 materials, no save)
python3 scripts/processing/regenerate_subtitles_with_processing.py --test

# Full regeneration (all materials with backup)
python3 scripts/processing/regenerate_subtitles_with_processing.py

# Skip frontmatter deployment
python3 scripts/processing/regenerate_subtitles_with_processing.py --skip-deploy
```

**Flow**:
1. Loads all materials from `Materials.yaml`
2. For each material:
   - Extracts current subtitle (shows comparison)
   - Generates new version via processing system
   - Updates `Materials.yaml` in memory
   - Tracks metadata (AI score, attempts, word count, generation timestamp)
3. Saves `Materials.yaml` (with timestamped backup like `Materials_backup_20251103_143022.yaml`)
4. Runs `--deploy` to export to frontmatter

**Best for**: Quality improvements, applying updated AI rules, consistency fixes

**Flags**:
- `--test` - Process only 10 random materials, don't save (dry run)
- `--skip-deploy` - Save Materials.yaml but don't export to frontmatter

**Why Regenerate?**
- Apply improved anti-AI rules to old content
- Update voice patterns after persona refinement
- Improve consistency across all materials
- Fix subtitles that fail current quality standards
- Refresh content generated with older prompts

**Example Output**:
```
1/132. Aluminum (Metal)
   Author: 2
   Current: Lightweight metal valued in aerospace, automotive, and construction industries
   ✅ New: Lightweight metal with 2.7 g/cm³ density enabling aerospace applications
   📊 AI Score: 0.000, Attempts: 1, Words: 14
```

---

## 🎯 Copilot Workflow (Quick Commands)

Ask Copilot to generate content directly:

```
"Generate subtitle for Aluminum"
"Generate caption for Steel"  
"Generate description for Granite"
```

**Note**: Author voice is automatically determined by the material's assigned author in Materials.yaml (cannot be overridden).

---

## 📝 Component Files

Located in `prompts/components/`:

| File | Purpose | Length | Key Feature |
|------|---------|--------|-------------|
| `subtitle.txt` | Short intro | 15 words | No period at end |
| `caption.txt` | Microscopy description | 25 words | Include 1-2 measurements |
| `description.txt` | Comprehensive overview | 150 words | Multiple paragraphs |
| `faq.txt` | Answer questions | 100 words | Conversational, use "you" |
| `troubleshooter.txt` | Solve problems | 120 words | Numbered steps |

Each file uses template variables:
- `{length}` - Target word count (from `processing/config.yaml`)
- `{topic}` - Material name
- `{facts}` - Material properties and data
- `{voice_instructions}` - Injected from author persona YAML
- `{anti_ai_rules}` - Injected from `prompts/rules/anti_ai_rules.txt`

**See**: `prompts/components/README.md` for detailed component documentation

---

## 🛠️ Quick Edits

**Want better subtitles?**  
→ Edit `prompts/components/subtitle.txt`

**Want stricter AI avoidance?**  
→ Edit `prompts/rules/anti_ai_rules.txt`

**Want different author voice?**  
→ Edit persona YAML in `prompts/personas/` (e.g., `united_states.yaml`)

**Changes apply immediately** - no deployment needed!

---

## 📊 Component Configuration

From `processing/config.yaml` (component_lengths):

- **subtitle**: 15 words, no period, focus on unique characteristics
- **caption**: 25 words, include measurements, technical but accessible
- **description**: 150 words (140-160 range), comprehensive coverage
- **faq**: 100 words (80-120 range), conversational and helpful
- **troubleshooter**: 120 words (100-140 range), methodical solutions

**Note**: Word counts defined in config, content instructions in component prompts.

---

## ✅ Quality Metrics

- **AI Detection**: 0.000 consistently (ensemble_advanced method)
- **Success Rate**: 100% on first attempt
- **Response Time**: ~3.7s average per generation
- **Method**: 70% advanced detection + 30% simple patterns

---

## 🚫 Anti-AI Instructions

From **prompts/rules/anti_ai_rules.txt** - Critical rules to avoid AI detection:

1. **No formulaic structures** (e.g., "X does Y while preserving Z")
2. **No abstract transitions** ("results suggest", "data indicate")
3. **Vary opening words** and sentence patterns
4. **Mix sentence lengths** (short punchy + longer explanatory)
5. **Add specific details** and concrete examples
6. **Use natural flow** (conversational, not robotic)

These instructions are embedded in every prompt to ensure AI-resistant output.

**See**: `prompts/rules/README.md` for complete rule documentation

---

## 🎤 Voice Profiles

From **prompts/personas/*.yaml** - 4 ESL author voices:

- **United States** (`united_states.yaml`): Formal academic, balanced active-passive
- **Italy** (`italy.yaml`): Technical precision with subtle EFL traits (0.3-0.5 per para)
- **Indonesia** (`indonesia.yaml`): Natural accessibility with light Southeast Asian markers
- **Taiwan** (`taiwan.yaml`): Concise technical with East Asian formal patterns

Voice profiles are automatically applied based on material's assigned author.

**See**: `prompts/personas/README.md` for persona system documentation

---

## 🔗 Related Files

### Processing System
- `processing/orchestrator.py` - Main coordinator (5-attempt retry, AI detection)
- `processing/generation/prompt_builder.py` - Prompt assembly from templates
- `processing/voice/store.py` - Author voice profile loading
- `processing/detection/ensemble.py` - Composite AI detection (70%+30%)
- `processing/detection/ai_detection.py` - Advanced pattern detection
- `processing/detection/patterns/ai_detection_patterns.txt` - Technical detection patterns

### Configuration
- `processing/config.yaml` - System-wide configuration (component lengths, API settings)

### Testing
- `processing/tests/test_e2e_pipeline.py` - Full pipeline validation (7 tests)

---

## 📝 Notes

1. **Organized by function** - components/, rules/, personas/, archive/ separation
2. **Changes propagate immediately** - No deployment needed for prompt updates
3. **Test after modifications** - Run E2E tests to verify changes
4. **Regeneration creates backups** - Materials.yaml backed up before save
5. **Component discovery** - System automatically scans `prompts/components/*.txt`

---

## 🚀 Quick Reference

**Generate new content**:
```bash
python3 run.py --material "Aluminum" --component subtitle
```

**Regenerate existing content**:
```bash
# Test with 10 materials (dry run)
python3 scripts/processing/regenerate_subtitles_with_processing.py --test

# Full regeneration with backup
python3 scripts/processing/regenerate_subtitles_with_processing.py
```

**Test E2E pipeline**:
```bash
python3 processing/tests/test_e2e_pipeline.py
```

**Most important directories**:
1. `prompts/components/` - Component task specifications (subtitle, caption, etc.)
2. `prompts/rules/` - Universal constraints (anti-AI rules, grammar rules)
3. `prompts/personas/` - Author voice profiles (4 ESL authors)
4. `processing/config.yaml` - Component lengths and system configuration

**See subdirectory READMEs for detailed documentation**:
- `prompts/components/README.md` - Component prompt system
- `prompts/rules/README.md` - Rule system documentation
- `prompts/personas/README.md` - Persona system guide
- `prompts/archive/README.md` - Deprecated files reference

