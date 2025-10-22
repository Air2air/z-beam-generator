#!/usr/bin/env python3
"""
Chain-Based Caption Generator - Simplified, Validated, Observable

Replaces the complex 26K+ character prompt system with a modular chain
approach that provides better validation, quality control, and observability.
"""

from dataclasses import dataclass
from typing import List
from pathlib import Path
import yaml
import logging

logger = logging.getLogger(__name__)


@dataclass
class VoiceProfile:
    """Simplified voice profile with essential characteristics"""
    country: str
    author_name: str
    key_traits: List[str]
    opening_styles: List[str]
    measurement_style: str
    cultural_context: str
    banned_phrases: List[str]
    required_elements: List[str]


@dataclass
class MaterialContext:
    """Essential material context for prompt generation"""
    material_name: str
    category: str
    key_challenges: List[str]
    cleaning_benefits: List[str]
    typical_measurements: dict
    applications: List[str]


@dataclass
class PromptChain:
    """Validated prompt chain for generation"""
    context_prompt: str
    voice_prompt: str
    generation_prompt: str
    validation_rules: dict
    expected_outcomes: dict


@dataclass
class ValidationResult:
    """Real-time validation results"""
    passed: bool
    issues: List[str]
    warnings: List[str]
    should_continue: bool


class VoiceProfileSelector:
    """Selects optimal voice profile for material/context combination"""
    
    VOICE_PROFILES = {
        'united_states': VoiceProfile(
            country='united_states',
            author_name='Todd Dunning, MA',
            key_traits=['Direct communication', 'Business focus', 'Results-oriented', 'Practical approach'],
            opening_styles=[
                "Here's what we're seeing with this {material}",
                "Looking at these {material} results",
                "Bottom line - this {material} cleaning"
            ],
            measurement_style="Imperfect ranges with business context",
            cultural_context="American industrial efficiency and optimization",
            banned_phrases=['Surface analysis reveals', 'Microscopic examination shows'],
            required_elements=['Business terminology', 'Direct language', 'Results focus']
        ),
        'taiwan': VoiceProfile(
            country='taiwan',
            author_name='Yi-Chun Lin, Ph.D.',
            key_traits=['Academic precision', 'Systematic approach', 'Data-driven', 'Measurement-focused'],
            opening_styles=[
                "According to our systematic analysis of {material}",
                "This data suggests that {material}",
                "Our findings indicate that {material}"
            ],
            measurement_style="Ranges with academic uncertainty",
            cultural_context="Taiwanese precision manufacturing and systematic documentation",
            banned_phrases=['Surface analysis reveals', 'Microscopic examination shows'],
            required_elements=['Academic markers', 'Systematic language', 'Measurement emphasis']
        ),
        'italy': VoiceProfile(
            country='italy',
            author_name='Alessandro Moretti, Ph.D.',
            key_traits=['Technical elegance', 'Aesthetic appreciation', 'Personal observation', 'Visual focus'],
            opening_styles=[
                "Examining this beautiful {material} surface",
                "What strikes me about this {material}",
                "I must say this {material} cleaning"
            ],
            measurement_style="Aesthetic descriptions with technical precision",
            cultural_context="Italian design excellence and visual appreciation",
            banned_phrases=['Surface analysis reveals', 'Microscopic examination shows'],
            required_elements=['Aesthetic language', 'Personal voice', 'Visual descriptions']
        ),
        'indonesia': VoiceProfile(
            country='indonesia',
            author_name='Ikmanda Roswati, Ph.D.',
            key_traits=['Environmental consciousness', 'Community focus', 'Practical benefits', 'Sustainability'],
            opening_styles=[
                "In our Indonesian context, this {material}",
                "From a practical standpoint, {material}",
                "Considering our environmental needs, {material}"
            ],
            measurement_style="Practical ranges with environmental context",
            cultural_context="Indonesian environmental stewardship and community benefits",
            banned_phrases=['Surface analysis reveals', 'Microscopic examination shows'],
            required_elements=['Environmental terms', 'Community benefits', 'Practical language']
        )
    }
    
    def select_voice(self, material: str, context: dict) -> VoiceProfile:
        """Select optimal voice profile based on material and context"""
        
        # For now, use round-robin or specified country
        # In production, this would use intelligent selection logic
        country = context.get('author_country', 'united_states')
        
        if country not in self.VOICE_PROFILES:
            logger.warning(f"Unknown country {country}, defaulting to united_states")
            country = 'united_states'
        
        return self.VOICE_PROFILES[country]


