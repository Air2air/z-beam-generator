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
        'material_description': '📌',
        'settings_description': '⚙️',
        'faq': '❓',
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
        # === Use UnifiedMaterialsGenerator with training_mode parameter ===
        from domains.materials.coordinator import UnifiedMaterialsGenerator
        
        # Initialize API client
        from shared.api.client_factory import create_api_client
        print("🔧 Initializing API client...")
        api_client = create_api_client('grok')
        print("✅ API client ready")
        print()
        
        # Initialize unified materials generator (PRODUCTION MODE: training_mode=False)
        print("🔧 Initializing UnifiedMaterialsGenerator...")
        generator = UnifiedMaterialsGenerator(api_client, training_mode=False)
        print("✅ Generator ready (production mode: fast, no quality gates)")
        print()
        
        # Generate content (component-agnostic)
        print(f"🤖 Generating AI-powered {component_type}...")
        print(f"   Component: {component_type}")
        print(f"   Target: {spec.default_length} words (range: {spec.min_length}-{spec.max_length})")
        print("   Note: Voice enhancement happens in post-processing")
        print()
        
        generation_succeeded = True
        content_data = None
        generation_error = None
        
        try:
            content_data = generator.generate(material_name, component_type, **kwargs)
            
            print(f"✅ {component_label.capitalize()} generated and saved to Materials.yaml")
            print()
            
        except Exception as gen_error:
            generation_succeeded = False
            generation_error = str(gen_error)
            
            # Try to get the last generated content from database for display
            print(f"⚠️  Generation failed after multiple attempts")
            print(f"   Retrieving last attempt for analysis...")
            print()
            
            try:
                import sqlite3
                conn = sqlite3.connect('z-beam.db')
                cursor = conn.cursor()
                
                # Get most recent attempt for this material/component
                cursor.execute("""
                    SELECT generated_text
                    FROM detection_results
                    WHERE material = ? AND component_type = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                """, (material_name, component_type))
                
                result = cursor.fetchone()
                if result:
                    content_data = result[0]
                    print(f"✅ Retrieved last generated attempt for review")
                    print()
                conn.close()
                
            except Exception as db_error:
                print(f"⚠️  Could not retrieve last attempt: {db_error}")
                print()
        
        # Extract content for display (even on failure)
        if content_data:
            full_content = _extract_content_for_display(content_data, component_type, spec)
            
            # POLICY: Always show complete generation report after each generation (success OR failure)
            _show_generation_report(full_content, material_name, component_type, 
                                   succeeded=generation_succeeded, error=generation_error)
        
        # NOTE: Subjective evaluation is ONLY for training mode (quality-gated generation)
        # Production mode (default) has ZERO evaluation for fast single-pass generation
        # Evaluation runs during quality gate BEFORE save in training mode only
        
        if generation_succeeded:
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
        else:
            print(f"❌ {component_label.capitalize()} generation failed!")
            print(f"   Error: {generation_error}")
            print()
            print("💡 The last generated attempt is shown above for analysis.")
            print("   Review the content and quality scores to understand why it failed.")
            print()
            return False
        
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


