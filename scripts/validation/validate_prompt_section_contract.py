#!/usr/bin/env python3
"""Validate prompt section metadata contract and frontend/backend naming parity."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

REQUIRED_METADATA_FIELDS = ("sectionTitle", "sectionDescription", "sectionMetadata")


def _load_generation_policy(repo_root: Path) -> dict[str, Any]:
    policy_path = repo_root / "data/schemas/content_generation_policy.yaml"
    payload = load_yaml(policy_path)

    policy = payload.get("content_generation_policy")
    if not isinstance(policy, dict):
        raise ValueError(
            f"{policy_path}: missing required mapping 'content_generation_policy'"
        )

    return policy


def _load_component_aliases(repo_root: Path) -> dict[str, str]:
    policy = _load_generation_policy(repo_root)
    aliases = (((policy.get("aliases") or {}).get("componentType")) or {})
    if not isinstance(aliases, dict):
        raise ValueError(
            "data/schemas/content_generation_policy.yaml: aliases.componentType must be a mapping"
        )

    normalized: dict[str, str] = {}
    for source, target in aliases.items():
        if isinstance(source, str) and isinstance(target, str) and source.strip() and target.strip():
            normalized[source.strip()] = target.strip()
    return normalized


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be mapping: {path}")
    return data


def _shared_prompt_registry_path(repo_root: Path) -> Path:
    return repo_root / "prompts/registry/shared_prompt_registry.yaml"


def _load_shared_prompt_registry(repo_root: Path) -> dict[str, Any]:
    registry_path = _shared_prompt_registry_path(repo_root)
    payload = load_yaml(registry_path)

    section_prompts = payload.get("section_prompts")
    section_prompt_metadata = payload.get("section_prompt_metadata")
    if not isinstance(section_prompts, dict):
        raise ValueError(
            f"{registry_path}: missing required mapping 'section_prompts'"
        )
    if not isinstance(section_prompt_metadata, dict):
        raise ValueError(
            f"{registry_path}: missing required mapping 'section_prompt_metadata'"
        )

    return payload


def _load_faq_shared_registry(repo_root: Path) -> tuple[str | None, dict[str, Any] | None]:
    shared_registry = _load_shared_prompt_registry(repo_root)
    section_prompts = shared_registry.get("section_prompts")
    section_prompt_metadata = shared_registry.get("section_prompt_metadata")

    shared_prompt = section_prompts.get("faq") if isinstance(section_prompts, dict) else None
    if not isinstance(shared_prompt, str) or not shared_prompt.strip():
        shared_prompt = None

    shared_metadata = section_prompt_metadata.get("faq") if isinstance(section_prompt_metadata, dict) else None
    if not isinstance(shared_metadata, dict):
        shared_metadata = None

    return shared_prompt, shared_metadata


def parse_string_union_block(ts_text: str, alias: str) -> set[str]:
    pattern = rf"export type {alias}\s*=\s*(.*?);\n\n"
    match = re.search(pattern, ts_text, re.S)
    if not match:
        raise ValueError(f"Could not parse union type '{alias}'")
    return {m.group(1) for m in re.finditer(r"'([^']+)'", match.group(1))}


def validate_prompt_files(repo_root: Path) -> list[str]:
    errors: list[str] = []

    content_prompt_files = sorted((repo_root / "prompts" / "registry").glob("content_prompts_*.yaml"))
    for prompt_file in content_prompt_files:
        if prompt_file.name == "content_prompts_shared.yaml":
            continue
        payload = load_yaml(prompt_file)
        section_prompt_metadata = payload.get("section_prompt_metadata")
        if not isinstance(section_prompt_metadata, dict):
            errors.append(
                f"{prompt_file}: missing required top-level mapping 'section_prompt_metadata'"
            )

    shared_inline_path = _shared_prompt_registry_path(repo_root)
    shared_inline = _load_shared_prompt_registry(repo_root)
    section_prompts = shared_inline.get("section_prompts")
    section_prompt_metadata = shared_inline.get("section_prompt_metadata")
    faq_shared_prompt, faq_shared_metadata = _load_faq_shared_registry(repo_root)

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
        if not isinstance(section_meta_payload, str) or not section_meta_payload.strip():
            errors.append(
                f"{shared_inline_path}: section_prompt_metadata.{key}.sectionMetadata must be a non-empty string"
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
        if prompt_ref == "faq":
            has_prompt = (prompt_ref in section_prompts) or (faq_shared_prompt is not None)
            has_metadata = (prompt_ref in section_prompt_metadata) or (faq_shared_metadata is not None)
            if not has_prompt:
                errors.append(f"{shared_inline_path}: missing section_prompts.{prompt_ref} required by schema prompt_ref")
            if not has_metadata:
                errors.append(f"{shared_inline_path}: missing section_prompt_metadata.{prompt_ref} required by schema prompt_ref")
            continue

        if prompt_ref not in section_prompts:
            errors.append(f"{shared_inline_path}: missing section_prompts.{prompt_ref} required by schema prompt_ref")
        if prompt_ref not in section_prompt_metadata:
            errors.append(f"{shared_inline_path}: missing section_prompt_metadata.{prompt_ref} required by schema prompt_ref")

    return errors


def validate_single_line_component_prompts(repo_root: Path) -> list[str]:
    """Validate one single-line prompt + variables contract for every schema component."""
    errors: list[str] = []

    schema_path = repo_root / "data/schemas/section_display_schema.yaml"
    schema = load_yaml(schema_path)
    sections = schema.get("sections")
    if not isinstance(sections, dict):
        return [f"{schema_path}: sections must be a mapping"]

    single_line_path = repo_root / "data/schemas/component_single_line_prompts.yaml"
    single_line_payload = load_yaml(single_line_path)
    policy = single_line_payload.get("component_single_line_prompts")
    if not isinstance(policy, dict):
        return [
            f"{single_line_path}: missing required mapping 'component_single_line_prompts'"
        ]

    required_variables = policy.get("required_variables")
    if not isinstance(required_variables, list) or not required_variables:
        return [
            f"{single_line_path}: component_single_line_prompts.required_variables must be a non-empty list"
        ]
    required_variables = [v for v in required_variables if isinstance(v, str) and v.strip()]
    if len(required_variables) == 0:
        return [
            f"{single_line_path}: component_single_line_prompts.required_variables must contain non-empty strings"
        ]

    by_domain = policy.get("by_domain")
    if not isinstance(by_domain, dict):
        return [
            f"{single_line_path}: component_single_line_prompts.by_domain must be a mapping"
        ]

    placeholder_pattern = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")

    component_aliases = _load_component_aliases(repo_root)
    generation_policy = _load_generation_policy(repo_root)
    required_by_domain = (((generation_policy.get("backfill") or {}).get("required_fields_by_domain")) or {})
    if not isinstance(required_by_domain, dict):
        return [
            "data/schemas/content_generation_policy.yaml: backfill.required_fields_by_domain must be a mapping"
        ]

    required_set = set(required_variables)

    for domain in sorted(required_by_domain.keys()):
        domain_required_entries = required_by_domain.get(domain)
        if not isinstance(domain_required_entries, list):
            errors.append(
                f"data/schemas/content_generation_policy.yaml: domain '{domain}' must map to a list"
            )
            continue

        domain_prompts = by_domain.get(domain)
        if not isinstance(domain_prompts, dict):
            errors.append(
                f"{single_line_path}: missing component_single_line_prompts.by_domain.{domain}"
            )
            continue

        domain_prompt_entries = {
            str(key): value
            for key, value in domain_prompts.items()
            if isinstance(key, str)
        }

        required_prompt_refs: set[str] = set()
        for idx, entry in enumerate(domain_required_entries):
            if not isinstance(entry, dict):
                errors.append(
                    f"data/schemas/content_generation_policy.yaml: domain '{domain}' entry {idx} must be a mapping"
                )
                continue
            component_type = entry.get("componentType")
            if not isinstance(component_type, str) or not component_type.strip():
                continue
            component_type = _normalize_component_type(component_type.strip(), component_aliases)
            section_data = sections.get(component_type)
            if not isinstance(section_data, dict):
                errors.append(
                    f"{schema_path}: component '{component_type}' referenced by policy for domain '{domain}' is missing"
                )
                continue
            prompt_ref = section_data.get("prompt_ref")
            if not isinstance(prompt_ref, str) or not prompt_ref.strip():
                errors.append(
                    f"{schema_path}: component '{component_type}' for domain '{domain}' missing prompt_ref"
                )
                continue
            required_prompt_refs.add(prompt_ref.strip())

        for prompt_ref in sorted(required_prompt_refs):
            entry = domain_prompt_entries.get(prompt_ref)
            if not isinstance(entry, dict):
                errors.append(
                    f"{single_line_path}: missing component_single_line_prompts.by_domain.{domain}.{prompt_ref}"
                )
                continue

            prompt = entry.get("prompt")
            variables = entry.get("variables")

            if not isinstance(prompt, str) or not prompt.strip():
                errors.append(
                    f"{single_line_path}: component_single_line_prompts.by_domain.{domain}.{prompt_ref}.prompt must be a non-empty string"
                )
                continue

            prompt_text = prompt.strip()
            if "\n" in prompt_text:
                errors.append(
                    f"{single_line_path}: component_single_line_prompts.by_domain.{domain}.{prompt_ref}.prompt must be single-line"
                )

            if not isinstance(variables, list) or not variables:
                errors.append(
                    f"{single_line_path}: component_single_line_prompts.by_domain.{domain}.{prompt_ref}.variables must be a non-empty list"
                )
                continue

            normalized_variables = [v for v in variables if isinstance(v, str) and v.strip()]
            if len(normalized_variables) != len(variables):
                errors.append(
                    f"{single_line_path}: component_single_line_prompts.by_domain.{domain}.{prompt_ref}.variables must contain only non-empty strings"
                )
                continue

            placeholders = set(placeholder_pattern.findall(prompt_text))
            if not placeholders:
                errors.append(
                    f"{single_line_path}: component_single_line_prompts.by_domain.{domain}.{prompt_ref}.prompt must include at least one variable placeholder"
                )
                continue

            declared = set(normalized_variables)

            missing_required_vars = sorted(required_set - declared)
            if missing_required_vars:
                errors.append(
                    f"{single_line_path}: component_single_line_prompts.by_domain.{domain}.{prompt_ref}.variables missing required variables: {', '.join(missing_required_vars)}"
                )

            undeclared = sorted(placeholders - declared)
            if undeclared:
                errors.append(
                    f"{single_line_path}: component_single_line_prompts.by_domain.{domain}.{prompt_ref}.prompt uses undeclared variables: {', '.join(undeclared)}"
                )

            missing_placeholders = sorted(required_set - placeholders)
            if missing_placeholders:
                errors.append(
                    f"{single_line_path}: component_single_line_prompts.by_domain.{domain}.{prompt_ref}.prompt must include required placeholders: {', '.join('{' + name + '}' for name in missing_placeholders)}"
                )

        extra_refs = sorted(set(domain_prompt_entries.keys()) - required_prompt_refs)
        for prompt_ref in extra_refs:
            errors.append(
                f"{single_line_path}: component_single_line_prompts.by_domain.{domain}.{prompt_ref} is not required by content generation policy"
            )

    return errors


def _load_domain_prompt_map(repo_root: Path, domain: str) -> dict[str, str]:
    prompt_contract_path = repo_root / "domains" / domain / "prompt.yaml"
    if not prompt_contract_path.exists():
        return {}

    prompt_contract_payload = load_yaml(prompt_contract_path)
    prompt_contract = prompt_contract_payload.get("prompt_contract")
    if not isinstance(prompt_contract, dict):
        return {}

    content_prompts_file = prompt_contract.get("content_prompts_file")
    if not isinstance(content_prompts_file, str) or not content_prompts_file.strip():
        return {}

    domain_file = repo_root / content_prompts_file.strip()
    if not domain_file.exists():
        return {}

    payload = load_yaml(domain_file)
    section_prompts = payload.get("section_prompts")
    if not isinstance(section_prompts, dict):
        return {}

    return {
        str(key): str(value)
        for key, value in section_prompts.items()
        if isinstance(key, str) and isinstance(value, str) and value.strip()
    }


def _normalize_component_type(component_type: str, aliases: dict[str, str]) -> str:
    return aliases.get(component_type, component_type)


def _collect_backfill_field_component_pairs(
    config_payload: dict[str, Any],
    aliases: dict[str, str],
) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    generators = config_payload.get("generators")
    if not isinstance(generators, list):
        return pairs

    for generator in generators:
        if not isinstance(generator, dict):
            continue
        fields = generator.get("fields")
        if not isinstance(fields, list):
            continue

        for field_mapping in fields:
            if not isinstance(field_mapping, dict):
                continue
            field_path = field_mapping.get("field")
            component_type = field_mapping.get("component_type")
            if not isinstance(field_path, str) or not field_path.strip():
                continue
            if not isinstance(component_type, str) or not component_type.strip():
                continue
            normalized_component = _normalize_component_type(component_type.strip(), aliases)
            pairs.append((field_path.strip(), normalized_component))

    return pairs


def validate_backfill_policy_alignment(repo_root: Path) -> list[str]:
    """Validate that backfill config field mappings align with centralized schema policy."""
    errors: list[str] = []

    policy = _load_generation_policy(repo_root)
    required_by_domain = (((policy.get("backfill") or {}).get("required_fields_by_domain")) or {})
    if not isinstance(required_by_domain, dict):
        return [
            "data/schemas/content_generation_policy.yaml: backfill.required_fields_by_domain must be a mapping"
        ]

    aliases = _load_component_aliases(repo_root)

    config_files = sorted((repo_root / "generation/backfill/config").glob("*.yaml"))
    for config_file in config_files:
        payload = load_yaml(config_file)
        domain = payload.get("domain")
        if not isinstance(domain, str) or not domain.strip():
            errors.append(f"{config_file}: missing non-empty 'domain'")
            continue
        domain = domain.strip()

        expected_entries = required_by_domain.get(domain)
        if not isinstance(expected_entries, list):
            errors.append(
                f"data/schemas/content_generation_policy.yaml: missing backfill policy list for domain '{domain}'"
            )
            continue

        expected_pairs: set[tuple[str, str]] = set()
        for idx, entry in enumerate(expected_entries):
            if not isinstance(entry, dict):
                errors.append(
                    f"data/schemas/content_generation_policy.yaml: domain '{domain}' entry {idx} must be a mapping"
                )
                continue
            field_path = entry.get("field")
            component_type = entry.get("componentType")
            if not isinstance(field_path, str) or not field_path.strip():
                errors.append(
                    f"data/schemas/content_generation_policy.yaml: domain '{domain}' entry {idx} missing non-empty field"
                )
                continue
            if not isinstance(component_type, str) or not component_type.strip():
                errors.append(
                    f"data/schemas/content_generation_policy.yaml: domain '{domain}' entry {idx} missing non-empty componentType"
                )
                continue
            expected_pairs.add((field_path.strip(), component_type.strip()))

        actual_pairs = set(_collect_backfill_field_component_pairs(payload, aliases))

        missing_pairs = sorted(expected_pairs - actual_pairs)
        extra_pairs = sorted(actual_pairs - expected_pairs)

        for field_path, component_type in missing_pairs:
            errors.append(
                f"{config_file}: missing required policy mapping field '{field_path}' -> component '{component_type}'"
            )

        for field_path, component_type in extra_pairs:
            errors.append(
                f"{config_file}: mapping field '{field_path}' -> component '{component_type}' not declared in content_generation_policy.yaml"
            )

    for domain in sorted(required_by_domain.keys()):
        expected_config = repo_root / "generation/backfill/config" / f"{domain}.yaml"
        if not expected_config.exists():
            errors.append(
                f"data/schemas/content_generation_policy.yaml: policy declares domain '{domain}' but missing {expected_config}"
            )

    return errors


def validate_backfill_prompt_wiring(repo_root: Path) -> list[str]:
    """Validate that every backfill-generated field resolves to a schema section and concrete prompt."""
    errors: list[str] = []

    schema_path = repo_root / "data/schemas/section_display_schema.yaml"
    schema = load_yaml(schema_path)
    sections = schema.get("sections")
    if not isinstance(sections, dict):
        return [f"{schema_path}: sections must be a mapping"]

    shared_inline = _load_shared_prompt_registry(repo_root)
    shared_prompts = shared_inline.get("section_prompts")
    if not isinstance(shared_prompts, dict):
        return ["prompts/registry/shared_prompt_registry.yaml: section_prompts must be a mapping"]

    faq_shared_prompt, _ = _load_faq_shared_registry(repo_root)
    if isinstance(faq_shared_prompt, str) and faq_shared_prompt.strip():
        shared_prompts = dict(shared_prompts)
        shared_prompts["faq"] = faq_shared_prompt.strip()

    component_aliases = _load_component_aliases(repo_root)

    config_files = sorted((repo_root / "generation/backfill/config").glob("*.yaml"))
    for config_file in config_files:
        payload = load_yaml(config_file)
        domain = payload.get("domain")
        if not isinstance(domain, str) or not domain.strip():
            errors.append(f"{config_file}: missing non-empty 'domain'")
            continue

        domain_prompts = _load_domain_prompt_map(repo_root, domain)
        generators = payload.get("generators")
        if not isinstance(generators, list):
            errors.append(f"{config_file}: generators must be a list")
            continue

        for generator in generators:
            if not isinstance(generator, dict):
                errors.append(f"{config_file}: each generator must be a mapping")
                continue

            fields = generator.get("fields")
            if not isinstance(fields, list):
                continue

            for index, field_mapping in enumerate(fields):
                if not isinstance(field_mapping, dict):
                    errors.append(f"{config_file}: fields[{index}] must be a mapping")
                    continue

                field_path = field_mapping.get("field")
                component_type = field_mapping.get("component_type")
                if not isinstance(field_path, str) or not field_path.strip():
                    errors.append(f"{config_file}: fields[{index}] missing non-empty 'field'")
                    continue
                if not isinstance(component_type, str) or not component_type.strip():
                    errors.append(
                        f"{config_file}: fields[{index}] ({field_path}) missing non-empty 'component_type'"
                    )
                    continue

                canonical_component_type = _normalize_component_type(component_type, component_aliases)
                section = sections.get(canonical_component_type)
                if not isinstance(section, dict):
                    errors.append(
                        f"{config_file}: field '{field_path}' references unknown component_type '{component_type}'"
                    )
                    continue

                prompt_ref = section.get("prompt_ref")
                if not isinstance(prompt_ref, str) or not prompt_ref.strip():
                    errors.append(
                        f"{schema_path}: component '{canonical_component_type}' must define non-empty prompt_ref"
                    )
                    continue

                has_domain_prompt = prompt_ref in domain_prompts
                has_shared_prompt = prompt_ref in shared_prompts
                if not has_domain_prompt and not has_shared_prompt:
                    errors.append(
                        f"{config_file}: field '{field_path}' component '{component_type}' (canonical '{canonical_component_type}') uses prompt_ref '{prompt_ref}' without domain/shared prompt definition"
                    )

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


def validate_domain_prompt_contracts(repo_root: Path) -> list[str]:
    errors: list[str] = []
    domains = ("applications", "materials", "contaminants", "compounds", "settings")

    for domain in domains:
        prompt_contract_path = repo_root / "domains" / domain / "prompt.yaml"
        catalog_path = repo_root / "domains" / domain / "catalog.yaml"
        domain_folder = repo_root / "domains" / domain

        prompt_contract = load_yaml(prompt_contract_path)
        catalog_payload = load_yaml(catalog_path)

        declared_domain = prompt_contract.get("domain")
        if not isinstance(declared_domain, str) or declared_domain.strip() != domain:
            errors.append(f"{prompt_contract_path}: domain must be '{domain}'")

        prompt_contract_body = prompt_contract.get("prompt_contract")
        if not isinstance(prompt_contract_body, dict):
            errors.append(f"{prompt_contract_path}: missing required mapping prompt_contract")
            continue

        content_prompts_file = prompt_contract_body.get("content_prompts_file")
        if not isinstance(content_prompts_file, str) or not content_prompts_file.strip():
            errors.append(
                f"{prompt_contract_path}: prompt_contract.content_prompts_file must be a non-empty string"
            )
            continue

        expected_prompt_path = repo_root / "prompts" / "registry" / "content_prompts_shared.yaml"
        configured_prompt_path = repo_root / content_prompts_file.strip()
        if configured_prompt_path != expected_prompt_path:
            errors.append(
                f"{prompt_contract_path}: content_prompts_file must point to prompts/registry/content_prompts_shared.yaml"
            )
        if not configured_prompt_path.exists():
            errors.append(f"{prompt_contract_path}: configured file not found: {configured_prompt_path}")

        declared_catalog_domain = catalog_payload.get("domain")
        if not isinstance(declared_catalog_domain, str) or declared_catalog_domain.strip() != domain:
            errors.append(f"{catalog_path}: domain must be '{domain}'")

        folder_contract = catalog_payload.get("domain_folder_contract")
        if not isinstance(folder_contract, dict):
            errors.append(f"{catalog_path}: missing required mapping domain_folder_contract")
            continue

        required_files = folder_contract.get("required_files")
        required_directories = folder_contract.get("required_directories")
        ignore_entries = folder_contract.get("ignore_entries")

        if not isinstance(required_files, list):
            errors.append(f"{catalog_path}: domain_folder_contract.required_files must be a list")
            required_files = []
        if not isinstance(required_directories, list):
            errors.append(f"{catalog_path}: domain_folder_contract.required_directories must be a list")
            required_directories = []
        if not isinstance(ignore_entries, list):
            errors.append(f"{catalog_path}: domain_folder_contract.ignore_entries must be a list")
            ignore_entries = []

        required_file_set = {
            item.strip()
            for item in required_files
            if isinstance(item, str) and item.strip()
        }
        required_dir_set = {
            item.strip()
            for item in required_directories
            if isinstance(item, str) and item.strip()
        }
        ignore_set = {
            item.strip()
            for item in ignore_entries
            if isinstance(item, str) and item.strip()
        }

        for file_name in sorted(required_file_set):
            file_path = domain_folder / file_name
            if not file_path.exists() or not file_path.is_file():
                errors.append(f"{catalog_path}: required file missing: {file_name}")

        for dir_name in sorted(required_dir_set):
            dir_path = domain_folder / dir_name
            if not dir_path.exists() or not dir_path.is_dir():
                errors.append(f"{catalog_path}: required directory missing: {dir_name}")

        known_entries = required_file_set | required_dir_set | ignore_set
        actual_entries = {entry.name for entry in domain_folder.iterdir()}
        unexpected = sorted(actual_entries - known_entries)
        if unexpected:
            errors.append(
                f"{catalog_path}: unexpected top-level entries require cleanup evaluation update: {', '.join(unexpected)}"
            )

        cleanup_eval = catalog_payload.get("cleanup_evaluation")
        if not isinstance(cleanup_eval, dict):
            errors.append(f"{catalog_path}: missing required mapping cleanup_evaluation")

        if "one_line_content_prompts" in prompt_contract:
            errors.append(
                f"{prompt_contract_path}: one_line_content_prompts is not allowed in domain prompt contracts; "
                "use data/schemas/component_single_line_prompts.yaml as the canonical single-line source"
            )

        article_pages = catalog_payload.get("article_pages")
        if not isinstance(article_pages, dict):
            errors.append(f"{catalog_path}: missing required mapping article_pages")
        else:
            frontmatter_directory = article_pages.get("frontmatter_directory")
            file_names = article_pages.get("file_names")
            if not isinstance(frontmatter_directory, str) or not frontmatter_directory.strip():
                errors.append(
                    f"{catalog_path}: article_pages.frontmatter_directory must be a non-empty string"
                )
            if not isinstance(file_names, list):
                errors.append(f"{catalog_path}: article_pages.file_names must be a list")
            else:
                declared_files = {
                    value.strip()
                    for value in file_names
                    if isinstance(value, str) and value.strip()
                }
                if len(declared_files) != len(file_names):
                    errors.append(
                        f"{catalog_path}: article_pages.file_names must contain only non-empty unique strings"
                    )

                if isinstance(frontmatter_directory, str) and frontmatter_directory.strip():
                    frontmatter_path = (repo_root / frontmatter_directory.strip()).resolve()
                    if not frontmatter_path.exists() or not frontmatter_path.is_dir():
                        errors.append(
                            f"{catalog_path}: article_pages.frontmatter_directory not found: {frontmatter_path}"
                        )
                    else:
                        actual_files = {
                            entry.name
                            for entry in frontmatter_path.glob("*.yaml")
                            if entry.is_file()
                        }
                        missing_files = sorted(actual_files - declared_files)
                        extra_files = sorted(declared_files - actual_files)
                        if missing_files:
                            errors.append(
                                f"{catalog_path}: article_pages.file_names missing files present in frontmatter: {', '.join(missing_files)}"
                            )
                        if extra_files:
                            errors.append(
                                f"{catalog_path}: article_pages.file_names contains files not present in frontmatter: {', '.join(extra_files)}"
                            )

    return errors


def validate_legacy_prompt_registry_absence(repo_root: Path) -> list[str]:
    """Fail if deprecated shared prompt registry files are reintroduced."""
    errors: list[str] = []
    legacy_paths = (
        "prompts/shared/faq_prompt.yaml",
        "prompts/shared/section_inline_prompts.yaml",
    )

    for relative_path in legacy_paths:
        legacy_path = repo_root / relative_path
        if legacy_path.exists():
            errors.append(
                f"{legacy_path}: deprecated legacy shared prompt file must not exist; use prompts/registry/shared_prompt_registry.yaml and data/schemas/component_single_line_prompts.yaml"
            )

    return errors


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]

    errors: list[str] = []
    errors.extend(validate_prompt_files(repo_root))
    errors.extend(validate_single_line_component_prompts(repo_root))
    errors.extend(validate_backfill_policy_alignment(repo_root))
    errors.extend(validate_backfill_prompt_wiring(repo_root))
    errors.extend(validate_domain_prompt_contracts(repo_root))
    errors.extend(validate_legacy_prompt_registry_absence(repo_root))
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
