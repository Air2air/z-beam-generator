#!/usr/bin/env python3
"""
Categories.yaml Reconciliation Script

Migrates metadata, ranges, and templates from Categories.yaml into the new
multi-file architecture:
- MaterialProperties.yaml: Extends with property definitions, categories, usage tiers
- MachineSettings.yaml: Extends with parameter ranges and descriptions
- CategoryMetadata.yaml: Creates new file with templates and frameworks

Preserves all existing per-material data while adding category-level metadata.
"""

import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import shutil


class CategoriesReconciler:
    """Reconciles Categories.yaml with new multi-file architecture."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.categories_path = data_dir / "Categories.yaml"
        self.properties_path = data_dir / "MaterialProperties.yaml"
        self.settings_path = data_dir / "MachineSettings.yaml"
        self.metadata_path = data_dir / "CategoryMetadata.yaml"
        self.archive_dir = data_dir / "archive"
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML file."""
        print(f"Loading {path.name}...")
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def save_yaml(self, data: Dict[str, Any], path: Path, backup: bool = True):
        """Save YAML file with optional backup."""
        if backup and path.exists():
            backup_path = path.parent / f"{path.stem}_{self.timestamp}{path.suffix}"
            print(f"Creating backup: {backup_path.name}")
            shutil.copy2(path, backup_path)
        
        print(f"Writing {path.name}...")
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, 
                     allow_unicode=True, width=120)
    
    def extend_material_properties(self, categories_data: Dict[str, Any], 
                                   properties_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extend MaterialProperties.yaml with metadata from Categories.yaml."""
        print("\n=== Extending MaterialProperties.yaml ===")
        
        # Create extended structure
        extended = {
            '_metadata': {
                'version': '2.0.0',
                'description': 'Material properties with category metadata and research tracking',
                'extracted_date': properties_data.get('_metadata', {}).get('extracted_date'),
                'total_materials': properties_data.get('_metadata', {}).get('total_materials'),
                'structure': 'Properties organized by category taxonomy with ranges and definitions',
                'research_confidence_threshold': categories_data.get('metadata', {}).get('research_confidence_threshold', 75),
                'last_updated': datetime.now().isoformat(),
                'reconciled_from_categories': True,
                'categories_version': categories_data.get('metadata', {}).get('version'),
            }
        }
        
        # Add property definitions
        if 'materialPropertyDescriptions' in categories_data:
            print("  ✓ Adding propertyDefinitions section")
            extended['propertyDefinitions'] = categories_data['materialPropertyDescriptions']
        
        # Add property categories taxonomy
        if 'propertyCategories' in categories_data:
            print("  ✓ Adding propertyCategories section")
            extended['propertyCategories'] = categories_data['propertyCategories']
        
        # Add usage tiers
        if 'propertyCategories' in categories_data and 'usage_tiers' in categories_data['propertyCategories']:
            print("  ✓ Adding usageTiers section")
            extended['usageTiers'] = categories_data['propertyCategories']['usage_tiers']
        
        # Add category ranges (extracted from categories section)
        if 'categories' in categories_data:
            print("  ✓ Adding categoryRanges section")
            category_ranges = {}
            for cat_name, cat_data in categories_data['categories'].items():
                if 'category_ranges' in cat_data:
                    category_ranges[cat_name] = {
                        'name': cat_data.get('name', cat_name),
                        'description': cat_data.get('description', ''),
                        'ranges': cat_data['category_ranges']
                    }
            if category_ranges:
                extended['categoryRanges'] = category_ranges
        
        # Preserve existing per-material properties (unchanged)
        print("  ✓ Preserving existing per-material properties")
        extended['properties'] = properties_data.get('properties', {})
        
        print(f"  ✓ Extended schema: {len(extended.keys())} top-level sections")
        return extended
    
    def extend_machine_settings(self, categories_data: Dict[str, Any],
                                settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extend MachineSettings.yaml with metadata from Categories.yaml."""
        print("\n=== Extending MachineSettings.yaml ===")
        
        # Create extended structure
        extended = {
            '_metadata': {
                'version': '2.0.0',
                'description': 'Machine settings with parameter ranges and optimization guidance',
                'extracted_date': settings_data.get('_metadata', {}).get('extracted_date'),
                'total_materials': settings_data.get('_metadata', {}).get('total_materials'),
                'structure': 'Settings with min/max ranges and category-specific optimization',
                'last_updated': datetime.now().isoformat(),
                'reconciled_from_categories': True,
                'categories_version': categories_data.get('metadata', {}).get('version'),
            }
        }
        
        # Add parameter ranges
        if 'machineSettingsRanges' in categories_data:
            print("  ✓ Adding parameterRanges section")
            extended['parameterRanges'] = categories_data['machineSettingsRanges']
        
        # Add parameter descriptions
        if 'machineSettingsDescriptions' in categories_data:
            print("  ✓ Adding parameterDescriptions section")
            extended['parameterDescriptions'] = categories_data['machineSettingsDescriptions']
        
        # Preserve existing per-material settings (unchanged)
        print("  ✓ Preserving existing per-material settings")
        extended['settings'] = settings_data.get('settings', {})
        
        print(f"  ✓ Extended schema: {len(extended.keys())} top-level sections")
        return extended
    
    def create_category_metadata(self, categories_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create CategoryMetadata.yaml with templates and frameworks."""
        print("\n=== Creating CategoryMetadata.yaml ===")
        
        metadata = {
            '_metadata': {
                'version': '1.0.0',
                'description': 'Category-level metadata, templates, and regulatory frameworks',
                'created_date': datetime.now().isoformat(),
                'source': 'Extracted from Categories.yaml',
                'categories_version': categories_data.get('metadata', {}).get('version'),
            }
        }
        
        # Extract template and framework sections
        template_sections = [
            'industryGuidance',
            'safetyTemplates',
            'regulatoryTemplates',
            'environmentalImpactTemplates',
            'applicationTypeDefinitions',
            'standardOutcomeMetrics',
        ]
        
        for section in template_sections:
            if section in categories_data:
                print(f"  ✓ Adding {section} section")
                metadata[section] = categories_data[section]
        
        # Add category definitions (without per-material data)
        if 'categories' in categories_data:
            print("  ✓ Adding category definitions")
            category_defs = {}
            for cat_name, cat_data in categories_data['categories'].items():
                # Extract only metadata, not per-material properties
                cat_def = {
                    'name': cat_data.get('name', cat_name),
                    'description': cat_data.get('description', ''),
                }
                if 'subcategories' in cat_data:
                    cat_def['subcategories'] = cat_data['subcategories']
                if 'common_applications' in cat_data:
                    cat_def['common_applications'] = cat_data['common_applications']
                if 'regulatory_standards' in cat_data:
                    cat_def['regulatory_standards'] = cat_data['regulatory_standards']
                
                category_defs[cat_name] = cat_def
            
            metadata['categoryDefinitions'] = category_defs
        
        # Add universal regulatory standards
        if 'universal_regulatory_standards' in categories_data:
            print("  ✓ Adding universal_regulatory_standards")
            metadata['universal_regulatory_standards'] = categories_data['universal_regulatory_standards']
        
        print(f"  ✓ Created metadata file: {len(metadata.keys())} top-level sections")
        return metadata
    
    def validate_data_preservation(self, original_properties: Dict[str, Any],
                                   extended_properties: Dict[str, Any],
                                   original_settings: Dict[str, Any],
                                   extended_settings: Dict[str, Any]) -> bool:
        """Validate that all per-material data is preserved."""
        print("\n=== Validating Data Preservation ===")
        
        # Check properties
        orig_props = original_properties.get('properties', {})
        ext_props = extended_properties.get('properties', {})
        
        if len(orig_props) != len(ext_props):
            print(f"  ✗ Material count mismatch in properties: {len(orig_props)} vs {len(ext_props)}")
            return False
        
        for material_name in orig_props:
            if material_name not in ext_props:
                print(f"  ✗ Missing material in extended properties: {material_name}")
                return False
            
            if orig_props[material_name] != ext_props[material_name]:
                print(f"  ✗ Data mismatch for material: {material_name}")
                return False
        
        print(f"  ✓ All {len(orig_props)} materials' properties preserved")
        
        # Check settings
        orig_settings = original_settings.get('settings', {})
        ext_settings = extended_settings.get('settings', {})
        
        if len(orig_settings) != len(ext_settings):
            print(f"  ✗ Material count mismatch in settings: {len(orig_settings)} vs {len(ext_settings)}")
            return False
        
        for material_name in orig_settings:
            if material_name not in ext_settings:
                print(f"  ✗ Missing material in extended settings: {material_name}")
                return False
            
            if orig_settings[material_name] != ext_settings[material_name]:
                print(f"  ✗ Data mismatch for material: {material_name}")
                return False
        
        print(f"  ✓ All {len(orig_settings)} materials' settings preserved")
        print("  ✓ 100% data preservation validated")
        return True
    
    def archive_categories(self):
        """Archive Categories.yaml to archive directory."""
        print("\n=== Archiving Categories.yaml ===")
        
        # Create archive directory if needed
        self.archive_dir.mkdir(exist_ok=True)
        
        # Archive with timestamp
        archive_path = self.archive_dir / f"Categories_{self.timestamp}.yaml"
        print(f"  Moving {self.categories_path.name} → {archive_path}")
        shutil.move(str(self.categories_path), str(archive_path))
        
        # Create README in archive
        readme_path = self.archive_dir / "README.md"
        if not readme_path.exists():
            readme_content = f"""# Archive Directory

This directory contains archived data files from schema migrations.

## Categories.yaml Archive

**Original File**: `Categories.yaml`  
**Archived**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Reason**: Schema reconciliation - data migrated to MaterialProperties.yaml, MachineSettings.yaml, and CategoryMetadata.yaml

### Migration Details

The Categories.yaml file contained:
- Property definitions and ranges → MaterialProperties.yaml
- Machine settings ranges and descriptions → MachineSettings.yaml
- Templates and frameworks → CategoryMetadata.yaml

All data has been preserved and integrated into the new multi-file architecture.

### Archived Files

"""
            with open(readme_path, 'w') as f:
                f.write(readme_content)
        
        # Append to README
        with open(readme_path, 'a') as f:
            f.write(f"- `{archive_path.name}` - Archived {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print("  ✓ Categories.yaml archived successfully")
    
    def run(self):
        """Execute the full reconciliation process."""
        print("=" * 70)
        print("CATEGORIES.YAML RECONCILIATION")
        print("=" * 70)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Load all files
        categories_data = self.load_yaml(self.categories_path)
        properties_data = self.load_yaml(self.properties_path)
        settings_data = self.load_yaml(self.settings_path)
        
        # Extend MaterialProperties.yaml
        extended_properties = self.extend_material_properties(categories_data, properties_data)
        
        # Extend MachineSettings.yaml
        extended_settings = self.extend_machine_settings(categories_data, settings_data)
        
        # Create CategoryMetadata.yaml
        category_metadata = self.create_category_metadata(categories_data)
        
        # Validate data preservation
        if not self.validate_data_preservation(properties_data, extended_properties,
                                               settings_data, extended_settings):
            print("\n✗ VALIDATION FAILED - Aborting migration")
            return False
        
        # Save extended files (with backups)
        print("\n=== Saving Extended Files ===")
        self.save_yaml(extended_properties, self.properties_path, backup=True)
        self.save_yaml(extended_settings, self.settings_path, backup=True)
        self.save_yaml(category_metadata, self.metadata_path, backup=False)
        
        # Archive Categories.yaml
        self.archive_categories()
        
        print("\n" + "=" * 70)
        print("✓ RECONCILIATION COMPLETE")
        print("=" * 70)
        print("\nResults:")
        print(f"  ✓ MaterialProperties.yaml extended ({self.properties_path.stat().st_size // 1024} KB)")
        print(f"  ✓ MachineSettings.yaml extended ({self.settings_path.stat().st_size // 1024} KB)")
        print(f"  ✓ CategoryMetadata.yaml created ({self.metadata_path.stat().st_size // 1024} KB)")
        print("  ✓ Categories.yaml archived to archive/")
        print("\nBackups created:")
        print(f"  - MaterialProperties_{self.timestamp}.yaml")
        print(f"  - MachineSettings_{self.timestamp}.yaml")
        print(f"  - Categories_{self.timestamp}.yaml (in archive/)")
        
        return True


def main():
    """Main entry point."""
    # Determine data directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    data_dir = project_root / "materials" / "data"
    
    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        return 1
    
    # Run reconciliation
    reconciler = CategoriesReconciler(data_dir)
    success = reconciler.run()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
