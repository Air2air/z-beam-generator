#!/usr/bin/env python3
"""
Generate Material → Contamination Pattern Mappings

Phase 2A: Create bidirectional mappings between materials and contamination patterns
based on material properties, environmental factors, and industry knowledge.

This script:
1. Loads all materials from Materials.yaml
2. Loads all contamination patterns from Contaminants.yaml
3. Generates likelihood scores for each material-pattern combination
4. Creates structured contamination field data for each material
5. Saves results back to Materials.yaml

Author: AI Assistant
Date: November 26, 2025
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@dataclass
class PatternApplicability:
    """Represents applicability of a contamination pattern to a material"""
    pattern_id: str
    pattern_name: str
    likelihood: str  # high | medium | low
    typical_environments: List[str]
    layer_thickness_range: List[float]  # [min, max] in microns
    reasoning: str


class ContaminationMapper:
    """
    Generate material → contamination pattern mappings.
    
    Uses material properties and pattern characteristics to determine
    which contamination patterns are applicable to each material.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.materials_file = project_root / 'data' / 'materials' / 'Materials.yaml'
        self.contaminants_file = project_root / 'data' / 'contaminants' / 'Contaminants.yaml'
        
        # Load data
        self.materials_data = self._load_yaml(self.materials_file)
        self.contaminants_data = self._load_yaml(self.contaminants_file)
        
        # Extract pattern info
        self.patterns = self.contaminants_data.get('contamination_patterns', {})
        
        print(f"✅ Loaded {len(self.materials_data.get('material_index', {}))} materials")
        print(f"✅ Loaded {len(self.patterns)} contamination patterns")
    
    def _load_yaml(self, filepath: Path) -> Dict:
        """Load YAML file with error handling"""
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _save_yaml(self, filepath: Path, data: Dict):
        """Save YAML file with backup"""
        backup_path = filepath.parent / f"{filepath.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        
        # Backup original
        if filepath.exists():
            import shutil
            shutil.copy(filepath, backup_path)
            print(f"📦 Backup created: {backup_path.name}")
        
        # Save updated data
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print(f"💾 Saved: {filepath.name}")
    
    def get_material_category_properties(self, material_name: str) -> Dict:
        """Get material category and properties"""
        material_index = self.materials_data.get('material_index', {})
        materials = self.materials_data.get('materials', {})
        
        category = material_index.get(material_name)
        material_data = materials.get(material_name, {})
        
        return {
            'category': category,
            'subcategory': material_data.get('subcategory'),
            'material_data': material_data
        }
    
    def determine_likelihood(
        self,
        material_name: str,
        material_category: str,
        material_data: Dict,
        pattern_id: str,
        pattern_data: Dict
    ) -> str:
        """
        Determine likelihood of contamination pattern on material.
        
        Returns: high | medium | low
        """
        # Check explicit lists first
        valid_materials = pattern_data.get('valid_materials', [])
        prohibited_materials = pattern_data.get('prohibited_materials', [])
        
        if material_name in prohibited_materials:
            return None  # Pattern not applicable
        
        if material_name in valid_materials:
            return 'high'
        
        # Category-based inference
        likelihood_map = self._infer_likelihood_by_category(
            material_category,
            pattern_id,
            pattern_data
        )
        
        return likelihood_map
    
    def _infer_likelihood_by_category(
        self,
        category: str,
        pattern_id: str,
        pattern_data: Dict
    ) -> Optional[str]:
        """
        Infer likelihood based on material category and pattern characteristics.
        """
        # Pattern-category likelihood rules
        RULES = {
            'rust-oxidation': {
                'metal': 'high',
                'steel_types': 'high',
                'non_ferrous_metals': 'low'
            },
            'paint-coatings': {
                'metal': 'high',
                'wood': 'high',
                'stone': 'medium',
                'masonry': 'medium',
                'plastic': 'medium',
                'glass': 'low',
                'ceramic': 'low'
            },
            'environmental-dust': {
                'all': 'high'  # Universal pattern
            },
            'oil-grease': {
                'metal': 'high',
                'plastic': 'medium',
                'composite': 'medium',
                'stone': 'low',
                'wood': 'low'
            },
            'biological-growth': {
                'stone': 'high',
                'masonry': 'high',
                'wood': 'high',
                'metal': 'low',
                'plastic': 'low',
                'glass': 'low'
            },
            'scale-buildup': {
                'metal': 'high',
                'glass': 'medium',
                'ceramic': 'medium',
                'stone': 'low'
            },
            'corrosion-pitting': {
                'metal': 'high',
                'stone': 'medium',
                'masonry': 'medium',
                'other': 'low'
            },
            'chemical-stains': {
                'stone': 'high',
                'masonry': 'high',
                'metal': 'medium',
                'plastic': 'medium',
                'wood': 'low'
            },
            'soot-carbon': {
                'stone': 'high',
                'masonry': 'high',
                'metal': 'medium',
                'wood': 'medium',
                'plastic': 'low'
            },
            'water-stains': {
                'stone': 'high',
                'masonry': 'high',
                'wood': 'medium',
                'metal': 'low',
                'plastic': 'low'
            },
            'mineral-deposits': {
                'stone': 'high',
                'masonry': 'high',
                'glass': 'medium',
                'metal': 'low'
            }
        }
        
        pattern_rules = RULES.get(pattern_id, {})
        
        # Check universal patterns
        if 'all' in pattern_rules:
            return pattern_rules['all']
        
        # Check specific category
        if category in pattern_rules:
            return pattern_rules[category]
        
        # Default to low if no specific rule
        return 'low'
    
    def get_typical_environments(
        self,
        material_category: str,
        pattern_id: str
    ) -> List[str]:
        """Get typical environments where pattern occurs on material"""
        ENVIRONMENT_MAP = {
            'rust-oxidation': {
                'metal': ['outdoor', 'marine', 'industrial', 'high_humidity']
            },
            'paint-coatings': {
                'all': ['outdoor', 'indoor', 'industrial', 'architectural']
            },
            'environmental-dust': {
                'all': ['outdoor', 'indoor', 'storage', 'transport']
            },
            'oil-grease': {
                'metal': ['industrial', 'automotive', 'manufacturing', 'machinery'],
                'default': ['industrial', 'manufacturing']
            },
            'biological-growth': {
                'stone': ['outdoor', 'shaded', 'high_humidity', 'low_maintenance'],
                'wood': ['outdoor', 'shaded', 'high_humidity'],
                'masonry': ['outdoor', 'shaded', 'high_humidity']
            },
            'scale-buildup': {
                'metal': ['high_temperature', 'industrial', 'thermal_processing'],
                'default': ['high_temperature', 'industrial']
            },
            'corrosion-pitting': {
                'metal': ['outdoor', 'marine', 'industrial', 'chemical_exposure'],
                'stone': ['outdoor', 'urban', 'acid_rain']
            },
            'chemical-stains': {
                'all': ['industrial', 'laboratory', 'chemical_processing']
            },
            'soot-carbon': {
                'stone': ['urban', 'industrial', 'fire_damaged', 'historical'],
                'masonry': ['urban', 'industrial', 'fire_damaged']
            },
            'water-stains': {
                'stone': ['outdoor', 'high_humidity', 'water_exposure'],
                'masonry': ['outdoor', 'high_humidity', 'water_exposure']
            },
            'mineral-deposits': {
                'stone': ['outdoor', 'water_exposure', 'calcium_rich_areas'],
                'glass': ['outdoor', 'water_exposure']
            }
        }
        
        pattern_map = ENVIRONMENT_MAP.get(pattern_id, {})
        
        # Check for 'all' key
        if 'all' in pattern_map:
            return pattern_map['all']
        
        # Check specific category
        if material_category in pattern_map:
            return pattern_map[material_category]
        
        # Default
        return pattern_map.get('default', ['general'])
    
    def get_thickness_range(
        self,
        pattern_id: str,
        material_category: str
    ) -> List[float]:
        """
        Get typical layer thickness range in microns.
        
        Returns [min, max] in microns
        """
        THICKNESS_MAP = {
            'rust-oxidation': {
                'metal': [5.0, 500.0]
            },
            'paint-coatings': {
                'all': [50.0, 300.0]
            },
            'environmental-dust': {
                'all': [1.0, 20.0]
            },
            'oil-grease': {
                'all': [0.5, 50.0]
            },
            'biological-growth': {
                'stone': [10.0, 500.0],
                'wood': [10.0, 1000.0],
                'masonry': [10.0, 500.0]
            },
            'scale-buildup': {
                'metal': [50.0, 1000.0],
                'default': [20.0, 500.0]
            },
            'corrosion-pitting': {
                'metal': [10.0, 200.0],
                'stone': [50.0, 500.0]
            },
            'chemical-stains': {
                'all': [1.0, 50.0]
            },
            'soot-carbon': {
                'all': [5.0, 100.0]
            },
            'water-stains': {
                'all': [1.0, 20.0]
            },
            'mineral-deposits': {
                'all': [10.0, 200.0]
            }
        }
        
        pattern_map = THICKNESS_MAP.get(pattern_id, {})
        
        if 'all' in pattern_map:
            return pattern_map['all']
        
        if material_category in pattern_map:
            return pattern_map[material_category]
        
        # Default range
        return pattern_map.get('default', [1.0, 100.0])
    
    def generate_pattern_reasoning(
        self,
        material_name: str,
        material_category: str,
        pattern_id: str,
        pattern_name: str,
        likelihood: str
    ) -> str:
        """Generate brief reasoning for pattern applicability"""
        
        REASONING_TEMPLATES = {
            'rust-oxidation': {
                'high': f"{material_name} is a ferrous metal highly susceptible to iron oxide formation in moisture and oxygen.",
                'medium': f"{material_name} can develop surface rust in certain environments despite protective measures.",
                'low': f"{material_name} rarely develops rust due to its non-ferrous composition."
            },
            'paint-coatings': {
                'high': f"{material_name} is commonly painted for protection and aesthetics in architectural and industrial applications.",
                'medium': f"{material_name} may have paint coatings in certain applications requiring surface protection.",
                'low': f"{material_name} is rarely painted due to its natural properties and typical applications."
            },
            'environmental-dust': {
                'high': f"All materials including {material_name} accumulate environmental dust during storage, transport, and exposure."
            },
            'oil-grease': {
                'high': f"{material_name} frequently contacts oils and greases in industrial machinery and manufacturing processes.",
                'medium': f"{material_name} may encounter oil/grease contamination in certain industrial settings.",
                'low': f"{material_name} rarely requires oil/grease removal due to its typical non-industrial applications."
            },
            'biological-growth': {
                'high': f"{material_name}'s porous nature and outdoor exposure make it highly susceptible to algae, moss, and lichen growth.",
                'medium': f"{material_name} can support biological growth in humid, shaded environments.",
                'low': f"{material_name}'s smooth, non-porous surface resists biological colonization."
            },
            'scale-buildup': {
                'high': f"{material_name} develops scale deposits when exposed to high temperatures and mineral-rich environments.",
                'medium': f"{material_name} may accumulate light scale in thermal processing applications.",
                'low': f"{material_name} rarely experiences scale buildup in typical applications."
            },
            'corrosion-pitting': {
                'high': f"{material_name} is prone to localized corrosion and pitting in aggressive environments with chlorides or acids.",
                'medium': f"{material_name} can develop surface pitting under prolonged environmental exposure.",
                'low': f"{material_name} exhibits excellent corrosion resistance and rarely develops pitting."
            },
            'chemical-stains': {
                'high': f"{material_name} readily absorbs chemical stains due to its porous structure and reactivity.",
                'medium': f"{material_name} may develop chemical staining in laboratory or industrial settings.",
                'low': f"{material_name}'s chemical resistance prevents most staining."
            },
            'soot-carbon': {
                'high': f"{material_name}'s porous texture readily traps soot and carbon deposits from combustion and pollution.",
                'medium': f"{material_name} can accumulate soot in urban or fire-damaged environments.",
                'low': f"{material_name}'s smooth surface resists soot adhesion."
            },
            'water-stains': {
                'high': f"{material_name}'s porosity allows water penetration, leading to visible staining and mineral deposits.",
                'medium': f"{material_name} can develop water stains with prolonged moisture exposure.",
                'low': f"{material_name}'s water resistance prevents most staining."
            },
            'mineral-deposits': {
                'high': f"{material_name} accumulates calcium and mineral deposits from hard water exposure, especially outdoors.",
                'medium': f"{material_name} may develop mineral deposits in water-rich environments.",
                'low': f"{material_name} rarely requires mineral deposit removal."
            }
        }
        
        pattern_reasoning = REASONING_TEMPLATES.get(pattern_id, {})
        
        if likelihood in pattern_reasoning:
            return pattern_reasoning[likelihood]
        
        # Generic fallback
        return f"{material_name} exhibits {likelihood} susceptibility to {pattern_name} based on material properties and typical applications."
    
    def generate_contamination_mapping(
        self,
        material_name: str
    ) -> Dict:
        """
        Generate complete contamination mapping for a single material.
        
        Returns structure:
        {
            'valid': [pattern_ids with high/medium likelihood],
            'prohibited': [pattern_ids explicitly incompatible],
            'conditional': {},
            'applicable_patterns': [
                {
                    'pattern_id': str,
                    'likelihood': str,
                    'typical_environments': [str],
                    'layer_thickness_range': [min, max]
                }
            ]
        }
        """
        # Get material info
        material_info = self.get_material_category_properties(material_name)
        category = material_info['category']
        material_data = material_info['material_data']
        
        if not category:
            print(f"⚠️  Skipping {material_name}: No category found")
            return None
        
        valid_patterns = []
        prohibited_patterns = []
        applicable_patterns = []
        
        # Evaluate each contamination pattern
        for pattern_id, pattern_data in self.patterns.items():
            likelihood = self.determine_likelihood(
                material_name,
                category,
                material_data,
                pattern_id,
                pattern_data
            )
            
            if likelihood is None:
                # Explicitly prohibited
                prohibited_patterns.append(pattern_id)
                continue
            
            if likelihood in ['high', 'medium']:
                valid_patterns.append(pattern_id)
            
            # Get environments and thickness
            environments = self.get_typical_environments(category, pattern_id)
            thickness_range = self.get_thickness_range(pattern_id, category)
            
            # Generate reasoning
            pattern_name = pattern_data.get('name', pattern_id)
            reasoning = self.generate_pattern_reasoning(
                material_name,
                category,
                pattern_id,
                pattern_name,
                likelihood
            )
            
            # Build applicable pattern entry
            applicable_entry = {
                'pattern_id': pattern_id,
                'likelihood': likelihood,
                'typical_environments': environments,
                'layer_thickness_range': thickness_range
            }
            
            applicable_patterns.append(applicable_entry)
        
        return {
            'valid': sorted(valid_patterns),
            'prohibited': sorted(prohibited_patterns),
            'conditional': {},
            'applicable_patterns': applicable_patterns
        }
    
    def generate_all_mappings(self) -> Dict[str, Dict]:
        """Generate contamination mappings for all materials"""
        material_index = self.materials_data.get('material_index', {})
        mappings = {}
        
        print(f"\n{'='*80}")
        print(f"🔄 Generating contamination mappings for {len(material_index)} materials...")
        print(f"{'='*80}\n")
        
        for i, material_name in enumerate(sorted(material_index.keys()), 1):
            print(f"[{i}/{len(material_index)}] Processing: {material_name}")
            
            mapping = self.generate_contamination_mapping(material_name)
            
            if mapping:
                mappings[material_name] = mapping
                valid_count = len(mapping['valid'])
                prohibited_count = len(mapping['prohibited'])
                print(f"    ✅ Valid: {valid_count}, Prohibited: {prohibited_count}")
        
        print(f"\n{'='*80}")
        print(f"✅ Generated {len(mappings)} material contamination mappings")
        print(f"{'='*80}\n")
        
        return mappings
    
    def update_materials_yaml(self, mappings: Dict[str, Dict]):
        """Update Materials.yaml with contamination mappings"""
        materials_section = self.materials_data.get('materials', {})
        
        updated_count = 0
        for material_name, mapping in mappings.items():
            if material_name in materials_section:
                materials_section[material_name]['contamination'] = mapping
                updated_count += 1
        
        # Save updated data
        self._save_yaml(self.materials_file, self.materials_data)
        
        print(f"✅ Updated {updated_count} materials with contamination mappings")
    
    def generate_summary_report(self, mappings: Dict[str, Dict]) -> str:
        """Generate summary report of contamination mappings"""
        total_materials = len(mappings)
        
        # Count patterns
        pattern_counts = {}
        for material_name, mapping in mappings.items():
            for pattern_id in mapping['valid']:
                pattern_counts[pattern_id] = pattern_counts.get(pattern_id, 0) + 1
        
        # Build report
        report = []
        report.append("=" * 80)
        report.append("CONTAMINATION MAPPING SUMMARY")
        report.append("=" * 80)
        report.append("")
        report.append(f"Total Materials Mapped: {total_materials}")
        report.append(f"Total Patterns: {len(self.patterns)}")
        report.append("")
        report.append("Pattern Applicability (by material count):")
        report.append("-" * 80)
        
        for pattern_id, count in sorted(pattern_counts.items(), key=lambda x: -x[1]):
            pattern_name = self.patterns[pattern_id].get('name', pattern_id)
            percentage = (count / total_materials) * 100
            report.append(f"  {pattern_name:40s} {count:3d} materials ({percentage:5.1f}%)")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """Main execution"""
    print("=" * 80)
    print("Phase 2A: Generate Material → Contamination Mappings")
    print("=" * 80)
    print()
    
    # Initialize mapper
    mapper = ContaminationMapper(project_root)
    
    # Generate all mappings
    mappings = mapper.generate_all_mappings()
    
    # Generate summary report
    summary = mapper.generate_summary_report(mappings)
    print("\n" + summary)
    
    # Ask for confirmation before updating
    print("\n" + "=" * 80)
    response = input("Update Materials.yaml with these mappings? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        mapper.update_materials_yaml(mappings)
        print("\n✅ Phase 2A Complete!")
        print("   Materials.yaml updated with contamination mappings")
        print("   Backup created for safety")
    else:
        print("\n⚠️  Skipped Materials.yaml update")
        print("   Mappings generated but not saved")


if __name__ == '__main__':
    main()
