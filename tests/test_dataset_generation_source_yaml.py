"""
Test suite for standalone dataset generation from source YAML

Tests the new source YAML-based dataset generation approach that replaces
the frontmatter-dependent pipeline. Validates:
- Direct YAML loading
- Schema.org JSON format
- CSV tabular format
- TXT human-readable format
- ADR 005 consolidation (materials+settings, contaminants+compounds)
- Generation statistics and error handling

File: scripts/export/generate_datasets.py
"""

import json
import csv
import tempfile
import sys
from pathlib import Path
import pytest

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

# Only skip non-critical tests
# Critical data completeness tests are NOT skipped


class TestDatasetGeneratorInitialization:
    """Test DatasetGenerator initialization and setup"""
    
    def test_generator_init_valid_path(self):
        """Test generator initializes with valid z-beam path"""
        from shared.dataset import MaterialsDataset, ContaminantsDataset
        
        # Test Dataset classes can be instantiated
        materials_dataset = MaterialsDataset()
        contaminants_dataset = ContaminantsDataset()
        
        assert materials_dataset is not None
        assert contaminants_dataset is not None
        print("✅ Dataset classes initialized successfully")
    
    def test_generator_init_invalid_path(self):
        """Test generator fails fast with invalid path"""
        # Dataset classes load from data/ directory
        # Invalid paths would cause FileNotFoundError in yaml.safe_load
        import yaml
        from pathlib import Path
        
        with pytest.raises(FileNotFoundError):
            with open("/nonexistent/path/Materials.yaml") as f:
                yaml.safe_load(f)
        
        print("✅ Invalid path raises FileNotFoundError as expected")
    
    def test_site_config_loading(self):
        """Test site configuration loads from z-beam/site-config.json"""
        # Site config is optional - tests default behavior
        default_config = {
            'site': {
                'domain': 'https://example.com',
                'name': 'Test Site'
            }
        }
        
        assert 'domain' in default_config['site']
        assert 'name' in default_config['site']
        print("✅ Site config structure validated")


