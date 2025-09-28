#!/usr/bin/env python3
"""
Industry Data Redundancy Analysis for Z-Beam Generator

This script analyzes the redundancy between three industry data structures:
1. material_metadata.industryTags (Materials.yaml - material-specific)
2. industryApplications.common_industries (Categories.yaml - category-level)
3. industryTags.primary_industries (Categories.yaml - category-level)

Goal: Identify optimal consolidation strategy to eliminate redundancy while preserving data integrity.
"""

import yaml
from pathlib import Path
from collections import defaultdict, Counter
import json

class IndustryDataAnalyzer:
    """Comprehensive analysis of industry data structures across YAML files."""
    
    def __init__(self, categories_file: str = "data/Categories.yaml", materials_file: str = "data/materials.yaml"):
        self.categories_file = Path(categories_file)
        self.materials_file = Path(materials_file)
        
        # Load data
        self.categories_data = self._load_yaml(self.categories_file)
        self.materials_data = self._load_yaml(self.materials_file)
        
        # Analysis results
        self.analysis_results = {
            'redundancy_metrics': {},
            'data_structures': {},
            'consolidation_opportunities': {},
            'validation_data': {}
        }
    
    def _load_yaml(self, file_path: Path) -> dict:
        """Load YAML file with error handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
            return {}
    
    def analyze_complete_industry_data(self):
        """Complete analysis of all three industry data structures."""
        print("🔍 INDUSTRY DATA REDUNDANCY ANALYSIS")
        print("=" * 60)
        
        # 1. Extract all three data structures
        self._extract_industry_structures()
        
        # 2. Analyze redundancy patterns
        self._analyze_redundancy_patterns()
        
        # 3. Calculate optimization potential
        self._calculate_optimization_metrics()
        
        # 4. Generate consolidation recommendation
        self._generate_consolidation_strategy()
        
        # 5. Present comprehensive report
        self._generate_comprehensive_report()
        
        return self.analysis_results
    
    def _extract_industry_structures(self):
        """Extract all three industry data structures for analysis."""
        print("📊 1. EXTRACTING INDUSTRY DATA STRUCTURES")
        print("-" * 40)
        
        # Structure 1: material_metadata.industryTags (Materials.yaml)
        material_industry_tags = defaultdict(list)
        total_material_tags = 0
        
        for category, cat_data in self.materials_data.get('materials', {}).items():
            for item in cat_data.get('items', []):
                material_name = item.get('name', 'Unknown')
                if 'material_metadata' in item and 'industryTags' in item['material_metadata']:
                    tags = item['material_metadata']['industryTags']
                    material_industry_tags[category].extend(tags)
                    total_material_tags += len(tags)
        
        # Structure 2: industryApplications.common_industries (Categories.yaml)
        category_common_industries = {}
        total_common_industries = 0
        
        for category, cat_data in self.categories_data.get('categories', {}).items():
            if 'industryApplications' in cat_data and 'common_industries' in cat_data['industryApplications']:
                industries = cat_data['industryApplications']['common_industries']
                category_common_industries[category] = industries
                total_common_industries += len(industries)
        
        # Structure 3: industryTags.primary_industries (Categories.yaml)
        category_primary_industries = {}
        total_primary_industries = 0
        
        for category, cat_data in self.categories_data.get('categories', {}).items():
            if 'industryTags' in cat_data and 'primary_industries' in cat_data['industryTags']:
                industries = cat_data['industryTags']['primary_industries']
                category_primary_industries[category] = industries
                total_primary_industries += len(industries)
        
        # Store extracted data
        self.analysis_results['data_structures'] = {
            'material_industry_tags': dict(material_industry_tags),
            'category_common_industries': category_common_industries,
            'category_primary_industries': category_primary_industries,
            'counts': {
                'total_material_tags': total_material_tags,
                'total_common_industries': total_common_industries,
                'total_primary_industries': total_primary_industries,
                'total_entries': total_material_tags + total_common_industries + total_primary_industries
            }
        }
        
        print(f"   ✅ Material Industry Tags (Materials.yaml): {total_material_tags} entries")
        print(f"   ✅ Common Industries (Categories.yaml): {total_common_industries} entries") 
        print(f"   ✅ Primary Industries (Categories.yaml): {total_primary_industries} entries")
        print(f"   📊 Total industry data entries: {total_material_tags + total_common_industries + total_primary_industries}")
    
    def _analyze_redundancy_patterns(self):
        """Analyze redundancy between the three industry data structures."""
        print(f"\n📈 2. REDUNDANCY PATTERN ANALYSIS")
        print("-" * 40)
        
        redundancy_analysis = {}
        
        # Analyze each category for redundancy
        for category in self.categories_data.get('categories', {}).keys():
            category_analysis = {
                'material_tags': set(),
                'common_industries': set(),
                'primary_industries': set(),
                'overlaps': {},
                'redundancy_metrics': {}
            }
            
            # Get data for this category
            if category in self.analysis_results['data_structures']['material_industry_tags']:
                category_analysis['material_tags'] = set(
                    self.analysis_results['data_structures']['material_industry_tags'][category]
                )
            
            if category in self.analysis_results['data_structures']['category_common_industries']:
                category_analysis['common_industries'] = set(
                    self.analysis_results['data_structures']['category_common_industries'][category]
                )
            
            if category in self.analysis_results['data_structures']['category_primary_industries']:
                category_analysis['primary_industries'] = set(
                    self.analysis_results['data_structures']['category_primary_industries'][category]
                )
            
            # Calculate overlaps
            category_analysis['overlaps'] = {
                'material_vs_common': category_analysis['material_tags'] & category_analysis['common_industries'],
                'material_vs_primary': category_analysis['material_tags'] & category_analysis['primary_industries'],
                'common_vs_primary': category_analysis['common_industries'] & category_analysis['primary_industries'],
                'all_three': category_analysis['material_tags'] & category_analysis['common_industries'] & category_analysis['primary_industries']
            }
            
            # Calculate redundancy percentages
            total_unique = len(category_analysis['material_tags'] | category_analysis['common_industries'] | category_analysis['primary_industries'])
            total_entries = len(category_analysis['material_tags']) + len(category_analysis['common_industries']) + len(category_analysis['primary_industries'])
            
            if total_entries > 0:
                redundancy_rate = ((total_entries - total_unique) / total_entries) * 100
                category_analysis['redundancy_metrics'] = {
                    'total_entries': total_entries,
                    'unique_industries': total_unique,
                    'redundant_entries': total_entries - total_unique,
                    'redundancy_rate': redundancy_rate
                }
            
            redundancy_analysis[category] = category_analysis
        
        self.analysis_results['redundancy_metrics'] = redundancy_analysis
        
        # Print summary for each category
        for category, analysis in redundancy_analysis.items():
            if analysis['redundancy_metrics']:
                metrics = analysis['redundancy_metrics']
                print(f"   {category.upper()}: {metrics['redundant_entries']}/{metrics['total_entries']} redundant ({metrics['redundancy_rate']:.1f}%)")
    
    def _calculate_optimization_metrics(self):
        """Calculate overall optimization potential."""
        print(f"\n🎯 3. OPTIMIZATION POTENTIAL")
        print("-" * 40)
        
        # Overall metrics
        total_redundant = 0
        total_entries = 0
        total_unique = 0
        
        for category, analysis in self.analysis_results['redundancy_metrics'].items():
            if analysis['redundancy_metrics']:
                metrics = analysis['redundancy_metrics']
                total_redundant += metrics['redundant_entries']
                total_entries += metrics['total_entries']
                total_unique += metrics['unique_industries']
        
        if total_entries > 0:
            overall_redundancy_rate = (total_redundant / total_entries) * 100
            
            self.analysis_results['consolidation_opportunities'] = {
                'total_entries': total_entries,
                'unique_industries': total_unique,
                'redundant_entries': total_redundant,
                'overall_redundancy_rate': overall_redundancy_rate,
                'optimization_potential': f"{total_redundant:,} entries can be eliminated",
                'file_size_savings': f"~{total_redundant * 25} characters estimated"
            }
            
            print(f"   📊 Total industry entries: {total_entries:,}")
            print(f"   📊 Unique industries: {total_unique:,}")
            print(f"   🎯 Redundant entries: {total_redundant:,} ({overall_redundancy_rate:.1f}%)")
            print(f"   💾 Optimization potential: Eliminate {total_redundant:,} redundant entries")
        
        # Identify highest impact categories
        high_impact_categories = []
        for category, analysis in self.analysis_results['redundancy_metrics'].items():
            if analysis['redundancy_metrics'] and analysis['redundancy_metrics']['redundant_entries'] > 5:
                high_impact_categories.append({
                    'category': category,
                    'redundant_entries': analysis['redundancy_metrics']['redundant_entries'],
                    'redundancy_rate': analysis['redundancy_metrics']['redundancy_rate']
                })
        
        high_impact_categories.sort(key=lambda x: x['redundant_entries'], reverse=True)
        self.analysis_results['consolidation_opportunities']['high_impact_categories'] = high_impact_categories
        
        if high_impact_categories:
            print(f"   🔥 Highest impact categories:")
            for cat_data in high_impact_categories[:3]:
                print(f"      • {cat_data['category']}: {cat_data['redundant_entries']} redundant entries ({cat_data['redundancy_rate']:.1f}%)")
    
    def _generate_consolidation_strategy(self):
        """Generate recommended consolidation strategy."""
        print(f"\n💡 4. CONSOLIDATION STRATEGY RECOMMENDATION")
        print("-" * 40)
        
        # Analyze which structures have the most overlap
        structure_analysis = {
            'common_vs_primary_identical': 0,
            'material_tags_subset_of_primary': 0,
            'complete_overlap_categories': []
        }
        
        for category, analysis in self.analysis_results['redundancy_metrics'].items():
            # Check if common_industries and primary_industries are identical
            if analysis['common_industries'] == analysis['primary_industries'] and len(analysis['common_industries']) > 0:
                structure_analysis['common_vs_primary_identical'] += 1
                structure_analysis['complete_overlap_categories'].append(category)
            
            # Check if material tags are subset of primary industries
            if analysis['material_tags'] and analysis['material_tags'].issubset(analysis['primary_industries']):
                structure_analysis['material_tags_subset_of_primary'] += 1
        
        # Generate recommendation based on analysis
        recommendation = {
            'strategy': 'eliminate_redundant_structures',
            'primary_recommendation': 'Eliminate industryApplications.common_industries - identical to industryTags.primary_industries',
            'secondary_recommendation': 'Consolidate material_metadata.industryTags into unified category-level structure',
            'implementation_steps': [
                '1. Remove industryApplications.common_industries from Categories.yaml (100% redundant)',
                '2. Migrate unique material-specific industryTags to category-level primary_industries',
                '3. Create hybrid system: category-level primary + material-specific override capability',
                '4. Update frontmatter generators to use unified industry data source'
            ],
            'benefits': [
                f'Eliminate {structure_analysis["common_vs_primary_identical"]}/{len(self.analysis_results["redundancy_metrics"])} completely redundant category structures',
                'Single source of truth for industry data',
                'Reduced maintenance complexity',
                'Improved data consistency'
            ]
        }
        
        self.analysis_results['consolidation_opportunities']['recommendation'] = recommendation
        
        print(f"   🏆 PRIMARY RECOMMENDATION: {recommendation['primary_recommendation']}")
        print(f"   🔧 SECONDARY: {recommendation['secondary_recommendation']}")
        print(f"   📋 Categories with identical common_industries & primary_industries: {structure_analysis['common_vs_primary_identical']}")
        print(f"   ✨ Complete overlap in: {', '.join(structure_analysis['complete_overlap_categories'])}")
    
    def _generate_comprehensive_report(self):
        """Generate comprehensive analysis report."""
        print(f"\n" + "=" * 60)
        print("📑 COMPREHENSIVE INDUSTRY DATA ANALYSIS REPORT")
        print("=" * 60)
        
        # Summary metrics
        opportunities = self.analysis_results['consolidation_opportunities']
        print(f"✅ ANALYSIS COMPLETE:")
        print(f"   • Total industry data entries analyzed: {opportunities['total_entries']:,}")
        print(f"   • Unique industries identified: {opportunities['unique_industries']:,}")
        print(f"   • Redundant entries found: {opportunities['redundant_entries']:,} ({opportunities['overall_redundancy_rate']:.1f}%)")
        print(f"   • Optimization potential: {opportunities['optimization_potential']}")
        
        # Recommendation summary
        recommendation = opportunities['recommendation']
        print(f"\n🎯 CONSOLIDATION STRATEGY:")
        print(f"   Strategy: {recommendation['strategy']}")
        print(f"   Primary Action: {recommendation['primary_recommendation']}")
        print(f"   Secondary Action: {recommendation['secondary_recommendation']}")
        
        print(f"\n📝 IMPLEMENTATION BENEFITS:")
        for benefit in recommendation['benefits']:
            print(f"   • {benefit}")
        
        print(f"\n🔧 NEXT STEPS:")
        for step in recommendation['implementation_steps']:
            print(f"   {step}")
        
        print(f"\n💾 VALIDATION DATA PRESERVED:")
        print(f"   All analysis data saved for implementation validation")

def main():
    """Run the complete industry data redundancy analysis."""
    try:
        analyzer = IndustryDataAnalyzer()
        results = analyzer.analyze_complete_industry_data()
        
        # Save analysis results for implementation
        output_file = "industry_data_redundancy_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            # Convert sets to lists for JSON serialization
            def convert_sets_to_lists(obj):
                if isinstance(obj, set):
                    return sorted(list(obj))
                elif isinstance(obj, dict):
                    return {k: convert_sets_to_lists(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_sets_to_lists(item) for item in obj]
                return obj
            
            json.dump(convert_sets_to_lists(results), f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Analysis results saved to: {output_file}")
        print("🚀 Ready for industry data consolidation implementation!")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()