#!/usr/bin/env python3
"""
Test Property Pattern Detection and Value Extraction

Tests the new pattern-aware property handling added to streamlined_generator.py
to support pulse-specific, wavelength-specific, and authoritative property formats.

Related to: FRONTMATTER_NORMALIZATION_REPORT.md
Priority 2 Updates: 224 authoritative properties across 91 materials
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from components.frontmatter.core.streamlined_generator import StreamlinedFrontmatterGenerator


class TestPropertyPatternDetection:
    """Test pattern detection for different property data structures"""
    
    @pytest.fixture
    def generator(self):
        """Create a generator instance for testing"""
        # Create minimal instance (we only need the pattern detection methods)
        gen = StreamlinedFrontmatterGenerator.__new__(StreamlinedFrontmatterGenerator)
        return gen
    
    def test_detect_legacy_pattern(self, generator):
        """Test detection of legacy property format"""
        legacy_prop = {
            'value': 0.8,
            'unit': 'J/cm²',
            'confidence': 80,
            'description': 'Laser ablation threshold',
            'min': None,
            'max': None
        }
        
        pattern = generator._detect_property_pattern(legacy_prop)
        assert pattern == 'legacy'
    
    def test_detect_pulse_specific_pattern(self, generator):
        """Test detection of pulse-specific property format (Priority 2 data)"""
        pulse_specific = {
            'nanosecond': {
                'min': 2.0,
                'max': 8.0,
                'unit': 'J/cm²'
            },
            'picosecond': {
                'min': 0.1,
                'max': 2.0,
                'unit': 'J/cm²'
            },
            'femtosecond': {
                'min': 0.14,
                'max': 1.7,
                'unit': 'J/cm²'
            },
            'source': 'Marks et al. 2022, Precision Engineering',
            'confidence': 90,
            'measurement_context': 'Varies by pulse duration (ns/ps/fs)'
        }
        
        pattern = generator._detect_property_pattern(pulse_specific)
        assert pattern == 'pulse-specific'
    
    def test_detect_wavelength_specific_pattern(self, generator):
        """Test detection of wavelength-specific property format (Priority 2 data)"""
        wavelength_specific = {
            'at_1064nm': {
                'min': 85,
                'max': 98,
                'unit': '%'
            },
            'at_532nm': {
                'min': 70,
                'max': 95,
                'unit': '%'
            },
            'at_355nm': {
                'min': 55,
                'max': 85,
                'unit': '%'
            },
            'at_10640nm': {
                'min': 95,
                'max': 99,
                'unit': '%'
            },
            'source': 'Handbook of Optical Constants (Palik)',
            'confidence': 85,
            'measurement_context': 'Varies by laser wavelength'
        }
        
        pattern = generator._detect_property_pattern(wavelength_specific)
        assert pattern == 'wavelength-specific'
    
    def test_detect_authoritative_pattern(self, generator):
        """Test detection of authoritative property format (high confidence with source)"""
        authoritative = {
            'value': 401,
            'unit': 'W/(m·K)',
            'confidence': 90,
            'description': 'Thermal conductivity',
            'min': 15,
            'max': 400,
            'source': 'MatWeb Materials Database',
            'notes': 'Typical range for metal materials at room temperature'
        }
        
        pattern = generator._detect_property_pattern(authoritative)
        assert pattern == 'authoritative'
    
    def test_detect_legacy_sourced_pattern(self, generator):
        """Test detection of legacy format with source but lower confidence"""
        legacy_sourced = {
            'value': 10.5,
            'unit': '%',
            'confidence': 75,
            'description': 'Porosity',
            'min': 5,
            'max': 15,
            'source': 'Research Database'
        }
        
        pattern = generator._detect_property_pattern(legacy_sourced)
        assert pattern == 'legacy-sourced'


class TestPropertyValueExtraction:
    """Test value extraction from different property patterns"""
    
    @pytest.fixture
    def generator(self):
        """Create a generator instance for testing"""
        gen = StreamlinedFrontmatterGenerator.__new__(StreamlinedFrontmatterGenerator)
        return gen
    
    def test_extract_from_legacy_format(self, generator):
        """Test extracting value from legacy format"""
        legacy_prop = {
            'value': 0.8,
            'unit': 'J/cm²',
            'confidence': 80,
            'min': None,
            'max': None
        }
        
        value = generator._extract_property_value(legacy_prop)
        assert value == 0.8
    
    def test_extract_from_pulse_specific_nanosecond(self, generator):
        """Test extracting nanosecond value from pulse-specific format"""
        pulse_specific = {
            'nanosecond': {
                'min': 2.0,
                'max': 8.0,
                'unit': 'J/cm²'
            },
            'picosecond': {
                'min': 0.1,
                'max': 2.0,
                'unit': 'J/cm²'
            },
            'femtosecond': {
                'min': 0.14,
                'max': 1.7,
                'unit': 'J/cm²'
            }
        }
        
        # Default should use nanosecond and return average
        value = generator._extract_property_value(pulse_specific)
        assert value == 5.0  # (2.0 + 8.0) / 2
    
    def test_extract_from_pulse_specific_picosecond(self, generator):
        """Test extracting picosecond value from pulse-specific format"""
        pulse_specific = {
            'nanosecond': {
                'min': 2.0,
                'max': 8.0,
                'unit': 'J/cm²'
            },
            'picosecond': {
                'min': 0.1,
                'max': 2.0,
                'unit': 'J/cm²'
            }
        }
        
        # Request picosecond specifically
        value = generator._extract_property_value(pulse_specific, prefer_pulse='picosecond')
        assert value == 1.05  # (0.1 + 2.0) / 2
    
    def test_extract_from_wavelength_specific_1064nm(self, generator):
        """Test extracting 1064nm value from wavelength-specific format"""
        wavelength_specific = {
            'at_1064nm': {
                'min': 85,
                'max': 98,
                'unit': '%'
            },
            'at_532nm': {
                'min': 70,
                'max': 95,
                'unit': '%'
            }
        }
        
        # Default should use 1064nm (most common Nd:YAG)
        value = generator._extract_property_value(wavelength_specific)
        assert value == 91.5  # (85 + 98) / 2
    
    def test_extract_from_wavelength_specific_532nm(self, generator):
        """Test extracting 532nm value from wavelength-specific format"""
        wavelength_specific = {
            'at_1064nm': {
                'min': 85,
                'max': 98,
                'unit': '%'
            },
            'at_532nm': {
                'min': 70,
                'max': 95,
                'unit': '%'
            }
        }
        
        # Request 532nm specifically
        value = generator._extract_property_value(wavelength_specific, prefer_wavelength='532nm')
        assert value == 82.5  # (70 + 95) / 2
    
    def test_extract_from_min_max_average(self, generator):
        """Test extracting average from min/max when no value field"""
        prop_with_range = {
            'unit': 'W/(m·K)',
            'confidence': 85,
            'min': 15,
            'max': 400,
            'source': 'MatWeb'
        }
        
        value = generator._extract_property_value(prop_with_range)
        assert value == 207.5  # (15 + 400) / 2
    
    def test_extract_simple_numeric(self, generator):
        """Test extracting from simple numeric value"""
        value = generator._extract_property_value(42)
        assert value == 42
    
    def test_extract_fallback_to_zero(self, generator):
        """Test fallback to zero when no value available"""
        empty_prop = {
            'unit': 'units',
            'description': 'Some property'
        }
        
        value = generator._extract_property_value(empty_prop)
        assert value == 0


class TestRealWorldData:
    """Test with real property data from frontmatter files"""
    
    @pytest.fixture
    def generator(self):
        """Create a generator instance for testing"""
        gen = StreamlinedFrontmatterGenerator.__new__(StreamlinedFrontmatterGenerator)
        return gen
    
    def test_copper_ablation_threshold(self, generator):
        """Test Copper's pulse-specific ablation threshold (from Priority 2 update)"""
        copper_ablation = {
            'nanosecond': {
                'min': 2.0,
                'max': 8.0,
                'unit': 'J/cm²'
            },
            'picosecond': {
                'min': 0.1,
                'max': 2.0,
                'unit': 'J/cm²'
            },
            'femtosecond': {
                'min': 0.14,
                'max': 1.7,
                'unit': 'J/cm²'
            },
            'source': 'Marks et al. 2022, Precision Engineering',
            'confidence': 90,
            'measurement_context': 'Varies by pulse duration (ns/ps/fs)'
        }
        
        # Verify pattern detection
        pattern = generator._detect_property_pattern(copper_ablation)
        assert pattern == 'pulse-specific'
        
        # Verify value extraction (nanosecond default)
        value = generator._extract_property_value(copper_ablation)
        assert value == 5.0
        
        # Verify femtosecond extraction
        fs_value = generator._extract_property_value(copper_ablation, prefer_pulse='femtosecond')
        assert abs(fs_value - 0.92) < 0.01  # (0.14 + 1.7) / 2 with floating point tolerance
    
    def test_copper_reflectivity(self, generator):
        """Test Copper's wavelength-specific reflectivity (from Priority 2 update)"""
        copper_reflectivity = {
            'at_1064nm': {
                'min': 85,
                'max': 98,
                'unit': '%'
            },
            'at_532nm': {
                'min': 70,
                'max': 95,
                'unit': '%'
            },
            'at_355nm': {
                'min': 55,
                'max': 85,
                'unit': '%'
            },
            'at_10640nm': {
                'min': 95,
                'max': 99,
                'unit': '%'
            },
            'source': 'Handbook of Optical Constants (Palik)',
            'confidence': 85,
            'measurement_context': 'Varies by laser wavelength'
        }
        
        # Verify pattern detection
        pattern = generator._detect_property_pattern(copper_reflectivity)
        assert pattern == 'wavelength-specific'
        
        # Verify value extraction (1064nm default)
        value = generator._extract_property_value(copper_reflectivity)
        assert value == 91.5
        
        # Verify CO2 wavelength extraction
        co2_value = generator._extract_property_value(copper_reflectivity, prefer_wavelength='10640nm')
        assert co2_value == 97.0  # (95 + 99) / 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
