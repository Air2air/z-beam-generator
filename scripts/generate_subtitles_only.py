#!/usr/bin/env python3
"""
Generate ONLY subtitles for all materials by updating existing frontmatter files.
Fast and focused - no caption/application regeneration.
"""

import yaml
from pathlib import Path
from api.client_factory import create_api_client
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def generate_subtitle(api_client, material_name: str, category: str, subcategory: str, material_data: dict) -> str:
    """Generate AI-powered subtitle for a material"""
    from utils.core.author_manager import get_author_by_id
    
    # Extract context
    applications = material_data.get('applications', [])[:3]
    properties = material_data.get('materialProperties', {})
    
    # Build property summary
    property_summary = []
    for prop, data in list(properties.items())[:5]:
        if isinstance(data, dict) and 'value' in data:
            unit = data.get('unit', '')
            property_summary.append(f"{prop}: {data['value']}{unit}")
    
    property_context = '; '.join(property_summary) if property_summary else 'Properties vary'
    apps_context = ', '.join(applications[:3]) if applications else 'General cleaning applications'
    
    # Get author information for voice profile
    author_id = None
    if 'author' in material_data and isinstance(material_data['author'], dict) and 'id' in material_data['author']:
        author_id = material_data['author']['id']
    elif 'author_id' in material_data:
        author_id = material_data['author_id']
    else:
        author_id = 3  # Default author
    
    author_info = get_author_by_id(author_id)
    if not author_info:
        raise ValueError(f"Author with ID {author_id} not found")
    
    # Load author voice profile
    country = author_info.get('country', 'United States')
    # Map country to voice profile file
    country_mapping = {
        'Taiwan': 'taiwan',
        'Italy': 'italy',
        'Indonesia': 'indonesia',
        'United States': 'united_states',
        'United States (California)': 'united_states'
    }
    profile_name = country_mapping.get(country, 'united_states')
    voice_file = Path(f"voice/profiles/{profile_name}.yaml")
    
    # Load voice profile
    voice_profile = {}
    if voice_file.exists():
        with open(voice_file, 'r') as f:
            voice_profile = yaml.safe_load(f)
    
    # Extract linguistic characteristics for prompt
    linguistic = voice_profile.get('linguistic_characteristics', {})
    sentence_structure = linguistic.get('sentence_structure', {})
    patterns = sentence_structure.get('patterns', [])
    tendencies = sentence_structure.get('tendencies', [])
    grammar = linguistic.get('grammar_characteristics', {})
    common_patterns = grammar.get('common_patterns', [])
    
    # Build author voice guidance (SUBTLE - don't dominate the output)
    author_voice = f"""
SUBTLE AUTHOR INFLUENCE (let personality show naturally, don't force patterns):
Author: {author_info['name']} from {country}
Voice hints: {', '.join(tendencies[:2]) if tendencies else 'Direct technical writing'}
"""
    
    # Build AI prompt that forces structural variation and human-like writing
    prompt = f"""You are writing subtitle copy for laser cleaning technical documentation. Generate a natural, conversational two-sentence subtitle about {material_name} that passes AI detection.

{author_voice}

CRITICAL: DO NOT USE REPETITIVE PATTERNS! Each subtitle must have a COMPLETELY UNIQUE structure.
BANNED: "What strikes me about...", "This [Material]...", any formulaic openings you've used before.
TONE: Professional technical writing - NO overly familiar expressions like "Hey!", "Wow!", or emotional exclamations.

MATERIAL CONTEXT:
- Material: {material_name}
- Category: {category}
- Subcategory: {subcategory}
- Properties: {property_context}
- Applications: {apps_context}

CRITICAL ANTI-AI-DETECTION REQUIREMENTS:

1. BANNED PHRASES & STRUCTURES (never use any of these):
   - "X is defined by..." / "X is characterized by..." / "X is known for..."
   - "stands out" / "sets apart" / "distinguishes"
   - "necessitates" / "requires" / "demands" + "precise/careful/tailored"
   - "When cleaning [Material], the surface..." (overused opening)
   - "dial in" / "dialed-in" (overused jargon)
   - "keep/keeping the [x] intact" (too common)
   - "calls for close attention" (AI favorite)
   - "well-tuned parameters" (AI favorite)

2. REQUIRED: Use COMPLETELY DIFFERENT sentence structures. Pick ONE (never repeat):
   
   A. Problem-first: "The biggest challenge with [material] is..."
   B. Behavior-first: "[Material] tends to react unpredictably when..."
   C. Property-leads: "Its [property] creates complications during..."
   D. Comparison: "Unlike [similar materials], [material] responds..."
   E. Operator perspective: "Most operators find [material] tricky because..."
   F. Timing-based: "During initial treatment, [material] often..."
   G. Conditional: "If power levels drift above X watts, [material]..."
   H. Consequence: "Skip proper calibration and [material] will..."
   I. Question-implied: "Why does [material] need special attention? Its..."
   J. Discovery: "Look at [material] under magnification and you'll spot..."
   K. Measurement-first: "At roughness levels exceeding X µm, [material]..."
   L. Process-flow: "Start with low power on [material], then gradually..."
   M. Contrast-within: "While the [part A] remains stable, [material's part B]..."
   N. User-instruction: "Keep your laser focused when treating [material] - its..."
   O. Observation: "Notice how [material] shifts color as contamination lifts..."
   P. Technical fact: "With thermal conductivity of X, [material] distributes..."
   Q. Industry-specific: "In aerospace applications, [material] demands..."
   R. Caution-first: "Watch out for [material's tendency] during..."
   S. Benefit-angle: "The advantage of [material] is its ability to..."
   T. Historical/Practical: "Operators have learned that [material] works best when..."3. VOCABULARY VARIATION - use fresh phrasing:
   - For "precise": specific, exact, targeted, controlled, focused
   - For "settings": controls, parameters, adjustments, power levels, conditions
   - For "avoid damage": prevent harm, protect, preserve, maintain, safeguard
   - For "surface": coating, layer, finish, skin, face
   - For "cleaning": treatment, processing, work, operation, removal

4. WRITE WITH PERSONALITY (match author voice above):
   - Use active, concrete verbs
   - Include occasional contractions (it's, won't, can't)
   - Add specifics (numbers, measurements, observations)
   - Vary rhythm (short + long sentence, or long + short)
   - Let expertise show through word choice

TARGET: 25-40 words, two sentences, completely unique structure from previous subtitles.

Generate the subtitle now:"""

    try:
        # Call API
        response = api_client.generate_simple(
            prompt=prompt,
            max_tokens=150,
            temperature=0.75  # Higher for more variety (was 0.6)
        )
        
        # Extract content
        if hasattr(response, 'content'):
            subtitle = response.content.strip()
        elif isinstance(response, str):
            subtitle = response.strip()
        else:
            subtitle = str(response).strip()
        
        # Clean up formatting
        subtitle = subtitle.replace('**', '').replace('*', '').strip()
        
        return subtitle
        
    except Exception as e:
        raise Exception(f"Subtitle generation failed: {e}")


