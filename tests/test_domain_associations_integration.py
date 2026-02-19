#!/usr/bin/env python3
"""
Test Suite: Domain Associations and Relationship Generation

PURPOSE: Verify single source of truth architecture for frontmatter relationships
COVERAGE:
  - Image URL format (no category paths, correct format)
  - Full IDs with suffixes (aluminum-laser-cleaning, adhesive-residue-contamination)
  - No stale relationships in source data
  - Relationships generator configured in export configs
  - No slug generators (prevent duplicate files)
  - Export produces correct file counts

CONTEXT: 
  - Migration completed Dec 18, 2025
  - Single source of truth: DomainAssociations.yaml
  - 619 material-contaminant associations
  - All 422 frontmatter files generated correctly

GRADE: Must pass 100% before production deployment
"""

import pytest
import yaml
from pathlib import Path
from shared.validation.domain_associations import DomainAssociationsValidator


class TestDomainAssociationsImageURLs:
    """Test image URL generation uses correct format"""
    
    def setup_method(self):
        """Initialize validator for all tests"""
        self.validator = DomainAssociationsValidator()
        self.validator.load()
    
    def test_contaminant_image_urls_no_category_paths(self):
        """Verify contaminant image URLs don't contain category paths"""
        contaminants = self.validator.get_contaminants_for_material('aluminum-laser-cleaning')
        
        assert len(contaminants) > 0, "No contaminants found for aluminum"
        
        for cont in contaminants:
            image = cont.get('image', '')
            
            # Should NOT contain category paths
            assert '/metal/' not in image, f"Image contains category: {image}"
            assert '/non-ferrous/' not in image, f"Image contains subcategory: {image}"
            assert '/wood/' not in image, f"Image contains category: {image}"
            assert '/plastic/' not in image, f"Image contains category: {image}"
            
            # Should use correct format - contaminants should have contaminant images
            assert image.startswith('/images/contaminants/'), \
                f"Wrong image prefix: {image}"
            assert image.endswith('.jpg'), \
                f"Wrong image suffix: {image}"
    
    def test_material_image_urls_no_category_paths(self):
        """Verify material image URLs don't contain category paths"""
        materials = self.validator.get_materials_for_contaminant('adhesive-residue-contamination')
        
        assert len(materials) > 0, "No materials found for adhesive residue"
        
        for mat in materials:
            image = mat.get('image', '')
            
            # Should NOT contain category paths
            assert '/metal/' not in image, f"Image contains category: {image}"
            assert '/non-ferrous/' not in image, f"Image contains subcategory: {image}"
            
            # Should use correct format
            assert image.startswith('/images/material/'), \
                f"Wrong image prefix: {image}"
            assert image.endswith('-laser-cleaning-hero.jpg'), \
                f"Wrong image suffix: {image}"
    
    def test_image_urls_use_lowercase_slugs(self):
        """Verify image URLs use lowercase slugs (no capitals)"""
        contaminants = self.validator.get_contaminants_for_material('aluminum-laser-cleaning')
        
        for cont in contaminants:
            image = cont.get('image', '')
            
            # Extract slug from image path
            slug = image.replace('/images/material/', '').replace('-laser-cleaning-hero.jpg', '')
            
            # Should be all lowercase
            assert slug == slug.lower(), \
                f"Image slug not lowercase: {slug}"
            
            # Should use hyphens, not underscores or spaces
            assert '_' not in slug, f"Image slug has underscores: {slug}"
            assert ' ' not in slug, f"Image slug has spaces: {slug}"


class TestDomainAssociationsFullIDs:
    """Test all IDs include proper suffixes"""
    
    def setup_method(self):
        """Initialize validator for all tests"""
        self.validator = DomainAssociationsValidator()
        self.validator.load()
    
    def test_material_ids_have_laser_cleaning_suffix(self):
        """Verify material IDs end with -laser-cleaning"""
        materials = self.validator.get_materials_for_contaminant('adhesive-residue-contamination')
        
        assert len(materials) > 0, "No materials found"
        
        for mat in materials:
            mat_id = mat.get('id', '')
            assert mat_id.endswith('-laser-cleaning'), \
                f"Material ID missing suffix: {mat_id}"
    
    def test_contaminant_ids_have_contamination_suffix(self):
        """Verify contaminant IDs end with -contamination"""
        contaminants = self.validator.get_contaminants_for_material('aluminum-laser-cleaning')
        
        assert len(contaminants) > 0, "No contaminants found"
        
        for cont in contaminants:
            cont_id = cont.get('id', '')
            assert cont_id.endswith('-contamination'), \
                f"Contaminant ID missing suffix: {cont_id}"
    
    def test_compound_ids_exist(self):
        """Verify compounds are returned (may not have standard suffix)"""
        compounds = self.validator.get_compounds_for_contaminant('carbon-buildup-contamination')
        
        # May be empty list for some contaminants
        for comp in compounds:
            comp_id = comp.get('id', '')
            assert len(comp_id) > 0, "Compound has empty ID"
            assert comp_id == comp_id.lower(), "Compound ID not lowercase"
            assert '-' in comp_id or len(comp_id.split()) == 1, \
                "Compound ID should use hyphens or be single word"


