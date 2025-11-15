#!/usr/bin/env python3
"""
Generation Command Handlers

Handles AI-powered content generation commands (caption, subtitle, FAQ).
"""


def handle_caption_generation(material_name: str):
    """Generate AI-powered caption for a material and save to Materials.yaml"""
    print("="*80)
    print(f"📝 CAPTION GENERATION: {material_name}")
    print("="*80)
    print()
    
    try:
        # Import required modules
        from materials.unified_generator import UnifiedMaterialsGenerator
        from data.materials.materials import load_materials, get_material_by_name
        
        # Initialize Grok API client for captions
        from shared.api.client_factory import create_api_client
        print("🔧 Initializing Grok API client...")
        grok_client = create_api_client('grok')
        print("✅ Grok client ready")
        print()
        
        # Initialize unified generator
        print("🔧 Initializing UnifiedMaterialsGenerator...")
        generator = UnifiedMaterialsGenerator(grok_client)
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
            print(f"   • Before: {before_text[:100]}...")
        if after_text:
            print(f"   • After: {after_text[:100]}...")
        print()
        
        print("💾 Saved to: materials/data/Materials.yaml → caption")
        print("✨ Caption generation complete!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during caption generation: {e}")
        import traceback
        traceback.print_exc()
        return False


def handle_subtitle_generation(material_name: str):
    """Generate AI-powered subtitle for a material and save to Materials.yaml"""
    print("="*80)
    print(f"📝 SUBTITLE GENERATION: {material_name}")
    print("="*80)
    print()
    
    try:
        # Import required modules
        from materials.unified_generator import UnifiedMaterialsGenerator
        
        # Initialize Grok API client for subtitles
        from shared.api.client_factory import create_api_client
        print("🔧 Initializing Grok API client...")
        grok_client = create_api_client('grok')
        print("✅ Grok client ready")
        print()
        
        # Initialize unified generator
        print("🔧 Initializing UnifiedMaterialsGenerator...")
        generator = UnifiedMaterialsGenerator(grok_client)
        print("✅ Generator ready")
        print()
        
        # Generate subtitle (no voice - that's done by post-processor)
        print("🤖 Generating AI-powered subtitle...")
        print("   • Target: 8-15 word professional tagline")
        print("   • Style: Technical, clear, professional")
        print("   • Audience: Technical professionals and decision-makers")
        print("   • Note: Voice enhancement happens in post-processing")
        print()
        
        subtitle = generator.generate(material_name, 'subtitle')
        
        print("✅ Subtitle generated and saved successfully!")
        print()
        
        # Show statistics
        print("📊 Statistics:")
        print(f"   • Length: {len(subtitle)} characters")
        print(f"   • Word count: {len(subtitle.split())} words")
        print()
        print("📝 FULL GENERATED TEXT:")
        print("─" * 80)
        print(subtitle)
        print("─" * 80)
        print()
        
        print("💾 Saved to: materials/data/Materials.yaml → subtitle")
        print("✨ Subtitle generation complete!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during subtitle generation: {e}")
        import traceback
        traceback.print_exc()
        return False


def handle_faq_generation(material_name: str):
    """Generate AI-powered FAQ for a material and save to Materials.yaml"""
    print("="*80)
    print(f"❓ FAQ GENERATION: {material_name}")
    print("="*80)
    print()
    
    try:
        # Import required modules
        from materials.unified_generator import UnifiedMaterialsGenerator
        
        # Initialize Grok API client for FAQ
        from shared.api.client_factory import create_api_client
        print("🔧 Initializing Grok API client...")
        grok_client = create_api_client('grok')
        print("✅ Grok client ready")
        print()
        
        # Initialize unified generator
        print("🔧 Initializing UnifiedMaterialsGenerator...")
        generator = UnifiedMaterialsGenerator(grok_client)
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
        print("📝 Preview (first 3 questions):")
        for i, qa in enumerate(faq_list[:3], 1):
            print(f"   {i}. {qa['question']}")
            print(f"      Answer: {qa['answer'][:80]}...")
            print()
        
        print("💾 Saved to: materials/data/Materials.yaml → faq")
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

