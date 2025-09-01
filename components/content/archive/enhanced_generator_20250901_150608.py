#!/usr/bin/env python3
"""
Enhanced Content Generator with Human-Like Validation Integration

Extends the existing content generator to include multi-pass generation
with human-like validation and automatic improvement.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from components.content.generator import ContentComponentGenerator, ComponentResult
from components.content.human_validator import HumanLikeValidator

logger = logging.getLogger(__name__)

class EnhancedContentGenerator(ContentComponentGenerator):
    """
    Enhanced content generator with integrated human-like validation.
    
    Features:
    - Multi-pass generation with validation feedback
    - Automatic content improvement prompts  
    - Human-likeness scoring and recommendations
    - Configurable validation thresholds
    """
    
    def __init__(self, enable_validation: bool = True, 
                 human_likeness_threshold: int = 80,
                 max_improvement_attempts: int = 2):
        """
        Initialize enhanced generator with validation options.
        
        Args:
            enable_validation: Whether to enable human-like validation
            human_likeness_threshold: Minimum score for content acceptance
            max_improvement_attempts: Maximum regeneration attempts
        """
        super().__init__()
        self.enable_validation = enable_validation
        self.human_likeness_threshold = human_likeness_threshold
        self.max_improvement_attempts = max_improvement_attempts
        self.validator = HumanLikeValidator() if enable_validation else None
        
        # Override validation threshold if provided
        if self.validator and human_likeness_threshold != 80:
            self.validator.validation_thresholds['human_likeness_threshold'] = human_likeness_threshold
    
    def generate(self, material_name: str, material_data: Dict,
                api_client=None, author_info: Optional[Dict] = None,
                frontmatter_data: Optional[Dict] = None,
                schema_fields: Optional[Dict] = None) -> ComponentResult:
        """
        Generate content with optional human-like validation and improvement.
        
        Workflow:
        1. Generate initial content using parent method
        2. If validation enabled, validate human-likeness
        3. If score below threshold, generate improvement prompt and retry
        4. Return best result with validation metadata
        """
        if not self.enable_validation:
            # Fallback to standard generation if validation disabled
            return super().generate(
                material_name, material_data, api_client, 
                author_info, frontmatter_data, schema_fields
            )
        
        if not api_client:
            return ComponentResult(
                component_type=self.component_type,
                success=False,
                content="",
                error_message="API client is required for enhanced content generation"
            )
        
        # Track generation attempts and results
        generation_attempts = []
        best_result = None
        best_score = 0
        
        # Initial generation attempt
        logger.info(f"Generating initial content for {material_name}")
        initial_result = super().generate(
            material_name, material_data, api_client,
            author_info, frontmatter_data, schema_fields
        )
        
        if not initial_result.success:
            return initial_result
        
        # Validate initial content
        validation_result = self.validator.validate_content(
            initial_result.content, material_name, author_info
        )
        
        score = validation_result.get('human_likeness_score', 0)
        generation_attempts.append({
            'attempt': 1,
            'score': score,
            'content_length': len(initial_result.content),
            'needs_improvement': validation_result.get('needs_regeneration', False)
        })
        
        best_result = initial_result
        best_score = score
        
        logger.info(f"Initial content score: {score}/100 for {material_name}")
        
        # Attempt improvements if needed and below threshold
        improvement_attempt = 0
        while (score < self.human_likeness_threshold and 
               improvement_attempt < self.max_improvement_attempts and
               validation_result.get('needs_regeneration', False)):
            
            improvement_attempt += 1
            logger.info(f"Attempting content improvement #{improvement_attempt} for {material_name}")
            
            # Generate improvement prompt
            improvement_prompt = self.validator.generate_improvement_prompt(
                validation_result, initial_result.content, material_name
            )
            
            if not improvement_prompt:
                logger.warning(f"No improvement prompt generated for {material_name}")
                break
            
            # Attempt improved generation
            try:
                improved_result = self._generate_improved_content(
                    improvement_prompt, material_name, material_data,
                    api_client, author_info
                )
                
                if improved_result.success:
                    # Validate improved content
                    improved_validation = self.validator.validate_content(
                        improved_result.content, material_name, author_info
                    )
                    
                    improved_score = improved_validation.get('human_likeness_score', 0)
                    
                    generation_attempts.append({
                        'attempt': improvement_attempt + 1,
                        'score': improved_score,
                        'content_length': len(improved_result.content),
                        'needs_improvement': improved_validation.get('needs_regeneration', False)
                    })
                    
                    logger.info(f"Improvement attempt {improvement_attempt} score: {improved_score}/100")
                    
                    # Keep best result
                    if improved_score > best_score:
                        best_result = improved_result
                        best_score = improved_score
                        validation_result = improved_validation
                        logger.info(f"New best score: {improved_score}/100 for {material_name}")
                    
                    # Update for next iteration
                    score = improved_score
                    
                else:
                    logger.warning(f"Improvement attempt {improvement_attempt} failed: {improved_result.error}")
                    
            except Exception as e:
                logger.error(f"Error during improvement attempt {improvement_attempt}: {e}")
                break
        
        # Enhance result metadata with validation information
        enhanced_metadata = best_result.metadata or {}
        enhanced_metadata.update({
            'human_likeness_validation': {
                'enabled': True,
                'final_score': best_score,
                'threshold': self.human_likeness_threshold,
                'passes_threshold': best_score >= self.human_likeness_threshold,
                'generation_attempts': generation_attempts,
                'total_attempts': len(generation_attempts),
                'validation_details': validation_result.get('category_scores', {}),
                'recommendations': validation_result.get('recommendations', []),
                'critical_issues': validation_result.get('critical_issues', [])
            }
        })
        
        return ComponentResult(
            component_type=self.component_type,
            success=best_result.success,
            content=best_result.content,
            error_message=best_result.error_message,
            metadata=enhanced_metadata
        )
    
    def _generate_improved_content(self, improvement_prompt: str, material_name: str,
                                 material_data: Dict, api_client, author_info: Dict) -> ComponentResult:
        """
        Generate improved content using the improvement prompt.
        
        Args:
            improvement_prompt: Specific prompt for content improvement
            material_name: Material being processed
            material_data: Material information
            api_client: API client for generation
            author_info: Author context
            
        Returns:
            ComponentResult with improved content
        """
        try:
            # Build persona-aware improvement prompt
            enhanced_improvement_prompt = self._build_persona_aware_improvement_prompt(
                improvement_prompt, material_name, author_info
            )
            
            # Use API client for improvement generation with persona context
            response = api_client.generate_simple(
                prompt=enhanced_improvement_prompt,
                system_prompt=self._get_persona_system_prompt(author_info),
                max_tokens=1500,
                temperature=0.8  # Higher temperature for more variety
            )
            
            if not response.success:
                return ComponentResult(
                    component_type=self.component_type,
                    success=False,
                    content="",
                    error_message=f"API failed during content improvement: {response.error}"
                )
            
            # Extract improved content from response
            improved_content = response.content.strip()
            
            # Apply persona-specific formatting if needed
            if improved_content and not improved_content.startswith('#'):
                improved_content = self._apply_persona_formatting(
                    improved_content, material_name, author_info
                )
            
            return ComponentResult(
                component_type=self.component_type,
                success=True,
                content=improved_content,
                metadata={
                    'generation_method': 'improvement_api',
                    'improvement_attempt': True,
                    'api_response_tokens': response.token_count
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating improved content for {material_name}: {e}")
            return ComponentResult(
                component_type=self.component_type,
                success=False,
                content="",
                error_message=f"Content improvement failed: {str(e)}"
            )
    
    def validate_existing_content(self, content: str, material_name: str = "",
                                author_info: Dict = None) -> Dict[str, Any]:
        """
        Validate existing content without regeneration.
        
        Args:
            content: Content to validate
            material_name: Material name for context
            author_info: Author information
            
        Returns:
            Validation results dictionary
        """
        if not self.validator:
            return {
                'success': False,
                'error': 'Validation is disabled'
            }
        
        return self.validator.validate_content(content, material_name, author_info)
    
    def set_validation_threshold(self, threshold: int):
        """Update the human-likeness threshold for validation."""
        self.human_likeness_threshold = threshold
        if self.validator:
            self.validator.validation_thresholds['human_likeness_threshold'] = threshold
    
    def enable_validation_mode(self, enabled: bool = True):
        """Enable or disable validation mode."""
        self.enable_validation = enabled
        if enabled and not self.validator:
            self.validator = HumanLikeValidator()
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get current validation configuration and statistics."""
        return {
            'validation_enabled': self.enable_validation,
            'human_likeness_threshold': self.human_likeness_threshold,
            'max_improvement_attempts': self.max_improvement_attempts,
            'validator_thresholds': self.validator.validation_thresholds if self.validator else None
        }
    
    def _build_persona_aware_improvement_prompt(self, improvement_prompt: str, 
                                              material_name: str, author_info: Dict) -> str:
        """Build improvement prompt that preserves persona characteristics."""
        if not author_info:
            return improvement_prompt
        
        author_id = author_info.get('id', 1)
        author_name = author_info.get('name', 'Expert')
        author_country = author_info.get('country', 'International')
        
        try:
            # Load persona configuration for this author
            from components.content.generator import load_persona_prompt
            persona_config = load_persona_prompt(author_id)
            prompt_key = author_country.lower()
            
            # Get persona-specific patterns
            persona_data = persona_config.get(f'{prompt_key}_persona', {})
            writing_style = persona_config.get('writing_style', {})
            language_patterns = persona_data.get('language_patterns', {})
            content_structure = persona_config.get('content_structure', {})
            
            # Build persona-aware improvement prompt
            persona_parts = [
                improvement_prompt,
                "",
                f"MAINTAIN AUTHOR PERSONA: {author_name} from {author_country}",
                f"PRESERVE WRITING STYLE: {writing_style.get('approach', 'professional')}",
            ]
            
            # Add language pattern requirements
            if language_patterns:
                persona_parts.extend([
                    "",
                    "PRESERVE THESE LANGUAGE PATTERNS:"
                ])
                signature_phrases = language_patterns.get('signature_phrases', [])
                if signature_phrases:
                    persona_parts.append(f"- Use signature phrases: {', '.join(signature_phrases[:3])}")
            
            # Add cultural elements
            cultural_elements = writing_style.get('cultural_elements', [])
            if cultural_elements:
                persona_parts.extend([
                    "",
                    f"MAINTAIN CULTURAL ELEMENTS: {', '.join(cultural_elements[:2])}"
                ])
            
            # Add formatting requirements
            title_pattern = content_structure.get('title_pattern', 'Laser Cleaning of {material}: Technical Analysis')
            byline = content_structure.get('byline', f"**{author_name}, Ph.D. - {author_country}**")
            
            persona_parts.extend([
                "",
                "PRESERVE FORMATTING STYLE:",
                f"- Title: {title_pattern.format(material=material_name)}",
                f"- Byline: {byline}",
                "",
                "Generate improved content that maintains the author's unique voice and cultural perspective:"
            ])
            
            return "\n".join(persona_parts)
            
        except Exception as e:
            logger.warning(f"Could not load persona config for author {author_id}: {e}")
            return improvement_prompt
    
    def _get_persona_system_prompt(self, author_info: Dict) -> str:
        """Get persona-specific system prompt."""
        if not author_info:
            return "You are an expert technical writer specializing in laser cleaning. Generate natural, human-like content that varies in structure and avoids mechanical patterns."
        
        author_name = author_info.get('name', 'Expert')
        author_country = author_info.get('country', 'International')
        
        return f"You are {author_name}, a technical expert from {author_country} specializing in laser cleaning. Write in your authentic voice with cultural nuances while generating natural, human-like content that varies in structure and avoids mechanical patterns. Maintain your unique writing style and perspective."
    
    def _apply_persona_formatting(self, content: str, material_name: str, author_info: Dict) -> str:
        """Apply persona-specific formatting to content with fallback handling."""
        if not author_info:
            # Fallback to basic formatting
            author_name = 'Expert'
            author_country = 'International'
            title = f"# Laser Cleaning of {material_name}: Technical Analysis"
            byline = f"**{author_name}, Ph.D. - {author_country}**"
            return f"{title}\n\n{byline}\n\n{content}"
        
        author_id = author_info.get('id', 1)
        author_name = author_info.get('name', 'Expert')
        author_country = author_info.get('country', 'International')
        
        try:
            # Load persona configuration
            from components.content.generator import load_persona_prompt
            persona_config = load_persona_prompt(author_id)
            content_structure = persona_config.get('content_structure', {})
            
            # Try to load enhanced formatting if available
            formatting_config = self._load_optional_formatting(author_info)
            if formatting_config:
                return self._apply_enhanced_formatting(content, material_name, author_info, formatting_config)
            
            # Fallback to existing persona-based formatting
            title_pattern = content_structure.get('title_pattern', 'Laser Cleaning of {material}: Technical Analysis')
            byline = content_structure.get('byline', f"**{author_name}, Ph.D. - {author_country}**")
            
            # Format title
            if '{material}' in title_pattern:
                title = f"# {title_pattern.format(material=material_name)}"
            else:
                title = f"# {title_pattern}"
            
            return f"{title}\n\n{byline}\n\n{content}"
            
        except Exception as e:
            logger.warning(f"Could not apply persona formatting for author {author_id}: {e}")
            # Fallback to basic formatting
            title = f"# Laser Cleaning of {material_name}: Technical Analysis"
            byline = f"**{author_name}, Ph.D. - {author_country}**"
            return f"{title}\n\n{byline}\n\n{content}"


    def _load_optional_formatting(self, author_info: Dict) -> Dict:
        """Load optional enhanced formatting configuration if available."""
        try:
            country = author_info.get('country', '').lower()
            
            # Try to load enhanced formatting files
            enhanced_files = [
                f"components/content/prompts/personas/{country}_complete.yaml",
                f"components/content/prompts/formatting/{country}_enhanced.yaml"
            ]
            
            for file_path in enhanced_files:
                if Path(file_path).exists() and Path(file_path).stat().st_size > 0:
                    import yaml
                    with open(file_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                        if config and 'formatting' in config:
                            return config['formatting']
        except Exception as e:
            logger.debug(f"No enhanced formatting available for {author_info.get('country', 'unknown')}: {e}")
        
        return {}
    
    def _apply_enhanced_formatting(self, content: str, material_name: str, 
                                 author_info: Dict, formatting_config: Dict) -> str:
        """Apply enhanced cultural formatting patterns."""
        author_name = author_info.get('name', 'Expert')
        
        # Apply enhanced title formatting
        title_style = formatting_config.get('title_style', {})
        title_pattern = title_style.get('pattern', 'Laser Cleaning of {material}: Technical Analysis')
        title = f"# {title_pattern.format(material=material_name)}"
        
        # Apply enhanced byline formatting
        byline_style = formatting_config.get('byline_style', {})
        byline_pattern = byline_style.get('pattern', '**{author_name}, Ph.D. - {country}**')
        byline = byline_pattern.format(
            author_name=author_name,
            country=author_info.get('country', 'International')
        )
        
        # Apply cultural sentence patterns
        enhanced_content = self._apply_cultural_patterns(content, formatting_config)
        
        return f"{title}\n\n{byline}\n\n{enhanced_content}"
    
    def _apply_cultural_patterns(self, content: str, formatting_config: Dict) -> str:
        """Apply cultural authenticity patterns to content."""
        paragraph_structure = formatting_config.get('paragraph_structure', {})
        sentence_patterns = formatting_config.get('sentence_patterns', {})
        
        # Apply transition phrases
        transition_phrases = paragraph_structure.get('transition_phrases', [])
        if transition_phrases:
            # Simple enhancement: add cultural transitions
            enhanced_content = content
            for phrase in transition_phrases[:2]:  # Limit to avoid over-application
                if phrase not in enhanced_content and len(enhanced_content.split('.')) > 3:
                    # Insert cultural transition in middle sections
                    sentences = enhanced_content.split('.')
                    if len(sentences) > 2:
                        insert_pos = len(sentences) // 2
                        sentences[insert_pos] = f". {phrase},"
                        enhanced_content = '.'.join(sentences)
                    break
            return enhanced_content
        
        return content

# Convenience function for backward compatibility
def create_enhanced_content_generator(enable_validation: bool = True,
                                    human_likeness_threshold: int = 80) -> EnhancedContentGenerator:
    """
    Create an enhanced content generator with specified settings.
    
    Args:
        enable_validation: Whether to enable human-like validation
        human_likeness_threshold: Minimum acceptable human-likeness score
        
    Returns:
        Configured enhanced content generator
    """
    return EnhancedContentGenerator(
        enable_validation=enable_validation,
        human_likeness_threshold=human_likeness_threshold
    )