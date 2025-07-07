#!/usr/bin/env python3
"""
Optimization Orchestrator - Manages multi-step optimization pipeline with bundled context

KEY FEATURES:
- Reads optimization steps from optimizations.json and executes in order
- Bundles previous content + new optimization in single API request
- Tracks optimization history for context preservation
- Fail-fast approach: any step failure aborts entire generation
- Complete content replacement at each step (not incremental editing)

ARCHITECTURE:
1. Load optimization steps (order 1+, excluding generation_enhancement)
2. For each step:
   - Bundle: previous content + optimization prompt + context
   - Send single API request with full context
   - Validate response (fail-fast on empty/invalid)
   - Replace current content completely with optimized version
   - Track step in optimization history
3. Return final optimized content

BUNDLED PROMPT STRUCTURE:
- OPTIMIZATION TASK: Current step name
- SECTION CONTEXT: Section info, material, target words, previous steps
- CURRENT CONTENT TO OPTIMIZE: Content from previous step
- OPTIMIZATION REQUIREMENTS: Step-specific prompt with substitutions
- INSTRUCTIONS: Clear directive for content replacement

FAIL-FAST BEHAVIOR:
- Empty API response = abort generation
- Missing provider config = abort generation
- No API keys = abort generation
- Any exception = bubble up to caller
"""

import json
import logging
from pathlib import Path
from modules import api_client

logger = logging.getLogger(__name__)

