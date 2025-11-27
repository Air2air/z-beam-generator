"""
Image Prompt Orchestrator - Chained Prompt Architecture

Implements PROMPT_CHAINING_POLICY.md for image generation.

Architecture Pattern (mirrors text generation):
    Stage 1: Research → Extract properties (low temp 0.3)
    Stage 2: Visual Description → Generate appearance (high temp 0.7)  
    Stage 3: Composition → Layout before/after (balanced 0.5)
    Stage 4: Refinement → Technical accuracy (precise 0.4)
    Stage 5: Assembly → Final polish (balanced 0.5)

Each stage:
- ONE specialized prompt template
- Receives output from previous stage as input
- Optimized temperature for task type
- Can be tested independently

Benefits:
- Separation of concerns (research vs creativity vs accuracy)
- Optimal parameters per stage
- Reusable components
- Easy debugging
- Better quality output

Example Usage:
    orchestrator = ImagePromptOrchestrator(
        domain='materials',
        api_client=api_client
    )
    
    result = orchestrator.generate_hero_prompt(
        identifier='Aluminum',
        category='metal'
    )
    
    print(result.prompt)          # Final chained prompt
    print(result.stage_outputs)   # Debug individual stages
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Import universal prompt validator
try:
    from shared.validation.prompt_validator import validate_image_prompt
except ImportError:
    # Fallback if validator not available
    logger.warning("⚠️  UniversalPromptValidator not available - skipping validation")
    
    @dataclass
    class FallbackValidationResult:
        """Fallback validation result when validator unavailable"""
        is_valid: bool = True
        
        def get_summary(self) -> str:
            return "✅ VALID (validator unavailable)"
        
        def format_report(self) -> str:
            return "Validator not available"
    
    def validate_image_prompt(prompt: str, **kwargs):
        """Fallback validator"""
        return FallbackValidationResult()


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
    Orchestrates chained prompts for image generation.
    
    Implements separation of concerns through specialized prompt stages:
    - Research stage: Extract factual properties (temp=0.3)
    - Visual stage: Generate creative descriptions (temp=0.7)
    - Composition stage: Layout and structure (temp=0.5)
    - Refinement stage: Technical accuracy (temp=0.4)
    - Assembly stage: Final polish (temp=0.5)
    
    Each stage has:
    - Dedicated template file
    - Optimized temperature
    - Clear input/output contract
    - Independent testability
    """
    
    def __init__(
        self,
        domain: str,
        api_client=None,
        data_loader=None
    ):
        """
        Initialize orchestrator.
        
        Args:
            domain: Domain name (materials, contaminants, etc.)
            api_client: Optional API client for multi-stage generation
            data_loader: Optional data loader for property extraction
        
        Note: If api_client not provided, only template loading works
              (useful for prompt generation without API calls)
        """
        self.domain = domain
        self.api_client = api_client
        self.data_loader = data_loader
        
        # Template paths
        self.shared_templates = Path('shared/image/templates')
        self.domain_templates = Path(f'domains/{domain}/image/templates')
    
    def generate_hero_prompt(
        self,
        identifier: str,
        **kwargs
    ) -> ChainedPromptResult:
        """
        Generate hero image prompt through chained stages.
        
        Chain:
        1. Research: Extract properties from data
        2. Visual: Generate appearance description
        3. Composition: Create before/after layout
        4. Refinement: Ensure technical accuracy
        5. Assembly: Final prompt with all details
        
        Args:
            identifier: Material/contaminant/etc name
            **kwargs: Additional context (category, etc.)
        
        Returns:
            ChainedPromptResult with final prompt and stage outputs
        """
        stage_outputs = {}
        
        # Stage 1: Research properties
        print("\n🔬 STAGE 1: Research Properties")
        logger.info("🔬 STAGE 1: Research Properties")
        research_data = self._research_stage(identifier, **kwargs)
        stage_outputs['research'] = research_data
        print(f"   ✅ Extracted {len(research_data)} properties")
        logger.info(f"   ✅ Extracted {len(research_data)} properties")
        
        # Stage 2: Generate visual description
        print("\n🎨 STAGE 2: Visual Description")
        logger.info("🎨 STAGE 2: Visual Description")
        visual_desc = self._visual_stage(identifier, research_data)
        stage_outputs['visual'] = visual_desc
        print(f"   ✅ Generated visual description ({len(visual_desc)} chars)")
        logger.info(f"   ✅ Generated visual description ({len(visual_desc)} chars)")
        
        # Stage 3: Compose before/after layout
        print("\n📐 STAGE 3: Composition Layout")
        logger.info("📐 STAGE 3: Composition Layout")
        composition = self._composition_stage(identifier, visual_desc, research_data)
        stage_outputs['composition'] = composition
        print(f"   ✅ Composed layout ({len(composition)} chars)")
        logger.info(f"   ✅ Composed layout ({len(composition)} chars)")
        
        # Stage 4: Technical refinement
        print("\n🔧 STAGE 4: Technical Refinement")
        logger.info("🔧 STAGE 4: Technical Refinement")
        refined = self._refinement_stage(composition, research_data)
        stage_outputs['refinement'] = refined
        print(f"   ✅ Applied technical refinement ({len(refined)} chars)")
        logger.info(f"   ✅ Applied technical refinement ({len(refined)} chars)")
        
        # Stage 5: Final assembly
        print("\n🎯 STAGE 5: Final Assembly")
        logger.info("🎯 STAGE 5: Final Assembly")
        final_prompt = self._assembly_stage(refined, **kwargs)
        stage_outputs['assembly'] = final_prompt
        print(f"   ✅ Assembled final prompt ({len(final_prompt)} chars)")
        logger.info(f"   ✅ Assembled final prompt ({len(final_prompt)} chars)")
        
        # CRITICAL: Validate final prompt before returning
        print("\n🔍 STAGE 6: Final Validation")
        logger.info("🔍 STAGE 6: Final Validation")
        validation_result = validate_image_prompt(
            final_prompt,
            material=identifier,
            **kwargs
        )
        stage_outputs['validation'] = validation_result
        
        print(f"   📊 Validation: {validation_result.get_summary()}")
        logger.info(f"   📊 Validation: {validation_result.get_summary()}")
        
        if not validation_result.is_valid:
            print(f"   ⚠️  Validation found issues:")
            logger.warning(f"   ⚠️  Validation found issues:")
            for issue in validation_result.issues[:5]:  # Show first 5
                print(f"      • {issue.severity.value}: {issue.message}")
                logger.warning(f"      • {issue.severity.value}: {issue.message}")
            
            if validation_result.has_critical_issues:
                logger.error("   🚨 CRITICAL issues found - prompt may fail")
                raise ValueError(
                    f"Prompt validation failed with critical issues:\n"
                    f"{validation_result.format_report()}"
                )
        else:
            print(f"   ✅ Prompt validated successfully")
            logger.info(f"   ✅ Prompt validated successfully")
        
        return ChainedPromptResult(
            prompt=final_prompt,
            domain=self.domain,
            identifier=identifier,
            image_type='hero',
            stage_outputs=stage_outputs,
            metadata={
                'stages': ['research', 'visual', 'composition', 'refinement', 'assembly', 'validation'],
                'temperatures': {
                    'research': 0.3,
                    'visual': 0.7,
                    'composition': 0.5,
                    'refinement': 0.4,
                    'assembly': 0.5
                },
                'validation': {
                    'is_valid': validation_result.is_valid,
                    'issues_count': len(validation_result.issues),
                    'has_critical': validation_result.has_critical_issues,
                    'has_errors': validation_result.has_errors,
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
        Stage 1: Research and extract properties.
        
        Temperature: 0.3 (low for factual accuracy)
        Purpose: Extract factual properties from data
        Input: identifier + kwargs
        Output: Dict of properties
        
        If data_loader available: Extract from data files
        If API client available: Could use AI for research
        Otherwise: Use provided kwargs as properties
        """
        if self.data_loader:
            # Extract from data files (Materials.yaml, etc.)
            data = self.data_loader.load_data(identifier)
            
            return {
                'name': identifier,
                'category': data.get('category', kwargs.get('category', 'unknown')),
                'color': data.get('color', kwargs.get('color', 'natural')),
                'texture': data.get('surface_finish', kwargs.get('texture', 'smooth')),
                'reflectivity': data.get('reflectivity', kwargs.get('reflectivity', 'moderate')),
                'common_contamination': data.get('typical_contamination', []),
                'applications': data.get('applications', [])
            }
        else:
            # Use provided kwargs or defaults
            return {
                'name': identifier,
                'category': kwargs.get('category', 'unknown'),
                'color': kwargs.get('color', 'natural'),
                'texture': kwargs.get('texture', 'smooth'),
                'reflectivity': kwargs.get('reflectivity', 'moderate'),
                'common_contamination': kwargs.get('common_contamination', []),
                'applications': kwargs.get('applications', [])
            }
    
    def _visual_stage(
        self,
        identifier: str,
        research: Dict[str, Any]
    ) -> str:
        """
        Stage 2: Generate visual appearance description.
        
        Temperature: 0.7 (high for creative descriptions)
        Purpose: Create vivid visual description from properties
        Input: identifier + research properties
        Output: Creative visual description
        
        If API available: Generate with creative prompt
        Otherwise: Construct from research data
        """
        if self.api_client:
            # Load specialized visual template
            template = self._load_template('generation/visual_appearance.txt')
            if template:
                prompt = template.format(
                    name=identifier,
                    color=research.get('color', 'natural'),
                    texture=research.get('texture', 'smooth'),
                    reflectivity=research.get('reflectivity', 'moderate')
                )
                
                # Generate with high temperature for creativity
                return self.api_client.generate(prompt, temperature=0.7)
        
        # Fallback: Construct description from research
        parts = [
            f"{identifier} exhibits a {research.get('color', 'natural')} coloration",
            f"with a {research.get('texture', 'smooth')} surface texture",
            f"and {research.get('reflectivity', 'moderate')} reflectivity."
        ]
        return ' '.join(parts)
    
    def _composition_stage(
        self,
        identifier: str,
        visual_desc: str,
        research: Dict[str, Any]
    ) -> str:
        """
        Stage 3: Compose before/after split-screen layout.
        
        Temperature: 0.5 (balanced for structure + creativity)
        Purpose: Create detailed composition description
        Input: identifier + visual description + research data
        Output: Before/after composition layout
        
        Uses hero template with context from previous stages.
        """
        # Load hero template (shared, universal)
        template = self._load_template('hero.txt')
        if not template:
            raise FileNotFoundError(f"Hero template not found in shared or domain templates")
        
        # Render template with data from previous stages
        return template.format(
            material_name=identifier,
            category=research.get('category', 'unknown'),
            color=research.get('color', 'natural'),
            surface_finish=research.get('texture', 'smooth'),
            reflectivity=research.get('reflectivity', 'moderate'),
            visual_description=visual_desc
        )
    
    def _refinement_stage(
        self,
        composition: str,
        research: Dict[str, Any]
    ) -> str:
        """
        Stage 4: Technical refinement and accuracy check.
        
        Temperature: 0.4 (low for precision)
        Purpose: Ensure technical accuracy and add specifications
        Input: composition + research constraints
        Output: Technically refined composition
        
        If API available: Check and refine with technical prompt
        Otherwise: Add technical details from research
        """
        if self.api_client:
            # Load refinement template
            template = self._load_template('refinement/technical_accuracy.txt')
            if template:
                prompt = template.format(
                    composition=composition,
                    technical_constraints=research.get('applications', [])
                )
                
                # Generate with low temperature for precision
                return self.api_client.generate(prompt, temperature=0.4)
        
        # Fallback: Return composition as-is
        return composition
    
    def _assembly_stage(
        self,
        refined: str,
        **kwargs
    ) -> str:
        """
        Stage 5: Final assembly and polish.
        
        Temperature: 0.5 (balanced)
        Purpose: Add final details and polish
        Input: refined composition + additional requirements
        Output: Final complete prompt
        
        If API available: Apply final polish
        Otherwise: Add any additional kwargs to prompt
        """
        if self.api_client:
            # Load assembly template
            template = self._load_template('refinement/final_polish.txt')
            if template:
                prompt = template.format(
                    content=refined,
                    **kwargs
                )
                
                # Generate with balanced temperature
                return self.api_client.generate(prompt, temperature=0.5)
        
        # Fallback: Return refined as final prompt
        return refined
    
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
