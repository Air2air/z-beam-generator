#!/usr/bin/env python3
"""
Enhanced JSON-LD Component Generator

Generates comprehensive JSON-LD structured data using dynamic frontmatter substitution.
Uses multi-schema approach with Article, Product, HowTo, BreadcrumbList, WebPage, Website, and FAQPage.
"""

import json
import logging
import re
from datetime import datetime
from typing import Dict, Optional

from generators.component_generators import ComponentResult

logger = logging.getLogger(__name__)


class EnhancedJsonldGenerator:
    """
    Enhanced JSON-LD generator using comprehensive schema.org structures.
    
    Creates multiple interconnected schema types with dynamic placeholder
    replacement from frontmatter data.
    """

    def __init__(self):
        self.component_type = "jsonld"
        self.file_extension = ".yaml"
        
        # Load the comprehensive schema template
        self.schema_template = self._load_schema_template()

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """Generate comprehensive JSON-LD using frontmatter data"""
        try:
            # Load frontmatter data if not provided
            if frontmatter_data is None:
                from utils.file_ops.frontmatter_loader import load_frontmatter_data
                frontmatter_data = load_frontmatter_data(material_name) or {}
            
            # Generate JSON-LD content with dynamic substitution
            jsonld_content = self._build_enhanced_jsonld(material_name, frontmatter_data, author_info)
            
            return ComponentResult(
                component_type=self.component_type,
                content=jsonld_content,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Enhanced JSON-LD generation failed for {material_name}: {e}")
            return ComponentResult(
                component_type=self.component_type,
                content="",
                success=False,
                error_message=str(e)
            )

    def _load_schema_template(self) -> Dict:
        """Load the comprehensive JSON-LD schema template"""
        try:
            import os
            schema_path = os.path.join(os.path.dirname(__file__), '../../schemas/json-ld.json')
            with open(schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load JSON-LD schema template: {e}")
            # Fallback to minimal schema
            return {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": "{{ARTICLE_TITLE}}",
                "description": "{{ARTICLE_DESCRIPTION}}"
            }

    def _build_enhanced_jsonld(self, material_name: str, frontmatter_data: Dict, author_info: Optional[Dict]) -> str:
        """Build comprehensive JSON-LD with dynamic substitution"""
        
        # Create substitution mapping
        substitutions = self._build_substitution_mapping(material_name, frontmatter_data, author_info)
        
        # Convert template to JSON string for substitution
        template_json = json.dumps(self.schema_template, ensure_ascii=False)
        
        # Apply substitutions
        for placeholder, value in substitutions.items():
            template_json = template_json.replace(f"{{{{{placeholder}}}}}", str(value))
        
        # Parse back to dict for validation and formatting
        try:
            jsonld_data = json.loads(template_json)
            return json.dumps(jsonld_data, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error after substitution: {e}")
            # Return template with basic substitutions
            raise RuntimeError(f"JSON-LD generation failed: {str(e)}. No fallback generation allowed.")

    def _build_substitution_mapping(self, material_name: str, frontmatter_data: Dict, author_info: Optional[Dict]) -> Dict[str, str]:
        """Build mapping of placeholders to actual values"""
        
        # Material processing
        material_title = material_name.title()
        slug = self._create_slug(material_name)
        
        # Extract frontmatter data safely
        description = frontmatter_data.get("description", f"Comprehensive guide to laser cleaning {material_title}")
        category = frontmatter_data.get("category", "material").title()
        keywords = self._extract_keywords(material_name, frontmatter_data)
        
        # Technical specifications
        tech_specs = frontmatter_data.get("technicalSpecifications", {})
        if isinstance(tech_specs, dict):
            wavelength = tech_specs.get("wavelength", "1064")
            power_range = tech_specs.get("powerRange", "100-500")
        else:
            wavelength = "1064"
            power_range = "100-500"
        
        # Machine settings
        machine_settings = frontmatter_data.get("machineSettings", {})
        if isinstance(machine_settings, dict):
            laser_power = machine_settings.get("power", power_range.split('-')[0] if '-' in power_range else power_range)
            laser_type = machine_settings.get("type", "Fiber Laser")
        else:
            laser_power = power_range.split('-')[0] if '-' in power_range else power_range
            laser_type = "Fiber Laser"
        
        # Material properties
        properties = frontmatter_data.get("properties", {})
        if isinstance(properties, dict):
            density = properties.get("density", "N/A")
            thermal_conductivity = properties.get("thermalConductivity", "N/A")
            melting_point = properties.get("meltingPoint", "N/A")
        else:
            density = thermal_conductivity = melting_point = "N/A"
        
        # Applications
        applications = self._extract_applications(frontmatter_data)
        
        # Author information
        author_name = self._extract_author_name(frontmatter_data, author_info)
        
        # Date handling
        now = datetime.now()
        date_published = now.strftime("%Y-%m-%d")
        date_modified = date_published
        
        # Create comprehensive mapping
        return {
            # Basic identifiers
            "SLUG": slug,
            "MATERIAL_NAME": material_title,
            "ARTICLE_TITLE": f"{material_title} Laser Cleaning Guide",
            "ARTICLE_DESCRIPTION": description[:160] + "..." if len(description) > 160 else description,
            "MATERIAL_DESCRIPTION": f"Industrial-grade {material_title} for precision laser cleaning applications",
            
            # Categorization
            "MATERIAL_CATEGORY": category.lower(),
            "MATERIAL_CATEGORY_DISPLAY": category,
            "ARTICLE_CATEGORY": "Laser Cleaning",
            "PRIMARY_APPLICATION": applications[0] if applications else "Industrial Cleaning",
            "SECONDARY_APPLICATION": applications[1] if len(applications) > 1 else "Surface Treatment",
            
            # Technical parameters
            "LASER_WAVELENGTH": str(wavelength).replace("nm", ""),
            "LASER_POWER": str(laser_power).replace("W", ""),
            "LASER_TYPE": laser_type,
            
            # Material properties
            "DENSITY_VALUE": str(density).replace("g/cm³", "").replace("g/cm3", "").strip(),
            "DENSITY_UNIT": "g/cm³",
            "DENSITY_UNIT_CODE": "GRM",
            "THERMAL_CONDUCTIVITY": str(thermal_conductivity).replace("W/m·K", "").replace("W/mK", "").strip(),
            "THERMAL_UNIT": "W/m·K",
            "THERMAL_UNIT_CODE": "WMK",
            "MELTING_POINT": str(melting_point).replace("°C", "").replace("C", "").strip(),
            "MELTING_POINT_UNIT": "°C",
            "MELTING_POINT_UNIT_CODE": "CEL",
            
            # Process timing
            "PROCESS_TIME": "15",
            "CLEANING_TIME": "10",
            
            # Content metadata
            "KEYWORDS": keywords,
            "WORD_COUNT": "850",  # Typical article length
            "AUTHOR_NAME": author_name,
            "DATE_PUBLISHED": date_published,
            "DATE_MODIFIED": date_modified,
        }

    def _create_slug(self, material_name: str) -> str:
        """Create URL-friendly slug from material name"""
        slug = material_name.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        return slug.strip('-')

    def _extract_keywords(self, material_name: str, frontmatter_data: Dict) -> str:
        """Extract and format keywords from frontmatter"""
        keywords = [
            material_name.lower(),
            f"{material_name.lower()} laser cleaning",
            "laser ablation",
            "surface treatment",
            "industrial cleaning"
        ]
        
        # Add industry tags if available
        industry_tags = frontmatter_data.get("industryTags", [])
        if isinstance(industry_tags, list):
            keywords.extend([tag.lower() for tag in industry_tags[:3]])
        
        # Add existing keywords
        existing_keywords = frontmatter_data.get("keywords", "")
        if isinstance(existing_keywords, str) and existing_keywords:
            keywords.extend([k.strip().lower() for k in existing_keywords.split(",") if k.strip()])
        
        return ", ".join(list(set(keywords))[:12])  # Limit to 12 unique keywords

    def _extract_applications(self, frontmatter_data: Dict) -> list:
        """Extract primary applications from frontmatter"""
        applications = frontmatter_data.get("applications", [])
        app_list = []
        
        if isinstance(applications, list):
            for app in applications[:3]:  # Take first 3 applications
                if isinstance(app, str):
                    if ":" in app:
                        # Handle "Industry: Application" format
                        app_clean = app.split(":")[1].strip()
                    else:
                        app_clean = app.strip()
                    app_list.append(app_clean.title())
                elif isinstance(app, dict):
                    # Handle dict format if present
                    app_name = app.get("name", app.get("application", "Industrial Processing"))
                    app_list.append(str(app_name).title())
        
        return app_list if app_list else ["Industrial Cleaning", "Surface Treatment"]

    def _extract_author_name(self, frontmatter_data: Dict, author_info: Optional[Dict]) -> str:
        """Extract author name from available sources"""
        # Try author_info first
        if author_info and isinstance(author_info, dict):
            if "name" in author_info:
                return str(author_info["name"])
        
        # Try frontmatter author
        author_obj = frontmatter_data.get("author", {})
        if isinstance(author_obj, dict) and "name" in author_obj:
            return str(author_obj["name"])
        
        # Try direct author field
        author = frontmatter_data.get("author", "")
        if isinstance(author, str) and author:
            return author
        
        # Fail-fast: Author information required - no fallback
        raise ValueError("Author information required in frontmatter or author_info - no fallback allowed")

    # Fallback method removed - fail-fast architecture requires complete JSON-LD generation