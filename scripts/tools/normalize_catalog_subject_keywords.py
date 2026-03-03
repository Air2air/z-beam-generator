#!/usr/bin/env python3
"""Normalize domain catalog article file names to subject keywords."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

DOMAINS = ("applications", "materials", "contaminants", "compounds", "settings")


def normalize_subject_keyword(domain: str, value: str) -> str:
    normalized = value.strip()
    if normalized.endswith(".yaml"):
        normalized = normalized[:-5]

    if domain == "applications":
        normalized = normalized.replace("-laser-cleaning-", "-")
        if normalized.endswith("-applications"):
            normalized = normalized[:-13]
        if normalized.endswith("-laser-cleaning"):
            normalized = normalized[:-15]
    elif domain == "materials":
        if normalized.endswith("-laser-cleaning"):
            normalized = normalized[:-15]
    elif domain == "settings":
        if normalized.endswith("-settings"):
            normalized = normalized[:-9]
    elif domain == "contaminants":
        if normalized.endswith("-contamination"):
            normalized = normalized[:-14]
    elif domain == "compounds":
        if normalized.endswith("-compound"):
            normalized = normalized[:-9]

    return normalized.strip()


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return payload


def save_yaml(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]

    for domain in DOMAINS:
        catalog_path = repo_root / "domains" / domain / "catalog.yaml"
        if not catalog_path.exists():
            continue

        payload = load_yaml(catalog_path)
        article_pages = payload.get("article_pages")
        if not isinstance(article_pages, dict):
            continue

        file_names = article_pages.get("file_names")
        if not isinstance(file_names, list):
            continue

        normalized_names = [
            normalize_subject_keyword(domain, value)
            for value in file_names
            if isinstance(value, str) and value.strip()
        ]

        if len(normalized_names) != len(file_names):
            raise ValueError(f"Invalid non-string/empty file_names entries in {catalog_path}")
        if len(set(normalized_names)) != len(normalized_names):
            raise ValueError(f"Duplicate normalized file_names detected in {catalog_path}")

        article_pages["file_names"] = normalized_names
        save_yaml(catalog_path, payload)
        print(f"normalized {catalog_path.relative_to(repo_root)} ({len(normalized_names)} entries)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
