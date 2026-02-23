"""
Subjective Content Evaluation Module

Provides final quality assessment of generated content using AI subjective evaluation.
Runs AFTER all other processing is complete to provide human-like quality judgment.

IMPLEMENTATION: Currently uses Claude API for subjective evaluation.
FUTURE ROADMAP: Multi-provider consensus scoring (Claude + GPT-4 + Gemini).

Author: System
Created: November 15, 2025
Updated: November 15, 2025 (renamed from claude_evaluator to subjective_evaluator)
"""

import time
from pathlib import Path
import yaml
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from generation.config.config_loader import ProcessingConfig
from shared.text.utils.prompt_registry_service import PromptRegistryService
from shared.validation.score_validator import validate_scores, ScoreValidationError


class EvaluationDimension(Enum):
    """Dimensions for subjective evaluation"""
    CLARITY = "clarity"
    PROFESSIONALISM = "professionalism"
    TECHNICAL_ACCURACY = "technical_accuracy"
    HUMAN_LIKENESS = "human_likeness"
    ENGAGEMENT = "engagement"
    JARGON_FREE = "jargon_free"


@dataclass
class SubjectiveScore:
    """Individual dimension score"""
    dimension: EvaluationDimension
    score: float  # 0-10
    feedback: str
    suggestions: List[str]


@dataclass
class SubjectiveEvaluationResult:
    """Complete evaluation result from Claude"""
    overall_score: float  # 0-10
    dimension_scores: List[SubjectiveScore]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    passes_quality_gate: bool
    evaluation_time_ms: float
    narrative_assessment: Optional[str] = None  # Paragraph-form evaluation
    raw_response: Optional[str] = None
    # Structured realism metrics (6 comprehensive dimensions)
    realism_score: Optional[float] = None  # Overall Realism 0-10
    voice_authenticity: Optional[float] = None  # Voice Authenticity 0-10
    tonal_consistency: Optional[float] = None  # Tonal Consistency 0-10
    technical_accessibility: Optional[float] = None  # Technical Accessibility 0-10 (NEW)
    natural_imperfection: Optional[float] = None  # Natural Imperfection 0-10 (NEW)
    conversational_flow: Optional[float] = None  # Conversational Flow 0-10 (NEW)
    ai_tendencies: Optional[List[str]] = None  # Detected AI patterns
    technical_jargon_issues: Optional[List[str]] = None  # Technical jargon problems (NEW)
    formulaic_structures: Optional[List[str]] = None  # Formulaic patterns (NEW)


