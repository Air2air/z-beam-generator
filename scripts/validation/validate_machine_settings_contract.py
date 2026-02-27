#!/usr/bin/env python3
"""Validate settings machineSettings contract.

Rules enforced:
- machineSettings schema prompt_ref must exist in shared inline prompt maps

Strict mode (`--check-settings-data`) also enforces:
- machineSettings leaf nodes must not contain `description`
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


REQUIRED_SHARED_PROMPT_KEYS = ("section_prompts", "section_prompt_metadata")


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be mapping: {path}")
    return data


def validate_machine_settings_leaf_descriptions(settings_path: Path) -> list[str]:
    errors: list[str] = []
    payload = load_yaml(settings_path)

    settings_root = payload.get("settings")
    if not isinstance(settings_root, dict):
        return [f"{settings_path}: missing required top-level mapping 'settings'"]

    for item_id, item_data in settings_root.items():
        if not isinstance(item_data, dict):
            errors.append(f"{settings_path}: settings.{item_id} must be a mapping")
            continue

        machine_settings = item_data.get("machineSettings")
        if not isinstance(machine_settings, dict):
            continue

        for leaf_key, leaf_value in machine_settings.items():
            if leaf_key == "_section" or not isinstance(leaf_value, dict):
                continue
            if "description" in leaf_value:
                errors.append(
                    f"{settings_path}: settings.{item_id}.machineSettings.{leaf_key}.description is forbidden"
                )

    return errors


def validate_prompt_schema_wiring(repo_root: Path) -> list[str]:
    errors: list[str] = []

    schema_path = repo_root / "data/schemas/section_display_schema.yaml"
    schema = load_yaml(schema_path)
    sections = schema.get("sections")
    if not isinstance(sections, dict):
        return [f"{schema_path}: missing required mapping 'sections'"]

    machine_settings_schema = sections.get("machineSettings")
    if not isinstance(machine_settings_schema, dict):
        return [f"{schema_path}: missing required sections.machineSettings mapping"]

    prompt_ref = machine_settings_schema.get("prompt_ref")
    if not isinstance(prompt_ref, str) or not prompt_ref.strip():
        return [f"{schema_path}: sections.machineSettings.prompt_ref must be a non-empty string"]

    shared_inline_path = repo_root / "prompts/shared/section_inline_prompts.yaml"
    shared_inline = load_yaml(shared_inline_path)

    for key in REQUIRED_SHARED_PROMPT_KEYS:
        if not isinstance(shared_inline.get(key), dict):
            errors.append(f"{shared_inline_path}: missing required mapping '{key}'")

    section_prompts = shared_inline.get("section_prompts")
    section_prompt_metadata = shared_inline.get("section_prompt_metadata")
    if not isinstance(section_prompts, dict) or not isinstance(section_prompt_metadata, dict):
        return errors

    if prompt_ref not in section_prompts:
        errors.append(f"{shared_inline_path}: missing section_prompts.{prompt_ref} required by schema")
    if prompt_ref not in section_prompt_metadata:
        errors.append(f"{shared_inline_path}: missing section_prompt_metadata.{prompt_ref} required by schema")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate machineSettings contract")
    parser.add_argument(
        "--check-settings-data",
        action="store_true",
        help="Also validate settings source data for forbidden machineSettings leaf descriptions",
    )
    parser.add_argument(
        "--include-shared-data",
        action="store_true",
        help="With --check-settings-data, also validate shared/data/settings/Settings.yaml mirror",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]

    errors: list[str] = []
    errors.extend(validate_prompt_schema_wiring(repo_root))

    if args.check_settings_data:
        checks = [repo_root / "data/settings/Settings.yaml"]
        if args.include_shared_data:
            checks.append(repo_root / "shared/data/settings/Settings.yaml")

        for path in checks:
            if path.exists():
                errors.extend(validate_machine_settings_leaf_descriptions(path))

    if errors:
        print("❌ machineSettings contract validation failed:")
        for issue in errors:
            print(f"  - {issue}")
        return 1

    print("✅ machineSettings contract validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
