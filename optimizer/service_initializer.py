#!/usr/bin/env python3
"""
Service Initializer for Z-Beam Optimizer

This module provides centralized service initialization and registration
for all optimizer components.
"""

import logging
from typing import Any, Dict, Optional

from optimizer.services import ServiceConfiguration
from optimizer.services.ai_detection_optimization import AIDetectionOptimizationService
from optimizer.services.iterative_workflow.service import IterativeWorkflowService
from optimizer.services.service_registry import service_registry

logger = logging.getLogger(__name__)


class ServiceInitializer:
    """Centralized service initializer and registry manager."""

    def __init__(self):
        self.services = {}
        self.initialized = False

    def initialize_all_services(self) -> Dict[str, Any]:
        """
        Initialize and register all optimizer services.

        Returns:
            Dict[str, Any]: Initialization results
        """
        results = {
            "success": True,
            "services_initialized": [],
            "services_failed": [],
            "errors": [],
        }

        try:
            # Initialize AI Detection Optimization Service
            ai_config = ServiceConfiguration(
                name="ai_detection_service",
                version="1.0.0",
                enabled=True,
                settings={
                    "providers": {
                        "winston": {
                            "type": "winston",
                            "enabled": True,
                            "target_score": 70.0,
                            "max_iterations": 5,
                        }
                    },
                    "target_score": 70.0,
                    "max_iterations": 5,
                    "improvement_threshold": 3.0,
                    "cache_ttl_hours": 1,
                    "max_workers": 4,
                    "detection_threshold": 0.7,
                    "confidence_threshold": 0.8,
                    "allow_mocks_for_testing": True,  # Allow for testing
                },
            )

            try:
                ai_service = AIDetectionOptimizationService(ai_config)
                service_registry.register_service(ai_service)
                self.services["ai_detection_service"] = ai_service
                results["services_initialized"].append("ai_detection_service")
                logger.info("✅ AI Detection Optimization Service initialized")
            except Exception as e:
                results["services_failed"].append("ai_detection_service")
                results["errors"].append(f"AI Detection Service: {e}")
                logger.error(f"❌ AI Detection Service failed: {e}")

            # Initialize Iterative Workflow Service
            workflow_config = ServiceConfiguration(
                name="iterative_workflow_service",
                version="1.0.0",
                enabled=True,
                settings={
                    "max_iterations": 10,
                    "quality_threshold": 0.9,
                    "time_limit_seconds": 300,
                    "convergence_threshold": 0.01,
                },
            )

            try:
                workflow_service = IterativeWorkflowService(workflow_config)
                service_registry.register_service(workflow_service)
                self.services["iterative_workflow_service"] = workflow_service
                results["services_initialized"].append("iterative_workflow_service")
                logger.info("✅ Iterative Workflow Service initialized")
            except Exception as e:
                results["services_failed"].append("iterative_workflow_service")
                results["errors"].append(f"Iterative Workflow Service: {e}")
                logger.error(f"❌ Iterative Workflow Service failed: {e}")

            self.initialized = True

            # Summary
            total_services = len(results["services_initialized"]) + len(
                results["services_failed"]
            )
            success_rate = (
                len(results["services_initialized"]) / total_services
                if total_services > 0
                else 0
            )

            logger.info(
                f"🏁 Service initialization completed: {len(results['services_initialized'])}/{total_services} successful ({success_rate:.1%})"
            )

            if results["services_failed"]:
                results["success"] = False
                logger.warning(
                    f"⚠️ Failed services: {', '.join(results['services_failed'])}"
                )

        except Exception as e:
            results["success"] = False
            results["errors"].append(f"Initialization failed: {e}")
            logger.error(f"❌ Service initialization failed: {e}")

        return results

    def get_service(self, service_name: str):
        """Get a registered service by name."""
        return service_registry.get_service_typed(service_name, object)

    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all registered services."""
        status = {"initialized": self.initialized, "services": {}}

        for service_name, service in self.services.items():
            if hasattr(service, "health_check"):
                healthy = service.health_check()
            else:
                healthy = True

            status["services"][service_name] = {
                "healthy": healthy,
                "class": service.__class__.__name__,
                "enabled": getattr(service.config, "enabled", True)
                if hasattr(service, "config")
                else True,
            }

        return status

    def cleanup(self):
        """Clean up services and resources."""
        for service_name, service in self.services.items():
            try:
                if hasattr(service, "cleanup"):
                    service.cleanup()
                logger.info(f"🧹 Cleaned up service: {service_name}")
            except Exception as e:
                logger.warning(f"Failed to cleanup {service_name}: {e}")

        self.services.clear()
        self.initialized = False


# Global service initializer instance
service_initializer = ServiceInitializer()


def initialize_optimizer_services() -> Dict[str, Any]:
    """
    Convenience function to initialize all optimizer services.

    Returns:
        Dict[str, Any]: Initialization results
    """
    return service_initializer.initialize_all_services()


def get_optimizer_service(service_name: str):
    """Get an optimizer service by name."""
    return service_initializer.get_service(service_name)


def get_optimizer_status() -> Dict[str, Any]:
    """Get status of all optimizer services."""
    return service_initializer.get_service_status()


def cleanup_optimizer_services():
    """Clean up all optimizer services."""
    service_initializer.cleanup()


# Auto-initialize services when module is imported
if __name__ != "__main__":
    try:
        logger.info("🚀 Auto-initializing optimizer services...")
        init_result = initialize_optimizer_services()
        if init_result["success"]:
            logger.info("✅ Optimizer services auto-initialized successfully")
        else:
            logger.warning("⚠️ Optimizer services auto-initialization had issues")
    except Exception as e:
        logger.error(f"❌ Optimizer services auto-initialization failed: {e}")
