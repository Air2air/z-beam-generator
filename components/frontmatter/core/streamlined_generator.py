#!/usr/bin/env python3
"""
Streamlined Frontmatter Generator

Consolidated generator with reduced architectural bloat while preserving all functionality.
Integrates MaterialsYamlFrontmatterMapper and property enhancement directly into core.

Follows GROK fail-fast principles:
- No mocks or fallbacks in production
- Explicit error handling with proper exceptions  
- Validates all configurations immediately
            if 'machineSettings' in parsed_content:
                range_machine_settings = self._generate_machine_settings_with_ranges(material_data, material_name)
                parsed_content['machineSettings'] = self._merge_with_ranges(parsed_content['machineSettings'], range_machine_settings)
            
            # Ensure images section is included if not provided by AI
            if 'images' not in parsed_content:
                parsed_content['images'] = self._generate_images_section(material_name)
                
            self.logger.info(f"Successfully generated frontmatter for {material_name} with Min/Max ranges")
            return parsed_contentle consolidated service instead of wrapper services
- Comprehensive exception handling ensures normalized fields always
"""

import logging
import re
import yaml
from typing import Dict, Optional

from generators.component_generators import APIComponentGenerator, ComponentResult, GenerationError
from components.frontmatter.ordering.field_ordering_service import FieldOrderingService
from components.frontmatter.core.validation_helpers import ValidationHelpers
from components.frontmatter.research.property_value_researcher import PropertyValueResearcher


class PropertyDiscoveryError(Exception):
    """Raised when property discovery fails - no fallbacks allowed per GROK_INSTRUCTIONS.md"""
    pass

logger = logging.getLogger(__name__)

# Enhanced schema validation (optional)
try:
    from scripts.validation.enhanced_schema_validator import EnhancedSchemaValidator
    ENHANCED_VALIDATION_AVAILABLE = True
    logger.info("Enhanced schema validation loaded successfully")
except ImportError as e:
    ENHANCED_VALIDATION_AVAILABLE = False
    EnhancedSchemaValidator = None
    logger.info(f"Enhanced schema validation not available - using basic validation: {e}")

# Import material-aware prompt system
try:
    from ai_research.prompt_exceptions.material_aware_generator import MaterialAwarePromptGenerator
    from ai_research.prompt_exceptions.material_exception_handler import AIPromptExceptionHandler as MaterialExceptionHandler
    MATERIAL_AWARE_PROMPTS_AVAILABLE = True
    logger.info("Material-aware prompt system loaded successfully")
except ImportError as e:
    MATERIAL_AWARE_PROMPTS_AVAILABLE = False
    MaterialAwarePromptGenerator = None
    MaterialExceptionHandler = None
    logger.warning(f"Material-aware prompt system not available - using basic prompts: {e}")


