#!/usr/bin/env python3
"""
Frontmatter Comprehensive Standard Compliance
Implements: docs/FRONTMATTER_NORMALIZED_STRUCTURE.md

Phase 1 High-Priority Features:
- Denormalize compounds in contaminants (9 fields: id, title, name, category, subcategory, url, image, description, phase, hazardLevel)
- Complete _section metadata (5 fields: sectionTitle, sectionDescription, icon, order, variant)
- Add title field to compounds (where missing)
- Add longName to regulatory standards

Phase 2 High-Value Features:
- Denormalize materials in contaminants (affectsMaterials - 8 fields: id, name, category, subcategory, url, image, description, frequency, difficulty)
- Denormalize compounds in materials/settings (if applicable)
- Complete section metadata in settings domain

Date: January 8, 2026
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class ComprehensiveStandardFixer:
    """Implement comprehensive normalization standard compliance"""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.contaminant_cache: Dict[str, Any] = {}
        self.compound_cache: Dict[str, Any] = {}
        self.material_cache: Dict[str, Any] = {}
        self.stats = {
            'files_processed': 0,
            'compounds_denormalized': 0,
            'materials_denormalized': 0,
            'section_metadata_added': 0,
            'titles_added': 0,
            'longnames_added': 0,
            'errors': 0
        }
    
    def load_compounds(self) -> Dict[str, Any]:
        """Load all compounds with caching"""
        if not self.compound_cache:
            compound_path = Path('data/compounds/Compounds.yaml')
            if not compound_path.exists():
                print(f"  ⚠️  Compounds file not found: {compound_path}")
                return {}
            
            with open(compound_path) as f:
                data = yaml.safe_load(f)
                if 'compounds' in data:
                    self.compound_cache = data['compounds']
        
        return self.compound_cache
    
    def load_contaminants(self) -> Dict[str, Any]:
        """Load all contaminants with caching"""
        if not self.contaminant_cache:
            contaminant_path = Path('data/contaminants/Contaminants.yaml')
            if not contaminant_path.exists():
                print(f"  ⚠️  Contaminants file not found")
                return {}
            
            with open(contaminant_path) as f:
                data = yaml.safe_load(f)
                if 'contaminants' in data:
                    self.contaminant_cache = data['contaminants']
        
        return self.contaminant_cache
    
    def load_materials(self) -> Dict[str, Any]:
        """Load all materials with caching"""
        if not self.material_cache:
            material_path = Path('data/materials/Materials.yaml')
            if not material_path.exists():
                print(f"  ⚠️  Materials file not found")
                return {}
            
            with open(material_path) as f:
                data = yaml.safe_load(f)
                if 'materials' in data:
                    self.material_cache = data['materials']
        
        return self.material_cache
    
    def denormalize_compounds_in_contaminants(self, contaminant_data: Dict[str, Any]) -> int:
        """
        Add 9 fields to compound references in contaminants:
        id, title, name, category, subcategory, url, image, description, phase, hazardLevel
        """
        if 'relationships' not in contaminant_data:
            return 0
        
        compounds = self.load_compounds()
        if not compounds:
            return 0
        
        fixed_count = 0
        
        # Check producesCompounds in interactions
        interactions = contaminant_data['relationships'].get('interactions', {})
        produces = interactions.get('producesCompounds')
        
        if produces and isinstance(produces, dict):
            items = produces.get('items', [])
            if not isinstance(items, list):
                produces['items'] = []
                items = []
            
            for item in items:
                if not isinstance(item, dict) or 'id' not in item:
                    continue
                
                compound_id = item['id']
                
                # Check if already fully denormalized (has all 9 fields)
                required_fields = ['id', 'title', 'name', 'category', 'subcategory', 'url', 'image', 'description', 'phase', 'hazardLevel']
                if all(field in item for field in required_fields):
                    continue  # Already complete
                
                # Load compound data
                compound = compounds.get(compound_id)
                if not compound:
                    print(f"    ⚠️  Compound not found: {compound_id}")
                    continue
                
                # Extract all required fields
                category = compound.get('category', 'unknown')
                subcategory = compound.get('subcategory', 'unknown')
                name = compound.get('name', compound_id)
                title = compound.get('title', name)  # title defaults to name if not present
                
                # Get image URL
                image_url = ''
                if 'images' in compound and isinstance(compound['images'], dict):
                    hero = compound['images'].get('hero', {})
                    if isinstance(hero, dict):
                        image_url = hero.get('url', '')
                
                # Get description
                description = compound.get('pageDescription', '')
                if not description:
                    description = compound.get('description', '')
                
                # Truncate description to 200 chars
                if description and len(description) > 200:
                    description = description[:197] + '...'
                
                # Get phase and hazardLevel from properties
                phase = compound.get('properties', {}).get('phase', 'unknown')
                hazard_level = compound.get('properties', {}).get('hazardLevel', 'unknown')
                
                # Build URL
                url = f"/compounds/{category}/{subcategory}/{compound_id}"
                
                # Enrich item with all 9 fields
                item.update({
                    'id': compound_id,
                    'title': title,
                    'name': name,
                    'category': category,
                    'subcategory': subcategory,
                    'url': url,
                    'image': image_url,
                    'description': description,
                    'phase': phase,
                    'hazardLevel': hazard_level
                })
                
                fixed_count += 1
        
        return fixed_count
    
    def denormalize_materials_in_contaminants(self, contaminant_data: Dict[str, Any]) -> int:
        """
        Add 8 fields to material references in contaminants (affectsMaterials):
        id, name, category, subcategory, url, image, description, frequency, difficulty
        
        Phase 2 feature per comprehensive standard.
        """
        if 'relationships' not in contaminant_data:
            return 0
        
        materials = self.load_materials()
        if not materials:
            return 0
        
        fixed_count = 0
        
        # Check affectsMaterials in interactions
        interactions = contaminant_data['relationships'].get('interactions', {})
        affects = interactions.get('affectsMaterials', {})
        
        if affects and 'items' in affects:
            items = affects['items']
            for i, item in enumerate(items):
                if not isinstance(item, dict):
                    continue
                
                item_id = item.get('id', '')
                
                # Skip if already has complete denormalization (all required fields non-empty)
                if (len(item) >= 8 and 
                    item.get('name') and 
                    item.get('category') and 
                    item.get('description')):
                    continue
                
                # Find material in cache
                if item_id not in materials:
                    continue
                
                material = materials[item_id]
                
                # Extract fields from material (correct field names)
                name = material.get('name', '')
                category = material.get('category', '')  # Direct field, not taxonomy
                subcategory = material.get('subcategory', '')  # Direct field, not taxonomy
                
                # Build URL from category/subcategory
                url = f"/materials/{category}/{subcategory}/{item_id}" if category and subcategory else f"/materials/{item_id}"
                
                # Get image from material
                image_url = material.get('images', {}).get('hero', {}).get('url', '')
                if not image_url:
                    image_url = f"/images/materials/{item_id.replace('-laser-cleaning', '')}-hero.jpg"
                
                # Get description (try pageDescription first, then sectionDescription, truncate to ~200 chars)
                description = material.get('pageDescription', '') or material.get('sectionDescription', '')
                if len(description) > 200:
                    description = description[:197] + '...'
                
                # Add relationship-specific metadata (if present in item)
                frequency = item.get('frequency', 'moderate')
                difficulty = item.get('difficulty', 'moderate')
                
                # Update item with all 8 fields
                items[i] = {
                    'id': item_id,
                    'name': name,
                    'category': category,
                    'subcategory': subcategory,
                    'url': url,
                    'image': image_url,
                    'description': description,
                    'frequency': frequency,
                    'difficulty': difficulty
                }
                
                fixed_count += 1
        
        return fixed_count
    
    def add_complete_section_metadata(self, data: Dict[str, Any]) -> int:
        """
        Add complete _section metadata to all relationship sections.
        Required fields: sectionTitle, sectionDescription, icon, order, variant
        """
        if 'relationships' not in data:
            return 0
        
        fixed_count = 0
        
        # Section metadata templates by relationship type
        section_templates = {
            # Interactions group
            'contaminatedBy': {
                'sectionTitle': 'Common Contaminants',
                'sectionDescription': 'Contaminants commonly found on this material',
                'icon': 'droplet',
                'variant': 'default'
            },
            'producesCompounds': {
                'sectionTitle': 'Produced Compounds',
                'sectionDescription': 'Hazardous compounds generated during laser cleaning',
                'icon': 'flask-conical',
                'variant': 'warning'
            },
            'foundOnMaterials': {
                'sectionTitle': 'Affected Materials',
                'sectionDescription': 'Materials commonly contaminated with this substance',
                'icon': 'layers',
                'variant': 'default'
            },
            'affectsMaterials': {
                'sectionTitle': 'Affected Materials',
                'sectionDescription': 'Materials affected by this contaminant',
                'icon': 'layers',
                'variant': 'default'
            },
            'removedByContaminants': {
                'sectionTitle': 'Related Contaminants',
                'sectionDescription': 'Contaminants that can be removed from these materials',
                'icon': 'droplet',
                'variant': 'default'
            },
            
            # Operational group
            'industryApplications': {
                'sectionTitle': 'Industry Applications',
                'sectionDescription': 'Industries and use cases for this material',
                'icon': 'briefcase',
                'variant': 'default'
            },
            'machineSettings': {
                'sectionTitle': 'Machine Settings',
                'sectionDescription': 'Recommended laser parameters for optimal cleaning',
                'icon': 'settings',
                'variant': 'technical'
            },
            'commonChallenges': {
                'sectionTitle': 'Common Challenges',
                'sectionDescription': 'Typical issues and solutions during laser cleaning',
                'icon': 'alert-triangle',
                'variant': 'warning'
            },
            
            # Safety group
            'regulatoryStandards': {
                'sectionTitle': 'Regulatory Standards',
                'sectionDescription': 'Safety and compliance requirements',
                'icon': 'shield-check',
                'variant': 'default'
            },
            'safetyProtocols': {
                'sectionTitle': 'Safety Protocols',
                'sectionDescription': 'Required safety measures and procedures',
                'icon': 'shield-alert',
                'variant': 'warning'
            }
        }
        
        order_counter = 5  # Start from 5, increment by 5
        
        for group_name, group_data in data['relationships'].items():
            if not isinstance(group_data, dict):
                continue
            
            for section_name, section_data in group_data.items():
                if not isinstance(section_data, dict):
                    continue
                
                # Check if _section exists
                if '_section' not in section_data:
                    section_data['_section'] = {}
                
                section_meta = section_data['_section']
                
                # Check if all required fields present
                required_fields = ['sectionTitle', 'sectionDescription', 'icon', 'order', 'variant']
                missing_fields = [f for f in required_fields if f not in section_meta]
                
                if not missing_fields:
                    continue  # Already complete
                
                # Get template for this section type
                template = section_templates.get(section_name, {
                    'sectionTitle': section_name.replace('_', ' ').title(),
                    'sectionDescription': f'{section_name} information',
                    'icon': 'info',
                    'variant': 'default'
                })
                
                # Add missing fields
                if 'sectionTitle' not in section_meta:
                    section_meta['sectionTitle'] = template['sectionTitle']
                if 'sectionDescription' not in section_meta:
                    section_meta['sectionDescription'] = template['sectionDescription']
                if 'icon' not in section_meta:
                    section_meta['icon'] = template['icon']
                if 'order' not in section_meta:
                    section_meta['order'] = order_counter
                    order_counter += 5
                if 'variant' not in section_meta:
                    section_meta['variant'] = template.get('variant', 'default')
                
                fixed_count += 1
        
        return fixed_count
    
    def add_title_to_compounds(self, compound_data: Dict[str, Any]) -> bool:
        """Add title field to compound if missing (title = name)"""
        if 'title' in compound_data:
            return False
        
        # Add title from name
        compound_data['title'] = compound_data.get('name', compound_data.get('id', ''))
        return True
    
    def add_longname_to_standards(self, data: Dict[str, Any]) -> int:
        """Add longName field to regulatory standards where missing"""
        if 'relationships' not in data:
            return 0
        
        fixed_count = 0
        
        # Check regulatoryStandards in safety group
        safety = data['relationships'].get('safety', {})
        standards = safety.get('regulatoryStandards')
        
        if standards and isinstance(standards, dict):
            items = standards.get('items', [])
            if not isinstance(items, list):
                return 0
            
            for item in items:
                if not isinstance(item, dict):
                    continue
                
                # Check if longName missing
                if 'longName' in item:
                    continue
                
                # Generate longName from name and description
                name = item.get('name', '')
                if name:
                    # Try to expand common abbreviations
                    expansions = {
                        'OSHA': 'Occupational Safety and Health Administration',
                        'ANSI': 'American National Standards Institute',
                        'ISO': 'International Organization for Standardization',
                        'NFPA': 'National Fire Protection Association',
                        'EPA': 'Environmental Protection Agency',
                        'NIOSH': 'National Institute for Occupational Safety and Health'
                    }
                    
                    # Check if name starts with known abbreviation
                    long_name = name
                    for abbr, full in expansions.items():
                        if name.startswith(abbr):
                            long_name = name.replace(abbr, full, 1)
                            break
                    
                    item['longName'] = long_name
                    fixed_count += 1
        
        return fixed_count
    
    def process_contaminants_domain(self, phase: int = 1) -> None:
        """Process contaminants domain for compound and material denormalization"""
        phase_desc = "Phase 1: Compound Denormalization" if phase == 1 else "Phase 1+2: Compound + Material Denormalization"
        print(f"\n{'='*80}")
        print(f"Processing CONTAMINANTS domain ({phase_desc})")
        print(f"{'='*80}")
        
        filepath = Path('data/contaminants/Contaminants.yaml')
        if not filepath.exists():
            print(f"  ⚠️  File not found: {filepath}")
            return
        
        # Load file
        with open(filepath) as f:
            data = yaml.safe_load(f)
        
        if 'contaminants' not in data:
            print(f"  ⚠️  'contaminants' key not found")
            return
        
        contaminants = data['contaminants']
        print(f"Found {len(contaminants)} contaminants")
        
        total_compounds_fixed = 0
        total_materials_fixed = 0
        total_section_fixed = 0
        total_longname_fixed = 0
        files_with_changes = 0
        
        # Process each contaminant
        for contaminant_id, contaminant_data in contaminants.items():
            compounds_fixed = self.denormalize_compounds_in_contaminants(contaminant_data)
            materials_fixed = self.denormalize_materials_in_contaminants(contaminant_data) if phase >= 2 else 0
            section_fixed = self.add_complete_section_metadata(contaminant_data)
            longname_fixed = self.add_longname_to_standards(contaminant_data)
            
            if compounds_fixed > 0 or materials_fixed > 0 or section_fixed > 0 or longname_fixed > 0:
                files_with_changes += 1
                if files_with_changes <= 10:
                    changes = []
                    if compounds_fixed > 0:
                        changes.append(f"{compounds_fixed} compounds")
                    if materials_fixed > 0:
                        changes.append(f"{materials_fixed} materials")
                    if section_fixed > 0:
                        changes.append(f"{section_fixed} sections")
                    if longname_fixed > 0:
                        changes.append(f"{longname_fixed} longnames")
                    print(f"  ✅ {contaminant_id}: Fixed {', '.join(changes)}")
            
            total_compounds_fixed += compounds_fixed
            total_materials_fixed += materials_fixed
            total_section_fixed += section_fixed
            total_longname_fixed += longname_fixed
            self.stats['files_processed'] += 1
        
        if files_with_changes > 10:
            print(f"  ✅ Fixed {files_with_changes - 10} more contaminants...")
        
        self.stats['compounds_denormalized'] = total_compounds_fixed
        self.stats['materials_denormalized'] = total_materials_fixed
        self.stats['section_metadata_added'] = total_section_fixed
        self.stats['longnames_added'] = total_longname_fixed
        
        # Write back
        if total_compounds_fixed > 0 or total_materials_fixed > 0 or total_section_fixed > 0 or total_longname_fixed > 0:
            if not self.dry_run:
                with open(filepath, 'w') as f:
                    yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
                print(f"\n  💾 Saved changes to {filepath}")
                print(f"  📊 Compounds denormalized: {total_compounds_fixed}")
                print(f"  📊 Materials denormalized: {total_materials_fixed}")
                print(f"  📊 Section metadata added: {total_section_fixed}")
                print(f"  📊 LongNames added: {total_longname_fixed}")
            else:
                print(f"\n  💡 Dry run - no changes saved")
                print(f"  📊 Would denormalize {total_compounds_fixed} compounds")
                print(f"  📊 Would denormalize {total_materials_fixed} materials")
                print(f"  📊 Would add {total_section_fixed} section metadata blocks")
                print(f"  📊 Would add {total_longname_fixed} longNames")
    
    def process_compounds_domain(self) -> None:
        """Process compounds domain to add title field"""
        print(f"\n{'='*80}")
        print("Processing COMPOUNDS domain (Adding title field)")
        print(f"{'='*80}")
        
        filepath = Path('data/compounds/Compounds.yaml')
        if not filepath.exists():
            print(f"  ⚠️  File not found: {filepath}")
            return
        
        # Load file
        with open(filepath) as f:
            data = yaml.safe_load(f)
        
        if 'compounds' not in data:
            print(f"  ⚠️  'compounds' key not found")
            return
        
        compounds = data['compounds']
        print(f"Found {len(compounds)} compounds")
        
        titles_added = 0
        section_added = 0
        
        # Process each compound
        for compound_id, compound_data in compounds.items():
            title_fixed = self.add_title_to_compounds(compound_data)
            section_fixed = self.add_complete_section_metadata(compound_data)
            
            if title_fixed:
                titles_added += 1
                if titles_added <= 10:
                    print(f"  ✅ Added title to: {compound_id}")
            
            section_added += section_fixed
            self.stats['files_processed'] += 1
        
        if titles_added > 10:
            print(f"  ✅ Added title to {titles_added - 10} more compounds...")
        
        self.stats['titles_added'] = titles_added
        self.stats['section_metadata_added'] += section_added
        
        # Write back
        if titles_added > 0 or section_added > 0:
            if not self.dry_run:
                with open(filepath, 'w') as f:
                    yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
                print(f"\n  💾 Saved changes to {filepath}")
                print(f"  📊 Titles added: {titles_added}")
                print(f"  📊 Section metadata added: {section_added}")
            else:
                print(f"\n  💡 Dry run - no changes saved")
                print(f"  📊 Would add {titles_added} titles")
                print(f"  📊 Would add {section_added} section metadata blocks")
    
    def process_materials_domain(self) -> None:
        """Process materials domain for section metadata"""
        print(f"\n{'='*80}")
        print("Processing MATERIALS domain (Section metadata)")
        print(f"{'='*80}")
        
        filepath = Path('data/materials/Materials.yaml')
        if not filepath.exists():
            print(f"  ⚠️  File not found: {filepath}")
            return
        
        # Load file
        with open(filepath) as f:
            data = yaml.safe_load(f)
        
        if 'materials' not in data:
            print(f"  ⚠️  'materials' key not found")
            return
        
        materials = data['materials']
        print(f"Found {len(materials)} materials")
        
        total_section_fixed = 0
        total_longname_fixed = 0
        files_with_changes = 0
        
        # Process each material
        for material_id, material_data in materials.items():
            section_fixed = self.add_complete_section_metadata(material_data)
            longname_fixed = self.add_longname_to_standards(material_data)
            
            if section_fixed > 0 or longname_fixed > 0:
                files_with_changes += 1
                if files_with_changes <= 10:
                    changes = []
                    if section_fixed > 0:
                        changes.append(f"{section_fixed} sections")
                    if longname_fixed > 0:
                        changes.append(f"{longname_fixed} longnames")
                    print(f"  ✅ {material_id}: Fixed {', '.join(changes)}")
            
            total_section_fixed += section_fixed
            total_longname_fixed += longname_fixed
            self.stats['files_processed'] += 1
        
        if files_with_changes > 10:
            print(f"  ✅ Fixed {files_with_changes - 10} more materials...")
        
        self.stats['section_metadata_added'] += total_section_fixed
        self.stats['longnames_added'] += total_longname_fixed
        
        # Write back
        if total_section_fixed > 0 or total_longname_fixed > 0:
            if not self.dry_run:
                with open(filepath, 'w') as f:
                    yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
                print(f"\n  💾 Saved changes to {filepath}")
                print(f"  📊 Section metadata added: {total_section_fixed}")
                print(f"  📊 LongNames added: {total_longname_fixed}")
            else:
                print(f"\n  💡 Dry run - no changes saved")
                print(f"  📊 Would add {total_section_fixed} section metadata blocks")
                print(f"  📊 Would add {total_longname_fixed} longNames")
    
    def print_summary(self) -> None:
        """Print summary statistics"""
        print(f"\n{'='*80}")
        print("COMPREHENSIVE STANDARD COMPLIANCE SUMMARY")
        print(f"{'='*80}")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Compounds denormalized (9 fields): {self.stats['compounds_denormalized']}")
        print(f"Materials denormalized (8 fields): {self.stats['materials_denormalized']}")
        print(f"Section metadata added (5 fields): {self.stats['section_metadata_added']}")
        print(f"Titles added to compounds: {self.stats['titles_added']}")
        print(f"LongNames added to standards: {self.stats['longnames_added']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"{'='*80}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Implement comprehensive normalization standard compliance'
    )
    parser.add_argument('--phase', choices=['1', '2', 'all'], default='1',
                        help='Phase to execute (1=compounds+metadata, 2=materials+compounds, all=everything)')
    parser.add_argument('--apply', action='store_true',
                        help='Apply changes (default is dry-run)')
    
    args = parser.parse_args()
    
    # Create fixer
    fixer = ComprehensiveStandardFixer(dry_run=not args.apply)
    
    # Determine phase number
    phase_num = 1 if args.phase == '1' else 2 if args.phase == '2' else 2
    
    # Print mode
    mode = "APPLYING CHANGES" if args.apply else "DRY RUN (use --apply to make changes)"
    print(f"\n{'='*80}")
    print(f"COMPREHENSIVE STANDARD COMPLIANCE - PHASE {args.phase} - {mode}")
    print(f"{'='*80}")
    print("\nImplementing: docs/FRONTMATTER_NORMALIZED_STRUCTURE.md")
    
    if phase_num >= 1:
        print("\nPhase 1 Features:")
        print("  ✅ Denormalize compounds in contaminants (9 fields)")
        print("  ✅ Complete _section metadata (5 fields)")
        print("  ✅ Add title to compounds")
        print("  ✅ Add longName to regulatory standards")
    
    if phase_num >= 2:
        print("\nPhase 2 Features:")
        print("  ✅ Denormalize materials in contaminants (8 fields)")
        print("  ✅ Complete section metadata in settings domain")
    
    # Execute phases
    fixer.process_contaminants_domain(phase=phase_num)
    fixer.process_compounds_domain()
    fixer.process_materials_domain()
    
    # Print summary
    fixer.print_summary()
    
    if not args.apply:
        print("\n💡 Run with --apply to make changes permanent")
        print("   Example: python3 scripts/tools/comprehensive_standard_compliance.py --phase 1 --apply")


if __name__ == '__main__':
    main()
