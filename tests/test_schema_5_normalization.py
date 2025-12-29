"""
Tests for Schema 5.0.0 Normalization Script

Tests the frontmatter structure migration from nested relationships (4.0.0)
to flattened top-level arrays (5.0.0).

Test Coverage:
- YAML loading with OrderedDict support
- Domain linkages flattening (8 linkage types)
- Duplicate field removal (name field)
- Field reordering per canonical specification
- Schema version update
- Dry-run mode
- Error handling

File: tests/test_schema_5_normalization.py
"""

import pytest
import yaml
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, mock_open
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from normalize_frontmatter_structure import (
    flatten_relationships,
    remove_duplicate_fields,
    reorder_fields,
    update_schema_version,
    normalize_file,
    FIELD_ORDER
)
from shared.utils.file_io import read_yaml_file as load_yaml, write_yaml_file as save_yaml


class TestYAMLLoading:
    """Test YAML loading with OrderedDict support"""
    
    def test_load_yaml_standard_format_with_unsafe(self):
        """Should load standard YAML using unsafe_load (for OrderedDict support)"""
        yaml_content = """id: test-id
name: Test Name
title: Test Title
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name
        
        try:
            data = load_yaml(temp_path)
            assert data['id'] == 'test-id'
            assert data['name'] == 'Test Name'
            assert data['page_title'] == 'Test Title'
        finally:
            Path(temp_path).unlink()
    
    def test_load_yaml_standard_format(self):
        """Should load standard YAML without OrderedDict"""
        yaml_content = """
id: test-id
title: Test Title
schema_version: '4.0.0'
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name
        
        try:
            data = load_yaml(temp_path)
            assert data['id'] == 'test-id'
            assert data['page_title'] == 'Test Title'
            assert data['schema_version'] == '4.0.0'
        finally:
            Path(temp_path).unlink()


class TestDomainLinkagesFlattening:
    """Test flattening of nested relationships to top-level"""
    
    def test_flatten_nested_relationships(self):
        """Should extract all linkage types from nested structure"""
        data = {
            'id': 'test-id',
            'page_title': 'Test',
            'relationships': {
                'produces_compounds': [{'id': 'compound-1'}],
                'related_materials': [{'id': 'material-1'}],
                'related_contaminants': [{'id': 'contaminant-1'}],
                'removes_contaminants': [{'id': 'removes-1'}],
                'found_in_materials': [{'id': 'found-1'}],
                'effective_against': [{'id': 'effective-1'}],
                'related_settings': [{'id': 'setting-1'}],
                'related_compounds': [{'id': 'compound-2'}]
            }
        }
        
        result = flatten_relationships(data)
        
        # Should have all 8 linkage types at top level (matching normalize script)
        assert 'produces_compounds' in result
        assert 'related_materials' in result
        assert 'related_contaminants' in result
        assert 'removes_contaminants' in result
        assert 'found_in_materials' in result
        assert 'effective_against' in result
        assert 'related_settings' in result
        assert 'related_compounds' in result
        
        # Should remove relationships key
        assert 'relationships' not in result
        
        # Data should be preserved
        assert result['produces_compounds'] == [{'id': 'compound-1'}]
        assert result['related_materials'] == [{'id': 'material-1'}]
    
    def test_flatten_partial_relationships(self):
        """Should handle relationships with only some linkage types"""
        data = {
            'id': 'test-id',
            'relationships': {
                'produces_compounds': [{'id': 'compound-1'}],
                'related_materials': [{'id': 'material-1'}]
                # Only 2 out of 8 linkage types
            }
        }
        
        result = flatten_relationships(data)
        
        assert 'produces_compounds' in result
        assert 'related_materials' in result
        assert 'relationships' not in result
        assert len(result['produces_compounds']) == 1
    
    def test_flatten_no_relationships(self):
        """Should return unchanged if no relationships"""
        data = {
            'id': 'test-id',
            'page_title': 'Test',
            'produces_compounds': [{'id': 'compound-1'}]  # Already flat
        }
        
        result = flatten_relationships(data)
        
        assert result == data
        assert 'produces_compounds' in result
    
    def test_flatten_empty_relationships(self):
        """Should handle empty relationships object"""
        data = {
            'id': 'test-id',
            'relationships': {}
        }
        
        result = flatten_relationships(data)
        
        assert 'relationships' not in result
        assert result['id'] == 'test-id'


