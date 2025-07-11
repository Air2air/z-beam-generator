#!/usr/bin/env python3
"""
Subject Router - Routes between different article types
"""
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class SubjectRouter:
    """Routes between different article types and their specialized handlers"""
    
    def __init__(self):
        self.handlers = {}
        self._load_handlers()
    
    def _load_handlers(self):
        """Load handlers for each article type"""
        try:
            from .material.material_handler import MaterialHandler
            from .application.application_handler import ApplicationHandler
            from .region.region_handler import RegionHandler
            from .thesaurus.thesaurus_handler import ThesaurusHandler
            
            self.handlers = {
                "material": MaterialHandler(),
                "application": ApplicationHandler(),
                "region": RegionHandler(),
                "thesaurus": ThesaurusHandler()
            }
            
            logger.info(f"🔧 Loaded {len(self.handlers)} subject handlers")
            
        except ImportError as e:
            logger.error(f"❌ Failed to load subject handlers: {e}")
            raise RuntimeError(f"Subject handlers not available: {e}")
    
    def get_handler(self, article_type: str):
        """Get handler for specific article type"""
        handler = self.handlers.get(article_type)
        
        if not handler:
            available_types = list(self.handlers.keys())
            raise ValueError(f"Unknown article type: {article_type}. Available: {available_types}")
        
        return handler
    
    def prepare_context(self, article_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for specific article type"""
        handler = self.get_handler(article_type)
        return handler.prepare_context(context)
    
    def validate_context(self, article_type: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate context for specific article type"""
        handler = self.get_handler(article_type)
        return handler.validate_context(context)
    
    def get_tag_config(self, article_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get tag generation configuration for specific article type"""
        handler = self.get_handler(article_type)
        return handler.get_tag_config(context)
    
    def get_tag_template_path(self, article_type: str) -> str:
        """Get tag template path for specific article type"""
        handler = self.get_handler(article_type)
        return handler.get_tag_template_path()
    
    def prepare_tag_context(self, article_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare tag-specific context for article type"""
        handler = self.get_handler(article_type)
        return handler.prepare_tag_context(context)
    
    def get_supported_types(self) -> list:
        """Get list of supported article types"""
        return list(self.handlers.keys())