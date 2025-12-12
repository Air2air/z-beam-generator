# Documentation Map - Z-Beam Generator

**🗺️ Master Navigation for All Documentation**  
**Last Updated**: November 22, 2025  
**For**: AI Assistants, Developers, Contributors, and Users  
**Recent Cleanup**: 52 implementation docs archived (streamlined from 120 → 70 files)

---

## 🎯 Start Here Based on Your Goal

| I Want To... | Go Here |
|--------------|---------|
| **Get started immediately** | `README.md` → `docs/01-getting-started/` |
| **AI Assistant Guide (30-sec nav)** | `docs/08-development/AI_ASSISTANT_GUIDE.md` |
| **Understand the system** | `.github/copilot-instructions.md` (AI assistants) |
| **Generate content** | `.github/COPILOT_GENERATION_GUIDE.md` |
| **Find answers fast** | `docs/QUICK_REFERENCE.md` |
| **Browse all docs** | `docs/INDEX.md` |
| **Fix issues** | `TROUBLESHOOTING.md` |
| **Learn architecture** | `docs/02-architecture/` |
| **Review recent changes** | `docs/archive/2025-11/` (52 archived docs) |
| **Image generation system** | `IMAGE_CENTRALIZATION_PLAN_NOV27_2025.md` |

---

## 📁 Documentation Structure

### Root Level (Priority Documents)
```
/
├── README.md                           # Project overview & features
├── DOCUMENTATION_MAP.md               # This file - master navigation
├── QUICK_START.md                     # Fast setup guide
├── TROUBLESHOOTING.md                 # Common issues & solutions
├── GROK_QUICK_REF.md                  # 🤖 Critical policies (TIER system)
├── IMAGE_CENTRALIZATION_PLAN_NOV27_2025.md  # Image generation architecture
├── .github/
│   ├── copilot-instructions.md       # 🤖 AI assistant guidelines (PRIMARY)
│   └── COPILOT_GENERATION_GUIDE.md   # Content generation commands
```

### Main Documentation (`/docs/`)
```
docs/
├── INDEX.md                           # Comprehensive doc index
├── QUICK_REFERENCE.md                 # Fast problem resolution
├── README.md                          # Documentation overview
│
├── 01-getting-started/               # Setup & installation
│   ├── INSTALLATION.md
│   ├── SETUP_GUIDE.md
│   ├── VALIDATION.md
│   ├── ai-assistants.md
│   └── processing-quickstart.md
│
├── 02-architecture/                   # System design
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── PROCESSING_WORKFLOW.md
│   ├── DATA_ARCHITECTURE.md
│   ├── COMPONENT_ARCHITECTURE.md
│   ├── COMPONENT_DISCOVERY.md        # NEW: Component type discovery
│   └── [29 more architecture docs]
│
├── 03-components/                     # Component-specific docs
│   ├── README.md
│   ├── text/                          # Text generation component
│   │   └── README.md
│   └── [other component docs]
│
├── 04-operations/                     # Daily operations
│   ├── content-generation.md
│   ├── BATCH_OPERATIONS.md
│   ├── deployment.md
│   └── MAINTENANCE.md
│
├── 05-data/                          # Data architecture
│   ├── DATA_STORAGE_POLICY.md
│   ├── ZERO_NULL_POLICY.md
│   ├── DATA_ARCHITECTURE.md
│   └── data-completion-action-plan.md
│
├── 06-ai-systems/                    # AI/ML systems
│   ├── opening-variation.md
│   ├── post-generation-checks.md
│   └── self-learning-prompts.md
│
├── 07-api/                           # External APIs
│   ├── ERROR_HANDLING.md
│   ├── GROK_API_LIMITATIONS.md
│   └── SUBJECTIVE_EVALUATION_API_FIX.md
│
├── 08-development/                    # Development guidelines
│   ├── HARDCODED_VALUE_POLICY.md     # 🔥 CRITICAL: No hardcoded values
│   ├── CONTENT_INSTRUCTION_POLICY.md # 🔥 CRITICAL: Prompts-only content rules
│   ├── WINSTON_ONLY_MODE.md
│   ├── SCORE_DISPLAY_STANDARDS.md
│   └── [17 more development docs]
│
├── 09-reference/                      # Reference materials
│   ├── cli-commands.md
│   ├── GLOSSARY.md
│   └── FAQ.md
│
├── decisions/                         # Architecture Decision Records (ADRs)
│   ├── ADR-001-dual-voice-enforcement.md
│   ├── ADR-002-fail-fast-vs-runtime-recovery.md
│   ├── ADR-003-exploration-rate-reproducibility.md
│   ├── ADR-004-content-instructions-location.md
│   ├── ADR-005-dynamic-threshold-learning.md
│   └── ADR-007-universal-humanness-layer.md  # 🔥 NEW (Nov 20, 2025)
│
└── archive/                           # Historical documents
    └── 2025-11/                       # November 2025 archives
        ├── E2E_PROCESSING_EVALUATION_NOV17_2025.md
        ├── PRIORITY1_UPDATES_COMPLETE.md
        └── test-reports/              # Test completion reports
```

