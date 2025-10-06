#!/usr/bin/env python3
"""
Voice Orchestrator - Central API for Voice Management

Provides unified interface for retrieving country-specific voice instructions
for all text-based content generation components.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from functools import lru_cache


class VoiceOrchestrator:
    """
    Orchestrates voice instructions for content generation components.
    
    Manages country-specific linguistic patterns and propagates consistent
    voice across all text-based components.
    """
    
    # Country name normalization
    COUNTRY_MAP = {
        "taiwan": "taiwan",
        "italy": "italy",
        "indonesia": "indonesia",
        "united states": "united_states",
        "united states (california)": "united_states",
        "usa": "united_states",
        "us": "united_states",
    }
    
    def __init__(self, country: str):
        """
        Initialize voice orchestrator for specific country.
        
        Args:
            country: Author's country (e.g., "Taiwan", "Italy", "Indonesia", "United States")
        
        Raises:
            ValueError: If country is invalid or profile not found
        """
        self.country_raw = country
        self.country = self._normalize_country(country)
        self.profile = self._load_profile()
        self.base_voice = self._load_base_voice()
    
    def _normalize_country(self, country: str) -> str:
        """Normalize country name to profile filename"""
        country_lower = country.lower().strip()
        
        if country_lower not in self.COUNTRY_MAP:
            raise ValueError(
                f"Unsupported country '{country}'. "
                f"Supported: Taiwan, Italy, Indonesia, United States. "
                f"Fail-fast architecture requires valid country profiles."
            )
        
        return self.COUNTRY_MAP[country_lower]
    
    @lru_cache(maxsize=10)
    def _load_profile(self) -> Dict[str, Any]:
        """
        Load country-specific voice profile.
        
        Returns:
            Voice profile dictionary
        
        Raises:
            FileNotFoundError: If profile file doesn't exist
            ValueError: If profile is invalid
        """
        profile_path = Path(__file__).parent / "profiles" / f"{self.country}.yaml"
        
        if not profile_path.exists():
            raise FileNotFoundError(
                f"Voice profile not found: {profile_path}. "
                f"Fail-fast architecture requires complete voice profiles."
            )
        
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile = yaml.safe_load(f)
        
        # Validate profile structure
        required_keys = [
            "name", "author", "country", "linguistic_characteristics",
            "voice_adaptation", "signature_phrases"
        ]
        
        for key in required_keys:
            if key not in profile:
                raise ValueError(
                    f"Invalid voice profile for {self.country}: missing '{key}'. "
                    f"Fail-fast architecture requires complete profiles."
                )
        
        return profile
    
    @lru_cache(maxsize=5)
    def _load_base_voice(self) -> Dict[str, Any]:
        """Load shared base voice characteristics"""
        base_path = Path(__file__).parent / "base" / "voice_base.yaml"
        
        if not base_path.exists():
            # Base voice is optional - country profiles can stand alone
            return {}
        
        with open(base_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get_voice_for_component(
        self, 
        component_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get voice instructions for specific component type.
        
        Args:
            component_type: Type of component (caption, text, tags, etc.)
            context: Optional context (material, technical_level, etc.)
        
        Returns:
            Complete voice instructions as formatted string
        """
        context = context or {}
        
        # Get component-specific adaptations
        adaptation = self.profile.get("voice_adaptation", {}).get(component_type, {})
        
        # Build voice instructions
        instructions = self._build_voice_instructions(
            adaptation=adaptation,
            context=context
        )
        
        return instructions
    
    def _build_voice_instructions(
        self,
        adaptation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """
        Build complete voice instructions from profile and context.
        
        Args:
            adaptation: Component-specific adaptation settings
            context: Generation context
        
        Returns:
            Formatted voice instructions string
        """
        linguistic = self.profile.get("linguistic_characteristics", {})
        
        # Build instruction sections
        sections = []
        
        # 1. Role and Authority
        sections.append(self._build_role_section(adaptation))
        
        # 2. Linguistic Patterns
        sections.append(self._build_linguistic_section(linguistic))
        
        # 3. Voice Characteristics
        sections.append(self._build_voice_characteristics_section(linguistic))
        
        # 4. Component-Specific Guidelines
        if adaptation:
            sections.append(self._build_adaptation_section(adaptation))
        
        # 5. Signature Phrases
        sections.append(self._build_signature_phrases_section())
        
        return "\n\n".join(filter(None, sections))
    
    def _build_role_section(self, adaptation: Dict[str, Any]) -> str:
        """Build role and authority section"""
        author = self.profile.get("author", "Technical Expert")
        country = self.profile.get("country", self.country_raw)
        
        focus = adaptation.get("focus", "technical analysis")
        style = adaptation.get("style", "professional communication")
        
        return f"""VOICE ROLE:
You are {author} from {country}, communicating technical expertise with authentic voice.

Focus: {focus}
Style: {style}
Authority: Technical expert with country-specific communication patterns"""
    
    def _build_linguistic_section(self, linguistic: Dict[str, Any]) -> str:
        """Build linguistic patterns section"""
        sentence = linguistic.get("sentence_structure", {})
        vocab = linguistic.get("vocabulary_patterns", {})
        grammar = linguistic.get("grammar_characteristics", {})
        
        patterns = sentence.get("patterns", [])
        tendencies = sentence.get("tendencies", [])
        natural_vars = sentence.get("natural_variations", [])
        
        sections = ["LINGUISTIC PATTERNS:"]
        
        if patterns:
            sections.append("\nSentence Structure Examples:")
            for pattern in patterns[:3]:
                sections.append(f"  - {pattern}")
        
        if tendencies:
            sections.append("\nCommunication Tendencies:")
            for tendency in tendencies:
                sections.append(f"  - {tendency}")
        
        if natural_vars:
            sections.append("\nNatural Variations (authentic patterns):")
            for var in natural_vars:
                sections.append(f"  - {var}")
        
        # Vocabulary preferences
        if vocab:
            preferred = vocab.get("preferred_terms", {})
            if preferred:
                sections.append("\nPreferred Vocabulary:")
                for category, terms in preferred.items():
                    if isinstance(terms, list) and terms:
                        sections.append(f"  {category.title()}: {', '.join(terms[:4])}")
        
        return "\n".join(sections)
    
    def _build_voice_characteristics_section(self, linguistic: Dict[str, Any]) -> str:
        """Build voice characteristics section"""
        cultural = linguistic.get("cultural_communication", {})
        
        if not cultural:
            return ""
        
        tone = cultural.get("tone", "professional")
        emphasis = cultural.get("emphasis_style", "technical accuracy")
        perspective = cultural.get("perspective", "expert analysis")
        
        return f"""VOICE CHARACTERISTICS:
Tone: {tone}
Emphasis: {emphasis}
Perspective: {perspective}"""
    
    def _build_adaptation_section(self, adaptation: Dict[str, Any]) -> str:
        """Build component-specific adaptation section"""
        if not adaptation:
            return ""
        
        word_limit = adaptation.get("word_limit")
        focus = adaptation.get("focus")
        style = adaptation.get("style")
        
        sections = ["COMPONENT-SPECIFIC GUIDELINES:"]
        
        if word_limit:
            sections.append(f"Word Limit: {word_limit} words")
        if focus:
            sections.append(f"Content Focus: {focus}")
        if style:
            sections.append(f"Writing Style: {style}")
        
        return "\n".join(sections)
    
    def _build_signature_phrases_section(self) -> str:
        """Build signature phrases section"""
        phrases = self.profile.get("signature_phrases", [])
        
        if not phrases:
            return ""
        
        return f"""SIGNATURE EXPRESSIONS:
Consider incorporating these natural expressions when appropriate:
{chr(10).join(f'  - "{phrase}"' for phrase in phrases[:5])}"""
    
    def get_word_limit(self) -> int:
        """
        Get word limit for this country's voice.
        
        Returns:
            Word limit as integer
        """
        # Try to get from any component adaptation
        adaptations = self.profile.get("voice_adaptation", {})
        
        for component in ["caption", "text", "description"]:
            if component in adaptations:
                limit = adaptations[component].get("word_limit")
                if limit:
                    return int(limit)
        
        # Default limits by country
        defaults = {
            "taiwan": 380,
            "italy": 450,
            "indonesia": 250,
            "united_states": 320
        }
        
        return defaults.get(self.country, 300)
    
    def get_quality_thresholds(self) -> Dict[str, float]:
        """
        Get quality thresholds for this voice profile.
        
        Returns:
            Dictionary of threshold values
        """
        return self.profile.get("quality_thresholds", {
            "formality_minimum": 70,
            "technical_accuracy_minimum": 85,
            "linguistic_authenticity_minimum": 70
        })
    
    def get_signature_phrases(self) -> list:
        """Get list of signature phrases for this country"""
        return self.profile.get("signature_phrases", [])
    
    def get_profile_summary(self) -> Dict[str, Any]:
        """
        Get summary of voice profile.
        
        Returns:
            Dictionary with key profile information
        """
        linguistic = self.profile.get("linguistic_characteristics", {})
        cultural = linguistic.get("cultural_communication", {})
        
        return {
            "country": self.profile.get("country"),
            "author": self.profile.get("author"),
            "word_limit": self.get_word_limit(),
            "tone": cultural.get("tone", "professional"),
            "formality": self.profile.get("vocabulary_patterns", {}).get("formality_level", "professional"),
            "signature_phrases_count": len(self.profile.get("signature_phrases", [])),
            "supported_components": list(self.profile.get("voice_adaptation", {}).keys())
        }


# Convenience function for quick access
def get_voice_instructions(country: str, component_type: str, context: Optional[Dict] = None) -> str:
    """
    Quick access function to get voice instructions.
    
    Args:
        country: Author's country
        component_type: Component type (caption, text, tags)
        context: Optional context dictionary
    
    Returns:
        Voice instructions string
    """
    orchestrator = VoiceOrchestrator(country=country)
    return orchestrator.get_voice_for_component(component_type, context)


if __name__ == "__main__":
    # Test voice orchestrator
    print("🎭 Voice Orchestrator Test\n" + "=" * 60)
    
    for country in ["Taiwan", "Italy", "Indonesia", "United States"]:
        try:
            voice = VoiceOrchestrator(country=country)
            summary = voice.get_profile_summary()
            
            print(f"\n{country}:")
            print(f"  Author: {summary['author']}")
            print(f"  Word Limit: {summary['word_limit']}")
            print(f"  Tone: {summary['tone']}")
            print(f"  Formality: {summary['formality']}")
            print(f"  Signature Phrases: {summary['signature_phrases_count']}")
            
        except Exception as e:
            print(f"\n{country}: ❌ {e}")
