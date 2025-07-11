#!/usr/bin/env python3
"""
Configuration Validator for Z-Beam Generator
Validates that the system is properly configured
"""

import os
import json
import yaml
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_system_config():
    """
    Validate the entire system configuration
    """
    logger.info("Validating Z-Beam Generator configuration...")
    
    issues = []
    
    # Check technical config
    tech_config_issues = validate_technical_config()
    issues.extend(tech_config_issues)
    
    # Check schema definitions
    schema_issues = validate_schema_definitions()
    issues.extend(schema_issues)
    
    # Check authors
    author_issues = validate_authors()
    issues.extend(author_issues)
    
    # Report validation results
    if issues:
        logger.error(f"Configuration validation failed with {len(issues)} issues:")
        for i, issue in enumerate(issues, 1):
            logger.error(f"Issue {i}: {issue}")
        return False
    else:
        logger.info("Configuration validation successful! System is properly configured.")
        return True

def validate_technical_config() -> List[str]:
    """
    Validate technical configuration
    
    Returns:
        List of validation issues
    """
    issues = []
    
    # Check if technical config exists
    config_file = "config/technical_config.json"
    if not os.path.exists(config_file):
        issues.append(f"Technical config file not found: {config_file}")
        return issues
    
    # Load technical config
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        issues.append(f"Invalid technical config JSON: {e}")
        return issues
    
    # Check required sections
    required_sections = ["tags", "jsonld", "metadata"]
    for section in required_sections:
        if section not in config:
            issues.append(f"Missing required section '{section}' in technical config")
    
    return issues

def validate_schema_definitions() -> List[str]:
    """
    Validate schema definitions
    
    Returns:
        List of validation issues
    """
    issues = []
    
    # Check if schema directory exists
    schema_dir = "schemas/definitions"
    if not os.path.exists(schema_dir):
        issues.append(f"Schema directory not found: {schema_dir}")
        return issues
    
    # Expected schema types
    expected_schemas = ["application", "material", "region", "thesaurus"]
    found_schemas = []
    
    # Check each schema file
    for schema_type in expected_schemas:
        schema_file = f"{schema_type}_schema_definition.md"
        schema_path = os.path.join(schema_dir, schema_file)
        
        if not os.path.exists(schema_path):
            issues.append(f"Schema definition not found: {schema_path}")
            continue
            
        found_schemas.append(schema_type)
        
        # Validate schema content
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                content = f.read()
                schema_def = yaml.safe_load(content)
                
                # Check required sections
                if "schemaVersion" not in schema_def:
                    issues.append(f"Missing 'schemaVersion' in {schema_file}")
                
                if "schemaType" not in schema_def:
                    issues.append(f"Missing 'schemaType' in {schema_file}")
                
                # Check for generator config
                if "generatorConfig" not in schema_def:
                    issues.append(f"Missing 'generatorConfig' in {schema_file}")
                else:
                    generator_config = schema_def["generatorConfig"]
                    
                    # Check for required generator configs
                    for generator_type in ["tags", "jsonld", "metadata"]:
                        if generator_type not in generator_config:
                            issues.append(f"Missing '{generator_type}' config in {schema_file}")
                
                # Check for profile section based on schema type
                profile_section = f"{schema_type}Profile"
                if profile_section not in schema_def:
                    issues.append(f"Missing '{profile_section}' in {schema_file}")
                    
        except yaml.YAMLError as e:
            issues.append(f"Invalid YAML in {schema_file}: {e}")
        except Exception as e:
            issues.append(f"Error validating {schema_file}: {e}")
    
    # Report on found schemas
    logger.info(f"Found {len(found_schemas)}/{len(expected_schemas)} schema definitions: {', '.join(found_schemas)}")
    
    return issues

def validate_authors() -> List[str]:
    """
    Validate author profiles
    
    Returns:
        List of validation issues
    """
    issues = []
    
    # Check if authors file exists
    authors_file = "authors/authors.json"
    if not os.path.exists(authors_file):
        issues.append(f"Authors file not found: {authors_file}")
        return issues
    
    # Load authors
    try:
        with open(authors_file, 'r', encoding='utf-8') as f:
            authors = json.load(f)
    except json.JSONDecodeError as e:
        issues.append(f"Invalid authors JSON: {e}")
        return issues
    
    # Check if authors list is empty
    if not authors:
        issues.append("Authors list is empty")
        return issues
    
    # Validate each author
    for i, author in enumerate(authors):
        # Check required fields
        required_fields = ["id", "name", "title", "country"]
        for field in required_fields:
            if field not in author:
                issues.append(f"Author at index {i} missing required field: {field}")
    
    return issues

if __name__ == "__main__":
    validate_system_config()