"""
Quality Orchestrator for Content Evaluation

🔄 REUSABILITY: Works for ANY domain (materials, settings, contaminants, compounds)
🎯 SEPARATION: ONLY coordinates evaluation, doesn't generate or save
🚀 ADAPTABILITY: Register new evaluators without changing core logic

This module provides a flexible, extensible quality evaluation system that:
- Coordinates multiple quality evaluators (Winston, Realism, Structural, Custom)
- Aggregates scores from all evaluators
- Works across all domains without modification
- Supports dynamic evaluator registration
"""

import logging
from typing import Any, Dict, List, Optional, Protocol

logger = logging.getLogger(__name__)


class QualityEvaluator(Protocol):
    """
    Protocol for any quality evaluator (reusability).
    
    Any class implementing this protocol can be registered with QualityOrchestrator.
    This enables extensibility without modifying core logic.
    """
    
    def evaluate(self, content: str, context: Dict) -> Dict[str, Any]:
        """
        Evaluate content quality.
        
        Args:
            content: Generated text (ANY domain)
            context: Domain-specific context (material_name, author, domain, etc.)
        
        Returns:
            Dict with evaluation results (structure depends on evaluator)
        """
        ...


class QualityOrchestrator:
    """
    🔄 REUSABLE: Works for ANY domain (materials, settings, contaminants, compounds)
    🎯 SEPARATION: ONLY coordinates evaluation, doesn't generate or save
    🚀 ADAPTABLE: Register new evaluators without changing core logic
    
    Orchestrates quality evaluation by coordinating multiple specialized evaluators.
    Pure coordination - delegates to specialized evaluators, doesn't implement
    evaluation logic itself.
    
    Usage:
        >>> orchestrator = QualityOrchestrator()
        >>> orchestrator.register_evaluator('winston', winston_client)
        >>> orchestrator.register_evaluator('realism', subjective_evaluator)
        >>> 
        >>> scores = orchestrator.evaluate(content, {
        ...     'domain': 'materials',
        ...     'item_name': 'Aluminum',
        ...     'component_type': 'description'
        ... })
    """
    
    def __init__(self):
        """
        Initialize orchestrator with empty evaluator list.
        
        Evaluators are registered dynamically via register_evaluator().
        This allows different configurations for different domains or use cases.
        """
        self.evaluators: List[tuple[str, QualityEvaluator]] = []
        self._weights: Dict[str, float] = {}
    
    def register_evaluator(
        self, 
        name: str, 
        evaluator: QualityEvaluator,
        weight: float = 1.0
    ) -> None:
        """
        🚀 ADAPTABILITY: Add new quality checks without modifying class.
        
        Register a quality evaluator to run on all content.
        
        Args:
            name: Identifier for this evaluator (e.g., 'winston', 'realism')
            evaluator: Object implementing QualityEvaluator protocol
            weight: Weight for overall quality calculation (default: 1.0)
        
        Example:
            >>> orchestrator.register_evaluator('winston', winston_client, weight=0.4)
            >>> orchestrator.register_evaluator('realism', subjective_eval, weight=0.6)
            >>> orchestrator.register_evaluator('custom', my_checker, weight=1.0)
        """
        self.evaluators.append((name, evaluator))
        self._weights[name] = weight
        logger.info(f"Registered quality evaluator: {name} (weight: {weight})")
    
    def list_evaluators(self) -> List[str]:
        """
        Get list of registered evaluator names.
        
        Returns:
            List of evaluator names (e.g., ['winston', 'realism', 'structural'])
        """
        return [name for name, _ in self.evaluators]
    
    def unregister_evaluator(self, name: str) -> bool:
        """
        Remove a registered evaluator.
        
        Args:
            name: Identifier of evaluator to remove
        
        Returns:
            True if evaluator was found and removed, False otherwise
        """
        for i, (eval_name, _) in enumerate(self.evaluators):
            if eval_name == name:
                self.evaluators.pop(i)
                self._weights.pop(name, None)
                logger.info(f"Unregistered quality evaluator: {name}")
                return True
        return False
    
    def evaluate(
        self, 
        content: str, 
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        🔄 REUSABLE: Same method for ALL domains.
        
        Run all registered quality evaluations and aggregate results.
        
        Args:
            content: Generated text (ANY domain: material desc, setting desc, etc.)
            context: Domain-specific context:
                - 'domain': 'materials' | 'settings' | 'contaminants' | 'compounds'
                - 'item_name': Name of item being evaluated
                - 'component_type': Type of content (description, micro, etc.)
                - 'author_id': Author persona ID
                - Any additional custom fields
        
        Returns:
            Dict with all quality scores:
            {
                'evaluator_name': {evaluation results},
                'overall_quality': float (0.0 to 1.0),
                'passed': bool,
                'failed_evaluators': List[str]
            }
        """
        context = context or {}
        results = {}
        
        logger.info(f"Running quality evaluation with {len(self.evaluators)} evaluators")
        
        # Run all registered evaluators (extensible!)
        for name, evaluator in self.evaluators:
            try:
                logger.debug(f"Running evaluator: {name}")
                eval_result = evaluator.evaluate(content, context)
                results[name] = eval_result
                logger.debug(f"Evaluator {name} completed successfully")
            except Exception as e:
                logger.error(f"Evaluator {name} failed: {e}")
                results[name] = {
                    'error': str(e), 
                    'success': False,
                    'passed': False
                }
        
        # Aggregate overall quality score
        results['overall_quality'] = self._calculate_overall_quality(results)
        
        # Determine pass/fail status
        results['passed'] = self._check_pass_status(results)
        results['failed_evaluators'] = self._get_failed_evaluators(results)
        
        logger.info(
            f"Quality evaluation complete: "
            f"overall={results['overall_quality']:.2f}, "
            f"passed={results['passed']}"
        )
        
        return results
    
    def _calculate_overall_quality(self, results: Dict) -> float:
        """
        Aggregate scores from all evaluators using weighted average.
        
        Attempts to extract scores from various evaluator result formats:
        - Winston: 'human_score' (0.0 to 1.0)
        - Subjective: 'overall_realism' (0 to 10, normalized to 0.0-1.0)
        - Structural: 'passed' (binary: 1.0 or 0.0)
        - Custom: 'score' (assumes 0.0 to 1.0)
        
        Args:
            results: Dict of evaluator results
        
        Returns:
            Weighted average score (0.0 to 1.0), or 0.0 if no scores available
        """
        weighted_scores = []
        total_weight = 0.0
        
        for name, result in results.items():
            if name in ['overall_quality', 'passed', 'failed_evaluators']:
                continue  # Skip aggregated fields
            
            if isinstance(result, dict) and result.get('error'):
                continue  # Skip failed evaluators
            
            score = self._extract_score(name, result)
            if score is not None:
                weight = self._weights.get(name, 1.0)
                weighted_scores.append(score * weight)
                total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return sum(weighted_scores) / total_weight
    
    def _extract_score(self, evaluator_name: str, result: Any) -> Optional[float]:
        """
        Extract normalized score (0.0-1.0) from evaluator result.
        
        Handles various result formats:
        - Winston: {'human_score': 0.85}
        - Subjective: {'overall_realism': 7.5}
        - Structural: {'passed': True}
        - Generic: {'score': 0.9}
        
        Args:
            evaluator_name: Name of evaluator
            result: Result dict from evaluator
        
        Returns:
            Normalized score (0.0 to 1.0), or None if score can't be extracted
        """
        if not isinstance(result, dict):
            return None
        
        # Winston: use human_score (already 0.0-1.0)
        if 'human_score' in result:
            return float(result['human_score'])
        
        # Subjective: use overall_realism (0-10, normalize to 0.0-1.0)
        if 'overall_realism' in result:
            return float(result['overall_realism']) / 10.0
        
        # Structural: binary pass/fail
        if 'passed' in result:
            return 1.0 if result['passed'] else 0.0
        
        # Generic: direct score field
        if 'score' in result:
            return float(result['score'])
        
        # Can't extract score
        return None
    
    def _check_pass_status(self, results: Dict) -> bool:
        """
        Check if all evaluators passed.
        
        An evaluator passes if:
        - It has 'passed': True in result
        - It has 'success': True in result
        - It doesn't have 'error' in result
        
        Args:
            results: Dict of evaluator results
        
        Returns:
            True if all evaluators passed, False otherwise
        """
        for name, result in results.items():
            if name in ['overall_quality', 'passed', 'failed_evaluators']:
                continue
            
            if isinstance(result, dict):
                # Check for explicit failure
                if result.get('error') or result.get('success') is False:
                    return False
                
                # Check for explicit pass flag
                if 'passed' in result and not result['passed']:
                    return False
        
        return True
    
    def _get_failed_evaluators(self, results: Dict) -> List[str]:
        """
        Get list of evaluator names that failed.
        
        Args:
            results: Dict of evaluator results
        
        Returns:
            List of evaluator names that failed
        """
        failed = []
        
        for name, result in results.items():
            if name in ['overall_quality', 'passed', 'failed_evaluators']:
                continue
            
            if isinstance(result, dict):
                if result.get('error') or result.get('success') is False:
                    failed.append(name)
                elif 'passed' in result and not result['passed']:
                    failed.append(name)
        
        return failed
    
    def get_registered_evaluators(self) -> List[str]:
        """
        Get list of registered evaluator names.
        
        Returns:
            List of evaluator names currently registered
        """
        return [name for name, _ in self.evaluators]
    
    def clear_evaluators(self) -> None:
        """Clear all registered evaluators."""
        self.evaluators.clear()
        self._weights.clear()
        logger.info("Cleared all registered evaluators")
