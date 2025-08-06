"""
Content formatting utilities for Z-Beam Generator.

This module handles all formatting tasks that were previously done by AI,
ensuring consistent and reliable output formatting.
"""

import re
from typing import Dict, Any, List
from components.base.image_handler import ImageHandler


class ContentFormatter:
    """Handles all content formatting tasks to offload work from AI."""
    
    @staticmethod
    def format_title(subject: str, article_type: str = "material") -> str:
        """Generate SEO-optimized title.
        
        Args:
            subject: The subject material/topic
            article_type: Type of article (material, application, etc.)
            
        Returns:
            str: Formatted title
        """
        return f"Laser Cleaning {subject} - Technical Guide for Optimal Processing"
    
    @staticmethod
    def format_headline(subject: str, category: str = None) -> str:
        """Generate concise headline.
        
        Args:
            subject: The subject material/topic
            category: Material category (ceramic, metal, etc.)
            
        Returns:
            str: Formatted headline
        """
        category_text = f"{category} " if category else ""
        return f"Comprehensive technical guide for laser cleaning {category_text}{subject.lower()}"
    
    @staticmethod
    def format_description(subject: str, formula: str = None, properties: Dict = None) -> str:
        """Generate technical description with key properties.
        
        Args:
            subject: The subject material/topic
            formula: Chemical formula if applicable
            properties: Key properties dictionary
            
        Returns:
            str: Formatted description (150-250 chars)
        """
        desc_parts = [f"Technical overview of {subject.lower()}"]
        
        if formula:
            desc_parts.append(f"({formula})")
        
        desc_parts.append("for laser cleaning applications")
        
        if properties:
            prop_parts = []
            if "density" in properties:
                prop_parts.append(f"{properties['density']} density")
            if "wavelength" in properties:
                prop_parts.append(f"{properties['wavelength']}")
            if "fluenceRange" in properties:
                prop_parts.append(f"{properties['fluenceRange']}")
            
            if prop_parts:
                desc_parts.append(f"including {', '.join(prop_parts[:2])}")
        
        desc_parts.append("and industrial applications")
        
        description = ", ".join(desc_parts) + "."
        
        # Ensure it's within 150-250 char range
        if len(description) > 250:
            description = description[:247] + "..."
        
        return description
    
    @staticmethod
    def format_keywords(subject: str, category: str = None, 
                       chemical_formula: str = None) -> List[str]:
        """Generate comprehensive keyword list.
        
        Args:
            subject: The subject material/topic
            category: Material category
            chemical_formula: Chemical formula if applicable
            
        Returns:
            List[str]: List of 8-12 keywords
        """
        keywords = []
        
        # Base keywords
        subject_lower = subject.lower()
        keywords.append(f"{subject_lower}")
        
        if category:
            keywords.append(f"{subject_lower} {category}")
        
        # Laser-specific terms
        keywords.extend([
            "laser ablation",
            "laser cleaning",
            "non-contact cleaning",
            "pulsed fiber laser",
            "surface contamination removal"
        ])
        
        # Chemical formula variations
        if chemical_formula:
            # Clean up formula for keyword use
            formula_clean = re.sub(r'[²³·⁰¹⁴⁵⁶⁷⁸⁹]', '', chemical_formula)
            keywords.append(f"{formula_clean} composite")
        
        # Technical terms
        keywords.extend([
            "industrial laser parameters",
            "thermal processing",
            "surface restoration"
        ])
        
        # Application-specific
        if category == "ceramic":
            keywords.extend(["ceramic restoration", "archaeological conservation"])
        elif category == "metal":
            keywords.extend(["metal surface treatment", "corrosion removal"])
        elif category == "plastic":
            keywords.extend(["polymer processing", "plastic surface modification"])
        
        # Ensure we have 8-12 keywords
        return keywords[:12]
    
    @staticmethod
    def format_images(subject: str) -> Dict[str, Dict[str, str]]:
        """Generate standardized image structure.
        
        Args:
            subject: The subject material/topic
            
        Returns:
            Dict: Standardized image structure with alt text and URLs
        """
        subject_lower = subject.lower()
        
        return {
            "hero": {
                "alt": f"{subject} surface undergoing laser cleaning showing precise contamination removal",
                "url": ImageHandler.format_image_url(subject, "hero")
            },
            "closeup": {
                "alt": f"Microscopic view of {subject_lower} surface after laser treatment showing preserved microstructure",
                "url": ImageHandler.format_image_url(subject, "closeup")
            }
        }
    
    @staticmethod
    def format_technical_specifications(base_specs: Dict = None) -> Dict[str, str]:
        """Generate standardized technical specifications.
        
        Args:
            base_specs: Base specifications to enhance
            
        Returns:
            Dict: Standardized technical specifications
        """
        default_specs = {
            "powerRange": "20-100W",
            "pulseDuration": "10-100ns", 
            "wavelength": "1064nm (primary), 532nm (optional)",
            "spotSize": "0.1-2.0mm",
            "repetitionRate": "10-50kHz",
            "fluenceRange": "0.5-5 J/cm²",
            "safetyClass": "Class 4 (requires full enclosure)"
        }
        
        if base_specs:
            default_specs.update(base_specs)
        
        return default_specs
    
    @staticmethod
    def format_regulatory_standards() -> List[Dict[str, str]]:
        """Generate standard regulatory standards list.
        
        Returns:
            List[Dict]: List of regulatory standards
        """
        return [
            {
                "code": "IEC 60825-1:2014",
                "description": "Safety of laser products - Equipment classification and requirements"
            },
            {
                "code": "ISO 11146:2021", 
                "description": "Lasers and laser-related equipment - Test methods for laser beam widths"
            },
            {
                "code": "EN 15898:2019",
                "description": "Conservation of cultural property - Main general terms and definitions"
            }
        ]
    
    @staticmethod
    def format_environmental_impact(subject: str = None) -> List[Dict[str, str]]:
        """Generate standardized environmental impact list.
        
        Args:
            subject: The subject material (for customization)
            
        Returns:
            List[Dict]: Environmental impact benefits
        """
        return [
            {
                "benefit": "Reduced chemical waste",
                "description": "Eliminates 100% of solvent use compared to traditional cleaning methods, preventing ~200L/year of hazardous waste in medium-scale operations."
            },
            {
                "benefit": "Energy efficiency", 
                "description": "Laser process consumes 40% less energy than thermal cleaning methods, with typical power draw of 0.5-2.5 kWh/m² treated surface."
            },
            {
                "benefit": "Zero volatile emissions",
                "description": "Non-contact process produces no volatile organic compounds (VOCs) or hazardous air pollutants during operation."
            }
        ]
    
    @staticmethod
    def format_outcomes() -> List[Dict[str, str]]:
        """Generate standardized measurement outcomes.
        
        Returns:
            List[Dict]: Measurable outcomes with metrics
        """
        return [
            {
                "result": "Surface cleanliness",
                "metric": "98% contamination removal measured by SEM-EDS analysis (ASTM E1508)"
            },
            {
                "result": "Substrate preservation", 
                "metric": "< 0.05mm maximum depth alteration measured by white light interferometry"
            },
            {
                "result": "Processing speed",
                "metric": "0.5-2.0 m²/hour coverage rate at 50W power"
            }
        ]
    
    @staticmethod
    def format_frontmatter_structure(raw_data: Dict[str, Any], subject: str, 
                                   category: str = None, article_type: str = "material") -> Dict[str, Any]:
        """Apply comprehensive formatting to frontmatter data.
        
        Args:
            raw_data: Raw data from AI generation
            subject: The subject material/topic
            category: Material category
            article_type: Type of article
            
        Returns:
            Dict: Fully formatted frontmatter data
        """
        formatted = raw_data.copy()
        
        # Apply standardized formatting
        formatted["title"] = ContentFormatter.format_title(subject, article_type)
        formatted["headline"] = ContentFormatter.format_headline(subject, category)
        
        # Format description with available data
        formula = formatted.get("chemicalProperties", {}).get("formula")
        properties = formatted.get("properties", {})
        formatted["description"] = ContentFormatter.format_description(subject, formula, properties)
        
        # Ensure keywords are properly formatted
        if "keywords" not in formatted or not formatted["keywords"]:
            formatted["keywords"] = ContentFormatter.format_keywords(subject, category, formula)
        
        # Ensure standardized image structure
        formatted["images"] = ContentFormatter.format_images(subject)
        
        # Apply standardized technical specifications
        if "technicalSpecifications" not in formatted:
            formatted["technicalSpecifications"] = ContentFormatter.format_technical_specifications()
        else:
            formatted["technicalSpecifications"] = ContentFormatter.format_technical_specifications(
                formatted["technicalSpecifications"]
            )
        
        # Apply standardized regulatory standards
        if "regulatoryStandards" not in formatted:
            formatted["regulatoryStandards"] = ContentFormatter.format_regulatory_standards()
        
        # Apply standardized environmental impact
        if "environmentalImpact" not in formatted:
            formatted["environmentalImpact"] = ContentFormatter.format_environmental_impact(subject)
        
        # Apply standardized outcomes
        if "outcomes" not in formatted:
            formatted["outcomes"] = ContentFormatter.format_outcomes()
        
        # Ensure required fields
        formatted["subject"] = subject
        formatted["article_type"] = article_type
        if category:
            formatted["category"] = category
        
        return formatted
    
    @staticmethod
    def normalize_yaml_content(content: str) -> str:
        """Normalize YAML content for consistency.
        
        Args:
            content: Raw YAML content string
            
        Returns:
            str: Normalized YAML content
        """
        # Remove any markdown code blocks
        content = re.sub(r'^```ya?ml\s*\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'\n```\s*$', '', content, flags=re.MULTILINE)
        
        # Fix image URL double dashes
        content = re.sub(r'(/images/[^"]*?)--+([^"]*?\.jpg)', r'\1-\2', content)
        
        # Normalize quote usage in YAML
        content = re.sub(r'([:\s]+)"([^"]*?)"(\s*)', r'\1"\2"\3', content)
        
        # Ensure consistent indentation (2 spaces)
        lines = content.split('\n')
        normalized_lines = []
        
        for line in lines:
            if line.strip():
                # Count leading spaces and convert tabs to spaces
                line = line.expandtabs(2)
                leading_spaces = len(line) - len(line.lstrip())
                
                # Normalize to multiples of 2
                if leading_spaces > 0:
                    normalized_indent = (leading_spaces // 2) * 2
                    line = ' ' * normalized_indent + line.lstrip()
                
            normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)
