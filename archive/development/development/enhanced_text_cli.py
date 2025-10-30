#!/usr/bin/env python3
"""
Enhanced Text Generation CLI

Commands for using the enhanced text generation system with author voice,
cultural adaptation, and sophisticated prompting across all frontmatter text fields.
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from components.frontmatter.core.hybrid_generation_manager import HybridFrontmatterManager, GenerationMode
from components.frontmatter.core.universal_text_enhancer import EnhancedTextFieldManager, AuthorProfile
from data.materials import get_material_by_name_cached
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_enhanced_prompting():
    """Test the enhanced prompting system for a single material"""
    
    # Initialize the enhanced text field manager
    manager = EnhancedTextFieldManager()
    
    print("🎯 Enhanced Text Field System Test")
    print("=" * 45)
    
    # Test with Aluminum
    material_name = "Aluminum"
    material_data = get_material_by_name_cached(material_name)
    
    if not material_data:
        print(f"❌ Material '{material_name}' not found in database")
        return
    
    context_frontmatter = {
        "title": "Aluminum Laser Cleaning Parameters",
        "applications": ["aerospace", "automotive", "electronics"]
    }
    
    # Test different field types
    test_fields = [
        "subtitle",
        "description", 
        "safety_considerations",
        "technical_notes"
    ]
    
    for field_name in test_fields:
        print(f"\n📝 Testing field: {field_name}")
        print("-" * 30)
        
        # Create basic prompt
        base_prompt = f"Generate professional {field_name} for laser cleaning {material_name}"
        
        # Enhance with universal system
        try:
            enhanced_prompt = manager.enhance_field_generation(
                field_name=field_name,
                base_prompt=base_prompt,
                material_name=material_name,
                material_data=material_data,
                context_frontmatter=context_frontmatter
            )
            
            print("✅ Enhanced prompt generated successfully")
            print(f"📏 Prompt length: {len(enhanced_prompt):,} characters")
            
            # Show key enhancement indicators
            enhancements = []
            if "AUTHOR VOICE" in enhanced_prompt:
                enhancements.append("Author Voice")
            if "FIELD-SPECIFIC REQUIREMENTS" in enhanced_prompt:
                enhancements.append("Field-Specific")
            if "ANTI-AI DETECTION" in enhanced_prompt:
                enhancements.append("Anti-AI")
            if "MATERIAL CONTEXT" in enhanced_prompt:
                enhancements.append("Material Context")
            
            print(f"🎨 Enhancements: {', '.join(enhancements)}")
            
        except Exception as e:
            print(f"❌ Failed to enhance {field_name}: {e}")
            logger.exception(f"Enhancement error for {field_name}")
    
    print("\n✅ Enhanced text field system test completed")

def show_author_profiles():
    """Show available author profiles and their characteristics"""
    
    print("🎭 Available Author Profiles")
    print("=" * 35)
    
    profiles = [
        (AuthorProfile.USA, "Conversational, innovation-focused, direct communication"),
        (AuthorProfile.ITALY, "Sophisticated, elegant, rich vocabulary with flowing transitions"),
        (AuthorProfile.TAIWAN, "Formal academic, systematic, comprehensive technical coverage"),
        (AuthorProfile.INDONESIA, "Clear accessible, practical, simplified technical language")
    ]
    
    for profile, description in profiles:
        print(f"\n🌍 {profile.name} ({profile.value})")
        print(f"   {description}")
    
    print("\n💡 Profiles are automatically selected based on material author_id")
    print("   or assigned consistently using material name hash")

def generate_enhanced_text(material_name: str, api_client_type: str = "mock"):
    """Generate enhanced text for a specific material"""
    
    print(f"🚀 Generating Enhanced Text for {material_name}")
    print("=" * 50)
    
    # Mock API client for demonstration
    class MockAPIClient:
        def generate_content(self, prompt, max_tokens=200, temperature=0.3):
            # Check for enhancement indicators
            enhanced_indicators = [
                "AUTHOR VOICE - USA PROFESSIONAL",
                "AUTHOR VOICE - ITALIAN TECHNICAL EXPERT", 
                "AUTHOR VOICE - TAIWAN ACADEMIC",
                "AUTHOR VOICE - INDONESIAN TECHNICAL COMMUNICATOR",
                "FIELD-SPECIFIC REQUIREMENTS",
                "ANTI-AI DETECTION MEASURES",
            ]
            
            has_enhancement = any(indicator in prompt for indicator in enhanced_indicators)
            
            if has_enhancement:
                return f"Enhanced AI-generated content for {material_name} with sophisticated prompting and author voice"
            else:
                return f"Basic AI-generated content for {material_name}"
    
    # Initialize hybrid manager
    manager = HybridFrontmatterManager()
    api_client = MockAPIClient()
    
    try:
        # Generate enhanced frontmatter
        result = manager.generate_frontmatter(
            material_name=material_name,
            mode=GenerationMode.TEXT_ONLY,
            text_api_client=api_client,
            existing_frontmatter={
                "title": f"{material_name} Laser Cleaning Parameters"
            }
        )
        
        print("✅ Enhanced generation completed successfully")
        print("\n📋 Generated Content:")
        
        for field, value in result.items():
            if isinstance(value, str):
                enhanced = "✨" if "Enhanced" in value else "📝"
                print(f"  {enhanced} {field}: {value}")
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        logger.exception("Generation error")

def list_text_fields():
    """List all text fields that can be enhanced"""
    
    print("📝 Text Fields Enhanced by Universal System")
    print("=" * 45)
    
    field_categories = {
        "Title & Description": ["title", "subtitle", "description", "headline"],
        "Technical Fields": ["technical_notes", "methodology", "validation_method", "research_basis"],
        "Safety Fields": ["safety_considerations", "safety_notes", "warnings", "limitations"],
        "Application Fields": ["applications", "use_cases", "application_notes"],
        "Property Descriptions": ["property_description", "explanation_text"]
    }
    
    for category, fields in field_categories.items():
        print(f"\n🏷️  {category}:")
        for field in fields:
            print(f"   • {field}")
    
    print(f"\n💡 All fields receive:")
    print("   • Author nationality voice consistency")
    print("   • Field-specific prompt optimization")
    print("   • Anti-AI detection measures")
    print("   • Cultural adaptation")
    print("   • Material-specific context")

def main():
    """Main CLI interface"""
    
    parser = argparse.ArgumentParser(
        description="Enhanced Text Generation CLI for Z-Beam Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 enhanced_text_cli.py test          # Test enhanced prompting system
  python3 enhanced_text_cli.py profiles      # Show author profiles
  python3 enhanced_text_cli.py generate -m Aluminum  # Generate enhanced text
  python3 enhanced_text_cli.py fields        # List enhanceable text fields
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Test command
    subparsers.add_parser('test', help='Test the enhanced prompting system')
    
    # Profiles command
    subparsers.add_parser('profiles', help='Show available author profiles')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate enhanced text for material')
    gen_parser.add_argument('-m', '--material', required=True, help='Material name')
    gen_parser.add_argument('--api', choices=['mock', 'grok'], default='mock', 
                           help='API client type (default: mock)')
    
    # Fields command
    subparsers.add_parser('fields', help='List all enhanceable text fields')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'test':
            test_enhanced_prompting()
        elif args.command == 'profiles':
            show_author_profiles()
        elif args.command == 'generate':
            generate_enhanced_text(args.material, args.api)
        elif args.command == 'fields':
            list_text_fields()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.exception("CLI error")

if __name__ == "__main__":
    main()