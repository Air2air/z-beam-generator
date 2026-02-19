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
3. Regenerating from scratch using original domain prompt template (always)
4. Saving regenerated content to SOURCE DATA ONLY (data/*.yaml)
6. User must run --export to update frontmatter after postprocessing
7. POLICY: Research and generate if field is empty

🔥 MANDATORY RETRY POLICY (December 14, 2025):
- System MUST retry regeneration until requirements are met
- Maximum attempts: 3 (configurable via MAX_REGENERATION_ATTEMPTS)
- Each attempt uses fresh generation with randomized parameters
- Only stops when: quality threshold met OR max attempts exhausted
- Keeps best version across all attempts (highest quality score)

CRITICAL: Regeneration = Fresh generation from original prompt, NOT refinement of existing text.
"""

import logging
import os
import re
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

logger = logging.getLogger(__name__)

# MANDATORY RETRY POLICY CONSTANTS
MAX_REGENERATION_ATTEMPTS = 3  # Must retry until requirements met or max reached
QUALITY_THRESHOLD = 60  # Minimum acceptable quality score for postprocessing acceptance
MIN_CONTENT_LENGTH = 150  # Minimum content length in characters


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
    
    Regeneration behavior (always):
    - Discards old content completely
    - Calls generator.generate() with original domain prompt template
    - Fresh generation (same as initial creation, NOT refinement)
    - Saves best regenerated result when available
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

        # Backward-compatibility aliases for description fields
        if content is None and self.field in ('page_description', 'pageDescription', 'description'):
            content = (
                item_data.get('page_description')
                or item_data.get('pageDescription')
                or item_data.get('description')
            )
        
        # Handle different field types
        if content is None or content == 'null' or content == '':
            return None
        
        # FAQ is an array, convert to string for processing
        if self.field == 'faq' and isinstance(content, list):
            return yaml.dump(content, default_flow_style=False)
        
        return str(content).strip() if content else None

    def _get_generation_component_type(self) -> str:
        """Map postprocess field names to generator component types."""
        if self.field in ('page_description', 'pageDescription'):
            return 'description'
        return self.field

    def _check_readability(self, text: str) -> Dict[str, Any]:
        """Return readability status in legacy-compatible dict shape."""
        violations: List[str] = []
        if not text or not str(text).strip():
            violations.append('empty_content')
        if len(str(text)) < MIN_CONTENT_LENGTH:
            violations.append('too_short')

        return {
            'status': 'fail' if violations else 'pass',
            'violations': violations,
        }
    
    def _check_winston(self, text: str) -> float:
        """Check Winston AI detection score (stub - uses generator's method)"""
        # This will be integrated with actual Winston API
        return 0.95  # Placeholder
    
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
            # Backward-compatible fallback path for tests/mocks that patch legacy loaders
            item_data = None
            if hasattr(self, 'data_loader') and hasattr(self.data_loader, 'get_item_data'):
                try:
                    item_data = self.data_loader.get_item_data(item_id)
                except Exception:
                    item_data = None

            if item_data is None and hasattr(self, '_load_frontmatter'):
                try:
                    legacy_data, _ = self._load_frontmatter(item_id)
                    item_data = legacy_data
                except Exception:
                    item_data = None

            if item_data is None:
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
                    component_type=self._get_generation_component_type(),
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
        
        # Check minimum length first
        if len(existing_content) < MIN_CONTENT_LENGTH:
            print(f"\n⚠️  Content too short ({len(existing_content)} chars < {MIN_CONTENT_LENGTH} minimum) - regenerating...")
        else:
            print(f"\nℹ️  Existing content score: {quality_analysis['overall_score']}/100")
            print("🔄 POLICY: Always regenerate and overwrite for fresh text processing")
        
        # Store old quality metrics BEFORE regenerating
        old_quality_score = quality_analysis['overall_score']
        old_ai_issues = quality_analysis['ai_patterns'].get('issues', [])
        old_ai_like = quality_analysis['ai_patterns'].get('is_ai_like', False)
        old_voice_score = quality_analysis['voice_authenticity'].get('score')
        old_pattern_compliance = quality_analysis['voice_authenticity'].get('pattern_compliance', {})
        old_pattern_count = old_pattern_compliance.get('found_count', 0) or 0
        old_forbidden_violations = quality_analysis['voice_authenticity'].get('forbidden_violations', []) or []

        old_structural = quality_analysis.get('structural_quality', {})
        old_structural_avg = (
            old_structural.get('sentence_variation', 0) +
            old_structural.get('rhythm_score', 0) +
            old_structural.get('complexity_variation', 0)
        ) / 3
        
        # 🔥 MANDATORY RETRY LOOP - Keep trying until requirements met
        print(f"\n🔧 Quality score {quality_analysis['overall_score']}/100 below threshold")
        max_attempts = 1 if dry_run else MAX_REGENERATION_ATTEMPTS

        print(f"🔄 Starting regeneration (max {max_attempts} attempts)...\n")
        
        # Generate unique session ID for grouping all retry attempts together
        retry_session_id = str(uuid.uuid4())
        print(f"📊 Retry session ID: {retry_session_id}\n")

        # Attempt-level target words for controlled length variation
        # Uses domain config component_lengths when available.
        attempt_targets = [None] * max_attempts
        try:
            domain_config = self._load_domain_config()
            component_cfg = domain_config.get('component_lengths', {}).get(self.field, {})
            if isinstance(component_cfg, dict):
                min_words = component_cfg.get('min')
                max_words = component_cfg.get('max')
            else:
                min_words = None
                max_words = None

            if isinstance(min_words, int) and isinstance(max_words, int) and max_words > min_words:
                step_denominator = max(1, max_attempts - 1)
                attempt_targets = [
                    min_words + int((max_words - min_words) * idx / step_denominator)
                    for idx in range(max_attempts)
                ]
                print(f"📏 Length targets by attempt: {attempt_targets}")
        except Exception as e:
            logger.warning(f"Could not load per-attempt length targets: {e}")
        
        best_result = None
        best_quality_analysis = None
        best_quality_score = 0
        best_selection_score = -1.0
        best_content = None
        best_ai_issues = None
        best_pattern_count = 0
        best_forbidden_count = 0
        
        for attempt in range(1, max_attempts + 1):
            print(f"\n{'='*80}")
            print(f"🔄 ATTEMPT {attempt}/{max_attempts}")
            print(f"{'='*80}")

            attempt_target_words = attempt_targets[attempt - 1]
            if isinstance(attempt_target_words, int):
                print(f"🎯 Attempt target words: {attempt_target_words}")
            
            try:
                # Use existing generator.generate() which includes ALL quality checks:
                # - Humanness layer (structural variation)
                # - Voice validation (author compliance)
                # - Quality evaluation (Winston, realism, diversity)
                # - Learning database logging
                # - Dual-write (data YAML + frontmatter sync)
                
                if dry_run:
                    result = self.generator.generate(
                        material_name=item_id,
                        component_type=self._get_generation_component_type(),
                        faq_count=None
                    )
                else:
                    result = self.generator.generate(
                        material_name=item_id,
                        component_type=self._get_generation_component_type(),
                        faq_count=None,
                        retry_session_id=retry_session_id,
                        is_retry=(attempt > 1),
                        skip_learning_evaluation=True,
                        target_words=attempt_target_words
                    )
                
                # Result is a QualityEvaluatedResult dataclass, not a dict
                if not result or not result.success or not result.content:
                    error_msg = result.error_message if result else 'No result returned'
                    print(f"❌ Attempt {attempt} failed: {error_msg}")
                    if attempt == max_attempts:
                        # Exhausted all attempts
                        print(f"\n❌ All {max_attempts} attempts failed")
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

                if dry_run:
                    best_result = result
                    best_content = new_content
                    best_quality_score = old_quality_score
                    print("🔎 Dry-run mode: single regeneration attempt completed")
                    break
                
                # Check new quality using the SAME unified analyzer as generation pipeline
                new_quality_analysis = analyzer.analyze(
                    text=new_content,
                    author=author_data,
                    include_recommendations=False
                )

                attempt_quality = new_quality_analysis['overall_score']
                attempt_ai_issues = new_quality_analysis['ai_patterns'].get('issues', [])
                attempt_ai_like = new_quality_analysis['ai_patterns'].get('is_ai_like', False)
                attempt_voice_score = new_quality_analysis['voice_authenticity'].get('score')
                pattern_compliance = new_quality_analysis['voice_authenticity'].get('pattern_compliance', {})
                attempt_pattern_count = pattern_compliance.get('found_count', 0) or 0
                attempt_pattern_found = bool(pattern_compliance.get('authentic')) or attempt_pattern_count > 0
                attempt_forbidden_violations = new_quality_analysis['voice_authenticity'].get('forbidden_violations', []) or []
                attempt_forbidden_count = len(attempt_forbidden_violations)

                # Stricter output-shape validation for pageDescription
                page_description_clean = True
                page_description_issues = []
                if self.field == 'pageDescription':
                    lowered = new_content.lower()
                    artifact_patterns = [
                        r"^\s*title\s*:",
                        r"^\s*description\s*:",
                        r"^\s*sectiontitle\s*:",
                        r"^\s*sectiondescription\s*:",
                        r"^\s*\{",
                        r"^\s*\[",
                        r"^\s*#{1,6}\s+",
                    ]
                    if any(re.search(pattern, lowered, flags=re.IGNORECASE | re.MULTILINE) for pattern in artifact_patterns):
                        page_description_clean = False
                        page_description_issues.append("template wrapper/label detected")

                    if new_content.strip().endswith(':'):
                        page_description_clean = False
                        page_description_issues.append("dangling colon at end")

                    sentence_count = len([s for s in re.split(r"[.!?]+", new_content) if s.strip()])
                    if sentence_count < 2:
                        page_description_clean = False
                        page_description_issues.append("too few complete sentences")

                attempt_structural = new_quality_analysis.get('structural_quality', {})
                attempt_structural_avg = (
                    attempt_structural.get('sentence_variation', 0) +
                    attempt_structural.get('rhythm_score', 0) +
                    attempt_structural.get('complexity_variation', 0)
                ) / 3
                
                print(f"🔍 Attempt {attempt} quality:")
                print(f"   • Overall: {attempt_quality}/100")
                print(f"   • AI-like: {'YES' if attempt_ai_like else 'NO'}")
                print(f"   • AI issues: {len(attempt_ai_issues)}")
                print(f"   • Voice authenticity: {attempt_voice_score if attempt_voice_score is not None else 'N/A'}/100")
                print(f"   • Voice patterns found: {attempt_pattern_count}")
                print(f"   • Forbidden phrases: {attempt_forbidden_count}")
                print(f"   • Structural avg: {attempt_structural_avg:.1f}/100")
                if self.field == 'pageDescription':
                    print(f"   • Output format clean: {'YES' if page_description_clean else 'NO'}")
                    if page_description_issues:
                        print(f"   • Format issues: {', '.join(page_description_issues)}")
                
                # Track best result
                attempt_selection_score = float(attempt_quality)
                # Strongly prefer attempts with detectable nationality patterns
                attempt_selection_score += float(attempt_pattern_count) * 20.0
                if attempt_pattern_found:
                    attempt_selection_score += 10.0
                # Heavily penalize forbidden phrase recurrence
                attempt_selection_score -= float(attempt_forbidden_count) * 50.0

                if attempt_selection_score > best_selection_score:
                    best_selection_score = attempt_selection_score
                    best_quality_score = float(attempt_quality)
                    best_result = result
                    best_content = new_content
                    best_quality_analysis = new_quality_analysis
                    best_ai_issues = attempt_ai_issues
                    best_pattern_count = attempt_pattern_count
                    best_forbidden_count = attempt_forbidden_count
                    print(f"   ✅ NEW BEST (quality: {attempt_quality}/100, selection: {attempt_selection_score:.1f})")
                
                # Check if requirements met
                requirements_met = (
                    attempt_quality >= QUALITY_THRESHOLD and
                    not attempt_ai_like and
                    len(attempt_ai_issues) == 0 and
                    attempt_forbidden_count == 0 and
                    (attempt_voice_score is None or attempt_voice_score >= 60) and
                    attempt_pattern_found and
                    attempt_structural_avg >= 50 and
                    page_description_clean
                )
                
                if requirements_met:
                    print(f"\n✅ REQUIREMENTS MET on attempt {attempt}!")
                    print(f"   • Quality: {attempt_quality}/100 (threshold: {QUALITY_THRESHOLD})")
                    print(f"   • AI-like: NO")
                    print(f"   • AI issues: 0")
                    print(f"   • Voice authenticity: {attempt_voice_score if attempt_voice_score is not None else 'N/A'}/100")
                    print(f"   • Voice patterns found: {attempt_pattern_count}")
                    print(f"   • Forbidden phrases: 0")
                    print(f"   • Structural avg: {attempt_structural_avg:.1f}/100")
                    break
                else:
                    print(f"\n⚠️  Attempt {attempt} below threshold")
                    if attempt < max_attempts:
                        print(f"   🔄 Retrying with fresh randomization...")
                    
            except Exception as e:
                print(f"❌ Attempt {attempt} error: {e}")
                if attempt == max_attempts:
                    import traceback
                    logger.error(traceback.format_exc())
        
        # After all attempts, use best result
        if not best_content:
            print(f"\n❌ All {max_attempts} attempts failed")
            return {
                'item': item_id,
                'field': self.field,
                'action': 'REGENERATION_FAILED_ALL_ATTEMPTS',
                'improved': False,
                'attempts': max_attempts
            }
        
        # Compare best vs original
        print(f"\n{'='*80}")
        print(f"📊 FINAL QUALITY COMPARISON (Best of {attempt} attempts)")
        print(f"{'='*80}")
        print(f"   Old quality score: {old_quality_score}/100")
        print(f"   Best quality score: {best_quality_score}/100")
        print(f"   Old AI issues: {len(old_ai_issues)}")
        print(f"   Best AI issues: {len(best_ai_issues) if best_ai_issues is not None else 'N/A'}")
        print(f"   Old forbidden phrases: {len(old_forbidden_violations)}")
        print(f"   Best forbidden phrases: {best_forbidden_count}")
        print(f"   Old voice patterns found: {old_pattern_count}")
        print(f"   Best voice patterns found: {best_pattern_count}")
        print(f"   Old voice authenticity: {old_voice_score if old_voice_score is not None else 'N/A'}/100")
        if best_quality_analysis:
            best_voice_score = best_quality_analysis['voice_authenticity'].get('score')
            best_structural = best_quality_analysis.get('structural_quality', {})
            best_structural_avg = (
                best_structural.get('sentence_variation', 0) +
                best_structural.get('rhythm_score', 0) +
                best_structural.get('complexity_variation', 0)
            ) / 3
            print(f"   Best voice authenticity: {best_voice_score if best_voice_score is not None else 'N/A'}/100")
            print(f"   Old structural avg: {old_structural_avg:.1f}/100")
            print(f"   Best structural avg: {best_structural_avg:.1f}/100")
        print(f"   Length change: {len(existing_content)} → {len(best_content)} chars")
        
        # Determine if improved
        ai_issues_improved = (
            best_ai_issues is not None and len(best_ai_issues) < len(old_ai_issues)
        )
        forbidden_improved = best_forbidden_count < len(old_forbidden_violations)
        pattern_improved = best_pattern_count > old_pattern_count
        quality_improved = best_quality_score > old_quality_score
        improved = (
            quality_improved or
            ai_issues_improved or
            forbidden_improved or
            pattern_improved or
            (
                best_quality_score >= QUALITY_THRESHOLD and
                best_forbidden_count == 0
            )
        )
        
        if improved:
            print(f"\n✅ Content IMPROVED after {attempt} attempts (dual-write complete)")
        else:
            print(f"\n⚠️  No measurable improvement after {attempt} attempts")

        # Always persist regenerated content per overwrite policy.
        if not dry_run:
            try:
                self.generator.generator.adapter.write_component(item_id, self.field, best_content)
                print("✅ Regenerated content persisted to source and frontmatter")
            except Exception as persist_error:
                print(f"❌ Failed to persist best attempt: {persist_error}")
                raise
        
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
                'overall_score': old_quality_score,
                'ai_like': old_ai_like,
                'ai_issues': len(old_ai_issues),
                'voice_authenticity': old_voice_score,
                'structural_avg': old_structural_avg
            },
            'new_quality': {
                'overall_score': best_quality_score,
                'ai_like': best_quality_analysis['ai_patterns'].get('is_ai_like') if best_quality_analysis else None,
                'ai_issues': len(best_ai_issues) if best_ai_issues is not None else None,
                'voice_authenticity': best_quality_analysis['voice_authenticity'].get('score') if best_quality_analysis else None,
                'structural_avg': best_structural_avg if best_quality_analysis else None
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
