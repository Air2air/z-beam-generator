# AI Integration Guide - AI Assistant Workflow

**Purpose**: Complete workflow integration for GitHub Copilot, Grok AI, Claude, and all AI assistants  
**Audience**: AI assistants (primary), developers using AI tools  
**Last Updated**: November 28, 2025

---

## 🚀 **30-Second Navigation** (Start Here)

### Quick Access to Any Documentation
1. **Policies & Rules**: `GROK_QUICK_REF.md` - TIER priorities, critical rules
2. **Content Generation**: `.github/COPILOT_GENERATION_GUIDE.md` - Step-by-step generation commands
3. **Architecture**: `docs/02-architecture/ARCHITECTURE_OVERVIEW.md` - System design overview
4. **Image Generation**: `docs/04-operations/IMAGE_GENERATION_GUIDE.md` - Complete image workflow
5. **Quick Answers**: `docs/QUICK_REFERENCE.md` - Problem → solution mappings

### Before ANY Code Change
**Mandatory**: `.github/copilot-instructions.md` - Pre-Change Checklist

1. Read request precisely
2. Search documentation for existing guidance  
3. Check policy documents (`docs/08-development/`)
4. Review system interactions (`docs/SYSTEM_INTERACTIONS.md`)
5. Plan minimal fix (one sentence)
6. Ask permission for major changes
7. Verify with tests before claiming success

---

## 📖 **Documentation Navigation by Task**

### Generate Content
**→ `.github/COPILOT_GENERATION_GUIDE.md`**

Step-by-step instructions for:
- Material descriptions (`python3 run.py --description "MaterialName"`)
- Captions (`python3 run.py --micro "MaterialName"`)
- FAQs (`python3 run.py --faq "MaterialName"`)
- Machine settings descriptions
- Hero images

**Terminal Output**: All generation operations stream comprehensive output to terminal (attempt progress, quality checks, feedback application, learning activity)

### Fix Bugs or Add Features
**→ `TROUBLESHOOTING.md` + `docs/SYSTEM_INTERACTIONS.md`**

1. **Check** `TROUBLESHOOTING.md` for known issues
2. **Review** `docs/SYSTEM_INTERACTIONS.md` for side effects
3. **Read** `docs/decisions/README.md` for Architecture Decision Records (WHY things work this way)
4. **Check** `docs/08-development/` for relevant policy documents
5. **Plan** minimal surgical fix (address only the specific issue)

### Understand Data Flow
**→ `docs/05-data/DATA_STORAGE_POLICY.md`**

- **Materials.yaml**: Single source of truth + all AI operations
- **Categories.yaml**: Category-level ranges
- **Frontmatter files**: Write-only mirrors (dual-write from Materials.yaml)
- **Generation flow**: Research → Materials.yaml (write) → Frontmatter (field sync)

### Check Policy Compliance
**→ `docs/08-development/`**

