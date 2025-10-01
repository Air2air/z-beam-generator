#!/usr/bin/env python3
"""
Enhanced Caption Component Generator
Optimized for readability, conciseness, and reduced AI detection scores
"""

import datetime
import json
import logging
import re
import random
from pathlib import Path
from typing import Dict, Optional
from generators.component_generators import APIComponentGenerator
from utils.config_loader import load_yaml_config

logger = logging.getLogger(__name__)

class HumanWritingPatterns:
    """Apply human writing patterns to reduce AI detection"""
    
    def __init__(self):
        self.qualifiers = [
            'typically', 'generally', 'often', 'usually', 'frequently',
            'commonly', 'predominantly', 'tends to'
        ]
        
        self.uncertainty_phrases = [
            'appears to show', 'tends to exhibit', 'seems to indicate',
            'may demonstrate', 'often reveals', 'typically displays'
        ]
        
        self.conversational_connectors = [
            'Interestingly,', 'Notably,', 'In this case,', 'What we see here is',
            'The analysis reveals', 'Examination shows', 'Field testing indicates'
        ]
        
        self.technical_hedging = [
            'analysis suggests', 'data indicates', 'testing shows',
            'measurements confirm', 'observations reveal'
        ]

    def humanize_technical_content(self, content: str) -> str:
        """Apply comprehensive humanization to technical content"""
        # Split into sentences for processing
        sentences = re.split(r'(?<=[.!?])\s+', content.strip())
        humanized_sentences = []
        
        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
            
            # Apply various humanization techniques
            sentence = self._add_conversational_elements(sentence, i)
            sentence = self._soften_absolute_statements(sentence)
            sentence = self._vary_sentence_structure(sentence)
            sentence = self._add_practical_context(sentence)
            
            humanized_sentences.append(sentence)
        
        return ' '.join(humanized_sentences)
    
    def _add_conversational_elements(self, sentence: str, position: int) -> str:
        """Add conversational elements to make content more natural"""
        if position > 0 and random.random() < 0.2:  # 20% chance
            connector = random.choice(self.conversational_connectors)
            sentence = f"{connector} {sentence.lower()}"
        return sentence
    
    def _soften_absolute_statements(self, sentence: str) -> str:
        """Replace absolute statements with qualified ones"""
        # Replace definitive technical claims
        patterns = {
            r'\bshows\s+([^.]+)': lambda m: f"{random.choice(self.technical_hedging)} {m.group(1)}",
            r'\breveals\s+([^.]+)': lambda m: f"appears to reveal {m.group(1)}",
            r'\bdemonstrates\s+([^.]+)': lambda m: f"{random.choice(['typically demonstrates', 'often shows'])} {m.group(1)}",
            r'\bconfirms\s+([^.]+)': lambda m: f"testing suggests {m.group(1)}",
        }
        
        for pattern, replacement in patterns.items():
            sentence = re.sub(pattern, replacement, sentence)
        
        return sentence
    
    def _vary_sentence_structure(self, sentence: str) -> str:
        """Add structural variety to sentences"""
        # Occasionally start with prepositional phrases
        if random.random() < 0.15 and not sentence.startswith(('The', 'A', 'An')):
            prep_phrases = [
                'In practice,', 'During processing,', 'Under these conditions,',
                'Through careful analysis,', 'Based on testing,'
            ]
            if not any(sentence.startswith(phrase) for phrase in self.conversational_connectors):
                sentence = f"{random.choice(prep_phrases)} {sentence.lower()}"
        
        return sentence
    
    def _add_practical_context(self, sentence: str) -> str:
        """Add practical, experience-based language"""
        # Replace overly technical phrases with practical ones
        replacements = {
            'exhibits': 'shows',
            'demonstrates': 'displays',
            'facilitates': 'helps',
            'eliminates': 'removes',
            'encompasses': 'includes'
        }
        
        for technical, practical in replacements.items():
            if random.random() < 0.3:  # 30% chance
                sentence = sentence.replace(technical, practical)
        
        return sentence


