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
            
            # Check for nested profile structure
            if "profile" in profile:
                logger.info("Found nested profile structure")
                fields_profile = profile["profile"]
            else:
                fields_profile = profile
                
            # Extract fields from sections (if present)
            if "sections" in fields_profile:
                logger.debug(f"Processing {len(fields_profile['sections'])} sections")
                for section_name in fields_profile["sections"]:
                    allowed_fields.add(section_name)
                    
            # Extract fields from fieldsets
            if "fieldsets" in fields_profile:
                logger.debug(f"Processing {len(fields_profile['fieldsets'])} fieldsets")
                for fieldset_name, fieldset in fields_profile["fieldsets"].items():
                    if "fields" in fieldset:
                        for field_name in fieldset["fields"]:
                            allowed_fields.add(field_name)
                            
            # Extract fields from direct fields structure
            if "fields" in fields_profile:
                logger.debug(f"Processing {len(fields_profile['fields'])} direct fields")
                for field_name in fields_profile["fields"]:
                    allowed_fields.add(field_name)
                    
            # Extract fields from legacy structure - direct field definitions
            direct_field_count = 0
            for key, value in fields_profile.items():
                if isinstance(value, dict) and any(k in value for k in ["type", "description", "example"]):
                    allowed_fields.add(key)
                    direct_field_count += 1
            logger.debug(f"Found {direct_field_count} direct field definitions")
            
            # Get validation-defined required fields (no hardcoded fallbacks)
            validation_fields = self._get_validation_required_fields(profile)
            for field in validation_fields:
                allowed_fields.add(field)
                
            logger.info(f"Found {len(allowed_fields)} total schema-defined fields")
            return list(allowed_fields)
        except Exception as e:
            logger.error(f"Error getting schema-defined fields: {e}", exc_info=True)
            return []
    
    def get_required_fields(self) -> List[str]:
        """Get required fields directly from schema, with no hardcoded values."""
        required_fields = []
        
        # Find the profile in the schema
        profile = self.get_profile()
        if not profile:
            logger.warning("No profile found for required fields")
            return []
        
        # Try to get validation-defined required fields first
        validation_fields = self._get_validation_required_fields(profile)
        if validation_fields:
            logger.info(f"Using {len(validation_fields)} validation-defined required fields")
            return validation_fields
        
        # If no validation section, fall back to scanning field definitions
        logger.info("No validation section found, scanning field definitions")
        
        # Get field profile (handle nested structure)
        if "profile" in profile:
            fields_profile = profile["profile"]
            logger.info("Using nested profile structure for fields")
        else:
            fields_profile = profile
            logger.info("Using direct profile structure for fields")

        # Scan all field definitions for required fields
        self._scan_fields_for_required(fields_profile, "", required_fields)

        logger.info(f"Found {len(required_fields)} required fields in schema")
        return required_fields
    
    def _scan_fields_for_required(self, obj: Dict[str, Any], path: str, required_fields: List[str]) -> None:
        """Recursively scan object for required fields."""
        if not isinstance(obj, dict):
            return
            
        # Check if this object itself is a field definition
        if "type" in obj and "required" in obj and obj["required"] is True:
            if path:  # Don't add empty path
                required_fields.append(path)
                logger.debug(f"Found required field: {path}")
            
        # Process fieldsets if present
        if "fieldsets" in obj:
            for fieldset_name, fieldset in obj["fieldsets"].items():
                if "fields" in fieldset:
                    for field_name, field_def in fieldset["fields"].items():
                        new_path = field_name
                        if isinstance(field_def, dict) and field_def.get("required", False):
                            required_fields.append(new_path)
                            logger.debug(f"Found required field in fieldset: {new_path}")
                
        # Process direct fields
        for key, value in obj.items():
            if isinstance(value, dict):
                if "type" in value and value.get("required", False):
                    new_path = key if not path else f"{path}.{key}"
                    if new_path not in required_fields:
                        required_fields.append(key)  # Just add the field name without path
                        logger.debug(f"Found required field: {key} (from {new_path})")
                        
                # If this is an object with properties, check those too
                if "properties" in value and isinstance(value["properties"], dict):
                    for prop_name, prop_def in value["properties"].items():
                        if isinstance(prop_def, dict) and prop_def.get("required", False):
                            # We don't need to build nested paths for frontmatter
                            required_fields.append(key)  # Add the parent field
                            logger.debug(f"Found object with required properties: {key}")
                            break  # Only need to add the parent field once
                
                # Recursively scan nested objects, excluding certain keys
                if key not in ["type", "description", "example", "properties"]:
                    new_path = key if not path else f"{path}.{key}"
                    self._scan_fields_for_required(value, new_path, required_fields)
    
    def _get_validation_required_fields(self, profile: Dict[str, Any]) -> List[str]:
        """Get required fields from validation section with multiple path checking."""
        # Check multiple possible paths for validation section
        validation_paths = [
            ["validation", "frontmatter", "requiredFields"],
            ["validation", "requiredFields"],
            ["frontmatter", "requiredFields"],
            ["requiredFields"]
        ]
        
        # Also check in profile subsection if it exists
        if "profile" in profile and isinstance(profile["profile"], dict):
            nested_profile = profile["profile"]
            for path in validation_paths:
                # Try to navigate the path in the nested profile
                current = nested_profile
                valid_path = True
                for key in path:
                    if key not in current:
                        valid_path = False
                        break
                    current = current[key]
                
                if valid_path and isinstance(current, list):
                    logger.info(f"Found validation requiredFields in profile.{'.'.join(path)}")
                    return current
        
        # Try each path
        for path in validation_paths:
            # Try to navigate the path
            current = profile
            valid_path = True
            for key in path:
                if key not in current:
                    valid_path = False
                    break
                current = current[key]
            
            if valid_path and isinstance(current, list):
                logger.info(f"Found validation requiredFields in {'.'.join(path)}")
                return current
        
        return []
    
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
        
        # Check for nested profile
        if "profile" in profile and isinstance(profile["profile"], dict):
            fields_profile = profile["profile"]
        else:
            fields_profile = profile
            
        # Try different schema structures
        if "fieldsets" in fields_profile:
            for fieldset in fields_profile["fieldsets"].values():
                if "fields" in fieldset and field_name in fieldset["fields"]:
                    return fieldset["fields"][field_name]
        elif "fields" in fields_profile:
            if field_name in fields_profile["fields"]:
                return fields_profile["fields"][field_name]
        else:
            # Legacy structure - direct field definition
            if field_name in fields_profile and isinstance(fields_profile[field_name], dict):
                return fields_profile[field_name]
            elif "sections" in fields_profile and field_name in fields_profile["sections"]:
                return fields_profile["sections"][field_name]
                
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
                logger.info(f"Found schema profile using key: {key}")
                return self.schema[key]
        
        # Log available keys for debugging
        logger.warning(f"No matching profile found. Available keys: {list(self.schema.keys())}")
        return None
    
    def get_default_display_config(self):
        """Get the default display configuration from schema."""
        base_profile = self.schema.get("baseProfile", {})
        return base_profile.get("defaultDisplayConfig", {})