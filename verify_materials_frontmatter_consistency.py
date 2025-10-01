#!/usr/bin/env python3
"""
Verify shared values between Materials.yaml and frontmatter files.
Ensures data consistency and integrity across the system.
"""

import yaml
import sys
from pathlib import Path
from collections import defaultdict

def load_materials_yaml():
    """Load and parse Materials.yaml"""
    materials_path = "data/materials.yaml"
    try:
        with open(materials_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Extract materials from category structure under 'materials' key
        materials = []
        materials_section = data.get('materials', {})
        category_keys = ['ceramic', 'composite', 'glass', 'masonry', 'metal', 'plastic', 'semiconductor', 'stone', 'wood']
        
        for category_key in category_keys:
            if category_key in materials_section and isinstance(materials_section[category_key], dict) and 'items' in materials_section[category_key]:
                items = materials_section[category_key]['items']
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict) and 'name' in item:
                            materials.append(item)
        
        print(f"✅ Loaded Materials.yaml with {len(materials)} materials")
        return materials
    except Exception as e:
        print(f"❌ Error loading Materials.yaml: {e}")
        return []

def load_frontmatter_files():
    """Load all frontmatter YAML files"""
    frontmatter_dir = Path("content/components/frontmatter")
    frontmatter_data = {}
    
    if not frontmatter_dir.exists():
        print(f"❌ Frontmatter directory not found: {frontmatter_dir}")
        return {}
    
    yaml_files = list(frontmatter_dir.glob("*.yaml"))
    print(f"📁 Found {len(yaml_files)} frontmatter files")
    
    for yaml_file in yaml_files:
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            material_name = data.get('name', yaml_file.stem.replace('-laser-cleaning', ''))
            frontmatter_data[material_name] = data
            
        except Exception as e:
            print(f"⚠️ Error loading {yaml_file}: {e}")
    
    print(f"✅ Loaded {len(frontmatter_data)} frontmatter files")
    return frontmatter_data

def normalize_material_name(name):
    """Normalize material names for comparison"""
    return name.strip().lower().replace(' ', '').replace('-', '').replace('_', '')

def create_material_lookup(materials):
    """Create lookup dict for materials by normalized name"""
    lookup = {}
    for material in materials:
        normalized = normalize_material_name(material.get('name', ''))
        lookup[normalized] = material
    return lookup

def compare_property_values(materials_data, frontmatter_data):
    """Compare property values between Materials.yaml and frontmatter files"""
    
    # Create normalized lookup for materials
    materials_lookup = create_material_lookup(materials_data)
    
    # Statistics
    stats = {
        'total_comparisons': 0,
        'exact_matches': 0,
        'value_mismatches': 0,
        'missing_in_materials': 0,
        'missing_in_frontmatter': 0,
        'materials_matched': 0,
        'materials_not_found': 0
    }
    
    mismatches = []
    
    print("\n🔍 COMPARING PROPERTY VALUES")
    print("=" * 50)
    
    for fm_name, fm_data in frontmatter_data.items():
        fm_normalized = normalize_material_name(fm_name)
        
        # Find corresponding material in Materials.yaml
        if fm_normalized in materials_lookup:
            material = materials_lookup[fm_normalized]
            stats['materials_matched'] += 1
            
            material_props = material.get('properties', {})
            fm_props = fm_data.get('materialProperties', {})
            
            print(f"\n📋 Comparing {fm_name}:")
            
            # Compare each property in frontmatter
            for prop_name, fm_prop in fm_props.items():
                stats['total_comparisons'] += 1
                
                if prop_name in material_props:
                    mat_value = material_props[prop_name].get('value')
                    fm_value = fm_prop.get('value')
                    
                    # Convert to comparable format
                    try:
                        if isinstance(mat_value, str) and isinstance(fm_value, str):
                            if mat_value.strip() == fm_value.strip():
                                stats['exact_matches'] += 1
                                print(f"  ✅ {prop_name}: MATCH ({mat_value})")
                            else:
                                stats['value_mismatches'] += 1
                                mismatches.append({
                                    'material': fm_name,
                                    'property': prop_name,
                                    'materials_value': mat_value,
                                    'frontmatter_value': fm_value
                                })
                                print(f"  ❌ {prop_name}: MISMATCH (Materials: {mat_value}, Frontmatter: {fm_value})")
                        
                        elif isinstance(mat_value, (int, float)) and isinstance(fm_value, (int, float)):
                            if abs(float(mat_value) - float(fm_value)) < 0.001:  # Allow small floating point differences
                                stats['exact_matches'] += 1
                                print(f"  ✅ {prop_name}: MATCH ({mat_value})")
                            else:
                                stats['value_mismatches'] += 1
                                mismatches.append({
                                    'material': fm_name,
                                    'property': prop_name,
                                    'materials_value': mat_value,
                                    'frontmatter_value': fm_value
                                })
                                print(f"  ❌ {prop_name}: MISMATCH (Materials: {mat_value}, Frontmatter: {fm_value})")
                        
                        else:
                            # Type mismatch
                            stats['value_mismatches'] += 1
                            mismatches.append({
                                'material': fm_name,
                                'property': prop_name,
                                'materials_value': f"{mat_value} ({type(mat_value).__name__})",
                                'frontmatter_value': f"{fm_value} ({type(fm_value).__name__})"
                            })
                            print(f"  ❌ {prop_name}: TYPE MISMATCH (Materials: {mat_value} ({type(mat_value).__name__}), Frontmatter: {fm_value} ({type(fm_value).__name__}))")
                    
                    except Exception as e:
                        print(f"  ⚠️ {prop_name}: ERROR comparing values ({e})")
                
                else:
                    stats['missing_in_materials'] += 1
                    print(f"  ⚠️ {prop_name}: MISSING in Materials.yaml")
            
            # Check for properties in Materials.yaml not in frontmatter
            for prop_name in material_props:
                if prop_name not in fm_props:
                    stats['missing_in_frontmatter'] += 1
                    print(f"  ⚠️ {prop_name}: MISSING in frontmatter")
        
        else:
            stats['materials_not_found'] += 1
            print(f"⚠️ Material '{fm_name}' not found in Materials.yaml")
    
    return stats, mismatches

