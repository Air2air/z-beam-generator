"""
Enricher Output Validation System
==================================

Validates enricher outputs to catch errors early before they propagate.

Key Features:
- Schema-based validation for enricher outputs
- Catches empty data, missing required fields, wrong types
- Provides clear error messages with field paths
- Logs warnings for suspicious patterns

Created: December 19, 2025
Purpose: Catch enricher bugs early, prevent data quality issues
"""

import logging
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class EnricherOutputValidator:
    """
    Validates enricher outputs against expected schemas.
    
    Usage:
        validator = EnricherOutputValidator()
        validator.validate_relationships(frontmatter)
        # Raises ValidationError if issues found
    """
    
    def __init__(self):
        """Initialize validator with validation rules."""
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_relationships(
        self, 
        frontmatter: Dict[str, Any],
        required_fields: Optional[List[str]] = None
    ) -> bool:
        """
        Validate relationships structure in frontmatter.
        
        Args:
            frontmatter: Frontmatter dict to validate
            required_fields: Fields required in each relationship item
                           (default: ['id', 'url'])
        
        Returns:
            True if valid, raises ValidationError if invalid
        
        Raises:
            ValidationError: If validation fails
        """
        self.errors = []
        self.warnings = []
        
        if required_fields is None:
            required_fields = ['id', 'url']
        
        # Check relationships exists
        if 'relationships' not in frontmatter:
            # Not an error - some items may not have relationships
            return True
        
        relationships = frontmatter['relationships']
        
        # Check relationships is a dict
        if not isinstance(relationships, dict):
            self.errors.append(f"relationships must be dict, got {type(relationships).__name__}")
            raise ValidationError(self.errors[0], self.errors, self.warnings)
        
        # Validate each relationship type
        for rel_type, rel_items in relationships.items():
            if not isinstance(rel_items, list):
                self.errors.append(f"relationships.{rel_type} must be list, got {type(rel_items).__name__}")
                continue
            
            # Validate each item in relationship
            for idx, item in enumerate(rel_items):
                if not isinstance(item, dict):
                    self.errors.append(f"relationships.{rel_type}[{idx}] must be dict, got {type(item).__name__}")
                    continue
                
                # Check required fields
                for field in required_fields:
                    if field not in item:
                        self.errors.append(f"relationships.{rel_type}[{idx}] missing required field '{field}'")
                    elif not item[field]:
                        self.warnings.append(f"relationships.{rel_type}[{idx}].{field} is empty")
                
                # Check for suspicious URL patterns
                if 'url' in item:
                    url = item['url']
                    if url == 'NO_URL' or url == '':
                        self.errors.append(f"relationships.{rel_type}[{idx}].url is invalid: '{url}'")
                    elif '/general/misc/' in url:
                        self.warnings.append(
                            f"relationships.{rel_type}[{idx}].url uses fallback path: {url}"
                        )
                
                # Check for empty compound_data (indicates lookup failure)
                if 'id' in item and item['id'] and 'category' in required_fields:
                    if 'category' not in item or item.get('category') == 'general':
                        self.warnings.append(
                            f"relationships.{rel_type}[{idx}] may have failed lookup (category=general)"
                        )
        
        # Raise error if any found
        if self.errors:
            raise ValidationError(
                f"Found {len(self.errors)} validation errors",
                self.errors,
                self.warnings
            )
        
        # Log warnings
        if self.warnings:
            for warning in self.warnings:
                logger.warning(f"EnricherOutputValidator: {warning}")
        
        return True
    
    def validate_linkage_enrichment(
        self,
        frontmatter: Dict[str, Any],
        field: str,
        expected_min: int = 0
    ) -> bool:
        """
        Validate linkage enrichment output.
        
        Args:
            frontmatter: Frontmatter dict to validate
            field: Field name (e.g., 'produces_compounds')
            expected_min: Minimum expected items (0 = optional)
        
        Returns:
            True if valid
        
        Raises:
            ValidationError: If validation fails
        """
        self.errors = []
        self.warnings = []
        
        if field not in frontmatter:
            if expected_min > 0:
                self.errors.append(f"Missing required field '{field}'")
                raise ValidationError(self.errors[0], self.errors, self.warnings)
            return True
        
        items = frontmatter[field]
        
        if not isinstance(items, list):
            self.errors.append(f"Field '{field}' must be list, got {type(items).__name__}")
            raise ValidationError(self.errors[0], self.errors, self.warnings)
        
        if len(items) < expected_min:
            self.warnings.append(f"Field '{field}' has {len(items)} items, expected at least {expected_min}")
        
        # Validate each item
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                self.errors.append(f"{field}[{idx}] must be dict, got {type(item).__name__}")
                continue
            
            # Check for common enrichment fields
            if 'id' not in item:
                self.errors.append(f"{field}[{idx}] missing 'id'")
        
        if self.errors:
            raise ValidationError(
                f"Linkage enrichment validation failed for '{field}'",
                self.errors,
                self.warnings
            )
        
        return True


class ValidationError(Exception):
    """Exception raised when enricher output validation fails."""
    
    def __init__(self, message: str, errors: List[str], warnings: List[str]):
        """
        Initialize validation error.
        
        Args:
            message: Primary error message
            errors: List of all errors found
            warnings: List of all warnings found
        """
        super().__init__(message)
        self.errors = errors
        self.warnings = warnings
    
    def __str__(self):
        """Format error message with all details."""
        lines = [self.args[0]]
        if self.errors:
            lines.append(f"\nErrors ({len(self.errors)}):")
            for error in self.errors:
                lines.append(f"  - {error}")
        if self.warnings:
            lines.append(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings:
                lines.append(f"  - {warning}")
        return "\n".join(lines)