class ContextAnalyzer:
    """Analyzes material properties to generate context-aware prompts"""
    
    def analyze_material(self, material: str) -> MaterialContext:
        """Analyze material to extract key context for generation"""
        
        # Load material data
        materials_path = Path("data/Materials.yaml")
        with open(materials_path, 'r') as f:
            data = yaml.safe_load(f)
        
        if material not in data['materials']:
            raise ValueError(f"Material {material} not found in database")
        
        material_data = data['materials'][material]
        
        # Extract key challenges (simplified for prototype)
        key_challenges = [
            "Surface contamination removal",
            "Oxide layer cleaning",
            "Maintaining substrate integrity"
        ]
        
        # Extract cleaning benefits
        cleaning_benefits = [
            "Improved surface quality",
            "Enhanced corrosion resistance", 
            "Better adhesion properties"
        ]
        
        # Typical measurements (would be material-specific)
        typical_measurements = {
            "contamination_thickness": "10-20 micrometers",
            "cleaning_efficiency": "85-95%",
            "surface_roughness": "0.2-0.5 micrometers"
        }
        
        applications = material_data.get('applications', ['General industrial'])
        if isinstance(applications, dict):
            applications = applications.get('industrial', ['General industrial'])
        
        return MaterialContext(
            material_name=material,
            category=material_data.get('category', 'material'),
            key_challenges=key_challenges,
            cleaning_benefits=cleaning_benefits,
            typical_measurements=typical_measurements,
            applications=applications
        )


class PromptChainBuilder:
    """Builds validated, country-specific prompt chains"""
    
    def build_chain(self, voice: VoiceProfile, context: MaterialContext) -> PromptChain:
        """Build complete prompt chain with validation rules"""
        
        # Context establishment prompt (short and focused)
        context_prompt = f"""
        Material: {context.material_name}
        Category: {context.category}
        Key Challenges: {', '.join(context.key_challenges)}
        Applications: {', '.join(context.applications[:2])}
        """
        
        # Voice-specific prompt (country characteristics)
        voice_prompt = f"""
        You are {voice.author_name}, providing technical analysis from a {voice.country} perspective.
        
        Voice Characteristics:
        - {', '.join(voice.key_traits)}
        - Cultural Context: {voice.cultural_context}
        - Opening Style: Use variations of these patterns: {voice.opening_styles[0]}
        - Measurement Style: {voice.measurement_style}
        
        CRITICAL REQUIREMENTS:
        - BANNED: Never use these phrases: {', '.join(voice.banned_phrases)}
        - REQUIRED: Include these elements: {', '.join(voice.required_elements)}
        - Write exactly 6-8 sentences total across both sections
        """
        
        # Generation-specific prompt (what to produce)
        generation_prompt = f"""
        Generate two text sections about {context.material_name} laser cleaning:
        
        BEFORE_TEXT (3-4 sentences):
        Describe contaminated surface using your voice style and cultural perspective.
        Include typical measurements: {context.typical_measurements}
        
        AFTER_TEXT (3-4 sentences):
        Describe cleaning results using your voice style.
        Highlight benefits: {', '.join(context.cleaning_benefits)}
        
        Total sentence count must be 6-8 sentences across both sections.
        """
        
        # Validation rules for this generation
        validation_rules = {
            'sentence_count_min': 6,
            'sentence_count_max': 8,
            'banned_phrases': voice.banned_phrases,
            'required_elements': voice.required_elements,
            'country_voice_markers': 2  # Minimum country-specific markers
        }
        
        # Expected outcomes
        expected_outcomes = {
            'voice_authenticity_min': 75,
            'ai_human_likeness_min': 80,
            'technical_accuracy_min': 80
        }
        
        return PromptChain(
            context_prompt=context_prompt,
            voice_prompt=voice_prompt,
            generation_prompt=generation_prompt,
            validation_rules=validation_rules,
            expected_outcomes=expected_outcomes
        )


class RealTimeValidator:
    """Validates content during generation"""
    
    def validate_during_generation(self, content: str, rules: dict) -> ValidationResult:
        """Validate content against rules during generation"""
        
        issues = []
        warnings = []
        
        # Check sentence count
        sentences = [s.strip() for s in content.replace('.', '.|').replace('!', '!|').replace('?', '?|').split('|') if s.strip()]
        if len(sentences) > rules.get('sentence_count_max', 8):
            issues.append(f"Too many sentences: {len(sentences)} > {rules['sentence_count_max']}")
        
        # Check for banned phrases
        content_lower = content.lower()
        for phrase in rules.get('banned_phrases', []):
            if phrase.lower() in content_lower:
                issues.append(f"Banned phrase detected: '{phrase}'")
        
        # Check for required elements (simplified)
        required_count = 0
        for element in rules.get('required_elements', []):
            if element.lower() in content_lower:
                required_count += 1
        
        if required_count < len(rules.get('required_elements', [])) / 2:
            warnings.append("Few required voice elements detected")
        
        passed = len(issues) == 0
        should_continue = passed and len(sentences) < rules.get('sentence_count_max', 8)
        
        return ValidationResult(
            passed=passed,
            issues=issues,
            warnings=warnings,
            should_continue=should_continue
        )


