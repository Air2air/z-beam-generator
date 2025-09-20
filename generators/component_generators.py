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

logger = logging.getLogger(__name__)


@dataclass
class ComponentResult:
    """Result of component generation"""

    component_type: str
    content: str
    success: bool
    error_message: Optional[str] = None
    token_count: Optional[int] = None


class GenerationError(Exception):
    """Raised when content generation fails."""

    pass


class BaseComponentGenerator(ABC):
    """Base class for component generators"""

    def __init__(self, component_type: str):
        # Load API keys using standardized approach
        try:
            # Load config/api_keys.py keys into environment
            from config.api_keys import API_KEYS
            import os
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
            from utils.ai.loud_errors import component_failure

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
            from utils.ai.loud_errors import api_failure

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
        """Build simple prompt for this component"""
        return f"Generate {self.component_type} content for {material_name}"

    def _post_process_content(
        self, content: str, material_name: str, material_data: Dict
    ) -> str:
        """Post-process generated content"""
        # Special handling for frontmatter enhancement
        if self.component_type == "frontmatter":
            try:
                from utils.property_enhancer import enhance_generated_frontmatter

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


class FrontmatterComponentGenerator(BaseComponentGenerator):
    """Base class for components that extract data from frontmatter without API calls"""

    def __init__(self, component_type: str):
        super().__init__(component_type)
        self.component_info = {
            "name": f"{component_type.title()} Component",
            "description": f"Generates {component_type} from frontmatter data",
            "version": "2.0.0",
            "type": "frontmatter_extraction",
        }

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """Generate component from frontmatter data - NO API calls required"""
        try:
            if frontmatter_data is None:
                return ComponentResult(
                    component_type=self.component_type,
                    content="",
                    success=False,
                    error_message="No frontmatter data available",
                )

            content = self._extract_from_frontmatter(material_name, frontmatter_data)
            return ComponentResult(
                component_type=self.component_type, content=content, success=True
            )
        except Exception as e:
            return ComponentResult(
                component_type=self.component_type,
                content="",
                success=False,
                error_message=str(e),
            )

    def _extract_from_frontmatter(
        self, material_name: str, frontmatter_data: Dict
    ) -> str:
        """Override this method in subclasses to implement specific extraction logic"""
        raise NotImplementedError("Subclasses must implement _extract_from_frontmatter")


class ComponentGeneratorFactory:
    """Factory for creating component generators - API ONLY"""

    @staticmethod
    def create_generator(component_type: str, ai_detection_service=None):
        """Create appropriate generator for component type"""

        try:
            # Import API generators dynamically
            if component_type == "frontmatter":
                from frontmatter.management.generator import (
                    FrontmatterComponentGenerator,
                )

                return FrontmatterComponentGenerator()
            elif component_type == "bullets":
                from components.bullets.generator import BulletsComponentGenerator

                return BulletsComponentGenerator()
            elif component_type == "author":
                from components.author.generator import AuthorComponentGenerator

                return AuthorComponentGenerator()
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
                                fromlist=[f"{component_type.title()}ComponentGenerator"],
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

                        # Pass AI detection service to text generator
                        if component_type == "text":
                            return generator_class()
                        else:
                            return generator_class()
                    except (ImportError, AttributeError) as e:
                        logger.debug(f"Failed to import from {module_path}: {e}")
                        continue

                # If both import paths failed
                from utils.ai.loud_errors import dependency_failure

                dependency_failure(
                    f"{component_type}_generator",
                    f"No generator found for component type: {component_type}",
                    impact="Component generation cannot proceed",
                )
                return None

        except ImportError as e:
            from utils.ai.loud_errors import dependency_failure

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