class StreamlinedFrontmatterGenerator(APIComponentGenerator):
    """Consolidated frontmatter generator with integrated services"""
    
    def __init__(self, api_client=None, config=None):
        """Initialize with required dependencies"""
        super().__init__("frontmatter")
        self.logger = logging.getLogger(__name__)
        
        # Store api_client and config for use
        self.api_client = api_client
        self.config = config
        
        # API client is only required for pure AI generation
        # For YAML-based generation with research enhancement, we can work without it
        
        # Load materials research data for range calculations
        self._load_materials_research_data()
        
        # Initialize integrated services
        self.validation_helpers = ValidationHelpers()
        self.field_ordering_service = FieldOrderingService()
        
        # Enhanced validation setup (optional)
        self.enhanced_validator = None
        if ENHANCED_VALIDATION_AVAILABLE:
            try:
                self.enhanced_validator = EnhancedSchemaValidator()
                self.logger.info("Enhanced validation initialized")
            except Exception as e:
                self.logger.warning(f"Enhanced validation setup failed: {e}")
        
        # Material-aware prompt system (optional)
        self.material_aware_generator = None
        if MATERIAL_AWARE_PROMPTS_AVAILABLE:
            try:
                self.material_aware_generator = MaterialAwarePromptGenerator()
                self.logger.info("Material-aware prompt system initialized")
            except Exception as e:
                self.logger.warning(f"Material-aware prompt system setup failed: {e}")

    def _load_materials_research_data(self):
        """Load materials science research data for accurate range calculations"""
        try:
            from data.materials import load_materials
            materials_data = load_materials()
            
            # Store category ranges for material properties
            self.category_ranges = materials_data.get('category_ranges', {})
            
            # Store machine settings ranges
            self.machine_settings_ranges = materials_data.get('machineSettingsRanges', {})
            
            self.logger.info("Loaded materials research data for accurate range calculations")
            
        except Exception as e:
            self.logger.error(f"Failed to load materials research data: {e}")
            # Fail-fast: Materials research data is required for accurate ranges
            raise ValueError(f"Materials research data required for accurate property ranges: {e}")
            
        # Initialize PropertyValueResearcher for comprehensive property discovery (NO FALLBACKS per GROK)
        try:
            self.property_researcher = PropertyValueResearcher(api_client=self.api_client, debug_mode=False)
            self.logger.info("PropertyValueResearcher initialized for comprehensive property discovery (GROK compliant - no fallbacks)")
        except Exception as e:
            self.logger.error(f"PropertyValueResearcher initialization failed: {e}")
            # FAIL-FAST per GROK_INSTRUCTIONS.md - no fallbacks allowed
            raise ValueError(f"PropertyValueResearcher required for comprehensive property discovery: {e}")
            
        # Initialize MachineSettingsResearcher for machine settings generation
        try:
            from components.frontmatter.research.machine_settings_researcher import MachineSettingsResearcher
            if not self.property_researcher:
                raise ValueError("PropertyValueResearcher required for MachineSettingsResearcher initialization")
            self.machine_settings_researcher = MachineSettingsResearcher(
                material_researcher=self.property_researcher,
                confidence_threshold=50,
                debug_mode=False
            )
            self.logger.info("MachineSettingsResearcher initialized for machine settings generation")
        except Exception as e:
            self.logger.error(f"MachineSettingsResearcher initialization failed: {e}")
            # Fail-fast per GROK instructions - no fallbacks allowed
            raise ValueError(f"MachineSettingsResearcher required for machine settings generation: {e}")

    def generate(self, material_name: str, **kwargs) -> ComponentResult:
        """Generate frontmatter content"""
        try:
            self.logger.info(f"Generating frontmatter for {material_name}")
            
            # Load material data first
            from data.materials import get_material_by_name
            material_data = get_material_by_name(material_name)
            
            if material_data:
                # Use YAML data with AI enhancement
                content = self._generate_from_yaml(material_name, material_data)
            else:
                # Pure AI generation for unknown materials
                content = self._generate_from_api(material_name, {})
            
            # Apply field ordering
            ordered_content = self.field_ordering_service.apply_field_ordering(content)
            
            # Enhanced validation if available
            if self.enhanced_validator:
                try:
                    validation_result = self.enhanced_validator.validate(ordered_content, material_name)
                    if validation_result.is_valid:
                        self.logger.info("Enhanced validation passed")
                    else:
                        self.logger.warning(f"Enhanced validation warnings: {validation_result.error_messages}")
                except Exception as e:
                    self.logger.warning(f"Enhanced validation failed: {e}")
            
            # Convert to proper YAML format
            import yaml
            yaml_content = yaml.dump(ordered_content, default_flow_style=False, allow_unicode=True, sort_keys=False, indent=2)
            
            return ComponentResult(
                component_type="frontmatter",
                content=yaml_content,
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"Frontmatter generation failed for {material_name}: {str(e)}")
            return ComponentResult(
                component_type="frontmatter",
                content="",
                success=False,
                error_message=str(e)
            )

    def _generate_from_yaml(self, material_name: str, material_data: Dict) -> Dict:
        """Generate frontmatter using YAML data with AI enhancement"""
        try:
            self.logger.info(f"Generating frontmatter for {material_name} using YAML data")
            
            # Build base structure from YAML with all required schema fields
            frontmatter = {
                'name': material_name.lower(),  # Required by schema
                'title': material_data.get('title', f"{material_name.title()} Laser Cleaning"),
                'description': material_data.get('description', f"Laser cleaning parameters for {material_name}"),
                'category': material_data.get('category', 'materials'),
                'subcategory': material_data.get('subcategory', material_name.lower()),
                'author_id': material_data.get('author_id', 3),  # Required by schema (not authorId)
                'applications': material_data.get('applications', ['laser cleaning', 'surface preparation']),  # Required by schema
            }
            
            # Generate properties with Min/Max ranges
            if 'materialProperties' in material_data or any(key in material_data for key in ['density', 'thermalConductivity', 'tensileStrength', 'youngsModulus']):
                generated_properties = self._generate_properties_with_ranges(material_data, material_name)
                frontmatter['materialProperties'] = generated_properties  # Our enhanced structure
            
            # Generate machine settings with Min/Max ranges (always generate for shared architecture)
            frontmatter['machineSettings'] = self._generate_machine_settings_with_ranges(material_data, material_name)
            
            # Generate images section
            frontmatter['images'] = self._generate_images_section(material_name)
            
            # Generate author object (required by schema)
            frontmatter.update(self._generate_author_object(material_data))
            
            return frontmatter
            
        except Exception as e:
            self.logger.error(f"YAML generation failed for {material_name}: {str(e)}")
            raise GenerationError(f"Failed to generate from YAML for {material_name}: {str(e)}")

    def _generate_properties_with_ranges(self, material_data: Dict, material_name: str) -> Dict:
        """Generate properties with Min/Max ranges - required for DataMetrics schema"""
        # Use the working implementation to provide required Min/Max structure
        return self._generate_basic_properties(material_data, material_name)

    def _generate_basic_properties(self, material_data: Dict, material_name: str) -> Dict:
        """Generate properties with DataMetrics structure using comprehensive AI discovery (GROK compliant - no fallbacks)"""
        properties = {}
        
        # Use PropertyValueResearcher for comprehensive material property discovery
        if not self.property_researcher:
            # FAIL-FAST per GROK_INSTRUCTIONS.md - no fallbacks allowed
            raise PropertyDiscoveryError("PropertyValueResearcher required for comprehensive property discovery")
            
        try:
            # Use comprehensive AI discovery to get ALL relevant properties with complete data
            discovered_properties = self.property_researcher.discover_all_material_properties(material_name)
            
            self.logger.info(f"Comprehensive AI discovery found {len(discovered_properties)} properties for {material_name}")
            
            # Use discovered properties directly (no need for additional research)
            for prop_name, prop_data in discovered_properties.items():
                try:
                    # Property data already complete from AI discovery
                    property_data = {
                        'value': prop_data['value'],
                        'unit': prop_data['unit'],
                        'confidence': prop_data['confidence'],
                        'description': prop_data['description'],
                        'min': prop_data.get('min'),
                        'max': prop_data.get('max')
                    }
                    properties[prop_name] = property_data
                    self.logger.info(f"AI-discovered {prop_name}: {prop_data['value']} {prop_data['unit']} (confidence: {prop_data['confidence']}%)")
                except Exception as e:
                    self.logger.warning(f"Error processing discovered property {prop_name}: {e}")
                        
                except Exception as e:
                    self.logger.warning(f"Property research failed for {prop_name}: {e}")
                    # Continue with other properties - don't fail entire generation for one property
                    
        except Exception as e:
            self.logger.error(f"Comprehensive property discovery failed for {material_name}: {e}")
            # FAIL-FAST per GROK_INSTRUCTIONS.md - no fallbacks allowed
            raise PropertyDiscoveryError(f"Cannot generate materialProperties without comprehensive discovery for {material_name}: {e}")
        
        if not properties:
            # FAIL-FAST - must have at least some properties for valid frontmatter
            raise PropertyDiscoveryError(f"No properties discovered for {material_name} - comprehensive discovery required")
                        
        return properties

    def _generate_machine_settings_with_ranges(self, material_data: Dict, material_name: str) -> Dict:
        """Generate machine settings with DataMetrics structure using comprehensive AI discovery (GROK compliant - no fallbacks)"""
        machine_settings = {}
        
        # Use PropertyValueResearcher for comprehensive machine settings discovery
        if not self.property_researcher:
            # FAIL-FAST per GROK_INSTRUCTIONS.md - no fallbacks allowed
            raise PropertyDiscoveryError("PropertyValueResearcher required for comprehensive machine settings discovery")
            
        try:
            # Use comprehensive AI discovery to find ALL relevant machine settings
            discovered_settings = self.property_researcher.discover_all_machine_settings(material_name)
            
            self.logger.info(f"Comprehensive AI discovery found {len(discovered_settings)} machine settings for {material_name}")
            
            # Use discovered settings directly (no need for additional research)
            for setting_name, setting_data in discovered_settings.items():
                try:
                    # Machine setting data already complete from AI discovery
                    machine_setting_data = {
                        'value': setting_data['value'],
                        'unit': setting_data['unit'],
                        'confidence': setting_data['confidence'],
                        'description': setting_data['description'],
                        'min': setting_data.get('min'),
                        'max': setting_data.get('max')
                    }
                    machine_settings[setting_name] = machine_setting_data
                    self.logger.info(f"AI-discovered machine setting {setting_name}: {setting_data['value']} {setting_data['unit']} (confidence: {setting_data['confidence']}%)")
                except Exception as e:
                    self.logger.warning(f"Error processing discovered machine setting {setting_name}: {e}")
                    # Continue with other settings - don't fail entire generation for one setting
                    
        except Exception as e:
            self.logger.error(f"Comprehensive machine settings discovery failed for {material_name}: {e}")
            # FAIL-FAST per GROK_INSTRUCTIONS.md - no fallbacks allowed
            raise PropertyDiscoveryError(f"Cannot generate machineSettings without comprehensive discovery for {material_name}: {e}")
        
        if not machine_settings:
            # FAIL-FAST - must have at least some machine settings for valid frontmatter
            raise PropertyDiscoveryError(f"No machine settings discovered for {material_name} - comprehensive discovery required")
        
        return machine_settings

    def _create_datametrics_property(self, material_value, prop_key: str, material_category: str = 'metal') -> Dict:
        """Create DataMetrics structure with research-based Min/Max ranges"""
        # Extract numeric value and unit
        numeric_value = self._extract_numeric_only(material_value)
        if numeric_value is None:
            return None
        
        unit = self._extract_unit(material_value) or ""
        
        # Get research-based ranges for this property and material category
        min_val, max_val = self._get_research_based_range(prop_key, material_category, numeric_value)
        
        # Create basic DataMetrics structure
        property_data = {
            'value': numeric_value,
            'unit': unit,
            'confidence': 0.85,  # Default confidence level
            'description': f'{prop_key} property',
            'min': min_val,
            'max': max_val
        }
        
        return property_data
    
    def _get_research_based_range(self, prop_key: str, material_category: str, current_value: float) -> tuple[float, float]:
        """Get research-based min/max ranges for a property based on materials science data"""
        # Map property keys to materials.yaml range keys
        property_mapping = {
            'density': 'density',
            'thermalConductivity': 'thermalConductivity', 
            'tensileStrength': 'tensileStrength',
            'youngsModulus': 'youngsModulus',
            'hardness': 'hardness',
            'electricalConductivity': 'electricalConductivity',
            'meltingPoint': 'thermalDestructionPoint'
        }
        
        # Map machine settings to range keys
        machine_mapping = {
            'powerRange': 'powerRange',
            'pulseDuration': 'pulseDuration',
            'wavelength': 'wavelength', 
            'spotSize': 'spotSize',
            'repetitionRate': 'repetitionRate',
            'fluenceRange': 'fluenceThreshold'
        }
        
        # Try material property ranges first
        if prop_key in property_mapping:
            range_key = property_mapping[prop_key]
            if material_category in self.category_ranges and range_key in self.category_ranges[material_category]:
                category_range = self.category_ranges[material_category][range_key]
                min_val = self._extract_numeric_only(category_range['min'])
                max_val = self._extract_numeric_only(category_range['max'])
                return min_val, max_val
        
        # Try machine settings ranges 
        if prop_key in machine_mapping:
            range_key = machine_mapping[prop_key]
            if range_key in self.machine_settings_ranges:
                machine_range = self.machine_settings_ranges[range_key]
                min_val = self._extract_numeric_only(machine_range['min'])
                max_val = self._extract_numeric_only(machine_range['max'])
                return min_val, max_val
        
        # FAIL-FAST per GROK_INSTRUCTIONS.md - no fallbacks allowed, must have research data
        raise PropertyDiscoveryError(f"No research data available for {prop_key} in {material_category} - comprehensive AI discovery required")

    def _generate_from_api(self, material_name: str, material_data: Dict) -> Dict:
        """Generate frontmatter content using AI with fallback to range functions for Min/Max"""
        if not self.api_client:
            raise ValueError("API client is required for AI generation - no fallbacks allowed")
            
        try:
            self.logger.info(f"Generating frontmatter for {material_name} using AI with Min/Max from range functions")
            
            # Generate AI content first
            ai_content = self._call_api_for_generation(material_name, material_data)
            if not ai_content:
                raise GenerationError(f"Failed to generate AI content for {material_name}")
                
            # Parse AI response and merge with Min/Max from range functions
            parsed_content = self._parse_api_response(ai_content, material_data)
            
            # Ensure Min/Max and description fields are present using range functions
            if 'materialProperties' in parsed_content:
                range_properties = self._generate_properties_with_ranges(material_data)
                parsed_content['materialProperties'] = self._merge_with_ranges(parsed_content['materialProperties'], range_properties)
            
            if 'machineSettings' in parsed_content:
                range_machine_settings = self._generate_machine_settings_with_ranges(material_data)
                parsed_content['machineSettings'] = self._merge_with_ranges(parsed_content['machineSettings'], range_machine_settings)
                
            self.logger.info(f"Successfully generated frontmatter for {material_name} with Min/Max ranges")
            return parsed_content
            
        except Exception as e:
            self.logger.error(f"API generation failed for {material_name}: {str(e)}")
            raise GenerationError(f"Failed to generate frontmatter for {material_name}: {str(e)}")
    
    def _merge_with_ranges(self, ai_properties: Dict, range_properties: Dict) -> Dict:
        """Merge AI-generated content with range-generated Min/Max and description fields"""
        merged = ai_properties.copy()
        
        for prop_key, range_data in range_properties.items():
            if prop_key in merged:
                # Ensure AI content has required Min/Max and description
                if isinstance(merged[prop_key], dict) and isinstance(range_data, dict):
                    # Add missing Min/Max from range data
                    if 'min' not in merged[prop_key] and 'min' in range_data:
                        merged[prop_key]['min'] = range_data['min']
                    if 'max' not in merged[prop_key] and 'max' in range_data:
                        merged[prop_key]['max'] = range_data['max']
                    if 'description' not in merged[prop_key] and 'description' in range_data:
                        merged[prop_key]['description'] = range_data['description']
            else:
                # Add entire property if missing from AI content
                merged[prop_key] = range_data
                
        return merged
    
    def _call_api_for_generation(self, material_name: str, material_data: Dict) -> str:
        """Call API to generate frontmatter content"""
        try:
            # Build material-aware prompt
            prompt = self._build_material_prompt(material_name, material_data)
            
            # Get generation configuration from run.py - FAIL FAST if unavailable
            from run import get_component_generation_config
            gen_config = get_component_generation_config("frontmatter")
            max_tokens = gen_config["max_tokens"]
            temperature = gen_config["temperature"]
            
            response = self.api_client.generate_simple(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"API call failed for {material_name}: {str(e)}")
            raise GenerationError(f"API generation failed for {material_name}: {str(e)}")

    def _build_material_prompt(self, material_name: str, material_data: Dict) -> str:
        """Build material-specific prompt for frontmatter generation"""
        prompt = f"""Generate comprehensive laser cleaning frontmatter for {material_name}.

Required structure with DataMetrics format:
- Each property must have: value, unit, confidence, min, max, description
- materialProperties: density, thermalConductivity, tensileStrength, etc.
- machineSettings: powerRange, wavelength, pulseDuration, etc.

Material context: {material_data}

Return YAML format with materialProperties (not properties) and machineSettings sections."""
        
        return prompt

    def _parse_api_response(self, response: str, material_data: Dict) -> Dict:
        """Parse API response into structured frontmatter"""
        try:
            # Extract YAML from response
            yaml_match = re.search(r'```yaml\n(.*?)\n```', response, re.DOTALL)
            if yaml_match:
                yaml_content = yaml_match.group(1)
            else:
                yaml_content = response
            
            # Parse YAML
            parsed = yaml.safe_load(yaml_content)
            if not isinstance(parsed, dict):
                raise ValueError("Invalid YAML structure")
            
            return parsed
            
        except Exception as e:
            self.logger.error(f"Failed to parse API response: {str(e)}")
            raise GenerationError(f"Response parsing failed: {str(e)}")

    def _extract_numeric_only(self, value) -> Optional[float]:
        """Extract numeric value from string or return number directly"""
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Extract first number from string
            match = re.search(r'(\d+(?:\.\d+)?)', value)
            if match:
                return float(match.group(1))
        
        return None

    def _extract_unit(self, value) -> Optional[str]:
        """Extract unit from string value"""
        if isinstance(value, str):
            # Extract unit after number - improved regex for special characters
            match = re.search(r'\d+(?:\.\d+)?\s*([a-zA-Z/°³²¹⁰⁻⁺μ]+)', value)
            if match:
                return match.group(1)
        
        return None

    def _generate_author_object(self, material_data: Dict) -> Dict:
        """Generate author_object from material data author_id"""
        try:
            from utils.core.author_manager import get_author_by_id
            
            author_id = material_data.get('author_id', 3)
            author_info = get_author_by_id(author_id)
            
            if not author_info:
                # FAIL-FAST per GROK_INSTRUCTIONS.md - no fallbacks allowed
                raise PropertyDiscoveryError(f"Author with ID {author_id} not found - author system required for content generation")
            
            return {
                'author_object': author_info
            }
            
        except Exception as e:
            self.logger.error(f"Author object generation failed: {e}")
            # FAIL-FAST per GROK_INSTRUCTIONS.md - no fallbacks allowed
            raise PropertyDiscoveryError(f"Author system required for content generation: {e}")

    def _generate_images_section(self, material_name: str) -> Dict:
        """
        Generate images section with material-specific URLs and alt text
        
        Creates proper alt text and URL patterns following schema requirements.
        Handles special characters, multi-word names, and URL normalization.
        
        Args:
            material_name: Name of the material
            
        Returns:
            Dict with 'hero' and 'micro' image objects containing 'alt' and 'url'
        """
        try:
            import re
            
            # Create URL-safe material name (lowercase, hyphens, handle special chars)
            material_slug = material_name.lower()
            material_slug = re.sub(r'[^a-z0-9\s-]', '', material_slug)  # Remove special chars except spaces and hyphens
            material_slug = re.sub(r'\s+', '-', material_slug)  # Replace spaces with hyphens
            material_slug = re.sub(r'-+', '-', material_slug)  # Collapse multiple hyphens
            material_slug = material_slug.strip('-')  # Remove leading/trailing hyphens
            
            # Generate descriptive alt text with proper capitalization
            material_title = material_name.title()
            hero_alt = f'{material_title} surface undergoing laser cleaning showing precise contamination removal'
            micro_alt = f'Microscopic view of {material_title} surface after laser cleaning showing detailed surface structure'
            
            return {
                'hero': {
                    'alt': hero_alt,
                    'url': f'/images/{material_slug}-laser-cleaning-hero.jpg'
                },
                'micro': {
                    'alt': micro_alt,
                    'url': f'/images/{material_slug}-laser-cleaning-micro.jpg'
                }
            }
            
        except Exception as e:
            self.logger.error(f"Images section generation failed for {material_name}: {e}")
            # FAIL-FAST per GROK_INSTRUCTIONS.md - no fallbacks allowed
            raise PropertyDiscoveryError(f"Images section generation required: {e}")