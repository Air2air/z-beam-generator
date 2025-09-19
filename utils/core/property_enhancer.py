"""
Property enhancement utilities for Z-Beam dynamic generation.
Enhances frontmatter properties with min/max context and percentile calculations.
"""

import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our percentile calculator
from utils.core.percentile_calculator import calculate_property_percentiles

logger = logging.getLogger(__name__)


def extract_numeric_and_unit(value_str: str) -> tuple[float, str]:
    """
    Extract numeric value and unit from a property string.
    
    Args:
        value_str: Property string like "2.70 g/cm³" or "385 MPa"
        
    Returns:
        Tuple of (numeric_value, unit)
        
    Examples:
        "2.70 g/cm³" -> (2.70, "g/cm³")
        "385 MPa" -> (385.0, "MPa")
        "1668°C" -> (1668.0, "°C")
    """
    if not value_str:
        return 0.0, ""
    
    # Handle range values by taking the midpoint
    if '-' in value_str and not value_str.startswith('-'):  # Avoid negative numbers
        # Split on dash and take midpoint
        parts = value_str.split('-')
        if len(parts) == 2:
            try:
                # Extract numbers from both parts
                import re
                num1_match = re.search(r'[\d.]+', parts[0].strip())
                num2_match = re.search(r'[\d.]+', parts[1].strip())
                
                if num1_match and num2_match:
                    num1 = float(num1_match.group())
                    num2 = float(num2_match.group())
                    midpoint = (num1 + num2) / 2
                    
                    # Extract unit from second part
                    unit_match = re.search(r'[a-zA-Z°/³²]+', parts[1].strip())
                    unit = unit_match.group() if unit_match else ""
                    
                    return midpoint, unit
            except (ValueError, AttributeError):
                pass
    
    # Extract single value
    import re
    try:
        # Find first number (including decimals)
        num_match = re.search(r'[\d.]+', value_str)
        if num_match:
            numeric_value = float(num_match.group())
            
            # Extract unit (everything after the number)
            unit_match = re.search(r'[a-zA-Z°/³²]+', value_str)
            unit = unit_match.group() if unit_match else ""
            
            return numeric_value, unit
    except (ValueError, AttributeError):
        pass
    
    return 0.0, ""


