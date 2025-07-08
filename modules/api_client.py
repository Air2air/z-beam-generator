# modules/api_client.py
"""
API Client - Handles AI API calls with provider abstraction
"""

import json
import logging
import time
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def call_ai_api(
    prompt: str,
    provider: str,
    model: str,
    api_keys: Dict[str, str],
    temperature: float,  # ✅ No default - must come from config
    max_tokens: int,     # ✅ No default - must come from config
    url_template: str,
    backoff_factor: float,  # ✅ No default - must come from config
    max_retries: int,       # ✅ No default - must come from config
    timeout: int            # ✅ No default - must come from config
) -> Optional[str]:
    """
    Make API call to specified AI provider with retry logic
    
    Args:
        prompt: The prompt to send
        provider: Provider name (DEEPSEEK, GEMINI, etc.)
        model: Model name for the provider
        api_keys: Dictionary of API keys
        temperature: Temperature for generation
        max_tokens: Maximum tokens to generate
        url_template: URL template for the provider (e.g., "https://.../{model}:generateContent")
        backoff_factor: Backoff factor for retries
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds
        
    Returns:
        Generated content or None if failed
    """
    
    logger.info(f"🌐 Making API call to {provider} with model {model}")
    
    for attempt in range(max_retries):
        try:
            if provider == "DEEPSEEK":
                return _call_deepseek_api(prompt, model, api_keys, temperature, max_tokens, url_template, timeout)
            elif provider == "GEMINI":
                # Pass the model name to _call_gemini_api for template resolution
                return _call_gemini_api(prompt, model, api_keys, temperature, max_tokens, url_template, timeout)
            elif provider == "XAI":
                return _call_xai_api(prompt, model, api_keys, temperature, max_tokens, url_template, timeout)
            elif provider == "OPENAI":
                return _call_openai_api(prompt, model, api_keys, temperature, max_tokens, url_template, timeout)
            elif provider == "CLAUDE":
                return _call_claude_api(prompt, model, api_keys, temperature, max_tokens, url_template, timeout)
            else:
                logger.error(f"❌ Unsupported provider: {provider}")
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ API call attempt {attempt + 1} failed for {provider}: {e}")
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                logger.info(f"🔄 Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"❌ All {max_retries} attempts failed for {provider}")
                return None

def _call_deepseek_api(prompt, model, api_keys, temperature, max_tokens, url_template, timeout):
    """Call DeepSeek API with enhanced error handling"""
    api_key = api_keys.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not found in api_keys")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    logger.debug(f"📡 DeepSeek API request: {url_template}")
    response = requests.post(url_template, headers=headers, json=payload, timeout=timeout)
    response.raise_for_status()
    
    data = response.json()
    
    # Enhanced error checking
    if "choices" not in data or not data["choices"]:
        raise ValueError("Invalid response structure: missing choices")
    
    content = data["choices"][0]["message"]["content"]
    if not content or not content.strip():
        raise ValueError("Empty content returned from API")
    
    logger.debug(f"✅ DeepSeek API response: {len(content)} characters")
    return content

def _call_gemini_api(prompt, model, api_keys, temperature, max_tokens, url_template, timeout):
    """Call Gemini API with enhanced error handling"""
    api_key = api_keys.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in api_keys")
    
    # MODIFIED: First, substitute the model name into the URL template
    resolved_url_base = url_template.replace("{model}", model)
    
    # MODIFIED: Then, append the API key as a query parameter to the resolved URL
    url = f"{resolved_url_base}?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens
        }
    }
    
    logger.debug(f"📡 Gemini API request: {url}")
    response = requests.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    
    data = response.json()
    
    # Enhanced error checking
    if "candidates" not in data or not data["candidates"]:
        raise ValueError("Invalid response structure: missing candidates")
    
    # MODIFIED: Safely access 'parts' using .get()
    content_parts = data["candidates"][0]["content"].get("parts")
    if not content_parts:
        raise ValueError("Invalid response structure: missing content parts in candidate")
    
    content = content_parts[0]["text"]
    if not content or not content.strip():
        raise ValueError("Empty content returned from API")
    
    logger.debug(f"✅ Gemini API response: {len(content)} characters")
    return content

