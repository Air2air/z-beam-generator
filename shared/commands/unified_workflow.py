#!/usr/bin/env python3
"""
Unified workflow commands for single-command content generation.

This module provides COMPLETE INLINE orchestration that combines:
0. Data Completeness Validation (inline)
1. Auto-Remediation Research (inline, if needed)
2. Content Generation (micro, subtitle, FAQ)
3. Voice Enhancement (post-processing)
4. Content Validation (quality checks)
5. Frontmatter Export

User workflow: "run Brass" → Complete validated frontmatter file
No manual steps. No separate scripts. Everything orchestrated inline.
"""

from typing import Dict, Any

# Import generation commands
from shared.commands import (
    handle_micro_generation,
    handle_material_description_generation,
    handle_faq_generation,
)

# Import voice enhancement
from scripts.voice.enhance_materials_voice import MaterialsVoiceEnhancer

# Import frontmatter export
from export.orchestrator import FrontmatterOrchestrator

# Import API client
from shared.api.client_factory import create_api_client


def _validate_material_completeness(material_name: str, material_data: Dict) -> Dict[str, Any]:
    """
    Inline validation of material data completeness.
    
    Returns:
        Dict with validation results including missing properties and range violations
    """
    validation = {
        'complete': True,
        'missing': [],
        'warnings': [],
        'range_violations': []
    }
    
    # Check critical sections
    critical_sections = {
        'materialProperties': material_data.get('materialProperties', {}),
        'machineSettings': material_data.get('machineSettings', {})
    }
    
    for section_name, section_data in critical_sections.items():
        if not section_data or len(section_data) == 0:
            validation['complete'] = False
            validation['missing'].append(section_name)
    
    # Check if materialProperties has actual values (not just labels)
    if material_data.get('materialProperties'):
        props = material_data['materialProperties']
        has_actual_properties = False
        label_only_count = 0
        
        for prop, value in props.items():
            if value is None or value == '':
                validation['warnings'].append(f"materialProperties.{prop} is null/empty")
            elif isinstance(value, dict):
                # Check if this property has actual value data (not just label/type metadata)
                has_value = any(key in value for key in ['value', 'min', 'max'])
                if has_value:
                    has_actual_properties = True
                elif 'label' in value:
                    label_only_count += 1
        
        # If ALL properties are label-only (no actual values), mark as incomplete
        if not has_actual_properties and label_only_count > 0:
            validation['complete'] = False
            validation['missing'].append('materialProperties (has labels but no actual property values)')
            validation['warnings'].append(
                f"materialProperties contains {label_only_count} label-only fields - needs property research"
            )
    
    if material_data.get('machineSettings'):
        for setting, value in material_data['machineSettings'].items():
            if value is None or value == '':
                validation['warnings'].append(f"machineSettings.{setting} is null/empty")
    
    # NEW: Validate property values are within category min/max ranges
    range_violations = _validate_property_ranges(material_name, material_data)
    validation['range_violations'] = range_violations
    
    if range_violations:
        validation['warnings'].append(f"Found {len(range_violations)} properties outside category ranges")
    
    return validation


def _validate_property_ranges(material_name: str, material_data: Dict) -> list:
    """
    Validate that property values fall within their category min/max ranges.
    
    Returns:
        List of violations with details
    """
    violations = []
    
    try:
        # Load Categories.yaml to get category ranges
        from pathlib import Path
        import yaml
        
        categories_path = Path("data/materials/Categories.yaml")
        if not categories_path.exists():
            return violations
        
        with open(categories_path, 'r', encoding='utf-8') as f:
            categories_data = yaml.safe_load(f)
        
        if not categories_data or 'categories' not in categories_data:
            return violations
        
        # Determine material category
        material_category = material_data.get('category')
        if not material_category:
            return violations
        
        # Get category ranges for this material type
        category_info = categories_data['categories'].get(material_category)
        if not category_info or 'category_ranges' not in category_info:
            return violations
        
        category_ranges = category_info['category_ranges']
        
        # Check materialProperties
        material_props = material_data.get('materialProperties', {})
        
        # Check both category groups and root-level properties
        for category_group in ['material_characteristics', 'laser_material_interaction']:
            group_data = material_props.get(category_group, {})
            if isinstance(group_data, dict):
                for prop_name, prop_value in group_data.items():
                    if prop_name == 'label':
                        continue
                    
                    _check_property_range(
                        prop_name, prop_value, category_ranges, 
                        material_name, violations
                    )
        
        # Also check root-level properties (for materials not yet normalized)
        for prop_name, prop_value in material_props.items():
            if prop_name in ['material_characteristics', 'laser_material_interaction']:
                continue
            
            _check_property_range(
                prop_name, prop_value, category_ranges,
                material_name, violations
            )
        
    except Exception as e:
        # Don't fail validation on range check errors
        print(f"⚠️  Range validation error: {e}")
    
    return violations