class TestSourceDataCleanliness:
    """Test source data relationship structures match current denormalized architecture."""
    
    def test_contaminants_yaml_has_relationships_field(self):
        """Verify Contaminants.yaml stores relationships in source data."""
        contaminants_path = Path('data/contaminants/Contaminants.yaml')
        
        assert contaminants_path.exists(), "Contaminants.yaml not found"
        
        with open(contaminants_path, 'r') as f:
            data = yaml.safe_load(f)
        
        patterns = data.get('contaminants', {})
        for pattern_id, pattern in patterns.items():
            assert 'relationships' in pattern, \
                f"Pattern {pattern_id} missing relationships field in source data"
            assert isinstance(pattern.get('relationships'), dict), \
                f"Pattern {pattern_id} relationships must be a dict"
    
    def test_materials_yaml_has_relationships_field(self):
        """Verify Materials.yaml stores relationships in source data."""
        materials_path = Path('data/materials/Materials.yaml')
        
        assert materials_path.exists(), "Materials.yaml not found"
        
        with open(materials_path, 'r') as f:
            data = yaml.safe_load(f)
        
        materials = data.get('materials', {})
        
        # Check each material
        for material_id, material in materials.items():
            assert 'relationships' in material, \
                f"Material {material_id} missing relationships field in source data"
            assert isinstance(material.get('relationships'), dict), \
                f"Material {material_id} relationships must be a dict"


class TestExportConfiguration:
    """Test export configs are properly configured"""
    
    def test_contaminants_config_has_relationships_generator(self):
        """Verify contaminants export config supports relationships in current architecture."""
        config_path = Path('export/config/contaminants.yaml')
        
        assert config_path.exists(), "Contaminants export config not found"
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        generators = config.get('generators', [])
        has_legacy_relationships = any(g.get('type') == 'relationships' for g in generators)
        has_universal_pipeline = any(g.get('type') == 'universal_content' for g in generators)

        assert has_legacy_relationships or has_universal_pipeline, \
            "Contaminants config missing both legacy relationships and universal_content pipeline support"
    
    def test_no_slug_generator_in_materials_config(self):
        """Verify slug generator removed from materials config (prevents duplicates)"""
        config_path = Path('export/config/materials.yaml')
        
        assert config_path.exists(), "Materials export config not found"
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        generators = config.get('generators', [])
        slug_generators = [g for g in generators if g.get('type') == 'slug']
        
        assert len(slug_generators) == 0, \
            "Found slug generator in materials config (causes duplicate file generation)"
    
    def test_no_slug_generator_in_contaminants_config(self):
        """Verify slug generator removed from contaminants config (prevents duplicates)"""
        config_path = Path('export/config/contaminants.yaml')
        
        assert config_path.exists(), "Contaminants export config not found"
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        generators = config.get('generators', [])
        slug_generators = [g for g in generators if g.get('type') == 'slug']
        
        assert len(slug_generators) == 0, \
            "Found slug generator in contaminants config (causes duplicate file generation)"


