"""
Tags Python Calculator for Advanced Tag Generation and SEO Optimization
Applies the proven methodology from metatags optimization to enhance tag relevance and quality.
"""

import re
from typing import Any, Dict, List

import yaml


def sanitize_tag(tag: str) -> str:
    """Sanitize tag content to ensure clean, URL-safe tags."""
    if not tag:
        return ""

    # Remove HTML tags and dangerous content first
    tag = re.sub(r"<[^>]*>", "", tag)
    tag = re.sub(r"script", "", tag, flags=re.IGNORECASE)
    tag = re.sub(r"javascript", "", tag, flags=re.IGNORECASE)
    tag = re.sub(r'[\'";]', "", tag)

    # Replace special characters with spaces (except hyphens)
    tag = re.sub(r"[^\w\s-]", " ", tag)

    # Replace multiple spaces with single spaces, then convert to hyphens
    tag = re.sub(r"\s+", " ", tag.strip())
    tag = tag.replace(" ", "-")

    # Clean up multiple hyphens
    tag = re.sub(r"-+", "-", tag)
    tag = tag.lower().strip("-")

    return tag


class TagsCalculator:
    """Advanced Python calculator for optimized tag generation."""

    def __init__(self, frontmatter_data: Dict[str, Any]):
        """Initialize with frontmatter data for tag calculations."""
        self.frontmatter = frontmatter_data
        self.subject = sanitize_tag(frontmatter_data.get("subject", "Unknown Material"))
        self.category = sanitize_tag(frontmatter_data.get("category", "material"))
        self.author = frontmatter_data.get("author", "Technical Expert")

        # Load advanced tag databases
        self.seo_keywords = self._load_seo_keyword_database()
        self.industry_terms = self._load_industry_terminology()
        self.technical_tags = self._load_technical_specifications()
        self.trend_tags = self._load_trending_keywords()

    def _load_seo_keyword_database(self) -> Dict[str, List[str]]:
        """Load SEO-optimized keyword database for laser cleaning industry."""
        return {
            "primary_processes": [
                "laser-cleaning",
                "laser-ablation",
                "surface-cleaning",
                "contamination-removal",
                "oxide-removal",
                "paint-stripping",
                "rust-removal",
                "coating-removal",
            ],
            "technology_keywords": [
                "pulsed-laser",
                "fiber-laser",
                "nanosecond-laser",
                "femtosecond-laser",
                "wavelength-optimization",
                "beam-delivery",
                "scanning-systems",
            ],
            "industry_applications": [
                "aerospace-cleaning",
                "automotive-processing",
                "heritage-restoration",
                "semiconductor-fabrication",
                "medical-device-cleaning",
                "marine-maintenance",
            ],
            "material_benefits": [
                "non-contact-processing",
                "precision-cleaning",
                "selective-removal",
                "damage-free",
                "chemical-free",
                "environmentally-friendly",
            ],
            "quality_standards": [
                "surface-preparation",
                "quality-control",
                "precision-processing",
                "repeatability",
                "automation-ready",
                "process-optimization",
            ],
        }

    def _load_industry_terminology(self) -> Dict[str, Dict[str, List[str]]]:
        """Load industry-specific terminology for enhanced relevance."""
        return {
            "metal": {
                "contaminants": [
                    "corrosion",
                    "oxidation",
                    "scale",
                    "rust",
                    "welding-spatter",
                    "heat-tint",
                ],
                "processes": [
                    "surface-preparation",
                    "weld-prep",
                    "paint-removal",
                    "decoating",
                ],
                "industries": [
                    "aerospace",
                    "automotive",
                    "shipbuilding",
                    "manufacturing",
                    "construction",
                ],
                "benefits": [
                    "material-preservation",
                    "dimensional-accuracy",
                    "adhesion-improvement",
                ],
            },
            "ceramic": {
                "contaminants": [
                    "firing-residue",
                    "glaze-defects",
                    "contamination",
                    "deposits",
                ],
                "processes": [
                    "precision-cleaning",
                    "surface-modification",
                    "defect-removal",
                ],
                "industries": [
                    "electronics",
                    "aerospace",
                    "medical-devices",
                    "research",
                ],
                "benefits": [
                    "micro-precision",
                    "controlled-removal",
                    "surface-integrity",
                ],
            },
            "glass": {
                "contaminants": [
                    "etching-marks",
                    "films",
                    "deposits",
                    "residue",
                    "contamination",
                ],
                "processes": [
                    "optical-cleaning",
                    "surface-restoration",
                    "clarity-enhancement",
                ],
                "industries": [
                    "optical",
                    "automotive",
                    "solar",
                    "electronics",
                    "architectural",
                ],
                "benefits": [
                    "optical-quality",
                    "transparency-restoration",
                    "precision-processing",
                ],
            },
            "composite": {
                "contaminants": [
                    "matrix-contamination",
                    "surface-films",
                    "release-agents",
                    "adhesive-residue",
                ],
                "processes": [
                    "surface-activation",
                    "bond-preparation",
                    "selective-cleaning",
                ],
                "industries": [
                    "aerospace",
                    "automotive",
                    "wind-energy",
                    "marine",
                    "sports-equipment",
                ],
                "benefits": [
                    "fiber-preservation",
                    "bond-enhancement",
                    "damage-free-processing",
                ],
            },
            "stone": {
                "contaminants": [
                    "biological-growth",
                    "pollution",
                    "weathering",
                    "graffiti",
                    "soot",
                ],
                "processes": [
                    "heritage-restoration",
                    "conservation",
                    "cleaning",
                    "preservation",
                ],
                "industries": [
                    "cultural-heritage",
                    "construction",
                    "archaeology",
                    "conservation",
                ],
                "benefits": [
                    "preservation",
                    "reversible-process",
                    "gentle-cleaning",
                    "material-conservation",
                ],
            },
            "wood": {
                "contaminants": [
                    "paint",
                    "char",
                    "stains",
                    "coatings",
                    "surface-damage",
                ],
                "processes": [
                    "restoration",
                    "refinishing",
                    "surface-preparation",
                    "gentle-cleaning",
                ],
                "industries": [
                    "furniture",
                    "construction",
                    "heritage",
                    "art-restoration",
                ],
                "benefits": [
                    "grain-preservation",
                    "controlled-depth",
                    "eco-friendly-process",
                ],
            },
            "semiconductor": {
                "contaminants": [
                    "particles",
                    "films",
                    "oxides",
                    "residue",
                    "contamination",
                ],
                "processes": [
                    "precision-cleaning",
                    "micro-fabrication",
                    "surface-preparation",
                ],
                "industries": [
                    "electronics",
                    "micro-manufacturing",
                    "research",
                    "nanotechnology",
                ],
                "benefits": [
                    "particle-free",
                    "micro-precision",
                    "contamination-control",
                    "chemical-free",
                ],
            },
        }

    def _load_technical_specifications(self) -> Dict[str, List[str]]:
        """Load technical specification tags for enhanced precision."""
        return {
            "wavelength_tags": [
                "1064nm",
                "532nm",
                "355nm",
                "266nm",
                "multi-wavelength",
            ],
            "pulse_characteristics": [
                "nanosecond",
                "picosecond",
                "femtosecond",
                "continuous-wave",
            ],
            "beam_delivery": [
                "fiber-delivery",
                "galvo-scanning",
                "robotic-integration",
                "handheld",
            ],
            "power_levels": [
                "low-power",
                "medium-power",
                "high-power",
                "variable-power",
            ],
            "automation": ["automated", "semi-automated", "manual", "robotic"],
            "monitoring": [
                "real-time-monitoring",
                "quality-control",
                "process-validation",
            ],
        }

    def _load_trending_keywords(self) -> List[str]:
        """Load trending keywords for current industry focus."""
        return [
            "digital-transformation",
            "industry-4.0",
            "smart-manufacturing",
            "sustainable-processing",
            "green-technology",
            "additive-manufacturing",
            "quality-assurance",
            "predictive-maintenance",
            "zero-waste",
            "circular-economy",
            "advanced-materials",
            "precision-engineering",
        ]

    def calculate_primary_material_tag(self) -> str:
        """Calculate the primary material identifier tag."""
        return sanitize_tag(self.subject)

    def calculate_category_tag(self) -> str:
        """Calculate the category-based tag."""
        return sanitize_tag(self.category)

    def calculate_application_tags(self, count: int = 2) -> List[str]:
        """Calculate application-specific tags based on material and industry data."""
        category_data = self.industry_terms.get(self.category, {})
        industries = category_data.get("industries", [])

        # Add author-specific preferences
        author_slug = self._generate_author_slug()
        if "alessandro-moretti" in author_slug:
            industries = ["heritage-restoration", "industrial-cleaning"] + industries
        elif "yi-chun-lin" in author_slug:
            industries = ["precision-manufacturing", "electronics"] + industries

        # Remove duplicates while preserving order
        seen = set()
        unique_industries = []
        for industry in industries:
            if industry not in seen:
                unique_industries.append(sanitize_tag(industry))
                seen.add(industry)

        return unique_industries[:count]

    def calculate_process_tags(self, count: int = 2) -> List[str]:
        """Calculate process-specific tags for the material type."""
        category_data = self.industry_terms.get(self.category, {})
        processes = category_data.get("processes", [])

        # Add universal laser cleaning processes
        universal_processes = ["laser-cleaning", "surface-preparation"]
        all_processes = universal_processes + processes

        # Remove duplicates
        seen = set()
        unique_processes = []
        for process in all_processes:
            clean_process = sanitize_tag(process)
            if clean_process not in seen:
                unique_processes.append(clean_process)
                seen.add(clean_process)

        return unique_processes[:count]

    def calculate_contaminant_tags(self, count: int = 2) -> List[str]:
        """Calculate contaminant-specific tags."""
        category_data = self.industry_terms.get(self.category, {})
        contaminants = category_data.get(
            "contaminants", ["contamination", "surface-deposits"]
        )

        return [sanitize_tag(cont) for cont in contaminants[:count]]

    def calculate_benefit_tags(self, count: int = 1) -> List[str]:
        """Calculate benefit-specific tags."""
        category_data = self.industry_terms.get(self.category, {})
        benefits = category_data.get("benefits", ["precision-cleaning"])

        return [sanitize_tag(benefit) for benefit in benefits[:count]]

    def calculate_technical_tags(self, count: int = 1) -> List[str]:
        """Calculate technical specification tags from frontmatter."""
        technical_tags = []

        # Extract wavelength information
        wavelength = self._extract_wavelength()
        if wavelength:
            technical_tags.append(sanitize_tag(wavelength))

        # Extract density information for material characterization
        density = self._extract_density()
        if density and len(technical_tags) < count:
            # Convert density to material classification tag
            try:
                density_val = float(re.search(r"(\d+\.?\d*)", density).group(1))
                if density_val < 2.0:
                    technical_tags.append("lightweight-material")
                elif density_val > 7.0:
                    technical_tags.append("high-density-material")
                else:
                    technical_tags.append("standard-density-material")
            except Exception:
                technical_tags.append("material-processing")

        # Fill with general technical tags if needed
        while len(technical_tags) < count:
            if "precision-processing" not in technical_tags:
                technical_tags.append("precision-processing")
            else:
                break

        return technical_tags[:count]

    def _extract_wavelength(self) -> str:
        """Extract wavelength from technical specifications."""
        tech_specs = self.frontmatter.get("technicalSpecifications", {})
        wavelength = tech_specs.get("wavelength", "")

        if wavelength:
            # Normalize wavelength format
            if "1064" in wavelength:
                return "1064nm"
            elif "532" in wavelength:
                return "532nm"
            elif "355" in wavelength:
                return "355nm"
            else:
                return sanitize_tag(wavelength)

        return ""

    def _extract_density(self) -> str:
        """Extract density from material properties."""
        properties = self.frontmatter.get("properties", {})
        return properties.get("density", "")

    def _extract_applications(self) -> List[str]:
        """Extract application information from frontmatter."""
        applications = self.frontmatter.get("applications", [])
        app_tags = []

        for app in applications:
            if isinstance(app, dict):
                industry = app.get("industry", "")
                if industry:
                    app_tags.append(sanitize_tag(industry))
            elif isinstance(app, str):
                app_tags.append(sanitize_tag(app))

        return app_tags

    def _generate_author_slug(self) -> str:
        """Generate author slug for tag inclusion."""
        author = self.author.strip()
        if not author:
            return "technical-expert"

        # Clean author name to slug format
        return sanitize_tag(author.replace("Dr. ", "").replace("Prof. ", ""))

    def calculate_seo_optimized_tags(self, total_count: int = 8) -> List[str]:
        """Calculate SEO-optimized tag set with strategic distribution."""
        tags = []
        used_tags = set()

        # 1. Primary material identifier (always first)
        primary_tag = self.calculate_primary_material_tag()
        if primary_tag:
            tags.append(primary_tag)
            used_tags.add(primary_tag)

        # 2-3. Application tags (high SEO value)
        app_tags = self.calculate_application_tags(2)
        for tag in app_tags:
            if tag not in used_tags and len(tags) < total_count - 1:
                tags.append(tag)
                used_tags.add(tag)

        # 4-5. Process tags (industry relevance)
        process_tags = self.calculate_process_tags(2)
        for tag in process_tags:
            if tag not in used_tags and len(tags) < total_count - 1:
                tags.append(tag)
                used_tags.add(tag)

        # 6. Contaminant/Problem tag (search intent)
        contaminant_tags = self.calculate_contaminant_tags(1)
        for tag in contaminant_tags:
            if tag not in used_tags and len(tags) < total_count - 1:
                tags.append(tag)
                used_tags.add(tag)
                break

        # 7. Benefit/Technical tag (value proposition)
        benefit_tags = self.calculate_benefit_tags(1) + self.calculate_technical_tags(1)
        for tag in benefit_tags:
            if tag not in used_tags and len(tags) < total_count - 1:
                tags.append(tag)
                used_tags.add(tag)
                break

        # Fill remaining slots with high-value SEO tags
        while len(tags) < total_count - 1:
            backup_tags = [
                "non-contact",
                "precision",
                "industrial",
                "automated",
                "quality-control",
            ]
            for backup_tag in backup_tags:
                if backup_tag not in used_tags:
                    tags.append(backup_tag)
                    used_tags.add(backup_tag)
                    break
            else:
                break

        # Last slot: Author (for attribution and authority)
        if len(tags) < total_count:
            author_tag = self._generate_author_slug()
            tags.append(author_tag)

        return tags[:total_count]

    def calculate_tag_relevance_scores(self, tags: List[str]) -> Dict[str, float]:
        """Calculate relevance scores for tag optimization."""
        scores = {}

        for tag in tags:
            score = 0.0

            # Material relevance (30%)
            if self.subject.lower() in tag.lower():
                score += 0.3
            elif self.category.lower() in tag.lower():
                score += 0.2

            # Industry relevance (25%)
            category_data = self.industry_terms.get(self.category, {})
            all_industry_terms = []
            for term_list in category_data.values():
                all_industry_terms.extend(term_list)

            if any(term in tag for term in all_industry_terms):
                score += 0.25

            # SEO value (25%)
            all_seo_terms = []
            for seo_list in self.seo_keywords.values():
                all_seo_terms.extend(seo_list)

            if any(term in tag for term in all_seo_terms):
                score += 0.25

            # Technical precision (20%)
            if any(
                tech_term in tag
                for tech_list in self.technical_tags.values()
                for tech_term in tech_list
            ):
                score += 0.2

            scores[tag] = min(score, 1.0)  # Cap at 1.0

        return scores

    def generate_complete_tags(self) -> Dict[str, Any]:
        """Generate complete tag analysis with metadata."""
        tags = self.calculate_seo_optimized_tags()
        scores = self.calculate_tag_relevance_scores(tags)

        return {
            "tags": tags,
            "tag_count": len(tags),
            "material": self.subject,
            "category": self.category,
            "author": self._generate_author_slug(),
            "relevance_scores": scores,
            "average_score": sum(scores.values()) / len(scores) if scores else 0.0,
            "seo_optimized": True,
            "generation_method": "python_calculator",
        }


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


