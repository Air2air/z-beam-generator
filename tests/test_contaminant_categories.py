"""
Test contaminant categorization system.

Validates that all contamination patterns have proper category/subcategory
assignments according to the 8-category system implemented Dec 14, 2025.
"""

import pytest
import yaml
from pathlib import Path


# Expected categories and subcategories (from schema)
ALLOWED_CATEGORIES = [
    'oxidation',
    'organic-residue',
    'inorganic-coating',
    'metallic-coating',
    'thermal-damage',
    'biological',
    'chemical-residue',
    'aging'
]

ALLOWED_SUBCATEGORIES = {
    'oxidation': ['ferrous', 'non-ferrous', 'battery'],
    'organic-residue': [
        'petroleum', 'adhesive', 'polymer', 'biological-fluid',
        'wax', 'marking', 'lubricant', 'cleaning-agent', 'natural', 'other'
    ],
    'inorganic-coating': ['paint', 'ceramic', 'mineral', 'coating', 'hazardous'],
    'metallic-coating': ['plating', 'anodizing'],
    'thermal-damage': ['scale', 'fire', 'coating'],
    'biological': ['growth', 'deposit'],
    'chemical-residue': ['hazardous', 'industrial'],
    'aging': ['photodegradation', 'weathering']
}


@pytest.fixture
def contaminants_data():
    """Load Contaminants.yaml data."""
    contaminants_path = Path('data/contaminants/Contaminants.yaml')
    with open(contaminants_path, 'r') as f:
        return yaml.safe_load(f)


@pytest.fixture
def frontmatter_files():
    """
    Get all contaminant frontmatter files from website export directory.
    
    NOTE: Tests check ../z-beam/frontmatter (website exports with complete metadata),
    NOT local frontmatter/ (postprocessing output with minimal fields).
    
    Per FRONTMATTER_SOURCE_OF_TRUTH_POLICY: Local frontmatter/ is postprocessing
    output (only generated content fields). Complete frontmatter with metadata 
    (category, subcategory, etc.) is in ../z-beam/frontmatter after --export.
    """
    frontmatter_dir = Path('../z-beam/frontmatter/contaminants')
    if not frontmatter_dir.exists():
        pytest.skip(f"Website frontmatter directory not found: {frontmatter_dir}")
    
    # Get files with single suffix only (exclude postprocessing duplicates if any)
    all_files = list(frontmatter_dir.glob('*.yaml'))
    
    # Filter: Keep -contamination.yaml, exclude -contamination-contamination.yaml
    filtered_files = [f for f in all_files if not f.stem.endswith('-contamination-contamination')]
    
    return filtered_files


class TestSourceDataCategories:
    """Test category fields in source data (Contaminants.yaml)."""
    
    def test_all_patterns_have_category(self, contaminants_data):
        """All patterns must have a category field."""
        patterns = contaminants_data['contaminants']
        missing_category = []
        
        for pattern_id, pattern_data in patterns.items():
            if 'category' not in pattern_data:
                missing_category.append(pattern_id)
        
        assert not missing_category, (
            f"Found {len(missing_category)} patterns without 'category' field: "
            f"{', '.join(missing_category[:5])}..."
        )
    
    def test_all_patterns_have_subcategory(self, contaminants_data):
        """All patterns must have a subcategory field."""
        patterns = contaminants_data['contaminants']
        missing_subcategory = []
        
        for pattern_id, pattern_data in patterns.items():
            if 'subcategory' not in pattern_data:
                missing_subcategory.append(pattern_id)
        
        assert not missing_subcategory, (
            f"Found {len(missing_subcategory)} patterns without 'subcategory' field: "
            f"{', '.join(missing_subcategory[:5])}..."
        )
    
    def test_categories_are_valid(self, contaminants_data):
        """All category values must be in allowed list."""
        patterns = contaminants_data['contaminants']
        invalid_categories = {}
        
        for pattern_id, pattern_data in patterns.items():
            category = pattern_data.get('category')
            if category not in ALLOWED_CATEGORIES:
                invalid_categories[pattern_id] = category
        
        assert not invalid_categories, (
            f"Found {len(invalid_categories)} patterns with invalid categories: "
            f"{dict(list(invalid_categories.items())[:3])}"
        )
    
    def test_subcategories_match_category(self, contaminants_data):
        """Subcategory values must match their parent category's allowed list."""
        patterns = contaminants_data['contaminants']
        invalid_subcategories = {}
        
        for pattern_id, pattern_data in patterns.items():
            category = pattern_data.get('category')
            subcategory = pattern_data.get('subcategory')
            
            if category in ALLOWED_SUBCATEGORIES:
                allowed = ALLOWED_SUBCATEGORIES[category]
                if subcategory not in allowed:
                    invalid_subcategories[pattern_id] = {
                        'category': category,
                        'subcategory': subcategory,
                        'allowed': allowed
                    }
        
        assert not invalid_subcategories, (
            f"Found {len(invalid_subcategories)} patterns with invalid subcategories: "
            f"{dict(list(invalid_subcategories.items())[:2])}"
        )


