#!/usr/bin/env python3
"""
Standardized API Client for Z-Beam Generator

Provides a robust, standardized interface for content generation using the DeepSeek API.
Features comprehensive error handling, retry logic, and configuration management.
"""

import os
import json
import requests
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

@dataclass
class APIResponse:
    """Standardized API response with comprehensive metadata"""
    success: bool
    content: str
    error: Optional[str] = None
    response_time: Optional[float] = None
    token_count: Optional[int] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    model_used: Optional[str] = None
    request_id: Optional[str] = None
    retry_count: int = 0

@dataclass 
class GenerationRequest:
    """Structured request for content generation"""
    prompt: str
    system_prompt: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

class APIError(Exception):
    """Custom exception for API-related errors"""
    pass

class APIClient:
    """Standardized API client with comprehensive features"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, 
                 model: Optional[str] = None, config: Optional[Dict] = None):
        """Initialize the API client with configuration"""
        
        # Store parameters as instance attributes for test compatibility
        self.base_url = base_url
        self.model = model
        
        # Load configuration
        if config:
            self.config = config
        else:
            try:
                from .config import get_default_config
                self.config = get_default_config()
            except ImportError:
                # Fallback configuration
                self.config = self._get_fallback_config(api_key, base_url)
        
        # Override config with provided parameters
        if api_key:
            if hasattr(self.config, 'api_key'):
                self.config.api_key = api_key
            else:
                self.config['api_key'] = api_key
        if base_url:
            if hasattr(self.config, 'base_url'):
                self.config.base_url = base_url
            else:
                self.config['base_url'] = base_url
        if model:
            if hasattr(self.config, 'model'):
                self.config.model = model
            else:
                self.config['model'] = model
        
        # Update instance attributes from config
        self.base_url = getattr(self.config, 'base_url', None) or (self.config.get('base_url') if hasattr(self.config, 'get') else base_url)
        self.model = getattr(self.config, 'model', None) or (self.config.get('model') if hasattr(self.config, 'get') else model or 'deepseek-chat')
        
        # Set timeout values with defaults
        self.timeout_connect = getattr(self.config, 'timeout_connect', None) or (self.config.get('timeout_connect') if hasattr(self.config, 'get') else 30)
        self.timeout_read = getattr(self.config, 'timeout_read', None) or (self.config.get('timeout_read') if hasattr(self.config, 'get') else 120)
        
        # Initialize session
        self.session = requests.Session()
        self._setup_session()
        
        # Statistics tracking
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_tokens': 0,
            'total_response_time': 0.0
        }
    
    def _get_fallback_config(self, api_key: Optional[str] = None, 
                            base_url: Optional[str] = None):
        """Get fallback configuration when config module is not available"""
        from dataclasses import dataclass
        
        @dataclass
        class FallbackConfig:
            api_key: str
            base_url: str
            model: str
            max_tokens: int = 4000
            temperature: float = 0.7
            timeout_connect: int = 10
            timeout_read: int = 120
            max_retries: int = 3
            retry_delay: float = 1.0
        
        # Use provided API key or raise error
        if not api_key:
            raise ValueError("API key must be provided to APIClient")
        
        return FallbackConfig(
            api_key=api_key,
            base_url=base_url or "https://api.deepseek.com",
            model=self.model or "deepseek-chat"
        )
    
    def _setup_session(self):
        """Setup the requests session with headers and configuration"""
        
        self.session.headers.update({
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Z-Beam-Generator/1.0'
        })
        
        # Configure session timeouts and retries
        adapter = requests.adapters.HTTPAdapter(
            max_retries=self.config.max_retries,
            pool_connections=10,
            pool_maxsize=10
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
    
    def test_connection(self) -> bool:
        """Test API connection with a minimal request"""
        
        logger.info("Testing API connection...")
        
        try:
            test_request = GenerationRequest(
                prompt="Test connection",
                max_tokens=10
            )
            response = self.generate(test_request)
            
            if response.success:
                logger.info("✅ API connection test successful")
                return True
            else:
                logger.error(f"❌ API connection test failed: {response.error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ API connection test failed with exception: {e}")
            return False
    
    def generate(self, request: GenerationRequest) -> APIResponse:
        """Generate content using the DeepSeek API with retry logic"""
        
        self.stats['total_requests'] += 1
        start_time = time.time()
        
        # Log API request details
        logger.info(f"🚀 API Request #{self.stats['total_requests']}: {self.model}")
        logger.debug(f"   📝 Prompt length: {len(request.prompt)} chars")
        logger.debug(f"   🎛️  Parameters: temp={request.temperature}, max_tokens={request.max_tokens}")
        if request.system_prompt:
            logger.debug(f"   💬 System prompt: {len(request.system_prompt)} chars")
        
        for attempt in range(self.config.max_retries + 1):
            try:
                if attempt > 0:
                    logger.warning(f"   🔄 Retry attempt {attempt}/{self.config.max_retries}")
                
                response = self._make_request(request)
                response.retry_count = attempt
                
                # Log API response details
                if response.success:
                    logger.info(f"   ✅ Success in {response.response_time:.2f}s")
                    logger.info(f"   📊 Tokens: {response.token_count} total ({response.prompt_tokens}+{response.completion_tokens})")
                    logger.info(f"   📝 Content: {len(response.content)} chars generated")
                    if response.retry_count > 0:
                        logger.info(f"   🔄 Required {response.retry_count} retries")
                else:
                    logger.error(f"   ❌ Failed: {response.error}")
                
                # Update statistics
                if response.success:
                    self.stats['successful_requests'] += 1
                    if response.token_count:
                        self.stats['total_tokens'] += response.token_count
                else:
                    self.stats['failed_requests'] += 1
                
                self.stats['total_response_time'] += response.response_time or 0
                return response
                
            except requests.exceptions.Timeout as e:
                if attempt == self.config.max_retries:
                    return APIResponse(
                        success=False,
                        content="",
                        error=f"Request timeout after {self.config.max_retries + 1} attempts",
                        response_time=time.time() - start_time,
                        retry_count=attempt
                    )
                time.sleep(self.config.retry_delay * (attempt + 1))
                
            except requests.exceptions.ConnectionError as e:
                if attempt == self.config.max_retries:
                    return APIResponse(
                        success=False,
                        content="",
                        error=f"Connection error after {self.config.max_retries + 1} attempts",
                        response_time=time.time() - start_time,
                        retry_count=attempt
                    )
                time.sleep(self.config.retry_delay * (attempt + 1))
                
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt == self.config.max_retries:
                    return APIResponse(
                        success=False,
                        content="",
                        error=f"Unexpected error: {str(e)}",
                        response_time=time.time() - start_time,
                        retry_count=attempt
                    )
                time.sleep(self.config.retry_delay * (attempt + 1))
        
        # Should never reach here, but just in case
        return APIResponse(
            success=False,
            content="",
            error="Maximum retries exceeded",
            response_time=time.time() - start_time
        )
    
    def _make_request(self, request: GenerationRequest) -> APIResponse:
        """Make a single API request"""
        
        start_time = time.time()
        
        # Prepare messages
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})
        
        # Prepare payload
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "frequency_penalty": request.frequency_penalty,
            "presence_penalty": request.presence_penalty,
            "stream": False
        }
        
        # Log request details
        logger.debug(f"   🌐 Making API call to {self.base_url}")
        logger.debug(f"   📦 Payload size: {len(json.dumps(payload))} bytes")
        
        # Make request
        response = self.session.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload,
            timeout=(self.timeout_connect, self.timeout_read)
        )
        
        response_time = time.time() - start_time
        
        # Log response status
        logger.debug(f"   📡 HTTP {response.status_code} in {response_time:.2f}s")
        
        # Process response
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            # Handle empty content from reasoning models like grok-4
            if not content and data.get('choices', [{}])[0].get('message', {}).get('content') == "":
                completion_tokens = data.get('usage', {}).get('completion_tokens_details', {}).get('reasoning_tokens', 0)
                if completion_tokens > 0:
                    logger.warning("   ⚠️  Model produced reasoning tokens but no completion content")
                    return APIResponse(
                        success=False,
                        content="",
                        error="Model produced reasoning tokens but no completion content. This may indicate the model needs different parameters.",
                        response_time=response_time,
                        token_count=data.get('usage', {}).get('total_tokens'),
                        model_used=data.get('model', self.model)
                    )
            
            # Extract usage information
            usage = data.get('usage', {})
            
            return APIResponse(
                success=True,
                content=content,
                response_time=response_time,
                token_count=usage.get('total_tokens'),
                prompt_tokens=usage.get('prompt_tokens'),
                completion_tokens=usage.get('completion_tokens'),
                model_used=data.get('model', self.model),
                request_id=response.headers.get('x-request-id')
            )
        else:
            # Handle error response
            error_msg = f"API request failed with status {response.status_code}"
            try:
                error_data = response.json()
                error_details = error_data.get('error', {})
                error_msg += f": {error_details.get('message', 'Unknown error')}"
                
                # Log additional error details
                if 'type' in error_details:
                    logger.error(f"Error type: {error_details['type']}")
                if 'code' in error_details:
                    logger.error(f"Error code: {error_details['code']}")
                    
            except json.JSONDecodeError:
                error_msg += f": {response.text}"
            
            return APIResponse(
                success=False,
                content="",
                error=error_msg,
                response_time=response_time
            )
    
    def generate_simple(self, prompt: str, system_prompt: Optional[str] = None, 
                       max_tokens: int = None, temperature: float = None) -> APIResponse:
        """Simplified generation method for backward compatibility"""
        
        request = GenerationRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens or self.config.max_tokens,
            temperature=temperature if temperature is not None else self.config.temperature
        )
        
        return self.generate(request)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get client usage statistics"""
        
        avg_response_time = (
            self.stats['total_response_time'] / self.stats['total_requests']
            if self.stats['total_requests'] > 0 else 0
        )
        
        success_rate = (
            self.stats['successful_requests'] / self.stats['total_requests'] * 100
            if self.stats['total_requests'] > 0 else 0
        )
        
        return {
            **self.stats,
            'average_response_time': avg_response_time,
            'success_rate': success_rate
        }
    
    def reset_statistics(self):
        """Reset usage statistics"""
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_tokens': 0,
            'total_response_time': 0.0
        }

