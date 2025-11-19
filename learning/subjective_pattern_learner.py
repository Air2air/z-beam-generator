"""
Subjective Pattern Learning System

Automatically updates learned_patterns.yaml based on subjective evaluation results
and acceptance decisions to improve evaluation quality over time.

Created: November 18, 2025
"""

import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging


class SubjectivePatternLearner:
    """
    Learns from subjective evaluation results and updates evaluation patterns.
    
    This system tracks:
    - Theatrical phrases that trigger rejection
    - AI tendencies that frequently appear
    - Success patterns from accepted content
    - Scoring adjustments based on empirical data
    """
    
    def __init__(self, patterns_file: Optional[Path] = None):
        """
        Initialize subjective pattern learner.
        
        Args:
            patterns_file: Path to learned_patterns.yaml (default: prompts/evaluation/learned_patterns.yaml)
        """
        self.logger = logging.getLogger(__name__)
        
        if patterns_file is None:
            self.patterns_file = Path('prompts/evaluation/learned_patterns.yaml')
        else:
            self.patterns_file = patterns_file
        
        # Ensure file exists
        if not self.patterns_file.exists():
            self.logger.warning(f"Patterns file not found: {self.patterns_file}")
            self._create_default_patterns()
    
    def update_from_evaluation(
        self,
        evaluation_result: Dict,
        content: str,
        accepted: bool,
        component_type: str,
        material_name: str
    ):
        """
        Update learned patterns based on evaluation result.
        
        Args:
            evaluation_result: Subjective evaluation result dictionary
            content: Generated content that was evaluated
            accepted: Whether content passed quality gates
            component_type: Type of component (caption, subtitle, etc.)
            material_name: Material being generated for
        """
        try:
            # Load current patterns
            patterns = self._load_patterns()
            
            # Increment evaluation count
            patterns['total_evaluations'] = patterns.get('total_evaluations', 0) + 1
            
            if not accepted:
                # Learn from rejection
                self._learn_from_rejection(patterns, evaluation_result, content)
            else:
                # Learn from success
                self._learn_from_success(patterns, evaluation_result)
            
            # Update timestamp
            patterns['last_updated'] = datetime.now().isoformat()
            
            # Save updated patterns
            self._save_patterns(patterns)
            
            self.logger.info(f"✅ Updated learned patterns (total evaluations: {patterns['total_evaluations']})")
            
        except Exception as e:
            self.logger.error(f"Failed to update learned patterns: {e}")
            # Don't fail generation - learning is enhancement not requirement
    
    def _learn_from_rejection(self, patterns: Dict, evaluation: Dict, content: str):
        """Learn from rejected content (Realism < 7.0)"""
        
        # Track AI tendencies
        ai_tendencies = evaluation.get('ai_tendencies', [])
        if ai_tendencies and ai_tendencies != ['none']:
            for tendency in ai_tendencies:
                if tendency != 'none':
                    current = patterns['ai_tendencies']['common'].get(tendency, 0)
                    patterns['ai_tendencies']['common'][tendency] = current + 1
        
        # Extract theatrical phrases from violations
        # This is a simplified version - could be enhanced with NLP
        violations = evaluation.get('violations', [])
        if violations:
            for phrase in violations:
                high_penalty = patterns['theatrical_phrases']['high_penalty']
                if phrase not in high_penalty and len(phrase) < 30:
                    # Add new theatrical phrase if not already tracked
                    high_penalty.append(phrase)
                    self.logger.info(f"📝 Learned new theatrical phrase: '{phrase}'")
    
    def _learn_from_success(self, patterns: Dict, evaluation: Dict):
        """Learn from accepted content (Realism >= 7.0)"""
        
        # Update success pattern statistics with exponential moving average
        alpha = 0.1  # Learning rate (10% new, 90% old)
        
        realism_score = evaluation.get('realism_score', 7.0)
        voice_auth = evaluation.get('voice_authenticity', 7.0)
        tonal_cons = evaluation.get('tonal_consistency', 7.0)
        
        success = patterns['success_patterns']
        success['sample_count'] = success.get('sample_count', 0) + 1
        
        # Exponential moving average
        success['average_realism_score'] = (
            (1 - alpha) * success.get('average_realism_score', 7.0) +
            alpha * realism_score
        )
        success['average_voice_authenticity'] = (
            (1 - alpha) * success.get('average_voice_authenticity', 7.0) +
            alpha * voice_auth
        )
        success['average_tonal_consistency'] = (
            (1 - alpha) * success.get('average_tonal_consistency', 7.0) +
            alpha * tonal_cons
        )
    
    def get_current_patterns(self) -> Dict:
        """Get current learned patterns for use in evaluation prompt"""
        return self._load_patterns()
    
    def _load_patterns(self) -> Dict:
        """Load patterns from YAML file"""
        try:
            with open(self.patterns_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load patterns: {e}")
            return self._get_default_patterns()
    
    def _save_patterns(self, patterns: Dict):
        """Save patterns to YAML file"""
        try:
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                yaml.dump(patterns, f, sort_keys=False, allow_unicode=True)
        except Exception as e:
            self.logger.error(f"Failed to save patterns: {e}")
            raise
    
    def _create_default_patterns(self):
        """Create default patterns file"""
        self.patterns_file.parent.mkdir(parents=True, exist_ok=True)
        patterns = self._get_default_patterns()
        self._save_patterns(patterns)
        self.logger.info(f"Created default patterns file: {self.patterns_file}")
    
    def _get_default_patterns(self) -> Dict:
        """Get default patterns structure"""
        return {
            'version': '1.0.0',
            'last_updated': datetime.now().isoformat(),
            'total_evaluations': 0,
            'theatrical_phrases': {
                'high_penalty': [
                    'zaps away', 'And yeah', 'changes everything', 'Wow',
                    'quick zap', 'pretty effective', 'turns out', 'you see',
                    'notice how', 'Amazing', 'revolutionary', 'game-changing'
                ],
                'medium_penalty': [
                    'really', 'very', 'quite', 'actually', 'literally'
                ]
            },
            'ai_tendencies': {
                'common': {
                    'formulaic_phrasing': 0,
                    'unnatural_transitions': 0,
                    'excessive_enthusiasm': 0,
                    'rigid_structure': 0,
                    'theatrical_casualness': 0,
                    'generic_language': 0
                },
                'emerging': []
            },
            'scoring_adjustments': {
                'theatrical_element_penalty': -2.0,
                'casual_marker_penalty': -3.0,
                'realism_threshold': 7.0,
                'voice_authenticity_floor': 4.0
            },
            'success_patterns': {
                'sample_count': 0,
                'average_realism_score': 7.0,
                'average_voice_authenticity': 7.0,
                'average_tonal_consistency': 7.0,
                'professional_verbs': [
                    'removes', 'restores', 'improves', 'provides',
                    'eliminates', 'preserves'
                ],
                'technical_precision': True,
                'neutral_tone': True,
                'objective_documentation': True
            }
        }
