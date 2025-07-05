# Prompts Directory

This directory contains all prompt templates used for content generation and detection.

- `detection/`: Prompts for AI and human-likeness detection, rewrite instructions, etc.
- `sections/`: Prompts for each article section type (e.g., introduction, chart, comparison).

All prompt loading should be done via the `PromptManager` class in `generator/modules/prompt_manager.py` for consistency and caching.