class EnhancedCaptionGenerator(APIComponentGenerator):
    """Enhanced caption generator with improved readability and reduced AI detection"""
    
    def __init__(self):
        super().__init__("caption")
        self.humanizer = HumanWritingPatterns()
        
        # Configuration for improved captions
        self.config = {
            'target_length_before': (350, 450),  # Reduced from 500-700
            'target_length_after': (350, 450),   # Reduced from 500-700
            'max_technical_density': 0.7,        # Limit technical jargon
            'readability_target': 'college',     # Target reading level
            'ai_detection_target': 75.0          # Target score (higher = more human)
        }

    def _load_frontmatter_data(self, material_name: str) -> Dict:
        """Load frontmatter data for the material - case-insensitive search"""
        content_dir = Path("content/components/frontmatter")
        
        # Normalize material name for more flexible matching
        normalized_name = material_name.lower().replace('_', ' ').replace(' ', '-')
        
        potential_paths = [
            content_dir / f"{material_name.lower()}.yaml",
            content_dir / f"{material_name.lower().replace(' ', '-')}.yaml",
            content_dir / f"{material_name.lower().replace('_', '-')}.yaml",
            content_dir / f"{normalized_name}.yaml",
            content_dir / f"{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml",
            content_dir / f"{normalized_name}-laser-cleaning.yaml"
        ]
        
        for path in potential_paths:
            if path.exists():
                try:
                    return load_yaml_config(str(path))
                except Exception as e:
                    logger.warning(f"Could not load frontmatter from {path}: {e}")
                    continue
        
        return {}

    def _build_enhanced_prompt(self, material_name: str, material_data: Dict, 
                             frontmatter_data: Optional[Dict] = None) -> str:
        """Build enhanced AI prompt for more readable, concise captions"""
        
        if not frontmatter_data:
            frontmatter_data = self._load_frontmatter_data(material_name)
        
        # Extract essential context
        material_props = frontmatter_data.get('materialProperties', {})
        category = frontmatter_data.get('category', 'material')
        
        # Focus on key properties only
        key_properties = self._extract_key_properties(material_props, category)
        
        return f"""You are an experienced materials engineer writing practical surface analysis descriptions for {material_name} laser cleaning.

WRITING STYLE REQUIREMENTS:
- Write in a professional but accessible tone
- Use active voice when possible
- Vary sentence structure and length
- Include specific measurements but explain their significance
- Use conversational transitions between technical points
- Blend technical accuracy with practical insights

CONTENT REQUIREMENTS:
- Material: {material_name} ({category} category)
- Key Properties: {json.dumps(key_properties, indent=2) if key_properties else 'Standard properties'}
- Target Length: 350-450 characters per section
- Focus: Practical surface analysis with essential technical details

Generate exactly two focused descriptions:

**BEFORE_TEXT:**
[Write a concise 350-450 character description of the contaminated {material_name.lower()} surface that includes:
- Primary contamination types with practical impact
- 2-3 key measurements (thickness, roughness, composition)
- How contamination affects the material's performance
- Brief mention of material properties relevant to laser processing
- Natural, conversational technical language]

**AFTER_TEXT:**
[Write a focused 350-450 character description of the cleaned surface that includes:
- Quantified improvements with practical significance
- 2-3 key performance metrics after cleaning
- Material integrity and quality preservation
- Practical benefits of the cleaning process
- Clear, accessible technical language with natural flow]

IMPORTANT: Write as an experienced practitioner sharing insights, not as an AI generating technical specifications. Use natural language patterns and vary your sentence structures."""

    def _extract_key_properties(self, material_props: Dict, category: str) -> Dict:
        """Extract 3-4 most relevant properties for laser cleaning context"""
        
        # Priority properties by category
        priority_props = {
            'metal': ['density', 'thermal_conductivity', 'melting_point', 'reflectivity'],
            'ceramic': ['hardness', 'thermal_expansion', 'melting_point', 'density'],
            'polymer': ['glass_transition', 'thermal_stability', 'density', 'hardness'],
            'composite': ['fiber_content', 'density', 'thermal_stability', 'hardness'],
            'glass': ['hardness', 'thermal_expansion', 'density', 'melting_point'],
            'wood': ['density', 'moisture_content', 'hardness', 'thermal_conductivity']
        }
        
        relevant_props = priority_props.get(category.lower(), ['density', 'hardness'])
        
        key_properties = {}
        for prop in relevant_props[:3]:  # Limit to 3 properties
            if prop in material_props and isinstance(material_props[prop], dict):
                prop_data = material_props[prop]
                if 'value' in prop_data:
                    key_properties[prop] = {
                        'value': prop_data['value'],
                        'unit': prop_data.get('unit', ''),
                        'significance': self._get_property_significance(prop, category)
                    }
        
        return key_properties

    def _get_property_significance(self, property_name: str, category: str) -> str:
        """Get practical significance of property for laser cleaning"""
        significance_map = {
            'density': 'affects heat dissipation and processing parameters',
            'thermal_conductivity': 'influences heat transfer during processing',
            'melting_point': 'determines maximum safe processing temperature',
            'reflectivity': 'affects laser absorption and energy requirements',
            'hardness': 'impacts contamination adhesion and removal difficulty'
        }
        return significance_map.get(property_name, 'affects processing characteristics')

    def _extract_and_optimize_content(self, ai_response: str, material_name: str) -> Dict:
        """Extract and optimize AI content for readability and reduced detection"""
        
        if not ai_response or not ai_response.strip():
            raise ValueError(f"Empty AI response for {material_name}")
        
        # Extract text blocks
        before_start = ai_response.find('**BEFORE_TEXT:**')
        before_end = ai_response.find('**AFTER_TEXT:**')
        
        if before_start == -1 or before_end == -1:
            raise ValueError(f"Missing text markers in AI response for {material_name}")
        
        before_text = ai_response[before_start + len('**BEFORE_TEXT:**'):before_end].strip()
        before_text = before_text.strip('[]').strip()
        
        after_start = before_end + len('**AFTER_TEXT:**')
        after_text = ai_response[after_start:].strip()
        after_text = after_text.strip('[]').strip()
        
        # Validate minimum content
        if not before_text or len(before_text) < 200:
            raise ValueError(f"BEFORE_TEXT too short for {material_name}")
        
        if not after_text or len(after_text) < 200:
            raise ValueError(f"AFTER_TEXT too short for {material_name}")
        
        # Apply humanization and optimization
        before_text = self._optimize_text_for_readability(before_text)
        after_text = self._optimize_text_for_readability(after_text)
        
        # Apply AI detection reduction
        before_text = self.humanizer.humanize_technical_content(before_text)
        after_text = self.humanizer.humanize_technical_content(after_text)
        
        return {
            'before_text': before_text,
            'after_text': after_text,
            'technical_focus': 'practical_analysis',
            'writing_style': 'professional_accessible',
            'optimization_applied': ['readability', 'conciseness', 'humanization']
        }

    def _optimize_text_for_readability(self, text: str) -> str:
        """Optimize text for better readability"""
        
        # Replace overly complex terms with clearer alternatives
        readability_improvements = {
            'exhibits': 'shows',
            'demonstrates': 'reveals',
            'facilitates': 'enables',
            'encompasses': 'includes',
            'predominant': 'main',
            'necessitates': 'requires',
            'accumulated': 'built-up',
            'substantial': 'significant',
            'elimination': 'removal',
            'optimization': 'improvement'
        }
        
        for complex_term, simple_term in readability_improvements.items():
            text = re.sub(f'\\b{complex_term}\\b', simple_term, text, flags=re.IGNORECASE)
        
        # Simplify overly technical phrases
        technical_simplifications = {
            r'stratified layer comprising': 'layered contamination with',
            r'surface profilometry reveals': 'surface measurements show',
            r'localized pitting to': 'pit depths up to',
            r'intergranular corrosion following': 'corrosion along',
            r'thermal gradient-induced stress': 'heat-related stress'
        }
        
        for pattern, replacement in technical_simplifications.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text

    def generate(self, material_name: str, material_data: Dict, 
                api_client=None, **kwargs) -> Dict:
        """Generate enhanced caption content with improved readability"""
        
        if not api_client:
            raise ValueError("API client required for caption generation")
        
        frontmatter_data = self._load_frontmatter_data(material_name)
        if not frontmatter_data:
            raise ValueError(f"Frontmatter data required for {material_name}")
        
        # Extract required metadata
        timestamp = datetime.datetime.now().isoformat() + "Z"
        author_obj = frontmatter_data.get('author', {})
        author = author_obj.get('name', 'Unknown Author')
        category = frontmatter_data.get('category', 'Material')
        
        try:
            # Generate content with enhanced prompt
            prompt = self._build_enhanced_prompt(material_name, material_data, frontmatter_data)
            
            response = api_client.generate_simple(
                prompt=prompt,
                max_tokens=2000,     # Reduced for more focused content
                temperature=0.3      # Slightly higher for more natural variation
            )
            
            if not response.success or not response.content:
                raise ValueError(f"AI generation failed for {material_name}")
            
            # Extract and optimize content
            optimized_content = self._extract_and_optimize_content(response.content, material_name)
                
        except Exception as e:
            logger.error(f"Enhanced caption generation failed for {material_name}: {e}")
            raise
        
        # Generate optimized YAML content
        yaml_content = f"""---
# Enhanced Caption Content for {material_name}
before_text: |
  {optimized_content['before_text']}

after_text: |
  {optimized_content['after_text']}

# Content Optimization
content_optimization:
  writing_style: "{optimized_content.get('writing_style', 'professional_accessible')}"
  focus: "{optimized_content.get('technical_focus', 'practical_analysis')}"
  improvements_applied: {optimized_content.get('optimization_applied', [])}
  readability_target: "{self.config['readability_target']}"
  ai_detection_target: {self.config['ai_detection_target']}

# Processing Information  
processing:
  frontmatter_available: true
  ai_generated: true
  generation_method: "enhanced_ai_with_humanization"
  generator_version: "enhanced_v1.0"

# Generation Metadata
generation:
  generated: "{timestamp}"
  component_type: "enhanced_ai_caption"
  optimization_level: "high"

# Author Information
author: "{author}"

# SEO Optimization (Enhanced)
seo:
  title: "{material_name.title()} Laser Surface Treatment Analysis"
  description: "Professional analysis of {material_name.lower()} surface cleaning with practical insights"
  focus_keywords: ["{material_name.lower()}", "laser cleaning", "surface analysis"]

# Material Classification
material_properties:
  materialType: "{category}"
  analysisMethod: "enhanced_practical_analysis"

---
# Component Metadata
Material: "{material_name.lower()}"
Component: enhanced_caption
Generated: {timestamp}
Generator: Z-Beam Enhanced v1.0 (Human-Optimized AI)
---"""

        return self._create_result(yaml_content, success=True)


def generate_enhanced_caption_content(material: str, material_data: Dict = None, api_client=None) -> str:
    """Generate enhanced caption content with improved readability and reduced AI detection"""
    
    if not api_client:
        raise ValueError("API client required for enhanced caption generation")
    
    generator = EnhancedCaptionGenerator()
    result = generator.generate(material, material_data or {}, api_client=api_client)
    
    if not result.success:
        raise ValueError(f"Enhanced caption generation failed for {material}: {result.error_message}")
    
    return result.content


# Test function for development
def test_enhanced_generator():
    """Test the enhanced caption generator"""
    try:
        from api.client_factory import create_api_client
        
        print("🚀 Testing Enhanced Caption Generator")
        print("=" * 50)
        
        # Create API client
        client = create_api_client('deepseek')
        
        # Test with aluminum
        material = "aluminum"
        print(f"\\n📝 Generating enhanced caption for {material}")
        
        result = generate_enhanced_caption_content(material, {}, api_client=client)
        
        print(f"✅ Generated enhanced caption ({len(result):,} characters)")
        print("\\nSample content:")
        print(result[:500] + "..." if len(result) > 500 else result)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_enhanced_generator()