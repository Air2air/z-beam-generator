"""YAML formatting utilities for frontmatter generation."""

import re
import logging

logger = logging.getLogger(__name__)

class YAMLFormatter:
    """Static utility class for YAML formatting operations."""
    
    @staticmethod
    def clean_response(response: str) -> str:
        """Clean API response to extract YAML frontmatter."""
        if not response:
            return ""
        
        # First, try to find YAML content between markdown code blocks with yaml indicator
        code_block_pattern = r'```\s*yaml\s*([\s\S]*?)\s*```'
        code_matches = re.search(code_block_pattern, response)
        
        if code_matches:
            # Extract YAML from code block
            yaml_content = code_matches.group(1).strip()
            logger.info("Extracted YAML from markdown code block")
            
            # Check for multiple documents and fix them
            yaml_content = YAMLFormatter.fix_multiple_documents(yaml_content)
            
            return f"---\n{yaml_content}\n---"
        
        # Second, try to find any code blocks
        generic_block_pattern = r'```\s*([\s\S]*?)\s*```'
        generic_matches = re.search(generic_block_pattern, response)
        
        if generic_matches:
            # Extract content from generic code block
            yaml_content = generic_matches.group(1).strip()
            logger.info("Extracted YAML from generic code block")
            
            # Check for multiple documents and fix them
            yaml_content = YAMLFormatter.fix_multiple_documents(yaml_content)
            
            return f"---\n{yaml_content}\n---"
            
        # Third, try to find YAML content between triple dashes (already formatted frontmatter)
        yaml_pattern = r'---\s*([\s\S]*?)\s*---'
        matches = re.search(yaml_pattern, response)
        
        if matches:
            # YAML was in frontmatter format - don't add extra markers
            yaml_content = matches.group(1).strip()
            logger.info("Extracted YAML from frontmatter format")
            
            # No need to fix multiple documents here as we only extract the first one
            return f"---\n{yaml_content}\n---"
        
        # Finally, if no patterns matched, assume entire response is YAML content
        # But first, clean it up by removing any markdown formatting indicators
        cleaned_response = response.strip()
        cleaned_response = re.sub(r'^#+\s*YAML\s*\n', '', cleaned_response)  # Remove "# YAML" headers
        cleaned_response = re.sub(r'^#+\s*Frontmatter\s*\n', '', cleaned_response)  # Remove "# Frontmatter" headers
        
        # Check for and fix multiple documents here too
        cleaned_response = YAMLFormatter.fix_multiple_documents(cleaned_response)
        
        logger.warning("No structured format found, using cleaned content with added frontmatter markers")
        return f"---\n{cleaned_response}\n---"
    
    @staticmethod
    def fix_multiple_documents(content: str) -> str:
        """Fix content that contains multiple YAML documents (multiple --- markers)."""
        # Count the number of --- markers
        dash_count = content.count('---')
        
        # If we have more than 1 set of markers (3+ dashes), we may have multiple documents
        if dash_count >= 2:
            logger.warning(f"Detected potential multiple YAML documents ({dash_count} --- markers)")
            
            # First, remove any --- at the beginning
            if content.lstrip().startswith('---'):
                # Find the end of the first marker
                first_dash_end = content.find('---') + 3
                # Remove everything before and including the first dash
                content = content[first_dash_end:].lstrip()
                logger.info("Removed leading --- marker")
            
            # Replace any remaining --- markers with spaces or newlines
            content = re.sub(r'---+', '\n', content)
            logger.info("Replaced internal document separators with newlines")
            
            return content
            
        return content
    
    @staticmethod
    def validate_yaml_structure(yaml_content: str) -> bool:
        """Basic validation of YAML structure."""
        # Verify frontmatter markers
        if not yaml_content.startswith('---') or not ('---' in yaml_content[3:]):
            logger.warning("Missing frontmatter markers")
            return False
            
        # Check for minimum content
        if len(yaml_content) < 50:
            logger.warning(f"YAML content too short: {len(yaml_content)} < 50 chars")
            return False
            
        # Check for common YAML issues
        issues = [
            (':', 'Missing colon in key-value pairs'),
            ('name:', 'Missing name field'),
            ('description:', 'Missing description field')
        ]
        
        for pattern, message in issues:
            if pattern not in yaml_content:
                logger.warning(f"YAML validation issue: {message}")
                return False
        
        return True
    
    @staticmethod
    def remove_duplicate_frontmatter(content: str) -> str:
        """Remove duplicate frontmatter markers from content."""
        # Count the number of --- markers
        dash_count = content.count('---')
        
        # If we have more than 2, we have duplicate frontmatter
        if dash_count > 2:
            # Find the first complete frontmatter section
            frontmatter_match = re.search(r'---\s*([\s\S]*?)\s*---', content)
            if frontmatter_match:
                # Extract just the content between the first set of --- markers
                yaml_content = frontmatter_match.group(1).strip()
                logger.info("Removed duplicate frontmatter markers")
                return f"---\n{yaml_content}\n---"
        
        return content
    
    @staticmethod
    def fix_nested_frontmatter(content: str) -> str:
        """Fix nested frontmatter markers that can cause YAML parsing errors."""
        # This pattern will match frontmatter with nested frontmatter inside
        nested_pattern = r'---\s*(.*?---.*?---.*?)\s*---'
        nested_match = re.search(nested_pattern, content, re.DOTALL)
        
        if nested_match:
            # There are nested frontmatter markers
            inner_content = nested_match.group(1)
            
            # Find just the first section of actual YAML content
            inner_yaml_match = re.search(r'^(.*?)---', inner_content, re.DOTALL)
            if inner_yaml_match:
                yaml_content = inner_yaml_match.group(1).strip()
                logger.info("Fixed nested frontmatter markers")
                return f"---\n{yaml_content}\n---"
        
        return content

    @staticmethod
    def extract_first_document_only(content: str) -> str:
        """Extract only the first YAML document from potentially multiple documents."""
        # This specifically handles the "expected a single document" error
        
        # If no document markers or just one set (start/end), return as is
        if content.count('---') <= 2:
            return content
        
        # Try to find the position of the second '---' marker (third overall)
        if content.startswith('---'):
            first_end = content.find('---', 3)  # Find second marker
            if first_end > 0:
                second_start = content.find('---', first_end + 3)  # Find third marker
                if second_start > 0:
                    # Extract just the first document
                    logger.info("Extracting first YAML document only (multiple documents detected)")
                    return content[:second_start].strip()
        
        # If we can't find the markers in sequence, try regex
        matches = re.findall(r'---\s*([\s\S]*?)\s*---', content)
        if matches and len(matches) > 0:
            logger.info("Extracted first YAML document using regex")
            return f"---\n{matches[0]}\n---"
        
        return content