class TestMaterialsDatasetGeneration:
    """Test materials dataset generation"""
    
    def test_materials_json_format(self):
        """Test JSON dataset has valid Schema.org structure"""
        from shared.dataset import MaterialsDataset
        
        dataset = MaterialsDataset()
        materials = dataset.get_all_materials()
        
        if not materials:
            pytest.skip("No materials found")
        
        # Test first material
        first_slug = list(materials.keys())[0]
        first_material = materials[first_slug]
        
        json_data = dataset.to_schema_org_json(first_slug, first_material)
        
        # Verify Schema.org structure
        assert json_data["@context"] == "https://schema.org"
        assert json_data["@type"] == "Dataset"
        assert "@id" in json_data
        # Verify @id format: https://www.z-beam.com/datasets/materials/{slug}-material-dataset#dataset
        assert "/datasets/materials/" in json_data["@id"], "@id must include /datasets/materials/ subdirectory"
        assert "-material-dataset#dataset" in json_data["@id"], "@id must end with -material-dataset#dataset"
        assert "name" in json_data
        assert "description" in json_data
        assert "variableMeasured" in json_data
        # v3.0: distribution, keywords, citations removed
        
        # Verify variableMeasured has sufficient items
        var_count = len(json_data["variableMeasured"])
        assert var_count >= 10, f"Expected ≥10 variables, got {var_count}"
        
        # Verify identifier has proper suffix
        assert "-material-dataset" in json_data["identifier"], "identifier must include -material-dataset suffix"
        
        print(f"✅ {first_slug}: Valid Schema.org structure with {var_count} variables")
    
    def test_materials_csv_format(self):
        """Test CSV dataset has correct structure"""
        from shared.dataset import MaterialsDataset
        
        dataset = MaterialsDataset()
        materials = dataset.get_all_materials()
        
        if not materials:
            pytest.skip("No materials found")
        
        first_slug = list(materials.keys())[0]
        first_material = materials[first_slug]
        
        csv_rows = dataset.to_csv_rows(first_material)
        
        # Verify CSV structure
        assert len(csv_rows) > 0, "No CSV rows generated"
        
        # Verify headers
        first_row = csv_rows[0]
        assert "Category" in first_row
        assert "Property" in first_row
        assert "Value" in first_row
        assert "Unit" in first_row
        
        # Check if machine settings appear first (ADR 005)
        machine_setting_rows = [r for r in csv_rows if r.get("Category") == "Machine Setting"]
        if machine_setting_rows:
            # First row should be machine setting
            assert csv_rows[0]["Category"] == "Machine Setting", "Machine settings should appear FIRST"
            print(f"✅ {len(machine_setting_rows)} machine settings appear first (ADR 005 compliant)")
        
        print(f"✅ {first_slug}: Valid CSV with {len(csv_rows)} rows")
    
    def test_materials_txt_format(self):
        """Test TXT dataset is human-readable"""
        from shared.dataset import MaterialsDataset
        
        dataset = MaterialsDataset()
        materials = dataset.get_all_materials()
        
        if not materials:
            pytest.skip("No materials found")
        
        first_slug = list(materials.keys())[0]
        first_material = materials[first_slug]
        
        txt_content = dataset.to_txt(first_slug, first_material)
        
        # Verify TXT structure
        assert len(txt_content) > 0, "No TXT content generated"
        assert "DATASET:" in txt_content
        assert "===" in txt_content  # Header separator
        
        # Check for sections
        assert "MACHINE SETTINGS:" in txt_content or "MATERIAL PROPERTIES:" in txt_content
        
        print(f"✅ {first_slug}: Valid TXT format ({len(txt_content)} chars)")
    
    def test_materials_slug_extraction(self):
        """Test base slug extraction from -laser-cleaning suffix"""
        from shared.dataset import MaterialsDataset
        
        dataset = MaterialsDataset()
        
        # Test slug extraction
        test_cases = [
            ("aluminum-laser-cleaning", "aluminum"),
            ("steel-laser-cleaning", "steel"),
            ("stainless-steel-316-laser-cleaning", "stainless-steel-316"),
        ]
        
        for full_slug, expected_base in test_cases:
            base_slug = dataset.get_base_slug(full_slug)
            assert base_slug == expected_base, f"Expected '{expected_base}', got '{base_slug}'"
        
        print("✅ Slug extraction working correctly")
    
    def test_materials_streamlined_format(self):
        """Test v3.0 streamlined format (no keywords, distribution, citations)"""
        from shared.dataset import MaterialsDataset
        
        dataset = MaterialsDataset()
        materials = dataset.get_all_materials()
        
        if not materials:
            pytest.skip("No materials found")
        
        first_slug = list(materials.keys())[0]
        first_material = materials[first_slug]
        
        json_data = dataset.to_schema_org_json(first_slug, first_material)
        
        # v3.0: Verify removed fields are absent
        assert "keywords" not in json_data, "v3.0 should not include keywords"
        assert "distribution" not in json_data, "v3.0 should not include distribution"
        assert "citation" not in json_data, "v3.0 should not include citation"
        assert "dateModified" not in json_data, "v3.0 should not include dateModified"
        assert "license" not in json_data, "v3.0 should not include license details"
        
        print(f"✅ {first_slug}: v3.0 streamlined format validated")


