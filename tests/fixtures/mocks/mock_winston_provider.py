#!/usr/bin/env python3
"""
Mock Winston AI Detection Provider

Provides mock implementation of Winston.ai AI detection service for testing.
"""

import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from ai_detection.providers.winston import (
    AIDetectionError,
    AIDetectionResult:,
    Any],
    Dict[str,
    Exception,
    :,
    @dataclass,
    class,
    classification:,
    confidence:,
    details:,
    float,
    pass,
    processing_time:,
    provider:,
    score:,
    str,
)

    @dataclass
    class AIDetectionConfig:
        timeout: float = 15.0
        min_text_length: int = 300


class MockWinstonProvider:
    """Mock Winston.ai AI detection provider"""

    def __init__(self, config: Optional[AIDetectionConfig] = None):
        self.config = config or AIDetectionConfig()
        self.api_key = "mock_winston_key"
        self.call_count = 0
        self.base_url = "https://api.mock-winston.ai"

        # Mock response patterns based on content characteristics
        self.response_patterns = {
            "technical_content": {
                "score_range": (
                    20,
                    45,
                ),  # Technical content often scores lower (more human-like)
                "confidence": 0.85,
                "classification": "human",
            },
            "marketing_content": {
                "score_range": (
                    60,
                    85,
                ),  # Marketing content often scores higher (more AI-like)
                "confidence": 0.75,
                "classification": "unclear",
            },
            "creative_writing": {
                "score_range": (15, 35),  # Creative writing scores low
                "confidence": 0.90,
                "classification": "human",
            },
            "generic_content": {
                "score_range": (40, 70),  # Generic content in middle range
                "confidence": 0.65,
                "classification": "unclear",
            },
        }

    def analyze_text(
        self, text: str, options: Optional[Dict] = None
    ) -> AIDetectionResult:
        """Analyze text for AI detection score using mock Winston.ai

        Mock Winston.ai scoring:
        - 0-100 scale where LOWER scores indicate MORE human-like content
        - 0 = Definitely human-written
        - 100 = Definitely AI-generated
        - 30-70 = Unclear/uncertain
        """
        self.call_count += 1
        start_time = time.time()

        # Check minimum text length requirement
        min_length = getattr(self.config, "min_text_length_winston", 300)
        if len(text.strip()) < min_length:
            return AIDetectionResult(
                score=50.0,  # Neutral score
                confidence=0.5,
                classification="unclear",
                details={
                    "error": "Text too short for analysis",
                    "text_length": len(text.strip()),
                    "minimum_required": min_length,
                },
                processing_time=time.time() - start_time,
                provider="mock_winston",
            )

        # Simulate API processing delay
        processing_delay = 0.5 + random.random() * 1.5  # 0.5-2.0 seconds
        time.sleep(processing_delay)

        # Determine content type and generate appropriate score
        content_type = self._classify_content_type(text)
        pattern = self.response_patterns[content_type]

        # Generate score within the pattern's range
        score = random.uniform(pattern["score_range"][0], pattern["score_range"][1])

        # Determine classification based on score
        if score < 30:
            classification = "human"
        elif score > 70:
            classification = "ai"
        else:
            classification = "unclear"

        # Calculate confidence based on distance from uncertain zone
        if score <= 50:
            confidence = score / 50  # 0-50 range
        else:
            confidence = (100 - score) / 50  # 50-100 range
        confidence = min(confidence, 1.0) * pattern["confidence"]

        # Generate mock sentence-level analysis
        sentences = self._analyze_sentences(text)

        # Generate mock details
        details = {
            "input": text[:100] + "..." if len(text) > 100 else text,
            "readability_score": random.uniform(60, 90),
            "credits_used": random.randint(1, 3),
            "credits_remaining": random.randint(95, 100),
            "version": "2.1.0",
            "language": "en",
            "attack_detected": self._generate_attack_detection(),
            "sentences": sentences,
        }

        return AIDetectionResult(
            score=round(score, 1),
            confidence=round(confidence, 2),
            classification=classification,
            details=details,
            processing_time=time.time() - start_time,
            provider="mock_winston",
        )

    def _classify_content_type(self, text: str) -> str:
        """Classify content type based on text characteristics"""
        text_lower = text.lower()

        # Technical content indicators
        technical_indicators = [
            "laser",
            "cleaning",
            "process",
            "material",
            "properties",
            "thermal",
            "conductivity",
            "wavelength",
            "parameters",
            "industrial",
            "manufacturing",
            "applications",
            "specifications",
        ]

        # Marketing content indicators
        marketing_indicators = [
            "amazing",
            "revolutionary",
            "best",
            "superior",
            "excellent",
            "innovative",
            "cutting-edge",
            "advanced",
            "powerful",
            "effective",
        ]

        # Creative writing indicators
        creative_indicators = [
            "once upon a time",
            "the story",
            "character",
            "narrative",
            "emotion",
            "feeling",
            "beautiful",
            "wonderful",
            "mysterious",
        ]

        technical_score = sum(
            1 for indicator in technical_indicators if indicator in text_lower
        )
        marketing_score = sum(
            1 for indicator in marketing_indicators if indicator in text_lower
        )
        creative_score = sum(
            1 for indicator in creative_indicators if indicator in text_lower
        )

        max_score = max(technical_score, marketing_score, creative_score)

        if max_score == 0:
            return "generic_content"
        elif technical_score == max_score:
            return "technical_content"
        elif marketing_score == max_score:
            return "marketing_content"
        else:
            return "creative_writing"

    def _analyze_sentences(self, text: str) -> list:
        """Generate mock sentence-level analysis"""
        sentences = []
        words = text.split()

        # Split text into mock sentences (roughly every 15-25 words)
        current_sentence = []
        for i, word in enumerate(words):
            current_sentence.append(word)
            if len(current_sentence) >= random.randint(15, 25) or i == len(words) - 1:
                sentence_text = " ".join(current_sentence)
                if (
                    len(sentence_text.strip()) > 10
                ):  # Only analyze substantial sentences
                    sentences.append(
                        {
                            "text": sentence_text,
                            "score": round(random.uniform(20, 80), 1),
                            "confidence": round(random.uniform(0.6, 0.95), 2),
                        }
                    )
                current_sentence = []

        return sentences[:10]  # Limit to first 10 sentences

    def _generate_attack_detection(self) -> Dict:
        """Generate mock attack detection results"""
        attack_types = [
            "paraphrasing",
            "synonym_replacement",
            "sentence_restructuring",
            "content_obfuscation",
            "formatting_manipulation",
        ]

        # 80% chance of no attack detected
        if random.random() < 0.8:
            return {"detected": False}

        return {
            "detected": True,
            "type": random.choice(attack_types),
            "confidence": round(random.uniform(0.7, 0.95), 2),
            "description": f"Detected potential {random.choice(attack_types)} manipulation",
        }

    def is_available(self) -> bool:
        """Check if mock Winston service is available"""
        # Mock service is always available
        return True

    def get_call_count(self) -> int:
        """Get the number of API calls made"""
        return self.call_count

    def reset_call_count(self):
        """Reset the call count"""
        self.call_count = 0


