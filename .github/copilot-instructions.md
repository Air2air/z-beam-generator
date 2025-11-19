# AI Assistant Instructions for Z-Beam Generator

**For**: GitHub Copilot, Grok AI, Claude, and all AI development assistants  
**System**: Laser cleaning content generation with strict fail-fast architecture  
**Last Updated**: November 18, 2025

---

## 📖 **Quick Navigation for AI Assistants**

### **User Requests Content Generation?**
→ **READ THIS FIRST**: `.github/COPILOT_GENERATION_GUIDE.md`
- Handles: "Generate subtitle for Aluminum", "Create caption for Steel", etc.
- Shows: Exact commands to run, terminal output handling, result reporting
- Covers: All component types (subtitle, caption, FAQ, description)

### **Need Documentation?**
→ **START HERE**: Root `/DOCUMENTATION_MAP.md` - Complete map of all documentation
→ **QUICK ANSWERS**: `docs/QUICK_REFERENCE.md` - Fastest path to solutions
→ **SYSTEM INDEX**: `docs/INDEX.md` - Comprehensive navigation

### **Working on Code/Architecture?**
→ **READ FIRST**: `docs/SYSTEM_INTERACTIONS.md` - Understand cascading effects before changing anything
→ **THEN CHECK**: `docs/decisions/README.md` - Architecture Decision Records (WHY things work this way)
→ **Continue below** for development guidelines and system rules

### **⚠️ Before Making ANY Change**
1. **Check `docs/SYSTEM_INTERACTIONS.md`**: What will your change affect?
2. **Check `docs/decisions/`**: Is there an ADR about this?
3. **Check git history**: Has this been tried and failed before?
4. **Plan minimal fix**: Address only the specific issue

---

## 🎯 Quick Reference Card

**READ THIS FIRST - BEFORE ANY CHANGE:**

1. ✅ **Read the request precisely** - What is the *exact* issue?
2. ✅ **Search documentation FIRST** - Check `docs/` for existing guidance (see Documentation Compliance Checklist below)
3. ✅ **Explore existing architecture** - Understand how it currently works
4. ✅ **Check git history for context** - See what was working previously
5. ✅ **Plan minimal fix only** - Address only the specific issue
6. ✅ **Ask permission for major changes** - Get approval before removing code or rewrites

