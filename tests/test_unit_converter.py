#!/usr/bin/env python3
"""
Unit Converter Tests

Tests for the unit normalization system that fixes the electricalConductivity
validation bug and ensures accurate range checking across different units.

Bug Fixed: electricalConductivity = 37,700,000 S/m incorrectly compared to 70 MS/m
Solution: Normalize to 37.7 MS/m before comparison
"""

import pytest
from shared.validation.helpers.unit_converter import UnitConverter, UnitConversionError


class TestElectricalConductivity:
    """Test electrical conductivity conversions (primary bug fix)"""
    
    def test_siemens_to_megasiemens(self):
        """Test S/m to MS/m conversion (Aluminum case)"""
        # Aluminum: 37.7 MS/m = 37,700,000 S/m
        normalized, unit = UnitConverter.normalize(
            'electricalConductivity',
            37700000.0,
            'S/m'
        )
        assert normalized == pytest.approx(37.7, rel=1e-6)
        assert unit == 'MS/m'
    
    def test_iacs_to_megasiemens(self):
        """Test % IACS to MS/m conversion"""
        # 100% IACS = 58.1 MS/m (copper standard)
        normalized, unit = UnitConverter.normalize(
            'electricalConductivity',
            100.0,
            '% IACS'
        )
        assert normalized == pytest.approx(58.1, rel=1e-3)
        assert unit == 'MS/m'
    
    def test_scientific_notation(self):
        """Test ×10⁷ S/m to MS/m conversion"""
        # 3.77×10⁷ S/m = 37.7 MS/m
        normalized, unit = UnitConverter.normalize(
            'electricalConductivity',
            3.77,
            '×10⁷ S/m'
        )
        assert normalized == pytest.approx(37.7, rel=1e-3)
        assert unit == 'MS/m'
    
    def test_already_normalized(self):
        """Test MS/m to MS/m (no conversion needed)"""
        normalized, unit = UnitConverter.normalize(
            'electricalConductivity',
            37.7,
            'MS/m'
        )
        assert normalized == pytest.approx(37.7, rel=1e-6)
        assert unit == 'MS/m'
    
    def test_silver_conductivity(self):
        """Test highest conductivity (silver: 63 MS/m)"""
        # Silver: 63,000,000 S/m = 63 MS/m
        normalized, unit = UnitConverter.normalize(
            'electricalConductivity',
            63000000.0,
            'S/m'
        )
        assert normalized == pytest.approx(63.0, rel=1e-6)
        assert unit == 'MS/m'
    
    def test_copper_standard(self):
        """Test copper reference (58.1 MS/m = 100% IACS)"""
        normalized, unit = UnitConverter.normalize(
            'electricalConductivity',
            58100000.0,
            'S/m'
        )
        assert normalized == pytest.approx(58.1, rel=1e-3)
        assert unit == 'MS/m'


class TestDensity:
    """Test density conversions"""
    
    def test_kg_m3_to_g_cm3(self):
        """Test kg/m³ to g/cm³ conversion"""
        # Aluminum: 2700 kg/m³ = 2.7 g/cm³
        normalized, unit = UnitConverter.normalize(
            'density',
            2700.0,
            'kg/m³'
        )
        assert normalized == pytest.approx(2.7, rel=1e-6)
        assert unit == 'g/cm³'
    
    def test_already_normalized_density(self):
        """Test g/cm³ to g/cm³ (no conversion)"""
        normalized, unit = UnitConverter.normalize(
            'density',
            2.7,
            'g/cm³'
        )
        assert normalized == pytest.approx(2.7, rel=1e-6)
        assert unit == 'g/cm³'
    
    def test_alternate_unit_grams_cc(self):
        """Test g/cc (same as g/cm³)"""
        normalized, unit = UnitConverter.normalize(
            'density',
            8.96,
            'g/cc'
        )
        assert normalized == pytest.approx(8.96, rel=1e-6)
        assert unit == 'g/cm³'


class TestMechanicalProperties:
    """Test mechanical property conversions"""
    
    def test_youngs_modulus_mpa_to_gpa(self):
        """Test MPa to GPa conversion"""
        # Aluminum: 70,000 MPa = 70 GPa
        normalized, unit = UnitConverter.normalize(
            'youngsModulus',
            70000.0,
            'MPa'
        )
        assert normalized == pytest.approx(70.0, rel=1e-6)
        assert unit == 'GPa'
    
    def test_tensile_strength_gpa_to_mpa(self):
        """Test GPa to MPa conversion"""
        # 0.31 GPa = 310 MPa
        normalized, unit = UnitConverter.normalize(
            'tensileStrength',
            0.31,
            'GPa'
        )
        assert normalized == pytest.approx(310.0, rel=1e-3)
        assert unit == 'MPa'
    
    def test_hardness_mpa_to_gpa(self):
        """Test hardness MPa to GPa"""
        normalized, unit = UnitConverter.normalize(
            'hardness',
            2400.0,
            'MPa'
        )
        assert normalized == pytest.approx(2.4, rel=1e-6)
        assert unit == 'GPa'


