#!/usr/bin/env python3
"""
Generation Command Handlers

Handles AI-powered content generation commands.

Architecture: Component-agnostic design - all components use same handler with
different templates/config. No hardcoded component types or branching logic.
"""


def handle_generation(
    material_name: str,
    component_type: str,
    skip_integrity_check: bool = False,
    **kwargs
):
    """
    Generate AI-powered content for ANY component type.
    
    Component-agnostic handler - behavior determined by:
    - prompts/components/{component_type}.txt (content instructions)
    - config.yaml component_lengths (length, extraction strategy)
    - ComponentRegistry (structural metadata)
    
    NO component-specific branching in this code.
    
    Args:
        material_name: Name of material to generate for
        component_type: Type of component (caption, subtitle, faq, etc.)
        skip_integrity_check: Skip pre-generation checks
        **kwargs: Additional parameters (e.g., faq_count for FAQ generation)
        
    Returns:
        bool: True if generation successful, False otherwise
    """
    # Get component metadata from registry (icon, etc.)
    from generation.core.component_specs import ComponentRegistry
    
    try:
        spec = ComponentRegistry.get_spec(component_type)
    except KeyError as e:
        print(f"❌ Error: {e}")
        return False
    
    # Display header with component type
    component_label = component_type.upper().replace('_', ' ')
    icon_map = {
        'caption': '📝',
        'subtitle': '📌',
        'faq': '❓',
        'description': '📄',
        'troubleshooter': '🔧'
    }
    icon = icon_map.get(component_type, '📝')
    
    print("="*80)
    print(f"{icon} {component_label} GENERATION: {material_name}")
    print("="*80)
    print()
    
    # Run pre-generation integrity check
    from shared.commands.integrity_helper import run_pre_generation_check
    if not run_pre_generation_check(skip_check=skip_integrity_check, quick=True):
        return False
    
    try:
        # Import required modules
        from domains.materials.coordinator import UnifiedMaterialsGenerator
        
        # Initialize API client (DeepSeek for consistency)
        from shared.api.client_factory import create_api_client
        print("🔧 Initializing DeepSeek API client...")
        api_client = create_api_client('deepseek')
        print("✅ DeepSeek client ready")
        print()
        
        # Initialize unified generator
        print("🔧 Initializing UnifiedMaterialsGenerator...")
        generator = UnifiedMaterialsGenerator(api_client)
        print("✅ Generator ready")
        print()
        
        # Generate content (component-agnostic)
        print(f"🤖 Generating AI-powered {component_type}...")
        print(f"   Component: {component_type}")
        print(f"   Target: {spec.default_length} words (range: {spec.min_length}-{spec.max_length})")
        print("   Note: Voice enhancement happens in post-processing")
        print()
        
        content_data = generator.generate(material_name, component_type, **kwargs)
        
        print(f"✅ {component_label.capitalize()} generated and saved to Materials.yaml")
        print()
        
        # DEBUG: Check what we received
        print(f"🔍 DEBUG: content_data type = {type(content_data)}")
        print(f"🔍 DEBUG: content_data = {content_data}")
        print()
        
        # Extract content for display (extraction strategy from config)
        full_content = _extract_content_for_display(content_data, component_type, spec)
        
        # POLICY: Always show complete generation report after each generation
        _show_generation_report(full_content, material_name, component_type)
        
        # Run subjective evaluation using Grok API
        _run_subjective_evaluation(full_content, material_name, component_type)
        
        # Run Winston AI detection and log to database  
        _run_winston_detection(full_content, material_name, component_type, api_client)
        
        print(f"✨ {component_label.capitalize()} generation complete!")
        print()
        
        # Run post-generation validation
        from shared.commands.integrity_helper import run_post_generation_validation
        run_post_generation_validation(material_name, component_type, quick=True)
        
        # Check if we should update sweet spot recommendations (generic learning)
        _update_sweet_spot_if_needed(material_name, component_type)
        
        # Run post-generation integrity check
        _run_post_generation_integrity(material_name, component_type)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during {component_type} generation: {e}")
        import traceback
        traceback.print_exc()
        return False


