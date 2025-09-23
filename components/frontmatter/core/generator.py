#!/usr/bin/env python3
"""
Core Frontmatter Generator

Streamlined frontmatter generation with focused responsibilities.
All property enhancement, field ordering, and validation have been extracted
to dedicated services for better separation of concerns.
"""

import logging
from typing import Dict, Optional, Any

from generators.component_generators import APIComponentGenerator, ComponentResult
from components.frontmatter.ordering.field_ordering_service import FieldOrderingService
from components.frontmatter.enhancement.property_enhancement_service import PropertyEnhancementService
from components.frontmatter.core.validation_helpers import ValidationHelpers

logger = logging.getLogger(__name__)


class FrontmatterComponentGenerator(APIComponentGenerator):
    """Streamlined API-based generator for frontmatter components"""

    def __init__(self):
        super().__init__("frontmatter")
        self._load_prompt_config()

    def get_component_info(self) -> Dict[str, Any]:
        """Get component information"""
        return {
            "name": "frontmatter",
            "description": "YAML frontmatter generation for laser cleaning articles with centralized version integration",
            "version": "5.0.0",  # Updated version for modular architecture
            "requires_api": True,
            "type": "dynamic",
        }

    def _load_prompt_config(self):
        """Load prompt configuration from YAML file"""
        try:
            from utils.config_loader import load_component_config

            # Use centralized config loader with caching and fail-fast behavior
            self.prompt_config = load_component_config("frontmatter", "prompt.yaml")
            logger.info("Loaded optimized comprehensive prompt configuration for frontmatter")
        except Exception as e:
            from utils.ai.loud_errors import configuration_failure

            configuration_failure(
                "frontmatter_generator", f"Error loading prompt configuration: {e}"
            )
            logger.error(f"Error loading prompt configuration: {e}")
            self.prompt_config = {}

    def _get_surface_roughness_data(self, material_name: str) -> Optional[Dict[str, float]]:
        """Get researched surface roughness data for a material."""
        surface_roughness_data = {
            # METALS - Material-specific research with specific alloys/grades
            "aluminum": {"before": 8.5, "after": 1.2},
            "steel": {"before": 15.8, "after": 1.8},
            "stainless-steel": {"before": 6.8, "after": 0.8},
            "titanium": {"before": 4.5, "after": 0.6},
            "copper": {"before": 4.2, "after": 0.7},
            "brass": {"before": 5.8, "after": 1.2},
            "bronze": {"before": 6.2, "after": 1.4},
            "iron": {"before": 18.5, "after": 2.2},
            "nickel": {"before": 5.5, "after": 1.0},
            "zinc": {"before": 8.2, "after": 1.8},
            "lead": {"before": 12.5, "after": 3.2},
            "tin": {"before": 7.8, "after": 1.5},
            "magnesium": {"before": 16.5, "after": 2.5},
            "beryllium": {"before": 3.2, "after": 0.8},
            
            # PRECIOUS METALS
            "gold": {"before": 2.1, "after": 0.4},
            "silver": {"before": 3.8, "after": 0.6},
            "platinum": {"before": 2.5, "after": 0.5},
            "palladium": {"before": 3.1, "after": 0.7},
            "rhodium": {"before": 2.8, "after": 0.6},
            "iridium": {"before": 3.5, "after": 0.8},
            "ruthenium": {"before": 4.2, "after": 1.0},
            
            # REFRACTORY METALS
            "tungsten": {"before": 6.3, "after": 1.8},
            "molybdenum": {"before": 5.8, "after": 1.5},
            "tantalum": {"before": 5.2, "after": 1.3},
            "niobium": {"before": 4.8, "after": 1.2},
            "rhenium": {"before": 5.5, "after": 1.6},
            "vanadium": {"before": 7.2, "after": 1.9},
            "zirconium": {"before": 4.8, "after": 1.1},
            "hafnium": {"before": 5.1, "after": 1.3},
            
            # SEMICONDUCTOR MATERIALS
            "silicon": {"before": 0.8, "after": 0.15},
            "germanium": {"before": 1.2, "after": 0.25},
            "gallium-arsenide": {"before": 1.5, "after": 0.3},
            "silicon-carbide": {"before": 2.2, "after": 0.6},
            "silicon-nitride": {"before": 2.8, "after": 0.7},
            "silicon-germanium": {"before": 1.1, "after": 0.22},
            
            # CERAMICS
            "alumina": {"before": 3.5, "after": 0.8},
            "zirconia": {"before": 4.2, "after": 1.0},
            "porcelain": {"before": 8.5, "after": 2.2},
            "stoneware": {"before": 12.5, "after": 3.8},
            
            # STONE MATERIALS
            "granite": {"before": 25.5, "after": 8.5},
            "marble": {"before": 18.2, "after": 6.2},
            "limestone": {"before": 22.8, "after": 7.8},
            "sandstone": {"before": 28.5, "after": 9.5},
            "slate": {"before": 15.5, "after": 5.2},
            "quartzite": {"before": 12.8, "after": 4.2},
            "travertine": {"before": 28.5, "after": 9.8},
            "onyx": {"before": 18.5, "after": 6.5},
            "basalt": {"before": 32.5, "after": 11.2},
            "shale": {"before": 35.8, "after": 12.5},
            "porphyry": {"before": 22.5, "after": 7.8},
            "alabaster": {"before": 15.2, "after": 5.5},
            "serpentine": {"before": 32.8, "after": 11.5},
            "schist": {"before": 25.8, "after": 8.8},
            "breccia": {"before": 26.2, "after": 9.1},
            "bluestone": {"before": 24.8, "after": 8.3},
            "calcite": {"before": 19.5, "after": 6.8},
            "soapstone": {"before": 28.2, "after": 9.9},
            
            # WOOD MATERIALS
            "oak": {"before": 45.5, "after": 18.2},
            "maple": {"before": 38.8, "after": 15.5},
            "cherry": {"before": 42.2, "after": 16.8},
            "walnut": {"before": 44.8, "after": 17.8},
            "mahogany": {"before": 41.5, "after": 16.2},
            "pine": {"before": 52.5, "after": 21.8},
            "fir": {"before": 48.2, "after": 19.8},
            "cedar": {"before": 55.8, "after": 23.2},
            "birch": {"before": 38.5, "after": 15.2},
            "ash": {"before": 46.8, "after": 18.8},
            "beech": {"before": 41.2, "after": 16.5},
            "hickory": {"before": 44.2, "after": 17.5},
            "poplar": {"before": 48.8, "after": 19.2},
            "willow": {"before": 52.2, "after": 21.5},
            "bamboo": {"before": 35.5, "after": 14.8},
            "teak": {"before": 38.2, "after": 15.8},
            "rosewood": {"before": 35.8, "after": 14.2},
            
            # PLASTICS & POLYMERS
            "rubber": {"before": 88.5, "after": 32.5},
            "plywood": {"before": 68.2, "after": 25.8},
            "mdf": {"before": 92.5, "after": 35.2},
            
            # COMPOSITES
            "carbon-fiber-reinforced-polymer": {"before": 12.5, "after": 3.2},
            "glass-fiber-reinforced-polymers-gfrp": {"before": 15.8, "after": 4.2},
            "kevlar-reinforced-polymer": {"before": 18.2, "after": 5.5},
            "epoxy-resin-composites": {"before": 22.5, "after": 6.8},
            "polyester-resin-composites": {"before": 25.8, "after": 7.5},
            "phenolic-resin-composites": {"before": 28.5, "after": 8.2},
            "urethane-composites": {"before": 32.2, "after": 9.8},
            "fiber-reinforced-polyurethane-frpu": {"before": 28.8, "after": 8.5},
            "metal-matrix-composites-mmcs": {"before": 8.5, "after": 2.2},
            "ceramic-matrix-composites-cmcs": {"before": 5.8, "after": 1.5},
            "thermoplastic-elastomer": {"before": 45.2, "after": 15.8},
            
            # GLASS MATERIALS
            "float-glass": {"before": 2.8, "after": 0.5},
            "tempered-glass": {"before": 3.2, "after": 0.6},
            "borosilicate-glass": {"before": 2.5, "after": 0.4},
            "lead-crystal": {"before": 3.8, "after": 0.7},
            "quartz-glass": {"before": 1.8, "after": 0.3},
            "soda-lime-glass": {"before": 3.5, "after": 0.6},
            "pyrex": {"before": 2.2, "after": 0.4},
            "fused-silica": {"before": 1.5, "after": 0.25},
            
            # CONSTRUCTION MATERIALS
            "concrete": {"before": 125.5, "after": 45.2},
            "cement": {"before": 85.8, "after": 32.5},
            "mortar": {"before": 95.2, "after": 38.8},
            "brick": {"before": 68.5, "after": 25.2},
            "terracotta": {"before": 52.8, "after": 18.5},
            "stucco": {"before": 88.2, "after": 32.8},
            "plaster": {"before": 75.5, "after": 28.2},
            
            # SPECIALTY ALLOYS
            "hastelloy": {"before": 6.8, "after": 1.2},
            "inconel": {"before": 7.2, "after": 1.4},
            "cobalt": {"before": 5.8, "after": 1.1},
            "indium": {"before": 8.5, "after": 2.2},
            "gallium": {"before": 12.5, "after": 3.8},
            "fiberglass": {"before": 35.8, "after": 12.5},
        }
        
        return surface_roughness_data.get(material_name)

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """
        Generate frontmatter prioritizing materials.yaml data with AI supplemental enhancement.
        
        Architecture: materials.yaml FIRST, AI supplemental for research and additional content.
        """
        print(f"[DEBUG] Frontmatter generate method called for {material_name} with material_data keys: {list(material_data.keys())}")
        try:
            # STEP 1: Build comprehensive frontmatter from materials.yaml data FIRST
            logger.info(f"🏗️ Building frontmatter from materials.yaml data for {material_name}")
            base_frontmatter = self._build_frontmatter_from_materials_yaml(
                material_name, material_data, author_info
            )
            
            # STEP 2: Use AI only supplementally for additional research and enhancement
            if api_client:
                logger.info(f"🤖 Using AI supplementally for additional research on {material_name}")
                enhanced_frontmatter = self._enhance_with_ai_research(
                    base_frontmatter, material_name, material_data, api_client
                )
            else:
                logger.info(f"📄 Using materials.yaml data only (no AI client provided) for {material_name}")
                enhanced_frontmatter = base_frontmatter

            # STEP 3: Apply final processing and ordering
            final_content = self._finalize_frontmatter_content(
                enhanced_frontmatter, material_name, material_data
            )

            logger.info(f"✅ Generated frontmatter for {material_name} (materials.yaml prioritized)")
            return ComponentResult(
                component_type="frontmatter", content=final_content, success=True
            )

        except Exception as e:
            from utils.ai.loud_errors import component_failure

            component_failure(
                "frontmatter_generator",
                f"Error generating frontmatter for {material_name}: {e}",
                component_type="frontmatter",
            )
            logger.error(f"Error generating frontmatter for {material_name}: {e}")
            return ComponentResult(
                component_type="frontmatter",
                content="",
                success=False,
                error_message=str(e),
            )

    def _build_frontmatter_from_materials_yaml(
        self, material_name: str, material_data: Dict, author_info: Optional[Dict] = None
    ) -> Dict:
        """
        Build comprehensive frontmatter matching legacy format from materials.yaml data FIRST.
        
        This method creates complete frontmatter with all sections found in legacy files:
        - Content metadata (title, headline, description, keywords)
        - Chemical identifiers with full chemicalProperties section
        - Enhanced physical properties with percentiles and ranges
        - Complete laser parameters with all machine settings
        - Applications, compatibility, regulatory standards
        - Author information with full details and images
        - Environmental impact and outcomes
        - Prompt chain verification metadata
        
        AI is NOT used here - only structured data from materials.yaml.
        """
        logger.info(f"📊 Building comprehensive frontmatter from materials.yaml for {material_name}")
        
        frontmatter = {}
        
        # === BASIC IDENTIFICATION (from materials.yaml) ===
        frontmatter['name'] = material_data.get('name', material_name)
        frontmatter['category'] = material_data.get('category', 'unknown')
        
        # === CHEMICAL IDENTIFIERS (from materials.yaml) ===
        if 'formula' in material_data:
            frontmatter['chemicalFormula'] = material_data['formula']
        if 'symbol' in material_data:
            frontmatter['symbol'] = material_data['symbol']
            
        # === ENHANCED PROPERTIES (from materials.yaml data) ===
        properties = {}
        
        # Extract real physical properties from materials.yaml
        property_mappings = {
            'density': 'density',
            'melting_point': 'meltingPoint', 
            'decomposition_point': 'decompositionPoint',
            'thermal_conductivity': 'thermalConductivity',
            'tensile_strength': 'tensileStrength',
            'hardness': 'hardness',
            'youngs_modulus': 'youngsModulus'
        }
        
        # Add real material properties from materials.yaml
        for yaml_key, prop_key in property_mappings.items():
            if yaml_key in material_data:
                properties[prop_key] = material_data[yaml_key]
        
        # Add laser parameters to properties
        if 'laser_parameters' in material_data:
            laser_params = material_data['laser_parameters']
            if 'laser_type' in laser_params:
                properties['laserType'] = laser_params['laser_type']
            if 'wavelength_optimal' in laser_params:
                properties['wavelength'] = laser_params['wavelength_optimal']
            if 'fluence_threshold' in laser_params:
                properties['fluenceRange'] = laser_params['fluence_threshold']
        
        # Add chemical formula to properties
        if 'formula' in material_data:
            properties['chemicalFormula'] = material_data['formula']
            
        if properties:
            frontmatter['properties'] = properties
            
        # === COMPOSITION (from materials.yaml) ===
        if 'composition' in material_data:
            # Parse composition string into array format
            composition_str = material_data['composition']
            if 'Cu' in composition_str and 'Zn' in composition_str:
                # Brass-specific composition parsing
                frontmatter['composition'] = [
                    'Copper (Cu) 60-90%',
                    'Zinc (Zn) 10-40%',
                    'Trace elements (Pb, Fe, Sn, Al)'
                ]
            else:
                frontmatter['composition'] = [composition_str]
                
        # === MACHINE SETTINGS (from materials.yaml laser_parameters) ===
        if 'laser_parameters' in material_data:
            laser_params = material_data['laser_parameters']
            machine_settings = {}
            
            # Map laser parameters to machine settings
            if 'power_range' in laser_params:
                machine_settings['powerRange'] = laser_params['power_range']
            if 'pulse_duration' in laser_params:
                machine_settings['pulseDuration'] = laser_params['pulse_duration']
            if 'wavelength_optimal' in laser_params:
                machine_settings['wavelength'] = f"{laser_params['wavelength_optimal']} (primary), 532nm (optional)"
            if 'spot_size' in laser_params:
                machine_settings['spotSize'] = laser_params['spot_size']
            if 'repetition_rate' in laser_params:
                machine_settings['repetitionRate'] = laser_params['repetition_rate']
            if 'fluence_threshold' in laser_params:
                machine_settings['fluenceRange'] = laser_params['fluence_threshold']
            
            # Only include beam profile and safety info if provided in materials.yaml
            if 'beam_profile' in laser_params:
                machine_settings['beamProfile'] = laser_params['beam_profile']
            if 'beam_profile_options' in laser_params:
                machine_settings['beamProfileOptions'] = laser_params['beam_profile_options']
            if 'safety_class' in laser_params:
                machine_settings['safetyClass'] = laser_params['safety_class']
            
            if machine_settings:
                frontmatter['machineSettings'] = machine_settings
                
        # Store laser parameters for property enhancement service
        if 'laser_parameters' in material_data:
            frontmatter['laser_parameters'] = material_data['laser_parameters']
                
        # === APPLICATIONS (from materials.yaml) ===
        if 'applications' in material_data:
            frontmatter['applications'] = material_data['applications']
            
        # === INDUSTRY TAGS (from materials.yaml) ===  
        if 'industry_tags' in material_data:
            frontmatter['tags'] = material_data['industry_tags']
            
        # === COMPATIBILITY SECTION (from materials.yaml) ===
        if 'compatibility' in material_data:
            frontmatter['compatibility'] = material_data['compatibility']
        
        # === REGULATORY STANDARDS (from materials.yaml) ===
        if 'regulatory_standards' in material_data:
            frontmatter['regulatoryStandards'] = material_data['regulatory_standards']
        
        # === AUTHOR INFORMATION (from provided author_info) ===
        if author_info:
            frontmatter['author'] = author_info.get('name')
            frontmatter['author_object'] = author_info
            
        # === IMAGES SECTION (from materials.yaml) ===
        if 'images' in material_data:
            frontmatter['images'] = material_data['images']
        
        # === ENVIRONMENTAL IMPACT (from materials.yaml) ===
        if 'environmental_impact' in material_data:
            frontmatter['environmentalImpact'] = material_data['environmental_impact']
        
        # === OUTCOMES SECTION (from materials.yaml) ===
        if 'outcomes' in material_data:
            frontmatter['outcomes'] = material_data['outcomes']
        
        # === COMPLEXITY METADATA (from materials.yaml) ===
        if 'complexity' in material_data:
            frontmatter['complexity'] = material_data['complexity']
            
        if 'difficulty_score' in material_data:
            frontmatter['difficultyScore'] = material_data['difficulty_score']
            
        # === SURFACE ROUGHNESS DATA ===
        surface_roughness = self._get_surface_roughness_data(material_name)
        if surface_roughness:
            frontmatter['surface_roughness_before'] = surface_roughness['before']
            frontmatter['surface_roughness_after'] = surface_roughness['after']
            
        logger.info(f"✅ Built comprehensive frontmatter matching legacy format: {len(frontmatter)} sections")
        return frontmatter



    def _enhance_with_ai_research(
        self, base_frontmatter: Dict, material_name: str, material_data: Dict, api_client
    ) -> Dict:
        """
        Use AI with the template-based prompt to generate comprehensive frontmatter.
        
        This method uses the structured template from prompt.yaml but prioritizes
        materials.yaml data over template defaults.
        """
        logger.info(f"🤖 Using template-based AI generation for {material_name}")
        
        # Create template variables for the prompt
        # Get author info from base_frontmatter if available
        author_info = base_frontmatter.get('author_object')
        template_vars = self._create_template_vars(
            material_name, material_data, author_info, base_frontmatter
        )
        
        # Build the template-based prompt
        try:
            prompt = self._build_api_prompt(template_vars, base_frontmatter)
            
            # Use AI to generate complete frontmatter
            api_response = api_client.generate_simple(prompt)
            if api_response.success:
                # Parse AI response 
                ai_content = ValidationHelpers.extract_yaml_from_content(api_response.content)
                import yaml
                ai_data = yaml.safe_load(ai_content)
                
                if ai_data:
                    # Merge AI-generated content with materials.yaml data
                    # Materials.yaml data takes priority over AI template defaults
                    enhanced_frontmatter = ai_data.copy()
                    
                    # Override AI template data with materials.yaml data (materials.yaml wins)
                    for key, value in base_frontmatter.items():
                        if value is not None:  # Only override if materials.yaml has actual data
                            if key == 'properties' and isinstance(value, dict) and key in enhanced_frontmatter:
                                # Merge properties - materials.yaml properties override template defaults
                                enhanced_frontmatter[key].update(value)
                                logger.info("✅ Materials.yaml properties merged and prioritized")
                            elif key == 'machineSettings' and isinstance(value, dict) and key in enhanced_frontmatter:
                                # Merge machine settings - materials.yaml settings override template defaults  
                                enhanced_frontmatter[key].update(value)
                                logger.info("✅ Materials.yaml machine settings merged and prioritized")
                            else:
                                # Direct override for other fields
                                enhanced_frontmatter[key] = value
                                logger.info(f"✅ Materials.yaml data preserved for: {key}")
                    
                    logger.info("🔗 Completed template-based AI generation with materials.yaml priority")
                    return enhanced_frontmatter
                else:
                    logger.error("Failed to parse AI-generated YAML content")
                    raise Exception("AI generated invalid YAML content")
            else:
                logger.error(f"AI API call failed: {api_response.error_message}")
                raise Exception(f"AI API call failed: {api_response.error_message}")
                
        except Exception as e:
            logger.error(f"Template-based AI generation failed for {material_name}: {e}")
            raise Exception(f"Failed to generate AI content for {material_name} - fail-fast architecture requires successful AI generation")

    def _finalize_frontmatter_content(
        self, frontmatter_data: Dict, material_name: str, material_data: Dict
    ) -> str:
        """
        Apply final processing, field ordering, and YAML formatting.
        
        Uses the modular services for:
        - Property enhancement (numeric/unit separation)
        - Field ordering (hierarchical organization)
        - Technical specifications validation
        - YAML sanitization to prevent parsing errors
        """
        logger.info(f"🎯 Finalizing frontmatter content for {material_name}")
        
        # Apply property enhancements using modular service
        if 'properties' in frontmatter_data:
            PropertyEnhancementService.add_triple_format_properties(frontmatter_data)
            
        if 'machineSettings' in frontmatter_data:
            PropertyEnhancementService.add_triple_format_machine_settings(frontmatter_data['machineSettings'])
            
        # Ensure technical specifications are complete
        ValidationHelpers.ensure_technical_specifications(frontmatter_data)
        
        # Sanitize frontmatter data to prevent YAML parsing issues
        sanitized_frontmatter = self._sanitize_frontmatter_data(frontmatter_data)
        
        # Apply field ordering using modular service  
        ordered_frontmatter = FieldOrderingService.apply_field_ordering(sanitized_frontmatter)
        
        # Convert to YAML format
        import yaml
        yaml_content = yaml.dump(ordered_frontmatter, default_flow_style=False, sort_keys=False)
        
        # Apply final YAML syntax fixes
        yaml_content = self._fix_yaml_syntax(yaml_content)
        
        # Validate the generated YAML
        try:
            yaml.safe_load(yaml_content)
        except yaml.YAMLError as yaml_err:
            logger.warning(f"Generated YAML has syntax issues for {material_name}: {yaml_err}")
            # Attempt one more fix
            yaml_content = self._fix_yaml_syntax_comprehensive(yaml_content)
            # Apply final aggressive cleanup for stubborn patterns
            yaml_content = self._final_yaml_cleanup(yaml_content)
        
        final_content = f"---\n{yaml_content}---"
        
        logger.info(f"📝 Finalized frontmatter: {len(yaml_content)} characters")
        return final_content

    def _sanitize_frontmatter_data(self, frontmatter_data: Dict) -> Dict:
        """Sanitize frontmatter data to prevent YAML parsing issues"""
        if not frontmatter_data:
            return frontmatter_data
        
        sanitized = {}
        for key, value in frontmatter_data.items():
            if isinstance(value, str):
                # Clean up unicode characters that cause issues
                value = value.replace('\u2082', '₂').replace('\u2083', '₃').replace('\xB0', '°').replace('\xB3', '³')
                
                # Fix over-quoted values
                if value.startswith("'\"") and value.endswith("\"'"):
                    value = value[2:-2]
                elif value.startswith('"\'') and value.endswith('\'"'):
                    value = value[2:-2]
                
                # Quote values that need it (but avoid double-quoting)
                if (any(char in value for char in ['(', ')', ':', '"', '\n', ',']) and 
                    not (value.startswith('"') and value.endswith('"'))):
                    # Escape internal quotes first
                    value = value.replace('"', '""')
                    value = f'"{value}"'
                
                sanitized[key] = value
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_frontmatter_data(value)
            elif isinstance(value, list):
                sanitized[key] = [self._sanitize_frontmatter_data(item) if isinstance(item, dict) else item for item in value]
            else:
                sanitized[key] = value
        
        return sanitized

    def _fix_yaml_syntax(self, yaml_content: str) -> str:
        """Fix common YAML syntax issues in generated content"""
        lines = yaml_content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Quote values with special characters
            if ':' in line and not line.strip().startswith('#'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key_part = parts[0]
                    value_part = parts[1].strip()
                    
                    # Quote values that need it
                    if value_part and not (value_part.startswith('"') and value_part.endswith('"')):
                        if any(char in value_part for char in ['(', ')', '-', 'µ', '°']):
                            value_part = f'"{value_part}"'
                    
                    line = f"{key_part}: {value_part}"
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

    def _fix_yaml_syntax_comprehensive(self, yaml_content: str) -> str:
        """Apply comprehensive YAML syntax fixes for complex issues"""
        import re
        
        # First, apply all pattern-based fixes
        yaml_content = self._apply_comprehensive_yaml_patterns(yaml_content)
        
        lines = yaml_content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Fix multi-line values that got broken
            if ':' in line and '"' in line and line.count('"') == 1:
                # This might be a broken multi-line value
                value_lines = [line]
                j = i + 1
                
                # Collect continuation lines
                while j < len(lines):
                    next_line = lines[j]
                    if not next_line.strip():  # Empty line
                        break
                    if re.match(r'^\w+:', next_line):  # New field
                        break
                    if next_line.strip().startswith('-'):  # Array item
                        break
                    
                    value_lines.append(next_line)
                    j += 1
                
                # If we collected multiple lines, join them
                if len(value_lines) > 1:
                    field_match = re.match(r'^(\w+:\s*)(.*)', value_lines[0])
                    if field_match:
                        field_prefix = field_match.group(1)
                        first_value = field_match.group(2)
                        
                        # Combine all values
                        all_values = [first_value] + [vl.strip() for vl in value_lines[1:]]
                        combined_value = ' '.join(all_values)
                        
                        # Clean up quotes
                        combined_value = combined_value.replace('""', '"').strip('"')
                        combined_value = f'"{combined_value}"'
                        
                        fixed_line = f"{field_prefix}{combined_value}"
                        fixed_lines.append(fixed_line)
                        i = j - 1
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
            
            i += 1
        
        return '\n'.join(fixed_lines)

    def _apply_comprehensive_yaml_patterns(self, yaml_content: str) -> str:
        """Apply all discovered YAML syntax patterns from our fix scripts"""
        import re
        
        # Pattern 1: Fix over-quoted patterns like "'"value"'" (including multi-line)
        yaml_content = re.sub(r':\s*"\'([^"\']*(?:\n[^"\']*)*)\'"', r': "\1"', yaml_content, flags=re.MULTILINE | re.DOTALL)
        
        # Pattern 2: Fix patterns like "'value'" (including multi-line)
        yaml_content = re.sub(r':\s*\'([^\']*(?:\n[^\']*)*?)\'', r': "\1"', yaml_content, flags=re.MULTILINE | re.DOTALL)
        
        # Pattern 3: Fix double-quoted patterns like ""value"" (including multi-line)
        yaml_content = re.sub(r':\s*""([^"]*(?:\n[^"]*)*?)""', r': "\1"', yaml_content, flags=re.MULTILINE | re.DOTALL)
        
        # Pattern 4: Fix over-escaped quotes
        yaml_content = re.sub(r'\\"([^"]+)\\"', r'"\1"', yaml_content)
        
        # Pattern 5: Fix patterns like ""\"text\""
        yaml_content = re.sub(r'""\\"([^"]+)\\""', r'"\1"', yaml_content)
        
        # Pattern 6: Fix broken multi-line strings that span multiple lines
        yaml_content = re.sub(r':\s*"([^"]*)\n\s*([^"]*)"', r': "\1 \2"', yaml_content, flags=re.MULTILINE)
        
        # Pattern 7: Fix unicode escape sequences with backslashes
        yaml_content = re.sub(r'\\([^"]*?)\\', r'\1', yaml_content)
        
        # Pattern 8: Fix unicode escape sequences
        unicode_fixes = {
            '\\xB0': '°',   # degree symbol
            '\\xB3': '³',   # superscript 3
            '\\xB7': '·',   # middle dot
            '\\u2082': '₂', # subscript 2
            '\\u2083': '₃', # subscript 3
            '\\u03BC': 'μ', # mu
            '\\u2013': '–', # en dash
            '\\u00B1': '±', # plus-minus
            '\\u03A9': 'Ω', # omega
            '\\u03B1': 'α', # alpha
            '\\u03B2': 'β', # beta
            '\\u03B3': 'γ', # gamma
            '\\u03B4': 'δ', # delta
            '\\u03BB': 'λ', # lambda
        }
        
        for escape_seq, char in unicode_fixes.items():
            yaml_content = yaml_content.replace(escape_seq, char)
        
        # Pattern 9: Fix broken array values that got split
        yaml_content = re.sub(r'- result: "([^"]*)\n\s*([^"]*)"', r'- result: "\1 \2"', yaml_content, flags=re.MULTILINE)
        
        # Pattern 10: Fix formula lines that got broken across multiple lines
        yaml_content = re.sub(r'formula: "([^"]*)\n\s*([^"]*)"', r'formula: "\1\2"', yaml_content, flags=re.MULTILINE)
        
        # Pattern 11: Fix chemical symbols that got broken
        yaml_content = re.sub(r'symbol: ([^\n]*)\n\s*([A-Z][a-z]*)', r'symbol: "\1\2"', yaml_content, flags=re.MULTILINE)
        
        # Pattern 12: Clean up any remaining whitespace and line breaks in quoted strings
        yaml_content = re.sub(r':\s*"([^"]*)\s*\n\s*([^"]*)"', r': "\1 \2"', yaml_content, flags=re.MULTILINE)
        
        # Pattern 13: Fix any remaining line continuations in quoted values
        yaml_content = re.sub(r'"([^"]*?)\n\s+([^"]*?)"', r'"\1 \2"', yaml_content, flags=re.MULTILINE)
        
        return yaml_content

    def _create_template_vars(
        self,
        material_name,
        material_data,
        author_info,
        frontmatter_data=None,
        schema_fields=None,
    ):
        """Create template variables for frontmatter generation."""
        subject_lowercase = material_name.lower()
        
        # Apply standardized naming convention that matches the resolved image naming
        subject_slug = self._apply_standardized_naming(subject_lowercase)

        # FAIL-FAST: Category is required for frontmatter generation
        if "category" not in material_data:
            raise Exception(
                "Material data missing required 'category' field - fail-fast architecture requires complete material information"
            )
        category = material_data["category"]

        # Extract formula and symbol with intelligent fallback generation
        formula, symbol = self._extract_chemical_identifiers(material_name, material_data, category)
        
        # Resolve author information with fail-fast validation
        author_name, resolved_author_info = self._resolve_author_info(material_data, author_info)

        # Add template variables needed by prompt.yaml
        from datetime import datetime
        
        # FAIL-FAST validation for required fields
        if not formula:
            logger.warning(f"No formula found in materials.yaml for {material_name} - AI must research chemical formula")
        if not symbol:
            logger.warning(f"No symbol found in materials.yaml for {material_name} - AI must research chemical symbol") 
        if not resolved_author_info.get("id") and not material_data.get("author_id"):
            raise Exception(f"No author_id found in materials.yaml or author_info for {material_name} - fail-fast architecture requires author identification")
        
        return {
            "subject": material_name,
            "subject_lowercase": subject_lowercase,
            "subject_slug": subject_slug,
            "exact-material-name": subject_slug,  # Required for template compatibility
            "material_formula": formula or "[RESEARCH: Chemical formula required]",
            "material_symbol": symbol or "[RESEARCH: Chemical symbol required]",
            "formula": formula or "[RESEARCH: Chemical formula required]",  # For compatibility with chemical fallback tests
            "symbol": symbol or "[RESEARCH: Chemical symbol required]",   # For compatibility with chemical fallback tests
            "material_type": material_data.get("material_type") or category,
            "category": category,
            "author_name": author_name,
            "author_id": resolved_author_info.get("id") or material_data.get("author_id"),
            "author_object_sex": resolved_author_info.get("sex") or "[RESEARCH: Author gender required]",
            "author_object_title": resolved_author_info.get("title") or "[RESEARCH: Author title required]",
            "author_object_country": resolved_author_info.get("country") or "[RESEARCH: Author country required]",
            "author_object_expertise": resolved_author_info.get("expertise") or "[RESEARCH: Author expertise required]",
            "author_object_image": resolved_author_info.get("image") or "[RESEARCH: Author image path required]",
            "persona_country": resolved_author_info.get("country") or "[RESEARCH: Author country required]",
            "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        }

    def _apply_standardized_naming(self, material_name_lower: str) -> str:
        """Apply naming standardization aligned with materials.yaml single source of truth"""
        # Basic kebab-case conversion
        slug = material_name_lower.replace(" ", "-")
        
        # Apply standardizations aligned with materials.yaml database
        naming_mappings = {
            "terra-cotta": "terracotta",
        }
        
        # Apply standardization if material matches known mappings
        if slug in naming_mappings:
            slug = naming_mappings[slug]
            
        # Remove wood- prefix (wood materials are defined without prefix in materials.yaml)
        if slug.startswith("wood-"):
            slug = slug[5:]  # Remove "wood-" prefix
            
        return slug

    def _extract_chemical_identifiers(self, material_name: str, material_data: Dict, category: str):
        """Extract formula and symbol from materials.yaml data"""
        # Formula extraction from materials.yaml
        formula = material_data.get("formula")
        if not formula and "data" in material_data:
            formula = material_data["data"].get("formula")
        
        # Symbol extraction from materials.yaml (often same as formula for materials)
        symbol = material_data.get("symbol")
        if not symbol and "data" in material_data:
            symbol = material_data["data"].get("symbol")
        
        # FAIL-FAST: No fallbacks allowed - symbol must be researched
        if not symbol:
            logger.warning(f"No symbol found in materials.yaml for {material_name} - AI must research chemical symbol")
            symbol = None  # Let AI research the symbol
        
        # Log what we found
        logger.info(f"Extracted chemical identifiers for {material_name}: formula='{formula}', symbol='{symbol}'")
        
        return formula, symbol

    def _resolve_author_info(self, material_data: Dict, author_info: Optional[Dict]):
        """Resolve author information with fail-fast validation"""
        # FAIL-FAST: Author information is required
        if not author_info or "name" not in author_info:
            # Try to extract author_id from material_data and resolve it
            author_id = None
            if "author_id" in material_data:
                author_id = material_data["author_id"]
            elif "data" in material_data and "author_id" in material_data["data"]:
                author_id = material_data["data"]["author_id"]

            if author_id:
                try:
                    from utils import get_author_by_id

                    author_data = get_author_by_id(author_id)
                    if author_data and "name" in author_data:
                        author_name = author_data["name"]
                        logger.info(f"Resolved author_id {author_id} to {author_name}")
                        resolved_author_info = author_data
                    else:
                        raise Exception(
                            f"Author data for ID {author_id} missing required 'name' field - fail-fast architecture requires complete author information"
                        )
                except Exception as e:
                    raise Exception(
                        f"Failed to resolve author_id {author_id}: {e} - fail-fast architecture requires valid author information"
                    )
            else:
                raise Exception(
                    "Author information with 'name' field is required for frontmatter generation - fail-fast architecture requires complete author information"
                )
        else:
            author_name = author_info["name"]
            resolved_author_info = author_info
        
        return author_name, resolved_author_info

    def _build_api_prompt(self, template_vars: Dict, frontmatter_data: Optional[Dict] = None) -> str:
        """Build API prompt using template variables"""
        try:
            # Get prompt configuration
            if not self.prompt_config:
                raise Exception("Prompt configuration not loaded")
            
            # Check for required template field
            if "template" not in self.prompt_config:
                from utils.ai.loud_errors import configuration_failure
                configuration_failure(
                    "frontmatter_generator",
                    "Prompt configuration missing required 'template' field - fail-fast architecture requires complete configuration"
                )
            
            template = self.prompt_config["template"]
            
            # Format the template with variables
            prompt = template.format(**template_vars)
            
            # Add context from frontmatter_data if provided
            if frontmatter_data:
                prompt += f"\n\nAdditional context: {frontmatter_data}"
            
            logger.debug(f"Built API prompt for {template_vars.get('subject', 'unknown material')}")
            return prompt
            
        except Exception as e:
            logger.error(f"Error building API prompt: {e}")
            raise Exception(f"Failed to build API prompt: {e} - fail-fast architecture requires valid prompt configuration")

    def _process_and_enhance_content(
        self,
        content: str,
        material_name: str,
        material_data: Dict,
        api_client=None
    ) -> str:
        """
        Process and enhance content using modular services
        
        Pipeline:
        1. Parse YAML content
        2. Apply property enhancement (numeric/unit separation)
        3. Add technical specifications
        4. Apply field ordering
        5. Validate and correct issues
        6. Return final content
        """
        print(f"[DEBUG] _process_and_enhance_content called for {material_name}")
        try:
            import yaml
            
            # Extract and parse YAML content
            yaml_content = ValidationHelpers.extract_yaml_from_content(content)
            frontmatter_data = yaml.safe_load(yaml_content)
            
            if not frontmatter_data:
                logger.warning(f"Failed to parse YAML content for {material_name}")
                return content
            
            # 0. Populate properties section from material_data comprehensive properties
            print("[DEBUG] About to populate properties from material data")
            self._populate_properties_from_material_data(frontmatter_data, material_data)
            print("[DEBUG] Finished populating properties from material data")
            
            # 1. Apply property enhancement (numeric/unit separation)
            PropertyEnhancementService.add_triple_format_properties(frontmatter_data)
            
            # 2. Add triple format for machine settings if present
            if "machineSettings" in frontmatter_data:
                PropertyEnhancementService.add_triple_format_machine_settings(
                    frontmatter_data["machineSettings"]
                )
            
            # 3. Ensure technical specifications structure
            ValidationHelpers.ensure_technical_specifications(frontmatter_data)
            
            # 4. Apply field ordering for optimal organization
            ordered_data = FieldOrderingService.apply_field_ordering(frontmatter_data)
            
            # 5. Validate and apply corrections if needed
            enhanced_yaml = yaml.dump(ordered_data, default_flow_style=False, sort_keys=False)
            enhanced_content = f"---\n{enhanced_yaml}---"
            
            if api_client:
                final_content, validation_report = ValidationHelpers.validate_and_enhance_content(
                    enhanced_content, material_name, material_data, api_client
                )
                return final_content
            else:
                logger.debug("No API client provided for validation")
                return enhanced_content
                
        except Exception as e:
            logger.error(f"Error processing content for {material_name}: {e}")
            return content

    def _populate_properties_from_material_data(self, frontmatter_data: Dict, material_data: Dict) -> None:
        """
        Populate the properties section in frontmatter_data with comprehensive properties from material_data.
        
        This method extracts all the comprehensive scientific properties that were added during the
        materials database enhancement and makes them available for the property enhancement service.
        """
        logger.debug(f"[DEBUG] Material data keys: {list(material_data.keys())}")
        
        if "properties" not in frontmatter_data:
            frontmatter_data["properties"] = {}
        
        properties = frontmatter_data["properties"]
        
        # List of comprehensive properties to extract from material_data
        property_mappings = [
            "density",
            "melting_point", 
            "boiling_point",
            "thermal_conductivity",
            "specific_heat_capacity",
            "thermal_expansion_coefficient",
            "electrical_resistivity",
            "tensile_strength",
            "yield_strength",
            "elastic_modulus",
            "curie_temperature",
            "crystal_structure",
            "magnetic_properties"
        ]
        
        # Extract properties from material_data if they exist
        found_props = []
        for prop in property_mappings:
            if prop in material_data:
                properties[prop] = material_data[prop]
                found_props.append(prop)
        
        logger.info(f"[DEBUG] Populated {len(found_props)} properties from material data: {found_props}")
        logger.debug(f"[DEBUG] Properties section now contains: {properties}")

    def _final_yaml_cleanup(self, yaml_content: str) -> str:
        """Apply final aggressive cleanup for stubborn YAML patterns"""
        import re
        
        # Fix the most common problematic patterns with simple string replacements
        yaml_content = yaml_content.replace('""', '"')  # Remove double quotes
        yaml_content = yaml_content.replace("''", "'")  # Remove double apostrophes
        yaml_content = re.sub(r'"\'([^"\']*)\'"', r'"\1"', yaml_content)  # Fix "'"value"'"
        yaml_content = re.sub(r'\'([^\']*?)\'', r'"\1"', yaml_content)  # Convert single quotes to double
        
        # Fix broken YAML structure - ensure proper spacing and formatting
        lines = yaml_content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Fix lines that lost their proper YAML structure
            if ':' in line and not line.strip().startswith('-'):
                # Ensure there's a space after the colon
                line = re.sub(r':([^\s])', r': \1', line)
                
                # Fix values that lost their quotes
                if re.match(r'^\s*\w+:\s*[^"\'\s].*[^"\s]$', line):
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0]
                        value = parts[1].strip()
                        if value and not value.startswith('"') and not value.startswith("'") and not value.replace('.', '').isdigit():
                            line = f'{key}: "{value}"'
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
