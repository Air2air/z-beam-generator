#!/usr/bin/env python3
"""
Pipeline Integration - Validation and Quality Improvement

Provides real-time validation and improvement of generated content.
Integrates with Materials.yaml and Categories.yaml for data consistency.
"""

import yaml
from pathlib import Path


def validate_material_pre_generation(material_name: str) -> dict:
    """
    Validate material data before generation.
    
    Args:
        material_name: Name of material to validate
        
    Returns:
        dict with validation results
    """
    issues = []
    warnings = []
    errors = []
    
    try:
        # Load Materials.yaml
        materials_path = Path("data/Materials.yaml")
        if not materials_path.exists():
            errors.append("Materials.yaml not found")
            return {
                "validation_passed": False,
                "material": material_name,
                "issues_detected": issues,
                "warnings": warnings,
                "errors": errors
            }
        
        with open(materials_path, 'r') as f:
            materials_data = yaml.safe_load(f)
        
        # Check if material exists in material_index
        material_index = materials_data.get('material_index', {})
        if material_name not in material_index:
            errors.append(f"Material '{material_name}' not found in Materials.yaml")
            return {
                "validation_passed": False,
                "material": material_name,
                "issues_detected": issues,
                "warnings": warnings,
                "errors": errors
            }
        
        # Get material category
        category = material_index[material_name]
        
        # Find material properties
        materials_section = materials_data.get('materials', {})
        material_found = False
        material_properties = {}
        
        if category in materials_section:
            for item in materials_section[category].get('items', []):
                if item.get('name') == material_name:
                    material_found = True
                    material_properties = item.get('properties', {})
                    break
        
        if not material_found:
            errors.append(f"Material '{material_name}' found in index but not in materials section")
        
        # Validate critical properties exist
        critical_properties = ['density', 'thermalConductivity', 'hardness']
        missing_properties = [prop for prop in critical_properties if prop not in material_properties]
        
        if missing_properties:
            warnings.append(f"Missing critical properties: {', '.join(missing_properties)}")
            issues.extend(missing_properties)
        
        # Check property confidence levels
        low_confidence_props = []
        for prop_name, prop_data in material_properties.items():
            if isinstance(prop_data, dict):
                confidence = prop_data.get('confidence', 0)
                if confidence < 70:
                    low_confidence_props.append(f"{prop_name} ({confidence}%)")
        
        if low_confidence_props:
            warnings.append(f"Low confidence properties: {', '.join(low_confidence_props)}")
        
        validation_passed = len(errors) == 0
        
        return {
            "validation_passed": validation_passed,
            "material": material_name,
            "category": category,
            "properties_count": len(material_properties),
            "issues_detected": issues,
            "warnings": warnings,
            "errors": errors
        }
        
    except Exception as e:
        return {
            "validation_passed": False,
            "material": material_name,
            "issues_detected": issues,
            "warnings": warnings,
            "errors": [f"Validation error: {str(e)}"]
        }


