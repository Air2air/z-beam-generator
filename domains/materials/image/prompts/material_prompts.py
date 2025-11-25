#!/usr/bin/env python3
"""
Material Before/After Image Prompts

Prompt generation for laser cleaning before/after images with scientifically
accurate contamination research.

Author: AI Assistant  
Date: November 24, 2025
"""

from typing import Dict, Optional
from pathlib import Path


def load_base_prompt_template() -> str:
    """Load the base prompt template from file."""
    template_path = Path(__file__).parent / "base_prompt.txt"
    
    if not template_path.exists():
        raise FileNotFoundError(f"Base prompt template not found: {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def build_material_cleaning_prompt(
    material_name: str,
    research_data: Dict,
    contamination_level: int = 3,
    contamination_uniformity: int = 3,
    view_mode: str = "Contextual",
    environment_wear: int = 3
) -> str:
    """
    Build complete image generation prompt for material laser cleaning.
    
    Args:
        material_name: Name of the material (e.g., "Aluminum", "Stainless Steel")
        research_data: Complete research data from MaterialContaminationResearcher
        contamination_level: Intensity 1-5 (default: 3)
        contamination_uniformity: Variety 1-5 (default: 3)
        view_mode: "Contextual" or "Isolated" (default: "Contextual")
        environment_wear: Background aging 1-5 (default: 3)
        
    Returns:
        Complete prompt string ready for Imagen 4
    """
    # Load base template
    base_template = load_base_prompt_template()
    
    # Extract research data
    common_object = research_data.get('common_object', f'{material_name} object')
    object_desc = research_data.get('object_description', '')
    typical_size = research_data.get('typical_size', 'standard size')
    environment = research_data.get('typical_environment', 'typical environment')
    env_desc = research_data.get('environment_description', '')
    
    # Build contamination details from research
    contaminants = research_data.get('contaminants', [])
    contamination_details = _build_contamination_section(contaminants, contamination_uniformity)
    
    # Build base material appearance
    base_appearance = research_data.get('base_material_appearance', {})
    material_details = _build_material_appearance_section(material_name, base_appearance)
    
    # Build complete prompt by replacing template variables
    prompt = base_template
    
    # Replace configuration variables
    prompt = prompt.replace('{MATERIAL}', material_name)
    prompt = prompt.replace('{COMMON_OBJECT}', common_object)
    prompt = prompt.replace('{ENVIRONMENT}', environment)
    prompt = prompt.replace('{CONTAMINATION_LEVEL}', str(contamination_level))
    prompt = prompt.replace('{UNIFORMITY}', str(contamination_uniformity))
    prompt = prompt.replace('{VIEW_MODE}', view_mode)
    prompt = prompt.replace('{ENVIRONMENT_WEAR}', str(environment_wear))
    
    # Add research-based content sections
    prompt += "\n\n" + "="*80
    prompt += "\n## RESEARCH-BASED SPECIFICATIONS\n"
    prompt += "="*80 + "\n\n"
    
    prompt += f"### Material: {material_name}\n"
    prompt += f"**Common Object**: {common_object}\n"
    prompt += f"**Description**: {object_desc}\n"
    prompt += f"**Typical Size**: {typical_size}\n\n"
    
    prompt += f"### Environment Context\n"
    prompt += f"**Environment**: {environment}\n"
    prompt += f"**Details**: {env_desc}\n\n"
    
    prompt += material_details + "\n\n"
    prompt += contamination_details + "\n\n"
    
    prompt += "### Generation Instructions\n"
    prompt += f"Create a 16:9 composite image showing {common_object} made from {material_name}:\n\n"
    prompt += "**LEFT SIDE (BEFORE CLEANING)**:\n"
    prompt += f"- Surface covered with researched contaminants (level {contamination_level}/5)\n"
    prompt += f"- {contamination_uniformity} types of contamination visible\n"
    prompt += f"- Darker overall tone due to contamination\n"
    prompt += f"- Object in {environment} context\n\n"
    
    prompt += "**RIGHT SIDE (AFTER LASER CLEANING)**:\n"
    prompt += f"- Clean {material_name} appearance fully visible\n"
    prompt += f"- Inverse residual contamination (level {5-contamination_level+1}/5 cleanliness)\n"
    prompt += f"- True material color and sheen restored\n"
    prompt += f"- Same object, same viewpoint, subtle position shift\n\n"
    
    prompt += f"**VIEW MODE**: {view_mode}\n"
    prompt += f"**ENVIRONMENT WEAR**: {environment_wear}/5\n"
    
    return prompt


def _build_contamination_section(contaminants: list, uniformity: int) -> str:
    """Build detailed contamination section from research data."""
    lines = []
    lines.append("### Scientifically Accurate Contaminants")
    lines.append(f"**Uniformity Level**: {uniformity}/5 (variety of contamination types)\n")
    
    # Select contaminants based on uniformity level
    num_contaminants = min(len(contaminants), uniformity + 1)
    selected = contaminants[:num_contaminants]
    
    for i, contam in enumerate(selected, 1):
        lines.append(f"**{i}. {contam['name']}**")
        if contam.get('chemical_formula'):
            lines.append(f"   - Formula: {contam['chemical_formula']}")
        lines.append(f"   - Cause: {contam['cause']}")
        lines.append(f"   - Color: {contam['appearance']['color']}")
        lines.append(f"   - Texture: {contam['appearance']['texture']}")
        lines.append(f"   - Pattern: {contam['appearance']['pattern']}")
        lines.append(f"   - Thickness: {contam['appearance']['thickness']}")
        lines.append(f"   - Prevalence: {contam['prevalence']}\n")
    
    lines.append("\n**CONTAMINATED STATE REQUIREMENTS**:")
    lines.append("- Apply ALL listed contaminants in natural, overlapping layers")
    lines.append("- Follow researched color, texture, and pattern specifications EXACTLY")
    lines.append("- Distribution should be uneven and realistic (heavier in crevices)")
    lines.append("- Overall darkening due to contamination light absorption")
    
    return "\n".join(lines)


def _build_material_appearance_section(material_name: str, base_appearance: Dict) -> str:
    """Build base material appearance section."""
    lines = []
    lines.append(f"### Base {material_name} Appearance (Clean State)")
    
    if base_appearance:
        lines.append(f"**Color**: {base_appearance.get('clean_color', 'natural color')}")
        lines.append(f"**Texture**: {base_appearance.get('clean_texture', 'natural texture')}")
        lines.append(f"**Sheen**: {base_appearance.get('clean_sheen', 'natural sheen')}")
        lines.append(f"**Natural Features**: {base_appearance.get('natural_features', 'typical features')}")
    else:
        lines.append(f"Use authentic {material_name} appearance when clean")
    
    lines.append("\n**CLEAN STATE REQUIREMENTS**:")
    lines.append("- Show true material color and texture")
    lines.append("- Maintain natural surface features and grain")
    lines.append("- Preserve permanent imperfections (light scratches, etc.)")
    lines.append("- Slight laser cleaning texture variation acceptable")
    
    return "\n".join(lines)
