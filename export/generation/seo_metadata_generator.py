"""
SEO Metadata Generator

Generates page_title and meta_description fields for materials, settings, and contaminants
based on technical specifications and best practices for industrial/technical audiences.

Part of Export System - Field Generation.

Architecture:
- Reads material properties, settings, and context
- Applies SEO best practices from PAGE_TITLE_META_DESCRIPTION_SPEC.md
- Generates unique, problem-focused titles and descriptions
- Validates character limits (title: 50-55, description: 155-160)

Usage:
    config = {
        'type': 'seo_metadata',
        'page_type': 'material',  # or 'settings' or 'contaminant'
        'title_field': 'page_title',
        'description_field': 'meta_description'
    }
    
    generator = SEOMetadataGenerator(config)
    frontmatter = generator.generate(frontmatter)
"""

import logging
import json
from pathlib import Path
from typing import Any, Dict, Optional

from export.generation.base import BaseGenerator

logger = logging.getLogger(__name__)


class SEOMetadataGenerator(BaseGenerator):
    """
    Generate SEO page titles and meta descriptions for technical laser cleaning content.
    
    Features:
    - Problem-solution format with specific metrics
    - Damage prevention language (engineers prioritize risk mitigation)
    - Unique differentiators (no generic "complete guide" language)
    - Character limit validation (title: 50-55, description: 155-160)
    - Material-specific challenge identification
    
    Based on: docs/PAGE_TITLE_META_DESCRIPTION_SPEC.md
    """
    
    # Challenge patterns for high reflectivity materials
    HIGH_REFLECTIVITY_CHALLENGES = {
        'aluminum': "High Reflectivity Laser Cleaning",
        'copper': "Green Laser Cleaning Required",
        'gold': "Ultra-High Reflectivity Control",
        'silver': "Near-Total Reflection Management",
        'polished-steel': "Reflectivity Optimization"
    }
    
    # Challenge patterns for high absorption materials
    HIGH_ABSORPTION_CHALLENGES = {
        'carbon-steel': "Efficient Rust Removal",
        'cast-iron': "Heavy Scale Stripping",
        'steel': "Rust Removal Without Warping"
    }
    
    # Thermal sensitive materials
    THERMAL_SENSITIVE_CHALLENGES = {
        'composite': "Multi-Layer Laser Cleaning",
        'plastic': "Low-Temperature Control",
        'polymer': "Thermal Management Required"
    }
    
    # Reactive materials
    REACTIVE_CHALLENGES = {
        'titanium': "Reactive Surface Laser Treatment",
        'stainless-steel': "Passivation Layer Preservation",
        'aluminum-alloy': "Anodized Finish Protection"
    }
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize SEO metadata generator.
        
        Args:
            config: Config with keys:
                - page_type: 'material', 'settings', or 'contaminant'
                - title_field: Output field for title (default: 'page_title')
                - description_field: Output field for description (default: 'meta_description')
        """
        super().__init__(config)
        
        self.page_type = config.get('page_type', 'material')
        self.title_field = config.get('title_field', 'page_title')
        self.description_field = config.get('description_field', 'meta_description')
        
        # Character limits
        self.title_min = 50
        self.title_max = 55
        self.desc_min = 155
        self.desc_max = 160
    
    def generate(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate SEO metadata fields.
        
        Args:
            frontmatter: Frontmatter dict with material/contaminant data
        
        Returns:
            Frontmatter with page_title and meta_description added
        """
        try:
            if self.page_type == 'material':
                title, description = self._generate_material_seo(frontmatter)
            elif self.page_type == 'settings':
                title, description = self._generate_settings_seo(frontmatter)
            elif self.page_type == 'contaminant':
                title, description = self._generate_contaminant_seo(frontmatter)
            elif self.page_type == 'compound':
                title, description = self._generate_compound_seo(frontmatter)
            else:
                logger.warning(f"Unknown page_type: {self.page_type}")
                return frontmatter
            
            # Validate and assign
            if title and description:
                title = self._validate_and_truncate_title(title)
                description = self._validate_and_truncate_description(description)
                
                frontmatter[self.title_field] = title
                frontmatter[self.description_field] = description
                
                logger.debug(
                    f"Generated SEO: title={len(title)} chars, desc={len(description)} chars"
                )
            
            return frontmatter
            
        except Exception as e:
            logger.error(f"Error generating SEO metadata: {e}")
            return frontmatter
    
    def _generate_material_seo(self, frontmatter: Dict[str, Any]) -> tuple[str, str]:
        """Generate title and description for material pages."""
        name = frontmatter.get('name', 'Material')
        category = frontmatter.get('category', '')
        subcategory = frontmatter.get('subcategory', '')
        
        # Get properties for context
        props = frontmatter.get('properties', {})
        reflectivity = self._get_property_value(props, 'reflectivity', 'optical_properties')
        absorption = self._get_property_value(props, 'absorption', 'optical_properties')
        thermal_cond = self._get_property_value(props, 'thermal_conductivity', 'thermal_properties')
        
        # Determine challenge based on material properties
        slug = name.lower().replace(' ', '-')
        challenge = self._determine_challenge(slug, reflectivity, absorption, thermal_cond)
        
        # Build title: "{Material}: {Challenge}"
        title = f"{name}: {challenge}"
        
        # Build description with specific metrics
        description = self._build_material_description(
            name, challenge, reflectivity, absorption, category, subcategory
        )
        
        return title, description
    
    def _generate_settings_seo(self, frontmatter: Dict[str, Any]) -> tuple[str, str]:
        """Generate title and description for settings pages."""
        name = frontmatter.get('name', 'Material')
        
        # Get wavelength and power from settings
        wavelength = frontmatter.get('wavelength_nm')
        power_min = frontmatter.get('power_watts_min')
        power_max = frontmatter.get('power_watts_max')
        
        # Get removal targets (from description or common contaminants)
        removal_target = self._infer_removal_target(name, frontmatter)
        
        # Build title: "{Material} Settings: {Wavelength}nm {Target}"
        if wavelength:
            title = f"{name} Settings: {wavelength}nm {removal_target}"
        elif power_min and power_max:
            title = f"{name} Settings: {power_min}-{power_max}W {removal_target}"
        else:
            title = f"{name} Settings: Laser Parameters"
        
        # Build description
        description = self._build_settings_description(
            name, wavelength, power_min, power_max, removal_target
        )
        
        return title, description
    
    def _generate_contaminant_seo(self, frontmatter: Dict[str, Any]) -> tuple[str, str]:
        """Generate title and description for contaminant pages."""
        name = frontmatter.get('name', 'Contaminant')
        category = frontmatter.get('category', '')
        
        # Infer key benefit based on contaminant type
        benefit = self._infer_contaminant_benefit(name, category)
        
        # Build title: "{Contaminant} Removal: {Method} {Benefit}"
        title = f"{name} Removal: Laser Ablation {benefit}"
        
        # Build description
        description = self._build_contaminant_description(name, category, benefit)
        
        return title, description
    
    def _generate_compound_seo(self, frontmatter: Dict[str, Any]) -> tuple[str, str]:
        """Generate title and description for compound pages."""
        name = frontmatter.get('name', 'Compound')
        hazard_class = frontmatter.get('hazard_class', 'Hazardous')
        cas_number = frontmatter.get('cas_number', '')
        
        # Infer hazard type from hazard_class
        hazard_type = self._infer_hazard_type(hazard_class, name)
        
        # Build title: "{Compound}: {Hazard Type} {Formation}"
        title = f"{name}: {hazard_type}"
        
        # Build description
        description = self._build_compound_description(name, hazard_class, hazard_type, cas_number)
        
        return title, description
    
    def _determine_challenge(
        self, 
        slug: str, 
        reflectivity: Optional[float],
        absorption: Optional[float],
        thermal_cond: Optional[float]
    ) -> str:
        """Determine the unique challenge/differentiator for this material."""
        
        # Check predefined challenges
        if slug in self.HIGH_REFLECTIVITY_CHALLENGES:
            return self.HIGH_REFLECTIVITY_CHALLENGES[slug]
        if slug in self.HIGH_ABSORPTION_CHALLENGES:
            return self.HIGH_ABSORPTION_CHALLENGES[slug]
        if slug in self.THERMAL_SENSITIVE_CHALLENGES:
            return self.THERMAL_SENSITIVE_CHALLENGES[slug]
        if slug in self.REACTIVE_CHALLENGES:
            return self.REACTIVE_CHALLENGES[slug]
        
        # Dynamic challenge based on properties
        if reflectivity and reflectivity > 85:
            return "High Reflectivity Laser Cleaning"
        elif absorption and absorption > 80:
            return "Efficient Absorption Cleaning"
        elif 'composite' in slug or 'fiber' in slug:
            return "Multi-Layer Laser Cleaning"
        elif 'ceramic' in slug or 'glass' in slug:
            return "Precision Surface Cleaning"
        elif 'wood' in slug:
            return "Gentle Laser Restoration"
        else:
            return "Precision Laser Cleaning"
    
    def _build_material_description(
        self,
        name: str,
        challenge: str,
        reflectivity: Optional[float],
        absorption: Optional[float],
        category: str,
        subcategory: str
    ) -> str:
        """Build SEO description for material with specific metrics."""
        
        # Start with challenge
        parts = [f"{name}:"]
        
        # Add specific metric based on challenge type
        if "Reflectivity" in challenge and reflectivity:
            parts.append(f"High reflectivity ({int(reflectivity)}%) requires 1064nm.")
            damage_prevention = "Prevents heat damage, preserves surface finish."
        elif "Absorption" in challenge and absorption:
            parts.append(f"{int(absorption)}% absorption at 1064nm enables efficient cleaning.")
            damage_prevention = "Removes contamination without warping."
        elif "Multi-Layer" in challenge:
            parts.append("Multi-layer structure requires balanced parameters.")
            damage_prevention = "No delamination, preserves fiber-matrix bond."
        elif "Reactive" in challenge:
            parts.append("Reactive surface requires controlled parameters.")
            damage_prevention = "Maintains passivation layer."
        else:
            parts.append("Optimized laser parameters for effective cleaning.")
            damage_prevention = "Preserves substrate integrity."
        
        parts.append(damage_prevention)
        
        # Add industry context
        industry_grade = self._get_industry_grade(category, subcategory, name)
        parts.append(industry_grade)
        
        return " ".join(parts)
    
    def _build_settings_description(
        self,
        name: str,
        wavelength: Optional[int],
        power_min: Optional[int],
        power_max: Optional[int],
        removal_target: str
    ) -> str:
        """Build SEO description for settings with power/wavelength."""
        
        parts = [f"{name}:"]
        
        # Add wavelength/power
        if wavelength and power_min and power_max:
            parts.append(f"{power_min}-{power_max}W, {wavelength}nm")
        elif wavelength:
            parts.append(f"{wavelength}nm")
        elif power_min and power_max:
            parts.append(f"{power_min}-{power_max}W")
        
        # Add removal target
        parts.append(f"removes {removal_target.lower()}.")
        
        # Add quality/speed metric
        parts.append("Industrial-grade parameters. No substrate damage.")
        
        return " ".join(parts)
    
    def _build_contaminant_description(
        self,
        name: str,
        category: str,
        benefit: str
    ) -> str:
        """Build SEO description for contaminant removal."""
        
        # Default absorption for common contaminants
        absorption_map = {
            'rust': '88-92',
            'oxide': '85-90',
            'scale': '90-95',
            'carbon': '95',
            'paint': '70-80'
        }
        
        name_lower = name.lower()
        absorption = '85-90'  # default
        for key, value in absorption_map.items():
            if key in name_lower:
                absorption = value
                break
        
        parts = [f"{name}: {absorption}% absorption at 1064nm."]
        
        # Add pass count
        if 'single' in benefit.lower():
            parts.append("Single-pass removal.")
        elif 'multi' in benefit.lower() or 'layer' in name_lower:
            parts.append("2-5 passes depending on thickness.")
        else:
            parts.append("2-3 passes for complete removal.")
        
        # Add protection
        parts.append("Preserves substrate integrity.")
        
        # Add vs alternative
        if 'no chemicals' in benefit.lower():
            parts.append("No chemical waste.")
        elif 'no warping' in benefit.lower():
            parts.append("No warping or distortion.")
        else:
            parts.append("No chemicals, no media waste.")
        
        return " ".join(parts)
    
    def _build_compound_description(
        self,
        name: str,
        hazard_class: str,
        hazard_type: str,
        cas_number: str
    ) -> str:
        """Build SEO description for compound with hazard and control info."""
        
        parts = [f"{name}:"]
        
        # Add hazard type
        parts.append(f"{hazard_type}")
        
        # Add formation source (common materials)
        if 'chromium' in name.lower():
            parts.append("from stainless steel processing.")
        elif 'lead' in name.lower():
            parts.append("from lead paint removal.")
        elif 'beryllium' in name.lower():
            parts.append("from beryllium-copper alloys.")
        elif 'cadmium' in name.lower():
            parts.append("from cadmium-plated parts.")
        else:
            parts.append("from metal processing.")
        
        # Add control requirements
        if hazard_class and 'carcinogen' in hazard_class.lower():
            parts.append("HEPA filtration required. Medical surveillance.")
        elif hazard_class and 'toxic' in hazard_class.lower():
            parts.append("Requires enclosed extraction.")
        else:
            parts.append("Requires proper ventilation and PPE.")
        
        return " ".join(parts)
    
    def _infer_hazard_type(self, hazard_class: str, name: str) -> str:
        """Infer hazard type for compound title."""
        name_lower = name.lower()
        hazard_lower = hazard_class.lower() if hazard_class else ''
        
        if 'carcinogen' in hazard_lower or 'chromium' in name_lower and 'hexavalent' in name_lower:
            return "Carcinogenic Fumes"
        elif 'neurotox' in hazard_lower or 'lead' in name_lower:
            return "Neurotoxic Particulate"
        elif 'respiratory' in hazard_lower or 'beryllium' in name_lower:
            return "Respiratory Hazard Dust"
        elif 'toxic' in hazard_lower or 'cadmium' in name_lower:
            return "Toxic Metal Fumes"
        elif 'corrosive' in hazard_lower:
            return "Corrosive Fumes"
        elif 'irritant' in hazard_lower:
            return "Respiratory Irritant"
        else:
            return "Hazardous Emission"
    
    def _get_property_value(
        self, 
        props: Dict[str, Any], 
        prop_name: str,
        category: str
    ) -> Optional[float]:
        """Extract property value from nested structure."""
        if not props:
            return None
        
        # Try category -> property structure
        if category in props and prop_name in props[category]:
            prop_data = props[category][prop_name]
            if isinstance(prop_data, dict):
                return prop_data.get('value')
            return prop_data
        
        # Try direct property access
        if prop_name in props:
            prop_data = props[prop_name]
            if isinstance(prop_data, dict):
                return prop_data.get('value')
            return prop_data
        
        return None
    
    def _infer_removal_target(self, material_name: str, frontmatter: Dict[str, Any]) -> str:
        """Infer primary removal target for this material."""
        name_lower = material_name.lower()
        
        if 'aluminum' in name_lower:
            return "Oxide Removal"
        elif 'steel' in name_lower:
            return "Rust/Scale Removal"
        elif 'copper' in name_lower or 'brass' in name_lower:
            return "Oxidation Treatment"
        elif 'titanium' in name_lower:
            return "Surface Preparation"
        elif 'stainless' in name_lower:
            return "Heat Tint Removal"
        else:
            return "Contamination Removal"
    
    def _infer_contaminant_benefit(self, name: str, category: str) -> str:
        """Infer key benefit for contaminant removal."""
        name_lower = name.lower()
        
        if 'rust' in name_lower:
            return "No Warping"
        elif 'paint' in name_lower or 'coating' in name_lower:
            return "No Chemicals"
        elif 'scale' in name_lower:
            return "High Efficiency"
        elif 'carbon' in name_lower:
            return "Substrate-Safe"
        elif 'oil' in name_lower or 'grease' in name_lower:
            return "Single-Pass"
        else:
            return "Clean Removal"
    
    def _get_industry_grade(self, category: str, subcategory: str, name: str) -> str:
        """Determine industry grade context."""
        name_lower = name.lower()
        
        if 'aluminum' in name_lower or 'titanium' in name_lower or 'composite' in name_lower:
            return "Aerospace-grade."
        elif 'copper' in name_lower or 'semiconductor' in category:
            return "Electronics-safe."
        elif 'stainless' in name_lower and 'food' not in name_lower:
            return "Food-grade safe."
        elif 'steel' in name_lower or 'iron' in name_lower:
            return "Industrial-rated."
        else:
            return "Professional-grade."
    
    def _validate_and_truncate_title(self, title: str) -> str:
        """Validate title character count and truncate if needed."""
        if len(title) <= self.title_max:
            return title
        
        # Truncate at word boundary
        truncated = title[:self.title_max]
        last_space = truncated.rfind(' ')
        if last_space > self.title_min:
            truncated = truncated[:last_space]
        
        logger.warning(f"Title truncated from {len(title)} to {len(truncated)} chars")
        return truncated
    
    def _validate_and_truncate_description(self, description: str) -> str:
        """Validate description character count and truncate if needed."""
        if len(description) <= self.desc_max:
            return description
        
        # Truncate at sentence boundary if possible
        truncated = description[:self.desc_max]
        last_period = truncated.rfind('.')
        if last_period > self.desc_min:
            truncated = truncated[:last_period + 1]
        else:
            # Truncate at word boundary
            last_space = truncated.rfind(' ')
            if last_space > self.desc_min:
                truncated = truncated[:last_space]
        
        logger.warning(f"Description truncated from {len(description)} to {len(truncated)} chars")
        return truncated
