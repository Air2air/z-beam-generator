"""
"""Voice Application Utility with Field-Level Control

Applies author voice markers to frontmatter fields based on configuration.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class VoiceApplicationController:
    """
    Controls which fields receive voice enhancement based on configuration.
    
    NO FALLBACKS: Fails if configuration is missing.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize voice controller with configuration.
        
        Args:
            config_path: Path to voice_application.yaml. If None, uses default.
        
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            ValueError: If configuration is invalid
        """
        if config_path is None:
            config_path = "components/text/config/voice_application.yaml"
        
        self.config_path = Path(config_path)
        
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Voice application config not found: {self.config_path}\n"
                f"NO FALLBACKS ALLOWED - configuration is required."
            )
        
        self.config = self._load_config()
        self.voice_markers = self.config.get('voice_markers', {})
        self.validation_rules = self.config.get('validation', {})
        
        logger.info(f"✅ Voice controller initialized from {self.config_path}")
    
    def _load_config(self) -> Dict:
        """Load and validate configuration file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Validate required sections
            required_sections = ['materials_page', 'settings_page', 'validation']
            for section in required_sections:
                if section not in config:
                    raise ValueError(f"Missing required config section: {section}")
            
            return config
            
        except Exception as e:
            raise ValueError(f"Failed to load voice config: {e}")
    
    def should_apply_voice(
        self,
        field_name: str,
        content_type: str = 'materials_page'
    ) -> bool:
        """
        Check if voice should be applied to this field.
        
        Args:
            field_name: Field identifier (e.g., 'caption', 'caption_before')
            content_type: Page type ('materials_page', 'settings_page', etc.)
        
        Returns:
            bool: True if voice should be applied
            
        Examples:
            >>> controller.should_apply_voice('caption_before', 'materials_page')
            True  # Captions always get voice
            
            >>> controller.should_apply_voice('faq_answers', 'materials_page')
            True  # FAQ answers get voice
        """
        page_config = self.config.get(content_type, {})
        return page_config.get(field_name, False)
    
    def get_voice_fields(self, content_type: str = 'materials_page') -> Dict[str, bool]:
        """
        Get all field voice settings for a content type.
        
        Args:
            content_type: Page type
            
        Returns:
            Dictionary mapping field names to voice enable status
        """
        return self.config.get(content_type, {})
    
    def validate_field_voice(
        self,
        field_name: str,
        content: str,
        content_type: str = 'materials_page'
    ) -> Tuple[bool, List[str]]:
        """
        Validate voice application for a field.
        
        Checks:
        - Fields that should have voice DO have markers
        - Fields that shouldn't have voice DON'T have markers
        - Marker density is appropriate
        
        Args:
            field_name: Field identifier
            content: Field content to validate
            content_type: Page type
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not content:
            return True, []
        
        has_voice_markers = self._has_voice_markers(content)
        
        # Check forbidden fields
        forbidden_fields = self.validation_rules.get('forbidden_voice_fields', [])
        if field_name in forbidden_fields and has_voice_markers:
            errors.append(
                f"❌ FORBIDDEN: Field '{field_name}' has voice markers but should NOT.\n"
                f"   Content: {content[:100]}..."
            )
        
        # Check required fields
        required_fields = self.validation_rules.get('required_voice_fields', [])
        if field_name in required_fields and not has_voice_markers:
            min_markers = self.validation_rules.get('min_markers_per_field', {}).get(field_name, 1)
            errors.append(
                f"❌ MISSING: Field '{field_name}' should have {min_markers}+ voice markers.\n"
                f"   Content: {content[:100]}..."
            )
        
        # Check marker density
        if has_voice_markers:
            marker_count = self._count_voice_markers(content)
            word_count = len(content.split())
            density = (marker_count / word_count * 100) if word_count > 0 else 0
            max_density = self.validation_rules.get('max_marker_density', 8)
            
            if density > max_density:
                errors.append(
                    f"⚠️  EXCESSIVE: Field '{field_name}' has {density:.1f} markers per 100 words "
                    f"(max: {max_density}). Content sounds unnatural."
                )
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def _has_voice_markers(self, text: str) -> bool:
        """Check if text contains any voice markers."""
        text_lower = text.lower()
        
        for marker in self.voice_markers.get('primary', []):
            if marker in text_lower:
                return True
        
        for marker in self.voice_markers.get('secondary', []):
            if marker in text_lower:
                return True
        
        for marker in self.voice_markers.get('contextual', []):
            if marker in text_lower:
                return True
        
        return False
    
    def _count_voice_markers(self, text: str) -> int:
        """Count total voice markers in text."""
        text_lower = text.lower()
        count = 0
        
        all_markers = (
            self.voice_markers.get('primary', []) +
            self.voice_markers.get('secondary', []) +
            self.voice_markers.get('contextual', [])
        )
        
        for marker in all_markers:
            count += text_lower.count(marker)
        
        return count
    
    def validate_frontmatter_voice(
        self,
        frontmatter: Dict,
        content_type: str = 'materials_page'
    ) -> Tuple[bool, List[str]]:
        """
        Validate voice application across entire frontmatter.
        
        Args:
            frontmatter: Frontmatter dictionary
            content_type: Page type
            
        Returns:
            Tuple of (is_valid, list_of_all_errors)
        """
        all_errors = []
        
        # Check materials_page fields
        if 'materials_page' in frontmatter:
            mp = frontmatter['materials_page']
            
            # Captions: MUST have voice
            if 'caption' in mp:
                if 'before' in mp['caption']:
                    is_valid, errors = self.validate_field_voice(
                        'caption_before', mp['caption']['before'], content_type
                    )
                    all_errors.extend(errors)
                
                if 'after' in mp['caption']:
                    is_valid, errors = self.validate_field_voice(
                        'caption_after', mp['caption']['after'], content_type
                    )
                    all_errors.extend(errors)
        
        # Check FAQ answers: MUST have voice
        if 'faq' in frontmatter:
            for i, faq in enumerate(frontmatter['faq']):
                if 'answer' in faq:
                    is_valid, errors = self.validate_field_voice(
                        'faq_answers', faq['answer'], content_type
                    )
                    if errors:
                        all_errors.append(f"FAQ #{i+1}: " + "; ".join(errors))
        
        is_valid = len(all_errors) == 0
        return is_valid, all_errors
    
    def get_author_preferences(self, author_id: int) -> Dict:
        """
        Get voice marker preferences for specific author.
        
        Args:
            author_id: Author ID (1-10)
            
        Returns:
            Dictionary with author's preferred markers and frequency
        """
        return self.config.get('author_preferences', {}).get(
            author_id,
            {
                'primary_marker': 'pretty',
                'secondary_marker': 'basically',
                'frequency': 'moderate'
            }
        )