def add_triple_format_fields(properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add numeric and unit fields for triple format compatibility.
    
    For each property like "density": "2.70 g/cm³", adds:
    - "densityNumeric": 2.70
    - "densityUnit": "g/cm³"
    """
    # Properties that need triple format
    triple_properties = {
        "density": ("densityNumeric", "densityUnit"),
        "meltingPoint": ("meltingPointNumeric", "meltingPointUnit"),
        "thermalConductivity": ("thermalConductivityNumeric", "thermalConductivityUnit"),
        "tensileStrength": ("tensileStrengthNumeric", "tensileStrengthUnit"),
        "hardness": ("hardnessNumeric", "hardnessUnit"),
        "youngsModulus": ("youngsModulusNumeric", "youngsModulusUnit"),
    }
    
    for prop_key, (numeric_key, unit_key) in triple_properties.items():
        if prop_key in properties:
            value_str = str(properties[prop_key])
            numeric_value, unit = extract_numeric_and_unit(value_str)
            
            # Add numeric and unit fields
            properties[numeric_key] = numeric_value
            properties[unit_key] = unit
            
            logger.debug(f"Added triple format for {prop_key}: {value_str} -> {numeric_value} {unit}")
    
    return properties


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

        with open(ranges_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Return the 'categories' section which contains the actual range data
        return data.get("categories", {})

    except Exception as e:
        logger.error(f"Error loading category ranges: {e}")
        return {}


def enhance_frontmatter_with_context(
    frontmatter_data: Dict[str, Any], category: str
) -> Dict[str, Any]:
    """
    Enhance frontmatter properties with min/max context and percentile calculations.

    Args:
        frontmatter_data: The frontmatter dictionary to enhance
        category: Material category (e.g., 'metal', 'ceramic', 'wood')

    Returns:
        Enhanced frontmatter dictionary with min/max ranges and percentiles
    """
    if not frontmatter_data or not category:
        return frontmatter_data

    # Load category ranges
    category_ranges = load_category_ranges()
    if not category_ranges or category not in category_ranges:
        logger.warning(f"No category ranges found for: {category}")
        return frontmatter_data

    # Get category ranges for this specific category
    ranges = category_ranges[category]

    # Enhance properties section
    properties = frontmatter_data.get("properties", {})
    if not properties:
        logger.warning("No properties section found in frontmatter")
        return frontmatter_data

    # Map of property names to range data keys
    property_mappings = {
        # Original 6 properties
        "density": "density",
        "meltingPoint": "meltingPoint",
        "thermalConductivity": "thermalConductivity",
        "tensileStrength": "tensileStrength",
        "hardness": "hardness",
        "youngsModulus": "youngsModulus",
        # Phase 1 & 2: Laser-specific and thermal properties
        "laserAbsorption": "laserAbsorption",
        "laserReflectivity": "laserReflectivity",
        "thermalDiffusivity": "thermalDiffusivity",
        "thermalExpansion": "thermalExpansion",
        "specificHeat": "specificHeat",
    }

    # Add min/max values from category ranges
    for prop_key, range_key in property_mappings.items():
        if range_key in ranges:
            range_data = ranges[range_key]

            # Add min/max values with appropriate key names
            if prop_key == "density":
                properties["densityMin"] = range_data.get("min", "")
                properties["densityMax"] = range_data.get("max", "")
            elif prop_key == "meltingPoint":
                properties["meltingMin"] = range_data.get("min", "")
                properties["meltingMax"] = range_data.get("max", "")
            elif prop_key == "thermalConductivity":
                properties["thermalMin"] = range_data.get("min", "")
                properties["thermalMax"] = range_data.get("max", "")
            elif prop_key == "tensileStrength":
                properties["tensileMin"] = range_data.get("min", "")
                properties["tensileMax"] = range_data.get("max", "")
            elif prop_key == "hardness":
                properties["hardnessMin"] = range_data.get("min", "")
                properties["hardnessMax"] = range_data.get("max", "")
            elif prop_key == "youngsModulus":
                properties["modulusMin"] = range_data.get("min", "")
                properties["modulusMax"] = range_data.get("max", "")
            elif prop_key == "laserAbsorption":
                properties["laserAbsorptionMin"] = range_data.get("min", "")
                properties["laserAbsorptionMax"] = range_data.get("max", "")
            elif prop_key == "laserReflectivity":
                properties["laserReflectivityMin"] = range_data.get("min", "")
                properties["laserReflectivityMax"] = range_data.get("max", "")
            elif prop_key == "thermalDiffusivity":
                properties["thermalDiffusivityMin"] = range_data.get("min", "")
                properties["thermalDiffusivityMax"] = range_data.get("max", "")
            elif prop_key == "thermalExpansion":
                properties["thermalExpansionMin"] = range_data.get("min", "")
                properties["thermalExpansionMax"] = range_data.get("max", "")
            elif prop_key == "specificHeat":
                properties["specificHeatMin"] = range_data.get("min", "")
                properties["specificHeatMax"] = range_data.get("max", "")

    # Calculate percentiles for all properties
    properties = calculate_property_percentiles(properties, category_ranges, category)

    # Add triple format fields (numeric and unit) for component compatibility
    properties = add_triple_format_fields(properties)

    # Update the frontmatter with enhanced properties
    frontmatter_data["properties"] = properties

    logger.info(
        f"Enhanced frontmatter for {category} category with min/max context, percentiles, and triple format fields"
    )
    return frontmatter_data


def enhance_generated_frontmatter(content: str, category: str) -> str:
    """
    Enhance generated frontmatter content with min/max context and percentiles.

    Args:
        content: Raw frontmatter content (YAML between --- markers or wrapped in markdown code blocks)
        category: Material category

    Returns:
        Enhanced frontmatter content with added context
    """
    try:
        yaml_content = None
        
        # Handle content wrapped in markdown code blocks (common AI response format)
        if content.strip().startswith("````markdown") or content.strip().startswith("```yaml"):
            # Extract YAML from markdown code blocks
            lines = content.strip().split('\n')
            yaml_lines = []
            in_yaml = False
            
            for line in lines:
                if line.strip().startswith("```yaml"):
                    in_yaml = True
                    continue
                elif line.strip().startswith("```") and in_yaml:
                    break
                elif in_yaml:
                    yaml_lines.append(line)
            
            if yaml_lines:
                yaml_content = '\n'.join(yaml_lines)
        
        # Handle standard frontmatter format
        elif content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 2:
                yaml_content = parts[1].strip()
                # Extract body content if it exists
                body_content = parts[2] if len(parts) > 2 else ""
        
        # If we extracted YAML content, validate and process it
        if yaml_content:
            # First, validate that the YAML is complete and parseable
            try:
                frontmatter_data = yaml.safe_load(yaml_content)
                if not frontmatter_data:
                    logger.warning("YAML content is empty or invalid")
                    return content
            except yaml.YAMLError as e:
                logger.error(f"YAML parsing failed, returning original content: {e}")
                return content

            # Enhance with context
            enhanced_data = enhance_frontmatter_with_context(
                frontmatter_data, category
            )

            # Convert back to YAML with proper frontmatter format
            enhanced_yaml = yaml.dump(
                enhanced_data,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            )

            # Always return in proper frontmatter format
            result = f"---\n{enhanced_yaml}---"
            
            # Append body content if it exists
            if 'body_content' in locals() and body_content:
                result += body_content
                
            return result

        # If we couldn't extract valid YAML, return original content
        logger.warning("Could not extract valid YAML content from response")
        return content

    except Exception as e:
        logger.error(f"Error enhancing frontmatter content: {e}")
        return content


# Test the enhancement if run directly
if __name__ == "__main__":
    # Test loading category ranges
    print("Testing category ranges loading:")
    ranges = load_category_ranges()
    print(f"Loaded {len(ranges)} categories: {list(ranges.keys())}")

    # Test enhancement with sample data
    print("\nTesting frontmatter enhancement:")
    sample_frontmatter = {
        "name": "Steel",
        "category": "metal",
        "properties": {
            "density": "7.85 g/cm³",
            "meltingPoint": "1500°C",
            "thermalConductivity": "50 W/m·K",
            "tensileStrength": "400 MPa",
            "hardness": "150 HV",
            "youngsModulus": "200 GPa",
            "laserAbsorption": "10 cm⁻¹",
            "laserReflectivity": "20%",
            "thermalDiffusivity": "15 mm²/s",
            "thermalExpansion": "12 µm/m·K",
            "specificHeat": "0.46 J/g·K",
        },
    }

    enhanced = enhance_frontmatter_with_context(sample_frontmatter, "metal")

    print("Enhanced properties:")
    props = enhanced.get("properties", {})
    for key, value in props.items():
        if "Percentile" in key:
            print(f"  {key}: {value}%")

    print("\nEnhancement complete!")
