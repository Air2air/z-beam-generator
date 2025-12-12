"""
Weight Learner

Dynamically learns optimal quality metric weights from historical correlation data.
Similar architecture to TemperatureAdvisor - uses database analysis to find
weights that maximize prediction accuracy.

Core Principle:
Weights should NOT be hardcoded or static config. They should be learned from
historical data showing which metric combinations best predict actual success.

UNIVERSAL WEIGHTS:
Weights are the SAME for all materials and components. Quality is quality
regardless of context. System learns ONE optimal weight set.

Why Universal?
- Good writing is universal (not material-specific)
- Winston measures AI detection (applies to all text)
- Subjective scores use universal quality standards
- Content must be generic and reusable

Learning Strategy:
1. Analyze ALL historical generations from database
2. Calculate correlation between each metric and final success
3. Optimize weights to maximize composite score prediction accuracy
4. Update continuously based on new feedback
"""

import sqlite3
import numpy as np
from typing import Dict, Optional, Tuple, List
from pathlib import Path
from dataclasses import dataclass
import logging
from scipy.optimize import minimize
from scipy import stats

logger = logging.getLogger(__name__)


@dataclass
class WeightSet:
    """Learned weight configuration for quality metrics."""
    winston_weight: float
    subjective_weight: float
    readability_weight: float
    sample_count: int
    prediction_accuracy: float  # R² score
    context: str  # "global", "material:Steel", "component:micro"


