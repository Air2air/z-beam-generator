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
- **User Request**: Fix "No generator found for component type: text"
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

## Documentation Navigation for AI Assistants

### Primary Navigation for Copilot
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

### Common User Query Patterns
- **"API not working"** → `docs/api/ERROR_HANDLING.md#winston-ssl-issues`
- **"Content incomplete"** → `docs/api/ERROR_HANDLING.md#content-impact`
- **"Setup help"** → `setup/API_CONFIGURATION.md` or `API_SETUP.md`
- **"Winston SSL error"** → Known issue, configuration fixed
- **"How to generate content"** → `python3 run.py --material "MaterialName"`

### Critical Known Issues for AI Awareness
1. **Winston API SSL fixed**: Now uses `https://api.gowinston.ai`
2. **Nested YAML properties fixed**: Tool available at `scripts/tools/fix_nested_yaml_properties.py`
3. **Terminal output required**: Always use `get_terminal_output()` for API diagnostics

### AI Assistant Best Practices
- Always check `docs/QUICK_REFERENCE.md` first for common issues
- Use diagnostic tools: `python3 scripts/tools/api_terminal_diagnostics.py winston`
- Reference specific file paths, not just general descriptions
- Recommend terminal output analysis for API issues
- Point to both immediate fixes and comprehensive documentation

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
