#!/usr/bin/env python3
"""
Loud Error Messages Utility

Provides clear, red, loud terminal messages for any failed process.
Uses ANSI color codes and prominent formatting to make errors highly visible.
"""

import sys
from typing import Optional


# ANSI color codes
class Colors:
    """ANSI color codes for terminal output"""

    RED = "\033[91m"
    BRIGHT_RED = "\033[91;1m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"
    BG_RED = "\033[41m"
    BG_WHITE = "\033[107m"


class LoudError:
    """Utility class for creating loud, visible error messages"""

    @staticmethod
    def critical_error(
        message: str, details: Optional[str] = None, context: Optional[str] = None
    ) -> None:
        """Display a critical error with maximum visibility"""
        print("\n" + "=" * 80, file=sys.stderr)
        print(
            f"{Colors.BG_RED}{Colors.WHITE}{Colors.BOLD}🚨 CRITICAL FAILURE 🚨{Colors.RESET}",
            file=sys.stderr,
        )
        print("=" * 80, file=sys.stderr)
        print(
            f"{Colors.BRIGHT_RED}{Colors.BOLD}ERROR: {message}{Colors.RESET}",
            file=sys.stderr,
        )

        if details:
            print(f"{Colors.RED}DETAILS: {details}{Colors.RESET}", file=sys.stderr)

        if context:
            print(f"{Colors.RED}CONTEXT: {context}{Colors.RESET}", file=sys.stderr)

        print("=" * 80, file=sys.stderr)
        print(
            f"{Colors.BG_RED}{Colors.WHITE}{Colors.BOLD}🔥 SYSTEM FAILURE - IMMEDIATE ATTENTION REQUIRED 🔥{Colors.RESET}",
            file=sys.stderr,
        )
        print("=" * 80, file=sys.stderr)

    @staticmethod
    def component_failure(
        component_name: str, error: str, material: Optional[str] = None
    ) -> None:
        """Display a component failure with high visibility"""
        print(
            f"\n{Colors.BRIGHT_RED}{Colors.BOLD}💥 COMPONENT FAILURE 💥{Colors.RESET}",
            file=sys.stderr,
        )
        print(
            f"{Colors.RED}{Colors.BOLD}❌ {component_name.upper()} FAILED{Colors.RESET}",
            file=sys.stderr,
        )

        if material:
            print(f"{Colors.RED}MATERIAL: {material}{Colors.RESET}", file=sys.stderr)

        print(f"{Colors.RED}ERROR: {error}{Colors.RESET}", file=sys.stderr)
        print(
            f"{Colors.BRIGHT_RED}{Colors.BOLD}⚠️  GENERATION CANNOT CONTINUE ⚠️{Colors.RESET}",
            file=sys.stderr,
        )

    @staticmethod
    def api_failure(
        service_name: str, error: str, retry_count: Optional[int] = None
    ) -> None:
        """Display an API failure with high visibility"""
        print(
            f"\n{Colors.BRIGHT_RED}{Colors.BOLD}🌐 API FAILURE 🌐{Colors.RESET}",
            file=sys.stderr,
        )
        print(
            f"{Colors.RED}{Colors.BOLD}❌ {service_name.upper()} API ERROR{Colors.RESET}",
            file=sys.stderr,
        )

        if retry_count is not None:
            print(f"{Colors.RED}RETRIES: {retry_count}{Colors.RESET}", file=sys.stderr)

        print(f"{Colors.RED}ERROR: {error}{Colors.RESET}", file=sys.stderr)
        print(
            f"{Colors.BRIGHT_RED}{Colors.BOLD}🚫 EXTERNAL SERVICE UNAVAILABLE 🚫{Colors.RESET}",
            file=sys.stderr,
        )

    @staticmethod
    def validation_failure(
        validation_type: str, details: str, field: Optional[str] = None
    ) -> None:
        """Display a validation failure with high visibility"""
        print(
            f"\n{Colors.BRIGHT_RED}{Colors.BOLD}🔍 VALIDATION FAILURE 🔍{Colors.RESET}",
            file=sys.stderr,
        )
        print(
            f"{Colors.RED}{Colors.BOLD}❌ {validation_type.upper()} VALIDATION FAILED{Colors.RESET}",
            file=sys.stderr,
        )

        if field:
            print(f"{Colors.RED}FIELD: {field}{Colors.RESET}", file=sys.stderr)

        print(f"{Colors.RED}DETAILS: {details}{Colors.RESET}", file=sys.stderr)
        print(
            f"{Colors.BRIGHT_RED}{Colors.BOLD}🛑 CANNOT PROCEED WITH INVALID DATA 🛑{Colors.RESET}",
            file=sys.stderr,
        )

    @staticmethod
    def dependency_failure(
        dependency_name: str, error: str, impact: Optional[str] = None
    ) -> None:
        """Display a dependency failure with high visibility"""
        print(
            f"\n{Colors.BRIGHT_RED}{Colors.BOLD}🔗 DEPENDENCY FAILURE 🔗{Colors.RESET}",
            file=sys.stderr,
        )
        print(
            f"{Colors.RED}{Colors.BOLD}❌ {dependency_name.upper()} UNAVAILABLE{Colors.RESET}",
            file=sys.stderr,
        )
        print(f"{Colors.RED}ERROR: {error}{Colors.RESET}", file=sys.stderr)

        if impact:
            print(f"{Colors.RED}IMPACT: {impact}{Colors.RESET}", file=sys.stderr)

        print(
            f"{Colors.BRIGHT_RED}{Colors.BOLD}⛔ CRITICAL DEPENDENCY MISSING ⛔{Colors.RESET}",
            file=sys.stderr,
        )

    @staticmethod
    def configuration_failure(
        config_type: str, error: str, suggestion: Optional[str] = None
    ) -> None:
        """Display a configuration failure with high visibility"""
        print(
            f"\n{Colors.BRIGHT_RED}{Colors.BOLD}⚙️ CONFIGURATION FAILURE ⚙️{Colors.RESET}",
            file=sys.stderr,
        )
        print(
            f"{Colors.RED}{Colors.BOLD}❌ {config_type.upper()} CONFIGURATION ERROR{Colors.RESET}",
            file=sys.stderr,
        )
        print(f"{Colors.RED}ERROR: {error}{Colors.RESET}", file=sys.stderr)

        if suggestion:
            print(
                f"{Colors.RED}SUGGESTION: {suggestion}{Colors.RESET}", file=sys.stderr
            )

        print(
            f"{Colors.BRIGHT_RED}{Colors.BOLD}🔧 CONFIGURATION MUST BE FIXED 🔧{Colors.RESET}",
            file=sys.stderr,
        )

    @staticmethod
    def file_system_failure(operation: str, path: str, error: str) -> None:
        """Display a file system failure with high visibility"""
        print(
            f"\n{Colors.BRIGHT_RED}{Colors.BOLD}📁 FILE SYSTEM FAILURE 📁{Colors.RESET}",
            file=sys.stderr,
        )
        print(
            f"{Colors.RED}{Colors.BOLD}❌ {operation.upper()} FAILED{Colors.RESET}",
            file=sys.stderr,
        )
        print(f"{Colors.RED}PATH: {path}{Colors.RESET}", file=sys.stderr)
        print(f"{Colors.RED}ERROR: {error}{Colors.RESET}", file=sys.stderr)
        print(
            f"{Colors.BRIGHT_RED}{Colors.BOLD}💾 FILE SYSTEM ERROR 💾{Colors.RESET}",
            file=sys.stderr,
        )

    @staticmethod
    def network_failure(operation: str, target: str, error: str) -> None:
        """Display a network failure with high visibility"""
        print(
            f"\n{Colors.BRIGHT_RED}{Colors.BOLD}🌐 NETWORK FAILURE 🌐{Colors.RESET}",
            file=sys.stderr,
        )
        print(
            f"{Colors.RED}{Colors.BOLD}❌ {operation.upper()} FAILED{Colors.RESET}",
            file=sys.stderr,
        )
        print(f"{Colors.RED}TARGET: {target}{Colors.RESET}", file=sys.stderr)
        print(f"{Colors.RED}ERROR: {error}{Colors.RESET}", file=sys.stderr)
        print(
            f"{Colors.BRIGHT_RED}{Colors.BOLD}📡 NETWORK CONNECTIVITY ISSUE 📡{Colors.RESET}",
            file=sys.stderr,
        )

    @staticmethod
    def loud_warning(message: str, details: Optional[str] = None) -> None:
        """Display a loud warning (less critical than error but still prominent)"""
        print(
            f"\n{Colors.BRIGHT_RED}{Colors.BOLD}⚠️  LOUD WARNING ⚠️{Colors.RESET}",
            file=sys.stderr,
        )
        print(
            f"{Colors.RED}{Colors.BOLD}WARNING: {message}{Colors.RESET}",
            file=sys.stderr,
        )

        if details:
            print(f"{Colors.RED}DETAILS: {details}{Colors.RESET}", file=sys.stderr)

    @staticmethod
    def success_highlight(message: str) -> None:
        """Display a success message with highlighting"""
        print(
            f"{Colors.BG_RED}{Colors.WHITE}{Colors.BOLD}✅ {message.upper()} ✅{Colors.RESET}"
        )

    @staticmethod
    def info_highlight(message: str) -> None:
        """Display an info message with highlighting"""
        print(f"{Colors.RED}{Colors.BOLD}ℹ️  {message}{Colors.RESET}")


