"""
Domain-specific SEO prompt templates optimized for user search intent.

Each domain has unique properties that users search for:
- Materials: reflectivity, damage risks, wavelength/power specs
- Contaminants: removal efficacy, safety, affected surfaces
- Settings: parameter ranges, success rates, troubleshooting
- Compounds: chemical hazards, safety protocols, exposure limits
"""

from typing import Dict


def _require_context_keys(context: Dict[str, str], keys: list[str], domain: str) -> None:
    missing = [key for key in keys if key not in context]
    if missing:
        raise KeyError(
            f"SEO prompt context for domain '{domain}' missing required keys: {', '.join(missing)}"
        )


def get_materials_prompt(context: Dict[str, str]) -> str:
    """
    Materials domain SEO prompt - User searches focus on:
    - "aluminum laser cleaning reflectivity"
    - "how to clean copper without damage"
    - "wavelength for [material] laser cleaning"
    - "power settings [material]"
    
    Highlights: Reflectivity%, absorption%, wavelength(nm), power(W), damage prevention
    """
    required_keys = [
        'material_name',
        'reflectivity',
        'absorption',
        'wavelength',
        'power_min',
        'power_max',
        'primary_challenge',
    ]
    _require_context_keys(context, required_keys, 'materials')

    return f"""Generate SEO metadata for laser cleaning of: {context['material_name']}

User Search Intent: Users search for "{context['material_name'].lower()} laser cleaning", "high reflectivity metal cleaning", "laser cleaning {context['material_name'].lower()} without damage", "wavelength for {context['material_name'].lower()}"

Technical Data:
• Reflectivity: {context['reflectivity']}% (affects laser effectiveness)
• Absorption: {context['absorption']}% (energy transfer rate)
• Optimal wavelength: {context['wavelength']}nm
• Power range: {context['power_min']}-{context['power_max']}W (prevents damage)
• Primary challenge: {context['primary_challenge']}

Create SEO that answers user questions:
1. page_title: "{context['material_name']}: [Key Technical Benefit] Laser Cleaning" (under 60 chars)
   - Include specific property (e.g., "High Reflectivity", "Damage-Free", "Precise Control")
   - Make it actionable and technical
   - MUST end with exactly "Laser Cleaning" (no additional suffixes like "| Z-Beam")

2. meta_description: (under 160 chars)
   - Start with "{context['material_name']} laser cleaning"
   - Include specific metrics (reflectivity%, absorption%, wavelength nm, power W)
   - Mention damage prevention/surface preservation
   - End with application benefit (restoration, manufacturing, maintenance)

Return ONLY JSON:
{{
  "page_title": "...",
  "meta_description": "..."
}}"""


def get_contaminants_prompt(context: Dict[str, str]) -> str:
    """
    Contaminants domain SEO prompt - User searches focus on:
    - "rust removal laser"
    - "oil cleaning industrial laser"
    - "paint stripping non-abrasive"
    - "how to remove [contaminant] laser"
    
    Highlights: Removal efficacy, surfaces affected, safety, alternative methods
    """
    required_keys = [
        'contaminant_name',
        'contaminant_type',
        'affected_materials',
        'removal_difficulty',
        'safety_notes',
        'alternatives',
    ]
    _require_context_keys(context, required_keys, 'contaminants')

    return f"""Generate SEO metadata for laser removal of: {context['contaminant_name']}

User Search Intent: Users search for "{context['contaminant_name'].lower()} removal laser", "laser cleaning {context['contaminant_name'].lower()}", "how to remove {context['contaminant_name'].lower()} laser", "industrial {context['contaminant_name'].lower()} cleaning"

Technical Data:
• Contaminant type: {context['contaminant_type']}
• Common on surfaces: {context['affected_materials']}
• Removal difficulty: {context['removal_difficulty']}
• Safety considerations: {context['safety_notes']}
• Alternative methods: {context['alternatives']}

Create SEO that answers user questions:
1. page_title: "{context['contaminant_name']}: [Key Benefit] Contaminants" (under 60 chars)
   - Include removal efficacy term (e.g., "Complete", "Precision", "Safe", "Non-Abrasive")
   - Make it solution-focused
   - MUST end with exactly "Contaminants"

2. meta_description: (under 160 chars)
   - Start with "{context['contaminant_name']} laser removal"
   - Mention affected surfaces/materials
   - Highlight key benefits (no chemicals, no damage, precise control)
   - Include safety aspect if relevant
   - End with application (industrial, restoration, maintenance)

Return ONLY JSON:
{{
  "page_title": "...",
  "meta_description": "..."
}}"""


