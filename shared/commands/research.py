#!/usr/bin/env python3
"""
Research Command Handlers

Handles AI research commands for data completion and gap analysis.
"""


def _determine_property_category(property_name: str) -> str:
    """
    Determine which category group a property belongs to.
    
    Returns 'material_characteristics' or 'laser_material_interaction'
    based on property name taxonomy.
    """
    try:
        from materials.utils.property_categorizer import get_property_categorizer
        categorizer = get_property_categorizer()
        category_id = categorizer.get_category(property_name)
        
        # Map category IDs to materialProperties group names
        if category_id in ['laser_material_interaction', 'optical', 'laser_absorption']:
            return 'laser_material_interaction'
        else:
            return 'material_characteristics'
    except Exception:
        # Default to material_characteristics if categorization fails
        return 'material_characteristics'


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
        materials_file = Path("data/materials/Materials.yaml")
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
            
            # Extract properties from GROUPED structure
            # materialProperties contains exactly two category groups:
            # - material_characteristics: Physical/thermal properties
            # - laser_material_interaction: Laser-specific properties
            # Each group has: label, description, and actual properties
            material_properties_section = material_data.get('materialProperties', {})
            
            # Flatten properties from both standard category groups
            properties = {}
            for group_name in ['material_characteristics', 'laser_material_interaction']:
                group_data = material_properties_section.get(group_name, {})
                if isinstance(group_data, dict):
                    for key, value in group_data.items():
                        # Skip metadata fields
                        if key in ('label', 'description', 'percentage'):
                            continue
                        properties[key] = value
            
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


def should_research_property(prop_value, confidence_threshold=70):
    """
    Determine if a property should be researched based on smart skip logic.
    
    Args:
        prop_value: The property value (could be None, dict, or scalar)
        confidence_threshold: Minimum confidence to skip research
        
    Returns:
        bool: True if property should be researched, False to skip
    """
    # Always research if value is None or missing
    if prop_value is None:
        return True
    
    # If it's not a dict, assume it's a simple value that exists
    if not isinstance(prop_value, dict):
        return False
    
    # Check if value field is missing or None
    value = prop_value.get('value')
    if value is None:
        return True
    
    # Check confidence - re-research if below threshold
    # Note: confidence might be stored as 'confidence' (0-1) or already as percentage
    confidence = prop_value.get('confidence', 1.0)
    
    # Convert to float if it's a string
    if isinstance(confidence, str):
        try:
            confidence = float(confidence)
        except (ValueError, TypeError):
            # If conversion fails, treat as missing confidence
            return True
    
    # Handle both formats: 0-1 scale and percentage
    if confidence < 1.0:
        confidence_pct = confidence * 100
    else:
        confidence_pct = confidence
    
    if confidence_pct < confidence_threshold:
        return True
    
    # Value exists and confidence is good - skip research
    return False


