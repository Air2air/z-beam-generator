#!/usr/bin/env python3
"""
Migrate video frontmatter files from the legacy associations.* structure to
the canonical relationships.discovery.* structure.

  BEFORE:
    associations:
      related_materials:
        _section: { sectionTitle: ..., icon: ..., ... }
        items: [slug1, slug2]
      related_contaminants: ...
      related_compounds: ...
      related_applications: ...

  AFTER:
    relationships:
      discovery:
        relatedMaterials:
          _section: { ... }
          items: [slug1, slug2]
        relatedContaminants: ...
        relatedCompounds: ...
        relatedApplications: ...

Run from z-beam-generator root:
  python3 scripts/migrate/migrate_video_associations.py [--dry-run]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VIDEO_DIR = PROJECT_ROOT.parent / "z-beam" / "frontmatter" / "videos"
sys.path.insert(0, str(PROJECT_ROOT))

from shared.utils.yaml_utils import load_yaml_fast as load_yaml, dump_yaml_fast as save_yaml

# snake_case → camelCase key mapping
KEY_MAP = {
    "related_materials": "relatedMaterials",
    "related_contaminants": "relatedContaminants",
    "related_compounds": "relatedCompounds",
    "related_applications": "relatedApplications",
}


def migrate_file(yaml_path: Path, dry_run: bool) -> bool:
    """
    Migrate a single video frontmatter file.
    Returns True if a change was made (or would be made in dry-run).
    """
    data = load_yaml(str(yaml_path))
    if not isinstance(data, dict):
        return False

    associations = data.get("associations")
    if not isinstance(associations, dict):
        return False  # nothing to migrate

    # Build relationships.discovery block from associations
    discovery: dict = data.get("relationships", {}).get("discovery", {})
    changed = False

    for old_key, new_key in KEY_MAP.items():
        section = associations.get(old_key)
        if not isinstance(section, dict):
            continue
        items = section.get("items", [])
        if not isinstance(items, list):
            continue
        # Preserve _section metadata and items; drop empty sections
        if not items and not section.get("_section"):
            continue
        discovery[new_key] = {
            "_section": section.get("_section", {}),
            "items": [s for s in items if isinstance(s, str)],
        }
        changed = True

    if not changed:
        return False

    # Write updated structure
    relationships = data.get("relationships", {})
    relationships["discovery"] = discovery
    data["relationships"] = relationships

    # Remove the legacy associations block
    del data["associations"]

    slug = yaml_path.stem
    if dry_run:
        print(f"  [dry-run] {slug}: would migrate {list(discovery.keys())}")
    else:
        save_yaml(data, str(yaml_path))
        print(f"  ✅ {slug}: migrated {list(discovery.keys())}")

    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not VIDEO_DIR.exists():
        print(f"Error: video directory not found: {VIDEO_DIR}")
        sys.exit(1)

    yaml_files = sorted(VIDEO_DIR.glob("*.yaml"))
    print(f"\n{'[DRY-RUN] ' if args.dry_run else ''}Migrating {len(yaml_files)} video frontmatter files")
    print(f"  {VIDEO_DIR}\n")

    changed = 0
    skipped = 0
    for yaml_path in yaml_files:
        if migrate_file(yaml_path, args.dry_run):
            changed += 1
        else:
            skipped += 1

    print(f"\n📊 {changed} migrated, {skipped} skipped (no associations block)")


if __name__ == "__main__":
    main()
