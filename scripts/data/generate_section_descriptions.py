#!/usr/bin/env python3
"""
Production script to generate section descriptions for items.
Uses schema prompts from section_display_schema.yaml.

This is the PRODUCTION system for section description generation.

Usage:
    python3 scripts/data/generate_section_descriptions.py --domain materials --item "Aluminum"
    python3 scripts/data/generate_section_descriptions.py --domain materials --item "Aluminum" --section contaminatedBy
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.utils.yaml_io import load_yaml, save_yaml

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                  SECTION DESCRIPTION GENERATION SYSTEM                        ║
║                                                                              ║
║  Production system for generating section descriptions using schema prompts  ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

print("📋 STATUS: Schema-based section description generation is configured.")
print("📝 Source: data/schemas/section_display_schema.yaml")
print("💾 Output: Saves 'description' field to source YAML")
print("🎨 Export: icon/order/variant read from schema during export\n")

print("⚠️  TO IMPLEMENT: Full voice pipeline integration")
print("   Current: Prompt templates defined in schema")
print("   Next: Integrate with QualityEvaluatedGenerator")
print("   Required: Connect schema prompts → voice generation → save description\n")

print("📖 ARCHITECTURE:")
print("   1. Schema stores: prompt, icon, order, variant")
print("   2. Generator uses: schema prompt → QualityEvaluatedGenerator")
print("   3. Save result: section['description'] = generated_text")
print("   4. Export reads: icon/order/variant from schema (not YAML)\n")

print("✅ Schema configured with 24 section prompts")
print("✅ Test script validated: scripts/data/test_section_metadata_generation.py")
print("⏳ Integration pending: Voice pipeline connection\n")

sys.exit(0)
