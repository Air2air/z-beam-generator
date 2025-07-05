# generator/modules/prompt_loader.py

import os
from typing import Dict
from generator.modules.logger import get_logger
from generator.config.settings import AppConfig

logger = get_logger("prompt_loader")
config = AppConfig()


class PromptLoader:
    def __init__(self, prompt_dir: str = None):
        # Use the provided directory or default to the one from settings
        self.prompt_dir = prompt_dir or str(config.directories.sections_dir)

    def load_all_templates(self) -> Dict[str, str]:
        prompt_templates = {}
        logger.info(f"Loading prompt templates from: {self.prompt_dir}")

        os.makedirs(self.prompt_dir, exist_ok=True)

        if not os.path.exists(self.prompt_dir):
            logger.error(
                f"Prompt directory not found after attempt to create: {self.prompt_dir}"
            )
            raise FileNotFoundError(f"Prompt directory not found: {self.prompt_dir}")

        try:
            for filename in os.listdir(self.prompt_dir):
                if filename.endswith(".txt"):
                    file_path = os.path.join(self.prompt_dir, filename)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            prompt_templates[filename] = f.read()
                        logger.debug(f"Loaded prompt: {filename}")
                    except IOError as e:
                        logger.warning(f"Could not read prompt file {filename}: {e}")
                    except Exception as e:
                        logger.error(
                            f"An unexpected error occurred reading prompt {filename}: {e}"
                        )
            logger.info(
                f"Successfully loaded {len(prompt_templates)} prompt templates."
            )
        except Exception as e:
            logger.critical(
                f"Failed to list or read files in prompt directory {self.prompt_dir}: {e}"
            )
            raise

        return prompt_templates
