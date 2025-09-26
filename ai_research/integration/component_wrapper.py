#!/usr/bin/env python3
"""
Material-Aware Component Wrapper

Wrapper system to add material-aware prompt capabilities to existing component generators
without requiring modification of their core logic. This allows seamless integration
of material-specific exception handling across all components.

Features:
- Transparent integration with existing generators
- Material-specific prompt enhancement 
- Automatic validation and correction
- Fallback to original generator behavior
- Comprehensive error handling
"""

import logging
from typing import Dict, Optional, Any
from generators.component_generators import ComponentResult, APIComponentGenerator

logger = logging.getLogger(__name__)


class MaterialAwareComponentWrapper:
    """
    Wrapper that adds material-aware prompt capabilities to any component generator
    
    This wrapper intercepts generate() calls and enhances them with:
    - Material-specific prompt modifications
    - Category-based field handling (wood vs ceramic vs metal)
    - Automatic validation and correction
    - Seamless fallback to original behavior
    """
    
    def __init__(self, wrapped_generator, component_type: str):
        """
        Initialize wrapper around existing generator
        
        Args:
            wrapped_generator: Original component generator to wrap
            component_type: Type of component (for prompt enhancement)
        """
        self.wrapped_generator = wrapped_generator
        self.component_type = component_type
        
        # Initialize material-aware systems if available
        self.material_aware_generator = None
        self.material_exception_handler = None
        
        try:
            from ai_research.prompt_exceptions.material_aware_generator import MaterialAwarePromptGenerator
            from ai_research.prompt_exceptions.material_exception_handler import MaterialExceptionHandler
            
            self.material_aware_generator = MaterialAwarePromptGenerator()
            self.material_exception_handler = MaterialExceptionHandler()
            logger.info(f"Initialized material-aware wrapper for {component_type}")
            
        except ImportError:
            logger.debug(f"Material-aware prompts not available for {component_type}")
        except Exception as e:
            logger.warning(f"Failed to initialize material-aware systems: {e}")
    
    def generate(self, material_name: str, **kwargs) -> ComponentResult:
        """
        Enhanced generate method with material-aware capabilities
        
        Args:
            material_name: Name of material to generate content for
            **kwargs: Additional arguments passed to wrapped generator
            
        Returns:
            ComponentResult with enhanced content
        """
        
        # If material-aware systems available, enhance the generation process
        if self.material_aware_generator and hasattr(self.wrapped_generator, '_build_prompt'):
            try:
                return self._generate_with_material_awareness(material_name, **kwargs)
            except Exception as e:
                logger.warning(f"Material-aware generation failed, falling back to original: {e}")
                # Fall back to original generator
        
        # Use original generator
        return self.wrapped_generator.generate(material_name, **kwargs)
    
    def _generate_with_material_awareness(self, material_name: str, **kwargs) -> ComponentResult:
        """Generate content with material-aware enhancements"""
        
        # Get material data
        material_data = kwargs.get('material_data', {})
        
        # Check if this is an API generator that we can enhance
        if isinstance(self.wrapped_generator, APIComponentGenerator):
            return self._enhance_api_generation(material_name, **kwargs)
        else:
            # For non-API generators, apply post-generation validation
            result = self.wrapped_generator.generate(material_name, **kwargs)
            
            if result.success and result.content:
                try:
                    validated_content = self.material_aware_generator.validate_generated_content(
                        content=result.content,
                        material_name=material_name,
                        component_type=self.component_type,
                        material_data=material_data
                    )
                    
                    if validated_content and validated_content != result.content:
                        logger.info(f"Applied post-generation validation for {self.component_type}")
                        result.content = validated_content
                        
                except Exception as e:
                    logger.warning(f"Post-generation validation failed: {e}")
            
            return result
    
    def _enhance_api_generation(self, material_name: str, **kwargs) -> ComponentResult:
        """Enhance API-based generation with material-aware prompts"""
        
        # Extract parameters
        material_data = kwargs.get('material_data', {})
        api_client = kwargs.get('api_client')
        author_info = kwargs.get('author_info')
        frontmatter_data = kwargs.get('frontmatter_data')
        schema_fields = kwargs.get('schema_fields')
        
        if not api_client:
            return ComponentResult(
                component_type=self.component_type,
                content="",
                success=False,
                error_message="API client required but not provided"
            )
        
        try:
            # Get base prompt from wrapped generator
            base_prompt = self._get_base_prompt_from_generator(
                material_name, material_data, author_info, frontmatter_data, schema_fields
            )
            
            # Enhance with material-aware prompt
            enhanced_prompt = self.material_aware_generator.generate_material_aware_prompt(
                material_name=material_name,
                component_type=self.component_type,
                base_prompt=base_prompt,
                material_data=material_data,
                author_info=author_info,
                frontmatter_data=frontmatter_data,
                schema_fields=schema_fields
            )
            
            logger.info(f"Using material-aware prompt for {self.component_type} - {material_name}")
            
            # Generate content using enhanced prompt
            response = self._call_api_with_enhanced_prompt(api_client, enhanced_prompt)
            
            # Process response
            if isinstance(response, str):
                content = response
            elif hasattr(response, 'success') and response.success:
                content = response.content
            elif hasattr(response, 'success'):
                return ComponentResult(
                    component_type=self.component_type,
                    content="",
                    success=False,
                    error_message=f"API generation failed: {getattr(response, 'error', 'Unknown error')}"
                )
            else:
                content = str(response)
            
            # Apply material-aware validation
            try:
                validated_content = self.material_aware_generator.validate_generated_content(
                    content=content,
                    material_name=material_name,
                    component_type=self.component_type,
                    material_data=material_data
                )
                
                if validated_content:
                    content = validated_content
                    logger.info(f"Applied material-aware validation for {self.component_type}")
                    
            except Exception as e:
                logger.warning(f"Material-aware validation failed: {e}")
            
            return ComponentResult(
                component_type=self.component_type,
                content=content,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Enhanced API generation failed for {self.component_type}: {e}")
            return ComponentResult(
                component_type=self.component_type,
                content="",
                success=False,
                error_message=str(e)
            )
    
    def _get_base_prompt_from_generator(self, material_name: str, material_data: Dict,
                                      author_info: Optional[Dict], frontmatter_data: Optional[Dict],
                                      schema_fields: Optional[Dict]) -> str:
        """Get base prompt from the wrapped generator"""
        
        if hasattr(self.wrapped_generator, '_build_prompt'):
            try:
                return self.wrapped_generator._build_prompt(
                    material_name, material_data, author_info, frontmatter_data, schema_fields
                )
            except Exception as e:
                logger.warning(f"Failed to get base prompt from generator: {e}")
        
        # Fallback: generate basic prompt
        return f"Generate high-quality {self.component_type} content for {material_name}."
    
    def _call_api_with_enhanced_prompt(self, api_client, prompt: str):
        """Call API with enhanced prompt using appropriate method"""
        
        if hasattr(api_client, "generate_for_component"):
            return api_client.generate_for_component(
                component_type=self.component_type,
                material="",  # Material info is in the prompt
                prompt_template=prompt,
            )
        elif hasattr(api_client, "generate_simple"):
            return api_client.generate_simple(prompt)
        else:
            return api_client.generate(prompt)
    
    def __getattr__(self, name):
        """Delegate all other attributes to the wrapped generator"""
        return getattr(self.wrapped_generator, name)


class MaterialAwareComponentFactory:
    """
    Factory that wraps existing component generators with material-aware capabilities
    
    This factory acts as a transparent enhancement layer - it creates the same generators
    as the original factory but wraps them with material-aware prompt capabilities.
    """
    
    def __init__(self, original_factory):
        """
        Initialize with reference to original ComponentGeneratorFactory
        
        Args:
            original_factory: Original ComponentGeneratorFactory class
        """
        self.original_factory = original_factory
        logger.info("Initialized MaterialAwareComponentFactory")
    
    def create_generator(self, component_type: str, **kwargs):
        """
        Create component generator with material-aware wrapper
        
        Args:
            component_type: Type of component to generate
            **kwargs: Additional arguments for generator creation
            
        Returns:
            Component generator wrapped with material-aware capabilities
        """
        
        # Create original generator
        original_generator = self.original_factory.create_generator(component_type, **kwargs)
        
        if original_generator is None:
            return None
        
        # Check if this generator would benefit from material-aware wrapping
        if self._should_wrap_generator(original_generator, component_type):
            wrapped_generator = MaterialAwareComponentWrapper(original_generator, component_type)
            logger.debug(f"Wrapped {component_type} generator with material-aware capabilities")
            return wrapped_generator
        else:
            logger.debug(f"Using original {component_type} generator without wrapping")
            return original_generator
    
    def _should_wrap_generator(self, generator, component_type: str) -> bool:
        """
        Determine if generator should be wrapped with material-aware capabilities
        
        Args:
            generator: Generator instance to potentially wrap
            component_type: Type of component
            
        Returns:
            True if generator should be wrapped
        """
        
        # Don't wrap generators that already have material-aware capabilities
        if hasattr(generator, 'material_aware_generator'):
            return False
        
        # Wrap API-based generators (most likely to benefit)
        if isinstance(generator, APIComponentGenerator):
            return True
        
        # Wrap specific component types that benefit from material-specific handling
        beneficial_components = [
            'metricsproperties', 'metricsmachinesettings', 'text', 'propertiestable',
            'tags', 'caption', 'table', 'settings'
        ]
        
        if component_type in beneficial_components:
            return True
        
        return False
    
    def get_available_components(self):
        """Get available components from original factory"""
        return self.original_factory.get_available_components()


# Utility functions for easy integration

def enhance_existing_factory():
    """
    Enhance the existing ComponentGeneratorFactory with material-aware capabilities
    
    This function can be called during system initialization to transparently
    upgrade all component generation with material-aware prompts.
    
    Returns:
        MaterialAwareComponentFactory instance
    """
    from generators.component_generators import ComponentGeneratorFactory
    
    enhanced_factory = MaterialAwareComponentFactory(ComponentGeneratorFactory)
    logger.info("Enhanced ComponentGeneratorFactory with material-aware capabilities")
    
    return enhanced_factory


def wrap_generator(generator, component_type: str):
    """
    Wrap an individual generator with material-aware capabilities
    
    Args:
        generator: Existing generator to wrap
        component_type: Type of component
        
    Returns:
        Wrapped generator with material-aware capabilities
    """
    return MaterialAwareComponentWrapper(generator, component_type)


# Example usage and integration patterns

def integrate_with_run_system():
    """
    Example integration with the main run.py system
    
    This shows how to integrate the material-aware wrapper with the existing
    component generation workflow without breaking existing functionality.
    """
    
    # Option 1: Replace factory at runtime
    try:
        # Import and replace the factory
        import generators.component_generators as cg
        
        # Create enhanced factory
        enhanced_factory = enhance_existing_factory()
        
        # Replace the factory class methods
        cg.ComponentGeneratorFactory.create_generator = enhanced_factory.create_generator
        cg.ComponentGeneratorFactory.get_available_components = enhanced_factory.get_available_components
        
        logger.info("Successfully integrated material-aware factory into component generation system")
        
    except Exception as e:
        logger.error(f"Failed to integrate material-aware factory: {e}")
        # System continues with original factory


if __name__ == "__main__":
    # Demo the enhancement system
    print("Material-Aware Component Wrapper Demo")
    print("=====================================")
    
    # Show how to enhance the factory
    enhanced_factory = enhance_existing_factory()
    print(f"Enhanced factory created: {enhanced_factory}")
    
    # Show available components
    components = enhanced_factory.get_available_components()
    print(f"Available components: {components}")
    
    # Demo creating an enhanced generator
    if 'text' in components:
        text_gen = enhanced_factory.create_generator('text')
        print(f"Created text generator: {type(text_gen)}")
        
        # Show wrapper capabilities
        if hasattr(text_gen, 'material_aware_generator'):
            print("✅ Generator has material-aware capabilities")
        else:
            print("ℹ️  Generator uses original behavior")