# 🚨 GROK QUICK REFERENCE - READ BEFORE EVERY CODE CHANGE

## 📘 PRIMARY DOCUMENTATION
**➡️ MAIN REFERENCE: [.github/copilot-instructions.md](/.github/copilot-instructions.md)**

This file provides **quick lookup** for tier priorities and decision trees.  
For complete rules, policies, and guardrails, see **copilot-instructions.md**.

---

## ⚡ CRITICAL RULES (Full details in copilot-instructions.md)

### 🔴 TIER 1: SYSTEM-BREAKING (Will cause failures)
1. ❌ **NO mocks/fallbacks in production code** (tests OK) - [Rule 2](#)
2. ❌ **NO hardcoded values/defaults** (use config/dynamic calc) - [Rule 3](#)
3. ❌ **NO rewriting working code** (minimal surgical fixes only) - [Rule 1](#)

### 🟡 TIER 2: QUALITY-CRITICAL (Will cause bugs)
4. ❌ **NO expanding scope** (fix X means fix ONLY X) - [Rule 5](#)
5. ❌ **NO skipping validation** (must test before claiming success) - [Step 6](#)
6. ✅ **ALWAYS fail-fast on config** (throw exceptions, no silent degradation) - [Rule 3](#)
7. ✅ **ALWAYS preserve runtime recovery** (API retries are correct) - [ADR-002](#)
8. ✅ **ALWAYS log to terminal** (all generation attempts, scores, feedback) - See Terminal Output Policy below

### 🟢 TIER 3: EVIDENCE & HONESTY (Will lose trust)
9. ✅ **ALWAYS provide evidence** (test output, counts, commits) - [Protocol](#)
10. ✅ **ALWAYS be honest** (acknowledge what remains broken) - [Protocol](#)
11. ✅ **ASK before major changes** (get permission for improvements) - [Rule 1](#)
12. ✅ **VERIFY before claiming violations** (check config files, confirm pattern exists) 🔥 **NEW (Nov 20, 2025)**

**🚨 CRITICAL: Claiming violations without verification is a TIER 3 violation itself.**

---

## 📋 TERMINAL OUTPUT LOGGING POLICY 🔥 **NEW (Nov 18, 2025)**

**ALL generation operations MUST stream comprehensive output to terminal in real-time.**

**Logging Requirements**:
1. **Stream to stdout/stderr ONLY** - No log files created or saved
2. **Real-time output** - User sees progress as it happens
3. **Attempt Progress** - Every retry with attempt number (e.g., "Attempt 2/5")
4. **Quality Checks** - Winston score, Realism score, thresholds, pass/fail
5. **Feedback Application** - Parameter adjustments between attempts
6. **Learning Activity** - Prompt optimization, pattern learning
7. **Final Report** - Complete generation report (see GROK_INSTRUCTIONS.md)

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

## 🚦 DECISION TREES

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

### Decision: Is this a mock/fallback violation?
```
What type of code is this?
├─ PRODUCTION CODE → ❌ NO mocks/fallbacks/defaults (ZERO TOLERANCE)
└─ TEST CODE → ✅ Mocks/fallbacks ALLOWED (testing infrastructure)
```

### Decision: Should I report a violation? 🔥 **NEW (Nov 20, 2025)**
```
Have I found suspect code pattern (.get with default)?
├─ NO → Not a violation
└─ YES → Does the key exist in config?
    ├─ YES → ✅ NOT A VIOLATION (valid fallback for optional key)
    └─ NO → Is this key supposed to be required?
        ├─ UNCLEAR → ⚠️ ASK USER (don't assume violation)
        └─ YES → ✅ VIOLATION (should fail-fast if missing)

CRITICAL: grep -r "key_name" config.yaml BEFORE reporting violation
Example: .get('intensity', 5) → Check if 'intensity' exists in config
```

### Decision: Should I claim "fixed" or "working"?
```
Have I run comprehensive tests?
├─ NO → ❌ DON'T CLAIM (validate first)
└─ YES → Do I have evidence?
    ├─ NO → ❌ DON'T CLAIM (capture output)
    └─ YES → Have I counted total vs passing?
        ├─ NO → ❌ DON'T CLAIM (be specific)
        └─ YES → Have I acknowledged what remains broken?
            ├─ NO → ❌ INCOMPLETE (mention limitations)
            └─ YES → ✅ CAN CLAIM with evidence

Example: "Fixed 11/11 requested failures (23/23 passing). 
Note: 10 other test files still have import errors."
```

---

## 📋 MANDATORY PRE-CHANGE CHECKLIST

**⏱️ PHASE 1-3: Complete research BEFORE coding (7-11 minutes prevents hours of fixing)**

**Phase 1: Verification (2-3 minutes)**
- [ ] Read request word-by-word (what EXACTLY is requested?)
- [ ] Check for assumptions (am I assuming anything not stated?)
- [ ] Verify file paths (do all referenced files exist?)
- [ ] Check config keys (do claimed violations exist in config files?)
- [ ] Search for existing solutions (does DynamicConfig/helper already solve this?)

**Phase 2: Research (3-5 minutes)**
- [ ] grep_search for patterns (how does system currently handle this?)
- [ ] Read relevant code (understand current implementation)
- [ ] Check git history (was this tried before? why changed?)
- [ ] Review docs/ (is there policy documentation?)
- [ ] Check ADRs (is there an architectural decision?)

**Phase 3: Planning (2-3 minutes)**
- [ ] Identify exact change needed (one sentence description)
- [ ] Confirm minimal scope (am I fixing ONLY what was requested?)
- [ ] Check for side effects (what else might this affect?)
- [ ] Plan validation (how will I prove it works?)
- [ ] Get permission if major (ask before removing/rewriting code)

**Before committing:**
- [ ] Ran comprehensive tests (not just 1 example)
- [ ] Captured evidence (test output, file counts)
- [ ] Verified no regressions (nothing else broke)
- [ ] Checked for violations (no mocks in production, no hardcoded values)
- [ ] Honest assessment (acknowledged limitations)
- [ ] Graded my work (A/B/C/F with evidence)

---

## 🚨 WHEN UNCERTAIN - STOP SIGNALS

**IF YOU'RE NOT SURE:**
1. 🛑 **STOP coding immediately**
2. 📖 **READ** relevant copilot-instructions.md section
3. 🤔 **CHECK** decision tree above
4. ❓ **ASK** user for clarification
5. 📚 **REFERENCE** specific ADR or doc section

**🚨 STOP SIGNALS - When to ASK instead of CODE:**
- ❓ Not 100% certain about the requirement
- ❓ Can't find the config key/file/pattern being referenced
- ❓ Fixing this requires changing more than 3 files
- ❓ About to add hardcoded value without finding dynamic config first
- ❓ Request conflicts with existing architecture
- ❓ Tests failing and don't understand why

**NEVER assume or guess when uncertain.**

---

## 🏆 SELF-ASSESSMENT (Grade Before Reporting)

**Grade A (90-100): Excellence**
- ✅ All changes work + comprehensive evidence + honest about limitations
- ✅ Zero violations introduced + zero scope creep
- ✅ Verification completed before claiming violations

**Grade B (80-89): Good**
- ✅ Changes work + some evidence + minor issues remain

**Grade C (70-79): Needs Improvement**
- ⚠️ Partial success + missing evidence + significant issues

**Grade F (<70): Unacceptable** 
- ❌ Made things worse + no evidence + false claims
- ❌ Reported violations without verification

**Example A-grade report:**
```
✅ Fixed 3/3 requested violations
📊 Evidence: 24/24 tests passing (see output below)
✅ Commit: abc123def
✅ Verified: grep confirms no config keys missing
⚠️ Note: 2 TODO comments remain (documented as future work)
🏆 Grade: A (95/100)
```

---

## 📂 QUICK FILE REFERENCE

- **Full instructions**: `GROK_INSTRUCTIONS.md`
- **Fail-fast vs retry**: `docs/decisions/ADR-002-fail-fast-vs-runtime-recovery.md`
- **Content instructions**: `docs/prompts/CONTENT_INSTRUCTION_POLICY.md`
- **Data storage**: `docs/data/DATA_STORAGE_POLICY.md`
- **System interactions**: `docs/SYSTEM_INTERACTIONS.md`
- **Quick answers**: `docs/QUICK_REFERENCE.md`

---

**🎯 REMEMBER: Validate before claiming success. Provide evidence with every claim. Be honest about limitations.**
