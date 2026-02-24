#!/usr/bin/env python3
"""
Normalize Applications domain IDs, slugs, and fullPaths.

Problem: Applications source data uses keys like `aerospace-laser-cleaning`
but filenames/exported ids use `aerospace-laser-cleaning-applications`.
This creates id/slug/fullPath inconsistencies in exported frontmatter.

Fix:
  1. Rename all Applications.yaml keys to include -applications suffix
  2. Update id, slug, fullPath fields within each item
  3. Update /applications/ URL cross-references in Materials.yaml
  4. Remove filename_suffix from export/config/applications.yaml
     (suffix now lives in source, not in exporter)

Dry-run by default. Pass --apply to write changes.
"""
import sys
import yaml
import re
from pathlib import Path
from collections import OrderedDict

DRY_RUN = '--apply' not in sys.argv

APPLICATIONS_YAML = Path('data/applications/Applications.yaml')
MATERIALS_YAML    = Path('data/materials/Materials.yaml')
EXPORT_CONFIG     = Path('export/config/applications.yaml')

# All 10 application keys: old → new
RENAMES = {
    'aerospace-laser-cleaning':            'aerospace-laser-cleaning-applications',
    'automotive-laser-cleaning':           'automotive-laser-cleaning-applications',
    'electronics-laser-cleaning':          'electronics-laser-cleaning-applications',
    'medical-devices-laser-cleaning':      'medical-devices-laser-cleaning-applications',
    'energy-power-laser-cleaning':         'energy-power-laser-cleaning-applications',
    'rail-transport-laser-cleaning':       'rail-transport-laser-cleaning-applications',
    'shipbuilding-marine-laser-cleaning':  'shipbuilding-marine-laser-cleaning-applications',
    'construction-equipment-laser-cleaning': 'construction-equipment-laser-cleaning-applications',
    'food-processing-laser-cleaning':      'food-processing-laser-cleaning-applications',
    'defense-laser-cleaning':              'defense-laser-cleaning-applications',
}


def load_yaml_raw(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def patch_applications_yaml(raw: str) -> str:
    """
    Rename all top-level keys and update id/slug/fullPath fields within each
    application entry using regex — preserves all other formatting exactly.
    """
    for old, new in RENAMES.items():
        # 1. Rename the indented YAML key (e.g., `  aerospace-laser-cleaning:`)
        raw = re.sub(
            rf'^(\s+){re.escape(old)}:$',
            rf'\g<1>{new}:',
            raw,
            flags=re.MULTILINE
        )
        # 2. Update `id: aerospace-laser-cleaning`
        raw = re.sub(
            rf'^(\s+id:\s+){re.escape(old)}$',
            rf'\g<1>{new}',
            raw,
            flags=re.MULTILINE
        )
        # 3. Update `slug: aerospace-laser-cleaning`
        raw = re.sub(
            rf'^(\s+slug:\s+){re.escape(old)}$',
            rf'\g<1>{new}',
            raw,
            flags=re.MULTILINE
        )
        # 4. Update `fullPath: /applications/aerospace-laser-cleaning`
        raw = re.sub(
            rf'^(\s+fullPath:\s+/applications/){re.escape(old)}$',
            rf'\g<1>{new}',
            raw,
            flags=re.MULTILINE
        )
    return raw


def patch_materials_yaml(raw: str) -> str:
    """
    Update all application URL cross-references in Materials.yaml.
    e.g. `url: /applications/aerospace-laser-cleaning`
      → `url: /applications/aerospace-laser-cleaning-applications`
    """
    for old, new in RENAMES.items():
        raw = re.sub(
            rf'(url:\s+/applications/){re.escape(old)}(\s|$)',
            rf'\g<1>{new}\2',
            raw
        )
    return raw


def patch_export_config(raw: str) -> str:
    """Remove filename_suffix (set to '') since suffix is now in source keys."""
    raw = re.sub(
        r"^filename_suffix:\s*'-applications'",
        "filename_suffix: ''",
        raw,
        flags=re.MULTILINE
    )
    return raw


def audit_changes(original: str, patched: str, label: str):
    orig_lines  = original.splitlines()
    patch_lines = patched.splitlines()
    changes = []
    for i, (a, b) in enumerate(zip(orig_lines, patch_lines), 1):
        if a != b:
            changes.append((i, a.strip(), b.strip()))
    print(f'\n{label}: {len(changes)} line(s) changed')
    for lineno, before, after in changes[:30]:
        print(f'  L{lineno}: {before!r} → {after!r}')
    if len(changes) > 30:
        print(f'  ... and {len(changes) - 30} more')
    return len(changes)


def main():
    mode = 'DRY RUN' if DRY_RUN else 'APPLYING'
    print(f'=== Normalize Applications IDs ({mode}) ===\n')

    total_changes = 0

    # --- Applications.yaml ---
    raw_apps  = load_yaml_raw(APPLICATIONS_YAML)
    new_apps  = patch_applications_yaml(raw_apps)
    total_changes += audit_changes(raw_apps, new_apps, 'Applications.yaml')

    # --- Materials.yaml ---
    raw_mats  = load_yaml_raw(MATERIALS_YAML)
    new_mats  = patch_materials_yaml(raw_mats)
    total_changes += audit_changes(raw_mats, new_mats, 'Materials.yaml')

    # --- export/config/applications.yaml ---
    raw_cfg   = load_yaml_raw(EXPORT_CONFIG)
    new_cfg   = patch_export_config(raw_cfg)
    total_changes += audit_changes(raw_cfg, new_cfg, 'export/config/applications.yaml')

    print(f'\nTotal: {total_changes} line(s) across 3 files')

    if DRY_RUN:
        print('\nDry run complete. Run with --apply to write changes.')
        return

    # Validate patched YAML parses cleanly before writing
    try:
        yaml.safe_load(new_apps)
        yaml.safe_load(new_cfg)
        print('\n✅ YAML validation passed')
    except yaml.YAMLError as e:
        print(f'\n❌ YAML validation FAILED: {e}')
        sys.exit(1)

    APPLICATIONS_YAML.write_text(new_apps, encoding='utf-8')
    MATERIALS_YAML.write_text(new_mats, encoding='utf-8')
    EXPORT_CONFIG.write_text(new_cfg, encoding='utf-8')

    print('✅ Files written successfully')
    print('\nNext: run  python3 run.py --export --domain applications --force')


if __name__ == '__main__':
    main()