def _extract_content_for_display(content_data, component_type, spec):
    """Extract content for display based on component type and extraction strategy."""
    if spec.extraction_strategy == 'before_after':
        # Caption: dict with 'before' and 'after'
        if isinstance(content_data, dict):
            before_text = content_data.get('before', '')
            after_text = content_data.get('after', '')
            return f"BEFORE:\n{before_text}\n\nAFTER:\n{after_text}"
        return str(content_data)
    elif spec.extraction_strategy == 'json_list':
        # FAQ: list of Q&A dicts
        if isinstance(content_data, list):
            faq_parts = []
            for qa in content_data:
                q = qa.get('question', '')
                a = qa.get('answer', '')
                faq_parts.append(f"Q: {q}\nA: {a}")
            return "\n\n".join(faq_parts)
        return str(content_data)
    else:
        # Raw: return as-is (subtitle, description, etc.)
        return str(content_data)


def _show_generation_report(content, material_name, component_type):
    """Display complete generation report (policy requirement)."""
    print("=" * 80)
    print("📊 GENERATION COMPLETE REPORT")
    print("=" * 80)
    print()
    print("📝 GENERATED CONTENT:")
    print("-" * 80)
    print(content)
    print("-" * 80)
    print()
    print("📏 STATISTICS:")
    print(f"   • Length: {len(content)} characters")
    print(f"   • Word count: {len(content.split())} words")
    print()
    print("💾 STORAGE:")
    print("   • Location: data/materials/Materials.yaml")
    print(f"   • Component: {component_type}")
    print(f"   • Material: {material_name}")
    print()
    print("🔔 NOTE: Run --validate to check quality and improve with learning systems")
    print()
    print("=" * 80)
    print()


def _run_subjective_evaluation(content, material_name, component_type):
    """Run subjective evaluation (component-agnostic)."""
    from shared.commands.subjective_evaluation_helper import SubjectiveEvaluationHelper
    from shared.api.client_factory import create_api_client
    
    print("🔍 Running subjective evaluation (Grok API)...")
    eval_client = create_api_client('grok')
    helper = SubjectiveEvaluationHelper(
        api_client=eval_client,
        verbose=True
    )
    
    eval_result = helper.evaluate_generation(
        content=content,
        topic=material_name,
        component_type=component_type,
        domain='materials'
    )
    
    # Display narrative assessment if available
    if eval_result and eval_result.narrative_assessment:
        print()
        print("📊 SUBJECTIVE EVALUATION:")
        print("-" * 80)
        print(eval_result.narrative_assessment)
        print()
    print()
    
    # Save report to markdown file
    from postprocessing.reports.generation_report_writer import GenerationReportWriter
    writer = GenerationReportWriter()
    evaluation_data = {
        'narrative_assessment': eval_result.narrative_assessment if eval_result else None
    }
    report_path = writer.save_individual_report(
        material_name=material_name,
        component_type=component_type,
        content=content,
        evaluation=evaluation_data
    )
    print(f"📄 Report saved: {report_path}")
    print()


def _run_winston_detection(content, material_name, component_type, api_client):
    """Run Winston AI detection (component-agnostic)."""
    print("🤖 Running Winston AI detection...")
    try:
        from postprocessing.detection.winston_integration import WinstonIntegration
        from postprocessing.detection.winston_feedback_db import WinstonFeedbackDatabase
        from generation.config.config_loader import get_config
        from generation.validation.constants import ValidationConstants
        
        config = get_config()
        db_path = config.config.get('winston_feedback_db_path')
        feedback_db = WinstonFeedbackDatabase(db_path) if db_path else None
        
        # Initialize Winston integration
        winston = WinstonIntegration(
            winston_client=api_client,
            feedback_db=feedback_db,
            config=config.config
        )
        
        # Use constant threshold from validation constants
        ai_threshold = ValidationConstants.WINSTON_AI_THRESHOLD
        
        # Detect and log
        winston_result = winston.detect_and_log(
            text=content,
            material=material_name,
            component_type=component_type,
            temperature=0.7,
            attempt=1,
            max_attempts=1,
            ai_threshold=ai_threshold
        )
        
        ai_score = winston_result['ai_score']
        human_score = 1.0 - ai_score
        
        print(f"   🎯 AI Score: {ai_score*100:.1f}% (threshold: {ai_threshold*100:.1f}%)")
        print(f"   👤 Human Score: {human_score*100:.1f}%")
        
        if ai_score <= ai_threshold:
            print("   ✅ Winston check PASSED")
        else:
            print("   ⚠️  Winston check FAILED - consider regenerating")
        print()
        
    except Exception as e:
        print(f"   ⚠️  Winston detection failed: {e}")
        print("   Continuing without Winston validation...")
        print()


