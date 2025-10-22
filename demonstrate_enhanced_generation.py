#!/usr/bin/env python3
"""
Demonstrate enhanced text generation with before/after comparison
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from components.frontmatter.core.hybrid_generation_manager import HybridFrontmatterManager, GenerationMode
from data.materials import get_material_by_name_cached

class ComparisonAPIClient:
    """Mock API client that shows the difference between basic and enhanced prompts"""
    
    def __init__(self, show_prompts=False):
        self.show_prompts = show_prompts
        self.call_count = 0
    
    def generate_content(self, prompt, max_tokens=200, temperature=0.3):
        self.call_count += 1
        
        # Detect if this is an enhanced prompt
        is_enhanced = any(indicator in prompt for indicator in [
            "MATERIAL DIFFERENTIATION REQUIREMENTS",
            "UNIQUE CHARACTERISTICS",
            "SPECIAL TECHNIQUES & CARE",
            "COMPARATIVE ANALYSIS"
        ])
        
        if self.show_prompts:
            print(f"\n{'='*60}")
            print(f"📋 API Call #{self.call_count} - {'Enhanced' if is_enhanced else 'Basic'} Prompt")
            print(f"📏 Length: {len(prompt):,} characters")
            print(f"{'='*60}")
            
            # Show first 500 characters
            preview = prompt[:500] + "..." if len(prompt) > 500 else prompt
            print(preview)
            print(f"{'='*60}")
        
        # Generate different responses based on prompt type
        if is_enhanced:
            return self._generate_enhanced_response(prompt)
        else:
            return self._generate_basic_response(prompt)
    
    def _generate_enhanced_response(self, prompt):
        """Generate response that reflects enhanced prompting"""
        if "subtitle" in prompt.lower():
            return "Lightweight non-ferrous metal offering superior thermal conductivity and corrosion resistance—ideal for precision aerospace applications requiring specialized low-power laser parameters"
        elif "description" in prompt.lower():
            return "Aluminum's exceptional thermal conductivity (237 W/m·K) and low density (2.70 g/cm³) distinguish it from other metals, requiring carefully controlled laser parameters to prevent thermal damage while achieving superior surface preparation compared to steel alternatives."
        elif "safety_considerations" in prompt.lower():
            return "Aluminum's high thermal conductivity demands reduced laser power settings (30% lower than steel) to prevent workpiece warping. Unlike ferrous metals, aluminum generates minimal sparks but requires enhanced ventilation due to oxide particle generation during ablation."
        elif "technical_notes" in prompt.lower():
            return "Optimize pulse frequency to 20-50 kHz for aluminum vs. 10-30 kHz for steel. Aluminum's reflectivity necessitates higher absorption coatings than copper but lower power density than titanium, making it ideal for delicate component cleaning."
        else:
            return "Enhanced content with material-specific differentiation, special techniques, and comparative advantages/disadvantages integrated"
    
    def _generate_basic_response(self, prompt):
        """Generate basic response without differentiation"""
        if "subtitle" in prompt.lower():
            return "Professional laser cleaning parameters for aluminum materials"
        elif "description" in prompt.lower():
            return "Technical laser cleaning specifications for aluminum with appropriate parameters and safety considerations."
        elif "safety_considerations" in prompt.lower():
            return "Follow standard laser safety protocols when cleaning aluminum materials."
        elif "technical_notes" in prompt.lower():
            return "Use appropriate laser settings for aluminum cleaning applications."
        else:
            return "Basic generated content without material differentiation"

def demonstrate_enhancement_difference():
    """Show before/after comparison of enhanced vs basic generation"""
    
    print("🔬 Enhanced vs Basic Text Generation Comparison")
    print("=" * 60)
    
    # Initialize manager
    manager = HybridFrontmatterManager()
    
    # Test with Aluminum
    material_name = "Aluminum"
    material_data = get_material_by_name_cached(material_name)
    
    context_frontmatter = {
        "title": "Aluminum Laser Cleaning Parameters",
        "applications": ["aerospace", "automotive", "electronics"]
    }
    
    # Test fields
    test_fields = ["subtitle", "description", "safety_considerations", "technical_notes"]
    
    for field_name in test_fields:
        print(f"\n🎯 Field: {field_name}")
        print("-" * 40)
        
        # Generate with enhanced prompting (our new system)
        api_client = ComparisonAPIClient(show_prompts=False)
        
        try:
            result = manager.generate_frontmatter(
                material_name=material_name,
                mode=GenerationMode.TEXT_ONLY,
                text_api_client=api_client,
                existing_frontmatter=context_frontmatter
            )
            
            enhanced_content = result.get(field_name, "Not generated")
            
            print(f"✨ Enhanced: {enhanced_content}")
            
            # Show what basic would look like
            basic_content = api_client._generate_basic_response(f"Generate {field_name} for {material_name}")
            print(f"📝 Basic:    {basic_content}")
            
            # Analysis
            enhanced_words = len(enhanced_content.split())
            basic_words = len(basic_content.split())
            
            has_differentiation = any(term in enhanced_content.lower() for term in [
                "compared to", "vs", "unlike", "than", "advantages", "disadvantages",
                "thermal conductivity", "density", "superior", "specialized"
            ])
            
            has_techniques = any(term in enhanced_content.lower() for term in [
                "parameters", "power", "frequency", "technique", "approach", "method"
            ])
            
            print(f"📊 Analysis:")
            print(f"   • Words: Enhanced ({enhanced_words}) vs Basic ({basic_words})")
            print(f"   • Material differentiation: {'✅' if has_differentiation else '❌'}")
            print(f"   • Special techniques: {'✅' if has_techniques else '❌'}")
            
        except Exception as e:
            print(f"❌ Error generating {field_name}: {e}")

def show_prompt_comparison():
    """Show actual prompt differences"""
    
    print(f"\n📋 Prompt Structure Comparison")
    print("=" * 50)
    
    api_client = ComparisonAPIClient(show_prompts=True)
    manager = HybridFrontmatterManager()
    
    print("🔍 Generating subtitle with enhanced prompting...")
    
    try:
        result = manager.generate_frontmatter(
            material_name="Aluminum",
            mode=GenerationMode.TEXT_ONLY,
            text_api_client=api_client,
            existing_frontmatter={"title": "Aluminum Laser Cleaning Parameters"}
        )
        
        print(f"\n✅ Result: {result.get('subtitle', 'No subtitle generated')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    demonstrate_enhancement_difference()
    show_prompt_comparison()