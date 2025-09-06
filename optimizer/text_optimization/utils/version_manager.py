#!/usr/bin/env python3
"""
AI Detection Prompts Version Manager
Manages versioning and changelog for ai_detection.yaml configuration files.
"""

import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

    parser = argparse.ArgumentParser(description="AI Detection Prompts Version Manager")
    parser.add_argument(
        "action", choices=["get", "bump", "update", "history"], help="Action to perform"
    )
    parser.add_argument("--version", help="New version (for update action)")
    parser.add_argument(
        "--bump-type",
        choices=["major", "minor", "patch"],
        default="patch",
        help="Type of version bump",
    )
    parser.add_argument(
        "--changelog", default="Minor updates", help="Changelog entry description"
    )
    parser.add_argument(
        "--author", default="AI Detection System", help="Author of the changes"
    )

    args = parser.parse_args()

    manager = AIDetectionVersionManager()

    if args.action == "get":
        version = manager.get_current_version()
        date = manager.get_current_date()
        print(f"Current Version: {version}")
        print(f"Last Updated: {date}")

    elif args.action == "bump":
        success = manager.bump_version(args.bump_type, args.changelog, args.author)
        if success:
            print(f"✅ Successfully bumped version ({args.bump_type})")
        else:
            print("❌ Failed to bump version")

    elif args.action == "update":
        if not args.version:
            print("❌ Version required for update action")
            return
        success = manager.update_version(args.version, args.changelog, args.author)
        if success:
            print(f"✅ Successfully updated to version {args.version}")
        else:
            print("❌ Failed to update version")

    elif args.action == "history":
        history = manager.get_version_history()
        print(f"Version History for {manager.config_path}:")
        print(f"Current Version: {history.get('current_version')}")
        print(f"Last Updated: {history.get('last_updated')}")
        print("\nChangelog:")
        for entry in history.get("changelog", []):
            print(f"  {entry['version']} ({entry['date']}): {entry['description']}")


if __name__ == "__main__":
    main()