def _update_sweet_spot_if_needed(material_name, component_type):
    """Update sweet spot recommendations if threshold met (component-agnostic)."""
    from postprocessing.detection.winston_feedback_db import WinstonFeedbackDatabase
    from generation.config.config_loader import get_config
    
    config = get_config()
    db_path = config.config.get('winston_feedback_db_path')
    feedback_db = WinstonFeedbackDatabase(db_path) if db_path else None
    
    if feedback_db and feedback_db.should_update_sweet_spot('*', '*', min_samples=3):
        print("📊 Updating generic sweet spot recommendations...")
        try:
            from learning.sweet_spot_analyzer import SweetSpotAnalyzer
            analyzer = SweetSpotAnalyzer(db_path, min_samples=3, success_threshold=0.80)
            results = analyzer.get_sweet_spot_table(save_to_db=True)
            
            if results['sweet_spots']:
                print("   ✅ Sweet spot recommendations updated")
                print(f"   📈 Based on {results['metadata']['sample_count']} samples")
                print(f"   🎯 Confidence: {results['metadata']['confidence_level']}")
            else:
                print("   ⚠️  Not enough data for sweet spot calculation")
            print()
        except Exception as e:
            print(f"   ⚠️  Could not update sweet spot: {e}")
            print()


def _run_post_generation_integrity(material_name, component_type):
    """Run post-generation integrity check (component-agnostic)."""
    print("🔍 Running post-generation integrity check...")
    from generation.integrity import IntegrityChecker
    checker = IntegrityChecker()
    post_results = checker.run_post_generation_checks(
        material=material_name,
        component_type=component_type
    )
    
    # Print post-gen results
    post_pass = sum(1 for r in post_results if r.status.value == 'PASS')
    post_warn = sum(1 for r in post_results if r.status.value == 'WARN')
    post_fail = sum(1 for r in post_results if r.status.value == 'FAIL')
    
    print(f"   {post_pass} passed, {post_warn} warnings, {post_fail} failed")
    
    for result in post_results:
        icon = {"FAIL": "❌", "WARN": "⚠️", "PASS": "✅"}[result.status.value]
        print(f"   {icon} {result.check_name}: {result.message}")
    
    print()


# ============================================================================
# DEPRECATED COMPONENT-SPECIFIC HANDLERS (Backward Compatibility)
# ============================================================================
# These handlers are maintained for backward compatibility but are DEPRECATED.
# All new code should use handle_generation(material, component_type) instead.
# ============================================================================

def handle_caption_generation(material_name: str, skip_integrity_check: bool = False):
    """
    DEPRECATED: Use handle_generation(material_name, 'caption') instead.
    
    Generate AI-powered caption for a material and save to Materials.yaml.
    This is a backward compatibility wrapper around the generic handler.
    """
    return handle_generation(material_name, 'caption', skip_integrity_check)


def handle_subtitle_generation(material_name: str, skip_integrity_check: bool = False):
    """
    DEPRECATED: Use handle_generation(material_name, 'subtitle') instead.
    
    Generate AI-powered subtitle for a material and save to Materials.yaml.
    This is a backward compatibility wrapper around the generic handler.
    """
    return handle_generation(material_name, 'subtitle', skip_integrity_check)


def handle_faq_generation(material_name: str, skip_integrity_check: bool = False):
    """
    DEPRECATED: Use handle_generation(material_name, 'faq') instead.
    
    Generate AI-powered FAQ for a material and save to Materials.yaml.
    This is a backward compatibility wrapper around the generic handler.
    """
    return handle_generation(material_name, 'faq', skip_integrity_check)


