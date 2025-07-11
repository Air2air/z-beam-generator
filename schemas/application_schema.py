#!/usr/bin/env python3
"""
Application Schema - Schema for application articles
"""
import logging
from typing import Dict, Any, List
from .base_schema import BaseSchema

logger = logging.getLogger(__name__)

class ApplicationSchema(BaseSchema):
    """Schema for application-type articles"""
    
    def __init__(self):
        super().__init__("application")
    
    def get_metadata_schema(self) -> Dict[str, Any]:
        """Get metadata schema for application articles"""
        return {
            "type": "object",
            "required": [
                "title", "application", "industryCategory",
                "authorName", "authorCountry"
            ],
            "properties": {
                "title": {"type": "string"},
                "application": {"type": "string"},
                "industryCategory": {"type": "string"},
                "componentType": {"type": "string"},
                "processParameters": {"type": "object"},
                "qualityRequirements": {"type": "array", "items": {"type": "string"}},
                "benefits": {"type": "array", "items": {"type": "string"}},
                "challenges": {"type": "array", "items": {"type": "string"}},
                "materialTypes": {"type": "array", "items": {"type": "string"}},  # Optional array of materials
                "authorName": {"type": "string"},
                "authorCountry": {"type": "string"},
                "articleType": {"type": "string", "enum": ["application"]}
            }
        }
    
    def get_tag_schema(self) -> Dict[str, Any]:
        """Get tag generation schema for application articles"""
        return {
            "max_tags": 15,
            "required_tags": ["LaserCleaning"],
            "tag_categories": [
                "application_specific",   # Application name and type
                "material_component",     # Material being cleaned
                "industry_process",       # Industry and process type
                "technical_process",      # Technical aspects
                "business_value"          # Benefits and value
            ],
            "tag_weights": {
                "application_specific": 0.30,
                "material_component": 0.25,
                "industry_process": 0.25,
                "technical_process": 0.15,
                "business_value": 0.05
            },
            "context_fields": [
                "application", "application_title", "industryCategory", 
                "componentType", "authorName", "authorCountry"
            ]
        }
    
    def get_jsonld_schema(self) -> Dict[str, Any]:
        """Get JSON-LD schema for application articles"""
        return {
            "@context": {
                "@vocab": "https://schema.org/",
                "laser": "https://laser-cleaning.org/terms/",
                "industrial": "https://industrial-process.org/terms/"
            },
            "@type": "Article",
            "about": {
                "@type": "industrial:Application",
                "name": "{application}",
                "applicationType": "{industryCategory}",
                "componentType": "{componentType}",
                "applicableMaterials": "{materialTypes}"
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "name": "Laser Cleaning for {application}"
            },
            "applicationCategory": "laser:ApplicationCleaning",
            "industry": "{industryCategory}"
        }
    
    def get_template_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get template context for application articles"""
        application = data.get("application", "unknown")
        
        return {
            "application": application,
            "application_title": application.title(),
            "authorName": data.get("authorName", "Unknown"),
            "authorCountry": data.get("authorCountry", "Unknown"),
            "industryCategory": data.get("industryCategory", "Industrial"),
            "componentType": data.get("componentType", "Components"),
            "materialTypes": ", ".join(data.get("materialTypes", ["Various materials"])),
            "application_category": self._get_application_category(application),
            "end_use": self._get_end_use(application),
            "process_focus": "PrecisionCleaning",
            "industry_application": "ManufacturingIndustry"
        }
    
    def validate_data(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate data against application schema"""
        errors = []
        
        if not data.get("subject"):
            errors.append("Application name (subject) is required")
        
        if data.get("article_type") != "application":
            errors.append("Article type must be 'application'")
        
        # Optional: Validate subject format
        subject = data.get("subject", "")
        if subject and len(subject) < 2:
            errors.append("Application name must be at least 2 characters")
        
        return len(errors) == 0, errors
    
    def get_fallback_tags(self) -> List[str]:
        """Get fallback tags for application articles"""
        return [
            "LaserCleaning", "IndustrialApplications", "ProcessOptimization",
            "Manufacturing", "Efficiency", "QualityControl",
            "ComponentCleaning", "IndustrialProcessing", "PrecisionCleaning",
            "ManufacturingIndustry", "ProcessImprovement", "TechnicalSolutions"
        ]
    
    def _get_application_category(self, application: str) -> str:
        """Get application category based on application name"""
        app_lower = application.lower()
        
        if "turbine" in app_lower or "blade" in app_lower:
            return "PowerGeneration"
        elif "engine" in app_lower or "motor" in app_lower:
            return "EngineComponents"
        elif "medical" in app_lower or "surgical" in app_lower:
            return "MedicalDevices"
        elif "aerospace" in app_lower or "aircraft" in app_lower:
            return "AerospaceComponents"
        elif "automotive" in app_lower or "vehicle" in app_lower:
            return "AutomotiveComponents"
        elif "electronics" in app_lower or "circuit" in app_lower:
            return "ElectronicsComponents"
        else:
            return "IndustrialComponents"
    
    def _get_end_use(self, application: str) -> str:
        """Get end use classification for application"""
        app_lower = application.lower()
        
        if "power" in app_lower or "energy" in app_lower:
            return "PowerGeneration"
        elif "transport" in app_lower or "vehicle" in app_lower:
            return "Transportation"
        elif "medical" in app_lower or "healthcare" in app_lower:
            return "Healthcare"
        elif "aerospace" in app_lower or "aviation" in app_lower:
            return "Aerospace"
        else:
            return "IndustrialSystems"