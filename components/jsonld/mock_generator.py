"""
JSON-LD component mock generator for testing and development.
"""
import random
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def generate_mock_jsonld(material_name: str = "", category: str = "") -> str:
    """
    Generate mock JSON-LD structured data for testing.
    
    Args:
        material_name: Name of the material
        category: Material category
        
    Returns:
        str: Mock JSON-LD content
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
    
    # Generate organization data
    organization = {
        "@type": "Organization",
        "name": "Advanced Laser Solutions",
        "url": "https://example.com",
        "logo": "https://example.com/logo.jpg",
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "+1-555-LASER",
            "contactType": "customer service"
        }
    }
    
    # Generate service data
    service_descriptions = [
        f"Professional {material_name} laser cleaning services for industrial applications",
        f"Precision {material_name} surface treatment using advanced laser technology",
        f"Expert {material_name} cleaning solutions for surface preparation and restoration"
    ]
    
    service = {
        "@type": "Service",
        "name": f"{material_name} Laser Cleaning",
        "description": random.choice(service_descriptions),
        "provider": organization,
        "areaServed": "Worldwide",
        "serviceType": "Industrial Laser Cleaning",
        "category": get_service_category(category)
    }
    
    # Generate article data
    article_title = f"{material_name} Laser Cleaning: Advanced Surface Treatment Solutions"
    article_description = f"Comprehensive guide to {material_name} laser cleaning technology and applications"
    
    # Generate random publish date (within last year)
    days_ago = random.randint(1, 365)
    publish_date = (datetime.now() - timedelta(days=days_ago)).isoformat()
    
    article = {
        "@type": "Article",
        "headline": article_title,
        "description": article_description,
        "author": {
            "@type": "Person",
            "name": "Dr. Sarah Johnson",
            "jobTitle": "Laser Technology Specialist"
        },
        "publisher": organization,
        "datePublished": publish_date,
        "dateModified": datetime.now().isoformat(),
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"https://example.com/{material_name.lower().replace(' ', '-')}-laser-cleaning"
        },
        "image": {
            "@type": "ImageObject",
            "url": f"https://example.com/images/{material_name.lower().replace(' ', '-')}-cleaning.jpg",
            "width": 1200,
            "height": 800
        }
    }
    
    # Generate FAQ data
    faqs = generate_material_faqs(material_name, category)
    
    faq_schema = {
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq["answer"]
                }
            } for faq in faqs
        ]
    }
    
    # Generate breadcrumb data
    breadcrumb = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": "https://example.com"
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": "Services",
                "item": "https://example.com/services"
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": f"{material_name} Cleaning",
                "item": f"https://example.com/services/{material_name.lower().replace(' ', '-')}"
            }
        ]
    }
    
    # Combine all schemas
    combined_schema = {
        "@context": "https://schema.org",
        "@graph": [
            service,
            article,
            faq_schema,
            breadcrumb
        ]
    }
    
    # Return formatted JSON-LD
    return f'<script type="application/ld+json">\n{json.dumps(combined_schema, indent=2)}\n</script>'


def generate_material_faqs(material_name: str, category: str) -> list:
    """Generate material-specific FAQ data."""
    base_faqs = [
        {
            "question": f"What are the benefits of laser cleaning for {material_name}?",
            "answer": f"Laser cleaning offers precise, non-contact removal of contaminants from {material_name} surfaces without chemical residues or substrate damage."
        },
        {
            "question": f"Is laser cleaning safe for {material_name}?",
            "answer": f"Yes, laser cleaning is safe for {material_name} when proper parameters are used. The process is precisely controlled to remove only surface contaminants."
        }
    ]
    
    category_faqs = {
        "metals": [
            {
                "question": f"Can laser cleaning remove rust from {material_name}?",
                "answer": f"Yes, laser cleaning effectively removes rust, oxide layers, and corrosion from {material_name} surfaces without damaging the base material."
            }
        ],
        "ceramics": [
            {
                "question": f"Will laser cleaning damage {material_name} surfaces?",
                "answer": f"No, laser cleaning parameters can be precisely tuned for {material_name} to ensure selective removal without substrate damage."
            }
        ],
        "composites": [
            {
                "question": f"Is laser cleaning suitable for {material_name} composites?",
                "answer": f"Yes, laser cleaning is ideal for {material_name} as it preserves fiber integrity while removing surface contaminants."
            }
        ]
    }
    
    specific_faqs = category_faqs.get(category.lower(), [])
    return base_faqs + specific_faqs[:2]  # Limit to reasonable number


def get_service_category(category: str) -> str:
    """Get service category for schema."""
    category_mapping = {
        "metals": "Metal Surface Treatment",
        "ceramics": "Advanced Material Processing",
        "composites": "Composite Material Treatment",
        "stones": "Stone Restoration Services",
        "default": "Industrial Surface Treatment"
    }
    
    return category_mapping.get(category.lower(), category_mapping["default"])


def generate_mock_jsonld_variations(material_name: str = "", category: str = "", count: int = 3) -> list:
    """
    Generate multiple mock JSON-LD variations.
    
    Args:
        material_name: Name of the material
        category: Material category
        count: Number of variations to generate
        
    Returns:
        list: List of mock JSON-LD variations
    """
    return [generate_mock_jsonld(material_name, category) for _ in range(count)]


def generate_mock_structured_jsonld(material_name: str = "", category: str = "") -> dict:
    """
    Generate mock JSON-LD as structured data (without script tags).
    
    Args:
        material_name: Name of the material
        category: Material category
        
    Returns:
        dict: Dictionary with JSON-LD structured data
    """
    if not material_name:
        material_name = "Industrial Material"
    
    return {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": f"{material_name} Laser Cleaning",
        "description": f"Professional {material_name} laser cleaning services",
        "provider": {
            "@type": "Organization",
            "name": "Advanced Laser Solutions"
        },
        "serviceType": "Industrial Laser Cleaning",
        "category": get_service_category(category)
    }
