#!/usr/bin/env python3
"""
Material Handler - Handles material-specific article generation
"""
import logging
from typing import Dict, Any, Tuple
from ..base_handler import BaseHandler

logger = logging.getLogger(__name__)

class MaterialHandler(BaseHandler):
    """Handler for material-type articles"""
    
    def __init__(self):
        super().__init__("material")
    
    def prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for material articles"""
        subject = context.get("subject", "unknown")
        material = context.get("material", subject)
        
        enhanced_context = context.copy()
        enhanced_context.update({
            "material": material,
            "material_title": material.title(),
            "article_focus": "material_properties",
            "primary_subject": subject
        })
        
        return enhanced_context
    
    def validate_context(self, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate context for material articles"""
        subject = context.get("subject")
        
        if not subject:
            return False, "Subject (material name) is required for material articles"
        
        return True, "Valid material context"
    
    def get_tag_config(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get tag generation configuration for material articles"""
        return {
            "max_tags": 15,
            "tag_categories": [
                "material_identity",
                "material_properties", 
                "material_classification",
                "industry_applications",
                "process_technology",
                "quality_metrics"
            ],
            "required_tags": ["LaserCleaning"],
            "tag_weights": {
                "material_identity": 0.3,
                "material_properties": 0.2,
                "industry_applications": 0.2,
                "process_technology": 0.2,
                "quality_metrics": 0.1
            },
            "fallback_tags": [
                "IndustrialCleaning", "ContaminantRemoval", 
                "Manufacturing", "QualityControl", "SurfacePreparation"
            ]
        }
    
    def get_tag_template_path(self) -> str:
        """Get tag template path for material articles"""
        return "tags/tag_material.md"
    
    def prepare_tag_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare tag-specific context for material articles"""
        material = context.get("material", "unknown")
        
        return {
            "material": material,
            "material_title": material.title(),
            "material_class": context.get("materialClass", "Material"),
            "chemical_symbol": context.get("chemicalSymbol", ""),
            "author_name": context.get("authorName", "Unknown"),
            "author_country": context.get("authorCountry", "Unknown"),
            "primary_applications": ", ".join(context.get("applications", ["Industrial cleaning"])[:3]),
            "key_properties": context.get("generalClassifier", "Material"),
            "related_materials": ", ".join(context.get("relatedMaterials", [])[:2])
        }