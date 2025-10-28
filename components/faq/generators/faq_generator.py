#!/usr/bin/env python3
"""
FAQ Component Generator - Discrete, Simple Material-Specific Q&A Generation

This component is DISCRETE and FOCUSED:
- Generates material-specific FAQ questions and answers
- NO author voice functionality (handled by separate post-processor)
- NO frontmatter dependencies
- NO voice validation
- Minimal, clean interface
"""

import json
import logging
import os
import random
import tempfile
import time
import yaml
from pathlib import Path
from typing import Dict, List
from generators.component_generators import APIComponentGenerator, ComponentResult

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION
# ============================================================================

# Answer length constraints (words)
MIN_WORDS_PER_ANSWER = 15
MAX_WORDS_PER_ANSWER = 50

# Question generation settings
MIN_QUESTIONS = 5
MAX_QUESTIONS = 10
QUESTION_RESEARCH_MAX_TOKENS = 2000
QUESTION_RESEARCH_TEMPERATURE = 0.7

# Answer generation settings
ANSWER_GENERATION_TEMPERATURE = 0.6
TOKEN_ESTIMATION_PER_WORD = 1.3  # Conservative estimate
TOKEN_SAFETY_MARGIN = 1.5  # Prevent truncation

# API call delays
API_CALL_DELAY_SECONDS = 0.5

# Data file paths
MATERIALS_DATA_PATH = "data/Materials.yaml"
CATEGORIES_DATA_PATH = "data/Categories.yaml"

# ============================================================================


