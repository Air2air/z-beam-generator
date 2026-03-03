#!/usr/bin/env python3
"""Validate generated text contract artifact and required prompt-key coverage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import text_contract_common as contract_common  # pyright: ignore[reportMissingImports]

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_artifact(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing artifact: {path}. Run scripts/validation/generate_text_contract_artifact.py first."
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Artifact root must be an object: {path}")
    return payload


def _domain_text_prompt_keys(repo_root: Path, domain: str) -> set[str]:
    prompt_contract = contract_common.load_yaml(repo_root / "domains" / domain / "prompt.yaml").get("prompt_contract")
    if not isinstance(prompt_contract, dict):
        raise ValueError(f"domains/{domain}/prompt.yaml missing prompt_contract")

    text_prompts_file = prompt_contract.get("text_prompts_file")
    if not isinstance(text_prompts_file, str) or not text_prompts_file.strip():
        raise ValueError(f"domains/{domain}/prompt.yaml missing prompt_contract.text_prompts_file")

    text_prompt = contract_common.load_yaml(repo_root / text_prompts_file.strip())
    field_prompts = text_prompt.get("field_prompts")
    if not isinstance(field_prompts, dict):
        raise ValueError(f"{text_prompts_file}: field_prompts must be a mapping")

    return {key.strip() for key in field_prompts if isinstance(key, str) and key.strip()}


def _missing_section_title_pairs(prompt_keys: set[str]) -> list[str]:
    missing: list[str] = []
    for key in sorted(prompt_keys):
        if not key.endswith("sectionDescription"):
            continue
        expected_title_key = key[: -len("sectionDescription")] + "sectionTitle"
        if expected_title_key not in prompt_keys:
            missing.append(f"{key} -> {expected_title_key}")
    return missing


def _single_line_keys(repo_root: Path, domain: str) -> set[str]:
    payload = contract_common.load_yaml(repo_root / "data/schemas/component_single_line_prompts.yaml")
    by_domain = ((payload.get("component_single_line_prompts") or {}).get("by_domain") or {})
    domain_map = by_domain.get(domain)
    if not isinstance(domain_map, dict):
        raise ValueError(f"component_single_line_prompts.by_domain.{domain} must be a mapping")
    return {key.strip() for key in domain_map if isinstance(key, str) and key.strip()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate generated text contract artifact")
    parser.add_argument(
        "--artifact",
        default="tasks/text_contract_artifact.json",
        help="Path to text contract artifact JSON",
    )
    args = parser.parse_args()

    repo_root = REPO_ROOT
    artifact_path = repo_root / args.artifact

    errors: list[str] = []

    try:
        artifact = _load_artifact(artifact_path)
    except Exception as exc:
        print(f"❌ {exc}")
        return 1

    live_contract = contract_common.compute_text_contract(repo_root)
    artifact_domains = artifact.get("domains")
    if not isinstance(artifact_domains, dict):
        print(f"❌ {artifact_path}: missing 'domains' object")
        return 1

    for domain in contract_common.CANONICAL_DOMAINS:
        live = live_contract.get(domain)
        art = artifact_domains.get(domain)
        if not isinstance(live, dict) or not isinstance(art, dict):
            errors.append(f"{domain}: missing domain block in live/artifact contract")
            continue

        if live != art:
            errors.append(
                f"{domain}: artifact drift detected. Regenerate with scripts/validation/generate_text_contract_artifact.py"
            )

        expected_prompt_keys = set(live.get("expected_prompt_keys", []))
        router_text_fields = set(live.get("router_text_fields", []))

        text_prompt_keys = _domain_text_prompt_keys(repo_root, domain)
        missing_text_prompt = sorted(expected_prompt_keys - text_prompt_keys)
        if missing_text_prompt:
            errors.append(
                f"{domain}: domains/*/prompts/text_prompt.yaml missing keys: {', '.join(missing_text_prompt)}"
            )

        missing_title_pairs = _missing_section_title_pairs(text_prompt_keys)
        if missing_title_pairs:
            errors.append(
                f"{domain}: sectionDescription keys missing sectionTitle counterparts: {', '.join(missing_title_pairs)}"
            )

        single_line_keys = _single_line_keys(repo_root, domain)
        missing_single_line = sorted(router_text_fields - single_line_keys)
        if missing_single_line:
            errors.append(
                f"{domain}: component_single_line_prompts missing router text keys: {', '.join(missing_single_line)}"
            )

    if errors:
        print("❌ Text contract artifact validation failed:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("✅ Text contract artifact validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
