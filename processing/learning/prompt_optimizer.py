"""
Prompt Optimizer - Dynamic Prompt Generation Based on Learning

Dynamically optimizes prompts based on Winston feedback patterns.
Uses learned patterns to inject targeted anti-AI instructions and
emphasize successful language patterns.

Key Features:
- Pattern-based prompt enhancement
- Material-specific prompt customization
- Success pattern reinforcement
- Dynamic anti-AI rule injection
- A/B testing support for prompt variations

Fail-fast design: Requires database and pattern learner, no fallbacks.
"""

import logging
from typing import Dict, List, Optional
from pathlib import Path

from processing.learning.pattern_learner import PatternLearner

logger = logging.getLogger(__name__)


class PromptOptimizer:
    """
    Optimize prompts based on learned patterns from Winston feedback.
    
    Analyzes:
    - Which prompt elements correlate with high human scores
    - Which anti-AI rules are most effective
    - Material-specific prompt adjustments
    - Component-specific optimizations
    
    Provides:
    - Enhanced prompts with learned anti-AI rules
    - Pattern-specific warnings
    - Success pattern reinforcement
    - Dynamic prompt variations for A/B testing
    """
    
    def __init__(self, db_path: str, pattern_learner: Optional[PatternLearner] = None):
        """
        Initialize prompt optimizer.
        
        Args:
            db_path: Path to Winston feedback database
            pattern_learner: Optional PatternLearner instance (creates new if None)
        """
        self.db_path = Path(db_path)
        self.pattern_learner = pattern_learner or PatternLearner(str(db_path))
        
        logger.info("[PROMPT OPTIMIZER] Initialized")
    
    def optimize_prompt(
        self,
        base_prompt: str,
        material: Optional[str] = None,
        component_type: Optional[str] = None,
        include_patterns: bool = True,
        include_recommendations: bool = True
    ) -> Dict:
        """
        Optimize prompt with learned patterns and recommendations.
        
        Args:
            base_prompt: Original prompt text
            material: Optional material context
            component_type: Optional component type
            include_patterns: Whether to inject pattern warnings
            include_recommendations: Whether to add success patterns
            
        Returns:
            Dict containing:
            - optimized_prompt: Enhanced prompt text
            - additions: List of what was added
            - confidence: Confidence level (high/medium/low)
            - expected_improvement: Estimated improvement percentage
        """
        # Learn patterns for this context
        patterns = self.pattern_learner.learn_patterns(material, component_type)
        
        if patterns['stats']['total_samples'] < 5:
            logger.info("[PROMPT OPTIMIZER] Insufficient data for optimization")
            return {
                'optimized_prompt': base_prompt,
                'additions': [],
                'confidence': 'none',
                'expected_improvement': 0.0,
                'reason': 'Need more samples for learning'
            }
        
        # Start with base prompt
        optimized = base_prompt
        additions = []
        
        # Add risky pattern warnings
        if include_patterns and patterns['risky_patterns']:
            risky_section = self._build_risky_patterns_section(patterns['risky_patterns'][:5])
            optimized += "\n\n" + risky_section
            additions.append(f"Added {len(patterns['risky_patterns'][:5])} risky pattern warnings")
        
        # Add success pattern encouragement
        if include_recommendations and patterns['safe_patterns']:
            safe_section = self._build_safe_patterns_section(patterns['safe_patterns'][:3])
            optimized += "\n\n" + safe_section
            additions.append(f"Added {len(patterns['safe_patterns'][:3])} success pattern examples")
        
        # Calculate expected improvement
        if patterns['stats']['failed_samples'] > 0:
            fail_rate = patterns['stats']['failed_samples'] / patterns['stats']['total_samples']
            # Estimate that addressing patterns could reduce failures by 30-50%
            expected_improvement = fail_rate * 0.4
        else:
            expected_improvement = 0.05  # Small baseline improvement
        
        # Determine confidence
        sample_size = patterns['stats']['total_samples']
        if sample_size >= 20:
            confidence = 'high'
        elif sample_size >= 10:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        logger.info(f"✅ [PROMPT OPTIMIZER] Enhanced prompt with {len(additions)} additions (confidence: {confidence})")
        
        return {
            'optimized_prompt': optimized,
            'additions': additions,
            'confidence': confidence,
            'expected_improvement': expected_improvement,
            'patterns_analyzed': len(patterns['risky_patterns']) + len(patterns['safe_patterns'])
        }
    
    def _build_risky_patterns_section(self, risky_patterns: List[Dict]) -> str:
        """Build prompt section warning about risky patterns."""
        lines = ["⚠️ CRITICAL: Avoid these AI-detected patterns:"]
        
        for i, pattern in enumerate(risky_patterns, 1):
            fail_rate = pattern['fail_rate'] * 100
            lines.append(f"{i}. NEVER use: \"{pattern['pattern']}\" (detected as AI {fail_rate:.0f}% of the time)")
        
        lines.append("\nThese patterns have been statistically proven to fail Winston AI detection.")
        lines.append("Find alternative phrasings that convey the same meaning.")
        
        return '\n'.join(lines)
    
    def _build_safe_patterns_section(self, safe_patterns: List[Dict]) -> str:
        """Build prompt section encouraging safe patterns."""
        lines = ["✅ ENCOURAGED: These patterns consistently pass as human:"]
        
        for i, pattern in enumerate(safe_patterns, 1):
            success_rate = pattern['success_rate'] * 100
            lines.append(f"{i}. Emulate style of: \"{pattern['pattern']}\" ({success_rate:.0f}% success rate)")
        
        lines.append("\nThese language patterns have proven effective at human-like writing.")
        
        return '\n'.join(lines)
    
    def generate_variants(
        self,
        base_prompt: str,
        material: Optional[str] = None,
        component_type: Optional[str] = None,
        num_variants: int = 3
    ) -> List[Dict]:
        """
        Generate multiple prompt variants for A/B testing.
        
        Args:
            base_prompt: Original prompt
            material: Optional material context
            component_type: Optional component type
            num_variants: Number of variants to generate
            
        Returns:
            List of variant dicts with:
            - variant_id: Identifier
            - prompt: Prompt text
            - strategy: What's different about this variant
            - expected_performance: Predicted success rate
        """
        patterns = self.pattern_learner.learn_patterns(material, component_type)
        
        variants = []
        
        # Variant 1: Base + top risky patterns only
        v1 = self.optimize_prompt(
            base_prompt,
            material,
            component_type,
            include_patterns=True,
            include_recommendations=False
        )
        variants.append({
            'variant_id': 'risky_only',
            'prompt': v1['optimized_prompt'],
            'strategy': 'Focus on avoiding risky patterns',
            'expected_performance': 0.6
        })
        
        # Variant 2: Base + safe patterns only
        v2 = self.optimize_prompt(
            base_prompt,
            material,
            component_type,
            include_patterns=False,
            include_recommendations=True
        )
        variants.append({
            'variant_id': 'safe_only',
            'prompt': v2['optimized_prompt'],
            'strategy': 'Reinforce successful patterns',
            'expected_performance': 0.65
        })
        
        # Variant 3: Base + both
        v3 = self.optimize_prompt(
            base_prompt,
            material,
            component_type,
            include_patterns=True,
            include_recommendations=True
        )
        variants.append({
            'variant_id': 'combined',
            'prompt': v3['optimized_prompt'],
            'strategy': 'Both avoidance and reinforcement',
            'expected_performance': 0.75
        })
        
        return variants[:num_variants]
    
    def get_prompt_effectiveness_report(self, material: Optional[str] = None) -> Dict:
        """
        Analyze which prompt strategies are most effective.
        
        Args:
            material: Optional filter by material
            
        Returns:
            Dict with effectiveness analysis
        """
        patterns = self.pattern_learner.learn_patterns(material)
        
        if patterns['stats']['total_samples'] < 10:
            return {
                'status': 'insufficient_data',
                'message': 'Need at least 10 samples for analysis'
            }
        
        success_rate = (patterns['stats']['success_samples'] / 
                       patterns['stats']['total_samples'])
        
        # Analyze if there are clear problem areas
        high_risk_count = sum(1 for p in patterns['risky_patterns'] if p['fail_rate'] > 0.9)
        medium_risk_count = sum(1 for p in patterns['risky_patterns'] if 0.7 <= p['fail_rate'] <= 0.9)
        
        recommendations = []
        
        if success_rate < 0.5:
            recommendations.append("🚨 SUCCESS RATE BELOW 50% - Immediate prompt overhaul needed")
            recommendations.append(f"   • {high_risk_count} patterns fail >90% - blacklist immediately")
            recommendations.append("   • Consider complete prompt rewrite with learned patterns")
        elif success_rate < 0.7:
            recommendations.append("⚠️  Success rate 50-70% - Prompt improvements needed")
            recommendations.append(f"   • Address {high_risk_count + medium_risk_count} risky patterns")
            recommendations.append("   • Add more specific anti-AI instructions")
        else:
            recommendations.append("✅ Success rate >70% - Prompt is working well")
            recommendations.append("   • Fine-tune by addressing remaining risky patterns")
            recommendations.append("   • Reinforce successful language patterns")
        
        return {
            'status': 'analyzed',
            'success_rate': success_rate,
            'total_samples': patterns['stats']['total_samples'],
            'high_risk_patterns': high_risk_count,
            'medium_risk_patterns': medium_risk_count,
            'recommendations': recommendations,
            'top_issues': patterns['risky_patterns'][:5]
        }
