#!/usr/bin/env python3
"""
Frontmatter Loader

Utility for loading and parsing frontmatter data from saved files.
"""

import logging
import re
from pathlib import Path
from typing import Dict, Optional

import yaml

logger = logging.getLogger(__name__)

def load_frontmatter_data(material_name: str) -> Optional[Dict]:
    """
    Load frontmatter data from saved file for dependent components.
    
    Args:
        material_name: Name of the material
        
    Returns:
        Dictionary containing parsed frontmatter data or None if not found/parsable
    """
    # Create safe filename from material name
    safe_material = material_name.lower().replace(" ", "-").replace("/", "-")
    
    # Try new frontmatter system first (YAML format)
    yaml_filename = f"{safe_material}.yaml"
    frontmatter_dir = Path("frontmatter") / "materials"
    yaml_filepath = frontmatter_dir / yaml_filename
    
    if yaml_filepath.exists():
        try:
            with open(yaml_filepath, "r", encoding="utf-8") as f:
                frontmatter_data = yaml.safe_load(f)
                if frontmatter_data:
                    logger.info(f"Successfully loaded frontmatter data for {material_name} from new system (YAML)")
                    return frontmatter_data
        except Exception as e:
            logger.warning(f"Failed to load from new system: {e}")
    
    # Fallback to old frontmatter system (MD format)
    md_filename = f"{safe_material}-laser-cleaning.md"
    old_frontmatter_dir = Path("content") / "components" / "frontmatter"
    filepath = old_frontmatter_dir / md_filename
    
    # Check if frontmatter file exists
    if not filepath.exists():
        logger.warning(f"Frontmatter file not found for {material_name}: {filepath}")
        return None
    
    # No more special handling for Oak file since the files are now standardized
    
    # Load and parse frontmatter
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
        
        # Debug: Print content details
        logger.debug(f"Loaded frontmatter file with {len(content)} bytes")
        logger.debug(f"First 20 chars: {repr(content[:20])}")
        
        # Specific format check: If content starts with ```yaml, it's in fenced code block format
        if content.startswith("```yaml"):
            # Extract content between code fence markers
            end_marker = content.find("```", 7)  # Find closing code fence after the opening one
            if end_marker != -1:
                yaml_content = content[7:end_marker].strip()
                try:
                    frontmatter_data = yaml.safe_load(yaml_content)
                    if frontmatter_data:
                        logger.info(f"Successfully loaded frontmatter data for {material_name} (code block format)")
                        return frontmatter_data
                except Exception as yaml_err:
                    logger.error(f"Failed to parse YAML in code block: {yaml_err}")
        
        # Format 1: Standard YAML between --- markers
        if content.startswith("---"):
            end_marker = content.find("---", 3)
            if end_marker != -1:
                yaml_content = content[3:end_marker].strip()
                frontmatter_data = yaml.safe_load(yaml_content)
                logger.info(f"Successfully loaded frontmatter data for {material_name} (standard format)")
                return frontmatter_data
            
        # Format 3: Try to parse the entire file as YAML (fallback)
        try:
            # If the file contains markdown after the YAML, this will fail, but worth trying
            frontmatter_data = yaml.safe_load(content)
            if isinstance(frontmatter_data, dict):
                logger.info(f"Successfully loaded frontmatter data for {material_name} (entire file as YAML)")
                return frontmatter_data
        except Exception as yaml_err:
            logger.debug(f"Failed to parse entire file as YAML: {yaml_err}")
            
        # One more attempt: Try to extract just the YAML portion by looking for the first non-YAML line
        # This is a heuristic and may not always work
        try:
            lines = content.split('\n')
            yaml_lines = []
            for line in lines:
                stripped = line.strip()
                # Skip code fence markers
                if stripped in ('```yaml', '```'):
                    continue
                # If we hit a line that's clearly not YAML, stop
                if stripped and not re.match(r'^[\w\-]+:|\s*-\s+|\s+\w+:', stripped):
                    break
                yaml_lines.append(line)
            
            # Try to parse what we've collected
            if yaml_lines:
                yaml_content = '\n'.join(yaml_lines)
                frontmatter_data = yaml.safe_load(yaml_content)
                if frontmatter_data and isinstance(frontmatter_data, dict):
                    logger.info(f"Successfully loaded frontmatter data for {material_name} (partial YAML extraction)")
                    return frontmatter_data
        except Exception as yaml_err:
            logger.debug(f"Failed to parse partial YAML: {yaml_err}")
            
        logger.warning(f"Invalid frontmatter format for {material_name}: Could not determine format")
            
    except Exception as e:
        logger.error(f"Failed to load/parse frontmatter for {material_name}: {e}")
        
    return None
