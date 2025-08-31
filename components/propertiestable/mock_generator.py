"""
Properties table component mock generator for testing and development.
"""
import random
import logging

logger = logging.getLogger(__name__)


def generate_mock_propertiestable(material_name: str = "", category: str = "") -> str:
    """
    Generate mock properties table content for testing.
    
    Args:
        material_name: Name of the material
        category: Material category
        
    Returns:
        str: Mock properties table content in HTML format
    """
    # Use provided material name or generate one
    if not material_name:
        materials_by_category = {
            "metals": ["Steel", "Aluminum", "Copper", "Titanium"],
            "ceramics": ["Alumina", "Zirconia", "Silicon Carbide"],
            "composites": ["Carbon Fiber", "Fiberglass"],
            "stones": ["Marble", "Granite", "Limestone"],
            "default": ["Industrial Material", "Advanced Alloy"]
        }
        materials = materials_by_category.get(category.lower(), materials_by_category["default"])
        material_name = random.choice(materials)
    
    # Generate category-specific properties
    properties = get_category_properties(category, material_name)
    
    # Generate laser cleaning specific properties
    laser_properties = get_laser_cleaning_properties(category)
    
    # Combine properties
    all_properties = {**properties, **laser_properties}
    
    # Create HTML table
    table_html = f'''<div class="properties-table-container">
    <h3>{material_name} Properties & Laser Cleaning Parameters</h3>
    <table class="properties-table">
        <thead>
            <tr>
                <th>Property</th>
                <th>Value</th>
                <th>Unit</th>
                <th>Notes</th>
            </tr>
        </thead>
        <tbody>'''
    
    for prop_name, prop_data in all_properties.items():
        table_html += f'''
            <tr>
                <td class="property-name">{prop_name}</td>
                <td class="property-value">{prop_data['value']}</td>
                <td class="property-unit">{prop_data['unit']}</td>
                <td class="property-notes">{prop_data['notes']}</td>
            </tr>'''
    
    table_html += '''
        </tbody>
    </table>
    <div class="table-footer">
        <p><em>Values are typical ranges and may vary based on specific material composition and laser cleaning parameters.</em></p>
    </div>
</div>'''
    
    return table_html


def get_category_properties(category: str, material_name: str) -> dict:
    """Get category-specific material properties."""
    
    if category.lower() == "metals":
        return {
            "Density": {
                "value": f"{random.uniform(2.7, 19.3):.1f}",
                "unit": "g/cm³",
                "notes": f"Typical density range for {material_name}"
            },
            "Melting Point": {
                "value": f"{random.randint(600, 3400)}",
                "unit": "°C",
                "notes": "Temperature at which material melts"
            },
            "Thermal Conductivity": {
                "value": f"{random.uniform(10, 400):.0f}",
                "unit": "W/m·K",
                "notes": "Heat transfer capability"
            },
            "Hardness (HV)": {
                "value": f"{random.randint(50, 800)}",
                "unit": "HV",
                "notes": "Vickers hardness measurement"
            },
            "Electrical Resistivity": {
                "value": f"{random.uniform(1.6, 100):.1f}",
                "unit": "μΩ·cm",
                "notes": "Electrical resistance property"
            }
        }
    
    elif category.lower() == "ceramics":
        return {
            "Density": {
                "value": f"{random.uniform(2.0, 6.0):.1f}",
                "unit": "g/cm³",
                "notes": f"Typical density for {material_name} ceramic"
            },
            "Melting Point": {
                "value": f"{random.randint(1500, 2800)}",
                "unit": "°C",
                "notes": "High temperature stability"
            },
            "Compressive Strength": {
                "value": f"{random.randint(1000, 4000)}",
                "unit": "MPa",
                "notes": "Resistance to compression"
            },
            "Thermal Expansion": {
                "value": f"{random.uniform(3, 12):.1f}",
                "unit": "×10⁻⁶/K",
                "notes": "Expansion coefficient"
            },
            "Dielectric Constant": {
                "value": f"{random.uniform(4, 25):.1f}",
                "unit": "εᵣ",
                "notes": "Electrical insulation property"
            }
        }
    
    elif category.lower() == "composites":
        return {
            "Fiber Volume Fraction": {
                "value": f"{random.randint(45, 70)}",
                "unit": "%",
                "notes": f"Fiber content in {material_name}"
            },
            "Tensile Strength": {
                "value": f"{random.randint(500, 3500)}",
                "unit": "MPa",
                "notes": "Ultimate tensile strength"
            },
            "Elastic Modulus": {
                "value": f"{random.randint(50, 300)}",
                "unit": "GPa",
                "notes": "Stiffness measurement"
            },
            "Glass Transition": {
                "value": f"{random.randint(80, 250)}",
                "unit": "°C",
                "notes": "Matrix softening temperature"
            },
            "Void Content": {
                "value": f"{random.uniform(0.5, 3.0):.1f}",
                "unit": "%",
                "notes": "Internal porosity level"
            }
        }
    
    elif category.lower() == "stones":
        return {
            "Density": {
                "value": f"{random.uniform(2.2, 3.0):.1f}",
                "unit": "g/cm³",
                "notes": f"Natural density of {material_name}"
            },
            "Compressive Strength": {
                "value": f"{random.randint(50, 300)}",
                "unit": "MPa",
                "notes": "Load bearing capacity"
            },
            "Porosity": {
                "value": f"{random.uniform(0.1, 15):.1f}",
                "unit": "%",
                "notes": "Open pore structure"
            },
            "Water Absorption": {
                "value": f"{random.uniform(0.05, 5):.2f}",
                "unit": "%",
                "notes": "Moisture uptake capacity"
            },
            "Abrasion Resistance": {
                "value": f"{random.uniform(15, 35):.1f}",
                "unit": "mm",
                "notes": "Wear resistance measure"
            }
        }
    
    else:  # default
        return {
            "Density": {
                "value": f"{random.uniform(1.5, 8.0):.1f}",
                "unit": "g/cm³",
                "notes": f"Material density for {material_name}"
            },
            "Service Temperature": {
                "value": f"{random.randint(200, 1000)}",
                "unit": "°C",
                "notes": "Maximum operating temperature"
            },
            "Surface Roughness": {
                "value": f"{random.uniform(0.1, 5.0):.1f}",
                "unit": "μm Ra",
                "notes": "Typical surface finish"
            }
        }


