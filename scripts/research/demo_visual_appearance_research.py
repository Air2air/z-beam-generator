#!/usr/bin/env python3
"""
Visual Appearance Research Demo

Demonstrates how VisualAppearanceResearcher works and shows
the expected output format for visual descriptions.

This is a dry-run that shows what the actual research would produce,
without requiring an API key.

Author: AI Assistant  
Date: November 26, 2025
"""

import json
from pathlib import Path


def demonstrate_research_workflow():
    """Show the complete research workflow."""
    
    print("=" * 80)
    print("VISUAL APPEARANCE RESEARCH WORKFLOW DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Step 1: Show example input
    print("📥 INPUT: Contamination Pattern")
    print("-" * 80)
    
    example_input = {
        'pattern_id': 'oil-grease',
        'name': 'Oil & Grease Contamination',
        'material': 'Aluminum',
        'composition': 'Hydrocarbon chains, mineral oils',
        'material_properties': {
            'color': 'Silver-white metallic',
            'hardness': '2.5-3 Mohs',
            'texture': 'Brushed metal finish'
        }
    }
    
    print(json.dumps(example_input, indent=2))
    print()
    
    # Step 2: Show what researcher does
    print("🔬 RESEARCH PROCESS")
    print("-" * 80)
    print("1. Builds detailed prompt asking about:")
    print("   - Overall visual appearance")
    print("   - Color variations (fresh to aged)")
    print("   - Texture details (smooth, rough, sticky, etc.)")
    print("   - Distribution patterns (drips, uniform, spots)")
    print("   - Aging effects (how it changes over time)")
    print("   - Lighting behavior (gloss, matte, iridescence)")
    print("   - Thickness range (thin film to heavy buildup)")
    print("   - Environmental factors (what affects distribution)")
    print()
    print("2. Queries Gemini 2.0 Flash for scientific accuracy")
    print("3. Parses JSON response into structured data")
    print("4. Formats for insertion into Contaminants.yaml")
    print()
    
    # Step 3: Show example output
    print("📤 OUTPUT: Visual Appearance Data")
    print("-" * 80)
    
    example_output = {
        "description": "Oil and grease on aluminum appears as dark, irregular patches with a distinctive rainbow sheen under direct light. Fresh contamination is translucent amber to brown, while aged deposits darken to near-black. The contamination preferentially collects in crevices, corners, and low points where it forms glossy pools when fresh, becoming matte and sticky as it ages.",
        
        "color_variations": "Fresh: Translucent amber to light brown with rainbow iridescence. Moderately aged (weeks): Dark brown with reduced sheen. Heavily aged (months): Nearly black with matte finish. May show rust-orange staining if mixed with ferrous particles from machinery.",
        
        "texture_details": "Fresh oil is smooth and glossy with liquid-like appearance. As it ages, it becomes increasingly sticky and tacky to touch. Old deposits are matte, grimy, and may feel waxy or crusty. Dust and particles adhere to aged grease, creating a rough, irregular surface texture.",
        
        "common_patterns": "Forms drip marks from vertical surfaces, pooling at edges and in recessed areas. Fingerprints and handling marks are clearly visible. On machinery components, concentrates around moving parts, joints, and fasteners. Creates irregular patches rather than uniform coating, with sharp boundaries between contaminated and clean areas.",
        
        "aged_appearance": "Fresh (hours-days): Glossy, liquid-like, amber to brown, strong rainbow sheen. Moderate age (weeks): Darker brown, reduced gloss, slightly tacky, dust begins adhering. Heavy age (months+): Nearly black, completely matte, crusty edges, significant dust/particle incorporation, may show cracking in thick deposits.",
        
        "lighting_effects": "Under direct sunlight: Shows prominent rainbow iridescence (fresh oil) or dull matte black (aged). Under fluorescent lighting: Fresh appears glossy with less pronounced colors; aged appears uniformly dark. Side lighting emphasizes texture differences between glossy pools and matte aged areas.",
        
        "thickness_range": "Thin film: 0.05-0.2mm (barely visible, slight darkening). Moderate: 0.2-1mm (clearly visible, drip marks, fingerprints). Heavy: 1-5mm (thick pools, crusty edges, completely obscures base metal).",
        
        "distribution_factors": "Gravity causes dripping and pooling in low areas. Mechanical contact deposits oil via tools and handling. Heat from machinery causes oil to flow and spread. Poor ventilation allows buildup rather than evaporation. High-touch areas show most contamination. Horizontal surfaces accumulate more than vertical."
    }
    
    print(json.dumps(example_output, indent=2))
    print()
    
    # Step 4: Show YAML format
    print("📝 YAML FORMAT (for Contaminants.yaml)")
    print("-" * 80)
    
    yaml_format = """visual_characteristics:
  appearance_on_materials:
    aluminum:
      description: "Oil and grease on aluminum appears as dark, irregular patches..."
      color_variations: "Fresh: Translucent amber to light brown with rainbow..."
      texture_details: "Fresh oil is smooth and glossy with liquid-like appearance..."
      common_patterns: "Forms drip marks from vertical surfaces, pooling at edges..."
      aged_appearance: "Fresh (hours-days): Glossy, liquid-like, amber to brown..."
      lighting_effects: "Under direct sunlight: Shows prominent rainbow iridescence..."
      thickness_range: "Thin film: 0.05-0.2mm (barely visible, slight darkening)..."
      distribution_factors: "Gravity causes dripping and pooling in low areas..."
"""
    
    print(yaml_format)
    print()
    
    # Step 5: Show usage impact
    print("🎨 IMPACT ON IMAGE GENERATION")
    print("-" * 80)
    print("With this data, AI image prompts will include:")
    print()
    print("✅ Specific colors: 'Dark brown with rainbow sheen' not just 'dark'")
    print("✅ Texture details: 'Glossy when fresh, matte when aged'")
    print("✅ Distribution: 'Drip marks, fingerprints, pools in crevices'")
    print("✅ Aging effects: 'Fresh vs months-old appearance'")
    print("✅ Lighting behavior: 'Rainbow iridescence under direct light'")
    print()
    print("Result: Photo-realistic, scientifically accurate contamination images")
    print()
    
    # Step 6: Show batch research
    print("📊 BATCH RESEARCH EXAMPLE")
    print("-" * 80)
    print("Research oil-grease on multiple materials:")
    print()
    
    materials = ['Aluminum', 'Steel', 'Copper', 'Brass', 'Titanium']
    for i, material in enumerate(materials, 1):
        print(f"[{i}/{len(materials)}] {material}")
        print(f"   🔬 Researching appearance on {material}...")
        print(f"   ✅ Complete - 8 visual aspects documented")
        print()
    
    print("Result: Material-specific descriptions for realistic variations")
    print()
    
    print("=" * 80)
    print("READY TO RUN ACTUAL RESEARCH")
    print("=" * 80)
    print()
    print("Set GEMINI_API_KEY and run:")
    print()
    print("  # Single pattern")
    print("  python3 scripts/research/populate_visual_appearances.py \\")
    print("    --pattern oil-grease")
    print()
    print("  # All patterns")
    print("  python3 scripts/research/populate_visual_appearances.py \\")
    print("    --all")
    print()
    print("  # Custom materials")
    print("  python3 scripts/research/populate_visual_appearances.py \\")
    print("    --pattern rust-oxidation \\")
    print("    --materials \"Steel,Iron,Cast Iron\"")
    print()


if __name__ == '__main__':
    demonstrate_research_workflow()
