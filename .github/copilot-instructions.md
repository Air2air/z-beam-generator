# AI Assistant Instructions for Z-Beam Generator

**For**: GitHub Copilot, Grok AI, Claude, and all AI development assistants  
**System**: Laser cleaning content generation with strict fail-fast architecture  
**Last Updated**: November 22, 2025

---

## 🚀 **30-SECOND QUICK START** 🔥 **NEW (Nov 22, 2025)**

**⚡ PRIORITY**: Read this section FIRST for immediate navigation, then consult detailed rules below.

### **📖 Full Navigation Guide**
**Primary Resource**: `docs/08-development/AI_ASSISTANT_GUIDE.md`  
- 30-second navigation to any documentation
- Quick lookup tables for common tasks
- Pre-change checklist
- Emergency recovery procedures

### **🎯 Common Tasks - Direct Links**

| Task | Resource |
|------|----------|
| **Generate content** | `.github/COPILOT_GENERATION_GUIDE.md` (step-by-step) |
| **Fix bugs/add features** | Pre-Change Checklist (see below) + `docs/SYSTEM_INTERACTIONS.md` |
| **Check policy compliance** | `docs/08-development/` (HARDCODED_VALUE_POLICY, TERMINAL_LOGGING_POLICY, etc.) |
| **Prompt chaining/orchestration** | `docs/08-development/PROMPT_CHAINING_POLICY.md` 🔥 **NEW** |
| **Naming conventions** | `docs/08-development/NAMING_CONVENTIONS_POLICY.md` 🔥 **NEW** |
| **Understand data flow** | `docs/02-architecture/processing-pipeline.md` |
| **Find quick answers** | `docs/QUICK_REFERENCE.md` |
| **Troubleshoot errors** | `TROUBLESHOOTING.md` (root) |
| **Research implementation history** | `docs/archive/2025-11/` (52 archived docs) |

### **🚦 Critical Policies Summary**

**TIER 1: System-Breaking** (Will cause failures)
- ❌ NO mocks/fallbacks in production code (tests OK)
- ❌ NO hardcoded values/defaults (use config/dynamic calc)
- ❌ NO rewriting working code (minimal surgical fixes only)

**TIER 2: Quality-Critical** (Will cause bugs)
- ❌ NO expanding scope (fix X means fix ONLY X)
- ✅ ALWAYS fail-fast on config (throw exceptions)
- ✅ ALWAYS log to terminal (comprehensive dual logging)

**TIER 3: Evidence & Honesty** (Will lose trust)
- ✅ ALWAYS provide evidence (test output, commits)
- ✅ ALWAYS be honest (acknowledge limitations)
- 🔥 NEVER report success when quality gates fail

**Full Details**: See TIER PRIORITIES section below + `docs/08-development/`

### **📋 Quick Pre-Change Checklist**

Before ANY code change:
1. [ ] Search `docs/QUICK_REFERENCE.md` for existing guidance
2. [ ] Check `docs/08-development/` for relevant policy
3. [ ] Review `docs/SYSTEM_INTERACTIONS.md` for side effects
4. [ ] **Check `.github/PROTECTED_FILES.md`** - Is this file protected?
5. [ ] Plan minimal fix (one sentence description)
6. [ ] Verify all file paths exist before coding
7. [ ] Ask permission before major changes or rewrites

---

## 🖼️ **IMAGE FEEDBACK CAPTURE PROTOCOL** 🔥 **NEW (Nov 29, 2025)**

**Purpose**: Automatically detect and capture user feedback on generated images for learning.

### **Explicit Trigger (Option B)**
User can use `/feedback` command for certainty:
```
/feedback Steel: rotation angle too small, both sides look identical
/feedback Aluminum contamination: oil looks painted on, not realistic
```

**When user uses `/feedback`, IMMEDIATELY run:**
```bash
python3 domains/materials/image/tools/add_feedback.py -m <material> -c <category> -f "<feedback_text>"
```

**Categories**: `physics`, `rotation`, `contamination`, `object`, `background`, `composition`, `realism`, `text`, `other`

### **Automatic Detection (Option C)**
When user comments on a generated image WITHOUT `/feedback`, detect these patterns:

**🚨 TRIGGER PHRASES** (offer to log feedback):
- "rotation is wrong/too small/not enough"
- "contamination looks wrong/thick/fake/painted"
- "background is wrong/white/studio"
- "object looks wrong/different/not the same"
- "unrealistic/fake looking/AI-looking"
- "text in image/watermark/label"
- "shadows wrong/lighting wrong"
- "not rotated/same angle"

**When detected, respond with:**
```
📝 I noticed feedback about the image. Should I log this to the learning database?

Detected:
- Material: [inferred or ask]
- Category: [inferred: rotation/contamination/etc]
- Feedback: "[user's comment]"

Reply 'yes' to log, or provide corrections.
```

### **After Logging, Confirm:**
```
✅ Feedback logged to learning database:
   Material: Steel
   Category: rotation
   Feedback: "rotation angle too small, both sides look identical"
   
This will help improve future generations. View all feedback:
   python3 domains/materials/image/tools/add_feedback.py --list
```

### **Integration with Generation**
When generating a new image for a material that has feedback:
1. Check SQLite for manual feedback on that material
2. Mention: "Note: Previous feedback for Steel includes rotation issues"
3. Consider applying corrections proactively

### **Feedback Integration Policy** 🔥 **NEW (Nov 30, 2025) - CRITICAL**

**Feedback MUST be analyzed and consolidated into appropriate prompt sections, NOT just concatenated.**

**PROHIBITED Approach** (Grade F):
```
❌ Append feedback to CORRECTIONS section
❌ Add more text to already-long prompts
❌ Let optimizer truncate important feedback
❌ Create feedback files that just get concatenated
```

**REQUIRED Approach** (Grade A):
```
✅ ANALYZE feedback to identify root cause location in prompt chain
✅ MODIFY the source template where the issue originates
✅ CONSOLIDATE feedback into existing prompt sections
✅ REWRITE sections if needed to integrate modifications
✅ REMOVE contradicting text when adding corrections
```

**Feedback Processing Steps**:
1. **Trace the prompt chain** - Find all templates that touch the issue
2. **Identify root location** - Which template is the source of the problem?
3. **Check for contradictions** - Does existing text contradict the feedback?
4. **Modify at source** - Edit the template, don't add another layer
5. **Verify integration** - Run dry-run to confirm feedback appears in final prompt
6. **Check prompt length** - Ensure changes don't exceed limits

**Example - "Glass contamination too thick"**:
```
❌ WRONG: Add "glass contamination should be thin" to user_corrections.txt
✅ RIGHT: 
   1. Find contamination_rules.txt (source of contamination description)
   2. Find base_structure.txt (describes contamination appearance)
   3. Modify BOTH to specify thin/uniform for glass
   4. Create glass_corrections.txt for glass-specific overrides
   5. Remove "chunky" or "thick" language if present
```

**Prompt Length Management**:
- If prompt exceeds 4096 chars after integration, REWRITE sections to be more concise
- Prioritize: Material-specific rules > Generic rules > Examples
- Never let optimizer truncate critical feedback

### **Feedback Analytics**
```bash
# View recent feedback
python3 domains/materials/image/tools/add_feedback.py --list

# Search feedback
python3 domains/materials/image/tools/add_feedback.py --search "rotation"

# Statistics by category
python3 domains/materials/image/tools/add_feedback.py --stats

# Via analytics CLI
python3 shared/image/learning/analytics.py --manual-feedback
```

---

## 📦 File Organization & Root Cleanliness Policy (Nov 28, 2025)

**Purpose:** Ensure all file types (.py, .sh, .log, .txt, etc.) are organized for maintainability and AI assistant workflow compliance. Prevent root clutter and legacy file sprawl.

**🎯 Current Status (Dec 6, 2025)**: Project cleanliness **A (92/100)** after November cleanup + December test fixes
- ✅ All root modules actively imported (no orphans)
- ✅ November 2025: 100% compliance achieved in voice, architecture, learning, domains
- ✅ December 2025: Field isolation tests fixed (14/14 passing) ⬆️
- ✅ Deprecated file removed: `scripts/validation/enhanced_schema_validator.py` ⬆️
- ⚠️ 73 `__pycache__` directories (routine cleanup needed)
- ✅ Test suite: 313/314 passing (99.7% success rate) ⬆️
- See: `docs/08-development/CLEANUP_AND_TEST_COVERAGE_ANALYSIS.md` for complete analysis

### 🔹 Python Scripts (.py)
- **Batch/utility scripts:** Move to `scripts/` or `tools/`.
- **Runner scripts:** Only keep essential entry points (e.g., `run.py`) in root.
- **Test scripts:** All `test_*.py` files must be in `tests/`.
- **Deprecated files:** Remove if zero imports found (use grep verification)

### 🔹 Shell Scripts (.sh)
- **Batch/process scripts:** Move to `scripts/` or `batch/`.
- **Migration/monitoring scripts:** Group by function in subfolders (e.g., `scripts/migration/`, `scripts/monitoring/`).

### 🔹 Log Files (.log)
- **Operational logs:** Store in `logs/`, set up `.gitignore` for auto-exclusion.
- **Batch/research logs:** Move to `logs/` or `output/` as appropriate.

### 🔹 Text Files (.txt)
- **Progress trackers:** Move to `progress/` or `logs/`.
- **Requirements files:** Keep `requirements.txt` in root or move to `config/` if multiple environments.
- **Coverage lists:** Store in `coverage/` or `tests/`.

### 🔹 Markdown Files (.md)
- **Documentation:** Only keep top-level navigation docs in root (e.g., `README.md`, `DOCUMENTATION_MAP.md`).
- **Guides/architecture:** Move to `docs/` or relevant subdirectories.
- **Archived docs:** Store in `docs/archive/`.

### 🔹 General Rules
- **No stray files in root:** Only keep essential entry points and navigation docs.
- **Use `.gitignore`:** Exclude logs, outputs, and temporary files.
- **Automate cleanup:** Add scripts to remove old logs and outputs.
- **Document structure:** Update `DOCUMENTATION_MAP.md` to reflect new locations.

### 🔹 Maintenance
- **Regular audits:** Periodically check for stray files in root.
- **Enforce structure:** Use pre-commit hooks or CI checks to prevent root clutter.
- **Update navigation docs:** Ensure all links in `DOCUMENTATION_MAP.md` and `.github/copilot-instructions.md` are current.

**Compliance:**
- All file moves and organization must follow this policy.
- AI assistants must enforce root cleanliness before major documentation or workflow changes.
- Any exceptions require explicit approval and documentation.

**Full Checklist**: See "Mandatory Pre-Change Checklist" section below (lines ~300)

---

## 🚨 **CRITICAL FAILURE PATTERNS TO AVOID** 🔥 **UPDATED (Dec 11, 2025)**

