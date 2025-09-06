#!/usr/bin/env python3
"""
Script Name: Debug Configuration Loading
Description: Debug what's being loaded from base configuration files
Usage: python3 scripts/debug_config.py
Dependencies: pathlib, yaml
Last Updated: 2025-09-05
"""

from pathlib import Path

import yaml


def debug_base_config():
    """Debug what's being loaded from base config"""
    base_prompt_file = "components/text/prompts/base_content_prompt.yaml"

    print(f"Checking file: {base_prompt_file}")
    print(f"File exists: {Path(base_prompt_file).exists()}")

    if Path(base_prompt_file).exists():
        with open(base_prompt_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        print(f"Loaded data type: {type(data)}")
        print(f"Loaded data: {data}")

        if data:
            print("Top-level keys:")
            for key in data.keys():
                print(f"  - {key}")

            if "author_configurations" in data:
                print("✅ author_configurations found")
                print(f"Content: {data['author_configurations']}")
            else:
                print("❌ author_configurations NOT found")

            if "technical_requirements" in data:
                print("✅ technical_requirements found")
            else:
                print("❌ technical_requirements NOT found")
        else:
            print("❌ Data is empty/None")


if __name__ == "__main__":
    debug_base_config()
