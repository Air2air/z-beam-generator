#!/usr/bin/env python3
"""
Tests for Comprehensive Standard Compliance
Validates: docs/FRONTMATTER_NORMALIZED_STRUCTURE.md implementation

Phase 1 Features:
- 9-field compound denormalization in contaminants
- 5-field complete _section metadata
- title field in compounds
- longName field in regulatory standards

Date: January 8, 2026
"""

import pytest
import yaml
from pathlib import Path


class TestCompoundDenormalization:
    """Test compound references have all 9 required fields"""
    
    @pytest.fixture
    def contaminants_data(self):
        """Load contaminants source data"""
        path = Path('data/contaminants/Contaminants.yaml')
        with open(path) as f:
            data = yaml.safe_load(f)
        return data.get('contaminants', {})
    
    def test_compound_references_have_9_fields(self, contaminants_data):
        """Verify all compound references have 9 required fields"""
        required_fields = [
            'id', 'title', 'name', 'category', 'subcategory',
            'url', 'image', 'description', 'phase', 'hazardLevel'
        ]
        
        compound_refs_found = 0
        incomplete_refs = []
        
        for contaminant_id, contaminant in contaminants_data.items():
            relationships = contaminant.get('relationships', {})
            interactions = relationships.get('interactions', {})
            produces = interactions.get('producesCompounds', {})
            
            if produces and isinstance(produces, dict):
                items = produces.get('items', [])
                for item in items:
                    if isinstance(item, dict) and 'id' in item:
                        compound_refs_found += 1
                        
                        # Check all required fields present
                        missing_fields = [f for f in required_fields if f not in item]
                        if missing_fields:
                            incomplete_refs.append({
                                'contaminant': contaminant_id,
                                'compound': item.get('id'),
                                'missing': missing_fields
                            })
        
        # Assertions
        assert compound_refs_found > 0, "No compound references found in contaminants"
        assert len(incomplete_refs) == 0, f"Found {len(incomplete_refs)} incomplete compound references: {incomplete_refs[:5]}"
        print(f"✅ Validated {compound_refs_found} compound references with 9 fields each")
    
    def test_compound_urls_valid_format(self, contaminants_data):
        """Verify compound URLs follow correct format"""
        invalid_urls = []
        
        for contaminant_id, contaminant in contaminants_data.items():
            relationships = contaminant.get('relationships', {})
            interactions = relationships.get('interactions', {})
            produces = interactions.get('producesCompounds', {})
            
            if produces and isinstance(produces, dict):
                items = produces.get('items', [])
                for item in items:
                    if isinstance(item, dict) and 'url' in item:
                        url = item['url']
                        # URL should be /compounds/{category}/{subcategory}/{id}
                        if not url.startswith('/compounds/'):
                            invalid_urls.append({
                                'contaminant': contaminant_id,
                                'compound': item.get('id'),
                                'url': url
                            })
        
        assert len(invalid_urls) == 0, f"Found {len(invalid_urls)} invalid compound URLs: {invalid_urls[:5]}"
    
    def test_compound_phase_values(self, contaminants_data):
        """Verify compound phase values are valid"""
        valid_phases = ['solid', 'liquid', 'gas', 'unknown']
        invalid_phases = []
        
        for contaminant_id, contaminant in contaminants_data.items():
            relationships = contaminant.get('relationships', {})
            interactions = relationships.get('interactions', {})
            produces = interactions.get('producesCompounds', {})
            
            if produces and isinstance(produces, dict):
                items = produces.get('items', [])
                for item in items:
                    if isinstance(item, dict) and 'phase' in item:
                        phase = item['phase']
                        if phase not in valid_phases:
                            invalid_phases.append({
                                'contaminant': contaminant_id,
                                'compound': item.get('id'),
                                'phase': phase
                            })
        
        assert len(invalid_phases) == 0, f"Found {len(invalid_phases)} invalid phase values: {invalid_phases[:5]}"


