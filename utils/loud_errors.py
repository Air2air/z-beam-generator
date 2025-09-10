#!/usr/bin/env python3
"""
Loud Errors Module

Provides comprehensive error handling and reporting utilities.
"""

import sys
from typing import Optional


def component_failure(component_name: str, error_message: str, **kwargs) -> None:
    """
    Report a component failure with high visibility.

    Args:
        component_name: Name of the component that failed
        error_message: Description of the error
        **kwargs: Additional arguments (for compatibility)
    """
    print(f"\n💥 COMPONENT FAILURE: {component_name}", file=sys.stderr)
    print(f"❌ Error: {error_message}", file=sys.stderr)
    print("⚠️  Generation cannot continue", file=sys.stderr)


def api_failure(component_name: str, error_message: str, retry_count: Optional[int] = None, **kwargs) -> None:
    """
    Report an API-related failure with high visibility.

    Args:
        component_name: Name of the component that failed
        error_message: Description of the API error
        retry_count: Number of retries attempted (optional)
        **kwargs: Additional arguments (for compatibility)
    """
    print(f"\n🔌 API FAILURE: {component_name}", file=sys.stderr)
    print(f"❌ API Error: {error_message}", file=sys.stderr)
    if retry_count is not None:
        print(f"🔄 Retry attempts: {retry_count}", file=sys.stderr)
    print("⚠️  API operation failed", file=sys.stderr)


def configuration_failure(component_name: str, error_message: str, **kwargs) -> None:
    """
    Report a configuration-related failure with high visibility.

    Args:
        component_name: Name of the component that failed
        error_message: Description of the configuration error
        **kwargs: Additional arguments (for compatibility)
    """
    print(f"\n⚙️ CONFIGURATION FAILURE: {component_name}", file=sys.stderr)
    print(f"❌ Config Error: {error_message}", file=sys.stderr)
    print("⚠️  Configuration issue detected", file=sys.stderr)


def dependency_failure(component_name: str, error_message: str, **kwargs) -> None:
    """
    Report a dependency-related failure with high visibility.

    Args:
        component_name: Name of the component that failed
        error_message: Description of the dependency error
        **kwargs: Additional arguments (for compatibility)
    """
    print(f"\n🔗 DEPENDENCY FAILURE: {component_name}", file=sys.stderr)
    print(f"❌ Dependency Error: {error_message}", file=sys.stderr)
    print("⚠️  Required dependency not available", file=sys.stderr)


def validation_failure(component_name: str, error_message: str, field: Optional[str] = None, **kwargs) -> None:
    """
    Report a validation-related failure with high visibility.

    Args:
        component_name: Name of the component that failed
        error_message: Description of the validation error
        field: Name of the field that failed validation (optional)
        **kwargs: Additional arguments (for compatibility)
    """
    print(f"\n✅ VALIDATION FAILURE: {component_name}", file=sys.stderr)
    print(f"❌ Validation Error: {error_message}", file=sys.stderr)
    if field:
        print(f"📋 Field: {field}", file=sys.stderr)
    print("⚠️  Data validation failed", file=sys.stderr)


def network_failure(component_name: str, error_message: str, **kwargs) -> None:
    """
    Report a network-related failure with high visibility.

    Args:
        component_name: Name of the component that failed
        error_message: Description of the network error
        **kwargs: Additional arguments (for compatibility)
    """
    print(f"\n🌐 NETWORK FAILURE: {component_name}", file=sys.stderr)
    print(f"❌ Network Error: {error_message}", file=sys.stderr)
    print("⚠️  Network connectivity issue detected", file=sys.stderr)


def critical_error(error_message: str, **kwargs) -> None:
    """
    Report a critical error that requires immediate attention.

    Args:
        error_message: Description of the critical error
        **kwargs: Additional arguments (for compatibility)
    """
    print(f"\n💀 CRITICAL ERROR", file=sys.stderr)
    print(f"❌ Fatal Error: {error_message}", file=sys.stderr)
    print("⚠️  System cannot continue", file=sys.stderr)