#!/usr/bin/env python3
"""Clean application relationship fields in source data.

Actions:
1) Remove item-level `description` from `relationships.interactions.contaminatedBy.items`
2) Replace generic `_section.sectionDescription` placeholders with application-specific text:
   - `relationships.discovery.relatedMaterials._section.sectionDescription`
   - `relationships.interactions.contaminatedBy._section.sectionDescription`

This updates source-of-truth only (`data/applications/Applications.yaml`).
Frontmatter should be regenerated via export after running.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from shared.utils.yaml_utils import load_yaml_fast as load_yaml
from shared.utils.yaml_utils import dump_yaml_fast as save_yaml

APPLICATIONS_PATH = PROJECT_ROOT / "data" / "applications" / "Applications.yaml"


def _application_label(app_id: str, app_data: Dict[str, Any]) -> str:
    for key in ("name", "displayName", "pageTitle"):
        value = app_data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return app_id.replace("-laser-cleaning", "").replace("-", " ").title()


def _sanitize_section_description(text: Any) -> str:
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


def main() -> int:
    data = load_yaml(APPLICATIONS_PATH)
    if not isinstance(data, dict):
        raise ValueError("Applications.yaml must parse to a dictionary")

    applications = data.get("applications")
    if not isinstance(applications, dict):
        raise ValueError("Applications.yaml key 'applications' must be a mapping")

    removed_item_descriptions = 0
    updated_section_descriptions = 0
    removed_legacy_root_fields = 0

    for app_id, app_data in applications.items():
        if not isinstance(app_data, dict):
            continue

        label = _application_label(app_id, app_data)

        relationships = app_data.get("relationships")
        if not isinstance(relationships, dict):
            continue

        discovery = relationships.get("discovery")
        related_section = None
        contaminated_section = None

        if isinstance(discovery, dict):
            related_materials = discovery.get("relatedMaterials")
            if isinstance(related_materials, dict):
                section = related_materials.get("_section")
                if isinstance(section, dict):
                    related_section = section
                    current_text = _sanitize_section_description(
                        section.get("sectionDescription")
                    )
                    new_text = (
                        f"Materials most frequently cleaned in {label} laser cleaning workflows."
                    )
                    if current_text != new_text:
                        section["sectionDescription"] = new_text
                        updated_section_descriptions += 1

        interactions = relationships.get("interactions")
        if isinstance(interactions, dict):
            contaminated_by = interactions.get("contaminatedBy")
            if isinstance(contaminated_by, dict):
                section = contaminated_by.get("_section")
                if isinstance(section, dict):
                    contaminated_section = section
                    current_text = _sanitize_section_description(
                        section.get("sectionDescription")
                    )
                    new_text = (
                        f"Contaminants most commonly removed in {label} laser cleaning workflows."
                    )
                    if current_text != new_text:
                        section["sectionDescription"] = new_text
                        updated_section_descriptions += 1

                items = contaminated_by.get("items")
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict) and "description" in item:
                            del item["description"]
                            removed_item_descriptions += 1

        legacy_related = app_data.get("relatedMaterials")
        if isinstance(legacy_related, dict):
            if isinstance(related_section, dict):
                legacy_title = legacy_related.get("title")
                if isinstance(legacy_title, str) and legacy_title.strip():
                    related_section["sectionTitle"] = legacy_title.strip()

                legacy_text = _sanitize_section_description(
                    legacy_related.get("description")
                )
                if legacy_text:
                    related_section["sectionDescription"] = legacy_text
                    updated_section_descriptions += 1

            del app_data["relatedMaterials"]
            removed_legacy_root_fields += 1

        legacy_contaminated = app_data.get("contaminatedBy")
        if isinstance(legacy_contaminated, dict):
            if isinstance(contaminated_section, dict):
                legacy_title = legacy_contaminated.get("title")
                if isinstance(legacy_title, str) and legacy_title.strip():
                    contaminated_section["sectionTitle"] = legacy_title.strip()

                legacy_text = _sanitize_section_description(
                    legacy_contaminated.get("description")
                )
                if legacy_text:
                    contaminated_section["sectionDescription"] = legacy_text
                    updated_section_descriptions += 1

            del app_data["contaminatedBy"]
            removed_legacy_root_fields += 1

    save_yaml(data, APPLICATIONS_PATH)

    print(
        {
            "file": str(APPLICATIONS_PATH),
            "removed_item_descriptions": removed_item_descriptions,
            "updated_section_descriptions": updated_section_descriptions,
            "removed_legacy_root_fields": removed_legacy_root_fields,
            "applications_count": len(applications),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
