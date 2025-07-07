"""
Simplified content generator following anti-bloat principles.
All configuration via GlobalConfigManager, no abstractions.
Includes MDX validation functionality and prompt management.
"""

import re
import os
import logging
import json
from typing import Dict, Any
from pathlib import Path
from config.global_config import GlobalConfigManager
from modules import api_client
from modules.api_client import get_logger  # Import the enhanced logger
import signal
from contextlib import contextmanager
from modules.optimization_orchestrator import OptimizationOrchestrator

logger = get_logger("content_generator")


# === PROMPT MANAGEMENT (merged from prompt_manager.py) ===

class PromptManager:
    """Centralized loader and cache for all prompt templates."""

    def __init__(self, base_dir: str = None):
        if base_dir:
            self.base_dir = base_dir
        else:
            # UPDATE: Changed from sections to prompts directory
            project_root = Path(__file__).parent.parent
            self.base_dir = str(project_root / "prompts")  # CHANGED FROM "sections" 
        self.cache: Dict[str, str] = {}

    def load_prompt(self, prompt_name: str, subdir: str = "") -> str:
        """Load a prompt template from file"""
        
        cache_key = f"{subdir}/{prompt_name}" if subdir else prompt_name
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Build file path - now looks in prompts directory
        if subdir:
            file_path = Path(self.base_dir) / subdir / f"{prompt_name}.txt"
        else:
            file_path = Path(self.base_dir) / f"{prompt_name}.txt"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read().strip()
            
            self.cache[cache_key] = prompt_content
            logger.info(f"📋 Loaded prompt: {cache_key}")
            return prompt_content
            
        except FileNotFoundError:
            logger.error(f"❌ Prompt file not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to load prompt {cache_key}: {e}")
            raise

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


def load_sections_from_json(config):
    """Load section configurations from JSON file"""
    
    # UPDATE PATH: Changed from sections/sections.json to prompts/sections.json
    sections_file = Path("prompts") / "sections.json"
    
    try:
        if not sections_file.exists():
            logger.error(f"❌ Sections file not found: {sections_file}")
            raise FileNotFoundError(f"Sections file not found: {sections_file}")
        
        with open(sections_file, 'r', encoding='utf-8') as f:
            sections_data = json.load(f)
        
        sections = sections_data.get('sections', [])
        
        if not sections:
            logger.error(f"❌ No sections found in {sections_file}")
            raise ValueError(f"No sections found in {sections_file}")
        
        # Sort sections by order
        sections.sort(key=lambda x: x.get('order', 999))
        
        logger.info(f"📋 Loaded {len(sections)} sections from prompts/sections.json")
        return sections
        
    except Exception as e:
        logger.error(f"❌ Failed to load sections from {sections_file}: {e}")
        raise


def check_api_health(provider, model, api_keys, base_url, temperature, max_tokens):
    """Check API health before starting generation - fail fast if issues exist"""
    logger.info(f"🔍 Checking API health for {provider}...")
    
    test_prompt = "Hello, this is a quick test. Please respond with 'API is working'."
    
    try:
        response = api_client.call_ai_api(
            prompt=test_prompt,
            provider=provider,
            model=model,
            api_keys=api_keys,
            temperature=temperature,
            max_tokens=50,  # Small response for quick test
            url_template=f"{base_url}/v1/chat/completions",
            backoff_factor=1.0  # No retry for health check
        )
        
        if response and response.strip():
            logger.info(f"✅ API health check passed for {provider}")
            return True
        else:
            logger.error(f"❌ API health check failed: Empty response from {provider}")
            return False
            
    except Exception as e:
        logger.error(f"❌ API health check failed for {provider}: {e}")
        return False


