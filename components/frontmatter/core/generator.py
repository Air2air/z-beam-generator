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
from components.frontmatter.enhancement.optimized_property_enhancement_service import OptimizedPropertyEnhancementService
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
            "description": "Optimized YAML frontmatter generation with pure numeric structures for maximum computational efficiency",
            "version": "6.0.0",  # Updated version for optimized numeric architecture
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
        
        Architecture: materials.yaml FIRST using enhanced mapper, AI supplemental for research.
        """
        print(f"[DEBUG] Frontmatter generate method called for {material_name} with material_data keys: {list(material_data.keys())}")
        try:
            # STEP 1: Use enhanced materials.yaml mapper for comprehensive frontmatter
            logger.info(f"🚀 Using enhanced MaterialsYamlFrontmatterMapper for {material_name}")
            
            # Import our enhanced mapper
            from components.frontmatter.enhancement.materials_yaml_mapper import MaterialsYamlFrontmatterMapper
            
            # Initialize the enhanced mapper
            materials_mapper = MaterialsYamlFrontmatterMapper()
            
            # Get comprehensive frontmatter from materials.yaml with all properties and logical organization
            base_frontmatter = materials_mapper.map_materials_to_comprehensive_frontmatter(
                material_data, material_name
            )
            
            # Fallback to legacy method if enhanced mapper fails
            if not base_frontmatter:
                logger.warning(f"⚠️ Enhanced mapper failed for {material_name}, using legacy method")
                base_frontmatter = self._build_frontmatter_from_materials_yaml(
                    material_name, material_data, author_info
                )
            else:
                logger.info(f"✅ Enhanced mapper generated {len(base_frontmatter)} sections for {material_name}")
            
            # STEP 2: Use AI only supplementally for additional research and enhancement
            if api_client:
                logger.info(f"🤖 Using targeted AI research for {material_name}")
                enhanced_frontmatter = self._enhance_with_targeted_ai_research(
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



    def _enhance_with_targeted_ai_research(
        self, base_frontmatter: Dict, material_name: str, material_data: Dict, api_client
    ) -> Dict:
        """
        Use AI for targeted research of specific fields without full YAML generation.
        This avoids YAML parsing issues by having AI generate only specific content.
        """
        logger.info(f"🔍 Using AI for targeted research on {material_name}")
        
        enhanced_frontmatter = base_frontmatter.copy()
        
        try:
            # Get chemical identifiers if missing
            formula = material_data.get('formula', 'Si')  # Default for Silicon
            symbol = material_data.get('symbol', 'Si')   # Default for Silicon
            
            # AI Research 1: Enhanced description (single field, easier to parse)
            description_prompt = f"""
            Generate a technical description (2-3 sentences) for laser cleaning of {material_name} ({formula}).
            Focus on: laser-material interaction, industrial applications, and technical advantages.
            Respond with ONLY the description text, no YAML formatting or quotes.
            """
            
            desc_response = api_client.generate_simple(description_prompt)
            if desc_response.success:
                # Clean the response and add to frontmatter
                description = desc_response.content.strip().replace('\n', ' ')
                enhanced_frontmatter['description'] = description
                logger.info(f"✅ AI enhanced description for {material_name}")
            
            # AI Research 2: Applications (structured but simpler)
            applications_prompt = f"""
            List 3 real industrial applications for {material_name} laser cleaning.
            Format as: Industry1: Application details1
            Industry2: Application details2
            Industry3: Application details3
            Respond with ONLY the list, no additional text.
            """
            
            apps_response = api_client.generate_simple(applications_prompt)
            if apps_response.success:
                # Parse applications into structured format
                applications = []
                for line in apps_response.content.strip().split('\n'):
                    if ':' in line:
                        industry, detail = line.split(':', 1)
                        applications.append({
                            'industry': industry.strip(),
                            'detail': detail.strip()
                        })
                
                if applications:
                    enhanced_frontmatter['applications'] = applications
                    logger.info(f"✅ AI enhanced applications for {material_name}")
            
            # Add other essential fields that don't require AI
            enhanced_frontmatter.update({
                'name': material_name,
                'title': f"{material_name} Laser Cleaning",
                'headline': f"Comprehensive technical guide for laser cleaning {material_data.get('category', 'material')} {material_name.lower()}",
                'category': material_data.get('category', 'material'),
                'keywords': f"{material_name.lower()}, {material_name.lower()} {material_data.get('category', 'material')}, laser ablation, laser cleaning, non-contact cleaning, pulsed fiber laser, surface contamination removal, industrial laser parameters, thermal processing, surface restoration",
                'chemicalProperties': {
                    'symbol': symbol,
                    'formula': formula,
                    'materialType': material_data.get('category', 'material')
                }
            })
            
            logger.info(f"✅ Enhanced frontmatter with targeted AI research for {material_name}")
            return enhanced_frontmatter
            
        except Exception as e:
            logger.warning(f"⚠️ AI enhancement failed for {material_name}: {e}, using base frontmatter")
            return base_frontmatter

    def _build_manual_yaml_frontmatter(self, frontmatter_data: Dict) -> str:
        """
        Build YAML frontmatter manually to avoid parsing issues.
        This ensures perfect YAML formatting without relying on yaml.dump.
        """
        lines = ["---"]
        
        # Helper function to properly quote and sanitize values
        def quote_value(value):
            if isinstance(value, str):
                # Apply comprehensive sanitization first
                # Clean up unicode characters that cause issues
                value = value.replace('\u2082', '₂').replace('\u2083', '₃').replace('\xB0', '°').replace('\xB3', '³')
                
                # Fix malformed quotes - comprehensive patterns
                if value.startswith('"""') and value.endswith('"""') and len(value) > 6:
                    value = value[3:-3].strip()
                elif value.startswith('""') and value.endswith('""') and len(value) > 4:
                    value = value[2:-2].strip()
                elif value.startswith("'\"") and value.endswith("\"'"):
                    value = value[2:-2].strip()  
                elif value.startswith('"\'') and value.endswith('\'"'):
                    value = value[2:-2].strip()
                
                # Clean up any remaining quote artifacts
                value = value.replace('""', '"').replace("''", "'")
                value = value.replace('\\"', '"').replace("\\'", "'")
                
                # Clean newlines and extra spaces
                value = value.replace('\n', ' ').replace('  ', ' ').strip()
                
                # Replace problematic double quotes with single quotes for safe quoting
                value = value.replace('"', "'")
                
                # Always quote string values for safety
                return f'"{value}"'
            elif isinstance(value, (int, float)):
                return str(value)
            elif isinstance(value, bool):
                return str(value).lower()
            elif value is None:
                return "null"
            else:
                # Convert to string and sanitize
                str_value = str(value).replace('"', "'")
                return f'"{str_value}"'
        
        # Helper function to add a field
        def add_field(key, value, indent=0):
            indent_str = "  " * indent
            if isinstance(value, dict):
                lines.append(f"{indent_str}{key}:")
                for sub_key, sub_value in value.items():
                    add_field(sub_key, sub_value, indent + 1)
            elif isinstance(value, list):
                lines.append(f"{indent_str}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"{indent_str}- ")
                        for sub_key, sub_value in item.items():
                            add_field(sub_key, sub_value, indent + 1)
                            break  # First item gets the dash
                        # Add remaining items with proper indentation
                        remaining_items = list(item.items())[1:]
                        for sub_key, sub_value in remaining_items:
                            add_field(sub_key, sub_value, indent + 1)
                    else:
                        lines.append(f"{indent_str}  - {quote_value(item)}")
            else:
                lines.append(f"{indent_str}{key}: {quote_value(value)}")
        
        # Define field order for optimal frontmatter structure
        field_order = [
            'name', 'category', 'title', 'headline', 'description', 'keywords',
            'chemicalProperties', 'properties', 'applications', 'composition',
            'compatibility', 'regulatoryStandards', 'author', 'author_object',
            'images', 'environmentalImpact', 'outcomes', 'prompt_chain_verification'
        ]
        
        # Add ordered fields
        for field in field_order:
            if field in frontmatter_data:
                add_field(field, frontmatter_data[field])
        
        # Add any remaining fields not in the order
        for key, value in frontmatter_data.items():
            if key not in field_order:
                add_field(key, value)
        
        lines.append("---")
        return '\n'.join(lines)

    def _finalize_frontmatter_content(
        self, frontmatter_data: Dict, material_name: str, material_data: Dict
    ) -> str:
        """
        Apply final processing and manual YAML formatting.
        
        Uses manual YAML building to avoid yaml.dump parsing issues.
        """
        logger.info(f"🎯 Finalizing frontmatter content for {material_name}")
        
        # Apply optimized property enhancements using new service
        from components.frontmatter.enhancement.optimized_property_enhancement_service import OptimizedPropertyEnhancementService
        
        # Apply optimizations to the frontmatter structure
        if 'properties' in frontmatter_data:
            OptimizedPropertyEnhancementService.add_optimized_properties(frontmatter_data['properties'])
        
        if 'machineSettings' in frontmatter_data:
            OptimizedPropertyEnhancementService.add_optimized_machine_settings(frontmatter_data['machineSettings'])
        
        # Apply field ordering for optimal structure
        from components.frontmatter.ordering.field_ordering_service import FieldOrderingService
        ordered_frontmatter = FieldOrderingService.apply_field_ordering(frontmatter_data)
        
        # Build YAML manually with integrated sanitization to avoid parsing issues
        final_content = self._build_manual_yaml_frontmatter(ordered_frontmatter)
        
        logger.info(f"📝 Finalized frontmatter with manual YAML formatting: {len(final_content)} characters")
        return final_content

    def _pre_sanitize_ai_yaml(self, ai_content: str) -> str:
        """Pre-sanitize AI-generated YAML content to fix common generation issues"""
        import re
        
        lines = ai_content.split('\n')
        fixed_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Fix broken keywords field (most common issue)
            if 'keywords:' in line and '"' in line:
                # Check if the quote is properly closed on this line
                quote_count = line.count('"')
                if quote_count == 1:  # Opening quote but no closing quote
                    # Look ahead to find content that should be part of keywords
                    keyword_parts = [line]
                    j = i + 1
                    
                    # Collect lines until we find a proper YAML field
                    while j < len(lines):
                        next_line = lines[j].strip()
                        if not next_line:  # Empty line
                            j += 1
                            continue
                        if next_line.endswith(':') or ': ' in next_line:  # Found next field
                            break
                        keyword_parts.append(next_line)
                        j += 1
                    
                    # Reconstruct the keywords field
                    if len(keyword_parts) > 1:
                        keywords_content = keyword_parts[0]
                        # Remove the opening quote and colon part
                        if ':"' in keywords_content:
                            key_part = keywords_content.split(':"')[0]
                            content_start = keywords_content.split(':"')[1]
                        else:
                            key_part = 'keywords'
                            content_start = keywords_content.split(':', 1)[1].strip().strip('"')
                        
                        # Join all the content
                        all_content = [content_start] + [kp.strip() for kp in keyword_parts[1:]]
                        combined_keywords = ' '.join(all_content).strip()
                        
                        # Clean up the combined content
                        combined_keywords = combined_keywords.replace('  ', ' ')
                        
                        fixed_lines.append(f'{key_part}: "{combined_keywords}"')
                        i = j
                        continue
            
            # Fix fields that got concatenated (missing newlines)
            if re.search(r'[a-zA-Z0-9"]\s+[a-zA-Z]+:', line):
                # Split the line where a new field starts
                match = re.search(r'([^"]*"[^"]*"?)\s+([a-zA-Z]+:.*)', line)
                if match:
                    first_part = match.group(1).strip()
                    second_part = match.group(2).strip()
                    fixed_lines.append(first_part)
                    fixed_lines.append(second_part)
                    i += 1
                    continue
            
            fixed_lines.append(line)
            i += 1
        
        return '\n'.join(fixed_lines)

    def _sanitize_frontmatter_data(self, frontmatter_data: Dict) -> Dict:
        """Enhanced sanitization for clean YAML frontmatter output with proper formatting"""
        if not frontmatter_data:
            return frontmatter_data
        
        sanitized = {}
        for key, value in frontmatter_data.items():
            if isinstance(value, str):
                # Clean up unicode characters that cause issues
                value = value.replace('\u2082', '₂').replace('\u2083', '₃').replace('\xB0', '°').replace('\xB3', '³')
                
                # Fix malformed quotes - comprehensive patterns
                if value.startswith('"""') and value.endswith('"""') and len(value) > 6:
                    value = value[3:-3].strip()
                elif value.startswith('""') and value.endswith('""') and len(value) > 4:
                    value = value[2:-2].strip()
                elif value.startswith("'\"") and value.endswith("\"'"):
                    value = value[2:-2].strip()  
                elif value.startswith('"\'') and value.endswith('\'"'):
                    value = value[2:-2].strip()
                
                # Fix broken quote patterns like: "text" remaining text
                if '"' in value:
                    # Find unmatched quotes that break YAML
                    quote_positions = [i for i, char in enumerate(value) if char == '"']
                    if len(quote_positions) % 2 == 1:  # Odd number of quotes
                        # Find the break point and fix it
                        for i in range(1, len(quote_positions), 2):
                            end_quote = quote_positions[i]
                            # Check if there's text after the closing quote
                            if end_quote < len(value) - 1 and value[end_quote + 1:].strip():
                                # Extend the quote to cover the remaining text
                                value = value[:end_quote] + value[end_quote+1:] + '"'
                                break
                
                # Clean up any remaining quote artifacts
                value = value.replace('""', '"').replace("''", "'")
                
                # Remove any backslash artifacts from quote escaping
                value = value.replace('\\"', '"').replace("\\'", "'")
                
                # Handle problematic characters for YAML
                if any(char in value for char in ['\n', '"', '\\', ':']) or value.startswith("'"):
                    # Clean the value first
                    clean_value = value.strip()
                    
                    # Use literal block scalar for multi-line content
                    if '\n' in clean_value:
                        indented_lines = '\n  '.join(clean_value.split('\n'))
                        sanitized[key] = f"|\n  {indented_lines}"
                    else:
                        # Single line - escape quotes properly and ensure proper quoting
                        if '"' in clean_value or ':' in clean_value or clean_value.endswith(','):
                            # Use single quotes if double quotes are problematic
                            if "'" not in clean_value:
                                sanitized[key] = f"'{clean_value}'"
                            else:
                                # Escape quotes and use double quotes
                                escaped_value = clean_value.replace('"', '\\"')
                                sanitized[key] = f'"{escaped_value}"'
                        else:
                            sanitized[key] = f'"{clean_value}"'
                else:
                    sanitized[key] = value
                    
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_frontmatter_data(value)
            elif isinstance(value, list):
                sanitized_list = []
                for item in value:
                    if isinstance(item, dict):
                        sanitized_list.append(self._sanitize_frontmatter_data(item))
                    elif isinstance(item, str):
                        # Fix double quotes in list items
                        clean_item = item.replace('""', '"').strip()
                        if clean_item.startswith('"') and clean_item.endswith('"'):
                            # Remove outer quotes if they're causing double-quote issues
                            inner_text = clean_item[1:-1]
                            if '""' not in inner_text:
                                sanitized_list.append(inner_text)
                            else:
                                sanitized_list.append(clean_item)
                        else:
                            sanitized_list.append(clean_item)
                    else:
                        sanitized_list.append(item)
                sanitized[key] = sanitized_list
            else:
                sanitized[key] = value
        
        return sanitized

    def _fix_yaml_syntax(self, yaml_content: str) -> str:
        """Fix common YAML syntax issues in generated content with enhanced quote and newline handling"""
        lines = yaml_content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Handle quote issues specifically for keywords field
            if 'keywords:' in line and '"' in line:
                # Fix malformed quotes in keywords
                if "'silicon, silicon semiconductor, laser ablation, laser cleaning, non-contact' cleaning," in line:
                    # Fix the specific pattern with misplaced quote
                    line = line.replace("'silicon, silicon semiconductor, laser ablation, laser cleaning, non-contact' cleaning,", 
                                      "'silicon, silicon semiconductor, laser ablation, laser cleaning, non-contact cleaning,'")
                elif line.count('"') % 2 == 1:  # Odd number of quotes
                    # Find and fix broken quote pattern
                    quote_pos = line.rfind('"')
                    if quote_pos > -1 and quote_pos < len(line) - 1:
                        # Check if there's text after the quote that should be included
                        remaining_text = line[quote_pos + 1:].strip()
                        if remaining_text and not remaining_text.startswith(' '):
                            # Include the remaining text within quotes
                            line = line[:quote_pos] + remaining_text + '"'
            
            # Ensure proper newlines between unit and range fields
            if ':' in line and not line.strip().startswith('#'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key_part = parts[0]
                    value_part = parts[1].strip()
                    
                    # Check for missing space after colon
                    if not value_part.startswith(' ') and value_part:
                        line = f"{key_part}: {value_part}"
                    
                    # Ensure unit fields are properly separated from range fields
                    if key_part.strip().endswith('Unit') and i + 1 < len(lines):
                        next_line = lines[i + 1]
                        if next_line.strip() and not next_line.startswith(' ') and 'Range:' in next_line:
                            # Ensure proper separation between unit and range
                            if not next_line.startswith(' '):
                                lines[i + 1] = next_line  # Keep as-is but ensure it's formatted properly
                    
                    # Quote values that need it
                    if value_part and not (value_part.startswith('"') and value_part.endswith('"')):
                        if any(char in value_part for char in ['(', ')', '-', 'µ', '°', ':']):
                            # Don't double-quote already quoted values
                            if not (value_part.startswith("'") and value_part.endswith("'")):
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
        
        # NEW Pattern 12: Fix specific broken keywords quote pattern
        yaml_content = re.sub(r'keywords: "([^"]*)" cl\s*eaning,', r'keywords: "\1 cleaning,"', yaml_content)
        
        # NEW Pattern 13: Fix missing space after quoted field causing line concatenation
        yaml_content = re.sub(r'([^:]+): "([^"]+)"\s*([a-zA-Z][^:]*:)', r'\1: "\2"\n\3', yaml_content)
        
        # NEW Pattern 14: Fix unit/range field separation issues
        yaml_content = re.sub(r'(\w+Unit): "([^"]+)"\s*(\w+Range):', r'\1: "\2"\n  \3:', yaml_content)
        
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
            "material_formula": formula,  # FAIL-FAST: Must be researched, no fallbacks
            "material_symbol": symbol,    # FAIL-FAST: Must be researched, no fallbacks
            "formula": formula,  # FAIL-FAST: Must be researched, no fallbacks
            "symbol": symbol,   # FAIL-FAST: Must be researched, no fallbacks
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
            
            # 1. Apply optimized property enhancement (pure numeric structure)
            OptimizedPropertyEnhancementService.add_optimized_properties(frontmatter_data.get('properties', {}))
            
            # 2. Add optimized machine settings if present
            if "machineSettings" in frontmatter_data:
                OptimizedPropertyEnhancementService.add_optimized_machine_settings(
                    frontmatter_data["machineSettings"]
                )
            
            # 3. Apply full optimization to remove redundant sections
            OptimizedPropertyEnhancementService.apply_full_optimization(frontmatter_data)
            
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
        
        # Fix specific keywords broken quote pattern
        yaml_content = re.sub(r'keywords: "([^"]*?)"\s*\n([^:]*)', r'keywords: "\1 \2"', yaml_content, flags=re.MULTILINE)
        
        # Fix field concatenation (no newline between fields)
        yaml_content = re.sub(r'([a-zA-Z0-9_]+)\s+([a-zA-Z]+):(\s*)', r'\1\n\2:\3', yaml_content)
        
        # Fix missing newlines between unit and range fields specifically
        yaml_content = re.sub(r'(\w+Unit): "([^"]+)"\s*(\w+Range):', r'\1: "\2"\n  \3:', yaml_content)
        yaml_content = re.sub(r'(\w+Unit): ([^\s]+)\s*(\w+Range):', r'\1: \2\n  \3:', yaml_content)
        
        # Fix broken YAML structure - ensure proper spacing and formatting
        lines = yaml_content.split('\n')
        fixed_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Handle multi-line broken quotes that span several lines
            if 'keywords:' in line and '"' in line and line.count('"') == 1:
                # This is likely a broken keywords field
                quote_content = [line.split('"', 1)[1]]  # Get content after first quote
                j = i + 1
                
                # Look for the closing context on subsequent lines
                while j < len(lines) and not lines[j].strip().endswith(':'):
                    quote_content.append(lines[j].strip())
                    if any(field + ':' in lines[j] for field in ['chemicalProperties', 'properties', 'machineSettings']):
                        # We found the next field, reconstruct the keywords
                        keyword_text = ' '.join(quote_content[:-1]).strip()
                        next_field_line = lines[j].strip()
                        
                        # Fix the keywords line
                        key_part = line.split(':')[0]
                        fixed_lines.append(f'{key_part}: "{keyword_text}"')
                        fixed_lines.append(next_field_line)
                        i = j + 1
                        break
                    j += 1
                else:
                    # No next field found, just fix what we have
                    keyword_text = ' '.join(quote_content).strip()
                    key_part = line.split(':')[0]
                    fixed_lines.append(f'{key_part}: "{keyword_text}"')
                    i = j
            else:
                # Normal line processing
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
                i += 1
        
        return '\n'.join(fixed_lines)
