#!/usr/bin/env python3
"""
Universal Text Field Enhancer
Handles all text field generation with Materials.yaml-first architecture
"""

import logging
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml
from api.client_factory import get_api_client_for_component


class TextFieldType(Enum):
    """Classification of text field types for prompt customization"""
    SUBTITLE = "subtitle"
    DESCRIPTION = "description"  
    TECHNICAL = "technical"
    SAFETY = "safety"
    APPLICATION = "application"
    CAPTION = "caption"
    PROPERTY_DESC = "property_description"
    GENERAL = "general"


class UniversalTextFieldEnhancer:
    """Universal text field generator with Materials.yaml persistence"""
    
    def __init__(self, config_path: str = None):
        """Initialize with configuration file path"""
        self.logger = logging.getLogger(__name__)
        
        # Default config path
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "enhanced_text_config.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # Materials.yaml path
        self.materials_path = Path("data/Materials.yaml")
        
        self.logger.info(f"✅ UniversalTextFieldEnhancer initialized with config: {self.config_path}")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            self.logger.info(f"📁 Configuration loaded from {self.config_path}")
            return config
        except Exception as e:
            self.logger.error(f"❌ Failed to load config from {self.config_path}: {e}")
            return {}

    def _classify_field_type(self, field_name: str) -> TextFieldType:
        """Classify field type for prompt customization"""
        if field_name in ['title', 'subtitle']:
            return TextFieldType.SUBTITLE
        elif field_name in ['description', 'desc']:
            return TextFieldType.DESCRIPTION
        elif field_name in ['technical_notes', 'technical', 'methodology', 'validation_method']:
            return TextFieldType.TECHNICAL
        elif field_name in ['safety_considerations', 'safety', 'safety_notes']:
            return TextFieldType.SAFETY
        elif field_name in ['applications', 'use_cases', 'application_notes']:
            return TextFieldType.APPLICATION
        elif field_name in ['caption', 'caption_beforeText', 'caption_afterText']:
            return TextFieldType.CAPTION
        elif 'description' in field_name.lower() or 'explanation' in field_name.lower():
            return TextFieldType.PROPERTY_DESC
        else:
            return TextFieldType.GENERAL

    def _build_enhanced_prompt(
        self,
        field_name: str,
        material_name: str,
        material_data: Dict[str, Any],
        field_type: TextFieldType,
        author_id: str = None
    ) -> str:
        """Build enhanced prompt with field-specific requirements"""
        
        # Get material properties for context
        material_props = material_data.get('materialProperties', {})
        applications = material_data.get('applications', [])
        material_category = material_data.get('category', 'unknown')
        
        # Select author if not provided (round-robin or random selection)
        if not author_id:
            author_profiles = self.config.get('author_profiles', {})
            available_authors = list(author_profiles.keys())
            if available_authors:
                import random
                author_id = random.choice(available_authors)
        
        # Get field-specific prompt configuration
        field_config = self._get_field_prompt_config(field_name)
        
        # Extract word count limits (author-specific)
        min_words, max_words = self._get_word_count_limits(field_name, author_id)
        
        # Get author-specific writing style
        author_style = self._get_author_style_instructions(author_id)
        
        # Build comprehensive prompt
        prompt = f"""
LASER CLEANING TECHNICAL CONTENT GENERATION

MATERIAL: {material_name}
CATEGORY: {material_category}
FIELD: {field_name}
AUTHOR: {author_id.upper()} ({self._get_author_name(author_id)})
WORD LIMIT: {'FLEXIBLE 20-80 words range (adapt to material complexity)' if field_name in ['caption_beforeText', 'caption_afterText'] else f'MAXIMUM {max_words} words (can be shorter if content is complete)'}

{field_config.get('base_instruction', 'Generate professional technical content')}

AUTHOR-SPECIFIC WRITING STYLE:
{author_style}

CONTENT REQUIREMENTS:
{self._format_content_focus(field_config.get('content_focus', []))}

TECHNICAL CONTEXT:
- Key Properties: {self._extract_key_properties(material_props)}
- Applications: {', '.join(applications[:2]) if applications else 'General industrial'}
- Material Category: {material_category}

CRITICAL CONSTRAINTS:
- WORD COUNT: {'20-80 words range for material-specific detail' if field_name in ['caption_beforeText', 'caption_afterText'] else f'Maximum {max_words} words - be concise, content can be shorter if complete'}
- TECHNICAL PRECISION: Use specific terminology and quantified values
- MATERIAL SPECIFICITY: Focus on unique aspects of {material_name}
- LASER CLEANING FOCUS: All content must relate to laser cleaning applications
- NO MARKETING LANGUAGE: Avoid promotional or sales-oriented terms
- AUTHOR VOICE: Follow {author_id.upper()} writing characteristics above

{self._get_field_specific_instructions(field_name, field_config)}

EXAMPLES TO FOLLOW:
{self._format_examples(field_config.get('examples', []))}

AVOID COMPLETELY:
{self._format_avoid_list(field_config.get('avoid', []))}

RESPONSE FORMAT:
- Respond with ONLY the requested content
- Do NOT include word counts, verification steps, or explanations
- Do NOT include "Word count:" or verification text
- Generate exactly {min_words}-{max_words} words of pure content

GENERATE CONTENT NOW:
"""
        
        return prompt

    def _get_field_prompt_config(self, field_name: str) -> Dict[str, Any]:
        """Get field-specific prompt configuration"""
        field_prompts = self.config.get('field_specific_prompts', {})
        return field_prompts.get(field_name, {})
    
    def _get_word_count_limits(self, field_name: str, author_id: str = None) -> tuple:
        """Get word count limits for field, with author-specific overrides"""
        
        # Try author-specific limits first
        if author_id:
            author_profiles = self.config.get('author_profiles', {})
            author_data = author_profiles.get(author_id, {})
            author_limits = author_data.get('word_count_limits', {})
            
            if field_name in author_limits:
                author_max = author_limits[field_name]
                # Special handling for caption fields - use random range 20-80
                if field_name in ['caption_beforeText', 'caption_afterText']:
                    import random
                    random_max = random.randint(20, min(80, author_max))
                    return 20, random_max
                # Use 1 as minimum, author limit as maximum for other fields
                return 1, author_max
        
        # Fall back to global quality standards
        quality_standards = self.config.get('quality_standards', {})
        min_counts = quality_standards.get('minimum_word_counts', {})
        max_counts = quality_standards.get('maximum_word_counts', {})
        
        min_words = min_counts.get(field_name, 3)
        max_words = max_counts.get(field_name, 8)
        
        return min_words, max_words
    
    def _format_content_focus(self, focus_list: list) -> str:
        """Format content focus points"""
        if not focus_list:
            return "- Focus on technical accuracy and laser cleaning relevance"
        return '\n'.join(f"- {focus}" for focus in focus_list)
    
    def _format_examples(self, examples: list) -> str:
        """Format example content"""
        if not examples:
            return "Use professional technical language with specific terminology"
        return '\n'.join(f'Example: "{example}"' for example in examples)
    
    def _format_avoid_list(self, avoid_list: list) -> str:
        """Format things to avoid"""
        if not avoid_list:
            return "- Avoid marketing language and unnecessary descriptive words"
        return '\n'.join(f"- {avoid}" for avoid in avoid_list)
    
    def _get_field_specific_instructions(self, field_name: str, field_config: Dict[str, Any]) -> str:
        """Get additional field-specific instructions"""
        instructions = []
        
        # Add format requirements if specified
        if 'format' in field_config:
            instructions.append(f"FORMAT REQUIREMENT: {field_config['format']}")
        
        # Add technical elements if specified
        if 'technical_elements' in field_config:
            elements = field_config['technical_elements']
            instructions.append("TECHNICAL ELEMENTS TO INCLUDE:")
            instructions.extend(f"- {element}" for element in elements)
        
        # Add specific field instructions
        if field_name in ['caption_beforeText', 'caption_afterText']:
            instructions.append("RETURN FORMAT: JSON structure as specified")
            instructions.append("MATERIAL-SPECIFIC FOCUS: Emphasize contamination types, measurements, and cleaning techniques unique to this material")
            instructions.append("QUANTIFICATION: Include specific measurements, percentages, and technical specifications")
            if field_name == 'caption_beforeText':
                instructions.append("CONTAMINATION EMPHASIS: Detail specific contamination types, thickness, and material property impacts")
            else:
                instructions.append("RESULTS EMPHASIS: Detail cleaning achievements, technique specifications, and quantified improvements")
        
        return '\n'.join(instructions) if instructions else ""

    def _get_author_name(self, author_id: str) -> str:
        """Get author display name"""
        if not author_id:
            return "Technical Specialist"
        
        author_profiles = self.config.get('author_profiles', {})
        author_data = author_profiles.get(author_id, {})
        return author_data.get('name', f'{author_id.title()} Specialist')

    def _get_author_style_instructions(self, author_id: str) -> str:
        """Get author-specific writing style instructions"""
        if not author_id:
            return "- Use professional technical language with precise terminology"
        
        # Get author profile data
        author_profiles = self.config.get('author_profiles', {})
        author_data = author_profiles.get(author_id, {})
        
        # Get author prompting strategy
        prompting_strategies = self.config.get('author_prompting_strategies', {})
        strategy_data = prompting_strategies.get(author_id, {})
        
        instructions = []
        
        # Add philosophy and approach
        philosophy = author_data.get('base_word_count_philosophy', '')
        approach = strategy_data.get('approach', '')
        if philosophy and approach:
            instructions.append(f"WRITING PHILOSOPHY: {philosophy.replace('_', ' ').title()}")
            instructions.append(f"APPROACH: {approach}")
        
        # Add sentence style
        sentence_style = strategy_data.get('sentence_style', '')
        if sentence_style:
            instructions.append(f"SENTENCE STYLE: {sentence_style}")
        
        # Add technical level
        technical_level = strategy_data.get('technical_level', '')
        if technical_level:
            instructions.append(f"TECHNICAL LEVEL: {technical_level}")
        
        # Add sentence patterns for structural guidance
        sentence_patterns = author_data.get('sentence_patterns', [])
        if sentence_patterns:
            instructions.append("SENTENCE STRUCTURES:")
            instructions.extend(f"- {pattern}" for pattern in sentence_patterns[:3])  # Limit to top 3
        
        # Add linguistic features for nationality-specific diction
        linguistic_features = author_data.get('linguistic_features', [])
        if linguistic_features:
            instructions.append("LINGUISTIC FEATURES:")
            instructions.extend(f"- {feature}" for feature in linguistic_features[:3])  # Limit to top 3
        
        # Add industry-specific terminology
        industry_terminology = author_data.get('industry_terminology', [])
        if industry_terminology:
            instructions.append("INDUSTRY TERMINOLOGY:")
            instructions.extend(f"- {term}" for term in industry_terminology[:3])  # Limit to top 3
        
        # Add technical confidence patterns
        technical_confidence = author_data.get('technical_confidence', [])
        if technical_confidence:
            instructions.append("TECHNICAL CONFIDENCE:")
            instructions.extend(f"- {conf}" for conf in technical_confidence[:2])  # Limit to top 2
        
        # Add measurement patterns
        measurement_patterns = author_data.get('measurement_patterns', [])
        if measurement_patterns:
            instructions.append("MEASUREMENT PATTERNS:")
            instructions.extend(f"- {pattern}" for pattern in measurement_patterns[:2])  # Limit to top 2
        
        # Add risk communication patterns
        risk_communication = author_data.get('risk_communication', [])
        if risk_communication:
            instructions.append("RISK COMMUNICATION:")
            instructions.extend(f"- {risk}" for risk in risk_communication[:2])  # Limit to top 2
        
        # Add process methodology
        process_methodology = author_data.get('process_methodology', [])
        if process_methodology:
            instructions.append("PROCESS METHODOLOGY:")
            instructions.extend(f"- {process}" for process in process_methodology[:2])  # Limit to top 2
        
        # Add discourse markers for logical flow
        discourse_markers = author_data.get('discourse_markers', [])
        if discourse_markers:
            instructions.append("DISCOURSE MARKERS:")
            instructions.extend(f"- {marker}" for marker in discourse_markers[:2])  # Limit to top 2
        
        # Add complexity level
        complexity_level = author_data.get('complexity_level', '')
        if complexity_level:
            instructions.append(f"COMPLEXITY APPROACH: {complexity_level.replace('_', ' ').title()}")
        
        # Add linguistic technicalities - Grammar & Stylistic Elements
        grammar_structures = author_data.get('grammar_structures', {})
        if grammar_structures:
            instructions.append("GRAMMAR STRUCTURES:")
            if 'sentence_patterns' in grammar_structures:
                instructions.extend(f"- {pattern}" for pattern in grammar_structures['sentence_patterns'][:2])
            if 'voice_preference' in grammar_structures:
                instructions.append(f"- Voice: {grammar_structures['voice_preference']}")
        
        diction_choices = author_data.get('diction_choices', {})
        if diction_choices:
            instructions.append("DICTION PATTERNS:")
            if 'register_selection' in diction_choices:
                instructions.append(f"- Register: {diction_choices['register_selection']}")
            if 'verb_preferences' in diction_choices:
                preferred_verbs = diction_choices['verb_preferences'][:3]  # Limit to 3
                instructions.append(f"- Preferred Verbs: {', '.join(preferred_verbs)}")
        
        stylistic_elements = author_data.get('stylistic_elements', {})
        if stylistic_elements:
            instructions.append("STYLISTIC ELEMENTS:")
            if 'paragraph_structure' in stylistic_elements:
                instructions.append(f"- Structure: {stylistic_elements['paragraph_structure']}")
            if 'transition_methods' in stylistic_elements:
                transitions = stylistic_elements['transition_methods'][:3]  # Limit to 3
                instructions.append(f"- Transitions: {', '.join(transitions)}")
        
        linguistic_markers = author_data.get('linguistic_markers', {})
        if linguistic_markers:
            instructions.append("LINGUISTIC MARKERS:")
            if 'modal_verbs' in linguistic_markers:
                modals = linguistic_markers['modal_verbs'][:2]  # Limit to 2
                instructions.append(f"- Modals: {', '.join(modals)}")
            if 'punctuation_style' in linguistic_markers:
                instructions.append(f"- Punctuation: {linguistic_markers['punctuation_style']}")
        
        # Add author characteristics (limited)
        characteristics = author_data.get('characteristics', [])
        if characteristics:
            instructions.append("KEY CHARACTERISTICS:")
            instructions.extend(f"- {char}" for char in characteristics[:2])  # Limit to top 2
        
        # Add preferred vocabulary
        vocab = author_data.get('vocabulary', {}).get('preferred_terms', [])
        if vocab:
            instructions.append(f"PREFERRED TERMS: {', '.join(vocab[:4])}")  # Limit to 4 terms
        
        # Add word count multiplier info
        multiplier = author_data.get('word_count_multiplier', 1.0)
        if multiplier != 1.0:
            if multiplier > 1.0:
                instructions.append(f"VERBOSITY: More detailed ({multiplier}x standard length)")
            else:
                instructions.append(f"CONCISENESS: More concise ({multiplier}x standard length)")
        
        return '\n'.join(instructions) if instructions else "- Use professional technical language"

    def _extract_key_properties(self, material_props: Dict[str, Any]) -> str:
        """Extract key material properties for context"""
        key_props = []
        
        # Look for laser-relevant properties
        for group_name, group_data in material_props.items():
            if isinstance(group_data, dict) and 'properties' in group_data:
                props = group_data['properties']
                
                # Priority properties for laser cleaning
                priority_props = ['density', 'meltingPoint', 'thermalConductivity', 'laserAbsorption', 'hardness']
                
                for prop in priority_props:
                    if prop in props and isinstance(props[prop], dict):
                        value = props[prop].get('value')
                        unit = props[prop].get('unit', '')
                        if value is not None:
                            key_props.append(f"{prop}: {value} {unit}".strip())
                            if len(key_props) >= 3:  # Limit to top 3 properties
                                break
                
                if len(key_props) >= 3:
                    break
        
        return '; '.join(key_props) if key_props else "Properties available in Materials.yaml"

    def _get_missing_text_fields(
        self,
        material_data: Dict[str, Any],
        force_refresh: bool
    ) -> list:
        """Identify text fields that need AI research"""
        
        # Standard text fields to research
        standard_text_fields = [
            'subtitle', 'description', 'technical_notes', 
            'safety_considerations', 'application_notes', 'caption_beforeText', 'caption_afterText'
        ]
        
        missing_fields = []
        existing_text_fields = material_data.get('ai_text_fields', {})
        
        for field_name in standard_text_fields:
            if force_refresh or field_name not in existing_text_fields:
                missing_fields.append(field_name)
                
        return missing_fields

    def _research_text_field(
        self,
        field_name: str,
        material_name: str,
        material_data: Dict[str, Any]
    ) -> Tuple[str, int, int]:
        """Research a single text field using AI"""
        
        field_type = self._classify_field_type(field_name)
        # Select author randomly for this field
        author_profiles = self.config.get('author_profiles', {})
        available_authors = list(author_profiles.keys())
        author_id = None
        if available_authors:
            import random
            author_id = random.choice(available_authors)
        
        prompt = self._build_enhanced_prompt(field_name, material_name, material_data, field_type, author_id)
        
        # Get word count targets from config
        field_config = self.config.get('quality_standards', {})
        max_words = field_config.get('maximum_word_counts', {}).get(field_name, 25)
        
        # Calculate max tokens (rough estimate: 1.3 tokens per word)
        # Special handling for caption fields that need 20-80 words (160-320 tokens)
        if field_name in ['caption_beforeText', 'caption_afterText']:
            max_tokens = 400  # Ample tokens for 20-80 words + buffer to avoid truncation
        else:
            # Use minimum of 50 tokens to allow proper generation, even for very short content
            max_tokens = max(50, min(200, int(max_words * 2.5)))  # Increased from 150 to 200, better token ratio
        
        try:
            # Get API client for caption component
            api_client = get_api_client_for_component("caption")
            
            self.logger.info(f"🌐 Making API request to {api_client.model}")
            self.logger.info(f"📝 Prompt length: {len(prompt)} chars")
            self.logger.info(f"🎯 Max tokens: {max_tokens}, Temperature: 0.3")
            
            response = api_client.generate_simple(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=0.3
            )
            
            if response and response.success and response.content:
                content = response.content.strip()
                word_count = len(content.split())
                char_count = len(content)
                
                self.logger.info(f"✅ Researched {field_name}: {char_count} characters")
                return content, word_count, char_count
            else:
                error_msg = response.error if response else "No response"
                self.logger.error(f"❌ API request failed for {field_name}: {error_msg}")
                return "", 0, 0
                
        except Exception as e:
            self.logger.error(f"❌ API request failed for {field_name}: {e}")
            return "", 0, 0

    def _persist_to_materials_yaml(
        self,
        material_name: str,
        text_fields: Dict[str, Dict[str, Any]]
    ) -> bool:
        """Persist text fields to Materials.yaml"""
        
        try:
            # Load current Materials.yaml
            with open(self.materials_path, 'r', encoding='utf-8') as f:
                materials_data = yaml.safe_load(f)
            
            # Create backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"data/Materials.backup_{timestamp}.yaml"
            with open(backup_path, 'w', encoding='utf-8') as f:
                yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True)
            self.logger.info(f"📋 Created backup: {backup_path}")
            
            # Update material with ai_text_fields
            if 'materials' not in materials_data:
                materials_data['materials'] = {}
            
            if material_name not in materials_data['materials']:
                materials_data['materials'][material_name] = {}
            
            materials_data['materials'][material_name]['ai_text_fields'] = text_fields
            
            # Save updated Materials.yaml
            with open(self.materials_path, 'w', encoding='utf-8') as f:
                yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True)
            
            self.logger.info(f"💾 Persisted {len(text_fields)} text fields to Materials.yaml")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to persist to Materials.yaml: {e}")
            return False

    def enhance_material_text_fields(
        self,
        material_name: str,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """Main method to enhance text fields for a material"""
        
        self.logger.info(f"🔬 Researching Text Fields for {material_name}")
        self.logger.info("Per DATA_STORAGE_POLICY.md: AI Research → Materials.yaml → Frontmatter")
        self.logger.info("=" * 60)
        
        try:
            # Load Materials.yaml to get material data
            with open(self.materials_path, 'r', encoding='utf-8') as f:
                materials_data = yaml.safe_load(f)
            
            material_data = materials_data.get('materials', {}).get(material_name, {})
            if not material_data:
                self.logger.error(f"❌ Material '{material_name}' not found in Materials.yaml")
                return {'success': False, 'error': f"Material '{material_name}' not found"}
            
            # Get missing text fields
            missing_fields = self._get_missing_text_fields(material_data, force_refresh)
            
            if not missing_fields:
                self.logger.info(f"✅ All text fields already exist for {material_name}")
                return {'success': True, 'fields_generated': 0}
            
            self.logger.info(f"🔬 Researching {len(missing_fields)} text fields for {material_name}")
            
            # Research each missing field
            text_fields = {}
            for field_name in missing_fields:
                content, word_count, char_count = self._research_text_field(
                    field_name, material_name, material_data
                )
                
                if content:
                    text_fields[field_name] = {
                        'content': content,
                        'source': 'ai_research',
                        'research_date': datetime.now(timezone.utc).isoformat(),
                        'word_count': word_count,
                        'character_count': char_count
                    }
            
            # Persist to Materials.yaml
            if text_fields and self._persist_to_materials_yaml(material_name, text_fields):
                self.logger.info(f"✅ Researched {len(text_fields)} text fields")
                
                # Show summary
                for field_name, field_data in text_fields.items():
                    content_preview = field_data['content'][:80] + "..." if len(field_data['content']) > 80 else field_data['content']
                    self.logger.info(f"  📄 {field_name}: {field_data['word_count']} words")
                    self.logger.info(f"      \"{content_preview}\"")
                
                return {
                    'success': True,
                    'fields_generated': len(text_fields),
                    'fields': text_fields
                }
            else:
                self.logger.error(f"❌ Failed to persist text fields for {material_name}")
                return {'success': False, 'error': 'Persistence failed'}
                
        except Exception as e:
            self.logger.error(f"❌ Error enhancing text fields for {material_name}: {e}")
            return {'success': False, 'error': str(e)}

    def research_and_persist_text_fields(
        self,
        material_name: str,
        api_client=None,
        force_refresh: bool = False
    ) -> Dict[str, str]:
        """CLI compatibility method - returns just the text content"""
        result = self.enhance_material_text_fields(material_name, force_refresh)
        
        if result['success'] and 'fields' in result:
            # Return just the content for CLI compatibility
            return {
                field_name: field_data['content'] 
                for field_name, field_data in result['fields'].items()
            }
        return {}


# Backward compatibility alias
EnhancedTextFieldManager = UniversalTextFieldEnhancer


def main():
    """CLI interface for testing"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python universal_text_enhancer.py <material_name> [--force]")
        sys.exit(1)
    
    material_name = sys.argv[1]
    force_refresh = '--force' in sys.argv
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    enhancer = UniversalTextFieldEnhancer()
    result = enhancer.enhance_material_text_fields(material_name, force_refresh)
    
    if result['success']:
        print(f"✅ Successfully enhanced {result.get('fields_generated', 0)} text fields")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


# Backward compatibility alias
EnhancedTextFieldManager = UniversalTextFieldEnhancer


if __name__ == "__main__":
    main()