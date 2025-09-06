#!/usr/bin/env python3
"""
Modular AI Detection Configuration Loader
Loads the core configuration and merges modular components dynamically.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class ModularConfigLoader:
    """Loads AI detection configuration with modular component support."""

    def __init__(self, config_dir: str = "components/text/prompts"):
        self.config_dir = Path(config_dir)
        self._cache = {}

    def load_config(self, use_modular: bool = True) -> Dict[str, Any]:
        """
        Load the complete AI detection configuration.

        Args:
            use_modular: Whether to load modular components or monolithic file

        Returns:
            Complete configuration dictionary
        """
        if use_modular:
            return self._load_modular_config()
        else:
            return self._load_legacy_config()

    def _load_modular_config(self) -> Dict[str, Any]:
        """Load configuration using modular components."""
        # Load core configuration from core/ directory
        core_config = self._load_yaml_file("core/ai_detection_core.yaml")

        if not core_config or "modular_components" not in core_config:
            # Fallback to legacy loading if core config is missing
            return self._load_legacy_config()

        # Load and merge modular components
        merged_config = core_config.copy()

        for component_name, component_path in core_config["modular_components"].items():
            try:
                component_config = self._load_yaml_file(component_path)
                if component_config:
                    # Deep merge the component into the main config
                    merged_config = self._deep_merge(merged_config, component_config)
                    print(f"✅ Loaded modular component: {component_name}")
                else:
                    print(f"⚠️ Failed to load component: {component_name}")
            except Exception as e:
                print(f"❌ Error loading component {component_name}: {e}")

        # Remove the modular_components reference from final config
        if "modular_components" in merged_config:
            del merged_config["modular_components"]

        return merged_config

    def _load_legacy_config(self) -> Dict[str, Any]:
        """Load configuration from monolithic file (fallback)."""
        return self._load_yaml_file("legacy/ai_detection.yaml")

    def _load_yaml_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load a YAML file from the config directory."""
        file_path = self.config_dir / filename

        # Check cache first
        cache_key = str(file_path)
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            if not file_path.exists():
                print(f"⚠️ Configuration file not found: {file_path}")
                return None

            with open(file_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # Cache the result
            self._cache[cache_key] = config
            return config

        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
            return None

    def _deep_merge(
        self, base: Dict[str, Any], update: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()

        for key, value in update.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def clear_cache(self):
        """Clear the configuration cache."""
        self._cache.clear()

    def get_component_info(self) -> Dict[str, Any]:
        """Get information about loaded components."""
        core_config = self._load_yaml_file("core/ai_detection_core.yaml")

        if not core_config or "modular_components" not in core_config:
            return {"modular": False, "components": []}

        components_info = []
        for name, path in core_config["modular_components"].items():
            component_config = self._load_yaml_file(path)
            components_info.append(
                {
                    "name": name,
                    "path": path,
                    "loaded": component_config is not None,
                    "size": len(str(component_config)) if component_config else 0,
                }
            )

        return {
            "modular": True,
            "components": components_info,
            "total_components": len(components_info),
        }


def load_ai_detection_config(use_modular: bool = True) -> Dict[str, Any]:
    """
    Convenience function to load AI detection configuration.

    Args:
        use_modular: Whether to use modular loading (default: True)

    Returns:
        Complete configuration dictionary
    """
    loader = ModularConfigLoader()
    return loader.load_config(use_modular=use_modular)


if __name__ == "__main__":
    # Test the modular loader
    loader = ModularConfigLoader()

    print("🔍 Testing modular configuration loading...")

    # Test modular loading
    config = loader.load_config(use_modular=True)
    if config:
        print(f"✅ Modular config loaded successfully")
        print(f"   - Total top-level sections: {len(config)}")
        print(
            f"   - Has human_writing_characteristics: {'human_writing_characteristics' in config}"
        )
        print(f"   - Has ai_detection_avoidance: {'ai_detection_avoidance' in config}")
    else:
        print("❌ Failed to load modular config")

    # Test component info
    info = loader.get_component_info()
    print(f"\n📊 Component Information:")
    print(f"   - Modular: {info['modular']}")
    print(f"   - Total components: {info['total_components']}")
    for comp in info["components"]:
        status = "✅" if comp["loaded"] else "❌"
        print(f"   - {comp['name']}: {status} ({comp['size']} chars)")
