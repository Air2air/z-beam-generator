#!/usr/bin/env python3
"""
Integration Workflow for Human-Like Content Validation

Demonstrates how to integrate the human-like validation system into 
the existing Z-Beam content generation workflow with minimal changes.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ContentValidationIntegrator:
    """
    Manages integration of human-like validation into existing workflows.
    
    Provides multiple integration strategies:
    1. Drop-in replacement (minimal changes)
    2. Validation-only mode (validate existing content)
    3. Hybrid mode (validate + optional improvement)
    4. Configuration-driven mode (runtime settings)
    """
    
    def __init__(self, validation_config: Dict[str, Any] = None):
        """
        Initialize the integrator with configuration.
        
        Args:
            validation_config: Configuration for validation behavior
                {
                    'enabled': bool,
                    'threshold': int (0-100),
                    'max_attempts': int,
                    'mode': 'strict'|'permissive'|'advisory'
                }
        """
        self.config = validation_config or self._get_default_config()
        self._enhanced_generator = None
        self._standard_generator = None
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default validation configuration."""
        return {
            'enabled': True,
            'threshold': 80,           # Require 80+ human-likeness score
            'max_attempts': 2,         # Maximum improvement attempts
            'mode': 'permissive',      # permissive|strict|advisory
            'fallback_on_failure': True,  # Use original if improvement fails
            'log_validation_details': True,
            'validate_existing_content': False
        }
    
    def get_content_generator(self):
        """
        Get the appropriate content generator based on configuration.
        
        Returns:
            Content generator (enhanced or standard)
        """
        if not self.config['enabled']:
            # Return standard generator if validation disabled
            if not self._standard_generator:
                from components.content.generator import ContentComponentGenerator
                self._standard_generator = ContentComponentGenerator()
            return self._standard_generator
        
        # Return enhanced generator with validation
        if not self._enhanced_generator:
            from components.content.enhanced_generator import EnhancedContentGenerator
            self._enhanced_generator = EnhancedContentGenerator(
                enable_validation=True,
                human_likeness_threshold=self.config['threshold'],
                max_improvement_attempts=self.config['max_attempts']
            )
        
        return self._enhanced_generator
    
    def generate_content_with_validation(self, material_name: str, material_data: Dict,
                                       api_client, author_info: Optional[Dict] = None,
                                       frontmatter_data: Optional[Dict] = None,
                                       schema_fields: Optional[Dict] = None):
        """
        Generate content with integrated validation.
        
        This is the main integration point - can be used as drop-in replacement
        for existing content generation calls.
        """
        generator = self.get_content_generator()
        
        try:
            result = generator.generate(
                material_name, material_data, api_client,
                author_info, frontmatter_data, schema_fields
            )
            
            # Log validation results if enabled
            if (self.config.get('log_validation_details', False) and 
                hasattr(result, 'metadata') and 
                result.metadata and 
                'human_likeness_validation' in result.metadata):
                
                validation_info = result.metadata['human_likeness_validation']
                self._log_validation_results(material_name, validation_info)
            
            # Handle different validation modes
            return self._handle_validation_mode(result, material_name)
            
        except Exception as e:
            logger.error(f"Content generation with validation failed for {material_name}: {e}")
            
            # Fallback to standard generation if enabled
            if self.config.get('fallback_on_failure', False):
                logger.info(f"Attempting fallback generation for {material_name}")
                return self._fallback_generation(
                    material_name, material_data, api_client,
                    author_info, frontmatter_data, schema_fields
                )
            
            raise
    
    def validate_existing_content(self, content: str, material_name: str = "",
                                author_info: Dict = None) -> Dict[str, Any]:
        """
        Validate existing content without regeneration.
        
        Useful for:
        - Auditing existing generated content
        - Testing validation criteria
        - Content quality assessment
        """
        if not self.config['enabled']:
            return {
                'success': False,
                'message': 'Validation is disabled'
            }
        
        try:
            from components.content.human_validator import validate_content_human_like
            
            validation_result = validate_content_human_like(
                content, material_name, author_info
            )
            
            if self.config.get('log_validation_details', False):
                self._log_validation_results(material_name, {
                    'final_score': validation_result.get('human_likeness_score', 0),
                    'passes_threshold': validation_result.get('human_likeness_score', 0) >= self.config['threshold'],
                    'validation_details': validation_result.get('category_scores', {}),
                    'recommendations': validation_result.get('recommendations', [])
                })
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Content validation failed for {material_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _handle_validation_mode(self, result, material_name: str):
        """Handle different validation modes."""
        mode = self.config.get('mode', 'permissive')
        
        if not hasattr(result, 'metadata') or not result.metadata:
            return result
        
        validation_info = result.metadata.get('human_likeness_validation', {})
        if not validation_info:
            return result
        
        score = validation_info.get('final_score', 0)
        passes = validation_info.get('passes_threshold', False)
        
        if mode == 'strict':
            # Strict mode: Fail if validation doesn't pass
            if not passes:
                logger.warning(f"Content for {material_name} failed strict validation (score: {score})")
                result.success = False
                result.error = f"Content failed human-likeness validation (score: {score}/{self.config['threshold']})"
        
        elif mode == 'advisory':
            # Advisory mode: Always succeed but log concerns
            if not passes:
                logger.info(f"Content for {material_name} below advisory threshold (score: {score})")
                # Add advisory metadata
                result.metadata['validation_advisory'] = {
                    'below_threshold': True,
                    'score': score,
                    'recommendations': validation_info.get('recommendations', [])
                }
        
        # Permissive mode: Always succeed (default behavior)
        
        return result
    
    def _fallback_generation(self, material_name: str, material_data: Dict,
                           api_client, author_info: Optional[Dict],
                           frontmatter_data: Optional[Dict],
                           schema_fields: Optional[Dict]):
        """Fallback to standard generation without validation."""
        try:
            from components.content.generator import ContentComponentGenerator
            
            standard_generator = ContentComponentGenerator()
            result = standard_generator.generate(
                material_name, material_data, api_client,
                author_info, frontmatter_data, schema_fields
            )
            
            # Mark as fallback generation
            if hasattr(result, 'metadata') and result.metadata:
                result.metadata['generation_method'] = 'fallback_no_validation'
            
            logger.info(f"Fallback generation successful for {material_name}")
            return result
            
        except Exception as e:
            logger.error(f"Fallback generation also failed for {material_name}: {e}")
            raise
    
    def _log_validation_results(self, material_name: str, validation_info: Dict):
        """Log detailed validation results."""
        score = validation_info.get('final_score', 0)
        passes = validation_info.get('passes_threshold', False)
        attempts = validation_info.get('total_attempts', 1)
        
        status = "✅ PASSED" if passes else "⚠️ BELOW THRESHOLD"
        logger.info(f"Validation Results for {material_name}: {status} (Score: {score}/100, Attempts: {attempts})")
        
        # Log category breakdown
        details = validation_info.get('validation_details', {})
        if details:
            logger.debug(f"Category Scores for {material_name}: {details}")
        
        # Log recommendations if any
        recommendations = validation_info.get('recommendations', [])
        if recommendations:
            logger.debug(f"Recommendations for {material_name}: {recommendations[:3]}")  # Top 3
    
    def update_config(self, **kwargs):
        """Update validation configuration at runtime."""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                logger.info(f"Updated validation config: {key} = {value}")
        
        # Update enhanced generator if it exists
        if self._enhanced_generator:
            if 'threshold' in kwargs:
                self._enhanced_generator.set_validation_threshold(kwargs['threshold'])
            if 'enabled' in kwargs:
                self._enhanced_generator.enable_validation_mode(kwargs['enabled'])
    
    def get_integration_guide(self) -> str:
        """Get integration guide for developers."""
        return """
# Human-Like Content Validation Integration Guide

## 1. Drop-in Replacement (Minimal Changes)

```python
# Before:
from components.content.generator import ContentComponentGenerator
generator = ContentComponentGenerator()
result = generator.generate(material_name, material_data, api_client, author_info)

# After:
from components.content.integration_workflow import ContentValidationIntegrator
integrator = ContentValidationIntegrator()
result = integrator.generate_content_with_validation(
    material_name, material_data, api_client, author_info
)
```

## 2. Configuration-Driven Integration

```python
# Custom configuration
config = {
    'enabled': True,
    'threshold': 85,  # Higher threshold
    'max_attempts': 3,
    'mode': 'strict',  # Fail if validation doesn't pass
    'log_validation_details': True
}

integrator = ContentValidationIntegrator(config)
result = integrator.generate_content_with_validation(...)
```

## 3. Validation-Only Mode (Audit Existing Content)

```python
integrator = ContentValidationIntegrator()
validation_result = integrator.validate_existing_content(
    existing_content, material_name, author_info
)
print(f"Human-likeness score: {validation_result['human_likeness_score']}/100")
```

## 4. Runtime Configuration Updates

```python
integrator = ContentValidationIntegrator()

# Update threshold based on content type
integrator.update_config(threshold=90, mode='strict')

# Disable validation for specific cases
integrator.update_config(enabled=False)
```

## 5. Integration into Existing run.py

```python
# In run.py, replace content generation calls:

# Before:
if component == "content":
    generator = ContentComponentGenerator()
    result = generator.generate(material_name, material_data, api_client, author_info)

# After:
if component == "content":
    integrator = ContentValidationIntegrator()
    result = integrator.generate_content_with_validation(
        material_name, material_data, api_client, author_info, frontmatter_data
    )
```

This approach provides backward compatibility while adding powerful validation capabilities.
        """


# Global integrator instance for easy access
_global_integrator = None

def get_content_integrator(config: Dict[str, Any] = None) -> ContentValidationIntegrator:
    """Get or create global content validation integrator."""
    global _global_integrator
    if _global_integrator is None or config is not None:
        _global_integrator = ContentValidationIntegrator(config)
    return _global_integrator

def generate_validated_content(material_name: str, material_data: Dict, api_client,
                             author_info: Optional[Dict] = None,
                             frontmatter_data: Optional[Dict] = None,
                             validation_config: Dict[str, Any] = None):
    """
    Convenience function for validated content generation.
    
    This is the simplest integration point - can be used as a direct replacement
    for existing content generation calls.
    """
    integrator = get_content_integrator(validation_config)
    return integrator.generate_content_with_validation(
        material_name, material_data, api_client, author_info, frontmatter_data
    )