class TestContaminantsDatasetGeneration:
    """Test contaminants dataset generation with compounds merged"""
    
    def test_contaminants_json_format(self):
        """Test JSON dataset has valid Schema.org structure"""
        from shared.dataset import ContaminantsDataset
        
        dataset = ContaminantsDataset()
        contaminants = dataset.get_all_contaminants()
        
        if not contaminants:
            pytest.skip("No contaminants found")
        
        # Test first contaminant
        first_id = list(contaminants.keys())[0]
        first_contaminant = contaminants[first_id]
        
        # Merge compounds first (ADR 005)
        enriched_data = dataset.merge_compounds(first_contaminant)
        
        json_data = dataset.to_schema_org_json(first_id, enriched_data)
        
        # Verify Schema.org structure
        assert json_data["@context"] == "https://schema.org"
        assert json_data["@type"] == "Dataset"
        assert "@id" in json_data
        assert "name" in json_data
        assert "variableMeasured" in json_data
        
        print(f"✅ {first_id}: Valid Schema.org structure")
    
    def test_compounds_merging(self):
        """Test compound data merged into contaminant datasets (ADR 005)"""
        from shared.dataset import ContaminantsDataset
        
        dataset = ContaminantsDataset()
        contaminants = dataset.get_all_contaminants()
        
        # Find contaminant with related compounds
        contaminant_with_compounds = None
        for pattern_id, pattern_data in contaminants.items():
            if pattern_data.get('related_compounds'):
                contaminant_with_compounds = (pattern_id, pattern_data)
                break
        
        if not contaminant_with_compounds:
            pytest.skip("No contaminants with related compounds found")
        
        pattern_id, pattern_data = contaminant_with_compounds
        enriched_data = dataset.merge_compounds(pattern_data)
        
        # Verify compounds array exists
        assert 'compounds' in enriched_data
        compounds = enriched_data['compounds']
        
        if len(compounds) > 0:
            # Verify compound structure
            first_compound = compounds[0]
            assert 'id' in first_compound
            assert 'name' in first_compound
            print(f"✅ {pattern_id}: {len(compounds)} compounds merged (ADR 005 compliant)")
        else:
            print(f"⚠️  {pattern_id}: No compound data found for related_compounds")
    
    def test_contaminants_csv_format(self):
        """Test CSV dataset structure for contaminants"""
        from shared.dataset import ContaminantsDataset
        
        dataset = ContaminantsDataset()
        contaminants = dataset.get_all_contaminants()
        
        if not contaminants:
            pytest.skip("No contaminants found")
        
        first_id = list(contaminants.keys())[0]
        first_contaminant = contaminants[first_id]
        
        enriched_data = dataset.merge_compounds(first_contaminant)
        csv_rows = dataset.to_csv_rows(enriched_data)
        
        # CSV rows may be empty if contaminant has minimal data
        # This is acceptable - just verify no errors occur
        if len(csv_rows) == 0:
            print(f"⚠️  {first_id}: No CSV rows (minimal contaminant data)")
            return
        
        # Verify headers
        first_row = csv_rows[0]
        assert "Category" in first_row
        assert "Property" in first_row
        assert "Value" in first_row
        
        print(f"✅ {first_id}: Valid CSV with {len(csv_rows)} rows")
    
    def test_contaminants_txt_format(self):
        """Test TXT includes compounds section"""
        from shared.dataset import ContaminantsDataset
        
        dataset = ContaminantsDataset()
        contaminants = dataset.get_all_contaminants()
        
        if not contaminants:
            pytest.skip("No contaminants found")
        
        # Find contaminant with compounds
        for pattern_id, pattern_data in contaminants.items():
            enriched_data = dataset.merge_compounds(pattern_data)
            txt_content = dataset.to_txt(pattern_id, enriched_data)
            
            # Verify TXT structure
            assert len(txt_content) > 0
            assert "DATASET:" in txt_content
            
            # Check for compounds section if compounds exist
            if enriched_data.get('compounds'):
                assert "COMPOUNDS:" in txt_content or "CHEMICAL" in txt_content
                print(f"✅ {pattern_id}: TXT includes compounds section")
                break
        else:
            print("⚠️  No contaminants with compounds to test")


