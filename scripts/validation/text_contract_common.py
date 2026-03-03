#!/usr/bin/env python3
"""Shared helpers for canonical text contract computation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

CANONICAL_DOMAINS = ("applications", "materials", "contaminants", "compounds", "settings")


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"YAML root must be mapping: {path}")
    return payload


def _normalize_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    output: list[str] = []
    for value in values:
        if isinstance(value, str) and value.strip():
            output.append(value.strip())
    return output


def compute_text_contract(repo_root: Path) -> dict[str, dict[str, list[str]]]:
    generation_cfg = load_yaml(repo_root / "generation/config.yaml")
    field_types = ((generation_cfg.get("field_router") or {}).get("field_types") or {})

    contract: dict[str, dict[str, list[str]]] = {}

    for domain in CANONICAL_DOMAINS:
        domain_types = field_types.get(domain)
        if not isinstance(domain_types, dict):
            raise ValueError(f"generation/config.yaml: missing field_router.field_types.{domain}")

        router_text_fields = sorted(set(_normalize_list(domain_types.get("text"))))

        backfill_cfg_path = repo_root / "generation/backfill/config" / f"{domain}.yaml"
        backfill_field_paths: set[str] = set()
        backfill_component_types: set[str] = set()

        if backfill_cfg_path.exists():
            backfill_cfg = load_yaml(backfill_cfg_path)
            generators = backfill_cfg.get("generators")
            if isinstance(generators, list):
                for generator in generators:
                    if not isinstance(generator, dict):
                        continue
                    if str(generator.get("type", "")).strip() != "multi_field_text":
                        continue
                    fields = generator.get("fields")
                    if not isinstance(fields, list):
                        continue
                    for field_mapping in fields:
                        if not isinstance(field_mapping, dict):
                            continue
                        field_path = field_mapping.get("field")
                        component_type = field_mapping.get("component_type")
                        if isinstance(field_path, str) and field_path.strip():
                            backfill_field_paths.add(field_path.strip())
                        if isinstance(component_type, str) and component_type.strip():
                            backfill_component_types.add(component_type.strip())

        expected_prompt_keys = sorted(
            set(router_text_fields)
            | backfill_field_paths
            | backfill_component_types
        )

        contract[domain] = {
            "router_text_fields": router_text_fields,
            "backfill_field_paths": sorted(backfill_field_paths),
            "backfill_component_types": sorted(backfill_component_types),
            "expected_prompt_keys": expected_prompt_keys,
        }

    return contract
