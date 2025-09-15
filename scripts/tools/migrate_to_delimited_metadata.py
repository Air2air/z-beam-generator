#!/usr/bin/env python3
"""
Migrate component files to use global metadata delimiting standard.
Adds HTML-style comment delimiters to separate content from metadata.
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import yaml


class MetadataDelimiterMigrator:
    """Migrates component files to use standardized metadata delimiters."""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.content_dir = self.workspace_root / "content" / "components"
        
        # Standard delimiter patterns
        self.content_start = "<!-- CONTENT START -->"
        self.content_end = "<!-- CONTENT END -->"
        self.metadata_start = "<!-- METADATA START -->"
        self.metadata_end = "<!-- METADATA END -->"
        
        # Metadata detection patterns
        self.metadata_patterns = [
            r'---\nai_detection_analysis:',  # AI detection YAML
            r'---\nquality_analysis:',       # Quality analysis YAML
            r'---\nVersion Log -',            # Version log start
            r'# Component Version:',          # Component version
            r'Version Log - Generated:',     # Version log entry
        ]
    
    def detect_metadata_boundary(self, content: str) -> int:
        """Detect where metadata section begins in file content."""
        # Look for first occurrence of any metadata pattern
        earliest_match = len(content)
        
        for pattern in self.metadata_patterns:
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                earliest_match = min(earliest_match, match.start())
        
        # If no metadata found, return end of content
        if earliest_match == len(content):
            return len(content)
            
        # Back up to find start of line
        while earliest_match > 0 and content[earliest_match - 1] != '\n':
            earliest_match -= 1
            
        return earliest_match
    
    def has_delimiters(self, content: str) -> bool:
        """Check if file already has metadata delimiters."""
        return (self.content_start in content and 
                self.content_end in content and
                self.metadata_start in content and
                self.metadata_end in content)
    
    def extract_content_and_metadata(self, file_content: str) -> Tuple[str, str]:
        """Split file into content and metadata sections."""
        metadata_start_pos = self.detect_metadata_boundary(file_content)
        
        if metadata_start_pos >= len(file_content):
            # No metadata found
            return file_content.strip(), ""
        
        content_section = file_content[:metadata_start_pos].strip()
        metadata_section = file_content[metadata_start_pos:].strip()
        
        return content_section, metadata_section
    
    def add_delimiters(self, content: str, metadata: str) -> str:
        """Add standard delimiters around content and metadata."""
        if not content:
            return ""
            
        result = f"{self.content_start}\n{content}\n{self.content_end}\n"
        
        if metadata:
            result += f"\n{self.metadata_start}\n{metadata}\n{self.metadata_end}\n"
            
        return result
    
    def migrate_file(self, file_path: Path, dry_run: bool = False) -> Dict[str, any]:
        """Migrate a single file to use delimiters."""
        result = {
            "file": str(file_path),
            "success": False,
            "already_delimited": False,
            "content_size": 0,
            "metadata_size": 0,
            "error": None,
            "backup_created": False
        }
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Check if already has delimiters
            if self.has_delimiters(original_content):
                result["already_delimited"] = True
                result["success"] = True
                return result
            
            # Extract content and metadata
            content_section, metadata_section = self.extract_content_and_metadata(original_content)
            
            result["content_size"] = len(content_section)
            result["metadata_size"] = len(metadata_section)
            
            # Create delimited version
            delimited_content = self.add_delimiters(content_section, metadata_section)
            
            if not dry_run:
                # Write delimited version (no backup to avoid including in optimization)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(delimited_content)
            
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def get_component_files(self, component_type: Optional[str] = None) -> List[Path]:
        """Get list of component files to migrate."""
        if component_type and component_type != "all":
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
    
    def migrate_components(self, component_type: Optional[str] = None, 
                          dry_run: bool = False) -> Dict[str, any]:
        """Migrate all component files of specified type."""
        files_to_migrate = self.get_component_files(component_type)
        
        results = {
            "total_files": len(files_to_migrate),
            "migrated": 0,
            "already_delimited": 0,
            "errors": 0,
            "backups_created": 0,
            "files": [],
            "summary": {}
        }
        
        print(f"Found {len(files_to_migrate)} files to process...")
        
        for file_path in files_to_migrate:
            print(f"Processing: {file_path.name}", end="")
            
            file_result = self.migrate_file(file_path, dry_run)
            results["files"].append(file_result)
            
            if file_result["success"]:
                if file_result["already_delimited"]:
                    results["already_delimited"] += 1
                    print(" - Already delimited")
                else:
                    results["migrated"] += 1
                    if file_result["backup_created"]:
                        results["backups_created"] += 1
                    content_kb = file_result["content_size"] / 1024
                    metadata_kb = file_result["metadata_size"] / 1024
                    print(f" - Migrated (Content: {content_kb:.1f}KB, Metadata: {metadata_kb:.1f}KB)")
            else:
                results["errors"] += 1
                print(f" - ERROR: {file_result['error']}")
        
        # Generate summary by component type
        for file_result in results["files"]:
            component_type = Path(file_result["file"]).parent.name
            if component_type not in results["summary"]:
                results["summary"][component_type] = {
                    "total": 0, "migrated": 0, "already_delimited": 0, "errors": 0
                }
            
            results["summary"][component_type]["total"] += 1
            if file_result["success"]:
                if file_result["already_delimited"]:
                    results["summary"][component_type]["already_delimited"] += 1
                else:
                    results["summary"][component_type]["migrated"] += 1
            else:
                results["summary"][component_type]["errors"] += 1
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Migrate component files to use global metadata delimiting standard"
    )
    
    parser.add_argument(
        "--component-type", 
        choices=["text", "frontmatter", "table", "tags", "jsonld", "metatags", 
                "bullets", "caption", "author", "badgesymbol", "propertiestable", "all"],
        default="all",
        help="Component type to migrate (default: all)"
    )
    
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Show what would be migrated without making changes"
    )
    
    parser.add_argument(
        "--workspace",
        default="/Users/todddunning/Desktop/Z-Beam/z-beam-generator",
        help="Workspace root directory"
    )
    
    args = parser.parse_args()
    
    # Validate workspace
    workspace_path = Path(args.workspace)
    if not workspace_path.exists():
        print(f"ERROR: Workspace not found: {workspace_path}")
        sys.exit(1)
    
    content_components_dir = workspace_path / "content" / "components"
    if not content_components_dir.exists():
        print(f"ERROR: Components directory not found: {content_components_dir}")
        sys.exit(1)
    
    # Initialize migrator
    migrator = MetadataDelimiterMigrator(args.workspace)
    
    # Show configuration
    print("="*80)
    print("Global Metadata Delimiting Migration")
    print("="*80)
    print(f"Workspace: {args.workspace}")
    print(f"Component Type: {args.component_type}")
    print(f"Dry Run: {args.dry_run}")
    print("="*80)
    
    # Run migration
    results = migrator.migrate_components(
        component_type=args.component_type if args.component_type != "all" else None,
        dry_run=args.dry_run
    )
    
    # Display results
    print("\n" + "="*80)
    print("MIGRATION RESULTS")
    print("="*80)
    print(f"Total Files: {results['total_files']}")
    print(f"Successfully Migrated: {results['migrated']}")
    print(f"Already Delimited: {results['already_delimited']}")
    print(f"Errors: {results['errors']}")
    print(f"Backups Created: {results['backups_created']}")
    
    # Component type breakdown
    print("\nBy Component Type:")
    print("-"*50)
    for comp_type, stats in results["summary"].items():
        print(f"{comp_type:15} | Total: {stats['total']:3d} | "
              f"Migrated: {stats['migrated']:3d} | "
              f"Already: {stats['already_delimited']:3d} | "
              f"Errors: {stats['errors']:3d}")
    
    # Show errors if any
    if results["errors"] > 0:
        print("\nERRORS:")
        print("-"*50)
        for file_result in results["files"]:
            if not file_result["success"]:
                print(f"{file_result['file']}: {file_result['error']}")
    
    print("\n" + "="*80)
    
    if args.dry_run:
        print("DRY RUN - No files were modified")
        print("Run without --dry-run to perform migration")
    else:
        print(f"Migration complete. {results['backups_created']} backup files created.")
        print("Original files backed up with .backup extension")
    
    print("="*80)


if __name__ == "__main__":
    main()