class TestThermalProperties:
    """Test thermal property conversions"""
    
    def test_thermal_diffusivity_m2_to_mm2(self):
        """Test m²/s to mm²/s conversion"""
        # 9.71e-5 m²/s = 97.1 mm²/s
        normalized, unit = UnitConverter.normalize(
            'thermalDiffusivity',
            9.71e-5,
            'm²/s'
        )
        assert normalized == pytest.approx(97.1, rel=1e-3)
        assert unit == 'mm²/s'
    
    def test_thermal_diffusivity_cm2_to_mm2(self):
        """Test cm²/s to mm²/s conversion"""
        # 0.971 cm²/s = 97.1 mm²/s
        normalized, unit = UnitConverter.normalize(
            'thermalDiffusivity',
            0.971,
            'cm²/s'
        )
        assert normalized == pytest.approx(97.1, rel=1e-3)
        assert unit == 'mm²/s'


class TestErrorHandling:
    """Test error cases"""
    
    def test_unknown_unit(self):
        """Test error on unknown unit"""
        with pytest.raises(UnitConversionError) as exc_info:
            UnitConverter.normalize(
                'electricalConductivity',
                37.7,
                'invalid_unit'
            )
        assert 'Unknown unit' in str(exc_info.value)
        assert 'invalid_unit' in str(exc_info.value)
    
    def test_non_convertible_property(self):
        """Test property without conversion rules returns unchanged"""
        normalized, unit = UnitConverter.normalize(
            'unknownProperty',
            100.0,
            'some_unit'
        )
        assert normalized == 100.0
        assert unit == 'some_unit'
    
    def test_mohs_hardness_non_linear(self):
        """Test Mohs hardness raises error (non-linear scale)"""
        with pytest.raises(UnitConversionError) as exc_info:
            UnitConverter.normalize(
                'hardness',
                6.0,
                'Mohs'
            )
        assert 'non-linear' in str(exc_info.value).lower()


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_get_normalized_unit(self):
        """Test getting normalized unit for a property"""
        unit = UnitConverter.get_normalized_unit('electricalConductivity')
        assert unit == 'MS/m'
        
        unit = UnitConverter.get_normalized_unit('density')
        assert unit == 'g/cm³'
        
        unit = UnitConverter.get_normalized_unit('unknownProperty')
        assert unit is None
    
    def test_is_convertible(self):
        """Test checking if unit is convertible"""
        assert UnitConverter.is_convertible('electricalConductivity', 'S/m')
        assert UnitConverter.is_convertible('electricalConductivity', 'MS/m')
        assert not UnitConverter.is_convertible('electricalConductivity', 'invalid')
        assert UnitConverter.is_convertible('unknownProperty', 'any_unit')  # No rules = convertible
        assert not UnitConverter.is_convertible('hardness', 'Mohs')  # Non-linear


class TestRealWorldCases:
    """Test with real Materials.yaml data"""
    
    def test_aluminum_electrical_conductivity(self):
        """Test the original bug case: Aluminum electricalConductivity"""
        # Materials.yaml: value: 37700000.0, unit: "S/m"
        # Should normalize to 37.7 MS/m, which is < 70 MS/m (valid)
        normalized, unit = UnitConverter.normalize(
            'electricalConductivity',
            37700000.0,
            'S/m'
        )
        assert normalized == pytest.approx(37.7, rel=1e-6)
        assert normalized < 70.0  # Should pass validation
        assert unit == 'MS/m'
    
    def test_copper_electrical_conductivity(self):
        """Test copper (59.6 MS/m reference)"""
        # Copper: 59,600,000 S/m = 59.6 MS/m
        normalized, unit = UnitConverter.normalize(
            'electricalConductivity',
            59600000.0,
            'S/m'
        )
        assert normalized == pytest.approx(59.6, rel=1e-3)
        assert normalized < 70.0  # Should pass validation
    
    def test_steel_electrical_conductivity(self):
        """Test steel (10 MS/m typical)"""
        # Steel: 10,000,000 S/m = 10 MS/m
        normalized, unit = UnitConverter.normalize(
            'electricalConductivity',
            10000000.0,
            'S/m'
        )
        assert normalized == pytest.approx(10.0, rel=1e-3)
        assert normalized < 70.0  # Should pass validation


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_zero_value(self):
        """Test conversion of zero value"""
        normalized, unit = UnitConverter.normalize(
            'electricalConductivity',
            0.0,
            'S/m'
        )
        assert normalized == 0.0
        assert unit == 'MS/m'
    
    def test_very_large_value(self):
        """Test conversion of very large value"""
        normalized, unit = UnitConverter.normalize(
            'electricalConductivity',
            1e10,  # 10 billion S/m
            'S/m'
        )
        assert normalized == pytest.approx(1e4, rel=1e-6)  # 10,000 MS/m
        assert unit == 'MS/m'
    
    def test_very_small_value(self):
        """Test conversion of very small value"""
        normalized, unit = UnitConverter.normalize(
            'electricalConductivity',
            1e-6,  # 0.000001 S/m
            'S/m'
        )
        assert normalized == pytest.approx(1e-12, rel=1e-6)  # Very small MS/m
        assert unit == 'MS/m'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
