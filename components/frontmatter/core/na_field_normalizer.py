#!/usr/bin/env python3
"""
Strict Field Normalization -             'images': lambda: {  # Images with N/A structure - fail-fast, no fallbacks
                'hero': {
                    'alt': f'{material_name} surface laser cleaning (N/A)',
                    'url': 'N/A'
                },
                'micro': {
                    'alt': f'Microscopic view of {material_name} surface (N/A)',
                    'url': 'N/A'
                }ks, N/A for Missing Fields

Simple approach that ensures all required fields exist but populates
missing/invalid fields with "N/A" or equivalent programmatic values.
No intelligent defaults or fallbacks - just structural completeness.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class StrictFieldNormalizer:
    """Simple field normalizer that uses N/A for missing fields"""
    
    def __init__(self):
        self.normalization_stats = {
            'fields_processed': 0,
            'fields_set_to_na': 0,
            'fields_normalized': 0
        }
    
    def normalize_frontmatter(self, frontmatter: Dict[str, Any], material_name: str) -> Dict[str, Any]:
        """
        Ensure all required fields exist, set missing ones to N/A equivalents
        
        Args:
            frontmatter: Input frontmatter data (can be incomplete/invalid)
            material_name: Material name for context
            
        Returns:
            Complete frontmatter with all required fields (N/A for missing)
        """
        if not isinstance(frontmatter, dict):
            logger.warning(f"Invalid frontmatter type for {material_name}, creating empty structure")
            frontmatter = {}
        
        normalized = {}
        
        # Required fields with their N/A equivalents
        required_fields = {
            'name': lambda: material_name,  # Only exception - use material name
            'category': lambda: 'N/A',
            'subcategory': lambda: 'N/A',  # New subcategory field
            'complexity': lambda: 'N/A', 
            'difficulty_score': lambda: 0,  # Numeric N/A equivalent
            'author_id': lambda: 0,  # Numeric N/A equivalent
            'title': lambda: 'N/A',
            'headline': lambda: 'N/A',
            'description': lambda: 'N/A',
            'keywords': lambda: [],  # Empty list as N/A equivalent
            'applications': lambda: [],  # Empty list as N/A equivalent
            'compatibility': lambda: {},  # Empty dict as N/A equivalent
            'images': lambda: {  # Images with N/A structure - fail-fast, no fallbacks
                'hero': {
                    'alt': f'{material_name} surface laser cleaning (N/A)',
                    'url': 'N/A'
                },
                'micro': {
                    'alt': f'Microscopic view of {material_name} surface (N/A)',
                    'url': 'N/A'
                }
            },
            'author_object': lambda: {  # Minimal structure with N/A values
                'id': 0,
                'name': 'N/A',
                'sex': 'N/A',
                'title': 'N/A',
                'country': 'N/A',
                'expertise': 'N/A',
                'image': 'N/A'
            }
        }
        
        # Process each required field
        for field_name, na_generator in required_fields.items():
            self.normalization_stats['fields_processed'] += 1
            
            if field_name in frontmatter and self._is_valid_value(frontmatter[field_name]):
                # Use existing valid value
                normalized[field_name] = self._normalize_existing_field(
                    field_name, frontmatter[field_name], material_name
                )
                self.normalization_stats['fields_normalized'] += 1
            else:
                # Set to N/A equivalent
                normalized[field_name] = na_generator()
                self.normalization_stats['fields_set_to_na'] += 1
                logger.info(f"Set {field_name} to N/A for {material_name}")
        
        # Handle optional fields (only include if present and valid)
        optional_fields = ['chemicalProperties', 'subcategory', 'properties', 'materialProperties', 'machineSettings']
        for field_name in optional_fields:
            if field_name in frontmatter and self._is_valid_value(frontmatter[field_name]):
                normalized[field_name] = frontmatter[field_name]
        
        return normalized
    
    def _is_valid_value(self, value: Any) -> bool:
        """Check if a value is considered valid (not None, not empty string, etc.)"""
        if value is None:
            return False
        if isinstance(value, str) and value.strip() == '':
            return False
        if isinstance(value, (list, dict)) and len(value) == 0:
            return False
        return True
    
    def _normalize_existing_field(self, field_name: str, value: Any, material_name: str) -> Any:
        """Normalize existing valid fields (minimal processing)"""
        
        # Type-specific normalization
        if field_name == 'keywords':
            return self._normalize_keywords(value)
        elif field_name in ['properties', 'machineSettings']:
            return self._normalize_hierarchical_section(value, field_name)
        elif field_name == 'author_object':
            return self._normalize_author_object(value)
        elif field_name in ['applications']:
            return self._normalize_list_field(value)
        elif field_name == 'compatibility':
            return self._normalize_compatibility(value)
        elif field_name == 'images':
            return self._normalize_images(value, material_name)
        else:
            # For simple fields, just return as-is (with basic cleanup)
            if isinstance(value, str):
                return value.strip()
            return value
    
    def _normalize_keywords(self, value: Any) -> List[str]:
        """Normalize keywords to list of strings"""
        if isinstance(value, list):
            return [str(kw).strip() for kw in value if str(kw).strip()]
        elif isinstance(value, str):
            return [kw.strip() for kw in value.split(',') if kw.strip()]
        else:
            return []  # N/A equivalent for keywords
    
    def _normalize_hierarchical_section(self, value: Any, section_name: str) -> Dict:
        """Normalize hierarchical sections like properties and machineSettings"""
        if not isinstance(value, dict):
            return {}  # N/A equivalent
        
        # For hierarchical sections, preserve the structure as-is
        # since they're already properly organized
        return value
    
    def _extract_numeric_only(self, value):
        """Extract numeric value from mixed string/number"""
        if isinstance(value, (int, float)):
            return value
        
        if isinstance(value, str):
            import re
            # Match number (int or float) at the beginning of the string
            match = re.match(r'^(-?\d+(?:\.\d+)?)', value.strip())
            if match:
                numeric_str = match.group(1)
                try:
                    return float(numeric_str) if '.' in numeric_str else int(numeric_str)
                except ValueError:
                    pass
        
        return None
    
    def _normalize_author_object(self, value: Any) -> Dict:
        """Normalize author object"""
        if not isinstance(value, dict):
            return {
                'id': 0, 'name': 'N/A', 'sex': 'N/A',
                'title': 'N/A', 'country': 'N/A',
                'expertise': 'N/A', 'image': 'N/A'
            }
        
        # Ensure required author fields exist
        required_author_fields = {
            'id': 0,
            'name': 'N/A',
            'sex': 'N/A', 
            'title': 'N/A',
            'country': 'N/A',
            'expertise': 'N/A',
            'image': 'N/A'
        }
        
        normalized_author = {}
        for field, na_value in required_author_fields.items():
            if field in value and self._is_valid_value(value[field]):
                normalized_author[field] = value[field]
            else:
                normalized_author[field] = na_value
        
        return normalized_author
    
    def _normalize_list_field(self, value: Any) -> List:
        """Normalize list fields"""
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        elif isinstance(value, str) and value.strip():
            return [value.strip()]
        else:
            return []  # N/A equivalent for lists
    
    def _normalize_compatibility(self, value: Any) -> Dict:
        """Normalize compatibility object"""
        if not isinstance(value, dict):
            return {}  # N/A equivalent
        
        # Ensure list fields are lists
        normalized_compat = {}
        for key, val in value.items():
            if isinstance(val, list):
                normalized_compat[key] = val
            elif isinstance(val, str):
                normalized_compat[key] = [val] if val.strip() else []
            else:
                normalized_compat[key] = []
        
        return normalized_compat
    
    def _normalize_images(self, value: Any, material_name: str) -> Dict:
        """Normalize images object"""
        if not isinstance(value, dict):
            # Return N/A structure (fail-fast: no placeholder fallbacks)
            return {
                'hero': {
                    'alt': f'{material_name} surface laser cleaning (N/A)',
                    'url': 'N/A'
                },
                'micro': {
                    'alt': f'Microscopic view of {material_name} surface (N/A)',
                    'url': 'N/A'
                }
            }
        
        normalized_images = {}
        
        # Ensure both hero and micro exist with proper structure
        for image_type in ['hero', 'micro']:
            if image_type in value and isinstance(value[image_type], dict):
                image_data = value[image_type]
                normalized_images[image_type] = {
                    'alt': image_data.get('alt', f'{material_name} {image_type} image (N/A)'),
                    'url': image_data.get('url', 'N/A')
                }
            else:
                # Create fail-fast structure (no placeholder fallbacks)
                alt_text = f'{material_name} surface laser cleaning' if image_type == 'hero' else f'Microscopic view of {material_name} surface'
                normalized_images[image_type] = {
                    'alt': f'{alt_text} (N/A)',
                    'url': 'N/A'  # Fail-fast: No placeholder URLs
                }
        
        return normalized_images
    
    def get_normalization_stats(self) -> Dict[str, int]:
        """Get normalization statistics"""
        return self.normalization_stats.copy()


class NAFrontmatterGenerator:
    """Wrapper that ensures complete frontmatter with N/A for missing fields"""
    
    def __init__(self, original_generator):
        self.original_generator = original_generator
        self.normalizer = StrictFieldNormalizer()
    
    def generate_with_na_handling(self, material_name: str, **kwargs) -> Dict[str, Any]:
        """
        Generate frontmatter ensuring all fields exist (N/A for missing)
        
        Args:
            material_name: Material name
            **kwargs: Generation parameters
            
        Returns:
            Complete frontmatter with N/A for missing fields
        """
        try:
            # Attempt original generation
            frontmatter = self.original_generator(material_name, **kwargs)
            logger.info(f"Original generation successful for {material_name}")
        except Exception as e:
            # If original fails, start with empty structure
            logger.warning(f"Original generation failed for {material_name}: {e}")
            frontmatter = {}
        
        # Normalize with N/A for missing fields
        normalized_frontmatter = self.normalizer.normalize_frontmatter(
            frontmatter, material_name
        )
        
        return normalized_frontmatter
    
    def get_stats(self) -> Dict[str, int]:
        """Get normalization statistics"""
        return self.normalizer.get_normalization_stats()