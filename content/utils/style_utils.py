"""Style utilities replacing randomizer functionality."""

def get_standard_prompt_style():
    """Return a standard prompt style."""
    return {
        "words_per_section": 200,
        "instruction": "Write about {subject} based on this information:",
        "details_instruction": "Provide comprehensive details and explain their significance.",
        "word_count_instruction": "Write approximately {words} words for this section."
    }

def format_section_prompt(section_id, title, subject, data, words):
    """Format a section prompt with standard styling."""
    style = get_standard_prompt_style()
    
    prompt = f"## {title}\n\n"
    prompt += style["instruction"].replace("{subject}", subject) + "\n"
    
    # Add section data/context
    if isinstance(data, str) and data.strip():
        prompt += data.strip() + "\n\n"
    elif isinstance(data, list):
        for item in data:
            if item and item.strip():
                prompt += "- " + item.strip() + "\n"
        prompt += "\n"
    
    # Add standard instructions
    prompt += style["details_instruction"] + "\n\n"
    prompt += style["word_count_instruction"].replace("{words}", str(words)) + "\n"
    
    return prompt