#!/usr/bin/env python3
"""
Research laser properties for all contamination patterns using AI.

Uses LaserPropertiesResearcher to populate complete laser property data
for all contamination patterns, with schema validation and YAML persistence.

Usage:
    python3 research_contamination_patterns.py --all
    python3 research_contamination_patterns.py --pattern rust_oxidation
    python3 research_contamination_patterns.py --pattern copper_patina --type optical
"""

import sys
import os
import yaml
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, '/Users/todddunning/Desktop/Z-Beam/z-beam-generator')

from domains.contaminants.data_loader_v2 import PatternDataLoader
from domains.contaminants.schema import (
    ContaminationPattern,
    LaserPropertyValue,
    OpticalProperties,
    ThermalProperties,
    RemovalCharacteristics,
    LayerProperties,
    LaserParameters,
    SafetyData,
    SelectivityRatios,
    ResearchConfidence
)
from domains.contaminants.research.laser_properties_researcher import LaserPropertiesResearcher
from shared.api.client_factory import APIClientFactory


class ContaminationPatternResearcher:
    """Orchestrates AI research for contamination pattern laser properties."""
    
    def __init__(self, api_client=None):
        self.loader = PatternDataLoader()
        
        # Initialize API client if not provided
        if api_client is None:
            factory = APIClientFactory()
            api_client = factory.create_client("grok")
        
        self.researcher = LaserPropertiesResearcher(api_client)
        self.contaminants_yaml_path = Path('/Users/todddunning/Desktop/Z-Beam/z-beam-generator/data/contaminants/Contaminants.yaml')
    
    def research_pattern(self, pattern_id: str, property_types: list = None) -> ContaminationPattern:
        """
        Research laser properties for a single pattern.
        
        Args:
            pattern_id: Pattern identifier
            property_types: List of property types to research, or None for all
        
        Returns:
            ContaminationPattern with researched properties
        """
        print(f"\n{'='*80}")
        print(f"🔬 RESEARCHING: {pattern_id}")
        print(f"{'='*80}")
        
        # Load existing pattern data
        pattern_data = self.loader.get_pattern(pattern_id)
        if not pattern_data:
            raise ValueError(f"Pattern not found: {pattern_id}")
        
        # Create typed pattern
        pattern = ContaminationPattern(
            pattern_id=pattern_id,
            name=pattern_data['name'],
            description=pattern_data['description'],
            composition=pattern_data.get('composition', [pattern_data.get('chemical_formula', 'Unknown')]),
            valid_materials=pattern_data.get('valid_materials', []),
            prohibited_materials=pattern_data.get('invalid_materials', [])
        )
        
        # Determine which properties to research
        if property_types is None:
            property_types = ['optical', 'thermal', 'removal', 'layer', 'parameters', 'safety', 'selectivity']
        
        # Research each property type
        for prop_type in property_types:
            print(f"\n  📊 Researching {prop_type} properties...")
            
            try:
                if prop_type == 'optical':
                    self._research_optical(pattern)
                elif prop_type == 'thermal':
                    self._research_thermal(pattern)
                elif prop_type == 'removal':
                    self._research_removal(pattern)
                elif prop_type == 'layer':
                    self._research_layer(pattern)
                elif prop_type == 'parameters':
                    self._research_parameters(pattern)
                elif prop_type == 'safety':
                    self._research_safety(pattern)
                elif prop_type == 'selectivity':
                    self._research_selectivity(pattern)
                
                print(f"     ✅ {prop_type.capitalize()} properties researched")
                
            except Exception as e:
                print(f"     ⚠️  Failed to research {prop_type}: {e}")
        
        # Add research metadata
        pattern.research_timestamp = datetime.utcnow().isoformat() + "Z"
        pattern.research_version = "1.0"
        
        # Validate pattern
        is_valid, errors = pattern.validate()
        if not is_valid:
            print(f"\n  ⚠️  VALIDATION WARNINGS:")
            for error in errors:
                print(f"     • {error}")
        
        # Show coverage
        coverage = pattern.get_laser_property_coverage()
        populated = sum(1 for v in coverage.values() if v)
        print(f"\n  📈 Coverage: {populated}/7 property types populated")
        
        return pattern
    
    def _research_optical(self, pattern: ContaminationPattern):
        """Research optical properties at common wavelengths."""
        wavelengths = ["1064nm", "532nm", "355nm"]
        
        for wavelength in wavelengths:
            # Use AI researcher to get absorption coefficient
            result = self.researcher.research_optical_properties(
                pattern.pattern_id,
                wavelength=wavelength
            )
            
            if result and 'absorption_coefficient' in result:
                optical = OpticalProperties(
                    wavelength=wavelength,
                    absorption_coefficient=LaserPropertyValue(
                        value=result['absorption_coefficient']['value'],
                        unit=result['absorption_coefficient'].get('unit', 'dimensionless'),
                        wavelength=wavelength,
                        confidence=ResearchConfidence.MEDIUM,
                        source="AI research (Grok API)"
                    )
                )
                
                # Add reflectivity if present
                if 'reflectivity' in result:
                    optical.reflectivity = LaserPropertyValue(
                        value=result['reflectivity']['value'],
                        unit=result['reflectivity'].get('unit', 'dimensionless'),
                        wavelength=wavelength,
                        confidence=ResearchConfidence.MEDIUM,
                        source="AI research (Grok API)"
                    )
                
                # Add transmittance if present
                if 'transmittance' in result:
                    optical.transmittance = LaserPropertyValue(
                        value=result['transmittance']['value'],
                        unit=result['transmittance'].get('unit', 'dimensionless'),
                        wavelength=wavelength,
                        confidence=ResearchConfidence.MEDIUM,
                        source="AI research (Grok API)"
                    )
                
                pattern.optical_properties_by_wavelength[wavelength] = optical
    
    def _research_thermal(self, pattern: ContaminationPattern):
        """Research thermal properties."""
        result = self.researcher.research_thermal_properties(pattern.pattern_id)
        
        if result:
            pattern.thermal_properties = ThermalProperties(
                ablation_threshold=LaserPropertyValue(
                    value=result.get('ablation_threshold', {}).get('value', 2.0),
                    unit="J/cm²",
                    min_value=result.get('ablation_threshold', {}).get('min', 1.0),
                    max_value=result.get('ablation_threshold', {}).get('max', 5.0),
                    confidence=ResearchConfidence.MEDIUM,
                    source="AI research (Grok API)"
                ) if 'ablation_threshold' in result else None,
                
                vaporization_temperature=LaserPropertyValue(
                    value=result.get('vaporization_temperature', {}).get('value', 1500),
                    unit="°C",
                    confidence=ResearchConfidence.MEDIUM,
                    source="AI research (Grok API)"
                ) if 'vaporization_temperature' in result else None
            )
    
    def _research_removal(self, pattern: ContaminationPattern):
        """Research removal characteristics."""
        result = self.researcher.research_removal_characteristics(pattern.pattern_id)
        
        if result:
            pattern.removal_characteristics = RemovalCharacteristics(
                removal_efficiency=LaserPropertyValue(
                    value=result.get('removal_efficiency', {}).get('value', 0.80),
                    unit="%",
                    confidence=ResearchConfidence.MEDIUM,
                    source="AI research (Grok API)"
                ) if 'removal_efficiency' in result else None,
                
                optimal_fluence_range=(
                    result.get('optimal_fluence', {}).get('min', 1.0),
                    result.get('optimal_fluence', {}).get('max', 5.0),
                    "J/cm²"
                ) if 'optimal_fluence' in result else None
            )
    
    def _research_layer(self, pattern: ContaminationPattern):
        """Research layer properties."""
        result = self.researcher.research_layer_properties(pattern.pattern_id)
        
        if result:
            pattern.layer_properties = LayerProperties(
                typical_thickness_range=(
                    result.get('thickness', {}).get('min', 1.0),
                    result.get('thickness', {}).get('max', 100.0),
                    "μm"
                ) if 'thickness' in result else None,
                
                layer_uniformity=result.get('uniformity', 'Variable')
            )
    
    def _research_parameters(self, pattern: ContaminationPattern):
        """Research recommended laser parameters."""
        result = self.researcher.research_laser_parameters(pattern.pattern_id)
        
        if result:
            pattern.laser_parameters = LaserParameters(
                wavelength_range=result.get('wavelengths', ["1064nm", "532nm"]),
                
                scan_speed_range=(
                    result.get('scan_speed', {}).get('min', 100.0),
                    result.get('scan_speed', {}).get('max', 500.0),
                    "mm/s"
                ) if 'scan_speed' in result else None
            )
    
    def _research_safety(self, pattern: ContaminationPattern):
        """Research safety data."""
        result = self.researcher.research_safety_data(pattern.pattern_id)
        
        if result:
            pattern.safety_data = SafetyData(
                fume_composition=result.get('fumes', []),
                toxicity_level=result.get('toxicity', 'Moderate'),
                ppe_requirements=result.get('ppe', ["Safety goggles", "Dust mask", "Ventilation"])
            )
    
    def _research_selectivity(self, pattern: ContaminationPattern):
        """Research selectivity ratios."""
        result = self.researcher.research_selectivity_ratios(pattern.pattern_id)
        
        if result:
            pattern.selectivity_ratios = SelectivityRatios(
                selectivity_index=LaserPropertyValue(
                    value=result.get('selectivity_index', {}).get('value', 1.5),
                    unit="dimensionless",
                    confidence=ResearchConfidence.LOW,
                    source="AI research (Grok API)",
                    notes="Higher values indicate better selectivity"
                ) if 'selectivity_index' in result else None
            )
    
    def save_pattern(self, pattern: ContaminationPattern, backup: bool = True):
        """
        Save researched pattern to Contaminants.yaml.
        
        Args:
            pattern: ContaminationPattern with researched properties
            backup: Whether to create backup before saving
        """
        print(f"\n{'='*80}")
        print(f"💾 SAVING: {pattern.pattern_id}")
        print(f"{'='*80}")
        
        # Create backup if requested
        if backup:
            backup_path = self.contaminants_yaml_path.with_suffix('.yaml.backup')
            import shutil
            shutil.copy2(self.contaminants_yaml_path, backup_path)
            print(f"  ✅ Backup created: {backup_path.name}")
        
        # Load existing YAML
        with open(self.contaminants_yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Update pattern data
        pattern_data = pattern.to_dict()
        data['contamination_patterns'][pattern.pattern_id] = pattern_data
        
        # Write back to YAML
        with open(self.contaminants_yaml_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, width=120)
        
        print(f"  ✅ Saved to: {self.contaminants_yaml_path.name}")
        
        # Verify
        is_valid, errors = pattern.validate()
        if is_valid:
            print(f"  ✅ Validation passed")
        else:
            print(f"  ⚠️  Validation warnings: {len(errors)}")
    
    def research_all_patterns(self, save: bool = True):
        """Research laser properties for all patterns."""
        pattern_ids = self.loader.get_pattern_ids()
        
        print(f"\n{'='*80}")
        print(f"🔬 RESEARCHING ALL PATTERNS ({len(pattern_ids)} total)")
        print(f"{'='*80}")
        
        results = []
        for i, pattern_id in enumerate(pattern_ids, 1):
            print(f"\n[{i}/{len(pattern_ids)}] {pattern_id}")
            
            try:
                pattern = self.research_pattern(pattern_id)
                results.append((pattern_id, True, pattern))
                
                if save:
                    self.save_pattern(pattern, backup=(i == 1))  # Backup only first save
                
            except Exception as e:
                print(f"  ❌ FAILED: {e}")
                results.append((pattern_id, False, None))
        
        # Summary
        print(f"\n{'='*80}")
        print(f"📊 RESEARCH COMPLETE")
        print(f"{'='*80}")
        
        successful = sum(1 for _, success, _ in results if success)
        print(f"  ✅ Successful: {successful}/{len(pattern_ids)}")
        print(f"  ❌ Failed: {len(pattern_ids) - successful}/{len(pattern_ids)}")
        
        if successful > 0:
            total_coverage = 0
            for pattern_id, success, pattern in results:
                if success and pattern:
                    coverage = pattern.get_laser_property_coverage()
                    populated = sum(1 for v in coverage.values() if v)
                    total_coverage += populated
            
            avg_coverage = total_coverage / successful
            print(f"  📈 Average coverage: {avg_coverage:.1f}/7 properties")
        
        return results


def main():
    """Main entry point for research script."""
    parser = argparse.ArgumentParser(
        description='Research laser properties for contamination patterns using AI'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Research all patterns'
    )
    parser.add_argument(
        '--pattern',
        type=str,
        help='Research specific pattern (e.g., rust_oxidation)'
    )
    parser.add_argument(
        '--type',
        type=str,
        choices=['optical', 'thermal', 'removal', 'layer', 'parameters', 'safety', 'selectivity'],
        help='Research only specific property type'
    )
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Skip saving results to YAML'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be researched without actually doing it'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.all and not args.pattern:
        parser.error("Either --all or --pattern must be specified")
    
    if args.pattern and args.all:
        parser.error("Cannot specify both --all and --pattern")
    
    # Create researcher
    researcher = ContaminationPatternResearcher()
    
    # Dry run
    if args.dry_run:
        loader = PatternDataLoader()
        patterns = loader.get_pattern_ids() if args.all else [args.pattern]
        print(f"\n🔍 DRY RUN - Would research {len(patterns)} pattern(s):")
        for pattern_id in patterns:
            print(f"  • {pattern_id}")
        return 0
    
    try:
        if args.all:
            # Research all patterns
            results = researcher.research_all_patterns(save=not args.no_save)
            return 0 if all(success for _, success, _ in results) else 1
        
        else:
            # Research single pattern
            property_types = [args.type] if args.type else None
            pattern = researcher.research_pattern(args.pattern, property_types)
            
            if not args.no_save:
                researcher.save_pattern(pattern)
            
            return 0
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
