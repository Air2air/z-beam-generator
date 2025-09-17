#!/usr/bin/env python3
"""
Import Validation Script for CI/CD

This script validates all imports in the codebase and reports issues.
Used in CI/CD pipeline to prevent import path errors.
"""

import ast
import importlib
import logging
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.import_system import import_manager, validate_critical_imports

logger = logging.getLogger(__name__)


class ImportValidator:
    """Validates imports across the codebase."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues: List[Dict[str, str]] = []
        self.checked_modules: Set[str] = set()
        self.python_files: List[Path] = []

    def find_python_files(self) -> None:
        """Find all Python files in the project."""
        self.python_files = list(self.project_root.rglob("*.py"))
        logger.info(f"Found {len(self.python_files)} Python files")

    def extract_imports_from_file(self, file_path: Path) -> List[Tuple[str, int]]:
        """Extract all import statements from a Python file."""
        imports = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append((alias.name, node.lineno))
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append((node.module, node.lineno))

        except SyntaxError as e:
            self.issues.append(
                {
                    "file": str(file_path),
                    "type": "syntax_error",
                    "message": f"Syntax error: {e}",
                    "line": str(e.lineno) if e.lineno else "unknown",
                }
            )
        except Exception as e:
            self.issues.append(
                {
                    "file": str(file_path),
                    "type": "parse_error",
                    "message": f"Failed to parse: {e}",
                    "line": "unknown",
                }
            )

        return imports

    def validate_import(self, module_name: str, file_path: Path, line_no: int) -> None:
        """Validate a single import."""
        if module_name in self.checked_modules:
            return

        self.checked_modules.add(module_name)

        try:
            # Try to import the module
            importlib.import_module(module_name)
            logger.debug(f"✓ {module_name}")
        except ImportError as e:
            # Check if it's a relative import that should be absolute
            if module_name.startswith("."):
                self.issues.append(
                    {
                        "file": str(file_path),
                        "type": "relative_import",
                        "message": f"Relative import '{module_name}' should be absolute",
                        "line": str(line_no),
                        "module": module_name,
                    }
                )
            else:
                # Check if it's a local module
                module_parts = module_name.split(".")
                possible_paths = [
                    self.project_root / f"{module_name.replace('.', '/')}.py",
                    self.project_root / module_parts[0] / "__init__.py",
                ]

                is_local = any(path.exists() for path in possible_paths)

                if is_local:
                    self.issues.append(
                        {
                            "file": str(file_path),
                            "type": "missing_local_import",
                            "message": f"Local module '{module_name}' not found in path",
                            "line": str(line_no),
                            "module": module_name,
                        }
                    )
                else:
                    self.issues.append(
                        {
                            "file": str(file_path),
                            "type": "missing_dependency",
                            "message": f"External dependency '{module_name}' not installed: {e}",
                            "line": str(line_no),
                            "module": module_name,
                        }
                    )

    def validate_all_imports(self) -> None:
        """Validate imports in all Python files."""
        logger.info("Starting import validation...")

        for file_path in self.python_files:
            # Skip certain directories
            if any(
                skip in str(file_path)
                for skip in ["__pycache__", ".git", "archive", "cleanup"]
            ):
                continue

            logger.debug(f"Checking {file_path}")
            imports = self.extract_imports_from_file(file_path)

            for module_name, line_no in imports:
                self.validate_import(module_name, file_path, line_no)

    def generate_report(self) -> Dict[str, any]:
        """Generate a validation report."""
        issue_counts = defaultdict(int)
        for issue in self.issues:
            issue_counts[issue["type"]] += 1

        return {
            "total_files": len(self.python_files),
            "total_issues": len(self.issues),
            "issue_counts": dict(issue_counts),
            "issues": self.issues,
            "critical_imports_ok": validate_critical_imports(),
        }

    def print_report(self, report: Dict[str, any]) -> None:
        """Print the validation report."""
        print("\n" + "=" * 60)
        print("IMPORT VALIDATION REPORT")
        print("=" * 60)

        print(f"Files checked: {report['total_files']}")
        print(f"Total issues: {report['total_issues']}")
        print(f"Critical imports OK: {report['critical_imports_ok']}")

        if report["issue_counts"]:
            print("\nIssue breakdown:")
            for issue_type, count in report["issue_counts"].items():
                print(f"  {issue_type}: {count}")

        if report["issues"]:
            print("\nDetailed issues:")
            for issue in report["issues"][:20]:  # Show first 20 issues
                print(
                    f"  {issue['file']}:{issue['line']} - {issue['type']}: {issue['message']}"
                )

            if len(report["issues"]) > 20:
                print(f"  ... and {len(report['issues']) - 20} more issues")

        print("\n" + "=" * 60)


def main():
    """Main validation function."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    validator = ImportValidator(project_root)
    validator.find_python_files()
    validator.validate_all_imports()

    report = validator.generate_report()
    validator.print_report(report)

    # Exit with error code if there are issues
    if report["total_issues"] > 0 or not report["critical_imports_ok"]:
        print("\n❌ Import validation failed!")
        sys.exit(1)
    else:
        print("\n✅ All imports validated successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
