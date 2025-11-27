"""
Universal Humanness Layer - Dual-Feedback Pattern Optimizer

Integrates learned patterns from TWO feedback systems:
1. Winston AI Detection (quantitative) - conversational markers from passing samples
2. Subjective Evaluation (qualitative) - AI tendencies and theatrical phrases to avoid

Generates dynamic humanness instructions that improve with each retry attempt (1-5 strictness levels).

Created: November 20, 2025
Updated: November 22, 2025 - Config-driven randomization (zero hardcoded values)
Policy Compliance: Zero hardcoded values, template-only approach, fail-fast architecture
"""

import re
import random
import yaml
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


@dataclass
class StructuralPatterns:
    """Patterns from structural variation analysis"""
    sample_count: int
    average_diversity: float
    successful_openings: List[str]  # High-scoring opening patterns
    overused_openings: List[str]  # Recent patterns to avoid
    diverse_structures: List[str]  # Successful structure types
    linguistic_diversity: List[str]  # Diverse linguistic patterns


class HumannessOptimizer:
    """
    Universal Humanness Layer - learns from THREE feedback sources.
    
    Analyzes:
    - Winston passing samples (database: detection_results table)
    - Subjective learned patterns (YAML: prompts/evaluation/learned_patterns.yaml)
    - Structural diversity patterns (database: structural_patterns table)
    
    Produces:
    - Dynamic humanness instructions for prompt injection
    - Strictness increases with retry attempts (1-5)
    """
    
    def __init__(
        self,
        winston_db_path: str = 'z-beam.db',
        patterns_file: Optional[Path] = None,
        structural_db_path: Optional[str] = None,
        config_path: str = 'generation/config.yaml'
    ):
        """
        Initialize humanness optimizer with triple feedback sources.
        
        Args:
            winston_db_path: Path to Winston feedback database
            patterns_file: Path to learned_patterns.yaml (default: prompts/evaluation/learned_patterns.yaml)
            structural_db_path: Path to structural patterns database (default: data/winston_feedback.db)
            config_path: Path to config.yaml for randomization targets (default: generation/config.yaml)
        
        Raises:
            FileNotFoundError: If required files missing (fail-fast)
            ValueError: If config.yaml missing randomization_targets section
        """
        self.winston_db_path = winston_db_path
        self.structural_db_path = structural_db_path or 'data/winston_feedback.db'
        
        if patterns_file is None:
            self.patterns_file = Path('shared/text/templates/evaluation/learned_patterns.yaml')
        else:
            self.patterns_file = patterns_file
        
        # Validate template file exists (fail-fast)
        self.template_file = Path('shared/text/templates/system/humanness_layer.txt')
        if not self.template_file.exists():
            raise FileNotFoundError(
                f"Humanness layer template not found: {self.template_file}. "
                f"Cannot operate without template per template-only policy."
            )
        
        # Load configuration for randomization targets (fail-fast)
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}. "
                f"Cannot operate without randomization_targets config."
            )
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        if 'randomization_targets' not in self.config:
            raise ValueError(
                f"Missing 'randomization_targets' in {self.config_path}. "
                f"Zero hardcoded values policy requires config-driven randomization."
            )
        
        # Lazy-load dependencies
        self._winston_db = None
        self._pattern_learner = None
        
        logger.info(f"✅ HumannessOptimizer initialized (Winston DB: {winston_db_path}, Config: {config_path})")
    
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
        
        # 3. Extract structural diversity patterns
        structural_patterns = self._extract_structural_patterns(component_type)
        logger.info(f"   ✅ Structural patterns: {structural_patterns.sample_count} samples, avg diversity {structural_patterns.average_diversity:.1f}/10")
        
        # 4. Build instructions with strictness progression
        instructions = self._build_instructions(
            winston_patterns=winston_patterns,
            subjective_patterns=subjective_patterns,
            structural_patterns=structural_patterns,
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
    
    def _extract_structural_patterns(self, component_type: str) -> StructuralPatterns:
        """
        Extract structural diversity patterns from database.
        
        Queries structural_patterns table for:
        - Successful patterns (diversity ≥8.0, passed=1)
        - Overused patterns (opening repetition >2)
        - Diverse structural approaches
        - Linguistic pattern variety
        
        Args:
            component_type: Type of component to analyze
        
        Returns:
            StructuralPatterns with learned diversity insights
        """
        import sqlite3
        
        try:
            conn = sqlite3.connect(self.structural_db_path)
            cursor = conn.cursor()
            
            # Get successful high-diversity patterns
            cursor.execute('''
                SELECT opening_pattern, structure_type, linguistic_patterns, diversity_score
                FROM structural_patterns
                WHERE component_type = ? AND passed = 1 AND diversity_score >= 8.0
                ORDER BY diversity_score DESC
                LIMIT 10
            ''', (component_type,))
            
            successful_rows = cursor.fetchall()
            successful_openings = []
            diverse_structures = []
            linguistic_diversity = []
            
            for row in successful_rows:
                opening, structure, linguistic, score = row
                if opening and opening not in successful_openings:
                    successful_openings.append(opening)
                if structure and structure not in diverse_structures:
                    diverse_structures.append(structure)
                if linguistic:
                    patterns = linguistic.split(',')
                    for p in patterns:
                        if p.strip() and p.strip() not in linguistic_diversity:
                            linguistic_diversity.append(p.strip())
            
            # Priority 3: Get recent patterns with usage statistics for weighted cooldown
            cursor.execute('''
                SELECT opening_pattern, 
                       COUNT(*) as frequency,
                       MAX(timestamp) as last_used,
                       julianday('now') - julianday(MAX(timestamp)) as days_since_use
                FROM structural_patterns
                WHERE component_type = ? 
                  AND timestamp > datetime('now', '-7 days')
                GROUP BY opening_pattern
                ORDER BY frequency DESC, last_used DESC
            ''', (component_type,))
            
            recent_usage_rows = cursor.fetchall()
            overused_openings = []
            
            # Priority 3: Identify overused patterns (used 3+ times in last 7 days or used in last 2 gens)
            for row in recent_usage_rows:
                pattern, freq, last_used, days_since = row
                if pattern and (freq >= 3 or days_since < 0.1):  # 0.1 days = ~2 hours
                    overused_openings.append(pattern)
            
            overused_openings = overused_openings[:5]  # Top 5 overused patterns
            
            # Get statistics
            cursor.execute('''
                SELECT COUNT(*), AVG(diversity_score)
                FROM structural_patterns
                WHERE component_type = ?
            ''', (component_type,))
            
            stats = cursor.fetchone()
            sample_count = stats[0] if stats else 0
            average_diversity = stats[1] if stats and stats[1] else 0.0
            
            conn.close()
            
            return StructuralPatterns(
                sample_count=sample_count,
                average_diversity=average_diversity,
                successful_openings=successful_openings[:8],  # Top 8 diverse openings
                overused_openings=overused_openings,
                diverse_structures=diverse_structures[:5],  # Top 5 structure types
                linguistic_diversity=linguistic_diversity[:12]  # Up to 12 patterns
            )
            
        except Exception as e:
            logger.warning(f"Could not extract structural patterns: {e}")
            # Return empty patterns (don't fail generation)
            return StructuralPatterns(
                sample_count=0,
                average_diversity=0.0,
                successful_openings=[],
                overused_openings=[],
                diverse_structures=[],
                linguistic_diversity=[]
            )
    
    def _build_instructions(
        self,
        winston_patterns: WinstonPatterns,
        subjective_patterns: SubjectivePatterns,
        structural_patterns: StructuralPatterns,
        component_type: str,
        strictness_level: int,
        previous_ai_tendencies: List[str]
    ) -> str:
        """
        Combine patterns into dynamic humanness instructions.
        
        Loads template from prompts/system/humanness_layer.txt and injects:
        - Winston conversational markers and number patterns
        - Subjective theatrical phrases and AI tendencies
        - Structural diversity patterns (openings to avoid, successful structures)
        - Success patterns (professional verbs, tone markers)
        - Strictness-appropriate guidance
        - Previous attempt feedback
        - RANDOMIZED SELECTIONS: length target, structure approach, voice style
        
        Args:
            winston_patterns: Patterns from Winston passing samples
            subjective_patterns: Patterns from subjective learning
            component_type: Type of component being generated
            strictness_level: 1-5 (controls emphasis)
            previous_ai_tendencies: AI patterns from last failed attempt
        
        Returns:
            Formatted humanness instructions with randomization
        """
        # Load template (fail-fast if missing - already validated in __init__)
        template = self.template_file.read_text(encoding='utf-8')
        
        # 🎲 RANDOMIZE LENGTH TARGET (from config - zero hardcoded values)
        # Use subtitle_length for material_description, default to 'length' for others
        length_config_key = 'subtitle_length' if component_type == 'material_description' else 'length'
        if length_config_key in self.config['randomization_targets']:
            length_config = self.config['randomization_targets'][length_config_key]
        else:
            # Fallback to 'length' if component-specific config not found
            length_config = self.config['randomization_targets']['length']
        
        length_options = []
        length_labels = {}
        for key, value in length_config.items():
            length_options.append(key)
            range_str = f"{value['range'][0]}-{value['range'][1]} words"
            length_labels[key] = f"{range_str} ({value['description']})"
        
        selected_length_key = random.choice(length_options)
        selected_length = length_labels[selected_length_key]
        
        # 🎲 RANDOMIZE STRUCTURAL APPROACH (from config)
        structure_config = self.config['randomization_targets']['structures']
        structure_options = []
        for idx, (key, value) in enumerate(structure_config.items(), 1):
            prob_pct = int(value['probability'] * 100)
            structure_options.append(
                f"{idx}. {value['label']} ({prob_pct}% chance): {value['description']}"
            )
        selected_structure = random.choice(structure_options)
        
        # 🎲 RANDOMIZE VOICE STYLE (from config)
        voice_config = self.config['randomization_targets']['voices']
        voice_options = []
        for key, value in voice_config.items():
            examples = ', '.join(f'"{ex}"' for ex in value['examples'])
            voice_options.append(
                f"{value['label']}: {examples} ({value['description']})"
            )
        selected_voice = random.choice(voice_options)
        
        # 🎲 RANDOMIZE SENTENCE RHYTHM (from config)
        rhythm_config = self.config['randomization_targets']['rhythms']
        rhythm_options = []
        for key, value in rhythm_config.items():
            rhythm_options.append(f"{value['label']}: {value['description']}")
        selected_rhythm = random.choice(rhythm_options)
        
        # 🎲 RANDOMIZE PROPERTY INTEGRATION STRATEGY (from config)
        property_config = self.config['randomization_targets']['property_strategies']
        property_options = []
        for key, value in property_config.items():
            property_options.append(f"{value['label']}: {value['description']}")
        selected_property_strategy = random.choice(property_options)
        
        # 🎲 RANDOMIZE WARNING PLACEMENT (from config)
        warning_config = self.config['randomization_targets']['warning_placements']
        warning_options = []
        for key, value in warning_config.items():
            warning_options.append(f"{value['label']}: {value['description']}")
        selected_warning = random.choice(warning_options)
        
        # Log randomization selections for terminal visibility
        print("\n🎲 RANDOMIZATION APPLIED:")
        print(f"   • Length Target: {selected_length_key.upper()} ({selected_length})")
        print(f"   • Structure: {selected_structure}")
        print(f"   • Voice Style: {selected_voice}")
        print(f"   • Sentence Rhythm: {selected_rhythm}")
        print(f"   • Property Strategy: {selected_property_strategy}")
        print(f"   • Warning Placement: {selected_warning}")
        
        # Format Winston success patterns
        winston_section = self._format_winston_patterns(winston_patterns)
        
        # Format subjective avoidance patterns
        subjective_section = self._format_subjective_patterns(subjective_patterns)
        
        # Format theatrical phrases
        theatrical_section = self._format_theatrical_phrases(subjective_patterns.theatrical_phrases)
        
        # Format conversational markers
        conversational_section = self._format_conversational_markers(winston_patterns.conversational_markers)
        
        # Format structural diversity patterns
        structural_section = self._format_structural_patterns(structural_patterns)
        overused_section = self._format_overused_patterns(structural_patterns.overused_openings)
        diverse_structures_section = self._format_diverse_structures(structural_patterns.diverse_structures)
        
        # Get strictness guidance
        strictness_guidance = self._get_strictness_guidance(strictness_level)
        
        # Format previous attempt feedback
        feedback_section = self._format_previous_feedback(previous_ai_tendencies, strictness_level)
        
        # Inject all data into template (including randomization)
        instructions = template.format(
            attempt_number=strictness_level,
            component_type=component_type,
            passing_sample_count=winston_patterns.sample_count,
            total_evaluations=self._get_total_evaluations(),
            winston_success_patterns=winston_section,
            subjective_ai_tendencies=subjective_section,
            theatrical_phrases_list=theatrical_section,
            conversational_markers=conversational_section,
            structural_sample_count=structural_patterns.sample_count,
            successful_structural_patterns=structural_section,
            overused_opening_patterns=overused_section,
            diverse_linguistic_patterns=diverse_structures_section,
            strictness_level=strictness_level,
            strictness_guidance=strictness_guidance,
            previous_attempt_feedback=feedback_section
        )
        
        # Append randomization selections to instructions (template placeholder approach)
        randomization_addendum = f"""

🎲 **YOUR RANDOMIZED TARGETS FOR THIS GENERATION** 🎲
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📏 **LENGTH TARGET**: {selected_length}

🏗️ **STRUCTURAL APPROACH** (pick THIS one from 5 options):
   {selected_structure}

🗣️ **VOICE STYLE** (use THIS persona):
   {selected_voice}

🎵 **SENTENCE RHYTHM**:
   {selected_rhythm}

🔢 **PROPERTY INTEGRATION**:
   {selected_property_strategy}

⚠️ **WARNING PLACEMENT**:
   {selected_warning}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 CRITICAL: These randomization targets are MANDATORY - use them to ensure 
dramatic variation between generations. No two outputs should be similar!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        return instructions + randomization_addendum
    
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
    
    def _format_structural_patterns(self, patterns: StructuralPatterns) -> str:
        """Format successful structural patterns for prompt injection"""
        if patterns.sample_count == 0:
            return "No structural patterns logged yet - focus on natural variation."
        
        lines = []
        lines.append(f"📊 Analyzed {patterns.sample_count} generations (avg diversity: {patterns.average_diversity:.1f}/10)")
        
        if patterns.successful_openings:
            lines.append("\n✅ HIGH-SCORING OPENING PATTERNS (prefer unused ones):")
            for i, opening in enumerate(patterns.successful_openings, 1):
                # Priority 3: Mark if recently overused
                cooldown_marker = " ⚠️ COOLDOWN (recently overused)" if opening in patterns.overused_openings else ""
                lines.append(f"   {i}. {opening}{cooldown_marker}")
        
        if patterns.linguistic_diversity:
            diverse_markers = ', '.join(patterns.linguistic_diversity[:8])
            lines.append(f"\n✅ Diverse linguistic patterns: {diverse_markers}")
        
        return '\n'.join(lines)
    
    def _format_overused_patterns(self, overused: List[str]) -> str:
        """Format overused opening patterns to avoid"""
        if not overused:
            return "(No pattern repetition detected yet)"
        
        lines = ["⚠️ RECENT PATTERNS TO AVOID (already used multiple times):"]
        for pattern in overused:
            lines.append(f"   • {pattern}")
        
        return '\n'.join(lines)
    
    def _format_diverse_structures(self, structures: List[str]) -> str:
        """Format diverse structure types"""
        if not structures:
            return "Vary your structure: problem-focused, contrast-based, process-focused, experience-based, property-driven"
        
        structure_list = ', '.join(structures)
        return f"✅ Successful structure types: {structure_list}"
    
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
        component_type: Type of component (caption, material_description, etc.)
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
