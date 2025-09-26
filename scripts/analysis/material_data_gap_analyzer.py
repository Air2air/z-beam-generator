#!/usr/bin/env python3
"""
Material Data Gap Analyzer

Comprehensive analysis tool to identify missing properties across all materials
and prioritize AI research tasks for data completion.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class PropertyGap:
    """Represents a missing property for a material"""
    material_name: str
    property_name: str
    property_type: str  # 'physical', 'thermal', 'mechanical', 'optical'
    priority: int  # 1=critical, 2=important, 3=supplementary
    research_difficulty: str  # 'easy', 'medium', 'hard'
    sources: List[str]  # Potential research sources


class MaterialDataGapAnalyzer:
    """Analyzes materials.yaml to identify comprehensive data gaps"""
    
    def __init__(self):
        self.materials_data = {}
        self.expected_properties = {
            # Physical properties (Priority 1)
            'density': {'type': 'physical', 'priority': 1, 'unit': 'g/cm³'},
            'melting_point': {'type': 'physical', 'priority': 1, 'unit': '°C'},
            'boiling_point': {'type': 'physical', 'priority': 2, 'unit': '°C'},
            
            # Thermal properties (Priority 1-2)
            'thermalConductivity': {'type': 'thermal', 'priority': 1, 'unit': 'W/m·K'},
            'specificHeat': {'type': 'thermal', 'priority': 2, 'unit': 'J/kg·K'},
            'thermalExpansion': {'type': 'thermal', 'priority': 2, 'unit': 'μm/m·K'},
            'thermalDiffusivity': {'type': 'thermal', 'priority': 3, 'unit': 'm²/s'},
            
            # Mechanical properties (Priority 2-3)
            'tensileStrength': {'type': 'mechanical', 'priority': 2, 'unit': 'MPa'},
            'compressiveStrength': {'type': 'mechanical', 'priority': 2, 'unit': 'MPa'},
            'youngsModulus': {'type': 'mechanical', 'priority': 2, 'unit': 'GPa'},
            'hardness': {'type': 'mechanical', 'priority': 3, 'unit': 'HV'},
            'fractureToughness': {'type': 'mechanical', 'priority': 3, 'unit': 'MPa·m½'},
            
            # Optical properties (Priority 2-3)
            'absorptionCoefficient': {'type': 'optical', 'priority': 2, 'unit': 'cm⁻¹'},
            'reflectance': {'type': 'optical', 'priority': 2, 'unit': '%'},
            'emissivity': {'type': 'optical', 'priority': 3, 'unit': ''},
            
            # Laser-specific properties (Priority 1)
            'ablationThreshold': {'type': 'laser', 'priority': 1, 'unit': 'J/cm²'},
            'damageThreshold': {'type': 'laser', 'priority': 1, 'unit': 'J/cm²'},
        }
        
        self.research_sources = {
            'easy': ['Wikipedia', 'MatWeb', 'Engineering Toolbox'],
            'medium': ['ASM Handbook', 'CRC Handbook', 'NIST WebBook'],
            'hard': ['Scientific Papers', 'Materials Databases', 'Experimental Studies']
        }
    
    def load_materials_data(self) -> None:
        """Load current materials.yaml data"""
        materials_path = Path(__file__).parent.parent.parent / "data" / "materials.yaml"
        
        with open(materials_path, 'r') as f:
            data = yaml.safe_load(f)
        
        self.materials_data = data.get('materials', {})
        print(f"Loaded {len(self.materials_data)} materials for analysis")
    
    def analyze_material_gaps(self, material_name: str, material_data: Dict) -> List[PropertyGap]:
        """Analyze gaps for a single material"""
        gaps = []
        
        for prop_name, prop_info in self.expected_properties.items():
            if not self._has_property(material_data, prop_name):
                difficulty = self._assess_research_difficulty(material_name, prop_name, material_data)
                sources = self.research_sources[difficulty]
                
                gap = PropertyGap(
                    material_name=material_name,
                    property_name=prop_name,
                    property_type=prop_info['type'],
                    priority=prop_info['priority'],
                    research_difficulty=difficulty,
                    sources=sources
                )
                gaps.append(gap)
        
        return gaps
    
    def _has_property(self, material_data: Dict, prop_name: str) -> bool:
        """Check if material has a specific property"""
        # Check direct property
        if prop_name in material_data:
            value = material_data[prop_name]
            # Exclude N/A, empty, or placeholder values
            if value and str(value).strip() not in ['N/A', '', '0', 'TBD']:
                return True
        
        # Check nested properties
        if 'properties' in material_data:
            if prop_name in material_data['properties']:
                value = material_data['properties'][prop_name]
                if value and str(value).strip() not in ['N/A', '', '0', 'TBD']:
                    return True
        
        # Check machine settings for laser properties
        if 'machineSettings' in material_data:
            if prop_name in material_data['machineSettings']:
                return True
        
        return False
    
    def _assess_research_difficulty(self, material_name: str, prop_name: str, material_data: Dict) -> str:
        """Assess how difficult it will be to research this property"""
        category = material_data.get('category', 'unknown')
        
        # Common materials with well-documented properties
        common_materials = ['aluminum', 'steel', 'copper', 'titanium', 'glass']
        if any(common in material_name.lower() for common in common_materials):
            return 'easy'
        
        # Standard categories with good documentation
        standard_categories = ['metal', 'ceramic', 'polymer']
        if category in standard_categories:
            if prop_name in ['density', 'melting_point', 'thermalConductivity']:
                return 'easy'
            elif prop_name in ['tensileStrength', 'youngsModulus']:
                return 'medium'
            else:
                return 'hard'
        
        # Specialty materials or laser-specific properties
        if prop_name in ['ablationThreshold', 'damageThreshold']:
            return 'hard'
        
        return 'medium'
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive gap analysis report"""
        if not self.materials_data:
            self.load_materials_data()
        
        all_gaps = []
        material_summaries = {}
        
        for material_name, material_data in self.materials_data.items():
            gaps = self.analyze_material_gaps(material_name, material_data)
            all_gaps.extend(gaps)
            
            material_summaries[material_name] = {
                'total_gaps': len(gaps),
                'critical_gaps': len([g for g in gaps if g.priority == 1]),
                'category': material_data.get('category', 'unknown'),
                'gaps_by_type': self._group_gaps_by_type(gaps)
            }
        
        # Aggregate statistics
        gap_stats = self._calculate_gap_statistics(all_gaps)
        
        report = {
            'analysis_summary': {
                'total_materials': len(self.materials_data),
                'total_gaps': len(all_gaps),
                'avg_gaps_per_material': len(all_gaps) / len(self.materials_data),
                'completion_percentage': self._calculate_completion_percentage(all_gaps)
            },
            'gap_statistics': gap_stats,
            'material_summaries': material_summaries,
            'prioritized_research_tasks': self._prioritize_research_tasks(all_gaps),
            'research_recommendations': self._generate_research_recommendations(all_gaps)
        }
        
        return report
    
    def _group_gaps_by_type(self, gaps: List[PropertyGap]) -> Dict:
        """Group gaps by property type"""
        grouped = defaultdict(int)
        for gap in gaps:
            grouped[gap.property_type] += 1
        return dict(grouped)
    
    def _calculate_gap_statistics(self, all_gaps: List[PropertyGap]) -> Dict:
        """Calculate comprehensive gap statistics"""
        stats = {
            'by_priority': defaultdict(int),
            'by_type': defaultdict(int),
            'by_difficulty': defaultdict(int),
            'most_missing_properties': defaultdict(int)
        }
        
        for gap in all_gaps:
            stats['by_priority'][gap.priority] += 1
            stats['by_type'][gap.property_type] += 1
            stats['by_difficulty'][gap.research_difficulty] += 1
            stats['most_missing_properties'][gap.property_name] += 1
        
        return {k: dict(v) for k, v in stats.items()}
    
    def _calculate_completion_percentage(self, all_gaps: List[PropertyGap]) -> Dict:
        """Calculate data completion percentage"""
        total_expected = len(self.materials_data) * len(self.expected_properties)
        total_missing = len(all_gaps)
        total_present = total_expected - total_missing
        
        return {
            'overall_completion': (total_present / total_expected) * 100,
            'critical_completion': self._calculate_critical_completion(all_gaps),
            'by_category': self._calculate_category_completion(all_gaps)
        }
    
    def _calculate_critical_completion(self, all_gaps: List[PropertyGap]) -> float:
        """Calculate completion for critical properties only"""
        critical_props = [p for p, info in self.expected_properties.items() if info['priority'] == 1]
        total_critical_expected = len(self.materials_data) * len(critical_props)
        critical_gaps = len([g for g in all_gaps if g.priority == 1])
        
        return ((total_critical_expected - critical_gaps) / total_critical_expected) * 100
    
    def _calculate_category_completion(self, all_gaps: List[PropertyGap]) -> Dict:
        """Calculate completion by material category"""
        category_gaps = defaultdict(int)
        category_totals = defaultdict(int)
        
        for material_name, material_data in self.materials_data.items():
            category = material_data.get('category', 'unknown')
            category_totals[category] += len(self.expected_properties)
        
        for gap in all_gaps:
            material_data = self.materials_data.get(gap.material_name, {})
            category = material_data.get('category', 'unknown')
            category_gaps[category] += 1
        
        completion_by_category = {}
        for category in category_totals:
            missing = category_gaps.get(category, 0)
            total = category_totals[category]
            completion_by_category[category] = ((total - missing) / total) * 100
        
        return completion_by_category
    
    def _prioritize_research_tasks(self, all_gaps: List[PropertyGap]) -> List[Dict]:
        """Prioritize research tasks by impact and feasibility"""
        # Sort by priority (1=highest), then by frequency (most common gaps first)
        gap_frequency = defaultdict(int)
        for gap in all_gaps:
            gap_frequency[gap.property_name] += 1
        
        prioritized = sorted(all_gaps, key=lambda g: (g.priority, -gap_frequency[g.property_name]))
        
        tasks = []
        for i, gap in enumerate(prioritized[:50]):  # Top 50 tasks
            task = {
                'rank': i + 1,
                'material': gap.material_name,
                'property': gap.property_name,
                'priority': gap.priority,
                'difficulty': gap.research_difficulty,
                'frequency': gap_frequency[gap.property_name],
                'sources': gap.sources
            }
            tasks.append(task)
        
        return tasks
    
    def _generate_research_recommendations(self, all_gaps: List[PropertyGap]) -> Dict:
        """Generate strategic research recommendations"""
        return {
            'immediate_actions': [
                "Focus on Priority 1 properties (density, melting_point, thermalConductivity, ablationThreshold)",
                "Start with 'easy' difficulty materials (common metals and ceramics)",
                "Target properties with highest frequency across materials"
            ],
            'research_strategies': [
                "Batch research by material category for efficiency",
                "Use multiple sources for validation and accuracy",
                "Implement automated quality checks for researched data"
            ],
            'automation_opportunities': [
                "Create AI research agents for different property types",
                "Implement web scraping for standard databases (MatWeb, NIST)",
                "Build validation pipelines for data quality assurance"
            ]
        }
    
    def save_report(self, report: Dict, output_path: str = None) -> None:
        """Save comprehensive report to file"""
        if output_path is None:
            output_path = Path(__file__).parent / "material_data_gap_report.json"
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Gap analysis report saved to: {output_path}")


if __name__ == "__main__":
    analyzer = MaterialDataGapAnalyzer()
    report = analyzer.generate_comprehensive_report()
    
    print("\n=== MATERIAL DATA GAP ANALYSIS REPORT ===")
    print(f"Total materials analyzed: {report['analysis_summary']['total_materials']}")
    print(f"Total data gaps found: {report['analysis_summary']['total_gaps']}")
    print(f"Overall completion: {report['analysis_summary']['completion_percentage']['overall_completion']:.1f}%")
    print(f"Critical properties completion: {report['analysis_summary']['completion_percentage']['critical_completion']:.1f}%")
    
    print("\n=== TOP MISSING PROPERTIES ===")
    for prop, count in sorted(report['gap_statistics']['most_missing_properties'].items(), 
                             key=lambda x: x[1], reverse=True)[:10]:
        print(f"{prop}: {count} materials missing")
    
    analyzer.save_report(report)