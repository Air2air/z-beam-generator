import logging
import os
import yaml
from typing import Dict, Any, Optional, List, Union

logger = logging.getLogger(__name__)

class MarkdownFormatter:
    """
    Formats complete markdown document outputs with proper triple backtick code blocks.
    """
    
    @staticmethod
    def format_and_write_markdown(
        output_path: str,
        frontmatter: Union[Dict[str, Any], str],
        content: str = "",
        jsonld: Optional[str] = None,
        tables: Optional[str] = None,
        code_blocks: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Formats and writes a complete markdown document with properly formatted triple backtick code blocks.
        
        Args:
            output_path: Path to write the markdown file
            frontmatter: Dictionary or string of frontmatter data
            content: Main markdown content
            jsonld: Optional JSON-LD content as string
            tables: Optional tables content as string
            code_blocks: Optional list of code blocks with language and content
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, "w", encoding="utf-8") as f:
                # 1. Format frontmatter with triple backticks
                if isinstance(frontmatter, dict):
                    # Convert dict to YAML string
                    f.write("```yaml\n")
                    yaml.dump(frontmatter, f, default_flow_style=False, sort_keys=False)
                    f.write("```\n\n")
                else:
                    # Assume frontmatter is already a string
                    frontmatter_str = str(frontmatter).strip()
                    if frontmatter_str.startswith("---"):
                        # Remove YAML document markers and add triple backticks
                        if frontmatter_str.startswith("---\n"):
                            frontmatter_str = frontmatter_str[4:]
                        if frontmatter_str.endswith("\n---"):
                            frontmatter_str = frontmatter_str[:-4]
                        frontmatter_str = frontmatter_str.strip()
                        f.write("```yaml\n")
                        f.write(frontmatter_str)
                        f.write("\n```\n\n")
                    elif not frontmatter_str.startswith("```yaml"):
                        # Add triple backticks if not present
                        f.write("```yaml\n")
                        f.write(frontmatter_str)
                        f.write("\n```\n\n")
                    else:
                        # Already has triple backticks
                        f.write(frontmatter_str)
                        f.write("\n\n")
                
                # 2. Write main content
                if content:
                    f.write(str(content).strip())
                    f.write("\n\n")
                
                # 3. Format and write JSON-LD with triple backticks if present
                if jsonld:
                    jsonld_str = str(jsonld).strip()
                    if not jsonld_str.startswith("```json"):
                        f.write("```json\n")
                        f.write(jsonld_str)
                        f.write("\n```\n\n")
                    else:
                        # Already has triple backticks
                        f.write(jsonld_str)
                        f.write("\n\n")
                
                # 4. Write tables if present
                if tables:
                    f.write(str(tables).strip())
                    f.write("\n\n")
                
                # 5. Write any additional code blocks
                if code_blocks:
                    for block in code_blocks:
                        language = block.get("language", "")
                        f.write(f"```{language}\n")
                        f.write(block["content"])
                        f.write("\n```\n\n")
                
                logger.info(f"Successfully wrote formatted markdown to {output_path}")
                return True
                
        except Exception as e:
            logger.error(f"Error writing markdown to {output_path}: {e}")
            return False