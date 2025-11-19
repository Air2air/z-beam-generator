#!/usr/bin/env python3
"""
Regenerate Professional Subtitles for All Materials

Simplified Architecture:
1. Generate context-only prompt (no voice markers)
2. Call API to generate neutral professional content
3. Apply voice postprocessor to add author-specific markers
4. Save to Materials.yaml

This ensures clean separation: prompt = context, voice = postprocessing.
"""

import yaml
import random
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.api.client_factory import create_api_client
from shared.prompts.text_prompt_builder import TextPromptBuilder, FocusArea as FocusAreaClass
from shared.voice.post_processor import VoicePostProcessor
from export.utils.author_manager import get_author_by_id

# Subtitle focus areas (randomly selected for each material)
SUBTITLE_FOCUS_AREAS = [
    {
        "id": "unique_characteristics",
        "name": "Unique Material Characteristics",
        "prompt_addition": "Focus on the material's unique physical, chemical, or structural properties that make laser cleaning particularly effective or challenging."
    },
    {
        "id": "sibling_comparison",
        "name": "Compare to Sibling Materials",
        "prompt_addition": "Briefly compare this material to similar materials in its category, highlighting why laser cleaning parameters differ."
    },
    {
        "id": "cleaning_techniques",
        "name": "Special Cleaning Techniques",
        "prompt_addition": "Emphasize specific laser cleaning techniques, wavelengths, or pulse durations optimized for this material."
    },
    {
        "id": "industry_applications",
        "name": "Industry-Specific Applications",
        "prompt_addition": "Reference the primary industries or applications where laser cleaning this material is most critical."
    },
    {
        "id": "critical_challenges",
        "name": "Critical Cleaning Challenges",
        "prompt_addition": "Highlight the main technical challenge in laser cleaning this material (e.g., thermal sensitivity, oxidation risk)."
    },
    {
        "id": "preservation_benefits",
        "name": "Preservation Over Traditional Methods",
        "prompt_addition": "Emphasize what laser cleaning preserves that traditional chemical or abrasive methods would damage."
    },
    {
        "id": "material_vulnerabilities",
        "name": "Material Vulnerability Concerns",
        "prompt_addition": "Address the material's thermal limits, damage thresholds, or phase change risks during cleaning."
    },
    {
        "id": "surface_outcomes",
        "name": "Surface Finish Outcomes",
        "prompt_addition": "Describe the expected surface finish, appearance, or functional properties after laser cleaning."
    },
    {
        "id": "contamination_types",
        "name": "Material-Specific Contamination",
        "prompt_addition": "Specify the types of contamination, corrosion, or coatings commonly found on this material that laser cleaning addresses."
    },
    {
        "id": "parameter_optimization",
        "name": "Critical Parameter Optimization",
        "prompt_addition": "Focus on the most critical laser parameter (fluence, pulse duration, wavelength) that determines success."
    }
]

def load_materials() -> Dict:
    """Load Materials.yaml"""
    materials_file = Path('data/materials/Materials.yaml')
    with open(materials_file, 'r') as f:
        return yaml.safe_load(f)

def get_sibling_materials(category: str, subcategory: str, all_materials: Dict, exclude_material: str) -> List[str]:
    """Get list of sibling materials in same category/subcategory"""
    siblings = []
    materials = all_materials.get('materials', {})
    
    for mat_name, mat_data in materials.items():
        if mat_name == exclude_material:
            continue
        if mat_data.get('category') == category:
            if subcategory and mat_data.get('subcategory') == subcategory:
                siblings.append(mat_name)
            elif not subcategory:
                siblings.append(mat_name)
    
    return siblings[:3]  # Return max 3 siblings

def generate_subtitle_prompt(material_name: str, category: str, subcategory: str, 
                             focus_area: Dict, siblings: List[str], author_id: int = None) -> str:
    """Generate the prompt for subtitle generation with author-specific voice using shared prompt builder"""
    
    # Initialize prompt builder
    builder = TextPromptBuilder()
    
    # Convert focus_area dict to FocusArea dataclass
    focus = FocusAreaClass(
        id=focus_area['id'],
        name=focus_area['name'],
        prompt_addition=focus_area['prompt_addition']
    )
    
    # Build prompt using shared template
    return builder.build_prompt(
        component_type='subtitle',
        material_name=material_name,
        category=category,
        subcategory=subcategory,
        author_id=author_id,
        focus_area=focus,
        siblings=siblings if siblings else None
    )

