#!/usr/bin/env python3
"""
File Operations

Centralized file operations for content generation.
Extracted from run.py to reduce bloat and improve testability.
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

# Import path manager for robust path handling
try:
    from utils.path_manager import PathManager

    _path_manager_available = True
except ImportError:
    _path_manager_available = False


def save_component_to_file(content: str, filepath: str) -> None:
    """
    Save component content to file with directory creation.

    Args:
        content: Content to save
        filepath: Full file path where to save content

    Raises:
        OSError: If file cannot be written
    """
    try:
        # Create directory if it doesn't exist
        file_path = Path(filepath)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write content to file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    except Exception as e:
        raise OSError(f"Failed to save file {filepath}: {e}")


def save_component_to_file_original(
    material: str, component_type: str, content: str
) -> str:
    """
    Save component content using original file naming convention.

    Args:
        material: Material name
        component_type: Component type
        content: Content to save

    Returns:
        Path to saved file

    Raises:
        OSError: If file cannot be written
    """
    # Create safe filename from material name
    safe_material = material.lower().replace(" ", "-").replace("/", "-")
    filename = f"{safe_material}-laser-cleaning.md"

    # Map component types to correct directories
    # Note: "content" component type has been removed - use "text" instead

    # Use path manager if available, otherwise fallback to relative paths
    if _path_manager_available:
        component_dir = PathManager.get_component_output_dir(component_type)
    else:
        # Fallback to relative path
        component_dir = Path("content") / "components" / component_type
        component_dir.mkdir(parents=True, exist_ok=True)

    # Full file path
    filepath = component_dir / filename

    # Add version log to content before saving
    content_with_version = add_version_log_to_content(
        content=content,
        material=material,
        component_type=component_type,
        filepath=str(filepath),
    )

    # Save content
    save_component_to_file(content_with_version, str(filepath))

    # Save version history to separate file
    version_entry = create_version_log_entry(material, component_type, str(filepath))
    # Removed version_history call - relying on MD timestamps

    return str(filepath)


def clean_content_components() -> dict:
    """
    Clean all generated component content files.

    Returns:
        Dictionary with cleanup statistics
    """
    content_dir = Path("content/components")

    if not content_dir.exists():
        return {
            "files_removed": 0,
            "directories_removed": 0,
            "errors": [],
            "message": "No content directory found",
        }

    files_removed = 0
    directories_removed = 0
    errors = []

    try:
        # Remove all component directories and files
        for item in content_dir.iterdir():
            try:
                if item.is_file():
                    item.unlink()
                    files_removed += 1
                elif item.is_dir():
                    shutil.rmtree(item)
                    directories_removed += 1
            except Exception as e:
                errors.append(f"Failed to remove {item}: {e}")

        # Remove the components directory if empty
        try:
            if content_dir.exists() and not any(content_dir.iterdir()):
                content_dir.rmdir()
                directories_removed += 1
        except OSError:
            pass  # Directory not empty, that's ok

    except Exception as e:
        errors.append(f"General cleanup error: {e}")

    return {
        "files_removed": files_removed,
        "directories_removed": directories_removed,
        "errors": errors,
        "message": f"Cleaned {files_removed} files and {directories_removed} directories",
    }


def ensure_output_directory() -> Path:
    """
    Ensure output directory structure exists.

    Returns:
        Path to content directory
    """
    content_dir = Path("content")
    content_dir.mkdir(exist_ok=True)

    components_dir = content_dir / "components"
    components_dir.mkdir(exist_ok=True)

    return content_dir


def get_file_stats(directory: str = "content") -> dict:
    """
    Get statistics about generated files.

    Args:
        directory: Directory to analyze

    Returns:
        Dictionary with file statistics
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        return {
            "total_files": 0,
            "total_size": 0,
            "by_component": {},
            "error": f"Directory {directory} not found",
        }

    stats = {"total_files": 0, "total_size": 0, "by_component": {}, "by_extension": {}}

    try:
        for file_path in dir_path.rglob("*"):
            if file_path.is_file():
                stats["total_files"] += 1
                file_size = file_path.stat().st_size
                stats["total_size"] += file_size

                # Component statistics
                if file_path.parent.name != directory:
                    component = file_path.parent.name
                    if component not in stats["by_component"]:
                        stats["by_component"][component] = {"files": 0, "size": 0}
                    stats["by_component"][component]["files"] += 1
                    stats["by_component"][component]["size"] += file_size

                # Extension statistics
                ext = file_path.suffix
                if ext not in stats["by_extension"]:
                    stats["by_extension"][ext] = {"files": 0, "size": 0}
                stats["by_extension"][ext]["files"] += 1
                stats["by_extension"][ext]["size"] += file_size

    except Exception as e:
        stats["error"] = str(e)

    return stats


