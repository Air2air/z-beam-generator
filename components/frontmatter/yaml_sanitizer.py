#!/usr/bin/env python3
"""
Frontmatter-specific YAML sanitization utilities.

This module provides YAML sanitization functionality specifically designed for
frontmatter files in the laser cleaning content generation system.
"""

import re
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger(__name__)

class FrontmatterYAMLSanitizer:
    """YAML sanitization utilities for frontmatter files."""
    
    def __init__(self, frontmatter_dir: Optional[str] = None):
        """Initialize the sanitizer with frontmatter directory."""
        if frontmatter_dir is None:
            # Default to content/components/frontmatter relative to project root
            project_root = Path(__file__).parent.parent.parent
            frontmatter_dir = project_root / "content" / "components" / "frontmatter"
        
        self.frontmatter_dir = Path(frontmatter_dir)
        self.stats = {
            'files_processed': 0,
            'files_fixed': 0,
            'files_failed': 0,
            'errors_found': []
        }
    
    def sanitize_yaml_content(self, content: str) -> Tuple[str, List[str]]:
        """
        Sanitize YAML content in frontmatter format.
        
        Args:
            content: Raw file content with frontmatter
            
        Returns:
            Tuple of (sanitized_content, list_of_fixes_applied)
        """
        fixes_applied = []
        
        # Check if content starts with frontmatter
        if not content.startswith('---'):
            return content, fixes_applied
        
        # Split frontmatter from content
        parts = content.split('---', 2)
        
        # Handle case where frontmatter is missing closing ---
        if len(parts) < 3:
            # The entire content after the first --- is YAML
            yaml_content = parts[1] if len(parts) > 1 else ""
            markdown_content = ""
            fixes_applied.append("Added missing closing frontmatter delimiter")
        else:
            yaml_content = parts[1]
            markdown_content = parts[2] if len(parts) > 2 else ""
        
        # Apply YAML fixes
        original_yaml = yaml_content
        yaml_content = self._fix_yaml_structure(yaml_content, fixes_applied)
        
        # Reconstruct content with proper frontmatter delimiters
        if yaml_content != original_yaml or "Added missing closing frontmatter delimiter" in fixes_applied:
            sanitized_content = f"---{yaml_content}---{markdown_content}"
        else:
            sanitized_content = content
        
        return sanitized_content, fixes_applied
    
    def _fix_yaml_structure(self, yaml_content: str, fixes_applied: List[str]) -> str:
        """Fix common YAML structure issues in frontmatter."""
        
        # Fix 1: Multiple key-value pairs on the same line (most common issue)
        # Split by lines and process each one
        lines = yaml_content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Check for multiple key-value pairs on the same line
            # Pattern: "key1: value1  key2: value2"
            pattern = r'^(\s*)(\w+):\s*([^\s:]+)\s\s+(\w+):\s*(.+)$'
            match = re.match(pattern, line)
            
            if match:
                indent, key1, value1, key2, value2 = match.groups()
                # Split into two lines with proper indentation
                fixed_lines.append(f"{indent}{key1}: {value1}")
                fixed_lines.append(f"{indent}{key2}: {value2}")
                if "Separated multiple key-value pairs on same line" not in fixes_applied:
                    fixes_applied.append("Separated multiple key-value pairs on same line")
            else:
                fixed_lines.append(line)
        
        yaml_content = '\n'.join(fixed_lines)
        
        # Fix 2: Remove extra quotes around numeric values
        pattern = r'(\s+\w+):\s*"(\d+(?:\.\d+)?)"'
        if re.search(pattern, yaml_content):
            yaml_content = re.sub(pattern, r'\1: \2', yaml_content)
            fixes_applied.append("Removed quotes from numeric values")
        
        # Fix 3: Fix colons in values (quote them)
        # Common patterns like "Nd: YAG laser" need to be quoted
        lines = yaml_content.split('\n')
        fixed_lines = []
        for line in lines:
            # Look for key-value pairs where the value contains a colon but isn't quoted
            pattern = r'^(\s*)(\w+):\s*([^"\']*:\s*[^"\']+)$'
            match = re.match(pattern, line)
            if match:
                indent, key, value = match.groups()
                # Quote the value to prevent YAML from treating it as a mapping
                fixed_line = f'{indent}{key}: "{value.strip()}"'
                fixed_lines.append(fixed_line)
                if "Fixed colons in unquoted values" not in fixes_applied:
                    fixes_applied.append("Fixed colons in unquoted values")
            else:
                fixed_lines.append(line)
        yaml_content = '\n'.join(fixed_lines)
        
        # Fix 4: Fix spacing issues around colons in key-value pairs
        # Handle cases like "key:value" -> "key: value"
        pattern = r'(\w+):(\S)'
        if re.search(pattern, yaml_content):
            yaml_content = re.sub(pattern, r'\1: \2', yaml_content)
            fixes_applied.append("Fixed spacing around colons")
        
        # Fix 5: Fix malformed density values and other quotes issues
        lines = yaml_content.split('\n')
        fixed_lines = []
        for line in lines:
            # Fix lines like: density: "600 - 800 kg/m³"
            if 'density:' in line and '"' in line:
                # Remove extra quotes and fix format
                if line.count('"') > 2:
                    # Malformed quotes
                    line = re.sub(r'density:\s*"([^"]+)"[^"]*"?', r'density: "\1"', line)
                    if "Fixed malformed density values" not in fixes_applied:
                        fixes_applied.append("Fixed malformed density values")
            fixed_lines.append(line)
        yaml_content = '\n'.join(fixed_lines)
        
        # Fix 5: Handle multiline chemical formulas that broke YAML structure
        lines = yaml_content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                fixed_lines.append(line)
                i += 1
                continue
            
            # Check if this looks like a continuation of a chemical formula
            if (i > 0 and 
                line.startswith('      ') and  # Deeply indented
                ':' not in stripped and  # No colon (not a key-value pair)
                (any(char in stripped for char in ['₁', '₂', '₃', '₄', '₅', '₆', '₇', '₈', '₉', '₀']) or
                 any(formula in stripped.lower() for formula in ['cao', 'sio', 'al2o3', 'h2o', 'oh']))):
                
                # This is likely a broken chemical formula - append to previous line
                if fixed_lines:
                    prev_line = fixed_lines[-1]
                    if prev_line.strip().endswith('"'):
                        # Remove the closing quote, append content, add quote back
                        prev_content = prev_line.rstrip()[:-1]  # Remove last quote
                        combined = f'{prev_content}{stripped}"'
                        fixed_lines[-1] = combined
                    else:
                        # Just append with space
                        fixed_lines[-1] = f"{prev_line.rstrip()} {stripped}"
                    if "Fixed broken chemical formula continuation" not in fixes_applied:
                        fixes_applied.append("Fixed broken chemical formula continuation")
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
            
            i += 1
        
        yaml_content = '\n'.join(fixed_lines)
        
        # Fix 6: Remove trailing whitespace
        lines = yaml_content.split('\n')
        clean_lines = [line.rstrip() for line in lines]
        if clean_lines != lines:
            yaml_content = '\n'.join(clean_lines)
            fixes_applied.append("Removed trailing whitespace")
        
        return yaml_content
    
    def _fix_indentation(self, yaml_content: str, fixes_applied: List[str]) -> str:
        """Fix indentation issues in YAML content."""
        lines = yaml_content.split('\n')
        fixed_lines = []
        indent_stack = []
        
        for line in lines:
            stripped = line.lstrip()
            if not stripped or stripped.startswith('#'):
                fixed_lines.append(line)
                continue
            
            # Calculate current indentation
            current_indent = len(line) - len(stripped)
            
            # Check if this is a key-value pair
            if ':' in stripped and not stripped.startswith('-'):
                # This is a key, maintain consistent indentation
                if indent_stack and current_indent % 2 != 0:
                    # Fix odd indentation to even
                    corrected_indent = (current_indent // 2) * 2
                    fixed_line = ' ' * corrected_indent + stripped
                    fixed_lines.append(fixed_line)
                    if "Fixed indentation" not in fixes_applied:
                        fixes_applied.append("Fixed indentation alignment")
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def validate_yaml(self, yaml_content: str) -> Tuple[bool, Optional[str]]:
        """
        Validate YAML content can be parsed.
        
        Args:
            yaml_content: YAML content to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            yaml.safe_load(yaml_content)
            return True, None
        except yaml.YAMLError as e:
            return False, str(e)
    
    def sanitize_file(self, file_path: Path, dry_run: bool = False) -> Dict[str, Any]:
        """
        Sanitize a single frontmatter file.
        
        Args:
            file_path: Path to the frontmatter file
            dry_run: If True, don't write changes to disk
            
        Returns:
            Dictionary with sanitization results
        """
        result = {
            'file': str(file_path),
            'success': False,
            'fixes_applied': [],
            'error': None,
            'needs_fixing': False
        }
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Sanitize content
            sanitized_content, fixes_applied = self.sanitize_yaml_content(content)
            
            result['fixes_applied'] = fixes_applied
            result['needs_fixing'] = len(fixes_applied) > 0
            
            if fixes_applied and not dry_run:
                # Write sanitized content back to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(sanitized_content)
                logger.info(f"Sanitized {file_path.name}: {', '.join(fixes_applied)}")
            
            # Validate the final YAML
            if content.startswith('---'):
                parts = sanitized_content.split('---', 2)
                if len(parts) >= 2:
                    yaml_part = parts[1]
                    is_valid, error = self.validate_yaml(yaml_part)
                    if not is_valid:
                        result['error'] = f"YAML validation failed: {error}"
                        return result
            
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Failed to sanitize {file_path}: {e}")
        
        return result
    
    def sanitize_all_files(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Sanitize all frontmatter files in the directory.
        
        Args:
            dry_run: If True, don't write changes to disk
            
        Returns:
            Summary of sanitization results
        """
        logger.info(f"Starting frontmatter sanitization in {self.frontmatter_dir}")
        logger.info(f"Dry run mode: {dry_run}")
        
        results = []
        
        # Find all frontmatter files
        pattern = "*-laser-cleaning.md"
        frontmatter_files = list(self.frontmatter_dir.glob(pattern))
        
        if not frontmatter_files:
            logger.warning(f"No frontmatter files found matching {pattern}")
            return {
                'total_files': 0,
                'files_processed': 0,
                'files_fixed': 0,
                'files_failed': 0,
                'results': []
            }
        
        logger.info(f"Found {len(frontmatter_files)} frontmatter files to process")
        
        for file_path in frontmatter_files:
            result = self.sanitize_file(file_path, dry_run)
            results.append(result)
            
            self.stats['files_processed'] += 1
            if result['success']:
                if result['needs_fixing']:
                    self.stats['files_fixed'] += 1
            else:
                self.stats['files_failed'] += 1
                self.stats['errors_found'].append({
                    'file': str(file_path),
                    'error': result['error']
                })
        
        summary = {
            'total_files': len(frontmatter_files),
            'files_processed': self.stats['files_processed'],
            'files_fixed': self.stats['files_fixed'],
            'files_failed': self.stats['files_failed'],
            'results': results
        }
        
        # Log summary
        logger.info("Sanitization complete:")
        logger.info(f"  Files processed: {summary['files_processed']}")
        logger.info(f"  Files fixed: {summary['files_fixed']}")
        logger.info(f"  Files failed: {summary['files_failed']}")
        
        if self.stats['errors_found']:
            logger.error("Errors encountered:")
            for error in self.stats['errors_found']:
                logger.error(f"  {error['file']}: {error['error']}")
        
        return summary


def main():
    """Command-line interface for frontmatter YAML sanitization."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sanitize YAML in frontmatter files")
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be fixed without making changes')
    parser.add_argument('--frontmatter-dir', type=str,
                       help='Path to frontmatter directory (default: auto-detect)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create sanitizer
    sanitizer = FrontmatterYAMLSanitizer(args.frontmatter_dir)
    
    # Run sanitization
    summary = sanitizer.sanitize_all_files(dry_run=args.dry_run)
    
    # Print results
    print("\n🧹 Frontmatter YAML Sanitization Results:")
    print(f"   Files processed: {summary['files_processed']}")
    print(f"   Files fixed: {summary['files_fixed']}")
    print(f"   Files failed: {summary['files_failed']}")
    
    if args.dry_run and summary['files_fixed'] > 0:
        print(f"\n💡 Run without --dry-run to apply {summary['files_fixed']} fixes")
    
    if summary['files_failed'] > 0:
        print(f"\n❌ {summary['files_failed']} files had errors - check logs for details")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
