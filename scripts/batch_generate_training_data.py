#!/usr/bin/env python3
"""
Batch Generate Training Data
=============================

Generate multiple samples across materials and components to build
clean training dataset with dynamic penalties.
"""

import subprocess
import sys
from typing import List

# Top materials to test (based on common usage)
DEFAULT_MATERIALS = [
    "Aluminum", "Steel", "Titanium", "Copper", "Brass",
    "Bronze", "Iron", "Zinc", "Nickel", "Stainless Steel"
]

DEFAULT_COMPONENTS = ["caption"]


def generate_samples(
    materials: List[str],
    components: List[str],
    samples_per: int = 5,
    skip_integrity: bool = True
):
    """Generate training samples"""
    
    total = len(materials) * len(components) * samples_per
    print(f"🚀 Generating {total} samples...")
    print(f"   Materials: {len(materials)}")
    print(f"   Components: {len(components)}")
    print(f"   Samples per: {samples_per}")
    print()
    
    completed = 0
    failed = 0
    
    for material in materials:
        for component in components:
            print(f"\n{'='*60}")
            print(f"Material: {material} | Component: {component}")
            print('='*60)
            
            for attempt in range(1, samples_per + 1):
                print(f"\n  Attempt {attempt}/{samples_per}...")
                
                # Build command
                cmd = ["python3", "run.py", f"--{component}", material]
                if skip_integrity:
                    cmd.append("--skip-integrity-check")
                
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minute timeout
                    )
                    
                    if result.returncode == 0:
                        # Check for success in output
                        if "Success" in result.stdout or "✅" in result.stdout:
                            print("    ✅ Success")
                            completed += 1
                        else:
                            print("    ⚠️  Generated but check results")
                            completed += 1
                    else:
                        print(f"    ❌ Failed (exit code: {result.returncode})")
                        failed += 1
                        if result.stderr:
                            print(f"    Error: {result.stderr[:200]}")
                
                except subprocess.TimeoutExpired:
                    print("    ❌ Timeout (>5 minutes)")
                    failed += 1
                except Exception as e:
                    print(f"    ❌ Error: {e}")
                    failed += 1
    
    print("\n" + "="*60)
    print("BATCH GENERATION COMPLETE")
    print("="*60)
    print(f"  Completed: {completed}/{total}")
    print(f"  Failed: {failed}/{total}")
    print(f"  Success Rate: {completed/total*100:.1f}%")
    print()
    print("💡 Next steps:")
    print("   1. Run: python3 scripts/e2e_system_evaluation.py")
    print("   2. Check: data/winston_feedback.db for new data")
    print("   3. Verify: Parameter logging at 100% coverage")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate training data')
    parser.add_argument('--materials', default=None,
                       help='Comma-separated material names (default: top 10)')
    parser.add_argument('--components', default='caption',
                       help='Comma-separated component types (default: caption)')
    parser.add_argument('--samples-per', type=int, default=3,
                       help='Number of samples per material/component (default: 3)')
    parser.add_argument('--no-skip-integrity', action='store_true',
                       help='Run integrity checks (slower but validates system)')
    
    args = parser.parse_args()
    
    # Parse materials
    if args.materials:
        if args.materials.lower() == 'all':
            # Would need to load from Materials.yaml
            print("❌ --materials all not yet implemented")
            print("   Use comma-separated list instead")
            sys.exit(1)
        materials = [m.strip() for m in args.materials.split(',')]
    else:
        materials = DEFAULT_MATERIALS
    
    # Parse components
    components = [c.strip() for c in args.components.split(',')]
    
    # Validate components
    valid_components = ['caption', 'faq', 'description']
    for c in components:
        if c not in valid_components:
            print(f"❌ Invalid component: {c}")
            print(f"   Valid: {', '.join(valid_components)}")
            sys.exit(1)
    
    generate_samples(
        materials,
        components,
        args.samples_per,
        not args.no_skip_integrity
    )
