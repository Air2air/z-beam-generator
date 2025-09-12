"""
AI Detection Analysis Utilities

Provides utility functions for data analysis, learning insights extraction,
and configuration optimization support.
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class AnalysisUtils:
    """Utility functions for AI detection analysis and optimization."""

    @staticmethod
    def get_learning_insights(successful_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract learning insights from successful configurations.
        
        Args:
            successful_configs: List of successful configuration entries
            
        Returns:
            Dict containing learning insights and recommendations
        """
        try:
            if not successful_configs:
                return {"insights": "No successful configurations available"}

            # Analyze flag frequency in successful configurations
            flag_frequency = {}
            total_configs = len(successful_configs)
            
            for config_entry in successful_configs:
                config = config_entry.get("config", {})
                for flag, enabled in config.items():
                    if not flag.startswith("_") and enabled:
                        flag_frequency[flag] = flag_frequency.get(flag, 0) + 1

            # Calculate success rates for each flag
            flag_success_rates = {
                flag: (count / total_configs) * 100
                for flag, count in flag_frequency.items()
            }

            # Identify most successful flags (>70% success rate)
            recommended_flags = [
                flag for flag, rate in flag_success_rates.items() if rate >= 70
            ]

            # Analyze score patterns
            scores = [entry.get("score", 0) for entry in successful_configs]
            avg_score = sum(scores) / len(scores) if scores else 0

            insights = {
                "total_successful_configs": total_configs,
                "average_successful_score": avg_score,
                "recommended_flags": recommended_flags,
                "flag_success_rates": flag_success_rates,
                "insights": f"Analyzed {total_configs} successful configurations with average score {avg_score:.1f}"
            }

            logger.info(f"Generated learning insights: {len(recommended_flags)} recommended flags")
            return insights

        except Exception as e:
            logger.warning(f"Failed to generate learning insights: {e}")
            return {"insights": "Error analyzing successful configurations"}

    @staticmethod
    def analyze_score_trends(iteration_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze score trends from iteration history.
        
        Args:
            iteration_history: List of iteration entries with scores
            
        Returns:
            Dict containing trend analysis
        """
        try:
            if not iteration_history:
                return {"insights": "No iteration history available"}

            # Analyze score patterns
            scores = [entry.get("score", 0) for entry in iteration_history]
            score_changes = []
            for i in range(1, len(scores)):
                score_changes.append(scores[i] - scores[i - 1])

            # Identify successful iterations
            successful_iterations = [
                entry for entry in iteration_history if entry.get("score", 0) > 50
            ]

            # Calculate trend metrics
            total_improvement = scores[-1] - scores[0] if len(scores) > 1 else 0
            avg_change = sum(score_changes) / len(score_changes) if score_changes else 0
            
            # Determine trend direction
            if avg_change > 2:
                trend = "strongly improving"
            elif avg_change > 0:
                trend = "improving"
            elif avg_change > -2:
                trend = "stable"
            else:
                trend = "declining"

            insights = {
                "total_iterations": len(iteration_history),
                "average_score": sum(scores) / len(scores) if scores else 0,
                "score_trend": trend,
                "total_improvement": total_improvement,
                "successful_iterations": len(successful_iterations),
                "success_rate": (len(successful_iterations) / len(iteration_history)) * 100,
                "insights": f"Analyzed {len(iteration_history)} iterations with {len(successful_iterations)} successful ones"
            }

            logger.info(f"Score trend analysis: {trend} with {total_improvement:.1f} total improvement")
            return insights

        except Exception as e:
            logger.warning(f"Failed to analyze score trends: {e}")
            return {"insights": "Error analyzing iteration history"}

    @staticmethod
    def find_optimal_flag_combinations(successful_configs: List[Dict[str, Any]]) -> List[List[str]]:
        """
        Find optimal flag combinations from successful configurations.
        
        Args:
            successful_configs: List of successful configuration entries
            
        Returns:
            List of optimal flag combinations
        """
        try:
            if not successful_configs:
                return []

            # Group configurations by score ranges
            score_ranges = {
                "excellent": [],  # 80+
                "good": [],       # 60-79
                "moderate": []    # 40-59
            }

            for config_entry in successful_configs:
                score = config_entry.get("score", 0)
                config = config_entry.get("config", {})
                
                if score >= 80:
                    score_ranges["excellent"].append(config)
                elif score >= 60:
                    score_ranges["good"].append(config)
                elif score >= 40:
                    score_ranges["moderate"].append(config)

            optimal_combinations = []

            # Find common patterns in each score range
            for range_name, configs in score_ranges.items():
                if not configs:
                    continue
                
                # Find flags that appear in most configurations in this range
                flag_frequency = {}
                for config in configs:
                    enabled_flags = [flag for flag, enabled in config.items() 
                                   if not flag.startswith("_") and enabled]
                    for flag in enabled_flags:
                        flag_frequency[flag] = flag_frequency.get(flag, 0) + 1

                # Get flags that appear in >50% of configs in this range
                threshold = len(configs) * 0.5
                common_flags = [flag for flag, count in flag_frequency.items() 
                              if count >= threshold]
                
                if common_flags:
                    optimal_combinations.append(common_flags)

            logger.info(f"Found {len(optimal_combinations)} optimal flag combinations")
            return optimal_combinations

        except Exception as e:
            logger.warning(f"Failed to find optimal flag combinations: {e}")
            return []

    @staticmethod
    def calculate_configuration_similarity(config1: Dict[str, Any], config2: Dict[str, Any]) -> float:
        """
        Calculate similarity between two configurations.
        
        Args:
            config1: First configuration
            config2: Second configuration
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        try:
            # Get all flags from both configurations
            all_flags = set()
            all_flags.update(k for k in config1.keys() if not k.startswith("_"))
            all_flags.update(k for k in config2.keys() if not k.startswith("_"))

            if not all_flags:
                return 1.0  # Empty configurations are identical

            # Count matching flags
            matching_flags = 0
            for flag in all_flags:
                val1 = config1.get(flag, False)
                val2 = config2.get(flag, False)
                if val1 == val2:
                    matching_flags += 1

            similarity = matching_flags / len(all_flags)
            return similarity

        except Exception as e:
            logger.warning(f"Failed to calculate configuration similarity: {e}")
            return 0.0

    @staticmethod
    def prioritize_enhancements_from_config(config: Dict[str, Any]) -> List[str]:
        """
        Prioritize enhancement flags based on configuration analysis.
        
        Args:
            config: Configuration to analyze
            
        Returns:
            List of prioritized enhancement flags
        """
        try:
            # Define priority categories
            high_priority = [
                "natural_language_patterns",
                "conversational_style", 
                "sentence_variability",
                "cultural_adaptation"
            ]
            
            medium_priority = [
                "syntactic_complexity_variation",
                "discourse_marker_diversity",
                "emotional_depth",
                "paragraph_structure"
            ]
            
            low_priority = [
                "epistemic_markers",
                "politeness_strategies",
                "expertise_level_markers"
            ]

            # Get currently enabled flags
            enabled_flags = [flag for flag, enabled in config.items() 
                           if not flag.startswith("_") and enabled]

            # Prioritize based on what's not yet enabled
            prioritized = []
            
            # Add high priority flags that aren't enabled
            for flag in high_priority:
                if flag not in enabled_flags:
                    prioritized.append(flag)
            
            # Add medium priority flags that aren't enabled
            for flag in medium_priority:
                if flag not in enabled_flags:
                    prioritized.append(flag)
            
            # Add low priority flags that aren't enabled
            for flag in low_priority:
                if flag not in enabled_flags:
                    prioritized.append(flag)

            logger.info(f"Prioritized {len(prioritized)} enhancement flags")
            return prioritized

        except Exception as e:
            logger.warning(f"Failed to prioritize enhancements: {e}")
            return []

    @staticmethod
    def detect_configuration_issues(config: Dict[str, Any]) -> List[str]:
        """
        Detect potential issues with a configuration.
        
        Args:
            config: Configuration to analyze
            
        Returns:
            List of detected issues
        """
        issues = []
        
        try:
            # Check for too many enabled flags
            enabled_count = sum(1 for k, v in config.items() 
                              if not k.startswith("_") and v is True)
            
            if enabled_count > 25:
                issues.append(f"Too many flags enabled ({enabled_count}), may cause conflicts")
            elif enabled_count == 0:
                issues.append("No enhancement flags enabled")
            
            # Check for conflicting combinations (example)
            if (config.get("formal_language", False) and 
                config.get("conversational_style", False)):
                issues.append("Conflicting flags: formal_language and conversational_style")
            
            # Check for missing core flags
            core_flags = ["natural_language_patterns", "sentence_variability"]
            missing_core = [flag for flag in core_flags if not config.get(flag, False)]
            
            if missing_core:
                issues.append(f"Missing core flags: {', '.join(missing_core)}")

            if issues:
                logger.warning(f"Detected {len(issues)} configuration issues")
            
            return issues

        except Exception as e:
            logger.warning(f"Failed to detect configuration issues: {e}")
            return ["Error analyzing configuration"]
