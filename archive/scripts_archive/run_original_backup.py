#!/usr/bin/env python3
"""
Z-Beam Generator - Main Interface

A comprehensive AI-powered content generation system for laser cleaning materials.

🚀 QUICK START SCRIPTS (User Commands):
========================================

BASIC GENERATION:
    python3 run.py                                    # Generate all materials (batch mode)
    python3 run.py --material "Steel"                 # Generate specific material
    python3 run.py --material "Aluminum" --author 2   # Generate with Italian author
    python3 run.py --interactive                      # Interactive mode with prompts
    python3 run.py --start-index 50                   # Start batch from material #50

COMPONENT CONTROL:
    python3 run.py --material "Copper" --components "frontmatter,content"  # Specific components only
    python3 run.py --list-components                  # Show all available components
    python3 run.py --show-config                     # Show component configuration

CONTENT MANAGEMENT:
    python3 run.py --clean                           # Remove all generated content files
    python3 run.py --yaml                            # Validate and fix YAML errors
    python3 run.py --cleanup-scan                    # Scan for cleanup opportunities
    python3 run.py --cleanup-report                  # Generate cleanup report
    python3 run.py --cleanup-root                    # Organize root directory files

SYSTEM INFO:
    python3 run.py --list-materials                  # List all 121 available materials
    python3 run.py --list-authors                    # List all authors with countries
    python3 run.py --check-env                       # Check API keys and environment
    python3 run.py --test-api                        # Test API connectivity
    python3 run.py --test                            # Run comprehensive test suite

MATERIAL MANAGEMENT (separate script):
    python3 remove_material.py --list-materials      # List all materials by category
    python3 remove_material.py --find-orphans        # Find orphaned files
    python3 remove_material.py --material "Material Name" --dry-run    # Test removal
    python3 remove_material.py --material "Material Name" --execute    # Remove material

PATH CLEANUP (one-time scripts):
    python3 cleanup_paths.py                         # Rename files to clean format (already done)

🔧 COMPONENT DATA SOURCE CONFIGURATION:
======================================

Component data sources are configured in: cli/component_config.py

DATA PROVIDER OPTIONS:
    "API"          - Generate content via AI API (deepseek, grok)
    "frontmatter"  - Extract data from frontmatter component
    "hybrid"       - Uses frontmatter data + API generation
    "none"         - Static component, no external data

API PROVIDER OPTIONS:
    "deepseek"     - DeepSeek API
    "grok"         - Grok (X.AI) API
    "none"         - No API needed

CURRENT CONFIGURATION:
    frontmatter:     API generation (grok)
    content:         hybrid (frontmatter + grok)
    bullets:         API generation (deepseek)
    caption:         API generation (deepseek)
    table:           API generation (grok)
    tags:            API generation (deepseek)
    jsonld:          Extract from frontmatter
    metatags:        Extract from frontmatter
    propertiestable: Extract from frontmatter
    badgesymbol:     Extract from frontmatter
    author:          Static component

TO MODIFY DATA SOURCES:
1. Edit cli/component_config.py
2. Change "data_provider" and/or "api_provider" for any component
3. Run: python3 run.py --show-config (to verify changes)

🎯 COMMON WORKFLOWS:
==================
1. Generate all content:           python3 run.py
2. Generate specific material:     python3 run.py --material "Steel"
3. Clean and regenerate:          python3 run.py --clean && python3 run.py
4. Check system health:           python3 run.py --check-env --show-config
5. Remove unwanted material:      python3 remove_material.py --material "Old Material" --execute

Features:
- Schema-driven content generation with JSON validation
- Multi-component orchestration (frontmatter, content, tags, etc.)
- Interactive and batch processing modes
- Multi-API provider support (DeepSeek, Grok)
- Component validation and autonomous fixing
- Progress tracking and resumption capabilities
- Clean slug generation for consistent file paths
"""

import argparse
import json
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from dotenv import load_dotenv

from api.client_manager import (
    API_PROVIDERS,
    COMPONENT_CONFIG,
    APIClient,
    CentralizedValidator,
    CleanupManager,
    ComponentResult,
    DynamicGenerator,
    EnvLoader,
    api.client,
    api.env_loader,
    check_environment,
    clean_content_components,
    cleanup.cleanup_manager,
    cli.api_config,
    cli.component_config,
    components.content.generators.fail_fast_generator,
)
from api.client_manager import create_api_client
from api.client_manager import create_api_client as cli_create_api_client
from api.client_manager import (
    create_filename_slug,
    create_material_slug,
    from,
    generators.dynamic_generator,
    generators.workflow_manager,
    get_author_by_id,
    import,
    list_authors,
    load_authors,
    save_component_to_file,
    show_component_configuration,
    traceback,
    traceback.print_exc,
    utils.author_manager,
    utils.environment_checker,
    utils.file_operations,
    utils.slug_utils,
    validators.centralized_validator,
)

        sys.exit(1)


if __name__ == "__main__":
    main()
