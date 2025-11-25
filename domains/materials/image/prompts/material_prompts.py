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
    # Load ultra-concise base template
    base_template = load_base_prompt_template()
    
    # Extract research data
    common_object = research_data.get('common_object', f'{material_name} object')
    environment = research_data.get('typical_environment', 'typical environment')
    
    # Build contamination details from category research patterns
    patterns = research_data.get('selected_patterns', research_data.get('contaminants', []))
    contamination_section = _build_concise_contamination_section(patterns)
    
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
    prompt = prompt.replace('{CONTAMINANTS_SECTION}', contamination_section)
    
    return prompt


def _build_concise_contamination_section(patterns: list) -> str:
    """Build concise contamination list from category research patterns."""
    if not patterns:
        raise ValueError("No contamination patterns provided. Research data is required.")
    
    lines = []
    for pattern in patterns[:4]:  # Max 4 patterns
        # Handle both old contaminant format and new pattern format
        if 'pattern_name' in pattern:
            name = pattern['pattern_name']
            visual = pattern.get('visual_characteristics', {})
            color = visual.get('color_range', 'varied tones')
            texture = visual.get('texture_detail', 'varied texture')
            lines.append(f"{name}: {color}, {texture}")
        else:
            name = pattern.get('name', 'contamination')
            appearance = pattern.get('appearance', {})
            color = appearance.get('color', 'dark')
            texture = appearance.get('texture', 'uneven')
            lines.append(f"{name}: {color}, {texture}")
    
    return ". ".join(lines) + "."


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
    
    lines.append("\n**REALISM IMPERATIVES** (CRITICAL - These determine image acceptability):")
    lines.append("- **Gravity compliance**: Liquids drip downward, heavy particles settle at bottom")
    lines.append("- **Layer interaction**: Contaminants overlap naturally, not as separate flat overlays")
    lines.append("- **Texture variation**: Each contaminant has distinct surface texture (matte dirt, glossy oil, granular rust)")
    lines.append("- **Light interaction**: Proper shadows, reflections, and light absorption for each material")
    lines.append("- **Uneven density**: Thicker in protected areas, thinner on exposed surfaces")
    lines.append("- **Weathering indicators**: Aged contamination shows fading, streaking, stratification")
    lines.append("- **NO uniform powders**: Avoid artificial-looking white/colored powder overlays")
    lines.append("- **NO perfect edges**: Contamination boundaries should be irregular and natural")
    lines.append("- **Reference reality**: Compare to actual photos of contaminated industrial materials")
    
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
