#!/usr/bin/env python3
"""
Comprehensive End-to-End Testing for Content Component

This test suite validates the complete content generation flow:
1. Frontmatter → Author Detection → Country Selection
2. Prompt Configuration Loading (Base + Persona)
3. Material Data Integration → Chemical Formula Extraction
4. Content Generation → Technical Structure Validation
5. Output Quality Assurance

Tests cover all author personas, material types, and edge cases.
"""

import sys
import os
import unittest
import yaml
import json
import tempfile
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from components.content.generator import (
    ContentComponentGenerator, 
    load_base_content_prompt,
    load_persona_prompt,
    load_authors_data
)

class TestContentEndToEnd(unittest.TestCase):
    """Comprehensive end-to-end testing for content generation."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment with sample data."""
        cls.test_dir = Path(tempfile.mkdtemp())
        cls.original_cwd = os.getcwd()
        os.chdir(project_root)
        
        # Initialize the generator
        cls.generator = ContentComponentGenerator()
        
        # Sample materials for testing
        cls.test_materials = {
            'Aluminum': {
                'density': '2.70 g/cm³',
                'melting_point': '660.3°C',
                'thermal_conductivity': '205 W/m·K',
                'formula': 'Al'
            },
            'Steel': {
                'density': '7.85 g/cm³', 
                'melting_point': '1370-1510°C',
                'thermal_conductivity': '50.2 W/m·K',
                'formula': 'Fe + C alloy'
            },
            'Unknown_Material': {
                'density': 'Unknown',
                'melting_point': 'Unknown'
                # No formula to test fallback
            }
        }
        
        # Sample frontmatter data for each author
        cls.sample_frontmatter = {
            'taiwan': {
                'name': 'Aluminum',
                'author': 'Yi-Chun Lin',
                'authorCountry': 'Taiwan',
                'description': 'Technical analysis of aluminum laser cleaning',
                'chemicalProperties': {
                    'formula': 'Al',
                    'symbol': 'Al'
                },
                'properties': {
                    'density': '2.70 g/cm³',
                    'meltingPoint': '660.3°C',
                    'thermalConductivity': '205 W/m·K',
                    'chemicalFormula': 'Al'
                },
                'technicalSpecifications': {
                    'powerRange': '100-500W',
                    'wavelength': '1064nm',
                    'pulseDuration': '10-100ns'
                }
            },
            'italy': {
                'name': 'Steel',
                'author': 'Alessandro Moretti',
                'authorCountry': 'Italy',
                'description': 'Steel laser cleaning for heritage preservation',
                'chemicalProperties': {
                    'formula': 'Fe + C alloy'
                },
                'properties': {
                    'density': '7.85 g/cm³',
                    'meltingPoint': '1370-1510°C'
                }
            },
            'indonesia': {
                'name': 'Copper',
                'author': 'Ikmanda Roswati',
                'authorCountry': 'Indonesia',
                'description': 'Copper laser cleaning for marine applications'
            },
            'usa': {
                'name': 'Titanium',
                'author': 'Todd Dunning', 
                'authorCountry': 'USA',
                'description': 'Titanium laser cleaning for aerospace'
            }
        }
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        os.chdir(cls.original_cwd)
        shutil.rmtree(cls.test_dir, ignore_errors=True)
    
    def test_01_prompt_configuration_loading(self):
        """Test that all prompt configurations load correctly."""
        print("\n🔍 Testing prompt configuration loading...")
        
        # Test base prompt loading
        base_config = load_base_content_prompt()
        self.assertIsInstance(base_config, dict)
        self.assertIn('author_configurations', base_config)
        self.assertIn('technical_requirements', base_config)
        
        # Verify all author configurations exist
        author_configs = base_config['author_configurations']
        required_authors = ['taiwan', 'italy', 'indonesia', 'usa']
        for author in required_authors:
            self.assertIn(author, author_configs)
            config = author_configs[author]
            self.assertIn('author_id', config)
            self.assertIn('max_word_count', config)
            self.assertIn('specialization_focus', config)
        
        # Test persona prompt loading for each author
        for author_id in [1, 2, 3, 4]:
            persona_config = load_persona_prompt(author_id)
            self.assertIsInstance(persona_config, dict)
            self.assertIn('name', persona_config)
            self.assertIn('country', persona_config)
            self.assertIn('writing_style', persona_config)
            self.assertIn('content_structure', persona_config)
        
        print("✅ All prompt configurations loaded successfully")
    
    def test_02_authors_data_loading(self):
        """Test that authors data loads and maps correctly."""
        print("\n🔍 Testing authors data loading...")
        
        authors_data = load_authors_data()
        self.assertIsInstance(authors_data, list)
        self.assertGreater(len(authors_data), 0)
        
        # Verify required author data structure
        for author in authors_data:
            self.assertIn('id', author)
            self.assertIn('name', author)
            self.assertIn('country', author)
        
        # Test specific author mapping
        author_names = [author['name'] for author in authors_data]
        expected_authors = ['Yi-Chun Lin', 'Alessandro Moretti', 'Ikmanda Roswati', 'Todd Dunning']
        
        for expected in expected_authors:
            self.assertIn(expected, author_names)
        
        print("✅ Authors data loaded and mapped correctly")
    
    def test_03_chemical_formula_extraction(self):
        """Test chemical formula extraction from various sources."""
        print("\n🔍 Testing chemical formula extraction...")
        
        # Test extraction from material_data
        formula = self.generator._extract_chemical_formula(
            self.test_materials['Aluminum'], None, 'Aluminum'
        )
        self.assertEqual(formula, 'Al')
        
        # Test extraction from frontmatter chemicalProperties
        formula = self.generator._extract_chemical_formula(
            {}, self.sample_frontmatter['taiwan'], 'Aluminum'
        )
        self.assertEqual(formula, 'Al')
        
        # Test extraction from frontmatter properties
        frontmatter_properties_only = {
            'properties': {'chemicalFormula': 'Fe + C alloy'}
        }
        formula = self.generator._extract_chemical_formula(
            {}, frontmatter_properties_only, 'Steel'
        )
        self.assertEqual(formula, 'Fe + C alloy')
        
        # Test fallback for unknown material
        formula = self.generator._extract_chemical_formula(
            {}, {}, 'Aluminum'
        )
        self.assertEqual(formula, 'Al')
        
        # Test fallback for completely unknown material
        formula = self.generator._extract_chemical_formula(
            {}, {}, 'UnknownMaterial'
        )
        self.assertEqual(formula, 'UnknownMaterial composition')
        
        print("✅ Chemical formula extraction working correctly")
    
    def test_04_author_detection_from_frontmatter(self):
        """Test author detection and country mapping from frontmatter."""
        print("\n🔍 Testing author detection from frontmatter...")
        
        test_cases = [
            ('Yi-Chun Lin', 'taiwan', 1),
            ('Alessandro Moretti', 'italy', 2),
            ('Ikmanda Roswati', 'indonesia', 3),
            ('Todd Dunning', 'usa', 4)
        ]
        
        for author_name, expected_country, expected_id in test_cases:
            # Create frontmatter with this author
            frontmatter = {
                'author': author_name,
                'name': 'Test Material',
                'chemicalProperties': {'formula': 'Test'}
            }
            
            # Generate content and verify author detection
            content = self.generator._generate_static_content(
                'Test Material',
                self.test_materials['Aluminum'],
                frontmatter_data=frontmatter
            )
            
            self.assertIsInstance(content, str)
            self.assertGreater(len(content), 0)
            
            # Verify the content reflects the correct author
            if author_name == 'Yi-Chun Lin':
                self.assertIn('systematic', content.lower())
            elif author_name == 'Alessandro Moretti':
                self.assertIn('technical', content.lower())
        
        print("✅ Author detection and mapping working correctly")
    
    def test_05_content_generation_all_authors(self):
        """Test content generation for all author personas."""
        print("\n🔍 Testing content generation for all authors...")
        
        for country, frontmatter in self.sample_frontmatter.items():
            material_name = frontmatter['name']
            material_data = self.test_materials.get(material_name, self.test_materials['Aluminum'])
            
            try:
                content = self.generator._generate_static_content(
                    material_name,
                    material_data,
                    frontmatter_data=frontmatter
                )
                
                # Validate content structure
                self.assertIsInstance(content, str)
                self.assertGreater(len(content), 100, f"Content too short for {country}")
                
                # Verify content contains required technical elements
                content_lower = content.lower()
                technical_terms = ['laser', 'cleaning', 'nm', 'wavelength']
                for term in technical_terms:
                    self.assertIn(term, content_lower, f"Missing '{term}' in {country} content")
                
                # Verify author-specific elements
                if country == 'taiwan':
                    self.assertTrue(
                        any(phrase in content for phrase in ['systematic', 'analysis', 'methodical']),
                        "Missing Taiwan-specific elements in content"
                    )
                elif country == 'italy':
                    self.assertTrue(
                        any(phrase in content for phrase in ['heritage', 'precision', 'technical']),
                        "Missing Italy-specific elements in content"
                    )
                
                print(f"✅ {country.capitalize()} content generated successfully ({len(content)} chars)")
                
            except Exception as e:
                self.fail(f"Content generation failed for {country}: {str(e)}")
        
        print("✅ All author personas generating content correctly")
    
    def test_06_technical_requirements_validation(self):
        """Test that generated content meets technical requirements."""
        print("\n🔍 Testing technical requirements validation...")
        
        # Generate content for Taiwan persona (most systematic)
        frontmatter = self.sample_frontmatter['taiwan']
        content = self.generator._generate_static_content(
            'Aluminum',
            self.test_materials['Aluminum'],
            frontmatter_data=frontmatter
        )
        
        # Technical requirements from base prompt
        required_elements = [
            '1064',  # wavelength
            'ns',    # nanosecond pulses
            'class 4',  # safety classification (case insensitive)
            'fiber',    # fiber laser
            'al',       # chemical formula (case insensitive)
            'fluence'   # technical parameter
        ]
        
        content_lower = content.lower()
        missing_elements = []
        
        for element in required_elements:
            if element.lower() not in content_lower:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"⚠️  Missing technical elements: {missing_elements}")
            print(f"Content preview: {content[:200]}...")
        
        # Should have most technical elements (allow some flexibility)
        self.assertLessEqual(len(missing_elements), 2, 
                           f"Too many missing technical elements: {missing_elements}")
        
        print("✅ Technical requirements validation passed")
    
    def test_07_content_structure_validation(self):
        """Test that content follows expected structure patterns."""
        print("\n🔍 Testing content structure validation...")
        
        for country, frontmatter in self.sample_frontmatter.items():
            content = self.generator._generate_static_content(
                frontmatter['name'],
                self.test_materials.get(frontmatter['name'], self.test_materials['Aluminum']),
                frontmatter_data=frontmatter
            )
            
            # Check for section headers (markdown format)
            sections_found = content.count('##')
            self.assertGreaterEqual(sections_found, 3, 
                                  f"Insufficient sections in {country} content")
            
            # Check for proper formatting
            self.assertIn('**', content, f"Missing bold formatting in {country} content")
            
            # Check for author byline
            author_name = frontmatter['author']
            self.assertIn(author_name, content, f"Missing author byline in {country} content")
            
            print(f"✅ {country.capitalize()} content structure validated")
        
        print("✅ Content structure validation completed")
    
    def test_08_edge_cases_and_error_handling(self):
        """Test edge cases and error handling."""
        print("\n🔍 Testing edge cases and error handling...")
        
        # Test with minimal frontmatter
        minimal_frontmatter = {'name': 'Unknown'}
        try:
            content = self.generator._generate_static_content(
                'Unknown',
                {},
                frontmatter_data=minimal_frontmatter
            )
            self.assertIsInstance(content, str)
            self.assertGreater(len(content), 50)
            print("✅ Minimal frontmatter handled correctly")
        except Exception as e:
            self.fail(f"Failed with minimal frontmatter: {str(e)}")
        
        # Test with None frontmatter
        try:
            content = self.generator._generate_static_content(
                'TestMaterial',
                self.test_materials['Aluminum'],
                frontmatter_data=None
            )
            self.assertIsInstance(content, str)
            print("✅ None frontmatter handled correctly")
        except Exception as e:
            self.fail(f"Failed with None frontmatter: {str(e)}")
        
        # Test with invalid author
        invalid_frontmatter = {
            'author': 'Invalid Author',
            'name': 'Test'
        }
        try:
            content = self.generator._generate_static_content(
                'Test',
                self.test_materials['Aluminum'],
                frontmatter_data=invalid_frontmatter
            )
            self.assertIsInstance(content, str)
            print("✅ Invalid author handled correctly (fallback applied)")
        except Exception as e:
            self.fail(f"Failed with invalid author: {str(e)}")
        
        print("✅ Edge cases and error handling validated")
    
    def test_09_content_quality_metrics(self):
        """Test content quality metrics and variation."""
        print("\n🔍 Testing content quality metrics...")
        
        contents = {}
        word_counts = {}
        
        # Generate content for each author
        for country, frontmatter in self.sample_frontmatter.items():
            content = self.generator._generate_static_content(
                frontmatter['name'],
                self.test_materials.get(frontmatter['name'], self.test_materials['Aluminum']),
                frontmatter_data=frontmatter
            )
            
            contents[country] = content
            word_counts[country] = len(content.split())
            
            # Validate word count is reasonable
            self.assertGreater(word_counts[country], 50, 
                             f"{country} content too short: {word_counts[country]} words")
            self.assertLess(word_counts[country], 800, 
                          f"{country} content too long: {word_counts[country]} words")
        
        # Test content variation between authors
        unique_contents = set(contents.values())
        self.assertEqual(len(unique_contents), len(contents), 
                        "Content should be unique for each author")
        
        # Verify word count differences align with author specifications
        # Taiwan should be more concise, Italy more detailed
        taiwan_words = word_counts.get('taiwan', 0)
        italy_words = word_counts.get('italy', 0)
        
        if taiwan_words > 0 and italy_words > 0:
            # Italy should generally have more words (but allow flexibility)
            ratio = italy_words / taiwan_words
            self.assertGreater(ratio, 0.8, "Word count ratios should reflect author styles")
        
        print(f"✅ Quality metrics: {word_counts}")
        print("✅ Content quality validation completed")
    
    def test_10_integration_with_real_files(self):
        """Test integration with actual prompt and data files."""
        print("\n🔍 Testing integration with real system files...")
        
        # Verify actual prompt files exist and are valid
        prompt_files = [
            'components/content/prompts/base_content_prompt.yaml',
            'components/content/prompts/taiwan_prompt.yaml',
            'components/content/prompts/italy_prompt.yaml',
            'components/content/prompts/indonesia_prompt.yaml',
            'components/content/prompts/usa_prompt.yaml'
        ]
        
        for prompt_file in prompt_files:
            file_path = Path(prompt_file)
            self.assertTrue(file_path.exists(), f"Prompt file missing: {prompt_file}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self.assertIsInstance(data, dict, f"Invalid YAML in {prompt_file}")
        
        # Test with real authors file
        authors_file = Path('components/author/authors.json')
        self.assertTrue(authors_file.exists(), "Authors file missing")
        
        with open(authors_file, 'r', encoding='utf-8') as f:
            authors_data = json.load(f)
            self.assertIn('authors', authors_data)
            self.assertGreater(len(authors_data['authors']), 0)
        
        # Test with actual frontmatter file if available
        frontmatter_files = list(Path('content/components/frontmatter').glob('*.md'))
        if frontmatter_files:
            test_file = frontmatter_files[0]
            print(f"Testing with real frontmatter: {test_file.name}")
            
            # Read frontmatter from actual file
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.startswith('---'):
                    yaml_end = content.find('---', 3)
                    if yaml_end > 0:
                        yaml_content = content[3:yaml_end]
                        frontmatter_data = yaml.safe_load(yaml_content)
                        
                        # Test content generation with real frontmatter
                        if frontmatter_data and 'name' in frontmatter_data:
                            generated_content = self.generator._generate_static_content(
                                frontmatter_data['name'],
                                self.test_materials.get(frontmatter_data['name'], {}),
                                frontmatter_data=frontmatter_data
                            )
                            
                            self.assertIsInstance(generated_content, str)
                            self.assertGreater(len(generated_content), 100)
                            print("✅ Real frontmatter integration successful")
        
        print("✅ Integration with real system files validated")

def run_comprehensive_test():
    """Run all tests with detailed output."""
    print("🚀 Starting Comprehensive Content Component End-to-End Testing")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestContentEndToEnd)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    print("🎯 TEST SUMMARY")
    print("=" * 70)
    
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED - Content component is fully functional!")
        print(f"   Tests run: {result.testsRun}")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
    else:
        print("❌ SOME TESTS FAILED")
        print(f"   Tests run: {result.testsRun}")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
        
        if result.failures:
            print("\nFAILURES:")
            for test, trace in result.failures:
                print(f"  - {test}: {trace}")
        
        if result.errors:
            print("\nERRORS:")
            for test, trace in result.errors:
                print(f"  - {test}: {trace}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
