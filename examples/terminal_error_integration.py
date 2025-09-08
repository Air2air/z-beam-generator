#!/usr/bin/env python3
"""
Example: Integrating Terminal Error Handler with Existing Code

This example shows how to integrate the TerminalErrorHandler with existing
error handling patterns in the Z-Beam generator system.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.loud_errors import LoudError
from utils.terminal_error_handler import handle_terminal_error


def example_component_with_error_handling():
    """
    Example of how to integrate error handling in a component
    """
    try:
        # Simulate some component work that might fail
        result = some_risky_operation()

    except Exception as e:
        # Capture the error and process it through the handler
        error_output = f"Component Error: {str(e)}"
        analysis = handle_terminal_error(error_output)

        # Also show the loud error (existing behavior)
        LoudError.component_failure(
            "example_component", "Component operation failed", details=str(e)
        )

        # Return appropriate error response
        return {"success": False, "error": str(e), "analysis": analysis}

    return {"success": True, "result": result}


def some_risky_operation():
    """
    Simulate an operation that might fail
    """
    # This could be any operation that might raise an exception
    raise ImportError("No module named 'nonexistent_module'")


def example_api_call_with_error_handling():
    """
    Example of API call with comprehensive error handling
    """
    try:
        # Simulate API call
        response = make_api_call()

    except Exception as e:
        error_output = f"API Error: {str(e)}"
        analysis = handle_terminal_error(error_output)

        LoudError.api_failure("example_api", "API call failed", details=str(e))

        return {"success": False, "error": str(e), "analysis": analysis}

    return {"success": True, "response": response}


def make_api_call():
    """
    Simulate an API call that fails
    """
    raise ConnectionError("Network is unreachable")


def example_file_operation_with_error_handling():
    """
    Example of file operation with error handling
    """
    try:
        # Simulate file operation
        content = read_config_file("nonexistent_config.yaml")

    except Exception as e:
        error_output = f"File Error: {str(e)}"
        analysis = handle_terminal_error(error_output)

        LoudError.file_system_failure(
            "config_reader", "Failed to read configuration file", details=str(e)
        )

        return {"success": False, "error": str(e), "analysis": analysis}

    return {"success": True, "content": content}


def read_config_file(filename):
    """
    Simulate reading a config file that doesn't exist
    """
    raise FileNotFoundError(f"No such file or directory: '{filename}'")


def demonstrate_error_workflow():
    """
    Demonstrate the complete error handling workflow
    """
    print("🚀 Demonstrating Terminal Error Handler Integration")
    print("=" * 60)

    # Example 1: Component error
    print("\n📦 Example 1: Component Error")
    result1 = example_component_with_error_handling()
    print(f"Result: {result1}")

    # Example 2: API error
    print("\n🌐 Example 2: API Error")
    result2 = example_api_call_with_error_handling()
    print(f"Result: {result2}")

    # Example 3: File error
    print("\n📄 Example 3: File Error")
    result3 = example_file_operation_with_error_handling()
    print(f"Result: {result3}")

    print("\n" + "=" * 60)
    print("✅ Error handling demonstration complete!")
    print("\n💡 Key Benefits:")
    print("  • Automatic error pattern recognition")
    print("  • Systematic fixing, documentation, and testing")
    print("  • Prevention of error reoccurrence")
    print("  • Integration with existing loud error system")
    print("  • Comprehensive error analysis and reporting")


if __name__ == "__main__":
    demonstrate_error_workflow()
