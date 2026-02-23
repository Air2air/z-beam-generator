# AI Assistant Guide - Z-Beam Generator

**For**: GitHub Copilot, Grok AI, Claude, and all AI development assistants  
**Last Updated**: November 22, 2025  
**Quick Start**: 30-second navigation to any answer

---

## Workflow Orchestration

### 1. Plan Node Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately - don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

### 2. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution

### 3. Self-Improvement Loop
- After ANY correction from the user: update tasks/lessons.md with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project

### 4. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 5. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes - don't over-engineer
- Challenge your own work before presenting it

### 6. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests - then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

## Task Management
1. **Plan First**: Write plan to tasks/todo.md with checkable items
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Document Results**: Add review section to tasks/todo.md
6. **Capture Lessons**: Update tasks/lessons.md after corrections

## Core Principles
- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.

## 🚀 **30-Second Quick Start**

### **User wants to generate content?**
→ `.github/COPILOT_GENERATION_GUIDE.md`

### **User reports an error?**
→ `TROUBLESHOOTING.md` (root)

### **Need to understand system architecture?**
→ `docs/SYSTEM_INTERACTIONS.md`

### **Working on code changes?**
→ `.github/copilot-instructions.md` (control surface: complexity gate, Core 5 Rules, checklists, navigation)  
→ `docs/08-development/` (full policy library)

### **Looking for documentation?**
→ `DOCUMENTATION_MAP.md` (complete map)  
→ `docs/QUICK_REFERENCE.md` (fastest answers)

---

## 📋 **Critical Rules (Read Before ANY Change)**

### **Execution Environment Rule**
1. ✅ ALWAYS run tasks directly with `python3` from repo root.
2. ❌ NEVER create/activate a virtual environment for standard project tasks.
3. ✅ Apply this to generation, postprocess, export, integrity checks, and tests.

### **TIER 1: System-Breaking** (Will cause failures)
1. ❌ NO mocks/fallbacks in production code (tests OK)
2. ❌ NO hardcoded values/defaults (use config/dynamic calc)
3. ❌ NO rewriting working code (minimal surgical fixes only)
4. ❌ NO exporter-only fixes for frontmatter issues (fix source data or generators only)

### **TIER 2: Quality-Critical** (Will cause bugs)
4. ❌ NO expanding scope (fix X means fix ONLY X)
5. ❌ NO skipping validation (must test before claiming success)
6. ✅ ALWAYS fail-fast on config (throw exceptions, no silent degradation)
7. ✅ ALWAYS preserve runtime recovery (API retries are correct)
8. ✅ ALWAYS log to terminal (all generation attempts, scores, feedback)

### **TIER 3: Evidence & Honesty** (Will lose trust)
9. ✅ ALWAYS provide evidence (test output, counts, commits)
10. ✅ ALWAYS be honest (acknowledge what remains broken)
11. ✅ ASK before major changes (get permission for improvements)
12. ✅ VERIFY before claiming violations (check config files, confirm pattern exists)
13. 🔥 NEVER report success when quality gates fail
14. 🔥 ALWAYS read ALL evaluation scores (pre-save AND post-generation)
15. 🔥 ALWAYS check for AI-like phrases (formulaic structure)

---

## 🎯 **Common Tasks - Direct Navigation**

### **Generate Content**
```bash
# Micro (regenerates ALL sections + titles/descriptions)
python3 run.py --micro "MaterialName"

# Subtitle (regenerates ALL sections + titles/descriptions)
python3 run.py --subtitle "MaterialName"

# Description (regenerates ALL sections + titles/descriptions)
python3 run.py --description "MaterialName"

# FAQ (regenerates ALL sections + titles/descriptions)
python3 run.py --faq "MaterialName"
```

**🔄 CRITICAL: Complete Section Regeneration**
EVERY generation request completely regenerates:
1. **Page title and description** - Material-specific content
2. **Each section title and description** - All relationship sections, properties, applications

