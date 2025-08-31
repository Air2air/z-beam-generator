"""
Content component mock generator for testing and development.
"""
import random
import logging

logger = logging.getLogger(__name__)


def generate_mock_content(material_name: str = "", category: str = "") -> str:
    """
    Generate mock content for testing.
    
    Args:
        material_name: Name of the material
        category: Material category
        
    Returns:
        str: Mock content
    """
    # Use provided material name or generate one
    if not material_name:
        materials_by_category = {
            "metals": ["Steel", "Aluminum", "Copper", "Titanium", "Stainless Steel"],
            "ceramics": ["Alumina", "Zirconia", "Silicon Carbide", "Advanced Ceramic"],
            "composites": ["Carbon Fiber", "Fiberglass", "Composite Panel"],
            "stones": ["Marble", "Granite", "Limestone", "Sandstone"],
            "default": ["Industrial Component", "Metal Alloy", "Advanced Material"]
        }
        materials = materials_by_category.get(category.lower(), materials_by_category["default"])
        material_name = random.choice(materials)
    
    # Generate introduction
    intro_templates = [
        f"Laser cleaning of {material_name} represents a cutting-edge approach to surface treatment and restoration.",
        f"The application of laser technology for {material_name} surface preparation offers unprecedented precision and control.",
        f"Advanced laser cleaning techniques for {material_name} provide superior results compared to traditional methods.",
        f"{material_name} laser cleaning has emerged as the preferred method for precision surface treatment in industrial applications."
    ]
    
    # Generate technical overview
    technical_templates = [
        f"When applied to {material_name}, laser cleaning utilizes precisely controlled photon energy to selectively remove surface contaminants while preserving the underlying substrate integrity.",
        f"The interaction between laser radiation and {material_name} surfaces creates controlled thermal effects that efficiently remove unwanted materials without damaging the base component.",
        f"Laser parameters are carefully optimized for {material_name} to achieve maximum cleaning efficiency while maintaining strict quality control standards.",
        f"The non-contact nature of laser cleaning makes it particularly suitable for {material_name} components that require precise dimensional tolerances."
    ]
    
    # Generate applications
    application_templates = [
        f"Industrial applications of {material_name} laser cleaning include surface preparation for coating, restoration of aged components, and removal of manufacturing residues.",
        f"Quality control processes for {material_name} often rely on laser cleaning to achieve consistent surface conditions required for subsequent processing steps.",
        f"Maintenance and refurbishment of {material_name} equipment benefit significantly from the precision and selectivity of laser cleaning technology.",
        f"Research and development activities involving {material_name} frequently utilize laser cleaning for sample preparation and surface analysis."
    ]
    
    # Generate advantages
    advantage_templates = [
        f"The primary advantages of laser cleaning for {material_name} include environmental friendliness, precision control, and minimal waste generation.",
        f"Compared to chemical or mechanical cleaning methods, laser treatment of {material_name} offers superior repeatability and consistency.",
        f"Cost-effectiveness and reduced downtime make laser cleaning an attractive option for {material_name} processing facilities.",
        f"The versatility of laser cleaning allows for customized treatment protocols specific to different {material_name} grades and conditions."
    ]
    
    # Select random content from each section
    intro = random.choice(intro_templates)
    technical = random.choice(technical_templates)
    application = random.choice(application_templates)
    advantage = random.choice(advantage_templates)
    
    # Combine into full content
    content = f"""# {material_name} Laser Cleaning

## Overview

{intro}

## Technical Approach

{technical}

## Applications

{application}

## Key Advantages

{advantage}

## Process Parameters

The laser cleaning process for {material_name} requires careful consideration of several critical parameters:

- **Wavelength Selection**: Optimized for {material_name} optical properties
- **Pulse Duration**: Precisely controlled for selective removal
- **Energy Density**: Calibrated to material-specific thresholds
- **Scanning Speed**: Adjusted for uniform treatment coverage
- **Atmospheric Conditions**: Controlled environment for consistent results

## Quality Assurance

Comprehensive quality control measures ensure optimal {material_name} laser cleaning results through real-time monitoring and post-process verification techniques.
"""
    
    return content


def generate_mock_content_sections(material_name: str = "", category: str = "") -> dict:
    """
    Generate mock content sections separately.
    
    Args:
        material_name: Name of the material
        category: Material category
        
    Returns:
        dict: Dictionary with different content sections
    """
    content = generate_mock_content(material_name, category)
    
    # Split content into sections
    sections = {}
    current_section = None
    current_content = []
    
    for line in content.split('\n'):
        if line.startswith('## '):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = line[3:].strip()
            current_content = []
        elif line.startswith('# '):
            sections['title'] = line[2:].strip()
        else:
            current_content.append(line)
    
    # Add the last section
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections
