"""
AI Detection Prompt Optimizer

Handles DeepSeek prompt generation and response parsing for AI detection
configuration optimization based on Winston AI analysis results.
"""

import json
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class PromptOptimizer:
    """Handles prompt generation and response parsing for DeepSeek optimization."""

    def __init__(self, optimization_flags: List[str]):
        self.optimization_flags = optimization_flags

    def generate_optimization_prompt(
        self, winston_result: Dict[str, Any], content: str, config: Dict[str, Any]
    ) -> str:
        """Generate the prompt for DeepSeek to optimize the configuration using comprehensive Winston AI data."""

        # Extract comprehensive metrics from Winston result
        overall_score = winston_result.get("overall_score", 0)
        confidence = winston_result.get("confidence", 0)
        classification = winston_result.get("classification", "unclear")

        # Extract detailed analysis from Winston response
        details = winston_result.get("analysis", {})  # Changed from 'details' to 'analysis'
        readability_score = details.get("readability_score")
        attack_detected = details.get("attack_detected", {})

        # Extract sentence-level analysis if available
        sentences_data = details.get("sentences", [])
        sentence_analysis = self._analyze_sentence_patterns(sentences_data)

        # Current flag states
        current_flags = {
            flag: config.get(flag, False) for flag in self.optimization_flags
        }

        # Build comprehensive analysis summary
        analysis_summary = self._build_analysis_summary(
            overall_score,
            confidence,
            classification,
            readability_score,
            attack_detected,
            sentence_analysis,
            content,
        )

        prompt = f"""You are an expert AI content optimization specialist with deep knowledge of linguistic patterns, cognitive authenticity markers, and advanced rhetorical techniques. Analyze Winston AI detection results and provide targeted, multi-layered enhancements for achieving high detection scores.

{analysis_summary}

CONTENT ANALYSIS:
- Overall Score: {overall_score:.1f}/100 ({classification})
- Readability: {readability_score if readability_score is not None else 'N/A'}
- Low-Scoring Sentences: {sentence_analysis.get('low_score_percentage', 0):.1f}%

SCORE-BASED ENHANCEMENT STRATEGY:

1. **CRITICAL SCORES (< 40)**: Aggressive multi-layered approach
   - Apply 3-4 enhancements simultaneously
   - Focus on: natural_language_patterns, syntactic_complexity_variation, cognitive_dissonance_indicators, mid_thought_interruptions
   - Target: Core manipulation detection + cognitive authenticity

2. **MODERATE SCORES (40-60)**: Authenticity enhancement
   - Apply 2-3 enhancements per iteration
   - Focus on: cultural_adaptation, personal_reflection_indicators, uncertainty_expressions, discourse_marker_diversity
   - Target: Human-like imperfections and cultural markers

3. **GOOD SCORES (60-80)**: Refinement and sophistication
   - Apply 1-2 enhancements per iteration
   - Focus on: rhetorical_question_patterns, metaphorical_language_usage, paragraph_rhythm_variation, pragmatic_context_markers
   - Target: Advanced rhetorical devices and structural variation

4. **EXCELLENT SCORES (80+)**: Fine-tuning
   - Apply 1 enhancement per iteration
   - Focus on: epistemic_markers, politeness_strategies, expertise_level_markers
   - Target: Subtle authenticity markers

GRADUAL APPLICATION PRINCIPLES:
- Start with foundational enhancements, then layer advanced techniques
- Combine linguistic + cognitive + structural approaches for maximum impact
- Use learning history to identify most effective enhancement combinations
- Prioritize enhancements that address specific detection patterns

CURRENT FLAGS: {json.dumps(current_flags, indent=2)}

Return ONLY JSON with targeted enhancements for this score range:
{{
  "natural_language_patterns": true/false,
  "sentence_variability": true/false,
  "paragraph_structure": true/false,
  "cultural_adaptation": true/false,
  "lexical_diversity": true/false,
  "emotional_depth": true/false,
  "conversational_style": true/false,
  "syntactic_complexity_variation": true/false,
  "discourse_marker_diversity": true/false,
  "pragmatic_context_markers": true/false,
  "information_structure_variation": true/false,
  "register_shifting": true/false,
  "hedging_and_qualification": true/false,
  "epistemic_markers": true/false,
  "mid_thought_interruptions": true/false,
  "cognitive_dissonance_indicators": true/false,
  "uncertainty_expressions": true/false,
  "subjective_evaluation_markers": true/false,
  "personal_reflection_indicators": true/false,
  "contextual_memory_references": true/false,
  "paragraph_rhythm_variation": true/false,
  "thematic_progression_markers": true/false,
  "coherence_breaking_devices": true/false,
  "narrative_digression_patterns": true/false,
  "perspective_shifting": true/false,
  "temporal_reference_diversity": true/false,
  "domain_specific_jargon_variation": true/false,
  "cultural_reference_integration": true/false,
  "situational_context_markers": true/false,
  "professional_experience_indicators": true/false,
  "expertise_level_markers": true/false,
  "metaphorical_language_usage": true/false,
  "rhetorical_question_patterns": true/false,
  "contrastive_construction_usage": true/false,
  "emphasis_and_intensification": true/false,
  "politeness_strategies": true/false,
  "persuasive_language_markers": true/false,
  "reasoning": "Specific analysis: which enhancements to enable/disable and why, focusing on score-based strategy and multi-layered approach"
}}

Focus on GRADUAL improvements that combine multiple enhancement types for breakthrough score improvements."""

        return prompt

    def _analyze_sentence_patterns(self, sentences_data: list) -> Dict[str, Any]:
        """Analyze sentence-level patterns from Winston AI response."""
        if not sentences_data:
            return {"available": False}

        try:
            scores = [s.get("score", 0) for s in sentences_data if isinstance(s, dict)]
            texts = [s.get("text", "") for s in sentences_data if isinstance(s, dict)]

            # Filter out None scores
            valid_scores = [score for score in scores if score is not None]
            valid_texts = [
                text for score, text in zip(scores, texts) if score is not None
            ]

            if not valid_scores:
                return {"available": False}

            scores = valid_scores
            texts = valid_texts

            # Calculate sentence-level statistics
            avg_sentence_score = sum(scores) / len(scores)
            score_variance = sum((s - avg_sentence_score) ** 2 for s in scores) / len(scores)

            # Analyze sentence length patterns
            sentence_lengths = [len(text.split()) for text in texts if text]
            avg_length = (
                sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
            )

            # Identify problematic sentences (very low scores)
            low_score_sentences = [i for i, score in enumerate(scores) if score < 20]

            return {
                "available": True,
                "sentence_count": len(sentences_data),
                "avg_sentence_score": avg_sentence_score,
                "score_variance": score_variance,
                "avg_sentence_length": avg_length,
                "low_score_count": len(low_score_sentences),
                "low_score_percentage": (len(low_score_sentences) / len(scores)) * 100,
            }

        except Exception as e:
            logger.warning(f"Failed to analyze sentence patterns: {e}")
            return {"available": False}

    def _build_analysis_summary(
        self,
        overall_score: float,
        confidence: float,
        classification: str,
        readability_score: float,
        attack_detected: Dict[str, Any],
        sentence_analysis: Dict[str, Any],
        content: str,
    ) -> str:
        """Build comprehensive analysis summary for prompt context."""
        
        # Content characteristics analysis
        content_chars = self._analyze_content_characteristics(content)
        
        analysis_parts = [
            f"- Overall Score: {overall_score:.1f}/100 ({classification})",
            f"- Confidence: {confidence:.1f}%",
            f"- Classification: {classification.upper()}"
        ]
        
        if readability_score is not None:
            analysis_parts.append(f"- Readability Score: {readability_score:.1f}")
        
        # Add attack detection information if available
        if attack_detected:
            attack_status = "DETECTED" if attack_detected.get("detected", False) else "NOT DETECTED"
            analysis_parts.append(f"- Attack Detection: {attack_status}")
            
            if attack_detected.get("confidence"):
                analysis_parts.append(f"- Attack Confidence: {attack_detected['confidence']:.1f}%")
        
        # Add sentence analysis if available
        if sentence_analysis.get("available"):
            analysis_parts.extend([
                f"- Sentence Count: {sentence_analysis['sentence_count']}",
                f"- Average Sentence Score: {sentence_analysis['avg_sentence_score']:.1f}",
                f"- Low-scoring Sentences: {sentence_analysis['low_score_count']} ({sentence_analysis['low_score_percentage']:.1f}%)",
                f"- Average Sentence Length: {sentence_analysis['avg_sentence_length']:.1f} words"
            ])
        
        # Add content characteristics
        analysis_parts.extend([
            f"- Writing Style: {content_chars['style']}",
            f"- Complexity Level: {content_chars['complexity']}",
            f"- Tone: {content_chars['tone']}"
        ])
        
        return "WINSTON AI ANALYSIS:\n" + "\n".join(analysis_parts)

    def _analyze_content_characteristics(self, content: str) -> Dict[str, str]:
        """Analyze content characteristics for optimization context."""
        if not content:
            return {"style": "unknown", "complexity": "unknown", "tone": "unknown"}
        
        # Simple heuristic analysis
        sentences = content.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        # Determine style based on patterns
        style = "academic" if any(word in content.lower() for word in ["however", "furthermore", "therefore", "consequently"]) else "conversational"
        
        # Determine complexity
        if avg_sentence_length > 20:
            complexity = "high"
        elif avg_sentence_length > 15:
            complexity = "medium"
        else:
            complexity = "low"
        
        # Determine tone (basic analysis)
        tone = "formal" if style == "academic" else "informal"
        
        return {
            "style": style,
            "complexity": complexity,
            "tone": tone
        }

    def parse_optimization_response(
        self, response: Any, current_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse DeepSeek's optimization response and merge with current configuration."""
        try:
            # Extract response content
            if hasattr(response, "content"):
                response_text = response.content
            else:
                response_text = str(response)

            logger.info(f"DeepSeek optimization response: {response_text[:500]}...")

            # Try to extract JSON from the response
            response_clean = response_text.strip()

            # Handle common response formats
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]

            # Find JSON in the response
            json_start = response_clean.find("{")
            json_end = response_clean.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_text = response_clean[json_start:json_end]
                optimization_data = json.loads(json_text)

                # Merge with current configuration
                optimized_config = current_config.copy()

                # Apply optimization recommendations
                for flag in self.optimization_flags:
                    if flag in optimization_data:
                        optimized_config[flag] = optimization_data[flag]

                # Add reasoning if provided
                if "reasoning" in optimization_data:
                    optimized_config["_optimization_reasoning"] = optimization_data["reasoning"]

                logger.info(f"Successfully parsed optimization response with {len(optimization_data)} flags")
                return optimized_config
            else:
                logger.warning("No valid JSON found in DeepSeek response")
                return current_config

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse DeepSeek response as JSON: {e}")
            logger.error(f"Response content: {response_text}")
            return current_config
        except Exception as e:
            logger.error(f"Unexpected error parsing optimization response: {e}")
            return current_config