@contextmanager
def timeout_handler(seconds):
    """Context manager for timing out operations"""
    def timeout_signal(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")
    
    # Set the signal handler and alarm
    signal.signal(signal.SIGALRM, timeout_signal)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        # Disable the alarm
        signal.alarm(0)

def enhance_section_prompt_with_generation_requirements(section, material, config):
    """Enhance section prompt with generation enhancement requirements (order 0) - FULLY DYNAMIC"""
    
    # Load generation enhancement requirements dynamically
    generation_requirements = load_generation_enhancement_requirements()
    
    # Format base prompt
    base_prompt = section['prompt'].format(material=material)
    word_limit = config.get('default_section_words', 150)
    
    # Combine all elements
    enhanced_prompt = f"""{base_prompt}

{generation_requirements}

WORD LIMIT: Write approximately {word_limit} words maximum. Do not exceed this limit."""
    
    return enhanced_prompt

def load_generation_enhancement_requirements():
    """Load generation enhancement requirements (order 0) dynamically - NO HARDCODING"""
    
    with open("prompts/optimizations.json", 'r', encoding='utf-8') as f:
        optimizations_data = json.load(f)
    
    # FIND GENERATION ENHANCEMENT STEP DYNAMICALLY
    generation_step = None
    for key, config in optimizations_data.items():
        if (config.get('type') == 'generation_enhancement' and 
            config.get('order') == 0):
            generation_step = config
            break
    
    if not generation_step:
        logger.warning("⚠️ No generation enhancement step found (type='generation_enhancement', order=0)")
        return ""
    
    # USE 'requirements' FIELD FOR GENERATION ENHANCEMENT
    requirements = generation_step.get('requirements', '')
    if not requirements:
        logger.warning(f"⚠️ Generation enhancement step '{generation_step.get('name', 'unknown')}' has no 'requirements' field")
        return ""
    
    logger.info(f"📋 Loaded {generation_step.get('name', 'unknown')} v{generation_step.get('version', 'unversioned')} for generation")
    return requirements

def generate_content_for_material(material, provider, max_tokens, temperature):
    """Generate content with fully dynamic optimization pipeline - SUPPORTS MULTIPLE STEPS"""
    
    # Initialize config from GlobalConfigManager
    from config.global_config import GlobalConfigManager
    config = GlobalConfigManager.get_instance()
    
    # FAIL FAST - NO OUTER TRY/CATCH, LET ERRORS BUBBLE UP
    with timeout_handler(config.get('overall_timeout', 300)):
        # Load sections from JSON
        sections = load_sections_from_json(config)
        logger.info(f"📋 Loaded {len(sections)} sections for material: {material}")
        
        # Format API keys
        api_key_mappings = config.get("api_key_mappings", {})
        api_keys = {}
        for prov, env_var in api_key_mappings.items():
            import os
            key = os.getenv(env_var)
            if key:
                api_keys[env_var] = key
        
        if not api_keys:
            logger.error(f"❌ GENERATION FAILED: No API keys configured")
            raise RuntimeError("No API keys available for content generation")
        
        model = config.get_model()
        base_url = config.get_base_url()
        
        # HEALTH CHECK - FAIL FAST
        if not check_api_health(provider, model, api_keys, base_url, temperature, max_tokens):
            logger.error(f"❌ GENERATION FAILED: API health check failed for {provider}")
            raise RuntimeError(f"API health check failed for provider: {provider}")
        
        # Initialize orchestrator ONCE (auto-detects optimization steps)
        orchestrator = OptimizationOrchestrator(config)
        
        # Generate each section - FAIL ON ANY SECTION FAILURE
        full_content = f"# Laser Cleaning for {material}\n\n"
        
        for section in sections:
            logger.info(f"🔧 Generating section: {section['name']} ({section['title']})")
            
            # 1. CREATE SINGLE COMBINED PROMPT (Section + Generation Enhancement)
            combined_prompt = enhance_section_prompt_with_generation_requirements(section, material, config)
            
            # 2. SINGLE API CALL - GENERATES ENHANCED CONTENT DIRECTLY
            logger.info(f"📡 Making generation API call for section with enhancement requirements")
            
            enhanced_content = api_client.call_ai_api(
                prompt=combined_prompt,
                provider=provider,
                model=model,
                api_keys=api_keys,
                temperature=temperature,
                max_tokens=max_tokens,
                url_template=f"{base_url}/v1/chat/completions",
                backoff_factor=2.0
            )
            
            # STRICT VALIDATION - FAIL IF NO CONTENT
            if not enhanced_content or not enhanced_content.strip():
                logger.error(f"❌ GENERATION FAILED: Empty content for section '{section['name']}'")
                raise RuntimeError(f"Failed to generate content for section: {section['name']}")
            
            logger.info(f"✅ Generated {len(enhanced_content.split())} words for: {section['name']}")
            
            # 3. RUN OPTIMIZATION PIPELINE (automatically detects and runs ALL optimization steps)
            logger.info(f"🎯 Starting optimization pipeline for section: {section['name']}")
            
            optimized_content = orchestrator.optimize_section(
                content=enhanced_content,
                section_name=section['name'],
                section_type=section.get('type', section['title']),  # Use title as fallback
                material=material
            )
            
            logger.info(f"🎯 Optimization pipeline complete for section: {section['name']}")
            
            # 4. ADD TO ARTICLE
            word_count = len(optimized_content.strip().split())
            full_content += f"\n## {section['title']}\n\n{optimized_content.strip()}\n"
            logger.info(f"✅ Section complete: {word_count} words for '{section['name']}'")
        
        # FINAL VALIDATION
        total_words = len(full_content.strip().split())
        min_article_words = config.get('min_article_words', 100)
        if total_words < min_article_words:
            logger.error(f"❌ GENERATION FAILED: Article too short ({total_words} words, minimum {min_article_words})")
            raise RuntimeError(f"Generated article too short: {total_words} words")
        
        logger.info(f"✅ GENERATION SUCCESS: Complete article with {total_words} words")
        return full_content
