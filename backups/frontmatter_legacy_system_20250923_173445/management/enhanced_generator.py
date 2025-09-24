#!/usr/bin/env python3
"""
Enhanced Component Generator Base Class
Integrates with the new frontmatter management system for robust data handling.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Import the new frontmatter manager
try:
    from frontmatter.management.manager import FrontmatterManager, FrontmatterValidationError, FrontmatterNotFoundError
except ImportError:
    # Fallback during migration
    FrontmatterManager = None
    FrontmatterValidationError = Exception
    FrontmatterNotFoundError = Exception

logger = logging.getLogger(__name__)

class EnhancedComponentGenerator(ABC):
    """
    Enhanced base class for component generators with integrated frontmatter management.
    Provides robust data loading, validation, and error handling.
    """
    
    def __init__(self, component_name: str):
        self.component_name = component_name
        
        # Initialize frontmatter manager if available
        self.frontmatter_manager = None
        if FrontmatterManager:
            try:
                self.frontmatter_manager = FrontmatterManager()
                logger.info(f"FrontmatterManager initialized for {component_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize FrontmatterManager: {e}")
        else:
            logger.warning("FrontmatterManager not available - using legacy loading")
    
    def load_frontmatter(self, material_name: str, validate: bool = True) -> Dict[str, Any]:
        """
        Load frontmatter data with enhanced error handling and validation.
        
        Args:
            material_name: Name of the material
            validate: Whether to perform schema validation
            
        Returns:
            Dictionary containing frontmatter data
            
        Raises:
            ValueError: If frontmatter cannot be loaded or is invalid
        """
        if self.frontmatter_manager:
            # Use new frontmatter management system
            try:
                return self.frontmatter_manager.load_material(material_name, validate=validate)
            except FrontmatterNotFoundError as e:
                raise ValueError(f"Frontmatter not found for {material_name}: {e}")
            except FrontmatterValidationError as e:
                raise ValueError(f"Frontmatter validation failed for {material_name}: {e}")
        else:
            # Fallback to legacy loading
            return self._legacy_load_frontmatter(material_name)
    
    def _legacy_load_frontmatter(self, material_name: str) -> Dict[str, Any]:
        """Legacy frontmatter loading for backward compatibility"""
        import yaml
        
        # Try new location first, then old location
        safe_name = material_name.lower().replace(' ', '-').replace('_', '-')
        possible_paths = [
            Path("frontmatter/materials") / f"{safe_name}-laser-cleaning.md",
            Path("frontmatter/materials") / f"{safe_name}-laser-cleaning.md"
        ]
        
        for frontmatter_path in possible_paths:
            if frontmatter_path.exists():
                try:
                    with open(frontmatter_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parse frontmatter
                    if content.startswith('---\\n'):
                        lines = content.split('\\n')
                        end_line = -1
                        for i, line in enumerate(lines[1:], 1):
                            if line.strip() == '---':
                                end_line = i
                                break
                        
                        if end_line == -1:
                            yaml_content = '\\n'.join(lines[1:])
                        else:
                            yaml_content = '\\n'.join(lines[1:end_line])
                        
                        return yaml.safe_load(yaml_content)
                    
                except Exception as e:
                    logger.error(f"Failed to load frontmatter from {frontmatter_path}: {e}")
                    continue
        
        raise ValueError(f"No frontmatter found for material: {material_name}")
    
    def validate_required_fields(self, frontmatter_data: Dict[str, Any], required_fields: list) -> None:
        """
        Validate that all required fields are present in frontmatter.
        
        Args:
            frontmatter_data: The frontmatter dictionary
            required_fields: List of required field paths (e.g., ['name', 'technicalSpecifications.wavelength'])
            
        Raises:
            ValueError: If any required fields are missing
        """
        missing_fields = []
        
        for field_path in required_fields:
            if '.' in field_path:
                # Handle nested fields
                parts = field_path.split('.')
                current = frontmatter_data
                try:
                    for part in parts:
                        current = current[part]
                except (KeyError, TypeError):
                    missing_fields.append(field_path)
            else:
                # Handle top-level fields
                if field_path not in frontmatter_data:
                    missing_fields.append(field_path)
        
        if missing_fields:
            raise ValueError(f"Required fields missing from frontmatter: {missing_fields}")
    
    def get_component_specific_requirements(self) -> Dict[str, Any]:
        """
        Get component-specific frontmatter requirements.
        Override in subclasses to define component needs.
        
        Returns:
            Dictionary with requirements specification
        """
        return {
            'required_fields': [],
            'optional_fields': [],
            'validation_rules': {}
        }
    
    def validate_frontmatter_for_component(self, frontmatter_data: Dict[str, Any]) -> None:
        """
        Validate frontmatter specifically for this component's requirements.
        
        Args:
            frontmatter_data: The frontmatter dictionary
            
        Raises:
            ValueError: If component-specific validation fails
        """
        requirements = self.get_component_specific_requirements()
        required_fields = requirements.get('required_fields', [])
        
        if required_fields:
            self.validate_required_fields(frontmatter_data, required_fields)
        
        # Additional validation can be added here
        validation_rules = requirements.get('validation_rules', {})
        for field, rule in validation_rules.items():
            if field in frontmatter_data:
                value = frontmatter_data[field]
                if not self._validate_field_rule(value, rule):
                    raise ValueError(f"Field '{field}' validation failed: {rule}")
    
    def _validate_field_rule(self, value: Any, rule: Dict[str, Any]) -> bool:
        """Validate a single field against a rule"""
        if 'type' in rule:
            expected_type = rule['type']
            if expected_type == 'string' and not isinstance(value, str):
                return False
            elif expected_type == 'number' and not isinstance(value, (int, float)):
                return False
            elif expected_type == 'list' and not isinstance(value, list):
                return False
        
        if 'min_length' in rule and isinstance(value, str):
            if len(value) < rule['min_length']:
                return False
        
        return True
    
    @abstractmethod
    def generate(self, material_name: str, **kwargs) -> Dict[str, Any]:
        """
        Generate component content for the specified material.
        
        Args:
            material_name: Name of the material
            **kwargs: Additional generation parameters
            
        Returns:
            Dictionary containing generated content and metadata
        """
        pass
    
    def generate_with_validation(self, material_name: str, **kwargs) -> Dict[str, Any]:
        """
        Generate component content with comprehensive validation.
        
        Args:
            material_name: Name of the material
            **kwargs: Additional generation parameters
            
        Returns:
            Dictionary containing generated content and metadata
        """
        try:
            # Load and validate frontmatter
            frontmatter_data = self.load_frontmatter(material_name, validate=True)
            
            # Component-specific validation
            self.validate_frontmatter_for_component(frontmatter_data)
            
            # Add frontmatter to kwargs for generation
            kwargs['frontmatter_data'] = frontmatter_data
            
            # Generate content
            result = self.generate(material_name, **kwargs)
            
            # Add metadata to result
            if isinstance(result, dict):
                result['_metadata'] = {
                    'component': self.component_name,
                    'material': material_name,
                    'frontmatter_validated': True,
                    'generation_method': 'enhanced'
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Generation failed for {self.component_name}/{material_name}: {e}")
            raise ValueError(f"Component generation failed: {e}")

class FailFastComponentGenerator(EnhancedComponentGenerator):
    """
    Specialized component generator for fail-fast architecture.
    Implements strict validation and immediate failure on any issues.
    """
    
    def __init__(self, component_name: str):
        super().__init__(component_name)
        self.strict_mode = True
    
    def generate_with_validation(self, material_name: str, **kwargs) -> Dict[str, Any]:
        """Generate with strict fail-fast validation"""
        if not self.frontmatter_manager:
            raise ValueError(f"FrontmatterManager required for fail-fast generation in {self.component_name}")
        
        # Strict validation mode
        try:
            result = super().generate_with_validation(material_name, **kwargs)
            
            # Additional fail-fast checks
            if not result or not isinstance(result, dict):
                raise ValueError(f"Invalid generation result for {material_name}")
            
            return result
            
        except Exception as e:
            # In fail-fast mode, re-raise with enhanced error information
            raise ValueError(
                f"FAIL-FAST VIOLATION in {self.component_name}: "
                f"Material '{material_name}' failed generation. "
                f"Error: {str(e)}. "
                f"This component requires complete, validated frontmatter data."
            )

# Convenience functions for easy migration
def create_enhanced_generator(component_name: str, generator_class=None):
    """Factory function to create enhanced generators"""
    if generator_class:
        # Wrap existing generator class
        class WrappedGenerator(FailFastComponentGenerator):
            def __init__(self):
                super().__init__(component_name)
                self._original_generator = generator_class()
            
            def generate(self, material_name: str, **kwargs):
                return self._original_generator.generate(material_name, **kwargs)
        
        return WrappedGenerator()
    else:
        return FailFastComponentGenerator(component_name)
