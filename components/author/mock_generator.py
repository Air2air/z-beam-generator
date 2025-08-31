"""
Author component mock generator for testing and development.
"""
import random
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def generate_mock_author(material_name: str = "", category: str = "") -> str:
    """
    Generate mock author content for testing.
    
    Args:
        material_name: Name of the material
        category: Material category
        
    Returns:
        str: Mock author content in HTML format
    """
    # Generate author profiles
    authors = get_author_profiles(category)
    author = random.choice(authors)
    
    # Generate publication date
    days_ago = random.randint(1, 365)
    pub_date = (datetime.now() - timedelta(days=days_ago)).strftime("%B %d, %Y")
    
    # Generate update date (more recent)
    update_days = random.randint(1, min(days_ago, 30))
    update_date = (datetime.now() - timedelta(days=update_days)).strftime("%B %d, %Y")
    
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
    
    # Generate author bio related to material
    bio_variations = [
        f"Dr. {author['name']} is a leading expert in {material_name} processing and surface treatment technologies.",
        f"With over {author['experience']} years of experience, {author['name']} specializes in advanced {material_name} applications.",
        f"{author['name']} is a renowned researcher in {material_name} laser processing and industrial surface modification."
    ]
    
    bio = random.choice(bio_variations)
    
    # Create author HTML
    author_html = f'''<div class="author-section">
    <div class="author-info">
        <div class="author-avatar">
            <img src="{author['avatar']}" alt="{author['name']}" class="author-image">
        </div>
        <div class="author-details">
            <h4 class="author-name">{author['name']}</h4>
            <p class="author-title">{author['title']}</p>
            <p class="author-affiliation">{author['affiliation']}</p>
            <p class="author-bio">{bio}</p>
            
            <div class="author-credentials">
                <span class="credential">{author['degree']}</span>
                <span class="credential">{author['experience']} Years Experience</span>
                <span class="credential">{author['specialization']}</span>
            </div>
            
            <div class="author-social">
                <a href="{author['linkedin']}" class="social-link linkedin" aria-label="LinkedIn Profile">
                    <i class="fab fa-linkedin"></i>
                </a>
                <a href="{author['researchgate']}" class="social-link researchgate" aria-label="ResearchGate Profile">
                    <i class="fab fa-researchgate"></i>
                </a>
                <a href="mailto:{author['email']}" class="social-link email" aria-label="Email Contact">
                    <i class="fas fa-envelope"></i>
                </a>
            </div>
        </div>
    </div>
    
    <div class="publication-info">
        <div class="pub-dates">
            <span class="published">Published: {pub_date}</span>
            <span class="updated">Last Updated: {update_date}</span>
        </div>
        <div class="article-meta">
            <span class="reading-time">{random.randint(5, 15)} min read</span>
            <span class="article-category">{category.title() if category else 'Materials Science'}</span>
        </div>
    </div>
</div>'''
    
    return author_html


