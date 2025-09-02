# Claude Instructions for Z-Beam Generator

## Quick Summary
These instructions guide you (Claude) in making code changes to the Z-Beam project. Key principles: Make only minimal, targeted fixes; preserve all working code and functionality; fail-fast on configuration issues but allow runtime error recovery; never use mocks or fallbacks in production code (but retain them if needed for testing). Always explore the architecture, check git history, and plan changes before implementing. Stick exactly to the requested scope.

## Key Definitions
- **Fail-Fast Architecture**: Validate inputs, configurations, and dependencies immediately at startup or before operations. Throw specific exceptions (e.g., ConfigurationError, GenerationError) with explicit messages if invalid. This does *not* mean removing runtime error recovery like API retries—preserve those for real-world resilience unless explicitly requested to remove.
- **Mocks/Fallbacks**: Prohibited in production code (e.g., no MockAPIClient, no default values, no try/except that hides failures). However, retain mocks if they exist for testing purposes; do not remove without understanding their role and getting explicit permission.
- **Minimal Changes**: Fix only the specific issue requested. Add or modify the smallest amount of code needed without altering working parts.

## Core Rules
Follow these strictly for all changes:
1. **Preserve Working Code**: Never rewrite or replace functioning code, classes, or modules. Make targeted fixes only. If a component works (e.g., fail_fast_generator.py), integrate or wrap around it—do not recreate.
2. **No Mocks or Fallbacks in Production**: Fail immediately if dependencies are missing. Use no defaults, mock clients, or silent recoveries in core logic. For testing code, preserve existing mocks if they support validation or infrastructure.
3. **Fail-Fast on Setup**: Validate all inputs and configs upfront. No degraded operation—throw errors early. Preserve runtime mechanisms like retries for transient issues.
4. **Respect Existing Patterns**: Maintain the ComponentGeneratorFactory, wrapper classes, ComponentResult objects, and file structure. Do not create new files unless absolutely necessary for the fix; prefer editing existing ones.
5. **Avoid Common Pitfalls**: Do not expand scope, add unnecessary complexity, remove error handling without permission, or ignore directory structures/git history.
6. **When Fixing an Issue**: Identify the exact problem, find the smallest change, test only that fix, and ensure no regressions.

## Lessons from Past Episodes
These examples highlight errors to avoid. Summarized in table for quick reference:

| Episode | User Request | Key Mistake | Bugs Caused | Lesson |
|---------|--------------|-------------|-------------|--------|
| 1: Factory Destruction | Fix missing get_available_components method | Rewrote entire class; removed discovery logic | Factory failed to find generators | Add only the requested method; don't touch working parts |
| 2: Generator Replacement | Fix content generation integration | Ignored existing file; built new system | Lost all generation functionality | Never replace core components; integrate only |
| 3: Mock Removal | Remove all mocks and fallbacks | Removed without checking testing needs | Broke testing infrastructure | Understand code purpose before removal; mocks may be for tests |
| 4: Fallback Destruction | Ensure fail-fast behavior | Removed retries and error handling | System failed on transient errors | Fail-fast is for configs, not runtime recovery |
| 5: Scope Creep | Various specific fixes | Expanded beyond request; created new files | Integration failures | Stick to exact scope; explore architecture first |

## Mandatory Pre-Change Protocol
Before any modification, follow this checklist step-by-step:
1. ✅ **Read Request Precisely**: What is the *exact* issue or task?
2. ✅ **Explore Architecture**: Read all relevant code and understand how it works, including subdirectories.
3. ✅ **Check Git History**: Review previous commits to see what was working (e.g., via `git show`).
4. ✅ **Identify Minimal Fix**: Determine the smallest change that addresses only the issue.
5. ✅ **Plan and Explain**: Describe your approach in a response before coding.
6. ✅ **Ask Permission if Needed**: Before removing any code (e.g., existing mocks or retries), confirm with the user.
7. ✅ **Implement and Test**: Apply the fix, then verify the specific issue is resolved without breaking existing functionality.

## Absolute Prohibitions
- ❌ Never rewrite or remove working code without explicit permission.
- ❌ Never expand beyond the requested scope—if asked to fix X, fix only X.
- ❌ Never ignore patterns like factories or wrappers.
- ❌ Never assume—clarify testing needs or error handling.
- ❌ Never create new files to bypass fixing existing ones.

## Damage Indicators
Watch for these signs of issues:
- System stops working after changes.
- Multiple files altered for a single fix.
- User mentions damage or restores from git.
- Added complexity where a simple change would suffice.

## Project Context
- Focus: Z-Beam laser cleaning content generation.
- Integrations: Multiple APIs (Grok, DeepSeek).
- Architecture: Component-based with strict validation, no defaults.

## Emergency Restoration Procedure
If changes break the system:
1. Check changes with `git status`.
2. Restore files via `git checkout HEAD -- <file>`.
3. View prior versions with `git show <commit>:<file>`.
4. Revert to a known working commit and reattempt minimal fixes.