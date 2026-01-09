"""
Domain-specific SEO prompt templates optimized for user search intent.

Each domain has unique properties that users search for:
- Materials: reflectivity, damage risks, wavelength/power specs
- Contaminants: removal efficacy, safety, affected surfaces
- Settings: parameter ranges, success rates, troubleshooting
- Compounds: chemical hazards, safety protocols, exposure limits
"""

from typing import Dict


def get_materials_prompt(context: Dict[str, str]) -> str:
    """
    Materials domain SEO prompt - User searches focus on:
    - "aluminum laser cleaning reflectivity"
    - "how to clean copper without damage"
    - "wavelength for [material] laser cleaning"
    - "power settings [material]"
    
    Highlights: Reflectivity%, absorption%, wavelength(nm), power(W), damage prevention
    """
    return f"""Generate SEO metadata for laser cleaning of: {context['material_name']}

User Search Intent: Users search for "{context['material_name'].lower()} laser cleaning", "high reflectivity metal cleaning", "laser cleaning {context['material_name'].lower()} without damage", "wavelength for {context['material_name'].lower()}"

Technical Data:
• Reflectivity: {context.get('reflectivity', 'N/A')}% (affects laser effectiveness)
• Absorption: {context.get('absorption', 'N/A')}% (energy transfer rate)
• Optimal wavelength: {context.get('wavelength', 'N/A')}nm
• Power range: {context.get('power_min', 'N/A')}-{context.get('power_max', 'N/A')}W (prevents damage)
• Primary challenge: {context.get('primary_challenge', 'N/A')}

Create SEO that answers user questions:
1. page_title: "{context['material_name']}: [Key Technical Benefit] Laser Cleaning" (under 60 chars)
   - Include specific property (e.g., "High Reflectivity", "Damage-Free", "Precise Control")
   - Make it actionable and technical

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
    return f"""Generate SEO metadata for laser removal of: {context['contaminant_name']}

User Search Intent: Users search for "{context['contaminant_name'].lower()} removal laser", "laser cleaning {context['contaminant_name'].lower()}", "how to remove {context['contaminant_name'].lower()} laser", "industrial {context['contaminant_name'].lower()} cleaning"

Technical Data:
• Contaminant type: {context.get('contaminant_type', 'N/A')}
• Common on surfaces: {context.get('affected_materials', 'Various metals and substrates')}
• Removal difficulty: {context.get('removal_difficulty', 'Moderate to challenging')}
• Safety considerations: {context.get('safety_notes', 'Standard laser safety protocols')}
• Alternative methods: {context.get('alternatives', 'Chemical, abrasive, thermal')}

Create SEO that answers user questions:
1. page_title: "{context['contaminant_name']} Laser Removal: [Key Benefit]" (under 60 chars)
   - Include removal efficacy term (e.g., "Complete", "Precision", "Safe", "Non-Abrasive")
   - Make it solution-focused

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
    return f"""Generate SEO metadata for laser cleaning settings: {context['setting_name']}

User Search Intent: Users search for "laser settings for {context.get('material', 'materials')}", "power range {context.get('contaminant', 'contaminant')} removal", "optimal parameters {context.get('material', 'material')}", "troubleshooting laser cleaning {context.get('material', 'material')}"

Technical Data:
• Material: {context.get('material', 'N/A')}
• Target contaminant: {context.get('contaminant', 'Various')}
• Power range: {context.get('power_min', 'N/A')}-{context.get('power_max', 'N/A')}W
• Wavelength: {context.get('wavelength', 'N/A')}nm
• Pulse frequency: {context.get('frequency', 'N/A')}kHz
• Common challenges: {context.get('challenges', 'Parameter optimization')}

Create SEO that answers user questions:
1. page_title: "{context['setting_name']}: [Power/Wavelength] Laser Settings" (under 60 chars)
   - Include specific parameter range (e.g., "100-300W", "1064nm")
   - Make it parameter-focused

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
    return f"""Generate SEO metadata for compound exposure in laser cleaning: {context['compound_name']}

User Search Intent: Users search for "{context['compound_name'].lower()} laser cleaning hazards", "safety protocols {context['compound_name'].lower()}", "{context['compound_name'].lower()} exposure limits", "VOC emissions laser cleaning", "toxic fumes laser ablation"

Technical Data:
• Chemical formula: {context.get('chemical_formula', 'N/A')}
• CAS number: {context.get('cas_number', 'N/A')}
• Hazard class: {context.get('hazard_class', 'Industrial chemical')}
• Exposure limit: {context.get('exposure_limit', 'OSHA guidelines')}
• Source: {context.get('source', 'Material ablation byproduct')}
• Safety protocols: {context.get('safety_protocols', 'Ventilation and monitoring required')}

Create SEO that answers user questions:
1. page_title: "{context['compound_name']}: [Safety/Hazard Term] Laser Cleaning" (under 60 chars)
   - Include safety/hazard term (e.g., "Toxic Gas", "Exposure Risks", "Safety Protocols")
   - Make it safety-focused

2. meta_description: (under 160 chars)
   - Start with "{context['compound_name']} ({context.get('chemical_formula', '')})"
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
        context: Domain-specific context data
    
    Returns:
        Optimized prompt string for that domain
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
