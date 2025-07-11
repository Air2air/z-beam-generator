#!/usr/bin/env python3
"""
Schema Validator - Validates generated content against schema definitions
"""
import re
import json
import yaml
import logging
from typing import Dict, Any, List, Tuple

class SchemaValidator:
    """Validates generated articles against their schema definitions"""
    
    def __init__(self, logger=None):
        """Initialize the validator with optional logger"""
        self.logger = logger or logging.getLogger(__name__)
    
    def validate_article(self, article_content: str, schema_type: str, schema_definition: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate article content against schema definition
        
        Args:
            article_content: The full generated article content
            schema_type: Type of schema (application, material, etc.)
            schema_definition: The schema definition to validate against
            
        Returns:
            Tuple containing (is_valid, list_of_issues)
        """
        issues = []
        
        # Parse article sections
        sections = self._parse_article_sections(article_content)
        
        # Validate required sections
        required_sections = ["metadata", "title", "tags", "jsonld", "overview"]
        for section in required_sections:
            if section not in sections:
                issues.append(f"Missing required section: {section}")
        
        # If parsing failed, return early
        if issues:
            return False, issues
            
        # Validate metadata
        metadata_issues = self._validate_metadata(sections["metadata"], schema_type)
        issues.extend(metadata_issues)
        
        # Validate JSON-LD
        jsonld_issues = self._validate_jsonld(sections["jsonld"], schema_type, schema_definition)
        issues.extend(jsonld_issues)
        
        # Validate tags
        tag_issues = self._validate_tags(sections["tags"], schema_type, schema_definition)
        issues.extend(tag_issues)
        
        # Validate content sections
        content_issues = self._validate_content_sections(sections, schema_type, schema_definition)
        issues.extend(content_issues)
        
        # Return validation result
        is_valid = len(issues) == 0
        return is_valid, issues
    
    def _parse_article_sections(self, content: str) -> Dict[str, Any]:
        """Parse article into sections for validation"""
        sections = {}
        
        # Extract YAML frontmatter
        frontmatter_match = re.match(r'^---\s+(.*?)\s+---\s*', content, re.DOTALL)
        if frontmatter_match:
            frontmatter_text = frontmatter_match.group(1)
            try:
                sections["metadata"] = yaml.safe_load(frontmatter_text)
            except Exception as e:
                self.logger.error(f"Error parsing frontmatter: {e}")
                sections["metadata"] = {}
        else:
            sections["metadata"] = {}
        
        # Extract title
        title_match = re.search(r'# (.*?)(?:\n|$)', content)
        if title_match:
            sections["title"] = title_match.group(1)
        
        # Extract tags
        tags_section = re.search(r'## Tags\s+(.*?)(?=##|\Z)', content, re.DOTALL)
        if tags_section:
            sections["tags"] = tags_section.group(1).strip()
        
        # Extract JSON-LD
        jsonld_match = re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', content, re.DOTALL)
        if jsonld_match:
            try:
                sections["jsonld"] = json.loads(jsonld_match.group(1))
            except json.JSONDecodeError:
                self.logger.error("Invalid JSON-LD in article")
                sections["jsonld"] = {}
        
        # Extract overview
        overview_match = re.search(r'## Overview\s+(.*?)(?=##|\Z)', content, re.DOTALL)
        if overview_match:
            sections["overview"] = overview_match.group(1).strip()
        
        # Extract other content sections
        section_matches = re.finditer(r'## ([^#\n]+)\s+(.*?)(?=##|\Z)', content, re.DOTALL)
        for match in section_matches:
            section_name = match.group(1).strip()
            section_content = match.group(2).strip()
            if section_name.lower() not in ["tags", "overview", "json-ld structured data"]:
                sections[section_name.lower()] = section_content
        
        return sections
    
    def _validate_metadata(self, metadata: Dict[str, Any], schema_type: str) -> List[str]:
        """Validate article metadata"""
        issues = []
        
        # Check required metadata fields
        required_fields = ["title", "articleType", "author", "generatedAt"]
        for field in required_fields:
            if field not in metadata:
                issues.append(f"Missing required metadata field: {field}")
        
        # Check article type matches schema type
        if "articleType" in metadata and metadata["articleType"] != schema_type:
            issues.append(f"Metadata articleType '{metadata['articleType']}' does not match schema type '{schema_type}'")
        
        return issues
    
    def _validate_jsonld(self, jsonld: Dict[str, Any], schema_type: str, schema_definition: Dict[str, Any]) -> List[str]:
        """Validate JSON-LD structure"""
        issues = []
        
        # Check required JSON-LD fields
        required_fields = ["@context", "@type", "name"]
        for field in required_fields:
            if field not in jsonld:
                issues.append(f"Missing required JSON-LD field: {field}")
        
        # Check @context is schema.org
        if "@context" in jsonld and jsonld["@context"] != "https://schema.org":
            issues.append(f"JSON-LD @context should be 'https://schema.org', found '{jsonld['@context']}'")
        
        # Check type is appropriate for schema type
        expected_type = self._get_expected_jsonld_type(schema_type)
        if "@type" in jsonld and jsonld["@type"] != expected_type:
            issues.append(f"JSON-LD @type should be '{expected_type}' for {schema_type}, found '{jsonld['@type']}'")
        
        return issues
    
    def _validate_tags(self, tags: str, schema_type: str, schema_definition: Dict[str, Any]) -> List[str]:
        """Validate article tags"""
        issues = []
        
        # Check if tags exist
        if not tags:
            issues.append("Tags section is empty")
            return issues
        
        # Check tags format (default to hash format)
        if not tags.startswith("#"):
            issues.append("Tags should be in hash format (#tag)")
        
        # Check number of tags
        tag_count = len(re.findall(r'#\w+', tags))
        if tag_count < 3:
            issues.append(f"Too few tags: found {tag_count}, minimum 3 recommended")
        
        return issues
    
    def _validate_content_sections(self, sections: Dict[str, Any], schema_type: str, schema_definition: Dict[str, Any]) -> List[str]:
        """Validate article content sections against schema"""
        issues = []
        
        # Check if overview exists and has content
        if "overview" not in sections:
            issues.append("Missing overview section")
        elif not sections["overview"]:
            issues.append("Overview section is empty")
        
        # Check for required sections based on schema type
        if schema_type == "material":
            required_sections = ["properties", "applications", "specifications"]
            for section in required_sections:
                if section not in sections:
                    issues.append(f"Missing required section for material: {section}")
        
        elif schema_type == "application":
            required_sections = ["benefits", "process", "case studies"]
            for section in required_sections:
                if section not in sections:
                    issues.append(f"Missing required section for application: {section}")
        
        return issues
    
    def _get_expected_jsonld_type(self, schema_type: str) -> str:
        """Get expected JSON-LD @type based on schema type"""
        type_mapping = {
            "application": "TechnicalArticle",
            "material": "Product",
            "region": "Place",
            "thesaurus": "DefinedTerm"
        }
        return type_mapping.get(schema_type, "Article")