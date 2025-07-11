#!/usr/bin/env python3
"""
Tag Generator - No fallbacks, 100% schema-driven
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class TagGenerator:
    """Tag generator - 100% schema-driven, no defaults"""
    
    def __init__(self, tag_rules: Dict[str, Any]):
        self.tag_rules = tag_rules
        self._validate_tag_rules()
    
    def _validate_tag_rules(self):
        """Validate tag rules - no fallbacks"""
        required_fields = ["base_tags", "metadata_fields", "search_fields", "max_tags", "format"]
        
        for field in required_fields:
            if field not in self.tag_rules:
                raise ValueError(f"Tag rules missing required field: {field}")
        
        # Validate field types
        if not isinstance(self.tag_rules["base_tags"], list):
            raise ValueError("Tag rules base_tags must be a list")
        
        if not isinstance(self.tag_rules["metadata_fields"], list):
            raise ValueError("Tag rules metadata_fields must be a list")
        
        if not isinstance(self.tag_rules["search_fields"], list):
            raise ValueError("Tag rules search_fields must be a list")
        
        if not isinstance(self.tag_rules["max_tags"], int):
            raise ValueError("Tag rules max_tags must be an integer")
        
        if self.tag_rules["format"] not in ["hash", "plain", "array"]:
            raise ValueError("Tag rules format must be 'hash', 'plain', or 'array'")
    
    def generate_tags(self, metadata: Dict[str, Any]) -> List[str]:
        """Generate tags from metadata - no fallbacks"""
        logger.info("🏷️ Generating tags from metadata")
        
        tags = set()
        
        # Add base tags
        tags.update(self.tag_rules["base_tags"])
        
        # Add tags from metadata fields
        for field_name in self.tag_rules["metadata_fields"]:
            if field_name not in metadata:
                raise ValueError(f"Required metadata field for tags not found: {field_name}")
            
            field_value = metadata[field_name]
            if isinstance(field_value, str):
                tags.add(field_value)
            elif isinstance(field_value, list):
                tags.update(field_value)
            else:
                tags.add(str(field_value))
        
        # Add search-based tags
        self._add_search_tags(tags, metadata)
        
        # Apply term mapping
        self._apply_term_mapping(tags, metadata)
        
        # Limit tags
        tag_list = list(tags)
        if len(tag_list) > self.tag_rules["max_tags"]:
            tag_list = tag_list[:self.tag_rules["max_tags"]]
        
        logger.info(f"🏷️ Generated {len(tag_list)} tags")
        return tag_list
    
    def _add_search_tags(self, tags: set, metadata: Dict[str, Any]):
        """Add tags based on search fields"""
        for field_name in self.tag_rules["search_fields"]:
            if field_name not in metadata:
                raise ValueError(f"Required search field for tags not found: {field_name}")
            
            field_value = str(metadata[field_name]).lower()
            
            # Search for matches in term mapping
            if "term_mapping" in self.tag_rules:
                for term, mapped_tags in self.tag_rules["term_mapping"].items():
                    if term.lower() in field_value:
                        if isinstance(mapped_tags, list):
                            tags.update(mapped_tags)
                        else:
                            tags.add(mapped_tags)
    
    def _apply_term_mapping(self, tags: set, metadata: Dict[str, Any]):
        """Apply term mapping transformations"""
        if "term_mapping" not in self.tag_rules:
            return
        
        # Create a copy to avoid modifying set during iteration
        current_tags = tags.copy()
        
        for tag in current_tags:
            tag_lower = tag.lower()
            if tag_lower in self.tag_rules["term_mapping"]:
                mapped_tags = self.tag_rules["term_mapping"][tag_lower]
                if isinstance(mapped_tags, list):
                    tags.update(mapped_tags)
                else:
                    tags.add(mapped_tags)
    
    def format_tags(self, tags: List[str]) -> str:
        """Format tags according to schema rules"""
        if not tags:
            raise ValueError("No tags provided for formatting")
        
        tag_format = self.tag_rules["format"]
        
        if tag_format == "hash":
            return " ".join(f"#{tag}" for tag in tags)
        elif tag_format == "plain":
            return " ".join(tags)
        elif tag_format == "array":
            return str(tags)
        else:
            raise ValueError(f"Unknown tag format: {tag_format}")