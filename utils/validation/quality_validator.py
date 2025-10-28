"""
AI Detection Circuit Breaker for Z-Beam Generator

⚠️  DEPRECATED - Use validation/content_validator.py instead
This module is maintained for backward compatibility only.
New code should use validation.content_validator.ContentValidationService

Migration Guide:
- QualityScoreValidator → ContentValidationService (validation/content_validator.py)
- AIDetectionCircuitBreaker → Use retry logic in api/client.py
- Persona thresholds → PERSONA_THRESHOLDS in validation/content_validator.py

See: docs/CONTENT_VALIDATION_SYSTEM.md for migration details

---

Legacy Implementation:
Implements circuit breaker pattern for AI detection services to ensure
resilient quality assurance. Supports Winston.ai primary with GPTZero fallback.
"""

import time
import warnings
from dataclasses import dataclass
from typing import Dict, List, Optional

# Issue deprecation warning on import
warnings.warn(
    "utils.validation.quality_validator is deprecated. "
    "Use validation.content_validator.ContentValidationService instead. "
    "See docs/CONTENT_VALIDATION_SYSTEM.md for migration guide.",
    DeprecationWarning,
    stacklevel=2
)


@dataclass
class ValidationResult:
    """Result of validation operation"""

    is_valid: bool
    message: str
    details: Optional[List[str]] = None
    warning: bool = False


@dataclass
class QualityScoreResult:
    """Result of quality score validation"""

    is_valid: bool
    score: float
    message: str
    recommendations: List[str]


class AIDetectionCircuitBreaker:
    """Circuit breaker for AI detection services"""

    def __init__(self):
        self.service_failures = {"winston": 0, "gptzero": 0}
        self.failure_threshold = 5
        
        # Get timeout configuration from run.py - FAIL FAST if unavailable
        from run import get_validation_config
        validation_config = get_validation_config()
        self.recovery_timeout = validation_config["quality_validator_recovery_timeout"]
        self.fallback_chain = ["winston", "gptzero"]

    def get_available_service(self) -> Optional[str]:
        """Get next available AI detection service"""
        for service in self.fallback_chain:
            if self._can_use_service(service):
                return service
        return None

    def _can_use_service(self, service: str) -> bool:
        """Check if service can be used"""
        if self.service_failures[service] >= self.failure_threshold:
            # Check recovery timeout
            if hasattr(self, f"{service}_failure_time"):
                failure_time = getattr(self, f"{service}_failure_time")
                if time.time() - failure_time > self.recovery_timeout:
                    self.service_failures[service] = 0
                    return True
            return False
        return True

    def record_service_failure(self, service: str):
        """Record service failure"""
        self.service_failures[service] += 1
        setattr(self, f"{service}_failure_time", time.time())

    def record_service_success(self, service: str):
        """Record service success"""
        if self.service_failures[service] > 0:
            self.service_failures[service] = max(0, self.service_failures[service] - 1)


class QualityScoreValidator:
    """Validate quality scores meet persona requirements"""

    def __init__(self):
        self.persona_thresholds = {
            1: {"min_score": 70, "target_score": 80},  # Taiwan - precision
            2: {"min_score": 75, "target_score": 85},  # Italy - expressiveness
            3: {"min_score": 65, "target_score": 75},  # Indonesia - accessibility
            4: {"min_score": 72, "target_score": 82},  # USA - innovation
        }

    def validate_quality_score(self, score: float, author_id: int) -> ValidationResult:
        """Validate quality score meets persona requirements"""
        thresholds = self.persona_thresholds.get(author_id)
        if not thresholds:
            return ValidationResult(False, f"No thresholds for author {author_id}")

        if score < thresholds["min_score"]:
            return ValidationResult(
                False,
                f"Score {score} below minimum {thresholds['min_score']} for author {author_id}",
            )

        if score < thresholds["target_score"]:
            return ValidationResult(
                True,
                f"Score {score} meets minimum but below target {thresholds['target_score']}",
                warning=True,
            )

        return ValidationResult(True, f"Score {score} meets all requirements")

    def get_score_recommendations(self, score: float, author_id: int) -> List[str]:
        """Get recommendations for improving score"""
        recommendations = []

        thresholds = self.persona_thresholds.get(author_id, {})
        target_score = thresholds.get("target_score", 80)

        if score < target_score:
            gap = target_score - score

            if gap > 10:
                recommendations.append(
                    "Major persona drift detected - consider regeneration"
                )
            elif gap > 5:
                recommendations.append(
                    "Moderate improvements needed in persona adherence"
                )
            else:
                recommendations.append(
                    "Minor adjustments recommended for optimal quality"
                )

            # Persona-specific recommendations
            if author_id == 1:  # Taiwan
                recommendations.append(
                    "Strengthen systematic approach and technical precision"
                )
            elif author_id == 2:  # Italy
                recommendations.append(
                    "Enhance expressive language and engineering passion"
                )
            elif author_id == 3:  # Indonesia
                recommendations.append(
                    "Improve analytical clarity and balanced presentation"
                )
            elif author_id == 4:  # USA
                recommendations.append(
                    "Boost innovative language and conversational tone"
                )

        return recommendations


class ComponentFactoryCircuitBreaker:
    """Circuit breaker for component factory operations"""

    def __init__(self):
        self.component_failures = {}
        self.failure_threshold = 3
        
        # Get timeout configuration from run.py - FAIL FAST if unavailable
        from run import get_validation_config
        validation_config = get_validation_config()
        self.recovery_timeout = validation_config["quality_validator_short_timeout"]

    def can_create_component(self, component_type: str) -> bool:
        """Check if component can be created"""
        if component_type not in self.component_failures:
            return True

        failures = self.component_failures[component_type]
        if failures >= self.failure_threshold:
            # Check recovery timeout
            if hasattr(self, f"{component_type}_failure_time"):
                failure_time = getattr(self, f"{component_type}_failure_time")
                if time.time() - failure_time > self.recovery_timeout:
                    # Reset failures
                    self.component_failures[component_type] = 0
                    return True
            return False

        return True

    def record_component_failure(self, component_type: str):
        """Record component creation failure"""
        if component_type not in self.component_failures:
            self.component_failures[component_type] = 0

        self.component_failures[component_type] += 1
        setattr(self, f"{component_type}_failure_time", time.time())

    def record_component_success(self, component_type: str):
        """Record component creation success"""
        if component_type in self.component_failures:
            self.component_failures[component_type] = max(
                0, self.component_failures[component_type] - 1
            )
