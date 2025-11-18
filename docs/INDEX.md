# Z-Beam Generator Documentation Index

**Last Updated**: November 17, 2025  
**Structure**: Numbered directories (01-09) for AI-friendly navigation

---

## 🎯 Start Here

**🗺️ NEW: Complete Navigation**: See [DOCUMENTATION_MAP.md](../DOCUMENTATION_MAP.md) for comprehensive directory structure and quick links.

---

## 📰 Recent Updates (November 2025)

### ✅ November 18: Realism Quality Gate Enforcement 🔥 **CRITICAL**
- Realism score (7.0/10 minimum) now enforced as rejection gate
- Blended learning: Winston (40%) + Realism (60%) feedback drives parameter adjustments
- AI tendency detection maps specific issues to parameter fixes
- **Grade**: B+ maintained with improved quality enforcement
- **Docs**: [08-development/REALISM_QUALITY_GATE.md](08-development/REALISM_QUALITY_GATE.md)

### ✅ November 17: Priority 1 Compliance Fixes
- Fixed RealismOptimizer import path
- Made SubjectiveEvaluator temperature configurable
- Removed non-existent fallback method calls
- **Grade**: C+ → B+ (85/100)
- **Docs**: [archive/2025-11/E2E_PROCESSING_EVALUATION_NOV17_2025.md](archive/2025-11/E2E_PROCESSING_EVALUATION_NOV17_2025.md)

### ✅ November 16: Composite Quality Scoring
- Implemented Winston (40%) + Realism (60%) composite weighting
- Adaptive threshold learning from 75th percentile
- Sweet spot analyzer uses composite scores
- **Docs**: [proposals/GENERIC_LEARNING_ARCHITECTURE.md](proposals/GENERIC_LEARNING_ARCHITECTURE.md)

### ✅ November 15: System Integrity Module
- ~20ms pre-generation validation
- 5 critical areas: config, parameters, API, readability, sweet spot
- **Docs**: [../processing/integrity/README.md](../processing/integrity/README.md)

---

## 🚀 Quick Start

| I want to... | Go to |
|--------------|-------|
| **Get started immediately** | [01-getting-started/installation.md](01-getting-started/installation.md) |
| **Set up API keys** | [01-getting-started/api-configuration.md](01-getting-started/api-configuration.md) |
| **Fix API issues** | [07-api/error-handling.md](07-api/error-handling.md) |
| **Generate content** | [04-operations/content-generation.md](04-operations/content-generation.md) |
| **Understand architecture** | [02-architecture/system-requirements.md](02-architecture/system-requirements.md) |
| **View CLI commands** | [09-reference/cli-commands.md](09-reference/cli-commands.md) |
| **Troubleshoot issues** | [01-getting-started/troubleshooting.md](01-getting-started/troubleshooting.md) |

---

## 📖 Documentation Structure

### 01-getting-started/
**Purpose**: First-time setup and quick start guides  
**For**: New users, AI assistants learning the system

- `installation.md` - Environment setup and dependencies
- `api-configuration.md` - API keys and provider setup
- `validation.md` - Health checks and system validation
- `troubleshooting.md` - Common issues and solutions
- `ai-assistants.md` - Guide for AI development assistants
- `processing-quickstart.md` - Processing pipeline quick start

### 02-architecture/
**Purpose**: System design and technical architecture  
**For**: Developers, architects, contributors

- `system-requirements.md` - E2E system requirements (7 critical rules)
- `processing-pipeline.md` - Unified content generation pipeline
- `data-architecture.md` - Data flow and range propagation
- `component-architecture.md` - Component system design
- `fail-fast-principles.md` - Design philosophy and constraints
- `parameter-system.md` - Parameter architecture and flow
- Plus 29 more architecture documents

### 03-components/
**Purpose**: Individual component documentation  
**For**: Component developers, maintainers

**Note**: Component-specific docs remain in `/components/` directory for proximity to code.

See `/components/` for:
- Text generation (`text/`)
- Frontmatter (`frontmatter/`)
- Settings (`settings/`)
- Other components

### 04-operations/
**Purpose**: Day-to-day usage and workflows  
**For**: Content creators, operators

- `content-generation.md` - Generate content for materials
- `batch-operations.md` - Batch content generation
- `deployment.md` - Deployment procedures
- `maintenance.md` - System maintenance tasks
- Plus 10 more operational guides

### 05-data/
**Purpose**: Data architecture and validation  
**For**: Data maintainers, QA

- `data-storage-policy.md` - Data storage rules (Materials.yaml as truth)
- `zero-null-policy.md` - Zero null value policy
- `data-architecture.md` - Complete data structure
- `category-refactoring-complete.md` - Category system (8 modular files)
- `data-completion-action-plan.md` - Path to 100% data coverage
- Plus 13 more data guides

### 06-ai-systems/
**Purpose**: AI/ML systems and learning  
**For**: ML engineers, quality analysts

