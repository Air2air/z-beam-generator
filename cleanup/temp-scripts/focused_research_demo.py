#!/usr/bin/env python3
"""
Focused Category Ranges Research - Demo Version

Quick research of a few key properties to demonstrate the verification system
and produce sample results for validation.
"""

import sys
import json
import yaml
from pathlib import Path
from typing import List
from dataclasses import dataclass
import time

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import API infrastructure
from api.client_factory import create_api_client
from api.key_manager import validate_all_api_keys


@dataclass
class PropertyRange:
    """Represents a researched property range"""
    property_name: str
    category: str
    min_value: float
    max_value: float
    unit: str
    confidence: float
    sources: List[str]


def research_property_range(api_client, category: str, property_name: str, unit: str) -> PropertyRange:
    """Research min/max range for a specific property in a category"""
    print(f"🔬 [RESEARCHER] Researching {property_name} for {category} category...")
    
    research_prompt = f"""You are a materials science expert researching property ranges for laser cleaning applications.

TASK: Provide accurate minimum and maximum values for the property "{property_name}" within the "{category}" material category.

REQUIREMENTS:
1. Consider ONLY materials that fall within the "{category}" category
2. Provide realistic min/max values based on actual materials science data
3. Focus on materials commonly used in industrial laser cleaning applications
4. Express values as numbers only (no ranges like "10-20")
5. Unit must be: {unit}

CATEGORY: {category}
PROPERTY: {property_name}
UNIT: {unit}

Please research and provide:
1. MINIMUM value (lowest realistic value for this property in this category)
2. MAXIMUM value (highest realistic value for this property in this category)
3. Brief explanation of materials representing these extremes
4. Confidence level (0.0-1.0) in your research

Format your response as JSON:
{{
    "min_value": <number>,
    "max_value": <number>,
    "unit": "{unit}",
    "min_material_example": "<material name>",
    "max_material_example": "<material name>",
    "confidence": <0.0-1.0>,
    "sources": ["<source1>", "<source2>"]
}}

IMPORTANT: Values must be realistic for the {category} category and suitable for laser cleaning applications."""

    try:
        # Make API request using correct interface
        response = api_client.generate_simple(
            prompt=research_prompt,
            max_tokens=1000,
            temperature=0.1
        )
        
        if not response or not response.success or not response.content:
            error_msg = response.error if response else "Unknown API error"
            raise ValueError(f"API request failed for {property_name}: {error_msg}")
        
        # Parse JSON response
        try:
            research_data = json.loads(response.content)
        except json.JSONDecodeError:
            # Try to extract JSON from response if wrapped in text
            content = response.content
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                research_data = json.loads(content[start_idx:end_idx])
            else:
                raise ValueError(f"Could not parse JSON from API response for {property_name}")
        
        # Validate required fields
        required_fields = ['min_value', 'max_value', 'confidence']
        for field in required_fields:
            if field not in research_data:
                raise ValueError(f"Missing required field '{field}' in API response")
        
        # Create PropertyRange object
        prop_range = PropertyRange(
            property_name=property_name,
            category=category,
            min_value=float(research_data['min_value']),
            max_value=float(research_data['max_value']),
            unit=unit,
            confidence=float(research_data.get('confidence', 0.8)),
            sources=research_data.get('sources', ['API Research'])
        )
        
        print(f"✅ [RESEARCHER] {property_name}: {prop_range.min_value}-{prop_range.max_value} {unit} (confidence: {prop_range.confidence:.2f})")
        return prop_range
        
    except Exception as e:
        print(f"❌ [RESEARCHER] Failed to research {property_name}: {e}")
        raise RuntimeError(f"Failed to research {property_name} for {category}: {e}")


