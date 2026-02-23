#!/usr/bin/env python3
"""
Generation Command Handlers

Handles AI-powered content generation commands.

Architecture: Domain-agnostic design - all domains use same handler with
different configs from domains/*/config.yaml. No hardcoded domain logic.

The unified pipeline:
1. Load domain config from domains/{domain}/config.yaml
2. Use DomainAdapter for data access
3. Use Generator for content generation
4. Use PromptBuilder for prompt construction
5. Use DynamicConfig for generation parameters
"""


def handle_generation(
    identifier: str,
    component_type: str,
    domain: str = 'materials',
    skip_integrity_check: bool = False,
    **kwargs
):
    """
    Generate AI-powered content for ANY domain and component type.
    
    Domain-agnostic handler - behavior determined by:
    - domains/{domain}/config.yaml (prompts, data paths)
    - generation/config.yaml (extraction strategies)
    - DynamicConfig (generation parameters)
    
    NO domain-specific branching in this code.
    
    Args:
        identifier: Item name (material, setting, etc.) - domain agnostic
        component_type: Type of component (micro, subtitle, faq, etc.)
        domain: Domain name (e.g., 'materials', 'settings')
        skip_integrity_check: Skip pre-generation checks
        **kwargs: Additional parameters (e.g., faq_count for FAQ generation)
        
    Returns:
        bool: True if generation successful, False otherwise
    """
    # Get component metadata from registry (icon, etc.)
    from shared.text.utils.component_specs import ComponentRegistry
    
    try:
        spec = ComponentRegistry.get_spec(component_type)
    except KeyError as e:
        print(f"❌ Error: {e}")
        return False
    
    # Display header with component type and domain
    component_label = component_type.upper().replace('_', ' ')
    icon_map = {
        'micro': '📝',
        'pageDescription': '📌',
        'settings_description': '⚙️',
        'component_summary': '📋',
        'faq': '❓',
        'troubleshooter': '🔧',
        'page_title': '🔍',
        'meta_description': '📄'
    }
    icon = icon_map.get(component_type, '📝')
    
    print("="*80)
    print(f"{icon} {component_label} GENERATION: {identifier} ({domain} domain)")
    print("="*80)
    print()
    
    # Run pre-generation integrity check
    from shared.commands.integrity_helper import run_pre_generation_check
    if not run_pre_generation_check(skip_check=skip_integrity_check, quick=True):
        return False
    
    try:
        # === Use unified Generator with domain adapter ===
        from generation.core.generator import Generator

        # Initialize API client
        from shared.api.client_factory import create_api_client
        print("🔧 Initializing API client...")
        api_client = create_api_client('grok')
        print("✅ API client ready")
        print()
        
        # Initialize generator with domain (uses DomainAdapter internally)
        print(f"🔧 Initializing Generator for '{domain}' domain...")
        generator = Generator(api_client, domain=domain)
        print("✅ Generator ready")
        print()
        
        # Generate content (domain-agnostic)
        print(f"🤖 Generating AI-powered {component_type}...")
        print(f"   Component: {component_type}")
        print(f"   Domain: {domain}")
        print(f"   Target Base: {spec.default_length} words (multiplier-driven variation)")
        print()
        
        generation_succeeded = True
        content_data = None
        generation_error = None
        
        try:
            content_data = generator.generate(identifier, component_type, **kwargs)
            
            print(f"✅ {component_label.capitalize()} generated and saved")
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
                
                # Get most recent attempt for this identifier/component
                cursor.execute("""
                    SELECT generated_text
                    FROM detection_results
                    WHERE material = ? AND component_type = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                """, (identifier, component_type))
                
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
            # Generator returns dict with 'content' key; database returns raw content
            actual_content = content_data.get('content', content_data) if isinstance(content_data, dict) and 'content' in content_data else content_data
            full_content = _extract_content_for_display(actual_content, component_type, spec)
            
            # POLICY: Always show complete generation report after each generation (success OR failure)
            _show_generation_report(full_content, identifier, component_type, 
                                   succeeded=generation_succeeded, error=generation_error)
        
        # NOTE: Subjective evaluation is ONLY for training mode (quality-gated generation)
        # Production mode (default) has ZERO evaluation for fast single-pass generation
        # Evaluation runs during quality gate BEFORE save in training mode only
        
        if generation_succeeded:
            print(f"✨ {component_label.capitalize()} generation complete!")
            print()
            
            # Run post-generation validation
            from shared.commands.integrity_helper import run_post_generation_validation
            run_post_generation_validation(identifier, component_type, quick=True)
            
            # Check if we should update sweet spot recommendations (generic learning)
            _update_sweet_spot_if_needed(identifier, component_type)
            
            # Run post-generation integrity check
            _run_post_generation_integrity(identifier, component_type)
            
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
        # Micro: dict with 'before' and 'after'
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


