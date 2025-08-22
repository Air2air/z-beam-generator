#!/usr/bin/env python3
"""
Z-Beam Test Suite Runner

Simple wrapper to run the test suite from the project root.
This maintains backward compatibility while using the new organized test structure.

Usage:
    python3 test.py              # Run core tests (default)
    python3 test.py --test       # Run core tests (explicit)
    python3 test.py --performance # Run performance tests only
    python3 test.py --all        # Run all tests

Or use the module directly:
    python3 -m tests             # Run core tests (default)
    python3 -m tests --performance # Run performance tests only
    python3 -m tests --all       # Run all tests
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Forward all arguments to the tests module"""
    try:
        # Run the tests module with all provided arguments
        cmd = [sys.executable, "-m", "tests"] + sys.argv[1:]
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
