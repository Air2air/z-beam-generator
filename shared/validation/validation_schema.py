"""
Reference Validation Schema

Defines validation rules and field mappings for all domains.
"""

from typing import Dict, List


class ValidationSchema:
    """Central schema for reference validation"""
    
    # Map relationship fields to target domains
    FIELD_TO_DOMAIN = {
        # Materials relationships
        'related_contaminants': 'contaminants',
        'related_compounds': 'compounds',
        'related_settings': 'settings',
        
        # Contaminants relationships
        'related_materials': 'materials',
        'produces_compounds': 'compounds',
        'recommended_settings': 'settings',
        
        # Compounds relationships
        'produced_by_contaminants': 'contaminants',
        'related_materials': 'materials',
        
        # Settings relationships
        'suitable_materials': 'materials',
        'effective_contaminants': 'contaminants',
    }
    
    # Relationship fields by source domain
    DOMAIN_RELATIONSHIPS = {
        'materials': ['related_contaminants', 'related_compounds', 'related_settings', 'regulatory_standards'],
        'contaminants': ['related_materials', 'produces_compounds', 'recommended_settings'],
        'compounds': ['produced_by_contaminants', 'related_materials'],
        'settings': ['suitable_materials', 'effective_contaminants'],
    }
    
    # Bidirectional relationship pairs
    BIDIRECTIONAL_PAIRS = {
        ('materials', 'related_contaminants'): ('contaminants', 'related_materials'),
        ('materials', 'related_compounds'): ('compounds', 'related_materials'),
        ('materials', 'related_settings'): ('settings', 'suitable_materials'),
        ('contaminants', 'produces_compounds'): ('compounds', 'produced_by_contaminants'),
        ('contaminants', 'recommended_settings'): ('settings', 'effective_contaminants'),
    }
    
    # Suffix rules by domain
    DOMAIN_SUFFIXES = {
        'contaminants': '-contamination',
        # Add other domain suffixes as needed
    }
    
    # Required fields by domain
    REQUIRED_FIELDS = {
        'materials': ['name', 'category', 'title'],
        'contaminants': ['name', 'category'],
        'compounds': ['name', 'formula'],
        'settings': ['name', 'laser_type'],
    }
    
    # Optional fields that should be validated if present
    OPTIONAL_VALIDATED_FIELDS = {
        'materials': ['subcategory', 'author'],
        'contaminants': ['severity', 'typical_context'],
        'compounds': ['cas_number', 'health_hazards'],
        'settings': ['power_range', 'frequency_range'],
    }
    
    @classmethod
    def get_target_domain(cls, relationship_field: str) -> str:
        """Get target domain for a relationship field"""
        return cls.FIELD_TO_DOMAIN.get(relationship_field)
    
    @classmethod
    def get_relationships(cls, source_domain: str) -> List[str]:
        """Get all relationship fields for a domain"""
        if source_domain not in cls.DOMAIN_RELATIONSHIPS:
            raise ValueError(f"Unknown source domain for relationships: {source_domain}")
        return cls.DOMAIN_RELATIONSHIPS[source_domain]
    
    @classmethod
    def get_suffix(cls, domain: str) -> str:
        """Get required suffix for a domain (or empty string)"""
        if domain not in cls.DOMAIN_SUFFIXES:
            raise ValueError(f"Unknown domain for suffix lookup: {domain}")
        return cls.DOMAIN_SUFFIXES[domain]
    
    @classmethod
    def is_bidirectional(cls, source_domain: str, rel_field: str) -> bool:
        """Check if a relationship is bidirectional"""
        return (source_domain, rel_field) in cls.BIDIRECTIONAL_PAIRS
    
    @classmethod
    def get_reverse_relationship(cls, source_domain: str, rel_field: str) -> tuple:
        """Get the reverse relationship pair"""
        key = (source_domain, rel_field)
        if key not in cls.BIDIRECTIONAL_PAIRS:
            raise ValueError(
                f"No bidirectional reverse relationship configured for ({source_domain}, {rel_field})"
            )
        return cls.BIDIRECTIONAL_PAIRS[key]
