#!/usr/bin/env python3
"""
Environment Checker

Centralized environment validation and configuration checking.
Extracted from run.py to reduce bloat and improve testability.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List

# Import API providers and COMPONENT_CONFIG directly to avoid circular imports
from api.config import API_PROVIDERS
from api.env_loader import EnvLoader
from run import COMPONENT_CONFIG


def check_environment() -> Dict[str, Any]:
    """
    Comprehensive environment check for Z-Beam system.

    Returns:
        Dictionary with detailed environment status
    """
    # Load environment variables
    EnvLoader.load_env()

    results = {
        "api_keys": {},
        "files": {},
        "configuration": {},
        "directories": {},
        "overall_status": "unknown",
        "critical_issues": [],
        "warnings": [],
    }

    # Check API keys
    for provider_id, config in API_PROVIDERS.items():
        api_key = os.getenv(config["env_var"])
        results["api_keys"][provider_id] = {
            "provider": config["name"],
            "env_var": config["env_var"],
            "configured": bool(api_key),
            "key_length": len(api_key) if api_key else 0,
            "masked_key": f"{api_key[:8]}...{api_key[-4:]}"
            if api_key and len(api_key) > 12
            else "Not set",
        }

        if not api_key:
            results["critical_issues"].append(
                f"Missing API key for {config['name']} ({config['env_var']})"
            )

    # Check required files
    required_files = [
        "components/author/authors.json",
        "data/materials.yaml",
        "cli/component_config.py",
        "api/config.py",
    ]

    for file_path in required_files:
        path = Path(file_path)
        results["files"][file_path] = {
            "exists": path.exists(),
            "size": path.stat().st_size if path.exists() else 0,
            "readable": path.is_file() and os.access(path, os.R_OK)
            if path.exists()
            else False,
        }

        if not path.exists():
            results["critical_issues"].append(f"Missing required file: {file_path}")
        elif not (path.is_file() and os.access(path, os.R_OK)):
            results["critical_issues"].append(f"Cannot read required file: {file_path}")

    # Check configuration
    try:
        components_config = COMPONENT_CONFIG.get("components", {})
        results["configuration"]["components_loaded"] = len(components_config)
        results["configuration"]["enabled_components"] = sum(
            1 for config in components_config.values() if config.get("enabled", False)
        )

        # Check for missing required configuration fields
        for component, config in components_config.items():
            required_fields = ["enabled", "data_provider", "api_provider"]
            missing_fields = [field for field in required_fields if field not in config]
            if missing_fields:
                results["warnings"].append(
                    f"Component {component} missing fields: {missing_fields}"
                )

    except Exception as e:
        results["critical_issues"].append(f"Configuration loading error: {e}")
        results["configuration"]["error"] = str(e)

    # Check directories
    required_dirs = ["content", "components", "api", "generators", "utils"]
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        results["directories"][dir_name] = {
            "exists": dir_path.exists(),
            "writable": dir_path.is_dir() and os.access(dir_path, os.W_OK)
            if dir_path.exists()
            else False,
        }

        if not dir_path.exists():
            results["warnings"].append(f"Directory missing: {dir_name}")
        elif not (dir_path.is_dir() and os.access(dir_path, os.W_OK)):
            results["warnings"].append(f"Directory not writable: {dir_name}")

    # Determine overall status
    if results["critical_issues"]:
        results["overall_status"] = "critical"
    elif results["warnings"]:
        results["overall_status"] = "warning"
    else:
        results["overall_status"] = "healthy"

    return results


def format_environment_report(results: Dict[str, Any]) -> str:
    """
    Format environment check results into readable report.

    Args:
        results: Results from check_environment()

    Returns:
        Formatted report string
    """
    lines = []

    # Header
    status_emoji = {"healthy": "✅", "warning": "⚠️", "critical": "❌"}

    lines.extend(
        [
            f"{status_emoji.get(results['overall_status'], '❓')} Z-BEAM ENVIRONMENT STATUS: {results['overall_status'].upper()}",
            "=" * 60,
        ]
    )

    # Critical issues
    if results["critical_issues"]:
        lines.extend(["", "🚨 CRITICAL ISSUES:", "-" * 20])
        for issue in results["critical_issues"]:
            lines.append(f"  ❌ {issue}")

    # Warnings
    if results["warnings"]:
        lines.extend(["", "⚠️  WARNINGS:", "-" * 12])
        for warning in results["warnings"]:
            lines.append(f"  ⚠️  {warning}")

    # API Keys status
    lines.extend(["", "🔑 API KEYS:", "-" * 12])

    for provider_id, api_info in results["api_keys"].items():
        status = "✅" if api_info["configured"] else "❌"
        lines.append(f"  {status} {api_info['provider']}: {api_info['masked_key']}")

    # Files status
    lines.extend(["", "📁 REQUIRED FILES:", "-" * 18])

    for file_path, file_info in results["files"].items():
        if file_info["exists"] and file_info["readable"]:
            status = "✅"
            size_info = f"({file_info['size']} bytes)"
        elif file_info["exists"]:
            status = "⚠️"
            size_info = "(not readable)"
        else:
            status = "❌"
            size_info = "(missing)"

        lines.append(f"  {status} {file_path} {size_info}")

    # Configuration status
    lines.extend(["", "⚙️  CONFIGURATION:", "-" * 16])

    if "error" in results["configuration"]:
        lines.append(f"  ❌ Configuration error: {results['configuration']['error']}")
    else:
        lines.append(
            f"  ✅ Components loaded: {results['configuration']['components_loaded']}"
        )
        lines.append(
            f"  ✅ Enabled components: {results['configuration']['enabled_components']}"
        )

    # Directories status
    lines.extend(["", "📂 DIRECTORIES:", "-" * 14])

    for dir_name, dir_info in results["directories"].items():
        if dir_info["exists"] and dir_info["writable"]:
            status = "✅"
            access_info = "(writable)"
        elif dir_info["exists"]:
            status = "⚠️"
            access_info = "(read-only)"
        else:
            status = "❌"
            access_info = "(missing)"

        lines.append(f"  {status} {dir_name}/ {access_info}")

    # Footer
    lines.extend(["", "=" * 60, ""])

    if results["overall_status"] == "healthy":
        lines.append("🎉 Environment is healthy and ready for content generation!")
    elif results["overall_status"] == "warning":
        lines.append("⚠️  Environment has warnings but should still work.")
    else:
        lines.append("🚨 Environment has critical issues that must be resolved.")

    return "\n".join(lines)


def validate_component_configuration() -> Dict[str, Any]:
    """
    Validate component configuration in detail.

    Returns:
        Dictionary with component validation results
    """
    results = {
        "valid_components": [],
        "invalid_components": [],
        "configuration_errors": [],
        "warnings": [],
    }

    try:
        components_config = COMPONENT_CONFIG.get("components", {})

        for component_name, config in components_config.items():
            component_result = {
                "name": component_name,
                "enabled": config.get("enabled", False),
                "data_provider": config.get("data_provider", "unknown"),
                "api_provider": config.get("api_provider", "unknown"),
                "issues": [],
            }

            # Check required fields
            required_fields = ["enabled", "data_provider", "api_provider"]
            for field in required_fields:
                if field not in config:
                    component_result["issues"].append(f"Missing field: {field}")

            # Validate field values
            if config.get("data_provider") not in ["API", "static", "hybrid"]:
                component_result["issues"].append(
                    f"Invalid data_provider: {config.get('data_provider')}"
                )

            if (
                config.get("api_provider")
                and config.get("api_provider") not in API_PROVIDERS
            ):
                component_result["issues"].append(
                    f"Invalid api_provider: {config.get('api_provider')}"
                )

            # Check component directory exists
            component_dir = Path(f"components/{component_name}")
            if not component_dir.exists():
                component_result["issues"].append(
                    f"Component directory missing: {component_dir}"
                )

            # Categorize component
            if component_result["issues"]:
                results["invalid_components"].append(component_result)
            else:
                results["valid_components"].append(component_result)

    except Exception as e:
        results["configuration_errors"].append(
            f"Failed to load component configuration: {e}"
        )

    return results


def check_material_data() -> Dict[str, Any]:
    """
    Check material data availability and integrity.

    Returns:
        Dictionary with material data status
    """
    results = {
        "materials_file_status": "unknown",
        "materials_count": 0,
        "sample_materials": [],
        "errors": [],
    }

    try:
        from generators.dynamic_generator import DynamicGenerator

        generator = DynamicGenerator()
        materials = generator.get_available_materials()

        results["materials_file_status"] = "loaded"
        results["materials_count"] = len(materials)
        results["sample_materials"] = materials[:10] if materials else []

    except Exception as e:
        results["materials_file_status"] = "error"
        results["errors"].append(f"Failed to load materials: {e}")

    return results
