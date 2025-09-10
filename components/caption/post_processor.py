"""
Caption component post-processor for content cleanup and enhancement.
"""
import logging
import re

logger = logging.getLogger(__name__)


def post_process_caption(content: str, material_name: str = "") -> str:
    """
    Post-process caption content for consistency and quality.

    Args:
        content: Generated caption content
        material_name: Name of the material being processed

    Returns:
        str: Post-processed caption content
    """
    if not content or not content.strip():
        return content

    # Clean up common formatting issues but preserve caption structure
    processed = content.strip()

    # For captions, preserve the double newline between lines
    lines = processed.split('\n')
    if len(lines) >= 2:
        # Keep the structure but clean individual lines
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:
                # Normalize whitespace within lines but preserve structure
                line = re.sub(r"\s+", " ", line)
                line = re.sub(r"\.{2,}", ".", line)  # Remove multiple periods
                cleaned_lines.append(line)
        
        # Rejoin with proper spacing for caption format
        if len(cleaned_lines) == 2:
            processed = cleaned_lines[0] + '\n\n' + cleaned_lines[1]
        else:
            processed = '\n\n'.join(cleaned_lines)
    else:
        # Single line processing
        processed = re.sub(r"\s+", " ", processed)  # Normalize whitespace
        processed = re.sub(r"\.{2,}", ".", processed)  # Remove multiple periods

    # Clean up technical terms
    technical_replacements = {
        "laser cleaning": "laser cleaning",
        "contaminant": "contaminant",
        "substrate": "substrate",
        "surface": "surface",
    }

    for old_term, new_term in technical_replacements.items():
        processed = re.sub(
            rf"\b{re.escape(old_term)}\b", new_term, processed, flags=re.IGNORECASE
        )

    # Material-specific enhancements
    if material_name:
        material_lower = material_name.lower()
        if material_lower in processed.lower() and material_name not in processed:
            processed = re.sub(
                rf"\b{re.escape(material_lower)}\b",
                material_name,
                processed,
                flags=re.IGNORECASE,
            )

    return processed
