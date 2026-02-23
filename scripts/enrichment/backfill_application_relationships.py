#!/usr/bin/env python3
"""
Backfill common materials and contaminants for application pages.

Populates denormalized relationship sections in Applications.yaml:
- relationships.discovery.relatedMaterials
- relationships.interactions.contaminatedBy

This script reads source data from Materials.yaml and Contaminants.yaml to
build complete card items (url, image) and writes them back
to Applications.yaml. It does not touch frontmatter output files.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

import yaml


APPLICATION_RELATIONSHIPS = {
    "automotive-laser-cleaning": {
        "materials": [
            "steel-laser-cleaning",
            "aluminum-laser-cleaning",
            "stainless-steel-laser-cleaning",
            "cast-iron-laser-cleaning",
            "copper-laser-cleaning",
        ],
        "contaminants": [
            "rust-oxidation-contamination",
            "industrial-oil-contamination",
            "grease-deposits-contamination",
            "paint-residue-contamination",
            "brake-dust-contamination",
        ],
    }
}


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required data file: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping at root of {path}, got {type(data).__name__}")
    return data


def _require_field(item: Dict[str, Any], field: str, item_id: str, domain: str) -> Any:
    value = item.get(field)
    if value in (None, ""):
        raise KeyError(f"Missing required field '{field}' for {domain} '{item_id}'")
    return value


def _build_material_item(item_id: str, materials: Dict[str, Any]) -> Dict[str, Any]:
    if item_id not in materials:
        raise KeyError(f"Material '{item_id}' not found in Materials.yaml")
    item = materials[item_id]

    name = _require_field(item, "name", item_id, "material")
    category = _require_field(item, "category", item_id, "material")
    subcategory = _require_field(item, "subcategory", item_id, "material")
    url = _require_field(item, "fullPath", item_id, "material")
    images = _require_field(item, "images", item_id, "material")
    hero = images.get("hero") if isinstance(images, dict) else None
    if not isinstance(hero, dict) or not hero.get("url"):
        raise KeyError(f"Missing images.hero.url for material '{item_id}'")
    return {
        "id": item_id,
        "name": name,
        "category": category,
        "subcategory": subcategory,
        "url": url,
        "image": hero["url"],
    }


def _build_contaminant_item(item_id: str, contaminants: Dict[str, Any]) -> Dict[str, Any]:
    if item_id not in contaminants:
        raise KeyError(f"Contaminant '{item_id}' not found in Contaminants.yaml")
    item = contaminants[item_id]

    name = _require_field(item, "name", item_id, "contaminant")
    category = _require_field(item, "category", item_id, "contaminant")
    subcategory = _require_field(item, "subcategory", item_id, "contaminant")
    url = _require_field(item, "fullPath", item_id, "contaminant")
    images = _require_field(item, "images", item_id, "contaminant")
    hero = images.get("hero") if isinstance(images, dict) else None
    if not isinstance(hero, dict) or not hero.get("url"):
        raise KeyError(f"Missing images.hero.url for contaminant '{item_id}'")
    description = item.get("pageDescription") or item.get("description")
    if not isinstance(description, str) or not description.strip():
        raise KeyError(f"Missing pageDescription/description for contaminant '{item_id}'")

    return {
        "id": item_id,
        "name": name,
        "category": category,
        "subcategory": subcategory,
        "url": url,
        "image": hero["url"],
        "description": description.strip(),
    }


def _build_relationship_sections(
    materials: Dict[str, Any],
    contaminants: Dict[str, Any],
    material_ids: List[str],
    contaminant_ids: List[str],
) -> Dict[str, Any]:
    related_materials = [_build_material_item(item_id, materials) for item_id in material_ids]
    common_contaminants = [_build_contaminant_item(item_id, contaminants) for item_id in contaminant_ids]

    return {
        "discovery": {
            "relatedMaterials": {
                "presentation": "card",
                "items": related_materials,
                "_section": {
                    "sectionTitle": "Common Materials",
                    "sectionDescription": "Materials most frequently cleaned in this application context.",
                    "icon": "layers",
                    "order": 30,
                    "variant": "default",
                },
            }
        },
        "interactions": {
            "contaminatedBy": {
                "presentation": "card",
                "items": common_contaminants,
                "_section": {
                    "sectionTitle": "Common Contaminants",
                    "sectionDescription": "Contaminants typically removed in these applications.",
                    "icon": "droplet",
                    "order": 31,
                    "variant": "default",
                },
            }
        },
    }


def backfill_application_relationships(targets: List[str], dry_run: bool) -> None:
    base_path = Path(__file__).resolve().parents[2]
    applications_path = base_path / "data" / "applications" / "Applications.yaml"
    materials_path = base_path / "data" / "materials" / "Materials.yaml"
    contaminants_path = base_path / "data" / "contaminants" / "Contaminants.yaml"

    applications_data = _load_yaml(applications_path)
    materials_data = _load_yaml(materials_path)
    contaminants_data = _load_yaml(contaminants_path)

    applications = applications_data.get("applications")
    if not isinstance(applications, dict):
        raise ValueError("Expected 'applications' mapping in Applications.yaml")

    materials = materials_data.get("materials")
    if not isinstance(materials, dict):
        raise ValueError("Expected 'materials' mapping in Materials.yaml")

    contaminants = contaminants_data.get("contaminants")
    if not isinstance(contaminants, dict):
        raise ValueError("Expected 'contaminants' mapping in Contaminants.yaml")

    for application_id in targets:
        if application_id not in APPLICATION_RELATIONSHIPS:
            raise KeyError(f"No relationship mapping configured for '{application_id}'")
        if application_id not in applications:
            raise KeyError(f"Application '{application_id}' not found in Applications.yaml")

        mapping = APPLICATION_RELATIONSHIPS[application_id]
        relationships = _build_relationship_sections(
            materials,
            contaminants,
            mapping["materials"],
            mapping["contaminants"],
        )

        applications[application_id]["relationships"] = relationships
        print(f"Updated relationships for {application_id}")

    if dry_run:
        print("Dry run: no changes written")
        return

    with applications_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(applications_data, handle, sort_keys=False, allow_unicode=True)
    print(f"Saved updates to {applications_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill application relationship sections")
    parser.add_argument("--item", action="append", dest="items", help="Application id to update")
    parser.add_argument("--all", action="store_true", help="Update all configured applications")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()

    if args.all:
        targets = list(APPLICATION_RELATIONSHIPS.keys())
    elif args.items:
        targets = args.items
    else:
        raise SystemExit("Specify --item <id> or --all")

    backfill_application_relationships(targets, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
