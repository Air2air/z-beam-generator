#!/usr/bin/env python3
"""
Z-Beam Generator - Simplified with GlobalConfigManager
"""


def main():

    # User settings
    context = {"material": "titaniun", "author_id": 2, "article_type": "material"}

    # Initialize configuration
    config = {
        "provider": "OPENAI",
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "metadata_temperature": 0.3,
        "max_tokens": 4000,
        "optimization_mode": "sample",
        "prompts_dir": "prompts",
        "output_dir": "output",
        "authors_file": "authors/authors.json",
        "sections_file": "sections/sections.json",
    }


if __name__ == "__main__":
    main()