class MockAPIClient:
    """Mock API client for testing without real API calls"""
    
    def __init__(self, *args, **kwargs):
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_tokens': 0,
            'total_response_time': 0.0
        }
    
    def test_connection(self) -> bool:
        """Mock connection test - always returns True"""
        return True
    
    def generate(self, request: GenerationRequest) -> APIResponse:
        """Generate mock content for testing"""
        
        self.stats['total_requests'] += 1
        self.stats['successful_requests'] += 1
        
        # Generate realistic mock content based on prompt
        prompt_lower = request.prompt.lower()
        
        if "frontmatter" in prompt_lower:
            content = self._generate_mock_frontmatter(request.prompt)
        elif "content" in prompt_lower or "article" in prompt_lower:
            content = self._generate_mock_article(request.prompt)
        elif "table" in prompt_lower:
            content = self._generate_mock_table(request.prompt)
        elif "json" in prompt_lower or "jsonld" in prompt_lower:
            content = self._generate_mock_jsonld(request.prompt)
        else:
            content = f"Mock generated content for: {request.prompt[:100]}..."
        
        mock_tokens = len(content.split())
        self.stats['total_tokens'] += mock_tokens
        
        return APIResponse(
            success=True,
            content=content,
            response_time=0.1,
            token_count=mock_tokens,
            prompt_tokens=len(request.prompt.split()),
            completion_tokens=mock_tokens,
            model_used="mock-model"
        )
    
    def generate_simple(self, prompt: str, system_prompt: Optional[str] = None,
                       max_tokens: int = None, temperature: float = None) -> APIResponse:
        """Simplified mock generation"""
        request = GenerationRequest(prompt=prompt, system_prompt=system_prompt)
        return self.generate(request)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get mock statistics"""
        return {**self.stats, 'average_response_time': 0.1, 'success_rate': 100.0}
    
    def reset_statistics(self):
        """Reset mock statistics"""
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_tokens': 0,
            'total_response_time': 0.0
        }
    
    def _generate_mock_frontmatter(self, prompt: str) -> str:
        """Generate mock frontmatter"""
        material = "Test Material"
        for word in prompt.split():
            if word.istitle() and len(word) > 3:
                material = word
                break
        
        return f"""---
