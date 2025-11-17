"""
Granular Parameter Correlator

Performs fine-grained correlation analysis between individual parameters
and quality metrics to enable precise parameter tuning and relationship discovery.

Key Features:
1. Per-parameter correlation coefficients with statistical significance
2. Non-linear relationship detection (polynomial, logarithmic)
3. Parameter interaction effects (2-way and 3-way)
4. Threshold detection (optimal ranges with diminishing returns)
5. Sensitivity analysis (impact of 1% parameter change)
6. Temporal trend analysis (parameter effectiveness over time)
"""

import sqlite3
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
import logging
from scipy import stats
from scipy.optimize import curve_fit
import json

logger = logging.getLogger(__name__)


@dataclass
class ParameterCorrelation:
    """Detailed correlation analysis for a single parameter."""
    parameter_name: str
    correlation_coefficient: float
    p_value: float
    strength: str  # 'very_strong', 'strong', 'moderate', 'weak', 'negligible'
    direction: str  # 'positive', 'negative', 'none'
    sample_count: int
    confidence_interval: Tuple[float, float]
    relationship_type: str  # 'linear', 'polynomial', 'logarithmic', 'exponential'
    optimal_range: Optional[Tuple[float, float]]
    sensitivity: float  # Change in score per 1% parameter change


@dataclass
class ParameterInteraction:
    """Interaction effect between two or three parameters."""
    parameters: List[str]
    interaction_strength: float
    combined_effect: float
    optimal_combination: Dict[str, float]
    sample_count: int


