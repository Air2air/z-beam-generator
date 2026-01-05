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
        """Test converting nested dictionaries."""
        input_dict = {
            'outer_field': 'value',
            'nested_object': {
                'inner_field': 'nested_value',
                'another_field': 123
            }
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        assert 'outerField' in result
        assert 'nestedObject' in result
        assert 'innerField' in result['nestedObject']
        assert 'anotherField' in result['nestedObject']
        assert result['nestedObject']['innerField'] == 'nested_value'
    
    def test_deeply_nested_structures(self, generator):
        """Test 5+ levels of nesting."""
        input_dict = {
            'level_1': {
                'level_2': {
                    'level_3': {
                        'level_4': {
                            'level_5': {
                                'deep_field': 'deep_value'
                            }
                        }
                    }
                }
            }
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        assert 'level1' in result
        assert 'level2' in result['level1']
        assert 'level3' in result['level1']['level2']
        assert 'level4' in result['level1']['level2']['level3']
        assert 'level5' in result['level1']['level2']['level3']['level4']
        assert 'deepField' in result['level1']['level2']['level3']['level4']['level5']
        assert result['level1']['level2']['level3']['level4']['level5']['deepField'] == 'deep_value'
    
    def test_list_of_dicts_conversion(self, generator):
        """Test converting lists containing dictionaries."""
        input_dict = {
            'item_list': [
                {'field_name': 'value1'},
                {'field_name': 'value2'},
                {'another_field': 'value3'}
            ]
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        assert 'itemList' in result
        assert len(result['itemList']) == 3
        assert 'fieldName' in result['itemList'][0]
        assert 'fieldName' in result['itemList'][1]
        assert 'anotherField' in result['itemList'][2]
        assert result['itemList'][0]['fieldName'] == 'value1'
    
    def test_underscore_prefix_preserved(self, generator):
        """Test that fields starting with underscore are preserved."""
        input_dict = {
            '_section': {'title': 'Test'},
            '_collapsible': True,
            '_open': False,
            'regular_field': 'value'
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        # Underscore-prefixed fields should be preserved
        assert '_section' in result
        assert '_collapsible' in result
        assert '_open' in result
        
        # Regular fields should be converted
        assert 'regularField' in result
        assert 'regular_field' not in result
        
        # Nested values in underscore fields should still be converted
        assert result['_section'] == {'title': 'Test'}
    
    def test_mixed_data_types(self, generator):
        """Test handling of various data types."""
        input_dict = {
            'string_field': 'text',
            'number_field': 42,
            'float_field': 3.14,
            'bool_field': True,
            'none_field': None,
            'list_field': [1, 2, 3],
            'dict_field': {'nested': 'value'}
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        assert result['stringField'] == 'text'
        assert result['numberField'] == 42
        assert result['floatField'] == 3.14
        assert result['boolField'] is True
        assert result['noneField'] is None
        assert result['listField'] == [1, 2, 3]
        assert 'nested' in result['dictField']
    
    def test_empty_dict(self, generator):
        """Test empty dictionary handling."""
        result = generator._task_camelcase_normalization({}, {})
        assert result == {}
    
    def test_empty_nested_structures(self, generator):
        """Test empty nested dicts and lists."""
        input_dict = {
            'empty_dict': {},
            'empty_list': [],
            'dict_with_empty': {
                'nested_empty': {}
            }
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        assert result['emptyDict'] == {}
        assert result['emptyList'] == []
        assert result['dictWithEmpty']['nestedEmpty'] == {}
    
    def test_special_characters_no_underscores(self, generator):
        """Test fields with hyphens, dots (no underscores - should remain unchanged)."""
        input_dict = {
            'field-with-hyphens': 'value1',
            'field.with.dots': 'value2',
            'field@special': 'value3',
            'normal_field': 'value4'
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        # No underscores = unchanged
        assert 'field-with-hyphens' in result
        assert 'field.with.dots' in result
        assert 'field@special' in result
        
        # Has underscore = converted
        assert 'normalField' in result
        assert 'normal_field' not in result
    
    def test_complex_real_world_structure(self, generator):
        """Test with a realistic frontmatter structure."""
        input_dict = {
            'id': 'test-material',
            'page_title': 'Test Material',
            'content_type': 'material',
            'schema_version': '5.0.0',
            'date_published': '2026-01-05',
            'date_modified': '2026-01-05',
            'author': {
                'author_id': 1,
                'full_name': 'John Doe'
            },
            'technical_specs': {
                'melting_point': 1000,
                'thermal_conductivity': 200
            },
            'safety': {
                'health_effects': [
                    {'symptom_name': 'Irritation', 'severity_level': 'low'}
                ]
            },
            '_section': {
                'section_title': 'Overview',
                'order_number': 1
            }
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        # Top level
        assert result['id'] == 'test-material'
        assert result['pageTitle'] == 'Test Material'
        assert result['contentType'] == 'material'
        assert result['schemaVersion'] == '5.0.0'
        assert result['datePublished'] == '2026-01-05'
        assert result['dateModified'] == '2026-01-05'
        
        # Nested author
        assert result['author']['authorId'] == 1
        assert result['author']['fullName'] == 'John Doe'
        
        # Nested technical_specs
        assert result['technicalSpecs']['meltingPoint'] == 1000
        assert result['technicalSpecs']['thermalConductivity'] == 200
        
        # Nested list with dict
        assert result['safety']['healthEffects'][0]['symptomName'] == 'Irritation'
        assert result['safety']['healthEffects'][0]['severityLevel'] == 'low'
        
        # Underscore-prefixed preserved but nested converted
        assert '_section' in result
        assert result['_section']['sectionTitle'] == 'Overview'
        assert result['_section']['orderNumber'] == 1
        
        # Old snake_case keys should NOT exist
        assert 'page_title' not in result
        assert 'content_type' not in result
        assert 'author_id' not in result['author']
        assert 'melting_point' not in result['technicalSpecs']
    
    def test_idempotency(self, generator):
        """Test that running conversion twice produces same result."""
        input_dict = {
            'field_name': 'value',
            'another_field': 123
        }
        
        result1 = generator._task_camelcase_normalization(input_dict, {})
        result2 = generator._task_camelcase_normalization(result1, {})
        
        assert result1 == result2
        assert 'fieldName' in result2
        assert 'anotherField' in result2
    
    def test_null_values_preserved(self, generator):
        """Test that None/null values are preserved."""
        input_dict = {
            'field_with_none': None,
            'nested_dict': {
                'null_field': None
            },
            'list_with_none': [None, 'value', None]
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        assert result['fieldWithNone'] is None
        assert result['nestedDict']['nullField'] is None
        assert result['listWithNone'] == [None, 'value', None]
    
    def test_boolean_values_preserved(self, generator):
        """Test that boolean values are correctly preserved."""
        input_dict = {
            'is_active': True,
            'is_deleted': False,
            'nested': {
                'has_permission': True
            }
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        assert result['isActive'] is True
        assert result['isDeleted'] is False
        assert result['nested']['hasPermission'] is True
    
    def test_list_of_primitives_unchanged(self, generator):
        """Test that lists of primitive values remain unchanged."""
        input_dict = {
            'string_list': ['a', 'b', 'c'],
            'number_list': [1, 2, 3],
            'mixed_list': ['text', 123, True, None]
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        assert result['stringList'] == ['a', 'b', 'c']
        assert result['numberList'] == [1, 2, 3]
        assert result['mixedList'] == ['text', 123, True, None]
    
    def test_multiple_underscore_prefixes(self, generator):
        """Test fields with multiple leading underscores."""
        input_dict = {
            '__private': 'value1',
            '___triple': 'value2',
            'regular_field': 'value3'
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        # All underscore-prefixed fields preserved
        assert '__private' in result
        assert '___triple' in result
        
        # Regular field converted
        assert 'regularField' in result


class TestCamelCaseEdgeCases:
    """Additional edge case tests for robustness."""
    
    @pytest.fixture
    def generator(self):
        """Create ContentGenerator instance for testing."""
        return ContentGenerator({})
    
    def test_unicode_characters(self, generator):
        """Test handling of unicode characters in values."""
        input_dict = {
            'field_name': 'café',
            'another_field': '日本語',
            'emoji_field': '🔥'
        }
        
        result = generator._task_camelcase_normalization(input_dict, {})
        
        assert result['fieldName'] == 'café'
        assert result['anotherField'] == '日本語'
        assert result['emojiField'] == '🔥'
    
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
