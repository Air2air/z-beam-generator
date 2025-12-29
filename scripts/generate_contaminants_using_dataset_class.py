#!/usr/bin/env python3
"""
Generate All Contaminant Datasets Using ContaminantsDataset Class

This script properly uses the ContaminantsDataset class to generate datasets
with the correct nested structure (properties, compounds, removalTechniques).

Usage:
    python3 scripts/generate_contaminants_using_dataset_class.py

Output:
    public/datasets/contaminants/*.json (98 files)
    public/datasets/contaminants/*.csv (98 files)
    public/datasets/contaminants/*.txt (98 files)
    
Total: 294 files (98 contaminants × 3 formats)
"""

import json
import csv
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from shared.dataset.contaminants_dataset import ContaminantsDataset


def generate_csv(dataset_json: dict, output_file: Path):
    """Generate CSV version from JSON dataset"""
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Header
        writer.writerow(['Property', 'Value'])
        
        # Basic fields
        writer.writerow(['Name', dataset_json.get('name', '')])
        writer.writerow(['Description', dataset_json.get('description', '')])
        
        # Contaminant properties
        if 'contaminant' in dataset_json:
            contaminant = dataset_json['contaminant']
            writer.writerow(['Category', contaminant.get('category', '')])
            writer.writerow(['Subcategory', contaminant.get('subcategory', '')])
            
            # Properties section
            if 'properties' in contaminant:
                props = contaminant['properties']
                for key, value in props.items():
                    writer.writerow([key, value])
            
            # Compounds section
            if 'compounds' in contaminant:
                compounds = contaminant['compounds']
                writer.writerow([f'Total Compounds', len(compounds)])
                for i, compound in enumerate(compounds[:5], 1):  # First 5
                    writer.writerow([f'Compound {i}', compound.get('name', '')])
            
            # Removal Techniques section
            if 'removalTechniques' in contaminant:
                techniques = contaminant['removalTechniques']
                for key, value in techniques.items():
                    writer.writerow([key, value])
        
        # Variable measured
        var_measured = dataset_json.get('variableMeasured', [])
        writer.writerow(['Variable Measured Count', len(var_measured)])


def generate_txt(dataset_json: dict, output_file: Path):
    """Generate TXT version from JSON dataset"""
    with open(output_file, 'w') as f:
        f.write(f"# {dataset_json.get('name', '')}\n\n")
        f.write(f"{dataset_json.get('description', '')}\n\n")
        
        if 'contaminant' in dataset_json:
            contaminant = dataset_json['contaminant']
            
            f.write(f"## Category\n")
            f.write(f"{contaminant.get('category', '')} / {contaminant.get('subcategory', '')}\n\n")
            
            # Properties
            if 'properties' in contaminant:
                f.write(f"## Properties\n")
                for key, value in contaminant['properties'].items():
                    f.write(f"- {key}: {value}\n")
                f.write("\n")
            
            # Compounds
            if 'compounds' in contaminant:
                compounds = contaminant['compounds']
                f.write(f"## Compounds ({len(compounds)} total)\n")
                for compound in compounds[:10]:  # First 10
                    f.write(f"- {compound.get('name', '')}\n")
                if len(compounds) > 10:
                    f.write(f"- ... and {len(compounds) - 10} more\n")
                f.write("\n")
            
            # Removal Techniques
            if 'removalTechniques' in contaminant:
                f.write(f"## Laser Removal Techniques\n")
                techniques = contaminant['removalTechniques']
                for key, value in techniques.items():
                    f.write(f"- {key}: {value}\n")
                f.write("\n")
        
        # Variable measured
        var_measured = dataset_json.get('variableMeasured', [])
        f.write(f"## Data Variables\n")
        f.write(f"Total variables measured: {len(var_measured)}\n")


def main():
    print("=" * 80)
    print("📊 GENERATING CONTAMINANT DATASETS USING ContaminantsDataset CLASS")
    print("=" * 80)
    print()
    
    # Initialize dataset
    dataset = ContaminantsDataset()
    
    # Get all contaminants
    print("📂 Loading contaminants...")
    contaminants = dataset.get_all_contaminants()
    print(f"   ✅ Loaded {len(contaminants)} contaminants")
    print()
    
    # Setup output directory
    output_dir = Path(__file__).resolve().parents[1] / 'public' / 'datasets' / 'contaminants'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate datasets
    print(f"🔧 Generating datasets for {len(contaminants)} contaminants...")
    print()
    
    success_count = 0
    error_count = 0
    
    for contaminant_id in contaminants:
        contaminant_data = contaminants[contaminant_id]
        
        # Get slug for filename (remove -contamination suffix)
        slug = contaminant_id.replace('-contamination', '')
        
        try:
            # Generate JSON using ContaminantsDataset class
            json_data = dataset.to_schema_org_json(contaminant_id, contaminant_data)
            
            # Save JSON
            json_file = output_dir / f'{slug}-contaminant-dataset.json'
            with open(json_file, 'w') as f:
                json.dump(json_data, f, indent=2)
            
            # Generate CSV
            csv_file = output_dir / f'{slug}-contaminant-dataset.csv'
            generate_csv(json_data, csv_file)
            
            # Generate TXT
            txt_file = output_dir / f'{slug}-contaminant-dataset.txt'
            generate_txt(json_data, txt_file)
            
            success_count += 1
            
            if success_count % 10 == 0:
                print(f"   ✅ Generated {success_count} datasets...")
        
        except Exception as e:
            error_count += 1
            print(f"   ❌ Error generating {slug}: {e}")
    
    print()
    print("=" * 80)
    print("✅ GENERATION COMPLETE")
    print("=" * 80)
    print()
    print(f"📊 Statistics:")
    print(f"   • Total contaminants: {len(contaminants)}")
    print(f"   • Successfully generated: {success_count}")
    print(f"   • Errors: {error_count}")
    print(f"   • Total files created: {success_count * 3} (JSON + CSV + TXT)")
    print()
    print(f"📁 Output directory: {output_dir}")
    print()
    
    if success_count == len(contaminants):
        print("🎉 All contaminant datasets generated successfully!")
        print()
        print("✅ All datasets have nested structure:")
        print("   • contaminant.properties (contaminant characteristics)")
        print("   • contaminant.compounds (chemical safety data from Compounds.yaml)")
        print("   • contaminant.removalTechniques (laser parameters)")
    else:
        print(f"⚠️  {error_count} datasets failed to generate")


if __name__ == '__main__':
    main()
