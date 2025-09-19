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

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """Generate frontmatter using API with modular processing pipeline"""
        try:
            if not api_client:
                from utils.ai.loud_errors import dependency_failure

                dependency_failure(
                    "frontmatter_generator",
                    "API client is required for frontmatter generation",
                )
                logger.error("API client is required for frontmatter generation")
                return ComponentResult(
                    component_type="frontmatter",
                    content="",
                    success=False,
                    error_message="API client not provided",
                )

            # Create template variables
            template_vars = self._create_template_vars(
                material_name,
                material_data,
                author_info,
                frontmatter_data,
                schema_fields,
            )

            # Build API prompt
            prompt = self._build_api_prompt(template_vars, frontmatter_data)

            # Call API
            api_response = api_client.generate_simple(prompt)

            if api_response.success:
                content = api_response.content

                # Process the content with modular enhancement pipeline
                final_content = self._process_and_enhance_content(
                    content, material_name, material_data, api_client
                )

                logger.info(f"Generated frontmatter for {material_name}")
                return ComponentResult(
                    component_type="frontmatter", content=final_content, success=True
                )
            else:
                error_msg = api_response.error or "API call failed"
                from utils.ai.loud_errors import api_failure

                api_failure(
                    "frontmatter_generator",
                    f"API error for frontmatter generation: {error_msg}",
                    retry_count=None,
                )
                logger.error(f"API error for frontmatter generation: {error_msg}")
                return ComponentResult(
                    component_type="frontmatter",
                    content="",
                    success=False,
                    error_message=error_msg,
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

        return {
            "subject": material_name,
            "subject_lowercase": subject_lowercase,
            "subject_slug": subject_slug,
            "exact-material-name": subject_slug,  # Required for template compatibility
            "material_formula": formula,
            "material_symbol": symbol,
            "formula": formula,  # For compatibility with chemical fallback tests
            "symbol": symbol,   # For compatibility with chemical fallback tests
            "material_type": material_data.get("material_type", category),
            "category": category,
            "author_name": author_name,
            "author_object_sex": resolved_author_info.get("sex", "unknown"),
            "author_object_title": resolved_author_info.get("title", "Expert"),
            "author_object_country": resolved_author_info.get("country", "Unknown"),
            "author_object_expertise": resolved_author_info.get("expertise", "Materials Science"),
            "author_object_image": resolved_author_info.get("image"),  # FAIL-FAST: No default image allowed
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
        """Extract formula and symbol with intelligent fallback generation"""
        # Formula extraction with intelligent fallback generation
        formula = None
        if "formula" in material_data and material_data["formula"]:
            formula = material_data["formula"]
        elif (
            "data" in material_data
            and "formula" in material_data["data"]
            and material_data["data"]["formula"]
        ):
            formula = material_data["data"]["formula"]
        
        # Symbol extraction with intelligent fallback generation
        symbol = None
        if "symbol" in material_data and material_data["symbol"]:
            symbol = material_data["symbol"]
        elif (
            "data" in material_data
            and "symbol" in material_data["data"]
            and material_data["data"]["symbol"]
        ):
            symbol = material_data["data"]["symbol"]
        
        # Apply category-specific fallback generation if formula/symbol missing
        if not formula or not symbol:
            try:
                from utils.core.chemical_fallback_generator import ChemicalFallbackGenerator
                
                fallback_generator = ChemicalFallbackGenerator()
                fallback_formula, fallback_symbol = fallback_generator.generate_formula_and_symbol(
                    material_name, category
                )
                
                if not formula and fallback_formula:
                    formula = fallback_formula
                    logger.info(f"Generated fallback formula '{formula}' for {material_name} using category-specific rules")
                
                if not symbol and fallback_symbol:
                    symbol = fallback_symbol
                    logger.info(f"Generated fallback symbol '{symbol}' for {material_name} using category-specific rules")
                    
            except Exception as e:
                logger.warning(f"Failed to generate chemical fallbacks for {material_name}: {e}")
        
        # Final fallback: use formula as symbol if still missing
        if not symbol and formula:
            symbol = formula
            logger.info(f"Using formula '{formula}' as final fallback for missing symbol in {material_name}")
        
        # Log warnings for truly missing data
        if not formula:
            logger.warning(f"No formula available for {material_name} - continuing without formula")
        if not symbol:
            logger.warning(f"No symbol available for {material_name} - continuing without symbol")
        
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
            
            # Build prompt using template engine
            from utils.template_engine import TemplateEngine
            template_engine = TemplateEngine()
            
            # Use base prompt from configuration
            base_prompt = self.prompt_config.get("base_prompt", "Generate frontmatter YAML for {{subject}}")
            
            # Apply template variables
            prompt = template_engine.render(base_prompt, template_vars)
            
            # Add context from frontmatter_data if provided
            if frontmatter_data:
                prompt += f"\n\nAdditional context: {frontmatter_data}"
            
            logger.debug(f"Built API prompt for {template_vars.get('subject', 'unknown material')}")
            return prompt
            
        except Exception as e:
            logger.error(f"Error building API prompt: {e}")
            # Fallback prompt
            return f"Generate comprehensive frontmatter YAML for laser cleaning {template_vars.get('subject', 'material')}"

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
        try:
            import yaml
            
            # Extract and parse YAML content
            yaml_content = ValidationHelpers.extract_yaml_from_content(content)
            frontmatter_data = yaml.safe_load(yaml_content)
            
            if not frontmatter_data:
                logger.warning(f"Failed to parse YAML content for {material_name}")
                return content
            
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
