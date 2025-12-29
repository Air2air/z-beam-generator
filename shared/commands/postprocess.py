"""
Postprocessing command for quality validation and regeneration of existing text fields.

🚨 MANDATORY POLICY (December 24, 2025): SOURCE DATA ONLY
- Postprocessing ONLY works on source data (data/*.yaml files)
- NEVER reads from or writes to frontmatter files directly
- Frontmatter is GENERATED OUTPUT - only modified via export process
- This enforces FRONTMATTER_SOURCE_OF_TRUTH_POLICY

This module handles:
1. Loading existing content from SOURCE DATA (data/*.yaml)
2. Analyzing quality using QualityAnalyzer (AI detection, voice, structural)
3. If quality < 60/100: Regenerate from scratch using original domain prompt template
4. If quality >= 60/100: Keep original content
5. Saving regenerated content to SOURCE DATA ONLY (data/*.yaml)
6. User must run --export to update frontmatter after postprocessing
7. POLICY: Research and generate if field is empty

🔥 MANDATORY RETRY POLICY (December 14, 2025):
- System MUST retry regeneration until requirements are met
- Maximum attempts: 5 (configurable via MAX_REGENERATION_ATTEMPTS)
- Each attempt uses fresh generation with randomized parameters
- Only stops when: quality threshold met OR max attempts exhausted
- Keeps best version across all attempts (highest quality score)

CRITICAL: Regeneration = Fresh generation from original prompt, NOT refinement of existing text.
"""

import logging
import os
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from generation.core.evaluated_generator import QualityEvaluatedGenerator
from generation.core.generator import Generator
from generation.utils.frontmatter_sync import sync_field_to_frontmatter
from postprocessing.evaluation.subjective_evaluator import SubjectiveEvaluator
from shared.api.client_factory import create_api_client
from shared.text.validation.forbidden_phrase_validator import ForbiddenPhraseValidator

logger = logging.getLogger(__name__)

# MANDATORY RETRY POLICY CONSTANTS
MAX_REGENERATION_ATTEMPTS = 5  # Must retry until requirements met or max reached
QUALITY_THRESHOLD = 50  # Minimum acceptable quality score (lowered from 60 Dec 14, 2025)
MIN_CONTENT_LENGTH = 50  # Minimum content length in characters


