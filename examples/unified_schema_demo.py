#!/usr/bin/env python3
"""
Unified Schema DataMetric Pattern Demo

Demonstrates the power of the reusable DataMetric pattern where:
1. Field names serve as keys (density, wavelength, power, etc.)
2. Each field uses the same comprehensive DataMetric structure
3. Confidence scores are directly accessible
4. Rich validation metadata provides research backing
"""

import json
from pathlib import Path

def demonstrate_datametric_pattern():
    """Show how the unified DataMetric pattern works in practice"""
    
    print("🏗️  UNIFIED SCHEMA DATAMETRIC PATTERN DEMONSTRATION")
    print("=" * 65)
    
    # Load the test data
    test_data_path = Path(__file__).parent.parent / "test_unified_schema_data.json"
    
    try:
        with open(test_data_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Test data not found - run from project root")
        return
    
    print("📊 MATERIAL PROPERTIES (using field names as keys):")
    print("-" * 50)
    
    properties = data.get('properties', {})
    for field_name, metric_data in properties.items():
        print(f"🔬 {field_name}:")
        print(f"   Value: {metric_data.get('value')} {metric_data.get('unit')}")
        print(f"   Confidence: {metric_data.get('confidence_score', 'N/A')}")
        print(f"   Sources: {metric_data.get('validation', {}).get('sources_validated', 'N/A')}")
        print(f"   Impact: {metric_data.get('processing_impact', 'Not specified')[:80]}...")
        print()
    
    print("⚙️  MACHINE SETTINGS (using field names as keys):")
    print("-" * 50)
    
    machine_settings = data.get('machineSettings', {})
    for field_name, metric_data in machine_settings.items():
        print(f"🔧 {field_name}:")
        print(f"   Value: {metric_data.get('value')} {metric_data.get('unit')}")
        print(f"   Range: {metric_data.get('min')}-{metric_data.get('max')} {metric_data.get('unit')}")
        print(f"   Confidence: {metric_data.get('confidence_score', 'N/A')}")
        print(f"   Notes: {metric_data.get('optimization_notes', 'Not specified')[:80]}...")
        print()
    
    print("✨ BENEFITS OF UNIFIED DATAMETRIC PATTERN:")
    print("-" * 50)
    print("1. 🔑 Field names serve as intuitive keys (density, wavelength, power)")
    print("2. 📏 Consistent structure for all numeric data across properties and settings")
    print("3. 🎯 Direct access to confidence scores without nested lookup")
    print("4. 📚 Rich validation metadata with research sources and methods")
    print("5. 🔄 Reusable pattern reduces schema complexity and maintenance")
    print("6. 🧠 Perfect for AI material prompting with standardized data access")
    
    # Show how easy it is to access data programmatically
    print("\n💻 PROGRAMMATIC ACCESS EXAMPLE:")
    print("-" * 50)
    
    # Get density data
    density = properties.get('density', {})
    print(f"Density confidence: {density.get('confidence_score', 0)}")
    print(f"Density validation sources: {density.get('validation', {}).get('sources_validated', 0)}")
    
    # Get wavelength data
    wavelength = machine_settings.get('wavelength', {})
    print(f"Wavelength optimization: {wavelength.get('optimization_notes', 'N/A')[:100]}")
    
    print("\n🚀 Ready for material prompting and AI generation!")

if __name__ == "__main__":
    demonstrate_datametric_pattern()