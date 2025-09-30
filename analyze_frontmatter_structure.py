#!/usr/bin/env python3
"""
Frontmatter Structure Analysis and Redundancy Detection
Analyzes frontmatter files to identify organization and redundancy removal opportunities.
"""

import sys
import yaml
import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Any, Set

# Add the project root to the Python path
sys.path.insert(0, '/Users/todddunning/Desktop/Z-Beam/z-beam-generator')

class FrontmatterAnalyzer:
    """Analyzes frontmatter files for structure and redundancy patterns."""
    
    def __init__(self):
        self.files_analyzed = 0
        self.total_size = 0
        self.structure_patterns = defaultdict(int)
        self.redundant_data = defaultdict(list)
        self.property_frequency = defaultdict(int)
        self.duplicated_content = defaultdict(list)
    
    def analyze_directory(self, directory_path: str) -> Dict[str, Any]:
        """Analyze all YAML files in a directory."""
        
        print(f"🔍 Analyzing frontmatter files in: {directory_path}")
        print("=" * 60)
        
        directory = Path(directory_path)
        yaml_files = list(directory.glob("*.yaml"))
        
        print(f"📁 Found {len(yaml_files)} YAML files")
        
        # Sample analysis on first 10 files for performance
        sample_files = yaml_files[:10] if len(yaml_files) > 10 else yaml_files
        
        for file_path in sample_files:
            self._analyze_file(file_path)
        
        # Analysis summary
        analysis_results = {
            "files_analyzed": self.files_analyzed,
            "total_size_kb": round(self.total_size / 1024, 2),
            "avg_size_kb": round((self.total_size / self.files_analyzed) / 1024, 2) if self.files_analyzed > 0 else 0,
            "structure_patterns": dict(self.structure_patterns),
            "property_frequency": dict(self.property_frequency),
            "redundancy_opportunities": self._identify_redundancy_opportunities(),
            "optimization_recommendations": self._generate_optimization_recommendations()
        }
        
        return analysis_results
    
    def _analyze_file(self, file_path: Path):
        """Analyze a single YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                data = yaml.safe_load(content)
            
            self.files_analyzed += 1
            self.total_size += len(content)
            
            # Analyze structure
            self._analyze_structure(data, file_path.name)
            
            # Analyze properties
            self._analyze_properties(data)
            
            # Check for common patterns
            self._check_common_patterns(data, file_path.name)
            
        except Exception as e:
            print(f"❌ Error analyzing {file_path}: {e}")
    
    def _analyze_structure(self, data: Dict, filename: str):
        """Analyze the structure of the frontmatter data."""
        if not isinstance(data, dict):
            return
        
        # Count top-level sections
        sections = list(data.keys())
        self.structure_patterns[f"sections_{len(sections)}"] += 1
        
        # Common sections
        common_sections = [
            'name', 'category', 'subcategory', 'title', 'description',
            'materialProperties', 'laserProperties', 'applications', 
            'processes', 'outcomeMetrics', 'componentOutputs', 'orchestration'
        ]
        
        for section in common_sections:
            if section in data:
                self.structure_patterns[f"has_{section}"] += 1
        
        # Check for component outputs structure
        if 'componentOutputs' in data:
            components = list(data['componentOutputs'].keys())
            self.structure_patterns[f"components_{len(components)}"] += 1
            
            for component in components:
                self.structure_patterns[f"component_{component}"] += 1
    
    def _analyze_properties(self, data: Dict):
        """Analyze material properties for frequency and patterns."""
        if 'materialProperties' in data and isinstance(data['materialProperties'], dict):
            for prop_name in data['materialProperties'].keys():
                self.property_frequency[prop_name] += 1
    
    def _check_common_patterns(self, data: Dict, filename: str):
        """Check for commonly duplicated content patterns."""
        
        # Check descriptions
        if 'description' in data:
            desc = data['description']
            if desc in [item[1] for item in self.duplicated_content['descriptions']]:
                self.duplicated_content['descriptions'].append((filename, desc))
            else:
                self.duplicated_content['descriptions'].append((filename, desc))
        
        # Check titles
        if 'title' in data:
            title = data['title']
            if title in [item[1] for item in self.duplicated_content['titles']]:
                self.duplicated_content['titles'].append((filename, title))
            else:
                self.duplicated_content['titles'].append((filename, title))
        
        # Check if name and subcategory are identical (redundancy)
        if data.get('name') == data.get('subcategory'):
            self.redundant_data['name_subcategory_identical'].append(filename)
    
    def _identify_redundancy_opportunities(self) -> Dict[str, Any]:
        """Identify specific redundancy removal opportunities."""
        opportunities = {
            "property_standardization": {},
            "content_deduplication": {},
            "structure_optimization": {},
            "metadata_consolidation": {}
        }
        
        # Property standardization opportunities
        common_properties = {k: v for k, v in self.property_frequency.items() if v > 1}
        opportunities["property_standardization"] = {
            "common_properties": common_properties,
            "total_properties": len(self.property_frequency),
            "standardization_potential": len(common_properties)
        }
        
        # Content deduplication
        duplicate_descriptions = [item for item in self.duplicated_content['descriptions'] 
                                if self.duplicated_content['descriptions'].count(item) > 1]
        duplicate_titles = [item for item in self.duplicated_content['titles'] 
                          if self.duplicated_content['titles'].count(item) > 1]
        
        opportunities["content_deduplication"] = {
            "duplicate_descriptions": len(set(duplicate_descriptions)),
            "duplicate_titles": len(set(duplicate_titles)),
            "name_subcategory_redundancy": len(self.redundant_data['name_subcategory_identical'])
        }
        
        # Structure optimization
        opportunities["structure_optimization"] = {
            "consistent_sections": self.structure_patterns,
            "component_distribution": {k: v for k, v in self.structure_patterns.items() if k.startswith('component_')}
        }
        
        return opportunities
    
    def _generate_optimization_recommendations(self) -> List[str]:
        """Generate specific optimization recommendations."""
        recommendations = []
        
        # Size optimization
        if self.total_size > 0:
            avg_size = self.total_size / self.files_analyzed
            if avg_size > 15000:  # > 15KB average
                recommendations.append("📏 Large file sizes detected - consider component separation")
        
        # Property standardization
        if len(self.property_frequency) > 20:
            recommendations.append("🔧 High property variety - implement property templates")
        
        # Redundant name/subcategory
        if len(self.redundant_data['name_subcategory_identical']) > 0:
            recommendations.append("🔄 Remove redundant name/subcategory duplication")
        
        # Component organization
        component_counts = [v for k, v in self.structure_patterns.items() if k.startswith('components_')]
        if component_counts and max(component_counts) > 2:
            recommendations.append("📦 Consider component output consolidation")
        
        # Metadata optimization
        if self.structure_patterns.get('has_orchestration', 0) > 0:
            recommendations.append("⚙️ Orchestration metadata could be moved to separate section")
        
        # Template opportunities
        recommendations.append("📋 Create base templates for common material categories")
        recommendations.append("🎯 Implement property inheritance for material families")
        recommendations.append("🚀 Consider lazy loading for large property sets")
        
        return recommendations

def analyze_orchestrated_files():
    """Analyze the specific orchestrated files we generated."""
    
    print("🎯 ANALYZING ORCHESTRATED FILES")
    print("=" * 50)
    
    orchestrated_files = [
        "aluminum-direct-orchestrated.yaml",
        "aluminum-unified-orchestrated.yaml"
    ]
    
    for filename in orchestrated_files:
        filepath = Path(filename)
        if filepath.exists():
            with open(filepath, 'r') as f:
                content = f.read()
                data = yaml.safe_load(content)
            
            print(f"\\n📄 {filename}:")
            print(f"   📏 Size: {len(content):,} characters ({len(content)/1024:.1f} KB)")
            print(f"   📁 Sections: {len(data.keys()) if isinstance(data, dict) else 0}")
            
            if 'componentOutputs' in data:
                components = data['componentOutputs']
                print(f"   🔧 Components: {len(components)} ({list(components.keys())})")
                
                # Analyze component sizes
                for comp_name, comp_data in components.items():
                    comp_size = len(str(comp_data))
                    print(f"      • {comp_name}: {comp_size:,} chars")
            
            if 'orchestration' in data:
                orch = data['orchestration']
                print(f"   ⚙️ Orchestration: {orch.get('method', 'unknown')} - {orch.get('totalTime', 'N/A')}")
                print(f"   🚀 Bypass: {orch.get('bypass', 'none')}")

def main():
    """Main analysis function."""
    
    print("🔍 FRONTMATTER STRUCTURE ANALYSIS")
    print("=" * 60)
    print("🎯 Analyzing organization and redundancy removal opportunities")
    print()
    
    # Analyze existing frontmatter files
    analyzer = FrontmatterAnalyzer()
    
    frontmatter_dir = "content/components/frontmatter"
    if Path(frontmatter_dir).exists():
        results = analyzer.analyze_directory(frontmatter_dir)
        
        print(f"\\n📊 ANALYSIS RESULTS:")
        print(f"   📁 Files analyzed: {results['files_analyzed']}")
        print(f"   📏 Total size: {results['total_size_kb']} KB")
        print(f"   📈 Average size: {results['avg_size_kb']} KB per file")
        
        print(f"\\n🔧 PROPERTY FREQUENCY (Top 10):")
        sorted_props = sorted(results['property_frequency'].items(), key=lambda x: x[1], reverse=True)
        for prop, count in sorted_props[:10]:
            print(f"   • {prop}: {count} files")
        
        print(f"\\n🎯 REDUNDANCY OPPORTUNITIES:")
        redund = results['redundancy_opportunities']
        print(f"   📋 Property standardization potential: {redund['property_standardization']['standardization_potential']}")
        print(f"   🔄 Content deduplication opportunities: {redund['content_deduplication']['duplicate_descriptions'] + redund['content_deduplication']['duplicate_titles']}")
        print(f"   📦 Name/subcategory redundancy: {redund['content_deduplication']['name_subcategory_redundancy']}")
        
        print(f"\\n💡 OPTIMIZATION RECOMMENDATIONS:")
        for i, rec in enumerate(results['optimization_recommendations'], 1):
            print(f"   {i}. {rec}")
    
    # Analyze our orchestrated files
    analyze_orchestrated_files()
    
    print(f"\\n" + "=" * 60)
    print("✅ Analysis complete! Review recommendations for optimization.")

if __name__ == "__main__":
    main()