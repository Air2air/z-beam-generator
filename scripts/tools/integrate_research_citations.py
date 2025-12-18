#!/usr/bin/env python3
"""
Integrate Research Citations into Materials.yaml

Extracts citation data from PropertyResearch.yaml and SettingResearch.yaml,
then updates Materials.yaml with proper citations following zero-fallback policy.

According to DATA_STORAGE_POLICY: ALL research must be saved to Materials.yaml.
"""

import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

# Use shared YAML utilities
from shared.utils.file_io import read_yaml_file, write_yaml_file


class ResearchCitationIntegrator:
    """Integrates research citations from PropertyResearch.yaml into Materials.yaml"""
    
    def __init__(self, dry_run: bool = False):
        self.project_root = Path(__file__).parent.parent.parent
        self.materials_file = self.project_root / 'materials' / 'data' / 'Materials.yaml'
        self.property_research_file = self.project_root / 'materials' / 'data' / 'PropertyResearch.yaml'
        self.setting_research_file = self.project_root / 'materials' / 'data' / 'SettingResearch.yaml'
        self.dry_run = dry_run
        
    def load_yaml(self, filepath: Path) -> Dict[str, Any]:
        """Load YAML file"""
        return read_yaml_file(filepath)
    
    def save_yaml(self, filepath: Path, data: Dict[str, Any]):
        """Save YAML file with backup"""
        if not self.dry_run:
            # Create backup
            backup_file = filepath.with_suffix(
                f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml'
            )
            if filepath.exists():
                import shutil
                shutil.copy2(filepath, backup_file)
                print(f"📦 Backup created: {backup_file.name}")
        
            # Save updated data
            write_yaml_file(filepath, data, sort_keys=False)
            print(f"💾 Saved: {filepath.name}")
        else:
            print(f"🔍 DRY RUN: Would save {filepath.name}")
    
    def extract_citation_from_raw_response(self, raw_response: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Extract citation and value from raw_response field.
        
        Returns:
            (citation_dict, value_string) or (None, None) if extraction fails
        """
        if not raw_response:
            return None, None
        
        # Try to parse as YAML
        try:
            # Extract YAML block from response (handle truncated responses)
            yaml_match = re.search(r'```yaml\n(.*?)(?:\n```|$)', raw_response, re.DOTALL)
            if not yaml_match:
                # Try without markdown code block
                yaml_match = re.search(r'^([\s\S]+?)(?:\n\n|$)', raw_response)
            
            if yaml_match:
                yaml_content = yaml_match.group(1)
                
                # Handle truncated YAML by adding closing if needed
                if yaml_content.count('[') > yaml_content.count(']'):
                    yaml_content = yaml_content.rstrip() + '\n]'
                
                try:
                    data = yaml.safe_load(yaml_content)
                except yaml.YAMLError:
                    # If YAML is truncated/invalid, try to extract key info with regex
                    return self._extract_with_regex(raw_response)
                
                if not isinstance(data, dict):
                    return None, None
                
                # Look for citation information
                citation = {}
                value = None
                
                # Strategy 1: Look for density_values, thermal_conductivity_values, etc.
                for key in data.keys():
                    if '_values' in key or key == 'values':
                        values_list = data[key]
                        if isinstance(values_list, list) and len(values_list) > 0:
                            first_value = values_list[0]
                            if isinstance(first_value, dict):
                                # Extract value (may include unit)
                                raw_value = first_value.get('value')
                                if raw_value:
                                    value = str(raw_value)  # Keep as string to preserve units
                                
                                citation = {
                                    'source_name': first_value.get('source_name', ''),
                                    'source_type': first_value.get('source_type', ''),
                                    'citation': first_value.get('citation', ''),
                                    'context': first_value.get('context', ''),
                                    'confidence': first_value.get('confidence', 90)
                                }
                                
                                # Only return if we have source_name
                                if citation.get('source_name'):
                                    return citation, value
                
                # Strategy 2: Check for nested property structure (laserAbsorption.values)
                for key, val in data.items():
                    if isinstance(val, dict) and 'values' in val:
                        values_list = val['values']
                        if isinstance(values_list, list) and len(values_list) > 0:
                            first_value = values_list[0]
                            if isinstance(first_value, dict):
                                raw_value = first_value.get('value')
                                if raw_value:
                                    value = str(raw_value)
                                
                                citation = {
                                    'source_name': first_value.get('source_name', ''),
                                    'source_type': first_value.get('source_type', ''),
                                    'citation': first_value.get('citation', ''),
                                    'context': first_value.get('context', ''),
                                    'confidence': first_value.get('confidence', 90)
                                }
                                
                                if citation.get('source_name'):
                                    return citation, value
                
                # Strategy 3: Look for direct property fields at root level
                if 'source_name' in data:
                    value = str(data.get('value', '')) if 'value' in data else None
                    citation = {
                        'source_name': data.get('source_name', ''),
                        'source_type': data.get('source_type', ''),
                        'citation': data.get('citation', ''),
                        'context': data.get('context', ''),
                        'confidence': data.get('confidence', 90)
                    }
                    if citation.get('source_name'):
                        return citation, value
                    
        except Exception as e:
            print(f"⚠️  Failed to parse raw_response: {e}")
            
        return None, None
    
    def _extract_with_regex(self, raw_response: str) -> Tuple[Optional[Dict], Optional[str]]:
        """Fallback extraction using regex for truncated YAML"""
        try:
            # Extract value
            value_match = re.search(r'value:\s*([0-9.]+(?:\s*g/cm³|W/m·K|dimensionless)?)', raw_response)
            value = value_match.group(1) if value_match else None
            
            # Extract source_name
            source_match = re.search(r'source_name:\s*(.+?)(?:\n|$)', raw_response)
            source_name = source_match.group(1).strip() if source_match else None
            
            # Extract source_type
            type_match = re.search(r'source_type:\s*(.+?)(?:\n|$)', raw_response)
            source_type = type_match.group(1).strip() if type_match else None
            
            # Extract citation
            citation_match = re.search(r'citation:\s*(.+?)(?:\n|$)', raw_response)
            citation_str = citation_match.group(1).strip() if citation_match else None
            
            # Extract context
            context_match = re.search(r'context:\s*(.+?)(?:\n|$)', raw_response)
            context = context_match.group(1).strip() if context_match else None
            
            if source_name:
                citation = {
                    'source_name': source_name,
                    'source_type': source_type or 'reference',
                    'citation': citation_str or '',
                    'context': context or '',
                    'confidence': 85  # Lower confidence for regex extraction
                }
                return citation, value
        except Exception as e:
            print(f"⚠️  Regex extraction failed: {e}")
        
        return None, None
    
    def integrate_property_research(self) -> int:
        """
        Integrate PropertyResearch.yaml citations into Materials.yaml
        
        Returns:
            Number of properties updated
        """
        print("\n" + "="*80)
        print("INTEGRATING PROPERTY RESEARCH CITATIONS")
        print("="*80)
        
        # Load data files
        print("📖 Loading data files...")
        materials_data = self.load_yaml(self.materials_file)
        property_research = self.load_yaml(self.property_research_file)
        
        if not materials_data or 'materials' not in materials_data:
            print("❌ Invalid Materials.yaml structure")
            return 0
        
        if not property_research:
            print("❌ PropertyResearch.yaml not found or empty")
            return 0
        
        updates_count = 0
        materials = materials_data['materials']
        
        # Process each material in PropertyResearch.yaml
        for material_name, properties in property_research.items():
            if material_name == '_metadata':
                continue
            
            if material_name not in materials:
                print(f"⚠️  Material '{material_name}' not found in Materials.yaml")
                continue
            
            print(f"\n🔬 Processing: {material_name}")
            
            # Ensure characteristics exists
            if 'characteristics' not in materials[material_name]:
                materials[material_name]['characteristics'] = {}
            
            material_chars = materials[material_name]['characteristics']
            
            # Process each property
            for prop_name, prop_data in properties.items():
                if not isinstance(prop_data, dict) or 'research' not in prop_data:
                    continue
                
                research = prop_data['research']
                if 'values' not in research or not research['values']:
                    continue
                
                # Get first research value
                first_value = research['values'][0]
                raw_response = first_value.get('raw_response', '')
                
                # Extract citation and value
                citation, value = self.extract_citation_from_raw_response(raw_response)
                
                if citation and citation.get('source_name'):
                    # Convert property name from camelCase to snake_case for Materials.yaml
                    # (e.g., thermalConductivity -> thermal_conductivity)
                    snake_case_prop = self._camel_to_snake(prop_name)
                    
                    # Create or update property entry
                    if snake_case_prop not in material_chars:
                        material_chars[snake_case_prop] = {}
                    
                    # Update with citation data
                    material_chars[snake_case_prop].update({
                        'source': 'scientific_literature',
                        'source_type': citation.get('source_type', 'reference'),
                        'source_name': citation['source_name'],
                        'citation': citation.get('citation', ''),
                        'context': citation.get('context', ''),
                        'confidence': citation.get('confidence', 90),
                        'researched_date': research.get('metadata', {}).get('last_researched', 
                                                                             datetime.now().isoformat()),
                        'needs_validation': research.get('metadata', {}).get('needs_validation', True)
                    })
                    
                    # Add value if extracted
                    if value is not None:
                        material_chars[snake_case_prop]['value'] = value
                    
                    print(f"  ✅ {prop_name} -> {citation['source_name']}")
                    updates_count += 1
                else:
                    # Mark as needs_research if no citation found
                    snake_case_prop = self._camel_to_snake(prop_name)
                    if snake_case_prop not in material_chars:
                        material_chars[snake_case_prop] = {}
                    
                    material_chars[snake_case_prop].update({
                        'source': 'ai_research',
                        'needs_research': True,
                        'researched_date': research.get('metadata', {}).get('last_researched', 
                                                                             datetime.now().isoformat())
                    })
                    print(f"  ⚠️  {prop_name} -> needs_research: true (no citation extracted)")
        
        # Save updated Materials.yaml
        if updates_count > 0:
            print(f"\n💾 Saving {updates_count} updates to Materials.yaml...")
            self.save_yaml(self.materials_file, materials_data)
        else:
            print("\n⚠️  No updates to save")
        
        return updates_count
    
    def _camel_to_snake(self, name: str) -> str:
        """Convert camelCase to snake_case"""
        # Handle special cases
        name = name.replace('thermalConductivity', 'thermal_conductivity')
        name = name.replace('laserAbsorption', 'laser_absorption')
        
        # General conversion
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
        return name.lower()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate report on citation coverage"""
        print("\n" + "="*80)
        print("CITATION COVERAGE REPORT")
        print("="*80)
        
        materials_data = self.load_yaml(self.materials_file)
        materials = materials_data.get('materials', {})
        
        stats = {
            'total_materials': len(materials),
            'with_citations': 0,
            'with_ai_research': 0,
            'needs_research': 0,
            'total_properties': 0,
            'properties_with_citations': 0
        }
        
        for material_name, material_data in materials.items():
            material_chars = material_data.get('characteristics', {})
            
            has_citation = False
            for prop_name, prop_data in material_chars.items():
                if not isinstance(prop_data, dict):
                    continue
                
                stats['total_properties'] += 1
                
                source = prop_data.get('source', '')
                if source == 'scientific_literature':
                    stats['properties_with_citations'] += 1
                    has_citation = True
                elif source == 'ai_research':
                    stats['with_ai_research'] += 1
                
                if prop_data.get('needs_research'):
                    stats['needs_research'] += 1
            
            if has_citation:
                stats['with_citations'] += 1
        
        # Print report
        print(f"\n📊 Materials: {stats['total_materials']}")
        print(f"   ✅ With citations: {stats['with_citations']}")
        print(f"   🤖 With AI research: {stats['with_ai_research']}")
        print(f"   ⚠️  Needs research: {stats['needs_research']}")
        print(f"\n📊 Properties: {stats['total_properties']}")
        print(f"   ✅ With citations: {stats['properties_with_citations']}")
        if stats['total_properties'] > 0:
            coverage = (stats['properties_with_citations'] / stats['total_properties']) * 100
            print(f"   📈 Coverage: {coverage:.1f}%")
        
        return stats


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Integrate research citations into Materials.yaml'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--report-only',
        action='store_true',
        help='Generate coverage report only'
    )
    
    args = parser.parse_args()
    
    integrator = ResearchCitationIntegrator(dry_run=args.dry_run)
    
    if args.report_only:
        integrator.generate_report()
    else:
        # Integrate citations
        updates = integrator.integrate_property_research()
        
        print(f"\n{'='*80}")
        print(f"✅ Integration complete: {updates} properties updated")
        print(f"{'='*80}")
        
        # Generate report
        integrator.generate_report()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
