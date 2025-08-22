#!/usr/bin/env python3
"""
Z-Beam Generator - Simplified Entry Point

This script has been simplified. All functionality has been moved to run.py.

USAGE:
    python3 run.py                          # Interactive generation mode
    python3 run.py --start-from "Copper"    # Start from specific material
    python3 run.py --yaml                   # Validate and fix YAML errors

This file now serves as a redirect to the new simplified interface.
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Redirect to the new simplified run.py interface."""
    print("🔄 Z-Beam Generator has been simplified!")
    print("   All functionality has been moved to run.py")
    print("")
    print("📖 Available commands:")
    print("   python3 run.py                          # Interactive generation") 
    print("   python3 run.py --start-from 'Copper'    # Start from specific material")
    print("   python3 run.py --yaml                   # Validate and fix YAML")
    print("")
    
    # If help requested, show run.py help
    if "--help" in sys.argv or "-h" in sys.argv:
        print("🚀 Showing run.py help:")
        print("=" * 50)
        
        # Show run.py help
        script_dir = Path(__file__).parent
        run_script = script_dir / "run.py"
        cmd = [sys.executable, str(run_script), "--help"]
        subprocess.run(cmd, cwd=script_dir)
        return
    
    print("🚀 Running interactive mode...")
    print("=" * 50)
    
    # Redirect to run.py with all arguments
    script_dir = Path(__file__).parent
    run_script = script_dir / "run.py"
    
    if not run_script.exists():
        print("❌ Error: run.py not found!")
        sys.exit(1)
    
    # Pass all arguments to run.py
    cmd = [sys.executable, str(run_script)] + sys.argv[1:]
    
    try:
        result = subprocess.run(cmd, cwd=script_dir)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n🛑 Operation interrupted.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
