#!/usr/bin/env python3
"""
Material Before/After Image Prompts

Prompt generation for laser cleaning before/after images with scientifically
accurate contamination research and quality validation.

Author: AI Assistant  
Date: November 25, 2025
"""

from typing import Dict, List, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


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
    environment_wear: int = 3,
    validate: bool = True
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
        validate: Validate prompt before returning (default: True)
        
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
    
    # Validate prompt if requested
    if validate:
        validation_result = validate_prompt(prompt, research_data)
        if not validation_result['valid']:
            logger.warning(f"⚠️  Prompt validation issues detected:")
            for issue in validation_result['issues']:
                logger.warning(f"   • {issue}")
        
        if validation_result['warnings']:
            logger.info(f"ℹ️  Prompt validation warnings:")
            for warning in validation_result['warnings']:
                logger.info(f"   • {warning}")
        
        metrics = validation_result['metrics']
        logger.info(f"📊 Prompt metrics: {metrics['length']} chars, "
                   f"detail {metrics['detail_score']:.0f}/100, "
                   f"clarity {metrics['clarity_score']:.0f}/100, "
                   f"duplication {metrics['duplication_score']:.0f}/100")
    
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


# ============================================================================
# PROMPT VALIDATION SYSTEM
# ============================================================================

def validate_prompt(prompt: str, research_data: Dict) -> Dict[str, any]:
    """
    Validate prompt for Imagen 4 generation quality.
    
    Checks for:
    - Length optimization (1,000-2,000 chars ideal)
    - Detail sufficiency (contamination, aging, distribution)
    - Contradiction detection (physics violations)
    - Clarity (no vague/abstract terms)
    - Duplication (< 10% repeated content)
    
    Args:
        prompt: Generated prompt string
        research_data: Research data used to build prompt
        
    Returns:
        {
            "valid": bool,
            "issues": List[str],
            "warnings": List[str],
            "metrics": {
                "length": int,
                "detail_score": float,
                "clarity_score": float,
                "duplication_score": float
            }
        }
    """
    issues = []
    warnings = []
    
    # 1. Length validation
    length = len(prompt)
    if length > 3000:
        issues.append(f"Prompt too long ({length} chars). Exceeds Imagen 4 effective limit (3000).")
    elif length > 2500:
        warnings.append(f"Prompt lengthy ({length} chars). Consider condensing for clarity.")
    elif length < 800:
        warnings.append(f"Prompt short ({length} chars). May lack sufficient detail.")
    
    # 2. Detail score
    detail_score = _calculate_detail_score(prompt, research_data)
    if detail_score < 60:
        issues.append(f"Insufficient detail (score: {detail_score}/100). Minimum 60 required.")
    elif detail_score < 70:
        warnings.append(f"Low detail score ({detail_score}/100). Consider adding more specifics.")
    
    # 3. Contradiction detection
    contradictions = _detect_contradictions(prompt)
    if contradictions:
        for contradiction in contradictions:
            issues.append(f"Contradiction detected: {contradiction}")
    
    # 4. Clarity analysis
    clarity_issues, clarity_warnings = _analyze_clarity(prompt)
    issues.extend(clarity_issues)
    warnings.extend(clarity_warnings)
    
    # 5. Duplication detection
    duplication_percent = _detect_duplication(prompt)
    if duplication_percent > 20:
        issues.append(f"High duplication ({duplication_percent:.1f}%). Consolidate repeated content.")
    elif duplication_percent > 10:
        warnings.append(f"Moderate duplication ({duplication_percent:.1f}%). Consider consolidating.")
    
    clarity_score = 100.0 - (len(clarity_issues) * 25 + len(clarity_warnings) * 10)
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "metrics": {
            "length": length,
            "detail_score": detail_score,
            "clarity_score": max(0, clarity_score),
            "duplication_score": 100 - duplication_percent
        }
    }