def _show_generation_report(content, identifier, component_type, succeeded=True, error=None):
    """
    Display complete generation report (policy requirement).
    
    Shows content even when generation fails quality gates, enabling analysis.
    
    Args:
        content: Generated content to display
        identifier: Domain-agnostic item identifier (material name, setting name, etc.)
        component_type: Type of component generated
        succeeded: Whether generation passed quality gates
        error: Error message if generation failed
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
        # Determine storage file based on component type (domain-agnostic)
        if 'settings' in component_type or component_type == 'component_summary':
            storage_file = "Settings.yaml"
        else:
            storage_file = "Materials.yaml"
        print(f"   • Location: data/materials/{storage_file}")
        print(f"   • Component: {component_type}")
        print(f"   • Item: {identifier}")
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
        print(f"   • Item: {identifier}")
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


def _run_subjective_evaluation(content, identifier, component_type):
    """Run subjective evaluation (domain-agnostic).
    
    Args:
        content: Generated content to evaluate
        identifier: Domain-agnostic item identifier
        component_type: Type of component generated
    """
    from shared.api.client_factory import create_api_client
    from shared.commands.subjective_evaluation_helper import SubjectiveEvaluationHelper
    
    print("🔍 Running subjective evaluation (Grok API)...")
    eval_client = create_api_client('grok')
    helper = SubjectiveEvaluationHelper(
        api_client=eval_client,
        verbose=True
    )
    
    # Determine domain from component type
    if 'settings' in component_type or component_type == 'component_summary':
        domain = 'settings'
    else:
        domain = 'materials'
    
    eval_result = helper.evaluate_generation(
        content=content,
        topic=identifier,
        component_type=component_type,
        domain=domain
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
        material_name=identifier,  # Keep param name for compatibility
        component_type=component_type,
        content=content,
        evaluation=evaluation_data
    )
    print(f"📄 Report saved: {report_path}")
    print()


def _run_winston_detection(content, identifier, component_type, api_client):
    """Run Winston API detection (domain-agnostic).
    
    Args:
        content: Generated content to analyze
        identifier: Domain-agnostic item identifier
        component_type: Type of component generated
        api_client: API client for generation (not used for Winston)
    """
    print("🤖 Running Winston AI detection...")
    try:
        from generation.config.config_loader import get_config
        from postprocessing.detection.winston_feedback_db import WinstonFeedbackDatabase
        from postprocessing.detection.winston_integration import WinstonIntegration
        from shared.api.client_factory import APIClientFactory
        from shared.text.validation.constants import ValidationConstants
        
        config = get_config()
        if 'winston_feedback_db_path' not in config.config:
            raise KeyError("Missing required config key: winston_feedback_db_path")
        db_path = config.config['winston_feedback_db_path']
        if not db_path:
            raise ValueError("winston_feedback_db_path must be configured and non-empty")
        feedback_db = WinstonFeedbackDatabase(db_path)
        
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
            material=identifier,
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
        print("\n❌ CRITICAL ERROR: Winston detection failed")
        print(f"   Error: {e}")
        print("\n   Fix: Configure Winston API in .env file")
        print("   See: setup/API_CONFIGURATION.md")
        raise RuntimeError(f"Winston API detection required but failed: {e}")


def _update_sweet_spot_if_needed(identifier, component_type):
    """Update sweet spot recommendations if threshold met (domain-agnostic).
    
    Args:
        identifier: Domain-agnostic item identifier
        component_type: Type of component generated
    """
    from generation.config.config_loader import get_config
    from postprocessing.detection.winston_feedback_db import WinstonFeedbackDatabase
    
    config = get_config()
    if 'winston_feedback_db_path' not in config.config:
        raise KeyError("Missing required config key: winston_feedback_db_path")
    db_path = config.config['winston_feedback_db_path']
    if not db_path:
        raise ValueError("winston_feedback_db_path must be configured and non-empty")
    sweet_spot_min_samples = int(
        config.get_required_config('constants.sweet_spot_analyzer.min_samples')
    )
    sweet_spot_success_threshold = float(
        config.get_required_config('constants.sweet_spot_analyzer.success_threshold')
    )
    feedback_db = WinstonFeedbackDatabase(db_path)
    
    if feedback_db and feedback_db.should_update_sweet_spot('*', '*', min_samples=sweet_spot_min_samples):
        print("📊 Updating generic sweet spot recommendations...")
        try:
            from learning.sweet_spot_analyzer import SweetSpotAnalyzer
            analyzer = SweetSpotAnalyzer(
                db_path,
                min_samples=sweet_spot_min_samples,
                success_threshold=sweet_spot_success_threshold,
            )
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


def _run_post_generation_integrity(identifier, component_type):
    """Run post-generation integrity check (domain-agnostic).
    
    Args:
        identifier: Domain-agnostic item identifier
        component_type: Type of component generated
    """
    print("🔍 Running post-generation integrity check...")
    from generation.integrity import IntegrityChecker
    checker = IntegrityChecker()
    post_results = checker.run_post_generation_checks(
        material=identifier,
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
# All new code should use handle_generation(identifier, component_type, domain=...) instead.
# ============================================================================

def handle_micro_generation(material_name: str, skip_integrity_check: bool = False):
    """
    DEPRECATED: Use handle_generation(material_name, 'micro') instead.
    
    Generate AI-powered micro for a material and save to Materials.yaml.
    This is a backward compatibility wrapper around the generic handler.
    """
    return handle_generation(material_name, 'micro', domain='materials', skip_integrity_check=skip_integrity_check)


def handle_description_generation(material_name: str, skip_integrity_check: bool = False):
    """
    DEPRECATED: Use handle_generation(material_name, 'description') instead.
    
    Generate AI-powered material description for a material and save to Materials.yaml.
    This is a backward compatibility wrapper around the generic handler.
    """
    return handle_generation(material_name, 'description', domain='materials', skip_integrity_check=skip_integrity_check)


def handle_settings_description_generation(material_name: str, skip_integrity_check: bool = False):
    """
    DEPRECATED: Use handle_generation(material_name, 'settings_description', domain='settings') instead.
    
    Generate AI-powered settings description for a material and save to Settings.yaml.
    This is a backward compatibility wrapper around the generic handler.
    """
    return handle_generation(material_name, 'settings_description', domain='settings', skip_integrity_check=skip_integrity_check)


def handle_component_summaries_generation(material_name: str, skip_integrity_check: bool = False):
    """
    DEPRECATED: Use generate_component_summaries(material_name, domain='settings') instead.
    
    Generate AI-powered component summaries for a material's Settings page.
    Uses per-component generation to keep prompts under API limits.
    """
    from .component_summaries_handler import generate_component_summaries
    return generate_component_summaries(material_name, skip_integrity_check, domain='settings')


def handle_faq_generation(material_name: str, skip_integrity_check: bool = False):
    """
    Generate AI-powered FAQ for a material and save to Materials.yaml.
    This is a backward compatibility wrapper around the generic handler.
    """
    return handle_generation(material_name, 'faq', domain='materials', skip_integrity_check=skip_integrity_check)