# Convenience functions for quick error reporting
def critical_error(message: str, **kwargs) -> None:
    """Quick critical error function"""
    LoudError.critical_error(message, **kwargs)


def component_failure(component_name: str, error: str, **kwargs) -> None:
    """Quick component failure function"""
    LoudError.component_failure(component_name, error, **kwargs)


def api_failure(service_name: str, error: str, **kwargs) -> None:
    """Quick API failure function"""
    LoudError.api_failure(service_name, error, **kwargs)


def validation_failure(validation_type: str, details: str, **kwargs) -> None:
    """Quick validation failure function"""
    LoudError.validation_failure(validation_type, details, **kwargs)


def dependency_failure(dependency_name: str, error: str, **kwargs) -> None:
    """Quick dependency failure function"""
    LoudError.dependency_failure(dependency_name, error, **kwargs)


def configuration_failure(config_type: str, error: str, **kwargs) -> None:
    """Quick configuration failure function"""
    LoudError.configuration_failure(config_type, error, **kwargs)


def file_system_failure(operation: str, path: str, error: str) -> None:
    """Quick file system failure function"""
    LoudError.file_system_failure(operation, path, error)


def network_failure(operation: str, target: str, error: str) -> None:
    """Quick network failure function"""
    LoudError.network_failure(operation, target, error)