**GOLDEN RULES:**
- 🚫 **NEVER rewrite working code**
- 🚫 **NEVER expand beyond requested scope**
- 🚫 **NEVER use mocks/fallbacks in production code - NO EXCEPTIONS**
- ✅ **ALLOW mocks/fallbacks in test code for proper testing**
- 🚫 **NEVER add "skip" logic or dummy test results**
- 🚫 **NEVER put content instructions in /processing folder code**
- 🚫 **NEVER hardcode component types in /processing code**
- 🚫 **NEVER hardcode values in production code** - use config or dynamic calculation
- ✅ **ALWAYS keep content instructions ONLY in prompts/*.txt files**
- ✅ **ALWAYS define components ONLY in prompts/*.txt and config.yaml**
- ✅ **ALWAYS preserve existing patterns**
- ✅ **ALWAYS fail-fast on configuration issues**
- ✅ **ALWAYS maintain runtime error recovery**

---

## 📚 Recent Critical Updates (November 2025)

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

---

## 📖 Core Principles

### 1. **No Mocks or Fallbacks in Production Code**
System must fail immediately if dependencies are missing. **ZERO TOLERANCE** for:
- MockAPIClient or mock responses in production
- Default values that bypass validation (`or "default"`)
- Skip logic that bypasses checks (`if not exists: return True`)
- Placeholder return values (`return {}`)
- Silent failures (`except: pass`)
- **Category fallback ranges** (`if prop missing: use category_range`)
- **Template fallbacks** (`if data missing: use template`)

**✅ EXCEPTION**: Mocks and fallbacks **ARE ALLOWED in test code** for proper testing infrastructure.

**🔍 TESTING REQUIREMENT**: Part of testing should include verifying ZERO presence of mocks and fallbacks in production code.

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
  - ALL AI text generation (captions, descriptions, etc.)
  - ALL property research and discovery
  - ALL completeness validation
  - ALL quality scoring and thresholds
  - ALL schema validation
- ✅ **Categories.yaml** - Single source of truth for category ranges
- ❌ **Frontmatter files** - Trivial export copies (NO API, NO validation)
  - Simple YAML-to-YAML field mapping
  - Should take seconds for 132 materials, not minutes
  - No complex operations during export
- ✅ **Data Flow**: Generate → Materials.yaml → Export to Frontmatter
- ✅ **Persistence**: All AI research saves to Materials.yaml immediately
- ❌ **Never read frontmatter** for data persistence (only for output verification)

See `docs/data/DATA_STORAGE_POLICY.md` for complete policy.

### 4. **Component Architecture**
Use ComponentGeneratorFactory pattern for all generators.

### 5. **Fail-Fast Design with Quality Gates**
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

### 6. **Content Instruction Policy** 🔥 **CRITICAL**
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

### 7. **Component Discovery Policy** 🔥 **NEW (Nov 16, 2025)**
**Component types MUST ONLY be defined in prompts/*.txt and config.yaml.**

- ✅ **prompts/*.txt files** - Define component types by filename
  - Create `prompts/caption.txt` to define 'caption' component
  - Create `prompts/subtitle.txt` to define 'subtitle' component
  - Each .txt file = one component type
- ✅ **config.yaml** - Define component word counts
  ```yaml
  component_lengths:
    caption: 25
    subtitle: 15
  ```
- ❌ **processing/*.py files** - NO hardcoded component types
  - ❌ `if component_type == 'caption':`
  - ❌ `SPEC_DEFINITIONS = {'caption': {...}}`
  - ❌ Hardcoded component lists
- ✅ **Dynamic Discovery**: Components discovered at runtime from prompts/
- ✅ **Generic Code**: Use `component_type` parameter, iterate `ComponentRegistry.list_types()`
- ✅ **ENFORCEMENT**: Automated tests verify zero hardcoded components

See `docs/architecture/COMPONENT_DISCOVERY.md` for complete policy.

### 8. **Template-Only Policy** 🔥 **NEW (Nov 18, 2025) - CRITICAL**
**ONLY prompt templates determine content and formatting. NO component-specific methods.**

- ✅ **prompts/components/*.txt** - ALL content instructions and formatting rules
  - Structure guidelines, style requirements, forbidden phrases
  - Format specifications, example outputs, voice/tone rules
  - COMPLETE content strategy for each component type
- ❌ **processing/*.py** - ZERO component-specific code
  - ❌ NO `if component_type == 'caption':` checks
  - ❌ NO component-specific methods (`_build_caption_prompt()`, `_extract_caption()`)
  - ❌ NO hardcoded content instructions in code
  - ❌ NO component-specific extraction logic in generators
- ✅ **Strategy Pattern**: Use `extraction_strategy` in config.yaml
  ```yaml
  component_lengths:
    caption:
      default: 50
      extraction_strategy: before_after  # Strategy-based extraction
    subtitle:
      default: 30
      extraction_strategy: raw  # Return text as-is
  ```
- ✅ **Generic Methods**: Use strategy dispatch, not component checks
  - ✅ `adapter.extract_content(text, component_type)` - delegates to strategy
  - ✅ `_load_prompt_template(component_type)` - loads generic template
  - ❌ `_extract_caption(text)` - component-specific method
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
1. ✅ Create prompts/components/new_component.txt (all instructions)
2. ✅ Add to config.yaml: component_lengths: { new_component: {default: 100, extraction_strategy: raw} }
```

See `docs/08-development/TEMPLATE_ONLY_POLICY.md` for complete policy.

### 9. **Prompt Purity Policy** 🔥 **NEW (Nov 18, 2025)**
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
  - ✅ `prompt = self._load_prompt_template('caption.txt')`
  - ✅ Technical parameters (temperature, penalties) in code
  - ✅ Data insertion (material names, properties) allowed
- ✅ **ENFORCEMENT**: Automated tests verify zero hardcoded prompts

See `docs/08-development/PROMPT_PURITY_POLICY.md` for complete policy.

### 10. **Generation Report Policy** 🔥 **NEW (Nov 18, 2025)**
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
**Compliance**: Mandatory for caption, subtitle, FAQ generation



## Code Standards
- Use strict typing with Optional[] for nullable parameters
- Implement comprehensive error handling with specific exception types
- No default values for critical dependencies (API clients, configuration files)
- Log all validation steps and failures clearly
- Keep code concise and avoid unnecessary complexity
- Never leave TODOs - provide complete solutions
- Never hardcode values - use configuration or parameters
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
- [ ] `components/[component]/docs/` or `components/[component]/README.md`
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
- **Component docs**: `components/[name]/docs/` or `docs/03-components/`
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

### Step 2: 🔍 Explore Architecture
- [ ] **Read relevant code** - Understand how it currently works
- [ ] **Check subdirectories** - Don't miss important context
- [ ] **Verify file existence** - Prevent "Content Not Found" errors
- [ ] **Read policy docs** - HARDCODED_VALUE_POLICY, CONTENT_INSTRUCTION_POLICY, etc.

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

### 🚨 CRITICAL: Fix Root Causes, Not Symptoms

**THE PROBLEM WITH TEMPORARY FIXES:**
If you create a "fix script" that patches frontmatter files directly, the fix will be **OVERWRITTEN** on the next `--deploy` because:
1. Frontmatter is **GENERATED FROM** Materials.yaml + Categories.yaml
2. The exporter code runs on every deployment
3. Patching output files is **TEMPORARY** - they get regenerated

**THE CORRECT APPROACH:**
1. ✅ **Fix the exporter code** (`components/frontmatter/core/trivial_exporter.py`) to ALWAYS generate correct structure
2. ✅ **Regenerate all frontmatter** with `--deploy` to apply the fix
3. ✅ **Verify the fix persists** by checking files after regeneration
4. ❌ **NEVER create one-off patch scripts** that modify frontmatter files directly

**EXAMPLE - Machine Settings Missing Min/Max:**
- ❌ WRONG: Create script to add min/max to existing frontmatter files
- ✅ RIGHT: Fix `_enrich_machine_settings()` in trivial_exporter.py, then redeploy
- WHY: Next deployment would overwrite the patched files with incomplete data

**RULE: If frontmatter has an issue, fix the GENERATOR, not the GENERATED files.**

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
- [ ] **If I fixed a generator: I've regenerated the output and verified persistence**