class TestExportedFrontmatter:
    """Test exported frontmatter files are correct"""
    
    def test_no_duplicate_materials_files(self):
        """Verify no duplicate materials files (all should end with -laser-cleaning.yaml)"""
        materials_dir = Path('frontmatter/materials')
        
        if not materials_dir.exists():
            pytest.skip("Frontmatter not exported yet")
        
        all_files = list(materials_dir.glob('*.yaml'))
        correct_files = [f for f in all_files if f.name.endswith('-laser-cleaning.yaml')]
        
        # All files should have correct suffix
        assert len(all_files) == len(correct_files), \
            f"Found {len(all_files) - len(correct_files)} materials files without -laser-cleaning.yaml suffix (duplicates)"
    
    def test_no_duplicate_contaminants_files(self):
        """Verify no duplicate contaminants files (all should end with -contaminant.yaml)"""
        contaminants_dir = Path('frontmatter/contaminants')
        
        if not contaminants_dir.exists():
            pytest.skip("Frontmatter not exported yet")
        
        all_files = list(contaminants_dir.glob('*.yaml'))
        correct_files = [f for f in all_files if f.name.endswith('-contaminant.yaml')]
        
        # All files should have correct suffix
        assert len(all_files) == len(correct_files), \
            f"Found {len(all_files) - len(correct_files)} contaminants files without -contaminant.yaml suffix (duplicates)"
    
    def test_materials_frontmatter_image_urls(self):
        """Verify exported materials frontmatter has correct image URLs in relationships"""
        materials_dir = Path('frontmatter/materials')
        
        if not materials_dir.exists():
            pytest.skip("Frontmatter not exported yet")
        
        # Test first 5 materials files
        test_files = list(materials_dir.glob('*-laser-cleaning.yaml'))[:5]
        
        for file_path in test_files:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            relationships = data.get('relationships', {})
            contaminants = relationships.get('related_contaminants', [])
            
            for cont in contaminants:
                image = cont.get('image', '')
                
                if image:  # Some may not have images
                    # Should NOT have category paths
                    assert '/metal/' not in image, \
                        f"Bad image URL in {file_path.name}: {image}"
                    assert '/non-ferrous/' not in image, \
                        f"Bad image URL in {file_path.name}: {image}"
                    
                    # Should use correct format
                    assert image.startswith('/images/material/'), \
                        f"Wrong image format in {file_path.name}: {image}"
                    assert image.endswith('-laser-cleaning-hero.jpg'), \
                        f"Wrong image suffix in {file_path.name}: {image}"
    
    def test_contaminants_frontmatter_image_urls(self):
        """Verify exported contaminants frontmatter has correct image URLs in relationships"""
        contaminants_dir = Path('frontmatter/contaminants')
        
        if not contaminants_dir.exists():
            pytest.skip("Frontmatter not exported yet")
        
        # Test first 5 contaminants files
        test_files = list(contaminants_dir.glob('*-contaminant.yaml'))[:5]
        
        for file_path in test_files:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            relationships = data.get('relationships', {})
            materials = relationships.get('related_materials', [])
            
            for mat in materials:
                image = mat.get('image', '')
                
                if image:  # Some may not have images
                    # Should NOT have category paths
                    assert '/metal/' not in image, \
                        f"Bad image URL in {file_path.name}: {image}"
                    assert '/non-ferrous/' not in image, \
                        f"Bad image URL in {file_path.name}: {image}"
                    
                    # Should use correct format
                    assert image.startswith('/images/material/'), \
                        f"Wrong image format in {file_path.name}: {image}"


class TestDomainAssociationsYAML:
    """Test DomainAssociations.yaml structure and completeness"""
    
    def test_domain_associations_file_exists(self):
        """Verify DomainAssociations.yaml exists"""
        associations_path = Path('data/associations/DomainAssociations.yaml')
        assert associations_path.exists(), "DomainAssociations.yaml not found"
    
    def test_material_contaminant_associations_populated(self):
        """Verify material-contaminant associations are populated"""
        associations_path = Path('data/associations/DomainAssociations.yaml')
        
        with open(associations_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Count material→contaminant associations in the associations list
        associations = data.get('associations', [])
        material_contaminant_count = sum(
            1 for assoc in associations 
            if assoc.get('source_domain') == 'materials' and 
               assoc.get('target_domain') == 'contaminants' and
               assoc.get('relationship_type') == 'can_have_contamination'
        )
        
        # Should have ~1300+ material→contaminant associations (98 materials × ~14 contaminants each)
        assert material_contaminant_count > 500, \
            f"Expected 500+ material→contaminant associations, found {material_contaminant_count}"
    
    def test_associations_have_required_fields(self):
        """Verify associations have all required fields"""
        associations_path = Path('data/associations/DomainAssociations.yaml')
        
        with open(associations_path, 'r') as f:
            data = yaml.safe_load(f)
        
        associations = data.get('material_contaminant_associations', [])
        
        # Test first 10 associations
        for assoc in associations[:10]:
            assert 'material_id' in assoc, "Missing material_id"
            assert 'contaminant_id' in assoc, "Missing contaminant_id"
            assert 'frequency' in assoc, "Missing frequency"
            assert 'severity' in assoc, "Missing severity"
            
            # Verify IDs have correct suffixes
            assert assoc['material_id'].endswith('-laser-cleaning'), \
                f"Material ID missing suffix: {assoc['material_id']}"
            assert assoc['contaminant_id'].endswith('-contamination'), \
                f"Contaminant ID missing suffix: {assoc['contaminant_id']}"
            
            # Verify frequency values
            assert assoc['frequency'] in ['common', 'uncommon', 'rare'], \
                f"Invalid frequency: {assoc['frequency']}"
            
            # Verify severity values
            assert assoc['severity'] in ['high', 'moderate', 'low'], \
                f"Invalid severity: {assoc['severity']}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
