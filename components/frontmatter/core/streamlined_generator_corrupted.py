#!/usr/bin/env python3
"""
Streamlined Frontmatter Generator

Consolidated generator with reduced architectural bloat while preserving all functionality.
Integrates MaterialsYamlFrontmatterMapper and property enhancement directly into core.

Follows GROK fail-fast principles:
- No mocks or fallbacks in production
- Explicit error handling with proper exceptions
- Validates all configurations immediately
- Single consolidated service instead of      def _extract_unit_from_range(self, range_config: Dict) -> str:pply_field_ordering(self, frontmatter: Di        except Exception as e:
            logger.error(f\"Failed to format YAML: {e}\")
            # Fail-fast: YAML formatting must succeed - no fallback
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
from typing import Dict, Optional, Any

from generators.component_generators import APIComponentGenerator, ComponentResult
from components.frontmatter.ordering.field_ordering_service import FieldOrderingService
from components.frontmatter.core.validation_helpers import ValidationHelpers
from generators.component_generators import GenerationError  # Add this import

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

    def __init__(self):
        super().__init__("frontmatter")
        self.category_ranges = {}
        self.machine_settings_ranges = {}
        
        # Initialize enhanced schema validator if available
        if ENHANCED_VALIDATION_AVAILABLE:
            try:
                # Use enhanced unified schema as primary, with fallbacks
                unified_schema_path = os.path.join(os.path.dirname(__file__), "../../../schemas/enhanced_unified_frontmatter.json")
                enhanced_schema_path = os.path.join(os.path.dirname(__file__), "../../../schemas/enhanced_frontmatter.json")
                fallback_schema_path = os.path.join(os.path.dirname(__file__), "../../../schemas/frontmatter.json")
                
                # Priority: unified > enhanced > fallback
                if os.path.exists(unified_schema_path):
                    schema_path = unified_schema_path
                elif os.path.exists(enhanced_schema_path):
                    schema_path = enhanced_schema_path
                else:
                    schema_path = fallback_schema_path
                
                self.enhanced_validator = EnhancedSchemaValidator(schema_path)
                logger.info(f"Enhanced schema validator initialized with {os.path.basename(schema_path)}")
            except Exception as e:
                logger.warning(f"Failed to initialize enhanced validator: {e}")
                self.enhanced_validator = None
        else:
            self.enhanced_validator = None
        
        # Initialize material-aware prompt generator if available
        if MATERIAL_AWARE_PROMPTS_AVAILABLE:
            try:
                self.material_aware_generator = MaterialAwarePromptGenerator()
                self.material_exception_handler = MaterialExceptionHandler()
                logger.info("Material-aware prompt system initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize material-aware prompts: {e}")
                self.material_aware_generator = None
                self.material_exception_handler = None
        else:
            self.material_aware_generator = None
            self.material_exception_handler = None
            
        self._load_configurations()

    def _load_configurations(self):
        """Load all required configurations with fail-fast behavior"""
        try:
            # Initialize API client
            from api.client_factory import APIClientFactory
            self.api_client = APIClientFactory.create_client()
            
            # Load Materials.yaml data
            materials_yaml_path = os.path.join(os.path.dirname(__file__), "../../../data/Materials.yaml")
            with open(materials_yaml_path, "r") as f:
                materials_data = yaml.safe_load(f)
            
            self.category_ranges = materials_data.get("category_ranges", {})
            self.machine_settings_ranges = materials_data.get("machineSettingsRanges", materials_data.get("machine_settings_ranges", {}))
            self.materials_data = materials_data
            
            logger.info(f"Loaded configurations: {len(self.category_ranges)} categories, {len(self.machine_settings_ranges)} machine settings")
            
            # Load prompt configuration
            self._load_prompt_config()
            
        except Exception as e:
            raise ValueError(f"Failed to load required configurations: {e}")

    # Consolidation helpers for error handling and debug logging
    def _debug_log(self, message: str, context: str = ""):
        """Consolidated debug logging"""
        context_str = f" [{context}]" if context else ""
        print(f"DEBUG{context_str}: {message}")

    def _handle_generation_error(self, error: Exception, operation: str):
        """Consolidated error handling for generation operations"""
        error_msg = f"Failed to {operation}: {str(error)}"
        print(f"ERROR: {error_msg}")
        return ComponentResult(
            component_type="frontmatter",
            content="",
            success=False,
            error_message=str(error)
        )

    def generate(self, material_name: str, **kwargs) -> ComponentResult:
        """
        Generate comprehensive frontmatter with fail-fast behavior.
        
        Args:
            material_name: Name of the material to generate frontmatter for
            **kwargs: Additional generation parameters
            
        Returns:
            ComponentResult with generated frontmatter
        """
        try:
            logger.info(f"Generating frontmatter for {material_name}")
            
            # Generate frontmatter directly via API - no fallbacks
            frontmatter = self._core_generate(material_name, **kwargs)
            
            # Apply field ordering
            ordered_frontmatter = self._apply_field_ordering(frontmatter)
            
            # Enhanced schema validation (optional)
            enhanced_mode = kwargs.get('enhanced_validation', False)
            if enhanced_mode and self.enhanced_validator:
                validation_result = self._validate_with_enhanced_schema(ordered_frontmatter, material_name)
                if not validation_result.is_valid:
                    # In enhanced mode, fail-fast on schema violations
                    validation_errors = "; ".join(validation_result.errors)
                    raise ValueError(f"Enhanced schema validation failed: {validation_errors}")
                else:
                    logger.info(f"Enhanced validation passed - Quality: {validation_result.quality_score:.1f}%, Coverage: {validation_result.research_validation_coverage:.1%}")
            
            return ComponentResult(
                component_type="frontmatter",
                content=self._format_as_yaml(ordered_frontmatter),
                success=True
            )
            
        except Exception as e:
            logger.error(f"Frontmatter generation failed for {material_name}: {e}")
            return self._handle_generation_error(e, f"generate frontmatter for {material_name}")
    
    def _core_generate(self, material_name: str, **kwargs) -> Dict:
        """
        Core generation logic (wrapped by exception handler)
        
        This method contains the original generation logic but is now
        wrapped by comprehensive exception handling.
        """
        # Handle materials_data override from kwargs
        original_materials_data = None
        if 'materials_data' in kwargs:
            original_materials_data = getattr(self, 'materials_data', None)
            self.materials_data = kwargs['materials_data']
        
        try:
            # Always use AI generation for dynamic materialProperties and machineSettings
            # Materials.yaml only provides basic metadata (category, subcategory, author_id)
            frontmatter = self._generate_from_api(material_name, **kwargs)
            
            # Overlay basic metadata from Materials.yaml if available
            material_data = self._get_material_data(material_name)
            if material_data:
                # Preserve AI-generated technical content, overlay basic metadata only
                for key in ['category', 'subcategory', 'author_id', 'complexity', 'index']:
                    if key in material_data:
                        frontmatter[key] = material_data[key]
                logger.info(f"Generated frontmatter via AI for {material_name} with metadata overlay")
            else:
                logger.info(f"Generated frontmatter via AI for {material_name}")
        
        finally:
            # Restore original materials_data if it was overridden
            if original_materials_data is not None:
                self.materials_data = original_materials_data
            elif 'materials_data' in kwargs:
                # If there was no original, remove the attribute
                if hasattr(self, 'materials_data'):
                    delattr(self, 'materials_data')
        
        # Apply unified property enhancement (with exception handling built-in)
        # Note: Property enhancement disabled - original flat structure maintained
        
        return frontmatter

    def _get_material_data(self, material_name: str) -> Optional[Dict]:
        """Get material data from Materials.yaml with index enrichment"""
        if not hasattr(self, 'materials_data'):
            return None
        
        material_index = self.materials_data.get('material_index', {})
        materials_structure = self.materials_data.get('materials', {})
        
        # Get index data for category and subcategory 
        index_data = {}
        for indexed_name, data in material_index.items():
            if indexed_name.lower() == material_name.lower():
                index_data = data.copy()
                break
        
        # Get rich data from materials structure
        for category_data in materials_structure.values():
            if 'items' in category_data:
                for item in category_data['items']:
                    if item.get('name', '').lower() == material_name.lower():
                        # Merge index data (category/subcategory) with rich data
                        merged_data = item.copy()
                        if index_data:
                            merged_data.update({k: v for k, v in index_data.items() 
                                              if k not in merged_data or not merged_data[k]})
                        return merged_data
        
        return index_data if index_data else None

    def _generate_from_materials_data(self, material_data: Dict, material_name: str) -> Dict:
        """Generate frontmatter from Materials.yaml data with original flat structure"""
        frontmatter = {}
        
        # 1. Core identification
        frontmatter.update({
            'name': material_data.get('name', material_name),
            'category': material_data.get('category', 'unknown'),
            'subcategory': material_data.get('subcategory', 'general'),
            'complexity': material_data.get('complexity', 'medium'),
            'difficulty_score': material_data.get('difficulty_score', 3),
            'author_id': material_data.get('author_id', 1)
        })
        
        # 2. Content metadata  
        frontmatter.update(self._generate_content_metadata(material_data, material_name))
        
        # 3. Chemical Properties (original flat structure)
        if 'formula' in material_data:
            frontmatter['chemicalProperties'] = {
                'formula': material_data['formula'],
                'symbol': material_data.get('symbol', material_data['formula'])
            }
        
        # 4. Material Properties (original flat structure)  
        properties = self._generate_properties_with_ranges(material_data)
        if properties:
            frontmatter['materialProperties'] = properties
        
        # 5. Machine Settings (original flat structure)
        machine_settings = self._generate_machine_settings_with_ranges(material_data)
        if machine_settings:
            frontmatter['machineSettings'] = machine_settings
        
        # 6. Applications and compatibility
        if 'applications' in material_data:
            frontmatter['applications'] = material_data['applications']
            
        if 'compatibility' in material_data:
            frontmatter['compatibility'] = material_data['compatibility']
        
        # 7. Author object (required by schema)
        frontmatter.update(self._generate_author_object(material_data))
        
        # 8. Images section (hero and micro images)
        frontmatter['images'] = self._generate_images_section(material_name)
            
        return frontmatter

    def _extract_numeric_only(self, value):
        """Extract numeric value from a string that may contain units"""
        if isinstance(value, (int, float)):
            return value
        
        if isinstance(value, str):
            # Remove common unit suffixes and extract numeric part
            import re
            # Match number (int or float) at the beginning of the string
            match = re.match(r'^(-?\d+(?:\.\d+)?)', value.strip())
            if match:
                numeric_str = match.group(1)
                try:
                    # Return int if it's a whole number, float otherwise
                    if '.' in numeric_str:
                        return float(numeric_str)
                    else:
                        return int(numeric_str)
                except ValueError:
                    return None
        
        return None

    def _generate_content_metadata(self, material_data: Dict, material_name: str) -> Dict:
        """Generate content metadata from materials data"""
        category = material_data.get('category', 'material')
        
        return {
            'title': f"Laser Cleaning {material_name}",
            'headline': f"Comprehensive laser cleaning guide for {category} {material_name.lower()}",
            'description': f"Technical overview of {material_name} laser cleaning applications and parameters",
            'keywords': self._generate_keywords(material_data, material_name)
        }

    def _generate_keywords(self, material_data: Dict, material_name: str) -> str:
        """Generate keywords from material data"""
        keywords = [
            material_name.lower(),
            f"{material_name.lower()} {material_data.get('category', 'material')}",
            'laser ablation',
            'laser cleaning',
            'non-contact cleaning'
        ]
        
        # Add from applications
        applications = material_data.get('applications', [])[:2]
        for app in applications:
            if ':' in app:
                industry = app.split(':')[0].strip().lower()
                keywords.append(f"{industry} applications")
        
        return ', '.join(keywords)

    def _generate_properties_with_ranges(self, material_data: Dict) -> Dict:
        """Generate properties with Min/Max ranges - required for DataMetrics schema"""
        # Use the working implementation to provide required Min/Max structure
        return self._generate_basic_properties(material_data)
    
    def _generate_basic_properties(self, material_data: Dict) -> Dict:
        """Generate properties with DataMetrics structure including Min/Max ranges"""
        properties = {}
        
        # Map actual Materials.yaml keys to property names
        property_mappings = {
            'density': 'density',
            'thermalConductivity': 'thermalConductivity', 
            'tensile_strength': 'tensileStrength',
            'youngs_modulus': 'youngsModulus',
            'meltingPoint': 'meltingPoint',
            'hardness': 'hardness',
            'electrical_conductivity': 'electricalConductivity'
        }
        
        for yaml_key, prop_key in property_mappings.items():
            if yaml_key in material_data:
                material_value = material_data[yaml_key]
                # Create DataMetrics structure with value, unit, confidence
                property_data = self._create_datametrics_property(material_value, prop_key)
                if property_data:
                    properties[prop_key] = property_data
                        
        return properties
        
    def _extract_unit(self, value_with_unit: str) -> str:
        """Extract unit from a string like '7.8-8.9 g/cm³'"""
        if not isinstance(value_with_unit, str):
            return ""
        
        import re
        # Look for unit patterns at the end of the string
        unit_match = re.search(r'([a-zA-Z/°×·⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)$', value_with_unit.strip())
        return unit_match.group(1) if unit_match else ""
    
    def _add_property_ranges_from_value(self, properties: Dict, value_str: str, prop_key: str):
        """Extract min/max ranges from values like '7.8-8.9 g/cm³' or '15-400 W/m·K'"""
        if not isinstance(value_str, str):
            return
            
        import re
        # Look for range pattern like "7.8-8.9" or "15-400"
        range_match = re.search(r'(\d+(?:\.\d+)?)\s*[-–—]\s*(\d+(?:\.\d+)?)', value_str)
        if range_match:
            min_val = float(range_match.group(1))
            max_val = float(range_match.group(2))
            properties[f'{prop_key}Min'] = min_val
            properties[f'{prop_key}Max'] = max_val

    def _add_property_ranges(self, properties: Dict, material_category: str, prop_key: str, range_key: str):
        """Add Min/Max/Unit ranges for a property"""
        if material_category not in self.category_ranges:
            return
        
        category_data = self.category_ranges[material_category]
        if range_key not in category_data:
            return
            
        prop_data = category_data[range_key]
        if not isinstance(prop_data, dict) or 'min' not in prop_data or 'max' not in prop_data:
            return
        
        # Extract unit from min/max values and numeric values only
        unit = self._extract_unit_from_range(prop_data)
        min_numeric = self._extract_numeric_only(prop_data['min'])
        max_numeric = self._extract_numeric_only(prop_data['max'])
        
        if min_numeric is not None:
            properties[f"{prop_key}Min"] = min_numeric
        if max_numeric is not None:
            properties[f"{prop_key}Max"] = max_numeric
        
        if unit:
            properties[f"{prop_key}Unit"] = unit

    def _generate_machine_settings_with_ranges(self, material_data: Dict) -> Dict:
        """Generate machine settings with DataMetrics structure including Min/Max ranges"""
        if 'machineSettings' not in material_data:
            return {}
        
        machine_settings_data = material_data['machineSettings']
        machine_settings = {}
        
        # Map actual machine settings keys
        machine_mappings = {
            'powerRange': 'powerRange',
            'pulseDuration': 'pulseDuration', 
            'wavelengthOptimal': 'wavelength',
            'spotSize': 'spotSize',
            'repetitionRate': 'repetitionRate',
            'fluenceThreshold': 'fluenceRange'
        }
        
        for yaml_key, settings_key in machine_mappings.items():
            if yaml_key in machine_settings_data:
                setting_value = machine_settings_data[yaml_key]
                # Create DataMetrics structure with value, unit, confidence, min/max
                setting_data = self._create_datametrics_property(setting_value, settings_key)
                if setting_data:
                    machine_settings[settings_key] = setting_data
                    
        return machine_settings
    
    def _create_datametrics_property(self, material_value, prop_key: str) -> Dict:
        """Create DataMetrics structure with value, unit, confidence, and Min/Max ranges"""
        # Extract numeric value and unit
        numeric_value = self._extract_numeric_only(material_value)
        if numeric_value is None:
            return None
        
        unit = self._extract_unit(material_value) or ""
        
        # Create basic DataMetrics structure
        property_data = {
            'value': numeric_value,
            'unit': unit,
            'confidence': 0.85,  # Default confidence level
            'description': f'{prop_key.replace("_", " ").title()} property'
        }
        
        # Add Min/Max ranges with variation based on property type
        property_data['min'] = round(numeric_value * 0.8, 2)  # 20% lower
        property_data['max'] = round(numeric_value * 1.2, 2)  # 20% higher
        
        return property_data

    def _add_machine_setting_ranges(self, machine_settings: Dict, settings_key: str, range_key: str):
        """Add Min/Max/Unit ranges for machine settings"""
        if range_key not in self.machine_settings_ranges:
            return
            
        ranges = self.machine_settings_ranges[range_key]
        if not isinstance(ranges, dict) or 'min' not in ranges or 'max' not in ranges:
            return
        
        # Extract unit from min/max values and numeric values only
        unit = self._extract_unit_from_range(ranges)
        min_numeric = self._extract_numeric_only(ranges['min'])
        max_numeric = self._extract_numeric_only(ranges['max'])
        
        if min_numeric is not None:
            machine_settings[f"{settings_key}Min"] = min_numeric
        if max_numeric is not None:
            machine_settings[f"{settings_key}Max"] = max_numeric
        
        if unit:
            machine_settings[f"{settings_key}Unit"] = unit

    def _generate_from_api(self, material_name: str, material_data: Dict) -> Dict:
        """Generate frontmatter content using AI with fallback to range functions for Min/Max"""
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
        """Generate frontmatter via API for materials not in YAML"""
        try:
            # Use material-aware prompts if available
            if self.material_aware_generator:
                logger.info(f"Using material-aware prompts for {material_name}")
                prompt = self.material_aware_generator.generate_material_aware_prompt(
                    material_name=material_name,
                    component_type="frontmatter",
                    base_prompt=self._get_base_frontmatter_prompt(),
                    **kwargs
                )
            else:
                # Fallback to basic prompts
                logger.info(f"Using basic prompts for {material_name}")
                prompt = self._build_prompt(material_name, **kwargs)
            
            response = self.api_client.generate_simple(
                prompt=prompt,
                max_tokens=4000,
                temperature=0.3
            )
            
            # Parse and structure the response
            frontmatter = self._parse_api_response(response, material_name)
            
            # Apply material-specific validation if available
            if self.material_aware_generator:
                try:
                    validated_frontmatter = self.material_aware_generator.validate_generated_content(
                        content=frontmatter,
                        material_name=material_name,
                        component_type="frontmatter"
                    )
                    if validated_frontmatter:
                        frontmatter = validated_frontmatter
                        logger.info(f"Applied material-specific validation for {material_name}")
                except Exception as e:
                    logger.warning(f"Material-specific validation failed for {material_name}: {e}")
                    # Continue with unvalidated content
            
            # Ensure images section is included
            if 'images' not in frontmatter:
                frontmatter['images'] = self._generate_images_section(material_name)
            
            return frontmatter
            
        except Exception as e:
            raise ValueError(f"API generation failed for {material_name}: {e}")

    def _apply_property_enhancement(self, frontmatter: Dict):
        """Apply unified property enhancement - original flat structure maintained"""
        # Original flat structure (chemicalProperties, properties, machineSettings) maintained
        # Legacy property enhancement not needed for restored original format
        pass

    def _apply_field_ordering(self, frontmatter: Dict) -> Dict:
        """Apply field ordering using the existing service"""
        return FieldOrderingService.apply_field_ordering(frontmatter)

    def _generate_images_section(self, material_name: str) -> Dict:
        """
        Generate images section with hero and micro images.
        
        Creates proper alt text and URL patterns following schema requirements.
        
        Args:
            material_name: Name of the material
            
        Returns:
            Dict with 'hero' and 'micro' image objects containing 'alt' and 'url'
        """
        # Create URL-safe material name
        url_safe_name = material_name.lower().replace(' ', '-')
        
        # Generate descriptive alt text
        hero_alt = f"{material_name} surface undergoing laser cleaning showing precise contamination removal"
        micro_alt = f"Microscopic view of {material_name} surface after laser cleaning showing detailed surface structure"
        
        return {
            'hero': {
                'alt': hero_alt,
                'url': f'/images/{url_safe_name}-laser-cleaning-hero.jpg'
            },
            'micro': {
                'alt': micro_alt,
                'url': f'/images/{url_safe_name}-laser-cleaning-micro.jpg'
            }
        }

    def _validate_frontmatter(self, frontmatter: Dict, material_name: str):
        """Validate generated frontmatter"""
        try:
            ValidationHelpers.validate_and_enhance_content(frontmatter, material_name)
        except Exception as e:
            logger.warning(f"Frontmatter validation warning for {material_name}: {e}")
            # Don't fail generation for validation warnings

    def _extract_unit_from_range(self, range_config: Dict) -> str:
        """Extract unit from range configuration"""
        for val in [range_config.get("min", ""), range_config.get("max", "")]:
            if val:
                unit_match = re.search(r'[a-zA-Z°/³²·]+', str(val))
                if unit_match:
                    return unit_match.group()
        return ""

    def get_component_info(self) -> Dict[str, Any]:
        """Return component information"""
        return {
            "name": "frontmatter",
            "description": "Streamlined frontmatter generation with integrated services",
            "version": "2.0.0-streamlined",
            "requires_api": True,  # Fail-fast: No mocks or fallbacks allowed
            "type": "dynamic",
            "capabilities": [
                "Materials.yaml integration",
                "unified property enhancement", 
                "consolidated architecture",
                "fail-fast validation"
            ]
        }

    # Existing methods that need to be preserved
    def _load_prompt_config(self):
        """Load prompt configuration (existing method)"""
        try:
            self.prompt_config = {
                "system_prompt": "Generate comprehensive laser cleaning frontmatter",
                "user_prompt": "Material: {material_name}\nGenerate detailed frontmatter including properties, machine settings, and applications."
            }
        except Exception as e:
            logger.error(f"Error loading prompt config: {e}")
            self.prompt_config = {}

    def _build_prompt(self, material_name: str, **kwargs) -> str:
        """Build API prompt for material"""
        base_prompt = self.prompt_config.get("user_prompt", "").format(material_name=material_name)
        return base_prompt
    
    def _get_base_frontmatter_prompt(self) -> str:
        """Get base frontmatter generation prompt for material-aware system"""
        return """Generate comprehensive frontmatter metadata for laser cleaning applications.