def compare_metadata_consistency(materials_data, frontmatter_data):
    """Compare metadata consistency (names, categories, etc.)"""
    
    materials_lookup = create_material_lookup(materials_data)
    
    print("\n🏷️ COMPARING METADATA CONSISTENCY")
    print("=" * 50)
    
    metadata_issues = []
    
    for fm_name, fm_data in frontmatter_data.items():
        fm_normalized = normalize_material_name(fm_name)
        
        if fm_normalized in materials_lookup:
            material = materials_lookup[fm_normalized]
            
            # Compare names
            mat_name = material.get('name', '')
            fm_actual_name = fm_data.get('name', '')
            
            if mat_name != fm_actual_name:
                metadata_issues.append({
                    'type': 'name_mismatch',
                    'material': fm_name,
                    'materials_value': mat_name,
                    'frontmatter_value': fm_actual_name
                })
                print(f"❌ {fm_name}: Name mismatch (Materials: '{mat_name}', Frontmatter: '{fm_actual_name}')")
            else:
                print(f"✅ {fm_name}: Name matches")
            
            # Compare categories
            mat_category = material.get('category', '')
            fm_category = fm_data.get('category', '')
            
            if mat_category != fm_category:
                metadata_issues.append({
                    'type': 'category_mismatch',
                    'material': fm_name,
                    'materials_value': mat_category,
                    'frontmatter_value': fm_category
                })
                print(f"❌ {fm_name}: Category mismatch (Materials: '{mat_category}', Frontmatter: '{fm_category}')")
            else:
                print(f"✅ {fm_name}: Category matches")
    
    return metadata_issues

def analyze_source_attribution(materials_data, frontmatter_data):
    """Analyze source attribution and AI research confidence"""
    
    materials_lookup = create_material_lookup(materials_data)
    
    print("\n🔬 ANALYZING SOURCE ATTRIBUTION")
    print("=" * 50)
    
    source_stats = {
        'ai_research_count': 0,
        'other_sources': 0,
        'missing_source': 0,
        'confidence_distribution': defaultdict(int)
    }
    
    for fm_name, fm_data in frontmatter_data.items():
        fm_normalized = normalize_material_name(fm_name)
        
        if fm_normalized in materials_lookup:
            material = materials_lookup[fm_normalized]
            material_props = material.get('properties', {})
            
            print(f"\n📊 Source analysis for {fm_name}:")
            
            for prop_name, prop_data in material_props.items():
                source = prop_data.get('source', 'unknown')
                confidence = prop_data.get('confidence', 0)
                
                if source == 'ai_research':
                    source_stats['ai_research_count'] += 1
                    source_stats['confidence_distribution'][f"{confidence//10*10}-{confidence//10*10+9}%"] += 1
                    print(f"  🤖 {prop_name}: AI research (confidence: {confidence}%)")
                elif source:
                    source_stats['other_sources'] += 1
                    print(f"  📚 {prop_name}: {source}")
                else:
                    source_stats['missing_source'] += 1
                    print(f"  ❓ {prop_name}: No source specified")
    
    return source_stats