def calculate_tags_for_material(material_file_path: str) -> str:
    """Generate optimized tags using Python calculations for a material."""
    frontmatter_data = load_frontmatter_data(material_file_path)

    if not frontmatter_data:
        return "technical-material, laser-cleaning, industrial, precision, surface-preparation, quality-control, automated, technical-expert"

    calculator = TagsCalculator(frontmatter_data)
    tags_data = calculator.calculate_seo_optimized_tags()

    return ", ".join(tags_data)


def generate_tags_for_material(material_file_path: str) -> str:
    """Generate complete tags content for file output."""
    return calculate_tags_for_material(material_file_path)


if __name__ == "__main__":
    # Example usage
    sample_frontmatter = {
        "subject": "Aluminum",
        "category": "metal",
        "author": "Alessandro Moretti",
        "properties": {"density": "2.7 g/cm³"},
        "technicalSpecifications": {"wavelength": "1064nm"},
        "applications": [{"industry": "aerospace", "detail": "aircraft cleaning"}],
    }

    calculator = TagsCalculator(sample_frontmatter)
    result = calculator.generate_complete_tags()

    print("🏷️ OPTIMIZED TAGS RESULT:")
    print("=" * 40)
    print(f"Tags: {', '.join(result['tags'])}")
    print(f"Count: {result['tag_count']}")
    print(f"Average Relevance: {result['average_score']:.2f}")
    print(f"SEO Optimized: {result['seo_optimized']}")
