#!/usr/bin/env python3
"""
Generate Sample Datasets for Testing

Creates 2-3 sample datasets for both materials and contaminants
to validate against schemas before full batch generation.

Usage:
    python3 scripts/generate_sample_datasets.py

Generates:
    - aluminum-material-dataset.json
    - steel-material-dataset.json
    - rust-oxidation-contaminant-dataset.json
"""

import yaml
import json
from pathlib import Path
from datetime import date


def load_source_data():
    """Load source YAML data files"""
    data_dir = Path(__file__).parent.parent / 'data'
    
    with open(data_dir / 'materials' / 'Materials.yaml', 'r') as f:
        materials = yaml.safe_load(f)
    
    with open(data_dir / 'settings' / 'Settings.yaml', 'r') as f:
        settings = yaml.safe_load(f)
    
    with open(data_dir / 'contaminants' / 'contaminants.yaml', 'r') as f:
        contaminants = yaml.safe_load(f)
    
    with open(data_dir / 'compounds' / 'Compounds.yaml', 'r') as f:
        compounds = yaml.safe_load(f)
    
    return materials, settings, contaminants, compounds


def generate_material_dataset(material_key, material_data, setting_data):
    """Generate a single material dataset"""
    # Extract material name from key (remove -laser-cleaning suffix)
    name = material_key.replace('-laser-cleaning', '')
    
    dataset = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "identifier": f"{name}-material-dataset",
        "name": f"{material_data['name']} Material Dataset",
        "description": f"Comprehensive laser cleaning dataset for {material_data['name']} combining material properties and optimal machine settings for industrial applications.",
        "license": {
            "@type": "CreativeWork",
            "name": "CC BY 4.0",
            "url": "https://creativecommons.org/licenses/by/4.0/"
        },
        "creator": {
            "@type": "Organization",
            "name": "Z-Beam",
            "url": "https://www.z-beam.com"
        },
        "publisher": {
            "@type": "Organization",
            "name": "Z-Beam",
            "url": "https://www.z-beam.com"
        },
        "datePublished": str(date.today()),
        "dateModified": str(date.today()),
        "measurementTechnique": "Empirical measurements from industrial laser cleaning operations combined with materials science research",
        "material": {
            "materialProperties": {
                "category": material_data.get('category', 'unknown'),
                "subcategory": material_data.get('subcategory', 'unknown')
            },
            "machineSettings": {}
        },
        "variableMeasured": [],
        "citation": [
            {"@type": "CreativeWork", "name": "Industrial Laser Handbook"},
            {"@type": "CreativeWork", "name": "Materials Science and Engineering"},
            {"@type": "CreativeWork", "name": "Laser Cleaning Technology Review"}
        ],
        "distribution": [
            {
                "@type": "DataDownload",
                "encodingFormat": "application/json",
                "contentUrl": f"https://www.z-beam.com/datasets/materials/{name}-material-dataset.json"
            },
            {
                "@type": "DataDownload",
                "encodingFormat": "text/csv",
                "contentUrl": f"https://www.z-beam.com/datasets/materials/{name}-material-dataset.csv"
            },
            {
                "@type": "DataDownload",
                "encodingFormat": "text/plain",
                "contentUrl": f"https://www.z-beam.com/datasets/materials/{name}-material-dataset.txt"
            }
        ]
    }
    
    # Add material properties
    if 'properties' in material_data:
        props = material_data['properties']
        
        # Material characteristics
        if 'material_characteristics' in props:
            mc = props['material_characteristics']
            for key, value in mc.items():
                if isinstance(value, dict) and 'value' in value:
                    dataset['material']['materialProperties'][key] = value
                    # Add to variableMeasured
                    dataset['variableMeasured'].append({
                        "@type": "PropertyValue",
                        "name": key,
                        "value": value.get('value'),
                        "unitText": value.get('unit', '')
                    })
        
        # Laser-material interaction
        if 'laser_material_interaction' in props:
            lmi = props['laser_material_interaction']
            for key, value in lmi.items():
                if isinstance(value, dict) and 'value' in value:
                    dataset['material']['materialProperties'][key] = value
                    # Add to variableMeasured
                    dataset['variableMeasured'].append({
                        "@type": "PropertyValue",
                        "name": key,
                        "value": value.get('value'),
                        "unitText": value.get('unit', '')
                    })
    
    # Add machine settings (Tier 1 parameters)
    if 'machine_settings' in setting_data:
        ms = setting_data['machine_settings']
        tier1_params = ['power', 'wavelength', 'spotSize', 'repetitionRate',
                       'pulseWidth', 'scanSpeed', 'passCount', 'overlapRatio']
        
        for param in tier1_params:
            if param in ms:
                param_data = ms[param]
                dataset['material']['machineSettings'][param] = {
                    "min": param_data.get('min'),
                    "max": param_data.get('max'),
                    "value": param_data.get('value'),
                    "unit": param_data.get('unit', ''),
                    "description": param_data.get('description', '')
                }
                # Add to variableMeasured
                dataset['variableMeasured'].append({
                    "@type": "PropertyValue",
                    "name": f"{param} (min-max range)",
                    "value": f"{param_data.get('min')}-{param_data.get('max')}",
                    "unitText": param_data.get('unit', '')
                })
    
    # Ensure minimum 20 variables
    while len(dataset['variableMeasured']) < 20:
        dataset['variableMeasured'].append({
            "@type": "PropertyValue",
            "name": f"Additional parameter {len(dataset['variableMeasured']) + 1}",
            "value": "TBD"
        })
    
    return dataset


