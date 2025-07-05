# modules/ai_detector.py

import json
import re
from typing import Dict, Any, Tuple
from datetime import datetime
import logging
from config.global_config import get_config

from modules.logger import get_logger
from modules import api_client
from modules.prompt_formatter import format_prompt
from config.settings import AppConfig

logger = get_logger("ai_detector")
config = AppConfig()


def research_material_config(
    material: str,
    provider: str,
    model: str,
    api_keys: Dict[str, str],
    prompt_templates_dict: Dict[str, str],
) -> Dict[str, Any] | None:
    logger.info(
        f"Researching material config for: {material} (provider: {provider}, model: {model})"
    )
    prompt_file_name = "material_research.txt"
    prompt_template = prompt_templates_dict.get(prompt_file_name)
    if not prompt_template:
        logger.error(
            f"Material research prompt template '{prompt_file_name}' not found in loaded templates."
        )
        return None

    filled_prompt = format_prompt(
        prompt_template,
        {"material": material},
        prompt_file_name,
        "material_config_research",
    )

    api_config = {
        "temperature": 0.2,
        "max_output_tokens": 500,
    }

    try:
        response_text = api_client.call_ai_api(
            prompt=filled_prompt,
            provider=provider,
            model=model,
            api_keys=api_keys,
            temperature=api_config["temperature"],
            max_tokens=api_config["max_output_tokens"],
        )
        if response_text:
            material_data = {}
            lines = response_text.strip().split("\n")
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    material_data[key.strip()] = value.strip()
            return material_data
        else:
            logger.warning(
                f"No response text received for material research on '{material}'."
            )
            return None
    except Exception as e:
        logger.error(f"API request failed for material research ({provider}): {e}")
        raise


def generate_content(
    section_name: str,
    prompt_template: str,
    section_variables: Dict[str, Any],
    article_data: Dict[str, Any],
    cache_data: Dict[str, Any],
    provider: str,
    model: str,
    force_regenerate: bool,
    api_keys: Dict[str, str],
    prompt_templates_dict: Dict[str, str],
    prompt_file_name: str,
) -> str:
    cache_key = f"{section_name}_{json.dumps(section_variables, sort_keys=True)}"

    if not force_regenerate and cache_key in cache_data.get("sections", {}):
        cached_content = cache_data["sections"][cache_key].get("content")
        if cached_content:
            logger.info(f"Returning cached content for section: {section_name}")
            return cached_content
        else:
            logger.warning(
                f"Cached content for section '{section_name}' was empty. Regenerating."
            )

    filled_prompt = format_prompt(
        prompt_template, section_variables, prompt_file_name, section_name
    )

    api_config = {
        "temperature": 0.7,
        "max_output_tokens": 1000,
    }

    content_length_hint = section_variables.get(
        "content_length", config.content.default_content_lengths
    )
    section_length_str = content_length_hint.get(
        section_name
    ) or content_length_hint.get("paragraph")
    if section_length_str:
        match = re.search(r"(\d+)-(\d+)", section_length_str)
        if match:
            max_words = int(match.group(2))
            # Use config for max article words instead of hardcoded value
            from config.global_config import get_config
            min_tokens = get_config().get_max_article_words() // 3  # Rough estimate: 3 words per token
            api_config["max_output_tokens"] = max(min_tokens, max_words * 2)

    try:
        response_text = api_client.call_ai_api(
            prompt=filled_prompt,
            provider=provider,
            model=model,
            api_keys=api_keys,
            temperature=api_config["temperature"],
            max_tokens=api_config["max_output_tokens"],
        )
        logger.debug(
            f"AI Response for section '{section_name}': {response_text[:500] if response_text else 'EMPTY'}..."
        )

        if not response_text:
            logger.warning(f"AI returned empty response for section: {section_name}")
            return ""

        content_type = section_name.replace("_", " ")
        ai_likelihood = _evaluate_human_likeness(
            response_text,
            provider,
            model,
            content_type,
            None,  # No audience_level/authority
            api_keys,
            prompt_templates_dict,
        )
        logger.info(f"AI Likelihood for '{section_name}': {ai_likelihood}%")

        if ai_likelihood > config.content.ai_detection_threshold:
            logger.warning(
                f"Content for '{section_name}' is too AI-like ({ai_likelihood}%). Attempting to regenerate..."
            )
            response_text_retry = api_client.call_ai_api(
                prompt=filled_prompt,
                provider=provider,
                model=model,
                api_keys=api_keys,
                temperature=api_config["temperature"],
                max_tokens=api_config["max_output_tokens"],
            )
            if response_text_retry:
                ai_likelihood_retry = _evaluate_human_likeness(
                    response_text_retry,
                    provider,
                    model,
                    content_type,
                    None,  # No audience_level/authority
                    api_keys,
                    prompt_templates_dict,
                )
                logger.info(
                    f"Retry AI Likelihood for '{section_name}': {ai_likelihood_retry}%"
                )
                if ai_likelihood_retry <= config.content.ai_detection_threshold:
                    response_text = response_text_retry
                    ai_likelihood = ai_likelihood_retry
                    logger.info(f"Regeneration successful for '{section_name}'.")
                else:
                    logger.warning(
                        f"Regenerated content for '{section_name}' is still too AI-like. Using first attempt."
                    )
            else:
                logger.warning(
                    f"Regeneration attempt for '{section_name}' failed to get a response. Using first attempt."
                )

        logger.info(
            f"[AI DETECTOR] Starting incremental human-likeness improvement for section: {section_name}"
        )
        improved_content, final_score = evaluate_human_likeness_incremental(
            response_text,
            provider,
            model,
            content_type,
            None,  # No audience_level/authority
            api_keys,
            prompt_templates_dict,
            max_attempts=5,
            threshold=config.content.ai_detection_threshold,
        )
        logger.info(
            f"[AI DETECTOR] Section '{section_name}' final AI-likeness score: {final_score}%\n---\n{improved_content[:300]}\n---"
        )

        if final_score <= config.content.ai_detection_threshold:
            logger.info(
                f"Content for '{section_name}' improved to acceptable AI-likeness level ({final_score}%)."
            )
            response_text = improved_content
        else:
            logger.warning(
                f"Content for '{section_name}' still too AI-like after regeneration ({final_score}%)."
            )

        if "sections" not in cache_data:
            cache_data["sections"] = {}
        cache_data["sections"][cache_key] = {
            "content": response_text,
            "ai_likelihood": ai_likelihood,
            "timestamp": datetime.now().isoformat(),
        }

        return response_text

    except Exception as e:
        logger.error(f"Error calling AI for section '{section_name}': {e}")
        return ""


