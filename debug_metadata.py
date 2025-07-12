#!/usr/bin/env python3
"""Debug metadata generation to see raw API response."""

import os
import json
from pathlib import Path

# Load environment variables manually
def load_env_file():
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Load environment
load_env_file()

from api_client import APIClient
from metadata.generator import MetadataGenerator

def main():
    print("🔍 Debugging Metadata Generation")
    print("=" * 50)
    
    # Load schema
    schema_path = Path("schemas/definitions/material_schema_definition.json")
    with open(schema_path, 'r') as f:
        schema = json.load(f)
    
    # Create context
    context = {
        "article_type": "material",
        "subject": "Aluminum",
        "ai_provider": "openai",
        "generation_timestamp": "2024-01-01T00:00:00",
        "model_used": "gpt-4",
        "lastUpdated": "2024-01-01",
        "publishedAt": "2024-01-01"
    }
    
    # Create generator
    generator = MetadataGenerator(context, schema, "openai")
    
    # Build prompt
    prompt = generator._build_metadata_prompt()
    print("🤖 Generated Prompt:")
    print("-" * 40)
    print(prompt)
    print("-" * 40)
    
    # Get raw API response
    print("\n📡 Making API call...")
    api_client = APIClient("openai")
    response = api_client.generate(prompt, max_tokens=800)
    
    print("\n📝 Raw API Response:")
    print("-" * 40)
    print(repr(response))  # Shows exact characters including newlines
    print("-" * 40)
    
    print("\n📝 Formatted Response:")
    print("-" * 40)
    print(response)
    print("-" * 40)
    
    # Try to parse YAML
    import yaml
    try:
        parsed = yaml.safe_load(response)
        print("\n✅ YAML Parsing Success:")
        print(json.dumps(parsed, indent=2))
    except yaml.YAMLError as e:
        print(f"\n❌ YAML Parsing Error: {e}")
        print(f"Error at line: {e.problem_mark.line if hasattr(e, 'problem_mark') else 'unknown'}")
        
        # Try to show problematic lines
        lines = response.split('\n')
        for i, line in enumerate(lines):
            print(f"{i+1:3d}: {repr(line)}")

if __name__ == "__main__":
    main()