#!/usr/bin/env python3
"""Verify relationship tables for AI-researched verifiability requirements."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from shared.utils.yaml_utils import load_yaml_fast as load_yaml

ASSOC_DIR = PROJECT_ROOT / "data" / "associations"


def _is_non_empty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _load(path: Path) -> Dict[str, Any]:
    data = load_yaml(path)
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must parse to a dictionary")
    return data


def _verify_extracted(path: Path) -> Dict[str, int]:
    data = _load(path)
    sections = ["material_contaminant_associations", "contaminant_compound_associations"]

    total = 0
    unverifiable = 0

    for section in sections:
        entries = data.get(section, [])
        if not isinstance(entries, list):
            raise ValueError(f"{path.name} {section} must be a list")
        for entry in entries:
            total += 1
            if not isinstance(entry, dict):
                unverifiable += 1
                continue
            if not (entry.get("verified") is True and _is_non_empty_str(entry.get("verification_source"))):
                unverifiable += 1

    return {"total": total, "unverifiable": unverifiable}


def _verify_material_application(path: Path) -> Dict[str, int]:
    data = _load(path)
    links = data.get("links", [])
    if not isinstance(links, list):
        raise ValueError(f"{path.name} links must be a list")

    total = 0
    unverifiable = 0

    for link in links:
        total += 1
        if not isinstance(link, dict):
            unverifiable += 1
            continue

        eligibility = link.get("eligibility")
        provenance = link.get("provenance")
        status = link.get("status")

        valid_eligibility = (
            isinstance(eligibility, dict)
            and eligibility.get("ai_researched_specific_to_material") is True
            and eligibility.get("application_domain_entry_exists") is True
        )

        if not (valid_eligibility and _is_non_empty_str(provenance) and status == "eligible"):
            unverifiable += 1

    return {"total": total, "unverifiable": unverifiable}


def _verify_domain_associations(path: Path) -> Dict[str, int]:
    data = _load(path)
    associations = data.get("associations", [])
    if not isinstance(associations, list):
        raise ValueError(f"{path.name} associations must be a list")

    total = len(associations)
    unverifiable = 0

    for assoc in associations:
        if not isinstance(assoc, dict):
            unverifiable += 1
            continue
        if not (assoc.get("verified") is True and _is_non_empty_str(assoc.get("verification_source"))):
            unverifiable += 1

    return {"total": total, "unverifiable": unverifiable}


def main() -> int:
    extracted = _verify_extracted(ASSOC_DIR / "ExtractedLinkages.yaml")
    material_app = _verify_material_application(ASSOC_DIR / "MaterialApplicationRelationships.yaml")
    domain = _verify_domain_associations(ASSOC_DIR / "DomainAssociations.yaml")

    report = {
        "ExtractedLinkages": extracted,
        "MaterialApplicationRelationships": material_app,
        "DomainAssociations": domain,
    }

    print(report)

    total_unverifiable = (
        extracted["unverifiable"]
        + material_app["unverifiable"]
        + domain["unverifiable"]
    )

    return 0 if total_unverifiable == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
