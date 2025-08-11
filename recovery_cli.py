#!/usr/bin/env python3
"""
Recovery CLI Entry Point

Main entry point for the recovery system CLI.
This provides a simple interface that works from the project root.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from recovery.cli import main

if __name__ == "__main__":
    main()
