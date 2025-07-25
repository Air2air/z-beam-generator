# API Module Directives

## Core Principles
1. PROVIDER ABSTRACTION: All AI provider implementations must inherit from BaseProvider
2. NO DIRECT IMPORTS: Always use the ProviderFactory to obtain provider instances
3. CONSISTENT INTERFACES: All providers must implement the same interface methods
4. ERROR HANDLING: All providers must handle their own errors and provide meaningful messages
5. CONFIGURATION CONSISTENCY: Provider configuration must follow the standard structure
6. MINIMAL DEPENDENCIES: Each provider should only import what it needs
7. PERFORMANCE FOCUS: Avoid unnecessary computation or network calls

## Anti-Patterns to Avoid
1. PROVIDER BLOAT: Don't add unnecessary methods to providers that aren't used by components
2. METHOD NAME MISMATCHES: All providers must use the exact method names defined in BaseProvider
3. HARDCODED CREDENTIALS: Never include API keys directly in provider code
4. EXCESSIVE LOGGING: Log only essential information, not full request/response contents
5. MISSING TIMEOUTS: All network calls must include appropriate timeouts
6. DIRECT API CALLS: Always use official client libraries when available

## Standard Method Names
- `generate(prompt, options)`: Generate text from a prompt
- `get_model(options)`: Get model name from options or context
- `get_default_model()`: Get default model for this provider
- `validate_options(options)`: Validate options for this provider
- `check_availability()`: Check if provider is available (API keys, etc.)

## Configuration Structure
```yaml
providers:
  provider_name:
    enabled: true
    model: "default_model"
    api_key: "${ENV_VAR_NAME}"
    temperature: 0.7
    max_tokens: 1000
    timeout: 60