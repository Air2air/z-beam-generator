#!/usr/bin/env python3
"""
Batch Progress Monitor
===================

Simple monitor to check batch processing progress without interrupting the main process.
"""

import subprocess
from pathlib import Path

def check_progress():
    """Check how many materials have been processed"""
    try:
        # Run validation to see current status
        result = subprocess.run([
            'python3', 'validation/caption_integration_validator.py'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        lines = result.stdout.split('\n')
        for line in lines:
            if 'Processed' in line and 'files' in line:
                # Extract numbers from "📊 Processed 121 files"
                parts = line.split()
                if len(parts) >= 2:
                    processed = parts[1]
                    print(f"📊 Current validation shows {processed} files processed")
                    break
            
            if '✅ Valid:' in line:
                # Extract valid count
                parts = line.split()
                if len(parts) >= 2:
                    valid = parts[2]
                    print(f"✅ Currently valid: {valid}")
                    break
                    
    except Exception as e:
        print(f"❌ Error checking progress: {e}")

if __name__ == '__main__':
    print("🔍 Checking batch processing progress...")
    check_progress()