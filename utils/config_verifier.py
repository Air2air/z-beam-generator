"""Utilities for verifying configuration."""

import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

class ConfigVerifier:
    """Verifies and validates configuration."""
    
    @staticmethod
    def verify_provider_config(context: Dict[str, Any]) -> List[Tuple[bool, str]]:
        """Verify provider configuration.
        
        Args:
            context: Context dictionary with configuration
            
        Returns:
            List of (success, message) tuples with verification results
        """
        results = []
        
        # Check main provider
        main_provider = context.get("ai_provider")
        if main_provider:
            results.append((True, f"Main provider configured: {main_provider}"))
        else:
            results.append((False, "Main provider not configured"))
        
        # Check content provider
        content_provider = context.get("content_provider")
        if content_provider:
            results.append((True, f"Content provider configured: {content_provider}"))
        else:
            results.append((False, "Content provider not configured"))
        
        # Check component-specific providers
        components = context.get("components", {})
        for component_name, component_config in components.items():
            if "ai_provider" in component_config:
                provider = component_config["ai_provider"]
                results.append((True, f"Component '{component_name}' provider: {provider}"))
        
        return results
    
    @staticmethod
    def log_verification_results(results: List[Tuple[bool, str]]):
        """Log verification results.
        
        Args:
            results: List of (success, message) tuples
        """
        logger.info("🔍 CONFIGURATION VERIFICATION:")
        
        for success, message in results:
            if success:
                logger.info(f"  ✅ {message}")
            else:
                logger.warning(f"  ❌ {message}")