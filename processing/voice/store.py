"""
Author Voice Storage and Retrieval

Manages ESL author profiles with country-specific linguistic traits.
"""

import logging
from pathlib import Path
from typing import Dict, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)


class AuthorVoiceStore:
    """
    Centralized storage for author voice profiles.
    
    Loads from existing voice profiles or creates from author data.
    """
    
    def __init__(self, profile_dir: Optional[Path] = None):
        """
        Initialize voice store.
        
        Args:
            profile_dir: Directory containing voice profiles (default: processing/voice/profiles)
        """
        if profile_dir is None:
            profile_dir = Path(__file__).parent / "profiles"
        
        self.profile_dir = Path(profile_dir)
        self._profiles = {}
        self._load_profiles()
    
    def _load_profiles(self):
        """Load all YAML profiles from directory"""
        if not self.profile_dir.exists():
            logger.warning(f"Profile directory not found: {self.profile_dir}")
            return
        
        import yaml
        for profile_file in self.profile_dir.glob("*.yaml"):
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    profile = yaml.safe_load(f)
                    country = profile_file.stem  # taiwan, italy, indonesia, united_states
                    self._profiles[country] = profile
                    logger.info(f"Loaded voice profile: {country}")
            except Exception as e:
                logger.error(f"Failed to load profile {profile_file}: {e}")
    
    @lru_cache(maxsize=10)
    def get_voice(self, author_id: int) -> Dict:
        """
        Get voice profile for author.
        
        Args:
            author_id: Author ID (1-4)
            
        Returns:
            Voice profile dict with country, linguistic traits, etc.
        """
        # Map author IDs to countries (from existing author system)
        author_map = {
            1: "united_states",
            2: "italy", 
            3: "indonesia",
            4: "taiwan"
        }
        
        country = author_map.get(author_id, "united_states")
        profile = self._profiles.get(country, {})
        
        if not profile:
            logger.warning(f"No profile found for author {author_id} (country: {country})")
            return {
                'country': country,
                'name': f'Author {author_id}',
                'linguistic_characteristics': {},
                'signature_phrases': []
            }
        
        return profile
    
    def get_esl_traits(self, author_id: int) -> str:
        """
        Extract ESL traits as formatted string for prompts.
        
        Args:
            author_id: Author ID
            
        Returns:
            Formatted ESL traits string
        """
        profile = self.get_voice(author_id)
        linguistic = profile.get('linguistic_characteristics', {})
        
        # Extract key ESL patterns
        patterns = []
        
        sentence_structure = linguistic.get('sentence_structure', {})
        if 'patterns' in sentence_structure:
            patterns.extend(sentence_structure['patterns'][:3])
        
        vocab = linguistic.get('vocabulary_patterns', {})
        if 'preferred_terms' in vocab:
            terms = vocab['preferred_terms']
            if isinstance(terms, dict):
                for category, words in list(terms.items())[:2]:
                    if isinstance(words, list):
                        patterns.append(f"{category}: {', '.join(words[:3])}")
        
        return "; ".join(patterns) if patterns else "Natural English with subtle regional patterns"
