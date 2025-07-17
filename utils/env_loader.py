"""Environment variable loader."""

import os
import logging
from pathlib import Path

logger = logging.getLogger("z-beam")

def load_env_file():
    """Load environment variables from .env file."""
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    if 'KEY' in key.upper():
                        logger.info(f"Loaded {key}=****{value[-4:] if len(value) > 4 else '****'}")
                    else:
                        logger.info(f"Loaded {key}={value}")