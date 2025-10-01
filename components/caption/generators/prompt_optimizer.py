#!/usr/bin/env python3
"""
Caption Prompt Optimization System
Advanced prompt engineering for better readability and reduced AI detection
"""

from typing import Dict

class CaptionPromptOptimizer:
    """Optimizes prompts for more natural, readab    print("\nContent    print(\"\\nContent Analysis Results:\")Analysis Results:")e, and less AI-detectable content"""
    
    def __init__(self):
        self.readability_guidelines = {
            'sentence_length': 'Mix short (10-15 words) and medium (16-25 words) sentences',
            'technical_density': 'Balance technical terms with plain language explanations',
            'active_voice': 'Use active voice for clarity and directness',
            'transitions': 'Use natural connectors between ideas',
            'specificity': 'Include specific measurements but explain their importance'
        }
        
        self.humanization_strategies = {
            'conversational_tone': 'Write as an experienced professional sharing insights',
            'practical_focus': 'Emphasize real-world applications and benefits',
            'varied_structures': 'Mix declarative, conditional, and explanatory sentences',
            'natural_flow': 'Use logical progression from observation to analysis',
            'personal_experience': 'Include subtle indicators of professional experience'
        }

    def create_optimized_prompt(self, material_name: str, material_data: Dict, 
                              category: str, key_properties: Dict) -> str:
        """Create an optimized prompt for natural, readable caption generation"""
        
        # Build context section
        context_section = self._build_material_context(material_name, category, key_properties)
        
        # Build writing guidelines
        guidelines_section = self._build_writing_guidelines()
        
        # Build content requirements
        requirements_section = self._build_content_requirements(material_name, category)
        
        # Build quality criteria
        quality_section = self._build_quality_criteria()
        
        return f"""{context_section}

{guidelines_section}

{requirements_section}

{quality_section}

Generate exactly two descriptions:

**BEFORE_TEXT:**
Write a natural, professional description (350-450 characters) of the contaminated {material_name.lower()} surface. Focus on:
- What contamination is present and why it matters
- Key measurements that affect performance
- How the material's properties influence the cleaning challenge
- Use conversational professional language, not AI-generated technical speak

**AFTER_TEXT:**
Write a clear, results-focused description (350-450 characters) of the cleaned surface. Focus on:
- Specific improvements that matter in practice
- Performance metrics that demonstrate success
- Why these results are significant for users
- Use natural, accessible language while maintaining technical accuracy

Remember: Write as an experienced materials professional sharing practical insights, not as an AI system generating specifications."""

    def _build_material_context(self, material_name: str, category: str, key_properties: Dict) -> str:
        """Build material context section"""
        return f"""MATERIAL ANALYSIS CONTEXT:
You are a senior materials engineer with 15+ years of experience in laser surface processing, writing practical surface analysis descriptions for {material_name} cleaning applications.

Material Profile:
- Name: {material_name}
- Category: {category}
- Key Properties for Laser Processing: {self._format_properties_naturally(key_properties)}
- Application Focus: Industrial surface preparation and contamination removal"""

    def _format_properties_naturally(self, properties: Dict) -> str:
        """Format properties in a natural, conversational way"""
        if not properties:
            return "Standard material characteristics"
        
        formatted_props = []
        for prop, data in properties.items():
            value = data.get('value', '')
            unit = data.get('unit', '')
            
            # Create natural descriptions
            if prop == 'density':
                formatted_props.append(f"density of {value} {unit} (important for heat distribution)")
            elif prop == 'thermal_conductivity':
                formatted_props.append(f"thermal conductivity of {value} {unit} (affects processing speed)")
            elif prop == 'melting_point':
                formatted_props.append(f"melting point of {value} {unit} (sets temperature limits)")
            else:
                formatted_props.append(f"{prop.replace('_', ' ')}: {value} {unit}")
        
        return "; ".join(formatted_props)

    def _build_writing_guidelines(self) -> str:
        """Build writing guidelines section"""
        return """PROFESSIONAL WRITING STYLE:
- Write in first person plural ("we observe") or professional passive voice
- Use varied sentence structures: some short and direct, others more detailed
- Include conversational transitions like "Interestingly," "What we see here," "The analysis shows"
- Balance technical precision with accessibility
- Write as if explaining to a knowledgeable colleague, not generating technical documentation
- Use active voice where natural, passive voice where it flows better
- Include subtle indicators of practical experience and field knowledge"""

    def _build_content_requirements(self, material_name: str, category: str) -> str:
        """Build content requirements section"""
        return f"""CONTENT STRUCTURE REQUIREMENTS:
- Length: 350-450 characters per section (concise but comprehensive)
- Technical Level: Professional but accessible (avoid unnecessary jargon)
- Measurement Focus: Include 2-3 key quantitative values with practical context
- Material Specificity: Reference {material_name}-specific properties and behaviors
- Contamination Analysis: Realistic contamination types for {category} materials
- Practical Impact: Explain why measurements and changes matter in real applications
- Natural Flow: Logical progression from observation to analysis to significance"""

    def _build_quality_criteria(self) -> str:
        """Build quality criteria section"""
        return """QUALITY AND NATURALNESS CRITERIA:
- Readability: Write at college professional level, not academic research level
- Authenticity: Sound like experienced professional insights, not AI-generated content
- Engagement: Include elements that show genuine professional interest and experience
- Precision: Be specific with measurements but explain their practical importance
- Flow: Use natural language patterns and avoid robotic technical writing
- Balance: Mix technical accuracy with practical, real-world perspective
- Variation: Vary sentence beginnings, lengths, and structures for natural rhythm"""

    def get_post_generation_improvements(self) -> Dict[str, str]:
        """Get guidelines for post-generation content improvement"""
        return {
            'sentence_variety': 'Ensure mix of short (10-15 words) and longer (16-25 words) sentences',
            'technical_balance': 'Replace 1-2 technical terms per paragraph with simpler alternatives',
            'conversational_elements': 'Add 1-2 conversational transitions or professional observations',
            'practical_context': 'Ensure all measurements include practical significance',
            'natural_flow': 'Check that content reads like professional communication, not technical specifications',
            'active_voice': 'Convert 30-40% of passive constructions to active voice',
            'professional_hedging': 'Add appropriate uncertainty markers for more natural technical writing'
        }

    def analyze_content_quality(self, content: str) -> Dict[str, any]:
        """Analyze generated content for quality and naturalness"""
        
        # Basic metrics
        word_count = len(content.split())
        sentence_count = len([s for s in content.split('.') if s.strip()])
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # Technical density (rough estimate)
        technical_terms = ['analysis', 'measurement', 'processing', 'surface', 'contamination', 
                          'temperature', 'structure', 'composition', 'parameters', 'optimization']
        technical_count = sum(1 for term in technical_terms if term.lower() in content.lower())
        technical_density = technical_count / max(word_count, 1) * 100
        
        # Passive voice detection (rough)
        passive_indicators = [' is ', ' are ', ' was ', ' were ', ' been ', ' being ']
        passive_count = sum(1 for indicator in passive_indicators if indicator in content.lower())
        
        # AI-like patterns (indicators of robotic writing)
        ai_indicators = ['demonstrates', 'exhibits', 'encompasses', 'facilitates', 'optimizes']
        ai_pattern_count = sum(1 for indicator in ai_indicators if indicator.lower() in content.lower())
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'technical_density_percent': round(technical_density, 1),
            'passive_voice_count': passive_count,
            'ai_pattern_count': ai_pattern_count,
            'readability_score': self._calculate_readability_score(
                avg_sentence_length, technical_density, ai_pattern_count
            ),
            'recommendations': self._get_improvement_recommendations(
                avg_sentence_length, technical_density, ai_pattern_count, passive_count
            )
        }

    def _calculate_readability_score(self, avg_sentence_length: float, 
                                   technical_density: float, ai_patterns: int) -> str:
        """Calculate overall readability score"""
        score = 100
        
        # Penalize for overly long sentences
        if avg_sentence_length > 25:
            score -= 15
        elif avg_sentence_length > 20:
            score -= 5
        
        # Penalize for high technical density
        if technical_density > 15:
            score -= 20
        elif technical_density > 10:
            score -= 10
        
        # Penalize for AI-like patterns
        score -= ai_patterns * 5
        
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Good"
        elif score >= 70:
            return "Fair"
        else:
            return "Needs Improvement"

    def _get_improvement_recommendations(self, avg_sentence_length: float,
                                       technical_density: float, ai_patterns: int,
                                       passive_count: int) -> list:
        """Get specific recommendations for content improvement"""
        recommendations = []
        
        if avg_sentence_length > 25:
            recommendations.append("Break up some longer sentences for better readability")
        elif avg_sentence_length < 12:
            recommendations.append("Combine some short sentences for better flow")
        
        if technical_density > 15:
            recommendations.append("Replace some technical terms with simpler alternatives")
        
        if ai_patterns > 2:
            recommendations.append("Replace AI-typical verbs (demonstrates, exhibits) with more natural language")
        
        if passive_count > 3:
            recommendations.append("Convert some passive voice constructions to active voice")
        
        if not recommendations:
            recommendations.append("Content quality is good - minor refinements may still improve naturalness")
        
        return recommendations