### Generation Code (`/generation/`)
```
generation/
├── core/                              # Core generation
│   ├── evaluated_generator.py         # Single-pass generator with quality evaluation
│   ├── generator.py                   # Base generator
│   └── batch_generator.py             # Batch processing
├── config/                            # Configuration
│   ├── config_loader.py               # Config loading
│   └── dynamic_config.py              # Dynamic calculations
└── [other generation modules]
```

### Processing Documentation (`/processing/`)
```
processing/
├── evaluation/
│   └── SCORING_MODULE_README.md      # Composite quality scoring
└── [other processing docs]
```

---

## 📂 Project Structure (Updated December 2025)

```
z-beam-generator/
├── domains/                # Domain-specific code & prompts
│   ├── materials/          # Materials domain (text + image prompts)
│   │   ├── prompts/        # Component prompts: micro.txt, faq.txt, material_description.txt
│   │   └── image/          # Image generation for materials
│   ├── settings/           # Settings domain
│   │   └── prompts/        # settings_description.txt, component_summaries.txt
│   ├── contaminants/       # Contaminants domain
│   └── data_orchestrator.py  # Cross-domain data coordination
├── generation/             # Core generation system
│   ├── core/               # Generators (quality_gated, batch, simple)
│   ├── config/             # Dynamic config, config loader
│   └── integrity/          # Integrity checks
├── learning/               # Learning/optimization modules
│   ├── humanness_optimizer.py
│   ├── realism_optimizer.py
│   ├── sweet_spot_analyzer.py
│   └── threshold_manager.py
├── postprocessing/         # Post-generation processing
├── shared/                 # Shared utilities
│   ├── text/               # Text processing utilities
│   └── image/              # Image processing utilities
├── scripts/                # Organized scripts
│   ├── batch/              # Batch processing scripts
│   ├── research/           # Research/data population scripts
│   ├── migrations/         # Migration scripts
│   ├── tools/              # Utility scripts
│   ├── analysis/           # Analysis scripts
│   ├── testing/            # Testing scripts
│   ├── maintenance/        # Maintenance scripts
│   └── operations/         # Operational scripts
├── data/                   # Data files (YAML)
├── frontmatter/            # Generated frontmatter files
├── tests/                  # Test suite
└── docs/                   # Documentation
```

---

## 🤖 For AI Assistants

### Primary Reference (READ FIRST)
**`.github/copilot-instructions.md`** - Your complete guide
- Core principles (no mocks, no hardcoded values, fail-fast)
- Recent updates (November 2025)
- Code modification rules
- Documentation compliance checklist
- Emergency recovery procedures

### Quick Problem Resolution
**`docs/QUICK_REFERENCE.md`**
- Direct problem → solution mappings
- File location quick map
- Common user questions with immediate answers
- Essential commands

### When to Check Documentation
**ALWAYS before implementing:**
1. Search `docs/` for existing guidance
2. Check policy docs:
   - `HARDCODED_VALUE_POLICY.md` - Before adding ANY values
   - `CONTENT_INSTRUCTION_POLICY.md` - Before touching prompts
   - `COMPONENT_DISCOVERY.md` - Before adding/modifying components
   - `DATA_STORAGE_POLICY.md` - Before data operations

### Red Flags Requiring Doc Check
- ⚠️ Adding thresholds → Check for dynamic calculation requirements
- ⚠️ Adding configuration values → Check config architecture docs
- ⚠️ Modifying validation → Check validation strategy docs
- ⚠️ Adding new component → Check component discovery policy
- ⚠️ Changing data flow → Check data storage policy
- ⚠️ Adding hardcoded values → STOP - check hardcoded value policy

---

## 📊 November 2025 Key Updates

### Universal Humanness Layer (Nov 20) 🔥 **NEW**
- **Dual-feedback learning**: Winston DB + Subjective patterns
- **Dynamic instructions**: Strictness progression (1-5 levels)
- **Integration**: Quality-gated retry loop with parameter adjustments
- **Grade**: A+ (98/100) - Production ready
- **Docs**: `docs/decisions/ADR-007-universal-humanness-layer.md`
- **Files**: `learning/humanness_optimizer.py`, `prompts/system/humanness_layer.txt`