class TestDuplicateFieldRemoval:
    """Test removal of duplicate 'name' field"""
    
    def test_remove_name_when_title_exists(self):
        """Should remove 'name' field if 'page_title' exists"""
        data = {
            'id': 'test-id',
            'name': 'Test Name',
            'page_title': 'Test Title',
            'slug': 'test-slug'
        }
        
        result = remove_duplicate_fields(data)
        
        assert 'name' not in result
        assert 'page_title' in result
        assert result['page_title'] == 'Test Title'
    
    def test_keep_name_if_no_title(self):
        """Should keep 'name' if 'page_title' doesn't exist"""
        data = {
            'id': 'test-id',
            'name': 'Test Name',
            'slug': 'test-slug'
        }
        
        result = remove_duplicate_fields(data)
        
        assert 'name' in result
        assert result['name'] == 'Test Name'
    
    def test_no_name_field(self):
        """Should return unchanged if no 'name' field"""
        data = {
            'id': 'test-id',
            'page_title': 'Test Title'
        }
        
        result = remove_duplicate_fields(data)
        
        assert result == data


class TestFieldReordering:
    """Test field reordering per canonical specification"""
    
    def test_reorder_to_canonical_order(self):
        """Should reorder fields according to FIELD_ORDER"""
        data = {
            'author': {'id': 'author-1'},
            'id': 'test-id',
            'schema_version': '5.0.0',
            'page_title': 'Test Title',
            'slug': 'test-slug',
            'category': 'test-category'
        }
        
        result = reorder_fields(data)
        keys = list(result.keys())
        
        # First 6 fields should be in canonical order
        assert keys[0] == 'id'
        assert keys[1] == 'page_title'
        assert keys[2] == 'slug'
        assert keys[3] == 'category'
        assert keys[4] == 'schema_version'
        # author comes later in FIELD_ORDER
        assert 'author' in keys
    
    def test_unknown_fields_at_end(self):
        """Should place unknown fields at end"""
        data = {
            'id': 'test-id',
            'unknown_field': 'value',
            'page_title': 'Test Title',
            'another_unknown': 'value2'
        }
        
        result = reorder_fields(data)
        keys = list(result.keys())
        
        assert keys[0] == 'id'
        assert keys[1] == 'page_title'
        # Unknown fields at end
        assert 'unknown_field' in keys[2:]
        assert 'another_unknown' in keys[2:]
    
    def test_preserve_all_fields(self):
        """Should preserve all fields during reordering"""
        data = {
            'field1': 'value1',
            'field2': 'value2',
            'id': 'test-id',
            'field3': 'value3'
        }
        
        result = reorder_fields(data)
        
        assert len(result) == len(data)
        assert all(k in result for k in data.keys())
        assert all(result[k] == data[k] for k in data.keys())


class TestSchemaVersionUpdate:
    """Test schema version update to 5.0.0"""
    
    def test_update_to_5_0_0(self):
        """Should update schema_version to '5.0.0'"""
        data = {
            'id': 'test-id',
            'schema_version': '4.0.0'
        }
        
        result = update_schema_version(data)
        
        assert result['schema_version'] == '5.0.0'
    
    def test_add_schema_version_if_missing(self):
        """Should add schema_version if not present"""
        data = {
            'id': 'test-id',
            'page_title': 'Test'
        }
        
        result = update_schema_version(data)
        
        assert 'schema_version' in result
        assert result['schema_version'] == '5.0.0'


class TestNormalizeFile:
    """Test complete file normalization"""
    
    def test_normalize_4_0_to_5_0(self):
        """Should normalize complete 4.0.0 file to 5.0.0"""
        # Create temp file with 4.0.0 structure
        yaml_content = """id: test-contaminant
name: Test Contaminant
title: Test Contaminant Title
slug: test-contaminant
category: organic-residue
schema_version: '4.0.0'
relationships:
  produces_compounds:
    - id: compound-1
      title: Compound 1
  related_materials:
    - id: material-1
      title: Material 1
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name
        
        try:
            # Normalize file (script expects Path object)
            result = normalize_file(Path(temp_path), dry_run=False)
            
            assert result['success'] is True
            assert len(result['changes']) > 0  # Should have changes
            
            # Load and verify
            data = load_yaml(Path(temp_path))
            
            # Should be 5.0.0
            assert data['schema_version'] == '5.0.0'
            
            # Should be flattened
            assert 'relationships' not in data
            assert 'produces_compounds' in data
            assert 'related_materials' in data
            
            # Should have removed duplicate name
            assert 'name' not in data
            assert 'page_title' in data
            
            # Should be reordered (id first)
            keys = list(data.keys())
            assert keys[0] == 'id'
            
        finally:
            Path(temp_path).unlink()
    
    def test_normalize_already_5_0(self):
        """Should return False for already normalized file"""
        yaml_content = """id: test-id
