#!/usr/bin/env python3
"""
Batch Monitor and Copy Script
Monitors the batch tags generation and copies files when complete.
"""

import os
import shutil
import time
import subprocess
from pathlib import Path

def is_batch_complete():
    """Check if the batch process is still running"""
    try:
        # Check if the python process is still running
        result = subprocess.run(
            ["pgrep", "-f", "batch_tags_generation.py"],
            capture_output=True,
            text=True
        )
        return result.returncode != 0  # Returns True if no process found (batch complete)
    except:
        return True  # Assume complete if can't check

def copy_tags_directory():
    """Copy the tags directory to the test-push location"""
    source_dir = Path("/Users/todddunning/Desktop/Z-Beam/z-beam-generator/content/components/tags")
    target_dir = Path("/Users/todddunning/Desktop/Z-Beam/z-beam-test-push/content/components/tags")
    
    try:
        # Create target directory structure
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        
        # Remove existing target directory if it exists
        if target_dir.exists():
            shutil.rmtree(target_dir)
        
        # Copy the entire tags directory
        shutil.copytree(source_dir, target_dir)
        
        # Count files copied
        file_count = len(list(target_dir.glob("*.md")))
        
        print(f"✅ Successfully copied {file_count} tag files to test-push location")
        print(f"📁 Source: {source_dir}")
        print(f"📁 Target: {target_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error copying files: {e}")
        return False

def main():
    """Monitor batch completion and copy files"""
    print("🔍 Monitoring batch tags generation...")
    
    while True:
        if is_batch_complete():
            print("🎉 Batch generation complete! Starting file copy...")
            
            # Wait a moment to ensure all files are written
            time.sleep(2)
            
            if copy_tags_directory():
                print("✨ Copy operation completed successfully!")
                break
            else:
                print("⚠️ Copy operation failed. Retrying in 10 seconds...")
                time.sleep(10)
        else:
            print("⏳ Batch still running... checking again in 30 seconds")
            time.sleep(30)

if __name__ == "__main__":
    main()
