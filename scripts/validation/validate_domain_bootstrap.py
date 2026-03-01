#!/usr/bin/env python3
"""Validate domain bootstrap wiring for command-ready generation.

This validator ensures a domain can be used immediately by CLI generation/export
commands after onboarding files are added.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


REQUIRED_DOMAIN_CONFIG_KEYS = ("data_path", "data_root_key", "frontmatter_pattern")


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"YAML root must be mapping: {path}")
    return payload


def _discover_domains(repo_root: Path) -> list[str]:
    domains_root = repo_root / "domains"
    if not domains_root.exists():
        return []
    return sorted(path.parent.name for path in domains_root.glob("*/config.yaml"))


def validate_domain(repo_root: Path, domain: str) -> list[str]:
    errors: list[str] = []

    domain_config_path = repo_root / "domains" / domain / "config.yaml"
    domain_prompt_path = repo_root / "domains" / domain / "prompt.yaml"
    domain_backfill_config_path = repo_root / "generation" / "backfill" / "config" / f"{domain}.yaml"
    domain_export_config_path = repo_root / "export" / "config" / f"{domain}.yaml"

    for required_path in (
        domain_config_path,
        domain_prompt_path,
        domain_backfill_config_path,
        domain_export_config_path,
    ):
        if not required_path.exists():
            errors.append(f"{domain}: missing required file {required_path.relative_to(repo_root)}")

    generation_config_path = repo_root / "generation" / "config.yaml"

    # Stop early for missing files so follow-on parsing errors stay focused.
    if errors:
        return errors

    try:
        domain_config = _load_yaml(domain_config_path)
    except Exception as exc:
        return [f"{domain}: invalid domain config {domain_config_path.relative_to(repo_root)} ({exc})"]

    for key in REQUIRED_DOMAIN_CONFIG_KEYS:
        value = domain_config.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{domain}: domains/{domain}/config.yaml missing required non-empty key '{key}'")

    data_path_value = domain_config.get("data_path")
    if isinstance(data_path_value, str) and data_path_value.strip():
        source_path = repo_root / data_path_value
        if not source_path.exists():
            errors.append(f"{domain}: data_path does not exist ({data_path_value})")

    try:
        domain_prompt_contract = _load_yaml(domain_prompt_path)
        prompt_contract = domain_prompt_contract.get("prompt_contract")
        if not isinstance(prompt_contract, dict):
            errors.append(f"{domain}: domains/{domain}/prompt.yaml missing required mapping 'prompt_contract'")
        else:
            configured_registry = prompt_contract.get("content_prompts_file")
            expected_registry = "prompts/registry/content_prompts_shared.yaml"
            if configured_registry != expected_registry:
                errors.append(
                    f"{domain}: prompt_contract.content_prompts_file must be '{expected_registry}' "
                    f"(found: {configured_registry!r})"
                )
    except Exception as exc:
        errors.append(f"{domain}: invalid prompt contract domains/{domain}/prompt.yaml ({exc})")

    try:
        generation_config = _load_yaml(generation_config_path)
    except Exception as exc:
        errors.append(f"{domain}: invalid generation/config.yaml ({exc})")
        return errors

    domain_generation = generation_config.get("domain_generation")
    if not isinstance(domain_generation, dict) or domain not in domain_generation:
        errors.append(f"{domain}: missing generation.config domain_generation.{domain}")

    field_router = generation_config.get("field_router")
    if not isinstance(field_router, dict):
        errors.append(f"{domain}: missing generation.config field_router block")
    else:
        field_types = field_router.get("field_types")
        field_aliases = field_router.get("field_aliases")
        data_generators = field_router.get("data_generators")

        if not isinstance(field_types, dict) or domain not in field_types:
            errors.append(f"{domain}: missing generation.config field_router.field_types.{domain}")
        if not isinstance(field_aliases, dict) or domain not in field_aliases:
            errors.append(f"{domain}: missing generation.config field_router.field_aliases.{domain}")
        if not isinstance(data_generators, dict) or domain not in data_generators:
            errors.append(f"{domain}: missing generation.config field_router.data_generators.{domain}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate domain bootstrap wiring")
    parser.add_argument("--domain", help="Validate one domain only")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    domains = [args.domain] if args.domain else _discover_domains(repo_root)

    if not domains:
        print("❌ No domains found under domains/*/config.yaml")
        return 1

    all_errors: list[str] = []
    for domain in domains:
        all_errors.extend(validate_domain(repo_root, domain))

    if all_errors:
        print("❌ Domain bootstrap validation failed:")
        for issue in all_errors:
            print(f"  - {issue}")
        return 1

    if args.domain:
        print(f"✅ Domain bootstrap validation passed for '{args.domain}'")
    else:
        print(f"✅ Domain bootstrap validation passed for {len(domains)} domain(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