def main():
    """Main execution function - focused research"""
    print("🚀 Starting Focused Category Ranges Research")
    print("=" * 50)
    
    try:
        # Validate API and create client
        print("🔍 Validating API configuration...")
        api_validation = validate_all_api_keys()
        if not any(api_validation.values()):
            raise RuntimeError("No valid API keys found")
        
        print("🔧 Creating API client...")
        api_client = create_api_client('deepseek')
        
        # Load current categories
        print("📂 Loading Categories.yaml...")
        categories_path = Path(__file__).parent / "data" / "Categories.yaml"
        with open(categories_path, 'r', encoding='utf-8') as f:
            categories_data = yaml.safe_load(f)
        
        categories = categories_data.get('categories', {})
        print(f"✅ Loaded {len(categories)} categories")
        
        # Focus on key properties from 3 categories for demonstration
        focus_research = {
            'ceramic': ['density', 'hardness', 'thermalConductivity'],
            'metal': ['density', 'thermalConductivity', 'tensileStrength'], 
            'wood': ['density', 'hardness', 'thermalConductivity']
        }
        
        results = {}
        
        print("\\n🎯 Starting focused research...")
        for category, properties in focus_research.items():
            print(f"\\n🔬 Researching {category} category...")
            category_results = {}
            
            if category in categories:
                category_ranges = categories[category].get('category_ranges', {})
                
                for prop_name in properties:
                    if prop_name in category_ranges:
                        range_data = category_ranges[prop_name]
                        if isinstance(range_data, dict) and 'unit' in range_data:
                            unit = range_data['unit']
                            
                            try:
                                # Add delay between requests
                                if len(category_results) > 0:
                                    time.sleep(3)
                                
                                prop_range = research_property_range(api_client, category, prop_name, unit)
                                category_results[prop_name] = prop_range
                                
                            except Exception as e:
                                print(f"⚠️ Skipping {prop_name} due to error: {e}")
                                continue
            
            results[category] = category_results
            
            # Longer delay between categories
            if len(results) < len(focus_research):
                print("⏳ Pausing before next category...")
                time.sleep(5)
        
        # Generate summary report
        print("\\n" + "=" * 50)
        print("✅ FOCUSED RESEARCH COMPLETED")
        print("=" * 50)
        
        # Save results
        report = {
            "research_metadata": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "research_type": "focused_demonstration",
                "api_provider": "deepseek"
            },
            "results": {}
        }
        
        print("\\n📊 RESEARCH RESULTS:")
        
        for category, category_results in results.items():
            print(f"\\n🏷️ {category.upper()} Category:")
            category_summary = {}
            
            for prop_name, prop_range in category_results.items():
                current_range = categories[category]['category_ranges'][prop_name]
                current_min = current_range.get('min', 'N/A')
                current_max = current_range.get('max', 'N/A') 
                
                print(f"  • {prop_name}:")
                print(f"    Current:    {current_min} - {current_max} {prop_range.unit}")
                print(f"    Researched: {prop_range.min_value} - {prop_range.max_value} {prop_range.unit}")
                print(f"    Confidence: {prop_range.confidence:.2f}")
                
                # Check if research suggests changes
                if current_min != prop_range.min_value or current_max != prop_range.max_value:
                    print("    🔍 DIFFERENCE DETECTED - May need update")
                else:
                    print("    ✅ Values match current data")
                
                category_summary[prop_name] = {
                    "current": {"min": current_min, "max": current_max},
                    "researched": {"min": prop_range.min_value, "max": prop_range.max_value},
                    "unit": prop_range.unit,
                    "confidence": prop_range.confidence,
                    "needs_update": current_min != prop_range.min_value or current_max != prop_range.max_value
                }
            
            report["results"][category] = category_summary
        
        # Save report
        report_path = Path(__file__).parent / "focused_research_results.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\\n📄 Report saved: {report_path}")
        
        # Summary statistics
        total_properties = sum(len(cat_results) for cat_results in results.values())
        high_confidence = sum(
            1 for cat_results in results.values() 
            for prop in cat_results.values() 
            if prop.confidence >= 0.8
        )
        
        print("\\n📈 SUMMARY:")
        print(f"  • Categories researched: {len(results)}")
        print(f"  • Properties researched: {total_properties}")
        print(f"  • High confidence (≥0.8): {high_confidence}")
        print(f"  • Confidence rate: {(high_confidence/total_properties*100):.1f}%")
        
    except Exception as e:
        print(f"\\n❌ RESEARCH FAILED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()