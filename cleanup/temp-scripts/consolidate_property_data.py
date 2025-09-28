#!/usr/bin/env python3
"""
Property Consolidation Implementation

This script implements comprehensive property consolidation to eliminate 150 redundant
property entries by moving duplicated properties to category level with inheritance.
"""

import yaml
import json
import shutil
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

def implement_property_consolidation():
    """Implement comprehensive property consolidation with category-level inheritance."""
    
    print("🚀 PROPERTY CONSOLIDATION IMPLEMENTATION")
    print("=" * 60)
    
    # Create backups first
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    categories_file = Path("data/Categories.yaml")
    materials_file = Path("data/materials.yaml")
    
    categories_backup = f"backups/Categories_backup_{timestamp}.yaml"
    materials_backup = f"backups/materials_backup_{timestamp}.yaml"
    
    print(f"📁 Creating backups...")
    Path("backups").mkdir(exist_ok=True)
    
    shutil.copy2(categories_file, categories_backup)
    shutil.copy2(materials_file, materials_backup)
    
    print(f"   ✅ Categories backup: {categories_backup}")
    print(f"   ✅ Materials backup: {materials_backup}")
    
    # Load data files
    with open(categories_file, 'r', encoding='utf-8') as f:
        categories_data = yaml.safe_load(f)
    
    with open(materials_file, 'r', encoding='utf-8') as f:
        materials_data = yaml.safe_load(f)
    
    print(f"\n📂 Loaded data files successfully")
    
    # Analyze current property redundancy (from our previous analysis)
    property_consolidation_plan = {
        'thermal_properties': {
            'eliminatable_entries': 50,
            'exact_duplications': 6,
            'category_defaults': {
                'metal': {
                    'thermalConductivity': '15-400 W/m·K',
                    'thermalExpansion': '10-25 × 10⁻⁶ /°C'
                },
                'composite': {
                    'thermalConductivity': '0.2-50 W/m·K',
                    'operating_temperature': '-40 to 200°C'
                },
                'stone': {
                    'thermalConductivity': '1.5-3.0 W/m·K',
                    'thermalExpansion': '8.0 × 10⁻⁶ /°C'
                },
                'wood': {
                    'thermalConductivity': '0.1-0.4 W/m·K',
                    'specific_heat': '1200-2000 J/kg·K'
                },
                'glass': {
                    'thermalConductivity': '1.0-1.4 W/m·K',
                    'thermalExpansion': '9.0 × 10⁻⁶ /°C'
                }
            }
        },
        'mechanical_properties': {
            'eliminatable_entries': 52,
            'exact_duplications': 6,
            'category_defaults': {
                'metal': {
                    'tensileStrength': '200-1200 MPa',
                    'youngsModulus': '200-250 GPa'
                },
                'composite': {
                    'tensileStrength': '100-1500 MPa',
                    'youngsModulus': '10-150 GPa'
                },
                'stone': {
                    'hardness': '6-7 Mohs',
                    'compressive_strength': '50-200 MPa'
                },
                'wood': {
                    'compressive_strength': '30-80 MPa',
                    'hardness': '1-5 Mohs'
                },
                'glass': {
                    'hardness': '5.5-6.5 Mohs',
                    'tensileStrength': '50-100 MPa',
                    'youngsModulus': '70-90 GPa'
                }
            }
        },
        'electrical_properties': {
            'eliminatable_entries': 30,
            'exact_duplications': 1,
            'category_defaults': {
                'metal': {
                    'electricalResistivity': '10-100 nΩ·m'
                },
                'semiconductor': {
                    'electricalResistivity': 'Variable'
                },
                'ceramic': {
                    'electricalResistivity': '1×10¹⁴ Ω·cm',
                    'dielectric_constant': '9.8'
                }
            }
        },
        'processing_properties': {
            'eliminatable_entries': 18,
            'exact_duplications': 2,
            'category_defaults': {
                'stone': {
                    'porosity': '5-15%'
                },
                'masonry': {
                    'porosity': '10-25%'
                },
                'wood': {
                    'moisture_content': '8-12%',
                    'grain_structure_type': 'Varied',
                    'resin_content': 'Low'
                }
            }
        }
    }
    
    # PHASE 1: Enhance Categories.yaml with materialPropertiesDefinitions
    print(f"\n🏗️ PHASE 1: ENHANCE CATEGORIES.YAML")
    
    # Create comprehensive materialPropertiesDefinitions
    material_properties_definitions = {
        'thermal_properties': {
            'description': 'Thermal behavior and heat transfer characteristics',
            'common_properties': {
                'thermalConductivity': {
                    'description': 'Rate of heat transfer through material',
                    'unit': 'W/(m·K)',
                    'measurement_method': 'ASTM C177 - Steady-State Heat Flux'
                },
                'thermalExpansion': {
                    'description': 'Change in dimensions with temperature',
                    'unit': '/K or /°C',
                    'measurement_method': 'ASTM E228 - Linear Thermal Expansion'
                },
                'specific_heat': {
                    'description': 'Heat capacity per unit mass',
                    'unit': 'J/(kg·K)',
                    'measurement_method': 'ASTM C351 - Mean Specific Heat'
                },
                'melting_point': {
                    'description': 'Temperature at which material transitions to liquid',
                    'unit': '°C',
                    'measurement_method': 'ASTM D3418 - Transition Temperatures'
                },
                'operating_temperature': {
                    'description': 'Safe operational temperature range',
                    'unit': '°C',
                    'measurement_method': 'Material-specific testing protocols'
                }
            }
        },
        'mechanical_properties': {
            'description': 'Material response to applied forces and deformation',
            'common_properties': {
                'hardness': {
                    'description': 'Resistance to indentation or scratching',
                    'unit': 'Mohs, HV, GPa',
                    'measurement_method': 'ASTM E384 - Microindentation Hardness'
                },
                'tensileStrength': {
                    'description': 'Maximum stress before failure under tension',
                    'unit': 'MPa',
                    'measurement_method': 'ASTM D638 - Tensile Properties'
                },
                'youngsModulus': {
                    'description': 'Elastic modulus measuring stiffness',
                    'unit': 'GPa',
                    'measurement_method': 'ASTM E111 - Young\'s Modulus'
                },
                'compressive_strength': {
                    'description': 'Maximum stress under compression',
                    'unit': 'MPa',
                    'measurement_method': 'ASTM D695 - Compressive Properties'
                },
                'flexural_strength': {
                    'description': 'Stress at failure in bending',
                    'unit': 'MPa',
                    'measurement_method': 'ASTM D790 - Flexural Properties'
                },
                'fracture_toughness': {
                    'description': 'Resistance to crack propagation',
                    'unit': 'MPa·m^0.5',
                    'measurement_method': 'ASTM E399 - Plane-Strain Fracture Toughness'
                }
            }
        },
        'electrical_properties': {
            'description': 'Electrical behavior and conductivity characteristics',
            'common_properties': {
                'electricalResistivity': {
                    'description': 'Resistance to electrical current flow',
                    'unit': 'Ω·m, Ω·cm, nΩ·m',
                    'measurement_method': 'ASTM B193 - Resistivity of Electrical Conductor Materials'
                },
                'dielectric_constant': {
                    'description': 'Relative permittivity for insulating materials',
                    'unit': 'dimensionless',
                    'measurement_method': 'ASTM D150 - AC Loss Characteristics'
                }
            }
        },
        'processing_properties': {
            'description': 'Manufacturing and processing characteristics',
            'common_properties': {
                'porosity': {
                    'description': 'Percentage of void space in material',
                    'unit': '%',
                    'measurement_method': 'ASTM C373 - Water Absorption'
                },
                'firing_temperature': {
                    'description': 'Temperature for ceramic processing',
                    'unit': '°C',
                    'measurement_method': 'Material-specific processing protocols'
                },
                'moisture_content': {
                    'description': 'Water content in material',
                    'unit': '%',
                    'measurement_method': 'ASTM D4442 - Moisture Content'
                },
                'resin_content': {
                    'description': 'Polymer matrix content in composites',
                    'unit': '%',
                    'measurement_method': 'ASTM D3171 - Constituent Content'
                },
                'grain_structure_type': {
                    'description': 'Microstructural grain organization',
                    'unit': 'descriptive',
                    'measurement_method': 'Microscopy and metallographic analysis'
                }
            }
        }
    }
    
    # Add category-level property defaults
    category_property_defaults = {}
    
    categories_to_process = materials_data.get('materials', {}).keys()
    
    for category_name in categories_to_process:
        category_defaults = {}
        
        # Add defaults from consolidation plan
        for prop_type, prop_plan in property_consolidation_plan.items():
            if category_name in prop_plan['category_defaults']:
                if prop_type not in category_defaults:
                    category_defaults[prop_type] = {}
                category_defaults[prop_type].update(prop_plan['category_defaults'][category_name])
        
        if category_defaults:
            category_property_defaults[category_name] = category_defaults
    
    print(f"   📊 Created property definitions for {len(material_properties_definitions)} property types")
    print(f"   📊 Generated category defaults for {len(category_property_defaults)} categories")
    
    # Add to Categories.yaml
    if 'materialPropertiesDefinitions' not in categories_data:
        categories_data['materialPropertiesDefinitions'] = material_properties_definitions
        print(f"   ✅ Added materialPropertiesDefinitions to Categories.yaml")
    else:
        print(f"   🔄 Updated existing materialPropertiesDefinitions")
        categories_data['materialPropertiesDefinitions'].update(material_properties_definitions)
    
    # Add category property defaults to each category
    categories_updated = 0
    for category_name, category_data in categories_data.items():
        if (isinstance(category_data, dict) and 
            category_name not in ['metadata', 'universal_regulatory_standards', 'machineSettingsDescriptions', 
                                'materialPropertiesDefinitions', 'environmentalImpactTemplates', 'applicationTypes']):
            
            if category_name in category_property_defaults:
                if 'categoryPropertyDefaults' not in category_data:
                    category_data['categoryPropertyDefaults'] = {}
                
                category_data['categoryPropertyDefaults'].update(category_property_defaults[category_name])
                categories_updated += 1
                print(f"   ✅ Added property defaults to {category_name} category")
    
    print(f"   📊 Updated {categories_updated} categories with property defaults")
    
    # PHASE 2: Consolidate materials.yaml properties
    print(f"\n🔄 PHASE 2: CONSOLIDATE MATERIALS.YAML PROPERTIES")
    
    consolidation_stats = {
        'materials_processed': 0,
        'properties_eliminated': 0,
        'exact_matches_found': 0,
        'inheritance_applied': 0
    }
    
    categories_materials = materials_data.get('materials', {})
    
    for category_name, category_data in categories_materials.items():
        if isinstance(category_data, dict) and 'items' in category_data:
            materials_list = category_data['items']
            category_defaults = category_property_defaults.get(category_name, {})
            
            print(f"   📁 Processing {category_name} category ({len(materials_list)} materials)")
            
            for material in materials_list:
                if isinstance(material, dict) and 'name' in material:
                    material_name = material['name']
                    consolidation_stats['materials_processed'] += 1
                    
                    # Process each property type
                    for prop_type in ['thermal_properties', 'mechanical_properties', 'electrical_properties', 'processing_properties']:
                        if prop_type in material:
                            material_props = material[prop_type]
                            category_props = category_defaults.get(prop_type, {})
                            
                            if isinstance(material_props, dict) and isinstance(category_props, dict):
                                # Check for exact matches with category defaults
                                exact_matches = []
                                for prop_name, prop_value in material_props.items():
                                    if prop_name in category_props and category_props[prop_name] == prop_value:
                                        exact_matches.append(prop_name)
                                
                                # Remove exact matches (inherit from category)
                                if exact_matches:
                                    for prop_name in exact_matches:
                                        del material_props[prop_name]
                                        consolidation_stats['properties_eliminated'] += 1
                                    
                                    consolidation_stats['exact_matches_found'] += len(exact_matches)
                                    consolidation_stats['inheritance_applied'] += 1
                                
                                # Remove empty property sections
                                if not material_props:
                                    del material[prop_type]
    
    print(f"   📊 Consolidation Results:")
    print(f"      Materials processed: {consolidation_stats['materials_processed']}")
    print(f"      Properties eliminated: {consolidation_stats['properties_eliminated']}")
    print(f"      Exact matches found: {consolidation_stats['exact_matches_found']}")
    print(f"      Materials using inheritance: {consolidation_stats['inheritance_applied']}")
    
    # PHASE 3: Update metadata and versioning
    print(f"\n📝 PHASE 3: UPDATE METADATA AND VERSIONING")
    
    # Update Categories.yaml metadata
    if 'metadata' in categories_data:
        metadata = categories_data['metadata']
        if 'version' in metadata:
            version_parts = metadata['version'].split('.')
            if len(version_parts) >= 2:
                minor_version = int(version_parts[1]) + 1
                metadata['version'] = f"{version_parts[0]}.{minor_version}.0"
            else:
                metadata['version'] = "2.5.0"
        
        metadata['last_updated'] = datetime.now().strftime('%Y-%m-%d')
        metadata['enhancement_notes'] = (
            f"{metadata.get('enhancement_notes', '')} "
            f"v{metadata['version']} applied comprehensive property consolidation eliminating "
            f"{consolidation_stats['properties_eliminated']} redundant property entries."
        ).strip()
        
        print(f"   ✅ Updated Categories.yaml to version {metadata['version']}")
    
    # Save updated files
    print(f"\n💾 SAVING UPDATED FILES:")
    
    with open(categories_file, 'w', encoding='utf-8') as f:
        yaml.dump(categories_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"   ✅ Updated Categories.yaml")
    
    with open(materials_file, 'w', encoding='utf-8') as f:
        yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"   ✅ Updated materials.yaml")
    
    # Generate consolidation report
    consolidation_report = {
        "consolidation_timestamp": datetime.now().isoformat(),
        "consolidation_type": "Property Consolidation",
        "backup_files": {
            "categories_backup": categories_backup,
            "materials_backup": materials_backup
        },
        "consolidation_plan": property_consolidation_plan,
        "implementation_results": {
            "categories_enhanced": categories_updated,
            "materials_processed": consolidation_stats['materials_processed'],
            "properties_eliminated": consolidation_stats['properties_eliminated'],
            "exact_matches_resolved": consolidation_stats['exact_matches_found'],
            "inheritance_implementations": consolidation_stats['inheritance_applied']
        },
        "property_definitions_added": len(material_properties_definitions),
        "category_defaults_created": len(category_property_defaults),
        "estimated_redundancy_reduction": f"{consolidation_stats['properties_eliminated']/150*100:.1f}%"
    }
    
    report_file = f"property_consolidation_report_{timestamp}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(consolidation_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 PROPERTY CONSOLIDATION COMPLETE!")
    print(f"   📊 Eliminated {consolidation_stats['properties_eliminated']} redundant property entries")
    print(f"   🏗️ Enhanced {categories_updated} categories with property defaults")
    print(f"   📋 Added comprehensive materialPropertiesDefinitions")
    print(f"   💾 Consolidation report: {report_file}")
    
    return consolidation_report

if __name__ == "__main__":
    implement_property_consolidation()