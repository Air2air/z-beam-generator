"""
Validation functions for metatags.
"""

def validate_article_specific_fields(article_type: str, category: str, parsed: dict) -> None:
    """
    Validates article-specific fields in the metatags.
    
    Args:
        article_type: Type of article (material, application, region, thesaurus)
        category: Category of article (metal, ceramic, etc.)
        parsed: Parsed YAML content
        
    Raises:
        ValueError: If validation fails
    """
    if article_type == "material":
        # For material articles, validate material-specific fields
        if 'application' in parsed:
            # Fix application if it's not properly structured
            if not isinstance(parsed['application'], dict):
                # Convert string or other types to proper dict structure
                if isinstance(parsed['application'], str):
                    parsed['application'] = {
                        'name': parsed['application'],
                        'description': f"Application of laser cleaning technology for {parsed['application']}."
                    }
                else:
                    # Create a default application object
                    subject = parsed.get('title', '').split(' ')[0] if 'title' in parsed else "Material"
                    parsed['application'] = {
                        'name': f"{subject} Laser Cleaning",
                        'description': f"Removal of contaminants, oxides, and coatings from surfaces using high-precision laser technology."
                    }
            
            # Ensure required fields exist in application object
            if 'name' not in parsed['application']:
                parsed['application']['name'] = "Laser Cleaning Application"
            
            if 'description' not in parsed['application']:
                parsed['application']['description'] = "Application of laser cleaning technology for surface preparation and contamination removal."
            
        if 'properties' in parsed:
            if not isinstance(parsed['properties'], dict):
                raise ValueError("'properties' must be an object")
                
            # Check for required properties based on material type
            if category in ["metal", "ceramic", "semiconductor"]:
                required_props = ["density", "meltingPoint", "thermalConductivity"]
                missing_props = [prop for prop in required_props if prop not in parsed['properties']]
                if missing_props:
                    raise ValueError(f"Missing required properties for {category}: {missing_props}")
        
        if 'chemicalProperties' in parsed:
            if not isinstance(parsed['chemicalProperties'], dict):
                raise ValueError("'chemicalProperties' must be an object")
            
            required_chem_props = ["symbol", "formula", "materialType"]
            missing_chem_props = [prop for prop in required_chem_props if prop not in parsed['chemicalProperties']]
            if missing_chem_props:
                raise ValueError(f"Missing required chemical properties: {missing_chem_props}")
                
    elif article_type == "application":
        # For application articles, validate application-specific fields
        if 'technicalSpecifications' in parsed and not isinstance(parsed['technicalSpecifications'], dict):
            raise ValueError("'technicalSpecifications' must be an object")
            
        if 'challenges' in parsed and not isinstance(parsed['challenges'], (list, dict)):
            raise ValueError("'challenges' must be an array or object")
            
    elif article_type == "region":
        # For region articles, validate region-specific fields
        if 'countries' in parsed and not isinstance(parsed['countries'], list):
            raise ValueError("'countries' must be an array")
            
        if 'geoCoordinates' in parsed and not isinstance(parsed['geoCoordinates'], dict):
            raise ValueError("'geoCoordinates' must be an object with 'latitude' and 'longitude'")
            
    # Add validation for thesaurus articles if needed
