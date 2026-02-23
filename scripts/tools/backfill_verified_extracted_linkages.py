#!/usr/bin/env python3
"""Backfill ExtractedLinkages.yaml from verified DomainAssociations entries only.

Eligibility for inclusion:
- association.verified == True
- association.verification_source is a non-empty string

This script never invents relationships; it only projects verified associations
into the ExtractedLinkages schema.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any, Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from shared.utils.yaml_loader import load_yaml_fast as load_yaml
from shared.utils.yaml_loader import dump_yaml_fast as save_yaml

DOMAIN_ASSOCIATIONS_PATH = PROJECT_ROOT / "data" / "associations" / "DomainAssociations.yaml"
EXTRACTED_LINKAGES_PATH = PROJECT_ROOT / "data" / "associations" / "ExtractedLinkages.yaml"


def _is_verified(assoc: Dict[str, Any]) -> bool:
    return assoc.get("verified") is True and isinstance(assoc.get("verification_source"), str) and bool(assoc["verification_source"].strip())


def _load_associations() -> List[Dict[str, Any]]:
    data = load_yaml(DOMAIN_ASSOCIATIONS_PATH)
    if not isinstance(data, dict):
        raise ValueError("DomainAssociations.yaml must parse to a dictionary")
    associations = data.get("associations")
    if not isinstance(associations, list):
        raise ValueError("DomainAssociations.yaml key 'associations' must be a list")
    return [a for a in associations if isinstance(a, dict)]


def _project_material_contaminant(assocs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    results: List[Dict[str, Any]] = []

    for assoc in assocs:
        if not _is_verified(assoc):
            continue

        source_domain = assoc.get("source_domain")
        target_domain = assoc.get("target_domain")
        relation = assoc.get("relationship_type")

        material_id = None
        contaminant_id = None

        if source_domain == "materials" and target_domain == "contaminants" and relation == "can_have_contamination":
            material_id = assoc.get("source_id")
            contaminant_id = assoc.get("target_id")
        elif source_domain == "contaminants" and target_domain == "materials" and relation == "can_contaminate":
            material_id = assoc.get("target_id")
            contaminant_id = assoc.get("source_id")
        else:
            continue

        if not isinstance(material_id, str) or not isinstance(contaminant_id, str):
            continue

        key = (material_id, contaminant_id)
        if key in seen:
            continue
        seen.add(key)

        results.append({
            "material_id": material_id,
            "contaminant_id": contaminant_id,
            "frequency": assoc.get("frequency"),
            "severity": assoc.get("severity"),
            "typical_context": assoc.get("typical_context"),
            "verified": True,
            "verification_source": assoc.get("verification_source"),
        })

    return sorted(results, key=lambda x: (x["material_id"], x["contaminant_id"]))


def _project_contaminant_compound(assocs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    results: List[Dict[str, Any]] = []

    for assoc in assocs:
        if not _is_verified(assoc):
            continue

        source_domain = assoc.get("source_domain")
        target_domain = assoc.get("target_domain")
        relation = assoc.get("relationship_type")

        contaminant_id = None
        compound_id = None

        if source_domain == "contaminants" and target_domain == "compounds" and relation == "generates_byproduct":
            contaminant_id = assoc.get("source_id")
            compound_id = assoc.get("target_id")
        elif source_domain == "compounds" and target_domain == "contaminants" and relation == "byproduct_of":
            contaminant_id = assoc.get("target_id")
            compound_id = assoc.get("source_id")
        else:
            continue

        if not isinstance(contaminant_id, str) or not isinstance(compound_id, str):
            continue

        key = (contaminant_id, compound_id)
        if key in seen:
            continue
        seen.add(key)

        results.append({
            "contaminant_id": contaminant_id,
            "compound_id": compound_id,
            "frequency": assoc.get("frequency"),
            "severity": assoc.get("severity"),
            "typical_context": assoc.get("typical_context"),
            "verified": True,
            "verification_source": assoc.get("verification_source"),
        })

    return sorted(results, key=lambda x: (x["contaminant_id"], x["compound_id"]))


def main() -> int:
    assocs = _load_associations()

    material_contaminant = _project_material_contaminant(assocs)
    contaminant_compound = _project_contaminant_compound(assocs)

    total = len(material_contaminant) + len(contaminant_compound)

    output = {
        "metadata": {
            "extracted_from": "DomainAssociations.yaml (verified entries only)",
            "total_associations": total,
            "verified": total,
            "verification_rate": "100%" if total else "0%",
        },
        "material_contaminant_associations": material_contaminant,
        "contaminant_compound_associations": contaminant_compound,
        "material_compound_associations": [],
    }

    save_yaml(output, EXTRACTED_LINKAGES_PATH)

    print({
        "written": str(EXTRACTED_LINKAGES_PATH),
        "material_contaminant_associations": len(material_contaminant),
        "contaminant_compound_associations": len(contaminant_compound),
        "total": total,
    })

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
