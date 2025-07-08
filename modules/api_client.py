#!/usr/bin/env python3
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
    temperature: float = 0.7,
    max_tokens: int = 4096,
    url_template: str = "",
    backoff_factor: float = 2.0,
    max_retries: int = 3,
    timeout: int = 60
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
        url_template: URL template for the provider
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
    
    url = f"{url_template}?key={api_key}"
    
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
    
    content = data["candidates"][0]["content"]["parts"][0]["text"]
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
        "anthropic-version": "2023-06-01"
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
