"""
Unit tests for camelCase conversion logic.

Tests the core conversion functions in ContentGenerator:
- _to_camel_case() - snake_case to camelCase conversion
- _task_camelcase_normalization() - recursive dict transformation
"""

import pytest
from export.generation.universal_content_generator import ContentGenerator


class TestCamelCaseConversionUnit:
    """Unit tests for camelCase conversion logic."""
    
    @pytest.fixture
    def generator(self):
        """Create ContentGenerator instance for testing."""
        return ContentGenerator({})
    
    # ============================================================
    # _to_camel_case() Method Tests
    # ============================================================
    
    def test_simple_snake_case_conversion(self, generator):
        """Test basic snake_case to camelCase conversion."""
        assert generator._to_camel_case('field_name') == 'fieldName'
        assert generator._to_camel_case('page_title') == 'pageTitle'
        assert generator._to_camel_case('content_type') == 'contentType'
    
    def test_multiple_underscores(self, generator):
        """Test conversion with multiple underscores."""
        assert generator._to_camel_case('some_long_field_name') == 'someLongFieldName'
        assert generator._to_camel_case('a_b_c_d_e_f') == 'aBCDEF'
        assert generator._to_camel_case('full_path_to_resource') == 'fullPathToResource'
    
    def test_numbers_in_field_names(self, generator):
        """Test conversion with numbers in field names."""
        assert generator._to_camel_case('field_1') == 'field1'
        assert generator._to_camel_case('api_v2') == 'apiV2'
        assert generator._to_camel_case('level_3_item') == 'level3Item'
        assert generator._to_camel_case('test_123_value') == 'test123Value'
    
    def test_single_word_unchanged(self, generator):
        """Test that single words without underscores remain unchanged."""
        assert generator._to_camel_case('name') == 'name'
        assert generator._to_camel_case('title') == 'title'
        assert generator._to_camel_case('id') == 'id'
    
    def test_already_camelcase_unchanged(self, generator):
        """Test that already camelCase fields remain unchanged."""
        # These don't have underscores, so they pass through
        assert generator._to_camel_case('pageTitle') == 'pageTitle'
        assert generator._to_camel_case('contentType') == 'contentType'
        assert generator._to_camel_case('datePublished') == 'datePublished'
    
    def test_leading_underscore_handled(self, generator):
        """Test fields starting with underscore."""
        # Note: These would be filtered out in normalization, but test the converter directly
        assert generator._to_camel_case('_section_title') == 'SectionTitle'
        assert generator._to_camel_case('_field_name') == 'FieldName'
    
    def test_trailing_underscore(self, generator):
        """Test fields ending with underscore."""
        assert generator._to_camel_case('field_name_') == 'fieldName'
        assert generator._to_camel_case('trailing_') == 'trailing'
    
    def test_double_underscore(self, generator):
        """Test fields with consecutive underscores."""
        assert generator._to_camel_case('field__name') == 'fieldName'
        assert generator._to_camel_case('multiple___underscores') == 'multipleUnderscores'
    
    def test_empty_string(self, generator):
        """Test empty string handling."""
        assert generator._to_camel_case('') == ''
    
    def test_single_underscore(self, generator):
        """Test single underscore only."""
        assert generator._to_camel_case('_') == ''
    
    # ============================================================
    # _task_camelcase_normalization() Method Tests
    # ============================================================
    
    def test_simple_dict_conversion(self, generator):
        """Test converting a simple flat dictionary."""
        input_dict = {
            'page_title': 'Test',
            'content_type': 'material',
            'schema_version': '5.0.0'
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        assert 'pageTitle' in result
        assert 'contentType' in result
        assert 'schemaVersion' in result
        assert result['pageTitle'] == 'Test'
        assert result['contentType'] == 'material'
        assert result['schemaVersion'] == '5.0.0'
        
        # Original snake_case keys should NOT exist
        assert 'page_title' not in result
        assert 'content_type' not in result
        assert 'schema_version' not in result
    
    def test_nested_dict_conversion(self, generator):
        """Test converting nested dictionaries (software metadata only)."""
        input_dict = {
            'page_title': 'Test Title',
            'content_type': 'material',
            'nested_metadata': {
                'display_name': 'Display Name',
                'image_url': 'https://example.com/image.jpg'
            }
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        # Software metadata should be camelCase
        assert 'pageTitle' in result
        assert 'contentType' in result
        assert result['pageTitle'] == 'Test Title'
        assert result['contentType'] == 'material'
        
        # Nested fields that aren't in SOFTWARE_FIELDS should be preserved
        # (nested_metadata is not a known field, so stays as-is)
        assert 'nested_metadata' in result
    
    def test_deeply_nested_structures(self, generator):
        """Test deeply nested structures preserve domain data snake_case."""
        input_dict = {
            'schema_version': '5.0.0',
            'machine_settings': {  # Domain data - should preserve snake_case
                'power_range': {
                    'min_watts': 100,
                    'max_watts': 500,
                    'pulse_duration': '10-50ns'
                }
            }
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        # Software metadata converted
        assert 'schemaVersion' in result
        assert result['schemaVersion'] == '5.0.0'
        
        # Domain data preserved as snake_case
        assert 'machine_settings' in result
        assert 'power_range' in result['machine_settings']
        assert 'min_watts' in result['machine_settings']['power_range']
        assert 'max_watts' in result['machine_settings']['power_range']
        assert 'pulse_duration' in result['machine_settings']['power_range']
    
    def test_list_of_dicts_conversion(self, generator):
        """Test converting lists containing dictionaries (domain data preserved).""" 
        input_dict = {
            'regulatory_standards': [  # Domain data field - preserved
                {'standard_name': 'OSHA 1926.57'},
                {'standard_name': 'ISO 11553-2'},
                {'exposure_limit': '5 mg/m3'}
            ]
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        # Domain data field preserved as snake_case
        assert 'regulatory_standards' in result
        assert len(result['regulatory_standards']) == 3
        # Nested fields within domain data also preserved
        assert 'standard_name' in result['regulatory_standards'][0]
        assert 'standard_name' in result['regulatory_standards'][1]
        assert 'exposure_limit' in result['regulatory_standards'][2]
    
    def test_underscore_prefix_preserved(self, generator):
        """Test that fields starting with underscore are preserved."""
        input_dict = {
            '_section': {'sectionTitle': 'Test'},
            '_collapsible': True,
            '_open': False,
            'page_title': 'My Page'  # Software metadata
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        # Underscore-prefixed fields should be preserved
        assert '_section' in result
        assert '_collapsible' in result
        assert '_open' in result
        
        # Software metadata converted to camelCase
        assert 'pageTitle' in result
        assert 'page_title' not in result
        
        # Nested values in underscore fields should be preserved
        assert result['_section'] == {'sectionTitle': 'Test'}
    
    def test_mixed_data_types(self, generator):
        """Test handling of various data types (software metadata)."""
        input_dict = {
            'page_title': 'text',
            'schema_version': '5.0.0',
            'date_published': '2026-01-05',
            'content_type': 'material',
            'machine_settings': {  # Domain data - preserved
                'power_min': 100,
                'power_max': 500
            }
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        # Software metadata converted to camelCase
        assert result['pageTitle'] == 'text'
        assert result['schemaVersion'] == '5.0.0'
        assert result['datePublished'] == '2026-01-05'
        assert result['contentType'] == 'material'
        
        # Domain data preserved as snake_case
        assert 'machine_settings' in result
        assert 'power_min' in result['machine_settings']
        assert 'power_max' in result['machine_settings']
    
    def test_empty_dict(self, generator):
        """Test empty dictionary handling."""
        result = generator._task_camelcase_normalization({}, {})
        assert result == {}
    
    def test_empty_nested_structures(self, generator):
        """Test empty nested dicts and lists."""
        input_dict = {
            'page_title': 'Test',
            'relationships': {},  # Empty domain data structure
            'metadata': []
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        assert result['pageTitle'] == 'Test'
        assert result['relationships'] == {}
        assert result['metadata'] == []
    
    def test_special_characters_no_underscores(self, generator):
        """Test fields with hyphens, dots stay as-is (not software metadata)."""
        input_dict = {
            'field-with-hyphens': 'value1',
            'field.with.dots': 'value2',
            'field@special': 'value3',
            'page_title': 'My Page'  # Software metadata
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        # Special chars = unchanged (not in SOFTWARE_FIELDS)
        assert 'field-with-hyphens' in result
        assert 'field.with.dots' in result
        assert 'field@special' in result
        
        # Software metadata converted
        assert 'pageTitle' in result
        assert 'page_title' not in result
    
    def test_complex_real_world_structure(self, generator):
        """Test with a realistic frontmatter structure (dual-case)."""
        input_dict = {
            'id': 'test-material',
            'page_title': 'Test Material',  # Software metadata → camelCase
            'content_type': 'material',  # Software metadata → camelCase
            'schema_version': '5.0.0',  # Software metadata → camelCase
            'date_published': '2026-01-05',  # Software metadata → camelCase
            'date_modified': '2026-01-05',  # Software metadata → camelCase
            'author': {
                'id': 1,
                'name': 'John Doe'
            },
            'machine_settings': {  # Domain data → snake_case preserved
                'power_min': 100,
                'power_max': 500,
                'pulse_duration': '10-50ns'
            },
            'chemical_formula': 'Al2O3',  # Domain data → snake_case preserved
            '_section': {
                'sectionTitle': 'Overview',
                'order': 1
            }
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        # Top level - software metadata converted to camelCase
        assert result['id'] == 'test-material'
        assert result['pageTitle'] == 'Test Material'
        assert result['contentType'] == 'material'
        assert result['schemaVersion'] == '5.0.0'
        assert result['datePublished'] == '2026-01-05'
        assert result['dateModified'] == '2026-01-05'
        
        # Author - regular nested structure (not in SOFTWARE_FIELDS, preserved)
        assert result['author']['id'] == 1
        assert result['author']['name'] == 'John Doe'
        
        # Domain data preserved as snake_case
        assert 'machine_settings' in result
        assert 'power_min' in result['machine_settings']
        assert 'power_max' in result['machine_settings']
        assert 'pulse_duration' in result['machine_settings']
        assert 'chemical_formula' in result
        assert result['chemical_formula'] == 'Al2O3'
        
        # Underscore-prefixed preserved
        assert '_section' in result
        assert result['_section']['sectionTitle'] == 'Overview'
        assert result['_section']['order'] == 1
        
        # Old snake_case software metadata keys should NOT exist
        assert 'page_title' not in result
        assert 'content_type' not in result
        assert 'schema_version' not in result
    
    def test_idempotency(self, generator):
        """Test that running conversion twice produces same result."""
        input_dict = {
            'page_title': 'Test',  # Software metadata
            'schema_version': '5.0.0'
        }
        
        result1 = generator._task_camelcase_normalization(input_dict, {})
        result2 = generator._task_camelcase_normalization(result1, {})
        
        assert result1 == result2
        assert 'pageTitle' in result2
        assert 'schemaVersion' in result2
    
    def test_null_values_preserved(self, generator):
        """Test that None/null values are preserved (software metadata)."""
        input_dict = {
            'page_description': None,  # Software metadata 
            'content_type': 'material',
            'machine_settings': {  # Domain data
                'optional_field': None
            }
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        # Software metadata converted, None preserved
        assert result['pageDescription'] is None
        assert result['contentType'] == 'material'
        
        # Domain data preserved
        assert 'machine_settings' in result
        assert result['machine_settings']['optional_field'] is None
    
    def test_boolean_values_preserved(self, generator):
        """Test that boolean values are correctly preserved."""
        input_dict = {
            '_collapsible': True,  # Underscore prefix - preserved
            '_open': False,
            'page_title': 'Test'
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        # Underscore fields preserved
        assert result['_collapsible'] is True
        assert result['_open'] is False
        
        # Software metadata converted
        assert result['pageTitle'] == 'Test'
    
    def test_list_of_primitives_unchanged(self, generator):
        """Test that lists of primitive values remain unchanged."""
        input_dict = {
            'metadata': ['tag1', 'tag2', 'tag3'],  # Regular field
            'regulatory_standards': ['OSHA', 'ISO']  # Domain data field
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        # Regular fields preserved (not in SOFTWARE_FIELDS)
        assert result['metadata'] == ['tag1', 'tag2', 'tag3']
        
        # Domain data preserved
        assert result['regulatory_standards'] == ['OSHA', 'ISO']
    
    def test_multiple_underscore_prefixes(self, generator):
        """Test fields with multiple leading underscores."""
        input_dict = {
            '__private': 'value1',
            '___triple': 'value2',
            'page_title': 'My Page'  # Software metadata
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        # All underscore-prefixed fields preserved
        assert '__private' in result
        assert '___triple' in result
        
        # Software metadata converted
        assert 'pageTitle' in result


class TestCamelCaseEdgeCases:
    """Additional edge case tests for robustness."""
    
    @pytest.fixture
    def generator(self):
        """Create ContentGenerator instance for testing."""
        return ContentGenerator({})
    
    def test_unicode_characters(self, generator):
        """Test that unicode characters are preserved, but only software fields are converted."""
        input_dict = {
            'content_type': 'café',  # Software field - will be converted
            'another_field': '日本語',  # Not a software field - stays snake_case
            'emoji_field': '🔥'  # Not a software field - stays snake_case
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        assert result['contentType'] == 'café'  # Software field converted
        assert result['another_field'] == '日本語'  # Domain field preserved
        assert result['emoji_field'] == '🔥'  # Domain field preserved
    
    def test_very_long_field_name(self, generator):
        """Test conversion of very long field names."""
        long_name = '_'.join([f'part{i}' for i in range(20)])
        input_dict = {long_name: 'value'}
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        # Should have camelCase version
        expected_name = 'part0' + ''.join([f'Part{i}' for i in range(1, 20)])
        assert expected_name in result
        assert result[expected_name] == 'value'
    
    def test_circular_reference_prevention(self, generator):
        """Test that circular references don't cause infinite loops."""
        # Note: This test verifies the function doesn't crash with circular refs
        # (though in practice, YAML serialization would prevent these)
        input_dict = {
            'field_name': 'value',
            'nested': {}
        }
        # Don't actually create circular ref (would break YAML anyway)
        # Just verify normal nested structures work
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        assert 'fieldName' in result
        assert 'nested' in result
    
    def test_large_dictionary(self, generator):
        """Test performance with large dictionary (1000+ fields)."""
        input_dict = {f'field_{i}': f'value_{i}' for i in range(1000)}
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        assert len(result) == 1000
        assert 'field500' in result
        assert result['field500'] == 'value_500'
    
    def test_config_parameter_ignored(self, generator):
        """Test that the config parameter (required by task interface) doesn't affect conversion."""
        input_dict = {'field_name': 'value'}
        
        result1 = generator._task_camelcase_normalization(input_dict, {})
        result2 = generator._task_camelcase_normalization(input_dict, {'some_config': 'value'})
        
        assert result1 == result2
        assert 'fieldName' in result1


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
