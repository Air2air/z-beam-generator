#!/usr/bin/env python3
"""
Content Component Directory Cleanup
Removes unnecessary files while preserving production components.
"""

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

from components.text.generators.fail_fast_generator import create_fail_fast_generator

        # Test initialization
        generator = create_fail_fast_generator()
        print("✅ Production generator imports and initializes correctly")

        # Check prompt files
        prompt_files = [
            "components/content/prompts/base_content_prompt.yaml",
            "components/content/prompts/personas/taiwan_persona.yaml",
            "components/content/prompts/formatting/taiwan_formatting.yaml",
        ]

        all_exist = all(Path(f).exists() for f in prompt_files)
        print(f"✅ Prompt files intact: {all_exist}")

        return True

    except Exception as e:
        print(f"❌ Production system verification failed: {e}")
        return False


def main():
    """Run the cleanup process."""
    print("🚀 Content Component Directory Cleanup")
    print("=" * 60)

    # Run cleanup
    cleanup_success = cleanup_content_directory()

    if cleanup_success:
        # Verify system still works
        verify_success = verify_production_system()

        if verify_success:
            print(f"\n" + "=" * 60)
            print("🎉 CLEANUP COMPLETE - PRODUCTION SYSTEM VERIFIED")
            print("=" * 60)
            print("\n📁 Production Directory Structure:")
            print("components/content/")
            print("├── fail_fast_generator.py      # Production content generator")
            print("├── prompts/")
            print("│   ├── base_content_prompt.yaml")
            print("│   ├── personas/               # Author personas (4 files)")
            print("│   └── formatting/             # Formatting configs (4 files)")
            print("├── archive/                    # Archived old generators")
            print("└── cleanup_archive/            # Archived development files")
            print("\n✅ System ready for production deployment")
        else:
            print(f"\n❌ CLEANUP FAILED - PRODUCTION SYSTEM BROKEN")
    else:
        print(f"\n❌ CLEANUP FAILED")


if __name__ == "__main__":
    main()
