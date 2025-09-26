#!/usr/bin/env python3
"""
Category and Subcategory-Aware Prompt Enhancement System - Organized Version

Extends the material-aware prompt system to provide category and subcategory-specific
context for relative data like min/max ranges, typical values, and comparative analysis.

Migrated from ai_research/prompt_exceptions/category_aware_enhancer.py
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class CategoryLevel(Enum):
    """Levels of categorization for contextual awareness"""
    BROAD = "broad"           # General material type (metal, ceramic, etc.)
    CATEGORY = "category"     # Specific category (aluminum_alloys, hardwoods)
    SUBCATEGORY = "subcategory"  # Fine-grained subcategory (6061_aluminum, red_oak)


@dataclass
class RelativeDataRange:
    """Range information for category-aware relative data positioning"""
    property_name: str
    category: str
    subcategory: Optional[str] = None
    min_value: float = 0.0
    max_value: float = 100.0
    typical_min: float = 25.0
    typical_max: float = 75.0
    unit: str = ""
    description: str = ""
    context_notes: List[str] = field(default_factory=list)


@dataclass
class CategoryContext:
    """Category-specific context for prompt enhancement"""
    category: str
    subcategory: Optional[str] = None
    relative_ranges: Dict[str, RelativeDataRange] = field(default_factory=dict)
    comparison_categories: List[str] = field(default_factory=list)
    distinctive_properties: List[str] = field(default_factory=list)
    common_applications: List[str] = field(default_factory=list)
    processing_considerations: List[str] = field(default_factory=list)


class CategoryAwarePromptEnhancer:
    """
    Enhanced prompt system with category and subcategory-aware relative data handling
    
    Provides contextual enhancement based on:
    - Material category positioning within broader ranges
    - Subcategory-specific refinements
    - Relative comparisons to similar materials
    - Range-aware min/max guidance
    """
    
    def __init__(self, materials_yaml_path: Optional[str] = None):
        """
        Initialize category-aware prompt enhancer
        
        Args:
            materials_yaml_path: Path to materials.yaml for range data
        """
        self.materials_yaml_path = materials_yaml_path
        self.category_contexts = {}
        self.relative_ranges = {}
        
        # Load category contexts and relative ranges
        self._load_category_contexts()
        self._load_relative_ranges()
        
        logger.info(f"Loaded {len(self.category_contexts)} category contexts")
        logger.info(f"Loaded {len(self.relative_ranges)} relative ranges")
    
    def _load_category_contexts(self):
        """Load category and subcategory context information"""
        
        # Define category contexts with relative positioning
        self.category_contexts = {
            'metal': CategoryContext(
                category='metal',
                comparison_categories=['ceramic', 'plastic', 'wood'],
                distinctive_properties=['electrical_conductivity', 'thermal_conductivity', 'ductility'],
                common_applications=['structural', 'electrical', 'heat_transfer'],
                processing_considerations=['oxidation_resistance', 'work_hardening', 'thermal_expansion']
            ),
            'ceramic': CategoryContext(
                category='ceramic',
                comparison_categories=['metal', 'glass', 'stone'],
                distinctive_properties=['hardness', 'brittleness', 'thermal_stability'],
                common_applications=['wear_resistance', 'high_temperature', 'electrical_insulation'],
                processing_considerations=['thermal_shock_resistance', 'fracture_toughness']
            ),
            'wood': CategoryContext(
                category='wood',
                comparison_categories=['plastic', 'composite'],
                distinctive_properties=['grain_structure', 'moisture_content', 'anisotropy'],
                common_applications=['construction', 'furniture', 'paper'],
                processing_considerations=['thermal_degradation', 'moisture_sensitivity', 'grain_direction']
            ),
            'plastic': CategoryContext(
                category='plastic',
                comparison_categories=['metal', 'ceramic', 'composite'],
                distinctive_properties=['polymer_structure', 'glass_transition', 'chemical_resistance'],
                common_applications=['packaging', 'automotive', 'consumer_goods'],
                processing_considerations=['thermal_degradation', 'UV_sensitivity', 'stress_cracking']
            ),
            'composite': CategoryContext(
                category='composite',
                comparison_categories=['metal', 'plastic'],
                distinctive_properties=['fiber_matrix_interface', 'anisotropy', 'layup_configuration'],
                common_applications=['aerospace', 'automotive', 'sporting_goods'],
                processing_considerations=['delamination', 'fiber_orientation', 'resin_degradation']
            )
        }
        
        # Add subcategory contexts
        self._add_subcategory_contexts()
    
    def _add_subcategory_contexts(self):
        """Add subcategory-specific contexts"""
        
        # Metal subcategories
        self.category_contexts['aluminum_alloy'] = CategoryContext(
            category='metal',
            subcategory='aluminum_alloy',
            comparison_categories=['steel', 'titanium', 'copper'],
            distinctive_properties=['low_density', 'corrosion_resistance', 'formability'],
            processing_considerations=['oxide_layer', 'work_hardening', 'heat_treatment']
        )
        
        self.category_contexts['steel'] = CategoryContext(
            category='metal',
            subcategory='steel',
            comparison_categories=['aluminum', 'titanium', 'cast_iron'],
            distinctive_properties=['high_strength', 'magnetic', 'hardenability'],
            processing_considerations=['oxidation', 'carbide_formation', 'quenching']
        )
        
        # Wood subcategories
        self.category_contexts['hardwood'] = CategoryContext(
            category='wood',
            subcategory='hardwood',
            comparison_categories=['softwood', 'engineered_wood'],
            distinctive_properties=['density', 'grain_complexity', 'durability'],
            processing_considerations=['machining_difficulty', 'seasoning_requirements']
        )
        
        self.category_contexts['softwood'] = CategoryContext(
            category='wood',
            subcategory='softwood',
            comparison_categories=['hardwood', 'plywood'],
            distinctive_properties=['resin_content', 'growth_rate', 'workability'],
            processing_considerations=['resin_bleeding', 'grain_tear_out']
        )
        
        # Ceramic subcategories
        self.category_contexts['oxide_ceramic'] = CategoryContext(
            category='ceramic',
            subcategory='oxide_ceramic',
            comparison_categories=['carbide_ceramic', 'nitride_ceramic'],
            distinctive_properties=['chemical_inertness', 'high_temperature_stability'],
            processing_considerations=['sintering_temperature', 'thermal_shock']
        )
    
    def _load_relative_ranges(self):
        """Load relative data ranges for different categories"""
        
        # Load default relative ranges
        self.relative_ranges = {
            # Metal ranges
            'metal_density': RelativeDataRange(
                property_name='density',
                category='metal',
                min_value=2.7,  # Aluminum
                max_value=19.3,  # Tungsten
                typical_min=7.0,
                typical_max=8.5,
                unit='g/cm³',
                description='Metal density range'
            ),
            'metal_thermal_conductivity': RelativeDataRange(
                property_name='thermal_conductivity',
                category='metal',
                min_value=15,   # Stainless steel
                max_value=400,  # Silver
                typical_min=50,
                typical_max=200,
                unit='W/m·K',
                description='Metal thermal conductivity range'
            ),
            
            # Wood ranges
            'wood_density': RelativeDataRange(
                property_name='density',
                category='wood',
                min_value=0.3,   # Balsa
                max_value=1.2,   # Lignum vitae
                typical_min=0.4,
                typical_max=0.8,
                unit='g/cm³',
                description='Wood density range'
            ),
            'wood_moisture_content': RelativeDataRange(
                property_name='moisture_content',
                category='wood',
                min_value=6,     # Kiln dried
                max_value=30,    # Green wood
                typical_min=8,
                typical_max=15,
                unit='%',
                description='Wood moisture content range'
            ),
            
            # Ceramic ranges
            'ceramic_density': RelativeDataRange(
                property_name='density',
                category='ceramic',
                min_value=2.0,   # Porous ceramics
                max_value=6.0,   # Dense ceramics
                typical_min=3.0,
                typical_max=4.5,
                unit='g/cm³',
                description='Ceramic density range'
            ),
            'ceramic_hardness': RelativeDataRange(
                property_name='hardness',
                category='ceramic',
                min_value=6,     # Mohs scale
                max_value=10,    # Diamond
                typical_min=7,
                typical_max=9,
                unit='Mohs',
                description='Ceramic hardness range'
            ),
        }
        
        logger.info("Loaded default relative ranges")
    
    def enhance_prompt_with_category_awareness(
        self,
        base_prompt: str,
        material_name: str,
        material_data: Dict[str, Any],
        component_type: str = None
    ) -> str:
        """
        Enhance prompt with category and subcategory-aware context
        
        Args:
            base_prompt: Base prompt to enhance
            material_name: Name of the material
            material_data: Material property data
            component_type: Type of component being generated
            
        Returns:
            Enhanced prompt with category-aware context
        """
        try:
            # Extract category and subcategory
            material_category = material_data.get('category', 'unknown')
            material_subcategory = material_data.get('subcategory', None)
            
            # Get category context
            context = self._get_category_context(material_category, material_subcategory)
            if not context:
                return base_prompt
            
            # Build enhanced prompt sections
            enhanced_sections = []
            
            # 1. Category-specific context
            category_section = self._build_category_context_section(
                context, material_name, material_category, material_subcategory
            )
            if category_section:
                enhanced_sections.append(category_section)
            
            # 2. Relative data context
            relative_section = self._build_relative_data_section(
                material_data, material_category
            )
            if relative_section:
                enhanced_sections.append(relative_section)
            
            # 3. Comparative analysis
            comparison_section = self._build_comparison_section(
                context, material_name, material_category
            )
            if comparison_section:
                enhanced_sections.append(comparison_section)
            
            # 4. Processing considerations
            processing_section = self._build_processing_section(context, material_category)
            if processing_section:
                enhanced_sections.append(processing_section)
            
            # 5. Component-specific guidance
            component_section = self._build_component_specific_section(
                component_type, material_category
            )
            if component_section:
                enhanced_sections.append(component_section)
            
            # Combine with base prompt
            if enhanced_sections:
                enhanced_content = "\n\n".join(enhanced_sections)
                return f"{base_prompt}\n\n{enhanced_content}"
            
            return base_prompt
            
        except Exception as e:
            logger.error(f"Error enhancing prompt with category awareness: {e}")
            return base_prompt
    
    def _get_category_context(self, category: str, subcategory: str = None) -> Optional[CategoryContext]:
        """Get appropriate category context"""
        
        # Try subcategory first if available
        if subcategory and subcategory in self.category_contexts:
            return self.category_contexts[subcategory]
        
        # Fall back to main category
        if category in self.category_contexts:
            return self.category_contexts[category]
        
        return None
    
    def _build_category_context_section(
        self, 
        context: CategoryContext, 
        material_name: str,
        category: str,
        subcategory: str = None
    ) -> str:
        """Build category-specific context section"""
        
        subcategory_text = f" - {subcategory.title().replace('_', ' ')}" if subcategory else ""
        
        lines = [
            f"### Category-Specific Context",
            f"Material Category: {category.title()}{subcategory_text}",
        ]
        
        if context.distinctive_properties:
            properties_text = ", ".join(context.distinctive_properties[:3])  # Limit to 3
            lines.append(f"Key Properties: {properties_text}")
        
        return "\n".join(lines)
    
    def _build_relative_data_section(self, material_data: Dict[str, Any], category: str) -> str:
        """Build relative data positioning section"""
        
        lines = ["### Relative Data Context"]
        
        # Find applicable ranges
        applicable_ranges = [
            range_data for key, range_data in self.relative_ranges.items()
            if range_data.category == category
        ]
        
        for range_data in applicable_ranges[:3]:  # Limit to prevent bloat
            property_name = range_data.property_name
            
            # Check if we have data for this property
            property_value = material_data.get(property_name)
            if property_value:
                position_text = self._calculate_relative_position(property_value, range_data)
                lines.append(f"- {property_name.replace('_', ' ').title()}: {property_value} (Position: {position_text})")
        
        return "\n".join(lines) if len(lines) > 1 else ""
    
    def _calculate_relative_position(self, value_str: str, range_data: RelativeDataRange) -> str:
        """Calculate relative position within range"""
        
        try:
            # Extract numeric value
            import re
            numbers = re.findall(r'(\d+\.?\d*)', str(value_str))
            if not numbers:
                return "Position unclear"
            
            value = float(numbers[0])
            
            # Calculate position
            range_span = range_data.max_value - range_data.min_value
            if range_span <= 0:
                return "Range error"
            
            position = (value - range_data.min_value) / range_span
            
            # Categorize position
            if position < 0.2:
                position_desc = "Low"
            elif position < 0.4:
                position_desc = "Low-Medium"
            elif position < 0.6:
                position_desc = "Medium"
            elif position < 0.8:
                position_desc = "Medium-High"
            else:
                position_desc = "High"
            
            return f"{position_desc} within {range_data.category} range {range_data.min_value}-{range_data.max_value} {range_data.unit}"
            
        except (ValueError, IndexError):
            return "Position calculation failed"
    
    def _build_comparison_section(
        self, 
        context: CategoryContext, 
        material_name: str, 
        category: str
    ) -> str:
        """Build comparative analysis section"""
        
        if not context.comparison_categories:
            return ""
        
        comparison_text = ", ".join(context.comparison_categories)
        distinctive_text = context.distinctive_properties[0] if context.distinctive_properties else "unique properties"
        
        lines = [
            "### Comparative Analysis",
            f"Compared to {comparison_text}, {material_name} as a {category} material typically exhibits:",
            f"- Enhanced {distinctive_text.replace('_', ' ')}"
        ]
        
        return "\n".join(lines)
    
    def _build_processing_section(self, context: CategoryContext, category: str) -> str:
        """Build processing considerations section"""
        
        if not context.processing_considerations:
            return ""
        
        lines = ["### Processing Considerations"]
        for consideration in context.processing_considerations[:2]:  # Limit to 2
            lines.append(f"- {consideration.replace('_', ' ').title()}")
        
        return "\n".join(lines)
    
    def _build_component_specific_section(self, component_type: str, category: str) -> str:
        """Build component-specific guidance"""
        
        if not component_type:
            return ""
        
        lines = [
            f"### {component_type.title()} Specific Guidance",
            f"Property generation for {category} materials:",
            "- Use category-appropriate units and ranges"
        ]
        
        return "\n".join(lines)


# Global enhancer instance
category_enhancer = CategoryAwarePromptEnhancer()


def enhance_prompt_with_category_awareness(
    base_prompt: str,
    material_name: str,
    material_data: Dict[str, Any],
    component_type: str = None
) -> str:
    """
    Global function to enhance prompts with category awareness
    
    Args:
        base_prompt: Base prompt to enhance
        material_name: Name of the material
        material_data: Material property data
        component_type: Type of component being generated
        
    Returns:
        Enhanced prompt with category-aware context
    """
    return category_enhancer.enhance_prompt_with_category_awareness(
        base_prompt, material_name, material_data, component_type
    )


if __name__ == "__main__":
    # Test category-aware enhancement
    enhancer = CategoryAwarePromptEnhancer()
    
    # Test wood enhancement
    wood_data = {
        'name': 'Oak',
        'category': 'wood',
        'subcategory': 'hardwood',
        'density': '0.75 g/cm³',
        'moisture_content': '8 %'
    }
    
    base_prompt = "Generate properties for Oak."
    enhanced_prompt = enhancer.enhance_prompt_with_category_awareness(
        base_prompt, 'Oak', wood_data, 'metricsproperties'
    )
    
    print("=== ENHANCED WOOD PROMPT ===")
    print(enhanced_prompt[:800] + "...")