class GranularParameterCorrelator:
    """
    Highly granular parameter correlation analysis.
    
    Enables:
    - Precise parameter tuning (0.01 increments)
    - Relationship discovery (linear, non-linear, interactions)
    - Sensitivity analysis (impact per 1% change)
    - Optimal range identification
    - Statistical confidence tracking
    """
    
    # Parameter metadata for granular analysis
    PARAMETER_RANGES = {
        'temperature': (0.0, 2.0),
        'frequency_penalty': (0.0, 2.0),
        'presence_penalty': (0.0, 2.0),
        'trait_frequency': (0.0, 1.0),
        'opinion_rate': (0.0, 1.0),
        'reader_address_rate': (0.0, 1.0),
        'colloquialism_frequency': (0.0, 1.0),
        'structural_predictability': (0.0, 1.0),
        'emotional_tone': (0.0, 1.0),
        'imperfection_tolerance': (0.0, 1.0),
        'sentence_rhythm_variation': (0.0, 1.0),
        'technical_intensity': (1, 3),
        'context_detail_level': (1, 3),
        'engagement_level': (1, 3),
        'detection_threshold': (0.0, 1.0),
        'readability_min': (0.0, 100.0),
        'readability_max': (0.0, 100.0),
        'grammar_strictness': (0.0, 1.0),
        'confidence_high': (0.0, 1.0),
        'confidence_medium': (0.0, 1.0)
    }
    
    def __init__(
        self,
        db_path: str,
        min_samples: int = 30,
        significance_level: float = 0.05
    ):
        """
        Initialize granular correlator.
        
        Args:
            db_path: Path to Winston feedback database
            min_samples: Minimum samples for reliable correlation
            significance_level: P-value threshold for statistical significance
        """
        self.db_path = db_path
        self.min_samples = min_samples
        self.significance_level = significance_level
    
    def analyze_all_parameters(
        self,
        target_metric: str = 'composite_quality_score',
        min_score: float = 50.0
    ) -> Dict[str, ParameterCorrelation]:
        """
        Perform granular correlation analysis for ALL parameters.
        
        Args:
            target_metric: Metric to correlate against (composite_quality_score, human_score, etc)
            min_score: Minimum score threshold for inclusion
            
        Returns:
            Dict mapping parameter_name to ParameterCorrelation object
        """
        logger.info(f"Starting granular correlation analysis for {target_metric}")
        
        conn = sqlite3.connect(self.db_path)
        
        # Query all parameters and scores
        query = f"""
            SELECT 
                p.temperature, p.frequency_penalty, p.presence_penalty,
                p.trait_frequency, p.opinion_rate, p.reader_address_rate,
                p.colloquialism_frequency, p.structural_predictability, p.emotional_tone,
                p.imperfection_tolerance, p.sentence_rhythm_variation,
                p.technical_intensity, p.context_detail_level, p.engagement_level,
                p.detection_threshold, p.readability_min, p.readability_max,
                p.grammar_strictness, p.confidence_high, p.confidence_medium,
                r.{target_metric}
            FROM generation_parameters p
            JOIN detection_results r ON p.detection_result_id = r.id
            WHERE r.{target_metric} IS NOT NULL
              AND r.{target_metric} >= ?
              AND r.success = 1
        """
        
        cursor = conn.execute(query, (min_score,))
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < self.min_samples:
            logger.warning(
                f"Insufficient data: {len(rows)} samples (need {self.min_samples})"
            )
            return {}
        
        logger.info(f"Analyzing {len(rows)} samples")
        
        # Extract parameter data
        param_names = list(self.PARAMETER_RANGES.keys())
        param_data = {name: [] for name in param_names}
        scores = []
        
        for row in rows:
            for i, name in enumerate(param_names):
                if row[i] is not None:
                    param_data[name].append(row[i])
                else:
                    param_data[name].append(None)
            scores.append(row[-1])
        
        # Analyze each parameter
        correlations = {}
        for name in param_names:
            # Filter out None values
            valid_indices = [
                i for i, val in enumerate(param_data[name])
                if val is not None
            ]
            
            if len(valid_indices) < self.min_samples:
                logger.debug(f"Skipping {name}: only {len(valid_indices)} samples")
                continue
            
            param_values = [param_data[name][i] for i in valid_indices]
            score_values = [scores[i] for i in valid_indices]
            
            correlation = self._analyze_parameter(
                name,
                param_values,
                score_values
            )
            
            if correlation:
                correlations[name] = correlation
                logger.info(
                    f"{name}: {correlation.correlation_coefficient:+.3f} "
                    f"({correlation.strength}, p={correlation.p_value:.4f})"
                )
        
        return correlations
    
    def _analyze_parameter(
        self,
        param_name: str,
        param_values: List[float],
        score_values: List[float]
    ) -> Optional[ParameterCorrelation]:
        """
        Perform detailed analysis for single parameter.
        
        Returns:
            ParameterCorrelation object with all granular details
        """
        # Convert to numpy arrays
        x = np.array(param_values)
        y = np.array(score_values)
        n = len(x)
        
        # Check for constant values (no variation)
        if np.std(x) == 0 or np.std(y) == 0:
            logger.debug(f"{param_name}: No variation in parameter or scores")
            return None
        
        # 1. Spearman correlation (handles non-linear relationships)
        try:
            spearman_corr, spearman_p = stats.spearmanr(x, y)
        except Exception:
            logger.debug(f"{param_name}: Failed to calculate Spearman correlation")
            return None
        
        # 2. Pearson correlation (linear relationships)
        try:
            pearson_corr, _ = stats.pearsonr(x, y)
        except Exception:
            pearson_corr = spearman_corr
        
        # Check for NaN
        if np.isnan(spearman_corr) or np.isnan(spearman_p):
            logger.debug(f"{param_name}: NaN in correlation results")
            return None
        
        # Use Spearman as primary (more robust)
        corr = spearman_corr
        p_value = spearman_p
        
        # Check statistical significance
        if p_value >= self.significance_level:
            logger.debug(f"{param_name}: Not significant (p={p_value:.4f})")
            return None
        
        # 3. Determine relationship strength and direction
        strength = self._interpret_correlation_strength(abs(corr))
        direction = 'positive' if corr > 0 else ('negative' if corr < 0 else 'none')
        
        # 4. Calculate confidence interval (bootstrap method)
        confidence_interval = self._calculate_confidence_interval(x, y)
        
        # 5. Detect relationship type (linear vs non-linear)
        relationship_type = self._detect_relationship_type(x, y, pearson_corr)
        
        # 6. Find optimal range (if non-linear)
        optimal_range = self._find_optimal_range(x, y, param_name)
        
        # 7. Calculate sensitivity (score change per 1% parameter change)
        sensitivity = self._calculate_sensitivity(x, y, param_name)
        
        return ParameterCorrelation(
            parameter_name=param_name,
            correlation_coefficient=corr,
            p_value=p_value,
            strength=strength,
            direction=direction,
            sample_count=n,
            confidence_interval=confidence_interval,
            relationship_type=relationship_type,
            optimal_range=optimal_range,
            sensitivity=sensitivity
        )
    
    def _interpret_correlation_strength(self, abs_corr: float) -> str:
        """Interpret correlation coefficient strength."""
        if abs_corr >= 0.7:
            return 'very_strong'
        elif abs_corr >= 0.5:
            return 'strong'
        elif abs_corr >= 0.3:
            return 'moderate'
        elif abs_corr >= 0.1:
            return 'weak'
        else:
            return 'negligible'
    
    def _calculate_confidence_interval(
        self,
        x: np.ndarray,
        y: np.ndarray,
        n_bootstrap: int = 1000
    ) -> Tuple[float, float]:
        """Calculate 95% confidence interval using bootstrap."""
        bootstrap_corrs = []
        n = len(x)
        
        for _ in range(n_bootstrap):
            indices = np.random.choice(n, n, replace=True)
            boot_x = x[indices]
            boot_y = y[indices]
            try:
                corr, _ = stats.spearmanr(boot_x, boot_y)
                bootstrap_corrs.append(corr)
            except Exception:
                continue
        
        if len(bootstrap_corrs) < 100:
            return (-1.0, 1.0)
        
        lower = np.percentile(bootstrap_corrs, 2.5)
        upper = np.percentile(bootstrap_corrs, 97.5)
        
        return (round(lower, 3), round(upper, 3))
    
    def _detect_relationship_type(
        self,
        x: np.ndarray,
        y: np.ndarray,
        pearson_corr: float
    ) -> str:
        """
        Detect if relationship is linear or non-linear.
        
        Tests polynomial and logarithmic fits.
        """
        # Linear R²
        linear_r2 = pearson_corr ** 2
        
        # Try polynomial fit (degree 2)
        try:
            poly_coeffs = np.polyfit(x, y, 2)
            poly_pred = np.polyval(poly_coeffs, x)
            poly_r2 = 1 - (np.sum((y - poly_pred)**2) / np.sum((y - np.mean(y))**2))
            
            # If polynomial is significantly better (>5% improvement)
            if poly_r2 > linear_r2 + 0.05:
                return 'polynomial'
        except Exception:
            pass
        
        # Try logarithmic fit
        try:
            if np.all(x > 0):
                log_x = np.log(x)
                log_corr, _ = stats.pearsonr(log_x, y)
                log_r2 = log_corr ** 2
                
                if log_r2 > linear_r2 + 0.05:
                    return 'logarithmic'
        except Exception:
            pass
        
        return 'linear'
    
    def _find_optimal_range(
        self,
        x: np.ndarray,
        y: np.ndarray,
        param_name: str
    ) -> Optional[Tuple[float, float]]:
        """
        Find optimal parameter range using percentile analysis.
        
        Identifies range where scores are consistently high.
        """
        if len(x) < 20:
            return None
        
        # Sort by parameter value
        sorted_indices = np.argsort(x)
        x_sorted = x[sorted_indices]
        y_sorted = y[sorted_indices]
        
        # Use sliding window to find best performing range
        window_size = max(10, len(x) // 5)
        best_avg_score = -np.inf
        best_range = None
        
        for i in range(len(x) - window_size + 1):
            window_scores = y_sorted[i:i+window_size]
            avg_score = np.mean(window_scores)
            
            if avg_score > best_avg_score:
                best_avg_score = avg_score
                best_range = (
                    round(float(x_sorted[i]), 3),
                    round(float(x_sorted[i+window_size-1]), 3)
                )
        
        return best_range
    
    def _calculate_sensitivity(
        self,
        x: np.ndarray,
        y: np.ndarray,
        param_name: str
    ) -> float:
        """
        Calculate score sensitivity to 1% parameter change.
        
        Uses linear regression slope scaled to parameter range.
        """
        try:
            # Linear regression
            slope, intercept = np.polyfit(x, y, 1)
            
            # Get parameter range
            param_range = self.PARAMETER_RANGES.get(param_name, (0, 1))
            range_size = param_range[1] - param_range[0]
            
            # Sensitivity = slope * 1% of range
            sensitivity = slope * (range_size * 0.01)
            
            return round(sensitivity, 4)
        except Exception:
            return 0.0
    
    def analyze_interactions(
        self,
        correlations: Dict[str, ParameterCorrelation],
        max_interactions: int = 10
    ) -> List[ParameterInteraction]:
        """
        Analyze 2-way parameter interactions.
        
        Identifies parameter combinations with synergistic effects.
        """
        logger.info("Analyzing parameter interactions")
        
        # Get top correlated parameters
        sorted_params = sorted(
            correlations.items(),
            key=lambda x: abs(x[1].correlation_coefficient),
            reverse=True
        )[:10]  # Top 10 parameters
        
        interactions = []
        
        # Analyze all pairs
        for i, (name1, corr1) in enumerate(sorted_params):
            for name2, corr2 in sorted_params[i+1:]:
                interaction = self._analyze_pair_interaction(
                    name1, name2, corr1, corr2
                )
                if interaction:
                    interactions.append(interaction)
        
        # Sort by interaction strength
        interactions.sort(key=lambda x: abs(x.interaction_strength), reverse=True)
        
        return interactions[:max_interactions]
    
    def _analyze_pair_interaction(
        self,
        param1: str,
        param2: str,
        corr1: ParameterCorrelation,
        corr2: ParameterCorrelation
    ) -> Optional[ParameterInteraction]:
        """
        Analyze interaction between two parameters.
        
        Uses multiple regression to detect interaction effects.
        """
        conn = sqlite3.connect(self.db_path)
        
        query = f"""
            SELECT 
                p.{param1}, p.{param2}, r.composite_quality_score
            FROM generation_parameters p
            JOIN detection_results r ON p.detection_result_id = r.id
            WHERE r.composite_quality_score IS NOT NULL
              AND p.{param1} IS NOT NULL
              AND p.{param2} IS NOT NULL
              AND r.success = 1
        """
        
        cursor = conn.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < self.min_samples:
            return None
        
        # Extract data
        x1 = np.array([row[0] for row in rows])
        x2 = np.array([row[1] for row in rows])
        y = np.array([row[2] for row in rows])
        
        # Calculate individual effects
        ind_effect1 = np.corrcoef(x1, y)[0, 1]
        ind_effect2 = np.corrcoef(x2, y)[0, 1]
        
        # Calculate combined effect (interaction term)
        interaction_term = x1 * x2
        combined_corr, p_value = stats.spearmanr(interaction_term, y)
        
        # Only report if interaction is significant
        if p_value >= self.significance_level:
            return None
        
        # Find optimal combination (highest average scores)
        # Grid search in top quartiles
        q1_high = np.percentile(x1, 75)
        q2_high = np.percentile(x2, 75)
        
        high_indices = (x1 >= q1_high) & (x2 >= q2_high)
        if np.sum(high_indices) > 5:
            optimal_combination = {
                param1: round(float(np.mean(x1[high_indices])), 3),
                param2: round(float(np.mean(x2[high_indices])), 3)
            }
        else:
            optimal_combination = {}
        
        return ParameterInteraction(
            parameters=[param1, param2],
            interaction_strength=combined_corr,
            combined_effect=combined_corr - (ind_effect1 + ind_effect2) / 2,
            optimal_combination=optimal_combination,
            sample_count=len(rows)
        )
    
    def generate_adjustment_recommendations(
        self,
        correlations: Dict[str, ParameterCorrelation],
        current_params: Dict[str, float],
        target_improvement: float = 5.0
    ) -> List[Dict[str, Any]]:
        """
        Generate granular parameter adjustment recommendations.
        
        Args:
            correlations: Parameter correlation analysis results
            current_params: Current parameter values
            target_improvement: Target score improvement (points)
            
        Returns:
            List of recommendations sorted by expected impact
        """
        recommendations = []
        
        for name, corr in correlations.items():
            if name not in current_params:
                continue
            
            current_value = current_params[name]
            param_range = self.PARAMETER_RANGES.get(name, (0, 1))
            
            # Calculate recommended adjustment based on sensitivity
            if corr.sensitivity != 0:
                # How much to change parameter to achieve target improvement
                required_change = target_improvement / corr.sensitivity
                
                # Limit change to 10% of parameter range per iteration
                max_change = (param_range[1] - param_range[0]) * 0.1
                recommended_change = np.clip(required_change, -max_change, max_change)
                
                # Apply direction
                if corr.direction == 'negative':
                    recommended_change = -recommended_change
                
                new_value = np.clip(
                    current_value + recommended_change,
                    param_range[0],
                    param_range[1]
                )
                
                # Calculate expected impact
                expected_impact = abs(new_value - current_value) * corr.sensitivity
                
                recommendations.append({
                    'parameter': name,
                    'current_value': round(current_value, 3),
                    'recommended_value': round(new_value, 3),
                    'change': round(new_value - current_value, 3),
                    'expected_impact': round(expected_impact, 2),
                    'confidence': 1 - corr.p_value,
                    'correlation_strength': corr.strength,
                    'optimal_range': corr.optimal_range,
                    'reasoning': self._generate_reasoning(corr, current_value)
                })
        
        # Sort by expected impact
        recommendations.sort(key=lambda x: x['expected_impact'], reverse=True)
        
        return recommendations
    
    def _generate_reasoning(
        self,
        corr: ParameterCorrelation,
        current_value: float
    ) -> str:
        """Generate human-readable reasoning for recommendation."""
        direction_word = "Increase" if corr.direction == 'positive' else "Decrease"
        
        reasoning = f"{direction_word} {corr.parameter_name} "
        reasoning += f"({corr.strength} {corr.correlation_coefficient:+.3f} correlation). "
        
        if corr.optimal_range:
            if not (corr.optimal_range[0] <= current_value <= corr.optimal_range[1]):
                reasoning += f"Optimal range: {corr.optimal_range[0]:.3f}-{corr.optimal_range[1]:.3f}. "
        
        reasoning += f"Expected: {abs(corr.sensitivity):.2f} points per 1% change."
        
        return reasoning
