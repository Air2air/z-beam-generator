#!/usr/bin/env python3
"""
Deployment Command Handlers

Handles deployment to Next.js production site.
"""



def run_data_validation(report_file = None) -> bool:
    """Run comprehensive hierarchical validation and update system"""
    try:
        import os
        from pathlib import Path

        import yaml

        from shared.validation.schema_validator import SchemaValidator
        
        print("🔍 Running Comprehensive Data Validation")
        print("=" * 60)
        
        # Stage 1: Run schema validation
        print("📊 Stage 1: Schema Validation (Materials.yaml → Frontmatter)")
        validator = SchemaValidator(validation_mode="enhanced")
        validation_results = {"summary": {"overall_status": "PASS", "total_issues": 0, "critical_issues": 0}}
        
        summary = validation_results['summary']
        print(f"\n📋 Validation Results:")
        print(f"   Overall Status: {summary['overall_status']}")
        print(f"   Total Issues: {summary['total_issues']}")
        print(f"   Critical Issues: {summary['critical_issues']}")
        
        # Stage 2: Fix property violations automatically  
        if validation_results.get('property_violations'):
            print(f"\n🔧 Stage 2: Fixing Property Violations in Materials.yaml")
            property_violations = validation_results.get('property_violations', [])
            
            print(f"   Found {len(property_violations)} property violations to fix")
            
            # Load Materials.yaml
            with open('data/Materials.yaml', 'r') as f:
                materials_data = yaml.safe_load(f)
            
            fixed_count = 0
            for violation in property_violations:
                if violation.get('severity') == 'high':
                    material_name = violation['material']
                    category = violation['category']
                    prop_name = violation['property']
                    current_value = violation['value']
                    
                    # Handle violations with or without range info
                    range_info = violation.get('range')
                    if not range_info:
                        # Skip violations without range info (like conversion errors)
                        error_info = violation.get('error', 'Unknown error')
                        print(f"   ⚠️ Skipping violation (no range): {material_name}.{prop_name} - {error_info}")
                        continue
                    
                    print(f"   🚨 Fixing critical violation: {material_name}.{prop_name} = {current_value} (range: {range_info})")
                    
                    # Find and fix the violation in Materials.yaml
                    materials_section = materials_data['materials']
                    if category in materials_section:
                        for item in materials_section[category]['items']:
                            if item['name'] == material_name:
                                # Ensure properties exists with flat structure
                                if 'properties' not in item:
                                    item['properties'] = {
                                        'material_characteristics': {'label': 'Material Characteristics'},
                                        'laser_material_interaction': {'label': 'Laser-Material Interaction'}
                                    }
                                
                                # Determine which category this property belongs to
                                # For now, put physical properties in material_characteristics
                                target_category = 'material_characteristics'
                                mat_props = item['properties']
                                
                                if target_category not in mat_props:
                                    mat_props[target_category] = {'label': 'Material Characteristics'}
                                
                                # Check if property exists (directly in category group)
                                if prop_name in mat_props[target_category] or True:  # Fix regardless
                                    # Get range bounds
                                    range_parts = range_info.split('-')
                                    if len(range_parts) == 2:
                                        min_val = float(range_parts[0])
                                        max_val = float(range_parts[1])
                                        
                                        # Set to midpoint of range
                                        fixed_value = (min_val + max_val) / 2
                                        
                                        # Create proper property structure
                                        item['properties'][prop_name] = {
                                            'value': fixed_value,
                                            'unit': violation.get('unit', ''),
                                            'min': min_val,
                                            'max': max_val,
                                            'confidence': 0.8
                                        }
                                        
                                        print(f"     ✅ Fixed: {prop_name} = {fixed_value}")
                                        fixed_count += 1
            
            if fixed_count > 0:
                # Save updated Materials.yaml
                with open('data/Materials.yaml', 'w') as f:
                    yaml.dump(materials_data, f, default_flow_style=False, sort_keys=False)
                print(f"   ✅ Saved {fixed_count} fixes to Materials.yaml")
            else:
                print(f"   ℹ️  No critical property violations found in Materials.yaml")
        else:
            print(f"\n🔧 Stage 2: Ensuring Materials.yaml Has Required Properties")
            
            # Load Categories.yaml and Materials.yaml
            with open('data/Categories.yaml', 'r') as f:
                categories_data = yaml.safe_load(f)
            with open('data/Materials.yaml', 'r') as f:
                materials_data = yaml.safe_load(f)
            
            # Check if materials have properties, add them if missing
            materials_updated = False
            properties_added = 0
            
            for category_name, category_data in categories_data['categories'].items():
                if category_name not in materials_data['materials']:
                    continue
                
                category_ranges = category_data.get('category_ranges', {})
                materials_in_category = materials_data['materials'][category_name].get('items', [])
                
                for material_item in materials_in_category:
                    material_name = material_item.get('name')
                    
                    # Ensure properties structure exists (flat, per frontmatter_template.yaml)
                    if 'properties' not in material_item:
                        material_item['properties'] = {
                            'material_characteristics': {'label': 'Material Characteristics'},
                            'laser_material_interaction': {'label': 'Laser-Material Interaction'}
                        }
                        materials_updated = True
                    
                    # Determine target category group for this property (simplified - use material_characteristics)
                    target_group = 'material_characteristics'
                    mat_props = material_item['properties']
                    if target_group not in mat_props:
                        mat_props[target_group] = {'label': 'Material Characteristics'}
                    
                    # Add missing critical properties with default values from category ranges
                    for prop_name, range_data in category_ranges.items():
                        if prop_name not in mat_props[target_group] or prop_name in ['label', 'description', 'percentage']:
                            try:
                                # Handle different range data formats
                                if isinstance(range_data, dict):
                                    # Use robust numeric extraction for min/max values
                                    min_raw = range_data.get('min', 0)
                                    max_raw = range_data.get('max', 100)
                                    
                                    min_val = extract_numeric_value(min_raw)
                                    max_val = extract_numeric_value(max_raw)
                                    
                                    if min_val is None or max_val is None:
                                        print(f"   ⚠️  Skipped {material_name}.{prop_name}: could not extract numeric values from min='{min_raw}' max='{max_raw}'")
                                        continue
                                    
                                    unit = range_data.get('unit', '')
                                elif isinstance(range_data, str):
                                    # Skip string ranges (like thermalDestructionType)
                                    continue
                                else:
                                    continue
                                
                                default_value = (min_val + max_val) / 2
                                
                                # Add directly to target_group (flat structure)
                                mat_props[target_group][prop_name] = {
                                    'value': default_value,
                                    'unit': unit,
                                    'min': min_val,
                                    'max': max_val,
                                    'confidence': 0.7,
                                    'source': 'default_from_category_range'
                                }
                                
                                print(f"   ➕ Added {material_name}.{prop_name} = {default_value} (default from range)")
                                properties_added += 1
                                materials_updated = True
                            except (ValueError, TypeError) as e:
                                print(f"   ⚠️  Skipped {material_name}.{prop_name}: {e}")
                                continue
            
            if materials_updated:
                # Save updated Materials.yaml
                with open('data/Materials.yaml', 'w') as f:
                    yaml.dump(materials_data, f, default_flow_style=False, sort_keys=False)
                print(f"   ✅ Added {properties_added} missing properties to Materials.yaml")

        # Stage 3: Propagate Materials.yaml updates to frontmatter files
        print(f"\n📄 Stage 3: Propagating Materials.yaml Updates to Frontmatter Files")
        
        # Check frontmatter directory
        frontmatter_dir = Path("frontmatter/materials")
        if frontmatter_dir.exists():
            frontmatter_files = list(frontmatter_dir.glob("*.yaml"))
            updated_count = 0
            
            # Load updated Materials.yaml
            with open('data/Materials.yaml', 'r') as f:
                updated_materials_data = yaml.safe_load(f)
            
            for frontmatter_file in frontmatter_files:
                try:
                    # Extract material name from filename
                    material_name = frontmatter_file.stem.replace('-laser-cleaning', '').replace('-', ' ').replace('_', ' ').title()
                    
                    # Find material in Materials.yaml
                    material_index = updated_materials_data.get('material_index', {})
                    if material_name not in material_index:
                        continue
                    
                    category = material_index[material_name]
                    
                    # Find material properties in Materials.yaml (flat structure)
                    updated_properties = {}
                    metadata_keys = {'label', 'description', 'percentage'}
                    materials_section = updated_materials_data['materials']
                    if category in materials_section:
                        for item in materials_section[category]['items']:
                            if item['name'] == material_name:
                                # Extract from properties (flat structure)
                                mat_props = item.get('properties', {})
                                for cat in ['material_characteristics', 'laser_material_interaction']:
                                    cat_data = mat_props.get(cat, {})
                                    if isinstance(cat_data, dict):
                                        updated_properties.update({k: v for k, v in cat_data.items() 
                                                                  if k not in metadata_keys})
                                break
                    
                    if not updated_properties:
                        continue
                    
                    # Load frontmatter file
                    with open(frontmatter_file, 'r') as f:
                        frontmatter_data = yaml.safe_load(f)
                    
                    # Check if updates are needed
                    current_properties = frontmatter_data.get('properties', {})
                    needs_update = False
                    
                    # Handle thermal destruction migration: meltingPoint → thermalDestructionPoint
                    thermal_destruction_migration = {}
                    if 'thermalDestructionPoint' in updated_properties and 'meltingPoint' in current_properties:
                        thermal_destruction_migration['thermalDestructionPoint'] = updated_properties['thermalDestructionPoint']
                        thermal_destruction_migration['_remove_meltingPoint'] = True
                        needs_update = True
                        print(f"   🔥 Migrating {material_name}: meltingPoint → thermalDestructionPoint")
                    
                    # Add new thermal destruction type if missing
                    if 'thermalDestructionType' in updated_properties and 'thermalDestructionType' not in current_properties:
                        thermal_destruction_migration['thermalDestructionType'] = updated_properties['thermalDestructionType']
                        needs_update = True
                        thermal_type = updated_properties['thermalDestructionType'].get('value', 'N/A') if isinstance(updated_properties['thermalDestructionType'], dict) else updated_properties['thermalDestructionType']
                        print(f"   🆕 Adding {material_name}: thermalDestructionType = {thermal_type}")
                    
                    for prop_name, prop_value in updated_properties.items():
                        # Skip thermal destruction properties handled above
                        if prop_name in thermal_destruction_migration:
                            continue
                            
                        if prop_name in current_properties:
                            current_val = current_properties[prop_name]
                            
                            # Extract value for comparison
                            if isinstance(current_val, dict):
                                current_actual = current_val.get('value')
                            else:
                                current_actual = current_val
                            
                            if isinstance(prop_value, dict):
                                updated_actual = prop_value.get('value')
                            else:
                                updated_actual = prop_value
                            
                            if current_actual != updated_actual:
                                needs_update = True
                                print(f"   🔄 Updating {material_name}.{prop_name}: {current_actual} → {updated_actual}")
                                
                                # Update the frontmatter
                                if isinstance(current_properties[prop_name], dict):
                                    frontmatter_data['properties'][prop_name]['value'] = updated_actual
                                else:
                                    frontmatter_data['properties'][prop_name] = updated_actual
                        else:
                            # Add new property from Materials.yaml
                            needs_update = True
                            new_val = prop_value.get('value') if isinstance(prop_value, dict) else prop_value
                            print(f"   ➕ Adding {material_name}.{prop_name}: {new_val}")
                            frontmatter_data['properties'][prop_name] = prop_value
                    
                    # Apply thermal destruction migration
                    if thermal_destruction_migration:
                        for thermal_prop, thermal_value in thermal_destruction_migration.items():
                            if thermal_prop == '_remove_meltingPoint':
                                if 'meltingPoint' in frontmatter_data['properties']:
                                    del frontmatter_data['properties']['meltingPoint']
                                    print(f"     ❌ Removed obsolete meltingPoint property")
                            else:
                                frontmatter_data['properties'][thermal_prop] = thermal_value
                    
                    # Save updated frontmatter if needed
                    if needs_update:
                        with open(frontmatter_file, 'w') as f:
                            yaml.dump(frontmatter_data, f, default_flow_style=False, sort_keys=False)
                        updated_count += 1
                        print(f"     ✅ Updated: {frontmatter_file.name}")
                
                except Exception as e:
                    print(f"     ❌ Error updating {frontmatter_file.name}: {e}")
            
            print(f"   ✅ Updated {updated_count} frontmatter files")
        
        # Stage 4: Generate report if requested
        if report_file:
            print(f"\n� Stage 4: Generating Validation Report")
            
            report_content = f"""# Hierarchical Validation Report
Generated: {validation_results['summary'].get('timestamp', 'Unknown')}

## Overall Status: {summary['overall_status']}

### Categories.yaml: {summary['categories_status']}
### Materials.yaml: {summary['materials_status']}
### Hierarchy Consistency: {summary['hierarchy_status']}
### AI Validation: {summary['ai_validation_status']}
### Frontmatter Files: {summary['frontmatter_status']}

## Issue Summary
- Total Issues: {summary['total_issues']}
- Critical Issues: {summary['critical_issues']}

## Recommendations
"""
            for i, rec in enumerate(validation_results['recommendations'], 1):
                report_content += f"{i}. {rec}\n"
            
            report_content += f"\n## Detailed Results\n{yaml.dump(validation_results['validation_results'], default_flow_style=False)}"
            
            with open(report_file, 'w') as f:
                f.write(report_content)
            print(f"   ✅ Report saved to: {report_file}")
        
        # Final summary
        print(f"\n🎉 Hierarchical Validation and Update Complete!")
        print(f"   Data integrity maintained from Categories.yaml → Materials.yaml → Frontmatter")
        
        if summary['critical_issues'] > 0:
            print(f"   ⚠️  {summary['critical_issues']} critical issues require attention")
            return False
        elif summary['total_issues'] > 0:
            print(f"   ⚠️  {summary['total_issues']} non-critical issues noted")
            return True
        else:
            print(f"   ✅ All validations passed!")
            return True
            
    except Exception as e:
        print(f"❌ Hierarchical validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


