import json
import os
from collections import defaultdict
from datetime import datetime, timezone

import yaml

FRONTMATTER_ROOT = '/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter'
OUTPUT_JSON = '/Users/todddunning/Desktop/Z-Beam/z-beam-generator/tasks/section_object_missing_report.json'
OUTPUT_MD = '/Users/todddunning/Desktop/Z-Beam/z-beam-generator/tasks/section_object_missing_report.md'
DOMAINS = ['materials', 'contaminants', 'compounds', 'settings', 'applications']

KNOWN_SECTION_KEYS = {
    'materialCharacteristics',
    'laserMaterialInteraction',
    'faq',
    'contaminatedBy',
    'relatedMaterials',
    'industryApplications',
    'regulatoryStandards',
    'producesCompounds',
    'affectsMaterials',
    'producedFromContaminants',
    'producedFromMaterials',
    'common_challenges',
    'commonChallenges',
    'machine_settings',
    'machineSettings',
    'prevention',
}


def has_nested_section(value):
    return isinstance(value, dict) and isinstance(value.get('_section'), dict)


def load_yaml(path):
    with open(path, 'r', encoding='utf-8') as handle:
        return yaml.safe_load(handle) or {}


report = {
    'generatedAt': datetime.now(timezone.utc).isoformat(),
    'frontmatterRoot': FRONTMATTER_ROOT,
    'domains': {},
    'totals': {
        'domainsScanned': 0,
        'filesScanned': 0,
        'missingPathKinds': 0,
        'missingFieldOccurrences': 0,
    },
}

for domain in DOMAINS:
    folder = os.path.join(FRONTMATTER_ROOT, domain)
    missing = defaultdict(list)
    orphan_root_section = []
    files_scanned = 0

    if not os.path.isdir(folder):
        report['domains'][domain] = {
            'error': f'missing folder: {folder}'
        }
        continue

    for filename in sorted(os.listdir(folder)):
        if not filename.endswith('.yaml'):
            continue

        files_scanned += 1
        path = os.path.join(folder, filename)

        try:
            data = load_yaml(path)
        except Exception:
            continue

        if '_section' in data:
            orphan_root_section.append(filename)

        if 'faq' in data and not has_nested_section(data.get('faq')):
            missing['faq'].append(filename)

        properties = data.get('properties')
        if isinstance(properties, dict):
            for key in ('materialCharacteristics', 'laserMaterialInteraction'):
                if key in properties and not has_nested_section(properties.get(key)):
                    missing[f'properties.{key}'].append(filename)

        relationships = data.get('relationships')
        if isinstance(relationships, dict):
            for key, value in relationships.items():
                if key in KNOWN_SECTION_KEYS and not isinstance(value, dict):
                    missing[f'relationships.{key}'].append(filename)

            for group, group_value in relationships.items():
                if not isinstance(group_value, dict):
                    continue
                for field, field_value in group_value.items():
                    if field.startswith('_'):
                        continue
                    is_section_container = (
                        field in KNOWN_SECTION_KEYS
                        or (
                            isinstance(field_value, dict)
                            and (
                                'items' in field_value
                                or 'presentation' in field_value
                                or '_section' in field_value
                            )
                        )
                    )
                    if is_section_container and not has_nested_section(field_value):
                        missing[f'relationships.{group}.{field}'].append(filename)

    missing_paths = {
        path: sorted(files)
        for path, files in sorted(missing.items(), key=lambda item: (-len(item[1]), item[0]))
    }

    missing_occurrences = sum(len(files) for files in missing_paths.values())

    report['domains'][domain] = {
        'filesScanned': files_scanned,
        'missingPathKinds': len(missing_paths),
        'missingFieldOccurrences': missing_occurrences,
        'missingPaths': missing_paths,
        'orphanRootSectionFiles': sorted(orphan_root_section),
    }

    report['totals']['domainsScanned'] += 1
    report['totals']['filesScanned'] += files_scanned
    report['totals']['missingPathKinds'] += len(missing_paths)
    report['totals']['missingFieldOccurrences'] += missing_occurrences

with open(OUTPUT_JSON, 'w', encoding='utf-8') as handle:
    json.dump(report, handle, indent=2)

md_lines = []
md_lines.append('# Section Object Audit (All Domains)')
md_lines.append('')
md_lines.append(f"Generated: {report['generatedAt']}")
md_lines.append('')
md_lines.append('## Summary')
md_lines.append('')
md_lines.append(f"- Domains scanned: {report['totals']['domainsScanned']}")
md_lines.append(f"- Files scanned: {report['totals']['filesScanned']}")
md_lines.append(f"- Missing path kinds: {report['totals']['missingPathKinds']}")
md_lines.append(f"- Missing field occurrences: {report['totals']['missingFieldOccurrences']}")
md_lines.append('')

for domain in DOMAINS:
    info = report['domains'].get(domain, {})
    md_lines.append(f"## {domain}")
    md_lines.append('')

    if 'error' in info:
        md_lines.append(f"- Error: {info['error']}")
        md_lines.append('')
        continue

    md_lines.append(f"- Files scanned: {info['filesScanned']}")
    md_lines.append(f"- Missing path kinds: {info['missingPathKinds']}")
    md_lines.append(f"- Missing field occurrences: {info['missingFieldOccurrences']}")
    md_lines.append('')

    if info['missingPaths']:
        md_lines.append('### Missing nested _section by field path')
        md_lines.append('')
        for path, files in info['missingPaths'].items():
            md_lines.append(f"- {path} ({len(files)})")
            for filename in files:
                md_lines.append(f"  - {filename}")
        md_lines.append('')
    else:
        md_lines.append('- No missing nested _section fields found.')
        md_lines.append('')

    if info['orphanRootSectionFiles']:
        md_lines.append(f"### Orphan root _section files ({len(info['orphanRootSectionFiles'])})")
        md_lines.append('')
        for filename in info['orphanRootSectionFiles']:
            md_lines.append(f"- {filename}")
        md_lines.append('')

with open(OUTPUT_MD, 'w', encoding='utf-8') as handle:
    handle.write('\n'.join(md_lines))

print(OUTPUT_JSON)
print(OUTPUT_MD)
