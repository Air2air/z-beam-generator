#!/usr/bin/env python3
"""
Application Handler - Handles application-specific article generation
"""
import logging
from typing import Dict, Any, Tuple
from ..base_handler import BaseHandler

logger = logging.getLogger(__name__)

class ApplicationHandler(BaseHandler):
    """Handler for application-type articles"""
    
    def __init__(self):
        super().__init__("application")
    
    def prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for application articles"""
        subject = context.get("subject", "unknown")
        material = context.get("material", "steel")
        
        enhanced_context = context.copy()
        enhanced_context.update({
            "application": subject,
            "application_title": subject.title(),
            "material": material,
            "material_title": material.title(),
            "article_focus": "application_process",
            "primary_subject": subject
        })
        
        return enhanced_context
    
    def validate_context(self, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate context for application articles"""
        subject = context.get("subject")
        
        if not subject:
            return False, "Subject (application name) is required for application articles"
        
        return True, "Valid application context"
    
    def get_tag_config(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get tag generation configuration for application articles"""
        return {
            "max_tags": 15,
            "tag_categories": [
                "application_specific",
                "material_component",
                "industry_process",
                "technical_process",
                "business_value"
            ],
            "required_tags": ["LaserCleaning"],
            "tag_weights": {
                "application_specific": 0.35,
                "material_component": 0.2,
                "industry_process": 0.25,
                "technical_process": 0.15,
                "business_value": 0.05
            },
            "fallback_tags": [
                "IndustrialApplications", "ProcessOptimization", 
                "Manufacturing", "Efficiency", "QualityControl"
            ]
        }
    
    def get_tag_template_path(self) -> str:
        """Get tag template path for application articles"""
        return "tags/tag_application.md"
    
    def prepare_tag_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare tag-specific context for application articles"""
        application = context.get("application", "unknown")
        material = context.get("material", "steel")
        
        return {
            "application": application,
            "application_title": application.title(),
            "material": material,
            "material_title": material.title(),
            "author_name": context.get("authorName", "Unknown"),
            "author_country": context.get("authorCountry", "Unknown"),
            "application_category": self._get_application_category(application),
            "end_use": self._get_end_use(application),
            "process_focus": self._get_process_focus(application),
            "industry_application": self._get_industry_application(application),
            "component_type": self._get_component_type(application)
        }
    
    def _get_application_category(self, application: str) -> str:
        """Get application category"""
        app_lower = application.lower()
        if "turbine" in app_lower:
            return "PowerGeneration"
        elif "engine" in app_lower:
            return "EngineComponents"
        elif "medical" in app_lower:
            return "MedicalDevices"
        else:
            return "IndustrialComponents"
    
    def _get_end_use(self, application: str) -> str:
        """Get end use for application"""
        return "IndustrialSystems"
    
    def _get_process_focus(self, application: str) -> str:
        """Get process focus for application"""
        return "PrecisionCleaning"
    
    def _get_industry_application(self, application: str) -> str:
        """Get industry application"""
        return "ManufacturingIndustry"
    
    def _get_component_type(self, application: str) -> str:
        """Get component type for application"""
        return "IndustrialComponents"