"""Enhanced tags generator with support for new schema structures."""

import logging
import yaml
import random
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class TagsGenerator:
    """Generates relevant tags for technical articles from schema and frontmatter."""

    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], frontmatter: Optional[Dict[str, Any]] = None):
        self.context = context
        self.schema = schema
        self.frontmatter = frontmatter or {}
        
        # Critical context values
        self.article_type = context.get("article_type", "material")
        self.subject = context.get("subject", "")
        
        # Load prompt template
        self.prompt_config = self._load_prompt_template()
        
        # Audience targeting
        self.audience = context.get("audience", "technical")
        
        # Track tag selections for debugging
        self.selected_tags = {
            "technical": [],
            "application": [],
            "industry": [],
            "process": [],
            "audience": []
        }
        
        logger.info(f"TagsGenerator initialized for {self.article_type}: {self.subject}")

    def _load_prompt_template(self) -> Dict[str, Any]:
        """Load prompt template from local YAML file."""
        try:
            prompt_path = Path(__file__).parent / "prompt.yaml"
            with open(prompt_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load tags prompt template: {e}")
            return {}

    def generate(self) -> Optional[List[str]]:
        """Generate relevant tags based on article type and content."""
        try:
            # First, try to use existing tags from frontmatter if available and valid
            if self.frontmatter and "tags" in self.frontmatter and isinstance(self.frontmatter["tags"], list):
                existing_tags = self.frontmatter["tags"]
                if len(existing_tags) >= 5:
                    logger.info(f"Using {len(existing_tags)} existing tags from frontmatter")
                    return existing_tags
            
            # Extract schema-based tags
            schema_tags = self._extract_schema_tags()
            logger.info(f"Extracted {len(schema_tags)} potential tags from schema")
            
            # Get existing keywords if available for context
            keywords = []
            if self.frontmatter and "keywords" in self.frontmatter and isinstance(self.frontmatter["keywords"], list):
                keywords = self.frontmatter["keywords"][:5]  # Use up to 5 keywords
                logger.info(f"Found {len(keywords)} keywords to use as tag seeds")
            
            # Combine with schema tags
            seed_tags = list(set(keywords + schema_tags))
            
            # Select tags from predefined categories
            tags = self._select_tags(seed_tags)
            
            # Ensure essential tags are included
            tags = self._ensure_essential_tags(tags)
            
            logger.info(f"Selected {len(tags)} audience-relevant tags")
            return tags
            
        except Exception as e:
            logger.error(f"Tag generation failed: {e}", exc_info=True)
            return self._generate_fallback_tags()

    def _extract_schema_tags(self) -> List[str]:
        """Extract potential tags from schema definition."""
        potential_tags = []
        
        # Find the schema profile
        profile_keys = [
            f"{self.article_type}Profile",
            "termProfile",
            f"{self.article_type}_profile",
            f"{self.article_type.title()}Profile",
            "schema"
        ]
        
        profile = None
        for key in profile_keys:
            if key in self.schema:
                profile = self.schema[key]
                break
        
        if not profile:
            return []
        
        # Extract field names from different schema structures
        if "fieldsets" in profile:
            # New fieldsets structure
            for fieldset_name, fieldset in profile["fieldsets"].items():
                potential_tags.append(fieldset_name.lower().replace("_", " "))
                
                if "fields" in fieldset:
                    for field_name in fieldset["fields"].keys():
                        if len(field_name) > 3:  # Skip short field names
                            potential_tags.append(field_name.lower().replace("_", " "))
        
        elif "fields" in profile:
            # Direct fields structure
            for field_name in profile["fields"].keys():
                if len(field_name) > 3:  # Skip short field names
                    potential_tags.append(field_name.lower().replace("_", " "))
        
        else:
            # Legacy structure
            for field_name, field_def in profile.items():
                if isinstance(field_def, dict) and len(field_name) > 3:
                    potential_tags.append(field_name.lower().replace("_", " "))
        
        # Filter out common structural field names that don't make good tags
        filtered_tags = []
        blacklist = ["name", "description", "type", "example", "fields", "items"]
        
        for tag in potential_tags:
            if tag not in blacklist and len(tag) > 3:
                filtered_tags.append(tag)
        
        return filtered_tags

    def _select_tags(self, seed_tags: List[str]) -> List[str]:
        """Select appropriate tags from predefined categories."""
        all_tags = []
        
        # Start with seed tags
        all_tags.extend(seed_tags)
        
        # Get tag templates from prompt config
        tag_templates = self.prompt_config.get("templates", {})
        
        # Add article type specific tags
        article_templates = tag_templates.get(self.article_type, {})
        
        # Select technical tags
        technical_tags = article_templates.get("technical", [])
        selected = self._select_category_tags(technical_tags, 3)
        self.selected_tags["technical"] = selected
        all_tags.extend(selected)
        
        # Select application tags
        application_tags = article_templates.get("application", [])
        selected = self._select_category_tags(application_tags, 2)
        self.selected_tags["application"] = selected
        all_tags.extend(selected)
        
        # Select industry tags
        industry_tags = article_templates.get("industry", [])
        selected = self._select_category_tags(industry_tags, 2)
        self.selected_tags["industry"] = selected
        all_tags.extend(selected)
        
        # Select process tags
        process_tags = article_templates.get("process", [])
        selected = self._select_category_tags(process_tags, 2)
        self.selected_tags["process"] = selected
        all_tags.extend(selected)
        
        # Select audience-specific tags
        audience_tags = tag_templates.get("audience", {}).get(self.audience, [])
        selected = self._select_category_tags(audience_tags, 3)
        self.selected_tags["audience"] = selected
        all_tags.extend(selected)
        
        # Make tags unique and lowercase
        unique_tags = []
        seen = set()
        for tag in all_tags:
            tag_lower = tag.lower().strip()
            if tag_lower and tag_lower not in seen and len(tag_lower) > 2:  # Skip very short tags
                unique_tags.append(tag_lower)
                seen.add(tag_lower)
        
        return unique_tags

    def _select_category_tags(self, category_tags: List[str], count: int) -> List[str]:
        """Select tags from a category, prioritizing relevant ones."""
        if not category_tags:
            return []
            
        # Try to find tags containing the subject
        subject_parts = self.subject.lower().split()
        relevant_tags = []
        
        # First pass: find tags containing the complete subject
        for tag in category_tags:
            if self.subject.lower() in tag.lower():
                relevant_tags.append(tag)
                
        # Second pass: find tags containing parts of the subject
        if len(relevant_tags) < count:
            for tag in category_tags:
                if tag not in relevant_tags:
                    for part in subject_parts:
                        if len(part) > 3 and part in tag.lower():  # Only match on significant parts
                            relevant_tags.append(tag)
                            break
        
        # If we found enough relevant tags, use those
        if len(relevant_tags) >= count:
            return random.sample(relevant_tags, count)
        
        # Otherwise, combine relevant tags with random selections
        remaining_count = count - len(relevant_tags)
        remaining_tags = [tag for tag in category_tags if tag not in relevant_tags]
        
        if remaining_tags and remaining_count > 0:
            # Add random selections from remaining tags
            random_selections = random.sample(remaining_tags, min(remaining_count, len(remaining_tags)))
            return relevant_tags + random_selections
        
        return relevant_tags

    def _ensure_essential_tags(self, tags: List[str]) -> List[str]:
        """Ensure essential tags are included and limit the total number."""
        # Add the subject as a tag
        subject_tag = self.subject.lower()
        if subject_tag not in tags:
            tags.append(subject_tag)
        
        # Add the article type as a tag
        article_type_tag = self.article_type.lower()
        if article_type_tag not in tags and article_type_tag != "thesaurus":
            tags.append(article_type_tag)
            
        # For thesaurus entries, add "glossary" and "terminology" instead
        if self.article_type == "thesaurus":
            for term_tag in ["glossary", "terminology", "technical term"]:
                if term_tag not in tags:
                    tags.append(term_tag)
        
        # Add "laser cleaning" as a required tag
        if "laser cleaning" not in tags:
            tags.append("laser cleaning")
            
        # Add validation required tags from prompt config
        required_tags = self.prompt_config.get("validation", {}).get("required_tags", [])
        for required_tag in required_tags:
            if required_tag not in tags:
                tags.append(required_tag)
                
        # Select a subset if we have too many
        max_tags = self.prompt_config.get("validation", {}).get("max_tags", 15)
        if len(tags) > max_tags:
            # Keep required tags
            required_tags = [subject_tag, "laser cleaning"] + required_tags
            if self.article_type != "thesaurus":
                required_tags.append(article_type_tag)
            else:
                required_tags.extend(["glossary", "terminology"])
                
            # Ensure uniqueness
            required_tags = list(set(required_tags))
            
            # Remove required tags from the pool
            optional_tags = [tag for tag in tags if tag not in required_tags]
            
            # Calculate how many additional tags we can include
            additional_count = max_tags - len(required_tags)
            
            if additional_count > 0 and optional_tags:
                # Randomly select additional tags to reach max_tags
                selected_optional = random.sample(optional_tags, min(additional_count, len(optional_tags)))
                tags = required_tags + selected_optional
            else:
                tags = required_tags
        
        return tags

    def _generate_fallback_tags(self) -> List[str]:
        """Generate fallback tags when normal generation fails."""
        # Basic tags that work for any article type
        fallback_tags = [
            "laser cleaning",
            "surface treatment",
            "industrial cleaning",
            self.subject.lower(),
        ]
        
        # Add article type specific fallback tags
        if self.article_type == "material":
            fallback_tags.extend(["material properties", "surface preparation", "material processing"])
        elif self.article_type == "application":
            fallback_tags.extend(["application technique", "process optimization", "industrial application"])
        elif self.article_type == "thesaurus":
            fallback_tags.extend(["technical term", "terminology", "definition", "glossary"])
        elif self.article_type == "region":
            fallback_tags.extend(["regional application", "local industry", "geographic implementation"])
            
        # Ensure uniqueness
        return list(set(fallback_tags))