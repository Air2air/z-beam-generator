#!/usr/bin/env python3
"""
Services Module - Unified Service Registry

Provides centralized access to all system services with clean import patterns.
Part of consolidation plan to organize services by domain.

Last Updated: October 22, 2025
"""

# Validation Services
from .validation.orchestrator import ValidationOrchestrator
from .validation.unified_schema_validator import UnifiedSchemaValidator

# Research Services (canonical location: research/services/)
from materials.research.services.ai_research_service import AIResearchEnrichmentService

# Property Services
# PropertyManager moved to components/frontmatter/services/property_manager.py
from .property.material_auditor import MaterialAuditor

__all__ = [
    # Validation Services
    'ValidationOrchestrator',
    'UnifiedSchemaValidator',
    
    # Research Services
    'AIResearchEnrichmentService',
    
    # Property Services
    'MaterialAuditor',
]

# Service registry for dynamic discovery
SERVICE_REGISTRY = {
    'validation': {
        'orchestrator': ValidationOrchestrator,
        'schema_validator': UnifiedSchemaValidator,
    },
    'research': {
        'ai_research': AIResearchEnrichmentService,
    },
    'property': {
        'material_auditor': MaterialAuditor,
    },
}


def get_service(domain: str, service_name: str):
    """
    Get service instance by domain and name.
    
    Args:
        domain: Service domain (validation, research, property)
        service_name: Service name within domain
        
    Returns:
        Service class or instance
        
    Raises:
        KeyError: If service not found
    """
    if domain not in SERVICE_REGISTRY:
        raise KeyError(f"Unknown service domain: {domain}")
    
    if service_name not in SERVICE_REGISTRY[domain]:
        raise KeyError(f"Unknown service in {domain}: {service_name}")
    
    return SERVICE_REGISTRY[domain][service_name]


def list_services(domain: str = None) -> dict:
    """
    List available services by domain.
    
    Args:
        domain: Optional domain filter
        
    Returns:
        Dictionary of available services
    """
    if domain:
        return SERVICE_REGISTRY.get(domain, {})
    
    return SERVICE_REGISTRY