class TestCategoryDistribution:
    """Test expected distribution across categories."""
    
    def test_category_counts(self, contaminants_data):
        """Verify expected number of patterns per category."""
        patterns = contaminants_data['contaminants']
        by_category = {}
        
        for pattern_data in patterns.values():
            category = pattern_data.get('category', 'MISSING')
            by_category[category] = by_category.get(category, 0) + 1
        
        # Expected distribution (approximate, based on implementation)
        expected_ranges = {
            'organic-residue': (25, 35),      # Largest category
            'inorganic-coating': (15, 20),
            'thermal-damage': (10, 15),
            'chemical-residue': (10, 15),
            'metallic-coating': (8, 12),
            'oxidation': (7, 11),
            'biological': (5, 10),
            'aging': (1, 3)
        }
        
        for category, (min_count, max_count) in expected_ranges.items():
            actual_count = by_category.get(category, 0)
            assert min_count <= actual_count <= max_count, (
                f"Category '{category}' has {actual_count} patterns, "
                f"expected {min_count}-{max_count}"
            )
    
    def test_no_missing_categories(self, contaminants_data):
        """All 8 categories should have at least one pattern."""
        patterns = contaminants_data['contaminants']
        by_category = {}
        
        for pattern_data in patterns.values():
            category = pattern_data.get('category')
            by_category[category] = by_category.get(category, 0) + 1
        
        for expected_category in ALLOWED_CATEGORIES:
            assert expected_category in by_category, (
                f"Category '{expected_category}' has no patterns"
            )
            assert by_category[expected_category] > 0, (
                f"Category '{expected_category}' count is zero"
            )


class TestQuestionablePatterns:
    """Test the 3 patterns that were moved to correct categories."""
    
    def test_brass_plating_moved_to_metallic_coating(self, contaminants_data):
        """brass-plating-contamination should be in metallic-coating/plating."""
        patterns = contaminants_data['contaminants']
        assert 'brass-plating-contamination' in patterns
        
        pattern = patterns['brass-plating-contamination']
        assert pattern['category'] == 'metallic-coating', (
            f"brass-plating-contamination category is '{pattern['category']}', "
            f"expected 'metallic-coating'"
        )
        assert pattern['subcategory'] == 'plating', (
            f"brass-plating-contamination subcategory is '{pattern['subcategory']}', "
            f"expected 'plating'"
        )
    
    def test_chrome_pitting_moved_to_oxidation(self, contaminants_data):
        """chrome-pitting-contamination should be in oxidation/non-ferrous."""
        patterns = contaminants_data['contaminants']
        assert 'chrome-pitting-contamination' in patterns
        
        pattern = patterns['chrome-pitting-contamination']
        assert pattern['category'] == 'oxidation', (
            f"chrome-pitting-contamination category is '{pattern['category']}', "
            f"expected 'oxidation'"
        )
        assert pattern['subcategory'] == 'non-ferrous', (
            f"chrome-pitting-contamination subcategory is '{pattern['subcategory']}', "
            f"expected 'non-ferrous'"
        )
    
    def test_chemical_stains_moved_to_chemical_residue(self, contaminants_data):
        """chemical-stains-contamination should be in chemical-residue/industrial."""
        patterns = contaminants_data['contaminants']
        assert 'chemical-stains-contamination' in patterns
        
        pattern = patterns['chemical-stains-contamination']
        assert pattern['category'] == 'chemical-residue', (
            f"chemical-stains-contamination category is '{pattern['category']}', "
            f"expected 'chemical-residue'"
        )
        assert pattern['subcategory'] == 'industrial', (
            f"chemical-stains-contamination subcategory is '{pattern['subcategory']}', "
            f"expected 'industrial'"
        )


