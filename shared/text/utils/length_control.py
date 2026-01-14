"""
Length Control Utilities for Text Generation

Provides smart truncation and length control functions to ensure generated
text meets target word count requirements while preserving content quality.

Key Features:
- Smart truncation at sentence boundaries
- Preserves content meaning and flow
- Configurable word count targets
- Fallback to word-level truncation

Usage:
    from shared.text.utils.length_control import smart_truncate_to_word_count
    
    content = "Long generated text..."
    truncated = smart_truncate_to_word_count(content, target_words=30)
"""

import re
from typing import Optional


def smart_truncate_to_word_count(content: str, target_words: int, tolerance: float = 0.1) -> str:
    """
    Truncate content to target word count with intelligent sentence boundary detection.
    
    Strategy:
    1. If already within target, return as-is
    2. Try to find sentence boundary within tolerance (default 10% over target)
    3. Fallback to word-level truncation if no good sentence boundary found
    
    Args:
        content: Generated text content to truncate
        target_words: Target word count to achieve
        tolerance: Allowable overage as percentage (0.1 = 10% over target allowed)
        
    Returns:
        Truncated content that meets target word count
        
    Examples:
        >>> content = "This is a test. It has multiple sentences. Each with different lengths."
        >>> smart_truncate_to_word_count(content, 8)
        'This is a test. It has multiple sentences.'
        
        >>> smart_truncate_to_word_count(content, 5)
        'This is a test. It has'
    """
    if not content or not content.strip():
        return content
    
    content = content.strip()
    words = content.split()
    
    # If already within target, return as-is
    if len(words) <= target_words:
        return content
    
    # Calculate tolerance window
    max_allowed_words = int(target_words * (1 + tolerance))
    
    # Try to find good sentence boundary within tolerance
    sentence_endings = ['. ', '! ', '? ']
    sentences = []
    
    # Split on sentence boundaries while preserving the punctuation
    current_sentence = ""
    for char in content:
        current_sentence += char
        if char in '.!?' and (current_sentence.endswith('. ') or 
                             current_sentence.endswith('! ') or 
                             current_sentence.endswith('? ') or
                             char == content[-1]):  # End of content
            sentences.append(current_sentence.strip())
            current_sentence = ""
    
    # If we have remaining content (no final punctuation), add it
    if current_sentence.strip():
        sentences.append(current_sentence.strip())
    
    # Find best sentence boundary within tolerance
    best_candidate = ""
    for i in range(len(sentences)):
        candidate = '. '.join(sentences[:i+1])
        if not candidate.endswith('.') and not candidate.endswith('!') and not candidate.endswith('?'):
            candidate += '.'
        
        candidate_words = len(candidate.split())
        
        # Perfect match or within tolerance
        if candidate_words <= target_words:
            best_candidate = candidate
        elif candidate_words <= max_allowed_words:
            # Slightly over but within tolerance
            return candidate
        else:
            # Too long, use previous candidate or fallback
            break
    
    # If we found a good sentence boundary candidate, use it
    if best_candidate and len(best_candidate.split()) >= target_words * 0.8:  # At least 80% of target
        return best_candidate
    
    # Fallback: word-level truncation
    truncated_words = words[:target_words]
    truncated_content = ' '.join(truncated_words)
    
    # Try to avoid cutting in the middle of a sentence awkwardly
    if truncated_content and not truncated_content[-1].isalnum():
        return truncated_content
    
    # Add period if the truncation doesn't end naturally
    if not truncated_content.endswith(('.', '!', '?')):
        # Only add period if it doesn't create an awkward phrase
        if len(truncated_words) >= 5:  # At least 5 words for a complete thought
            truncated_content += '.'
    
    return truncated_content


def get_word_count(text: str) -> int:
    """
    Get accurate word count for text.
    
    Args:
        text: Text to count words in
        
    Returns:
        Number of words in the text
    """
    if not text:
        return 0
    return len(text.strip().split())


