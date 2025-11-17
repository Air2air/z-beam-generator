"""
Global Subjective Evaluation System

Centralized evaluation that runs after ANY content generation (caption, subtitle, FAQ, etc.).
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
from shared.api.client_factory import create_api_client
from shared.commands.subjective_evaluation_helper import SubjectiveEvaluationHelper
from processing.detection.winston_feedback_db import WinstonFeedbackDatabase
from processing.config.config_loader import get_config
from data.materials.loader import load_material

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
        component_type: 'caption', 'subtitle', 'faq', etc.
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
        print(f"🔍 [DEBUG] Helper created, about to evaluate...")
        
        # Run evaluation
        result = helper.evaluate_generation(
            content=content,
            topic=topic,
            component_type=component_type,
            domain=domain
        )
        
        print(f"🔍 [DEBUG] Evaluation returned: {result is not None}")
        if result:
            print(f"🔍 [DEBUG] Has narrative: {result.narrative_assessment is not None}")
        
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
        component_type: 'caption', 'subtitle', 'faq', etc.
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
            
            if component_type == 'caption':
                caption_data = material.get('caption')
                if isinstance(caption_data, dict):
                    # Caption has 'before' and 'after' - evaluate the 'after' version
                    return caption_data.get('after', caption_data.get('before'))
                return caption_data
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
