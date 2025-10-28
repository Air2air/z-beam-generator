#!/usr/bin/env python3
"""FAQ Component Generator - Material-Specific Question/Answer Generation with Author Voice"""

import json
import logging
import time
import yaml
from pathlib import Path
from typing import Dict, Optional, List
from generators.component_generators import APIComponentGenerator, ComponentResult
from utils.config_loader import load_yaml_config
from voice.orchestrator import VoiceOrchestrator

logger = logging.getLogger(__name__)


class FAQComponentGenerator(APIComponentGenerator):
    """Generate material-specific FAQ with 7-12 questions using author voice"""
    
    def __init__(self):
        super().__init__("faq")
        self.min_words_per_answer = 20
        self.max_words_per_answer = 60
        
    def _load_frontmatter_data(self, material_name: str) -> Dict:
        """Load frontmatter data for the material - case-insensitive search"""
        content_dir = Path("content/frontmatter")
        
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
    
    def _load_materials_data(self) -> Dict:
        """Load Materials.yaml for property lookups"""
        materials_path = Path("data/Materials.yaml")
        if materials_path.exists():
            try:
                return load_yaml_config(str(materials_path))
            except Exception as e:
                logger.warning(f"Could not load Materials.yaml: {e}")
        return {}
    
    def _load_categories_data(self) -> Dict:
        """Load Categories.yaml for range comparisons"""
        categories_path = Path("data/Categories.yaml")
        if categories_path.exists():
            try:
                return load_yaml_config(str(categories_path))
            except Exception as e:
                logger.warning(f"Could not load Categories.yaml: {e}")
        return {}
    
    def _generate_material_questions(
        self,
        material_name: str,
        material_data: Dict,
        frontmatter_data: Dict,
        categories_data: Dict,
        api_client=None
    ) -> List[Dict]:
        """Generate material-specific questions using AI research of public discourse
        
        Returns:
            List of question dictionaries with 'question', 'category', 'focus'
        """
        from research.topic_researcher import TopicResearcher
        
        if not api_client:
            raise ValueError("API client required for question generation")
        
        logger.info(f"🔍 Researching what people actually ask about {material_name}...")
        
        # Use TopicResearcher to find real public questions
        researcher = TopicResearcher(api_client)
        
        # Load cached research or perform new research
        research_data = researcher.load_cached_research(material_name, "faq_questions")
        
        if not research_data:
            # Perform AI research on what people actually ask
            research_prompt = f"""Research what people ACTUALLY ask about {material_name} in the context of laser cleaning and surface treatment.

PRIMARY FOCUS - Laser Cleaning:
1. Common questions from laser cleaning industry forums and discussions
2. Concerns raised in technical documentation and safety sheets
3. Questions from laser cleaning equipment manufacturers
4. Issues discussed in online communities and Q&A sites
5. Topics covered in training materials and guides

SECONDARY FOCUS - If laser cleaning information is limited:
6. General material characteristics relevant to surface treatment
7. Physical and chemical properties that affect cleaning methods
8. Common applications and handling requirements
9. Safety considerations and regulatory compliance
10. Industry-standard practices for this material

Generate 7-12 questions based on the material's complexity and available discourse.
Prioritize laser cleaning-specific questions, but include material characteristic questions if needed.

Format as JSON:
{{
  "questions": [
    {{
      "question": "The actual question people ask",
      "category": "topic_category",
      "focus": "Key points to address in the answer"
    }}
  ]
}}

Make questions specific to {material_name}, not generic questions."""
            
            research_result = api_client.generate_simple(
                research_prompt,
                max_tokens=2000,
                temperature=0.7
            )
            
            if not research_result.success:
                raise ValueError(f"Failed to research questions: {research_result.error}")
            
            # Parse JSON response (FAQ-specific structure)
            try:
                content = research_result.content.strip()
                # Extract JSON from markdown code blocks if present
                import re
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
                if not json_match:
                    # Try without code blocks
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                
                if json_match:
                    json_str = json_match.group(1) if json_match.lastindex else json_match.group()
                    research_data = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in AI response")
                    
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse AI response: {e}")
                logger.debug(f"Raw response: {research_result.content[:500]}...")
                raise ValueError(f"Invalid JSON response from AI: {e}")
            
            logger.info(f"✅ Generated {len(research_data.get('questions', []))} questions from AI research")
        
        # Extract questions from research
        questions = research_data.get('questions', [])
        
        # Validate we got questions
        if not questions:
            raise ValueError("Research returned no questions")
        
        # Return all AI-generated questions (AI determines optimal count)
        logger.info(f"✅ AI generated {len(questions)} questions based on material complexity")
        return questions

    
    def _build_faq_answer_prompt(
        self,
        material_name: str,
        question: str,
        focus_points: str,
        frontmatter_data: Dict,
        material_data: Dict,
        categories_data: Dict,
        target_words: int = 250
    ) -> str:
        """Build AI prompt for FAQ answer generation using Voice service
        
        Args:
            material_name: Name of the material
            question: The FAQ question
            focus_points: Key points to address in answer
            frontmatter_data: Frontmatter data dictionary
            material_data: Full material data from Materials.yaml
            categories_data: Category ranges from Categories.yaml
            target_words: Target word count (150-300)
            
        Returns:
            Complete prompt string for answer generation
        """
        # Extract author data
        author_obj = frontmatter_data.get('author', {})
        if not author_obj or not author_obj.get('country'):
            raise ValueError(f"No author data found for {material_name} - required for voice system")
        
        # Get author details
        author_name = author_obj.get('name', 'Unknown')
        author_country = author_obj.get('country', 'Unknown')
        author_expertise = author_obj.get('expertise', 'Laser cleaning technology')
        
        # Initialize VoiceOrchestrator for country-specific voice
        voice = VoiceOrchestrator(country=author_country)
        
        # Extract material properties for context
        material_props = material_data.get('materialProperties', {})
        category = material_data.get('category', 'material')
        applications = material_data.get('applications', [])
        machine_settings = material_data.get('machineSettings', {})
        
        # Build comprehensive material context
        properties_summary = {}
        for category_key in ['material_characteristics', 'laser_material_interaction']:
            if category_key in material_props:
                for prop_name, prop_data in material_props[category_key].items():
                    if isinstance(prop_data, dict) and 'value' in prop_data:
                        properties_summary[prop_name] = {
                            'value': prop_data['value'],
                            'unit': prop_data.get('unit', ''),
                            'min': prop_data.get('min'),
                            'max': prop_data.get('max')
                        }
        
        settings_summary = {}
        for setting_name, setting_data in machine_settings.items():
            if isinstance(setting_data, dict) and 'value' in setting_data:
                settings_summary[setting_name] = {
                    'value': setting_data['value'],
                    'unit': setting_data.get('unit', ''),
                    'description': setting_data.get('description', '')
                }
        
        # Get category ranges for comparison
        category_ranges = {}
        if category in categories_data.get('categories', {}):
            cat_data = categories_data['categories'][category]
            if 'category_ranges' in cat_data:
                category_ranges = cat_data['category_ranges']
        
        # Build material context dict
        material_context = {
            'material_name': material_name,
            'category': category,
            'applications': ', '.join(applications[:5]) if applications else 'General applications',
            'properties': json.dumps(properties_summary, indent=2),
            'machine_settings': json.dumps(settings_summary, indent=2),
            'category_ranges': json.dumps(category_ranges, indent=2) if category_ranges else 'No category data'
        }
        
        # Build author dict
        author_dict = {
            'name': author_name,
            'country': author_country,
            'expertise': author_expertise
        }
        
        # Call Voice service to generate FAQ answer prompt
        try:
            prompt = voice.get_unified_prompt(
                component_type='technical_faq_answer',
                material_context=material_context,
                author=author_dict,
                question=question,
                focus_points=focus_points,
                target_words=target_words,
                include_property_values=True,
                technical_depth='expert'
            )
            
            # Add word limit enforcement
            tolerance = 20
            prompt += f"\n\nSTRICT WORD LIMIT: Write {target_words} words (±{tolerance} words tolerance).\n"
            prompt += "CRITICAL: Include actual property values from material data in your answer.\n"
            prompt += "REQUIRED: Use author's country-specific voice and technical style.\n"
            prompt += f"MINIMUM: Write at least {self.min_words_per_answer} words for substantive content.\n"
            prompt += f"MAXIMUM: Do NOT exceed {self.max_words_per_answer} words.\n"
            
            logger.info(f"✅ Generated FAQ answer prompt for: {question[:50]}... ({author_country} voice, {target_words}w)")
            
            return prompt
            
        except Exception as e:
            logger.error(f"Failed to generate FAQ answer prompt via Voice service: {e}")
            raise
    
    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """Generate complete FAQ with 7-12 questions for the material
        
        Returns:
            ComponentResult with generated FAQ content in YAML format
        """
        try:
            logger.info(f"🎯 Generating FAQ for {material_name}...")
            
            # Load frontmatter if not provided
            if not frontmatter_data:
                frontmatter_data = self._load_frontmatter_data(material_name)
                if not frontmatter_data:
                    raise ValueError(f"No frontmatter data found for {material_name}")
            
            # Load Materials.yaml and Categories.yaml for context
            materials_yaml = self._load_materials_data()
            categories_yaml = self._load_categories_data()
            
            # Get material data from Materials.yaml
            if 'materials' in materials_yaml and material_name in materials_yaml['materials']:
                full_material_data = materials_yaml['materials'][material_name]
            else:
                full_material_data = material_data
            
            # Generate questions - AI determines optimal count
            logger.info(f"📊 Generating AI-researched questions for {material_name}")
            
            questions = self._generate_material_questions(
                material_name,
                full_material_data,
                frontmatter_data,
                categories_yaml,
                api_client
            )
            
            # Generate answers for each question
            faq_items = []
            total_words = 0
            total_questions = len(questions)
            
            for idx, q_dict in enumerate(questions, 1):
                question = q_dict.get('question') or q_dict.get('template')  # Support both AI-generated and legacy format
                focus = q_dict['focus']
                
                # Vary word count (20-60 range - concise and accessible)
                if idx <= 2:
                    target_words = 58  # Comprehensive for early questions
                elif idx >= total_questions - 1:
                    target_words = 55  # Moderate for late questions
                else:
                    target_words = 45  # Standard middle questions
                
                logger.info(f"  Question {idx}/{total_questions}: {question[:60]}...")
                
                # Build prompt
                prompt = self._build_faq_answer_prompt(
                    material_name,
                    question,
                    focus,
                    frontmatter_data,
                    full_material_data,
                    categories_yaml,
                    target_words
                )
                
                # Generate answer via API
                if not api_client:
                    raise ValueError("API client required for FAQ answer generation")
                
                # Calculate max_tokens for target word count (fail-fast: explicit values required)
                # FAQ answers: 150-300 words
                # Token estimation: ~1.3 tokens per word (conservative)
                # Safety margin: 1.5x to prevent truncation
                max_tokens = int(target_words * 1.3 * 1.5)  # Explicit calculation
                
                try:
                    response = api_client.generate_simple(
                        prompt,
                        max_tokens=max_tokens,  # Explicit - no defaults
                        temperature=0.6  # Slightly creative for natural FAQ responses
                    )
                    
                    if not response.success:
                        raise ValueError(f"API generation failed: {response.error}")
                    
                    answer = response.content
                    word_count = len(answer.split())
                    total_words += word_count
                    
                    # Validate word count
                    if word_count < self.min_words_per_answer:
                        logger.warning(f"    ⚠️  Answer too short: {word_count} words (min {self.min_words_per_answer})")
                    elif word_count > self.max_words_per_answer:
                        logger.warning(f"    ⚠️  Answer too long: {word_count} words (max {self.max_words_per_answer})")
                    else:
                        logger.info(f"    ✅ Answer generated: {word_count} words")
                    
                    faq_items.append({
                        'question': question,
                        'answer': answer.strip()
                    })
                    
                    # Brief delay between API calls
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"    ❌ Failed to generate answer: {e}")
                    raise
            
            # Build FAQ structure - simplified to only questions and answers
            faq_structure = faq_items
            
            # Convert to YAML format
            faq_yaml = yaml.dump({'faq': faq_structure}, 
                                default_flow_style=False, 
                                allow_unicode=True,
                                sort_keys=False)
            
            logger.info(f"✅ FAQ generation complete: {len(faq_items)} questions, {total_words} total words")
            
            return self._create_result(faq_yaml, success=True)
            
        except Exception as e:
            logger.error(f"❌ FAQ generation failed for {material_name}: {e}")
            from utils.ai.loud_errors import component_failure
            component_failure(self.component_type, str(e), material=material_name)
            return self._create_result("", success=False, error_message=str(e))