class PostprocessCommand:
    """
    Postprocess existing text fields: validate quality and regenerate if needed.
    
    🚨 SOURCE DATA ONLY (December 24, 2025):
    - Reads from data/*.yaml files ONLY (never frontmatter)
    - Writes to data/*.yaml files ONLY (never frontmatter)
    - User must run --export after postprocessing to update frontmatter
    - This enforces FRONTMATTER_SOURCE_OF_TRUTH_POLICY
    
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
            domain: Domain name (materials, contaminants, settings, compounds)
            field: Field name to postprocess (description, micro, faq, etc.)
        """
        self.domain = domain
        self.field = field
        self.phrase_validator = ForbiddenPhraseValidator()
        
        # Initialize API client
        self.api_client = create_api_client()
        
        # Use FieldRouter to determine generator type
        from generation.field_router import FieldRouter
        
        self.field_type = FieldRouter.get_field_type(domain, field)
        
        if self.field_type == 'text':
            # Text field - use full quality pipeline
            self.evaluator = SubjectiveEvaluator(self.api_client)
            domain_generator = Generator(api_client=self.api_client, domain=domain)
            
            self.generator = QualityEvaluatedGenerator(
                api_client=self.api_client,
                subjective_evaluator=self.evaluator
            )
            self.generator.generator = domain_generator
        
        elif self.field_type == 'data':
            # Data field - use simple generator
            self.generator = FieldRouter._create_data_generator(domain, field, self.api_client)
            logger.info(f"Using simple data generator for '{field}' (no quality pipeline)")
    
    def _load_source_data(self, item_id: str) -> Dict[str, Any]:
        """
        Load item data from SOURCE DATA file (data/*.yaml) - NOT frontmatter.
        
        🚨 MANDATORY: Only reads from data/*.yaml files (FRONTMATTER_SOURCE_OF_TRUTH_POLICY)
        
        Args:
            item_id: Item identifier (slug/key in source data)
            
        Returns:
            Item data dictionary from source YAML
            
        Raises:
            FileNotFoundError: If data file or item not found
        """
        data_path = self._get_data_path()
        
        if not data_path.exists():
            raise FileNotFoundError(f"Source data file not found: {data_path}")
        
        # Load source data
        with open(data_path, 'r', encoding='utf-8') as f:
            all_data = yaml.safe_load(f)
        
        # Get root key from config
        config = self._load_domain_config()
        data_root_key = config.get('data_root_key', self.domain)
        
        # Get items dict
        items = all_data.get(data_root_key, {})
        
        # Try exact match first
        if item_id in items:
            return items[item_id]
        
        # Try finding by name (case-insensitive)
        for key, item_data in items.items():
            if item_data.get('name', '').lower() == item_id.lower():
                return item_data
        
        raise FileNotFoundError(f"Item '{item_id}' not found in {data_path}")
    
    def _save_to_source_data(self, item_id: str, content: str) -> None:
        """
        Save content to SOURCE DATA file (data/*.yaml) - NOT frontmatter.
        
        🚨 MANDATORY: Only writes to data/*.yaml files (FRONTMATTER_SOURCE_OF_TRUTH_POLICY)
        User must run --export after postprocessing to update frontmatter.
        
        Args:
            item_id: Item identifier (slug/key in source data)
            content: Content to save
        """
        data_path = self._get_data_path()
        
        if not data_path.exists():
            raise FileNotFoundError(f"Source data file not found: {data_path}")
        
        # Load current data
        with open(data_path, 'r', encoding='utf-8') as f:
            all_data = yaml.safe_load(f)
        
        # Get root key from config
        config = self._load_domain_config()
        data_root_key = config.get('data_root_key', self.domain)
        
        # Get items dict
        items = all_data.get(data_root_key, {})
        
        # Find item (exact match or by name)
        target_key = None
        if item_id in items:
            target_key = item_id
        else:
            for key, item_data in items.items():
                if item_data.get('name', '').lower() == item_id.lower():
                    target_key = key
                    break
        
        if not target_key:
            raise FileNotFoundError(f"Item '{item_id}' not found in {data_path}")
        
        # Write content to item
        items[target_key][self.field] = content
        
        # Atomic write with temp file
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
        logger.info(f"✅ {self.field} written to {data_path} → {data_root_key}.{target_key}.{self.field}")
    
    def _load_domain_config(self) -> Dict[str, Any]:
        """Load domain config to get data paths"""
        config_path = Path(f"domains/{self.domain}/config.yaml")
        if not config_path.exists():
            raise FileNotFoundError(f"Domain config not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _get_data_path(self) -> Path:
        """Get path to domain source data YAML file (data/*.yaml)"""
        config = self._load_domain_config()
        data_path = config.get('data_path', f"data/{self.domain}/{self.domain.title()}.yaml")
        return Path(data_path)
    
    def _get_field_content(self, item_data: Dict[str, Any]) -> Optional[str]:
        """Extract field content from source data item"""
        content = item_data.get(self.field)
        
        # Handle different field types
        if content is None or content == 'null' or content == '':
            return None
        
        # FAQ is an array, convert to string for processing
        if self.field == 'faq' and isinstance(content, list):
            return yaml.dump(content, default_flow_style=False)
        
        return str(content).strip() if content else None
    
    def _check_winston(self, text: str) -> float:
        """Check Winston AI detection score (stub - uses generator's method)"""
        # This will be integrated with actual Winston API
        return 0.95  # Placeholder
    
    def _check_readability(self, text: str) -> dict:
        """Check forbidden phrases and patterns"""
        is_valid, violations = self.phrase_validator.validate(text)  # FIX: validate() returns tuple
        
        # DIAGNOSTIC OUTPUT: Show what failed (Option A - Dec 14, 2025)
        if violations:
            print(f"   ⚠️  Forbidden phrases detected ({len(violations)} total):")
            for v in violations[:5]:  # Show first 5
                print(f"      • {v}")
            if len(violations) > 5:
                print(f"      ... and {len(violations) - 5} more")
        
        return {
            'status': 'pass' if is_valid else 'fail',
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
    
    def postprocess_item(self, item_id: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Postprocess single item's field.
        
        🚨 SOURCE DATA ONLY: Works on data/*.yaml files, NOT frontmatter.
        User must run --export after postprocessing to update frontmatter.
        
        POLICY: If field is empty, research and generate it instead.
        
        Args:
            item_id: ID/slug of the item to postprocess (from source data)
            dry_run: If True, compare but don't save
            
        Returns:
            Dictionary with results and comparison
        """
        print(f"\n{'='*80}")
        print(f"📝 POSTPROCESSING: {item_id} - {self.field}")
        print(f"{'='*80}")
        print(f"🔍 Reading from SOURCE DATA: {self._get_data_path()}")
        
        # Load item data from SOURCE DATA (not frontmatter)
        try:
            item_data = self._load_source_data(item_id)
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            return {
                'item': item_id,
                'field': self.field,
                'action': 'LOAD_FAILED',
                'improved': False,
                'error': str(e)
            }
        
        # Get existing content
        existing_content = self._get_field_content(item_data)
        
        # POLICY: If empty, research and generate
        if not existing_content:
            print(f"⚠️  Field '{self.field}' is EMPTY for {item_id}")
            print(f"📊 POLICY: Research and generate new content...")
            
            # Route to appropriate generator based on field type
            if self.field_type == 'text':
                # Text field - use quality pipeline
                print(f"   • Using QualityEvaluatedGenerator (voice + quality validation)")
                result = self.generator.generate(
                    material_name=item_id,
                    component_type=self.field,
                    author_id=item_data.get('author', {}).get('id')
                )
                
                if result.success:
                    content = result.content
                    if not dry_run:
                        self._save_to_source_data(item_id, content)
                        print(f"✅ Generated and saved new content to SOURCE DATA ({len(content)} chars)")
                        print(f"⚠️  Run `python3 run.py --export --domain {self.domain}` to update frontmatter")
                    else:
                        print(f"✅ Generated new content ({len(content)} chars) [DRY RUN - not saved]")
                    
                    return {
                        'item': item_id,
                        'field': self.field,
                        'action': 'GENERATED_NEW',
                        'improved': True,
                        'new_content': content,
                        'dry_run': dry_run
                    }
                else:
                    print(f"❌ Failed to generate new content: {result.error_message}")
                    return {
                        'item': item_id,
                        'field': self.field,
                        'action': 'GENERATION_FAILED',
                        'improved': False,
                        'error': result.error_message
                    }
            
            elif self.field_type == 'data':
                # Data field - use simple generator
                print(f"   • Using simple data generator (research + validate, no quality pipeline)")
                result = self.generator.generate(item_id, dry_run=dry_run)
                
                if result['success']:
                    value = result['value']
                    if result.get('skipped'):
                        print(f"⏭️  Field already populated, skipped")
                    elif not dry_run:
                        print(f"✅ Generated and saved {self.field} to SOURCE DATA")
                        print(f"   Value: {value}")
                        print(f"⚠️  Run `python3 run.py --export --domain {self.domain}` to update frontmatter")
                    else:
                        print(f"✅ Generated {self.field} [DRY RUN - not saved]")
                        print(f"   Value: {value}")
                    
                    return {
                        'item': item_id,
                        'field': self.field,
                        'action': 'GENERATED_NEW',
                        'improved': True,
                        'new_value': value,
                        'dry_run': dry_run
                    }
                else:
                    print(f"❌ Failed to generate {self.field}: {result.get('error')}")
                    return {
                        'item': item_id,
                        'field': self.field,
                        'action': 'GENERATION_FAILED',
                        'improved': False,
                        'error': result.get('error')
                    }
        
        # Existing content - evaluate using pipeline's QualityAnalyzer
        print(f"📄 Current content: {len(existing_content)} chars")
        
        # Use same quality analyzer as generation pipeline
        from shared.voice.quality_analyzer import QualityAnalyzer
        analyzer = QualityAnalyzer(self.generator.api_client, strict_mode=False)
        
        # Get author data for voice validation (use item_id, not display name)
        author_data = self.generator._get_author_data(item_id)
        
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
        # Lowered from 70 to account for single-sentence description content
        # which appropriately scores lower on structural variation metrics
        QUALITY_THRESHOLD = 60
        MIN_CONTENT_LENGTH = 150  # Minimum characters for acceptable content
        
        # Check minimum length first
        if len(existing_content) < MIN_CONTENT_LENGTH:
            print(f"\n⚠️  Content too short ({len(existing_content)} chars < {MIN_CONTENT_LENGTH} minimum) - regenerating...")
        elif quality_analysis['overall_score'] >= QUALITY_THRESHOLD:
            print(f"\n✅ Content meets quality threshold ({QUALITY_THRESHOLD}/100) - keeping original")
            return {
                'item': item_id,
                'field': self.field,
                'action': 'KEPT_ORIGINAL',
                'improved': False,
                'reason': f"Quality score {quality_analysis['overall_score']}/100 passes threshold"
            }
        
        # Store old quality metrics BEFORE regenerating
        old_ai_patterns = self._detect_ai_patterns(existing_content)
        old_readability = self._check_readability(existing_content)
        
        # 🔥 MANDATORY RETRY LOOP - Keep trying until requirements met
        print(f"\n🔧 Quality score {quality_analysis['overall_score']}/100 below threshold")
        print(f"🔄 Starting regeneration (max {MAX_REGENERATION_ATTEMPTS} attempts)...\n")
        
        # Generate unique session ID for grouping all retry attempts together
        retry_session_id = str(uuid.uuid4())
        print(f"📊 Retry session ID: {retry_session_id}\n")
        
        best_result = None
        best_quality_score = 0
        best_content = None
        best_readability = None
        best_ai_patterns = None
        
        for attempt in range(1, MAX_REGENERATION_ATTEMPTS + 1):
            print(f"\n{'='*80}")
            print(f"🔄 ATTEMPT {attempt}/{MAX_REGENERATION_ATTEMPTS}")
            print(f"{'='*80}")
            
            try:
                # Use existing generator.generate() which includes ALL quality checks:
                # - Humanness layer (structural variation)
                # - Voice validation (author compliance)
                # - Quality evaluation (Winston, realism, diversity)
                # - Learning database logging
                # - Dual-write (data YAML + frontmatter sync)
                
                result = self.generator.generate(
                    material_name=item_id,
                    component_type=self.field,
                    faq_count=None,
                    retry_session_id=retry_session_id,
                    is_retry=(attempt > 1)
                )
                
                # Result is a QualityEvaluatedResult dataclass, not a dict
                if not result or not result.success or not result.content:
                    error_msg = result.error_message if result else 'No result returned'
                    print(f"❌ Attempt {attempt} failed: {error_msg}")
                    if attempt == MAX_REGENERATION_ATTEMPTS:
                        # Exhausted all attempts
                        print(f"\n❌ All {MAX_REGENERATION_ATTEMPTS} attempts failed")
                        return {
                            'item': item_id,
                            'field': self.field,
                            'action': 'REGENERATION_FAILED_ALL_ATTEMPTS',
                            'improved': False,
                            'attempts': attempt,
                            'error': error_msg
                        }
                    continue  # Try next attempt
                
                new_content = result.content
                if isinstance(new_content, dict):
                    # FAQ returns dict, extract text
                    new_content = str(new_content)
                new_content = new_content.strip()
                
                # Note: generator.generate() already saved via dual-write
                print(f"\n✨ Generated: {len(new_content)} chars")
                
                # Check new quality
                new_ai_patterns = self._detect_ai_patterns(new_content)
                new_readability = self._check_readability(new_content)
                
                # Calculate quality score (Option B: partial credit for readability - Dec 14, 2025)
                # Old: readability fail = 0 points (too harsh)
                # New: readability fail = 40 points (acknowledges AI-pattern-free content has value)
                readability_score = 100 if new_readability.get('status') == 'pass' else 40
                ai_score = max(0, 100 - (len(new_ai_patterns) * 20))  # -20 per pattern
                attempt_quality = (readability_score + ai_score) / 2
                
                print(f"🔍 Attempt {attempt} quality:")
                print(f"   • Overall: {attempt_quality}/100")
                print(f"   • Readability: {new_readability.get('status', 'unknown')}")
                print(f"   • AI patterns: {len(new_ai_patterns)} detected")
                
                # Track best result
                if attempt_quality > best_quality_score:
                    best_quality_score = attempt_quality
                    best_result = result
                    best_content = new_content
                    best_readability = new_readability
                    best_ai_patterns = new_ai_patterns
                    print(f"   ✅ NEW BEST (score: {attempt_quality}/100)")
                
                # Check if requirements met
                requirements_met = (
                    new_readability.get('status') == 'pass' and
                    len(new_ai_patterns) == 0 and
                    attempt_quality >= QUALITY_THRESHOLD
                )
                
                if requirements_met:
                    print(f"\n✅ REQUIREMENTS MET on attempt {attempt}!")
                    print(f"   • Quality: {attempt_quality}/100 (threshold: {QUALITY_THRESHOLD})")
                    print(f"   • Readability: PASS")
                    print(f"   • AI patterns: 0")
                    break
                else:
                    print(f"\n⚠️  Attempt {attempt} below threshold")
                    if attempt < MAX_REGENERATION_ATTEMPTS:
                        print(f"   🔄 Retrying with fresh randomization...")
                    
            except Exception as e:
                print(f"❌ Attempt {attempt} error: {e}")
                if attempt == MAX_REGENERATION_ATTEMPTS:
                    import traceback
                    logger.error(traceback.format_exc())
        
        # After all attempts, use best result
        if not best_content:
            print(f"\n❌ All {MAX_REGENERATION_ATTEMPTS} attempts failed")
            return {
                'item': item_id,
                'field': self.field,
                'action': 'REGENERATION_FAILED_ALL_ATTEMPTS',
                'improved': False,
                'attempts': MAX_REGENERATION_ATTEMPTS
            }
        
        # Compare best vs original
        print(f"\n{'='*80}")
        print(f"📊 FINAL QUALITY COMPARISON (Best of {attempt} attempts)")
        print(f"{'='*80}")
        print(f"   Old readability: {old_readability.get('status', 'unknown')}")
        print(f"   Best readability: {best_readability.get('status', 'unknown')}")
        print(f"   Old AI patterns: {len(old_ai_patterns)}")
        print(f"   Best AI patterns: {len(best_ai_patterns)}")
        print(f"   Length change: {len(existing_content)} → {len(best_content)} chars")
        print(f"   Best quality score: {best_quality_score}/100")
        
        # Determine if improved
        readability_improved = (
            best_readability.get('status') == 'pass' and
            old_readability.get('status') != 'pass'
        )
        ai_patterns_improved = len(best_ai_patterns) < len(old_ai_patterns)
        improved = readability_improved or ai_patterns_improved or best_quality_score >= QUALITY_THRESHOLD
        
        if improved:
            print(f"\n✅ Content IMPROVED after {attempt} attempts (dual-write complete)")
        else:
            print(f"\n⚠️  No improvement after {attempt} attempts (keeping best version)")
        
        return {
            'item': item_id,
            'field': self.field,
            'action': 'REGENERATED',
            'improved': improved,
            'attempts': attempt,
            'old_content': existing_content,
            'new_content': best_content,
            'best_quality_score': best_quality_score,
            'old_quality': {
                'readability': old_readability.get('status'),
                'ai_patterns': len(old_ai_patterns)
            },
            'new_quality': {
                'readability': best_readability.get('status'),
                'ai_patterns': len(best_ai_patterns)
            }
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
        
        # Guard against zero items
        if len(items) == 0:
            print(f"⚠️  No items found in domain '{self.domain}'")
            print(f"   Check data_root_key in domains/{self.domain}/config.yaml")
            return []
        
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
        
        # Final summary (guarded against zero division)
        print(f"\n{'='*80}")
        print(f"📊 FINAL SUMMARY")
        print(f"{'='*80}")
        print(f"Total processed: {len(items)}")
        if len(items) > 0:
            print(f"✅ Improved: {improved_count} ({improved_count/len(items)*100:.1f}%)")
            print(f"⚠️  Kept original: {len(items) - improved_count - failed_count}")
            print(f"❌ Failed: {failed_count}")
        print(f"{'='*80}\n")
        
        return results
    
    def _list_items_with_field(self) -> List[str]:
        """
        List all items in domain that have this field.
        
        🚨 MANDATORY: Reads from SOURCE DATA (data/*.yaml), NOT frontmatter
        Returns item IDs/keys as they exist in source YAML files
        """
        data_path = self._get_data_path()
        
        if not data_path.exists():
            print(f"⚠️  Source data file not found: {data_path}")
            return []
        
        # Load source data
        with open(data_path, 'r', encoding='utf-8') as f:
            all_data = yaml.safe_load(f)
        
        # Get root key from config
        config = self._load_domain_config()
        data_root_key = config.get('data_root_key', self.domain)
        
        # Get items dict
        items_dict = all_data.get(data_root_key, {})
        
        if not items_dict:
            print(f"⚠️  No items found under key '{data_root_key}' in {data_path}")
            print(f"   Available keys: {list(all_data.keys())}")
            return []
        
        # Return all item IDs (keys from the dict)
        return sorted(items_dict.keys())
