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
    _prompt_catalog_cache: Optional[Dict[str, Any]] = None

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

        registry_path = cls._project_root() / "prompts" / domain / "content_prompts.yaml"
        if not registry_path.exists():
            cls._domain_registry_cache[domain] = {}
            return cls._domain_registry_cache[domain]

        registry = cls._load_yaml_file(registry_path)
        extends_path = registry.get("extends")

        if extends_path:
            base_path = cls._project_root() / str(extends_path)
            base_registry = cls._load_yaml_file(base_path)
            registry = cls._deep_merge(base_registry, registry)

        cls._domain_registry_cache[domain] = registry
        return registry

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
        if not isinstance(prompts, dict):
            raise ValueError(
                f"Invalid section_prompt map in {shared_path}: expected mapping at section_prompts"
            )

        cls._shared_inline_prompts_cache = {k: str(v) for k, v in prompts.items()}
        return cls._shared_inline_prompts_cache

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
