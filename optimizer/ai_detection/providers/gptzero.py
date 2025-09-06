#!/usr/bin/env python3
"""
GPTZero AI Detection Provider
"""

import logging
import os
import time
from pathlib import Path
from typing import Dict, Optional

import requests

from ..service import AIDetectionConfig, AIDetectionError, AIDetectionResult

logger = logging.getLogger(__name__)


class GPTZeroProvider:
    """GPTZero AI detection provider"""

    def __init__(self, config: AIDetectionConfig):
        self.config = config
        self.api_key = self._get_api_key()
        self.base_url = "https://api.gptzero.me"
        self.session = requests.Session()

        if self.api_key:
            self.session.headers.update(
                {
                    "X-Api-Key": self.api_key,
                    "Content-Type": "application/json",
                    "User-Agent": "Z-Beam-Generator/1.0",
                }
            )

    def analyze_text(
        self, text: str, options: Optional[Dict] = None
    ) -> AIDetectionResult:
        """Analyze text for AI detection score"""
        if not self.api_key:
            raise AIDetectionError("GPTZero API key not configured")

        start_time = time.time()

        payload = {"document": text, "multilingual": False}

        if options:
            payload.update(options)

        try:
            response = self.session.post(
                f"{self.base_url}/v2/predict/text",
                json=payload,
                timeout=self.config.timeout,
            )

            if response.status_code == 200:
                data = response.json()

                # GPTZero returns different field structure
                # Extract the overall AI probability score
                ai_probability = data.get("documents", [{}])[0].get(
                    "average_generated_prob", 0.0
                )
                ai_score = ai_probability * 100  # Convert to 0-100 scale

                # Determine classification based on score
                if ai_score > 70:
                    classification = "ai"
                elif ai_score < 30:
                    classification = "human"
                else:
                    classification = "unclear"

                # Calculate confidence based on the score spread
                confidence = min(abs(ai_score - 50) / 50, 1.0)

                return AIDetectionResult(
                    score=ai_score,
                    confidence=confidence,
                    classification=classification,
                    details=data,
                    processing_time=time.time() - start_time,
                    provider="gptzero",
                )
            else:
                logger.error(
                    f"GPTZero API error: {response.status_code} - {response.text}"
                )
                raise AIDetectionError(f"API error {response.status_code}")

        except requests.exceptions.Timeout:
            raise AIDetectionError("GPTZero API request timeout")
        except requests.exceptions.RequestException as e:
            raise AIDetectionError(f"GPTZero API request failed: {e}")
        except Exception as e:
            logger.error(f"GPTZero analysis failed: {e}")
            raise AIDetectionError(f"Analysis failed: {e}")

    def is_available(self) -> bool:
        """Check if GPTZero service is available"""
        if not self.api_key:
            return False

        try:
            # Simple health check
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def _get_api_key(self) -> Optional[str]:
        """Get GPTZero API key from environment or config"""
        # Try environment variable first
        api_key = os.getenv("GPTZERO_API_KEY")

        # Fallback to config file
        if not api_key:
            raise Exception(
                "GPTZero API key not found in environment - no fallback to config file permitted in fail-fast architecture"
            )

        return api_key
