#!/usr/bin/env python3
"""
Generation Command Handlers

Handles AI-powered content generation commands (caption, subtitle, FAQ).
"""


def handle_caption_generation(material_name: str, skip_integrity_check: bool = False):
    """Generate AI-powered caption for a material and save to Materials.yaml"""
    print("="*80)
    print(f"📝 CAPTION GENERATION: {material_name}")
    print("="*80)
    print()
    
    # Run pre-generation integrity check
    from shared.commands.integrity_helper import run_pre_generation_check
    if not run_pre_generation_check(skip_check=skip_integrity_check, quick=True):
        return False
    
    try:
        # Import required modules
        from materials.unified_generator import UnifiedMaterialsGenerator
        from data.materials.materials import load_materials, get_material_by_name
        
        # Initialize Grok API client for captions
        from shared.api.client_factory import create_api_client
        print("🔧 Initializing Grok API client...")
        api_client = create_api_client('grok')
        print("✅ Grok client ready")
        print()
        
        # Initialize unified generator
        print("🔧 Initializing UnifiedMaterialsGenerator...")
        generator = UnifiedMaterialsGenerator(api_client)
        print("✅ Generator ready")
        print()
        
        # Generate caption (no voice - that's done by post-processor)
        print("🤖 Generating AI-powered caption...")
        print("   before: Contaminated surface analysis")
        print("   after: Cleaned surface analysis")
        print("   Target: Technical, factual content")
        print("   Note: Voice enhancement happens in post-processing")
        print()
        
        caption_data = generator.generate(material_name, 'caption')
        
        print("✅ Caption generated and saved to Materials.yaml")
        print()
        
        # Show statistics
        before_text = caption_data.get('content', {}).get('before', '')
        after_text = caption_data.get('content', {}).get('after', '')
        
        print("📊 Statistics:")
        if before_text:
            print(f"   before: {len(before_text)} characters, {len(before_text.split())} words")
        if after_text:
            print(f"   after: {len(after_text)} characters, {len(after_text.split())} words")
        print()
        print("📝 Preview:")
        if before_text:
            print(f"   Before: {before_text}")
        if after_text:
            print(f"   After: {after_text}")
        print()
        
        print("💾 Saved to: materials/data/Materials.yaml → caption")
        print()
        
        # Run subjective evaluation
        from shared.commands.subjective_evaluation_helper import SubjectiveEvaluationHelper
        print("🔍 Running subjective evaluation...")
        helper = SubjectiveEvaluationHelper(
            api_client=api_client,
            verbose=True
        )
        
        # Combine before and after for evaluation
        full_content = f"BEFORE:\n{before_text}\n\nAFTER:\n{after_text}"
        eval_result = helper.evaluate_generation(
            content=full_content,
            topic=material_name,
            component_type='caption',
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
        
        print("✨ Caption generation complete!")
        print()
        
        # Run post-generation validation
        from shared.commands.integrity_helper import run_post_generation_validation
        run_post_generation_validation(material_name, 'caption', quick=True)
        
        # Check if we should update sweet spot recommendations (generic learning)
        from processing.detection.winston_feedback_db import WinstonFeedbackDatabase
        from processing.config.config_loader import get_config
        
        config = get_config()
        db_path = config.config.get('winston_feedback_db_path')
        feedback_db = WinstonFeedbackDatabase(db_path) if db_path else None
        
        if feedback_db and feedback_db.should_update_sweet_spot('*', '*', min_samples=5):
            print("📊 Updating generic sweet spot recommendations...")
            try:
                from processing.learning.sweet_spot_analyzer import SweetSpotAnalyzer
                analyzer = SweetSpotAnalyzer(db_path, min_samples=5, success_threshold=80.0)
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
        
        # Run post-generation integrity check
        print("🔍 Running post-generation integrity check...")
        from processing.integrity import IntegrityChecker
        checker = IntegrityChecker()
        post_results = checker.run_post_generation_checks(
            material=material_name,
            component_type='caption'
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
        
        return True
        
    except Exception as e:
        print(f"❌ Error during caption generation: {e}")
        import traceback
        traceback.print_exc()
        return False


def handle_subtitle_generation(material_name: str, skip_integrity_check: bool = False):
    """Generate AI-powered subtitle for a material using processing pipeline"""
    print("="*80)
    print(f"📝 SUBTITLE GENERATION: {material_name}")
    print("="*80)
    print()
    
    # Run pre-generation integrity check
    from shared.commands.integrity_helper import run_pre_generation_check
    if not run_pre_generation_check(skip_check=skip_integrity_check, quick=True):
        return False
    
    try:
        # Initialize API client
        from shared.api.client_factory import create_api_client
        print("🔧 Initializing Grok API client...")
        api_client = create_api_client('grok')
        print("✅ Grok client ready")
        print()
        
        # Initialize processing orchestrator
        from processing.orchestrator import Orchestrator
        from processing.config.dynamic_config import DynamicConfig
        
        print("🔧 Initializing processing pipeline...")
        config = DynamicConfig()
        orchestrator = Orchestrator(api_client, config)
        print("✅ Pipeline ready")
        print()
        
        # Generate subtitle through processing pipeline (includes AI detection)
        print("🤖 Generating AI-powered subtitle with quality validation...")
        print("   • Target: Professional technical subtitle")
        print("   • Pipeline: Enrichment → Generation → AI Detection → Validation")
        print()
        
        result = orchestrator.generate(
            topic=material_name,
            component_type='subtitle',
            author_id=1,  # Will be randomly selected by orchestrator
            domain='materials'
        )
        
        if not result.get('success'):
            print(f"❌ Generation failed: {result.get('reason', 'Unknown error')}")
            if 'last_ai_score' in result:
                print(f"   Last AI score: {result['last_ai_score']:.3f}")
            return False
        
        subtitle = result['text']  # Orchestrator returns 'text' not 'content'
        ai_score = result.get('ai_score', 0)
        attempts = result.get('attempts', 1)
        
        # Save to Materials.yaml
        import yaml
        from pathlib import Path
        materials_path = Path('data/materials/Materials.yaml')
        with open(materials_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Materials are under 'materials' key
        if 'materials' not in data or material_name not in data['materials']:
            print(f"❌ Material '{material_name}' not found in Materials.yaml")
            return False
        
        data['materials'][material_name]['subtitle'] = subtitle
        
        with open(materials_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print("✅ Subtitle generated and validated successfully!")
        print()
        
        # Show statistics
        print("📊 Statistics:")
        print(f"   • Length: {len(subtitle)} characters")
        print(f"   • Word count: {len(subtitle.split())} words")
        print(f"   • AI Score: {ai_score:.3f} (threshold: {orchestrator.ai_threshold:.3f})")
        print(f"   • Attempts: {attempts}")
        print()
        print("📝 FULL GENERATED TEXT:")
        print("─" * 80)
        print(subtitle)
        print("─" * 80)
        print()
        
        print("💾 Saved to: data/materials/Materials.yaml → subtitle")
        print()
        
        # Run subjective evaluation
        from shared.commands.subjective_evaluation_helper import SubjectiveEvaluationHelper
        print("🔍 Running subjective evaluation...")
        helper = SubjectiveEvaluationHelper(
            api_client=api_client,
            verbose=True
        )
        
        eval_result = helper.evaluate_generation(
            content=subtitle,
            topic=material_name,
            component_type='subtitle',
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
        
        print("✨ Subtitle generation complete!")
        print()
        
        # Run post-generation integrity check
        print("🔍 Running post-generation integrity check...")
        from processing.integrity import IntegrityChecker
        checker = IntegrityChecker()
        post_results = checker.run_post_generation_checks(
            material=material_name,
            component_type='subtitle'
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
        
        return True
        
    except Exception as e:
        print(f"❌ Error during subtitle generation: {e}")
        import traceback
        traceback.print_exc()
        return False


def handle_faq_generation(material_name: str, skip_integrity_check: bool = False):
    """Generate AI-powered FAQ for a material and save to Materials.yaml"""
    print("="*80)
    print(f"❓ FAQ GENERATION: {material_name}")
    print("="*80)
    print()
    
    # Run pre-generation integrity check
    from shared.commands.integrity_helper import run_pre_generation_check
    if not run_pre_generation_check(skip_check=skip_integrity_check, quick=True):
        return False
    
    try:
        # Import required modules
        from materials.unified_generator import UnifiedMaterialsGenerator
        
        # Initialize Grok API client for FAQ
        from shared.api.client_factory import create_api_client
        print("🔧 Initializing Grok API client...")
        api_client = create_api_client('grok')
        print("✅ Grok client ready")
        print()
        
        # Initialize unified generator
        print("🔧 Initializing UnifiedMaterialsGenerator...")
        generator = UnifiedMaterialsGenerator(api_client)
        print("✅ Generator ready")
        print()
        
        # Generate FAQ (no voice - that's done by post-processor)
        print("🤖 Generating AI-powered FAQ...")
        print("   • Questions: Random 2-8 material-specific Q&As")
        print("   • Categories: Based on researched material characteristics")
        print("   • Answers: 10-50 words each with HIGH variability (mixed short/medium/long)")
        print("   • Note: Voice enhancement happens in post-processing")
        print()
        
        faq_list = generator.generate(material_name, 'faq')  # Random count between 2-8
        
        print("✅ FAQ generated and saved successfully!")
        print()
        
        # Show statistics
        total_words = sum(len(qa['answer'].split()) for qa in faq_list)
        
        print("📊 Statistics:")
        print(f"   • Questions: {len(faq_list)}")
        print(f"   • Total words: {total_words}")
        print(f"   • Avg words/answer: {total_words / len(faq_list):.1f}")
        print()
        print("📝 Questions & Answers:")
        for i, qa in enumerate(faq_list, 1):
            print(f"   {i}. {qa['question']}")
            print(f"      {qa['answer']}")
            print()
        
        print("💾 Saved to: materials/data/Materials.yaml → faq")
        print()
        
        # Run subjective evaluation on all Q&A pairs
        from shared.commands.subjective_evaluation_helper import SubjectiveEvaluationHelper
        print("🔍 Running subjective evaluation...")
        helper = SubjectiveEvaluationHelper(
            api_client=api_client,
            verbose=True
        )
        
        # Combine all Q&As for evaluation
        all_content = []
        for qa in faq_list:
            all_content.append(f"Q: {qa['question']}\nA: {qa['answer']}")
        full_content = "\n\n".join(all_content)
        
        eval_result = helper.evaluate_generation(
            content=full_content,
            topic=material_name,
            component_type='faq',
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
        
        print("✨ FAQ generation complete!")
        print()
        
        # Run post-generation integrity check
        print("🔍 Running post-generation integrity check...")
        from processing.integrity import IntegrityChecker
        checker = IntegrityChecker()
        post_results = checker.run_post_generation_checks(
            material=material_name,
            component_type='faq'
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
        
        return True
        
    except Exception as e:
        print(f"❌ Error during FAQ generation: {e}")
        import traceback
        traceback.print_exc()
        return False


# =================================================================================
# MATERIAL AUDITING SYSTEM
# =================================================================================

