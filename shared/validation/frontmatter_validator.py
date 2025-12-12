"""
Frontmatter Dependency Validation System for Z-Beam Generator

Validates frontmatter data integrity and prevents cascading failures
in the component generation pipeline. Ensures all required fields are
present before component generation begins.
"""

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ValidationResult:
    """Result of validation operation"""

    is_valid: bool
    message: str
    details: Optional[List[str]] = None
    warning: bool = False


@dataclass
class RiskAssessment:
    """Assessment of generation failure risk"""

    risk_level: str  # 'low', 'medium', 'high'
    recovery_options: List[str]


@dataclass
class HealthStatus:
    """Component health status"""

    status: str  # 'healthy', 'degraded', 'unhealthy', 'unknown'
    message: str


class FrontmatterDependencyValidator:
    """Validate frontmatter meets all component requirements"""

    def __init__(self):
        self.component_requirements = self._load_component_requirements()

    def _load_component_requirements(self) -> Dict[str, List[str]]:
        """Load requirements for each component"""
        return {
            "text": ["name", "category", "properties", "applications", "author"],
            "bullets": ["name", "category", "properties", "applications"],
            "micro": ["name", "category", "properties"],
            "table": ["name", "properties", "technicalSpecifications"],
            "frontmatter": ["name", "category", "formula", "properties"],
        }

    def validate_frontmatter_for_components(
        self, frontmatter_data: Dict, components: List[str]
    ) -> ValidationResult:
        """Validate frontmatter meets requirements for specified components"""
        if not frontmatter_data:
            return ValidationResult(False, "No frontmatter data provided")

        all_issues = []

        for component in components:
            requirements = self.component_requirements.get(component, [])
            component_issues = []

            for field in requirements:
                if field not in frontmatter_data:
                    component_issues.append(f"Missing {field} for {component}")
                    continue

                value = frontmatter_data[field]
                if not value:
                    component_issues.append(f"Empty {field} for {component}")
                    continue

                # Validate field-specific requirements
                if field in ["properties", "applications"] and len(value) == 0:
                    component_issues.append(f"Empty {field} list for {component}")

            if component_issues:
                all_issues.extend(component_issues)

        return ValidationResult(
            len(all_issues) == 0,
            "Frontmatter validation passed"
            if len(all_issues) == 0
            else f"Found {len(all_issues)} issues",
            all_issues,
        )

    def get_missing_fields_report(
        self, frontmatter_data: Dict, components: List[str]
    ) -> Dict[str, List[str]]:
        """Generate detailed report of missing fields by component"""
        report = {}

        for component in components:
            requirements = self.component_requirements.get(component, [])
            missing = []

            for field in requirements:
                if field not in frontmatter_data or not frontmatter_data[field]:
                    missing.append(field)

            if missing:
                report[component] = missing

        return report