### Priority 1 Compliance Fixes (Nov 17)
- **Fixed**: RealismOptimizer import path
- **Fixed**: SubjectiveEvaluator hardcoded temperature
- **Fixed**: Non-existent fallback method calls
- **Grade**: C+ → B+ (85/100)
- **Docs**: `docs/archive/2025-11/E2E_PROCESSING_EVALUATION_NOV17_2025.md`
- **Tests**: `tests/test_priority1_fixes.py` (10/10 passing)

### Frontmatter Generation Architecture (Nov 27) 🔥 **NEW**
- **Documentation**: Complete domain-agnostic frontmatter system
  - `docs/architecture/FRONTMATTER_GENERATION_ARCHITECTURE.md` (1,064 lines)
  - All domains export similar structures (author, content, metadata, properties)
- **Minimal Domain Architecture Proposal**: 82% code reduction plan
  - `docs/architecture/MINIMAL_DOMAIN_ARCHITECTURE_PROPOSAL.md` (600+ lines)
  - Universal generator + 12 prompt files = 853 → 150 lines of code
  - Migration plan: 9.5 hours, reversible approach
- **Author Voice Coverage Verification**: Comprehensive coverage audit
  - `AUTHOR_VOICE_COVERAGE_VERIFICATION_NOV27_2025.md` (complete analysis)
  - ✅ VERIFIED: 100% text coverage - ALL text has author voice
  - ✅ CONFIRMED: Proper pipeline integration in BaseFrontmatterGenerator
  - Grade: A+ (100/100) - Complete coverage verified
  - Mandatory post-processing: AI detection + author voice enhancement
  - Domain-specific prompts as primary user interface
  - Complete workflow examples for materials, contaminants, applications, regions
- **Proposal**: Minimal domain architecture (82% code reduction)
  - `docs/architecture/MINIMAL_DOMAIN_ARCHITECTURE_PROPOSAL.md` (600+ lines)
  - Replace 4 generators (853 lines) with 1 universal generator (150 lines)
  - Configuration-driven via config.yaml per domain
  - Creates 12 new domain-specific prompt files
  - Migration: ~9.5 hours | Status: 🔄 Ready for review

### Composite Quality Scoring (Nov 16)
- Winston (60%) + Subjective (30%) + Readability (10%)
- Adaptive threshold learning
- Sweet spot analyzer integration
- **Docs**: `docs/proposals/GENERIC_LEARNING_ARCHITECTURE.md`

### Content Instruction Policy (Nov 14)
- Content instructions ONLY in `prompts/*.txt`
- Technical mechanisms ONLY in `processing/`
- **Docs**: `docs/prompts/CONTENT_INSTRUCTION_POLICY.md`

### Component Discovery (Nov 16)
- Components defined dynamically from `prompts/*.txt` files
- No hardcoded component types in code
- **Docs**: `docs/architecture/COMPONENT_DISCOVERY.md`

---

## 📖 Critical Policy Documents

These policies are **MANDATORY** reading before related work:

1. **HARDCODED_VALUE_POLICY.md** (`docs/08-development/`)
   - No hardcoded temperatures, thresholds, penalties
   - Use config or dynamic calculation
   - Enforcement via integrity checker

2. **CONTENT_INSTRUCTION_POLICY.md** (`docs/08-development/`)
   - Content instructions ONLY in prompts/
   - NO content logic in processing code
   - 5 automated tests enforce compliance

3. **DATA_STORAGE_POLICY.md** (`docs/05-data/`)
   - Materials.yaml is single source of truth
   - All generation happens there
   - Frontmatter is trivial export only

