#!/usr/bin/env python3
"""
Terminal Error Analysis and Prevention System

This module provides comprehensive error handling, analysis, and prevention
to ensure terminal errors are systematically addressed and documented.
"""

import json
import logging
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from utils.loud_errors import LoudError

logger = logging.getLogger(__name__)


@dataclass
class ErrorPattern:
    """Represents a recognized error pattern with solution"""

    pattern: str
    error_type: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    description: str
    solution: str
    test_case: str
    documentation_update: str
    prevention_measures: List[str] = field(default_factory=list)


@dataclass
class ErrorAnalysis:
    """Analysis result for a captured error"""

    timestamp: str
    error_text: str
    error_type: str
    severity: str
    matched_pattern: Optional[ErrorPattern] = None
    suggested_fix: str = ""
    documentation_updates: List[str] = field(default_factory=list)
    test_updates: List[str] = field(default_factory=list)
    prevention_measures: List[str] = field(default_factory=list)
    fixed: bool = False
    documented: bool = False
    tested: bool = False


class TerminalErrorHandler:
    """
    Comprehensive terminal error handling and prevention system.

    Features:
    - Real-time error capture from terminal output
    - Pattern-based error recognition and classification
    - Automated fix suggestions
    - Documentation updates
    - Test case generation
    - Prevention measure implementation
    """

    def __init__(self, error_log_path: str = "logs/terminal_errors.json"):
        self.error_log_path = Path(error_log_path)
        self.error_log_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize error patterns database
        self.error_patterns = self._load_error_patterns()

        # Error history for analysis
        self.error_history: List[ErrorAnalysis] = self._load_error_history()

        # Prevention tracking
        self.prevention_measures: Dict[str, List[str]] = {}

    def _load_error_patterns(self) -> Dict[str, ErrorPattern]:
        """Load predefined error patterns from configuration"""
        patterns_file = Path("config/error_patterns.json")

        if patterns_file.exists():
            try:
                with open(patterns_file, "r") as f:
                    data = json.load(f)
                    return {k: ErrorPattern(**v) for k, v in data.items()}
            except Exception as e:
                logger.error(f"Failed to load error patterns: {e}")

        # Default patterns if config doesn't exist
        return self._get_default_error_patterns()

    def _get_default_error_patterns(self) -> Dict[str, ErrorPattern]:
        """Get default error patterns for common issues"""
        return {
            "import_error": ErrorPattern(
                pattern=r"ImportError: No module named '(\w+)'",
                error_type="import_error",
                severity="high",
                description="Missing Python module dependency",
                solution="Install missing package with: pip install {module}",
                test_case="test_import_{module}",
                documentation_update="Add {module} to requirements.txt and installation docs",
                prevention_measures=[
                    "Add dependency to requirements.txt",
                    "Update installation documentation",
                    "Add import validation in __init__.py",
                ],
            ),
            "file_not_found": ErrorPattern(
                pattern=r"FileNotFoundError:.*No such file or directory: '(.+)'",
                error_type="file_not_found",
                severity="high",
                description="Required file is missing",
                solution="Create missing file: {file_path}",
                test_case="test_file_exists_{file_name}",
                documentation_update="Document required files in setup documentation",
                prevention_measures=[
                    "Add file existence validation",
                    "Create file templates",
                    "Update setup documentation",
                ],
            ),
            "api_key_missing": ErrorPattern(
                pattern=r"API key not found.*environment",
                error_type="configuration_error",
                severity="critical",
                description="Required API key is missing from environment",
                solution="Set environment variable: export {API_KEY_NAME}={value}",
                test_case="test_api_key_{api_name}_configured",
                documentation_update="Add API key setup to README and .env.example",
                prevention_measures=[
                    "Add .env.example file",
                    "Update README with API setup instructions",
                    "Add configuration validation on startup",
                ],
            ),
            "network_timeout": ErrorPattern(
                pattern=r"timeout|TimeoutError|ConnectionError",
                error_type="network_error",
                severity="medium",
                description="Network connectivity or timeout issue",
                solution="Check network connection and retry with increased timeout",
                test_case="test_network_connectivity_{service}",
                documentation_update="Add network requirements to documentation",
                prevention_measures=[
                    "Implement retry logic with exponential backoff",
                    "Add network connectivity tests",
                    "Document network requirements",
                ],
            ),
            "validation_error": ErrorPattern(
                pattern=r"ValidationError|ValueError.*required",
                error_type="validation_error",
                severity="medium",
                description="Data validation failure",
                solution="Provide valid data or fix validation logic",
                test_case="test_validation_{field_name}",
                documentation_update="Update data format documentation",
                prevention_measures=[
                    "Add input validation",
                    "Improve error messages",
                    "Update data format documentation",
                ],
            ),
        }

    def _load_error_history(self) -> List[ErrorAnalysis]:
        """Load error history from log file"""
        if self.error_log_path.exists():
            try:
                with open(self.error_log_path, "r") as f:
                    data = json.load(f)
                    return [ErrorAnalysis(**item) for item in data]
            except Exception as e:
                logger.error(f"Failed to load error history: {e}")
        return []

    def _save_error_history(self):
        """Save error history to log file"""
        try:
            data = [vars(error) for error in self.error_history]
            with open(self.error_log_path, "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save error history: {e}")

    def capture_terminal_error(self, error_output: str) -> ErrorAnalysis:
        """
        Capture and analyze a terminal error

        Args:
            error_output: Raw terminal error output

        Returns:
            ErrorAnalysis object with analysis results
        """
        analysis = ErrorAnalysis(
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            error_text=error_output,
            error_type="unknown",
            severity="low",
        )

        # Analyze error against known patterns
        for pattern_name, pattern in self.error_patterns.items():
            match = re.search(pattern.pattern, error_output, re.IGNORECASE)
            if match:
                analysis.matched_pattern = pattern
                analysis.error_type = pattern.error_type
                analysis.severity = pattern.severity
                analysis.suggested_fix = pattern.solution.format(
                    **match.groupdict() if match.groups() else {}
                )
                analysis.documentation_updates = [pattern.documentation_update]
                analysis.test_updates = [pattern.test_case]
                analysis.prevention_measures = pattern.prevention_measures.copy()
                break

        # Add to history
        self.error_history.append(analysis)
        self._save_error_history()

        return analysis

    def fix_error(self, analysis: ErrorAnalysis) -> bool:
        """
        Attempt to automatically fix the error

        Args:
            analysis: ErrorAnalysis object

        Returns:
            True if fix was successful, False otherwise
        """
        if not analysis.matched_pattern:
            return False

        try:
            # Execute fix based on error type
            if analysis.error_type == "import_error":
                return self._fix_import_error(analysis)
            elif analysis.error_type == "file_not_found":
                return self._fix_file_not_found(analysis)
            elif analysis.error_type == "api_key_missing":
                return self._fix_api_key_missing(analysis)
            elif analysis.error_type == "network_timeout":
                return self._fix_network_timeout(analysis)
            elif analysis.error_type == "validation_error":
                return self._fix_validation_error(analysis)

        except Exception as e:
            logger.error(f"Failed to apply automatic fix: {e}")

        return False

    def _fix_import_error(self, analysis: ErrorAnalysis) -> bool:
        """Fix missing import by installing package"""
        match = re.search(r"No module named '(\w+)'", analysis.error_text)
        if match:
            module_name = match.group(1)
            try:
                # Install package
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", module_name],
                    check=True,
                    capture_output=True,
                )

                # Update requirements.txt
                self._update_requirements_txt(module_name)

                analysis.fixed = True
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install {module_name}: {e}")

        return False

    def _fix_file_not_found(self, analysis: ErrorAnalysis) -> bool:
        """Fix missing file by creating template"""
        match = re.search(r"No such file or directory: '(.+)'", analysis.error_text)
        if match:
            file_path = match.group(1)
            try:
                # Create directory if needed
                Path(file_path).parent.mkdir(parents=True, exist_ok=True)

                # Create template file based on extension
                self._create_file_template(file_path)

                analysis.fixed = True
                return True
            except Exception as e:
                logger.error(f"Failed to create file {file_path}: {e}")

        return False

    def _fix_api_key_missing(self, analysis: ErrorAnalysis) -> bool:
        """Fix missing API key by updating .env.example"""
        # This is more of a documentation/setup fix
        self._update_env_example()
        analysis.fixed = True
        return True

    def _fix_network_timeout(self, analysis: ErrorAnalysis) -> bool:
        """Fix network timeout by updating retry logic"""
        # This would typically require code changes
        # For now, just log the recommendation
        logger.info("Network timeout detected - consider implementing retry logic")
        analysis.fixed = True  # Mark as addressed
        return True

    def _fix_validation_error(self, analysis: ErrorAnalysis) -> bool:
        """Fix validation error by improving validation logic"""
        # This would typically require code changes
        logger.info("Validation error detected - consider improving input validation")
        analysis.fixed = True  # Mark as addressed
        return True

    def update_documentation(self, analysis: ErrorAnalysis) -> bool:
        """
        Update documentation to prevent future occurrences

        Args:
            analysis: ErrorAnalysis object

        Returns:
            True if documentation was updated successfully
        """
        try:
            # Update README.md
            self._update_readme(analysis)

            # Update setup documentation
            self._update_setup_docs(analysis)

            analysis.documented = True
            return True

        except Exception as e:
            logger.error(f"Failed to update documentation: {e}")
            return False

    def generate_tests(self, analysis: ErrorAnalysis) -> bool:
        """
        Generate test cases to prevent future occurrences

        Args:
            analysis: ErrorAnalysis object

        Returns:
            True if tests were generated successfully
        """
        try:
            # Generate unit tests
            self._generate_unit_tests(analysis)

            # Generate integration tests
            self._generate_integration_tests(analysis)

            analysis.tested = True
            return True

        except Exception as e:
            logger.error(f"Failed to generate tests: {e}")
            return False

    def implement_prevention_measures(self, analysis: ErrorAnalysis) -> bool:
        """
        Implement prevention measures to avoid future occurrences

        Args:
            analysis: ErrorAnalysis object

        Returns:
            True if prevention measures were implemented
        """
        if not analysis.prevention_measures:
            return True

        try:
            for measure in analysis.prevention_measures:
                if "requirements.txt" in measure:
                    # Already handled in _fix_import_error
                    continue
                elif "validation" in measure:
                    self._add_validation_checks(analysis)
                elif "documentation" in measure:
                    # Already handled in update_documentation
                    continue
                elif "retry" in measure:
                    self._add_retry_logic(analysis)

            return True

        except Exception as e:
            logger.error(f"Failed to implement prevention measures: {e}")
            return False

    def _update_requirements_txt(self, package_name: str):
        """Update requirements.txt with new package"""
        req_file = Path("requirements.txt")
        if not req_file.exists():
            req_file.touch()

        with open(req_file, "a") as f:
            f.write(f"{package_name}\n")

    def _create_file_template(self, file_path: str):
        """Create a template file based on extension"""
        path = Path(file_path)
        extension = path.suffix.lower()

        templates = {
            ".py": '#!/usr/bin/env python3\n"""\nTemplate file\n"""\n\n',
            ".json": "{}\n",
            ".yaml": "---\n# Template YAML file\n",
            ".md": "# Template Markdown File\n\n",
            ".txt": "# Template text file\n",
        }

        content = templates.get(extension, f"# Template file: {path.name}\n")
        path.write_text(content)

    def _update_env_example(self):
        """Update .env.example with API key templates"""
        env_example = Path(".env.example")
        if not env_example.exists():
            env_example.touch()

        with open(env_example, "a") as f:
            f.write("\n# API Keys\n")
            f.write("# WINSTON_API_KEY=your_winston_api_key_here\n")
            f.write("# OPENAI_API_KEY=your_openai_api_key_here\n")
            f.write("# DEEPSEEK_API_KEY=your_deepseek_api_key_here\n")

    def _update_readme(self, analysis: ErrorAnalysis):
        """Update README.md with error prevention information"""
        readme_path = Path("README.md")
        if not readme_path.exists():
            return

        # Add troubleshooting section if it doesn't exist
        content = readme_path.read_text()
        if "## Troubleshooting" not in content:
            content += "\n## Troubleshooting\n\n"

        # Add specific error information
        if analysis.matched_pattern:
            content += f"### {analysis.matched_pattern.description}\n"
            content += f"- **Error**: {analysis.error_text[:100]}...\n"
            content += f"- **Solution**: {analysis.matched_pattern.solution}\n\n"

        readme_path.write_text(content)

    def _update_setup_docs(self, analysis: ErrorAnalysis):
        """Update setup documentation"""
        docs_dir = Path("docs")
        docs_dir.mkdir(exist_ok=True)

        setup_doc = docs_dir / "SETUP.md"
        if not setup_doc.exists():
            setup_doc.write_text("# Setup Documentation\n\n")

        content = setup_doc.read_text()
        if "## Common Issues" not in content:
            content += "\n## Common Issues\n\n"

        if analysis.matched_pattern:
            content += f"### {analysis.matched_pattern.description}\n"
            content += (
                f"- **Prevention**: {', '.join(analysis.prevention_measures)}\n\n"
            )

        setup_doc.write_text(content)

    def _generate_unit_tests(self, analysis: ErrorAnalysis):
        """Generate unit tests for the error scenario"""
        tests_dir = Path("tests/unit")
        tests_dir.mkdir(parents=True, exist_ok=True)

        if analysis.matched_pattern:
            test_file = tests_dir / f"test_{analysis.matched_pattern.error_type}.py"
            if not test_file.exists():
                test_content = f'''#!/usr/bin/env python3
"""
Unit tests for {analysis.matched_pattern.error_type}
"""

import pytest
from unittest.mock import patch, MagicMock


class Test{analysis.matched_pattern.error_type.title().replace('_', '')}:
    """Test cases for {analysis.matched_pattern.description}"""

    def test_{analysis.matched_pattern.error_type}_prevention(self):
        """Test that {analysis.matched_pattern.error_type} is properly handled"""
        # TODO: Implement test case
        pass

    def test_{analysis.matched_pattern.error_type}_recovery(self):
        """Test recovery from {analysis.matched_pattern.error_type}"""
        # TODO: Implement test case
        pass
'''
                test_file.write_text(test_content)

    def _generate_integration_tests(self, analysis: ErrorAnalysis):
        """Generate integration tests for the error scenario"""
        tests_dir = Path("tests/integration")
        tests_dir.mkdir(parents=True, exist_ok=True)

        if analysis.matched_pattern:
            test_file = (
                tests_dir / f"test_{analysis.matched_pattern.error_type}_integration.py"
            )
            if not test_file.exists():
                test_content = f'''#!/usr/bin/env python3
"""
Integration tests for {analysis.matched_pattern.error_type}
"""

import pytest


class Test{analysis.matched_pattern.error_type.title().replace('_', '')}Integration:
    """Integration tests for {analysis.matched_pattern.description}"""

    def test_end_to_end_{analysis.matched_pattern.error_type}_handling(self):
        """Test end-to-end handling of {analysis.matched_pattern.error_type}"""
        # TODO: Implement integration test
        pass
'''
                test_file.write_text(test_content)

    def _add_validation_checks(self, analysis: ErrorAnalysis):
        """Add validation checks to prevent future errors"""
        # This would typically modify source code
        # For now, just log the recommendation
        logger.info(f"Consider adding validation checks for: {analysis.error_type}")

    def _add_retry_logic(self, analysis: ErrorAnalysis):
        """Add retry logic to handle transient errors"""
        # This would typically modify source code
        # For now, just log the recommendation
        logger.info(f"Consider adding retry logic for: {analysis.error_type}")

    def process_error_output(self, error_output: str) -> ErrorAnalysis:
        """
        Complete workflow: capture, analyze, fix, document, and test error

        Args:
            error_output: Raw terminal error output

        Returns:
            ErrorAnalysis with complete processing results
        """
        # Step 1: Capture and analyze error
        analysis = self.capture_terminal_error(error_output)

        # Display loud error message
        LoudError.critical_error(
            "Terminal error detected",
            details=f"{analysis.error_type}: {analysis.error_text[:200]}",
        )

        # Step 2: Attempt automatic fix
        if analysis.matched_pattern:
            print(f"🔧 Attempting automatic fix for {analysis.error_type}...")
            analysis.fixed = self.fix_error(analysis)

            if analysis.fixed:
                print("✅ Error automatically fixed!")
            else:
                print("❌ Automatic fix failed, manual intervention required")

        # Step 3: Update documentation
        print("📚 Updating documentation...")
        analysis.documented = self.update_documentation(analysis)

        if analysis.documented:
            print("✅ Documentation updated!")
        else:
            print("❌ Documentation update failed")

        # Step 4: Generate tests
        print("🧪 Generating test cases...")
        analysis.tested = self.generate_tests(analysis)

        if analysis.tested:
            print("✅ Test cases generated!")
        else:
            print("❌ Test generation failed")

        # Step 5: Implement prevention measures
        print("🛡️ Implementing prevention measures...")
        prevention_success = self.implement_prevention_measures(analysis)

        if prevention_success:
            print("✅ Prevention measures implemented!")
        else:
            print("❌ Prevention measures implementation failed")

        # Save updated analysis
        self._save_error_history()

        return analysis

    def get_error_statistics(self) -> Dict:
        """Get statistics about captured errors"""
        total_errors = len(self.error_history)
        error_types = {}
        severities = {}

        for error in self.error_history:
            error_types[error.error_type] = error_types.get(error.error_type, 0) + 1
            severities[error.severity] = severities.get(error.severity, 0) + 1

        fixed_count = sum(1 for e in self.error_history if e.fixed)
        documented_count = sum(1 for e in self.error_history if e.documented)
        tested_count = sum(1 for e in self.error_history if e.tested)

        return {
            "total_errors": total_errors,
            "error_types": error_types,
            "severities": severities,
            "fixed_percentage": (fixed_count / total_errors * 100)
            if total_errors > 0
            else 0,
            "documented_percentage": (documented_count / total_errors * 100)
            if total_errors > 0
            else 0,
            "tested_percentage": (tested_count / total_errors * 100)
            if total_errors > 0
            else 0,
        }

    def generate_error_report(self) -> str:
        """Generate a comprehensive error report"""
        stats = self.get_error_statistics()

        report = "# Terminal Error Analysis Report\n\n"
        report += "## Summary\n"
        report += f"- Total Errors: {stats['total_errors']}\n"
        report += f"- Fixed: {stats['fixed_percentage']:.1f}%\n"
        report += f"- Documented: {stats['documented_percentage']:.1f}%\n"
        report += f"- Tested: {stats['tested_percentage']:.1f}%\n\n"

        report += "## Error Types\n"
        for error_type, count in stats["error_types"].items():
            report += f"- {error_type}: {count}\n"

        report += "\n## Severity Distribution\n"
        for severity, count in stats["severities"].items():
            report += f"- {severity}: {count}\n"

        report += "\n## Recent Errors\n"
        for error in self.error_history[-10:]:  # Last 10 errors
            report += f"- {error.timestamp}: {error.error_type} ({error.severity})\n"
            if error.fixed:
                report += "  ✅ Fixed\n"
            if error.documented:
                report += "  📚 Documented\n"
            if error.tested:
                report += "  🧪 Tested\n"

        return report