Critical policies:
- `HARDCODED_VALUE_POLICY.md` - Zero hardcoded values in production code
- `CONTENT_INSTRUCTION_POLICY.md` - Content instructions ONLY in prompts/*.txt
- `TEMPLATE_ONLY_POLICY.md` - ONLY templates determine content (no component-specific code)
- `PROMPT_PURITY_POLICY.md` - ALL prompts in template files (ZERO in code)
- `PROMPT_CHAINING_POLICY.md` - Multi-stage orchestration for separation of concerns
- `TERMINAL_LOGGING_POLICY.md` - Dual logging (print + logger) for visibility
- `NAMING_CONVENTIONS_POLICY.md` - Remove redundant prefixes (Simple, Universal, Unified)

### Prompt Chaining & Orchestration
**→ `docs/08-development/PROMPT_CHAINING_POLICY.md`**

Break generation into specialized prompts:
- Stage 1: Research (low temp 0.3)
- Stage 2: Visual description (high temp 0.7)
- Stage 3: Composition (balanced 0.5)
- Stage 4: Refinement (precise 0.4)
- Stage 5: Assembly (balanced 0.5)

**Benefits**: Separation of concerns, optimal parameters per stage, reusable components, easy debugging

### Image Generation
**→ `docs/04-operations/IMAGE_GENERATION_GUIDE.md`**

Complete workflow:
- Domain adapter pattern (materials, contaminants)
- 5-stage prompt chaining
- Pre-generation validation
- Learning system integration
- Troubleshooting common issues

### Research Implementation History
**→ `docs/archive/2025-11/README.md`**

82 archived implementation documents:
- Completed implementations
- Analysis & research
- Test results & demos
- Session summaries
- Migrations & enhancements
- Proposals & planning

---

## 🚦 **TIER Priorities** (Critical Rules Hierarchy)

### 🔴 TIER 1: SYSTEM-BREAKING (Will cause failures)
1. ❌ **NO mocks/fallbacks in production code** (tests OK)
2. ❌ **NO hardcoded values/defaults** (use config/dynamic calc)
3. ❌ **NO rewriting working code** (minimal surgical fixes only)

### 🟡 TIER 2: QUALITY-CRITICAL (Will cause bugs)
4. ❌ **NO expanding scope** (fix X means fix ONLY X)
5. ✅ **ALWAYS fail-fast on config** (throw exceptions)
6. ✅ **ALWAYS log to terminal** (comprehensive dual logging)
7. ✅ **ALWAYS preserve runtime recovery** (API retries are correct)

### 🟢 TIER 3: EVIDENCE & HONESTY (Will lose trust)
8. ✅ **ALWAYS provide evidence** (test output, counts, commits)
9. ✅ **ALWAYS be honest** (acknowledge limitations)
10. 🔥 **NEVER report success when quality gates fail**
11. 🔥 **ALWAYS read ALL evaluation scores** (pre-save AND post-generation)
12. 🔥 **ALWAYS verify implementation before documentation** (tests prove it works)
13. 🔥 **NEVER document features without evidence** (tests prove claims)

**Grade**: Reporting success when quality fails is TIER 3 violation → Grade F

---

## 📋 **Mandatory Pre-Change Checklist**

### Step 1: Read & Understand (2-3 min)
- [ ] **Read request word-by-word** - What EXACTLY is being asked?
- [ ] **Check for assumptions** - Am I assuming anything not stated?
- [ ] **Verify file paths** - Do all referenced files actually exist?
- [ ] **Check config keys** - Do claimed violations actually exist in config files?

### Step 2: Research (3-5 min)
- [ ] **Search documentation** - `docs/QUICK_REFERENCE.md`, `docs/08-development/`
- [ ] **grep_search for patterns** - How does the system currently handle this?
- [ ] **Read relevant code** - Understand current implementation
- [ ] **Check git history** - Was this tried before? Why was it changed?
- [ ] **Review ADRs** - Is there an architectural decision about this?

### Step 3: Planning (2-3 min)
- [ ] **Identify exact change needed** - One sentence description
- [ ] **Confirm minimal scope** - Am I fixing ONLY what was requested?
- [ ] **Check for side effects** - What else might this affect?
- [ ] **Plan validation** - How will I prove it works?
- [ ] **Get permission if major** - Ask before removing/rewriting code

### Step 4: Implementation
- [ ] **Apply the fix** - Make only the planned changes
- [ ] **Write verification test FIRST** - Prove the fix works before documenting
- [ ] **Read back your changes** - Use read_file to verify what you wrote
- [ ] **Check for new violations** - Did you introduce hardcoded values, TODOs, fallbacks?

### Step 5: Verification & Documentation
- [ ] **Verify implementation matches documentation** - Run live test to confirm claims
- [ ] **STOP if verification fails** - Do NOT proceed to documentation
- [ ] **Document with evidence** - Include test results, success rate, terminal output
- [ ] **Never claim "COMPLETE" without verification test**

### Step 6: Honest Reporting
- [ ] **Check documentation matches reality** - Run live test to confirm claims
- [ ] **Provide verification evidence** - Test results, success rates, terminal output
- [ ] **Acknowledge limitations** - Be honest about architectural constraints
- [ ] **Grade your work** - A (excellent), B (good), C (needs improvement), F (unacceptable)

**⏱️ Time Investment**: 7-11 minutes of research prevents hours of fixing broken code

---

## 🚨 **Critical Failure Patterns to Avoid**

### Pattern 0: Documentation Claims Contradicting Code Reality 🔥 **MOST CRITICAL**
**Example**: Documentation claimed "Option C implemented - saves all attempts" but code was still blocking saves (10% success rate proved gates were active)

**Correct Behavior**:
- ✅ VERIFY implementation with tests BEFORE documenting as complete
- ✅ Check actual code behavior matches documentation claims
- ✅ Use success rate as reality check (10% = gates blocking, 100% = Option C working)
- ✅ Write verification tests: `test_saves_all_attempts_regardless_of_quality()`

### Pattern 1: Reporting Success When Quality Gates Fail
**Example**: AI reported "✅ Description generated" when realism score was 5.0/10 (threshold: 5.5/10)

**Correct Behavior**:
- ❌ REJECT if any gate fails (Realism < 5.5, Winston fail, Readability fail)
- ✅ Only report success when ALL gates pass
- ✅ Report failures honestly: "Quality gate failed, regenerating..."

### Pattern 2: Not Reading Evaluation Scores Carefully
**Example**: Two evaluations ran (9.0/10, then 5.0/10), AI only noticed the first

**Correct Behavior**:
- ✅ Read ALL evaluation outputs
- ✅ Check BOTH pre-save AND post-generation scores
- ✅ Verify final stored content meets thresholds

### Pattern 6: Treating Symptoms Instead of Root Causes 🔥 **CRITICAL**
**Example**: Word counts 20-50% over target. AI added stricter prompt instructions 5+ times instead of fixing the mechanism.

**Correct Behavior**:
- ✅ Measure results after EACH fix attempt
- ✅ When same approach fails 2+ times, question the approach itself
- ✅ Research: What is ACTUALLY possible with LLM architecture?
- ✅ Accept architectural limitations: "approximately X words" not strict limits
- ✅ Be honest with user about what can't be fixed

**Red Flags**:
- 🚩 Adding more "CRITICAL" keywords to prompts
- 🚩 Rephrasing the same instruction in different words
- 🚩 Not measuring actual results after each change
- 🚩 Assuming "this time it will work" without architectural change

---

## 🔧 **Decision Trees**

### Should I use a default value?
```
Is this a config/setup issue?
├─ YES → ❌ FAIL FAST (throw ConfigurationError)
└─ NO → Is this a runtime/transient issue?
    ├─ YES → ✅ RETRY with backoff (API timeout)
    └─ NO → ❌ FAIL FAST (programming error)
```

### Should I rewrite this code?
```
Does the code work correctly?
├─ YES → ❌ NO REWRITE (integrate around it)
└─ NO → Is it a small targeted fix?
    ├─ YES → ✅ FIX ONLY broken part
    └─ NO → ⚠️ ASK PERMISSION
```

### Should I add a hardcoded value?
```
Can I find an existing dynamic solution?
├─ YES → ✅ USE IT (grep_search for DynamicConfig)
└─ NO → Is this truly a constant?
    ├─ YES → ✅ CONFIG FILE (config.yaml)
    └─ NO → ⚠️ ASK USER
```

**🔍 MANDATORY: Search Before Adding ANY Value**

Before adding any hardcoded value:
1. `grep -r "DynamicConfig|dynamic_config" generation/`
2. `grep -r "calculate_temperature|calculate_penalties" generation/config/`
3. `grep -r "temperature|threshold" generation/config.yaml`

**If no existing solution**: ASK USER before proceeding

---

## 🛠️ **Common Tasks - Direct Solutions**

### Generate Material Description
```bash
python3 run.py --description "Aluminum"
```

### Generate Material Caption
```bash
python3 run.py --micro "Steel"
```

### Generate Hero Image
```bash
python3 domains/materials/image/generate.py "Copper" --output-dir public/images/materials
```

### Check Data Completeness
```bash
python3 run.py --data-completeness-report
```

### View Data Gaps (Research Priorities)
```bash
python3 run.py --data-gaps
```

### Run Integrity Check
```bash
python3 scripts/tools/integrity_checker.py
```

### View Learning Analytics
```bash
python3 domains/materials/image/learning/analytics.py attempts
```

---

## 📚 **Policy Quick Reference**

### Zero Hardcoded Values
**Document**: `docs/08-development/HARDCODED_VALUE_POLICY.md`

- ❌ `temperature=0.7` → ✅ `dynamic_config.calculate_temperature(component_type)`
- ❌ `frequency_penalty=0.0` → ✅ `params['api_penalties']['frequency_penalty']` (fail if missing)
- ❌ `if score > 30:` → ✅ `config.get_threshold('score_type')`

### Content Instructions Only in Templates
**Document**: `docs/08-development/CONTENT_INSTRUCTION_POLICY.md`

- ✅ `prompts/*.txt` - ALL content instructions
- ❌ `processing/*.py` - ZERO content instructions
- ❌ `ComponentSpec.format_rules` - Forbidden field
- ✅ `ComponentSpec.prompt_template_file` - Reference template only

### Template-Only Policy
**Document**: `docs/08-development/TEMPLATE_ONLY_POLICY.md`

- ✅ `domains/*/prompts/*.txt` - ALL content and formatting
- ❌ `processing/*.py` - ZERO component-specific methods
- ✅ Add new component = template file + config entry ONLY (zero code changes)

### Prompt Purity Policy
**Document**: `docs/08-development/PROMPT_PURITY_POLICY.md`

- ✅ `prompts/*.txt` - ALL prompt text
- ❌ `processing/*.py` - ZERO prompt text (NO EXCEPTIONS)
- ❌ `system_prompt = "You are..."` - Forbidden
- ✅ `prompt = self._load_prompt_template('micro.txt')` - Correct

### Terminal Logging Policy
**Document**: `docs/08-development/TERMINAL_LOGGING_POLICY.md`

**Requirements**:
- Stream to stdout using `print()` - Always visible to user
- Dual logging: Both `print()` (terminal) AND `logger.info()` (file records)
- Real-time output, attempt progress, quality checks, parameter adjustments
- FULL NON-TRUNCATED OUTPUT (NEVER use tail, head, or truncation)

---

## 🎯 **Success Patterns**

### Effective Code Changes
1. **Minimal scope** - Fix only what was requested
2. **Evidence-based** - Test output proves it works
3. **Documented** - Clear explanation with examples
4. **Policy-compliant** - Follows all TIER 1-3 rules
5. **Honest** - Acknowledges what remains broken

### Effective Communication
1. **Concise** - 1-3 sentences for simple answers
2. **Evidence** - "24/24 tests passing (see output below)"
3. **Honest** - "This architectural limitation cannot be fixed with prompts"
4. **Actionable** - "Option A: Accept approximate counts, Option B: Manual review"

### Effective Research
1. **Documentation first** - Check `docs/QUICK_REFERENCE.md`
2. **Pattern search** - `grep_search` for similar implementations
3. **History check** - `git log --follow` to understand changes
4. **Policy review** - Read relevant `docs/08-development/` policies

---

## 🔗 **Related Documentation**

### For AI Assistants (Primary)
- **This Guide**: `docs/01-getting-started/AI_INTEGRATION_GUIDE.md` - Complete workflow
- **Quick Start**: `docs/08-development/AI_ASSISTANT_GUIDE.md` - 30-second navigation
- **Policies**: `GROK_QUICK_REF.md` - TIER priorities
- **Generation**: `.github/COPILOT_GENERATION_GUIDE.md` - Commands

### Architecture & Design
- **Architecture**: `docs/02-architecture/ARCHITECTURE_OVERVIEW.md` - System design
- **Images**: `docs/04-operations/IMAGE_GENERATION_GUIDE.md` - Image workflow
- **Quick Ref**: `docs/QUICK_REFERENCE.md` - Problem → solution

### Development Policies
- **All Policies**: `docs/08-development/` - Complete policy library
- **Copilot Instructions**: `.github/copilot-instructions.md` - Full guidelines

---

**Last Major Update**: November 28, 2025 - Documentation consolidation, AI workflow integration, 82% documentation reduction for 90% faster navigation