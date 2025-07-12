"""JSON-LD prompt builder for schema-driven generation."""

import json
from typing import Dict, Any

def build_jsonld_prompt(context: Dict[str, Any], schema: Dict[str, Any]) -> str:
    """Build JSON-LD generation prompt using schema structure."""
    article_type = context.get("article_type")
    subject = context.get("subject")
    
    # Map context subject to schema placeholder
    placeholder_map = {
        "material": "materialName",
        "application": "applicationName", 
        "region": "regionName",
        "thesaurus": "term"
    }
    
    placeholder = placeholder_map.get(article_type, "subject")
    
    # Find JSON-LD section in schema (flexible naming)
    jsonld_section = None
    for key, value in schema.items():
        if "jsonld" in key.lower() or "structured" in key.lower():
            jsonld_section = value
            break
    
    if not jsonld_section:
        raise ValueError(f"No JSON-LD section found in schema for {article_type}")
    
    # Replace system placeholders in schema
    schema_with_system = json.dumps(jsonld_section, indent=2)
    for sys_key, sys_value in context.items():
        if sys_key in ["generation_timestamp", "model_used", "lastUpdated", "publishedAt"]:
            schema_with_system = schema_with_system.replace(f"{{{{{sys_key}}}}}", str(sys_value))
    
    prompt = f"""You are an expert technical writer creating JSON-LD structured data for a laser cleaning article.

Subject: {subject}
Article Type: {article_type}

Generate JSON-LD following this exact schema structure:
{schema_with_system}

CRITICAL REQUIREMENTS:
- Replace ALL instances of {{{{{placeholder}}}}} with "{subject}"
- Use the subject "{subject}" appropriately in all JSON-LD fields
- Include ALL fields from the schema - no omissions
- Follow the schema data types and formats exactly
- Return ONLY valid JSON format
- Do NOT include any explanatory text or markdown formatting
- Ensure every field has meaningful content (no empty strings)
- Follow Schema.org standards for structured data

Generate the JSON-LD now:"""
    
    return prompt