class SubjectiveEvaluator:
    """
    Final-stage subjective evaluation using Claude AI
    
    Evaluates content across 6 dimensions:
    1. Clarity - Is the content clear and understandable?
    2. Professionalism - Does it maintain professional tone?
    3. Technical Accuracy - Are technical details correct?
    4. Human-likeness - Does it sound naturally human-written?
    5. Engagement - Is it engaging and interesting?
    6. Jargon-free - Does it avoid unnecessary jargon?
    """
    
    def __init__(
        self,
        api_client,
        quality_threshold: Optional[float] = None,
        verbose: bool = False,
        evaluation_temperature: Optional[float] = None
    ):
        """
        Initialize Subjective evaluator
        
        Args:
            api_client: Claude API client (REQUIRED - fail-fast architecture)
            quality_threshold: Minimum acceptable overall score (0-10)
            verbose: Print detailed evaluation output
            evaluation_temperature: Temperature for subjective evaluation API calls (default 0.2 for consistency)
        
        Raises:
            ValueError: If api_client is None (fail-fast, no fallbacks)
        """
        # FAIL-FAST: No fallback mode allowed per GROK_INSTRUCTIONS.md
        if api_client is None:
            raise ValueError(
                "SubjectiveEvaluator requires api_client. "
                "Cannot operate in fallback mode per fail-fast architecture. "
                "Ensure Claude API is properly configured before initializing."
            )
        
        config = ProcessingConfig()

        self.api_client = api_client
        self.quality_threshold = quality_threshold if quality_threshold is not None else float(
            config.get_required_config('constants.subjective_evaluator.quality_threshold')
        )
        self.verbose = verbose
        self.evaluation_temperature = (
            evaluation_temperature
            if evaluation_temperature is not None
            else float(config.get_required_config('constants.subjective_evaluator.evaluation_temperature'))
        )
        self.request_max_tokens = int(config.get_required_config('constants.subjective_evaluator.request_max_tokens'))
        
        # Validate evaluation template in consolidated prompt catalog (fail-fast)
        PromptRegistryService.get_quality_evaluation_prompt()

        # Learned patterns file path
        self.patterns_file = Path('prompts/quality/learned_patterns.yaml')
        self._pattern_learner = None
        self._cached_patterns: Optional[Dict[str, Any]] = None
        self._cached_patterns_mtime: Optional[float] = None
    
    @validate_scores
    def evaluate(
        self,
        content: str,
        material_name: str,
        component_type: str = "micro",
        context: Optional[Dict[str, Any]] = None
    ) -> SubjectiveEvaluationResult:
        """
        Perform subjective evaluation of generated content
        
        Args:
            content: The text content to evaluate
            material_name: Name of the material (e.g., "Aluminum")
            component_type: Type of content (caption, faq, etc.)
            context: Additional context (properties, author, etc.)
        
        Returns:
            SubjectiveEvaluationResult with scores and recommendations
        """
        start = time.time()
        
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"  CLAUDE SUBJECTIVE EVALUATION")
            print(f"{'='*70}\n")
            print(f"Material: {material_name}")
            print(f"Component: {component_type}")
            print(f"Content length: {len(content)} chars\n")
        
        # Build evaluation prompt
        prompt = self._build_evaluation_prompt(
            content, material_name, component_type, context
        )
        
        # Get Claude evaluation (no fallback - fail fast per GROK_INSTRUCTIONS.md)
        evaluation = self._get_subjective_evaluation(prompt, content)
        
        evaluation.evaluation_time_ms = (time.time() - start) * 1000
        
        if self.verbose:
            self._print_evaluation(evaluation)
        
        return evaluation
    
    def _build_evaluation_prompt(
        self,
        content: str,
        material_name: str,
        component_type: str,
        context: Optional[Dict]
    ) -> str:
        """Build evaluation prompt using template and learned patterns"""
        
        # Load template and patterns
        template = self._load_template()
        patterns = self._load_learned_patterns()
        
        # Format theatrical phrases for prompt
        high_penalty_phrases = ', '.join(patterns['theatrical_phrases']['high_penalty'][:10])
        medium_penalty_phrases = ', '.join(patterns['theatrical_phrases'].get('medium_penalty', [])[:10])
        theatrical_phrases_text = f"HIGH PENALTY: {high_penalty_phrases}\nMEDIUM PENALTY: {medium_penalty_phrases}"
        
        # Format AI tendencies for prompt
        ai_tendencies_list = list(patterns['ai_tendencies']['common'].keys())
        ai_tendencies_text = ', '.join(ai_tendencies_list)
        
        # Get realism threshold
        realism_threshold = patterns['scoring_adjustments'].get('realism_threshold', 7.0)
        
        # Format template with learned patterns
        prompt = template.format(
            component_type=component_type,
            material_name=material_name,
            content=content,
            theatrical_phrases=theatrical_phrases_text,
            ai_tendencies=ai_tendencies_text,
            realism_threshold=realism_threshold
        )
        
        # Add context if provided
        if context:
            prompt += "\n\nADDITIONAL CONTEXT:\n"
            if 'author' in context:
                prompt += f"- Author: {context['author']}\n"
            if 'properties' in context:
                prompt += f"- Key Properties: {', '.join(context['properties'][:5])}\n"
        
        return prompt
    
    def _load_template(self) -> str:
        """Load evaluation prompt template from file"""
        try:
            return PromptRegistryService.get_quality_evaluation_prompt()
        except Exception as e:
            raise Exception(f"Failed to load evaluation template: {e}") from e
    
    def _load_learned_patterns(self) -> Dict:
        """Load learned patterns from YAML file"""
        try:
            if not self.patterns_file.exists():
                # Create default patterns file if missing
                from learning.subjective_pattern_learner import SubjectivePatternLearner
                learner = SubjectivePatternLearner(self.patterns_file)
                # Will create default file

            patterns_mtime = (
                self.patterns_file.stat().st_mtime
                if self.patterns_file.exists()
                else None
            )

            if (
                self._cached_patterns is not None
                and patterns_mtime == self._cached_patterns_mtime
            ):
                return self._cached_patterns

            with open(self.patterns_file, 'r', encoding='utf-8') as f:
                patterns = yaml.safe_load(f)

            if isinstance(patterns, dict):
                self._cached_patterns = patterns
                self._cached_patterns_mtime = patterns_mtime

            return patterns
        except Exception as e:
            # Fallback to minimal patterns if file can't be loaded
            return {
                'theatrical_phrases': {'high_penalty': ['zaps away', 'And yeah', 'Wow']},
                'ai_tendencies': {'common': {'formulaic_phrasing': 0}},
                'scoring_adjustments': {'realism_threshold': 7.0}
            }
    
    def _get_pattern_learner(self):
        """Lazy load pattern learner"""
        if self._pattern_learner is None:
            from learning.subjective_pattern_learner import SubjectivePatternLearner
            self._pattern_learner = SubjectivePatternLearner(self.patterns_file)
        return self._pattern_learner
    
    def _get_subjective_evaluation(
        self,
        prompt: str,
        content: str
    ) -> SubjectiveEvaluationResult:
        """Get evaluation from Claude AI"""
        
        try:
            # Import GenerationRequest
            from shared.api.client import GenerationRequest
            
            # Build proper API request
            # OPTIMIZED: 600 tokens sufficient for structured evaluation output
            # OPTIMIZED: temperature=0.2 for consistent scoring (Claude is deterministic at low temps)
            # POLICY: No hardcoded system prompts - critical tone comes from template file
            request = GenerationRequest(
                prompt=prompt,
                system_prompt=None,  # Let template's first line set the critical evaluator tone
                max_tokens=self.request_max_tokens,
                temperature=self.evaluation_temperature
            )
            
            # Call API with proper request object
            response = self.api_client.generate(request)
            
            if not response.success:
                raise Exception(f"API call failed: {response.error}")
            
            # Parse Claude's response
            return self._parse_claude_response(response.content)
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Subjective evaluation failed: {e}")
            # FAIL-FAST: No fallback mode per GROK_INSTRUCTIONS.md
            raise Exception(f"Subjective evaluation failed: {e}") from e
    
    def _parse_claude_response(self, response: str) -> SubjectiveEvaluationResult:
        """
        Parse Claude's six-dimension comprehensive human realism evaluation response
        
        Expected format (November 22, 2025 - Six Comprehensive Dimensions):
        **Overall Realism (0-10)**: X
        **Voice Authenticity (0-10)**: X
        **Tonal Consistency (0-10)**: X
        **Technical Accessibility (0-10)**: X
        **Natural Imperfection (0-10)**: X
        **Conversational Flow (0-10)**: X
        **Reasoning** (briefly cover all dimensions):
        **Technical Jargon Issues**: [list specific examples or "none"]
        **AI Patterns Found**: [list or "none"]
        **Theatrical Phrases Found**: [quotes or "none"]
        **Formulaic Structures**: [describe or "none"]
        **Pass/Fail**: [PASS/FAIL]
        """
        
        lines = response.split('\n')
        
        # Initialize variables for six-dimension format
        overall_realism = None
        voice_authenticity = None
        tonal_consistency = None
        technical_accessibility = None
        natural_imperfection = None
        conversational_flow = None
        narrative_assessment = None
        ai_tendencies = []
        theatrical_phrases = []
        technical_jargon_issues = []
        formulaic_structures = []
        pass_fail = None
        
        # Parse response
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Extract Overall Realism (primary gate score)
            if '**Overall Realism' in line or 'Overall Realism' in line:
                if ':' in line:
                    score_str = line.split(':', 1)[1].strip()
                    score_str = score_str.split('/')[0].strip()
                    try:
                        overall_realism = float(score_str)
                    except ValueError:
                        pass
            
            # Extract Voice Authenticity
            elif '**Voice Authenticity' in line or 'Voice Authenticity' in line:
                if ':' in line:
                    score_str = line.split(':', 1)[1].strip()
                    score_str = score_str.split('/')[0].strip()
                    try:
                        voice_authenticity = float(score_str)
                    except ValueError:
                        pass
            
            # Extract Tonal Consistency
            elif '**Tonal Consistency' in line or 'Tonal Consistency' in line:
                if ':' in line:
                    score_str = line.split(':', 1)[1].strip()
                    score_str = score_str.split('/')[0].strip()
                    try:
                        tonal_consistency = float(score_str)
                    except ValueError:
                        pass
            
            # Extract Technical Accessibility (NEW)
            elif '**Technical Accessibility' in line or 'Technical Accessibility' in line:
                if ':' in line:
                    score_str = line.split(':', 1)[1].strip()
                    score_str = score_str.split('/')[0].strip()
                    try:
                        technical_accessibility = float(score_str)
                    except ValueError:
                        pass
            
            # Extract Natural Imperfection (NEW)
            elif '**Natural Imperfection' in line or 'Natural Imperfection' in line:
                if ':' in line:
                    score_str = line.split(':', 1)[1].strip()
                    score_str = score_str.split('/')[0].strip()
                    try:
                        natural_imperfection = float(score_str)
                    except ValueError:
                        pass
            
            # Extract Conversational Flow (NEW)
            elif '**Conversational Flow' in line or 'Conversational Flow' in line:
                if ':' in line:
                    score_str = line.split(':', 1)[1].strip()
                    score_str = score_str.split('/')[0].strip()
                    try:
                        conversational_flow = float(score_str)
                    except ValueError:
                        pass
            
            # Extract narrative explanation ("Reasoning")
            elif '**Reasoning**' in line or 'Reasoning' in line:
                # Read following lines until next ** marker
                narrative_lines = []
                for j in range(i+1, len(lines)):
                    next_line = lines[j].strip()
                    if next_line and not next_line.startswith('**'):
                        narrative_lines.append(next_line)
                    elif next_line.startswith('**'):
                        break
                if narrative_lines:
                    narrative_assessment = ' '.join(narrative_lines)
            
            # Extract Technical Jargon Issues (NEW)
            elif '**Technical Jargon Issues**' in line or 'Technical Jargon Issues' in line:
                if ':' in line:
                    jargon_str = line.split(':', 1)[1].strip()
                    jargon_str = jargon_str.strip('[]')
                    if jargon_str and jargon_str.lower() not in ('none', 'n/a', ''):
                        technical_jargon_issues = [j.strip() for j in jargon_str.split(',') if j.strip()]
            
            # Extract AI Tendencies
            elif '**AI Patterns Found**' in line or 'AI Patterns Found' in line:
                if ':' in line:
                    tendencies_str = line.split(':', 1)[1].strip()
                    tendencies_str = tendencies_str.strip('[]')
                    if tendencies_str and tendencies_str.lower() not in ('none', 'n/a', ''):
                        ai_tendencies = [t.strip() for t in tendencies_str.split(',') if t.strip()]
            
            # Extract Theatrical Phrases
            elif '**Theatrical Phrases Found**' in line or 'Theatrical Phrases Found' in line:
                if ':' in line:
                    phrases_str = line.split(':', 1)[1].strip()
                    phrases_str = phrases_str.strip('[]')
                    if phrases_str and phrases_str.lower() not in ('none', 'n/a', ''):
                        theatrical_phrases = [p.strip().strip('"\'') for p in phrases_str.split(',') if p.strip()]
            
            # Extract Formulaic Structures (NEW)
            elif '**Formulaic Structures**' in line or 'Formulaic Structures' in line:
                if ':' in line:
                    formulaic_str = line.split(':', 1)[1].strip()
                    formulaic_str = formulaic_str.strip('[]')
                    if formulaic_str and formulaic_str.lower() not in ('none', 'n/a', ''):
                        formulaic_structures = [f.strip() for f in formulaic_str.split(',') if f.strip()]
            
            # Extract Pass/Fail status
            elif '**Pass/Fail**' in line or 'Pass/Fail' in line:
                if ':' in line:
                    pass_fail = line.split(':', 1)[1].strip().upper()
            
            i += 1
        
        # Use overall_realism as overall_score (primary gate score)
        overall_score = overall_realism if overall_realism is not None else 7.0
        
        # Determine pass/fail if not explicitly stated
        if pass_fail is None:
            passes = overall_score >= self.quality_threshold
        else:
            passes = 'PASS' in pass_fail
        
        # Return result with six comprehensive dimensions
        return SubjectiveEvaluationResult(
            overall_score=overall_score,
            dimension_scores=[],  # Legacy field - no longer populated
            strengths=[],  # Simplified format uses narrative instead
            weaknesses=[],  # Simplified format uses detection lists
            recommendations=[],  # Simplified format focuses on pass/fail
            passes_quality_gate=passes,
            evaluation_time_ms=0,
            narrative_assessment=narrative_assessment,
            realism_score=overall_realism,  # Primary gate score
            voice_authenticity=voice_authenticity,
            tonal_consistency=tonal_consistency,
            technical_accessibility=technical_accessibility,  # NEW
            natural_imperfection=natural_imperfection,  # NEW
            conversational_flow=conversational_flow,  # NEW
            ai_tendencies=ai_tendencies if ai_tendencies else None,
            technical_jargon_issues=technical_jargon_issues if technical_jargon_issues else None,  # NEW
            formulaic_structures=formulaic_structures if formulaic_structures else None,  # NEW
            raw_response=response
        )
    
    # REMOVED: _fallback_evaluation() method
    # REASON: Violates GROK_INSTRUCTIONS.md no-mocks/fallbacks policy
    # REPLACEMENT: Fail-fast in __init__ if api_client is None
    
    def _print_evaluation(self, evaluation: SubjectiveEvaluationResult):
        """Print formatted evaluation results"""
        
        print(f"{'─'*70}")
        print(f"EVALUATION RESULTS")
        print(f"{'─'*70}\n")
        
        print(f"Overall Score: {evaluation.overall_score:.1f}/10")
        print(f"Quality Gate: {'✅ PASS' if evaluation.passes_quality_gate else '❌ FAIL'}\n")
        
        print("Dimension Scores:")
        for score in evaluation.dimension_scores:
            status = "✅" if score.score >= self.quality_threshold else "⚠️"
            print(f"  {status} {score.dimension.value.replace('_', ' ').title()}: {score.score:.1f}/10")
            print(f"     {score.feedback}")
            if score.suggestions:
                for suggestion in score.suggestions:
                    print(f"     → {suggestion}")
        
        print(f"\n{'─'*70}")
        
        if evaluation.strengths:
            print("\n✅ Strengths:")
            for strength in evaluation.strengths:
                print(f"  • {strength}")
        
        if evaluation.weaknesses:
            print("\n⚠️  Areas for Improvement:")
            for weakness in evaluation.weaknesses:
                print(f"  • {weakness}")
        
        if evaluation.recommendations:
            print("\n💡 Recommendations:")
            for rec in evaluation.recommendations:
                print(f"  • {rec}")
        
        print(f"\n{'='*70}\n")


