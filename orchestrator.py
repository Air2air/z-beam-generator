#!/usr/bin/env python3
"""
Schema-Driven Article Orchestrator
Assembles components from schema generators with mandatory validation
"""

import logging
import os
import re
from datetime import datetime
from typing import Dict, Any, Tuple, List
# Import the validator
from utils.schema_validator import SchemaValidator

class ArticleOrchestrator:
    """
    Orchestrator that assembles components from schema generators
    with mandatory validation against schema definitions
    """
    
    def __init__(self, logger=None):
        """Initialize orchestrator with logger and validator."""
        self.logger = logger or logging.getLogger(__name__)
        self.validator = SchemaValidator(self.logger)
        # Track validation status
        self.last_validation_result = None
        self.last_validation_issues = []
        # Track generation issues
        self.generation_issues = []

    def assemble_article(self, generation_result: Dict[str, Any]) -> str:
        """Assemble article from schema generator components with validation."""
        self.logger.info("Assembling article from schema components")
        
        # Reset generation issues
        self.generation_issues = []
        
        # Check for generation issues in the result
        if "errors" in generation_result:
            for error in generation_result["errors"]:
                self.generation_issues.append(error)
                self.logger.warning(f"Generation issue: {error}")
        
        # Extract components
        components = generation_result["components"]
        
        # Get individual components
        metadata = components["metadata"]
        tags = components["tags"] 
        json_ld = components["json_ld"]
        schema_type = components["schema_type"]
        subject = components["subject"]
        schema = components.get("schema", {})
        content_sections = components.get("content_sections", {})
        
        # Build article structure
        article_parts = []
        
        # Add YAML frontmatter
        article_parts.append("---")
        for key, value in metadata.items():
            if isinstance(value, str):
                article_parts.append(f"{key}: \"{value}\"")
            else:
                article_parts.append(f"{key}: {value}")
        article_parts.append("---")
        article_parts.append("")
        
        # Add title
        article_parts.append(f"# {schema_type.title()} Guide: {subject}")
        article_parts.append("")
        
        # Add tags
        article_parts.append("## Tags")
        article_parts.append("")
        article_parts.append(tags)
        article_parts.append("")
        
        # Add JSON-LD
        article_parts.append("## JSON-LD Structured Data")
        article_parts.append("")
        article_parts.append("<script type=\"application/ld+json\">")
        article_parts.append(json_ld)
        article_parts.append("</script>")
        article_parts.append("")
        
        # Add content sections
        if "overview" in content_sections:
            article_parts.append("## Overview")
            article_parts.append("")
            article_parts.append(content_sections["overview"])
            article_parts.append("")
        
        # Add other content sections
        for section_name, section_content in content_sections.items():
            if section_name != "overview" and section_content:  # Skip overview as it's already added
                article_parts.append(f"## {section_name.title()}")
                article_parts.append("")
                article_parts.append(section_content)
                article_parts.append("")
        
        # Get assembled article content
        article_content = "\n".join(article_parts)
        
        # Validate the article and add validation results section
        article_content = self._validate_and_annotate(article_content, schema_type, schema)
        
        return article_content
    
    def _validate_and_annotate(self, article_content: str, schema_type: str, schema: Dict[str, Any]) -> str:
        """Validate the article and add validation results."""
        issues = []
        
        # Check for basic required sections
        required_sections = schema.get("validation", {}).get("requiredSections", [])
        for section in required_sections:
            section_heading = f"## {section}"
            if section_heading not in article_content:
                issues.append(f"Missing required section: {section}")
            else:
                # Find the section content
                start_idx = article_content.find(section_heading) + len(section_heading)
                end_idx = article_content.find("##", start_idx)
                if end_idx == -1:
                    end_idx = len(article_content)
                section_content = article_content[start_idx:end_idx].strip()
                
                # Check if it's empty or just placeholder text
                if not section_content:
                    issues.append(f"Empty content in {section} section")
                elif f"Information about" in section_content and "goes here" in section_content:
                    issues.append(f"Placeholder text in {section} section")
                elif len(section_content.split()) < 10:
                    issues.append(f"Insufficient content in {section} section (less than 10 words)")
        
        # Check JSON-LD
        if "<script type=\"application/ld+json\">" not in article_content:
            issues.append("Missing JSON-LD section")
        else:
            # Extract JSON-LD
            import re
            import json
            
            jsonld_match = re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', article_content, re.DOTALL)
            if jsonld_match:
                try:
                    jsonld_content = json.loads(jsonld_match.group(1))
                    
                    # Check JSON-LD against schema requirements
                    jsonld_requirements = schema.get("jsonLD", {})
                    required_type = jsonld_requirements.get("@type")
                    
                    if required_type and jsonld_content.get("@type") != required_type:
                        issues.append(f"JSON-LD @type should be '{required_type}', found '{jsonld_content.get('@type', '')}'")
                    
                    # Check for required properties
                    required_props = jsonld_requirements.get("requiredProperties", [])
                    for prop in required_props:
                        if prop not in jsonld_content:
                            issues.append(f"JSON-LD missing required property: {prop}")
                    
                    # Check for empty values in properties
                    for key, value in jsonld_content.items():
                        if key != "@context" and (value == "" or (isinstance(value, dict) and all(v == "" for v in value.values()))):
                            issues.append(f"JSON-LD has empty value for property: {key}")
                            
                except json.JSONDecodeError:
                    issues.append("Invalid JSON-LD format")
        
        # Store validation results
        self.last_validation_result = len(issues) == 0
        self.last_validation_issues = issues
        
        # Add validation section
        article_parts = article_content.split("\n")
        
        # Add validation section
        article_parts.append("\n## Validation Results\n")
        
        if self.last_validation_result:
            article_parts.append("✅ **VALIDATION PASSED**: Article successfully validated against schema definition\n")
        else:
            article_parts.append("⚠️ **VALIDATION FAILED**: The following issues were found:\n")
            for issue in issues:
                article_parts.append(f"- {issue}\n")
        
        # Add validation timestamp
        from datetime import datetime
        article_parts.append(f"Validated: {datetime.now().isoformat()}")
        
        # Reassemble with validation section
        return "\n".join(article_parts)
    
    def save_article(self, article_content: str, generation_result: Dict[str, Any], output_dir: str = "output") -> str:
        """
        Save article to file with appropriate directory structure.
        
        Args:
            article_content: The assembled and validated article content
            generation_result: Original generation result dict
            output_dir: Base output directory
            
        Returns:
            Path to saved article file
        """
        # Extract components and context
        components = generation_result["components"]
        context = generation_result.get("context", {})
        
        schema_type = components["schema_type"]
        subject = components["subject"]
        
        # Create sanitized filename
        sanitized_subject = subject.lower().replace(' ', '_').replace('/', '_')
        filename = f"{schema_type}_{sanitized_subject}.md"
        
        # Create directory structure
        schema_dir = os.path.join(output_dir, schema_type)
        os.makedirs(schema_dir, exist_ok=True)
        
        # Full file path
        file_path = os.path.join(schema_dir, filename)
        
        # Add file header comment
        file_header = f"<!-- filepath: {os.path.abspath(file_path)} -->\n"
        article_with_header = file_header + article_content
        
        # Save file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(article_with_header)
        
        self.logger.info(f"Article saved to {file_path}")
        
        # If validation failed, also save validation report
        if not self.last_validation_result:
            report_path = f"{file_path}.validation.txt"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f"Validation Report for {file_path}\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n\n")
                f.write(f"Schema Type: {schema_type}\n")
                f.write(f"Subject: {subject}\n\n")
                f.write("Validation Issues:\n")
                for issue in self.last_validation_issues:
                    f.write(f"- {issue}\n")
            
            self.logger.info(f"Validation report saved to {report_path}")
        
        return file_path
    
    def get_validation_status(self) -> Tuple[bool, list]:
        """
        Get the result of the last validation.
        
        Returns:
            Tuple containing (is_valid, list_of_issues)
        """
        return self.last_validation_result, self.last_validation_issues
    
    def _generate_article_components(self, result):
        """
        Generate article components from result.
        No fallbacks - fail fast with clear errors.
        """
        # Extract data from result
        components = result.get("components", {})
        metadata = components.get("metadata", {})
        tags = components.get("tags", [])
        json_ld = components.get("json_ld", "")
        content_sections = components.get("content_sections", {})
        
        # Validate required components
        if not metadata:
            raise ValueError("Missing metadata component")
        
        if not json_ld:
            raise ValueError("Missing JSON-LD component") 
        
        if not content_sections:
            raise ValueError("Missing content sections")
        
        # Return components
        return {
            "metadata": metadata,
            "tags": tags,
            "json_ld": json_ld,
            "content_sections": content_sections
        }

    def _generate_jsonld(self, data: Dict[str, Any]) -> str:
        """Generate JSON-LD for article"""
        if self.json_ld_generator:
            try:
                return self.json_ld_generator.generate(data)
            except Exception as e:
                # No fallback - propagate the error
                self.logger.error(f"JSON-LD generator failed: {e}")
                raise RuntimeError(f"JSON-LD generation failed: {e}")
        else:
            raise RuntimeError("No JSON-LD generator available")

    def _generate_tags(self, data: Dict[str, Any]) -> List[str]:
        """Generate tags for article"""
        if self.tags_generator:
            try:
                return self.tags_generator.generate(data)
            except Exception as e:
                # No fallback - propagate the error
                self.logger.error(f"Tags generator failed: {e}")
                raise RuntimeError(f"Tags generation failed: {e}")
        else:
            raise RuntimeError("No tags generator available")

    def _generate_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate metadata for article"""
        if self.metadata_generator:
            try:
                return self.metadata_generator.generate(data)
            except Exception as e:
                # No fallback - propagate the error
                self.logger.error(f"Metadata generator failed: {e}")
                raise RuntimeError(f"Metadata generation failed: {e}")
        else:
            raise RuntimeError("No metadata generator available")