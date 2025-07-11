#!/usr/bin/env python3
"""
Metadata Generator - No fallbacks, 100% schema-driven
"""
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_metadata(subject: str, author_id: int, config: Dict[str, Any], api_client, schema_fields: Dict[str, Any]) -> Dict[str, Any]:
    """Generate metadata - 100% schema-driven, no defaults"""
    logger.info(f"📊 Generating metadata for {subject} by author ID {author_id}")
    
    # Start with schema fields only
    metadata = schema_fields.copy()
    
    # Add only essential fields
    metadata["subject"] = subject
    metadata["generation_timestamp"] = datetime.now().isoformat()
    
    # Get author info from config
    author_info = _get_author_info(author_id, config)
    metadata.update(author_info)
    
    # Generate content via API
    content = _generate_content(subject, api_client, config, metadata)
    metadata.update(content)
    
    # Add model info
    metadata["model_used"] = _get_model_info(config)
    
    # Add timestamps
    current_date = datetime.now().strftime("%Y-%m-%d")
    metadata["lastUpdated"] = current_date
    metadata["publishedAt"] = current_date
    
    return metadata

def _get_model_info(config: Dict[str, Any]) -> str:
    """Get model information from config - no fallbacks"""
    if "model_name" in config:
        return config["model_name"]
    
    if "api" in config and isinstance(config["api"], dict):
        api_config = config["api"]
        if "provider" in api_config and "model" in api_config:
            return f"{api_config['provider'].upper()}/{api_config['model']}"
    
    if "providers" in config and isinstance(config["providers"], dict):
        providers = config["providers"]
        for provider_name, provider_config in providers.items():
            if provider_config.get("active", False):
                model = provider_config.get("model")
                if model:
                    return f"{provider_name.upper()}/{model}"
    
    raise ValueError("No model configuration found in config")

def _get_author_info(author_id: int, config: Dict[str, Any]) -> Dict[str, Any]:
    """Get author information - no defaults"""
    if "authors" not in config:
        raise ValueError("No authors configuration found in config")
    
    if not isinstance(config["authors"], dict):
        raise ValueError("Invalid authors configuration in config")
    
    author_info = config["authors"].get(str(author_id))
    if not author_info:
        raise ValueError(f"Author ID {author_id} not found in config")
    
    # Map author fields to metadata fields
    required_fields = ["name", "country", "title", "image", "slug"]
    for field in required_fields:
        if field not in author_info:
            raise ValueError(f"Author {author_id} missing required field: {field}")
    
    return {
        "authorName": author_info["name"],
        "authorCountry": author_info["country"],
        "authorTitle": author_info["title"],
        "authorImage": author_info["image"],
        "authorSlug": author_info["slug"]
    }

def _generate_content(subject: str, api_client, config: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Generate content using API - no fallbacks"""
    logger.info(f"🔬 Generating content for {subject}")
    
    article_type = metadata.get("articleType", "article")
    
    prompt = f"""Generate metadata for laser cleaning {article_type}: {subject}

Context:
- Article type: {article_type}
- Subject: {subject}

Return JSON with:
- title: Article title
- description: Brief description (1-2 sentences)
- nameShort: Short name for the topic
- image: Image URL for the topic

Format as valid JSON only."""
    
    # Use the correct method name - it's 'call'
    try:
        response = api_client.call(prompt)
    except Exception as e:
        raise ValueError(f"API call failed: {e}")
    
    # Debug logging removed - clean response parsing
    response = response.strip()
    if response.startswith('```json'):
        response = response.replace('```json', '').replace('```', '').strip()
    elif response.startswith('```'):
        response = response.replace('```', '').strip()
    
    # Parse JSON response
    import json
    try:
        content = json.loads(response)
        if not isinstance(content, dict):
            raise ValueError("API response is not a JSON object")
        
        # Validate required fields (including title)
        required_fields = ["title", "description", "nameShort"]
        for field in required_fields:
            if field not in content:
                raise ValueError(f"API response missing required field: {field}")
        
        # Add default image if not provided by API
        if "image" not in content:
            if "default_image_url" in config:
                content["image"] = config["default_image_url"]
            else:
                content["image"] = "https://example.com/default-image.jpg"
        
        return content
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response from API: {e}")
    except Exception as e:
        raise ValueError(f"Content generation failed: {e}")