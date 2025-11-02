#!/usr/bin/env python3
"""
Voice Enhancement for Materials.yaml

This tool reads materials/data/materials.yaml, applies author voice to text content,
and writes the enhanced content back to materials.yaml.

Workflow:
1. Read materials.yaml
2. For each material with caption/subtitle/faq
3. Apply VoicePostProcessor to enhance text
4. Write back to materials.yaml with voice markers
5. Then frontmatter export reads the enhanced data

Usage:
    # Single material
    python3 scripts/voice/enhance_materials_voice.py --material "Steel"
    
    # All materials
    python3 scripts/voice/enhance_materials_voice.py --all
    
    # Dry run (no changes)
    python3 scripts/voice/enhance_materials_voice.py --material "Steel" --dry-run
    
    # Validate only
    python3 scripts/voice/enhance_materials_voice.py --validate-only
"""

import argparse
import logging
import sys
import tempfile
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.voice.post_processor import VoicePostProcessor
from shared.api.client_factory import create_api_client
from components.frontmatter.utils.author_manager import get_author_info_for_material
from materials.data.materials import load_materials, get_material_by_name

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


class MaterialsVoiceEnhancer:
    """
    Voice enhancement for materials.yaml.
    
    Reads materials.yaml, applies voice, writes back.
    """
    
    def __init__(self, api_client, dry_run: bool = False):
        """
        Initialize enhancer.
        
        Args:
            api_client: API client for voice enhancement
            dry_run: If True, don't save changes
        """
        self.api_client = api_client
        self.dry_run = dry_run
        self.voice_processor = VoicePostProcessor(api_client)
        
        self.stats = {
            'processed': 0,
            'enhanced': 0,
            'skipped': 0,
            'errors': 0
        }
        
        self.materials_path = Path("materials/data/materials.yaml")
    
    def enhance_material(self, material_name: str, intensity: int = 3) -> bool:
        """
        Enhance voice for a single material.
        
        Args:
            material_name: Material name
            intensity: Voice intensity (1-5)
            
        Returns:
            True if enhanced successfully
        """
        try:
            print(f"\n{'='*80}")
            print(f"🎤 VOICE ENHANCEMENT: {material_name}")
            print(f"{'='*80}\n")
            
            # Load materials.yaml
            materials_data = load_materials()
            material_data = get_material_by_name(material_name, materials_data)
            
            if not material_data:
                print(f"❌ Material '{material_name}' not found")
                self.stats['errors'] += 1
                return False
            
            # Get author info
            try:
                author_info = get_author_info_for_material(material_data)
                print(f"👤 Author: {author_info['name']} ({author_info['country']})")
            except Exception as e:
                print(f"❌ Failed to get author info: {e}")
                self.stats['errors'] += 1
                return False
            
            modified = False
            
            # Enhance caption
            if 'caption' in material_data:
                print("\n📸 Processing caption...")
                caption_modified = self._enhance_caption(
                    material_data['caption'],
                    author_info,
                    intensity
                )
                modified = modified or caption_modified
            
            # Enhance subtitle
            if 'subtitle' in material_data:
                print("\n🎭 Processing subtitle...")
                subtitle_modified = self._enhance_subtitle(
                    material_data,
                    author_info,
                    intensity
                )
                modified = modified or subtitle_modified
            
            # Enhance FAQ
            if 'faq' in material_data:
                print("\n❓ Processing FAQ...")
                faq_modified = self._enhance_faq(
                    material_data['faq'],
                    author_info,
                    intensity
                )
                modified = modified or faq_modified
            
            if not modified:
                print("\n✅ No changes needed - content already has good voice markers")
                self.stats['skipped'] += 1
                return True
            
            # Write back to materials.yaml
            if not self.dry_run:
                print("\n💾 Saving to materials.yaml...")
                self._save_materials(materials_data, material_name, material_data)
                print("✅ Voice enhancement saved")
            else:
                print("\n🔍 DRY RUN - No changes saved")
            
            self.stats['processed'] += 1
            if modified:
                self.stats['enhanced'] += 1
            
            return True
            
        except Exception as e:
            print(f"❌ Error enhancing {material_name}: {e}")
            import traceback
            traceback.print_exc()
            self.stats['errors'] += 1
            return False
    
    def _enhance_caption(
        self,
        caption: Dict,
        author_info: Dict,
        intensity: int
    ) -> bool:
        """Enhance caption before/after text."""
        modified = False
        
        # Check before text
        if 'before' in caption:
            before_text = caption['before']
            score = self.voice_processor.get_voice_score(before_text, author_info)
            
            print(f"   Before: {score['authenticity_score']:.0f}/100 ({score['marker_count']} markers)")
            
            if score['authenticity_score'] < 70:
                enhanced_text = self.voice_processor.enhance(
                    text=before_text,
                    author=author_info,
                    voice_voice_intensity=intensity
                )
                caption['before'] = enhanced_text
                modified = True
                new_score = self.voice_processor.get_voice_score(
                    enhanced_text,
                    author_info
                )
                print(f"   ✅ Enhanced: {new_score['authenticity_score']:.0f}/100 ({new_score['marker_count']} markers)")
            else:
                print(f"   ✅ Already good")
        
        # Check after text
        if 'after' in caption:
            after_text = caption['after']
            score = self.voice_processor.get_voice_score(after_text, author_info)
            
            print(f"   After: {score['authenticity_score']:.0f}/100 ({score['marker_count']} markers)")
            
            if score['authenticity_score'] < 70:
                enhanced_text = self.voice_processor.enhance(
                    text=after_text,
                    author=author_info,
                    voice_intensity=intensity
                )
                caption['after'] = enhanced_text
                modified = True
                new_score = self.voice_processor.get_voice_score(
                    enhanced_text,
                    author_info
                )
                print(f"   ✅ Enhanced: {new_score['authenticity_score']:.0f}/100 ({new_score['marker_count']} markers)")
            else:
                print(f"   ✅ Already good")
        
        return modified
    
    def _enhance_subtitle(
        self,
        material_data: Dict,
        author_info: Dict,
        intensity: int
    ) -> bool:
        """Enhance subtitle text."""
        if 'subtitle' not in material_data:
            return False
        
        subtitle_text = material_data['subtitle']
        if not isinstance(subtitle_text, str):
            return False
        
        score = self.voice_processor.get_voice_score(subtitle_text, author_info)
        print(f"   Current: {score['authenticity_score']:.0f}/100 ({score['marker_count']} markers)")
        
        if score['authenticity_score'] < 70:
            enhanced_text = self.voice_processor.enhance(
                text=subtitle_text,
                author=author_info,
                voice_intensity=intensity
            )
            material_data['subtitle'] = enhanced_text
            new_score = self.voice_processor.get_voice_score(
                enhanced_text,
                author_info
            )
            print(f"   ✅ Enhanced: {new_score['authenticity_score']:.0f}/100 ({new_score['marker_count']} markers)")
            return True
        else:
            print(f"   ✅ Already good")
            return False
    
    def _enhance_faq(
        self,
        faq: Dict,
        author_info: Dict,
        intensity: int
    ) -> bool:
        """Enhance FAQ answers."""
        if not isinstance(faq, dict) or 'questions' not in faq:
            return False
        
        questions = faq['questions']
        if not isinstance(questions, list):
            return False
        
        modified = False
        enhanced_count = 0
        
        for i, qa in enumerate(questions, 1):
            if 'answer' not in qa:
                continue
            
            answer = qa['answer']
            score = self.voice_processor.get_voice_score(answer, author_info)
            
            if score['authenticity_score'] < 70:
                enhanced_text = self.voice_processor.enhance(
                    text=answer,
                    author=author_info,
                    voice_intensity=intensity
                )
                qa['answer'] = enhanced_text
                modified = True
                enhanced_count += 1
        
        if enhanced_count > 0:
            print(f"   ✅ Enhanced {enhanced_count}/{len(questions)} answers")
        else:
            print(f"   ✅ All {len(questions)} answers already good")
        
        return modified
    
    def _save_materials(
        self,
        materials_data: Dict,
        material_name: str,
        material_data: Dict
    ) -> None:
        """Save enhanced material back to materials.yaml."""
        
        # Update the material in the full data structure
        # Find the actual key (case-insensitive)
        actual_key = None
        for key in materials_data['materials'].keys():
            if key.lower().replace('_', ' ') == material_name.lower().replace('_', ' '):
                actual_key = key
                break
        
        if not actual_key:
            raise ValueError(f"Material {material_name} not found")
        
        # Update with enhanced data
        materials_data['materials'][actual_key] = material_data
        
        # Add voice enhancement timestamp
        materials_data['materials'][actual_key]['voice_enhanced'] = datetime.now(timezone.utc).isoformat()
        
        # Atomic write
        temp_fd, temp_path = tempfile.mkstemp(suffix='.yaml', dir=self.materials_path.parent)
        try:
            import os
            os.close(temp_fd)
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                yaml.dump(
                    materials_data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False
                )
            
            Path(temp_path).replace(self.materials_path)
            
        except Exception as e:
            if Path(temp_path).exists():
                Path(temp_path).unlink()
            raise e
    
    def enhance_all_materials(self, intensity: int = 3) -> bool:
        """Enhance all materials in materials.yaml."""
        print(f"\n{'='*80}")
        print("🎤 VOICE ENHANCEMENT: ALL MATERIALS")
        print(f"{'='*80}\n")
        
        materials_data = load_materials()
        materials_section = materials_data.get('materials', {})
        
        total = len(materials_section)
        print(f"Found {total} materials\n")
        
        for i, material_name in enumerate(materials_section.keys(), 1):
            print(f"\n[{i}/{total}] Processing {material_name}...")
            self.enhance_material(material_name, intensity)
        
        return True
    
    def validate_all(self) -> None:
        """Validate voice markers in all materials."""
        print(f"\n{'='*80}")
        print("🔍 VOICE VALIDATION: ALL MATERIALS")
        print(f"{'='*80}\n")
        
        materials_data = load_materials()
        materials_section = materials_data.get('materials', {})
        
        issues = []
        
        for material_name, material_data in materials_section.items():
            try:
                author_info = get_author_info_for_material(material_data)
                
                # Check caption
                if 'caption' in material_data:
                    caption = material_data['caption']
                    if 'before' in caption:
                        score = self.voice_processor.get_voice_score(
                            caption['before'],
                            author_info
                        )
                        if score['authenticity_score'] < 70:
                            issues.append(f"{material_name}: Caption before ({score['authenticity_score']:.0f}/100)")
                    
                    if 'after' in caption:
                        score = self.voice_processor.get_voice_score(
                            caption['after'],
                            author_info
                        )
                        if score['authenticity_score'] < 70:
                            issues.append(f"{material_name}: Caption after ({score['authenticity_score']:.0f}/100)")
                
                # Check subtitle
                if 'subtitle' in material_data:
                    score = self.voice_processor.get_voice_score(
                        material_data['subtitle'],
                        author_info
                    )
                    if score['authenticity_score'] < 70:
                        issues.append(f"{material_name}: Subtitle ({score['authenticity_score']:.0f}/100)")
                
                # Check FAQ
                if 'faq' in material_data:
                    faq = material_data['faq']
                    if isinstance(faq, dict) and 'questions' in faq:
                        low_scores = 0
                        for qa in faq['questions']:
                            if 'answer' in qa:
                                score = self.voice_processor.get_voice_score(
                                    qa['answer'],
                                    author_info
                                )
                                if score['authenticity_score'] < 70:
                                    low_scores += 1
                        if low_scores > 0:
                            issues.append(f"{material_name}: FAQ ({low_scores} answers < 70)")
                
            except Exception as e:
                issues.append(f"{material_name}: Error - {e}")
        
        print(f"\n{'='*80}")
        print("📊 VALIDATION RESULTS")
        print(f"{'='*80}\n")
        
        if issues:
            print(f"❌ Found {len(issues)} issues:\n")
            for issue in issues:
                print(f"   • {issue}")
        else:
            print("✅ All materials have good voice markers (≥ 70/100)")
    
    def print_stats(self):
        """Print enhancement statistics."""
        print(f"\n{'='*80}")
        print("📊 VOICE ENHANCEMENT SUMMARY")
        print(f"{'='*80}\n")
        print(f"   Processed: {self.stats['processed']}")
        print(f"   Enhanced: {self.stats['enhanced']}")
        print(f"   Skipped: {self.stats['skipped']}")
        print(f"   Errors: {self.stats['errors']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Apply voice enhancement to materials.yaml"
    )
    
    parser.add_argument(
        '--material',
        help='Material name to enhance'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Enhance all materials'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate voice markers, no changes'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without saving'
    )
    
    parser.add_argument(
        '--voice-intensity',
        type=int,
        default=3,
        choices=[1, 2, 3, 4, 5],
        help='Voice intensity (1=minimal, 5=maximum, default=3)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.material and not args.all and not args.validate_only:
        parser.error("Must specify --material, --all, or --validate-only")
    
    try:
        # Initialize API client
        print("🔧 Initializing API client...")
        api_client = create_api_client('grok')
        print("✅ API client ready\n")
        
        # Initialize enhancer
        enhancer = MaterialsVoiceEnhancer(
            api_client=api_client,
            dry_run=args.dry_run
        )
        
        # Execute command
        if args.validate_only:
            enhancer.validate_all()
        elif args.all:
            enhancer.enhance_all_materials(intensity=args.voice_intensity)
            enhancer.print_stats()
        elif args.material:
            enhancer.enhance_material(args.material, intensity=args.voice_intensity)
            enhancer.print_stats()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
