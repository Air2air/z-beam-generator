"""
Image Prompt Orchestrator - Chained Prompt Architecture

Implements PROMPT_CHAINING_POLICY.md for image generation.

SIMPLIFIED ARCHITECTURE (November 30, 2025):
    Stage 1: RESEARCH → Load/use provided research data
    Stage 2: ASSEMBLY → SharedPromptBuilder creates comprehensive prompt
    Stage 3: VALIDATION → UnifiedValidator checks prompt quality

Each stage:
- ONE clear responsibility
- Receives output from previous stage as input
- Can be tested independently

Benefits:
- Separation of concerns
- Clear data flow
- Easy debugging
- SharedPromptBuilder handles all prompt assembly complexity
- UnifiedValidator handles all validation (consolidated)

Legacy Note:
    Previous 6-stage design had stages 2-4 (Visual/Composition/Refinement)
    that were no-ops without an API client. Simplified to 3 actual stages.

Example Usage:
    from shared.image.utils.prompt_builder import SharedPromptBuilder
    
    prompt_builder = SharedPromptBuilder(prompts_dir=Path('prompts/shared'))
    orchestrator = ImagePromptOrchestrator(
        domain='materials',
        prompt_builder=prompt_builder
    )
    
    result = orchestrator.generate_hero_prompt(
        identifier='Aluminum',
        research_data=my_research_data,  # Pre-gathered research data
        material_properties=props,
        config=config
    )
    
    print(result.prompt)          # Final prompt from SharedPromptBuilder
    print(result.stage_outputs)   # Debug individual stages
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

# FAIL-FAST: Import unified validator - validation is REQUIRED per copilot-instructions.md
# No try/except fallback - if validator unavailable, fail immediately
from shared.validation.validator import (
    validate_prompt_quick,
    ValidationReport
)

logger = logging.getLogger(__name__)


def validate_image_prompt(prompt: str, **kwargs) -> ValidationReport:
    """Validate image prompt using unified validator."""
    return validate_prompt_quick(prompt, material=kwargs.get('material', ''))


@dataclass
class ChainedPromptResult:
    """Result from chained prompt generation"""
    prompt: str
    domain: str
    identifier: str
    image_type: str
    stage_outputs: Dict[str, Any]  # Debug: output from each stage
    metadata: Dict[str, Any]


class ImagePromptOrchestrator:
    """
    Orchestrates 3-stage prompt generation for images.
    
    SIMPLIFIED ARCHITECTURE (November 30, 2025):
    - Stage 1: RESEARCH - Load/use provided research data
    - Stage 2: ASSEMBLY - SharedPromptBuilder creates comprehensive prompt
    - Stage 3: VALIDATION - UnifiedValidator checks prompt quality
    
    SharedPromptBuilder handles all the complexity:
    - 4-layer templates (base + physics + contamination + micro)
    - Variable replacements (material, patterns, visual properties)
    - Prompt optimization for Imagen API limits
    - Research data retention verification
    
    UnifiedValidator handles all validation:
    - Length limits
    - Contradictions and logic
    - Material-contamination compatibility
    - Physics plausibility
    """
    
    def __init__(
        self,
        domain: str,
        api_client=None,
        data_loader=None,
        prompt_builder=None
    ):
        """
        Initialize orchestrator.
        
        Args:
            domain: Domain name (materials, contaminants, etc.)
            api_client: Optional API client (rarely used)
            data_loader: Optional data loader for property extraction
            prompt_builder: SharedPromptBuilder for assembly stage (RECOMMENDED)
        """
        self.domain = domain
        self.api_client = api_client
        self.data_loader = data_loader
        self.prompt_builder = prompt_builder
        
        # Template paths (fallback if no prompt_builder)
        self.shared_templates = Path('shared/image/templates')
        self.domain_templates = Path(f'domains/{domain}/image/templates')
    
    def generate_hero_prompt(
        self,
        identifier: str,
        research_data: Optional[Dict[str, Any]] = None,
        material_properties: Optional[Dict[str, Any]] = None,
        config: Optional[Any] = None,
        **kwargs
    ) -> ChainedPromptResult:
        """
        Generate hero image prompt through 3-stage pipeline.
        
        SIMPLIFIED CHAIN (November 30, 2025):
        1. RESEARCH: Use provided research_data or extract from data_loader
        2. ASSEMBLY: SharedPromptBuilder creates comprehensive prompt
        3. VALIDATION: UnifiedValidator checks prompt quality
        
        Args:
            identifier: Material/contaminant/etc name
            research_data: Pre-gathered research data (contamination, shape, etc.)
            material_properties: Material properties from Materials.yaml
            config: Domain-specific config object (e.g., MaterialImageConfig)
            **kwargs: Additional context (category, etc.)
        
        Returns:
            ChainedPromptResult with final prompt and stage outputs
        """
        stage_outputs = {}
        
        # ═══════════════════════════════════════════════════════════════════════
        # STAGE 1: RESEARCH - Load or use provided research data
        # ═══════════════════════════════════════════════════════════════════════
        print("\n🔬 STAGE 1/3: Research Data")
        logger.info("🔬 STAGE 1/3: Research Data")
        
        if research_data:
            # Use pre-gathered research data (from MaterialImageGenerator)
            internal_research = research_data.copy()
            print(f"   ✅ Using provided research data ({len(internal_research)} keys)")
            logger.info(f"   ✅ Using provided research data ({len(internal_research)} keys)")
        else:
            # Extract properties from data_loader or kwargs
            internal_research = self._research_stage(identifier, **kwargs)
            print(f"   ✅ Extracted {len(internal_research)} properties")
            logger.info(f"   ✅ Extracted {len(internal_research)} properties")
        stage_outputs['research'] = internal_research
        
        # ═══════════════════════════════════════════════════════════════════════
        # STAGE 2: ASSEMBLY - SharedPromptBuilder creates comprehensive prompt
        # ═══════════════════════════════════════════════════════════════════════
        print("\n🎯 STAGE 2/3: Prompt Assembly")
        logger.info("🎯 STAGE 2/3: Prompt Assembly")
        
        if self.prompt_builder and material_properties is not None:
            # Use SharedPromptBuilder for comprehensive prompt generation
            print("   📦 Using SharedPromptBuilder (4-layer templates)")
            logger.info("   📦 Using SharedPromptBuilder (4-layer templates)")
            final_prompt = self.prompt_builder.build_generation_prompt(
                material_name=identifier,
                material_properties=material_properties,
                config=config,
                research_data=internal_research
            )
            print(f"   ✅ Assembled prompt: {len(final_prompt)} chars")
            logger.info(f"   ✅ Assembled prompt: {len(final_prompt)} chars")
        else:
            # Fallback to legacy assembly (template-based)
            print("   ⚠️  No prompt_builder - using legacy assembly")
            logger.warning("   ⚠️  No prompt_builder - using legacy assembly")
            final_prompt = self._legacy_assembly(identifier, internal_research, **kwargs)
            print(f"   ✅ Legacy assembly: {len(final_prompt)} chars")
            logger.info(f"   ✅ Legacy assembly: {len(final_prompt)} chars")
        stage_outputs['assembly'] = final_prompt
        
        # ═══════════════════════════════════════════════════════════════════════
        # STAGE 3: VALIDATION - UnifiedValidator checks prompt quality
        # ═══════════════════════════════════════════════════════════════════════
        print("\n🔍 STAGE 3/3: Validation")
        logger.info("🔍 STAGE 3/3: Validation")
        
        validation_result = validate_image_prompt(
            final_prompt,
            material=identifier,
            **kwargs
        )
        stage_outputs['validation'] = validation_result
        
        print(f"   📊 Result: {validation_result.status.value}")
        logger.info(f"   📊 Result: {validation_result.status.value}")
        
        # Check validation status
        is_valid = getattr(validation_result, 'is_valid', True)
        if hasattr(validation_result, 'status'):
            from shared.validation.validator import ValidationStatus
            is_valid = validation_result.status in (ValidationStatus.PASS, ValidationStatus.WARN)
        
        if not is_valid:
            print("   ⚠️  Issues found:")
            logger.warning("   ⚠️  Issues found:")
            for issue in validation_result.issues[:5]:
                sev_val = issue.severity.value if hasattr(issue.severity, 'value') else str(issue.severity)
                print(f"      • {sev_val}: {issue.message}")
                logger.warning(f"      • {sev_val}: {issue.message}")
            
            if getattr(validation_result, 'has_critical', False):
                logger.error("   🚨 CRITICAL issues - prompt may fail")
                raise ValueError(
                    f"Prompt validation failed:\n"
                    f"{validation_result.to_report() if hasattr(validation_result, 'to_report') else str(validation_result)}"
                )
        else:
            print("   ✅ Validation passed")
            logger.info("   ✅ Validation passed")
        
        return ChainedPromptResult(
            prompt=final_prompt,
            domain=self.domain,
            identifier=identifier,
            image_type='hero',
            stage_outputs=stage_outputs,
            metadata={
                'stages': ['research', 'assembly', 'validation'],
                'validation': {
                    'is_valid': is_valid,
                    'issues_count': len(validation_result.issues),
                    'has_critical': getattr(validation_result, 'has_critical', False),
                    'prompt_length': validation_result.prompt_length,
                    'estimated_tokens': validation_result.estimated_tokens
                }
            }
        )
    
    def _research_stage(
        self,
        identifier: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Stage 1: Extract properties from data sources.
        
        FAIL-FAST: Requires either data_loader with valid data OR complete kwargs.
        No hardcoded defaults - missing data raises errors.
        
        Priority:
        1. Use data_loader if available
        2. Fall back to provided kwargs (must be complete)
        
        Returns basic property dict for prompt building.
        
        Raises:
            ValueError: If required properties are missing
        """
        if self.data_loader:
            # Extract from data files (Materials.yaml, etc.)
            data = self.data_loader.load_data(identifier)
            
            # FAIL-FAST: Require category (essential for prompt generation)
            category = data.get('category') or kwargs.get('category')
            if not category:
                raise ValueError(
                    f"FAIL-FAST: 'category' is required for {identifier}. "
                    f"Add to data source or provide via kwargs."
                )
            
            return {
                'name': identifier,
                'category': category,
                # Optional properties - use None instead of fake defaults
                'color': data.get('color') or kwargs.get('color'),
                'texture': data.get('surface_finish') or kwargs.get('texture'),
                'reflectivity': data.get('reflectivity') or kwargs.get('reflectivity'),
                'common_contamination': data.get('typical_contamination') or [],
                'applications': data.get('applications') or []
            }
        else:
            # FAIL-FAST: Require category when no data_loader
            category = kwargs.get('category')
            if not category:
                raise ValueError(
                    f"FAIL-FAST: 'category' is required for {identifier}. "
                    f"Provide via kwargs or configure a data_loader."
                )
            
            return {
                'name': identifier,
                'category': category,
                # Optional properties - use None instead of fake defaults
                'color': kwargs.get('color'),
                'texture': kwargs.get('texture'),
                'reflectivity': kwargs.get('reflectivity'),
                'common_contamination': kwargs.get('common_contamination', []),
                'applications': kwargs.get('applications', [])
            }
    
    def _legacy_assembly(
        self,
        identifier: str,
        research: Dict[str, Any],
        **kwargs
    ) -> str:
        """
        Legacy assembly: Template-based prompt generation when no SharedPromptBuilder.
        
        DEPRECATED: Use SharedPromptBuilder for comprehensive prompt generation.
        This method exists only for backward compatibility.
        
        FAIL-FAST: Raises error if template not found or required variables missing.
        """
        logger.warning("⚠️  Using legacy assembly - prefer SharedPromptBuilder")
        print("⚠️  Using legacy assembly - prefer SharedPromptBuilder")
        
        # Load hero template - FAIL-FAST if not found
        template = self._load_template('hero.txt')
        if not template:
            raise FileNotFoundError(
                f"FAIL-FAST: hero.txt template not found in shared or domain templates. "
                f"Searched: {self.shared_templates}/hero.txt, {self.domain_templates}/hero.txt"
            )
        
        # FAIL-FAST: Require category in research data
        if 'category' not in research or not research['category']:
            raise ValueError(
                f"FAIL-FAST: 'category' is required in research data for {identifier}. "
                f"Got research keys: {list(research.keys())}"
            )
        
        # FAIL-FAST: Check for required template variables
        # color, texture, reflectivity are optional - use empty string if None
        color = research.get('color') or ''
        texture = research.get('texture') or ''
        reflectivity = research.get('reflectivity') or ''
        
        # Filter out kwargs that would conflict with explicit template vars
        filtered_kwargs = {k: v for k, v in kwargs.items() 
                           if k not in ('material_name', 'category', 'color', 
                                       'surface_finish', 'reflectivity')}
        try:
            return template.format(
                material_name=identifier,
                category=research['category'],
                color=color,
                surface_finish=texture,
                reflectivity=reflectivity,
                **filtered_kwargs
            )
        except KeyError as e:
            raise KeyError(
                f"FAIL-FAST: Template variable {e} missing for {identifier}. "
                f"Available research: {list(research.keys())}, kwargs: {list(kwargs.keys())}"
            )
    
    def _load_template(self, template_file: str) -> Optional[str]:
        """
        Load template following hierarchy: shared → domain → error.
        
        Args:
            template_file: Template filename (e.g., 'hero.txt' or 'research/properties.txt')
        
        Returns:
            Template content or None if not found
        """
        # Check shared templates first (universal)
        shared_path = self.shared_templates / template_file
        if shared_path.exists():
            logger.info(f"   📄 Loading shared template: {template_file}")
            return shared_path.read_text()
        
        # Fall back to domain-specific templates
        domain_path = self.domain_templates / template_file
        if domain_path.exists():
            logger.info(f"   📄 Loading domain template: {template_file}")
            return domain_path.read_text()
        
        # Not found in either location
        logger.warning(f"   ⚠️  Template not found: {template_file}")
        return None
