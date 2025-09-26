#!/usr/bin/env python3
"""
Category and Subcategory-Aware Prompt Enhancement System

Extends the material-aware prompt system to provide category and subcategory-specific
context for relative data like min/max ranges, typical values, and comparative analysis.

This system provides:
- Category-specific range contexts (metals vs ceramics vs woods)
- Subcategory refinement (hardwoods vs softwoods, ferrous vs non-ferrous)
- Relative positioning within category ranges
- Contextual min/max guidance
- Comparative analysis prompts
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
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
    context_notes: List[str] = None


@dataclass
class CategoryContext:
    """Category-specific context for prompt enhancement"""
    category: str
    subcategory: Optional[str] = None
    relative_ranges: Dict[str, RelativeDataRange] = None
    comparison_categories: List[str] = None
    distinctive_properties: List[str] = None
    common_applications: List[str] = None
    processing_considerations: List[str] = None


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
            processing_considerations=['moisture_movement', 'machining_difficulty', 'finishing']
        )
        
        self.category_contexts['softwood'] = CategoryContext(
            category='wood',
            subcategory='softwood',
            comparison_categories=['hardwood', 'plywood'],
            distinctive_properties=['resin_content', 'growth_rings', 'workability'],
            processing_considerations=['resin_bleeding', 'grain_tear_out', 'drying_checks']
        )
        
        # Ceramic subcategories
        self.category_contexts['oxide_ceramic'] = CategoryContext(
            category='ceramic',
            subcategory='oxide_ceramic',
            comparison_categories=['carbide_ceramic', 'nitride_ceramic'],
            distinctive_properties=['chemical_inertness', 'electrical_insulation', 'thermal_stability'],
            processing_considerations=['sintering_temperature', 'thermal_shock', 'phase_transitions']
        )
    
    def _load_relative_ranges(self):
        """Load relative range data for category-aware positioning"""
        
        # Try to load from materials.yaml if available
        if self.materials_yaml_path and Path(self.materials_yaml_path).exists():
            try:
                with open(self.materials_yaml_path, 'r') as f:
                    materials_data = yaml.safe_load(f)
                
                category_ranges = materials_data.get('category_ranges', {})
                self._process_category_ranges(category_ranges)
                
                logger.info("Loaded relative ranges from materials.yaml")
                
            except Exception as e:
                logger.warning(f"Failed to load ranges from materials.yaml: {e}")
                self._load_default_ranges()
        else:
            self._load_default_ranges()
    
    def _process_category_ranges(self, category_ranges: Dict):
        """Process category ranges from materials.yaml"""
        
        for category, ranges in category_ranges.items():
            if isinstance(ranges, dict):
                for prop, range_data in ranges.items():
                    if isinstance(range_data, dict) and 'min' in range_data and 'max' in range_data:
                        self.relative_ranges[f"{category}_{prop}"] = RelativeDataRange(
                            property_name=prop,
                            category=category,
                            min_value=self._extract_numeric(range_data['min']),
                            max_value=self._extract_numeric(range_data['max']),
                            typical_min=self._extract_numeric(range_data.get('typical_min', range_data['min'])),
                            typical_max=self._extract_numeric(range_data.get('typical_max', range_data['max'])),
                            unit=self._extract_unit(str(range_data['min'])),
                            description=f"{prop} range for {category} materials"
                        )
    
    def _load_default_ranges(self):
        """Load default relative ranges for common material properties"""
        
        # Define common property ranges by category
        default_ranges = {
            # Metal ranges
            'metal_density': RelativeDataRange(
                'density', 'metal', min_value=2.7, max_value=19.3, 
                typical_min=7.0, typical_max=8.9, unit='g/cm³',
                description='Density range for metallic materials'
            ),
            'metal_thermal_conductivity': RelativeDataRange(
                'thermal_conductivity', 'metal', min_value=15, max_value=400,
                typical_min=50, typical_max=200, unit='W/m·K',
                description='Thermal conductivity range for metals'
            ),
            
            # Ceramic ranges  
            'ceramic_density': RelativeDataRange(
                'density', 'ceramic', min_value=2.0, max_value=6.0,
                typical_min=3.5, typical_max=4.5, unit='g/cm³',
                description='Density range for ceramic materials'
            ),
            'ceramic_hardness': RelativeDataRange(
                'hardness', 'ceramic', min_value=6, max_value=10,
                typical_min=8, typical_max=9, unit='Mohs',
                description='Hardness range for ceramics'
            ),
            
            # Wood ranges
            'wood_density': RelativeDataRange(
                'density', 'wood', min_value=0.3, max_value=1.2,
                typical_min=0.5, typical_max=0.8, unit='g/cm³',
                description='Density range for wood materials'
            ),
            'wood_moisture_content': RelativeDataRange(
                'moisture_content', 'wood', min_value=6, max_value=30,
                typical_min=8, typical_max=12, unit='%',
                description='Moisture content range for seasoned wood'
            )
        }
        
        self.relative_ranges = default_ranges
        logger.info("Loaded default relative ranges")
    
    def _extract_numeric(self, value: Any) -> float:
        """Extract numeric value from string or number"""
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            import re
            match = re.search(r'(\d+(?:\.\d+)?)', value)
            if match:
                return float(match.group(1))
        
        return 0.0
    
    def _extract_unit(self, value_str: str) -> str:
        """Extract unit from value string"""
        import re
        unit_match = re.search(r'([a-zA-Z/°×·⁻⁰¹²³⁴⁵⁶⁷⁸⁹%]+)$', str(value_str).strip())
        return unit_match.group(1) if unit_match else ""
    
    def enhance_prompt_with_category_context(self, base_prompt: str, material_name: str,
                                           material_data: Dict, component_type: str) -> str:
        """
        Enhance prompt with category and subcategory-aware context
        
        Args:
            base_prompt: Original prompt template
            material_name: Name of material
            material_data: Material property data
            component_type: Type of component being generated
            
        Returns:
            Enhanced prompt with category-specific relative data context
        """
        
        category = material_data.get('category', '').lower()
        subcategory = material_data.get('subcategory', '').lower()
        
        # Get category context
        category_context = self._get_category_context(category, subcategory)
        
        if not category_context:
            return base_prompt
        
        # Build enhanced prompt with category context
        enhanced_prompt = base_prompt + "\n\n"
        
        # Add category-specific context
        enhanced_prompt += f"## Category-Specific Context for {material_name}\n"
        enhanced_prompt += f"Material Category: {category.title()}"
        
        if subcategory:
            enhanced_prompt += f" - {subcategory.title()}\n"
        else:
            enhanced_prompt += "\n"
        
        # Add relative positioning context
        relative_context = self._generate_relative_positioning_context(
            category, subcategory, material_data
        )
        if relative_context:
            enhanced_prompt += f"\n### Relative Data Context:\n{relative_context}\n"
        
        # Add comparison context
        comparison_context = self._generate_comparison_context(category_context, material_name)
        if comparison_context:
            enhanced_prompt += f"\n### Comparative Analysis:\n{comparison_context}\n"
        
        # Add processing considerations
        processing_context = self._generate_processing_context(category_context)
        if processing_context:
            enhanced_prompt += f"\n### Processing Considerations:\n{processing_context}\n"
        
        # Add component-specific enhancements
        component_context = self._generate_component_specific_context(
            component_type, category_context, material_data
        )
        if component_context:
            enhanced_prompt += f"\n### {component_type.title()} Specific Guidance:\n{component_context}\n"
        
        return enhanced_prompt
    
    def _get_category_context(self, category: str, subcategory: Optional[str] = None) -> Optional[CategoryContext]:
        """Get category context with subcategory fallback"""
        
        # Try subcategory first if available
        if subcategory:
            subcategory_key = f"{category}_{subcategory}"
            if subcategory_key in self.category_contexts:
                return self.category_contexts[subcategory_key]
            
            # Try direct subcategory match
            if subcategory in self.category_contexts:
                return self.category_contexts[subcategory]
        
        # Fall back to category
        return self.category_contexts.get(category)
    
    def _generate_relative_positioning_context(self, category: str, subcategory: Optional[str],
                                             material_data: Dict) -> str:
        """Generate relative positioning context for material properties"""
        
        context_parts = []
        
        # Check each property in material_data against category ranges
        for prop_name, prop_value in material_data.items():
            if prop_name in ['name', 'category', 'subcategory']:
                continue
            
            # Look for range data
            range_key = f"{category}_{prop_name}"
            if range_key in self.relative_ranges:
                range_data = self.relative_ranges[range_key]
                
                # Extract numeric value
                numeric_value = self._extract_numeric(prop_value)
                
                if numeric_value > 0:
                    # Calculate relative position
                    relative_position = self._calculate_relative_position(
                        numeric_value, range_data
                    )
                    
                    context_parts.append(
                        f"- {prop_name.title()}: {prop_value} "
                        f"(Position: {relative_position} within {category} range "
                        f"{range_data.min_value}-{range_data.max_value} {range_data.unit})"
                    )
        
        return "\n".join(context_parts) if context_parts else ""
    
    def _calculate_relative_position(self, value: float, range_data: RelativeDataRange) -> str:
        """Calculate relative position description within range"""
        
        total_range = range_data.max_value - range_data.min_value
        position = (value - range_data.min_value) / total_range
        
        if position < 0.2:
            return "Low"
        elif position < 0.4:
            return "Low-Medium" 
        elif position < 0.6:
            return "Medium"
        elif position < 0.8:
            return "Medium-High"
        else:
            return "High"
    
    def _generate_comparison_context(self, category_context: CategoryContext, material_name: str) -> str:
        """Generate comparative context with similar materials"""
        
        if not category_context.comparison_categories:
            return ""
        
        context = f"Compared to {', '.join(category_context.comparison_categories)}, "
        context += f"{material_name} as a {category_context.category} material typically exhibits:\n"
        
        if category_context.distinctive_properties:
            for prop in category_context.distinctive_properties[:3]:  # Top 3 distinctive properties
                context += f"- Enhanced {prop.replace('_', ' ')}\n"
        
        return context
    
    def _generate_processing_context(self, category_context: CategoryContext) -> str:
        """Generate processing-specific context"""
        
        if not category_context.processing_considerations:
            return ""
        
        context = "Key processing considerations:\n"
        for consideration in category_context.processing_considerations:
            context += f"- {consideration.replace('_', ' ').title()}\n"
        
        return context
    
    def _generate_component_specific_context(self, component_type: str, 
                                           category_context: CategoryContext,
                                           material_data: Dict) -> str:
        """Generate component-specific contextual guidance"""
        
        if component_type == 'frontmatter':
            return self._generate_frontmatter_context(category_context, material_data)
        elif component_type in ['metricsproperties', 'properties']:
            return self._generate_properties_context(category_context, material_data)
        elif component_type in ['metricsmachinesettings', 'machinesettings']:
            return self._generate_machine_settings_context(category_context, material_data)
        
        return ""
    
    def _generate_frontmatter_context(self, category_context: CategoryContext, material_data: Dict) -> str:
        """Generate frontmatter-specific guidance"""
        
        context = f"For {category_context.category} materials, emphasize:\n"
        context += "- Property ranges should reflect category-typical values\n"
        context += "- Include category-specific processing parameters\n"
        
        if category_context.distinctive_properties:
            context += f"- Highlight distinctive properties: {', '.join(category_context.distinctive_properties[:2])}\n"
        
        return context
    
    def _generate_properties_context(self, category_context: CategoryContext, material_data: Dict) -> str:
        """Generate properties component-specific guidance"""
        
        context = f"Property generation for {category_context.category} materials:\n"
        context += "- Use category-appropriate units and ranges\n"
        context += "- Include min/max values within category bounds\n"
        
        if category_context.distinctive_properties:
            context += f"- Focus on: {', '.join(category_context.distinctive_properties)}\n"
        
        return context
    
    def _generate_machine_settings_context(self, category_context: CategoryContext, material_data: Dict) -> str:
        """Generate machine settings-specific guidance"""
        
        category = category_context.category
        
        if category == 'metal':
            return "Metal processing: Focus on thermal conductivity effects, oxidation prevention, power density requirements"
        elif category == 'ceramic':
            return "Ceramic processing: Consider brittleness, thermal shock sensitivity, high power requirements"
        elif category == 'wood':
            return "Wood processing: Account for moisture content, grain structure, thermal degradation limits"
        elif category == 'plastic':
            return "Plastic processing: Consider polymer degradation, glass transition effects, low power requirements"
        
        return f"Processing guidance for {category} materials"


# Global instance for easy access
category_aware_enhancer = CategoryAwarePromptEnhancer()


def enhance_prompt_with_category_awareness(base_prompt: str, material_name: str,
                                         material_data: Dict, component_type: str) -> str:
    """
    Global function to enhance any prompt with category and subcategory awareness
    
    Args:
        base_prompt: Original prompt template
        material_name: Name of material
        material_data: Material property data 
        component_type: Type of component being generated
        
    Returns:
        Enhanced prompt with category-specific relative data context
    """
    return category_aware_enhancer.enhance_prompt_with_category_context(
        base_prompt, material_name, material_data, component_type
    )


if __name__ == "__main__":
    # Test the category-aware enhancement system
    enhancer = CategoryAwarePromptEnhancer()
    
    # Test materials
    test_materials = {
        'aluminum': {
            'name': 'Aluminum',
            'category': 'metal',
            'subcategory': 'non_ferrous',
            'density': '2.7 g/cm³',
            'thermal_conductivity': '205 W/m·K'
        },
        'oak': {
            'name': 'Oak',
            'category': 'wood', 
            'subcategory': 'hardwood',
            'density': '0.75 g/cm³',
            'moisture_content': '10 %'
        }
    }
    
    base_prompt = "Generate comprehensive material data with appropriate ranges and context."
    
    for material_name, material_data in test_materials.items():
        print(f"\n=== CATEGORY-AWARE ENHANCEMENT FOR {material_name.upper()} ===")
        
        enhanced_prompt = enhancer.enhance_prompt_with_category_context(
            base_prompt, material_name, material_data, 'frontmatter'
        )
        
        print(enhanced_prompt[:800] + "..." if len(enhanced_prompt) > 800 else enhanced_prompt)