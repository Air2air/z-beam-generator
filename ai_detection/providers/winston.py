#!/usr/bin/env python3
"""
Winston.ai AI Detection Provider
"""

import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from ..service import AIDetectionConfig, AIDetectionError, AIDetectionResult

logger = logging.getLogger(__name__)


class WinstonProvider:
    """Winston.ai AI detection provider"""

    def __init__(self, config: AIDetectionConfig):
        self.config = config
        self.api_key = self._get_api_key()
        self.base_url = "https://api.gowinston.ai"
        self.session = requests.Session()

        if self.api_key:
            self.session.headers.update(
                {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "Z-Beam-Generator/1.0",
                }
            )

    def analyze_text(
        self, text: str, options: Optional[Dict] = None
    ) -> AIDetectionResult:
        """Analyze text for AI detection score

        Winston.ai scoring:
        - 0-100 scale where LOWER scores indicate MORE AI-like content
        - 0 = Definitely AI-generated
        - 100 = Definitely human-written
        - 30-70 = Unclear/uncertain
        """
        if not self.api_key:
            raise AIDetectionError("Winston.ai API key not configured")

        # Check minimum text length requirement
        # Import centralized AI detection config
        from ai_detection.config import AI_DETECTION_CONFIG

        if len(text.strip()) < AI_DETECTION_CONFIG["min_text_length_winston"]:
            logger.warning(
                f"Text too short for Winston.ai analysis: {len(text.strip())} characters (minimum {AI_DETECTION_CONFIG['min_text_length_winston']} required)"
            )
            # Return a neutral result for short text
            return AIDetectionResult(
                score=AI_DETECTION_CONFIG["fallback_score_error"],  # Neutral score
                confidence=0.5,
                classification="unclear",
                details={
                    "error": "Text too short for analysis",
                    "text_length": len(text.strip()),
                    "minimum_required": AI_DETECTION_CONFIG["min_text_length_winston"],
                },
                processing_time=0.0,
                provider="winston",
            )

        start_time = time.time()

        payload = {"text": text, "sentences": True}  # Get sentence-level scores

        # Add optional parameters
        if options:
            if "version" in options:
                payload["version"] = options["version"]
            if "language" in options:
                payload["language"] = options["language"]

        # API Terminal Messaging - Start
        print(f"🔍 [AI DETECTOR] Starting Winston.ai analysis...")
        print(f"📤 [AI DETECTOR] Sending text ({len(text)} chars) for AI detection")
        logger.info(
            f"🔍 [AI DETECTOR] Winston.ai API call initiated - Text length: {len(text)} chars"
        )

        try:
            response = self.session.post(
                f"{self.base_url}/v2/ai-content-detection",
                json=payload,
                timeout=min(
                    self.config.timeout, AI_DETECTION_CONFIG["winston_timeout_cap"]
                ),  # CAP timeout at configured seconds for faster response
            )

            # API Terminal Messaging - Response received
            print(
                f"📥 [AI DETECTOR] Received response from Winston.ai (Status: {response.status_code})"
            )

            if response.status_code == 200:
                data = response.json()

                # Winston.ai returns score as 0-100 (lower = more AI-like)
                ai_score = data.get("score", 0.0)

                # Determine classification based on score
                # Low scores (< 30) indicate AI-generated content
                # High scores (> 70) indicate human-written content
                if ai_score < 30:
                    classification = "ai"
                elif ai_score > 70:
                    classification = "human"
                else:
                    classification = "unclear"

                # Calculate confidence based on distance from the uncertain zone (around 50)
                # Higher confidence when score is closer to 0 (AI) or 100 (Human)
                if ai_score <= 50:
                    confidence = (
                        ai_score / 50
                    )  # 0-50 range: 0=low confidence, 50=high confidence
                else:
                    confidence = (
                        100 - ai_score
                    ) / 50  # 50-100 range: 50=high confidence, 100=low confidence
                confidence = min(confidence, 1.0)

                # API Terminal Messaging - Success
                processing_time = time.time() - start_time
                print(
                    f"✅ [AI DETECTOR] Analysis completed - Score: {ai_score:.1f}, Classification: {classification}"
                )
                print(f"⏱️ [AI DETECTOR] Processing time: {processing_time:.2f}s")
                logger.info(
                    f"✅ [AI DETECTOR] Winston.ai analysis successful - Score: {ai_score:.1f} ({classification})"
                )

                # Extract sentence-level details if available
                details = {
                    "input": data.get("input", text),
                    "readability_score": data.get("readability_score"),
                    "credits_used": data.get("credits_used", 0),
                    "credits_remaining": data.get("credits_remaining"),
                    "version": data.get("version"),
                    "language": data.get("language"),
                    "attack_detected": data.get("attack_detected", {}),
                }

                # OPTIMIZATION: Enhanced sentence-level analysis for better feedback
                if "sentences" in data and data["sentences"]:
                    details["sentences"] = data["sentences"]

                    # Add analysis of failing sentences
                    failing_sentences = [
                        s
                        for s in data["sentences"]
                        if isinstance(s, dict) and s.get("score", 100) < 30
                    ]
                    details["failing_sentences_count"] = len(failing_sentences)
                    details["failing_sentences_percentage"] = (
                        (len(failing_sentences) / len(data["sentences"])) * 100
                        if data["sentences"]
                        else 0
                    )

                    # Analyze patterns in failing sentences
                    if failing_sentences:
                        failing_texts = [s.get("text", "") for s in failing_sentences]
                        details["failing_patterns"] = self._analyze_failing_patterns(
                            failing_texts
                        )

                    logger.info(
                        f"📊 Sentence analysis: {len(failing_sentences)}/{len(data['sentences'])} failing sentences ({details['failing_sentences_percentage']:.1f}%)"
                    )

                return AIDetectionResult(
                    score=ai_score,
                    confidence=confidence,
                    classification=classification,
                    details=details,
                    processing_time=time.time() - start_time,
                    provider="winston",
                )
            elif response.status_code == 403:
                # Handle validation errors (like text too short)
                error_data = response.json()
                error_desc = error_data.get("description", "Validation failed")
                from utils.loud_errors import validation_failure

                validation_failure("winston_ai", error_desc, field="text_content")
                raise AIDetectionError(f"Winston.ai validation failed: {error_desc}")
            else:
                from utils.loud_errors import api_failure

                api_failure(
                    "winston_ai", f"API error {response.status_code}", retry_count=None
                )
                raise AIDetectionError(f"API error {response.status_code}")

        except requests.exceptions.Timeout:
            print("⏰ [AI DETECTOR] Winston.ai API request timeout")
            raise AIDetectionError("Winston.ai API request timeout")
        except requests.exceptions.RequestException as e:
            print(f"❌ [AI DETECTOR] Winston.ai API request failed: {e}")
            raise AIDetectionError(f"Winston.ai API request failed: {e}")
        except Exception as e:
            print(f"❌ [AI DETECTOR] Winston.ai analysis failed: {e}")
            logger.error(f"Winston.ai analysis failed: {e}")
            raise AIDetectionError(f"Analysis failed: {e}")

    def is_available(self) -> bool:
        """Check if Winston.ai service is available"""
        if not self.api_key:
            return False

        # API Terminal Messaging - Connectivity Test
        print("🔗 [AI DETECTOR] Testing Winston.ai service connectivity...")
        logger.info("🔗 [AI DETECTOR] Testing Winston.ai service availability")

        try:
            # Test with sufficient text length (minimum 300 characters)
            test_text = "This is a comprehensive test text that should definitely meet the minimum 300 character requirement for the Winston.ai API. We are testing the AI detection capabilities of this service to ensure it can properly analyze content and provide accurate scoring. The system should be able to detect whether this text was written by a human or generated by an AI language model. This is important for content quality assurance and ensuring the authenticity of generated materials in various applications including content generation, academic writing, and creative projects. The API should return a score between 0 and 100 indicating the likelihood of AI generation, with lower scores indicating more AI-like content and higher scores indicating human-written content. This test will help verify that the Winston.ai service is functioning correctly and can be relied upon for AI detection analysis."
            test_payload = {"text": test_text}

            print("📤 [AI DETECTOR] Sending connectivity test to Winston.ai...")
            response = self.session.post(
                f"{self.base_url}/v2/ai-content-detection",
                json=test_payload,
                timeout=10,
            )

            if response.status_code == 200:
                print("✅ [AI DETECTOR] Winston.ai service is available")
                logger.info("✅ [AI DETECTOR] Winston.ai service connectivity confirmed")
                return True
            else:
                print(
                    f"❌ [AI DETECTOR] Winston.ai service unavailable (Status: {response.status_code})"
                )
                logger.warning(
                    f"❌ [AI DETECTOR] Winston.ai service returned status {response.status_code}"
                )
                return False

        except Exception as e:
            print(f"❌ [AI DETECTOR] Winston.ai connectivity test failed: {e}")
            logger.error(f"❌ [AI DETECTOR] Winston.ai connectivity test failed: {e}")
            return False

    def _get_api_key(self) -> Optional[str]:
        """Get Winston.ai API key using standardized key manager"""
        from api.key_manager import get_api_key

        try:
            return get_api_key("winston")
        except ValueError:
            raise Exception(
                "Winston.ai API key not found in environment - no fallback to config file permitted in fail-fast architecture"
            )

    def _analyze_failing_patterns(self, failing_texts: list) -> Dict[str, Any]:
        """Analyze patterns in sentences that are failing AI detection."""
        if not failing_texts:
            return {}

        patterns = {
            "avg_length": sum(len(text.split()) for text in failing_texts)
            / len(failing_texts),
            "contains_repetition": any(
                "very" in text.lower() or "really" in text.lower()
                for text in failing_texts
            ),
            "uniform_structure": self._check_uniform_structure(failing_texts),
            "technical_density": sum(
                1 for text in failing_texts for word in text.split() if len(word) > 8
            )
            / sum(len(text.split()) for text in failing_texts)
            if failing_texts
            else 0,
        }

        return patterns

    def _check_uniform_structure(self, texts: list) -> bool:
        """Check if sentences have uniform structure (potential AI detection trigger)."""
        if len(texts) < 2:
            return False

        # Check for similar sentence starters
        starters = []
        for text in texts:
            words = text.strip().split()
            if words:
                starters.append(words[0].lower())

        # If more than 50% of sentences start with same word, consider uniform
        if starters:
            most_common = max(set(starters), key=starters.count)
            return (starters.count(most_common) / len(starters)) > 0.5

        return False
