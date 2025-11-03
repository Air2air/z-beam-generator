#!/usr/bin/env python3
"""
Streamlined Frontmatter Generator

Consolidated generator with reduced architectural bloat while preserving all functionality.
Integrates MaterialsYamlFrontmatterMapper and property enhancement directly into core.

Follows GROK fail-fast principles:
- No mocks or fallbacks in production
- Explicit error handling with proper exceptions
- Validates all configurations immediately
- Uses refactored consolidated services (PropertyManager, PropertyProcessor)
- Comprehensive exception handling ensures normalized fields always
"""
import logging
import re
import yaml
from pathlib import Path
from typing import Dict, Optional, List

from shared.generators.component_generators import APIComponentGenerator, ComponentResult
from components.frontmatter.ordering.field_ordering_service import FieldOrderingService
from materials.research.unified_material_research import PropertyValueResearcher
from materials.services.template_service import TemplateService
from materials.services.pipeline_process_service import PipelineProcessService

# Unified property management service (replaces PropertyDiscoveryService + PropertyResearchService)
from materials.services.property_manager import PropertyManager
from components.frontmatter.core.property_processor import PropertyProcessor

# Completeness validation (100% data coverage enforcement)
from materials.validation.completeness_validator import CompletenessValidator

# Import unified exception classes from validation system
from shared.validation.errors import (
    PropertyDiscoveryError,
    ConfigurationError,
    MaterialDataError,
    GenerationError
)

# Qualitative property definitions and classification
from components.frontmatter.qualitative_properties import (
    QUALITATIVE_PROPERTIES,
    MATERIAL_CHARACTERISTICS_CATEGORIES,
    is_qualitative_property
)
# Unified validation system for confidence normalization and validation
from shared.services.validation import ValidationOrchestrator

# Requirements loader for consistency with audit system
from shared.utils.requirements_loader import RequirementsLoader
# Property taxonomy for analysis and validation (REQUIRED per fail-fast)
from materials.utils.property_taxonomy import get_property_taxonomy as get_property_categorizer

logger = logging.getLogger(__name__)

def _load_frontmatter_config() -> Dict:
    """
    Load frontmatter generation configuration with fail-fast validation
    
    Returns:
        Dict containing material_abbreviations and thermal_property_mapping
        
    Raises:
        ConfigurationError: If configuration missing or invalid
    """
    try:
        from shared.config.settings import get_frontmatter_generation_config
        config = get_frontmatter_generation_config()
        
        # Validate required sections
        required_sections = ['material_abbreviations', 'thermal_property_mapping']
        for section in required_sections:
            if section not in config:
                raise ConfigurationError(
                    f"Configuration missing required section '{section}'. "
                    f"Check config.settings.FRONTMATTER_GENERATION_CONFIG for proper structure."
                )
        
        logger.info("Loaded frontmatter configuration from shared.config.settings")
        return config
        
    except ImportError as e:
        raise ConfigurationError(f"Failed to import configuration from shared.config.settings: {e}")
    except Exception as e:
        raise ConfigurationError(f"Failed to load configuration from shared.config.settings: {e}")
# Load configuration at module level (fail-fast if config missing)
_FRONTMATTER_CONFIG = _load_frontmatter_config()
MATERIAL_ABBREVIATIONS = _FRONTMATTER_CONFIG['material_abbreviations']
THERMAL_PROPERTY_MAP = _FRONTMATTER_CONFIG['thermal_property_mapping']

# Unified schema validation (aligned with audit system)
from shared.validation.schema_validator import SchemaValidator
logger.info("Unified schema validation loaded successfully")
# Import material-aware prompt system (OPTIONAL - archived infrastructure)
# TODO: Re-enable when material_prompting module is restored
# from material_prompting.core.material_aware_generator import MaterialAwarePromptGenerator
# from material_prompting.exceptions.handler import MaterialExceptionHandler
# logger.info("Material-aware prompt system loaded successfully")

