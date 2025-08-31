"""
Metatags component mock generator for testing and development.
"""
import random
import logging

logger = logging.getLogger(__name__)


def generate_mock_metatags(material_name: str = "", category: str = "") -> str:
    """
    Generate mock metatags content for testing.
    
    Args:
        material_name: Name of the material
        category: Material category
        
    Returns:
        str: Mock metatags content in HTML format
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
    
    # Generate meta descriptions
    descriptions = [
        f"Professional {material_name} laser cleaning services for precision surface treatment and contamination removal.",
        f"Advanced laser cleaning technology for {material_name} surface preparation and restoration applications.",
        f"Industrial {material_name} cleaning solutions using state-of-the-art laser ablation technology.",
        f"Expert {material_name} surface treatment with environmentally friendly laser cleaning processes."
    ]
    
    # Generate keywords
    base_keywords = ["laser cleaning", "surface treatment", "industrial cleaning", "precision processing"]
    material_keywords = [material_name.lower(), f"{material_name.lower()} cleaning", f"{material_name.lower()} processing"]
    category_keywords = get_category_keywords(category)
    
    all_keywords = base_keywords + material_keywords + category_keywords
    selected_keywords = random.sample(all_keywords, min(8, len(all_keywords)))
    
    # Generate robots directive
    robots_options = ["index,follow", "index,follow,max-snippet:150", "index,follow,noarchive"]
    robots = random.choice(robots_options)
    
    # Generate viewport
    viewport = "width=device-width, initial-scale=1.0"
    
    # Generate author
    authors = ["Laser Technology Expert", "Industrial Processing Specialist", "Surface Treatment Professional"]
    author = random.choice(authors)
    
    # Create metatags HTML
    description = random.choice(descriptions)
    keywords_str = ", ".join(selected_keywords)
    
    metatags = f'''<meta charset="UTF-8">
<meta name="viewport" content="{viewport}">
<meta name="description" content="{description}">
<meta name="keywords" content="{keywords_str}">
<meta name="author" content="{author}">
<meta name="robots" content="{robots}">
<meta name="language" content="en">
<meta name="revisit-after" content="7 days">

<!-- Open Graph meta tags -->
<meta property="og:title" content="{material_name} Laser Cleaning Services">
<meta property="og:description" content="{description}">
<meta property="og:type" content="article">
<meta property="og:url" content="https://example.com/{material_name.lower().replace(' ', '-')}-laser-cleaning">
<meta property="og:image" content="https://example.com/images/{material_name.lower().replace(' ', '-')}-laser-cleaning.jpg">

<!-- Twitter Card meta tags -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{material_name} Laser Cleaning">
<meta name="twitter:description" content="{description[:150]}...">
<meta name="twitter:image" content="https://example.com/images/{material_name.lower().replace(' ', '-')}-twitter.jpg">'''
    
    return metatags


def get_category_keywords(category: str) -> list:
    """Get category-specific keywords."""
    category_keywords = {
        "metals": ["metal processing", "oxide removal", "rust cleaning", "metalworking"],
        "ceramics": ["ceramic treatment", "advanced materials", "technical ceramics"],
        "composites": ["composite cleaning", "fiber processing", "advanced composites"],
        "stones": ["stone restoration", "architectural cleaning", "monument preservation"],
        "default": ["material processing", "surface preparation", "industrial applications"]
    }
    
    return category_keywords.get(category.lower(), category_keywords["default"])


def generate_mock_metatags_variations(material_name: str = "", category: str = "", count: int = 3) -> list:
    """
    Generate multiple mock metatags variations.
    
    Args:
        material_name: Name of the material
        category: Material category
        count: Number of variations to generate
        
    Returns:
        list: List of mock metatags variations
    """
    return [generate_mock_metatags(material_name, category) for _ in range(count)]


def generate_mock_structured_metatags(material_name: str = "", category: str = "") -> dict:
    """
    Generate mock metatags as structured data.
    
    Args:
        material_name: Name of the material
        category: Material category
        
    Returns:
        dict: Dictionary with organized metatag data
    """
    if not material_name:
        material_name = "Industrial Material"
    
    return {
        "basic": {
            "charset": "UTF-8",
            "viewport": "width=device-width, initial-scale=1.0",
            "language": "en"
        },
        "seo": {
            "title": f"{material_name} Laser Cleaning Services",
            "description": f"Professional {material_name} laser cleaning for precision surface treatment.",
            "keywords": ["laser cleaning", material_name.lower(), "surface treatment"],
            "author": "Laser Technology Expert",
            "robots": "index,follow"
        },
        "social": {
            "og_title": f"{material_name} Laser Cleaning",
            "og_description": f"Advanced laser cleaning technology for {material_name} processing.",
            "og_type": "article",
            "twitter_card": "summary_large_image"
        },
        "technical": {
            "revisit_after": "7 days",
            "cache_control": "public, max-age=3600",
            "content_language": "en-US"
        }
    }
