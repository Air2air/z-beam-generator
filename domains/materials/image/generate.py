#!/usr/bin/env python3
"""
Material Image Generator CLI

REFACTORED: This is now a thin wrapper for backward compatibility.
Core logic moved to:
  - pipeline.py: Generation pipeline (research, generate, validate, learn)
  - cli.py: Command-line interface

Usage:
    python3 domains/materials/image/generate.py --material "Aluminum"
    python3 domains/materials/image/generate.py --material "Stainless Steel"
    
For new code, prefer:
    python3 domains/materials/image/cli.py --material "Aluminum"
"""

import sys
from pathlib import Path

# Add project root to path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Backward compatibility: import and run cli.main()
from domains.materials.image.cli import main, parse_args

# Re-export pipeline components for existing imports
from domains.materials.image.pipeline import (
    GUIDANCE_SCALE_DEFAULT,
    PASS_THRESHOLD,
    GenerationResult,
    ImageGenerationPipeline,
    build_feedback_text,
    load_image_config,
    load_material_properties,
)

if __name__ == "__main__":
    main()
