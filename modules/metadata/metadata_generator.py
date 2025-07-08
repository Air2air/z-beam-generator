import json
import logging
import re
import os
from pathlib import Path
from jinja2 import Template
from modules.api_client import APIClient

logger = logging.getLogger(__name__)

class MetadataGenerator:
    def __init__(self, config, module_config):
        self.config = config
        self.module_config = module_config
        self.api_client = APIClient(config)
    
    def execute(self, context):
        """Generate metadata using PRIMARY USER SETTINGS"""
        logger.info("📊 Generating metadata...")
        
        # Read prompt template
        prompt_path = Path(self.config["metadata_prompt"])
        if not prompt_path.exists():
            raise FileNotFoundError(f"Metadata prompt not found: {prompt_path}")
        
        prompt_template = prompt_path.read_text(encoding='utf-8')
        
        # Use Jinja2 template engine for advanced features
        try:
            template = Template(prompt_template)
            prompt = template.render(
                materialType=context["materialType"],
                authorId=context["authorId"],
                articleType=context["articleType"]
            )
            
            # DEBUG: Log the rendered prompt to see what's being sent
            logger.info(f"🔍 Rendered prompt preview: {prompt[:200]}...")
            
        except Exception as e:
            logger.error(f"❌ Template rendering failed: {e}")
            logger.error(f"Available context keys: {list(context.keys())}")
            raise
        
        # Generate metadata
        response = self.api_client.generate_content(
            prompt=prompt,
            provider=self.module_config["provider"],
            temperature=self.config["metadata_temperature"]
        )
        
        # DEBUG: Log the raw response to see what we're getting
        logger.info(f"🔍 Raw API response preview: {response[:200]}...")
        
        # Parse and convert to YAML frontmatter
        metadata_yaml = self._parse_metadata(response)
        
        logger.info("✅ Metadata generated successfully")
        return metadata_yaml
    
    def _parse_metadata(self, response):
        """Extract JSON from xaiArtifact wrapper and convert to YAML frontmatter"""
        try:
            # First, extract JSON from <xaiArtifact> tags
            artifact_match = re.search(r'<xaiArtifact[^>]*>(.*?)</xaiArtifact>', response, re.DOTALL)
            if artifact_match:
                json_content = artifact_match.group(1).strip()
            else:
                # Fallback: look for JSON in markdown code blocks
                code_block_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', response, re.DOTALL)
                if code_block_match:
                    json_content = code_block_match.group(1).strip()
                else:
                    # Fallback: look for JSON directly
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        json_content = json_match.group(0)
                    else:
                        logger.error("❌ No JSON found in response. Full response:")
                        logger.error(response)
                        raise ValueError("No JSON found in response")
            
            # Clean up any remaining markdown formatting
            json_content = json_content.strip()
            if json_content.startswith('```'):
                json_content = json_content.split('\n', 1)[1]
            if json_content.endswith('```'):
                json_content = json_content.rsplit('\n', 1)[0]
            
            # Parse JSON
            metadata = json.loads(json_content)
            
            # Convert to YAML frontmatter
            yaml_frontmatter = self._json_to_yaml_frontmatter(metadata)
            
            return yaml_frontmatter
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"❌ Failed to parse metadata: {e}")
            logger.error(f"Response: {response[:500]}...")
            raise
    
    def _json_to_yaml_frontmatter(self, metadata):
        """Convert JSON metadata to YAML frontmatter"""
        yaml_lines = ["---"]
        
        # Convert key metadata fields to YAML
        for key, value in metadata.items():
            if isinstance(value, str):
                yaml_lines.append(f'{key}: "{value}"')
            elif isinstance(value, (int, float, bool)):
                yaml_lines.append(f'{key}: {value}')
            elif isinstance(value, list):
                yaml_lines.append(f'{key}: {json.dumps(value)}')
            elif isinstance(value, dict):
                yaml_lines.append(f'{key}: {json.dumps(value)}')
            elif value is None:
                yaml_lines.append(f'{key}: null')
        
        yaml_lines.append("---")
        return "\n".join(yaml_lines)