#!/usr/bin/env python3
"""
Master Orchestration Script
Runs all phases of relationship population in sequence.
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent.parent

def run_phase(phase_num, script_path, description):
    """Run a phase script and check exit code"""
    print()
    print("=" * 80)
    print(f"STARTING PHASE {phase_num}: {description}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    try:
        result = subprocess.run(
            ['python3', str(script_path)],
            cwd=str(project_root),
            check=True,
            capture_output=False
        )
        
        print()
        print(f"✅ Phase {phase_num} completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print()
        print(f"❌ Phase {phase_num} failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print()
        print(f"❌ Phase {phase_num} error: {e}")
        return False

def main():
    start_time = datetime.now()
    
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  RELATIONSHIP POPULATION & LINK VALIDATION - FULL PIPELINE".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("║" + f"  Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}".ljust(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    phases = [
        (1, project_root / "scripts/analysis/audit_domain_associations.py", 
         "Association Auditor"),
        (2, project_root / "scripts/population/auto_populate_relationships.py", 
         "Auto-Populate Relationships"),
        (3, project_root / "scripts/population/enable_enrichers.py", 
         "Enable Enrichers"),
        (4, project_root / "scripts/validation/comprehensive_link_validator.py", 
         "Comprehensive Link Validator"),
    ]
    
    results = []
    
    for phase_num, script_path, description in phases:
        success = run_phase(phase_num, script_path, description)
        results.append((phase_num, description, success))
        
        if not success:
            print()
            print("=" * 80)
            print(f"⚠️  PIPELINE STOPPED AT PHASE {phase_num}")
            print("=" * 80)
            break
    
    # Phase 5: Export (only if validation passed)
    if all(r[2] for r in results):
        print()
        print("=" * 80)
        print("PHASE 5: FULL EXPORT & DEPLOYMENT")
        print("=" * 80)
        print()
        
        print("🚀 Exporting all domains with new relationships...")
        try:
            subprocess.run(
                ['python3', 'run.py', '--export-all'],
                cwd=str(project_root),
                check=True,
                capture_output=False
            )
            results.append((5, "Full Export & Deployment", True))
            print()
            print("✅ Phase 5 completed successfully")
        except subprocess.CalledProcessError as e:
            results.append((5, "Full Export & Deployment", False))
            print()
            print(f"❌ Phase 5 failed with exit code {e.returncode}")
    
    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print()
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  PIPELINE SUMMARY".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    print(f"⏱️  Total Duration: {duration}")
    print(f"🏁 Completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("📊 PHASE RESULTS:")
    print("-" * 80)
    for phase_num, description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   Phase {phase_num}: {description.ljust(40)} {status}")
    print()
    
    all_passed = all(r[2] for r in results)
    
    if all_passed:
        print("=" * 80)
        print("🎉 ALL PHASES COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print()
        print("✅ Relationship population complete")
        print("✅ Link validation passed")
        print("✅ Frontmatter deployed to production")
        print()
        print("📁 Next Steps:")
        print("   1. Verify sample frontmatter files have relationships")
        print("   2. Test navigation on website")
        print("   3. Monitor for any link errors")
        print()
        return 0
    else:
        print("=" * 80)
        print("⚠️  PIPELINE INCOMPLETE - REVIEW ERRORS ABOVE")
        print("=" * 80)
        print()
        failed_phases = [f"Phase {r[0]}" for r in results if not r[2]]
        print(f"❌ Failed: {', '.join(failed_phases)}")
        print()
        return 1

if __name__ == '__main__':
    sys.exit(main())
