#!/usr/bin/env python3
"""
Frontmatter Component Post-Processor

Component-specific post-processing logic for frontmatter components.
"""

import logging
from typing import Any, Dict

import yaml

from .utils import validate_frontmatter_properties_completeness

logger = logging.getLogger(__name__)


def analyze_frontmatter_completeness(content: str) -> Dict[str, Any]:
    """
    Analyze frontmatter content for completeness and structure.

    Args:
        content: The frontmatter content to analyze

    Returns:
        Dictionary with analysis results
    """
    try:
        # Extract YAML content from frontmatter
        if not content.startswith("---"):
            return {"error": "Content does not start with frontmatter markers"}

        yaml_end = content.find("---", 3)
        if yaml_end == -1:
            return {"error": "Frontmatter not properly closed"}

        yaml_content = content[3:yaml_end].strip()
        frontmatter_data = yaml.safe_load(yaml_content)

        if not frontmatter_data:
            return {"error": "Empty frontmatter data"}

        # Get completeness analysis
        completeness = validate_frontmatter_properties_completeness(frontmatter_data)

        # Add additional metrics
        summary = {
            "total_fields": len(frontmatter_data),
            "has_properties": "properties" in frontmatter_data,
            "has_chemical_props": "chemicalProperties" in frontmatter_data,
            "has_category": "category" in frontmatter_data,
            "completeness_score": completeness["completeness"],
            "missing_sections": completeness["missing_sections"],
            "missing_properties": completeness["missing_properties"],
            "recommendations": completeness["recommendations"],
        }

        return summary

    except Exception as e:
        return {"error": f"Analysis failed: {e}"}


def post_process_frontmatter(content: str, material_name: str) -> str:
    """
    Post-process frontmatter content with enhancements and proper formatting.
    
    Ensures clean YAML frontmatter section while preserving version information
    in separate sections as handled by versioning/generator.py.

    Args:
        content: Raw frontmatter content
        material_name: Name of the material

    Returns:
        Enhanced frontmatter content with proper formatting
    """
    try:
        logger.info(f"Post-processing frontmatter for {material_name}")

        # Basic validation
        if not content or not content.strip():
            logger.warning(f"Empty frontmatter content for {material_name}")
            return content

        # Clean up malformed content while preserving intended structure
        lines = content.split('\n')
        cleaned_lines = []
        in_yaml_section = False
        yaml_closed = False
        
        for i, line in enumerate(lines):
            # Handle YAML frontmatter boundaries
            if line.strip() == '---':
                if not in_yaml_section:
                    in_yaml_section = True
                    cleaned_lines.append(line)
                elif in_yaml_section and not yaml_closed:
                    yaml_closed = True
                    cleaned_lines.append(line)
                else:
                    # Additional --- markers (version sections, etc.)
                    cleaned_lines.append(line)
            elif in_yaml_section and not yaml_closed:
                # We're inside the YAML frontmatter
                # Fix common YAML formatting issues
                if line.strip().startswith('description: "') and line.count('"') == 1:
                    # Handle incomplete quoted strings
                    if i + 1 < len(lines) and not lines[i + 1].strip():
                        # If next line is empty, close the quote
                        line = line + '"'
                elif line.strip().startswith('url: "') and line.count('"') == 1:
                    # Handle incomplete URL quotes
                    if i + 1 < len(lines) and not lines[i + 1].strip():
                        line = line + '"'
                cleaned_lines.append(line)
            else:
                # Outside YAML frontmatter (comments, version info, etc.)
                cleaned_lines.append(line)

        # Ensure proper frontmatter structure
        final_content = '\n'.join(cleaned_lines)
        
        # Validate that we have proper frontmatter markers
        if not final_content.startswith("---"):
            final_content = f"---\n{final_content}"
        
        # Count --- markers to ensure proper structure
        marker_count = final_content.count('\n---\n') + (1 if final_content.startswith('---') else 0)
        if marker_count < 2:
            # Find where YAML ends and add closing marker if needed
            lines = final_content.split('\n')
            yaml_end_found = False
            for i, line in enumerate(lines[1:], 1):  # Skip first ---
                if line.strip() == '---':
                    yaml_end_found = True
                    break
                elif line.startswith('#') or 'Version' in line or 'Generated:' in line:
                    # Insert closing --- before version info
                    lines.insert(i, '---')
                    final_content = '\n'.join(lines)
                    yaml_end_found = True
                    break
            
            if not yaml_end_found and not final_content.strip().endswith('---'):
                # Add closing marker at end
                final_content = f"{final_content}\n---"

        logger.info(f"Successfully post-processed frontmatter for {material_name}")
        return final_content

    except Exception as e:
        logger.error(f"Error post-processing frontmatter for {material_name}: {e}")
        return content
