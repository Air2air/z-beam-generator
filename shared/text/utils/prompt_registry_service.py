"""Centralized prompt/schema access for section prompts and descriptor chains."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class PromptRegistryService:
    """Single access layer for schema sections, registries, and prompt references."""

    _COMPONENT_PROMPT_REGISTRY_RELATIVE_PATH = Path("prompts/registry/component_prompt_registry.yaml")
    _COMPONENT_SHORT_CONTENT_PROMPT_REGISTRY_RELATIVE_PATH = Path(
        "prompts/registry/component_short_content_prompts.yaml"
    )

    _schema_cache: Optional[Dict[str, Any]] = None
    _domain_registry_cache: Dict[str, Dict[str, Any]] = {}
    _shared_prompt_registry_cache: Optional[Dict[str, Any]] = None
    _shared_inline_prompts_cache: Optional[Dict[str, str]] = None
    _shared_inline_metadata_cache: Optional[Dict[str, Dict[str, Any]]] = None
    _prompt_catalog_cache: Optional[Dict[str, Any]] = None
    _single_line_component_prompts_cache: Optional[Dict[str, Dict[str, Any]]] = None
    _faq_prompt_cache: Optional[Dict[str, Any]] = None
    _domain_text_prompt_entries_cache: Dict[str, Dict[str, Dict[str, str]]] = {}
    _domain_non_text_prompt_cache: Dict[str, str] = {}
    _prompt_gate_config_cache: Optional[Dict[str, Any]] = None
    _generation_config_cache: Optional[Dict[str, Any]] = None
    _domain_optimizer_prompt_cache: Dict[str, Optional[str]] = {}
    _component_prompt_registry_cache: Optional[Dict[str, Any]] = None
    _component_short_content_prompt_registry_cache: Optional[Dict[str, Any]] = None

    @classmethod
    def _get_component_prompt_registry_path(cls, domain: str) -> Path:
        registry_path = cls._project_root() / cls._COMPONENT_PROMPT_REGISTRY_RELATIVE_PATH
        if not registry_path.exists():
            raise FileNotFoundError(
                f"Configured component prompt registry does not exist for '{domain}': {registry_path}"
            )

        return registry_path

    @classmethod
    def _load_component_prompt_registry(cls, domain: str) -> Dict[str, Any]:
        if cls._component_prompt_registry_cache is not None:
            return cls._component_prompt_registry_cache

        registry_path = cls._get_component_prompt_registry_path(domain)
        registry = cls._load_yaml_file(registry_path)
        cls._component_prompt_registry_cache = registry
        return registry

    @classmethod
    def _load_component_short_content_prompt_registry(cls) -> Dict[str, Any]:
        if cls._component_short_content_prompt_registry_cache is not None:
            return cls._component_short_content_prompt_registry_cache

        registry_path = cls._project_root() / cls._COMPONENT_SHORT_CONTENT_PROMPT_REGISTRY_RELATIVE_PATH
        if not registry_path.exists():
            raise FileNotFoundError(
                "Configured short-content prompt registry does not exist: "
                f"{registry_path}"
            )

        registry = cls._load_yaml_file(registry_path)
        required_variables = registry.get("required_variables")
        if not isinstance(required_variables, list):
            raise ValueError("Short-content prompt registry requires list: required_variables")

        required_variable_set = {str(value).strip() for value in required_variables if isinstance(value, str)}
        required_expected = {"subject", "category", "context"}
        if not required_expected.issubset(required_variable_set):
            raise ValueError(
                "Short-content prompt registry required_variables must include "
                "subject, category, context"
            )

        by_component = registry.get("by_component")
        if not isinstance(by_component, dict):
            raise ValueError("Short-content prompt registry requires mapping: by_component")

        cls._component_short_content_prompt_registry_cache = registry
        return registry

    @classmethod
    def _resolve_short_content_prompt(
        cls,
        component_type: str,
        prompt_ref: Optional[str],
    ) -> Optional[str]:
        registry = cls._load_component_short_content_prompt_registry()
        by_component = registry.get("by_component")
        if not isinstance(by_component, dict):
            return None

        candidate_keys: list[str] = []
        if isinstance(prompt_ref, str) and prompt_ref.strip():
            candidate_keys.append(prompt_ref.strip())
        if isinstance(component_type, str) and component_type.strip():
            candidate_keys.append(component_type.strip())

        seen: set[str] = set()
        for key in candidate_keys:
            if key in seen:
                continue
            seen.add(key)

            entry = by_component.get(key)
            if not isinstance(entry, dict):
                continue

            prompt = entry.get("prompt")
            if isinstance(prompt, str) and prompt.strip():
                return prompt.strip()

        return None

    @staticmethod
    def _resolve_scoped_prompt_value(scope: Any, domain: str) -> Optional[str]:
        if not isinstance(scope, dict):
            return None

        domains_map = scope.get("domains")
        if isinstance(domains_map, dict):
            domain_value = domains_map.get(domain)
            if isinstance(domain_value, str) and domain_value.strip():
                return domain_value.strip()

        shared_value = scope.get("shared")
        if isinstance(shared_value, str) and shared_value.strip():
            return shared_value.strip()

        return None

    @classmethod
    def _resolve_component_descriptor_prompt(cls, domain: str, component_type: str) -> Optional[str]:
        registry = cls._load_component_prompt_registry(domain)
        components = registry.get("components")
        if not isinstance(components, dict):
            return None

        component_entry = components.get(component_type)
        if not isinstance(component_entry, dict):
            return None

        descriptor_scope = component_entry.get("descriptor")
        return cls._resolve_scoped_prompt_value(descriptor_scope, domain)

    @classmethod
    def _resolve_component_text_prompt_entry(
        cls,
        domain: str,
        component_key: str,
    ) -> Optional[Dict[str, str]]:
        registry = cls._load_component_prompt_registry(domain)
        components = registry.get("components")
        if not isinstance(components, dict):
            return None

        component_entry = components.get(component_key)
        if not isinstance(component_entry, dict):
            return None

        text_scope = component_entry.get("text")
        if not isinstance(text_scope, dict):
            return None

        domains_map = text_scope.get("domains")
        if isinstance(domains_map, dict):
            domain_entry = domains_map.get(domain)
            if isinstance(domain_entry, dict):
                return {
                    key: value.strip()
                    for key, value in domain_entry.items()
                    if isinstance(key, str) and isinstance(value, str) and value.strip()
                }

        shared_entry = text_scope.get("shared")
        if isinstance(shared_entry, dict):
            return {
                key: value.strip()
                for key, value in shared_entry.items()
                if isinstance(key, str) and isinstance(value, str) and value.strip()
            }

        return None

    @classmethod
    def _resolve_component_non_text_prompt(cls, domain: str) -> Optional[str]:
        registry = cls._load_component_prompt_registry(domain)
        return cls._resolve_scoped_prompt_value(registry.get("non_text"), domain)

    @classmethod
    def _resolve_component_optimizer_prompt(cls, domain: str) -> Optional[str]:
        registry = cls._load_component_prompt_registry(domain)
        return cls._resolve_scoped_prompt_value(registry.get("optimizer"), domain)

    @staticmethod
    def _normalize_prompt_line(line: str) -> str:
        """Normalize a prompt line for conservative duplicate detection."""
        return re.sub(r"\s+", " ", line.strip().lower())

    @classmethod
    def _is_descriptor_redundant_for_field_prompt(
        cls,
        descriptor_prompt: str,
        field_prompt: str,
    ) -> bool:
        """Determine whether descriptor guidance is redundant when field prompt is already specific."""
        descriptor = descriptor_prompt.strip()
        field = field_prompt.strip()
        if not descriptor or not field:
            return False

        normalized_descriptor = cls._normalize_prompt_line(descriptor)
        normalized_field = cls._normalize_prompt_line(field)

        if normalized_descriptor and normalized_descriptor in normalized_field:
            return True

        directive_tokens = (
            "describe",
            "write",
            "summarize",
            "provide",
            "list",
            "state",
            "explain",
        )

        if len(field) >= 80 and any(token in normalized_field for token in directive_tokens):
            if "{subject}" in field or "{context}" in field:
                return True

        return False

    @classmethod
    def _dedupe_optimizer_prompt(cls, base_prompt: str, optimizer_prompt: str) -> str:
        """Remove optimizer lines that are already present in the base prompt."""
        base_lines = {
            cls._normalize_prompt_line(line)
            for line in base_prompt.splitlines()
            if cls._normalize_prompt_line(line)
        }

        deduped_lines: list[str] = []
        for raw_line in optimizer_prompt.splitlines():
            normalized_line = cls._normalize_prompt_line(raw_line)
            if not normalized_line:
                deduped_lines.append(raw_line)
                continue
            if normalized_line in base_lines:
                continue
            deduped_lines.append(raw_line)

        deduped = "\n".join(deduped_lines).strip()
        return deduped

    @classmethod
    def _load_domain_optimizer_prompt(cls, domain: str) -> Optional[str]:
        if domain in cls._domain_optimizer_prompt_cache:
            return cls._domain_optimizer_prompt_cache[domain]

        component_optimizer_prompt = cls._resolve_component_optimizer_prompt(domain)
        if isinstance(component_optimizer_prompt, str) and component_optimizer_prompt.strip():
            cls._domain_optimizer_prompt_cache[domain] = component_optimizer_prompt.strip()
            return cls._domain_optimizer_prompt_cache[domain]

        cls._domain_optimizer_prompt_cache[domain] = None
        return None

    @classmethod
    def _load_generation_config(cls) -> Dict[str, Any]:
        if cls._generation_config_cache is None:
            config_path = cls._project_root() / "generation" / "config.yaml"
            cls._generation_config_cache = cls._load_yaml_file(config_path)
        return cls._generation_config_cache

    @classmethod
    def _load_prompt_gate_config(cls) -> Dict[str, Any]:
        if cls._prompt_gate_config_cache is not None:
            return cls._prompt_gate_config_cache

        config_path = cls._project_root() / "config" / "final_prompt_gate.yaml"
        if not config_path.exists():
            cls._prompt_gate_config_cache = {}
            return cls._prompt_gate_config_cache

        cls._prompt_gate_config_cache = cls._load_yaml_file(config_path)
        return cls._prompt_gate_config_cache

    @classmethod
    def _get_min_description_words(cls) -> int:
        config = cls._load_generation_config()
        shared_validation = config.get("shared_domain_validation")
        if not isinstance(shared_validation, dict):
            raise KeyError("Missing required config block: shared_domain_validation")
        if "min_description_words" not in shared_validation:
            raise KeyError("Missing required config key: shared_domain_validation.min_description_words")
        min_words = shared_validation["min_description_words"]
        if not isinstance(min_words, int):
            raise TypeError("shared_domain_validation.min_description_words must be an integer")
        return min_words

    @classmethod
    def _get_prompt_gate_max_words(cls, component_type: str) -> Optional[int]:
        config = cls._load_prompt_gate_config()
        components = config.get("components")
        if not isinstance(components, list):
            return None

        for component in components:
            if not isinstance(component, dict):
                continue
            if component.get("name") != component_type:
                continue
            checks = component.get("checks")
            if not isinstance(checks, dict):
                raise KeyError(
                    f"Prompt gate config for '{component_type}' missing required 'checks' mapping"
                )
            if "max_prompt_words" not in checks:
                raise KeyError(
                    f"Prompt gate config for '{component_type}' missing required 'checks.max_prompt_words'"
                )
            max_words = checks["max_prompt_words"]
            if not isinstance(max_words, int):
                raise TypeError(
                    f"Prompt gate config for '{component_type}' requires integer checks.max_prompt_words"
                )
            return max_words

        return None

    @classmethod
    def _should_include_optimizer_prompt(
        cls,
        component_type: str,
        base_prompt: str,
        optimizer_prompt: str
    ) -> bool:
        from shared.text.utils.component_specs import ComponentRegistry

        min_description_words = cls._get_min_description_words()
        base_length = ComponentRegistry.get_default_length(component_type)
        if base_length < min_description_words:
            return False

        max_prompt_words = cls._get_prompt_gate_max_words(component_type)
        if max_prompt_words is None:
            return True

        combined_words = len(base_prompt.split()) + len(optimizer_prompt.split())
        return combined_words <= max_prompt_words

    @classmethod
    def _load_domain_text_prompt_entries(cls, domain: str) -> Dict[str, Dict[str, str]]:
        cached = cls._domain_text_prompt_entries_cache.get(domain)
        if isinstance(cached, dict) and cached:
            return cached

        normalized: Dict[str, Dict[str, str]] = {}
        registry = cls._load_component_prompt_registry(domain)
        components = registry.get("components")
        if not isinstance(components, dict):
            raise ValueError("Component prompt registry missing required mapping: components")

        for key in components:
            if not isinstance(key, str) or not key.strip():
                continue
            entry = cls._resolve_component_text_prompt_entry(domain, key.strip())
            if isinstance(entry, dict) and entry:
                normalized[key.strip()] = entry

        if not normalized:
            raise ValueError(
                f"Component prompt registry must provide non-empty text entries for domain '{domain}'"
            )

        cls._domain_text_prompt_entries_cache[domain] = normalized
        return normalized

    @classmethod
    def _load_domain_non_text_prompt(cls, domain: str) -> str:
        component_non_text_prompt = cls._resolve_component_non_text_prompt(domain)
        if isinstance(component_non_text_prompt, str) and component_non_text_prompt.strip():
            return component_non_text_prompt.strip()

        raise ValueError(
            f"Component prompt registry missing required non_text prompt for domain '{domain}'"
        )

    @staticmethod
    def _is_non_text_prompt_ref(prompt_ref: str) -> bool:
        normalized = prompt_ref.strip()
        return normalized.endswith("Title")

    @staticmethod
    def _expected_text_child_key(entry_key: str, prompt_ref: Optional[str] = None) -> str:
        normalized = entry_key.strip()
        if normalized.endswith(".sectionTitle"):
            return "sectionTitle"
        if normalized.endswith(".sectionDescription"):
            return "sectionDescription"
        if isinstance(prompt_ref, str) and prompt_ref.strip().endswith("Title"):
            return "sectionTitle"
        return "prompt"

    @classmethod
    def _resolve_text_prompt_entry(
        cls,
        entry_key: str,
        entry_value: Dict[str, str],
        prompt_ref: Optional[str],
    ) -> Optional[str]:
        if not isinstance(entry_value, dict):
            return None

        normalized_key = entry_key.strip()
        if normalized_key.endswith(".sectionTitle"):
            value = entry_value.get("sectionTitle")
            return value.strip() if isinstance(value, str) and value.strip() else None
        if normalized_key.endswith(".sectionDescription"):
            value = entry_value.get("sectionDescription")
            return value.strip() if isinstance(value, str) and value.strip() else None

        section_title = entry_value.get("sectionTitle")
        section_description = entry_value.get("sectionDescription")
        if isinstance(section_title, str) and section_title.strip() and isinstance(section_description, str) and section_description.strip():
            if isinstance(prompt_ref, str) and prompt_ref.strip().endswith("Title"):
                return section_title.strip()
            return section_description.strip()

        expected_child = cls._expected_text_child_key(normalized_key, prompt_ref)
        child_value = entry_value.get(expected_child)
        if isinstance(child_value, str) and child_value.strip():
            return child_value.strip()

        fallback = entry_value.get("prompt")
        if isinstance(fallback, str) and fallback.strip():
            return fallback.strip()

        return None

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
    def _get_shared_prompt_registry(cls) -> Dict[str, Any]:
        """Load canonical shared prompt registry (section + FAQ prompt source of truth)."""
        if cls._shared_prompt_registry_cache is None:
            registry_path = cls._project_root() / "prompts" / "registry" / "shared_prompt_registry.yaml"
            registry = cls._load_yaml_file(registry_path)

            section_prompts = registry.get("section_prompts")
            section_prompt_metadata = registry.get("section_prompt_metadata")
            if not isinstance(section_prompts, dict):
                raise ValueError(
                    f"Invalid shared prompt registry in {registry_path}: expected mapping at section_prompts"
                )
            if not isinstance(section_prompt_metadata, dict):
                raise ValueError(
                    f"Invalid shared prompt registry in {registry_path}: expected mapping at section_prompt_metadata"
                )

            cls._shared_prompt_registry_cache = registry

        return cls._shared_prompt_registry_cache

    @classmethod
    def get_faq_prompt_registry(cls) -> Dict[str, Any]:
        """Load canonical FAQ prompt definitions from shared prompt registry."""
        if cls._faq_prompt_cache is None:
            registry = cls._get_shared_prompt_registry()
            section_prompts = registry.get("section_prompts")
            section_prompt_metadata = registry.get("section_prompt_metadata")

            if not isinstance(section_prompts, dict):
                raise ValueError("Shared prompt registry missing section_prompts mapping")
            if not isinstance(section_prompt_metadata, dict):
                raise ValueError("Shared prompt registry missing section_prompt_metadata mapping")

            faq_prompt = section_prompts.get("faq")
            faq_metadata = section_prompt_metadata.get("faq")
            if not isinstance(faq_prompt, str) or not faq_prompt.strip():
                raise ValueError("Shared prompt registry missing required section_prompts.faq")
            if not isinstance(faq_metadata, dict):
                raise ValueError("Shared prompt registry missing required section_prompt_metadata.faq")

            single_line_by_domain: Dict[str, Dict[str, Any]] = {}
            for domain in ("applications", "materials", "contaminants", "compounds", "settings"):
                domain_prompts = cls._load_domain_text_prompt_entries(domain)
                faq_entry = domain_prompts.get("faq")
                faq_prompt = cls._resolve_text_prompt_entry("faq", faq_entry or {}, "faq") if isinstance(faq_entry, dict) else None
                if isinstance(faq_prompt, str) and faq_prompt.strip():
                    single_line_by_domain[domain] = {
                        "prompt": faq_prompt.strip(),
                        "variables": ["subject", "context"],
                    }

            if not single_line_by_domain:
                raise ValueError(
                    "component prompt registry missing FAQ single-line entries by domain"
                )

            cls._faq_prompt_cache = {
                "shared_section_prompt": faq_prompt.strip(),
                "shared_section_metadata": dict(faq_metadata),
                "single_line": {"by_domain": single_line_by_domain},
            }
        return cls._faq_prompt_cache

    @classmethod
    def get_single_line_component_prompts(cls) -> Dict[str, Dict[str, Any]]:
        """Derive single-line component prompt registry from centralized component prompt registry."""
        if cls._single_line_component_prompts_cache is None:
            normalized_by_domain: Dict[str, Dict[str, Any]] = {}
            for domain_key in ("applications", "materials", "contaminants", "compounds", "settings"):
                domain_prompts = cls._load_domain_text_prompt_entries(domain_key)
                normalized_prompts: Dict[str, Any] = {}

                for component_key, prompt_entry in domain_prompts.items():
                    if not isinstance(component_key, str) or not component_key.strip():
                        continue
                    if not isinstance(prompt_entry, dict):
                        continue

                    resolved_prompt = cls._resolve_text_prompt_entry(component_key, prompt_entry, component_key)
                    if not isinstance(resolved_prompt, str) or not resolved_prompt.strip():
                        continue

                    normalized_prompts[component_key] = {
                        "prompt": resolved_prompt.strip(),
                        "variables": ["subject", "context"],
                    }

                normalized_by_domain[domain_key] = normalized_prompts

            cls._single_line_component_prompts_cache = normalized_by_domain
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
            entry = registry.get(component_type)
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
    def _get_shared_registry_value(cls, keys: tuple[str, ...]) -> str:
        """Read required string value from consolidated shared prompt registry by nested path."""
        value: Any = cls._get_shared_prompt_registry()
        traversed: list[str] = []

        for key in keys:
            traversed.append(key)
            if not isinstance(value, dict) or key not in value:
                dotted = ".".join(traversed)
                raise KeyError(f"Missing required shared prompt registry key: {dotted}")
            value = value[key]

        if not isinstance(value, str) or not value.strip():
            dotted = ".".join(keys)
            raise ValueError(f"Shared prompt registry value must be non-empty string: {dotted}")

        return value

    @classmethod
    def get_shared_text_prompt_core(cls) -> str:
        registry = cls._get_shared_prompt_registry()
        shared_core = registry.get("shared_core_prompts")
        if not isinstance(shared_core, dict):
            raise KeyError("Missing required shared prompt registry key: shared_core_prompts")

        section_order = shared_core.get("textPromptCoreOrder")
        sections = shared_core.get("textPromptCoreSections")

        if isinstance(section_order, list) and isinstance(sections, dict):
            normalized_order: list[str] = []
            for key in section_order:
                if not isinstance(key, str) or not key.strip():
                    raise ValueError("shared_core_prompts.textPromptCoreOrder must contain non-empty strings")
                normalized_order.append(key.strip())

            if not normalized_order:
                raise ValueError("shared_core_prompts.textPromptCoreOrder must not be empty")

            lines = ["GLOBAL TEXT GENERATION CORE (REUSABLE)"]
            for section_key in normalized_order:
                section_text = sections.get(section_key)
                if not isinstance(section_text, str) or not section_text.strip():
                    raise ValueError(
                        f"Missing or invalid shared_core_prompts.textPromptCoreSections.{section_key}"
                    )
                lines.append(f"- {section_text.strip()}")

            return "\n".join(lines)

        return cls._get_shared_registry_value(("shared_core_prompts", "textPromptCore"))

    @classmethod
    def get_opening_style_bank(cls) -> list[str]:
        registry = cls._get_shared_prompt_registry()
        styles = registry.get("shared_core_prompts", {}).get("opening_style_bank")
        if not isinstance(styles, list) or not styles:
            raise ValueError("shared_core_prompts.opening_style_bank must be a non-empty list")

        normalized: list[str] = []
        for style in styles:
            if isinstance(style, str) and style.strip():
                normalized.append(style.strip())

        if not normalized:
            raise ValueError("shared_core_prompts.opening_style_bank must contain non-empty strings")

        return normalized

    @classmethod
    def get_humanness_template(cls, compact: bool = False) -> str:
        variant = "compact" if compact else "full"
        registry = cls._get_shared_prompt_registry()
        shared_core = registry.get("shared_core_prompts")
        if not isinstance(shared_core, dict):
            raise KeyError("Missing required shared prompt registry key: shared_core_prompts")

        humanness = shared_core.get("humanness")
        if not isinstance(humanness, dict):
            raise KeyError("Missing required shared prompt registry key: shared_core_prompts.humanness")

        order_key = f"{variant}Order"
        sections_key = f"{variant}Sections"
        section_order = humanness.get(order_key)
        sections = humanness.get(sections_key)

        if isinstance(section_order, list) and isinstance(sections, dict):
            normalized_order: list[str] = []
            for key in section_order:
                if not isinstance(key, str) or not key.strip():
                    raise ValueError(
                        f"shared_core_prompts.humanness.{order_key} must contain non-empty strings"
                    )
                normalized_order.append(key.strip())

            if not normalized_order:
                raise ValueError(f"shared_core_prompts.humanness.{order_key} must not be empty")

            blocks: list[str] = []
            for section_key in normalized_order:
                section_text = sections.get(section_key)
                if not isinstance(section_text, str) or not section_text.strip():
                    raise ValueError(
                        f"Missing or invalid shared_core_prompts.humanness.{sections_key}.{section_key}"
                    )
                blocks.append(section_text.strip())

            return "\n\n".join(blocks)

        return cls._get_shared_registry_value(("shared_core_prompts", "humanness", variant))

    @classmethod
    def get_quality_evaluation_prompt(cls) -> str:
        registry = cls._get_shared_prompt_registry()
        shared_core = registry.get("shared_core_prompts")
        if not isinstance(shared_core, dict):
            raise KeyError("Missing required shared prompt registry key: shared_core_prompts")

        quality = shared_core.get("quality")
        if not isinstance(quality, dict):
            raise KeyError("Missing required shared prompt registry key: shared_core_prompts.quality")

        section_order = quality.get("evaluationOrder")
        sections = quality.get("evaluationSections")

        if isinstance(section_order, list) and isinstance(sections, dict):
            normalized_order: list[str] = []
            for key in section_order:
                if not isinstance(key, str) or not key.strip():
                    raise ValueError(
                        "shared_core_prompts.quality.evaluationOrder must contain non-empty strings"
                    )
                normalized_order.append(key.strip())

            if not normalized_order:
                raise ValueError("shared_core_prompts.quality.evaluationOrder must not be empty")

            blocks: list[str] = []
            for section_key in normalized_order:
                section_text = sections.get(section_key)
                if not isinstance(section_text, str) or not section_text.strip():
                    raise ValueError(
                        f"Missing or invalid shared_core_prompts.quality.evaluationSections.{section_key}"
                    )
                blocks.append(section_text.strip())

            return "\n\n".join(blocks)

        return cls._get_shared_registry_value(("shared_core_prompts", "quality", "evaluation"))

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

        component_registry = cls._load_component_prompt_registry(domain)
        components = component_registry.get("components")
        if not isinstance(components, dict):
            raise ValueError("Component prompt registry missing required mapping: components")

        descriptor_prompts: Dict[str, str] = {}
        for component_key in components:
            if not isinstance(component_key, str) or not component_key.strip():
                continue
            descriptor_value = cls._resolve_component_descriptor_prompt(domain, component_key.strip())
            if isinstance(descriptor_value, str) and descriptor_value.strip():
                descriptor_prompts[component_key.strip()] = descriptor_value.strip()

        schema_version = component_registry.get("schemaVersion")
        registry: Dict[str, Any] = {
            "schemaVersion": schema_version,
            "descriptor_prompts": descriptor_prompts,
        }
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

        shared_path = cls._project_root() / "prompts" / "registry" / "shared_prompt_registry.yaml"
        shared = cls._get_shared_prompt_registry()
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
        component_descriptor_prompt = cls._resolve_component_descriptor_prompt(domain, component_type)
        if isinstance(component_descriptor_prompt, str) and component_descriptor_prompt.strip():
            return component_descriptor_prompt.strip()
        return None

    @classmethod
    def resolve_field_prompt(cls, domain: str, component_type: str, section: Dict[str, Any]) -> Optional[str]:
        prompt_ref = section.get("prompt_ref")
        if not prompt_ref:
            raise ValueError(
                f"Section '{component_type}' is missing required prompt_ref. "
                "Fail-fast prompt architecture requires prompt_ref for all schema sections."
            )

        component_entry = cls._resolve_component_text_prompt_entry(domain, component_type)
        if isinstance(component_entry, dict):
            component_field_prompt = cls._resolve_text_prompt_entry(component_type, component_entry, prompt_ref)
            if isinstance(component_field_prompt, str) and component_field_prompt.strip():
                return component_field_prompt.strip()

        component_entry_by_ref = cls._resolve_component_text_prompt_entry(domain, str(prompt_ref))
        if isinstance(component_entry_by_ref, dict):
            component_field_prompt_by_ref = cls._resolve_text_prompt_entry(
                str(prompt_ref),
                component_entry_by_ref,
                prompt_ref,
            )
            if isinstance(component_field_prompt_by_ref, str) and component_field_prompt_by_ref.strip():
                return component_field_prompt_by_ref.strip()

        if cls._is_non_text_prompt_ref(prompt_ref):
            return cls._load_domain_non_text_prompt(domain)

        shared_map = cls._load_shared_inline_prompts()
        if prompt_ref in shared_map:
            return shared_map[prompt_ref]

        raise ValueError(
            f"prompt_ref '{prompt_ref}' for section '{component_type}' not found in component prompt registry or shared prompt registry"
        )

    @classmethod
    def get_schema_prompt(cls, domain: str, component_type: str, include_descriptor: bool = True) -> Optional[str]:
        section = cls.get_section(component_type)
        if not section:
            return None

        prompt_ref = section.get("prompt_ref")
        short_content_prompt: Optional[str] = None
        if isinstance(prompt_ref, str) and not cls._is_non_text_prompt_ref(prompt_ref):
            short_content_prompt = cls._resolve_short_content_prompt(
                component_type=component_type,
                prompt_ref=prompt_ref,
            )

        descriptor_prompt = None
        if include_descriptor:
            descriptor_prompt = cls.resolve_descriptor_prompt(
                domain=domain,
                component_type=component_type,
            )

        field_prompt = cls.resolve_field_prompt(domain=domain, component_type=component_type, section=section)

        optimizer_prompt = cls._load_domain_optimizer_prompt(domain)

        if descriptor_prompt and field_prompt:
            if cls._is_descriptor_redundant_for_field_prompt(descriptor_prompt, field_prompt):
                base_prompt = field_prompt.strip()
            else:
                base_prompt = f"{descriptor_prompt.strip()}\n\n{field_prompt.strip()}"
        elif descriptor_prompt:
            base_prompt = descriptor_prompt
        else:
            base_prompt = field_prompt

        if short_content_prompt and base_prompt:
            base_prompt = f"{short_content_prompt.strip()}\n\n{base_prompt.strip()}"
        elif short_content_prompt:
            base_prompt = short_content_prompt

        if optimizer_prompt and base_prompt:
            if cls._should_include_optimizer_prompt(component_type, base_prompt, optimizer_prompt):
                deduped_optimizer_prompt = cls._dedupe_optimizer_prompt(
                    base_prompt=base_prompt,
                    optimizer_prompt=optimizer_prompt,
                )
                if deduped_optimizer_prompt:
                    return f"{base_prompt.strip()}\n\n{deduped_optimizer_prompt}"

        return base_prompt
