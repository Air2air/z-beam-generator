#!/usr/bin/env python3
"""
Quick Data Refresh - Frontmatter Generation

Fast command to refresh non-text data from Materials.yaml without AI calls.
Perfect for frequent data updates when you don't need text regeneration.

Usage:
    python3 scripts/refresh_data.py Aluminum
    python3 scripts/refresh_data.py Steel --dry-run
    python3 scripts/refresh_data.py --all
"""

import sys
import subprocess
from pathlib import Path

def main():
    # Get script directory
    script_dir = Path(__file__).parent
    hybrid_cli = script_dir / "hybrid_frontmatter_cli.py"
    
    # Build command with data-only mode
    cmd = [
        sys.executable,
        str(hybrid_cli),
        "--mode", "data-only"
    ]
    
    # Pass through all arguments
    if len(sys.argv) > 1:
        # Handle special case of material name without --material flag
        if sys.argv[1] not in ['--all', '--dry-run', '--verbose', '--force-refresh', '--help', '-h', '-a', '-n', '-v', '-f']:
            cmd.extend(["--material", sys.argv[1]])
            # Add any remaining arguments
            cmd.extend(sys.argv[2:])
        else:
            cmd.extend(sys.argv[1:])
    else:
        print("❌ Error: Material name or --all required")
        print("Usage: python3 scripts/refresh_data.py <material_name>")
        print("       python3 scripts/refresh_data.py --all")
        return 1
    
    # Execute the hybrid CLI with data-only mode
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n⚠️  Data refresh interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error running data refresh: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())