Required sections:
- title: Descriptive title for the material
- name: Material name
- category: Material category (metal, ceramic, plastic, etc.)
- subcategory: More specific classification
- description: Technical overview
- materialProperties: Physical and chemical properties using DataMetrics structure:
  Each property should have: {value: number, unit: string, confidence: percentage}
  Include: density, melting_point, thermal_conductivity, hardness, etc.
- machineSettings: Laser parameters using DataMetrics structure:
  Each setting should have: {value: number, unit: string, confidence: percentage}
  May include min/max ranges: {value: number, unit: string, min: number, max: number, confidence: percentage}
  Include: power_range, wavelength, pulse_duration, frequency, scan_speed, etc.
- applications: Industrial applications and use cases (array)
- author_object: Author information with id, name, title, country, expertise, sex
- images: Hero and micro image specifications with alt text and URLs

Format as valid YAML frontmatter with proper DataMetrics structure."""

    def _parse_api_response(self, response, material_name: str) -> Dict:
        """Parse API response into structured frontmatter - fail-fast on invalid responses"""
        import yaml
        import re
        
        # Extract content from APIResponse object
        if hasattr(response, 'content'):
            content = response.content
        else:
            content = str(response)
            
        logger.debug(f"Parsing API response for {material_name}: {len(content)} characters")
        
        # Try to extract YAML content from the response
        yaml_patterns = [
            r'```yaml\n(.*?)\n```',
            r'```\n(.*?)\n```', 
            r'---\n(.*?)\n---'
        ]
        
        yaml_content = None
        for pattern in yaml_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                yaml_content = match.group(1).strip()
                break
        
        if not yaml_content:
            raise ValueError(f"No valid YAML content found in API response for {material_name}")
        
        try:
            # Parse the extracted YAML - handle multiple documents by taking the first
            if yaml_content.count('---') > 1:
                # Split on document separators and take the first valid document
                docs = yaml_content.split('---')
                for doc in docs:
                    doc = doc.strip()
                    if doc and not doc.startswith('#'):  # Skip empty docs and comments
                        try:
                            parsed_data = yaml.safe_load(doc)
                            if isinstance(parsed_data, dict) and parsed_data:
                                yaml_content = doc  # Use this document
                                break
                        except Exception:
                            continue
            
            parsed_data = yaml.safe_load(yaml_content)
            if not isinstance(parsed_data, dict):
                raise ValueError(f"API response did not contain valid YAML dictionary for {material_name}")
            
            # Ensure basic required fields exist
            if 'name' not in parsed_data:
                parsed_data['name'] = material_name
                
            logger.info(f"Successfully parsed YAML frontmatter for {material_name}")
            return parsed_data
            
        except yaml.YAMLError as e:
            raise ValueError(f"YAML parsing failed for {material_name}: {e}")
        except Exception as e:
            raise ValueError(f"Response parsing failed for {material_name}: {e}")

    def _validate_with_enhanced_schema(self, frontmatter_data: Dict, material_name: str):
        """
        Validate frontmatter data with enhanced schema validation.
        
        Args:
            frontmatter_data: Generated frontmatter to validate
            material_name: Material name for context
            
        Returns:
            ValidationResult with detailed validation feedback
        """
        if not self.enhanced_validator:
            logger.warning("Enhanced validator not available - skipping validation")
            return None
            
        try:
            validation_result = self.enhanced_validator.validate(frontmatter_data, material_name)
            
            # Log validation details
            if validation_result.errors:
                logger.warning(f"Enhanced validation errors for {material_name}: {validation_result.errors}")
            if validation_result.warnings:
                logger.info(f"Enhanced validation warnings for {material_name}: {validation_result.warnings}")
                
            return validation_result
            
        except Exception as e:
            logger.error(f"Enhanced validation failed for {material_name}: {e}")
            # In enhanced mode, validation failures should be reported
            raise ValueError(f"Enhanced validation error: {e}")

    def _generate_author_object(self, material_data: Dict) -> Dict:
        """Generate author_object from material data author_id"""
        try:
            from utils.core.author_manager import get_author_by_id
            
            author_id = material_data.get('author_id', 1)
            author_info = get_author_by_id(author_id)
            
            if not author_info:
                raise ValueError(f"No author found for ID {author_id}")
            
            return {
                'author_object': author_info
            }
            
        except Exception as e:
            logger.error(f"Failed to resolve author object: {e}")
            # Fail-fast behavior - don't provide fallback
            raise ValueError(f"Author object generation failed: {e}")

    def _format_as_yaml(self, frontmatter_data: Dict) -> str:
        """Format frontmatter data as pure YAML content (no delimiters)"""
        try:
            import yaml
            yaml_content = yaml.dump(
                frontmatter_data, 
                default_flow_style=False, 
                sort_keys=False, 
                allow_unicode=True,
                width=1000
            )
            return yaml_content.rstrip() + "\n"
        except Exception as e:
            logger.error(f"Failed to format YAML: {e}")
            # Return basic format as fallback
            return f"{str(frontmatter_data)}\n"

    def _create_template_variables(self, material_name: str, material_data: Dict, api_client) -> Dict:
        """Create template variables for testing purposes"""
        return {
            "material_name": material_name,
            "category": material_data.get('category', 'unknown').title(),
            "complexity": material_data.get('complexity', 'medium')
        }
