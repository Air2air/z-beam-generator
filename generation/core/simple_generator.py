"""
Simple Generator - Single-Pass Content Generation

Clean, focused generator for the generation phase:
- ONE API call per material
- Single-pass generation (no automatic retries)
- Save directly to Materials.yaml with atomic writes
- Quality validation happens after save

Architecture:
    Generation Phase: Generate → Evaluate → Save → Learn (single-pass)
    Learning Phase: Analyze patterns, update recommendations (discrete)
    
Note: No automatic retry loop. Manual re-run required if quality insufficient.
Quality gates (Winston AI, Subjective Eval, Realism) provide feedback for learning
but do not trigger automatic regeneration.

Design Principles:
- Fail fast with clear error messages
- No fallbacks or defaults that hide problems
- Atomic file operations (never corrupt Materials.yaml)
- Simple, linear flow with explicit error handling
"""

import logging
import random
from pathlib import Path
from typing import Dict, Any
import yaml

logger = logging.getLogger(__name__)


class SimpleGenerator:
    """
    Single-pass generator for content creation.
    
    Responsibilities:
    - Load material data
    - Build prompt with facts
    - Make ONE API call
    - Save result to Materials.yaml
    
    Does NOT handle:
    - Quality validation (post-processing)
    - Retry loops (post-processing)
    - Learning feedback (post-processing)
    """
    
    def __init__(self, api_client, adapter=None):
        """
        Initialize simple generator.
        
        Args:
            api_client: API client for content generation (required)
            adapter: Domain adapter for extraction (optional)
        """
        if not api_client:
            raise ValueError("API client required for content generation")
        
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)
        
        # Initialize adapter
        if adapter is None:
            from generation.core.adapters.materials_adapter import MaterialsAdapter
            self.adapter = MaterialsAdapter()
        else:
            self.adapter = adapter
        
        # Initialize enricher for real facts
        from generation.enrichment.data_enricher import DataEnricher
        self.enricher = DataEnricher()
        
        # Load config for base parameters
        from generation.config.config_loader import get_config
        config = get_config()
        self.config = config.config
        
        # Dynamic config for parameter baseline
        from generation.config.dynamic_config import DynamicConfig
        self.dynamic_config = DynamicConfig()
        
        # Load personas
        self.personas = self._load_all_personas()
        
        self.logger.info("SimpleGenerator initialized (single-pass, no validation)")
    
    def _load_all_personas(self) -> Dict[int, Dict[str, Any]]:
        """Load all author personas from prompts/personas/ or domains/materials/prompts/personas/"""
        personas = {}
        
        # Try both locations (for backward compatibility)
        personas_dir = Path("prompts/personas")
        if not personas_dir.exists():
            personas_dir = Path("domains/materials/prompts/personas")
        
        if not personas_dir.exists():
            raise FileNotFoundError(f"Personas directory not found: {personas_dir}")
        
        for persona_file in personas_dir.glob("*.yaml"):
            with open(persona_file, 'r') as f:
                persona_data = yaml.safe_load(f)
                author_id = persona_data.get('id')  # Changed from 'author_id' to 'id'
                if author_id:
                    personas[author_id] = persona_data
        
        self.logger.info(f"Loaded {len(personas)} personas")
        return personas
    
    def _get_persona_by_author_id(self, author_id: int) -> Dict[str, Any]:
        """Get persona by author ID"""
        if author_id not in self.personas:
            raise ValueError(f"Persona not found for author_id {author_id}")
        return self.personas[author_id]
    
    def _load_materials_data(self) -> Dict:
        """Load materials data from Materials.yaml"""
        materials_path = Path("data/materials/Materials.yaml")
        if not materials_path.exists():
            raise FileNotFoundError(f"Materials.yaml not found: {materials_path}")
        
        with open(materials_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _build_context(self, material_data: Dict) -> str:
        """Build context from material properties"""
        properties = material_data.get('properties', {})
        context_parts = []
        
        for prop_name, prop_value in properties.items():
            if isinstance(prop_value, dict):
                value = prop_value.get('value', 'N/A')
                unit = prop_value.get('unit', '')
                context_parts.append(f"{prop_name}: {value} {unit}".strip())
            else:
                context_parts.append(f"{prop_name}: {prop_value}")
        
        return "\n".join(context_parts)
    
    def _get_base_parameters(self, component_type: str) -> Dict[str, Any]:
        """Get base generation parameters from dynamic config"""
        return {
            'temperature': self.dynamic_config.calculate_temperature(),
            'max_tokens': self.dynamic_config.calculate_max_tokens(component_type)
        }
    
    def generate(
        self,
        material_name: str,
        component_type: str,
        faq_count: int = None
    ) -> Dict[str, Any]:
        """
        Generate content with single API call AND save to Materials.yaml.
        
        Args:
            material_name: Name of material
            component_type: Type of component (caption, subtitle, faq)
            faq_count: Number of FAQ items (ignored for non-FAQ components)
            
        Returns:
            Dict with 'content', 'length', 'word_count', 'saved', 'temperature'
            
        Raises:
            ValueError: If material not found or generation fails
            FileNotFoundError: If required files missing
        """
        result = self.generate_without_save(material_name, component_type, faq_count)
        
        # Save to Materials.yaml
        self._save_to_yaml(material_name, component_type, result['content'])
        self.logger.info("💾 Saved to Materials.yaml")
        result['saved'] = True
        
        return result
    
    def generate_without_save(
        self,
        material_name: str,
        component_type: str,
        faq_count: int = None
    ) -> Dict[str, Any]:
        """
        Generate content WITHOUT saving to Materials.yaml.
        
        Used by QualityGatedGenerator to generate content that will only be
        saved if it passes quality gates.
        
        Args:
            material_name: Name of material
            component_type: Type of component (caption, subtitle, faq)
            faq_count: Number of FAQ items (ignored for non-FAQ components)
            
        Returns:
            Dict with 'content', 'length', 'word_count', 'saved'=False, 'temperature'
            
        Raises:
            ValueError: If material not found or generation fails
            FileNotFoundError: If required files missing
        """
        self.logger.info(f"\n🔄 SIMPLE GENERATION: {component_type} for {material_name}")
        
        # Validate component type exists
        from generation.core.component_specs import ComponentRegistry
        try:
            spec = ComponentRegistry.get_spec(component_type)
        except KeyError:
            raise ValueError(f"Unknown component type: {component_type}")
        
        # Load material data
        materials_data = self._load_materials_data()
        if material_name not in materials_data['materials']:
            raise ValueError(f"Material '{material_name}' not found in Materials.yaml")
        
        material_data = materials_data['materials'][material_name]
        
        # Get author and voice
        author_id = material_data.get('author', {}).get('id', 2)
        voice = self._get_persona_by_author_id(author_id)
        
        # Get facts and context
        facts = self.enricher.fetch_real_facts(material_name)
        context = self._build_context(material_data)
        
        # Get target length with variation
        target_length = random.randint(spec.min_length, spec.max_length)
        self.logger.info(f"🎯 Target: {target_length} words (range: {spec.min_length}-{spec.max_length})")
        
        # Get base parameters
        params = self._get_base_parameters(component_type)
        self.logger.info(f"🌡️  Temperature: {params['temperature']:.3f}")
        
        # Build prompt (voice_params and enrichment_params come from dynamic_config if needed)
        from generation.core.prompt_builder import PromptBuilder
        prompt = PromptBuilder.build_unified_prompt(
            topic=material_name,
            voice=voice,
            length=target_length,
            facts=facts,
            context=context,
            component_type=component_type,
            domain='materials'
        )
        
        # Make API call
        self.logger.info("📡 Making API request...")
        from shared.api.client import GenerationRequest
        
        try:
            request = GenerationRequest(
                prompt=prompt,
                max_tokens=params['max_tokens'],
                temperature=params['temperature'],
                **params.get('api_penalties', {})
            )
            
            response = self.api_client.generate(request)
        except Exception as e:
            raise ValueError(f"API call failed: {e}")
        
        # Extract content from APIResponse object
        if not response or not response.success or not response.content or not response.content.strip():
            raise ValueError("Empty or failed response from API")
        
        # Extract content using adapter
        try:
            content = self.adapter.extract_content(response.content, component_type)
        except Exception as e:
            raise ValueError(f"Content extraction failed: {e}")
        
        # Calculate word count (handle both string and dict content)
        if isinstance(content, dict):
            # Caption has before/after structure
            word_count = sum(len(str(v).split()) for v in content.values() if v)
            char_count = sum(len(str(v)) for v in content.values() if v)
        elif isinstance(content, list):
            # FAQ has list of Q&A dicts
            word_count = sum(len(qa.get('answer', '').split()) for qa in content)
            char_count = sum(len(qa.get('answer', '')) for qa in content)
        else:
            # String content (subtitle, etc.)
            word_count = len(str(content).split())
            char_count = len(str(content))
        
        self.logger.info(f"✅ Generated: {char_count} chars, {word_count} words")
        
        return {
            'content': content,
            'length': char_count,
            'word_count': word_count,
            'saved': False,
            'temperature': params['temperature']
        }
    
    def _save_to_yaml(self, material_name: str, component_type: str, content: Any):
        """Save generated content to Materials.yaml with atomic write."""
        materials_path = Path("data/materials/Materials.yaml")
        
        # Load existing data
        try:
            with open(materials_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            raise FileNotFoundError(f"Failed to load Materials.yaml: {e}")
        
        if material_name not in data['materials']:
            raise ValueError(f"Material '{material_name}' not found in Materials.yaml")
        
        # Ensure components section exists
        if 'components' not in data['materials'][material_name]:
            data['materials'][material_name]['components'] = {}
        
        # Update content
        data['materials'][material_name]['components'][component_type] = content
        
        # Atomic write: write to temp file, then rename
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(
                mode='w',
                encoding='utf-8',
                dir=materials_path.parent,
                delete=False,
                suffix='.yaml'
            ) as temp_f:
                yaml.safe_dump(data, temp_f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                temp_path = temp_f.name
            
            # Atomic rename (POSIX guarantees atomicity)
            Path(temp_path).replace(materials_path)
        except Exception as e:
            # Clean up temp file on failure
            if 'temp_path' in locals():
                Path(temp_path).unlink(missing_ok=True)
            raise ValueError(f"Failed to save to Materials.yaml: {e}")