def check_length_compliance(text: str, target_words: int, tolerance: float = 0.1) -> dict:
    """
    Check if text meets length requirements.
    
    Args:
        text: Text to check
        target_words: Target word count
        tolerance: Allowable variance as percentage
        
    Returns:
        Dictionary with compliance information:
        {
            'compliant': bool,
            'word_count': int,
            'target_words': int,
            'variance': float,
            'within_tolerance': bool
        }
    """
    word_count = get_word_count(text)
    variance = abs(word_count - target_words) / target_words if target_words > 0 else 0
    within_tolerance = variance <= tolerance
    
    return {
        'compliant': word_count == target_words,
        'word_count': word_count,
        'target_words': target_words,
        'variance': variance,
        'variance_percent': variance * 100,
        'within_tolerance': within_tolerance,
        'overage': word_count - target_words,
        'overage_percent': ((word_count - target_words) / target_words * 100) if target_words > 0 else 0
    }


def extract_word_count_from_prompt(prompt: str) -> Optional[int]:
    """
    Extract target word count from prompt text.
    
    Looks for patterns like:
    - "Base word count: 30"
    - "EXACTLY 30 words"
    - "Target: 30 words"
    
    Args:
        prompt: Prompt text to analyze
        
    Returns:
        Extracted word count or None if not found
    """
    patterns = [
        r'Base word count:\s*(\d+)',
        r'EXACTLY\s+(\d+)\s+words?',
        r'Target:\s*(\d+)\s+words?',
        r'(\d+)\s+words?\s+exactly',
        r'word count[:\s]+(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            return int(match.group(1))
    
    return None


def apply_length_control(content: str, prompt: str, fallback_target: int = 50) -> dict:
    """
    Apply length control to generated content based on prompt instructions.
    
    Args:
        content: Generated text content
        prompt: Original prompt (may contain word count instructions)
        fallback_target: Target word count if none found in prompt
        
    Returns:
        Dictionary with controlled content and metadata:
        {
            'content': str,           # Length-controlled content
            'original_words': int,    # Original word count
            'final_words': int,       # Final word count after control
            'target_words': int,      # Target word count used
            'truncated': bool,        # Whether content was truncated
            'compliance': dict        # Detailed compliance info
        }
    """
    # Extract target from prompt or use fallback
    target_words = extract_word_count_from_prompt(prompt) or fallback_target
    original_word_count = get_word_count(content)
    
    # Apply smart truncation if needed
    if original_word_count > target_words:
        controlled_content = smart_truncate_to_word_count(content, target_words)
        truncated = True
    else:
        controlled_content = content
        truncated = False
    
    final_word_count = get_word_count(controlled_content)
    compliance = check_length_compliance(controlled_content, target_words)
    
    return {
        'content': controlled_content,
        'original_words': original_word_count,
        'final_words': final_word_count,
        'target_words': target_words,
        'truncated': truncated,
        'compliance': compliance,
        'reduction': original_word_count - final_word_count if truncated else 0
    }


# Example usage and testing
if __name__ == "__main__":
    # Test content
    test_content = """During typical use and storage, aluminum surfaces commonly accumulate dust and particles from the environment. Oil residues from handling create persistent films that attract additional contaminants. Fingerprints leave behind salts and organic compounds that can cause localized corrosion. Moisture exposure leads to oxidation and the formation of aluminum oxide layers."""
    
    print("=== LENGTH CONTROL TESTING ===")
    print(f"Original content ({get_word_count(test_content)} words):")
    print(test_content)
    print()
    
    # Test different target lengths
    for target in [15, 30, 45]:
        print(f"--- Target: {target} words ---")
        result = smart_truncate_to_word_count(test_content, target)
        compliance = check_length_compliance(result, target)
        
        print(f"Result ({compliance['word_count']} words): {result}")
        print(f"Compliant: {compliance['compliant']} (variance: {compliance['variance_percent']:.1f}%)")
        print()
    
    # Test prompt extraction
    test_prompt = "Describe contamination. Base word count: 25. Be specific."
    extracted = extract_word_count_from_prompt(test_prompt)
    print(f"Extracted from prompt '{test_prompt}': {extracted} words")