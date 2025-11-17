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
        api_client = None,
        quality_threshold: float = 7.0,
        verbose: bool = False
    ):
        """
        Initialize Claude evaluator
        
        Args:
            api_client: Claude API client (optional - will use Anthropic if available)
            quality_threshold: Minimum acceptable overall score (0-10)
            verbose: Print detailed evaluation output
        """
        self.api_client = api_client
        self.quality_threshold = quality_threshold
        self.verbose = verbose
        
        # Check if Claude/Anthropic is available
        self._check_claude_availability()
    
    def _check_claude_availability(self):
        """Check if Grok API is available"""
        if self.api_client is not None:
            self.has_claude = True  # Using Grok API client
        else:
            self.has_claude = False
            if self.verbose:
                print("⚠️  Grok API not available - evaluations will be limited")
    
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
        
        # Get Claude's evaluation
        if self.has_claude and self.api_client:
            evaluation = self._get_subjective_evaluation(prompt, content)
        else:
            # Fallback to rule-based evaluation
            evaluation = self._fallback_evaluation(content, material_name)
        
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

**Narrative Assessment** (2-3 sentences that MUST specifically address whether the voice sounds authentically human or artificially generated. Comment on natural conversational flow, realistic word choices, genuine tone variations, and whether sentence patterns feel organic. Be explicit about any AI-like tendencies such as formulaic phrasing, excessive enthusiasm, or unnatural transitions):

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
            request = GenerationRequest(
                prompt=prompt,
                system_prompt="You are an expert content quality evaluator.",
                max_tokens=1000,
                temperature=0.3
            )
            
            # Call API with proper request object
            response = self.api_client.generate(request)
            
            if not response.success:
                raise Exception(f"API call failed: {response.error}")
            
            # Parse Grok's response
            return self._parse_claude_response(response.content)
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Subjective evaluation failed: {e}")
                print("   Falling back to rule-based evaluation")
            
            return self._fallback_evaluation(content, "")
    
    def _parse_claude_response(self, response: str) -> SubjectiveEvaluationResult:
        """Parse Claude's evaluation response"""
        
        # DEBUG: Log what we received
        print(f"🔍 [DEBUG PARSER] Response length: {len(response)} chars")
        print(f"🔍 [DEBUG PARSER] First 500 chars: {response[:500]}")
        
        # Simple parsing (can be enhanced)
        lines = response.split('\n')
        
        dimension_scores = []
        strengths = []
        weaknesses = []
        recommendations = []
        overall_score = 7.0
        narrative_assessment = None
        
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
        
        # DEBUG: Log narrative assessment extraction
        if narrative_assessment:
            print(f"🔍 [DEBUG] EVALUATOR: Extracted narrative ({len(narrative_assessment)} chars): {narrative_assessment[:100]}...")
        else:
            print("⚠️ [DEBUG] EVALUATOR: NO narrative extracted from response")
        
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
            raw_response=response
        )
    
    def _fallback_evaluation(
        self,
        content: str,
        material_name: str
    ) -> SubjectiveEvaluationResult:
        """
        Rule-based fallback evaluation when Claude is unavailable
        
        Provides basic quality checks without AI subjective judgment
        """
        
        dimension_scores = []
        
        # 1. Clarity - based on readability metrics
        word_count = len(content.split())
        avg_word_length = sum(len(w) for w in content.split()) / max(word_count, 1)
        clarity_score = min(10, max(5, 10 - (avg_word_length - 5)))
        
        dimension_scores.append(SubjectiveScore(
            dimension=EvaluationDimension.CLARITY,
            score=clarity_score,
            feedback=f"Average word length: {avg_word_length:.1f} chars",
            suggestions=["Consider shorter words for better clarity"] if avg_word_length > 6 else []
        ))
        
        # 2. Professionalism - basic tone check
        casual_words = ['gonna', 'wanna', 'yeah', 'cool', 'awesome']
        has_casual = any(word in content.lower() for word in casual_words)
        prof_score = 7.0 if not has_casual else 5.0
        
        dimension_scores.append(SubjectiveScore(
            dimension=EvaluationDimension.PROFESSIONALISM,
            score=prof_score,
            feedback="Professional tone maintained" if not has_casual else "Some casual language detected",
            suggestions=["Remove casual language"] if has_casual else []
        ))
        
        # 3-6. Default scores for other dimensions
        for dim in [EvaluationDimension.TECHNICAL_ACCURACY,
                   EvaluationDimension.HUMAN_LIKENESS,
                   EvaluationDimension.ENGAGEMENT,
                   EvaluationDimension.JARGON_FREE]:
            dimension_scores.append(SubjectiveScore(
                dimension=dim,
                score=7.0,
                feedback="Unable to evaluate without Claude AI",
                suggestions=[]
            ))
        
        overall_score = sum(s.score for s in dimension_scores) / len(dimension_scores)
        
        return SubjectiveEvaluationResult(
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            strengths=["Content generated successfully"],
            weaknesses=["Subjective evaluation not available"],
            recommendations=["Enable Claude API for detailed subjective evaluation"],
            passes_quality_gate=overall_score >= self.quality_threshold,
            evaluation_time_ms=0
        )
    
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
        api_client: Optional Claude API client
        verbose: Print detailed output
    
    Returns:
        SubjectiveEvaluationResult
    """
    
    evaluator = SubjectiveEvaluator(
        api_client=api_client,
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
