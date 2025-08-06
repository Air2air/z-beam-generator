#!/usr/bin/env python3
"""
Script to remove HTML comments from the beginning of all generated files.
"""

import os
import re
import glob

def remove_html_comments(directory):
    """Remove HTML comments from all files in the specified directory."""
    # Find all markdown files in the directory and its subdirectories
    files = glob.glob(f"{directory}/**/*.md", recursive=True)
    
    # HTML comment pattern to match
    pattern = re.compile(r'^<!--.*?-->\n', re.DOTALL)
    
    # Counter for modified files
    modified_count = 0
    
    for file_path in files:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if there's an HTML comment at the beginning
        match = pattern.match(content)
        if match:
            # Remove the comment
            new_content = pattern.sub('', content)
            
            # Write the modified content back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            modified_count += 1
            print(f"Removed HTML comment from {file_path}")
    
    return modified_count

if __name__ == "__main__":
    # Directory containing generated files
    components_dir = "/Users/todddunning/Desktop/Z-Beam/z-beam-generator/content/components"
    
    # Remove HTML comments
    modified_count = remove_html_comments(components_dir)
    
    print(f"\nCompleted: Removed HTML comments from {modified_count} files.")
