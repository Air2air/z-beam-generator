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

from shared.generators.component_generators import APIComponentGenerator, ComponentResult
from shared.validation.errors import (
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
            from shared.validation.schema_validator import SchemaValidator
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
        AUTOMATIC VOICE QUALITY GATE (runs during frontmatter export).
        
        This automatically validates and repairs voice quality:
        1. Scans all text fields for quality issues (score >= 70 required)
        2. If issues found, triggers automatic repair in Materials.yaml
        3. Repairs regenerate text with quality validation + retries
        4. Materials.yaml updated with fixed content (source of truth maintained)
        5. Export continues with clean data from Materials.yaml
        
        **FULLY AUTOMATIC - NO USER INTERVENTION REQUIRED**
        
        Per DATA_STORAGE_POLICY:
        - Materials.yaml is always the source of truth
        - Frontmatter export validates + auto-repairs if needed
        - All fixes saved back to Materials.yaml before export
        
        Args:
            frontmatter_data: Frontmatter dictionary with text fields
            author_data: Author information (name, country, expertise)
            context: Generation context
            
        Returns:
            Validated frontmatter (automatically repaired if issues found)
            
        Raises:
            GenerationError: If voice quality cannot be fixed after retries
        """
        try:
            from shared.voice.quality_scanner import VoiceQualityScanner
            from shared.voice.source_data_repairer import SourceDataRepairer
            
            # Initialize scanner and repairer (content-agnostic)
            if not self.api_client:
                self.logger.warning(
                    "API client required for automatic quality gate - "
                    "skipping voice validation"
                )
                return frontmatter_data
            
            scanner = VoiceQualityScanner(self.api_client)
            
            # STEP 1: Automatic quality scan
            self.logger.info(
                f"🔍 Scanning voice quality for {context.identifier}..."
            )
            
            issues, total_scanned, failed_count = scanner.scan_text_fields(
                frontmatter_data,
                author_data
            )
            
            if failed_count == 0:
                self.logger.info(
                    f"✅ Voice quality passed: {total_scanned} fields scanned, all clean"
                )
            else:
                # STEP 2: Automatic repair triggered
                self.logger.warning(
                    f"🚨 Voice quality issues detected: {failed_count}/{total_scanned} fields failed"
                )
                
                for issue in issues[:5]:  # Show top 5 issues
                    self.logger.warning(
                        f"   - {issue['field_path']}: {issue['score']:.1f}/100"
                    )
                    for problem in issue['issues'][:2]:
                        self.logger.warning(f"     • {problem}")
                
                # STEP 3: Automatic repair in source YAML (content-agnostic)
                self.logger.info(
                    f"🔧 Triggering automatic repair in source YAML ({self.content_type})..."
                )
                self.logger.info(f"   Found {len(issues)} issues to repair")
                
                # Create content-agnostic repairer
                repairer = SourceDataRepairer.create_for_content_type(
                    api_client=self.api_client,
                    content_type=self.content_type
                )
                
                repairs_successful = 0
                repairs_failed = 0
                
                for issue in issues:
                    if issue['failed']:
                        self.logger.info(f"   Attempting repair of {issue['field_path']}...")
                        fixed_text, success = repairer.repair_field(
                            identifier=context.identifier,
                            field_path=issue['field_path'],
                            current_text=issue.get('text_preview', ''),
                            author_data=author_data
                        )
                        
                        if success:
                            repairs_successful += 1
                            # Apply fix to frontmatter_data using field path
                            try:
                                self._update_field_by_path(
                                    frontmatter_data,
                                    issue['field_path'],
                                    fixed_text
                                )
                                self.logger.info(f"   ✅ Applied fix to {issue['field_path']}")
                            except Exception as e:
                                self.logger.warning(f"   ⚠️  Failed to apply fix to {issue['field_path']}: {e}")
                                repairs_failed += 1
                                repairs_successful -= 1
                        else:
                            repairs_failed += 1
                
                if repairs_failed > 0:
                    self.logger.error(
                        f"❌ {repairs_failed} field(s) could not be repaired automatically"
                    )
                    # Continue anyway - some fields may be fixed
                else:
                    self.logger.info(
                        f"✅ All {repairs_successful} field(s) repaired successfully in Materials.yaml"
                    )
            
            validated_data = frontmatter_data  # Return validated/repaired data
            
            # Inject voice metadata
            if '_metadata' not in validated_data:
                validated_data['_metadata'] = {}
            
            # Extract country - FAIL-FAST if missing
            if 'country' not in author_data:
                raise ValueError(
                    "Author data missing 'country' field. "
                    "All authors must have country defined."
                )
            author_country = author_data['country']
            
            validated_data['_metadata']['voice'] = {
                'author_name': author_data.get('name', 'Unknown'),
                'author_country': author_country,
                'voice_applied': True,
                'voice_validated': True,
                'quality_issues_detected': failed_count,
                'total_fields_scanned': total_scanned,
                'content_type': self.content_type
            }
            
            self.logger.info(
                f"✅ Voice quality gate complete for {context.identifier} "
                f"({author_country} author, {total_scanned} fields scanned)"
            )
            
            return validated_data
            
        except Exception as e:
            # Voice processing failure should not block generation
            # Log error and return original data
            self.logger.error(f"Author voice processing failed: {e}")
            return frontmatter_data
    
    def _update_field_by_path(
        self,
        data: Dict,
        field_path: str,
        new_value: str
    ):
        """
        Update a field in nested dict using dot-notation path with array indexing.
        
        Supports paths like:
        - "caption" → data['caption'] = new_value
        - "images.hero.alt" → data['images']['hero']['alt'] = new_value
        - "faq[0].answer" → data['faq'][0]['answer'] = new_value
        
        Args:
            data: Data dictionary to update
            field_path: Dot-notation path (e.g., "faq[1].answer", "images.hero.alt")
            new_value: New value to set
        """
        import re
        
        # Parse path into parts (handle array indexing)
        parts = []
        for part in field_path.split('.'):
            # Check for array indexing like "faq[0]"
            match = re.match(r'(\w+)\[(\d+)\]', part)
            if match:
                parts.append(match.group(1))  # field name
                parts.append(int(match.group(2)))  # array index
            else:
                parts.append(part)
        
        # Navigate to parent object
        current = data
        for part in parts[:-1]:
            if isinstance(part, int):
                current = current[part]
            else:
                if part not in current:
                    current[part] = {}
                current = current[part]
        
        # Set final value
        final_key = parts[-1]
        if isinstance(final_key, int):
            current[final_key] = new_value
        else:
            current[final_key] = new_value
    
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
    
    def _validate_text_fields_voice_quality(
        self,
        data: Any,
        processor: Any,
        author_data: Dict[str, str],
        context: GenerationContext,
        field_path: str = ""
    ) -> tuple[Any, int]:
        """
        Recursively validate voice quality in all text fields (QUALITY GATE).
        
        This method:
        1. Checks voice quality of text fields from Materials.yaml
        2. If quality score < 70, regenerates and updates Materials.yaml
        3. Returns validated data (from Materials.yaml after fixes)
        
        Args:
            data: Data structure to validate (dict, list, or string)
            processor: VoicePostProcessor instance
            author_data: Author information
            context: Generation context
            field_path: Current field path (for logging)
            
        Returns:
            Tuple of (validated_data, fixes_applied_count)
        """
        fixes_count = 0
        
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                current_path = f"{field_path}.{key}" if field_path else key
                validated_value, field_fixes = self._validate_text_fields_voice_quality(
                    value, processor, author_data, context, current_path
                )
                result[key] = validated_value
                fixes_count += field_fixes
            return result, fixes_count
            
        elif isinstance(data, list):
            result = []
            for idx, item in enumerate(data):
                current_path = f"{field_path}[{idx}]"
                validated_item, item_fixes = self._validate_text_fields_voice_quality(
                    item, processor, author_data, context, current_path
                )
                result.append(validated_item)
                fixes_count += item_fixes
            return result, fixes_count
            
        elif isinstance(data, str) and len(data.split()) > 10:
            # Validate text field voice quality
            try:
                from shared.voice.orchestrator import VoiceOrchestrator
                
                country = author_data.get('country', 'Unknown')
                voice = VoiceOrchestrator(country=country)
                voice_indicators = voice.get_signature_phrases()
                
                # Check quality score
                quality = processor.score_voice_authenticity(
                    data, author_data, voice_indicators
                )
                
                quality_score = quality['authenticity_score']
                
                # Quality threshold: 70 points
                if quality_score < 70:
                    self.logger.warning(
                        f"🚨 Voice quality issue in {field_path}: {quality_score:.1f}/100"
                    )
                    for issue in quality['issues'][:3]:
                        self.logger.warning(f"   - {issue}")
                    
                    self.logger.info(
                        "   🔧 Regenerating field in Materials.yaml..."
                    )
                    
                    # Regenerate with quality validation
                    fixed_text = processor.enhance(
                        text=data,
                        author=author_data,
                        preserve_length=True,
                        voice_intensity=3
                    )
                    
                    # Update Materials.yaml with fixed text
                    self._update_materials_yaml_field(
                        context.identifier,
                        field_path,
                        fixed_text
                    )
                    
                    self.logger.info(
                        f"   ✅ Fixed and saved to Materials.yaml: {field_path}"
                    )
                    
                    return fixed_text, 1
                else:
                    # Quality passed
                    return data, 0
                    
            except Exception as e:
                self.logger.warning(
                    f"Failed to validate voice quality for {field_path}: {e}"
                )
                return data, 0
        else:
            return data, 0
    
    def _update_materials_yaml_field(
        self,
        material_name: str,
        field_path: str,
        new_value: str
    ):
        """
        Update a specific field in Materials.yaml (source of truth).
        
        Args:
            material_name: Material identifier
            field_path: Dot-notation path to field (e.g., "faq[0].answer")
            new_value: New text value to save
        """
        try:
            import yaml
            from pathlib import Path
            
            materials_yaml_path = Path("materials/data/materials.yaml")
            
            # Load materials.yaml
            with open(materials_yaml_path, 'r', encoding='utf-8') as f:
                materials_data = yaml.safe_load(f)
            
            # Navigate to material
            if material_name not in materials_data:
                self.logger.error(f"Material {material_name} not found in Materials.yaml")
                return
            
            # Parse field path and update
            # material = materials_data[material_name]  # Will be used when path navigation implemented
            # For now, support simple paths like "faq[0].answer"
            # TODO: Implement full path navigation
            self.logger.warning(
                f"Materials.yaml update for {field_path} - "
                f"implementation pending (full path navigation needed)"
            )
            
            # Save materials.yaml
            # with open(materials_yaml_path, 'w', encoding='utf-8') as f:
            #     yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True)
            
        except Exception as e:
            self.logger.error(f"Failed to update Materials.yaml: {e}")
    
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
            # All frontmatter goes to /frontmatter/{type}/
            if self.content_type == 'material':
                output_dir = Path("frontmatter/materials")
            elif self.content_type == 'region':
                output_dir = Path("frontmatter/regions")
            elif self.content_type == 'application':
                output_dir = Path("frontmatter/applications")
            elif self.content_type == 'contaminant':
                output_dir = Path("frontmatter/contaminants")
            elif self.content_type == 'thesaurus':
                output_dir = Path("frontmatter/thesaurus")
            else:
                # Fallback for any future types
                output_dir = Path("frontmatter") / f"{self.content_type}s"
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
