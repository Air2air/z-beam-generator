"""
API MODULE DIRECTIVES FOR AI ASSISTANTS:
1. INTERFACE COMPLIANCE: All provider implementations must implement every method defined here
2. NO EXTENSIONS: Do not add methods to provider implementations that aren't defined in this base class
3. SIGNATURE MATCHING: Method signatures in implementations must exactly match these definitions
4. ERROR HANDLING: All methods must handle provider-specific errors and convert to standard errors
"""

from abc import ABC, abstractmethod
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class BaseProvider(ABC):
    """Base class for all AI providers."""
    
    def __init__(self, context=None):
        """Initialize the provider."""
        self.context = context or {}
        
    @abstractmethod
    def generate(self, prompt: str, **options) -> str:
        """Generate text using this provider."""
        pass
        
    def get_default_model(self) -> str:
        """Get default model for this provider."""
        return "default-model"