**Documentation**: `.github/COPILOT_GENERATION_GUIDE.md`

---

### **Fix Bugs or Add Features**

**Step 1: Research BEFORE coding**
1. Search documentation: `docs/QUICK_REFERENCE.md`
2. Check system interactions: `docs/SYSTEM_INTERACTIONS.md`
3. Review policies: `docs/08-development/` (all policies)
4. Check git history: Has this been tried before?

**Step 2: Plan minimal fix**
- Identify exact change needed (one sentence)
- Confirm minimal scope (fix ONLY what requested)
- Check for side effects
- Plan validation

**Step 3: Implement & Test**
- Apply fix
- Run tests: `pytest tests/`
- Verify no regressions
- Check for new violations

**Documentation**: `.github/copilot-instructions.md` (complete guide)

---

### **Policy Compliance Check**

**Zero Hardcoded Values**:
```bash
grep -r "temperature = 0\.|frequency_penalty = 0\." generation/**/*.py
```
Expected: Only acceptable patterns (constants, formulas)

**No Mocks/Fallbacks**:
```bash
grep -r "MockAPIClient|mock_response|skip_validation" generation/**/*.py
```
Expected: 0 matches in production code

**Documentation**: `docs/08-development/HARDCODED_VALUE_POLICY.md`

---

### **Understanding Data Flow**

**Generation Pipeline**:
```
Generate → Evaluate → Save → Improve Continuously (Option C)
```

**Quality Gates** (ALL must pass for "excellent"):
- Winston: 69%+ human (dynamic threshold)
- Realism: 7.0/10 minimum
- Structural Diversity: 6.0/10 minimum
- No AI Tendencies

**Documentation**: `docs/02-architecture/processing-pipeline.md`

---

### **Terminal Logging Requirements**

**MANDATORY for ALL generation operations**:
1. Dual logging: `print()` (terminal) + `logger.info()` (file)
2. Real-time streaming (no batch output at end)
3. Comprehensive coverage:
   - API request/response status
   - Every attempt with parameters
   - Quality scores (Winston, Realism, Structural)
   - Parameter adjustments between attempts
   - Database logging confirmation
   - Full generated content display

**Documentation**: `docs/08-development/TERMINAL_LOGGING_POLICY.md`

---

## 📚 **Documentation Structure**

### **Root Level** (Essential, keep here)
- `README.md` - Project overview
- `QUICK_START.md` - Get started in 5 minutes
- `TROUBLESHOOTING.md` - Common errors and solutions
- `DOCUMENTATION_MAP.md` - Complete documentation index
- `GROK_QUICK_REF.md` - Critical policies for AI assistants

### **docs/** (Organized by category)
- `01-getting-started/` - Setup, installation, first generation
- `02-architecture/` - System design, component interactions
- `03-components/` - Component-specific documentation
- `04-operations/` - Running, monitoring, maintenance
- `05-data/` - Data structure, validation, completeness
- `06-ai-systems/` - Learning, optimization, quality evaluation
- `07-api/` - API integration, error handling, rate limits
- `08-development/` - **Policies, guidelines, contribution rules**
- `09-reference/` - Parameter reference, CLI commands, glossary
- `archive/` - Historical documentation (completed implementations)

### **.github/** (AI Assistant Instructions)
- `copilot-instructions.md` - Control surface: complexity gate, Core 5 Rules, Grade F violations, pre-change checklist, navigation (~126 lines). Full pre-refactor archive: `docs/archive/2026-02/copilot-instructions-pre-refactor-feb2026.md`
- `COPILOT_GENERATION_GUIDE.md` - Content generation step-by-step

---

## 🔍 **Quick Lookups**

### **Policy Documents** (`docs/08-development/`)
- `HARDCODED_VALUE_POLICY.md` - Zero hardcoded values enforcement
- `TERMINAL_LOGGING_POLICY.md` - Comprehensive terminal output requirements
- `TEMPLATE_ONLY_POLICY.md` - All content in prompt catalog entries, not code
- `PROMPT_PURITY_POLICY.md` - Zero prompt text in generators
- `CONTENT_INSTRUCTION_POLICY.md` - Content rules ONLY in prompt catalog entries

