"""
Badge symbol component mock generator for testing and development.
"""
import random
import logging

logger = logging.getLogger(__name__)


def generate_mock_badgesymbol(material_name: str = "", category: str = "") -> str:
    """
    Generate mock badge symbol content for testing.
    
    Args:
        material_name: Name of the material
        category: Material category
        
    Returns:
        str: Mock badge symbol content in HTML format
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
    
    # Generate category-specific badges
    badges = get_category_badges(category, material_name)
    
    # Generate certification badges
    cert_badges = get_certification_badges()
    
    # Generate quality badges
    quality_badges = get_quality_badges(material_name)
    
    # Generate process badges
    process_badges = get_process_badges()
    
    # Select random badges from each category
    selected_badges = (
        random.sample(badges, min(2, len(badges))) +
        random.sample(cert_badges, min(2, len(cert_badges))) +
        random.sample(quality_badges, min(2, len(quality_badges))) +
        random.sample(process_badges, min(1, len(process_badges)))
    )
    
    # Create badge HTML
    badge_html = '<div class="badge-collection">\n'
    
    for badge in selected_badges:
        badge_html += f'''    <div class="badge-item {badge['type']}-badge">
        <div class="badge-icon">
            <i class="{badge['icon']}" aria-hidden="true"></i>
        </div>
        <div class="badge-content">
            <span class="badge-title">{badge['title']}</span>
            <span class="badge-subtitle">{badge['subtitle']}</span>
        </div>
        <div class="badge-verify">
            <a href="{badge['verify_url']}" class="verify-link" aria-label="Verify {badge['title']}">
                <i class="fas fa-external-link-alt"></i>
            </a>
        </div>
    </div>
'''
    
    badge_html += '</div>'
    
    # Add badge styles
    styles = '''
<style>
.badge-collection {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin: 1rem 0;
}

.badge-item {
    display: flex;
    align-items: center;
    background: linear-gradient(135deg, #f8f9fa, #e9ecef);
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 0.75rem;
    min-width: 200px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: transform 0.2s ease;
}

.badge-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.certification-badge {
    border-color: #28a745;
    background: linear-gradient(135deg, #d4edda, #c3e6cb);
}

.quality-badge {
    border-color: #007bff;
    background: linear-gradient(135deg, #d1ecf1, #bee5eb);
}

.process-badge {
    border-color: #6f42c1;
    background: linear-gradient(135deg, #e2d9f3, #d1c4e9);
}

.material-badge {
    border-color: #fd7e14;
    background: linear-gradient(135deg, #ffe8d1, #fed7aa);
}

.badge-icon {
    font-size: 1.5rem;
    margin-right: 0.75rem;
    color: #495057;
}

.badge-content {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.badge-title {
    font-weight: 600;
    font-size: 0.9rem;
    color: #212529;
}

.badge-subtitle {
    font-size: 0.75rem;
    color: #6c757d;
    margin-top: 0.25rem;
}

.badge-verify {
    margin-left: 0.5rem;
}

.verify-link {
    color: #6c757d;
    text-decoration: none;
    font-size: 0.8rem;
}

.verify-link:hover {
    color: #495057;
}
</style>'''
    
    return styles + badge_html


def get_category_badges(category: str, material_name: str) -> list:
    """Get category-specific badges."""
    
    if category.lower() == "metals":
        return [
            {
                "type": "material",
                "title": f"{material_name} Certified",
                "subtitle": "Alloy Composition Verified",
                "icon": "fas fa-certificate",
                "verify_url": "https://example.com/verify/metal-cert"
            },
            {
                "type": "material",
                "title": "Corrosion Resistant",
                "subtitle": "Enhanced Durability",
                "icon": "fas fa-shield-alt",
                "verify_url": "https://example.com/verify/corrosion"
            },
            {
                "type": "material",
                "title": "High Strength",
                "subtitle": "Superior Mechanical Properties",
                "icon": "fas fa-dumbbell",
                "verify_url": "https://example.com/verify/strength"
            }
        ]
    
    elif category.lower() == "ceramics":
        return [
            {
                "type": "material",
                "title": f"{material_name} Grade",
                "subtitle": "Premium Ceramic Quality",
                "icon": "fas fa-gem",
                "verify_url": "https://example.com/verify/ceramic-grade"
            },
            {
                "type": "material",
                "title": "High Temperature",
                "subtitle": "Thermal Stability Tested",
                "icon": "fas fa-thermometer-full",
                "verify_url": "https://example.com/verify/thermal"
            },
            {
                "type": "material",
                "title": "Electrical Insulation",
                "subtitle": "Dielectric Properties",
                "icon": "fas fa-bolt",
                "verify_url": "https://example.com/verify/dielectric"
            }
        ]
    
    elif category.lower() == "composites":
        return [
            {
                "type": "material",
                "title": f"{material_name} Composite",
                "subtitle": "Fiber Reinforced Structure",
                "icon": "fas fa-layer-group",
                "verify_url": "https://example.com/verify/composite"
            },
            {
                "type": "material",
                "title": "Lightweight Design",
                "subtitle": "High Strength-to-Weight",
                "icon": "fas fa-feather-alt",
                "verify_url": "https://example.com/verify/lightweight"
            },
            {
                "type": "material",
                "title": "Fatigue Resistant",
                "subtitle": "Long Service Life",
                "icon": "fas fa-clock",
                "verify_url": "https://example.com/verify/fatigue"
            }
        ]
    
    elif category.lower() == "stones":
        return [
            {
                "type": "material",
                "title": f"Natural {material_name}",
                "subtitle": "Authentic Stone Material",
                "icon": "fas fa-mountain",
                "verify_url": "https://example.com/verify/natural-stone"
            },
            {
                "type": "material",
                "title": "Weather Resistant",
                "subtitle": "Outdoor Durability",
                "icon": "fas fa-cloud-rain",
                "verify_url": "https://example.com/verify/weather"
            },
            {
                "type": "material",
                "title": "Architectural Grade",
                "subtitle": "Building Standard Quality",
                "icon": "fas fa-building",
                "verify_url": "https://example.com/verify/architectural"
            }
        ]
    
    else:  # default
        return [
            {
                "type": "material",
                "title": f"{material_name} Verified",
                "subtitle": "Quality Assured Material",
                "icon": "fas fa-check-circle",
                "verify_url": "https://example.com/verify/material"
            },
            {
                "type": "material",
                "title": "Industrial Grade",
                "subtitle": "Commercial Application",
                "icon": "fas fa-industry",
                "verify_url": "https://example.com/verify/industrial"
            }
        ]


def get_certification_badges() -> list:
    """Get certification badges."""
    return [
        {
            "type": "certification",
            "title": "ISO 9001:2015",
            "subtitle": "Quality Management System",
            "icon": "fas fa-award",
            "verify_url": "https://example.com/verify/iso9001"
        },
        {
            "type": "certification",
            "title": "ISO 14001",
            "subtitle": "Environmental Management",
            "icon": "fas fa-leaf",
            "verify_url": "https://example.com/verify/iso14001"
        },
        {
            "type": "certification",
            "title": "OHSAS 18001",
            "subtitle": "Occupational Health & Safety",
            "icon": "fas fa-hard-hat",
            "verify_url": "https://example.com/verify/ohsas"
        },
        {
            "type": "certification",
            "title": "CE Marking",
            "subtitle": "European Conformity",
            "icon": "fas fa-stamp",
            "verify_url": "https://example.com/verify/ce"
        }
    ]


def get_quality_badges(material_name: str) -> list:
    """Get quality assurance badges."""
    return [
        {
            "type": "quality",
            "title": "Laboratory Tested",
            "subtitle": "Third-Party Verification",
            "icon": "fas fa-microscope",
            "verify_url": "https://example.com/verify/lab-test"
        },
        {
            "type": "quality",
            "title": "Zero Defects",
            "subtitle": "100% Quality Inspection",
            "icon": "fas fa-search",
            "verify_url": "https://example.com/verify/inspection"
        },
        {
            "type": "quality",
            "title": "Traceability",
            "subtitle": "Full Supply Chain Tracking",
            "icon": "fas fa-barcode",
            "verify_url": "https://example.com/verify/traceability"
        },
        {
            "type": "quality",
            "title": "Performance Validated",
            "subtitle": f"{material_name} Testing Complete",
            "icon": "fas fa-chart-line",
            "verify_url": "https://example.com/verify/performance"
        }
    ]


def get_process_badges() -> list:
    """Get process-related badges."""
    return [
        {
            "type": "process",
            "title": "Laser Optimized",
            "subtitle": "Cleaning Parameters Verified",
            "icon": "fas fa-laser-pointer",
            "verify_url": "https://example.com/verify/laser-process"
        },
        {
            "type": "process",
            "title": "Non-Contact Process",
            "subtitle": "Safe Surface Treatment",
            "icon": "fas fa-hand-paper",
            "verify_url": "https://example.com/verify/non-contact"
        },
        {
            "type": "process",
            "title": "Eco-Friendly",
            "subtitle": "Chemical-Free Cleaning",
            "icon": "fas fa-recycle",
            "verify_url": "https://example.com/verify/eco-friendly"
        }
    ]


def generate_mock_badgesymbol_variations(material_name: str = "", category: str = "", count: int = 3) -> list:
    """
    Generate multiple mock badge symbol variations.
    
    Args:
        material_name: Name of the material
        category: Material category
        count: Number of variations to generate
        
    Returns:
        list: List of mock badge variations
    """
    return [generate_mock_badgesymbol(material_name, category) for _ in range(count)]


def generate_mock_structured_badges(material_name: str = "", category: str = "") -> dict:
    """
    Generate mock badges as structured data.
    
    Args:
        material_name: Name of the material
        category: Material category
        
    Returns:
        dict: Dictionary with organized badge data
    """
    if not material_name:
        material_name = "Industrial Material"
    
    badges = get_category_badges(category, material_name)
    cert_badges = get_certification_badges()
    quality_badges = get_quality_badges(material_name)
    process_badges = get_process_badges()
    
    return {
        "material_name": material_name,
        "category": category,
        "badges": {
            "material_specific": badges,
            "certifications": cert_badges[:2],  # Limit for brevity
            "quality_assurance": quality_badges[:2],
            "process_related": process_badges[:1]
        },
        "badge_count": len(badges) + 2 + 2 + 1
    }