def _show_generation_report(content, material_name, component_type, succeeded=True, error=None):
    """
    Display complete generation report (policy requirement).
    
    Shows content even when generation fails quality gates, enabling analysis.
    """
    status_emoji = "✅" if succeeded else "⚠️"
    status_text = "SUCCESS" if succeeded else "FAILED QUALITY GATES"
    
    print("=" * 80)
    print(f"📊 GENERATION {status_text} REPORT")
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
    
    if succeeded:
        print("📈 QUALITY METRICS:")
        print(f"   • Status: {status_emoji} PASSED all quality gates")
        print()
        print("💾 STORAGE:")
        # settings_description goes to Settings.yaml, everything else to Materials.yaml
        storage_file = "Settings.yaml" if component_type == 'settings_description' else "Materials.yaml"
        print(f"   • Location: data/materials/{storage_file}")
        print(f"   • Component: {component_type}")
        print(f"   • Material: {material_name}")
        print(f"   • Saved: {status_emoji} YES")
    else:
        print("📈 QUALITY METRICS:")
        print(f"   • Status: {status_emoji} FAILED quality gates")
        if error:
            # Extract quality scores from error message
            print(f"   • Failure reason: {error[:200]}...")
        print()
        print("💾 STORAGE:")
        print("   • Location: NOT SAVED (failed quality gates)")
        print(f"   • Component: {component_type}")
        print(f"   • Material: {material_name}")
        print(f"   • Saved: ❌ NO")
        print()
        print("💡 ANALYSIS:")
        print("   This content failed quality gates but is shown for review.")
        print("   Check the quality scores above to understand why it was rejected.")
        print("   The system will continue learning from these attempts.")
    
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
    """Run Winston API detection (component-agnostic)."""
    print("🤖 Running Winston AI detection...")
    try:
        from postprocessing.detection.winston_integration import WinstonIntegration
        from postprocessing.detection.winston_feedback_db import WinstonFeedbackDatabase
        from generation.config.config_loader import get_config
        from generation.validation.constants import ValidationConstants
        from shared.api.client_factory import APIClientFactory
        
        config = get_config()
        db_path = config.config.get('winston_feedback_db_path')
        feedback_db = WinstonFeedbackDatabase(db_path) if db_path else None
        
        # Create Winston-specific API client (not DeepSeek)
        winston_client = APIClientFactory.create_client(provider="winston")
        
        # Initialize Winston integration
        winston = WinstonIntegration(
            winston_client=winston_client,
            feedback_db=feedback_db,
            config=config.config
        )
        
        # Use dynamic threshold from database learning
        ai_threshold = ValidationConstants.get_winston_threshold(use_learned=True)
        print(f"   Using learned Winston threshold: {ai_threshold:.3f}")
        
        # Calculate temperature dynamically from voice configuration
        # Note: This temperature is for database logging/analysis only.
        # Winston API analyzes text content, not generation parameters.
        # Using DynamicConfig ensures consistency with generation settings.
        from generation.config.dynamic_config import DynamicConfig
        dynamic_config = DynamicConfig()
        generation_temp = dynamic_config.calculate_temperature(component_type)
        
        # Detect and log
        winston_result = winston.detect_and_log(
            text=content,
            material=material_name,
            component_type=component_type,
            temperature=generation_temp,
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
        # Winston detection optional for short content (captions often <300 chars)
        error_msg = str(e)
        if 'Text too short' in error_msg or 'not configured' in error_msg:
            print("\n⚠️  WARNING: Winston detection skipped")
            print(f"   Reason: {e}")
            print("\n   ℹ️  Content saved but not validated by Winston API.")
            print("   Subjective evaluation (Grok) was completed successfully.")
            print("\n   To enable Winston: Configure API in .env file")
            print("   See: setup/API_CONFIGURATION.md")
            print()
        else:
            # Other errors should still fail-fast
            print("\n❌ CRITICAL ERROR: Winston detection failed")
            print(f"   Error: {e}")
            print("\n   Fix: Configure Winston API in .env file")
            print("   See: setup/API_CONFIGURATION.md")
            raise RuntimeError(f"Winston API detection required but failed: {e}")


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


def handle_material_description_generation(material_name: str, skip_integrity_check: bool = False):
    """
    Generate AI-powered material description for a material and save to Materials.yaml.
    This is a backward compatibility wrapper around the generic handler.
    """
    return handle_generation(material_name, 'material_description', skip_integrity_check)


def handle_settings_description_generation(material_name: str, skip_integrity_check: bool = False):
    """
    Generate AI-powered settings description for a material and save to Settings.yaml.
    This is a backward compatibility wrapper around the generic handler.
    """
    return handle_generation(material_name, 'settings_description', skip_integrity_check)


def handle_faq_generation(material_name: str, skip_integrity_check: bool = False):
    """
    Generate AI-powered FAQ for a material and save to Materials.yaml.
    This is a backward compatibility wrapper around the generic handler.
    """
    return handle_generation(material_name, 'faq', skip_integrity_check)



