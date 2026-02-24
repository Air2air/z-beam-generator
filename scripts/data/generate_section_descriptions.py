#!/usr/bin/env python3
"""
Production script to generate section descriptions for items.
Uses schema prompts from section_display_schema.yaml.

This is the PRODUCTION system for section description generation.

Usage:
    python3 scripts/data/generate_section_descriptions.py --domain materials --item "Aluminum"
    python3 scripts/data/generate_section_descriptions.py --domain materials --item "Aluminum" --section contaminatedBy
    python3 scripts/data/generate_section_descriptions.py --domain materials --all
    python3 scripts/data/generate_section_descriptions.py --domain all --all --dry-run
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.utils.yaml_utils import load_yaml, save_yaml
from shared.text.utils.prompt_registry_service import PromptRegistryService


DOMAIN_MAP: Dict[str, Tuple[str, str]] = {
    'materials': ('data/materials/Materials.yaml', 'materials'),
    'contaminants': ('data/contaminants/Contaminants.yaml', 'contaminants'),
    'compounds': ('data/compounds/Compounds.yaml', 'compounds'),
    'settings': ('data/settings/Settings.yaml', 'settings'),
    'applications': ('data/applications/Applications.yaml', 'applications'),
}


def _build_generator(domain: str):
    from generation.core.evaluated_generator import QualityEvaluatedGenerator
    from postprocessing.evaluation.subjective_evaluator import SubjectiveEvaluator
    from shared.api.client_factory import APIClientFactory

    api_client = APIClientFactory.create_client(provider='grok')
    winston_client = APIClientFactory.create_client(provider='winston')
    subjective_evaluator = SubjectiveEvaluator(api_client)

    return QualityEvaluatedGenerator(
        api_client=api_client,
        subjective_evaluator=subjective_evaluator,
        winston_client=winston_client,
        domain=domain,
    )


def _resolve_item(domain_items: Dict[str, dict], item_name: str) -> Tuple[str, dict]:
    # Match by key or display name.
    for key, value in domain_items.items():
        if key.lower() == item_name.lower():
            return key, value
        display_name = value.get('name') if isinstance(value, dict) else None
        if isinstance(display_name, str) and display_name.lower() == item_name.lower():
            return key, value
    return None, None


def _get_description_text(content_data) -> str:
    if isinstance(content_data, dict):
        if 'description' in content_data and isinstance(content_data['description'], str):
            return content_data['description']
        if 'before' in content_data and isinstance(content_data['before'], str):
            return content_data['before']
    if isinstance(content_data, str):
        return content_data
    return ''


def _sanitize_section_description(text: str) -> str:
    if not isinstance(text, str):
        return ''

    cleaned = text.strip()
    if not cleaned:
        return ''

    lower = cleaned.lower()
    marker = 'description:'

    if marker in lower:
        marker_index = lower.find(marker)
        return cleaned[marker_index + len(marker):].strip()

    if lower.startswith('title:'):
        return cleaned[len('title:'):].strip()

    return cleaned


def _save_section_description(section_data: dict, description_text: str) -> None:
    if '_section' not in section_data or not isinstance(section_data['_section'], dict):
        section_data['_section'] = {}

    section_data['_section']['sectionDescription'] = description_text

    if 'sectionMetadata' in section_data:
        del section_data['sectionMetadata']
    if 'description' in section_data:
        del section_data['description']

def main() -> int:
    parser = argparse.ArgumentParser(
        description='Generate section descriptions using schema prompts (full pipeline).'
    )
    parser.add_argument(
        '--domain',
        required=True,
        choices=[*DOMAIN_MAP.keys(), 'all'],
        help='Domain to process (or "all")',
    )
    parser.add_argument('--item', help='Item name or slug (optional when using --all)')
    parser.add_argument('--section', help='Section key to limit generation (e.g., contaminatedBy)')
    parser.add_argument('--all', action='store_true', help='Process all items in the domain(s)')
    parser.add_argument('--dry-run', action='store_true', help='Do not write changes')

    args = parser.parse_args()

    if not args.all and not args.item:
        raise ValueError('Provide --item for a single item or use --all to process all items.')

    domains = list(DOMAIN_MAP.keys()) if args.domain == 'all' else [args.domain]

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                  SECTION DESCRIPTION GENERATION SYSTEM                        ║
║                                                                              ║
║  Production system for generating section descriptions using schema prompts  ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    print("📝 Source: data/schemas/section_display_schema.yaml")
    print("💾 Output: Saves '_section.sectionDescription' to source YAML")
    print(f"🧪 Mode: {'DRY RUN' if args.dry_run else 'WRITE'}\n")

    overall_stats = {'processed': 0, 'generated': 0, 'skipped': 0, 'errors': 0}

    for domain in domains:
        source_path, items_key = DOMAIN_MAP[domain]
        data_path = project_root / source_path

        print(f"{'=' * 80}")
        print(f"🔧 Domain: {domain}")
        print(f"📂 Source: {data_path}")
        print(f"{'=' * 80}")

        domain_data = load_yaml(data_path)
        items = domain_data.get(items_key, {})
        if not isinstance(items, dict):
            raise TypeError(f"Expected '{items_key}' to be a dictionary in {data_path}")

        if args.item:
            item_key, item_data = _resolve_item(items, args.item)
            if not item_data:
                print(f"❌ Item '{args.item}' not found in {domain}")
                continue
            items_to_process = [(item_key, item_data)]
        else:
            items_to_process = list(items.items())

        generator = _build_generator(domain)
        modified = False

        for item_key, item_data in items_to_process:
            overall_stats['processed'] += 1

            relationships = item_data.get('relationships')
            if not isinstance(relationships, dict) or not relationships:
                print(f"⚠️  {item_key}: no relationships found")
                overall_stats['skipped'] += 1
                continue

            sections_to_process = []
            for group_key, group_data in relationships.items():
                if not isinstance(group_data, dict):
                    continue
                for section_key in group_data.keys():
                    if args.section and section_key != args.section:
                        continue
                    sections_to_process.append((group_key, section_key))

            if not sections_to_process:
                print(f"⚠️  {item_key}: no matching sections")
                overall_stats['skipped'] += 1
                continue

            print(f"\n🧱 {item_key}: {len(sections_to_process)} sections")

            for group_key, section_key in sections_to_process:
                prompt = PromptRegistryService.get_schema_prompt(domain, section_key, include_descriptor=True)
                if not prompt:
                    print(f"  ⏭️  {group_key}.{section_key}: no prompt resolved")
                    overall_stats['skipped'] += 1
                    continue

                try:
                    result = generator.generate(
                        material_name=item_key,
                        component_type=section_key,
                    )
                except Exception as exc:
                    print(f"  ❌ {group_key}.{section_key}: generation error - {exc}")
                    overall_stats['errors'] += 1
                    continue

                if not getattr(result, 'success', False) or not getattr(result, 'content', None):
                    error_msg = getattr(result, 'error_message', None) or 'Unknown error'
                    print(f"  ❌ {group_key}.{section_key}: generation failed - {error_msg}")
                    overall_stats['errors'] += 1
                    continue

                description_text = _sanitize_section_description(
                    _get_description_text(result.content)
                )
                if not description_text:
                    print(f"  ❌ {group_key}.{section_key}: no description extracted")
                    overall_stats['errors'] += 1
                    continue

                section_data = relationships[group_key].get(section_key, {})
                if not isinstance(section_data, dict):
                    section_data = {}

                _save_section_description(section_data, description_text)
                relationships[group_key][section_key] = section_data
                overall_stats['generated'] += 1
                modified = True
                print(f"  ✅ {group_key}.{section_key}: sectionDescription saved")

            item_data['relationships'] = relationships
            items[item_key] = item_data

        if modified and not args.dry_run:
            domain_data[items_key] = items
            save_yaml(data_path, domain_data)
            print(f"\n💾 Saved updates to {data_path}")
        elif modified and args.dry_run:
            print(f"\n🔍 DRY RUN: Would save updates to {data_path}")

    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"Processed: {overall_stats['processed']}")
    print(f"Generated: {overall_stats['generated']}")
    print(f"Skipped:   {overall_stats['skipped']}")
    print(f"Errors:    {overall_stats['errors']}")
    print("=" * 80 + "\n")

    return 0 if overall_stats['errors'] == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
