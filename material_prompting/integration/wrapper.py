#!/usr/bin/env python3
"""
Material Prompting Integration Wrapper

Materials Research and Population System for Z-Beam Generator

KEY PURPOSE: Research and populate materials.yaml and frontmatter with
comprehensive, scientifically accurate material data.

Core Research Functions:
- Materials.yaml gap analysis and intelligent population
- Frontmatter metadata research and enhancement
- Material property validation and completion
- Machine settings research based on material science
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class MaterialPromptingIntegration:
    """
    Integration wrapper for material prompting system
    
    Provides unified access to:
    - Material-aware prompt generation
    - Property enhancement and validation
    - Machine settings optimization
    - Materials.yaml updates
    - Component generator integration
    """
    
    def __init__(self):
        """Initialize material prompting integration"""
        # Lazy load components for efficient resource management
        self._material_generator = None
        self._property_enhancer = None  # Fixed: should be _property_enhancer not _properties_enhancer
        self._machine_settings_enhancer = None
        self._materials_updater = None
        self._frontmatter_researcher = None
        
        logger.info("Material Prompting Integration initialized")
    
    @property
    def material_generator(self):
        """Lazy-loaded material-aware prompt generator"""
        if self._material_generator is None:
            from ..core.material_aware_generator import MaterialAwarePromptGenerator
            self._material_generator = MaterialAwarePromptGenerator()
        return self._material_generator
    
    @property
    def property_enhancer(self):
        """Lazy-loaded property enhancer"""
        if self._property_enhancer is None:
            from ..properties.enhancer import MaterialPropertiesEnhancer
            self._property_enhancer = MaterialPropertiesEnhancer()
        return self._property_enhancer
    
    @property
    def settings_optimizer(self):
        """Lazy-loaded settings optimizer"""
        if self._settings_optimizer is None:
            from ..machine_settings.optimizer import MaterialMachineSettingsEnhancer
            self._settings_optimizer = MaterialMachineSettingsEnhancer()
        return self._settings_optimizer
    
    @property
    def materials_updater(self):
        """Lazy-loaded materials.yaml updater"""
        if self._materials_updater is None:
            from ..generators.materials_yaml_updater import MaterialsYamlUpdater
            self._materials_updater = MaterialsYamlUpdater()
        return self._materials_updater
    
    @property
    def frontmatter_researcher(self):
        """Lazy load frontmatter researcher"""
        if self._frontmatter_researcher is None:
            try:
                from ..generators.frontmatter_researcher import FrontmatterResearcher
                self._frontmatter_researcher = FrontmatterResearcher(self.material_generator)
            except ImportError:
                self._frontmatter_researcher = None
        return self._frontmatter_researcher
    
    def generate_material_aware_prompt(
        self,
        component_type: str,
        material_name: str,
        material_category: str = None,
        material_data: Dict[str, Any] = None,
        base_prompt: str = None,
        **kwargs
    ) -> str:
        """
        Generate material-aware prompt for any component
        
        Args:
            component_type: Component type (metricsproperties, text, etc.)
            material_name: Material name
            material_category: Material category (optional, will be inferred)
            material_data: Material property data (optional)
            base_prompt: Custom base prompt (optional)
            **kwargs: Additional template variables
            
        Returns:
            Enhanced material-aware prompt
        """
        return self.material_generator.generate_material_aware_prompt(
            component_type=component_type,
            material_name=material_name,
            material_category=material_category,
            material_data=material_data,
            base_prompt=base_prompt,
            **kwargs
        )
    
    def enhance_material_properties(
        self,
        material_name: str,
        material_category: str,
        existing_properties: Dict[str, Any],
        material_data: Dict[str, Any] = None
    ):
        """
        Enhance material properties with category-aware validation
        
        Args:
            material_name: Material name
            material_category: Material category
            existing_properties: Current property data
            material_data: Additional material context
            
        Returns:
            PropertyEnhancementResult with enhanced properties
        """
        return self.property_enhancer.enhance_material_properties(
            material_name=material_name,
            material_category=material_category,
            existing_properties=existing_properties,
            material_data=material_data
        )
    
    def optimize_machine_settings(
        self,
        material_name: str,
        material_category: str,
        material_properties: Dict[str, Any],
        processing_mode: str = "cleaning"
    ):
        """
        Optimize laser machine settings for material
        
        Args:
            material_name: Material name
            material_category: Material category
            material_properties: Material property data
            processing_mode: Processing mode (cleaning, cutting, etc.)
            
        Returns:
            MachineSettingsResult with optimized settings
        """
        from ..machine_settings.optimizer import ProcessingMode
        
        # Convert string to enum
        mode_map = {
            'cleaning': ProcessingMode.CLEANING,
            'cutting': ProcessingMode.CUTTING,
            'welding': ProcessingMode.WELDING,
            'marking': ProcessingMode.MARKING,
            'texturing': ProcessingMode.TEXTURING
        }
        
        processing_enum = mode_map.get(processing_mode.lower(), ProcessingMode.CLEANING)
        
        return self.settings_optimizer.optimize_machine_settings(
            material_name=material_name,
            material_category=material_category,
            material_properties=material_properties,
            processing_mode=processing_enum
        )
    
    def update_materials_yaml(
        self,
        target_materials: Optional[list] = None,
        backup: bool = True,
        validate_only: bool = False
    ):
        """
        Update materials.yaml with enhanced properties and settings
        
        Args:
            target_materials: Specific materials to update (None = all)
            backup: Create backup before updating
            validate_only: Only validate without making changes
            
        Returns:
            UpdateResult with operation details
        """
        return self.materials_updater.update_materials_yaml(
            target_materials=target_materials,
            backup=backup,
            validate_only=validate_only
        )
    
    def analyze_materials_gaps(self) -> Dict[str, list]:
        """
        Analyze materials.yaml for gaps and optimization opportunities
        
        Returns:
            Dictionary mapping material names to lists of missing data
        """
        return self.materials_updater.analyze_materials_gaps()
    
    def research_frontmatter_metadata(
        self,
        material_name: str,
        material_category: str = None,
        existing_metadata: Dict[str, Any] = None
    ):
        """
        Research and populate frontmatter metadata for material
        
        Args:
            material_name: Material name
            material_category: Material category (optional, will be inferred)
            existing_metadata: Existing frontmatter data to enhance
            
        Returns:
            FrontmatterResearchResult with researched metadata
        """
        if not material_category:
            material_category = self._infer_material_category(material_name)
            
        if not self.frontmatter_researcher:
            raise ImportError("FrontmatterResearcher not available")
            
        return self.frontmatter_researcher.research_frontmatter_metadata(
            material_name=material_name,
            material_category=material_category,
            existing_metadata=existing_metadata
        )
    
    def get_component_wrapper(self, component_generator, component_type: str):
        """
        Wrap existing component generator with material-aware capabilities
        
        Args:
            component_generator: Existing generator to wrap
            component_type: Type of component
            
        Returns:
            Material-aware wrapped generator
        """
        try:
            from .component_wrapper import MaterialAwareComponentWrapper
            return MaterialAwareComponentWrapper(component_generator, component_type)
        except ImportError:
            logger.warning("Component wrapper not available, using original generator")
            return component_generator
    
    def validate_material_content(
        self,
        component_type: str,
        material_category: str,
        generated_content: Dict[str, Any]
    ):
        """
        Validate generated content against material-specific rules
        
        Args:
            component_type: Type of component
            material_category: Material category
            generated_content: Content to validate
            
        Returns:
            (is_valid, list_of_validation_errors)
        """
        return self.material_generator.validate_generated_content(
            component_type, material_category, generated_content
        )


# Global instance for convenience access
material_prompting = MaterialPromptingIntegration()


def research_frontmatter_metadata(
    material_name: str, 
    material_category: str = None,
    existing_metadata: Dict[str, Any] = None
):
    """
    Convenience function for frontmatter metadata research
    
    Args:
        material_name: Material name
        material_category: Material category (optional)
        existing_metadata: Existing frontmatter data to enhance
        
    Returns:
        FrontmatterResearchResult with researched metadata
    """
    return material_prompting.research_frontmatter_metadata(
        material_name=material_name,
        material_category=material_category,
        existing_metadata=existing_metadata
    )


# Convenience functions for backward compatibility
def generate_material_aware_prompt(
    component_type: str,
    material_name: str,
    material_category: str = None,
    material_data: Dict[str, Any] = None,
    **kwargs
) -> str:
    """Generate material-aware prompt (convenience function)"""
    return material_prompting.generate_material_aware_prompt(
        component_type, material_name, material_category, material_data, **kwargs
    )


def enhance_material_properties(
    material_name: str,
    material_category: str,
    existing_properties: Dict[str, Any]
):
    """Enhance material properties (convenience function)"""
    return material_prompting.enhance_material_properties(
        material_name, material_category, existing_properties
    )


def optimize_machine_settings(
    material_name: str,
    material_category: str,
    material_properties: Dict[str, Any]
):
    """Optimize machine settings (convenience function)"""
    return material_prompting.optimize_machine_settings(
        material_name, material_category, material_properties
    )


def update_materials_yaml(target_materials: Optional[list] = None):
    """Update materials.yaml (convenience function)"""
    return material_prompting.update_materials_yaml(target_materials)


if __name__ == "__main__":
    # Test integration system
    integration = MaterialPromptingIntegration()
    
    # Test material-aware prompt generation
    print("=== MATERIAL-AWARE PROMPT TEST ===")
    prompt = integration.generate_material_aware_prompt(
        component_type="metricsproperties",
        material_name="Aluminum 6061",
        material_category="metal"
    )
    print(f"Generated prompt length: {len(prompt)} characters")
    print(f"Prompt preview: {prompt[:200]}...")
    
    # Test property enhancement
    print("\n=== PROPERTY ENHANCEMENT TEST ===")
    aluminum_props = {
        'density': {'value': '2.7 g/cm³'},
        'thermalConductivity': {'value': '167 W/m·K'}
    }
    
    result = integration.enhance_material_properties(
        material_name="Aluminum 6061",
        material_category="metal",
        existing_properties=aluminum_props
    )
    
    print(f"Enhancement success: {result.success}")
    print(f"Enhanced properties: {len(result.enhanced_properties)}")
    print(f"Missing properties: {result.missing_properties}")
    
    # Test gap analysis
    print("\n=== MATERIALS GAPS ANALYSIS ===")
    gaps = integration.analyze_materials_gaps()
    print(f"Materials with gaps: {len(gaps)}")
    
    for material, gap_list in list(gaps.items())[:2]:  # Show first 2
        print(f"{material}: {len(gap_list)} gaps")
    
    print("\n✅ Material Prompting Integration fully operational!")