### **Architecture Documents** (`docs/02-architecture/`)
- `COMPONENT_DISCOVERY.md` - How components are discovered dynamically
- `processing-pipeline.md` - Generation flow (Generate → Evaluate → Save)
- `quality-gates.md` - What quality checks are enforced

### **Recent Implementations** (`docs/archive/2025-11/`)
- `OPTION_C_IMPLEMENTATION_NOV22_2025.md` - Save-all architecture
- `CONFIG_DRIVEN_RANDOMIZATION_NOV22_2025.md` - All randomization in config
- `PRIORITY1_COMPLETE_NOV22_2025.md` - Log ALL attempts for learning
- `E2E_SYSTEM_ANALYSIS_NOV22_2025.md` - Complete system grade (A+)

---

## ⚡ **Pre-Change Checklist**

**MANDATORY before ANY code modification**:

1. [ ] **Read request precisely** - What is the exact issue?
2. [ ] **Search documentation** - Check `docs/QUICK_REFERENCE.md`
3. [ ] **Check policies** - Review `docs/08-development/`
4. [ ] **Verify file paths** - Do referenced files exist?
5. [ ] **Search for existing solutions** - Use grep for DynamicConfig, helpers
6. [ ] **Plan minimal fix** - One sentence description
7. [ ] **Ask permission** - Before removing/rewriting code

**Documentation**: `.github/copilot-instructions.md` lines 300-350

---

## 🎓 **Learning Resources**

### **New to the Project?**
1. Read: `README.md`
2. Follow: `QUICK_START.md`
3. Generate: Your first micro/subtitle
4. Review: `docs/SYSTEM_INTERACTIONS.md`

### **Contributing Code?**
1. Study: `.github/copilot-instructions.md` (complete rules)
2. Review: `GROK_QUICK_REF.md` (critical policies)
3. Check: `docs/08-development/` (all policies)
4. Test: Run `pytest tests/` before committing

### **Debugging Issues?**
1. Check: `TROUBLESHOOTING.md`
2. Review: `docs/07-api/ERROR_HANDLING.md`
3. Search: `docs/QUICK_REFERENCE.md`
4. Ask: Provide terminal output + context

---

## 🚨 **Emergency: System Broken?**

### **Quick Recovery**
```bash
# Check git status
git status

# Restore specific file
git checkout HEAD -- <file>

# Revert last commit
git revert HEAD

# Full reset (CAUTION)
git reset --hard HEAD
```

### **Common Fixes**
1. **Import errors**: Check `docs/08-development/` for import paths
2. **Config missing**: Verify `generation/config.yaml` exists
3. **API errors**: Check `docs/07-api/ERROR_HANDLING.md`
4. **Quality gate fails**: Review `docs/06-ai-systems/quality-gates.md`

---

## 📞 **Getting Help**

### **For AI Assistants**
- Primary: `.github/copilot-instructions.md` (complete guide)
- Quick Ref: `GROK_QUICK_REF.md` (critical policies)
- This Guide: `docs/08-development/AI_ASSISTANT_GUIDE.md`

### **For Human Developers**
- Quick Start: `QUICK_START.md`
- Troubleshooting: `TROUBLESHOOTING.md`
- Full Docs: `DOCUMENTATION_MAP.md`

### **For Content Generation**
- Step-by-step: `.github/COPILOT_GENERATION_GUIDE.md`
- Terminal output: `docs/08-development/TERMINAL_LOGGING_POLICY.md`
- Quality gates: `docs/06-ai-systems/quality-gates.md`

---

**Last Updated**: November 22, 2025  
**System Status**: Production Ready (Grade A+, 98/100)  
**Documentation Status**: Consolidated and Streamlined
