"""
Shared prompt resources.

NOTE: Text prompt templates are now in domain config.yaml files:
- domains/materials/config.yaml → prompts.caption, prompts.faq, prompts.material_description
- domains/settings/config.yaml → prompts.component_summary_base, prompts.settings_description

The old TextPromptBuilder class was removed as it violated the Template-Only Policy
(hardcoded component configs in Python code instead of template files).
"""

# Personas are loaded from shared/prompts/personas/*.yaml
# by generation/core/generator.py

__all__ = []
