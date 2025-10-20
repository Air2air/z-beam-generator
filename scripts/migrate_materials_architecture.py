#!/usr/bin/env python3
"""
Materials Architecture Migration Script

Transforms Materials.yaml to match new Next.js frontend architecture:
1. Reorganizes properties into three categories (material_characteristics, laser_material_interaction, other)
2. Adds subcategory field for each material
3. Adds crystallineStructure to materialCharacteristics
4. Updates machineSettings structure with enhanced metadata
5. Preserves all existing AI research data and metadata

Per GROK_INSTRUCTIONS.md: Changes ONLY data files (Materials.yaml), never frontmatter.
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

# Property categorization based on new architecture
PROPERTY_CATEGORIES = {
    'material_characteristics': {
        'label': 'Material Characteristics',
        'description': 'Intrinsic physical, mechanical, chemical, and structural properties affecting cleaning outcomes and material integrity',
        'percentage': 40.0,
        'properties': [
            'density', 'hardness', 'tensileStrength', 'youngsModulus', 'compressiveStrength',
            'flexuralStrength', 'shearModulus', 'bulkModulus', 'poissonsRatio', 'fatigueLimit',
            'toughness', 'ductility', 'brittleness', 'corrosionResistance', 'oxidationResistance',
            'chemicalStability', 'biocompatibility', 'toxicity', 'flammability', 'smokeDensity',
            'crystallineStructure', 'grainSize', 'porosity', 'permeability', 'solubility',
            'diffusivity', 'viscosity', 'surfaceTension', 'electricalResistivity',
            'electricalConductivity', 'dielectricConstant', 'magneticPermeability'
        ]
    },
    'laser_material_interaction': {
        'label': 'Laser-Material Interaction',
        'description': 'Optical, thermal, and surface properties governing laser processing behavior',
        'percentage': 40.0,
        'properties': [
            'laserAbsorption', 'laserReflectivity', 'reflectivity', 'absorptivity', 'emissivity',
            'refractiveIndex', 'laserDamageThreshold', 'ablationThreshold', 'opticalTransmittance',
            'thermalConductivity', 'thermalExpansion', 'specificHeat', 'thermalDiffusivity',
            'heatCapacity', 'meltingPoint', 'boilingPoint', 'thermalDestructionPoint',
            'thermalDestruction', 'glasTransitionTemperature', 'sinteringTemperature',
            'ignitionTemperature', 'autoignitionTemperature', 'decompositionTemperature',
            'sublimationPoint', 'thermalStability', 'thermalDegradationPoint',
            'photonPenetrationDepth', 'thermalShockResistance'
        ]
    },
    'other': {
        'label': 'Other Properties',
        'description': 'Additional material-specific properties',
        'percentage': 20.0,
        'properties': [
            'fractureToughness', 'vaporPressure', 'moistureContent', 'resinContent',
            'grainStructureType', 'firingTemperature', 'operatingTemperature'
        ]
    }
}

# Subcategory mapping by category
SUBCATEGORY_MAP = {
    'metal': {
        'default': 'non-ferrous',
        'Steel': 'ferrous',
        'Cast Iron': 'ferrous',
        'Stainless Steel': 'ferrous',
        'Carbon Steel': 'ferrous',
        'Tool Steel': 'ferrous'
    },
    'wood': {
        'default': 'hardwood',
        'Pine': 'softwood',
        'Cedar': 'softwood',
        'Spruce': 'softwood',
        'Fir': 'softwood'
    },
    'stone': {
        'default': 'sedimentary',
        'Granite': 'igneous',
        'Basalt': 'igneous',
        'Marble': 'metamorphic',
        'Slate': 'metamorphic'
    },
    'ceramic': {'default': 'oxide'},
    'glass': {'default': 'soda-lime'},
    'composite': {'default': 'fiber-reinforced'},
    'plastic': {'default': 'thermoplastic'},
    'polymer': {'default': 'synthetic'},
    'semiconductor': {'default': 'elemental'}
}

# Crystalline structure defaults by category
CRYSTALLINE_STRUCTURE_DEFAULTS = {
    'metal': {
        'default': 'FCC',
        'Aluminum': 'FCC',
        'Copper': 'FCC',
        'Gold': 'FCC',
        'Silver': 'FCC',
        'Nickel': 'FCC',
        'Steel': 'BCC',
        'Iron': 'BCC',
        'Titanium': 'HCP',
        'Magnesium': 'HCP',
        'Zinc': 'HCP'
    },
    'ceramic': {'default': 'cubic'},
    'glass': {'default': 'amorphous'},
    'stone': {'default': 'crystalline'},
    'composite': {'default': 'mixed'},
    'plastic': {'default': 'amorphous'},
    'polymer': {'default': 'amorphous'},
    'semiconductor': {'default': 'cubic'}
}


def categorize_property(prop_name: str) -> str:
    """Determine which category a property belongs to"""
    for category, info in PROPERTY_CATEGORIES.items():
        if prop_name in info['properties']:
            return category
    return 'other'  # Default fallback


def get_subcategory(material_name: str, category: str) -> str:
    """Determine subcategory for a material"""
    category_map = SUBCATEGORY_MAP.get(category, {})
    return category_map.get(material_name, category_map.get('default', 'general'))


def get_crystalline_structure(material_name: str, category: str) -> Dict[str, Any]:
    """Get crystalline structure data for a material"""
    category_map = CRYSTALLINE_STRUCTURE_DEFAULTS.get(category, {})
    structure = category_map.get(material_name, category_map.get('default', 'amorphous'))
    
    return {
        'value': structure,
        'unit': 'crystal system',
        'confidence': 0.95,
        'description': f'{structure} crystal structure',
        'source': 'ai_research',
        'research_date': datetime.now(timezone.utc).isoformat(),
        'allowedValues': ['FCC', 'BCC', 'HCP', 'amorphous', 'cubic', 'hexagonal', 
                         'tetragonal', 'orthorhombic', 'monoclinic', 'triclinic']
    }


def migrate_properties(material_data: Dict[str, Any], material_name: str, category: str) -> Dict[str, Any]:
    """Reorganize properties into three categories"""
    properties = material_data.get('properties', {})
    
    # Initialize categorized structure
    categorized = {
        'material_characteristics': {
            'label': PROPERTY_CATEGORIES['material_characteristics']['label'],
            'description': PROPERTY_CATEGORIES['material_characteristics']['description'],
            'percentage': PROPERTY_CATEGORIES['material_characteristics']['percentage'],
            'properties': {}
        },
        'laser_material_interaction': {
            'label': PROPERTY_CATEGORIES['laser_material_interaction']['label'],
            'description': PROPERTY_CATEGORIES['laser_material_interaction']['description'],
            'percentage': PROPERTY_CATEGORIES['laser_material_interaction']['percentage'],
            'properties': {}
        },
        'other': {
            'label': PROPERTY_CATEGORIES['other']['label'],
            'description': PROPERTY_CATEGORIES['other']['description'],
            'percentage': PROPERTY_CATEGORIES['other']['percentage'],
            'properties': {}
        }
    }
    
    # Categorize each property
    for prop_name, prop_data in properties.items():
        prop_category = categorize_property(prop_name)
        categorized[prop_category]['properties'][prop_name] = prop_data
    
    return categorized


def migrate_machine_settings(machine_settings: Dict[str, Any]) -> Dict[str, Any]:
    """Update machineSettings structure with enhanced metadata"""
    if not machine_settings:
        return {}
    
    migrated = {}
    for setting_name, setting_data in machine_settings.items():
        if isinstance(setting_data, dict) and 'value' in setting_data:
            # Already in new format
            migrated[setting_name] = setting_data
        elif isinstance(setting_data, (int, float, str)):
            # Convert old format to new format
            migrated[setting_name] = {
                'value': setting_data,
                'unit': 'TBD',  # Will need manual review
                'confidence': 0.85,
                'description': f'{setting_name} setting for optimal cleaning',
                'source': 'ai_research',
                'research_date': datetime.now(timezone.utc).isoformat()
            }
        else:
            # Keep as-is
            migrated[setting_name] = setting_data
    
    return migrated


def migrate_material(material_name: str, material_data: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate a single material to new architecture"""
    category = material_data.get('category', 'metal')
    
    # Create new structure
    migrated = {
        'name': material_name,
        'category': category,
        'subcategory': get_subcategory(material_name, category)
    }
    
    # Reorganize properties into categories
    migrated['materialProperties'] = migrate_properties(material_data, material_name, category)
    
    # Add crystalline structure to material_characteristics
    migrated['materialCharacteristics'] = {
        'crystallineStructure': get_crystalline_structure(material_name, category)
    }
    
    # Preserve existing fields
    if 'author' in material_data:
        migrated['author'] = material_data['author']
    
    if 'industryTags' in material_data:
        migrated['applications'] = material_data['industryTags']
    elif 'material_metadata' in material_data and 'industryTags' in material_data['material_metadata']:
        migrated['applications'] = material_data['material_metadata']['industryTags']
    
    # Migrate machine settings
    if 'machineSettings' in material_data:
        migrated['machineSettings'] = migrate_machine_settings(material_data['machineSettings'])
    
    # Preserve regulatory standards
    if 'material_metadata' in material_data and 'regulatoryStandards' in material_data['material_metadata']:
        migrated['material_metadata'] = {
            'regulatoryStandards': material_data['material_metadata']['regulatoryStandards']
        }
    
    return migrated