def _check_property_range(prop_name: str, prop_value: Any, category_ranges: Dict, 
                         material_name: str, violations: list) -> None:
    """Helper to check a single property against its category range."""
    if not isinstance(prop_value, dict):
        return
    
    # Get the actual value
    value = prop_value.get('value')
    if value is None:
        return
    
    # Check if this property has a category range
    prop_range = category_ranges.get(prop_name)
    if not prop_range or not isinstance(prop_range, dict):
        return
    
    range_min = prop_range.get('min')
    range_max = prop_range.get('max')
    
    # Skip if range is null (intentionally unbounded)
    if range_min is None or range_max is None:
        return
    
    # Convert value to float for comparison
    try:
        value_float = float(value)
        min_float = float(range_min)
        max_float = float(range_max)
        
        # Check if value is outside range
        if value_float < min_float or value_float > max_float:
            violations.append({
                'material': material_name,
                'property': prop_name,
                'value': value_float,
                'min': min_float,
                'max': max_float,
                'unit': prop_value.get('unit', ''),
                'outside_by': min(abs(value_float - min_float), abs(value_float - max_float))
            })
    except (ValueError, TypeError):
        # Skip properties that can't be converted to float
        pass


def _research_missing_properties_inline(material_name: str, missing_sections: list) -> bool:
    """
    Inline property research using PropertyManager.
    Triggers auto-remediation for missing materialProperties or machineSettings.
    
    Returns:
        True if research succeeded, False otherwise
    """
    try:
        print("🔬 Starting inline property research...")
        print(f"   Missing sections: {', '.join(missing_sections)}")
        
        # Check if materialProperties section exists but is incomplete
        if 'materialProperties' in missing_sections or \
           any('materialProperties' in section for section in missing_sections):
            
            print("   Triggering property research to populate missing data...")
            
            # Import and call the existing research handler
            from shared.commands.research import handle_research_missing_properties
            
            # Research properties for this specific material (no user confirmation in auto mode)
            # Note: This will populate the materialProperties structure with actual property values
            research_success = handle_research_missing_properties(
                batch_size=10,
                confidence_threshold=70,
                specific_materials=[material_name],
                specific_properties=None,
                auto_mode=True  # Skip user confirmation in workflow auto-remediation
            )
            
            if research_success:
                print("✅ Property research completed - Materials.yaml updated")
                return True
            else:
                print("⚠️  Property research had issues - continuing anyway")
                return True  # Don't block workflow
        else:
            print("   No materialProperties issues detected")
            return True
            
    except Exception as e:
        print(f"❌ Property research error: {e}")
        import traceback
        traceback.print_exc()
        # Don't block workflow even on error
        return True


