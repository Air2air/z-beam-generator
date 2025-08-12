"""
Unified Document Generator - Minimal Implementation

Single API call generates complete material documentation.
Eliminates fragmented generation and retry complexity.
Uses BATCH_CONFIG for consistency with main system.
"""

import logging
import json
import os
import sys
from typing import Dict, Any

# Add project root to path to import BATCH_CONFIG
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

logger = logging.getLogger(__name__)

class UnifiedDocumentGenerator:
    """Single API call generates complete material document using BATCH_CONFIG."""
    
    def __init__(self, ai_provider: str = "deepseek", options: Dict[str, Any] = None):
        self.ai_provider = ai_provider
        self.options = options or {"model": "deepseek-chat", "max_tokens": 8000}
        
        # Import BATCH_CONFIG for component settings
        from run import BATCH_CONFIG
        self.config = BATCH_CONFIG
    
    def generate_complete_document(self, subject: str, article_type: str, 
                                 category: str, author_data: Dict[str, Any],
                                 schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete document with single API call using schema."""
        
        try:
            # Build context with schema
            context = {
                "subject": subject,
                "article_type": article_type,
                "category": category,
                "author_context": author_data.get("author_name", "Expert") + " from " + author_data.get("author_country", "International"),
                "schema": schema
            }
            
            # Create unified prompt with schema structure
            prompt = self._build_unified_prompt(context)
            
            # Single API call
            response = self._call_api(prompt)
            
            # Parse JSON response
            document = self._parse_response(response, subject, schema)
            
            return document
            
        except Exception as e:
            logger.error(f"Unified generation failed for {subject}: {e}")
            return None
    
    def _build_unified_prompt(self, context: Dict[str, Any]) -> str:
        """Build single comprehensive prompt using schema structure and BATCH_CONFIG."""
        
        subject = context["subject"]
        category = context["category"]
        article_type = context["article_type"]
        schema = context.get("schema", {})
        author_context = context["author_context"]
        
        # Get enabled components from BATCH_CONFIG
        enabled_components = []
        component_configs = {}
        for name, config in self.config["components"].items():
            if config.get("enabled", False):
                enabled_components.append(name)
                component_configs[name] = config
        
        # Extract schema structure for frontmatter
        frontmatter_schema = self._extract_frontmatter_schema(schema)
        table_schema = self._extract_table_schema(schema)
        
        # Build component requirements based on BATCH_CONFIG
        component_requirements = self._build_component_requirements(enabled_components, component_configs)
        
        system_prompt = f"""Generate complete technical {article_type} documentation for {subject} as JSON.

CRITICAL: You MUST follow the EXACT legacy component prompt requirements with 100% accuracy.
These are the PROVEN specifications from the working legacy system that must be retained exactly.

CRITICAL: Frontmatter MUST include ALL required schema fields:
{self._format_schema_requirements(frontmatter_schema, table_schema)}

ENABLED COMPONENTS (from BATCH_CONFIG): {', '.join(enabled_components)}

LEGACY COMPONENT SPECIFICATIONS (MUST BE FOLLOWED EXACTLY):
{component_requirements}

ARTICLE TYPE: {article_type}
CATEGORY: {category}
AUTHOR PERSPECTIVE: {author_context}

CRITICAL FORMATTING REQUIREMENTS:
- Caption: EXACTLY 2 lines, no more, no less
- JSON-LD: YAML format only, never JSON syntax
- Metatags: Exact character limits (50-60 title, 150-160 description)  
- Frontmatter: Raw factual content only, no formatting
- Content: Technical but accessible, specific word counts
- Bullets: Technical content only, formatting handled by Python
- Table: Data content only, Python handles structure
- Tags: Comma-separated list only, no formatting
- Properties Table: Markdown table format with exact technical values

Return ONLY this JSON structure with ALL REQUIRED FIELDS populated following legacy specs:
{{
  {self._build_json_structure(enabled_components, frontmatter_schema, table_schema, subject, category)}
}}

CRITICAL REQUIREMENTS: 
- Follow EVERY legacy prompt requirement exactly - no deviations
- Include EVERY required field from schema: name, description, author, keywords, category, chemicalProperties, properties, composition, compatibility, regulatoryStandards, images
- Real technical data, no placeholders or "TBD" values
- Follow exact schema structure and data types
- Author field must be populated from provided author context
- Technical accuracy for {category} materials
- Respect all legacy formatting and content rules"""
        
        user_prompt = f"""Generate complete documentation for {subject} ({category} {article_type}).

RETURN ONLY JSON - NO OTHER TEXT OR EXPLANATIONS."""
        
        return f"{system_prompt}\n\nHuman: {user_prompt}\n\nAssistant:"
    
    def _call_api(self, prompt: str) -> str:
        """Make API call."""
        from api.client import ApiClient
        
        # Create minimal article context for API client
        article_context = {
            "subject": "Unified Generation",
            "article_type": "material",
            "ai_provider": self.ai_provider,
            "options": self.options
        }
        
        client = ApiClient(provider=self.ai_provider, options=self.options, article_context=article_context)
        return client.complete(prompt)
    
    def _parse_response(self, response: str, subject: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JSON response with schema validation."""
        from components.base.utils.content_formatter import ContentFormatter
        
        cleaned = ContentFormatter.extract_json_content(response)
        document = json.loads(cleaned)
        
        # Get enabled components from BATCH_CONFIG
        enabled_components = []
        if hasattr(self, 'config'):
            for name, config in self.config["components"].items():
                if config.get("enabled", False):
                    enabled_components.append(name)
        else:
            enabled_components = ["frontmatter", "content", "table", "bullets", "tags", "metatags", "jsonld"]
        
        # Validate against schema requirements
        missing = [comp for comp in enabled_components if not document.get(comp)]
        if missing:
            raise ValueError(f"Missing components: {missing}")
        
        # Validate frontmatter against schema
        if schema:
            self._validate_frontmatter_schema(document.get("frontmatter", {}), schema)
        
        return document
    
    def _build_component_requirements(self, enabled_components: list, component_configs: Dict[str, Any]) -> str:
        """Build component requirements based on legacy prompt specifications with 100% accuracy."""
        requirements = []
        
        for component in enabled_components:
            if component == "frontmatter":
                requirements.append("""- frontmatter:
    CRITICAL REQUIREMENTS FROM LEGACY PROMPT (v4.0.0):
    - Output ONLY raw factual content. NO formatting, NO structure, NO YAML, NO JSON, NO markdown formatting
    - Python utilities will handle ALL formatting, structuring, and organization
    - Include EXACT technical facts:
      * Physical properties: density, melting point, thermal conductivity, electrical properties with exact values and units
      * Chemical properties: composition percentages, chemical formulas, molecular structure, purity levels  
      * Laser parameters: optimal wavelengths in nanometers, power ranges in watts, pulse durations in nanoseconds, fluence values in J/cm²
      * Processing data: cleaning rates, temperature ranges, optimal settings, measured outcomes
      * Applications: specific industrial uses, equipment types, processing conditions, success metrics
      * Compatibility: substrate materials, coating types, environmental conditions
      * Safety data: emission levels, ventilation requirements, protective equipment specifications
      * Standards: relevant industry standards, regulatory requirements, certification details
    - Provide only factual technical information with specific numerical data
    - No formatting whatsoever - Python will structure everything""")
            
            elif component == "caption":
                requirements.append("""- caption:
    EXACT REQUIREMENTS FROM LEGACY PROMPT (v5.0.0):
    - Generate EXACTLY ONE clean, professional image caption
    - CONTENT REQUIREMENTS:
      * Line 1: Material description with contamination/surface analysis details
      * Line 2: Laser cleaning process parameters and results
      * Include technical specifications: power, wavelength, pulse duration, spot size
      * Use scientific terminology appropriate for technical documentation
    - EXAMPLE STRUCTURE:
      [Material name with formula] microscopic surface analysis showing contaminants.
      After laser cleaning at [wavelength], [power], [pulse duration] and [spot size].
    - STRICT RULES:
      * Provide ONLY the two-line caption content
      * No introductory text, no multiple variations, no explanations
      * Focus on technical accuracy and scientific precision
      * Material formatting will be handled automatically""")
            
            elif component == "jsonld":
                requirements.append("""- jsonld:
    MANDATORY FORMAT FROM LEGACY PROMPT (v3.0.5):
    - OUTPUT ONLY YAML - NEVER JSON
    - Example required format:
      headline: Your headline here
      description: Your description here
      keywords:
      - keyword1
      - keyword2
      articleBody: Your article body content here
    - FORBIDDEN FORMATS:
      * Do NOT use JSON: {"key": "value"}
      * Do NOT use code blocks: ```
      * Do NOT use quotes around keys: "headline"
    - Create rich, descriptive content for structured data using YAML format""")
            
            elif component == "metatags":
                requirements.append("""- metatags:
    CONTENT-ONLY FOCUS FROM LEGACY PROMPT (v4.0.0):
    - You provide ONLY the meta content values. All YAML structure and formatting will be handled by Python
    - CONTENT AREAS TO PROVIDE:
      * meta_title: SEO-optimized page title (50-60 characters)
      * meta_description: Compelling description with technical details (150-160 characters)  
      * meta_keywords: Comma-separated keyword list (10-15 relevant terms)
    - TECHNICAL FOCUS AREAS:
      * Laser parameters and wavelengths
      * Material properties and composition
      * Industrial applications and benefits
      * Safety and precision aspects
      * Industry-specific terminology
    - OUTPUT FORMAT:
      meta_title: Your optimized title here
      meta_description: Your compelling description here
      meta_keywords: keyword1, keyword2, keyword3, etc.""")
            
            elif component == "bullets":
                count = component_configs.get(component, {}).get("count", 6)
                requirements.append(f"""- bullets:
    CONTENT-ONLY FOCUS FROM LEGACY PROMPT (v4.0.0):
    - You provide ONLY the technical content. All bullet formatting and structure will be handled by Python
    - CONTENT GUIDANCE:
      * Focus on the most important technical information
      * Include specific measurements and values when possible
      * Emphasize practical applications and benefits
      * Highlight unique properties of subject
      * Include environmental and efficiency advantages
      * Provide content for exactly {count} comprehensive points
    - CONTENT AREAS TO COVER:
      * Technical specifications (power, wavelength, spot size)
      * Key applications and use cases
      * Environmental benefits and advantages
      * Manufacturing advantages and efficiency
      * Performance metrics and measurable outcomes
      * Material properties and characteristics
    - Focus on providing rich technical content that can be organized into bullet points""")
            
            elif component == "content":
                min_words = component_configs.get(component, {}).get("min_words", 800)
                max_words = component_configs.get(component, {}).get("max_words", 1200)
                requirements.append(f"""- content:
    CONTENT-ONLY FOCUS FROM LEGACY PROMPT (v4.0.0):
    - You provide ONLY the article content. All formatting and structure will be handled by Python
    - CONTENT GUIDANCE:
      * Focus on technical accuracy and completeness
      * Provide substantial detail about subject
      * Include real-world examples and applications
      * Explain technical concepts clearly and authoritatively
      * Maintain a technical but accessible writing style
      * Write between {min_words} and {max_words} words
    - CONTENT AREAS TO COVER:
      * Introduction and overview of subject
      * Technical specifications and capabilities
      * Applications and use cases with specific examples
      * Manufacturing and processing context
      * Environmental benefits and considerations
      * Industry standards and regulatory aspects
      * Future outlook and developments
    - Focus on providing rich, detailed content that leverages technical information""")
            
            elif component == "table":
                requirements.append("""- table:
    CONTENT-ONLY FOCUS FROM LEGACY PROMPT (v4.1.0):
    - You provide ONLY the data content. All table formatting and structure will be handled by Python
    - CONTENT GUIDANCE:
      * Focus on providing accurate technical data for tabular presentation
      * Include specifications, properties, applications, or measurements
      * Use proper technical terminology relevant to subject
      * Provide content that would work well in different table types
    - CONTENT AREAS TO PROVIDE:
      * Technical specifications and parameters with values
      * Material properties or composition details with measurements
      * Performance metrics or test results with units
      * Compatibility information with specific details
      * Application data with quantifiable benefits
      * Regulatory or standards information
    - Focus on providing rich, structured data content for tables""")
            
            elif component == "tags":
                min_tags = component_configs.get(component, {}).get("min_tags", 8)
                max_tags = component_configs.get(component, {}).get("max_tags", 12)
                requirements.append(f"""- tags:
    CONTENT-ONLY FOCUS FROM LEGACY PROMPT (v4.0.0):
    - Generate navigation-focused content for tags
    - TAG CATEGORIES TO INCLUDE:
      * Material type (e.g., ceramic, metal)
      * Application domain (e.g., semiconductor, aerospace)
      * Technology (e.g., laser-ablation, nd-yag)
      * Benefits (e.g., precision-cleaning, chemical-free)
    - OUTPUT INSTRUCTIONS:
      * Generate between {min_tags} and {max_tags} tags
      * Output ONLY a comma-separated list of tags (e.g., "tag1, tag2, tag3")
      * No numbering, no asterisks, no formatting, no explanations
      * Be concise and focused on laser cleaning applications
      * PREFER SINGLE WORDS when possible (e.g., "laser" instead of "laser-cleaning")
      * Use hyphens ONLY for essential compound concepts (e.g., "nd-yag", "co2-laser")
      * Maximum 2 words per tag - avoid long descriptive phrases
      * Focus on core concepts: materials, processes, applications, technologies""")
            
            elif component == "propertiestable":
                requirements.append("""- propertiestable:
    PROPERTIES TABLE REQUIREMENTS (Direct generation from base component data):
    - Generate single unified markdown table with 4 most interesting properties
    - Format: | Property | Value |
    - Include chemical formula, material symbol, category, material type when available
    - Add category-specific properties based on material type
    - Provide exact technical values with proper units
    - No TBD or placeholder values allowed""")
        
        return "\n".join(requirements)
    
    def _build_json_structure(self, enabled_components: list, frontmatter_schema: str, 
                             table_schema: Dict[str, Any], subject: str, category: str) -> str:
        """Build JSON structure string for enabled components following legacy specifications."""
        components = []
        
        for component in enabled_components:
            if component == "frontmatter":
                components.append(f'"frontmatter": {frontmatter_schema}')
            elif component == "content":
                components.append('"content": "Comprehensive technical overview (800-1200 words following legacy content prompt v4.0.0)"')
            elif component == "table":
                headers = table_schema.get("headers", ["Property", "Value", "Unit"])
                components.append(f'"table": {{"headers": {headers}, "rows": ["Technical data following legacy table prompt v4.1.0"]}}')
            elif component == "bullets":
                components.append('"bullets": ["Technical content point 1", "Technical content point 2", "Technical content point 3", "Technical content point 4", "Technical content point 5", "Technical content point 6"]')
            elif component == "tags":
                components.append('"tags": "comma-separated, list, of, navigation, tags, following, legacy, prompt, v4.0.0"')
            elif component == "metatags":
                components.append('"metatags": {"meta_title": "50-60 char SEO title", "meta_description": "150-160 char compelling description with technical details", "meta_keywords": "10-15 relevant terms, comma-separated"}')
            elif component == "jsonld":
                components.append('"jsonld": "headline: YAML format headline\\ndescription: YAML format description\\nkeywords:\\n- keyword1\\n- keyword2\\narticleBody: YAML format article body"')
            elif component == "caption":
                components.append(f'"caption": "Line 1: {subject} microscopic surface analysis showing contaminants.\\nLine 2: After laser cleaning at wavelength, power, pulse duration and spot size."')
            elif component == "propertiestable":
                components.append('"propertiestable": "| Property | Value |\\n|----------|-------|\\n| Chemical Formula | ... |\\n| Material Symbol | ... |\\n| Category | ... |\\n| Material Type | ... |"')
        
        return ",\n  ".join(components)
    
    def _extract_frontmatter_schema(self, schema: Dict[str, Any]) -> str:
        """Extract frontmatter schema structure as string with all required fields."""
        if not schema:
            return '{"title": "...", "description": "...", "category": "..."}'
        
        # Get the main profile structure and validation requirements
        profile = schema.get("materialProfile", {}).get("profile", {})
        validation = schema.get("materialProfile", {}).get("validation", {}).get("frontmatter", {})
        required_fields = validation.get("requiredFields", [])
        
        if not profile:
            return '{"title": "...", "description": "...", "category": "..."}'
        
        # Build complete schema structure with all required fields
        schema_structure = {}
        
        for field_name in required_fields:
            if field_name in profile:
                field_config = profile[field_name]
                field_type = field_config.get("type", "string")
                
                if field_type == "array":
                    schema_structure[field_name] = "[...]"
                elif field_type == "object":
                    # Get object properties if available
                    properties = field_config.get("properties", {})
                    if properties:
                        obj_structure = {}
                        for prop_name, prop_config in properties.items():
                            prop_type = prop_config.get("type", "string")
                            if prop_type == "array":
                                obj_structure[prop_name] = "[...]"
                            elif prop_type == "object":
                                obj_structure[prop_name] = "{...}"
                            else:
                                obj_structure[prop_name] = f'"{prop_config.get("example", "...")}"'
                        schema_structure[field_name] = obj_structure
                    else:
                        schema_structure[field_name] = "{...}"
                else:
                    example = field_config.get("example", "...")
                    schema_structure[field_name] = f'"{example}"'
            else:
                # Handle special required fields not in profile
                if field_name == "name":
                    schema_structure[field_name] = '"Material Name"'
                elif field_name == "description":
                    schema_structure[field_name] = '"Technical description"'
                elif field_name == "author":
                    schema_structure[field_name] = '"Author Name"'
                elif field_name == "keywords":
                    schema_structure[field_name] = '["keyword1", "keyword2"]'
                else:
                    schema_structure[field_name] = '"..."'
        
        import json
        return json.dumps(schema_structure, indent=2)
    
    def _extract_table_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract table schema requirements."""
        if not schema:
            return {"headers": ["Property", "Value", "Unit"]}
        
        # Look for properties structure in schema
        profile = schema.get("materialProfile", {}).get("profile", {})
        properties = profile.get("properties", {})
        
        if properties and isinstance(properties, dict):
            # Extract property names as potential table headers
            prop_names = list(properties.get("properties", {}).keys())
            if prop_names:
                return {"headers": ["Property", "Value", "Unit"], "suggested_properties": prop_names}
        
        return {"headers": ["Property", "Value", "Unit"]}
    
    def _format_schema_requirements(self, frontmatter_schema: str, table_schema: Dict[str, Any]) -> str:
        """Format schema requirements for prompt."""
        requirements = [
            f"Frontmatter must include: {frontmatter_schema}",
            f"Table headers: {table_schema.get('headers', ['Property', 'Value', 'Unit'])}"
        ]
        
        if "suggested_properties" in table_schema:
            requirements.append(f"Include these properties in table: {', '.join(table_schema['suggested_properties'])}")
        
        return "\n".join(requirements)
    
    def _validate_frontmatter_schema(self, frontmatter: Dict[str, Any], schema: Dict[str, Any]) -> None:
        """Validate frontmatter against schema requirements."""
        if not schema:
            return
        
        validation = schema.get("materialProfile", {}).get("validation", {}).get("frontmatter", {})
        
        # Check required fields
        required_fields = validation.get("requiredFields", [])
        missing_fields = [field for field in required_fields if field not in frontmatter]
        
        if missing_fields:
            logger.warning(f"Frontmatter missing required fields: {missing_fields}")
        
        # Additional validation could be added here
        return
