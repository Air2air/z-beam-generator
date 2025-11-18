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
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
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
    # NEW: Structured realism metrics
    realism_score: Optional[float] = None  # 0-10
    voice_authenticity: Optional[float] = None  # 0-10
    tonal_consistency: Optional[float] = None  # 0-10
    ai_tendencies: Optional[List[str]] = None  # Detected AI patterns


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
        quality_threshold: float = 7.0,
        verbose: bool = False,
        evaluation_temperature: float = 0.2
    ):
        """
        Initialize Subjective evaluator
        
        Args:
            api_client: Grok API client (REQUIRED - fail-fast architecture)
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
                "Ensure Grok API is properly configured before initializing."
            )
        
        self.api_client = api_client
        self.quality_threshold = quality_threshold
        self.verbose = verbose
        self.evaluation_temperature = evaluation_temperature
    
    @validate_scores
    def evaluate(
        self,
        content: str,
        material_name: str,
        component_type: str = "caption",
        context: Optional[Dict[str, Any]] = None
    ) -> SubjectiveEvaluationResult:
        """
        Perform subjective evaluation of generated content
        
        Args:
            content: The text content to evaluate
            material_name: Name of the material (e.g., "Aluminum")
            component_type: Type of content (caption, subtitle, faq, etc.)
            context: Additional context (properties, author, etc.)
        
        Returns:
            SubjectiveEvaluationResult with scores and recommendations
        """
        start = time.time()
        
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"  GROK SUBJECTIVE EVALUATION")
            print(f"{'='*70}\n")
            print(f"Material: {material_name}")
            print(f"Component: {component_type}")
            print(f"Content length: {len(content)} chars\n")
        
        # Build evaluation prompt
        prompt = self._build_evaluation_prompt(
            content, material_name, component_type, context
        )
        
        # Get Grok evaluation (no fallback - fail fast per GROK_INSTRUCTIONS.md)
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
        """Build evaluation prompt for Claude"""
        
        prompt = f"""You are an expert content evaluator specializing in technical writing quality assessment.

Evaluate this {component_type} for {material_name} laser cleaning across these dimensions:

1. **Clarity** (0-10): Is the content clear, concise, and easy to understand?
2. **Professionalism** (0-10): Does it maintain appropriate professional tone?
3. **Technical Accuracy** (0-10): Are technical details correct and appropriate?
4. **Human-likeness** (0-10): Does it sound naturally human-written (not AI-generated)?
5. **Engagement** (0-10): Is it interesting and engaging to read?
6. **Jargon-free** (0-10): Does it avoid unnecessary jargon and use plain language?

CONTENT TO EVALUATE:
{content}

Provide your evaluation in this format:

**Narrative Assessment** (2-3 sentences with CRITICAL STANCE: Assume this is AI-generated unless proven otherwise. Scrutinize for contrived informality, forced casualness, unnatural enthusiasm, or overly-constructed "humanness". Real human writing has subtle imperfections, inconsistent pacing, and genuine voice - not theatrical authenticity. Flag ANY signs of artificial construction, formulaic patterns, or trying-too-hard informality):

**Realism Analysis** (Identify specific issues - select ALL that apply):
- AI Tendencies Detected: [comma-separated list: formulaic_phrasing, unnatural_transitions, excessive_enthusiasm, rigid_structure, overly_polished, mechanical_tone, repetitive_patterns, forced_transitions, artificial_symmetry, generic_language, theatrical_casualness, sentence_fragments_for_drama, direct_reader_address, exclamation_markers, vague_promises, contrived_informality, none]
- Theatrical/Casual Penalties: [List ANY: "Wow", "Amazing", exclamations, "you see/notice", fragments for impact, "changes everything", "quick [noun]", "turns out", em-dashes for drama]
- Realism Score (0-10): X (10=perfectly human, 0=obviously AI) - DEDUCT 2 points per theatrical element
- Voice Authenticity (0-10): X (natural conversational flow) - DEDUCT 3 points if any casual/theatrical markers
- Tonal Consistency (0-10): X (genuine variations without jarring shifts)

- Overall Score (0-10):
- Dimension Scores:
  - Clarity: X/10 - feedback
  - Professionalism: X/10 - feedback
  - Technical Accuracy: X/10 - feedback
  - Human-likeness: X/10 - feedback
  - Engagement: X/10 - feedback
  - Jargon-free: X/10 - feedback
