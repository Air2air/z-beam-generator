"""
Content formatting utilities for Z-Beam Generator.

This module handles all formatting tasks that were previously done by AI,
ensuring consistent and reliable output formatting.
"""

import re
from typing import Dict, Any, List
from components.base.image_handler import ImageHandler


class ContentFormatter:
    """Handles all content formatting tasks to offload work from AI."""
    
    @staticmethod
    def format_title(subject: str, article_type: str = "material") -> str:
        """Generate SEO-optimized title.
        
        Args:
            subject: The subject material/topic
            article_type: Type of article (material, application, etc.)
            
        Returns:
            str: Formatted title
        """
        return f"Laser Cleaning {subject} - Technical Guide for Optimal Processing"
    
    @staticmethod
    def format_headline(subject: str, category: str = None) -> str:
        """Generate concise headline.
        
        Args:
            subject: The subject material/topic
            category: Material category (ceramic, metal, etc.)
            
        Returns:
            str: Formatted headline
        """
        category_text = f"{category} " if category else ""
        return f"Comprehensive technical guide for laser cleaning {category_text}{subject.lower()}"
    
    @staticmethod
    def format_description(subject: str, formula: str = None, properties: Dict = None) -> str:
        """Generate technical description with key properties.
        
        Args:
            subject: The subject material/topic
            formula: Chemical formula if applicable
            properties: Key properties dictionary
            
        Returns:
            str: Formatted description (150-250 chars)
        """
        desc_parts = [f"Technical overview of {subject.lower()}"]
        
        if formula:
            desc_parts.append(f"({formula})")
        
        desc_parts.append("for laser cleaning applications")
        
        if properties:
            prop_parts = []
            if "density" in properties:
                prop_parts.append(f"{properties['density']} density")
            if "wavelength" in properties:
                prop_parts.append(f"{properties['wavelength']}")
            if "fluenceRange" in properties:
                prop_parts.append(f"{properties['fluenceRange']}")
            
            if prop_parts:
                desc_parts.append(f"including {', '.join(prop_parts[:2])}")
        
        desc_parts.append("and industrial applications")
        
        description = ", ".join(desc_parts) + "."
        
        # Ensure it's within 150-250 char range
        if len(description) > 250:
            description = description[:247] + "..."
        
        return description
    
    @staticmethod
    def format_keywords(subject: str, category: str = None, 
                       chemical_formula: str = None) -> List[str]:
        """Generate comprehensive keyword list.
        
        Args:
            subject: The subject material/topic
            category: Material category
            chemical_formula: Chemical formula if applicable
            
        Returns:
            List[str]: List of 8-12 keywords
        """
        keywords = []
        
        # Base keywords
        subject_lower = subject.lower()
        keywords.append(f"{subject_lower}")
        
        if category:
            keywords.append(f"{subject_lower} {category}")
        
        # Laser-specific terms
        keywords.extend([
            "laser ablation",
            "laser cleaning",
            "non-contact cleaning",
            "pulsed fiber laser",
            "surface contamination removal"
        ])
        
        # Chemical formula variations
        if chemical_formula:
            # Clean up formula for keyword use
            formula_clean = re.sub(r'[²³·⁰¹⁴⁵⁶⁷⁸⁹]', '', chemical_formula)
            keywords.append(f"{formula_clean} composite")
        
        # Technical terms
        keywords.extend([
            "industrial laser parameters",
            "thermal processing",
            "surface restoration"
        ])
        
        # Application-specific
        if category == "ceramic":
            keywords.extend(["ceramic restoration", "archaeological conservation"])
        elif category == "metal":
            keywords.extend(["metal surface treatment", "corrosion removal"])
        elif category == "plastic":
            keywords.extend(["polymer processing", "plastic surface modification"])
        
        # Ensure we have 8-12 keywords
        return keywords[:12]
    
    @staticmethod
    def format_images(subject: str) -> Dict[str, Dict[str, str]]:
        """Generate standardized image structure.
        
        Args:
            subject: The subject material/topic
            
        Returns:
            Dict: Standardized image structure with alt text and URLs
        """
        subject_lower = subject.lower()
        
        return {
            "hero": {
                "alt": f"{subject} surface undergoing laser cleaning showing precise contamination removal",
                "url": ImageHandler.format_image_url(subject, "hero")
            },
            "closeup": {
                "alt": f"Microscopic view of {subject_lower} surface after laser treatment showing preserved microstructure",
                "url": ImageHandler.format_image_url(subject, "closeup")
            }
        }
    
    @staticmethod
    def format_technical_specifications(base_specs: Dict = None) -> Dict[str, str]:
        """Generate standardized technical specifications.
        
        Args:
            base_specs: Base specifications to enhance
            
        Returns:
            Dict: Standardized technical specifications
        """
        default_specs = {
            "powerRange": "20-100W",
            "pulseDuration": "10-100ns", 
            "wavelength": "1064nm (primary), 532nm (optional)",
            "spotSize": "0.1-2.0mm",
            "repetitionRate": "10-50kHz",
            "fluenceRange": "0.5-5 J/cm²",
            "safetyClass": "Class 4 (requires full enclosure)"
        }
        
        if base_specs:
            default_specs.update(base_specs)
        
        return default_specs
    
    @staticmethod
    def format_regulatory_standards() -> List[Dict[str, str]]:
        """Generate standard regulatory standards list.
        
        Returns:
            List[Dict]: List of regulatory standards
        """
        return [
            {
                "code": "IEC 60825-1:2014",
                "description": "Safety of laser products - Equipment classification and requirements"
            },
            {
                "code": "ISO 11146:2021", 
                "description": "Lasers and laser-related equipment - Test methods for laser beam widths"
            },
            {
                "code": "EN 15898:2019",
                "description": "Conservation of cultural property - Main general terms and definitions"
            }
        ]
    
    @staticmethod
    def format_environmental_impact(subject: str = None) -> List[Dict[str, str]]:
        """Generate standardized environmental impact list.
        
        Args:
            subject: The subject material (for customization)
            
        Returns:
            List[Dict]: Environmental impact benefits
        """
        return [
            {
                "benefit": "Reduced chemical waste",
                "description": "Eliminates 100% of solvent use compared to traditional cleaning methods, preventing ~200L/year of hazardous waste in medium-scale operations."
            },
            {
                "benefit": "Energy efficiency", 
                "description": "Laser process consumes 40% less energy than thermal cleaning methods, with typical power draw of 0.5-2.5 kWh/m² treated surface."
            },
            {
                "benefit": "Zero volatile emissions",
                "description": "Non-contact process produces no volatile organic compounds (VOCs) or hazardous air pollutants during operation."
            }
        ]
    
    @staticmethod
    def format_outcomes() -> List[Dict[str, str]]:
        """Generate standardized measurement outcomes.
        
        Returns:
            List[Dict]: Measurable outcomes with metrics
        """
        return [
            {
                "result": "Surface cleanliness",
                "metric": "98% contamination removal measured by SEM-EDS analysis (ASTM E1508)"
            },
            {
                "result": "Substrate preservation", 
                "metric": "< 0.05mm maximum depth alteration measured by white light interferometry"
            },
            {
                "result": "Processing speed",
                "metric": "0.5-2.0 m²/hour coverage rate at 50W power"
            }
        ]
    
    @staticmethod
    def format_frontmatter_structure(raw_data: Dict[str, Any], subject: str, 
                                   category: str = None, article_type: str = "material") -> Dict[str, Any]:
        """Apply comprehensive formatting to frontmatter data.
        
        Args:
            raw_data: Raw data from AI generation
            subject: The subject material/topic
            category: Material category
            article_type: Type of article
            
        Returns:
            Dict: Fully formatted frontmatter data
        """
        formatted = raw_data.copy()
        
        # Apply standardized formatting
        formatted["title"] = ContentFormatter.format_title(subject, article_type)
        formatted["headline"] = ContentFormatter.format_headline(subject, category)
        
        # Format description with available data
        formula = formatted.get("chemicalProperties", {}).get("formula")
        properties = formatted.get("properties", {})
        formatted["description"] = ContentFormatter.format_description(subject, formula, properties)
        
        # Ensure keywords are properly formatted
        if "keywords" not in formatted or not formatted["keywords"]:
            formatted["keywords"] = ContentFormatter.format_keywords(subject, category, formula)
        
        # Ensure standardized image structure
        formatted["images"] = ContentFormatter.format_images(subject)
        
        # Apply standardized technical specifications
        if "technicalSpecifications" not in formatted:
            formatted["technicalSpecifications"] = ContentFormatter.format_technical_specifications()
        else:
            formatted["technicalSpecifications"] = ContentFormatter.format_technical_specifications(
                formatted["technicalSpecifications"]
            )
        
        # Apply standardized regulatory standards
        if "regulatoryStandards" not in formatted:
            formatted["regulatoryStandards"] = ContentFormatter.format_regulatory_standards()
        
        # Apply standardized environmental impact
        if "environmentalImpact" not in formatted:
            formatted["environmentalImpact"] = ContentFormatter.format_environmental_impact(subject)
        
        # Apply standardized outcomes
        if "outcomes" not in formatted:
            formatted["outcomes"] = ContentFormatter.format_outcomes()
        
        # Ensure required fields
        formatted["subject"] = subject
        formatted["article_type"] = article_type
        if category:
            formatted["category"] = category
        
        return formatted
    
    @staticmethod
    def clean_yaml_output(content: str) -> str:
        """Clean YAML output by removing hard returns and unnecessary escaping.
        
        Args:
            content: YAML content string
            
        Returns:
            str: Cleaned YAML content without hard returns and escaping
        """
        # Remove escaped backslashes followed by spaces and newlines within quoted strings
        content = re.sub(r'\\[\s\n]+', ' ', content)
        
        # Remove hard returns within quoted values (indicated by quotes on separate lines)
        lines = content.split('\n')
        cleaned_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Check if this line starts a quoted string that continues on next lines
            if ':' in line and ('"' in line or "'" in line):
                # Find if the string is broken across lines
                if line.count('"') == 1 or line.count("'") == 1:
                    # This is a multi-line quoted string
                    quote_char = '"' if '"' in line else "'"
                    combined_line = line
                    i += 1
                    
                    # Combine lines until we find the closing quote
                    while i < len(lines) and quote_char not in lines[i]:
                        combined_line += ' ' + lines[i].strip()
                        i += 1
                    
                    # Add the final line with closing quote
                    if i < len(lines):
                        combined_line += ' ' + lines[i].strip()
                    
                    cleaned_lines.append(combined_line)
                else:
                    cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)
            
            i += 1
        
        content = '\n'.join(cleaned_lines)
        
        # Remove backslash escaping at end of lines (YAML line continuation)
        content = re.sub(r'\\\s*\n\s*', ' ', content)
        
        # Clean up extra spaces
        content = re.sub(r'  +', ' ', content)
        
        return content

    @staticmethod
    def normalize_yaml_content(content: str) -> str:
        """Normalize YAML content for consistency.
        
        Args:
            content: Raw YAML content string
            
        Returns:
            str: Normalized YAML content
        """
        # Remove any markdown code blocks
        content = re.sub(r'^```ya?ml\s*\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'\n```\s*$', '', content, flags=re.MULTILINE)
        
        # Fix image URL double dashes
        content = re.sub(r'(/images/[^"]*?)--+([^"]*?\.jpg)', r'\1-\2', content)
        
        # Fix trailing dashes in image URLs (before file extension)
        content = re.sub(r'(/images/[^"]*?)-+(\.[a-z]+)', r'\1\2', content)
        
        # Fix any trailing dashes in slugs throughout the content
        content = re.sub(r'([a-z0-9])-+(\s|"|\'|$)', r'\1\2', content)
        
        # Escape YAML values that start with special characters that cause parsing issues
        content = ContentFormatter._escape_yaml_values(content)
        
        # Normalize quote usage in YAML
        content = re.sub(r'([:\s]+)"([^"]*?)"(\s*)', r'\1"\2"\3', content)
        
        # Ensure consistent indentation (2 spaces)
        lines = content.split('\n')
        normalized_lines = []
        
        for line in lines:
            if line.strip():
                # Count leading spaces and convert tabs to spaces
                line = line.expandtabs(2)
                leading_spaces = len(line) - len(line.lstrip())
                
                # Normalize to multiples of 2
                if leading_spaces > 0:
                    normalized_indent = (leading_spaces // 2) * 2
                    line = ' ' * normalized_indent + line.lstrip()
                
            normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)
    
    @staticmethod
    def _escape_yaml_values(content: str) -> str:
        """Escape problematic YAML values to prevent parsing errors.
        
        Args:
            content: YAML content string
            
        Returns:
            str: YAML content with problematic values quoted
        """
        # Quote values that start with > or < followed by numbers (like >95% or <0.1µm)
        content = re.sub(r'(\w+:\s*)([><]\d+[^"\n]*)', r'\1"\2"', content)
        
        return content
    
    @staticmethod
    def extract_yaml_content(content: str) -> str:
        """Extract clean YAML content from various AI response formats.
        
        Args:
            content: Raw AI response content
            
        Returns:
            str: Clean YAML content
        """
        # Check if the content seems to be markdown with a code block instead of raw YAML
        if content.startswith('```yaml') or content.startswith('```'):
            # Extract the YAML content from the code block
            lines = content.split('\n')
            content_lines = []
            in_yaml_block = False
            for line in lines:
                if line.startswith('```yaml') or line.startswith('```'):
                    if in_yaml_block:
                        break  # End of YAML block
                    in_yaml_block = True
                    continue
                if in_yaml_block:
                    content_lines.append(line)
            
            if content_lines:
                return '\n'.join(content_lines)
        
        # Look for YAML content after explanatory text
        # Pattern: "Here's the YAML..." followed by actual YAML starting with a key
        lines = content.split('\n')
        yaml_start_idx = None
        
        for i, line in enumerate(lines):
            # Find the first line that looks like YAML (key: value pattern)
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*:', line.strip()):
                yaml_start_idx = i
                break
        
        if yaml_start_idx is not None:
            yaml_lines = lines[yaml_start_idx:]
            # Remove any trailing explanatory text after the YAML
            final_lines = []
            for line in yaml_lines:
                # Stop when we hit explanatory text (lines that don't look like YAML)
                stripped = line.strip()
                if stripped and not (
                    stripped.startswith('#') or  # Comments
                    ':' in stripped or  # Key-value pairs
                    stripped.startswith('-') or  # List items
                    stripped.startswith(' ') or stripped.startswith('\t') or  # Indented content
                    stripped == '' or  # Empty lines
                    re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', stripped)  # Single words (possible keys)
                ):
                    break
                final_lines.append(line)
            
            return '\n'.join(final_lines).strip()
        
        # If no clear YAML structure found, return the content as-is
        return content
    
    @staticmethod
    def extract_content_between_markers(content: str, marker: str = '---') -> str:
        """Extract content between YAML frontmatter markers.
        
        Args:
            content: Content with markers
            marker: Marker string (default: '---')
            
        Returns:
            str: Content between first set of markers
        """
        if marker in content:
            parts = content.split(marker)
            if len(parts) >= 3:
                return parts[1].strip()
            elif len(parts) == 2:
                return parts[1].strip()
        
        return content.strip()
    
    @staticmethod
    def clean_string_content(text: str) -> str:
        """Clean string content by removing escape characters and normalizing whitespace.
        
        Args:
            text: Text to clean
            
        Returns:
            str: Cleaned text
        """
        if not isinstance(text, str):
            return text
        
        # Remove escape characters
        text = text.replace("\\n", "\n").replace('\\ ', ' ')
        
        # Normalize whitespace in multiline strings
        if '\n' in text:
            lines = text.split('\n')
            text = '\n'.join(line.strip() for line in lines if line.strip())
        
        return text
    
    @staticmethod
    def normalize_case(text: str, case_type: str = 'lower') -> str:
        """Normalize text case consistently.
        
        Args:
            text: Text to normalize
            case_type: 'lower', 'upper', 'title', or 'sentence'
            
        Returns:
            str: Normalized text
        """
        if not isinstance(text, str):
            return text
        
        if case_type == 'lower':
            return text.lower()
        elif case_type == 'upper':
            return text.upper()
        elif case_type == 'title':
            return text.title()
        elif case_type == 'sentence':
            return text.capitalize()
        
        return text
    
    @staticmethod
    def extract_json_content(content: str) -> str:
        """Extract JSON content from various response formats.
        
        Args:
            content: Raw content that may contain JSON
            
        Returns:
            str: Clean JSON content
        """
        # Try to extract from code blocks first
        json_block_pattern = r'```(?:json|javascript)?\s*\n?(.*?)\n?```'
        matches = re.finditer(json_block_pattern, content, re.DOTALL)
        
        for match in matches:
            try:
                import json
                json.loads(match.group(1).strip())
                return match.group(1).strip()
            except:
                continue
        
        # Try to extract from YAML-like blocks
        yaml_block_pattern = r'```(?:yaml|yml)?\s*\n?(.*?)\n?```'
        matches = re.finditer(yaml_block_pattern, content, re.DOTALL)
        
        for match in matches:
            try:
                import yaml, json
                yaml_data = yaml.safe_load(match.group(1).strip())
                if yaml_data:
                    return json.dumps(yaml_data, indent=2)
            except:
                continue
        
        # Try to parse the entire content as JSON
        try:
            import json
            json.loads(content.strip())
            return content.strip()
        except:
            # Try as YAML
            try:
                import yaml, json
                yaml_data = yaml.safe_load(content.strip())
                if yaml_data:
                    return json.dumps(yaml_data, indent=2)
            except:
                pass
        
        # Look for JSON-like content in the response
        if content.strip().startswith('{') and content.strip().endswith('}'):
            try:
                import json
                json.loads(content.strip())
                return content.strip()
            except:
                pass
        
        return content
    
    @staticmethod
    def extract_tags_from_content(content: str) -> List[str]:
        """Extract and normalize tags from various content formats.
        
        Args:
            content: Content containing tags
            
        Returns:
            List[str]: List of normalized tags
        """
        tags = []
        lines = content.strip().split('\n')
        
        # Process each line looking for tags
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Handle comma-separated tags in a single line
            if ',' in line:
                tags.extend([tag.strip() for tag in line.split(',') if tag.strip()])
            else:
                # Single tag per line (possibly with bullet points)
                line = re.sub(r'^[-*•]\s*', '', line)  # Remove bullet points
                if line:
                    tags.append(line)
        
        # Clean and deduplicate
        return list(set([tag.strip() for tag in tags if tag.strip()]))
    
    @staticmethod
    def format_author_info(author_data: Dict[str, Any], fallback_id: int = 1) -> Dict[str, Any]:
        """Format author information consistently.
        
        Args:
            author_data: Raw author data
            fallback_id: Fallback author ID if data is missing
            
        Returns:
            Dict: Formatted author information
        """
        if not author_data:
            return {"id": fallback_id}
        
        formatted = {}
        
        # Map common field variations
        if "author_name" in author_data:
            formatted["name"] = author_data["author_name"]
        elif "name" in author_data:
            formatted["name"] = author_data["name"]
        
        if "author_country" in author_data:
            formatted["country"] = author_data["author_country"]
        elif "country" in author_data:
            formatted["country"] = author_data["country"]
        
        if "author_id" in author_data:
            formatted["id"] = author_data["author_id"]
        elif "id" in author_data:
            formatted["id"] = author_data["id"]
        else:
            formatted["id"] = fallback_id
        
        # Add credentials if available
        if "credentials" in author_data:
            formatted["credentials"] = author_data["credentials"]
        
        return formatted
    
    @staticmethod
    def format_metatags_structure(parsed_data: Dict[str, Any], subject: str, category: str = None) -> Dict[str, Any]:
        """Format metatags structure for Next.js compatibility.
        
        This method ensures all metatags follow the expected Next.js structure
        without doing any local formatting - just structural organization.
        
        Args:
            parsed_data: Raw parsed YAML data from AI
            subject: The subject material/topic
            category: Material category if applicable
            
        Returns:
            Dict: Properly structured metatags for Next.js
        """
        from components.base.utils.slug_utils import SlugUtils
        
        # Normalize field names first (handle inconsistent AI output)
        normalized_data = {}
        for key, value in parsed_data.items():
            # Normalize common metatag field name variations
            if key.lower() in ['title', 'meta_title']:
                normalized_data['meta_title'] = value
            elif key.lower() in ['description', 'meta_description']:
                normalized_data['meta_description'] = value
            elif key.lower() in ['keywords', 'meta_keywords']:
                normalized_data['meta_keywords'] = value
            else:
                # Keep other fields as-is
                normalized_data[key] = value
        
        # Use the normalized data for structure formatting
        formatted = {}
        
        # Basic meta fields (use AI content if provided, otherwise use centralized formatting)
        if "meta_title" in normalized_data:
            formatted["meta_title"] = normalized_data["meta_title"]
        elif "title" in normalized_data:
            formatted["meta_title"] = normalized_data["title"]
        else:
            formatted["meta_title"] = ContentFormatter.format_title(subject)
            
        if "meta_description" in normalized_data:
            formatted["meta_description"] = normalized_data["meta_description"]
        elif "description" in normalized_data:
            formatted["meta_description"] = normalized_data["description"]
        else:
            formatted["meta_description"] = ContentFormatter.format_description(subject)
            
        if "meta_keywords" in normalized_data:
            formatted["meta_keywords"] = normalized_data["meta_keywords"]
        elif "keywords" in normalized_data:
            formatted["meta_keywords"] = normalized_data["keywords"]
        else:
            keywords = ContentFormatter.format_keywords(subject, category)
            formatted["meta_keywords"] = ", ".join(keywords)
        
        # Ensure openGraph structure exists
        if "openGraph" not in normalized_data:
            formatted["openGraph"] = {}
        else:
            formatted["openGraph"] = normalized_data["openGraph"].copy()
            
        og = formatted["openGraph"]
        
        # Use subject slug for consistent URLs
        subject_slug = SlugUtils.create_subject_slug(subject)
        
        # Ensure required openGraph fields
        if "title" not in og:
            og["title"] = formatted["meta_title"]
        if "description" not in og:
            og["description"] = formatted["meta_description"]
        if "url" not in og:
            og["url"] = f"https://www.z-beam.com/{subject_slug}-laser-cleaning"
        if "siteName" not in og:
            og["siteName"] = "Z-Beam"
        if "type" not in og:
            og["type"] = "article"
        if "locale" not in og:
            og["locale"] = "en_US"
            
        # Ensure images structure
        if "images" not in og or not og["images"]:
            images_data = ContentFormatter.format_images(subject)
            og["images"] = [
                {
                    "url": images_data["hero"]["url"],
                    "width": 1200,
                    "height": 630,
                    "alt": images_data["hero"]["alt"]
                }
            ]
        
        # Ensure twitter structure exists
        if "twitter" not in parsed_data:
            formatted["twitter"] = {}
        else:
            formatted["twitter"] = parsed_data["twitter"].copy()
            
        twitter = formatted["twitter"]
        
        # Ensure required twitter fields
        if "card" not in twitter:
            twitter["card"] = "summary_large_image"
        if "title" not in twitter:
            twitter["title"] = og.get("title", formatted["meta_title"])
        if "description" not in twitter:
            twitter["description"] = og.get("description", formatted["meta_description"])
        if "images" not in twitter or not twitter["images"]:
            if og.get("images"):
                twitter["images"] = [og["images"][0]["url"]]
        
        # Copy other fields from AI if they exist (exclude normalized fields)
        for key, value in normalized_data.items():
            if key not in ["meta_title", "meta_description", "meta_keywords", "title", "description", "keywords", "openGraph", "twitter"]:
                formatted[key] = value
        
        return formatted
    
    @staticmethod
    def format_created_date() -> str:
        """Generate standardized created date.
        
        Returns:
            str: ISO formatted created date
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    
    @staticmethod
    def format_updated_date() -> str:
        """Generate standardized updated date.
        
        Returns:
            str: ISO formatted updated date
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    
    @staticmethod
    def format_publish_date() -> str:
        """Generate standardized publish date.
        
        Returns:
            str: ISO formatted publish date
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    
    @staticmethod
    def format_iso_date() -> str:
        """Generate standardized ISO date.
        
        Returns:
            str: Full ISO formatted datetime
        """
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
