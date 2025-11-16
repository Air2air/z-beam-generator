"""
Sweet Spot Analyzer - Intelligent Parameter Optimization

Analyzes successful generations to identify "sweet spot" parameter ranges that
consistently produce high human scores. Continuously updates as new data arrives.

Key Features:
1. Parameter Range Analysis - Find optimal ranges for each parameter
2. Correlation Detection - Identify which parameters most affect human_score
3. Material-Specific Sweet Spots - Different materials may need different settings
4. Maximum Score Tracking - Always know the best ever achieved
5. Success Pattern Recognition - What combinations work best together?

Fail-fast design: Requires sufficient database samples for statistical validity.
"""

import sqlite3
import statistics
import json
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class SweetSpot:
    """Represents an optimal parameter range."""
    parameter_name: str
    optimal_min: float
    optimal_max: float
    optimal_median: float
    avg_human_score: float
    sample_count: int
    confidence: str  # 'high', 'medium', 'low'
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class MaximumAchievement:
    """Tracks the best ever achieved score."""
    material: str
    component_type: str
    max_human_score: float
    max_claude_score: Optional[float]
    achieved_at: str
    parameters: Dict[str, Any]
    generated_text: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


class SweetSpotAnalyzer:
    """
    Analyze success patterns to find optimal parameter ranges.
    
    Uses statistical analysis to identify:
    - Parameter ranges that correlate with high human scores
    - Material-specific optimal settings
    - Cross-parameter interactions (what works well together)
    - Maximum achievements (best ever scores)
    """
    
    def __init__(
        self,
        db_path: str,
        min_samples: int = 10,
        success_threshold: float = 50.0
    ):
        """
        Initialize sweet spot analyzer.
        
        Args:
            db_path: Path to Winston feedback database
            min_samples: Minimum samples needed for reliable analysis
            success_threshold: Minimum human_score to consider "successful"
        """
        self.db_path = Path(db_path)
        self.min_samples = min_samples
        self.success_threshold = success_threshold
        
        if not self.db_path.exists():
            logger.warning(f"Database not found: {db_path}")
        
        logger.info(
            f"[SWEET SPOT] Initialized "
            f"(min_samples={min_samples}, threshold={success_threshold}%)"
        )
    
    def find_sweet_spots(
        self,
        material: Optional[str] = None,
        component_type: Optional[str] = None,
        top_n_percent: int = 25
    ) -> Dict[str, SweetSpot]:
        """
        Find optimal parameter ranges based on top performing generations.
        
        Strategy:
        1. Get ALL successful generations (human_score >= threshold) - GENERIC LEARNING
        2. Take top N% by human_score
        3. Calculate parameter ranges from these top performers
        4. Return sweet spot ranges
        
        Args:
            material: IGNORED - learning is generic across all materials
            component_type: IGNORED - learning is generic across all components
            top_n_percent: Consider top N% of successful generations (default 25%)
            
        Returns:
            Dictionary of {parameter_name: SweetSpot}
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # Build query - NO material/component filtering (generic learning)
        query = """
            SELECT 
                gp.*,
                dr.human_score,
                dr.material,
                dr.component_type
            FROM generation_parameters gp
            JOIN detection_results dr ON gp.detection_result_id = dr.id
            WHERE dr.human_score >= ?
              AND dr.success = 1
            ORDER BY dr.human_score DESC
        """
        params = [self.success_threshold]
        
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < self.min_samples:
            logger.warning(
                f"[SWEET SPOT] Insufficient data: {len(rows)} samples "
                f"(need {self.min_samples})"
            )
            return {}
        
        # Take top N%
        top_n = max(self.min_samples, int(len(rows) * (top_n_percent / 100)))
        top_performers = rows[:top_n]
        
        logger.info(
            f"[SWEET SPOT] Analyzing {len(top_performers)} top performers "
            f"({top_n_percent}% of {len(rows)} successful generations)"
        )
        
        # Analyze each parameter
        sweet_spots = {}
        
        # Numeric parameters to analyze
        numeric_params = [
            'temperature',
            'frequency_penalty',
            'presence_penalty',
            'trait_frequency',
            'opinion_rate',
            'reader_address_rate',
            'colloquialism_frequency',
            'structural_predictability',
            'emotional_tone',
            'imperfection_tolerance',
            'sentence_rhythm_variation',
            'technical_intensity',
            'context_detail_level',
            'engagement_level',
            'detection_threshold',
            'grammar_strictness'
        ]
        
        for param_name in numeric_params:
            values = []
            human_scores = []
            
            for row in top_performers:
                if row[param_name] is not None:
                    values.append(float(row[param_name]))
                    human_scores.append(row['human_score'])
            
            if len(values) >= self.min_samples:
                sweet_spot = self._calculate_sweet_spot(
                    param_name,
                    values,
                    human_scores
                )
                sweet_spots[param_name] = sweet_spot
        
        return sweet_spots
    
    def _calculate_sweet_spot(
        self,
        param_name: str,
        values: List[float],
        human_scores: List[float]
    ) -> SweetSpot:
        """Calculate optimal range for a parameter."""
        # Statistical measures
        min_val = min(values)
        max_val = max(values)
        median_val = statistics.median(values)
        avg_score = statistics.mean(human_scores)
        
        # Confidence based on sample size and score variance
        sample_count = len(values)
        score_variance = statistics.stdev(human_scores) if len(human_scores) > 1 else 0
        
        if sample_count >= 20 and score_variance < 15:
            confidence = 'high'
        elif sample_count >= 10:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        return SweetSpot(
            parameter_name=param_name,
            optimal_min=round(min_val, 3),
            optimal_max=round(max_val, 3),
            optimal_median=round(median_val, 3),
            avg_human_score=round(avg_score, 2),
            sample_count=sample_count,
            confidence=confidence
        )
    
    def get_maximum_achievements(
        self,
        material: Optional[str] = None,
        component_type: Optional[str] = None,
        limit: int = 10
    ) -> List[MaximumAchievement]:
        """
        Get the highest human scores ever achieved.
        
        Returns list of MaximumAchievement objects with full parameter details.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        query = """
            SELECT 
                dr.material,
                dr.component_type,
                dr.human_score,
                dr.timestamp,
                dr.generated_text,
                gp.full_params_json,
                se.overall_score as claude_score
            FROM detection_results dr
            JOIN generation_parameters gp ON dr.id = gp.detection_result_id
            LEFT JOIN subjective_evaluations se 
                ON dr.material = se.topic 
                AND dr.component_type = se.component_type
                AND dr.timestamp = se.timestamp
            WHERE dr.success = 1
        """
        params = []
        
        if material:
            query += " AND dr.material = ?"
            params.append(material)
        
        if component_type:
            query += " AND dr.component_type = ?"
            params.append(component_type)
        
        query += " ORDER BY dr.human_score DESC LIMIT ?"
        params.append(limit)
        
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        achievements = []
        for row in rows:
            achievements.append(MaximumAchievement(
                material=row['material'],
                component_type=row['component_type'],
                max_human_score=row['human_score'],
                max_claude_score=row['claude_score'] if row['claude_score'] else None,
                achieved_at=row['timestamp'],
                parameters=json.loads(row['full_params_json']),
                generated_text=row['generated_text']
            ))
        
        return achievements
    
    def analyze_parameter_correlation(
        self,
        material: Optional[str] = None,
        component_type: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """
        Analyze which parameters correlate most with human_score.
        
        Returns:
            List of (parameter_name, correlation_strength) sorted by strength
            Correlation: -1.0 (negative) to +1.0 (positive)
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        query = """
            SELECT 
                gp.*,
                dr.human_score
            FROM generation_parameters gp
            JOIN detection_results dr ON gp.detection_result_id = dr.id
            WHERE dr.success = 1
        """
        params = []
        
        if material:
            query += " AND dr.material = ?"
            params.append(material)
        
        if component_type:
            query += " AND dr.component_type = ?"
            params.append(component_type)
        
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < self.min_samples:
            logger.warning(
                f"[CORRELATION] Insufficient data: {len(rows)} samples"
            )
            return []
        
        # Parameters to analyze
        numeric_params = [
            'temperature', 'frequency_penalty', 'presence_penalty',
            'trait_frequency', 'technical_intensity', 
            'imperfection_tolerance', 'sentence_rhythm_variation'
        ]
        
        correlations = []
        
        for param_name in numeric_params:
            param_values = []
            human_scores = []
            
            for row in rows:
                if row[param_name] is not None:
                    param_values.append(float(row[param_name]))
                    human_scores.append(row['human_score'])
            
            if len(param_values) >= self.min_samples:
                correlation = self._calculate_correlation(
                    param_values,
                    human_scores
                )
                correlations.append((param_name, correlation))
        
        # Sort by absolute correlation strength
        correlations.sort(key=lambda x: abs(x[1]), reverse=True)
        
        return correlations
    
    def _calculate_correlation(
        self,
        values1: List[float],
        values2: List[float]
    ) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(values1) != len(values2) or len(values1) < 2:
            return 0.0
        
        n = len(values1)
        
        # Calculate means
        mean1 = statistics.mean(values1)
        mean2 = statistics.mean(values2)
        
        # Calculate covariance and standard deviations
        covariance = sum((values1[i] - mean1) * (values2[i] - mean2) for i in range(n))
        
        std1 = statistics.stdev(values1)
        std2 = statistics.stdev(values2)
        
        if std1 == 0 or std2 == 0:
            return 0.0
        
        correlation = covariance / (n * std1 * std2)
        
        return round(correlation, 3)
    
    def get_sweet_spot_table(
        self,
        material: Optional[str] = None,
        component_type: Optional[str] = None,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive sweet spot analysis.
        
        Args:
            material: Filter by material
            component_type: Filter by component type
            save_to_db: If True, save results to sweet_spot_recommendations table
        
        Returns:
            Dictionary containing:
            - sweet_spots: Optimal parameter ranges
            - maximums: Best ever achievements
            - correlations: Parameter importance ranking
            - recommendations: Actionable suggestions
        """
        sweet_spots = self.find_sweet_spots(material, component_type)
        maximums = self.get_maximum_achievements(material, component_type, limit=5)
        correlations = self.analyze_parameter_correlation(material, component_type)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            sweet_spots,
            maximums,
            correlations
        )
        
        # Calculate statistics
        max_human_score = maximums[0].max_human_score if maximums else 0.0
        avg_human_score = sum(ss.avg_human_score for ss in sweet_spots.values()) / len(sweet_spots) if sweet_spots else 0.0
        sample_count = max(ss.sample_count for ss in sweet_spots.values()) if sweet_spots else 0
        
        # Determine overall confidence
        if sweet_spots:
            confidence_scores = {'high': 3, 'medium': 2, 'low': 1}
            avg_confidence_score = sum(confidence_scores[ss.confidence] for ss in sweet_spots.values()) / len(sweet_spots)
            if avg_confidence_score >= 2.5:
                overall_confidence = 'high'
            elif avg_confidence_score >= 1.5:
                overall_confidence = 'medium'
            else:
                overall_confidence = 'low'
        else:
            overall_confidence = 'low'
        
        result = {
            'sweet_spots': {k: v.to_dict() for k, v in sweet_spots.items()},
            'maximum_achievements': [m.to_dict() for m in maximums],
            'parameter_correlations': [
                {'parameter': name, 'correlation': corr}
                for name, corr in correlations
            ],
            'recommendations': recommendations,
            'metadata': {
                'material': material or 'all',
                'component_type': component_type or 'all',
                'sample_count': sample_count,
                'max_human_score': max_human_score,
                'avg_human_score': avg_human_score,
                'confidence_level': overall_confidence
            }
        }
        
        # Save to database if requested and we have specific material+component
        if save_to_db and material and component_type:
            try:
                from processing.detection.winston_feedback_db import WinstonFeedbackDatabase
                
                db = WinstonFeedbackDatabase(str(self.db_path))
                db.upsert_sweet_spot(
                    material=material,
                    component_type=component_type,
                    sweet_spots=sweet_spots,
                    correlations=result['parameter_correlations'],
                    max_human_score=max_human_score,
                    avg_human_score=avg_human_score,
                    sample_count=sample_count,
                    confidence=overall_confidence,
                    recommendations=recommendations
                )
                
                logger.info(
                    f"[SWEET SPOT] Saved to database: {material} {component_type} "
                    f"({sample_count} samples, {overall_confidence} confidence)"
                )
            except Exception as e:
                logger.warning(f"[SWEET SPOT] Failed to save to database: {e}")
        
        return result
    
    def _generate_recommendations(
        self,
        sweet_spots: Dict[str, SweetSpot],
        maximums: List[MaximumAchievement],
        correlations: List[Tuple[str, float]]
    ) -> List[str]:
        """Generate actionable recommendations from analysis."""
        recommendations = []
        
        # Check if we have enough data
        if not maximums:
            recommendations.append(
                "⚠️  Generate more content to build statistical baseline"
            )
            return recommendations
        
        # Best achievement recommendation
        best = maximums[0]
        recommendations.append(
            f"🏆 Best achievement: {best.max_human_score:.1f}% human "
            f"({best.material} {best.component_type})"
        )
        
        # Parameter correlations
        if correlations:
            top_positive = [c for c in correlations if c[1] > 0.3]
            top_negative = [c for c in correlations if c[1] < -0.3]
            
            if top_positive:
                params = ', '.join(c[0] for c in top_positive[:3])
                recommendations.append(
                    f"📈 Increase these for better scores: {params}"
                )
            
            if top_negative:
                params = ', '.join(c[0] for c in top_negative[:3])
                recommendations.append(
                    f"📉 Decrease these for better scores: {params}"
                )
        
        # Sweet spot recommendations
        if sweet_spots:
            high_confidence = [
                ss for ss in sweet_spots.values()
                if ss.confidence == 'high'
            ]
            
            if high_confidence:
                recommendations.append(
                    f"✅ {len(high_confidence)} parameters have high-confidence "
                    f"optimal ranges"
                )
        
        # Sample size recommendation
        total_samples = sum(ss.sample_count for ss in sweet_spots.values())
        if total_samples < 50:
            recommendations.append(
                f"⚡ Generate {50 - total_samples} more samples for better "
                f"statistical confidence"
            )
        
        return recommendations
