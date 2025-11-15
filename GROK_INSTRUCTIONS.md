# Grok Instructions for Z-Beam Generator

## 🎯 Mission Statement
You are working on a **laser cleaning content generation system** with strict fail-fast architecture. Your role is to make **minimal, targeted fixes** while preserving all working functionality.

## ⚡ Quick Reference Card

**📘 FIRST: Read [docs/AI_QUICK_REFERENCE.md](./docs/AI_QUICK_REFERENCE.md) for coding patterns**

**BEFORE ANY CHANGE:**
1. ✅ Read the request precisely
2. ✅ Explore existing architecture
3. ✅ Check git history for context
4. ✅ Plan minimal fix only
5. ✅ Ask permission for major changes

**GOLDEN RULES:**
- 🚫 **NEVER rewrite working code**
- 🚫 **NEVER expand beyond requested scope**
- 🚫 **NEVER use mocks/fallbacks in production code - NO EXCEPTIONS**
- ✅ **ALLOW mocks/fallbacks in test code for proper testing**
- 🚫 **NEVER add "skip" logic or dummy test results**
- 🚫 **NEVER create placeholder return values**
- ✅ **ALWAYS preserve existing patterns**
- ✅ **ALWAYS fail-fast on configuration issues**
- ✅ **ALWAYS maintain runtime error recovery**

## 🚨 **ZERO TOLERANCE FOR MOCKS/FALLBACKS IN PRODUCTION CODE**

**ANY** code that returns a default value, skips validation, or provides placeholder data is **STRICTLY FORBIDDEN** in production code. This includes:
- `return True` when tests don't exist
- `result = {} if not found` patterns
- `or "default"` fallback values
- Skip logic that bypasses validation
- Mock API responses outside test files

### 🎭 **TEST CODE EXCEPTION**
**✅ Mocks and fallbacks ARE ALLOWED in test code** for the following purposes:
- Unit testing without external dependencies
- Integration testing with controlled scenarios
- Performance testing with mock responses
- Error handling testing with simulated failures

### 🔍 **TESTING REQUIREMENT**
**Part of testing should include verifying ZERO presence of mocks and fallbacks in production code:**
- Static analysis to detect mock usage in non-test files
- Code review checks for fallback patterns
- Automated tests that fail if production code contains mocks
- Build verification that excludes mock dependencies from production builds

## 📖 Key Definitions

### Fail-Fast Architecture
- ✅ **What it IS**: Validate inputs, configurations, and dependencies immediately at startup
- ✅ **What it IS**: Throw specific exceptions (ConfigurationError, GenerationError) with clear messages
- ❌ **What it's NOT**: Removing runtime error recovery like API retries

### Mocks/Fallbacks
- ❌ **Prohibited in Production**: No MockAPIClient, no default values, no silent failures
- ✅ **Allowed in Testing**: Retain existing mocks for test infrastructure (ask before removing)
- 🔍 **Testing Requirement**: Verify zero presence of mocks/fallbacks in production code

### Minimal Changes
- 🎯 **Target**: Fix only the specific issue requested
- 🎯 **Scope**: Modify the smallest amount of code needed
- 🎯 **Preserve**: All working parts remain untouched

## 🔒 Core Rules (Non-Negotiable)

### 1. 🛡️ Preserve Working Code
- **NEVER rewrite or replace** functioning code, classes, or modules
- **ONLY make targeted fixes** - if `fail_fast_generator.py` works, integrate around it
- **Example**: Add missing method ≠ Rewrite entire class

### 2. 🚫 No Production Mocks/Fallbacks
- **Fail immediately** if dependencies are missing
- **No defaults, mock clients, or silent recoveries** in core logic
- **No skip logic, placeholder returns, or dummy values**
- **✅ ALLOWED in test code** for proper testing infrastructure
- **🔍 REQUIRE testing** to verify zero mocks/fallbacks in production
- **VIOLATION EXAMPLES TO AVOID**:
  - `test_results['missing'] = True  # Skip logic`
  - `return "default" if not data`
  - `except: pass  # Silent failure`

### 3. ⚡ Fail-Fast on Setup
- **Validate all inputs and configs upfront** - no degraded operation
- **Throw errors early** with specific exception types
- **Preserve runtime mechanisms** like API retries for transient issues

### 4. 🏗️ Respect Existing Patterns
- **Maintain**: ComponentGeneratorFactory, wrapper classes, ComponentResult objects
- **Preserve**: File structure and directory organization
- **Prefer**: Editing existing files over creating new ones

### 5. 🎯 Surgical Precision
- **Identify exact problem** → **Find smallest change** → **Test only that fix**
- **No scope expansion** - fix X means fix only X
- **Complete solutions** - don't leave parts for user to debug

