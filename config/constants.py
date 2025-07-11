"""
Configuration constants for Z-Beam Generator
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for Z-Beam Generator"""
    
    def __init__(self):
        self._api_config = None
        self._authors = None
        
    @property
    def api_config(self) -> Dict[str, Any]:
        """Get API configuration"""
        if self._api_config is None:
            self._api_config = self._load_api_config()
        return self._api_config
    
    @property
    def authors(self) -> Dict[str, Any]:
        """Get authors configuration"""
        if self._authors is None:
            self._authors = self._load_authors_config()
        return self._authors
    
    def get_full_config(self) -> Dict[str, Any]:
        """Get complete configuration combining all sources"""
        return {
            **self.api_config,
            "authors": self.authors,
        }
    
    def _load_api_config(self) -> Dict[str, Any]:
        """Load API configuration from config/api.json"""
        return self._load_config_file("config/api.json")
    
    def _load_authors_config(self) -> Dict[str, Any]:
        """Load authors configuration from authors/authors.json"""
        return self._load_config_file("authors/authors.json")
    
    def _load_config_file(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        config_path = Path(config_file)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Required config file missing: {config_file}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Remove comments (lines starting with //)
                lines = content.split('\n')
                clean_lines = [line for line in lines if not line.strip().startswith('//')]
                clean_content = '\n'.join(clean_lines)
                
                return json.loads(clean_content)
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in {config_file}: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error loading {config_file}: {e}")
            raise

# Global configuration instance
CONFIG = Config()