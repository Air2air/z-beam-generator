# generator/modules/file_handler.py

import os
import json
import re
from typing import Any

from generator.modules.logger import get_logger

logger = get_logger("generator.file_handler")


def save_file(file_path: str, content: str):
    """Saves content to a specified file path, creating directories if needed."""
    try:
        dir_name = os.path.dirname(file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.debug(f"File saved: {file_path}")
    except IOError as e:
        logger.error(f"Error saving file {file_path}: {e}")
        raise


def read_cache(cache_file_path: str) -> dict | None:
    """Reads and returns cached data from a JSON file."""
    if os.path.exists(cache_file_path):
        try:
            with open(cache_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.debug(f"Cache loaded from {cache_file_path}")
            return data
        except json.JSONDecodeError as e:
            logger.warning(
                f"Error decoding JSON from cache file {cache_file_path}: {e}"
            )
        except FileNotFoundError:
            logger.warning(f"Cache file not found: {cache_file_path}")
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while reading cache {cache_file_path}: {e}"
            )
    return None


def write_cache(cache_file_path: str, data: dict):
    """Writes data to a cache file in JSON format."""
    try:
        dir_name = os.path.dirname(cache_file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(cache_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.debug(f"Cache written to {cache_file_path}")
    except IOError as e:
        logger.error(f"Error writing cache to {cache_file_path}: {e}")
    except Exception as e:
        logger.error(
            f"An unexpected error occurred while writing cache {cache_file_path}: {e}"
        )


def parse_json_response(response_text: str, section_name: str, logger) -> Any | None:
    """
    Attempts to parse a JSON string from a larger text, often from an LLM response.
    Handles cases where the JSON is wrapped in markdown code blocks.
    """
    json_match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_str = response_text

    try:
        parsed_data = json.loads(json_str)
        logger.debug(f"Successfully parsed JSON for {section_name}.")
        return parsed_data
    except json.JSONDecodeError as e:
        logger.warning(
            f"Failed to decode JSON for {section_name}: {e}. Raw attempt: '{json_str[:200]}...'"
        )
        return None


def read_file_content(file_path: str) -> str | None:
    """Reads and returns the entire content of a text file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        logger.debug(f"File content read: {file_path}")
        return content
    except FileNotFoundError:
        logger.warning(f"File not found: {file_path}")
        return None
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None