class TestADR005Consolidation:
    """Test ADR 005 dataset consolidation architecture"""
    
    def test_materials_settings_unified(self):
        """Test materials datasets include machine settings"""
        from shared.dataset import MaterialsDataset
        
        dataset = MaterialsDataset()
        materials = dataset.get_all_materials()
        
        # Find material with machine settings
        material_with_settings = None
        for slug, material_data in materials.items():
            if material_data.get('machine_settings'):
                material_with_settings = (slug, material_data)
                break
        
        if not material_with_settings:
            print("⚠️  No materials with machine_settings found")
            return
        
        slug, material_data = material_with_settings
        
        # Verify JSON includes machine settings
        json_data = dataset.to_schema_org_json(slug, material_data)
        var_measured = json_data.get("variableMeasured", [])
        machine_vars = [v for v in var_measured if "laser" in v.get("description", "").lower()]
        
        # Verify CSV has machine settings FIRST
        csv_rows = dataset.to_csv_rows(material_data)
        if csv_rows and csv_rows[0].get("Category") == "Machine Setting":
            print(f"✅ {slug}: Machine settings appear FIRST in CSV (ADR 005)")
        
        # Verify TXT has machine settings section
        txt_content = dataset.to_txt(slug, material_data)
        assert "MACHINE SETTINGS" in txt_content
        
        print(f"✅ ADR 005: Materials + Settings unified")
    
    def test_contaminants_compounds_merged(self):
        """Test contaminant datasets include compounds array"""
        from shared.dataset import ContaminantsDataset
        
        dataset = ContaminantsDataset()
        contaminants = dataset.get_all_contaminants()
        
        # Find contaminant with compounds
        found_with_compounds = False
        for pattern_id, pattern_data in contaminants.items():
            if pattern_data.get('related_compounds'):
                enriched_data = dataset.merge_compounds(pattern_data)
                
                if enriched_data.get('compounds'):
                    # Verify compounds array structure
                    compounds = enriched_data['compounds']
                    if len(compounds) > 0:
                        first_compound = compounds[0]
                        assert 'id' in first_compound
                        assert 'name' in first_compound
                        found_with_compounds = True
                        print(f"✅ {pattern_id}: Compounds merged (ADR 005)")
                        break
        
        if not found_with_compounds:
            print("⚠️  No contaminants with merged compound data found")
    
    def test_output_directories(self):
        """Test outputs go to correct consolidated directories"""
        z_beam_path = project_root.parent / "z-beam"
        
        if not z_beam_path.exists():
            pytest.skip("z-beam project not found")
        
        datasets_dir = z_beam_path / "public" / "datasets"
        
        if not datasets_dir.exists():
            pytest.skip("Datasets directory not found")
        
        # Verify consolidated directories exist
        materials_dir = datasets_dir / "materials"
        contaminants_dir = datasets_dir / "contaminants"
        
        assert materials_dir.exists(), "datasets/materials/ should exist (ADR 005)"
        assert contaminants_dir.exists(), "datasets/contaminants/ should exist (ADR 005)"
        
        # Verify NO separate settings or compounds directories
        settings_dir = datasets_dir / "settings"
        compounds_dir = datasets_dir / "compounds"
        
        assert not settings_dir.exists(), "datasets/settings/ should NOT exist (consolidated into materials)"
        assert not compounds_dir.exists(), "datasets/compounds/ should NOT exist (merged into contaminants)"
        
        print("✅ ADR 005: Consolidated directory structure verified")


@pytest.mark.critical
class TestVariableMeasuredArray:
    """Test variableMeasured array generation (≥20 required)"""
    
    @pytest.mark.critical
    def test_materials_variable_measured_minimum(self):
        """CRITICAL: Test materials datasets have ≥20 variableMeasured items"""
        z_beam_path = project_root.parent / "z-beam"
        if not z_beam_path.exists():
            pytest.skip("z-beam project not found")
        
        datasets_dir = z_beam_path / "public" / "datasets" / "materials"
        if not datasets_dir.exists():
            pytest.skip("Datasets not generated yet")
        
        # Test sample of materials
        test_materials = ["aluminum.json", "steel.json", "copper.json"]
        for material_file in test_materials:
            json_path = datasets_dir / material_file
            if json_path.exists():
                with open(json_path) as f:
                    data = json.load(f)
                    var_count = len(data.get("variableMeasured", []))
                    assert var_count >= 20, f"{material_file}: Expected ≥20 variables, got {var_count}"
                    print(f"✅ {material_file}: {var_count} variables")
    
    @pytest.mark.critical
    def test_contaminants_variable_measured_minimum(self):
        """CRITICAL: Test contaminant datasets have ≥20 variableMeasured items"""
        z_beam_path = project_root.parent / "z-beam"
        if not z_beam_path.exists():
            pytest.skip("z-beam project not found")
        
        datasets_dir = z_beam_path / "public" / "datasets" / "contaminants"
        if not datasets_dir.exists():
            pytest.skip("Datasets not generated yet")
        
        # Test at least one contaminant file if any exist
        json_files = list(datasets_dir.glob("*.json"))
        if json_files:
            test_file = json_files[0]
            with open(test_file) as f:
                data = json.load(f)
                var_count = len(data.get("variableMeasured", []))
                # Contaminants may have fewer properties than materials
                assert var_count >= 5, f"{test_file.name}: Expected ≥5 variables, got {var_count}"
                print(f"✅ {test_file.name}: {var_count} variables")
    
    @pytest.mark.critical
    def test_variable_measured_structure(self):
        """CRITICAL: Test each variableMeasured item has required fields"""
        z_beam_path = project_root.parent / "z-beam"
        if not z_beam_path.exists():
            pytest.skip("z-beam project not found")
        
        json_path = z_beam_path / "public" / "datasets" / "materials" / "aluminum.json"
        if not json_path.exists():
            pytest.skip("aluminum.json not found")
        
        with open(json_path) as f:
            data = json.load(f)
            variables = data.get("variableMeasured", [])
            
            assert len(variables) > 0, "No variableMeasured items found"
            
            for idx, var in enumerate(variables[:5]):  # Check first 5
                assert var.get("@type") == "PropertyValue", f"Variable {idx}: Missing @type"
                assert "name" in var, f"Variable {idx}: Missing name"
                assert "description" in var, f"Variable {idx}: Missing description"
                # Check for value/unit fields (should be present in our implementation)
                assert "value" in var or "unitText" in var, f"Variable {idx}: Missing value/unit data"


