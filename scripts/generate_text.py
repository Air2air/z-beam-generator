#!/usr/bin/env python3
"""
Generate Text Content - Frontmatter Generation

Uses Grok AI to generate high-quality text content for frontmatter fields.
Updates text fields (subtitle, description, notes) while preserving data.

Usage:
    python3 scripts/generate_text.py Aluminum
    python3 scripts/generate_text.py Steel --force-refresh
    python3 scripts/generate_text.py --all --dry-run
"""

import sys
import subprocess
from pathlib import Path

def main():
    # Get script directory
    script_dir = Path(__file__).parent
    hybrid_cli = script_dir / "hybrid_frontmatter_cli.py"
    
    # Build command with hybrid mode (data + text generation)
    cmd = [
        sys.executable,
        str(hybrid_cli),
        "--mode", "hybrid"  # Best balance: data from YAML + Grok text
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
        print("Usage: python3 scripts/generate_text.py <material_name>")
        print("       python3 scripts/generate_text.py --all")
        return 1
    
    # Execute the hybrid CLI with hybrid mode
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n⚠️  Text generation interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error running text generation: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())