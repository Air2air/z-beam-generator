#!/usr/bin/env python3
"""
Base Handler - Abstract base class for all subject handlers
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class BaseHandler(ABC):
    """Abstract base class for subject handlers"""
    
    def __init__(self, subject_type: str):
        self.subject_type = subject_type
    
    @abstractmethod
    def prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for this subject type"""
        pass
    
    @abstractmethod
    def validate_context(self, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate context for this subject type"""
        pass
    
    @abstractmethod
    def get_tag_config(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get tag generation configuration for this subject type"""
        pass
    
    @abstractmethod
    def get_tag_template_path(self) -> str:
        """Get tag template path for this subject type"""
        pass
    
    @abstractmethod
    def prepare_tag_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare tag-specific context for this subject type"""
        pass
    
    def get_metadata_enhancements(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get metadata enhancements for this subject type"""
        return {"articleType": self.subject_type}
    
    def get_tag_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get tag generation context for this subject type"""
        return {"tag_focus": self.subject_type}