class TestFrontmatterCategories:
    """Test category fields in exported frontmatter files."""
    
    def test_all_frontmatter_have_category(self, frontmatter_files):
        """All frontmatter files must have category field."""
        missing_category = []
        
        for file_path in frontmatter_files:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            if 'category' not in data:
                missing_category.append(file_path.name)
        
        assert not missing_category, (
            f"Found {len(missing_category)} frontmatter files without 'category': "
            f"{', '.join(missing_category[:5])}..."
        )
    
    def test_all_frontmatter_have_subcategory(self, frontmatter_files):
        """All frontmatter files must have subcategory field."""
        missing_subcategory = []
        
        for file_path in frontmatter_files:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            if 'subcategory' not in data:
                missing_subcategory.append(file_path.name)
        
        assert not missing_subcategory, (
            f"Found {len(missing_subcategory)} frontmatter files without 'subcategory': "
            f"{', '.join(missing_subcategory[:5])}..."
        )
    
    def test_frontmatter_categories_valid(self, frontmatter_files):
        """Frontmatter category values must be valid."""
        invalid_categories = {}
        
        for file_path in frontmatter_files:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            category = data.get('category')
            if category not in ALLOWED_CATEGORIES:
                invalid_categories[file_path.name] = category
        
        assert not invalid_categories, (
            f"Found {len(invalid_categories)} frontmatter files with invalid categories: "
            f"{dict(list(invalid_categories.items())[:3])}"
        )
    
    def test_frontmatter_matches_source(self, contaminants_data, frontmatter_files):
        """Frontmatter categories should match source data."""
        patterns = contaminants_data['contaminants']
        mismatches = []
        
        for file_path in frontmatter_files:
            with open(file_path, 'r') as f:
                frontmatter = yaml.safe_load(f)
            
            # Extract pattern_id from slug (remove -contamination suffix)
            slug = frontmatter.get('slug', '')
            pattern_id = slug.replace('-contamination', '')
            
            if pattern_id in patterns:
                source_cat = patterns[pattern_id].get('category')
                source_subcat = patterns[pattern_id].get('subcategory')
                fm_cat = frontmatter.get('category')
                fm_subcat = frontmatter.get('subcategory')
                
                if source_cat != fm_cat or source_subcat != fm_subcat:
                    mismatches.append({
                        'file': file_path.name,
                        'pattern_id': pattern_id,
                        'source': f"{source_cat}/{source_subcat}",
                        'frontmatter': f"{fm_cat}/{fm_subcat}"
                    })
        
        assert not mismatches, (
            f"Found {len(mismatches)} frontmatter/source mismatches: "
            f"{mismatches[:2]}"
        )


class TestRemovedPatterns:
    """Test that removed patterns are actually gone."""
    
    def test_natural_weathering_removed_from_source(self, contaminants_data):
        """natural-weathering pattern should not exist in source data."""
        patterns = contaminants_data['contaminants']
        assert 'natural-weathering' not in patterns, (
            "Pattern 'natural-weathering' should have been removed "
            "(had no name in source data)"
        )
    
    def test_natural_weathering_removed_from_frontmatter(self):
        """natural-weathering frontmatter file should not exist."""
        frontmatter_file = Path('frontmatter/contaminants/natural-weathering-contamination.yaml')
        assert not frontmatter_file.exists(), (
            f"Frontmatter file {frontmatter_file} should have been removed"
        )


class TestFlatStructure:
    """Test that frontmatter maintains flat structure (no subdirectories)."""
    
    def test_no_category_subdirectories(self):
        """Frontmatter should not have category subdirectories."""
        frontmatter_dir = Path('frontmatter/contaminants')
        subdirs = [d for d in frontmatter_dir.iterdir() if d.is_dir()]
        
        assert not subdirs, (
            f"Found {len(subdirs)} subdirectories in frontmatter/contaminants/: "
            f"{[d.name for d in subdirs[:3]]}"
        )
    
    def test_all_files_in_root(self, frontmatter_files):
        """All frontmatter files should be directly in contaminants/ directory."""
        for file_path in frontmatter_files:
            parent_name = file_path.parent.name
            assert parent_name == 'contaminants', (
                f"File {file_path.name} is in '{parent_name}/', "
                f"should be in 'contaminants/'"
            )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
