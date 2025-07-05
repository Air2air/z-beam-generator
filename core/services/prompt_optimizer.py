"""
Prompt optimization service for AI detection prompts.
Tracks performance, analyzes patterns, and generates optimized prompts.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from generator.modules.logger import get_logger

logger = get_logger("prompt_optimizer")


class PromptOptimizer:
    """Service for optimizing detection prompts based on performance data."""

    def __init__(self, storage_path: str = None):
        """Initialize with optional custom storage path."""
        self.storage_path = storage_path or "generator/cache/prompt_performance.json"
        self.performance_data = self._load_performance_data()
        self.prompt_templates_dir = Path("generator/prompts/detection")

    def _load_performance_data(self) -> Dict:
        """Load existing performance data from storage."""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    logger.info(f"Loaded performance data for {len(data)} prompts")
                    return data
        except Exception as e:
            logger.warning(f"Failed to load performance data: {e}")

        return {}

    def _save_performance_data(self) -> None:
        """Save performance data to persistent storage."""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, "w") as f:
                json.dump(self.performance_data, f, indent=2)
            logger.debug("Performance data saved successfully")
        except Exception as e:
            logger.error(f"Failed to save performance data: {e}")

    def track_performance(
        self,
        prompt_name: str,
        detection_type: str,
        score: int,
        iteration: int,
        success: bool,
        section_name: str = None,
        context: Dict = None,
    ) -> None:
        """
        Track prompt performance with enhanced context.

        Args:
            prompt_name: Name of the prompt used
            detection_type: 'ai' or 'human'
            score: Detection score returned (0-100)
            iteration: Iteration number
            success: Whether the score met the threshold
            section_name: Section being processed
            context: Additional context data
        """
        key = f"{prompt_name}_{detection_type}"

        if key not in self.performance_data:
            self.performance_data[key] = {
                "prompt_name": prompt_name,
                "detection_type": detection_type,
                "uses": 0,
                "total_score": 0,
                "successes": 0,
                "avg_score": 0,
                "success_rate": 0,
                "scores": [],
                "iterations": [],
                "sections": [],
                "last_used": None,
                "created": datetime.now().isoformat(),
            }

        perf = self.performance_data[key]
        perf["uses"] += 1
        perf["total_score"] += score
        perf["successes"] += 1 if success else 0
        perf["avg_score"] = perf["total_score"] / perf["uses"]
        perf["success_rate"] = perf["successes"] / perf["uses"]
        perf["scores"].append(score)
        perf["iterations"].append(iteration)
        perf["sections"].append(section_name or "unknown")
        perf["last_used"] = datetime.now().isoformat()

        # Keep only recent scores for trend analysis (last 20)
        if len(perf["scores"]) > 20:
            perf["scores"] = perf["scores"][-20:]
            perf["iterations"] = perf["iterations"][-20:]
            perf["sections"] = perf["sections"][-20:]

        self._save_performance_data()
        logger.debug(f"Performance tracked: {key} - Score: {score}, Success: {success}")

    def get_optimal_prompt(
        self,
        detection_type: str,
        iteration: int = 1,
        section_name: str = None,
        available_prompts: List[str] = None,
    ) -> str:
        """
        Select the optimal prompt based on performance data and context.

        Args:
            detection_type: 'ai' or 'human'
            iteration: Current iteration number
            section_name: Section being processed
            available_prompts: List of available prompt names

        Returns:
            Best prompt name to use
        """
        if not available_prompts:
            available_prompts = self._get_available_prompts(detection_type)

        # For iteration 1, use performance-based selection
        if iteration == 1:
            best_prompt = self._select_best_performing_prompt(
                detection_type, available_prompts, section_name
            )
            if best_prompt:
                logger.info(f"Selected best performing prompt: {best_prompt}")
                return best_prompt

        # For later iterations, avoid recently failed prompts
        return self._select_diverse_prompt(detection_type, iteration, available_prompts)

    def _get_available_prompts(self, detection_type: str) -> List[str]:
        """Get list of available prompt files for detection type."""
        pattern = f"{detection_type}_detection*.txt"
        prompt_files = list(self.prompt_templates_dir.glob(pattern))
        return [f.stem for f in prompt_files]

    def _select_best_performing_prompt(
        self,
        detection_type: str,
        available_prompts: List[str],
        section_name: str = None,
    ) -> Optional[str]:
        """Select prompt with best success rate and score performance."""
        candidates = []

        for prompt in available_prompts:
            key = f"{prompt}_{detection_type}"
            if key in self.performance_data:
                perf = self.performance_data[key]

                # Weight by success rate and average score
                score_weight = 1.0 - (
                    perf["avg_score"] / 100.0
                )  # Lower scores are better
                success_weight = perf["success_rate"]
                combined_score = (score_weight * 0.6) + (success_weight * 0.4)

                candidates.append((prompt, combined_score, perf["uses"]))

        if not candidates:
            return None

        # Sort by combined score, but prefer prompts with more usage data
        candidates.sort(key=lambda x: (x[1], x[2]), reverse=True)
        return candidates[0][0]

    def _select_diverse_prompt(
        self, detection_type: str, iteration: int, available_prompts: List[str]
    ) -> str:
        """Select prompt ensuring diversity across iterations."""
        # Avoid prompts that recently failed
        avoided_prompts = set()
        for prompt in available_prompts:
            key = f"{prompt}_{detection_type}"
            if key in self.performance_data:
                perf = self.performance_data[key]
                # Avoid if recent success rate is very low
                if perf["uses"] >= 3 and perf["success_rate"] < 0.2:
                    avoided_prompts.add(prompt)

        # Select from remaining prompts
        viable_prompts = [p for p in available_prompts if p not in avoided_prompts]
        if not viable_prompts:
            viable_prompts = available_prompts

        # Rotate through viable prompts
        index = (iteration - 1) % len(viable_prompts)
        return viable_prompts[index]

    def analyze_prompt_patterns(self, detection_type: str = None) -> Dict:
        """Analyze patterns in prompt performance to identify success factors."""
        analysis = {
            "top_performers": [],
            "worst_performers": [],
            "trends": {},
            "recommendations": [],
        }

        # Filter by detection type if specified
        relevant_data = {}
        for key, perf in self.performance_data.items():
            if detection_type is None or perf["detection_type"] == detection_type:
                relevant_data[key] = perf

        if not relevant_data:
            return analysis

        # Identify top and worst performers
        sorted_prompts = sorted(
            relevant_data.items(),
            key=lambda x: (x[1]["success_rate"], -x[1]["avg_score"]),
            reverse=True,
        )

        analysis["top_performers"] = [
            {
                "prompt": perf["prompt_name"],
                "type": perf["detection_type"],
                "success_rate": perf["success_rate"],
                "avg_score": perf["avg_score"],
                "uses": perf["uses"],
            }
            for _, perf in sorted_prompts[:3]
            if perf["uses"] >= 2
        ]

        analysis["worst_performers"] = [
            {
                "prompt": perf["prompt_name"],
                "type": perf["detection_type"],
                "success_rate": perf["success_rate"],
                "avg_score": perf["avg_score"],
                "uses": perf["uses"],
            }
            for _, perf in sorted_prompts[-3:]
            if perf["uses"] >= 2
        ]

        # Generate recommendations
        if analysis["top_performers"]:
            best = analysis["top_performers"][0]
            analysis["recommendations"].append(
                f"Use '{best['prompt']}' as primary {best['type']} detection prompt "
                f"(success rate: {best['success_rate']:.1%})"
            )

        return analysis

    def generate_optimized_prompt(
        self, detection_type: str, base_prompts: List[str] = None
    ) -> Tuple[str, str]:
        """
        Generate an optimized prompt based on successful patterns.

        Returns:
            Tuple of (prompt_content, suggested_filename)
        """
        analysis = self.analyze_prompt_patterns(detection_type)

        if not analysis["top_performers"]:
            logger.warning("No performance data available for prompt optimization")
            return self._create_default_optimized_prompt(detection_type)

        # Analyze successful prompts to extract patterns
        successful_prompts = [p["prompt"] for p in analysis["top_performers"]]

        # Load content of successful prompts
        successful_contents = []
        for prompt_name in successful_prompts:
            try:
                prompt_path = self.prompt_templates_dir / f"{prompt_name}.txt"
                if prompt_path.exists():
                    with open(prompt_path, "r") as f:
                        successful_contents.append(f.read().strip())
            except Exception as e:
                logger.warning(f"Failed to load prompt {prompt_name}: {e}")

        if not successful_contents:
            return self._create_default_optimized_prompt(detection_type)

        # Generate optimized prompt based on patterns
        optimized_content = self._synthesize_prompt_patterns(
            detection_type, successful_contents
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"{detection_type}_detection_optimized_{timestamp}.txt"

        return optimized_content, filename

    def _synthesize_prompt_patterns(
        self, detection_type: str, successful_prompts: List[str]
    ) -> str:
        """Synthesize successful prompt patterns into an optimized prompt."""

        # Extract common patterns
        common_phrases = self._extract_common_phrases(successful_prompts)

        if detection_type == "ai":
            optimized_prompt = f"""Rate this text's AI generation likelihood (0-100%):

