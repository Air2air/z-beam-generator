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
    
    def build_generation_prompt(
        self,
        material_name: str,
        research_data: Dict,
        contamination_uniformity: int = 3,
        view_mode: str = "Contextual",
        material_category: Optional[str] = None,
        learned_feedback: Optional[str] = None,
        severity: str = "moderate",
        aging_weight: Optional[float] = None,
        contamination_weight: Optional[float] = None
    ) -> str:
        """
        Build complete generation prompt from shared templates + researched defaults.
        
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
        
        Args:
            material_name: Name of material (e.g., "Aluminum")
            research_data: Research data with contamination patterns
            contamination_uniformity: Variety 1-5 (default: 3, researched default)
            view_mode: "Contextual" or "Isolated" (default: "Contextual")
            material_category: Material category for learned feedback (e.g., "metal_ferrous")
            learned_feedback: Pre-formatted learned feedback from learning system
            severity: Contamination severity - "light" (<30%), "moderate" (30-60%), "heavy" (>60%)
            aging_weight: Visual weight for aging on left side (0.0-2.0, default 1.0)
            contamination_weight: Visual weight for contamination on right side (0.0-2.0, default 1.0)
            
        Returns:
            Complete prompt string for Imagen 4
            
        Raises:
            FileNotFoundError: If required template files missing
            ValueError: If research_data lacks required contamination patterns
        """
        prompt_parts = []
        
        # Build replacement context once (using researched defaults)
        replacements = self._build_replacement_dict(
            material_name, research_data,
            contamination_uniformity, view_mode,
            severity
        )
        
        # Layer 1: Base Structure
        base = self._load_template(self.generation_dir / "base_structure.txt")
        if not base:
            raise FileNotFoundError(
                f"Base structure template required: {self.generation_dir / 'base_structure.txt'}"
            )
        base = self._apply_replacements(base, replacements)
        prompt_parts.append(base)
        
        # Layer 2: Realism Physics
        physics = self._load_template(self.generation_dir / "realism_physics.txt")
        if physics:
            physics = self._apply_replacements(physics, replacements)
            prompt_parts.append(physics)
        
        # Layer 3: Contamination Rules
        contamination = self._load_template(self.generation_dir / "contamination_rules.txt")
        if contamination:
            contamination = self._apply_replacements(contamination, replacements)
            prompt_parts.append(contamination)
        
        # Layer 4: Micro-Scale Details
        micro_scale = self._load_template(self.generation_dir / "micro_scale_details.txt")
        if micro_scale:
            micro_scale = self._apply_replacements(micro_scale, replacements)
            prompt_parts.append(micro_scale)
        
        # Anti-Layer: Forbidden Patterns
        forbidden = self._load_template(self.generation_dir / "forbidden_patterns.txt")
        if forbidden:
            prompt_parts.append(f"AVOID THESE PATTERNS:\n{forbidden}")
        
        # User Feedback Integration (core + category-specific)
        feedback = self._load_feedback(material_category=material_category)
        if feedback:
            prompt_parts.append(f"CORRECTIONS:\n{feedback}")
            logger.info("📝 Applied user feedback corrections to generation prompt")
        
        # Category-Specific Learned Feedback
        if learned_feedback:
            prompt_parts.append(learned_feedback)
            logger.info(f"🧠 Applied learned feedback from category: {material_category}")
        
        # Visual Weight Adjustments (user-specified intensity overrides)
        weight_instructions = self._build_visual_weight_instructions(
            aging_weight, contamination_weight
        )
        if weight_instructions:
            prompt_parts.append(weight_instructions)
            logger.info(f"⚖️  Applied visual weight adjustments")
        
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
        
        # 🔥 DEBUG: Log full optimized prompt to verify anti-text preservation
        if len(optimized_prompt) > 3000:
            logger.warning(f"⚠️  Optimized prompt near limit: {len(optimized_prompt)}/4096 chars")
        
        logger.debug(f"FINAL OPTIMIZED PROMPT:\n{'='*80}\n{optimized_prompt}\n{'='*80}")
        
        # 🔥 TEMPORARY: Print full prompt to terminal for debugging
        print(f"\n{'='*80}\n🔍 FINAL PROMPT SENT TO IMAGEN API:\n{'='*80}\n{optimized_prompt}\n{'='*80}\n")
        
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
        
        # Header with material context
        prompt_parts.append(f"""Analyze this material before/after laser cleaning image of {material_name}.

IMAGE STRUCTURE:
- LEFT SIDE: Contaminated/aged material BEFORE cleaning
- RIGHT SIDE: Clean material AFTER laser cleaning
- Format: Side-by-side composite (16:9 aspect ratio)
- Same physical object shown twice

EXPECTED CHARACTERISTICS:
- Material: {material_name}
- Contamination patterns: {', '.join(pattern_names)}
- Contamination variety: {config.get('contamination_uniformity', 'researched default')}
- View mode: {config.get('view_mode', 'Contextual')}
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
        
        # Optimize for API limits - PRESERVE JSON format specification
        optimized_prompt = self.optimizer.optimize_prompt(
            full_prompt,
            preserve_feedback=True,
            preserve_json_format=True  # Critical: JSON format must not be truncated
        )
        
        return optimized_prompt
    
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
        severity: str = "moderate"
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
        
        Args:
            material_name: Material name
            research_data: Research data dict
            contamination_uniformity: 1-5 variety (auto-set by category)
            view_mode: View mode string (auto-set to "Contextual")
            severity: Contamination severity (light, moderate, heavy)
            
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
            '{COVERAGE_DESCRIPTION}': coverage_description
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
        Build contamination list from research patterns.
        
        Args:
            patterns: List of contamination pattern dicts
            
        Returns:
            Concise contamination description
            
        Raises:
            ValueError: If no patterns provided
        """
        if not patterns:
            raise ValueError(
                "No contamination patterns provided. Research data is required. "
                "Cannot generate prompt without contamination information."
            )
        
        lines = []
        for pattern in patterns[:4]:  # Max 4 patterns
            # Handle both category pattern format and old contaminant format
            if 'pattern_name' in pattern:
                name = pattern['pattern_name']
                visual = pattern.get('visual_characteristics', {})
                color = visual.get('color_range', 'varied tones')
                texture = visual.get('texture_detail', 'varied texture')
                lines.append(f"{name}: {color}, {texture}")
            else:
                name = pattern.get('name', 'contamination')
                appearance = pattern.get('appearance', {})
                color = appearance.get('color', 'dark')
                texture = appearance.get('texture', 'uneven')
                lines.append(f"{name}: {color}, {texture}")
        
        return ". ".join(lines) + "."
    
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

CRITICAL: Set "text_labels_present" to true if ANY text, labels, watermarks, captions, logos, numbers, letters, or written characters are visible anywhere in the image. Describe what was found in "text_label_details". Images with text/labels automatically fail validation."""


def create_prompt_builder() -> SharedPromptBuilder:
    """Factory function to create shared prompt builder."""
    return SharedPromptBuilder()
