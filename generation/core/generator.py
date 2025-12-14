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
            component_type: Type of component (micro, material_description, faq)
            faq_count: Number of FAQ items (ignored for non-FAQ components)
            
        Returns:
            Dict with 'content', 'length', 'word_count', 'saved', 'temperature'
            
        Raises:
            ValueError: If identifier not found or generation fails
            FileNotFoundError: If required files missing
        """
        # Generate humanness layer (structural variation only - voice comes from persona)
        from learning.humanness_optimizer import HumannessOptimizer
        humanness_optimizer = HumannessOptimizer()
        humanness_layer = humanness_optimizer.generate_humanness_instructions(
            component_type=component_type
        )
        self.logger.info(f"🧠 Generated humanness layer ({len(humanness_layer)} chars)")
        
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
        humanness_layer: Optional[str] = None,
        **kwargs  # Accept existing_content and other postprocess params
    ) -> Dict[str, Any]:
        """
        Generate content WITHOUT saving.
        
        Used by QualityEvaluatedGenerator for single-pass generation
        with post-save quality evaluation for learning.
        
        Args:
            identifier: Item name (material, setting, etc.) - domain agnostic
            component_type: Type of component (micro, material_description, faq)
            faq_count: Number of FAQ items (ignored for non-FAQ components)
            humanness_layer: Dynamic humanness instructions (from HumannessOptimizer)
            **kwargs: Additional context (e.g., existing_content for postprocessing)
            
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
        
        # Merge any additional context from kwargs (e.g., existing_content for postprocessing)
        # CRITICAL: Don't overwrite item_data keys, only add missing ones
        for key, value in kwargs.items():
            if key not in item_data and value is not None:
                item_data[key] = value
        
        # Generate humanness layer if not provided
        if humanness_layer is None:
            from learning.humanness_optimizer import HumannessOptimizer
            humanness_optimizer = HumannessOptimizer()
            humanness_layer = humanness_optimizer.generate_humanness_instructions(
                component_type=component_type
            )
            print(f"🧠 Generating humanness instructions...")
            self.logger.info(f"🧠 Generated humanness layer ({len(humanness_layer)} chars)")
        
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
        
        # 🎯 SIZE-AWARE HUMANNESS LAYER: Check base prompt size BEFORE adding humanness
        # Build base prompt WITHOUT humanness first
        base_prompt = PromptBuilder.build_unified_prompt(
            topic=identifier,
            voice=voice,
            length=None,
            facts=facts,
            context=context,
            component_type=component_type,
            domain=self.domain,
            enrichment_params=enrichment_params,
            humanness_layer="",  # Empty first to measure base size
            faq_count=faq_count,
            item_data=item_data  # Pass item_data for template placeholders
        )
        
        base_size = len(base_prompt)
        
        # 🎯 SIZE-AWARE DECISION: Compress humanness if base already large
        # API limit: 8,000 chars. Full humanness ~9K would push any base > 0 over limit
        # Compressed humanness ~1K allows base up to ~6.5K
        SIZE_THRESHOLD = 2000  # If base exceeds this, use compressed humanness
        
        if base_size > SIZE_THRESHOLD:
            # Base prompt moderate - use COMPRESSED humanness (essential rules only ~1K)
            print(f"📦 Base prompt {base_size:,} chars > {SIZE_THRESHOLD:,} - using COMPRESSED humanness")
            self.logger.info(f"📦 Base prompt {base_size:,} chars > {SIZE_THRESHOLD:,} - using COMPRESSED humanness")
            # Generate compressed version (10-15% of normal size, learning-optimized)
            from learning.humanness_optimizer import HumannessOptimizer
            optimizer = HumannessOptimizer(winston_db_path='z-beam.db')
            final_humanness = optimizer.generate_compressed_humanness(
                component_type=component_type
            )
        else:
            # Base prompt small - use FULL humanness layer
            print(f"✅ Base prompt {base_size:,} chars < {SIZE_THRESHOLD:,} - using FULL humanness")
            self.logger.info(f"✅ Base prompt {base_size:,} chars < {SIZE_THRESHOLD:,} - using FULL humanness")
            final_humanness = humanness_layer
        
        # Rebuild prompt with appropriate humanness
        prompt = PromptBuilder.build_unified_prompt(
            topic=identifier,
            voice=voice,
            length=None,
            facts=facts,
            context=context,
            component_type=component_type,
            domain=self.domain,
            enrichment_params=enrichment_params,
            humanness_layer=final_humanness,
            faq_count=faq_count,
            item_data=item_data  # Pass item_data for template placeholders
        )
        
        print(f"📊 Final prompt: {len(prompt):,} chars (base: {base_size:,}, humanness: {len(final_humanness):,})")
        self.logger.info(f"📊 Final prompt: {len(prompt):,} chars (base: {base_size:,}, humanness: {len(final_humanness):,})")
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
            from shared.validation.prompt_coherence_validator import validate_prompt_coherence
            
            # Stage 1: Standard validation (length, format, technical)
            validation_result = validate_text_prompt(prompt)
            
            # Stage 2: Coherence validation (separation of concerns, contradictions)
            coherence_result = validate_prompt_coherence(prompt)
            
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
            if 'VOICE INSTRUCTIONS' in prompt or 'VOICE:' in prompt or 'voice_instruction' in prompt:
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
            
            # Report standard validation (AUTO-FIX CRITICAL/WARNING issues)
            if not validation_result.is_valid or validation_result.has_warnings:
                if validation_result.has_critical_issues or validation_result.has_warnings:
                    # CRITICAL/WARNING ISSUES: AUTO-FIX
                    severity_label = "CRITICAL" if validation_result.has_critical_issues else "WARNING"
                    print(f"\n⚠️  {severity_label} VALIDATION ISSUES - AUTO-FIXING")
                    print(validation_result.format_report())
                    self.logger.warning(f"{severity_label} validation issues detected - attempting auto-fix")
                    
                    # Auto-optimize prompt
                    from shared.validation.prompt_optimizer import optimize_prompt
                    optimized_prompt = optimize_prompt(prompt, validation_result)
                    
                    if optimized_prompt != prompt:
                        print(f"\n✅ PROMPT AUTO-OPTIMIZED:")
                        print(f"   Original: {len(prompt):,} chars")
                        print(f"   Optimized: {len(optimized_prompt):,} chars")
                        print(f"   Reduction: {len(prompt) - len(optimized_prompt):,} chars ({100*(len(prompt)-len(optimized_prompt))/len(prompt):.1f}%)")
                        self.logger.info(f"Prompt optimized: {len(prompt)} → {len(optimized_prompt)} chars")
                        prompt = optimized_prompt
                        
                        # Re-validate optimized prompt
                        validation_result = validate_text_prompt(prompt)
                        if validation_result.has_critical_issues or validation_result.has_warnings:
                            print(f"   ⚠️  Still has issues after optimization")
                            self.logger.warning(f"Optimization insufficient - proceeding anyway")
                        else:
                            print(f"   ✅ Issues resolved")
                            self.logger.info(f"Issues resolved by optimization")
                    
                    self._log_validation_issues(
                        validation_result, 
                        'standard',
                        material=identifier,
                        component_type=component_type,
                        domain=self.domain
                    )
                else:
                    # INFO ONLY: Log but don't block (learning feedback)
                    print(f"\n💡 VALIDATION INFO (logged for learning)")
                    print(validation_result.format_report())
                    self.logger.info(f"Validation info detected: {validation_result.format_report()}")
                    # Log to learning database for humanness optimizer to adapt
                    self._log_validation_issues(
                        validation_result, 
                        'standard',
                        material=identifier,
                        component_type=component_type,
                        domain=self.domain
                    )
            else:
                print(f"   ✅ Standard validation passed")
                self.logger.info("   ✅ Standard validation passed")
            
            # Report coherence validation (AUTO-FIX CRITICAL issues)
            print(f"\n🔗 COHERENCE VALIDATION:")
            print(f"   {coherence_result.get_summary()}")
            self.logger.info(f"🔗 COHERENCE VALIDATION: {coherence_result.get_summary()}")
            
            if not coherence_result.is_coherent:
                critical_coherence = [i for i in coherence_result.issues if i.severity == "CRITICAL"]
                
                if critical_coherence:
                    # CRITICAL COHERENCE ISSUES: LOG AND PROCEED
                    print(f"\n⚠️  CRITICAL COHERENCE ISSUES (logged for learning):")
                    for issue in critical_coherence:
                        print(f"   • [{issue.severity}] {issue.message}")
                        self.logger.warning(f"   [{issue.severity}] {issue.message}")
                    
                    self.logger.warning(f"{len(critical_coherence)} critical coherence issues - logged for learning")
                    self._log_validation_issues(
                        coherence_result, 
                        'coherence',
                        material=identifier,
                        component_type=component_type,
                        domain=self.domain
                    )
                else:
                    # ERROR/WARNING: Log but don't block
                    print(f"\n⚠️  COHERENCE ISSUES DETECTED (logged for learning):")
                    for issue in coherence_result.issues:
                        if issue.severity in ["ERROR", "WARNING"]:
                            print(f"   • [{issue.severity}] {issue.message}")
                            self.logger.warning(f"   [{issue.severity}] {issue.message}")
                    
                    # Log full report to file and learning database
                    self.logger.info("\n" + coherence_result.format_report())
                    self._log_validation_issues(
                        coherence_result, 
                        'coherence',
                        material=identifier,
                        component_type=component_type,
                        domain=self.domain
                    )
            else:
                print(f"   ✅ Coherence validated successfully")
                self.logger.info("   ✅ Coherence validated successfully")
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
                max_tokens=4096,  # Large limit to allow natural completion (Grok max context)
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
        
        # Add sparse cross-links (UPDATED - Dec 14, 2025)
        # Documentation: docs/03-components/text/CROSSLINKING.md
        # Apply to all text fields: strings, dicts (micro), and lists (FAQ)
        # Automatically links materials/contaminants mentioned in generated text
        try:
            self.logger.info("🔗 Adding cross-links...")
            
            if isinstance(content, str) and len(content) > 50:
                # String content (material_description, description, etc.)
                content = self.link_builder.add_links(
                    content=content,
                    current_item=identifier,
                    domain=self.domain
                )
            elif isinstance(content, dict):
                # Dict content (micro with before/after)
                for key, value in content.items():
                    if isinstance(value, str) and len(value) > 50:
                        content[key] = self.link_builder.add_links(
                            content=value,
                            current_item=identifier,
                            domain=self.domain
                        )
            elif isinstance(content, list):
                # List content (FAQ with Q&A pairs)
                for item in content:
                    if isinstance(item, dict) and 'answer' in item:
                        if isinstance(item['answer'], str) and len(item['answer']) > 50:
                            item['answer'] = self.link_builder.add_links(
                                content=item['answer'],
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
    
    def _save_to_yaml(self, identifier: str, component_type: str, content: Any):
        """
        Save generated content to domain data YAML file using domain adapter.
        
        Domain-aware: Uses adapter.write_component() which automatically:
        - Writes to correct YAML file (Materials.yaml, Contaminants.yaml, Settings.yaml, etc.)
        - Uses correct root key (materials, contamination_patterns, settings, etc.)
        - Performs atomic write with temp file
        - Syncs to frontmatter immediately (dual-write policy)
        """
        self.adapter.write_component(identifier, component_type, content)
    
    def _save_to_settings_yaml(self, material_name: str, content: Any):
        """
        DEPRECATED: Hardcoded for Settings.yaml only.
        Use adapter.write_component() instead (domain-aware).
        
        This method is kept for backward compatibility but should not be used.
        """
        import sys
        print(f"⚠️  [DEPRECATED] _save_to_settings_yaml called for {material_name}")
        print(f"💡 Use adapter.write_component() instead (domain-aware)")
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
        """
        DEPRECATED: Hardcoded for Materials.yaml only.
        Use adapter.write_component() instead (domain-aware).
        
        This method is kept for backward compatibility but should not be used.
        """
        import sys
        print(f"⚠️  [DEPRECATED] _save_to_materials_yaml called for {material_name}")
        print(f"💡 Use adapter.write_component() instead (domain-aware)")
        sys.stdout.flush()
        
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
            # Author field is NEVER updated (immutability policy)
            print(f"🔄 Syncing {component_type} to frontmatter...")
            from generation.utils.frontmatter_sync import sync_field_to_frontmatter
            sync_field_to_frontmatter(material_name, component_type, content, domain='materials')
            
        except Exception as e:
            # Clean up temp file on failure
            if 'temp_path' in locals():
                Path(temp_path).unlink(missing_ok=True)
            raise ValueError(f"Failed to save to Materials.yaml: {e}")
    
    def _log_validation_issues(
        self, 
        validation_result, 
        validation_type: str,
        material: Optional[str] = None,
        component_type: Optional[str] = None,
        domain: str = 'materials'
    ):
        """
        Log validation issues to learning database for humanness optimizer feedback.
        
        This enables dynamic adaptation: validation issues feed into the humanness
        layer, which adjusts future prompts to address recurring problems.
        
        Args:
            validation_result: ValidationResult or CoherenceResult object
            validation_type: Type of validation ('standard' or 'coherence')
            material: Material/item name for correlation with Winston results
            component_type: Content type for correlation analysis
            domain: Content domain (materials, contaminants, settings)
        
        Design: Non-blocking - logs for learning, never raises exceptions
        """
        try:
            # Lazy import to avoid circular dependencies
            from postprocessing.detection.winston_feedback_db import WinstonFeedbackDatabase
            
            db = WinstonFeedbackDatabase('z-beam.db')
            
            # Extract issues from validation result
            issues = []
            if hasattr(validation_result, 'issues'):
                for issue in validation_result.issues:
                    # Convert enum to string value for JSON serialization
                    severity = getattr(issue, 'severity', 'UNKNOWN')
                    if hasattr(severity, 'value'):
                        severity = severity.value
                    issues.append({
                        'severity': severity,
                        'message': getattr(issue, 'message', str(issue)),
                        'suggestion': getattr(issue, 'suggestion', None)
                    })
            
            # Log to prompt_validation_feedback table (auto-creates if not exists)
            db.log_prompt_validation(
                validation_type=validation_type,
                is_valid=getattr(validation_result, 'is_valid', True) or 
                        getattr(validation_result, 'is_coherent', True),
                issues=issues,
                prompt_length=getattr(validation_result, 'prompt_length', None) or 0,
                word_count=getattr(validation_result, 'word_count', None) or 0,
                estimated_tokens=getattr(validation_result, 'estimated_tokens', None) or 0,
                material=material,
                component_type=component_type,
                domain=domain
            )
            
            self.logger.info(f"   📊 Validation feedback logged ({len(issues)} issues) for humanness optimizer")
            
        except Exception as e:
            # Non-blocking: log error but continue generation
            self.logger.warning(f"   ⚠️  Could not log validation feedback: {e}")

