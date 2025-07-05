#!/usr/bin/env python3
"""
Main entry point for the Z-Beam article generation system.
Handles configuration loading and orchestrates the generation process.
"""

import sys
import argparse
import os

# Setup paths for internal imports
import setup_paths

from modules.runner import ApplicationRunner
from config.configurator import build_run_config
from core.domain.models import TemperatureConfig


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Z-Beam Article Generation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 run.py                     # Normal article generation
  python3 run.py --test-detector     # Test detector improvements and optimization
        """,
    )

    # Test modes
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument(
        "--test-detector",
        action="store_true",
        help="Test detector improvements and prompt optimization (validate human-like output)",
    )

    return parser.parse_args()


def load_user_config():
    """Load user configuration from root run.py file."""
    try:
        # Add parent directory to path to import from root run.py
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, parent_dir)
        
        from run import USER_CONFIG, PROVIDER_MODELS
        
        # Initialize global config manager to prevent hardcoding
        from config.global_config import GlobalConfigManager
        global_config = GlobalConfigManager.initialize(USER_CONFIG)
        global_config.validate_thresholds()
        global_config.validate_temperatures()
        
        # Convert flat user config to proper structure with TemperatureConfig
        if isinstance(USER_CONFIG, dict):
            temp_config = global_config.get_temperature_config()
            
            # Convert to the expected format
            config = USER_CONFIG.copy()
            config["temperature_config"] = temp_config
            config["temperature"] = global_config.get_content_temperature()  # Legacy compatibility
            config["detection_temperature"] = global_config.get_detection_temperature()  # Legacy compatibility
            
            return config, PROVIDER_MODELS
        else:
            return USER_CONFIG, PROVIDER_MODELS
            
    except ImportError as e:
        print(f"❌ Could not load configuration from run.py: {e}")
        print("Make sure run.py exists in the project root with USER_CONFIG and PROVIDER_MODELS")
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    args = parse_arguments()
    
    # Load configuration from root run.py
    user_config, provider_models = load_user_config()
    
    # Make provider models available globally (for backward compatibility)
    globals()["PROVIDER_MODELS"] = provider_models

    # Handle test detector mode
    if args.test_detector:
        # Import test runner (only when needed)
        try:
            from test_runner import run_detector_validation_test

            print("🧪 Running Detector Improvement Test...")
            print("🎯 This will test the prompt optimization improvements")
            print(
                "   to ensure content reads as human-written without try-hard traits.\n"
            )

            # Run detector-focused test with optimized settings
            success = run_detector_validation_test()

            print(
                f"\n{'✅ Test completed successfully!' if success else '❌ Test failed or did not meet thresholds.'}"
            )
            sys.exit(0 if success else 1)

        except ImportError as e:
            print(f"❌ Test runner not available: {e}")
            print("Make sure test_runner.py is in the generator directory")
            sys.exit(1)

    # Normal article generation mode
    run_config = build_run_config(user_config)
    runner = ApplicationRunner()
    success = runner.run(run_config)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
