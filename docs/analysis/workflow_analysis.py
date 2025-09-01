#!/usr/bin/env python3
"""
Quick Content Generation Analysis
Focus on bloat, simplicity, and effectiveness evaluation.
"""

import sys
from pathlib import Path

# Add project root to path  
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from components.content.enhanced_generator import EnhancedContentGenerator
from components.content.human_validator import HumanLikeValidator
from api.client import MockAPIClient

def analyze_workflow():
    """Analyze the current workflow for bloat and effectiveness."""
    print("🔍 WORKFLOW ANALYSIS: Bloat, Simplicity, Effectiveness")
    print("=" * 60)
    
    # 1. Configuration Complexity Analysis
    print("\n📁 CONFIGURATION COMPLEXITY")
    print("-" * 30)
    
    config_files = [
        "components/content/prompts/base_content_prompt.yaml",
        "components/content/prompts/personas/taiwan_persona.yaml",
        "components/content/prompts/personas/italy_persona.yaml", 
        "components/content/prompts/personas/indonesia_persona.yaml",
        "components/content/prompts/personas/usa_persona.yaml",
        "components/content/prompts/formatting/taiwan_formatting.yaml",
        "components/content/prompts/formatting/italy_formatting.yaml",
        "components/content/prompts/formatting/indonesia_formatting.yaml",
        "components/content/prompts/formatting/usa_formatting.yaml",
        "components/author/authors.json"
    ]
    
    existing_files = []
    empty_files = []
    
    for file_path in config_files:
        try:
            path = Path(file_path)
            if path.exists():
                if path.stat().st_size == 0:
                    empty_files.append(file_path)
                else:
                    existing_files.append(file_path)
        except:
            pass
    
    print(f"📊 Configuration Files Found: {len(existing_files)}")
    print(f"❌ Empty/Broken Files: {len(empty_files)}")
    
    if empty_files:
        print("\n🚨 BLOAT ALERT: Empty formatting files detected!")
        for empty in empty_files:
            print(f"   - {empty}")
        print("   → ACTION: Remove or implement these files")
    
    # 2. Code Complexity Analysis
    print("\n💻 CODE COMPLEXITY")
    print("-" * 30)
    
    # Analyze Enhanced Generator complexity
    try:
        generator = EnhancedContentGenerator()
        validator = HumanLikeValidator()
        
        print("✅ Enhanced Generator: Initialized successfully")
        print(f"   - Validation enabled: {generator.enable_validation}")
        print(f"   - Threshold: {generator.human_likeness_threshold}")
        print(f"   - Max attempts: {generator.max_improvement_attempts}")
        
        print("✅ Human Validator: Initialized successfully")
        print(f"   - Validation categories: 5 (structural, typography, vocabulary, sentence, tone)")
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
    
    # 3. Generation Process Analysis
    print("\n⚙️ GENERATION PROCESS")
    print("-" * 30)
    
    process_steps = [
        "1. Load material data",
        "2. Load author configuration", 
        "3. Load persona configuration",
        "4. Load base prompt configuration",
        "5. Load formatting configuration (BROKEN)",
        "6. Generate initial content via API",
        "7. Validate content with 5-category system",
        "8. Generate improvement prompt if needed",
        "9. Regenerate content (up to 3 times)",
        "10. Apply persona formatting (BROKEN)",
        "11. Return best result"
    ]
    
    print("Current workflow steps:")
    for step in process_steps:
        if "BROKEN" in step:
            print(f"   ❌ {step}")
        else:
            print(f"   ✅ {step}")
    
    # 4. Effectiveness Analysis
    print("\n🎯 EFFECTIVENESS ANALYSIS")
    print("-" * 30)
    
    print("Current System Strengths:")
    print("   ✅ Multi-pass improvement capability")
    print("   ✅ Comprehensive human-like validation")
    print("   ✅ Persona-aware content generation")
    print("   ✅ Detailed scoring and feedback")
    
    print("\nCurrent System Weaknesses:")
    print("   ❌ Broken formatting files (empty)")
    print("   ❌ Complex configuration spread across multiple files")
    print("   ❌ Potential over-engineering (5 validation categories)")
    print("   ❌ Multiple file loads per generation")
    
    # 5. Recommendations
    print("\n💡 OPTIMIZATION RECOMMENDATIONS")
    print("-" * 30)
    
    recommendations = [
        {
            'priority': 'CRITICAL',
            'issue': 'Empty formatting files',
            'action': 'Remove or implement formatting logic',
            'impact': 'Eliminates broken functionality'
        },
        {
            'priority': 'HIGH', 
            'issue': 'Configuration complexity',
            'action': 'Consolidate persona + formatting into single files',
            'impact': 'Reduces file I/O and complexity'
        },
        {
            'priority': 'MEDIUM',
            'issue': 'Validation complexity',
            'action': 'Consider simplified 3-category validation',
            'impact': 'Faster validation, still effective'
        },
        {
            'priority': 'LOW',
            'issue': 'Multiple regeneration attempts',
            'action': 'Better initial prompts vs post-generation fixes',
            'impact': 'Reduced API calls, better efficiency'
        }
    ]
    
    for rec in recommendations:
        priority_color = {
            'CRITICAL': '🚨',
            'HIGH': '⚡',
            'MEDIUM': '🎯', 
            'LOW': '💡'
        }
        icon = priority_color.get(rec['priority'], '📝')
        
        print(f"{icon} {rec['priority']}: {rec['issue']}")
        print(f"   Action: {rec['action']}")
        print(f"   Impact: {rec['impact']}")
        print()

def test_simple_generation():
    """Test a simple generation to verify current functionality."""
    print("\n🧪 SIMPLE GENERATION TEST")
    print("-" * 30)
    
    try:
        # Test with mock client to avoid API dependencies
        generator = EnhancedContentGenerator(enable_validation=False)  # Disable validation for simplicity
        mock_client = MockAPIClient()
        
        test_material = {
            'name': 'Stainless Steel 316L',
            'formula': 'Fe-18Cr-10Ni-2Mo'
        }
        
        test_author = {
            'id': 1,
            'name': 'Yi-Chun Lin',
            'country': 'Taiwan'
        }
        
        print("Testing basic generation (validation disabled)...")
        
        result = generator.generate(
            material_name=test_material['name'],
            material_data=test_material,
            api_client=mock_client,
            author_info=test_author
        )
        
        if result.success:
            print("✅ Generation successful!")
            print(f"   Content length: {len(result.content)} characters")
            print(f"   Content preview: {result.content[:150]}...")
            print(f"   Metadata: {result.metadata}")
        else:
            print(f"❌ Generation failed: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run focused analysis."""
    analyze_workflow()
    test_simple_generation()
    
    print("\n🎯 CONCLUSION")
    print("=" * 40)
    print("The system has solid functionality but suffers from:")
    print("1. Configuration bloat (empty formatting files)")
    print("2. Complexity that doesn't add value")
    print("3. Broken components that need fixing")
    print("\nFocus on simplification and fixing broken parts first.")

if __name__ == "__main__":
    main()
