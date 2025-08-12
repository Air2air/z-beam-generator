"""
Document Processor - Minimal Implementation

Processes unified API responses into individual component files.
Uses BATCH_CONFIG from run.py for consistency.
"""

import logging
import json
import yaml
import os
import sys
from typing import Dict, Any
from pathlib import Path

# Add project root to path to import BATCH_CONFIG
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Processes unified responses into component files using BATCH_CONFIG."""
    
    def __init__(self, content_dir: str = None):
        # Import BATCH_CONFIG
        from run import BATCH_CONFIG
        self.config = BATCH_CONFIG
        
        # Use configured base directory
        if content_dir:
            self.content_dir = Path(content_dir)
        else:
            self.content_dir = Path(self.config["output"]["base_dir"])
        
        self.content_dir.mkdir(parents=True, exist_ok=True)
    
    def process_unified_response(self, document: Dict[str, Any], subject: str, 
                               article_type: str, category: str = "") -> Dict[str, bool]:
        """Process document into component files using BATCH_CONFIG."""
        
        results = {}
        
        # Only process enabled components from BATCH_CONFIG
        enabled_components = []
        for name, config in self.config["components"].items():
            if config.get("enabled", False):
                enabled_components.append(name)
        
        for component_name in enabled_components:
            if component_name in document:
                try:
                    # Format content
                    content = self._format_component(component_name, document[component_name], subject)
                    
                    # Save file using BATCH_CONFIG patterns
                    success = self._save_file(component_name, content, subject, article_type, category)
                    results[component_name] = success
                    
                except Exception as e:
                    logger.error(f"Failed to process {component_name}: {e}")
                    results[component_name] = False
            else:
                logger.warning(f"Component {component_name} not found in unified response")
                results[component_name] = False
        
        return results
    
    def _format_component(self, component_name: str, data: Any, subject: str) -> str:
        """Format component data."""
        
        if component_name == "frontmatter":
            yaml_content = yaml.dump(data, default_flow_style=False)
            return f"---\n{yaml_content.strip()}\n---"
        
        elif component_name == "content":
            return str(data).strip()
        
        elif component_name == "table":
            headers = data.get("headers", ["Property", "Value"])
            rows = data.get("rows", [])
            
            if not rows:
                return f"# {subject} Properties\n\n| Property | Value |\n|----------|-------|\n| No data | available |"
            
            header_row = "| " + " | ".join(headers) + " |"
            separator_row = "|" + "|".join(["-" * 10 for _ in headers]) + "|"
            data_rows = ["| " + " | ".join([str(cell) for cell in row]) + " |" for row in rows]
            
            table = "\n".join([header_row, separator_row] + data_rows)
            return f"# {subject} Properties\n\n{table}"
        
        elif component_name == "bullets":
            bullets = [f"- {bullet}" for bullet in data]
            return f"# {subject} Key Points\n\n" + "\n".join(bullets)
        
        elif component_name == "tags":
            return yaml.dump(data, default_flow_style=False).strip()
        
        elif component_name == "metatags":
            yaml_content = yaml.dump(data, default_flow_style=False)
            return f"---\n{yaml_content.strip()}\n---"
        
        elif component_name == "jsonld":
            return json.dumps(data, indent=2, ensure_ascii=False)
        
        else:
            return str(data)
    
    def _save_file(self, component_name: str, content: str, subject: str, 
                   article_type: str, category: str = "") -> bool:
        """Save component file using BATCH_CONFIG filename patterns."""
        
        try:
            # Use the same logic as the main system
            from run import get_component_output_path
            
            # Get the correct output path using BATCH_CONFIG patterns
            output_path = get_component_output_path(component_name, subject, category, article_type)
            
            # Write the file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Saved {component_name} to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save {component_name}: {e}")
            return False
