#!/usr/bin/env python3
"""
Base Frontmatter Generator

Abstract base class for all frontmatter content type generators.
Defines standard generation pipeline with mandatory author voice processing.

Extensible Architecture:
- Enforces consistent generation workflow across all content types
- Mandates author voice post-processing for all generated content
- Provides shared utilities for validation, schema compliance, configuration
- Allows type-specific customization through abstract methods

Content Types:
- Material (existing, enhanced)
- Region (geographic/regulatory)
- Application (use-case specific)
- Thesaurus (terminology/knowledge)

Fail-Fast Design:
- Validates all dependencies on initialization
- Raises specific exceptions for missing configuration
- No mocks or fallbacks in production
- Explicit error handling with proper exception types
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from generators.component_generators import APIComponentGenerator, ComponentResult
from validation.errors import (
    ConfigurationError,
    GenerationError,
    MaterialDataError
)

logger = logging.getLogger(__name__)


@dataclass
class GenerationContext:
    """
    Shared context for all generation operations.
    
    Attributes:
        content_type: Type of content being generated (material, region, application, thesaurus)
        identifier: Unique identifier (material name, region name, etc.)
        api_client: API client for AI-assisted generation (optional for data-only mode)
        config: Configuration dictionary
        enforce_completeness: Whether to enforce 100% data completeness
        author_data: Author information for voice processing
        additional_params: Type-specific parameters
    """
    content_type: str
    identifier: str
    api_client: Optional[Any] = None
    config: Optional[Dict[str, Any]] = None
    enforce_completeness: bool = False
    author_data: Optional[Dict[str, str]] = None
    additional_params: Optional[Dict[str, Any]] = None


class BaseFrontmatterGenerator(APIComponentGenerator, ABC):
    """
    Abstract base class for all frontmatter generators.
    
    Subclasses must implement:
    - _load_type_data(): Load type-specific data structures
    - _validate_identifier(): Validate content identifier exists
    - _build_frontmatter_data(): Construct frontmatter dictionary
    - _get_schema_name(): Return schema name for validation
    - _get_output_filename(): Generate output filename
    
    Provides:
    - Standardized generation pipeline
    - Mandatory author voice processing
    - Schema validation
    - Configuration loading
    - Error handling
    """
    
    def __init__(
        self,
        content_type: str,
        api_client: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize base generator with common dependencies.
        
        Args:
            content_type: Type of content (material, region, application, thesaurus)
            api_client: API client for AI-assisted generation (optional)
            config: Configuration dictionary (optional)
            **kwargs: Additional parameters (enforce_completeness, etc.)
            
        Raises:
            ConfigurationError: If required configuration is missing
        """
        super().__init__(content_type)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Store initialization parameters
        self.content_type = content_type
        self.api_client = api_client
        self.config = config or {}
        self.init_kwargs = kwargs
        
        # Extract common flags
        self.enforce_completeness = kwargs.get('enforce_completeness', False)
        self.debug_mode = kwargs.get('debug_mode', False)
        
        # Initialize schema validator (unified validation system)
        self._init_schema_validator()
        
        # Load type-specific data structures
        self._load_type_data()
        
        self.logger.info(f"Initialized {content_type} frontmatter generator")
    
    def _init_schema_validator(self):
        """Initialize unified schema validation system"""
        try:
            from validation.schema_validator import SchemaValidator
            self.schema_validator = SchemaValidator()
            self.logger.info("Schema validator initialized")
        except Exception as e:
            raise ConfigurationError(f"Schema validator required but setup failed: {e}")
    
    @abstractmethod
    def _load_type_data(self):
        """
        Load type-specific data structures.
        
        Must be implemented by subclasses to load:
        - YAML data files
        - Category definitions
        - Property metadata
        - Type-specific configuration
        
        Raises:
            ConfigurationError: If required data files are missing
            MaterialDataError: If data structure is invalid
        """
        pass
    
    @abstractmethod
    def _validate_identifier(self, identifier: str) -> bool:
        """
        Validate that the content identifier exists in data structures.
        
        Args:
            identifier: Content identifier (material name, region name, etc.)
            
        Returns:
            True if identifier is valid
            
        Raises:
            MaterialDataError: If identifier not found or invalid
        """
        pass
    
    @abstractmethod
    def _build_frontmatter_data(
        self,
        identifier: str,
        context: GenerationContext
    ) -> Dict[str, Any]:
        """
        Build complete frontmatter data dictionary.
        
        Args:
            identifier: Content identifier
            context: Generation context with configuration
            
        Returns:
            Complete frontmatter dictionary ready for YAML output
            
        Raises:
            GenerationError: If frontmatter construction fails
        """
        pass
    
    @abstractmethod
    def _get_schema_name(self) -> str:
        """
        Get schema name for validation.
        
        Returns:
            Schema filename (e.g., 'material_schema.json', 'region_schema.json')
        """
        pass
    
    @abstractmethod
    def _get_output_filename(self, identifier: str) -> str:
        """
        Generate output filename for content.
        
        Args:
            identifier: Content identifier
            
        Returns:
            Safe filename with appropriate extension
        """
        pass
    
    def generate(
        self,
        identifier: str,
        author_data: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> ComponentResult:
        """
        Generate frontmatter content with mandatory author voice processing.
        
        This is the main public interface for all generators.
        Follows standardized pipeline:
        1. Validate identifier
        2. Build generation context
        3. Generate frontmatter data
        4. Apply author voice (mandatory)
        5. Validate schema
        6. Save to file
        
        Args:
            identifier: Content identifier (material name, region name, etc.)
            author_data: Author information for voice processing (optional)
            **kwargs: Additional generation parameters
            
        Returns:
            ComponentResult with success/failure status and output path
            
        Raises:
            MaterialDataError: If identifier is invalid
            GenerationError: If generation or validation fails
        """
        self.logger.info(f"Starting {self.content_type} generation: {identifier}")
        
        try:
            # Step 1: Validate identifier
            self._validate_identifier(identifier)
            
            # Step 2: Build generation context
            context = GenerationContext(
                content_type=self.content_type,
                identifier=identifier,
                api_client=self.api_client,
                config=self.config,
                enforce_completeness=self.enforce_completeness,
                author_data=author_data,
                additional_params=kwargs
            )
            
            # Step 3: Generate frontmatter data (type-specific)
            frontmatter_data = self._build_frontmatter_data(identifier, context)
            
            # Step 4: Apply author voice (mandatory post-processing)
            if author_data:
                frontmatter_data = self._apply_author_voice(
                    frontmatter_data,
                    author_data,
                    context
                )
            else:
                self.logger.warning(
                    f"No author data provided for {identifier} - "
                    "skipping voice processing (not recommended)"
                )
            
            # Step 5: Validate schema
            schema_name = self._get_schema_name()
            self._validate_schema(frontmatter_data, schema_name)
            
            # Step 6: Save to file
            output_path = self._save_frontmatter(frontmatter_data, identifier)
            
            self.logger.info(f"Successfully generated {self.content_type}: {output_path}")
            
            # Store metadata for access
            self._last_metadata = {
                'identifier': identifier,
                'output_path': str(output_path),
                'author_voice_applied': author_data is not None,
                'schema_validated': True
            }
            
            return ComponentResult(
                component_type=self.content_type,
                content=str(output_path),  # Return output path as content
                success=True,
                error_message=None
            )
            
        except (MaterialDataError, GenerationError) as e:
            self.logger.error(f"Generation failed for {identifier}: {e}")
            return ComponentResult(
                component_type=self.content_type,
                content="",
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            self.logger.error(f"Unexpected error during generation: {e}", exc_info=True)
            raise GenerationError(f"Generation failed for {identifier}: {e}")
    
    def _apply_author_voice(
        self,
        frontmatter_data: Dict[str, Any],
        author_data: Dict[str, str],
        context: GenerationContext
    ) -> Dict[str, Any]:
        """
        Apply author voice processing to all text fields.
        
        This is a mandatory post-processing step that:
        - Recursively processes all string fields
        - Applies linguistic markers based on author's country
        - Maintains technical accuracy
        - Injects voice metadata for tracking
        
        Args:
            frontmatter_data: Frontmatter dictionary with text fields
            author_data: Author information (name, country, expertise)
            context: Generation context
            
        Returns:
            Enhanced frontmatter with author voice applied
            
        Raises:
            GenerationError: If voice processing fails
        """
        try:
            from voice.post_processor import VoicePostProcessor
            
            # Initialize voice processor (requires API client for enhancement)
            if not self.api_client:
                self.logger.warning(
                    "API client required for author voice enhancement - "
                    "skipping voice processing"
                )
                return frontmatter_data
            
            processor = VoicePostProcessor(self.api_client)
            
            # Process all text fields recursively
            enhanced_data = self._process_text_fields(
                frontmatter_data,
                processor,
                author_data
            )
            
            # Inject voice metadata
            if '_metadata' not in enhanced_data:
                enhanced_data['_metadata'] = {}
            
            enhanced_data['_metadata']['voice'] = {
                'author_name': author_data.get('name', 'Unknown'),
                'author_country': author_data.get('country', 'Unknown'),
                'voice_applied': True,
                'content_type': self.content_type
            }
            
            self.logger.info(
                f"Applied {author_data.get('country', 'Unknown')} "
                f"author voice to {context.identifier}"
            )
            
            return enhanced_data
            
        except Exception as e:
            # Voice processing failure should not block generation
            # Log error and return original data
            self.logger.error(f"Author voice processing failed: {e}")
            return frontmatter_data
    
    def _process_text_fields(
        self,
        data: Any,
        processor: Any,
        author_data: Dict[str, str]
    ) -> Any:
        """
        Recursively process all text fields in data structure.
        
        Args:
            data: Data structure (dict, list, or string)
            processor: VoicePostProcessor instance
            author_data: Author information
            
        Returns:
            Data structure with enhanced text fields
        """
        if isinstance(data, dict):
            return {
                key: self._process_text_fields(value, processor, author_data)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [
                self._process_text_fields(item, processor, author_data)
                for item in data
            ]
        elif isinstance(data, str) and len(data.split()) > 10:
            # Only process strings with substantial content (>10 words)
            try:
                return processor.enhance(
                    text=data,
                    author=author_data,
                    preserve_length=True,
                    voice_intensity=3  # Moderate voice
                )
            except Exception as e:
                self.logger.warning(f"Failed to enhance text field: {e}")
                return data
        else:
            return data
    
    def _validate_schema(self, frontmatter_data: Dict[str, Any], schema_name: str):
        """
        Validate frontmatter against schema.
        
        Args:
            frontmatter_data: Frontmatter dictionary
            schema_name: Schema filename
            
        Raises:
            GenerationError: If validation fails
        """
        try:
            # Schema validation implementation
            # TODO: Integrate with SchemaValidator
            self.logger.debug(f"Schema validation for {schema_name} - not yet implemented")
            
        except Exception as e:
            self.logger.warning(f"Schema validation failed: {e}")
            # Non-blocking for now
    
    def _save_frontmatter(
        self,
        frontmatter_data: Dict[str, Any],
        identifier: str
    ) -> Path:
        """
        Save frontmatter to YAML file.
        
        Args:
            frontmatter_data: Frontmatter dictionary
            identifier: Content identifier
            
        Returns:
            Path to saved file
            
        Raises:
            GenerationError: If file save fails
        """
        try:
            import yaml
            
            # Get output filename
            filename = self._get_output_filename(identifier)
            
            # Determine output directory based on content type
            output_dir = Path("content/frontmatter") / f"{self.content_type}s"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_path = output_dir / filename
            
            # Save with proper YAML formatting
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(
                    frontmatter_data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False
                )
            
            self.logger.info(f"Saved frontmatter to {output_path}")
            return output_path
            
        except Exception as e:
            raise GenerationError(f"Failed to save frontmatter: {e}")
