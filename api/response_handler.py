class ResponseHandler:
    """Unified handler for API responses from different providers."""
    
    @staticmethod
    def extract_content(response, provider):
        """Extract content from API response based on provider."""
        if provider == "deepseek":
            return ResponseHandler._extract_deepseek_content(response)
        elif provider == "xai":
            return ResponseHandler._extract_xai_content(response)
        # Add other providers as needed
        else:
            raise ValueError(f"Unsupported provider: {provider}")
            
    @staticmethod
    def _extract_deepseek_content(response):
        """Extract content from Deepseek API response."""
        try:
            return response.get("choices", [{}])[0].get("message", {}).get("content", "")
        except (KeyError, IndexError):
            raise ValueError("Invalid Deepseek API response format")
            
    @staticmethod
    def _extract_xai_content(response):
        """Extract content from XAI API response."""
        try:
            return response.get("choices", [{}])[0].get("text", "")
        except (KeyError, IndexError):
            raise ValueError("Invalid XAI API response format")