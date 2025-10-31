#!/usr/bin/env python3
"""
Relationship Validation Helpers

Extracted from PreGenerationValidationService to reduce code bloat.
Contains relationship validation logic for properties that depend on each other.
"""

from typing import Dict, List
from shared.validation.errors import ValidationError as VError, ErrorSeverity, ErrorType


class RelationshipValidators:
    """Static validation methods for inter-property relationships"""
    
    @staticmethod
    def validate_optical_energy(material: str, category: str, props: Dict) -> List[Dict]:
        """Validate A + R ≤ 100% (conservation of energy)"""
        issues = []
        
        absorption = props.get('laserAbsorption', {}).get('value')
        reflectivity = props.get('laserReflectivity', {}).get('value')
        
        if absorption is None or reflectivity is None:
            return issues
        
        try:
            A = float(absorption)
            R = float(reflectivity)
            total = A + R
            
            # Increased tolerance to 130% to account for:
            # - Measurement uncertainty (±5-10%)
            # - Non-ideal surface conditions
            # - Multiple scattering effects
            # - Wavelength-dependent measurements
            if total > 130:
                issues.append({
                    'severity': 'ERROR',
                    'type': 'optical_sum_high',
                    'material': material,
                    'category': category,
                    'absorption': A,
                    'reflectivity': R,
                    'sum': total,
                    'message': f"A + R = {total:.1f}% > 130% (exceeds physical limits with measurement uncertainty)"
                })
            elif total < 80:
                issues.append({
                    'severity': 'WARNING',
                    'type': 'optical_sum_low',
                    'material': material,
                    'category': category,
                    'absorption': A,
                    'reflectivity': R,
                    'sum': total,
                    'message': f"A + R = {total:.1f}% < 80% (may have transmittance)"
                })
        except (ValueError, TypeError):
            pass
        
        return issues
    
    @staticmethod
    def validate_thermal_diffusivity(material: str, category: str, props: Dict) -> List[Dict]:
        """Validate α = k / (ρ × Cp)"""
        issues = []
        
        alpha = props.get('thermalDiffusivity', {}).get('value')
        k = props.get('thermalConductivity', {}).get('value')
        cp = props.get('specificHeat', {}).get('value')
        rho = props.get('density', {}).get('value')
        
        if any(v is None for v in [alpha, k, cp, rho]):
            return issues
        
        try:
            alpha_measured = float(alpha)
            k_val = float(k)
            cp_val = float(cp)
            rho_val = float(rho) * 1000  # g/cm³ to kg/m³
            
            # Calculate expected: α = k / (ρ × Cp) × 10^6 (mm²/s)
            alpha_calculated = (k_val / (rho_val * cp_val)) * 1e6
            
            error_percent = abs(alpha_calculated - alpha_measured) / alpha_calculated * 100
            
            if error_percent > 20:
                issues.append({
                    'severity': 'ERROR',
                    'type': 'formula_violation',
                    'material': material,
                    'category': category,
                    'property': 'thermalDiffusivity',
                    'measured': alpha_measured,
                    'calculated': alpha_calculated,
                    'error_percent': error_percent,
                    'message': f"α measured {alpha_measured:.2f} vs calculated {alpha_calculated:.2f} mm²/s ({error_percent:.1f}% error)"
                })
        except (ValueError, TypeError, ZeroDivisionError):
            pass
        
        return issues
    
    @staticmethod
    def validate_youngs_tensile_ratio(material: str, category: str, props: Dict) -> List[Dict]:
        """Validate E/TS ratio is physically reasonable"""
        issues = []
        
        E = props.get('youngsModulus', {}).get('value')
        TS = props.get('tensileStrength', {}).get('value')
        
        if E is None or TS is None:
            return issues
        
        try:
            E_val = float(E)
            TS_val = float(TS)
            
            E_MPa = E_val * 1000
            ratio = E_MPa / TS_val if TS_val > 0 else float('inf')
            
            # Category-specific expected ranges
            category_ranges = {
                'metal': (100, 500),
                'ceramic': (500, 2000),
                'stone': (500, 15000),
                'glass': (500, 3000),
                'wood': (50, 300),
                'plastic': (30, 200),
                'composite': (30, 500),
                'semiconductor': (100, 1000),
                'masonry': (500, 10000)
            }
            
            expected_range = category_ranges.get(category, (50, 500))
            min_ratio, max_ratio = expected_range
            
            if ratio > max_ratio:
                issues.append({
                    'severity': 'ERROR',
                    'type': 'ratio_too_high',
                    'material': material,
                    'category': category,
                    'E_GPa': E_val,
                    'TS_MPa': TS_val,
                    'ratio': ratio,
                    'expected_range': expected_range,
                    'message': f"E/TS ratio {ratio:.1f} > {max_ratio} (exceeds {category} range)"
                })
            elif ratio < min_ratio:
                issues.append({
                    'severity': 'WARNING',
                    'type': 'ratio_too_low',
                    'material': material,
                    'category': category,
                    'E_GPa': E_val,
                    'TS_MPa': TS_val,
                    'ratio': ratio,
                    'expected_range': expected_range,
                    'message': f"E/TS ratio {ratio:.1f} < {min_ratio} (unusually low for {category})"
                })
        except (ValueError, TypeError, ZeroDivisionError):
            pass
        
        return issues
    
    @staticmethod
    def validate_two_category_system(material: str, material_properties: Dict) -> List[VError]:
        """
        Validate that frontmatter uses only the two-category system.
        
        Per system requirements:
        - ONLY two categories allowed: laser_material_interaction, material_characteristics
        - 'other' category is STRICTLY FORBIDDEN (ERROR severity)
        - Both categories should be present (WARNING if missing)
        
        Args:
            material: Material name
            material_properties: Dictionary with category keys
        
        Returns:
            List of ValidationError objects
        """
        errors = []
        
        ALLOWED_CATEGORIES = {'laser_material_interaction', 'material_characteristics'}
        found_categories = set(material_properties.keys())
        
        # Check for 'other' category (strictly forbidden)
        if 'other' in found_categories:
            errors.append(VError(
                severity=ErrorSeverity.ERROR,
                error_type=ErrorType.FORBIDDEN_CATEGORY,
                message="FORBIDDEN: 'other' category found. System uses ONLY two categories: laser_material_interaction and material_characteristics",
                material=material,
                category='other',
                suggestion="Move properties to laser_material_interaction or material_characteristics"
            ))
        
        # Check for any invalid categories
        invalid_categories = found_categories - ALLOWED_CATEGORIES
        for invalid_cat in invalid_categories:
            if invalid_cat != 'other':  # Already reported
                errors.append(VError(
                    severity=ErrorSeverity.ERROR,
                    error_type=ErrorType.INCORRECT_CATEGORIZATION,
                    message=f"Invalid category '{invalid_cat}'. Only 'laser_material_interaction' and 'material_characteristics' allowed",
                    material=material,
                    category=invalid_cat,
                    suggestion="Use only the two allowed categories"
                ))
        
        # Check both required categories exist
        if 'laser_material_interaction' not in found_categories:
            errors.append(VError(
                severity=ErrorSeverity.WARNING,
                error_type=ErrorType.MISSING_CATEGORY,
                message="Missing required category 'laser_material_interaction'",
                material=material,
                category='laser_material_interaction',
                suggestion="Add laser-material interaction properties"
            ))
        
        if 'material_characteristics' not in found_categories:
            errors.append(VError(
                severity=ErrorSeverity.WARNING,
                error_type=ErrorType.MISSING_CATEGORY,
                message="Missing required category 'material_characteristics'",
                material=material,
                category='material_characteristics',
                suggestion="Add material characteristics properties"
            ))
        
        return errors