def evaluate_content(
    content: str,
    material_name: str,
    component_type: str = "micro",
    api_client = None,
    verbose: bool = True
) -> SubjectiveEvaluationResult:
    """
    Convenience function for content evaluation
    
    Args:
        content: Text content to evaluate
        material_name: Material name (e.g., "Aluminum")
        component_type: Component type (caption, faq, etc.)
        api_client: REQUIRED Claude API client (fail-fast if None)
        verbose: Print detailed output
    
    Returns:
        SubjectiveEvaluationResult
    
    Raises:
        ValueError: If api_client is None
    """
    
    evaluator = SubjectiveEvaluator(
        api_client=api_client,  # Will raise ValueError if None
        quality_threshold=float(ProcessingConfig().get_required_config('constants.subjective_evaluator.quality_threshold')),
        verbose=verbose
    )
    
    return evaluator.evaluate(content, material_name, component_type)


# Example usage
if __name__ == "__main__":
    # Example evaluation
    test_content = """
    Aluminum oxide coatings accumulate rapidly on aluminum surfaces exposed to 
    industrial environments, forming a persistent layer that affects thermal 
    conductivity. Laser cleaning removes these layers through selective ablation, 
    targeting the oxide while preserving the base metal integrity.
    """
    
    result = evaluate_content(
        content=test_content,
        material_name="Aluminum",
        component_type="micro",
        verbose=True
    )
    
    print(f"Evaluation complete: {result.overall_score:.1f}/10")
    print(f"Passes quality gate: {result.passes_quality_gate}")