def generate_subtitle(api_client, voice_processor: VoicePostProcessor, material_name: str, category: str, 
                     subcategory: str, focus_area: Dict, siblings: List[str], 
                     author_id: int = None) -> Optional[str]:
    """
    Generate subtitle using post-processing architecture:
    1. Generate simple neutral subtitle (context only)
    2. Transform structure for variation
    3. Validate with AI detection
    4. Retry on failure (max 3 attempts)
    """
    from shared.voice.orchestrator import VoiceOrchestrator
    
    # Get author information
    author_info = get_author_by_id(author_id) if author_id else None
    if not author_info:
        print(f"  ⚠️  Author ID {author_id} not found, using default")
        author_info = get_author_by_id(1)  # Default to author 1
    
    try:
        # Initialize VoiceOrchestrator with author's country
        voice = VoiceOrchestrator(country=author_info['country'])
        
        # Build material context
        material_context = {
            'material_name': material_name,
            'category': category,
            'subcategory': subcategory,
            'focus_area': focus_area['prompt_addition'] if focus_area else None,
            'siblings': siblings if siblings else []
        }
        
        # Generate SIMPLE prompt (context only - no anti-AI rules)
        prompt = voice.get_unified_prompt(
            component_type='subtitle',
            material_context=material_context,
            author=author_info
        )
        
        # Call API with simple prompt
        response = api_client.generate_simple(
            prompt=prompt,
            system_prompt="You are a technical writer creating concise, professional subtitles.",
            temperature=0.7,
            max_tokens=100
        )
        
        if not response.success or not response.content or not response.content.strip():
            error_msg = response.error if hasattr(response, 'error') else "Empty response"
            print(f"  ❌ API error: {error_msg}")
            return None
        
        # Get neutral subtitle
        neutral_subtitle = response.content.strip().strip('"\'')
        print(f"   📝 Generated: {neutral_subtitle}")
        
        # Apply structural transformation with AI detection
        result = voice_processor.transform_subtitle_structure(
            subtitle=neutral_subtitle,
            material_name=material_name,
            max_attempts=3
        )
        
        if not result['success']:
            print(f"  ⚠️  Transformation failed after {result['attempts']} attempts")
            print(f"      AI score: {result['ai_score']:.1f}/100")
            # Use original if transformation failed but score is acceptable
            if result['ai_score'] < 50:
                transformed_subtitle = result['content']
            else:
                return None
        else:
            transformed_subtitle = result['content']
            print(f"   ✅ Transformed ({result['transformation']}): {transformed_subtitle}")
            print(f"      AI score: {result['original_ai_score']:.1f} → {result['ai_score']:.1f}")
        
        # Validate word count
        word_count = len(transformed_subtitle.split())
        if word_count < 7 or word_count > 20:
            print(f"  ⚠️  Unusual length: {word_count} words")
        
        return transformed_subtitle
            
    except Exception as e:
        print(f"  ❌ Generation error: {e}")
        import traceback
        traceback.print_exc()
        return None

def validate_subtitle(subtitle: str) -> tuple[bool, List[str]]:
    """Validate subtitle for voice markers and quality using voice controller"""
    
    # Import voice controller for official validation
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from components.text.utils.voice_controller import VoiceApplicationController
        
        controller = VoiceApplicationController()
        
        # Validate that subtitle does NOT have voice markers (as per policy)
        is_valid, errors = controller.validate_field_voice(
            'subtitle', subtitle, 'materials_page'
        )
        
        if not is_valid:
            # Extract just the marker names from error messages
            found_markers = []
            for error in errors:
                if 'voice markers' in error.lower():
                    # Parse markers from error message if needed
                    found_markers.append("voice_marker_detected")
            return False, found_markers if found_markers else ["validation_failed"]
        
        return True, []
        
    except Exception:
        # Fallback to simple validation if controller fails
        voice_markers = [
            "pretty", "basically", "fairly", "typically", "notably", 
            "specifically", "thus", "distinctly", "essential", "straightforwardly",
            "generally", "essentially", "relatively"
        ]
        
        found_markers = []
        subtitle_lower = subtitle.lower()
        
        for marker in voice_markers:
            if f" {marker} " in f" {subtitle_lower} " or subtitle_lower.startswith(marker + " "):
                found_markers.append(marker)
        
        is_valid = len(found_markers) == 0
        
        return is_valid, found_markers