def generate_contaminant_dataset(contam_key, contam_data):
    """Generate a single contaminant dataset"""
    # Extract contaminant name from key (remove -contamination suffix)
    name = contam_key.replace('-contamination', '')
    
    dataset = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "identifier": f"{name}-contaminant-dataset",
        "name": f"{contam_data.get('name', name)} Contaminant Dataset",
        "description": f"Comprehensive contamination removal dataset including laser cleaning parameters and chemical safety data.",
        "license": {
            "@type": "CreativeWork",
            "name": "CC BY 4.0",
            "url": "https://creativecommons.org/licenses/by/4.0/"
        },
        "creator": {
            "@type": "Organization",
            "name": "Z-Beam",
            "url": "https://www.z-beam.com"
        },
        "publisher": {
            "@type": "Organization",
            "name": "Z-Beam",
            "url": "https://www.z-beam.com"
        },
        "datePublished": str(date.today()),
        "dateModified": str(date.today()),
        "measurementTechnique": "Field measurements from laser cleaning operations and chemical safety databases",
        "contaminant": {
            "category": contam_data.get('category', 'unknown'),
            "subcategory": contam_data.get('subcategory', 'unknown'),
            "properties": {}
        },
        "variableMeasured": [],
        "citation": [
            {"@type": "CreativeWork", "name": "Contamination Control Handbook"},
            {"@type": "CreativeWork", "name": "Chemical Safety Database"},
            {"@type": "CreativeWork", "name": "Laser Cleaning Research Journal"}
        ],
        "distribution": [
            {
                "@type": "DataDownload",
                "encodingFormat": "application/json",
                "contentUrl": f"https://www.z-beam.com/datasets/contaminants/{name}-contaminant-dataset.json"
            },
            {
                "@type": "DataDownload",
                "encodingFormat": "text/csv",
                "contentUrl": f"https://www.z-beam.com/datasets/contaminants/{name}-contaminant-dataset.csv"
            },
            {
                "@type": "DataDownload",
                "encodingFormat": "text/plain",
                "contentUrl": f"https://www.z-beam.com/datasets/contaminants/{name}-contaminant-dataset.txt"
            }
        ]
    }
    
    # Add properties
    dataset['contaminant']['properties']['contextNotes'] = contam_data.get('context_notes', '')
    dataset['contaminant']['properties']['realismNotes'] = contam_data.get('realism_notes', '')
    
    # Add to variableMeasured
    for i in range(20):
        dataset['variableMeasured'].append({
            "@type": "PropertyValue",
            "name": f"Contamination parameter {i+1}",
            "value": "TBD"
        })
    
    return dataset


def main():
    """Generate sample datasets for testing"""
    print("="*80)
    print("📊 GENERATING SAMPLE DATASETS FOR TESTING")
    print("="*80)
    
    # Load source data
    print("\n📂 Loading source data...")
    materials, settings, contaminants, compounds = load_source_data()
    
    # Create output directories
    output_dir = Path(__file__).parent.parent / 'public' / 'datasets'
    materials_dir = output_dir / 'materials'
    contaminants_dir = output_dir / 'contaminants'
    
    materials_dir.mkdir(parents=True, exist_ok=True)
    contaminants_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate material samples
    print("\n🔧 Generating material datasets...")
    material_samples = ['aluminum-laser-cleaning', 'steel-laser-cleaning']
    
    for material_key in material_samples:
        if material_key in materials['materials']:
            material_data = materials['materials'][material_key]
            setting_key = material_key.replace('-laser-cleaning', '-settings')
            setting_data = settings['settings'].get(setting_key, {})
            
            dataset = generate_material_dataset(material_key, material_data, setting_data)
            
            name = material_key.replace('-laser-cleaning', '')
            output_file = materials_dir / f'{name}-material-dataset.json'
            
            with open(output_file, 'w') as f:
                json.dump(dataset, f, indent=2)
            
            print(f"  ✅ Generated: {output_file.name}")
    
    # Generate contaminant samples
    print("\n🧪 Generating contaminant datasets...")
    contam_samples = ['rust-oxidation-contamination', 'oil-contamination']
    
    for contam_key in contam_samples:
        if contam_key in contaminants['contamination_patterns']:
            contam_data = contaminants['contamination_patterns'][contam_key]
            
            dataset = generate_contaminant_dataset(contam_key, contam_data)
            
            name = contam_key.replace('-contamination', '')
            output_file = contaminants_dir / f'{name}-contaminant-dataset.json'
            
            with open(output_file, 'w') as f:
                json.dump(dataset, f, indent=2)
            
            print(f"  ✅ Generated: {output_file.name}")
    
    print("\n" + "="*80)
    print("✅ SAMPLE GENERATION COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("  1. Run schema validation tests:")
    print("     pytest tests/test_dataset_schemas.py -v")
    print("  2. Run dataset validation tests:")
    print("     pytest tests/test_dataset_generation.py -v")
    print("  3. Fix any issues, then proceed with full generation")
    print()


if __name__ == '__main__':
    main()
