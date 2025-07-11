#!/usr/bin/env python3
"""
Thesaurus Handler - Handles thesaurus-specific article generation
"""
import logging
from typing import Dict, Any, Tuple
from ..base_handler import BaseHandler

logger = logging.getLogger(__name__)

class ThesaurusHandler(BaseHandler):
    """Handler for thesaurus-type articles"""
    
    def __init__(self):
        super().__init__("thesaurus")
    
    def prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for thesaurus articles"""
        subject = context.get("subject", "unknown")
        material = context.get("material", "aluminum")
        
        enhanced_context = context.copy()
        enhanced_context.update({
            "technical_term": subject,
            "technical_term_title": subject.title(),
            "material": material,
            "material_title": material.title(),
            "article_focus": "technical_definition",
            "primary_subject": subject
        })
        
        return enhanced_context
    
    def validate_context(self, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate context for thesaurus articles"""
        subject = context.get("subject")
        
        if not subject:
            return False, "Subject (technical term) is required for thesaurus articles"
        
        return True, "Valid thesaurus context"
    
    def get_tag_config(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get tag generation configuration for thesaurus articles"""
        return {
            "max_tags": 15,
            "tag_categories": [
                "technical_terminology",
                "term_category",
                "scientific_technical",
                "educational_reference",
                "application_context"
            ],
            "required_tags": ["LaserCleaning"],
            "tag_weights": {
                "technical_terminology": 0.35,
                "term_category": 0.2,
                "scientific_technical": 0.25,
                "educational_reference": 0.15,
                "application_context": 0.05
            },
            "fallback_tags": [
                "TechnicalTerminology", "MaterialScience", 
                "LaserPhysics", "EngineeringTerms", "ScientificDefinition"
            ]
        }
    
    def get_tag_template_path(self) -> str:
        """Get tag template path for thesaurus articles"""
        return "tags/tag_thesaurus.md"
    
    def prepare_tag_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare tag-specific context for thesaurus articles"""
        technical_term = context.get("technical_term", "LaserCleaning")
        material = context.get("material", "aluminum")
        
        return {
            "technical_term": technical_term,
            "technical_term_title": technical_term.title(),
            "material": material,
            "material_title": material.title(),
            "author_name": context.get("authorName", "Unknown"),
            "author_country": context.get("authorCountry", "Unknown"),
            "term_category": self._get_term_category(technical_term),
            "term_variations": self._get_term_variations(technical_term),
            "related_concepts": self._get_related_concepts(technical_term),
            "scientific_notation": self._get_scientific_notation(technical_term),
            "primary_applications": self._get_term_applications(technical_term),
            "target_industries": self._get_term_industries(technical_term)
        }
    
    def _get_term_category(self, term: str) -> str:
        """Get term category"""
        return "LaserTechnology"
    
    def _get_term_variations(self, term: str) -> str:
        """Get term variations"""
        return term.replace(" ", "")
    
    def _get_related_concepts(self, term: str) -> str:
        """Get related concepts"""
        return "SurfaceEngineering"
    
    def _get_scientific_notation(self, term: str) -> str:
        """Get scientific notation"""
        return "SIUnits"
    
    def _get_term_applications(self, term: str) -> str:
        """Get term applications"""
        return "IndustrialProcessing"
    
    def _get_term_industries(self, term: str) -> str:
        """Get term industries"""
        return "ManufacturingIndustry"