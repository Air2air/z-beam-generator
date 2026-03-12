"""Regression checks for the single canonical frontmatter schema model."""

from pathlib import Path


def test_single_canonical_frontmatter_schema_exists() -> None:
    schema_path = Path("data/schemas/frontmatter.json")
    assert schema_path.exists(), "Expected canonical frontmatter schema at data/schemas/frontmatter.json"


def test_duplicate_domain_schema_contract_files_are_absent() -> None:
    schema_dir = Path("schemas")
    duplicate_contracts = sorted(path.name for path in schema_dir.glob("*.schema.yaml"))
    assert duplicate_contracts == [], (
        "Duplicate per-domain schema contracts reintroduced in schemas/: "
        f"{duplicate_contracts}"
    )