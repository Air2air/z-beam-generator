#!/usr/bin/env python3
"""
Universal Image Generator

⚠️  DEPRECATED (November 30, 2025):
    This module is deprecated and will be removed in a future version.
    
    Use ImagePromptOrchestrator + SharedPromptBuilder instead:
    
        from shared.image.orchestrator import ImagePromptOrchestrator
        from shared.image.utils.prompt_builder import SharedPromptBuilder
        
        prompt_builder = SharedPromptBuilder(prompts_dir=Path('prompts/shared'))
        orchestrator = ImagePromptOrchestrator(
            domain='materials',
            prompt_builder=prompt_builder
        )
        result = orchestrator.generate_hero_prompt(
            identifier='Aluminum',
            research_data={...},
            material_properties={...},
            config=config
        )
    
    The new architecture is:
    - SharedPromptBuilder: Handles all template loading, variable replacement, optimization
    - ImagePromptOrchestrator: 3-stage pipeline (Research → Assembly → Validation)
    - UnifiedValidator: Single validator for all stages

ORIGINAL DOCSTRING:
Domain-agnostic image generation engine that loads domain-specific prompts
and has access to domain data (materials, contaminants, applications, etc.).

Author: AI Assistant
Date: November 27, 2025 (Deprecated: November 30, 2025)
"""

import warnings
import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Emit deprecation warning on import
warnings.warn(
    "UniversalImageGenerator is deprecated. Use ImagePromptOrchestrator + SharedPromptBuilder instead. "
    "See module docstring for migration guide.",
    DeprecationWarning,
    stacklevel=2
)

from shared.image.utils.prompt_builder import SharedPromptBuilder
from shared.image.validation.payload_validator import ImagePromptPayloadValidator
from shared.validation.errors import ConfigurationError, GenerationError

logger = logging.getLogger(__name__)


@dataclass
class ImagePrompt:
    """Result of image prompt generation"""
    prompt: str
    image_type: str
    domain: str
    identifier: str
    output_path: str
    metadata: Dict[str, Any]