class FAQComponentGenerator(APIComponentGenerator):
    """
    Generate material-specific FAQ with 7-12 questions.
    
    Responsibilities:
    - Generate relevant questions based on material properties
    - Generate technical answers (20-60 words each)
    - Return FAQ data structure
    
    NOT Responsible For:
    - Author voice (use VoicePostProcessor separately)
    - Frontmatter management
    - Voice validation
    """
    
    def __init__(self):
        super().__init__("faq")
        self.min_words_per_answer = MIN_WORDS_PER_ANSWER
        self.max_words_per_answer = MAX_WORDS_PER_ANSWER
    
    def _load_materials_data(self) -> Dict:
        """Load Materials.yaml"""
        materials_path = Path(MATERIALS_DATA_PATH)
        if not materials_path.exists():
            raise FileNotFoundError(f"Materials.yaml not found at {materials_path}")
        
        with open(materials_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_categories_data(self) -> Dict:
        """Load Categories.yaml for property ranges"""
        categories_path = Path(CATEGORIES_DATA_PATH)
        if not categories_path.exists():
            raise FileNotFoundError(f"Categories.yaml not found at {categories_path}")
        
        with open(categories_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _generate_material_questions(
        self,
        material_name: str,
        material_data: Dict,
        categories_data: Dict,
        api_client
    ) -> List[Dict]:
        """
        Generate 7-12 material-specific FAQ questions using AI research.
        
        Args:
            material_name: Name of the material
            material_data: Material properties from Materials.yaml
            categories_data: Category ranges (currently unused, reserved for future)
            api_client: API client for generation
            
        Returns:
            List of question dictionaries with 'question', 'category', 'focus'
        """
        # Validate inputs
        if not material_data:
            raise ValueError(f"Empty material_data for {material_name}")
        
        # Extract material context
        category = material_data.get('category', 'material')
        material_props = material_data.get('materialProperties', {})
        applications = material_data.get('applications', [])
        machine_settings = material_data.get('machineSettings', {})
        
        # Build comprehensive research prompt
        research_prompt = f"""You are a laser cleaning expert researching frequently asked questions about {material_name}.

MATERIAL CONTEXT:
• Category: {category}
• Key Properties: {', '.join([f"{k}: {v}" for k, v in list(material_props.items())[:5]])}
• Applications: {', '.join(applications[:3]) if applications else 'General industrial use'}
• Machine Settings: Wavelength {machine_settings.get('wavelength', 'N/A')} nm, Power {machine_settings.get('power', 'N/A')} W

TASK: Generate {MIN_QUESTIONS}-{MAX_QUESTIONS} specific, practical questions that professionals ask about laser cleaning {material_name}.

REQUIREMENTS:
1. Questions must be SPECIFIC to {material_name} - not generic
2. Cover diverse categories: safety, effectiveness, equipment, applications, challenges
3. Address real-world concerns and technical details
4. Be practical and actionable
5. Focus on laser cleaning context specifically

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
            max_tokens=QUESTION_RESEARCH_MAX_TOKENS,
            temperature=QUESTION_RESEARCH_TEMPERATURE
        )
        
        if not research_result.success:
            raise ValueError(f"Failed to research questions: {research_result.error}")
        
        # Parse JSON response - simplified, fail-fast approach
        try:
            content = research_result.content.strip()
            
            # Try to extract JSON from markdown code blocks first
            if '```' in content:
                import re
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
                if json_match:
                    content = json_match.group(1)
            
            # Parse JSON
            research_data = json.loads(content)
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from AI: {e}")
            logger.debug(f"Raw response: {research_result.content[:500]}...")
            raise ValueError(f"AI returned invalid JSON for question research: {e}")
        
        questions = research_data.get('questions', [])
        
        if not questions:
            raise ValueError("Research returned no questions")
        
        logger.info(f"✅ AI generated {len(questions)} questions based on material complexity")
        return questions

    
    def _build_faq_answer_prompt(
        self,
        material_name: str,
        question: str,
        focus_points: str,
        material_data: Dict,
        categories_data: Dict,
        target_words: int = 45
    ) -> str:
        """
        Build simple, direct prompt for FAQ answer generation.
        NO voice functionality - just technical accuracy.
        
        Args:
            material_name: Name of the material
            question: The FAQ question
            focus_points: Key points to address
            material_data: Full material data from Materials.yaml
            categories_data: Category ranges from Categories.yaml
            target_words: Target word count (20-60)
            
        Returns:
            Complete prompt string for answer generation
        """
        # Extract material properties
        material_props = material_data.get('materialProperties', {})
        category = material_data.get('category', 'material')
        applications = material_data.get('applications', [])
        machine_settings = material_data.get('machineSettings', {})
        
        # Build material context
        material_context = f"""
MATERIAL: {material_name}
CATEGORY: {category}

KEY PROPERTIES:
{chr(10).join([f"• {k}: {v}" for k, v in material_props.items()])}

MACHINE SETTINGS:
• Wavelength: {machine_settings.get('wavelength', 'N/A')} nm
• Power: {machine_settings.get('power', 'N/A')} W
• Fluence: {machine_settings.get('fluence', 'N/A')} J/cm²
• Pulse Duration: {machine_settings.get('pulseDuration', 'N/A')} ns

APPLICATIONS:
{chr(10).join([f"• {app}" for app in applications])}
"""
        
        # Build simple, direct prompt
        prompt = f"""You are a laser cleaning expert answering a technical question about {material_name}.

{material_context}

QUESTION: {question}

FOCUS AREAS: {focus_points}

REQUIREMENTS:
1. Write EXACTLY {target_words} words (±5 words tolerance)
2. Be technically accurate - use actual property values from the material data
3. Be specific to {material_name} - not generic answers
4. Include concrete numbers and parameters
5. **ANSWER IN ENGLISH ONLY**

ANSWER ({target_words} words):"""
        
        return prompt
    
    def _write_faq_to_materials(
        self,
        material_name: str,
        faq_items: List[Dict]
    ) -> bool:
        """Write FAQ to Materials.yaml with atomic write"""
        
        materials_path = Path(MATERIALS_DATA_PATH)
        
        try:
            # Load Materials.yaml
            with open(materials_path, 'r', encoding='utf-8') as f:
                materials_data = yaml.safe_load(f) or {}
            
            # Navigate to materials section
            if 'materials' not in materials_data:
                raise ValueError("No 'materials' section found in Materials.yaml")
            
            materials_section = materials_data['materials']
            
            # Find material (case-insensitive)
            actual_key = None
            for key in materials_section.keys():
                if key.lower().replace('_', ' ') == material_name.lower().replace('_', ' '):
                    actual_key = key
                    break
            
            if not actual_key:
                raise ValueError(f"Material {material_name} not found in Materials.yaml")
            
            # Write FAQ
            materials_section[actual_key]['faq'] = faq_items
            
            # Atomic write using tempfile (matches Subtitle/Caption pattern)
            temp_fd, temp_path = tempfile.mkstemp(suffix='.yaml', dir=materials_path.parent)
            try:
                os.close(temp_fd)  # Close file descriptor before writing
                with open(temp_path, 'w', encoding='utf-8') as f:
                    yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                
                # Atomic rename
                Path(temp_path).replace(materials_path)
                logger.info(f"✅ FAQ written to Materials.yaml → materials.{actual_key}.faq")
                return True
                
            except Exception as e:
                # Cleanup temp file on error
                if Path(temp_path).exists():
                    Path(temp_path).unlink()
                raise e
            
        except Exception as e:
            logger.error(f"Failed to write FAQ to Materials.yaml: {e}")
            raise
    
    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        **kwargs  # Accept but ignore extra parameters
    ) -> ComponentResult:
        """
        Generate complete FAQ with 7-12 questions for the material.
        
        Args:
            material_name: Name of the material
            material_data: Material properties dictionary
            api_client: API client for generation (required)
            **kwargs: Extra parameters (ignored - for compatibility)
            
        Returns:
            ComponentResult with generated FAQ content in YAML format
        """
        try:
            # Input validation
            if not api_client:
                raise ValueError("API client required for FAQ generation")
            
            if not material_data or not isinstance(material_data, dict):
                raise ValueError(f"Valid material_data dict required for {material_name}")
            
            logger.info(f"🎯 Generating FAQ for {material_name}...")
            
            # Load data files
            materials_yaml = self._load_materials_data()
            categories_yaml = self._load_categories_data()
            
            # Get full material data from Materials.yaml
            if 'materials' in materials_yaml and material_name in materials_yaml['materials']:
                full_material_data = materials_yaml['materials'][material_name]
            else:
                full_material_data = material_data
            
            # Generate questions - AI determines optimal count
            logger.info(f"📊 Generating AI-researched questions for {material_name}")
            
            questions = self._generate_material_questions(
                material_name,
                full_material_data,
                categories_yaml,
                api_client
            )
            
            # Generate answers for each question
            faq_items = []
            total_words = 0
            total_questions = len(questions)
            
            for idx, q_dict in enumerate(questions, 1):
                question = q_dict.get('question') or q_dict.get('template')
                focus = q_dict['focus']
                
                # Completely random word count between min and max
                target_words = random.randint(MIN_WORDS_PER_ANSWER, MAX_WORDS_PER_ANSWER)
                
                logger.info(f"  Question {idx}/{total_questions}: {question[:60]}... (target: {target_words}w)")
                
                # Build prompt - simple and direct
                prompt = self._build_faq_answer_prompt(
                    material_name,
                    question,
                    focus,
                    full_material_data,
                    categories_yaml,
                    target_words
                )
                
                # Calculate max_tokens
                max_tokens = int(target_words * TOKEN_ESTIMATION_PER_WORD * TOKEN_SAFETY_MARGIN)
                
                try:
                    # Generate answer
                    response = api_client.generate_simple(
                        prompt,
                        system_prompt=None,
                        max_tokens=max_tokens,
                        temperature=ANSWER_GENERATION_TEMPERATURE
                    )
                    
                    if not response.success:
                        raise ValueError(f"API generation failed: {response.error}")
                    
                    answer = response.content.strip()
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
                        'answer': answer
                    })
                    
                    # Brief delay between API calls
                    time.sleep(API_CALL_DELAY_SECONDS)
                    
                except Exception as e:
                    logger.error(f"    ❌ Failed to generate answer: {e}")
                    raise
            
            # Build simple FAQ structure - just questions and answers
            faq_structure = faq_items
            
            # Convert to YAML format
            faq_yaml = yaml.dump({'faq': faq_structure}, 
                                default_flow_style=False, 
                                allow_unicode=True,
                                sort_keys=False)
            
            logger.info(f"✅ FAQ generation complete: {len(faq_items)} questions, {total_words} total words")
            
            # Write to Materials.yaml using dedicated method (atomic write)
            self._write_faq_to_materials(
                material_name=material_name,
                faq_items=faq_structure
            )
            
            return self._create_result(faq_yaml, success=True)
            
        except Exception as e:
            logger.error(f"FAQ generation failed: {e}")
            return self._create_result("", success=False, error_message=str(e))
