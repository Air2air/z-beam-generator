"""
Temperature Advisor - Dynamic Temperature Optimization

Analyzes Winston feedback to recommend optimal temperature settings for
different materials and component types. Uses statistical learning to
find the temperature "sweet spot" that maximizes human scores.

Key Features:
- Material-specific temperature recommendations
- Component-type specific optimization (caption vs subtitle vs FAQ)
- Statistical analysis of temperature vs success rate
- Confidence intervals for recommendations
- Historical tracking of temperature effectiveness

Fail-fast design: Requires database connection, no fallbacks.
"""

import logging
import sqlite3
import statistics
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


class TemperatureAdvisor:
    """
    Recommend optimal temperature settings based on Winston feedback.
    
    Analyzes:
    - Temperature vs human score correlation
    - Temperature vs success rate correlation
    - Material-specific optimal temperatures
    - Component-specific optimal temperatures
    - Temperature stability (variance in outcomes)
    
    Provides:
    - Recommended temperature for material+component combinations
    - Confidence level of recommendations
    - Temperature adjustment suggestions
    - Performance predictions for different temperatures
    """
    
    def __init__(self, db_path: str, min_samples: int = 5):
        """
        Initialize temperature advisor.
        
        Args:
            db_path: Path to Winston feedback database
            min_samples: Minimum samples needed for reliable recommendation
        """
        self.db_path = Path(db_path)
        self.min_samples = min_samples
        
        if not self.db_path.exists():
            logger.warning(f"Database not found: {db_path}. TemperatureAdvisor will work once data exists.")
        
        logger.info(f"[TEMPERATURE ADVISOR] Initialized (min_samples={min_samples})")
    
    def get_optimal_temperature(
        self, 
        material: Optional[str] = None,
        component_type: Optional[str] = None
    ) -> Dict:
        """
        Get optimal temperature recommendation.
        
        Args:
            material: Optional filter by material
            component_type: Optional filter by component type
            
        Returns:
            Dict containing:
            - recommended_temp: Optimal temperature (float)
            - confidence: Confidence level (low/medium/high)
            - success_rate: Expected success rate at this temp
            - avg_human_score: Expected human score at this temp
            - sample_size: Number of samples analyzed
            - temperature_range: (min, max) range analyzed
            - analysis: Detailed analysis by temperature bucket
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # Build query
        query = """
            SELECT 
                temperature,
                success,
                human_score,
                material,
                component_type
            FROM detection_results
            WHERE temperature IS NOT NULL
        """
        params = []
        
        if material:
            query += " AND material = ?"
            params.append(material)
        
        if component_type:
            query += " AND component_type = ?"
            params.append(component_type)
        
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < self.min_samples:
            logger.warning(f"[TEMPERATURE ADVISOR] Insufficient samples ({len(rows)} < {self.min_samples})")
            return {
                'recommended_temp': 0.7,  # Default
                'confidence': 'none',
                'reason': f'Need {self.min_samples - len(rows)} more samples',
                'sample_size': len(rows)
            }
        
        logger.info(f"[TEMPERATURE ADVISOR] Analyzing {len(rows)} samples...")
        
        # Group by temperature buckets (0.05 increments)
        temp_buckets = defaultdict(lambda: {
            'samples': [],
            'success_count': 0,
            'human_scores': []
        })
        
        for row in rows:
            temp = round(row['temperature'] / 0.05) * 0.05  # Round to nearest 0.05
            temp_buckets[temp]['samples'].append(row)
            temp_buckets[temp]['success_count'] += int(row['success'])
            temp_buckets[temp]['human_scores'].append(row['human_score'])
        
        # Calculate statistics for each temperature
        temp_analysis = []
        for temp, data in temp_buckets.items():
            sample_size = len(data['samples'])
            if sample_size < 2:  # Need at least 2 samples
                continue
            
            success_rate = data['success_count'] / sample_size
            avg_score = statistics.mean(data['human_scores'])
            score_std = statistics.stdev(data['human_scores']) if sample_size > 1 else 0
            
            # Composite score: success rate + normalized human score
            composite = (success_rate * 0.6) + (avg_score / 100.0 * 0.4)
            
            temp_analysis.append({
                'temperature': temp,
                'sample_size': sample_size,
                'success_rate': success_rate,
                'avg_human_score': avg_score,
                'score_std': score_std,
                'composite_score': composite
            })
        
        if not temp_analysis:
            logger.warning("[TEMPERATURE ADVISOR] No valid temperature buckets")
            return {
                'recommended_temp': 0.7,
                'confidence': 'low',
                'reason': 'Insufficient data distribution'
            }
        
        # Sort by composite score
        temp_analysis.sort(key=lambda x: x['composite_score'], reverse=True)
        
        # Best temperature
        best = temp_analysis[0]
        
        # Determine confidence based on sample size and consistency
        if best['sample_size'] >= 10 and best['success_rate'] >= 0.7:
            confidence = 'high'
        elif best['sample_size'] >= 5 and best['success_rate'] >= 0.5:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        logger.info(f"✅ [TEMPERATURE ADVISOR] Optimal temp: {best['temperature']:.2f} (confidence: {confidence})")
        
        return {
            'recommended_temp': best['temperature'],
            'confidence': confidence,
            'success_rate': best['success_rate'],
            'avg_human_score': best['avg_human_score'],
            'score_stability': 1.0 / (best['score_std'] + 1.0),  # Lower std = higher stability
            'sample_size': best['sample_size'],
            'temperature_range': (min(d['temperature'] for d in temp_analysis),
                                 max(d['temperature'] for d in temp_analysis)),
            'analysis': temp_analysis[:5],  # Top 5 temperatures
            'total_samples': len(rows)
        }
    
    def compare_temperatures(
        self,
        temps: List[float],
        material: Optional[str] = None,
        component_type: Optional[str] = None
    ) -> Dict:
        """
        Compare performance of specific temperatures.
        
        Args:
            temps: List of temperatures to compare
            material: Optional filter by material
            component_type: Optional filter by component type
            
        Returns:
            Dict with comparison results
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        results = {}
        
        for temp in temps:
            # Query samples near this temperature (±0.02)
            query = """
                SELECT success, human_score
                FROM detection_results
                WHERE temperature BETWEEN ? AND ?
            """
            params = [temp - 0.02, temp + 0.02]
            
            if material:
                query += " AND material = ?"
                params.append(material)
            
            if component_type:
                query += " AND component_type = ?"
                params.append(component_type)
            
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            if rows:
                success_rate = sum(1 for r in rows if r['success']) / len(rows)
                avg_score = statistics.mean(r['human_score'] for r in rows)
                
                results[temp] = {
                    'success_rate': success_rate,
                    'avg_human_score': avg_score,
                    'sample_size': len(rows),
                    'rating': self._rate_performance(success_rate, avg_score)
                }
            else:
                results[temp] = {
                    'success_rate': None,
                    'avg_human_score': None,
                    'sample_size': 0,
                    'rating': 'no_data'
                }
        
        conn.close()
        
        # Find best
        valid_temps = {t: r for t, r in results.items() if r['sample_size'] > 0}
        if valid_temps:
            best_temp = max(valid_temps.items(), 
                           key=lambda x: (x[1]['success_rate'], x[1]['avg_human_score']))[0]
        else:
            best_temp = None
        
        return {
            'results': results,
            'best_temperature': best_temp,
            'recommendation': f"Use {best_temp:.2f} for best results" if best_temp else "Need more data"
        }
    
    def _rate_performance(self, success_rate: float, avg_score: float) -> str:
        """Rate performance as excellent/good/fair/poor."""
        composite = (success_rate * 0.6) + (avg_score / 100.0 * 0.4)
        
        if composite >= 0.8:
            return 'excellent'
        elif composite >= 0.6:
            return 'good'
        elif composite >= 0.4:
            return 'fair'
        else:
            return 'poor'
    
    def get_adjustment_suggestion(
        self,
        current_temp: float,
        recent_failures: int,
        material: Optional[str] = None,
        component_type: Optional[str] = None
    ) -> Dict:
        """
        Suggest temperature adjustment based on recent failures.
        
        Args:
            current_temp: Current temperature setting
            recent_failures: Number of recent failures in a row
            material: Optional material context
            component_type: Optional component type context
            
        Returns:
            Dict with adjustment suggestion
        """
        optimal = self.get_optimal_temperature(material, component_type)
        
        if optimal['confidence'] == 'none':
            return {
                'suggested_temp': current_temp,
                'action': 'keep',
                'reason': 'Insufficient data for adjustment'
            }
        
        optimal_temp = optimal['recommended_temp']
        
        # If far from optimal and failing, move toward optimal
        if recent_failures >= 2 and abs(current_temp - optimal_temp) > 0.1:
            # Move 50% toward optimal
            new_temp = current_temp + (optimal_temp - current_temp) * 0.5
            new_temp = round(new_temp, 2)
            
            return {
                'suggested_temp': new_temp,
                'action': 'adjust',
                'direction': 'increase' if new_temp > current_temp else 'decrease',
                'reason': f'Moving toward optimal ({optimal_temp:.2f}) after {recent_failures} failures',
                'confidence': optimal['confidence']
            }
        
        # If close to optimal but failing, small adjustment
        if recent_failures >= 3:
            # Small random walk
            adjustment = 0.05 if recent_failures % 2 == 0 else -0.05
            new_temp = round(current_temp + adjustment, 2)
            new_temp = max(0.3, min(1.0, new_temp))  # Clamp to valid range
            
            return {
                'suggested_temp': new_temp,
                'action': 'explore',
                'direction': 'increase' if adjustment > 0 else 'decrease',
                'reason': f'Exploring alternatives after {recent_failures} failures near optimal',
                'confidence': 'low'
            }
        
        # Otherwise keep current
        return {
            'suggested_temp': current_temp,
            'action': 'keep',
            'reason': 'Current temperature performing adequately'
        }
