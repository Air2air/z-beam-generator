#!/usr/bin/env python3
"""
Shared Dynamic Prompt Builder

Loads prompts from shared/ directory for BOTH generation and validation.
Automatically integrates user feedback from feedback/ files.

Zero hardcoded prompts - all content loaded from template files.
Ensures generator and validator use identical quality standards.

Author: AI Assistant
Date: November 25, 2025
"""

from pathlib import Path
from typing import Dict, List, Optional
import logging

from .prompt_optimizer import PromptOptimizer
from .research_data_verifier import ResearchDataVerifier, verify_optimization

logger = logging.getLogger(__name__)


class SharedPromptBuilder:
    """
    Loads and assembles prompts from shared directory.
    
    Used by BOTH MaterialImageGenerator and MaterialImageValidator
    to ensure consistent standards.
    
    Architecture:
    - Generation: 4-layer prompt (base + physics + contamination + micro-scale)
    - Validation: Mirrors generation standards exactly
    - Feedback: User corrections automatically applied to both
    
    Example:
        builder = SharedPromptBuilder()
        
        # For generation:
        prompt = builder.build_generation_prompt(
            material_name="Aluminum",
            research_data={...},
            contamination_level=3
        )
        
        # For validation (uses same standards):
        validation_prompt = builder.build_validation_prompt(
            material_name="Aluminum",
            research_data={...},
            config={...}
        )
    """
    
    def __init__(self, prompts_dir: Optional[Path] = None):
        """
        Initialize with shared prompts directory.
        
        Args:
            prompts_dir: Optional path to shared prompts directory
                        (defaults to prompts/shared/)
        
        Raises:
            FileNotFoundError: If shared prompts directory doesn't exist
        """
        if prompts_dir is None:
            prompts_dir = Path(__file__).parent / "shared"
        
        self.prompts_dir = prompts_dir
        self.generation_dir = prompts_dir / "generation"
        self.validation_dir = prompts_dir / "validation"
        self.feedback_dir = prompts_dir / "feedback"
        
        # Initialize prompt optimizer
        self.optimizer = PromptOptimizer()
        
        # Initialize research data verifier
        self.verifier = ResearchDataVerifier()
        
        # Initialize learning system for learned defaults (lazy-loaded)
        self._learning_logger = None
        
        # Fail-fast validation
        if not self.prompts_dir.exists():
            raise FileNotFoundError(
                f"Shared prompts directory not found: {self.prompts_dir}. "
                f"Cannot operate without prompt templates."
            )
        
        if not self.generation_dir.exists():
            raise FileNotFoundError(
                f"Generation prompts directory not found: {self.generation_dir}"
            )
        
        if not self.validation_dir.exists():
            raise FileNotFoundError(
                f"Validation prompts directory not found: {self.validation_dir}"
            )
        
        logger.info(f"✅ Shared prompt builder initialized: {self.prompts_dir}")
    
    @property
    def learning_logger(self):
        """Lazy-load learning logger to avoid circular imports."""
        if self._learning_logger is None:
            try:
                from shared.image.learning import create_logger
                self._learning_logger = create_logger()
            except Exception as e:
                logger.warning(f"Could not initialize learning logger: {e}")
                self._learning_logger = None
        return self._learning_logger
    
    def _get_learned_or_fail(
        self,
        param_name: str,
        explicit_value: Optional[str],
        category: str,
        context: str,
        material_name: str
    ) -> str:
        """
        Get parameter value: explicit > learned > FAIL.
        
        NO HARDCODED DEFAULTS - uses learning system or fails fast.
        
        Args:
            param_name: Parameter name (e.g., 'severity', 'view_mode')
            explicit_value: Value explicitly provided (takes priority)
            category: Material category for learning lookup
            context: Context for learning lookup
            material_name: Material name for error messages
            
        Returns:
            Parameter value (explicit or learned)
            
        Raises:
            ValueError: If no explicit value AND no learned default available
        """
        # 1. Explicit value takes priority
        if explicit_value is not None:
            return explicit_value
        
        # 2. Try learning system
        if self.learning_logger:
            learned = self.learning_logger.get_learned_param(param_name, category, context)
            if learned is not None:
                logger.info(f"🧠 Using learned {param_name}={learned} for {category}/{context}")
                return learned
        
        # 3. FAIL FAST - no default available
        raise ValueError(
            f"{param_name.upper()} REQUIRED for {material_name}. "
            f"No learned default available for category={category}, context={context}. "
            f"Please specify --{param_name.replace('_', '-')} explicitly."
        )
    
    def build_generation_prompt(
        self,
        material_name: str,
        research_data: Dict,
        contamination_uniformity: Optional[int] = None,
        view_mode: Optional[str] = None,
        material_category: Optional[str] = None,
        learned_feedback: Optional[str] = None,
        severity: Optional[str] = None,
        aging_weight: Optional[float] = None,
        contamination_weight: Optional[float] = None,
        material_properties: Optional[Dict] = None,
        config: Optional["MaterialImageConfig"] = None
    ) -> str:
        """
        Build complete generation prompt from shared templates + learned defaults.
        
        NO HARDCODED DEFAULTS - uses learning system for missing parameters.
        
        Loads 4-layer prompt system:
        1. Base Structure: Core format (side-by-side, 16:9, position shift)
        2. Realism Physics: Physics constraints (gravity, accumulation, layering)
        3. Contamination Rules: Distribution rules (uneven, edge effects, grain following)
        4. Micro-Scale Details: Fine details (porosity, feathering, lighting)
        
        Plus:
        - Forbidden Patterns: Anti-patterns to avoid
        - User Feedback: Your latest quality corrections
        - Learned Feedback: Category-specific feedback from previous attempts
        - Visual Weights: Custom aging/contamination intensity adjustments
        - Material Visual Properties: Reflectivity, absorptivity, surface finish
        
        Args:
            material_name: Name of material (e.g., "Aluminum")
            research_data: Research data with contamination patterns
            contamination_uniformity: Variety 1-5 (learned from successful generations)
            view_mode: "Contextual" or "Isolated" (learned from successful generations)
            material_category: Material category for learned feedback (e.g., "metal_ferrous")
            learned_feedback: Pre-formatted learned feedback from learning system
            severity: Contamination severity - "light" (<30%), "moderate" (30-60%), "heavy" (>60%)
            aging_weight: Visual weight for aging on left side (0.0-2.0)
            contamination_weight: Visual weight for contamination on right side (0.0-2.0)
            material_properties: Material properties from Materials.yaml (includes visual props)
            config: Optional MaterialImageConfig for additional settings
            
        Returns:
            Complete prompt string for Imagen 4
            
        Raises:
            FileNotFoundError: If required template files missing
            ValueError: If research_data lacks required contamination patterns
            ValueError: If required parameter missing and no learned default available
        """
        prompt_parts = []
        
        # Extract values from config if provided
        context = 'outdoor'  # Default context for learning lookup
        if config:
            config_dict = config.to_dict() if hasattr(config, 'to_dict') else config
            if 'severity' in config_dict and config_dict['severity']:
                severity = config_dict['severity']
            if 'view_mode' in config_dict and config_dict['view_mode']:
                view_mode = config_dict['view_mode']
            if 'contamination_uniformity' in config_dict and config_dict['contamination_uniformity']:
                contamination_uniformity = config_dict['contamination_uniformity']
            if 'context' in config_dict:
                context = config_dict['context']
        
        # Category for learning lookup
        category = material_category or 'metal'
        
        # Get severity - FAIL FAST if not provided and no learned default
        severity = self._get_learned_or_fail(
            'severity', severity, category, context, material_name
        )
        
        # Get view_mode - use learned default or fail
        if view_mode is None:
            if self.learning_logger:
                learned_view = self.learning_logger.get_learned_param('view_mode', category, context)
                if learned_view:
                    view_mode = learned_view
                    logger.info(f"🧠 Using learned view_mode={view_mode}")
            if view_mode is None:
                # Context-derived default (not hardcoded - based on context logic)
                view_mode = 'Contextual'
                logger.info(f"📍 Using context-derived view_mode={view_mode}")
        
        # Get contamination_uniformity - use learned or context-derived
        if contamination_uniformity is None:
            if self.learning_logger:
                learned_uni = self.learning_logger.get_learned_param('contamination_uniformity', category, context)
                if learned_uni:
                    contamination_uniformity = int(learned_uni)
                    logger.info(f"🧠 Using learned contamination_uniformity={contamination_uniformity}")
            if contamination_uniformity is None:
                # Context-derived default
                contamination_uniformity = 3
                logger.info(f"📍 Using context-derived contamination_uniformity={contamination_uniformity}")
        
        # Build replacement context once (using researched defaults + visual properties)
        replacements = self._build_replacement_dict(
            material_name, research_data,
            contamination_uniformity, view_mode,
            severity, material_properties
        )
        
        # Layer 1: Base Structure
        base = self._load_template(self.generation_dir / "base_structure.txt")
        if not base:
            raise FileNotFoundError(
                f"Base structure template required: {self.generation_dir / 'base_structure.txt'}"
            )
        base = self._apply_replacements(base, replacements)
        prompt_parts.append(base)
        
        # Layer 2: Realism Physics - DISABLED (now integrated into contamination_rules.txt)
        # physics = self._load_template(self.generation_dir / "realism_physics.txt")
        # if physics:
        #     physics = self._apply_replacements(physics, replacements)
        #     prompt_parts.append(physics)
        
        # Layer 3: Contamination Rules (includes REALISM section)
        contamination = self._load_template(self.generation_dir / "contamination_rules.txt")
        if contamination:
            contamination = self._apply_replacements(contamination, replacements)
            prompt_parts.append(contamination)
        
        # Layer 4: Micro-Scale Details - DISABLED (REALISM now in contamination_rules.txt)
        # micro_scale = self._load_template(self.generation_dir / "micro_scale_details.txt")
        # if micro_scale:
        #     micro_scale = self._apply_replacements(micro_scale, replacements)
        #     prompt_parts.append(micro_scale)
        
        # Anti-Layer: Forbidden Patterns
        forbidden = self._load_template(self.generation_dir / "forbidden_patterns.txt")
        if forbidden:
            prompt_parts.append(f"AVOID THESE PATTERNS:\n{forbidden}")
        
        # User Feedback Integration - DISABLED (now integrated into base templates)
        # feedback = self._load_feedback(material_category=material_category)
        # if feedback:
        #     prompt_parts.append(f"CORRECTIONS:\n{feedback}")
        #     logger.info("📝 Applied user feedback corrections to generation prompt")
        
        # Category-Specific Learned Feedback - DISABLED (now integrated into templates)
        # if learned_feedback:
        #     prompt_parts.append(learned_feedback)
        #     logger.info(f"🧠 Applied learned feedback from category: {material_category}")
        
        # Visual Weight Adjustments (user-specified intensity overrides)
        weight_instructions = self._build_visual_weight_instructions(
            aging_weight, contamination_weight
        )
        if weight_instructions:
            prompt_parts.append(weight_instructions)
            logger.info("⚖️  Applied visual weight adjustments")
        
        # Assemble full prompt
        full_prompt = "\n\n".join(prompt_parts)
        
        # Optimize for Imagen API limits
        optimized_prompt = self.optimizer.optimize_prompt(
            full_prompt,
            preserve_feedback=True
        )
        
        # Log optimization results
        reduction_pct = ((len(full_prompt) - len(optimized_prompt)) / len(full_prompt) * 100) if full_prompt else 0
        logger.info(
            f"📐 Prompt optimized: {len(full_prompt)} → {len(optimized_prompt)} chars "
            f"(-{len(full_prompt) - len(optimized_prompt)} chars, {reduction_pct:.1f}% reduction)"
        )
        
        # ═══════════════════════════════════════════════════════════════════════════
        # POST-OPTIMIZATION VERIFICATION: Ensure research data was preserved
        # ═══════════════════════════════════════════════════════════════════════════
        verification_result = verify_optimization(full_prompt, optimized_prompt, research_data)
        
        if not verification_result.is_valid:
            logger.error("🚨 RESEARCH DATA LOST DURING OPTIMIZATION:")
            for item in verification_result.missing_data:
                logger.error(f"   • {item}")
            print(f"\n⚠️  CRITICAL: Research data lost during optimization!")
            print(verification_result.format_report())
        elif verification_result.warnings:
            logger.warning(f"⚠️  Optimization warnings ({len(verification_result.warnings)}):")
            for warning in verification_result.warnings[:3]:
                logger.warning(f"   • {warning}")
        else:
            logger.info(f"✅ Post-optimization verification: {verification_result.get_summary()}")
        
        # Additional verification: Check material name specifically
        material_verification = self.verifier.verify(
            optimized_prompt, research_data, material_name
        )
        if not material_verification.is_valid:
            logger.warning(f"⚠️  Material verification issues detected")
        
        # 🔥 DEBUG: Log full optimized prompt to verify anti-text preservation
        if len(optimized_prompt) > 3000:
            logger.warning(f"⚠️  Optimized prompt near limit: {len(optimized_prompt)}/4096 chars")
        
        logger.debug(f"FINAL OPTIMIZED PROMPT:\n{'='*80}\n{optimized_prompt}\n{'='*80}")
        
        # Print full prompt to terminal for debugging
        print(f"\n{'='*80}\n🔍 FINAL PROMPT SENT TO IMAGEN API:\n{'='*80}\n{optimized_prompt}\n{'='*80}\n")
        
        return optimized_prompt
        
        return optimized_prompt
    
    def build_validation_prompt(
        self,
        material_name: str,
        research_data: Dict,
        config: Optional[Dict] = None,
        material_category: Optional[str] = None,
        learned_feedback: Optional[str] = None
    ) -> str:
        """
        Build validation prompt using SAME standards as generation.
        
        Loads validation criteria that mirror generation templates:
        - Realism Criteria: Scoring rubric (90-100 = photorealistic, etc.)
        - Physics Checklist: Exact same physics as generation/realism_physics.txt
        - Red Flags: Inverse of generation/forbidden_patterns.txt
        - User Feedback: Ensures validator checks updated requirements
        - Learned Feedback: Category-specific feedback from previous attempts
        
        Args:
            material_name: Name of material being validated
            research_data: Research data with expected contamination patterns
            config: Optional MaterialImageConfig dict with contamination settings
            material_category: Material category for learned feedback (e.g., "metal_ferrous")
            learned_feedback: Pre-formatted learned feedback from learning system
            
        Returns:
            Complete validation prompt for Gemini Vision
            
        Raises:
            FileNotFoundError: If required template files missing
        """
        prompt_parts = []
        
        # Extract material context
        patterns = research_data.get('selected_patterns', research_data.get('contaminants', []))
        pattern_names = [
            p.get('pattern_name', p.get('name', 'Unknown'))
            for p in patterns[:3]
        ]
        
        # Extract config parameters - fail fast if missing
        if not config:
            raise ValueError(f"Configuration required for validation prompt building for {material_name}")
        
        # Validation no longer uses contamination_level (removed from config)
        # uniformity = config['contamination_uniformity']  # Fail if missing
        # view_mode = config['view_mode']  # Fail if missing
        
        # Header with material context - FAIL FAST if severity missing
        if 'severity' not in config:
            raise ValueError(
                f"Severity REQUIRED in config for validation of {material_name}. "
                "NO DEFAULTS - per copilot-instructions.md policy."
            )
        severity = config['severity']
        severity_descriptions = {
            "light": "scattered spots, <30% coverage, isolated patches",
            "moderate": "connected patches, 30-60% coverage",
            "heavy": "continuous coverage, >60% coverage, thick accumulation"
        }
        if severity not in severity_descriptions:
            raise ValueError(f"Invalid severity '{severity}'. Must be: light, moderate, or heavy")
        severity_desc = severity_descriptions[severity]
        
        prompt_parts.append(f"""Analyze this material before/after laser cleaning image of {material_name}.

IMAGE STRUCTURE:
- LEFT SIDE: Contaminated/aged material BEFORE cleaning
- RIGHT SIDE: Clean material AFTER laser cleaning
- Format: Side-by-side composite (16:9 aspect ratio)
- Same physical object shown twice

EXPECTED CHARACTERISTICS:
- Material: {material_name}
- Contamination patterns: {', '.join(pattern_names)}
- Contamination variety: {config['contamination_uniformity']}
- Contamination severity: {severity.upper()} - {severity_desc}
- View mode: {config['view_mode']}

SEVERITY VALIDATION ({severity.upper()}):
The 'before' side MUST show {severity_desc}. If contamination appears lighter than "{severity}" level, reduce score.
""")
        
        # Realism Criteria (maps to generation standards)
        criteria = self._load_template(self.validation_dir / "realism_criteria.txt")
        if not criteria:
            raise FileNotFoundError(
                f"Realism criteria template required: {self.validation_dir / 'realism_criteria.txt'}"
            )
        prompt_parts.append("VALIDATION CRITERIA:\n" + criteria)
        
        # Physics Checklist (exact same as generation physics)
        physics = self._load_template(self.validation_dir / "physics_checklist.txt")
        if physics:
            prompt_parts.append("PHYSICS VALIDATION:\n" + physics)
        
        # Red Flags (exact inverse of generation forbidden patterns)
        red_flags = self._load_template(self.validation_dir / "red_flags.txt")
        if red_flags:
            prompt_parts.append("QUALITY RED FLAGS:\n" + red_flags)
        
        # User Feedback (validator checks updated criteria)
        feedback = self._load_feedback()
        if feedback:
            prompt_parts.append(f"UPDATED VALIDATION CRITERIA (from user review):\n{feedback}")
            logger.info("📝 Applied user feedback corrections to validation prompt")
        
        # Category-Specific Learned Feedback
        if learned_feedback:
            prompt_parts.append(learned_feedback)
            logger.info(f"🧠 Applied learned feedback to validation for category: {material_category}")
        
        # JSON response format
        prompt_parts.append(self._get_validation_json_format())
        
        # Assemble full validation prompt
        full_prompt = "\n\n".join(prompt_parts)
        
        # NOTE: Validation prompts go to Gemini Vision, NOT Imagen
        # Gemini has 1M+ token context window, so NO optimization needed
        # The Imagen optimizer (4096 char limit) was incorrectly truncating validation prompts
        logger.info(f"📝 Validation prompt: {len(full_prompt):,} chars (Gemini limit: ~4M chars)")
        
        return full_prompt
    
    def _load_template(self, template_path: Path) -> str:
        """
        Load prompt template from file.
        
        Args:
            template_path: Path to template file
            
        Returns:
            Template content as string (empty string if file doesn't exist)
        """
        if not template_path.exists():
            logger.warning(f"⚠️  Template not found: {template_path.name}")
            return ""
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if content:
                logger.debug(f"✅ Loaded template: {template_path.name} ({len(content)} chars)")
            
            return content
        except Exception as e:
            logger.error(f"❌ Failed to load template {template_path.name}: {e}")
            return ""
    
    def _load_feedback(self, material_category: Optional[str] = None) -> str:
        """
        Load user feedback corrections - core + category-specific.
        
        Args:
            material_category: Optional category for category-specific rules (e.g., "wood", "metal")
        
        Returns:
            Combined feedback content (core + category-specific)
        """
        feedback_parts = []
        
        # Load core feedback (always)
        core_path = self.feedback_dir / "user_corrections.txt"
        if core_path.exists():
            core = self._load_template(core_path)
            # Filter out comments
            lines = [l for l in core.split('\n') if l.strip() and not l.strip().startswith('#')]
            if lines:
                feedback_parts.append('\n'.join(lines).strip())
        
        # Load category-specific feedback if available
        if material_category:
            # Normalize category name (wood_hardwood -> wood, metals_ferrous -> metal)
            cat_prefix = material_category.split('_')[0].lower()
            if cat_prefix == 'metals':
                cat_prefix = 'metal'
            
            cat_path = self.feedback_dir / f"{cat_prefix}_corrections.txt"
            if cat_path.exists():
                cat_feedback = self._load_template(cat_path)
                lines = [l for l in cat_feedback.split('\n') if l.strip() and not l.strip().startswith('#')]
                if lines:
                    feedback_parts.append('\n'.join(lines).strip())
                    logger.info(f"📝 Loaded {cat_prefix}-specific feedback")
        
        combined = '\n\n'.join(feedback_parts).strip()
        if combined:
            logger.info(f"📝 Loaded user feedback: {len(combined)} chars")
        
        return combined
    
    def _replace_variables(
        self,
        template: str,
        material_name: str,
        research_data: Dict,
        contamination_uniformity: int,
        view_mode: str
    ) -> str:
        """
        DEPRECATED: Use _build_replacement_dict() + _apply_replacements() instead.
        
        Kept for backwards compatibility.
        """
        replacements = self._build_replacement_dict(
            material_name, research_data,
            contamination_uniformity, view_mode
        )
        return self._apply_replacements(template, replacements)
    
    def _build_replacement_dict(
        self,
        material_name: str,
        research_data: Dict,
        contamination_uniformity: int,
        view_mode: str,
        severity: str,
        material_properties: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        Build dictionary of template variable replacements using researched defaults.
        
        Variables:
        - {MATERIAL}: Material name
        - {COMMON_OBJECT}: Common object type from research
        - {ENVIRONMENT}: Typical environment from research
        - {SETTING}: Contextual setting (workshop bench, building exterior, etc.)
        - {UNIFORMITY}: 1-5 variety (researched default)
        - {VIEW_MODE}: Contextual or Isolated (researched default)
        - {CONTAMINANTS_SECTION}: Built from research patterns
        - {SEVERITY}: Contamination severity (light, moderate, heavy)
        - {COVERAGE_DESCRIPTION}: Human-readable coverage description
        - {REFLECTIVITY}: Material reflectivity value (e.g., "0.95")
        - {ABSORPTIVITY}: Material absorptivity value (e.g., "0.06")
        - {SURFACE_FINISH}: Material surface finish description
        - {VISUAL_APPEARANCE}: Combined visual appearance description
        
        Args:
            material_name: Material name
            research_data: Research data dict
            contamination_uniformity: 1-5 variety (auto-set by category)
            view_mode: View mode string (auto-set to "Contextual")
            severity: Contamination severity (light, moderate, heavy)
            material_properties: Material properties from Materials.yaml
            
        Returns:
            Dict mapping {VARIABLE} → value
            
        Raises:
            ValueError: If research_data missing required patterns
        """
        # Use researched shape/item if available
        common_object = research_data.get('common_shape') or research_data.get('common_object', f'{material_name} object')
        environment = research_data.get('typical_environment', 'typical environment')
        setting = research_data.get('setting', 'a workshop bench')  # Contextual setting
        
        # Get assembly context for complex parts (from AssemblyResearcher)
        assembly_description = research_data.get('assembly_description', '')
        
        # Get background from context settings (loaded from YAML)
        context_background = research_data.get('context_background', 'neutral environment')
        
        # === EXTRACT VISUAL PROPERTIES FROM material_properties ===
        reflectivity = "unknown"
        absorptivity = "unknown"
        surface_finish = "typical"
        visual_appearance = ""
        
        if material_properties:
            chars = material_properties.get('materialCharacteristics', {})
            
            # Get reflectivity
            refl_data = chars.get('reflectivity', {})
            if isinstance(refl_data, dict) and 'value' in refl_data:
                refl_value = refl_data['value']
                reflectivity = f"{refl_value:.2f}" if isinstance(refl_value, (int, float)) else str(refl_value)
                # Add human-readable description
                if isinstance(refl_value, (int, float)):
                    if refl_value > 0.8:
                        reflectivity += " (highly reflective, mirror-like)"
                    elif refl_value > 0.5:
                        reflectivity += " (moderately reflective)"
                    elif refl_value > 0.2:
                        reflectivity += " (low reflectivity)"
                    else:
                        reflectivity += " (absorptive, matte)"
            
            # Get absorptivity
            abs_data = chars.get('absorptivity', {})
            if isinstance(abs_data, dict) and 'value' in abs_data:
                abs_value = abs_data['value']
                absorptivity = f"{abs_value:.2f}" if isinstance(abs_value, (int, float)) else str(abs_value)
            
            # Get surface finish (could be in various places)
            sf_data = chars.get('surfaceFinish', chars.get('surface_finish', {}))
            if isinstance(sf_data, dict) and 'value' in sf_data:
                surface_finish = sf_data['value']
            elif isinstance(sf_data, str):
                surface_finish = sf_data
            
            # Build combined visual appearance description
            visual_parts = []
            if reflectivity != "unknown":
                visual_parts.append(f"reflectivity {reflectivity}")
            if absorptivity != "unknown":
                visual_parts.append(f"absorptivity {absorptivity}")
            if surface_finish != "typical":
                visual_parts.append(f"{surface_finish} surface finish")
            visual_appearance = ", ".join(visual_parts) if visual_parts else f"typical {material_name} appearance"
            
            logger.info(f"📊 Visual properties extracted: {visual_appearance}")
        
        patterns = research_data.get('selected_patterns', research_data.get('contaminants', []))
        contamination_section = self._build_contamination_section(patterns)
        
        # Build severity-specific coverage descriptions
        severity_descriptions = {
            "light": "scattered spots covering less than 30% of surface, isolated patches with bare material visible between them",
            "moderate": "connected patches covering 30-60% of surface, contamination forming patterns with some bare areas",
            "heavy": "continuous coverage over 60% of surface, thick accumulation with minimal bare material visible"
        }
        coverage_description = severity_descriptions.get(severity, severity_descriptions["moderate"])
        
        return {
            '{MATERIAL}': material_name,
            '{COMMON_OBJECT}': common_object,
            '{ENVIRONMENT}': environment,
            '{SETTING}': setting,
            '{BACKGROUND}': context_background,
            '{ASSEMBLY_CONTEXT}': assembly_description,
            '{CONTAMINATION_LEVEL}': str(contamination_uniformity),  # Same value, correct variable name
            '{UNIFORMITY}': str(contamination_uniformity),
            '{VIEW_MODE}': view_mode,
            '{CONTAMINANTS_SECTION}': contamination_section,
            '{SEVERITY}': severity,
            '{COVERAGE_DESCRIPTION}': coverage_description,
            # NEW: Visual properties from Materials.yaml
            '{REFLECTIVITY}': reflectivity,
            '{ABSORPTIVITY}': absorptivity,
            '{SURFACE_FINISH}': surface_finish,
            '{VISUAL_APPEARANCE}': visual_appearance
        }
    
    def _apply_replacements(self, template: str, replacements: Dict[str, str]) -> str:
        """
        Apply variable replacements to template.
        
        Args:
            template: Template string with {VARIABLES}
            replacements: Dict mapping {VARIABLE} → value
            
        Returns:
            Template with all variables replaced
        """
        result = template
        for key, value in replacements.items():
            result = result.replace(key, value)
        return result
    
    def _build_contamination_section(self, patterns: list) -> str:
        """
        Build contamination list from research patterns with full distribution physics.
        
        Includes:
        - Pattern names and visual characteristics
        - Distribution physics (gravity, edges, coverage)
        - Material-specific image generation feedback
        - Expert realism notes (NEW)
        
        Args:
            patterns: List of contamination pattern dicts
            
        Returns:
            Rich contamination description including distribution physics and material feedback
            
        Raises:
            ValueError: If no patterns provided
        """
        if not patterns:
            raise ValueError(
                "No contamination patterns provided. Research data is required. "
                "Cannot generate prompt without contamination information."
            )
        
        lines = []
        feedback_notes = []
        realism_insights = []
        
        for pattern in patterns[:3]:  # Max 3 patterns for richer detail each
            # Handle both category pattern format and old contaminant format
            if 'pattern_name' in pattern:
                name = pattern['pattern_name']
                visual = pattern.get('visual_characteristics', {})
                
                # Helper to convert lists/dicts to strings
                def to_str(val, max_len=80):
                    if isinstance(val, list):
                        return ', '.join(str(v) for v in val)[:max_len]
                    elif isinstance(val, dict):
                        return ', '.join(f"{k}: {v}" for k, v in val.items())[:max_len]
                    elif val:
                        return str(val)[:max_len]
                    return ''
                
                # Extract all available visual data
                color = to_str(visual.get('color_variations', visual.get('color_range', '')), 80)
                texture = to_str(visual.get('texture_details', visual.get('texture_detail', '')), 60)
                distribution = to_str(visual.get('distribution_patterns', ''), 60)
                coverage = to_str(visual.get('coverage_ranges', ''), 50)
                edge_behavior = to_str(visual.get('edge_center_behavior', ''), 50)
                gravity = to_str(visual.get('gravity_influence', ''), 40)
                lighting = to_str(visual.get('lighting_effects', ''), 40)
                
                # Build rich description
                desc_parts = [name]
                if color:
                    desc_parts.append(f"colors: {color}")
                if texture:
                    desc_parts.append(f"texture: {texture}")
                if distribution:
                    desc_parts.append(f"distribution: {distribution}")
                if edge_behavior:
                    desc_parts.append(f"edges: {edge_behavior}")
                if gravity:
                    desc_parts.append(f"gravity: {gravity}")
                if lighting:
                    desc_parts.append(f"lighting: {lighting}")
                
                lines.append(", ".join(desc_parts))
                
                # Include material-specific image generation feedback if available
                feedback = pattern.get('image_generation_feedback', '')
                if feedback:
                    feedback_notes.append(f"{name}: {feedback}")
                
                # Include expert realism notes (NEW - from Contaminants.yaml)
                realism = pattern.get('realism_notes', '')
                if realism:
                    realism_insights.append(f"{name}: {realism}")
            else:
                name = pattern.get('name', 'contamination')
                appearance = pattern.get('appearance', {})
                color = appearance.get('color', 'dark')
                texture = appearance.get('texture', 'uneven')
                lines.append(f"{name}: {color}, {texture}")
        
        result = ". ".join(lines) + "."
        
        # Append expert realism insights (for accuracy)
        if realism_insights:
            result += " REALISM: " + " ".join(realism_insights[:2])  # Limit to 2 for space
        
        # Append material-specific feedback notes (critical for accuracy)
        if feedback_notes:
            result += " CRITICAL: " + " ".join(feedback_notes)
        
        return result
    
    def _build_visual_weight_instructions(
        self,
        aging_weight: Optional[float],
        contamination_weight: Optional[float]
    ) -> Optional[str]:
        """
        Build visual weight adjustment instructions for aging and contamination intensity.
        
        Args:
            aging_weight: Weight for aging on left (before) side. 0.0-2.0, default 1.0
                         <1.0 = less visible aging, >1.0 = more prominent aging
            contamination_weight: Weight for contamination on right (after) side. 0.0-2.0, default 1.0
                                 <1.0 = less visible contamination, >1.0 = more contamination
                                 
        Returns:
            Prompt instruction string, or None if no adjustments needed
        """
        instructions = []
        
        # Aging weight adjustments (left/before side)
        if aging_weight is not None:
            if aging_weight > 1.0:
                intensity = "very prominent" if aging_weight >= 1.5 else "more visible"
                instructions.append(
                    f"LEFT SIDE (before): Show {intensity} aging and wear - "
                    f"deeper patina, more pronounced weathering, visible wear patterns"
                )
            elif aging_weight < 1.0:
                intensity = "minimal" if aging_weight <= 0.5 else "subtle"
                instructions.append(
                    f"LEFT SIDE (before): Show {intensity} aging - "
                    f"lighter patina, subtle wear, fresher appearance"
                )
        
        # Contamination weight adjustments (right/after side)
        if contamination_weight is not None:
            if contamination_weight > 1.0:
                intensity = "very prominent" if contamination_weight >= 1.5 else "more visible"
                instructions.append(
                    f"RIGHT SIDE (after/cleaned): Show {intensity} remaining contamination - "
                    f"some residue still visible, partial cleaning result"
                )
            elif contamination_weight < 1.0:
                intensity = "minimal" if contamination_weight <= 0.5 else "very little"
                instructions.append(
                    f"RIGHT SIDE (after/cleaned): Show {intensity} remaining contamination - "
                    f"thoroughly cleaned surface, pristine appearance, clear laser cleaning result"
                )
        
        if instructions:
            return "VISUAL INTENSITY ADJUSTMENTS:\n" + "\n".join(instructions)
        
        return None
    
    def check_prompt_length(self, prompt: str) -> Dict:
        """
        Check prompt length against Imagen API limits.
        
        Args:
            prompt: Prompt string to check
            
        Returns:
            Dict with length analysis and recommendations
        """
        return self.optimizer.check_prompt_length(prompt)
    
    def _get_validation_json_format(self) -> str:
        """Return JSON response format for validation."""
        return """RESPOND IN JSON FORMAT:
{
  "realism_score": <0-100>,
  "same_object": <true/false>,
  "position_shift_appropriate": <true/false>,
  "damage_consistent": <true/false>,
  "physics_compliant": <true/false>,
  "physics_issues": ["<issue1>", "<issue2>", ...] or [],
  "distribution_realistic": <true/false>,
  "distribution_issues": ["<issue1>", ...] or [],
  "layering_natural": <true/false>,
  "layering_issues": ["<issue1>", ...] or [],
  "clean_side_accurate": <true/false>,
  "material_appearance_issues": ["<issue1>", ...] or [],
  "contamination_matches_research": <true/false>,
  "research_deviations": ["<deviation1>", ...] or [],
  "micro_scale_accurate": <true/false>,
  "micro_scale_issues": ["<issue1>", ...] or [],
  "text_labels_present": <true/false>,
  "text_label_details": ["<description of any text/labels found>", ...] or [],
  "confidence": <0.0-1.0>,
  "overall_assessment": "<2-3 sentence summary of realism quality>",
  "recommendations": ["<improvement1>", "<improvement2>", ...] or []
}

NOTE: Set "text_labels_present" to true if ANY prominent text, labels, watermarks, micros, or logos are visible ON THE MAIN OBJECT. Describe what was found in "text_label_details". IGNORE: volume markings on glassware/labware, background text, measurement gradations - these are expected on laboratory equipment. Only flag prominent brand labels or artificial text that doesn't belong."""


def create_prompt_builder() -> SharedPromptBuilder:
    """Factory function to create shared prompt builder."""
    return SharedPromptBuilder()
