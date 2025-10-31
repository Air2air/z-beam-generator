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
        from materials.caption.generators.generator import CaptionComponentGenerator
        from materials.data.materials import load_materials, get_material_by_name
        from pathlib import Path
        import yaml
        from datetime import datetime, timezone
        
        # Load materials data
        print("📂 Loading Materials.yaml...")
        materials_data = load_materials()
        material_data = get_material_by_name(material_name, materials_data)
        
        if not material_data:
            print(f"❌ Material '{material_name}' not found in Materials.yaml")
            return False
        
        print(f"✅ Found material: {material_name}")
        print()
        
        # Initialize Grok API client for captions
        from shared.api.client_factory import create_api_client
        print("🔧 Initializing Grok API client...")
        grok_client = create_api_client('grok')
        print("✅ Grok client ready")
        print()
        
        # Initialize caption generator
        print("🔧 Initializing CaptionComponentGenerator...")
        generator = CaptionComponentGenerator()
        print("✅ Generator ready")
        print()
        
        # Extract author for voice enhancement
        author = material_data.get('author')
        if author:
            print(f"👤 Author: {author.get('name', 'Unknown')} ({author.get('country', 'Unknown')})")
        
        # Generate caption
        print("🤖 Generating AI-powered caption with author voice...")
        print("   • beforeText: Contaminated surface analysis")
        print("   • afterText: Cleaned surface analysis")
        print("   • Voice: Country-specific authenticity")
        print("   • Quality: Production-grade validation")
        print()
        
        result = generator.generate(
            material_name=material_name,
            material_data=material_data,
            api_client=grok_client,
            author=author
        )
        
        if not result.success:
            print(f"❌ Caption generation failed: {result.error_message}")
            return False
        
        # Caption was already written to Materials.yaml by the generator
        # Reload to display statistics
        print("✅ Caption generated and saved successfully!")
        print()
        
        # Reload materials to show what was written
        materials_data = load_materials()
        material_data = get_material_by_name(material_name, materials_data)
        
        caption = material_data.get('caption', {})
        if 'beforeText' in caption and 'afterText' in caption:
            before_text = caption['beforeText']
            after_text = caption['afterText']
            
            print("📊 Statistics:")
            print(f"   • beforeText: {len(before_text)} characters, {len(before_text.split())} words")
            print(f"   • afterText: {len(after_text)} characters, {len(after_text.split())} words")
            print()
            print("📝 Preview:")
            print(f"   • Before: {before_text[:100]}...")
            print(f"   • After: {after_text[:100]}...")
            print()
        
        print("💾 Saved to: materials/data/materials.yaml → caption")
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
        from materials.subtitle.core.subtitle_generator import SubtitleComponentGenerator
        from materials.data.materials import load_materials, get_material_by_name
        from pathlib import Path
        import yaml
        from datetime import datetime, timezone
        
        # Load materials data
        print("📂 Loading Materials.yaml...")
        materials_data = load_materials()
        material_data = get_material_by_name(material_name, materials_data)
        
        if not material_data:
            print(f"❌ Material '{material_name}' not found in Materials.yaml")
            return False
        
        print(f"✅ Found material: {material_name}")
        print()
        
        # Initialize Grok API client for subtitles
        from shared.api.client_factory import create_api_client
        print("🔧 Initializing Grok API client...")
        grok_client = create_api_client('grok')
        print("✅ Grok client ready")
        print()
        
        # Initialize subtitle generator
        print("🔧 Initializing SubtitleComponentGenerator...")
        generator = SubtitleComponentGenerator()
        print("✅ Generator ready")
        print()
        
        # Extract author for voice enhancement
        author = material_data.get('author')
        if author:
            print(f"👤 Author: {author.get('name', 'Unknown')} ({author.get('country', 'Unknown')})")
        
        # Generate subtitle
        print("🤖 Generating AI-powered subtitle with author voice...")
        print("   • Target: 8-12 word professional tagline")
        print("   • Voice: Country-specific writing style")
        print("   • Audience: Technical professionals and decision-makers")
        print()
        
        result = generator.generate(
            material_name=material_name,
            material_data=material_data,
            api_client=grok_client,
            author=author
        )
        
        if not result.success:
            print(f"❌ Subtitle generation failed: {result.error_message}")
            return False
        
        # Subtitle was already written to Materials.yaml by the generator
        # Reload to display statistics
        print("✅ Subtitle generated and saved successfully!")
        print()
        
        # Reload materials to show what was written
        materials_data = load_materials()
        material_data = get_material_by_name(material_name, materials_data)
        
        subtitle = material_data.get('subtitle', '')
        subtitle_meta = material_data.get('subtitle_metadata', {})
        
        if subtitle:
            print("📊 Statistics:")
            print(f"   • Length: {len(subtitle)} characters")
            print(f"   • Word count: {len(subtitle.split())} words")
            if subtitle_meta.get('author'):
                print(f"   • Author: {subtitle_meta['author']}")
            print()
            print("📝 Subtitle:")
            print(f"   {subtitle}")
            print()
        
        print("💾 Saved to: materials/data/materials.yaml → subtitle")
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
        from materials.faq.generators.faq_generator import FAQComponentGenerator
        from materials.data.materials import load_materials, get_material_by_name
        from pathlib import Path
        import yaml
        from datetime import datetime, timezone
        
        # Load materials data
        print("📂 Loading Materials.yaml...")
        materials_data = load_materials()
        material_data = get_material_by_name(material_name, materials_data)
        
        if not material_data:
            print(f"❌ Material '{material_name}' not found in Materials.yaml")
            return False
        
        print(f"✅ Found material: {material_name}")
        print()
        
        # Initialize Grok API client for FAQ (voice enforcement works better with Grok)
        from shared.api.client_factory import create_api_client
        print("🔧 Initializing Grok API client...")
        grok_client = create_api_client('grok')
        print("✅ Grok client ready")
        print()
        
        # Initialize FAQ generator
        print("🔧 Initializing FAQComponentGenerator...")
        generator = FAQComponentGenerator()
        print("✅ Generator ready")
        print()
        
        # Generate FAQ
        print("🤖 Generating AI-powered FAQ with author voice...")
        print("   • Questions: 7-12 material-specific Q&As")
        print("   • Categories: Based on researched material characteristics")
        print("   • Answers: 20-60 words each with technical precision")
        print("   • Voice: Country-specific writing style and formality")
        print()
        
        result = generator.generate(
            material_name=material_name,
            material_data=material_data,
            api_client=grok_client
        )
        
        if not result.success:
            print(f"❌ FAQ generation failed: {result.error_message}")
            return False
        
        # FAQ was already written to Materials.yaml by the generator
        # Reload to display statistics
        print("✅ FAQ generated and saved successfully!")
        print()
        
        # Reload materials to show what was written
        materials_data = load_materials()
        material_data = get_material_by_name(material_name, materials_data)
        
        faq = material_data.get('faq', {})
        if 'questions' in faq:
            questions = faq['questions']
            total_words = sum(q.get('word_count', 0) for q in questions)
            
            print("📊 Statistics:")
            print(f"   • Questions: {len(questions)}")
            print(f"   • Total words: {total_words}")
            print(f"   • Avg words/answer: {total_words / len(questions):.1f}")
            if faq.get('author'):
                print(f"   • Author: {faq['author']}")
            print()
            print("📝 Preview (first 3 questions):")
            for i, qa in enumerate(questions[:3], 1):
                print(f"   {i}. {qa['question']}")
                print(f"      Answer: {qa['answer'][:80]}...")
                print()
        
        print("💾 Saved to: materials/data/materials.yaml → faq")
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

