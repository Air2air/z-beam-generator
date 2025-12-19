"""
Global Subjective Evaluation System

Centralized evaluation that runs after ANY content generation (micro, subtitle, FAQ, etc.).
Eliminates duplicate evaluation code in component handlers.

Architecture:
    Generation Handler → Returns → Global Evaluation Runs → Database Logging
    
Benefits:
    - Single evaluation point for all components
    - Consistent evaluation across all content types
    - Eliminates duplicate code in handlers
    - Easier to maintain and test
"""

import logging
from typing import Optional

from domains.materials.data_loader import load_material
from generation.config.config_loader import get_config
from postprocessing.detection.winston_feedback_db import WinstonFeedbackDatabase
from shared.api.client_factory import create_api_client
from shared.commands.subjective_evaluation_helper import SubjectiveEvaluationHelper

logger = logging.getLogger(__name__)


def run_global_subjective_evaluation(
    topic: str,
    component_type: str,
    domain: str = 'materials',
    verbose: bool = True
) -> None:
    """
    Run subjective evaluation after ANY content generation.
    
    This is the SINGLE ENTRY POINT for all subjective evaluations.
    Component handlers should NOT call evaluation directly.
    
    Args:
        topic: Material name, region name, etc.
        component_type: 'micro', 'subtitle', 'faq', etc.
        domain: 'materials', 'regions', 'applications', etc.
        verbose: Show detailed output
        
    Flow:
        1. Load generated content from Materials.yaml (or equivalent)
        2. Create Grok API client
        3. Run subjective evaluation
        4. Log to database
        5. Display results
    """
    
    print()
    print("🤖 Running subjective content evaluation...")
    print(f"🔍 [DEBUG] Topic: {topic}")
    print(f"🔍 [DEBUG] Component: {component_type}")
    print(f"🔍 [DEBUG] Domain: {domain}")
    
    try:
        # Load the generated content from data files
        content = _load_generated_content(topic, component_type, domain)
        if not content:
            print(f"   ⚠️  No content found for {topic}/{component_type}")
            print()
            return
        
        print(f"🔍 [DEBUG] Content loaded ({len(content)} chars)")
        
        # Create Grok API client for evaluation
        api_client = create_api_client('grok')
        print(f"🔍 [DEBUG] API client created: {api_client is not None}")
        
        # Initialize feedback database
        config = get_config()
        db_path = config.config.get('winston_feedback_db_path')
        feedback_db = None
        if db_path:
            feedback_db = WinstonFeedbackDatabase(db_path)
            print(f"🔍 [DEBUG] Database initialized: {feedback_db is not None}")
        else:
            print(f"🔍 [DEBUG] NO database path in config")
        
        # Create evaluation helper
        helper = SubjectiveEvaluationHelper(
            api_client=api_client,
            feedback_db=feedback_db
        )
        logger.debug("Helper created, about to evaluate...")
        
        # Run evaluation
        result = helper.evaluate_generation(
            content=content,
            topic=topic,
            component_type=component_type,
            domain=domain
        )
        logger.debug(f"Evaluation returned: {result is not None}")
        if result:
            logger.debug(f"Has narrative: {result.narrative_assessment is not None}")
        
        # Display results
        if result:
            print()
            print(f"   ✅ Quality: {result.overall_score:.1f}/10 - {'PASS' if result.passes_quality_gate else 'FAIL'}")
            
            # Show narrative assessment
            if result.narrative_assessment:
                print()
                print("   📝 Narrative Assessment:")
                print(f"      {result.narrative_assessment}")
            
            # Show dimension breakdown
            print()
            print("   📊 Quality Dimensions:")
            for score in result.dimension_scores:
                status = "✅" if score.score >= 7.0 else "⚠️"
                print(f"      {status} {score.dimension.value.replace('_', ' ').title()}: {score.score:.1f}/10")
            
            # Apply realism-based learning for future generations
            _apply_realism_learning(result, topic, component_type, feedback_db)
        
        print()
        
    except Exception as e:
        print(f"   ⚠️  Subjective evaluation unavailable: {e}")
        import traceback
        traceback.print_exc()
        print()


