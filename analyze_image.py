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
    prompt = """Analyze this before/after laser cleaning composite image in detail:

1. **STRUCTURE ANALYSIS**:
   - Is this a side-by-side composite (left=before, right=after)?
   - Are both sides showing the same object?
   - Is there a clear vertical split?
   - What is the aspect ratio?

2. **CONTAMINATION ASSESSMENT (LEFT SIDE - BEFORE)**:
   - What material/object is shown?
   - What types of contamination are visible?
   - How heavy is the contamination (coverage %)?
   - Are the contaminants scientifically accurate?
   - Color, texture, and pattern of contamination?

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

5. **REALISM & QUALITY**:
   - Does contamination look natural or artificial?
   - Is the material appearance authentic?
   - Are there any AI artifacts or unrealistic elements?
   - Overall photorealism quality (1-10)?
   - Any text, labels, or watermarks?

6. **TECHNICAL ACCURACY**:
   - Are the contaminants chemically/scientifically accurate?
   - Is the contamination pattern realistic for this material?
   - Does the clean state look like actual laser cleaning results?
   - Any physics violations or impossible elements?

7. **OVERALL ASSESSMENT**:
   - Does this successfully demonstrate laser cleaning effectiveness?
   - Would this be useful for marketing/educational purposes?
   - What are the strongest aspects?
   - What could be improved?
   - Grade (A/B/C/D/F) with explanation.

Be detailed, specific, and honest in your analysis."""
    
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
