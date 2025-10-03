#!/usr/bin/env python3
"""
Batch regenerate all frontmatter files for all materials.

This script regenerates frontmatter for all 122 materials with:
- Progress tracking
- Error handling
- YAML-first optimization where available
- Detailed logging
- Per-material timeout protection
"""

import sys
import os
import subprocess
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.materials import load_materials

def regenerate_all_frontmatter():
    """Regenerate frontmatter for all materials."""
    
    print("=" * 80)
    print("BATCH FRONTMATTER REGENERATION")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load materials
    print("Loading materials database...")
    materials_data = load_materials()
    materials = materials_data['materials']
    material_names = sorted(materials.keys())
    
    total = len(material_names)
    print(f"✅ Loaded {total} materials")
    print()
    
    # Track results
    successful = []
    failed = []
    skipped = []
    
    # Log file
    log_file = Path("full_regeneration.log")
    with open(log_file, 'w') as log:
        log.write(f"Frontmatter Regeneration Log - {datetime.now()}\n")
        log.write(f"{'='*80}\n\n")
        
        print(f"{'='*80}")
        print(f"REGENERATION PROGRESS")
        print(f"{'='*80}\n")
        
        start_time = time.time()
        
        for idx, material_name in enumerate(material_names, 1):
            # Progress indicator
            progress = f"[{idx}/{total}]"
            percent = (idx / total) * 100
            
            print(f"{progress} ({percent:.1f}%) Processing: {material_name:40s}", end=" ", flush=True)
            log.write(f"\n{progress} {material_name}\n")
            log.write("-" * 80 + "\n")
            
            try:
                # Run generation with timeout
                cmd = [
                    "python3", "run.py",
                    "--material", material_name,
                    "--components", "frontmatter"
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=180,  # 3 minute timeout per material
                    cwd=Path(__file__).parent.parent
                )
                
                if result.returncode == 0:
                    print("✅")
                    successful.append(material_name)
                    log.write(f"✅ SUCCESS\n")
                else:
                    print("❌")
                    failed.append((material_name, "Non-zero exit code"))
                    log.write(f"❌ FAILED: {result.returncode}\n")
                    log.write(f"STDERR: {result.stderr[:500]}\n")
                    
            except subprocess.TimeoutExpired:
                print("⏱️  TIMEOUT")
                failed.append((material_name, "Timeout (>180s)"))
                log.write(f"⏱️  TIMEOUT after 180 seconds\n")
                
            except Exception as e:
                print(f"❌ ERROR")
                failed.append((material_name, str(e)[:100]))
                log.write(f"❌ ERROR: {str(e)}\n")
            
            # Brief pause between materials to avoid overwhelming the API
            if idx < total:
                time.sleep(0.5)
        
        elapsed = time.time() - start_time
        
        # Summary
        print()
        print(f"{'='*80}")
        print(f"REGENERATION COMPLETE")
        print(f"{'='*80}")
        print(f"Total materials: {total}")
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        print(f"⏭️  Skipped: {len(skipped)}")
        print(f"⏱️  Total time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        print(f"⏱️  Average: {elapsed/total:.1f} seconds per material")
        print()
        
        log.write(f"\n{'='*80}\n")
        log.write(f"SUMMARY\n")
        log.write(f"{'='*80}\n")
        log.write(f"Total: {total}\n")
        log.write(f"Successful: {len(successful)}\n")
        log.write(f"Failed: {len(failed)}\n")
        log.write(f"Skipped: {len(skipped)}\n")
        log.write(f"Time: {elapsed:.1f}s ({elapsed/60:.1f}m)\n")
        log.write(f"Average: {elapsed/total:.1f}s per material\n\n")
        
        if failed:
            print(f"{'='*80}")
            print(f"FAILED MATERIALS ({len(failed)})")
            print(f"{'='*80}")
            for mat, reason in failed[:10]:
                print(f"  ❌ {mat}: {reason}")
            if len(failed) > 10:
                print(f"  ... and {len(failed) - 10} more (see log)")
            print()
            
            log.write(f"\n{'='*80}\n")
            log.write(f"FAILED MATERIALS\n")
            log.write(f"{'='*80}\n")
            for mat, reason in failed:
                log.write(f"  ❌ {mat}: {reason}\n")
        
        print(f"📝 Full log saved to: {log_file}")
        print()
        
        # Return success/failure count
        return len(successful), len(failed)

if __name__ == "__main__":
    try:
        success_count, fail_count = regenerate_all_frontmatter()
        
        # Exit with appropriate code
        if fail_count == 0:
            print("🎉 All materials regenerated successfully!")
            sys.exit(0)
        elif success_count > 0:
            print(f"⚠️  Completed with {fail_count} failures")
            sys.exit(1)
        else:
            print("❌ Regeneration failed")
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Regeneration interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        sys.exit(3)
