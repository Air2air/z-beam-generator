"""Service for managing author-specific layouts."""

import logging
from typing import Dict, Any, List

from .author_service import AuthorService
from .config.component_config import get_component_config

logger = logging.getLogger(__name__)

class AuthorLayoutService:
    """Service for retrieving author-specific layout settings."""
    
    def __init__(self):
        """Initialize the author layout service."""
        self.author_service = AuthorService()
    
    def get_component_order(self, author_id: int) -> List[str]:
        """Get component order for an author."""
        from .config.layout_config import get_component_order
        return get_component_order(author_id)
    
    def get_component_params(self, author_id: int, component: str) -> Dict[str, Any]:
        """Get component parameters for an author."""
        return get_component_config(author_id, component)
    
    def get_template(self, author_id: int) -> str:
        """Get template name for an author."""
        # Get author data
        author = self.author_service.get_author_by_id(author_id)
        
        # Default template if author not found
        if not author or "country" not in author:
            return "usa"
        
        # Use country as template name
        return author["country"].lower()