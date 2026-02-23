#!/usr/bin/env python3
"""
Migrate all prompts/**/*.txt files into a single YAML catalog.

Phase 1 utility only:
- Builds consolidated prompt catalog
- Preserves every prompt in catalog.byPath (lossless mirror)
- Does not modify runtime loading behavior

Usage:
    python3 scripts/tools/migrate_prompts_to_yaml.py --dry-run
    python3 scripts/tools/migrate_prompts_to_yaml.py
    python3 scripts/tools/migrate_prompts_to_yaml.py --output prompts/registry/prompt_catalog.yaml
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import yaml

DOMAIN_NAMES = {"materials", "settings", "contaminants", "compounds", "applications"}


class LiteralString(str):
    """YAML helper type to force multiline literal block style."""


def literal_string_representer(dumper: yaml.Dumper, data: LiteralString) -> yaml.ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data), style="|")


yaml.SafeDumper.add_representer(LiteralString, literal_string_representer)


class PromptCatalogMigrationError(RuntimeError):
    """Raised when migration cannot safely proceed (fail-fast)."""


def as_literal(value: str) -> str:
    """Keep multiline prompts readable in YAML while preserving content."""
    if "\n" in value:
        return LiteralString(value)
    return value


def read_prompt_file(path: Path) -> str:
    if not path.exists():
        raise PromptCatalogMigrationError(f"Prompt file not found: {path}")

    content = path.read_text(encoding="utf-8")
    content = content.rstrip("\n")

    if not content.strip():
        raise PromptCatalogMigrationError(f"Prompt file is empty: {path}")

    return content


def build_empty_catalog() -> Dict[str, Any]:
    return {
        "schemaVersion": "1.0.0",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceRoot": "prompts",
        "catalog": {
            "shared": {
                "textPromptCore": "",
                "components": {},
            },
            "core": {
                "humanness": {
                    "full": "",
                    "compact": "",
                },
            },
            "quality": {
                "evaluation": "",
            },
            "domains": {
                "materials": {},
                "settings": {},
                "contaminants": {},
                "compounds": {},
                "applications": {},
            },
            "extras": {},
            "byPath": {},
        },
    }


def assign_prompt(catalog: Dict[str, Any], rel_path: str, content: str) -> None:
    """Assign prompt content into structured keys + lossless byPath mirror."""
    parts = rel_path.split("/")
    if len(parts) < 3:
        raise PromptCatalogMigrationError(
            f"Unexpected prompt path structure (expected prompts/<group>/<file>.txt): {rel_path}"
        )

    group = parts[1]
    filename = parts[-1]
    stem = Path(filename).stem

    catalog["catalog"]["byPath"][rel_path] = as_literal(content)

    if group in DOMAIN_NAMES and len(parts) == 3:
        catalog["catalog"]["domains"][group][stem] = as_literal(content)
        return

    if group == "shared" and len(parts) == 3 and filename == "text_prompt_core.txt":
        catalog["catalog"]["shared"]["textPromptCore"] = as_literal(content)
        return

    if group == "shared" and len(parts) == 4 and parts[2] == "components":
        catalog["catalog"]["shared"]["components"][stem] = as_literal(content)
        return

    if group == "core" and len(parts) == 3 and filename == "humanness_layer.txt":
        catalog["catalog"]["core"]["humanness"]["full"] = as_literal(content)
        return

    if group == "core" and len(parts) == 3 and filename == "humanness_layer_compact.txt":
        catalog["catalog"]["core"]["humanness"]["compact"] = as_literal(content)
        return

    if group == "quality" and len(parts) == 3 and filename == "evaluation.txt":
        catalog["catalog"]["quality"]["evaluation"] = as_literal(content)
        return

    catalog["catalog"]["extras"][rel_path] = as_literal(content)


def validate_catalog(catalog: Dict[str, Any], discovered_count: int) -> None:
    """Fail-fast validation for required migration outputs."""
    by_path_count = len(catalog["catalog"]["byPath"])
    if by_path_count != discovered_count:
        raise PromptCatalogMigrationError(
            f"Catalog byPath count mismatch: expected {discovered_count}, got {by_path_count}"
        )

    # Required top-level prompt groups for phase-1
    if not catalog["catalog"]["core"]["humanness"]["full"]:
        raise PromptCatalogMigrationError("Missing core humanness full prompt (humanness_layer.txt)")

    if not catalog["catalog"]["quality"]["evaluation"]:
        raise PromptCatalogMigrationError("Missing quality evaluation prompt (evaluation.txt)")

    if not catalog["catalog"]["shared"]["textPromptCore"]:
        raise PromptCatalogMigrationError("Missing shared text prompt core (text_prompt_core.txt)")


def gather_prompt_files(prompts_root: Path) -> List[Path]:
    if not prompts_root.exists():
        raise PromptCatalogMigrationError(f"Prompts root not found: {prompts_root}")

    txt_files = sorted(prompts_root.rglob("*.txt"), key=lambda path: path.as_posix())
    if not txt_files:
        raise PromptCatalogMigrationError(f"No .txt prompt files found under: {prompts_root}")

    return txt_files


def migrate(project_root: Path, output_path: Path, dry_run: bool) -> int:
    prompts_root = project_root / "prompts"
    txt_files = gather_prompt_files(prompts_root)

    catalog = build_empty_catalog()

    for txt_file in txt_files:
        rel_path = txt_file.relative_to(project_root).as_posix()
        content = read_prompt_file(txt_file)
        assign_prompt(catalog, rel_path, content)

    validate_catalog(catalog, discovered_count=len(txt_files))

    print("=" * 80)
    print("PROMPT CATALOG MIGRATION")
    print("=" * 80)
    print(f"Discovered .txt prompts: {len(txt_files)}")
    print(f"Domain prompt count: {sum(len(v) for v in catalog['catalog']['domains'].values())}")
    print(f"Shared components count: {len(catalog['catalog']['shared']['components'])}")
    print(f"Extras count: {len(catalog['catalog']['extras'])}")
    print(f"Output: {output_path}")

    if dry_run:
        print("\nDRY RUN: No file written.")
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file_handle:
        yaml.safe_dump(catalog, file_handle, sort_keys=False, allow_unicode=True, width=120)

    print("\n✅ Migration complete.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migrate prompts/**/*.txt into YAML prompt catalog")
    parser.add_argument(
        "--project-root",
        default=str(Path(__file__).resolve().parents[2]),
        help="Project root containing prompts/ (default: repository root)",
    )
    parser.add_argument(
        "--output",
        default="prompts/registry/prompt_catalog.yaml",
        help="Output catalog path, relative to project root",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate and report without writing output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    project_root = Path(args.project_root).resolve()
    output_path = (project_root / args.output).resolve()

    try:
        return migrate(project_root=project_root, output_path=output_path, dry_run=args.dry_run)
    except PromptCatalogMigrationError as error:
        print(f"❌ Migration failed: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
