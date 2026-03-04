#!/usr/bin/env python3
"""Validate prompt section metadata contract and frontend/backend naming parity."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

REQUIRED_METADATA_FIELDS = ("sectionTitle", "sectionDescription", "sectionMetadata")
NON_SECTION_TEXT_KEYS = {"pageTitle", "pageDescription"}


def _is_non_text_prompt_ref(prompt_ref: str) -> bool:
    return prompt_ref.strip().endswith("Title")


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


def _normalize_catalog_subject_keyword(domain: str, value: str) -> str:
    normalized = value.strip()
    if normalized.endswith('.yaml'):
        normalized = normalized[:-5]

    if domain == 'applications':
        normalized = normalized.replace('-laser-cleaning-', '-')
        if normalized.endswith('-applications'):
            normalized = normalized[:-13]
        if normalized.endswith('-laser-cleaning'):
            normalized = normalized[:-15]
    elif domain == 'materials':
        if normalized.endswith('-laser-cleaning'):
            normalized = normalized[:-15]
    elif domain == 'settings':
        if normalized.endswith('-settings'):
            normalized = normalized[:-9]
    elif domain == 'contaminants':
        if normalized.endswith('-contamination'):
            normalized = normalized[:-14]
    elif domain == 'compounds':
        if normalized.endswith('-compound'):
            normalized = normalized[:-9]

    return normalized.strip()


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


def _load_domain_component_text_entries(repo_root: Path, domain: str) -> dict[str, dict[str, str]]:
    prompt_contract_path = repo_root / "domains" / domain / "prompt.yaml"
    prompt_contract_payload = load_yaml(prompt_contract_path)
    prompt_contract = prompt_contract_payload.get("prompt_contract")
    if not isinstance(prompt_contract, dict):
        raise ValueError(f"{prompt_contract_path}: missing required mapping prompt_contract")

    component_registry_file = prompt_contract.get("component_prompt_registry_file")
    if not isinstance(component_registry_file, str) or not component_registry_file.strip():
        raise ValueError(
            f"{prompt_contract_path}: prompt_contract.component_prompt_registry_file must be a non-empty string"
        )

    component_registry_path = repo_root / component_registry_file.strip()
    component_registry_payload = load_yaml(component_registry_path)
    components = component_registry_payload.get("components")
    if not isinstance(components, dict):
        raise ValueError(f"{component_registry_path}: components must be a mapping")

    normalized: dict[str, dict[str, str]] = {}
    for key, value in components.items():
        if not isinstance(key, str) or not key.strip() or not isinstance(value, dict):
            continue

        text_scope = value.get("text")
        if not isinstance(text_scope, dict):
            continue

        entry: dict[str, str] = {}
        domain_map = text_scope.get("domains")
        if isinstance(domain_map, dict):
            domain_entry = domain_map.get(domain)
            if isinstance(domain_entry, dict):
                entry = {
                    child_key: child_value.strip()
                    for child_key, child_value in domain_entry.items()
                    if isinstance(child_key, str)
                    and isinstance(child_value, str)
                    and child_value.strip()
                }

        if not entry:
            shared_entry = text_scope.get("shared")
            if isinstance(shared_entry, dict):
                entry = {
                    child_key: child_value.strip()
                    for child_key, child_value in shared_entry.items()
                    if isinstance(child_key, str)
                    and isinstance(child_value, str)
                    and child_value.strip()
                }

        if entry:
            normalized[key.strip()] = entry

    return normalized


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


def validate_domain_text_prompt_files(repo_root: Path) -> list[str]:
    """Validate domain-local text prompt files contain per-field prompts for all router text fields."""
    errors: list[str] = []

    generation_config_path = repo_root / "generation/config.yaml"
    generation_config = load_yaml(generation_config_path)
    field_router = generation_config.get("field_router")
    if not isinstance(field_router, dict):
        return [f"{generation_config_path}: missing required mapping field_router"]

    field_types = field_router.get("field_types")
    if not isinstance(field_types, dict):
        return [f"{generation_config_path}: field_router.field_types must be a mapping"]

    schema_path = repo_root / "data/schemas/section_display_schema.yaml"
    schema_payload = load_yaml(schema_path)
    sections = schema_payload.get("sections")
    if not isinstance(sections, dict):
        return [f"{schema_path}: sections must be a mapping"]

    component_aliases = _load_component_aliases(repo_root)

    placeholder_pattern = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")
    required_variables = {"subject", "context"}

    for domain, type_map in sorted(field_types.items()):
        if not isinstance(domain, str) or not isinstance(type_map, dict):
            continue

        text_fields = type_map.get("text")
        if not isinstance(text_fields, list):
            errors.append(f"{generation_config_path}: field_router.field_types.{domain}.text must be a list")
            continue

        prompt_contract_path = repo_root / "domains" / domain / "prompt.yaml"
        prompt_contract_payload = load_yaml(prompt_contract_path)
        prompt_contract = prompt_contract_payload.get("prompt_contract")
        if not isinstance(prompt_contract, dict):
            errors.append(f"{prompt_contract_path}: missing required mapping prompt_contract")
            continue

        try:
            field_prompts = _load_domain_component_text_entries(repo_root, domain)
            text_prompt_path = repo_root / "prompts" / "registry" / "component_prompt_registry.yaml"
        except Exception as exc:
            errors.append(f"{prompt_contract_path}: invalid component prompt registry contract ({exc})")
            continue

        def _is_section_key(component_key: str) -> bool:
            key_name = component_key.strip()
            if not key_name or "." in key_name:
                return False
            if key_name in NON_SECTION_TEXT_KEYS:
                return False
            canonical_name = component_aliases.get(key_name, key_name)
            return canonical_name in sections

        def _expected_children_for_key(component_key: str) -> tuple[str, ...]:
            key_name = component_key.strip()
            if key_name.endswith(".sectionTitle"):
                return ("sectionTitle",)
            if key_name.endswith(".sectionDescription"):
                return ("sectionDescription",)
            if _is_section_key(key_name):
                return ("sectionTitle", "sectionDescription")
            return ("prompt",)

        expected_children_by_key: dict[str, tuple[str, ...]] = {}
        required_text_keys: set[str] = set()

        for field_name in text_fields:
            if not isinstance(field_name, str) or not field_name.strip():
                continue
            component_key = field_name.strip()
            required_text_keys.add(component_key)
            expected_children_by_key[component_key] = _expected_children_for_key(component_key)

        backfill_path = repo_root / "generation" / "backfill" / "config" / f"{domain}.yaml"
        if backfill_path.exists():
            backfill_payload = load_yaml(backfill_path)
            generators = backfill_payload.get("generators")
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
                        if isinstance(field_path, str) and field_path.strip():
                            key_name = field_path.strip()
                            required_text_keys.add(key_name)
                            expected_children_by_key.setdefault(
                                key_name,
                                _expected_children_for_key(key_name),
                            )

                        component_type = field_mapping.get("component_type")
                        if isinstance(component_type, str) and component_type.strip():
                            component_key = component_type.strip()
                            required_text_keys.add(component_key)
                            expected_children_by_key[component_key] = _expected_children_for_key(component_key)

        normalized_entries: dict[str, str] = {}
        for key, value in field_prompts.items():
            if not isinstance(key, str) or not key.strip():
                continue

            key_name = key.strip()
            expected_children = expected_children_by_key.get(
                key_name,
                _expected_children_for_key(key_name),
            )

            if isinstance(value, dict):
                missing_children: list[str] = []
                child_values: dict[str, str] = {}
                for child_key in expected_children:
                    child_value = value.get(child_key)
                    if not isinstance(child_value, str) or not child_value.strip():
                        missing_children.append(child_key)
                    else:
                        child_values[child_key] = child_value.strip()

                if missing_children:
                    errors.append(
                        f"{text_prompt_path}: field_prompts.{key_name} missing required child keys: {', '.join(missing_children)}"
                    )
                    continue

                if "sectionDescription" in child_values:
                    normalized_entries[key_name] = child_values["sectionDescription"]
                elif "prompt" in child_values:
                    normalized_entries[key_name] = child_values["prompt"]
                elif "sectionTitle" in child_values:
                    normalized_entries[key_name] = child_values["sectionTitle"]
                continue

            if isinstance(value, str) and value.strip():
                errors.append(
                    f"{text_prompt_path}: field_prompts.{key_name} must use nested child fields ({', '.join(expected_children)})"
                )
                normalized_entries[key_name] = value.strip()

        for key_name in sorted(required_text_keys):
            prompt_text = normalized_entries.get(key_name)
            if not isinstance(prompt_text, str) or not prompt_text:
                errors.append(f"{text_prompt_path}: missing field_prompts.{key_name}")
                continue

            if "\n" in prompt_text:
                errors.append(f"{text_prompt_path}: field_prompts.{key_name} must be single-line")

            placeholders = set(placeholder_pattern.findall(prompt_text))
            if not placeholders:
                errors.append(f"{text_prompt_path}: field_prompts.{key_name} must include variable placeholders")
                continue

            missing_required = sorted(required_variables - placeholders)
            if missing_required:
                errors.append(
                    f"{text_prompt_path}: field_prompts.{key_name} missing required placeholders: {', '.join('{' + name + '}' for name in missing_required)}"
                )

    return errors


def _load_domain_text_prompt_refs(repo_root: Path, domain: str) -> set[str]:
    prompt_contract_path = repo_root / "domains" / domain / "prompt.yaml"
    if not prompt_contract_path.exists():
        return set()

    prompt_contract_payload = load_yaml(prompt_contract_path)
    prompt_contract = prompt_contract_payload.get("prompt_contract")
    if not isinstance(prompt_contract, dict):
        return set()

    try:
        field_prompts = _load_domain_component_text_entries(repo_root, domain)
    except Exception:
        return set()

    normalized: set[str] = set()
    for key, value in field_prompts.items():
        if not isinstance(key, str) or not key.strip():
            continue
        key_name = key.strip()
        if isinstance(value, str) and value.strip():
            normalized.add(key_name)
            continue
        if isinstance(value, dict):
            for child_key in ("sectionDescription", "sectionTitle", "prompt"):
                child_value = value.get(child_key)
                if isinstance(child_value, str) and child_value.strip():
                    normalized.add(key_name)
                    break

    return normalized


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

        domain_prompt_refs = _load_domain_text_prompt_refs(repo_root, domain)
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

                has_single_line_prompt = prompt_ref in domain_prompt_refs
                has_shared_prompt = prompt_ref in shared_prompts
                if not has_single_line_prompt and not has_shared_prompt:
                    errors.append(
                        f"{config_file}: field '{field_path}' component '{component_type}' (canonical '{canonical_component_type}') uses prompt_ref '{prompt_ref}' without single-line/shared prompt definition"
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

        component_registry_file = prompt_contract_body.get("component_prompt_registry_file")
        if not isinstance(component_registry_file, str) or not component_registry_file.strip():
            errors.append(
                f"{prompt_contract_path}: prompt_contract.component_prompt_registry_file must be a non-empty string"
            )
        else:
            configured_path = repo_root / component_registry_file.strip()
            if not configured_path.exists():
                errors.append(f"{prompt_contract_path}: configured file not found: {configured_path}")

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
                "use domains/*/prompts/text_prompt.yaml field_prompts as the canonical text field source"
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
                declared_keywords = {
                    _normalize_catalog_subject_keyword(domain, value)
                    for value in file_names
                    if isinstance(value, str) and value.strip()
                }
                if len(declared_keywords) != len(file_names) or any(not value for value in declared_keywords):
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
                        actual_keywords = {
                            _normalize_catalog_subject_keyword(domain, entry.name)
                            for entry in frontmatter_path.glob("*.yaml")
                            if entry.is_file()
                        }
                        missing_keywords = sorted(actual_keywords - declared_keywords)
                        extra_keywords = sorted(declared_keywords - actual_keywords)
                        if missing_keywords:
                            errors.append(
                                f"{catalog_path}: article_pages.file_names missing subject keywords present in frontmatter: {', '.join(missing_keywords)}"
                            )
                        if extra_keywords:
                            errors.append(
                                f"{catalog_path}: article_pages.file_names contains subject keywords not present in frontmatter: {', '.join(extra_keywords)}"
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
                f"{legacy_path}: deprecated legacy shared prompt file must not exist; use prompts/registry/shared_prompt_registry.yaml and domains/*/prompts/text_prompt.yaml"
            )

    return errors


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]

    errors: list[str] = []
    errors.extend(validate_prompt_files(repo_root))
    errors.extend(validate_domain_text_prompt_files(repo_root))
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
