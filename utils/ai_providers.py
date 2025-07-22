"""AI Provider implementations for various LLM APIs."""

import os
import json
import logging
import re
import requests
import time
from typing import Dict, Any, Optional, Union

# Set up logging
logger = logging.getLogger(__name__)

class BaseAIClient:
    """Base class for all AI clients."""
    
    def generate_content(self, prompt: str) -> str:
        """Generate content from prompt."""
        raise NotImplementedError("Subclasses must implement generate_content")
        
    def generate_structured_data(self, prompt: str, output_format: str = "json", schema: Optional[Dict] = None) -> Union[Dict, str]:
        """Generate structured data from prompt with schema guidance."""
        # Add format instructions
        format_instructions = f"Return your response in {output_format} format."
        if schema:
            format_instructions += " Follow this schema structure exactly:"
            schema_str = json.dumps(schema, indent=2)
            format_instructions += f"\n\n```json\n{schema_str}\n```"
            
        full_prompt = f"{prompt}\n\n{format_instructions}"
        
        # Call the model with structured data prompt
        response = self.generate_content(full_prompt)
        
        # Extract structured data from response
        if output_format == "json":
            # Try to extract JSON from the response
            return self._extract_json(response)
        
        return response
    
    def _extract_json(self, text: str) -> Union[Dict, str]:
        """Extract JSON from text response."""
        # Try to find JSON block in markdown
        json_match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
                
        # Try to find JSON block without language specifier
        json_match = re.search(r'```\n(.*?)\n```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
                
        # Try to parse the entire text as JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
            
        # Return original text if parsing fails
        return text


class DeepseekClient(BaseAIClient):
    """Client for Deepseek API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_base = "https://api.deepseek.com/v1"
        
    def generate_content(self, prompt: str) -> str:
        """Generate content from prompt using Deepseek API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-coder",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 4000
            }
            
            response = requests.post(
                f"{self.api_base}/chat/completions", 
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"Deepseek API error: {response.status_code} - {response.text}")
                return f"Error: API returned status code {response.status_code}"
                
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.exception(f"Error calling Deepseek API: {str(e)}")
            return f"Error: {str(e)}"


class OpenAIClient(BaseAIClient):
    """Client for OpenAI API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_base = "https://api.openai.com/v1"
        
    def generate_content(self, prompt: str) -> str:
        """Generate content from prompt using OpenAI API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o",  # Using GPT-4o as default model
                "messages": [
                    {"role": "system", "content": "You are a materials science expert specializing in laser cleaning technologies."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,  # Lower temperature for more factual responses
                "max_tokens": 4000
            }
            
            response = requests.post(
                f"{self.api_base}/chat/completions", 
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return f"Error: API returned status code {response.status_code}"
                
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.exception(f"Error calling OpenAI API: {str(e)}")
            return f"Error: {str(e)}"


class GeminiClient(BaseAIClient):
    """Client for Google Gemini API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_base = "https://generativelanguage.googleapis.com/v1"
        
    def generate_content(self, prompt: str) -> str:
        """Generate content from prompt using Gemini API."""
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": prompt}]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.4,
                    "topP": 0.95,
                    "topK": 40,
                    "maxOutputTokens": 4096
                }
            }
            
            # API key is passed as a query parameter
            url = f"{self.api_base}/models/gemini-1.5-pro:generateContent?key={self.api_key}"
            
            response = requests.post(
                url,
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                return f"Error: API returned status code {response.status_code}"
                
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
            
        except Exception as e:
            logger.exception(f"Error calling Gemini API: {str(e)}")
            return f"Error: {str(e)}"


class GrokClient(BaseAIClient):
    """Client for Grok AI API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_base = "https://api.grok.x/v1"  # Update this when official API is available
        
    def generate_content(self, prompt: str) -> str:
        """Generate content from prompt using Grok API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5,
                "max_tokens": 4000
            }
            
            response = requests.post(
                f"{self.api_base}/chat/completions", 
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"Grok API error: {response.status_code} - {response.text}")
                return f"Error: API returned status code {response.status_code}"
                
            result = response.json()
            
            # Assuming Grok follows OpenAI-like response format
            # Update this when official API is available
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.exception(f"Error calling Grok API: {str(e)}")
            return f"Error: {str(e)}"


def get_ai_client(provider_name: str) -> BaseAIClient:
    """Get AI client for specified provider.
    
    Args:
        provider_name: Name of the AI provider (deepseek, openai, gemini, grok)
        
    Returns:
        Instance of appropriate AI client
    """
    provider_name = provider_name.lower()
    
    if provider_name == "deepseek":
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            logger.error("DEEPSEEK_API_KEY environment variable not set")
            raise ValueError("DEEPSEEK_API_KEY environment variable not set")
        return DeepseekClient(api_key)
        
    elif provider_name == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set")
            raise ValueError("OPENAI_API_KEY environment variable not set")
        return OpenAIClient(api_key)
        
    elif provider_name == "gemini":
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY environment variable not set")
            raise ValueError("GEMINI_API_KEY environment variable not set")
        return GeminiClient(api_key)
        
    elif provider_name == "grok":
        api_key = os.environ.get("XAI_API_KEY")
        if not api_key:
            logger.error("XAI_API_KEY environment variable not set")
            raise ValueError("XAI_API_KEY environment variable not set")
        return GrokClient(api_key)
        
    elif provider_name == "auto":
        # Default to OpenAI if auto is specified (you can modify this logic)
        logger.info("'auto' provider specified, using OpenAI as default")
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not found, falling back to Deepseek")
            return get_ai_client("deepseek")
        return OpenAIClient(api_key)
        
    else:
        logger.error(f"Unknown AI provider: {provider_name}")
        raise ValueError(f"Unknown AI provider: {provider_name}. Supported providers: deepseek, openai, gemini, grok, auto")


def test_provider_connection(provider_name: str) -> Dict[str, Any]:
    """Test connection to AI provider.
    
    Args:
        provider_name: Name of the AI provider to test
        
    Returns:
        Dict with test results
    """
    start_time = time.time()
    results = {
        "provider": provider_name,
        "success": False,
        "latency_ms": 0,
        "error": None
    }
    
    try:
        # Get client for provider
        client = get_ai_client(provider_name)
        
        # Simple test prompt
        test_response = client.generate_content("Respond with 'Connection successful' if you can read this message.")
        
        # Calculate latency
        latency = time.time() - start_time
        results["latency_ms"] = round(latency * 1000)
        
        # Check response
        if "Connection successful" in test_response or "connection successful" in test_response.lower():
            results["success"] = True
        else:
            results["error"] = f"Unexpected response: {test_response[:100]}..."
            
    except Exception as e:
        results["error"] = str(e)
        
    return results