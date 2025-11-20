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
        from domains.materials.coordinator import UnifiedMaterialsGenerator
        from data.materials.materials import load_materials, get_material_by_name
        
        # Initialize DeepSeek API client for captions (switched from Grok due to API hang issues)
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
        
        # DEBUG: Check what we received
        print(f"🔍 DEBUG: caption_data type = {type(caption_data)}")
        print(f"🔍 DEBUG: caption_data = {caption_data}")
        print()
        
        # SimpleGenerator returns content string directly (no dict wrapper)
        # For captions, content is a dict with 'before' and 'after' keys
        if isinstance(caption_data, dict):
            before_text = caption_data.get('before', '')
            after_text = caption_data.get('after', '')
        else:
            # Unexpected format
            before_text = str(caption_data)
            after_text = ''
        
        # POLICY: Always show complete generation report after each generation
        print("=" * 80)
        print("📊 GENERATION COMPLETE REPORT")
        print("=" * 80)
        print()
        print("📝 GENERATED CONTENT:")
        print("-" * 80)
        if before_text:
            print(f"BEFORE: {before_text}")
        if after_text:
            print(f"AFTER:  {after_text}")
        print("-" * 80)
        print()
        print("📈 STATISTICS:")
        if before_text:
            print(f"   • Before: {len(before_text)} chars, {len(before_text.split())} words")
        if after_text:
            print(f"   • After:  {len(after_text)} chars, {len(after_text.split())} words")
        print()
        print("💾 STORAGE:")
        print(f"   • Location: data/materials/Materials.yaml")
        print(f"   • Component: caption")
        print(f"   • Material: {material_name}")
        print()
        print("🔔 NOTE: Run --validate to check quality and improve with learning systems")
        print()
        print("=" * 80)
        print()
        
        # Run subjective evaluation using Grok API
        from shared.commands.subjective_evaluation_helper import SubjectiveEvaluationHelper
        print("🔍 Running subjective evaluation (Grok API)...")
        eval_client = create_api_client('grok')
        helper = SubjectiveEvaluationHelper(
            api_client=eval_client,
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
        
        # Save report to markdown file
        from postprocessing.reports.generation_report_writer import GenerationReportWriter
        writer = GenerationReportWriter()
        evaluation_data = {
            'narrative_assessment': eval_result.narrative_assessment if eval_result else None
        }
        report_path = writer.save_individual_report(
            material_name=material_name,
            component_type='caption',
            content=full_content,
            evaluation=evaluation_data
        )
        print(f"📄 Report saved: {report_path}")
        print()
        
        # Run Winston AI detection and log to database
        print("🤖 Running Winston AI detection...")
        try:
            from postprocessing.detection.winston_integration import WinstonIntegration
            from postprocessing.detection.winston_feedback_db import WinstonFeedbackDatabase
            from generation.config.config_loader import get_config
            from generation.config.dynamic_config import DynamicConfig
            
            config = get_config()
            db_path = config.config.get('winston_feedback_db_path')
            feedback_db = WinstonFeedbackDatabase(db_path) if db_path else None
            
            # Initialize Winston integration
            winston = WinstonIntegration(
                winston_client=api_client,  # Use same API client
                feedback_db=feedback_db,
                config=config.config
            )
            
            # Get dynamic threshold
            dynamic_config = DynamicConfig()
            ai_threshold = dynamic_config.calculate_winston_threshold()
            
            # Detect and log
            winston_result = winston.detect_and_log(
                text=full_content,
                material=material_name,
                component_type='caption',
                temperature=0.7,  # Default for captions
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
        
        print("✨ Caption generation complete!")
        print()
        
        # Run post-generation validation
        from shared.commands.integrity_helper import run_post_generation_validation
        run_post_generation_validation(material_name, 'caption', quick=True)
        
        # Check if we should update sweet spot recommendations (generic learning)
        if feedback_db and feedback_db.should_update_sweet_spot('*', '*', min_samples=3):
            print("📊 Updating generic sweet spot recommendations...")
            try:
                from learning.sweet_spot_analyzer import SweetSpotAnalyzer
                # Threshold as 0-1.0 scale (database stores normalized scores)
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
        
        # Run post-generation integrity check
        print("🔍 Running post-generation integrity check...")
        from generation.integrity import IntegrityChecker
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
        print("🔧 Initializing DeepSeek API client...")
        api_client = create_api_client('deepseek')
        print("✅ DeepSeek client ready")
        print()
        
        # Initialize unified generator
        from domains.materials.coordinator import UnifiedMaterialsGenerator
        
        print("🔧 Initializing UnifiedMaterialsGenerator...")
        generator = UnifiedMaterialsGenerator(api_client)
        print("✅ Generator ready")
        print()
        
        # Generate subtitle
        print("🤖 Generating AI-powered subtitle...")
        print("   Target: Professional technical subtitle")
        print("   Note: Voice enhancement happens in post-processing")
        print()
        
        subtitle_data = generator.generate(material_name, 'subtitle')
        
        print("✅ Subtitle generated and saved to Materials.yaml")
        print()
        
        # DEBUG: Check what we received
        print(f"🔍 DEBUG: subtitle_data type = {type(subtitle_data)}")
        print(f"🔍 DEBUG: subtitle_data = {subtitle_data}")
        print()
        
        # SimpleGenerator returns content string directly
        subtitle = str(subtitle_data)
        
        # POLICY: Always show complete generation report after each generation
        print("=" * 80)
        print("📊 GENERATION COMPLETE REPORT")
        print("=" * 80)
        print()
        print("📝 GENERATED CONTENT:")
        print("-" * 80)
        print(subtitle)
        print("-" * 80)
        print()
        print("📏 STATISTICS:")
        print(f"   • Length: {len(subtitle)} characters")
        print(f"   • Word count: {len(subtitle.split())} words")
        print()
        print("💾 STORAGE:")
        print("   • Location: data/materials/Materials.yaml")
        print("   • Component: subtitle")
        print(f"   • Material: {material_name}")
        print()
        print("🔔 NOTE: Run --validate to check quality and improve with learning systems")
        print()
        print("=" * 80)
        print()
        
        # Run subjective evaluation using Grok API
        from shared.commands.subjective_evaluation_helper import SubjectiveEvaluationHelper
        print("🔍 Running subjective evaluation (Grok API)...")
        eval_client = create_api_client('grok')
        helper = SubjectiveEvaluationHelper(
            api_client=eval_client,
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
        
        # Save report to markdown file
        from postprocessing.reports.generation_report_writer import GenerationReportWriter
        writer = GenerationReportWriter()
        evaluation_data = {
            'narrative_assessment': eval_result.narrative_assessment if eval_result else None
        }
        report_path = writer.save_individual_report(
            material_name=material_name,
            component_type='subtitle',
            content=subtitle,
            evaluation=evaluation_data
        )
        print(f"📄 Report saved: {report_path}")
        print()
        
        print("✨ Subtitle generation complete!")
        print()
        
        # Run post-generation integrity check
        print("🔍 Running post-generation integrity check...")
        from generation.integrity import IntegrityChecker
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
        from domains.materials.coordinator import UnifiedMaterialsGenerator
        
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
        
        # SimpleGenerator returns list of FAQ dicts directly
        faq_data = faq_list
        
        # Validate extraction succeeded
        if not faq_data or not isinstance(faq_data, list):
            print("⚠️  Warning: FAQ extraction returned unexpected format")
            print(f"   Result type: {type(faq_data)}")
            print(f"   Result: {faq_data}")
            return False
        
        # Show statistics
        total_words = sum(len(qa.get('answer', '').split()) for qa in faq_data if isinstance(qa, dict))
        
        # POLICY: Always show complete generation report after each generation
        print("=" * 80)
        print("📊 GENERATION COMPLETE REPORT")
        print("=" * 80)
        print()
        print("📝 GENERATED CONTENT:")
        print("-" * 80)
        for i, qa in enumerate(faq_data, 1):
            print(f"Q{i}: {qa['question']}")
            print(f"A{i}: {qa['answer']}")
            if i < len(faq_data):
                print()
        print("-" * 80)
        print()
        print("📏 STATISTICS:")
        print(f"   • Total Questions: {len(faq_data)}")
        print(f"   • Total Words: {total_words}")
        if len(faq_data) > 0:
            print(f"   • Avg Words/Answer: {total_words / len(faq_data):.1f}")
            answer_lengths = [len(qa.get('answer', '').split()) for qa in faq_data if isinstance(qa, dict)]
            if answer_lengths:
                print(f"   • Min Answer Length: {min(answer_lengths)} words")
                print(f"   • Max Answer Length: {max(answer_lengths)} words")
        print()
        print("💾 STORAGE:")
        print("   • Location: data/materials/Materials.yaml")
        print("   • Component: faq")
        print(f"   • Material: {material_name}")
        print()
        print("🔔 NOTE: Run --validate to check quality and improve with learning systems")
        print()
        print("=" * 80)
        print()
        
        # Run subjective evaluation on all Q&A pairs using Grok API
        from shared.commands.subjective_evaluation_helper import SubjectiveEvaluationHelper
        print("🔍 Running subjective evaluation (Grok API)...")
        eval_client = create_api_client('grok')
        helper = SubjectiveEvaluationHelper(
            api_client=eval_client,
            verbose=True
        )
        
        # Combine all Q&As for evaluation
        all_content = []
        for qa in faq_data:
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
        
        # Save report to markdown file
        from postprocessing.reports.generation_report_writer import GenerationReportWriter
        writer = GenerationReportWriter()
        evaluation_data = {
            'narrative_assessment': eval_result.narrative_assessment if eval_result else None
        }
        report_path = writer.save_individual_report(
            material_name=material_name,
            component_type='faq',
            content=full_content,
            evaluation=evaluation_data
        )
        print(f"📄 Report saved: {report_path}")
        print()
        
        print("✨ FAQ generation complete!")
        print()
        
        # Run post-generation integrity check
        print("🔍 Running post-generation integrity check...")
        from generation.integrity import IntegrityChecker
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

