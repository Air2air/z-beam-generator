"""Schema parsing utilities for frontmatter generator."""

import logging
from typing import Dict, Any, List, Optional, Set, Union

logger = logging.getLogger(__name__)

class SchemaParser:
    """Parses schema structures for frontmatter generation."""
    
    def __init__(self, schema: Dict[str, Any], article_type: str, subject: str):
        """Initialize with schema and context."""
        self.schema = schema
        self.article_type = article_type
        self.subject = subject
    
    def get_schema_defined_fields(self) -> List[str]:
        """Extract all valid field names from the current schema definition."""
        try:
            allowed_fields: Set[str] = set()  # Using set to avoid duplicates
            
            profile = self.get_profile()
            if not profile:
                logger.warning("No profile found for field validation")
                return []
                
            # Extract fields from sections (if present)
            if "sections" in profile:
                for section_name in profile["sections"]:
                    allowed_fields.add(section_name)
                    
            # Extract fields from fieldsets
            if "fieldsets" in profile:
                for fieldset in profile["fieldsets"].values():
                    if "fields" in fieldset:
                        for field_name in fieldset["fields"]:
                            allowed_fields.add(field_name)
                            
            # Extract fields from direct fields structure
            if "fields" in profile:
                for field_name in profile["fields"]:
                    allowed_fields.add(field_name)
                    
            # Extract fields from legacy structure
            for key, value in profile.items():
                if isinstance(value, dict) and any(k in value for k in ["type", "description", "example"]):
                    allowed_fields.add(key)
                    
            # Always allow these core fields
            core_fields = ["name", "description", "author", "tags", "keywords"]
            for field in core_fields:
                allowed_fields.add(field)
                
            return list(allowed_fields)
        except Exception as e:
            logger.error(f"Error getting schema-defined fields: {e}")
            return []
    
    def get_required_fields(self) -> List[str]:
        """Get list of required fields from schema."""
        required_fields = []
        
        # Find the profile in the schema
        profile = self.get_profile()
        if not profile:
            return []
        
        # Extract required fields based on schema structure
        if "sections" in profile:
            for section_name, section in profile["sections"].items():
                if section.get("required", False):
                    required_fields.append(section_name)
        elif "fieldsets" in profile:
            for fieldset_name, fieldset in profile["fieldsets"].items():
                if "fields" in fieldset:
                    for field_name, field_def in fieldset["fields"].items():
                        if field_def.get("required", False):
                            required_fields.append(field_name)
        elif "fields" in profile:
            for field_name, field_def in profile["fields"].items():
                if field_def.get("required", False):
                    required_fields.append(field_name)
        
        # Always include these core fields
        core_fields = ["name", "description"]
        for field in core_fields:
            if field not in required_fields:
                required_fields.append(field)
                
        return required_fields
    
    def get_schema_version(self) -> str:
        """Get the schema version to handle migrations."""
        profile = self.get_profile()
        
        if profile and "version" in profile:
            return profile["version"]
        return "1.0"  # Default version
    
    def get_field_type(self, field_name: str) -> str:
        """Detect field type from schema."""
        field_def = self.get_field_definition(field_name)
        if not field_def:
            return "string"  # Default type
            
        return field_def.get("type", "string")
    
    def get_field_definition(self, field_name: str) -> Optional[Dict[str, Any]]:
        """Get field definition from schema."""
        profile = self.get_profile()
        if not profile:
            return None
            
        # Try different schema structures
        if "fieldsets" in profile:
            for fieldset in profile["fieldsets"].values():
                if "fields" in fieldset and field_name in fieldset["fields"]:
                    return fieldset["fields"][field_name]
        elif "fields" in profile:
            if field_name in profile["fields"]:
                return profile["fields"][field_name]
        else:
            # Legacy structure
            if field_name in profile and isinstance(profile[field_name], dict):
                return profile[field_name]
            elif "sections" in profile and field_name in profile["sections"]:
                return profile["sections"][field_name]
                
        return None
    
    def get_profile(self) -> Optional[Dict[str, Any]]:
        """Get the profile from schema."""
        profile_keys = [
            f"{self.article_type}Profile",
            "termProfile",
            f"{self.article_type}_profile",
            f"{self.article_type.title()}Profile",
            "schema"
        ]
        
        for key in profile_keys:
            if key in self.schema:
                return self.schema[key]
        
        return None