def _evaluate_human_likeness(
    content: str,
    provider: str,
    model: str,
    content_type: str,
    audience_level: str,
    api_keys: Dict[str, str],
    prompt_templates_dict: Dict[str, str],
) -> int:
    prompt_file_name = "ai_detection_prompt.txt"
    prompt_template = prompt_templates_dict.get(prompt_file_name)

    if not prompt_template:
        logger.error(
            f"AI detection prompt template '{prompt_file_name}' not found in loaded templates."
        )
        return 0

    filled_prompt = format_prompt(
        prompt_template,
        {
            "content": content,
            "content_type": content_type,
            "audience_level": audience_level,
        },
        prompt_file_name,
        "ai_likeness_evaluation",
    )

    api_config = {
        "temperature": 0.0,
        "max_output_tokens": 50,
    }

    try:
        response = api_client.call_ai_api(
            prompt=filled_prompt,
            provider=provider,
            model=model,
            api_keys=api_keys,
            temperature=api_config["temperature"],
            max_tokens=api_config["max_output_tokens"],
        )
        logger.debug(
            f"AI Detection Response: {response[:100] if response else 'EMPTY'}..."
        )
        if response:
            # Try strict match first
            match = re.search(r"Percentage:\s*(\d+)%", response, re.IGNORECASE)
            if match:
                return int(match.group(1))
            # Try to find a number 0-100 in the first 3 lines
            lines = response.splitlines()
            for line in lines[:3]:
                num_match = re.search(r"(\d{1,3})\s*%?", line)
                if num_match:
                    val = int(num_match.group(1))
                    if 0 <= val <= 100:
                        return val
            # Try to find any number 0-100 in the whole response
            num_match = re.search(r"(\d{1,3})\s*%", response)
            if num_match:
                val = int(num_match.group(1))
                if 0 <= val <= 100:
                    return val
            logger.warning(
                f"Could not robustly parse AI likelihood percentage from response: '{response[:100]}...'"
            )
            return 100
        else:
            logger.warning("AI detection model returned empty response.")
            return 100
    except Exception as e:
        logger.error(f"Error calling AI for human-likeness evaluation: {e}")
        return 100


