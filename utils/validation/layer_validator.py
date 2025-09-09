"""
Layer Validation System for Z-Beam Generator

Validates the integrity of the three-layer architecture:
- Base Layer: Technical content requirements
- Persona Layer: Author characteristics and cultural authenticity
- Formatting Layer: Cultural presentation standards

Ensures fail-fast validation while preserving architectural integrity.
"""

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class ValidationResult:
    """Result of validation operation"""

    is_valid: bool
    message: str
    details: Optional[List[str]] = None
    warning: bool = False


@dataclass
class DriftReport:
    """Report of persona drift detection"""

    is_authentic: bool
    issues: List[str]


@dataclass
class HealthStatus:
    """Component health status"""

    status: str  # 'healthy', 'degraded', 'unhealthy', 'unknown'
    message: str


class LayerValidator:
    """Validate three-layer architecture integrity"""

    def __init__(self):
        self.config_cache = {}
        self.cache_timeout = 300  # 5 minutes

    def validate_base_layer(self, base_config: Dict) -> ValidationResult:
        """Validate base content prompt structure"""
        required_sections = [
            "overall_subject",
            "author_expertise_areas",
            "author_configurations",
            "content_structure",
        ]

        missing = [s for s in required_sections if s not in base_config]
        if missing:
            return ValidationResult(False, f"Missing base sections: {missing}")

        # Validate author configurations
        authors = base_config.get("author_configurations", {})
        for author_id in [1, 2, 3, 4]:  # Taiwan, Italy, Indonesia, USA
            if str(author_id) not in authors:
                return ValidationResult(False, f"Missing author {author_id} config")

            author_config = authors[str(author_id)]
            if "max_word_count" not in author_config:
                return ValidationResult(
                    False, f"Missing word limit for author {author_id}"
                )

        return ValidationResult(True, "Base layer validation passed")

    def validate_persona_layer(
        self, persona_config: Dict, author_id: int
    ) -> ValidationResult:
        """Validate persona configuration structure"""
        required_fields = [
            "author_id",
            "name",
            "country",
            "writing_style",
            "language_patterns",
            "technical_focus",
        ]

        missing = [f for f in required_fields if f not in persona_config]
        if missing:
            return ValidationResult(False, f"Missing persona fields: {missing}")

        # Validate author ID consistency
        if persona_config.get("author_id") != author_id:
            return ValidationResult(
                False,
                f"Author ID mismatch: expected {author_id}, got {persona_config.get('author_id')}",
            )

        return ValidationResult(True, "Persona layer validation passed")

    def validate_formatting_layer(self, formatting_config: Dict) -> ValidationResult:
        """Validate formatting configuration structure"""
        required_fields = ["markdown_formatting", "content_structure"]

        missing = [f for f in required_fields if f not in formatting_config]
        if missing:
            return ValidationResult(False, f"Missing formatting fields: {missing}")

        # Validate markdown formatting structure
        md_format = formatting_config.get("markdown_formatting", {})
        if "headers" not in md_format or "emphasis" not in md_format:
            return ValidationResult(
                False, "Incomplete markdown formatting configuration"
            )

        return ValidationResult(True, "Formatting layer validation passed")

    def validate_three_layer_integrity(
        self, base_path: str, persona_path: str, formatting_path: str, author_id: int
    ) -> ValidationResult:
        """Validate complete three-layer integrity"""
        issues = []

        # Validate base layer
        base_config = self._load_config(base_path)
        if not base_config:
            issues.append("Failed to load base configuration")
        else:
            base_result = self.validate_base_layer(base_config)
            if not base_result.is_valid:
                issues.append(f"Base layer: {base_result.message}")

        # Validate persona layer
        persona_config = self._load_config(persona_path)
        if not persona_config:
            issues.append("Failed to load persona configuration")
        else:
            persona_result = self.validate_persona_layer(persona_config, author_id)
            if not persona_result.is_valid:
                issues.append(f"Persona layer: {persona_result.message}")

        # Validate formatting layer
        formatting_config = self._load_config(formatting_path)
        if not formatting_config:
            issues.append("Failed to load formatting configuration")
        else:
            formatting_result = self.validate_formatting_layer(formatting_config)
            if not formatting_result.is_valid:
                issues.append(f"Formatting layer: {formatting_result.message}")

        if issues:
            return ValidationResult(False, "Three-layer validation failed", issues)

        return ValidationResult(True, "Three-layer integrity validated")

    def _load_config(self, config_path: str) -> Optional[Dict]:
        """Load configuration with caching"""
        cache_key = config_path
        current_time = time.time()

        # Check cache
        if cache_key in self.config_cache:
            cached_time, cached_config = self.config_cache[cache_key]
            if current_time - cached_time < self.cache_timeout:
                return cached_config

        # Load from file
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                self.config_cache[cache_key] = (current_time, config)
                return config
        except Exception as e:
            print(f"Failed to load config {config_path}: {e}")
            return None


