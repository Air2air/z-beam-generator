#!/usr/bin/env python3
"""Validate prompt section metadata contract and frontend/backend naming parity."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml


REQUIRED_METADATA_FIELDS = ("sectionTitle", "sectionDescription", "sectionMetadata")


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be mapping: {path}")
    return data


def parse_string_union_block(ts_text: str, alias: str) -> set[str]:
    pattern = rf"export type {alias}\s*=\s*(.*?);\n\n"
    match = re.search(pattern, ts_text, re.S)
    if not match:
        raise ValueError(f"Could not parse union type '{alias}'")
    return {m.group(1) for m in re.finditer(r"'([^']+)'", match.group(1))}


def validate_prompt_files(repo_root: Path) -> list[str]:
    errors: list[str] = []

    content_prompt_files = sorted((repo_root / "prompts").glob("*/content_prompts.yaml"))
    for prompt_file in content_prompt_files:
        payload = load_yaml(prompt_file)
        section_prompt_metadata = payload.get("section_prompt_metadata")
        if not isinstance(section_prompt_metadata, dict):
            errors.append(
                f"{prompt_file}: missing required top-level mapping 'section_prompt_metadata'"
            )

    shared_inline_path = repo_root / "prompts/shared/section_inline_prompts.yaml"
    shared_inline = load_yaml(shared_inline_path)
    section_prompts = shared_inline.get("section_prompts")
    section_prompt_metadata = shared_inline.get("section_prompt_metadata")

    if not isinstance(section_prompts, dict):
        errors.append(f"{shared_inline_path}: 'section_prompts' must be a mapping")
        return errors
    if not isinstance(section_prompt_metadata, dict):
        errors.append(f"{shared_inline_path}: 'section_prompt_metadata' must be a mapping")
        return errors

    for key, value in section_prompts.items():
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{shared_inline_path}: section_prompts.{key} must be a non-empty string")

        meta = section_prompt_metadata.get(key)
        if not isinstance(meta, dict):
            errors.append(f"{shared_inline_path}: missing section_prompt_metadata.{key}")
            continue

        for required in REQUIRED_METADATA_FIELDS:
            if required not in meta:
                errors.append(
                    f"{shared_inline_path}: section_prompt_metadata.{key} missing '{required}'"
                )

        section_meta_payload = meta.get("sectionMetadata")
        if not isinstance(section_meta_payload, dict):
            errors.append(
                f"{shared_inline_path}: section_prompt_metadata.{key}.sectionMetadata must be a mapping"
            )

    schema_path = repo_root / "data/schemas/section_display_schema.yaml"
    schema = load_yaml(schema_path)
    sections = schema.get("sections")
    if not isinstance(sections, dict):
        errors.append(f"{schema_path}: sections must be a mapping")
        return errors

    prompt_refs = {
        section_data.get("prompt_ref")
        for section_data in sections.values()
        if isinstance(section_data, dict)
    }
    prompt_refs = {ref for ref in prompt_refs if isinstance(ref, str) and ref.strip()}

    for prompt_ref in sorted(prompt_refs):
        if prompt_ref not in section_prompts:
            errors.append(f"{shared_inline_path}: missing section_prompts.{prompt_ref} required by schema prompt_ref")
        if prompt_ref not in section_prompt_metadata:
            errors.append(f"{shared_inline_path}: missing section_prompt_metadata.{prompt_ref} required by schema prompt_ref")

    return errors


def collect_relationship_shape(frontmatter_root: Path) -> tuple[set[str], set[str]]:
    categories: set[str] = set()
    keys: set[str] = set()

    for domain_dir in sorted(frontmatter_root.iterdir()):
        if not domain_dir.is_dir():
            continue
        for page in domain_dir.glob("*.yaml"):
            payload = load_yaml(page)
            relationships = payload.get("relationships")
            if not isinstance(relationships, dict):
                continue
            for category, section_map in relationships.items():
                if not isinstance(section_map, dict):
                    continue
                categories.add(category)
                for key, value in section_map.items():
                    if key == "_section":
                        continue
                    if isinstance(value, dict):
                        keys.add(key)

    return categories, keys


def validate_naming_parity(repo_root: Path) -> list[str]:
    errors: list[str] = []

    frontend_types_path = repo_root.parent / "z-beam/types/relationships.ts"
    frontend_types = frontend_types_path.read_text(encoding="utf-8")

    categories_in_types = parse_string_union_block(frontend_types, "RelationshipCategory")
    keys_in_types = parse_string_union_block(frontend_types, "RelationshipKey")

    frontmatter_root = repo_root.parent / "z-beam/frontmatter"
    runtime_categories, runtime_keys = collect_relationship_shape(frontmatter_root)

    missing_categories = sorted(runtime_categories - categories_in_types)
    missing_keys = sorted(runtime_keys - keys_in_types)

    if missing_categories:
        errors.append(
            "types/relationships.ts RelationshipCategory missing: "
            + ", ".join(missing_categories)
        )
    if missing_keys:
        errors.append(
            "types/relationships.ts RelationshipKey missing: "
            + ", ".join(missing_keys)
        )

    return errors


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]

    errors: list[str] = []
    errors.extend(validate_prompt_files(repo_root))
    errors.extend(validate_naming_parity(repo_root))

    if errors:
        print("❌ Prompt/section contract validation failed:")
        for issue in errors:
            print(f"  - {issue}")
        return 1

    print("✅ Prompt/section contract validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
