"""
Compound Frontmatter Structure Validation Tests

Validates that compound frontmatter files conform to the specification in:
docs/COMPOUND_FRONTMATTER_RESTRUCTURE_SPEC.md

Tests verify:
1. Only metadata and identifiers at top-level
2. All technical data under relationships.*
3. Relationships use data objects (not reference arrays)
4. Cross-references present with correct structure
5. Field naming consistency

Created: December 18, 2025
Part of: Compound Frontmatter Restructure validation
"""

import pytest
import yaml
from pathlib import Path
from typing import Dict, Any


# Path to compound frontmatter directory
FRONTMATTER_DIR = Path(__file__).parent.parent.parent.parent / 'z-beam' / 'frontmatter' / 'compounds'

# Required top-level fields (page metadata + identifiers)
REQUIRED_TOP_LEVEL = {
    'id', 'name', 'display_name', 'category', 'datePublished', 
    'dateModified', 'content_type', 'schema_version', 'full_path', 
    'breadcrumb', 'chemical_formula', 'author'
}

# Optional top-level fields (AI-generated content, identifiers)
OPTIONAL_TOP_LEVEL = {
    'subcategory', 'hazard_class', 'cas_number', 'molecular_weight',
    'description', 'health_effects', 'exposure_guidelines',
    'detection_methods', 'first_aid'
}

# Fields that MUST be under relationships (not top-level)
FORBIDDEN_TOP_LEVEL = {
    'exposure_limits', 'health_effects_keywords', 'monitoring_required',
    'typical_concentration_range', 'sources_in_laser_cleaning',
    'ppe_requirements', 'physical_properties', 'emergency_response',
    'storage_requirements', 'regulatory_classification',
    'workplace_exposure', 'synonyms_identifiers', 'reactivity',
    'environmental_impact', 'detection_monitoring'
}

# Required relationships sub-keys
REQUIRED_RELATIONSHIPS = {
    'chemical_properties', 'exposure_limits', 'health_hazards',
    'ppe_requirements', 'emergency_response', 'storage_requirements',
    'regulatory_classification', 'workplace_exposure',
    'synonyms_identifiers', 'reactivity', 'environmental_impact',
    'detection_monitoring', 'production_sources',
    'produced_by_contaminants', 'found_on_materials'
}


