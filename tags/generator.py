"""Simplified tags generator - SCHEMA-DRIVEN ONLY."""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from api_client import APIClient
import re
import json

logger = logging.getLogger(__name__)

class TagsGenerator:
    """Generates tags ONLY from schema definitions."""
    
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str, frontmatter: Optional[str] = None, frontmatter_summary: Optional[str] = None):
        # Existing initialization
        self.context = context
        self.schema = schema
        self.ai_provider = ai_provider
        self.api_client = APIClient(ai_provider)
        
        # Store frontmatter if provided
        self.frontmatter = frontmatter
        self.frontmatter_summary = frontmatter_summary

        # NO DEFAULT VALUES - Must come from context
        self.subject = context["subject"]  # Will fail if not provided
        self.article_type = context["article_type"]  # Will fail if not provided
        
        # Load prompt template
        self.prompt_config = self._load_prompt_template()
        
        logger.info(f"TagsGenerator initialized for {self.article_type}: {self.subject}")
    
    def generate(self) -> Optional[str]:
        """Generate tags for an article using frontmatter when available."""
        try:
            # Check if we should use the two-stage process (requires frontmatter)
            if self.frontmatter:
                logger.info("Using two-stage tag generation process with frontmatter")
                
                # Generate candidate tags first (30-40)
                candidate_tags = self._generate_candidate_tags()
                if not candidate_tags or len(candidate_tags) < 5:
                    logger.error("Failed to generate sufficient candidate tags")
                    return None
                    
                logger.info(f"Generated {len(candidate_tags)} candidate tags")
                
                # Select the best tags based on audience
                final_tags = self._select_audience_relevant_tags(candidate_tags)
                logger.info(f"Selected {len(final_tags)} audience-relevant tags")
                
                return ', '.join(final_tags)
            else:
                # Fall back to standard generation if no frontmatter
                logger.info("Using standard tag generation (no frontmatter provided)")
                prompt = self._build_prompt()
                
                if not prompt:
                    logger.error("Failed to build prompt - no schema fields available")
                    return None
                
                # Use prompt config for parameters
                max_tokens = self.prompt_config.get("parameters", {}).get("max_tokens", 1000)
                response = self.api_client.generate(prompt, max_tokens=max_tokens)
                
                if not response:
                    logger.error("Failed to generate tags")
                    return None
                
                # Process tags from response
                tags = self._process_response(response)
                
                return tags
                
        except Exception as e:
            logger.error(f"Tags generation failed: {e}")
            return None

    def _generate_candidate_tags(self) -> List[str]:
        """Generate 30-40 candidate tags."""
        prompt = self._build_candidate_tags_prompt()
        if not prompt:
            return []
            
        # Generate response
        response = self.api_client.generate(prompt, max_tokens=2000)
        if not response:
            return []
        
        # FIXED APPROACH:
        # 1. First get the raw response as a string
        raw_response = response
    
        # 2. Process the string into a list of tags
        # (Either using process_tags directly if it handles strings properly)
        return self.process_tags(raw_response)
    
        # OR if you want to use _clean_response:
        # tags_list = self._clean_response(raw_response)
        # return tags_list
    
    def _build_candidate_tags_prompt(self) -> str:
        """Build prompt for generating candidate tags."""
        schema_template = self._build_schema_template()
        
        if not schema_template:
            logger.error("No schema fields available for tag generation")
            return None
        
        # Use template from prompt config
        template = self.prompt_config.get("template", "")
        if not template:
            logger.error("No prompt template found")
            return None
        
        # No need for replacement - YAML already has the right instructions!
        # Remove the entire template.replace() section
        
        return template.format(
            article_type=self.article_type,
            subject=self.subject,
            schema_template=schema_template,
            frontmatter_summary=self.frontmatter_summary or ""
        )
    
    def _build_prompt(self) -> str:
        """Build tags prompt using template."""
        schema_template = self._build_schema_template()
        
        if not schema_template:
            logger.error("No schema fields available for tags generation")
            return None
        
        # Use template from prompt config
        template = self.prompt_config.get("template", "")
        if not template:
            logger.error("No prompt template found")
            return None
        
        return template.format(
            article_type=self.article_type,
            subject=self.subject,
            schema_template=schema_template
        )
    
    def _build_schema_template(self) -> str:
        """Build template using schema structure."""
        # Handle different profile naming conventions
        profile_keys = [
            f"{self.article_type}Profile",  # Standard: "applicationProfile"
            "termProfile",                   # Thesaurus: "termProfile"
            f"{self.article_type}_profile",  # Snake case
            f"{self.article_type.title()}Profile"  # Title case
        ]
        
        profile = None
        for key in profile_keys:
            if key in self.schema:
                profile = self.schema[key]
                logger.info(f"✅ Found profile using key: {key}")
                break
        
        if profile:
            return self._build_schema_template_from_profile(profile)
        else:
            logger.error(f"❌ No profile found. Tried keys: {profile_keys}")
            return None  # NO FALLBACK - FAIL FAST
    
    def _build_schema_template_from_profile(self, profile: Dict[str, Any]) -> str:
        """Build dynamic schema template with field-specific instructions."""
        template_parts = []
        
        # Add header with field count
        field_count = len(profile)
        template_parts.append(f"TOTAL FIELDS FOR TAG EXTRACTION: {field_count}")
        template_parts.append("=" * 50)
        
        field_index = 1
        for field_name, field_def in profile.items():
            if isinstance(field_def, dict) and "example" in field_def:
                # Add field header
                template_parts.append(f"\nFIELD {field_index}/{field_count}: {field_name}")
                template_parts.append("-" * 30)
                
                # Add field type and description
                field_type = field_def.get("type", "unknown")
                field_description = field_def.get("description", "No description")
                template_parts.append(f"Type: {field_type}")
                template_parts.append(f"Description: {field_description}")
                
                # Add example with tag extraction instruction
                example = field_def["example"]
                if isinstance(example, str):
                    processed_value = self._replace_placeholders(example)
                    template_parts.append(f"Example: {processed_value}")
                    template_parts.append(f"REQUIRED: Extract 3-5 technical tags from {field_name}")
                elif isinstance(example, list):
                    processed_items = [self._replace_placeholders(str(item)) for item in example]
                    template_parts.append(f"Examples: {processed_items}")
                    template_parts.append(f"REQUIRED: Extract tags from ALL examples in {field_name}")
                
                template_parts.append("")  # Add spacing
                field_index += 1
        
        # Add validation footer
        template_parts.append("=" * 50)
        template_parts.append(f"TAG EXTRACTION: Generate tags from ALL {field_count} fields above")
        template_parts.append("MINIMUM 3-5 TAGS PER FIELD - NO FIELD SHOULD BE IGNORED")
        
        return '\n'.join(template_parts)
    
    def _replace_placeholders(self, value: str) -> str:
        """Replace schema placeholders."""
        placeholder_map = {
            "materialName": self.subject,
            "applicationName": self.subject,
            "regionName": self.subject,
            "term": self.subject,
            "{{materialName}}": self.subject,
            "{{applicationName}}": self.subject,
            "{{regionName}}": self.subject,
            "{{term}}": self.subject
        }
        
        for placeholder, replacement in placeholder_map.items():
            value = value.replace(placeholder, replacement)
        
        return value
    
    def _clean_response(self, response: str) -> List[str]:
        """Clean the API response to extract tags."""
        try:
            # Split the response by lines and cleanup
            lines = response.strip().split('\n')
            
            # Extract tags (one per line or comma-separated)
            tags = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Split by comma if present (handles both formats)
                if ',' in line:
                    parts = [p.strip() for p in line.split(',')]
                    tags.extend([p for p in parts if p])
                else:
                    # Remove bullet points or other markers
                    line = re.sub(r'^[-•*]\s*', '', line)
                    if line:
                        tags.append(line)
            
            # Clean up any remaining issues
            clean_tags = []
            for tag in tags:
                # Remove quotes and formatting
                tag = tag.strip('"\'')
                tag = re.sub(r'\s+', '-', tag)
                
                # CRITICAL: Ensure we're not adding characters individually
                if len(tag) > 1:  # Only add tags longer than a single character
                    clean_tags.append(tag)
            
            logger.debug(f"Extracted {len(clean_tags)} clean tags: {clean_tags[:10]}...")
            return clean_tags
            
        except Exception as e:
            logger.error(f"Error cleaning tags: {e}")
            return []
    
    def _validate_tags(self, tags: List[str]) -> bool:
        """Validate tags."""
        # Update the defaults here to match your new requirements
        validation_config = self.prompt_config.get("validation", {})
        min_tags = validation_config.get("min_tags", 5)  # Changed from 75 to 5
        max_tags = validation_config.get("max_tags", 15)  # Changed from 100 to 15
        
        if len(tags) < min_tags:
            logger.error(f"Too few tags: {len(tags)} < {min_tags}")
            return False
        
        if len(tags) > max_tags:
            logger.warning(f"Too many tags: {len(tags)} > {max_tags}, truncating")
            tags = tags[:max_tags]  # This truncation happens here, but doesn't affect the original list
        
        return True
    
    def process_tags(self, raw_tags: str) -> List[str]:
        """
        Process raw tags from the API into a clean list of tags.
        
        Args:
            raw_tags: Raw tags string from API
            
        Returns:
            List of cleaned tag strings
        """
        # Handle empty input
        if not raw_tags:
            return []
            
        # Try to parse as JSON if it looks like a JSON array
        if raw_tags.strip().startswith('[') and raw_tags.strip().endswith(']'):
            try:
                tags_list = json.loads(raw_tags)
                if isinstance(tags_list, list):
                    return [t.strip().lower().replace(' ', '-') for t in tags_list if t.strip()]
            except json.JSONDecodeError:
                pass
        
        # Process as comma-separated string
        tags_list = []
        
        # Split by commas and process each tag
        parts = raw_tags.split(',')
        for part in parts:
            part = part.strip()
            if part:
                # Skip spaces as individual characters
                if part == " ":
                    continue
                # Convert spaces to dashes for kebab-case
                tags_list.append(part.lower().replace(' ', '-'))
        
        # Return unique tags
        return list(dict.fromkeys(tags_list))
    
    def process_response(self, response):
        """Process the raw response from the LLM."""
        if not response:
            return []
        
        try:
            # Check if response is already a list
            if isinstance(response, list):
                return response
            
            # Clean up the response
            lines = response.strip().split('\n')
            tags = []
            
            for line in lines:
                # Skip empty lines
                if not line.strip():
                    continue
                    
                # Handle bullet points or numbered lists
                if line.strip().startswith('-') or line.strip().startswith('*'):
                    tag = line.strip()[1:].strip()
                    tags.append(tag)
                    continue
                    
                # If it's not a list item, check for comma separation
                if ',' in line:
                    parts = [part.strip() for part in line.split(',')]
                    tags.extend(parts)
                    continue
                    
                # Otherwise, assume it's a single tag
                tags.append(line.strip())
            
            # Final cleanup - remove any empty tags
            tags = [tag for tag in tags if tag and not tag.isspace()]
            
            # Remove any "tags:" header if present
            tags = [tag for tag in tags if tag.lower() != "tags:" and not tag.lower().startswith("tags:")]
            
            # Log the number of tags found
            logger.info(f"Generated {len(tags)} candidate tags")
            
            return tags
        except Exception as e:
            logger.error(f"Error processing tags: {e}", exc_info=True)
            return []
    
    def _process_response(self, response: str) -> str:
        """Process the API response to extract tags."""
        try:
            # Extract tags from response
            cleaned_response = self._clean_response(response)
            
            # Split by commas and clean each tag
            tags_list = [tag.strip() for tag in cleaned_response.split(',') if tag.strip()]
            
            # Ensure we have exactly 15 tags
            if len(tags_list) < 15:
                logger.warning(f"Not enough tags: {len(tags_list)} < 15, using what we have")
            elif len(tags_list) > 15:
                logger.warning(f"Too many tags: {len(tags_list)} > 15, using only first 15")
                tags_list = tags_list[:15]
            else:
                logger.info(f"Successfully generated exactly 15 schema-driven tags")
            
            # Validate tags
            valid_tags = []
            for tag in tags_list:
                if self._is_valid_tag(tag):
                    valid_tags.append(tag)
            
            # Return comma-separated string of tags
            return ", ".join(valid_tags)
        except Exception as e:
            logger.error(f"Failed to process tags response: {e}")
            return None
    
    def _is_valid_tag(self, tag: str) -> bool:
        """Check if a tag is valid based on custom criteria."""
        # Example criteria: tag must be alphanumeric and between 3 to 30 characters
        if re.match(r'^[a-zA-Z0-9-]{3,30}$', tag):
            return True
        else:
            logger.warning(f"Invalid tag skipped: {tag}")
            return False
    
    def _extract_audience_info(self) -> str:
        """Extract audience information from frontmatter."""
        if not self.frontmatter:
            return ""
            
        # Simple extraction using regex
        audience_info = []
        
        # Extract primary audience
        primary_match = re.search(r'primaryAudience:\s*(.*?)(?=\n\w+:|$)', self.frontmatter, re.DOTALL)
        if primary_match:
            audience_info.append(f"PRIMARY AUDIENCE: {primary_match.group(1).strip()}")
            
        # Extract secondary audience
        secondary_match = re.search(r'secondaryAudience:\s*(.*?)(?=\n\w+:|$)', self.frontmatter, re.DOTALL)
        if secondary_match:
            audience_info.append(f"SECONDARY AUDIENCE: {secondary_match.group(1).strip()}")
            
        # Extract industries
        industries_match = re.search(r'industries:\s*((?:-.*?\n)+)', self.frontmatter, re.DOTALL)
        if industries_match:
            audience_info.append(f"INDUSTRIES: {industries_match.group(1).strip()}")
        
        return "\n".join(audience_info)

    def _select_audience_relevant_tags(self, candidate_tags: List[str]) -> List[str]:
        """Select exactly 15 tags that are most relevant to the audience."""
        if not candidate_tags:
            return []
            
        # Extract audience information from frontmatter
        audience_info = self._extract_audience_info()
        
        # If we couldn't extract audience info, just return first 15 tags
        if not audience_info:
            logger.warning("No audience information found in frontmatter, using first 15 tags")
            return candidate_tags[:15]
        
        # Get audience selection prompt template from YAML
        template = self.prompt_config.get("audience_selection_template", "")
        if not template:
            logger.warning("No audience selection template found, using first 15 tags")
            return candidate_tags[:15]
        
        # Format the prompt with dynamic content
        tags_str = ", ".join(candidate_tags)
        prompt = template.format(
            article_type=self.article_type,
            subject=self.subject,
            audience_info=audience_info,
            tags_list=tags_str
        )
        
        # Get selected tags
        response = self.api_client.generate(prompt, max_tokens=1000)
        if not response:
            logger.warning("Failed to get audience-relevant tags, using first 15 tags")
            return candidate_tags[:15]
        
        # Parse response into tags
        cleaned_response = self._clean_response(response)
        selected_tags = self.process_tags(cleaned_response)
        
        # Ensure we have exactly 15 tags
        if len(selected_tags) > 15:
            selected_tags = selected_tags[:15]
        elif len(selected_tags) < 15:
            # Fill in with remaining candidate tags
            remaining = 15 - len(selected_tags)
            for tag in candidate_tags:
                if tag not in selected_tags:
                    selected_tags.append(tag)
                    remaining -= 1
                    if remaining <= 0:
                        break
        
        return selected_tags

    def _load_prompt_template(self) -> Dict[str, Any]:
        """Load prompt template from YAML file."""
        try:
            prompt_path = Path(__file__).parent / "prompt.yaml"
            with open(prompt_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load prompt template: {e}")
            return {}