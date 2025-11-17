# Development Documentation

Developer guides for contributing to and extending the Z-Beam Generator.

## Getting Started

- **[new_component_guide.md](new_component_guide.md)** - Guide for creating new components

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
