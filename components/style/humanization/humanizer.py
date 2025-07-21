"""Helper functions to make writing more human-like."""

import random
from typing import Any, Dict, List
from .variations import get_humanizing_techniques

def get_humanization_instructions(params: Dict[str, Any] = None) -> str:
    """Get randomized instructions to make AI output more human-like."""
    if params is None:
        params = {}
    
    # Use parameters for configuration if provided
    min_techniques = params.get("min_humanization_techniques", 3)
    max_techniques = params.get("max_humanization_techniques", 5)
    
    intro_phrases = [
        "For more natural writing:",
        "To sound more like a human author:",
        "To create more authentic content:",
        "For a more natural voice:",
        "To improve writing authenticity:"
    ]
    
    # Get techniques from variations module
    human_techniques = get_humanizing_techniques()
    
    # Select a random intro phrase
    intro = random.choice(intro_phrases)
    
    # Select min_techniques to max_techniques random techniques
    selected_techniques = random.sample(human_techniques, 
                                       random.randint(min_techniques, max_techniques))
    
    # Format as bullet points
    techniques = "\n".join(f"- {technique}" for technique in selected_techniques)
    
    return f"{intro}\n{techniques}"