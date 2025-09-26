#!/usr/bin/env python3
"""
Clean up legacy field references in test files.

This script removes references to materialProperties and laserProcessing
that are no longer valid after field consolidation.
"""

import re
from pathlib import Path


def clean_test_file(file_path):
    """Clean legacy references from a test file"""
    print(f"Processing {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Remove materialProperties test methods
        content = re.sub(
            r'def test_.*materialProperties.*?(?=\n    def|\nclass|\nif __name__|\Z)',
            '', 
            content, 
            flags=re.DOTALL
        )
        
        # Remove laserProcessing test methods
        content = re.sub(
            r'def test_.*laserProcessing.*?(?=\n    def|\nclass|\nif __name__|\Z)',
            '', 
            content, 
            flags=re.DOTALL
        )
        
        # Update field lists to remove legacy references
        content = re.sub(
            r'[\'"]materialProperties[\'"],?\s*',
            '',
            content
        )
        
        content = re.sub(
            r'[\'"]laserProcessing[\'"],?\s*',
            '',
            content
        )
        
        # Clean up test data structures with legacy fields
        # Remove materialProperties test data blocks
        content = re.sub(
            r'"materialProperties":\s*{[^}]*(?:{[^}]*}[^}]*)*},?\s*',
            '',
            content,
            flags=re.MULTILINE
        )
        
        # Remove laserProcessing test data blocks  
        content = re.sub(
            r'"laserProcessing":\s*{[^}]*(?:{[^}]*}[^}]*)*},?\s*',
            '',
            content,
            flags=re.MULTILINE
        )
        
        # Remove assertions that check for legacy fields
        content = re.sub(
            r'.*assertIn.*[\'"]materialProperties[\'"].*\n?',
            '',
            content
        )
        
        content = re.sub(
            r'.*assertIn.*[\'"]laserProcessing[\'"].*\n?',
            '',
            content
        )
        
        # Clean up empty lines and formatting
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Updated {file_path}")
            return True
        else:
            print(f"  ✅ No changes needed in {file_path}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False


def main():
    """Main function to clean up all test files"""
    test_dirs = [
        "components/frontmatter/tests",
        "tests/frontmatter",
        "components/caption/testing",
        "tests"
    ]
    
    updated_count = 0
    processed_count = 0
    
    for test_dir in test_dirs:
        test_path = Path(test_dir)
        if test_path.exists():
            for file_path in test_path.glob("**/*.py"):
                processed_count += 1
                if clean_test_file(file_path):
                    updated_count += 1
    
    print("\n🎉 Processing complete!")
    print(f"✅ Updated {updated_count} files")
    print(f"📁 Total files processed: {processed_count}")


if __name__ == "__main__":
    main()