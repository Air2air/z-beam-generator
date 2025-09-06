#!/usr/bin/env python3
"""
Z-Beam Generator - Main Interface (Cleaned)

A comprehensive AI-powered content generation system for laser cleaning materials.
"""

import argparse
import asyncio
import json
import logging
import os
import shutil
import sys
import time as time_module
from pathlib import Path

import yaml

from api.client_manager import get_api_client_for_component, test_api_connectivity
from components.text.generator import TextComponentGenerator
from generators.dynamic_generator import DynamicGenerator
from optimizer.optimization_orchestrator import ContentOptimizationOrchestrator
from utils.author_manager import get_author_by_id, list_authors
from utils.environment_checker import check_environment
from utils.file_operations import (
    clean_content_components,
    load_component_from_file,
    save_component_to_file,
    save_component_to_file_original,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import traceback

try:
    # Your main application code here
    pass
except Exception as e:
    logger.error(f"Application error: {e}")
    traceback.print_exc()
    sys.exit(1)


def main():
    """Main entry point for Z-Beam generator."""
    parser = argparse.ArgumentParser(description="Z-Beam Content Generator")

    # Basic arguments
    parser.add_argument(
        "--optimize", help="Optimize content for a component (e.g., 'text', 'bullets')"
    )
    parser.add_argument(
        "--material",
        help="Material name for optimization (optional - optimizes all if not specified)",
    )
    parser.add_argument("--component", help="Component type for optimization")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        if args.optimize:
            component_name = args.optimize
            print(f"🚀 Starting optimization for component: {component_name}")

            # Find all material files in the component directory
            component_dir = Path("content/components") / component_name
            if not component_dir.exists():
                print(f"❌ Component directory not found: {component_dir}")
                return

            # Get all .md files in the component directory
            material_files = list(component_dir.glob("*.md"))
            if not material_files:
                print(f"⚠️ No material files found in {component_dir}")
                return

            print(f"📂 Found {len(material_files)} material files to optimize")

            # Load content from each file
            materials_content = {}
            for file_path in material_files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Extract material name from filename (remove -laser-cleaning.md suffix)
                    material_name = file_path.stem.replace("-laser-cleaning", "")
                    materials_content[material_name] = content
                    print(f"   📄 Loaded {material_name} from {file_path.name}")

                except Exception as e:
                    print(f"❌ Error loading {file_path}: {e}")
                    continue

            if not materials_content:
                print("❌ No content loaded for optimization")
                return

            # Run batch optimization
            print(f"\n🔄 Optimizing {len(materials_content)} materials...")

            async def run_optimization():
                print("⚠️  Optimization services not fully configured yet")
                print("💡 This demonstrates the file processing functionality")

                # For now, just demonstrate that we can process the files
                successful_optimizations = 0
                for material_name, content in materials_content.items():
                    # Find the original file
                    original_file = component_dir / f"{material_name}-laser-cleaning.md"
                    if original_file.exists():
                        print(f"   📝 Would optimize {material_name} (file exists)")
                        successful_optimizations += 1
                    else:
                        print(f"   ⚠️ Original file not found for {material_name}")

                print(
                    f"\n🏁 File processing completed: {successful_optimizations}/{len(materials_content)} files found"
                )
                print("📊 Ready for optimization integration")

            # Run the async optimization
            asyncio.run(run_optimization())

        else:
            print("Z-Beam Generator")
            print("Use --optimize <component> to optimize content")
            print("Example: python3 run.py --optimize text")

    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
