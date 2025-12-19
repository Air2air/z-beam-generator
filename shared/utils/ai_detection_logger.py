"""
AI Detection Logging Utilities

Optimized logging system for AI detection iteration tracking with minimal verbosity.
Tracks score changes per iteration and reduces sentence logging to essential failure patterns.
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional


class AIDetectionIterationLogger:
    """Tracks AI detection scores across optimization iterations with concise logging."""
    
    def __init__(self):
        self.iteration_history: List[Dict[str, Any]] = []
        self.session_start_time = time.time()
    
    def log_iteration(self, 
                     iteration: int,
                     score: float,
                     classification: str,
                     confidence: float,
                     provider: str,
                     processing_time: float,
                     failing_sentences_count: int = 0,
                     failing_sentences_percentage: float = 0.0,
                     key_failing_patterns: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a single optimization iteration with minimal data.
        
        Args:
            iteration: Iteration number
            score: AI detection score
            classification: Detection classification (ai/human/unclear)
            confidence: Detection confidence level
            provider: AI detection provider (winston, etc.)
            processing_time: Time taken for this iteration
            failing_sentences_count: Number of sentences flagged as AI-like
            failing_sentences_percentage: Percentage of sentences flagged
            key_failing_patterns: Essential failure pattern metrics only
        """
        iteration_data = {
            "iteration": iteration,
            "timestamp": datetime.now().isoformat(),
            "score": round(score, 2),
            "score_change": self._calculate_score_change(score),
            "classification": classification,
            "confidence": round(confidence, 4),
            "provider": provider,
            "processing_time": round(processing_time, 3),
            "cumulative_time": round(time.time() - self.session_start_time, 3)
        }
        
        # Add concise sentence analysis if provided
        if failing_sentences_count > 0:
            iteration_data["sentence_analysis"] = {
                "failing_count": failing_sentences_count,
                "failing_percentage": round(failing_sentences_percentage, 1),
                "patterns": key_failing_patterns or {}
            }
        
        self.iteration_history.append(iteration_data)
    
    def _calculate_score_change(self, current_score: float) -> Optional[float]:
        """Calculate score change from previous iteration."""
        if not self.iteration_history:
            return None
        
        previous_score = self.iteration_history[-1]["score"]
        change = current_score - previous_score
        return round(change, 2)
    
    def get_iteration_summary(self) -> Dict[str, Any]:
        """Get concise summary of all iterations."""
        if not self.iteration_history:
            return {}
        
        first_score = self.iteration_history[0]["score"]
        last_score = self.iteration_history[-1]["score"]
        total_improvement = round(last_score - first_score, 2)
        
        # Find best iteration
        best_iteration = max(self.iteration_history, key=lambda x: x["score"])
        
        return {
            "total_iterations": len(self.iteration_history),
            "initial_score": first_score,
            "final_score": last_score,
            "total_improvement": total_improvement,
            "best_score": best_iteration["score"],
            "best_iteration": best_iteration["iteration"],
            "total_processing_time": round(sum(x["processing_time"] for x in self.iteration_history), 3),
            "average_score": round(sum(x["score"] for x in self.iteration_history) / len(self.iteration_history), 2),
            "improvement_trend": self._calculate_trend()
        }
    
    def _calculate_trend(self) -> str:
        """Calculate overall improvement trend."""
        if len(self.iteration_history) < 2:
            return "insufficient_data"
        
        scores = [x["score"] for x in self.iteration_history]
        
        # Simple trend analysis
        improvements = sum(1 for i in range(1, len(scores)) if scores[i] > scores[i-1])
        degradations = sum(1 for i in range(1, len(scores)) if scores[i] < scores[i-1])
        
        if improvements > degradations:
            return "improving"
        elif degradations > improvements:
            return "degrading"
        else:
            return "stable"
    
    def format_compact_log(self, include_details: bool = False) -> str:
        """
        Format iteration history as compact YAML for MD file logging.
        
        Args:
            include_details: Whether to include sentence analysis details
            
        Returns:
            Compact YAML string suitable for markdown files
        """
        if not self.iteration_history:
            return ""
        
        lines = ["optimization_iterations:"]
        summary = self.get_iteration_summary()
        
        # Add summary
        lines.append(f"  summary:")
        lines.append(f"    total_iterations: {summary['total_iterations']}")
        lines.append(f"    score_progression: {summary['initial_score']} → {summary['final_score']} ({summary['total_improvement']:+.1f})")
        lines.append(f"    best_score: {summary['best_score']} (iteration {summary['best_iteration']})")
        lines.append(f"    trend: {summary['improvement_trend']}")
        lines.append(f"    total_time: {summary['total_processing_time']}s")
        lines.append("")
        
        # Add iteration details
        lines.append("  iterations:")
        for iteration_data in self.iteration_history:
            score_change = iteration_data.get("score_change")
            change_str = f" ({score_change:+.1f})" if score_change is not None else ""
            
            lines.append(f"    - iteration: {iteration_data['iteration']}")
            lines.append(f"      score: {iteration_data['score']}{change_str}")
            lines.append(f"      classification: {iteration_data['classification']}")
            lines.append(f"      time: {iteration_data['processing_time']}s")
            
            # Add sentence analysis if requested and available
            if include_details and "sentence_analysis" in iteration_data:
                analysis = iteration_data["sentence_analysis"]
                lines.append(f"      failing_sentences: {analysis['failing_count']} ({analysis['failing_percentage']}%)")
                
                if analysis["patterns"]:
                    patterns = analysis["patterns"]
                    pattern_items = []
                    for key, value in patterns.items():
                        if isinstance(value, (int, float)):
                            pattern_items.append(f"{key}: {value}")
                        elif isinstance(value, bool):
                            pattern_items.append(f"{key}: {str(value).lower()}")
                    
                    if pattern_items:
                        lines.append(f"      patterns: {{{', '.join(pattern_items)}}}")
            
            lines.append("")
        
        return "\n".join(lines)


