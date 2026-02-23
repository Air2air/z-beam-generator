#!/usr/bin/env python3
"""Remove non-verifiable entries from ExtractedLinkages.yaml.

Keeps only entries where:
- verified == true
- verification_source is a non-empty string
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from shared.utils.yaml_loader import load_yaml_fast as load_yaml
from shared.utils.yaml_loader import dump_yaml_fast as save_yaml

EXTRACTED_PATH = PROJECT_ROOT / "data" / "associations" / "ExtractedLinkages.yaml"


def _is_verifiable(entry: Dict[str, Any]) -> bool:
    verified = entry.get("verified") is True
    source = entry.get("verification_source")
    has_source = isinstance(source, str) and bool(source.strip())
    return verified and has_source


def main() -> int:
    data = load_yaml(EXTRACTED_PATH)
    if not isinstance(data, dict):
        raise ValueError("ExtractedLinkages.yaml must parse to a dictionary")

    removed = 0
    kept = 0

    for section_key in ["material_contaminant_associations", "contaminant_compound_associations"]:
        section = data.get(section_key)
        if section is None:
            section = []
        if not isinstance(section, list):
            raise ValueError(f"{section_key} must be a list")

        filtered = []
        for entry in section:
            if isinstance(entry, dict) and _is_verifiable(entry):
                filtered.append(entry)
                kept += 1
            else:
                removed += 1

        data[section_key] = filtered

    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}

    metadata["total_associations"] = kept
    metadata["verified"] = kept
    metadata["verification_rate"] = "100%" if kept else "0%"
    data["metadata"] = metadata

    save_yaml(data, EXTRACTED_PATH)

    print({
        "file": str(EXTRACTED_PATH),
        "kept": kept,
        "removed": removed,
    })

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
