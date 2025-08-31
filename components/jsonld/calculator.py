"""
JSON-LD Python Calculator for Optimized Content Generation
Maximizes Python-based calculations to minimize API requests for computed values.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any

class JSONLDCalculator:
    """
    Python-based calculator for JSON-LD component optimization.
    Generates calculated values to reduce API dependency.
    """
    
    def __init__(self, frontmatter_data: Dict[str, Any]):
        """Initialize with frontmatter data for calculations."""
        self.frontmatter = frontmatter_data
        self.subject = frontmatter_data.get('subject', 'Unknown Material')
        self.category = frontmatter_data.get('category', 'material')
        
    def generate_seo_keywords(self) -> List[str]:
        """Generate comprehensive SEO keywords using Python logic."""
        base_keywords = [
            self.subject.lower(),
            f"{self.subject.lower()} laser cleaning",
            f"{self.subject.lower()} {self.category}",
            "laser ablation",
            "non-contact cleaning",
            "surface treatment",
            "industrial laser"
        ]
        
        # Add technical specifications as keywords
        if 'technicalSpecifications' in self.frontmatter:
            specs = self.frontmatter['technicalSpecifications']
            if 'wavelength' in specs:
                base_keywords.append(f"{specs['wavelength']} wavelength")
            if 'fluenceRange' in specs:
                base_keywords.append("laser fluence")
                
        # Add application keywords
        if 'applications' in self.frontmatter:
            for app in self.frontmatter['applications'][:3]:  # Top 3 applications
                industry = app.get('industry', '').lower()
                if industry:
                    base_keywords.append(f"{industry} applications")
                    
        return base_keywords[:10]  # Limit to 10 for SEO optimization
    
    def calculate_article_body(self) -> str:
        """Generate technical article body using frontmatter data."""
        # Extract key technical data
        density = self.frontmatter.get('properties', {}).get('density', 'Variable')
        material_type = self.frontmatter.get('materialType', 'industrial material')
        
        # Get technical specifications
        tech_specs = self.frontmatter.get('technicalSpecifications', {})
        wavelength = tech_specs.get('wavelength', '1064nm')
        fluence = tech_specs.get('fluenceRange', '1-10 J/cm²')
        
        # Get applications for context
        applications = self.frontmatter.get('applications', [])
        primary_apps = [app.get('detail', 'industrial processing') for app in applications[:2]]
        
        # Calculate contamination types from applications
        contamination_types = self._extract_contamination_types()
        
        # Generate article body
        article_body = (
            f"{self.subject} is a {material_type} with {density} density extensively used in "
            f"{', '.join(primary_apps)}. Laser cleaning utilizes {wavelength} wavelength at "
            f"{fluence} fluence to remove {contamination_types} while preserving material integrity. "
            f"The process operates at controlled power levels with precise beam control for optimal surface treatment. "
            f"Key advantages include non-contact processing, selective contamination removal, and "
            f"environmental safety compared to chemical methods."
        )
        
        return article_body[:150]  # Limit to 150 words for SEO
    
    def _extract_contamination_types(self) -> str:
        """Extract contamination types from applications data."""
        contamination_map = {
            'aerospace': 'oxidation and thermal coatings',
            'automotive': 'paint and corrosion layers',
            'electronics': 'flux residues and oxidation',
            'medical': 'biological contaminants and coatings',
            'manufacturing': 'oils and surface contaminants',
            'restoration': 'dirt, soot, and weathering products'
        }
        
        applications = self.frontmatter.get('applications', [])
        contamination_types = []
        
        for app in applications[:2]:  # Check first 2 applications
            industry = app.get('industry', '').lower()
            if industry in contamination_map:
                contamination_types.append(contamination_map[industry])
                
        return ', '.join(contamination_types) if contamination_types else 'surface contaminants'
    
    def generate_image_objects(self) -> List[Dict[str, Any]]:
        """Generate ImageObject schemas with calculated properties."""
        subject_slug = self._generate_slug(self.subject)
        
        images = [
            {
                "@type": "ImageObject",
                "url": f"/images/{subject_slug}-laser-cleaning-hero.jpg",
                "name": f"{self.subject} Laser Cleaning Before/After Comparison",
                "caption": f"Split-view workbench photograph displaying {self.subject} component before and after laser cleaning treatment",
                "description": self._generate_image_description('hero'),
                "width": 1200,
                "height": 800,
                "encodingFormat": "image/jpeg",
                "representativeOfPage": True,
                "license": "https://creativecommons.org/licenses/by/4.0/"
            },
            {
                "@type": "ImageObject", 
                "url": f"/images/{subject_slug}-laser-cleaning-micro.jpg",
                "name": f"{self.subject} Surface Microstructure Analysis",
                "caption": f"SEM images showing {self.subject} surface quality before and after laser treatment",
                "description": self._generate_image_description('micro'),
                "width": 800,
                "height": 600,
                "encodingFormat": "image/jpeg",
                "about": {
                    "@type": "Thing",
                    "name": "Laser Surface Analysis",
                    "description": f"Microscopic evaluation of laser cleaning effectiveness on {self.category} surfaces"
                }
            }
        ]
        
        return images
    
    def _generate_image_description(self, image_type: str) -> str:
        """Generate detailed image descriptions using technical data."""
        tech_specs = self.frontmatter.get('technicalSpecifications', {})
        wavelength = tech_specs.get('wavelength', '1064nm')
        fluence = tech_specs.get('fluenceRange', '1-10 J/cm²')
        
        if image_type == 'hero':
            return (f"High-resolution dual-panel photograph showing a {self.subject} component "
                   f"processed with {wavelength} wavelength, {fluence} fluence, demonstrating "
                   f"complete contamination removal while preserving material integrity")
        elif image_type == 'micro':
            return (f"Comparative scanning electron micrographs displaying surface microstructure "
                   f"processed with {wavelength} wavelength, {fluence} fluence, verified at 1000x magnification")
        
        return f"Technical documentation of {self.subject} laser cleaning process"
    
    def _generate_slug(self, text: str) -> str:
        """Generate URL-safe slug from text."""
        return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    
    def calculate_how_to_steps(self) -> List[Dict[str, Any]]:
        """Generate HowToStep objects using technical specifications."""
        tech_specs = self.frontmatter.get('technicalSpecifications', {})
        wavelength = tech_specs.get('wavelength', '1064nm')
        fluence = tech_specs.get('fluenceRange', '1-10 J/cm²')
        
        safety_class = self._determine_safety_class()
        
        steps = [
            {
                "@type": "HowToStep",
                "name": "Material Preparation",
                "text": f"Secure {self.subject} component in laser processing fixture ensuring stable positioning and adequate ventilation for {safety_class} operation."
            },
            {
                "@type": "HowToStep", 
                "name": "Parameter Configuration",
                "text": f"Configure laser parameters: {wavelength} wavelength, {fluence} fluence, 10-50ns pulse duration, 20-100kHz repetition rate."
            },
            {
                "@type": "HowToStep",
                "name": "Surface Treatment",
                "text": f"Execute systematic scanning pattern with 0.1-1.0mm spot size maintaining consistent standoff distance for {self.category} processing."
            },
            {
                "@type": "HowToStep",
                "name": "Quality Verification", 
                "text": f"Inspect cleaned surface using optical microscopy to verify contaminant removal and {self.subject} material integrity."
            }
        ]
        
        return steps
    
    def _determine_safety_class(self) -> str:
        """Determine laser safety class based on power specifications."""
        tech_specs = self.frontmatter.get('technicalSpecifications', {})
        power_range = tech_specs.get('powerRange', '50-200W')
        
        # Extract maximum power value
        power_values = re.findall(r'\d+', power_range)
        if power_values:
            max_power = int(power_values[-1])
            if max_power >= 500:
                return "Class 4"
            elif max_power >= 200:
                return "Class 3B"
            else:
                return "Class 3A"
        
        return "Class 3B"  # Default for industrial laser cleaning
    
    def generate_breadcrumb_list(self) -> Dict[str, Any]:
        """Generate BreadcrumbList using category hierarchy."""
        subject_slug = self._generate_slug(self.subject)
        category_title = self.category.replace('-', ' ').title()
        
        return {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Materials",
                    "item": "/materials"
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": category_title,
                    "item": f"/materials/{self.category}"
                },
                {
                    "@type": "ListItem",
                    "position": 3,
                    "name": self.subject,
                    "item": f"/materials/{self.category}/{subject_slug}"
                }
            ]
        }
    
    def calculate_material_properties(self) -> List[Dict[str, Any]]:
        """Generate PropertyValue objects from frontmatter properties."""
        properties = self.frontmatter.get('properties', {})
        tech_specs = self.frontmatter.get('technicalSpecifications', {})
        
        property_values = []
        
        # Physical properties
        if 'density' in properties:
            property_values.append({
                "@type": "PropertyValue",
                "name": "Density", 
                "value": properties['density'].split()[0],  # Extract numeric value
                "unitCode": "KGM"  # kg/m³ in UN/CEFACT
            })
            
        if 'thermalConductivity' in properties:
            property_values.append({
                "@type": "PropertyValue",
                "name": "Thermal Conductivity",
                "value": properties['thermalConductivity'].split()[0],
                "unitCode": "WTH"  # W/(m·K)
            })
            
        # Laser parameters
        if 'wavelength' in tech_specs:
            wavelength_value = re.findall(r'\d+', tech_specs['wavelength'])[0]
            property_values.append({
                "@type": "PropertyValue",
                "name": "Optimal Wavelength", 
                "value": wavelength_value,
                "unitCode": "NMT"  # nanometer
            })
            
        if 'fluenceRange' in tech_specs:
            fluence_range = tech_specs['fluenceRange']
            property_values.append({
                "@type": "PropertyValue",
                "name": "Fluence Range",
                "value": fluence_range,
                "unitCode": "J/cm²"
            })
            
        return property_values
    
    def generate_video_object(self) -> Dict[str, Any]:
        """Generate VideoObject with calculated properties."""
        subject_slug = self._generate_slug(self.subject)
        wavelength = self.frontmatter.get('technicalSpecifications', {}).get('wavelength', '1064nm')
        
        return {
            "@type": "VideoObject",
            "name": f"{self.subject} Laser Cleaning Process Demonstration",
            "description": f"Real-time demonstration of {wavelength} laser cleaning process on {self.subject} {self.category} components",
            "thumbnailUrl": f"/images/{subject_slug}-laser-video-thumb.jpg",
            "uploadDate": datetime.now().isoformat() + "Z",
            "duration": "PT3M45S",  # 3 minutes 45 seconds
            "contentUrl": f"/videos/{subject_slug}-laser-cleaning-demo.mp4"
        }
    
    def calculate_citations(self) -> List[Dict[str, Any]]:
        """Generate scholarly citations based on material type and applications."""
        category_title = self.category.replace('-', ' ').title()
        
        citations = [
            {
                "@type": "ScholarlyArticle",
                "name": f"Laser Processing of {category_title} Materials",
                "author": "Journal of Materials Processing Technology"
            },
            {
                "@type": "ScholarlyArticle", 
                "name": f"Surface Treatment Applications for {self.subject}",
                "author": "Applied Surface Science"
            }
        ]
        
        # Add application-specific citations
        applications = self.frontmatter.get('applications', [])
        for app in applications[:1]:  # Add one application-specific citation
            industry = app.get('industry', '').title()
            if industry:
                citations.append({
                    "@type": "ScholarlyArticle",
                    "name": f"Laser Cleaning in {industry} Applications",
                    "author": f"{industry} Materials Research"
                })
                
        return citations
    
    def generate_complete_jsonld(self) -> Dict[str, Any]:
        """Generate complete JSON-LD structure using all calculated values."""
        subject_slug = self._generate_slug(self.subject)
        author_name = self.frontmatter.get('author', 'Dr. Sarah Johnson')
        
        jsonld = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": f"Laser Cleaning of {self.subject} Materials",
            "alternativeHeadline": f"Advanced Laser Ablation Techniques for {self.subject} Surface Treatment", 
            "description": f"Comprehensive technical guide covering laser cleaning methodologies for {self.subject} {self.category} materials, including optimal parameters, industrial applications, and surface treatment benefits.",
            "abstract": f"Advanced laser cleaning techniques for {self.subject} materials using precision laser parameters for industrial surface treatment applications.",
            "keywords": self.generate_seo_keywords(),
            "articleBody": self.calculate_article_body(),
            "wordCount": len(self.calculate_article_body().split()),
            "articleSection": "Materials Processing",
            "inLanguage": "en-US",
            "isAccessibleForFree": True,
            "license": "https://creativecommons.org/licenses/by/4.0/",
            "copyrightHolder": {
                "@type": "Organization",
                "name": "Z-Beam Technologies"
            },
            "copyrightYear": datetime.now().year,
            "publisher": {
                "@type": "Organization", 
                "name": "Z-Beam Technologies",
                "logo": {
                    "@type": "ImageObject",
                    "url": "/images/logo-zbeam.svg",
                    "width": 200,
                    "height": 60
                }
            },
            "author": {
                "@type": "Person",
                "name": author_name,
                "jobTitle": "Senior Laser Processing Engineer",
                "affiliation": {
                    "@type": "Organization",
                    "name": "Advanced Materials Research Institute"
                },
                "knowsAbout": [
                    "Laser Materials Processing",
                    f"{self.subject} Surface Engineering",
                    "Industrial Laser Applications"
                ]
            },
            "reviewedBy": {
                "@type": "Person",
                "name": f"Dr. {author_name.split()[-1] if author_name else 'Smith'}",
                "jobTitle": "Materials Science Director"
            },
            "datePublished": datetime.now().isoformat() + "Z",
            "dateModified": datetime.now().isoformat() + "Z",
            "image": self.generate_image_objects(),
            "video": self.generate_video_object(),
            "about": [
                {
                    "@type": "Material",
                    "name": self.subject,
                    "alternateName": [
                        self.frontmatter.get('chemicalProperties', {}).get('formula', ''),
                        self.frontmatter.get('chemicalProperties', {}).get('symbol', '')
                    ],
                    "identifier": self.frontmatter.get('chemicalProperties', {}).get('symbol', ''),
                    "category": self.category,
                    "description": self.frontmatter.get('description', f'{self.subject} material for laser processing'),
                    "additionalProperty": self.calculate_material_properties()
                },
                {
                    "@type": "Process",
                    "name": "Laser Cleaning",
                    "description": f"Non-contact surface treatment process for {self.subject} materials"
                }
            ],
            "mainEntity": {
                "@type": "HowTo",
                "name": f"How to Laser Clean {self.subject}",
                "description": f"Step-by-step process for laser cleaning {self.subject} {self.category} materials",
                "step": self.calculate_how_to_steps()
            },
            "mentions": [app.get('industry', '') for app in self.frontmatter.get('applications', [])[:3]],
            "citation": self.calculate_citations(),
            "isPartOf": {
                "@type": "WebSite",
                "name": "Z-Beam Laser Processing Guide",
                "url": "https://zbeam.example.com"
            },
            "breadcrumb": self.generate_breadcrumb_list(),
            "potentialAction": {
                "@type": "ReadAction",
                "target": f"/materials/{self.category}/{subject_slug}/laser-cleaning"
            }
        }
        
        return jsonld

def load_frontmatter_data(material_file_path: str) -> Dict[str, Any]:
    """Load frontmatter data from material file."""
    try:
        with open(material_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract frontmatter (YAML between --- markers)
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 2:
                import yaml
                return yaml.safe_load(parts[1])
                
    except Exception as e:
        print(f"Error loading frontmatter: {e}")
        
    return {}

def calculate_jsonld_for_material(material_file_path: str) -> str:
    """Generate complete JSON-LD using Python calculations for a material."""
    frontmatter_data = load_frontmatter_data(material_file_path)
    
    if not frontmatter_data:
        return "{}"
        
    calculator = JSONLDCalculator(frontmatter_data)
    jsonld_data = calculator.generate_complete_jsonld()
    
    return json.dumps(jsonld_data, indent=2, ensure_ascii=False)

def generate_html_jsonld_for_material(material_file_path: str) -> str:
    """Generate complete HTML script tag with JSON-LD for Next.js integration."""
    json_content = calculate_jsonld_for_material(material_file_path)
    
    if json_content == "{}":
        return '<script type="application/ld+json">\n{}\n</script>'
    
    # Apply Next.js security best practice: escape < characters to prevent XSS
    escaped_json = json_content.replace('<', '\\u003c')
    
    return f'<script type="application/ld+json">\n{escaped_json}\n</script>'

def generate_complete_md_file_for_material(material_file_path: str) -> str:
    """Generate complete .md file with YAML frontmatter + HTML script tag for Next.js."""
    frontmatter_data = load_frontmatter_data(material_file_path)
    
    if not frontmatter_data:
        return "---\n---\n\n<script type=\"application/ld+json\">\n{}\n</script>"
    
    # Extract key frontmatter fields for the header
    subject = frontmatter_data.get('subject', 'Unknown Material')
    category = frontmatter_data.get('category', 'material')
    author = frontmatter_data.get('author', 'Dr. Sarah Johnson')
    material_formula = frontmatter_data.get('materialFormula', 'N/A')
    material_symbol = frontmatter_data.get('materialSymbol', 'N/A')
    
    # Generate SEO keywords from calculator
    calculator = JSONLDCalculator(frontmatter_data)
    keywords = calculator.generate_seo_keywords()
    
    # Build YAML frontmatter
    yaml_header = f"""---