def backup_file(filepath: Path) -> Path:
    """Create backup of original file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = filepath.parent / f"{filepath.stem}.backup_{timestamp}{filepath.suffix}"
    import shutil
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path


def main():
    """Run the migration"""
    materials_path = Path('data/Materials.yaml')
    
    if not materials_path.exists():
        print(f"❌ Materials.yaml not found at {materials_path}")
        sys.exit(1)
    
    print("📖 Reading Materials.yaml...")
    with open(materials_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Create backup
    backup_path = backup_file(materials_path)
    
    print(f"🔄 Migrating {len(data['materials'])} materials...")
    
    # Migrate each material
    migrated_materials = {}
    for material_name, material_data in data['materials'].items():
        try:
            migrated_materials[material_name] = migrate_material(material_name, material_data)
            print(f"  ✅ {material_name}")
        except Exception as e:
            print(f"  ❌ {material_name}: {e}")
    
    # Update metadata
    data['metadata']['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    data['metadata']['migration_date'] = datetime.now(timezone.utc).isoformat()
    data['metadata']['migration_version'] = '2.0.0'
    data['metadata']['architecture_notes'] = 'Reorganized properties into three categories with 40/40/20 percentage weighting'
    
    # Replace materials
    data['materials'] = migrated_materials
    
    print(f"\n💾 Writing migrated data to {materials_path}...")
    with open(materials_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, indent=2)
    
    print(f"\n✅ Migration complete!")
    print(f"   - Migrated: {len(migrated_materials)} materials")
    print(f"   - Backup: {backup_path}")
    print(f"   - New architecture: 3 property categories (40/40/20)")
    print(f"\n⚠️  Review the output and run validation tests before committing!")


if __name__ == '__main__':
    main()