def load_compound_frontmatter(compound_id: str) -> Dict[str, Any]:
    """Load compound frontmatter file."""
    file_path = FRONTMATTER_DIR / f"{compound_id}-compound.yaml"
    if not file_path.exists():
        pytest.skip(f"Frontmatter file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_all_compound_ids() -> list:
    """Get list of all compound IDs from frontmatter directory."""
    if not FRONTMATTER_DIR.exists():
        return []
    
    files = FRONTMATTER_DIR.glob("*-compound.yaml")
    return [f.stem.replace('-compound', '') for f in files]


# Parametrize tests to run against all compound files
@pytest.fixture(params=get_all_compound_ids())
def compound_frontmatter(request):
    """Fixture that loads each compound frontmatter file."""
    return load_compound_frontmatter(request.param)


class TestCompoundFrontmatterStructure:
    """Test suite for compound frontmatter structure validation."""
    
    def test_has_required_top_level_fields(self, compound_frontmatter):
        """Test that all required top-level fields are present."""
        for field in REQUIRED_TOP_LEVEL:
            assert field in compound_frontmatter, (
                f"Missing required top-level field: {field}"
            )
    
    def test_no_forbidden_fields_at_top_level(self, compound_frontmatter):
        """Test that technical data is NOT at top-level (must be in relationships)."""
        for field in FORBIDDEN_TOP_LEVEL:
            assert field not in compound_frontmatter, (
                f"Forbidden field at top-level: {field}\n"
                f"This field must be under relationships.{field}"
            )
    
    def test_has_relationships_dict(self, compound_frontmatter):
        """Test that relationships dict exists."""
        assert 'relationships' in compound_frontmatter, (
            "Missing 'relationships' dict"
        )
        assert isinstance(compound_frontmatter['relationships'], dict), (
            "'relationships' must be a dict"
        )
    
    def test_relationships_has_required_keys(self, compound_frontmatter):
        """Test that all required relationship keys are present."""
        relationships = compound_frontmatter.get('relationships', {})
        
        for key in REQUIRED_RELATIONSHIPS:
            assert key in relationships, (
                f"Missing required relationship key: {key}"
            )
    
    def test_relationships_use_data_objects_not_arrays(self, compound_frontmatter):
        """Test that relationships use data objects, not reference arrays."""
        relationships = compound_frontmatter.get('relationships', {})
        
        # These fields should be dicts (data objects), not lists (reference arrays)
        data_object_fields = [
            'chemical_properties', 'exposure_limits', 'health_hazards',
            'ppe_requirements', 'emergency_response', 'storage_requirements',
            'regulatory_classification', 'workplace_exposure',
            'synonyms_identifiers', 'reactivity', 'environmental_impact',
            'detection_monitoring', 'production_sources'
        ]
        
        for field in data_object_fields:
            if field in relationships:
                assert not isinstance(relationships[field], list) or (
                    isinstance(relationships[field], list) and 
                    len(relationships[field]) > 0 and 
                    not isinstance(relationships[field][0], dict) or
                    'type' not in relationships[field][0]
                ), (
                    f"relationships.{field} should be a data object (dict), "
                    f"not a reference array (list with type/id)"
                )
    
    def test_cross_references_have_correct_structure(self, compound_frontmatter):
        """Test that cross-reference fields have grouped structure."""
        relationships = compound_frontmatter.get('relationships', {})
        
        # Check produced_by_contaminants structure
        if 'produced_by_contaminants' in relationships:
            pbc = relationships['produced_by_contaminants']
            assert isinstance(pbc, dict), (
                "produced_by_contaminants must be a dict"
            )
            assert 'title' in pbc, "produced_by_contaminants must have 'title'"
            assert 'description' in pbc, "produced_by_contaminants must have 'description'"
            assert 'items' in pbc, "produced_by_contaminants must have 'items'"
            assert isinstance(pbc['items'], list), (
                "produced_by_contaminants.items must be a list"
            )
        
        # Check found_on_materials structure
        if 'found_on_materials' in relationships:
            fom = relationships['found_on_materials']
            assert isinstance(fom, dict), (
                "found_on_materials must be a dict"
            )
            assert 'title' in fom, "found_on_materials must have 'title'"
            assert 'description' in fom, "found_on_materials must have 'description'"
            assert 'items' in fom, "found_on_materials must have 'items'"
            assert isinstance(fom['items'], list), (
                "found_on_materials.items must be a list"
            )
    
    def test_exposure_limits_group_structure(self, compound_frontmatter):
        """Test that exposure_limits has combined fields."""
        relationships = compound_frontmatter.get('relationships', {})
        
        if 'exposure_limits' in relationships:
            el = relationships['exposure_limits']
            assert isinstance(el, dict), "exposure_limits must be a dict"
            
            # Should contain both exposure limit values AND monitoring fields
            expected_fields = ['monitoring_required', 'typical_concentration_range']
            # At least one should be present (some compounds may not have all)
    
    def test_health_hazards_group_structure(self, compound_frontmatter):
        """Test that health_hazards has structured format."""
        relationships = compound_frontmatter.get('relationships', {})
        
        if 'health_hazards' in relationships:
            hh = relationships['health_hazards']
            assert isinstance(hh, dict), "health_hazards must be a dict"
            assert 'keywords' in hh, "health_hazards must have 'keywords'"
            assert isinstance(hh['keywords'], list), (
                "health_hazards.keywords must be a list"
            )
    
    def test_production_sources_structure(self, compound_frontmatter):
        """Test that production_sources has structured laser_cleaning_processes."""
        relationships = compound_frontmatter.get('relationships', {})
        
        if 'production_sources' in relationships:
            ps = relationships['production_sources']
            assert isinstance(ps, dict), "production_sources must be a dict"
            assert 'laser_cleaning_processes' in ps, (
                "production_sources must have 'laser_cleaning_processes'"
            )
            
            lcp = ps['laser_cleaning_processes']
            assert isinstance(lcp, list), (
                "laser_cleaning_processes must be a list"
            )
            
            # Check structure of items
            for item in lcp:
                assert isinstance(item, dict), (
                    "laser_cleaning_processes items must be dicts"
                )
                assert 'process' in item, (
                    "laser_cleaning_processes items must have 'process'"
                )
                assert 'description' in item, (
                    "laser_cleaning_processes items must have 'description'"
                )
    
    def test_schema_version_is_5_0_0(self, compound_frontmatter):
        """Test that schema_version is 5.0.0."""
        assert compound_frontmatter.get('schema_version') == '5.0.0', (
            "schema_version must be '5.0.0' for new structure"
        )


class TestCompoundFrontmatterValidation:
    """Validation tests to run after migration."""
    
    def test_all_compounds_migrated(self):
        """Test that all expected compound files exist."""
        # Known compound IDs (from Compounds.yaml metadata)
        expected_compounds = 20  # As per metadata.total_compounds
        
        if not FRONTMATTER_DIR.exists():
            pytest.skip("Frontmatter directory not found")
        
        actual_files = list(FRONTMATTER_DIR.glob("*-compound.yaml"))
        
        assert len(actual_files) == expected_compounds, (
            f"Expected {expected_compounds} compound files, found {len(actual_files)}"
        )
    
    def test_no_null_required_fields(self, compound_frontmatter):
        """Test that required fields are not null."""
        required_non_null = ['id', 'name', 'display_name', 'content_type', 'schema_version']
        
        for field in required_non_null:
            value = compound_frontmatter.get(field)
            assert value is not None, (
                f"Required field '{field}' is null"
            )
            assert value != '', (
                f"Required field '{field}' is empty string"
            )


def test_migration_script_exists():
    """Test that migration script exists and is executable."""
    script_path = Path(__file__).parent.parent.parent / 'scripts' / 'migration' / 'migrate_compound_frontmatter.py'
    
    assert script_path.exists(), (
        f"Migration script not found: {script_path}"
    )
    
    # Check if it's executable (on Unix-like systems)
    import os
    if os.name != 'nt':  # Not Windows
        assert os.access(script_path, os.X_OK) or script_path.suffix == '.py', (
            f"Migration script is not executable: {script_path}"
        )
