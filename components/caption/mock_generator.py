"""
Caption component mock generator for testing and development.
"""
import random
import logging

logger = logging.getLogger(__name__)


def generate_mock_caption(material_name: str = "", category: str = "") -> str:
    """
    Generate mock caption content for testing.
    
    Args:
        material_name: Name of the material
        category: Material category
        
    Returns:
        str: Mock caption content
    """
    # Base caption templates
    caption_templates = [
        "Laser cleaning process removing {contaminant} from {material} surface",
        "High-precision {material} surface treatment using pulsed laser technology",
        "Before and after comparison of {material} laser cleaning results",
        "Detailed view of {material} surface after laser contaminant removal",
        "Industrial laser cleaning setup for {material} processing",
        "Microscopic analysis of {material} surface post-laser treatment",
        "Quality control inspection of laser-cleaned {material} component",
        "Professional {material} restoration using advanced laser cleaning"
    ]
    
    # Material-specific contaminants
    contaminants_by_category = {
        "metals": ["rust", "oxide layers", "paint", "grease", "welding residue"],
        "ceramics": ["organic residues", "carbon deposits", "surface coatings"],
        "composites": ["adhesive residues", "surface contamination", "old coatings"],
        "stones": ["weathering products", "biological growth", "pollution deposits"],
        "default": ["contaminants", "unwanted deposits", "surface impurities"]
    }
    
    # Get appropriate contaminants
    contaminants = contaminants_by_category.get(category.lower(), contaminants_by_category["default"])
    
    # Select random template and contaminant
    template = random.choice(caption_templates)
    contaminant = random.choice(contaminants)
    
    # Use provided material name or generate one
    if not material_name:
        materials_by_category = {
            "metals": ["steel", "aluminum", "copper", "titanium", "stainless steel"],
            "ceramics": ["alumina", "zirconia", "silicon carbide", "ceramic"],
            "composites": ["carbon fiber", "fiberglass", "composite panel"],
            "stones": ["marble", "granite", "limestone", "sandstone"],
            "default": ["industrial component", "metal part", "surface"]
        }
        materials = materials_by_category.get(category.lower(), materials_by_category["default"])
        material_name = random.choice(materials)
    
    # Format the caption
    caption = template.format(
        material=material_name,
        contaminant=contaminant
    )
    
    return caption


def generate_mock_caption_variations(material_name: str = "", category: str = "", count: int = 3) -> list:
    """
    Generate multiple mock caption variations.
    
    Args:
        material_name: Name of the material
        category: Material category
        count: Number of variations to generate
        
    Returns:
        list: List of mock caption variations
    """
    return [generate_mock_caption(material_name, category) for _ in range(count)]
