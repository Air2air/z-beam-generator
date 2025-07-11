#!/usr/bin/env python3
"""
Configuration package - Load authors from authors.json
"""
import os
import json
from typing import Dict, Any
from pathlib import Path

def load_config() -> Dict[str, Any]:
    """Load configuration - includes authors from authors/authors.json"""
    config_dir = Path(__file__).parent
    project_root = config_dir.parent
    config = {}
    
    # Load JSON files from config directory
    json_files = ['api.json', 'debug.json', 'generation.json', 'paths.json', 'providers.json', 'tags.json', 'thresholds.json']
    
    for filename in json_files:
        file_path = config_dir / filename
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    key = filename.replace('.json', '')
                    config[key] = file_config
            except Exception as e:
                print(f"Warning: Could not load {filename}: {e}")
    
    # Load authors from authors/authors.json
    authors_file = project_root / 'authors' / 'authors.json'
    if authors_file.exists():
        try:
            with open(authors_file, 'r', encoding='utf-8') as f:
                authors_list = json.load(f)
                # Convert list to dict with ID as key
                authors_dict = {}
                for author in authors_list:
                    if 'id' in author:
                        authors_dict[str(author['id'])] = author
                config['authors'] = authors_dict
        except Exception as e:
            print(f"Warning: Could not load authors.json: {e}")
    else:
        print(f"Warning: Authors file not found: {authors_file}")
    
    # Load constants.py if it exists
    constants_file = config_dir / 'constants.py'
    if constants_file.exists():
        try:
            import sys
            sys.path.insert(0, str(config_dir))
            import constants
            config['constants'] = {}
            
            # Get all uppercase attributes as constants
            for attr_name in dir(constants):
                if not attr_name.startswith('_') and attr_name.isupper():
                    config['constants'][attr_name] = getattr(constants, attr_name)
        except Exception as e:
            print(f"Warning: Could not load constants.py: {e}")
    
    # Add environment defaults
    config.update({
        'api_base_url': os.getenv('API_BASE_URL', 'https://api.example.com'),
        'api_key': os.getenv('API_KEY', ''),
        'api_timeout': int(os.getenv('API_TIMEOUT', '30')),
        'default_author_id': int(os.getenv('DEFAULT_AUTHOR_ID', '1')),
        'output_directory': os.getenv('OUTPUT_DIRECTORY', 'output'),
        'create_directories': True,
        'log_level': 'INFO',
        'model_name': os.getenv('MODEL_NAME', 'DEEPSEEK/deepseek-chat'),
        'default_image_url': os.getenv('DEFAULT_IMAGE_URL', 'https://example.com/laser-cleaning-image.jpg'),
        'default_encoding': 'utf-8'
    })
    
    return config

def get_config_value(key: str, default: Any = None) -> Any:
    """Get a specific configuration value"""
    config = load_config()
    return config.get(key, default)

def get_author_info(author_id: int) -> Dict[str, Any]:
    """Get author information by ID"""
    config = load_config()
    authors = config.get('authors', {})
    return authors.get(str(author_id), {})