def evaluate_human_likeness_incremental(
    content: str,
    provider: str,
    model: str,
    content_type: str,
    audience_level: str,
    api_keys: dict,
    prompt_templates_dict: dict,
    max_attempts: int = 5,
    threshold: int = None,
    section_name: str = None,
) -> tuple[str, int]:
    """
    Iteratively improve content to lower AI-likeness using feedback and prompt variation.
    Returns (final_content, ai_likeness_score)
    """
    # Set threshold from config if not provided
    if threshold is None:
        from config.global_config import get_config
        threshold = get_config().get_ai_detection_threshold()
    logger = get_logger("ai_detector", context=section_name)
    prompt_file_name = "ai_detection_prompt.txt"
    prompt_template = prompt_templates_dict.get(
        f"detection/{prompt_file_name}"
    ) or prompt_templates_dict.get(prompt_file_name)
    logger.log_with_context(
        logging.INFO, f"Starting AI-likeness detection for section '{section_name}'"
    )
    if not prompt_template:
        logger.log_with_context(
            logging.ERROR,
            f"AI detector prompt template '{prompt_file_name}' not found in loaded templates.",
        )
        return content, 100
    last_content = content
    last_score = 100
    for attempt in range(max_attempts):
        feedback = ""
        if attempt > 0:
            feedback = (
                f"\n\nPrevious output (AI-likeness: {last_score}%):\n{last_content}\n"
                "Please revise the above to reduce the AI-likeness score, using the criteria and guidance in this prompt."
            )
        filled_prompt = format_prompt(
            prompt_template,
            {
                "content": last_content,
                "content_type": content_type,
                "audience_level": audience_level,
                "feedback": feedback,
            },
            prompt_file_name,
            "ai_likeness_evaluation",
        )
        try:
            # Use config for temperature instead of hardcoded value
            from config.global_config import get_config
            detection_temp = get_config().get_detection_temperature()
            
            response = api_client.call_ai_api(
                prompt=filled_prompt,
                provider=provider,
                model=model,
                api_keys=api_keys,
                temperature=detection_temp,
                max_tokens=get_config().get_max_tiny_response_tokens(),
            )
            if response:
                match = re.search(r"Percentage:\s*(\d+)%", response)
                if match:
                    score = int(match.group(1))
                    logger.log_with_context(
                        logging.INFO,
                        f"Iteration {attempt + 1}: AI-likeness score = {score}%",
                    )
                    logger.log_with_context(
                        logging.DEBUG, f"---OUTPUT---\n{response[:300]}\n---END---"
                    )
                    if score <= threshold:
                        logger.log_with_context(
                            logging.INFO,
                            f"Section '{section_name}' passed with score: {score}% after {attempt + 1} iterations.",
                        )
                        return response, score
                    last_score = score
                    last_content = response
                else:
                    logger.log_with_context(
                        logging.WARNING,
                        f"Could not parse AI likelihood percentage from response: '{response[:100]}...'",
                    )
            else:
                logger.log_with_context(
                    logging.WARNING, "AI detection model returned empty response."
                )
        except Exception as e:
            logger.log_with_context(
                logging.ERROR,
                f"Error calling AI for human-likeness evaluation (Attempt {attempt + 1}): {e}",
            )
        regenerated = api_client.regenerate_content(
            last_content,
            provider,
            model,
            api_keys,
            prompt_templates_dict,
            section_name="ai_likeness_evaluation",
        )
        if regenerated == last_content:
            logger.log_with_context(
                logging.WARNING,
                f"No change in regenerated content at attempt {attempt + 1}. Breaking loop.",
            )
            break
        last_content = regenerated
    logger.log_with_context(
        logging.ERROR,
        f"Max attempts reached. Section '{section_name}' did not pass. Final score: {last_score}%",
    )
    return last_content, last_score


def parse_ai_detection_feedback(
    content: str,
    provider: str,
    model: str,
    section_name: str,
    audience_level: str,
    api_keys: dict,
    prompt_templates_dict: dict,
) -> tuple[int, str]:
    """
    Parse the AI detection output to extract both the percentage score and revision feedback (summary/examples).
    Returns (score, feedback_text).
    """
    # Try to extract percentage as before
    match = re.search(r"Percentage:\s*(\d+)%", content, re.IGNORECASE)
    if match:
        score = int(match.group(1))
    else:
        # Fallback: look for any number 0-100 in first 3 lines
        lines = content.splitlines()
        score = 100
        for line in lines[:3]:
            num_match = re.search(r"(\d{1,3})\s*%?", line)
            if num_match:
                val = int(num_match.group(1))
                if 0 <= val <= 100:
                    score = val
                    break
    # Extract feedback: summary and examples if present
    summary = ""
    examples = ""
    summary_match = re.search(r"Summary:\s*(.*)", content, re.IGNORECASE)
    if summary_match:
        summary = summary_match.group(1).strip()
    examples_match = re.search(r"Examples.*?:\s*(.*)", content, re.IGNORECASE)
    if examples_match:
        examples = examples_match.group(1).strip()
    feedback = summary
    if examples:
        feedback += " Examples: " + examples
    return score, feedback