def update_subtitle_in_yaml(file_path: Path, new_subtitle: str):
    """Update only the subtitle field in an existing YAML file"""
    
    # Read existing file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Parse YAML
    data = yaml.safe_load(content)
    
    # Update subtitle
    data['subtitle'] = new_subtitle
    
    # Write back
    with open(file_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def main():
    # Load Materials.yaml
    materials_path = Path("data/Materials.yaml")
    with open(materials_path, 'r') as f:
        materials_data = yaml.safe_load(f)
    
    material_index = materials_data.get('material_index', {})
    materials = sorted(material_index.keys())
    
    logger.info(f"🚀 Starting SUBTITLE-ONLY generation for {len(materials)} materials")
    logger.info("=" * 70)
    logger.info("⚡ Fast mode: Only updating subtitle field (no caption/application regen)")
    logger.info("=" * 70)
    
    # Initialize API client
    api_client = create_api_client('grok')
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    start_time = time.time()
    
    for i, material_name in enumerate(materials, 1):
        try:
            # Get material data
            material_entry = material_index[material_name]
            
            # Handle different material_index formats
            if isinstance(material_entry, dict):
                material_data = material_entry
            else:
                # Material index just has material names as strings
                # Load from Materials.yaml materials section
                material_data = materials_data.get('materials', {}).get(material_name, {})
            
            # Get category/subcategory
            category = material_data.get('category', 'material') if isinstance(material_data, dict) else 'material'
            subcategory = material_data.get('subcategory', 'general') if isinstance(material_data, dict) else 'general'
            
            # Find existing frontmatter file
            file_name = f"{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml"
            file_path = Path(f"content/components/frontmatter/{file_name}")
            
            if not file_path.exists():
                logger.warning(f"[{i}/{len(materials)}] ⚠️  {material_name} - No frontmatter file found, skipping")
                skipped_count += 1
                continue
            
            logger.info(f"[{i}/{len(materials)}] 🔄 Generating subtitle for {material_name}...")
            
            # Generate new subtitle
            new_subtitle = generate_subtitle(
                api_client=api_client,
                material_name=material_name,
                category=category,
                subcategory=subcategory,
                material_data=material_data
            )
            
            # Update YAML file
            update_subtitle_in_yaml(file_path, new_subtitle)
            
            success_count += 1
            
            # Calculate ETA
            elapsed = time.time() - start_time
            avg_time = elapsed / success_count
            remaining = (len(materials) - i) * avg_time
            eta_minutes = remaining / 60
            
            logger.info(f"✅ {material_name}")
            logger.info(f"   Subtitle: {new_subtitle[:80]}..." if len(new_subtitle) > 80 else f"   Subtitle: {new_subtitle}")
            logger.info(f"   ⏱️  ETA: {eta_minutes:.1f} minutes ({success_count}/{len(materials)} complete)")
            logger.info("")
                
        except Exception as e:
            error_count += 1
            logger.error(f"❌ {material_name} - Error: {e}")
            logger.info("")
            continue
    
    # Final summary
    total_time = time.time() - start_time
    logger.info("\n" + "=" * 70)
    logger.info("🎉 Subtitle generation complete!")
    logger.info("=" * 70)
    logger.info(f"✅ Success: {success_count}/{len(materials)}")
    logger.info(f"⚠️  Skipped: {skipped_count}/{len(materials)}")
    logger.info(f"❌ Errors: {error_count}/{len(materials)}")
    logger.info(f"📊 Success rate: {success_count/(len(materials)-skipped_count)*100:.1f}%")
    logger.info(f"⏱️  Total time: {total_time/60:.1f} minutes")
    if success_count > 0:
        logger.info(f"⚡ Average: {total_time/success_count:.1f} seconds per material")

if __name__ == "__main__":
    main()
