#!/usr/bin/env python3
"""
Regenerate All Subtitles Using Processing System

Uses the /processing system to generate AI-resistant subtitles
and saves them to Materials.yaml, then exports to frontmatter.

Flow:
1. Load materials from Materials.yaml
2. For each material:
   - Generate subtitle via processing.Orchestrator
   - Update Materials.yaml with result
3. Save Materials.yaml (with backup)
4. Run --deploy to export to frontmatter
"""

import sys
import yaml
from pathlib import Path
from typing import Dict
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from processing.orchestrator import Orchestrator
from shared.api.client_factory import create_api_client


def load_materials() -> Dict:
    """Load Materials.yaml"""
    materials_file = Path('data/materials/Materials.yaml')
    with open(materials_file, 'r') as f:
        return yaml.safe_load(f)


def save_materials(materials_data: Dict, backup: bool = True):
    """Save Materials.yaml with optional backup"""
    materials_file = Path('data/materials/Materials.yaml')
    
    if backup:
        backup_file = materials_file.parent / f'Materials_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml'
        with open(materials_file, 'r') as f:
            backup_content = f.read()
        with open(backup_file, 'w') as bf:
            bf.write(backup_content)
        print(f"💾 Backup created: {backup_file}")
    
    with open(materials_file, 'w') as f:
        yaml.dump(materials_data, f, default_flow_style=False, sort_keys=False, 
                  allow_unicode=True, width=1000)
    print(f"💾 Saved to {materials_file}")


def main():
    # Check for test mode
    test_mode = '--test' in sys.argv
    test_count = 10 if '--test' in sys.argv else None
    skip_deploy = '--skip-deploy' in sys.argv
    
    print("=" * 80)
    if test_mode:
        print(f"SUBTITLE REGENERATION - TEST MODE ({test_count} MATERIALS)")
    else:
        print("SUBTITLE REGENERATION - PROCESSING SYSTEM")
    print("=" * 80)
    print()
    
    # Load materials
    print("📂 Loading materials data...")
    materials_data = load_materials()
    all_materials = materials_data.get('materials', {})
    print(f"✅ Loaded {len(all_materials)} materials")
    
    # Test mode: select subset
    if test_mode:
        import random
        print(f"🧪 TEST MODE: Selecting {test_count} materials...")
        material_names = list(all_materials.keys())
        selected_names = random.sample(material_names, min(test_count, len(material_names)))
        materials = {name: all_materials[name] for name in selected_names}
        print(f"✅ Selected {len(materials)} materials")
    else:
        materials = all_materials
    
    print()
    
    # Initialize processing system
    print("🔑 Initializing API client...")
    api_client = create_api_client('grok')
    print("✅ API client ready")
    print()
    
    print("🎭 Initializing orchestrator...")
    orchestrator = Orchestrator(
        api_client=api_client,
        max_attempts=5,
        ai_threshold=0.3,  # Allow up to 30% AI score
        readability_min=60.0,  # Standard readability
        use_ml_detection=False  # Use pattern-based detection
    )
    print("✅ Orchestrator ready")
    print()
    
    # Statistics
    total_materials = len(materials)
    processed = 0
    successful = 0
    failed = 0
    
    print(f"🎯 Regenerating subtitles for {total_materials} materials...")
    print("-" * 80)
    
    # Process each material
    for material_name, material_data in sorted(materials.items()):
        processed += 1
        
        category = material_data.get('category', 'unknown')
        subcategory = material_data.get('subcategory', '')
        current_subtitle = material_data.get('subtitle', '')
        author_id = material_data.get('author', {}).get('id', 1)
        
        print(f"\n{processed}/{total_materials}. {material_name} ({category})")
        print(f"   Author: {author_id}")
        print(f"   Current: {current_subtitle[:70]}{'...' if len(current_subtitle) > 70 else ''}")
        
        # Generate new subtitle
        try:
            result = orchestrator.generate(
                topic=material_name,
                component_type='subtitle',
                author_id=author_id,
                length=15,
                domain='materials'
            )
            
            if result['success']:
                new_subtitle = result['text']
                word_count = len(new_subtitle.split())
                
                print(f"   ✅ New: {new_subtitle}")
                print(f"   📊 AI Score: {result['ai_score']:.3f}, Attempts: {result['attempts']}, Words: {word_count}")
                
                # Update material data
                material_data['subtitle'] = new_subtitle
                
                # Update metadata
                if 'subtitle_metadata' not in material_data:
                    material_data['subtitle_metadata'] = {}
                
                material_data['subtitle_metadata'].update({
                    'generated': datetime.now().isoformat(),
                    'word_count': word_count,
                    'character_count': len(new_subtitle),
                    'generation_method': 'processing_system',
                    'ai_score': round(result['ai_score'], 3),
                    'attempts': result['attempts'],
                    'author_id': author_id,
                    'detection_method': result['detection'].get('method', 'pattern_only')
                })
                
                successful += 1
            else:
                print(f"   ❌ Generation failed: {result['reason']}")
                failed += 1
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed += 1
    
    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total materials: {total_materials}")
    print(f"✅ Successfully regenerated: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"Success rate: {(successful/total_materials)*100:.1f}%")
    print()
    
    # Save results
    if test_mode:
        print("=" * 80)
        print("TEST MODE - SKIPPING SAVE")
        print("=" * 80)
        print("⚠️  Test mode - changes NOT saved to disk")
        print("   To save changes, run without --test flag")
        print()
    else:
        print("=" * 80)
        print("SAVING RESULTS")
        print("=" * 80)
        save_materials(materials_data, backup=True)
        print()
        
        if not skip_deploy and successful > 0:
            print("=" * 80)
            print("DEPLOYING TO FRONTMATTER")
            print("=" * 80)
            print("Running: python3 run.py --deploy")
            print()
            
            import subprocess
            result = subprocess.run(
                ['python3', 'run.py', '--deploy'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Deployment successful!")
                # Show last few lines of output
                lines = result.stdout.strip().split('\n')
                for line in lines[-10:]:
                    print(line)
            else:
                print("❌ Deployment failed!")
                print(result.stderr)
        elif skip_deploy:
            print("⏭️  Skipping deployment (--skip-deploy flag)")
            print("   Run manually: python3 run.py --deploy")
        print()
    
    print("✨ Subtitle regeneration complete!")
    print()


if __name__ == '__main__':
    main()
