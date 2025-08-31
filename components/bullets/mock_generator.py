"""
Bullets component mock generator for testing and development.
"""
import random
import logging

logger = logging.getLogger(__name__)


def generate_mock_bullets(material_name: str = "", category: str = "") -> str:
    """
    Generate mock bullet points for testing.
    
    Args:
        material_name: Name of the material
        category: Material category
        
    Returns:
        str: Mock bullet points content
    """
    # Use provided material name or generate one
    if not material_name:
        materials_by_category = {
            "metals": ["steel", "aluminum", "copper", "titanium"],
            "ceramics": ["alumina", "zirconia", "silicon carbide"],
            "composites": ["carbon fiber", "fiberglass"],
            "stones": ["marble", "granite", "limestone"],
            "default": ["industrial components", "metal surfaces"]
        }
        materials = materials_by_category.get(category.lower(), materials_by_category["default"])
        material_name = random.choice(materials)
    
    # Bullet point categories
    advantages_bullets = [
        f"Precise removal of contaminants from {material_name} surfaces",
        f"Non-contact process preserves {material_name} dimensional integrity",
        "Environmentally friendly alternative to chemical cleaning",
        f"Selective targeting minimizes {material_name} substrate damage",
        f"Real-time process control ensures consistent {material_name} treatment",
        "Reduced processing time compared to traditional methods"
    ]
    
    applications_bullets = [
        f"Surface preparation for {material_name} coating applications",
        f"Restoration of aged {material_name} components",
        f"Removal of manufacturing residues from {material_name}",
        f"Pre-welding surface cleaning of {material_name}",
        "Quality control and inspection preparation",
        f"Maintenance cleaning for {material_name} equipment"
    ]
    
    technical_bullets = [
        f"Wavelength optimization for {material_name} material properties",
        "Pulse duration control for selective contaminant removal",
        f"Energy density calibration specific to {material_name}",
        "Scanning pattern optimization for uniform coverage",
        "Atmospheric condition monitoring during processing",
        f"Temperature management to prevent {material_name} damage"
    ]
    
    safety_bullets = [
        f"Enclosed processing area for {material_name} laser cleaning",
        "Fume extraction systems for safe operation",
        "Laser safety protocols and protective equipment",
        f"Regular monitoring of {material_name} surface temperature",
        "Emergency shutdown procedures and safety interlocks",
        f"Personnel training for {material_name} laser cleaning operations"
    ]
    
    # Randomly select bullets from different categories
    selected_bullets = []
    selected_bullets.extend(random.sample(advantages_bullets, 2))
    selected_bullets.extend(random.sample(applications_bullets, 2))
    selected_bullets.extend(random.sample(technical_bullets, 2))
    selected_bullets.extend(random.sample(safety_bullets, 1))
    
    # Shuffle the order
    random.shuffle(selected_bullets)
    
    # Format as markdown bullet points
    bullet_content = '\n'.join(f"- {bullet}" for bullet in selected_bullets)
    
    return bullet_content


def generate_mock_bullets_by_category(material_name: str = "", category: str = "") -> dict:
    """
    Generate mock bullet points organized by category.
    
    Args:
        material_name: Name of the material
        category: Material category
        
    Returns:
        dict: Dictionary with categorized bullet points
    """
    if not material_name:
        materials_by_category = {
            "metals": ["steel", "aluminum", "copper"],
            "ceramics": ["alumina", "zirconia"],
            "composites": ["carbon fiber"],
            "stones": ["marble", "granite"],
            "default": ["industrial components"]
        }
        materials = materials_by_category.get(category.lower(), materials_by_category["default"])
        material_name = random.choice(materials)
    
    return {
        "advantages": [
            f"Precise removal of contaminants from {material_name} surfaces",
            f"Non-contact process preserves {material_name} dimensional integrity",
            "Environmentally friendly alternative to chemical cleaning",
            f"Selective targeting minimizes {material_name} substrate damage"
        ],
        "applications": [
            f"Surface preparation for {material_name} coating applications",
            f"Restoration of aged {material_name} components",
            f"Removal of manufacturing residues from {material_name}",
            f"Pre-welding surface cleaning of {material_name}"
        ],
        "technical": [
            f"Wavelength optimization for {material_name} material properties",
            "Pulse duration control for selective contaminant removal",
            f"Energy density calibration specific to {material_name}",
            "Scanning pattern optimization for uniform coverage"
        ],
        "safety": [
            f"Enclosed processing area for {material_name} laser cleaning",
            "Fume extraction systems for safe operation",
            "Laser safety protocols and protective equipment",
            f"Regular monitoring of {material_name} surface temperature"
        ]
    }