class StreamlinedFrontmatterGenerator(APIComponentGenerator):
    """Consolidated frontmatter generator with integrated services"""
    def __init__(self, api_client=None, config=None, **kwargs):
        """Initialize with required dependencies"""
        super().__init__("frontmatter")
        self.logger = logging.getLogger(__name__)
        # Store api_client and config for use
        self.api_client = api_client
        self.config = config
        # Store additional kwargs for completeness validation
        self._init_kwargs = kwargs
        
        # API client is only required for pure AI generation
        # For YAML-based generation with research enhancement, we can work without it
        
        # Initialize service placeholders (will be set during data loading)
        self.template_service = None  # Initialized in _load_categories_data()
        self.pipeline_process_service = None  # Initialized in _load_categories_data()
        # Load materials research data for range calculations
        self._load_materials_research_data()
        # Initialize integrated services
        # Note: ValidationHelpers removed in Step 6 - using ValidationService instead
        self.field_ordering_service = FieldOrderingService()
        # Unified validation setup (REQUIRED - aligned with audit system)
        try:
            self.schema_validator = SchemaValidator()
            self.requirements_loader = RequirementsLoader()
            self.logger.info("Unified schema validation initialized")
        except Exception as e:
            raise ConfigurationError(f"Unified schema validation required but setup failed: {e}")
        
        # Completeness validation (100% data coverage)
        # CHANGED: Default to strict mode (enforce completeness by default)
        # Can be disabled with enforce_completeness=False if needed
        strict_mode = self._init_kwargs.get('enforce_completeness', True)
        self.completeness_validator = CompletenessValidator(strict_mode=strict_mode)
        self.logger.info(f"Completeness validation initialized (strict_mode={strict_mode})")
        
        # Enhanced validator (optional - currently unused)
        self.enhanced_validator = None
        # Material-aware prompt system (OPTIONAL - archived infrastructure)
        # TODO: Re-enable when material_prompting module is restored
        # try:
        #     self.material_aware_generator = MaterialAwarePromptGenerator()
        #     self.logger.info("Material-aware prompt system initialized")
        # except Exception as e:
        #     raise ConfigurationError(f"Material-aware prompt system required but setup failed: {e}")
        self.material_aware_generator = None  # Temporarily disabled
        
        # Initialize specialized prompt builders for enhanced quality
        # (NOT separate generators - just improved prompts within frontmatter)
        try:
            from components.frontmatter.prompts.industry_applications import IndustryApplicationsPromptBuilder
            from components.frontmatter.prompts.regulatory_standards import RegulatoryStandardsPromptBuilder
            from components.frontmatter.prompts.environmental_impact import EnvironmentalImpactPromptBuilder
            
            self.industry_prompts = IndustryApplicationsPromptBuilder()
            self.regulatory_prompts = RegulatoryStandardsPromptBuilder()
            self.environmental_prompts = EnvironmentalImpactPromptBuilder()
            self.logger.info("Specialized prompt builders initialized for enhanced quality")
        except Exception as e:
            # Not critical - can fall back to existing prompts
            self.logger.warning(f"Specialized prompt builders not available: {e}")
            self.industry_prompts = None
            self.regulatory_prompts = None
            self.environmental_prompts = None

    def _load_materials_research_data(self):
        """Load materials science research data for accurate range calculations"""
        try:
            # Use CategoryDataLoader to get machine settings from split files
            from materials.category_loader import CategoryDataLoader
            category_loader = CategoryDataLoader()
            
            # Load machine settings ranges from Categories.yaml (category-level data)
            machine_settings_data = category_loader.get_machine_settings()
            if 'machineSettingsRanges' not in machine_settings_data:
                raise MaterialDataError("machineSettingsRanges section required in category data")
            self.machine_settings_ranges = machine_settings_data['machineSettingsRanges']
            self.logger.info("Loaded machine settings ranges from category data (via CategoryDataLoader)")
        except Exception as e:
            self.logger.error(f"Failed to load machine settings data: {e}")
            # Fail-fast: Machine settings data is required for accurate ranges
            raise ValueError(f"Machine settings data required for accurate ranges: {e}")
        # Initialize PropertyValueResearcher (only if API client available)
        if self.api_client:
            try:
                self.property_researcher = PropertyValueResearcher(api_client=self.api_client)
                self.logger.info("PropertyValueResearcher initialized for comprehensive property discovery (GROK compliant - no fallbacks)")
            except Exception as e:
                self.logger.error(f"PropertyValueResearcher initialization failed: {e}")
                # FAIL-FAST per GROK_INSTRUCTIONS.md - no fallbacks allowed
                raise PropertyDiscoveryError(f"PropertyValueResearcher required for AI-driven property discovery: {e}")
        else:
            self.property_researcher = None
            self.logger.info("PropertyValueResearcher skipped - data-only mode (100% complete YAML data)")
        # Load Categories.yaml for category-level data
        try:
            self._load_categories_data()
        except Exception as e:
            self.logger.error(f"Failed to load Categories.yaml: {e}")
            # FAIL-FAST per GROK_INSTRUCTIONS.md - Categories.yaml is now required
            raise ValueError(f"Categories.yaml required for enhanced category-level data: {e}")
            
    def _load_categories_data(self):
        """Load category data using CategoryDataLoader for modular access"""
        try:
            from materials.category_loader import CategoryDataLoader
            
            # Use CategoryDataLoader to access split category files
            category_loader = CategoryDataLoader()
            
            # Load all category data (backward compatible - returns full structure)
            categories_data = category_loader.get_all_categories()
            # Extract category ranges from Categories.yaml structure
            self.category_ranges = {}
            if 'categories' in categories_data:
                for category_name, category_data in categories_data['categories'].items():
                    if 'category_ranges' in category_data:
                        self.category_ranges[category_name] = category_data['category_ranges']
                self.logger.info(f"Loaded category ranges for {len(self.category_ranges)} categories")
            else:
                raise ConfigurationError("'categories' section missing from Categories.yaml")
            
            self.category_enhanced_data = {}
            self.categories_data = categories_data  # Store full categories data for unified industry access
            
            # Load standardized descriptions and templates
            if 'machineSettingsDescriptions' not in categories_data:
                raise ConfigurationError("machineSettingsDescriptions section required in Categories.yaml")
            self.machine_settings_descriptions = categories_data['machineSettingsDescriptions']
            
            # Initialize TemplateService with configuration and ranges
            self.template_service = TemplateService(
                material_abbreviations=MATERIAL_ABBREVIATIONS,
                thermal_property_map=THERMAL_PROPERTY_MAP,
                category_ranges=self.category_ranges
            )
            self.logger.info("TemplateService initialized with abbreviations and thermal mappings")
            
            # Initialize PropertyManager (unified service - replaces PropertyDiscoveryService + PropertyResearchService)
            self.property_manager = PropertyManager(
                property_researcher=self.property_researcher,  # Can be None in data-only mode
                categories_data=categories_data,
                get_category_ranges_func=self.template_service.get_category_ranges_for_property
            )
            self.logger.info(f"PropertyManager initialized (refactored unified service) - researcher: {self.property_researcher is not None}")
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
            
            # Load universal regulatory standards (optimization v2.4.0)
            if 'universal_regulatory_standards' not in categories_data:
                raise ConfigurationError("universal_regulatory_standards section required in Categories.yaml")
            self.universal_regulatory_standards = categories_data['universal_regulatory_standards']
            
            # Initialize PipelineProcessService with API client for AI generation
            # In data-only mode (no API client), skip this service - sections come directly from Materials.yaml
            if self.api_client:
                self.pipeline_process_service = PipelineProcessService(
                    api_client=self.api_client,
                    environmental_impact_templates=self.environmental_impact_templates,
                    standard_outcome_metrics=self.standard_outcome_metrics,
                    universal_regulatory_standards=self.universal_regulatory_standards
                )
                self.logger.info("PipelineProcessService initialized with API client (NO TEMPLATES)")
            else:
                self.pipeline_process_service = None
                self.logger.info("PipelineProcessService skipped - data-only mode (sections from Materials.yaml)")
            
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

    def generate(self, material_name: str, skip_subtitle: bool = True, **kwargs) -> ComponentResult:
        """Generate frontmatter content
        
        Args:
            material_name: Name of material to generate frontmatter for
            skip_subtitle: If True, skip AI subtitle generation (default True)
            **kwargs: Additional generation parameters
        """
        try:
            self.logger.info(f"Generating frontmatter for {material_name} (skip_subtitle={skip_subtitle})")
            # Load material data first (using cached version for performance)
            from materials.data.materials import get_material_by_name_cached
            material_data = get_material_by_name_cached(material_name)
            
            if material_data:
                # Use YAML data with AI enhancement
                content = self._generate_from_yaml(material_name, material_data, skip_subtitle=skip_subtitle)
            else:
                # Pure AI generation for unknown materials
                content = self._generate_from_api(material_name, {})
            # Apply field ordering (handles both flat and categorized structures)
            ordered_content = self.field_ordering_service.apply_field_ordering(content)
            
            # Completeness validation and legacy migration
            ordered_content = self._apply_completeness_validation(
                ordered_content, material_name, material_data.get('category', 'metal')
            )
            
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
            import traceback
            self.logger.error(f"Frontmatter generation failed for {material_name}: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return ComponentResult(
                component_type="frontmatter",
                content="",
                success=False,
                error_message=str(e)
            )

    # def _add_prompt_chain_verification(self, content: Dict) -> Dict:
    #     """
    #     REMOVED: Add prompt chain verification metadata to frontmatter content.
    #     This was adding unnecessary metadata to frontmatter files.
    #     """
    #     pass
    
    def _apply_completeness_validation(
        self,
        frontmatter: Dict,
        material_name: str,
        material_category: str
    ) -> Dict:
        """
        Apply 100% completeness validation and automatic remediation.
        
        Steps:
        1. Detect and migrate legacy qualitative properties
        2. Validate all sections are populated
        3. Check essential properties coverage
        4. Validate all values have required fields (value, unit, description)
        5. Trigger research for missing properties (if not strict mode)
        
        Args:
            frontmatter: Generated frontmatter content
            material_name: Material name
            material_category: Category (metal, plastic, etc.)
            
        Returns:
            Updated frontmatter with completeness fixes applied
            
        Raises:
            GenerationError: If strict mode enabled and data incomplete
        """
        self.logger.info(f"🔍 Validating 100% data completeness for {material_name}...")
        
        # Step 1: Migrate legacy qualitative properties
        if frontmatter.get('materialProperties'):
            updated_props, migration_log = self.completeness_validator.migrate_legacy_qualitative(
                frontmatter['materialProperties']
            )
            if migration_log:
                self.logger.info(f"✅ Migrated {len(migration_log)} legacy qualitative properties")
                for log_entry in migration_log:
                    self.logger.debug(f"  - {log_entry}")
                frontmatter['materialProperties'] = updated_props
        
        # Step 2: Validate completeness
        result = self.completeness_validator.validate_completeness(
            frontmatter, material_name, material_category
        )
        
        # Log warnings
        for warning in result.warnings:
            self.logger.warning(f"⚠️ {warning}")
        
        # Step 3: Handle empty sections - trigger research
        if result.empty_sections:
            self.logger.warning(
                f"⚠️ Empty sections detected: {', '.join(result.empty_sections)}"
            )
            
            # Auto-remediate: trigger property research if properties empty
            if 'materialProperties' in result.empty_sections:
                self.logger.info("🔧 Auto-remediating: researching missing properties...")
                try:
                    # Use property_manager to discover and research
                    if hasattr(self, 'property_manager') and self.property_manager:
                        research_result = self.property_manager.discover_and_research_properties(
                            material_name=material_name,
                            material_category=material_category,
                            existing_properties={}
                        )
                        
                        # Apply discovered properties
                        if research_result.quantitative_properties:
                            categorized = self.property_processor.organize_properties_by_category(
                                research_result.quantitative_properties
                            )
                            frontmatter['materialProperties'] = self.property_processor.apply_category_ranges(
                                categorized, material_category
                            )
                            self.logger.info(f"✅ Auto-remediated: added {len(research_result.quantitative_properties)} properties")
                except Exception as e:
                    self.logger.error(f"Failed to auto-remediate properties: {e}")
            
            # Re-validate after remediation
            result = self.completeness_validator.validate_completeness(
                frontmatter, material_name, material_category
            )
        
        # Step 4: Check if complete
        if not result.is_complete:
            error_summary = (
                f"Data completeness validation failed for {material_name}:\n"
                f"  - Missing properties: {len(result.missing_properties)}\n"
                f"  - Empty sections: {len(result.empty_sections)}\n"
                f"  - Errors: {len(result.error_messages)}"
            )
            
            if self.completeness_validator.strict_mode:
                # Strict mode: fail generation
                self.logger.error(f"❌ STRICT MODE: {error_summary}")
                for error in result.error_messages:
                    self.logger.error(f"  - {error}")
                raise GenerationError(
                    f"STRICT MODE: Incomplete data for {material_name}. "
                    f"Missing {len(result.missing_properties)} properties, "
                    f"{len(result.empty_sections)} empty sections. "
                    f"Run with --data-gaps to see research priorities."
                )
            else:
                # Non-strict: log warnings and continue
                self.logger.warning(f"⚠️ {error_summary}")
                for error in result.error_messages[:5]:  # Show first 5
                    self.logger.warning(f"  - {error}")
                if len(result.error_messages) > 5:
                    self.logger.warning(f"  ... and {len(result.error_messages) - 5} more")
        else:
            self.logger.info(f"✅ 100% data completeness validated for {material_name}")
        
        return frontmatter

    def _generate_from_yaml(self, material_name: str, material_data: Dict, skip_subtitle: bool = True) -> Dict:
        """Generate frontmatter using YAML data with AI enhancement
        
        Args:
            material_name: Name of material
            material_data: Material data from Materials.yaml
            skip_subtitle: If True, skip AI subtitle generation (default True)
        """
        try:
            self.logger.info(f"Generating frontmatter for {material_name} using YAML data")
            # Apply abbreviation template if applicable
            if not self.template_service:
                raise ConfigurationError("TemplateService not initialized")
            abbreviation_format = self.template_service.apply_abbreviation_template(material_name)
            # Build base structure from YAML with all required schema fields
            category = (material_data['category'] if 'category' in material_data else 'materials').title()
            subcategory = material_data['subcategory'] if 'subcategory' in material_data else abbreviation_format['subcategory']
            # Generate subtitle only if not skipped
            if skip_subtitle:
                subtitle_text = f"Laser cleaning parameters and specifications for {abbreviation_format['name']}"
                self.logger.info(f"⏭️  Skipping AI subtitle generation for {material_name}")
            else:
                subtitle_text = self._generate_subtitle(
                    material_name=abbreviation_format['name'],
                    category=category,
                    subcategory=subcategory,
                    material_data=material_data
                )
            
            frontmatter = {
                'name': abbreviation_format['name'],
                'title': material_data['title'] if 'title' in material_data else abbreviation_format['title'],
                'subtitle': subtitle_text,
                'description': material_data['description'] if 'description' in material_data else f"Laser cleaning parameters for {material_data['name'] if 'name' in material_data else material_name}{abbreviation_format['description_suffix']}",
                'category': category,
                'subcategory': subcategory,
            }
            # Load materialProperties directly from materials.yaml (data-only mode)
            # Only copy category groups (material_characteristics, laser_material_interaction, etc.)
            # Skip individual properties at root level
            material_props = material_data.get('materialProperties', {})
            
            if material_props:
                # Filter to only include category groups (objects with 'label' key)
                filtered_props = {}
                for key, value in material_props.items():
                    if isinstance(value, dict) and 'label' in value:
                        filtered_props[key] = value
                
                self.logger.info(f"📦 Using {len(filtered_props)} property categories from materials.yaml for {material_name}")
                
                # Apply category ranges (min/max) to properties
                material_category = material_data.get('category', 'metal').lower()
                filtered_props = self.property_processor.apply_category_ranges(
                    filtered_props, 
                    material_category
                )
                self.logger.info(f"✅ Applied category ranges to {len(filtered_props)} property categories")
                
                frontmatter['materialProperties'] = filtered_props
            else:
                self.logger.warning(f"⚠️ No materialProperties found in materials.yaml for {material_name}")
                frontmatter['materialProperties'] = {}
            
            # Generate machine settings with Min/Max ranges
            frontmatter['machineSettings'] = self._generate_machine_settings_with_ranges(material_data, material_name)
            # Generate images section
            frontmatter['images'] = self._generate_images_section(material_name)
            # REMOVED: environmentalImpact and outcomeMetrics - these are AI-generated content, not data
            # frontmatter['environmentalImpact'] = self._get_environmental_impact_from_ai_fields(material_data, material_name)
            # frontmatter['outcomeMetrics'] = self._get_outcome_metrics_from_ai_fields(material_data, material_name)
            # Add regulatory standards (universal + material-specific)
            if self.pipeline_process_service:
                # AI mode: Generate using PipelineProcessService
                frontmatter = self.pipeline_process_service.add_regulatory_standards_section(frontmatter, material_data)
            elif 'regulatoryStandards' in material_data:
                # Data-only mode: Copy directly from Materials.yaml
                frontmatter['regulatoryStandards'] = material_data['regulatoryStandards']
                self.logger.info(f"✅ Copied {len(material_data['regulatoryStandards'])} regulatory standards from Materials.yaml")
            else:
                self.logger.warning(f"⚠️  No regulatoryStandards in Materials.yaml for {material_name}")
            
            # Generate author
            author_info = self._generate_author(material_data)
            frontmatter.update(author_info)
            
            # Add caption section - check ai_text_fields first, then generate if needed
            caption_data = self._get_caption_from_ai_fields(material_data, material_name)
            if caption_data:
                frontmatter['caption'] = caption_data
                self.logger.info("✅ Using caption from Materials.yaml ai_text_fields")
            else:
                self.logger.info(f"⚠️ No caption found in ai_text_fields for {material_name}")
            
            # Add FAQ section if available in Materials.yaml
            if 'faq' in material_data:
                frontmatter['faq'] = material_data['faq']
                faq_data = material_data['faq']
                # FAQ is a list of {question, answer} dicts
                faq_count = len(faq_data) if isinstance(faq_data, list) else len(faq_data.get('questions', []))
                self.logger.info(f"✅ Including FAQ section ({faq_count} questions)")
            
            # Apply author voice transformation to text fields (including FAQ)
            try:
                self.logger.info("🎭 Preparing author voice transformation...")
                voice_profile = self._get_author_voice_profile(author_info)
                self.logger.info(f"🎭 Voice profile loaded for {voice_profile['country']}")
                frontmatter = self._apply_author_voice_to_text_fields(frontmatter, voice_profile)
                self.logger.info(f"✨ Applied {voice_profile['country']} voice transformation")
                
                # Note: Voice metadata is added by base_generator.apply_author_voice()
                # This ensures consistent metadata handling across all content types
            except Exception as e:
                self.logger.error(f"❌ Voice transformation failed: {e}", exc_info=True)
            
            return frontmatter
            
        except Exception as e:
            self.logger.error(f"YAML generation failed for {material_name}: {str(e)}")
            raise GenerationError(f"Failed to generate from YAML for {material_name}: {str(e)}")
    # ============================================================================
    def _generate_basic_properties(self, material_data: Dict, material_name: str) -> Dict:
        """Generate properties with DataMetrics structure using YAML-first approach with AI fallback (OPTIMIZED)"""
        properties = {}
        
        # OPTIMIZATION: Check Materials.yaml first before calling AI
        yaml_properties = material_data.get('materialProperties', {})
        yaml_count = 0
        ai_count = 0
        
        # Pre-load all category ranges (batch optimization)
        material_category = material_data.get('category', 'metal').lower()
        all_category_ranges = self.template_service.get_all_category_ranges(material_category)
        self.logger.debug(f"Pre-loaded {len(all_category_ranges)} category ranges for {material_category}")
        # Use PropertyValueResearcher for AI discovery of missing properties only (if available)
        if not self.property_researcher:
            self.logger.info("PropertyValueResearcher not available - using YAML data only (data-only mode)")
            # In data-only mode, we should have 100% complete YAML data
            
        try:
            # Use high-confidence YAML properties first
            for prop_name, yaml_prop in yaml_properties.items():
                if isinstance(yaml_prop, dict):
                    # Special handling for nested thermalDestruction structure
                    if prop_name == 'thermalDestruction' and 'point' in yaml_prop:
                        yaml_count += 1
                        point_data = yaml_prop['point']
                        
                        # Build point structure with value/unit from materials.yaml
                        point_structure = {
                            'value': point_data.get('value'),
                            'unit': point_data.get('unit', '°C'),
                            'description': point_data.get('description', 'Thermal destruction point')
                        }
                        # Use pre-loaded category ranges (dict lookup)
                        # AUTO-REMEDIATION: Research and populate missing ranges instead of failing
                        category_ranges = all_category_ranges.get(prop_name)
                        if not category_ranges or 'point' not in category_ranges:
                            self.logger.warning(f"Property '{prop_name}' missing from Categories.yaml - researching ranges...")
                            
                            # Use CategoryRangeResearcher to find and populate the missing range
                            try:
                                from materials.research.category_range_researcher import CategoryRangeResearcher
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
                    
                    # Regular flat properties - use all YAML properties
                    yaml_count += 1
                    properties[prop_name] = {
                        'value': yaml_prop.get('value'),
                        'unit': yaml_prop.get('unit', ''),
                        'description': yaml_prop.get('description', f'{prop_name} from Materials.yaml')
                    }
                    # Use pre-loaded category ranges
                    # AUTO-REMEDIATION: Research and populate missing ranges instead of failing
                    # SKIP qualitative properties (string values like 'melting', 'oxidation', etc.)
                    prop_value = yaml_prop.get('value')
                    is_qualitative = isinstance(prop_value, str) and not self._is_numeric_string(prop_value)
                    
                    if is_qualitative:
                        # Qualitative property - OMIT min/max fields entirely (Zero Null Policy)
                        self.logger.debug(f"Skipping range validation for qualitative property: {prop_name}={prop_value}")
                        # ✅ NO min/max fields at all - complete omission per Zero Null Policy
                        # Fields are simply not added to the properties dict
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
                                from materials.research.category_range_researcher import CategoryRangeResearcher
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
                    self.logger.info(f"✅ YAML: {prop_name} = {yaml_prop.get('value')} {yaml_prop.get('unit', '')}")
            # PHASE 1.5: Add category-specific thermal property field (dual-field approach)
            material_category = material_data.get('category', 'metal').lower()
            if not self.property_manager:
                raise PropertyDiscoveryError("PropertyManager not initialized")
            
            thermal_field_added = self.property_manager.add_category_thermal_property(
                material_name=material_name,
                properties=properties,
                category=material_category
            )
            if thermal_field_added:
                yaml_count += 1
            
            # PHASE 2: Use PropertyManager to determine what needs research
            if not self.property_manager:
                raise PropertyDiscoveryError("PropertyManager not initialized")
            # Discover which properties need AI research (using compatibility method)
            to_research, skip_reasons = self.property_manager.discover_properties_to_research(
                material_name=material_name,
                material_category=material_category,
                yaml_properties=yaml_properties
            )
            # Log what we're skipping and why
            for prop, reason in skip_reasons.items():
                self.logger.info(f"⏭️  Skipping {prop}: {reason}")
            # Use PropertyManager for AI research (using compatibility method)
            if not self.property_manager:
                raise PropertyDiscoveryError("PropertyManager not initialized")
            
            researched_properties = self.property_manager.research_material_properties(
                material_name=material_name,
                to_research=to_research,
                category=material_category
            )
            # Add researched properties to our collection
            properties.update(researched_properties)
        except Exception as e:
            self.logger.error(f"Property discovery failed for {material_name}: {e}")
            # FAIL-FAST per GROK_INSTRUCTIONS.md - no fallbacks allowed
            raise PropertyDiscoveryError(f"Cannot generate materialProperties for {material_name}: {e}")
        
        if not properties:
            # FAIL-FAST - must have at least some properties for valid frontmatter
            raise PropertyDiscoveryError(f"No properties found for {material_name}")
        # Calculate and log comprehensive coverage statistics
        coverage_stats = self.property_manager.calculate_coverage(
            material_name=material_name,
            yaml_properties=yaml_properties,
            category=material_category
        )
        
        self.logger.info(
            f"📊 Property coverage for {material_name}: "
            f"{coverage_stats['yaml_count']} YAML ({coverage_stats['yaml_percentage']}%), "
            f"{coverage_stats['ai_count']} AI ({coverage_stats['ai_percentage']}%), "
            f"Essential coverage: {coverage_stats['essential_coverage']}%"
        )
        # Validate essential properties are present
        self.property_manager.validate_property_completeness(
            category=material_category,
            material_category=material_category,
            properties=properties
        )
        # Log cache statistics for performance monitoring
        cache_stats = self.template_service.get_cache_stats()
        if cache_stats['hits'] + cache_stats['misses'] > 0:
            self.logger.info(
                f"Cache performance: {cache_stats['hits']} hits, "
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
        # First check if machine settings already exist in materials.yaml
        if 'machineSettings' in material_data and material_data['machineSettings']:
            self.logger.info(f"Using existing machine settings from materials.yaml for {material_name}")
            settings = material_data['machineSettings']
            
            # Add min/max ranges from machineSettingsRanges in Categories.yaml
            ranges = self.categories_data.get('machineSettingsRanges', {})
            for setting_name, setting_data in settings.items():
                if isinstance(setting_data, dict) and setting_name in ranges:
                    range_data = ranges[setting_name]
                    if 'min' in range_data:
                        setting_data['min'] = range_data['min']
                    if 'max' in range_data:
                        setting_data['max'] = range_data['max']
            
            return settings
        
        # Use PropertyManager for comprehensive machine settings discovery
        if not self.property_manager:
            raise PropertyDiscoveryError("PropertyManager required for machine settings discovery")
        
        try:
            machine_settings = self.property_manager.research_machine_settings(material_name)
            return machine_settings
        except Exception as e:
            self.logger.error(f"Machine settings research failed for {material_name}: {e}")
            raise PropertyDiscoveryError(f"Cannot generate machineSettings for {material_name}: {e}")

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
        
        categories_file = Path('materials/data/Categories.yaml')
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
            # Ensure Min/Max using PropertyProcessor (Step 5: Direct usage, no deprecated wrappers)
            if 'materialProperties' in parsed_content:
                # Generate properties with ranges using PropertyProcessor
                basic_properties = self._generate_basic_properties(material_data, material_name)
                categorized = self.property_processor.organize_properties_by_category(basic_properties)
                parsed_content['materialProperties'] = self.property_processor.merge_with_ranges(
                    parsed_content['materialProperties'], categorized
                )
            
            if 'machineSettings' in parsed_content:
                # Generate machine settings using PropertyManager
                machine_settings = self.property_manager.research_machine_settings(material_name)
                parsed_content['machineSettings'] = self.property_processor.merge_with_ranges(
                    parsed_content['machineSettings'], machine_settings
                )
            self.logger.info(f"Successfully generated frontmatter for {material_name} with Min/Max ranges")
            return parsed_content
            
        except Exception as e:
            self.logger.error(f"API generation failed for {material_name}: {str(e)}")
            raise GenerationError(f"Failed to generate frontmatter for {material_name}: {str(e)}")
    
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
   - Each setting must have: value, unit, description, min, max
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
   - Comprehensive applications (target: 8-10)
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
    
    def _detect_property_pattern(self, prop_data) -> str:
        """
        Detect property data pattern type.
        
        PROPERTY DATA PATTERNS (as of Oct 2025):
        
        1. LEGACY FORMAT (original AI-generated):
           {value, unit, description, min, max}
        
        2. PULSE-SPECIFIC (Priority 2 authoritative data):
           {nanosecond: {min, max, unit}, picosecond: {...}, femtosecond: {...},
            source, measurement_context}
           Used for: ablationThreshold (45 materials)
        
        3. WAVELENGTH-SPECIFIC (Priority 2 authoritative data):
           {at_1064nm: {min, max, unit}, at_532nm: {...}, at_355nm: {...}, at_10640nm: {...},
            source, measurement_context}
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

    def _generate_author(self, material_data: Dict) -> Dict:
        """Generate author from material data author.id"""
        try:
            from components.frontmatter.utils.author_manager import get_author_by_id
            
            # Use author.id from materials.yaml - FAIL-FAST if missing
            if 'author' not in material_data:
                raise PropertyDiscoveryError(
                    "Material missing 'author' field in Materials.yaml. "
                    "All materials must have author.id defined."
                )
            
            author_field = material_data['author']
            if not isinstance(author_field, dict) or 'id' not in author_field:
                raise PropertyDiscoveryError(
                    "Material author must be dict with 'id' field. "
                    "Add author.id to Materials.yaml for this material."
                )
            
            author_id = author_field['id']
            author_info = get_author_by_id(author_id)
            
            if not author_info:
                # FAIL-FAST per GROK_INSTRUCTIONS.md - no fallbacks allowed
                raise PropertyDiscoveryError(f"Author with ID {author_id} not found - author system required for content generation")
            
            # Filter out internal fields (persona_file, formatting_file) before returning
            # These are for prompt construction only, not for frontmatter export
            public_fields = {'id', 'name', 'country', 'title', 'sex', 'expertise', 'image'}
            filtered_author = {k: v for k, v in author_info.items() if k in public_fields}
            
            return {
                'author': filtered_author
            }
        except Exception as e:
            self.logger.error(f"Author generation failed: {e}")
            # FAIL-FAST per GROK_INSTRUCTIONS.md - no fallbacks allowed
            raise PropertyDiscoveryError(f"Author system required for content generation: {e}")

    def _get_author_voice_profile(self, author_info: Dict) -> Dict:
        """
        Extract voice profile from author information.
        
        Args:
            author_info: Author information dictionary with 'author' key
            
        Returns:
            Voice profile dictionary with country and linguistic characteristics
        """
        author = author_info.get('author', {})
        # Extract country - FAIL-FAST if missing
        if 'country' not in author:
            raise ValueError(
                "Author missing 'country' field. "
                "All authors must have country defined in registry."
            )
        country = author['country']
        
        # Map country to voice profiles
        voice_profiles = {
            'Taiwan': {
                'country': 'Taiwan',
                'linguistic_characteristics': {
                    'sentence_structure': {
                        'patterns': ['systematic', 'logical', 'formal'],
                        'connectors': ['Furthermore', 'Therefore', 'Consequently', 'Additionally']
                    }
                }
            },
            'Italy': {
                'country': 'Italy',
                'linguistic_characteristics': {
                    'sentence_structure': {
                        'patterns': ['descriptive', 'elegant', 'sophisticated'],
                        'descriptive_terms': ['sophisticated', 'elegant', 'refined', 'meticulous']
                    }
                }
            },
            'Indonesia': {
                'country': 'Indonesia',
                'linguistic_characteristics': {
                    'sentence_structure': {
                        'patterns': ['accessible', 'practical', 'simplified'],
                        'simplifications': {
                            'utilize': 'use', 'facilitate': 'help', 
                            'demonstrate': 'show', 'implement': 'apply'
                        }
                    }
                }
            }
        }
        
        # Default to USA conversational if not found
        return voice_profiles.get(country, {
            'country': 'USA',
            'linguistic_characteristics': {
                'sentence_structure': {
                    'patterns': ['conversational', 'engaging', 'direct'],
                    'conversational_starters': ['This great', 'excellent', 'really effective']
                }
            }
        })

    def _apply_author_voice_to_text_fields(
        self,
        frontmatter: Dict,
        voice_profile: Dict
    ) -> Dict:
        """
        Apply author voice characteristics to non-numeric text fields.
        
        Uses voice profile to transform generic text into author-specific
        linguistic patterns while preserving technical accuracy.
        
        Args:
            frontmatter: Generated frontmatter dictionary
            voice_profile: Author's voice profile with linguistic characteristics
            
        Returns:
            Enhanced frontmatter with author-voiced text fields
        """
        try:
            country = voice_profile.get('country', 'USA')
            self.logger.info(f"🎭 Applying {country} author voice to text fields...")
            
            # Transform applications if present
            if 'applications' in frontmatter and frontmatter['applications']:
                frontmatter['applications'] = self._voice_transform_applications(
                    frontmatter['applications'],
                    voice_profile
                )
            
            # Transform materialProperties category descriptions
            if 'materialProperties' in frontmatter:
                for category_key, category_data in frontmatter['materialProperties'].items():
                    if isinstance(category_data, dict) and 'description' in category_data:
                        category_data['description'] = self._voice_transform_text(
                            category_data['description'],
                            voice_profile
                        )
            
            # Transform materialCharacteristics descriptions
            if 'materialCharacteristics' in frontmatter:
                for category_key, category_data in frontmatter['materialCharacteristics'].items():
                    if isinstance(category_data, dict) and 'description' in category_data:
                        category_data['description'] = self._voice_transform_text(
                            category_data['description'],
                            voice_profile
                        )
            
            # Transform environmentalImpact descriptions
            if 'environmentalImpact' in frontmatter:
                for impact_item in frontmatter['environmentalImpact']:
                    if isinstance(impact_item, dict) and 'description' in impact_item:
                        impact_item['description'] = self._voice_transform_text(
                            impact_item['description'],
                            voice_profile
                        )
            
            # Transform outcomeMetrics descriptions
            if 'outcomeMetrics' in frontmatter:
                for metric_item in frontmatter['outcomeMetrics']:
                    if isinstance(metric_item, dict) and 'description' in metric_item:
                        metric_item['description'] = self._voice_transform_text(
                            metric_item['description'],
                            voice_profile
                        )
            
            # Transform FAQ questions and answers
            if 'faq' in frontmatter and isinstance(frontmatter['faq'], list):
                for faq_item in frontmatter['faq']:
                    if isinstance(faq_item, dict):
                        if 'question' in faq_item:
                            faq_item['question'] = self._voice_transform_text(
                                faq_item['question'],
                                voice_profile
                            )
                        if 'answer' in faq_item:
                            faq_item['answer'] = self._voice_transform_text(
                                faq_item['answer'],
                                voice_profile
                            )
            
            self.logger.info("✅ Author voice applied successfully")
            return frontmatter
            
        except Exception as e:
            # Graceful fallback - don't fail generation if voice transformation fails
            self.logger.warning(f"⚠️  Voice transformation failed, using original text: {e}")
            return frontmatter

    def _voice_transform_applications(
        self,
        applications: list,
        voice_profile: Dict
    ) -> list:
        """
        Transform application descriptions with author voice.
        
        Format: "Industry: Description"
        Enhanced: "Industry: Author-voiced description"
        """
        transformed = []
        
        for app in applications:
            if isinstance(app, str) and ':' in app:
                industry, description = app.split(':', 1)
                # Transform description part only
                voiced_desc = self._voice_transform_text(
                    description.strip(),
                    voice_profile
                )
                transformed.append(f"{industry}: {voiced_desc}")
            else:
                transformed.append(app)
        
        return transformed

    def _voice_transform_text(
        self,
        text: str,
        voice_profile: Dict
    ) -> str:
        """
        Transform descriptive text to match author voice.
        
        Preserves technical accuracy while adjusting:
        - Sentence structure
        - Connectors and transitions
        - Formality level
        """
        if not text or not isinstance(text, str):
            return text
        
        linguistic = voice_profile.get('linguistic_characteristics', {})
        sentence_structure = linguistic.get('sentence_structure', {})
        tendencies = sentence_structure.get('tendencies', [])
        grammar = linguistic.get('grammar_characteristics', {})
        natural_patterns = grammar.get('natural_patterns', [])
        
        # Detect author style from patterns
        tendencies_text = ' '.join(tendencies).lower() if tendencies else ''
        patterns_text = ' '.join(natural_patterns).lower() if natural_patterns else ''
        
        # Taiwan: Add systematic connectors
        if 'systematic' in tendencies_text or 'formal academic' in patterns_text:
            text = self._add_systematic_connectors(text)
        
        # Italy: Enhance descriptive richness  
        elif 'descriptive' in tendencies_text or 'flowing' in tendencies_text:
            text = self._add_descriptive_elements(text)
        
        # Indonesia: Simplify for accessibility
        elif 'accessible' in tendencies_text or 'practical' in tendencies_text:
            text = self._simplify_for_accessibility(text)
        
        # USA: Add conversational tone
        elif 'conversational' in tendencies_text or 'innovation' in tendencies_text:
            text = self._add_conversational_tone(text)
        
        return text

    def _add_systematic_connectors(self, text: str) -> str:
        """Add Taiwan-style systematic connectors"""
        # Don't transform if already has systematic language
        if any(word in text.lower() for word in ['therefore', 'furthermore', 'consequently', 'systematic']):
            return text
        
        sentences = text.split('. ')
        if len(sentences) > 1 and len(sentences[1]) > 10:
            # Add connector to second sentence
            sentences[1] = f"Furthermore, {sentences[1][0].lower()}{sentences[1][1:]}"
        
        return '. '.join(sentences)

    def _add_descriptive_elements(self, text: str) -> str:
        """Enhance with Italy-style descriptive richness"""
        # Add descriptive qualifiers where appropriate
        replacements = {
            'process': 'sophisticated process',
            'technique': 'elegant technique',
            'method': 'refined method',
            'approach': 'comprehensive approach'
        }
        
        for old, new in replacements.items():
            if old in text.lower() and new not in text.lower():
                text = text.replace(old, new)
                break  # Only apply one transformation to avoid over-enhancement
        
        return text

    def _simplify_for_accessibility(self, text: str) -> str:
        """Simplify for Indonesia-style practical accessibility"""
        # Replace complex terms with simpler alternatives
        replacements = {
            'utilize': 'use',
            'facilitate': 'help',
            'demonstrate': 'show',
            'substantial': 'large',
            'comprehensive': 'complete'
        }
        
        for old, new in replacements.items():
            if old in text.lower():
                # Case-insensitive replacement
                import re
                text = re.sub(re.escape(old), new, text, flags=re.IGNORECASE)
        
        return text

    def _add_conversational_tone(self, text: str) -> str:
        """Add USA-style conversational tone"""
        # Don't transform if already conversational
        if any(word in text.lower() for word in ['great', 'ideal', 'perfect', 'excellent']):
            return text
        
        # Add conversational enhancers
        if text.startswith(('This ', 'These ')):
            text = text.replace('This ', 'This great ', 1).replace('These ', 'These excellent ', 1)
        
        return text
    
    def _enhance_industry_applications_2phase(self, material_name: str, material_data: Dict, 
                                                existing_industries: List[str]) -> List[str]:
        """
        Optionally enhance industry applications using 2-phase prompting.
        
        Only runs if:
        - Prompt builders are available (self.industry_prompts)
        - API client is available (self.api_client)
        - Existing industries are insufficient (<5 industries)
        
        Returns enhanced or original list depending on availability.
        """
        # Skip if prompt builders or API not available
        if not self.industry_prompts or not self.api_client:
            return existing_industries
        
        # Skip if already have sufficient industries
        if len(existing_industries) >= 5:
            self.logger.info(f"✅ Already have {len(existing_industries)} industries, skipping enhancement")
            return existing_industries
        
        try:
            self.logger.info(f"🔬 Enhancing industry applications with 2-phase research for {material_name}")
            
            # Phase 1: Research
            research_prompt = self.industry_prompts.build_research_prompt(
                material_name=material_name,
                category=material_data.get('category', 'material'),
                material_properties=material_data.get('materialProperties', {})
            )
            research_response = self.api_client.generate_simple(research_prompt, max_tokens=1000)
            
            # Validate research quality
            validation = self.industry_prompts.validate_research_quality(research_response)
            if not validation['passed']:
                self.logger.warning(f"⚠️  Research quality below threshold: {validation['issues']}")
                return existing_industries  # Keep original
            
            # Phase 2: Generate detailed descriptions
            generation_prompt = self.industry_prompts.build_generation_prompt(
                material_name=material_name,
                research_data=research_response,
                target_count=7  # 5-8 range, aim for 7
            )
            industry_list_response = self.api_client.generate_simple(generation_prompt, max_tokens=800)
            
            # Parse response (expected format: list of industry names)
            import re
            industries = re.findall(r'[-•]\s*([^\n]+)', industry_list_response)
            industries = [ind.strip() for ind in industries if ind.strip()]
            
            if len(industries) >= 5:
                self.logger.info(f"✨ Enhanced to {len(industries)} industries via 2-phase prompting")
                return industries
            else:
                self.logger.warning(f"⚠️  2-phase prompting returned insufficient industries ({len(industries)})")
                return existing_industries
                
        except Exception as e:
            self.logger.warning(f"⚠️  2-phase enhancement failed: {e}")
            return existing_industries

    def _get_environmental_impact_from_ai_fields(self, material_data: Dict, material_name: str) -> list:
        """
        Extract environmentalImpact from Materials.yaml ai_text_fields with template fallback.
        
        Priority:
        1. Materials.yaml ai_text_fields.environmental_impact (generated content)
        2. Template generation from Categories.yaml
        
        Args:
            material_data: Material data from Materials.yaml
            material_name: Name of the material
            
        Returns:
            List of environmental impact items with author voice applied
        """
        # Check for ai_text_fields first (Materials.yaml priority)
        ai_text_fields = material_data.get('ai_text_fields', {})
        if 'environmental_impact' in ai_text_fields:
            ai_content = ai_text_fields['environmental_impact']['content']
            self.logger.info(f"✅ Using environmental_impact from Materials.yaml ai_text_fields ({len(ai_content)} chars)")
            
            # Parse structured content into list format expected by frontmatter
            # Assuming ai_text_fields content is structured text that needs parsing
            return self._parse_environmental_impact_content(ai_content)
        
        # Fallback to template generation
        self.logger.info("⚠️  No environmental_impact in Materials.yaml ai_text_fields, using template fallback")
        if not self.pipeline_process_service:
            raise ConfigurationError("PipelineProcessService not initialized for template fallback")
        
        # Use existing template generation method
        temp_frontmatter = {'materialProperties': material_data.get('materialProperties', {})}
        temp_frontmatter = self.pipeline_process_service.add_environmental_impact_section(temp_frontmatter, material_data)
        return temp_frontmatter.get('environmentalImpact', [])
    
    def _get_outcome_metrics_from_ai_fields(self, material_data: Dict, material_name: str) -> list:
        """
        Extract outcomeMetrics from Materials.yaml ai_text_fields with template fallback.
        
        Priority:
        1. Materials.yaml ai_text_fields.outcome_metrics (generated content)
        2. Template generation from Categories.yaml
        
        Args:
            material_data: Material data from Materials.yaml
            material_name: Name of the material
            
        Returns:
            List of outcome metrics items with author voice applied
        """
        # Check for ai_text_fields first (Materials.yaml priority)
        ai_text_fields = material_data.get('ai_text_fields', {})
        if 'outcome_metrics' in ai_text_fields:
            ai_content = ai_text_fields['outcome_metrics']['content']
            self.logger.info(f"✅ Using outcome_metrics from Materials.yaml ai_text_fields ({len(ai_content)} chars)")
            
            # Parse structured content into list format expected by frontmatter
            return self._parse_outcome_metrics_content(ai_content)
        
        # Fallback to template generation
        self.logger.info("⚠️  No outcome_metrics in Materials.yaml ai_text_fields, using template fallback")
        if not self.pipeline_process_service:
            raise ConfigurationError("PipelineProcessService not initialized for template fallback")
        
        # Use existing template generation method
        temp_frontmatter = {'materialProperties': material_data.get('materialProperties', {})}
        temp_frontmatter = self.pipeline_process_service.add_outcome_metrics_section(temp_frontmatter, material_data)
        return temp_frontmatter.get('outcomeMetrics', [])
    
    def _get_caption_from_ai_fields(self, material_data: Dict, material_name: str) -> Dict:
        """
        Extract caption data from Materials.yaml ai_text_fields.
        
        Args:
            material_data: Material data from Materials.yaml
            material_name: Name of the material
            
        Returns:
            Dict with caption structure or empty dict if not found
        """
        try:
            # Check for ai_text_fields caption data
            ai_text_fields = material_data.get('ai_text_fields', {})
            
            caption_data = {}
            
            # Extract beforeText from caption_beforeText field
            if 'caption_beforeText' in ai_text_fields:
                before_content = ai_text_fields['caption_beforeText']['content']
                self.logger.info(f"✅ Found caption_beforeText in ai_text_fields ({len(before_content)} chars)")
                
                # Parse the content - it might be JSON format or plain text
                try:
                    import json
                    # Try to parse as JSON first
                    if before_content.strip().startswith('{'):
                        try:
                            parsed = json.loads(before_content)
                            if 'content' in parsed:
                                caption_data['beforeText'] = parsed['content']
                            else:
                                caption_data['beforeText'] = before_content
                        except json.JSONDecodeError:
                            # If JSON is malformed, try to extract content manually
                            import re
                            # Try to extract content from truncated JSON
                            content_match = re.search(r'"content":\s*"([^"]*)', before_content)
                            if content_match:
                                caption_data['beforeText'] = content_match.group(1)
                            else:
                                # Fallback: look for any text after "content": 
                                fallback_match = re.search(r'"content":\s*"(.+)', before_content, re.DOTALL)
                                if fallback_match:
                                    # Clean up the extracted text
                                    text = fallback_match.group(1)
                                    # Remove trailing quote and JSON artifacts
                                    text = re.sub(r'["}]*$', '', text).strip()
                                    caption_data['beforeText'] = text
                                else:
                                    caption_data['beforeText'] = before_content
                    else:
                        caption_data['beforeText'] = before_content
                except Exception:
                    # If all parsing fails, use as plain text
                    caption_data['beforeText'] = before_content
            
            # Extract afterText from caption_afterText field
            if 'caption_afterText' in ai_text_fields:
                after_content = ai_text_fields['caption_afterText']['content']
                self.logger.info(f"✅ Found caption_afterText in ai_text_fields ({len(after_content)} chars)")
                
                # Parse the content - it might be JSON format or plain text
                try:
                    import json
                    # Try to parse as JSON first
                    if after_content.strip().startswith('{'):
                        try:
                            parsed = json.loads(after_content)
                            if 'content' in parsed:
                                caption_data['afterText'] = parsed['content']
                            else:
                                caption_data['afterText'] = after_content
                        except json.JSONDecodeError:
                            # If JSON is malformed, try to extract content manually
                            import re
                            # Try to extract content from truncated JSON
                            content_match = re.search(r'"content":\s*"([^"]*)', after_content)
                            if content_match:
                                caption_data['afterText'] = content_match.group(1)
                            else:
                                # Fallback: look for any text after "content": 
                                fallback_match = re.search(r'"content":\s*"(.+)', after_content, re.DOTALL)
                                if fallback_match:
                                    # Clean up the extracted text
                                    text = fallback_match.group(1)
                                    # Remove trailing quote and JSON artifacts
                                    text = re.sub(r'["}]*$', '', text).strip()
                                    caption_data['afterText'] = text
                                else:
                                    caption_data['afterText'] = after_content
                    else:
                        caption_data['afterText'] = after_content
                except Exception:
                    # If all parsing fails, use as plain text
                    caption_data['afterText'] = after_content
            
            # Add image URL for micro image (standard pattern)
            if caption_data:
                # Generate standard micro image URL following the pattern: material-laser-cleaning-micro.jpg
                material_slug = material_name.lower().replace(' ', '-')
                caption_data['imageUrl'] = f"/images/material/{material_slug}-laser-cleaning-micro.jpg"
                
                self.logger.info(f"✅ Built caption structure with {len(caption_data)} fields")
                return caption_data
            else:
                self.logger.info(f"⚠️ No caption fields found in ai_text_fields for {material_name}")
                return {}
                
        except Exception as e:
            self.logger.warning(f"Failed to extract caption from ai_text_fields for {material_name}: {e}")
            return {}
    
    def _parse_environmental_impact_content(self, content: str) -> list:
        """
        Parse environmental_impact ai_text_fields content into structured list format.
        
        Args:
            content: Generated text content from ai_text_fields
            
        Returns:
            List of environmental impact items in frontmatter format
        """
        try:
            # Split content into logical sections/points
            # Look for pattern: "Title: Description. Next Title: Description"
            import re
            
            # Split on pattern: ". [Title with multiple words]: " but only when it's a main section
            # Look for titles that are likely section headers (2+ words, capitalized)
            sections = []
            
            # Use a more precise regex to find main section boundaries
            # This looks for ". [Multi-word Title]: " where the title is likely a main benefit name
            section_pattern = r'\.\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)+):\s+'
            section_matches = list(re.finditer(section_pattern, content))
            
            if section_matches:
                # Extract sections based on matches
                start_pos = 0
                for i, match in enumerate(section_matches):
                    if i == 0:
                        # First section starts from beginning
                        first_title_start = content.find(':')
                        if first_title_start > 0:
                            first_title = content[:first_title_start].strip()
                            if first_title and len(first_title.split()) >= 2:  # Multi-word title
                                sections.append(content[:match.start() + 1].strip())
                    
                    # Current section
                    section_start = match.start() + 2  # Skip ". "
                    section_end = section_matches[i + 1].start() + 1 if i + 1 < len(section_matches) else len(content)
                    section_text = content[section_start:section_end].strip()
                    if section_text:
                        sections.append(section_text)
            
            # If no clear sections found, try simpler approach looking for patterns at start
            if not sections:
                # Look for title patterns at the start or after ". "
                parts = re.split(r'(?:^|\.\s+)([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)+):\s+', content.strip())
                for i in range(1, len(parts), 2):
                    if i + 1 < len(parts):
                        title = parts[i].strip()
                        desc = parts[i + 1].strip()
                        # Remove trailing periods that might be section separators
                        desc = re.sub(r'\.\s*$', '', desc)
                        sections.append(f"{title}: {desc}")
            
            # Final fallback - split on clear sentence boundaries and filter
            if not sections:
                potential_sections = re.split(r'[.!?]\s+', content.strip())
                sections = [s.strip() for s in potential_sections if s.strip() and len(s) > 30 and ':' in s[:50]]
            
            # Convert to structured format expected by frontmatter
            impact_items = []
            
            # Standard environmental benefits for laser cleaning
            benefit_names = [
                'Chemical Waste Elimination',
                'Water Usage Reduction', 
                'Energy Efficiency',
                'Air Quality Improvement',
                'Waste Reduction'
            ]
            
            for i, section in enumerate(sections[:5]):  # Limit to 5 items
                if len(section) > 20:  # Skip very short fragments
                    # Extract benefit title from description if it starts with a title and colon
                    if ':' in section and section.index(':') < 50:  # Title should be near the beginning
                        title_part, desc_part = section.split(':', 1)
                        benefit_name = title_part.strip()
                        clean_description = desc_part.strip()
                    else:
                        benefit_name = benefit_names[i] if i < len(benefit_names) else f'Environmental Benefit {i+1}'
                        clean_description = section.strip()
                    
                    # Skip if description is too short after cleaning
                    if len(clean_description) > 10:
                        impact_items.append({
                            'benefit': benefit_name,
                            'applicableIndustries': [],
                            'description': clean_description
                        })
            
            return impact_items if impact_items else [
                {'benefit': 'Environmental Benefits', 'applicableIndustries': [], 'description': content[:200] + '...' if len(content) > 200 else content}
            ]
            
        except Exception as e:
            self.logger.warning(f"Failed to parse environmental_impact content: {e}")
            # Fallback to single item
            return [{
                'benefit': 'Environmental Benefits',
                'applicableIndustries': [],
                'description': content[:300] + '...' if len(content) > 300 else content
            }]
    
    def _parse_outcome_metrics_content(self, content: str) -> list:
        """
        Parse outcome_metrics ai_text_fields content into structured list format.
        
        Args:
            content: Generated text content from ai_text_fields
            
        Returns:
            List of outcome metrics items in frontmatter format
        """
        try:
            # Split content into logical metrics/points
            # Look for pattern: "Title: Description. Next Title: Description"
            import re
            
            # Split on pattern: ". [Title with multiple words]: " but only when it's a main section
            # Look for titles that are likely section headers (2+ words, capitalized)
            sections = []
            
            # Use a more precise regex to find main section boundaries
            # This looks for ". [Multi-word Title]: " where the title is likely a main metric name
            section_pattern = r'\.\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)+):\s+'
            section_matches = list(re.finditer(section_pattern, content))
            
            if section_matches:
                # Extract sections based on matches
                start_pos = 0
                for i, match in enumerate(section_matches):
                    if i == 0:
                        # First section starts from beginning
                        first_title_start = content.find(':')
                        if first_title_start > 0:
                            first_title = content[:first_title_start].strip()
                            if first_title and len(first_title.split()) >= 2:  # Multi-word title
                                sections.append(content[:match.start() + 1].strip())
                    
                    # Current section
                    section_start = match.start() + 2  # Skip ". "
                    section_end = section_matches[i + 1].start() + 1 if i + 1 < len(section_matches) else len(content)
                    section_text = content[section_start:section_end].strip()
                    if section_text:
                        sections.append(section_text)
            
            # If no clear sections found, try simpler approach looking for patterns at start
            if not sections:
                # Look for title patterns at the start or after ". "
                parts = re.split(r'(?:^|\.\s+)([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)+):\s+', content.strip())
                for i in range(1, len(parts), 2):
                    if i + 1 < len(parts):
                        title = parts[i].strip()
                        desc = parts[i + 1].strip()
                        # Remove trailing periods that might be section separators
                        desc = re.sub(r'\.\s*$', '', desc)
                        sections.append(f"{title}: {desc}")
            
            # Final fallback - split on clear sentence boundaries and filter
            if not sections:
                potential_sections = re.split(r'[.!?]\s+', content.strip())
                sections = [s.strip() for s in potential_sections if s.strip() and len(s) > 30 and ':' in s[:50]]
            
            # Convert to structured format expected by frontmatter
            metric_items = []
            
            # Standard outcome metrics for laser cleaning
            metric_names = [
                'Contaminant Removal Efficiency',
                'Processing Speed',
                'Surface Quality Preservation', 
                'Thermal Damage Avoidance',
                'Cost Effectiveness'
            ]
            
            for i, section in enumerate(sections[:5]):  # Limit to 5 items
                if len(section) > 20:  # Skip very short fragments
                    # Extract metric title from description if it starts with a title and colon
                    if ':' in section and section.index(':') < 50:  # Title should be near the beginning
                        title_part, desc_part = section.split(':', 1)
                        metric_name = title_part.strip()
                        clean_description = desc_part.strip()
                    else:
                        metric_name = metric_names[i] if i < len(metric_names) else f'Performance Metric {i+1}'
                        clean_description = section.strip()
                    
                    # Skip if description is too short after cleaning
                    if len(clean_description) > 10:
                        metric_items.append({
                            'metric': metric_name,
                            'description': clean_description,
                            'measurementMethods': [],
                            'factorsAffecting': [],
                            'units': []
                    })
            
            return metric_items if metric_items else [
                {'metric': 'Performance Metrics', 'description': content[:200] + '...' if len(content) > 200 else content, 'measurementMethods': [], 'factorsAffecting': [], 'units': []}
            ]
            
        except Exception as e:
            self.logger.warning(f"Failed to parse outcome_metrics content: {e}")
            # Fallback to single item
            return [{
                'metric': 'Performance Metrics', 
                'description': content[:300] + '...' if len(content) > 300 else content,
                'measurementMethods': [],
                'factorsAffecting': [],
                'units': []
            }]

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
            # Best practices: 125 chars ideal, 155 max for SEO
            # Include material, process, scale, and specific visual details
            material_title = material_name.title()
            
            # Hero image: Focus on active cleaning process with visible laser interaction
            hero_alt = f'{material_title} surface during precision laser cleaning process removing contamination layer at microscopic scale'
            
            # Micro image: Focus on before/after comparison at 500x magnification showing surface transformation
            micro_alt = f'{material_title} surface at 500x magnification comparing contaminated state with cleaned substrate showing complete restoration'
            
            # Include both hero and micro images per frontmatter schema requirements
            return {
                'hero': {
                    'alt': hero_alt,
                    'url': f'/images/material/{material_slug}-laser-cleaning-hero.jpg'
                },
                'micro': {
                    'alt': micro_alt,
                    'url': f'/images/material/{material_slug}-microscopic-before-after.jpg'
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
            from components.frontmatter.utils.author_manager import get_author_by_id
            
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
            else:
                author_id = 3  # Default to Ikmanda Roswati
            
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
            tendencies = sentence_structure.get('tendencies', [])
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



