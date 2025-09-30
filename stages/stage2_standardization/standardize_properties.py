#!/usr/bin/env python3
"""
Stage 2: Property Standardization
Standardizes property formats, units, and data structures based on defined schemas.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class PropertyStandardizer:
    """
    Standardizes material properties to ensure consistent formats,
    units, and data structures across all materials.
    """
    
    def __init__(self):
        self.frontmatter_dir = Path("content/components/frontmatter")
        self.categories_file = Path("data/Categories.yaml")
        self.config_file = Path("config/pipeline_config.yaml")
        
        # Load standardization rules
        self.standardization_rules = self._load_standardization_rules()
        self.unit_conversions = self._load_unit_conversions()
        
        # Statistics tracking
        self.standardization_stats = {
            'files_processed': 0,
            'properties_standardized': 0,
            'units_converted': 0,
            'structures_normalized': 0,
            'errors': []
        }
    
    def _load_standardization_rules(self) -> Dict[str, Any]:
        """Load standardization rules from configuration"""
        
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            return config.get('standardization', {
                'units': {
                    'density': 'g/cm³',
                    'meltingPoint': '°C',
                    'thermalConductivity': 'W/m·K',
                    'hardness': 'HV',
                    'youngsModulus': 'GPa',
                    'tensileStrength': 'MPa',
                    'thermalExpansion': '1/°C'
                },
                'precision': {
                    'density': 3,
                    'meltingPoint': 0,
                    'thermalConductivity': 2,
                    'hardness': 1,
                    'youngsModulus': 1,
                    'tensileStrength': 0
                },
                'required_fields': ['value', 'unit', 'min', 'max']
            })
            
        except Exception as e:
            print(f"⚠️  Could not load standardization rules: {e}")
            return self._get_default_standardization_rules()
    
    def _get_default_standardization_rules(self) -> Dict[str, Any]:
        """Default standardization rules if config file unavailable"""
        
        return {
            'units': {
                'density': 'g/cm³',
                'meltingPoint': '°C',
                'thermalConductivity': 'W/m·K',
                'hardness': 'HV',
                'youngsModulus': 'GPa',
                'tensileStrength': 'MPa',
                'thermalExpansion': '1/°C',
                'specificHeat': 'J/kg·K',
                'electricalResistivity': 'Ω·m',
                'poissonRatio': ''
            },
            'precision': {
                'density': 3,
                'meltingPoint': 0,
                'thermalConductivity': 2,
                'hardness': 1,
                'youngsModulus': 1,
                'tensileStrength': 0,
                'specificHeat': 0,
                'electricalResistivity': 6,
                'poissonRatio': 3
            },
            'required_fields': ['value', 'unit', 'min', 'max'],
            'optional_fields': ['confidence', 'description', 'source']
        }
    
    def _load_unit_conversions(self) -> Dict[str, Dict[str, float]]:
        """Load unit conversion factors"""
        
        return {
            'density': {
                'kg/m³': 0.001,  # to g/cm³
                'g/ml': 1.0,     # to g/cm³
                'kg/l': 1.0,     # to g/cm³
                'g/cm³': 1.0     # already correct
            },
            'temperature': {
                'K': lambda k: k - 273.15,      # Kelvin to Celsius
                'F': lambda f: (f - 32) * 5/9,  # Fahrenheit to Celsius
                '°C': lambda c: c,               # already correct
                'C': lambda c: c                 # already correct
            },
            'pressure': {
                'Pa': 1e-6,      # to MPa
                'kPa': 1e-3,     # to MPa
                'GPa': 1000,     # to MPa
                'MPa': 1.0       # already correct
            },
            'thermal_conductivity': {
                'W/mK': 1.0,     # already correct
                'W/m·K': 1.0,    # already correct
                'W/m-K': 1.0,    # alternative notation
                'cal/cm·s·°C': 418.4  # to W/m·K
            }
        }
    
    def standardize_materials(self, materials_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Standardize all material properties according to defined standards.
        
        Args:
            materials_filter: Optional list of specific materials to process
            
        Returns:
            Standardization results with statistics and changes made
        """
        
        print("🔧 Starting property standardization process...")
        
        standardization_results = []
        changes_made = []
        
        for yaml_file in self.frontmatter_dir.glob("*.yaml"):
            material_name = yaml_file.stem.replace("-laser-cleaning", "")
            
            # Apply materials filter if provided
            if materials_filter and material_name not in materials_filter:
                continue
            
            try:
                # Load material data
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                original_data = data.copy()
                
                # Standardize material properties
                if 'materialProperties' in data:
                    material_changes = self._standardize_material_properties(
                        material_name, 
                        data['materialProperties']
                    )
                    
                    # Track changes
                    if material_changes:
                        changes_made.extend(material_changes)
                        
                        # Save standardized data
                        self._save_standardized_material(yaml_file, data)
                
                # Create result record
                result = {
                    'material': material_name,
                    'category': data.get('category', 'unknown'),
                    'properties_processed': len(data.get('materialProperties', {})),
                    'changes_made': len([c for c in material_changes if c['material'] == material_name]),
                    'status': 'success'
                }
                
                standardization_results.append(result)
                self.standardization_stats['files_processed'] += 1
                
            except Exception as e:
                error_msg = f"Error standardizing {material_name}: {e}"
                self.standardization_stats['errors'].append(error_msg)
                print(f"❌ {error_msg}")
                
                standardization_results.append({
                    'material': material_name,
                    'status': 'error',
                    'error': str(e)
                })
        
        print(f"✅ Standardization complete: {self.standardization_stats['files_processed']} files processed")
        print(f"🔧 {len(changes_made)} properties standardized")
        
        return {
            'results': standardization_results,
            'changes': changes_made,
            'statistics': self.standardization_stats,
            'summary': self._generate_standardization_summary(standardization_results, changes_made)
        }
    
    def _standardize_material_properties(self, material_name: str, properties: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Standardize all properties for a single material"""
        
        changes = []
        
        for prop_name, prop_data in properties.items():
            try:
                # Standardize individual property
                standardized_prop, property_changes = self._standardize_property(
                    material_name, prop_name, prop_data
                )
                
                # Update the property data
                properties[prop_name] = standardized_prop
                
                # Track changes
                changes.extend(property_changes)
                
            except Exception as e:
                error_msg = f"Error standardizing {prop_name} for {material_name}: {e}"
                self.standardization_stats['errors'].append(error_msg)
                print(f"⚠️  {error_msg}")
        
        return changes
    
    def _standardize_property(self, material_name: str, prop_name: str, prop_data: Any) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Standardize a single property according to rules"""
        
        changes = []
        
        # Handle simple values (convert to structured format)
        if not isinstance(prop_data, dict):
            prop_data = self._convert_simple_value_to_structure(prop_name, prop_data)
            changes.append({
                'material': material_name,
                'property': prop_name,
                'change_type': 'structure_normalized',
                'description': 'Converted simple value to structured format',
                'old_format': 'simple_value',
                'new_format': 'structured'
            })
            self.standardization_stats['structures_normalized'] += 1
        
        # Ensure property has required structure
        standardized_prop = dict(prop_data)
        
        # Standardize units
        if 'unit' in standardized_prop:
            new_unit, unit_changed = self._standardize_unit(prop_name, standardized_prop['unit'])
            if unit_changed:
                # Convert value to new unit
                old_value = standardized_prop.get('value')
                new_value = self._convert_value_to_unit(prop_name, old_value, standardized_prop['unit'], new_unit)
                
                standardized_prop['unit'] = new_unit
                standardized_prop['value'] = new_value
                
                # Update ranges if they exist
                if 'min' in standardized_prop:
                    standardized_prop['min'] = self._convert_value_to_unit(
                        prop_name, standardized_prop['min'], prop_data['unit'], new_unit
                    )
                
                if 'max' in standardized_prop:
                    standardized_prop['max'] = self._convert_value_to_unit(
                        prop_name, standardized_prop['max'], prop_data['unit'], new_unit
                    )
                
                changes.append({
                    'material': material_name,
                    'property': prop_name,
                    'change_type': 'unit_standardized',
                    'description': f'Unit converted from {prop_data["unit"]} to {new_unit}',
                    'old_unit': prop_data['unit'],
                    'new_unit': new_unit,
                    'old_value': old_value,
                    'new_value': new_value
                })
                self.standardization_stats['units_converted'] += 1
        
        # Standardize precision
        if 'value' in standardized_prop and prop_name in self.standardization_rules['precision']:
            precision = self.standardization_rules['precision'][prop_name]
            old_value = standardized_prop['value']
            
            if isinstance(old_value, (int, float)):
                new_value = round(float(old_value), precision)
                if new_value != old_value:
                    standardized_prop['value'] = new_value
                    changes.append({
                        'material': material_name,
                        'property': prop_name,
                        'change_type': 'precision_standardized',
                        'description': f'Value precision set to {precision} decimal places',
                        'old_value': old_value,
                        'new_value': new_value
                    })
        
        # Ensure required fields exist
        required_fields = self.standardization_rules.get('required_fields', [])
        for field in required_fields:
            if field not in standardized_prop:
                if field == 'unit' and prop_name in self.standardization_rules['units']:
                    standardized_prop[field] = self.standardization_rules['units'][prop_name]
                    changes.append({
                        'material': material_name,
                        'property': prop_name,
                        'change_type': 'missing_field_added',
                        'description': f'Added missing {field}',
                        'field': field,
                        'value': standardized_prop[field]
                    })
        
        # Add confidence if missing
        if 'confidence' not in standardized_prop:
            standardized_prop['confidence'] = self._estimate_confidence(prop_name, standardized_prop)
            changes.append({
                'material': material_name,
                'property': prop_name,
                'change_type': 'confidence_estimated',
                'description': 'Added estimated confidence score',
                'confidence': standardized_prop['confidence']
            })
        
        self.standardization_stats['properties_standardized'] += 1
        
        return standardized_prop, changes
    
    def _convert_simple_value_to_structure(self, prop_name: str, simple_value: Any) -> Dict[str, Any]:
        """Convert simple value to structured property format"""
        
        structured = {
            'value': simple_value,
            'unit': self.standardization_rules['units'].get(prop_name, 'unknown'),
            'confidence': 0.7  # Default confidence for converted values
        }
        
        # Try to estimate reasonable ranges based on the value
        if isinstance(simple_value, (int, float)):
            value = float(simple_value)
            structured['min'] = round(value * 0.8, 2)
            structured['max'] = round(value * 1.2, 2)
        
        return structured
    
    def _standardize_unit(self, prop_name: str, current_unit: str) -> Tuple[str, bool]:
        """Standardize unit for a property"""
        
        standard_unit = self.standardization_rules['units'].get(prop_name)
        
        if not standard_unit:
            return current_unit, False
        
        # Check if unit is already standardized
        if current_unit == standard_unit:
            return current_unit, False
        
        # Check for common variations
        unit_variations = {
            'g/cm³': ['g/cm3', 'g/cc', 'g/ml'],
            '°C': ['C', 'deg C', 'degrees C'],
            'W/m·K': ['W/mK', 'W/m-K', 'W/m*K'],
            'MPa': ['N/mm²', 'N/mm2', 'mega Pa'],
            'GPa': ['GN/m²', 'GN/m2', 'giga Pa']
        }
        
        for standard, variations in unit_variations.items():
            if current_unit in variations and standard_unit == standard:
                return standard_unit, True
        
        return standard_unit, True
    
    def _convert_value_to_unit(self, prop_name: str, value: Any, from_unit: str, to_unit: str) -> Any:
        """Convert value between units"""
        
        if not isinstance(value, (int, float)) or value is None:
            return value
        
        # Handle temperature conversions (special case with functions)
        if prop_name in ['meltingPoint', 'temperature'] and 'temperature' in self.unit_conversions:
            temp_conversions = self.unit_conversions['temperature']
            if from_unit in temp_conversions and to_unit == '°C':
                conversion_func = temp_conversions[from_unit]
                if callable(conversion_func):
                    return round(conversion_func(value), 1)
        
        # Handle other property conversions
        property_mapping = {
            'density': 'density',
            'tensileStrength': 'pressure',
            'youngsModulus': 'pressure',
            'thermalConductivity': 'thermal_conductivity'
        }
        
        conversion_category = property_mapping.get(prop_name)
        if conversion_category and conversion_category in self.unit_conversions:
            conversions = self.unit_conversions[conversion_category]
            
            if from_unit in conversions and to_unit in conversions:
                # Convert to base unit then to target
                base_value = value / conversions[from_unit]
                return round(base_value * conversions[to_unit], 4)
        
        # If no conversion available, return original value
        return value
    
    def _estimate_confidence(self, prop_name: str, prop_data: Dict[str, Any]) -> float:
        """Estimate confidence score for a property"""
        
        confidence = 0.5  # Base confidence
        
        # Higher confidence for complete data
        if all(field in prop_data for field in ['value', 'unit', 'min', 'max']):
            confidence += 0.2
        
        # Higher confidence for critical properties
        critical_properties = ['density', 'meltingPoint', 'thermalConductivity']
        if prop_name in critical_properties:
            confidence += 0.1
        
        # Higher confidence for numeric values
        if isinstance(prop_data.get('value'), (int, float)):
            confidence += 0.1
        
        # Higher confidence if ranges are reasonable
        value = prop_data.get('value')
        min_val = prop_data.get('min')
        max_val = prop_data.get('max')
        
        if all(isinstance(v, (int, float)) for v in [value, min_val, max_val]):
            if min_val <= value <= max_val:
                confidence += 0.1
        
        return round(min(confidence, 1.0), 2)
    
    def _save_standardized_material(self, yaml_file: Path, data: Dict[str, Any]):
        """Save standardized material data back to file"""
        
        try:
            # Create backup
            backup_dir = Path("backups/standardization")
            backup_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"{yaml_file.stem}_backup_{timestamp}.yaml"
            
            # Copy original to backup
            with open(yaml_file, 'r') as f:
                original_content = f.read()
            with open(backup_file, 'w') as f:
                f.write(original_content)
            
            # Save standardized version
            with open(yaml_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            
        except Exception as e:
            print(f"⚠️  Could not save standardized data for {yaml_file}: {e}")
    
    def _generate_standardization_summary(self, results: List[Dict[str, Any]], changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive summary of standardization results"""
        
        successful_materials = [r for r in results if r.get('status') == 'success']
        failed_materials = [r for r in results if r.get('status') == 'error']
        
        # Analyze change types
        change_types = {}
        for change in changes:
            change_type = change.get('change_type', 'unknown')
            change_types[change_type] = change_types.get(change_type, 0) + 1
        
        # Properties with most changes
        property_changes = {}
        for change in changes:
            prop = change.get('property', 'unknown')
            property_changes[prop] = property_changes.get(prop, 0) + 1
        
        top_changed_properties = sorted(property_changes.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'materials_processed': len(results),
            'successful_standardizations': len(successful_materials),
            'failed_standardizations': len(failed_materials),
            'total_changes': len(changes),
            'change_types': change_types,
            'top_changed_properties': top_changed_properties,
            'error_rate': len(failed_materials) / len(results) if results else 0,
            'standardization_rate': len(changes) / max(1, sum(r.get('properties_processed', 0) for r in successful_materials))
        }

def main():
    """Test the standardization functionality"""
    
    standardizer = PropertyStandardizer()
    
    # Run standardization
    results = standardizer.standardize_materials()
    
    # Save results
    results_dir = Path("pipeline_results")
    results_dir.mkdir(exist_ok=True)
    
    with open(results_dir / "stage2_standardization_results.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n" + "="*60)
    print("🔧 STANDARDIZATION STAGE COMPLETE")
    print("="*60)
    print(f"Materials processed: {results['summary']['materials_processed']}")
    print(f"Total changes made: {results['summary']['total_changes']}")
    print(f"Success rate: {(1 - results['summary']['error_rate']):.1%}")
    
    print("\nTop change types:")
    for change_type, count in results['summary']['change_types'].items():
        print(f"  🔧 {change_type}: {count}")

if __name__ == "__main__":
    main()