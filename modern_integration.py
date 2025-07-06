"""
Z-Beam Modern Architecture Integration

This module integrates the modern clean architecture implementation with
the existing Z-Beam application, providing a bridge between the two.
"""

import sys
import os
import asyncio
from typing import Dict, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.di.service_configuration import get_configured_container
from application.commands.content_generation import ContentGenerationHandler, GenerateContentCommand
from domain.value_objects.content_specs import ContentSpecs
from config.global_config import GlobalConfigManager


class ModernZBeamIntegration:
    """
    Integration layer that connects the modern clean architecture
    with the existing Z-Beam application.
    """
    
    def __init__(self):
        self._container = None
        self._config_manager = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the modern architecture components."""
        if self._initialized:
            return
            
        # Get configuration from the global config (already initialized)
        self._config_manager = GlobalConfigManager.get_instance()
        
        # Get fully configured container with all services
        self._container = get_configured_container()
        
        self._initialized = True
        print("✅ Modern Z-Beam architecture initialized")
    
    async def generate_content(
        self,
        material: str,
        category: str,
        author: str,
        max_words: Optional[int] = None,
        target_style: str = "professional"
    ) -> Dict[str, Any]:
        """
        Generate content using the modern architecture.
        Returns a dictionary with results and metadata.
        """
        if not self._initialized:
            await self.initialize()
        
        # Get max words from config if not provided
        if max_words is None:
            max_words = self._config_manager.get_max_article_words()
        
        # Create content specs
        specs = ContentSpecs(
            max_words=max_words,
            target_style=target_style,
            requirements=[
                "Include practical applications",
                "Provide technical details",
                "Write in natural, engaging style",
                "Avoid AI-like repetitive phrasing"
            ]
        )
        
        # Create command
        command = GenerateContentCommand(
            material=material,
            category=category,
            author=author,
            specs=specs
        )
        
        # Get command handler from container
        handler = await self._container.resolve(ContentGenerationHandler)
        
        # Execute command
        result = await handler.handle(command)
        
        # Return structured result for the legacy system
        if result.success:
            return {
                "success": True,
                "content": result.content.body,
                "content_id": result.content.id,
                "ai_score": result.detection_result.ai_score,
                "human_score": result.detection_result.human_score,
                "confidence": result.detection_result.ai_confidence,  # Use ai_confidence as the general confidence
                "word_count": result.metadata.word_count,
                "metadata": {
                    "title": result.metadata.title,
                    "description": result.metadata.description,
                    "author": result.metadata.author,
                    "category": result.metadata.category,
                    "material": result.metadata.material,
                    "tags": result.metadata.tags
                }
            }
        else:
            return {
                "success": False,
                "error": result.message
            }
    
    async def shutdown(self) -> None:
        """Shutdown the modern architecture components."""
        # In a real implementation, we might have cleanup logic here
        self._initialized = False
        print("👋 Modern architecture shutdown complete")


# Singleton instance for global access
_instance = None

def get_modern_architecture() -> ModernZBeamIntegration:
    """Get or create the singleton instance of the modern architecture integration."""
    global _instance
    if _instance is None:
        _instance = ModernZBeamIntegration()
    return _instance


async def test_integration():
    """Test the modern architecture integration."""
    # Initialize configuration first
    from config.global_config import GlobalConfigManager
    
    # Basic test configuration
    USER_CONFIG = {
        "material": "Bronze",
        "category": "Material",
        "generator_provider": "TEST",  # Changed to TEST for testing
        "detection_provider": "TEST",  # Changed to TEST for testing
        "api_timeout": 45,
        "max_article_words": 800,
    }
    
    PROVIDER_MODELS = {
        "DEEPSEEK": {
            "model": "deepseek-chat",
            "url_template": "https://api.deepseek.com/v1/chat/completions",  # FALLBACK
        },
        "XAI": {
            "model": "grok-3-mini-beta",
            "url_template": "https://api.x.ai/v1/chat/completions",  # FALLBACK
        },
        "TEST": {  # Added TEST provider for testing
            "model": "test-model",
            "url_template": "http://localhost:8000/test",  # FALLBACK
        }
    }
    
    # Initialize config manager
    GlobalConfigManager.initialize(USER_CONFIG, PROVIDER_MODELS)
    
    # Now proceed with integration
    integration = get_modern_architecture()
    await integration.initialize()
    
    result = await integration.generate_content(
        material="Bronze",
        category="Material",
        author="todd_dunning.mdx",
        max_words=800
    )
    
    if result["success"]:
        print("✅ Content generated successfully!")
        print(f"📊 AI Detection Score: {result['ai_score']:.1f}")
        print(f"🗣️ Human Voice Score: {result['human_score']:.1f}")
        print(f"🎯 Confidence: {result['confidence']:.2f}")
        print(f"📝 Word Count: {result['word_count']}")
        print(f"💾 Content ID: {result['content_id']}")
        print("\n--- Content Preview ---")
        print(result["content"][:300] + "...")
    else:
        print(f"❌ Content generation failed: {result['error']}")
    
    await integration.shutdown()


if __name__ == "__main__":
    asyncio.run(test_integration())
