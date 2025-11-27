#!/usr/bin/env python3
"""
Image Pipeline Failure Monitor

Tracks and anticipates failure points across the entire image generation pipeline:
- Research phase failures
- Prompt construction issues
- Imagen API failures
- Validation failures
- Quality degradation patterns

Author: AI Assistant
Date: November 25, 2025
"""

import json
import logging
import os
import time
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class FailureStage(Enum):
    """Pipeline stages where failures can occur"""
    RESEARCH = "research"
    PROMPT_BUILDING = "prompt_building"
    IMAGEN_GENERATION = "imagen_generation"
    VALIDATION = "validation"
    POST_PROCESSING = "post_processing"


class FailureType(Enum):
    """Specific failure types to monitor"""
    # Research failures
    JSON_MALFORMED = "json_malformed"
    MISSING_PATTERNS = "missing_patterns"
    INSUFFICIENT_PHOTO_REFS = "insufficient_photo_refs"
    
    # Prompt failures
    PROMPT_TOO_LONG = "prompt_too_long"
    CONTRADICTORY_INSTRUCTIONS = "contradictory_instructions"
    MISSING_MATERIAL_DATA = "missing_material_data"
    
    # Imagen failures
    SAFETY_FILTER = "safety_filter"
    API_TIMEOUT = "api_timeout"
    API_RATE_LIMIT = "api_rate_limit"
    GENERATION_ERROR = "generation_error"
    
    # Validation failures
    LOW_REALISM_SCORE = "low_realism_score"
    PHYSICS_VIOLATION = "physics_violation"
    MATERIAL_MISMATCH = "material_mismatch"
    BEFORE_AFTER_INCONSISTENT = "before_after_inconsistent"
    AI_HALLUCINATION = "ai_hallucination"
    
    # Quality degradation
    BLURRY_OUTPUT = "blurry_output"
    COLOR_INACCURACY = "color_inaccuracy"
    TEXTURE_UNREALISTIC = "texture_unrealistic"
    COMPOSITION_POOR = "composition_poor"


@dataclass
class FailureRecord:
    """Record of a pipeline failure"""
    timestamp: str
    material: str
    stage: str
    failure_type: str
    severity: str  # low, medium, high, critical
    details: Dict[str, Any]
    retry_succeeded: Optional[bool] = None
    resolution: Optional[str] = None


