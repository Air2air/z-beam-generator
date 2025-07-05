"""
Training Integration Service

Connects interactive training feedback to the production optimization system.
Ensures that training improvements propagate to production content generation.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from config.global_config import get_config
from modules.logger import get_logger

logger = get_logger("training_integration")


class TrainingIntegrationService:
    """Service that applies training insights to improve production prompts."""
    
    def __init__(self):
        self.config = get_config()
        self.training_data_file = "naturalness_training_data.json"
        self.prompt_updates_file = "generator/cache/prompt_updates.json"
        self.detection_prompts_file = "generator/detection/detection_prompts.json"
        self.improvement_prompts_file = "generator/detection/improvement_prompts.json"
        
    def apply_training_insights(self) -> Dict[str, Any]:
        """Apply training insights to improve production prompts."""
        results = {
            "updates_applied": 0,
            "prompts_modified": [],
            "insights_processed": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Load training data
        training_data = self._load_training_data()
        if not training_data:
            logger.info("No training data found to process")
            return results
            
        # Analyze patterns in training feedback
        insights = self._analyze_training_patterns(training_data)
        results["insights_processed"] = len(insights)
        
        # Apply insights to prompts
        for insight in insights:
            if self._apply_insight_to_prompts(insight):
                results["updates_applied"] += 1
                results["prompts_modified"].append(insight["prompt_type"])
                
        # Update optimization parameters based on feedback
        self._update_optimization_parameters(training_data)
        
        logger.info(f"Applied {results['updates_applied']} training insights to production system")
        return results
    
    def _load_training_data(self) -> List[Dict[str, Any]]:
        """Load training data from file."""
        try:
            if os.path.exists(self.training_data_file):
                with open(self.training_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"Loaded {len(data)} training entries")
                return data
        except Exception as e:
            logger.error(f"Failed to load training data: {e}")
        return []
    
    def _analyze_training_patterns(self, training_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze training data to extract actionable insights."""
        insights = []
        
        # Group feedback by rating patterns
        rating_patterns = self._analyze_rating_patterns(training_data)
        
        # Detect common issues in content that users rated as fake
        fake_content_issues = self._analyze_fake_content_patterns(training_data)
        
        # Find successful natural content characteristics  
        natural_content_patterns = self._analyze_natural_content_patterns(training_data)
        
        # Create insights for prompt improvements
        if fake_content_issues:
            insights.append({
                "type": "detection_improvement",
                "prompt_type": "ai_detection", 
                "issue": "false_negatives",
                "patterns": fake_content_issues,
                "action": "strengthen_detection_of_patterns"
            })
            
        if natural_content_patterns:
            insights.append({
                "type": "content_improvement",
                "prompt_type": "content_generation",
                "patterns": natural_content_patterns,
                "action": "incorporate_natural_patterns"
            })
            
        # Threshold adjustments based on user vs system disagreements
        threshold_insights = self._analyze_threshold_disagreements(training_data)
        if threshold_insights:
            insights.extend(threshold_insights)
            
        return insights
    
    def _analyze_rating_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user rating patterns."""
        ratings = [entry.get("user_rating", 3) for entry in data]
        avg_rating = sum(ratings) / len(ratings) if ratings else 3
        
        # Count disagreements with system
        disagreements = 0
        for entry in data:
            user_rating = entry.get("user_rating", 3)
            system_score = entry.get("system_nv_score")
            
            if system_score is not None:
                # Convert user rating (1-5, lower is more natural) to score (0-100, higher is more natural)
                user_naturalness = (6 - user_rating) * 20  # 1->100, 5->20
                if abs(user_naturalness - system_score) > 30:  # Significant disagreement
                    disagreements += 1
                    
        return {
            "average_user_rating": avg_rating,
            "total_entries": len(data),
            "system_disagreements": disagreements,
            "disagreement_rate": disagreements / len(data) if data else 0
        }
    
    def _analyze_fake_content_patterns(self, data: List[Dict[str, Any]]) -> List[str]:
        """Find patterns in content that users rated as fake (4-5)."""
        fake_patterns = []
        fake_content = []
        
        for entry in data:
            if entry.get("user_rating", 3) >= 4:  # User rated as fake
                content = entry.get("content", "")
                feedback = entry.get("user_feedback", "")
                fake_content.append({"content": content, "feedback": feedback})
        
        # Analyze common phrases/patterns in fake content
        if fake_content:
            # Look for common words/phrases that appear in fake content
            common_fake_phrases = self._extract_common_phrases(fake_content)
            fake_patterns.extend(common_fake_phrases)
            
        return fake_patterns
    
    def _analyze_natural_content_patterns(self, data: List[Dict[str, Any]]) -> List[str]:
        """Find patterns in content that users rated as natural (1-2).""" 
        natural_patterns = []
        natural_content = []
        
        for entry in data:
            if entry.get("user_rating", 3) <= 2:  # User rated as natural
                content = entry.get("content", "")
                feedback = entry.get("user_feedback", "")
                natural_content.append({"content": content, "feedback": feedback})
        
        # Analyze successful natural patterns
        if natural_content:
            common_natural_phrases = self._extract_common_phrases(natural_content)
            natural_patterns.extend(common_natural_phrases)
            
        return natural_patterns
    
    def _extract_common_phrases(self, content_entries: List[Dict[str, Any]]) -> List[str]:
        """Extract common phrases from content entries."""
        # Simple implementation - could be enhanced with NLP
        phrases = []
        
        for entry in content_entries:
            content = entry["content"].lower()
            feedback = entry["feedback"].lower()
            
            # Extract phrases from feedback that indicate specific issues
            if "sounds like ai" in feedback or "robotic" in feedback:
                phrases.append("robotic_language_pattern")
            if "too formal" in feedback:
                phrases.append("overly_formal_tone")
            if "repetitive" in feedback:
                phrases.append("repetitive_structure")
            if "natural" in feedback or "human" in feedback:
                phrases.append("natural_expression_pattern")
                
        return list(set(phrases))  # Remove duplicates
    
    def _analyze_threshold_disagreements(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze where user ratings disagree with system thresholds."""
        insights = []
        
        # Find cases where system and user strongly disagree
        strong_disagreements = []
        for entry in data:
            user_rating = entry.get("user_rating", 3)
            system_score = entry.get("system_nv_score")
            
            if system_score is not None:
                user_naturalness = (6 - user_rating) * 20
                disagreement = abs(user_naturalness - system_score)
                
                if disagreement > 40:  # Very strong disagreement
                    strong_disagreements.append({
                        "user_rating": user_rating,
                        "system_score": system_score,
                        "content": entry.get("content", "")[:100],
                        "disagreement": disagreement
                    })
        
        if strong_disagreements:
            # Determine if system is too strict or too lenient
            system_too_strict = sum(1 for d in strong_disagreements if d["system_score"] < (6 - d["user_rating"]) * 20)
            system_too_lenient = len(strong_disagreements) - system_too_strict
            
            if system_too_strict > system_too_lenient:
                insights.append({
                    "type": "threshold_adjustment",
                    "prompt_type": "natural_voice_detection",
                    "action": "increase_threshold",
                    "reason": "system_too_strict_compared_to_users"
                })
            elif system_too_lenient > system_too_strict:
                insights.append({
                    "type": "threshold_adjustment", 
                    "prompt_type": "natural_voice_detection",
                    "action": "decrease_threshold",
                    "reason": "system_too_lenient_compared_to_users"
                })
                
        return insights
    
    def _apply_insight_to_prompts(self, insight: Dict[str, Any]) -> bool:
        """Apply a specific insight to improve prompts."""
        try:
            if insight["type"] == "detection_improvement":
                return self._improve_detection_prompts(insight)
            elif insight["type"] == "content_improvement":
                return self._improve_content_prompts(insight)
            elif insight["type"] == "threshold_adjustment":
                return self._adjust_thresholds(insight)
        except Exception as e:
            logger.error(f"Failed to apply insight {insight['type']}: {e}")
            return False
        return False
    
    def _improve_detection_prompts(self, insight: Dict[str, Any]) -> bool:
        """Improve detection prompts based on training insight."""
        # Load current detection prompts
        try:
            with open(self.detection_prompts_file, 'r', encoding='utf-8') as f:
                prompts = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load detection prompts: {e}")
            return False
            
        # Find patterns that should be detected better
        patterns = insight.get("patterns", [])
        if not patterns:
            return False
            
        # Update AI detection prompt to catch these patterns
        if "ai_detection" in prompts:
            current_prompt = prompts["ai_detection"].get("system_prompt", "")
            
            # Add pattern awareness
            pattern_text = ", ".join(patterns)
            enhancement = f"\\n\\nPay special attention to detecting these AI-like patterns: {pattern_text}"
            
            if enhancement not in current_prompt:
                prompts["ai_detection"]["system_prompt"] = current_prompt + enhancement
                
                # Save updated prompts
                with open(self.detection_prompts_file, 'w', encoding='utf-8') as f:
                    json.dump(prompts, f, indent=2, ensure_ascii=False)
                    
                logger.info(f"Enhanced AI detection prompt with patterns: {pattern_text}")
                return True
                
        return False
    
    def _improve_content_prompts(self, insight: Dict[str, Any]) -> bool:
        """Improve content generation prompts based on training insight."""
        # This would update section prompts to incorporate natural patterns
        # Implementation depends on how section prompts are structured
        logger.info("Content prompt improvement not implemented yet")
        return False
    
    def _adjust_thresholds(self, insight: Dict[str, Any]) -> bool:
        """Adjust detection thresholds based on user feedback patterns."""
        action = insight.get("action", "")
        reason = insight.get("reason", "")
        
        try:
            # Get current thresholds
            current_ai = self.config.get_ai_detection_threshold()
            current_nv = self.config.get_natural_voice_threshold()
            
            # Apply adjustment based on insight
            if action == "increase_threshold":
                # System is too strict, increase threshold (be more lenient)
                new_ai = min(100, current_ai + 5)
                new_nv = min(100, current_nv + 5)
                self.config.update_ai_detection_threshold(new_ai)
                self.config.update_natural_voice_threshold(new_nv)
                logger.info(f"Increased thresholds: AI {current_ai}→{new_ai}, NV {current_nv}→{new_nv}")
                return True
                
            elif action == "decrease_threshold":
                # System is too lenient, decrease threshold (be more strict)
                new_ai = max(5, current_ai - 5)
                new_nv = max(5, current_nv - 5)
                self.config.update_ai_detection_threshold(new_ai)
                self.config.update_natural_voice_threshold(new_nv)
                logger.info(f"Decreased thresholds: AI {current_ai}→{new_ai}, NV {current_nv}→{new_nv}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to adjust thresholds: {e}")
            
        # Log recommendation even if we can't apply it
        recommendation = {
            "timestamp": datetime.now().isoformat(),
            "type": "threshold_recommendation",
            "action": action,
            "reason": reason,
            "current_ai_threshold": self.config.get_ai_detection_threshold(),
            "current_nv_threshold": self.config.get_natural_voice_threshold()
        }
        
        self._save_recommendation(recommendation)
        return True
    
    def _update_optimization_parameters(self, training_data: List[Dict[str, Any]]) -> None:
        """Update optimization parameters based on training patterns."""
        # Analyze if more iterations are needed based on user satisfaction
        recent_data = [entry for entry in training_data 
                      if self._is_recent(entry.get("timestamp", 0))]
        
        if recent_data:
            avg_satisfaction = sum(6 - entry.get("user_rating", 3) for entry in recent_data) / len(recent_data)
            
            # If users are generally unsatisfied, suggest more iterations
            if avg_satisfaction < 60:  # Less than 60% satisfaction
                recommendation = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "optimization_recommendation", 
                    "suggestion": "increase_iterations_per_section",
                    "reason": f"User satisfaction only {avg_satisfaction:.1f}%",
                    "current_iterations": self.config.get_iterations_per_section()
                }
                self._save_recommendation(recommendation)
    
    def _is_recent(self, timestamp: float) -> bool:
        """Check if timestamp is from the last week."""
        try:
            entry_time = datetime.fromtimestamp(timestamp)
            week_ago = datetime.now() - timedelta(days=7)
            return entry_time > week_ago
        except:
            return False
    
    def _save_recommendation(self, recommendation: Dict[str, Any]) -> None:
        """Save optimization recommendation."""
        try:
            recommendations_file = "generator/cache/training_recommendations.json"
            
            # Load existing recommendations
            recommendations = []
            if os.path.exists(recommendations_file):
                with open(recommendations_file, 'r', encoding='utf-8') as f:
                    recommendations = json.load(f)
                    
            # Add new recommendation
            recommendations.append(recommendation)
            
            # Keep only last 20 recommendations
            recommendations = recommendations[-20:]
            
            # Save back
            os.makedirs(os.path.dirname(recommendations_file), exist_ok=True)
            with open(recommendations_file, 'w', encoding='utf-8') as f:
                json.dump(recommendations, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Saved optimization recommendation: {recommendation['type']}")
            
        except Exception as e:
            logger.error(f"Failed to save recommendation: {e}")


def integrate_training_improvements():
    """Main function to integrate training improvements into production."""
    # Initialize config manager
    try:
        import sys
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        sys.path.insert(0, parent_dir)
        from run import USER_CONFIG, PROVIDER_MODELS
        
        from config.global_config import GlobalConfigManager
        GlobalConfigManager.initialize(USER_CONFIG, PROVIDER_MODELS)
        
    except Exception as e:
        print(f"❌ Failed to initialize configuration: {e}")
        return {"error": str(e)}
    
    service = TrainingIntegrationService()
    results = service.apply_training_insights()
    
    print("🔄 Training Integration Results:")
    print(f"   Insights processed: {results['insights_processed']}")
    print(f"   Updates applied: {results['updates_applied']}")
    print(f"   Prompts modified: {', '.join(results['prompts_modified']) if results['prompts_modified'] else 'None'}")
    
    return results


if __name__ == "__main__":
    integrate_training_improvements()
