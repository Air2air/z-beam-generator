#!/usr/bin/env python3
"""
Absolute Import Migration Tool

This script helps migrate relative imports to absolute imports
throughout the codebase to prevent import path issues.
"""

import os
import re
import ast
import logging
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ImportIssue:
    """Represents an import issue found in a file."""
    file_path: str
    line_number: int
    original_import: str
    suggested_fix: str
    confidence: str  # 'high', 'medium', 'low'


class AbsoluteImportMigrator:
    """Tool for migrating relative imports to absolute imports."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.python_files: List[Path] = []
        self.issues: List[ImportIssue] = []

    def scan_project(self) -> None:
        """Scan the project for Python files."""
        self.python_files = list(self.project_root.rglob("*.py"))
        logger.info(f"Found {len(self.python_files)} Python files")

    def analyze_imports(self) -> List[ImportIssue]:
        """Analyze all Python files for import issues."""
        issues = []

        for file_path in self.python_files:
            try:
                issues.extend(self._analyze_file_imports(file_path))
            except Exception as e:
                logger.warning(f"Error analyzing {file_path}: {e}")

        self.issues = issues
        return issues

    def _analyze_file_imports(self, file_path: Path) -> List[ImportIssue]:
        """Analyze imports in a single file."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse the AST
            tree = ast.parse(content, filename=str(file_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    issue = self._check_import_statement(file_path, node, content)
                    if issue:
                        issues.append(issue)

        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            logger.warning(f"Error parsing {file_path}: {e}")

        return issues

    def _check_import_statement(self, file_path: Path, node: ast.ImportFrom, content: str) -> Optional[ImportIssue]:
        """Check if an import statement needs to be fixed."""
        if not node.level:  # Not a relative import
            return None

        # Get the line content
        lines = content.split('\n')
        line_content = lines[node.lineno - 1].strip()

        # Calculate the absolute module path
        relative_parts = ['.'] * node.level
        if node.module:
            relative_parts.append(node.module)

        relative_path = '.'.join(relative_parts)

        # Calculate absolute path from file location
        file_dir = file_path.parent
        absolute_parts = []

        # Go up the directory tree based on relative import level
        current_dir = file_dir
        for _ in range(node.level):
            current_dir = current_dir.parent
            if current_dir == self.project_root:
                break

        # Build absolute path
        try:
            relative_to_root = file_dir.relative_to(self.project_root)
            path_parts = str(relative_to_root).split(os.sep)

            # Remove the parts we're going up
            if len(path_parts) >= node.level:
                remaining_parts = path_parts[:-node.level] if node.level > 0 else path_parts
                absolute_parts.extend(remaining_parts)

            if node.module:
                absolute_parts.extend(node.module.split('.'))

            absolute_import = '.'.join(absolute_parts)

            # Create suggested fix
            imports = []
            for alias in node.names:
                if alias.asname:
                    imports.append(f"{alias.name} as {alias.asname}")
                else:
                    imports.append(alias.name)

            suggested_fix = f"from {absolute_import} import {', '.join(imports)}"

            confidence = self._calculate_confidence(file_path, absolute_import)

            return ImportIssue(
                file_path=str(file_path),
                line_number=node.lineno,
                original_import=line_content,
                suggested_fix=suggested_fix,
                confidence=confidence
            )

        except Exception as e:
            logger.debug(f"Could not calculate absolute import for {line_content}: {e}")
            return None

    def _calculate_confidence(self, file_path: Path, absolute_import: str) -> str:
        """Calculate confidence level for the suggested fix."""
        try:
            # Try to import the module to verify it exists
            import importlib
            importlib.import_module(absolute_import)
            return 'high'
        except ImportError:
            # Check if the module file exists
            module_path = absolute_import.replace('.', os.sep) + '.py'
            if (self.project_root / module_path).exists():
                return 'medium'
            else:
                return 'low'

    def generate_report(self) -> str:
        """Generate a report of all import issues."""
        report = []
        report.append("# Absolute Import Migration Report")
        report.append(f"Project: {self.project_root}")
        report.append(f"Files scanned: {len(self.python_files)}")
        report.append(f"Issues found: {len(self.issues)}")
        report.append("")

        # Group by confidence
        high_confidence = [i for i in self.issues if i.confidence == 'high']
        medium_confidence = [i for i in self.issues if i.confidence == 'medium']
        low_confidence = [i for i in self.issues if i.confidence == 'low']

        report.append("## High Confidence Fixes")
        report.append(f"Count: {len(high_confidence)}")
        for issue in high_confidence[:10]:  # Show first 10
            report.append(f"- {issue.file_path}:{issue.line_number}")
            report.append(f"  `{issue.original_import}`")
            report.append(f"  → `{issue.suggested_fix}`")
        if len(high_confidence) > 10:
            report.append(f"  ... and {len(high_confidence) - 10} more")
        report.append("")

        report.append("## Medium Confidence Fixes")
        report.append(f"Count: {len(medium_confidence)}")
        for issue in medium_confidence[:5]:
            report.append(f"- {issue.file_path}:{issue.line_number}")
            report.append(f"  `{issue.original_import}`")
            report.append(f"  → `{issue.suggested_fix}`")
        report.append("")

        report.append("## Low Confidence Fixes")
        report.append(f"Count: {len(low_confidence)}")
        report.append("These may need manual review")
        report.append("")

        return '\n'.join(report)

    def apply_fixes(self, confidence_threshold: str = 'high') -> int:
        """Apply fixes for issues above the confidence threshold."""
        confidence_levels = {'high': 3, 'medium': 2, 'low': 1}
        threshold_level = confidence_levels.get(confidence_threshold, 3)

        fixes_applied = 0
        for issue in self.issues:
            issue_level = confidence_levels.get(issue.confidence, 0)
            if issue_level >= threshold_level:
                try:
                    self._apply_single_fix(issue)
                    fixes_applied += 1
                    logger.info(f"Applied fix: {issue.file_path}:{issue.line_number}")
                except Exception as e:
                    logger.error(f"Failed to apply fix {issue.file_path}:{issue.line_number}: {e}")

        return fixes_applied

    def _apply_single_fix(self, issue: ImportIssue) -> None:
        """Apply a single import fix."""
        with open(issue.file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        lines[issue.line_number - 1] = issue.suggested_fix

        with open(issue.file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))


def main():
    """Main function for the migration tool."""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate relative imports to absolute imports")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--analyze-only", action="store_true", help="Only analyze, don't fix")
    parser.add_argument("--confidence", choices=['high', 'medium', 'low'], default='high',
                       help="Minimum confidence level for fixes")
    parser.add_argument("--report-file", help="Save report to file")

    args = parser.parse_args()

    migrator = AbsoluteImportMigrator(args.project_root)
    migrator.scan_project()

    print(f"Scanning {len(migrator.python_files)} Python files...")

    issues = migrator.analyze_imports()
    print(f"Found {len(issues)} import issues")

    # Generate and display report
    report = migrator.generate_report()
    print(report)

    if args.report_file:
        with open(args.report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report saved to {args.report_file}")

    if not args.analyze_only:
        print(f"\nApplying fixes with {args.confidence} confidence...")
        fixes_applied = migrator.apply_fixes(args.confidence)
        print(f"Applied {fixes_applied} fixes")

    return 0


if __name__ == "__main__":
    exit(main())
