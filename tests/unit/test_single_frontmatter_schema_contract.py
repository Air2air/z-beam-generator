"""Regression checks for the single canonical frontmatter schema model."""

from pathlib import Path

import yaml


def test_single_canonical_frontmatter_schema_exists() -> None:
    schema_path = Path("schemas/all_domains_schema.yaml")
    assert schema_path.exists(), "Expected canonical frontmatter schema at schemas/all_domains_schema.yaml"


def test_canonical_schema_defines_core_cross_domain_sections() -> None:
    schema = yaml.safe_load(Path("schemas/all_domains_schema.yaml").read_text(encoding="utf-8"))
    properties = schema.get("properties", {})

    for field_name in [
        "pageTitle",
        "pageDescription",
        "metaDescription",
        "breadcrumbs",
        "card",
        "eeat",
        "author",
        "properties",
        "removalMethods",
        "machineSettings",
        "applications",
        "faq",
    ]:
        assert field_name in properties, f"Expected canonical schema to define {field_name}"


def test_removed_legacy_schema_files_are_absent() -> None:
    removed_schema_paths = [
        Path("data/schemas/frontmatter.json"),
        Path("domains/contaminants/schema.json"),
        Path("domains/contaminants/schema.yaml"),
    ]

    for schema_path in removed_schema_paths:
        assert not schema_path.exists(), f"Legacy schema should have been removed: {schema_path}"


def test_duplicate_domain_schema_contract_files_are_absent() -> None:
    schema_dir = Path("schemas")
    duplicate_contracts = sorted(path.name for path in schema_dir.glob("*.schema.yaml"))
    assert duplicate_contracts == [], (
        "Duplicate per-domain schema contracts reintroduced in schemas/: "
        f"{duplicate_contracts}"
    )