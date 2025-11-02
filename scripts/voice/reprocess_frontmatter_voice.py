#!/usr/bin/env python3
"""
Reusable Voice Post-Processor for Frontmatter

This standalone tool reads existing frontmatter files, applies author voice
to text content (caption, subtitle, FAQ), and saves back with proper voice markers.

Architecture:
- Reads from frontmatter/materials/ or frontmatter/regions/
- Applies VoicePostProcessor to text fields
- Validates voice markers were added
- Saves back atomically
- Works on individual files or batches

Usage:
    # Single file
    python3 scripts/voice/reprocess_frontmatter_voice.py --file aluminum-laser-cleaning.yaml
    
    # All materials
    python3 scripts/voice/reprocess_frontmatter_voice.py --all-materials
    
    # All regions
    python3 scripts/voice/reprocess_frontmatter_voice.py --all-regions
    
    # Specific content type
    python3 scripts/voice/reprocess_frontmatter_voice.py --content-type material --identifier Aluminum
    
    # Dry run (no changes)
    python3 scripts/voice/reprocess_frontmatter_voice.py --file aluminum-laser-cleaning.yaml --dry-run
    
    # Validate only (check voice markers)
    python3 scripts/voice/reprocess_frontmatter_voice.py --validate-only
"""

import argparse
import logging
import sys
import tempfile
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.voice.post_processor import VoicePostProcessor
from shared.api.client_factory import create_api_client
from components.frontmatter.utils.author_manager import get_author_info_for_material

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FrontmatterVoiceReprocessor:
    """
    Reusable voice post-processor for frontmatter files.
    
    Reads frontmatter, applies voice to text content, saves back.
    """
    
    def __init__(self, api_client, dry_run: bool = False):
        """
        Initialize reprocessor.
        
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
    
    def get_frontmatter_path(self, content_type: str, identifier: str) -> Path:
        """
        Get frontmatter file path for content type and identifier.
        
        Args:
            content_type: 'material', 'region', etc.
            identifier: Content identifier (e.g., 'Aluminum')
            
        Returns:
            Path to frontmatter file
        """
        # Normalize identifier for filename
        normalized = identifier.lower().replace(' ', '-').replace('_', '-')
        filename = f"{normalized}-laser-cleaning.yaml"
        
        base_path = Path('frontmatter')
        
        if content_type == 'material':
            return base_path / 'materials' / filename
        elif content_type == 'region':
            return base_path / 'regions' / filename
        elif content_type == 'contaminant':
            return base_path / 'contaminants' / filename
        elif content_type == 'application':
            return base_path / 'applications' / filename
        elif content_type == 'thesaurus':
            return base_path / 'thesaurus' / filename
        else:
            raise ValueError(f"Unknown content type: {content_type}")
    
    def load_frontmatter(self, file_path: Path) -> Tuple[Dict, Optional[Dict]]:
        """
        Load frontmatter file and extract author data.
        
        Args:
            file_path: Path to frontmatter YAML file
            
        Returns:
            Tuple of (frontmatter_dict, author_data)
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Frontmatter file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            frontmatter = yaml.safe_load(f)
        
        # Extract author data
        author_data = frontmatter.get('author')
        
        if not author_data:
            logger.warning(f"No author data in {file_path}")
            return frontmatter, None
        
        return frontmatter, author_data
    
    def apply_voice_to_caption(
        self,
        caption: Dict,
        author: Dict,
        voice_intensity: int = 3
    ) -> Tuple[Dict, bool]:
        """
        Apply voice to caption before/after text.
        
        Args:
            caption: Caption dictionary with 'before' and 'after' keys
            author: Author data
            voice_intensity: Voice intensity level (1-5)
            
        Returns:
            Tuple of (updated_caption, was_modified)
        """
        modified = False
        updated_caption = caption.copy()
        
        # Process 'before' text
        if 'before' in caption:
            before_text = caption['before']
            enhanced_before = self.voice_processor.enhance(
                text=before_text,
                author=author,
                voice_intensity=voice_intensity,
                preserve_length=True,
                length_tolerance=5
            )
            
            if enhanced_before != before_text:
                updated_caption['before'] = enhanced_before
                modified = True
                logger.info(f"✅ Enhanced caption 'before' section")
        
        # Process 'after' text
        if 'after' in caption:
            after_text = caption['after']
            enhanced_after = self.voice_processor.enhance(
                text=after_text,
                author=author,
                voice_intensity=voice_intensity,
                preserve_length=True,
                length_tolerance=5
            )
            
            if enhanced_after != after_text:
                updated_caption['after'] = enhanced_after
                modified = True
                logger.info(f"✅ Enhanced caption 'after' section")
        
        # Update metadata
        if modified:
            updated_caption['voice_applied'] = datetime.utcnow().isoformat() + 'Z'
            updated_caption['voice_intensity'] = voice_intensity
        
        return updated_caption, modified
    
    def apply_voice_to_subtitle(
        self,
        subtitle: str,
        author: Dict,
        voice_intensity: int = 3
    ) -> Tuple[str, bool]:
        """
        Apply voice to subtitle text.
        
        Args:
            subtitle: Subtitle text
            author: Author data
            voice_intensity: Voice intensity level (1-5)
            
        Returns:
            Tuple of (enhanced_subtitle, was_modified)
        """
        enhanced_subtitle = self.voice_processor.enhance(
            text=subtitle,
            author=author,
            voice_intensity=voice_intensity,
            preserve_length=True,
            length_tolerance=2
        )
        
        modified = enhanced_subtitle != subtitle
        
        if modified:
            logger.info(f"✅ Enhanced subtitle")
        
        return enhanced_subtitle, modified
    
    def apply_voice_to_faq(
        self,
        faq: Dict,
        author: Dict,
        voice_intensity: int = 2
    ) -> Tuple[Dict, bool]:
        """
        Apply voice to FAQ answers.
        
        Args:
            faq: FAQ dictionary with 'questions' list
            author: Author data
            voice_intensity: Voice intensity level (1-5)
            
        Returns:
            Tuple of (updated_faq, was_modified)
        """
        if 'questions' not in faq:
            return faq, False
        
        questions = faq['questions']
        
        # Use batch enhancement for better marker distribution
        enhanced_items = self.voice_processor.enhance_batch(
            faq_items=questions,
            author=author,
            voice_intensity=voice_intensity,
            preserve_length=True,
            length_tolerance=5
        )
        
        # Check if any answers changed
        modified = False
        for original, enhanced in zip(questions, enhanced_items):
            if original.get('answer') != enhanced.get('answer'):
                modified = True
                break
        
        if modified:
            updated_faq = faq.copy()
            updated_faq['questions'] = enhanced_items
            updated_faq['voice_applied'] = datetime.utcnow().isoformat() + 'Z'
            updated_faq['voice_intensity'] = voice_intensity
            logger.info(f"✅ Enhanced FAQ ({len(questions)} answers)")
            return updated_faq, True
        
        return faq, False
    
    def reprocess_frontmatter(
        self,
        file_path: Path,
        voice_intensity: int = 3
    ) -> bool:
        """
        Reprocess frontmatter file with voice enhancement.
        
        Args:
            file_path: Path to frontmatter file
            voice_intensity: Voice intensity level (1-5)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"📝 Processing: {file_path.name}")
            
            # Load frontmatter
            frontmatter, author = self.load_frontmatter(file_path)
            
            if not author:
                logger.warning(f"⏭️  Skipping (no author data): {file_path.name}")
                self.stats['skipped'] += 1
                return False
            
            # Track if anything was modified
            modified = False
            
            # Process caption
            if 'caption' in frontmatter:
                updated_caption, caption_modified = self.apply_voice_to_caption(
                    frontmatter['caption'],
                    author,
                    voice_intensity
                )
                if caption_modified:
                    frontmatter['caption'] = updated_caption
                    modified = True
            
            # Process subtitle
            if 'subtitle' in frontmatter:
                updated_subtitle, subtitle_modified = self.apply_voice_to_subtitle(
                    frontmatter['subtitle'],
                    author,
                    voice_intensity
                )
                if subtitle_modified:
                    frontmatter['subtitle'] = updated_subtitle
                    
                    # Update subtitle metadata
                    if 'subtitle_metadata' not in frontmatter:
                        frontmatter['subtitle_metadata'] = {}
                    frontmatter['subtitle_metadata']['voice_applied'] = datetime.utcnow().isoformat() + 'Z'
                    frontmatter['subtitle_metadata']['voice_intensity'] = voice_intensity
                    modified = True
            
            # Process FAQ
            if 'faq' in frontmatter:
                updated_faq, faq_modified = self.apply_voice_to_faq(
                    frontmatter['faq'],
                    author,
                    voice_intensity
                )
                if faq_modified:
                    frontmatter['faq'] = updated_faq
                    modified = True
            
            if not modified:
                logger.info(f"⏭️  No changes needed: {file_path.name}")
                self.stats['skipped'] += 1
                return True
            
            # Save changes (unless dry run)
            if self.dry_run:
                logger.info(f"🔍 [DRY RUN] Would save changes to: {file_path.name}")
                self.stats['enhanced'] += 1
            else:
                self._save_frontmatter(file_path, frontmatter)
                logger.info(f"💾 Saved enhanced frontmatter: {file_path.name}")
                self.stats['enhanced'] += 1
            
            self.stats['processed'] += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing {file_path.name}: {e}")
            self.stats['errors'] += 1
            return False
    
    def _save_frontmatter(self, file_path: Path, frontmatter: Dict):
        """
        Save frontmatter with atomic write.
        
        Args:
            file_path: Path to frontmatter file
            frontmatter: Frontmatter dictionary
        """
        # Atomic write using temp file
        temp_fd, temp_path = tempfile.mkstemp(
            suffix='.yaml',
            dir=file_path.parent
        )
        
        try:
            import os
            os.close(temp_fd)  # Close file descriptor
            
            # Write to temp file
            with open(temp_path, 'w', encoding='utf-8') as f:
                yaml.dump(
                    frontmatter,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False
                )
            
            # Atomic rename
            Path(temp_path).replace(file_path)
            
        except Exception as e:
            # Cleanup temp file on error
            if Path(temp_path).exists():
                Path(temp_path).unlink()
            raise e
    
    def validate_voice_markers(self, file_path: Path) -> Dict:
        """
        Validate voice markers in frontmatter file.
        
        Args:
            file_path: Path to frontmatter file
            
        Returns:
            Dictionary with validation results
        """
        try:
            frontmatter, author = self.load_frontmatter(file_path)
            
            if not author:
                return {
                    'file': file_path.name,
                    'valid': False,
                    'reason': 'No author data'
                }
            
            results = {
                'file': file_path.name,
                'author': author.get('name'),
                'country': author.get('country'),
                'caption': None,
                'subtitle': None,
                'faq': None
            }
            
            # Validate caption
            if 'caption' in frontmatter:
                before_score = self.voice_processor.get_voice_score(
                    frontmatter['caption'].get('before', ''),
                    author
                )
                after_score = self.voice_processor.get_voice_score(
                    frontmatter['caption'].get('after', ''),
                    author
                )
                results['caption'] = {
                    'before': {
                        'score': before_score['authenticity_score'],
                        'markers': before_score['marker_count']
                    },
                    'after': {
                        'score': after_score['authenticity_score'],
                        'markers': after_score['marker_count']
                    }
                }
            
            # Validate subtitle
            if 'subtitle' in frontmatter:
                subtitle_score = self.voice_processor.get_voice_score(
                    frontmatter['subtitle'],
                    author
                )
                results['subtitle'] = {
                    'score': subtitle_score['authenticity_score'],
                    'markers': subtitle_score['marker_count']
                }
            
            # Validate FAQ
            if 'faq' in frontmatter and 'questions' in frontmatter['faq']:
                questions = frontmatter['faq']['questions']
                faq_scores = []
                
                for qa in questions[:3]:  # Sample first 3
                    score = self.voice_processor.get_voice_score(
                        qa.get('answer', ''),
                        author
                    )
                    faq_scores.append(score['authenticity_score'])
                
                results['faq'] = {
                    'avg_score': sum(faq_scores) / len(faq_scores) if faq_scores else 0,
                    'question_count': len(questions),
                    'sample_size': len(faq_scores)
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Error validating {file_path.name}: {e}")
            return {
                'file': file_path.name,
                'valid': False,
                'reason': str(e)
            }
    
    def print_stats(self):
        """Print processing statistics."""
        print("\n" + "="*80)
        print("📊 VOICE REPROCESSING STATISTICS")
        print("="*80)
        print(f"Processed:  {self.stats['processed']}")
        print(f"Enhanced:   {self.stats['enhanced']}")
        print(f"Skipped:    {self.stats['skipped']}")
        print(f"Errors:     {self.stats['errors']}")
        print("="*80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Reusable voice post-processor for frontmatter files"
    )
    
    # Input options
    parser.add_argument(
        '--file',
        help="Process single frontmatter file (path relative to frontmatter/)"
    )
    parser.add_argument(
        '--content-type',
        choices=['material', 'region', 'contaminant', 'application', 'thesaurus'],
        help="Content type for --identifier"
    )
    parser.add_argument(
        '--identifier',
        help="Content identifier (e.g., 'Aluminum') - requires --content-type"
    )
    parser.add_argument(
        '--all-materials',
        action='store_true',
        help="Process all material frontmatter files"
    )
    parser.add_argument(
        '--all-regions',
        action='store_true',
        help="Process all region frontmatter files"
    )
    
    # Processing options
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help="Only validate voice markers, don't enhance"
    )
    parser.add_argument(
        '--voice-intensity',
        type=int,
        default=3,
        choices=[1, 2, 3, 4, 5],
        help="Voice intensity level (1-5, default: 3)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.identifier and not args.content_type:
        print("❌ Error: --identifier requires --content-type")
        return 1
    
    if not any([args.file, args.identifier, args.all_materials, args.all_regions]):
        parser.print_help()
        return 1
    
    # Initialize API client
    print("🔧 Initializing API client...")
    api_client = create_api_client('grok')
    
    # Initialize reprocessor
    reprocessor = FrontmatterVoiceReprocessor(
        api_client=api_client,
        dry_run=args.dry_run
    )
    
    # Determine files to process
    files_to_process = []
    
    if args.file:
        file_path = Path('frontmatter') / args.file
        files_to_process.append(file_path)
    
    elif args.identifier and args.content_type:
        file_path = reprocessor.get_frontmatter_path(
            args.content_type,
            args.identifier
        )
        files_to_process.append(file_path)
    
    elif args.all_materials:
        materials_dir = Path('frontmatter/materials')
        files_to_process.extend(sorted(materials_dir.glob('*.yaml')))
    
    elif args.all_regions:
        regions_dir = Path('frontmatter/regions')
        files_to_process.extend(sorted(regions_dir.glob('*.yaml')))
    
    if not files_to_process:
        print("❌ No files found to process")
        return 1
    
    print(f"\n📋 Processing {len(files_to_process)} file(s)...")
    print()
    
    # Process files
    if args.validate_only:
        # Validation mode
        results = []
        for file_path in files_to_process:
            result = reprocessor.validate_voice_markers(file_path)
            results.append(result)
        
        # Print validation results
        print("\n" + "="*80)
        print("🔍 VOICE VALIDATION RESULTS")
        print("="*80)
        for result in results:
            print(f"\n{result['file']}:")
            if 'valid' in result and not result['valid']:
                print(f"  ❌ {result.get('reason', 'Unknown error')}")
            else:
                if result.get('caption'):
                    print(f"  Caption before: {result['caption']['before']['score']:.1f}/100 ({result['caption']['before']['markers']} markers)")
                    print(f"  Caption after:  {result['caption']['after']['score']:.1f}/100 ({result['caption']['after']['markers']} markers)")
                if result.get('subtitle'):
                    print(f"  Subtitle: {result['subtitle']['score']:.1f}/100 ({result['subtitle']['markers']} markers)")
                if result.get('faq'):
                    print(f"  FAQ avg: {result['faq']['avg_score']:.1f}/100 ({result['faq']['question_count']} questions)")
    else:
        # Enhancement mode
        for file_path in files_to_process:
            reprocessor.reprocess_frontmatter(
                file_path,
                voice_intensity=args.voice_intensity
            )
        
        # Print statistics
        reprocessor.print_stats()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
