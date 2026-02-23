#!/usr/bin/env python3
"""Enforce verification-only entries in DomainAssociations.yaml.

Rules:
- association.verified must be True
- association.verification_source must be a non-empty string

Default mode is check-only (exit 1 if violations found).
Use --write to remove non-verifiable entries in-place.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from shared.utils.yaml_loader import load_yaml_fast as load_yaml
from shared.utils.yaml_loader import dump_yaml_fast as save_yaml

DOMAIN_ASSOCIATIONS_PATH = PROJECT_ROOT / "data" / "associations" / "DomainAssociations.yaml"


def _is_verified(association: Dict[str, Any]) -> bool:
    return (
        association.get("verified") is True
        and isinstance(association.get("verification_source"), str)
        and bool(association["verification_source"].strip())
    )


def enforce(write: bool) -> Dict[str, int]:
    data = load_yaml(DOMAIN_ASSOCIATIONS_PATH)
    if not isinstance(data, dict):
        raise ValueError("DomainAssociations.yaml must parse to a dictionary")

    associations = data.get("associations")
    if not isinstance(associations, list):
        raise ValueError("DomainAssociations.yaml key 'associations' must be a list")

    kept: List[Dict[str, Any]] = []
    removed = 0

    for entry in associations:
        if isinstance(entry, dict) and _is_verified(entry):
            kept.append(entry)
        else:
            removed += 1

    if write and removed > 0:
        data["associations"] = kept

        metadata = data.get("metadata")
        if not isinstance(metadata, dict):
            metadata = {}

        metadata["total_associations"] = len(kept)
        metadata["verified"] = len(kept)
        metadata["verification_rate"] = "100%" if kept else "0%"
        data["metadata"] = metadata

        save_yaml(data, DOMAIN_ASSOCIATIONS_PATH)

    return {
        "total": len(associations),
        "kept": len(kept),
        "removed": removed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Enforce verified-only DomainAssociations entries")
    parser.add_argument("--write", action="store_true", help="Remove non-verifiable entries")
    args = parser.parse_args()

    stats = enforce(write=args.write)
    mode = "WRITE" if args.write else "CHECK"
    print({"mode": mode, **stats})

    if not args.write and stats["removed"] > 0:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
