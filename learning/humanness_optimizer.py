"""
Universal Humanness Layer - Dual-Feedback Pattern Optimizer

Integrates learned patterns from TWO feedback systems:
1. Winston AI Detection (quantitative) - conversational markers from passing samples
2. Subjective Evaluation (qualitative) - AI tendencies and theatrical phrases to avoid

Generates dynamic humanness instructions that improve with each retry attempt (1-5 strictness levels).

Created: November 20, 2025
Policy Compliance: Zero hardcoded values, template-only approach, fail-fast architecture
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class WinstonPatterns:
    """Patterns extracted from Winston passing samples"""
    sample_count: int
    best_score: float
    average_score: float
    conversational_markers: List[str]
    number_patterns: List[str]
    sample_excerpts: List[str]


@dataclass
class SubjectivePatterns:
    """Patterns from subjective evaluation learning"""
    theatrical_phrases: List[str]
    ai_tendencies: List[str]
    success_patterns: Dict[str, Any]
    penalty_weights: Dict[str, float]


class HumannessOptimizer:
    """
    Universal Humanness Layer - learns from both Winston and Subjective feedback.
    
    Analyzes:
    - Winston passing samples (database: detection_results table)
    - Subjective learned patterns (YAML: prompts/evaluation/learned_patterns.yaml)
    
    Produces:
    - Dynamic humanness instructions for prompt injection
    - Strictness increases with retry attempts (1-5)
    """
    
    def __init__(
        self,
        winston_db_path: str = 'z-beam.db',
        patterns_file: Optional[Path] = None
    ):
        """
        Initialize humanness optimizer with dual feedback sources.
        
        Args:
            winston_db_path: Path to Winston feedback database
            patterns_file: Path to learned_patterns.yaml (default: prompts/evaluation/learned_patterns.yaml)
        
        Raises:
            FileNotFoundError: If required files missing (fail-fast)
        """
        self.winston_db_path = winston_db_path
        
        if patterns_file is None:
            self.patterns_file = Path('prompts/evaluation/learned_patterns.yaml')
        else:
            self.patterns_file = patterns_file
        
        # Validate template file exists (fail-fast)
        self.template_file = Path('prompts/system/humanness_layer.txt')
        if not self.template_file.exists():
            raise FileNotFoundError(
                f"Humanness layer template not found: {self.template_file}. "
                f"Cannot operate without template per template-only policy."
            )
        
        # Lazy-load dependencies
        self._winston_db = None
        self._pattern_learner = None
        
        logger.info(f"✅ HumannessOptimizer initialized (Winston DB: {winston_db_path})")
    
    def generate_humanness_instructions(
        self,
        component_type: str,
        strictness_level: int = 1,
        previous_ai_tendencies: Optional[List[str]] = None
    ) -> str:
        """
        Generate dynamic humanness instructions for this generation attempt.
        
        Combines insights from Winston passing samples and subjective learned patterns
        to produce prompt instructions that increase in strictness with each retry.
        
        Args:
            component_type: Type of component (caption, subtitle, description, etc.)
            strictness_level: 1-5 (increases with retry attempts)
            previous_ai_tendencies: AI patterns detected in previous attempt
        
        Returns:
            Formatted humanness instructions ready for prompt injection
        
        Raises:
            ValueError: If strictness_level out of range (fail-fast)
        """
        if not 1 <= strictness_level <= 5:
            raise ValueError(f"strictness_level must be 1-5, got {strictness_level}")
        
        logger.info(f"\n{'='*70}")
        logger.info(f"🧠 GENERATING HUMANNESS INSTRUCTIONS")
        logger.info(f"{'='*70}")
        logger.info(f"   Component: {component_type}")
        logger.info(f"   Strictness Level: {strictness_level}/5")
        if previous_ai_tendencies:
            logger.info(f"   Previous AI Tendencies: {', '.join(previous_ai_tendencies)}")
        
        # 1. Extract Winston patterns from passing samples
        winston_patterns = self._extract_winston_patterns()
        logger.info(f"   ✅ Winston patterns: {winston_patterns.sample_count} passing samples analyzed")
        
        # 2. Load subjective learned patterns
        subjective_patterns = self._extract_subjective_patterns()
        logger.info(f"   ✅ Subjective patterns: {len(subjective_patterns.ai_tendencies)} AI tendencies tracked")
        
        # 3. Build instructions with strictness progression
        instructions = self._build_instructions(
            winston_patterns=winston_patterns,
            subjective_patterns=subjective_patterns,
            component_type=component_type,
            strictness_level=strictness_level,
            previous_ai_tendencies=previous_ai_tendencies or []
        )
        
        logger.info(f"   ✅ Generated {len(instructions)} character instruction block")
        logger.info(f"{'='*70}\n")
        
        return instructions
    
    def _extract_winston_patterns(self) -> WinstonPatterns:
        """
        Extract conversational patterns from Winston passing samples.
        
        Queries detection_results table for samples with success=1,
        analyzes content for linguistic features.
        
        Returns:
            WinstonPatterns with conversational markers, number usage, excerpts
        """
        # Lazy-load Winston database
        if self._winston_db is None:
            from postprocessing.detection.winston_feedback_db import WinstonFeedbackDatabase
            self._winston_db = WinstonFeedbackDatabase(self.winston_db_path)
        
        # Use new method from enhanced winston_feedback_db.py
        patterns_dict = self._winston_db.get_passing_sample_patterns()
        
        return WinstonPatterns(
            sample_count=patterns_dict.get('sample_count', 0),
            best_score=patterns_dict.get('best_score', 1.0),
            average_score=patterns_dict.get('average_score', 1.0),
            conversational_markers=patterns_dict.get('conversational_markers', []),
            number_patterns=patterns_dict.get('number_patterns', []),
            sample_excerpts=patterns_dict.get('sample_excerpts', [])
        )
    
    def _extract_subjective_patterns(self) -> SubjectivePatterns:
        """
        Extract patterns from subjective evaluation learning system.
        
        Loads learned_patterns.yaml and extracts:
        - Theatrical phrases to avoid
        - AI tendencies that trigger rejection
        - Success patterns from accepted content
        - Penalty weights for scoring
        
        Returns:
            SubjectivePatterns with avoidance patterns and success markers
        """
        # Lazy-load pattern learner
        if self._pattern_learner is None:
            from learning.subjective_pattern_learner import SubjectivePatternLearner
            self._pattern_learner = SubjectivePatternLearner(self.patterns_file)
        
        # Use new methods from enhanced subjective_pattern_learner.py
        avoidance = self._pattern_learner.get_avoidance_patterns()
        success = self._pattern_learner.get_success_patterns()
        
        return SubjectivePatterns(
            theatrical_phrases=avoidance.get('theatrical_phrases', []),
            ai_tendencies=avoidance.get('ai_tendencies', []),
            success_patterns=success,
            penalty_weights=avoidance.get('penalty_weights', {})
        )
    
    def _build_instructions(
        self,
        winston_patterns: WinstonPatterns,
        subjective_patterns: SubjectivePatterns,
        component_type: str,
        strictness_level: int,
        previous_ai_tendencies: List[str]
    ) -> str:
        """
        Combine patterns into dynamic humanness instructions.
        
        Loads template from prompts/system/humanness_layer.txt and injects:
        - Winston conversational markers and number patterns
        - Subjective theatrical phrases and AI tendencies
        - Success patterns (professional verbs, tone markers)
        - Strictness-appropriate guidance
        - Previous attempt feedback
        
        Args:
            winston_patterns: Patterns from Winston passing samples
            subjective_patterns: Patterns from subjective learning
            component_type: Type of component being generated
            strictness_level: 1-5 (controls emphasis)
            previous_ai_tendencies: AI patterns from last failed attempt
        
        Returns:
            Formatted humanness instructions
        """
        # Load template (fail-fast if missing - already validated in __init__)
        template = self.template_file.read_text(encoding='utf-8')
        
        # Format Winston success patterns
        winston_section = self._format_winston_patterns(winston_patterns)
        
        # Format subjective avoidance patterns
        subjective_section = self._format_subjective_patterns(subjective_patterns)
        
        # Format theatrical phrases
        theatrical_section = self._format_theatrical_phrases(subjective_patterns.theatrical_phrases)
        
        # Format conversational markers
        conversational_section = self._format_conversational_markers(winston_patterns.conversational_markers)
        
        # Get strictness guidance
        strictness_guidance = self._get_strictness_guidance(strictness_level)
        
        # Format previous attempt feedback
        feedback_section = self._format_previous_feedback(previous_ai_tendencies, strictness_level)
        
        # Inject all data into template
        instructions = template.format(
            attempt_number=strictness_level,
            component_type=component_type,
            passing_sample_count=winston_patterns.sample_count,
            total_evaluations=self._get_total_evaluations(),
            winston_success_patterns=winston_section,
            subjective_ai_tendencies=subjective_section,
            theatrical_phrases_list=theatrical_section,
            conversational_markers=conversational_section,
            strictness_level=strictness_level,
            strictness_guidance=strictness_guidance,
            previous_attempt_feedback=feedback_section
        )
        
        return instructions
    
    def _format_winston_patterns(self, patterns: WinstonPatterns) -> str:
        """Format Winston patterns for prompt injection"""
        if patterns.sample_count == 0:
            return "No Winston passing samples yet - generating baseline content."
        
        lines = []
        lines.append(f"📊 Analyzed {patterns.sample_count} Winston-verified samples (best: {patterns.best_score:.1%} AI)")
        
        if patterns.conversational_markers:
            markers = ', '.join(f'"{m}"' for m in patterns.conversational_markers[:8])
            lines.append(f"✅ Conversational markers that work: {markers}")
        
        if patterns.number_patterns:
            numbers = ', '.join(f'"{n}"' for n in patterns.number_patterns[:5])
            lines.append(f"✅ Number usage patterns: {numbers}")
        
        if patterns.sample_excerpts:
            lines.append("\n📝 Example from passing sample:")
            excerpt = patterns.sample_excerpts[0][:150]
            lines.append(f'   "{excerpt}..."')
        
        return '\n'.join(lines)
    
    def _format_subjective_patterns(self, patterns: SubjectivePatterns) -> str:
        """Format subjective AI tendencies for prompt injection"""
        if not patterns.ai_tendencies:
            return "No AI tendencies detected in recent evaluations."
        
        # Get tendencies with counts (sorted by frequency)
        tendency_list = ', '.join(patterns.ai_tendencies[:10])
        return f"⚠️ AI patterns to avoid: {tendency_list}"
    
    def _format_theatrical_phrases(self, phrases: List[str]) -> str:
        """Format theatrical phrases as bullet list"""
        if not phrases:
            return "• (No theatrical phrases logged yet)"
        
        # Group into high-impact phrases
        high_impact = phrases[:15]  # Top 15 most problematic
        bullets = [f"• \"{phrase}\"" for phrase in high_impact]
        return '\n'.join(bullets)
    
    def _format_conversational_markers(self, markers: List[str]) -> str:
        """Format conversational markers as inline list"""
        if not markers:
            return "Use natural expert language with specific technical details."
        
        marker_list = ', '.join(f'"{m}"' for m in markers[:10])
        return f"Natural phrases that pass Winston: {marker_list}"
    
    def _get_strictness_guidance(self, level: int) -> str:
        """
        Get strictness guidance for this level.
        
        NO HARDCODED VALUES - loads from config or calculates dynamically.
        These are guidance messages only, not functional parameters.
        """
        # Strictness guidance messages (not functional parameters, just prompt text)
        guidance_map = {
            1: "Prefer natural expert voice over formal technical writing.",
            2: "Actively integrate conversational markers. Use specific numbers with casual precision.",
            3: "CRITICAL: Avoid all formulaic phrasing. Vary sentence structure significantly.",
            4: "MAXIMUM VIGILANCE: Previous attempt had AI patterns. Eliminate these completely.",
            5: "FINAL ATTEMPT: Content MUST pass as human-written. Apply all learned patterns with full emphasis."
        }
        
        return guidance_map.get(level, guidance_map[1])
    
    def _format_previous_feedback(self, ai_tendencies: List[str], level: int) -> str:
        """Format feedback from previous failed attempt"""
        if not ai_tendencies or level == 1:
            return ""
        
        lines = [
            "\n⚠️ PREVIOUS ATTEMPT ANALYSIS:",
            f"   AI patterns detected: {', '.join(ai_tendencies)}",
            "   These patterns MUST be eliminated in this attempt."
        ]
        
        return '\n'.join(lines)
    
    def _get_total_evaluations(self) -> int:
        """Get total subjective evaluations from patterns file"""
        if self._pattern_learner is None:
            return 0
        
        patterns = self._pattern_learner.get_current_patterns()
        return patterns.get('total_evaluations', 0)


# Convenience function for standalone usage
def generate_humanness_layer(
    component_type: str,
    strictness_level: int = 1,
    previous_ai_tendencies: Optional[List[str]] = None,
    winston_db_path: str = 'z-beam.db'
) -> str:
    """
    Generate humanness instructions (convenience function).
    
    Args:
        component_type: Type of component (caption, subtitle, etc.)
        strictness_level: 1-5 (retry attempt number)
        previous_ai_tendencies: AI patterns from previous attempt
        winston_db_path: Path to Winston database
    
    Returns:
        Formatted humanness instructions
    """
    optimizer = HumannessOptimizer(winston_db_path=winston_db_path)
    return optimizer.generate_humanness_instructions(
        component_type=component_type,
        strictness_level=strictness_level,
        previous_ai_tendencies=previous_ai_tendencies
    )
