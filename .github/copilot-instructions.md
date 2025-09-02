# GitHub Copilot Instructions for Z-Beam Generator

## Project Overview
This is a laser cleaning content generation system with strict fail-fast architecture.

## Core Principles
1. **No Mocks or Fallbacks**: System must fail immediately if dependencies are missing
2. **Explicit Dependencies**: All required components must be explicitly provided
3. **Component Architecture**: Use ComponentGeneratorFactory pattern for all generators
4. **Fail-Fast Design**: Validate configurations and inputs immediately

## Code Standards
- Use strict typing with Optional[] for nullable parameters
- Implement comprehensive error handling with specific exception types
- No default values for critical dependencies (API clients, configuration files)
- Log all validation steps and failures clearly

## Architecture Patterns
- **Wrapper Pattern**: Use lightweight wrappers to integrate specialized generators
- **Factory Pattern**: ComponentGeneratorFactory for component discovery and creation
- **Result Objects**: Return structured ComponentResult objects with success/error states
- **Configuration Validation**: Validate all required files and settings on startup

## Error Handling
- ConfigurationError: Missing or invalid configuration files
- GenerationError: Content generation failures
- RetryableError: Temporary failures that could be retried (but avoid retries)
- Never silently fail or use default values

## Testing Approach
- No mock APIs in production code
- No fallbacks or hardcode ever.
- Fail fast on missing test dependencies
- Use real API clients with proper error handling
- Validate all component integrations
- Ensure solid retention of API keys

## Critical Lessons from Claude's Destructive Episodes

### Episode 1: ComponentGeneratorFactory Destruction
- **User Request**: Fix "No generator found for component type: content" 
- **Claude's Damage**: Completely rewrote working ComponentGeneratorFactory instead of adding one missing method
- **Code Destroyed**: Factory pattern implementation, component discovery logic
- **Bug Result**: System couldn't find any generators
- **Lesson**: Add ONLY what's requested - one method means one method

### Episode 2: fail_fast_generator Replacement Attempt  
- **User Request**: Fix content generation integration
- **Claude's Damage**: Ignored existing working fail_fast_generator.py, tried to create new system
- **Code Destroyed**: Quality scoring, established patterns, working content generation
- **Bug Result**: Complete loss of content generation functionality
- **Lesson**: NEVER replace working core components - wrap or integrate only

### Episode 3: MockAPIClient Blind Removal
- **User Request**: "Remove all mocks and fallbacks"
- **Claude's Damage**: Removed MockAPIClient without understanding testing requirements
- **Code Destroyed**: Testing infrastructure, validation capabilities
- **Bug Result**: System became untestable
- **Lesson**: Understand WHY code exists before removing it

### Episode 4: Content Scorer Fallback Destruction
- **User Request**: Ensure fail-fast behavior
- **Claude's Damage**: Removed working retry logic and error recovery mechanisms
- **Code Destroyed**: content_scorer fallback, API retry logic
- **Bug Result**: System too brittle for real-world transient errors
- **Lesson**: Fail-fast = validate config, not remove all error recovery

## Mandatory Rules from Damage Analysis
1. **NEVER rewrite working files** - fix specific issues only
2. **NEVER remove code without explicit permission** - understand purpose first  
3. **NEVER assume scope** - "fix X" means fix X, not rewrite everything
4. **NEVER ignore existing architecture** - explore completely before changing
5. **NEVER remove testing infrastructure** - MockAPIClient may be needed
6. **NEVER eliminate error recovery** - fail-fast ≠ no retry logic
7. **ALWAYS ask before major changes** - get permission for rewrites

When suggesting code changes:
1. Maintain fail-fast behavior
2. Preserve existing working functionality  
3. Use minimal, targeted changes
4. Follow established patterns and conventions
5. Include comprehensive error handling
6. Focus on reducing bloat
7. Prioritize changing existing components, not creating new ones
8. **ASK PERMISSION before removing any existing code**
