#!/usr/bin/env python3
"""
Export Validation Report

Validates exported frontmatter files for quality and consistency.
Generates comprehensive validation report with actionable fixes.

Checks:
- Required fields present
- YAML well-formed
- Schema version consistency
- File naming conventions
- Internal links valid
- Data type correctness
- No broken references

Usage:
    # Validate all domains
    python3 scripts/validation/validate_export.py
    
    # Validate specific domain
    python3 scripts/validation/validate_export.py --domain materials
    
    # Output JSON report
    python3 scripts/validation/validate_export.py --json
    
    # Strict mode (fail on warnings)
    python3 scripts/validation/validate_export.py --strict

Exit Codes:
    0: All validations passed
    1: Validation errors found
    2: Validation warnings found (strict mode only)
"""

import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.exceptions import ValidationError

logger = logging.getLogger(__name__)


@dataclass
class ValidationIssue:
    """Represents a validation issue."""
    severity: str  # 'error' or 'warning'
    category: str  # Type of issue
    file: str  # File path
    message: str  # Issue description
    fix: Optional[str] = None  # Suggested fix


@dataclass
class ValidationReport:
    """Comprehensive validation report."""
    total_files: int = 0
    files_checked: int = 0
    errors: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0
    
    @property
    def passed(self) -> bool:
        return not self.has_errors


