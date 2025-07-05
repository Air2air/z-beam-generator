"""
Configuration builder for the article generation system.
Handles dynamic config logic and ensures all required fields are set.
"""

import importlib.util
import os
from generator.modules.runner import RunConfiguration


def build_run_config(user_config: dict) -> RunConfiguration:
    config = dict(user_config)
    # Keep 'category' field for RunConfiguration (don't map to 'article_category')

    # Map natural_voice_threshold to human_detection_threshold for backward compatibility
    if (
        "natural_voice_threshold" in config
        and "human_detection_threshold" not in config
    ):
        config["human_detection_threshold"] = config["natural_voice_threshold"]
        # Remove the original key since RunConfiguration doesn't expect it
        del config["natural_voice_threshold"]

    # Dynamically import PROVIDER_MODELS from run.py to avoid circular imports
    try:
        # Get the path to run.py (assumed to be in the project root)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        run_path = os.path.join(project_root, "run.py")

        # Use spec-based loading to avoid circular imports
        spec = importlib.util.spec_from_file_location("run_module", run_path)
        run_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(run_module)

        # Get PROVIDER_MODELS from the imported module
        provider_models = getattr(run_module, "PROVIDER_MODELS", {})

        # Set model settings from the imported provider_models
        config["generator_model_settings"] = provider_models.get(
            config["generator_provider"], {}
        )
        config["detection_model_settings"] = provider_models.get(
            config["detection_provider"], {}
        )
    except (ImportError, AttributeError) as e:
        print(f"Warning: Could not import PROVIDER_MODELS from run.py: {e}")
        # Fallback to empty dictionaries if run.py can't be loaded
        config["generator_model_settings"] = {}
        config["detection_model_settings"] = {}
    # Set 'model' from generator_model_settings if not present
    if "model" not in config and config["generator_model_settings"]:
        config["model"] = config["generator_model_settings"].get("model")
    return RunConfiguration(**config)
