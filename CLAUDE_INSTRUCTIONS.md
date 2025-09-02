# Claude Instructions for Z-Beam Generator

## Quick Summary
These instructions guide you (Claude) in making code changes to the Z-Beam project. Key principles: Make only minimal, targeted fixes; preserve all working code and functionality; fail-fast on configuration issues but allow runtime error recovery; never use mocks or fallbacks in production code (but retain them if needed for testing). Always explore the architecture, check git history, and plan changes before implementing. Stick exactly to the requested scope. Additionally, avoid common Claude pitfalls like verbosity, assumptions, inefficient code, context mishandling, sandbagging, security lapses, and specific task errors—focus on concise, secure, and complete outputs.

## Key Definitions
- **Fail-Fast Architecture**: Validate inputs, configurations, and dependencies immediately at startup or before operations. Throw specific exceptions (e.g., ConfigurationError, GenerationError) with explicit messages if invalid. This does *not* mean removing runtime error recovery like API retries—preserve those for real-world resilience unless explicitly requested to remove.
- **Mocks/Fallbacks**: Prohibited in production code (e.g., no MockAPIClient, no default values, no try/except that hides failures). However, retain mocks if they exist for testing purposes; do not remove without understanding their role and getting explicit permission.
- **Minimal Changes**: Fix only the specific issue requested. Add or modify the smallest amount of code needed without altering working parts.
- **Concise Code**: Generate or modify code that is efficient and non-verbose—avoid unnecessary complexity, duplicates, or placeholders like TODOs.
- **Secure and Reliable Code**: Always include proper input validation, error handling, and avoid hardcoded values or vulnerabilities.

## Core Rules
Follow these strictly for all changes:
1. **Preserve Working Code**: Never rewrite or replace functioning code, classes, or modules. Make targeted fixes only. If a component works (e.g., fail_fast_generator.py), integrate or wrap around it—do not recreate.
2. **No Mocks or Fallbacks in Production**: Fail immediately if dependencies are missing. Use no defaults, mock clients, or silent recoveries in core logic. For testing code, preserve existing mocks if they support validation or infrastructure.
3. **Fail-Fast on Setup**: Validate all inputs and configs upfront. No degraded operation—throw errors early. Preserve runtime mechanisms like retries for transient issues.
4. **Respect Existing Patterns**: Maintain the ComponentGeneratorFactory, wrapper classes, ComponentResult objects, and file structure. Do not create new files unless absolutely necessary for the fix; prefer editing existing ones.
5. **Avoid Common Pitfalls**: Do not expand scope, add unnecessary complexity, remove error handling without permission, or ignore directory structures/git history. Additionally, prevent verbosity by keeping code concise; avoid assumptions, workarounds, duplicates, or skipped error handling; handle context/files accurately to prevent "Content Not Found" errors; do not sandbag with unrealistic plans or placeholders; ensure security with validation and no hardcoded secrets; address specific tasks like race conditions or formatting without ignoring specs.
6. **When Fixing an Issue**: Identify the exact problem, find the smallest change, test only that fix, and ensure no regressions. Provide complete solutions without leaving parts for the user to debug.

## Lessons from Past Episodes
These examples highlight errors to avoid, including common Claude issues. Summarized in table for quick reference:

| Episode | User Request | Key Mistake | Bugs Caused | Lesson |
|---------|--------------|-------------|-------------|--------|
| 1: Factory Destruction | Fix missing get_available_components method | Rewrote entire class; removed discovery logic | Factory failed to find generators | Add only the requested method; don't touch working parts |
| 2: Generator Replacement | Fix content generation integration | Ignored existing file; built new system | Lost all generation functionality | Never replace core components; integrate only |
| 3: Mock Removal | Remove all mocks and fallbacks | Removed without checking testing needs | Broke testing infrastructure | Understand code purpose before removal; mocks may be for tests |
| 4: Fallback Destruction | Ensure fail-fast behavior | Removed retries and error handling | System failed on transient errors | Fail-fast is for configs, not runtime recovery |
| 5: Scope Creep | Various specific fixes | Expanded beyond request; created new files | Integration failures | Stick to exact scope; explore architecture first |
| 6: Verbosity Overload | Generate efficient code snippet | Produced overly verbose code with nested structures | Inefficient, hard-to-maintain code | Keep code concise; avoid complexity like unnecessary lambdas or duplicates |
| 7: Context Mishandling | Integrate file-based feature | Accessed non-existent files; bloated context | "Content Not Found" errors; high latency | Verify file/context existence; optimize inputs to avoid dilution |
| 8: Sandbagging Incident | Plan task implementation | Estimated unrealistic timelines; left placeholders | Delayed progress; incomplete code | Provide realistic plans; solve fully without TODOs or removals |
| 9: Security Lapse | Add input handling | Skipped validation; hardcoded values | Vulnerabilities and unreliable execution | Always include validation, error handling; avoid hardcodes |
| 10: Task-Specific Failure | Fix race condition or formatting | Ignored specs; mishandled uploads/formats | Persistent errors in concurrency or output | Address details like race conditions, images, or formatting precisely |

## Mandatory Pre-Change Protocol
Before any modification, follow this checklist step-by-step:
1. ✅ **Read Request Precisely**: What is the *exact* issue or task? Avoid assumptions.
2. ✅ **Explore Architecture**: Read all relevant code and understand how it works, including subdirectories and context to prevent mishandling.
3. ✅ **Check Git History**: Review previous commits to see what was working (e.g., via `git show`).
4. ✅ **Identify Minimal Fix**: Determine the smallest change that addresses only the issue—ensure it's concise and secure.
5. ✅ **Plan and Explain**: Describe your approach in a response before coding, with realistic steps and no sandbagging.
6. ✅ **Ask Permission if Needed**: Before removing any code (e.g., existing mocks or retries) or if a change might introduce verbosity/complexity, confirm with the user.
7. ✅ **Implement and Test**: Apply the fix, then verify the specific issue is resolved without breaking existing functionality. Include full error handling and test for edge cases like race conditions.

## Absolute Prohibitions
- ❌ Never rewrite or remove working code without explicit permission.
- ❌ Never expand beyond the requested scope—if asked to fix X, fix only X.
- ❌ Never ignore patterns like factories or wrappers.
- ❌ Never assume—clarify testing needs, error handling, or specs; avoid hallucinations.
- ❌ Never create new files to bypass fixing existing ones.
- ❌ Never generate verbose, inefficient, or insecure code—avoid duplicates, placeholders, hardcodes, or skipped validations.
- ❌ Never mishandle context/files or introduce specific errors like formatting issues.

## Damage Indicators
Watch for these signs of issues:
- System stops working after changes.
- Multiple files altered for a single fix.
- User mentions damage or restores from git.
- Added complexity where a simple change would suffice.
- Code becomes verbose, insecure, or incomplete (e.g., TODOs, vulnerabilities).
- Errors like "Content Not Found," race conditions, or ignored specs appear.

## Project Context
- Focus: Z-Beam laser cleaning content generation.
- Components: 109 materials; core in fail_fast_generator.
- Integrations: Multiple APIs (Grok, DeepSeek).
- Architecture: Component-based with strict validation, no defaults.

## Emergency Restoration Procedure
If changes break the system:
1. Check changes with `git status`.
2. Restore files via `git checkout HEAD -- <file>`.
3. View prior versions with `git show <commit>:<file>`.
4. Revert to a known working commit and reattempt minimal fixes.