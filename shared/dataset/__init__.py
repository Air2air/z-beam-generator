"""
Dataset Module - Dynamic Field Detection

Automatically detects all fields in YAML data and generates Schema.org datasets
without hardcoded field lists.

Usage:
    from shared.dataset import MaterialsDataset, ContaminantsDataset
    
    # Materials dataset
    materials = MaterialsDataset()
    material_data = materials.get_material('aluminum')
    json_data = materials.to_schema_org_json('aluminum', material_data)
    csv_rows = materials.to_csv_rows(material_data)
    txt_content = materials.to_txt('aluminum', material_data)
    
    # Contaminants dataset (with compounds merged)
    contaminants = ContaminantsDataset()
    pattern_data = contaminants.get_contaminant('rust')
    enriched_data = contaminants.merge_compounds(pattern_data)
    json_data = contaminants.to_schema_org_json('rust', enriched_data)

Features:
- Zero hardcoding: No skip lists or field name checks
- Dynamic detection: Automatically detects all YAML fields
- Type-aware: Ranges, property values, objects, arrays
- Metadata exclusion: Automatically filters metadata fields
- Schema.org compliant: Proper PropertyValue structures
- Multi-format: JSON, CSV, TXT output
- ADR 005 compliant: Materials+Settings, Contaminants+Compounds merged
"""

from shared.dataset.base_dataset import BaseDataset
from shared.dataset.materials_dataset import MaterialsDataset
from shared.dataset.contaminants_dataset import ContaminantsDataset

__all__ = [
    'BaseDataset',
    'MaterialsDataset',
    'ContaminantsDataset'
]
