#!/usr/bin/env python3
"""
Centralized Versioning System for Z-Beam Components

Provides unified versioning methods for all component generators.
Handles version stamping, legacy stamp management, and consistent formatting.
Integrates with Global Metadata Delimiting Standard for proper content/metadata separation.
"""

import json
import logging
import platform
import sys
import time
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, List

logger = logging.getLogger(__name__)


class VersioningError(Exception):
    """Raised when versioning operations fail."""
    pass


class VersionGenerator:
    """
    Centralized versioning generator for all Z-Beam components.

    Provides consistent version stamping, legacy stamp management,
    and unified versioning format across all components.
    Integrates with Global Metadata Delimiting Standard when enabled.
    """

    def _load_delimiter_config(self):
        """Load Global Metadata Delimiting configuration."""
        try:
            config_path = Path("config/metadata_delimiting.yaml")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.delimiter_config = yaml.safe_load(f)
                logger.debug("Loaded Global Metadata Delimiting configuration")
            else:
                logger.warning(f"Delimiter config not found: {config_path}")
                self.delimiter_config = None
        except Exception as e:
            logger.error(f"Failed to load delimiter config: {e}")
            self.delimiter_config = None

    def _should_use_delimited_format(self) -> bool:
        """Check if delimited format should be used for output."""
        # Always return False to disable HTML comment delimiters
        return False

    def _get_delimiters(self) -> Dict[str, str]:
        """Get delimiter markers from configuration."""
        if not self.delimiter_config:
            return {}
        
        try:
            return self.delimiter_config.get('metadata_delimiting', {}).get('delimiters', {
                'content_start': '',
                'content_end': '',
                'metadata_start': '',
                'metadata_end': ''
            })
        except Exception as e:
            logger.warning(f"Error getting delimiters: {e}")
            return {
                'content_start': '',
                'content_end': '',
                'metadata_start': '',
                'metadata_end': ''
            }

    def __init__(self):
        """Initialize the version generator."""
        self.generator_version = "1.0.0"
        self.system_info = self._get_system_info()
        self.delimiter_config = None
        self._load_delimiter_config()

    def _get_system_info(self) -> Dict[str, str]:
        """Get system information for version stamps."""
        return {
            "platform": platform.system(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "timestamp": datetime.now().isoformat(),
        }

    def generate_version_stamp(
        self,
        component_name: str,
        component_version: str,
        material_name: str,
        author_name: Optional[str] = None,
        operation: str = "generation",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate a standardized version stamp for component output.

        Args:
            component_name: Name of the component (e.g., 'frontmatter', 'text')
            component_version: Version of the component
            material_name: Name of the material being processed
            author_name: Name of the author (optional)
            operation: Type of operation (default: 'generation')
            metadata: Additional metadata to include

        Returns:
            Formatted version stamp string
        """
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

        stamp_data = {
            "version_log": f"Generated: {timestamp}",
            "material": material_name,
            "component": component_name,
            "generator": f"Z-Beam v{self.generator_version}",
            "component_version": component_version,
            "author": author_name or "AI Assistant",
            "platform": self.system_info["platform"],
            "python_version": self.system_info["python_version"],
            "operation": operation,
        }

        if metadata:
            stamp_data.update(metadata)

        # Format as YAML block with consistent structure
        stamp_lines = [
            "---",
            f"Version Log - {stamp_data['version_log']}",
            f"Material: {stamp_data['material']}",
            f"Component: {stamp_data['component']}",
            f"Generator: {stamp_data['generator']}",
            f"Component Version: {stamp_data['component_version']}",
            f"Author: {stamp_data['author']}",
            f"Platform: {stamp_data['platform']} ({stamp_data['python_version']})",
            f"Operation: {stamp_data['operation']}",
        ]

        # Add metadata if provided
        if metadata:
            for key, value in metadata.items():
                if key not in ['version_log', 'material', 'component', 'generator',
                              'component_version', 'author', 'platform', 'python_version', 'operation']:
                    stamp_lines.append(f"{key.replace('_', ' ').title()}: {value}")

        stamp_lines.append("---")

        return "\n".join(stamp_lines)

    def append_version_stamp(
        self,
        content: str,
        new_stamp: str,
        legacy_marker: str = "Version Log - Generated:"
    ) -> str:
        """
        Append a new version stamp to content, preserving any existing legacy stamps.

        Args:
            content: The content to stamp
            new_stamp: The new version stamp to append
            legacy_marker: Marker to identify existing legacy stamps

        Returns:
            Content with new stamp appended and legacy stamps preserved
        """
        lines = content.split('\n')
        legacy_stamp_start = -1
        legacy_stamp_end = -1

        # Find existing legacy stamp
        for i, line in enumerate(lines):
            if legacy_marker in line:
                legacy_stamp_start = i
                # Find the end of the legacy stamp (next --- marker)
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() == '---':
                        legacy_stamp_end = j
                        break
                break

        if legacy_stamp_start >= 0 and legacy_stamp_end >= 0:
            # Extract legacy stamp
            legacy_stamp = '\n'.join(lines[legacy_stamp_start:legacy_stamp_end + 1])

            # Remove legacy stamp from content
            content_without_legacy = (
                '\n'.join(lines[:legacy_stamp_start]) +
                '\n'.join(lines[legacy_stamp_end + 1:])
            ).strip()

            # Append new stamp and legacy stamp at the END
            return f"{content_without_legacy}\n\n{new_stamp}\n\n{legacy_stamp}"
        else:
            # No legacy stamp found, just append new stamp at the END
            return f"{content}\n\n{new_stamp}"

    def stamp_component_output(
        self,
        content: str,
        component_name: str,
        component_version: str,
        material_name: str,
        author_name: Optional[str] = None,
        operation: str = "generation",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Stamp component output with version information.

        Integrates with Global Metadata Delimiting Standard when enabled.
        For frontmatter components, adds version info as YAML comments.
        For other components, uses standard version stamping with optional delimited format.

        Args:
            content: The component output content
            component_name: Name of the component
            component_version: Version of the component
            material_name: Name of the material
            author_name: Name of the author (optional)
            operation: Type of operation
            metadata: Additional metadata

        Returns:
            Content with version stamp applied, optionally with delimited format
        """
        try:
            # Special handling for frontmatter - add version info as YAML comments
            if component_name == "frontmatter":
                return self.stamp_frontmatter_output(
                    content=content,
                    component_name=component_name,
                    component_version=component_version,
                    material_name=material_name,
                    author_name=author_name,
                    operation=operation,
                    metadata=metadata,
                )
            
            # Check if we should use delimited format
            if self._should_use_delimited_format():
                return self._stamp_with_delimited_format(
                    content=content,
                    component_name=component_name,
                    component_version=component_version,
                    material_name=material_name,
                    author_name=author_name,
                    operation=operation,
                    metadata=metadata,
                )
            
            # Standard handling for other components (legacy format)
            # Generate new version stamp
            new_stamp = self.generate_version_stamp(
                component_name=component_name,
                component_version=component_version,
                material_name=material_name,
                author_name=author_name,
                operation=operation,
                metadata=metadata,
            )

            # Apply stamp (will handle legacy stamps automatically)
            stamped_content = self.append_version_stamp(content, new_stamp)

            logger.info(f"Applied version stamp to {component_name} for {material_name}")
            return stamped_content

        except Exception as e:
            logger.error(f"Failed to stamp {component_name} output: {e}")
            # Return original content if stamping fails
            return content

    def _stamp_with_delimited_format(
        self,
        content: str,
        component_name: str,
        component_version: str,
        material_name: str,
        author_name: Optional[str] = None,
        operation: str = "generation",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Apply version stamping using Global Metadata Delimiting Standard format.
        
        Separates content and metadata with proper delimiters.
        """
        try:
            # Get delimiter markers
            delimiters = self._get_delimiters()
            
            # Extract existing content if already delimited
            existing_content = self._extract_content_from_delimited(content)
            if not existing_content:
                # Use full content if no delimiters found
                existing_content = self._clean_content_for_delimiting(content)
            
            # Generate metadata section
            metadata_section = self._generate_metadata_section(
                component_name=component_name,
                component_version=component_version,
                material_name=material_name,
                author_name=author_name,
                operation=operation,
                metadata=metadata,
                original_content=content
            )
            
            # Format with delimiters (clean format without HTML comments)
            parts = []
            if delimiters['content_start']:
                parts.append(delimiters['content_start'])
            parts.append(existing_content)
            if delimiters['content_end']:
                parts.append(delimiters['content_end'])
            if delimiters['metadata_start']:
                parts.append(delimiters['metadata_start'])
            parts.append(metadata_section)
            if delimiters['metadata_end']:
                parts.append(delimiters['metadata_end'])
            
            delimited_content = '\n'.join(filter(None, parts))
            
            logger.info(f"Applied delimited format to {component_name} for {material_name}")
            return delimited_content
            
        except Exception as e:
            logger.error(f"Failed to apply delimited format: {e}")
            # Fallback to legacy format
            return self.stamp_component_output(
                content=content,
                component_name=component_name,
                component_version=component_version,
                material_name=material_name,
                author_name=author_name,
                operation=operation,
                metadata=metadata
            )

    def _extract_content_from_delimited(self, content: str) -> Optional[str]:
        """Extract content from existing delimited format."""
        delimiters = self._get_delimiters()
        start_marker = delimiters.get('content_start', '<!-- CONTENT START -->')
        end_marker = delimiters.get('content_end', '<!-- CONTENT END -->')
        
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker)
        
        if start_idx >= 0 and end_idx >= 0 and end_idx > start_idx:
            start_idx += len(start_marker)
            return content[start_idx:end_idx].strip()
        
        return None

    def _clean_content_for_delimiting(self, content: str) -> str:
        """Clean content by removing existing metadata for delimiting."""
        lines = content.split('\n')
        cleaned_lines = []
        skip_patterns = [
            'Version Log - Generated:',
            'Material:',
            'Component:',
            'Generator: Z-Beam',
            'Platform: Darwin',
            'author:',
            'material:',
            'component:',
            'generated:',
            'source:'
        ]
        
        in_yaml_block = False
        for line in lines:
            stripped = line.strip()
            
            # Track YAML block boundaries
            if stripped == '---':
                in_yaml_block = not in_yaml_block
                continue
                
            # Skip metadata patterns
            if any(pattern in line for pattern in skip_patterns):
                continue
                
            # Skip YAML frontmatter
            if in_yaml_block:
                continue
                
            # Skip empty lines at start/end
            if not stripped and not cleaned_lines:
                continue
                
            cleaned_lines.append(line)
        
        # Remove trailing empty lines
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
            
        return '\n'.join(cleaned_lines)

    def _generate_metadata_section(
        self,
        component_name: str,
        component_version: str,
        material_name: str,
        author_name: Optional[str] = None,
        operation: str = "generation",
        metadata: Optional[Dict[str, Any]] = None,
        original_content: str = ""
    ) -> str:
        """Generate metadata section for delimited format."""
        # Extract existing metadata from original content
        existing_metadata = self._extract_existing_metadata(original_content)
        
        # Generate new version stamp
        new_stamp = self.generate_version_stamp(
            component_name=component_name,
            component_version=component_version,
            material_name=material_name,
            author_name=author_name,
            operation=operation,
            metadata=metadata,
        )
        
        # Combine existing metadata with new stamp
        metadata_parts = []
        
        if existing_metadata:
            metadata_parts.append(existing_metadata)
            
        metadata_parts.append(new_stamp)
        
        return '\n\n'.join(metadata_parts)

    def _extract_existing_metadata(self, content: str) -> str:
        """Extract existing metadata (YAML frontmatter, version logs) from content."""
        lines = content.split('\n')
        metadata_lines = []
        
        in_yaml = False
        for line in lines:
            stripped = line.strip()
            
            # YAML frontmatter
            if stripped == '---':
                in_yaml = not in_yaml
                metadata_lines.append(line)
                continue
                
            if in_yaml:
                metadata_lines.append(line)
                continue
                
            # Version logs and other metadata
            if any(pattern in line for pattern in [
                'Version Log - Generated:',
                'author:',
                'material:',
                'component:',
                'generated:',
                'source:'
            ]):
                metadata_lines.append(line)
        
        return '\n'.join(metadata_lines).strip() if metadata_lines else ""

    def stamp_frontmatter_output(
        self,
        content: str,
        component_name: str,
        component_version: str,
        material_name: str,
        author_name: Optional[str] = None,
        operation: str = "generation",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Stamp frontmatter output with version information as YAML comments.

        This preserves YAML validity by adding version info as comments within
        the YAML structure rather than creating multiple documents.

        Args:
            content: The frontmatter YAML content
            component_name: Name of the component
            component_version: Version of the component
            material_name: Name of the material
            author_name: Name of the author (optional)
            operation: Type of operation
            metadata: Additional metadata

        Returns:
            Content with version information added as YAML comments
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

            lines = content.split('\n')

            # Find the opening and closing --- markers
            opening_marker_index = -1
            closing_marker_index = -1

            for i, line in enumerate(lines):
                if line.strip() == '---':
                    if opening_marker_index == -1:
                        opening_marker_index = i
                    else:
                        closing_marker_index = i
                        break

            # If we found both markers, add version info at the END of the file
            if opening_marker_index >= 0 and closing_marker_index >= 0:
                # Create version comment block for the END of the file
                version_comments = [
                    "",
                    "# Version Information",
                    f"# Generated: {timestamp}",
                    f"# Material: {material_name}",
                    f"# Component: {component_name}",
                    f"# Generator: Z-Beam v{self.generator_version}",
                    f"# Component Version: {component_version}",
                    f"# Author: {author_name or 'AI Assistant'}",
                    f"# Platform: {self.system_info['platform']} ({self.system_info['python_version']})",
                    f"# Operation: {operation}",
                ]

                # Add metadata as comments if provided
                if metadata:
                    for key, value in metadata.items():
                        if key not in ['version_log', 'material', 'component', 'generator',
                                      'component_version', 'author', 'platform', 'python_version', 'operation']:
                            version_comments.append(f"# {key.replace('_', ' ').title()}: {value}")

                # Keep the original YAML structure and append version info at the END
                new_lines = (
                    lines[:closing_marker_index + 1] +  # Keep entire YAML block including closing ---
                    [""] +                              # Add empty line for separation
                    version_comments                     # Add version comments at the END
                )
                return '\n'.join(new_lines)

            # If no closing marker found, just add comments at the END
            elif opening_marker_index >= 0:
                # Create version comment block for the END
                version_comments = [
                    "",
                    "# Version Information",
                    f"# Generated: {timestamp}",
                    f"# Material: {material_name}",
                    f"# Component: {component_name}",
                    f"# Generator: Z-Beam v{self.generator_version}",
                    f"# Component Version: {component_version}",
                    f"# Author: {author_name or 'AI Assistant'}",
                    f"# Platform: {self.system_info['platform']} ({self.system_info['python_version']})",
                    f"# Operation: {operation}",
                ]

                # Add metadata as comments if provided
                if metadata:
                    for key, value in metadata.items():
                        if key not in ['version_log', 'material', 'component', 'generator',
                                      'component_version', 'author', 'platform', 'python_version', 'operation']:
                            version_comments.append(f"# {key.replace('_', ' ').title()}: {value}")

                # Add version comments at the END of the file
                return content + '\n' + '\n'.join(version_comments)

            # If no markers found, append version comments at the END
            else:
                version_comments = [
                    "",
                    "# Version Information",
                    f"# Generated: {timestamp}",
                    f"# Material: {material_name}",
                    f"# Component: {component_name}",
                    f"# Generator: Z-Beam v{self.generator_version}",
                    f"# Component Version: {component_version}",
                    f"# Author: {author_name or 'AI Assistant'}",
                    f"# Platform: {self.system_info['platform']} ({self.system_info['python_version']})",
                    f"# Operation: {operation}",
                ]

                if metadata:
                    for key, value in metadata.items():
                        version_comments.append(f"# {key.replace('_', ' ').title()}: {value}")

                return content + '\n' + '\n'.join(version_comments)

        except Exception as e:
            logger.error(f"Failed to stamp frontmatter output: {e}")
            # Return original content if stamping fails
            return content

    def validate_version_stamp(self, content: str) -> Dict[str, Any]:
        """
        Validate that content has proper version stamping.

        Args:
            content: Content to validate

        Returns:
            Dictionary with validation results
        """
        validation_result = {
            "has_version_stamp": False,
            "stamp_count": 0,
            "latest_stamp": None,
            "legacy_stamps": [],
            "is_valid": False,
        }

        lines = content.split('\n')
        stamps = []

        # Find all version stamps
        i = 0
        while i < len(lines):
            if "Version Log - Generated:" in lines[i]:
                stamp_start = i
                stamp_end = i
                # Find end of stamp
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() == '---':
                        stamp_end = j
                        break
                if stamp_end > stamp_start:
                    stamps.append('\n'.join(lines[stamp_start:stamp_end + 1]))
                i = stamp_end
            i += 1

        if stamps:
            validation_result["has_version_stamp"] = True
            validation_result["stamp_count"] = len(stamps)
            validation_result["latest_stamp"] = stamps[0]  # First stamp is the latest
            validation_result["legacy_stamps"] = stamps[1:] if len(stamps) > 1 else []
            validation_result["is_valid"] = True

        return validation_result


# Global instance for easy access
_version_generator = None

def get_version_generator() -> VersionGenerator:
    """Get the global version generator instance."""
    global _version_generator
    if _version_generator is None:
        _version_generator = VersionGenerator()
    return _version_generator


def stamp_component_output(
    component_name: str,
    content: str,
) -> str:
    """
    Simple API to stamp component output with version information.

    This is the normalized API that all components should use.
    It automatically extracts metadata from the content and system.

    Args:
        component_name: Name of the component (e.g., 'frontmatter', 'text')
        content: The component output content

    Returns:
        Content with version stamp applied
    """
    generator = get_version_generator()

    # Extract basic metadata from content if possible
    material_name = "Unknown"
    author_name = None

    # Try to extract material name from content
    lines = content.split('\n')
    for line in lines[:20]:  # Check first 20 lines
        if 'material:' in line.lower() or 'Material:' in line:
            # Extract material name
            parts = line.split(':', 1)
            if len(parts) > 1:
                material_name = parts[1].strip()
                break
        elif 'title:' in line.lower() and ('laser' in line.lower() or 'cleaning' in line.lower()):
            # Try to extract from title
            parts = line.split(':', 1)
            if len(parts) > 1:
                title = parts[1].strip()
                # Extract material name from title like "Laser Cleaning of Aluminum"
                if 'Laser Cleaning of' in title:
                    material_name = title.replace('Laser Cleaning of', '').strip()
                    break

    # Try to extract author name from content
    for line in lines[:30]:  # Check first 30 lines
        if 'author:' in line.lower() or 'Author:' in line:
            parts = line.split(':', 1)
            if len(parts) > 1:
                author_name = parts[1].strip()
                break

    # Get component version from a simple mapping
    component_versions = {
        "frontmatter": "4.0.1",
        "text": "3.0.0",
        "author": "2.0.0",
        "badgesymbol": "2.0.0",
        "caption": "1.0.0",
        "propertiestable": "2.0.0",
        "table": "2.0.0",
        "jsonld": "1.0.0",
        "metatags": "1.0.0",
    }

    component_version = component_versions.get(component_name, "1.0.0")

    # Use standard stamping for all components
    return generator.stamp_component_output(
        content=content,
        component_name=component_name,
        component_version=component_version,
        material_name=material_name,
        author_name=author_name,
        operation="generation",
    )


# Legacy full API for backward compatibility
def stamp_component_output_full(
    content: str,
    component_name: str,
    component_version: str,
    material_name: str,
    author_name: Optional[str] = None,
    operation: str = "generation",
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Full API to stamp component output (legacy compatibility).

    Args:
        content: The component output content
        component_name: Name of the component
        component_version: Version of the component
        material_name: Name of the material
        author_name: Name of the author (optional)
        operation: Type of operation
        metadata: Additional metadata

    Returns:
        Content with version stamp applied
    """
    generator = get_version_generator()
    return generator.stamp_component_output(
        content=content,
        component_name=component_name,
        component_version=component_version,
        material_name=material_name,
        author_name=author_name,
        operation=operation,
        metadata=metadata,
    )


if __name__ == "__main__":
    # Test the versioning system
    generator = VersionGenerator()

    # Test version stamp generation
    stamp = generator.generate_version_stamp(
        component_name="test",
        component_version="1.0.0",
        material_name="Steel",
        author_name="Test Author"
    )
    print("Generated Version Stamp:")
    print(stamp)
    print("\n" + "="*50 + "\n")

    # Test stamp prepending
    test_content = "This is test content.\n\n---\nVersion Log - Generated: 2025-01-01T00:00:00.000000\nMaterial: Steel\nComponent: legacy\n---"

    stamped_content = generator.stamp_component_output(
        content=test_content,
        component_name="frontmatter",
        component_version="4.0.1",
        material_name="Steel",
        author_name="Test Author"
    )
    print("Stamped Content with Legacy Preservation:")
    print(stamped_content)
