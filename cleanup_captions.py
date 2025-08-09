#!/usr/bin/env python3

import os
import re
import glob

def cleanup_caption_file(file_path):
    """Clean up any formatting issues in caption files."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix extra asterisks
        content = re.sub(r'\*{3,}', '**', content)
        
        # Ensure proper spacing after punctuation
        content = re.sub(r'(\w),(\w)', r'\1, \2', content)
        content = re.sub(r'(\w)\.(\w)', r'\1. \2', content)
        
        # Fix missing commas before "showing"
        content = re.sub(r'(\d+\s*µm\s+spot\s+size)\s+(showing)', r'\1, \2', content)
        
        # Clean up extra whitespace
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = content.strip()
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Cleaned up: {os.path.basename(file_path)}")
            return True
        return False
            
    except Exception as e:
        print(f"Error cleaning {os.path.basename(file_path)}: {e}")
        return False

def main():
    caption_dir = "content/components/caption"
    pattern = os.path.join(caption_dir, "*.md")
    files = glob.glob(pattern)
    
    print("Cleaning up caption formatting issues...")
    print("=" * 50)
    
    cleaned_count = 0
    for file_path in sorted(files):
        if cleanup_caption_file(file_path):
            cleaned_count += 1
    
    print("=" * 50)
    print(f"Cleaned up {cleaned_count} caption files")

if __name__ == "__main__":
    main()
