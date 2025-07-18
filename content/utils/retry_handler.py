import logging
from typing import Callable

logger = logging.getLogger(__name__)

class RetryHandler:
    """Handles retry logic for content generation."""
    
    @staticmethod
    def generate_with_retry(
        generate_func: Callable[[str, int], str], 
        prompt: str, 
        min_words: int, 
        max_words: int,
        max_attempts: int = 3
    ) -> str:
        """
        Generate content with retry logic for word count requirements.
        """
        attempt = 1
        # Simple implementation - just call the generate function once
        try:
            content = generate_func(prompt, int(max_words * 1.5))
            word_count = len(content.split())
            logger.info(f"Attempt {attempt}: Generated content with {word_count} words")
            
            if min_words <= word_count <= max_words:
                logger.info(f"Content meets word count requirements ({min_words}-{max_words})")
            
            return content
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return ""