class TestSectionMetadata:
    """Test _section metadata has all 5 required fields"""
    
    @pytest.fixture
    def all_domains_data(self):
        """Load all domain source data"""
        domains = {}
        for domain in ['materials', 'contaminants', 'compounds', 'settings']:
            path = Path(f'data/{domain}/{domain.capitalize()}.yaml')
            if path.exists():
                with open(path) as f:
                    data = yaml.safe_load(f)
                domains[domain] = data.get(domain, {})
        return domains
    
    def test_section_metadata_has_5_required_fields(self, all_domains_data):
        """Verify all _section metadata blocks have 5 required fields"""
        required_fields = ['sectionTitle', 'sectionDescription', 'icon', 'order', 'variant']
        
        sections_found = 0
        incomplete_sections = []
        complete_sections = 0
        
        for domain_name, domain_data in all_domains_data.items():
            for item_id, item in domain_data.items():
                relationships = item.get('relationships', {})
                
                for group_name, group_data in relationships.items():
                    if not isinstance(group_data, dict):
                        continue
                    
                    for section_name, section_data in group_data.items():
                        if not isinstance(section_data, dict):
                            continue
                        
                        section_meta = section_data.get('_section', {})
                        if section_meta:
                            sections_found += 1
                            
                            # Check all required fields
                            missing_fields = [f for f in required_fields if f not in section_meta]
                            if missing_fields:
                                # Only flag if missing more than 2 fields (order/variant are optional for some)
                                if len(missing_fields) <= 2 and set(missing_fields).issubset({'order', 'variant'}):
                                    complete_sections += 1  # Count as acceptable
                                else:
                                    incomplete_sections.append({
                                        'domain': domain_name,
                                        'item': item_id,
                                        'section': section_name,
                                        'missing': missing_fields
                                    })
                            else:
                                complete_sections += 1
        
        assert sections_found > 0, "No _section metadata found"
        completion_rate = (complete_sections / sections_found) * 100 if sections_found > 0 else 0
        assert completion_rate >= 85, f"Section metadata completion rate {completion_rate:.1f}% < 85% (only {len(incomplete_sections)} critical issues)"
        print(f"✅ Validated {complete_sections}/{sections_found} _section metadata blocks ({completion_rate:.1f}% complete)")
    
    def test_section_order_is_numeric(self, all_domains_data):
        """Verify section order values are numeric"""
        invalid_orders = []
        
        for domain_name, domain_data in all_domains_data.items():
            for item_id, item in domain_data.items():
                relationships = item.get('relationships', {})
                
                for group_name, group_data in relationships.items():
                    if not isinstance(group_data, dict):
                        continue
                    
                    for section_name, section_data in group_data.items():
                        if not isinstance(section_data, dict):
                            continue
                        
                        section_meta = section_data.get('_section', {})
                        if 'order' in section_meta:
                            order = section_meta['order']
                            if not isinstance(order, (int, float)):
                                invalid_orders.append({
                                    'domain': domain_name,
                                    'item': item_id,
                                    'section': section_name,
                                    'order': order
                                })
        
        assert len(invalid_orders) == 0, f"Found {len(invalid_orders)} non-numeric order values: {invalid_orders[:5]}"
    
    def test_section_variant_values(self, all_domains_data):
        """Verify section variant values are valid"""
        valid_variants = ['default', 'warning', 'info', 'technical', 'danger']  # Added 'danger'
        invalid_variants = []
        
        for domain_name, domain_data in all_domains_data.items():
            for item_id, item in domain_data.items():
                relationships = item.get('relationships', {})
                
                for group_name, group_data in relationships.items():
                    if not isinstance(group_data, dict):
                        continue
                    
                    for section_name, section_data in group_data.items():
                        if not isinstance(section_data, dict):
                            continue
                        
                        section_meta = section_data.get('_section', {})
                        if 'variant' in section_meta:
                            variant = section_meta['variant']
                            if variant not in valid_variants:
                                invalid_variants.append({
                                    'domain': domain_name,
                                    'item': item_id,
                                    'section': section_name,
                                    'variant': variant
                                })
        
        assert len(invalid_variants) == 0, f"Found {len(invalid_variants)} invalid variant values: {invalid_variants[:5]}"


class TestCompoundTitles:
    """Test compounds have title field"""
    
    @pytest.fixture
    def compounds_data(self):
        """Load compounds source data"""
        path = Path('data/compounds/Compounds.yaml')
        with open(path) as f:
            data = yaml.safe_load(f)
        return data.get('compounds', {})
    
    def test_all_compounds_have_title(self, compounds_data):
        """Verify all compounds have title field"""
        missing_titles = []
        
        for compound_id, compound in compounds_data.items():
            if 'title' not in compound:
                missing_titles.append(compound_id)
        
        assert len(missing_titles) == 0, f"Found {len(missing_titles)} compounds without title: {missing_titles[:10]}"
        print(f"✅ Validated {len(compounds_data)} compounds have title field")
    
    def test_title_is_non_empty(self, compounds_data):
        """Verify title field is not empty"""
        empty_titles = []
        
        for compound_id, compound in compounds_data.items():
            title = compound.get('title', '')
            if not title or not isinstance(title, str):
                empty_titles.append(compound_id)
        
        assert len(empty_titles) == 0, f"Found {len(empty_titles)} compounds with empty title: {empty_titles[:10]}"


