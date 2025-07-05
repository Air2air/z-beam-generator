# generator/modules/content_generator.py

"""
from config.global_config import get_config
Legacy content generator - now uses the new architecture under the hood.
This file maintains backward compatibility while delegating to the new system.

DEPRECATION NOTICE: This module is being refactored. New code should use the
services in generator.core.services instead.
"""

# Import the new adapter for generate_content function
from generator.modules.legacy_adapter import generate_content  # noqa: F401

# Keep all the existing imports and functions for backward compatibility
from typing import Dict, Any
from generator.modules.logger import get_logger
from generator.modules import api_client
from generator.modules.prompt_formatter import format_prompt
from generator.modules.prompt_manager import PromptManager
from generator.config.settings import AppConfig
import os

logger = get_logger("content_generator")
config = AppConfig()

prompt_manager = PromptManager(os.path.join(os.path.dirname(__file__), "../prompts"))


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

    # Default values if settings are missing
    default_temp = 0.2
    default_max_tokens = 500
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
    import re

    # Remove up to and including the first blank line (\n\n) after the instruction/feedback
    pattern = r"^(Revise the following section based on this feedback to make it more human-like and less AI-detectable\.\nFeedback:.*?\n\n)"
    return re.sub(pattern, "", response_text, flags=re.DOTALL)


