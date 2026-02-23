# Development Documentation

Developer guides for contributing to and extending the Z-Beam Generator.

## Execution Environment Policy

- Always run project commands with `python3` from the repository root.
- Do not create or activate a virtual environment (`venv`/`virtualenv`) for standard development, generation, postprocess, export, or test workflows.
- Examples:
  - `python3 run.py --description "Steel"`
  - `python3 -m pytest tests/`

## Text Length Policy

- Length variation is multiplier-based and centralized in `generation/text_field_config.yaml` under `randomization_range`.
- Do not introduce new `min_length`/`max_length` bounds for generation targeting.
- `length_variation_range` in legacy config paths is compatibility-only and should not be used for new logic.

## Getting Started

- **[new_component_guide.md](new_component_guide.md)** - Guide for creating new components

## � Reference Documentation

- **[GENERATION_VS_DISPLAY_TERMINOLOGY.md](../09-reference/GENERATION_VS_DISPLAY_TERMINOLOGY.md)** - ✅ **NEW (Jan 7, 2026)**: Clarifies terminology
  - `component_type` (generation layer) vs `presentation` (display layer)
  - Explains removal of redundant `presentation_type` field
  - Quick reference table and common patterns
  - Essential for understanding generation vs export systems

## �🔥 Critical Policies (December 2025)

### Voice & Enforcement Architecture
- **[VOICE_ENFORCEMENT_CENTRALIZATION_DEC12_2025.md](VOICE_ENFORCEMENT_CENTRALIZATION_DEC12_2025.md)** - ✅ **NEW**: Complete architecture for centralized voice enforcement
  - Single source of truth in `_build_voice_instruction()` method
  - 60%+ voice distinctiveness achieved (4x improvement)
  - Automatic propagation to all domains via `{voice_instruction}` placeholder
  - Grade: A+ (100/100) - Production ready
  
- **[VOICE_INSTRUCTION_CENTRALIZATION_POLICY.md](VOICE_INSTRUCTION_CENTRALIZATION_POLICY.md)** - Policy document (Dec 6, 2025)
  - Mandatory: ALL voice instructions in `shared/voice/profiles/*.yaml` only
  - Grade F violation if voice instructions appear in domain prompts or code
  
- **[CLEAN_SEPARATION_OF_CONCERNS_DEC12_2025.md](CLEAN_SEPARATION_OF_CONCERNS_DEC12_2025.md)** - Three-layer architecture
  - Layer 1: Author Personas (voice definition)
  - Layer 2: Humanness Optimizer (structural variation)
  - Layer 3: Domain Prompts (content requirements)

## Testing

See: [Testing Documentation](../testing/) for comprehensive testing guides

## Code Standards

- Use strict typing with `Optional[]` for nullable parameters
- Implement comprehensive error handling with specific exception types
- No default values for critical dependencies
- Log all validation steps and failures clearly
- Keep code concise and avoid unnecessary complexity
- Never leave TODOs - provide complete solutions
- Never hardcode values - use configuration or parameters

## Architecture Patterns

- **Wrapper Pattern**: Use lightweight wrappers to integrate specialized generators
- **Factory Pattern**: ComponentGeneratorFactory for component discovery
- **Result Objects**: Return structured ComponentResult objects
- **Configuration Validation**: Validate all required files on startup
- **Fail-Fast Design**: Validate inputs immediately, throw specific exceptions

## Error Handling

- **ConfigurationError**: Missing or invalid configuration files
- **GenerationError**: Content generation failures
- **RetryableError**: Temporary failures (with retry logic)
- Never silently fail or use default values
- Fail immediately with specific exception types

## Component Development Workflow

1. Review [new_component_guide.md](new_component_guide.md)
2. Study existing components in `components/`
3. Follow the ComponentGeneratorFactory pattern
4. Write tests in `tests/test_[component]/`
5. Update documentation

## See Also

- [Component Documentation](../components/) - Component architecture
- [Architecture Documentation](../architecture/) - System architecture
- [Testing Documentation](../testing/) - Testing guidelines
- [GitHub Copilot Instructions](../../.github/copilot-instructions.md) - AI assistant guidelines
