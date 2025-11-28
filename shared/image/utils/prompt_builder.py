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
        learned_feedback: Optional[str] = None
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
        
        Args:
            material_name: Name of material (e.g., "Aluminum")
            research_data: Research data with contamination patterns
            contamination_uniformity: Variety 1-5 (default: 3, researched default)
            view_mode: "Contextual" or "Isolated" (default: "Contextual")
            material_category: Material category for learned feedback (e.g., "metal_ferrous")
            learned_feedback: Pre-formatted learned feedback from learning system
            
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
            contamination_uniformity, view_mode
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
        
        # User Feedback Integration
        feedback = self._load_feedback()
        if feedback:
            prompt_parts.append(f"CRITICAL CORRECTIONS (from user review):\n{feedback}")
            logger.info("📝 Applied user feedback corrections to generation prompt")
        
        # Category-Specific Learned Feedback
        if learned_feedback:
            prompt_parts.append(learned_feedback)
            logger.info(f"🧠 Applied learned feedback from category: {material_category}")
        
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
    
    def _load_feedback(self) -> str:
        """
        Load latest user feedback corrections.
        
        Returns:
            User feedback content (empty string if no feedback or file doesn't exist)
        """
        feedback_path = self.feedback_dir / "user_corrections.txt"
        
        if not feedback_path.exists():
            logger.debug("ℹ️  No user feedback file found (this is normal for initial runs)")
            return ""
        
        feedback = self._load_template(feedback_path)
        
        # Filter out comments and empty lines
        lines = []
        for line in feedback.split('\n'):
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                lines.append(line)
        
        filtered_feedback = '\n'.join(lines).strip()
        
        if filtered_feedback:
            logger.info(f"📝 Loaded user feedback: {len(filtered_feedback)} chars")
            return filtered_feedback
        
        return ""
    
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
        view_mode: str
    ) -> Dict[str, str]:
        """
        Build dictionary of template variable replacements using researched defaults.
        
        Variables:
        - {MATERIAL}: Material name
        - {COMMON_OBJECT}: Common object type from research
        - {ENVIRONMENT}: Typical environment from research
        - {UNIFORMITY}: 1-5 variety (researched default)
        - {VIEW_MODE}: Contextual or Isolated (researched default)
        - {CONTAMINANTS_SECTION}: Built from research patterns
        
        Args:
            material_name: Material name
            research_data: Research data dict
            contamination_uniformity: 1-5 variety (auto-set by category)
            view_mode: View mode string (auto-set to "Contextual")
            
        Returns:
            Dict mapping {VARIABLE} → value
            
        Raises:
            ValueError: If research_data missing required patterns
        """
        common_object = research_data.get('common_object', f'{material_name} object')
        environment = research_data.get('typical_environment', 'typical environment')
        
        patterns = research_data.get('selected_patterns', research_data.get('contaminants', []))
        contamination_section = self._build_contamination_section(patterns)
        
        return {
            '{MATERIAL}': material_name,
            '{COMMON_OBJECT}': common_object,
            '{ENVIRONMENT}': environment,
            '{CONTAMINATION_LEVEL}': str(contamination_uniformity),  # Same value, correct variable name
            '{UNIFORMITY}': str(contamination_uniformity),
            '{VIEW_MODE}': view_mode,
            '{CONTAMINANTS_SECTION}': contamination_section
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
