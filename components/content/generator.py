#!/usr/bin/env python3
"""
Content Component Generator Wrapper

Simple wrapper that integrates fail_fast_generator with the ComponentGeneratorFactory system.
"""

import logging
from typing import Dict, Optional
from dataclasses import dataclass
import json
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ComponentResult:
    """Result of component generation"""
    component_type: str
    content: str
    success: bool
    error_message: Optional[str] = None

class ContentComponentGenerator:
    """Lightweight wrapper for fail_fast_generator integration"""
    
    def __init__(self):
        self.component_type = "content"
        
    def generate(self, material_name: str, material_data: Dict, 
                api_client=None, author_info: Optional[Dict] = None,
                frontmatter_data: Optional[Dict] = None,
                schema_fields: Optional[Dict] = None) -> ComponentResult:
        """Generate content using fail_fast_generator"""
        
        try:
            # Import the fail_fast_generator
            from components.content.generators.fail_fast_generator import create_fail_fast_generator
            
            # Create generator with NO FALLBACKS - comprehensive validation enabled
            generator = create_fail_fast_generator(
                max_retries=0,  # NO RETRIES - fail immediately
                retry_delay=0.0,
                enable_scoring=True,   # Enable comprehensive quality scoring for persona/formatting validation
                human_threshold=75.0   # Standard human believability threshold
            )
            
            # Require real API client - no mocks or fallbacks
            if not api_client:
                return ComponentResult(
                    component_type=self.component_type,
                    content="",
                    success=False,
                    error_message="API client is required - no mock fallbacks available"
                )
            
            # Enhance author_info with complete data for proper validation
            enhanced_author_info = self._get_complete_author_info(author_info)
            
            # Call the generator with the parameters it expects
            result = generator.generate(
                material_name=material_name,
                material_data=material_data,
                api_client=api_client,
                author_info=enhanced_author_info,  # Use complete author info
                frontmatter_data=frontmatter_data
            )
            
            # Convert to ComponentResult format
            return ComponentResult(
                component_type=self.component_type,
                content=result.content,
                success=result.success,
                error_message=result.error_message if not result.success else None
            )
            
        except Exception as e:
            logger.error(f"Error in content generator: {e}")
            return ComponentResult(
                component_type=self.component_type,
                content="",
                success=False,
                error_message=str(e)
            )
    
    def _get_complete_author_info(self, author_info: Optional[Dict]) -> Dict:
        """
        Enhance author_info with complete data for proper validation.
        The validation system requires 'name' and 'country' for high scores.
        NO FALLBACKS - fails if author data cannot be loaded.
        """
        if not author_info:
            raise ValueError("Author info is required - no fallbacks available")
        
        # If already complete, return as-is
        if 'name' in author_info and 'country' in author_info:
            return author_info
        
        # Load complete author data from authors.json - REQUIRED
        if 'id' not in author_info:
            raise ValueError("Author ID is required in author_info")
        
        author_id = author_info['id']
        
        try:
            import json
            from pathlib import Path
            
            authors_file = Path("components/author/authors.json")
            if not authors_file.exists():
                raise FileNotFoundError(f"Required authors.json not found at {authors_file}")
            
            with open(authors_file, 'r', encoding='utf-8') as f:
                authors_data = json.load(f)
            
            if 'authors' not in authors_data:
                raise ValueError("Invalid authors.json structure - missing 'authors' key")
            
            # Find author by ID - MUST exist
            for author in authors_data['authors']:
                if author.get('id') == author_id:
                    # Validate required fields
                    if 'name' not in author or 'country' not in author:
                        raise ValueError(f"Author {author_id} missing required name/country fields")
                    
                    # Return complete author info for validation
                    return {
                        'id': author['id'],
                        'name': author['name'],
                        'country': author['country'],
                        'title': author.get('title', ''),
                        'expertise': author.get('expertise', '')
                    }
            
            # Author not found - fail immediately
            raise ValueError(f"Author ID {author_id} not found in authors.json - no fallbacks available")
            
        except Exception as e:
            logger.error(f"Failed to load complete author info: {e}")
            raise ValueError(f"Author data loading failed: {e}") from e