def main():
    # Check for test mode
    test_mode = '--test' in sys.argv
    test_count = 10 if test_mode else None
    
    print("=" * 80)
    if test_mode:
        print(f"SUBTITLE REGENERATION - TEST MODE ({test_count} MATERIALS)")
    else:
        print("SUBTITLE REGENERATION - PROFESSIONAL VOICE-FREE EDITION")
    print("=" * 80)
    print()
    
    # Load materials
    print("📂 Loading materials data...")
    materials_data = load_materials()
    materials = materials_data.get('materials', {})
    print(f"✅ Loaded {len(materials)} materials")
    
    if test_mode:
        print(f"🧪 TEST MODE: Will process only {test_count} materials")
        # Select diverse sample across categories
        materials_by_category = {}
        for name, data in materials.items():
            cat = data.get('category', 'unknown')
            if cat not in materials_by_category:
                materials_by_category[cat] = []
            materials_by_category[cat].append((name, data))
        
        # Sample from each category
        test_materials = {}
        per_category = max(1, test_count // len(materials_by_category))
        for cat, mat_list in materials_by_category.items():
            sample = random.sample(mat_list, min(per_category, len(mat_list)))
            test_materials.update(dict(sample))
        
        # If we need more, add random extras
        if len(test_materials) < test_count:
            remaining = list(set(materials.keys()) - set(test_materials.keys()))
            extras = random.sample(remaining, min(test_count - len(test_materials), len(remaining)))
            for name in extras:
                test_materials[name] = materials[name]
        
        materials = test_materials
        print(f"✅ Selected {len(materials)} materials for testing")
    
    print()
    
    # Create API client and voice processor
    print("🔑 Initializing Grok API client...")
    api_client = create_api_client('grok')
    print("✅ API client ready")
    
    print("🎭 Initializing voice postprocessor...")
    voice_processor = VoicePostProcessor(api_client)
    print("✅ Voice processor ready")
    print()
    
    # Statistics
    total_materials = len(materials)
    processed = 0
    successful = 0
    failed = 0
    validation_failures = 0
    
    print(f"🎯 Regenerating subtitles for {total_materials} materials...")
    print("📊 Focus areas will be randomly assigned for variety")
    print()
    print("-" * 80)
    
    # Process each material
    for material_name, material_data in sorted(materials.items()):
        processed += 1
        
        category = material_data.get('category', 'unknown')
        subcategory = material_data.get('subcategory', '')
        current_subtitle = material_data.get('subtitle', '')
        author_id = material_data.get('author', {}).get('id')
        
        # Randomly select focus area
        focus_area = random.choice(SUBTITLE_FOCUS_AREAS)
        
        # Get sibling materials if doing comparison
        siblings = []
        if focus_area['id'] == 'sibling_comparison':
            siblings = get_sibling_materials(category, subcategory, materials_data, material_name)
        
        print(f"\n{processed}/{total_materials}. {material_name} ({category})")
        print(f"   Author: {author_id}, Focus: {focus_area['name']}")
        print(f"   Current: {current_subtitle[:80]}{'...' if len(current_subtitle) > 80 else ''}")
        
        # Generate new subtitle using simplified pipeline: prompt → API → postprocessor
        new_subtitle = generate_subtitle(api_client, voice_processor, material_name, category, 
                                        subcategory, focus_area, siblings, author_id)
        
        if new_subtitle:
            # Validate
            is_valid, markers = validate_subtitle(new_subtitle)
            
            if is_valid:
                print(f"   ✅ New: {new_subtitle}")
                print(f"   Length: {len(new_subtitle.split())} words")
                
                # Update material data
                material_data['subtitle'] = new_subtitle
                
                # Update metadata
                if 'subtitle_metadata' not in material_data:
                    material_data['subtitle_metadata'] = {}
                
                material_data['subtitle_metadata'].update({
                    'generated': '2025-11-13T00:00:00Z',
                    'word_count': len(new_subtitle.split()),
                    'character_count': len(new_subtitle),
                    'generation_method': 'context_prompt_plus_voice_postprocessor',
                    'focus_area': focus_area['id'],
                    'voice_enhanced': True,
                    'author_id': author_id
                })
                
                successful += 1
            else:
                print(f"   ❌ VALIDATION FAILED: Voice markers found: {', '.join(markers)}")
                print(f"   Generated: {new_subtitle}")
                validation_failures += 1
                failed += 1
        else:
            print("   ❌ Generation failed")
            failed += 1
    
    print()
    print("=" * 80)
    if test_mode:
        print("TEST MODE - SKIPPING SAVE")
    else:
        print("SAVING UPDATED MATERIALS")
    print("=" * 80)
    
    if not test_mode:
        # Create backup
        backup_file = Path('data/materials/Materials_backup_before_subtitle_regen.yaml')
        with open('data/materials/Materials.yaml', 'r') as f:
            backup_content = f.read()
        with open(backup_file, 'w') as bf:
            bf.write(backup_content)
        print(f"💾 Backup created: {backup_file}")
        
        # Save updated materials
        with open('data/materials/Materials.yaml', 'w') as f:
            yaml.dump(materials_data, f, default_flow_style=False, sort_keys=False, 
                      allow_unicode=True, width=1000)
        print("💾 Saved to materials/data/Materials.yaml")
    else:
        print("⚠️  Test mode - changes NOT saved to disk")
        print("   To save changes, run without --test flag")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total materials: {total_materials}")
    print(f"✅ Successfully regenerated: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Validation failures: {validation_failures}")
    print(f"Success rate: {(successful/total_materials)*100:.1f}%")
    print()
    
    # Focus area distribution
    print("Focus Area Distribution:")
    focus_counts = {}
    for material_data in materials.values():
        focus = material_data.get('subtitle_metadata', {}).get('focus_area', 'unknown')
        focus_counts[focus] = focus_counts.get(focus, 0) + 1
    
    for focus_id, count in sorted(focus_counts.items(), key=lambda x: x[1], reverse=True):
        focus_name = next((f['name'] for f in SUBTITLE_FOCUS_AREAS if f['id'] == focus_id), focus_id)
        print(f"  {focus_name}: {count}")
    
    print()
    print("✨ Subtitle regeneration complete!")
    print()

if __name__ == '__main__':
    main()
