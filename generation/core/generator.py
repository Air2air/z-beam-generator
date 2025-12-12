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
import re
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

logger = logging.getLogger(__name__)


class Generator:
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
    
    def __init__(self, api_client, domain: str = 'materials', adapter=None):
        """
        Initialize generator for any domain.
        
        Args:
            api_client: API client for content generation (required)
            domain: Domain name (e.g., 'materials', 'settings') - determines config
            adapter: Optional pre-configured adapter (overrides domain parameter)
        """
        if not api_client:
            raise ValueError("API client required for content generation")
        
        self.api_client = api_client
        self.domain = domain
        self.logger = logging.getLogger(__name__)
        
        # Initialize adapter - use DomainAdapter for config-driven behavior
        if adapter is None:
            from generation.core.adapters.domain_adapter import DomainAdapter
            self.adapter = DomainAdapter(domain)
        else:
            self.adapter = adapter
        
        # Initialize enricher for real facts
        from generation.enrichment.data_enricher import DataEnricher
        self.enricher = DataEnricher()
        
        # Initialize research capabilities (NEW - Dec 11, 2025)
        from shared.text.research import SystemDataResearcher
        self.researcher = SystemDataResearcher()
        
        # Initialize cross-linking builder (NEW - Dec 11, 2025)
        from shared.text.cross_linking import CrossLinkBuilder
        self.link_builder = CrossLinkBuilder()
        
        # Load config for base parameters
        from generation.config.config_loader import get_config
        config = get_config()
        self.config = config.config
        
        # Dynamic config for parameter baseline
        from generation.config.dynamic_config import DynamicConfig
        self.dynamic_config = DynamicConfig()
        
        # Load personas
        self.personas = self._load_all_personas()
        
        self.logger.info(f"Generator initialized for '{domain}' domain (single-pass with research + cross-linking)")
    
    def _load_all_personas(self) -> Dict[int, Dict[str, Any]]:
        """Load all author voice profiles from shared/voice/profiles/"""
        personas = {}
        
        # Use shared/voice location (correct path per policy)
        personas_dir = Path("shared/voice/profiles")
        if not personas_dir.exists():
            raise FileNotFoundError(f"Voice profiles directory not found: {personas_dir}")
        
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
    
    def _load_data(self) -> Dict:
        """Load data using domain adapter"""
        return self.adapter.load_all_data()
    
    def _get_item_data(self, identifier: str) -> Dict:
        """Get item data using domain adapter"""
        return self.adapter.get_item_data(identifier)
    
    def _build_context(self, item_data: Dict) -> str:
        """Build context using domain adapter"""
        return self.adapter.build_context(item_data)
    
    def _get_base_parameters(self, component_type: str) -> Dict[str, Any]:
        """Get base generation parameters from dynamic config"""
        return {
            'temperature': self.dynamic_config.calculate_temperature(),
            'max_tokens': self.dynamic_config.calculate_max_tokens(component_type)
        }
    
    def generate(
        self,
        identifier: str,
        component_type: str,
        faq_count: int = None
    ) -> Dict[str, Any]:
        """
        Generate content with single API call AND save to domain data file.
        
        Args:
            identifier: Item name (material, setting, etc.) - domain agnostic
            component_type: Type of component (caption, material_description, faq)
            faq_count: Number of FAQ items (ignored for non-FAQ components)
            
        Returns:
            Dict with 'content', 'length', 'word_count', 'saved', 'temperature'
            
        Raises:
            ValueError: If identifier not found or generation fails
            FileNotFoundError: If required files missing
        """
        # TEMPORARY DISABLE: Humanness layer conflicts with voice policy (forbidden phrases)
        # Generate humanness layer with randomized length from config
        # from learning.humanness_optimizer import HumannessOptimizer
        # humanness_optimizer = HumannessOptimizer()
        # humanness_layer = humanness_optimizer.generate_humanness_instructions(
        #     component_type=component_type,
        #     strictness_level=1  # Production mode uses level 1 (lowest strictness)
        # )
        # self.logger.info(f"🧠 Generated humanness layer ({len(humanness_layer)} chars)")
        
        humanness_layer = None  # DISABLED: Conflicts with persona forbidden phrases
        self.logger.info(f"⚠️  Humanness layer DISABLED (conflicts with voice policy)")
        
        result = self.generate_without_save(identifier, component_type, faq_count, humanness_layer)

        
        # Save using domain adapter (handles correct file path automatically)
        self.adapter.write_component(identifier, component_type, result['content'])
        self.logger.info(f"💾 Saved to {self.adapter.get_data_path()}")
        result['saved'] = True
        
        return result
    
    def generate_without_save(
        self,
        identifier: str,
        component_type: str,
        faq_count: int = None,
        humanness_layer: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate content WITHOUT saving.
        
        Used by QualityEvaluatedGenerator for single-pass generation
        with post-save quality evaluation for learning.
        
        Args:
            identifier: Item name (material, setting, etc.) - domain agnostic
            component_type: Type of component (caption, material_description, faq)
            faq_count: Number of FAQ items (ignored for non-FAQ components)
            humanness_layer: Dynamic humanness instructions (from HumannessOptimizer)
            
        Returns:
            Dict with 'content', 'length', 'word_count', 'saved'=False, 'temperature'
            
        Raises:
            ValueError: If identifier not found or generation fails
            FileNotFoundError: If required files missing
        """
        self.logger.info(f"\n🔄 GENERATION: {component_type} for {identifier} ({self.domain} domain)")
        
        # Validate component type exists
        from shared.text.utils.component_specs import ComponentRegistry
        try:
            spec = ComponentRegistry.get_spec(component_type)
        except KeyError:
            raise ValueError(f"Unknown component type: {component_type}")
        
        # Load item data using domain adapter
        item_data = self._get_item_data(identifier)
        
        # Get author ID using adapter (domain-agnostic)
        author_id = self.adapter.get_author_id(item_data)
        voice = self._get_persona_by_author_id(author_id)
        
        # Get facts and context
        facts = self.enricher.fetch_real_facts(identifier)
        context = self._build_context(item_data)
        
        # Get base parameters
        params = self._get_base_parameters(component_type)
        self.logger.info(f"🌡️  Temperature: {params['temperature']:.3f}")
        
        # Build prompt using unified builder for all components
        from shared.text.utils.prompt_builder import PromptBuilder
        
        # Get technical intensity from config and normalize to 0.0-1.0 scale
        config_technical_intensity = self.config.get('voice_parameters', {}).get('technical_intensity', 2)
        normalized_intensity = (config_technical_intensity - 1) / 2.0  # 1→0.0, 2→0.5, 3→1.0
        
        enrichment_params = {
            'technical_intensity': normalized_intensity
        }
        
        prompt = PromptBuilder.build_unified_prompt(
            topic=identifier,
            voice=voice,
            length=None,  # Length is in humanness_layer, not passed separately
            facts=facts,
            context=context,
            component_type=component_type,
            domain=self.domain,
            enrichment_params=enrichment_params,
            humanness_layer=humanness_layer,
            faq_count=faq_count
        )
        self.logger.info(f"📝 Prompt built for {component_type}")
        
        # CRITICAL: Validate FULL ASSEMBLED PROMPT before API call
        print("\n" + "="*80)
        print("🔍 COMPREHENSIVE PROMPT VALIDATION (FULL PROMPT)")
        print("="*80)
        self.logger.info("\n" + "="*80)
        self.logger.info("🔍 COMPREHENSIVE PROMPT VALIDATION (FULL PROMPT)")
        self.logger.info("="*80)
        
        try:
            from shared.validation.prompt_validator import validate_text_prompt
            validation_result = validate_text_prompt(prompt)
            
            # Print FULL validation metrics (TERMINAL + FILE LOGGING)
            print(f"\n📊 PROMPT METRICS:")
            print(f"   • Characters: {validation_result.prompt_length:,}")
            print(f"   • Words: {validation_result.word_count:,}")
            print(f"   • Estimated tokens: {validation_result.estimated_tokens:,}")
            print(f"   • Status: {validation_result.get_summary()}")
            self.logger.info(f"\n📊 PROMPT METRICS:")
            self.logger.info(f"   • Characters: {validation_result.prompt_length:,}")
            self.logger.info(f"   • Words: {validation_result.word_count:,}")
            self.logger.info(f"   • Estimated tokens: {validation_result.estimated_tokens:,}")
            self.logger.info(f"   • Status: {validation_result.get_summary()}")
            
            # Display FULL PROMPT STRUCTURE (TERMINAL + FILE LOGGING)
            print(f"\n📜 FULL PROMPT STRUCTURE:")
            print(f"   • Total lines: {len(prompt.split('\n'))}")
            print(f"   • First 15 lines:")
            for i, line in enumerate(prompt.split('\n')[:15], 1):
                print(f"      {i:2d}. {line[:100]}{'...' if len(line) > 100 else ''}")
            if len(prompt.split('\n')) > 15:
                print(f"   • ... ({len(prompt.split('\n')) - 15} more lines)")
            
            self.logger.info(f"\n📜 FULL PROMPT STRUCTURE:")
            prompt_lines = prompt.split('\n')
            self.logger.info(f"   • Total lines: {len(prompt_lines)}")
            self.logger.info(f"   • First 10 lines:")
            for i, line in enumerate(prompt_lines[:10], 1):
                self.logger.info(f"      {i:2d}. {line[:100]}{'...' if len(line) > 100 else ''}")
            if len(prompt_lines) > 10:
                self.logger.info(f"   • ... ({len(prompt_lines) - 10} more lines)")
            
            # Check for voice instruction rendering (TERMINAL + FILE LOGGING)
            print(f"\n🔍 CRITICAL SECTIONS CHECK:")
            if 'VOICE:' in prompt or 'voice_instruction' in prompt:
                print("   • Voice instructions: ✅ PRESENT")
                self.logger.info("   ✅ Voice instructions present in prompt")
            else:
                print("   • Voice instructions: ❌ MISSING")
                self.logger.warning("   ⚠️  NO voice instructions found in prompt!")
            
            # Check for forbidden phrase instructions
            if 'FORBIDDEN' in prompt.upper() or 'forbidden' in prompt:
                print("   • Forbidden phrases: ✅ PRESENT")
                self.logger.info("   ✅ Contains forbidden phrase instructions")
            else:
                print("   • Forbidden phrases: ❌ MISSING")
                self.logger.warning("   ⚠️  NO forbidden phrase instructions found!")
            
            # Check for component requirements
            if 'REQUIREMENTS:' in prompt.upper():
                print("   • Component requirements: ✅ PRESENT")
            else:
                print("   • Component requirements: ❌ MISSING")
            
            # Display ALL validation issues (TERMINAL + FILE LOGGING)
            if validation_result.issues:
                print(f"\n⚠️  VALIDATION ISSUES ({len(validation_result.issues)} total):")
                for i, issue in enumerate(validation_result.issues, 1):
                    print(f"   {i}. [{issue.severity.value}] {issue.message}")
                    if issue.suggestion:
                        print(f"      💡 {issue.suggestion}")
                
                self.logger.info(f"\n⚠️  VALIDATION ISSUES ({len(validation_result.issues)} total):")
                for i, issue in enumerate(validation_result.issues, 1):
                    self.logger.info(f"   {i}. [{issue.severity.value}] {issue.message}")
                    if issue.suggestion:
                        self.logger.info(f"      💡 {issue.suggestion}")
            else:
                print(f"\n✅ No validation issues found")
                self.logger.info(f"\n✅ No validation issues found")
            
            print("\n" + "="*80)
            self.logger.info("\n" + "="*80)
            
            # Save full prompt to temp file for detailed inspection
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='_prompt.txt', delete=False, dir='/tmp') as f:
                f.write(prompt)
                prompt_file = f.name
            print(f"📄 Full prompt saved to: {prompt_file}")
            print(f"   View with: cat {prompt_file}")
            self.logger.info(f"📄 Full prompt saved to: {prompt_file}\n")
            
            if not validation_result.is_valid:
                if validation_result.has_critical_issues:
                    print(f"\n❌ CRITICAL VALIDATION FAILURE")
                    print(validation_result.format_report())
                    raise ValueError(
                        f"Prompt validation failed with critical issues:\n"
                        f"{validation_result.format_report()}"
                    )
                else:
                    print(f"   ⚠️  Validation warnings present (not blocking)")
                    self.logger.info("   ⚠️  Validation warnings present (not blocking)")
            else:
                print(f"   ✅ Prompt validated successfully")
                self.logger.info("   ✅ Prompt validated successfully")
        except ImportError as e:
            print(f"\n⚠️  Prompt validator not available - skipping validation")
            print(f"   Error: {e}")
            self.logger.warning(f"⚠️  UniversalPromptValidator not available - skipping validation: {e}")
        
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
        
        # Add sparse cross-links (NEW - Dec 11, 2025)
        # Only for string content (not micro dict or FAQ list)
        if isinstance(content, str) and len(content) > 100:
            try:
                self.logger.info("🔗 Adding cross-links...")
                content = self.link_builder.add_links(
                    content=content,
                    current_item=identifier,
                    domain=self.domain
                )
                self.logger.info("✅ Cross-linking complete")
            except Exception as e:
                self.logger.warning(f"⚠️  Cross-linking failed: {e} (continuing without links)")
        
        # Calculate word count (handle both string and dict content)
        if isinstance(content, dict):
            # Micro has before/after structure
            word_count = sum(len(str(v).split()) for v in content.values() if v)
            char_count = sum(len(str(v)) for v in content.values() if v)
        elif isinstance(content, list):
            # FAQ has list of Q&A dicts
            word_count = sum(len(qa.get('answer', '').split()) for qa in content)
            char_count = sum(len(qa.get('answer', '')) for qa in content)
        else:
            # String content (material_description, etc.)
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
        """Save generated content to appropriate YAML file with atomic write + immediate frontmatter sync."""
        
        # settings_description goes to Settings.yaml, everything else to Materials.yaml
        if component_type == 'settings_description':
            self._save_to_settings_yaml(material_name, content)
        else:
            self._save_to_materials_yaml(material_name, component_type, content)
    
    def _save_to_settings_yaml(self, material_name: str, content: Any):
        """Save settings_description to Settings.yaml with atomic write + frontmatter sync."""
        import sys
        print(f"🔧 [DEBUG] _save_to_settings_yaml called for {material_name}")
        sys.stdout.flush()
        
        from domains.settings.data_loader import get_settings_path
        settings_path = get_settings_path()
        
        # Load existing data
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            raise FileNotFoundError(f"Failed to load Settings.yaml: {e}")
        
        if material_name not in data.get('settings', {}):
            raise ValueError(f"Material '{material_name}' not found in Settings.yaml")
        
        # Save settings_description to Settings.yaml
        data['settings'][material_name]['settings_description'] = content
        
        # Update metadata
        data['_metadata']['last_updated'] = '2025-11-24T21:00:00Z'
        
        # Atomic write: write to temp file, then rename
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(
                mode='w',
                encoding='utf-8',
                dir=settings_path.parent,
                delete=False,
                suffix='.yaml'
            ) as temp_f:
                yaml.safe_dump(data, temp_f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                temp_path = temp_f.name
            
            # Atomic rename (POSIX guarantees atomicity)
            Path(temp_path).replace(settings_path)
            
            print(f"✅ settings_description written to data/settings/Settings.yaml → settings.{material_name}.settings_description")
            import sys
            sys.stdout.flush()
            
            # DUAL-WRITE POLICY: Immediately sync field to frontmatter
            print(f"🔄 Syncing to frontmatter...")
            sys.stdout.flush()
            try:
                from generation.utils.frontmatter_sync import sync_field_to_frontmatter
                sync_field_to_frontmatter(material_name, 'settings_description', content, domain='settings')
                print(f"✅ Frontmatter sync complete for {material_name}")
                sys.stdout.flush()
            except Exception as sync_error:
                print(f"❌ Frontmatter sync FAILED: {sync_error}")
                sys.stdout.flush()
                import traceback
                traceback.print_exc()
                # Don't fail the whole generation - sync can be done manually
                print(f"⚠️  Continuing despite sync failure...")
            
        except Exception as e:
            # Clean up temp file on failure
            if 'temp_path' in locals():
                Path(temp_path).unlink(missing_ok=True)
            raise ValueError(f"Failed to save to Settings.yaml: {e}")
    
    def _save_to_materials_yaml(self, material_name: str, component_type: str, content: Any):
        """Save generated content to Materials.yaml with atomic write + immediate frontmatter sync."""
        materials_path = Path("data/materials/Materials.yaml")
        
        # Load existing data
        try:
            with open(materials_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            raise FileNotFoundError(f"Failed to load Materials.yaml: {e}")
        
        if material_name not in data['materials']:
            raise ValueError(f"Material '{material_name}' not found in Materials.yaml")
        
        # material_description/settings_description/faq go at ROOT level (not in components)
        # Micro goes in components (before/after structure)
        if component_type in ['material_description', 'settings_description', 'faq']:
            # Save to root level for consistency with existing structure
            data['materials'][material_name][component_type] = content
        else:
            # Micro and other components go in components section
            if 'components' not in data['materials'][material_name]:
                data['materials'][material_name]['components'] = {}
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
            
            print(f"💾 Saved to data/materials/Materials.yaml")
            
            # DUAL-WRITE POLICY (Nov 22, 2025): Immediately sync field to frontmatter
            # Only updated field written to frontmatter, others preserved
            print(f"🔄 Syncing {component_type} to frontmatter...")
            from generation.utils.frontmatter_sync import sync_field_to_frontmatter
            sync_field_to_frontmatter(material_name, component_type, content, domain='materials')
            
        except Exception as e:
            # Clean up temp file on failure
            if 'temp_path' in locals():
                Path(temp_path).unlink(missing_ok=True)
            raise ValueError(f"Failed to save to Materials.yaml: {e}")
