#!/usr/bin/env python3
"""Validate catalog subject keywords resolve to exactly one source-data item ID per domain."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DOMAINS_ROOT = REPO_ROOT / "domains"


def _discover_domains() -> list[str]:
    if not DOMAINS_ROOT.exists():
        return []
    return sorted(path.parent.name for path in DOMAINS_ROOT.glob("*/config.yaml") if path.parent.name)


def _normalize_subject_keyword(domain: str, value: str) -> str:
    normalized = value.strip()
    if normalized.endswith('.yaml'):
        normalized = normalized[:-5]

    if domain == 'applications':
        normalized = normalized.replace('-laser-cleaning-', '-')
        if normalized.endswith('-applications'):
            normalized = normalized[:-13]
        if normalized.endswith('-laser-cleaning'):
            normalized = normalized[:-15]
    elif domain == 'materials':
        if normalized.endswith('-laser-cleaning'):
            normalized = normalized[:-15]
    elif domain == 'settings':
        if normalized.endswith('-settings'):
            normalized = normalized[:-9]
    elif domain == 'contaminants':
        if normalized.endswith('-contamination'):
            normalized = normalized[:-14]
    elif domain == 'compounds':
        if normalized.endswith('-compound'):
            normalized = normalized[:-9]

    return normalized.strip()


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path.relative_to(REPO_ROOT)}")

    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping in {path.relative_to(REPO_ROOT)}")
    return payload


def _load_catalog_subjects(domain: str) -> list[str]:
    catalog_path = REPO_ROOT / "domains" / domain / "catalog.yaml"
    catalog_payload = _load_yaml(catalog_path)

    article_pages = catalog_payload.get("article_pages")
    if not isinstance(article_pages, dict):
        raise ValueError(f"Missing required mapping article_pages in {catalog_path.relative_to(REPO_ROOT)}")

    file_names = article_pages.get("file_names")
    if not isinstance(file_names, list) or not file_names:
        raise ValueError(
            f"article_pages.file_names must be a non-empty list in {catalog_path.relative_to(REPO_ROOT)}"
        )

    normalized_subjects: list[str] = []
    seen_subjects: set[str] = set()

    for value in file_names:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"article_pages.file_names contains invalid value {value!r} in {catalog_path.relative_to(REPO_ROOT)}"
            )

        subject = _normalize_subject_keyword(domain, value)
        if not subject:
            raise ValueError(
                f"article_pages.file_names contains empty normalized subject {value!r} in {catalog_path.relative_to(REPO_ROOT)}"
            )

        if subject in seen_subjects:
            raise ValueError(
                f"article_pages.file_names contains duplicate normalized subject '{subject}' in {catalog_path.relative_to(REPO_ROOT)}"
            )

        seen_subjects.add(subject)
        normalized_subjects.append(subject)

    return normalized_subjects


def _load_source_item_keys(domain: str) -> list[str]:
    config_path = REPO_ROOT / "domains" / domain / "config.yaml"
    config_payload = _load_yaml(config_path)

    data_path_value = config_payload.get("data_path")
    data_root_key = config_payload.get("data_root_key")
    if not isinstance(data_path_value, str) or not data_path_value.strip():
        raise ValueError(f"Missing required non-empty data_path in {config_path.relative_to(REPO_ROOT)}")
    if not isinstance(data_root_key, str) or not data_root_key.strip():
        raise ValueError(f"Missing required non-empty data_root_key in {config_path.relative_to(REPO_ROOT)}")

    source_path = (REPO_ROOT / data_path_value).resolve()
    source_payload = _load_yaml(source_path)

    items = source_payload.get(data_root_key)
    if not isinstance(items, dict):
        raise ValueError(
            f"Expected mapping at root key '{data_root_key}' in {source_path.relative_to(REPO_ROOT)}"
        )

    return list(items.keys())


def _validate_domain(domain: str) -> list[str]:
    errors: list[str] = []

    catalog_subjects = _load_catalog_subjects(domain)
    source_item_keys = _load_source_item_keys(domain)

    keyword_to_items: dict[str, list[str]] = {}
    for item_key in source_item_keys:
        keyword = _normalize_subject_keyword(domain, item_key)
        keyword_to_items.setdefault(keyword, []).append(item_key)

    resolved_items: set[str] = set()

    for subject in catalog_subjects:
        matches = keyword_to_items.get(subject, [])

        if not matches:
            errors.append(
                f"{domain}: catalog subject '{subject}' missing in source data keys"
            )
            continue

        if len(matches) > 1:
            errors.append(
                f"{domain}: catalog subject '{subject}' maps to multiple source IDs: {', '.join(sorted(matches))}"
            )
            continue

        resolved_item = matches[0]
        if resolved_item in resolved_items:
            errors.append(
                f"{domain}: duplicate catalog mapping to source ID '{resolved_item}'"
            )
            continue

        resolved_items.add(resolved_item)

    return errors


def main() -> int:
    try:
        domains = _discover_domains()
        if not domains:
            print("❌ No domains discovered from domains/*/config.yaml")
            return 1

        all_errors: list[str] = []
        for domain in domains:
            all_errors.extend(_validate_domain(domain))

        if all_errors:
            print("❌ Catalog subject resolution validation failed:")
            for error in all_errors:
                print(f"  - {error}")
            return 1

        print("✅ Catalog subject resolution validation passed")
        print(f"   Domains validated: {', '.join(domains)}")
        return 0

    except Exception as exc:
        print(f"❌ Validation error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
