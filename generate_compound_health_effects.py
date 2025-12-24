#!/usr/bin/env python3
"""
Batch generate health_effects for all compounds.

Generates descriptive health effects text for compounds domain.
Uses QualityEvaluatedGenerator pipeline with health_effects.txt prompt.
"""

import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from shared.api.client_factory import create_api_client
from domains.compounds.coordinator import CompoundCoordinator

def main():
    print("="*80)
    print("🏥 COMPOUND HEALTH EFFECTS BATCH GENERATION")
    print("="*80)
    
    # Load compounds data
    with open('data/compounds/Compounds.yaml', 'r') as f:
        data = yaml.safe_load(f)
    
    compounds = list(data['compounds'].keys())
    print(f"\n📊 Found {len(compounds)} compounds")
    
    # Create API client
    print("\n1️⃣ Creating API client...")
    try:
        client = create_api_client('grok')
        print("✅ API client created")
    except Exception as e:
        print(f"❌ Failed to create API client: {e}")
        return 1
    
    # Initialize coordinator
    print("\n2️⃣ Initializing compounds coordinator...")
    try:
        coordinator = CompoundCoordinator(api_client=client)
        print(f"✅ Coordinator initialized")
        print(f"   - Domain: {coordinator.domain_name}")
        print(f"   - Has generator: {coordinator.generator is not None}")
    except Exception as e:
        print(f"❌ Failed to initialize coordinator: {e}")
        return 1
    
    # Generate health_effects for each compound
    print(f"\n3️⃣ Generating health_effects for {len(compounds)} compounds...")
    print("="*80)
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for i, compound_id in enumerate(compounds, 1):
        compound = data['compounds'][compound_id]
        compound_name = compound.get('name', compound_id)
        
        print(f"\n[{i}/{len(compounds)}] {compound_name} ({compound_id})")
        print("-"*80)
        
        try:
            result = coordinator.generate_compound_content(
                compound_id=compound_id,
                component_type='health_effects',
                force_regenerate=False  # Skip if already exists
            )
            
            if result.get('skipped'):
                print(f"⏭️  Skipped: {result.get('reason', 'unknown')}")
                skipped_count += 1
            elif result.get('success'):
                content_len = len(result.get('content', ''))
                attempts = result.get('attempts', 1)
                print(f"✅ Generated successfully")
                print(f"   - Length: {content_len} chars")
                print(f"   - Attempts: {attempts}")
                success_count += 1
            else:
                print(f"❌ Generation failed: {result.get('error', 'unknown')}")
                error_count += 1
                
        except Exception as e:
            print(f"❌ Error: {e}")
            error_count += 1
    
    # Summary
    print("\n" + "="*80)
    print("📊 BATCH GENERATION SUMMARY")
    print("="*80)
    print(f"✅ Successful: {success_count}/{len(compounds)}")
    print(f"⏭️  Skipped: {skipped_count}/{len(compounds)}")
    print(f"❌ Errors: {error_count}/{len(compounds)}")
    
    if success_count > 0:
        print("\n🎉 Health effects generated successfully!")
        print("Next step: Run export to update frontmatter:")
        print("   python3 run.py --export --domain compounds")
    
    return 0 if error_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
