# Shared Prompts

## Overview

This directory contains shared prompt resources used across the generation system.

## Consolidated Structure (Jan 13, 2026)

```
shared/prompts/
├── README.md           # This file
├── __init__.py         # Module exports
├── common/             # Common prompt templates (base versions) 🆕
│   ├── pageDescription_base.txt
│   ├── excerpt_base.txt
│   ├── faq_base.txt
│   └── micro_base.txt
└── personas/           # Author voice personas
    ├── indonesia.yaml
    ├── italy.yaml
    ├── taiwan.yaml
    └── united_states.yaml
```

## Common Templates 🆕

Templates appearing in 2+ domains are documented here as base versions:
- **pageDescription**: materials, contaminants, compounds, settings (4 domains)
- **excerpt**: DEPRECATED (was materials, contaminants, settings)  
- **faq**: materials, contaminants (2 domains)
- **micro**: materials, contaminants (2 domains)

Domain-specific files override these bases as needed.

## Author Personas

The `personas/` directory contains YAML files defining author voice characteristics:
- Linguistic patterns and cultural nuances
- Writing style preferences
- Regional expressions and idioms

These are loaded by `generation/core/generator.py` to add authentic voice variation.

## Domain Prompts (In config.yaml Files)

Text prompt templates are now in domain config.yaml files under `prompts:` key:

```
domains/materials/
├── config.yaml              # Contains prompts.micro, prompts.faq, prompts.description
└── prompts/personas/        # Author voice personas (materials-specific)

domains/settings/
├── config.yaml              # Contains prompts.component_summary_base, prompts.settings_description
└── config/
    └── component_summaries.yaml  # Component definitions (titles, descriptions)
```

This follows the **Template-Only Policy**: all content instructions exist in YAML template
files, not hardcoded in Python code.

## Current Architecture

The generation pipeline now uses:

1. **Domain prompt templates** (`prompts/{domain}/*.txt`) - Content instructions
2. **Humanness optimizer** (`learning/humanness_optimizer.py`) - Voice variation
3. **Single-pass generation** - No post-processing voice enhancement
4. **Direct save** - Content saved immediately to YAML files

## Migration Note (Dec 2025)

The old `text_prompt_builder.py` was removed because it:
1. Hardcoded component configs in Python (violates Template-Only Policy)
2. Used post-processor voice architecture (no longer used)
3. Was not imported by the main generation pipeline

The current architecture uses domain prompt templates loaded directly by generators.
