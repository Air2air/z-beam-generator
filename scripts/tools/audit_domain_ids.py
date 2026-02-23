#!/usr/bin/env python3
"""
Audit id / slug / fullPath consistency across all domains.

Checks:
1. Source data:   id == slug == YAML key    (no mutation in source)
2. Frontmatter:   id / slug / fullPath match source exactly
                  (export pipeline must not mutate these fields)
"""
import yaml
from pathlib import Path

GENERATOR_ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_ROOT  = GENERATOR_ROOT.parent / 'z-beam'

DOMAINS = [
    {
        'name':        'materials',
        'source_file': 'data/materials/Materials.yaml',
        'source_key':  'materials',
        'frontmatter': 'frontmatter/materials',
    },
    {
        'name':        'contaminants',
        'source_file': 'data/contaminants/Contaminants.yaml',
        'source_key':  'contaminants',
        'frontmatter': 'frontmatter/contaminants',
    },
    {
        'name':        'compounds',
        'source_file': 'data/compounds/Compounds.yaml',
        'source_key':  'compounds',
        'frontmatter': 'frontmatter/compounds',
    },
    {
        'name':        'settings',
        'source_file': 'data/settings/Settings.yaml',
        'source_key':  'settings',
        'frontmatter': 'frontmatter/settings',
    },
    {
        'name':        'applications',
        'source_file': 'data/applications/Applications.yaml',
        'source_key':  'applications',
        'frontmatter': 'frontmatter/applications',
    },
]


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def find_frontmatter_file(fm_dir: Path, source_key: str):
    """Find frontmatter file for a source key, tolerating filename suffixes."""
    exact = fm_dir / f'{source_key}.yaml'
    if exact.exists():
        return exact
    for f in fm_dir.glob('*.yaml'):
        stem = f.stem
        if stem == source_key or stem.startswith(source_key + '-') or stem.endswith('-' + source_key):
            return f
    return None


total_issues = 0
print()

for domain_cfg in DOMAINS:
    domain      = domain_cfg['name']
    source_path = GENERATOR_ROOT / domain_cfg['source_file']
    fm_dir      = FRONTEND_ROOT  / domain_cfg['frontmatter']

    try:
        source_data = load_yaml(source_path)
    except Exception as e:
        print(f'=== {domain.upper()} ===')
        print(f'  ❌ Could not load source: {e}\n')
        continue

    items          = source_data.get(domain_cfg['source_key'], {})
    source_issues  = []
    fm_issues      = []
    fm_missing     = []

    for key, item in items.items():
        src_id   = item.get('id',       '')
        src_slug = item.get('slug',     '')
        src_fp   = item.get('fullPath', '')

        # 1. Source self-consistency
        flags = []
        if src_id and src_id != key:
            flags.append(f'id({src_id!r}) != key({key!r})')
        if src_slug and src_slug != key:
            flags.append(f'slug({src_slug!r}) != key({key!r})')
        if flags:
            source_issues.append((key, flags))

        # 2. Frontmatter vs source
        fm_file = find_frontmatter_file(fm_dir, key)
        if not fm_file:
            fm_missing.append(key)
            continue

        try:
            fm = load_yaml(fm_file)
        except Exception as e:
            fm_issues.append((key, [f'parse error: {e}']))
            continue

        fm_id   = fm.get('id',       '')
        fm_slug = fm.get('slug',     '')
        fm_fp   = fm.get('fullPath', '')

        flags = []
        if src_id   and fm_id   and fm_id   != src_id:
            flags.append(f'frontmatter id({fm_id!r}) != source id({src_id!r})')
        if src_slug and fm_slug and fm_slug != src_slug:
            flags.append(f'frontmatter slug({fm_slug!r}) != source slug({src_slug!r})')
        if src_fp   and fm_fp   and fm_fp   != src_fp:
            flags.append(f'frontmatter fullPath({fm_fp!r}) != source fullPath({src_fp!r})')
        if flags:
            fm_issues.append((key, flags))

    issue_count   = len(source_issues) + len(fm_issues) + len(fm_missing)
    total_issues += issue_count
    status = '✅' if issue_count == 0 else '⚠️ '

    print(f'=== {domain.upper()} ({len(items)} items) {status} ===')

    if source_issues:
        print(f'  SOURCE INCONSISTENCIES ({len(source_issues)}):')
        for key, flags in source_issues:
            print(f'    KEY: {key}')
            for flag in flags:
                print(f'      ❌ {flag}')

    if fm_issues:
        print(f'  FRONTMATTER vs SOURCE MISMATCHES ({len(fm_issues)}):')
        for key, flags in fm_issues:
            print(f'    KEY: {key}')
            for flag in flags:
                print(f'      ❌ {flag}')

    if fm_missing:
        print(f'  FRONTMATTER FILES MISSING ({len(fm_missing)}):')
        for key in fm_missing[:10]:
            print(f'    ❌ {key}')
        if len(fm_missing) > 10:
            print(f'    ... and {len(fm_missing) - 10} more')

    if issue_count == 0:
        print(f'  ✅ All {len(items)} items: source and frontmatter id/slug/fullPath are consistent')

    # Show 2 comparison samples
    for key, item in list(items.items())[:2]:
        fm_file = find_frontmatter_file(fm_dir, key)
        fm = load_yaml(fm_file) if fm_file else {}
        print(f'  SAMPLE  src: id={item.get("id","—")}  slug={item.get("slug","—")}  fullPath={item.get("fullPath","—")}')
        print(f'          fm:  id={fm.get("id","—")}  slug={fm.get("slug","—")}  fullPath={fm.get("fullPath","—")}')
    print()

print(f'═══════════════════════════════')
print(f'TOTAL ISSUES: {total_issues}')
if total_issues == 0:
    print('✅ All domains fully consistent — no export pipeline mutations detected.')
print()