4. **COMPONENT_DISCOVERY.md** (`docs/02-architecture/`)
   - Component types discovered from prompts/*.txt
   - No hardcoded components in code
   - Generic, dynamic component handling

5. **ZERO_NULL_POLICY.md** (`docs/05-data/`)
   - Null ranges are correct by design
   - Range propagation from categories
   - Complete data completion strategy

---

## 🔍 Finding Specific Information

### By Topic
| Topic | Location |
|-------|----------|
| **API Issues** | `docs/07-api/ERROR_HANDLING.md` |
| **Winston AI** | `docs/08-development/WINSTON_ONLY_MODE.md` |
| **Data Gaps** | `docs/05-data/data-completion-action-plan.md` |
| **Testing** | `tests/` + component-specific `tests/` |
| **Configuration** | `processing/config.yaml` + `docs/configuration/` |
| **Commands** | `docs/09-reference/cli-commands.md` |
| **Recent Changes** | `docs/archive/2025-11/` |
| **Proposals** | `docs/proposals/` |

### By File Type
| Need | Extension | Primary Location |
|------|-----------|------------------|
| **Python Code** | `.py` | `generation/`, `export/`, `shared/`, `domains/` |
| **Configuration** | `.yaml`, `.json` | `data/`, `processing/config.yaml` |
| **Documentation** | `.md` | `docs/`, component `docs/` folders |
| **Tests** | `test_*.py` | `tests/`, component `tests/` |
| **Prompts** | `.txt` | `prompts/` |
| **Data** | `.yaml` | `data/materials/`, `data/authors/`, etc. |
| **Batch Scripts** | `.sh` | `scripts/`, `batch/` |
| **Logs** | `.log` | `logs/`, `output/` |
| **Progress Trackers** | `.txt` | `progress/`, `logs/` |
| **Coverage Lists** | `.txt` | `coverage/`, `tests/` |
| **Requirements** | `requirements.txt` | root or `config/` |

---

## 🎓 Learning Paths

### New to the Project?
1. `README.md` - Understand what this is
2. `QUICK_START.md` - Get it running
3. `docs/01-getting-started/INSTALLATION.md` - Detailed setup
4. `docs/02-architecture/SYSTEM_ARCHITECTURE.md` - How it works
5. `.github/copilot-instructions.md` - Development rules

### AI Assistant Onboarding?
1. `.github/copilot-instructions.md` - PRIMARY REFERENCE
2. `docs/QUICK_REFERENCE.md` - Fast answers
3. `docs/INDEX.md` - Full navigation
4. Policy docs in `docs/08-development/` - Rules
5. `docs/archive/2025-11/` - Recent changes

### Contributing Code?
1. `.github/copilot-instructions.md` - Coding rules
2. `docs/08-development/` - All policies
3. `docs/03-components/` - Component documentation
4. `tests/test_priority1_fixes.py` - Compliance examples
5. `generation/integrity/integrity_checker.py` - Validation

### Understanding Data Flow?
1. `docs/05-data/DATA_STORAGE_POLICY.md` - Data rules
2. `docs/02-architecture/DATA_ARCHITECTURE.md` - Structure
3. `docs/05-data/ZERO_NULL_POLICY.md` - Null handling
4. `data/materials/Materials.yaml` - Single source of truth
5. `data/materials/Categories.yaml` - Category ranges

---

## 🔗 External Resources

### APIs Used
- **Grok AI**: Content generation
- **DeepSeek**: Material property research
- **Winston AI**: AI detection and scoring

### Key Repositories
- **Main Repo**: Air2air/z-beam-generator
- **Branch**: main
- **CI/CD**: GitHub Actions

---

## 🆘 Getting Help

### Quick Answers
1. Check `docs/QUICK_REFERENCE.md`
2. Search this documentation map
3. Check `TROUBLESHOOTING.md`

### Detailed Investigation
1. Review relevant policy doc
2. Check `docs/INDEX.md` for related docs
3. Search component-specific documentation
4. Review `docs/archive/2025-11/` for recent changes

### For AI Assistants
1. Always check `.github/copilot-instructions.md` first
2. Search documentation before asking user
3. Follow Documentation Compliance Checklist
4. When unclear, ASK user instead of guessing

---

## 📝 Maintenance Notes

### When Adding New Documentation
1. Add entry to this map
2. Update `docs/INDEX.md`
3. Update `.github/copilot-instructions.md` if policy-related
4. Cross-reference from related documents

### When Organizing Files
1. Follow explicit file type rules in `.github/copilot-instructions.md` (see "File Organization & Root Cleanliness Policy")
2. Move batch scripts, logs, progress trackers, and coverage lists to their designated folders
3. Keep only essential entry points and navigation docs in root
4. Update this map and navigation docs after any major reorganization

### When Archiving Documents
1. Move to appropriate `docs/archive/YYYY-MM/` directory
2. Update references in this map
3. Add redirect note in original location if necessary

### When Updating Policies
1. Update policy document
2. Update `.github/copilot-instructions.md`
3. Update this map with "Last Updated" date
4. Update relevant tests if compliance-related

---

**Last Review**: December 3, 2025  
**Next Review**: January 2026 (or when major changes occur)  
**Maintainer**: See git log for recent contributors
