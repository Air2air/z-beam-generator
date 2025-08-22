#!/usr/bin/env python3
"""
Fix YAML formatting issues in frontmatter files.

Issues to fix:
1. Double opening delimiters (--- at the beginning)
2. Empty object placeholders ({})
3. Malformed nested structures
4. Duplicate field names
"""

import re
import yaml
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_yaml_content(content: str) -> str:
    """Fix YAML formatting issues in content."""
    
    # Fix 1: Remove double delimiters at the beginning
    if content.startswith('---\n---\n'):
        content = content[4:]  # Remove first '---\n'
        logger.info("Fixed double opening delimiters")
    
    # Fix 2: Remove empty object placeholders
    content = re.sub(r':\s*\{\}\s*\n', ':\n', content)
    content = re.sub(r':\s*\{\}$', ':', content, flags=re.MULTILINE)
    
    # Fix 3: Fix malformed nested structures like "components: components: {}"
    content = re.sub(r'(\w+):\s*\n\s*\1:\s*\{\}', r'\1:', content)
    content = re.sub(r'(\w+):\s*\n\s*(\w+):\s*\n\s*\2:\s*\{\}', r'\1:\n  \2:', content)
    
    # Fix 4: Remove duplicate field names that appear back-to-back
    lines = content.split('\n')
    fixed_lines = []
    prev_field = None
    
    for line in lines:
        # Check if line is a field definition
        field_match = re.match(r'^(\s*)(\w+):\s*$', line)
        if field_match:
            indent, field_name = field_match.groups()
            if field_name != prev_field:
                fixed_lines.append(line)
                prev_field = field_name
            else:
                logger.info(f"Removed duplicate field: {field_name}")
        else:
            fixed_lines.append(line)
            if line.strip():  # Reset field tracking on non-empty, non-field lines
                prev_field = None
    
    content = '\n'.join(fixed_lines)
    
    # Fix 5: Clean up empty lines and trailing whitespace
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)  # Multiple empty lines to double
    content = re.sub(r' +$', '', content, flags=re.MULTILINE)  # Trailing spaces
    
    return content

def validate_yaml_structure(content: str) -> tuple[bool, str]:
    """Validate YAML structure and return success status with error message."""
    try:
        # Extract YAML frontmatter
        if not content.startswith('---'):
            return False, "Missing opening delimiter"
        
        end_marker = content.find('---', 3)
        if end_marker == -1:
            return False, "Missing closing delimiter"
        
        yaml_content = content[3:end_marker].strip()
        parsed = yaml.safe_load(yaml_content)
        
        if not parsed:
            return False, "Empty YAML content"
        
        return True, "Valid YAML"
        
    except yaml.YAMLError as e:
        return False, f"YAML parsing error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"

def fix_frontmatter_file(file_path: Path) -> bool:
    """Fix a single frontmatter file."""
    try:
        logger.info(f"Processing: {file_path.name}")
        
        # Read original content
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Validate original
        is_valid, error_msg = validate_yaml_structure(original_content)
        if is_valid:
            logger.info(f"✅ Already valid: {file_path.name}")
            return True
        
        logger.warning(f"❌ Issues found: {error_msg}")
        
        # Apply fixes
        fixed_content = fix_yaml_content(original_content)
        
        # Validate fixed content
        is_valid_fixed, fixed_error = validate_yaml_structure(fixed_content)
        
        if is_valid_fixed:
            # Write fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            logger.info(f"✅ Fixed and saved: {file_path.name}")
            return True
        else:
            logger.error(f"❌ Still invalid after fixes: {fixed_error}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error processing {file_path.name}: {e}")
        return False

def main():
    """Main function to fix all frontmatter files."""
    frontmatter_dir = Path("content/components/frontmatter")
    
    if not frontmatter_dir.exists():
        logger.error(f"Directory not found: {frontmatter_dir}")
        return
    
    # Find all markdown files
    md_files = list(frontmatter_dir.glob("*.md"))
    
    if not md_files:
        logger.warning("No markdown files found in frontmatter directory")
        return
    
    logger.info(f"Found {len(md_files)} frontmatter files to process")
    
    fixed_count = 0
    failed_count = 0
    
    for md_file in sorted(md_files):
        if fix_frontmatter_file(md_file):
            fixed_count += 1
        else:
            failed_count += 1
    
    logger.info("\n📊 Summary:")
    logger.info(f"✅ Successfully processed: {fixed_count}")
    logger.info(f"❌ Failed to fix: {failed_count}")
    logger.info(f"📁 Total files: {len(md_files)}")

if __name__ == "__main__":
    main()
