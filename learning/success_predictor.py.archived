"""
Success Predictor - Predict Generation Success Before Running Winston

Uses machine learning on historical Winston feedback to predict:
1. Likelihood of passing Winston detection (before generating)
2. Expected human score range
3. Optimal generation parameters (temperature, length, etc.)
4. Risk assessment for material+component combinations

This enables:
- Smart retry decisions (skip if predicted to fail)
- Cost savings (avoid Winston API calls for predicted failures)
- Parameter optimization (use settings most likely to succeed)
- Risk warnings (alert when material/component combo has low success rate)

Fail-fast design: Requires database with sufficient samples.
"""

import logging
import sqlite3
import statistics
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict
import math

logger = logging.getLogger(__name__)


class SuccessPredictor:
    """
    Predict content generation success based on historical Winston feedback.
    
    Uses statistical models trained on:
    - Material success rates
    - Component type success rates  
    - Temperature effectiveness
    - Word count correlations
    - Attempt number patterns
    
    Provides:
    - Success probability prediction
    - Expected human score prediction
    - Confidence intervals
    - Parameter recommendations
    - Risk assessments
    """
    
    def __init__(self, db_path: str, min_samples: int = 10):
        """
        Initialize success predictor.
        
        Args:
            db_path: Path to Winston feedback database
            min_samples: Minimum samples needed for reliable predictions
        """
        self.db_path = Path(db_path)
        self.min_samples = min_samples
        
        # Cache for frequently accessed data
        self._cache = {}
        
        if not self.db_path.exists():
            logger.warning(f"Database not found: {db_path}. SuccessPredictor will work once data exists.")
        
        logger.info(f"[SUCCESS PREDICTOR] Initialized (min_samples={min_samples})")
    
    def predict_success(
        self,
        material: str,
        component_type: str,
        temperature: float,
        attempt_number: int = 1
    ) -> Dict:
        """
        Predict likelihood of generating successful content.
        
        Args:
            material: Material name
            component_type: Component type (caption/subtitle/faq)
            temperature: Generation temperature
            attempt_number: Which attempt this will be
            
        Returns:
            Dict containing:
            - success_probability: 0.0-1.0 probability of passing Winston
            - expected_human_score: Predicted human score (0-100)
            - confidence: Prediction confidence (high/medium/low/none)
            - recommendation: 'proceed' or 'skip' or 'adjust'
            - reasoning: Explanation of prediction
            - suggested_adjustments: List of parameter suggestions
        """
        # Build prediction from multiple models
        
        # Model 1: Material-specific success rate
        material_model = self._get_material_success_rate(material, component_type)
        
        # Model 2: Component type success rate
        component_model = self._get_component_success_rate(component_type)
        
        # Model 3: Temperature effectiveness
        temp_model = self._get_temperature_effectiveness(temperature, material, component_type)
        
        # Model 4: Attempt number pattern
        attempt_model = self._get_attempt_success_pattern(attempt_number, material, component_type)
        
        # Combine models (weighted average)
        models = [material_model, component_model, temp_model, attempt_model]
        valid_models = [m for m in models if m['valid']]
        
        if not valid_models:
            logger.warning("[SUCCESS PREDICTOR] No valid models - insufficient data")
            return {
                'success_probability': 0.5,  # Unknown - assume 50/50
                'expected_human_score': 50.0,
                'confidence': 'none',
                'recommendation': 'proceed',
                'reasoning': 'Insufficient historical data for prediction',
                'suggested_adjustments': ['Generate more samples to enable prediction'],
                'sample_size': 0
            }
        
        # Calculate weighted average
        weights = {
            'material': 0.4,
            'component': 0.2,
            'temperature': 0.25,
            'attempt': 0.15
        }
        
        success_prob = 0.0
        expected_score = 0.0
        total_weight = 0.0
        
        for model in valid_models:
            weight = weights.get(model['type'], 0.25)
            success_prob += model['success_rate'] * weight
            expected_score += model['avg_score'] * weight
            total_weight += weight
        
        # Normalize if not all models available
        if total_weight > 0:
            success_prob /= total_weight
            expected_score /= total_weight
        
        # Determine confidence based on total samples
        total_samples = sum(m.get('samples', 0) for m in valid_models)
        if total_samples >= 30:
            confidence = 'high'
        elif total_samples >= 15:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        # Generate recommendation
        if success_prob >= 0.7:
            recommendation = 'proceed'
            reasoning = f"High success probability ({success_prob:.0%})"
        elif success_prob >= 0.4:
            recommendation = 'proceed_with_caution'
            reasoning = f"Moderate success probability ({success_prob:.0%}) - monitor closely"
        else:
            recommendation = 'adjust_parameters'
            reasoning = f"Low success probability ({success_prob:.0%}) - adjust parameters first"
        
        # Generate suggested adjustments
        adjustments = self._generate_adjustments(models, material, component_type, temperature)
        
        logger.info(f"✅ [SUCCESS PREDICTOR] {material}/{component_type}: {success_prob:.0%} success probability")
        
        return {
            'success_probability': success_prob,
            'expected_human_score': expected_score,
            'confidence': confidence,
            'recommendation': recommendation,
            'reasoning': reasoning,
            'suggested_adjustments': adjustments,
            'sample_size': total_samples,
            'models_used': [m['type'] for m in valid_models]
        }
    
    def _get_material_success_rate(self, material: str, component_type: Optional[str] = None) -> Dict:
        """Get success rate - GENERIC LEARNING (material param ignored)."""
        cache_key = "global:success_rate"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        query = "SELECT success, human_score FROM detection_results"
        params = []
        
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < self.min_samples:
            result = {'valid': False, 'type': 'material', 'samples': len(rows)}
        else:
            success_count = sum(1 for r in rows if r['success'])
            success_rate = success_count / len(rows)
            avg_score = statistics.mean(r['human_score'] for r in rows)
            
            result = {
                'valid': True,
                'type': 'material',
                'success_rate': success_rate,
                'avg_score': avg_score,
                'samples': len(rows)
            }
        
        self._cache[cache_key] = result
        return result
    
    def _get_component_success_rate(self, component_type: str) -> Dict:
        """Get success rate for component type across all materials."""
        cache_key = f"component:{component_type}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute(
            "SELECT success, human_score FROM detection_results WHERE component_type = ?",
            [component_type]
        )
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < self.min_samples:
            result = {'valid': False, 'type': 'component', 'samples': len(rows)}
        else:
            success_count = sum(1 for r in rows if r['success'])
            success_rate = success_count / len(rows)
            avg_score = statistics.mean(r['human_score'] for r in rows)
            
            result = {
                'valid': True,
                'type': 'component',
                'success_rate': success_rate,
                'avg_score': avg_score,
                'samples': len(rows)
            }
        
        self._cache[cache_key] = result
        return result
    
    def _get_temperature_effectiveness(
        self,
        temperature: float,
        material: Optional[str] = None,
        component_type: Optional[str] = None
    ) -> Dict:
        """Get success rate for temperature range."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # Query temperatures within ±0.1 of target
        query = """
            SELECT success, human_score 
            FROM detection_results 
            WHERE temperature BETWEEN ? AND ?
        """
        params = [temperature - 0.1, temperature + 0.1]
        
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < max(3, self.min_samples // 2):  # Lower threshold for temp
            return {'valid': False, 'type': 'temperature', 'samples': len(rows)}
        
        success_count = sum(1 for r in rows if r['success'])
        success_rate = success_count / len(rows)
        avg_score = statistics.mean(r['human_score'] for r in rows)
        
        return {
            'valid': True,
            'type': 'temperature',
            'success_rate': success_rate,
            'avg_score': avg_score,
            'samples': len(rows)
        }
    
    def _get_attempt_success_pattern(
        self,
        attempt_number: int,
        material: Optional[str] = None,
        component_type: Optional[str] = None
    ) -> Dict:
        """Analyze if later attempts tend to succeed more/less."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        query = "SELECT success, human_score FROM detection_results WHERE attempt_number = ?"
        params = [attempt_number]
        
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < max(3, self.min_samples // 2):
            return {'valid': False, 'type': 'attempt', 'samples': len(rows)}
        
        success_count = sum(1 for r in rows if r['success'])
        success_rate = success_count / len(rows)
        avg_score = statistics.mean(r['human_score'] for r in rows)
        
        return {
            'valid': True,
            'type': 'attempt',
            'success_rate': success_rate,
            'avg_score': avg_score,
            'samples': len(rows)
        }
    
    def _generate_adjustments(
        self,
        models: List[Dict],
        material: str,
        component_type: str,
        temperature: float
    ) -> List[str]:
        """Generate specific parameter adjustment suggestions."""
        adjustments = []
        
        # Check material model
        material_model = next((m for m in models if m['type'] == 'material' and m['valid']), None)
        if material_model and material_model['success_rate'] < 0.4:
            adjustments.append(f"⚠️  Material '{material}' has low success rate ({material_model['success_rate']:.0%}) - consider reviewing material-specific prompt")
        
        # Check temperature model
        temp_model = next((m for m in models if m['type'] == 'temperature' and m['valid']), None)
        if temp_model and temp_model['success_rate'] < 0.5:
            if temperature > 0.7:
                adjustments.append(f"🌡️  Try lowering temperature from {temperature:.2f} to ~0.6 for more consistent results")
            else:
                adjustments.append(f"🌡️  Try increasing temperature from {temperature:.2f} to ~0.75 for more variation")
        
        # Check component model
        component_model = next((m for m in models if m['type'] == 'component' and m['valid']), None)
        if component_model and component_model['success_rate'] < 0.4:
            adjustments.append(f"📝 Component type '{component_type}' has low overall success rate - may need prompt overhaul")
        
        if not adjustments:
            adjustments.append("✅ Parameters look good based on historical data")
        
        return adjustments
    
    def get_risk_assessment(self, material: str, component_type: str) -> Dict:
        """
        Assess risk level for material+component combination.
        
        Returns:
            Dict with risk level and recommendations
        """
        prediction = self.predict_success(material, component_type, 0.7, 1)
        
        if prediction['confidence'] == 'none':
            return {
                'risk_level': 'unknown',
                'message': 'Insufficient data for risk assessment',
                'recommendation': 'Generate samples to establish baseline'
            }
        
        success_prob = prediction['success_probability']
        
        if success_prob >= 0.7:
            risk_level = 'low'
            message = f"Low risk - {success_prob:.0%} historical success rate"
            recommendation = "Proceed with confidence"
        elif success_prob >= 0.4:
            risk_level = 'medium'
            message = f"Medium risk - {success_prob:.0%} historical success rate"
            recommendation = "Proceed with monitoring, expect some retries"
        else:
            risk_level = 'high'
            message = f"High risk - {success_prob:.0%} historical success rate"
            recommendation = "Review and optimize parameters before generating"
        
        return {
            'risk_level': risk_level,
            'success_probability': success_prob,
            'message': message,
            'recommendation': recommendation,
            'confidence': prediction['confidence'],
            'adjustments': prediction['suggested_adjustments']
        }