def _call_xai_api(prompt, model, api_keys, temperature, max_tokens, url_template, timeout):
    """Call XAI (Grok) API with enhanced error handling"""
    api_key = api_keys.get("XAI_API_KEY")
    if not api_key:
        raise ValueError("XAI_API_KEY not found in api_keys")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    logger.debug(f"📡 XAI API request: {url_template}")
    response = requests.post(url_template, headers=headers, json=payload, timeout=timeout)
    response.raise_for_status()
    
    data = response.json()
    
    # Enhanced error checking
    if "choices" not in data or not data["choices"]:
        raise ValueError("Invalid response structure: missing choices")
    
    content = data["choices"][0]["message"]["content"]
    if not content or not content.strip():
        raise ValueError("Empty content returned from API")
    
    logger.debug(f"✅ XAI API response: {len(content)} characters")
    return content

def _call_openai_api(prompt, model, api_keys, temperature, max_tokens, url_template, timeout):
    """Call OpenAI API with enhanced error handling"""
    api_key = api_keys.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in api_keys")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    logger.debug(f"📡 OpenAI API request: {url_template}")
    response = requests.post(url_template, headers=headers, json=payload, timeout=timeout)
    response.raise_for_status()
    
    data = response.json()
    
    # Enhanced error checking
    if "choices" not in data or not data["choices"]:
        raise ValueError("Invalid response structure: missing choices")
    
    content = data["choices"][0]["message"]["content"]
    if not content or not content.strip():
        raise ValueError("Empty content returned from API")
    
    logger.debug(f"✅ OpenAI API response: {len(content)} characters")
    return content

def _call_claude_api(prompt, model, api_keys, temperature, max_tokens, url_template, timeout):
    """Call Claude API with enhanced error handling"""
    api_key = api_keys.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in api_keys")
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01" # Required for Claude API
    }
    
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    logger.debug(f"📡 Claude API request: {url_template}")
    response = requests.post(url_template, headers=headers, json=payload, timeout=timeout)
    response.raise_for_status()
    
    data = response.json()
    
    # Enhanced error checking
    if "content" not in data or not data["content"]:
        raise ValueError("Invalid response structure: missing content")
    
    content = data["content"][0]["text"]
    if not content or not content.strip():
        raise ValueError("Empty content returned from API")
    
    logger.debug(f"✅ Claude API response: {len(content)} characters")
    return content

class APIClient:
    """Wrapper class for API client functionality"""
    
    def __init__(self, config):
        self.config = config
        self.api_keys = self._get_api_keys()
        
    def _get_api_keys(self):
        """Extract API keys from environment using config mappings"""
        import os
        api_keys = {}
        
        api_key_mappings = self.config.get("api_key_mappings", {})
        for provider, env_var in api_key_mappings.items():
            api_key = os.getenv(env_var)
            if api_key:
                api_keys[f"{provider}_API_KEY"] = api_key
            else:
                logger.warning(f"⚠️ API key not found for {provider} (env: {env_var})")
        
        return api_keys
    
    def generate_content(self, prompt, provider, temperature=None, max_tokens=None):
        """Generate content using the specified provider"""
        provider_config = self.config.get("provider_models", {}).get(provider, {})
        model = provider_config.get("model", "")
        url_template = provider_config.get("url_template", "")
        
        # Always use config values - no defaults allowed
        return call_ai_api(
            prompt=prompt,
            provider=provider,
            model=model,
            api_keys=self.api_keys,
            temperature=temperature or self.config.get("generation_temperature", 0.7),
            max_tokens=max_tokens or self.config.get("max_tokens", 4000),
            url_template=url_template,
            backoff_factor=self.config.get("backoff_factor", 2.0),
            max_retries=self.config.get("max_retries", 3),
            timeout=self.config.get("timeout", 60)
        )