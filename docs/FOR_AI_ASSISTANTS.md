# Documentation for AI Assistants

**Purpose**: Quick navigation guide for AI assistants (GitHub Copilot, Grok, Claude, etc.)  
**Last Updated**: December 12, 2025

---

## 🎯 Your Primary Resources (In Order)

### 1. **Comprehensive Guide** ⭐ START HERE
[`.github/copilot-instructions.md`](../.github/copilot-instructions.md) (1,398 lines)

**What's inside**:
- 🚀 **30-second quick start navigation** - Lines 1-100
- 🚦 **TIER 1-3 rule priorities** - Lines 200-250 (critical → quality → evidence)
- 📋 **Mandatory 8-step pre-change checklist** - Lines 300-400
- 🚫 **Critical failure patterns to avoid** - Lines 100-200 (Grade F violations)
- 🔒 **Protected files policy** - Lines 450-500 (require permission)
- 📖 **14 core principles** - Lines 500-800 (architectural rules)
- 🔥 **Recent critical updates** - Lines 50-100 (Nov-Dec 2025)

**Read this BEFORE any code change.**

---

### 2. **Content Generation**
[`.github/COPILOT_GENERATION_GUIDE.md`](../.github/COPILOT_GENERATION_GUIDE.md)

Step-by-step guide for generating:
- Material descriptions
- Micros (captions)
- FAQs
- Settings descriptions
- All other text components

**When to use**: User requests "generate", "create content", "write description"

---

### 3. **30-Second Navigation**
[`docs/08-development/AI_ASSISTANT_GUIDE.md`](08-development/AI_ASSISTANT_GUIDE.md)

Quick lookup for:
- Common tasks → direct links
- Policy summaries with TIER priorities
- Pre-change checklist (condensed version)
- Emergency recovery procedures

**When to use**: Need fast lookup, already familiar with system

---

### 4. **Fast Problem Resolution**
[`docs/QUICK_REFERENCE.md`](QUICK_REFERENCE.md)

Immediate answers for:
- API errors and configuration issues
- Data problems and validation failures
- Common bugs and quick fixes
- Recent updates and critical changes

**When to use**: Something's broken, need immediate fix

---

### 5. **System Architecture**
[`docs/SYSTEM_INTERACTIONS.md`](SYSTEM_INTERACTIONS.md)

Understanding side effects:
- What changes affect what
- Data flow diagrams
- Component dependencies
- Cascading effects

**When to use**: Before making ANY architecture change

---

## 🚦 Critical Rules Summary

### TIER 1: System-Breaking (Will cause failures)
1. ❌ **NO mocks/fallbacks in production code** (tests OK)
   - Violates fail-fast architecture
   - System MUST fail immediately if dependencies missing
2. ❌ **NO hardcoded values/defaults** (use config/dynamic calc)
   - All thresholds, temperatures, penalties from config or dynamic calculation
3. ❌ **NO rewriting working code** (minimal surgical fixes only)
   - Preserve working functionality, make targeted changes only

### TIER 2: Quality-Critical (Will cause bugs)
4. ❌ **NO expanding scope** (fix X means fix ONLY X)
   - Stick to exact request, no "while I'm here" changes
5. ✅ **ALWAYS fail-fast on config** (throw exceptions, no silent degradation)
   - Missing config = ConfigurationError, not default values
6. ✅ **ALWAYS log to terminal** (comprehensive dual logging)
   - All generation attempts, scores, feedback visible to user

### TIER 3: Evidence & Honesty (Will lose trust)
7. ✅ **ALWAYS provide evidence** (test output, commits, counts)
   - Back up claims with verifiable proof
8. ✅ **ALWAYS be honest** (acknowledge limitations)
   - Don't claim success when quality gates fail
9. 🔥 **NEVER report success when quality gates fail**
   - Realism < 5.5, Winston fail, Readability fail = NOT success

**Full details**: [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) lines 200-250

---

## 📋 Before ANY Code Change

