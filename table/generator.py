import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class TableGenerator:
    """Generates markdown tables for technical articles from schema-driven metadata."""

    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], metadata: Dict[str, Any]):
        self.context = context
        self.schema = schema
        self.metadata = metadata
        self.prompt_config = self._load_prompt_template()

    def _load_prompt_template(self) -> Dict[str, Any]:
        try:
            prompt_path = Path(__file__).parent / "prompt.yaml"
            with open(prompt_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load table prompt template: {e}")
            return {}

    def generate(self) -> Optional[str]:
        """Generate a markdown table from metadata."""
        try:
            template = self.prompt_config.get("template", "")
            if not template:
                logger.error("No table prompt template found")
                return None

            # Prepare table rows from metadata (example: manufacturingCenters)
            centers = self.metadata.get("manufacturingCenters", [])
            rows = []
            for center in centers:
                name = center.get("name", "")
                usage = center.get("laserCleaningUsage", "")
                address = center.get("address", "")
                rows.append(f"| {name} | {usage} | {address} |")

            # Build the table string
            table_header = template.format()
            table_body = "\n".join(rows)
            markdown_table = f"{table_header}\n{table_body}"

            logger.info("Successfully generated markdown table")
            return markdown_table
        except Exception as e:
            logger.error(f"Table generation failed: {e}")
            return None