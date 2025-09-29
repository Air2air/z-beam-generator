#!/usr/bin/env python3
"""
Stage 1: Property Discovery & Inventory
Comprehensive scanning and analysis of all material properties across the system.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import re

class PropertyDiscoverer:
    """
    Discovers and inventories all material properties across frontmatter files,
    Categories.yaml, and Materials.yaml to identify gaps and priorities.
    """
    
    def __init__(self):
        self.frontmatter_dir = Path("content/components/frontmatter")
        self.categories_file = Path("data/Categories.yaml")
        self.materials_file = Path("data/Materials.yaml")
        
        # Property statistics
        self.property_usage = defaultdict(int)
        self.material_coverage = defaultdict(set)
        self.category_coverage = defaultdict(set)
        self.value_types = defaultdict(set)
        
    def scan_frontmatter_files(self, materials_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Scan all frontmatter YAML files to discover properties and their usage patterns.
        
        Args:
            materials_filter: Optional list of specific materials to process
            
        Returns:
            Comprehensive property discovery results
        """
        
        print("🔍 Scanning frontmatter files for property discovery...")
        
        discovered_properties = []
        files_processed = 0
        errors = []
        
        for yaml_file in self.frontmatter_dir.glob("*.yaml"):
            material_name = yaml_file.stem.replace("-laser-cleaning", "")
            
            # Apply materials filter if provided
            if materials_filter and material_name not in materials_filter:
                continue
                
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                material_category = data.get('category', 'unknown').lower()
                material_properties = data.get('materialProperties', {})
                
                # Process each property
                for prop_name, prop_data in material_properties.items():
                    property_info = self._analyze_property(
                        material_name, 
                        material_category, 
                        prop_name, 
                        prop_data
                    )
                    
                    discovered_properties.append(property_info)
                    
                    # Update statistics
                    self.property_usage[prop_name] += 1
                    self.material_coverage[prop_name].add(material_name)
                    self.category_coverage[prop_name].add(material_category)
                    
                    # Track value types
                    if isinstance(prop_data, dict) and 'value' in prop_data:
                        value_type = type(prop_data['value']).__name__
                        self.value_types[prop_name].add(value_type)
                
                files_processed += 1
                
            except Exception as e:
                error_info = f"Error processing {yaml_file}: {e}"
                errors.append(error_info)
                print(f"⚠️  {error_info}")
        
        print(f"✅ Processed {files_processed} frontmatter files")
        print(f"📊 Discovered {len(discovered_properties)} property instances")
        
        return {
            'discovered_properties': discovered_properties,
            'files_processed': files_processed,
            'unique_properties': len(self.property_usage),
            'property_statistics': dict(self.property_usage),
            'material_coverage': {k: list(v) for k, v in self.material_coverage.items()},
            'category_coverage': {k: list(v) for k, v in self.category_coverage.items()},
            'value_types': {k: list(v) for k, v in self.value_types.items()},
            'errors': errors
        }
    
    def _analyze_property(self, material_name: str, category: str, prop_name: str, prop_data: Any) -> Dict[str, Any]:
        """Analyze individual property and extract metadata"""
        
        property_info = {
            'material': material_name,
            'category': category,
            'property': prop_name,
            'original_data': prop_data,
            'data_quality': {}
        }
        
        # Analyze data structure and quality
        if isinstance(prop_data, dict):
            # Extract structured property data
            property_info['value'] = prop_data.get('value')
            property_info['unit'] = prop_data.get('unit')
            property_info['min_range'] = prop_data.get('min')
            property_info['max_range'] = prop_data.get('max')
            property_info['confidence'] = prop_data.get('confidence')
            property_info['description'] = prop_data.get('description')
            
            # Data quality assessment
            property_info['data_quality'] = {
                'has_value': 'value' in prop_data,
                'has_unit': 'unit' in prop_data,
                'has_range': 'min' in prop_data and 'max' in prop_data,
                'has_confidence': 'confidence' in prop_data,
                'has_description': 'description' in prop_data,
                'is_complete': all(k in prop_data for k in ['value', 'unit', 'min', 'max']),
                'value_type': type(prop_data.get('value')).__name__ if 'value' in prop_data else None
            }
            
            # Check for range consistency
            if property_info['value'] is not None and property_info['min_range'] is not None and property_info['max_range'] is not None:
                try:
                    value = float(property_info['value'])
                    min_val = float(property_info['min_range'])
                    max_val = float(property_info['max_range'])
                    property_info['data_quality']['range_consistent'] = min_val <= value <= max_val
                except (ValueError, TypeError):
                    property_info['data_quality']['range_consistent'] = None
        else:
            # Simple value (not structured)
            property_info['value'] = prop_data
            property_info['data_quality'] = {
                'is_simple_value': True,
                'needs_structuring': True,
                'value_type': type(prop_data).__name__
            }
        
        return property_info
    
    def analyze_category_definitions(self) -> Dict[str, Any]:
        """Analyze Categories.yaml for property definitions and standards"""
        
        print("📋 Analyzing Categories.yaml definitions...")
        
        try:
            with open(self.categories_file, 'r') as f:
                categories_data = yaml.safe_load(f)
            
            # Extract property descriptions
            property_descriptions = categories_data.get('materialPropertyDescriptions', {})
            
            # Extract category-specific ranges
            category_ranges = {}
            categories_section = categories_data.get('categories', {})
            
            for category_name, category_info in categories_section.items():
                if 'category_ranges' in category_info:
                    category_ranges[category_name] = category_info['category_ranges']
            
            # Analyze machine settings
            machine_settings = categories_data.get('machineSettingsDescriptions', {})
            
            analysis_results = {
                'property_descriptions_count': len(property_descriptions),
                'property_descriptions': list(property_descriptions.keys()),
                'category_ranges': category_ranges,
                'categories_with_ranges': list(category_ranges.keys()),
                'machine_settings': list(machine_settings.keys()),
                'total_defined_properties': len(property_descriptions) + len(machine_settings)
            }
            
            print(f"✅ Found {len(property_descriptions)} property descriptions")
            print(f"📊 Found ranges for {len(category_ranges)} categories")
            
            return analysis_results
            
        except Exception as e:
            print(f"❌ Error analyzing Categories.yaml: {e}")
            return {'error': str(e)}
    
    def create_property_inventory(self, frontmatter_data: Dict[str, Any], category_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive property inventory with gap analysis"""
        
        print("📊 Creating comprehensive property inventory...")
        
        # Get all unique properties from frontmatter
        frontmatter_properties = set(self.property_usage.keys())
        
        # Get all defined properties from Categories.yaml
        defined_properties = set(category_data.get('property_descriptions', []))
        
        # Identify gaps
        undefined_properties = frontmatter_properties - defined_properties
        unused_definitions = defined_properties - frontmatter_properties
        
        # Analyze completeness by category
        category_completeness = {}
        for category in set().union(*self.category_coverage.values()):
            category_properties = {prop for prop, cats in self.category_coverage.items() if category in cats}
            category_ranges = category_data.get('category_ranges', {}).get(category, {})
            
            category_completeness[category] = {
                'properties_used': len(category_properties),
                'properties_with_ranges': len(set(category_properties) & set(category_ranges.keys())),
                'completeness_rate': len(set(category_properties) & set(category_ranges.keys())) / len(category_properties) if category_properties else 0,
                'missing_ranges': list(category_properties - set(category_ranges.keys())),
                'properties_list': list(category_properties)
            }
        
        # Property usage analysis
        property_analysis = {}
        for prop_name, usage_count in self.property_usage.items():
            total_materials = sum(len(materials) for materials in self.material_coverage.values())
            
            property_analysis[prop_name] = {
                'usage_count': usage_count,
                'material_coverage': len(self.material_coverage[prop_name]),
                'category_coverage': len(self.category_coverage[prop_name]),
                'coverage_rate': usage_count / total_materials if total_materials > 0 else 0,
                'categories': list(self.category_coverage[prop_name]),
                'value_types': list(self.value_types[prop_name]),
                'has_definition': prop_name in defined_properties,
                'priority_score': self._calculate_priority_score(prop_name)
            }
        
        inventory = {
            'summary': {
                'total_properties_discovered': len(frontmatter_properties),
                'total_properties_defined': len(defined_properties),
                'undefined_properties_count': len(undefined_properties),
                'unused_definitions_count': len(unused_definitions),
                'total_materials_scanned': len(set().union(*self.material_coverage.values())),
                'total_categories': len(set().union(*self.category_coverage.values()))
            },
            'gaps': {
                'undefined_properties': list(undefined_properties),
                'unused_definitions': list(unused_definitions),
                'categories_missing_ranges': [cat for cat, info in category_completeness.items() if info['completeness_rate'] < 0.8]
            },
            'category_analysis': category_completeness,
            'property_analysis': property_analysis,
            'recommendations': self._generate_recommendations(property_analysis, category_completeness)
        }
        
        print(f"✅ Inventory complete: {len(frontmatter_properties)} properties analyzed")
        print(f"⚠️  {len(undefined_properties)} properties need definitions")
        print(f"📈 {len(unused_definitions)} definitions not used")
        
        return inventory
    
    def prioritize_properties(self, inventory: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create prioritized processing queue based on importance and impact"""
        
        print("🎯 Creating prioritized processing queue...")
        
        property_analysis = inventory['property_analysis']
        processing_queue = []
        
        # Critical properties that should be prioritized
        critical_properties = {
            'density', 'meltingPoint', 'thermalConductivity', 'hardness', 
            'youngsModulus', 'tensileStrength', 'thermalExpansion'
        }
        
        # Create queue items
        for prop_name, analysis in property_analysis.items():
            for category in analysis['categories']:
                queue_item = {
                    'property': prop_name,
                    'category': category,
                    'priority_score': analysis['priority_score'],
                    'usage_count': analysis['usage_count'],
                    'coverage_rate': analysis['coverage_rate'],
                    'has_definition': analysis['has_definition'],
                    'is_critical': prop_name in critical_properties,
                    'materials': [m for m in self.material_coverage[prop_name] 
                                if m in [mat for mat, cat in self._get_material_categories().items() if cat == category]]
                }
                processing_queue.append(queue_item)
        
        # Sort by priority score (descending)
        processing_queue.sort(key=lambda x: (
            x['is_critical'],           # Critical properties first
            x['priority_score'],        # Then by priority score
            x['usage_count'],          # Then by usage frequency
            x['coverage_rate']         # Then by coverage
        ), reverse=True)
        
        print(f"✅ Created processing queue with {len(processing_queue)} items")
        print(f"🔥 {sum(1 for item in processing_queue if item['is_critical'])} critical properties identified")
        
        return processing_queue
    
    def _calculate_priority_score(self, prop_name: str) -> float:
        """Calculate priority score based on multiple factors"""
        
        # Base factors
        usage_frequency = self.property_usage[prop_name]
        material_coverage = len(self.material_coverage[prop_name])
        category_coverage = len(self.category_coverage[prop_name])
        
        # Critical property bonus
        critical_properties = {
            'density': 1.5, 'meltingPoint': 1.4, 'thermalConductivity': 1.3,
            'hardness': 1.2, 'youngsModulus': 1.2, 'tensileStrength': 1.1
        }
        critical_bonus = critical_properties.get(prop_name, 1.0)
        
        # Data quality factor (properties with more complete data get higher priority)
        data_quality_bonus = 1.0
        if prop_name in self.value_types:
            if 'float' in self.value_types[prop_name] or 'int' in self.value_types[prop_name]:
                data_quality_bonus += 0.2
        
        # Calculate final score
        priority_score = (
            (usage_frequency * 0.3) +
            (material_coverage * 0.25) +
            (category_coverage * 0.25) +
            (critical_bonus * 0.2)
        ) * data_quality_bonus
        
        return round(priority_score, 3)
    
    def _get_material_categories(self) -> Dict[str, str]:
        """Get mapping of materials to their categories from frontmatter"""
        
        material_categories = {}
        
        for yaml_file in self.frontmatter_dir.glob("*.yaml"):
            material_name = yaml_file.stem.replace("-laser-cleaning", "")
            
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                material_categories[material_name] = data.get('category', 'unknown').lower()
            except:
                continue
                
        return material_categories
    
    def _generate_recommendations(self, property_analysis: Dict[str, Any], category_completeness: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        
        recommendations = []
        
        # High-priority missing definitions
        undefined_high_usage = [
            prop for prop, analysis in property_analysis.items() 
            if not analysis['has_definition'] and analysis['usage_count'] > 10
        ]
        
        if undefined_high_usage:
            recommendations.append(
                f"URGENT: Add definitions for high-usage properties: {', '.join(undefined_high_usage[:5])}"
            )
        
        # Categories with low completeness
        low_completeness_categories = [
            cat for cat, info in category_completeness.items() 
            if info['completeness_rate'] < 0.5
        ]
        
        if low_completeness_categories:
            recommendations.append(
                f"Improve range definitions for categories: {', '.join(low_completeness_categories)}"
            )
        
        # Properties with inconsistent data types
        inconsistent_types = [
            prop for prop, types in self.value_types.items() 
            if len(types) > 1 and 'str' in types
        ]
        
        if inconsistent_types:
            recommendations.append(
                f"Standardize data types for: {', '.join(inconsistent_types[:3])}"
            )
        
        # Low coverage properties
        low_coverage = [
            prop for prop, analysis in property_analysis.items()
            if analysis['coverage_rate'] < 0.1 and analysis['usage_count'] > 1
        ]
        
        if low_coverage:
            recommendations.append(
                f"Expand coverage for properties: {', '.join(low_coverage[:3])}"
            )
        
        return recommendations

def main():
    """Test the property discovery functionality"""
    
    discoverer = PropertyDiscoverer()
    
    # Run discovery
    frontmatter_results = discoverer.scan_frontmatter_files()
    category_results = discoverer.analyze_category_definitions()
    
    # Create inventory
    inventory = discoverer.create_property_inventory(frontmatter_results, category_results)
    
    # Create processing queue
    queue = discoverer.prioritize_properties(inventory)
    
    # Save results
    results_dir = Path("pipeline_results")
    results_dir.mkdir(exist_ok=True)
    
    with open(results_dir / "stage1_discovery_results.json", 'w') as f:
        json.dump({
            'frontmatter_scan': frontmatter_results,
            'category_analysis': category_results,
            'property_inventory': inventory,
            'processing_queue': queue[:20]  # Top 20 priorities
        }, f, indent=2, default=str)
    
    print("\n" + "="*60)
    print("🎉 DISCOVERY STAGE COMPLETE")
    print("="*60)
    print(f"Properties discovered: {frontmatter_results['unique_properties']}")
    print(f"Processing queue items: {len(queue)}")
    print(f"Recommendations: {len(inventory['recommendations'])}")
    
    for rec in inventory['recommendations']:
        print(f"  💡 {rec}")

if __name__ == "__main__":
    main()