def _calculate_detail_score(prompt: str, research_data: Dict) -> float:
    """Calculate prompt detail sufficiency score (0-100)."""
    score = 0.0
    prompt_lower = prompt.lower()
    
    # Contamination patterns described (+20)
    patterns = research_data.get('selected_patterns', research_data.get('contaminants', []))
    if len(patterns) >= 3:
        score += 20
    elif len(patterns) >= 2:
        score += 15
    elif len(patterns) >= 1:
        score += 10
    
    # Aging effects included (+15)
    aging_keywords = ['aging', 'weathering', 'degradation', 'uv', 'oxidation', 'corrosion']
    if any(kw in prompt_lower for kw in aging_keywords):
        score += 15
    
    # Distribution physics explained (+15)
    physics_keywords = ['gravity', 'drip', 'pool', 'accumulation', 'gradient', 'exposure']
    if any(kw in prompt_lower for kw in physics_keywords):
        score += 15
    
    # Micro-scale details (+10)
    micro_keywords = ['grain', 'edge', 'stress', 'porous', 'crevice', 'corner']
    if any(kw in prompt_lower for kw in micro_keywords):
        score += 10
    
    # Color specificity (+10)
    color_keywords = ['orange-brown', 'dark brown', 'silvery', 'gray', 'black', 'yellow', 'green']
    if any(kw in prompt_lower for kw in color_keywords):
        score += 10
    
    # Texture specificity (+10)
    texture_keywords = ['matte', 'glossy', 'granular', 'smooth', 'rough', 'chalky', 'flaky']
    if any(kw in prompt_lower for kw in texture_keywords):
        score += 10
    
    # Thickness variations (+10)
    thickness_keywords = ['thick', 'thin', 'layer', 'coating', 'film', 'buildup']
    if any(kw in prompt_lower for kw in thickness_keywords):
        score += 10
    
    # Environmental context (+10)
    env_keywords = ['environment', 'outdoor', 'indoor', 'industrial', 'moisture', 'uv']
    if any(kw in prompt_lower for kw in env_keywords):
        score += 10
    
    return min(score, 100.0)


def _detect_contradictions(prompt: str) -> List[str]:
    """Detect physics violations and logical contradictions."""
    contradictions = []
    prompt_lower = prompt.lower()
    
    # Physics violations
    if 'uniform' in prompt_lower and any(kw in prompt_lower for kw in ['drip', 'run', 'pool', 'gravity']):
        contradictions.append("'Uniform' contradicts gravity-driven distribution (drips/pools)")
    
    if 'symmetric' in prompt_lower and 'environment' in prompt_lower:
        contradictions.append("'Symmetric' contradicts environmental exposure gradients")
    
    if 'instant' in prompt_lower and 'aging' in prompt_lower:
        contradictions.append("'Instant' contradicts aging timeline progression")
    
    # Spatial inconsistencies
    if 'same object' in prompt_lower and 'different size' in prompt_lower:
        contradictions.append("'Same object' contradicts 'different size'")
    
    if 'identical position' in prompt_lower and 'shift' in prompt_lower:
        contradictions.append("'Identical position' contradicts 'shift' requirement")
    
    return contradictions


def _analyze_clarity(prompt: str) -> Tuple[List[str], List[str]]:
    """Analyze prompt clarity, return (issues, warnings)."""
    issues = []
    warnings = []
    prompt_lower = prompt.lower()
    
    # Vague terms (warnings)
    vague_terms = ['some', 'various', 'typical', 'normal', 'standard', 'average']
    found_vague = [term for term in vague_terms if term in prompt_lower]
    if found_vague:
        warnings.append(f"Vague terms detected: {', '.join(found_vague)}")
    
    # Abstract terms (issues - fail generation)
    abstract_terms = ['artistic', 'interesting', 'nice', 'beautiful', 'dramatic', 'creative']
    found_abstract = [term for term in abstract_terms if term in prompt_lower]
    if found_abstract:
        issues.append(f"Abstract terms detected: {', '.join(found_abstract)}")
    
    # Missing split definition (issue)
    if 'left' not in prompt_lower or 'right' not in prompt_lower:
        issues.append("Missing left/right split definition")
    
    # Missing contamination level (warning)
    if not any(str(i) in prompt for i in range(1, 6)):  # 1-5 scale
        warnings.append("No contamination level specified")
    
    return issues, warnings


def _detect_duplication(prompt: str) -> float:
    """Detect duplicate content, return percentage."""
    # Split into words
    words = prompt.lower().split()
    
    if len(words) == 0:
        return 0.0
    
    # Count word frequencies
    word_counts = {}
    for word in words:
        if len(word) > 3:  # Ignore short words
            word_counts[word] = word_counts.get(word, 0) + 1
    
    # Calculate duplication: (repeated_words / total_words) * 100
    repeated_words = sum(count - 1 for count in word_counts.values() if count > 1)
    duplication_percent = (repeated_words / len(words)) * 100
    
    return min(duplication_percent, 100.0)