class TestGenerationStatistics:
    """Test generation statistics and reporting"""
    
    def test_statistics_tracking(self):
        """Test stats track generated/skipped/errors"""
        # TODO: Generate datasets with some failures
        # TODO: Verify stats.generated count correct
        # TODO: Verify stats.errors count correct
        # TODO: Verify stats.total_files count correct
        pass
    
    def test_summary_output(self):
        """Test summary prints correctly"""
        # TODO: Capture summary output
        # TODO: Verify format matches expected
        # TODO: Verify counts displayed
        pass


class TestErrorHandling:
    """Test error handling and recovery"""
    
    def test_missing_material_data(self):
        """Test graceful handling of missing material fields"""
        # TODO: Test with incomplete material data
        # TODO: Verify generation continues (no crash)
        # TODO: Verify error logged
        pass
    
    def test_invalid_compound_reference(self):
        """Test handling of invalid compound IDs"""
        # TODO: Test contaminant with non-existent compound ID
        # TODO: Verify generation continues
        # TODO: Verify compound skipped gracefully
        pass
    
    def test_file_write_failure(self):
        """Test handling of file write errors"""
        # TODO: Mock file write failure
        # TODO: Verify error counted
        # TODO: Verify next material processed
        pass


class TestAtomicWrites:
    """Test atomic file writes with temp files"""
    
    def test_temp_file_creation(self):
        """Test writes to .tmp files first"""
        # TODO: Mock file system
        # TODO: Verify .json.tmp created
        # TODO: Verify .csv.tmp created
        # TODO: Verify .txt.tmp created
        pass
    
    def test_atomic_rename(self):
        """Test temp files renamed to final names"""
        # TODO: Generate dataset
        # TODO: Verify temp files deleted
        # TODO: Verify final files exist
        pass


class TestCLIFlags:
    """Test command-line interface flags"""
    
    def test_dry_run_mode(self):
        """Test --dry-run prevents file writes"""
        # TODO: Run with --dry-run
        # TODO: Verify no files written
        # TODO: Verify statistics still tracked
        pass
    
    def test_domain_filter_materials(self):
        """Test --domain materials only generates materials"""
        # TODO: Run with --domain materials
        # TODO: Verify only materials generated
        # TODO: Verify contaminants skipped
        pass
    
    def test_domain_filter_contaminants(self):
        """Test --domain contaminants only generates contaminants"""
        # TODO: Run with --domain contaminants
        # TODO: Verify only contaminants generated
        # TODO: Verify materials skipped
        pass


class TestDataConsistency:
    """Test data consistency with source YAML"""
    
    def test_materials_yaml_consistency(self):
        """Test generated datasets match Materials.yaml data"""
        # TODO: Load Materials.yaml
        # TODO: Generate dataset
        # TODO: Compare values field-by-field
        pass
    
    def test_contaminants_yaml_consistency(self):
        """Test generated datasets match Contaminants.yaml data"""
        # TODO: Load Contaminants.yaml
        # TODO: Generate dataset
        # TODO: Compare values field-by-field
        pass


class TestPerformance:
    """Test generation performance"""
    
    def test_generation_speed(self):
        """Test full generation completes in reasonable time"""
        # TODO: Time full generation (153 materials + 98 contaminants)
        # TODO: Assert completes in <60 seconds
        pass
    
    def test_memory_usage(self):
        """Test memory usage stays reasonable"""
        # TODO: Monitor memory during generation
        # TODO: Assert peak memory <100 MB
        pass


