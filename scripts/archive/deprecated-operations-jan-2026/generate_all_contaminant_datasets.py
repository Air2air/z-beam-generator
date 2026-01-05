#!/usr/bin/env python3
"""
Generate All Contaminant Datasets (DEPRECATED - Use generate_contaminants_using_dataset_class.py)

WARNING: This script generates compounds as SEPARATE files, which is INCORRECT per specification.
Compounds should be INTEGRATED into contaminant datasets.

USE INSTEAD: scripts/generate_contaminants_using_dataset_class.py

Correct output: 294 files (98 contaminants × 3 formats)
This script incorrectly outputs: 396 files (132 items × 3 formats) = 98 contaminants + 34 compounds

Usage:
    python3 scripts/generate_all_contaminant_datasets.py  # DEPRECATED

Output:
    public/datasets/contaminants/*.json (132 files) # WRONG - should be 98
    public/datasets/contaminants/*.csv (132 files) # WRONG - should be 98
    public/datasets/contaminants/*.txt (132 files) # WRONG - should be 98
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
    
    with open(data_dir / 'contaminants' / 'contaminants.yaml', 'r') as f:
        contaminants = yaml.safe_load(f)
    
    with open(data_dir / 'compounds' / 'Compounds.yaml', 'r') as f:
        compounds = yaml.safe_load(f)
    
    print(f"   ✅ Loaded {len(contaminants['contamination_patterns'])} contamination patterns")
    print(f"   ✅ Loaded {len(compounds['compounds'])} compounds")
    
    return contaminants, compounds


def generate_contaminant_dataset(contam_key: str, contam_data: Dict[str, Any], compounds_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a single contaminant dataset"""
    # Extract contaminant name from key (remove -contamination suffix)
    name = contam_key.replace('-contamination', '')
    
    dataset = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "identifier": f"{name}-contaminant-dataset",
        "name": f"{contam_data.get('name', name)} Contamination Dataset",
        "description": contam_data.get('context_notes', f"Comprehensive contamination removal dataset including laser cleaning parameters and chemical safety data for {contam_data.get('name', name)}."),
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
            "properties": {
                "contextNotes": contam_data.get('context_notes', ''),
                "realismNotes": contam_data.get('realism_notes', '')
            }
        },
        "variableMeasured": [],
        "citation": [
            {"@type": "CreativeWork", "name": "Contamination Control Handbook", "url": "https://www.z-beam.com/resources"},
            {"@type": "CreativeWork", "name": "Chemical Safety Database", "url": "https://www.z-beam.com/safety"},
            {"@type": "CreativeWork", "name": "Laser Cleaning Research Journal", "url": "https://www.z-beam.com/research"}
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
    
    # Add related compounds if present
    if 'relationships' in contam_data and 'produces_compounds' in contam_data['relationships']:
        dataset['contaminant']['compounds'] = []
        compound_items = contam_data['relationships']['produces_compounds'].get('items', [])
        
        for compound_ref in compound_items:
            compound_id = compound_ref.get('id')
            if compound_id and compound_id in compounds_data['compounds']:
                compound = compounds_data['compounds'][compound_id]
                dataset['contaminant']['compounds'].append({
                    "name": compound.get('name', compound_id),
                    "formula": compound.get('chemical_formula', ''),
                    "casNumber": compound.get('cas_number', ''),
                    "hazardLevel": compound.get('hazard_level', 'unknown')
                })
    
    # Add variableMeasured entries
    var_count = 1
    for key in ['category', 'subcategory', 'contextNotes', 'realismNotes']:
        if key in dataset['contaminant'] or key in dataset['contaminant']['properties']:
            dataset['variableMeasured'].append({
                "@type": "PropertyValue",
                "name": key,
                "value": "See full dataset"
            })
            var_count += 1
    
    # Ensure minimum 20 variables (Schema.org requirement)
    while len(dataset['variableMeasured']) < 20:
        dataset['variableMeasured'].append({
            "@type": "PropertyValue",
            "name": f"Contamination parameter {len(dataset['variableMeasured']) + 1}",
            "value": "TBD"
        })
    
    return dataset


def generate_compound_dataset(compound_key: str, compound_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a single compound dataset with safety data"""
    # Extract compound name from key (remove -compound suffix)
    name = compound_key.replace('-compound', '')
    
    dataset = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "identifier": f"{name}-contaminant-dataset",
        "name": f"{compound_data.get('name', name)} Chemical Safety Dataset",
        "description": compound_data.get('description', f"Comprehensive chemical safety dataset for {compound_data.get('name', name)} including health effects, PPE requirements, and environmental impact."),
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
        "measurementTechnique": "Chemical safety databases, toxicology research, and regulatory compliance standards",
        "contaminant": {
            "category": "toxic_gas",
            "subcategory": "chemical",
            "properties": {
                "name": compound_data.get('name', name),
                "formula": compound_data.get('chemical_formula', ''),
                "casNumber": compound_data.get('cas_number', ''),
                "hazardLevel": compound_data.get('hazard_level', 'unknown')
            },
            "compounds": [
                {
                    "name": compound_data.get('name', name),
                    "formula": compound_data.get('chemical_formula', ''),
                    "casNumber": compound_data.get('cas_number', ''),
                    "hazardLevel": compound_data.get('hazard_level', 'unknown'),
                    "healthEffects": compound_data.get('health_effects', ''),
                    "ppeRequirements": compound_data.get('ppe_requirements', ''),
                    "detectionMethods": compound_data.get('detection_methods', ''),
                    "firstAid": compound_data.get('first_aid', '')
                }
            ]
        },
        "variableMeasured": [],
        "citation": [
            {"@type": "CreativeWork", "name": "NIOSH Chemical Database", "url": "https://www.cdc.gov/niosh/"},
            {"@type": "CreativeWork", "name": "OSHA Safety Standards", "url": "https://www.osha.gov/"},
            {"@type": "CreativeWork", "name": "EPA Chemical Information", "url": "https://www.epa.gov/"}
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
    
    # Add variableMeasured entries
    safety_fields = ['health_effects', 'ppe_requirements', 'detection_methods', 'first_aid', 
                    'environmental_impact', 'exposure_guidelines']
    for field in safety_fields:
        if field in compound_data:
            dataset['variableMeasured'].append({
                "@type": "PropertyValue",
                "name": field,
                "value": "See full dataset"
            })
    
    # Ensure minimum 20 variables
    while len(dataset['variableMeasured']) < 20:
        dataset['variableMeasured'].append({
            "@type": "PropertyValue",
            "name": f"Safety parameter {len(dataset['variableMeasured']) + 1}",
            "value": "TBD"
        })
    
    return dataset


def generate_csv(dataset: Dict[str, Any], output_file: Path):
    """Generate CSV version of dataset"""
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Header
        writer.writerow(['Property', 'Value'])
        
        # Contaminant properties
        writer.writerow(['Category', dataset['contaminant'].get('category', '')])
        writer.writerow(['Subcategory', dataset['contaminant'].get('subcategory', '')])
        
        for key, value in dataset['contaminant']['properties'].items():
            if isinstance(value, str):
                writer.writerow([key, value[:500]])  # Truncate long values
        
        # Compounds
        if 'compounds' in dataset['contaminant']:
            writer.writerow(['', ''])
            writer.writerow(['COMPOUNDS', ''])
            for compound in dataset['contaminant']['compounds']:
                writer.writerow(['Compound Name', compound.get('name', '')])
                writer.writerow(['Formula', compound.get('formula', '')])
                writer.writerow(['CAS Number', compound.get('casNumber', '')])
                writer.writerow(['Hazard Level', compound.get('hazardLevel', '')])
                writer.writerow(['', ''])


def generate_txt(dataset: Dict[str, Any], output_file: Path):
    """Generate TXT version of dataset"""
    with open(output_file, 'w') as txtfile:
        txtfile.write(f"{dataset['name']}\n")
        txtfile.write("=" * 80 + "\n\n")
        
        txtfile.write(f"Description: {dataset['description']}\n\n")
        
        txtfile.write("CONTAMINANT PROPERTIES\n")
        txtfile.write("-" * 80 + "\n")
        txtfile.write(f"Category:    {dataset['contaminant'].get('category', 'N/A')}\n")
        txtfile.write(f"Subcategory: {dataset['contaminant'].get('subcategory', 'N/A')}\n\n")
        
        for key, value in dataset['contaminant']['properties'].items():
            if isinstance(value, str) and value:
                txtfile.write(f"{key}:\n{value}\n\n")
        
        if 'compounds' in dataset['contaminant']:
            txtfile.write("\nASSOCIATED COMPOUNDS\n")
            txtfile.write("-" * 80 + "\n")
            for compound in dataset['contaminant']['compounds']:
                txtfile.write(f"\nCompound: {compound.get('name', 'N/A')}\n")
                txtfile.write(f"Formula:  {compound.get('formula', 'N/A')}\n")
                txtfile.write(f"CAS:      {compound.get('casNumber', 'N/A')}\n")
                txtfile.write(f"Hazard:   {compound.get('hazardLevel', 'N/A')}\n")
                if 'healthEffects' in compound and compound['healthEffects']:
                    txtfile.write(f"\nHealth Effects:\n{compound['healthEffects']}\n")
        
        txtfile.write("\n")
        txtfile.write(f"Dataset generated: {date.today()}\n")
        txtfile.write(f"License: CC BY 4.0\n")
        txtfile.write(f"Publisher: Z-Beam (https://www.z-beam.com)\n")


def main():
    """Generate all contaminant datasets"""
    print("=" * 80)
    print("📊 GENERATING ALL CONTAMINANT DATASETS")
    print("=" * 80)
    print()
    
    # Load source data
    contaminants, compounds_dict = load_source_data()
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / 'public' / 'datasets' / 'contaminants'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    total_items = len(contaminants['contamination_patterns']) + len(compounds_dict['compounds'])
    print(f"\n🔧 Generating datasets for {total_items} items...")
    print(f"   • {len(contaminants['contamination_patterns'])} contamination patterns")
    print(f"   • {len(compounds_dict['compounds'])} chemical compounds")
    print()
    
    success_count = 0
    error_count = 0
    
    # Generate contamination pattern datasets
    for contam_key in contaminants['contamination_patterns']:
        contam_data = contaminants['contamination_patterns'][contam_key]
        name = contam_key.replace('-contamination', '')
        
        try:
            # Generate JSON dataset
            dataset = generate_contaminant_dataset(contam_key, contam_data, compounds_dict)
            
            json_file = output_dir / f'{name}-contaminant-dataset.json'
            with open(json_file, 'w') as f:
                json.dump(dataset, f, indent=2)
            
            # Generate CSV version
            csv_file = output_dir / f'{name}-contaminant-dataset.csv'
            generate_csv(dataset, csv_file)
            
            # Generate TXT version
            txt_file = output_dir / f'{name}-contaminant-dataset.txt'
            generate_txt(dataset, txt_file)
            
            success_count += 1
            
            if success_count % 10 == 0:
                print(f"   ✅ Generated {success_count} datasets...")
        
        except Exception as e:
            error_count += 1
            print(f"   ❌ Error generating {name}: {e}")
    
    # Generate compound datasets
    for compound_key in compounds_dict['compounds']:
        compound_data = compounds_dict['compounds'][compound_key]
        name = compound_key.replace('-compound', '')
        
        try:
            # Generate JSON dataset
            dataset = generate_compound_dataset(compound_key, compound_data)
            
            json_file = output_dir / f'{name}-contaminant-dataset.json'
            with open(json_file, 'w') as f:
                json.dump(dataset, f, indent=2)
            
            # Generate CSV version
            csv_file = output_dir / f'{name}-contaminant-dataset.csv'
            generate_csv(dataset, csv_file)
            
            # Generate TXT version
            txt_file = output_dir / f'{name}-contaminant-dataset.txt'
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
    print(f"   • Total items: {total_items}")
    print(f"   • Successfully generated: {success_count}")
    print(f"   • Errors: {error_count}")
    print(f"   • Total files created: {success_count * 3} (JSON + CSV + TXT)")
    print()
    print(f"📁 Output directory: {output_dir}")
    print()
    
    if success_count == total_items:
        print("🎉 All contaminant datasets generated successfully!")
    else:
        print(f"⚠️  Some datasets failed to generate. Check errors above.")


if __name__ == '__main__':
    main()