def get_settings_prompt(context: Dict[str, str]) -> str:
    """
    Settings domain SEO prompt - User searches focus on:
    - "laser settings for aluminum"
    - "power range rust removal"
    - "wavelength for copper cleaning"
    - "optimal parameters [material] [contaminant]"
    
    Highlights: Parameter ranges (power, wavelength, frequency), success rates, troubleshooting
    """
    required_keys = [
        'setting_name',
        'material',
        'contaminant',
        'power_min',
        'power_max',
        'wavelength',
        'frequency',
        'challenges',
    ]
    _require_context_keys(context, required_keys, 'settings')

    return f"""Generate SEO metadata for laser cleaning settings: {context['setting_name']}

User Search Intent: Users search for "laser settings for {context['material']}", "power range {context['contaminant']} removal", "optimal parameters {context['material']}", "troubleshooting laser cleaning {context['material']}"

Technical Data:
• Material: {context['material']}
• Target contaminant: {context['contaminant']}
• Power range: {context['power_min']}-{context['power_max']}W
• Wavelength: {context['wavelength']}nm
• Pulse frequency: {context['frequency']}kHz
• Common challenges: {context['challenges']}

Create SEO that answers user questions:
1. page_title: "{context['setting_name']}: [Power/Wavelength] Settings" (under 60 chars)
   - Include specific parameter range (e.g., "100-300W", "1064nm")
   - Make it parameter-focused
   - MUST end with exactly "Settings"

2. meta_description: (under 160 chars)
   - Start with "{context['setting_name']} laser settings"
   - Include specific parameters (power W, wavelength nm, frequency kHz)
   - Mention material compatibility
   - Highlight outcome (prevents damage, optimal removal, surface preservation)
   - End with application context

Return ONLY JSON:
{{
  "page_title": "...",
  "meta_description": "..."
}}"""


def get_compounds_prompt(context: Dict[str, str]) -> str:
    """
    Compounds domain SEO prompt - User searches focus on:
    - "carbon monoxide laser cleaning hazards"
    - "VOC emissions laser safety"
    - "chemical exposure laser cleaning"
    - "toxic fumes laser ablation"
    
    Highlights: Chemical formula, hazard class, safety protocols, exposure limits
    """
    required_keys = [
        'compound_name',
        'chemical_formula',
        'cas_number',
        'hazard_class',
        'exposure_limit',
        'source',
        'safety_protocols',
    ]
    _require_context_keys(context, required_keys, 'compounds')

    return f"""Generate SEO metadata for compound exposure in laser cleaning: {context['compound_name']}

User Search Intent: Users search for "{context['compound_name'].lower()} laser cleaning hazards", "safety protocols {context['compound_name'].lower()}", "{context['compound_name'].lower()} exposure limits", "VOC emissions laser cleaning", "toxic fumes laser ablation"

Technical Data:
• Chemical formula: {context['chemical_formula']}
• CAS number: {context['cas_number']}
• Hazard class: {context['hazard_class']}
• Exposure limit: {context['exposure_limit']}
• Source: {context['source']}
• Safety protocols: {context['safety_protocols']}

Create SEO that answers user questions:
1. page_title: "{context['compound_name']}: [Safety/Hazard Term] Compound" (under 60 chars)
   - Include safety/hazard term (e.g., "Toxic Gas", "Exposure Risks", "Safety Protocols")
   - Make it safety-focused
   - MUST end with exactly "Compound"

2. meta_description: (under 160 chars)
    - Start with "{context['compound_name']} ({context['chemical_formula']})"
   - Mention hazard type (toxic gas, VOC, particulate)
   - Include safety requirements (ventilation, monitoring, PPE)
   - Highlight regulatory compliance (OSHA, EPA)
   - End with protective measures

Return ONLY JSON:
{{
  "page_title": "...",
  "meta_description": "..."
}}"""


def get_prompt_for_domain(domain: str, context: Dict[str, str]) -> str:
    """
    Get domain-specific SEO prompt based on user search intent research.
    
    Args:
        domain: 'materials', 'contaminants', 'settings', or 'compounds'
        context: Context data with domain-specific keys
    
    Returns:
        Formatted prompt string for SEO generation
        
    Raises:
        ValueError: If domain is not recognized
    """
    prompts = {
        'materials': get_materials_prompt,
        'contaminants': get_contaminants_prompt,
        'settings': get_settings_prompt,
        'compounds': get_compounds_prompt,
    }
    
    if domain not in prompts:
        raise ValueError(f"Unknown domain: {domain}. Must be one of {list(prompts.keys())}")
    
    return prompts[domain](context)
