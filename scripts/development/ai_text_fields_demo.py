#!/usr/bin/env python3
"""
Demo script to display AI-generated text fields for Materials.yaml entries
"""

import yaml
from pathlib import Path

def load_materials():
    """Load materials data"""
    materials_path = Path("data/materials.yaml")
    with open(materials_path, 'r') as f:
        data = yaml.safe_load(f)
        # Materials are under the 'materials' key
        return data.get('materials', {})

def display_ai_text_fields(material_name):
    """Display all AI text fields for a material"""
    materials = load_materials()
    
    if material_name not in materials:
        print(f"❌ Material '{material_name}' not found")
        return
    
    material = materials[material_name]
    ai_fields = material.get('ai_text_fields', {})
    
    if not ai_fields:
        print(f"❌ No ai_text_fields found for {material_name}")
        return
    
    print(f"\n🎯 AI Text Fields for {material_name}")
    print("=" * 60)
    
    # Group fields by category
    standard_fields = [
        'applicationDescription', 'benefitsIntroduction', 'benefitsOutline',
        'compatibilityDescription', 'processOverview', 'qualityStandards',
        'safetyInformation', 'technicalSpecifications', 'usageGuidelines'
    ]
    
    environmental_fields = [
        'environmentalImpact_benefit', 'environmentalImpact_description',
        'environmentalImpact_quantifiedBenefits', 'environmentalImpact_sustainabilityBenefit'
    ]
    
    outcome_fields = [
        'outcomeMetrics_metric', 'outcomeMetrics_description', 'outcomeMetrics_typicalRanges'
    ]
    
    # Display Standard AI Text Fields
    print("\n📋 Standard AI Text Fields:")
    print("-" * 40)
    for field in standard_fields:
        if field in ai_fields:
            data = ai_fields[field]
            content = data.get('content', 'N/A')
            word_count = data.get('word_count', 0)
            char_count = data.get('character_count', 0)
            print(f"\n✅ {field}:")
            print(f"   Content: {content}")
            print(f"   Stats: {word_count} words, {char_count} chars")
    
    # Display Environmental Impact Fields
    print("\n🌱 Environmental Impact AI Text Fields:")
    print("-" * 40)
    for field in environmental_fields:
        if field in ai_fields:
            data = ai_fields[field]
            content = data.get('content', 'N/A')
            word_count = data.get('word_count', 0)
            char_count = data.get('character_count', 0)
            print(f"\n✅ {field}:")
            print(f"   Content: {content}")
            print(f"   Stats: {word_count} words, {char_count} chars")
    
    # Display Outcome Metrics Fields
    print("\n📊 Outcome Metrics AI Text Fields:")
    print("-" * 40)
    for field in outcome_fields:
        if field in ai_fields:
            data = ai_fields[field]
            content = data.get('content', 'N/A')
            word_count = data.get('word_count', 0)
            char_count = data.get('character_count', 0)
            print(f"\n✅ {field}:")
            print(f"   Content: {content}")
            print(f"   Stats: {word_count} words, {char_count} chars")
    
    # Summary
    total_fields = len([f for f in ai_fields if f in standard_fields + environmental_fields + outcome_fields])
    print(f"\n📈 Summary: {total_fields} AI text fields generated")
    print(f"🔧 Configuration: Normalized word counts (15-35 words)")
    print(f"👥 Author Voice: Multi-author rotation for variety")
    print(f"⚡ Generation: AI-researched content, no legacy extraction")

if __name__ == "__main__":
    display_ai_text_fields("Aluminum")