Key indicators: {", ".join(common_phrases[:5])}

{{content}}

Format:
Percentage: X%
Summary: Brief analysis focusing on the strongest indicators
"""
        else:  # human detection
            optimized_prompt = f"""Rate this text's "trying too hard to be human" likelihood (0-100%):

Red flags: {", ".join(common_phrases[:5])}

{{content}}

Format:
Percentage: X%
Summary: Issues found
"""

        return optimized_prompt

    def _extract_common_phrases(self, prompts: List[str]) -> List[str]:
        """Extract common phrases and patterns from successful prompts."""
        # Simple pattern extraction - could be enhanced with NLP
        common_terms = [
            "formal language",
            "generic phrasing",
            "perfect grammar",
            "forced casual language",
            "fake emotions",
            "performative authenticity",
            "structured content",
            "consistent tone",
            "technical precision",
        ]

        # Return terms that appear in multiple prompts
        relevant_terms = []
        for term in common_terms:
            if sum(1 for prompt in prompts if term.lower() in prompt.lower()) >= 2:
                relevant_terms.append(term)

        return relevant_terms or common_terms[:3]

    def _create_default_optimized_prompt(self, detection_type: str) -> Tuple[str, str]:
        """Create a default optimized prompt when no data is available."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")

        if detection_type == "ai":
            content = """Rate this text's AI generation likelihood (0-100%):

Focus on: formal tone, generic phrasing, perfect structure, lack of personality

{content}

Format:
Percentage: X%
Summary: Key indicators found
"""
            filename = f"ai_detection_optimized_{timestamp}.txt"
        else:
            content = """Rate this text's "trying too hard to be human" likelihood (0-100%):

Red flags: forced informality, fake emotions, inappropriate casual language

{content}

Format:
Percentage: X%
Summary: Issues identified
"""
            filename = f"human_detection_optimized_{timestamp}.txt"

        return content, filename

    def get_performance_report(self) -> str:
        """Generate a comprehensive performance report."""
        if not self.performance_data:
            return "No performance data available yet."

        report = ["🎯 Prompt Performance Report", "=" * 50, ""]

        # Overall statistics
        total_uses = sum(p["uses"] for p in self.performance_data.values())
        ai_prompts = [
            p for p in self.performance_data.values() if p["detection_type"] == "ai"
        ]
        human_prompts = [
            p for p in self.performance_data.values() if p["detection_type"] == "human"
        ]

        report.extend(
            [
                f"Total prompt uses: {total_uses}",
                f"AI detection prompts tracked: {len(ai_prompts)}",
                f"Human detection prompts tracked: {len(human_prompts)}",
                "",
            ]
        )

        # Top performers
        for detection_type in ["ai", "human"]:
            analysis = self.analyze_prompt_patterns(detection_type)
            report.append(f"🏆 Top {detection_type.upper()} Detection Prompts:")

            if analysis["top_performers"]:
                for i, perf in enumerate(analysis["top_performers"], 1):
                    report.append(
                        f"  {i}. {perf['prompt']} - "
                        f"Success: {perf['success_rate']:.1%}, "
                        f"Avg Score: {perf['avg_score']:.1f}, "
                        f"Uses: {perf['uses']}"
                    )
            else:
                report.append("  No sufficient data yet")
            report.append("")

        # Recommendations
        ai_analysis = self.analyze_prompt_patterns("ai")
        human_analysis = self.analyze_prompt_patterns("human")

        all_recommendations = (
            ai_analysis["recommendations"] + human_analysis["recommendations"]
        )
        if all_recommendations:
            report.append("💡 Recommendations:")
            for rec in all_recommendations:
                report.append(f"  • {rec}")

        return "\n".join(report)
