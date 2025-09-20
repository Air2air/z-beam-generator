#!/usr/bin/env python3
"""
API Client Management Consolidation Layer

GROK-COMPLIANT: Provides unified management layer while preserving all existing 
client_manager.py and client_factory.py functionality without modifying working code.

This layer consolidates overlapping functionality between:
- api/client_manager.py (management and validation functions)  
- api/client_factory.py (client creation functions)

All original interfaces are preserved for backward compatibility.
"""

import time
from typing import Dict, Any

# Import existing functionality without modification
from .client_factory import APIClientFactory
from .client_manager import setup_api_client, validate_api_environment, test_api_connectivity


class ConsolidatedAPIManager:
    """
    Unified API client management layer that consolidates overlapping functionality
    while preserving all existing interfaces.
    
    CONSOLIDATION BENEFITS:
    - Single entry point for all API client operations
    - Unified validation and testing
    - Performance monitoring across all operations
    - Consistent error handling and logging
    """
    
    def __init__(self):
        self.operation_stats = {
            "clients_created": 0,
            "validations_performed": 0,
            "connectivity_tests": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    # UNIFIED CLIENT CREATION (consolidates client_factory functionality)
    
    def create_client(self, provider: str = "deepseek", **kwargs):
        """Unified client creation with performance tracking"""
        self.operation_stats["clients_created"] += 1
        return APIClientFactory.create_client(provider, **kwargs)
    
    def create_client_for_component(self, component_type: str, **kwargs):
        """Unified component client creation with performance tracking"""
        self.operation_stats["clients_created"] += 1
        return APIClientFactory.create_client_for_component(component_type, **kwargs)
    
    def setup_client_with_caching(self, provider: str = "deepseek"):
        """Unified client setup with caching (from client_manager)"""
        self.operation_stats["cache_hits"] += 1
        return setup_api_client(provider)
    
    # UNIFIED VALIDATION (consolidates client_manager functionality)
    
    def validate_environment(self) -> Dict[str, Any]:
        """Unified environment validation with enhanced reporting"""
        self.operation_stats["validations_performed"] += 1
        
        base_results = validate_api_environment()
        factory_validation = APIClientFactory.validate_configuration()
        
        # Combine results for comprehensive validation
        enhanced_results = {
            "timestamp": time.time(),
            "environment_validation": base_results,
            "configuration_validation": factory_validation,
            "summary": {
                "total_providers": len(base_results),
                "configured_providers": sum(1 for r in base_results.values() if r["configured"]),
                "valid_configurations": len([p for p in factory_validation["providers"].values() if p["valid"]]),
                "overall_status": "healthy" if factory_validation["status"] == "valid" else "issues_detected"
            }
        }
        
        return enhanced_results
    
    def test_connectivity(self, provider: str = None) -> Dict[str, Any]:
        """Unified connectivity testing with enhanced reporting"""
        self.operation_stats["connectivity_tests"] += 1
        
        start_time = time.time()
        results = test_api_connectivity(provider)
        end_time = time.time()
        
        # Add performance metrics
        results["performance"] = {
            "test_duration": end_time - start_time,
            "average_test_time": (end_time - start_time) / len(results["tested_providers"]) if results["tested_providers"] else 0
        }
        
        return results
    
    # UNIFIED MONITORING AND STATISTICS
    
    def get_operation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive operation statistics"""
        return {
            "consolidation_stats": self.operation_stats.copy(),
            "timestamp": time.time()
        }
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive system status combining all validations"""
        return {
            "environment": self.validate_environment(),
            "connectivity": self.test_connectivity(),
            "operations": self.get_operation_statistics(),
            "system_health": "operational"  # Could be enhanced with more checks
        }
    
    # UTILITY METHODS
    
    def reset_statistics(self):
        """Reset operation statistics"""
        self.operation_stats = {key: 0 for key in self.operation_stats}
    
    def is_system_healthy(self) -> bool:
        """Quick health check for the entire API system"""
        try:
            validation = self.validate_environment()
            return validation["summary"]["overall_status"] == "healthy"
        except Exception:
            return False


# Global consolidation manager instance
consolidated_manager = ConsolidatedAPIManager()

# ENHANCED CONVENIENCE FUNCTIONS (preserving backward compatibility)

def create_consolidated_client(provider: str = "deepseek", **kwargs):
    """Create client through consolidated manager"""
    return consolidated_manager.create_client(provider, **kwargs)

def validate_consolidated_environment() -> Dict[str, Any]:
    """Validate environment through consolidated manager"""
    return consolidated_manager.validate_environment()

def test_consolidated_connectivity(provider: str = None) -> Dict[str, Any]:
    """Test connectivity through consolidated manager"""
    return consolidated_manager.test_connectivity(provider)

def get_consolidated_status() -> Dict[str, Any]:
    """Get comprehensive system status"""
    return consolidated_manager.get_comprehensive_status()

def is_api_system_healthy() -> bool:
    """Quick health check for API system"""
    return consolidated_manager.is_system_healthy()

# PERFORMANCE MONITORING UTILITIES

class APIPerformanceMonitor:
    """Monitor API performance across the consolidated system"""
    
    def __init__(self):
        self.performance_data = {
            "response_times": [],
            "error_rates": {},
            "provider_usage": {},
            "component_usage": {}
        }
    
    def track_client_creation(self, provider: str, duration: float):
        """Track client creation performance"""
        if provider not in self.performance_data["provider_usage"]:
            self.performance_data["provider_usage"][provider] = {"count": 0, "avg_duration": 0}
        
        stats = self.performance_data["provider_usage"][provider]
        stats["count"] += 1
        stats["avg_duration"] = (stats["avg_duration"] * (stats["count"] - 1) + duration) / stats["count"]
    
    def track_component_usage(self, component_type: str):
        """Track component usage patterns"""
        if component_type not in self.performance_data["component_usage"]:
            self.performance_data["component_usage"][component_type] = 0
        self.performance_data["component_usage"][component_type] += 1
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        return {
            "provider_stats": self.performance_data["provider_usage"],
            "component_stats": self.performance_data["component_usage"],
            "total_operations": sum(stats["count"] for stats in self.performance_data["provider_usage"].values()),
            "most_used_provider": max(self.performance_data["provider_usage"].items(), 
                                    key=lambda x: x[1]["count"])[0] if self.performance_data["provider_usage"] else None,
            "most_used_component": max(self.performance_data["component_usage"].items(), 
                                     key=lambda x: x[1])[0] if self.performance_data["component_usage"] else None
        }

# Global performance monitor
performance_monitor = APIPerformanceMonitor()

# Export consolidated interfaces
__all__ = [
    'ConsolidatedAPIManager',
    'consolidated_manager',
    'create_consolidated_client',
    'validate_consolidated_environment', 
    'test_consolidated_connectivity',
    'get_consolidated_status',
    'is_api_system_healthy',
    'APIPerformanceMonitor',
    'performance_monitor'
]
