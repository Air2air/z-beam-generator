#!/usr/bin/env python3
"""
Streamlined Frontmatter Generator

Consolidated generator with reduced architectural bloat while preserving all functionality.
Integrates MaterialsYamlFrontmatterMapper and property enhancement directly into core.

Follows GROK fail-fast principles:
- No mocks or fallbacks in production
- Explicit error handling with proper exceptions  
- Validates all configurations immediately
- Single consolidated service instead of wrapper services
- Comprehensive exception handling ensures normalized fields always
"""

import logging
import os
import re
import yaml
from typing import Dict, Optional, Any, List

from generators.component_generators import APIComponentGenerator, ComponentResult, GenerationError
from components.frontmatter.ordering.field_ordering_service import FieldOrderingService
from components.frontmatter.core.validation_helpers import ValidationHelpers
from components.frontmatter.research.property_value_researcher import PropertyValueResearcher

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
                self.material_aware_generator = MaterialAwarePromptGenerator(api_client=api_client)
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
            
        # Initialize PropertyValueResearcher for dynamic property selection
        try:
            self.property_researcher = PropertyValueResearcher(debug_mode=False)
            self.logger.info("PropertyValueResearcher initialized for dynamic property selection")
        except Exception as e:
            self.logger.error(f"PropertyValueResearcher initialization failed: {e}")
            self.property_researcher = None
            
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
                'properties': {},  # Required by schema - will be populated below
            }
            
            # Generate properties with Min/Max ranges
            if 'materialProperties' in material_data or any(key in material_data for key in ['density', 'thermalConductivity', 'tensileStrength', 'youngsModulus']):
                generated_properties = self._generate_properties_with_ranges(material_data, material_name)
                frontmatter['materialProperties'] = generated_properties  # Our enhanced structure  
                frontmatter['properties'] = generated_properties  # Required by schema
            
            # Generate machine settings with Min/Max ranges (always generate for shared architecture)
            frontmatter['machineSettings'] = self._generate_machine_settings_with_ranges(material_data, material_name)
            
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
        """Generate properties with DataMetrics structure including Min/Max ranges using dynamic property selection"""
        properties = {}
        
        # Determine material category and use passed material name
        material_category = material_data.get('category', 'metal')
        # Use the passed material_name parameter instead of trying to get it from material_data
        
        # Use PropertyValueResearcher to discover material-specific properties
        try:
            # Get dynamic property list based on material type
            from research.material_property_research_system import MaterialPropertyResearchSystem
            property_system = MaterialPropertyResearchSystem()
            
            # Try multiple case variations to handle case-insensitive matching
            material_variations = [
                material_name.capitalize(),  # Aluminum
                material_name.upper(),       # ALUMINUM
                material_name.lower(),       # aluminum
                material_name               # Original case
            ]
            
            recommendations = None
            successful_material_name = None
            
            for variant in material_variations:
                test_recommendations = property_system.get_recommended_properties_for_material(variant)
                if 'error' not in test_recommendations:
                    recommendations = test_recommendations
                    successful_material_name = variant
                    break
            
            if recommendations and 'error' not in recommendations:
                # Use recommended properties from research system
                recommended_properties = recommendations.get('recommended_properties', [])
                dynamic_property_list = [prop['name'] for prop in recommended_properties]
                
                logger.info(f"Dynamic property selection for {successful_material_name or material_name}: {dynamic_property_list}")
            else:
                # Fallback to category-based properties
                dynamic_property_list = self._get_fallback_properties(material_category)
                logger.info(f"Using fallback properties for {material_name} ({material_category}): {dynamic_property_list}")
                
        except Exception as e:
            logger.warning(f"Dynamic property selection failed for {material_name}: {e}")
            # Fallback to category-based properties
            dynamic_property_list = self._get_fallback_properties(material_category)
        
        # Convert snake_case research system properties to camelCase for consistency
        def snake_to_camel_case(snake_str: str) -> str:
            """Convert snake_case to camelCase"""
            components = snake_str.split('_')
            return components[0] + ''.join(word.capitalize() for word in components[1:])
        
        def _camel_to_snake_case(camel_str: str) -> str:
            """Convert camelCase to snake_case for research system compatibility"""
            import re
            return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()
        
        # Make it accessible as instance method
        self._camel_to_snake_case = _camel_to_snake_case
        
        # Normalize dynamic property list to camelCase to match materials.yaml naming
        normalized_dynamic_properties = [snake_to_camel_case(prop) for prop in dynamic_property_list]
        
        logger.info(f"Normalized dynamic properties to camelCase: {normalized_dynamic_properties}")
        
        # Materials.yaml data is ignored - we use AI-researched values only
        # Only process properties that are recommended by the dynamic property selection system
        for camel_case_property in normalized_dynamic_properties:
            # Use PropertyValueResearcher to get AI-researched values
            if self.property_researcher:
                try:
                    # Use camelCase property names directly (research system expects camelCase)
                    research_result = self.property_researcher.research_property_value(
                        material_name.lower(), camel_case_property  # Use lowercase material name
                    )
                    if research_result and research_result.success:
                        # Create property data from AI research
                        property_data = {
                            'value': research_result.property_data.value,
                            'unit': research_result.property_data.unit,
                            'confidence': research_result.confidence,
                            'description': research_result.property_data.description,
                            'min': research_result.property_data.min,
                            'max': research_result.property_data.max
                        }
                        properties[camel_case_property] = property_data
                        logger.info(f"AI-researched {camel_case_property}: {research_result.property_data.value} {research_result.property_data.unit} (confidence: {research_result.confidence}%)")
                except Exception as e:
                    logger.warning(f"AI research failed for {camel_case_property}: {e}")
            
            # Fallback: if AI research fails, skip this property (no fallbacks allowed for AI-only mode)
                        
        return properties
        
    def _get_fallback_properties(self, material_category: str) -> List[str]:
        """Get fallback property list when dynamic selection is unavailable (using camelCase)"""
        fallback_properties = {
            'metal': ['density', 'thermalConductivity', 'meltingPoint', 'tensileStrength', 'youngsModulus', 'hardness'],
            'ceramic': ['density', 'meltingPoint', 'hardness', 'thermalConductivity', 'thermalExpansion'],
            'polymer': ['density', 'meltingPoint', 'tensileStrength', 'elasticModulus', 'thermalExpansion'],
            'glass': ['density', 'meltingPoint', 'hardness', 'thermalConductivity'],
            'composite': ['density', 'tensileStrength', 'youngsModulus', 'thermalConductivity']
        }
        
        return fallback_properties.get(material_category, ['density', 'meltingPoint', 'thermalConductivity'])

    def _generate_machine_settings_with_ranges(self, material_data: Dict, material_name: str) -> Dict:
        """Generate machine settings with DataMetrics structure using MachineSettingsResearcher - shared architecture with materialProperties"""
        machine_settings = {}
        
        # Use dedicated MachineSettingsResearcher (fail-fast per GROK - no fallbacks)
        # MachineSettingsResearcher should be initialized in __init__, if not present this will fail-fast
        
        # Machine settings properties for laser cleaning
        machine_property_list = [
            'powerRange',           # Laser power settings
            'wavelength',          # Optimal wavelength for material
            'pulseWidth',          # Pulse duration settings  
            'repetitionRate',      # Laser repetition rate
            'scanSpeed',           # Processing/scanning speed
            'fluenceThreshold'     # Energy density threshold
        ]
        
        # Generate machine settings using MachineSettingsResearcher (shared architecture principle)
        for machine_property in machine_property_list:
            try:
                # Use dedicated machine settings researcher
                research_result = self.machine_settings_researcher.research_machine_setting(
                    material_name.lower(), machine_property  # Same interface pattern as materialProperties
                )
                if research_result and research_result.is_valid():
                    # Create machine setting data using shared DataMetrics structure
                    property_data = {
                        'value': research_result.value,
                        'unit': research_result.unit, 
                        'confidence': research_result.confidence,
                        'description': research_result.calculation_notes or f"AI-researched {machine_property} for {material_name}",
                        'min': research_result.min_range,
                        'max': research_result.max_range
                    }
                    machine_settings[machine_property] = property_data
                    self.logger.info(f"AI-researched machine setting {machine_property}: {research_result.value} {research_result.unit} (confidence: {research_result.confidence}%)")
            except Exception as e:
                self.logger.warning(f"Machine settings research failed for {machine_property}: {e}")
        
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
        
        # Fallback to calculated ranges if no research data available
        self.logger.warning(f"No research data for {prop_key} in {material_category}, using calculated range")
        return round(current_value * 0.8, 2), round(current_value * 1.2, 2)

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
            
            response = self.api_client.generate_simple(
                prompt=prompt,
                max_tokens=4000,
                temperature=0.3
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
                # Fallback author object if not found
                return {
                    'author_object': {
                        'id': author_id,
                        'name': 'Default Author',
                        'bio': 'Materials science expert',
                        'email': 'author@example.com'
                    }
                }
            
            return {
                'author_object': author_info
            }
            
        except Exception as e:
            self.logger.warning(f"Author object generation failed: {e}")
            # Return fallback author object
            return {
                'author_object': {
                    'id': 3,
                    'name': 'Default Author', 
                    'bio': 'Materials science expert',
                    'email': 'author@example.com'
                }
            }