# AI Assistant Instructions for Z-Beam Generator

**For**: GitHub Copilot, Grok AI, and all AI development assistants  
**System**: Laser cleaning content generation with strict fail-fast architecture  
**Last Updated**: October 14, 2025

---

## 🎯 Quick Reference Card

**READ THIS FIRST - BEFORE ANY CHANGE:**

1. ✅ **Read the request precisely** - What is the *exact* issue?
2. ✅ **Explore existing architecture** - Understand how it currently works
3. ✅ **Check git history for context** - See what was working previously
4. ✅ **Plan minimal fix only** - Address only the specific issue
5. ✅ **Ask permission for major changes** - Get approval before removing code or rewrites

**GOLDEN RULES:**
- 🚫 **NEVER rewrite working code**
- 🚫 **NEVER expand beyond requested scope**
- 🚫 **NEVER use mocks/fallbacks in production code - NO EXCEPTIONS**
- ✅ **ALLOW mocks/fallbacks in test code for proper testing**
- 🚫 **NEVER add "skip" logic or dummy test results**
- ✅ **ALWAYS preserve existing patterns**
- ✅ **ALWAYS fail-fast on configuration issues**
- ✅ **ALWAYS maintain runtime error recovery**

---

## 📖 Core Principles

### 1. **No Mocks or Fallbacks in Production Code**
System must fail immediately if dependencies are missing. **ZERO TOLERANCE** for:
- MockAPIClient or mock responses in production
- Default values that bypass validation (`or "default"`)
- Skip logic that bypasses checks (`if not exists: return True`)
- Placeholder return values (`return {}`)
- Silent failures (`except: pass`)

**✅ EXCEPTION**: Mocks and fallbacks **ARE ALLOWED in test code** for proper testing infrastructure.

**🔍 TESTING REQUIREMENT**: Part of testing should include verifying ZERO presence of mocks and fallbacks in production code.

### 2. **Explicit Dependencies**
All required components must be explicitly provided - no silent degradation.

### 3. **Data Storage Policy** 🔥 **CRITICAL**
**ALL data updates MUST be saved to Materials.yaml or Categories.yaml.**

- ✅ **Materials.yaml** - Single source of truth for all material data
- ✅ **Categories.yaml** - Single source of truth for all category data
- ❌ **Frontmatter files** - OUTPUT ONLY, never data storage
- ✅ **Data Flow**: Materials.yaml → Frontmatter (one-way only)
- ✅ **Persistence**: All AI research saves to Materials.yaml immediately
- ❌ **Never read frontmatter** for data persistence (only for output verification)

See `docs/DATA_STORAGE_POLICY.md` for complete policy.

### 4. **Component Architecture**
Use ComponentGeneratorFactory pattern for all generators.

### 5. **Fail-Fast Design**
- ✅ **What it IS**: Validate inputs, configurations, and dependencies immediately at startup
- ✅ **What it IS**: Throw specific exceptions (ConfigurationError, GenerationError) with clear messages
- ❌ **What it's NOT**: Removing runtime error recovery like API retries for transient issues

## Code Standards
- Use strict typing with Optional[] for nullable parameters
- Implement comprehensive error handling with specific exception types
- No default values for critical dependencies (API clients, configuration files)
- Log all validation steps and failures clearly
- Keep code concise and avoid unnecessary complexity
- Never leave TODOs - provide complete solutions
- Never hardcode values - use configuration or parameters

## Architecture Patterns
- **Wrapper Pattern**: Use lightweight wrappers to integrate specialized generators
- **Factory Pattern**: ComponentGeneratorFactory for component discovery and creation
- **Result Objects**: Return structured ComponentResult objects with success/error states
- **Configuration Validation**: Validate all required files and settings on startup
- **Linguistic Patterns**: Keep ONLY in `components/text/prompts/personas/` - never duplicate elsewhere

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

## 🔒 Core Rules (Non-Negotiable)

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

### Rule 3: ⚡ Fail-Fast on Setup
- **Validate all inputs and configs upfront** - no degraded operation
- **Throw errors early** with specific exception types
- **Preserve runtime mechanisms** like API retries for transient issues

### Rule 4: 🏗️ Respect Existing Patterns
- **Maintain**: ComponentGeneratorFactory, wrapper classes, ComponentResult objects
- **Preserve**: File structure and directory organization
- **Prefer**: Editing existing files over creating new ones

### Rule 5: 🎯 Surgical Precision
- **Identify exact problem** → **Find smallest change** → **Test only that fix**
- **No scope expansion** - fix X means fix only X
- **Complete solutions** - don't leave parts for user to debug

### Rule 6: 🔍 Prompt Chain Verification
- **VERIFY prompt chain integration** in frontmatter using `prompt_chain_verification` metadata
- **CHECK frontmatter** contains verification fields: base_config_loaded, persona_config_loaded, etc.
- **VALIDATE** all 4 prompt components (base, persona, formatting, AI detection) were integrated
- **USE** `verify_frontmatter_prompt_chain.py` script to validate generated content

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

### 🎯 Success Pattern
1. **Understand** the existing code
2. **Identify** the minimal change needed
3. **Implement** only that change
4. **Verify** the fix works
5. **Confirm** nothing else broke

---

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
- Contains direct problem → solution mappings
- Lists most common user questions with immediate answers
- Provides file location quick map for efficient navigation
- Includes essential commands and critical known issues

### AI-Optimized Documentation Structure
1. **Immediate Problem Resolution**: `docs/QUICK_REFERENCE.md` 
2. **Comprehensive Navigation**: `docs/INDEX.md`
3. **API Issues**: `docs/api/ERROR_HANDLING.md` (includes terminal diagnostics)
4. **Component Help**: `components/[component]/README.md` or `components/[component]/docs/README.md`
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

### AI Assistant Best Practices
- Always check `docs/QUICK_REFERENCE.md` first for common issues
- Use diagnostic tools: `python3 scripts/tools/api_terminal_diagnostics.py winston`
- Reference specific file paths, not just general descriptions
- Recommend terminal output analysis for API issues
- Point to both immediate fixes and comprehensive documentation

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
  - `python3 run.py --enforce-completeness` - Strict mode (blocks if incomplete)
**Enforcement**: Automatic linking to action plan when gaps detected

### Mandatory Documentation Review
**BEFORE** making ANY changes to text component code, you MUST:
1. **READ** the complete documentation: `components/text/docs/README.md`
2. **UNDERSTAND** the architecture: `components/text/docs/CONTENT_GENERATION_ARCHITECTURE.md`
3. **STUDY** the prompt system: `components/text/docs/PROMPT_SYSTEM.md`
4. **REFERENCE** the API: `components/text/docs/API_REFERENCE.md`

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
1. **READ THE DOCS FIRST** - All answers are in `components/text/docs/`
2. **Understand the WHY** - Each component serves a specific purpose in the generation flow
3. **Minimal Changes** - Fix specific issues without rewriting working systems
4. **Test Thoroughly** - Validate all 4 author personas work correctly
5. **Ask Permission** - Get explicit approval before major modifications

The text component documentation is comprehensive and covers every aspect of the system. Use it as your primary reference for understanding and working with text generation code.

When suggesting code changes:
1. Maintain fail-fast behavior
2. Preserve existing working functionality
3. Use minimal, targeted changes
4. Follow established patterns and conventions
5. Include comprehensive error handling
6. Focus on reducing bloat
7. Prioritize changing existing components, not creating new ones
8. **ASK PERMISSION before removing any existing code**

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
- [ ] No production mocks or fallbacks were introduced