### 6. 🗣️ Linguistic Patterns Location
- **KEEP linguistic patterns ONLY in `components/text/prompts/personas/`**
- **NEVER duplicate or move linguistic patterns** to other configuration files
- **ALWAYS reference personas for nationality-specific language variations**
- **Exception**: Brief summaries may exist in other files, but detailed patterns stay in personas

### 7. 🔍 Prompt Chain Verification
- **VERIFY prompt chain integration** in frontmatter using `prompt_chain_verification` metadata
- **CHECK frontmatter** contains verification fields: base_config_loaded, persona_config_loaded, etc.
- **VALIDATE** all 4 prompt components (base, persona, formatting, AI detection) were integrated
- **CONFIRM** cultural adaptation and human authenticity focus were applied
- **USE** `verify_frontmatter_prompt_chain.py` script to validate generated content

## 📚 Lessons from Past Failures

### 🚨 Critical Failure Patterns to Avoid

| 🔥 Episode | 👤 Request | ❌ Mistake | 💥 Damage | ✅ Correct Approach |
|------------|------------|------------|-----------|-------------------|
| **Factory Destruction** | Add missing method | Rewrote entire class | Lost all generator discovery | Add ONLY the requested method |
| **Generator Replacement** | Fix integration | Ignored existing file | Lost all functionality | Integrate around existing code |
| **Mock Removal** | Remove fallbacks | Deleted without understanding | Broke testing infrastructure | Understand purpose first |
| **Fallback Destruction** | Ensure fail-fast | Removed error recovery | Failed on transient errors | Fail-fast ≠ no retries |
| **Scope Creep** | Fix specific issue | Expanded beyond request | Integration failures | Stick to exact scope |

### 🎯 Success Pattern
1. **Understand** the existing code
2. **Identify** the minimal change needed
3. **Implement** only that change
4. **Verify** the fix works
5. **Confirm** nothing else broke

## ✅ Mandatory Pre-Change Checklist

**Before making ANY modification, complete ALL steps:**

### Step 1: 📖 Read & Understand
- [ ] **Read request precisely** - What is the *exact* issue?
- [ ] **No assumptions** - Ask for clarification if unclear

### Step 2: 🔍 Explore Architecture
- [ ] **Read relevant code** - Understand how it currently works
- [ ] **Check subdirectories** - Don't miss important context
- [ ] **Verify file existence** - Prevent "Content Not Found" errors

### Step 3: 📜 Check History
- [ ] **Review git commits** - See what was working previously
- [ ] **Use `git show`** - Understand recent changes

### Step 4: 🎯 Plan Minimal Fix
- [ ] **Identify smallest change** - Address only the specific issue
- [ ] **Ensure security** - Include validation and error handling
- [ ] **Keep it concise** - Avoid unnecessary complexity

### Step 5: 💬 Communicate Plan
- [ ] **Describe approach** - Explain what you'll change before coding
- [ ] **Be realistic** - No sandbagging or unrealistic timelines
- [ ] **Ask permission** - Before removing code or major changes

### Step 6: 🔧 Implement & Test
- [ ] **Apply the fix** - Make only the planned changes
- [ ] **Verify it works** - Test the specific issue is resolved
- [ ] **Check for regressions** - Ensure nothing else broke
- [ ] **🔍 Verify no production mocks** - Confirm changes don't introduce mocks/fallbacks in production code

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

## 🚨 Damage Warning Signs

Watch for these indicators of problems:
- 🔴 **System stops working** after your changes
- 🔴 **Multiple files altered** for a single fix request
- 🔴 **User mentions damage** or restores from git
- 🔴 **Added complexity** where simple change would work
- 🔴 **Security vulnerabilities** or incomplete code introduced

## 🏗️ Project Context

**System:** Z-Beam laser cleaning content generation
**Scale:** 109 materials, sophisticated multi-component architecture
**APIs:** Grok, DeepSeek integration
**Architecture:** Component-based with strict validation, no defaults

## 🔥 TEXT COMPONENT - CRITICAL SYSTEM CORE

### 🚨 EXTREME CAUTION REQUIRED
The text component (`components/text/`) is the **MOST CRITICAL** part of the system:
- **25,679 bytes** of production-ready code
- **Sophisticated multi-layered prompt engineering**
- **Core revenue-generating functionality**

### 📚 MANDATORY READING BEFORE ANY TEXT WORK

**You MUST read these files BEFORE touching ANY text component code:**

1. 📖 **`components/text/docs/README.md`** - Start here for overview
2. 🏗️ **`components/text/docs/CONTENT_GENERATION_ARCHITECTURE.md`** - System architecture
3. 🎯 **`components/text/docs/PROMPT_SYSTEM.md`** - Prompt engineering details
4. 📚 **`components/text/docs/API_REFERENCE.md`** - API documentation

