#!/usr/bin/env python3
"""
Validate content boundaries in component files using global metadata delimiting standard.
Ensures proper separation between content and metadata sections.
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json


class ContentBoundaryValidator:
    """Validates component files have proper content/metadata boundaries."""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.content_dir = self.workspace_root / "content" / "components"
        
        # Standard delimiter patterns
        self.content_start = "<!-- CONTENT START -->"
        self.content_end = "<!-- CONTENT END -->"
        self.metadata_start = "<!-- METADATA START -->"
        self.metadata_end = "<!-- METADATA END -->"
        
        # Forbidden patterns in content sections
        self.forbidden_in_content = [
            r'ai_detection_analysis:',
            r'quality_analysis:',
            r'Version Log - Generated:',
            r'Component Version:',
            r'Generator: Z-Beam',
            r'Platform: Darwin',
            r'score: \d+\.\d+',
            r'provider: "winston"',
            r'optimization_iterations:',
            r'processing_time:',
            r'classification:',
            r'confidence:',
            r'overall_score:',
            r'formatting_score:',
            r'technical_score:',
            r'authenticity_score:',
            r'readability_score:',
            r'believability_score:',
            r'word_count:',
            r'author_country:',
            r'error_type:',
        ]
    
    def extract_content_section(self, file_content: str) -> Optional[str]:
        """Extract content section between delimiters."""
        pattern = rf'{re.escape(self.content_start)}\s*\n(.*?)\n\s*{re.escape(self.content_end)}'
        match = re.search(pattern, file_content, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        return None
    
    def extract_metadata_section(self, file_content: str) -> Optional[str]:
        """Extract metadata section between delimiters."""
        pattern = rf'{re.escape(self.metadata_start)}\s*\n(.*?)\n\s*{re.escape(self.metadata_end)}'
        match = re.search(pattern, file_content, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        return None
    
    def has_all_delimiters(self, content: str) -> bool:
        """Check if file has all required delimiters."""
        has_content_delimiters = (self.content_start in content and 
                                self.content_end in content)
        has_metadata_delimiters = (self.metadata_start in content and 
                                 self.metadata_end in content)
        
        # Allow files with only content delimiters if no metadata present
        return has_content_delimiters
    
    def validate_content_purity(self, content_section: str) -> List[str]:
        """Check if content section contains forbidden metadata patterns."""
        violations = []
        
        for pattern in self.forbidden_in_content:
            matches = re.finditer(pattern, content_section, re.IGNORECASE)
            for match in matches:
                line_num = content_section[:match.start()].count('\n') + 1
                violations.append(f"Line {line_num}: Found forbidden pattern '{pattern}' in content")
        
        return violations
    
    def validate_file(self, file_path: Path) -> Dict[str, any]:
        """Validate a single file's content boundaries."""
        result = {
            "file": str(file_path.relative_to(self.workspace_root)),
            "component_type": file_path.parent.name,
            "valid": True,
            "has_delimiters": False,
            "content_size": 0,
            "metadata_size": 0,
            "violations": [],
            "warnings": [],
            "error": None
        }
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            # Check for delimiters
            if not self.has_all_delimiters(file_content):
                result["valid"] = False
                result["violations"].append("Missing required content delimiters (CONTENT START/END)")
                return result
            
            result["has_delimiters"] = True
            
            # Extract sections
            content_section = self.extract_content_section(file_content)
            metadata_section = self.extract_metadata_section(file_content)
            
            if content_section is None:
                result["valid"] = False
                result["violations"].append("Could not extract content section")
                return result
            
            if metadata_section is None:
                result["warnings"].append("No metadata section found")
            else:
                result["metadata_size"] = len(metadata_section)
            
            result["content_size"] = len(content_section)
            
            # Validate content purity
            content_violations = self.validate_content_purity(content_section)
            if content_violations:
                result["valid"] = False
                result["violations"].extend(content_violations)
            
            # Component-specific validations
            component_warnings = self.validate_component_specific(
                file_path.parent.name, content_section, metadata_section
            )
            result["warnings"].extend(component_warnings)
            
        except Exception as e:
            result["valid"] = False
            result["error"] = str(e)
        
        return result
    
    def validate_component_specific(self, component_type: str, content: str, metadata: Optional[str]) -> List[str]:
        """Component-specific validation rules."""
        warnings = []
        
        if component_type == "text":
            # Text components should have substantial content
            if len(content) < 500:
                warnings.append(f"Text content seems short ({len(content)} chars)")
            
            # Should not have YAML frontmatter in content
            if content.strip().startswith('---'):
                warnings.append("Text content should not start with YAML frontmatter")
        
        elif component_type == "frontmatter":
            # Frontmatter should be valid YAML
            if not content.strip().startswith('---'):
                warnings.append("Frontmatter content should start with YAML delimiter")
        
        elif component_type == "jsonld":
            # Should contain JSON
            if '```json' not in content:
                warnings.append("JSON-LD content should contain JSON code block")
        
        elif component_type == "table":
            # Should contain markdown tables
            if '|' not in content:
                warnings.append("Table content should contain markdown table syntax")
        
        elif component_type == "tags":
            # Should be comma-separated
            if content and ',' not in content:
                warnings.append("Tags content should contain comma-separated values")
        
        return warnings
    
    def get_component_files(self, component_type: Optional[str] = None, 
                           file_path: Optional[str] = None) -> List[Path]:
        """Get list of component files to validate."""
        if file_path:
            # Single file
            file_path_obj = Path(file_path)
            if not file_path_obj.is_absolute():
                file_path_obj = self.workspace_root / file_path
            return [file_path_obj] if file_path_obj.exists() else []
        
        elif component_type and component_type != "all":
            # Specific component type
            component_dir = self.content_dir / component_type
            if not component_dir.exists():
                return []
            return list(component_dir.glob("*.md"))
        
        else:
            # All component types
            files = []
            for component_dir in self.content_dir.iterdir():
                if component_dir.is_dir():
                    files.extend(component_dir.glob("*.md"))
            return files
    
    def validate_components(self, component_type: Optional[str] = None, 
                           file_path: Optional[str] = None) -> Dict[str, any]:
        """Validate component files."""
        files_to_validate = self.get_component_files(component_type, file_path)
        
        results = {
            "total_files": len(files_to_validate),
            "valid_files": 0,
            "invalid_files": 0,
            "files_with_warnings": 0,
            "files_without_delimiters": 0,
            "total_violations": 0,
            "total_warnings": 0,
            "files": [],
            "summary": {}
        }
        
        print(f"Validating {len(files_to_validate)} files...")
        
        for file_path in files_to_validate:
            print(f"Validating: {file_path.name}", end="")
            
            file_result = self.validate_file(file_path)
            results["files"].append(file_result)
            
            if file_result["valid"]:
                results["valid_files"] += 1
                print(" ✓")
            else:
                results["invalid_files"] += 1
                print(" ✗")
            
            if not file_result["has_delimiters"]:
                results["files_without_delimiters"] += 1
            
            if file_result["warnings"]:
                results["files_with_warnings"] += 1
            
            results["total_violations"] += len(file_result["violations"])
            results["total_warnings"] += len(file_result["warnings"])
        
        # Generate summary by component type
        for file_result in results["files"]:
            comp_type = file_result["component_type"]
            if comp_type not in results["summary"]:
                results["summary"][comp_type] = {
                    "total": 0, "valid": 0, "invalid": 0, 
                    "without_delimiters": 0, "with_warnings": 0
                }
            
            stats = results["summary"][comp_type]
            stats["total"] += 1
            
            if file_result["valid"]:
                stats["valid"] += 1
            else:
                stats["invalid"] += 1
            
            if not file_result["has_delimiters"]:
                stats["without_delimiters"] += 1
            
            if file_result["warnings"]:
                stats["with_warnings"] += 1
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Validate content boundaries in component files"
    )
    
    parser.add_argument(
        "--component-type", 
        choices=["text", "frontmatter", "table", "tags", "jsonld", "metatags", 
                "bullets", "caption", "author", "badgesymbol", "propertiestable", "all"],
        help="Component type to validate (default: all)"
    )
    
    parser.add_argument(
        "--file-path",
        help="Validate a specific file (relative to workspace or absolute path)"
    )
    
    parser.add_argument(
        "--workspace",
        default="/Users/todddunning/Desktop/Z-Beam/z-beam-generator",
        help="Workspace root directory"
    )
    
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed violations and warnings for each file"
    )
    
    parser.add_argument(
        "--json-output",
        help="Save results as JSON to specified file"
    )
    
    args = parser.parse_args()
    
    # Validate workspace
    workspace_path = Path(args.workspace)
    if not workspace_path.exists():
        print(f"ERROR: Workspace not found: {workspace_path}")
        sys.exit(1)
    
    if not args.file_path:
        content_components_dir = workspace_path / "content" / "components"
        if not content_components_dir.exists():
            print(f"ERROR: Components directory not found: {content_components_dir}")
            sys.exit(1)
    
    # Initialize validator
    validator = ContentBoundaryValidator(args.workspace)
    
    # Show configuration
    print("="*80)
    print("Content Boundary Validation")
    print("="*80)
    print(f"Workspace: {args.workspace}")
    if args.file_path:
        print(f"File: {args.file_path}")
    else:
        print(f"Component Type: {args.component_type or 'all'}")
    print("="*80)
    
    # Run validation
    results = validator.validate_components(
        component_type=args.component_type,
        file_path=args.file_path
    )
    
    # Display results
    print("\n" + "="*80)
    print("VALIDATION RESULTS")
    print("="*80)
    print(f"Total Files: {results['total_files']}")
    print(f"Valid Files: {results['valid_files']}")
    print(f"Invalid Files: {results['invalid_files']}")
    print(f"Files Without Delimiters: {results['files_without_delimiters']}")
    print(f"Files With Warnings: {results['files_with_warnings']}")
    print(f"Total Violations: {results['total_violations']}")
    print(f"Total Warnings: {results['total_warnings']}")
    
    # Component type breakdown
    if not args.file_path:
        print("\nBy Component Type:")
        print("-"*70)
        print(f"{'Type':<15} | {'Total':>5} | {'Valid':>5} | {'Invalid':>7} | {'No Delim':>8} | {'Warnings':>8}")
        print("-"*70)
        for comp_type, stats in results["summary"].items():
            print(f"{comp_type:<15} | {stats['total']:>5} | {stats['valid']:>5} | "
                  f"{stats['invalid']:>7} | {stats['without_delimiters']:>8} | {stats['with_warnings']:>8}")
    
    # Show detailed results if requested
    if args.detailed or results["total_violations"] > 0:
        print("\nDETAILED RESULTS:")
        print("-"*80)
        
        for file_result in results["files"]:
            if not file_result["valid"] or file_result["warnings"]:
                print(f"\n{file_result['file']} ({file_result['component_type']})")
                
                if not file_result["valid"]:
                    print("  VIOLATIONS:")
                    for violation in file_result["violations"]:
                        print(f"    ✗ {violation}")
                
                if file_result["warnings"]:
                    print("  WARNINGS:")
                    for warning in file_result["warnings"]:
                        print(f"    ⚠ {warning}")
                
                if file_result["error"]:
                    print(f"  ERROR: {file_result['error']}")
                
                print(f"  Content Size: {file_result['content_size']} chars")
                print(f"  Metadata Size: {file_result['metadata_size']} chars")
    
    print("\n" + "="*80)
    
    # Overall status
    if results["invalid_files"] == 0:
        print("✓ ALL FILES VALID - Content boundaries properly defined")
    else:
        print(f"✗ {results['invalid_files']} FILES INVALID - See violations above")
        print("\nTo fix issues:")
        if results["files_without_delimiters"] > 0:
            print("  1. Run migration script: scripts/tools/migrate_to_delimited_metadata.py")
        if results["total_violations"] > results["files_without_delimiters"]:
            print("  2. Review and fix content purity violations")
    
    print("="*80)
    
    # Save JSON output if requested
    if args.json_output:
        with open(args.json_output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to: {args.json_output}")
    
    # Exit with error code if validation failed
    sys.exit(0 if results["invalid_files"] == 0 else 1)


if __name__ == "__main__":
    main()