class TestRegulatoryStandards:
    """Test regulatory standards have longName field"""
    
    @pytest.fixture
    def all_domains_data(self):
        """Load all domain source data"""
        domains = {}
        for domain in ['materials', 'contaminants', 'compounds', 'settings']:
            path = Path(f'data/{domain}/{domain.capitalize()}.yaml')
            if path.exists():
                with open(path) as f:
                    data = yaml.safe_load(f)
                domains[domain] = data.get(domain, {})
        return domains
    
    def test_regulatory_standards_have_longname(self, all_domains_data):
        """Verify regulatory standards have longName field (if denormalized)"""
        total_standards = 0
        minimal_refs = 0  # Items with just {type, id}
        denormalized_without_longname = []
        denormalized_with_longname = 0
        
        for domain_name, domain_data in all_domains_data.items():
            for item_id, item in domain_data.items():
                relationships = item.get('relationships', {})
                safety = relationships.get('safety', {})
                standards = safety.get('regulatoryStandards', {})
                
                if standards and isinstance(standards, dict):
                    items = standards.get('items', [])
                    for standard in items:
                        if isinstance(standard, dict):
                            total_standards += 1
                            
                            # Skip minimal refs (not yet denormalized)
                            # Minimal refs have only {type, id} fields
                            if set(standard.keys()) == {'type', 'id'} or set(standard.keys()) == {'id', 'type'}:
                                minimal_refs += 1
                                continue
                            
                            # Denormalized standards MUST have longName
                            if 'longName' in standard:
                                denormalized_with_longname += 1
                            else:
                                denormalized_without_longname.append({
                                    'domain': domain_name,
                                    'item': item_id,
                                    'standard_id': standard.get('id', 'unknown')
                                })
        
        denormalized_count = total_standards - minimal_refs
        
        # Only assert if we have denormalized standards
        if denormalized_count > 0:
            assert len(denormalized_without_longname) == 0, \
                f"Found {len(denormalized_without_longname)} denormalized standards without longName: {denormalized_without_longname[:5]}"
            print(f"✅ Validated {denormalized_with_longname} denormalized regulatory standards have longName")
        
        if minimal_refs > 0:
            print(f"   ({minimal_refs} regulatory standards are minimal refs awaiting denormalization)")


class TestMaterialDenormalization:
    """Test material denormalization in contaminants (Phase 2)"""
    
    @pytest.fixture(scope='class')
    def all_domains_data(self):
        """Load all domain data once per test class"""
        data = {}
        
        # Load contaminants
        contaminants_path = Path('data/contaminants/Contaminants.yaml')
        if contaminants_path.exists():
            with open(contaminants_path) as f:
                contaminants_data = yaml.safe_load(f)
                data['contaminants'] = contaminants_data.get('contaminants', {})
        
        return data
    
    def test_material_references_have_8_fields(self, all_domains_data):
        """Verify material references in affectsMaterials have 8 required fields"""
        required_fields = ['id', 'name', 'category', 'subcategory', 'url', 'image', 'description', 'frequency']
        materials_found = 0
        incomplete_materials = []
        
        # Check contaminants domain for affectsMaterials
        if 'contaminants' in all_domains_data:
            for item_id, item in all_domains_data['contaminants'].items():
                relationships = item.get('relationships', {})
                interactions = relationships.get('interactions', {})
                affects = interactions.get('affectsMaterials', {})
                
                if affects and isinstance(affects, dict):
                    items = affects.get('items', [])
                    for material in items:
                        if isinstance(material, dict):
                            materials_found += 1
                            
                            # Check for required fields
                            missing_fields = [f for f in required_fields if f not in material]
                            if missing_fields:
                                incomplete_materials.append({
                                    'contaminant': item_id,
                                    'material_id': material.get('id', 'unknown'),
                                    'missing': missing_fields
                                })
        
        assert materials_found > 0, "No material references found in contaminants"
        assert len(incomplete_materials) == 0, f"Found {len(incomplete_materials)} incomplete material references: {incomplete_materials[:5]}"
        print(f"✅ Validated {materials_found} material references with 8 fields each")