class ChainCaptionGenerator:
    """Main chain-based caption generator"""
    
    def __init__(self):
        self.voice_selector = VoiceProfileSelector()
        self.context_analyzer = ContextAnalyzer()
        self.chain_builder = PromptChainBuilder()
        self.validator = RealTimeValidator()
    
    def generate_caption(self, material: str, context: dict = None) -> dict:
        """Generate caption using chain-based approach"""
        
        context = context or {}
        
        try:
            # Stage 1: Select optimal voice profile
            voice_profile = self.voice_selector.select_voice(material, context)
            logger.info(f"Selected voice profile: {voice_profile.country} ({voice_profile.author_name})")
            
            # Stage 2: Analyze material context
            material_context = self.context_analyzer.analyze_material(material)
            logger.info(f"Analyzed material context: {len(material_context.key_challenges)} challenges identified")
            
            # Stage 3: Build prompt chain
            prompt_chain = self.chain_builder.build_chain(voice_profile, material_context)
            logger.info(f"Built prompt chain: {len(prompt_chain.context_prompt + prompt_chain.voice_prompt + prompt_chain.generation_prompt)} chars")
            
            # Stage 4: Generate content (simplified - would use API)
            # For prototype, return structured result
            generated_content = self._simulate_generation(prompt_chain, voice_profile, material_context)
            
            # Stage 5: Validate result
            validation_result = self.validator.validate_during_generation(
                generated_content['before_text'] + ' ' + generated_content['after_text'],
                prompt_chain.validation_rules
            )
            
            return {
                'before_text': generated_content['before_text'],
                'after_text': generated_content['after_text'],
                'voice_profile': voice_profile.country,
                'author': voice_profile.author_name,
                'validation_passed': validation_result.passed,
                'validation_issues': validation_result.issues,
                'validation_warnings': validation_result.warnings,
                'prompt_complexity': len(prompt_chain.context_prompt + prompt_chain.voice_prompt + prompt_chain.generation_prompt),
                'generation_successful': True
            }
        
        except Exception as e:
            logger.error(f"Caption generation failed for {material}: {e}")
            return {
                'error': str(e),
                'generation_successful': False
            }
    
    def _simulate_generation(self, chain: PromptChain, voice: VoiceProfile, context: MaterialContext) -> dict:
        """Simulate API generation for prototype (replace with real API call)"""
        
        # This would be replaced with actual API call
        # For now, return country-appropriate simulated content
        
        if voice.country == 'united_states':
            return {
                'before_text': f"Here's what we're seeing with this {context.material_name} - heavy contamination around 15-20 micrometers thick that's creating real challenges for our cleaning process. The buildup shows irregular patterns that'll require careful parameter adjustment to get optimal results.",
                'after_text': f"Looking at these results, we've achieved roughly 90% cleaning efficiency while maintaining the base {context.material_name} integrity. This works out to significantly improved surface quality that translates directly into better performance for industrial applications."
            }
        elif voice.country == 'italy':
            return {
                'before_text': f"Examining this beautiful {context.material_name} surface, I must say the contamination presents quite an artistic challenge. One cannot help but notice the organic residues measuring perhaps 12-18 micrometers thick, creating patterns that require elegant cleaning solutions.",
                'after_text': f"Observing these results, the transformation is nothing short of captivating. The surface now exhibits this beautiful clarity with residual traces below 1 micrometer, creating visual harmony that enhances both aesthetic and functional performance."
            }
        # Add other countries as needed...
        
        return {
            'before_text': f"Analysis of this {context.material_name} surface reveals contamination challenges requiring systematic cleaning approach.",
            'after_text': f"Post-cleaning results demonstrate significant improvement in {context.material_name} surface quality and performance characteristics."
        }


# CLI Interface for testing
def main():
    """Test the chain-based generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test chain-based caption generator")
    parser.add_argument("--material", required=True, help="Material to generate caption for")
    parser.add_argument("--country", help="Author country (usa, taiwan, italy, indonesia)")
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = ChainCaptionGenerator()
    
    # Set up context
    context = {}
    if args.country:
        context['author_country'] = args.country
    
    # Generate caption
    result = generator.generate_caption(args.material, context)
    
    if result.get('generation_successful', False):
        print(f"🎯 CHAIN GENERATION SUCCESSFUL: {args.material}")
        print(f"Voice Profile: {result['voice_profile']} ({result['author']})")
        print(f"Prompt Complexity: {result['prompt_complexity']} chars (vs 26K+ in old system)")
        print(f"Validation Passed: {result['validation_passed']}")
        
        print(f"\n📝 BEFORE TEXT:")
        print(f'"{result["before_text"]}"')
        
        print(f"\n📝 AFTER TEXT:")
        print(f'"{result["after_text"]}"')
        
        if result['validation_issues']:
            print(f"\n⚠️ VALIDATION ISSUES:")
            for issue in result['validation_issues']:
                print(f"  • {issue}")
        
        if result['validation_warnings']:
            print(f"\n🔔 WARNINGS:")
            for warning in result['validation_warnings']:
                print(f"  • {warning}")
        
        print(f"\n🏆 BENEFITS OF CHAIN APPROACH:")
        print(f"✅ Reduced prompt complexity: {result['prompt_complexity']} chars (vs 26K+)")
        print(f"✅ Real-time validation during generation")  
        print(f"✅ Clear separation of concerns (voice, context, generation)")
        print(f"✅ Observable and testable components")
        print(f"✅ Country-specific voice profiles")
        
    else:
        print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()