### 🚫 TEXT COMPONENT FORBIDDEN ACTIONS

**ABSOLUTELY NEVER:**
1. Modify `fail_fast_generator.py` without explicit permission
2. Change prompt files without understanding 3-layer system
3. Alter author personas (linguistic nuances are carefully crafted)
4. Modify word count limits (250-450 words per author)
5. Remove retry logic or error recovery mechanisms
6. Change the 12-step prompt construction process

### ✅ TEXT COMPONENT REQUIRED ACTIONS

**ALWAYS:**
1. Preserve multi-layered prompt architecture (Base + Persona + Formatting)
2. Maintain author authenticity and writing style consistency
3. Validate configuration files exist and are properly structured
4. Respect word count limits per author
5. Maintain quality scoring and human believability thresholds
6. Use fail-fast validation with proper exception types
7. Test with real API clients, never mocks

### 🏛️ Text Component Architecture Overview

- **Wrapper Pattern**: `TextComponentGenerator` wraps `fail_fast_generator`
- **Factory Integration**: Works with `ComponentGeneratorFactory.create_generator("text")`
- **Three-Layer Prompts**: Base guidance + Author persona + Formatting rules
- **Quality Assurance**: 5-dimension scoring with human believability threshold
- **Author Authentication**: 4 country-specific personas with linguistic nuances
- **Configuration Caching**: LRU cache for YAML files, lazy loading

### 🔧 Text Component Work Protocol

1. **📖 READ THE DOCS FIRST** - All answers are in `components/text/docs/`
2. **🤔 Understand the WHY** - Each component serves a specific purpose
3. **🎯 Minimal Changes** - Fix specific issues without rewriting working systems
4. **🧪 Test Thoroughly** - Validate all 4 author personas work correctly
5. **🙋 Ask Permission** - Get explicit approval before major modifications

**The text component documentation is comprehensive and covers every aspect of the system. Use it as your primary reference.**

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

## � Deployment & Monitoring Protocol

### 🚨 MANDATORY: Always Monitor Deployments

**WHEN PUSHING TO MAIN:**
1. **Push changes** to GitHub
2. **IMMEDIATELY start deployment monitoring** - NO EXCEPTIONS
3. **Wait for completion** - Don't move to next task until deployment finishes
4. **Report status** to user (success/failure, deployment time, URL)

### �📋 Deployment Monitoring Methods

**Option 1: Smart Deploy Script (PREFERRED)**
```bash
cd scripts/deployment
./smart-deploy.sh monitor
```

**Option 2: Node Monitor (RECOMMENDED)**
```bash
node scripts/deployment/monitor-deployment.js
```

**Option 3: VS Code Task**
- Press `Cmd+Shift+P` → "Tasks: Run Task" → "Monitor Vercel Deployment"

### ✅ What Monitoring Provides

- **Real-time build status** (Building, Queued, Ready, Error)
- **Deployment URL** and environment
- **Total deployment time**
- **Automatic failure detection** with logs
- **Exit codes** for success/failure validation

### 🚫 NEVER Skip Monitoring

**Reasons monitoring is MANDATORY:**
- Catches build failures immediately
- Detects configuration issues
- Verifies production deployment success
- Provides deployment URL for verification
- Alerts on timeout issues (max 10 minutes)

**VIOLATION:** Pushing code and not monitoring = incomplete task

### 📚 Full Documentation

See `scripts/deployment/README.md` for:
- Complete setup instructions
- GitHub Actions integration
- NPM scripts
- Git hooks
- Troubleshooting guide

## 📋 Summary Checklist for Every Task

**Before I start:**
- [ ] I understand the exact request
- [ ] I've explored the existing architecture
- [ ] I've checked git history for context
- [ ] I've planned the minimal fix needed

**During implementation:**
- [ ] I'm making only the requested changes
- [ ] I'm preserving all working functionality
- [ ] I'm following existing patterns and conventions
- [ ] I'm including proper error handling

**For text component work:**
- [ ] I've read the documentation in `components/text/docs/`
- [ ] I understand the multi-layered architecture
- [ ] I have permission for any major changes
- [ ] I'm testing with real API clients

**After completion:**
- [ ] The specific issue is resolved
- [ ] No working functionality was broken
- [ ] The solution is complete and secure
- [ ] I haven't expanded beyond the requested scope

**For deployments to main:**
- [ ] Code is pushed to GitHub
- [ ] 🚨 **DEPLOYMENT MONITORING IS RUNNING** 🚨
- [ ] Monitoring shows final status (Ready/Error)
- [ ] User is informed of deployment result
- [ ] Deployment URL is provided if successful

````