class OptimizationOrchestrator:
    """
    Manages ordered optimization pipeline with bundled context preservation
    
    CONTENT FLOW:
    Generated Content → Step 1 (bundled) → Replacement Content → Step 2 (bundled) → Final Content
    
    Each step receives:
    - Previous optimized content
    - New optimization requirements  
    - Full context (section, material, history)
    - Target constraints (word count, etc.)
    
    Each step produces:
    - Complete replacement content
    - Preserves previous optimization gains
    - Builds incrementally toward final quality
    """
    
    def __init__(self, config):
        """
        Initialize orchestrator with configuration
        
        Args:
            config: GlobalConfigManager instance with:
                - optimization_provider: str (DEEPSEEK, GEMINI, etc.)
                - default_section_words: int (target word count)
                - provider_models: dict (provider configurations)
                - api_key_mappings: dict (environment variable mappings)
        """
        self.config = config
        
        # SET PROMPTS DIRECTORY FIRST
        self.prompts_directory = Path("prompts")
        
        # NOW AUTO-DETECT optimization enabled based on available steps
        try:
            optimization_steps = self._load_optimization_pipeline()
            self.optimization_enabled = len(optimization_steps) > 0
            logger.info(f"🔧 Optimization auto-detected: {'enabled' if self.optimization_enabled else 'disabled'}")
        except (FileNotFoundError, KeyError, Exception) as e:
            self.optimization_enabled = False
            logger.info(f"🔧 No optimization steps found - optimization disabled ({e})")
        
    def optimize_section(self, content, section_name, section_type, material):
        """
        Run complete optimization pipeline for a section with bundled context
        FAIL-FAST: Any step failure causes complete generation failure
        
        Args:
            content (str): Generated content with E-A-T requirements already applied
            section_name (str): Section identifier (e.g., "introduction")
            section_type (str): Section type for context (e.g., "Introduction Section")
            material (str): Material being discussed (e.g., "Hafnium")
            
        Returns:
            str: Fully optimized content with all pipeline steps applied
            
        Raises:
            RuntimeError: If any optimization step fails or returns empty content
            FileNotFoundError: If optimizations.json not found
            
        PROCESS:
        1. Load optimization steps from JSON (order 1+)
        2. For each step:
           a. Create bundled prompt (content + optimization + context)
           b. Send API request with full bundle
           c. Validate response (fail if empty)
           d. Replace current content completely
           e. Add step to history
        3. Return final optimized content
        
        LOGGING OUTPUT:
        🎯 Starting optimization pipeline for section: {section_name}
        📋 Loaded {n} optimization steps
           Step {order}: {step_name}
        🔧 Applying step {order}: {step_name}
        📋 Created bundled prompt: {chars} characters
           ⏱️ {step_name} completed in {time}s
        ✅ {step_name}: {before}→{after} ({change})
        🎯 Optimization pipeline complete: {original}→{final} ({total_change})
        """
        
        if not self.optimization_enabled:
            logger.info("🔧 Optimization disabled - returning original content")
            return content
        
        logger.info(f"🎯 Starting optimization pipeline for section: {section_name}")
        
        # Load and sort optimization steps
        optimization_steps = self._load_optimization_pipeline()
        
        current_content = content
        original_words = len(content.split())
        optimization_history = []  # Track applied optimizations for context
        
        # Execute each step in order with context bundling
        for step in optimization_steps:
            step_name = step['key']
            step_config = step['config']
            
            # ENHANCED STEP LOGGING WITH NAME AND DESCRIPTION
            logger.info(f"🔧 Applying step {step_config['order']}: {step_config['name']}")
            logger.info(f"📝 Step details: {step_config.get('description', 'No description available')}")
            
            # CREATE BUNDLED PROMPT (previous content + new optimization + context)
            bundled_prompt = self._create_bundled_optimization_prompt(
                previous_content=current_content,
                optimization_config=step_config,
                section_context={
                    "name": section_name,
                    "type": section_type,
                    "material": material,
                    "previous_steps": optimization_history.copy(),
                    "target_words": self.config.get('default_section_words', 150)
                }
            )
            
            # Apply optimization step with bundled context
            optimized_content = self._apply_optimization_step_bundled(
                bundled_prompt, step_name, step_config, section_name
            )
            
            # STRICT VALIDATION - FAIL IF EMPTY OR INVALID
            if not optimized_content or not optimized_content.strip():
                logger.error(f"❌ GENERATION FAILED: {step_config['name']} returned empty content")
                logger.error(f"💀 Section '{section_name}' optimization failed - aborting entire generation")
                raise RuntimeError(f"Optimization step '{step_config['name']}' failed for section '{section_name}'")
            
            # Log step results with word count tracking
            before_words = len(current_content.split())
            after_words = len(optimized_content.split())
            word_change = after_words - before_words
            change_sign = "+" if word_change > 0 else ""
            
            # ENHANCED RESULT LOGGING WITH STEP NAME
            logger.info(f"✅ {step_config['name']}: {before_words}→{after_words} ({change_sign}{word_change})")
            
            # COMPLETE REPLACEMENT - Update content and history for next iteration
            current_content = optimized_content
            optimization_history.append(step_name)

        # Final pipeline results
        final_words = len(current_content.split())
        total_change = final_words - original_words
        change_sign = "+" if total_change > 0 else ""
        
        logger.info(f"🎯 Optimization pipeline complete: {original_words}→{final_words} ({change_sign}{total_change})")
        return current_content

    def _load_optimization_pipeline(self):
        """Load optimization steps from JSON and sort by order - COMPLETELY DYNAMIC FOR MULTIPLE STEPS"""
    
        prompt_file = self.prompts_directory / "optimizations.json"
    
        if not prompt_file.exists():
            logger.error(f"❌ Optimization file not found: {prompt_file}")
            raise FileNotFoundError(f"Optimization file not found: {prompt_file}")
    
        with open(prompt_file, 'r', encoding='utf-8') as f:
            optimizations_data = json.load(f)
    
        # Filter and sort optimization steps - SUPPORTS ANY NUMBER OF STEPS
        optimization_steps = []
    
        for key, config in optimizations_data.items():
            # DYNAMIC FILTERING: Include steps that have 'prompt' and order > 0
            if (config.get('prompt') and 
                config.get('order', 999) > 0 and  # Only optimization steps (not generation)
                config.get('type') != 'generation_enhancement'):  # Skip generation enhancement
                
                optimization_steps.append({
                    'key': key,
                    'config': config
                })
    
        # Sort by order field - SUPPORTS UNLIMITED STEPS
        optimization_steps.sort(key=lambda x: x['config'].get('order', 999))
    
        # ENHANCED LOGGING WITH STEP NAMES AND DETAILS
        logger.info(f"📋 Loaded {len(optimization_steps)} optimization steps")
        for step in optimization_steps:
            step_config = step['config']
            logger.info(f"   Step {step_config['order']}: {step_config['name']}")
            logger.info(f"      Type: {step_config.get('type', 'unknown')} | Version: {step_config.get('version', 'unversioned')}")
    
        return optimization_steps
    
    def _create_bundled_optimization_prompt(self, previous_content, optimization_config, section_context):
        """Create bundled prompt with previous content + new optimization requirements"""
        
        # Build comprehensive context information
        context_info = f"""OPTIMIZATION TASK: {optimization_config['name']}

SECTION CONTEXT:
- Section: {section_context['name']} ({section_context['type']})
- Material: {section_context['material']}
- Target words: ~{section_context['target_words']}
- Previous optimizations: {', '.join(section_context['previous_steps']) if section_context['previous_steps'] else 'None'}

CURRENT CONTENT TO OPTIMIZE:
{previous_content}

OPTIMIZATION REQUIREMENTS:
{optimization_config['prompt'].format(
    content=previous_content,
    section_type=section_context['type'],
    material=section_context['material']
)}

CRITICAL OUTPUT REQUIREMENTS:
- Return ONLY the optimized content itself
- Do NOT include any meta-commentary, explanations, or introductory phrases
- Do NOT add "Here's the optimized version" or similar commentary
- Do NOT include separators, dashes, or explanatory text
- Start immediately with the actual content
- End immediately after the content

Your response must begin directly with the content and contain nothing else."""
        
        logger.info(f"📋 Created bundled prompt: {len(context_info)} characters")
        return context_info
    
    def _apply_optimization_step_bundled(self, bundled_prompt, step_name, step_config, section_name):
        """
        Apply optimization using bundled prompt with full context
        
        FAIL-FAST BEHAVIOR:
        - Missing provider config → RuntimeError
        - No API keys → RuntimeError  
        - Empty API response → RuntimeError
        - Any API exception → Bubbles up
        
        Args:
            bundled_prompt (str): Complete prompt with content + optimization + context
            step_name (str): Step identifier for logging
            step_config (dict): Step configuration from JSON
            section_name (str): Section name for error reporting
            
        Returns:
            str: Optimized content (complete replacement)
            
        Raises:
            RuntimeError: If provider missing, keys missing, or empty response
        """
        
        optimization_provider = self.config.get('optimization_provider')
        
        # Get provider configuration
        provider_models = self.config.get('provider_models', {})
        provider_config = provider_models.get(optimization_provider, {})
        
        if not provider_config:
            logger.error(f"❌ GENERATION FAILED: No configuration found for provider: {optimization_provider}")
            raise RuntimeError(f"Provider configuration missing: {optimization_provider}")
        
        # Format API keys
        api_key_mappings = self.config.get("api_key_mappings", {})
        api_keys = {}
        for prov, env_var in api_key_mappings.items():
            import os
            key = os.getenv(env_var)
            if key:
                api_keys[env_var] = key
        
        if not api_keys:
            logger.error(f"❌ GENERATION FAILED: No API keys available for optimization")
            raise RuntimeError("No API keys configured for optimization")
        
        # Make API call with bundled prompt
        import time
        start_time = time.time()
        
        result = api_client.call_ai_api(
            prompt=bundled_prompt,  # Full bundled context
            provider=optimization_provider,
            model=provider_config.get('model'),
            api_keys=api_keys,
            temperature=0.3,  # Lower temperature for consistency
            max_tokens=self.config.get('max_tokens', 4096),
            url_template=provider_config.get('url_template'),
            backoff_factor=2.0
        )
        
        response_time = time.time() - start_time
        
        # STRICT VALIDATION - FAIL FAST ON EMPTY RESPONSE
        if not result or not result.strip():
            logger.error(f"❌ GENERATION FAILED: {step_config['name']} returned empty response")
            logger.error(f"💀 API call succeeded but content is empty - aborting generation")
            raise RuntimeError(f"Empty response from optimization step: {step_config['name']}")
        
        logger.info(f"   ⏱️ {step_config['name']} completed in {response_time:.1f}s")
        return result.strip()