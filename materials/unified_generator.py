#!/usr/bin/env python3
"""
Unified Materials Content Generator

TEXT CONTENT GENERATOR for caption, FAQ, and subtitle generation ONLY.
Used by shared/commands/generation.py (--caption, --subtitle, --faq commands).

ARCHITECTURE:
- Integrates with /processing/orchestrator.py for dynamic generation
- Uses slider-driven configuration (processing/config.yaml)
- Applies author voice, sentence variation, and human realism automatically
- Wraps processing system for materials-specific workflow

Usage:
    generator = UnifiedMaterialsGenerator(api_client)
    
    # Generate with dynamic processing
    generator.generate('Bronze', 'caption')   # Uses orchestrator
    generator.generate('Bronze', 'subtitle')  # Uses orchestrator
    generator.generate('Bronze', 'faq')       # Uses orchestrator
"""

import logging
import random
import re
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Optional

from materials.research.faq_topic_researcher import FAQTopicResearcher
from processing.orchestrator import Orchestrator
from processing.config.dynamic_config import DynamicConfig
from processing.config.author_config_loader import get_author_config

logger = logging.getLogger(__name__)

# Paths
MATERIALS_DATA_PATH = Path("data/materials/Materials.yaml")
PROMPTS_DIR = Path("prompts")


