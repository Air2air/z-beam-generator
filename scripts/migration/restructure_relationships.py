#!/usr/bin/env python3
"""
Phase 2: Restructure Relationships in All Entities

Converts relationship structure from:
  relationship_key:
    - id: entity-id
      presentation: card
      url: /path/to/entity

To:
  relationship_key:
    presentation: card
    items:
      - id: entity-id

This removes redundant data (presentation, url) and normalizes structure.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import yaml
from typing import Dict, Any, List


class RelationshipRestructurer:
    """Restructure relationships to new format."""
    
    def __init__(self):
        self.stats = {
            'presentation_moved': 0,
            'urls_removed': 0,
            'items_wrapped': 0,
            'intrinsic_props_removed': 0
        }
        
        # Properties that should NOT be in relationship items (entity intrinsic)
        self.intrinsic_properties = {
            'hazard_level', 'phase', 'state', 'color', 'texture',
            'molecular_weight', 'boiling_point', 'melting_point',
            'density', 'viscosity', 'flash_point'
        }
    
    def restructure_relationship(self, relationship_data: Any) -> Dict[str, Any]:
        """
        Restructure a single relationship from old to new format.
        
        Args:
            relationship_data: Original relationship data (list or dict)
        
        Returns:
            Restructured relationship with presentation at key level
        """
        # Handle None or empty
        if relationship_data is None or relationship_data == []:
            return None
        
        # Handle _section or metadata keys
        if isinstance(relationship_data, dict) and '_section' in relationship_data:
            # Already has _section structure
            items = relationship_data.get('items', [])
            section = relationship_data.get('_section')
        elif isinstance(relationship_data, list):
            # Flat list of items
            items = relationship_data
            section = None
        else:
            # Unknown structure, skip
            return relationship_data
        
        # Detect presentation type from first item
        presentation = 'card'  # default
        if items and len(items) > 0:
            first_item = items[0]
            if isinstance(first_item, dict):
                presentation = first_item.get('presentation', 'card')
        
        # Clean items - remove presentation, url, and intrinsic properties
        cleaned_items = []
        for item in items:
            if not isinstance(item, dict):
                cleaned_items.append(item)
                continue
            
            cleaned = {}
            for key, value in item.items():
                # Remove presentation (moved to key level)
                if key == 'presentation':
                    self.stats['presentation_moved'] += 1
                    continue
                
                # Remove url (derived from full_path)
                if key == 'url':
                    self.stats['urls_removed'] += 1
                    continue
                
                # Remove intrinsic properties (belong in entity)
                if key in self.intrinsic_properties:
                    self.stats['intrinsic_props_removed'] += 1
                    continue
                
                # Keep relationship-specific metadata
                cleaned[key] = value
            
            cleaned_items.append(cleaned)
        
        # Build new structure
        new_structure = {
            'presentation': presentation
        }
        
        # Add _section if it existed
        if section:
            new_structure['_section'] = section
        
        # Add items
        new_structure['items'] = cleaned_items
        self.stats['items_wrapped'] += len(cleaned_items)
        
        return new_structure
    
    def restructure_entity_relationships(self, entity_data: Dict[str, Any]) -> int:
        """
        Restructure all relationships in an entity.
        
        Args:
            entity_data: Entity data dictionary
        
        Returns:
            Number of relationships restructured
        """
        if 'relationships' not in entity_data:
            return 0
        
        relationships = entity_data['relationships']
        if not relationships:
            return 0
        
        restructured_count = 0
        
        for key, value in list(relationships.items()):
            # Skip _section metadata
            if key == '_section':
                continue
            
            # Check if already restructured
            if isinstance(value, dict) and 'presentation' in value and 'items' in value:
                continue  # Already in new format
            
            # Restructure
            new_structure = self.restructure_relationship(value)
            if new_structure:
                relationships[key] = new_structure
                restructured_count += 1
        
        return restructured_count


def restructure_materials():
    """Restructure relationships in Materials.yaml."""
    print("Processing Materials.yaml...")
    
    materials_path = project_root / 'data' / 'materials' / 'Materials.yaml'
    
    with open(materials_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    restructurer = RelationshipRestructurer()
    total_relationships = 0
    
    for material_id, material_data in data['materials'].items():
        count = restructurer.restructure_entity_relationships(material_data)
        total_relationships += count
    
    # Save
    with open(materials_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ Restructured {total_relationships} relationships in materials")
    return restructurer.stats


def restructure_contaminants():
    """Restructure relationships in Contaminants.yaml."""
    print("Processing Contaminants.yaml...")
    
    contaminants_path = project_root / 'data' / 'contaminants' / 'Contaminants.yaml'
    
    with open(contaminants_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    restructurer = RelationshipRestructurer()
    total_relationships = 0
    
    for pattern_id, pattern_data in data['contamination_patterns'].items():
        count = restructurer.restructure_entity_relationships(pattern_data)
        total_relationships += count
    
    # Save
    with open(contaminants_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ Restructured {total_relationships} relationships in contaminants")
    return restructurer.stats


def restructure_compounds():
    """Restructure relationships in Compounds.yaml."""
    print("Processing Compounds.yaml...")
    
    compounds_path = project_root / 'data' / 'compounds' / 'Compounds.yaml'
    
    with open(compounds_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    restructurer = RelationshipRestructurer()
    total_relationships = 0
    
    for compound_id, compound_data in data['compounds'].items():
        count = restructurer.restructure_entity_relationships(compound_data)
        total_relationships += count
    
    # Save
    with open(compounds_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ Restructured {total_relationships} relationships in compounds")
    return restructurer.stats


def restructure_settings():
    """Restructure relationships in Settings.yaml."""
    print("Processing Settings.yaml...")
    
    settings_path = project_root / 'data' / 'settings' / 'Settings.yaml'
    
    with open(settings_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    restructurer = RelationshipRestructurer()
    total_relationships = 0
    
    for setting_id, setting_data in data['settings'].items():
        count = restructurer.restructure_entity_relationships(setting_data)
        total_relationships += count
    
    # Save
    with open(settings_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ Restructured {total_relationships} relationships in settings")
    return restructurer.stats


def main():
    """Run Phase 2: Restructure all relationships."""
    print("="*80)
    print("PHASE 2: RESTRUCTURE RELATIONSHIPS")
    print("="*80)
    print()
    
    combined_stats = {
        'presentation_moved': 0,
        'urls_removed': 0,
        'items_wrapped': 0,
        'intrinsic_props_removed': 0
    }
    
    # Process each domain
    for stats in [
        restructure_materials(),
        restructure_contaminants(),
        restructure_compounds(),
        restructure_settings()
    ]:
        for key, value in stats.items():
            combined_stats[key] += value
    
    print()
    print("="*80)
    print(f"✅ PHASE 2 COMPLETE")
    print(f"   Presentation fields moved to key level: {combined_stats['presentation_moved']}")
    print(f"   URL fields removed: {combined_stats['urls_removed']}")
    print(f"   Items wrapped in items array: {combined_stats['items_wrapped']}")
    print(f"   Intrinsic properties removed: {combined_stats['intrinsic_props_removed']}")
    print("="*80)


if __name__ == '__main__':
    main()
