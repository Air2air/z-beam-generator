#!/usr/bin/env python3
"""
Reconcile material/application relationships with strict eligibility and a shared table.

Eligibility (MANDATORY):
    1) Link exists in applications domain relationships (AI-researched link provenance)
    2) Target application/material entries exist in source domain files

Canonical relationship table:
    data/associations/MaterialApplicationRelationships.yaml

Target:
    data/applications/Applications.yaml
  data/materials/Materials.yaml
    - applications.relationships.discovery.relatedMaterials
    - materials.relationships.operational.industryApplications

Behavior:
    - Builds canonical eligible pairs from applications-domain links
    - Generates discrepancy report (materials-only vs applications-only)
    - Writes shared relationship table
    - Reconciles BOTH domain files from canonical pairs
  - Supports check mode (no writes) and write mode
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any, Dict, List, Set, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from shared.utils.yaml_utils import dump_yaml_fast as save_yaml
from shared.utils.yaml_utils import load_yaml_fast as load_yaml

APPLICATIONS_PATH = PROJECT_ROOT / "data" / "applications" / "Applications.yaml"
MATERIALS_PATH = PROJECT_ROOT / "data" / "materials" / "Materials.yaml"
RELATIONSHIPS_TABLE_PATH = PROJECT_ROOT / "data" / "associations" / "MaterialApplicationRelationships.yaml"


def _require_mapping(obj: Dict[str, Any], key: str, path: Path) -> Dict[str, Any]:
    value = obj.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"Expected '{key}' mapping in {path}")
    return value


def _require_string(item: Dict[str, Any], key: str, context: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing required string '{key}' for {context}")
    return value.strip()


def _build_application_card(application_id: str, application: Dict[str, Any]) -> Dict[str, Any]:
    name = _require_string(application, "name", f"application '{application_id}'")
    category = _require_string(application, "category", f"application '{application_id}'")
    subcategory = _require_string(application, "subcategory", f"application '{application_id}'")
    url = _require_string(application, "fullPath", f"application '{application_id}'")
    description = _require_string(application, "pageDescription", f"application '{application_id}'")

    image = None
    images = application.get("images")
    if isinstance(images, dict):
        hero = images.get("hero")
        if isinstance(hero, dict):
            hero_url = hero.get("url")
            if isinstance(hero_url, str) and hero_url.strip():
                image = hero_url.strip()

    card = {
        "id": application_id,
        "name": name,
        "category": category,
        "subcategory": subcategory,
        "url": url,
        "description": description,
    }

    if image:
        card["image"] = image

    return card


def _build_material_card(material_id: str, material: Dict[str, Any]) -> Dict[str, Any]:
    name = _require_string(material, "name", f"material '{material_id}'")
    category = _require_string(material, "category", f"material '{material_id}'")
    subcategory = _require_string(material, "subcategory", f"material '{material_id}'")
    url = _require_string(material, "fullPath", f"material '{material_id}'")

    images = material.get("images")
    if not isinstance(images, dict):
        raise ValueError(f"Missing images mapping for material '{material_id}'")

    hero = images.get("hero")
    if not isinstance(hero, dict):
        raise ValueError(f"Missing images.hero mapping for material '{material_id}'")

    image = _require_string(hero, "url", f"material '{material_id}' images.hero")

    return {
        "id": material_id,
        "name": name,
        "category": category,
        "subcategory": subcategory,
        "url": url,
        "image": image,
    }


def _extract_app_pairs(applications: Dict[str, Any], materials: Dict[str, Any]) -> Set[Tuple[str, str]]:
    pairs: Set[Tuple[str, str]] = set()

    for app_id, app_data in applications.items():
        if not isinstance(app_data, dict):
            raise ValueError(f"Application '{app_id}' must be a dictionary")

        relationships = app_data.get("relationships")
        if not isinstance(relationships, dict):
            raise ValueError(f"Application '{app_id}' missing relationships")

        discovery = relationships.get("discovery")
        if not isinstance(discovery, dict):
            raise ValueError(f"Application '{app_id}' missing relationships.discovery")

        related_materials = discovery.get("relatedMaterials")
        if not isinstance(related_materials, dict):
            raise ValueError(f"Application '{app_id}' missing relationships.discovery.relatedMaterials")

        items = related_materials.get("items")
        if not isinstance(items, list):
            raise ValueError(f"Application '{app_id}' relationships.discovery.relatedMaterials.items must be a list")

        for item in items:
            if not isinstance(item, dict):
                raise ValueError(f"Application '{app_id}' relatedMaterials item must be a mapping")

            material_id = _require_string(item, "id", f"application '{app_id}' related material item")

            if material_id not in materials:
                raise ValueError(
                    f"Application '{app_id}' references unknown material '{material_id}' in relatedMaterials"
                )

            pairs.add((material_id, app_id))

    return pairs


def _extract_material_pairs(materials: Dict[str, Any], applications: Dict[str, Any]) -> Set[Tuple[str, str]]:
    pairs: Set[Tuple[str, str]] = set()

    for material_id, material_data in materials.items():
        if not isinstance(material_data, dict):
            raise ValueError(f"Material '{material_id}' must be a dictionary")

        relationships = material_data.get("relationships")
        if not isinstance(relationships, dict):
            continue

        operational = relationships.get("operational")
        if not isinstance(operational, dict):
            continue

        industry_applications = operational.get("industryApplications")
        if not isinstance(industry_applications, dict):
            continue

        items = industry_applications.get("items")
        if not isinstance(items, list):
            raise ValueError(
                f"Material '{material_id}' relationships.operational.industryApplications.items must be a list"
            )

        for item in items:
            if not isinstance(item, dict):
                raise ValueError(
                    f"Material '{material_id}' industryApplications item must be a mapping"
                )

            app_id = _require_string(item, "id", f"material '{material_id}' industry application item")
            if app_id not in applications:
                continue

            pairs.add((material_id, app_id))

    return pairs


def _build_relationship_table(
    canonical_pairs: Set[Tuple[str, str]],
    app_pairs: Set[Tuple[str, str]],
    material_pairs: Set[Tuple[str, str]],
) -> Dict[str, Any]:
    links = [
        {
            "material_id": material_id,
            "application_id": app_id,
            "eligibility": {
                "ai_researched_specific_to_material": True,
                "application_domain_entry_exists": True,
            },
            "provenance": "applications.relationships.discovery.relatedMaterials",
            "status": "eligible",
        }
        for material_id, app_id in sorted(canonical_pairs)
    ]

    return {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "version": "1.0.0",
            "description": "Canonical material-application relationships for two-way reconciliation",
            "eligibility_rules": [
                "Link must exist in applications domain relationships (AI-researched provenance)",
                "Referenced application and material entries must exist",
            ],
        },
        "summary": {
            "eligible_links": len(canonical_pairs),
            "links_from_applications": len(app_pairs),
            "links_from_materials": len(material_pairs),
            "materials_only_discrepancies": len(material_pairs - app_pairs),
            "applications_only_discrepancies": len(app_pairs - material_pairs),
        },
        "links": links,
        "discrepancies": {
            "materials_only": [
                {"material_id": material_id, "application_id": app_id}
                for material_id, app_id in sorted(material_pairs - app_pairs)
            ],
            "applications_only": [
                {"material_id": material_id, "application_id": app_id}
                for material_id, app_id in sorted(app_pairs - material_pairs)
            ],
        },
    }


def _reconcile_materials_from_pairs(
    materials: Dict[str, Any],
    applications: Dict[str, Any],
    canonical_pairs: Set[Tuple[str, str]],
) -> int:
    by_material: Dict[str, Dict[str, Dict[str, Any]]] = {material_id: {} for material_id in materials.keys()}

    for material_id, app_id in canonical_pairs:
        app_data = applications[app_id]
        by_material[material_id][app_id] = _build_application_card(app_id, app_data)

    changed = 0

    for material_id, material_data in materials.items():
        if not isinstance(material_data, dict):
            raise ValueError(f"Material '{material_id}' must be a dictionary")

        relationships = material_data.setdefault("relationships", {})
        if not isinstance(relationships, dict):
            raise ValueError(f"Material '{material_id}' relationships must be a dictionary")

        operational = relationships.setdefault("operational", {})
        if not isinstance(operational, dict):
            raise ValueError(f"Material '{material_id}' relationships.operational must be a dictionary")

        existing_section = operational.get("industryApplications")
        if not isinstance(existing_section, dict):
            raise ValueError(f"Material '{material_id}' missing relationships.operational.industryApplications")

        existing_metadata = existing_section.get("_section")
        if not isinstance(existing_metadata, dict):
            raise ValueError(f"Material '{material_id}' missing industryApplications._section metadata")

        required_meta = ["sectionTitle", "sectionDescription", "icon", "order", "variant"]
        missing_meta = [key for key in required_meta if key not in existing_metadata]
        if missing_meta:
            raise ValueError(
                f"Material '{material_id}' industryApplications._section missing: {', '.join(missing_meta)}"
            )

        expected_items = sorted(by_material[material_id].values(), key=lambda x: x["name"].lower())
        expected_section = {
            "presentation": "card",
            "items": expected_items,
            "_section": existing_metadata,
        }

        if existing_section != expected_section:
            changed += 1
            operational["industryApplications"] = expected_section

    return changed


def _reconcile_applications_from_pairs(
    applications: Dict[str, Any],
    materials: Dict[str, Any],
    canonical_pairs: Set[Tuple[str, str]],
) -> int:
    by_application: Dict[str, Dict[str, Dict[str, Any]]] = {app_id: {} for app_id in applications.keys()}

    for material_id, app_id in canonical_pairs:
        material_data = materials[material_id]
        by_application[app_id][material_id] = _build_material_card(material_id, material_data)

    changed = 0

    for app_id, app_data in applications.items():
        if not isinstance(app_data, dict):
            raise ValueError(f"Application '{app_id}' must be a dictionary")

        relationships = app_data.get("relationships")
        if not isinstance(relationships, dict):
            raise ValueError(f"Application '{app_id}' missing relationships")

        discovery = relationships.get("discovery")
        if not isinstance(discovery, dict):
            raise ValueError(f"Application '{app_id}' missing relationships.discovery")

        related_materials = discovery.get("relatedMaterials")
        if not isinstance(related_materials, dict):
            raise ValueError(f"Application '{app_id}' missing relationships.discovery.relatedMaterials")

        expected_items = sorted(by_application[app_id].values(), key=lambda x: x["name"].lower())
        current_items = related_materials.get("items")
        if not isinstance(current_items, list):
            raise ValueError(f"Application '{app_id}' relatedMaterials.items must be a list")

        if current_items != expected_items:
            changed += 1
            related_materials["items"] = expected_items

    return changed

def reconcile_material_industry_applications(write: bool) -> Tuple[int, int]:
    applications_data = load_yaml(APPLICATIONS_PATH)
    materials_data = load_yaml(MATERIALS_PATH)

    if not isinstance(applications_data, dict):
        raise ValueError("Applications.yaml must parse to a dictionary")
    if not isinstance(materials_data, dict):
        raise ValueError("Materials.yaml must parse to a dictionary")

    applications = _require_mapping(applications_data, "applications", APPLICATIONS_PATH)
    materials = _require_mapping(materials_data, "materials", MATERIALS_PATH)

    app_pairs = _extract_app_pairs(applications, materials)
    material_pairs = _extract_material_pairs(materials, applications)

    # Canonical eligible set = applications-derived links (AI-researched provenance)
    canonical_pairs = set(app_pairs)

    table = _build_relationship_table(canonical_pairs, app_pairs, material_pairs)

    materials_changed = _reconcile_materials_from_pairs(materials, applications, canonical_pairs)
    applications_changed = _reconcile_applications_from_pairs(applications, materials, canonical_pairs)

    changed = materials_changed + applications_changed
    checked = len(materials)

    if write:
        save_yaml(table, RELATIONSHIPS_TABLE_PATH)

    if write and changed > 0:
        save_yaml(applications_data, APPLICATIONS_PATH)
        save_yaml(materials_data, MATERIALS_PATH)

    return checked, changed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reconcile materials industryApplications from applications domain"
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Apply reconciliation to Materials.yaml (default is check-only)",
    )
    args = parser.parse_args()

    checked, changed = reconcile_material_industry_applications(write=args.write)

    mode = "WRITE" if args.write else "CHECK"
    print(f"[{mode}] Materials checked: {checked}")
    print(f"[{mode}] Materials requiring reconciliation: {changed}")

    if not args.write and changed > 0:
        print("Run with --write to apply reconciliation.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
