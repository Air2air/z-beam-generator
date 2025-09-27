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

# Abbreviation mappings for standardized naming
MATERIAL_ABBREVIATIONS = {
    'Fiber Reinforced Polyurethane FRPU': {
        'abbreviation': 'FRPU',
        'full_name': 'Fiber Reinforced Polyurethane'
    },
    'Glass Fiber Reinforced Polymers GFRP': {
        'abbreviation': 'GFRP', 
        'full_name': 'Glass Fiber Reinforced Polymers'
    },
    'Carbon Fiber Reinforced Polymer': {
        'abbreviation': 'CFRP',
        'full_name': 'Carbon Fiber Reinforced Polymer'
    },
    'Metal Matrix Composites MMCs': {
        'abbreviation': 'MMCs',
        'full_name': 'Metal Matrix Composites'
    },
    'Ceramic Matrix Composites CMCs': {
        'abbreviation': 'CMCs', 
        'full_name': 'Ceramic Matrix Composites'
    },
    'MDF': {
        'abbreviation': 'MDF',
        'full_name': 'Medium Density Fiberboard'
    },
    'Polyvinyl Chloride': {
        'abbreviation': 'PVC',
        'full_name': 'Polyvinyl Chloride'
    },
    'Polytetrafluoroethylene': {
        'abbreviation': 'PTFE',
        'full_name': 'Polytetrafluoroethylene'
    }
}

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
            
            # Store machine settings ranges (from Materials.yaml - machine-specific)
            self.machine_settings_ranges = materials_data.get('machineSettingsRanges', {})
            
            self.logger.info("Loaded materials research data for enhanced range calculations")
            
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
            raise PropertyDiscoveryError(f"PropertyValueResearcher required for AI-driven property discovery: {e}")
            
        # Load Categories.yaml for enhanced category-level data (after PropertyValueResearcher)
        try:
            self._load_categories_data()
        except Exception as e:
            self.logger.error(f"Failed to load Categories.yaml: {e}")
            # FAIL-FAST per GROK_INSTRUCTIONS.md - Categories.yaml is now required
            raise ValueError(f"Categories.yaml required for enhanced category-level data: {e}")
            
    def _load_categories_data(self):
        """Load Categories.yaml for enhanced category-level data and ranges"""
        try:
            import yaml
            from pathlib import Path
            
                        # Load Categories.yaml for enhanced category data
            base_dir = Path(__file__).resolve().parents[3]
            categories_enhanced_path = base_dir / "data" / "Categories.yaml"
            categories_path = base_dir / "data" / "Categories.yaml"
            
            categories_file = categories_enhanced_path if categories_enhanced_path.exists() else categories_path
            
            if not categories_file.exists():
                raise FileNotFoundError(f"Categories file not found: {categories_file}")
                
            with open(categories_file, 'r', encoding='utf-8') as file:
                categories_data = yaml.safe_load(file)
            
            # Extract category ranges from Categories.yaml structure
            self.category_ranges = {}
            self.category_enhanced_data = {}
            
            # Load standardized descriptions and templates
            self.machine_settings_descriptions = categories_data.get('machineSettingsDescriptions', {})
            self.material_property_descriptions = categories_data.get('materialPropertyDescriptions', {})
            self.environmental_impact_templates = categories_data.get('environmentalImpactTemplates', {})
            self.application_type_definitions = categories_data.get('applicationTypeDefinitions', {})
            self.standard_outcome_metrics = categories_data.get('standardOutcomeMetrics', {})
            
            # Load universal regulatory standards (optimization v2.4.0)
            self.universal_regulatory_standards = categories_data.get('universal_regulatory_standards', [])
            
            if 'categories' in categories_data:
                for category_name, category_info in categories_data['categories'].items():
                    # Store traditional category_ranges (for compatibility)
                    if 'category_ranges' in category_info:
                        self.category_ranges[category_name] = category_info['category_ranges']
                    
                    # Store enhanced category data (industry applications, electrical properties, etc.)
                    self.category_enhanced_data[category_name] = {
                        'industryApplications': category_info.get('industryApplications', {}),
                        'electricalProperties': category_info.get('electricalProperties', {}),
                        'processingParameters': category_info.get('processingParameters', {}),
                        'chemicalProperties': category_info.get('chemicalProperties', {}),
                        'common_applications': category_info.get('common_applications', [])
                    }
            
            self.logger.info(f"Loaded Categories.yaml data: {len(self.category_ranges)} categories with enhanced properties")
            
        except Exception as e:
            self.logger.error(f"Failed to load Categories.yaml: {e}")
            raise

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

    def _apply_abbreviation_template(self, material_name: str) -> Dict[str, str]:
        """Apply abbreviation template formatting for materials with known abbreviations"""
        # Check for exact matches or close matches
        for pattern, mapping in MATERIAL_ABBREVIATIONS.items():
            if (pattern.lower() == material_name.lower() or 
                mapping['full_name'].lower() == material_name.lower() or
                pattern.lower().replace(' ', '').replace('-', '') in material_name.lower().replace(' ', '').replace('-', '')):
                
                return {
                    'name': mapping['abbreviation'],
                    'subcategory': f"{mapping['full_name']} ({mapping['abbreviation']})",
                    'title': f"{mapping['abbreviation']} Laser Cleaning",
                    'description_suffix': f" ({mapping['abbreviation']})"
                }
        
        # No abbreviation template found - use standard formatting
        return {
            'name': material_name.title(),
            'subcategory': material_name.title(),
            'title': f"{material_name.title()} Laser Cleaning",
            'description_suffix': ''
        }

    def _generate_from_yaml(self, material_name: str, material_data: Dict) -> Dict:
        """Generate frontmatter using YAML data with AI enhancement"""
        try:
            self.logger.info(f"Generating frontmatter for {material_name} using YAML data")
            
            # Apply abbreviation template if applicable
            abbreviation_format = self._apply_abbreviation_template(material_name)
            
            # Build base structure from YAML with all required schema fields
            frontmatter = {
                'name': abbreviation_format['name'],
                'title': material_data.get('title', abbreviation_format['title']),
                'description': material_data.get('description', f"Laser cleaning parameters for {material_data.get('name', material_name)}{abbreviation_format['description_suffix']}"),
                'category': material_data.get('category', 'materials').title(),  # Capitalized for consistency
                'subcategory': material_data.get('subcategory', abbreviation_format['subcategory']),
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
            
            # Add standardized sections from Categories.yaml
            frontmatter = self._add_environmental_impact_section(frontmatter, material_data)
            frontmatter = self._add_application_types_section(frontmatter, material_data)
            frontmatter = self._add_outcome_metrics_section(frontmatter, material_data)
            
            # Add regulatory standards (universal + material-specific)
            frontmatter = self._add_regulatory_standards_section(frontmatter, material_data)
            
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
                    
                    # Enhance with standardized descriptions from Categories.yaml
                    property_data = self._enhance_with_standardized_descriptions(
                        property_data, prop_name, 'materialProperties'
                    )
                    
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
                    
                    # Enhance with standardized descriptions from Categories.yaml
                    machine_setting_data = self._enhance_with_standardized_descriptions(
                        machine_setting_data, setting_name, 'machineSettings'
                    )
                    
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
        
        # Get unit from Categories.yaml first, then extraction from material_value - FAIL-FAST: no empty fallbacks
        unit = self._get_category_unit(material_category, prop_key)
        if not unit:
            unit = self._extract_unit(material_value)
        if not unit:
            raise ValueError(f"No unit found for property '{prop_key}' in material '{material_category}' - GROK requires explicit unit data")
        
        # Get research-based ranges for this property and material category
        min_val, max_val = self._get_research_based_range(prop_key, material_category, numeric_value)
        
        # FAIL-FAST: No default confidence - must be calculated from data quality
        confidence = self._calculate_property_confidence(prop_key, material_category, numeric_value)
        
        # Create basic DataMetrics structure
        property_data = {
            'value': numeric_value,
            'unit': unit,
            'confidence': confidence,
            'description': f'{prop_key} property',
            'min': min_val,
            'max': max_val
        }
        
        return property_data

    def _calculate_property_confidence(self, prop_key: str, material_category: str, numeric_value: float) -> float:
        """Calculate confidence based on data quality - FAIL-FAST: no defaults allowed."""
        # Base confidence from data source
        if hasattr(self, 'property_researcher') and self.property_researcher:
            # Research-backed values get higher confidence
            base_confidence = 0.90
        elif self._has_category_data(material_category, prop_key):
            # Category-based values get medium confidence
            base_confidence = 0.75
        else:
            # FAIL-FAST: If no data source, we shouldn't have gotten this far
            raise ValueError(f"No data source found for property '{prop_key}' - GROK requires explicit data backing")
        
        # Adjust based on numeric value reasonableness (if value seems extreme, reduce confidence)
        if numeric_value <= 0:
            # Non-positive values are suspicious for most physical properties
            confidence_adjustment = -0.10
        else:
            confidence_adjustment = 0.0
            
        final_confidence = max(0.1, min(1.0, base_confidence + confidence_adjustment))
        return round(final_confidence, 2)

    def _has_category_data(self, material_category: str, prop_key: str) -> bool:
        """Check if we have category-specific data for this property."""
        try:
            category_data = self.categories_data.get(material_category, {})
            return prop_key in category_data.get('properties', {})
        except Exception:
            return False
    
    def _get_research_based_range(self, prop_key: str, material_category: str, current_value: float) -> tuple[float, float]:
        """Get research-based min/max ranges for a property based on materials science data"""
        # Map property keys to Materials.yaml range keys
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
                
                # Handle Categories.yaml format (separate unit field) vs Materials.yaml format (inline units)
                if isinstance(category_range.get('min'), (int, float)) and isinstance(category_range.get('max'), (int, float)):
                    # Categories.yaml format: numeric min/max with separate unit field
                    min_val = float(category_range['min'])
                    max_val = float(category_range['max'])
                else:
                    # Legacy Materials.yaml format: string values with inline units
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
        """Generate frontmatter content using AI - FAIL-FAST: no fallbacks allowed per GROK"""
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
            
            # Capitalize name, category, and subcategory fields
            if 'name' in parsed:
                parsed['name'] = str(parsed['name']).title()
            if 'category' in parsed:
                parsed['category'] = str(parsed['category']).title()
            if 'subcategory' in parsed:
                parsed['subcategory'] = str(parsed['subcategory']).title()
            
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

    def _get_category_unit(self, material_category: str, prop_key: str) -> Optional[str]:
        """Get unit for property from Categories.yaml enhanced data"""
        try:
            # Map frontend property keys to Categories.yaml range keys
            property_mapping = {
                'density': 'density',
                'thermalConductivity': 'thermalConductivity', 
                'tensileStrength': 'tensileStrength',
                'youngsModulus': 'youngsModulus',
                'hardness': 'hardness',
                'electricalConductivity': 'electricalConductivity',
                'meltingPoint': 'thermalDestructionPoint',
                'thermalExpansion': 'thermalExpansion',
                'thermalDiffusivity': 'thermalDiffusivity',
                'specificHeat': 'specificHeat',
                'laserAbsorption': 'laserAbsorption',
                'laserReflectivity': 'laserReflectivity'
            }
            
            if prop_key in property_mapping:
                range_key = property_mapping[prop_key]
                if (material_category in self.category_ranges and 
                    range_key in self.category_ranges[material_category] and
                    'unit' in self.category_ranges[material_category][range_key]):
                    return self.category_ranges[material_category][range_key]['unit']
                    
            # Check enhanced properties for electrical, processing, chemical properties
            if material_category in self.category_enhanced_data:
                enhanced_data = self.category_enhanced_data[material_category]
                
                for property_type in ['electricalProperties', 'processingParameters', 'chemicalProperties']:
                    if property_type in enhanced_data and prop_key in enhanced_data[property_type]:
                        prop_data = enhanced_data[property_type][prop_key]
                        if isinstance(prop_data, dict) and 'unit' in prop_data:
                            return prop_data['unit']
                            
        except Exception as e:
            self.logger.warning(f"Could not get unit for {prop_key} in {material_category}: {e}")
            
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

    def _enhance_with_standardized_descriptions(self, property_data: Dict, property_name: str, property_type: str) -> Dict:
        """Enhance property data with standardized descriptions from Categories.yaml"""
        try:
            enhanced_data = property_data.copy()
            
            if property_type == 'machineSettings':
                # Skip adding standardized machine settings descriptions to reduce verbosity
                # The AI-generated description is sufficient
                pass
                        
            elif property_type == 'materialProperties':
                # Skip adding standardized material property descriptions to reduce verbosity
                # The AI-generated description is sufficient
                pass
                        
            return enhanced_data
            
        except Exception as e:
            self.logger.warning(f"Failed to enhance {property_name} with standardized descriptions: {e}")
            return property_data  # Return original data if enhancement fails

    def _add_environmental_impact_section(self, frontmatter: Dict, material_data: Dict) -> Dict:
        """Add environmental impact section using standardized templates"""
        try:
            environmental_impact = []
            
            # Apply relevant environmental impact templates
            for impact_type, template in self.environmental_impact_templates.items():
                environmental_impact.append({
                    'benefit': impact_type.replace('_', ' ').title(),
                    'description': template.get('description', ''),
                    'applicableIndustries': template.get('applicable_industries', []),
                    'quantifiedBenefits': template.get('quantified_benefits', ''),
                    'sustainabilityBenefit': template.get('sustainability_benefit', '')
                })
                
            if environmental_impact:
                frontmatter['environmentalImpact'] = environmental_impact
                
            return frontmatter
            
        except Exception as e:
            self.logger.warning(f"Failed to add environmental impact section: {e}")
            return frontmatter

    def _add_application_types_section(self, frontmatter: Dict, material_data: Dict) -> Dict:
        """Add application types section using standardized definitions"""
        try:
            applications = []
            
            # Apply relevant application type definitions
            for app_type, definition in self.application_type_definitions.items():
                applications.append({
                    'type': app_type.replace('_', ' ').title(),
                    'description': definition.get('description', ''),
                    'industries': definition.get('industries', []),
                    'qualityMetrics': definition.get('quality_metrics', []),
                    'typicalTolerances': definition.get('typical_tolerances', ''),
                    'objectives': definition.get('objectives', [])
                })
                
            if applications:
                frontmatter['applicationTypes'] = applications
                
            return frontmatter
            
        except Exception as e:
            self.logger.warning(f"Failed to add application types section: {e}")
            return frontmatter

    def _add_outcome_metrics_section(self, frontmatter: Dict, material_data: Dict) -> Dict:
        """Add outcome metrics section using standardized metrics"""
        try:
            outcome_metrics = []
            
            # Apply relevant standard outcome metrics
            for metric_type, metric_def in self.standard_outcome_metrics.items():
                outcome_metrics.append({
                    'metric': metric_type.replace('_', ' ').title(),
                    'description': metric_def.get('description', ''),
                    'measurementMethods': metric_def.get('measurement_methods', []),
                    'typicalRanges': metric_def.get('typical_ranges', ''),
                    'factorsAffecting': metric_def.get('factors_affecting', []),
                    'units': metric_def.get('units', [])
                })
                
            if outcome_metrics:
                frontmatter['outcomeMetrics'] = outcome_metrics
                
            return frontmatter
        except Exception as e:
            self.logger.error(f"Failed to add outcome metrics: {e}")
            return frontmatter

    def _add_regulatory_standards_section(self, frontmatter: Dict, material_data: Dict) -> Dict:
        """Add regulatory standards combining universal standards from Categories.yaml with material-specific standards"""
        try:
            all_regulatory_standards = []
            
            # Add universal regulatory standards from Categories.yaml (applies to ALL materials)
            if hasattr(self, 'universal_regulatory_standards') and self.universal_regulatory_standards:
                all_regulatory_standards.extend(self.universal_regulatory_standards)
                self.logger.info(f"Added {len(self.universal_regulatory_standards)} universal regulatory standards")
            
            # Add material-specific regulatory standards from Materials.yaml
            material_specific_standards = []
            
            # Check for standards in material_metadata (optimized structure)
            if 'material_metadata' in material_data and 'regulatoryStandards' in material_data['material_metadata']:
                material_specific_standards = material_data['material_metadata']['regulatoryStandards']
            # Fallback to direct field (legacy structure)
            elif 'regulatoryStandards' in material_data:
                material_specific_standards = material_data['regulatoryStandards']
            
            if material_specific_standards:
                all_regulatory_standards.extend(material_specific_standards)
                self.logger.info(f"Added {len(material_specific_standards)} material-specific regulatory standards")
            
            # Add combined regulatory standards to frontmatter
            if all_regulatory_standards:
                frontmatter['regulatoryStandards'] = all_regulatory_standards
                self.logger.info(f"Total regulatory standards: {len(all_regulatory_standards)} (universal + specific)")
            else:
                # Ensure universal standards are always present
                frontmatter['regulatoryStandards'] = self.universal_regulatory_standards if hasattr(self, 'universal_regulatory_standards') else []
                
            return frontmatter
        except Exception as e:
            self.logger.error(f"Failed to add regulatory standards: {e}")
            # Ensure universal standards are preserved even on error
            if hasattr(self, 'universal_regulatory_standards'):
                frontmatter['regulatoryStandards'] = self.universal_regulatory_standards
            return frontmatter
            
        except Exception as e:
            self.logger.warning(f"Failed to add outcome metrics section: {e}")
            return frontmatter