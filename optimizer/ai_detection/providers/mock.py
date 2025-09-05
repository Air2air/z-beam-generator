#!/usr/bin/env python3
"""
Mock AI Detection Provider for Testing
"""

import time
import random
import logging
from typing import Dict, Optional

from ..service import AIDetectionResult, AIDetectionConfig

logger = logging.getLogger(__name__)

class MockProvider:
    """Mock AI detection provider for testing"""

    def __init__(self, config: AIDetectionConfig):
        self.config = config
        self._available = True
        logger.info("Mock AI detection provider initialized")

    def analyze_text(self, text: str, options: Optional[Dict] = None) -> AIDetectionResult:
        """Mock analysis - returns random but realistic results"""
        start_time = time.time()

        # Simulate API delay
        time.sleep(random.uniform(0.1, 0.5))

        # Generate mock results
        ai_score = random.uniform(10, 90)  # Random score between 10-90

        if ai_score > 70:
            classification = "ai"
        elif ai_score < 30:
            classification = "human"
        else:
            classification = "unclear"

        confidence = random.uniform(0.7, 0.95)

        # Mock API response structure
        mock_details = {
            "documents": [{
                "average_generated_prob": ai_score / 100,
                "completely_generated_prob": ai_score / 100 + random.uniform(-0.1, 0.1),
                "sentences": [
                    {
                        "sentence": "Mock sentence analysis",
                        "generated_prob": ai_score / 100
                    }
                ]
            }],
            "mock": True,
            "processing_time": time.time() - start_time
        }

        return AIDetectionResult(
            score=ai_score,
            confidence=confidence,
            classification=classification,
            details=mock_details,
            processing_time=time.time() - start_time,
            provider="mock"
        )

    def is_available(self) -> bool:
        """Mock provider is always available"""
        return self._available

    def set_available(self, available: bool):
        """Set availability for testing"""
        self._available = available
