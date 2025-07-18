import logging
import random
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class FrontmatterProcessor:
    """Process frontmatter data for content generation."""
    
    @staticmethod
    def detect_content_sections(frontmatter: Dict[str, Any], article_type: str = None, 
                               randomize_order: bool = False) -> List[Dict[str, Any]]:
        """
        Detect which frontmatter fields can be used as content sections.
        
        Args:
            frontmatter: The frontmatter dictionary
            article_type: Optional article type for type-specific detection
            randomize_order: Whether to randomize section order
            
        Returns:
            List of section objects with id, title, and frontmatter_field
        """
        if not frontmatter:
            return []
            
        # Map frontmatter fields to section names
        section_mapping = {
            "description": "overview",
            "applications": "applications", 
            "technicalSpecifications": "technicalSpecifications",
            "facilities": "facilities",
            "regulatoryStandards": "regulations",
            "challenges": "challenges",
            "outcomes": "outcomes",
            "qualityStandards": "qualityStandards",
            "benefits": "benefits",
            "properties": "specifications"
        }
        
        # Find valid sections based on available frontmatter
        sections = []
        for field, section_id in section_mapping.items():
            if field in frontmatter and frontmatter[field]:
                sections.append({
                    "id": section_id,
                    "title": FrontmatterProcessor.format_section_title(section_id),
                    "frontmatter_field": field
                })
                
        # Basic priority ordering for sections (unless randomized)
        if sections and not randomize_order:
            priority_order = ["overview", "applications", "specifications", "technicalSpecifications", 
                             "facilities", "challenges", "outcomes", "benefits", "regulations", "qualityStandards"]
            
            # Sort sections by priority (index in priority_order)
            sections.sort(key=lambda x: (
                priority_order.index(x["id"]) if x["id"] in priority_order else 999
            ))
        elif sections and randomize_order:
            # Randomly shuffle sections
            random.shuffle(sections)
            
            # But ensure overview is always first if it exists
            overview = next((s for s in sections if s["id"] == "overview"), None)
            if overview:
                sections.remove(overview)
                sections.insert(0, overview)
        
        return sections
    
    @staticmethod
    def format_section_title(section_id: str) -> str:
        """Format a section ID into a readable title."""
        # Special case formatting for specific sections
        title_mapping = {
            "technicalSpecifications": "Technical Specifications",
            "regulatoryStandards": "Regulatory Standards",
            "qualityStandards": "Quality Standards",
            "overview": "Overview",
            "applications": "Applications",
            "facilities": "Facilities",
            "regulations": "Regulations",
            "challenges": "Challenges",
            "outcomes": "Outcomes",
            "benefits": "Benefits",
            "specifications": "Specifications"
        }
        
        if section_id in title_mapping:
            return title_mapping[section_id]
            
        # Default formatting: capitalize each word
        return " ".join(word.capitalize() for word in section_id.split("_"))
    
    @staticmethod
    def format_section_data(field_name: str, data: Any) -> str:
        """Format frontmatter data into a string for content generation."""
        if data is None:
            return ""
            
        if isinstance(data, str):
            return data
        
        elif isinstance(data, list):
            if not data:
                return ""
                
            if isinstance(data[0], dict):
                # Handle list of dictionaries
                items = []
                for item in data:
                    if "name" in item and "description" in item:
                        items.append(f"- {item['name']}: {item['description']}")
                    elif "code" in item and "description" in item:
                        items.append(f"- {item['code']}: {item['description']}")
                    elif "issue" in item and "solution" in item:
                        items.append(f"- {item['issue']} - Solution: {item['solution']}")
                    elif "name" in item:
                        items.append(f"- {item['name']}")
                    elif "code" in item:
                        items.append(f"- {item['code']}")
                    else:
                        # Use first key-value pair
                        if item:
                            first_key = next(iter(item))
                            items.append(f"- {first_key}: {item[first_key]}")
                
                return "\n".join(items)
            else:
                # Simple list of strings
                return "\n".join([f"- {item}" for item in data])
        
        elif isinstance(data, dict):
            # Handle dictionary (like technicalSpecifications)
            return "\n".join([f"- {key}: {value}" for key, value in data.items()])
        
        # Default for other types
        return str(data)
    
    @staticmethod
    def create_section_prompt(section: Dict[str, Any], subject: str, section_data: str, 
                             words_per_section: int) -> str:
        """Create a prompt for a section based on its data."""
        section_id = section["id"]
        section_title = section["title"]
        
        # Base prompt structure
        prompt = f"## {section_title}\n\n"
        
        # Section-specific guidance
        if section_id == "overview":
            prompt += f"Write a comprehensive overview about {subject} based on this description:\n{section_data}\n\n"
            prompt += "Expand on the key points, focusing on the importance and general context."
            
        elif section_id == "applications":
            prompt += f"Detail the applications of {subject} based on these items:\n{section_data}\n\n"
            prompt += "For each application, explain its significance and specific benefits."
            
        elif section_id in ["technicalSpecifications", "specifications"]:
            prompt += f"Explain these technical specifications for {subject}:\n{section_data}\n\n"
            prompt += "Describe why each specification is important and how it affects performance."
            
        elif section_id == "facilities":
            prompt += f"Describe the facilities related to {subject} based on:\n{section_data}\n\n"
            prompt += "Highlight the capabilities and significance of each facility."
            
        elif section_id in ["regulations", "regulatoryStandards"]:
            prompt += f"Explain these regulatory standards applicable to {subject}:\n{section_data}\n\n"
            prompt += "Describe the impact and compliance requirements for each regulation."
            
        elif section_id == "challenges":
            prompt += f"Discuss these challenges related to {subject}:\n{section_data}\n\n"
            prompt += "For each challenge, explain the issue and how the solution addresses it effectively."
            
        elif section_id == "outcomes":
            prompt += f"Detail these performance outcomes for {subject}:\n{section_data}\n\n"
            prompt += "Explain the significance of each result and how it compares to industry standards."
            
        elif section_id in ["qualityStandards", "standards"]:
            prompt += f"Describe these quality standards relevant to {subject}:\n{section_data}\n\n"
            prompt += "Explain how each standard ensures optimal performance and reliability."
            
        elif section_id == "benefits":
            prompt += f"Explain the key benefits of {subject} based on:\n{section_data}\n\n"
            prompt += "Elaborate on why these benefits are important and how they compare to alternatives."
            
        else:
            # Generic section prompt
            prompt += f"Write about {section_title.lower()} of {subject} based on this information:\n{section_data}\n\n"
            prompt += "Provide comprehensive details and explain their significance."
        
        # Add word count guidance
        prompt += f"\n\nWrite approximately {words_per_section} words for this section."
        
        return prompt
    
    @staticmethod
    def extract_frontmatter_context(frontmatter: Dict[str, Any], article_type: str) -> str:
        """Extract relevant data from frontmatter to enrich content."""
        if not frontmatter:
            return ""
            
        context_parts = []
        
        # Common fields across all types
        if "description" in frontmatter:
            context_parts.append(f"Description: {frontmatter['description']}")
            
        if "keywords" in frontmatter and isinstance(frontmatter["keywords"], list):
            context_parts.append(f"Keywords: {', '.join(frontmatter['keywords'])}")
        
        # Extract article type specific context
        if article_type == "material":
            # Extract material properties
            if "properties" in frontmatter:
                props = frontmatter["properties"]
                if isinstance(props, dict):
                    for key, value in props.items():
                        context_parts.append(f"{key}: {value}")
                        
            # Extract compatibility information
            if "compatibility" in frontmatter:
                compat = frontmatter["compatibility"]
                if isinstance(compat, list):
                    context_parts.append(f"Compatible with: {', '.join(compat)}")
                    
        elif article_type == "region":
            # Extract region-specific data
            if "location" in frontmatter:
                loc = frontmatter["location"]
                if isinstance(loc, dict):
                    city = loc.get("city", "")
                    state = loc.get("state", "")
                    country = loc.get("country", "")
                    context_parts.append(f"Location: {city}, {state}, {country}")
                    
            # Extract regional industries
            if "industries" in frontmatter and isinstance(frontmatter["industries"], list):
                context_parts.append(f"Key Industries: {', '.join(frontmatter['industries'])}")
        
        # Extract regulatory standards if available
        if "regulatoryStandards" in frontmatter and isinstance(frontmatter["regulatoryStandards"], list):
            standards = []
            for std in frontmatter["regulatoryStandards"]:
                if isinstance(std, dict) and "code" in std:
                    standards.append(std["code"])
                elif isinstance(std, str):
                    standards.append(std)
            if standards:
                context_parts.append(f"Regulatory Standards: {', '.join(standards)}")
        
        # Join all context parts
        return "\n".join(context_parts)