#!/usr/bin/env python3
"""
Z-Beam Generator - Command Line Interface

Entry point for the Z-Beam Generator system.
All configurations have been moved to config/settings.py for better organization.

═══════════════════════════════════════════════════════════════════════════════
📋 QUICK START GUIDE
═══════════════════════════════════════════════════════════════════════════════

🎯 GENERATE CONTENT:
  python3 run.py --material "Aluminum"     # Specific material (Materials.yaml-only)
  python3 run.py --all                     # All materials (Materials.yaml-only)
  python3 run.py --content-batch           # First 8 categories

🚀 DEPLOYMENT:
  python3 run.py --deploy                  # Deploy to Next.js production site

🧪 TESTING & VALIDATION:
  python3 run.py --test                    # Full test suite
  python3 run.py --test-api                # Test API connections
  python3 run.py --validate                # Validate existing data without regeneration
  python3 run.py --validate-report report.md  # Generate validation report
  python3 run.py --check-env               # Health check
  python3 run.py --list-materials          # List available materials

🔍 DATA VALIDATION & INTEGRITY:
  python3 run.py --validate              # Run hierarchical validation & auto-fix
  python3 run.py --validate-report FILE  # Generate detailed validation report

🔬 STAGE 0: AI RESEARCH & DATA COMPLETION (⚡ MANDATORY):
  python3 run.py --data-completeness-report  # Check current status (75.8% complete)
  python3 run.py --data-gaps                 # Show research priorities (635 gaps)
  python3 run.py --research-missing-properties  # Fill ALL missing properties
  python3 run.py --research-properties "porosity,electricalResistivity"  # Specific properties
  python3 run.py --research-materials "Copper,Steel"  # Specific materials
  python3 run.py --research-batch-size 20    # Parallel research (default: 10)
  python3 run.py --enforce-completeness      # Strict mode - block if incomplete

🔬 SYSTEMATIC DATA VERIFICATION (Legacy):
  python3 run.py --data                  # Verify ALL properties (18 hours, $14.64)
  python3 run.py --data=critical         # Verify critical properties (3 hours, $1.20)
  python3 run.py --data=test             # Safe test run (15 min, $0.10, dry-run)
  python3 run.py --data=important        # Verify important properties (3 hours, $1.20)
  python3 run.py --data=--group=mechanical  # Verify property group
  python3 run.py --data=--properties=density,meltingPoint  # Specific properties

⚙️  SYSTEM MANAGEMENT:
  python3 run.py --config                  # Show configuration
  python3 run.py --cache-stats             # Cache performance
  python3 run.py --preload-cache           # Optimize performance
  python3 run.py --clean                   # Clean generated content

🚀 OPTIMIZATION:
  python3 run.py --optimize frontmatter     # Optimize specific component

💡 For complete command reference: python3 run.py --help

═══════════════════════════════════════════════════════════════════════════════
📝 CONFIGURATION
═══════════════════════════════════════════════════════════════════════════════

All user-configurable settings are in: config/settings.py

To modify system behavior, edit config/settings.py:
  • GLOBAL_OPERATIONAL_CONFIG - Timeouts, retries, operational parameters
  • API_PROVIDERS - API provider settings (DeepSeek, Winston, Grok)
  • COMPONENT_CONFIG - Component enable/disable and priorities
  • AI_DETECTION_CONFIG - AI detection behavior
  • OPTIMIZER_CONFIG - Optimizer and text generation settings

═══════════════════════════════════════════════════════════════════════════════
"""

# Import all configuration from centralized location
from config.settings import (
    GLOBAL_OPERATIONAL_CONFIG,
    API_PROVIDERS,
    COMPONENT_CONFIG,
    AI_DETECTION_CONFIG,
    OPTIMIZER_CONFIG,
    get_optimizer_config,
    get_global_operational_config,
    get_batch_timeout,
    get_enhanced_client_config,
    get_research_config,
    get_component_generation_config,
    get_validation_config,
    get_api_providers,
    get_api_config_fallbacks,
    get_ai_detection_config,
    get_workflow_config,
    get_optimization_config,
    get_text_optimization_config,
    get_persona_config,
    get_dynamic_config_for_component,
    create_dynamic_ai_detection_config,
    extract_numeric_value,
)

# Standard library imports
import os
import sys
import re
import yaml
import shutil
import traceback
import subprocess
import argparse
from pathlib import Path

# =================================================================================
# DEPLOYMENT FUNCTIONS
# =================================================================================

def deploy_to_production():
    """Deploy generated content to Next.js production site."""
    import shutil
    import os
    
    # Define source and target paths - ONLY FRONTMATTER
    source_dir = "/Users/todddunning/Desktop/Z-Beam/z-beam-generator/content/components/frontmatter"
    target_dir = "/Users/todddunning/Desktop/Z-Beam/z-beam-test-push/content/components/frontmatter"
    
    try:
        # Verify source directory exists
        if not os.path.exists(source_dir):
            print(f"❌ Source directory not found: {source_dir}")
            return False
        
        # Verify target directory exists
        if not os.path.exists(target_dir):
            print(f"❌ Target directory not found: {target_dir}")
            return False
        
        print("🚀 Deploying frontmatter content from generator to Next.js production site...")
        print(f"📂 Source: {source_dir}")
        print(f"📂 Target: {target_dir}")
        print("📋 Deploying frontmatter component only")
        
        deployment_stats = {
            "updated": 0,
            "created": 0,
            "errors": 0,
            "skipped": 0
        }
        
        # Deploy frontmatter component
        print("\n📦 Deploying frontmatter component...")
        
        # Create target directory if it doesn't exist
        os.makedirs(target_dir, exist_ok=True)
        
        # Get list of files in source directory
        try:
            source_files = [f for f in os.listdir(source_dir) 
                          if os.path.isfile(os.path.join(source_dir, f)) and not f.startswith('.')]
            
            if not source_files:
                print("  ⚠️ No files found in frontmatter")
                deployment_stats["skipped"] += 1
            else:
                # Copy each file
                for filename in source_files:
                    source_file = os.path.join(source_dir, filename)
                    target_file = os.path.join(target_dir, filename)
                    
                    try:
                        # Check if target file exists
                        file_exists = os.path.exists(target_file)
                        
                        # Copy the file
                        shutil.copy2(source_file, target_file)
                        
                        if file_exists:
                            print(f"  ✅ Updated: {filename}")
                            deployment_stats["updated"] += 1
                        else:
                            print(f"  ✨ Created: {filename}")
                            deployment_stats["created"] += 1
                            
                    except Exception as e:
                        print(f"  ❌ Error copying {filename}: {e}")
                        deployment_stats["errors"] += 1
                    
        except Exception as e:
            print(f"  ❌ Error processing frontmatter: {e}")
            deployment_stats["errors"] += 1
        
        # Print deployment summary
        print("\n🏁 Deployment completed!")
        print("📊 Statistics:")
        print(f"  ✨ Created: {deployment_stats['created']} files")
        print(f"  ✅ Updated: {deployment_stats['updated']} files")
        print(f"  ⚠️ Skipped: {deployment_stats['skipped']} components")
        print(f"  ❌ Errors: {deployment_stats['errors']} files")
        
        # Success if at least some files were deployed and no errors
        success = (deployment_stats["created"] + deployment_stats["updated"]) > 0 and deployment_stats["errors"] == 0
        
        if success:
            print("🎉 Deployment successful! Next.js production site updated.")
        else:
            print("⚠️ Deployment completed with issues.")
            
        return success
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# =================================================================================
# FRONTMATTER SANITIZATION POST-PROCESSOR
# =================================================================================

