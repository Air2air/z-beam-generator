#!/usr/bin/env python3
"""
Regulatory Standards Redundancy Analysis

This script analyzes redundancy between Categories.yaml regulatory standards
and material-specific regulatory standards to identify consolidation opportunities.
"""

import yaml
import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

def analyze_regulatory_standards_redundancy():
    """Analyze regulatory standards redundancy across Categories and Materials."""
    
    print("🔍 REGULATORY STANDARDS REDUNDANCY ANALYSIS")
    print("=" * 60)
    
    # Load Categories.yaml
    categories_file = Path("data/Categories.yaml")
    if not categories_file.exists():
        print("❌ Categories.yaml not found")
        return
        
    with open(categories_file, 'r', encoding='utf-8') as f:
        categories_data = yaml.safe_load(f)
    
    # Load materials.yaml  
    materials_file = Path("data/materials.yaml")
    if not materials_file.exists():
        print("❌ materials.yaml not found")
        return
        
    with open(materials_file, 'r', encoding='utf-8') as f:
        materials_data = yaml.safe_load(f)
    
    print(f"📂 Loaded {len(categories_data)} categories")
    print(f"📂 Loaded {len(materials_data)} materials")
    
    # Extract regulatory standards from categories
    category_regulatory = {}
    category_regulatory_count = 0
    
    for category_name, category_data in categories_data.items():
        if isinstance(category_data, dict):
            # Check for regulatory standards in various locations
            regulatory_standards = []
            
            # Check universal_regulatory_standards (if exists)
            if 'universal_regulatory_standards' in category_data:
                universal = category_data['universal_regulatory_standards']
                if isinstance(universal, list):
                    regulatory_standards.extend(universal)
                    category_regulatory_count += len(universal)
            
            # Check regulatoryStandards in category
            if 'regulatoryStandards' in category_data:
                reg_std = category_data['regulatoryStandards']
                if isinstance(reg_std, list):
                    regulatory_standards.extend(reg_std)
                    category_regulatory_count += len(reg_std)
            
            # Check nested regulatory standards
            for key, value in category_data.items():
                if isinstance(value, dict) and 'regulatoryStandards' in value:
                    nested_reg = value['regulatoryStandards']
                    if isinstance(nested_reg, list):
                        regulatory_standards.extend(nested_reg)
                        category_regulatory_count += len(nested_reg)
            
            if regulatory_standards:
                category_regulatory[category_name] = regulatory_standards
    
    print(f"📊 Category regulatory standards: {category_regulatory_count} total entries")
    
    # Extract regulatory standards from materials
    material_regulatory = {}
    material_regulatory_count = 0
    material_category_mapping = {}
    
    for material_name, material_data in materials_data.items():
        if isinstance(material_data, dict):
            material_category = material_data.get('category', 'unknown')
            material_category_mapping[material_name] = material_category
            
            regulatory_standards = []
            
            # Check material_metadata.regulatoryStandards
            if 'material_metadata' in material_data:
                metadata = material_data['material_metadata']
                if isinstance(metadata, dict) and 'regulatoryStandards' in metadata:
                    reg_std = metadata['regulatoryStandards']
                    if isinstance(reg_std, list):
                        regulatory_standards.extend(reg_std)
                        material_regulatory_count += len(reg_std)
            
            # Check direct regulatoryStandards
            if 'regulatoryStandards' in material_data:
                reg_std = material_data['regulatoryStandards']
                if isinstance(reg_std, list):
                    regulatory_standards.extend(reg_std)
                    material_regulatory_count += len(reg_std)
            
            if regulatory_standards:
                material_regulatory[material_name] = regulatory_standards
    
    print(f"📊 Material regulatory standards: {material_regulatory_count} total entries")
    
    # Analyze redundancy patterns
    print(f"\n🔍 REDUNDANCY ANALYSIS:")
    
    # Count regulatory standards by frequency
    all_regulatory_standards = []
    regulatory_standard_sources = defaultdict(list)
    
    # Add category standards
    for category, standards in category_regulatory.items():
        for standard in standards:
            all_regulatory_standards.append(standard)
            regulatory_standard_sources[standard].append(f"category:{category}")
    
    # Add material standards
    for material, standards in material_regulatory.items():
        for standard in standards:
            all_regulatory_standards.append(standard)
            regulatory_standard_sources[standard].append(f"material:{material}")
    
    regulatory_frequency = Counter(all_regulatory_standards)
    total_regulatory_entries = len(all_regulatory_standards)
    
    print(f"📈 Total regulatory standard entries across system: {total_regulatory_entries:,}")
    print(f"📈 Unique regulatory standards: {len(regulatory_frequency):,}")
    
    # Identify redundant standards (appearing in multiple places)
    redundant_standards = {std: count for std, count in regulatory_frequency.items() if count > 1}
    redundant_entries = sum(count - 1 for count in redundant_standards.values())  # Subtract 1 to keep one copy
    
    print(f"🔄 Redundant regulatory standards: {len(redundant_standards):,}")
    print(f"🔄 Redundant entries that could be eliminated: {redundant_entries:,}")
    
    if total_regulatory_entries > 0:
        redundancy_percentage = (redundant_entries / total_regulatory_entries) * 100
        print(f"📊 Regulatory redundancy rate: {redundancy_percentage:.1f}%")
    else:
        redundancy_percentage = 0
        print("📊 No regulatory standards found")
    
    # Analyze category vs material inheritance potential
    print(f"\n🏗️ INHERITANCE ANALYSIS:")
    
    category_material_matches = 0
    total_material_standards = 0
    inheritance_opportunities = defaultdict(list)
    
    for material, standards in material_regulatory.items():
        material_category = material_category_mapping.get(material, 'unknown')
        category_standards = category_regulatory.get(material_category, [])
        
        total_material_standards += len(standards)
        
        # Check if material standards could inherit from category
        for standard in standards:
            if standard in category_standards:
                category_material_matches += 1
                inheritance_opportunities[material_category].append(material)
    
    if total_material_standards > 0:
        inheritance_rate = (category_material_matches / total_material_standards) * 100
        print(f"📈 Materials that could inherit from category: {category_material_matches:,}/{total_material_standards:,} ({inheritance_rate:.1f}%)")
    
    # Show top redundant standards
    print(f"\n🔝 TOP REDUNDANT REGULATORY STANDARDS:")
    top_redundant = sorted(redundant_standards.items(), key=lambda x: x[1], reverse=True)[:10]
    
    for standard, count in top_redundant:
        sources = regulatory_standard_sources[standard]
        category_sources = [s for s in sources if s.startswith('category:')]
        material_sources = [s for s in sources if s.startswith('material:')]
        
        print(f"   • {standard}")
        print(f"     Appears {count}x: {len(category_sources)} categories, {len(material_sources)} materials")
    
    # Category-by-category analysis
    print(f"\n📋 CATEGORY ANALYSIS:")
    category_optimization_potential = {}
    
    for category in category_regulatory.keys():
        category_standards = set(category_regulatory[category])
        materials_in_category = [m for m, c in material_category_mapping.items() if c == category]
        
        materials_with_regulatory = [m for m in materials_in_category if m in material_regulatory]
        
        eliminatable_standards = 0
        for material in materials_with_regulatory:
            material_standards = set(material_regulatory[material])
            # Standards that exist in both category and material (could be eliminated from material)
            overlap = material_standards.intersection(category_standards)
            eliminatable_standards += len(overlap)
        
        category_optimization_potential[category] = {
            'materials_count': len(materials_in_category),
            'materials_with_regulatory': len(materials_with_regulatory),
            'category_standards': len(category_standards),
            'eliminatable_standards': eliminatable_standards
        }
        
        if eliminatable_standards > 0:
            print(f"   📁 {category}:")
            print(f"      Materials: {len(materials_with_regulatory)}/{len(materials_in_category)} with regulatory standards")
            print(f"      Eliminatable entries: {eliminatable_standards}")
    
    # Generate consolidation recommendation
    total_eliminatable = sum(data['eliminatable_standards'] for data in category_optimization_potential.values())
    
    print(f"\n💡 CONSOLIDATION RECOMMENDATION:")
    print(f"   🎯 Estimated eliminatable entries: {total_eliminatable:,}")
    print(f"   📊 Potential reduction: {(total_eliminatable/total_regulatory_entries)*100:.1f}%" if total_regulatory_entries > 0 else "   📊 No regulatory standards to optimize")
    print(f"   🏗️ Recommended approach: Category-level regulatory inheritance")
    
    # Save analysis results
    analysis_results = {
        "analysis_timestamp": datetime.now().isoformat(),
        "regulatory_standards_analysis": {
            "total_entries": total_regulatory_entries,
            "unique_standards": len(regulatory_frequency),
            "redundant_standards_count": len(redundant_standards),
            "redundant_entries": redundant_entries,
            "redundancy_percentage": redundancy_percentage,
            "category_standards_count": category_regulatory_count,
            "material_standards_count": material_regulatory_count
        },
        "inheritance_analysis": {
            "category_material_matches": category_material_matches,
            "total_material_standards": total_material_standards,
            "inheritance_rate_percentage": inheritance_rate if total_material_standards > 0 else 0
        },
        "consolidation_potential": {
            "total_eliminatable_entries": total_eliminatable,
            "potential_reduction_percentage": (total_eliminatable/total_regulatory_entries)*100 if total_regulatory_entries > 0 else 0,
            "category_optimization": category_optimization_potential
        },
        "top_redundant_standards": dict(top_redundant),
        "regulatory_standard_sources": dict(regulatory_standard_sources)
    }
    
    # Save detailed report
    report_file = "regulatory_standards_redundancy_analysis.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed analysis saved to: {report_file}")
    
    return analysis_results

if __name__ == "__main__":
    analyze_regulatory_standards_redundancy()