def get_laser_cleaning_properties(category: str) -> dict:
    """Get laser cleaning specific properties."""
    base_properties = {
        "Laser Wavelength": {
            "value": "1064",
            "unit": "nm",
            "notes": "Optimal wavelength for cleaning"
        },
        "Pulse Duration": {
            "value": f"{random.randint(50, 500)}",
            "unit": "ns",
            "notes": "Nanosecond pulse regime"
        },
        "Repetition Rate": {
            "value": f"{random.randint(10, 100)}",
            "unit": "kHz",
            "notes": "Pulse frequency for optimal cleaning"
        },
        "Beam Diameter": {
            "value": f"{random.uniform(5, 20):.1f}",
            "unit": "mm",
            "notes": "Focused beam size on surface"
        }
    }
    
    # Add category-specific laser parameters
    if category.lower() == "metals":
        base_properties["Fluence Range"] = {
            "value": f"{random.uniform(1, 10):.1f}",
            "unit": "J/cm²",
            "notes": "Energy density for oxide removal"
        }
        base_properties["Scan Speed"] = {
            "value": f"{random.randint(100, 1000)}",
            "unit": "mm/min",
            "notes": "Optimal processing speed"
        }
    
    elif category.lower() == "ceramics":
        base_properties["Fluence Range"] = {
            "value": f"{random.uniform(0.5, 5):.1f}",
            "unit": "J/cm²",
            "notes": "Gentle cleaning parameters"
        }
        base_properties["Overlap Ratio"] = {
            "value": f"{random.randint(70, 90)}",
            "unit": "%",
            "notes": "Pulse overlap for uniform cleaning"
        }
    
    elif category.lower() == "composites":
        base_properties["Fluence Range"] = {
            "value": f"{random.uniform(0.2, 2):.1f}",
            "unit": "J/cm²",
            "notes": "Low energy to preserve fibers"
        }
        base_properties["Spot Size"] = {
            "value": f"{random.uniform(0.1, 1):.1f}",
            "unit": "mm",
            "notes": "Small spot for precision"
        }
    
    return base_properties


def generate_mock_propertiestable_variations(material_name: str = "", category: str = "", count: int = 3) -> list:
    """
    Generate multiple mock properties table variations.
    
    Args:
        material_name: Name of the material
        category: Material category
        count: Number of variations to generate
        
    Returns:
        list: List of mock table variations
    """
    return [generate_mock_propertiestable(material_name, category) for _ in range(count)]


def generate_mock_structured_properties(material_name: str = "", category: str = "") -> dict:
    """
    Generate mock properties as structured data.
    
    Args:
        material_name: Name of the material
        category: Material category
        
    Returns:
        dict: Dictionary with organized property data
    """
    if not material_name:
        material_name = "Industrial Material"
    
    properties = get_category_properties(category, material_name)
    laser_properties = get_laser_cleaning_properties(category)
    
    return {
        "material_name": material_name,
        "category": category,
        "material_properties": properties,
        "laser_parameters": laser_properties,
        "notes": "Properties optimized for laser cleaning applications"
    }