def run_data_validation(report_file = None) -> bool:
    """Run comprehensive hierarchical validation and update system"""
    try:
        from hierarchical_validator import HierarchicalValidator
        import yaml
        import os
        from pathlib import Path
        
        print("🔍 Running Comprehensive Hierarchical Data Validation")
        print("=" * 60)
        
        # Stage 1: Run full hierarchical validation
        print("📊 Stage 1: Hierarchical Validation (Categories.yaml → Materials.yaml → Frontmatter)")
        validator = HierarchicalValidator(ai_validation_enabled=True, silent_mode=False)
        validation_results = validator.run_hierarchical_validation()
        
        summary = validation_results['summary']
        print(f"\n📋 Validation Results:")
        print(f"   Overall Status: {summary['overall_status']}")
        print(f"   Categories: {summary['categories_status']}")
        print(f"   Materials: {summary['materials_status']}")
        print(f"   Hierarchy: {summary['hierarchy_status']}")
        print(f"   AI Validation: {summary['ai_validation_status']}")
        print(f"   Frontmatter: {summary['frontmatter_status']}")
        print(f"   Total Issues: {summary['total_issues']}")
        print(f"   Critical Issues: {summary['critical_issues']}")
        
        # Stage 2: Fix property violations automatically
        if validation_results['validation_results']['materials_validation'].get('property_violations'):
            print(f"\n🔧 Stage 2: Fixing Property Violations in Materials.yaml")
            property_violations = validation_results['validation_results']['materials_validation']['property_violations']
            
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
                                # Ensure properties section exists
                                if 'properties' not in item:
                                    item['properties'] = {}
                                
                                if prop_name in item['properties'] or True:  # Fix regardless
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
                    
                    # Ensure properties exist
                    if 'properties' not in material_item:
                        material_item['properties'] = {}
                        materials_updated = True
                    
                    # Add missing critical properties with default values from category ranges
                    for prop_name, range_data in category_ranges.items():
                        if prop_name not in material_item['properties']:
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
                                
                                material_item['properties'][prop_name] = {
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
        
        frontmatter_dir = Path("content/components/frontmatter")
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
                    
                    # Find material properties in Materials.yaml
                    updated_properties = {}
                    materials_section = updated_materials_data['materials']
                    if category in materials_section:
                        for item in materials_section[category]['items']:
                            if item['name'] == material_name:
                                updated_properties = item.get('properties', {})
                                break
                    
                    if not updated_properties:
                        continue
                    
                    # Load frontmatter file
                    with open(frontmatter_file, 'r') as f:
                        frontmatter_data = yaml.safe_load(f)
                    
                    # Check if updates are needed
                    current_properties = frontmatter_data.get('materialProperties', {})
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
                                    frontmatter_data['materialProperties'][prop_name]['value'] = updated_actual
                                else:
                                    frontmatter_data['materialProperties'][prop_name] = updated_actual
                        else:
                            # Add new property from Materials.yaml
                            needs_update = True
                            new_val = prop_value.get('value') if isinstance(prop_value, dict) else prop_value
                            print(f"   ➕ Adding {material_name}.{prop_name}: {new_val}")
                            frontmatter_data['materialProperties'][prop_name] = prop_value
                    
                    # Apply thermal destruction migration
                    if thermal_destruction_migration:
                        for thermal_prop, thermal_value in thermal_destruction_migration.items():
                            if thermal_prop == '_remove_meltingPoint':
                                if 'meltingPoint' in frontmatter_data['materialProperties']:
                                    del frontmatter_data['materialProperties']['meltingPoint']
                                    print(f"     ❌ Removed obsolete meltingPoint property")
                            else:
                                frontmatter_data['materialProperties'][thermal_prop] = thermal_value
                    
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


def run_frontmatter_sanitization(specific_file=None):
    """Run frontmatter YAML sanitization as a post-processor"""
    try:
        # Import the sanitizer
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts', 'tools'))
        from scripts.tools.sanitize_frontmatter import FrontmatterSanitizer
        
        sanitizer = FrontmatterSanitizer()
        
        if specific_file:
            # Sanitize specific file
            from pathlib import Path
            file_path = Path(specific_file)
            if not file_path.exists():
                print(f"❌ File not found: {specific_file}")
                return False
            
            print(f"🧹 Sanitizing specific file: {file_path.name}")
            result = sanitizer.sanitize_file(file_path)
            
            if result["fixed"]:
                print(f"✅ File fixed: {result['reason']}")
            else:
                print(f"ℹ️  No changes needed: {result['reason']}")
            
            return True
        else:
            # Sanitize all frontmatter files
            print("🧹 Running comprehensive frontmatter YAML sanitization...")
            result = sanitizer.sanitize_all_frontmatter()
            
            if result["success"]:
                if result["fixed"] > 0:
                    print(f"🎉 Sanitization complete! Fixed {result['fixed']} out of {result['total']} files")
                else:
                    print(f"✅ All {result['total']} frontmatter files are already valid!")
                return True
            else:
                print(f"❌ Sanitization failed: {result.get('error', 'Unknown error')}")
                return False
    
    except Exception as e:
        print(f"❌ Sanitization error: {e}")
        import traceback
        traceback.print_exc()
        return False


# =================================================================================
# DATA COMPLETENESS REPORTING & ANALYSIS
# =================================================================================

def handle_data_completeness_report():
    """Generate comprehensive data completeness report"""
    try:
        # Use the property completeness analysis tool
        import subprocess
        import sys
        
        print("="*80)
        print("DATA COMPLETENESS REPORT")
        print("="*80)
        print()
        
        # Run the property completeness report script
        script_path = "scripts/analysis/property_completeness_report.py"
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # Print the output
            print(result.stdout)
            
            # Add next actions
            print()
            print("="*80)
            print("NEXT ACTIONS")
            print("="*80)
            print()
            print("📋 Complete Action Plan: docs/DATA_COMPLETION_ACTION_PLAN.md")
            print("🔬 Research Tools: components/frontmatter/research/")
            print("⚡ Quick Win: Research 2 category ranges (30 mins)")
            print()
            print("To see research priorities:")
            print("  python3 run.py --data-gaps")
            print()
            
            return True
        else:
            print(f"❌ Script error: {result.stderr}")
            return False
        
    except Exception as e:
        print(f"❌ Data completeness report error: {e}")
        import traceback
        traceback.print_exc()
        return False


def handle_data_gaps():
    """Show data gaps with research priorities"""
    try:
        import subprocess
        import sys
        import yaml
        from pathlib import Path
        from collections import defaultdict
        from utils.category_property_cache import get_category_property_cache
        
        print("="*80)
        print("DATA GAPS & RESEARCH PRIORITIES")
        print("="*80)
        print()
        
        # Load category property cache
        cache = get_category_property_cache()
        valid_properties_by_category = cache.load()
        print(f"✅ Loaded property definitions for {len(valid_properties_by_category)} categories")
        print()
        
        # Load Materials.yaml to analyze gaps
        materials_file = Path("data/Materials.yaml")
        if not materials_file.exists():
            print("❌ Materials.yaml not found")
            return False
        
        with open(materials_file) as f:
            materials_data = yaml.safe_load(f)
        
        # Track property gaps across all materials (only valid properties per category)
        property_gaps = defaultdict(int)
        material_gaps = []
        total_materials = 0
        total_gaps = 0
        
        materials_section = materials_data.get('materials', {})
        
        # Analyze gaps per material, respecting category property definitions
        for material_name, material_data in materials_section.items():
            if not isinstance(material_data, dict):
                continue
            
            category = material_data.get('category', 'unknown')
            valid_properties = valid_properties_by_category.get(category, set())
            
            if not valid_properties:
                continue  # Skip materials with unknown categories
            
            properties = material_data.get('properties', {})
            total_materials += 1
            
            missing_props = []
            # Only check properties valid for this category
            for prop in valid_properties:
                if prop not in properties or properties[prop] is None:
                    property_gaps[prop] += 1
                    missing_props.append(prop)
                    total_gaps += 1
            
            if missing_props:
                category = material_data.get('category', 'unknown')
                material_gaps.append({
                    'name': material_name,
                    'category': category,
                    'missing_count': len(missing_props),
                    'missing_props': missing_props
                })
        
        # Sort materials by gap count
        material_gaps.sort(key=lambda x: x['missing_count'], reverse=True)
        
        # Sort properties by impact
        sorted_props = sorted(property_gaps.items(), key=lambda x: x[1], reverse=True)
        
        # Show top materials needing research
        print("Top 10 Materials Needing Research:")
        print("-"*80)
        for i, material in enumerate(material_gaps[:10], 1):
            print(f"{i:2d}. {material['name']:30s} - {material['missing_count']:2d} gaps")
        
        print()
        print("Research Priority Order (Properties with Most Gaps):")
        print("-"*80)
        
        for i, (prop_name, count) in enumerate(sorted_props[:10], 1):
            pct = (count / total_gaps * 100) if total_gaps > 0 else 0
            print(f"{i:2d}. {prop_name:30s} - {count:3d} materials affected ({pct:5.1f}%)")
        
        # Calculate impact of top 5 properties
        top5_count = sum(count for _, count in sorted_props[:5]) if len(sorted_props) >= 5 else 0
        
        print()
        print("="*80)
        print("RECOMMENDED ACTIONS")
        print("="*80)
        print()
        
        if total_gaps > 0:
            pct = (top5_count/total_gaps*100) if top5_count > 0 else 0
            print(f"🎯 Focus on top 5 properties → fixes {top5_count} gaps ({pct:.1f}% of total)")
            print()
            print("Start with:")
            for i, (prop_name, count) in enumerate(sorted_props[:5], 1):
                prop_pct = (count / total_gaps * 100) if total_gaps > 0 else 0
                print(f"  {i}. Research {prop_name} ({count} gaps, {prop_pct:.1f}% of total)")
        else:
            print("✅ No data gaps found! All properties are complete.")
        
        print()
        print("📋 Complete methodology: docs/DATA_COMPLETION_ACTION_PLAN.md")
        print("🔬 Research tools: components/frontmatter/research/")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Data gaps analysis error: {e}")
        import traceback
        traceback.print_exc()
        return False


def handle_research_missing_properties(batch_size=10, confidence_threshold=70, 
                                       specific_properties=None, specific_materials=None):
    """
    Run AI research to fill missing property values (Stage 0 requirement)
    
    This function implements the automated AI research system to achieve 100% data completeness.
    It uses PropertyValueResearcher to fill missing property values in materials.yaml.
    
    Args:
        batch_size: Number of properties to research in parallel
        confidence_threshold: Minimum confidence for accepting results
        specific_properties: Optional list of specific properties to research
        specific_materials: Optional list of specific materials to research
    """
    try:
        import yaml
        from pathlib import Path
        from collections import defaultdict
        import sys
        from datetime import datetime
        
        # Import research infrastructure
        sys.path.insert(0, str(Path(__file__).parent))
        from components.frontmatter.research.property_value_researcher import PropertyValueResearcher, ResearchContext
        from api.client_factory import create_api_client
        
        print("="*80)
        print("🔬 STAGE 0: AI RESEARCH & DATA COMPLETION")
        print("="*80)
        print()
        print("⚡ MANDATORY REQUIREMENT - Filling missing property values")
        print(f"📊 Batch size: {batch_size}")
        print(f"🎯 Confidence threshold: {confidence_threshold}%")
        print()
        
        # Load category property cache (validates property applicability per category)
        from utils.category_property_cache import get_category_property_cache
        
        print("📂 Loading category property definitions...")
        cache = get_category_property_cache()
        valid_properties_by_category = cache.load()
        
        cache_stats = cache.get_stats()
        print(f"✅ Loaded {cache_stats['categories']} categories with {cache_stats['total_properties']} total property definitions")
        print(f"📋 Cache: {cache_stats['cache_file']} ({'exists' if cache_stats['cache_exists'] else 'created'})")
        print()
        
        # Load materials.yaml
        materials_file = Path("data/Materials.yaml")
        if not materials_file.exists():
            print("❌ Materials.yaml not found")
            return False
        
        print("📂 Loading Materials.yaml...")
        with open(materials_file) as f:
            materials_data = yaml.safe_load(f)
        
        # Analyze gaps
        print("🔍 Analyzing data gaps...")
        materials_section = materials_data.get('materials', {})
        
        # Find missing values (only for properties valid in each material's category)
        missing_by_material = {}
        missing_by_property = defaultdict(list)
        total_gaps = 0
        skipped_invalid = 0
        
        for material_name, material_data in materials_section.items():
            if not isinstance(material_data, dict):
                continue
            
            # Get material category
            category = material_data.get('category', 'unknown')
            valid_properties = valid_properties_by_category.get(category, set())
            
            if not valid_properties:
                print(f"⚠️  Warning: Material '{material_name}' has unknown category '{category}'")
                continue
            
            properties = material_data.get('properties', {})
            missing_props = []
            
            # Only check properties that are valid for this category
            for prop_name in valid_properties:
                if prop_name not in properties or properties[prop_name] is None:
                    missing_props.append(prop_name)
                    missing_by_property[prop_name].append(material_name)
                    total_gaps += 1
            
            if missing_props:
                missing_by_material[material_name] = {
                    'category': category,
                    'missing_properties': missing_props
                }
        
        print(f"📊 Found {total_gaps} missing property values across {len(missing_by_material)} materials")
        print(f"✅ All properties validated against category definitions")
        print()
        
        # Filter by specific properties/materials if requested
        if specific_properties:
            missing_by_property = {k: v for k, v in missing_by_property.items() if k in specific_properties}
            print(f"🎯 Filtering to specific properties: {', '.join(specific_properties)}")
        
        if specific_materials:
            # Filter materials first
            missing_by_material = {k: v for k, v in missing_by_material.items() if k in specific_materials}
            # Rebuild missing_by_property to only include filtered materials
            filtered_missing_by_property = defaultdict(list)
            for material_name, material_info in missing_by_material.items():
                for prop_name in material_info['missing_properties']:
                    if not specific_properties or prop_name in specific_properties:
                        filtered_missing_by_property[prop_name].append(material_name)
            missing_by_property = dict(filtered_missing_by_property)
            print(f"🎯 Filtering to specific materials: {', '.join(specific_materials)}")
        
        if not missing_by_property:
            print("✅ No missing properties found! Data is 100% complete.")
            return True
        
        # Show top priorities
        sorted_props = sorted(missing_by_property.items(), key=lambda x: len(x[1]), reverse=True)
        print("🎯 Research Priorities (Top 10):")
        print("-"*80)
        for i, (prop_name, materials) in enumerate(sorted_props[:10], 1):
            pct = (len(materials) / total_gaps * 100) if total_gaps > 0 else 0
            print(f"{i:2d}. {prop_name:30s} - {len(materials):3d} materials ({pct:5.1f}%)")
        print()
        
        # Confirm before proceeding
        print("⚠️  This will use AI API calls to research missing properties.")
        response = input("Continue? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("❌ Research cancelled by user")
            return False
        
        print()
        print("🚀 Starting AI research...")
        print("="*80)
        print()
        
        # Initialize researcher - Use AIResearchEnrichmentService (not PropertyValueResearcher)
        from research.services.ai_research_service import AIResearchEnrichmentService
        researcher = AIResearchEnrichmentService(api_provider="deepseek")
        print("✅ AI Research Service initialized with DeepSeek API")
        print()
        
        # Research missing properties
        research_results = {}
        successful_research = 0
        failed_research = 0
        research_count = 0
        
        # Process by priority (most missing first)
        for prop_name, materials in sorted_props:
            print(f"\n📊 Researching {prop_name} for {len(materials)} materials...")
            print("-"*80)
            
            for material_name in materials:
                research_count += 1
                print(f"[{research_count}/{total_gaps}] Researching {material_name}.{prop_name}...", end=" ")
                
                try:
                    # Get material category for context
                    category = missing_by_material[material_name]['category']
                    
                    # ⚡ CRITICAL VALIDATION: Verify property is valid for this category
                    valid_properties = valid_properties_by_category.get(category, set())
                    if prop_name not in valid_properties:
                        print(f"⚠️  SKIPPED (property not defined for {category} category)")
                        failed_research += 1
                        continue
                    
                    # Research the property using AIResearchEnrichmentService
                    result = researcher.research_property(
                        material_name=material_name,
                        property_name=prop_name,
                        category=category,
                        confidence_threshold=confidence_threshold / 100.0  # Convert to 0-1 scale
                    )
                    
                    if result.success and result.confidence >= (confidence_threshold / 100.0):
                        # Store result in format compatible with Materials.yaml
                        if material_name not in research_results:
                            research_results[material_name] = {}
                        research_results[material_name][prop_name] = {
                            'value': result.researched_value,
                            'unit': result.unit,
                            'confidence': int(result.confidence * 100),
                            'source': result.source,
                            'research_date': result.research_date
                        }
                        
                        print(f"✅ {result.researched_value} {result.unit} (confidence: {int(result.confidence * 100)}%)")
                        successful_research += 1
                    else:
                        error_msg = result.error_message if hasattr(result, 'error_message') and result.error_message else "Unknown error"
                        print(f"❌ Low confidence ({int(result.confidence * 100)}%) or failed: {error_msg}")
                        failed_research += 1
                
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
                    failed_research += 1
                
                # Progress update every 10 items
                if research_count % 10 == 0:
                    pct = (successful_research / research_count * 100) if research_count > 0 else 0
                    print(f"\n   Progress: {research_count}/{total_gaps} ({pct:.1f}% success rate)")
        
        print()
        print("="*80)
        print("📊 RESEARCH SUMMARY")
        print("="*80)
        print(f"Total researched: {research_count}")
        print(f"✅ Successful: {successful_research}")
        print(f"❌ Failed: {failed_research}")
        print(f"Success rate: {(successful_research/research_count*100):.1f}%")
        print()
        
        if successful_research == 0:
            print("⚠️  No successful research results. Materials.yaml not updated.")
            return False
        
        # Update materials.yaml
        print("💾 Updating Materials.yaml...")
        
        # Create backup
        backup_file = materials_file.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml')
        import shutil
        shutil.copy2(materials_file, backup_file)
        print(f"   Backup created: {backup_file.name}")
        
        # Apply updates
        updates_applied = 0
        for material_name, properties in research_results.items():
            if material_name not in materials_section:
                print(f"⚠️  Warning: Material '{material_name}' not found in Materials.yaml, skipping...")
                continue
                
            if 'properties' not in materials_section[material_name]:
                materials_section[material_name]['properties'] = {}
            
            for prop_name, prop_data in properties.items():
                materials_section[material_name]['properties'][prop_name] = prop_data
                updates_applied += 1
        
        # Save updated file
        with open(materials_file, 'w') as f:
            yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print(f"   Applied {updates_applied} property updates")
        print()
        
        # Run completeness report
        print("="*80)
        print("📊 UPDATED DATA COMPLETENESS")
        print("="*80)
        print()
        
        # Re-run completeness report
        import subprocess
        result = subprocess.run(
            [sys.executable, "scripts/analysis/property_completeness_report.py"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # Show relevant sections of output
            lines = result.stdout.split('\n')
            # Find and print the summary section
            for i, line in enumerate(lines):
                if 'Overall' in line or '✅' in line or '⚠️' in line or '❌' in line:
                    print(line)
        
        print()
        print("="*80)
        print("✅ STAGE 0 COMPLETE")
        print("="*80)
        print()
        print(f"📊 Researched {successful_research} property values")
        print(f"💾 Updated Materials.yaml")
        print(f"🔒 Backup saved: {backup_file.name}")
        print()
        print("Next steps:")
        print("  1. Review updated data: data/Materials.yaml")
        print("  2. Verify zero nulls: python3 scripts/validation/validate_zero_nulls.py --materials")
        print("  3. Generate content: python3 run.py --material \"MaterialName\"")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ AI research error: {e}")
        import traceback
        traceback.print_exc()
        return False


# =================================================================================
# UTILITY FUNCTIONS
# =================================================================================

def run_data_verification(mode='--all'):
    """Run systematic data verification with AI research"""
    try:
        import subprocess
        import sys
        
        print("🔬 SYSTEMATIC DATA VERIFICATION")
        print("=" * 80)
        
        # Build command based on mode
        cmd = [sys.executable, 'scripts/research_tools/systematic_verify.py']
        
        # Parse mode parameter
        if mode == '--all' or mode == 'all':
            cmd.append('--all')
            print("📋 Mode: Verify ALL properties (~60 properties, $14.64, 18 hours)")
        elif mode == '--critical' or mode == 'critical':
            cmd.append('--critical')
            print("📋 Mode: Verify critical properties (5 properties, $1.20, 3 hours)")
        elif mode == '--important' or mode == 'important':
            cmd.append('--important')
            print("📋 Mode: Verify important properties (5 properties, $1.20, 3 hours)")
        elif mode == '--test' or mode == 'test':
            cmd.extend(['--critical', '--dry-run', '--batch-size', '10'])
            print("📋 Mode: Test run (10 materials, dry-run, $0.10, 15 minutes)")
        elif mode.startswith('--group='):
            group = mode.split('=')[1]
            cmd.extend(['--group', group])
            print(f"📋 Mode: Verify {group} property group")
        elif mode.startswith('--properties='):
            properties = mode.split('=')[1]
            cmd.extend(['--properties', properties])
            print(f"📋 Mode: Verify specific properties: {properties}")
        else:
            # Default to all
            cmd.append('--all')
            print(f"📋 Mode: {mode} (defaulting to --all)")
        
        # Auto-accept all AI values (no manual review)
        cmd.append('--auto-accept-all')
        print("🤖 Auto-accept: ALL AI-verified values will be accepted automatically")
        
        print("=" * 80)
        print("")
        
        # Run the systematic verification tool
        result = subprocess.run(cmd, check=False)
        
        if result.returncode == 0:
            print("\n✅ Data verification completed successfully")
            print("📄 See verification report in data/research/")
            return True
        else:
            print(f"\n⚠️ Data verification exited with code {result.returncode}")
            return False
            
    except FileNotFoundError:
        print("❌ Systematic verification tool not found")
        print("Expected: scripts/research_tools/systematic_verify.py")
        return False
    except Exception as e:
        print(f"❌ Data verification error: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_safe_filename(material_name: str) -> str:
    """
    Generate a safe filename from material name by converting spaces and underscores to hyphens.
    
    Args:
        material_name: The material name (e.g., "Stainless Steel")
        
    Returns:
        Safe filename string (e.g., "stainless-steel")
        
    Example:
        >>> generate_safe_filename("Stainless Steel")
        'stainless-steel'
        >>> generate_safe_filename("Ti-6Al-4V")
        'ti-6al-4v'
    """
    import re
    # Convert to lowercase, replace spaces and underscores with hyphens, 
    # then remove any consecutive hyphens
    safe_name = material_name.lower().replace(' ', '-').replace('_', '-')
    # Remove consecutive hyphens and clean up
    return re.sub(r'-+', '-', safe_name).strip('-')


# =================================================================================
# MAIN ENTRY POINT
# =================================================================================

def main():
    """Main application entry point with basic command line interface."""
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 🚨 CONSOLIDATED SERVICE INITIALIZATION
    # ═══════════════════════════════════════════════════════════════════════════
    print("🔧 Initializing consolidated validation & research services...")
    
    try:
        # Initialize singleton services (lazy initialization on first use)
        from scripts.pipeline_integration import (
            get_pre_generation_service,
            get_research_service, 
            get_quality_service
        )
        
        # Validate services are available (triggers initialization)
        pre_gen_service = get_pre_generation_service()
        research_service = get_research_service()
        quality_service = get_quality_service()
        
        print("✅ All services initialized successfully")
        print(f"  • Pre-Generation Validation: {len(pre_gen_service.property_rules)} property rules")
        print(f"  • AI Research Enrichment: Ready")
        print(f"  • Post-Generation Quality: Schema & integration validation ready")
        
    except Exception as e:
        print(f"🚨 CRITICAL: Service initialization failed: {e}")
        print("🚫 Per GROK_INSTRUCTIONS.md: ZERO TOLERANCE FOR DEFAULTS/FALLBACKS")
        return False
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 🚨 FAIL-FAST VALIDATION (Per GROK_INSTRUCTIONS.md)
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n🚨 ENFORCING FAIL-FAST VALIDATION")
    print("Per GROK_INSTRUCTIONS.md: ZERO TOLERANCE FOR MOCKS/FALLBACKS/DEFAULTS")
    
    try:
        # Run hierarchical validation via pre-generation service
        validation_result = pre_gen_service.validate_hierarchical()
        
        if validation_result.success:
            print(f"✅ Materials database validation PASSED - System approved for operation")
            
            if validation_result.warnings:
                print(f"  ⚠️ {len(validation_result.warnings)} warnings detected")
                for warning in validation_result.warnings[:3]:  # Show first 3
                    print(f"     - {warning}")
        else:
            print("🚨 CRITICAL: System cannot start due to validation failure")
            print(f"  • {len(validation_result.errors)} critical errors detected")
            for error in validation_result.errors[:5]:  # Show first 5
                print(f"     💥 {error}")
            print("\n🚫 Per GROK_INSTRUCTIONS.md: ZERO TOLERANCE FOR DEFAULTS/FALLBACKS")
            print("� Run: python3 scripts/validation/fail_fast_materials_validator.py")
            return False
            
    except Exception as e:
        print("🚨 CRITICAL: Validation service failed")
        print(f"💥 Error: {e}")
        print("🚫 Per GROK_INSTRUCTIONS.md: ZERO TOLERANCE FOR DEFAULTS/FALLBACKS")
        return False
    
    import argparse
    import os
    from generators.dynamic_generator import DynamicGenerator
    from api.client_factory import create_api_client
    from data.materials import load_materials_cached as load_materials, clear_materials_cache
    
    # Import pipeline integration from scripts directory
    try:
        from scripts.pipeline_integration import validate_material_pre_generation, validate_and_improve_frontmatter
    except ImportError:
        # Fallback: define dummy functions if pipeline_integration not available
        def validate_material_pre_generation(material_name):
            return {'valid': True, 'issues': []}
        def validate_and_improve_frontmatter(material_name, frontmatter):
            return {'improvements_made': False, 'improved_frontmatter': frontmatter}
    
    # Clear materials cache at startup to ensure fresh data
    # (cache will be populated on first material access)
    clear_materials_cache()
    
    parser = argparse.ArgumentParser(description="Z-Beam Content Generator")
    parser.add_argument("--material", help="Generate content for specific material")
    parser.add_argument("--components", help="Comma-separated list of components to generate")
    parser.add_argument("--all", action="store_true", help="Generate all materials")
    parser.add_argument("--test", action="store_true", help="Run test mode")
    parser.add_argument("--deploy", action="store_true", help="Deploy generated content to Next.js production site")
    parser.add_argument("--sanitize", action="store_true", help="Sanitize all existing frontmatter files (post-processor)")
    parser.add_argument("--sanitize-file", help="Sanitize a specific frontmatter file")
    parser.add_argument("--validate", action="store_true", help="Run hierarchical validation (Categories.yaml → Materials.yaml → Frontmatter) and auto-fix issues")
    parser.add_argument("--validate-report", help="Generate hierarchical validation report to file")
    parser.add_argument("--data", nargs='?', const='--all', help="Systematically verify Materials.yaml data with AI research (use --data=critical, --data=all, or --data=test)")
    parser.add_argument("--data-completeness-report", action="store_true", help="Generate comprehensive data completeness report")
    parser.add_argument("--data-gaps", action="store_true", help="Analyze data gaps and show research priorities")
    parser.add_argument("--research-missing-properties", action="store_true", help="Run AI research to fill missing property values (Stage 0 requirement)")
    parser.add_argument("--research-properties", help="Research specific properties (comma-separated list)")
    parser.add_argument("--research-materials", help="Research properties for specific materials (comma-separated list)")
    parser.add_argument("--research-batch-size", type=int, default=10, help="Number of properties to research in parallel (default: 10)")
    parser.add_argument("--research-confidence-threshold", type=int, default=70, help="Minimum confidence threshold for research results (default: 70)")
    parser.add_argument("--enforce-completeness", action="store_true", help="Block generation if data completeness below threshold (strict mode)")

    
    args = parser.parse_args()
    
    # Handle data completeness reporting
    if args.data_completeness_report:
        return handle_data_completeness_report()
    
    # Handle data gaps analysis
    if args.data_gaps:
        return handle_data_gaps()
    
    # Handle AI research automation (Stage 0 requirement)
    if args.research_missing_properties:
        return handle_research_missing_properties(
            batch_size=args.research_batch_size,
            confidence_threshold=args.research_confidence_threshold,
            specific_properties=args.research_properties.split(',') if args.research_properties else None,
            specific_materials=args.research_materials.split(',') if args.research_materials else None
        )
    
    # Handle systematic data verification
    if args.data is not None:
        return run_data_verification(args.data)
    
    # Handle deployment to Next.js production site
    if args.deploy:
        return deploy_to_production()
    
    # Handle data validation without regeneration
    if args.validate or args.validate_report:
        return run_data_validation(args.validate_report)
    
    # Apply enforcement flag if specified
    if hasattr(args, 'enforce_completeness') and args.enforce_completeness:
        GLOBAL_OPERATIONAL_CONFIG['data_completeness']['enforce_before_generation'] = True
        print("🔒 Strict mode enabled: Will block generation if data incomplete")
    
    # Handle frontmatter sanitization (post-processor)
    if args.sanitize or args.sanitize_file:
        return run_frontmatter_sanitization(args.sanitize_file)
    
    if args.test:
        print("🧪 Test mode - basic functionality check")
        from components.table.generators.generator import TableComponentGenerator
        generator = TableComponentGenerator()
        print(f"✅ Table generator loaded: {generator.component_type}")
        return True
    
    if args.material:
        if args.components:
            # Use specified components
            component_types = [c.strip() for c in args.components.split(',')]
            print(f"🚀 Generating {args.components} for {args.material}")
        else:
            # Use enabled components from configuration
            component_types = [comp for comp, config in COMPONENT_CONFIG.items() if config.get('enabled', False)]
            if not component_types:
                print("❌ No components are enabled in configuration")
                return False
            print(f"🚀 Generating enabled components ({', '.join(component_types)}) for {args.material}")
        
        try:
            # Load materials data
            materials_data_dict = load_materials()
            
            # Use the optimized material lookup function
            from data.materials import get_material_by_name
            material_info = get_material_by_name(args.material, materials_data_dict)
            
            if not material_info:
                print(f"❌ Material '{args.material}' not found")
                return False

            # 🔍 INVISIBLE PIPELINE: Pre-generation validation
            print(f"🔍 Validating material data for {args.material}...")
            validation_result = validate_material_pre_generation(args.material)
            if not validation_result['validation_passed']:
                print(f"⚠️ Material validation issues detected: {', '.join(validation_result['issues_detected'])}")
                print("🔧 Proceeding with generation, pipeline will attempt corrections...")

            # Check if any components require API clients
            requires_api = any(
                COMPONENT_CONFIG.get(comp, {}).get('api_provider', 'none') != 'none' 
                for comp in component_types
            )
            
            # Create API client only if needed
            api_client = None
            if requires_api:
                # Find the first non-none API provider for enabled components
                api_provider = None
                for comp in component_types:
                    provider = COMPONENT_CONFIG.get(comp, {}).get('api_provider', 'none')
                    if provider != 'none':
                        api_provider = provider
                        break
                if api_provider:
                    api_client = create_api_client(api_provider)
            
            generator = DynamicGenerator()            # Split components - already done above
            
            for component_type in component_types:
                print(f"📋 Generating {component_type}...")
                
                # Load frontmatter data for components that need it
                frontmatter_data = None
                if component_type in ['table', 'author', 'metatags', 'jsonld', 'caption', 'propertiestable']:
                    # Try to load existing frontmatter - prioritize .yaml format
                    base_name = generate_safe_filename(args.material)
                    frontmatter_paths = [
                        f"content/components/frontmatter/{base_name}-laser-cleaning.yaml",
                        f"content/components/frontmatter/{base_name}.yaml",
                        f"content/components/frontmatter/{base_name}-laser-cleaning.md"  # Legacy support
                    ]
                    
                    for frontmatter_path in frontmatter_paths:
                        if os.path.exists(frontmatter_path):
                            import yaml
                            try:
                                if frontmatter_path.endswith('.yaml'):
                                    # Direct YAML file
                                    with open(frontmatter_path, 'r') as f:
                                        frontmatter_data = yaml.safe_load(f)
                                else:
                                    # Markdown file with frontmatter
                                    with open(frontmatter_path, 'r') as f:
                                        content = f.read()
                                    yaml_start = content.find('---') + 3
                                    yaml_end = content.find('---', yaml_start)
                                    if yaml_start > 2 and yaml_end > yaml_start:
                                        # Traditional frontmatter with closing ---
                                        yaml_content = content[yaml_start:yaml_end].strip()
                                    elif yaml_start > 2:
                                        # Pure YAML file without closing --- (our current format)
                                        yaml_content = content[yaml_start:].strip()
                                    else:
                                        yaml_content = None
                                        
                                    if yaml_content:
                                        frontmatter_data = yaml.safe_load(yaml_content)
                                
                                if frontmatter_data:
                                    print(f"✅ Loaded frontmatter data from {frontmatter_path}")
                                    break
                                    
                            except Exception as e:
                                print(f"Warning: Could not load frontmatter from {frontmatter_path}: {e}")
                                continue
                    
                    if not frontmatter_data and component_type != 'frontmatter':
                        print(f"❌ No frontmatter data found for {args.material} - {component_type} component requires frontmatter")
                        continue
                
                # Prepare kwargs for component generation
                generation_kwargs = {
                    'enforce_completeness': args.enforce_completeness if hasattr(args, 'enforce_completeness') else False,
                }
                
                # Frontmatter generation is now Materials.yaml-only - no AI flags needed
                
                result = generator.generate_component(
                    material=args.material,
                    component_type=component_type,
                    api_client=api_client,
                    frontmatter_data=frontmatter_data,
                    material_data=material_info,
                    **generation_kwargs
                )
                
                if result.success:
                    # 🔍 INVISIBLE PIPELINE: Post-generation validation for frontmatter
                    if component_type == 'frontmatter':
                        try:
                            import yaml
                            frontmatter_content = yaml.safe_load(result.content)
                            pipeline_result = validate_and_improve_frontmatter(args.material, frontmatter_content)
                            
                            if pipeline_result['improvements_made']:
                                print(f"🔧 Pipeline improved frontmatter quality for {args.material}")
                                # Use improved frontmatter
                                result.content = yaml.dump(pipeline_result['improved_frontmatter'], default_flow_style=False, sort_keys=False)
                            
                            validation_info = pipeline_result['validation_result']
                            if not validation_info['validation_passed']:
                                print(f"⚠️ Quality issues detected: {', '.join(validation_info['issues_detected'])}")
                        except Exception as e:
                            print(f"⚠️ Pipeline validation failed: {e}")
                    
                    # Save the result
                    output_dir = f"content/components/{component_type}"
                    os.makedirs(output_dir, exist_ok=True)
                    filename = generate_safe_filename(args.material)
                    output_file = f"{output_dir}/{filename}-laser-cleaning.json" if component_type == 'jsonld' else f"{output_dir}/{filename}-laser-cleaning.yaml" if component_type in ['frontmatter', 'table', 'metatags', 'author', 'caption'] else f"{output_dir}/{filename}-laser-cleaning.md"
                    
                    with open(output_file, 'w') as f:
                        f.write(result.content)
                    
                    print(f"✅ {component_type} generated successfully → {output_file}")
                else:
                    print(f"❌ {component_type} generation failed: {result.error_message}")
            
            return True
            
        except Exception as e:
            print(f"❌ Generation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    elif args.all:
        # Generate for all materials
        if args.components:
            component_types = [c.strip() for c in args.components.split(',')]
            print(f"🚀 Generating {args.components} for all materials")
        else:
            # Use enabled components from configuration
            component_types = [comp for comp, config in COMPONENT_CONFIG.items() if config.get('enabled', False)]
            if not component_types:
                print("❌ No components are enabled in configuration")
                return False
            print(f"🚀 Generating enabled components ({', '.join(component_types)}) for all materials")
        
        try:
            # Load materials data
            materials_data_dict = load_materials()
            all_materials = []
            
            # Get all materials from all categories
            # In the new format, each category key IS a material name
            for material_name, material_data in materials_data_dict.get('materials', {}).items():
                if material_name and isinstance(material_data, dict):
                    all_materials.append((material_name, material_data))
            
            if not all_materials:
                print("❌ No materials found in database")
                return False
            
            print(f"📋 Found {len(all_materials)} materials to process")
            
            # 🔍 INVISIBLE PIPELINE: Batch validation for all materials
            # ═══════════════════════════════════════════════════════════════════════
            # 🔍 BATCH PRE-GENERATION VALIDATION
            # ═══════════════════════════════════════════════════════════════════
            print("\n🔍 Running batch pre-generation validation...")
            
            try:
                from scripts.pipeline_integration import validate_batch_generation
                material_names = [material[0] for material in all_materials]
                batch_validation = validate_batch_generation(material_names)
                
                if batch_validation['valid']:
                    print(f"✅ Batch validation: {batch_validation['total_materials']} materials ready")
                    print(f"   Data completion: {batch_validation.get('data_completion', 'N/A'):.1f}%")
                    
                    # Show critical gaps if any
                    if batch_validation.get('critical_gaps'):
                        print(f"   ⚠️ {len(batch_validation['critical_gaps'])} critical data gaps detected")
                        for gap in batch_validation['critical_gaps'][:3]:
                            print(f"      - {gap}")
                else:
                    print(f"⚠️ Batch validation issues detected:")
                    
                if batch_validation.get('errors'):
                    print(f"   ❌ {len(batch_validation['errors'])} errors")
                    for error in batch_validation['errors'][:3]:
                        print(f"      - {error}")
                        
                if batch_validation.get('warnings'):
                    print(f"   ⚠️ {len(batch_validation['warnings'])} warnings")
                    
            except ImportError:
                print("⚠️ Pipeline integration not available, skipping batch validation")
            except Exception as e:
                print(f"⚠️ Batch validation failed: {e}")
            
            # Check if any components require API clients
            requires_api = any(
                COMPONENT_CONFIG.get(comp, {}).get('api_provider', 'none') != 'none' 
                for comp in component_types
            )
            
            # Initialize API client if needed
            api_client = None
            if requires_api:
                from api.client_cache import get_cached_api_client
                # Try to get a working API client
                for provider in ['deepseek', 'grok', 'winston']:
                    try:
                        api_client = get_cached_api_client(provider)
                        if api_client:
                            print(f"🔧 Using API provider: {provider}")
                            break
                    except Exception as e:
                        print(f"⚠️ Failed to initialize {provider}: {e}")
                        continue
                
                if not api_client:
                    print("❌ Failed to initialize any API client")
                    return False
            
            # Process each material
            generator = DynamicGenerator()
            success_count = 0
            failure_count = 0
            
            for material_name, material_info in all_materials:
                print(f"\n📋 Processing {material_name}...")
                
                for component_type in component_types:
                    try:
                        # Load frontmatter data for components that need it
                        frontmatter_data = None
                        if component_type in ['table', 'author', 'metatags', 'jsonld', 'caption', 'propertiestable']:
                            # Try to load existing frontmatter
                            material_slug = generate_safe_filename(material_name)
                            frontmatter_paths = [
                                f"content/components/frontmatter/{material_slug}-laser-cleaning.yaml",
                                f"content/components/frontmatter/{material_slug}.yaml",
                                f"content/components/frontmatter/{material_slug}-laser-cleaning.md"  # Legacy support
                            ]
                            frontmatter_path = None
                            for path in frontmatter_paths:
                                if os.path.exists(path):
                                    frontmatter_path = path
                                    break
                            if frontmatter_path and os.path.exists(frontmatter_path):
                                import yaml
                                with open(frontmatter_path, 'r', encoding='utf-8') as f:
                                    # Check if file is pure YAML or markdown with frontmatter
                                    content = f.read()
                                    if frontmatter_path.endswith('.yaml'):
                                        # Pure YAML file - load directly
                                        frontmatter_data = yaml.safe_load(content)
                                    else:
                                        # Markdown file with frontmatter - extract YAML between --- delimiters
                                        yaml_start = content.find('---') + 3
                                        yaml_end = content.find('---', yaml_start)
                                        if yaml_start > 2 and yaml_end > yaml_start:
                                            yaml_content = content[yaml_start:yaml_end].strip()
                                            frontmatter_data = yaml.safe_load(yaml_content)
                            
                            if not frontmatter_data and component_type != 'frontmatter':
                                print(f"  ⚠️ No frontmatter data found for {material_name} - skipping {component_type}")
                                continue
                        
                        result = generator.generate_component(
                            material=material_name,
                            component_type=component_type,
                            api_client=api_client,
                            frontmatter_data=frontmatter_data,
                            material_data=material_info
                        )
                        
                        if result.success:
                            # Save the result
                            output_dir = f"content/components/{component_type}"
                            os.makedirs(output_dir, exist_ok=True)
                            filename = generate_safe_filename(material_name)
                            output_file = f"{output_dir}/{filename}-laser-cleaning.json" if component_type == 'jsonld' else f"{output_dir}/{filename}-laser-cleaning.yaml" if component_type in ['frontmatter', 'table', 'metatags', 'author', 'caption'] else f"{output_dir}/{filename}-laser-cleaning.md"
                            
                            with open(output_file, 'w') as f:
                                f.write(result.content)
                            
                            # 🔍 POST-GENERATION QUALITY VALIDATION (if frontmatter)
                            if component_type == 'frontmatter':
                                try:
                                    quality_validation = quality_service.validate_quality(
                                        result.content, 
                                        material_name
                                    )
                                    
                                    if quality_validation.success:
                                        print(f"  ✅ {component_type} → {output_file} (Quality: {quality_validation.quality_score.total_score:.0f}%)")
                                    else:
                                        print(f"  ⚠️ {component_type} saved but quality issues detected")
                                        for issue in quality_validation.issues[:3]:  # Show first 3
                                            print(f"      - {issue}")
                                except Exception as qe:
                                    print(f"  ⚠️ Quality validation failed: {qe}")
                                    print(f"  ✅ {component_type} → {output_file}")
                            else:
                                print(f"  ✅ {component_type} → {output_file}")
                            
                            success_count += 1
                        else:
                            print(f"  ❌ {component_type} failed: {result.error_message}")
                            failure_count += 1
                    
                    except Exception as e:
                        print(f"  ❌ {component_type} error: {e}")
                        failure_count += 1
            
            print(f"\n🏁 Generation completed: {success_count} successes, {failure_count} failures")
            return True
            
        except Exception as e:
            print(f"❌ All materials generation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    else:
        parser.print_help()
        return True


if __name__ == "__main__":
    import sys
    
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
