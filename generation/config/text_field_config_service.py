"""Centralized text field config access and resolution helpers.

Single source for generation/text_field_config.yaml loading, alias handling,
and field entry resolution used by prompt assembly and component specs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from shared.utils.yaml_utils import load_yaml

_text_field_config_cache: dict[str, Any] | None = None


def load_text_field_config() -> dict[str, Any]:
    """Load and cache generation/text_field_config.yaml."""
    global _text_field_config_cache

    if _text_field_config_cache is None:
        config_path = Path(__file__).parent.parent / "text_field_config.yaml"
        if not config_path.exists():
            raise FileNotFoundError(
                f"Text field config not found: {config_path}. "
                "Expected location: generation/text_field_config.yaml"
            )

        config = load_yaml(config_path)
        if not isinstance(config, dict):
            raise ValueError("generation/text_field_config.yaml must contain a YAML dictionary")

        _text_field_config_cache = config

    return _text_field_config_cache


def resolve_text_field_name(component_type: str, text_field_config: dict[str, Any] | None = None) -> str:
    """Resolve aliases from component type to canonical field key."""
    config = text_field_config if isinstance(text_field_config, dict) else load_text_field_config()
    aliases = config.get('aliases', {})
    if aliases and not isinstance(aliases, dict):
        raise ValueError("Invalid aliases block in generation/text_field_config.yaml")
    return aliases.get(component_type, component_type)


def resolve_text_field_entry(
    component_type: str,
    text_field_config: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Resolve field config by exact key, alias, and nested section suffix."""
    config = text_field_config if isinstance(text_field_config, dict) else load_text_field_config()
    fields_cfg = config.get('fields')
    if not isinstance(fields_cfg, dict):
        raise ValueError("Missing required fields block in generation/text_field_config.yaml")

    aliases = config.get('aliases', {})
    if aliases and not isinstance(aliases, dict):
        raise ValueError("Invalid aliases block in generation/text_field_config.yaml")

    candidates: list[str] = [component_type]

    alias_target = aliases.get(component_type) if isinstance(aliases, dict) else None
    if isinstance(alias_target, str) and alias_target.strip():
        candidates.append(alias_target.strip())

    if component_type.endswith('.sectionDescription'):
        candidates.append('sectionDescription')
    if component_type.endswith('.sectionTitle'):
        candidates.append('pageTitle')

    # Also support suffix fallback for deeply nested component keys.
    if '.' in component_type:
        suffix = component_type.split('.')[-1]
        if suffix and suffix not in candidates:
            candidates.append(suffix)

    for candidate in candidates:
        entry = fields_cfg.get(candidate)
        if isinstance(entry, dict):
            return entry

    return None


def resolve_base_length(
    component_type: str,
    fallback_length: int,
    text_field_config: dict[str, Any] | None = None,
) -> int:
    """Resolve base length from field config/defaults/fallback."""
    config = text_field_config if isinstance(text_field_config, dict) else load_text_field_config()

    defaults_cfg = config.get('defaults', {})
    if defaults_cfg and not isinstance(defaults_cfg, dict):
        raise ValueError("Invalid defaults block in generation/text_field_config.yaml")

    default_base = defaults_cfg.get('base_length') if isinstance(defaults_cfg, dict) else None
    if default_base is not None and (not isinstance(default_base, int) or default_base <= 0):
        raise ValueError("defaults.base_length must be a positive integer in generation/text_field_config.yaml")

    entry = resolve_text_field_entry(component_type, config)
    if isinstance(entry, dict) and 'base_length' in entry:
        base_length = entry.get('base_length')
        if not isinstance(base_length, int) or base_length <= 0:
            raise ValueError(
                f"Invalid base_length for '{component_type}' in generation/text_field_config.yaml"
            )
        return base_length

    if isinstance(default_base, int) and default_base > 0:
        return default_base

    if not isinstance(fallback_length, int) or fallback_length <= 0:
        raise ValueError(f"Invalid fallback base length for '{component_type}': {fallback_length}")

    return fallback_length


def resolve_extraction_strategy(
    component_type: str,
    fallback_strategy: str = 'raw',
    text_field_config: dict[str, Any] | None = None,
) -> str:
    """Resolve extraction strategy from field config/defaults/fallback."""
    config = text_field_config if isinstance(text_field_config, dict) else load_text_field_config()

    defaults_cfg = config.get('defaults', {})
    if defaults_cfg and not isinstance(defaults_cfg, dict):
        raise ValueError("Invalid defaults block in generation/text_field_config.yaml")

    entry = resolve_text_field_entry(component_type, config)
    strategy = None
    if isinstance(entry, dict):
        strategy = entry.get('extraction_strategy')

    if strategy is None and isinstance(defaults_cfg, dict):
        strategy = defaults_cfg.get('extraction_strategy')

    if strategy is None:
        strategy = fallback_strategy

    if not isinstance(strategy, str) or not strategy.strip():
        raise ValueError(
            f"Invalid extraction_strategy for '{component_type}' in generation/text_field_config.yaml"
        )

    return strategy.strip()
