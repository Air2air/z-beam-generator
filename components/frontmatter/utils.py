#!/usr/bin/env python3
"""
Frontmatter Component Utilities

Focused utility functions for frontmatter generation and validation.
"""

import yaml
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def load_category_ranges() -> Dict[str, Any]:
    """
    Load category ranges from data/category_ranges.yaml
    
    Returns:
        Dictionary containing category range data for all material categories
    """
    ranges_path = Path("data/category_ranges.yaml")
    
    with open(ranges_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    return data['categories']  # Must exist, no fallback


def validate_frontmatter_properties_completeness(frontmatter_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate completeness of frontmatter properties and sections.
    
    Args:
        frontmatter_data: The frontmatter data dictionary to validate
        
    Returns:
        Dictionary with completeness analysis
    """
    essential_sections = ['properties', 'chemicalProperties', 'category']
    essential_properties = ['density', 'meltingPoint', 'thermalConductivity']
    
    results = {
        "completeness": 0.0,
        "missing_sections": [],
        "missing_properties": [],
        "recommendations": []
    }
    
    if not frontmatter_data:
        results["recommendations"].append("Add frontmatter data")
        return results
    
    # Check essential sections
    missing_sections = [section for section in essential_sections if section not in frontmatter_data]
    results["missing_sections"] = missing_sections
    
    # Check essential properties
    properties = frontmatter_data['properties']  # Must exist, no fallback
    missing_properties = [prop for prop in essential_properties if prop not in properties]
    results["missing_properties"] = missing_properties
    
    # Calculate completeness score
    total_essential = len(essential_sections) + len(essential_properties)
    missing_total = len(missing_sections) + len(missing_properties)
    results["completeness"] = max(0.0, (total_essential - missing_total) / total_essential)
    
    # Generate recommendations
    if missing_sections:
        results["recommendations"].append(f"Add missing sections: {', '.join(missing_sections)}")
    if missing_properties:
        results["recommendations"].append(f"Add missing properties: {', '.join(missing_properties)}")
    
    if results["completeness"] > 0.8:
        results["recommendations"].append("Frontmatter is well-structured")
    elif results["completeness"] > 0.6:
        results["recommendations"].append("Consider adding more technical properties")
    else:
        results["recommendations"].append("Significant enhancement needed for comprehensive coverage")
    
    return results
