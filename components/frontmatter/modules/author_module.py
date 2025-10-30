"""
AuthorModule - Extract author metadata from Materials.yaml

Handles: author dictionary extraction

Architecture:
- Pure extraction from Materials.yaml
- Validation of required author fields
- No modification or enhancement
- Fail-fast on missing data
"""

import logging
from typing import Dict


class AuthorModule:
    """Extract author metadata for frontmatter"""
    
    # Required author fields
    REQUIRED_FIELDS = ['id', 'name', 'country']
    
    # Optional but expected fields
    OPTIONAL_FIELDS = ['title', 'sex', 'expertise', 'authoredMaterials']
    
    def __init__(self):
        """Initialize author module"""
        self.logger = logging.getLogger(__name__)
    
    def generate(self, material_data: Dict) -> Dict:
        """
        Extract author metadata from material data
        
        Args:
            material_data: Material data from Materials.yaml
            
        Returns:
            Author dictionary with fields:
            - id: Author ID (int)
            - name: Full name (str)
            - country: Country code/name (str)
            - title: Professional title (str, optional)
            - sex: Gender (str, optional)
            - expertise: Area of expertise (str, optional)
            - authoredMaterials: Number of materials (int, optional)
            
        Raises:
            ValueError: If author data missing or invalid
        """
        self.logger.info("Extracting author metadata")
        
        # Extract author from material data
        if 'author' not in material_data:
            raise ValueError("Author field missing in material data")
        
        author = material_data['author']
        
        if not isinstance(author, dict):
            raise ValueError(f"Author must be dict, got {type(author)}")
        
        # Validate required fields
        self._validate_author(author)
        
        # Return author dict as-is (pure extraction)
        self.logger.info(
            f"✅ Extracted author: {author.get('name')} ({author.get('country')})"
        )
        
        return author
    
    def _validate_author(self, author: Dict):
        """
        Validate author has required fields
        
        Raises:
            ValueError: If required fields missing
        """
        missing = [f for f in self.REQUIRED_FIELDS if f not in author or not author[f]]
        
        if missing:
            raise ValueError(f"Missing required author fields: {missing}")
        
        # Validate field types
        if not isinstance(author['id'], int):
            raise ValueError(f"Author ID must be int, got {type(author['id'])}")
        
        if not isinstance(author['name'], str) or not author['name'].strip():
            raise ValueError("Author name must be non-empty string")
        
        if not isinstance(author['country'], str) or not author['country'].strip():
            raise ValueError("Author country must be non-empty string")
        
        self.logger.debug(f"Author validation passed: {author['name']}")


# Backward compatibility
class AuthorGenerator(AuthorModule):
    """Alias for backward compatibility"""
    pass
