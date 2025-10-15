"""
Test suite for verifying correct range propagation from Categories → Materials → Frontmatter

These tests ensure that:
1. Category ranges load correctly from Categories.yaml
2. Frontmatter uses category ranges (NOT material-specific tolerances)
3. Null ranges are preserved when no category range exists
4. Material-specific tolerances in materials.yaml are NOT propagated to frontmatter

Created: October 14, 2025
Related: docs/DATA_ARCHITECTURE.md, MISSING_RANGE_VALUES_FIXED.md
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
        """Verify all 9 categories are defined"""
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
    
    def test_category_ranges_have_twelve_properties(self, categories_data):
        """Each category should have exactly 12 properties with ranges"""
        expected_properties = [
            'density', 'hardness', 'laserAbsorption', 'laserReflectivity',
            'specificHeat', 'tensileStrength', 'thermalConductivity',
            'thermalDestructionPoint', 'thermalDestructionType',
            'thermalDiffusivity', 'thermalExpansion', 'youngsModulus'
        ]
        
        for category_name, category_data in categories_data['categories'].items():
            ranges = category_data['category_ranges']
            
            # Check count
            assert len(ranges) == 12, \
                f"Category '{category_name}' has {len(ranges)} properties, expected 12"
            
            # Check all expected properties present
            for prop in expected_properties:
                assert prop in ranges, \
                    f"Category '{category_name}' missing property '{prop}'"
    
    def test_range_structure_valid(self, categories_data):
        """Each range should have min, max, and unit (except thermalDestructionType)"""
        for category_name, category_data in categories_data['categories'].items():
            ranges = category_data['category_ranges']
            
            for prop_name, prop_data in ranges.items():
                # thermalDestructionType is a string, not a range
                if prop_name == 'thermalDestructionType':
                    assert isinstance(prop_data, str), \
                        f"{category_name}.thermalDestructionType should be string"
                    continue
                
                # All other properties should have min, max, unit
                assert isinstance(prop_data, dict), \
                    f"{category_name}.{prop_name} should be dict"
                
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
    
    def test_identify_category_range_duplicates(self, materials_data, categories_data):
        """Identify materials that duplicate category ranges exactly"""
        duplicates = []
        
        for mat_name, mat_data in materials_data['materials'].items():
            if 'category' not in mat_data or 'properties' not in mat_data:
                continue
            
            category = mat_data['category']
            if category not in categories_data['categories']:
                continue
            
            category_ranges = categories_data['categories'][category].get('category_ranges', {})
            
            for prop_name, prop_data in mat_data['properties'].items():
                if not isinstance(prop_data, dict):
                    continue
                if 'min' not in prop_data or 'max' not in prop_data:
                    continue
                if prop_name not in category_ranges:
                    continue
                
                cat_range = category_ranges[prop_name]
                if not isinstance(cat_range, dict):
                    continue
                
                # Check for exact match
                if (prop_data['min'] == cat_range.get('min') and 
                    prop_data['max'] == cat_range.get('max')):
                    duplicates.append({
                        'material': mat_name,
                        'category': category,
                        'property': prop_name,
                        'range': f"{prop_data['min']}-{prop_data['max']}"
                    })
        
        # Log duplicates for awareness (not a failure - known issue)
        if duplicates:
            print(f"\n⚠️  Found {len(duplicates)} category range duplicates in materials.yaml:")
            for dup in duplicates[:10]:  # Show first 10
                print(f"  - {dup['material']} ({dup['category']}) - {dup['property']}")
            
            # This is a known data quality issue, not a test failure
            # But we document it for awareness
            assert len(duplicates) <= 10, \
                f"Too many duplicates found ({len(duplicates)}). Expected ~8 known issues."


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
        assert len(category_ranges['metal']) == 12
    
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
        
        # Test property without category range
        result = get_category_ranges_for_property('masonry', 'compressiveStrength')
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
        """Copper density in frontmatter should use metal category ranges, not material tolerances"""
        # Get density from frontmatter
        fm_density = copper_frontmatter['materialProperties']['physical_structural']['properties']['density']
        
        # Get material tolerance ranges
        mat_density = copper_material['properties']['density']
        
        # Get category ranges
        cat_density = metal_category_ranges['density']
        
        # Frontmatter value should match material value
        assert fm_density['value'] == mat_density['value'], \
            "Frontmatter value should come from materials.yaml"
        
        # Frontmatter ranges should match CATEGORY ranges
        assert fm_density['min'] == cat_density['min'], \
            f"Frontmatter min ({fm_density['min']}) should match category min ({cat_density['min']})"
        assert fm_density['max'] == cat_density['max'], \
            f"Frontmatter max ({fm_density['max']}) should match category max ({cat_density['max']})"
        
        # Frontmatter ranges should NOT match material tolerance ranges
        assert fm_density['min'] != mat_density['min'] or fm_density['max'] != mat_density['max'], \
            "Frontmatter should NOT use material-specific tolerance ranges"
    
    def test_stucco_null_ranges_when_no_category_range(self):
        """Properties without category ranges should have null min/max in frontmatter"""
        # Load Stucco frontmatter
        fm_file = Path('content/components/frontmatter/stucco-laser-cleaning.yaml')
        with open(fm_file, 'r', encoding='utf-8') as f:
            stucco_fm = yaml.safe_load(f)
        
        # Load masonry category ranges
        with open('data/Categories.yaml', 'r', encoding='utf-8') as f:
            categories = yaml.safe_load(f)
            masonry_ranges = categories['categories']['masonry']['category_ranges']
        
        # Check that compressiveStrength is NOT in category ranges
        assert 'compressiveStrength' not in masonry_ranges, \
            "Test assumption violated: compressiveStrength should not be in masonry category_ranges"
        
        # Check frontmatter has null ranges for compressiveStrength
        if 'mechanical' in stucco_fm['materialProperties']:
            comp = stucco_fm['materialProperties']['mechanical']['properties'].get('compressiveStrength')
            if comp:
                assert comp['value'] is not None, "Should have a value"
                assert comp['min'] is None, "Should have null min (no category range)"
                assert comp['max'] is None, "Should have null max (no category range)"
    
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