class UniversalImageGenerator:
    """
    Universal image generator that works across all domains.
    
    Loads domain-specific prompts from domains/{domain}/image/prompts/
    Accesses domain data via domain-specific data loaders
    Applies universal validation and optimization
    """
    
    def __init__(
        self,
        domain: str,
        api_key: Optional[str] = None,
        config_override: Optional[Dict] = None
    ):
        """
        Initialize universal image generator for a domain.
        
        Args:
            domain: Domain name (materials, contaminants, applications, regions, thesaurus)
            api_key: Optional API key for research/generation
            config_override: Optional config overrides
            
        Raises:
            ConfigurationError: If domain prompts/config not found
        """
        self.domain = domain
        self.api_key = api_key
        
        # Validate domain exists
        self.domain_path = Path(f"domains/{domain}")
        if not self.domain_path.exists():
            raise ConfigurationError(f"Domain not found: {domain}")
        
        # Load domain configuration
        self.config = self._load_domain_config()
        if config_override:
            self.config.update(config_override)
        
        # Initialize validator only (no prompt builder needed - we use templates directly)
        self.validator = ImagePromptPayloadValidator()
        
        # Load domain data loaders
        self.data_loader = self._initialize_data_loader()
        
        logger.info(f"✅ UniversalImageGenerator initialized for domain: {domain}")
    
    def _load_domain_config(self) -> Dict[str, Any]:
        """
        Load domain-specific image configuration.
        
        Returns:
            Configuration dictionary
            
        Raises:
            ConfigurationError: If config file missing or invalid
        """
        config_path = self.domain_path / "image" / "config.yaml"
        
        if not config_path.exists():
            raise ConfigurationError(
                f"Image config not found: {config_path}\n"
                f"Create domains/{self.domain}/image/config.yaml with image_types, "
                f"variables, and output patterns."
            )
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Validate required keys
        required = ['domain', 'image_types', 'output_pattern']
        missing = [k for k in required if k not in config]
        if missing:
            raise ConfigurationError(
                f"Missing required keys in {config_path}: {missing}"
            )
        
        logger.info(f"📋 Loaded config: {len(config.get('image_types', {}))} image types")
        return config
    
    def _initialize_data_loader(self):
        """
        Initialize domain-specific data loader.
        
        Returns:
            Domain data loader instance
        """
        # Dynamic import based on domain
        if self.domain == 'materials':
            from domains.materials.materials_cache import load_materials, get_material_by_name
            return MaterialsDataLoader()
        elif self.domain == 'contaminants':
            from domains.contaminants.library import ContaminantLibrary
            return ContaminantsDataLoader()
        elif self.domain == 'applications':
            # TODO: Implement applications data loader
            return GenericDataLoader(self.domain)
        elif self.domain == 'regions':
            # TODO: Implement regions data loader
            return GenericDataLoader(self.domain)
        else:
            return GenericDataLoader(self.domain)
    
    def generate(
        self,
        identifier: str,
        image_type: str,
        **kwargs
    ) -> ImagePrompt:
        """
        Generate image prompt for any domain.
        
        Args:
            identifier: Domain-specific identifier
                - Materials: material name (e.g., "Aluminum")
                - Contaminants: contaminant ID (e.g., "rust-oxidation")
                - Applications: application name (e.g., "aerospace-cleaning")
                - Regions: region name (e.g., "europe")
            image_type: Type of image (hero, contamination, before_after, etc.)
            **kwargs: Additional domain-specific parameters
            
        Returns:
            ImagePrompt with prompt text and metadata
            
        Raises:
            ConfigurationError: If image_type not configured
            GenerationError: If prompt generation fails
        """
        logger.info(f"🎨 Generating {image_type} image for {self.domain}/{identifier}")
        
        # Validate image_type exists in config
        if image_type not in self.config['image_types']:
            available = list(self.config['image_types'].keys())
            raise ConfigurationError(
                f"Unknown image_type '{image_type}' for domain '{self.domain}'. "
                f"Available: {available}"
            )
        
        # Get image type configuration
        image_config = self.config['image_types'][image_type]
        
        # Load domain data for identifier
        domain_data = self.data_loader.load(identifier)
        
        # Load domain-specific prompt template
        template = self._load_prompt_template(image_type, image_config)
        
        # Load research data if required
        research_data = None
        if image_config.get('requires_research', False):
            research_data = self._load_research(identifier, image_type, **kwargs)
        
        # Build prompt variables from domain data + kwargs
        variables = self._build_variables(domain_data, research_data, **kwargs)
        
        # Generate prompt using template + variables
        prompt = self._render_template(template, variables)
        
        # Apply universal validation and optimization
        validated_prompt = self._validate_and_optimize(prompt, image_type)
        
        # Build output path
        output_path = self._build_output_path(identifier, image_type)
        
        # Create result
        result = ImagePrompt(
            prompt=validated_prompt,
            image_type=image_type,
            domain=self.domain,
            identifier=identifier,
            output_path=output_path,
            metadata={
                'domain_data': domain_data,
                'research_data': research_data,
                'variables': variables,
                'config': image_config
            }
        )
        
        logger.info(f"✅ Generated prompt: {len(validated_prompt)} chars → {output_path}")
        return result
    
    def _load_prompt_template(
        self,
        image_type: str,
        image_config: Dict
    ) -> str:
        """
        Load prompt template (checks shared first, then domain-specific).
        
        Args:
            image_type: Type of image
            image_config: Image type configuration
            
        Returns:
            Template text
            
        Raises:
            ConfigurationError: If template file not found
        """
        template_file = image_config.get('template_file')
        if not template_file:
            raise ConfigurationError(
                f"No template_file specified for {self.domain}/{image_type}"
            )
        
        # Check shared templates first
        shared_template_path = Path('shared/image/templates') / template_file
        if shared_template_path.exists():
            with open(shared_template_path, 'r') as f:
                template = f.read()
            logger.info(f"📄 Loaded shared template: {template_file} ({len(template)} chars)")
            return template
        
        # Fall back to domain-specific template
        domain_template_path = self.domain_path / "image" / "templates" / template_file
        if domain_template_path.exists():
            with open(domain_template_path, 'r') as f:
                template = f.read()
            logger.info(f"📄 Loaded domain template: {template_file} ({len(template)} chars)")
            return template
        
        # Not found in either location
        raise ConfigurationError(
            f"Template file not found: {template_file}\n"
            f"Checked:\n"
            f"  - shared/image/templates/{template_file}\n"
            f"  - domains/{self.domain}/image/templates/{template_file}"
        )
    
    def _load_research(
        self,
        identifier: str,
        image_type: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Load research data for identifier (if domain supports it).
        
        Args:
            identifier: Domain identifier
            image_type: Image type
            **kwargs: Additional parameters
            
        Returns:
            Research data dictionary or None
        """
        # Domain-specific research logic
        if self.domain == 'materials':
            return self._load_materials_research(identifier, **kwargs)
        elif self.domain == 'contaminants':
            return self._load_contaminants_research(identifier, **kwargs)
        else:
            return None
    
    def _load_materials_research(
        self,
        material_name: str,
        contaminant: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Load contamination research for material using YAML data (ZERO API calls)"""
        if not contaminant:
            return {}
        
        try:
            # Use ContaminationPatternSelector (reads from Contaminants.yaml, no API calls)
            from domains.materials.image.research.contamination_pattern_selector import (
                ContaminationPatternSelector
            )
            
            selector = ContaminationPatternSelector()
            result = selector.get_patterns_for_image_gen(
                material_name=material_name,
                num_patterns=3
            )
            
            return result
        except Exception as e:
            logger.warning(f"⚠️  Research failed: {e}")
            return {}
    
    def _load_contaminants_research(
        self,
        contaminant_id: str,
        material: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Load visual appearance research for contaminant"""
        try:
            from domains.contaminants.research.visual_appearance_researcher import (
                VisualAppearanceResearcher
            )
            
            if not material:
                logger.warning("⚠️  Material required for contaminant research")
                return {}
            
            researcher = VisualAppearanceResearcher(api_key=self.api_key)
            visual_data = researcher.research_contaminant_appearance(
                contaminant_id,
                material
            )
            
            return visual_data
        except Exception as e:
            logger.warning(f"⚠️  Research failed: {e}")
            return {}
    
    def _build_variables(
        self,
        domain_data: Dict,
        research_data: Optional[Dict],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Build template variables from domain data + research + kwargs.
        
        Args:
            domain_data: Data from domain data loader
            research_data: Research data (if available)
            **kwargs: Additional parameters
            
        Returns:
            Variables dictionary for template rendering
        """
        variables = {}
        
        # Add domain data
        variables.update(domain_data)
        
        # Add research data
        if research_data:
            variables.update(research_data)
        
        # Add kwargs (overrides)
        variables.update(kwargs)
        
        # Add domain name
        variables['domain'] = self.domain
        
        return variables
    
    def _render_template(
        self,
        template: str,
        variables: Dict[str, Any]
    ) -> str:
        """
        Render prompt template with variables.
        
        Args:
            template: Template text with {variable} placeholders
            variables: Variables dictionary
            
        Returns:
            Rendered prompt
        """
        # Simple string formatting (can be enhanced with Jinja2 if needed)
        try:
            prompt = template.format(**variables)
            return prompt
        except KeyError as e:
            raise GenerationError(
                f"Missing template variable: {e}\n"
                f"Available variables: {list(variables.keys())}"
            )
    
    def _validate_and_optimize(
        self,
        prompt: str,
        image_type: str
    ) -> str:
        """
        Apply universal validation and optimization.
        
        Args:
            prompt: Generated prompt
            image_type: Image type
            
        Returns:
            Validated and optimized prompt
        """
        # Run universal validation
        validation_result = self.validator.validate(prompt)
        
        if not validation_result['valid']:
            logger.warning(f"⚠️  Validation issues: {validation_result['issues']}")
            
            # Auto-fix if possible
            if validation_result.get('can_fix', False):
                prompt = validation_result.get('fixed_prompt', prompt)
                logger.info("✅ Auto-fixed validation issues")
        
        # Optimize for Imagen length limits
        if len(prompt) > 3500:
            logger.info(f"📏 Optimizing prompt length: {len(prompt)} → target 3500")
            # Use prompt optimizer if needed
            # For now, just warn
            logger.warning("⚠️  Prompt may exceed optimal length")
        
        return prompt
    
    def _build_output_path(
        self,
        identifier: str,
        image_type: str
    ) -> str:
        """
        Build output path using domain configuration.
        
        Args:
            identifier: Domain identifier
            image_type: Image type
            
        Returns:
            Output file path
        """
        pattern = self.config['output_pattern']
        
        # Replace placeholders
        output_path = pattern.format(
            domain=self.domain,
            identifier=identifier.lower().replace(' ', '-'),
            image_type=image_type
        )
        
        return output_path


# ============================================================================
# Domain Data Loaders
# ============================================================================

class MaterialsDataLoader:
    """Data loader for materials domain"""
    
    def load(self, material_name: str) -> Dict[str, Any]:
        """Load material data from Materials.yaml"""
        from domains.materials.materials_cache import get_material_by_name
        
        material_data = get_material_by_name(material_name)
        if not material_data:
            raise GenerationError(f"Material not found: {material_name}")
        
        # Extract relevant fields for image generation - FAIL FAST if missing
        category = material_data.get('category')
        if not category:
            raise GenerationError(f"Material '{material_name}' missing required 'category' field")
        
        return {
            'material_name': material_name,
            'category': category,
            'properties': material_data.get('properties', {}),
            'surface_finish': material_data.get('surface_finish'),  # None if missing
            'reflectivity': material_data.get('reflectivity'),  # None if missing
            'color': material_data.get('color')  # None if missing
        }


class ContaminantsDataLoader:
    """Data loader for contaminants domain"""
    
    def load(self, contaminant_id: str) -> Dict[str, Any]:
        """Load contaminant data from Contaminants.yaml"""
        from domains.contaminants.library import ContaminantLibrary
        
        library = ContaminantLibrary()
        contaminant = library.get_contaminant(contaminant_id)
        
        if not contaminant:
            raise GenerationError(f"Contaminant not found: {contaminant_id}")
        
        # Extract relevant fields
        return {
            'contaminant_name': contaminant.name,
            'contaminant_id': contaminant_id,
            'description': contaminant.description,
            'removal_mechanism': getattr(contaminant, 'removal_mechanism', 'Unknown'),
            'difficulty': getattr(contaminant, 'difficulty', 'Unknown')
        }


class GenericDataLoader:
    """Generic data loader for domains without custom loaders"""
    
    def __init__(self, domain: str):
        self.domain = domain
    
    def load(self, identifier: str) -> Dict[str, Any]:
        """Return basic identifier data"""
        return {
            'identifier': identifier,
            'domain': self.domain
        }
