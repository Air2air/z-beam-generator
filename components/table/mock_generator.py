"""
Table component mock generator for testing and development.
"""
import random
import logging

logger = logging.getLogger(__name__)


def generate_mock_table(material_name: str = "", category: str = "") -> str:
    """
    Generate mock table content for testing.
    
    Args:
        material_name: Name of the material
        category: Material category
        
    Returns:
        str: Mock table content in markdown format
    """
    # Use provided material name or generate one
    if not material_name:
        materials_by_category = {
            "metals": ["Steel", "Aluminum", "Copper", "Titanium"],
            "ceramics": ["Alumina", "Zirconia", "Silicon Carbide"],
            "composites": ["Carbon Fiber", "Fiberglass"],
            "stones": ["Marble", "Granite", "Limestone"],
            "default": ["Metal Alloy", "Industrial Material"]
        }
        materials = materials_by_category.get(category.lower(), materials_by_category["default"])
        material_name = random.choice(materials)
    
    # Generate different types of tables
    table_types = ["parameters", "properties", "results", "comparison"]
    table_type = random.choice(table_types)
    
    if table_type == "parameters":
        return generate_parameters_table(material_name)
    elif table_type == "properties":
        return generate_properties_table(material_name)
    elif table_type == "results":
        return generate_results_table(material_name)
    else:  # comparison
        return generate_comparison_table(material_name)


def generate_parameters_table(material_name: str) -> str:
    """Generate laser parameters table."""
    parameters = [
        ("Wavelength", random.choice(["1064 nm", "532 nm", "355 nm", "266 nm"])),
        ("Pulse Duration", random.choice(["10 ns", "100 ps", "1 fs", "500 fs"])),
        ("Repetition Rate", random.choice(["1 kHz", "10 kHz", "100 kHz", "1 MHz"])),
        ("Energy Density", f"{random.randint(1, 50)} J/cm²"),
        ("Beam Diameter", f"{random.randint(1, 10)} mm"),
        ("Scanning Speed", f"{random.randint(10, 1000)} mm/s"),
        ("Number of Passes", str(random.randint(1, 5)))
    ]
    
    # Select random subset
    selected_params = random.sample(parameters, random.randint(4, 6))
    
    table = f"| Parameter | Value for {material_name} |\n"
    table += "|-----------|-------------------------|\n"
    
    for param, value in selected_params:
        table += f"| {param} | {value} |\n"
    
    return table


def generate_properties_table(material_name: str) -> str:
    """Generate material properties table."""
    properties = [
        ("Absorption Coefficient", f"{random.uniform(0.1, 0.9):.2f}"),
        ("Reflectance", f"{random.randint(10, 90)}%"),
        ("Thermal Conductivity", f"{random.randint(10, 400)} W/m·K"),
        ("Melting Point", f"{random.randint(500, 3000)}°C"),
        ("Density", f"{random.uniform(1.0, 20.0):.2f} g/cm³"),
        ("Surface Roughness", f"{random.uniform(0.1, 10.0):.1f} μm"),
        ("Hardness", f"{random.randint(50, 1000)} HV")
    ]
    
    # Select random subset
    selected_props = random.sample(properties, random.randint(4, 6))
    
    table = f"| Property | {material_name} Value |\n"
    table += "|----------|---------------------|\n"
    
    for prop, value in selected_props:
        table += f"| {prop} | {value} |\n"
    
    return table


def generate_results_table(material_name: str) -> str:
    """Generate cleaning results table."""
    contaminants = ["Rust", "Paint", "Oxide", "Grease", "Carbon Deposits"]
    removal_rates = [f"{random.randint(85, 99)}%" for _ in range(len(contaminants))]
    
    table = f"| Contaminant Type | Removal Efficiency from {material_name} |\n"
    table += "|------------------|----------------------------------------|\n"
    
    for contaminant, rate in zip(random.sample(contaminants, random.randint(3, 5)), removal_rates):
        table += f"| {contaminant} | {rate} |\n"
    
    return table


def generate_comparison_table(material_name: str) -> str:
    """Generate method comparison table."""
    methods = [
        ("Laser Cleaning", "Excellent", "High", "Low", "Minimal"),
        ("Chemical Cleaning", "Good", "Medium", "High", "High"),
        ("Mechanical Cleaning", "Fair", "Low", "Medium", "Medium"),
        ("Ultrasonic Cleaning", "Good", "Medium", "Low", "Medium")
    ]
    
    table = f"| Cleaning Method | {material_name} Quality | Precision | Environmental Impact | Waste Generation |\n"
    table += "|-----------------|-------------------------|-----------|----------------------|------------------|\n"
    
    for method, quality, precision, env_impact, waste in methods:
        table += f"| {method} | {quality} | {precision} | {env_impact} | {waste} |\n"
    
    return table


def generate_mock_table_variations(material_name: str = "", category: str = "", count: int = 3) -> list:
    """
    Generate multiple mock table variations.
    
    Args:
        material_name: Name of the material
        category: Material category
        count: Number of variations to generate
        
    Returns:
        list: List of mock table variations
    """
    return [generate_mock_table(material_name, category) for _ in range(count)]