def loud_warning(message: str, **kwargs) -> None:
    """Quick loud warning function"""
    LoudError.loud_warning(message, **kwargs)


def success_highlight(message: str) -> None:
    """Quick success highlight function"""
    LoudError.success_highlight(message)


def info_highlight(message: str) -> None:
    """Quick info highlight function"""
    LoudError.info_highlight(message)


# Test function to demonstrate the loud error messages
if __name__ == "__main__":
    print("🧪 Testing Loud Error Messages")
    print("=" * 50)

    # Test critical error
    critical_error(
        "System initialization failed",
        details="Database connection timeout",
        context="Main application startup",
    )

    # Test component failure
    component_failure(
        "text_generator", "Author information missing", material="Steel material"
    )

    # Test API failure
    api_failure("DeepSeek", "Connection timeout after 30 seconds", retry_count=3)

    # Test validation failure
    validation_failure(
        "author_data", "Required field 'name' is missing", field="author.name"
    )

    # Test dependency failure
    dependency_failure(
        "API Client", "Module not found", impact="Content generation cannot proceed"
    )

    # Test configuration failure
    configuration_failure(
        "API Keys",
        "DEEPSEEK_API_KEY not found in environment",
        suggestion="Set DEEPSEEK_API_KEY environment variable",
    )

    # Test file system failure
    file_system_failure("read", "/path/to/config.yaml", "Permission denied")

    # Test network failure
    network_failure("connect", "api.deepseek.com", "DNS resolution failed")

    # Test warning
    loud_warning(
        "High memory usage detected", details="Consider increasing system memory"
    )

    # Test success
    success_highlight("All systems operational")

    # Test info
    info_highlight("Processing complete")
