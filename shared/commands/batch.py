#!/usr/bin/env python3
"""
Batch Generation Command Handlers

Handles batch content generation commands to meet Winston minimums efficiently.
"""

import sys
from pathlib import Path


def handle_batch_subtitle_generation(materials_input: str, skip_integrity_check: bool = False):
    """
    Generate subtitles for multiple materials in batches.
    
    Args:
        materials_input: Comma-separated material names or "--all"
        skip_integrity_check: Skip integrity validation
        
    Returns:
        True if successful, False otherwise
    """
    print("="*80)
    print("🔄 BATCH SUBTITLE GENERATION")
    print("="*80)
    print()
    
    # Run pre-generation integrity check
    if not skip_integrity_check:
        from shared.commands.integrity_helper import run_pre_generation_check
        if not run_pre_generation_check(skip_check=False, quick=True):
            return False
    
    # Parse materials list
    materials = _parse_materials_input(materials_input)
    
    if not materials:
        print("❌ No materials specified")
        return False
    
    print(f"📋 Materials to process: {len(materials)}")
    print(f"   {', '.join(materials[:5])}{'...' if len(materials) > 5 else ''}")
    print()
    
    try:
        # Initialize generator and batch generator
        from generation.core.generator import DynamicGenerator
        from generation.core.batch_generator import BatchGenerator
        from shared.api.client_factory import create_api_client
        
        print("🔧 Initializing generators...")
        api_client = create_api_client('deepseek')
        generator = DynamicGenerator(api_client=api_client)
        batch_gen = BatchGenerator(generator)
        print("✅ Generators ready")
        print()
        
        # Check if component is batch-eligible
        if not batch_gen.is_batch_eligible('subtitle'):
            print("⚠️  Subtitles not batch-eligible - using individual generation")
            return _generate_individually(materials, 'subtitle', skip_integrity_check)
        
        # Calculate optimal batch size
        batch_size = batch_gen.calculate_batch_size('subtitle', len(materials))
        print(f"📊 Optimal batch size: {batch_size} materials per batch")
        print()
        
        # Split materials into batches
        batches = [materials[i:i+batch_size] for i in range(0, len(materials), batch_size)]
        print(f"📦 Split into {len(batches)} batches")
        print()
        
        # Process batches
        total_success = 0
        total_failed = 0
        total_cost_savings = 0.0
        
        for batch_num, batch in enumerate(batches, 1):
            print(f"\n{'='*80}")
            print(f"📦 BATCH {batch_num}/{len(batches)}")
            print(f"{'='*80}")
            print(f"Materials: {', '.join(batch)}")
            print()
            
            result = batch_gen.batch_generate_subtitles(
                materials=batch,
                skip_integrity_check=skip_integrity_check
            )
            
            if result['success']:
                total_success += result.get('saved_count', 0)
                total_cost_savings += result.get('cost_savings', 0.0)
                print(f"✅ Batch {batch_num} complete: {result.get('saved_count', 0)}/{len(batch)} saved")
            else:
                total_failed += len(batch)
                print(f"❌ Batch {batch_num} failed: {result.get('error', 'Unknown error')}")
            
            print()
        
        # Final report
        print("\n" + "="*80)
        print("📊 BATCH GENERATION COMPLETE")
        print("="*80)
        print(f"✅ Success: {total_success}/{len(materials)} materials")
        print(f"❌ Failed:  {total_failed}/{len(materials)} materials")
        print(f"💰 Cost savings: ${total_cost_savings:.2f}")
        print(f"📍 Location: data/materials/Materials.yaml")
        print("="*80)
        print()
        
        return total_success == len(materials)
        
    except Exception as e:
        print(f"❌ Batch generation error: {e}")
        import traceback
        traceback.print_exc()
        return False


def handle_batch_caption_generation(materials_input: str, skip_integrity_check: bool = False):
    """
    Generate captions for multiple materials in batches.
    
    Note: Captions already meet Winston 300-char minimum individually,
    so batch generation may not provide cost savings. This command exists
    for consistency and potential future optimization.
    
    Args:
        materials_input: Comma-separated material names or "--all"
        skip_integrity_check: Skip integrity validation
        
    Returns:
        True if successful, False otherwise
    """
    print("="*80)
    print("🔄 BATCH CAPTION GENERATION")
    print("="*80)
    print()
    print("ℹ️  Note: Captions already meet Winston minimum individually.")
    print("   Batch generation available for consistency but may not save costs.")
    print()
    
    # Parse materials list
    materials = _parse_materials_input(materials_input)
    
    if not materials:
        print("❌ No materials specified")
        return False
    
    # Use individual generation (captions don't benefit from batching)
    return _generate_individually(materials, 'caption', skip_integrity_check)


def _parse_materials_input(materials_input: str) -> list:
    """
    Parse materials input string into list of material names.
    
    Args:
        materials_input: Comma-separated names or "--all"
        
    Returns:
        List of material names
    """
    if materials_input == "--all" or materials_input.lower() == "all":
        # Load all materials from Materials.yaml
        from data.materials.materials import load_materials
        materials_data = load_materials()
        return list(materials_data['materials'].keys())
    else:
        # Parse comma-separated list
        return [m.strip() for m in materials_input.split(',') if m.strip()]


def _generate_individually(materials: list, component_type: str, skip_integrity_check: bool) -> bool:
    """
    Generate components individually (fallback when batching not beneficial).
    
    Args:
        materials: List of material names
        component_type: Type of component (caption, subtitle, etc.)
        skip_integrity_check: Skip integrity validation
        
    Returns:
        True if all successful, False otherwise
    """
    print(f"🔄 Generating {component_type}s individually...")
    print(f"📋 Materials: {len(materials)}")
    print()
    
    # Import generation handlers
    if component_type == 'caption':
        from shared.commands.generation import handle_caption_generation as handler
    elif component_type == 'subtitle':
        from shared.commands.generation import handle_subtitle_generation as handler
    elif component_type == 'faq':
        from shared.commands.generation import handle_faq_generation as handler
    else:
        print(f"❌ Unsupported component type: {component_type}")
        return False
    
    # Process each material
    success_count = 0
    failed_count = 0
    
    for i, material in enumerate(materials, 1):
        print(f"\n{'='*80}")
        print(f"📝 {i}/{len(materials)}: {material}")
        print(f"{'='*80}")
        
        try:
            result = handler(material, skip_integrity_check=skip_integrity_check)
            if result:
                success_count += 1
                print(f"✅ Success: {material}")
            else:
                failed_count += 1
                print(f"❌ Failed: {material}")
        except Exception as e:
            failed_count += 1
            print(f"❌ Error processing {material}: {e}")
        
        print()
    
    # Final report
    print("\n" + "="*80)
    print(f"📊 INDIVIDUAL GENERATION COMPLETE")
    print("="*80)
    print(f"✅ Success: {success_count}/{len(materials)} materials")
    print(f"❌ Failed:  {failed_count}/{len(materials)} materials")
    print(f"📍 Location: data/materials/Materials.yaml")
    print("="*80)
    print()
    
    return success_count == len(materials)
