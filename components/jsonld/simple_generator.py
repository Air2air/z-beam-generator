#!/usr/bin/env python3
"""
Simplified JSON-LD Component Generator

Generates JSON-LD structured data using ONLY frontmatter data.
Bypasses complex template processing to ensure reliability.
"""

import json
import logging
from typing import Dict, Optional

from generators.component_generators import ComponentResult

logger = logging.getLogger(__name__)


class SimpleJsonldGenerator:
    """
    Simplified JSON-LD generator that only uses frontmatter data.
    
    Creates Schema.org Article structured data for laser cleaning materials
    using frontmatter fields directly without complex template processing.
    """

    def __init__(self):
        self.component_type = "jsonld"
        self.file_extension = ".yaml"

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """Generate JSON-LD using only frontmatter data"""
        try:
            # Load frontmatter data if not provided
            if frontmatter_data is None:
                from utils.file_ops.frontmatter_loader import load_frontmatter_data
                frontmatter_data = load_frontmatter_data(material_name) or {}
            
            # Generate JSON-LD content
            jsonld_content = self._build_simple_jsonld(material_name, frontmatter_data)
            
            return ComponentResult(
                component_type=self.component_type,
                content=jsonld_content,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Simple JSON-LD generation failed for {material_name}: {e}")
            return ComponentResult(
                component_type=self.component_type,
                content="",
                success=False,
                error_message=str(e)
            )

    def _build_simple_jsonld(self, material_name: str, frontmatter_data: Dict) -> str:
        """Build basic JSON-LD structure from frontmatter data"""
        
        # Material name in title case
        material_title = material_name.title()
        
        # Extract basic data from frontmatter
        category = frontmatter_data.get("category", "material")
        description = frontmatter_data.get("description", f"Laser cleaning of {material_title}")
        keywords = frontmatter_data.get("keywords", "")
        
        # Extract technical specifications
        tech_specs = frontmatter_data.get("technicalSpecifications", {})
        wavelength = tech_specs.get("wavelength", "1064nm") if isinstance(tech_specs, dict) else "1064nm"
        
        # Extract properties
        properties = frontmatter_data.get("properties", {})
        density = properties.get("density", "") if isinstance(properties, dict) else ""
        
        # Extract applications (handle both string list and dict list formats)
        applications = frontmatter_data.get("applications", [])
        app_keywords = []
        if isinstance(applications, list):
            for app in applications[:3]:
                if isinstance(app, str) and ":" in app:
                    industry = app.split(":")[0].strip()
                    app_keywords.append(industry.lower())
        
        # Extract author information
        author_obj = frontmatter_data.get("author", {})
        author_name = author_obj.get("name", "Laser Technology Specialist") if isinstance(author_obj, dict) else "Laser Technology Specialist"
        
        # Build JSON-LD structure
        jsonld_data = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": f"{material_title} Laser Cleaning",
            "alternativeHeadline": f"Advanced Laser Ablation Techniques for {material_title}",
            "description": description[:200] + "..." if len(description) > 200 else description,
            "keywords": self._build_keywords(material_name, category, app_keywords, keywords),
            "articleSection": "Materials Processing",
            "inLanguage": "en-US",
            "isAccessibleForFree": True,
            "author": {
                "@type": "Person",
                "name": author_name
            },
            "about": {
                "@type": "Material",
                "name": material_title,
                "category": category,
                "density": density,
                "description": f"{material_title} material for laser cleaning applications"
            },
            "mainEntity": {
                "@type": "HowTo",
                "name": f"How to Laser Clean {material_title}",
                "description": f"Process for laser cleaning {material_title} using {wavelength} wavelength",
                "step": [
                    {
                        "@type": "HowToStep",
                        "name": "Material Preparation",
                        "text": f"Secure {material_title} component in laser processing fixture"
                    },
                    {
                        "@type": "HowToStep", 
                        "name": "Parameter Configuration",
                        "text": f"Configure laser parameters: {wavelength} wavelength"
                    },
                    {
                        "@type": "HowToStep",
                        "name": "Surface Treatment",
                        "text": f"Execute systematic scanning pattern for {material_title} processing"
                    }
                ]
            },
            "datePublished": "2025-09-20",
            "dateModified": "2025-09-20",
            "publisher": {
                "@type": "Organization",
                "name": "Z-Beam"
            }
        }
        
        # Convert to JSON format
        return json.dumps(jsonld_data, indent=2, ensure_ascii=False)

    def _build_keywords(self, material_name: str, category: str, app_keywords: list, existing_keywords: str) -> list:
        """Build keyword list from various sources"""
        keywords = [
            f"{material_name.lower()}",
            f"{material_name.lower()} laser cleaning",
            "laser ablation",
            "surface treatment",
            "industrial laser",
            f"{category} laser cleaning"
        ]
        
        # Add application keywords
        keywords.extend([f"{app} laser cleaning" for app in app_keywords])
        
        # Add existing keywords if it's a string
        if isinstance(existing_keywords, str):
            keywords.extend([k.strip() for k in existing_keywords.split(",") if k.strip()])
        
        # Remove duplicates and return first 15
        return list(set(keywords))[:15]
