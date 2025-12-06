#!/usr/bin/env python3
"""
Quick Image Analysis using Gemini Vision

Analyzes generated before/after images using Gemini 2.0 Flash vision.
"""

import os
import sys
from pathlib import Path
import google.generativeai as genai
from PIL import Image

def analyze_image(image_path: str):
    """Analyze image with Gemini Vision."""
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not set")
        sys.exit(1)
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Load image
    image_path = Path(image_path)
    if not image_path.exists():
        print(f"❌ Image not found: {image_path}")
        sys.exit(1)
    
    print(f"🔍 Analyzing: {image_path.name}")
    print(f"📂 Path: {image_path}")
    print("")
    
    # Open image
    img = Image.open(image_path)
    print(f"📐 Dimensions: {img.size[0]}x{img.size[1]} ({img.size[0]/img.size[1]:.2f}:1 ratio)")
    print(f"💾 Format: {img.format}")
    print(f"📏 File size: {image_path.stat().st_size / 1024:.1f} KB")
    print("")
    
    # Analysis prompt
    prompt = """Analyze this before/after laser cleaning composite image in detail.

**CRITICAL FOCUS**: Absolute realism in contamination distribution and appearance.
Compare this image to your knowledge of actual photographs of contaminated materials.
If contamination looks "painted on" or artificially applied, flag it immediately.

1. **STRUCTURE ANALYSIS**:
   - Is this a side-by-side composite (left=before, right=after)?
   - Are both sides showing the same object?
   - Is there a clear vertical split?
   - What is the aspect ratio?

2. **CONTAMINATION REALISM ASSESSMENT (LEFT SIDE - BEFORE)**:
   
   **Material Identification**:
   - What material/object is shown?
   - Is the base material appearance authentic?
   - Does it match real-world examples of this material?
   
   **Contamination Types & Accuracy**:
   - What specific contaminants are visible (rust, oxidation, oils, dirt, grime, etc.)?
   - Are these contaminants chemically/physically accurate for this material?
   - Do they follow real-world formation patterns?
   - Compare to actual photos of contaminated [material name] - does this match?
   
   **Distribution Realism** (CRITICAL):
   - Is contamination distributed naturally or uniformly artificial?
   - Does it accumulate in physically logical locations (edges, crevices, horizontal surfaces)?
   - Are there gravity effects (drips, runs, pooling at bottom)?
   - Is there variation in contamination density (heavier in some areas)?
   - Any impossible patterns (floating contamination, defying physics)?
   
   **Contamination Coverage**:
   - Estimated coverage percentage (10%, 50%, 90%)?
   - Is coverage realistic for the contamination type?
   - Too uniform/perfect or naturally irregular?
   
   **Visual Authenticity**:
   - Color accuracy: Do contaminants have realistic hues and tones?
   - Texture realism: Matte dirt, glossy oils, granular rust, etc.?
   - Thickness variation: Thin films vs thick buildup where appropriate?
   - Layer interaction: Do multiple contaminants overlap naturally?
   - Light interaction: Proper absorption/reflection for contamination type?
   
   **Red Flags for Artificial Contamination**:
   - "Painted-on" appearance
   - Perfectly even distribution
   - Contamination in impossible locations
   - Wrong colors for material chemistry
   - Missing expected weathering patterns
   - Looks like digital overlay vs physical buildup

3. **CLEAN STATE ASSESSMENT (RIGHT SIDE - AFTER)**:
   - Is the material clearly visible and clean?
   - Is it the same object as the left side?
   - Are there subtle differences in positioning/angle?
   - Is there any residual contamination?
   - Does it show laser cleaning characteristics?

4. **CONSISTENCY CHECKS**:
   - Same object geometry on both sides?
   - Same permanent features (scratches, dents, marks)?
   - Consistent lighting and shadows?
   - Realistic viewpoint shift?
   - Same base material properties visible?

5. **REALISM & AUTHENTICITY**:
   
   **Contamination Naturalness**:
   - Does contamination look like real environmental/industrial buildup?
   - Natural vs artificial appearance (1-10 scale)?
   - Would this fool an expert in material contamination?
   
   **Material Appearance**:
   - Is the base material authentic for its type?
   - Proper surface characteristics (grain, texture, finish)?
   - Realistic wear patterns and age indicators?
   
   **Photographic Quality**:
   - Overall photorealism (1-10)?
   - Lighting quality and consistency?
   - Depth, shadows, and three-dimensionality?
   
   **AI Artifacts** (Flag if detected):
   - Unnatural patterns or repetition
   - Blurry/merged boundaries
   - Impossible reflections or lighting
   - Text generation errors
   - "Too perfect" synthetic appearance
   
   **Professional Assessment**:
   - Could this be used in professional documentation?
   - Would materials scientists accept this as realistic?
   - Marketing/educational value (high/medium/low)?
   - Any text, labels, watermarks, or overlays?

6. **TECHNICAL ACCURACY & PHYSICS**:
   
   **Contamination Chemistry**:
   - Are the contaminants chemically/scientifically accurate for this material?
   - Do oxidation colors match real chemistry (e.g., green copper patina, orange iron rust)?
   - Are interaction products realistic (corrosion patterns, chemical staining)?
   
   **Contamination Physics**:
   - Does contamination follow gravity (drips down, pools at bottom)?
   - Appropriate adhesion patterns for contamination type?
   - Proper weathering progression (fresh vs aged contamination)?
   - Realistic accumulation in recesses and protected areas?
   
   **Reference Comparison**:
   - Compare to actual photographs of contaminated [material]
   - Does this match real-world industrial/environmental contamination?
   - Any elements that wouldn't occur naturally?
   
   **Laser Cleaning Characteristics**:
   - Does the clean state show authentic laser cleaning results?
   - Appropriate micro-texture from laser ablation?
   - Realistic residue patterns in deep features?
   - Proper material color restoration?
   
   **Physics Violations** (Flag if present):
   - Contamination defying gravity
   - Impossible chemical combinations
   - Wrong oxidation states for environment
   - Contamination in physically unreachable locations

7. **OVERALL ASSESSMENT & GRADING**:
   
   **Effectiveness**:
   - Does this successfully demonstrate laser cleaning effectiveness?
   - Clear before/after contrast visible?
   - Would this convince someone of laser cleaning capabilities?
   
   **Use Cases**:
   - Marketing materials: Suitable? (Yes/No + why)
   - Educational/training: Suitable? (Yes/No + why)
   - Technical documentation: Suitable? (Yes/No + why)
   
   **Strengths** (List 3-5):
   - What works well in this image?
   - Most realistic elements?
   - Best demonstrations of contamination/cleaning?
   
   **Improvements Needed** (List 3-5):
   - What breaks realism?
   - Most artificial-looking elements?
   - Critical fixes required?
   
   **GRADING RUBRIC**:
   - **A (90-100)**: Photorealistic, natural contamination distribution, could pass as real photo
   - **B (80-89)**: Mostly realistic, minor artificial elements, usable with disclaimers
   - **C (70-79)**: Acceptable concept demo, obvious synthetic elements, limited professional use
   - **D (60-69)**: Poor realism, heavily artificial contamination, educational use only
   - **F (<60)**: Fails to demonstrate concept, unrealistic, unusable
   
   **FINAL GRADE**: [Letter grade] ([Score]/100)
   
   **GRADE JUSTIFICATION**: 
   - Primary reasons for this grade
   - Key factors affecting contamination realism
   - Comparison to real-world contaminated materials
   - Would a materials expert accept this as realistic?

Be detailed, specific, and brutally honest. Contamination realism is the #1 priority."""
    
    print("🤖 Analyzing with Gemini 2.0 Flash Vision...")
    print("="*80)
    
    # Generate analysis
    response = model.generate_content([prompt, img])
    
    print(response.text)
    print("")
    print("="*80)
    print("✅ Analysis complete")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_image.py <image_path>")
        print("Example: python3 analyze_image.py public/images/materials/beryllium-laser-cleaning.png")
        sys.exit(1)
    
    analyze_image(sys.argv[1])