### **Pattern 0A: Bypassing the Text Processing Pipeline** 🔥 **NEW - CRITICAL (Dec 11, 2025)**
**What It Is**: Generating text without going through QualityEvaluatedGenerator pipeline
**Why It's Grade F**: Bypasses author voice, AI detection avoidance, quality learning, and architectural consistency
**Impact**:
- Content generated without author voice consistency (violates immutability policy)
- No humanness layer applied (fails AI detection)
- No quality evaluation or learning (system doesn't improve)
- Inconsistent text quality across domains
**Correct Behavior**:
```python
# ✅ CORRECT - All text goes through pipeline
from generation.core.evaluated_generator import QualityEvaluatedGenerator
result = generator.generate(material_name, component_type, author_id)

# ❌ WRONG - Direct API call bypasses pipeline
text = api_client.generate(prompt, temperature=0.7)

# ❌ WRONG - Custom generation logic
text = custom_function(material)
```

**MANDATORY REQUIREMENTS (Dec 11, 2025):**
1. **Universal Pipeline** - ALL text in ALL domains uses QualityEvaluatedGenerator
2. **Single Voice Source** - ONLY `shared/voice/profiles/*.yaml` defines voice
3. **Zero Bypass** - NO text generated outside pipeline (NO EXCEPTIONS)

**Grade:** F violation - Immediate architectural failure

### **Pattern 0: Documentation Claims Contradicting Code Reality** 🔥 **NEW - MOST CRITICAL**
**What Happened**: Documentation claimed "Option C implemented - saves all attempts" but code was still blocking saves (10% success rate proved gates were active)
**Why It's Grade F**: Creates architectural confusion, wastes effort on wrong diagnosis, erodes user trust
**Impact**: 
- All Nov 22 analysis based on false assumption (Option C active)
- Wrong root cause identified (blamed Winston thresholds when real issue was gate blocking)
- Wasted time on fixes that couldn't help
**Correct Behavior**:
```
✅ VERIFY implementation with tests BEFORE documenting as complete
✅ Check actual code behavior matches documentation claims
✅ Use success rate as reality check (10% = gates blocking, 100% = Option C working)
✅ Write verification tests: test_saves_all_attempts_regardless_of_quality()
```

**Prevention Checklist**:
- [ ] Does a test verify this claim? (If no, don't claim "COMPLETE")
- [ ] Does actual behavior match documentation? (Run live test)
- [ ] Can I prove it with evidence? (Success rate, terminal output, test results)

### **Pattern 1: Reporting Success When Quality Gates Fail**
**What Happened**: AI reported "✅ Description generated" when realism score was 5.0/10 (threshold: 5.5/10)
**Why It's Grade F**: Bypassed quality control, shipped low-quality content, dishonest reporting
**Correct Behavior**: 
```
❌ REJECT if any gate fails:
  - Realism < 5.5/10
  - Winston > threshold
  - Readability FAIL
✅ Only report success when ALL gates pass
✅ Report failures honestly: "Quality gate failed, regenerating..."
```

### **Pattern 2: Not Reading Evaluation Scores Carefully**
**What Happened**: Two evaluations ran (9.0/10, then 5.0/10), AI only noticed the first
**Why It's Grade C**: Incomplete verification, missed critical quality failure
**Correct Behavior**:
```
✅ Read ALL evaluation outputs
✅ Check BOTH pre-save AND post-generation scores
✅ Verify final stored content meets thresholds
✅ Report: "Attempt 1: 9.0/10 ✅ PASS, Attempt 2: 5.0/10 ❌ FAIL"
```

### **Pattern 3: Manual Data Fixes Instead of Root Cause**
**What Happened**: Description saved to wrong location (line 1180), AI manually moved it to line 832
**Why It's Grade B**: Workaround instead of fixing the save logic
**Correct Behavior**:
```
❌ Don't patch data files
✅ Fix the generator code that saves incorrectly
✅ Regenerate to verify fix persists
✅ Ask: "Should I fix UnifiedMaterialsGenerator.save() logic?"
```

### **Pattern 4: Not Testing Against Actual Quality**
**What Happened**: AI-like phrases detected: "presents a unique challenge", "critical pitfall", formulaic structure
**Why It's Grade D**: Content reads like AI technical manual, not human writing
**Correct Behavior**:
```
✅ Check for AI tell-tale phrases:
  - "presents a [unique/primary/significant] challenge"
  - "[critical/significant/primary] pitfall"  
  - "This [property/balance/approach] is essential for"
  - Formulaic structure (challenge → solution → importance)
✅ Verify natural human voice
✅ Reject robotic/textbook language
```

### **Pattern 5: Learned Parameters Producing Poor Quality**
**What Happened**: Sweet spot learning stored temp=0.815 but correlation showed temp has NEGATIVE correlation (-0.515)
**Why It's Grade C**: Learning system storing parameters that hurt quality
**Correct Behavior**:
```
✅ Check learned parameter correlations
✅ Question parameters with negative correlation
✅ Verify sweet spot samples include recent high-quality content
✅ Test: Does lower temperature produce better results?
```

### **Pattern 6: Treating Symptoms Instead of Root Causes** 🔥 **NEW (Nov 22, 2025) - CRITICAL**
**What Happened**: Word counts consistently 20-50% over target (150-194 words vs 50-150 max). AI added stricter prompt instructions 5+ times instead of fixing the actual mechanism.
**Why It's Grade F**: 
- Repeated the same failed approach multiple times
- Added "CRITICAL" warnings to prompts that were already being ignored
- Never addressed the real issue: LLMs don't count words during generation
- Wasted user's time with solutions that couldn't work

**What AI Did Wrong**:
1. ❌ Fixed hardcoded "150-450 words" in template (good fix, but insufficient)
2. ❌ Added "CRITICAL: Stay within word count" to prompt (ignored by model)
3. ❌ Added "DO NOT EXCEED THE MAXIMUM" instruction (also ignored)
4. ❌ Added placeholder `[TARGET_LENGTH_DISPLAY]` that was never replaced
5. ❌ Never checked if prompt instructions were even being used
6. ❌ Never measured actual word counts after each "fix"
7. ❌ Never questioned why prompt-only approach kept failing

**Root Cause Ignored**: LLMs generate token-by-token without counting words. Prompt instructions alone cannot enforce strict limits.

**Why max_tokens Won't Work**: Lowering max_tokens causes mid-sentence truncation, creating broken/incomplete content. This is WORSE than being over the word count.

**The Fundamental Truth**:
```
❌ Prompt instructions alone: LLMs ignore word counts
❌ Strict max_tokens: Causes truncation and broken sentences
❌ Post-generation truncation: Also breaks sentences
✅ Reality: Approximate word counts are inherent to LLM architecture
```

**Correct Behavior**:
```
✅ Measure results after EACH fix attempt (don't assume it worked)
✅ When same approach fails 2+ times, question the approach itself
✅ Ask: "Why do prompt instructions keep getting ignored?"
✅ Research: What is ACTUALLY possible with LLM architecture?
✅ Accept architectural limitations: "approximately X words" not strict limits
✅ Be honest with user: "LLMs consistently generate 20-30% over target"
✅ Offer real solutions:
   - Option A: Accept approximate word counts (150-180w for 150w target)
   - Option B: Use quality-gated mode with multiple attempts and selection
   - Option C: Post-generation editing (manual review required)
✅ DO NOT waste time on solutions that can't work (more prompt keywords)
```

**Prevention Checklist**:
- [ ] Did I measure the actual result after my fix?
- [ ] Am I repeating the same approach that already failed?
- [ ] Am I treating a symptom (prompt text) vs architectural limitation?
- [ ] Do I understand what is ACTUALLY POSSIBLE with this technology?
- [ ] Have I been honest about what can't be fixed?

**Red Flags That You're Treating Symptoms**:
- 🚩 Adding more "CRITICAL" or "IMPORTANT" keywords to prompts
- 🚩 Making text BOLD or adding emoji to existing instructions
- 🚩 Rephrasing the same instruction in different words
- 🚩 Adding duplicate requirements in multiple places
- 🚩 Not measuring actual results after each change
- 🚩 Assuming "this time it will work" without architectural change
- 🚩 Proposing max_tokens limits (causes truncation)
- 🚩 Proposing post-generation truncation (also causes truncation)

**Grade**: F - Wasting user time with ineffective solutions violates TIER 3 honesty requirements

### **Pattern 7: Architectural Documentation Inconsistency** 🔥 **NEW (Nov 22, 2025) - CRITICAL**
**What Happened**: Multiple documents claimed different architectures were "COMPLETE":
- `E2E_SYSTEM_ANALYSIS_NOV22_2025.md`: Graded system A+ assuming "Option C" active
- `OPTION_C_IMPLEMENTATION_NOV22_2025.md`: Documented "quality gates removed"
- **Reality**: Code still enforced quality gates (10% success rate proved it)

**Why It's Grade F**: 
- Wastes effort on wrong diagnosis
- User cannot trust documentation
- Future work builds on false assumptions
- Regression goes undetected

**Correct Behavior**:
```
✅ MEASURE actual behavior (success rate, terminal output, test results)
✅ If metrics contradict docs → Documentation is WRONG
✅ Write verification tests BEFORE claiming "COMPLETE"
✅ Update ALL related docs when architecture changes
✅ Never grade system A+ without verifying claims with tests
✅ Use correct data access patterns when verifying (dict vs list)
```

**How to Detect This Pattern**:
- 🚩 Success rate doesn't match documented behavior (10% ≠ "saves all")
- 🚩 Terminal output contradicts documentation claims
- 🚩 User reports failures but docs claim success
- 🚩 Multiple documents describe different implementations
- 🚩 High grade (A+) but low success metrics (10%)
- 🚩 Verification scripts report failure when direct file inspection shows success

**Prevention**:
```
Before documenting as "COMPLETE":
1. Write test: test_[feature]_actually_works()
2. Run live test: python3 run.py --[feature]
3. Measure metrics: Success rate, save count, terminal output
4. Compare: Do metrics match documentation claims?
5. Verify data access patterns match actual structure (dict vs list)
6. If NO → Fix code OR fix docs, then retest
7. Only claim "COMPLETE" when test + metrics verify it
```

**✅ RESOLVED (Nov 23, 2025)**: Property research verification issue - materials were successfully researched and populated in Materials.yaml. Initial "NOT FOUND" reports were due to verification script bugs using list iteration on dict structure. Correct access pattern: `data['materials'][material_name]` not `next((m for m in materials...))`.

---

## 🔒 **PROTECTED FILES POLICY** 🔥 **NEW (Dec 6, 2025) - CRITICAL**

**MANDATORY: Check `.github/PROTECTED_FILES.md` before modifying any file.**

### Quick Reference - Files That Require Permission

**TIER 1 (NEVER TOUCH without explicit permission)**:
- `shared/voice/profiles/*.yaml` - Author voice definitions
- `domains/*/prompts/*.txt` - Domain prompt templates
- `generation/core/evaluated_generator.py` - Main generation orchestrator (25KB+)
- `generation/core/generator.py` - Core generation logic
- `shared/text/utils/prompt_builder.py` - Prompt assembly (has known bug, needs surgical fix only)

**TIER 2 (ASK FIRST)**:
- `generation/config.yaml`, `domains/*/config.yaml` - All configuration files
- `data/materials/Materials.yaml`, `data/settings/Settings.yaml` - Primary data files
- `learning/*.py` - Learning system files

**TIER 3 (VERIFY WITH TESTS)**:
- `domains/*/coordinator.py` - Coordination logic
- `domains/*/data_loader.py` - Data loading utilities
- `shared/text/adapters/*.py` - Domain adapters

### Required Protocol

**Before ANY modification**:
1. Check if file is in `.github/PROTECTED_FILES.md`
2. If TIER 1: **STOP and ASK user for permission**
3. If TIER 2: **EXPLAIN impact and wait for approval**
4. If TIER 3: **PROCEED but verify with tests**

**Common Mistakes to Avoid**:
- ❌ "The prompt isn't working" → Rewriting prompt file
- ❌ "Generation is slow" → Modifying generator.py
- ❌ "Voice needs work" → Changing persona files
- ✅ **ALWAYS ask first, suggest minimal changes, respect existing architecture**

**Full details**: `.github/PROTECTED_FILES.md`

---

## 📖 **Detailed Navigation for AI Assistants**

**🔍 Already checked 30-SECOND QUICK START above?** If not, scroll to top first.

### **User Requests Content Generation?**
→ **READ THIS FIRST**: `.github/COPILOT_GENERATION_GUIDE.md`
- Handles: "Generate material description for Aluminum", "Create micro for Steel", etc.
- Shows: Exact commands to run, terminal output handling, result reporting
- Covers: All component types (description, micro, FAQ, settings_description)

### **Need Documentation?**
→ **PRIMARY GUIDE**: `docs/08-development/AI_ASSISTANT_GUIDE.md` - 30-second navigation (NEW)
→ **COMPLETE MAP**: Root `/DOCUMENTATION_MAP.md` - All documentation indexed
→ **QUICK ANSWERS**: `docs/QUICK_REFERENCE.md` - Fastest path to solutions
→ **SYSTEM INDEX**: `docs/INDEX.md` - Comprehensive navigation

### **Working on Code/Architecture?**
→ **READ FIRST**: `docs/SYSTEM_INTERACTIONS.md` - Understand cascading effects before changing anything
→ **THEN CHECK**: `docs/decisions/README.md` - Architecture Decision Records (WHY things work this way)
→ **CHECK POLICIES**: `docs/08-development/` - All development policies and guidelines
→ **Continue below** for comprehensive rules and examples

### **⚠️ Before Making ANY Change**
1. **Check `docs/SYSTEM_INTERACTIONS.md`**: What will your change affect?
2. **Check `docs/decisions/`**: Is there an ADR about this?
3. **Check git history**: Has this been tried and failed before?
4. **Check `docs/08-development/`**: Is there a policy document about this?
5. **Plan minimal fix**: Address only the specific issue

---

## 🚦 **TIER PRIORITIES** - Critical Rules Hierarchy

Understanding rule severity helps prioritize fixes and avoid introducing worse problems.

### 🔴 **TIER 1: SYSTEM-BREAKING** (Will cause failures)
1. ❌ **NO mocks/fallbacks in production code** (tests OK) - [Rule #2](#rule-2-zero-production-mocksfallbacks)
2. ❌ **NO hardcoded values/defaults** (use config/dynamic calc) - [Rule #3](#rule-3-fail-fast-on-setup--zero-hardcoded-values)
3. ❌ **NO rewriting working code** (minimal surgical fixes only) - [Rule #1](#rule-1-preserve-working-code)

### 🟡 **TIER 2: QUALITY-CRITICAL** (Will cause bugs)
4. ❌ **NO expanding scope** (fix X means fix ONLY X) - [Rule #5](#rule-5-surgical-precision)
5. ❌ **NO skipping validation** (must test before claiming success) - [Step 6](#step-6-implement--test)
6. ✅ **ALWAYS fail-fast on config** (throw exceptions, no silent degradation) - [Rule #3](#rule-3-fail-fast-on-setup--zero-hardcoded-values)
7. ✅ **ALWAYS preserve runtime recovery** (API retries are correct) - See ADRs
8. ✅ **ALWAYS log to terminal** (all generation attempts, scores, feedback) - See Terminal Output Policy

### 🟢 **TIER 3: EVIDENCE & HONESTY** (Will lose trust)
9. ✅ **ALWAYS provide evidence** (test output, counts, commits) - [Verification Protocol](#mandatory-verify-before-claiming-success)
10. ✅ **ALWAYS be honest** (acknowledge what remains broken) - [Step 7](#step-7-honest-reporting)
11. ✅ **ASK before major changes** (get permission for improvements) - [Rule #1](#rule-1-preserve-working-code)
12. ✅ **VERIFY before claiming violations** (check config files, confirm pattern exists) - [Step 6](#step-6-verify-before-claiming-violations)
13. 🔥 **NEVER report success when quality gates fail** (realism < 5.5, Winston fail) - [Pattern 1](#critical-failure-patterns-to-avoid)
14. 🔥 **ALWAYS read ALL evaluation scores** (pre-save AND post-generation) - [Pattern 2](#critical-failure-patterns-to-avoid)
15. 🔥 **ALWAYS check for AI-like phrases** ("presents a challenge", formulaic structure) - [Pattern 4](#critical-failure-patterns-to-avoid)
16. 🔥 **ALWAYS verify implementation before documentation** (write tests, measure success rate) - [Pattern 0](#critical-failure-patterns-to-avoid) **NEW**
17. 🔥 **NEVER document features without evidence** (tests prove it works) - [Step 6.5](#step-6-5-verify-implementation-matches-documentation) **NEW**

**🚨 CRITICAL: Reporting success when quality fails is a TIER 3 violation - Grade F.**
**🚨 CRITICAL: Documenting unimplemented features as "COMPLETE" is a TIER 3 violation - Grade F.** 🔥 **NEW**

---

## 🚦 **DECISION TREES** - When in Doubt, Use These

### Decision: Should I use a default value?
```
Is this a config/setup issue?
├─ YES → ❌ FAIL FAST (throw ConfigurationError)
└─ NO → Is this a runtime/transient issue?
    ├─ YES → ✅ RETRY with backoff (API timeout, network error)
    └─ NO → Is this a quality check iteration?
        ├─ YES → ✅ ITERATE (adjust parameters based on feedback)
        └─ NO → ❌ FAIL FAST (programming error)
```

### Decision: Should I rewrite this code?
```
Does the code work correctly?
├─ YES → ❌ NO REWRITE (integrate around it, add method, minimal fix)
└─ NO → Is it a small targeted fix?
    ├─ YES → ✅ FIX ONLY broken part
    └─ NO → ⚠️ ASK PERMISSION (explain why rewrite needed)
```

### Decision: Should I add a hardcoded value?
```
Can I find an existing dynamic solution?
├─ YES → ✅ USE IT (grep_search for DynamicConfig, helpers)
└─ NO → Is this truly a constant?
    ├─ YES → ✅ CONFIG FILE (config.yaml, not code)
    └─ NO → ⚠️ ASK USER (explain why dynamic solution doesn't exist)
```

---

## 📋 **TERMINAL OUTPUT LOGGING POLICY**

**ALL generation operations MUST stream comprehensive output to terminal in real-time.**

**Logging Requirements**:
1. **Stream to stdout/stderr ONLY** - No log files created or saved
2. **Real-time output** - User sees progress as it happens
3. **Attempt Progress** - Every retry with attempt number (e.g., "Attempt 2/5")
4. **Quality Checks** - Winston score, Realism score, thresholds, pass/fail
5. **Feedback Application** - Parameter adjustments between attempts
6. **Learning Activity** - Prompt optimization, pattern learning
7. **Final Report** - Complete generation report (see Generation Report Policy)

**Example Streaming Output**:
```
Attempt 2/5
🌡️  Temperature: 0.750 → 0.825
📉 Frequency penalty: 0.20 → 0.30
Winston Score: 98.6% human ✅ PASS
Realism Score: 5.0/10 (threshold: 5.5) ❌ FAIL
✅ [REALISM FEEDBACK] Parameter adjustments calculated
```

**Implementation**:
- Use `print()` for terminal output (not `logger.info()` to files)
- All subprocess calls inherit stdout/stderr (no capture)
- Batch tests stream directly (no tee to log files)

**Purpose**: User visibility, debugging, transparency, verification

**Anti-Patterns**: 
- ❌ Silent failures, hidden retries, opaque processing
- ❌ Log files in /tmp/ or elsewhere
- ❌ Capturing output without displaying it

---

## 📋 **IMAGE GENERATION MONITORING POLICY** 🔥 **NEW (Nov 30, 2025)**

**AI assistants MUST actively monitor image generation terminal output for bottlenecks.**

**Monitoring Requirements**:
1. **Watch for slow stages** - If any stage takes >30 seconds without output, investigate
2. **Identify API timeouts** - Note if Imagen or Gemini calls exceed expected times
3. **Report hanging operations** - If no output for 60+ seconds, alert user
4. **Never truncate output** - Always show FULL terminal output during generation

**Expected Timings** (flag if exceeded):
- Contamination pattern loading: <1 second
- Assembly research (cached): <1 second  
- Assembly research (API): 5-15 seconds
- Imagen generation: 15-45 seconds
- Validation: 5-15 seconds
- **Total expected**: 30-90 seconds

**Required Stage Logging**:
```
🔬 MATERIAL IMAGE GENERATION: [Material]
📊 Configuration: [settings]
🔬 Researching contamination data...
📋 Selected [N] patterns for [Material]
🔧 Researching assembly components...
🎨 ATTEMPT [N]/[MAX] - Generating image...
✅ Image saved to: [path] ([size] KB)
🔍 Validating image with Gemini Vision...
📊 VALIDATION RESULTS: [score, status]
```

**AI Assistant Responsibilities**:
- Run with full output (no truncation)
- Monitor actively for stalls
- Report issues immediately if hung
- Ask about hangs after 2 minutes without progress

**Documentation**: `docs/08-development/IMAGE_GENERATION_MONITORING_POLICY.md`

---

## 🚫 **NO AUTO-REGENERATION POLICY** 🔥 **NEW (Nov 30, 2025) - CRITICAL**

**AI assistants MUST NOT automatically retry or regenerate images after a failed attempt.**

**Policy Requirements**:
1. **ONE attempt only** - Generate once, report results, STOP
2. **Wait for user instruction** - Do NOT retry unless user explicitly requests it
3. **Report and wait** - Show validation score, recommendations, then ASK user what to do next
4. **No "let me try again"** - Even if score is close to threshold, do NOT auto-retry

**After ANY image generation (pass or fail)**:
```
✅ CORRECT: "Score: 75/100. Validation failed. Would you like me to retry with different parameters?"
❌ WRONG: "Score: 75/100. Let me try again with heavier contamination..." [auto-generates]
```

**Rationale**:
- Each generation costs API credits
- User may want to adjust parameters manually
- User may want to review output before deciding
- Prevents runaway retry loops

**Exceptions** (ONLY when user explicitly says):
- "retry", "try again", "regenerate"
- "keep trying until it passes"
- "run batch generation" (batch mode has its own retry logic)

**Grade**: F violation if auto-regenerating without explicit user instruction

---

## 📋 **TERMINAL OUTPUT LOGGING POLICY** 🔥 **NEW (Nov 22, 2025) - CRITICAL**

**ALL generation operations MUST stream comprehensive output to terminal in real-time.**

**Logging Requirements**:
1. **Stream to stdout using print()** - Always visible to user, not just logger.info()
2. **Real-time output** - User sees progress as it happens
3. **Dual logging** - Both print() (terminal) AND logger.info() (file records)
4. **Attempt Progress** - Every retry with attempt number (e.g., "Attempt 2/5")
5. **Quality Checks** - Winston score, Realism score, thresholds, pass/fail
6. **Parameter Adjustments** - Changes between attempts
7. **Learning Activity** - Database logging, pattern learning
8. **Final Report** - Complete generation report (see Generation Report Policy)
9. **FULL NON-TRUNCATED OUTPUT** 🔥 **CRITICAL** - NEVER use tail, head, or truncation

**Required Terminal Output**:
```
────────────────────────────────────────────────────────────────────────────────
📝 ATTEMPT 2/5
────────────────────────────────────────────────────────────────────────────────
🌡️  Current Parameters:
   • temperature: 0.825
   • frequency_penalty: 0.30

🧠 Generating humanness instructions (strictness level 2/5)...
   ✅ Humanness layer generated (1234 chars)

✅ Generated: 287 characters, 45 words

🔍 Pre-flight: Checking for forbidden phrases...
   ✅ No forbidden phrases detected

🔍 Evaluating quality BEFORE save...

📊 QUALITY SCORES:
   • Overall Realism: 8.5/10
   • Voice Authenticity: 8.0/10
   • Tonal Consistency: 7.5/10
   • AI Tendencies: None detected

📉 ADAPTIVE THRESHOLD: 5.2/10 (relaxed from 5.5 for attempt 2)

   📊 Logged attempt 2 to database (detection_id=779, passed=False)

⚠️  QUALITY GATE FAILED - Will retry with adjusted parameters
   • Realism score too low: 5.0/10 < 5.5/10

🔧 Adjusting parameters for attempt 3...
   ✅ Parameters adjusted for retry

🔄 Parameter changes for next attempt:
   • temperature: 0.825 → 0.900
   • frequency_penalty: 0.30 → 0.40
```

**Implementation Pattern**:
```python
# Terminal output (always visible)
print(f"📊 QUALITY SCORES:")
print(f"   • Overall Realism: {score:.1f}/10")

# File logging (for records)
logger.info(f"📊 QUALITY SCORES:")
logger.info(f"   • Overall Realism: {score:.1f}/10")
```

**Documentation**: `docs/08-development/TERMINAL_LOGGING_POLICY.md`
**Tests**: `tests/test_terminal_logging_policy.py` - 12 tests verify compliance
**Enforcement**: All generation operations must use dual logging (print + logger)

**Anti-Patterns**: 
- ❌ Silent operations (logger.info() only, no print())
- ❌ Hidden retries (no terminal visibility)
- ❌ Batch output at end (should stream in real-time)
- ❌ Log files only (user can't see what's happening)
- ❌ **TRUNCATED OUTPUT** (tail -n, head -n, or any output limiting) 🔥 **CRITICAL**

**Grade**: MANDATORY - Non-compliance is a policy violation

---

## 🛡️ **MANDATORY: Pre-Code Execution Protocol** 🔥 **UPDATED (Nov 22, 2025)**

**🛑 STOP - Complete ALL checks BEFORE writing any code:**

**📖 Quick Reference**: See `docs/08-development/AI_ASSISTANT_GUIDE.md` for streamlined checklist

### ✅ Phase 1: Verification (2-3 minutes)
- [ ] **Read request word-by-word** - What EXACTLY is being asked?
- [ ] **Check for assumptions** - Am I assuming anything not stated?
- [ ] **Verify file paths** - Do all referenced files actually exist?
- [ ] **Check config keys** - Do claimed violations actually exist in config files?
- [ ] **Search for existing solutions** - Does DynamicConfig/helper already solve this?

### ✅ Phase 2: Research (3-5 minutes)
- [ ] **grep_search for patterns** - How does the system currently handle this?
- [ ] **Read relevant code** - Understand current implementation
- [ ] **Check git history** - Was this tried before? Why was it changed?
- [ ] **Review docs/** - Is there policy documentation on this?
- [ ] **Check ADRs** - Is there an architectural decision about this?

### ✅ Phase 3: Planning (2-3 minutes)
- [ ] **Identify exact change needed** - One sentence description
- [ ] **Confirm minimal scope** - Am I fixing ONLY what was requested?
- [ ] **Check for side effects** - What else might this affect?
- [ ] **Plan validation** - How will I prove it works?
- [ ] **Get permission if major** - Ask before removing/rewriting code

### 🚨 **STOP SIGNALS** - When to ASK instead of CODE:
- ❓ If you're not 100% certain about the requirement
- ❓ If you can't find the config key/file/pattern being referenced
- ❓ If fixing this requires changing more than 3 files
- ❓ If you're about to add a hardcoded value without finding dynamic config first
- ❓ If the request conflicts with existing architecture
- ❓ If tests are failing and you don't understand why

**⏱️ Time Investment**: 7-11 minutes of research prevents hours of fixing broken code.

---

## 🎯 Quick Reference Card

**READ THIS FIRST - BEFORE ANY CHANGE:**

1. ✅ **Read the request precisely** - What is the *exact* issue?
2. ✅ **Search documentation FIRST** - Check `docs/` for existing guidance (see Documentation Compliance Checklist below)
3. ✅ **Explore existing architecture** - Understand how it currently works
4. ✅ **Check git history for context** - See what was working previously
5. ✅ **Plan minimal fix only** - Address only the specific issue
6. ✅ **Ask permission for major changes** - Get approval before removing code or rewrites
7. ✅ **🔥 Verify with tests BEFORE claiming complete** - Evidence over assumptions

**GOLDEN RULES:**
- 🚫 **NEVER rewrite working code**
- 🚫 **NEVER expand beyond requested scope**
- 🚫 **NEVER bypass text processing pipeline** - ALL text uses QualityEvaluatedGenerator 🔥 **NEW (Dec 11, 2025)**
- 🚫 **NEVER generate text with direct API calls** - Use pipeline ONLY 🔥 **NEW (Dec 11, 2025)**
- 🚫 **NEVER put voice instructions outside personas/*.yaml** - Single source only 🔥 **NEW (Dec 11, 2025)**
- 🚫 **NEVER embed prompts in content generators** - Use template files ONLY 🔥 **NEW (Dec 29, 2025)**
- 🚫 **NEVER restrict word counts using max_tokens** - Causes mid-sentence truncation 🔥 **NEW (Dec 24, 2025)**
- 🚫 **NEVER use enrichers to add missing data** - Generate complete data during generation 🔥 **NEW (Jan 2, 2026)**
- 🚫 **NEVER use mocks/fallbacks in production code - NO EXCEPTIONS**
- ✅ **ALLOW mocks/fallbacks in test code for proper testing**
- ✅ **ALLOW embedded prompts in research scripts** - Data discovery OK 🔥 **NEW (Dec 29, 2025)**
- 🚫 **NEVER add "skip" logic or dummy test results**
- 🚫 **NEVER put content instructions in /processing folder code**
- 🚫 **NEVER hardcode component types in /processing code**
- 🚫 **NEVER hardcode values in production code** - use config or dynamic calculation
- 🚫 **NEVER claim "COMPLETE" without verification tests** 🔥 **NEW**
- 🚫 **NEVER document features as implemented without evidence** 🔥 **NEW**
- ✅ **ALWAYS keep content instructions ONLY in prompts/*.txt files**
- ✅ **ALWAYS define components ONLY in prompts/*.txt and config.yaml**
- ✅ **ALWAYS preserve existing patterns**
- ✅ **ALWAYS fail-fast on configuration issues**
- ✅ **ALWAYS maintain runtime error recovery**
- ✅ **ALWAYS verify documentation matches reality with tests** 🔥 **NEW**
- ✅ **ALWAYS sync Materials.yaml updates to frontmatter (dual-write)** 🔥 **NEW (Nov 22, 2025)**
- ✅ **ALWAYS save to frontmatter whenever you save to data** 🔥 **MANDATORY (Dec 12, 2025)**
- ✅ **ALWAYS generate complete data to YAML** - Enrichers format, not add data 🔥 **NEW (Jan 2, 2026)**

---

## 📚 Recent Critical Updates

### 🎭 Voice Pattern Compliance System (December 13, 2025) 🔥 **NEW**
**Status**: ✅ IMPLEMENTED - Automated validation of author-specific linguistic patterns

**Problem**: Generic technical writing across all authors despite rich persona definitions. Content read like identical AI-generated text regardless of nationality.

**Solution**: 
1. **Relaxed Domain Prompt**: Changed from "single sentence" to "1-2 sentences" + added explicit voice reminder
2. **Pattern Compliance Validation**: Automated checking for nationality-specific linguistic patterns

**Implementation**:
- `domains/materials/prompts/description.txt`: Relaxed constraint + voice emphasis
- `shared/voice/quality_analyzer.py`: New `_check_pattern_compliance()` method
- `tests/test_voice_pattern_compliance.py`: 11 tests validating all 4 nationalities

**Pattern Detection**:
- **US**: Phrasal verbs ("line up", "ramp up"), quantified outcomes ("by 20%"), practical transitions
- **Taiwan**: Topic-comment structures, article omission, temporal markers
- **Italy**: Cleft structures, subjunctive hedging, Romance cognates
- **Indonesia**: Topic prominence ("This X, it..."), aspectual markers ("already", "still", "just now"), preposition patterns ("from the data", "at the surface") - **STRENGTHENED (Dec 26, 2025)**: Frequency increased to 2-3 per paragraph for better detection

**Results**:
- Voice Authenticity: None/100 → **85.0/100** (+85 points)
- Phrasal verbs now appearing in US content ("ramp up", "holds up")
- Natural 2-sentence structures (not forced single sentence)
- Pattern detection operational across all nationalities
- **Indonesian patterns strengthened**: Expected detection 60-80% (from 0%)

**Documentation**: `VOICE_COMPLIANCE_IMPLEMENTATION_DEC13_2025.md`

### 🚀 Learning System Improvements (November 22, 2025)
**Status**: ✅ Priority 1 & 2 COMPLETE - System producing 50x more learning data

**Problem Solved**: Quality gates blocked 90% of content from learning system, creating "quality-learning death spiral"
**Solution**: Multi-phase approach enabling learning while maintaining quality standards

**Implementations**:
1. **Priority 1 - Log ALL Attempts** (✅ COMPLETE):
   - Added `_log_attempt_for_learning()` method (~160 lines)
   - Logs EVERY attempt BEFORE quality gate decision (not just successes)
   - Result: **50x more learning data** (5 attempts/material vs 0.1 success/material)
   - Database captures: Winston scores, subjective evaluation, structural diversity, ALL parameters
   - Enables correlation analysis and sweet spot improvements

2. **Priority 2 - Adaptive Threshold Relaxation** (✅ COMPLETE):
   - Added `_get_adaptive_threshold()` method with graduated relaxation
   - Thresholds: Attempt 1 (5.5/10) → 2 (5.3) → 3 (5.0) → 4 (4.8) → 5 (4.5)
   - Result: Expected **29% → 50-70% success rate**
   - Maintains quality floor (4.5/10 minimum) while reducing 70% waste
   - Verified working: Terminal shows "📉 ADAPTIVE THRESHOLD: 5.2/10 (relaxed from 5.5 for attempt 2)"

**Future Priorities** (Ready for implementation):
- Priority 3: Opening pattern cooldown (5 hours) - Reduce 10/10 repetition → 2/10
- Priority 4: Correlation filter (3 hours) - Exclude negative correlation parameters
- Priority 5: Two-phase strategy (6 hours) - Exploration → exploitation approach

**Documentation**: 
- `LEARNING_IMPROVEMENTS_NOV22_2025.md` - Complete implementation guide
- `LEARNING_SYSTEM_ANALYSIS_NOV22_2025.md` - Original analysis and recommendations
- `PRIORITY1_COMPLETE_NOV22_2025.md` - Priority 1 detailed documentation

**Policy Compliance**: 100% compliant - fail-fast architecture, zero hardcoded values, template-only
**Grade**: Priority 1: A+ (100/100), Priority 2: A (95/100)

### 🚨 Mock/Fallback Violations Eliminated (November 20, 2025) 🔥 **CRITICAL**
**Status**: ✅ FIXED - 26 violations eliminated, 24/24 tests passing

**Discovery**: Batch test revealed Winston API unconfigured but system continuing with fake scores (100% human, 0% AI)
**Grade**: Grade F violation of GROK_QUICK_REF.md TIER 3: Evidence & Honesty

**Violations Fixed**:
1. **generation.py**: Silent Winston failure → RuntimeError (fail-fast)
2. **generation.py**: Hardcoded temperature=0.7 → None (metadata only)
3. **constants.py**: Removed DEFAULT_AI_SCORE, DEFAULT_HUMAN_SCORE, DEFAULT_FALLBACK_AI_SCORE
4. **batch_generator.py**: 13 violations - removed skip logic, fallback scores, mock data, hardcoded penalties
5. **run.py**: Marked --skip-integrity-check as [DEV ONLY] with warnings
6. **integrity_helper.py**: 3 violations - fixed silent failures on exceptions
7. **subtitle_generator.py**: Removed hardcoded temperature (0.6), now uses dynamic config
8. **evaluated_generator.py**: Removed TODO, documented design decision
9. **threshold_manager.py**: 2 TODOs → documented as future work with design rationale
10. **test_score_normalization_e2e.py**: Updated tests to remove assertions on deleted constants

**Enforcement**:
- System now raises RuntimeError if Winston API unavailable
- All `.get('score', default)` patterns replaced with fail-fast None checks
- No fallback scores available - validation REQUIRED
- Skip flags marked DEV ONLY with explicit warnings

**Documentation**: 
- `VIOLATION_FIXES_NOV20_2025.md` - Complete fix documentation with before/after code
- `TEST_RESULTS_NOV20_2025.md` - Test execution before violations discovered

**Policy Compliance**: 100% compliant with Core Principle #2 (No Mocks/Fallbacks)
**Grade**: System upgraded from Grade F to A+ (100/100) after complete remediation

### ✅ Learned Evaluation Pipeline Integration (November 18, 2025) 🔥 **NEW**
**Status**: ✅ IMPLEMENTED AND TESTED (17/17 tests passing)

**What**: Complete pipeline for template-based evaluation with continuous learning
**Components**:
- `prompts/evaluation/subjective_quality.txt` - Template for evaluation prompts (no hardcoded prompts in code)
- `prompts/evaluation/learned_patterns.yaml` - Auto-updating learned patterns from evaluations
- `processing/learning/subjective_pattern_learner.py` - Learning system with exponential moving averages
- Integration: SubjectiveEvaluator loads templates, generator updates patterns after each evaluation

**Learning Flow**:
1. Content generated
2. Evaluator loads template + learned patterns from files
3. Grok evaluates content
4. Pattern learner updates YAML (rejection patterns: AI tendencies, theatrical phrases)
5. If accepted: Pattern learner updates success patterns (EMA with alpha=0.1)
6. Next generation uses updated patterns

**Files Changed**:
- NEW: `prompts/evaluation/subjective_quality.txt` (template)
- NEW: `prompts/evaluation/learned_patterns.yaml` (learning data)
- NEW: `processing/learning/subjective_pattern_learner.py` (learner)
- NEW: `tests/test_learned_evaluation_pipeline.py` (17 tests ✅)
- MODIFIED: `processing/subjective/evaluator.py` (template integration)
- MODIFIED: `processing/generator.py` (learning integration)

**Documentation**: 
- `LEARNED_EVALUATION_INTEGRATION_NOV18_2025.md` - Complete implementation summary
- `docs/08-development/LEARNED_EVALUATION_PROPOSAL.md` - Architecture (now IMPLEMENTED)

**Policy Compliance**:
- ✅ Prompt Purity Policy: Zero hardcoded prompts in evaluator code
- ✅ Fail-Fast Architecture: Template missing → FileNotFoundError
- ✅ Learning Integration: Works with Winston, Realism, Composite scoring

**Grade**: A+ (100/100) - Full implementation, all tests passing

### ✅ Priority 1 Compliance Fixes (November 17, 2025)
**Commit**: c5aa1d6c - All critical violations resolved

1. **RealismOptimizer Import Fixed**: Corrected path from `processing.realism.optimizer` to `processing.learning.realism_optimizer`
2. **SubjectiveEvaluator Temperature**: Now configurable via parameter (no hardcoded values)
3. **Fail-Fast Architecture Enforced**: Removed non-existent fallback method calls

**Documentation**: 
- `docs/archive/2025-11/E2E_PROCESSING_EVALUATION_NOV17_2025.md` - Full evaluation report
- `docs/archive/2025-11/PRIORITY1_UPDATES_COMPLETE.md` - Implementation summary
- `tests/test_priority1_fixes.py` - 10 automated tests (all passing ✅)

**Grade**: System upgraded from C+ to B+ (85/100) after fixes

### 🎯 Prompt Purity Policy (November 18, 2025) 🔥 **CRITICAL**
**Issue**: Prompt instructions hardcoded in generator code (orchestrator.py, generator.py)
**Fix**: All content instructions MUST exist ONLY in prompts/*.txt files
**Violations Found**: 5 critical violations (system_prompt hardcoding, inline CRITICAL RULE text)
**Policy**: ZERO prompt text permitted in generators - use _load_prompt_template() only
**Documentation**: docs/08-development/PROMPT_PURITY_POLICY.md

### 🎯 Realism Quality Gate Enforcement (November 18, 2025) 🔥 **CRITICAL**
**Issue**: Subjective evaluation was running but NOT rejecting low-quality content
**Fix**: Realism score (7.0/10 minimum) now enforced as quality gate
**Impact**: Content with AI issues (theatrical phrases, casual language) now REJECTED
**Learning**: Both Winston and Realism feedback drive parameter adjustments on retry

### 🎯 Composite Quality Scoring (November 16, 2025)
**Architecture**: GENERIC_LEARNING_ARCHITECTURE.md implemented
- Winston (40%) + Realism (60%) weighting for combined score
- Realism gate: 7.0/10 minimum threshold (enforced)
- Adaptive threshold learning from 75th percentile of successful content
- Sweet spot analyzer uses composite scores for parameter optimization

### 🗣️ Content Instruction Policy
**CRITICAL**: Content instructions ONLY in `prompts/*.txt` files, NEVER in code
- Format rules, style guidance, focus areas → prompts/
- Technical mechanisms only → processing/
- See: `docs/prompts/CONTENT_INSTRUCTION_POLICY.md`

### 📝 Embedded Prompts Policy 🔥 **NEW (Dec 29, 2025) - CRITICAL**
**MANDATORY: Distinguish between CONTENT generation and DATA research.**

**❌ FORBIDDEN - User-Facing Content Generation:**
Content displayed on website MUST use prompt templates ONLY:
```python
# ❌ WRONG: Embedded prompt for content
def generate_description(material):
    prompt = f"You are {author}. Write a description..."
    return api.generate(prompt)

# ✅ CORRECT: Load from template
def generate_description(material):
    template = self._load_prompt_template('description.txt')
    return self.generator.generate(material, 'description')
```

**Applies to:**
- ✅ Descriptions, FAQs, micros, excerpts
- ✅ Any text displayed on website
- ✅ Content with author voice/style
- ✅ All components in `domains/*/prompts/*.txt`

**✅ ALLOWED - Technical Data Research:**
Research scripts for property discovery can use inline prompts:
```python
# ✅ CORRECT: Research script for data population
def research_melting_point(material):
    prompt = f"What is the melting point of {material}? Return only numeric value."
    return api.generate(prompt)
```

**Applies to:**
- ✅ Property discovery (melting points, thermal conductivity, NFPA codes)
- ✅ One-time data population scripts (`scripts/research/*.py`)
- ✅ Backfill operations (`generation/backfill/*.py`)
- ✅ Research infrastructure (`domains/*/research/*.py`)

**Key Distinction:**
- **CONTENT** = What users read → Template files ONLY
- **DATA** = Technical properties → Inline prompts OK

**Verification:**
```bash
# Check for violations in content generators
grep -r "prompt.*=.*You are" generation/core/ domains/*/coordinator.py
# Result should be: 0 matches

# Research scripts can have embedded prompts (acceptable)
grep -r "prompt.*=.*You are" scripts/research/
# Result: Multiple matches (acceptable for data research)
```

**Grade:** F violation if content generators have embedded prompts

---

## 📖 Core Principles

### 0. **Universal Text Processing Pipeline** 🔥 **NEW MANDATE (Dec 11, 2025)**
ALL text generation MUST go through the standardized processing pipeline. **ZERO EXCEPTIONS**.

**MANDATORY ARCHITECTURE:**
- ✅ **ALL domains use QualityEvaluatedGenerator** - materials, contaminants, settings, future domains
- ✅ **ONLY `shared/voice/profiles/*.yaml` defines voice** - Single source of truth for author voice
- ✅ **NO bypassing pipeline** - No direct API calls, no custom generation logic
- ❌ **NO voice instructions in domain prompts** - Use `{voice_instruction}` placeholder only
- ❌ **NO text generation outside pipeline** - Every text component uses evaluated_generator

**Pipeline ensures:**
- Author voice consistency (persona-based, immutable)
- AI detection avoidance (humanness layer)
- Quality evaluation and learning
- Structural diversity
- Parameter optimization

**Grade:** F violation if ANY text bypasses this pipeline

**Documentation:** `docs/02-architecture/processing-pipeline.md`

### 0.5. **Generate to Data, Not Enrichers** 🔥 **MANDATORY POLICY (Jan 2, 2026)**
**ALL metadata and content MUST be generated directly to data files during generation phase, NOT added later by enrichers during export.**

**MANDATORY ARCHITECTURE:**
- ✅ **Generate complete data to source YAML** - Write full metadata to Materials.yaml, Contaminants.yaml, etc.
- ✅ **Enrich during write** - Generation pipeline enriches data before saving (e.g., author metadata)
- ✅ **Export reads complete data** - Export/frontmatter generation uses data files as-is
- ❌ **NO enrichers adding missing data** - Enrichers can format/transform, but NOT add essential fields
- ❌ **NO lazy enrichment** - Data must be complete when saved, not completed later

**Why This Matters:**
- Single source of truth: Data files contain complete information
- Export works immediately without complex enrichment pipelines
- Quality evaluation sees complete data (no "None (None)" issues)
- Clear separation: Generation creates data, Export formats/presents data

**Examples:**

✅ **CORRECT - Generate Complete Data**:
```python
# During generation, write FULL author metadata
material_data['author'] = {
    'id': 2,
    'name': 'Alessandro Moretti',
    'country': 'Italy',
    'title': 'Ph.D.',
    'expertise': [...]
}
save_to_materials_yaml(material_data)

# Export just reads and formats
author = material_data['author']  # Already complete
frontmatter['author'] = author    # No enrichment needed
```

❌ **WRONG - Lazy Enrichment**:
```python
# Generation writes minimal data
material_data['author'] = {'id': 2}  # Incomplete!
save_to_materials_yaml(material_data)

# Export has to enrich (BAD - violates policy)
author_id = material_data['author']['id']
full_author = lookup_in_registry(author_id)  # Should have been done during generation
frontmatter['author'] = full_author
```

**Implementation Locations:**
- `generation/core/adapters/domain_adapter.py` - Enriches data during write
- `generation/core/evaluated_generator.py` - Generates complete content
- All data must be complete BEFORE export phase

**Grade:** F violation if enrichers add essential metadata that should have been generated

**Related:** Author Attribution Refactor (Dec 30, 2025) - Implements this policy for author metadata

### 1. **No Mocks or Fallbacks in Production Code** 🔥 **MANDATORY FIRM POLICY (Dec 11, 2025)**
System must fail immediately if dependencies are missing. **ZERO TOLERANCE** for:
- MockAPIClient or mock responses in production
- Default values that bypass validation (`or "default"`, `.get('key', 'default')`)
- Skip logic that bypasses checks (`if not exists: return True`)
- Placeholder return values (`return {}`)
- Silent failures (`except: pass`)
- **Category fallback ranges** (`if prop missing: use category_range`)
- **Template fallbacks** (`if data missing: use template`)
- **Any defaults in generators** - Generators MUST fail if data/config missing

**FIRM POLICY applies to:**
- ✅ **ALL generators** - Must fail fast if data/config/dependencies missing
- ✅ **ALL data loaders** - Must fail if files missing (no empty returns)
- ✅ **ALL configuration** - Must fail if required keys missing (no defaults)
- ✅ **ALL API clients** - Must fail if credentials missing (no mock mode)
- ✅ **ALL validators** - Must fail if validation impossible (no skip logic)

**✅ EXCEPTION**: Mocks and fallbacks **ARE ALLOWED in test code** for proper testing infrastructure.

**🔍 TESTING REQUIREMENT**: Part of testing should include verifying ZERO presence of mocks and fallbacks in production code.

**Grade:** F violation for ANY default/fallback in production code, especially generators.

### 2. **No Hardcoded Values in Production Code** 🔥 **NEW POLICY**
All configuration values MUST come from config files or dynamic calculation. **ZERO TOLERANCE** for:
- **Hardcoded API penalties** (`frequency_penalty=0.0`, `presence_penalty=0.5`)
- **Hardcoded thresholds** (`if score > 30:`, `threshold = 0.7`)
- **Hardcoded temperatures** (`temperature = 0.8`)
- **Hardcoded defaults** (`.get('key', 0.0)`, `or {}` in production paths)
- **Magic numbers** (`attempts = 5`, `max_length = 100`)

**✅ CORRECT APPROACH**:
- Use `config.get_temperature()` not `temperature = 0.8`
- Use `dynamic_config.calculate_penalties()` not `frequency_penalty = 0.0`
- Use `config.get_threshold()` not `if score > 30:`
- Fail fast if config missing, don't use defaults

**🔍 ENFORCEMENT**: Integrity checker automatically detects hardcoded values in production code.

### 3. **Explicit Dependencies**
All required components must be explicitly provided - no silent degradation.

### 3. **Data Storage Policy** 🔥 **CRITICAL**
**ALL generation and validation happens on Materials.yaml ONLY.**

- ✅ **Materials.yaml** - Single source of truth + all generation/validation happens here
  - ALL AI text generation (micros, descriptions, etc.)
  - ALL property research and discovery
  - ALL completeness validation
  - ALL quality scoring and thresholds
  - ALL schema validation
- ✅ **Frontmatter files** - Receive immediate partial field updates (dual-write)
  - Automatic sync when Materials.yaml updated
  - Only changed field written (others preserved)
  - Never read for data persistence
- ✅ **Categories.yaml** - Single source of truth for category ranges
- ❌ **Frontmatter files** - Never read for data persistence (write-only mirror)
  - Simple field-level sync from Materials.yaml
  - Should take milliseconds per update
  - No complex operations during sync
- ✅ **Data Flow**: Generate → Materials.yaml (full write) + Frontmatter (field sync)
- ✅ **Persistence**: All AI research saves to Materials.yaml immediately
- ✅ **Dual-Write**: Every Materials.yaml update triggers frontmatter field sync

### 🚨 **MANDATORY: Field Isolation During Generation** 🔥 **NEW (Nov 22, 2025)**
**Component generation flags (--description, --micro, etc.) MUST ONLY update the specified field.**

- ✅ `--description` → Updates ONLY description field (preserves micro, faq, author, etc.)
- ✅ `--micro` → Updates ONLY caption field (preserves description, faq, etc.)
- ✅ `--faq` → Updates ONLY faq field (preserves description, micro, etc.)
- ❌ **VIOLATION**: Overwriting ANY unrelated field during component generation

**Enforcement**: 15 automated tests verify field isolation (`tests/test_frontmatter_partial_field_sync.py`)

See `docs/data/DATA_STORAGE_POLICY.md` for complete policy.

### 3.5. **Dual-Write Policy** 🔥 **MANDATORY (Dec 12, 2025) - CRITICAL**
**EVERY save to data YAML files MUST immediately trigger a save to frontmatter.**

**STRICT REQUIREMENTS**:
1. ✅ **ALWAYS dual-write** - Save to data/*.yaml AND frontmatter/*.yaml in same operation
2. ✅ **IMMEDIATE sync** - Frontmatter update happens immediately after data save
3. ✅ **NEVER data-only** - No operation should save ONLY to data files without frontmatter
4. ✅ **Field-level sync** - Only modified fields written to frontmatter (preserves other fields)
5. ✅ **Same transaction** - Both saves should succeed or fail together

**Implementation Pattern**:
```python
# ✅ CORRECT - Dual-write pattern
def save_content(material_name, field, value):
    # 1. Save to data source
    save_to_materials_yaml(material_name, field, value)
    
    # 2. IMMEDIATELY sync to frontmatter (same operation)
    sync_field_to_frontmatter(material_name, field, domain='materials')
    
# ❌ WRONG - Data-only save
def save_content(material_name, field, value):
    save_to_materials_yaml(material_name, field, value)
    # Missing frontmatter sync!
```

**Why This Matters**:
- Frontmatter files are displayed on website - users see stale content if not synced
- Data consistency across system - no divergence between sources
- Immediate visibility - generated content appears in frontmatter instantly
- Field isolation - partial updates preserve unmodified fields

**Enforcement**: 
- Code review requirement - all data save operations must include frontmatter sync
- Test requirement - verify frontmatter updated after data operations
- Grade F violation if data saved without frontmatter sync

See `docs/data/DATA_STORAGE_POLICY.md` for complete dual-write implementation details.

### 4. **Contaminant Appearance Data Policy** 🔥 **UPDATED (Dec 1, 2025)**
**All contaminant visual appearance data MUST be pre-populated in `Contaminants.yaml`.**

**🚨 MANDATORY: Contaminants.yaml is the ONLY Source of Truth for Image Generation**

**STRICT REQUIREMENTS**:
1. ✅ **ALL contamination patterns MUST come from Contaminants.yaml** - NO fallbacks, NO defaults
2. ✅ **Material matching MUST use intelligent lookup** - "Titanium Alloy (Ti-6Al-4V)" matches "Titanium"
3. ✅ **EVERY pattern used MUST have valid_materials entry** - No arbitrary pattern selection
4. ✅ **Pattern selection MUST be logged** - Show exactly which patterns were selected and why
5. ❌ **NO category-only fallbacks** - If a material has no patterns in valid_materials, FAIL

**🚨 MANDATORY SELECTION POLICIES** (Dec 1, 2025) 🔥 **NEW**:
1. ✅ **ALWAYS select 3-5 contaminants** - Default is 4, enforced range 3-5
2. ✅ **Context is NOT a factor in selection** - Ignore indoor/outdoor/industrial/marine
3. ✅ **Select most common contaminants for that material** - Based on:
   - Patterns with rich appearance data (highest priority)
   - Patterns explicitly listing this material (not just ALL)
   - Commonality score (how frequently this contamination appears on this material)

**Selection Priority** (Dec 1, 2025):
```
1. Rich appearance data (Format B with 16 fields): +200 points
2. Simple appearance data (Format A): +100 points  
3. Material explicitly listed (not ALL): +50 points
4. Commonality score from Contaminants.yaml: +score points
5. Priority weight multiplier: score × weight
```

**INTELLIGENT MATERIAL MATCHING** (Fixed Dec 1, 2025):
- ✅ Exact match: "Titanium" matches "Titanium"
- ✅ Base material in name: "Titanium" matches "Titanium Alloy (Ti-6Al-4V)"
- ✅ Alloy variants: "Steel" matches "Stainless Steel 316"
- ❌ WRONG: Only exact string matching (breaks alloy materials)

**SIMPLIFIED ARCHITECTURE**:
- ✅ **Single class: `ContaminationPatternSelector`** - ONLY source for contamination data
- ✅ **ZERO API calls** - Reads from Contaminants.yaml only (no Gemini calls for contamination)
- ✅ **Pattern selection by valid_materials field** - Deterministic, reproducible
- ✅ **Priority scoring** - Prefers patterns with rich appearance data
- ❌ **Deprecated**: CategoryContaminationResearcher, MaterialContaminationResearcher, ContaminantAppearanceLoader

**VERIFICATION REQUIREMENT**:
When generating images, the terminal MUST show:
```
📋 Selected 4 patterns for [Material]: ['pattern-1', 'pattern-2', 'pattern-3', 'pattern-4']
📊 [Material] ([context]): 4 patterns selected, 4 with rich data, N aging patterns
```

Note: Pattern count should always be 3-5 (default: 4). Context is logged but NOT used for selection.

If you see "using metal fallback" or "No direct contamination patterns", the system is NOT working correctly.

**🚨 MANDATORY TERMINAL OUTPUT POLICY** (Dec 1, 2025):
During EVERY image generation, the terminal MUST display a detailed contamination report:
```
======================================================================
🧪 CONTAMINATION PATTERNS FOR: [Material Name]
======================================================================
   Context: [industrial/outdoor/indoor/marine]
   Patterns requested: [N]
   Patterns selected: [N]
   Rich appearance data: [N]/[N]

   📋 SELECTED CONTAMINATION PATTERNS:

   1. [Pattern Name] ([pattern-id])
      ✅ Rich data | Category: [contamination/aging]
      Colors: [color list]
      Texture: [texture description]...
      Realism: [realism notes if available]...

   2. [Pattern Name] ([pattern-id])
      ...
======================================================================
```
This output is MANDATORY to verify that contaminants are being properly evaluated from Contaminants.yaml.

**CONTAMINANT WEIGHTING** (Dec 1, 2025):
Contaminant weighting can be applied at two levels:
1. **Context-level** (in `context_settings` of Contaminants.yaml):
   - `aging_weight`: Boost/reduce aging patterns (e.g., 1.5 for outdoor)
   - `contamination_weight`: Boost/reduce contamination patterns
2. **Per-pattern level** (future enhancement):
   - Add `priority_weight` field to individual patterns in Contaminants.yaml
   - Higher weight = more likely to be selected

**Only Remaining API Call**: Shape research (optional) - What object form is most common

```python
# Single source of truth
from domains.materials.image.research.contamination_pattern_selector import (
    ContaminationPatternSelector
)
selector = ContaminationPatternSelector()
result = selector.get_patterns_for_image_gen("Aluminum", num_patterns=3)
# result['api_calls_made'] == 0  # ALWAYS zero for contamination
```

**Coverage Status** (Nov 29, 2025):
- 100 contamination patterns
- 159 materials
- 15,900 expected combinations
- ~4% currently populated (652/15,900)

**Populate Missing Data**:
```bash
python3 scripts/research/batch_visual_appearance_research.py --all
```

See `docs/05-data/CONTAMINANT_APPEARANCE_POLICY.md` for complete policy.
**Enforcement**: 16 automated tests in `tests/domains/materials/image/test_contamination_pattern_selector.py`

### 5. **Component Architecture**
Use ComponentGeneratorFactory pattern for all generators.

### 6. **Fail-Fast Design with Quality Gates**
- ✅ **What it IS**: Validate inputs, configurations, and dependencies immediately at startup
- ✅ **What it IS**: Throw specific exceptions (ConfigurationError, GenerationError) with clear messages
- ✅ **What it IS**: Enforce quality gates (Winston 69%+, Realism 7.0+, Readability pass)
- ❌ **What it's NOT**: Removing runtime error recovery like API retries for transient issues

**Quality Gates (ALL must pass)**:
1. Winston AI Detection: 69%+ human score (configurable via humanness_intensity, currently at level 7)
2. Readability Check: Pass status
3. Subjective Language: No violations
4. **Realism Score: 7.0/10 minimum** ← NEW (Nov 18, 2025)
5. Combined Quality Target: Meets learning target

### 7. **Content Instruction Policy** 🔥 **CRITICAL**
**Content instructions MUST ONLY exist in prompts/*.txt files.**

- ✅ **prompts/*.txt files** - Single source of truth for ALL content instructions
  - Focus areas (what to emphasize)
  - Format rules (structural requirements)
  - Style guidance (voice and tone)
  - Component-specific content strategy
- ❌ **processing/*.py files** - ONLY technical mechanisms (NO content instructions)
  - Word count calculations
  - Voice parameter application
  - API integration
  - Quality validation
- 🚫 **FORBIDDEN in ComponentSpec**: `format_rules`, `focus_areas`, `style_notes` fields
- 🚫 **FORBIDDEN in SPEC_DEFINITIONS**: Content instruction keys
- ✅ **ALLOWED in ComponentSpec**: `name`, `lengths`, `end_punctuation`, `prompt_template_file`
- ✅ **ENFORCEMENT**: 5 automated tests verify policy compliance (see `tests/test_content_instruction_policy.py`)

See `docs/prompts/CONTENT_INSTRUCTION_POLICY.md` for complete policy.

### 8. **Component Discovery Policy** 🔥 **NEW (Nov 16, 2025)**
**Component types MUST ONLY be defined in prompts/*.txt and config.yaml.**

- ✅ **prompts/*.txt files** - Define component types by filename
  - Create `prompts/micro.txt` to define 'micro' component
  - Create `prompts/description.txt` to define 'description' component
  - Each .txt file = one component type
- ✅ **config.yaml** - Define component word counts
  ```yaml
  component_lengths:
    micro: 25
    description: 15
  ```
- ❌ **processing/*.py files** - NO hardcoded component types
  - ❌ `if component_type == 'micro':`
  - ❌ `SPEC_DEFINITIONS = {'micro': {...}}`
  - ❌ Hardcoded component lists
- ✅ **Dynamic Discovery**: Components discovered at runtime from prompts/
- ✅ **Generic Code**: Use `component_type` parameter, iterate `ComponentRegistry.list_types()`
- ✅ **ENFORCEMENT**: Automated tests verify zero hardcoded components

See `docs/architecture/COMPONENT_DISCOVERY.md` for complete policy.

### 9. **Template-Only Policy** 🔥 **NEW (Nov 18, 2025) - CRITICAL**
**ONLY prompt templates determine content and formatting. NO component-specific methods.**

- ✅ **domains/*/prompts/*.txt** - ALL content instructions and formatting rules
  - Structure guidelines, style requirements, forbidden phrases
  - Format specifications, example outputs, voice/tone rules
  - COMPLETE content strategy for each component type
- ❌ **processing/*.py** - ZERO component-specific code
  - ❌ NO `if component_type == 'micro':` checks
  - ❌ NO component-specific methods (`_build_caption_prompt()`, `_extract_micro()`)
  - ❌ NO hardcoded content instructions in code
  - ❌ NO component-specific extraction logic in generators
- ✅ **Strategy Pattern**: Use `extraction_strategy` in config.yaml
  ```yaml
  component_lengths:
    micro:
      default: 50
      extraction_strategy: before_after  # Strategy-based extraction
    description:
      default: 30
      extraction_strategy: raw  # Return text as-is
  ```
- ✅ **Generic Methods**: Use strategy dispatch, not component checks
  - ✅ `adapter.extract_content(text, component_type)` - delegates to strategy
  - ✅ `_load_prompt_template(component_type)` - loads generic template
  - ❌ `_extract_micro(text)` - component-specific method
- ✅ **Full Reusability**: /processing works for ANY domain (materials, contaminants, regions)
- ✅ **Zero Code Changes**: Add new component = create template + config entry only

**Adding New Component**:
```bash
# OLD WAY (NON-COMPLIANT): 4 code files + 1 template
1. ❌ Edit generator.py - add elif component_type == 'new_component'
2. ❌ Edit adapter.py - add _extract_new_component() method
3. ❌ Edit prompt_builder.py - add _build_new_component_prompt()
4. ❌ Add content instructions to code

# NEW WAY (COMPLIANT): 1 config + 1 template = ZERO CODE CHANGES
1. ✅ Create domains/{domain}/prompts/new_component.txt (all instructions)
2. ✅ Add to config.yaml: component_lengths: { new_component: {default: 100, extraction_strategy: raw} }
```

See `docs/08-development/TEMPLATE_ONLY_POLICY.md` for complete policy.

### 10. **Prompt Purity Policy** 🔥 **NEW (Nov 18, 2025)**
**ALL content generation instructions MUST exist ONLY in prompt template files.**

- ✅ **prompts/*.txt files** - Single source of truth for ALL prompts
  - System prompts, content rules, style guidance
  - Voice/tone instructions, format requirements
  - Forbidden phrases, required elements
- ❌ **processing/*.py files** - ZERO prompt text permitted (NO EXCEPTIONS)
  - ❌ `system_prompt = "You are a professional technical writer..."`
  - ❌ `prompt += "\nCRITICAL RULE: Write ONLY..."`
  - ❌ `prompt.replace("text", "YOU MUST NOT...")`
  - ❌ Inline content instructions of any kind
- ✅ **Generator code** - Load prompts from templates ONLY
  - ✅ `prompt = self._load_prompt_template('micro.txt')`
  - ✅ Technical parameters (temperature, penalties) in code
  - ✅ Data insertion (material names, properties) allowed
- ✅ **ENFORCEMENT**: Automated tests verify zero hardcoded prompts

See `docs/08-development/PROMPT_PURITY_POLICY.md` for complete policy.

### 11. **Author Assignment Immutability Policy** 🔥 **NEW (Dec 6, 2025) - CRITICAL**
**Once an author is assigned to content, it NEVER changes.**

**ARCHITECTURE RULES**:
1. ✅ **Author assignment happens ONCE** - When content is first created for a material/item
2. ✅ **Assignment is PERMANENT** - Author never changes for that material/item thereafter
3. ✅ **Voice consistency** - All content for that material uses same author's voice
4. ❌ **NO re-randomization** - Never pick a new author on regeneration
5. ❌ **NO voice randomization per generation** - Voice determined by author, not per-call

**Implementation**:
- Author stored in Materials.yaml, Settings.yaml, etc. under `author.id` field
- Generator reads existing author ID from data file
- If no author assigned (new material), randomly assign once, then persist
- Persona loaded from `shared/voice/profiles/{author}.yaml` defines ALL voice behavior
- Humanness optimizer provides structural variation (rhythm, opening) NOT voice

**Separation of Concerns**:
- **Author Personas** (`shared/voice/profiles/*.yaml`) - Define ALL voice characteristics (ONLY source)
- **Humanness Optimizer** (`learning/humanness_optimizer.py`) - Structural variation ONLY (rhythm, opening, diversity) NOT voice
- **Domain Prompts** (`domains/*/prompts/*.txt`) - Content requirements + `{voice_instruction}` placeholder
- **Prompt Assembly**: Domain prompt → inject voice from persona → add humanness (structure) → send to LLM

**Grade**: F violation if voice/author changes on regeneration

### 12. **Generation Report Policy** 🔥 **NEW (Nov 18, 2025)**
**ALWAYS display complete generation report after EVERY content generation.**

**Required Report Sections**:
1. **📝 Generated Content** - Full text with clear formatting
2. **📈 Quality Metrics** - AI scores, validation results, pass/fail status
3. **📏 Statistics** - Character counts, word counts, length analysis
4. **💾 Storage** - Exact location, component type, material name

**Format Example**:
```
================================================================================
📊 GENERATION COMPLETE REPORT
================================================================================

📝 GENERATED CONTENT:
────────────────────────────────────────────────────────────────────────────────
[Full generated text here]
────────────────────────────────────────────────────────────────────────────────

📈 QUALITY METRICS:
   • AI Detection Score: 0.245 (threshold: 0.303)
   • Status: ✅ PASS
   • Attempts: 1

📏 STATISTICS:
   • Length: 287 characters
   • Word count: 45 words

💾 STORAGE:
   • Location: data/materials/Materials.yaml
   • Component: caption
   • Material: Aluminum

================================================================================
```

**Purpose**: Provides complete transparency and verification of generation results.
**Implementation**: `shared/commands/generation.py` - all generation handlers
**Compliance**: Mandatory for micro, description, FAQ generation

### 13. **Voice Instruction Centralization Policy** 🔥 **NEW (Dec 6, 2025) - CRITICAL**
**ALL voice, tone, and style instructions MUST exist ONLY in persona files.**

**Single Source of Truth**: `shared/voice/profiles/*.yaml`

**Zero Tolerance** for voice instructions in:
- ❌ Domain prompt templates (`domains/*/prompts/*.txt`)
- ❌ Generation code (`generation/**/*.py`)
- ❌ Configuration files (any config.yaml)
- ❌ Shared templates outside personas/

**Critical Problem Solved**: Domain prompts contained contradictory voice instructions ("conversational" vs "NO conversational tone"), causing LLM to ignore both and produce forbidden phrases in ALL outputs.

**Compliance**:
- ✅ Domain prompts: ONLY `{voice_instruction}` placeholder
- ✅ Persona files: ALL voice guidance (tone, style, forbidden phrases)
- ✅ Generation code: Load persona and render, NO voice logic
- ✅ Enforcement: Automated tests in `tests/test_voice_centralization_policy.py`

**Migration Complete**: Removed voice instructions from 3 domain prompt files (Dec 6, 2025)

See `docs/08-development/VOICE_INSTRUCTION_CENTRALIZATION_POLICY.md` for complete policy.

### 14. **Voice Pattern Compliance Policy** 🔥 **NEW (Dec 13, 2025) - CRITICAL**
**Generated content MUST use author-specific linguistic patterns from persona files.**

**Problem**: Generic technical writing that ignores author voice instructions, producing identical content across all authors.

**Solution**: Automated pattern compliance validation in quality analysis.

**Pattern Requirements by Nationality**:

**United States (Todd Dunning)**:
- ✅ Phrasal verbs: "line up", "dial in", "ramp up", "cut down", "work out"
- ✅ Quantified outcomes: "by 20%", "cuts X%", "improves Y%"  
- ✅ Practical transitions: "turns out", "in practice", "overall"

**Taiwan (Yi-Chun Lin)**:
- ✅ Topic-comment: "Surface roughness, it measures 0.8 μm"
- ✅ Article omission: "Process yields result" (not "The process")
- ✅ Temporal markers: "After treatment", "Following adjustment"

**Italy (Alessandro Moretti)**:
- ✅ Cleft structures: "This property, it enables..."
- ✅ Subjunctive hedging: "It seems that...", "It appears..."
- ✅ Romance cognates: "tenaciously", "manifests", "persists"

**Indonesia (Ikmanda Roswati)** 🔥 **STRENGTHENED (Dec 26, 2025)**:
- ✅ Topic prominence: "This contamination, it forms..." (1-2x per paragraph)
- ✅ Aspectual markers: "already", "still", "just now" (temporal completion)
- ✅ Time-fronting with passive: "After treatment is applied, roughness decreases"
- ✅ Agentless passives with prepositions: "is observed at 20 μm", "from the data"
- ✅ Explicit preposition patterns: "from the measurements", "at the surface", "in observations"
- ✅ Frequency: 2-3 distinctive markers per paragraph (CRITICAL for detection)

**Compliance Validation**:
- 🔍 **Automatic checking**: Quality analyzer validates pattern presence
- 📊 **Scoring**: Requires 2+ pattern types for authenticity (85+ score)
- ⚠️ **Deductions**: -15 points per missing pattern type
- 🎯 **Voice Authenticity Score**: Reflects pattern compliance

**Domain Prompt Changes**:
- ✅ Relaxed from "single sentence" to "1-2 sentences"
- ✅ Added explicit voice reminder: "EXPRESS YOUR AUTHENTIC VOICE"
- ✅ Removed restrictive "technical subtitle" framing

**Implementation**:
- `shared/voice/quality_analyzer.py`: `_check_pattern_compliance()` method
- `domains/materials/prompts/description.txt`: Relaxed prompt with voice emphasis
- Enforcement: Automated tests in `tests/test_voice_pattern_compliance.py` (11 tests, all passing)

**Results**:
- Voice Authenticity: None/100 → **85/100** (+85 points)
- Phrasal verbs now appearing in US content
- More natural sentence structures (2 sentences vs 1 rigid)
- Pattern detection operational across all 4 nationalities

See `VOICE_COMPLIANCE_IMPLEMENTATION_DEC13_2025.md` for implementation details.

### 15. **Postprocessing Retry-Until-Requirements-Met Policy** 🔥 **NEW (Dec 14, 2025) - MANDATORY**
**Postprocessing system MUST retry regeneration until quality requirements are met.**

**Problem Solved**: Previous implementation tried once, saw no improvement, gave up. Content stayed low-quality despite multiple attempts being available.

**MANDATORY Requirements**:
1. ✅ **Maximum attempts**: `MAX_REGENERATION_ATTEMPTS = 5`
2. ✅ **Retry loop**: Keep trying until requirements met OR max attempts exhausted
3. ✅ **Best version tracking**: Return highest quality version, not last attempt
4. ✅ **Attempt reporting**: Result includes `attempts` field
5. ✅ **Stop conditions**: Requirements met (readability pass + 0 AI patterns + score ≥ 60) OR max attempts

**Quality Requirements (all must pass)**:
- Readability: `status == 'pass'`
- AI Patterns: `len(patterns) == 0`
- Quality Score: `score >= 60/100`

**Implementation**:
```python
# CORRECT: Retry until requirements met
best_quality_score = 0
best_content = None

for attempt in range(1, MAX_REGENERATION_ATTEMPTS + 1):
    result = generator.generate(item_name, component_type)
    quality_score = evaluate_quality(result.content)
    
    if quality_score > best_quality_score:
        best_quality_score = quality_score
        best_content = result.content
    
    if meets_all_requirements(result.content, quality_score):
        print(f"✅ REQUIREMENTS MET on attempt {attempt}!")
        break

return {
    'attempts': attempt,
    'best_quality_score': best_quality_score,
    'improved': True
}
```

**Anti-Pattern (Grade F violation)**:
```python
# ❌ WRONG: Single attempt then give up
result = generator.generate(...)
if result.quality < threshold:
    return keep_original()  # NO RETRY!
```

**Enforcement**:
- Automated tests: `tests/test_postprocessing_retry_policy.py` (4 tests)
- Module docstring: Must mention "MANDATORY RETRY POLICY"
- Result dict: Must include `attempts` and `best_quality_score` fields

**Grade**: Mandatory compliance - violations = Grade F

See `docs/08-development/POSTPROCESSING_RETRY_POLICY.md` for complete policy.

### 16. **Prompt Chaining & Orchestration Policy** 🔥 **NEW (Nov 27, 2025) - CRITICAL**
**Maximum use of prompt chaining and orchestration to preserve separation of concerns and specificity.**

**Core Principle**: Break generation into specialized prompts instead of one monolithic prompt.

**Architecture Pattern**:
```
Stage 1: Research → Extract properties (low temp 0.3)
Stage 2: Visual Description → Generate appearance (high temp 0.7)
Stage 3: Composition → Layout before/after (balanced 0.5)
Stage 4: Refinement → Technical accuracy (precise 0.4)
Stage 5: Assembly → Final polish (balanced 0.5)
```

**Benefits**:
- ✅ **Separation of concerns** - Research vs creativity vs accuracy
- ✅ **Optimal parameters per stage** - Different temps for different tasks
- ✅ **Reusable components** - Same research for multiple outputs
- ✅ **Easy debugging** - Test each stage independently
- ✅ **Better quality** - Focused prompts produce better results

**Requirements**:
- ✅ **Orchestrator layer** - Chains prompts with context passing
- ✅ **Specialized templates** - One template per stage/task
- ✅ **Context passing** - Each stage receives previous output as input
- ✅ **Independent testability** - Can test each stage separately

**Examples**:
- ✅ **Text Generation**: `generation/core/evaluated_generator.py` (single-pass with learning)
  - Stage 1: Build base prompt from template
  - Stage 2: Add humanness layer (randomized voice, structure)
  - Stage 3: Generate content (single API call)
  - Stage 4: Save immediately to Materials.yaml
  - Stage 5: Evaluate quality for learning (Winston, Realism, Structural)
  - Stage 6: Log to learning database

- ✅ **Image Generation**: `shared/image/orchestrator.py` (new implementation)
  - Stage 1: Research material properties
  - Stage 2: Generate visual description
  - Stage 3: Compose hero layout
  - Stage 4: Technical refinement
  - Stage 5: Final assembly

**Anti-Patterns**:
- ❌ **Monolithic prompts** - One massive prompt trying to do everything
- ❌ **No context passing** - Independent prompts duplicating work
- ❌ **Single temperature** - Using same temp for research AND creativity
- ❌ **Hardcoded prompts** - Prompt text in code instead of templates

**Enforcement**:
- Code review checklist (see policy document)
- Grade penalties for violations (-30 points for monolithic prompts)
- Mandatory for ALL generation systems (text, image, future domains)

See `docs/08-development/PROMPT_CHAINING_POLICY.md` for complete policy with examples.

### 16.5. **Word Count Control Policy** 🔥 **NEW (Dec 24, 2025) - MANDATORY**
**Word counts MUST NOT be restricted using token limits (max_tokens parameter).**

**The Problem**: Using `max_tokens` to enforce word count limits causes mid-sentence truncation, creating broken/incomplete content.

**PROHIBITED Approach** (Grade F):
```python
# ❌ WRONG: Using max_tokens to control word count
response = api.generate(
    prompt=prompt,
    max_tokens=150  # This causes truncation!
)
# Result: "The laser cleaning process requires careful attention to surface" [CUT OFF]
```

**REQUIRED Approach**:
```python
# ✅ CORRECT: Use prompt instructions only, accept approximate word counts
prompt = """
Write a description about {material}.
WORD LENGTH: 50-150 words
"""
response = api.generate(prompt=prompt)  # No max_tokens restriction
# Result: Content may be 160-180 words (20% over), but COMPLETE sentences
```

**Architectural Reality**:
- LLMs generate token-by-token and don't count words during generation
- Prompt instructions provide approximate guidance (typically 20-30% variance)
- This variance is acceptable and inherent to LLM architecture
- Post-generation truncation also causes broken sentences (DO NOT USE)

**Acceptable Solutions**:
1. ✅ **Accept approximate word counts** - Prompts guide to roughly correct length
2. ✅ **Use wide ranges** - 1x-3x ranges accommodate natural variance
3. ✅ **Quality-gated mode** - Multiple attempts, select best length match
4. ❌ **max_tokens limits** - FORBIDDEN (causes truncation)
5. ❌ **Post-generation truncation** - FORBIDDEN (also causes truncation)

**Requirements**:
- All prompts MUST use 1x-3x word count ranges minimum
- NO max_tokens restrictions in ANY generation code
- Accept that LLMs produce approximate word counts
- Post-processing can REGENERATE (not truncate) if too long

**Grade**: F violation if using max_tokens or truncation to control word count

### 17. **Material Name Consistency Across Domains Policy** 🔥 **NEW (Dec 20, 2025) - CRITICAL**
**ALL domains MUST use consistent material naming conventions based on their role.**

**Single Source of Truth**: Materials.yaml defines ALL material identities.

**Domain-Specific Formats** (MANDATORY):

| Domain | Format | Example | Use Case |
|--------|--------|---------|----------|
| **Materials.yaml** | `{slug}-laser-cleaning` | `aluminum-laser-cleaning` | Dictionary keys (source of truth) |
| **Settings.yaml** | `{slug}` (base only) | `aluminum` | Dictionary keys (matches material) |
| **Contaminants.yaml** | `Display Name` | `Aluminum` | valid_materials lists (human-readable) |
| **DomainAssociations.yaml** | `{slug}` (base only) | `aluminum` | Lookup keys (for associations) |

**Format Conversion Rules**:
```python
# Materials.yaml → Settings.yaml
'aluminum-laser-cleaning' → 'aluminum'  # Remove suffix

# Materials.yaml → Contaminants.yaml
'aluminum-laser-cleaning' → 'Aluminum'  # Display name
'stainless-steel-316-laser-cleaning' → 'Stainless Steel 316'

# Contaminants.yaml → Lookups
'Aluminum' → 'aluminum'  # Lowercase, slugify
'Stainless Steel 316' → 'stainless-steel-316'
```

**MANDATORY Implementation**:
```python
# ✅ CORRECT: Use appropriate format for domain
from shared.utils.core.slug_utils import create_material_slug

# For Materials.yaml operations
material_key = f"{base_slug}-laser-cleaning"

# For Settings.yaml operations  
setting_key = base_slug  # No suffix

# For Contaminants.yaml operations
display_name = ' '.join(word.capitalize() for word in base_slug.split('-'))

# ❌ WRONG: Mixing formats
materials_data['materials']['Aluminum']  # Display name in Materials.yaml
contaminants_data['valid_materials'] = ['aluminum-laser-cleaning']  # Slug in Contaminants
```

**Normalization Tool**:
```bash
# Check consistency across all domains
python3 scripts/tools/normalize_all_domains.py --check

# Fix inconsistencies
python3 scripts/tools/normalize_all_domains.py --fix --dry-run
python3 scripts/tools/normalize_all_domains.py --fix
```

**Why This Matters**:
- ✅ **Cross-domain lookups work correctly**
- ✅ **Consistent user experience** (display names match across UI)
- ✅ **No broken associations** (material references resolve)
- ✅ **Frontmatter generation accurate** (correct slugs for URLs)
- ❌ **Mixing formats breaks everything** (lookups fail, associations break)

**Common Mistakes to Avoid**:
```python
# ❌ Using display name in Materials.yaml
materials_data['materials']['Aluminum'] = {...}  # WRONG

# ❌ Using slug in Contaminants.yaml  
pattern_data['valid_materials'] = ['aluminum-laser-cleaning']  # WRONG

# ❌ Using full slug in Settings.yaml
settings_data['settings']['aluminum-laser-cleaning'] = {...}  # WRONG

# ✅ CORRECT formats for each domain
materials_data['materials']['aluminum-laser-cleaning'] = {...}  # Materials
settings_data['settings']['aluminum'] = {...}  # Settings
pattern_data['valid_materials'] = ['Aluminum']  # Contaminants
```

**Enforcement**:
- Automated tests: `tests/test_material_name_consistency.py` (to be created)
- Validation script: `scripts/tools/normalize_all_domains.py`
- Pre-commit hook: Check for format violations

**Grade**: F violation if mixing formats or using wrong convention for domain

See `docs/08-development/MATERIAL_NAME_CONSISTENCY_POLICY.md` for complete policy.



## Code Standards
- Use strict typing with Optional[] for nullable parameters
- Implement comprehensive error handling with specific exception types
- No default values for critical dependencies (API clients, configuration files)
- Log all validation steps and failures clearly
- Keep code concise and avoid unnecessary complexity
- Never leave TODOs - provide complete solutions
- Never hardcode values - use configuration or parameters
- **Simplify naming** - Remove redundant prefixes (Simple, Basic, Universal, Unified)
  - ❌ `SimpleGenerator` → ✅ `Generator`
  - ❌ `UniversalImageGenerator` → ✅ `ImageGenerator`
  - ❌ `simple_validate()` → ✅ `validate()`
  - See `docs/08-development/NAMING_CONVENTIONS_POLICY.md` for complete rules
- **Material naming conventions** - Use domain-appropriate format (MANDATORY)
  - Materials.yaml: `aluminum-laser-cleaning` (slug with suffix)
  - Settings.yaml: `aluminum` (base slug)
  - Contaminants.yaml: `Aluminum` (display name)
  - See Core Principle 17 for complete requirements
- **NEVER add content instructions to code** - they belong ONLY in prompts/*.txt
- **NEVER hardcode component types** - they're discovered from prompts/*.txt
- **ALWAYS check documentation before implementing** - see Documentation Compliance Checklist

## Architecture Patterns
- **Wrapper Pattern**: Use lightweight wrappers to integrate specialized generators
- **Factory Pattern**: ComponentGeneratorFactory for component discovery and creation
- **Result Objects**: Return structured ComponentResult objects with success/error states
- **Configuration Validation**: Validate all required files and settings on startup
- **Linguistic Patterns**: Keep ONLY in `prompts/personas/` - never duplicate elsewhere
- **Dynamic Calculation**: Use dynamic_config for all thresholds, penalties, temperatures
- **Prompt Chaining**: Use orchestrated multi-stage prompts for separation of concerns (see PROMPT_CHAINING_POLICY.md) 🔥 **NEW**

## Error Handling
- **ConfigurationError**: Missing or invalid configuration files
- **GenerationError**: Content generation failures
- **RetryableError**: Temporary failures that could be retried (but avoid retries)
- **Never silently fail** or use default values
- **Fail immediately** with specific exception types and clear messages

## Testing Approach
- **No mock APIs in production code** - ZERO TOLERANCE
- **✅ Mocks allowed in test code** for proper testing infrastructure
- **🔍 Verify zero mocks in production** as part of test suite
- **Fail fast on missing test dependencies**
- **Use real API clients** with proper error handling
- **Validate all component integrations**
- **Ensure solid retention of API keys**

---

## 📖 Documentation Compliance Checklist

**MANDATORY BEFORE implementing ANY feature/fix:**

### Step 1: Search Documentation
```bash
# Search for existing guidance
grep -r "feature_name|threshold|validation" docs/**/*.md
```

### Step 2: Read Applicable Policy Documents
- [ ] **HARDCODED_VALUE_POLICY.md** - Before adding ANY values/thresholds/temperatures
- [ ] **CONTENT_INSTRUCTION_POLICY.md** - Before touching prompts/ or content logic
- [ ] **COMPONENT_DISCOVERY.md** - Before adding/modifying components
- [ ] **DATA_STORAGE_POLICY.md** - Before data operations
- [ ] **system-requirements.md** - For quality thresholds and acceptance criteria
- [ ] **processing-pipeline.md** - For generation flow and validation steps

### Step 3: Check Component-Specific Documentation
- [ ] `docs/03-components/` for component-specific docs
- [ ] `[feature]/README.md` for feature-specific guidance

### Step 4: Verify Approach Matches Architecture
- [ ] Does implementation follow documented patterns?
- [ ] Are values dynamically calculated (not hardcoded)?
- [ ] Does it integrate with existing systems correctly?
- [ ] Is it consistent with system architecture?

### Step 5: Ask If Unclear
- [ ] If documentation is missing, contradictory, or unclear: **ASK USER**
- [ ] Don't assume or guess - get clarification first
- [ ] Example: "I don't see guidance on X. Should I implement Y approach or Z?"

### Step 6: Verify Before Claiming Violations 🔥 **CRITICAL (Nov 20, 2025)**

**MANDATORY verification BEFORE reporting ANY violation:**

#### 📋 Verification Checklist:
- [ ] **Grep the config** - `grep -r "key_name" config.yaml generation/config.yaml`
- [ ] **Check all config locations** - Don't assume single config file
- [ ] **Read the actual code** - Not just grep results
- [ ] **Understand the context** - Is this production or test code?
- [ ] **Verify the pattern** - Is `.get('key', default)` actually wrong here?

#### 🚨 Common False Positives:

**FALSE POSITIVE #1: Optional config with sensible default**
```python
# ❌ WRONG: Reported as violation
max_retries = config.get('max_retries', 3)  # 3 is reasonable default

# ✅ RIGHT: Verify if 'max_retries' is in config
# If NOT in config AND this is optional → NOT a violation
# If NOT in config AND this is required → IS a violation
```

**FALSE POSITIVE #2: Test code with mocks**
```python
# ❌ WRONG: Reported as violation
# tests/test_generation.py
mock_response = {"score": 0.95}  # Mock for testing

# ✅ RIGHT: Mocks in test code are ALLOWED
```

**FALSE POSITIVE #3: Calculation constants**
```python
# ❌ WRONG: Reported as violation
penalty = 0.6 + (value - 7) / 3.0 * 0.6  # 0.6 is calculation constant

# ✅ RIGHT: Mathematical constants in formulas are NOT violations
```

#### ✅ Real Violations:

**REAL VIOLATION #1: Production fallback bypassing validation**
```python
# ✅ CORRECT: This IS a violation
winston_score = data.get('winston_score', 0.95)  # Should fail-fast if missing
```

**REAL VIOLATION #2: Skip logic**
```python
# ✅ CORRECT: This IS a violation
if not api_configured:
    return True  # Skipping validation
```

**REAL VIOLATION #3: Hardcoded API parameters**
```python
# ✅ CORRECT: This IS a violation
response = api.generate(temperature=0.8)  # Should use dynamic_config
```

#### 📝 Required Response Format:

When uncertain, use this template:
```
I found X pattern in Y file (line Z):
[code snippet]

grep shows 'key_name' is NOT in config.yaml.

Question: Should 'key_name' be:
A) Added to config.yaml (required config, fail-fast if missing)
B) Keep default (optional config, sensible fallback)
C) Something else

I won't report this as a violation until you clarify.
```

### Red Flags Requiring Doc Check
- ⚠️ Adding **thresholds** → Check for dynamic calculation requirements
- ⚠️ Adding **configuration values** → Check config architecture docs
- ⚠️ Modifying **validation** → Check validation strategy docs
- ⚠️ Adding **new component** → Check component discovery policy
- ⚠️ Changing **data flow** → Check data storage policy
- ⚠️ Adding **hardcoded values** → STOP - check hardcoded value policy

### Documentation Locations Quick Reference
- **Quick answers**: `docs/QUICK_REFERENCE.md`
- **Policies**: `docs/08-development/`
- **Architecture**: `docs/02-architecture/`
- **Component docs**: `docs/03-components/`
- **API guidance**: `docs/07-api/`
- **Data operations**: `docs/05-data/`

### Enforcement
- Integrity checker validates code matches documented architecture
- Pre-commit hooks can check doc compliance
- Manual review catches documentation violations

---

## 🔒 Core Rules (Non-Negotiable)

### Rule 0: 📖 Documentation-First Development (NEW - November 16, 2025)
- **ALWAYS search docs BEFORE coding** - see Documentation Compliance Checklist above
- **NEVER implement without checking guidance** - docs define system architecture
- **ASK if documentation unclear** - don't guess or assume
- **Example violation**: Implementing static thresholds when docs require dynamic calculation

### Rule 1: 🛡️ Preserve Working Code
- **NEVER rewrite or replace** functioning code, classes, or modules
- **ONLY make targeted fixes** - if `fail_fast_generator.py` works, integrate around it
- **Example**: Add missing method ≠ Rewrite entire class

### Rule 2: 🚫 Zero Production Mocks/Fallbacks
**VIOLATION EXAMPLES TO AVOID**:
- `test_results['missing'] = True  # Skip logic`
- `return "default" if not data`
- `except: pass  # Silent failure`
- `or {} # Fallback value`
- `if not found: return True  # Skip validation`

### Rule 3: ⚡ Fail-Fast on Setup + Zero Hardcoded Values + SEARCH FIRST 🔥

- **Validate all inputs and configs upfront** - no degraded operation
- **Throw errors early** with specific exception types
- **Preserve runtime mechanisms** like API retries for transient issues

**🔍 MANDATORY: Search Before Adding ANY Value**

Before adding a hardcoded value, temperature, threshold, or penalty:

1. **Search for DynamicConfig** - `grep -r "DynamicConfig\|dynamic_config" generation/`
2. **Check for existing method** - `grep -r "calculate_temperature\|calculate_penalties" generation/config/`
3. **Look for config file** - `grep -r "temperature\|threshold" generation/config.yaml`
4. **Search for similar patterns** - `grep -r "humanness_intensity\|voice.*intensity" generation/`

**Example Search Pattern**:
```bash
# Before: temperature = 0.8
# Do this FIRST:
grep -r "calculate_temperature" generation/
# Find: generation/config/dynamic_config.py: def calculate_temperature(component_type)
# Result: Use existing method instead of hardcoding
```

**If no existing solution found**:
```
I need to add [value] for [purpose].

I searched:
- grep -r "DynamicConfig" generation/ → [results]
- grep -r "calculate_[thing]" generation/config/ → [results]
- grep -r "[thing]" generation/config.yaml → [results]

No existing solution found. Should I:
A) Add to config.yaml
B) Add to DynamicConfig
C) Use a different approach

Waiting for guidance before proceeding.
```

**🚨 ZERO TOLERANCE for hardcoded values**:
- ❌ `temperature=0.7` → ✅ `dynamic_config.calculate_temperature(component_type)`
- ❌ `frequency_penalty=0.0` → ✅ `params['api_penalties']['frequency_penalty']` (fail if missing)
- ❌ `if score > 30:` → ✅ `config.get_threshold('score_type')`
- ❌ `attempts = 5` → ✅ `config.get('max_attempts')`

**🚨 ANTI-PATTERN: Swapping hardcoded values**
- ❌ Changing `0.7` to `0.8` is NOT fixing the violation
- ❌ Changing `0.7` to `None` is WORSE (introduces bugs)
- ✅ Using dynamic calculation from DynamicConfig IS the fix

**BEFORE adding new code, SEARCH for existing solutions:**
```python
# ❌ WRONG: Assume no solution exists, add hardcoded value
temperature = 0.8  # "temporary" default

# ✅ RIGHT: Search for dynamic_config, find it exists
from generation.config.dynamic_config import DynamicConfig
dynamic_config = DynamicConfig()
temperature = dynamic_config.calculate_temperature(component_type)
```

### Rule 4: 🏗️ Respect Existing Patterns
- **Maintain**: ComponentGeneratorFactory, wrapper classes, ComponentResult objects
- **Preserve**: File structure and directory organization
- **Prefer**: Editing existing files over creating new ones

### Rule 5: 🎯 Surgical Precision
- **Identify exact problem** → **Find smallest change** → **Test only that fix**
- **No scope expansion** - fix X means fix only X
- **Complete solutions** - don't leave parts for user to debug

### Rule 6: 🔍 Content Quality Verification
- **VALIDATE** generated content meets quality standards
- **CHECK frontmatter** structure and required fields
- **ENSURE** proper YAML formatting and schema compliance
- **USE** validation tools to verify content integrity

---

## 📚 Lessons from Past Failures

### 🚨 Critical Failure Patterns to Avoid

| 🔥 Episode | 👤 Request | ❌ Mistake | 💥 Damage | ✅ Correct Approach |
|------------|------------|------------|-----------|-------------------|
| **Factory Destruction** | Add missing method | Rewrote entire class | Lost all generator discovery | Add ONLY the requested method |
| **Generator Replacement** | Fix integration | Ignored existing file | Lost all functionality | Integrate around existing code |
| **Mock Removal** | Remove fallbacks | Deleted without understanding | Broke testing infrastructure | Understand purpose first |
| **Fallback Destruction** | Ensure fail-fast | Removed error recovery | Failed on transient errors | Fail-fast ≠ no retries |
| **Scope Creep** | Fix specific issue | Expanded beyond request | Integration failures | Stick to exact scope |
| **Static Thresholds** | Fix validation | Ignored docs requiring dynamic | Violated architecture policy | Read docs first, found dynamic requirement |

### 🎯 Success Pattern
1. **Search documentation** for existing guidance
2. **Understand** the existing code and design intent
3. **Identify** the minimal change needed
4. **Implement** only that change per documented architecture
5. **Verify** the fix works
6. **Confirm** nothing else broke

---

## ✅ Mandatory Pre-Change Checklist

**Before making ANY modification, complete ALL steps:**

### Step 1: 📖 Read & Understand
- [ ] **Read request precisely** - What is the *exact* issue?
- [ ] **Search documentation** - Check `docs/` for existing guidance
- [ ] **No assumptions** - Ask for clarification if unclear
- [ ] **🔥 Check for metric-documentation mismatches** - Does 10% success rate match "saves all" claims? **NEW**

### Step 2: 🔍 Explore Architecture
- [ ] **Read relevant code** - Understand how it currently works
- [ ] **Search for existing solutions** - Use grep_search to find dynamic config, helpers, utilities
- [ ] **Check subdirectories** - Don't miss important context
- [ ] **Verify file existence** - Prevent "Content Not Found" errors
- [ ] **Read policy docs** - HARDCODED_VALUE_POLICY, CONTENT_INSTRUCTION_POLICY, etc.
- [ ] **Look for similar patterns** - How does the system solve this elsewhere?
- [ ] **🔥 Test actual behavior** - Run live test to verify documentation claims **NEW**

### Step 3: 📜 Check History
- [ ] **Review git commits** - See what was working previously
- [ ] **Use `git show`** - Understand recent changes

### Step 4: 🎯 Plan Minimal Fix
- [ ] **Identify smallest change** - Address only the specific issue
- [ ] **Verify matches documentation** - Implementation follows documented design
- [ ] **Ensure security** - Include validation and error handling
- [ ] **Keep it concise** - Avoid unnecessary complexity

### Step 5: 💬 Communicate Plan
- [ ] **Describe approach** - Explain what you'll change before coding
- [ ] **Be realistic** - No sandbagging or unrealistic timelines
- [ ] **Ask permission** - Before removing code or major changes

### Step 6: 🔧 Implement & Test
- [ ] **Apply the fix** - Make only the planned changes
- [ ] **Read back your changes** - Use read_file to verify what you wrote
- [ ] **Check for new violations** - Did you introduce hardcoded values, TODOs, or fallbacks?
- [ ] **Write verification test FIRST** - Prove the fix works before documenting
- [ ] **Verify it works** - Test the specific issue is resolved
- [ ] **Check for regressions** - Ensure nothing else broke
- [ ] **Run tests** - Confirm test suite still passes
- [ ] **🔍 Verify no production mocks** - Confirm changes don't introduce mocks/fallbacks

### Step 6.5: 📊 Verify Implementation Matches Documentation 🔥 **NEW (Nov 22, 2025)**
**MANDATORY before claiming ANY feature "COMPLETE":**

- [ ] **Write verification test** - Create test that proves implementation works
  ```python
  def test_option_c_saves_all_attempts():
      # Generate with terrible quality
      # Verify ALL attempts saved (not rejected)
      assert save_count == max_attempts  # Proves Option C working
  ```
- [ ] **Run live verification** - Test with real material, check terminal output
- [ ] **Check success metrics** - Does behavior match claims?
  - Option C claimed → Expect 100% completion rate
  - Quality gates claimed → Expect <100% completion rate
  - If mismatch: Documentation is WRONG, not implementation
- [ ] **STOP if verification fails** - Do NOT proceed to documentation
  - ⛔ Success rate ≠ documented behavior → STOP, ASK USER
  - ⛔ Test fails but claim is "COMPLETE" → STOP, FIX CODE
  - ⛔ Live test contradicts claim → STOP, INVESTIGATE
  - ⛔ Multiple docs contradict → STOP, RECONCILE FIRST
- [ ] **Document with evidence** - Include test results, success rate, terminal output
- [ ] **Never claim "COMPLETE" without verification test**

**Example of WRONG approach**:
```markdown
❌ Option C Implementation: COMPLETE
   - Saves all attempts ← NO TEST TO VERIFY THIS
   - 100% completion ← NO MEASUREMENT PROVIDED
   - Documentation done ← BUT CODE STILL BLOCKS SAVES
```

**Example of CORRECT approach**:
```markdown
✅ Option C Implementation: COMPLETE
   - test_saves_all_attempts_regardless_of_quality: PASSING ✅
   - Live test (Copper): All 5 attempts saved ✅
   - Success rate: 100% (10/10 materials) ✅
   - Terminal shows: "💾 Saving attempt X" for ALL attempts ✅
```

### Step 7: 📊 Honest Reporting
- [ ] **Count violations accurately** - Test file updates are not violations
- [ ] **Report what actually changed** - Not what you intended to change
- [ ] **Provide verification evidence** - Test results, success rates, terminal output
- [ ] **Acknowledge limitations** - Be honest about architectural constraints
- [ ] **Don't claim success prematurely** - Verify first, then report
- [ ] **🔥 Check documentation matches reality** - Run live test to confirm claims

### Step 7.5: 🚨 Documentation-Reality Verification 🔥 **NEW (Nov 22, 2025)**
**MANDATORY before updating ANY documentation:**

**Reality Check Protocol**:
1. **Claim**: "Feature X is implemented"
2. **Test**: Write test that proves feature X works
3. **Measure**: Run live test, record actual behavior
4. **Compare**: Does behavior match claim?
   - ✅ YES → Documentation accurate, proceed
   - ❌ NO → Documentation WRONG, fix code OR fix docs
5. **Evidence**: Include metrics that prove reality
   - Success rates, terminal output, test results
   - NOT assumptions or intentions

**Red Flags - Stop and Verify**:
- 🚩 Documentation says "saves all" but success rate is 10%
- 🚩 Documentation says "quality gates removed" but code has gate checks
- 🚩 Documentation says "100% completion" but materials are missing content
- 🚩 Documentation graded A+ but user reports failures
- 🚩 Multiple documents contradict each other

**When Documentation Contradicts Reality**:
```
1. Trust the metrics (success rate, terminal output, tests)
2. Documentation is WRONG (not reality)
3. Either:
   - Fix code to match documentation, OR
   - Fix documentation to match reality
4. Add verification test to prevent regression
5. Never leave contradictory documentation
```

**⚠️ CRITICAL: When Metrics Contradict Documentation - STOP** 🔥 **NEW**:
```
DO NOT PROCEED with analysis or fixes until resolved:

STOP AND ASK USER if:
❌ Success rate doesn't match docs (10% ≠ "saves all")
❌ Test verifies X but docs claim Y
❌ Multiple documents describe different implementations
❌ Live test output contradicts documentation
❌ User reports behavior different from docs

HIERARCHY OF TRUTH (when conflict occurs):
1. Live test results (what actually happens)
2. Success rate metrics (10% vs 100%)
3. Terminal output (what system prints)
4. Test assertions (what tests verify)
5. Documentation (what we THINK happens)

Never try to "explain away" metrics - if 10% success rate, 
then Option C is NOT working regardless of what docs say.
```

### Step 8: Grade Your Work 🔥 **MANDATORY (Nov 20, 2025)**

**Before reporting completion, assign yourself a grade:**

#### 🏆 Grade A (90-100): Excellence
- ✅ All requested changes work (with evidence)
- ✅ Comprehensive tests run and passed
- ✅ Evidence provided (test output, commit hash, file counts)
- ✅ Honest about limitations
- ✅ Zero violations introduced
- ✅ Zero scope creep
- ✅ Verification completed before claiming violations

**Example A Report**:
```
✅ Fixed 3/3 requested violations
📊 Evidence: 24/24 tests passing (see output below)
✅ Commit: abc123def
✅ Verified: grep confirms no config keys missing
⚠️ Note: 2 TODO comments remain (documented as future work)
🏆 Grade: A (95/100)
```

#### 📊 Grade B (80-89): Good
- ✅ Changes work
- ✅ Some evidence provided
- ⚠️ Minor issues remain (acknowledged)
- ⚠️ Partial test coverage

**Example B Report**:
```
✅ Fixed 2/3 violations
📊 Evidence: 22/24 tests passing
⚠️ 2 tests still failing (unrelated to my changes)
🏆 Grade: B (85/100)
```

#### ⚠️ Grade C (70-79): Needs Improvement
- ⚠️ Partial success
- ⚠️ Missing evidence
- ⚠️ Significant issues remain
- ⚠️ Scope expanded beyond request

#### ❌ Grade F (<70): Unacceptable
- ❌ Made things worse
- ❌ No evidence
- ❌ False claims
- ❌ Reported violations without verification
- ❌ Introduced new violations while claiming fixes
- ❌ **Documentation claims contradict metrics** (10% ≠ "saves all")
- ❌ **Documented features without verification tests**
- ❌ **Multiple docs describe different implementations**

**CRITICAL**: Grade F requires immediate rollback and fresh start.

**Documentation Accuracy Penalties**:
- **-20 points**: Documentation claims contradict measured metrics
- **-15 points**: Features documented as "COMPLETE" without verification tests
- **-10 points**: Multiple documents describe conflicting implementations

---

## 🚫 Absolute Prohibitions

### ❌ CODE MODIFICATION PROHIBITIONS
- **Never rewrite or remove working code** without explicit permission
- **Never expand beyond requested scope** - fix X means fix only X
- **Never create new files** to bypass fixing existing ones
- **Never ignore existing patterns** - factories, wrappers, etc.

### ❌ DEVELOPMENT PRACTICE PROHIBITIONS
- **Never assume requirements** - ask for clarification instead
- **Never generate verbose/inefficient code** - keep it concise
- **Never skip validation** - always include error handling
- **Never hardcode values** - use configuration or parameters
- **Never leave TODOs** - provide complete solutions

### ❌ CONTEXT HANDLING PROHIBITIONS
- **Never access non-existent files** - verify existence first
- **Never mishandle context** - prevent "Content Not Found" errors
- **Never ignore specifications** - address race conditions, formatting precisely

---

## 🚨 Damage Warning Signs

Watch for these indicators of problems:
- 🔴 **System stops working** after your changes
- 🔴 **Multiple files altered** for a single fix request
- 🔴 **User mentions damage** or restores from git
- 🔴 **Added complexity** where simple change would work
- 🔴 **Security vulnerabilities** or incomplete code introduced

---

## 🚑 Emergency Recovery Procedures

### If You Break Something:

#### Step 1: 🔍 Assess Damage
```bash
git status  # See what files changed
```

#### Step 2: 🔄 Restore Files
```bash
git checkout HEAD -- <file>  # Restore specific file
```

#### Step 3: 📜 Check Previous Versions
```bash
git show <commit>:<file>  # View older versions
```

#### Step 4: 🏠 Full Recovery
```bash
git revert <commit>  # Revert to known working state
```

### Then: Start Over with Minimal Changes

---

## 📖 Documentation Navigation for AI Assistants

### Primary Navigation
**Start here for ALL documentation queries**: `docs/QUICK_REFERENCE.md`
### Primary Navigation (UPDATED Nov 22, 2025)
**Start here for 30-second navigation**: `docs/08-development/AI_ASSISTANT_GUIDE.md` ⭐ **NEW**
- Complete quick-start guide for all AI assistants
- Direct links to common tasks
- Policy summaries with tier priorities
- Pre-change checklist
- Emergency recovery procedures

**Alternative entry points**:
- `docs/QUICK_REFERENCE.md` - Direct problem → solution mappings
- `DOCUMENTATION_MAP.md` - Complete documentation index  
- `.github/COPILOT_GENERATION_GUIDE.md` - Content generation step-by-step

### AI-Optimized Documentation Structure
1. **Immediate Problem Resolution**: `docs/QUICK_REFERENCE.md` 
2. **Comprehensive Navigation**: `docs/INDEX.md`
3. **API Issues**: `docs/api/ERROR_HANDLING.md` (includes terminal diagnostics)
4. **Component Help**: `docs/03-components/` for all component documentation
5. **Setup Issues**: `setup/API_CONFIGURATION.md` and `API_SETUP.md`
6. **Data Architecture**: `docs/DATA_ARCHITECTURE.md` (range propagation, null ranges explained)

### Common User Query Patterns
- **"Check data completeness"** → `python3 run.py --data-completeness-report`
- **"See data gaps / research priorities"** → `python3 run.py --data-gaps`
- **"Enforce completeness (strict mode)"** → `python3 run.py --enforce-completeness`
- **"API not working"** → `docs/api/ERROR_HANDLING.md#winston-ssl-issues`
- **"Content incomplete"** → `docs/api/ERROR_HANDLING.md#content-impact`
- **"Setup help"** → `setup/API_CONFIGURATION.md` or `API_SETUP.md`
- **"Winston SSL error"** → Known issue, configuration fixed
- **"How to generate content"** → `python3 run.py --material "MaterialName"`
- **"Min/max ranges missing"** → `docs/DATA_ARCHITECTURE.md` - Null ranges are correct by design
- **"Range propagation"** → `docs/DATA_ARCHITECTURE.md` + `tests/test_range_propagation.py`
- **"Frontmatter incomplete"** → `FRONTMATTER_POPULATION_REPORT.md` (58.3% complete)
- **"Category vs material ranges"** → `docs/DATA_ARCHITECTURE.md`

### Critical Known Issues for AI Awareness
1. **Winston API SSL fixed**: Now uses `https://api.gowinston.ai`
2. **Nested YAML properties fixed**: Tool available at `scripts/tools/fix_nested_yaml_properties.py`
3. **Terminal output required**: Always use `get_terminal_output()` for API diagnostics
4. **Range propagation documented**: `docs/DATA_ARCHITECTURE.md` + 14 passing tests
5. **Frontmatter 58.3% complete**: Technical data excellent (95%+), metadata gaps identified
6. **✅ RESOLVED: Voice validation false negative (Dec 12, 2025)** 🔥 **FIXED**
   - **Issue**: Validation check was looking for 'VOICE:' or 'voice_instruction' but actual prompt contains 'VOICE INSTRUCTIONS'
   - **Symptom**: Terminal showed "⚠️ NO voice instructions found in prompt!" despite voice being present
   - **Resolution**: Fixed validation check in generator.py line 350 to check for 'VOICE INSTRUCTIONS'
   - **Impact**: Voice instructions were ALWAYS being included in prompts, validation was just reporting false negative
7. **✅ RESOLVED: Persona files consolidated (Dec 11, 2025)** 🔥 **FIXED**
   - **Issue**: TWO DIFFERENT persona sets existed with conflicting voice instructions
     * Deprecated location: `shared/prompts/personas/` (no longer exists)
     * Current location: `shared/voice/profiles/*.yaml` - "Comprehensive Formal" style (detailed EFL patterns)
   - **Resolution**: Consolidated to comprehensive personas with detailed linguistics
     * Removed deprecated duplicate directory
     * Single source of truth: `shared/voice/profiles/` (comprehensive versions)
   - **Current personas include**: Full EFL patterns, voice examples, grammar norms, generation constraints
   - **Generation pipeline uses** `shared/voice/profiles/` (via Generator._load_all_personas())
   - **Status**: ✅ CONSOLIDATED with comprehensive linguistic characteristics restored
   - **Verification**: test_persona_loading_simple.py confirms correct loading (838-897 char voice instructions)
7. **✅ Field isolation tests FIXED (Dec 6, 2025)**: All 14 tests now passing
   - File: `tests/test_frontmatter_partial_field_sync.py` - 14/14 tests passing ✅
   - Resolution: Added domain parameter to all 16 sync_field_to_frontmatter() calls
   - Fix: Created domain config fixtures in test environment
   - Impact: **PRODUCTION UNBLOCKED** - Policy #3 (Field Isolation During Generation) verified
   - See: `docs/08-development/CLEANUP_AND_TEST_COVERAGE_ANALYSIS.md` for details
8. **Voice validation untested (Dec 6, 2025)**: No automated tests for voice compliance integration
   - VoicePostProcessor integrated into evaluated_generator.py ✅
   - Language detection and pattern scoring active ✅
   - Zero automated tests for integration ❌
   - Required: Create test suite before production use
   - See: `docs/08-development/CLEANUP_AND_TEST_COVERAGE_ANALYSIS.md` - Priority 2

### AI Assistant Best Practices
- Always check `docs/QUICK_REFERENCE.md` first for common issues
- Use diagnostic tools: `python3 scripts/tools/api_terminal_diagnostics.py winston`
- Reference specific file paths, not just general descriptions
- Recommend terminal output analysis for API issues
- Point to both immediate fixes and comprehensive documentation

## 🔧 **Terminal & Script Execution Settings**

### **Auto-Confirmation for Batch Operations**
When running cleanup scripts or batch operations, use these patterns:
- `rm -f` instead of `rm -i` (force, no confirmation)
- `yes | command` for auto-confirmation
- Check for `BATCH_MODE=1` environment variable in scripts
- Use `--yes` or `-y` flags when available

### **Environment Variables**
The following environment variables are set for auto-confirmation:
- `BATCH_MODE=1` - Skip interactive prompts
- `FORCE_YES=true` - Auto-confirm with "yes"
- `AUTO_CONFIRM=y` - Default response for prompts

### **Script Best Practices**
```bash
# Check for batch mode in scripts
if [[ -n "$BATCH_MODE" ]]; then
    # Skip confirmations
    rm -f files*
else
    # Normal interactive mode
    read -p "Continue? (y/N) " response
fi
```

### Critical Documentation for AI Assistants
**BEFORE** any data-related work, review these files:
1. **`docs/QUICK_REFERENCE.md`** - Fastest path to common solutions
2. **`docs/DATA_COMPLETION_ACTION_PLAN.md`** - Complete plan to achieve 100% data coverage
3. **`docs/ZERO_NULL_POLICY.md`** - Zero null policy & AI research methodology
4. **`docs/DATA_ARCHITECTURE.md`** - How ranges propagate through the system
5. **`docs/DATA_VALIDATION_STRATEGY.md`** - Validation architecture and quality gates

### Data Completion Context (October 17, 2025)
**Current Status**: 93.5% complete (1,975/2,240 properties)
**Missing**: 265 property values + 2 category ranges
**Priority**: 5 properties = 96% of all gaps
**Action Plan**: Fully documented in `docs/DATA_COMPLETION_ACTION_PLAN.md`
**Tools**: PropertyValueResearcher, CategoryRangeResearcher (operational)
**Quality**: Multi-strategy validation with 4 quality gates
**Timeline**: 1 week to 100% completeness
**✨ NEW Commands** (October 17, 2025):
  - `python3 run.py --data-completeness-report` - Full status report
  - `python3 run.py --data-gaps` - Research priorities
  
**⚡ AUTOMATIC (November 1, 2025)**: 
  - Data completeness validation now runs **automatically inline** during every generation
  - No flags needed - validation is built into the pipeline (strict mode enabled by default)
  - Use `--no-completeness-check` to disable if needed (not recommended)
  - Generation will **fail fast** if data is incomplete, prompting you to run research commands
  
**Enforcement**: Automatic linking to action plan when gaps detected

### Mandatory Documentation Review
**BEFORE** making ANY changes to text component code, you MUST:
1. **READ** the complete documentation: `docs/03-components/text/README.md`
2. **UNDERSTAND** the architecture: `docs/02-architecture/processing-pipeline.md`
3. **STUDY** the prompt system: `domains/*/prompts/` and `shared/text/templates/`
4. **REFERENCE** the generation code: `generation/core/evaluated_generator.py`

### Text Component Forbidden Actions
1. **NEVER** modify `fail_fast_generator.py` without explicit permission - it's 25,679 bytes of working production code
2. **NEVER** change prompt files without understanding the 3-layer system (Base + Persona + Formatting)
3. **NEVER** alter author personas without understanding linguistic nuances and cultural elements
4. **NEVER** modify word count limits or quality scoring thresholds
5. **NEVER** remove retry logic or error recovery mechanisms
6. **NEVER** change the prompt construction process (12-step layered building)

### Text Component Required Actions
1. **ALWAYS** preserve the multi-layered prompt architecture
2. **ALWAYS** maintain author authenticity and writing style consistency
3. **ALWAYS** validate configuration files exist and are properly structured
4. **ALWAYS** respect word count limits per author (250-450 words)
5. **ALWAYS** maintain quality scoring and human believability thresholds
6. **ALWAYS** use fail-fast validation with proper exception types
7. **ALWAYS** test with real API clients, never mocks

### Text Component Architecture Rules
- **Wrapper Pattern**: TextComponentGenerator is a lightweight wrapper for fail_fast_generator
- **Factory Integration**: Must work with ComponentGeneratorFactory.create_generator("text")
- **Three-Layer Prompts**: Base guidance + Author persona + Formatting rules
- **Quality Assurance**: 5-dimension scoring with human believability threshold
- **Author Authentication**: 4 country-specific personas with linguistic nuances
- **Configuration Caching**: LRU cache for YAML files, lazy loading for performance

### When Working on Text Component
1. **READ THE DOCS FIRST** - Check `docs/03-components/text/README.md` and `docs/02-architecture/processing-pipeline.md`
2. **Understand the WHY** - Each component serves a specific purpose in the generation flow
3. **Minimal Changes** - Fix specific issues without rewriting working systems
4. **Test Thoroughly** - Validate all 4 author personas work correctly
5. **Ask Permission** - Get explicit approval before major modifications

The text component documentation and processing pipeline docs cover the generation system. Use them as your primary reference for understanding and working with text generation code.

When suggesting code changes:
1. Maintain fail-fast behavior
2. Preserve existing working functionality
3. Use minimal, targeted changes
4. Follow established patterns and conventions
5. Include comprehensive error handling
6. Focus on reducing bloat
7. Prioritize changing existing components, not creating new ones
8. **ASK PERMISSION before removing any existing code**

### 🚨 CRITICAL: Frontmatter Source-of-Truth Policy 🔥 **MANDATORY (Dec 23, 2025)**

**📖 REQUIRED READING**: `docs/08-development/FRONTMATTER_SOURCE_OF_TRUTH_POLICY.md`

**THE FUNDAMENTAL RULE:**
Frontmatter files are **GENERATED OUTPUT**, NOT source data. ALL changes MUST be made in source data or export configurations, NEVER in frontmatter files directly.

**THE PROBLEM WITH TEMPORARY FIXES:**
If you create a "fix script" that patches frontmatter files directly, the fix will be **OVERWRITTEN** on the next `--export` because:
1. Frontmatter is **GENERATED FROM** data/*.yaml + export/config/*.yaml
2. The export process runs regularly and regenerates ALL frontmatter
3. Patching output files is **TEMPORARY** - they get regenerated on every export
4. You're editing "compiled binaries" instead of "source code"

**THE THREE-LAYER ARCHITECTURE:**
```
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1: SOURCE DATA (Single Source of Truth)                   │
│ • data/materials/Materials.yaml                                  │
│ • data/contaminants/Contaminants.yaml                           │
│ • data/associations/DomainAssociations.yaml                     │
│ • data/settings/Settings.yaml, data/compounds/Compounds.yaml    │
│ FIX HERE: When data is wrong (missing values, incorrect ranges) │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 2: EXPORT CONFIGURATION & LOGIC                           │
│ • export/config/*.yaml (domain configurations) ← FIX STRUCTURE  │
│ • export/enrichers/**/*.py (enrichment logic)                   │
│ • export/generation/**/*.py (field generators)                  │
│ • export/core/universal_exporter.py (orchestration)             │
│ FIX HERE: When generation logic/format/structure is wrong       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 3: FRONTMATTER FILES (Generated Output) ⛔ READ-ONLY      │
│ • ../z-beam/frontmatter/materials/*.yaml                        │
│ • ../z-beam/frontmatter/contaminants/*.yaml                     │
│ • ../z-beam/frontmatter/compounds/*.yaml                        │
│ • ../z-beam/frontmatter/settings/*.yaml                         │
│ • ❌ NEVER EDIT DIRECTLY - These get regenerated on every export│
└─────────────────────────────────────────────────────────────────┘
```

**THE CORRECT APPROACH:**
1. ✅ **Identify the layer** - Is this a data issue, generation logic issue, or export config issue?
2. ✅ **Fix at the source** - Edit the appropriate file in Layer 1 (data/*.yaml) or Layer 2 (export/config/*.yaml or export/**/*.py)
3. ✅ **Regenerate domain** - Run `python3 run.py --export --domain {domain}` to apply the fix
4. ✅ **Verify the fix persists** - Check multiple frontmatter files, ensure fix is present
5. ✅ **Test regeneration** - Export again to confirm fix persists through repeated exports
6. ❌ **NEVER create scripts that modify frontmatter files** - Layer 3 files directly

**PROHIBITED PATTERNS** (Grade F violations):
```bash
# ❌ WRONG: Direct frontmatter editing
sed -i '' 's/old/new/' frontmatter/materials/*.yaml
python3 fix_frontmatter.py  # Script that modifies Layer 3 files
# Result: Changes OVERWRITTEN on next export

# ✅ CORRECT: Fix export configuration
# Edit export/config/materials.yaml or export/enrichers/
python3 run.py --export --domain materials
# Result: Changes PERSIST through all future exports
```

**EXAMPLE 1 - Missing _section Metadata (Dec 23, 2025):**
- **Issue**: Relationship blocks missing `_section: {title, description, icon, order, variant}` metadata
- ❌ WRONG: Create script to add _section blocks to frontmatter/*.yaml files (tried v1, v2, normalize_relationships.py - all failed)
- ✅ RIGHT: Update export/config/*.yaml with complete section_metadata configuration + enhance SectionMetadataEnricher
- **Result**: Export generates frontmatter with complete _section metadata, persists through all future exports
- **Verification**: 793/793 contaminants (100%), 2/2 materials (100%), 14/14 compounds sampled (100%)
- WHY: Export config controls generation; changes to config affect ALL future exports

**EXAMPLE 2 - Breadcrumbs Wrong Format (Dec 18, 2025):**
- **Issue**: 422 frontmatter files had `breadcrumb_text: "Home / Materials / stone / Alabaster"` (text string)
- **Expected**: `breadcrumb: [{label: "Home", href: "/"}, {label: "Materials", href: "/materials"}]` (array)
- ❌ WRONG: Create script to convert breadcrumb_text to breadcrumb arrays in frontmatter files
- ✅ RIGHT: Removed `BreadcrumbGenerator` from export/config/*.yaml (Layer 2) - it was overwriting correct format
- **Result**: Next regeneration uses BreadcrumbEnricher in universal_exporter.py which creates proper arrays
- **Verification**: After regeneration, checked multiple files confirmed breadcrumb is array, breadcrumb_text removed
- WHY: Fixing the config prevents the bad generator from running; fix persists through all future regenerations

**VERIFICATION CHECKLIST - Did Your Fix Persist?**
After fixing at source (Layer 1 or 2) and regenerating:
- [ ] Check 3-5 files from each affected domain
- [ ] Confirm fix appears in ALL checked files (not just one)
- [ ] Verify old incorrect format is completely gone
- [ ] Export the domain again - does fix still persist?
- [ ] If fix disappeared → You fixed the wrong layer! (Edited Layer 3 instead of Layer 1/2)

**CRITICAL RULE: If frontmatter has an issue, fix Layer 1 (data) or Layer 2 (export config/logic), NOT Layer 3 (frontmatter).**

**Grade**: F violation if creating scripts that modify frontmatter files directly.

**Full Policy**: See `docs/08-development/FRONTMATTER_SOURCE_OF_TRUTH_POLICY.md` for complete rules, examples, and enforcement.

---

## 🤖 AI-Specific Guidance

### For GitHub Copilot Users
- **VS Code Integration**: Use Copilot's inline suggestions for minor edits
- **Context Awareness**: Leverage file tabs and workspace context
- **Quick Fixes**: Use Copilot Chat for rapid problem-solving
- **Documentation**: Reference this file via `.github/copilot-instructions.md`
- **Testing**: Run pytest in terminal for validation

### For Grok AI Users
- **Damage Prevention Focus**: Monitor the 🚨 Damage Warning Signs actively
- **Self-Monitoring**: Check your changes against the checklist after each edit
- **Recovery Emphasis**: Keep Emergency Recovery Procedures handy
- **Systematic Approach**: Follow the 6-step Pre-Change Checklist religiously
- **Permission Culture**: Always ask before major changes - better safe than sorry

### For All AI Assistants
- **Start with Quick Reference** at the top of this file
- **Complete the Pre-Change Checklist** before every modification
- **Preserve working code** - this is the #1 rule
- **No production mocks/fallbacks** - this is non-negotiable
- **Fail fast on config** but maintain runtime error recovery
- **Read text component docs** before touching text generation code
- **Use minimal changes** - surgical precision over comprehensive rewrites

---

## 📋 Summary Checklist for Every Task

**Before I start:**
- [ ] I understand the exact request
- [ ] I've explored the existing architecture
- [ ] I've checked git history for context
- [ ] I've planned the minimal fix needed
- [ ] **I've identified if this is a GENERATOR issue or DATA issue**

**During implementation:**
- [ ] I'm making only the requested changes
- [ ] I'm preserving all working functionality
- [ ] I'm following existing patterns and conventions
- [ ] I'm including proper error handling
- [ ] **If fixing frontmatter: I'm fixing the EXPORTER, not patching files**

**For text component work:**
- [ ] I've read the documentation in `docs/03-components/text/` and `docs/02-architecture/processing-pipeline.md`
- [ ] I understand the multi-layered architecture
- [ ] I have permission for any major changes
- [ ] I'm testing with real API clients

**After completion:**
- [ ] The specific issue is resolved
- [ ] No working functionality was broken
- [ ] The solution is complete and secure
- [ ] I haven't expanded beyond the requested scope
- [ ] No production mocks or fallbacks were introduced
- [ ] **If I fixed a generator: I've regenerated the output and verified persistence**