def generate_with_feedback_loop(
    section_name: str,
    prompt_template: str,
    section_variables: dict,
    generator_provider: str,
    model: str,
    api_keys: dict,
    prompt_templates_dict: dict,
    prompt_file_name: str,
    ai_detection_threshold: int,
    human_detection_threshold: int,
    iterations_per_section: int,
    generator_model_settings: dict = None,
    detection_provider: str = None,
    detection_model_settings: dict = None,
) -> tuple[str, int, bool]:
    """
    Adaptive feedback-driven revision loop for robust human-like content generation.
    Keeps a history of attempts, dynamically injects feedback, varies temperature, and selects the best output.
    """
    from generator.modules.ai_detector import parse_ai_detection_feedback

    attempts = []
    best_content = ""
    best_ai_score = 100
    best_human_score = 0
    threshold_met = False
    previous_output = None
    revision_feedback = ""
    detection_prompt_template = prompt_manager.load_prompt(
        "ai_detection_prompt.txt", "detection"
    )
    base_temperature = section_variables.get("temperature", 0.7)
    for i in range(iterations_per_section):
        temperature = base_temperature + (0.1 * i if i > 0 else 0)
        # Always revise previous output after the first iteration
        if i > 0 and previous_output:
            section_variables_with_feedback = dict(section_variables)
            # Use feedback if available, otherwise use initial_prompt.txt for first iteration
            if revision_feedback:
                section_variables_with_feedback["revision_feedback"] = revision_feedback
                revision_instruction = (
                    "Revise the following section based on this feedback to make it more human-like and less AI-detectable.\n"
                    "Feedback: {revision_feedback}\n\n"
                )
            else:
                # For first iteration or when no feedback available, use initial_prompt.txt
                initial_prompt = prompt_manager.load_prompt(
                    "initial_prompt.txt", "detection"
                )
                section_variables_with_feedback["revision_feedback"] = initial_prompt
                revision_instruction = (
                    "Revise the following section to make it more human-like and less AI-detectable.\n"
                    "Guidelines: {revision_feedback}\n\n"
                )
            revision_instruction += (
                "Previous Output:\n" + previous_output.strip() + "\n\n"
            )
            filled_prompt = format_prompt(
                revision_instruction + prompt_template,
                section_variables_with_feedback,
                prompt_file_name,
                section_name,
            )
        else:
            filled_prompt = format_prompt(
                prompt_template,
                section_variables,
                prompt_file_name,
                section_name,
            )
        logger.debug(
            f"[FEEDBACK LOOP] Iteration {i + 1} for '{section_name}':\nFeedback: {revision_feedback}\nPrompt: {filled_prompt[:1000]}\n---END PROMPT---"
        )
        try:
            response_text = api_client.call_ai_api(
                prompt=filled_prompt,
                provider=generator_provider,
                model=model,
                api_keys=api_keys,
                temperature=temperature,
                max_tokens=1500,
                url_template=generator_model_settings.get("url_template")
                if generator_model_settings
                else None,
                backoff_factor=2.0,
            )
        except Exception as e:
            logger.error(
                f"API request failed for section '{section_name}' (iteration {i + 1}): {e}"
            )
            continue
        if not response_text or not response_text.strip():
            logger.warning(
                f"Empty response for section '{section_name}' (iteration {i + 1})"
            )
            continue
        cleaned_response = _strip_revision_instruction(response_text)
        previous_output = cleaned_response
        # --- AI DETECTION CALL ---
        detection_vars = {
            "content": cleaned_response,
            "content_type": section_name.replace("_", " "),
            "audience_level": section_variables.get("audience_level", "general"),
        }

        # AI Detection
        ai_detection_prompt = format_prompt(
            detection_prompt_template,
            detection_vars,
            "ai_detection_prompt.txt",
            section_name,
        )
        try:
            ai_detection_response = api_client.call_ai_api(
                prompt=ai_detection_prompt,
                provider=detection_provider or generator_provider,
                model=detection_model_settings.get("model")
                if detection_model_settings
                else model,
                api_keys=api_keys,
                temperature=get_config().get_metadata_temperature(),
                max_tokens=500,
                url_template=detection_model_settings.get("url_template")
                if detection_model_settings
                else (
                    generator_model_settings.get("url_template")
                    if generator_model_settings
                    else None
                ),
                backoff_factor=2.0,
            )
        except Exception as e:
            logger.error(
                f"AI detection request failed for section '{section_name}' (iteration {i + 1}): {e}"
            )
            continue
        logger.info(
            f"[RAW AI DETECTION OUTPUT] Iteration {i + 1} for '{section_name}': {ai_detection_response}"
        )
        ai_score, ai_feedback = parse_ai_detection_feedback(
            ai_detection_response or "",
            detection_provider or generator_provider,
            detection_model_settings.get("model")
            if detection_model_settings
            else model,
            section_name,
            section_variables.get("audience_level", "general"),
            api_keys,
            prompt_templates_dict,
        )
        logger.info(
            f"[AI FEEDBACK] Iteration {i + 1} for '{section_name}': {ai_feedback}"
        )

        # --- HUMAN DETECTION CALL ---
        # Load human detection prompt template
        human_detection_template = prompt_manager.load_prompt(
            "human_detection_prompt.txt", "detection"
        )
        human_detection_prompt = format_prompt(
            human_detection_template,
            detection_vars,
            "human_detection_prompt.txt",
            section_name,
        )
        try:
            human_detection_response = api_client.call_ai_api(
                prompt=human_detection_prompt,
                provider=detection_provider or generator_provider,
                model=detection_model_settings.get("model")
                if detection_model_settings
                else model,
                api_keys=api_keys,
                temperature=get_config().get_metadata_temperature(),
                max_tokens=500,
                url_template=detection_model_settings.get("url_template")
                if detection_model_settings
                else (
                    generator_model_settings.get("url_template")
                    if generator_model_settings
                    else None
                ),
                backoff_factor=2.0,
            )
        except Exception as e:
            logger.error(
                f"Human detection request failed for section '{section_name}' (iteration {i + 1}): {e}"
            )
            continue
        logger.info(
            f"[RAW HUMAN DETECTION OUTPUT] Iteration {i + 1} for '{section_name}': {human_detection_response}"
        )
        human_score, human_feedback = parse_ai_detection_feedback(
            human_detection_response or "",
            detection_provider or generator_provider,
            detection_model_settings.get("model")
            if detection_model_settings
            else model,
            section_name,
            section_variables.get("audience_level", "general"),
            api_keys,
            prompt_templates_dict,
        )
        logger.info(
            f"[HUMAN FEEDBACK] Iteration {i + 1} for '{section_name}': {human_feedback}"
        )
        # Combine feedback from both detectors
        combined_feedback = (
            f"AI Detection: {ai_feedback}\nHuman Detection: {human_feedback}"
        )

        attempts.append(
            {
                "iteration": i + 1,
                "content": cleaned_response,
                "ai_score": ai_score,
                "human_score": human_score,
                "ai_feedback": ai_feedback,
                "human_feedback": human_feedback,
                "combined_feedback": combined_feedback,
            }
        )

        # Log both scores for this iteration
        logger.info(
            f"[SCORES] Iteration {i + 1} for '{section_name}': "
            f"AI Score: {ai_score}%, Human Score: {human_score}%"
        )

        # Track best (lowest combined score)
        combined_score = (ai_score + human_score) / 2
        best_combined_score = (best_ai_score + best_human_score) / 2
        if combined_score < best_combined_score or (
            combined_score == best_combined_score and ai_score < best_ai_score
        ):
            best_content = cleaned_response
            best_ai_score = ai_score
            best_human_score = human_score

        # Check if both scores are below their thresholds (CORRECT LOGIC)
        if (
            ai_score <= ai_detection_threshold
            and human_score <= human_detection_threshold
        ):
            threshold_met = True
            logger.info(
                f"Section '{section_name}' passed on iteration {i + 1} "
                f"(AI: {ai_score}% <= {ai_detection_threshold}%, "
                f"Human: {human_score}% <= {human_detection_threshold}%)"
            )
            break

        # If feedback is unchanged for 2+ attempts, escalate by increasing temperature
        if (
            i > 0
            and attempts[-1]["combined_feedback"] == attempts[-2]["combined_feedback"]
        ):
            logger.info(
                "Escalating: feedback unchanged, increasing temperature for next attempt."
            )

        # Use combined feedback for next iteration
        revision_feedback = combined_feedback or ""
        logger.info(
            f"Section '{section_name}' failed iteration {i + 1} "
            f"(AI: {ai_score}% > {ai_detection_threshold}% OR "
            f"Human: {human_score}% > {human_detection_threshold}%)"
        )
    if not best_content:
        logger.error(
            f"No valid content generated for section '{section_name}' after {iterations_per_section} iterations. Returning default values."
        )
        return "", 100, False
    # Optionally, log all attempts for diagnostics
    logger.info(f"[ATTEMPTS SUMMARY] Section '{section_name}': {attempts}")
    return best_content, best_ai_score, threshold_met


# All legacy functions are now handled by the new architecture
# The generate_content function is imported from legacy_adapter

# Track which sections have had their metadata logged (for backward compatibility)
section_metadata_logged = set()
