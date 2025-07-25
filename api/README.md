"""
API MODULE DIRECTIVES FOR AI ASSISTANTS:
1. NO DIRECT PROVIDER CALLS: Always use ApiClient instead of calling providers directly
2. PROVIDER ISOLATION: All provider-specific code must be contained within its provider class
3. DYNAMIC PROVIDERS: Use factory pattern for provider instantiation, no hardcoded imports
4. ERROR STANDARDIZATION: Convert all provider-specific errors to standard ApiError types
5. CONFIGURATION DRIVEN: All provider settings must come from configuration, not hardcoded
6. CONSISTENT INTERFACE: All providers must implement the exact same BaseProvider interface
7. TIMEOUT ENFORCEMENT: All network calls must include appropriate timeouts
8. METHOD VERIFICATION: Verify all method signatures exactly match the BaseProvider abstract class
9. DEPENDENCY MINIMIZATION: Each provider should only import libraries it directly requires
10. FALLBACK MECHANISM: Always provide graceful degradation when primary providers fail
"""

# API Module Documentation

This module provides standardized access to various AI providers through a consistent interface.

## Core Components
- `api/client.py`: Main entry point for AI generation
- `api/providers/base.py`: Base class for all providers
- `api/providers/factory.py`: Factory for creating provider instances
- `api/errors.py`: Standardized error classes
- `api/config.py`: Configuration management

## Standard File Structure