class ImagePipelineMonitor:
    """Comprehensive pipeline failure monitoring and prediction"""
    
    def __init__(self, max_history: int = 200):
        """
        Initialize pipeline monitor.
        
        Args:
            max_history: Maximum number of failures to track
        """
        self.max_history = max_history
        
        # Failure tracking by stage and type
        self.failure_history = deque(maxlen=max_history)
        self.failures_by_stage = defaultdict(int)
        self.failures_by_type = defaultdict(int)
        self.failures_by_material_category = defaultdict(int)
        
        # Success tracking
        self.total_attempts = 0
        self.successful_completions = 0
        
        # Quality trend tracking
        self.realism_scores = deque(maxlen=50)
        self.validation_failures = deque(maxlen=50)
        
        # Material-specific failure patterns
        self.material_specific_issues = defaultdict(lambda: defaultdict(int))
        
        # Cache directory
        self.cache_dir = "domains/cache/pipeline_monitoring"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Load historical data
        self._load_history()
    
    def record_failure(
        self,
        material: str,
        stage: FailureStage,
        failure_type: FailureType,
        severity: str = "medium",
        details: Optional[Dict[str, Any]] = None,
        retry_succeeded: Optional[bool] = None
    ):
        """
        Record a pipeline failure.
        
        Args:
            material: Material being processed
            stage: Pipeline stage where failure occurred
            failure_type: Specific type of failure
            severity: Impact level (low, medium, high, critical)
            details: Additional context
            retry_succeeded: Whether retry fixed the issue
        """
        record = FailureRecord(
            timestamp=datetime.now().isoformat(),
            material=material,
            stage=stage.value,
            failure_type=failure_type.value,
            severity=severity,
            details=details or {},
            retry_succeeded=retry_succeeded
        )
        
        self.failure_history.append(record)
        self.failures_by_stage[stage.value] += 1
        self.failures_by_type[failure_type.value] += 1
        
        # Track material category patterns
        category = self._get_material_category(material)
        self.material_specific_issues[category][failure_type.value] += 1
        
        self._save_history()
        
        logger.warning(
            f"⚠️  Pipeline failure recorded: {stage.value} - {failure_type.value} "
            f"({severity}) for {material}"
        )
    
    def record_success(self, material: str, realism_score: Optional[float] = None):
        """
        Record a successful completion.
        
        Args:
            material: Material processed
            realism_score: Optional realism score (0-100)
        """
        self.total_attempts += 1
        self.successful_completions += 1
        
        if realism_score is not None:
            self.realism_scores.append(realism_score)
        
        self._save_history()
    
    def record_validation_result(self, material: str, validation_result: Dict[str, Any]):
        """
        Record validation result for quality trend analysis.
        
        Args:
            material: Material validated
            validation_result: Validation result dictionary
        """
        self.validation_failures.append({
            'material': material,
            'timestamp': datetime.now().isoformat(),
            'passed': validation_result.get('passed', False),
            'realism_score': validation_result.get('realism_score'),
            'issues': {
                'physics': validation_result.get('physics_issues', []),
                'distribution': validation_result.get('distribution_issues', []),
                'material': validation_result.get('material_appearance_issues', [])
            }
        })
    
    def predict_likely_failures(self, material: str) -> List[Dict[str, Any]]:
        """
        Predict likely failure points for a material based on history.
        
        Args:
            material: Material to be processed
            
        Returns:
            List of predicted failure points with probabilities
        """
        category = self._get_material_category(material)
        predictions = []
        
        # Get material-specific failure rates
        category_issues = self.material_specific_issues.get(category, {})
        total_category_attempts = sum(category_issues.values())
        
        if total_category_attempts > 0:
            for failure_type, count in category_issues.items():
                probability = count / total_category_attempts
                if probability > 0.2:  # 20% threshold
                    predictions.append({
                        'failure_type': failure_type,
                        'probability': probability,
                        'historical_count': count,
                        'recommendation': self._get_mitigation_strategy(failure_type)
                    })
        
        # Sort by probability
        predictions.sort(key=lambda x: x['probability'], reverse=True)
        return predictions
    
    def get_quality_trend_analysis(self) -> Dict[str, Any]:
        """
        Analyze quality trends over recent generations.
        
        Returns:
            Dictionary with trend analysis
        """
        if not self.realism_scores:
            return {'status': 'insufficient_data'}
        
        scores = list(self.realism_scores)
        avg_score = sum(scores) / len(scores)
        
        # Calculate trend (recent vs older)
        if len(scores) >= 10:
            recent_avg = sum(scores[-5:]) / 5  # Last 5 scores
            older_avg = sum(scores[:5]) / 5 if len(scores) >= 10 else avg_score  # First 5 scores
            trend_magnitude = abs(recent_avg - older_avg)
            if recent_avg > older_avg + 2:  # Improving by at least 2 points
                trend = "improving"
            elif older_avg > recent_avg + 2:  # Declining by at least 2 points
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
            trend_magnitude = 0
        
        # Identify common quality issues
        common_issues = defaultdict(int)
        for validation in list(self.validation_failures)[-20:]:
            for issue_type, issues in validation['issues'].items():
                if issues:
                    common_issues[issue_type] += len(issues)
        
        return {
            'average_realism': avg_score,
            'trend': trend,
            'trend_magnitude': trend_magnitude,
            'samples': len(scores),
            'common_issues': dict(common_issues),
            'recommendation': self._get_quality_recommendation(avg_score, trend)
        }
    
    def get_stage_failure_rates(self) -> Dict[str, float]:
        """
        Calculate failure rates by pipeline stage.
        
        Returns:
            Dictionary of stage -> failure_rate
        """
        total_failures = sum(self.failures_by_stage.values())
        if total_failures == 0:
            return {}
        
        return {
            stage: (count / total_failures) * 100
            for stage, count in self.failures_by_stage.items()
        }
    
    def get_monitoring_report(self) -> str:
        """
        Generate comprehensive monitoring report.
        
        Returns:
            Formatted report string
        """
        if self.total_attempts == 0:
            return "No pipeline monitoring data yet."
        
        success_rate = (self.successful_completions / self.total_attempts) * 100
        
        report = [
            "\n" + "="*80,
            "🔍 IMAGE PIPELINE MONITORING REPORT",
            "="*80,
            f"\n📈 Success Rate: {success_rate:.1f}% ({self.successful_completions}/{self.total_attempts})",
            f"🔄 Total Failures: {len(self.failure_history)}",
        ]
        
        # Failure by stage
        if self.failures_by_stage:
            report.append("\n\n📊 Failures by Stage:")
            stage_rates = self.get_stage_failure_rates()
            for stage, percentage in sorted(stage_rates.items(), key=lambda x: x[1], reverse=True):
                count = self.failures_by_stage[stage]
                report.append(f"   • {stage}: {count} ({percentage:.1f}%)")
        
        # Top failure types
        if self.failures_by_type:
            report.append("\n\n⚠️  Top Failure Types:")
            top_failures = sorted(
                self.failures_by_type.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            for failure_type, count in top_failures:
                report.append(f"   • {failure_type}: {count}")
        
        # Quality trend
        quality_trend = self.get_quality_trend_analysis()
        if quality_trend.get('status') != 'insufficient_data':
            report.append(f"\n\n🎨 Quality Trend:")
            report.append(f"   • Average Realism: {quality_trend['average_realism']:.1f}/100")
            report.append(f"   • Trend: {quality_trend['trend'].upper()}")
            if quality_trend['common_issues']:
                report.append(f"   • Common Issues: {', '.join(quality_trend['common_issues'].keys())}")
        
        # Recent critical failures
        recent_critical = [
            f for f in list(self.failure_history)[-10:]
            if f.severity in ['high', 'critical']
        ]
        if recent_critical:
            report.append(f"\n\n🚨 Recent Critical Failures: {len(recent_critical)}")
            for failure in recent_critical[-3:]:
                report.append(
                    f"   • {failure.material} - {failure.failure_type} "
                    f"({failure.stage})"
                )
        
        report.append("\n" + "="*80 + "\n")
        return "\n".join(report)
    
    def _get_material_category(self, material: str) -> str:
        """Map material to category for pattern tracking"""
        material_lower = material.lower()
        
        if any(m in material_lower for m in ["steel", "iron"]):
            return "metals_ferrous"
        elif any(m in material_lower for m in ["aluminum", "copper", "brass", "bronze"]):
            return "metals_non_ferrous"
        elif "glass" in material_lower:
            return "ceramics_glass"
        elif any(c in material_lower for c in ["ceramic", "porcelain"]):
            return "ceramics_traditional"
        elif any(p in material_lower for p in ["plastic", "polymer"]):
            return "polymers"
        elif "wood" in material_lower:
            return "wood"
        else:
            return "other"
    
    def _get_mitigation_strategy(self, failure_type: str) -> str:
        """Get recommended mitigation for failure type"""
        strategies = {
            'json_malformed': "Enable progressive JSON repair, add format validation",
            'missing_patterns': "Increase research depth, add fallback patterns",
            'insufficient_photo_refs': "Require minimum 2 URLs per pattern",
            'prompt_too_long': "Enable prompt compression, prioritize critical details",
            'safety_filter': "Review contamination descriptions for triggering language",
            'low_realism_score': "Add reference image comparison, strengthen physics constraints",
            'physics_violation': "Enhance contamination physics validation in prompt",
            'material_mismatch': "Improve material-specific appearance descriptions",
            'ai_hallucination': "Add reference image anchoring, increase photo URL weight",
            'blurry_output': "Increase resolution guidance, add sharpness constraints",
        }
        return strategies.get(failure_type, "Review logs and adjust pipeline parameters")
    
    def _get_quality_recommendation(self, avg_score: float, trend: str) -> str:
        """Get quality improvement recommendation"""
        if avg_score < 60:
            return "CRITICAL: Review contamination patterns and reference images"
        elif avg_score < 75 and trend == "declining":
            return "WARNING: Quality declining - investigate recent prompt changes"
        elif avg_score < 75:
            return "ATTENTION: Below target - add more photo references"
        elif trend == "declining":
            return "Monitor trend - quality starting to decline"
        else:
            return "Quality acceptable - maintain current approach"
    
    def _load_history(self):
        """Load failure history from disk"""
        history_file = os.path.join(self.cache_dir, "pipeline_history.json")
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    self.total_attempts = data.get('total_attempts', 0)
                    self.successful_completions = data.get('successful_completions', 0)
                    self.failures_by_stage = defaultdict(int, data.get('failures_by_stage', {}))
                    self.failures_by_type = defaultdict(int, data.get('failures_by_type', {}))
                    
                    # Reconstruct material-specific issues
                    for category, issues in data.get('material_specific_issues', {}).items():
                        self.material_specific_issues[category] = defaultdict(int, issues)
                    
                    # Load recent history
                    history = data.get('recent_failures', [])
                    for record_dict in history[-self.max_history:]:
                        record = FailureRecord(**record_dict)
                        self.failure_history.append(record)
                    
                logger.info(f"📥 Loaded pipeline monitoring history: {self.total_attempts} attempts")
            except Exception as e:
                logger.warning(f"Failed to load pipeline history: {e}")
    
    def _save_history(self):
        """Save failure history to disk"""
        history_file = os.path.join(self.cache_dir, "pipeline_history.json")
        try:
            # Convert material_specific_issues to JSON-serializable format
            material_issues_dict = {
                category: dict(issues)
                for category, issues in self.material_specific_issues.items()
            }
            
            data = {
                'total_attempts': self.total_attempts,
                'successful_completions': self.successful_completions,
                'failures_by_stage': dict(self.failures_by_stage),
                'failures_by_type': dict(self.failures_by_type),
                'material_specific_issues': material_issues_dict,
                'recent_failures': [asdict(f) for f in list(self.failure_history)],
                'last_updated': datetime.now().isoformat()
            }
            with open(history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save pipeline history: {e}")


# Global monitor instance
_pipeline_monitor_instance = None


def get_pipeline_monitor() -> ImagePipelineMonitor:
    """Get or create global pipeline monitor instance"""
    global _pipeline_monitor_instance
    if _pipeline_monitor_instance is None:
        _pipeline_monitor_instance = ImagePipelineMonitor()
    return _pipeline_monitor_instance