def validate_and_improve_frontmatter(material_name: str, frontmatter_content: dict) -> dict:
    """
    Validate and improve generated frontmatter.
    
    Args:
        material_name: Name of material
        frontmatter_content: Generated frontmatter content as dict
        
    Returns:
        dict with validation/improvement results
    """
    improvements = []
    issues_detected = []
    errors = []
    improvements_made = False
    
    try:
        # Validate required fields
        required_fields = ['name', 'category', 'title', 'description', 'materialProperties', 'applications']
        missing_fields = [field for field in required_fields if field not in frontmatter_content]
        
        if missing_fields:
            issues_detected.extend(missing_fields)
            errors.append(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Check material properties completeness
        if 'materialProperties' in frontmatter_content:
            props = frontmatter_content['materialProperties']
            if len(props) < 5:
                issues_detected.append("Insufficient materialProperties (need at least 5)")
        
        # Check applications completeness and structure
        if 'applications' in frontmatter_content:
            apps = frontmatter_content['applications']
            if isinstance(apps, list):
                # Check count (relaxed minimum to match Gallium reference)
                if len(apps) < 2:
                    issues_detected.append(f"Insufficient applications ({len(apps)}, minimum 2)")
                    errors.append("CRITICAL: Need at least 2 applications")
                elif len(apps) < 3:
                    improvements.append(f"Consider adding more applications (currently {len(apps)}, target 3-5)")
                
                # NEW FORMAT: Applications are simple strings like "Aerospace: Description"
                # Validate string format
                for idx, app in enumerate(apps):
                    if isinstance(app, str):
                        # Applications should be simple industry names (no descriptions/colons)
                        if ':' in app:
                            issues_detected.append(f"Application {idx+1} contains colon (old format) - should be simple industry name only")
                            improvements.append("Remove descriptions from applications - use industry names only")
                        elif len(app.strip()) < 3:
                            issues_detected.append(f"Application {idx+1} name too short (need 3+ chars)")
                    elif isinstance(app, dict):
                        # OLD FORMAT WARNING: Should be strings now
                        issues_detected.append(f"Application {idx+1} is dict (old format) - should be simple string")
                        improvements.append("Convert structured application objects to simple strings")
        else:
            issues_detected.append("Missing applications field")
            errors.append("CRITICAL: applications field is required")
        
        # Check if tags field exists and has content
        if 'tags' in frontmatter_content:
            tags = frontmatter_content['tags']
            if isinstance(tags, list):
                if len(tags) < 4:
                    issues_detected.append(f"Insufficient tags ({len(tags)}, minimum 4)")
                elif len(tags) > 10:
                    issues_detected.append(f"Too many tags ({len(tags)}, maximum 10)")
        else:
            issues_detected.append("Missing tags field")
        
        # Check image paths
        if 'images' in frontmatter_content:
            images = frontmatter_content['images']
            if isinstance(images, dict):
                for img_type in ['hero', 'micro']:
                    if img_type in images:
                        img_data = images[img_type]
                        if isinstance(img_data, dict) and 'url' in img_data:
                            url = img_data['url']
                            if not url.startswith('/images/material/'):
                                issues_detected.append(f"Incorrect image path format: {url}")
                                improvements.append(f"Fix {img_type} image path to use /images/material/ prefix")
        
        validation_passed = len(errors) == 0
        
        return {
            "validation_passed": validation_passed,
            "validation_result": {  # Add nested validation_result for backward compatibility
                "validation_passed": validation_passed,
                "issues_detected": issues_detected
            },
            "material": material_name,
            "improvements": improvements,
            "improvements_made": improvements_made,
            "issues_detected": issues_detected,
            "errors": errors,
            "properties_count": len(frontmatter_content.get('materialProperties', {})),
            "applications_count": len(frontmatter_content.get('applications', [])),
            "tags_count": len(frontmatter_content.get('tags', []))
        }
        
    except Exception as e:
        return {
            "validation_passed": False,
            "validation_result": {  # Add this key for consistency
                "validation_passed": False,
                "issues_detected": issues_detected + [f"Validation error: {str(e)}"]
            },
            "material": material_name,
            "improvements": improvements,
            "improvements_made": False,
            "issues_detected": issues_detected,
            "errors": [f"Validation error: {str(e)}"]
        }


def validate_batch_generation(materials: list) -> dict:
    """
    Validate batch generation setup.
    
    Args:
        materials: List of material names to validate
        
    Returns:
        dict with batch validation results
    """
    warnings = []
    errors = []
    validated_materials = []
    
    try:
        # Load Materials.yaml
        materials_path = Path("data/Materials.yaml")
        if not materials_path.exists():
            return {
                "valid": False,
                "total_materials": len(materials),
                "validated_materials": 0,
                "warnings": warnings,
                "errors": ["Materials.yaml not found"]
            }
        
        with open(materials_path, 'r') as f:
            materials_data = yaml.safe_load(f)
        
        material_index = materials_data.get('material_index', {})
        
        # Validate each material
        for material_name in materials:
            if material_name not in material_index:
                warnings.append(f"Material '{material_name}' not found in Materials.yaml")
            else:
                validated_materials.append(material_name)
        
        # Check batch size
        if len(materials) > 50:
            warnings.append(f"Large batch size ({len(materials)} materials) - consider splitting for better error recovery")
        
        validation_rate = len(validated_materials) / len(materials) * 100 if materials else 0
        
        return {
            "valid": len(errors) == 0,
            "total_materials": len(materials),
            "validated_materials": len(validated_materials),
            "validation_rate": validation_rate,
            "warnings": warnings,
            "errors": errors
        }
        
    except Exception as e:
        return {
            "valid": False,
            "total_materials": len(materials),
            "validated_materials": 0,
            "warnings": warnings,
            "errors": [f"Batch validation error: {str(e)}"]
        }