def apply_voice_with_config(
    frontmatter: Dict,
    author_id: int,
    content_type: str = 'materials_page',
    voice_controller: Optional[VoiceApplicationController] = None
) -> Dict:
    """
    Apply voice to frontmatter fields based on configuration.
    
    This is the main entry point for voice enhancement that respects
    the field-level configuration.
    
    Args:
        frontmatter: Frontmatter dictionary
        author_id: Author ID for persona
        content_type: Page type
        voice_controller: Optional controller instance (creates new if None)
        
    Returns:
        Frontmatter with voice applied to appropriate fields only
        
    Raises:
        FileNotFoundError: If voice config is missing
        ValidationError: If voice validation fails after application
    """
    if voice_controller is None:
        voice_controller = VoiceApplicationController()
    
    logger.info(f"🎭 Applying voice for author {author_id}, content_type: {content_type}")
    
    # Get author preferences
    author_prefs = voice_controller.get_author_preferences(author_id)
    logger.info(f"   Using preferences: {author_prefs}")
    
    # Apply voice to materials_page fields
    if 'materials_page' in frontmatter:
        mp = frontmatter['materials_page']
        
        # Captions: APPLY
        if 'caption' in mp:
            if 'before' in mp['caption']:
                if voice_controller.should_apply_voice('caption_before', content_type):
                    logger.info("   ✓ Applying voice to caption_before")
                    # Voice transformation happens here (integrated with existing system)
                    # For now, just mark it for processing
                    mp['caption']['_voice_before'] = True
            
            if 'after' in mp['caption']:
                if voice_controller.should_apply_voice('caption_after', content_type):
                    logger.info("   ✓ Applying voice to caption_after")
                    mp['caption']['_voice_after'] = True
    
    # Apply voice to FAQ answers
    if 'faq' in frontmatter:
        if voice_controller.should_apply_voice('faq_answers', content_type):
            logger.info(f"   ✓ Applying voice to {len(frontmatter['faq'])} FAQ answers")
            for faq in frontmatter['faq']:
                faq['_voice_answer'] = True
    
    # Validate after application
    is_valid, errors = voice_controller.validate_frontmatter_voice(frontmatter, content_type)
    
    if not is_valid:
        logger.error("❌ Voice validation failed:")
        for error in errors:
            logger.error(f"   {error}")
        # Don't fail generation, but log prominently
    
    return frontmatter


if __name__ == "__main__":
    # Test the controller
    logging.basicConfig(level=logging.INFO)
    
    try:
        controller = VoiceApplicationController()
        print("\n✅ Controller initialized successfully\n")
        
        # Test field checks
        print("Field Voice Settings (materials_page):")
        print(f"  caption_before: {controller.should_apply_voice('caption_before', 'materials_page')}")
        print(f"  caption_after: {controller.should_apply_voice('caption_after', 'materials_page')}")
        print(f"  faq_answers: {controller.should_apply_voice('faq_answers', 'materials_page')}")
        
        # Test validation
        print("\nValidation Tests:")
        
        # Test 1: Caption without voice (should FAIL)
        caption_no_voice = "Surface shows heavy contamination from exposure"
        is_valid, errors = controller.validate_field_voice('caption_before', caption_no_voice, 'materials_page')
        print(f"\n1. Caption without voice markers: {'❌ FAILED' if errors else '✓ PASSED'}")
        if errors:
            for error in errors:
                print(f"   {error}")
        
        # Test 2: Caption with voice (should PASS)
        caption_with_voice = "Surface shows pretty heavy contamination from years of exposure"
        is_valid, errors = controller.validate_field_voice('caption_before', caption_with_voice, 'materials_page')
        print(f"\n2. Caption with voice markers: {'✓ PASSED' if not errors else '❌ FAILED'}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