title: Test Title
slug: test-slug
schema_version: '5.0.0'
produces_compounds:
  - id: compound-1
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name
        
        try:
            # Normalize already-normalized file (script expects Path object)
            result = normalize_file(Path(temp_path), dry_run=False)
            
            # Should return success with no changes
            assert result['success'] is True
            assert len(result['changes']) == 0  # No changes needed
            
        finally:
            Path(temp_path).unlink()
    
    def test_dry_run_no_changes(self):
        """Should not modify file in dry-run mode"""
        yaml_content = """id: test-id
schema_version: '4.0.0'
relationships:
  produces_compounds: []
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name
        
        try:
            # Dry run (script expects Path object)
            result = normalize_file(Path(temp_path), dry_run=True)
            
            assert result['success'] is True
            assert len(result['changes']) > 0  # Would change
            
            # File should be unchanged (dry-run doesn't save)
            data = load_yaml(Path(temp_path))
            assert data['schema_version'] == '4.0.0'
            assert 'relationships' in data
            
        finally:
            Path(temp_path).unlink()


class TestFieldOrderSpecification:
    """Test FIELD_ORDER specification completeness"""
    
    def test_field_order_has_required_fields(self):
        """Should contain all required fields in correct order"""
        required_first = ['id', 'page_title', 'slug', 'category', 'subcategory']
        
        for i, field in enumerate(required_first):
            assert FIELD_ORDER[i] == field
    
    def test_schema_version_position(self):
        """schema_version should come after category/subcategory"""
        assert 'schema_version' in FIELD_ORDER
        schema_idx = FIELD_ORDER.index('schema_version')
        category_idx = FIELD_ORDER.index('category')
        assert schema_idx > category_idx
    
    def test_linkages_after_content(self):
        """Domain linkages should come after content fields"""
        content_fields = ['excerpt', 'content', 'seo_description']
        linkage_fields = ['produces_compounds', 'related_materials', 'related_contaminants']
        
        for content_field in content_fields:
            if content_field in FIELD_ORDER:
                content_idx = FIELD_ORDER.index(content_field)
                for linkage in linkage_fields:
                    if linkage in FIELD_ORDER:
                        linkage_idx = FIELD_ORDER.index(linkage)
                        assert linkage_idx > content_idx


class TestIntegration:
    """Integration tests for complete normalization workflow"""
    
    def test_complete_normalization_workflow(self):
        """Should normalize directory of files"""
        # Create temp directory with test files
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # File 1: Needs normalization
            file1 = tmpdir_path / 'file1.yaml'
            file1.write_text("""id: file1
name: File 1
title: File 1 Title
schema_version: '4.0.0'
relationships:
  produces_compounds: []
""")
            
            # File 2: Already normalized
            file2 = tmpdir_path / 'file2.yaml'
            file2.write_text("""id: file2
title: File 2 Title
schema_version: '5.0.0'
produces_compounds: []
""")
            
            # File 3: Needs normalization
            file3 = tmpdir_path / 'file3.yaml'
            file3.write_text("""id: file3
name: File 3
schema_version: '4.0.0'
relationships:
  related_materials: []
""")
            
            # Normalize all files (script expects Path objects)
            changed_count = 0
            for yaml_file in tmpdir_path.glob('*.yaml'):
                result = normalize_file(yaml_file, dry_run=False)
                if result['success'] and len(result['changes']) > 0:
                    changed_count += 1
            
            # Should have changed 2 files (file1 and file3)
            assert changed_count == 2
            
            # Verify all files are now 5.0.0
            for yaml_file in tmpdir_path.glob('*.yaml'):
                data = load_yaml(yaml_file)
                assert data['schema_version'] == '5.0.0'
                assert 'relationships' not in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