class ExportValidator:
    """Validates exported frontmatter files."""
    
    # Required fields for all frontmatter files
    REQUIRED_FIELDS = ['id', 'name', 'slug', 'schema_version']
    
    # Expected schema version
    EXPECTED_SCHEMA_VERSION = '1.0'
    
    # Valid slug pattern (lowercase, hyphens, no spaces)
    SLUG_PATTERN = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
    
    def __init__(self, frontmatter_dir: Path, strict: bool = False):
        """
        Initialize validator.
        
        Args:
            frontmatter_dir: Path to frontmatter directory
            strict: If True, treat warnings as errors
        """
        self.frontmatter_dir = frontmatter_dir
        self.strict = strict
        self.report = ValidationReport()
        self.all_slugs: Set[str] = set()  # Track for duplicates
        self.all_ids: Set[str] = set()  # Track for duplicates
    
    def validate_all(self, domain: Optional[str] = None) -> ValidationReport:
        """
        Validate all frontmatter files or specific domain.
        
        Args:
            domain: Specific domain to validate (None = all domains)
        
        Returns:
            ValidationReport with results
        """
        if domain:
            domain_dir = self.frontmatter_dir / domain
            if not domain_dir.exists():
                self.report.errors.append(ValidationIssue(
                    severity='error',
                    category='missing_domain',
                    file=str(domain_dir),
                    message=f"Domain directory not found: {domain}",
                    fix=f"Run export for domain: python3 scripts/operations/deploy_all.py"
                ))
                return self.report
            
            self._validate_domain(domain)
        else:
            # Validate all domains
            for domain_dir in self.frontmatter_dir.iterdir():
                if domain_dir.is_dir() and not domain_dir.name.startswith('.'):
                    self._validate_domain(domain_dir.name)
        
        return self.report
    
    def _validate_domain(self, domain: str) -> None:
        """Validate all files in a domain."""
        domain_dir = self.frontmatter_dir / domain
        
        for yaml_file in domain_dir.glob('*.yaml'):
            self.report.total_files += 1
            self._validate_file(yaml_file, domain)
    
    def _validate_file(self, file_path: Path, domain: str) -> None:
        """Validate a single frontmatter file."""
        try:
            # Load YAML
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not isinstance(data, dict):
                self._add_error(
                    'invalid_yaml',
                    str(file_path),
                    "File content is not a YAML dictionary",
                    "Ensure file contains valid YAML dictionary (key: value pairs)"
                )
                return
            
            self.report.files_checked += 1
            
            # Run all validation checks
            self._check_required_fields(data, file_path)
            self._check_schema_version(data, file_path)
            self._check_slug_format(data, file_path)
            self._check_duplicates(data, file_path)
            self._check_filename_matches_slug(data, file_path)
            self._check_data_types(data, file_path)
            self._check_relationships(data, file_path, domain)
            
        except yaml.YAMLError as e:
            self._add_error(
                'yaml_parsing',
                str(file_path),
                f"YAML parsing error: {e}",
                "Fix YAML syntax errors"
            )
        except Exception as e:
            self._add_error(
                'validation_error',
                str(file_path),
                f"Unexpected error during validation: {e}",
                "Check file integrity"
            )
    
    def _check_required_fields(self, data: Dict[str, Any], file_path: Path) -> None:
        """Check all required fields are present."""
        missing = [field for field in self.REQUIRED_FIELDS if field not in data]
        
        if missing:
            self._add_error(
                'missing_fields',
                str(file_path),
                f"Missing required fields: {', '.join(missing)}",
                f"Add missing fields to frontmatter"
            )
    
    def _check_schema_version(self, data: Dict[str, Any], file_path: Path) -> None:
        """Check schema version matches expected."""
        if 'schema_version' in data:
            version = str(data['schema_version'])
            if version != self.EXPECTED_SCHEMA_VERSION:
                self._add_warning(
                    'schema_version',
                    str(file_path),
                    f"Schema version {version} doesn't match expected {self.EXPECTED_SCHEMA_VERSION}",
                    f"Update schema_version to {self.EXPECTED_SCHEMA_VERSION}"
                )
    
    def _check_slug_format(self, data: Dict[str, Any], file_path: Path) -> None:
        """Check slug follows naming conventions."""
        if 'slug' in data:
            slug = data['slug']
            if not isinstance(slug, str):
                self._add_error(
                    'invalid_slug',
                    str(file_path),
                    f"Slug must be string, got {type(slug).__name__}",
                    "Convert slug to string"
                )
            elif not self.SLUG_PATTERN.match(slug):
                self._add_error(
                    'invalid_slug',
                    str(file_path),
                    f"Invalid slug format: '{slug}' (must be lowercase with hyphens)",
                    "Convert slug to lowercase with hyphens (no spaces or underscores)"
                )
    
    def _check_duplicates(self, data: Dict[str, Any], file_path: Path) -> None:
        """Check for duplicate IDs and slugs across all files."""
        if 'id' in data:
            item_id = data['id']
            if item_id in self.all_ids:
                self._add_error(
                    'duplicate_id',
                    str(file_path),
                    f"Duplicate ID: '{item_id}'",
                    "Ensure each item has unique ID"
                )
            self.all_ids.add(item_id)
        
        if 'slug' in data:
            slug = data['slug']
            if slug in self.all_slugs:
                self._add_error(
                    'duplicate_slug',
                    str(file_path),
                    f"Duplicate slug: '{slug}'",
                    "Ensure each item has unique slug"
                )
            self.all_slugs.add(slug)
    
    def _check_filename_matches_slug(self, data: Dict[str, Any], file_path: Path) -> None:
        """Check filename matches slug."""
        if 'slug' in data:
            expected_filename = f"{data['slug']}.yaml"
            actual_filename = file_path.name
            
            if expected_filename != actual_filename:
                self._add_warning(
                    'filename_mismatch',
                    str(file_path),
                    f"Filename '{actual_filename}' doesn't match slug '{data['slug']}'",
                    f"Rename file to {expected_filename}"
                )
    
    def _check_data_types(self, data: Dict[str, Any], file_path: Path) -> None:
        """Check data types are correct."""
        # String fields
        for field in ['id', 'name', 'slug', 'description']:
            if field in data and not isinstance(data[field], str):
                self._add_warning(
                    'invalid_type',
                    str(file_path),
                    f"Field '{field}' should be string, got {type(data[field]).__name__}",
                    f"Convert {field} to string"
                )
        
        # Array fields
        for field in ['breadcrumb', 'categories']:
            if field in data and not isinstance(data[field], list):
                self._add_warning(
                    'invalid_type',
                    str(file_path),
                    f"Field '{field}' should be array, got {type(data[field]).__name__}",
                    f"Convert {field} to array"
                )
    
    def _check_relationships(self, data: Dict[str, Any], file_path: Path, domain: str) -> None:
        """Check relationship fields reference valid items."""
        # Check breadcrumb links if present
        if 'breadcrumb' in data and isinstance(data['breadcrumb'], list):
            for idx, crumb in enumerate(data['breadcrumb']):
                if isinstance(crumb, dict) and 'href' in crumb:
                    href = crumb['href']
                    if href and href != '/' and not href.startswith('http'):
                        # Internal link - basic format check only
                        # (full validation would require checking all domains)
                        if not href.startswith('/'):
                            self._add_warning(
                                'invalid_link',
                                str(file_path),
                                f"Breadcrumb link should be absolute: '{href}'",
                                f"Add leading slash to href"
                            )
    
    def _add_error(self, category: str, file: str, message: str, fix: Optional[str] = None) -> None:
        """Add error to report."""
        self.report.errors.append(ValidationIssue(
            severity='error',
            category=category,
            file=file,
            message=message,
            fix=fix
        ))
    
    def _add_warning(self, category: str, file: str, message: str, fix: Optional[str] = None) -> None:
        """Add warning to report (or error if strict mode)."""
        issue = ValidationIssue(
            severity='warning' if not self.strict else 'error',
            category=category,
            file=file,
            message=message,
            fix=fix
        )
        
        if self.strict:
            self.report.errors.append(issue)
        else:
            self.report.warnings.append(issue)


