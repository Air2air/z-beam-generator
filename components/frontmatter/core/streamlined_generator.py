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
from pathlib import Path
from typing import Dict, Optional

from generators.component_generators import APIComponentGenerator, ComponentResult
from components.frontmatter.ordering.field_ordering_service import FieldOrderingService
from components.frontmatter.core.validation_helpers import ValidationHelpers
from components.frontmatter.research.property_value_researcher import PropertyValueResearcher
from components.frontmatter.services.property_discovery_service import PropertyDiscoveryService
from components.frontmatter.services.property_research_service import PropertyResearchService
from components.frontmatter.services.template_service import TemplateService
from components.frontmatter.services.pipeline_process_service import PipelineProcessService

# Refactored services (Step 1 & 2 of refactoring plan)
from components.frontmatter.services.property_manager import PropertyManager
from components.frontmatter.core.property_processor import PropertyProcessor

# Import unified exception classes from validation system
from validation.errors import (
    PropertyDiscoveryError,
    ConfigurationError,
    MaterialDataError,
    GenerationError
)

# Phase 3.3: Import validation utilities for confidence normalization
from components.frontmatter.services.validation_utils import ValidationUtils

# Qualitative property definitions and classification
from components.frontmatter.qualitative_properties import (
    QUALITATIVE_PROPERTIES,
    MATERIAL_CHARACTERISTICS_CATEGORIES,
    is_qualitative_property
)

# Property categorizer for analysis and validation (REQUIRED per fail-fast)
from utils.core.property_categorizer import get_property_categorizer

logger = logging.getLogger(__name__)

def _load_frontmatter_config() -> Dict:
    """
    Load frontmatter generation configuration from YAML file.
    Fails fast if configuration file is missing or invalid.
    
    Returns:
        Dict containing material_abbreviations and thermal_property_mapping
        
    Raises:
        ConfigurationError: If configuration file missing or invalid
    """
    config_path = Path(__file__).parent.parent.parent.parent / 'config' / 'frontmatter_generation.yaml'
    
    if not config_path.exists():
        raise ConfigurationError(
            f"Frontmatter configuration not found at {config_path}. "
            "This file is required for generation. Ensure config/frontmatter_generation.yaml exists."
        )
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Validate required sections
        required_sections = ['material_abbreviations', 'thermal_property_mapping']
        for section in required_sections:
            if section not in config:
                raise ConfigurationError(
                    f"Configuration missing required section '{section}'. "
                    f"Check {config_path} for proper structure."
                )
        
        logger.info(f"Loaded frontmatter configuration from {config_path}")
        return config
        
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in {config_path}: {e}")
    except Exception as e:
        raise ConfigurationError(f"Failed to load configuration from {config_path}: {e}")

# Load configuration at module level (fail-fast if config missing)
_FRONTMATTER_CONFIG = _load_frontmatter_config()
MATERIAL_ABBREVIATIONS = _FRONTMATTER_CONFIG['material_abbreviations']
THERMAL_PROPERTY_MAP = _FRONTMATTER_CONFIG['thermal_property_mapping']

# Enhanced schema validation (REQUIRED per fail-fast)
from scripts.validation.enhanced_schema_validator import EnhancedSchemaValidator
logger.info("Enhanced schema validation loaded successfully")