def load_component_from_file(material: str, component_type: str) -> Optional[str]:
    """
    Load component content from file.

    Args:
        material: Material name
        component_type: Component type

    Returns:
        Content string if file exists, None otherwise
    """
    # Create safe filename from material name
    safe_material = material.lower().replace(" ", "-").replace("/", "-")
    filename = f"{safe_material}-laser-cleaning.md"

    # Handle legacy "content" component type - raise error since it's been removed
    if component_type == "content":
        raise ValueError("Component type 'content' has been removed. Use 'text' instead.")

    # Construct file path
    component_dir = Path("content") / "components" / component_type
    filepath = component_dir / filename

    # Check if file exists and load content
    if filepath.exists():
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise OSError(f"Failed to load file {filepath}: {e}")

    return None


def add_version_log_to_content(
    content: str, material: str, component_type: str, filepath: str
) -> str:
    """
    Add version log to component content.

    For YAML frontmatter files, add version info as comments to preserve format.
    For other content types, append as footer section.

    Args:
        content: Original content
        material: Material name
        component_type: Component type
        filepath: File path where content will be saved

    Returns:
        Content with version log appended
    """
    # Create version log entry
    version_entry = create_version_log_entry(material, component_type, filepath)

    # Check if content is YAML frontmatter (starts and ends with ---)
    is_yaml_frontmatter = (
        content.strip().startswith('---') and
        content.strip().endswith('---') and
        content.count('---') >= 2
    )

    if is_yaml_frontmatter:
        # For YAML files, add version info as comments at the end (without --- delimiters)
        version_comments = [
            "",
            "# Version Information",
            f"# Generated: {version_entry['timestamp']}",
            f"# Material: {version_entry['material']}",
            f"# Component: {version_entry['component_type']}",
            f"# Generator: Z-Beam v{version_entry['generator_version']}",
            f"# Author: {version_entry['author']}",
            f"# Platform: {version_entry['system_info']['platform']} ({version_entry['system_info']['python_version']})",
            f"# File: {version_entry['filepath']}",
        ]
        return content + "\n" + "\n".join(version_comments)
    else:
        # For other content types, use the original footer format
        version_footer = format_version_log_footer(version_entry)
        return content + "\n\n" + version_footer


def create_version_log_entry(material: str, component_type: str, filepath: str) -> dict:
    """
    Create a version log entry for the component.

    Args:
        material: Material name
        component_type: Component type
        filepath: File path

    Returns:
        Dictionary with version log data
    """
    timestamp = datetime.now().isoformat()

    # Get system information
    try:
        import platform

        system_info = {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
        }
    except Exception:
        system_info = {
            "platform": "unknown",
            "python_version": "unknown",
            "hostname": "unknown",
        }

    # Get generation context
    generation_context = {
        "material": material,
        "component_type": component_type,
        "filepath": filepath,
        "timestamp": timestamp,
        "generator_version": "2.1.0",  # Update as needed
        "system_info": system_info,
    }

    # Try to get author information from environment or context
    try:
        # This would be passed from the generation context
        author_info = os.environ.get("z-beam_AUTHOR", "AI Assistant")
        generation_context["author"] = author_info
    except Exception:
        generation_context["author"] = "AI Assistant"

    return generation_context


def format_version_log_footer(version_entry: dict) -> str:
    """
    Format version log entry as a standardized footer.

    Args:
        version_entry: Version log data dictionary

    Returns:
        Formatted footer string
    """
    footer_lines = [
        "---",
        f"Version Log - Generated: {version_entry['timestamp']}",
        f"Material: {version_entry['material']}",
        f"Component: {version_entry['component_type']}",
        f"Generator: Z-Beam v{version_entry['generator_version']}",
        f"Author: {version_entry['author']}",
        f"Platform: {version_entry['system_info']['platform']} ({version_entry['system_info']['python_version']})",
        f"File: {version_entry['filepath']}",
        "---",
    ]

    return "\n".join(footer_lines)


def save_version_history(
    material: str, component_type: str, version_entry: dict
) -> None:
    """
    DEPRECATED: Version history tracking removed - relying on MD file timestamps.
    Kept for backward compatibility.
    """
    pass


