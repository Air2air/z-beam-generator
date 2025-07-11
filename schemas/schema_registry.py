#!/usr/bin/env python3
"""
Schema Registry - Uses single schema generator
"""
import logging
from typing import Dict, Any
from .schema_generator import create_schema

logger = logging.getLogger(__name__)

def get_schema(schema_type: str):
    """Get schema instance using single generator"""
    logger.info(f"📋 Creating schema for type: {schema_type}")
    
    try:
        schema = create_schema(schema_type)
        logger.info(f"✅ Schema created successfully: {schema_type}")
        return schema
    except Exception as e:
        logger.error(f"❌ Failed to create schema {schema_type}: {e}")
        raise

def list_available_schemas() -> list:
    """List all available schema types"""
    return ["thesaurus", "material", "application", "region"]

def validate_schema_type(schema_type: str) -> bool:
    """Validate if schema type is supported"""
    return schema_type in list_available_schemas()

def get_available_types() -> str:
    """Get comma-separated list of available types"""
    return ", ".join(list_available_schemas())


# Legacy compatibility - remove old registry class if it exists
class SchemaRegistry:
    """Legacy compatibility class - redirects to new functions"""
    
    def __init__(self):
        pass
    
    def get_schema(self, schema_type: str):
        """Legacy method - redirects to new function"""
        return get_schema(schema_type)
    
    def list_schemas(self) -> list:
        """Legacy method - redirects to new function"""
        return list_available_schemas()


# Remove any old registry instance
_registry = None