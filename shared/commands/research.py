#!/usr/bin/env python3
"""
Research Command Handlers

Handles AI research commands for data completion and gap analysis.
"""


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
        from materials.utils.category_property_cache import get_category_property_cache
        
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
        from materials.research.unified_material_research import PropertyValueResearcher, ResearchContext
        from shared.api.client_factory import create_api_client
        
        print("="*80)
        print("🔬 STAGE 0: AI RESEARCH & DATA COMPLETION")
        print("="*80)
        print()
        print("⚡ MANDATORY REQUIREMENT - Filling missing property values")
        print(f"📊 Batch size: {batch_size}")
        print(f"🎯 Confidence threshold: {confidence_threshold}%")
        print()
        
        # Load category property cache (validates property applicability per category)
        from materials.utils.category_property_cache import get_category_property_cache
        
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
        from materials.research.services.ai_research_service import AIResearchEnrichmentService
        researcher = AIResearchEnrichmentService(api_provider="grok")
        print("✅ AI Research Service initialized with Grok API")
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
                            'source': result.source
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


# Import from centralized utility
from shared.utils.filename import generate_safe_filename


# =================================================================================
# MAIN ENTRY POINT
# =================================================================================

