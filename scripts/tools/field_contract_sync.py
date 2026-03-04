#!/usr/bin/env python3
"""Synchronize domain field-contract artifacts from canonical router definitions.

Phase 2 scope (current):
- Canonical source: generation/config.yaml -> field_router.field_types.<domain>.text
- Target artifact: prompts/registry/component_prompt_registry.yaml
- Preserves domain-specific field sets (per-domain sync only)
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

CANONICAL_DOMAINS = ("applications", "materials", "contaminants", "compounds", "settings")
COMPONENT_PROMPT_REGISTRY_RELATIVE_PATH = Path("prompts/registry/component_prompt_registry.yaml")


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"YAML root must be mapping: {path}")
    return payload


def _save_yaml(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)


def _normalize_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    out: list[str] = []
    for value in values:
        if isinstance(value, str) and value.strip():
            out.append(value.strip())
    return out


def _default_prompt_for_field(domain: str, field: str) -> str:
    common_templates = {
        "pageTitle": "Write a concise {context} page title for {subject}.",
        "pageDescription": "Describe what {subject} is and why it matters in {context}.",
        "faq": "Provide concise FAQ content for {subject} relevant to {context} using practical evidence and domain-specific details.",
        "micro": "Describe the before-and-after surface transformation of {subject} in {context}.",
    }
    if field in common_templates:
        return common_templates[field]

    # Generic fallback keeps domain-specific field names intact without introducing hardcoded business values.
    return f"Describe {field} considerations for {{subject}} in {{context}} within the {domain} domain."


def _has_text_content(entry: Any) -> bool:
    if not isinstance(entry, dict):
        return False
    for key in ("prompt", "sectionTitle", "sectionDescription"):
        value = entry.get(key)
        if isinstance(value, str) and value.strip():
            return True
    return False


def _component_registry_path(repo_root: Path) -> Path:
    return repo_root / COMPONENT_PROMPT_REGISTRY_RELATIVE_PATH


@dataclass
class SyncResult:
    domain: str
    added_fields: list[str]
    removed_fields: list[str]
    unchanged_fields: list[str]



def _sync_domain_prompts(
    components: dict[str, Any],
    domain: str,
    router_text_fields: list[str],
    prune_extras: bool,
) -> SyncResult:
    canonical_order = list(dict.fromkeys(router_text_fields))
    existing_keys = {key for key in components.keys() if isinstance(key, str)}
    router_keys = set(canonical_order)

    added_fields = sorted(router_keys - existing_keys)
    removed_fields: list[str] = []
    unchanged_fields: list[str] = []

    for field in canonical_order:
        component_entry = components.get(field)
        if not isinstance(component_entry, dict):
            component_entry = {
                "descriptor": {"shared": None, "domains": {}},
                "text": {"shared": None, "domains": {}},
            }
            components[field] = component_entry

        text_entry = component_entry.get("text")
        if not isinstance(text_entry, dict):
            text_entry = {"shared": None, "domains": {}}
            component_entry["text"] = text_entry

        if "shared" not in text_entry:
            text_entry["shared"] = None
        domains_entry = text_entry.get("domains")
        if not isinstance(domains_entry, dict):
            domains_entry = {}
            text_entry["domains"] = domains_entry

        shared_entry = text_entry.get("shared")
        domain_entry = domains_entry.get(domain)

        if _has_text_content(domain_entry) or _has_text_content(shared_entry):
            unchanged_fields.append(field)
            continue

        domains_entry[domain] = {"prompt": _default_prompt_for_field(domain, field)}

    if prune_extras:
        for extra_key in sorted(existing_keys - router_keys):
            component_entry = components.get(extra_key)
            if not isinstance(component_entry, dict):
                continue
            text_entry = component_entry.get("text")
            if not isinstance(text_entry, dict):
                continue
            domains_entry = text_entry.get("domains")
            if isinstance(domains_entry, dict) and domain in domains_entry:
                del domains_entry[domain]
                removed_fields.append(extra_key)

    return SyncResult(
        domain=domain,
        added_fields=added_fields,
        removed_fields=removed_fields,
        unchanged_fields=sorted(set(unchanged_fields) & router_keys),
    )



def main() -> int:
    parser = argparse.ArgumentParser(description="Sync field-contract prompt coverage from canonical router config")
    parser.add_argument("--domain", choices=CANONICAL_DOMAINS, help="Sync one domain")
    parser.add_argument("--all-domains", action="store_true", help="Sync all canonical domains")
    parser.add_argument("--write", action="store_true", help="Persist updates to YAML files")
    parser.add_argument(
        "--prune-extras",
        action="store_true",
        help="Remove prompt fields not present in canonical router text fields",
    )
    args = parser.parse_args()

    if not args.domain and not args.all_domains:
        parser.error("Provide --domain <name> or --all-domains")

    repo_root = Path(__file__).resolve().parents[2]
    generation_path = repo_root / "generation/config.yaml"

    generation_cfg = _load_yaml(generation_path)
    domains = [args.domain] if args.domain else list(CANONICAL_DOMAINS)
    registry_path = _component_registry_path(repo_root)

    registry_cfg = _load_yaml(registry_path)
    components = registry_cfg.get("components")
    if not isinstance(components, dict):
        raise ValueError(f"{registry_path.relative_to(repo_root).as_posix()}: missing components mapping")

    field_types = (((generation_cfg.get("field_router") or {}).get("field_types") or {}))
    results: list[SyncResult] = []

    for domain in domains:
        domain_field_cfg = field_types.get(domain)
        if not isinstance(domain_field_cfg, dict):
            raise ValueError(f"generation/config.yaml: missing field_router.field_types.{domain} mapping")

        router_text_fields = _normalize_list(domain_field_cfg.get("text"))
        result = _sync_domain_prompts(
            components=components,
            domain=domain,
            router_text_fields=router_text_fields,
            prune_extras=args.prune_extras,
        )
        results.append(result)

    report = {
        "write_mode": bool(args.write),
        "prune_extras": bool(args.prune_extras),
        "domains": [
            {
                "domain": result.domain,
                "added_fields": result.added_fields,
                "removed_fields": result.removed_fields,
                "unchanged_fields_count": len(result.unchanged_fields),
            }
            for result in results
        ],
    }

    tasks_dir = repo_root / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    report_path = tasks_dir / "field_contract_sync_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.write:
        _save_yaml(registry_path, registry_cfg)

    for item in report["domains"]:
        print(f"[{item['domain']}]")
        print(f"  added_fields: {', '.join(item['added_fields']) if item['added_fields'] else 'none'}")
        print(f"  removed_fields: {', '.join(item['removed_fields']) if item['removed_fields'] else 'none'}")
        print(f"  unchanged_fields_count: {item['unchanged_fields_count']}")

    print(f"Wrote report: {report_path.relative_to(repo_root).as_posix()}")
    if args.write:
        print(f"Updated: {registry_path.relative_to(repo_root).as_posix()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
