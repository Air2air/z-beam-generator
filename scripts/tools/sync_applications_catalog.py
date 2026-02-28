#!/usr/bin/env python3
"""Synchronize applications catalog to required IDs and marine rename contract.

- Ensures required application IDs exist in source data
- Renames shipbuilding-marine IDs to marine IDs
- Preserves author identity on renamed records
- Creates missing records from category templates using KeywordSeedService logic
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
import sys

import yaml

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "applications" / "Applications.yaml"
sys.path.insert(0, str(ROOT))

from shared.services.keyword_seed_service import KeywordSeedService

RENAME_MAP = {
    "shipbuilding-marine-laser-cleaning-applications": "marine-laser-cleaning-applications",
    "shipbuilding-marine-laser-cleaning-ship-hulls-applications": "marine-ship-hulls-applications",
    "shipbuilding-marine-laser-cleaning-corrosion-removal-applications": "marine-corrosion-removal-applications",
    "shipbuilding-marine-laser-cleaning-paint-stripping-applications": "marine-paint-stripping-applications",
    "shipbuilding-marine-laser-cleaning-rust-removal-applications": "marine-rust-removal-applications",
    "shipbuilding-marine-laser-cleaning-barnacle-removal-applications": "marine-barnacle-removal-applications",
    "shipbuilding-marine-laser-cleaning-ndt-prep-applications": "marine-ndt-prep-applications",
}

REMOVE_IDS = {
    "marine-laser-cleaning-ship-hulls-applications",
}

REQUIRED_SPECS: List[Tuple[str, str, str]] = [
    # automotive
    ("automotive-aluminum-applications", "automotive", "automotive-laser-cleaning-applications"),
    ("automotive-steel-applications", "automotive", "automotive-laser-cleaning-applications"),
    ("automotive-paint-coating-removal-applications", "automotive", "automotive-laser-cleaning-applications"),
    ("automotive-rust-oxide-removal-applications", "automotive", "automotive-laser-cleaning-applications"),
    ("automotive-weld-prep-applications", "automotive", "automotive-laser-cleaning-applications"),
    ("automotive-ndt-surface-prep-applications", "automotive", "automotive-laser-cleaning-applications"),
    # construction equipment
    ("construction-heavy-equipment-applications", "construction-equipment", "construction-equipment-laser-cleaning-applications"),
    ("construction-rust-removal-applications", "construction-equipment", "construction-equipment-laser-cleaning-applications"),
    ("construction-paint-stripping-applications", "construction-equipment", "construction-equipment-laser-cleaning-applications"),
    ("construction-corrosion-removal-applications", "construction-equipment", "construction-equipment-laser-cleaning-applications"),
    ("construction-grease-oil-removal-applications", "construction-equipment", "construction-equipment-laser-cleaning-applications"),
    ("construction-surface-prep-applications", "construction-equipment", "construction-equipment-laser-cleaning-applications"),
    # defense
    ("defense-weapons-applications", "defense", "defense-laser-cleaning-applications"),
    ("defense-military-vehicle-applications", "defense", "defense-laser-cleaning-applications"),
    ("defense-aircraft-applications", "defense", "defense-laser-cleaning-applications"),
    ("defense-corrosion-removal-applications", "defense", "defense-laser-cleaning-applications"),
    ("defense-paint-removal-applications", "defense", "defense-laser-cleaning-applications"),
    ("defense-ndt-prep-applications", "defense", "defense-laser-cleaning-applications"),
    # electronics
    ("electronics-circuit-boards-applications", "electronics", "electronics-laser-cleaning-applications"),
    ("electronics-precision-applications", "electronics", "electronics-laser-cleaning-applications"),
    ("electronics-residue-removal-applications", "electronics", "electronics-laser-cleaning-applications"),
    ("electronics-oxide-removal-applications", "electronics", "electronics-laser-cleaning-applications"),
    ("electronics-semiconductors-applications", "electronics", "electronics-laser-cleaning-applications"),
    # energy & power
    ("energy-power-plant-applications", "energy-power", "energy-power-laser-cleaning-applications"),
    ("energy-turbine-applications", "energy-power", "energy-power-laser-cleaning-applications"),
    ("energy-insulator-applications", "energy-power", "energy-power-laser-cleaning-applications"),
    ("energy-rust-oxide-removal-applications", "energy-power", "energy-power-laser-cleaning-applications"),
    ("energy-corrosion-removal-applications", "energy-power", "energy-power-laser-cleaning-applications"),
    ("energy-ndt-surface-prep-applications", "energy-power", "energy-power-laser-cleaning-applications"),
    # food processing
    ("food-processing-equipment-applications", "food-processing", "food-processing-laser-cleaning-applications"),
    ("food-processing-conveyor-applications", "food-processing", "food-processing-laser-cleaning-applications"),
    ("food-processing-mold-removal-applications", "food-processing", "food-processing-laser-cleaning-applications"),
    ("food-processing-grease-removal-applications", "food-processing", "food-processing-laser-cleaning-applications"),
    ("food-processing-sanitary-applications", "food-processing", "food-processing-laser-cleaning-applications"),
    # medical devices
    ("medical-device-applications", "medical-devices", "medical-devices-laser-cleaning-applications"),
    ("medical-precision-instruments-applications", "medical-devices", "medical-devices-laser-cleaning-applications"),
    ("medical-residue-removal-applications", "medical-devices", "medical-devices-laser-cleaning-applications"),
    ("medical-oxide-removal-applications", "medical-devices", "medical-devices-laser-cleaning-applications"),
    ("medical-surgical-tools-applications", "medical-devices", "medical-devices-laser-cleaning-applications"),
    # marine (renamed)
    ("marine-ship-hulls-applications", "marine", "marine-laser-cleaning-applications"),
    ("marine-corrosion-removal-applications", "marine", "marine-laser-cleaning-applications"),
    ("marine-paint-stripping-applications", "marine", "marine-laser-cleaning-applications"),
    ("marine-rust-removal-applications", "marine", "marine-laser-cleaning-applications"),
    ("marine-barnacle-removal-applications", "marine", "marine-laser-cleaning-applications"),
    ("marine-ndt-prep-applications", "marine", "marine-laser-cleaning-applications"),
    # welding prep
    ("welding-aluminum-applications", "welding-prep", "welding-prep-laser-cleaning-applications"),
    ("welding-steel-applications", "welding-prep", "welding-prep-laser-cleaning-applications"),
    ("welding-paint-coating-removal-applications", "welding-prep", "welding-prep-laser-cleaning-applications"),
    ("welding-rust-oxide-removal-applications", "welding-prep", "welding-prep-laser-cleaning-applications"),
    ("welding-weld-prep-applications", "welding-prep", "welding-prep-laser-cleaning-applications"),
    ("welding-ndt-surface-prep-applications", "welding-prep", "welding-prep-laser-cleaning-applications"),
]


def _load_yaml(path: Path) -> Dict:
    with open(path, "r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping root in {path}")
    return payload


def _write_yaml(path: Path, payload: Dict) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)


def _topic_from_item_id(item_id: str) -> str:
    if not item_id.endswith("-applications"):
        raise ValueError(f"Unexpected applications item id format: {item_id}")
    return item_id[: -len("-applications")]


def _rename_item_preserve_author(
    service: KeywordSeedService,
    item: Dict,
    new_id: str,
    subcategory: str,
) -> Dict:
    renamed = deepcopy(item)
    topic = _topic_from_item_id(new_id)
    topic_title = service._to_title(topic)
    page_title = service._build_page_title(topic_title)

    renamed["id"] = new_id
    renamed["slug"] = new_id
    renamed["name"] = topic_title
    renamed["displayName"] = page_title
    renamed["pageTitle"] = page_title
    renamed["fullPath"] = f"/applications/{new_id}"
    renamed["category"] = "applications"
    renamed["subcategory"] = subcategory

    now = datetime.now(timezone.utc)
    renamed["dateModified"] = now.isoformat()

    if isinstance(renamed.get("card"), dict):
        renamed["card"]["title"] = page_title
        renamed["card"]["description"] = service._build_summary_text(page_title)

    renamed["metaDescription"] = service._build_summary_text(page_title)
    renamed["keywords"] = service._unique_non_empty([page_title, topic_title])

    service._remove_legacy_root_relationship_fields(renamed)
    service._update_breadcrumb(
        item=renamed,
        topic_title=topic_title,
        category="applications",
        subcategory=subcategory,
        item_id=new_id,
        full_path=renamed["fullPath"],
    )
    return renamed


def _create_new_item(
    service: KeywordSeedService,
    template_item: Dict,
    item_id: str,
    subcategory: str,
) -> Dict:
    keyword = _topic_from_item_id(item_id)
    created = service._build_item_from_template(
        template_item=template_item,
        keyword=keyword,
        item_id=item_id,
        category="applications",
        subcategory=subcategory,
    )
    service._clear_generated_text_fields(created)
    return created


def main() -> int:
    service = KeywordSeedService("applications")
    payload = _load_yaml(SOURCE)
    items = payload.get("applications")
    if not isinstance(items, dict):
        raise ValueError("Expected 'applications' mapping in source payload")

    created: List[str] = []
    renamed: List[str] = []
    removed: List[str] = []

    # Ensure parent records used by breadcrumbs exist before child creation
    if "marine-laser-cleaning-applications" not in items:
        if "shipbuilding-marine-laser-cleaning-applications" in items:
            original = items.pop("shipbuilding-marine-laser-cleaning-applications")
            items["marine-laser-cleaning-applications"] = _rename_item_preserve_author(
                service,
                original,
                "marine-laser-cleaning-applications",
                "marine",
            )
            renamed.append("shipbuilding-marine-laser-cleaning-applications -> marine-laser-cleaning-applications")
        else:
            template = items["defense-laser-cleaning-applications"]
            items["marine-laser-cleaning-applications"] = _create_new_item(
                service,
                template,
                "marine-laser-cleaning-applications",
                "marine",
            )
            created.append("marine-laser-cleaning-applications")

    if "welding-prep-laser-cleaning-applications" not in items:
        template = items["automotive-laser-cleaning-applications"]
        items["welding-prep-laser-cleaning-applications"] = _create_new_item(
            service,
            template,
            "welding-prep-laser-cleaning-applications",
            "welding-prep",
        )
        created.append("welding-prep-laser-cleaning-applications")

    # Rename shipbuilding marine children to marine slugs
    for old_id, new_id in RENAME_MAP.items():
        if old_id in items and new_id not in items:
            original = items.pop(old_id)
            items[new_id] = _rename_item_preserve_author(service, original, new_id, "marine")
            renamed.append(f"{old_id} -> {new_id}")

    # Remove known obsolete IDs after rename
    for obsolete in sorted(REMOVE_IDS):
        if obsolete in items:
            del items[obsolete]
            removed.append(obsolete)

    # Ensure required records exist
    for item_id, subcategory, template_id in REQUIRED_SPECS:
        if item_id in items:
            continue
        template = items.get(template_id)
        if not isinstance(template, dict):
            raise KeyError(f"Missing template record required for {item_id}: {template_id}")
        items[item_id] = _create_new_item(service, template, item_id, subcategory)
        created.append(item_id)

    payload["lastUpdated"] = datetime.now(timezone.utc).date().isoformat()
    _write_yaml(SOURCE, payload)

    print({
        "source": str(SOURCE),
        "total_items": len(items),
        "created_count": len(created),
        "renamed_count": len(renamed),
        "removed_count": len(removed),
        "created": created,
        "renamed": renamed,
        "removed": removed,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
