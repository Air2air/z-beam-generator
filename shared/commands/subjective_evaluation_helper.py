"""
Integration helper for Subjective evaluation in generation workflows

Provides easy integration of Claude subjective evaluation as a final
post-generation quality check step with learning database integration.
"""

from typing import Optional, Dict, Any
import logging
from processing.subjective import SubjectiveEvaluator, SubjectiveEvaluationResult

logger = logging.getLogger(__name__)


class SubjectiveEvaluationHelper:
    """
    Helper for integrating Subjective evaluation into generation workflows
    
    Features:
    - Post-generation subjective evaluation
    - Learning database integration for tracking improvements
    - Quality gate enforcement
    - Batch evaluation support
    
    Usage:
        helper = SubjectiveEvaluationHelper(
            verbose=True,
            feedback_db=feedback_db  # Optional: for learning
        )
        result = helper.evaluate_generation(
            content=generated_text,
            topic="Aluminum",
            component_type="caption",
            domain="materials"
        )
        
        if not result.passes_quality_gate:
            print("Quality gate failed!")
    """
    
    def __init__(
        self,
        api_client = None,
        quality_threshold: float = 7.0,
        verbose: bool = False,
        enabled: bool = True,
        feedback_db = None
    ):
        """
        Initialize evaluation helper
        
        Args:
            api_client: Claude API client (optional)
            quality_threshold: Minimum acceptable quality score (0-10)
            verbose: Print detailed evaluation output
            enabled: Enable/disable evaluation (useful for --skip-claude-eval flag)
            feedback_db: WinstonFeedbackDatabase instance for learning (optional)
        """
        self.enabled = enabled
        self.verbose = verbose
        self.feedback_db = feedback_db
        
        if enabled:
            self.evaluator = SubjectiveEvaluator(
                api_client=api_client,
                quality_threshold=quality_threshold,
                verbose=verbose
            )
        else:
            self.evaluator = None
    
    def evaluate_generation(
        self,
        content: str,
        topic: str,  # Changed from material_name for reusability
        component_type: str = "caption",
        domain: str = "materials",
        context: Optional[Dict[str, Any]] = None,
        fail_on_low_quality: bool = False,
        author_id: Optional[int] = None,
        attempt_number: Optional[int] = None
    ) -> Optional[SubjectiveEvaluationResult]:
        """
        Evaluate generated content with optional learning database integration
        
        Args:
            content: Generated text to evaluate
            topic: Subject matter (material name, historical event, recipe name, etc.)
            component_type: Type of content (caption, subtitle, etc.)
            domain: Content domain (materials, history, recipes, etc.)
            context: Additional context (properties, author, etc.)
            fail_on_low_quality: Raise exception if quality gate fails
            author_id: Optional author ID for learning database
            attempt_number: Optional attempt number for learning database
        
        Returns:
            SubjectiveEvaluationResult or None if disabled
        
        Raises:
            ValueError: If fail_on_low_quality=True and quality gate fails
        """
        
        if not self.enabled:
            if self.verbose:
                print("⏭️  Subjective evaluation disabled")
            return None
        
        # Perform evaluation
        result = self.evaluator.evaluate(
            content=content,
            material_name=topic,  # Backward compatible parameter
            component_type=component_type,
            context=context
        )
        
        # DEBUG: Log narrative before database insert
        if result.narrative_assessment:
            logger.info(f"🔍 [DEBUG] HELPER: Has narrative ({len(result.narrative_assessment)} chars): {result.narrative_assessment[:100]}...")
        else:
            logger.warning(f"⚠️ [DEBUG] HELPER: Result has NO narrative_assessment")
        
        # Log to learning database if available
        if self.feedback_db:
            try:
                eval_id = self.feedback_db.log_subjective_evaluation(
                    topic=topic,
                    component_type=component_type,
                    generated_text=content,
                    evaluation_result=result,
                    domain=domain,
                    author_id=author_id,
                    attempt_number=attempt_number
                )
                logger.info(f"✅ [LEARNING] Subjective evaluation #{eval_id} logged to database")
            except Exception as e:
                logger.warning(f"⚠️  [LEARNING] Failed to log Subjective evaluation: {e}")
        
        # Handle quality gate failure
        if fail_on_low_quality and not result.passes_quality_gate:
            raise ValueError(
                f"Content quality below threshold: {result.overall_score:.1f}/10 "
                f"(required: {self.evaluator.quality_threshold:.1f}/10)"
            )
        
        return result
    
    def evaluate_batch(
        self,
        generations: Dict[str, str],
        topic: str,
        component_type: str = "caption",
        domain: str = "materials"
    ) -> Dict[str, SubjectiveEvaluationResult]:
        """
        Evaluate multiple generations
        
        Args:
            generations: Dict of {identifier: content}
            topic: Subject matter (material name, etc.)
            component_type: Component type
            domain: Content domain
        
        Returns:
            Dict of {identifier: evaluation_result}
        """
        
        if not self.enabled:
            return {}
        
        results = {}
        for identifier, content in generations.items():
            result = self.evaluator.evaluate(
                content=content,
                material_name=topic,
                component_type=component_type
            )
            results[identifier] = result
            
            # Log to database if available
            if self.feedback_db:
                try:
                    self.feedback_db.log_subjective_evaluation(
                        topic=topic,
                        component_type=component_type,
                        generated_text=content,
                        evaluation_result=result,
                        domain=domain
                    )
                except Exception as e:
                    logger.warning(f"⚠️  [LEARNING] Failed to log evaluation: {e}")
        
        return results
    
    def get_summary_report(
        self,
        evaluation: SubjectiveEvaluationResult
    ) -> str:
        """
        Generate summary report for evaluation result
        
        Args:
            evaluation: SubjectiveEvaluationResult to summarize
        
        Returns:
            Formatted summary string
        """
        
        if evaluation is None:
            return "Subjective evaluation disabled"
        
        report = []
        report.append(f"Overall Score: {evaluation.overall_score:.1f}/10")
        report.append(f"Quality Gate: {'PASS ✅' if evaluation.passes_quality_gate else 'FAIL ❌'}")
        report.append(f"Evaluation Time: {evaluation.evaluation_time_ms:.1f}ms")
        
        # Dimension scores summary
        failing_dims = [s for s in evaluation.dimension_scores if s.score < 7.0]
        if failing_dims:
            report.append(f"Low-scoring dimensions: {len(failing_dims)}")
            for dim in failing_dims:
                report.append(f"  • {dim.dimension.value}: {dim.score:.1f}/10")
        
        return "\n".join(report)


# Convenience function for quick integration
def evaluate_after_generation(
    content: str,
    topic: str,  # Changed from material_name for reusability
    component_type: str = "caption",
    domain: str = "materials",
    api_client = None,
    verbose: bool = True,
    skip_evaluation: bool = False,
    feedback_db = None
) -> Optional[SubjectiveEvaluationResult]:
    """
    Quick evaluation function for post-generation quality check
    
    Args:
        content: Generated content
        topic: Subject matter (material name, historical event, etc.)
        component_type: Component type
        domain: Content domain (materials, history, recipes, etc.)
        api_client: Claude API client
        verbose: Print detailed output
        skip_evaluation: Skip evaluation if True
        feedback_db: WinstonFeedbackDatabase for learning (optional)
    
    Returns:
        SubjectiveEvaluationResult or None if skipped
    """
    
    helper = SubjectiveEvaluationHelper(
        api_client=api_client,
        verbose=verbose,
        enabled=not skip_evaluation,
        feedback_db=feedback_db
    )
    
    return helper.evaluate_generation(
        content=content,
        topic=topic,
        component_type=component_type,
        domain=domain
    )
