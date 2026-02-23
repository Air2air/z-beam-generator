"""
Universal Humanness Layer - Dual-Feedback Pattern Optimizer

CRITICAL ARCHITECTURE RULE (Dec 6, 2025):
- Author voice is NEVER randomized per generation
- Voice is determined by author assignment (happens ONCE, persists forever)
- This class provides STRUCTURAL variation ONLY (rhythm, opening, structure)
- Voice characteristics come from shared/voice/profiles/*.yaml

Integrates learned patterns from TWO feedback systems:
1. Winston AI Detection (quantitative) - conversational markers from passing samples
2. Subjective Evaluation (qualitative) - AI tendencies and theatrical phrases to avoid

Generates dynamic humanness instructions that improve with each retry attempt (1-5 strictness levels).

Created: November 20, 2025
Updated: December 6, 2025 - Removed voice randomization (author-controlled only)
Policy Compliance: Zero hardcoded values, template-only approach, fail-fast architecture
"""

import re
import random
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from shared.text.utils.prompt_registry_service import PromptRegistryService


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
    - Subjective learned patterns (YAML: prompts/quality/learned_patterns.yaml)
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
            patterns_file: Path to learned_patterns.yaml (default: prompts/quality/learned_patterns.yaml)
            structural_db_path: Path to structural patterns database (default: data/winston_feedback.db)
            config_path: Path to config.yaml for randomization targets (default: generation/config.yaml)
        
        Raises:
            FileNotFoundError: If required files missing (fail-fast)
            ValueError: If config.yaml missing randomization_targets section
        """
        self.winston_db_path = winston_db_path
        self.structural_db_path = structural_db_path or 'data/winston_feedback.db'
        self._current_variation = None  # Store randomized variation for access
        
        if patterns_file is None:
            self.patterns_file = Path('prompts/quality/learned_patterns.yaml')
        else:
            self.patterns_file = patterns_file
        
        # Validate required templates in consolidated prompt catalog (fail-fast)
        PromptRegistryService.get_humanness_template(compact=False)
        PromptRegistryService.get_humanness_template(compact=True)
        
        # Components using compact humanness layer (structural variation ONLY, no voice)
        # Compact template follows separation of concerns: voice from personas, structure from humanness
        # Micro prompts are ~5500 chars with compact template, would exceed limit with full
        # Settings_description also needs compact to avoid exceeding limits
        # Description field needs compact to prevent prompt bloat (full version causes 12k+ char prompts)
        # Contaminant descriptions need compact to prevent voice override issues
        # Compound_description also needs compact (9,600 char prompts exceed 8,000 limit)
        # All compound fields need compact (added Dec 24, 2025 - base prompts + full humanness exceed 8k limit)
        self.compact_components = {
            'micro', 
            'settings_description', 
            'component_summaries', 
            'description',
            'pageDescription',
            'frontmatter_description',  # Frontmatter-specific descriptions
            # Compound component types (all need compact to stay under 8k limit)
            'health_effects',
            'exposure_guidelines',
            'detection_methods',
            'first_aid',
            'ppe_requirements',
            'regulatory_standards',
            'emergency_response',
            'chemical_properties',
            'environmental_impact',
            'detection_monitoring'
        }
        
        # Load configuration for randomization targets (fail-fast)
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}. "
                f"Cannot operate without randomization_targets config."
            )
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # Load centralized text length randomization config (single source of truth)
        self.text_field_config_path = Path('generation/text_field_config.yaml')
        if not self.text_field_config_path.exists():
            raise FileNotFoundError(
                f"Text field config not found: {self.text_field_config_path}. "
                "Cannot resolve randomization_range without centralized config."
            )
        with open(self.text_field_config_path, 'r', encoding='utf-8') as f:
            self.text_field_config = yaml.safe_load(f)
        if not isinstance(self.text_field_config, dict):
            raise ValueError("generation/text_field_config.yaml must contain a YAML dictionary")
        
        # Merge domain-specific configs (randomization_targets moved to domain configs)
        # Load materials domain config for structures, property_strategies, length, etc.
        materials_config_path = Path('domains/materials/config.yaml')
        if materials_config_path.exists():
            with open(materials_config_path, 'r', encoding='utf-8') as f:
                materials_config = yaml.safe_load(f)
            
            # Merge randomization_targets from materials config
            if 'randomization_targets' in materials_config:
                if self.config.get('randomization_targets') is None:
                    self.config['randomization_targets'] = {}
                self.config['randomization_targets'].update(materials_config['randomization_targets'])
        
        # Load settings domain config for voices, rhythms, etc.
        settings_config_path = Path('domains/settings/config.yaml')
        if settings_config_path.exists():
            with open(settings_config_path, 'r', encoding='utf-8') as f:
                settings_config = yaml.safe_load(f)
            
            # Merge randomization_targets from settings config
            if 'randomization_targets' in settings_config:
                if self.config.get('randomization_targets') is None:
                    self.config['randomization_targets'] = {}
                self.config['randomization_targets'].update(settings_config['randomization_targets'])
        
        if not self.config.get('randomization_targets'):
            raise ValueError(
                f"Missing 'randomization_targets' in {self.config_path} and domain configs. "
                f"Zero hardcoded values policy requires config-driven randomization."
            )
        
        # Lazy-load dependencies
        self._winston_db = None
        self._pattern_learner = None
        
        logger.info(f"✅ HumannessOptimizer initialized (Winston DB: {winston_db_path}, Config: {config_path})")

    def _get_randomization_factors(self) -> tuple[float, float]:
        """Get centralized length randomization factors from text_field_config.yaml."""
        randomization_cfg = self.text_field_config.get('randomization_range')
        if not isinstance(randomization_cfg, dict):
            raise ValueError(
                "Missing required config block: randomization_range in generation/text_field_config.yaml"
            )

        min_factor = randomization_cfg.get('min_factor')
        max_factor = randomization_cfg.get('max_factor')
        if not isinstance(min_factor, (int, float)) or not isinstance(max_factor, (int, float)):
            raise TypeError("randomization_range.min_factor and max_factor must be numeric")
        if min_factor <= 0 or max_factor <= 0 or min_factor > max_factor:
            raise ValueError(
                f"Invalid randomization_range: min_factor={min_factor}, max_factor={max_factor}"
            )

        return float(min_factor), float(max_factor)
    
    def generate_humanness_instructions(
        self,
        component_type: str,
        length_target: int = None
    ) -> str:
        """
        Generate dynamic humanness instructions from learned patterns.
        
        Uses learned patterns from database (Winston samples, subjective evaluation,
        structural diversity). Learning system optimizes parameters BETWEEN generations,
        not during retries.
        
        Provides STRUCTURAL VARIATION ONLY (opening patterns, rhythm, diversity).
        Voice and tone come from author persona (injected separately in domain prompt).
        
        Args:
            component_type: Type of component (micro, subtitle, description, etc.)
            length_target: Base word count target from generation config (e.g., 50)
        
        Returns:
            Formatted humanness instructions ready for prompt injection
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"🧠 GENERATING HUMANNESS INSTRUCTIONS")
        logger.info(f"{'='*70}")
        logger.info(f"   Component: {component_type}")
        
        # 1. Extract Winston patterns from passing samples
        winston_patterns = self._extract_winston_patterns()
        logger.info(f"   ✅ Winston patterns: {winston_patterns.sample_count} passing samples analyzed")
        
        # 2. Load subjective learned patterns
        subjective_patterns = self._extract_subjective_patterns()
        logger.info(f"   ✅ Subjective patterns: {len(subjective_patterns.ai_tendencies)} AI tendencies tracked")
        
        # 3. Extract structural diversity patterns
        structural_patterns = self._extract_structural_patterns(component_type)
        logger.info(f"   ✅ Structural patterns: {structural_patterns.sample_count} samples, avg diversity {structural_patterns.average_diversity:.1f}/10")
        
        # 4. Extract validation feedback (NEW - Dec 12, 2025)
        validation_feedback = self._extract_validation_feedback(domain=None)  # Global feedback
        if validation_feedback['total_feedback_count'] > 0:
            logger.info(f"   ✅ Validation feedback: {validation_feedback['total_feedback_count']} recent issues analyzed")
            if validation_feedback['errors']:
                top_error = validation_feedback['errors'][0]
                logger.info(f"      🔴 Most common error: \"{top_error['message']}\" ({top_error['count']} occurrences)")
            if validation_feedback['warnings']:
                top_warning = validation_feedback['warnings'][0]
                logger.info(f"      ⚠️  Most common warning: \"{top_warning['message']}\" ({top_warning['count']} occurrences)")
        
        # 5. Build instructions from learned patterns
        instructions = self._build_instructions(
            winston_patterns=winston_patterns,
            subjective_patterns=subjective_patterns,
            structural_patterns=structural_patterns,
            validation_feedback=validation_feedback,
            component_type=component_type,
            length_target=length_target
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

        required_keys = [
            'sample_count',
            'best_score',
            'average_score',
            'conversational_markers',
            'number_patterns',
            'sample_excerpts',
        ]
        missing = [key for key in required_keys if key not in patterns_dict]
        if missing:
            raise KeyError(
                f"Winston passing patterns missing required keys: {', '.join(missing)}"
            )
        
        return WinstonPatterns(
            sample_count=patterns_dict['sample_count'],
            best_score=patterns_dict['best_score'],
            average_score=patterns_dict['average_score'],
            conversational_markers=patterns_dict['conversational_markers'],
            number_patterns=patterns_dict['number_patterns'],
            sample_excerpts=patterns_dict['sample_excerpts']
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

        required_avoidance_keys = ['theatrical_phrases', 'ai_tendencies', 'penalty_weights']
        missing_avoidance_keys = [key for key in required_avoidance_keys if key not in avoidance]
        if missing_avoidance_keys:
            raise KeyError(
                f"Subjective avoidance patterns missing required keys: {', '.join(missing_avoidance_keys)}"
            )
        
        return SubjectivePatterns(
            theatrical_phrases=avoidance['theatrical_phrases'],
            ai_tendencies=avoidance['ai_tendencies'],
            success_patterns=success,
            penalty_weights=avoidance['penalty_weights']
        )
    
    def _extract_validation_feedback(self, domain: str = None) -> Dict[str, Any]:
        """
        Extract common validation issues from prompt_validation_feedback table.
        
        Analyzes recent validation feedback to identify:
        - Most common errors (ERROR, CRITICAL)
        - Recurring warnings (WARNING)
        - Issue frequency trends
        
        This data helps optimizer avoid generating prompts that trigger known issues.
        
        Args:
            domain: Optional domain filter (contaminants, materials, settings)
        
        Returns:
            Dict with issue frequencies, top problems, and avoidance guidance
        """
        import sqlite3
        import json
        from datetime import datetime, timedelta
        
        try:
            conn = sqlite3.connect(self.winston_db_path)
            cursor = conn.cursor()
            
            # Get recent validation feedback (last 7 days)
            lookback = (datetime.now() - timedelta(days=7)).isoformat()
            
            # Query for issue frequencies
            query = """
                SELECT 
                    json_extract(value, '$.severity') as severity,
                    json_extract(value, '$.message') as message,
                    COUNT(*) as occurrences
                FROM prompt_validation_feedback, json_each(issues)
                WHERE timestamp > ?
            """
            params = [lookback]
            
            if domain:
                query += " AND domain = ?"
                params.append(domain)
            
            query += """
                GROUP BY severity, message
                ORDER BY occurrences DESC
                LIMIT 20
            """
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Categorize by severity
            critical_issues = []
            error_issues = []
            warning_issues = []
            
            for severity, message, count in rows:
                issue = {'message': message, 'count': count}
                if severity == 'CRITICAL':
                    critical_issues.append(issue)
                elif severity == 'ERROR':
                    error_issues.append(issue)
                elif severity == 'WARNING':
                    warning_issues.append(issue)
            
            conn.close()
            
            return {
                'critical': critical_issues[:5],  # Top 5 critical
                'errors': error_issues[:10],      # Top 10 errors
                'warnings': warning_issues[:10],  # Top 10 warnings
                'total_feedback_count': len(rows)
            }
            
        except Exception as e:
            logger.warning(f"Could not extract validation feedback: {e}")
            return {
                'critical': [],
                'errors': [],
                'warnings': [],
                'total_feedback_count': 0
            }
    
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
        validation_feedback: Dict[str, Any],
        component_type: str,
        length_target: int = None
    ) -> str:
        """
        Combine patterns into dynamic humanness instructions.
        
        Provides STRUCTURAL VARIATION ONLY (opening patterns, rhythm, diversity).
        Voice and tone come from author persona (injected separately in domain prompt).
        
        NEW (Dec 12, 2025): Integrates validation feedback to avoid generating
        prompts that trigger known issues.
        
        Loads template from prompts/system/humanness_layer.txt and injects:
        - Winston conversational markers and number patterns
        - Subjective theatrical phrases and AI tendencies
        - Structural diversity patterns (openings to avoid, successful structures)
        - Validation feedback (common errors/warnings to prevent)
        - Success patterns (professional verbs, tone markers)
        - RANDOMIZED SELECTIONS: length target, structure approach
        
        Uses COMPACT template for short-form content (micro, subtitle) to stay
        within prompt length limits. Full template for descriptions/FAQ.
        
        Args:
            winston_patterns: Patterns from Winston passing samples
            subjective_patterns: Patterns from subjective learning
            structural_patterns: Structural diversity patterns
            validation_feedback: Common validation issues to avoid
            component_type: Type of component being generated
        
        Returns:
            Formatted humanness instructions with randomization
        """
        # Select template: compact for micro (8000 char API limit), full for others
        use_compact = component_type in self.compact_components
        
        if use_compact:
            template = PromptRegistryService.get_humanness_template(compact=True)
            logger.info(f"📝 Using COMPACT humanness template for {component_type}")
        else:
            template = PromptRegistryService.get_humanness_template(compact=False)
            logger.info(f"📝 Using humanness template for {component_type}")
        
        # 🎲 RANDOMIZE WORD COUNT TARGET (multiplier-only)
        # NOTE: This generates instruction guidance for humanness layer only.
        # PromptBuilder remains responsible for final prompt-level target injection.
        min_factor, max_factor = self._get_randomization_factors()
        randomized_multiplier = random.uniform(min_factor, max_factor)

        if length_target:
            selected_length_value = max(1, int(length_target * randomized_multiplier))
            selected_length_key = "RANDOMIZED"
            selected_length = selected_length_value
        else:
            variation_pct = int(abs(randomized_multiplier - 1.0) * 100)
            selected_length_key = "RANDOMIZED"
            selected_length = f"x{randomized_multiplier:.2f} multiplier (≈±{variation_pct}% from base)"

        # pageDescription uses sentence-count constraints from schema prompt.
        # Avoid introducing extra word-count targets in humanness layer.
        if component_type == 'pageDescription':
            selected_length_key = "SENTENCE_BASED"
            selected_length = "single focused paragraph (no explicit word target)"
        
        # Store normalized variation magnitude for reporting/legacy access
        self._current_variation = abs(randomized_multiplier - 1.0)
        
        # 🎲 RANDOMIZE STRUCTURAL APPROACH (from config)
        structure_config = self.config['randomization_targets']['structures']
        structure_options = []
        for idx, (key, value) in enumerate(structure_config.items(), 1):
            prob_pct = int(value['probability'] * 100)
            structure_options.append(
                f"{value['label']} ({prob_pct}% chance): {value['description']}"
            )
        selected_structure = random.choice(structure_options)
        
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
        if component_type == 'pageDescription':
            selected_property_strategy = "Practical Clarity: Explain behavior and operator implications in plain prose"
        
        # 🎲 RANDOMIZE WARNING PLACEMENT (from config)
        warning_config = self.config['randomization_targets']['warning_placements']
        warning_options = []
        for key, value in warning_config.items():
            warning_options.append(f"{value['label']}: {value['description']}")
        selected_warning = random.choice(warning_options)
        
        # 🎲 RANDOMIZE OPENING STYLE (from config - if available)
        selected_opening = None
        if 'opening_styles' in self.config['randomization_targets']:
            opening_config = self.config['randomization_targets']['opening_styles']
            opening_options = []
            for key, value in opening_config.items():
                opening_options.append(f"{value['label']}: {value['description']}")
            selected_opening = random.choice(opening_options)
        
        # Log randomization selections for terminal visibility
        print("\n🎲 RANDOMIZATION APPLIED:")
        print(f"   • Length Target: {selected_length_key.upper()} ({selected_length})")
        print(f"   • Structure: {selected_structure}")
        print(f"   • Sentence Rhythm: {selected_rhythm}")
        print(f"   • Property Strategy: {selected_property_strategy}")
        print(f"   • Warning Placement: {selected_warning}")
        if selected_opening:
            print(f"   • Opening Style: {selected_opening}")
        
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
        
        # Handle compact vs full template differently
        if use_compact:
            # Compact template uses simpler placeholders (NO voice - structural only)
            instructions = template.format(
                selected_length=selected_length,
                selected_structure=selected_structure,
                selected_rhythm=selected_rhythm
            )
            # Log size for visibility
            logger.info(f"✅ Generated {len(instructions)} character COMPACT instruction block")
            print(f"   ✅ Generated {len(instructions)} character COMPACT instruction block")
            return instructions
        
        # Full template with all placeholders
        instructions = template.format(
            component_type=component_type,
            selected_length=selected_length,
            selected_structure=selected_structure,
            selected_rhythm=selected_rhythm,
            selected_property_strategy=selected_property_strategy,
            selected_warning=selected_warning,
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
            structural_diversity_patterns=structural_section
        )
        
        # Append randomization selections to instructions (template placeholder approach)
        length_guideline_line = f"📏 **LENGTH GUIDELINE**: ~{selected_length} words (approximate target)"
        length_guideline_note = "    Note: This is a guideline, not a strict requirement\n    Write naturally until the content is complete"
        if component_type == 'pageDescription':
            length_guideline_line = f"📏 **LENGTH GUIDELINE**: {selected_length}"
            length_guideline_note = "    Follow sentence-count guidance only; keep full, natural sentences"

        randomization_addendum = f"""

🎲 **YOUR RANDOMIZED TARGETS FOR THIS GENERATION** 🎲
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{length_guideline_line}
{length_guideline_note}

🏗️ **STRUCTURAL APPROACH**: {selected_structure}

🎵 **SENTENCE RHYTHM**: {selected_rhythm}

🔧 **PROPERTY STRATEGY**: {selected_property_strategy}

⚠️ **WARNING PLACEMENT**: {selected_warning}
"""
        # Add opening style if available
        if selected_opening:
            randomization_addendum += f"""
🎬 **OPENING STYLE**: {selected_opening}
"""
        
        # Add validation feedback guidance if available (NEW - Dec 12, 2025)
        if validation_feedback['total_feedback_count'] > 0:
            randomization_addendum += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ **VALIDATION LEARNING - AVOID THESE COMMON ISSUES** ⚠️
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            # Add top errors
            if validation_feedback['errors']:
                randomization_addendum += "\n🔴 **TOP ERRORS TO PREVENT**:\n"
                for error in validation_feedback['errors'][:3]:  # Top 3 errors
                    randomization_addendum += f"   • {error['message']} ({error['count']} recent occurrences)\n"
            
            # Add top warnings
            if validation_feedback['warnings']:
                randomization_addendum += "\n⚠️ **TOP WARNINGS TO AVOID**:\n"
                for warning in validation_feedback['warnings'][:3]:  # Top 3 warnings
                    randomization_addendum += f"   • {warning['message']} ({warning['count']} recent occurrences)\n"
            
            randomization_addendum += """
💡 These issues were detected in recent generations. Structure your response
to avoid triggering them. The system auto-fixes these but prevention is better!

"""
        
        randomization_addendum += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ **FOLLOW THESE EXACTLY** - They define your unique approach for THIS generation.
Each generation gets different random selections to maximize diversity.

🚨 CRITICAL: These randomization targets are MANDATORY - use them to ensure 
dramatic variation between generations. No two outputs should be similar!

NOTE: Voice style comes from assigned author persona (specified in VOICE INSTRUCTIONS).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        logger.info(f"✅ Generated {len(instructions + randomization_addendum)} character instruction block")
        print(f"   ✅ Generated {len(instructions + randomization_addendum)} character instruction block")
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
        
        if level not in guidance_map:
            raise ValueError(f"Invalid strictness level: {level}. Expected one of {sorted(guidance_map.keys())}")
        return guidance_map[level]
    
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
        if 'total_evaluations' not in patterns:
            raise KeyError("Current patterns missing required key: total_evaluations")
        return patterns['total_evaluations']
    
    def get_current_variation(self) -> float:
        """
        Get the randomized word count variation for current generation.
        
        Returns:
            Current variation magnitude (0.0-1.0), derived from randomization multiplier.
        """
        if self._current_variation is not None:
            return self._current_variation
        min_factor, max_factor = self._get_randomization_factors()
        midpoint_multiplier = (min_factor + max_factor) / 2.0
        return abs(midpoint_multiplier - 1.0)


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
        component_type: Type of component (micro, description, etc.)
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
