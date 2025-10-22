#!/usr/bin/env python3
"""
Hybrid Component Generator

Base class for components that require both frontmatter data and API access.
Can dynamically switch between static and hybrid modes based on configuration.
"""

import logging
from typing import Dict, Optional

from generators.component_generators import APIComponentGenerator, ComponentResult
from utils.file_ops.frontmatter_loader import load_frontmatter_data
from utils.component_mode import get_component_mode, should_use_api

logger = logging.getLogger(__name__)

class HybridComponentGenerator(APIComponentGenerator):
    """
    Base class for components that need both frontmatter data and API access.
    Provides automatic loading of frontmatter data from files when not provided directly.
    Can dynamically switch between static and hybrid modes based on configuration.
    """

    def __init__(self, component_type: str):
        super().__init__(component_type)
        self.component_info = {
            "name": f"{component_type.title()} Component",
            "description": f"Generates {component_type} using frontmatter data and API",
            "version": "1.0.0",
            "type": "hybrid",
        }

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """
        Generate component content using frontmatter data and optionally API.
        Will automatically load frontmatter data from file if not provided.
        Dynamically switches between static and hybrid modes based on configuration.
        """
        # If no frontmatter data was provided, try to load it from file
        if frontmatter_data is None:
            frontmatter_data = load_frontmatter_data(material_name)
            if not frontmatter_data:
                return ComponentResult(
                    component_type=self.component_type,
                    content="",
                    success=False,
                    error_message="No frontmatter data available",
                )
        
        # Determine the generation mode based on configuration
        component_mode = get_component_mode(self.component_type, api_client)
        logger.info(f"Generating {self.component_type} for {material_name} in {component_mode} mode")
        
        # If configured for static or frontmatter mode, or no API client is available,
        # try to use the _extract_from_frontmatter method if it exists
        if component_mode != "hybrid" and hasattr(self, "_extract_from_frontmatter"):
            try:
                content = self._extract_from_frontmatter(material_name, frontmatter_data)
                logger.info(f"Generated {self.component_type} for {material_name} using static extraction")
                return ComponentResult(
                    component_type=self.component_type,
                    content=content,
                    success=True,
                )
            except Exception as e:
                logger.warning(f"Static extraction failed for {self.component_type}, falling back to API: {e}")
                # Fall back to API if static extraction fails and we're in hybrid mode
                if component_mode == "hybrid" and api_client:
                    pass  # Continue to API generation below
                else:
                    return ComponentResult(
                        component_type=self.component_type,
                        content="",
                        success=False,
                        error_message=f"Static extraction failed: {str(e)}",
                    )

        # For hybrid mode with API client, or if static extraction failed and we're falling back
        if component_mode == "hybrid" and api_client:
            # Call the parent class's generate method with the frontmatter data for API-based generation
            return super().generate(
                material_name=material_name,
                material_data=material_data,
                api_client=api_client,
                author=author,
                frontmatter_data=frontmatter_data,
                schema_fields=schema_fields,
            )
        elif component_mode == "hybrid" and not api_client:
            return ComponentResult(
                component_type=self.component_type,
                content="",
                success=False,
                error_message="Hybrid mode requires API client but none was provided",
            )
        else:
            # This should only happen if we failed to handle a component mode
            return ComponentResult(
                component_type=self.component_type,
                content="",
                success=False,
                error_message=f"Unable to generate content in {component_mode} mode",
            )

    def _build_prompt(
        self,
        material_name: str,
        material_data: Dict,
        author: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> str:
        """
        Build prompt using both material data and frontmatter data.
        Subclasses should override this to construct specific prompts.
        """
        # Default implementation that subclasses should override
        return f"Generate {self.component_type} content for {material_name} using frontmatter data"
        
    def _extract_from_frontmatter(
        self,
        material_name: str,
        frontmatter_data: Dict,
        material_data: Optional[Dict] = None,
    ) -> str:
        """
        Extract component content from frontmatter data without using API.
        This method should be overridden by component classes that support static generation.
        
        Args:
            material_name: Name of the material
            frontmatter_data: Dictionary containing frontmatter data
            material_data: Optional dictionary containing material data
            
        Returns:
            str: Generated content
            
        Raises:
            NotImplementedError: If the component doesn't support static generation
        """
        raise NotImplementedError(
            f"Static generation not implemented for {self.component_type}. "
            "Override _extract_from_frontmatter in your component class to support static mode."
        )
        
    def _enhance_with_api(
        self,
        material_name: str,
        material_data: Dict,
        api_client,
        author: Optional[Dict],
        frontmatter_data: Dict,
        base_content: str,
    ) -> str:
        """
        Enhance statically generated content with API-generated content.
        This method should be overridden by component classes that support hybrid generation.
        
        Args:
            material_name: Name of the material
            material_data: Dictionary containing material data
            api_client: API client to use for generation
            author: Optional dictionary containing author information
            frontmatter_data: Dictionary containing frontmatter data
            base_content: Base content to enhance
            
        Returns:
            str: Enhanced content
            
        Raises:
            NotImplementedError: If the component doesn't support hybrid generation
        """
        # Default implementation just delegates to the API
        # Component classes should override this with more sophisticated logic
        prompt = self._build_prompt(
            material_name, material_data, author, frontmatter_data
        )
        try:
            response = api_client.generate(prompt)
            if response and isinstance(response, str):
                return response
            return base_content
        except Exception as e:
            logger.warning(f"API enhancement failed for {self.component_type}: {e}")
            return base_content