def extract_key_failing_patterns(winston_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract only essential failing pattern metrics from verbose Winston details.
    
    Args:
        winston_details: Full Winston API response details
        
    Returns:
        Concise dictionary with key pattern metrics
    """
    patterns = {}
    
    # Extract failing patterns if available
    if "failing_patterns" in winston_details:
        failing_patterns = winston_details["failing_patterns"]
        
        # Only include essential metrics
        if "avg_length" in failing_patterns:
            patterns["avg_length"] = round(failing_patterns["avg_length"], 1)
        
        if "contains_repetition" in failing_patterns:
            patterns["repetition"] = failing_patterns["contains_repetition"]
        
        if "uniform_structure" in failing_patterns:
            patterns["uniform"] = failing_patterns["uniform_structure"]
        
        if "technical_density" in failing_patterns:
            patterns["tech_density"] = round(failing_patterns["technical_density"], 3)
    
    return patterns


def update_content_with_iteration_log(content: str, logger: AIDetectionIterationLogger, 
                                    include_sentence_details: bool = False) -> str:
    """
    Replace verbose AI detection logging with concise iteration tracking.
    
    Args:
        content: Original markdown content
        logger: Iteration logger with tracked data
        include_sentence_details: Whether to include sentence analysis details
        
    Returns:
        Updated content with compact iteration logging
    """
    lines = content.split('\n')
    updated_lines = []
    
    # Find and replace ai_detection_analysis section
    in_ai_detection = False
    in_quality_analysis = False
    detection_start_idx = None
    
    for i, line in enumerate(lines):
        if line.strip() == "ai_detection_analysis:":
            in_ai_detection = True
            detection_start_idx = i
            continue
        elif line.strip() == "quality_analysis:" and in_ai_detection:
            in_quality_analysis = True
            in_ai_detection = False
            
            # Insert compact iteration log before quality_analysis
            if logger.iteration_history:
                compact_log = logger.format_compact_log(include_sentence_details)
                updated_lines.extend(compact_log.split('\n'))
                updated_lines.append("")
            
            updated_lines.append(line)
            continue
        elif line.strip().startswith("---") and (in_ai_detection or in_quality_analysis):
            in_ai_detection = False
            in_quality_analysis = False
            updated_lines.append(line)
            continue
        elif not in_ai_detection:
            updated_lines.append(line)
    
    return '\n'.join(updated_lines)


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    logger = AIDetectionIterationLogger()
    
    # Simulate optimization iterations
    logger.log_iteration(
        iteration=1,
        score=35.2,
        classification="unclear",
        confidence=0.706,
        provider="winston",
        processing_time=2.1,
        failing_sentences_count=25,
        failing_sentences_percentage=31.6,
        key_failing_patterns={
            "avg_length": 21.3,
            "contains_repetition": True,
            "uniform_structure": True,
            "technical_density": 0.274
        }
    )
    
    logger.log_iteration(
        iteration=2,
        score=42.8,
        classification="unclear", 
        confidence=0.856,
        provider="winston",
        processing_time=1.9,
        failing_sentences_count=18,
        failing_sentences_percentage=24.1,
        key_failing_patterns={
            "avg_length": 23.7,
            "contains_repetition": True,
            "uniform_structure": False,
            "technical_density": 0.291
        }
    )
    
    logger.log_iteration(
        iteration=3,
        score=46.2,
        classification="unclear",
        confidence=0.924,
        provider="winston", 
        processing_time=2.3,
        failing_sentences_count=15,
        failing_sentences_percentage=20.8,
        key_failing_patterns={
            "avg_length": 25.1,
            "contains_repetition": False,
            "uniform_structure": False,
            "technical_density": 0.312
        }
    )
    
    print("=== Compact Iteration Log ===")
    print(logger.format_compact_log(include_details=True))
    
    print("\n=== Summary ===")
    summary = logger.get_iteration_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
