#!/usr/bin/env python3
"""
Demo: Category-Specific Range Validation System

Demonstrates the upgraded min/max value research and verification system
that ensures property ranges represent realistic values within each material's category.
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from research.category_range_researcher import CategoryRangeResearcher


def demo_range_validation():
    """Demonstrate the range validation system"""
    
    print("🔬 CATEGORY-SPECIFIC RANGE VALIDATION DEMO")
    print("=" * 60)
    
    researcher = CategoryRangeResearcher()
    
    # Test materials with different data quality
    test_materials = [
        "aluminum",  # Has some properties
        "Aluminum",            # Missing properties
        "Stainless Steel"      # Check what data exists
    ]
    
    print("\n📊 INDIVIDUAL MATERIAL ANALYSIS")
    print("-" * 40)
    
    for material_name in test_materials:
        print(f"\n🔍 Analyzing: {material_name}")
        
        # Get validation results
        results = researcher.validate_material_ranges(material_name)
        
        # Count status types
        status_counts = {}
        for result in results:
            status = result.validation_status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"  📋 Properties analyzed: {len(results)}")
        for status, count in status_counts.items():
            emoji = {"valid": "✅", "narrow": "📏", "wide": "📐", 
                    "missing": "❌", "invalid": "🚫"}.get(status, "❓")
            print(f"  {emoji} {status.title()}: {count}")
        
        # Show specific examples
        if results:
            example = results[0]
            print(f"  🔬 Example - {example.property_name}:")
            print(f"    Status: {example.validation_status}")
            print(f"    Confidence: {example.confidence_score:.2f}")
            if example.recommendations:
                print(f"    Recommendation: {example.recommendations[0][:80]}...")
    
    print("\n\n📋 CATEGORY ANALYSIS: METALS")
    print("-" * 40)
    
    # Generate metal category report
    metal_report = researcher.generate_category_range_report("metal")
    
    print(f"  🏭 Materials analyzed: {metal_report['materials_analyzed']}")
    print(f"  📊 Total validations: {metal_report['total_validations']}")
    print(f"  🎯 Average confidence: {metal_report['average_confidence']:.2f}")
    
    print("  📈 Status Summary:")
    for status, count in metal_report['status_summary'].items():
        emoji = {"valid": "✅", "narrow": "📏", "wide": "📐", 
                "missing": "❌", "invalid": "🚫"}.get(status, "❓")
        percentage = (count / metal_report['total_validations']) * 100
        print(f"    {emoji} {status.title()}: {count} ({percentage:.1f}%)")
    
    print("\n  🔬 Research Ranges for Metal Category:")
    for prop_name, range_data in metal_report['research_ranges'].items():
        print(f"    {prop_name}: [{range_data['min']:.2f}, {range_data['max']:.2f}] {range_data['unit']}")
        print(f"      Confidence: {range_data['confidence']:.2f}, Sample size: {range_data['sample_size']}")
    
    print("\n\n🚀 CORRECTION SUGGESTIONS")
    print("-" * 40)
    
    # Generate correction suggestions for aluminum
    corrections = researcher.suggest_range_corrections("aluminum")
    
    print(f"  🎯 Material: {corrections['material_name']}")
    print(f"  📊 Data Quality Score: {corrections['data_quality_score']:.2f}")
    print(f"  🔧 Properties needing correction: {corrections['properties_needing_correction']}")
    
    print("  \n🚨 Priority Actions:")
    for action in corrections['priority_actions'][:3]:  # Show top 3
        print(f"    • {action['property']}: {action['current_status']}")
        if 'suggested_range' in action:
            range_info = action['suggested_range']
            print(f"      Suggested: [{range_info['min']:.2f}, {range_info['max']:.2f}] {range_info['unit']}")
            print(f"      Confidence: {range_info['confidence']:.2f}")
    
    print("\n\n📊 RANGE COMPARISON EXAMPLES")
    print("-" * 40)
    
    # Show specific range comparisons
    example_corrections = corrections['corrections'][:2]  # First 2 properties
    
    for correction in example_corrections:
        prop = correction['property']
        print(f"\n  🔬 Property: {prop}")
        print(f"    Status: {correction['current_status']}")
        
        if 'current_range' in correction:
            current = correction['current_range']
            print(f"    Current Range: [{current['min']:.2f}, {current['max']:.2f}]")
            if 'value' in current:
                print(f"    Current Value: {current['value']:.2f}")
        
        if 'suggested_range' in correction:
            suggested = correction['suggested_range']
            print(f"    Category Range: [{suggested['min']:.2f}, {suggested['max']:.2f}] {suggested['unit']}")
            print(f"    Confidence: {suggested['confidence']:.2f}")
        
        if correction['recommendations']:
            print(f"    💡 Recommendation: {correction['recommendations'][0][:100]}...")
    
    print("\n\n🎯 KEY INSIGHTS")
    print("-" * 40)
    print("  1. 🔍 System identifies missing critical properties with high confidence")
    print("  2. 📏 Current ranges often too narrow for category representation")
    print("  3. 📊 Research-based ranges provide realistic category boundaries")
    print("  4. 🎯 Confidence scores help prioritize corrections")
    print("  5. 🚀 Automated suggestions enable systematic data improvement")
    
    print("\n\n📈 VALIDATION BENEFITS")
    print("-" * 40)
    print("  ✅ Ensures properties represent full category diversity")
    print("  📚 Literature-backed ranges with confidence scoring")
    print("  🔧 Identifies specific correction opportunities")
    print("  📊 Statistical validation with outlier detection")
    print("  🎯 Priority-based improvement recommendations")
    
    print("\n✨ Range validation system ready for database updates!")


if __name__ == '__main__':
    demo_range_validation()