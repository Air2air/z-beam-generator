#!/usr/bin/env python3
"""FAQ Component Generator - Material-Specific Question/Answer Generation with Author Voice"""

import datetime
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
        self.min_questions = 7
        self.max_questions = 12
        self.min_words_per_answer = 150
        self.max_words_per_answer = 300
        
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
    
    def _determine_question_count(self, material_data: Dict, category: str) -> int:
        """Determine optimal question count (7-12) based on material complexity
        
        Args:
            material_data: Material data from Materials.yaml
            category: Material category (metal, ceramic, etc.)
            
        Returns:
            Question count between 7 and 12
        """
        complexity_score = 0
        
        # Factor 1: Number of material properties
        props = material_data.get('materialProperties', {})
        prop_count = 0
        for category_key in ['material_characteristics', 'laser_material_interaction']:
            if category_key in props:
                prop_count += len(props[category_key])
        
        if prop_count > 20:
            complexity_score += 3
        elif prop_count > 10:
            complexity_score += 2
        else:
            complexity_score += 1
        
        # Factor 2: Number of applications
        app_count = len(material_data.get('applications', []))
        if app_count > 6:
            complexity_score += 2
        elif app_count > 3:
            complexity_score += 1
        
        # Factor 3: Hazardous/special materials get more questions
        safety_keywords = ['toxic', 'hazard', 'flammable', 'beryllium', 'lead', 'cadmium']
        material_name_lower = material_data.get('name', '').lower()
        if any(keyword in material_name_lower for keyword in safety_keywords):
            complexity_score += 2
        
        # Factor 4: Heritage/rare materials get more questions
        heritage_keywords = ['heritage', 'conservation', 'restoration', 'cultural', 'archaeological']
        applications = [app.lower() for app in material_data.get('applications', [])]
        if any(any(keyword in app for keyword in heritage_keywords) for app in applications):
            complexity_score += 1
        
        # Map complexity score to question count (7-12)
        if complexity_score >= 7:
            return 12
        elif complexity_score >= 5:
            return 10
        elif complexity_score >= 3:
            return 9
        else:
            return 7
    
    def _generate_material_questions(
        self,
        material_name: str,
        material_data: Dict,
        frontmatter_data: Dict,
        categories_data: Dict,
        question_count: int
    ) -> List[Dict]:
        """Generate material-specific questions with category tags
        
        Returns:
            List of question dictionaries with 'question', 'category', 'focus_points'
        """
        questions = []
        
        # Extract material context
        category = material_data.get('category', 'material')
        applications = material_data.get('applications', [])
        props = material_data.get('materialProperties', {})
        
        # Base questions for all materials (adapt to specific material)
        base_templates = [
            {
                'template': f"What types of contaminants can be removed from {material_name}?",
                'category': 'contaminants',
                'focus': 'Common contaminants, removal difficulty, material-specific challenges'
            },
            {
                'template': f"What makes {material_name} challenging to laser clean?",
                'category': 'material_handling',
                'focus': 'Material properties affecting cleaning, damage risks, parameter sensitivity'
            },
            {
                'template': f"Why is [wavelength] recommended for {material_name}?",
                'category': 'physical_properties',
                'focus': 'Wavelength selection, absorption characteristics, optimal parameters'
            },
            {
                'template': f"How does {material_name} compare to similar materials for laser cleaning?",
                'category': 'material_comparison',
                'focus': 'Category comparisons, unique characteristics, relative difficulty'
            },
            {
                'template': f"What surface quality results can I expect from laser cleaning {material_name}?",
                'category': 'outcome_quality',
                'focus': 'Surface finish, roughness, contaminant removal efficiency, damage indicators'
            },
            {
                'template': f"What are the environmental benefits of laser cleaning {material_name}?",
                'category': 'environmental',
                'focus': 'Chemical waste elimination, water reduction, energy efficiency, VOC reduction'
            },
        ]
        
        # Add application-specific question if primary application exists
        if applications:
            primary_app = applications[0]
            base_templates.append({
                'template': f"Why is laser cleaning preferred for {material_name} in {primary_app} applications?",
                'category': 'applications',
                'focus': f'Application requirements, industry standards, why laser vs alternatives for {primary_app}'
            })
        
        # Add questions based on material category
        if category == 'metal':
            # Check for high reflectivity
            laser_props = props.get('laser_material_interaction', {})
            reflectivity = None
            for prop_name in ['laserReflectivity', 'reflectivity']:
                if prop_name in laser_props:
                    reflectivity = laser_props[prop_name].get('value')
                    if reflectivity and reflectivity > 70:
                        questions.append({
                            'template': f"Why does {material_name}'s high reflectivity create laser safety challenges?",
                            'category': 'safety_hazards',
                            'focus': 'Reflectivity values, safety protocols, beam containment, PPE requirements'
                        })
                        break
            
            # Check for thermal conductivity
            thermal_cond = laser_props.get('thermalConductivity', {}).get('value')
            if thermal_cond and thermal_cond > 200:
                questions.append({
                    'template': f"How does {material_name}'s thermal conductivity affect laser cleaning strategy?",
                    'category': 'thermal_behavior',
                    'focus': 'Heat dissipation, parameter adjustments, thermal management'
                })
        
        elif category == 'ceramic' or category == 'stone':
            # Heritage/conservation questions
            if any('heritage' in app.lower() or 'conservation' in app.lower() for app in applications):
                questions.append({
                    'template': f"What conservation principles guide {material_name} laser cleaning?",
                    'category': 'heritage_conservation',
                    'focus': 'Reversibility, minimal intervention, authentication, patina preservation'
                })
        
        elif category == 'composite':
            questions.append({
                'template': f"How do {material_name}'s multiple material phases affect laser cleaning?",
                'category': 'composite_complexity',
                'focus': 'Fiber/matrix interaction, delamination risks, differential thermal response'
            })
        
        # Start with base templates
        for template_dict in base_templates[:question_count]:
            questions.append(template_dict)
        
        # Truncate or pad to exactly question_count
        if len(questions) > question_count:
            questions = questions[:question_count]
        elif len(questions) < question_count:
            # Add generic expansion questions
            remaining = question_count - len(questions)
            generic_questions = [
                {
                    'template': f"What are common troubleshooting issues when cleaning {material_name}?",
                    'category': 'troubleshooting',
                    'focus': 'Common problems, solutions, parameter adjustments'
                },
                {
                    'template': f"How do you verify successful {material_name} laser cleaning?",
                    'category': 'quality_verification',
                    'focus': 'Inspection methods, quality metrics, testing protocols'
                },
                {
                    'template': f"What safety precautions are critical for {material_name} laser cleaning?",
                    'category': 'safety',
                    'focus': 'Hazards, PPE, environmental controls, regulatory compliance'
                },
            ]
            questions.extend(generic_questions[:remaining])
        
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
            
            # Determine question count based on complexity
            category = full_material_data.get('category', 'material')
            question_count = self._determine_question_count(full_material_data, category)
            
            logger.info(f"📊 Generating {question_count} questions for {material_name} (category: {category})")
            
            # Generate questions
            questions = self._generate_material_questions(
                material_name,
                full_material_data,
                frontmatter_data,
                categories_yaml,
                question_count
            )
            
            # Generate answers for each question
            faq_items = []
            total_words = 0
            
            for idx, q_dict in enumerate(questions, 1):
                question = q_dict['template']
                category_tag = q_dict['category']
                focus = q_dict['focus']
                
                # Vary word count (150-300 range)
                if idx <= 2:
                    target_words = 295  # Comprehensive for early questions
                elif idx >= question_count - 1:
                    target_words = 280  # Moderate for late questions
                else:
                    target_words = 250  # Standard middle questions
                
                logger.info(f"  Question {idx}/{question_count}: {question[:60]}...")
                
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
                        'answer': answer.strip(),
                        'category': category_tag,
                        'word_count': word_count
                    })
                    
                    # Brief delay between API calls
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"    ❌ Failed to generate answer: {e}")
                    raise
            
            # Build FAQ structure
            author_obj = frontmatter_data.get('author', {})
            faq_structure = {
                'generated': datetime.datetime.now().isoformat() + 'Z',
                'author': author_obj.get('name', 'Unknown'),
                'generation_method': 'web_research_driven',
                'total_questions': len(faq_items),
                'total_words': total_words,
                'questions': faq_items
            }
            
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
