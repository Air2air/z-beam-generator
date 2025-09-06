"""
Bullets component post-processor for content cleanup and enhancement.
"""
import logging
import re

logger = logging.getLogger(__name__)


def post_process_bullets(content: str, material_name: str = "") -> str:
    """
    Post-process bullet points content for consistency and quality.

    Args:
        content: Generated bullets content
        material_name: Name of the material being processed

    Returns:
        str: Post-processed bullets content
    """
    if not content or not content.strip():
        return content

    lines = content.strip().split("\n")
    processed_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            processed_lines.append("")
            continue

        # Ensure bullet points start with proper markdown format
        if line and not line.startswith(
            ("- ", "* ", "+ ", "1. ", "2. ", "3. ", "4. ", "5. ")
        ):
            # If it looks like a bullet point without proper formatting
            if re.match(r"^[•·‣▪▫]", line):
                line = "- " + line[1:].strip()
            elif not line.startswith("#"):  # Don't modify headers
                line = "- " + line

        # Clean up spacing and punctuation
        line = re.sub(r"\s+", " ", line)  # Normalize whitespace

        # Ensure consistent capitalization for bullet points
        if line.startswith(("- ", "* ", "+ ")):
            bullet_content = line[2:].strip()
            if bullet_content and bullet_content[0].islower():
                line = line[:2] + bullet_content[0].upper() + bullet_content[1:]

        # Remove trailing periods from bullet points (optional style choice)
        if (
            line.startswith(("- ", "* ", "+ "))
            and line.endswith(".")
            and not line.endswith("..")
        ):
            line = line[:-1]

        processed_lines.append(line)

    processed = "\n".join(processed_lines)

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
