#!/usr/bin/env python3
"""
Script to fix all double dashes in existing content files.
"""

import os
import re
import glob
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_double_dashes_in_file(file_path):
    """Fix double dashes in image URLs within a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix double dashes in image URLs
        # Pattern matches: url: "/images/something--laser-cleaning-something.jpg"
        content = re.sub(
            r'((?:url|src):\s*["\']?/images/[a-zA-Z0-9-]+)--([a-zA-Z0-9-]+\.jpg["\']?)',
            r'\1-\2',
            content
        )
        
        # Also fix any remaining multiple consecutive dashes in image URLs
        content = re.sub(
            r'(/images/[a-zA-Z0-9-]*)-{2,}([a-zA-Z0-9-]*\.jpg)',
            r'\1-\2',
            content
        )
        
        # Check if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Fixed double dashes in {file_path}")
            return True
        return False
        
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return False

def main():
    """Find and fix double dashes in all content files."""
    # Get all markdown files in the content directory
    content_files = glob.glob('content/**/*.md', recursive=True)
    
    fixed_count = 0
    total_files = len(content_files)
    
    logger.info(f"Checking {total_files} content files for double dashes...")
    
    for file_path in content_files:
        if fix_double_dashes_in_file(file_path):
            fixed_count += 1
    
    logger.info(f"Fixed double dashes in {fixed_count} of {total_files} files.")
    
    # Verify no double dashes remain
    logger.info("Verifying no double dashes remain...")
    remaining_issues = []
    
    for file_path in content_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for any remaining double dashes in image URLs
            double_dash_matches = re.findall(r'/images/[^"\']*--[^"\']*\.jpg', content)
            if double_dash_matches:
                remaining_issues.append((file_path, double_dash_matches))
        except Exception as e:
            logger.error(f"Error verifying {file_path}: {e}")
    
    if remaining_issues:
        logger.warning(f"Still found double dashes in {len(remaining_issues)} files:")
        for file_path, matches in remaining_issues:
            logger.warning(f"  {file_path}: {matches}")
        return False
    else:
        logger.info("✅ No double dashes found in any content files!")
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
