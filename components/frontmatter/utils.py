#!/usr/bin/env python3
"""
Frontmatter Component Utilities

Component-specific utility functions for frontmatter generation and enhancement.
"""

import yaml
from pathlib import Path
from typing import Dict, Any
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import our percentile calculator
try:
    from utils.percentile_calculator import calculate_property_percentiles
except ImportError:
    # Fallback if percentile calculator not available
    def calculate_property_percentiles(category: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        return properties

logger = logging.getLogger(__name__)


def load_category_ranges() -> Dict[str, Any]:
    """
    Load category ranges from data/category_ranges.yaml
    
    Returns:
        Dictionary containing category range data for all material categories
    """
    try:
        ranges_path = Path("data/category_ranges.yaml")
        if not ranges_path.exists():
            logger.warning(f"Category ranges file not found: {ranges_path}")
            return {}
        
        with open(ranges_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Return the 'categories' section which contains the actual range data
        return data.get('categories', {})
        
    except Exception as e:
        logger.error(f"Error loading category ranges: {e}")
        return {}


def enhance_frontmatter_with_context(frontmatter_data: Dict[str, Any], category: str) -> Dict[str, Any]:
    """
    Enhance frontmatter properties with min/max context and percentile calculations.
    
    Args:
        frontmatter_data: The frontmatter dictionary to enhance
        category: Material category for context
        
    Returns:
        Enhanced frontmatter dictionary with min/max values and percentiles
    """
    if not frontmatter_data or not category:
        return frontmatter_data
    
    try:
        # Load category ranges
        category_ranges = load_category_ranges()
        if not category_ranges or category not in category_ranges:
            logger.warning(f"No category ranges found for: {category}")
            return frontmatter_data
        
        # Get properties section
        properties = frontmatter_data.get('properties', {})
        if not properties:
            return frontmatter_data
        
        # Calculate percentiles and add min/max context
        enhanced_properties = calculate_property_percentiles(category, properties)
        
        # Update the frontmatter data
        enhanced_frontmatter = frontmatter_data.copy()
        enhanced_frontmatter['properties'] = enhanced_properties
        
        return enhanced_frontmatter
        
    except Exception as e:
        logger.error(f"Error enhancing frontmatter: {e}")
        return frontmatter_data


def enhance_generated_frontmatter(content: str, category: str) -> str:
    """
    Enhance frontmatter content with property context and percentile calculations.
    
    Args:
        content: Raw frontmatter content string
        category: Material category for enhancement
        
    Returns:
        Enhanced frontmatter content string
    """
    try:
        # Parse YAML frontmatter
        if not content.startswith('---'):
            return content
        
        yaml_end = content.find('---', 3)
        if yaml_end == -1:
            return content
        
        yaml_content = content[3:yaml_end].strip()
        remaining_content = content[yaml_end:]
        
        # Load and enhance the YAML
        frontmatter_data = yaml.safe_load(yaml_content)
        if not frontmatter_data:
            return content
        
        enhanced_data = enhance_frontmatter_with_context(frontmatter_data, category)
        
        # Convert back to YAML string
        enhanced_yaml = yaml.dump(enhanced_data, default_flow_style=False, sort_keys=False)
        
        return f"---\n{enhanced_yaml}{remaining_content}"
        
    except Exception as e:
        logger.error(f"Error enhancing generated frontmatter: {e}")
        return content


def validate_frontmatter_properties_completeness(frontmatter_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and report on frontmatter properties completeness.
    
    Args:
        frontmatter_data: The frontmatter dictionary to validate
        
    Returns:
        Dictionary with completeness metrics and recommendations
    """
    if not frontmatter_data:
        return {"completeness": 0.0, "missing": [], "recommendations": ["Add frontmatter data"]}
    
    # Essential properties for laser cleaning applications
    essential_properties = [
        'density', 'meltingPoint', 'thermalConductivity', 
        'tensileStrength', 'hardness', 'youngsModulus'
    ]
    
    essential_sections = [
        'category', 'chemicalProperties', 'properties', 'name'
    ]
    
    results = {
        "completeness": 0.0,
        "missing_sections": [],
        "missing_properties": [],
        "recommendations": []
    }
    
    # Check essential sections
    missing_sections = [section for section in essential_sections if section not in frontmatter_data]
    results["missing_sections"] = missing_sections
    
    # Check essential properties
    properties = frontmatter_data.get('properties', {})
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