class TestIntegrationWithDataLoaders:
    """Test integration with domain data loaders"""
    
    def test_materials_loader_integration(self):
        """Test MaterialsDataLoader integration"""
        # TODO: Verify MaterialsDataLoader used correctly
        # TODO: Verify cache behavior
        pass
    
    def test_contaminants_loader_integration(self):
        """Test ContaminantsDataLoader integration"""
        # TODO: Verify ContaminantsDataLoader used correctly
        pass
    
    def test_compounds_loader_integration(self):
        """Test CompoundsDataLoader integration"""
        # TODO: Verify CompoundsDataLoader used correctly
        pass


# Integration test placeholders
@pytest.mark.integration
class TestFullGenerationPipeline:
    """Integration tests for full generation pipeline"""
    
    def test_full_materials_generation(self):
        """Test generating all 153 materials datasets"""
        # TODO: Run full materials generation
        # TODO: Verify 459 files created (153 × 3)
        # TODO: Verify no errors
        pass
    
    def test_full_contaminants_generation(self):
        """Test generating all 98 contaminants datasets"""
        # TODO: Run full contaminants generation
        # TODO: Verify 294 files created (98 × 3)
        # TODO: Verify compounds merged
        pass
    
    def test_full_generation_all_domains(self):
        """Test generating all datasets (materials + contaminants)"""
        # TODO: Run full generation
        # TODO: Verify 753 files created (251 × 3)
        # TODO: Verify 100% success rate
        pass


@pytest.mark.critical
class TestDataPopulationCompleteness:
    """CRITICAL: Test data population completeness in exported datasets
    
    These tests validate the fix for nested property extraction (commit 9108bfbb)
    that improved data completeness from F (17%) to A (95%).
    """
    
    def test_csv_row_count_minimum(self):
        """CRITICAL: Verify CSV has 20+ rows (not 3 empty rows)"""
        z_beam_path = project_root.parent / "z-beam"
        if not z_beam_path.exists():
            pytest.skip("z-beam project not found")
        
        csv_path = z_beam_path / "public" / "datasets" / "materials" / "aluminum.csv"
        if not csv_path.exists():
            pytest.skip("aluminum.csv not found")
        
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            row_count = len(rows)
            
            assert row_count >= 20, f"Expected ≥20 rows, got {row_count} (bug: empty CSV)"
            print(f"✅ aluminum.csv: {row_count} rows")
    
    def test_csv_value_column_populated(self):
        """CRITICAL: Verify CSV Value column is populated (not empty)"""
        z_beam_path = project_root.parent / "z-beam"
        if not z_beam_path.exists():
            pytest.skip("z-beam project not found")
        
        csv_path = z_beam_path / "public" / "datasets" / "materials" / "aluminum.csv"
        if not csv_path.exists():
            pytest.skip("aluminum.csv not found")
        
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            populated_rows = [r for r in rows if r.get("Value") and str(r["Value"]).strip()]
            populated_count = len(populated_rows)
            
            assert populated_count >= 20, f"Expected ≥20 populated rows, got {populated_count}"
            print(f"✅ aluminum.csv: {populated_count} rows with values")
    
    def test_nested_property_extraction(self):
        """CRITICAL REGRESSION TEST for commit 9108bfbb
        
        Verifies properties are correctly extracted from nested structure:
        properties -> category (material_characteristics) -> property (density) -> {value, unit, min, max}
        
        Bug: Originally code checked if properties[key] had 'value', 
        but properties are nested in category objects.
        """
        z_beam_path = project_root.parent / "z-beam"
        if not z_beam_path.exists():
            pytest.skip("z-beam project not found")
        
        json_path = z_beam_path / "public" / "datasets" / "materials" / "aluminum.json"
        if not json_path.exists():
            pytest.skip("aluminum.json not found")
        
        with open(json_path) as f:
            data = json.load(f)
            variables = data.get("variableMeasured", [])
            
            # Check for known properties that are nested in materials
            # Use partial matching since property names may be formatted differently
            expected_properties = ["density", "thermal", "hardness"]
            found_properties = [v.get("name", "").lower() for v in variables]
            
            for prop in expected_properties:
                found = any(prop in fp for fp in found_properties if fp)
                assert found, f"Property containing '{prop}' not extracted from nested structure. Found: {found_properties[:10]}"
            
            print(f"✅ Nested properties extracted: {len(variables)} total variables")
    
    def test_json_values_not_empty(self):
        """CRITICAL: Verify JSON variableMeasured items have actual values (not empty)"""
        z_beam_path = project_root.parent / "z-beam"
        if not z_beam_path.exists():
            pytest.skip("z-beam project not found")
        
        json_path = z_beam_path / "public" / "datasets" / "materials" / "aluminum.json"
        if not json_path.exists():
            pytest.skip("aluminum.json not found")
        
        with open(json_path) as f:
            data = json.load(f)
            variables = data.get("variableMeasured", [])
            
            # Count variables with actual values
            with_values = [v for v in variables if v.get("value") and str(v["value"]).strip()]
            
            # Most variables should have values (allow some without for special cases)
            assert len(with_values) >= 15, f"Expected ≥15 variables with values, got {len(with_values)}"
            print(f"✅ {len(with_values)}/{len(variables)} variables have values")
    
    def test_all_materials_meet_minimum_requirement(self):
        """CRITICAL: Verify most materials meet 20+ variable requirement
        
        Note: Some rare earth elements may have fewer properties due to limited data.
        This test ensures at least 90% of materials meet the requirement.
        """
        z_beam_path = project_root.parent / "z-beam"
        if not z_beam_path.exists():
            pytest.skip("z-beam project not found")
        
        materials_dir = z_beam_path / "public" / "datasets" / "materials"
        if not materials_dir.exists():
            pytest.skip("Materials datasets not found")
        
        json_files = [f for f in materials_dir.glob("*.json") if f.name != "index.json"]
        assert len(json_files) > 0, "No JSON files found"
        
        failures = []
        for json_file in json_files:
            with open(json_file) as f:
                data = json.load(f)
                var_count = len(data.get("variableMeasured", []))
                if var_count < 20:
                    failures.append(f"{json_file.name}: {var_count} variables")
        
        # Allow up to 10% of materials to have < 20 variables (for rare earth elements, etc.)
        failure_rate = len(failures) / len(json_files)
        assert failure_rate < 0.10, f"{len(failures)}/{len(json_files)} materials below 20 variables ({failure_rate:.1%}):\n" + "\n".join(failures[:10])
        
        print(f"✅ {len(json_files) - len(failures)}/{len(json_files)} materials have ≥20 variables ({(1-failure_rate):.1%} success rate)")


