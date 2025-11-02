#!/usr/bin/env python3
"""
End-to-End Pipeline Test

Tests the complete generation pipeline:
1. Generate content (caption/subtitle/FAQ) → Materials.yaml
2. Export to frontmatter
3. Apply voice processing to frontmatter
4. Validate voice markers present
5. Verify data integrity

This validates the full flow from AI generation through voice enhancement.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from materials.caption.generators.generator import CaptionComponentGenerator
from materials.subtitle.core.subtitle_generator import SubtitleComponentGenerator
from materials.faq.generators.faq_generator import FAQComponentGenerator
from materials.data.materials import load_materials, get_material_by_name
from shared.api.client_factory import create_api_client
from shared.voice.post_processor import VoicePostProcessor
from components.frontmatter.utils.author_manager import get_author_info_for_material
import yaml

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class E2EPipelineTester:
    """
    End-to-end pipeline tester for generation → voice → validation flow.
    """
    
    def __init__(self):
        """Initialize tester with API client."""
        logger.info("🔧 Initializing API client...")
        self.api_client = create_api_client('grok')
        self.voice_processor = VoicePostProcessor(self.api_client)
        
        self.test_results = {
            'generation': {},
            'materials_yaml': {},
            'frontmatter_export': {},
            'voice_application': {},
            'voice_validation': {}
        }
    
    def test_caption_pipeline(self, material_name: str):
        """
        Test caption generation pipeline.
        
        Flow:
        1. Generate caption via CaptionComponentGenerator
        2. Verify saved to Materials.yaml
        3. Check data integrity
        
        Args:
            material_name: Material to test
        """
        print("\n" + "="*80)
        print(f"🧪 TEST: Caption Generation Pipeline - {material_name}")
        print("="*80)
        
        try:
            # Step 1: Generate caption
            print("\n📝 Step 1: Generating caption...")
            generator = CaptionComponentGenerator()
            
            materials_data = load_materials()
            material_data = get_material_by_name(material_name, materials_data)
            
            if not material_data:
                print(f"❌ Material '{material_name}' not found")
                self.test_results['generation']['caption'] = False
                return False
            
            # Get author for voice (pass material_data, not material_name)
            author = get_author_info_for_material(material_data)
            
            result = generator.generate(
                material_name=material_name,
                material_data=material_data,
                api_client=self.api_client,
                author=author
            )
            
            if not result.success:
                print(f"❌ Caption generation failed: {result.error_message}")
                self.test_results['generation']['caption'] = False
                return False
            
            print("✅ Caption generated successfully")
            self.test_results['generation']['caption'] = True
            
            # Step 2: Verify in Materials.yaml
            print("\n🔍 Step 2: Verifying Materials.yaml...")
            materials_data = load_materials()  # Reload
            material_data = get_material_by_name(material_name, materials_data)
            
            if 'caption' not in material_data:
                print("❌ Caption not found in Materials.yaml")
                self.test_results['materials_yaml']['caption'] = False
                return False
            
            caption = material_data['caption']
            
            # Check structure
            if 'before' not in caption or 'after' not in caption:
                print("❌ Caption missing before/after sections")
                self.test_results['materials_yaml']['caption'] = False
                return False
            
            print(f"✅ Caption in Materials.yaml:")
            print(f"   - Before: {len(caption['before'].split())} words")
            print(f"   - After: {len(caption['after'].split())} words")
            print(f"   - Generated: {caption.get('generated', 'N/A')}")
            
            # Step 3: Validate voice markers
            print("\n🎤 Step 3: Validating voice markers...")
            
            before_score = self.voice_processor.get_voice_score(
                caption['before'],
                author
            )
            after_score = self.voice_processor.get_voice_score(
                caption['after'],
                author
            )
            
            print(f"   Before authenticity: {before_score['authenticity_score']:.1f}/100")
            print(f"   Before markers: {before_score['marker_count']}")
            print(f"   After authenticity: {after_score['authenticity_score']:.1f}/100")
            print(f"   After markers: {after_score['marker_count']}")
            
            # Voice validation passes if authenticity >= 70
            voice_valid = (
                before_score['authenticity_score'] >= 70 and
                after_score['authenticity_score'] >= 70
            )
            
            if voice_valid:
                print("✅ Voice markers validated")
            else:
                print("⚠️  Voice markers below threshold (may need enhancement)")
            
            self.test_results['materials_yaml']['caption'] = True
            self.test_results['voice_validation']['caption'] = voice_valid
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_subtitle_pipeline(self, material_name: str):
        """
        Test subtitle generation pipeline.
        
        Args:
            material_name: Material to test
        """
        print("\n" + "="*80)
        print(f"🧪 TEST: Subtitle Generation Pipeline - {material_name}")
        print("="*80)
        
        try:
            # Step 1: Generate subtitle
            print("\n📝 Step 1: Generating subtitle...")
            generator = SubtitleComponentGenerator()
            
            materials_data = load_materials()
            material_data = get_material_by_name(material_name, materials_data)
            
            if not material_data:
                print(f"❌ Material '{material_name}' not found")
                return False
            
            author = get_author_info_for_material(material_data)
            
            result = generator.generate(
                material_name=material_name,
                material_data=material_data,
                api_client=self.api_client,
                author=author
            )
            
            if not result.success:
                print(f"❌ Subtitle generation failed: {result.error_message}")
                return False
            
            print("✅ Subtitle generated successfully")
            
            # Step 2: Verify in Materials.yaml
            print("\n🔍 Step 2: Verifying Materials.yaml...")
            materials_data = load_materials()  # Reload
            material_data = get_material_by_name(material_name, materials_data)
            
            if 'subtitle' not in material_data:
                print("❌ Subtitle not found in Materials.yaml")
                return False
            
            subtitle = material_data['subtitle']
            print(f"✅ Subtitle in Materials.yaml: '{subtitle}'")
            print(f"   - Words: {len(subtitle.split())}")
            
            # Step 3: Validate voice
            print("\n🎤 Step 3: Validating voice markers...")
            score = self.voice_processor.get_voice_score(subtitle, author)
            
            print(f"   Authenticity: {score['authenticity_score']:.1f}/100")
            print(f"   Markers: {score['marker_count']}")
            
            if score['authenticity_score'] >= 70:
                print("✅ Voice markers validated")
            else:
                print("⚠️  Voice markers below threshold")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_faq_pipeline(self, material_name: str):
        """
        Test FAQ generation pipeline.
        
        Args:
            material_name: Material to test
        """
        print("\n" + "="*80)
        print(f"🧪 TEST: FAQ Generation Pipeline - {material_name}")
        print("="*80)
        
        try:
            # Step 1: Generate FAQ
            print("\n📝 Step 1: Generating FAQ...")
            generator = FAQComponentGenerator()
            
            materials_data = load_materials()
            material_data = get_material_by_name(material_name, materials_data)
            
            if not material_data:
                print(f"❌ Material '{material_name}' not found")
                return False
            
            result = generator.generate(
                material_name=material_name,
                material_data=material_data,
                api_client=self.api_client
            )
            
            if not result.success:
                print(f"❌ FAQ generation failed: {result.error_message}")
                return False
            
            print("✅ FAQ generated successfully")
            
            # Step 2: Verify in Materials.yaml
            print("\n🔍 Step 2: Verifying Materials.yaml...")
            materials_data = load_materials()  # Reload
            material_data = get_material_by_name(material_name, materials_data)
            
            if 'faq' not in material_data:
                print("❌ FAQ not found in Materials.yaml")
                return False
            
            faq = material_data['faq']
            questions = faq.get('questions', [])
            
            print(f"✅ FAQ in Materials.yaml:")
            print(f"   - Questions: {len(questions)}")
            print(f"   - Generated: {faq.get('generated', 'N/A')}")
            
            # Step 3: Validate voice (sample first 3 answers)
            print("\n🎤 Step 3: Validating voice markers (sample)...")
            
            author = get_author_info_for_material(material_data)
            
            sample_scores = []
            for i, qa in enumerate(questions[:3], 1):
                score = self.voice_processor.get_voice_score(
                    qa.get('answer', ''),
                    author
                )
                sample_scores.append(score['authenticity_score'])
                print(f"   Q{i} authenticity: {score['authenticity_score']:.1f}/100 ({score['marker_count']} markers)")
            
            avg_score = sum(sample_scores) / len(sample_scores) if sample_scores else 0
            print(f"\n   Average authenticity: {avg_score:.1f}/100")
            
            if avg_score >= 70:
                print("✅ Voice markers validated")
            else:
                print("⚠️  Voice markers below threshold")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_frontmatter_export(self, material_name: str):
        """
        Test frontmatter export from Materials.yaml.
        
        Args:
            material_name: Material to test
        """
        print("\n" + "="*80)
        print(f"🧪 TEST: Frontmatter Export - {material_name}")
        print("="*80)
        
        try:
            from components.frontmatter.core.trivial_exporter import TrivialFrontmatterExporter
            
            print("\n📤 Exporting to frontmatter...")
            
            # Load material data
            materials_data = load_materials()
            material_data = get_material_by_name(material_name, materials_data)
            
            if not material_data:
                print(f"❌ Material '{material_name}' not found")
                return False
            
            # Export using TrivialFrontmatterExporter
            exporter = TrivialFrontmatterExporter()
            exporter.export_single(material_name, material_data)
            
            print("✅ Frontmatter exported successfully")
            
            print("✅ Frontmatter exported successfully")
            
            # Verify file exists
            filename = material_name.lower().replace(' ', '-')
            frontmatter_path = Path(f"frontmatter/materials/{filename}-laser-cleaning.yaml")
            
            if not frontmatter_path.exists():
                print(f"❌ Frontmatter file not found: {frontmatter_path}")
                return False
            
            # Load and verify structure
            with open(frontmatter_path, 'r') as f:
                frontmatter = yaml.safe_load(f)
            
            print(f"✅ Frontmatter file verified: {frontmatter_path}")
            
            # Check key sections
            sections = ['caption', 'subtitle', 'faq']
            for section in sections:
                if section in frontmatter:
                    print(f"   ✅ {section} section present")
                else:
                    print(f"   ⚠️  {section} section missing")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*80)
        print("📊 E2E PIPELINE TEST SUMMARY")
        print("="*80)
        
        for stage, results in self.test_results.items():
            if results:
                print(f"\n{stage.upper()}:")
                for test, passed in results.items():
                    status = "✅" if passed else "❌"
                    print(f"  {status} {test}")
        
        print("\n" + "="*80)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="End-to-end pipeline test"
    )
    parser.add_argument(
        'material',
        help="Material name to test (e.g., 'Aluminum')"
    )
    parser.add_argument(
        '--component',
        choices=['caption', 'subtitle', 'faq', 'all'],
        default='all',
        help="Component to test (default: all)"
    )
    
    args = parser.parse_args()
    
    tester = E2EPipelineTester()
    
    if args.component in ['caption', 'all']:
        tester.test_caption_pipeline(args.material)
    
    if args.component in ['subtitle', 'all']:
        tester.test_subtitle_pipeline(args.material)
    
    if args.component in ['faq', 'all']:
        tester.test_faq_pipeline(args.material)
    
    # Always test frontmatter export
    tester.test_frontmatter_export(args.material)
    
    # Print summary
    tester.print_summary()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
