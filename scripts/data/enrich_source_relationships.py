#!/usr/bin/env python3
"""
Phase 2: Enrich relationship references in SOURCE data files (data/*.yaml).

POLICY COMPLIANCE: Core Principle 0.5 and 0.6
- Modifies SOURCE data (data/compounds/Compounds.yaml)
- NOT generated output (frontmatter/*.yaml)
- Export reads complete data → frontmatter automatically complete

CURRENT STATE: Relationship items have only 3-4 fields (id, frequency, severity, typicalContext)
TARGET STATE: All 9-11 fields (+ url, title, name, image, category, subcategory, description, etc.)
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, List

class SourceDataEnricher:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.data_dir = base_path / 'data'
        
        # Load all source data
        self.compounds_data = self.load_yaml(self.data_dir / 'compounds' / 'Compounds.yaml')
        self.contaminants_data = self.load_yaml(self.data_dir / 'contaminants' / 'Contaminants.yaml')
        self.materials_data = self.load_yaml(self.data_dir / 'materials' / 'Materials.yaml')
        
        # Statistics
        self.stats = {
            'compounds_processed': 0,
            'compounds_updated': 0,
            'contaminants_enriched': 0,
            'materials_enriched': 0,
            'errors': []
        }
    
    def load_yaml(self, file_path: Path) -> Dict:
        """Load and parse YAML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Load error {file_path}: {e}")
            sys.exit(1)
    
    def save_yaml(self, file_path: Path, data: Dict):
        """Save enriched data back to YAML"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False)
        except Exception as e:
            print(f"❌ Save error {file_path}: {e}")
            sys.exit(1)
    
    def get_contaminant_by_id(self, contaminant_id: str) -> Dict:
        """Get full contaminant data from source"""
        return self.contaminants_data.get('contaminants', {}).get(contaminant_id, {})
    
    def get_material_by_id(self, material_id: str) -> Dict:
        """Get full material data from source"""
        return self.materials_data.get('materials', {}).get(material_id, {})
    
    def enrich_contaminant_reference(self, item: Dict) -> Dict:
        """Enrich contaminant reference with complete fields"""
        contaminant_id = item.get('id')
        if not contaminant_id:
            return item
        
        full_data = self.get_contaminant_by_id(contaminant_id)
        if not full_data:
            self.stats['errors'].append(f"Missing contaminant: {contaminant_id}")
            return item
        
        # Build complete reference with all fields
        enriched = {
            'id': contaminant_id,
            'name': full_data.get('name', ''),
            'title': full_data.get('title', full_data.get('name', '')),
            'category': full_data.get('category', ''),
            'subcategory': full_data.get('subcategory', ''),
            'url': f"/contaminants/{full_data.get('category', '')}/{full_data.get('subcategory', '')}/{contaminant_id}",
            'image': full_data.get('images', {}).get('hero', {}).get('url', ''),
            'description': full_data.get('description', full_data.get('caption', '')),
            'frequency': item.get('frequency', 'common'),
            'severity': item.get('severity', 'moderate'),
            'typicalContext': item.get('typicalContext', '')
        }
        
        self.stats['contaminants_enriched'] += 1
        return enriched
    
    def enrich_material_reference(self, item: Dict) -> Dict:
        """Enrich material reference with complete fields"""
        material_id = item.get('id')
        if not material_id:
            return item
        
        full_data = self.get_material_by_id(material_id)
        if not full_data:
            self.stats['errors'].append(f"Missing material: {material_id}")
            return item
        
        # Build complete reference with all fields
        enriched = {
            'id': material_id,
            'name': full_data.get('name', ''),
            'title': full_data.get('title', full_data.get('name', '')),
            'category': full_data.get('category', ''),
            'subcategory': full_data.get('subcategory', ''),
            'url': f"/materials/{full_data.get('category', '')}/{full_data.get('subcategory', '')}/{material_id}",
            'image': full_data.get('images', {}).get('hero', {}).get('url', ''),
            'description': full_data.get('description', full_data.get('caption', '')),
            'frequency': item.get('frequency', 'common'),
            'difficulty': item.get('difficulty', 'moderate')
        }
        
        self.stats['materials_enriched'] += 1
        return enriched
    
    def enrich_compound(self, compound_id: str, compound_data: Dict) -> bool:
        """Enrich single compound's relationships"""
        needs_update = False
        
        # Get relationships
        relationships = compound_data.get('relationships', {})
        interactions = relationships.get('interactions', {})
        
        # Enrich producedFromContaminants
        if 'producedFromContaminants' in interactions:
            section = interactions['producedFromContaminants']
            items = section.get('items', [])
            
            if items and len(items[0]) <= 5:  # Check if needs enrichment
                enriched_items = [self.enrich_contaminant_reference(item) for item in items]
                section['items'] = enriched_items
                needs_update = True
                print(f"   ✅ Enriched {len(items)} contaminant references")
        
        # Enrich affectsMaterials
        if 'affectsMaterials' in interactions:
            section = interactions['affectsMaterials']
            items = section.get('items', [])
            
            if items and len(items[0]) <= 3:  # Check if needs enrichment
                enriched_items = [self.enrich_material_reference(item) for item in items]
                section['items'] = enriched_items
                needs_update = True
                print(f"   ✅ Enriched {len(items)} material references")
        
        return needs_update
    
    def enrich_all_compounds(self):
        """Process all compounds in source data"""
        compounds = self.compounds_data.get('compounds', {})
        
        print(f"\n🔍 Found {len(compounds)} compounds in source data")
        print("="*80)
        
        for compound_id, compound_data in compounds.items():
            self.stats['compounds_processed'] += 1
            print(f"\n📦 Processing: {compound_id}")
            
            if self.enrich_compound(compound_id, compound_data):
                self.stats['compounds_updated'] += 1
            else:
                print(f"   ⏭️  Already complete")
        
        # Save updated source data
        if self.stats['compounds_updated'] > 0:
            print(f"\n💾 Saving changes to data/compounds/Compounds.yaml...")
            self.save_yaml(self.data_dir / 'compounds' / 'Compounds.yaml', self.compounds_data)
            print("   ✅ Saved successfully")
        
        self.print_report()
    
    def print_report(self):
        """Print enrichment statistics"""
        print("\n" + "="*80)
        print("📊 PHASE 2 SOURCE DATA ENRICHMENT COMPLETE")
        print("="*80)
        print(f"\n✅ Compounds processed: {self.stats['compounds_processed']}")
        print(f"✅ Compounds updated: {self.stats['compounds_updated']}")
        print(f"📦 Contaminant references enriched: {self.stats['contaminants_enriched']}")
        print(f"📦 Material references enriched: {self.stats['materials_enriched']}")
        
        if self.stats['errors']:
            print(f"\n⚠️  Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:10]:
                print(f"   • {error}")
            if len(self.stats['errors']) > 10:
                print(f"   ... and {len(self.stats['errors']) - 10} more")
        else:
            print("\n✅ No errors encountered")
        
        print("\n" + "="*80)
        print("📋 NEXT STEPS:")
        print("="*80)
        print("1. Re-export compounds domain:")
        print("   python3 run.py --export --domain compounds")
        print("\n2. Verify frontmatter has complete data:")
        print("   cat ../z-beam/frontmatter/compounds/benzene-compound.yaml")
        print("\n3. Commit source data changes:")
        print("   git add data/compounds/Compounds.yaml")
        print("   git commit -m 'Phase 2: Denormalize compound relationships at source'")

if __name__ == "__main__":
    # Get workspace base path
    script_path = Path(__file__).resolve()
    base_path = script_path.parent.parent.parent  # scripts/data/ -> scripts/ -> root
    
    print(f"📁 Working directory: {base_path}")
    print(f"📂 Source data: {base_path / 'data'}")
    
    enricher = SourceDataEnricher(base_path)
    enricher.enrich_all_compounds()
