"""Centralized prompt/schema access for section prompts and descriptor chains."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class PromptRegistryService:
    """Single access layer for schema sections, registries, and prompt references."""

    _schema_cache: Optional[Dict[str, Any]] = None
    _domain_registry_cache: Dict[str, Dict[str, Any]] = {}
    _shared_inline_prompts_cache: Optional[Dict[str, str]] = None
    _shared_inline_metadata_cache: Optional[Dict[str, Dict[str, Any]]] = None
    _prompt_catalog_cache: Optional[Dict[str, Any]] = None
    _single_line_component_prompts_cache: Optional[Dict[str, Dict[str, Any]]] = None
    _faq_prompt_cache: Optional[Dict[str, Any]] = None

    @classmethod
    def _get_domain_prompt_contract(cls, domain: str) -> Dict[str, Any]:
        contract_path = cls._project_root() / "domains" / domain / "prompt.yaml"
        contract = cls._load_yaml_file(contract_path)

        declared_domain = contract.get("domain")
        if not isinstance(declared_domain, str) or declared_domain.strip() != domain:
            raise ValueError(
                f"Invalid prompt contract domain in {contract_path}: expected '{domain}'"
            )

        prompt_contract = contract.get("prompt_contract")
        if not isinstance(prompt_contract, dict):
            raise ValueError(
                f"Invalid prompt contract in {contract_path}: expected mapping at prompt_contract"
            )

        return prompt_contract

    @classmethod
    def _get_domain_registry_path(cls, domain: str) -> Path:
        prompt_contract = cls._get_domain_prompt_contract(domain)
        relative_path = prompt_contract.get("content_prompts_file")
        if not isinstance(relative_path, str) or not relative_path.strip():
            raise ValueError(
                f"domains/{domain}/prompt.yaml: prompt_contract.content_prompts_file must be a non-empty string"
            )

        registry_path = cls._project_root() / relative_path.strip()
        if not registry_path.exists():
            raise FileNotFoundError(
                f"Configured domain registry does not exist for '{domain}': {registry_path}"
            )

        return registry_path

    @classmethod
    def _project_root(cls) -> Path:
        return Path(__file__).resolve().parents[3]

    @classmethod
    def _load_yaml_file(cls, path: Path) -> Dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"Required YAML file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data is None:
            raise ValueError(f"Invalid YAML format in {path}: file is empty")

        if not isinstance(data, dict):
            raise ValueError(f"Invalid YAML format in {path}: expected mapping")

        return data

    @classmethod
    def _deep_merge(cls, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(base)
        for key, value in override.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = cls._deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        if cls._schema_cache is None:
            schema_path = cls._project_root() / "data" / "schemas" / "section_display_schema.yaml"
            cls._schema_cache = cls._load_yaml_file(schema_path)
        return cls._schema_cache

    @classmethod
    def get_prompt_catalog(cls) -> Dict[str, Any]:
        """Load consolidated prompt catalog (fail-fast)."""
        if cls._prompt_catalog_cache is None:
            catalog_path = cls._project_root() / "prompts" / "registry" / "prompt_catalog.yaml"
            cls._prompt_catalog_cache = cls._load_yaml_file(catalog_path)
        return cls._prompt_catalog_cache

    @classmethod
    def get_faq_prompt_registry(cls) -> Dict[str, Any]:
        """Load canonical FAQ prompt definitions (single source of truth)."""
        if cls._faq_prompt_cache is None:
            faq_path = cls._project_root() / "prompts" / "shared" / "faq_prompt.yaml"
            payload = cls._load_yaml_file(faq_path)
            faq_prompt = payload.get("faq_prompt")
            if not isinstance(faq_prompt, dict):
                raise ValueError(
                    f"Invalid FAQ prompt registry in {faq_path}: expected mapping at faq_prompt"
                )
            cls._faq_prompt_cache = faq_prompt
        return cls._faq_prompt_cache

    @classmethod
    def get_single_line_component_prompts(cls) -> Dict[str, Dict[str, Any]]:
        """Load centralized single-line component prompt registry (fail-fast)."""
        if cls._single_line_component_prompts_cache is None:
            prompts_path = cls._project_root() / "data" / "schemas" / "component_single_line_prompts.yaml"
            payload = cls._load_yaml_file(prompts_path)
            policy = payload.get("component_single_line_prompts")
            if not isinstance(policy, dict):
                raise ValueError(
                    f"Invalid single-line prompt registry in {prompts_path}: expected mapping at component_single_line_prompts"
                )

            by_domain = policy.get("by_domain")
            if not isinstance(by_domain, dict):
                raise ValueError(
                    f"Invalid single-line prompt registry in {prompts_path}: expected mapping at component_single_line_prompts.by_domain"
                )

            faq_registry = cls.get_faq_prompt_registry()
            faq_single_line = faq_registry.get("single_line") if isinstance(faq_registry, dict) else None
            faq_by_domain = faq_single_line.get("by_domain") if isinstance(faq_single_line, dict) else None

            merged_by_domain: Dict[str, Dict[str, Any]] = {}
            for domain_key, domain_prompts in by_domain.items():
                if not isinstance(domain_key, str) or not isinstance(domain_prompts, dict):
                    continue
                merged_prompts = {
                    str(key): dict(value)
                    for key, value in domain_prompts.items()
                    if isinstance(key, str) and isinstance(value, dict)
                }

                if isinstance(faq_by_domain, dict):
                    faq_entry = faq_by_domain.get(domain_key)
                    if isinstance(faq_entry, dict):
                        merged_prompts["faq"] = dict(faq_entry)

                merged_by_domain[domain_key] = merged_prompts

            cls._single_line_component_prompts_cache = merged_by_domain
        return cls._single_line_component_prompts_cache

    @classmethod
    def get_single_line_component_prompt(cls, domain: str, component_type: str) -> Optional[Dict[str, Any]]:
        """Get single-line prompt template + variables for a schema component type."""
        section = cls.get_section(component_type)
        if not isinstance(section, dict):
            return None
        prompt_ref = section.get("prompt_ref")
        if not isinstance(prompt_ref, str) or not prompt_ref.strip():
            return None

        registry = cls.get_single_line_component_prompts().get(domain)
        if not isinstance(registry, dict):
            return None

        entry = registry.get(prompt_ref)
        if not isinstance(entry, dict):
            return None

        resolved = dict(entry)
        resolved["prompt_ref"] = prompt_ref
        resolved["component_type"] = component_type
        return resolved

    @classmethod
    def _get_catalog_value(cls, keys: tuple[str, ...]) -> str:
        """Read required string value from prompt catalog by nested path."""
        value: Any = cls.get_prompt_catalog()
        traversed: list[str] = []

        for key in keys:
            traversed.append(key)
            if not isinstance(value, dict) or key not in value:
                dotted = ".".join(traversed)
                raise KeyError(f"Missing required prompt catalog key: {dotted}")
            value = value[key]

        if not isinstance(value, str) or not value.strip():
            dotted = ".".join(keys)
            raise ValueError(f"Prompt catalog value must be non-empty string: {dotted}")

        return value

    @classmethod
    def get_shared_text_prompt_core(cls) -> str:
        return cls._get_catalog_value(("catalog", "shared", "textPromptCore"))

    @classmethod
    def get_humanness_template(cls, compact: bool = False) -> str:
        variant = "compact" if compact else "full"
        return cls._get_catalog_value(("catalog", "core", "humanness", variant))

    @classmethod
    def get_quality_evaluation_prompt(cls) -> str:
        return cls._get_catalog_value(("catalog", "quality", "evaluation"))

    @classmethod
    def get_section(cls, component_type: str) -> Optional[Dict[str, Any]]:
        sections = cls.get_schema().get("sections", {})
        section = sections.get(component_type)
        if isinstance(section, dict):
            return section
        return None

    @classmethod
    def get_domain_registry(cls, domain: str) -> Dict[str, Any]:
        if domain in cls._domain_registry_cache:
            return cls._domain_registry_cache[domain]

        registry_path = cls._get_domain_registry_path(domain)

        registry = cls._load_yaml_file(registry_path)
        extends_path = registry.get("extends")

        if extends_path:
            base_path = cls._project_root() / str(extends_path)
            base_registry = cls._load_yaml_file(base_path)
            registry = cls._deep_merge(base_registry, registry)

        cls._validate_prompt_metadata_contract(registry, registry_path)

        cls._domain_registry_cache[domain] = registry
        return registry

    @classmethod
    def _validate_prompt_metadata_contract(cls, registry: Dict[str, Any], source_path: Path) -> None:
        section_prompts = registry.get("section_prompts")
        section_metadata = registry.get("section_prompt_metadata")

        if section_prompts is None:
            return

        if not isinstance(section_prompts, dict):
            raise ValueError(
                f"Invalid section_prompts in {source_path}: expected mapping"
            )

        if not isinstance(section_metadata, dict):
            raise ValueError(
                f"Missing required section_prompt_metadata mapping in {source_path}"
            )

        for key, metadata in section_metadata.items():
            if not isinstance(metadata, dict):
                raise ValueError(
                    f"section_prompt_metadata.{key} must be a mapping in {source_path}"
                )

            for required_field in ("sectionTitle", "sectionDescription", "sectionMetadata"):
                if required_field not in metadata:
                    raise ValueError(
                        f"section_prompt_metadata.{key} missing required field '{required_field}' in {source_path}"
                    )

            for text_field in ("sectionTitle", "sectionDescription", "sectionMetadata"):
                value = metadata.get(text_field)
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(
                        f"section_prompt_metadata.{key}.{text_field} must be a non-empty string in {source_path}"
                    )

        for key, prompt_value in section_prompts.items():
            if not isinstance(prompt_value, str) or not prompt_value.strip():
                raise ValueError(
                    f"section_prompts.{key} must be a non-empty string in {source_path}"
                )

            metadata = section_metadata.get(key)
            if not isinstance(metadata, dict):
                raise ValueError(
                    f"Missing section_prompt_metadata.{key} in {source_path}"
                )

    @classmethod
    def _load_shared_inline_prompts(cls) -> Dict[str, str]:
        if cls._shared_inline_prompts_cache is not None:
            return cls._shared_inline_prompts_cache

        shared_path = cls._project_root() / "prompts" / "shared" / "section_inline_prompts.yaml"
        if not shared_path.exists():
            cls._shared_inline_prompts_cache = {}
            return cls._shared_inline_prompts_cache

        shared = cls._load_yaml_file(shared_path)
        prompts = shared.get("section_prompts", {})
        prompt_metadata = shared.get("section_prompt_metadata", {})
        if not isinstance(prompts, dict):
            raise ValueError(
                f"Invalid section_prompt map in {shared_path}: expected mapping at section_prompts"
            )
        if not isinstance(prompt_metadata, dict):
            raise ValueError(
                f"Invalid section_prompt metadata in {shared_path}: expected mapping at section_prompt_metadata"
            )

        faq_registry = cls.get_faq_prompt_registry()
        shared_faq_prompt = faq_registry.get("shared_section_prompt") if isinstance(faq_registry, dict) else None
        if isinstance(shared_faq_prompt, str) and shared_faq_prompt.strip():
            prompts["faq"] = shared_faq_prompt.strip()

        shared_faq_metadata = faq_registry.get("shared_section_metadata") if isinstance(faq_registry, dict) else None
        if isinstance(shared_faq_metadata, dict):
            prompt_metadata["faq"] = dict(shared_faq_metadata)

        cls._validate_prompt_metadata_contract(
            {
                "section_prompts": prompts,
                "section_prompt_metadata": prompt_metadata,
            },
            shared_path,
        )

        cls._shared_inline_prompts_cache = {k: str(v) for k, v in prompts.items()}
        cls._shared_inline_metadata_cache = {
            key: dict(value)
            for key, value in prompt_metadata.items()
            if isinstance(value, dict)
        }
        return cls._shared_inline_prompts_cache

    @classmethod
    def get_shared_section_metadata(cls, prompt_ref: str) -> Optional[Dict[str, Any]]:
        cls._load_shared_inline_prompts()
        if cls._shared_inline_metadata_cache is None:
            return None
        metadata = cls._shared_inline_metadata_cache.get(prompt_ref)
        return dict(metadata) if isinstance(metadata, dict) else None

    @classmethod
    def resolve_descriptor_prompt(
        cls,
        domain: str,
        component_type: str,
    ) -> Optional[str]:
        registry = cls.get_domain_registry(domain)
        descriptor_map = registry.get("descriptor_prompts", {})
        if isinstance(descriptor_map, dict) and descriptor_map.get(component_type):
            return str(descriptor_map[component_type])
        return None

    @classmethod
    def resolve_field_prompt(cls, domain: str, component_type: str, section: Dict[str, Any]) -> Optional[str]:
        prompt_ref = section.get("prompt_ref")
        if not prompt_ref:
            raise ValueError(
                f"Section '{component_type}' is missing required prompt_ref. "
                "Fail-fast prompt architecture requires prompt_ref for all schema sections."
            )

        registry = cls.get_domain_registry(domain)
        section_map = registry.get("section_prompts", {})
        if isinstance(section_map, dict) and section_map.get(prompt_ref):
            return str(section_map[prompt_ref])

        shared_map = cls._load_shared_inline_prompts()
        if prompt_ref in shared_map:
            return shared_map[prompt_ref]

        raise ValueError(
            f"prompt_ref '{prompt_ref}' for section '{component_type}' not found in domain/shared registries"
        )

    @classmethod
    def get_schema_prompt(cls, domain: str, component_type: str, include_descriptor: bool = True) -> Optional[str]:
        section = cls.get_section(component_type)
        if not section:
            return None

        descriptor_prompt = None
        if include_descriptor:
            descriptor_prompt = cls.resolve_descriptor_prompt(
                domain=domain,
                component_type=component_type,
            )

        field_prompt = cls.resolve_field_prompt(domain=domain, component_type=component_type, section=section)

        if descriptor_prompt and field_prompt:
            return f"{descriptor_prompt.strip()}\n\n{field_prompt.strip()}"

        if descriptor_prompt:
            return descriptor_prompt

        return field_prompt