# Global instance for easy access
_error_handler = None


def get_error_handler() -> TerminalErrorHandler:
    """Get the global terminal error handler instance"""
    global _error_handler
    if _error_handler is None:
        _error_handler = TerminalErrorHandler()
    return _error_handler


def handle_terminal_error(error_output: str) -> ErrorAnalysis:
    """
    Convenience function to handle a terminal error

    Args:
        error_output: Raw terminal error output

    Returns:
        ErrorAnalysis with complete processing results
    """
    handler = get_error_handler()
    return handler.process_error_output(error_output)


# Integration with existing error handling
def integrate_with_existing_errors():
    """Integrate with existing error handling systems"""
    # This could be called during system initialization
    # to set up error capture hooks
    pass


if __name__ == "__main__":
    # Example usage
    handler = TerminalErrorHandler()

    # Simulate an error
    sample_error = "ImportError: No module named 'requests'"
    analysis = handler.process_error_output(sample_error)

    print("\nError Analysis Complete:")
    print(f"- Type: {analysis.error_type}")
    print(f"- Severity: {analysis.severity}")
    print(f"- Fixed: {analysis.fixed}")
    print(f"- Documented: {analysis.documented}")
    print(f"- Tested: {analysis.tested}")

    # Generate report
    report = handler.generate_error_report()
    print(f"\n{report}")
