"""
Metatags Python Calculator for Optimized Content Generation
Maximizes Python-based calculations to minimize API requests and enhance SEO performance.
Follows current best practice standards for comprehensive meta tag implementation.
"""

import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import yaml

import html



def sanitize_content(content: str) -> str:
    """Sanitize content to prevent XSS and remove dangerous patterns."""
    if not content:
        return ""

    # Remove HTML tags and dangerous patterns
    content = re.sub(r"<[^>]+>", "", content)  # Remove HTML tags
    content = re.sub(
        r"javascript:", "", content, flags=re.IGNORECASE
    )  # Remove javascript:
    content = re.sub(
        r"on\w+\s*=", "", content, flags=re.IGNORECASE
    )  # Remove event handlers
    content = re.sub(
        r"drop\s+table[^;]*", "", content, flags=re.IGNORECASE
    )  # Remove SQL injection
    content = re.sub(r";--", "", content)  # Remove SQL comment injection
    content = re.sub(
        r"alert\s*\(", "", content, flags=re.IGNORECASE
    )  # Remove alert() calls
    content = html.escape(content)  # HTML encode remaining content

    return content.strip()


class MetatagsCalculator:
    """
    Python-based calculator for metatags component optimization.
    Generates comprehensive meta tags following current SEO best practices.
    """

    def __init__(self, frontmatter_data: Dict[str, Any]):
        """Initialize with frontmatter data for calculations."""
        self.frontmatter = frontmatter_data
        # Sanitize key fields to prevent XSS
        self.subject = sanitize_content(
            frontmatter_data.get("subject", "Unknown Material")
        )
        self.category = sanitize_content(frontmatter_data.get("category", "material"))

    def calculate_meta_title(self) -> str:
        """Calculate optimized meta title (45-65 characters ideal)."""
        base_title = f"Laser Cleaning {self.subject} - Complete Technical Guide"

        # Add specialization based on category
        specializations = {
            "metal": "Industrial Processing Solutions",
            "ceramic": "Precision Restoration Methods",
            "stone": "Heritage Conservation Techniques",
            "glass": "Optical Applications Guide",
            "composite": "Advanced Materials Processing",
            "wood": "Eco-Friendly Treatment Methods",
            "semiconductor": "Electronics Manufacturing Guide",
        }

        specialization = specializations.get(self.category, "Professional Processing")
        full_title = f"{base_title} for {specialization}"

        # Ensure title is within optimal length (45-65 chars)
        if len(full_title) > 65:
            # Use shorter version
            result = f"{self.subject} Laser Cleaning - {specialization}"[:65]
        elif len(full_title) < 45:
            # Add more context
            result = f"{self.subject} Laser Cleaning Technology - {specialization}"
        else:
            result = full_title

        # Sanitize before returning
        return sanitize_content(result)

    def calculate_meta_description(self) -> str:
        """Calculate comprehensive meta description (150-160 characters)."""
        # Extract technical specifications
        density = self._extract_density()
        wavelength = self._extract_wavelength()
        applications = self._extract_primary_applications()

        # Build description with real data
        description = f"Advanced laser cleaning for {self.subject}"

        if density:
            description += f" ({density})"

        description += f" using {wavelength} technology"

        if applications:
            description += f" for {applications}"

        description += ". Precision surface treatment with technical specifications."

        # Ensure optimal length (150-160 characters)
        if len(description) > 160:
            # Truncate intelligently
            description = description[:157] + "..."
        elif len(description) < 120:
            # Add more detail if too short
            description += f" Expert {self.category} processing guide."

        # Sanitize before returning
        return sanitize_content(description)

    def generate_seo_keywords(self) -> List[str]:
        """Generate comprehensive SEO keywords based on frontmatter data."""
        keywords = []

        # Core material keywords
        subject_lower = self.subject.lower()
        keywords.extend(
            [
                subject_lower,
                f"{subject_lower} laser cleaning",
                f"{subject_lower} {self.category}",
                "laser ablation",
                "laser cleaning",
            ]
        )

        # Technical process keywords
        technical_keywords = [
            "non-contact cleaning",
            "precision laser processing",
            "surface contamination removal",
            "industrial laser applications",
            "laser surface treatment",
            "pulsed laser cleaning",
        ]
        keywords.extend(technical_keywords)

        # Category-specific keywords
        category_keywords = {
            "metal": ["metal fabrication", "corrosion removal", "oxide cleaning"],
            "ceramic": [
                "ceramic restoration",
                "archaeological conservation",
                "heritage preservation",
            ],
            "stone": [
                "stone conservation",
                "monument restoration",
                "heritage cleaning",
            ],
            "glass": ["optical cleaning", "precision optics", "glass restoration"],
            "composite": [
                "composite repair",
                "advanced materials",
                "aerospace applications",
            ],
            "wood": ["wood restoration", "eco-friendly cleaning", "cultural heritage"],
            "semiconductor": [
                "semiconductor processing",
                "electronics manufacturing",
                "clean room applications",
            ],
        }

        if self.category in category_keywords:
            keywords.extend(category_keywords[self.category])

        # Application-specific keywords from frontmatter
        applications = self.frontmatter.get("applications", [])
        for app in applications[:3]:  # Limit to top 3
            if isinstance(app, dict):
                industry = app.get("industry", "")
                if industry:
                    keywords.append(f"{industry} applications")

        # Technical specification keywords
        wavelength = self._extract_wavelength()
        if wavelength:
            keywords.append(f"{wavelength} laser")

        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword.lower() not in seen:
                unique_keywords.append(keyword)
                seen.add(keyword.lower())

        return unique_keywords[:20]  # Limit to 20 keywords for SEO optimization

    def calculate_structured_data_keywords(self) -> str:
        """Calculate structured data keywords as comma-separated string."""
        keywords = self.generate_seo_keywords()
        return ", ".join(keywords)

    def generate_opengraph_data(self) -> Dict[str, Any]:
        """Generate comprehensive OpenGraph data for social media optimization."""
        subject_slug = self._generate_slug(self.subject)

        # Enhanced OpenGraph properties
        og_data = [
            {"property": "og:title", "content": self.calculate_meta_title()},
            {
                "property": "og:description",
                "content": self.calculate_meta_description(),
            },
            {"property": "og:type", "content": "article"},
            {
                "property": "og:image",
                "content": f"/images/{subject_slug}-laser-cleaning-hero.jpg",
            },
            {
                "property": "og:image:alt",
                "content": f"{self.subject} laser cleaning process showing precision surface treatment and contamination removal",
            },
            {"property": "og:image:width", "content": "1200"},
            {"property": "og:image:height", "content": "630"},
            {
                "property": "og:url",
                "content": f"https://z-beam.com/{subject_slug}-laser-cleaning",
            },
            {"property": "og:site_name", "content": "Z-Beam Laser Processing Guide"},
            {"property": "og:locale", "content": "en_US"},
            {
                "property": "article:author",
                "content": self.frontmatter.get("author", "Z-Beam Technical Team"),
            },
            {
                "property": "article:section",
                "content": f"{self.category.title()} Processing",
            },
            {"property": "article:tag", "content": f"{self.subject} laser cleaning"},
        ]

        return og_data

    def generate_twitter_card_data(self) -> List[Dict[str, str]]:
        """Generate Twitter Card data for enhanced social sharing."""
        subject_slug = self._generate_slug(self.subject)

        twitter_data = [
            {"name": "twitter:card", "content": "summary_large_image"},
            {"name": "twitter:title", "content": self.calculate_meta_title()},
            {
                "name": "twitter:description",
                "content": self.calculate_meta_description(),
            },
            {
                "name": "twitter:image",
                "content": f"/images/{subject_slug}-laser-cleaning-hero.jpg",
            },
            {
                "name": "twitter:image:alt",
                "content": f"{self.subject} laser cleaning technical guide",
            },
            {"name": "twitter:site", "content": "@ZBeamTech"},
            {"name": "twitter:creator", "content": "@ZBeamTech"},
        ]

        return twitter_data

    def generate_advanced_meta_tags(self) -> List[Dict[str, str]]:
        """Generate advanced meta tags following current best practices."""
        meta_tags = [
            {"name": "description", "content": self.calculate_meta_description()},
            {"name": "keywords", "content": self.calculate_structured_data_keywords()},
            {
                "name": "author",
                "content": sanitize_content(
                    self.frontmatter.get("author", "Z-Beam Technical Team")
                ),
            },
            {"name": "category", "content": self.category},
            {
                "name": "robots",
                "content": "index, follow, max-snippet:-1, max-image-preview:large",
            },
            {
                "name": "googlebot",
                "content": "index, follow, max-snippet:-1, max-image-preview:large",
            },
            {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
            {"name": "format-detection", "content": "telephone=no"},
            {"name": "theme-color", "content": "#1a365d"},
            {"name": "color-scheme", "content": "light dark"},
        ]

        # Add technical specifications as meta tags
        density = self._extract_density()
        if density:
            meta_tags.append({"name": "material:density", "content": density})

        wavelength = self._extract_wavelength()
        if wavelength:
            meta_tags.append({"name": "laser:wavelength", "content": wavelength})

        # Add schema.org markup references
        meta_tags.extend(
            [
                {
                    "name": "application-name",
                    "content": "Z-Beam Laser Processing Guide",
                },
                {"name": "msapplication-TileColor", "content": "#1a365d"},
                {"name": "msapplication-config", "content": "/browserconfig.xml"},
            ]
        )

        return meta_tags

    def generate_complete_metatags(self) -> Dict[str, Any]:
        """Generate complete comprehensive metatags structure."""
        return {
            "title": self.calculate_meta_title(),
            "meta_tags": self.generate_advanced_meta_tags(),
            "opengraph": self.generate_opengraph_data(),
            "twitter": self.generate_twitter_card_data(),
            "canonical": f"https://z-beam.com/{self._generate_slug(self.subject)}-laser-cleaning",
            "alternate": [
                {
                    "hreflang": "en",
                    "href": f"https://z-beam.com/{self._generate_slug(self.subject)}-laser-cleaning",
                }
            ],
        }

    def _extract_density(self) -> Optional[str]:
        """Extract density value from frontmatter."""
        properties = self.frontmatter.get("properties", {})

        # Try different possible density fields
        density_fields = ["density", "materialDensity", "specificGravity"]
        for field in density_fields:
            if field in properties:
                return str(properties[field])

        # Try chemical properties
        chem_props = self.frontmatter.get("chemicalProperties", {})
        if "density" in chem_props:
            return str(chem_props["density"])

        # Default based on category
        default_densities = {
            "metal": "7.8 g/cm³",
            "ceramic": "3.5 g/cm³",
            "stone": "2.6 g/cm³",
            "glass": "2.5 g/cm³",
            "composite": "1.8 g/cm³",
            "wood": "0.6 g/cm³",
            "semiconductor": "5.3 g/cm³",
        }

        return default_densities.get(self.category, "2.5 g/cm³")

    def _extract_wavelength(self) -> str:
        """Extract wavelength from frontmatter or provide default."""
        # Try technical specifications
        tech_specs = self.frontmatter.get("technicalSpecifications", {})
        if "wavelength" in tech_specs:
            return str(tech_specs["wavelength"])

        # Try properties
        properties = self.frontmatter.get("properties", {})
        if "wavelength" in properties:
            return str(properties["wavelength"])

        # Category-specific defaults
        default_wavelengths = {
            "metal": "1064nm",
            "ceramic": "532nm",
            "stone": "1064nm",
            "glass": "355nm",
            "composite": "1064nm",
            "wood": "532nm",
            "semiconductor": "355nm",
        }

        return default_wavelengths.get(self.category, "1064nm")

    def _extract_primary_applications(self) -> str:
        """Extract primary applications from frontmatter."""
        applications = self.frontmatter.get("applications", [])

        if applications and len(applications) > 0:
            if isinstance(applications[0], dict):
                industry = applications[0].get("industry", "")
                detail = applications[0].get("detail", "")
                if industry and detail:
                    return f"{industry} {detail}"
                elif industry:
                    return f"{industry} applications"

        # Category-based defaults
        default_applications = {
            "metal": "industrial manufacturing",
            "ceramic": "heritage conservation",
            "stone": "architectural restoration",
            "glass": "optical applications",
            "composite": "aerospace components",
            "wood": "cultural preservation",
            "semiconductor": "electronics manufacturing",
        }

        return default_applications.get(self.category, "industrial applications")

    def _generate_slug(self, text: str) -> str:
        """Generate URL-friendly slug from text."""
        return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def load_frontmatter_data(material_file_path: str) -> Dict[str, Any]:
    """Load and parse frontmatter data from a material file."""
    try:
        with open(material_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 2:
                frontmatter_content = parts[1].strip()
                return yaml.safe_load(frontmatter_content)

    except FileNotFoundError:
        raise FileNotFoundError(f"Material file not found: {material_file_path}")
    except Exception as e:
        print(f"Error loading frontmatter: {e}")

    return {}


def calculate_metatags_for_material(material_file_path: str) -> str:
    """Generate complete metatags YAML using Python calculations for a material."""
    frontmatter_data = load_frontmatter_data(material_file_path)

    if not frontmatter_data:
        return "---\ntitle: Laser Cleaning Guide\nmeta_tags: []\n---"

    calculator = MetatagsCalculator(frontmatter_data)
    metatags_data = calculator.generate_complete_metatags()

    return yaml.dump(
        metatags_data, default_flow_style=False, sort_keys=False, allow_unicode=True
    )


def generate_yaml_metatags_for_material(material_file_path: str) -> str:
    """Generate complete YAML metatags file for Next.js integration."""
    yaml_content = calculate_metatags_for_material(material_file_path)

    # Wrap in YAML frontmatter delimiters
    return f"---\n{yaml_content.strip()}\n---"


if __name__ == "__main__":
    # Example usage
    sample_frontmatter = {
        "subject": "Aluminum",
        "category": "metal",
        "author": "Dr. Emily Chen",
        "properties": {"density": "2.7 g/cm³", "thermalConductivity": "237 W/(m·K)"},
        "technicalSpecifications": {
            "wavelength": "1064nm",
            "fluenceRange": "1.0-10 J/cm²",
        },
        "applications": [
            {"industry": "aerospace", "detail": "aircraft component cleaning"},
            {"industry": "automotive", "detail": "engine part restoration"},
        ],
    }

    calculator = MetatagsCalculator(sample_frontmatter)
    result = calculator.generate_complete_metatags()

    print("=== Available Functions ===")
    print("1. calculate_metatags_for_material(path) -> YAML string")
    print("2. generate_yaml_metatags_for_material(path) -> Complete YAML file")
    print("\n=== Sample Metatags Output ===")
    print(yaml.dump(result, default_flow_style=False, sort_keys=False)[:500] + "...")
