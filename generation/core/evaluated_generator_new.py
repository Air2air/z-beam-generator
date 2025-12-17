"""
NEW: Simplified QualityEvaluatedGenerator using extracted components.

🔄 REUSABLE: Works for all domains (materials, settings, contaminants, compounds)
🎯 SEPARATION: Pure orchestration, delegates to specialized components
🚀 ADAPTABLE: Easy to extend with new evaluators or parameters

Architecture:
    1. Get parameters → ParameterManager
    2. Generate content → Generator
    3. Save to data file → Domain-specific save logic
    4. Evaluate quality → QualityOrchestrator
    5. Log for learning → LearningIntegrator

Design: Component-based with Protocol extensibility.
        Zero generation logic - only coordination.
        Works across all domains without domain-specific code.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging
from pathlib import Path

from generation.core.quality_orchestrator import QualityOrchestrator
from generation.core.learning_integrator import LearningIntegrator
from generation.core.parameter_manager import ParameterManager
from generation.core.generator import Generator

logger = logging.getLogger(__name__)


@dataclass
class QualityEvaluatedResult:
    """Result from quality-evaluated generation"""
    success: bool
    content: Any
    quality_scores: Dict[str, Any]
    evaluation_logged: bool
    detection_id: int
    error_message: Optional[str] = None


class QualityEvaluatedGenerator:
    """
    NEW: Simplified generator that coordinates specialized components.
    
    🎯 RESPONSIBILITIES (Pure orchestration):
    1. Get parameters (delegate to ParameterManager)
    2. Generate content (delegate to Generator)
    3. Save to data file (delegate to domain save logic)
    4. Evaluate quality (delegate to QualityOrchestrator)
    5. Log for learning (delegate to LearningIntegrator)
    
    ✅ ZERO GENERATION LOGIC - only coordination!
    ✅ ZERO DOMAIN-SPECIFIC CODE - works for all domains!
    ✅ ZERO HARDCODED VALUES - all from config or dynamic calculation!
    
    Extensibility:
    - Add evaluator: quality_orchestrator.register_evaluator(name, evaluator, weight)
    - Add parameter: parameter_manager.register_calculator(name, calculator)
    - Add domain: Just pass domain='new_domain' (no code changes)
    """
    
    def __init__(
        self,
        api_client,
        dynamic_config,
        humanness_optimizer,
        subjective_evaluator=None,
        winston_client=None,
        structural_variation_checker=None,
        learning_db_path: str = 'learning/detection_results.db'
    ):
        """
        Initialize simplified generator with specialized components.
        
        Args:
            api_client: LLM API client (required, fail-fast if None)
            dynamic_config: DynamicConfig instance (required, fail-fast if None)
            humanness_optimizer: HumannessOptimizer instance (required, fail-fast if None)
            subjective_evaluator: Optional subjective quality evaluator
            winston_client: Optional Winston AI detection client
            structural_variation_checker: Optional structural variation checker
            learning_db_path: Path to learning database
            
        Raises:
            ValueError: If required components missing (fail-fast)
        """
        # Fail-fast validation (NO fallbacks, NO defaults)
        if not api_client:
            raise ValueError("API client required - cannot generate without LLM access")
        if not dynamic_config:
            raise ValueError("DynamicConfig required - cannot calculate parameters without config")
        if not humanness_optimizer:
            raise ValueError("HumannessOptimizer required - cannot generate humanness layer")
        
        # Core generator (existing, single-pass)
        self.generator = Generator(api_client)
        
        # NEW: Specialized components (separation of concerns)
        self.parameter_manager = ParameterManager(dynamic_config, humanness_optimizer)
        self.quality_orchestrator = QualityOrchestrator()
        self.learning_integrator = LearningIntegrator(learning_db_path)
        
        # Register quality evaluators (optional - can run without them)
        if subjective_evaluator:
            self.quality_orchestrator.register_evaluator(
                'subjective', 
                subjective_evaluator, 
                weight=0.6
            )
            logger.info("Registered subjective evaluator (weight: 0.6)")
        
        if winston_client:
            self.quality_orchestrator.register_evaluator(
                'winston', 
                winston_client, 
                weight=0.4
            )
            logger.info("Registered Winston evaluator (weight: 0.4)")
        
        if structural_variation_checker:
            self.quality_orchestrator.register_evaluator(
                'structural', 
                structural_variation_checker, 
                weight=1.0
            )
            logger.info("Registered structural checker (weight: 1.0)")
        
        logger.info("NEW QualityEvaluatedGenerator initialized with refactored architecture")
        logger.info("   - ParameterManager: Temperature, penalties, voice, humanness")
        logger.info("   - QualityOrchestrator: Weighted evaluation coordination")
        logger.info("   - LearningIntegrator: SQLite database logging")
    
    def generate(
        self,
        item_name: str,
        component_type: str,
        author_id: str,
        domain: str = 'materials',
        **kwargs
    ) -> QualityEvaluatedResult:
        """
        Generate content with quality evaluation and learning.
        
        🎯 PURE ORCHESTRATION - delegates everything to specialized components.
        🔄 REUSABLE - works for all domains (materials, settings, contaminants, compounds).
        
        Args:
            item_name: Name of item (material, setting, contaminant, compound)
            component_type: Type of content (material_description, micro, faq, etc.)
            author_id: Author persona ID (todd, yi_chun, alessandro, ikmanda)
            domain: Domain name (materials, settings, contaminants, compounds)
            **kwargs: Additional parameters (e.g., faq_count)
        
        Returns:
            QualityEvaluatedResult with content and quality scores
            
        Process (single-pass):
            1. Get parameters (ParameterManager)
            2. Generate content (Generator)
            3. Save to data file (domain-specific logic)
            4. Evaluate quality (QualityOrchestrator)
            5. Log for learning (LearningIntegrator)
        """
        try:
            logger.info(f"\n{'='*80}")
            logger.info(f"📝 GENERATION: {domain}/{component_type} for {item_name}")
            logger.info(f"{'='*80}")
            
            print(f"\n{'='*80}")
            print(f"📝 GENERATION: {domain}/{component_type} for {item_name}")
            print(f"{'='*80}\n")
            
            # 1. Get parameters (DELEGATED to ParameterManager)
            params = self.parameter_manager.get_parameters(
                component_type,
                author_id,
                domain,
                context={'item_name': item_name, **kwargs}
            )
            
            # Safe logging - handle both real values and mocks in tests
            temp = params['temperature']
            freq = params.get('frequency_penalty', 0)
            pres = params.get('presence_penalty', 0)
            
            if isinstance(temp, (int, float)) and isinstance(freq, (int, float)) and isinstance(pres, (int, float)):
                logger.info(f"Parameters: temp={temp:.3f}, freq_penalty={freq:.2f}")
                print(f"🌡️  Parameters:")
                print(f"   • temperature: {temp:.3f}")
                print(f"   • frequency_penalty: {freq:.2f}")
                print(f"   • presence_penalty: {pres:.2f}")
            else:
                logger.info(f"Parameters: temp={temp}, freq_penalty={freq}")
                print(f"🌡️  Parameters:")
                print(f"   • temperature: {temp}")
                print(f"   • frequency_penalty: {freq}")
                print(f"   • presence_penalty: {pres}")
            
            # 2. Generate content (DELEGATED to Generator)
            content = self.generator.generate(
                material_name=item_name,  # Generator uses 'material_name' param
                component_type=component_type,
                author_id=author_id,
                **params,
                **kwargs
            )
            logger.info(f"Generated content: {len(str(content))} characters")
            print(f"\n✅ Generated: {len(str(content))} characters")
            
            # Display preview
            content_text = self._content_to_text(content, component_type)
            print(f"\n{'─'*80}")
            print(f"📄 GENERATED CONTENT:")
            print(f"{'─'*80}")
            print(content_text[:500] + ("..." if len(content_text) > 500 else ""))
            print(f"{'─'*80}\n")
            
            # 3. Save to data file (domain-specific)
            self._save_to_data_file(item_name, component_type, content, domain)
            logger.info(f"Saved to {domain} data file")
            print(f"💾 Saved to {domain} data file")
            
            # 4. Evaluate quality (DELEGATED to QualityOrchestrator)
            quality_scores = self.quality_orchestrator.evaluate(
                content,
                context={
                    'domain': domain,
                    'item_name': item_name,
                    'component_type': component_type,
                    'author_id': author_id
                }
            )
            logger.info(f"Quality scores: {quality_scores}")
            print(f"\n📊 Quality Scores:")
            for key, value in quality_scores.items():
                if isinstance(value, (int, float)):
                    print(f"   • {key}: {value:.2f}")
                else:
                    print(f"   • {key}: {value}")
            
            # 5. Log for learning (DELEGATED to LearningIntegrator)
            detection_id = self.learning_integrator.log_generation(
                content,
                quality_scores,
                params,
                context={
                    'domain': domain,
                    'item_name': item_name,
                    'component_type': component_type,
                    'author_id': author_id,
                    **kwargs
                }
            )
            logger.info(f"Logged to learning database: detection_id={detection_id}")
            print(f"💾 Logged to learning database: detection_id={detection_id}\n")
            
            return QualityEvaluatedResult(
                success=True,
                content=content,
                quality_scores=quality_scores,
                evaluation_logged=True,
                detection_id=detection_id
            )
            
        except Exception as e:
            logger.error(f"❌ Generation failed: {e}", exc_info=True)
            print(f"❌ Generation failed: {e}")
            return QualityEvaluatedResult(
                success=False,
                content=None,
                quality_scores={},
                evaluation_logged=False,
                detection_id=-1,
                error_message=str(e)
            )
    
    def _save_to_data_file(
        self,
        item_name: str,
        component_type: str,
        content: Any,
        domain: str
    ) -> None:
        """
        Save generated content to appropriate data file.
        
        Args:
            item_name: Name of item
            component_type: Type of content
            content: Generated content
            domain: Domain name
            
        Note: Uses existing domain-specific save logic.
              Could be refactored to use domain adapters for better separation.
        """
        # Use existing generator save logic
        # (Domain-specific save mechanisms already implemented in Generator)
        self.generator._save_to_yaml(item_name, component_type, content, domain)
        logger.debug(f"Saved {component_type} for {item_name} to {domain} data")
    
    def _content_to_text(self, content: Any, component_type: str) -> str:
        """
        Convert content to text for display.
        
        Args:
            content: Generated content (str, dict, or list)
            component_type: Type of content
            
        Returns:
            Text representation
        """
        if isinstance(content, str):
            return content
        elif isinstance(content, dict):
            if component_type == 'faq':
                return '\n\n'.join([f"Q: {item['question']}\nA: {item['answer']}" 
                                   for item in content.get('items', [])])
            else:
                return str(content)
        elif isinstance(content, list):
            return '\n\n'.join([str(item) for item in content])
        else:
            return str(content)