name: {material}
description: "Mock description for {material} laser cleaning applications"
category: "metal"
author: "Mock Expert"
keywords: {material.lower()}, laser cleaning, surface preparation
chemicalProperties:
  symbol: "Tm"
  formula: "TestMaterial"
  materialType: "compound"
properties:
  density: "7.8 g/cm³"
  meltingPoint: "1500°C"
  wavelength: "1064nm"
applications:
- industry: "Manufacturing"
  useCase: "Surface cleaning and preparation"
  detail: "Mock application details"
title: "Laser Cleaning {material} - Technical Guide"
headline: "Comprehensive guide for {material} laser processing"
---"""
    
    def _generate_mock_article(self, prompt: str) -> str:
        """Generate mock article content"""
        return """# Mock Article Content

This is mock-generated content for testing the dynamic generation system.

## Introduction

This content demonstrates the structure and format of generated articles.

## Technical Specifications

- Wavelength: 1064nm
- Power: 50-100W
- Pulse duration: 10-100ns

## Applications

Mock applications and use cases would be listed here.

## Conclusion

This concludes the mock article content generation."""
    
    def _generate_mock_table(self, prompt: str) -> str:
        """Generate mock table content"""
        return """| Property | Value | Unit |
|----------|-------|------|
| Density | 7.8 | g/cm³ |
| Melting Point | 1500 | °C |
| Wavelength | 1064 | nm |
| Power Range | 50-100 | W |"""
    
    def _generate_mock_jsonld(self, prompt: str) -> str:
        """Generate mock JSON-LD content"""
        return """{
  "@context": "https://schema.org/",
  "@type": "Product",
  "name": "Mock Material",
  "description": "Mock material for laser cleaning applications",
  "category": "Industrial Material"
}"""