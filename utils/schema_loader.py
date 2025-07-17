"""Schema loading utilities."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("z-beam")

def load_schema(article_type: str) -> Optional[Dict[str, Any]]:
    """Load schema for the given article type."""
    schema_mapping = {
        "application": "schemas/definitions/application.json",
        "material": "schemas/definitions/material.json",
        "region": "schemas/definitions/region.json", 
        "thesaurus": "schemas/definitions/thesaurus.json"
    }
    
    profile_key_mapping = {
        "application": "applicationProfile",
        "material": "materialProfile",
        "region": "regionProfile",
        "thesaurus": "termProfile" 
    }
    
    schema_path = schema_mapping.get(article_type)
    if not Path(schema_path).exists():
        logger.error(f"Schema file not found: {schema_path}")
        return None
    
    try:
        with open(schema_path, 'r') as f:
            raw_schema = json.load(f)
        
        profile_key = profile_key_mapping.get(article_type)
        
        if profile_key in raw_schema:
            return raw_schema
        elif article_type in raw_schema:
            return {profile_key: raw_schema[article_type]}
        elif f"{article_type}Profile" in raw_schema:
            return {profile_key: raw_schema[f"{article_type}Profile"]}
        else:
            logger.error(f"Schema structure not recognized")
            return None
    except Exception as e:
        logger.error(f"Failed to load schema: {e}")
        return None