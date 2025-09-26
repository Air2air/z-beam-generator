#!/usr/bin/env python3
"""
AI Research Bridge System - Core Architecture

Comprehensive system to identify and fill data gaps in materials.yaml using
structured AI research protocols with fail-fast validation.
"""

import yaml
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResearchPriority(Enum):
    """Research priority levels"""
    CRITICAL = 1    # Essential properties for laser cleaning
    IMPORTANT = 2   # Significant properties for optimization
    SUPPLEMENTARY = 3  # Additional properties for completeness


class ResearchDifficulty(Enum):
    """Research difficulty assessment"""
    EASY = "easy"        # Well-documented common materials
    MEDIUM = "medium"    # Standard materials with some documentation
    HARD = "hard"        # Specialized or poorly documented materials


class ResearchStatus(Enum):
    """Status of research tasks"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    FAILED = "failed"
    VALIDATED = "validated"


@dataclass
class PropertyGap:
    """Represents a missing property for a material"""
    material_name: str
    property_name: str
    property_type: str  # 'physical', 'thermal', 'mechanical', 'optical', 'laser'
    priority: ResearchPriority
    difficulty: ResearchDifficulty
    sources: List[str]
    research_query: str
    expected_units: str
    validation_range: Optional[Tuple[float, float]] = None


@dataclass
class ResearchResult:
    """Result of AI research for a property"""
    property_gap: PropertyGap
    researched_value: str
    confidence_score: float  # 0.0 to 1.0
    sources_used: List[str]
    research_notes: str
    validation_status: str
    timestamp: datetime
    researcher_id: str = "ai_research_bridge"


class PropertyDefinitions:
    """Central definition of all expected material properties"""
    
    PROPERTIES = {
        # Physical properties (Priority 1)
        'density': {
            'type': 'physical', 
            'priority': ResearchPriority.CRITICAL,
            'units': 'g/cm³',
            'description': 'Material density at room temperature',
            'validation_range': (0.1, 25.0),
            'query_template': 'What is the density of {material} in g/cm³?'
        },
        'melting_point': {
            'type': 'physical',
            'priority': ResearchPriority.CRITICAL,
            'units': '°C',
            'description': 'Melting point temperature',
            'validation_range': (-50, 4000),
            'query_template': 'What is the melting point of {material} in degrees Celsius?'
        },
        'boiling_point': {
            'type': 'physical',
            'priority': ResearchPriority.IMPORTANT,
            'units': '°C',
            'description': 'Boiling point temperature',
            'validation_range': (-200, 6000),
            'query_template': 'What is the boiling point of {material} in degrees Celsius?'
        },
        
        # Thermal properties (Priority 1-2)
        'thermalConductivity': {
            'type': 'thermal',
            'priority': ResearchPriority.CRITICAL,
            'units': 'W/m·K',
            'description': 'Thermal conductivity at room temperature',
            'validation_range': (0.01, 500),
            'query_template': 'What is the thermal conductivity of {material} in W/m·K at room temperature?'
        },
        'specificHeat': {
            'type': 'thermal',
            'priority': ResearchPriority.IMPORTANT,
            'units': 'J/kg·K',
            'description': 'Specific heat capacity',
            'validation_range': (100, 5000),
            'query_template': 'What is the specific heat capacity of {material} in J/kg·K?'
        },
        'thermalExpansion': {
            'type': 'thermal',
            'priority': ResearchPriority.IMPORTANT,
            'units': 'μm/m·K',
            'description': 'Linear thermal expansion coefficient',
            'validation_range': (0.1, 200),
            'query_template': 'What is the linear thermal expansion coefficient of {material} in μm/m·K?'
        },
        'thermalDiffusivity': {
            'type': 'thermal',
            'priority': ResearchPriority.SUPPLEMENTARY,
            'units': 'm²/s',
            'description': 'Thermal diffusivity',
            'validation_range': (1e-8, 1e-3),
            'query_template': 'What is the thermal diffusivity of {material} in m²/s?'
        },
        
        # Mechanical properties (Priority 2-3)
        'tensileStrength': {
            'type': 'mechanical',
            'priority': ResearchPriority.IMPORTANT,
            'units': 'MPa',
            'description': 'Ultimate tensile strength',
            'validation_range': (1, 10000),
            'query_template': 'What is the tensile strength of {material} in MPa?'
        },
        'compressiveStrength': {
            'type': 'mechanical',
            'priority': ResearchPriority.IMPORTANT,
            'units': 'MPa',
            'description': 'Compressive strength',
            'validation_range': (1, 15000),
            'query_template': 'What is the compressive strength of {material} in MPa?'
        },
        'youngsModulus': {
            'type': 'mechanical',
            'priority': ResearchPriority.IMPORTANT,
            'units': 'GPa',
            'description': "Young's modulus of elasticity",
            'validation_range': (0.01, 1000),
            'query_template': 'What is the Young\'s modulus of {material} in GPa?'
        },
        'hardness': {
            'type': 'mechanical',
            'priority': ResearchPriority.SUPPLEMENTARY,
            'units': 'HV',
            'description': 'Vickers hardness',
            'validation_range': (1, 10000),
            'query_template': 'What is the Vickers hardness of {material} in HV?'
        },
        
        # Optical properties (Priority 2-3)
        'absorptionCoefficient': {
            'type': 'optical',
            'priority': ResearchPriority.IMPORTANT,
            'units': 'cm⁻¹',
            'description': 'Optical absorption coefficient at 1064nm',
            'validation_range': (0.001, 1000),
            'query_template': 'What is the optical absorption coefficient of {material} at 1064nm wavelength in cm⁻¹?'
        },
        'reflectance': {
            'type': 'optical',
            'priority': ResearchPriority.IMPORTANT,
            'units': '%',
            'description': 'Optical reflectance at 1064nm',
            'validation_range': (0, 100),
            'query_template': 'What is the optical reflectance of {material} at 1064nm wavelength as a percentage?'
        },
        'emissivity': {
            'type': 'optical',
            'priority': ResearchPriority.SUPPLEMENTARY,
            'units': '',
            'description': 'Thermal emissivity',
            'validation_range': (0.01, 1.0),
            'query_template': 'What is the thermal emissivity of {material}?'
        },
        
        # Laser-specific properties (Priority 1)
        'ablationThreshold': {
            'type': 'laser',
            'priority': ResearchPriority.CRITICAL,
            'units': 'J/cm²',
            'description': 'Laser ablation threshold fluence',
            'validation_range': (0.01, 100),
            'query_template': 'What is the laser ablation threshold of {material} in J/cm² for nanosecond pulses at 1064nm?'
        },
        'damageThreshold': {
            'type': 'laser',
            'priority': ResearchPriority.CRITICAL,
            'units': 'J/cm²',
            'description': 'Laser damage threshold fluence',
            'validation_range': (0.01, 200),
            'query_template': 'What is the laser damage threshold of {material} in J/cm² for nanosecond pulses at 1064nm?'
        }
    }
    
    @classmethod
    def get_property_info(cls, property_name: str) -> Optional[Dict]:
        """Get property definition by name"""
        return cls.PROPERTIES.get(property_name)
    
    @classmethod
    def get_all_properties(cls) -> List[str]:
        """Get list of all property names"""
        return list(cls.PROPERTIES.keys())
    
    @classmethod
    def get_properties_by_priority(cls, priority: ResearchPriority) -> List[str]:
        """Get properties by priority level"""
        return [
            name for name, info in cls.PROPERTIES.items()
            if info['priority'] == priority
        ]


class MaterialDataGapDetector:
    """Detects data gaps in materials.yaml"""
    
    def __init__(self, materials_yaml_path: Path):
        self.materials_yaml_path = materials_yaml_path
        self.materials_data = {}
        self.property_definitions = PropertyDefinitions()
        self._load_materials_data()
    
    def _load_materials_data(self) -> None:
        """Load materials.yaml data"""
        try:
            with open(self.materials_yaml_path, 'r') as f:
                data = yaml.safe_load(f)
            self.materials_data = data.get('materials', {})
            logger.info(f"Loaded {len(self.materials_data)} material categories")
        except Exception as e:
            raise ValueError(f"Failed to load materials.yaml: {e}")
    
    def detect_gaps_for_material(self, material_name: str, material_data: Dict) -> List[PropertyGap]:
        """Detect all property gaps for a single material"""
        gaps = []
        
        for prop_name in self.property_definitions.get_all_properties():
            if not self._has_property(material_data, prop_name):
                prop_info = self.property_definitions.get_property_info(prop_name)
                difficulty = self._assess_difficulty(material_name, prop_name, material_data)
                sources = self._get_research_sources(difficulty)
                
                gap = PropertyGap(
                    material_name=material_name,
                    property_name=prop_name,
                    property_type=prop_info['type'],
                    priority=prop_info['priority'],
                    difficulty=difficulty,
                    sources=sources,
                    research_query=prop_info['query_template'].format(material=material_name),
                    expected_units=prop_info['units'],
                    validation_range=prop_info.get('validation_range')
                )
                gaps.append(gap)
        
        return gaps
    
    def _has_property(self, material_data: Dict, prop_name: str) -> bool:
        """Check if material has a specific property with valid data"""
        # Check direct property
        if prop_name in material_data:
            value = material_data[prop_name]
            if self._is_valid_value(value):
                return True
        
        # Check nested properties
        if 'properties' in material_data:
            if prop_name in material_data['properties']:
                value = material_data['properties'][prop_name]
                if self._is_valid_value(value):
                    return True
        
        # Check machine settings for laser properties
        if 'machineSettings' in material_data:
            if prop_name in material_data['machineSettings']:
                value = material_data['machineSettings'][prop_name]
                if self._is_valid_value(value):
                    return True
        
        return False
    
    def _is_valid_value(self, value: Any) -> bool:
        """Check if a value is valid (not N/A, empty, or placeholder)"""
        if value is None:
            return False
        
        str_value = str(value).strip()
        invalid_values = {'N/A', '', '0', 'TBD', 'null', 'None', 'unknown'}
        
        return str_value not in invalid_values and len(str_value) > 0
    
    def _assess_difficulty(self, material_name: str, prop_name: str, material_data: Dict) -> ResearchDifficulty:
        """Assess research difficulty for a property"""
        category = material_data.get('category', 'unknown')
        
        # Common materials with well-documented properties
        common_materials = ['aluminum', 'steel', 'copper', 'titanium', 'glass', 'carbon']
        if any(common in material_name.lower() for common in common_materials):
            if prop_name in ['density', 'melting_point', 'thermalConductivity']:
                return ResearchDifficulty.EASY
            elif prop_name in ['tensileStrength', 'youngsModulus']:
                return ResearchDifficulty.MEDIUM
            else:
                return ResearchDifficulty.HARD
        
        # Standard categories with good documentation
        if category in ['metal', 'ceramic', 'glass']:
            if prop_name in ['density', 'melting_point', 'thermalConductivity']:
                return ResearchDifficulty.EASY
            elif prop_name in ['tensileStrength', 'youngsModulus', 'hardness']:
                return ResearchDifficulty.MEDIUM
            else:
                return ResearchDifficulty.HARD
        
        # Laser-specific properties are generally harder to find
        if prop_name in ['ablationThreshold', 'damageThreshold']:
            return ResearchDifficulty.HARD
        
        # Wood and composites often have variable properties
        if category in ['wood', 'composite']:
            return ResearchDifficulty.MEDIUM
        
        return ResearchDifficulty.MEDIUM
    
    def _get_research_sources(self, difficulty: ResearchDifficulty) -> List[str]:
        """Get appropriate research sources based on difficulty"""
        source_map = {
            ResearchDifficulty.EASY: [
                'Wikipedia Materials Database',
                'MatWeb Material Property Database',
                'Engineering Toolbox',
                'ASM Materials Database'
            ],
            ResearchDifficulty.MEDIUM: [
                'ASM Handbook Online',
                'CRC Handbook of Chemistry and Physics',
                'NIST Materials Database',
                'Springer Materials Database',
                'Academic Literature Search'
            ],
            ResearchDifficulty.HARD: [
                'Scientific Journal Papers',
                'Specialized Materials Databases',
                'Experimental Studies Database',
                'Laser-Materials Interaction Papers',
                'Industry Technical Reports'
            ]
        }
        
        return source_map.get(difficulty, source_map[ResearchDifficulty.MEDIUM])
    
    def detect_all_gaps(self) -> List[PropertyGap]:
        """Detect all property gaps across all materials"""
        all_gaps = []
        
        for category, category_data in self.materials_data.items():
            if 'items' in category_data:
                for material_data in category_data['items']:
                    material_name = material_data.get('name')
                    if material_name:
                        gaps = self.detect_gaps_for_material(material_name, material_data)
                        all_gaps.extend(gaps)
        
        return all_gaps
    
    def generate_gap_report(self) -> Dict:
        """Generate comprehensive gap analysis report"""
        all_gaps = self.detect_all_gaps()
        
        # Group by priority
        gaps_by_priority = defaultdict(list)
        for gap in all_gaps:
            gaps_by_priority[gap.priority].append(gap)
        
        # Group by difficulty
        gaps_by_difficulty = defaultdict(list)
        for gap in all_gaps:
            gaps_by_difficulty[gap.difficulty].append(gap)
        
        # Most missing properties
        property_counts = defaultdict(int)
        for gap in all_gaps:
            property_counts[gap.property_name] += 1
        
        report = {
            'summary': {
                'total_gaps': len(all_gaps),
                'critical_gaps': len(gaps_by_priority[ResearchPriority.CRITICAL]),
                'important_gaps': len(gaps_by_priority[ResearchPriority.IMPORTANT]),
                'supplementary_gaps': len(gaps_by_priority[ResearchPriority.SUPPLEMENTARY]),
                'easy_research': len(gaps_by_difficulty[ResearchDifficulty.EASY]),
                'medium_research': len(gaps_by_difficulty[ResearchDifficulty.MEDIUM]),
                'hard_research': len(gaps_by_difficulty[ResearchDifficulty.HARD])
            },
            'most_missing_properties': dict(sorted(
                property_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:20]),
            'prioritized_gaps': sorted(
                all_gaps, 
                key=lambda g: (g.priority.value, -property_counts[g.property_name])
            )[:100],  # Top 100 priority gaps
            'research_recommendations': self._generate_recommendations(all_gaps)
        }
        
        return report
    
    def _generate_recommendations(self, gaps: List[PropertyGap]) -> Dict:
        """Generate strategic research recommendations"""
        return {
            'immediate_priorities': [
                f"Research {ResearchPriority.CRITICAL.name} properties first",
                "Focus on EASY difficulty materials to build momentum",
                "Target properties missing from most materials"
            ],
            'batch_research_strategy': [
                "Group materials by category for efficient research",
                "Research common properties across multiple materials simultaneously",
                "Validate results using multiple sources"
            ],
            'automation_opportunities': [
                "Implement web scraping for standard databases",
                "Create property-specific research agents",
                "Build automated validation pipelines"
            ]
        }


if __name__ == "__main__":
    # Test the gap detection system
    materials_path = Path(__file__).parent.parent.parent / "data" / "materials.yaml"
    
    if materials_path.exists():
        detector = MaterialDataGapDetector(materials_path)
        report = detector.generate_gap_report()
        
        print("=== AI RESEARCH BRIDGE SYSTEM - GAP ANALYSIS ===")
        print(f"Total gaps found: {report['summary']['total_gaps']}")
        print(f"Critical gaps: {report['summary']['critical_gaps']}")
        print(f"Easy research tasks: {report['summary']['easy_research']}")
        
        print("\n=== TOP MISSING PROPERTIES ===")
        for prop, count in list(report['most_missing_properties'].items())[:10]:
            print(f"{prop}: {count} materials")
        
        # Save detailed report
        output_path = Path(__file__).parent / "gap_analysis_report.json"
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\nDetailed report saved to: {output_path}")
    else:
        print(f"Materials file not found: {materials_path}")