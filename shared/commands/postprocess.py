"""
Postprocessing command for quality validation and regeneration of existing text fields.

This module handles:
1. Loading existing content from frontmatter
2. Analyzing quality using QualityAnalyzer (AI detection, voice, structural)
3. If quality < 60/100: Regenerate from scratch using original domain prompt template
4. If quality >= 60/100: Keep original content
5. Saving regenerated content to data YAML + frontmatter (dual-write)
6. POLICY: Research and generate if field is empty

CRITICAL: Regeneration = Fresh generation from original prompt, NOT refinement of existing text.
"""

import os
import yaml
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from generation.core.evaluated_generator import QualityEvaluatedGenerator
from generation.core.generator import Generator
from shared.api.client_factory import create_api_client
from postprocessing.evaluation.subjective_evaluator import SubjectiveEvaluator
from shared.text.validation.forbidden_phrase_validator import ForbiddenPhraseValidator
from generation.utils.frontmatter_sync import sync_field_to_frontmatter
import logging

logger = logging.getLogger(__name__)


class PostprocessCommand:
    """
    Postprocess existing text fields: validate quality and regenerate if needed.
    
    Quality validation checks:
    - AI detection score (Winston)
    - Voice authenticity (author compliance)
    - Structural quality (sentence variation, rhythm)
    - Composite threshold: 60/100 minimum
    
    Regeneration behavior (when quality < 60/100):
    - Discards old content completely
    - Calls generator.generate() with original domain prompt template
    - Fresh generation (same as initial creation, NOT refinement)
    - Saves if successful, keeps original if regeneration fails
    """
    
    def __init__(self, domain: str, field: str):
        """
        Initialize postprocessing command.
        
        Args:
            domain: Domain name (materials, contaminants, settings)
            field: Field name to postprocess (description, micro, faq, etc.)
        """
        self.domain = domain
        self.field = field
        self.phrase_validator = ForbiddenPhraseValidator()
        
        # Initialize API client and evaluator
        self.api_client = create_api_client()
        self.evaluator = SubjectiveEvaluator(self.api_client)
        
        # Create domain-specific generator
        domain_generator = Generator(api_client=self.api_client, domain=domain)
        
        # Create evaluated generator
        self.generator = QualityEvaluatedGenerator(
            api_client=self.api_client,
            subjective_evaluator=self.evaluator
        )
        self.generator.generator = domain_generator
    
    def _load_frontmatter(self, item_name: str) -> Dict[str, Any]:
        """Load frontmatter YAML file for item using domain config pattern"""
        frontmatter_dir = f"frontmatter/{self.domain}"
        
        # Get filename pattern from domain config
        from generation.core.adapters.domain_adapter import DomainAdapter
        try:
            adapter = DomainAdapter(self.domain)
            pattern = adapter.config.get('frontmatter_filename_pattern', '{slug}.yaml')
        except:
            pattern = '{slug}.yaml'
        
        # Create slug (remove parentheses for consistency)
        slug = item_name.lower().replace(' ', '-').replace('(', '').replace(')', '')
        while '--' in slug:
            slug = slug.replace('--', '-')
        slug = slug.strip('-')
        
        # Apply pattern
        filename = pattern.format(slug=slug)
        yaml_file = f"{frontmatter_dir}/{filename}"
        
        if not os.path.exists(yaml_file):
            # Try alternative naming patterns
            for file in Path(frontmatter_dir).glob("*.yaml"):
                with open(file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data.get('name') == item_name or data.get('slug') == slug:
                        yaml_file = str(file)
                        break
        
        if not os.path.exists(yaml_file):
            raise FileNotFoundError(f"Frontmatter not found for {item_name} in {frontmatter_dir}")
        
        with open(yaml_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f), yaml_file
    
    def _save_frontmatter(self, yaml_file: str, data: Dict[str, Any]):
        """Save updated frontmatter back to YAML file"""
        with open(yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    def _load_domain_config(self) -> Dict[str, Any]:
        """Load domain config to get data paths"""
        config_path = Path(f"domains/{self.domain}/config.yaml")
        if not config_path.exists():
            raise FileNotFoundError(f"Domain config not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _get_data_path(self) -> Path:
        """Get path to domain data YAML file"""
        config = self._load_domain_config()
        data_path = config.get('data_path', f"data/{self.domain}/{self.domain.title()}.yaml")
        return Path(data_path)
    
    def _save_to_data_yaml(self, item_name: str, content: str) -> None:
        """Save content to data YAML file (dual-write requirement)"""
        data_path = self._get_data_path()
        
        if not data_path.exists():
            logger.warning(f"Data file not found: {data_path} - skipping data save")
            return
        
        # Load current data
        with open(data_path, 'r', encoding='utf-8') as f:
            all_data = yaml.safe_load(f)
        
        # Get root key from config
        config = self._load_domain_config()
        data_root_key = config.get('data_root_key', self.domain)
        
        # Verify item exists
        items = all_data.get(data_root_key, {})
        if item_name not in items:
            logger.warning(f"'{item_name}' not found in {data_path} - skipping data save")
            return
        
        # Write content to item
        items[item_name][self.field] = content
        
        # Atomic write with temp file (same pattern as DomainAdapter)
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            dir=data_path.parent,
            delete=False,
            suffix='.yaml'
        ) as temp_f:
            yaml.dump(all_data, temp_f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            temp_path = temp_f.name
        
        Path(temp_path).replace(data_path)
        logger.info(f"✅ {self.field} written to {data_path} → {data_root_key}.{item_name}.{self.field}")
    
    def _get_field_content(self, frontmatter: Dict[str, Any]) -> Optional[str]:
        """Extract field content from frontmatter"""
        content = frontmatter.get(self.field)
        
        # Handle different field types
        if content is None or content == 'null' or content == '':
            return None
        
        # FAQ is an array, convert to string for processing
        if self.field == 'faq' and isinstance(content, list):
            return yaml.dump(content, default_flow_style=False)
        
        return str(content).strip() if content else None
    
    def _set_field_content(self, frontmatter: Dict[str, Any], content: str):
        """Set field content in frontmatter"""
        # FAQ needs to be parsed back to array
        if self.field == 'faq':
            frontmatter[self.field] = yaml.safe_load(content)
        else:
            frontmatter[self.field] = content
    
    def _build_postprocess_context(self, item_name: str, frontmatter: Dict[str, Any], existing_content: str) -> Dict[str, str]:
        """Build context dictionary for postprocessing prompt"""
        author = frontmatter.get('author', {})
        
        context = {
            'existing_content': existing_content,
            'author_name': author.get('name', 'Unknown'),
            'author_country': author.get('country', 'Unknown'),
        }
        
        # Domain-specific context
        if self.domain == 'materials':
            context['material_name'] = frontmatter.get('name', item_name)
            context['category'] = frontmatter.get('category', 'unknown')
            context['subcategory'] = frontmatter.get('subcategory', 'unknown')
        elif self.domain == 'contaminants':
            context['contaminant_name'] = frontmatter.get('name', item_name)
            context['category'] = frontmatter.get('category', 'unknown')
            context['context_notes'] = frontmatter.get('context', 'general')
        elif self.domain == 'settings':
            context['material_name'] = frontmatter.get('name', item_name)
            context['category'] = frontmatter.get('category', 'unknown')
        
        return context
    
    def _check_winston(self, text: str) -> float:
        """Check Winston AI detection score (stub - uses generator's method)"""
        # This will be integrated with actual Winston API
        return 0.95  # Placeholder
    
    def _check_readability(self, text: str) -> dict:
        """Check forbidden phrases and patterns"""
        violations = self.phrase_validator.validate(text)
        return {
            'status': 'pass' if not violations else 'fail',
            'violations': violations
        }
    
    def _detect_ai_patterns(self, text: str) -> List[str]:
        """Detect AI-like patterns in text"""
        ai_patterns = [
            'presents a challenge',
            'presents a unique challenge',
            'critical aspect',
            'critical pitfall',
            'it is essential',
            'it is important to note',
            'furthermore',
            'moreover',
            'in conclusion',
        ]
        
        found_patterns = []
        text_lower = text.lower()
        
        for pattern in ai_patterns:
            if pattern in text_lower:
                found_patterns.append(pattern)
        
        return found_patterns
    
    def _compare_versions(self, old: str, new: str) -> Dict[str, Any]:
        """Compare old vs new content quality"""
        old_readability = self._check_readability(old)
        new_readability = self._check_readability(new)
        
        old_ai_patterns = self._detect_ai_patterns(old)
        new_ai_patterns = self._detect_ai_patterns(new)
        
        length_change = len(new) - len(old)
        length_change_pct = (length_change / len(old)) * 100 if len(old) > 0 else 0
        
        scores = {
            'old_readability': old_readability.get('status', 'unknown'),
            'new_readability': new_readability.get('status', 'unknown'),
            'old_ai_patterns': old_ai_patterns,
            'new_ai_patterns': new_ai_patterns,
            'length_change': length_change,
            'length_change_pct': length_change_pct,
            'old_length': len(old),
            'new_length': len(new)
        }
        
        # Determine if improvement
        # Readability: Must improve OR stay same (neutral)
        readability_improved = (
            new_readability.get('status') == 'pass' and 
            old_readability.get('status') != 'pass'
        )
        readability_neutral = (
            new_readability.get('status') == old_readability.get('status')
        )
        readability_ok = readability_improved or readability_neutral
        
        # AI patterns: Must reduce OR stay at zero (neutral)
        ai_patterns_reduced = len(new_ai_patterns) < len(old_ai_patterns)
        ai_patterns_neutral = (
            len(new_ai_patterns) == 0 and len(old_ai_patterns) == 0
        )
        ai_patterns_ok = ai_patterns_reduced or ai_patterns_neutral
        
        # Overall improvement: All criteria must pass (improved OR neutral)
        # NOTE: Length criteria removed per user request (Dec 13, 2025)
        improved = (
            readability_ok and
            ai_patterns_ok
        )
        
        return {
            'quality_improved': improved,
            'scores': scores,
            'recommendation': 'REPLACE' if improved else 'KEEP_ORIGINAL',
            'criteria': {
                'Readability OK': readability_ok,
                'AI Patterns OK': ai_patterns_ok,
            }
        }
    
    def postprocess_item(self, item_name: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Postprocess single item's field.
        
        POLICY: If field is empty, research and generate it instead.
        
        Args:
            item_name: Name of the item to postprocess
            dry_run: If True, compare but don't save
            
        Returns:
            Dictionary with results and comparison
        """
        print(f"\n{'='*80}")
        print(f"📝 POSTPROCESSING: {item_name} - {self.field}")
        print(f"{'='*80}")
        
        # Load frontmatter
        frontmatter, yaml_file = self._load_frontmatter(item_name)
        
        # Get existing content
        existing_content = self._get_field_content(frontmatter)
        
        # POLICY: If empty, research and generate
        if not existing_content:
            print(f"⚠️  Field '{self.field}' is EMPTY for {item_name}")
            print(f"📊 POLICY: Research and generate new content...")
            
            # Generate new content using standard generation
            result = self.generator.generate(
                item_name=item_name,
                component_type=self.field,
                author_id=frontmatter.get('author', {}).get('id')
            )
            
            if result.success:
                self._set_field_content(frontmatter, result.content)
                if not dry_run:
                    self._save_frontmatter(yaml_file, frontmatter)
                    print(f"✅ Generated and saved new content ({len(result.content)} chars)")
                else:
                    print(f"✅ Generated new content ({len(result.content)} chars) [DRY RUN - not saved]")
                
                return {
                    'item': item_name,
                    'field': self.field,
                    'action': 'GENERATED_NEW',
                    'improved': True,
                    'new_content': result.content,
                    'dry_run': dry_run
                }
            else:
                print(f"❌ Failed to generate new content: {result.error}")
                return {
                    'item': item_name,
                    'field': self.field,
                    'action': 'GENERATION_FAILED',
                    'improved': False,
                    'error': result.error
                }
        
        # Existing content - evaluate using pipeline's QualityAnalyzer
        print(f"📄 Current content: {len(existing_content)} chars")
        
        # Use same quality analyzer as generation pipeline
        from shared.voice.quality_analyzer import QualityAnalyzer
        analyzer = QualityAnalyzer(self.generator.api_client, strict_mode=False)
        
        # Get author data for voice validation
        author_data = self.generator._get_author_data(item_name)
        
        print(f"🔍 Analyzing quality (using pipeline's validator)...")
        quality_analysis = analyzer.analyze(
            text=existing_content,
            author=author_data,
            include_recommendations=False
        )
        
        print(f"   • Overall Score: {quality_analysis['overall_score']}/100")
        print(f"   • AI Patterns: {quality_analysis['ai_patterns']['score']}/100")
        print(f"   • Voice Authenticity: {quality_analysis['voice_authenticity']['score']}/100")
        
        # Use pipeline's threshold (60/100 allows concise content to pass)
        # Lowered from 70 to account for single-sentence material_description content
        # which appropriately scores lower on structural variation metrics
        QUALITY_THRESHOLD = 60
        MIN_CONTENT_LENGTH = 150  # Minimum characters for acceptable content
        
        # Check minimum length first
        if len(existing_content) < MIN_CONTENT_LENGTH:
            print(f"\n⚠️  Content too short ({len(existing_content)} chars < {MIN_CONTENT_LENGTH} minimum) - regenerating...")
        elif quality_analysis['overall_score'] >= QUALITY_THRESHOLD:
            print(f"\n✅ Content meets quality threshold ({QUALITY_THRESHOLD}/100) - keeping original")
            return {
                'item': item_name,
                'field': self.field,
                'action': 'KEPT_ORIGINAL',
                'improved': False,
                'reason': f"Quality score {quality_analysis['overall_score']}/100 passes threshold"
            }
        
        # Store old quality metrics BEFORE regenerating
        old_ai_patterns = self._detect_ai_patterns(existing_content)
        old_readability = self._check_readability(existing_content)
        
        # Regenerate using FULL PIPELINE (Core Principle #0)
        print(f"\n🔧 Quality score {quality_analysis['overall_score']}/100 below threshold - regenerating...")
        
        try:
            # Use existing generator.generate() which includes ALL quality checks:
            # - Humanness layer (structural variation)
            # - Voice validation (author compliance)
            # - Quality evaluation (Winston, realism, diversity)
            # - Learning database logging
            # - Dual-write (data YAML + frontmatter sync)
            
            result = self.generator.generate(
                material_name=item_name,
                component_type=self.field,
                faq_count=None
            )
            
            # Result is a QualityEvaluatedResult dataclass, not a dict
            if not result or not result.success or not result.content:
                error_msg = result.error_message if result else 'No result returned'
                print(f"❌ Regeneration failed: {error_msg}")
                return {
                    'item': item_name,
                    'field': self.field,
                    'action': 'REGENERATION_FAILED',
                    'improved': False,
                    'error': error_msg
                }
            
            new_content = result.content
            if isinstance(new_content, dict):
                # FAQ returns dict, extract text
                new_content = str(new_content)
            new_content = new_content.strip()
            
            # Note: generator.generate() already saved via dual-write
            # We just need to verify and report
            print(f"\n✨ Regenerated: {len(new_content)} chars")
            
            # Check new quality
            new_ai_patterns = self._detect_ai_patterns(new_content)
            new_readability = self._check_readability(new_content)
            
            print(f"🔍 New quality:")
            print(f"   • Readability: {new_readability.get('status', 'unknown')}")
            print(f"   • AI patterns: {len(new_ai_patterns)} detected")
            
            # Compare old vs new
            print(f"\n📊 QUALITY COMPARISON:")
            print(f"   Old readability: {old_readability.get('status', 'unknown')}")
            print(f"   New readability: {new_readability.get('status', 'unknown')}")
            print(f"   Old AI patterns: {len(old_ai_patterns)}")
            print(f"   New AI patterns: {len(new_ai_patterns)}")
            print(f"   Length change: {len(existing_content)} → {len(new_content)} chars")
            
            # Determine if improved
            readability_improved = (
                new_readability.get('status') == 'pass' and
                old_readability.get('status') != 'pass'
            )
            ai_patterns_improved = len(new_ai_patterns) < len(old_ai_patterns)
            
            improved = readability_improved or ai_patterns_improved
            
            if improved:
                print(f"\n✅ Content IMPROVED and saved (dual-write complete)")
            else:
                print(f"\n⚠️  Content regenerated but quality similar (dual-write complete)")
            
            return {
                'item': item_name,
                'field': self.field,
                'action': 'REGENERATED',
                'improved': improved,
                'old_content': existing_content,
                'new_content': new_content,
                'old_quality': {
                    'readability': old_readability.get('status'),
                    'ai_patterns': len(old_ai_patterns)
                },
                'new_quality': {
                    'readability': new_readability.get('status'),
                    'ai_patterns': len(new_ai_patterns)
                }
            }
            
        except Exception as e:
            print(f"❌ Regeneration failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'item': item_name,
                'field': self.field,
                'action': 'REGENERATION_FAILED',
                'improved': False,
                'error': str(e)
            }
    
    def postprocess_all(self, batch_size: int = 10, dry_run: bool = False) -> List[Dict[str, Any]]:
        """
        Postprocess all items in domain with this field.
        
        Args:
            batch_size: Number of items to process before checkpoint
            dry_run: If True, compare but don't save
            
        Returns:
            List of result dictionaries
        """
        # Get all items in domain
        items = self._list_items_with_field()
        
        print(f"\n{'='*80}")
        print(f"📦 BATCH POSTPROCESSING")
        print(f"{'='*80}")
        print(f"Domain: {self.domain}")
        print(f"Field: {self.field}")
        print(f"Total items: {len(items)}")
        print(f"Batch size: {batch_size}")
        print(f"Dry run: {dry_run}")
        print(f"{'='*80}\n")
        
        results = []
        improved_count = 0
        failed_count = 0
        
        for i, item in enumerate(items, 1):
            try:
                result = self.postprocess_item(item, dry_run=dry_run)
                results.append(result)
                
                if result.get('improved'):
                    improved_count += 1
                elif result.get('action') in ['POSTPROCESS_FAILED', 'GENERATION_FAILED']:
                    failed_count += 1
                
                if i % batch_size == 0:
                    print(f"\n{'='*80}")
                    print(f"📊 CHECKPOINT: {i}/{len(items)} items processed")
                    print(f"   Improved: {improved_count}")
                    print(f"   Failed: {failed_count}")
                    print(f"   Kept original: {i - improved_count - failed_count}")
                    print(f"{'='*80}\n")
            
            except Exception as e:
                print(f"❌ Error processing {item}: {e}")
                results.append({
                    'item': item,
                    'field': self.field,
                    'action': 'ERROR',
                    'improved': False,
                    'error': str(e)
                })
                failed_count += 1
        
        # Final summary
        print(f"\n{'='*80}")
        print(f"📊 FINAL SUMMARY")
        print(f"{'='*80}")
        print(f"Total processed: {len(items)}")
        print(f"✅ Improved: {improved_count} ({improved_count/len(items)*100:.1f}%)")
        print(f"⚠️  Kept original: {len(items) - improved_count - failed_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"{'='*80}\n")
        
        return results
    
    def _list_items_with_field(self) -> List[str]:
        """List all items in domain that have this field"""
        frontmatter_dir = f"frontmatter/{self.domain}"
        items = []
        
        for yaml_file in Path(frontmatter_dir).glob("*.yaml"):
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                # Check if field exists (even if empty, we'll generate it)
                item_name = data.get('name', data.get('slug', yaml_file.stem))
                items.append(item_name)
        
        return sorted(items)