class PersonaDriftDetector:
    """Detect and prevent persona characteristic drift"""

    def __init__(self):
        self.persona_baselines = self._load_persona_baselines()

    def _load_persona_baselines(self) -> Dict[int, Dict]:
        """Load baseline persona characteristics"""
        return {
            1: {  # Taiwan - Yi-Chun Lin
                "word_range": (300, 400),
                "signature_phrases": ["systematic approach", "methodical analysis"],
                "technical_focus": "semiconductor processing",
                "linguistic_markers": ["precise", "systematic", "methodical"],
            },
            2: {  # Italy - Alessandro Moretti
                "word_range": (400, 500),
                "signature_phrases": [
                    "engineering excellence",
                    "heritage preservation",
                ],
                "technical_focus": "aerospace applications",
                "linguistic_markers": ["passionate", "innovative", "expressive"],
            },
            3: {  # Indonesia - Ikmanda Roswati
                "word_range": (200, 280),
                "signature_phrases": ["renewable energy", "marine applications"],
                "technical_focus": "sustainable technologies",
                "linguistic_markers": ["analytical", "balanced", "accessible"],
            },
            4: {  # USA - Todd Dunning
                "word_range": (280, 350),
                "signature_phrases": ["Silicon Valley", "biomedical devices"],
                "technical_focus": "emerging technologies",
                "linguistic_markers": ["conversational", "optimistic", "innovative"],
            },
        }

    def detect_persona_drift(self, content: str, author_id: int) -> DriftReport:
        """Detect if content deviates from persona baseline"""
        baseline = self.persona_baselines.get(author_id)
        if not baseline:
            return DriftReport(False, [f"Unknown author ID: {author_id}"])

        issues = []

        # Check word count
        word_count = len(content.split())
        if not (baseline["word_range"][0] <= word_count <= baseline["word_range"][1]):
            issues.append(
                f"Word count {word_count} outside range {baseline['word_range']}"
            )

        # Check signature phrases
        signature_found = any(
            phrase.lower() in content.lower()
            for phrase in baseline["signature_phrases"]
        )
        if not signature_found:
            issues.append("Missing signature phrases")

        # Check linguistic markers
        markers_found = sum(
            1
            for marker in baseline["linguistic_markers"]
            if marker.lower() in content.lower()
        )
        if markers_found < len(baseline["linguistic_markers"]) * 0.5:
            issues.append("Insufficient linguistic markers")

        return DriftReport(len(issues) == 0, issues)


class CulturalFormattingValidator:
    """Validate cultural authenticity in formatting"""

    def validate_country_formatting(
        self, content: str, country: str
    ) -> ValidationResult:
        """Validate formatting matches cultural expectations"""
        validators = {
            "Taiwan": self._validate_taiwan_formatting,
            "Italy": self._validate_italy_formatting,
            "Indonesia": self._validate_indonesia_formatting,
            "USA": self._validate_usa_formatting,
        }

        validator = validators.get(country)
        if not validator:
            return ValidationResult(False, f"No validator for country: {country}")

        return validator(content)

    def _validate_taiwan_formatting(self, content: str) -> ValidationResult:
        """Validate Taiwan academic precision formatting"""
        issues = []

        # Check for systematic section organization
        if "## " not in content:
            issues.append("Missing hierarchical section structure")

        # Check for precise technical formatting
        if "**" not in content and "*" not in content:
            issues.append("Missing technical term emphasis")

        return ValidationResult(
            len(issues) == 0, issues or ["Taiwan formatting validated"]
        )

    def _validate_italy_formatting(self, content: str) -> ValidationResult:
        """Validate Italy engineering precision formatting"""
        issues = []

        # Check for detailed bullet structures
        bullet_count = content.count("•") + content.count("- ")
        if bullet_count < 3:
            issues.append("Insufficient detailed bullet points")

        return ValidationResult(
            len(issues) == 0, issues or ["Italy formatting validated"]
        )

    def _validate_indonesia_formatting(self, content: str) -> ValidationResult:
        """Validate Indonesia accessible clarity formatting"""
        issues = []

        # Check for readable paragraph structure
        paragraphs = content.split("\n\n")
        if len(paragraphs) < 5:
            issues.append("Insufficient paragraph breaks for accessibility")

        return ValidationResult(
            len(issues) == 0, issues or ["Indonesia formatting validated"]
        )

    def _validate_usa_formatting(self, content: str) -> ValidationResult:
        """Validate USA modern business formatting"""
        issues = []

        # Check for action-oriented language
        action_words = ["optimize", "enhance", "improve", "achieve"]
        action_found = any(word in content.lower() for word in action_words)
        if not action_found:
            issues.append("Missing action-oriented language")

        return ValidationResult(
            len(issues) == 0, issues or ["USA formatting validated"]
        )


class LayerCircuitBreaker:
    """Circuit breaker for three-layer dependencies"""

    def __init__(self):
        self.layer_failures = {"base": 0, "persona": 0, "formatting": 0}
        self.failure_threshold = 3
        self.recovery_timeout = 300  # 5 minutes

    def can_proceed_with_layer(self, layer_name: str) -> bool:
        """Check if layer can be used"""
        if self.layer_failures[layer_name] >= self.failure_threshold:
            # Check if recovery timeout has passed
            if hasattr(self, f"{layer_name}_failure_time"):
                failure_time = getattr(self, f"{layer_name}_failure_time")
                if time.time() - failure_time > self.recovery_timeout:
                    # Attempt recovery
                    self.layer_failures[layer_name] = 0
                    return True
            return False
        return True

    def record_layer_failure(self, layer_name: str):
        """Record layer failure"""
        self.layer_failures[layer_name] += 1
        setattr(self, f"{layer_name}_failure_time", time.time())

    def record_layer_success(self, layer_name: str):
        """Record layer success"""
        if self.layer_failures[layer_name] > 0:
            self.layer_failures[layer_name] = max(
                0, self.layer_failures[layer_name] - 1
            )