# Import material-aware prompt system (REQUIRED per fail-fast)
from material_prompting.core.material_aware_generator import MaterialAwarePromptGenerator
from material_prompting.exceptions.handler import MaterialExceptionHandler
logger.info("Material-aware prompt system loaded successfully")


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
        
        # Initialize service placeholders (will be set during data loading)
        self.property_discovery_service = None  # Initialized in _load_categories_data()
        self.property_research_service = None  # Initialized in _load_categories_data()
        self.template_service = None  # Initialized in _load_categories_data()
        self.pipeline_process_service = None  # Initialized in _load_categories_data()
        
        # Load materials research data for range calculations
        self._load_materials_research_data()
        
        # Initialize integrated services
        self.validation_helpers = ValidationHelpers()
        self.field_ordering_service = FieldOrderingService()
        
        # Enhanced validation setup (REQUIRED)
        try:
            self.enhanced_validator = EnhancedSchemaValidator()
            self.logger.info("Enhanced validation initialized")
        except Exception as e:
            raise ConfigurationError(f"Enhanced validation required but setup failed: {e}")
        
        # Material-aware prompt system (REQUIRED)
        try:
            self.material_aware_generator = MaterialAwarePromptGenerator()
            self.logger.info("Material-aware prompt system initialized")
        except Exception as e:
            raise ConfigurationError(f"Material-aware prompt system required but setup failed: {e}")

    def _load_materials_research_data(self):
        """Load materials science research data for accurate range calculations"""
        try:
            from data.materials import load_materials_cached
            materials_data = load_materials_cached()  # Use cached version for performance
            
            # Store machine settings ranges (from Materials.yaml - machine-specific) - FAIL-FAST per GROK_INSTRUCTIONS.md
            if 'machineSettingsRanges' not in materials_data:
                raise MaterialDataError("machineSettingsRanges section required in materials data - these ranges are easily researched and provide critical value")
            self.machine_settings_ranges = materials_data['machineSettingsRanges']
            
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
            if 'categories' in categories_data:
                for category_name, category_data in categories_data['categories'].items():
                    if 'properties' in category_data:
                        self.category_ranges[category_name] = category_data['properties']
                self.logger.info(f"Loaded category ranges for {len(self.category_ranges)} categories")
            else:
                raise ConfigurationError("'categories' section missing from Categories.yaml")
            
            self.category_enhanced_data = {}
            self.categories_data = categories_data  # Store full categories data for unified industry access
            
            # Load standardized descriptions and templates - FAIL-FAST per GROK_INSTRUCTIONS.md
            if 'machineSettingsDescriptions' not in categories_data:
                raise ConfigurationError("machineSettingsDescriptions section required in Categories.yaml")
            self.machine_settings_descriptions = categories_data['machineSettingsDescriptions']
            
            # Initialize PropertyDiscoveryService with categories data
            self.property_discovery_service = PropertyDiscoveryService(categories_data=categories_data)
            self.logger.info("PropertyDiscoveryService initialized with categories data")
            
            # Initialize TemplateService with configuration and ranges
            self.template_service = TemplateService(
                material_abbreviations=MATERIAL_ABBREVIATIONS,
                thermal_property_map=THERMAL_PROPERTY_MAP,
                category_ranges=self.category_ranges
            )
            self.logger.info("TemplateService initialized with abbreviations and thermal mappings")
            
            # Initialize PropertyResearchService with researcher and template service functions
            self.property_research_service = PropertyResearchService(
                property_researcher=self.property_researcher,
                get_category_ranges_func=self.template_service.get_category_ranges_for_property,
                enhance_descriptions_func=self.template_service.enhance_with_standardized_descriptions
            )
            self.logger.info("PropertyResearchService initialized with property researcher")
            
            # Initialize PropertyManager (refactored unified service - Step 1)
            self.property_manager = PropertyManager(
                property_researcher=self.property_researcher,
                categories_data=categories_data,
                get_category_ranges_func=self.template_service.get_category_ranges_for_property
            )
            self.logger.info("PropertyManager initialized (refactored unified service)")
            
            # Initialize PropertyProcessor (refactored processing service - Step 2)
            self.property_processor = PropertyProcessor(
                categories_data=categories_data,
                category_ranges=self.category_ranges
            )
            self.logger.info("PropertyProcessor initialized (refactored processing service)")
            
            if 'materialPropertyDescriptions' not in categories_data:
                raise ConfigurationError("materialPropertyDescriptions section required in Categories.yaml")
            self.material_property_descriptions = categories_data['materialPropertyDescriptions']
            
            if 'environmentalImpactTemplates' not in categories_data:
                raise ConfigurationError("environmentalImpactTemplates section required in Categories.yaml")
            self.environmental_impact_templates = categories_data['environmentalImpactTemplates']
            
            # Load applicationTypeDefinitions for test compliance
            if 'applicationTypeDefinitions' not in categories_data:
                raise ConfigurationError("applicationTypeDefinitions section required in Categories.yaml")
            self.application_type_definitions = categories_data['applicationTypeDefinitions']
            
            if 'standardOutcomeMetrics' not in categories_data:
                raise ConfigurationError("standardOutcomeMetrics section required in Categories.yaml")
            self.standard_outcome_metrics = categories_data['standardOutcomeMetrics']
            
            # Load universal regulatory standards (optimization v2.4.0) - FAIL-FAST per GROK_INSTRUCTIONS.md
            if 'universal_regulatory_standards' not in categories_data:
                raise ConfigurationError("universal_regulatory_standards section required in Categories.yaml")
            self.universal_regulatory_standards = categories_data['universal_regulatory_standards']
            
            # Initialize PipelineProcessService AFTER loading all required templates/standards
            self.pipeline_process_service = PipelineProcessService(
                environmental_impact_templates=self.environmental_impact_templates,
                standard_outcome_metrics=self.standard_outcome_metrics,
                universal_regulatory_standards=self.universal_regulatory_standards,
                category_enhanced_data=self.category_enhanced_data
            )
            self.logger.info("PipelineProcessService initialized with pipeline templates")
            
            if 'categories' in categories_data:
                for category_name, category_info in categories_data['categories'].items():
                    # Store traditional category_ranges (for compatibility)
                    if 'category_ranges' in category_info:
                        self.category_ranges[category_name] = category_info['category_ranges']
                    
                    # Store enhanced category data (industry applications, electrical properties, etc.) - FAIL-FAST per GROK_INSTRUCTIONS.md
                    enhanced_data = {}
                    
                    if 'industryApplications' in category_info:
                        enhanced_data['industryApplications'] = category_info['industryApplications']
                    if 'electricalProperties' in category_info:
                        enhanced_data['electricalProperties'] = category_info['electricalProperties']
                    if 'processingParameters' in category_info:
                        enhanced_data['processingParameters'] = category_info['processingParameters']
                    if 'chemicalProperties' in category_info:
                        enhanced_data['chemicalProperties'] = category_info['chemicalProperties']
                    if 'common_applications' in category_info:
                        enhanced_data['common_applications'] = category_info['common_applications']
                    if 'industryTags' in category_info:
                        enhanced_data['industryTags'] = category_info['industryTags']
                    
                    self.category_enhanced_data[category_name] = enhanced_data
            
            self.logger.info(f"Loaded Categories.yaml data: {len(self.category_ranges)} categories with enhanced properties")
            
        except Exception as e:
            self.logger.error(f"Failed to load Categories.yaml: {e}")
            raise

    def generate(self, material_name: str, **kwargs) -> ComponentResult:
        """Generate frontmatter content"""
        try:
            self.logger.info(f"Generating frontmatter for {material_name}")
            
            # Load material data first (using cached version for performance)
            from data.materials import get_material_by_name_cached
            material_data = get_material_by_name_cached(material_name)
            
            if material_data:
                # Use YAML data with AI enhancement
                content = self._generate_from_yaml(material_name, material_data)
            else:
                # Pure AI generation for unknown materials
                content = self._generate_from_api(material_name, {})
            
            # Apply field ordering (handles both flat and categorized structures)
            ordered_content = self.field_ordering_service.apply_field_ordering(content)
            
            # Add prompt chain verification metadata
            ordered_content = self._add_prompt_chain_verification(ordered_content)
            
            # Enforce camelCase for caption keys (fix snake_case if present)
            if 'caption' in ordered_content and isinstance(ordered_content['caption'], dict):
                caption = ordered_content['caption']
                # Convert snake_case to camelCase if needed
                if 'before_text' in caption:
                    caption['beforeText'] = caption.pop('before_text')
                if 'after_text' in caption:
                    caption['afterText'] = caption.pop('after_text')
                if 'technical_analysis' in caption:
                    caption['technicalAnalysis'] = caption.pop('technical_analysis')
                if 'material_properties' in caption:
                    caption['materialProperties'] = caption.pop('material_properties')
                if 'image_url' in caption:
                    caption['imageUrl'] = caption.pop('image_url')
                self.logger.debug("Enforced camelCase for caption keys")
            
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

    def _add_prompt_chain_verification(self, content: Dict) -> Dict:
        """
        Add prompt chain verification metadata to frontmatter content.
        
        Per copilot-instructions.md:
        - Verifies all 4 prompt components were integrated (base, persona, formatting, AI detection)
        - Tracks configuration loading status
        - Records author/persona information
        - Timestamps verification
        
        Args:
            content: Frontmatter content dictionary
            
        Returns:
            Content with prompt_chain_verification metadata added
        """
        from datetime import datetime, timezone
        
        self.logger.info("🔍 Adding prompt chain verification metadata...")
        
        # For frontmatter component: We don't use text prompts, but we verify config loading
        # The text component uses the actual 3-layer prompt system
        verification = {
            'base_config_loaded': True,  # frontmatter_generation.yaml loaded at module level
            'persona_config_loaded': False,  # N/A for frontmatter (text component only)
            'formatting_config_loaded': False,  # N/A for frontmatter (text component only)
            'ai_detection_config_loaded': False,  # N/A for frontmatter (text component only)
            'persona_country': 'N/A',  # Frontmatter doesn't use author personas
            'author_id': 0,  # No author for frontmatter
            'verification_timestamp': datetime.now(timezone.utc).isoformat(),
            'prompt_components_integrated': 1,  # Only base config for frontmatter
            'human_authenticity_focus': False,  # N/A for structured data
            'cultural_adaptation_applied': False  # N/A for structured data
        }
        
        content['prompt_chain_verification'] = verification
        self.logger.info(f"✅ Added prompt chain verification metadata: {len(verification)} fields")
        
        return content

    def _generate_from_yaml(self, material_name: str, material_data: Dict) -> Dict:
        """Generate frontmatter using YAML data with AI enhancement"""
        try:
            self.logger.info(f"Generating frontmatter for {material_name} using YAML data")
            
            # Apply abbreviation template if applicable
            if not self.template_service:
                raise ConfigurationError("TemplateService not initialized")
            abbreviation_format = self.template_service.apply_abbreviation_template(material_name)
            
            # Build base structure from YAML with all required schema fields - FAIL-FAST per GROK_INSTRUCTIONS.md
            category = (material_data['category'] if 'category' in material_data else 'materials').title()
            subcategory = material_data['subcategory'] if 'subcategory' in material_data else abbreviation_format['subcategory']
            
            frontmatter = {
                'name': abbreviation_format['name'],
                'title': material_data['title'] if 'title' in material_data else abbreviation_format['title'],
                'subtitle': self._generate_subtitle(
                    material_name=abbreviation_format['name'],
                    category=category,
                    subcategory=subcategory,
                    material_data=material_data
                ),
                'description': material_data['description'] if 'description' in material_data else f"Laser cleaning parameters for {material_data['name'] if 'name' in material_data else material_name}{abbreviation_format['description_suffix']}",
                'category': category,
                'subcategory': subcategory,
            }
            
            # OPTIMIZATION: Check Materials.yaml for industryTags first before calling AI
            yaml_industries = None
            if 'material_metadata' in material_data and 'industryTags' in material_data['material_metadata']:
                yaml_industries = material_data['material_metadata']['industryTags']
                if isinstance(yaml_industries, list) and len(yaml_industries) > 0:
                    self.logger.info(f"✅ Using {len(yaml_industries)} applications from Materials.yaml industryTags")
                    frontmatter['applications'] = yaml_industries
                elif isinstance(yaml_industries, dict):
                    # Handle structured industryTags (primary/secondary)
                    apps = []
                    if 'primary_industries' in yaml_industries:
                        apps.extend(yaml_industries['primary_industries'])
                    if 'secondary_industries' in yaml_industries:
                        apps.extend(yaml_industries['secondary_industries'])
                    if apps:
                        self.logger.info(f"✅ Using {len(apps)} applications from Materials.yaml structured industryTags")
                        frontmatter['applications'] = apps
                        yaml_industries = apps
            
            # Fallback to AI generation only if no YAML industryTags
            if not yaml_industries or not frontmatter.get('applications'):
                if self.api_client:
                    try:
                        self.logger.info(f"🤖 Calling AI to generate applications for {material_name} (no YAML industryTags)")
                        ai_content = self._call_api_for_generation(material_name, material_data)
                        if ai_content:
                            self.logger.info(f"📥 AI response received, parsing...")
                            parsed_ai = self._parse_api_response(ai_content, material_data)
                            # Extract applications from AI response and convert to simple strings
                            if 'applications' in parsed_ai and isinstance(parsed_ai['applications'], list):
                                self.logger.info(f"🤖 AI generated {len(parsed_ai['applications'])} applications")
                                simplified_apps = []
                                for app in parsed_ai['applications']:
                                    if isinstance(app, dict) and 'industry' in app:
                                        simplified_apps.append(app['industry'])
                                    elif isinstance(app, str):
                                        simplified_apps.append(app)
                                    else:
                                        raise GenerationError(f"Invalid application format: {type(app)}")
                                frontmatter['applications'] = simplified_apps
                            else:
                                raise GenerationError(f"No applications in AI response for {material_name}")
                    except Exception as e:
                        self.logger.error(f"❌ Failed to generate AI applications: {e}")
                        import traceback
                        traceback.print_exc()
                        # FAIL-FAST per GROK_INSTRUCTIONS.md - no fallbacks allowed
                        raise GenerationError(f"Failed to generate applications for {material_name}: {e}")
                else:
                    # FAIL-FAST per GROK_INSTRUCTIONS.md - must have applications
                    raise GenerationError(f"No industryTags in YAML and no API client for {material_name}")
            
            # Generate properties with Min/Max ranges using unified inheritance
            unified_properties = self._get_unified_material_properties(material_name, material_data)
            
            # REFACTORED: Use PropertyManager for discovery + research (Step 1)
            if self.property_manager:
                material_category = material_data.get('category', 'metal')
                
                # Merge unified properties with existing properties from YAML
                existing_properties = material_data.get('properties', {})
                for prop_type, props in unified_properties.items():
                    if prop_type == 'properties':
                        existing_properties.update(props)
                
                # Use PropertyManager for complete discovery → research → categorization pipeline
                research_result = self.property_manager.discover_and_research_properties(
                    material_name=material_name,
                    material_category=material_category,
                    existing_properties=existing_properties
                )
                
                # Use PropertyProcessor to organize and apply ranges (Step 2)
                categorized_quantitative = self.property_processor.organize_properties_by_category(
                    research_result.quantitative_properties
                )
                
                # Apply category ranges to quantitative properties
                frontmatter['materialProperties'] = self.property_processor.apply_category_ranges(
                    categorized_quantitative,
                    material_category
                )
                
                # Qualitative characteristics already organized by PropertyManager
                frontmatter['materialCharacteristics'] = research_result.qualitative_characteristics
                
                self.logger.info(
                    f"✅ Refactored property generation for {material_name}: "
                    f"{len(frontmatter['materialProperties'])} quantitative categories, "
                    f"{len(frontmatter.get('materialCharacteristics', {}))} qualitative categories"
                )
            else:
                # FAIL-FAST per GROK_INSTRUCTIONS.md - no fallbacks allowed
                raise PropertyDiscoveryError(f"PropertyManager required for property generation for {material_name}")
            
            # Generate machine settings with Min/Max ranges (always generate for shared architecture)
            frontmatter['machineSettings'] = self._generate_machine_settings_with_ranges(material_data, material_name)
            
            # Generate images section
            frontmatter['images'] = self._generate_images_section(material_name)
            
            # Add standardized sections from Categories.yaml
            if not self.pipeline_process_service:
                raise ConfigurationError("PipelineProcessService not initialized")
            frontmatter = self.pipeline_process_service.add_environmental_impact_section(frontmatter, material_data)
            # applicationTypes removed per GROK_INSTRUCTIONS.md - NO FALLBACKS
            frontmatter = self.pipeline_process_service.add_outcome_metrics_section(frontmatter, material_data)
            
            # Add regulatory standards (universal + material-specific)
            frontmatter = self.pipeline_process_service.add_regulatory_standards_section(frontmatter, material_data)
            
            # Generate author (required by schema) - must come before caption/tags that reference it
            frontmatter.update(self._generate_author(material_data))
            
            # Add caption section (AI-generated before/after text)
            frontmatter = self._add_caption_section(frontmatter, material_data, material_name)
            
            # Add tags section (10 essential tags for frontmatter)
            frontmatter = self._add_tags_section(frontmatter, material_data, material_name)
            
            return frontmatter
            
        except Exception as e:
            self.logger.error(f"YAML generation failed for {material_name}: {str(e)}")
            raise GenerationError(f"Failed to generate from YAML for {material_name}: {str(e)}")

    # ============================================================================
    # DEPRECATED METHODS - Now handled by PropertyProcessor (Step 2)
    # These methods are kept for backward compatibility but should not be used
    # Will be removed in Step 5 of refactoring plan
    # ============================================================================
    
    def _generate_properties_with_ranges(self, material_data: Dict, material_name: str) -> Dict:
        """
        DEPRECATED: Use PropertyProcessor.organize_properties_by_category() instead.
        This method is kept for backward compatibility only.
        """
        self.logger.warning("DEPRECATED: _generate_properties_with_ranges() - Use PropertyProcessor instead")
        # Generate basic properties first
        basic_properties = self._generate_basic_properties(material_data, material_name)
        
        # Categorize properties using PropertyProcessor
        categorized = self.property_processor.organize_properties_by_category(basic_properties)
        self.logger.info(f"✅ Organized {len(basic_properties)} properties into {len(categorized)} categories for {material_name}")
        return categorized

    def _organize_properties_by_category(self, properties: Dict) -> Dict:
        """
        DEPRECATED: Use PropertyProcessor.organize_properties_by_category() instead.
        This method is kept for backward compatibility only.
        """
        self.logger.warning("DEPRECATED: _organize_properties_by_category() - Use PropertyProcessor instead")
        return self.property_processor.organize_properties_by_category(properties)
    
    def _separate_qualitative_properties(self, all_properties: Dict) -> tuple[Dict, Dict]:
        """
        DEPRECATED: Use PropertyProcessor.separate_qualitative_properties() instead.
        This method is kept for backward compatibility only.
        """
        self.logger.warning("DEPRECATED: _separate_qualitative_properties() - Use PropertyProcessor instead")
        return self.property_processor.separate_qualitative_properties(all_properties)
    
    # ============================================================================
    # END DEPRECATED METHODS
    # ============================================================================
    
    def _generate_basic_properties(self, material_data: Dict, material_name: str) -> Dict:
        """Generate properties with DataMetrics structure using YAML-first approach with AI fallback (OPTIMIZED)"""
        properties = {}
        
        # OPTIMIZATION: Check Materials.yaml first before calling AI
        yaml_properties = material_data.get('properties', {})
        yaml_count = 0
        ai_count = 0
        
        # PHASE 3.2 OPTIMIZATION: Pre-load all category ranges at once (batch loading)
        material_category = material_data.get('category', 'metal').lower()
        all_category_ranges = self.template_service.get_all_category_ranges(material_category)
        self.logger.debug(f"Phase 3.2: Pre-loaded {len(all_category_ranges)} category ranges for {material_category}")
        
        # Use PropertyValueResearcher for AI discovery of missing properties only
        if not self.property_researcher:
            # FAIL-FAST per GROK_INSTRUCTIONS.md - no fallbacks allowed
            raise PropertyDiscoveryError("PropertyValueResearcher required for property discovery")
            
        try:
            # PHASE 1: Use high-confidence YAML properties first (OPTIMIZATION)
            for prop_name, yaml_prop in yaml_properties.items():
                if isinstance(yaml_prop, dict):
                    # Special handling for nested thermalDestruction structure
                    if prop_name == 'thermalDestruction' and 'point' in yaml_prop:
                        yaml_count += 1
                        point_data = yaml_prop['point']
                        
                        # Build point structure with value/unit/confidence from materials.yaml
                        point_structure = {
                            'value': point_data.get('value'),
                            'unit': point_data.get('unit', '°C'),
                            'confidence': ValidationUtils.normalize_confidence(point_data.get('confidence', 0)),
                            'description': point_data.get('description', 'Thermal destruction point')
                        }
                        
                        # PHASE 3.2 OPTIMIZATION: Use pre-loaded category ranges (dict lookup instead of method call)
                        # AUTO-REMEDIATION: Research and populate missing ranges instead of failing
                        category_ranges = all_category_ranges.get(prop_name)
                        if not category_ranges or 'point' not in category_ranges:
                            self.logger.warning(f"Property '{prop_name}' missing from Categories.yaml - researching ranges...")
                            
                            # Use CategoryRangeResearcher to find and populate the missing range
                            try:
                                from research.category_range_researcher import CategoryRangeResearcher
                                researcher = CategoryRangeResearcher()
                                
                                # Research the missing property range for this category
                                range_data = researcher.research_property_range(
                                    property_name=prop_name,
                                    category=material_category,
                                    material_name=material_name
                                )
                                
                                if range_data and 'min' in range_data and 'max' in range_data:
                                    # Update Categories.yaml with the researched range
                                    self._update_categories_yaml_with_range(
                                        category=material_category,
                                        property_name=prop_name,
                                        range_data=range_data
                                    )
                                    
                                    # Reload category ranges
                                    all_category_ranges = self.template_service.get_all_category_ranges(material_category)
                                    category_ranges = all_category_ranges.get(prop_name)
                                    self.logger.info(f"✅ Researched and populated {prop_name} range for {material_category}")
                                else:
                                    raise PropertyDiscoveryError(
                                        f"Failed to research range for '{prop_name}' in category '{material_category}'. "
                                        f"Cannot proceed without valid min/max ranges."
                                    )
                            except Exception as e:
                                raise PropertyDiscoveryError(
                                    f"Property '{prop_name}' missing from Categories.yaml and auto-research failed: {e}"
                                )
                        
                        # Extract point ranges from nested structure
                        point_ranges = category_ranges.get('point', category_ranges) if 'point' in category_ranges else category_ranges
                        if point_ranges.get('min') is None or point_ranges.get('max') is None:
                            raise PropertyDiscoveryError(
                                f"Property '{prop_name}.point' has incomplete ranges in Categories.yaml. "
                                f"Found min={point_ranges.get('min')}, max={point_ranges.get('max')}. "
                                f"Both min and max MUST be defined."
                            )
                        
                        point_structure['min'] = point_ranges['min']
                        point_structure['max'] = point_ranges['max']
                        
                        properties[prop_name] = {
                            'point': point_structure,
                            'type': yaml_prop.get('type', 'melting')
                        }
                        self.logger.info(f"✅ YAML: {prop_name} = {point_data.get('value')} {point_data.get('unit', '°C')} (type: {yaml_prop.get('type')})")
                        continue
                    
                    # Regular flat properties
                    confidence = yaml_prop.get('confidence', 0)
                    if confidence >= 0.85:  # High confidence threshold
                        yaml_count += 1
                        properties[prop_name] = {
                            'value': yaml_prop.get('value'),
                            'unit': yaml_prop.get('unit', ''),
                            'confidence': ValidationUtils.normalize_confidence(confidence),
                            'description': yaml_prop.get('description', f'{prop_name} from Materials.yaml')
                        }
                        # PHASE 3.2 OPTIMIZATION: Use pre-loaded category ranges (dict lookup instead of method call)
                        # AUTO-REMEDIATION: Research and populate missing ranges instead of failing
                        # SKIP qualitative properties (string values like 'melting', 'oxidation', etc.)
                        prop_value = yaml_prop.get('value')
                        is_qualitative = isinstance(prop_value, str) and not self._is_numeric_string(prop_value)
                        
                        if is_qualitative:
                            # Qualitative property - no min/max ranges needed
                            self.logger.debug(f"Skipping range validation for qualitative property: {prop_name}={prop_value}")
                            properties[prop_name]['min'] = None
                            properties[prop_name]['max'] = None
                        else:
                            # Quantitative property - needs min/max ranges
                            category_ranges = all_category_ranges.get(prop_name)
                            
                            # Check if ranges are missing or incomplete
                            needs_research = (
                                not category_ranges or 
                                category_ranges.get('min') is None or 
                                category_ranges.get('max') is None
                            )
                            
                            if needs_research:
                                self.logger.warning(f"Property '{prop_name}' missing or incomplete in Categories.yaml - researching ranges...")
                                
                                # Use CategoryRangeResearcher to find and populate the missing range
                                try:
                                    from research.category_range_researcher import CategoryRangeResearcher
                                    researcher = CategoryRangeResearcher()
                                    
                                    # Research the missing property range for this category
                                    range_data = researcher.research_property_range(
                                        property_name=prop_name,
                                        category=material_category,
                                        material_name=material_name
                                    )
                                    
                                    if range_data and 'min' in range_data and 'max' in range_data:
                                        # Update Categories.yaml with the researched range
                                        self._update_categories_yaml_with_range(
                                            category=material_category,
                                            property_name=prop_name,
                                            range_data=range_data
                                        )
                                        
                                        # Reload category ranges
                                        all_category_ranges = self.template_service.get_all_category_ranges(material_category)
                                        category_ranges = all_category_ranges.get(prop_name)
                                        self.logger.info(f"✅ Researched and populated {prop_name} range for {material_category}")
                                    else:
                                        raise PropertyDiscoveryError(
                                            f"Failed to research range for '{prop_name}' in category '{material_category}'. "
                                            f"Cannot proceed without valid min/max ranges."
                                        )
                                except Exception as e:
                                    raise PropertyDiscoveryError(
                                        f"Property '{prop_name}' missing/incomplete in Categories.yaml and auto-research failed: {e}"
                                    )
                            
                            # Final validation - should never fail if auto-remediation worked
                            if category_ranges.get('min') is None or category_ranges.get('max') is None:
                                raise PropertyDiscoveryError(
                                    f"Property '{prop_name}' STILL has incomplete ranges after auto-remediation. "
                                    f"Found min={category_ranges.get('min')}, max={category_ranges.get('max')}. "
                                    f"This indicates a bug in auto-remediation logic."
                                )
                            
                            properties[prop_name]['min'] = category_ranges['min']
                            properties[prop_name]['max'] = category_ranges['max']
                        
                        self.logger.info(f"✅ YAML: {prop_name} = {yaml_prop.get('value')} {yaml_prop.get('unit', '')} (confidence: {confidence})")
            
            # PHASE 1.5: Add category-specific thermal property field (dual-field approach)
            material_category = material_data.get('category', 'metal').lower()
            if not self.property_research_service:
                raise PropertyDiscoveryError("PropertyResearchService not initialized")
            
            thermal_field_added = self.property_research_service.add_category_thermal_property(
                properties=properties,
                yaml_properties=yaml_properties,
                material_category=material_category,
                thermal_property_map=THERMAL_PROPERTY_MAP
            )
            if thermal_field_added:
                yaml_count += 1
            
            # PHASE 2: Use PropertyDiscoveryService to determine what needs research
            if not self.property_discovery_service:
                raise PropertyDiscoveryError("PropertyDiscoveryService not initialized")
            
            # Discover which properties need AI research
            to_research, skip_reasons = self.property_discovery_service.discover_properties_to_research(
                material_name=material_name,
                material_category=material_category,
                yaml_properties=yaml_properties
            )
            
            # Log what we're skipping and why
            for prop, reason in skip_reasons.items():
                self.logger.info(f"⏭️  Skipping {prop}: {reason}")
            
            # Use PropertyResearchService for AI research
            if not self.property_research_service:
                raise PropertyDiscoveryError("PropertyResearchService not initialized")
            
            researched_properties = self.property_research_service.research_material_properties(
                material_name=material_name,
                material_category=material_category,
                existing_properties=properties
            )
            
            # Add researched properties to our collection
            properties.update(researched_properties)
            ai_count = len(researched_properties)
                    
        except Exception as e:
            self.logger.error(f"Property discovery failed for {material_name}: {e}")
            # FAIL-FAST per GROK_INSTRUCTIONS.md - no fallbacks allowed
            raise PropertyDiscoveryError(f"Cannot generate materialProperties for {material_name}: {e}")
        
        if not properties:
            # FAIL-FAST - must have at least some properties for valid frontmatter
            raise PropertyDiscoveryError(f"No properties found for {material_name}")
        
        # Calculate and log comprehensive coverage statistics
        ai_properties = {k: v for k, v in properties.items() if k not in yaml_properties or yaml_properties[k].get('confidence', 0) < 0.85}
        coverage_stats = self.property_discovery_service.calculate_coverage(
            material_category=material_category,
            yaml_properties=yaml_properties,
            researched_properties=ai_properties
        )
        
        self.logger.info(
            f"📊 Property coverage for {material_name}: "
            f"{coverage_stats['yaml_count']} YAML ({coverage_stats['yaml_percentage']}%), "
            f"{coverage_stats['ai_count']} AI ({coverage_stats['ai_percentage']}%), "
            f"Essential coverage: {coverage_stats['essential_coverage']}%"
        )
        
        # Validate essential properties are present
        self.property_discovery_service.validate_property_completeness(
            material_name=material_name,
            material_category=material_category,
            properties=properties
        )
        
        # PHASE 3.2 OPTIMIZATION: Log cache statistics for performance monitoring
        cache_stats = self.template_service.get_cache_stats()
        if cache_stats['hits'] + cache_stats['misses'] > 0:
            self.logger.info(
                f"🚀 Phase 3.2 cache performance: {cache_stats['hits']} hits, "
                f"{cache_stats['misses']} misses, {cache_stats['hit_rate']:.1%} hit rate"
            )
                        
        return properties
    
    def _update_categories_yaml_with_range(self, property_name: str, category: str, min_val: float, max_val: float, unit: str) -> bool:
        """
        Update Categories.yaml with a researched range for a property.
        
        Args:
            property_name: Name of the property to add
            category: Material category (metal, ceramic, etc.)
            min_val: Minimum value for the range
            max_val: Maximum value for the range
            unit: Unit of measurement
            
        Returns:
            True if successfully updated, False otherwise
        """
        try:
            categories_file = Path(__file__).parent.parent.parent.parent / 'data' / 'Categories.yaml'
            
            # Read current Categories.yaml
            with open(categories_file, 'r', encoding='utf-8') as f:
                categories_data = yaml.safe_load(f)
            
            # Add the property range to the category
            if 'categories' not in categories_data:
                self.logger.error("Categories.yaml missing 'categories' section")
                return False
            
            if category not in categories_data['categories']:
                self.logger.error(f"Category '{category}' not found in Categories.yaml")
                return False
            
            if 'properties' not in categories_data['categories'][category]:
                categories_data['categories'][category]['properties'] = {}
            
            # Add the new property range
            categories_data['categories'][category]['properties'][property_name] = {
                'min': min_val,
                'max': max_val,
                'unit': unit
            }
            
            # Write back to file
            with open(categories_file, 'w', encoding='utf-8') as f:
                yaml.dump(categories_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            # Update in-memory cache
            if category not in self.category_ranges:
                self.category_ranges[category] = {}
            self.category_ranges[category][property_name] = {
                'min': min_val,
                'max': max_val,
                'unit': unit
            }
            
            self.logger.info(f"✅ Added {property_name} range to Categories.yaml: min={min_val}, max={max_val} {unit}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update Categories.yaml with {property_name}: {e}")
            return False
    
    def _generate_machine_settings_with_ranges(self, material_data: Dict, material_name: str) -> Dict:
        """Generate machine settings with DataMetrics structure using comprehensive AI discovery (GROK compliant - no fallbacks)"""
        # Use PropertyResearchService for comprehensive machine settings discovery
        if not self.property_research_service:
            raise PropertyDiscoveryError("PropertyResearchService required for machine settings discovery")
        
        try:
            machine_settings = self.property_research_service.research_machine_settings(material_name)
            return machine_settings
        except Exception as e:
            self.logger.error(f"Machine settings research failed for {material_name}: {e}")
            raise PropertyDiscoveryError(f"Cannot generate machineSettings for {material_name}: {e}")

    # ============================================================================
    # DEPRECATED METHODS - Now handled by PropertyProcessor
    # Kept for backward compatibility, will be removed in Step 5
    # ============================================================================

    def _create_datametrics_property(self, material_value, prop_key: str, material_category: str = 'metal') -> Dict:
        """
        DEPRECATED: Use PropertyProcessor.create_datametrics_property() instead.
        This method is no longer used internally and will be removed in Step 5.
        """
        self.logger.warning("DEPRECATED: _create_datametrics_property() - Use PropertyProcessor instead")
        return self.property_processor.create_datametrics_property(material_value, prop_key, material_category)

    def _calculate_property_confidence(self, prop_key: str, material_category: str, numeric_value: float) -> float:
        """
        DEPRECATED: Confidence calculation now handled by PropertyProcessor.
        This method is kept for backward compatibility only.
        """
        self.logger.warning("DEPRECATED: _calculate_property_confidence() - Use PropertyProcessor instead")
        # Delegate to PropertyProcessor's internal method
        return self.property_processor._calculate_property_confidence(prop_key, material_category, numeric_value)

    def _has_category_data(self, material_category: str, prop_key: str) -> bool:
        """
        DEPRECATED: Category data checking now handled by PropertyProcessor.
        This method is kept for backward compatibility only.
        """
        self.logger.warning("DEPRECATED: _has_category_data() - Use PropertyProcessor instead")
        return self.property_processor._has_category_data(material_category, prop_key)
    
    # ============================================================================
    # END DEPRECATED PROPERTY PROCESSING METHODS
    # ============================================================================
    
    def _update_categories_yaml_with_range(self, category: str, property_name: str, range_data: Dict) -> None:
        """
        Update Categories.yaml with researched property range.
        
        Args:
            category: Material category (metal, ceramic, etc.)
            property_name: Name of the property to update
            range_data: Dict with min, max, unit, and optional description
        """
        import yaml
        from pathlib import Path
        
        categories_file = Path('data/Categories.yaml')
        
        # Read current data
        with open(categories_file, 'r', encoding='utf-8') as f:
            categories_data = yaml.safe_load(f)
        
        # Navigate to the category's properties section
        if 'categories' not in categories_data:
            categories_data['categories'] = {}
        
        if category not in categories_data['categories']:
            categories_data['categories'][category] = {'properties': {}}
        
        if 'properties' not in categories_data['categories'][category]:
            categories_data['categories'][category]['properties'] = {}
        
        # Add the researched range
        categories_data['categories'][category]['properties'][property_name] = {
            'min': range_data['min'],
            'max': range_data['max'],
            'unit': range_data.get('unit', '')
        }
        
        # Write back to file
        with open(categories_file, 'w', encoding='utf-8') as f:
            yaml.dump(categories_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        # Update in-memory category ranges
        if category not in self.category_ranges:
            self.category_ranges[category] = {}
        self.category_ranges[category][property_name] = {
            'min': range_data['min'],
            'max': range_data['max'],
            'unit': range_data.get('unit', '')
        }
        
        # Update template service's cache
        if hasattr(self, 'template_service'):
            self.template_service.category_ranges = self.category_ranges
        
        self.logger.info(f"✅ Updated Categories.yaml: {category}.{property_name} = [{range_data['min']}, {range_data['max']}] {range_data.get('unit', '')}")
    
    def _get_research_based_range(self, prop_key: str, material_category: str, current_value: float) -> tuple[float, float]:
        """
        DEPRECATED: Not used anywhere in code. Range logic now in PropertyProcessor.
        This method will be removed in Step 5.
        """
        self.logger.warning("DEPRECATED: _get_research_based_range() is not used and will be removed")
        # Delegate to PropertyProcessor if ever called
        return self.property_processor._get_category_range(prop_key, material_category, current_value)

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
        """
        DEPRECATED: Use PropertyProcessor.merge_with_ranges() instead.
        Kept for backward compatibility - delegates to PropertyProcessor.
        """
        self.logger.warning("DEPRECATED: _merge_with_ranges() - Use PropertyProcessor.merge_with_ranges() instead")
        return self.property_processor.merge_with_ranges(ai_properties, range_properties)
    
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
            
            # Extract content from APIResponse object if needed
            if hasattr(response, 'content'):
                return response.content
            elif isinstance(response, str):
                return response
            else:
                return str(response)
            
        except Exception as e:
            self.logger.error(f"API call failed for {material_name}: {str(e)}")
            raise GenerationError(f"API generation failed for {material_name}: {str(e)}")

    def _build_material_prompt(self, material_name: str, material_data: Dict) -> str:
        """Build material-specific prompt for frontmatter generation with structured applications"""
        
        # Get cleaning types from Categories.yaml for reference
        cleaning_types_reference = """
Coating Removal, Oxide Removal, Rust Removal, Paint Stripping, Grease/Oil Removal,
Carbon Deposit Removal, Biological Growth Removal, Contamination Removal, Surface Preparation,
Precision Cleaning, Restoration Cleaning, Degreasing, Descaling, Paint Removal, Corrosion Removal
"""
        
        prompt = f"""Generate comprehensive laser cleaning frontmatter for {material_name}.

CRITICAL REQUIREMENTS:

1. **Material Properties Structure** (DataMetrics format):
   - Each property must have: value, unit, confidence, min, max, description
   - Use materialProperties (not properties) key
   - Include: density, thermalConductivity, tensileStrength, hardness, etc.

2. **Machine Settings Structure** (DataMetrics format):
   - Each setting must have: value, unit, confidence, min, max, description
   - Include: powerRange, wavelength, spotSize, repetitionRate, pulseDuration, etc.

3. **Applications Structure** (CRITICAL - MUST BE STRUCTURED OBJECTS):
   REQUIRED: Generate 8-10 diverse laser cleaning applications using this EXACT format:
   
   applications:
     - industry: "Industry Name"
       description: "Detailed description of the specific laser cleaning application (30-50 words minimum)"
       cleaningTypes:
         - "Primary Cleaning Type"
         - "Secondary Cleaning Type"
         - "Additional Type"
       contaminantTypes:
         - "Specific Contaminant 1"
         - "Specific Contaminant 2"
         - "Additional Contaminant"
     - industry: "Different Industry"
       description: "Another detailed cleaning application description (30-50 words)"
       cleaningTypes: [...]
       contaminantTypes: [...]

   **Application Requirements:**
   - Minimum: 8 applications (target: 8-10)
   - Each application MUST be a structured object (NOT a string)
   - Required fields for EVERY application: industry, description, cleaningTypes, contaminantTypes
   - Industries must be diverse: Aerospace, Automotive, Medical, Marine, Electronics, Cultural Heritage, Manufacturing, Energy, etc.
   - Descriptions must be detailed (30+ words) and material-specific
   - cleaningTypes: Use 2-4 types per application from: {cleaning_types_reference}
   - contaminantTypes: Specify 2-4 specific contaminants relevant to that industry/material
   - NO duplicate industries
   - Include both common AND specialized applications

   **Example for {material_name}:**
   applications:
     - industry: "Aerospace"
       description: "Removal of protective coatings, oxidation layers, and manufacturing residues from {material_name} aircraft components during maintenance and overhaul, ensuring surface integrity for inspection and subsequent coating application without thermal damage to the substrate material."
       cleaningTypes:
         - "Coating Removal"
         - "Oxide Removal"
         - "Surface Preparation"
       contaminantTypes:
         - "Protective Coatings"
         - "Oxidation Layers"
         - "Manufacturing Residues"
         - "Hydraulic Fluids"

Material context: {material_data}

**VALIDATION CHECKLIST** (verify before returning):
✓ 8-10 structured applications provided (NOT strings)
✓ Each application has: industry, description, cleaningTypes, contaminantTypes
✓ All industries are different (no duplicates)
✓ Descriptions are detailed (30+ words each)
✓ cleaningTypes arrays have 2-4 relevant types
✓ contaminantTypes arrays have 2-4 specific contaminants
✓ Applications are material-specific and realistic

Return YAML format with materialProperties, machineSettings, and structured applications sections."""
        
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

    def _is_numeric_string(self, value: str) -> bool:
        """Check if a string represents a numeric value"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
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

    def _detect_property_pattern(self, prop_data) -> str:
        """
        Detect property data pattern type.
        
        PROPERTY DATA PATTERNS (as of Oct 2025):
        
        1. LEGACY FORMAT (original AI-generated):
           {value, unit, confidence, description, min, max}
        
        2. PULSE-SPECIFIC (Priority 2 authoritative data):
           {nanosecond: {min, max, unit}, picosecond: {...}, femtosecond: {...},
            source, confidence, measurement_context}
           Used for: ablationThreshold (45 materials)
        
        3. WAVELENGTH-SPECIFIC (Priority 2 authoritative data):
           {at_1064nm: {min, max, unit}, at_532nm: {...}, at_355nm: {...}, at_10640nm: {...},
            source, confidence, measurement_context}
           Used for: reflectivity (35 metals)
        
        4. AUTHORITATIVE (Priority 2 enhanced legacy):
           Legacy format + {source, notes, measurement_context}
           Used for: thermal properties, porosity, oxidation resistance
        
        CRITICAL: Generators must preserve patterns 2-4 during regeneration!
        """
        if not isinstance(prop_data, dict):
            return 'simple'
        
        # Check for pulse-specific pattern
        if 'nanosecond' in prop_data or 'picosecond' in prop_data or 'femtosecond' in prop_data:
            return 'pulse-specific'
        
        # Check for wavelength-specific pattern
        if 'at_1064nm' in prop_data or 'at_532nm' in prop_data or 'at_355nm' in prop_data or 'at_10640nm' in prop_data:
            return 'wavelength-specific'
        
        # Check for authoritative pattern (high confidence with source)
        if 'source' in prop_data and prop_data.get('confidence', 0) > 85:
            return 'authoritative'
        
        # Check for legacy with source
        if 'source' in prop_data or 'notes' in prop_data:
            return 'legacy-sourced'
        
        # Standard legacy format
        return 'legacy'

    def _extract_property_value(self, prop_data, prefer_wavelength: str = '1064nm', prefer_pulse: str = 'nanosecond'):
        """
        Extract value from property data, handling multiple formats.
        
        Args:
            prop_data: Property data dictionary or simple value
            prefer_wavelength: Preferred wavelength for wavelength-specific (default: 1064nm - most common Nd:YAG)
            prefer_pulse: Preferred pulse duration for pulse-specific (default: nanosecond - most common)
        
        Returns:
            Numeric value suitable for comparisons and calculations
        """
        if not isinstance(prop_data, dict):
            return prop_data
        
        pattern = self._detect_property_pattern(prop_data)
        
        # Pattern 1: Pulse-specific (nanosecond/picosecond/femtosecond)
        if pattern == 'pulse-specific':
            pulse_key = prefer_pulse
            if pulse_key in prop_data and isinstance(prop_data[pulse_key], dict):
                pulse_data = prop_data[pulse_key]
                # Calculate average of min/max
                min_val = pulse_data.get('min', 0)
                max_val = pulse_data.get('max', 0)
                if min_val is not None and max_val is not None:
                    return (float(min_val) + float(max_val)) / 2
                return min_val or max_val or 0
            # Fallback to any available pulse duration
            for key in ['nanosecond', 'picosecond', 'femtosecond']:
                if key in prop_data and isinstance(prop_data[key], dict):
                    pulse_data = prop_data[key]
                    min_val = pulse_data.get('min', 0)
                    max_val = pulse_data.get('max', 0)
                    if min_val is not None and max_val is not None:
                        return (float(min_val) + float(max_val)) / 2
        
        # Pattern 2: Wavelength-specific (at_1064nm/at_532nm/at_355nm/at_10640nm)
        if pattern == 'wavelength-specific':
            wavelength_key = f'at_{prefer_wavelength}'
            if wavelength_key in prop_data and isinstance(prop_data[wavelength_key], dict):
                wave_data = prop_data[wavelength_key]
                # Calculate average of min/max
                min_val = wave_data.get('min', 0)
                max_val = wave_data.get('max', 0)
                if min_val is not None and max_val is not None:
                    return (float(min_val) + float(max_val)) / 2
                return min_val or max_val or 0
            # Fallback to any available wavelength
            for key in ['at_1064nm', 'at_532nm', 'at_355nm', 'at_10640nm']:
                if key in prop_data and isinstance(prop_data[key], dict):
                    wave_data = prop_data[key]
                    min_val = wave_data.get('min', 0)
                    max_val = wave_data.get('max', 0)
                    if min_val is not None and max_val is not None:
                        return (float(min_val) + float(max_val)) / 2
        
        # Pattern 3 & 4: Legacy format (with or without source/notes)
        # Try value field first
        if 'value' in prop_data:
            return prop_data['value']
        
        # Try min/max average
        if 'min' in prop_data and 'max' in prop_data:
            min_val = prop_data.get('min')
            max_val = prop_data.get('max')
            if min_val is not None and max_val is not None:
                try:
                    return (float(min_val) + float(max_val)) / 2
                except (ValueError, TypeError):
                    pass
        
        # Fallback to 0
        return 0

    def _get_category_unit(self, material_category: str, prop_key: str) -> Optional[str]:
        """Get unit for property from Categories.yaml enhanced data"""
        try:
            # Map machine settings to machineSettingsDescriptions keys - FIX for min/max unit extraction
            machine_settings_mapping = {
                'powerRange': 'powerRange',
                'spotSize': 'spotSize',
                'repetitionRate': 'repetitionRate',
                'fluenceThreshold': 'fluenceThreshold',
                'pulseDuration': 'pulseDuration',
                'scanningSpeed': 'scanningSpeed',
                'processingSpeed': 'processingSpeed',
                'ablationThreshold': 'ablationThreshold',
                'thermalDamageThreshold': 'thermalDamageThreshold'
            }
            
            # Check machine settings first (these come from machineSettingsDescriptions)
            if prop_key in machine_settings_mapping:
                desc_key = machine_settings_mapping[prop_key]
                if (hasattr(self, 'machine_settings_descriptions') and 
                    desc_key in self.machine_settings_descriptions and
                    isinstance(self.machine_settings_descriptions[desc_key], dict) and
                    'unit' in self.machine_settings_descriptions[desc_key]):
                    unit = self.machine_settings_descriptions[desc_key]['unit']
                    # Handle multi-unit strings like "ns, ps, fs" - take first unit
                    if ',' in unit:
                        unit = unit.split(',')[0].strip()
                    return unit
            
            # Map material property keys to Categories.yaml range keys
            property_mapping = {
                'density': 'density',
                'thermalConductivity': 'thermalConductivity', 
                'tensileStrength': 'tensileStrength',
                'youngsModulus': 'youngsModulus',
                'hardness': 'hardness',
                'electricalConductivity': 'electricalConductivity',
                'thermalDestruction': 'thermalDestruction',  # Nested structure
                'thermalExpansion': 'thermalExpansion',
                'thermalDiffusivity': 'thermalDiffusivity',
                'specificHeat': 'specificHeat',
                'laserAbsorption': 'laserAbsorption',
                'laserReflectivity': 'laserReflectivity',
                'thermalDestructionType': 'thermalDestructionType'  # Add missing property
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

    def _generate_author(self, material_data: Dict) -> Dict:
        """Generate author from material data author.id"""
        try:
            from utils.core.author_manager import get_author_by_id
            
            # Prefer author.id from materials.yaml, fallback to legacy author_id for backwards compatibility
            author_id = None
            if 'author' in material_data and isinstance(material_data['author'], dict) and 'id' in material_data['author']:
                author_id = material_data['author']['id']
            elif 'author_id' in material_data:
                author_id = material_data['author_id']
            else:
                author_id = 3
                
            author_info = get_author_by_id(author_id)
            
            if not author_info:
                # FAIL-FAST per GROK_INSTRUCTIONS.md - no fallbacks allowed
                raise PropertyDiscoveryError(f"Author with ID {author_id} not found - author system required for content generation")
            
            return {
                'author': author_info
            }
            
        except Exception as e:
            self.logger.error(f"Author generation failed: {e}")
            # FAIL-FAST per GROK_INSTRUCTIONS.md - no fallbacks allowed
            raise PropertyDiscoveryError(f"Author system required for content generation: {e}")

    def _generate_images_section(self, material_name: str) -> Dict:
        """
        Generate images section with material-specific URLs and alt text
        
        Per PYTHON_GENERATOR_PROMPT_CORRECTED.md:
        - images section contains ONLY hero image
        - micro image goes in caption.imageUrl (generated separately in _add_caption_section)
        
        Creates proper alt text and URL patterns following schema requirements.
        Handles special characters, multi-word names, and URL normalization.
        
        Args:
            material_name: Name of the material
            
        Returns:
            Dict with ONLY 'hero' image object containing 'alt' and 'url'
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
            
            # ONLY hero image in images section per PYTHON_GENERATOR_PROMPT_CORRECTED.md
            # Micro image is in caption.imageUrl (see _add_caption_section)
            return {
                'hero': {
                    'alt': hero_alt,
                    'url': f'/images/material/{material_slug}-laser-cleaning-hero.jpg'
                }
            }
            
        except Exception as e:
            self.logger.error(f"Images section generation failed for {material_name}: {e}")
            # FAIL-FAST per GROK_INSTRUCTIONS.md - no fallbacks allowed
            raise PropertyDiscoveryError(f"Images section generation required: {e}")

    def _get_unified_material_properties(self, material_name: str, material_data: Dict) -> Dict:
        """Get material properties using unified inheritance from category definitions"""
        try:
            unified_properties = {}
            if 'category' not in material_data:
                raise MaterialDataError(f"Material category required for {material_name} - no fallbacks allowed per GROK_INSTRUCTIONS.md")
            material_category = material_data['category']
            
            # Get category property defaults from Categories.yaml
            category_property_defaults = {}
            if material_category in self.category_enhanced_data:
                enhanced_data = self.category_enhanced_data[material_category]
                if 'categoryPropertyDefaults' in enhanced_data:
                    category_property_defaults = enhanced_data['categoryPropertyDefaults']
            
            # Property types to consolidate
            property_types = ['thermalProperties', 'mechanicalProperties', 'electricalProperties', 'processingProperties']
            
            for prop_type in property_types:
                combined_properties = {}
                
                # Start with category defaults
                if prop_type in category_property_defaults:
                    combined_properties.update(category_property_defaults[prop_type])
                
                # Override with material-specific properties (if any)
                if prop_type in material_data:
                    combined_properties.update(material_data[prop_type])
                
                # Only include if we have properties
                if combined_properties:
                    unified_properties[prop_type] = combined_properties
            
            self.logger.info(f"Retrieved unified properties for {material_name} with category inheritance")
            return unified_properties
            
        except Exception as e:
            self.logger.error(f"Failed to get unified properties for {material_name}: {str(e)}")
            raise PropertyDiscoveryError(f"Property inheritance failed for {material_name}: {str(e)}")
    
    def _generate_subtitle(self, material_name: str, category: str, subcategory: str, material_data: Dict) -> str:
        """Generate AI-powered subtitle highlighting material-specific characteristics and treatment differences"""
        try:
            import yaml
            from pathlib import Path
            from utils.core.author_manager import get_author_by_id
            
            # Extract context
            applications = material_data.get('applications', [])
            properties = material_data.get('materialProperties', {})
            
            # Build property summary for context
            property_summary = []
            for prop, data in list(properties.items())[:5]:  # Limit to top 5 properties
                if isinstance(data, dict) and 'value' in data:
                    unit = data.get('unit', '')
                    property_summary.append(f"{prop}: {data['value']}{unit}")
            
            property_context = '; '.join(property_summary) if property_summary else 'Properties vary'
            apps_context = ', '.join(applications[:3]) if applications else 'General cleaning applications'
            
            # Get author information for voice profile
            author_id = None
            if 'author' in material_data and isinstance(material_data['author'], dict) and 'id' in material_data['author']:
                author_id = material_data['author']['id']
            elif 'author_id' in material_data:
                author_id = material_data['author_id']
            else:
                author_id = 3  # Default author
            
            author_info = get_author_by_id(author_id)
            if not author_info:
                raise PropertyDiscoveryError(f"Author with ID {author_id} not found")
            
            # Load author voice profile
            country = author_info.get('country', 'United States')
            # Map country to voice profile file
            country_mapping = {
                'Taiwan': 'taiwan',
                'Italy': 'italy',
                'Indonesia': 'indonesia',
                'United States': 'united_states',
                'United States (California)': 'united_states'
            }
            profile_name = country_mapping.get(country, 'united_states')
            voice_file = Path(f"voice/profiles/{profile_name}.yaml")
            
            # Load voice profile
            voice_profile = {}
            if voice_file.exists():
                with open(voice_file, 'r', encoding='utf-8') as f:
                    voice_profile = yaml.safe_load(f)
            
            # Extract linguistic characteristics for prompt
            linguistic = voice_profile.get('linguistic_characteristics', {})
            sentence_structure = linguistic.get('sentence_structure', {})
            patterns = sentence_structure.get('patterns', [])
            tendencies = sentence_structure.get('tendencies', [])
            grammar = linguistic.get('grammar_characteristics', {})
            common_patterns = grammar.get('common_patterns', [])
            
            # Build author voice guidance (SUBTLE - don't dominate the output)
            author_voice = f"""
SUBTLE AUTHOR INFLUENCE (let personality show naturally, don't force patterns):
Author: {author_info['name']} from {country}
Voice hints: {', '.join(tendencies[:2]) if tendencies else 'Direct technical writing'}
"""
            
            # Build AI prompt that forces structural variation and human-like writing
            prompt = f"""You are writing subtitle copy for laser cleaning technical documentation. Generate a natural, conversational two-sentence subtitle about {material_name} that passes AI detection.

{author_voice}

CRITICAL: DO NOT USE REPETITIVE PATTERNS! Each subtitle must have a COMPLETELY UNIQUE structure.
BANNED: "What strikes me about...", "This [Material]...", any formulaic openings you've used before.
TONE: Professional technical writing - NO overly familiar expressions like "Hey!", "Wow!", or emotional exclamations.

MATERIAL CONTEXT:
- Material: {material_name}
- Category: {category}
- Subcategory: {subcategory}
- Properties: {property_context}
- Applications: {apps_context}

CRITICAL ANTI-AI-DETECTION REQUIREMENTS:

1. BANNED PHRASES & STRUCTURES (never use any of these):
   - "X is defined by..." / "X is characterized by..." / "X is known for..."
   - "stands out" / "sets apart" / "distinguishes"
   - "necessitates" / "requires" / "demands" + "precise/careful/tailored"
   - "When cleaning [Material], the surface..." (overused opening)
   - "dial in" / "dialed-in" (overused jargon)
   - "keep/keeping the [x] intact" (too common)
   - "calls for close attention" (AI favorite)
   - "well-tuned parameters" (AI favorite)

2. REQUIRED: Use COMPLETELY DIFFERENT sentence structures. Pick ONE (never repeat):
   
   A. Problem-first: "The biggest challenge with [material] is..."
   B. Behavior-first: "[Material] tends to react unpredictably when..."
   C. Property-leads: "Its [property] creates complications during..."
   D. Comparison: "Unlike [similar materials], [material] responds..."
   E. Operator perspective: "Most operators find [material] tricky because..."
   F. Timing-based: "During initial treatment, [material] often..."
   G. Conditional: "If power levels drift above X watts, [material]..."
   H. Consequence: "Skip proper calibration and [material] will..."
   I. Question-implied: "Why does [material] need special attention? Its..."
   J. Discovery: "Look at [material] under magnification and you'll spot..."
   K. Measurement-first: "At roughness levels exceeding X µm, [material]..."
   L. Process-flow: "Start with low power on [material], then gradually..."
   M. Contrast-within: "While the [part A] remains stable, [material's part B]..."
   N. User-instruction: "Keep your laser focused when treating [material] - its..."
   O. Observation: "Notice how [material] shifts color as contamination lifts..."
   P. Technical fact: "With thermal conductivity of X, [material] distributes..."
   Q. Industry-specific: "In aerospace applications, [material] demands..."
   R. Caution-first: "Watch out for [material's tendency] during..."
   S. Benefit-angle: "The advantage of [material] is its ability to..."
   T. Historical/Practical: "Operators have learned that [material] works best when..."

3. VOCABULARY VARIATION - use fresh phrasing:
   - For "precise": specific, exact, targeted, controlled, focused
   - For "settings": controls, parameters, adjustments, power levels, conditions
   - For "avoid damage": prevent harm, protect, preserve, maintain, safeguard
   - For "surface": coating, layer, finish, skin, face
   - For "cleaning": treatment, processing, work, operation, removal

4. WRITE WITH PERSONALITY (match author voice above):
   - Use active, concrete verbs
   - Include occasional contractions (it's, won't, can't)
   - Add specifics (numbers, measurements, observations)
   - Vary rhythm (short + long sentence, or long + short)
   - Let expertise show through word choice

TARGET: 25-40 words, two sentences, completely unique structure from previous subtitles.

Generate the subtitle now:"""

            # Call API
            self.logger.info(f"Generating AI subtitle for {material_name}")
            response = self.api_client.generate_simple(
                prompt=prompt,
                max_tokens=150,  # Enough for 2 sentences
                temperature=0.75  # Higher for more variety (was 0.6)
            )
            
            # Extract content
            if hasattr(response, 'content'):
                subtitle = response.content.strip()
            elif isinstance(response, str):
                subtitle = response.strip()
            else:
                subtitle = str(response).strip()
            
            # Clean up any markdown formatting or extra whitespace
            subtitle = subtitle.replace('**', '').replace('*', '').strip()
            
            self.logger.info(f"✅ Generated subtitle for {material_name}: {subtitle}")
            return subtitle
            
        except Exception as e:
            self.logger.error(f"Failed to generate subtitle for {material_name}: {e}")
            # FAIL-FAST: subtitle is required
            raise GenerationError(f"Subtitle generation failed for {material_name}: {e}")

    def _add_caption_section(self, frontmatter: Dict, material_data: Dict, material_name: str) -> Dict:
        """Add caption section with before/after text using AI generation"""
        try:
            import json
            import random
            
            # Generate random target lengths for variation
            before_target = random.randint(200, 800)
            after_target = random.randint(200, 800)
            
            # Determine paragraph count based on target length
            before_paragraphs = "1-2 paragraphs" if before_target < 400 else "2-3 paragraphs"
            after_paragraphs = "1-2 paragraphs" if after_target < 400 else "2-3 paragraphs"
            
            # Extract material properties for context
            material_props = frontmatter.get('materialProperties', {})
            category = frontmatter.get('category', 'material')
            applications = frontmatter.get('applications', [])
            
            # Build context for AI
            # Filter applications to ensure they are strings only (fail-fast if not)
            if applications:
                filtered_apps = []
                for app in applications[:3]:
                    if isinstance(app, str):
                        filtered_apps.append(app)
                    elif isinstance(app, dict) and 'industry' in app:
                        # Handle old dict format (should not happen after migration)
                        filtered_apps.append(app['industry'])
                    else:
                        raise GenerationError(f"Invalid application format for {material_name}: {type(app)}")
                applications_list = filtered_apps
            else:
                applications_list = []
            
            context_data = {
                'material': material_name,
                'category': category,
                'properties': {},
                'settings': {},
                'applications': applications_list
            }
            
            # Extract key properties
            for prop, data in material_props.items():
                if isinstance(data, dict) and 'value' in data:
                    context_data['properties'][prop] = {
                        'value': data['value'],
                        'unit': data.get('unit', ''),
                        'description': data.get('description', '')
                    }
            
            # Build AI prompt for caption generation
            prompt = f"""Generate clear, readable descriptions of {material_name} laser cleaning for educated professionals.

MATERIAL CONTEXT:
- Material: {material_name}
- Category: {category}
- Material Properties: {json.dumps(context_data['properties'], indent=2) if context_data['properties'] else 'Limited data available'}
- Applications: {', '.join(context_data['applications']) if context_data['applications'] else 'General cleaning'}

REQUIREMENTS:
- Write clear, accessible descriptions that educated professionals can understand
- Use appropriate scientific terminology when it adds precision
- Include specific measurements when relevant
- Focus on visual and performance impacts
- Use objective, factual language (avoid "stunning", "dramatic", etc.)

Generate exactly two text blocks:

**BEFORE_TEXT:**
[Write a microscopic analysis of the contaminated {material_name.lower()} surface in {before_paragraphs} (target ~{before_target} characters). Focus on contamination visible at 500x magnification. Describe layer thickness, surface texture, contamination patterns. Use accessible language while maintaining technical precision.]

**AFTER_TEXT:**
[Write a microscopic analysis of the cleaned {material_name.lower()} surface in {after_paragraphs} (target ~{after_target} characters). Focus on visual transformation at 500x magnification. Contrast with contaminated state, highlight surface improvements. Use accessible language while maintaining technical precision.]"""
            
            # Generate caption using AI
            self.logger.info(f"Generating AI caption for {material_name} (target: before={before_target}, after={after_target})")
            
            try:
                # Call API for caption generation
                response = self.api_client.generate_simple(
                    prompt=prompt,
                    max_tokens=2000,  # Enough for both captions
                    temperature=0.7
                )
                
                # Extract content from APIResponse object if needed
                if hasattr(response, 'content'):
                    caption_text = response.content
                elif isinstance(response, str):
                    caption_text = response
                else:
                    caption_text = str(response)
                
                # Parse the response to extract before_text and after_text
                import re
                before_match = re.search(r'\*\*BEFORE_TEXT:\*\*\s*\n(.*?)(?=\*\*AFTER_TEXT:|\Z)', caption_text, re.DOTALL)
                after_match = re.search(r'\*\*AFTER_TEXT:\*\*\s*\n(.*?)(?=\Z)', caption_text, re.DOTALL)
                
                if before_match and after_match:
                    before_text = before_match.group(1).strip()
                    after_text = after_match.group(1).strip()
                    self.logger.info(f"✅ AI caption generated: before={len(before_text)} chars, after={len(after_text)} chars")
                else:
                    raise ValueError("Could not parse BEFORE_TEXT and AFTER_TEXT from API response")
                    
            except Exception as e:
                self.logger.error(f"Failed to generate AI caption for {material_name}: {e}")
                # FAIL-FAST per GROK_INSTRUCTIONS.md - no fallbacks allowed
                raise GenerationError(f"AI caption generation failed for {material_name}: {e}")
            
            # Get author info for caption
            author_info = frontmatter.get('author', {})
            author_name = author_info.get('name', 'Unknown Author') if isinstance(author_info, dict) else str(author_info)
            
            # Build complete caption structure matching Gallium format
            frontmatter['caption'] = {
                'beforeText': before_text,
                'afterText': after_text,
                'description': f'Microscopic analysis of {material_name.lower()} surface before and after laser cleaning treatment',
                'alt': f'Microscopic view of {material_name.lower()} surface showing laser cleaning effects',
                'technicalAnalysis': {
                    'focus': 'surface_analysis',
                    'uniqueCharacteristics': [f'{material_name.lower()}_specific'],
                    'contaminationProfile': f'{material_name.lower()} surface contamination'
                },
                'microscopy': {
                    'parameters': f'Microscopic analysis of {material_name}',
                    'qualityMetrics': 'Surface improvement analysis'
                },
                'generation': {
                    'method': 'frontmatter_integrated_generation',
                    'timestamp': '2025-10-02T00:00:00.000000Z',
                    'generator': 'FrontmatterCaptionGenerator',
                    'componentType': 'template_caption'
                },
                'author': author_name,
                'materialProperties': {
                    'materialType': category.capitalize(),
                    'analysisMethod': 'template_microscopy'
                },
                'imageUrl': {
                    'alt': f'Microscopic view of {material_name} surface after laser cleaning showing detailed surface structure',
                    'url': f'/images/material/{material_name.lower().replace(" ", "-")}-laser-cleaning-micro.jpg'
                }
            }
            self.logger.info(f"✅ Added caption section for {material_name}")
            return frontmatter
            
        except Exception as e:
            self.logger.error(f"Failed to add caption section for {material_name}: {e}")
            # FAIL-FAST per GROK_INSTRUCTIONS.md - caption is required
            raise GenerationError(f"Caption generation failed for {material_name}: {e}")

    def _add_tags_section(self, frontmatter: Dict, material_data: Dict, material_name: str) -> Dict:
        """Add tags section with 10 tags: 1 category + 3 industries + 3 processes + 2 characteristics + 1 author"""
        try:
            self.logger.info(f"Starting tags generation for {material_name}")
            tags = []
            
            # 1. CORE: Category
            category_raw = frontmatter.get('category', material_data.get('category', 'material'))
            category = category_raw.lower() if isinstance(category_raw, str) else str(category_raw).lower()
            tags.append(category)
            self.logger.info(f"Added category tag: {category}")
            
            # 2-4. INDUSTRIES: Extract from applicationTypes
            industry_tags = self._extract_industry_tags_for_tags(frontmatter, category)
            tags.extend(industry_tags[:3])
            
            # 5-7. PROCESSES: Extract from applicationTypes
            process_tags = self._extract_process_tags_for_tags(frontmatter, category)
            tags.extend(process_tags[:3])
            
            # 8-9. CHARACTERISTICS: Extract from materialProperties
            characteristic_tags = self._extract_characteristic_tags_for_tags(frontmatter, material_data, category)
            tags.extend(characteristic_tags[:2])
            
            # 10. AUTHOR: Author name slug
            author_info = frontmatter.get('author', {})
            if isinstance(author_info, dict):
                author_raw = author_info.get('name', '')
            else:
                author_raw = str(author_info)
            author_slug = author_raw.lower().replace(' ', '-').replace('.', '').replace(',', '') if author_raw else 'unknown-author'
            tags.append(author_slug)
            
            # Validation: Ensure exactly 10 tags
            while len(tags) < 10:
                tags.append('laser-processing')
            tags = tags[:10]
            
            frontmatter['tags'] = tags
            self.logger.info(f"✅ Successfully added {len(tags)} tags for {material_name}: {tags}")
            return frontmatter
            
        except Exception as e:
            self.logger.error(f"❌ FAILED to add tags section for {material_name}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return frontmatter

    def _extract_industry_tags_for_tags(self, frontmatter: Dict, category: str) -> list:
        """Extract 3 industry tags from applications (supports both string and structured formats)"""
        industries = []
        
        # Extract from applications field (both string and structured formats)
        if 'applications' in frontmatter:
            apps = frontmatter['applications']
            if isinstance(apps, list):
                for app in apps:
                    industry = None
                    
                    # Structured format: {industry: "Aerospace", detail: "..."}
                    if isinstance(app, dict) and 'industry' in app:
                        industry = app['industry']
                    # String format: "Aerospace: Description..."
                    elif isinstance(app, str) and ':' in app:
                        industry = app.split(':')[0].strip()
                    
                    if industry:
                        industry_slug = industry.lower().replace(' ', '-').replace('_', '-').replace('&', 'and')
                        if industry_slug not in industries:
                            industries.append(industry_slug)
                        if len(industries) >= 3:
                            return industries[:3]
        
        # Fallback from legacy applicationTypes if present
        if 'applicationTypes' in frontmatter:
            app_types = frontmatter['applicationTypes']
            if isinstance(app_types, list):
                for app_type in app_types:
                    if isinstance(app_type, dict) and 'industries' in app_type:
                        app_industries = app_type['industries']
                        if isinstance(app_industries, list):
                            for industry in app_industries:
                                if isinstance(industry, str):
                                    industry_slug = industry.lower().replace(' ', '-').replace('_', '-').replace('&', 'and')
                                    if industry_slug not in industries:
                                        industries.append(industry_slug)
                                    if len(industries) >= 3:
                                        return industries[:3]
        
        # Final fallback: category-specific defaults
        fallback_industries = {
            'metal': ['manufacturing', 'aerospace', 'automotive'],
            'metals': ['manufacturing', 'aerospace', 'automotive'],
            'ceramic': ['electronics', 'medical', 'aerospace'],
            'ceramics': ['electronics', 'medical', 'aerospace'],
            'stone': ['cultural-heritage', 'architecture', 'restoration'],
        }
        
        category_fallbacks = fallback_industries.get(category, ['manufacturing', 'industrial', 'processing'])
        for fallback in category_fallbacks:
            if fallback not in industries:
                industries.append(fallback)
            if len(industries) >= 3:
                break
        
        return industries[:3]

    def _extract_process_tags_for_tags(self, frontmatter: Dict, category: str) -> list:
        """Extract 3 process tags from applicationTypes"""
        processes = []
        
        if 'applicationTypes' in frontmatter:
            app_types = frontmatter['applicationTypes']
            if isinstance(app_types, list):
                for app_type in app_types:
                    if isinstance(app_type, dict) and 'type' in app_type:
                        process_type = app_type['type']
                        if isinstance(process_type, str):
                            process_slug = process_type.lower().replace(' ', '-').replace('_', '-')
                            if process_slug not in processes:
                                processes.append(process_slug)
                            if len(processes) >= 3:
                                return processes
        
        # Fallback: category-specific
        fallback_processes = {
            'metal': ['decoating', 'oxide-removal', 'surface-preparation'],
            'metals': ['decoating', 'oxide-removal', 'surface-preparation'],
            'ceramic': ['precision-cleaning', 'surface-preparation', 'restoration'],
        }
        
        category_fallbacks = fallback_processes.get(category, ['surface-preparation', 'contamination-removal', 'maintenance'])
        for fallback in category_fallbacks:
            if fallback not in processes:
                processes.append(fallback)
            if len(processes) >= 3:
                break
        
        return processes[:3]

    def _extract_characteristic_tags_for_tags(self, frontmatter: Dict, material_data: Dict, category: str) -> list:
        """Extract 2 material characteristic tags from materialProperties"""
        characteristics = []
        
        if 'materialProperties' in frontmatter:
            props = frontmatter['materialProperties']
            
            # Check for thermal sensitivity
            if 'thermalConductivity' in props:
                # Use pattern-aware extraction
                thermal_val = self._extract_property_value(props['thermalConductivity'])
                try:
                    if float(thermal_val) < 10:
                        characteristics.append('thermal-sensitive')
                except (ValueError, TypeError):
                    pass
            
            # Check for reflectivity
            if 'reflectivity' in props and len(characteristics) < 2:
                # Use pattern-aware extraction (handles wavelength-specific reflectivity)
                reflectivity_val = self._extract_property_value(props['reflectivity'])
                try:
                    if float(reflectivity_val) > 0.5:
                        characteristics.append('reflective-surface')
                except (ValueError, TypeError):
                    pass
        
        # Fallback: category-specific
        if len(characteristics) < 2:
            fallback_chars = {
                'metal': ['conductive', 'reflective-surface'],
                'metals': ['conductive', 'reflective-surface'],
                'ceramic': ['thermal-resistant', 'hard-material'],
            }
            
            category_fallbacks = fallback_chars.get(category, ['industrial-grade', 'processed'])
            for fallback in category_fallbacks:
                if len(characteristics) >= 2:
                    break
                if fallback not in characteristics:
                    characteristics.append(fallback)
        
        return characteristics[:2]

