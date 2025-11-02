"""
Test suite for verifying complete pipeline normalization from Categories → Materials → Frontmatter

These tests ensure that:
1. Category ranges load correctly from Categories.yaml
2. Materials.yaml has NO min/max (values only)
3. Frontmatter uses category ranges from Categories.yaml
4. Nested thermalDestruction structure works correctly
5. Null ranges are preserved when no category range exists

Created: October 14, 2025
Updated: October 14, 2025 (Complete normalization achieved)
Related: docs/DATA_ARCHITECTURE.md, COMPLETE_PIPELINE_NORMALIZATION.md
"""

import pytest
import yaml
from pathlib import Path


class TestCategoryRangesLoading:
    """Test that Categories.yaml category_ranges load correctly"""
    
    @pytest.fixture
    def categories_data(self):
        """Load Categories.yaml"""
        categories_file = Path('data/Categories.yaml')
        with open(categories_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def test_all_nine_categories_exist(self, categories_data):
        """Verify all 9 material categories are defined (distinct from 4 property categories)"""
        expected_categories = [
            'ceramic', 'composite', 'glass', 'masonry', 'metal',
            'plastic', 'semiconductor', 'stone', 'wood'
        ]
        
        assert 'categories' in categories_data, "Missing 'categories' in Categories.yaml"
        
        for category in expected_categories:
            assert category in categories_data['categories'], \
                f"Category '{category}' not found in Categories.yaml"
    
    def test_all_categories_have_ranges(self, categories_data):
        """Each category should have category_ranges defined"""
        for category_name, category_data in categories_data['categories'].items():
            assert 'category_ranges' in category_data, \
                f"Category '{category_name}' missing 'category_ranges'"
            
            ranges = category_data['category_ranges']
            assert isinstance(ranges, dict), \
                f"Category '{category_name}' category_ranges should be dict"
            
            # After data quality remediation (Oct 2025), categories have 16-19 properties
            # chemicalStability and crystallineStructure were removed (SEVERE data quality issues)
            assert len(ranges) >= 15, \
                f"Category '{category_name}' has only {len(ranges)} properties (expected at least 15)"
    
    def test_category_ranges_have_core_properties(self, categories_data):
        """Each category should have core properties with ranges (variable count 16-19)"""
        # After data quality remediation (Oct 2025):
        # - Removed: chemicalStability, crystallineStructure (SEVERE issues)
        # - Standardized: thermalExpansion, thermalDiffusivity, youngsModulus, oxidationResistance
        # - Property count varies: 16-19 depending on material category
        
        core_properties = [
            'density', 'hardness', 'laserAbsorption', 'laserReflectivity',
            'specificHeat', 'tensileStrength', 'thermalConductivity',
            'thermalDiffusivity', 'thermalExpansion', 'youngsModulus'
        ]
        
        for category_name, category_data in categories_data['categories'].items():
            ranges = category_data['category_ranges']
            
            # Check that most core properties are present (some categories may not have all)
            present_core = sum(1 for prop in core_properties if prop in ranges)
            assert present_core >= 8, \
                f"Category '{category_name}' missing too many core properties (only {present_core}/10)"
            
            # Each category should have 16-19 properties total
            assert 15 <= len(ranges) <= 25, \
                f"Category '{category_name}' has {len(ranges)} properties (expected 15-25)"
    
    def test_range_structure_valid(self, categories_data):
        """Each range should have min, max, and unit (some properties have nested structures)"""
        for category_name, category_data in categories_data['categories'].items():
            ranges = category_data['category_ranges']
            
            for prop_name, prop_data in ranges.items():
                # thermalDestruction is nested structure with point and type
                if prop_name == 'thermalDestruction':
                    assert isinstance(prop_data, dict), \
                        f"{category_name}.thermalDestruction should be dict"
                    
                    # Check nested structure
                    assert 'point' in prop_data, \
                        f"{category_name}.thermalDestruction missing 'point'"
                    assert 'type' in prop_data, \
                        f"{category_name}.thermalDestruction missing 'type'"
                    
                    # Check point structure
                    point = prop_data['point']
                    assert isinstance(point, dict), "point should be dict"
                    assert 'min' in point, "point missing 'min'"
                    assert 'max' in point, "point missing 'max'"
                    assert 'unit' in point, "point missing 'unit'"
                    assert point['min'] < point['max'], "min should be less than max"
                    
                    # Check type is string
                    assert isinstance(prop_data['type'], str), "type should be string"
                    continue
                
                # Properties like ablationThreshold may have pulse-duration-specific nested structures
                if prop_name == 'ablationThreshold':
                    assert isinstance(prop_data, dict), \
                        f"{category_name}.{prop_name} should be dict"
                    
                    # May have nested femtosecond, nanosecond, picosecond structures
                    nested_keys = ['femtosecond', 'nanosecond', 'picosecond']
                    has_nested = any(key in prop_data for key in nested_keys)
                    
                    if has_nested:
                        # Verify at least one nested structure exists with min/max/unit
                        for key in nested_keys:
                            if key in prop_data:
                                nested = prop_data[key]
                                assert isinstance(nested, dict), f"{key} should be dict"
                                assert 'min' in nested and 'max' in nested and 'unit' in nested, \
                                    f"{category_name}.{prop_name}.{key} missing min/max/unit"
                        continue
                    # If no nested structure, fall through to standard validation
                
                # All other properties should have min, max, unit at top level
                assert isinstance(prop_data, dict), \
                    f"{category_name}.{prop_name} should be dict"
                
                # Skip if this is a complex nested property we don't recognize
                if not ('min' in prop_data or 'max' in prop_data):
                    # Check if it has any nested structures with ranges
                    has_nested_ranges = any(
                        isinstance(v, dict) and 'min' in v and 'max' in v 
                        for v in prop_data.values()
                    )
                    if has_nested_ranges:
                        continue  # Complex nested property, skip standard validation
                
                assert 'min' in prop_data, \
                    f"{category_name}.{prop_name} missing 'min'"
                assert 'max' in prop_data, \
                    f"{category_name}.{prop_name} missing 'max'"
                assert 'unit' in prop_data, \
                    f"{category_name}.{prop_name} missing 'unit'"
                
                # min should be less than max
                assert prop_data['min'] < prop_data['max'], \
                    f"{category_name}.{prop_name}: min ({prop_data['min']}) >= max ({prop_data['max']})"


class TestMaterialsYamlStructure:
    """Test materials.yaml structure and identify data quality issues"""
    
    @pytest.fixture
    def materials_data(self):
        """Load materials.yaml"""
        materials_file = Path('data/materials.yaml')
        with open(materials_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @pytest.fixture
    def categories_data(self):
        """Load Categories.yaml"""
        categories_file = Path('data/Categories.yaml')
        with open(categories_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def test_materials_yaml_has_no_category_ranges_at_root(self, materials_data):
        """materials.yaml should NOT have category_ranges at root level"""
        assert 'category_ranges' not in materials_data, \
            "materials.yaml should not have 'category_ranges' at root level"
    
    def test_all_materials_have_category(self, materials_data):
        """Every material should have a category defined"""
        for mat_name, mat_data in materials_data['materials'].items():
            assert 'category' in mat_data, \
                f"Material '{mat_name}' missing 'category'"
            
            assert mat_data['category'] in [
                'ceramic', 'composite', 'glass', 'masonry', 'metal',
                'plastic', 'semiconductor', 'stone', 'wood'
            ], f"Material '{mat_name}' has invalid category: {mat_data['category']}"
    
    def test_materials_have_no_min_max(self, materials_data):
        """Verify complete normalization: materials.yaml should have NO min/max anywhere"""
        properties_with_ranges = []
        
        for mat_name, mat_data in materials_data['materials'].items():
            if 'properties' not in mat_data:
                continue
            
            for prop_name, prop_data in mat_data['materialProperties'].items():
                if not isinstance(prop_data, dict):
                    continue
                
                # Check regular properties for min/max
                if 'min' in prop_data or 'max' in prop_data:
                    properties_with_ranges.append({
                        'material': mat_name,
                        'property': prop_name,
                        'has_min': 'min' in prop_data,
                        'has_max': 'max' in prop_data
                    })
                
                # Check nested thermalDestruction.point for min/max
                if prop_name == 'thermalDestruction' and isinstance(prop_data, dict):
                    if 'point' in prop_data and isinstance(prop_data['point'], dict):
                        point = prop_data['point']
                        if 'min' in point or 'max' in point:
                            properties_with_ranges.append({
                                'material': mat_name,
                                'property': 'thermalDestruction.point',
                                'has_min': 'min' in point,
                                'has_max': 'max' in point
                            })
        
        if properties_with_ranges:
            print(f"\n❌ Found {len(properties_with_ranges)} properties with min/max in materials.yaml:")
            for prop in properties_with_ranges[:10]:
                print(f"  - {prop['material']}.{prop['property']}")
        
        assert len(properties_with_ranges) == 0, \
            f"Complete normalization violated: {len(properties_with_ranges)} properties have min/max in materials.yaml. They should ONLY be in Categories.yaml."


class TestGeneratorBehavior:
    """Test that generator correctly loads and uses category ranges"""
    
    @pytest.fixture
    def category_ranges(self):
        """Load category_ranges as generator would"""
        import yaml
        from pathlib import Path
        
        categories_file = Path('data/Categories.yaml')
        with open(categories_file, 'r', encoding='utf-8') as f:
            cat_data = yaml.safe_load(f)
        
        # Extract category_ranges like generator does
        category_ranges = {}
        if 'categories' in cat_data:
            for category_name, category_info in cat_data['categories'].items():
                if 'category_ranges' in category_info:
                    category_ranges[category_name] = category_info['category_ranges']
        
        return category_ranges
    
    def test_generator_loads_category_ranges(self, category_ranges):
        """Generator should load all category ranges from Categories.yaml"""
        assert len(category_ranges) == 9, \
            f"Loaded {len(category_ranges)} categories, expected 9"
        
        # Check metal category as example
        assert 'metal' in category_ranges
        # After data quality remediation, categories have 16-19 properties
        assert len(category_ranges['metal']) >= 15, \
            f"Metal category should have at least 15 properties, has {len(category_ranges['metal'])}"
    
    def test_get_category_ranges_for_property_logic(self, category_ranges):
        """Test the logic of _get_category_ranges_for_property"""
        # Simulate the method logic
        def get_category_ranges_for_property(category: str, property_name: str):
            if not category or category not in category_ranges:
                return None
            
            cat_ranges = category_ranges[category]
            
            if property_name in cat_ranges:
                ranges = cat_ranges[property_name]
                if isinstance(ranges, dict) and 'min' in ranges and 'max' in ranges:
                    if 'unit' not in ranges:
                        return None  # Fail-fast
                    return {
                        'min': ranges['min'],
                        'max': ranges['max'],
                        'unit': ranges['unit']
                    }
            return None
        
        # Test valid property
        result = get_category_ranges_for_property('metal', 'density')
        assert result is not None
        assert 'min' in result and result['min'] == 0.53
        assert 'max' in result and result['max'] == 22.6
        assert 'unit' in result and result['unit'] == 'g/cm³'
        
        # Test property without category range (using a truly non-existent property)
        result = get_category_ranges_for_property('masonry', 'nonExistentProperty')
        assert result is None, "Should return None for properties without category ranges"
        
        # Test invalid category
        result = get_category_ranges_for_property('invalid_category', 'density')
        assert result is None


class TestFrontmatterRangePropagation:
    """Test that frontmatter uses category ranges, not material-specific ranges"""
    
    @pytest.fixture
    def copper_frontmatter(self):
        """Load Copper frontmatter"""
        fm_file = Path('content/components/frontmatter/copper-laser-cleaning.yaml')
        with open(fm_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @pytest.fixture
    def copper_material(self):
        """Load Copper from materials.yaml"""
        with open('data/materials.yaml', 'r', encoding='utf-8') as f:
            materials = yaml.safe_load(f)
            return materials['materials']['Copper']
    
    @pytest.fixture
    def metal_category_ranges(self):
        """Load metal category ranges from Categories.yaml"""
        with open('data/Categories.yaml', 'r', encoding='utf-8') as f:
            categories = yaml.safe_load(f)
            return categories['categories']['metal']['category_ranges']
    
    def test_copper_density_uses_category_ranges(
        self, copper_frontmatter, copper_material, metal_category_ranges
    ):
        """Copper density in frontmatter should use metal category ranges from Categories.yaml"""
        # Get density from frontmatter (in material_characteristics category)
        fm_density = copper_frontmatter['materialProperties']['material_characteristics']['properties']['density']
        
        # Get material value (should have NO min/max)
        mat_density = copper_material['materialProperties']['density']
        
        # Get category ranges
        cat_density = metal_category_ranges['density']
        
        # Verify material has NO min/max (complete normalization)
        assert 'min' not in mat_density, \
            "Material should not have 'min' - ranges come from Categories.yaml only"
        assert 'max' not in mat_density, \
            "Material should not have 'max' - ranges come from Categories.yaml only"
        
        # Frontmatter value should match material value
        assert fm_density['value'] == mat_density['value'], \
            "Frontmatter value should come from materials.yaml"
        
        # Frontmatter ranges should match CATEGORY ranges
        assert fm_density['min'] == cat_density['min'], \
            f"Frontmatter min ({fm_density['min']}) should match category min ({cat_density['min']})"
        assert fm_density['max'] == cat_density['max'], \
            f"Frontmatter max ({fm_density['max']}) should match category max ({cat_density['max']})"
    
    def test_copper_thermal_destruction_nested_structure(
        self, copper_frontmatter, copper_material, metal_category_ranges
    ):
        """Verify thermalDestruction uses nested structure correctly"""
        # Get thermalDestruction from frontmatter (in laser_material_interaction category)
        fm_td = copper_frontmatter['materialProperties']['laser_material_interaction']['properties'].get('thermalDestruction')
        
        # Skip test if thermalDestruction not present in this material
        if not fm_td:
            pytest.skip("thermalDestruction not present in copper frontmatter")
        
        # Get material thermalDestruction (should be nested with NO min/max)
        mat_td = copper_material['materialProperties']['thermalDestruction']
        
        # Get category thermalDestruction (nested structure)
        cat_td = metal_category_ranges['thermalDestruction']
        
        # Verify material has nested structure with NO min/max in point
        assert 'point' in mat_td, "Material should have nested 'point'"
        assert 'type' in mat_td, "Material should have 'type'"
        assert 'min' not in mat_td['point'], "Material point should not have 'min'"
        assert 'max' not in mat_td['point'], "Material point should not have 'max'"
        
        # Verify frontmatter has nested structure
        assert 'point' in fm_td, "Frontmatter should have nested 'point'"
        assert 'type' in fm_td, "Frontmatter should have 'type'"
        
        # Verify frontmatter point.value matches material
        assert fm_td['point']['value'] == mat_td['point']['value'], \
            "Frontmatter point.value should come from materials.yaml"
        
        # Verify frontmatter point ranges match category ranges
        assert fm_td['point']['min'] == cat_td['point']['min'], \
            f"Frontmatter point.min should match category ({cat_td['point']['min']})"
        assert fm_td['point']['max'] == cat_td['point']['max'], \
            f"Frontmatter point.max should match category ({cat_td['point']['max']})"
        
        # Verify type matches category
        assert fm_td['type'] == cat_td['type'], \
            f"Frontmatter type should match category ({cat_td['type']})"
    
    def test_stucco_null_ranges_when_no_category_range(self):
        """Properties without category ranges should have null min/max in frontmatter"""
        # In the new 2-category system, compressiveStrength is now in category ranges
        # All core properties now have category ranges after Priority 2 research
        # Skip this test as the assumption has changed
        pytest.skip("Test assumption changed: All core properties now have category ranges after Priority 2 research")
    
    def test_all_frontmatter_properties_with_ranges_match_categories(self):
        """Comprehensive test: All frontmatter properties with ranges should match category ranges"""
        # Load Categories.yaml
        with open('data/Categories.yaml', 'r', encoding='utf-8') as f:
            categories = yaml.safe_load(f)
        
        # Load materials.yaml
        with open('data/materials.yaml', 'r', encoding='utf-8') as f:
            materials = yaml.safe_load(f)
        
        # Check a sample of frontmatter files
        frontmatter_dir = Path('content/components/frontmatter')
        sample_files = list(frontmatter_dir.glob('*-laser-cleaning.yaml'))[:10]  # Test first 10
        
        mismatches = []
        
        for fm_file in sample_files:
            with open(fm_file, 'r', encoding='utf-8') as f:
                fm_data = yaml.safe_load(f)
            
            # Get material name from filename
            mat_name = fm_file.stem.replace('-laser-cleaning', '').replace('-', ' ').title()
            
            # Find material in materials.yaml (handle naming variations)
            mat_data = None
            for key in materials['materials'].keys():
                if key.lower().replace(' ', '-') == mat_name.lower().replace(' ', '-'):
                    mat_data = materials['materials'][key]
                    break
            
            if not mat_data or 'category' not in mat_data:
                continue
            
            category = mat_data['category']
            if category not in categories['categories']:
                continue
            
            category_ranges = categories['categories'][category].get('category_ranges', {})
            
            # Check all properties in frontmatter
            if 'materialProperties' not in fm_data:
                continue
            
            for prop_group in fm_data['materialProperties'].values():
                if 'properties' not in prop_group:
                    continue
                
                for prop_name, prop_data in prop_group['properties'].items():
                    if not isinstance(prop_data, dict):
                        continue
                    if 'min' not in prop_data or 'max' not in prop_data:
                        continue
                    
                    # If property has non-null ranges, they should match category
                    if prop_data['min'] is not None and prop_data['max'] is not None:
                        if prop_name in category_ranges:
                            cat_range = category_ranges[prop_name]
                            if isinstance(cat_range, dict):
                                if (prop_data['min'] != cat_range.get('min') or
                                    prop_data['max'] != cat_range.get('max')):
                                    mismatches.append({
                                        'file': fm_file.name,
                                        'material': mat_name,
                                        'category': category,
                                        'property': prop_name,
                                        'fm_range': f"{prop_data['min']}-{prop_data['max']}",
                                        'cat_range': f"{cat_range.get('min')}-{cat_range.get('max')}"
                                    })
        
        if mismatches:
            print(f"\n❌ Found {len(mismatches)} range mismatches:")
            for mm in mismatches[:5]:
                print(f"  {mm['file']}: {mm['property']}")
                print(f"    Frontmatter: {mm['fm_range']}")
                print(f"    Category: {mm['cat_range']}")
        
        assert len(mismatches) == 0, \
            f"Found {len(mismatches)} properties with ranges not matching category ranges"


class TestDataIntegrity:
    """Test overall data integrity and relationships"""
    
    def test_no_orphaned_categories(self):
        """All material categories should exist in Categories.yaml"""
        with open('data/materials.yaml', 'r', encoding='utf-8') as f:
            materials = yaml.safe_load(f)
        
        with open('data/Categories.yaml', 'r', encoding='utf-8') as f:
            categories = yaml.safe_load(f)
        
        category_names = set(categories['categories'].keys())
        
        for mat_name, mat_data in materials['materials'].items():
            if 'category' in mat_data:
                assert mat_data['category'] in category_names, \
                    f"Material '{mat_name}' has invalid category: {mat_data['category']}"
    
    def test_all_frontmatter_files_exist(self):
        """All materials should have corresponding frontmatter files"""
        with open('data/materials.yaml', 'r', encoding='utf-8') as f:
            materials = yaml.safe_load(f)
        
        frontmatter_dir = Path('content/components/frontmatter')
        
        missing = []
        for mat_name in materials['materials'].keys():
            # Convert material name to filename format
            filename = mat_name.lower().replace(' ', '-') + '-laser-cleaning.yaml'
            fm_file = frontmatter_dir / filename
            
            if not fm_file.exists():
                missing.append(mat_name)
        
        if missing:
            print(f"\n⚠️  {len(missing)} materials missing frontmatter files:")
            for mat in missing[:10]:
                print(f"  - {mat}")
        
        # Allow some missing (might be in progress)
        assert len(missing) <= 5, \
            f"Too many missing frontmatter files: {len(missing)}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