def generate_summary_report(stats, mismatches, metadata_issues, source_stats):
    """Generate comprehensive summary report"""
    
    print("\n" + "=" * 60)
    print("📊 MATERIALS.YAML ↔ FRONTMATTER CONSISTENCY REPORT")
    print("=" * 60)
    
    print("\n🔢 PROPERTY VALUE COMPARISON:")
    print(f"  Total comparisons: {stats['total_comparisons']}")
    print(f"  Exact matches: {stats['exact_matches']} ({stats['exact_matches']/max(stats['total_comparisons'],1)*100:.1f}%)")
    print(f"  Value mismatches: {stats['value_mismatches']} ({stats['value_mismatches']/max(stats['total_comparisons'],1)*100:.1f}%)")
    print(f"  Missing in Materials.yaml: {stats['missing_in_materials']}")
    print(f"  Missing in frontmatter: {stats['missing_in_frontmatter']}")
    
    print("\n🏷️ MATERIAL MATCHING:")
    print(f"  Materials matched: {stats['materials_matched']}")
    print(f"  Materials not found: {stats['materials_not_found']}")
    
    print("\n🔬 SOURCE ATTRIBUTION:")
    print(f"  AI research properties: {source_stats['ai_research_count']}")
    print(f"  Other sources: {source_stats['other_sources']}")
    print(f"  Missing source: {source_stats['missing_source']}")
    
    if source_stats['confidence_distribution']:
        print("\n📈 CONFIDENCE DISTRIBUTION:")
        for range_str, count in sorted(source_stats['confidence_distribution'].items()):
            print(f"  {range_str}: {count} properties")
    
    if metadata_issues:
        print(f"\n⚠️ METADATA ISSUES ({len(metadata_issues)}):")
        for issue in metadata_issues[:10]:  # Show first 10
            print(f"  {issue['type']}: {issue['material']}")
    
    if mismatches:
        print(f"\n❌ VALUE MISMATCHES ({len(mismatches)}) - First 10:")
        for mismatch in mismatches[:10]:
            print(f"  {mismatch['material']}.{mismatch['property']}: {mismatch['materials_value']} → {mismatch['frontmatter_value']}")
    
    # Overall assessment
    if stats['total_comparisons'] > 0:
        match_percentage = stats['exact_matches'] / stats['total_comparisons'] * 100
        
        if match_percentage >= 95:
            print(f"\n🎉 OVERALL ASSESSMENT: EXCELLENT ({match_percentage:.1f}% match rate)")
        elif match_percentage >= 85:
            print(f"\n✅ OVERALL ASSESSMENT: GOOD ({match_percentage:.1f}% match rate)")
        elif match_percentage >= 70:
            print(f"\n⚠️ OVERALL ASSESSMENT: NEEDS ATTENTION ({match_percentage:.1f}% match rate)")
        else:
            print(f"\n❌ OVERALL ASSESSMENT: CRITICAL ISSUES ({match_percentage:.1f}% match rate)")
    
    return match_percentage if stats['total_comparisons'] > 0 else 0

def main():
    """Main verification function"""
    print("🔍 MATERIALS.YAML ↔ FRONTMATTER CONSISTENCY VERIFICATION")
    print("=" * 60)
    
    # Load data
    materials_data = load_materials_yaml()
    frontmatter_data = load_frontmatter_files()
    
    if not materials_data:
        print("❌ Cannot proceed without Materials.yaml data")
        return False
    
    if not frontmatter_data:
        print("❌ Cannot proceed without frontmatter data")
        return False
    
    # Perform comparisons
    stats, mismatches = compare_property_values(materials_data, frontmatter_data)
    metadata_issues = compare_metadata_consistency(materials_data, frontmatter_data)
    source_stats = analyze_source_attribution(materials_data, frontmatter_data)
    
    # Generate report
    match_percentage = generate_summary_report(stats, mismatches, metadata_issues, source_stats)
    
    # Return success based on match percentage
    return match_percentage >= 85

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)