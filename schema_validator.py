"""Schema validator for ensuring complete field population."""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def validate_schema_completion(output: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """Validate that ALL schema fields are populated in the output."""
    errors = []
    
    try:
        # Check each section of the schema
        for section_name, section_schema in schema.items():
            if section_name.lower() in ["metadata", "tags", "jsonld"] or \
               "profile" in section_name.lower() or \
               "structured" in section_name.lower():
                
                # Get corresponding output section
                output_section = output.get(section_name.lower().replace("profile", ""))
                
                if not output_section:
                    errors.append(f"Missing output section: {section_name}")
                    continue
                
                # Validate all fields in this section
                section_errors = _validate_fields(output_section, section_schema, section_name)
                errors.extend(section_errors)
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info("Schema validation passed - all fields populated")
        else:
            logger.error(f"Schema validation failed with {len(errors)} errors")
            for error in errors:
                logger.error(f"  - {error}")
        
        return {
            "valid": is_valid,
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"Schema validation error: {e}", exc_info=True)
        return {
            "valid": False,
            "errors": [f"Validation exception: {str(e)}"]
        }

def _validate_fields(output_data: Any, schema_data: Any, path: str = "") -> List[str]:
    """Recursively validate that all schema fields are populated."""
    errors = []
    
    if isinstance(schema_data, dict):
        if not isinstance(output_data, dict):
            errors.append(f"Expected dict at {path}, got {type(output_data)}")
            return errors
        
        for key, value in schema_data.items():
            current_path = f"{path}.{key}" if path else key
            
            if key not in output_data:
                errors.append(f"Missing field: {current_path}")
                continue
            
            # Recursively validate nested structures
            nested_errors = _validate_fields(output_data[key], value, current_path)
            errors.extend(nested_errors)
    
    elif isinstance(schema_data, list):
        if not isinstance(output_data, list):
            errors.append(f"Expected list at {path}, got {type(output_data)}")
            return errors
        
        if len(output_data) == 0:
            errors.append(f"Empty list at {path}")
    
    else:
        # Leaf value - check if it's populated
        if output_data is None or output_data == "":
            errors.append(f"Empty value at {path}")
        elif isinstance(output_data, str) and output_data.strip() == "":
            errors.append(f"Empty string at {path}")
    
    return errors