class CascadingFailurePreventer:
    """Prevent cascading failures in component generation"""

    def __init__(self):
        self.failure_patterns = {}
        self.recovery_strategies = self._load_recovery_strategies()

    def _load_recovery_strategies(self) -> Dict[str, callable]:
        """Load recovery strategies for different failure types"""
        return {
            "missing_frontmatter": self._recover_missing_frontmatter,
            "incomplete_properties": self._recover_incomplete_properties,
            "invalid_category": self._recover_invalid_category,
        }

    def assess_generation_risk(
        self, frontmatter_data: Dict, components: List[str]
    ) -> RiskAssessment:
        """Assess risk of generation failure"""
        validator = FrontmatterDependencyValidator()
        validation = validator.validate_frontmatter_for_components(
            frontmatter_data, components
        )

        if validation.is_valid:
            return RiskAssessment("low", [])

        # Analyze failure patterns
        missing_report = validator.get_missing_fields_report(
            frontmatter_data, components
        )

        risk_level = self._calculate_risk_level(missing_report)
        recovery_options = self._identify_recovery_options(missing_report)

        return RiskAssessment(risk_level, recovery_options)

    def _calculate_risk_level(self, missing_report: Dict) -> str:
        """Calculate overall risk level"""
        total_missing = sum(len(fields) for fields in missing_report.values())

        if total_missing == 0:
            return "low"
        elif total_missing <= 2:
            return "medium"
        else:
            return "high"

    def _identify_recovery_options(self, missing_report: Dict) -> List[str]:
        """Identify possible recovery strategies"""
        options = []

        for component, missing_fields in missing_report.items():
            for field in missing_fields:
                strategy_key = f"missing_{field}"
                if strategy_key in self.recovery_strategies:
                    options.append(f"Recover {field} for {component}")

        return options

    def execute_recovery(self, frontmatter_data: Dict, recovery_option: str) -> Dict:
        """Execute selected recovery strategy"""
        # Parse recovery option
        if "properties" in recovery_option:
            return self._recover_incomplete_properties(frontmatter_data)
        elif "category" in recovery_option:
            return self._recover_invalid_category(frontmatter_data)

        return frontmatter_data

    def _recover_missing_frontmatter(self, frontmatter_data: Dict) -> Dict:
        """Recover from missing frontmatter"""
        # Provide minimal frontmatter structure
        return {
            "name": frontmatter_data.get("name", "Unknown Material"),
            "category": "material",
            "properties": {"type": "unknown"},
            "applications": ["general use"],
        }

    def _recover_incomplete_properties(self, frontmatter_data: Dict) -> Dict:
        """Recover from incomplete properties"""
                # Ensure materialProperties structure exists per frontmatter_template.yaml
        if "materialProperties" not in frontmatter_data:
            frontmatter_data["materialProperties"] = {
                "material_characteristics": {"label": "Material Characteristics"},
                "laser_material_interaction": {"label": "Laser-Material Interaction"}
            }

        # Add default properties to material_characteristics if needed
        defaults = {
            "density": {"value": "Unknown", "unit": "g/cm³"},
            "thermalConductivity": {"value": "Unknown", "unit": "W/(m·K)"},
        }

        mat_char = frontmatter_data["materialProperties"].get("material_characteristics", {})
        for key, value in defaults.items():
            if key not in mat_char or key in ['label', 'description', 'percentage']:
                mat_char[key] = value
        
        frontmatter_data["materialProperties"]["material_characteristics"] = mat_char
        return frontmatter_data

    def _recover_invalid_category(self, frontmatter_data: Dict) -> Dict:
        """Recover from invalid category"""
        valid_categories = ["metal", "ceramic", "polymer", "composite"]
        current_category = frontmatter_data.get("category", "").lower()

        if current_category not in valid_categories:
            frontmatter_data["category"] = "material"  # Safe default

        return frontmatter_data


class ComponentHealthMonitor:
    """Monitor component health and performance"""

    def __init__(self):
        self.component_metrics = {}
        self.performance_thresholds = {
            "generation_time": 30,  # seconds
            "success_rate": 0.95,  # 95%
            "error_rate": 0.05,  # 5%
        }

    def record_component_metric(
        self, component_type: str, metric_name: str, value: float
    ):
        """Record component performance metric"""
        if component_type not in self.component_metrics:
            self.component_metrics[component_type] = {}

        if metric_name not in self.component_metrics[component_type]:
            self.component_metrics[component_type][metric_name] = []

        metrics = self.component_metrics[component_type][metric_name]
        metrics.append((time.time(), value))

        # Keep only last 100 measurements
        if len(metrics) > 100:
            metrics.pop(0)

    def get_component_health(self, component_type: str) -> "HealthStatus":
        """Get component health status"""
        if component_type not in self.component_metrics:
            return HealthStatus("unknown", "No metrics available")

        metrics = self.component_metrics[component_type]

        # Calculate health indicators
        success_rate = self._calculate_success_rate(metrics)
        avg_generation_time = self._calculate_avg_generation_time(metrics)
        error_rate = 1 - success_rate

        # Determine health status
        if error_rate > self.performance_thresholds["error_rate"]:
            status = "unhealthy"
            message = f"High error rate: {error_rate:.1%}"
        elif avg_generation_time > self.performance_thresholds["generation_time"]:
            status = "degraded"
            message = f"Slow performance: {avg_generation_time:.1f}s"
        else:
            status = "healthy"
            message = "Component performing well"

        return HealthStatus(status, message)

    def _calculate_success_rate(self, metrics: Dict) -> float:
        """Calculate component success rate"""
        if "success" not in metrics:
            return 0.0

        successes = [v for t, v in metrics["success"] if v == 1.0]
        return len(successes) / len(metrics["success"]) if metrics["success"] else 0.0

    def _calculate_avg_generation_time(self, metrics: Dict) -> float:
        """Calculate average generation time"""
        if "generation_time" not in metrics:
            return 0.0

        times = [v for t, v in metrics["generation_time"]]
        return sum(times) / len(times) if times else 0.0