def test_prompt_optimizer():
    """Test the prompt optimization system"""
    
    optimizer = CaptionPromptOptimizer()
    
    # Sample material data
    material_name = "aluminum"
    category = "metal"
    key_properties = {
        'density': {'value': '2.70', 'unit': 'g/cm³', 'significance': 'affects heat dissipation'},
        'thermal_conductivity': {'value': '237', 'unit': 'W/m·K', 'significance': 'influences processing speed'}
    }
    
    # Generate optimized prompt
    prompt = optimizer.create_optimized_prompt(material_name, {}, category, key_properties)
    
    print("🚀 Optimized Caption Prompt")
    print("=" * 50)
    print(prompt)
    print("\\n" + "=" * 50)
    
    # Test content analysis
    sample_content = """The aluminum surface shows contamination with oxide layers measuring 15-25 micrometers thick. 
    Analysis reveals chloride deposits and organic residues that reduce the material's reflectivity. 
    After laser cleaning, surface roughness improved from 3.8 to 0.8 micrometers, restoring optimal performance."""
    
    analysis = optimizer.analyze_content_quality(sample_content)
    print(f"\\nContent Analysis Results:")
    print(f"Readability Score: {analysis['readability_score']}")
    print(f"Average Sentence Length: {analysis['avg_sentence_length']} words")
    print(f"Technical Density: {analysis['technical_density_percent']}%")
    print(f"Recommendations: {analysis['recommendations']}")


if __name__ == "__main__":
    test_prompt_optimizer()