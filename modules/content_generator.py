"""
Simplified content generator following anti-bloat principles.
All configuration via GlobalConfigManager, no abstractions.
Includes MDX validation functionality and prompt management.
"""

import re, os, logging
from typing import Dict, Any
from pathlib import Path
from config.global_config import GlobalConfigManager
from modules import api_client

# === SIMPLE LOGGING (inlined from utils.py) ===
def get_logger(name: str):
    """Simple logger setup - replaces entire logger.py module."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

logger = get_logger("content_generator")


# === PROMPT MANAGEMENT (merged from prompt_manager.py) ===

class PromptManager:
    """Centralized loader and cache for all prompt templates."""

    def __init__(self, base_dir: str = None):
        if base_dir:
            self.base_dir = base_dir
        else:
            # Default to sections directory relative to project root
            project_root = Path(__file__).parent.parent
            self.base_dir = str(project_root / "sections")
        self.cache: Dict[str, str] = {}

    def load_prompt(self, prompt_name: str, subdir: str = "") -> str:
        key = f"{subdir}/{prompt_name}" if subdir else prompt_name
        if key in self.cache:
            return self.cache[key]
        path = (
            os.path.join(self.base_dir, subdir, prompt_name)
            if subdir
            else os.path.join(self.base_dir, prompt_name)
        )
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                self.cache[key] = content
                return content
        except Exception as e:
            logger.error(f"Prompt not found: {path} ({e})")
            raise FileNotFoundError(f"Prompt not found: {path} ({e})")

    def load_all_prompts(self, subdir: str = "") -> Dict[str, str]:
        dir_path = os.path.join(self.base_dir, subdir) if subdir else self.base_dir
        prompt_templates = {}
        logger.info(f"Loading prompt templates from: {dir_path}")

        os.makedirs(dir_path, exist_ok=True)

        if not os.path.exists(dir_path):
            logger.error(f"Prompt directory not found after attempt to create: {dir_path}")
            raise FileNotFoundError(f"Prompt directory not found: {dir_path}")

        try:
            for filename in os.listdir(dir_path):
                if filename.endswith(".txt"):
                    file_path = os.path.join(dir_path, filename)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            prompt_templates[filename] = content
                            self.cache[filename] = content  # Add to cache
                        logger.debug(f"Loaded prompt: {filename}")
                    except IOError as e:
                        logger.warning(f"Could not read prompt file {filename}: {e}")
                    except Exception as e:
                        logger.error(f"An unexpected error occurred reading prompt {filename}: {e}")
            logger.info(f"Successfully loaded {len(prompt_templates)} prompt templates.")
        except Exception as e:
            logger.critical(f"Failed to list or read files in prompt directory {dir_path}: {e}")
            raise

        return prompt_templates


# Initialize global prompt manager
prompt_manager = PromptManager(os.path.join(os.path.dirname(__file__), "../prompts"))


# === MDX VALIDATION FUNCTIONS (merged from mdx_validator.py) ===

def validate_mdx_output(content: str) -> str:
    """
    Simplified MDX validation - fixes most common issues without over-engineering.
    Returns cleaned content ready for Next.js.
    """
    if not content:
        return content
    
    # Fix the most critical MDX parsing issues
    fixed = content
    
    # Fix HTML entities in tags (e.g., <td&gt; -> <td>&gt;)
    fixed = re.sub(r"<([a-zA-Z][a-zA-Z0-9]*)((?:&[a-zA-Z0-9]+;|&#[0-9]+;|&#x[0-9a-fA-F]+;))", r"<\1>\2", fixed)
    
    # Fix comparison operators with numbers
    fixed = re.sub(r"<(\d+\.?\d*)", r"&lt;\1", fixed)
    fixed = re.sub(r">(\d+\.?\d*)", r"&gt;\1", fixed)
    fixed = re.sub(r"<=(\d+\.?\d*)", r"&le;\1", fixed)
    fixed = re.sub(r">=(\d+\.?\d*)", r"&ge;\1", fixed)
    
    # Fix unescaped ampersands
    fixed = re.sub(r"&(?![a-zA-Z0-9#]+;)", r"&amp;", fixed)
    
    # Fix basic YAML frontmatter issues
    if fixed.startswith("---"):
        parts = fixed.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            # Fix malformed quotes in YAML
            frontmatter = re.sub(r'^\s*-\s*"-\s*"([^"]+)""', r'  - "\1"', frontmatter, flags=re.MULTILINE)
            fixed = f"---{frontmatter}---{parts[2]}"
    
    return fixed


# === PROMPT FORMATTING ===

def format_prompt(prompt, format_vars, prompt_file, section_name):
    """Format prompt, handle missing variables with strict placeholder validation.

    Args:
        prompt (str): Raw prompt text.
        format_vars (dict): Variables to insert into the prompt.
        prompt_file (str): Path to the prompt file.
        section_name (str): Name of the section.

    Returns:
        str: Formatted prompt.
    """
    # Match placeholders outside JSON example blocks
    placeholders = re.findall(r"\{(\w+)\}(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", prompt)
    missing_vars = [var for var in placeholders if var not in format_vars]
    try:
        if missing_vars:
            logger.warning(
                f"Prompt {prompt_file} has undefined variables {missing_vars}. Using manual replacement."
            )
            formatted = prompt
            for key, value in format_vars.items():
                formatted = formatted.replace(f"{{{key}}}", str(value))
        else:
            logger.debug(f"Raw prompt for {section_name}: {prompt[:500]}...")
            formatted = prompt.format(**format_vars)
            logger.debug(f"Formatted prompt for {section_name}: {formatted[:500]}...")
        return formatted
    except KeyError as e:
        logger.warning(
            f"Warning: Prompt {prompt_file} has undefined variable {e}. Using manual replacement."
        )
        formatted = prompt
        for key, value in format_vars.items():
            formatted = formatted.replace(f"{{{key}}}", str(value))
        logger.debug(
            f"Manually formatted prompt for {section_name}: {formatted[:500]}..."
        )
        return formatted


def load_rewrite_prompt():
    try:
        prompt = prompt_manager.load_prompt("rewrite_humanize_prompt.txt", "detection")
        if not prompt:
            logger.warning(
                "rewrite_humanize_prompt.txt not found or empty in detection prompts."
            )
        return prompt
    except Exception as e:
        logger.error(f"Failed to load rewrite prompt: {e}")
        return None


def research_material_config(
    material: str,
    generator_provider: str,
    model: str,
    api_keys: Dict[str, str],
    prompt_templates_dict: Dict[str, str],
    generator_model_settings: dict = None,
) -> Dict[str, Any] | None:
    logger.info(
        f"Researching material config for: {material} (generator_provider: {generator_provider}, model: {model})"
    )
    prompt_file_name = "material_research.txt"
    prompt_template = prompt_templates_dict.get(prompt_file_name)
    if not prompt_template:
        logger.error(
            f"Material research prompt template '{prompt_file_name}' not found in loaded templates."
        )
        return None
    if not prompt_template.strip():
        logger.error(
            f"Material research prompt template '{prompt_file_name}' is empty."
        )
        return None

    filled_prompt = format_prompt(
        prompt_template,
        {"material": material},
        prompt_file_name,
        "material_config_research",
    )

    # Default values if settings are missing - now using config
    config = GlobalConfigManager.get_instance()
    default_temp = config.get_content_temperature()
    default_max_tokens = config.get_max_content_tokens()
    default_url = None

    # Safe extraction of settings with defaults
    api_config = {
        "temperature": generator_model_settings.get("default_temperature", default_temp)
        if generator_model_settings
        else default_temp,
        "max_output_tokens": generator_model_settings.get(
            "default_max_tokens", default_max_tokens
        )
        if generator_model_settings
        else default_max_tokens,
        "url_template": generator_model_settings.get("url_template", default_url)
        if generator_model_settings
        else default_url,
    }

    try:
        response_text = api_client.call_ai_api(
            prompt=filled_prompt,
            provider=generator_provider,
            model=model,
            api_keys=api_keys,
            temperature=api_config["temperature"],
            max_tokens=api_config["max_output_tokens"],
            url_template=api_config["url_template"],
            backoff_factor=2.0,
        )
        logger.debug(
            f"Raw AI response for material research on '{material}': {response_text}"
        )
        if response_text:
            material_data = {}
            lines = response_text.strip().split("\n")
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    # Parse comma-separated fields as lists
                    if key in ["keywords", "industries", "applications"]:
                        material_data[key] = [
                            v.strip() for v in value.split(",") if v.strip()
                        ]
                    else:
                        material_data[key] = value
            # Map legacy/alternate keys to expected ones for metadata
            if "material_type" in material_data:
                material_data["materialType"] = material_data.pop("material_type")
            if "metal_class" in material_data:
                material_data["metalClass"] = material_data.pop("metal_class")
            if "primary_application" in material_data:
                material_data["primaryApplication"] = material_data.pop(
                    "primary_application"
                )
            if "material_description" in material_data:
                if "material_details" not in material_data:
                    material_data["material_details"] = {}
                material_data["material_details"]["material_description"] = (
                    material_data.pop("material_description")
                )
            if "applications" in material_data:
                if "material_details" not in material_data:
                    material_data["material_details"] = {}
                material_data["material_details"]["applications"] = material_data[
                    "applications"
                ]
            if not material_data:
                logger.warning(
                    f"Parsed material_data is empty for '{material}'. Raw response: {response_text}"
                )
            return material_data
        else:
            logger.warning(
                f"No response text received for material research on '{material}'."
            )
            return None
    except Exception as e:
        logger.error(
            f"API request failed for material research ({generator_provider}): {e}"
        )
        raise


def _strip_revision_instruction(response_text: str) -> str:
    """
    Remove the prepended revision instruction and feedback from the model's response, if present.
    """
    # Remove up to and including the first blank line (\n\n) after the instruction/feedback
    pattern = r"^(Revise the following section based on this feedback to make it more human-like and less AI-detectable\.\nFeedback:.*?\n\n)"
    return re.sub(pattern, "", response_text, flags=re.DOTALL)


def generate_content(
    section_name: str,
    prompt_template: str,
    section_variables: dict,
    generator_provider: str,
    model: str,
    api_keys: dict,
    generator_model_settings: dict = None,
) -> str:
    """
    Single-pass, template-driven content generation for a section.
    No feedback loop, no dynamic optimization, no fallbacks.
    Strictly uses centralized config for all parameters.
    """
    logger.info(f"Generating content for section: {section_name}")
    filled_prompt = format_prompt(
        prompt_template,
        section_variables,
        f"{section_name}.txt",
        section_name,
    )
    # Centralized config
    config = GlobalConfigManager.get_instance()
    temperature = config.get_content_temperature()
    max_tokens = config.get_max_content_tokens()
    url_template = None
    if generator_model_settings:
        url_template = generator_model_settings.get("url_template")
    try:
        response_text = api_client.call_ai_api(
            prompt=filled_prompt,
            provider=generator_provider,
            model=model,
            api_keys=api_keys,
            temperature=temperature,
            max_tokens=max_tokens,
            url_template=url_template,
            backoff_factor=2.0,
        )
        if not response_text or not response_text.strip():
            logger.warning(f"Empty response for section '{section_name}'")
            return ""
        return response_text.strip()
    except Exception as e:
        logger.error(f"API request failed for section '{section_name}': {e}")
        return ""


def generate_content_for_material(material: str, provider: str, max_tokens: int, temperature: float) -> str:
    """
    Simplified content generation function for the main interface.
    Generates content for a material using the specified provider and settings.
    """
    try:
        # Get configuration 
        config_manager = GlobalConfigManager()
        api_keys = config_manager.get_api_keys()
        
        # Load prompt template for the material
        prompt_template = prompt_manager.load_prompt("prompt_material.txt")
        if not prompt_template:
            logger.error("No prompt template found for material generation")
            return ""
        
        # Create section variables for the material
        section_variables = {
            "material": material,
            "provider": provider,
            "max_words": "1200",  # Default word count
            "category": "metals"  # Default category, could be made configurable
        }
        
        # Set up generator model settings
        generator_model_settings = {
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # Generate content using the existing function
        content = generate_content(
            section_name="material_content",
            prompt_template=prompt_template,
            section_variables=section_variables,
            generator_provider=provider,
            model=config_manager.get_generator_model(),
            api_keys=api_keys,
            generator_model_settings=generator_model_settings
        )
        
        return content
        
    except Exception as e:
        logger.error(f"Content generation failed for material {material}: {e}")
        return ""


# Remove the entire feedback loop and related legacy logic
def generate_with_feedback_loop(*args, **kwargs):
    raise NotImplementedError("Iterative feedback loop is deprecated. Use generate_content for single-pass generation.")

# All legacy functions are now handled by the new architecture
# The generate_content function is imported from legacy_adapter

# Track which sections have had their metadata logged (for backward compatibility)
section_metadata_logged = set()
