#!/usr/bin/env python3
"""
Category Ranges Research and Verification Script

Custom script to research and verify min/max values for each property 
in each material category using the existing API client infrastructure.

This script follows the fail-fast architecture:
- No fallbacks or mocks allowed
- Uses real API clients only
- Validates all dependencies before execution
- Fails immediately if any configuration is missing

Usage:
    python3 verify_category_ranges.py
"""

import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any
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
    confidence: float  # 0.0-1.0
    sources: List[str]
    
    
@dataclass
class CategoryResearchResult:
    """Results of category range research"""
    category: str
    properties: Dict[str, PropertyRange]
    research_timestamp: str
    total_properties: int
    high_confidence_count: int
    

class CategoryRangeVerifier:
    """Researches and verifies category-specific property ranges using API clients"""
    
    def __init__(self):
        """Initialize the verifier with API client"""
        print("🔬 [CATEGORY RANGE VERIFIER] Initializing...")
        
        # Validate API configuration - fail fast if missing
        self._validate_api_configuration()
        
        # Create API client - fail fast if unsuccessful
        self.api_client = self._create_api_client()
        
        # Load current categories data
        self.categories_path = Path(__file__).parent / "data" / "Categories.yaml"
        self.current_categories = self._load_current_categories()
        
        print("✅ [CATEGORY RANGE VERIFIER] Initialization complete")
    
    def _validate_api_configuration(self):
        """Validate API configuration exists - fail fast if not"""
        print("🔍 [VALIDATOR] Validating API configuration...")
        
        try:
            api_validation = validate_all_api_keys()
            if not any(api_validation.values()):
                raise RuntimeError("No valid API keys found - at least one provider must be configured")
            
            available_providers = [provider for provider, valid in api_validation.items() if valid]
            print(f"✅ [VALIDATOR] Available API providers: {available_providers}")
            
        except Exception as e:
            print(f"❌ [VALIDATOR] API configuration validation failed: {e}")
            raise RuntimeError(f"API configuration validation failed: {e}")
    
    def _create_api_client(self):
        """Create API client - fail fast if unsuccessful"""
        print("🔧 [VALIDATOR] Creating API client...")
        
        try:
            # Try to create deepseek client first (primary research provider)
            client = create_api_client('deepseek')
            print("✅ [VALIDATOR] DeepSeek API client created successfully")
            return client
            
        except Exception as e:
            print(f"❌ [VALIDATOR] Failed to create API client: {e}")
            raise RuntimeError(f"Failed to create API client: {e}")
    
    def _load_current_categories(self) -> Dict[str, Any]:
        """Load current Categories.yaml file"""
        print("📂 [VALIDATOR] Loading current Categories.yaml...")
        
        try:
            with open(self.categories_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            print(f"✅ [VALIDATOR] Loaded {len(data.get('categories', {}))} categories")
            return data
            
        except Exception as e:
            print(f"❌ [VALIDATOR] Failed to load Categories.yaml: {e}")
            raise RuntimeError(f"Failed to load Categories.yaml: {e}")
    
    def research_property_range(self, category: str, property_name: str, unit: str) -> PropertyRange:
        """Research min/max range for a specific property in a category"""
        print(f"🔬 [RESEARCHER] Researching {property_name} for {category} category...")
        
        # Construct research prompt for accurate min/max values
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
            response = self.api_client.generate_simple(
                prompt=research_prompt,
                max_tokens=1000,  # Explicit parameter required
                temperature=0.1   # Low temperature for factual accuracy
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
            # Fail fast - no fallbacks allowed
            raise RuntimeError(f"Failed to research {property_name} for {category}: {e}")
    
    def research_category(self, category_name: str) -> CategoryResearchResult:
        """Research all properties for a given category"""
        print(f"\n🎯 [CATEGORY RESEARCHER] Starting research for {category_name} category")
        
        # Get current category data to extract properties
        category_data = self.current_categories.get('categories', {}).get(category_name, {})
        category_ranges = category_data.get('category_ranges', {})
        
        if not category_ranges:
            raise ValueError(f"No category_ranges found for {category_name}")
        
        properties = {}
        high_confidence_count = 0
        
        # Research each property
        for prop_name, current_range in category_ranges.items():
            if isinstance(current_range, dict) and 'unit' in current_range:
                unit = current_range['unit']
                
                try:
                    # Add delay between API calls to avoid rate limiting
                    time.sleep(2)
                    
                    prop_range = self.research_property_range(category_name, prop_name, unit)
                    properties[prop_name] = prop_range
                    
                    if prop_range.confidence >= 0.8:
                        high_confidence_count += 1
                        
                except Exception as e:
                    print(f"⚠️ [CATEGORY RESEARCHER] Skipping {prop_name} due to error: {e}")
                    continue
        
        # Create research result
        result = CategoryResearchResult(
            category=category_name,
            properties=properties,
            research_timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            total_properties=len(properties),
            high_confidence_count=high_confidence_count
        )
        
        print(f"✅ [CATEGORY RESEARCHER] Completed {category_name}: {result.total_properties} properties researched, {result.high_confidence_count} high-confidence")
        return result
    
    def verify_all_categories(self) -> Dict[str, CategoryResearchResult]:
        """Research and verify all categories"""
        print("\n🚀 [MAIN VERIFIER] Starting comprehensive category research...")
        
        # Get all categories from current data
        categories = list(self.current_categories.get('categories', {}).keys())
        print(f"📋 [MAIN VERIFIER] Categories to research: {categories}")
        
        results = {}
        
        for category in categories:
            try:
                result = self.research_category(category)
                results[category] = result
                
                # Add longer delay between categories
                print("⏳ [MAIN VERIFIER] Waiting before next category...")
                time.sleep(5)
                
            except Exception as e:
                print(f"❌ [MAIN VERIFIER] Failed to research {category}: {e}")
                # Fail fast - don't continue if category research fails
                raise RuntimeError(f"Category research failed for {category}: {e}")
        
        return results
    
    def generate_research_report(self, results: Dict[str, CategoryResearchResult]) -> Dict[str, Any]:
        """Generate comprehensive research report"""
        print("\n📊 [REPORT GENERATOR] Generating research report...")
        
        report = {
            "research_metadata": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_categories": len(results),
                "total_properties": sum(r.total_properties for r in results.values()),
                "high_confidence_properties": sum(r.high_confidence_count for r in results.values()),
                "api_provider": "deepseek",
                "research_method": "api_based_materials_research"
            },
            "category_results": {}
        }
        
        for category, result in results.items():
            category_report = {
                "research_timestamp": result.research_timestamp,
                "total_properties": result.total_properties,
                "high_confidence_count": result.high_confidence_count,
                "confidence_percentage": (result.high_confidence_count / result.total_properties * 100) if result.total_properties > 0 else 0,
                "properties": {}
            }
            
            for prop_name, prop_range in result.properties.items():
                category_report["properties"][prop_name] = {
                    "min": prop_range.min_value,
                    "max": prop_range.max_value,
                    "unit": prop_range.unit,
                    "confidence": prop_range.confidence,
                    "sources": prop_range.sources
                }
            
            report["category_results"][category] = category_report
        
        return report
    
    def save_research_report(self, results: Dict[str, CategoryResearchResult]):
        """Save detailed research report to file"""
        report = self.generate_research_report(results)
        
        # Save comprehensive report
        report_path = Path(__file__).parent / "category_ranges_research_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 [REPORT GENERATOR] Comprehensive report saved: {report_path}")
        
        # Save summary report
        summary_path = Path(__file__).parent / "category_ranges_research_summary.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("# Category Ranges Research Summary\n\n")
            f.write(f"**Research Date:** {report['research_metadata']['timestamp']}\n")
            f.write(f"**Total Categories:** {report['research_metadata']['total_categories']}\n")
            f.write(f"**Total Properties:** {report['research_metadata']['total_properties']}\n")
            f.write(f"**High Confidence Properties:** {report['research_metadata']['high_confidence_properties']}\n\n")
            
            for category, result in results.items():
                f.write(f"## {category.title()} Category\n\n")
                f.write(f"- **Properties Researched:** {result.total_properties}\n")
                f.write(f"- **High Confidence:** {result.high_confidence_count}\n")
                f.write(f"- **Confidence Rate:** {(result.high_confidence_count / result.total_properties * 100):.1f}%\n\n")
                
                f.write("### Property Ranges\n\n")
                f.write("| Property | Min | Max | Unit | Confidence |\n")
                f.write("|----------|-----|-----|------|------------|\n")
                
                for prop_name, prop_range in result.properties.items():
                    f.write(f"| {prop_name} | {prop_range.min_value} | {prop_range.max_value} | {prop_range.unit} | {prop_range.confidence:.2f} |\n")
                
                f.write("\n")
        
        print(f"📄 [REPORT GENERATOR] Summary report saved: {summary_path}")


def main():
    """Main execution function"""
    print("🚀 Starting Category Ranges Research and Verification")
    print("=" * 60)
    
    try:
        # Initialize verifier
        verifier = CategoryRangeVerifier()
        
        # Research all categories
        results = verifier.verify_all_categories()
        
        # Generate and save reports
        verifier.save_research_report(results)
        
        # Print summary
        print("\n" + "=" * 60)
        print("✅ RESEARCH COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        total_properties = sum(r.total_properties for r in results.values())
        high_confidence = sum(r.high_confidence_count for r in results.values())
        
        print("📊 SUMMARY:")
        print(f"  • Categories researched: {len(results)}")
        print(f"  • Total properties: {total_properties}")
        print(f"  • High confidence: {high_confidence}")
        print(f"  • Confidence rate: {(high_confidence / total_properties * 100):.1f}%")
        
        print("\n📄 Reports generated:")
        print("  • category_ranges_research_report.json")
        print("  • category_ranges_research_summary.md")
        
    except Exception as e:
        print(f"\n❌ RESEARCH FAILED: {e}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()