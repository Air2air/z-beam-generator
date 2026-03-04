#!/usr/bin/env python3
"""Validate per-domain field contract parity across core contract sources.

Parity is enforced PER DOMAIN (not cross-domain unification), preserving each domain's
intentional field differences while preventing drift within a domain.
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
        raise ValueError(f"YAML root must be a mapping: {path}")
    return payload


def _normalize_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    output: list[str] = []
    for value in values:
        if isinstance(value, str) and value.strip():
            output.append(value.strip())
    return output


def _normalize_mapping_keys(values: Any) -> set[str]:
    if not isinstance(values, dict):
        return set()
    return {str(key).strip() for key in values if isinstance(key, str) and key.strip()}


def _frontmatter_directory_for_domain(repo_root: Path, domain: str) -> Path:
    frontmatter_root = repo_root.parent / "z-beam" / "frontmatter"
    return frontmatter_root / domain


def _extract_top_level_keys(path: Path) -> set[str]:
    payload = _load_yaml(path)
    return _normalize_mapping_keys(payload)


def _domain_prompt_fields(repo_root: Path, domain: str, allowed_fields: set[str]) -> set[str]:
    component_registry = _load_yaml(repo_root / COMPONENT_PROMPT_REGISTRY_RELATIVE_PATH)
    components = component_registry.get("components")
    if not isinstance(components, dict):
        raise ValueError(f"{COMPONENT_PROMPT_REGISTRY_RELATIVE_PATH}: components must be a mapping")

    prompt_fields: set[str] = set()
    for key, value in components.items():
        if not isinstance(key, str) or not key.strip() or not isinstance(value, dict):
            continue
        normalized_key = key.strip()
        if normalized_key not in allowed_fields:
            continue

        text_scope = value.get("text")
        if not isinstance(text_scope, dict):
            continue

        domain_entries = text_scope.get("domains")
        if isinstance(domain_entries, dict):
            domain_entry = domain_entries.get(domain)
            if isinstance(domain_entry, dict) and domain_entry:
                prompt_fields.add(normalized_key)
                continue

        shared_entry = text_scope.get("shared")
        if isinstance(shared_entry, dict) and shared_entry:
            prompt_fields.add(normalized_key)

    return prompt_fields


@dataclass
class DomainParityResult:
    domain: str
    missing_prompt_fields: list[str]
    extra_prompt_fields: list[str]
    missing_section_schema_fields: list[str]
    missing_required_in_sample_frontmatter: list[str]
    sample_frontmatter_file: str | None

    @property
    def has_errors(self) -> bool:
        return any(
            [
                self.missing_prompt_fields,
                self.extra_prompt_fields,
                self.missing_required_in_sample_frontmatter,
            ]
        )


def _resolve_frontmatter_sample(repo_root: Path, domain: str) -> Path | None:
    folder = _frontmatter_directory_for_domain(repo_root, domain)
    if not folder.exists() or not folder.is_dir():
        return None

    candidates = sorted(folder.glob("*.yaml"))
    if not candidates:
        return None
    return candidates[0]


def _validate_domain(repo_root: Path, domain: str) -> DomainParityResult:
    generation_cfg = _load_yaml(repo_root / "generation/config.yaml")
    section_schema = _load_yaml(repo_root / "data/schemas/section_display_schema.yaml")
    field_order_cfg = _load_yaml(repo_root / "data/schemas/FrontmatterFieldOrder.yaml")

    field_types = (((generation_cfg.get("field_router") or {}).get("field_types") or {}).get(domain) or {})
    router_text_fields = set(_normalize_list(field_types.get("text")))

    prompt_fields = _domain_prompt_fields(repo_root, domain, router_text_fields)

    sections = section_schema.get("sections") or {}
    section_fields = _normalize_mapping_keys(sections)

    domain_order = field_order_cfg.get(domain) or {}
    required_fields = set(_normalize_list(domain_order.get("required_fields")))

    sample_path = _resolve_frontmatter_sample(repo_root, domain)
    sample_keys: set[str] = set()
    sample_file: str | None = None
    if sample_path is not None:
        sample_keys = _extract_top_level_keys(sample_path)
        sample_file = sample_path.relative_to(repo_root.parent).as_posix()

    # Exclude legacy title helper fields from required prompt parity
    excluded_prompt_fields = {"relatedMaterialsTitle", "contaminatedByTitle"}

    target_router_fields = {field for field in router_text_fields if field not in excluded_prompt_fields}

    missing_prompt_fields = sorted(target_router_fields - prompt_fields)
    extra_prompt_fields: list[str] = []

    missing_section_schema_fields = sorted(
        field
        for field in target_router_fields
        if field not in section_fields and field not in {"pageDescription", "pageTitle"}
    )

    missing_required_in_sample_frontmatter: list[str] = []
    if sample_keys:
        missing_required_in_sample_frontmatter = sorted(required_fields - sample_keys)

    return DomainParityResult(
        domain=domain,
        missing_prompt_fields=missing_prompt_fields,
        extra_prompt_fields=extra_prompt_fields,
        missing_section_schema_fields=missing_section_schema_fields,
        missing_required_in_sample_frontmatter=missing_required_in_sample_frontmatter,
        sample_frontmatter_file=sample_file,
    )


def _format_console_report(results: list[DomainParityResult]) -> str:
    lines: list[str] = []
    for result in results:
        lines.append(f"\n[{result.domain}]")
        if result.sample_frontmatter_file:
            lines.append(f"  sample_frontmatter: {result.sample_frontmatter_file}")
        else:
            lines.append("  sample_frontmatter: <none>")

        if result.missing_prompt_fields:
            lines.append(f"  missing_prompt_fields: {', '.join(result.missing_prompt_fields)}")
        else:
            lines.append("  missing_prompt_fields: none")

        if result.extra_prompt_fields:
            lines.append(f"  extra_prompt_fields: {', '.join(result.extra_prompt_fields)}")
        else:
            lines.append("  extra_prompt_fields: none")

        if result.missing_section_schema_fields:
            lines.append(
                "  missing_section_schema_fields: "
                + ", ".join(result.missing_section_schema_fields)
            )
        else:
            lines.append("  missing_section_schema_fields: none")

        if result.missing_required_in_sample_frontmatter:
            lines.append(
                "  missing_required_in_sample_frontmatter: "
                + ", ".join(result.missing_required_in_sample_frontmatter)
            )
        else:
            lines.append("  missing_required_in_sample_frontmatter: none")

    return "\n".join(lines).lstrip()


def _write_report(repo_root: Path, results: list[DomainParityResult]) -> Path:
    tasks_dir = repo_root / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)

    report_path = tasks_dir / "field_contract_parity_report.json"
    payload = {
        "summary": {
            "domain_count": len(results),
            "domains_with_errors": sum(1 for item in results if item.has_errors),
        },
        "results": [
            {
                "domain": item.domain,
                "sample_frontmatter_file": item.sample_frontmatter_file,
                "missing_prompt_fields": item.missing_prompt_fields,
                "extra_prompt_fields": item.extra_prompt_fields,
                "missing_section_schema_fields": item.missing_section_schema_fields,
                "missing_required_in_sample_frontmatter": item.missing_required_in_sample_frontmatter,
            }
            for item in results
        ],
    }

    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate per-domain field contract parity")
    parser.add_argument(
        "--domain",
        choices=CANONICAL_DOMAINS,
        help="Validate one domain only",
    )
    parser.add_argument(
        "--all-domains",
        action="store_true",
        help="Validate all canonical domains",
    )
    args = parser.parse_args()

    if not args.domain and not args.all_domains:
        parser.error("Provide --domain <name> or --all-domains")

    repo_root = Path(__file__).resolve().parents[2]
    domains = [args.domain] if args.domain else list(CANONICAL_DOMAINS)

    results = [_validate_domain(repo_root, domain) for domain in domains]
    report_path = _write_report(repo_root, results)

    print(_format_console_report(results))
    print(f"\nWrote report: {report_path.relative_to(repo_root).as_posix()}")

    if any(result.has_errors for result in results):
        print("\n❌ Field contract parity validation failed")
        return 1

    print("\n✅ Field contract parity validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
