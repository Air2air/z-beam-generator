# 🚨 GROK QUICK REFERENCE - READ BEFORE EVERY CODE CHANGE

## ⚡ CRITICAL RULES (See GROK_INSTRUCTIONS.md for full details)

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

**Before writing ANY code:**
- [ ] Read request precisely (what EXACTLY is requested?)
- [ ] Check GROK_INSTRUCTIONS relevant sections
- [ ] Explore existing architecture (how does it work now?)
- [ ] Plan minimal fix (smallest change needed)
- [ ] Ask permission if expanding scope

**Before committing:**
- [ ] Ran comprehensive tests (not just 1 example)
- [ ] Captured evidence (test output, file counts)
- [ ] Verified no regressions (nothing else broke)
- [ ] Checked for violations (no mocks in production, no hardcoded values)
- [ ] Honest assessment (acknowledged limitations)

---

## 🚨 WHEN UNCERTAIN

**IF YOU'RE NOT SURE:**
1. 🛑 **STOP coding**
2. 📖 **READ** relevant GROK_INSTRUCTIONS section
3. 🤔 **CHECK** decision tree above
4. ❓ **ASK** user for clarification
5. 📚 **REFERENCE** specific ADR or doc section

**NEVER assume or guess when uncertain.**

---

## 🏆 SELF-ASSESSMENT

**Before reporting results:**
- [ ] Grade A (90-100): All changes work + comprehensive evidence + honest about limitations
- [ ] Grade B (80-89): Changes work + some evidence + minor issues remain
- [ ] Grade C (70-79): Partial success + missing evidence + significant issues
- [ ] Grade F (<70): Made things worse + no evidence + false claims

**Example A-grade report:**
```
✅ Fixed 11/11 requested test failures
📊 Evidence: 23/23 tests passing (see output below)
✅ Commit: 3125e555
⚠️ Note: 10 other test files still have import errors (not in scope)
🏆 Grade: A (100/100)
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
