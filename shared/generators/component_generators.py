#!/usr/bin/env python3
"""
Component Generators for Z-Beam

This module provides individual component generators that can be used
independently or orchestrated by the dynamic generator.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

# Import GenerationError from centralized validation.errors
from shared.validation.errors import GenerationError

# Import material-aware prompt system
try:
    from material_prompting.core.material_aware_generator import (
        MaterialAwarePromptGenerator,
    )
    from material_prompting.exceptions.handler import MaterialExceptionHandler
    MATERIAL_AWARE_PROMPTS_AVAILABLE = True
except ImportError:
    MATERIAL_AWARE_PROMPTS_AVAILABLE = False
    MaterialAwarePromptGenerator = None
    MaterialExceptionHandler = None

logger = logging.getLogger(__name__)

# Global material-aware prompt system (initialized once)
_material_aware_generator = None
_material_exception_handler = None


def get_material_aware_generator():
    """Get global material-aware prompt generator (lazy initialization)"""
    global _material_aware_generator
    if _material_aware_generator is None and MATERIAL_AWARE_PROMPTS_AVAILABLE:
        try:
            _material_aware_generator = MaterialAwarePromptGenerator()
            logger.info("Initialized global material-aware prompt generator")
        except Exception as e:
            logger.warning(f"Failed to initialize material-aware generator: {e}")
    return _material_aware_generator


def get_material_exception_handler():
    """Get global material exception handler (lazy initialization)"""
    global _material_exception_handler
    if _material_exception_handler is None and MATERIAL_AWARE_PROMPTS_AVAILABLE:
        try:
            _material_exception_handler = MaterialExceptionHandler()
            logger.info("Initialized global material exception handler")
        except Exception as e:
            logger.warning(f"Failed to initialize material exception handler: {e}")
    return _material_exception_handler


@dataclass
class ComponentResult:
    """Result of component generation"""

    component_type: str
    content: str
    success: bool
    error_message: Optional[str] = None
    token_count: Optional[int] = None


class BaseComponentGenerator(ABC):
    """Base class for component generators"""

    def __init__(self, component_type: str):
        # Load API keys using standardized approach
        try:
            # Load config/api_keys.py keys into environment
            import os

            from shared.config.api_keys import API_KEYS
            for key, value in API_KEYS.items():
                if value and not os.getenv(key):
                    os.environ[key] = str(value)
        except ImportError:
            raise RuntimeError(
                "CONFIGURATION ERROR: config/api_keys.py not found. "
                "API keys must be defined in config/api_keys.py with no fallbacks."
            )

        self.component_type = component_type
        self.component_dir = Path("components") / component_type

    @abstractmethod
    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """Generate component content"""
        pass

    def _create_result(
        self, content: str, success: bool = True, error_message: Optional[str] = None
    ) -> ComponentResult:
        """Create a ComponentResult"""
        return ComponentResult(
            component_type=self.component_type,
            content=content,
            success=success,
            error_message=error_message,
        )


class StaticComponentGenerator(BaseComponentGenerator):
    """Base class for static components that don't require API calls"""

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """Generate static component content"""
        try:
            content = self._generate_static_content(
                material_name,
                material_data,
                author_info,
                frontmatter_data,
                schema_fields,
            )
            return self._create_result(content, success=True)
        except Exception as e:
            from shared.utils.ai.loud_errors import component_failure

            component_failure(self.component_type, str(e), material=material_name)
            return self._create_result("", success=False, error_message=str(e))

    @abstractmethod
    def _generate_static_content(
        self,
        material_name: str,
        material_data: Dict,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> str:
        """Generate static content for this component"""
        pass


class APIComponentGenerator(BaseComponentGenerator):
    """Base class for components that require API calls"""

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """Generate API-driven component content"""

        if not api_client:
            return self._create_result(
                "", success=False, error_message="API client required but not provided"
            )

        try:
            # Build the prompt with schema fields
            prompt = self._build_prompt(
                material_name,
                material_data,
                author_info,
                frontmatter_data,
                schema_fields,
            )

            # Generate content using API
            if hasattr(api_client, "generate_for_component"):
                response = api_client.generate_for_component(
                    component_type=self.component_type,
                    material=material_name,
                    prompt_template=prompt,
                )
            elif hasattr(api_client, "generate_simple"):
                response = api_client.generate_simple(prompt)
            else:
                response = api_client.generate(prompt)

            # Handle different response types
            if isinstance(response, str):
                # Direct string response
                content = self._post_process_content(
                    response, material_name, material_data
                )
                logger.info(
                    f"Generated {self.component_type} for {material_name} (direct string response)"
                )
                return self._create_result(content, success=True)
            elif hasattr(response, "success") and response.success:
                # Structured response object
                content = self._post_process_content(
                    response.content, material_name, material_data
                )
                logger.info(
                    f"Generated {self.component_type} for {material_name} ({getattr(response, 'token_count', 0)} tokens)"
                )
                return self._create_result(content, success=True)
            elif hasattr(response, "success"):
                # Failed structured response
                return self._create_result(
                    "",
                    success=False,
                    error_message=f"API generation failed: {getattr(response, 'error', 'Unknown error')}",
                )
            else:
                # Unknown response type, treat as string
                content = self._post_process_content(
                    str(response), material_name, material_data
                )
                logger.info(
                    f"Generated {self.component_type} for {material_name} (unknown response type)"
                )
                return self._create_result(content, success=True)

        except Exception as e:
            from shared.utils.ai.loud_errors import api_failure

            api_failure(self.component_type, str(e), retry_count=None)
            return self._create_result("", success=False, error_message=str(e))

    def _build_prompt(
        self,
        material_name: str,
        material_data: Dict,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> str:
        """Build prompt for this component with material-aware enhancements"""
        
        # Try to use material-aware prompts if available
        material_aware_gen = get_material_aware_generator()
        if material_aware_gen:
            try:
                # Get base prompt for this component type
                base_prompt = self._get_base_component_prompt()
                
                # Generate material-aware prompt
                enhanced_prompt = material_aware_gen.generate_material_aware_prompt(
                    material_name=material_name,
                    component_type=self.component_type,
                    base_prompt=base_prompt,
                    material_data=material_data,
                    author_info=author_info,
                    frontmatter_data=frontmatter_data,
                    schema_fields=schema_fields
                )
                
                logger.debug(f"Using material-aware prompt for {self.component_type} - {material_name}")
                return enhanced_prompt
                
            except Exception as e:
                # FAIL-FAST per GROK_INSTRUCTIONS.md - no fallbacks allowed
                raise ValueError(f"Material-aware prompt generation failed for {self.component_type}: {e}")
    
    def _get_base_component_prompt(self) -> str:
        """Get base prompt template for this component type - override in subclasses"""
        return f"Generate high-quality {self.component_type} content for the specified material. Follow component requirements and maintain consistency with material properties."
    
    def _get_basic_prompt(self, material_name: str, material_data: Dict, 
                         author_info: Optional[Dict] = None, 
                         frontmatter_data: Optional[Dict] = None,
                         schema_fields: Optional[Dict] = None) -> str:
        """Generate basic prompt without material-aware enhancements"""
        return f"Generate {self.component_type} content for {material_name}"

    def _post_process_content(
        self, content: str, material_name: str, material_data: Dict
    ) -> str:
        """Post-process generated content with material-aware validation"""
        
        # Apply material-aware validation if available
        material_aware_gen = get_material_aware_generator()
        if material_aware_gen:
            try:
                validated_content = material_aware_gen.validate_generated_content(
                    content=content,
                    material_name=material_name,
                    component_type=self.component_type,
                    material_data=material_data
                )
                
                if validated_content and validated_content != content:
                    logger.info(f"Applied material-aware validation for {self.component_type} - {material_name}")
                    content = validated_content
                    
            except Exception as e:
                logger.warning(f"Material-aware validation failed for {self.component_type}: {e}")
                # Continue with unvalidated content
        
        # Special handling for frontmatter enhancement
        if self.component_type == "frontmatter":
            try:
                from domains.materials.utils.property_enhancer import (
                    enhance_generated_frontmatter,
                )

                category = material_data.get("category", "")
                content = enhance_generated_frontmatter(content, category)
                logger.info(
                    f"Enhanced frontmatter for {material_name} with property context and percentiles"
                )
            except Exception as e:
                logger.warning(f"Failed to enhance frontmatter: {e}")

        return content


# Specific component generators
# (Author component generator moved to components/author/generator.py)


# Component generator factory

class ComponentGeneratorFactory:
    """Factory for creating component generators - API ONLY"""

    @staticmethod
    def create_generator(component_type: str, ai_detection_service=None, api_client=None):
        """Create appropriate generator for component type"""

        try:
            # Import API generators dynamically
            if component_type == "frontmatter":
                # NOTE: StreamlinedFrontmatterGenerator removed Dec 19, 2025
                from export.core.frontmatter_exporter import (
                    StreamlinedFrontmatterGenerator,
                )

                return StreamlinedFrontmatterGenerator(api_client=api_client)
            elif component_type == "author":
                # Author component was removed - authors come from registry
                raise ValueError(
                    f"Author component type is deprecated. "
                    f"Authors are loaded from data/authors/AuthorRegistry.yaml"
                )
            elif component_type == "micro":
                # Use refactored micro generator (68% code reduction: 928 → 315 lines)
                from materials.micro.core.generator import RefactoredMicroGenerator

                return RefactoredCaptionGenerator()
            elif component_type == "subtitle":
                # Subtitle generator with Author Voice integration (Phase 1)
                from materials.subtitle.generators.generator import (
                    SubtitleComponentGenerator,
                )

                return SubtitleComponentGenerator()
            # Try hybrid components first for known hybrid components
            elif component_type in ["metatags", "jsonld", "propertiestable", "badgesymbol"]:
                # Use logging to show we're trying to use hybrid generators
                logger.info(f"Creating hybrid component generator for {component_type}")
                try:
                    import_paths = [
                        f"components.{component_type}.generator",
                        f"components.{component_type}.generators.generator",
                    ]
                    for module_path in import_paths:
                        try:
                            module = __import__(
                                module_path,
                                fromlist=[f"{component_type.title().replace('s', 'S')}ComponentGenerator"],
                            )
                            generator_class = getattr(
                                module, f"{component_type.title()}ComponentGenerator"
                            )
                            return generator_class()
                        except (ImportError, AttributeError) as e:
                            logger.debug(f"Failed to import from {module_path}: {e}")
                            continue
                except Exception as e:
                    logger.warning(f"Failed to create hybrid generator for {component_type}: {e}")
            else:
                # Try to import from components directory
                # Some components have generator.py directly, others have generators/generator.py
                import_paths = [
                    f"components.{component_type}.generator",
                    f"components.{component_type}.generators.generator",
                ]

                for module_path in import_paths:
                    logger.info(f"Trying to import {module_path}")
                    try:
                        module = __import__(
                            module_path,
                            fromlist=[f"{component_type.title()}ComponentGenerator"],
                        )
                        generator_class = getattr(
                            module, f"{component_type.title()}ComponentGenerator"
                        )
                        logger.info(f"Got generator class: {generator_class}")

                        # Return generator instance
                        return generator_class()
                    except (ImportError, AttributeError) as e:
                        logger.debug(f"Failed to import from {module_path}: {e}")
                        continue

                # If both import paths failed
                from shared.utils.ai.loud_errors import dependency_failure

                dependency_failure(
                    f"{component_type}_generator",
                    f"No generator found for component type: {component_type}",
                    impact="Component generation cannot proceed",
                )
                return None

        except ImportError as e:
            from shared.utils.ai.loud_errors import dependency_failure

            dependency_failure(
                f"{component_type}_generator",
                str(e),
                impact="Component generation cannot proceed",
            )
            return None

    @staticmethod
    def get_available_components():
        """Get list of available component types"""
        # Scan components directory for available components
        components_dir = Path("components")
        available_components = []

        if components_dir.exists():
            for component_dir in components_dir.iterdir():
                if component_dir.is_dir() and component_dir.name != "__pycache__":
                    # Check if it has a generator or prompt file
                    # Some components have generator.py directly, others have generators/generator.py
                    generator_file = component_dir / "generator.py"
                    generators_file = component_dir / "generators" / "generator.py"
                    prompt_file = component_dir / "prompt.yaml"

                    if (
                        generator_file.exists()
                        or generators_file.exists()
                        or prompt_file.exists()
                    ):
                        available_components.append(component_dir.name)

        # Also add known generators from generators directory
        generators_dir = Path("generators")
        if generators_dir.exists():
            for generator_file in generators_dir.glob("*_generator.py"):
                component_name = generator_file.stem.replace("_generator", "")
                # Skip dynamic generator as it's not a component type
                if (
                    component_name != "dynamic"
                    and component_name not in available_components
                ):
                    available_components.append(component_name)

        return sorted(available_components)
