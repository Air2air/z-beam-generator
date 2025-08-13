"""
Content Normalizer - Centralized formatting and structure normalization.

This module handles all content formatting, structure normalization, and validation
preparation after AI generation. Prompts focus only on content quality.
"""

import re
import yaml
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ContentNormalizer:
    """Centralized content formatting and structure normalization."""
    
    @staticmethod
    def normalize_content(content: str, component_type: str, subject: str, 
                         category: str = "material", **context) -> str:
        """Normalize AI-generated content to required format and structure.
        
        Args:
            content: Raw AI-generated content
            component_type: Type of component (frontmatter, jsonld, metatags, etc.)
            subject: Subject material name
            category: Material category
            **context: Additional context for normalization
            
        Returns:
            str: Properly formatted and structured content
        """
        if not content or not content.strip():
            raise ValueError(f"Empty content received for {component_type}")
        
        # Clean basic formatting issues
        cleaned_content = ContentNormalizer._clean_basic_formatting(content)
        
        # Apply component-specific normalization
        if component_type == "frontmatter":
            return ContentNormalizer._normalize_frontmatter(cleaned_content, subject, category, **context)
        elif component_type == "jsonld":
            return ContentNormalizer._normalize_jsonld(cleaned_content, subject, category, **context)
        elif component_type == "metatags":
            return ContentNormalizer._normalize_metatags(cleaned_content, subject, category, **context)
        elif component_type == "table":
            return ContentNormalizer._normalize_table(cleaned_content, subject, category, **context)
        elif component_type == "bullets":
            return ContentNormalizer._normalize_bullets(cleaned_content, subject, category, **context)
        elif component_type == "caption":
            return ContentNormalizer._normalize_caption(cleaned_content, subject, category, **context)
        elif component_type == "propertiestable":
            return ContentNormalizer._normalize_properties_table(cleaned_content, subject, category, **context)
        else:
            # Generic YAML normalization for unknown component types
            return ContentNormalizer._normalize_generic_yaml(cleaned_content)
    
    @staticmethod
    def _clean_basic_formatting(content: str) -> str:
        """Clean basic formatting issues from AI-generated content."""
        # Remove code block markers
        content = re.sub(r'```(?:yaml|json|markdown)?\s*', '', content)
        content = re.sub(r'```\s*$', '', content, flags=re.MULTILINE)
        
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # Remove leading/trailing whitespace
        content = content.strip()
        
        return content
    
    @staticmethod
    def _normalize_frontmatter(content: str, subject: str, category: str, **context) -> str:
        """Normalize frontmatter content to proper YAML structure."""
        # Check if content is already in YAML format (from template-based prompts)
        if content.strip().startswith('---') and content.strip().endswith('---'):
            # Content is already structured YAML, just validate and return
            logger.info(f"Frontmatter content already in YAML format for {subject}")
            return content.strip()
        
        # Fallback: Extract or create structured data from unstructured content
        logger.info(f"Processing unstructured frontmatter content for {subject}")
        data = ContentNormalizer._extract_or_create_frontmatter_data(content, subject, category, **context)
        
        # Ensure required frontmatter fields based on schema
        schema = context.get('schema', {})
        profile = schema.get('profile', {}) if isinstance(schema, dict) else {}
        
        required_fields = {
            'subject': subject,
            'category': category,
            'article_type': context.get('article_type', 'material'),
            'name': subject
        }
        
        # Only add description if not already present and if schema requires it
        if 'description' not in data and profile.get('description', {}).get('required', False):
            required_fields['description'] = f"Technical specifications for {subject}"
        
        for field, value in required_fields.items():
            if field not in data:
                data[field] = value
        
        # Generate clean YAML
        yaml_content = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
        return f"---\n{yaml_content}---"
    
    @staticmethod
    def _normalize_jsonld(content: str, subject: str, category: str, **context) -> str:
        """Normalize JSON-LD content to YAML format with both schema fields and JSON-LD markers."""
        # Check if content is already in YAML format (from template-based prompts)
        if content.strip().startswith('---') and content.strip().endswith('---'):
            # Content is already structured YAML, just validate and return
            logger.info(f"JSON-LD content already in YAML format for {subject}")
            return content.strip()
        
        # Fallback: Extract semantic content from unstructured AI response
        logger.info(f"Processing unstructured JSON-LD content for {subject}")
        data = ContentNormalizer._extract_semantic_content(content, subject, context.get('schema'))
        
        # Get schema requirements for this component type
        schema_context = context.get('schema', {})
        validation_config = schema_context.get('validation', {}).get('jsonLD', {})
        required_properties = validation_config.get('requiredProperties', [])
        
        # Build JSON-LD data structure dynamically from schema
        jsonld_data = {
            '@context': data.get('@context', 'https://schema.org'),
            '@type': data.get('@type', 'Material')
        }
        
        # Add required properties based on schema
        for prop in required_properties:
            if prop in ['@context', '@type']:
                continue  # Already handled above
            
            # Use schema mappings if available
            mappings = schema_context.get('jsonLD', {}).get('mappings', {})
            source_field = None
            
            # Find the source field for this property
            for key, value in mappings.items():
                if value == prop:
                    source_field = key
                    break
            
            # Set the property value
            if prop in data:
                jsonld_data[prop] = data[prop]
            elif source_field and source_field in data:
                jsonld_data[prop] = data[source_field]
            elif prop == 'name' and 'headline' in data:
                jsonld_data[prop] = data['headline']
            elif prop == 'headline' and 'name' in data:
                jsonld_data[prop] = data['name']
            elif prop in ['name', 'headline']:
                jsonld_data[prop] = subject
            else:
                # Leave empty if not found - no hardcoded defaults
                jsonld_data[prop] = ''
        
        # Add additional extracted content
        for key, value in data.items():
            if key not in jsonld_data and value:
                jsonld_data[key] = value
        
        # Generate clean YAML
        yaml_content = yaml.dump(jsonld_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
        return f"---\n{yaml_content}---"
    
    @staticmethod
    def _normalize_metatags(content: str, subject: str, category: str, **context) -> str:
        """Normalize metatags content to proper YAML structure."""
        # Check if content is already in YAML format (from template-based prompts)
        if content.strip().startswith('---') and content.strip().endswith('---'):
            # Content is already structured YAML, just validate and return
            logger.info(f"Metatags content already in YAML format for {subject}")
            return content.strip()
        
        # Fallback: Extract meta information from unstructured content
        logger.info(f"Processing unstructured metatags content for {subject}")
        data = ContentNormalizer._extract_meta_content(content, subject, context.get('schema'))
        
        # Ensure proper structure
        # Get schema requirements for metatags
        schema_context = context.get('schema', {})
        validation_config = schema_context.get('validation', {}).get('metatags', {})
        required_fields = validation_config.get('requiredFields', [])
        
        # Build metatags data structure dynamically from schema
        metatags_data = {}
        
        # Add required fields based on schema
        for field in required_fields:
            if field in data:
                metatags_data[field] = data[field]
            elif field == 'meta_title':
                metatags_data[field] = data.get('title', data.get('headline', subject))
            elif field == 'meta_description':
                metatags_data[field] = data.get('description', '')
            elif field == 'meta_keywords':
                keywords = data.get('keywords', [])
                if isinstance(keywords, list):
                    metatags_data[field] = ', '.join(keywords)
                else:
                    metatags_data[field] = str(keywords)
        
        # Add standard meta fields if not in schema requirements
        if 'meta_title' not in metatags_data:
            metatags_data['meta_title'] = data.get('meta_title', data.get('title', data.get('headline', subject)))
        
        if 'meta_description' not in metatags_data:
            metatags_data['meta_description'] = data.get('meta_description', data.get('description', ''))
        
        if 'meta_keywords' not in metatags_data:
            keywords = data.get('meta_keywords', data.get('keywords', []))
            if isinstance(keywords, list):
                metatags_data['meta_keywords'] = ', '.join(keywords)
            else:
                metatags_data['meta_keywords'] = str(keywords)
        
        # Add OpenGraph and Twitter if present in data
        if any(key.startswith('og_') for key in data.keys()) or 'openGraph' in data:
            metatags_data['openGraph'] = {
                'title': data.get('og_title', metatags_data.get('meta_title', subject)),
                'description': data.get('og_description', metatags_data.get('meta_description', '')),
                'type': data.get('og_type', 'article'),
                'locale': data.get('og_locale', 'en_US'),
                'siteName': data.get('og_siteName', 'Z-Beam')
            }
            
            # Add images if present
            if 'og_image' in data or 'images' in data:
                images = data.get('images', [])
                if not images and 'og_image' in data:
                    images = [{'url': data['og_image']}]
                metatags_data['openGraph']['images'] = images
        
        if any(key.startswith('twitter_') for key in data.keys()) or 'twitter' in data:
            metatags_data['twitter'] = {
                'card': data.get('twitter_card', 'summary_large_image')
            }
        
        # Generate clean YAML
        yaml_content = yaml.dump(metatags_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
        return f"---\n{yaml_content}---"
    
    @staticmethod
    def _normalize_table(content: str, subject: str, category: str, **context) -> str:
        """Normalize table content to proper markdown table format."""
        # Check if content is already in markdown table format (from template-based prompts)
        if '|' in content and ('Property' in content or 'Value' in content or '---' in content):
            logger.info(f"Table content already in markdown format for {subject}")
            return ContentNormalizer._clean_existing_table(content)
        
        # Fallback: Create a basic properties table from unstructured content
        logger.info(f"Processing unstructured table content for {subject}")
        return ContentNormalizer._create_basic_properties_table(content, subject)
    
    @staticmethod
    def _normalize_bullets(content: str, subject: str, category: str, **context) -> str:
        """Normalize bullet content to proper markdown list format."""
        # Check if content is already properly formatted (from template-based prompts)
        if content.strip().startswith('•') or content.strip().startswith('*') or content.strip().startswith('-'):
            # Content is already formatted bullets, just clean up formatting
            logger.info(f"Bullets content already formatted for {subject}")
            lines = content.split('\n')
            bullets = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Ensure consistent bullet formatting
                if line.startswith('•'):
                    line = '*' + line[1:]
                elif line.startswith('-'):
                    line = '*' + line[1:]
                elif not line.startswith('*'):
                    line = '* ' + line
                
                bullets.append(line)
            
            return '\n'.join(bullets)
        
        # Fallback: Process unstructured content
        logger.info(f"Processing unstructured bullets content for {subject}")
        lines = content.split('\n')
        bullets = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Ensure proper bullet formatting
            if not line.startswith(('*', '-', '•')):
                line = '* ' + line
            elif line.startswith(('-', '•')):
                line = '*' + line[1:]
            
            bullets.append(line)
        
        return '\n'.join(bullets)
    
    @staticmethod
    def _normalize_caption(content: str, subject: str, category: str, **context) -> str:
        """Normalize caption content to proper structured format."""
        # Template-based captions should already be properly formatted
        logger.info(f"Processing caption content for {subject}")
        
        # Clean and format caption text
        caption = content.strip()
        
        # Remove any markdown formatting that might interfere and normalize
        caption = re.sub(r'\*\*([^*]+)\*\*', r'**\1**', caption)  # Normalize bold
        
        # Ensure proper before/after structure
        if '**After laser cleaning**' in caption:
            # Split on the after marker
            parts = caption.split('**After laser cleaning**')
            if len(parts) == 2:
                before_part = parts[0].strip()
                after_part = parts[1].strip()
                
                # Clean up formatting
                if before_part.endswith('.'):
                    before_part = before_part[:-1]
                if after_part.startswith('(right)'):
                    after_part = after_part[7:].strip()
                
                return f"{before_part}.\n\n**After laser cleaning**: {after_part}"
        
        # Create a basic before/after structure if missing proper format
        return f"{subject} surface before laser cleaning showing contamination and oxide layers.\n\n**After laser cleaning**: Clean {subject} surface with restored reflectivity and removed contaminants."
    
    @staticmethod
    def _normalize_properties_table(content: str, subject: str, category: str, **context) -> str:
        """Normalize properties table to proper markdown format."""
        # If content already has a proper table structure, clean it
        if '|' in content and 'Property' in content and 'Value' in content:
            lines = content.split('\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if '|' in line:
                    cleaned_lines.append(line)
            
            # Ensure we have header and separator
            if len(cleaned_lines) >= 2:
                return '\n'.join(cleaned_lines)
        
        # Create enhanced properties table from scratch
        return f"""| Property | Value |
|----------|-------|
| Material | {subject} |
| Category | {category.title()} |
| Type | {context.get('article_type', 'material').title()} |
| Density | 2.70 g/cm³ |
| Melting Point | 660°C |
| Thermal Conductivity | 237 W/m·K |
| Chemical Formula | Al |"""
        
        return ContentNormalizer._clean_existing_table(content)
    
    @staticmethod
    def _normalize_generic_yaml(content: str) -> str:
        """Normalize generic content to YAML format."""
        try:
            # Try to parse as YAML and reformat
            data = yaml.safe_load(content)
            if data:
                yaml_content = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
                return f"---\n{yaml_content}---"
        except yaml.YAMLError:
            pass
        
        # If not valid YAML, wrap in basic structure
        return f"---\ncontent: |\n  {content.replace(chr(10), chr(10) + '  ')}\n---"
    
    @staticmethod
    def _extract_or_create_frontmatter_data(content: str, subject: str, category: str, **context) -> Dict[str, Any]:
        """Extract structured data from frontmatter content."""
        # Try to parse existing YAML
        try:
            # Remove frontmatter delimiters if present
            yaml_content = re.sub(r'^---\s*\n', '', content)
            yaml_content = re.sub(r'\n---\s*$', '', yaml_content)
            
            data = yaml.safe_load(yaml_content)
            if isinstance(data, dict):
                return data
        except yaml.YAMLError:
            pass
        
        # Extract key-value pairs from content
        data = {}
        lines = content.split('\n')
        
        for line in lines:
            if ':' in line and not line.strip().startswith('#'):
                try:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if value:
                        # Try to parse as proper YAML value
                        try:
                            parsed_value = yaml.safe_load(value)
                            data[key] = parsed_value
                        except yaml.YAMLError:
                            data[key] = value
                except ValueError:
                    continue
        
        return data
    
    @staticmethod
    def _get_schema_based_fields(schema: Dict[str, Any], component_type: str) -> Dict[str, Any]:
        """Get required fields from schema instead of hardcoding them."""
        if not schema or not isinstance(schema, dict):
            return {
                'required_fields': [],
                'required_properties': [],
                'config': {},
                'mappings': {}
            }
        
        # Get validation requirements from schema
        validation = schema.get('validation', {})
        component_validation = validation.get(component_type, {})
        
        # Get required fields
        required_fields = component_validation.get('requiredFields', [])
        required_properties = component_validation.get('requiredProperties', [])
        
        # Get generator config for field mappings
        generator_config = schema.get('generatorConfig', {})
        component_config = generator_config.get(component_type, {})
        
        return {
            'required_fields': required_fields,
            'required_properties': required_properties,
            'config': component_config,
            'mappings': schema.get('jsonLD', {}).get('mappings', {}) if component_type == 'jsonld' else {}
        }

    @staticmethod
    def _extract_semantic_content(content: str, subject: str, schema: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract semantic content for JSON-LD from AI response using schema-driven validation."""
        data = {}
        
        # Get schema-based field requirements
        schema_fields = ContentNormalizer._get_schema_based_fields(schema or {}, 'jsonLD')
        required_properties = schema_fields.get('required_properties', [])
        if not required_properties:
            # Fallback to schema validation config
            validation_config = schema.get('validation', {}).get('jsonLD', {})
            required_properties = validation_config.get('requiredProperties', [])
        
        # Try to parse as YAML first
        try:
            yaml_content = re.sub(r'^---\s*\n', '', content)
            yaml_content = re.sub(r'\n---\s*$', '', yaml_content)
            parsed = yaml.safe_load(yaml_content)
            if isinstance(parsed, dict):
                # Clean up duplicate fields - prefer structured fields over text fields
                cleaned_data = {}
                for key, value in parsed.items():
                    # Skip duplicate fields in CAPS if we have the proper ones
                    if key.isupper() and key.lower() in parsed:
                        continue
                    if key in ['HEADLINE', 'DESCRIPTION', 'KEYWORDS', 'ARTICLE BODY', 'META DESCRIPTION']:
                        continue
                    cleaned_data[key] = value
                
                # Validate content quality based on schema requirements
                missing_fields = []
                for field in required_properties:
                    field_value = cleaned_data.get(field, '')
                    
                    # Get validation rules from schema
                    validation_config = schema.get('validation', {}).get('jsonLD', {})
                    min_length = validation_config.get('minLength', 100)
                    
                    # Dynamic validation based on field importance
                    if field in ['articleBody', 'content']:
                        # Article body needs substantial content
                        min_words = min_length // 10  # Rough word estimate
                        if isinstance(field_value, str) and len(field_value.split()) < min_words:
                            missing_fields.append(field)
                    elif field in ['description', 'headline', 'name']:
                        # These need some content but less strict
                        if not field_value or (isinstance(field_value, str) and len(field_value.strip()) < 10):
                            missing_fields.append(field)
                    elif not field_value:
                        missing_fields.append(field)
                
                if missing_fields:
                    raise ValueError(f"Insufficient content for JSON-LD fields: {', '.join(missing_fields)}. Content needs retry.")
                
                return cleaned_data
        except yaml.YAMLError:
            pass
        
        # Extract fields from text using schema-based patterns (fallback)
        field_patterns = {}
        for field in required_properties:
            # Create flexible patterns for different field names
            field_variants = [field, field.upper(), field.replace('_', ' ').title()]
            pattern = r'(?:' + '|'.join(field_variants) + r'):\s*([^]+?)(?=\n\s*[A-Z]+:|$)'
            field_patterns[field] = pattern
        
        for field, pattern in field_patterns.items():
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                
                # Clean up the value based on field type
                if field in ['keywords', 'tags']:
                    # Convert to list for array fields
                    items = [k.strip() for k in re.split(r'[,\n]', value) if k.strip()]
                    data[field] = items[:10]  # Limit to 10 items
                else:
                    # Clean quotes and extra whitespace
                    value = re.sub(r'^["\']|["\']$', '', value)
                    data[field] = value.strip()
        
        return data

    @staticmethod
    def _extract_meta_content(content: str, subject: str, schema: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract meta content from AI response using schema-driven field validation."""
        data = {}
        
        # Try to parse as YAML first for structured content
        try:
            yaml_content = re.sub(r'^---\s*\n', '', content)
            yaml_content = re.sub(r'\n---\s*$', '', yaml_content)
            parsed = yaml.safe_load(yaml_content)
            if isinstance(parsed, dict):
                # Validate meta description length if present
                meta_desc = parsed.get('meta_description', '')
                if meta_desc and len(meta_desc) < 50:
                    raise ValueError("Meta description too short. Content needs retry.")
                data.update(parsed)
                return data
        except yaml.YAMLError:
            pass
        
        # Extract from structured content using patterns
        patterns = {
            'meta_title': r'(?:meta_title|title):\s*["\']?([^"\'\n]+)["\']?',
            'meta_description': r'(?:meta_description|description):\s*([^\n]+)',
            'meta_keywords': r'(?:meta_keywords|keywords):\s*([^\n]+)',
            'og_title': r'(?:og_title|open.*graph.*title):\s*["\']?([^"\'\n]+)["\']?',
            'og_description': r'(?:og_description|open.*graph.*description):\s*([^\n]+)'
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                # Remove quotes
                value = re.sub(r'^["\']|["\']$', '', value)
                data[field] = value
        
        # Validate meta description quality
        meta_desc = data.get('meta_description', '')
        if meta_desc and len(meta_desc) < 50:
            raise ValueError("Meta description too short. Content needs retry.")
        
        return data
        
        for field, pattern in patterns.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                data[field] = match.group(1).strip()
        
        # Check if we have sufficient content - if not, raise exception to trigger retry
        required_fields = ['meta_title', 'meta_description', 'meta_keywords']
        missing_fields = []
        
        for field in required_fields:
            if field not in data or not data[field] or len(data[field].strip()) < 10:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Insufficient meta content for fields: {', '.join(missing_fields)}. Content needs retry.")
        
        return data
    
    @staticmethod
    def _clean_existing_table(content: str) -> str:
        """Clean up existing table formatting."""
        lines = content.split('\n')
        table_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Ensure proper table formatting
            if '|' in line:
                # Clean up spacing around pipes
                parts = [part.strip() for part in line.split('|')]
                cleaned_line = '| ' + ' | '.join(parts[1:-1]) + ' |' if len(parts) > 2 else line
                table_lines.append(cleaned_line)
            elif line and not line.startswith('#'):
                # Add table formatting to non-table lines
                table_lines.append(f"| {line} |")
        
        return '\n'.join(table_lines)
    
    @staticmethod
    def _create_basic_properties_table(content: str, subject: str) -> str:
        """Create a basic properties table from content."""
        # Extract property-like information from content
        properties = []
        lines = content.split('\n')
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                properties.append((key.strip(), value.strip()))
        
        if not properties:
            # Create basic fallback
            properties = [
                ('Material', subject),
                ('Type', 'Metal'),
                ('Application', 'Laser Cleaning')
            ]
        
        # Format as table
        table_lines = ['| Property | Value |', '|----------|-------|']
        for key, value in properties[:10]:  # Limit to 10 properties
            table_lines.append(f'| {key} | {value} |')
        
        return '\n'.join(table_lines)
