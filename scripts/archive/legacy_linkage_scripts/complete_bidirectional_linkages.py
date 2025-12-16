#!/usr/bin/env python3
"""
Complete Bidirectional Linkages - Add Missing Material→Compound Links

Current Status:
✅ Materials ↔ Contaminants: Fully bidirectional
✅ Contaminants ↔ Compounds: Fully bidirectional
❌ Materials ↔ Compounds: MISSING

This script generates Material→Compound linkages based on the transitive relationship:
    Material → Contaminant → Compound
    
If Material X produces Contaminant Y during cleaning, and Contaminant Y produces 
Compound Z, then Material X should be linked to Compound Z.

Usage:
    python3 scripts/data/complete_bidirectional_linkages.py --dry-run
    python3 scripts/data/complete_bidirectional_linkages.py --apply
"""

import yaml
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Any


class BidirectionalLinkageCompleter:
    """Completes bidirectional linkages between all domains."""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        
        # File paths
        self.materials_path = Path('data/materials/Materials.yaml')
        self.contaminants_path = Path('data/contaminants/Contaminants.yaml')
        self.compounds_path = Path('data/compounds/Compounds.yaml')
        
        # Load data
        print("📂 Loading data files...")
        self.materials_data = self._load_yaml(self.materials_path)
        self.contaminants_data = self._load_yaml(self.contaminants_path)
        self.compounds_data = self._load_yaml(self.compounds_path)
        
        print(f"   ✅ Materials: {len(self.materials_data.get('materials', {}))} entries")
        print(f"   ✅ Contaminants: {len(self.contaminants_data.get('contamination_patterns', {}))} entries")
        print(f"   ✅ Compounds: {len(self.compounds_data.get('compounds', {}))} entries")
        print()
        
        # Stats
        self.stats = {
            'materials_updated': 0,
            'compounds_linked': 0,
            'total_linkages_added': 0
        }
    
    def _load_yaml(self, path: Path) -> Dict:
        """Load YAML file."""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    def _save_yaml(self, path: Path, data: Dict):
        """Save YAML file with proper formatting."""
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, 
                     allow_unicode=True, width=120)
    
    def _get_compound_info(self, compound_id: str) -> Dict[str, str]:
        """Get compound name and URL."""
        compound = self.compounds_data['compounds'].get(compound_id, {})
        name = compound.get('name', compound_id)
        slug = compound.get('slug', compound_id)
        
        return {
            'id': f"{slug}-compound",
            'title': name,
            'url': f"/compounds/{slug}",
            'image': f"/images/compounds/{slug}-compound.jpg"
        }
    
    def analyze_material_compound_relationships(self) -> Dict[str, Set[str]]:
        """
        Build Material → Compound linkages via transitive relationship:
        Material → Contaminant → Compound
        
        Returns: {material_name: set(compound_ids)}
        """
        print("🔗 Analyzing Material → Contaminant → Compound relationships...")
        
        material_to_compounds = defaultdict(set)
        
        # Step 1: Build Contaminant → Compound map
        contaminant_to_compounds = defaultdict(set)
        for compound_id, compound_data in self.compounds_data['compounds'].items():
            produced_by = compound_data.get('domain_linkages', {}).get('produced_by_contaminants', [])
            for contaminant_link in produced_by:
                contaminant_id = contaminant_link.get('id', '')
                if contaminant_id:
                    # Remove -contamination suffix if present
                    contaminant_slug = contaminant_id.replace('-contamination', '')
                    contaminant_to_compounds[contaminant_slug].add(compound_id)
        
        print(f"   Found {len(contaminant_to_compounds)} contaminants producing compounds")
        
        # Step 2: For each Material, find its Contaminants, then find their Compounds
        for material_name, material_data in self.materials_data['materials'].items():
            related_contaminants = material_data.get('domain_linkages', {}).get('related_contaminants', [])
            
            for contaminant_link in related_contaminants:
                contaminant_id = contaminant_link.get('id', '')
                if contaminant_id:
                    # Remove -contamination suffix if present
                    contaminant_slug = contaminant_id.replace('-contamination', '')
                    
                    # Add all compounds produced by this contaminant
                    compounds_from_contaminant = contaminant_to_compounds.get(contaminant_slug, set())
                    material_to_compounds[material_name].update(compounds_from_contaminant)
        
        print(f"   Found {len(material_to_compounds)} materials with compound linkages")
        print()
        
        return material_to_compounds
    
    def add_material_compound_linkages(self, material_to_compounds: Dict[str, Set[str]]):
        """Add related_compounds to materials."""
        print("📝 Adding Material → Compound linkages...")
        print()
        
        for material_name, compound_ids in sorted(material_to_compounds.items()):
            if not compound_ids:
                continue
            
            material_data = self.materials_data['materials'][material_name]
            
            # Build linkage entries
            compound_linkages = []
            for compound_id in sorted(compound_ids):
                compound_info = self._get_compound_info(compound_id)
                compound_linkages.append({
                    'id': compound_info['id'],
                    'title': compound_info['title'],
                    'url': compound_info['url'],
                    'image': compound_info['image'],
                    'exposure_risk': 'moderate',  # Default, can be refined
                    'source': 'laser_ablation'
                })
            
            # Add to material's domain_linkages
            if 'domain_linkages' not in material_data:
                material_data['domain_linkages'] = {}
            
            material_data['domain_linkages']['related_compounds'] = compound_linkages
            
            self.stats['materials_updated'] += 1
            self.stats['compounds_linked'] += len(compound_linkages)
            self.stats['total_linkages_added'] += len(compound_linkages)
            
            print(f"   ✅ {material_name}: Added {len(compound_linkages)} compound linkages")
        
        print()
        print(f"📊 Summary:")
        print(f"   • Materials updated: {self.stats['materials_updated']}")
        print(f"   • Unique compounds linked: {self.stats['compounds_linked']}")
        print(f"   • Total linkages added: {self.stats['total_linkages_added']}")
        print()
    
    def run(self):
        """Execute the complete linkage generation."""
        print("=" * 80)
        print("COMPLETE BIDIRECTIONAL LINKAGE GENERATION")
        print("=" * 80)
        print()
        
        # Analyze relationships
        material_to_compounds = self.analyze_material_compound_relationships()
        
        # Add linkages
        self.add_material_compound_linkages(material_to_compounds)
        
        # Save or report
        if self.dry_run:
            print("🔍 DRY RUN - No files modified")
            print()
            print("Sample linkages that would be added:")
            print()
            for material_name, compound_ids in sorted(list(material_to_compounds.items())[:3]):
                if compound_ids:
                    print(f"   {material_name}:")
                    for compound_id in sorted(compound_ids):
                        compound_info = self._get_compound_info(compound_id)
                        print(f"      → {compound_info['title']}")
            print()
            print("Run with --apply to save changes")
        else:
            print("💾 Saving changes...")
            self._save_yaml(self.materials_path, self.materials_data)
            print(f"   ✅ Saved {self.materials_path}")
            print()
            print("✅ COMPLETE - All bidirectional linkages generated!")


def main():
    parser = argparse.ArgumentParser(
        description='Complete bidirectional linkages between all domains'
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Apply changes (default is dry-run)'
    )
    
    args = parser.parse_args()
    dry_run = not args.apply
    
    completer = BidirectionalLinkageCompleter(dry_run=dry_run)
    completer.run()


if __name__ == '__main__':
    main()