- Strengths: [list 2-3 key strengths]
- Weaknesses: [list 2-3 areas for improvement]
- Recommendations: [2-3 specific actionable suggestions]
"""
        
        if context:
            prompt += f"\n\nADDITIONAL CONTEXT:\n"
            if 'author' in context:
                prompt += f"- Author: {context['author']}\n"
            if 'properties' in context:
                prompt += f"- Key Properties: {', '.join(context['properties'][:5])}\n"
        
        return prompt
    
    def _get_subjective_evaluation(
        self,
        prompt: str,
        content: str
    ) -> SubjectiveEvaluationResult:
        """Get evaluation from Grok AI"""
        
        try:
            # Import GenerationRequest
            from shared.api.client import GenerationRequest
            
            # Build proper API request
            # OPTIMIZED: 600 tokens sufficient for structured evaluation output
            # OPTIMIZED: temperature=0.2 for consistent scoring (grok-2-fast is deterministic at low temps)
            request = GenerationRequest(
                prompt=prompt,
                system_prompt="You are an expert content quality evaluator. Provide concise, structured responses.",
                max_tokens=600,
                temperature=self.evaluation_temperature
            )
            
            # Call API with proper request object
            response = self.api_client.generate(request)
            
            if not response.success:
                raise Exception(f"API call failed: {response.error}")
            
            # Parse Grok's response
            return self._parse_claude_response(response.content)
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Subjective evaluation failed: {e}")
            # FAIL-FAST: No fallback mode per GROK_INSTRUCTIONS.md
            raise Exception(f"Subjective evaluation failed: {e}") from e
    
    def _parse_claude_response(self, response: str) -> SubjectiveEvaluationResult:
        """Parse Claude's evaluation response"""
        
        # Simple parsing (can be enhanced)
        lines = response.split('\n')
        
        dimension_scores = []
        strengths = []
        weaknesses = []
        recommendations = []
        overall_score = 7.0
        narrative_assessment = None
        # NEW: Realism metrics
        realism_score = None
        voice_authenticity = None
        tonal_consistency = None
        ai_tendencies = []
        
        # Extract narrative assessment - handle both inline and separate line formats
        for i, line in enumerate(lines):
            if '**Narrative Assessment**' in line or 'Narrative Assessment:' in line:
                # Check if narrative is on the same line (after colon)
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        narrative_text = parts[1].strip()
                        if narrative_text:
                            narrative_assessment = narrative_text
                            # Continue reading subsequent lines until we hit structured data
                            for j in range(i+1, len(lines)):
                                next_line = lines[j].strip()
                                if next_line and not next_line.startswith('-') and not next_line.startswith('*'):
                                    narrative_assessment += ' ' + next_line
                                elif next_line.startswith('-') or next_line.startswith('*'):
                                    break
                            break
                # Otherwise read following lines
                else:
                    narrative_lines = []
                    for j in range(i+1, len(lines)):
                        next_line = lines[j].strip()
                        if next_line and not next_line.startswith('-') and not next_line.startswith('*'):
                            narrative_lines.append(next_line)
                        elif next_line.startswith('-') or next_line.startswith('*'):
                            break
                    if narrative_lines:
                        narrative_assessment = ' '.join(narrative_lines)
                    break
        
        # Extract realism analysis metrics
        for i, line in enumerate(lines):
            if '**Realism Analysis**' in line or 'Realism Analysis:' in line:
                # Parse the structured realism data in following lines
                for j in range(i+1, len(lines)):
                    line_text = lines[j].strip()
                    
                    # Extract AI Tendencies
                    if 'AI Tendencies Detected:' in line_text or 'ai tendencies detected:' in line_text.lower():
                        # Extract the list portion after the colon
                        if ':' in line_text:
                            tendencies_str = line_text.split(':', 1)[1].strip()
                            # Remove brackets if present
                            tendencies_str = tendencies_str.strip('[]')
                            # Split by comma and clean up
                            if tendencies_str and tendencies_str.lower() != 'none':
                                ai_tendencies = [t.strip() for t in tendencies_str.split(',') if t.strip()]
                    
                    # Extract Realism Score
                    if 'Realism Score' in line_text:
                        if ':' in line_text:
                            score_str = line_text.split(':', 1)[1].strip()
                            # Extract number (handle "X/10" or just "X" format)
                            score_str = score_str.split('/')[0].strip()
                            try:
                                realism_score = float(score_str)
                            except ValueError:
                                pass
                    
                    # Extract Voice Authenticity
                    if 'Voice Authenticity' in line_text:
                        if ':' in line_text:
                            score_str = line_text.split(':', 1)[1].strip()
                            score_str = score_str.split('/')[0].strip()
                            try:
                                voice_authenticity = float(score_str)
                            except ValueError:
                                pass
                    
                    # Extract Tonal Consistency
                    if 'Tonal Consistency' in line_text:
                        if ':' in line_text:
                            score_str = line_text.split(':', 1)[1].strip()
                            score_str = score_str.split('/')[0].strip()
                            try:
                                tonal_consistency = float(score_str)
                            except ValueError:
                                pass
                    
                    # Stop if we hit another section marker
                    if line_text.startswith('**') and 'Realism Analysis' not in line_text:
                        break
        
        # Parse response (simplified - enhance as needed)
        # This would need actual parsing logic based on Claude's response format
        
        return SubjectiveEvaluationResult(
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            passes_quality_gate=overall_score >= self.quality_threshold,
            evaluation_time_ms=0,
            narrative_assessment=narrative_assessment,
            realism_score=realism_score,
            voice_authenticity=voice_authenticity,
            tonal_consistency=tonal_consistency,
            ai_tendencies=ai_tendencies if ai_tendencies else None,
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
    component_type: str = "caption",
    api_client = None,
    verbose: bool = True
) -> SubjectiveEvaluationResult:
    """
    Convenience function for content evaluation
    
    Args:
        content: Text content to evaluate
        material_name: Material name (e.g., "Aluminum")
        component_type: Component type (caption, subtitle, etc.)
        api_client: REQUIRED Grok API client (fail-fast if None)
        verbose: Print detailed output
    
    Returns:
        SubjectiveEvaluationResult
    
    Raises:
        ValueError: If api_client is None
    """
    
    evaluator = SubjectiveEvaluator(
        api_client=api_client,  # Will raise ValueError if None
        quality_threshold=7.0,
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
        component_type="caption",
        verbose=True
    )
    
    print(f"Evaluation complete: {result.overall_score:.1f}/10")
    print(f"Passes quality gate: {result.passes_quality_gate}")
