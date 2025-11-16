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
        
        # Initialize DeepSeek API client for captions
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
        print("   • before: Contaminated surface analysis")
        print("   • after: Cleaned surface analysis")
        print("   • Target: Technical, factual content")
        print("   • Note: Voice enhancement happens in post-processing")
        print()
        
        caption_data = generator.generate(material_name, 'caption')
        
        print("✅ Caption generated and saved to Materials.yaml")
        print()
        
        # Show statistics
        before_text = caption_data.get('before', '')
        after_text = caption_data.get('after', '')
        
        print("📊 Statistics:")
        if before_text:
            print(f"   • before: {len(before_text)} characters, {len(before_text.split())} words")
        if after_text:
            print(f"   • after: {len(after_text)} characters, {len(after_text.split())} words")
        print()
        print("📝 Preview:")
        if before_text:
            print(f"   • Before: {before_text}")
        if after_text:
            print(f"   • After: {after_text}")
        print()
        
        print("💾 Saved to: materials/data/Materials.yaml → caption")
        print()
        
        # Run Subjective evaluation as final quality check
        print("🤖 Running subjective content evaluation...")
        from shared.commands.subjective_evaluation_helper import evaluate_after_generation
        from processing.detection.winston_feedback_db import WinstonFeedbackDatabase
        from processing.config.config_loader import get_config
        
        try:
            # Initialize feedback database if configured
            config = get_config()
            db_path = config.config.get('winston_feedback_db_path')
            feedback_db = None
            if db_path:
                feedback_db = WinstonFeedbackDatabase(db_path)
            
            # Evaluate both before and after captions
            print()
            if before_text:
                print("   Evaluating 'before' caption...")
                before_eval = evaluate_after_generation(
                    content=before_text,
                    topic=material_name,
                    component_type='caption_before',
                    domain='materials',
                    feedback_db=feedback_db,
                    verbose=False
                )
                if before_eval:
                    print(f"   ✅ Before: {before_eval.overall_score:.1f}/10 - {'PASS' if before_eval.passes_quality_gate else 'FAIL'}")
            
            if after_text:
                print("   Evaluating 'after' caption...")
                after_eval = evaluate_after_generation(
                    content=after_text,
                    topic=material_name,
                    component_type='caption_after',
                    domain='materials',
                    feedback_db=feedback_db,
                    verbose=False
                )
                if after_eval:
                    print(f"   ✅ After: {after_eval.overall_score:.1f}/10 - {'PASS' if after_eval.passes_quality_gate else 'FAIL'}")
                    
                    # Show dimension breakdown for 'after' caption
                    print()
                    print("   📊 Quality Dimensions (After):")
                    for score in after_eval.dimension_scores:
                        status = "✅" if score.score >= 7.0 else "⚠️"
                        print(f"      {status} {score.dimension.value.replace('_', ' ').title()}: {score.score:.1f}/10")
            
            print()
        except Exception as e:
            print(f"   ⚠️  Subjective evaluation unavailable: {e}")
            print()
        
        print("✨ Caption generation complete!")
        
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
        
        # Run Subjective evaluation as final quality check
        print("🤖 Running subjective content evaluation...")
        from shared.commands.subjective_evaluation_helper import evaluate_after_generation
        
        try:
            # Use existing feedback_db from orchestrator if available
            feedback_db = orchestrator.feedback_db if hasattr(orchestrator, 'feedback_db') else None
            
            evaluation = evaluate_after_generation(
                content=subtitle,
                topic=material_name,
                component_type='subtitle',
                domain='materials',
                feedback_db=feedback_db,
                verbose=False
            )
            
            if evaluation:
                print(f"   Overall Quality Score: {evaluation.overall_score:.1f}/10")
                print(f"   Quality Gate: {'✅ PASS' if evaluation.passes_quality_gate else '❌ FAIL'}")
                print()
                print("   📊 Quality Dimensions:")
                for score in evaluation.dimension_scores:
                    status = "✅" if score.score >= 7.0 else "⚠️"
                    print(f"      {status} {score.dimension.value.replace('_', ' ').title()}: {score.score:.1f}/10")
                print()
                
                # Show top strength and weakness
                if evaluation.strengths:
                    print(f"   💪 Top Strength: {evaluation.strengths[0]}")
                if evaluation.weaknesses:
                    print(f"   ⚠️  Area for Improvement: {evaluation.weaknesses[0]}")
                print()
        except Exception as e:
            print(f"   ⚠️  Subjective evaluation unavailable: {e}")
            print()
        
        print("✨ Subtitle generation complete!")
        
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
        
        # Initialize DeepSeek API client for FAQ
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
        
        # Run Subjective evaluation as final quality check
        print("🤖 Running subjective content evaluation...")
        from shared.commands.subjective_evaluation_helper import SubjectiveEvaluationHelper
        from processing.detection.winston_feedback_db import WinstonFeedbackDatabase
        from processing.config.config_loader import get_config
        
        try:
            # Initialize feedback database if configured
            config = get_config()
            db_path = config.config.get('winston_feedback_db_path')
            feedback_db = None
            if db_path:
                feedback_db = WinstonFeedbackDatabase(db_path)
            
            helper = SubjectiveEvaluationHelper(
                feedback_db=feedback_db,
                verbose=False
            )
            
            # Evaluate each FAQ entry
            print()
            total_score = 0
            pass_count = 0
            
            for i, qa in enumerate(faq_list, 1):
                # Combine question and answer for evaluation
                faq_content = f"Q: {qa['question']}\nA: {qa['answer']}"
                
                evaluation = helper.evaluate_generation(
                    content=faq_content,
                    topic=material_name,
                    component_type='faq',
                    domain='materials'
                )
                
                if evaluation:
                    total_score += evaluation.overall_score
                    if evaluation.passes_quality_gate:
                        pass_count += 1
                    
                    status = "✅" if evaluation.passes_quality_gate else "⚠️"
                    print(f"   {status} Q{i}: {evaluation.overall_score:.1f}/10")
            
            # Show summary
            if len(faq_list) > 0:
                avg_score = total_score / len(faq_list)
                pass_rate = (pass_count / len(faq_list)) * 100
                
                print()
                print("   📊 FAQ Quality Summary:")
                print(f"      Average Score: {avg_score:.1f}/10")
                print(f"      Quality Gate Pass Rate: {pass_rate:.0f}% ({pass_count}/{len(faq_list)})")
                print()
        except Exception as e:
            print(f"   ⚠️  Subjective evaluation unavailable: {e}")
            print()
        
        print("✨ FAQ generation complete!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during FAQ generation: {e}")
        import traceback
        traceback.print_exc()
        return False


# =================================================================================
# MATERIAL AUDITING SYSTEM
# =================================================================================

