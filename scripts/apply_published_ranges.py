#!/usr/bin/env python3
"""
Apply Published Ranges to Categories.yaml
Integrates validated research data from Priority 2 into the authoritative Categories.yaml file
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class PublishedRangeIntegrator:
    """Integrates published research data into Categories.yaml"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "data"
        
        # Load files
        self.categories = self._load_yaml(self.data_dir / "Categories.yaml")
        self.research_data = self._load_yaml(self.data_dir / "PublishedRanges_Research.yaml")
        self.progress = self._load_yaml(self.data_dir / "Priority2_Research_Progress.yaml")
        
        # Track changes
        self.updates_applied = []
        self.properties_updated = 0
        self.categories_modified = set()
        
    def _load_yaml(self, filepath: Path) -> dict:
        """Load YAML file"""
        if not filepath.exists():
            print(f"⚠️  Warning: {filepath} not found")
            return {}
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    def _save_yaml(self, data: dict, filepath: Path):
        """Save YAML file with backup"""
        # Create backup
        if filepath.exists():
            backup_path = filepath.with_suffix('.yaml.backup')
            import shutil
            shutil.copy(filepath, backup_path)
            print(f"✅ Backup created: {backup_path.name}")
        
        # Save updated file
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        print(f"✅ Updated: {filepath.name}")
    
    def integrate_published_ranges(self):
        """Main integration process"""
        print("=" * 80)
        print(" 📥 INTEGRATING PUBLISHED RANGES INTO CATEGORIES.YAML")
        print("=" * 80)
        print()
        
        # Process research findings
        if 'findings' in self.progress:
            print("📊 Processing validated research findings...")
            for property_name, category_data in self.progress['findings'].items():
                if not isinstance(category_data, dict):
                    continue
                for category, research in category_data.items():
                    if isinstance(research, dict) and research.get('status') == 'VALIDATED':
                        self._apply_range_to_category(property_name, category, research['data'])
        
        # Process recommended ranges from research file
        for category in self.research_data:
            if category in ['metadata', 'priority_searches', 'methodology', 'notes']:
                continue
            
            if isinstance(self.research_data[category], dict):
                for property_name, prop_data in self.research_data[category].items():
                    if isinstance(prop_data, dict) and 'recommended_range' in prop_data:
                        rec_range = prop_data['recommended_range']
                        if isinstance(rec_range, dict) and rec_range.get('status') != 'PLACEHOLDER - NEEDS RESEARCH':
                            self._apply_range_to_category(property_name, category, rec_range)
        
        # Update metadata
        self._update_categories_metadata()
        
        # Save updated Categories.yaml
        self._save_yaml(self.categories, self.data_dir / "Categories.yaml")
        
        # Generate integration report
        self._generate_integration_report()
        
        print("\n" + "=" * 80)
        print(" ✅ INTEGRATION COMPLETE")
        print("=" * 80)
        print(f"\nProperties updated: {self.properties_updated}")
        print(f"Categories modified: {len(self.categories_modified)}")
        print(f"Total updates applied: {len(self.updates_applied)}")
    
    def _apply_range_to_category(self, property_name: str, category: str, data: Dict):
        """Apply a single property range to a category"""
        # Ensure category exists in Categories.yaml
        if 'categories' not in self.categories:
            print("⚠️  'categories' section not found in Categories.yaml")
            return
        
        if category not in self.categories['categories']:
            print(f"⚠️  Category '{category}' not found in Categories.yaml, skipping {property_name}")
            return
        
        # Skip if data is incomplete
        if not isinstance(data, dict):
            return
        
        # Handle pulse-duration-specific data (e.g., ablationThreshold)
        if 'nanosecond' in data or 'picosecond' in data or 'femtosecond' in data:
            self._apply_pulse_specific_range(property_name, category, data)
            return
        
        # Handle wavelength-specific data (e.g., reflectivity)
        if 'at_1064nm' in data or 'at_532nm' in data:
            self._apply_wavelength_specific_range(property_name, category, data)
            return
        
        # Standard min/max range
        if 'min' in data and 'max' in data:
            self._apply_standard_range(property_name, category, data)
    
    def _apply_standard_range(self, property_name: str, category: str, data: Dict):
        """Apply standard min/max range"""
        range_data = {
            'min': data['min'],
            'max': data['max'],
            'unit': data.get('unit', ''),
            'source': data.get('source', 'Published research'),
            'confidence': data.get('confidence', 75),
            'notes': data.get('notes', ''),
            'last_updated': datetime.now().isoformat()
        }
        
        # Update Categories.yaml
        cat_ref = self.categories['categories'][category]
        if 'category_ranges' not in cat_ref:
            cat_ref['category_ranges'] = {}
        
        cat_ref['category_ranges'][property_name] = range_data
        
        # Track update
        self.updates_applied.append({
            'property': property_name,
            'category': category,
            'range': f"{data['min']}-{data['max']} {data.get('unit', '')}",
            'source': data.get('source', ''),
            'confidence': data.get('confidence', 75)
        })
        self.properties_updated += 1
        self.categories_modified.add(category)
        
        print(f"  ✅ {category}.{property_name}: {data['min']}-{data['max']} {data.get('unit', '')} ({data.get('confidence', 75)}%)")
    
    def _apply_pulse_specific_range(self, property_name: str, category: str, data: Dict):
        """Apply pulse-duration-specific ranges"""
        pulse_data = {}
        
        for pulse_type in ['nanosecond', 'picosecond', 'femtosecond']:
            if pulse_type in data and isinstance(data[pulse_type], dict):
                pulse_data[pulse_type] = {
                    'min': data[pulse_type]['min'],
                    'max': data[pulse_type]['max'],
                    'unit': data[pulse_type].get('unit', 'J/cm²'),
                }
        
        if pulse_data:
            range_data = {
                **pulse_data,
                'source': data.get('source', 'Published research'),
                'confidence': data.get('confidence', 75),
                'notes': data.get('notes', 'Pulse-duration-specific values'),
                'measurement_context': 'Varies by pulse duration (ns/ps/fs)',
                'last_updated': datetime.now().isoformat()
            }
            
            cat_ref = self.categories['categories'][category]
            if 'category_ranges' not in cat_ref:
                cat_ref['category_ranges'] = {}
            
            cat_ref['category_ranges'][property_name] = range_data
            
            self.updates_applied.append({
                'property': property_name,
                'category': category,
                'type': 'pulse-specific',
                'regimes': list(pulse_data.keys()),
                'confidence': data.get('confidence', 75)
            })
            self.properties_updated += 1
            self.categories_modified.add(category)
            
            print(f"  ✅ {category}.{property_name}: Pulse-specific ranges added ({len(pulse_data)} regimes, {data.get('confidence', 75)}%)")
    
    def _apply_wavelength_specific_range(self, property_name: str, category: str, data: Dict):
        """Apply wavelength-specific ranges"""
        wavelength_data = {}
        
        for key in data:
            if key.startswith('at_') and 'nm' in key:
                wavelength_data[key] = data[key]
        
        if wavelength_data:
            range_data = {
                **wavelength_data,
                'source': data.get('source', 'Published research'),
                'confidence': data.get('confidence', 75),
                'notes': data.get('notes', 'Wavelength-specific values'),
                'measurement_context': 'Varies by laser wavelength',
                'last_updated': datetime.now().isoformat()
            }
            
            cat_ref = self.categories['categories'][category]
            if 'category_ranges' not in cat_ref:
                cat_ref['category_ranges'] = {}
            
            cat_ref['category_ranges'][property_name] = range_data
            
            self.updates_applied.append({
                'property': property_name,
                'category': category,
                'type': 'wavelength-specific',
                'wavelengths': list(wavelength_data.keys()),
                'confidence': data.get('confidence', 75)
            })
            self.properties_updated += 1
            self.categories_modified.add(category)
            
            print(f"  ✅ {category}.{property_name}: Wavelength-specific ranges added ({len(wavelength_data)} wavelengths, {data.get('confidence', 75)}%)")
    
    def _update_categories_metadata(self):
        """Update Categories.yaml metadata"""
        if 'metadata' not in self.categories:
            self.categories['metadata'] = {}
        
        metadata = self.categories['metadata']
        metadata['priority2_integration_date'] = datetime.now().isoformat()
        metadata['priority2_properties_updated'] = self.properties_updated
        metadata['priority2_categories_modified'] = len(self.categories_modified)
        metadata['priority2_validation_status'] = 'INTEGRATED'
        
                # Calculate new authoritative coverage
        total_properties = 0
        authoritative_properties = 0
        
        if 'categories' in self.categories:
            for category, cat_data in self.categories['categories'].items():
                if 'category_ranges' in cat_data and isinstance(cat_data['category_ranges'], dict):
                    for prop_name, prop_data in cat_data['category_ranges'].items():
                        if isinstance(prop_data, dict):
                            total_properties += 1
                            if prop_data.get('source') and prop_data.get('confidence', 0) >= 75:
                                authoritative_properties += 1
        
        if total_properties > 0:
            coverage = (authoritative_properties / total_properties) * 100
            metadata['authoritative_coverage'] = round(coverage, 1)
            print(f"\n📊 Authoritative Coverage: {coverage:.1f}% ({authoritative_properties}/{total_properties} properties)")
    
    def _generate_integration_report(self):
        """Generate integration report"""
        report = {
            'integration_metadata': {
                'timestamp': datetime.now().isoformat(),
                'properties_updated': self.properties_updated,
                'categories_modified': sorted(list(self.categories_modified)),
                'total_updates': len(self.updates_applied)
            },
            'updates_applied': self.updates_applied,
            'next_steps': [
                'Regenerate frontmatter files to inherit new ranges',
                'Run test_range_quality.py to verify improvements',
                'Generate final Priority 2 completion documentation',
                'Update PROJECT_STATUS.md with completion metrics'
            ]
        }
        
        report_path = self.data_dir / "Categories_Integration_Report.yaml"
        with open(report_path, 'w', encoding='utf-8') as f:
            yaml.dump(report, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        print(f"\n✅ Integration report saved: {report_path.name}")


def main():
    """Main entry point"""
    integrator = PublishedRangeIntegrator()
    integrator.integrate_published_ranges()


if __name__ == "__main__":
    main()