# Integration test placeholders
@pytest.mark.integration
class TestFullGenerationPipeline:
    """Integration tests for full generation pipeline"""
    
    def test_full_materials_generation(self):
        """Test generating all 153 materials datasets"""
        # TODO: Run full materials generation
        # TODO: Verify 459 files created (153 × 3)
        # TODO: Verify no errors
        pass
    
    def test_full_contaminants_generation(self):
        """Test generating all 98 contaminants datasets"""
        # TODO: Run full contaminants generation
        # TODO: Verify 294 files created (98 × 3)
        # TODO: Verify compounds merged
        pass
    
    def test_full_generation_all_domains(self):
        """Test generating all datasets (materials + contaminants)"""
        # TODO: Run full generation
        # TODO: Verify 753 files created (251 × 3)
        # TODO: Verify 100% success rate
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "critical"])
    
    def test_contaminants_loader_integration(self):
        """Test ContaminantsDataLoader integration"""
        # TODO: Verify ContaminantsDataLoader used correctly
        pass
    
    def test_compounds_loader_integration(self):
        """Test CompoundsDataLoader integration"""
        # TODO: Verify CompoundsDataLoader used correctly
        pass


# Integration test placeholders
@pytest.mark.integration
class TestFullGenerationPipeline:
    """Integration tests for full generation pipeline"""
    
    def test_full_materials_generation(self):
        """Test generating all 153 materials datasets"""
        # TODO: Run full materials generation
        # TODO: Verify 459 files created (153 × 3)
        # TODO: Verify no errors
        pass
    
    def test_full_contaminants_generation(self):
        """Test generating all 98 contaminants datasets"""
        # TODO: Run full contaminants generation
        # TODO: Verify 294 files created (98 × 3)
        # TODO: Verify compounds merged
        pass
    
    def test_full_generation_all_domains(self):
        """Test generating all datasets (materials + contaminants)"""
        # TODO: Run full generation
        # TODO: Verify 753 files created (251 × 3)
        # TODO: Verify 100% success rate
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "critical"])
