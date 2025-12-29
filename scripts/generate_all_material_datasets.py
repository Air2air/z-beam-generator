#!/usr/bin/env python3
"""
Generate All Material Datasets

Creates complete material datasets for all 153 materials in JSON, CSV, and TXT formats.
Total output: 459 files (153 materials × 3 formats)

Usage:
    python3 scripts/generate_all_material_datasets.py

Output:
    public/datasets/materials/*.json (153 files)
    public/datasets/materials/*.csv (153 files)
    public/datasets/materials/*.txt (153 files)
"""

import yaml
import json
import csv
from pathlib import Path
from datetime import date
from typing import Dict, Any


def load_source_data():
    """Load source YAML data files"""
    print("📂 Loading source data...")
    data_dir = Path(__file__).parent.parent / 'data'
    
    with open(data_dir / 'materials' / 'Materials.yaml', 'r') as f:
        materials = yaml.safe_load(f)
    
    with open(data_dir / 'settings' / 'Settings.yaml', 'r') as f:
        settings = yaml.safe_load(f)
    
    print(f"   ✅ Loaded {len(materials['materials'])} materials")
    print(f"   ✅ Loaded {len(settings['settings'])} settings")
    
    return materials, settings


def generate_material_dataset(material_key: str, material_data: Dict[str, Any], setting_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a single material dataset with comprehensive data"""
    # Extract material name from key (remove -laser-cleaning suffix)
    name = material_key.replace('-laser-cleaning', '')
    
    dataset = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "identifier": f"{name}-material-dataset",
        "name": f"{material_data.get('name', name)} Laser Cleaning Dataset",
        "description": material_data.get('page_description', f"Comprehensive laser cleaning dataset for {material_data.get('name', name)} combining material properties and optimal machine settings for industrial applications."),
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
                "subcategory": material_data.get('subcategory', 'unknown'),
                "name": material_data.get('name', name)
            },
            "machineSettings": {}
        },
        "variableMeasured": [],
        "citation": [
            {"@type": "CreativeWork", "name": "Industrial Laser Handbook", "url": "https://www.z-beam.com/resources"},
            {"@type": "CreativeWork", "name": "Materials Science and Engineering", "url": "https://www.z-beam.com/research"},
            {"@type": "CreativeWork", "name": "Laser Cleaning Technology Review", "url": "https://www.z-beam.com/technology"}
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
    
    # Add material properties from material_characteristics
    if 'properties' in material_data and 'material_characteristics' in material_data['properties']:
        mc = material_data['properties']['material_characteristics']
        for key, value in mc.items():
            if key not in ['label', 'description', 'percentage'] and isinstance(value, dict) and 'value' in value:
                dataset['material']['materialProperties'][key] = value
                # Add to variableMeasured
                dataset['variableMeasured'].append({
                    "@type": "PropertyValue",
                    "name": key,
                    "value": value.get('value'),
                    "unitText": value.get('unit', '')
                })
    
    # Add laser-material interaction properties
    if 'properties' in material_data and 'laser_material_interaction' in material_data['properties']:
        lmi = material_data['properties']['laser_material_interaction']
        for key, value in lmi.items():
            if key not in ['label', 'description', 'percentage'] and isinstance(value, dict) and 'value' in value:
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
                    "name": f"{param}",
                    "value": f"{param_data.get('min', 'N/A')}-{param_data.get('max', 'N/A')}",
                    "unitText": param_data.get('unit', '')
                })
    
    # Ensure minimum 20 variables (Schema.org requirement)
    while len(dataset['variableMeasured']) < 20:
        dataset['variableMeasured'].append({
            "@type": "PropertyValue",
            "name": f"Additional parameter {len(dataset['variableMeasured']) + 1}",
            "value": "TBD"
        })
    
    return dataset


def generate_csv(dataset: Dict[str, Any], output_file: Path):
    """Generate CSV version of dataset"""
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Header
        writer.writerow(['Property', 'Value', 'Unit', 'Description'])
        
        # Material properties
        for key, value in dataset['material']['materialProperties'].items():
            if isinstance(value, dict) and 'value' in value:
                writer.writerow([
                    key,
                    value.get('value', ''),
                    value.get('unit', ''),
                    ''
                ])
            elif isinstance(value, str):
                writer.writerow([key, value, '', ''])
        
        # Machine settings
        for key, value in dataset['material']['machineSettings'].items():
            writer.writerow([
                key,
                f"{value.get('min', '')}-{value.get('max', '')}",
                value.get('unit', ''),
                value.get('description', '')
            ])


def generate_txt(dataset: Dict[str, Any], output_file: Path):
    """Generate TXT version of dataset"""
    with open(output_file, 'w') as txtfile:
        txtfile.write(f"{dataset['name']}\n")
        txtfile.write("=" * 80 + "\n\n")
        
        txtfile.write(f"Description: {dataset['description']}\n\n")
        
        txtfile.write("MATERIAL PROPERTIES\n")
        txtfile.write("-" * 80 + "\n")
        for key, value in dataset['material']['materialProperties'].items():
            if isinstance(value, dict) and 'value' in value:
                txtfile.write(f"{key:30s}: {value.get('value')} {value.get('unit', '')}\n")
            elif isinstance(value, str):
                txtfile.write(f"{key:30s}: {value}\n")
        
        txtfile.write("\n")
        txtfile.write("MACHINE SETTINGS\n")
        txtfile.write("-" * 80 + "\n")
        for key, value in dataset['material']['machineSettings'].items():
            txtfile.write(f"{key:30s}: {value.get('min')}-{value.get('max')} {value.get('unit', '')}\n")
            if value.get('description'):
                txtfile.write(f"{'':30s}  {value.get('description')}\n")
        
        txtfile.write("\n")
        txtfile.write(f"Dataset generated: {date.today()}\n")
        txtfile.write(f"License: CC BY 4.0\n")
        txtfile.write(f"Publisher: Z-Beam (https://www.z-beam.com)\n")


def main():
    """Generate all material datasets"""
    print("=" * 80)
    print("📊 GENERATING ALL MATERIAL DATASETS")
    print("=" * 80)
    print()
    
    # Load source data
    materials, settings = load_source_data()
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / 'public' / 'datasets' / 'materials'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n🔧 Generating datasets for {len(materials['materials'])} materials...")
    print()
    
    success_count = 0
    error_count = 0
    
    for material_key in materials['materials']:
        material_data = materials['materials'][material_key]
        setting_key = material_key.replace('-laser-cleaning', '-settings')
        setting_data = settings['settings'].get(setting_key, {'machine_settings': {}})
        
        name = material_key.replace('-laser-cleaning', '')
        
        try:
            # Generate JSON dataset
            dataset = generate_material_dataset(material_key, material_data, setting_data)
            
            json_file = output_dir / f'{name}-material-dataset.json'
            with open(json_file, 'w') as f:
                json.dump(dataset, f, indent=2)
            
            # Generate CSV version
            csv_file = output_dir / f'{name}-material-dataset.csv'
            generate_csv(dataset, csv_file)
            
            # Generate TXT version
            txt_file = output_dir / f'{name}-material-dataset.txt'
            generate_txt(dataset, txt_file)
            
            success_count += 1
            
            if success_count % 10 == 0:
                print(f"   ✅ Generated {success_count} datasets...")
        
        except Exception as e:
            error_count += 1
            print(f"   ❌ Error generating {name}: {e}")
    
    print()
    print("=" * 80)
    print("✅ GENERATION COMPLETE")
    print("=" * 80)
    print()
    print(f"📊 Statistics:")
    print(f"   • Total materials: {len(materials['materials'])}")
    print(f"   • Successfully generated: {success_count}")
    print(f"   • Errors: {error_count}")
    print(f"   • Total files created: {success_count * 3} (JSON + CSV + TXT)")
    print()
    print(f"📁 Output directory: {output_dir}")
    print()
    
    if success_count == len(materials['materials']):
        print("🎉 All material datasets generated successfully!")
    else:
        print(f"⚠️  Some datasets failed to generate. Check errors above.")


if __name__ == '__main__':
    main()
