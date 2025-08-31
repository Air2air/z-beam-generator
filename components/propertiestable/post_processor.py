"""
Properties table component post-processor for content cleanup and enhancement.
"""
import re
import logging

logger = logging.getLogger(__name__)


def post_process_propertiestable(content: str, material_name: str = "") -> str:
    """
    Post-process properties table content for consistency and quality.
    
    Args:
        content: Generated properties table content
        material_name: Name of the material being processed
        
    Returns:
        str: Post-processed properties table content
    """
    if not content or not content.strip():
        return content
    
    lines = content.strip().split('\n')
    processed_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            processed_lines.append('')
            continue
        
        # Clean up table formatting
        if '|' in line:
            line = clean_properties_table_row(line)
        
        processed_lines.append(line)
    
    processed = '\n'.join(processed_lines)
    
    # Material-specific enhancements
    if material_name:
        material_lower = material_name.lower()
        if material_lower in processed.lower() and material_name not in processed:
            processed = re.sub(rf'\b{re.escape(material_lower)}\b', material_name, processed, flags=re.IGNORECASE)
    
    return processed


def clean_properties_table_row(line: str) -> str:
    """Clean individual properties table row."""
    # Split by pipes and clean each cell
    cells = line.split('|')
    cleaned_cells = []
    
    for i, cell in enumerate(cells):
        cell = cell.strip()
        
        if not cell:
            cleaned_cells.append(cell)
            continue
        
        # Skip separator rows (contains only dashes and spaces)
        if re.match(r'^[-\s:]+$', cell):
            cleaned_cells.append(cell)
            continue
        
        # Normalize whitespace
        cell = re.sub(r'\s+', ' ', cell)
        
        # Clean up property names (first column typically)
        if i == 1:  # First actual column (index 0 is empty due to leading |)
            cell = clean_property_name(cell)
        else:
            # Clean property values
            cell = clean_property_value(cell)
        
        cleaned_cells.append(cell)
    
    # Reconstruct the row with proper spacing
    if len(cleaned_cells) > 1:
        return '| ' + ' | '.join(cleaned_cells[1:-1]) + ' |'
    else:
        return line


def clean_property_name(name: str) -> str:
    """Clean property names."""
    # Standard property name formatting
    property_replacements = {
        'melting point': 'Melting Point',
        'boiling point': 'Boiling Point',
        'density': 'Density',
        'thermal conductivity': 'Thermal Conductivity',
        'electrical conductivity': 'Electrical Conductivity',
        'hardness': 'Hardness',
        'tensile strength': 'Tensile Strength',
        'yield strength': 'Yield Strength',
        'elastic modulus': 'Elastic Modulus',
        'absorption coefficient': 'Absorption Coefficient',
        'reflectance': 'Reflectance',
        'surface roughness': 'Surface Roughness'
    }
    
    name_lower = name.lower()
    for old_name, new_name in property_replacements.items():
        if old_name in name_lower:
            return new_name
    
    # Capitalize first letter of each word
    return ' '.join(word.capitalize() for word in name.split())


def clean_property_value(value: str) -> str:
    """Clean property values."""
    # Normalize units and formatting
    unit_replacements = {
        'deg c': '°C',
        'deg f': '°F',
        'degrees c': '°C',
        'degrees f': '°F',
        'celsius': '°C',
        'fahrenheit': '°F',
        'g/cm3': 'g/cm³',
        'kg/m3': 'kg/m³',
        'w/mk': 'W/m·K',
        'w/m*k': 'W/m·K',
        's/m': 'S/m',
        'gpa': 'GPa',
        'mpa': 'MPa',
        'hv': 'HV',
        'μm': 'μm',
        'nm': 'nm',
        'um': 'μm'
    }
    
    for old_unit, new_unit in unit_replacements.items():
        value = re.sub(rf'\b{re.escape(old_unit)}\b', new_unit, value, flags=re.IGNORECASE)
    
    # Clean up number formatting
    value = re.sub(r'(\d+)\s*-\s*(\d+)', r'\1–\2', value)  # Use en dash for ranges
    value = re.sub(r'(\d+)\s*x\s*10\^?(-?\d+)', r'\1×10^\2', value)  # Scientific notation
    
    return value
