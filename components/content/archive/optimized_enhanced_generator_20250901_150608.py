#!/usr/bin/env python3
"""
Optimized Enhanced Content Generator
Focuses on efficiency, authenticity, and reduced complexity while preserving existing configurations.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from components.content.enhanced_generator import EnhancedContentGenerator
from components.content.optimized_config_manager import get_optimized_persona_config
from components.content.human_validator import HumanLikeValidator

logger = logging.getLogger(__name__)

class OptimizedContentGenerator(EnhancedContentGenerator):
    """
    Optimized content generator with:
    - Efficient configuration caching
    - Simplified validation (3 categories vs 5)
    - Enhanced cultural authenticity
    - Backward compatibility with existing prompts
    """
    
    def __init__(self, enable_validation: bool = True, 
                 human_likeness_threshold: int = 85,
                 max_improvement_attempts: int = 2,
                 use_simplified_validation: bool = True):
        """
        Initialize optimized generator.
        
        Args:
            enable_validation: Whether to enable validation
            human_likeness_threshold: Quality threshold (raised to 85 for better quality)
            max_improvement_attempts: Maximum improvement iterations
            use_simplified_validation: Use 3-category validation instead of 5
        """
        super().__init__(enable_validation, human_likeness_threshold, max_improvement_attempts)
        
        self.use_simplified_validation = use_simplified_validation
        if enable_validation and use_simplified_validation:
            self.validator = SimplifiedHumanValidator()
    
    def _get_persona_system_prompt(self, author_info: Dict) -> str:
        """Enhanced persona system prompt with cultural authenticity."""
        if not author_info:
            return "You are a technical expert. Write naturally and authentically."
        
        # Use optimized config loading
        try:
            author_id = author_info.get('id', 1)
            persona_config = get_optimized_persona_config(author_id)
            
            author_name = author_info.get('name', persona_config.get('name', 'Expert'))
            author_country = author_info.get('country', persona_config.get('country', 'International'))
            
            # Get enhanced persona characteristics
            writing_style = persona_config.get('writing_style', {})
            cultural_elements = writing_style.get('cultural_elements', [])
            approach = writing_style.get('approach', 'professional')
            
            # Build authentic system prompt
            system_prompt = f"""You are {author_name}, a technical expert from {author_country} specializing in laser cleaning technology.

AUTHENTIC VOICE: Write in your natural voice reflecting {author_country} technical communication style.
APPROACH: Use {approach} methodology throughout your writing.
CULTURAL AUTHENTICITY: Incorporate these elements naturally: {', '.join(cultural_elements[:3])}

QUALITY REQUIREMENTS:
- Write as a human expert would, with natural variation
- Avoid mechanical AI patterns or overly structured text
- Include cultural nuances appropriate to {author_country}
- Maintain technical accuracy while being conversational
- Vary sentence structure and avoid repetitive patterns