**Mandatory 8-Step Checklist** (from primary guide lines 300-400):

1. [ ] **Read request word-by-word** - What EXACTLY is being asked?
2. [ ] **Search documentation** - Does guidance already exist?
3. [ ] **Explore architecture** - How does it currently work?
4. [ ] **Check git history** - Was this tried before? Why changed?
5. [ ] **Plan minimal fix** - One sentence description
6. [ ] **Verify file paths exist** - Prevent "Content Not Found" errors
7. [ ] **Ask permission before major changes** - Rewriting, removing code
8. [ ] **Check protected files** - Does this require explicit permission?

**⚠️ STOP SIGNALS** - When to ASK instead of CODE:
- ❓ Not 100% certain about the requirement
- ❓ Can't find the config key/file/pattern referenced
- ❓ Fixing requires changing more than 3 files
- ❓ About to add hardcoded value without finding dynamic config
- ❓ Request conflicts with existing architecture
- ❓ Tests failing and don't understand why

---

## 🔍 Finding Information

### By Task Type
- **Generate content** → [COPILOT_GENERATION_GUIDE.md](../.github/COPILOT_GENERATION_GUIDE.md)
- **Fix bug** → [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Add feature** → [SYSTEM_INTERACTIONS.md](SYSTEM_INTERACTIONS.md) + check policies
- **Check policy** → [docs/08-development/](08-development/) (all policy documents)
- **Understand data** → [docs/05-data/](05-data/) (data architecture & policies)
- **API issues** → [docs/07-api/](07-api/) (API documentation)

### By Document Type
- **Policies** → [docs/08-development/](08-development/)
  - HARDCODED_VALUE_POLICY.md
  - CONTENT_INSTRUCTION_POLICY.md
  - TEMPLATE_ONLY_POLICY.md
  - PROMPT_PURITY_POLICY.md
  - PROTECTED_FILES.md (in .github/)
- **Architecture** → [docs/02-architecture/](02-architecture/)
  - processing-pipeline.md
  - COMPONENT_DISCOVERY.md
  - ARCHITECTURE_OVERVIEW.md
- **Components** → [docs/03-components/](03-components/)
  - Text component (generation system)
  - Image component (Imagen)
- **Operations** → [docs/04-operations/](04-operations/)
  - content-generation.md
  - BATCH_OPERATIONS.md
  - deployment.md
- **Data** → [docs/05-data/](05-data/)
  - DATA_STORAGE_POLICY.md
  - NORMALIZATION_GUIDE.md
  - ZERO_NULL_POLICY.md

### By Question Type
- **"How do I...?"** → [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **"What is...?"** → [INDEX.md](INDEX.md)
- **"Why does...?"** → [SYSTEM_INTERACTIONS.md](SYSTEM_INTERACTIONS.md)
- **"Where is...?"** → [DOCUMENTATION_MAP.md](../DOCUMENTATION_MAP.md)
- **"Can I...?"** → [.github/copilot-instructions.md](../.github/copilot-instructions.md)

---

## 🎓 Learning Path

### New to this project?
1. Read [README.md](../README.md) - Project overview (5 minutes)
2. Read [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) - Complete rules (30 minutes)
3. Scan [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Common issues (10 minutes)
4. Review [SYSTEM_INTERACTIONS.md](SYSTEM_INTERACTIONS.md) - Architecture (15 minutes)

**Total**: ~60 minutes to full productivity

### Ready to contribute?
1. Study [docs/08-development/](08-development/) - All policies (30 minutes)
2. Read [docs/02-architecture/](02-architecture/) - System design (20 minutes)
3. Review [docs/03-components/](03-components/) - Component docs (15 minutes)
4. Check [.github/PROTECTED_FILES.md](../.github/PROTECTED_FILES.md) - Permission requirements (5 minutes)

**Total**: ~70 minutes to expert level

---

## 🔒 Protected Files (Require Permission)

**TIER 1 (NEVER TOUCH without explicit permission)**:
- `shared/prompts/personas/*.yaml` - Author voice definitions
- `domains/*/prompts/*.txt` - Domain prompt templates
- `generation/core/evaluated_generator.py` - Main generation orchestrator (25KB+)
- `generation/core/generator.py` - Core generation logic

**TIER 2 (ASK FIRST)**:
- `generation/config.yaml`, `domains/*/config.yaml` - All configuration files
- `data/materials/Materials.yaml`, `data/settings/Settings.yaml` - Primary data files
- `learning/*.py` - Learning system files

**TIER 3 (VERIFY WITH TESTS)**:
- `domains/*/coordinator.py` - Coordination logic
- `domains/*/data_loader.py` - Data loading utilities
- `shared/text/adapters/*.py` - Domain adapters

**Full policy**: [.github/PROTECTED_FILES.md](../.github/PROTECTED_FILES.md)

---

## ⚡ Emergency Procedures

### Something broke?
1. **Stop immediately** - Don't make it worse
2. Read [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) - Common fixes
3. Check [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) - Emergency Recovery section
4. Git rollback if needed:
   ```bash
   git checkout HEAD -- <file>  # Restore specific file
   git revert <commit>           # Revert entire commit
   ```

### Quality gate failed?
1. **Read terminal output carefully** - Shows exact failure reason
2. Check [docs/QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Similar issues
3. Review quality thresholds in config files
4. **Don't report success** - Be honest about failure
5. Understand quality gates:
   - Winston: 69%+ human score (configurable via humanness_intensity)
   - Realism: 5.5/10 minimum (adaptive thresholds)
   - Readability: Must pass
   - No forbidden phrases

### Tests failing?
1. Read test output completely
2. Don't assume - verify with evidence
3. Check if changes introduced violations
4. Run specific test: `python3 -m pytest tests/test_name.py -v`
5. Ask for clarification if unclear

---

## 📊 Common Patterns

### Content Generation Pattern
```bash
# Always use run.py for generation
python3 run.py --micro "MaterialName"
python3 run.py --description "MaterialName"
python3 run.py --faq "MaterialName"

# Check terminal output for quality scores
# Reports success only when ALL quality gates pass
```

### Bug Fix Pattern
1. Search docs for existing guidance
2. Read relevant code to understand current behavior
3. Check git history for context
4. Plan minimal surgical fix
5. Test the specific fix
6. Verify no regressions

### Feature Addition Pattern
1. Check if it conflicts with existing architecture
2. Review [SYSTEM_INTERACTIONS.md](SYSTEM_INTERACTIONS.md) for side effects
3. Check [docs/08-development/](08-development/) for policy compliance
4. Ask permission if major change
5. Implement with tests
6. Document the change

---

## 📚 Complete Documentation Map

For comprehensive navigation of ALL documentation:
[`DOCUMENTATION_MAP.md`](../DOCUMENTATION_MAP.md)

Includes:
- Complete file structure
- Quick links by goal
- Archive documentation
- Recent updates
- Policy references

---

## 💡 Pro Tips

1. **Always read the primary guide first** - Saves hours of fixing mistakes
2. **Use grep to find examples** - Search codebase for similar patterns
3. **Check git history** - See what worked before
4. **Test incrementally** - Don't wait until the end
5. **Provide evidence** - Back up all claims with test output
6. **Be honest** - Acknowledge limitations and failures
7. **Ask permission** - Better safe than breaking working code

---

## 🤝 Getting Help

### From Documentation
1. Primary: [.github/copilot-instructions.md](../.github/copilot-instructions.md)
2. Quick: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
3. Detailed: [docs/08-development/](08-development/)

### From User
- Ask specific questions with context
- Reference documentation you've already checked
- Explain what you've tried
- Be clear about uncertainties

---

**Last Updated**: December 12, 2025  
**Maintained by**: Project team  
**For**: AI assistants (GitHub Copilot, Grok AI, Claude, etc.)