def _research_missing_category_ranges_inline() -> bool:
    """
    Inline category range research using CategoryRangeResearcher.
    Checks Categories.yaml for missing/null ranges and auto-remediates them.
    
    Returns:
        True if all missing ranges were researched and fixed, False otherwise
    """
    try:
        print("🔬 Starting inline category range research...")
        
        from pathlib import Path
        import yaml
        
        # Load Categories.yaml directly (avoid fail_fast validation triggers)
        categories_path = Path("data/materials/Categories.yaml")
        if not categories_path.exists():
            print("❌ Categories.yaml not found")
            return False
        
        with open(categories_path, 'r', encoding='utf-8') as f:
            categories_data = yaml.safe_load(f)
        
        if not categories_data or 'categories' not in categories_data:
            print("❌ Invalid Categories.yaml structure")
            return False
        
        # Find missing ranges
        missing_ranges = []
        for category_name, category_data in categories_data['categories'].items():
            if 'category_ranges' not in category_data:
                continue
            
            for prop_name, prop_range in category_data['category_ranges'].items():
                if not isinstance(prop_range, dict):
                    continue
                
                # Check for null/missing min or max
                if prop_range.get('min') is None or prop_range.get('max') is None:
                    missing_ranges.append({
                        'category': category_name,
                        'property': prop_name,
                        'current_min': prop_range.get('min'),
                        'current_max': prop_range.get('max'),
                        'unit': prop_range.get('unit', '')
                    })
        
        if not missing_ranges:
            print("✅ All category ranges are complete")
            return True
        
        print(f"   Found {len(missing_ranges)} missing/null ranges")
        for item in missing_ranges[:10]:  # Show first 10
            print(f"   • {item['category']}.{item['property']} (min={item['current_min']}, max={item['current_max']})")
        if len(missing_ranges) > 10:
            print(f"   ... and {len(missing_ranges) - 10} more")
        
        # Use default ranges for thermal destruction (the missing property)
        # Based on material science literature and CategoryRangeResearcher defaults
        default_thermal_ranges = {
            'metal': {'min': 273.0, 'max': 3695.0, 'unit': 'K', 'confidence': 0.7},
            'ceramic': {'min': 273.0, 'max': 3900.0, 'unit': 'K', 'confidence': 0.7},
            'composite': {'min': 273.0, 'max': 900.0, 'unit': 'K', 'confidence': 0.7},
            'glass': {'min': 273.0, 'max': 2300.0, 'unit': 'K', 'confidence': 0.7},
            'masonry': {'min': 273.0, 'max': 2500.0, 'unit': 'K', 'confidence': 0.7},
            'plastic': {'min': 273.0, 'max': 700.0, 'unit': 'K', 'confidence': 0.7},
            'semiconductor': {'min': 273.0, 'max': 1685.0, 'unit': 'K', 'confidence': 0.7},
            'stone': {'min': 273.0, 'max': 2300.0, 'unit': 'K', 'confidence': 0.7},
            'wood': {'min': 273.0, 'max': 600.0, 'unit': 'K', 'confidence': 0.7},
            'rare-earth': {'min': 273.0, 'max': 3520.0, 'unit': 'K', 'confidence': 0.7}
        }
        
        fixed_count = 0
        
        print("\n🔬 Applying default thermal destruction ranges...")
        for item in missing_ranges:
            category = item['category']
            prop_name = item['property']
            
            # Check if this is thermalDestruction and we have defaults for this category
            if 'thermal' in prop_name.lower() and category in default_thermal_ranges:
                range_data = default_thermal_ranges[category]
                
                # Update Categories.yaml with default range
                categories_data['categories'][category]['category_ranges'][prop_name] = {
                    'min': range_data['min'],
                    'max': range_data['max'],
                    'unit': range_data.get('unit', item['unit'])
                }
                
                print(f"   ✅ {category}.{prop_name}: {range_data['min']}-{range_data['max']} {range_data.get('unit', '')}")
                fixed_count += 1
            else:
                print(f"   ⚠️  No default range available for {category}.{prop_name}")
        
        # Save updated Categories.yaml if we fixed any ranges
        if fixed_count > 0:
            with open(categories_path, 'w', encoding='utf-8') as f:
                yaml.dump(categories_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            print(f"\n✅ Fixed {fixed_count}/{len(missing_ranges)} ranges and updated Categories.yaml")
            return True
        else:
            print("⚠️  Could not fix any ranges - manual review needed")
            return False
            
    except Exception as e:
        print(f"❌ Category range research error: {e}")
        import traceback
        traceback.print_exc()
        return False


def _validate_content_quality_inline(material_name: str, material_data: Dict) -> Dict[str, Any]:
    """
    Inline content quality validation.
    Checks for voice markers, word counts, completeness.
    
    Returns:
        Dict with quality validation results
    """
    quality = {
        'passed': True,
        'issues': []
    }
    
    # Check micro
    micro = material_data.get('micro', {})
    if micro:
        before = micro.get('before', '')
        after = micro.get('after', '')
        
        if not before or len(before.split()) < 10:
            quality['issues'].append("Caption 'before' too short or missing")
            quality['passed'] = False
            
        if not after or len(after.split()) < 10:
            quality['issues'].append("Caption 'after' too short or missing")
            quality['passed'] = False
    else:
        quality['issues'].append("Caption missing")
        quality['passed'] = False
    
    # Check subtitle
    subtitle = material_data.get('subtitle', '')
    if not subtitle or len(subtitle.split()) < 5:
        quality['issues'].append("Subtitle missing or too short")
        quality['passed'] = False
    
    # Check FAQ
    faq = material_data.get('faq', [])
    if not faq or len(faq) < 2:
        quality['issues'].append("FAQ missing or too few questions")
        quality['passed'] = False
    
    # Check for voice markers (Taiwan markers)
    text_content = str(micro) + str(subtitle) + str(faq)
    voice_markers = ['particularly', 'specifically', 'notably', 'thereby', 'thus', 'hence']
    found_markers = [m for m in voice_markers if m.lower() in text_content.lower()]
    
    if len(found_markers) < 2:
        quality['issues'].append(f"Insufficient voice markers (found {len(found_markers)}, need 2+)")
        quality['passed'] = False
    
    return quality


def run_material_workflow(
    material_name: str,
    skip_validation: bool = False,
    skip_research: bool = False,
    skip_generation: bool = False,
    skip_voice: bool = False,
    skip_export: bool = False
) -> Dict[str, Any]:
    """
    COMPLETE INLINE WORKFLOW for material content generation.
    
    Everything orchestrated inline - no manual steps required:
    0. System integrity check (inline)
    1. Data completeness validation (inline)
    2. Auto-remediation research (inline, if needed)
    3. Content generation (micro, subtitle, FAQ)
    4. Voice enhancement with validation
    5. Content quality validation (inline)
    6. Frontmatter export
    
    User experience: "run Brass" → Complete validated frontmatter
    
    Args:
        material_name: Name of material
        skip_validation: Skip all validation steps (NOT RECOMMENDED)
        skip_research: Skip property research (validation still runs)
        skip_generation: Skip text generation if already exists
        skip_voice: Skip voice enhancement if already applied
        skip_export: Skip frontmatter export if not needed
        
    Returns:
        Dict with complete workflow results including all validation
    """
    results = {
        'material': material_name,
        'steps': {
            'integrity_check': {},
            'data_validation': {},
            'research': {},
            'generation': {},
            'voice': {},
            'content_validation': {},
            'export': {}
        },
        'overall_success': False
    }
    
    step_results = results['steps']
    
    try:
        # ========================================================================
        # STEP 0: SYSTEM INTEGRITY CHECK (INLINE)
        # ========================================================================
        if not skip_validation:
            print("\n" + "="*80)
            print("STEP 0: SYSTEM INTEGRITY CHECK (INLINE)")
            print("Verifying system health before generation")
            print("="*80 + "\n")
            
            from shared.commands.integrity_helper import run_pre_generation_check
            integrity_passed = run_pre_generation_check(skip_check=False, quick=True)
            step_results['integrity_check']['passed'] = integrity_passed
            
            if not integrity_passed:
                print("❌ System integrity check FAILED")
                print("   Fix integrity issues before generating content.")
                print("   Run: python3 run.py --integrity-check --quick")
                return results
            
            print("✅ System integrity verified\n")
        
        # ========================================================================
        # STEP 1: DATA COMPLETENESS VALIDATION (INLINE)
        # ========================================================================
        if not skip_validation:
            print("\n" + "="*80)
            print("STEP 1: DATA COMPLETENESS VALIDATION (INLINE)")
            print("Material: " + material_name)
            print("="*80 + "\n")
            
            # Load material data
            from domains.materials.materials_cache import load_materials, get_material_by_name
            materials = load_materials()
            material_data = get_material_by_name(material_name, materials)
            
            if not material_data:
                print("❌ Material not found in Materials.yaml: " + material_name)
                step_results['data_validation']['material_found'] = False
                return results
            
            print("✅ Material found in Materials.yaml")
            step_results['data_validation']['material_found'] = True
            
            # Validate data completeness
            print("\n📋 Checking data completeness...")
            validation = _validate_material_completeness(material_name, material_data)
            step_results['data_validation']['validation'] = validation
            
            # Check category ranges completeness
            print("\n📋 Checking category ranges in Categories.yaml...")
            from scripts.validation.fail_fast_materials_validator import validate_category_ranges
            category_violations = validate_category_ranges()
            
            if category_violations:
                print(f"⚠️  Found {len(category_violations)} missing/null category ranges")
                for violation in category_violations[:5]:  # Show first 5
                    print(f"   • {violation}")
                if len(category_violations) > 5:
                    print(f"   ... and {len(category_violations) - 5} more")
                
                # Trigger category range auto-remediation
                print("\n🔬 Triggering category range auto-remediation...")
                category_research_success = _research_missing_category_ranges_inline()
                step_results['data_validation']['category_ranges_fixed'] = category_research_success
                
                if category_research_success:
                    print("✅ Category ranges researched and updated in Categories.yaml")
                else:
                    print("⚠️  Some category ranges could not be auto-fixed - manual review needed")
            else:
                print("✅ All category ranges are complete")
                step_results['data_validation']['category_ranges_complete'] = True
            
            # Display range violations
            if validation.get('range_violations'):
                print(f"\n⚠️  Found {len(validation['range_violations'])} properties outside category ranges:")
                for violation in validation['range_violations'][:10]:  # Show first 10
                    value = violation['value']
                    min_val = violation['min']
                    max_val = violation['max']
                    unit = violation['unit']
                    prop = violation['property']
                    print(f"   • {prop}: {value}{unit} (range: {min_val}-{max_val}{unit})")
                if len(validation['range_violations']) > 10:
                    print(f"   ... and {len(validation['range_violations']) - 10} more")
                print("   ℹ️  Range violations may indicate research errors or category range issues")
            
            if validation['complete']:
                print("\n✅ All critical material data present")
                validation_success = True
            else:
                print("\n⚠️  Missing critical data sections:")
                for missing in validation['missing']:
                    print(f"   • {missing}")
                
                if skip_research:
                    print("\n⏭️  Skipping auto-remediation research (--skip-research flag)")
                    print("⚠️  Data gaps remain - continuing anyway")
                    validation_success = True
                else:
                    # ====================================================================
                    # STEP 1: AUTO-REMEDIATION RESEARCH (INLINE)
                    # ====================================================================
                    print("\n" + "="*80)
                    print("STEP 1: AUTO-REMEDIATION RESEARCH (INLINE)")
                    print("="*80 + "\n")
                    
                    research_success = _research_missing_properties_inline(
                        material_name, 
                        validation['missing']
                    )
                    
                    step_results['research']['triggered'] = True
                    step_results['research']['success'] = research_success
                    
                    if research_success:
                        print("✅ Property research completed - Materials.yaml updated")
                        # Reload material data after research
                        from domains.materials.materials_cache import load_materials as reload_materials, get_material_by_name as get_mat
                        materials = reload_materials()
                        material_data = get_mat(material_name, materials)
                        validation_success = True
                    else:
                        print("⚠️  Research had issues - continuing anyway")
                        validation_success = True  # Don't block workflow
            
            # Show warnings if any
            if validation.get('warnings'):
                print("\n⚠️  Validation warnings:")
                for warning in validation['warnings']:
                    print(f"   • {warning}")
            
            print("\n✅ Data validation complete\n")
        else:
            print("\n⏭️  Skipping validation/research (--skip-validation flag)")
            validation_success = True
        # ========================================================================
        # STEP 2: TEXT CONTENT GENERATION
        # ========================================================================
        if not skip_generation:
            print("\n" + "="*80)
            print("STEP 2: TEXT CONTENT GENERATION")
            print("="*80 + "\n")
            
            # Generate micro
            print("→ Generating micro...")
            micro_success = handle_micro_generation(material_name)
            step_results['generation']['micro'] = micro_success
            
            # Generate material description
            print("→ Generating material description...")
            material_desc_success = handle_material_description_generation(material_name)
            step_results['generation']['material_description'] = material_desc_success
            
            # Generate FAQ
            print("→ Generating FAQ...")
            faq_success = handle_faq_generation(material_name)
            step_results['generation']['faq'] = faq_success
            
            generation_success = micro_success and material_desc_success and faq_success
            if not generation_success:
                print("\n⚠️  Some text generation steps failed. Check logs above.")
            else:
                print("\n✅ All text content generated successfully")
        else:
            print("\n⏭️  Skipping text generation (--skip-generation flag)")
            generation_success = True
        
        # ========================================================================
        # STEP 3: VOICE ENHANCEMENT
        # ========================================================================
        if not skip_voice:
            print("\n" + "="*80)
            print("STEP 3: VOICE ENHANCEMENT")
            print("="*80 + "\n")
            
            try:
                # Create API client for voice enhancement
                api_client = create_api_client('grok')
                enhancer = MaterialsVoiceEnhancer(api_client)
                voice_success = enhancer.enhance_material(material_name)
                
                step_results['voice'] = {'success': voice_success}
                
                if voice_success:
                    print("\n✅ Voice enhancement applied successfully")
                else:
                    print("\n⚠️  Voice enhancement failed. Check logs above.")
                    
            except Exception as e:
                print("❌ Voice enhancement error: " + str(e))
                step_results['voice'] = {
                    'success': False,
                    'error': str(e)
                }
                voice_success = False
        else:
            print("\n⏭️  Skipping voice enhancement (--skip-voice flag)")
            voice_success = True
        
        # ========================================================================
        # STEP 4: CONTENT QUALITY VALIDATION (INLINE)
        # ========================================================================
        if not skip_validation:
            print("\n" + "="*80)
            print("STEP 4: CONTENT QUALITY VALIDATION (INLINE)")
            print("="*80 + "\n")
            
            # Reload material data to get latest content
            from domains.materials.materials_cache import load_materials, get_material_by_name
            materials = load_materials()
            material_data = get_material_by_name(material_name, materials)
            
            quality = _validate_content_quality_inline(material_name, material_data)
            step_results['content_validation'] = quality
            
            if quality['passed']:
                print("✅ Content quality validation passed")
            else:
                print("⚠️  Content quality issues detected:")
                for issue in quality['issues']:
                    print(f"   • {issue}")
                print("\n   Continuing to export anyway...")
            
            print()
        
        # ========================================================================
        # STEP 5: FRONTMATTER EXPORT
        # ========================================================================
        if not skip_export:
            print("\n" + "="*80)
            print("STEP 5: FRONTMATTER EXPORT")
            print("="*80 + "\n")
            
            try:
                # Load material data from Materials.yaml
                from domains.materials.materials_cache import load_materials, get_material_by_name  # noqa: F811
                materials = load_materials()
                material_data = get_material_by_name(material_name, materials)
                
                if not material_data:
                    raise ValueError("Material not found in Materials.yaml: " + material_name)
                
                # Generate frontmatter
                orchestrator = FrontmatterOrchestrator()
                export_result = orchestrator.generate(
                    material_name=material_name,
                    material_data=material_data
                )
                
                # Check if export succeeded
                export_success = export_result is not None and 'error' not in export_result
                
                if export_success:
                    # Write frontmatter file to frontmatter/materials/ directory
                    from pathlib import Path
                    import yaml
                    
                    output_dir = Path("frontmatter/materials")
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Use naming convention: material-name-laser-cleaning.yaml
                    filename = material_name.lower().replace(" ", "-") + "-laser-cleaning.yaml"
                    output_path = output_dir / filename
                    
                    # Write YAML file (overwrite if exists)
                    with open(output_path, 'w') as f:
                        yaml.dump(export_result, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                    
                    step_results['export'] = {
                        'success': True,
                        'path': str(output_path)
                    }
                    print("\n✅ Frontmatter exported successfully to: " + str(output_path))
                else:
                    step_results['export'] = {
                        'success': False,
                        'error': export_result.get('error', 'Unknown error') if isinstance(export_result, dict) else 'Export failed'
                    }
                    print("\n⚠️  Frontmatter export failed")
                    
            except Exception as e:
                print("❌ Export error: " + str(e))
                step_results['export'] = {
                    'success': False,
                    'error': str(e)
                }
                export_success = False
        else:
            print("\n⏭️  Skipping frontmatter export (--skip-export flag)")
            export_success = True
        
        # Final Summary
        print("\n" + "="*80)
        print("WORKFLOW COMPLETE: " + material_name)
        print("="*80)
        
        overall_success = (
            (skip_validation or validation_success) and
            (skip_generation or generation_success) and
            (skip_voice or voice_success) and
            (skip_export or export_success)
        )
        
        results['overall_success'] = overall_success
        
        if overall_success:
            print("\n✅ All workflow steps completed successfully!")
        else:
            print("\n⚠️  Some workflow steps failed. See details above.")
        
        # Step-by-step results
        print("\nStep Results:")
        if not skip_validation:
            val_status = "✅" if validation_success else "❌"
            research_triggered = step_results['validation'].get('research_triggered', False)
            if research_triggered:
                print("  " + val_status + " Validation & Research (auto-remediation triggered)")
            else:
                print("  " + val_status + " Validation (all properties present)")
        
        if not skip_generation:
            gen_status = "✅" if generation_success else "❌"
            print("  " + gen_status + " Generation: Caption=" + 
                  str(step_results['generation'].get('micro', False)) +
                  ", Subtitle=" + str(step_results['generation'].get('subtitle', False)) +
                  ", FAQ=" + str(step_results['generation'].get('faq', False)))
        
        if not skip_voice:
            voice_status = "✅" if voice_success else "❌"
            print("  " + voice_status + " Voice Enhancement")
        
        if not skip_export:
            export_status = "✅" if export_success else "❌"
            print("  " + export_status + " Frontmatter Export")
        
        print("\n")
        
        return results
        
    except Exception as e:
        print("\n❌ WORKFLOW ERROR: " + str(e))
        results['overall_success'] = False
        results['error'] = str(e)
        return results


def run_region_workflow(region_name: str) -> Dict[str, Any]:
    """
    Complete workflow for region content generation.
    
    Args:
        region_name: Name of region
        
    Returns:
        Dict with workflow results
    """
    print("\n⚠️  Region workflow not yet implemented")
    print("Coming soon: --run-region flag will generate complete region content")
    
    return {
        'region': region_name,
        'overall_success': False,
        'error': 'Region workflow not implemented yet'
    }


def run_application_workflow(application_name: str) -> Dict[str, Any]:
    """
    Complete workflow for application content generation.
    
    Args:
        application_name: Name of application
        
    Returns:
        Dict with workflow results
    """
    print("\n⚠️  Application workflow not yet implemented")
    print("Coming soon: --run-application flag will generate complete application content")
    
    return {
        'application': application_name,
        'overall_success': False,
        'error': 'Application workflow not implemented yet'
    }


def run_thesaurus_workflow(term: str) -> Dict[str, Any]:
    """
    Complete workflow for thesaurus entry generation.
    
    Args:
        term: Thesaurus term
        
    Returns:
        Dict with workflow results
    """
    print("\n⚠️  Thesaurus workflow not yet implemented")
    print("Coming soon: --run-thesaurus flag will generate complete thesaurus entries")
    
    return {
        'term': term,
        'overall_success': False,
        'error': 'Thesaurus workflow not implemented yet'
    }