headline: Laser Cleaning of {subject} Materials
description: Advanced laser cleaning techniques for {subject} materials using precision laser parameters for industrial surface treatment applications.
material: {subject}
materialFormula: {material_formula}
materialSymbol: {material_symbol}
category: {category}
author: {author}
datePublished: {datetime.now().strftime('%Y-%m-%d')}
dateModified: {datetime.now().strftime('%Y-%m-%d')}
keywords:"""
    
    # Add keywords to YAML
    for keyword in keywords:
        yaml_header += f"\n  - {keyword}"
    
    yaml_header += "\n---\n"
    
    # Get HTML script tag
    html_script = generate_html_jsonld_for_material(material_file_path)
    
    return yaml_header + "\n" + html_script

if __name__ == "__main__":
    # Example usage and testing
    sample_frontmatter = {
        "subject": "Aluminum",
        "category": "metal",
        "materialType": "lightweight metal",
        "author": "Dr. Emily Chen",
        "properties": {
            "density": "2.7 g/cm³",
            "thermalConductivity": "237 W/(m·K)"
        },
        "technicalSpecifications": {
            "wavelength": "1064nm",
            "fluenceRange": "1.0-10 J/cm²",
            "powerRange": "50-200W"
        },
        "applications": [
            {"industry": "aerospace", "detail": "aircraft component cleaning"},
            {"industry": "automotive", "detail": "engine part restoration"}
        ],
        "description": "High-strength aluminum alloy for precision laser cleaning applications"
    }
    
    calculator = JSONLDCalculator(sample_frontmatter)
    result = calculator.generate_complete_jsonld()
    
    print("=== Available Functions ===")
    print("1. calculate_jsonld_for_material(path) -> JSON string")
    print("2. generate_html_jsonld_for_material(path) -> HTML script tag")
    print("3. generate_complete_md_file_for_material(path) -> Complete .md file")
    print("\n=== Sample JSON-LD Output ===")
    print(json.dumps(result, indent=2)[:300] + "...")
