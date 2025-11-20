"""Validation Orchestrator

Ultra-modular pipeline coordinator for content validation and improvement.
Orchestrates 6 passes with 19 discrete steps, each independently testable.

Architecture:
    Pass 1: Load (2 steps) - Load and validate content
    Pass 2: Quality Assessment (5 steps) - Winston, Realism, Readability, Subjective, Composite
    Pass 3: Gate Checks (5 steps) - Individual gates + composite
    Pass 4: Learning (5 steps) - Sweet spot, temperature, realism, pattern, merger
    Pass 5: Recording (2 steps) - Pattern recorder + database logger
    Pass 6: Regeneration (1 step) - Content regenerator with adjustments

Created: November 19, 2025
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import asdict

# Steps
from postprocessing.steps.load.content_loader import ContentLoader
from postprocessing.steps.load.content_validator import ContentValidator
from postprocessing.steps.quality.winston_detector import WinstonDetector
from postprocessing.steps.quality.realism_evaluator import RealismEvaluator
from postprocessing.steps.quality.readability_checker import ReadabilityChecker
from postprocessing.steps.quality.subjective_checker import SubjectiveChecker
from postprocessing.steps.quality.composite_scorer import CompositeScorer
from postprocessing.steps.gates.winston_gate import WinstonGateChecker
from postprocessing.steps.gates.realism_gate import RealismGateChecker
from postprocessing.steps.gates.readability_gate import ReadabilityGateChecker
from postprocessing.steps.gates.subjective_gate import SubjectiveGateChecker
from postprocessing.steps.gates.composite_gate import CompositeGateChecker
from postprocessing.steps.learning.sweet_spot_retriever import SweetSpotRetriever
from postprocessing.steps.learning.temperature_calculator import TemperatureCalculator
from postprocessing.steps.learning.realism_adjuster import RealismAdjuster
from postprocessing.steps.learning.pattern_adjuster import PatternAdjuster
from postprocessing.steps.learning.adjustment_merger import AdjustmentMerger
from postprocessing.steps.recording.pattern_recorder import PatternRecorder
from postprocessing.steps.recording.database_logger import DatabaseLogger
from postprocessing.steps.regeneration.content_regenerator import ContentRegenerator

# Results
from postprocessing.results import ValidationResult, QualityResults, GateResults

logger = logging.getLogger(__name__)


class ValidationOrchestrator:
    """
    Lightweight coordinator for ultra-modular validation pipeline.
    
    Pure orchestration - zero logic, just step coordination.
    Each step is independently tested and replaceable.
    """
    
    def __init__(
        self,
        api_client,
        winston_client,
        simple_generator,
        config: Optional[Dict] = None
    ):
        """
        Initialize orchestrator with required dependencies.
        
        Args:
            api_client: API client for content generation
            winston_client: Winston API client for detection
            simple_generator: SimpleGenerator for regeneration
            config: Configuration dictionary
        """
        if not api_client or not winston_client or not simple_generator:
            raise ValueError("All clients required (api, winston, generator)")
        
        self.api_client = api_client
        self.winston_client = winston_client
        self.simple_generator = simple_generator
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize all steps
        self._init_steps()
    
    def _init_steps(self):
        """Initialize all pipeline steps"""
        # Pass 1: Load steps
        self.content_loader = ContentLoader()
        self.content_validator = ContentValidator()
        
        # Pass 2: Quality steps (require dependencies)
        from postprocessing.evaluation.subjective_evaluator import SubjectiveEvaluator
        from generation.validation.readability.readability import ReadabilityValidator
        
        # Create simple validator wrapper for subjective checker
        class SubjectiveValidatorWrapper:
            def __init__(self, evaluator):
                self.evaluator = evaluator
            def validate(self, content, component_type):
                return self.evaluator.evaluate(content, component_type)
        
        self.subjective_evaluator = SubjectiveEvaluator(
            self.api_client,
            quality_threshold=7.0,
            evaluation_temperature=0.2
        )
        
        self.winston_detector = WinstonDetector(self.winston_client)
        self.realism_evaluator = RealismEvaluator(self.subjective_evaluator)
        self.readability_checker = ReadabilityChecker(ReadabilityValidator())
        self.subjective_checker = SubjectiveChecker(SubjectiveValidatorWrapper(self.subjective_evaluator))
        self.composite_scorer = CompositeScorer()
        
        # Pass 3: Gate steps
        self.winston_gate = WinstonGateChecker(threshold=0.33)
        self.realism_gate = RealismGateChecker(threshold=7.0)
        self.readability_gate = ReadabilityGateChecker()
        self.subjective_gate = SubjectiveGateChecker()
        self.composite_gate = CompositeGateChecker()
        
        # Pass 4: Learning steps
        from learning.sweet_spot_analyzer import SweetSpotAnalyzer
        from learning.temperature_advisor import TemperatureAdvisor
        from learning.realism_optimizer import RealismOptimizer
        from learning.pattern_learner import PatternLearner
        
        db_path = self.config.get('winston_feedback_db_path', 'z-beam.db')
        
        self.sweet_spot_retriever = SweetSpotRetriever(SweetSpotAnalyzer(db_path=db_path))
        self.temperature_calculator = TemperatureCalculator(TemperatureAdvisor(db_path=db_path))
        self.realism_adjuster = RealismAdjuster(RealismOptimizer())
        self.pattern_adjuster = PatternAdjuster(PatternLearner())
        self.adjustment_merger = AdjustmentMerger()
        
        # Pass 5: Recording steps
        self.pattern_recorder = PatternRecorder(self.subjective_evaluator)
        self.database_logger = DatabaseLogger(self.config)
        
        # Pass 6: Regeneration step
        self.content_regenerator = ContentRegenerator(self.simple_generator)
        
        self.logger.info("✅ Orchestrator initialized with 19 steps")
    
    def validate_and_improve(
        self,
        material_name: str,
        component_type: str,
        max_attempts: int = 5
    ) -> Dict[str, Any]:
        """
        Execute complete validation pipeline with automatic retries.
        
        Args:
            material_name: Material to validate
            component_type: Component type to validate
            max_attempts: Maximum retry attempts
            
        Returns:
            Dictionary with validation results
        """
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"🚀 VALIDATION PIPELINE START: {material_name}/{component_type}")
        self.logger.info(f"{'='*80}\n")
        
        context = {
            'material_name': material_name,
            'component_type': component_type,
            'attempt': 0,
            'step_durations': {}
        }
        
        best_score = 0.0
        best_content = None
        
        while context['attempt'] < max_attempts:
            context['attempt'] += 1
            
            self.logger.info(f"\n--- ATTEMPT {context['attempt']}/{max_attempts} ---\n")
            
            # ============================================================
            # PASS 1: LOAD CONTENT
            # ============================================================
            if not self._execute_load_pass(context):
                return self._failure_result("Load failed", context)
            
            # ============================================================
            # PASS 2: QUALITY ASSESSMENT
            # ============================================================
            if not self._execute_quality_pass(context):
                return self._failure_result("Quality assessment failed", context)
            
            # Track best result
            composite_score = context.get('composite_score', 0.0)
            if composite_score > best_score:
                best_score = composite_score
                best_content = context['content']
            
            # ============================================================
            # PASS 3: GATE CHECKS
            # ============================================================
            all_gates_passed = self._execute_gate_pass(context)
            
            if all_gates_passed:
                # SUCCESS! Record and return
                self._execute_recording_pass(context, accepted=True)
                return self._success_result(context)
            
            # Failed gates - need retry
            if context['attempt'] < max_attempts:
                self.logger.info("\n🔄 Gates failed, initiating retry with learning adjustments...\n")
                
                # ============================================================
                # PASS 4: LEARNING ADJUSTMENTS
                # ============================================================
                self._execute_learning_pass(context)
                
                # ============================================================
                # PASS 5: RECORD FAILURE
                # ============================================================
                self._execute_recording_pass(context, accepted=False)
                
                # ============================================================
                # PASS 6: REGENERATE
                # ============================================================
                if not self._execute_regeneration_pass(context):
                    return self._failure_result("Regeneration failed", context)
                
                # Loop back to PASS 2 with new content
        
        # Max attempts exhausted - return best result
        self.logger.warning(f"\n⚠️  Max attempts reached. Best score: {best_score:.1f}%\n")
        
        return {
            'success': False,
            'content': best_content or context.get('content', ''),
            'attempts': max_attempts,
            'composite_score': best_score,
            'reason': 'max_attempts_reached',
            'step_durations': context.get('step_durations', {})
        }
    
    def _execute_load_pass(self, context: Dict[str, Any]) -> bool:
        """Execute Pass 1: Load content"""
        self.logger.info("📂 PASS 1: LOAD CONTENT")
        
        # Step 1.1: Load content
        result = self.content_loader.execute(context)
        context['step_durations'][result.step_name] = result.duration_ms
        
        if not result.success:
            self.logger.error(f"Load failed: {result.error}")
            return False
        
        context['content'] = result.data
        
        # Step 1.2: Validate content
        result = self.content_validator.execute(context)
        context['step_durations'][result.step_name] = result.duration_ms
        
        if not result.success:
            self.logger.error(f"Validation failed: {result.error}")
            return False
        
        context['content_validation'] = result.data
        
        return True
    
    def _execute_quality_pass(self, context: Dict[str, Any]) -> bool:
        """Execute Pass 2: Quality assessment"""
        self.logger.info("\n🔍 PASS 2: QUALITY ASSESSMENT")
        
        # Step 2.1: Winston detection
        result = self.winston_detector.execute(context)
        context['step_durations'][result.step_name] = result.duration_ms
        if not result.success:
            return False
        context['winston_result'] = result.data
        
        # Step 2.2: Realism evaluation
        result = self.realism_evaluator.execute(context)
        context['step_durations'][result.step_name] = result.duration_ms
        if not result.success:
            return False
        context['realism_result'] = result.data
        
        # Step 2.3: Readability check
        result = self.readability_checker.execute(context)
        context['step_durations'][result.step_name] = result.duration_ms
        if not result.success:
            return False
        context['readability_result'] = result.data
        
        # Step 2.4: Subjective check
        result = self.subjective_checker.execute(context)
        context['step_durations'][result.step_name] = result.duration_ms
        if not result.success:
            return False
        context['subjective_result'] = result.data
        
        # Step 2.5: Composite score
        result = self.composite_scorer.execute(context)
        context['step_durations'][result.step_name] = result.duration_ms
        if not result.success:
            return False
        context['composite_score'] = result.data
        
        return True
    
    def _execute_gate_pass(self, context: Dict[str, Any]) -> bool:
        """Execute Pass 3: Gate checks"""
        self.logger.info("\n🚦 PASS 3: GATE CHECKS")
        
        # Step 3.1: Winston gate
        result = self.winston_gate.execute(context)
        context['step_durations'][result.step_name] = result.duration_ms
        if result.success:
            context['winston_gate'] = result.data
        
        # Step 3.2: Realism gate
        result = self.realism_gate.execute(context)
        context['step_durations'][result.step_name] = result.duration_ms
        if result.success:
            context['realism_gate'] = result.data
        
        # Step 3.3: Readability gate
        result = self.readability_gate.execute(context)
        context['step_durations'][result.step_name] = result.duration_ms
        if result.success:
            context['readability_gate'] = result.data
        
        # Step 3.4: Subjective gate
        result = self.subjective_gate.execute(context)
        context['step_durations'][result.step_name] = result.duration_ms
        if result.success:
            context['subjective_gate'] = result.data
        
        # Step 3.5: Composite gate (all must pass)
        result = self.composite_gate.execute(context)
        context['step_durations'][result.step_name] = result.duration_ms
        
        if result.success:
            context['gate_results'] = result.data
            return result.data['all_passed']
        
        return False
    
    def _execute_learning_pass(self, context: Dict[str, Any]):
        """Execute Pass 4: Learning adjustments"""
        self.logger.info("\n🧠 PASS 4: LEARNING ADJUSTMENTS")
        
        # Step 4.1: Sweet spot retrieval
        result = self.sweet_spot_retriever.execute(context)
        context['step_durations'][result.step_name] = result.duration_ms
        context['sweet_spot_adjustments'] = result.data if result.success else {}
        
        # Step 4.2: Temperature calculation
        result = self.temperature_calculator.execute(context)
        context['step_durations'][result.step_name] = result.duration_ms
        context['temperature_adjustments'] = result.data if result.success else {}
        
        # Step 4.3: Realism adjuster
        result = self.realism_adjuster.execute(context)
        context['step_durations'][result.step_name] = result.duration_ms
        context['realism_adjustments'] = result.data if result.success else {}
        
        # Step 4.4: Pattern adjuster
        result = self.pattern_adjuster.execute(context)
        context['step_durations'][result.step_name] = result.duration_ms
        context['pattern_adjustments'] = result.data if result.success else {}
        
        # Step 4.5: Merge adjustments
        result = self.adjustment_merger.execute(context)
        context['step_durations'][result.step_name] = result.duration_ms
        context['adjustments'] = result.data if result.success else {}
    
    def _execute_recording_pass(self, context: Dict[str, Any], accepted: bool):
        """Execute Pass 5: Recording"""
        self.logger.info(f"\n💾 PASS 5: RECORDING (accepted={accepted})")
        
        context['accepted'] = accepted
        context['success'] = accepted
        
        # Step 5.1: Pattern recorder
        result = self.pattern_recorder.execute(context)
        context['step_durations'][result.step_name] = result.duration_ms
        
        # Step 5.2: Database logger
        result = self.database_logger.execute(context)
        context['step_durations'][result.step_name] = result.duration_ms
    
    def _execute_regeneration_pass(self, context: Dict[str, Any]) -> bool:
        """Execute Pass 6: Regeneration"""
        self.logger.info("\n🔄 PASS 6: REGENERATION")
        
        # Step 6.1: Content regenerator
        result = self.content_regenerator.execute(context)
        context['step_durations'][result.step_name] = result.duration_ms
        
        if not result.success:
            self.logger.error(f"Regeneration failed: {result.error}")
            return False
        
        # Update context with new content
        context['content'] = result.data
        
        return True
    
    def _success_result(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build success result"""
        self.logger.info(f"\n{'='*80}")
        self.logger.info("🎉 VALIDATION PIPELINE SUCCESS")
        self.logger.info(f"{'='*80}\n")
        
        return {
            'success': True,
            'content': context['content'],
            'attempts': context['attempt'],
            'composite_score': context.get('composite_score', 0.0),
            'quality_results': context.get('winston_result', {}),
            'gate_results': context.get('gate_results', {}),
            'step_durations': context.get('step_durations', {})
        }
    
    def _failure_result(self, reason: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build failure result"""
        self.logger.error(f"\n{'='*80}")
        self.logger.error(f"❌ VALIDATION PIPELINE FAILED: {reason}")
        self.logger.error(f"{'='*80}\n")
        
        return {
            'success': False,
            'content': context.get('content', ''),
            'attempts': context.get('attempt', 0),
            'reason': reason,
            'step_durations': context.get('step_durations', {})
        }