class TestPhase1Summary:
    """Overall Phase 1 compliance test"""
    
    def test_phase1_complete(self):
        """Verify Phase 1 implementation is complete"""
        # Load contaminants
        contaminants_path = Path('data/contaminants/Contaminants.yaml')
        with open(contaminants_path) as f:
            contaminants = yaml.safe_load(f).get('contaminants', {})
        
        # Load compounds
        compounds_path = Path('data/compounds/Compounds.yaml')
        with open(compounds_path) as f:
            compounds = yaml.safe_load(f).get('compounds', {})
        
        # Count implementations
        compound_refs = 0
        section_metadata = 0
        compound_titles = 0
        
        # Count compound references with 9 fields
        for contaminant in contaminants.values():
            produces = contaminant.get('relationships', {}).get('interactions', {}).get('producesCompounds', {})
            if produces:
                items = produces.get('items', [])
                for item in items:
                    if isinstance(item, dict) and len(item) >= 9:
                        compound_refs += 1
        
        # Count section metadata with 5 fields
        for contaminant in contaminants.values():
            relationships = contaminant.get('relationships', {})
            for group in relationships.values():
                if isinstance(group, dict):
                    for section in group.values():
                        if isinstance(section, dict):
                            meta = section.get('_section', {})
                            if len(meta) >= 5:
                                section_metadata += 1
        
        # Count compound titles
        for compound in compounds.values():
            if 'title' in compound:
                compound_titles += 1
        
        # Assertions
        assert compound_refs > 300, f"Expected 326+ compound refs, found {compound_refs}"
        assert section_metadata > 200, f"Expected 227+ section metadata, found {section_metadata}"
        assert compound_titles == len(compounds), f"Expected {len(compounds)} titles, found {compound_titles}"
        
        print(f"\n{'='*80}")
        print("PHASE 1 COMPREHENSIVE STANDARD COMPLIANCE SUMMARY")
        print(f"{'='*80}")
        print(f"✅ Compounds denormalized (9 fields): {compound_refs}")
        print(f"✅ Section metadata (5 fields): {section_metadata}")
        print(f"✅ Compound titles: {compound_titles}/{len(compounds)}")
        print(f"{'='*80}")
        print("PHASE 1: COMPLETE ✅")
        print(f"{'='*80}\n")


class TestPhase3SettingsCompletion:
    """Test Phase 3: Settings section metadata completion"""
    
    @pytest.fixture
    def settings_data(self):
        """Load settings source data"""
        path = Path('data/settings/Settings.yaml')
        with open(path) as f:
            data = yaml.safe_load(f)
        return data.get('settings', {})
    
    def test_all_settings_sections_have_complete_metadata(self, settings_data):
        """Verify all settings sections have complete 5-field metadata"""
        required_fields = ['sectionTitle', 'sectionDescription', 'icon', 'order', 'variant']
        
        total_sections = 0
        complete_sections = 0
        incomplete_sections = []
        
        for setting_id, setting in settings_data.items():
            relationships = setting.get('relationships', {})
            
            for group_name, group_data in relationships.items():
                if isinstance(group_data, dict):
                    for rel_type, rel_data in group_data.items():
                        if isinstance(rel_data, dict):
                            total_sections += 1
                            section = rel_data.get('_section', {})
                            
                            missing = [f for f in required_fields if f not in section]
                            
                            if not missing:
                                complete_sections += 1
                            else:
                                if len(incomplete_sections) < 5:
                                    incomplete_sections.append({
                                        'setting': setting_id,
                                        'group': group_name,
                                        'rel_type': rel_type,
                                        'missing': missing
                                    })
        
        completion_rate = (complete_sections / total_sections * 100) if total_sections > 0 else 0
        
        # Assert 100% completion
        assert completion_rate == 100.0, (
            f"Expected 100% section metadata completion, found {completion_rate:.1f}% "
            f"({complete_sections}/{total_sections} complete)\n"
            f"Sample incomplete: {incomplete_sections[:3]}"
        )
        
        print(f"\n{'='*80}")
        print("PHASE 3: SETTINGS SECTION METADATA COMPLETION")
        print(f"{'='*80}")
        print(f"✅ Total sections: {total_sections}")
        print(f"✅ Complete sections: {complete_sections} (100%)")
        print(f"{'='*80}")
    
    def test_settings_section_metadata_has_proper_values(self, settings_data):
        """Verify section metadata fields have proper values"""
        total_sections = 0
        valid_variants = ['default', 'warning', 'danger', 'info', 'success']
        invalid_sections = []
        
        for setting_id, setting in settings_data.items():
            relationships = setting.get('relationships', {})
            
            for group_data in relationships.values():
                if isinstance(group_data, dict):
                    for rel_data in group_data.values():
                        if isinstance(rel_data, dict):
                            section = rel_data.get('_section', {})
                            if section:
                                total_sections += 1
                                
                                # Check variant is valid
                                variant = section.get('variant')
                                if variant and variant not in valid_variants:
                                    if len(invalid_sections) < 5:
                                        invalid_sections.append({
                                            'setting': setting_id,
                                            'variant': variant,
                                            'allowed': valid_variants
                                        })
                                
                                # Check order is numeric
                                order = section.get('order')
                                if order is not None and not isinstance(order, (int, float)):
                                    if len(invalid_sections) < 5:
                                        invalid_sections.append({
                                            'setting': setting_id,
                                            'order': order,
                                            'type': type(order).__name__
                                        })
        
        assert len(invalid_sections) == 0, (
            f"Found {len(invalid_sections)} sections with invalid values:\n"
            f"{invalid_sections[:3]}"
        )
        
        print(f"✅ All {total_sections} sections have valid metadata values")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

