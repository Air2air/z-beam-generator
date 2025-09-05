#!/usr/bin/env python3
"""
AI Detection Prompts Version Manager
Manages versioning and changelog for ai_detection.yaml configuration files.
"""

import yaml
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

class AIDetectionVersionManager:
    """Manages versioning for AI detection prompt configurations."""

    def __init__(self, config_path: str = "components/text/prompts/ai_detection.yaml"):
        self.config_path = Path(config_path)
        self.version_pattern = re.compile(r'# Version: (\d+\.\d+\.\d+)')
        self.date_pattern = re.compile(r'# Last Updated: (\d{4}-\d{2}-\d{2})')

    def get_current_version(self) -> Optional[str]:
        """Get the current version from the config file."""
        if not self.config_path.exists():
            return None

        with open(self.config_path, 'r', encoding='utf-8') as f:
            content = f.read()

        version_match = self.version_pattern.search(content)
        return version_match.group(1) if version_match else None

    def get_current_date(self) -> Optional[str]:
        """Get the current last updated date from the config file."""
        if not self.config_path.exists():
            return None

        with open(self.config_path, 'r', encoding='utf-8') as f:
            content = f.read()

        date_match = self.date_pattern.search(content)
        return date_match.group(1) if date_match else None

    def update_version(self, new_version: str, changelog_entry: str, author: str = "AI Detection System") -> bool:
        """Update the version and add a changelog entry."""
        try:
            if not self.config_path.exists():
                return False

            with open(self.config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Update version
            content = self.version_pattern.sub(f'# Version: {new_version}', content)

            # Update last updated date
            today = datetime.now().strftime('%Y-%m-%d')
            content = self.date_pattern.sub(f'# Last Updated: {today}', content)

            # Add changelog entry
            changelog_marker = "# Changelog:"
            if changelog_marker in content:
                # Insert new entry after the changelog header
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip() == changelog_marker:
                        # Insert new entry after the changelog header
                        lines.insert(i + 1, f"#   {new_version} ({today}): {changelog_entry}")
                        break
                content = '\n'.join(lines)

            # Write back to file
            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✅ Updated {self.config_path} to version {new_version}")
            return True

        except Exception as e:
            print(f"❌ Failed to update version: {e}")
            return False

    def bump_version(self, bump_type: str = "patch", changelog_entry: str = "Minor updates",
                    author: str = "AI Detection System") -> bool:
        """Bump version number (major, minor, or patch)."""
        current_version = self.get_current_version()
        if not current_version:
            print("❌ Could not determine current version")
            return False

        try:
            major, minor, patch = map(int, current_version.split('.'))

            if bump_type == "major":
                major += 1
                minor = 0
                patch = 0
            elif bump_type == "minor":
                minor += 1
                patch = 0
            elif bump_type == "patch":
                patch += 1
            else:
                print(f"❌ Invalid bump type: {bump_type}. Use 'major', 'minor', or 'patch'")
                return False

            new_version = f"{major}.{minor}.{patch}"
            return self.update_version(new_version, changelog_entry, author)

        except ValueError:
            print(f"❌ Invalid version format: {current_version}")
            return False

    def get_version_history(self) -> Dict[str, Any]:
        """Get version history from changelog."""
        if not self.config_path.exists():
            return {}

        with open(self.config_path, 'r', encoding='utf-8') as f:
            content = f.read()

        history = {
            'current_version': self.get_current_version(),
            'last_updated': self.get_current_date(),
            'changelog': []
        }

        # Extract changelog entries
        lines = content.split('\n')
        in_changelog = False
        for line in lines:
            if line.strip() == "# Changelog:":
                in_changelog = True
                continue
            elif in_changelog and line.startswith("#   v"):
                # Parse changelog entry
                match = re.match(r'#   v(\d+\.\d+\.\d+) \((\d{4}-\d{2}-\d{2})\): (.+)', line)
                if match:
                    version, date, description = match.groups()
                    history['changelog'].append({
                        'version': version,
                        'date': date,
                        'description': description
                    })

        return history

def main():
    """Command line interface for version management."""
    import argparse

    parser = argparse.ArgumentParser(description='AI Detection Prompts Version Manager')
    parser.add_argument('action', choices=['get', 'bump', 'update', 'history'],
                       help='Action to perform')
    parser.add_argument('--version', help='New version (for update action)')
    parser.add_argument('--bump-type', choices=['major', 'minor', 'patch'],
                       default='patch', help='Type of version bump')
    parser.add_argument('--changelog', default='Minor updates',
                       help='Changelog entry description')
    parser.add_argument('--author', default='AI Detection System',
                       help='Author of the changes')

    args = parser.parse_args()

    manager = AIDetectionVersionManager()

    if args.action == 'get':
        version = manager.get_current_version()
        date = manager.get_current_date()
        print(f"Current Version: {version}")
        print(f"Last Updated: {date}")

    elif args.action == 'bump':
        success = manager.bump_version(args.bump_type, args.changelog, args.author)
        if success:
            print(f"✅ Successfully bumped version ({args.bump_type})")
        else:
            print("❌ Failed to bump version")

    elif args.action == 'update':
        if not args.version:
            print("❌ Version required for update action")
            return
        success = manager.update_version(args.version, args.changelog, args.author)
        if success:
            print(f"✅ Successfully updated to version {args.version}")
        else:
            print("❌ Failed to update version")

    elif args.action == 'history':
        history = manager.get_version_history()
        print(f"Version History for {manager.config_path}:")
        print(f"Current Version: {history.get('current_version')}")
        print(f"Last Updated: {history.get('last_updated')}")
        print("\nChangelog:")
        for entry in history.get('changelog', []):
            print(f"  {entry['version']} ({entry['date']}): {entry['description']}")

if __name__ == "__main__":
    main()