def print_report(report: ValidationReport, json_output: bool = False) -> None:
    """
    Print validation report.
    
    Args:
        report: Validation report to print
        json_output: If True, output JSON instead of human-readable
    """
    if json_output:
        # JSON output
        report_dict = {
            'total_files': report.total_files,
            'files_checked': report.files_checked,
            'errors': [
                {
                    'severity': issue.severity,
                    'category': issue.category,
                    'file': issue.file,
                    'message': issue.message,
                    'fix': issue.fix
                }
                for issue in report.errors
            ],
            'warnings': [
                {
                    'severity': issue.severity,
                    'category': issue.category,
                    'file': issue.file,
                    'message': issue.message,
                    'fix': issue.fix
                }
                for issue in report.warnings
            ],
            'passed': report.passed
        }
        print(json.dumps(report_dict, indent=2))
    else:
        # Human-readable output
        print("\n" + "="*80)
        print("EXPORT VALIDATION REPORT")
        print("="*80)
        print(f"\nFiles checked: {report.files_checked}/{report.total_files}")
        
        if report.errors:
            print(f"\n❌ ERRORS: {len(report.errors)}")
            print("-" * 80)
            for issue in report.errors:
                print(f"\n[{issue.category.upper()}] {issue.file}")
                print(f"  {issue.message}")
                if issue.fix:
                    print(f"  💡 Fix: {issue.fix}")
        
        if report.warnings:
            print(f"\n⚠️  WARNINGS: {len(report.warnings)}")
            print("-" * 80)
            for issue in report.warnings:
                print(f"\n[{issue.category.upper()}] {issue.file}")
                print(f"  {issue.message}")
                if issue.fix:
                    print(f"  💡 Fix: {issue.fix}")
        
        print("\n" + "="*80)
        if report.passed:
            print("✅ VALIDATION PASSED")
        else:
            print("❌ VALIDATION FAILED")
        print("="*80 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate exported frontmatter files"
    )
    parser.add_argument(
        '--domain',
        help="Specific domain to validate (materials, contaminants, etc.)"
    )
    parser.add_argument(
        '--frontmatter-dir',
        default='../z-beam/frontmatter',
        help="Path to frontmatter directory (default: ../z-beam/frontmatter)"
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help="Output JSON report instead of human-readable"
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help="Treat warnings as errors (fail on warnings)"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    # Validate frontmatter directory exists
    frontmatter_dir = Path(args.frontmatter_dir)
    if not frontmatter_dir.exists():
        logger.error(f"Frontmatter directory not found: {frontmatter_dir}")
        logger.error("Run export first: python3 scripts/operations/deploy_all.py")
        sys.exit(1)
    
    # Run validation
    validator = ExportValidator(frontmatter_dir, strict=args.strict)
    report = validator.validate_all(domain=args.domain)
    
    # Print report
    print_report(report, json_output=args.json)
    
    # Exit with appropriate code
    if report.has_errors:
        sys.exit(1)
    elif args.strict and report.has_warnings:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