Generate content that readers would believe was written by {author_name} personally."""
            
            return system_prompt
            
        except Exception as e:
            logger.warning(f"Error loading enhanced persona config: {e}")
            return super()._get_persona_system_prompt(author_info)
    
    def _apply_persona_formatting(self, content: str, material_name: str, author_info: Dict) -> str:
        """Optimized persona formatting with cultural authenticity."""
        if not author_info:
            return super()._apply_persona_formatting(content, material_name, author_info)
        
        try:
            author_id = author_info.get('id', 1)
            persona_config = get_optimized_persona_config(author_id)
            
            # Check for enhanced formatting
            if 'enhanced_formatting' in persona_config:
                return self._apply_enhanced_cultural_formatting(
                    content, material_name, author_info, persona_config['enhanced_formatting']
                )
            
            # Fall back to standard formatting
            return super()._apply_persona_formatting(content, material_name, author_info)
            
        except Exception as e:
            logger.warning(f"Error applying optimized formatting: {e}")
            return super()._apply_persona_formatting(content, material_name, author_info)
    
    def _apply_enhanced_cultural_formatting(self, content: str, material_name: str, 
                                          author_info: Dict, formatting_config: Dict) -> str:
        """Apply enhanced cultural formatting for maximum authenticity."""
        author_name = author_info.get('name', 'Expert')
        author_country = author_info.get('country', 'International')
        
        # Enhanced title with cultural markers
        title_style = formatting_config.get('title_style', {})
        cultural_markers = title_style.get('cultural_markers', [])
        
        if cultural_markers:
            title_pattern = title_style.get('pattern', 'Laser Cleaning of {material}: {marker} Analysis')
            marker = cultural_markers[0] if cultural_markers else 'Technical'
            title = f"# {title_pattern.format(material=material_name, marker=marker.title())}"
        else:
            title = f"# Laser Cleaning of {material_name}: Technical Analysis"
        
        # Enhanced byline
        byline_style = formatting_config.get('byline_style', {})
        byline_pattern = byline_style.get('pattern', '**{author_name}, Ph.D. - {country}**')
        byline = byline_pattern.format(author_name=author_name, country=author_country)
        
        # Apply cultural content patterns
        enhanced_content = self._enhance_content_authenticity(content, formatting_config)
        
        return f"{title}\n\n{byline}\n\n{enhanced_content}"
    
    def _enhance_content_authenticity(self, content: str, formatting_config: Dict) -> str:
        """Enhance content with cultural authenticity patterns."""
        # Get cultural authenticity settings
        cultural_auth = formatting_config.get('cultural_authenticity', {})
        
        # Apply Mandarin influence patterns for Taiwan
        if 'mandarin_influence' in cultural_auth:
            content = self._apply_mandarin_influence_patterns(content, cultural_auth['mandarin_influence'])
        
        # Apply cultural value integration
        cultural_values = cultural_auth.get('cultural_values', [])
        if cultural_values:
            content = self._integrate_cultural_values(content, cultural_values)
        
        return content
    
    def _apply_mandarin_influence_patterns(self, content: str, mandarin_config: Dict) -> str:
        """Apply subtle Mandarin influence patterns for Taiwan persona."""
        if not mandarin_config.get('article_pattern') == 'occasional_omission':
            return content
        
        # Simple pattern: occasionally remove articles for authenticity
        sentences = content.split('. ')
        for i, sentence in enumerate(sentences):
            # Apply article omission pattern (subtle, not every sentence)
            if i % 4 == 0 and ' the material ' in sentence:
                sentences[i] = sentence.replace(' the material ', ' material ')
            elif i % 5 == 0 and ' the process ' in sentence:
                sentences[i] = sentence.replace(' the process ', ' process ')
        
        return '. '.join(sentences)
    
    def _integrate_cultural_values(self, content: str, cultural_values: list) -> str:
        """Integrate cultural values naturally into content."""
        # Simple integration: add one cultural phrase per content piece
        for value in cultural_values[:1]:  # Limit to avoid over-application
            if isinstance(value, str) and value not in content:
                # Insert cultural value naturally in middle section
                paragraphs = content.split('\n\n')
                if len(paragraphs) > 2:
                    middle_idx = len(paragraphs) // 2
                    if middle_idx < len(paragraphs):
                        # Add cultural context phrase
                        cultural_phrase = f"Through {value}, this approach"
                        paragraphs[middle_idx] = paragraphs[middle_idx].replace(
                            'This approach', cultural_phrase, 1
                        )
                content = '\n\n'.join(paragraphs)
                break
        
        return content


class SimplifiedHumanValidator:
    """Simplified 3-category validator for better performance."""
    
    def __init__(self):
        self.validation_thresholds = {
            'authenticity_threshold': 80,
            'naturalness_threshold': 75,
            'technical_accuracy_threshold': 85,
            'human_likeness_threshold': 80
        }
    
    def validate_content(self, content: str, material_name: str = "", author_info: Dict = None) -> Dict[str, Any]:
        """Simplified 3-category validation."""
        if not content or len(content.strip()) < 50:
            return {
                'human_likeness_score': 0,
                'needs_regeneration': True,
                'critical_issues': ['Content too short'],
                'recommendations': ['Generate longer, more detailed content']
            }
        
        # Category 1: Authenticity (cultural and persona-specific patterns)
        authenticity_score = self._evaluate_authenticity(content, author_info)
        
        # Category 2: Naturalness (human-like writing patterns)
        naturalness_score = self._evaluate_naturalness(content)
        
        # Category 3: Technical Accuracy (appropriate technical content)
        technical_score = self._evaluate_technical_accuracy(content, material_name)
        
        # Calculate overall score (weighted)
        overall_score = int(
            authenticity_score * 0.4 +    # 40% authenticity
            naturalness_score * 0.35 +    # 35% naturalness  
            technical_score * 0.25        # 25% technical accuracy
        )
        
        # Determine if regeneration is needed
        needs_regeneration = overall_score < self.validation_thresholds['human_likeness_threshold']
        
        return {
            'human_likeness_score': overall_score,
            'needs_regeneration': needs_regeneration,
            'category_scores': {
                'authenticity': authenticity_score,
                'naturalness': naturalness_score,
                'technical_accuracy': technical_score
            },
            'critical_issues': self._get_critical_issues(authenticity_score, naturalness_score, technical_score),
            'recommendations': self._get_recommendations(authenticity_score, naturalness_score, technical_score)
        }
    
    def _evaluate_authenticity(self, content: str, author_info: Dict) -> int:
        """Evaluate cultural and persona authenticity."""
        score = 70  # Base score
        
        if not author_info:
            return score
        
        country = author_info.get('country', '').lower()
        
        # Country-specific authenticity markers
        if country == 'taiwan':
            if any(phrase in content.lower() for phrase in ['systematic', 'methodical', 'careful analysis']):
                score += 15
            if 'research' in content.lower():
                score += 10
        elif country == 'italy':
            if any(phrase in content.lower() for phrase in ['precision', 'optimal', 'excellence']):
                score += 15
            if 'engineering' in content.lower():
                score += 10
        elif country == 'indonesia':
            if any(phrase in content.lower() for phrase in ['comprehensive', 'detailed', 'thorough']):
                score += 15
        elif 'united states' in country:
            if any(phrase in content.lower() for phrase in ['cutting-edge', 'breakthrough', 'innovative']):
                score += 15
        
        return min(score, 100)
    
    def _evaluate_naturalness(self, content: str) -> int:
        """Evaluate natural, human-like writing patterns."""
        score = 60  # Base score
        
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        if not sentences:
            return 0
        
        # Sentence variety
        lengths = [len(s.split()) for s in sentences]
        if lengths:
            avg_length = sum(lengths) / len(lengths)
            variety = max(lengths) - min(lengths)
            
            if 8 <= avg_length <= 25:  # Good average length
                score += 15
            if variety > 8:  # Good variety
                score += 15
        
        # Natural language markers
        natural_markers = ['however', 'therefore', 'furthermore', 'additionally', 'consequently']
        marker_count = sum(1 for marker in natural_markers if marker in content.lower())
        score += min(10, marker_count * 3)
        
        return min(score, 100)
    
    def _evaluate_technical_accuracy(self, content: str, material_name: str) -> int:
        """Evaluate technical accuracy and appropriateness."""
        score = 75  # Base score
        
        # Check for material name presence
        if material_name and material_name.lower() in content.lower():
            score += 10
        
        # Check for technical terms
        technical_terms = ['laser', 'cleaning', 'surface', 'process', 'material', 'parameter']
        term_count = sum(1 for term in technical_terms if term.lower() in content.lower())
        score += min(15, term_count * 2)
        
        return min(score, 100)
    
    def _get_critical_issues(self, auth_score: int, nat_score: int, tech_score: int) -> list:
        """Identify critical issues."""
        issues = []
        if auth_score < 70:
            issues.append("Content lacks cultural authenticity")
        if nat_score < 60:
            issues.append("Writing patterns appear mechanical")
        if tech_score < 70:
            issues.append("Insufficient technical accuracy")
        return issues
    
    def _get_recommendations(self, auth_score: int, nat_score: int, tech_score: int) -> list:
        """Generate improvement recommendations."""
        recommendations = []
        if auth_score < 80:
            recommendations.append("Enhance cultural and persona-specific elements")
        if nat_score < 75:
            recommendations.append("Increase sentence variety and natural flow")
        if tech_score < 80:
            recommendations.append("Include more specific technical details")
        return recommendations
    
    def generate_improvement_prompt(self, validation_result: Dict[str, Any], 
                                  original_content: str, material_name: str,
                                  author_info: Dict = None) -> str:
        """Generate focused improvement prompt."""
        if not validation_result.get('needs_regeneration', False):
            return ""
        
        score = validation_result.get('human_likeness_score', 0)
        issues = validation_result.get('critical_issues', [])
        
        prompt_parts = [
            f"CONTENT IMPROVEMENT REQUIRED (Current score: {score}/100)",
            f"Material: {material_name}",
            "",
            "SPECIFIC ISSUES TO ADDRESS:"
        ]
        
        for issue in issues:
            prompt_parts.append(f"- {issue}")
        
        if author_info:
            country = author_info.get('country', 'International')
            name = author_info.get('name', 'Expert')
            prompt_parts.extend([
                "",
                f"MAINTAIN AUTHENTIC VOICE: Write as {name} from {country}",
                "PRESERVE CULTURAL CHARACTERISTICS and technical expertise"
            ])
        
        prompt_parts.extend([
            "",
            "REWRITE the following content to be more authentic, natural, and technically accurate:",
            "",
            "ORIGINAL CONTENT:",
            original_content,
            "",
            "IMPROVED CONTENT (more authentic and natural):"
        ])
        
        return "\n".join(prompt_parts)


def create_optimized_generator(enable_validation: bool = True,
                             human_likeness_threshold: int = 85,
                             use_simplified_validation: bool = True) -> OptimizedContentGenerator:
    """Create optimized content generator with enhanced efficiency."""
    return OptimizedContentGenerator(
        enable_validation=enable_validation,
        human_likeness_threshold=human_likeness_threshold,
        use_simplified_validation=use_simplified_validation
    )