def get_author_profiles(category: str) -> list:
    """Get category-specific author profiles."""
    
    base_authors = [
        {
            "name": "Dr. Sarah Johnson",
            "title": "Senior Laser Technology Specialist",
            "affiliation": "Advanced Materials Research Institute",
            "degree": "Ph.D. Materials Science",
            "experience": "15",
            "specialization": "Laser Surface Processing",
            "avatar": "https://example.com/avatars/sarah-johnson.jpg",
            "linkedin": "https://linkedin.com/in/sarah-johnson-laser",
            "researchgate": "https://researchgate.net/profile/sarah-johnson",
            "email": "s.johnson@amri.edu"
        },
        {
            "name": "Prof. Michael Chen",
            "title": "Professor of Industrial Engineering",
            "affiliation": "Institute of Technology",
            "degree": "Ph.D. Mechanical Engineering",
            "experience": "20",
            "specialization": "Manufacturing Processes",
            "avatar": "https://example.com/avatars/michael-chen.jpg",
            "linkedin": "https://linkedin.com/in/michael-chen-prof",
            "researchgate": "https://researchgate.net/profile/michael-chen",
            "email": "m.chen@tech.edu"
        },
        {
            "name": "Dr. Elena Rodriguez",
            "title": "Principal Research Engineer",
            "affiliation": "Laser Processing Solutions",
            "degree": "Ph.D. Optical Engineering",
            "experience": "12",
            "specialization": "Precision Laser Applications",
            "avatar": "https://example.com/avatars/elena-rodriguez.jpg",
            "linkedin": "https://linkedin.com/in/elena-rodriguez-laser",
            "researchgate": "https://researchgate.net/profile/elena-rodriguez",
            "email": "e.rodriguez@lps.com"
        }
    ]
    
    # Add category-specific authors
    category_authors = {
        "metals": [
            {
                "name": "Dr. James Patterson",
                "title": "Metallurgy and Corrosion Expert",
                "affiliation": "Steel Research Foundation",
                "degree": "Ph.D. Metallurgical Engineering",
                "experience": "18",
                "specialization": "Metal Surface Treatment",
                "avatar": "https://example.com/avatars/james-patterson.jpg",
                "linkedin": "https://linkedin.com/in/james-patterson-metal",
                "researchgate": "https://researchgate.net/profile/james-patterson",
                "email": "j.patterson@steel.org"
            }
        ],
        "ceramics": [
            {
                "name": "Dr. Lisa Wang",
                "title": "Advanced Ceramics Researcher",
                "affiliation": "Ceramic Technology Center",
                "degree": "Ph.D. Ceramic Engineering",
                "experience": "14",
                "specialization": "Technical Ceramics",
                "avatar": "https://example.com/avatars/lisa-wang.jpg",
                "linkedin": "https://linkedin.com/in/lisa-wang-ceramics",
                "researchgate": "https://researchgate.net/profile/lisa-wang",
                "email": "l.wang@ceramics.edu"
            }
        ],
        "composites": [
            {
                "name": "Dr. Robert Kumar",
                "title": "Composite Materials Specialist",
                "affiliation": "Aerospace Composites Lab",
                "degree": "Ph.D. Composite Engineering",
                "experience": "16",
                "specialization": "Fiber Reinforced Composites",
                "avatar": "https://example.com/avatars/robert-kumar.jpg",
                "linkedin": "https://linkedin.com/in/robert-kumar-composites",
                "researchgate": "https://researchgate.net/profile/robert-kumar",
                "email": "r.kumar@aerolab.edu"
            }
        ],
        "stones": [
            {
                "name": "Dr. Maria Fernandez",
                "title": "Stone Conservation Expert",
                "affiliation": "Heritage Preservation Institute",
                "degree": "Ph.D. Materials Conservation",
                "experience": "22",
                "specialization": "Stone Restoration",
                "avatar": "https://example.com/avatars/maria-fernandez.jpg",
                "linkedin": "https://linkedin.com/in/maria-fernandez-conservation",
                "researchgate": "https://researchgate.net/profile/maria-fernandez",
                "email": "m.fernandez@heritage.org"
            }
        ]
    }
    
    # Combine base authors with category-specific ones
    all_authors = base_authors.copy()
    if category.lower() in category_authors:
        all_authors.extend(category_authors[category.lower()])
    
    return all_authors


def generate_mock_author_variations(material_name: str = "", category: str = "", count: int = 3) -> list:
    """
    Generate multiple mock author variations.
    
    Args:
        material_name: Name of the material
        category: Material category
        count: Number of variations to generate
        
    Returns:
        list: List of mock author variations
    """
    return [generate_mock_author(material_name, category) for _ in range(count)]


def generate_mock_structured_author(material_name: str = "", category: str = "") -> dict:
    """
    Generate mock author as structured data.
    
    Args:
        material_name: Name of the material
        category: Material category
        
    Returns:
        dict: Dictionary with organized author data
    """
    if not material_name:
        material_name = "Industrial Material"
    
    authors = get_author_profiles(category)
    author = random.choice(authors)
    
    days_ago = random.randint(1, 365)
    pub_date = (datetime.now() - timedelta(days=days_ago)).isoformat()
    
    return {
        "author": {
            "name": author['name'],
            "title": author['title'],
            "affiliation": author['affiliation'],
            "credentials": author['degree'],
            "experience_years": int(author['experience']),
            "specialization": author['specialization'],
            "contact": {
                "email": author['email'],
                "linkedin": author['linkedin'],
                "researchgate": author['researchgate']
            }
        },
        "publication": {
            "published_date": pub_date,
            "material_focus": material_name,
            "category": category,
            "estimated_reading_time": f"{random.randint(5, 15)} minutes"
        }
    }