def handle_research_missing_properties(batch_size=10, confidence_threshold=70, 
                                       specific_properties=None, specific_materials=None,
                                       auto_mode=False):
    """
    Run AI research to fill missing property values (Stage 0 requirement)
    
    This function implements the automated AI research system to achieve 100% data completeness.
    It uses PropertyValueResearcher to fill missing property values in Materials.yaml.
    
    Args:
        batch_size: Number of properties to research in parallel
        confidence_threshold: Minimum confidence for accepting results
        specific_properties: Optional list of specific properties to research
        specific_materials: Optional list of specific materials to research
        auto_mode: If True, skip user confirmation (for workflow auto-remediation)
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
        
        # Load Materials.yaml
        materials_file = Path("data/materials/Materials.yaml")
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
        # SMART SKIP: Uses confidence thresholds and value checks
        missing_by_material = {}
        missing_by_property = defaultdict(list)
        total_gaps = 0
        skipped_good_values = 0
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
            
            properties = material_data.get('materialProperties', {})
            missing_props = []
            
            # Check inside category groups (FLAT structure per frontmatter_template.yaml)
            # Properties are DIRECTLY under material_characteristics/laser_material_interaction
            # NOT nested under a 'properties' key
            material_characteristics = properties.get('material_characteristics', {})
            laser_material_interaction = properties.get('laser_material_interaction', {})
            
            # Only check properties that are valid for this category
            for prop_name in valid_properties:
                # Check directly in category groups (excluding metadata keys)
                in_mc = (isinstance(material_characteristics, dict) and 
                        prop_name in material_characteristics and
                        prop_name not in ['label', 'description', 'percentage'])
                in_lmi = (isinstance(laser_material_interaction, dict) and 
                         prop_name in laser_material_interaction and
                         prop_name not in ['label', 'description', 'percentage'])
                
                # Find property value
                prop_value = None
                if in_mc:
                    prop_value = material_characteristics.get(prop_name)
                elif in_lmi:
                    prop_value = laser_material_interaction.get(prop_name)
                
                # Use smart skip logic to determine if research needed
                if should_research_property(prop_value, confidence_threshold):
                    missing_props.append(prop_name)
                    missing_by_property[prop_name].append(material_name)
                    total_gaps += 1
                else:
                    # Property exists with good value/confidence - skip
                    skipped_good_values += 1
            
            if missing_props:
                missing_by_material[material_name] = {
                    'category': category,
                    'missing_properties': missing_props
                }
        
        print(f"📊 Found {total_gaps} missing property values across {len(missing_by_material)} materials")
        print(f"✅ Skipped {skipped_good_values} properties with good values (confidence ≥ {confidence_threshold}%)")
        print("✅ All properties validated against category definitions")
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
        
        # Confirm before proceeding (skip in auto mode)
        if not auto_mode:
            print("⚠️  This will use AI API calls to research missing properties.")
            response = input("Continue? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("❌ Research cancelled by user")
                return False
        else:
            print("🤖 Auto-mode enabled - proceeding with research...")
        
        print()
        print("🚀 Starting AI research...")
        print("="*80)
        print()
        
        # Initialize researcher - Use AIResearchEnrichmentService (not PropertyValueResearcher)
        from materials.research.services.ai_research_service import AIResearchEnrichmentService
        researcher = AIResearchEnrichmentService(api_provider="grok")
        print("✅ AI Research Service initialized with Grok API")
        print()
        
        # Research missing properties - Save incrementally per material
        successful_research = 0
        failed_research = 0
        research_count = 0
        materials_updated = set()
        
        # Group properties by material for incremental saving
        properties_by_material = {}
        for prop_name, materials in sorted_props:
            for material_name in materials:
                if material_name not in properties_by_material:
                    properties_by_material[material_name] = []
                properties_by_material[material_name].append(prop_name)
        
        # Process each material completely, then save
        for mat_idx, (material_name, properties) in enumerate(properties_by_material.items(), 1):
            print(f"\n{'='*80}")
            print(f"📦 Material {mat_idx}/{len(properties_by_material)}: {material_name} ({len(properties)} properties)")
            print('='*80)
            
            material_results = {}
            category = missing_by_material[material_name]['category']
            valid_properties = valid_properties_by_category.get(category, set())
            
            for prop_name in properties:
                research_count += 1
                print(f"  [{research_count}/{total_gaps}] {prop_name}...", end=" ")
                
                try:
                    # Validate property is valid for this category
                    if prop_name not in valid_properties:
                        print(f"⚠️  SKIPPED (not valid for {category})")
                        failed_research += 1
                        continue
                    
                    # Research the property
                    result = researcher.research_property(
                        material_name=material_name,
                        property_name=prop_name,
                        category=category,
                        confidence_threshold=confidence_threshold / 100.0
                    )
                    
                    if result.success and result.confidence >= (confidence_threshold / 100.0):
                        # Write full citation schema to Materials.yaml
                        material_results[prop_name] = {
                            'value': result.researched_value,
                            'unit': result.unit,
                            'source': result.source,
                            'source_type': result.source_type,
                            'source_name': result.source_name,
                            'citation': result.citation,
                            'context': result.context,
                            'confidence': int(result.confidence * 100),
                            'researched_date': result.research_date,
                            'needs_validation': result.needs_validation
                        }
                        print(f"✅ {result.researched_value} {result.unit} ({int(result.confidence * 100)}%) - {result.source_name}")
                        successful_research += 1
                    else:
                        error_msg = result.error_message if hasattr(result, 'error_message') and result.error_message else "Unknown error"
                        print(f"❌ Low confidence or failed: {error_msg}")
                        failed_research += 1
                
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
                    failed_research += 1
            
            # SAVE IMMEDIATELY after each material completes
            if material_results:
                print(f"\n💾 Saving {len(material_results)} properties for {material_name}...")
                
                # Ensure category groups exist
                if 'materialProperties' not in materials_section[material_name]:
                    materials_section[material_name]['materialProperties'] = {}
                
                mat_props = materials_section[material_name]['materialProperties']
                if 'material_characteristics' not in mat_props:
                    mat_props['material_characteristics'] = {
                        'label': 'Material Characteristics',
                        'description': 'Intrinsic physical, mechanical, chemical, and structural properties affecting cleaning outcomes and material integrity'
                    }
                if 'laser_material_interaction' not in mat_props:
                    mat_props['laser_material_interaction'] = {
                        'label': 'Laser-Material Interaction',
                        'description': 'Optical and thermal properties governing laser energy absorption, reflection, propagation, and ablation thresholds'
                    }
                
                # Write properties to correct category groups
                for prop_name, prop_data in material_results.items():
                    category_group = _determine_property_category(prop_name)
                    mat_props[category_group][prop_name] = prop_data
                
                # Save to file immediately
                with open(materials_file, 'w') as f:
                    yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                
                materials_updated.add(material_name)
                print(f"✅ Saved to Materials.yaml")
            
            # Progress update
            pct = (successful_research / research_count * 100) if research_count > 0 else 0
            print(f"\n📊 Progress: {research_count}/{total_gaps} ({pct:.1f}% success), {len(materials_updated)} materials updated")
        
        print()
        print("="*80)
        print("📊 FINAL RESEARCH SUMMARY")
        print("="*80)
        print(f"Total properties researched: {research_count}")
        print(f"✅ Successful: {successful_research}")
        print(f"❌ Failed: {failed_research}")
        print(f"Success rate: {(successful_research/research_count*100):.1f}%")
        print(f"📦 Materials updated: {len(materials_updated)}")
        print()
        
        if successful_research == 0:
            print("⚠️  No successful research results.")
            return False
        
        print("✅ All updates saved incrementally to Materials.yaml")
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
        print(f"� Updated {len(materials_updated)} materials")
        print("� All changes saved incrementally")
        print()
        print("Next steps:")
        print("  1. Review updated data: materials/data/Materials.yaml")
        print("  2. Verify completeness: python3 run.py --data-completeness-report")
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


def handle_fix_analysis(material=None, failure_type=None):
    """
    Generate fix strategy effectiveness report.
    
    Args:
        material: Optional material filter
        failure_type: Optional failure type filter (uniform, borderline, partial, poor)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        from processing.detection.winston_feedback_db import WinstonFeedbackDatabase
        from processing.learning.fix_strategy_manager import FixStrategyManager
        from pathlib import Path
        
        print("=" * 80)
        print("🔧 FIX STRATEGY EFFECTIVENESS REPORT")
        print("=" * 80)
        print()
        
        # Get database path
        from processing.config.config_loader import get_config
        config = get_config()
        db_path = config.config.get('winston_feedback_db_path', 'data/winston_feedback.db')
        
        if not Path(db_path).exists():
            print(f"❌ Winston feedback database not found: {db_path}")
            print("   Run some generations first to collect data")
            return False
        
        # Initialize database and fix manager
        db = WinstonFeedbackDatabase(db_path)
        fix_manager = FixStrategyManager(db)
        
        # Generate report
        report = fix_manager.get_fix_effectiveness_report(
            material=material,
            failure_type=failure_type
        )
        
        if 'error' in report:
            print(f"❌ Error generating report: {report['error']}")
            return False
        
        # Display overall statistics
        overall = report.get('overall', {})
        print("📊 Overall Statistics:")
        print(f"   • Total fix attempts: {overall.get('total_fixes', 0)}")
        print(f"   • Successful fixes: {overall.get('total_successes', 0)}")
        print(f"   • Failed fixes: {overall.get('total_failures', 0)}")
        
        if overall.get('total_fixes', 0) > 0:
            success_pct = (overall.get('total_successes', 0) / overall['total_fixes']) * 100
            print(f"   • Success rate: {success_pct:.1f}%")
            print(f"   • Avg improvement: {overall.get('avg_improvement', 0):.1f}% human score")
        
        print()
        
        # Display top strategies
        top_strategies = report.get('top_strategies', [])
        
        if not top_strategies:
            print("⚠️  No fix strategies found in database")
            print("   Run some failed generations to collect fix data")
            return True
        
        print("🎯 Most Effective Strategies:")
        print()
        
        for i, strategy in enumerate(top_strategies, 1):
            status_icon = "✅" if strategy['success_rate'] > 0.7 else "⚠️" if strategy['success_rate'] > 0.4 else "❌"
            
            print(f"{i}. {strategy['failure_type'].upper()} → \"{strategy['name']}\"")
            print(f"   {status_icon} Success rate: {strategy['success_rate']*100:.1f}%")
            print(f"   📈 Avg improvement: {strategy['avg_improvement']:.1f}% human score")
            print(f"   🔢 Used: {strategy['times_used']} times")
            print()
        
        # Show filters applied
        if material or failure_type:
            print("=" * 80)
            print("📋 Filters Applied:")
            if material:
                print(f"   • Material: {material}")
            if failure_type:
                print(f"   • Failure type: {failure_type}")
            print()
        
        # Recommendations
        print("=" * 80)
        print("💡 Recommendations:")
        print()
        
        if overall.get('total_fixes', 0) < 10:
            print("⚠️  Limited data - run more generations to build learning database")
        else:
            # Find strategies with low success rates
            poor_strategies = [s for s in top_strategies if s['success_rate'] < 0.4]
            if poor_strategies:
                print("🔄 Consider alternative strategies for:")
                for strategy in poor_strategies[:3]:
                    print(f"   • {strategy['failure_type']}: {strategy['name']} ({strategy['success_rate']*100:.1f}% success)")
            else:
                print("✅ All strategies performing well!")
        
        print()
        print("To view more details, query the database tables:")
        print("   • fix_attempts: Every fix applied")
        print("   • fix_outcomes: Success/failure results")
        print("   • fix_statistics: Aggregated learning data")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Fix analysis error: {e}")
        import traceback
        traceback.print_exc()
        return False


# =================================================================================
# MAIN ENTRY POINT
# =================================================================================