class UnifiedMaterialsGenerator:
    """
    Unified generator for all materials content types.
    
    Responsibilities:
    - Load and format prompt templates
    - Generate content via API
    - Extract and validate responses
    - Write to Materials.yaml atomically
    
    NOT Responsible For:
    - Author voice (use VoicePostProcessor separately)
    - Frontmatter export (handled by export pipeline)
    """
    
    def __init__(self, api_client):
        """
        Initialize unified generator.
        
        Args:
            api_client: API client for content generation (required)
        """
        if not api_client:
            raise ValueError("API client required for content generation")
        
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)
        
        # Load prompt templates
        self.prompts = {}
        for content_type in ['caption', 'faq', 'subtitle']:
            prompt_file = PROMPTS_DIR / f"{content_type}.txt"
            if prompt_file.exists():
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    self.prompts[content_type] = f.read()
                self.logger.debug(f"Loaded {content_type} prompt template")
            else:
                self.logger.warning(f"Prompt template not found: {prompt_file}")
        
        self.logger.info("UnifiedMaterialsGenerator initialized")
    
    def _load_materials_data(self) -> Dict:
        """Load Materials.yaml using centralized loader"""
        from data.materials import load_materials_data
        return load_materials_data()
    
    def _build_context(self, material_data: Dict) -> str:
        """Build context string from material data"""
        context_parts = []
        
        # Basic info
        if 'category' in material_data:
            context_parts.append(f"Category: {material_data['category']}")
        
        if 'description' in material_data:
            context_parts.append(f"Description: {material_data['description'][:300]}")
        
        # Key properties
        properties = material_data.get('materialProperties', {})
        key_props = []
        for prop in ['hardness', 'thermalConductivity', 'density', 'meltingPoint']:
            if prop in properties:
                key_props.append(f"{prop}: {properties[prop]}")
        
        if key_props:
            context_parts.append("Properties: " + ", ".join(key_props[:5]))
        
        return "\n".join(context_parts)
    
    def _format_prompt(self, content_type: str, material_name: str, material_data: Dict, **kwargs) -> str:
        """
        Format prompt template with material data and parameters.
        
        Args:
            content_type: Type of content ('caption', 'faq', 'subtitle')
            material_name: Name of material
            material_data: Material data dictionary
            **kwargs: Additional parameters for prompt formatting
            
        Returns:
            Formatted prompt string
        """
        if content_type not in self.prompts:
            raise ValueError(f"No prompt template for content type: {content_type}")
        
        prompt_template = self.prompts[content_type]
        
        # Build context
        context = self._build_context(material_data)
        
        # Legacy settings for caption/FAQ (subtitle uses orchestrator)
        legacy_settings = {
            'caption': {
                'min_words_before': 15,
                'max_words_before': 70,
                'min_words_after': 15,
                'max_words_after': 70,
            },
            'faq': {
                'min_count': 2,
                'max_count': 8,
                'word_count_range': '10-50',
            }
        }
        settings = legacy_settings.get(content_type, {})
        
        # Build format parameters
        format_params = {
            'material_name': material_name,
            'material': material_name,  # Alias for compatibility
            'context': context,
            'category': material_data.get('category', 'material'),
            'subcategory': material_data.get('subcategory', ''),
            'description': material_data.get('description', ''),
        }
        
        # Add author information if available
        author_data = material_data.get('author', {})
        if author_data:
            format_params['author'] = author_data.get('name', 'Expert')
            format_params['author_country'] = author_data.get('country', 'USA')
        else:
            format_params['author'] = 'Expert'
            format_params['author_country'] = 'USA'
        
        # Add content-type specific parameters
        if content_type == 'caption':
            format_params['target_words_before'] = random.randint(
                settings['min_words_before'], settings['max_words_before']
            )
            format_params['target_words_after'] = random.randint(
                settings['min_words_after'], settings['max_words_after']
            )
        
        elif content_type == 'faq':
            # Random count between min_count and max_count if not specified
            default_faq_count = random.randint(settings['min_count'], settings['max_count'])
            format_params['faq_count'] = kwargs.get('faq_count', default_faq_count)
            format_params['word_count_range'] = settings['word_count_range']
        
        # Override with any kwargs
        format_params.update(kwargs)
        
        # Format prompt
        try:
            formatted_prompt = prompt_template.format(**format_params)
        except KeyError as e:
            self.logger.error(f"Missing parameter in prompt template: {e}")
            raise
        
        # Add cache-busting
        random_seed = random.randint(10000, 99999)
        formatted_prompt += f"\n\n[Generation ID: {random_seed}]"
        
        return formatted_prompt
    
    def _generate_with_api(self, prompt: str, content_type: str) -> str:
        """Generate content using API (legacy method for caption/FAQ)"""
        # Legacy settings for caption/FAQ
        legacy_settings = {
            'caption': {'temperature': 0.6, 'max_tokens': 300},
            'faq': {'temperature': 0.7, 'max_tokens': 2000},
        }
        settings = legacy_settings.get(content_type, {'temperature': 0.7, 'max_tokens': 500})
        
        response = self.api_client.generate_simple(
            prompt=prompt,
            max_tokens=settings.get('max_tokens', 500),
            temperature=settings.get('temperature', 0.7)
        )
        
        if not response.success:
            raise ValueError(f"API generation failed: {response.error}")
        
        return response.content
    
    def _write_to_materials_yaml(self, material_name: str, content_type: str, content_data: Dict):
        """
        Write generated content to Materials.yaml atomically.
        
        Args:
            material_name: Name of material
            content_type: Type of content ('caption', 'faq', 'subtitle')
            content_data: Content data to write
        """
        # Load current data
        materials_data = self._load_materials_data()
        
        if material_name not in materials_data['materials']:
            raise ValueError(f"Material '{material_name}' not found in Materials.yaml")
        
        # Update content
        materials_data['materials'][material_name][content_type] = content_data
        
        # Atomic write via temp file
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            dir=MATERIALS_DATA_PATH.parent,
            delete=False,
            suffix='.yaml'
        ) as temp_f:
            yaml.dump(materials_data, temp_f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            temp_path = temp_f.name
        
        # Atomic rename
        Path(temp_path).replace(MATERIALS_DATA_PATH)
        self.logger.info(f"✅ {content_type} written to Materials.yaml → materials.{material_name}.{content_type}")
    
    def generate_caption(self, material_name: str, material_data: Dict) -> Dict[str, str]:
        """Generate before/after microscopy captions using processing orchestrator"""
        self.logger.info(f"📸 Generating caption for {material_name}")
        
        # Get author ID from material data
        author_id = material_data.get('author', {}).get('id', 2)  # Default to Alessandro
        
        # Initialize orchestrator with author-specific config
        author_config = get_author_config(author_id)
        dynamic_config = DynamicConfig(base_config=author_config)
        orchestrator = Orchestrator(
            api_client=self.api_client,
            dynamic_config=dynamic_config
        )
        
        # Generate using processing system (applies all sliders, voice, variation)
        result = orchestrator.generate(
            topic=material_name,
            component_type='caption',
            author_id=author_id,
            context=self._build_context(material_data)
        )
        
        if result['success']:
            response = result['text']
            word_count = len(response.split())
            self.logger.info(f"   ✅ Generated caption ({word_count} words)")
        else:
            self.logger.error(f"   ❌ Generation failed: {result['reason']}")
            # Fallback to legacy method if orchestrator fails
            return self._generate_caption_legacy(material_name, material_data)
        
        # Extract sections
        before_match = re.search(r'\*\*BEFORE_TEXT:\*\*\s*(.+?)(?=\*\*AFTER_TEXT:|\Z)', response, re.DOTALL)
        after_match = re.search(r'\*\*AFTER_TEXT:\*\*\s*(.+)', response, re.DOTALL)
        
        if not before_match or not after_match:
            # Fallback: split by paragraph
            paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
            if len(paragraphs) < 2:
                raise ValueError(f"Could not extract before/after sections: {response[:200]}")
            before_text = paragraphs[0]
            after_text = paragraphs[1]
        else:
            before_text = before_match.group(1).strip()
            after_text = after_match.group(1).strip()
        
        # Clean up markers
        before_text = re.sub(r'^\*\*(?:BEFORE_TEXT|AFTER_TEXT):\*\*\s*', '', before_text).strip()
        after_text = re.sub(r'^\*\*(?:BEFORE_TEXT|AFTER_TEXT):\*\*\s*', '', after_text).strip()
        
        caption_data = {
            'before': before_text,
            'after': after_text
        }
        
        self.logger.info(f"   Before: {len(before_text.split())} words")
        self.logger.info(f"   After: {len(after_text.split())} words")
        
        return caption_data
    
    def _generate_caption_legacy(self, material_name: str, material_data: Dict) -> Dict[str, str]:
        """Legacy caption generation as fallback (direct API, no orchestrator)"""
        self.logger.warning("Using legacy caption generation (orchestrator failed)")
        
        # Format prompt
        prompt = self._format_prompt('caption', material_name, material_data)
        
        # Generate
        response = self._generate_with_api(prompt, 'caption')
        
        # Extract sections
        before_match = re.search(r'\*\*BEFORE_TEXT:\*\*\s*(.+?)(?=\*\*AFTER_TEXT:|\Z)', response, re.DOTALL)
        after_match = re.search(r'\*\*AFTER_TEXT:\*\*\s*(.+)', response, re.DOTALL)
        
        if not before_match or not after_match:
            paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
            if len(paragraphs) < 2:
                raise ValueError(f"Could not extract before/after sections: {response[:200]}")
            before_text = paragraphs[0]
            after_text = paragraphs[1]
        else:
            before_text = before_match.group(1).strip()
            after_text = after_match.group(1).strip()
        
        before_text = re.sub(r'^\*\*(?:BEFORE_TEXT|AFTER_TEXT):\*\*\s*', '', before_text).strip()
        after_text = re.sub(r'^\*\*(?:BEFORE_TEXT|AFTER_TEXT):\*\*\s*', '', after_text).strip()
        
        return {'before': before_text, 'after': after_text}
    
    def generate_faq(self, material_name: str, material_data: Dict, faq_count: int = None, enhance_topics: bool = True) -> list:
        """
        Generate FAQ questions and answers using processing orchestrator.
        
        Args:
            material_name: Name of material
            material_data: Material data from Materials.yaml
            faq_count: Number of FAQ items to generate (2-8 if not specified)
            enhance_topics: Whether to enhance FAQ with topic keywords/statements
            
        Returns:
            List of FAQ dicts with question, answer, and optionally topic_keyword, topic_statement
        """
        # Randomize FAQ count between 2-8 if not specified
        if faq_count is None:
            faq_count = random.randint(2, 8)
        
        self.logger.info(f"❓ Generating {faq_count} FAQ items for {material_name}")
        
        # Get author ID from material data
        author_id = material_data.get('author', {}).get('id', 2)  # Default to Alessandro
        
        # Initialize orchestrator with author-specific config
        author_config = get_author_config(author_id)
        dynamic_config = DynamicConfig(base_config=author_config)
        orchestrator = Orchestrator(
            api_client=self.api_client,
            dynamic_config=dynamic_config
        )
        
        # Generate using processing system (applies all sliders, voice, variation)
        result = orchestrator.generate(
            topic=material_name,
            component_type='faq',
            author_id=author_id,
            context=self._build_context(material_data)
        )
        
        if result['success']:
            response = result['text']
            word_count = len(response.split())
            self.logger.info(f"   ✅ Generated FAQ content ({word_count} words)")
        else:
            self.logger.error(f"   ❌ Generation failed: {result['reason']}")
            # Fallback to legacy method if orchestrator fails
            return self._generate_faq_legacy(material_name, material_data, faq_count, enhance_topics)
        
        # Extract JSON - Look for the final FAQ JSON block specifically
        import json
        try:
            # Find the last JSON block with "faq" key
            faq_pattern = r'\{\s*"faq"\s*:\s*\[(.*?)\]\s*\}'
            matches = list(re.finditer(faq_pattern, response, re.DOTALL))
            
            if matches:
                # Use the last match (final FAQ output)
                json_str = matches[-1].group(0)
                data = json.loads(json_str)
                faq_list = data.get('faq', [])
            else:
                raise ValueError("Could not find FAQ JSON in response")
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse FAQ JSON: {e}")
            raise ValueError(f"Invalid FAQ JSON: {response[:200]}")
        
        if not faq_list:
            raise ValueError("FAQ list is empty")
        
        self.logger.info(f"   Generated {len(faq_list)} FAQ items")
        
        # INLINE TOPIC ENHANCEMENT (before Materials.yaml write)
        if enhance_topics:
            try:
                self.logger.info("🔍 Enhancing FAQ topics inline...")
                topic_researcher = FAQTopicResearcher(self.api_client)
                faq_list = topic_researcher.enhance_faq_topics(material_name, faq_list)
                self.logger.info("   ✅ Topic enhancement complete")
            except Exception as e:
                self.logger.warning(f"   ⚠️  Topic enhancement failed: {e}")
                self.logger.warning("   Continuing with non-enhanced FAQ")
        
        return faq_list
    
    def _generate_faq_legacy(self, material_name: str, material_data: Dict, faq_count: int, enhance_topics: bool) -> list:
        """Legacy FAQ generation as fallback (direct API, no orchestrator)"""
        self.logger.warning("Using legacy FAQ generation (orchestrator failed)")
        
        # Format prompt
        prompt = self._format_prompt('faq', material_name, material_data, faq_count=faq_count)
        
        # Generate
        response = self._generate_with_api(prompt, 'faq')
        
        # Extract JSON
        import json
        try:
            faq_pattern = r'\{\s*"faq"\s*:\s*\[(.*?)\]\s*\}'
            matches = list(re.finditer(faq_pattern, response, re.DOTALL))
            
            if matches:
                json_str = matches[-1].group(0)
                data = json.loads(json_str)
                faq_list = data.get('faq', [])
            else:
                raise ValueError("Could not find FAQ JSON in response")
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse FAQ JSON: {e}")
            raise ValueError(f"Invalid FAQ JSON: {response[:200]}")
        
        if not faq_list:
            raise ValueError("FAQ list is empty")
        
        # Topic enhancement
        if enhance_topics:
            try:
                topic_researcher = FAQTopicResearcher(self.api_client)
                faq_list = topic_researcher.enhance_faq_topics(material_name, faq_list)
            except Exception as e:
                self.logger.warning(f"Topic enhancement failed: {e}")
        
        return faq_list
    
    def generate_subtitle(self, material_name: str, material_data: Dict) -> str:
        """
        Generate subtitle using processing orchestrator with dynamic config.
        Integrates with slider-driven system for sentence variation and length control.
        """
        self.logger.info(f"📝 Generating subtitle for {material_name}")
        
        # Get author ID from material data
        author_id = material_data.get('author', {}).get('id', 2)  # Default to Alessandro
        
        # Initialize orchestrator with author-specific config
        author_config = get_author_config(author_id)
        dynamic_config = DynamicConfig(base_config=author_config)
        orchestrator = Orchestrator(
            api_client=self.api_client,
            dynamic_config=dynamic_config
        )
        
        # Generate using processing system (applies all sliders, voice, variation)
        result = orchestrator.generate(
            topic=material_name,
            component_type='subtitle',
            author_id=author_id,
            context=self._build_context(material_data)
        )
        
        if result['success']:
            subtitle = result['text'].strip()
            word_count = len(subtitle.split())
            self.logger.info(f"   ✅ Generated: {subtitle[:80]}... ({word_count} words)")
            return subtitle
        else:
            self.logger.error(f"   ❌ Generation failed: {result['reason']}")
            # Fallback to legacy method if orchestrator fails
            return self._generate_subtitle_legacy(material_name, material_data)
    
    def _generate_subtitle_legacy(self, material_name: str, material_data: Dict) -> str:
        """Legacy subtitle generation as fallback (direct API, no orchestrator)"""
        # Build simple prompt without orchestrator
        prompt = f"Generate a concise subtitle (8-15 words) for {material_name}.\n\nContext: {self._build_context(material_data)}\n\nSubtitle:"
        
        response = self.api_client.generate_simple(
            prompt=prompt,
            max_tokens=100,
            temperature=0.6
        )
        
        if not response.success:
            raise ValueError(f"API generation failed: {response.error}")
            
        subtitle = response.content.strip().split('\n')[0].strip().strip('"\'')
        return subtitle
    
    def generate_eeat(self, material_name: str, material_data: Dict) -> Optional[Dict]:
        """
        Generate EEAT section from regulatoryStandards (pure Python, no AI).
        
        EEAT (Experience, Expertise, Authoritativeness, Trustworthiness):
        - reviewedBy: Fixed string "Z-Beam Quality Assurance Team"
        - citations: 1-3 random regulatoryStandards descriptions
        - isBasedOn: 1 random regulatoryStandard with name and url
        
        Args:
            material_name: Name of material
            material_data: Material data from Materials.yaml
            
        Returns:
            EEAT dict or None if no regulatoryStandards available
        """
        self.logger.info(f"📊 Generating EEAT section for {material_name}")
        
        # Get regulatoryStandards
        regulatory_standards = material_data.get('regulatoryStandards', [])
        
        # Filter to dict entries only (skip any legacy string entries)
        dict_standards = [
            std for std in regulatory_standards 
            if isinstance(std, dict) and 'description' in std and 'url' in std
        ]
        
        if not dict_standards:
            self.logger.warning(f"No valid regulatoryStandards found for {material_name}")
            return None
        
        # Select 1-3 random standards for citations
        num_citations = random.randint(1, min(3, len(dict_standards)))
        citation_standards = random.sample(dict_standards, num_citations)
        
        # Convert to citation strings (just the description)
        citations = [std['description'] for std in citation_standards]
        
        # Select 1 random standard for isBasedOn
        based_on_standard = random.choice(dict_standards)
        is_based_on = {
            'name': based_on_standard['description'],
            'url': based_on_standard['url']
        }
        
        eeat_data = {
            'reviewedBy': 'Z-Beam Quality Assurance Team',
            'citations': citations,
            'isBasedOn': is_based_on
        }
        
        self.logger.info(f"   reviewedBy: {eeat_data['reviewedBy']}")
        self.logger.info(f"   citations: {num_citations} selected from {len(dict_standards)} standards")
        self.logger.info(f"   isBasedOn: {is_based_on['name'][:60]}...")
        
        return eeat_data
    
    def generate(self, material_name: str, content_type: str, **kwargs):
        """
        Generate content for material.
        
        Args:
            material_name: Name of material
            content_type: Type of content ('caption', 'faq', 'subtitle', 'eeat')
            **kwargs: Additional parameters (e.g., faq_count=8)
            
        Returns:
            Generated content (dict for caption/faq/eeat, str for subtitle)
        """
        # Load material data
        materials_data = self._load_materials_data()
        
        if material_name not in materials_data['materials']:
            raise ValueError(f"Material '{material_name}' not found in Materials.yaml")
        
        material_data = materials_data['materials'][material_name]
        
        # Generate based on type
        if content_type == 'caption':
            content_data = self.generate_caption(material_name, material_data)
        elif content_type == 'faq':
            content_data = self.generate_faq(material_name, material_data, **kwargs)
        elif content_type == 'subtitle':
            content_data = self.generate_subtitle(material_name, material_data)
        elif content_type == 'eeat':
            content_data = self.generate_eeat(material_name, material_data)
        else:
            raise ValueError(f"Unknown content type: {content_type}")
        
        # Write to Materials.yaml
        self._write_to_materials_yaml(material_name, content_type, content_data)
        
        return content_data
