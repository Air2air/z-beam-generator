#!/usr/bin/env python3
"""
Materials.yaml Enhancement Pipeline

Automated system to detect gaps in materials.yaml, research missing properties,
and update the file with validated data while maintaining backup and integrity.

Features:
- Gap detection across all 124 materials
- AI research pipeline integration
- Automatic backup and versioning
- Property validation and quality control
- Fail-fast architecture with comprehensive error handling
"""

import logging
import yaml
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
import shutil
import os

from ai_research.core.bridge_system import MaterialDataGapDetector, PropertyDefinitions
from ai_research.pipeline.research_engine import AIResearchPipeline, PropertyValidator

logger = logging.getLogger(__name__)


class MaterialsYamlEnhancer:
    """Automated enhancement system for materials.yaml with gap detection and research"""
    
    def __init__(self, materials_yaml_path: Optional[str] = None):
        """
        Initialize the enhancement system
        
        Args:
            materials_yaml_path: Path to materials.yaml file (auto-detected if None)
        """
        self.materials_yaml_path = Path(materials_yaml_path) if materials_yaml_path else self._find_materials_yaml()
        self.backup_dir = Path("backups") / "materials_enhancement"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize core systems
        self.gap_detector = MaterialDataGapDetector()
        self.research_pipeline = AIResearchPipeline()
        self.property_validator = PropertyValidator()
        
        # Load current materials data
        self.materials_data = self._load_materials_data()
        
        logger.info(f"Materials.yaml enhancer initialized with {len(self._get_all_materials())} materials")
    
    def _find_materials_yaml(self) -> Path:
        """Find materials.yaml file in the project"""
        current_dir = Path.cwd()
        
        # Common locations to check
        locations = [
            current_dir / "data" / "materials.yaml",
            current_dir / "materials.yaml",
            current_dir.parent / "data" / "materials.yaml"
        ]
        
        for location in locations:
            if location.exists():
                return location
        
        raise FileNotFoundError("Could not find materials.yaml file")
    
    def _load_materials_data(self) -> Dict:
        """Load current materials.yaml data"""
        try:
            with open(self.materials_yaml_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"Failed to load materials.yaml: {e}")
    
    def _get_all_materials(self) -> List[Dict]:
        """Get all material entries from materials.yaml structure"""
        materials = []
        
        # Handle materials structure
        materials_section = self.materials_data.get('materials', {})
        
        for category, category_data in materials_section.items():
            if isinstance(category_data, dict) and 'items' in category_data:
                # Direct category with items
                materials.extend(category_data['items'])
            elif isinstance(category_data, dict):
                # Category with subcategories
                for subcat_name, subcat_data in category_data.items():
                    if isinstance(subcat_data, dict) and 'items' in subcat_data:
                        materials.extend(subcat_data['items'])
        
        return materials
    
    def analyze_material_gaps(self) -> Dict[str, Any]:
        """
        Analyze all materials for missing properties and generate comprehensive gap report
        
        Returns:
            Dict containing gap analysis results
        """
        logger.info("Starting comprehensive gap analysis of materials.yaml")
        
        all_materials = self._get_all_materials()
        gap_analysis = {
            'total_materials': len(all_materials),
            'materials_with_gaps': [],
            'gap_summary': {},
            'priority_research': [],
            'analysis_date': datetime.now().isoformat()
        }
        
        # Track gap statistics
        gap_counts = {}
        
        for material in all_materials:
            material_name = material.get('name', 'Unknown')
            
            # Detect gaps for this material
            gaps = self.gap_detector.detect_gaps_for_material(material)
            
            if gaps['missing_properties'] or gaps['incomplete_properties']:
                gap_analysis['materials_with_gaps'].append({
                    'name': material_name,
                    'category': material.get('category', 'unknown'),
                    'missing_properties': gaps['missing_properties'],
                    'incomplete_properties': gaps['incomplete_properties'],
                    'research_priority': gaps['research_priority'].value,
                    'estimated_difficulty': gaps['estimated_difficulty'].value
                })
                
                # Count gaps by type
                for prop in gaps['missing_properties']:
                    gap_counts[prop] = gap_counts.get(prop, 0) + 1
        
        # Generate summary statistics
        gap_analysis['gap_summary'] = {
            'materials_needing_research': len(gap_analysis['materials_with_gaps']),
            'completion_percentage': ((gap_analysis['total_materials'] - len(gap_analysis['materials_with_gaps'])) 
                                    / gap_analysis['total_materials'] * 100),
            'most_common_gaps': sorted(gap_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'total_gap_instances': sum(gap_counts.values())
        }
        
        # Generate priority research list
        gap_analysis['priority_research'] = self._generate_priority_research_list(
            gap_analysis['materials_with_gaps']
        )
        
        logger.info(f"Gap analysis complete: {len(gap_analysis['materials_with_gaps'])} materials need research")
        
        return gap_analysis
    
    def _generate_priority_research_list(self, materials_with_gaps: List[Dict]) -> List[Dict]:
        """Generate prioritized research list based on gaps and material importance"""
        research_items = []
        
        for material_gap in materials_with_gaps:
            for prop in material_gap['missing_properties']:
                research_items.append({
                    'material': material_gap['name'],
                    'property': prop,
                    'category': material_gap['category'],
                    'priority': material_gap['research_priority'],
                    'difficulty': material_gap['estimated_difficulty']
                })
        
        # Sort by priority (high first) then difficulty (low first)
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        difficulty_order = {'low': 1, 'medium': 2, 'high': 3}
        
        research_items.sort(
            key=lambda x: (priority_order.get(x['priority'], 0), -difficulty_order.get(x['difficulty'], 2)),
            reverse=True
        )
        
        return research_items[:50]  # Top 50 priority items
    
    def enhance_materials_with_research(self, max_materials: int = 10, 
                                      target_properties: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Enhance materials.yaml by researching missing properties
        
        Args:
            max_materials: Maximum number of materials to research
            target_properties: Specific properties to focus on (None for all)
            
        Returns:
            Enhancement results with statistics
        """
        logger.info(f"Starting materials enhancement for up to {max_materials} materials")
        
        # Create backup before enhancement
        backup_path = self._create_backup()
        logger.info(f"Created backup at: {backup_path}")
        
        try:
            # Analyze gaps
            gap_analysis = self.analyze_material_gaps()
            materials_to_enhance = gap_analysis['materials_with_gaps'][:max_materials]
            
            enhancement_results = {
                'enhanced_materials': [],
                'failed_materials': [],
                'properties_researched': 0,
                'backup_path': str(backup_path),
                'enhancement_date': datetime.now().isoformat()
            }
            
            for material_gap in materials_to_enhance:
                material_name = material_gap['name']
                
                try:
                    # Research missing properties
                    research_results = self._research_material_properties(
                        material_name, 
                        material_gap['missing_properties'],
                        target_properties
                    )
                    
                    if research_results['successful_properties']:
                        # Update materials.yaml with researched data
                        updated_count = self._update_material_in_yaml(
                            material_name, 
                            research_results['successful_properties']
                        )
                        
                        enhancement_results['enhanced_materials'].append({
                            'name': material_name,
                            'properties_added': list(research_results['successful_properties'].keys()),
                            'properties_count': updated_count
                        })
                        
                        enhancement_results['properties_researched'] += updated_count
                        
                        logger.info(f"Enhanced {material_name} with {updated_count} properties")
                    
                    # Track any failures
                    if research_results['failed_properties']:
                        enhancement_results['failed_materials'].append({
                            'name': material_name,
                            'failed_properties': research_results['failed_properties']
                        })
                
                except Exception as e:
                    logger.error(f"Failed to enhance {material_name}: {e}")
                    enhancement_results['failed_materials'].append({
                        'name': material_name,
                        'error': str(e)
                    })
            
            # Save updated materials.yaml
            self._save_materials_data()
            
            logger.info(f"Enhancement complete: {len(enhancement_results['enhanced_materials'])} materials enhanced")
            
            return enhancement_results
            
        except Exception as e:
            # Restore from backup on critical failure
            logger.error(f"Critical enhancement failure: {e}")
            self._restore_from_backup(backup_path)
            raise ValueError(f"Enhancement failed and backup restored: {e}")
    
    def _research_material_properties(self, material_name: str, missing_properties: List[str],
                                    target_properties: Optional[List[str]] = None) -> Dict[str, Any]:
        """Research missing properties for a material"""
        
        # Filter properties if target list provided
        if target_properties:
            missing_properties = [prop for prop in missing_properties if prop in target_properties]
        
        research_results = {
            'successful_properties': {},
            'failed_properties': []
        }
        
        for property_name in missing_properties:
            try:
                # Research the property using our AI pipeline
                research_result = self.research_pipeline.research_property_gap(
                    material_name=material_name,
                    property_name=property_name,
                    priority="medium",
                    sources=["technical_databases", "material_handbooks", "research_papers"]
                )
                
                if research_result and research_result.get('success'):
                    # Validate the researched value
                    value = research_result.get('value')
                    unit = research_result.get('unit', '')
                    
                    if self.property_validator.validate_value(property_name, value, material_name):
                        research_results['successful_properties'][property_name] = {
                            'value': value,
                            'unit': unit,
                            'source': research_result.get('source', 'AI_research'),
                            'confidence': research_result.get('confidence', 0.8),
                            'research_date': datetime.now().isoformat()
                        }
                        logger.debug(f"Researched {property_name} for {material_name}: {value} {unit}")
                    else:
                        research_results['failed_properties'].append(f"{property_name}: validation_failed")
                        logger.warning(f"Validation failed for {property_name} in {material_name}")
                else:
                    research_results['failed_properties'].append(f"{property_name}: research_failed")
                    
            except Exception as e:
                research_results['failed_properties'].append(f"{property_name}: {str(e)}")
                logger.error(f"Failed to research {property_name} for {material_name}: {e}")
        
        return research_results
    
    def _update_material_in_yaml(self, material_name: str, researched_properties: Dict[str, Any]) -> int:
        """Update a material in the YAML structure with researched properties"""
        
        updated_count = 0
        materials_section = self.materials_data.get('materials', {})
        
        # Find and update the material
        for category, category_data in materials_section.items():
            if isinstance(category_data, dict) and 'items' in category_data:
                # Direct category with items
                for item in category_data['items']:
                    if item.get('name', '').lower() == material_name.lower():
                        updated_count += self._apply_property_updates(item, researched_properties)
                        break
            elif isinstance(category_data, dict):
                # Category with subcategories
                for subcat_name, subcat_data in category_data.items():
                    if isinstance(subcat_data, dict) and 'items' in subcat_data:
                        for item in subcat_data['items']:
                            if item.get('name', '').lower() == material_name.lower():
                                updated_count += self._apply_property_updates(item, researched_properties)
                                break
        
        return updated_count
    
    def _apply_property_updates(self, material_item: Dict, researched_properties: Dict[str, Any]) -> int:
        """Apply researched property updates to a material item"""
        
        updated_count = 0
        
        for prop_name, prop_data in researched_properties.items():
            try:
                # Map property names to YAML structure
                yaml_key = self._map_property_to_yaml_key(prop_name)
                
                if yaml_key:
                    # Format the value with unit
                    value = prop_data['value']
                    unit = prop_data.get('unit', '')
                    
                    if unit:
                        formatted_value = f"{value} {unit}"
                    else:
                        formatted_value = value
                    
                    # Update the material item
                    material_item[yaml_key] = formatted_value
                    
                    # Add metadata about the research
                    metadata_key = f"{yaml_key}_research_metadata"
                    material_item[metadata_key] = {
                        'source': prop_data.get('source', 'AI_research'),
                        'confidence': prop_data.get('confidence', 0.8),
                        'research_date': prop_data.get('research_date')
                    }
                    
                    updated_count += 1
                    
                    logger.debug(f"Updated {yaml_key} = {formatted_value}")
                
            except Exception as e:
                logger.error(f"Failed to apply update for {prop_name}: {e}")
        
        return updated_count
    
    def _map_property_to_yaml_key(self, property_name: str) -> Optional[str]:
        """Map property names to materials.yaml keys"""
        
        property_mapping = {
            'density': 'density',
            'thermal_conductivity': 'thermal_conductivity',
            'melting_point': 'melting_point',
            'boiling_point': 'boiling_point',
            'tensile_strength': 'tensile_strength',
            'youngs_modulus': 'youngs_modulus',
            'hardness': 'hardness',
            'thermal_expansion': 'thermal_expansion',
            'electrical_conductivity': 'electrical_conductivity',
            'specific_heat': 'specific_heat'
        }
        
        return property_mapping.get(property_name)
    
    def _create_backup(self) -> Path:
        """Create timestamped backup of materials.yaml"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"materials_before_enhancement_{timestamp}.yaml"
        backup_path = self.backup_dir / backup_filename
        
        shutil.copy2(self.materials_yaml_path, backup_path)
        
        return backup_path
    
    def _restore_from_backup(self, backup_path: Path):
        """Restore materials.yaml from backup"""
        
        if backup_path.exists():
            shutil.copy2(backup_path, self.materials_yaml_path)
            logger.info(f"Restored materials.yaml from backup: {backup_path}")
        else:
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
    
    def _save_materials_data(self):
        """Save updated materials data to YAML file"""
        
        try:
            with open(self.materials_yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(
                    self.materials_data, 
                    f, 
                    default_flow_style=False, 
                    sort_keys=False,
                    allow_unicode=True,
                    width=1000
                )
            
            logger.info(f"Saved updated materials.yaml to {self.materials_yaml_path}")
            
        except Exception as e:
            raise ValueError(f"Failed to save materials.yaml: {e}")
    
    def generate_enhancement_report(self, output_path: Optional[str] = None) -> str:
        """Generate comprehensive enhancement report"""
        
        gap_analysis = self.analyze_material_gaps()
        
        report = f"""# Materials.yaml Enhancement Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Gap Analysis Summary
- Total Materials: {gap_analysis['total_materials']}
- Materials Needing Research: {gap_analysis['gap_summary']['materials_needing_research']}
- Current Completion: {gap_analysis['gap_summary']['completion_percentage']:.1f}%
- Total Gap Instances: {gap_analysis['gap_summary']['total_gap_instances']}

## Most Common Missing Properties
"""
        
        for prop, count in gap_analysis['gap_summary']['most_common_gaps']:
            report += f"- {prop}: {count} materials missing\n"
        
        report += f"\n## Priority Research Items (Top 20)\n"
        
        for i, item in enumerate(gap_analysis['priority_research'][:20], 1):
            report += f"{i}. {item['material']} - {item['property']} (Priority: {item['priority']}, Difficulty: {item['difficulty']})\n"
        
        report += f"\n## Materials Requiring Research\n"
        
        for material in gap_analysis['materials_with_gaps'][:20]:  # Top 20
            report += f"\n### {material['name']} ({material['category']})\n"
            report += f"Missing Properties: {', '.join(material['missing_properties'])}\n"
            report += f"Research Priority: {material['research_priority']}\n"
        
        # Save report if path provided
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Enhancement report saved to: {output_path}")
        
        return report


# CLI Integration Functions

def run_gap_analysis():
    """Run gap analysis and generate report"""
    enhancer = MaterialsYamlEnhancer()
    
    report_path = f"materials_gap_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report = enhancer.generate_enhancement_report(report_path)
    
    print("Gap Analysis Complete!")
    print(f"Report saved to: {report_path}")
    print(f"\nSummary:")
    
    gap_analysis = enhancer.analyze_material_gaps()
    print(f"- {gap_analysis['total_materials']} total materials")
    print(f"- {gap_analysis['gap_summary']['materials_needing_research']} need research")
    print(f"- {gap_analysis['gap_summary']['completion_percentage']:.1f}% complete")


def run_materials_enhancement(max_materials: int = 5):
    """Run materials enhancement with AI research"""
    enhancer = MaterialsYamlEnhancer()
    
    print(f"Starting enhancement of up to {max_materials} materials...")
    
    results = enhancer.enhance_materials_with_research(max_materials=max_materials)
    
    print("Enhancement Complete!")
    print(f"- Enhanced: {len(results['enhanced_materials'])} materials")
    print(f"- Properties Researched: {results['properties_researched']}")
    print(f"- Failed: {len(results['failed_materials'])} materials")
    print(f"- Backup: {results['backup_path']}")
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "analyze":
            run_gap_analysis()
        elif sys.argv[1] == "enhance":
            max_materials = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            run_materials_enhancement(max_materials)
        else:
            print("Usage: python materials_yaml_enhancer.py [analyze|enhance] [max_materials]")
    else:
        run_gap_analysis()