class WeightLearner:
    """
    Learn optimal quality metric weights from historical success patterns.
    
    Uses correlation analysis and optimization to find weight combinations
    that maximize prediction accuracy of final generation success.
    
    UNIVERSAL WEIGHTS:
    Weights are NOT context-specific. Quality is quality regardless of
    material or component type. The system learns ONE optimal weight set
    that works across all content types.
    
    Why Universal?
    - Good writing is good writing (material-independent)
    - Winston scores measure AI detection (not material quality)
    - Subjective scores measure content quality (universal standards)
    - Readability is universal (Flesch-Kincaid applies to all text)
    
    Continuously adapts as new generations provide more correlation data.
    """
    
    # Minimum samples needed for reliable weight learning
    MIN_GLOBAL_SAMPLES = 110  # Need 110+ generations for learned weights
    
    # Default fallback weights (used only if insufficient data)
    DEFAULT_WEIGHTS = {
        'winston_weight': 0.6,
        'subjective_weight': 0.3,
        'readability_weight': 0.1
    }
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize weight learner with database connection.
        
        Args:
            db_path: Path to SQLite database (default: processing/learning/data/learning.db)
        """
        if db_path is None:
            db_path = Path(__file__).parent / "data" / "learning.db"
        
        self.db_path = db_path
        self._ensure_database()
        
        # Cache for learned weights to avoid repeated DB queries
        self._weight_cache: Dict[str, WeightSet] = {}
        
        logger.info(f"WeightLearner initialized with database: {db_path}")
    
    def _ensure_database(self):
        """Verify database exists and has required tables."""
        if not self.db_path.exists():
            logger.warning(
                f"Learning database not found at {self.db_path}. "
                "Will use default weights until data available."
            )
    
    def get_optimal_weights(self) -> Tuple[float, float, float]:
        """
        Get optimal weights learned from historical data.
        
        Weights are UNIVERSAL - not context-specific. Good writing is good writing
        regardless of material or component type. The system learns ONE optimal
        weight set that maximizes prediction accuracy across all generations.
        
        Returns:
            Tuple of (winston_weight, subjective_weight, readability_weight)
        """
        # Try global learned weights
        global_weights = self._get_global_weights()
        if global_weights:
            return (global_weights.winston_weight, global_weights.subjective_weight, global_weights.readability_weight)
        
        # Fallback to defaults if insufficient data
        logger.warning(
            "Insufficient data for weight learning. Using default weights. "
            f"Need {self.MIN_GLOBAL_SAMPLES}+ generations for learning."
        )
        return (
            self.DEFAULT_WEIGHTS['winston_weight'],
            self.DEFAULT_WEIGHTS['subjective_weight'],
            self.DEFAULT_WEIGHTS['readability_weight']
        )
    
    def _get_global_weights(self) -> Optional[WeightSet]:
        """
        Get global learned weights (all materials/components).
        
        Returns:
            WeightSet if sufficient data, None otherwise
        """
        cache_key = "global"
        
        # Check cache
        if cache_key in self._weight_cache:
            return self._weight_cache[cache_key]
        
        # Learn from all data
        weights = self._learn_weights_from_data()
        
        if weights and weights.sample_count >= self.MIN_GLOBAL_SAMPLES:
            self._weight_cache[cache_key] = weights
            logger.info(
                f"Learned global weights: "
                f"winston={weights.winston_weight:.2f}, "
                f"subjective={weights.subjective_weight:.2f}, "
                f"readability={weights.readability_weight:.2f} "
                f"(n={weights.sample_count}, R²={weights.prediction_accuracy:.3f})"
            )
            return weights
        
        return None
    
    def _learn_weights_from_data(self) -> Optional[WeightSet]:
        """
        Learn optimal weights by analyzing historical correlation data.
        
        Strategy:
        1. Fetch ALL historical generations (no material/component filtering)
        2. Calculate correlation between each metric and success
        3. Use optimization to find weights maximizing prediction accuracy
        4. Validate weights sum to 1.0 and are all positive
        
        Weights are UNIVERSAL - quality is quality regardless of context.
        
        Returns:
            WeightSet with optimized weights, or None if insufficient data
        """
        if not self.db_path.exists():
            return None
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Query ALL generations (no filtering by material/component)
            query = """
                SELECT 
                    r.human_score as winston,
                    r.subjective_overall_score as subjective,
                    r.readability_score as readability,
                    r.success as actual_success
                FROM generation_results r
                WHERE r.human_score IS NOT NULL
                    AND r.subjective_overall_score IS NOT NULL
                    AND r.readability_score IS NOT NULL
                    AND r.success IS NOT NULL
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
            
            if len(rows) < self.MIN_GLOBAL_SAMPLES:
                return None
            
            # Convert to numpy arrays
            winston_scores = np.array([r[0] for r in rows])
            subjective_scores = np.array([r[1] for r in rows])
            readability_scores = np.array([r[2] for r in rows])
            actual_success = np.array([r[3] for r in rows])
            
            # Normalize scores to 0-1 range for fair comparison
            winston_norm = winston_scores / 100.0
            subjective_norm = subjective_scores / 10.0  # Subjective is 0-10 scale
            readability_norm = readability_scores / 100.0
            
            # Optimization objective: find weights that maximize prediction accuracy
            def objective(weights):
                """
                Calculate prediction error for given weights.
                Lower error = better weights.
                """
                w_winston, w_subjective, w_readability = weights
                
                # Calculate composite predictions
                predictions = (
                    w_winston * winston_norm +
                    w_subjective * subjective_norm +
                    w_readability * readability_norm
                )
                
                # Calculate mean squared error
                mse = np.mean((predictions - actual_success) ** 2)
                return mse
            
            # Constraints: weights must sum to 1.0 and be positive
            constraints = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}  # Sum to 1.0
            ]
            bounds = [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0)]  # Each weight 0-1
            
            # Initial guess (current defaults)
            initial_weights = [
                self.DEFAULT_WEIGHTS['winston_weight'],
                self.DEFAULT_WEIGHTS['subjective_weight'],
                self.DEFAULT_WEIGHTS['readability_weight']
            ]
            
            # Optimize
            result = minimize(
                objective,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'maxiter': 100}
            )
            
            if not result.success:
                logger.warning(f"Weight optimization failed: {result.message}")
                return None
            
            optimal_weights = result.x
            
            # Calculate R² (prediction accuracy)
            predictions = (
                optimal_weights[0] * winston_norm +
                optimal_weights[1] * subjective_norm +
                optimal_weights[2] * readability_norm
            )
            ss_res = np.sum((actual_success - predictions) ** 2)
            ss_tot = np.sum((actual_success - np.mean(actual_success)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            # Context is always "global" - no material/component specificity
            return WeightSet(
                winston_weight=float(optimal_weights[0]),
                subjective_weight=float(optimal_weights[1]),
                readability_weight=float(optimal_weights[2]),
                sample_count=len(rows),
                prediction_accuracy=float(r_squared),
                context="global"
            )
            
        except sqlite3.Error as e:
            logger.error(f"Database error learning weights: {e}")
            return None
        except Exception as e:
            logger.error(f"Error learning weights: {e}", exc_info=True)
            return None
    
    def invalidate_cache(self):
        """
        Clear weight cache to force relearning from updated data.
        Call this after new generations are added to database.
        """
        self._weight_cache.clear()
        logger.info("Weight cache cleared - will relearn from fresh data")
    
    def get_weight_statistics(self) -> Dict[str, any]:
        """
        Get statistics about learned weights across all contexts.
        
        Returns:
            Dict with weight statistics and learning status
        """
        if not self.db_path.exists():
            return {
                'status': 'no_database',
                'message': 'Learning database not found'
            }
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Count total samples
            cursor.execute("""
                SELECT COUNT(*) 
                FROM generation_results 
                WHERE human_score IS NOT NULL 
                    AND subjective_overall_score IS NOT NULL
                    AND readability_score IS NOT NULL
                    AND success IS NOT NULL
            """)
            total_samples = cursor.fetchone()[0]
            
            conn.close()
            
            # Determine learning readiness
            can_learn_global = total_samples >= self.MIN_GLOBAL_SAMPLES
            
            return {
                'status': 'ready' if can_learn_global else 'insufficient_data',
                'total_samples': total_samples,
                'min_required': self.MIN_GLOBAL_SAMPLES,
                'can_learn': can_learn_global,
                'cached_weight_sets': len(self._weight_cache)
            }
            
        except sqlite3.Error as e:
            logger.error(f"Database error getting statistics: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