- `opening-variation.md` - Opening variation system
- `post-generation-checks.md` - Post-generation integrity checks
- `self-learning-prompts.md` - Self-learning prompt system
- `batch-subtitle-strategy.md` - Winston batch subtitle strategy
- **Scoring Module** (`processing/evaluation/SCORING_MODULE_README.md`) - Comprehensive quality assessment and parameter correlation

### 07-api/
**Purpose**: External API integration  
**For**: Developers, troubleshooters

- `error-handling.md` - API error handling and Winston SSL fixes
- `grok-api-limitations.md` - Grok API known limitations
- `subjective-evaluation-api-fix.md` - Subjective evaluation fixes

### 08-development/
**Purpose**: Development and contribution  
**For**: Contributors, developers

- `LEARNED_EVALUATION_PROPOSAL.md` - 🎯 **PROPOSAL** Learned subjective evaluation system (Nov 18, 2025)
- `PROMPT_PURITY_POLICY.md` - 🔥 **NEW** Zero prompt text in generators (Nov 18, 2025)
- `REALISM_QUALITY_GATE.md` - 🔥 **NEW** Realism quality gate policy (mandatory 7.0/10 minimum)
- `chain-verification.md` - Chain verification guide
- `database-parameter-priority.md` - Database-first parameter policy
- `sweet-spot-analyzer.md` - Statistical parameter optimization
- Plus 6 more development guides

### 09-reference/
**Purpose**: Complete references and lookups  
**For**: All users for quick lookup

- `cli-commands.md` - Complete CLI reference
- `content-instructions.md` - Content instruction policy
- `property-categories.md` - Property categorization
- `property-terminology.md` - Property terminology reference
- Plus 14 more reference documents

---

## 📚 Archive

### archive/2025-11/
**Historical Documentation**: November 2025 cleanup

- `evaluations/` - 7 E2E evaluation reports
- `completions/` - 13 completion reports
- `sessions/` - 5 session change logs
- `parameters/` - 5 parameter system docs
- `phases/` - 3 cleanup phase reports
  - PHASE2_CLEANUP_COMPLETE.md - Documentation restructuring (Nov 16)
  - PHASE3_CODE_CLEANUP_ANALYSIS.md - Code health analysis (Nov 16)

See [archive/2025-11/README.md](archive/2025-11/README.md) for complete archive index.

---

## 🔍 Finding Documentation

### By Topic
1. **Installation/Setup** → `01-getting-started/`
2. **How it works** → `02-architecture/`
3. **Specific component** → `03-components/` or `/components/`
4. **How to use** → `04-operations/`
5. **Data structure** → `05-data/`
6. **AI features** → `06-ai-systems/`
7. **API issues** → `07-api/`
8. **Contributing** → `08-development/`
9. **Quick lookup** → `09-reference/`

### By Question
- "How do I install?" → `01-getting-started/installation.md`
- "How do I fix API errors?" → `07-api/error-handling.md`
- "How does data flow?" → `02-architecture/data-architecture.md`
- "What commands exist?" → `09-reference/cli-commands.md`
- "How do I generate content?" → `04-operations/content-generation.md`
- "What are the rules?" → `02-architecture/system-requirements.md`

---

## 📊 Documentation Stats

**Total Active Docs**: ~109 markdown files  
**Archived Docs**: 33 files in archive/2025-11/  
**Last Major Cleanup**: November 16, 2025 (Phase 1-3)  
**Structure**: Numbered directories (01-09) for predictable navigation

---

## 🔄 Recent Updates

### Scoring Module (November 16, 2025)
- ✅ Created unified Scoring Module for quality assessment
- ✅ GranularParameterCorrelator: Fine-grained analysis of 20+ parameters
- ✅ CompositeScorer: Unified quality metric (Winston + Subjective + Readability)
- ✅ Database enhancements: Foreign keys linking evaluations to parameters
- ✅ Statistical rigor: P-values, confidence intervals, relationship detection
- ✅ Added numpy and scipy dependencies for scientific computing

### Phase 1-3 Cleanup (November 16, 2025)
- ✅ Root consolidation: 32 → 4 files (-88%)
- ✅ Documentation restructure: Created 01-09 numbered directories
- ✅ Archive organization: 33 files archived in 2025-11/
- ✅ Code health analysis: Grade A, zero critical issues

### Documentation Improvements
- Clear numbered hierarchy (01-09)
- Purpose-driven categorization
- Reduced navigation depth (2-3 clicks)
- AI-friendly predictable structure
- Comprehensive archive with policy

---

## 🆘 Quick Help

**Can't find something?**
1. Check `QUICK_REFERENCE.md` for common solutions
2. Look in relevant numbered directory (01-09)
3. Search archive/ for historical docs
4. Check component-specific docs in `/components/`

**Documentation issues?**
- File an issue describing what's missing
- Reference this INDEX.md for structure
- Check archive policy before moving files

---

**Navigation Tip**: Numbers indicate recommended reading order for new users (01 → 09)  
**AI Assistants**: Start with `01-getting-started/ai-assistants.md`