def _load_generated_content(topic: str, component_type: str, domain: str) -> Optional[str]:
    """
    Load generated content from appropriate data file.
    
    Args:
        topic: Material name, region name, etc.
        component_type: 'micro', 'subtitle', 'faq', etc.
        domain: 'materials', 'regions', 'applications', etc.
        
    Returns:
        Generated content string or None if not found
    """
    
    if domain == 'materials':
        try:
            material = load_material(topic)
            if not material:
                logger.warning(f"Material {topic} not found")
                return None
            
            if component_type == 'micro':
                micro_data = material.get('micro')
                if isinstance(micro_data, dict):
                    # Micro has 'before' and 'after' - evaluate the 'after' version
                    return micro_data.get('after', micro_data.get('before'))
                return micro_data
            elif component_type == 'subtitle':
                return material.get('subtitle')
            elif component_type == 'faq':
                faq = material.get('faq', {})
                if isinstance(faq, dict):
                    # Combine all FAQ Q&A pairs
                    pairs = []
                    for key in ['q1', 'q2', 'q3', 'q4', 'q5']:
                        q = faq.get(key, {}).get('question', '')
                        a = faq.get(key, {}).get('answer', '')
                        if q and a:
                            pairs.append(f"Q: {q}\nA: {a}")
                    return '\n\n'.join(pairs) if pairs else None
                return None
            else:
                # Generic field access
                return material.get(component_type)
                
        except Exception as e:
            logger.warning(f"Could not load {component_type} for {topic}: {e}")
            return None
    
    # Add support for other domains (regions, applications, etc.) here
    
    return None


def _apply_realism_learning(
    result,
    topic: str,
    component_type: str,
    feedback_db
) -> None:
    """
    Apply realism-based learning for future generations.
    
    Analyzes realism evaluation results and logs parameter optimization suggestions
    to the realism_learning table. Future generations will query this table to
    apply learned adjustments.
    
    Args:
        result: SubjectiveEvaluationResult with realism metrics
        topic: Material/region/etc. name
        component_type: 'micro', 'subtitle', etc.
        feedback_db: WinstonFeedbackDatabase instance
    """
    
    if not feedback_db or not result:
        return
    
    try:
        from learning.realism_optimizer import RealismOptimizer

        # Initialize optimizer
        optimizer = RealismOptimizer()
        
        # Get current parameters (simplified - in production would load from context)
        current_params = {
            'temperature': 0.8,
            'frequency_penalty': 0.0,
            'presence_penalty': 0.5,
            'voice_params': {}
        }
        
        # Calculate suggested adjustments based on realism scores
        ai_tendencies = {}
        for score in result.dimension_scores:
            dimension = score.dimension.value
            # Map dimensions to AI tendencies
            if dimension == 'voice_authenticity':
                ai_tendencies['generic_language'] = max(0, 7.0 - score.score) / 7.0
            elif dimension == 'tonal_consistency':
                ai_tendencies['hedge_words'] = max(0, 7.0 - score.score) / 7.0
            elif dimension == 'human_believability':
                ai_tendencies['formal_structure'] = max(0, 7.0 - score.score) / 7.0
        
        # Get suggested adjustments from optimizer
        if ai_tendencies:
            suggested_params = optimizer.suggest_parameter_adjustments(
                ai_tendencies=ai_tendencies,
                current_params=current_params
            )
            
            # Log to realism_learning table
            feedback_db.log_realism_learning(
                topic=topic,
                component_type=component_type,
                ai_tendencies=ai_tendencies,
                suggested_params=suggested_params,
                realism_score=result.overall_score
            )
            
            logger.info(f"📚 [LEARNING] Realism optimization logged for future {component_type} generations")
    
    except Exception as e:
        logger.warning(f"Failed to apply realism learning: {e}")