# Global mock instance for easy access in tests
_mock_winston_provider = None


def get_mock_winston_provider(
    config: Optional[AIDetectionConfig] = None,
) -> MockWinstonProvider:
    """Get or create mock Winston provider instance"""
    global _mock_winston_provider
    if _mock_winston_provider is None:
        _mock_winston_provider = MockWinstonProvider(config)
    return _mock_winston_provider


def create_mock_winston_provider(**kwargs) -> MockWinstonProvider:
    """Create a new mock Winston provider with custom configuration"""
    config = AIDetectionConfig(**kwargs)
    return MockWinstonProvider(config)


if __name__ == "__main__":
    # Test the mock Winston provider
    provider = MockWinstonProvider()

    # Test with technical content
    test_text = """
    Laser cleaning technology represents a cutting-edge approach to surface preparation and contamination removal.
    This non-contact method utilizes focused laser energy to vaporize unwanted materials from substrate surfaces.
    The process offers significant advantages over traditional cleaning methods, including precision control,
    environmental friendliness, and suitability for automation in industrial applications.
    """

    print("🧪 Testing Mock Winston Provider")
    print("=" * 50)

    result = provider.analyze_text(test_text)

    print(f"📊 Score: {result.score}")
    print(f"🎯 Confidence: {result.confidence}")
    print(f"🏷️  Classification: {result.classification}")
    print(f"⏱️  Processing Time: {result.processing_time:.2f}s")
    print(f"📝 Sentences Analyzed: {len(result.details.get('sentences', []))}")
    print(f"💰 Credits Used: {result.details.get('credits_used', 0)}")
    print(
        f"🔍 Attack Detected: {result.details.get('attack_detected', {}).get('detected', False)}"
    )

    print("\n✅ Mock Winston provider test completed!")
