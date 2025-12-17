#!/usr/bin/env python3
"""
Complete Deployment Pipeline
=============================

Automated end-to-end deployment:
1. Export all domains to frontmatter
2. Re-extract domain associations  
3. Run test suite
4. Report results

Usage:
    python3 scripts/operations/deploy_all.py
    python3 scripts/operations/deploy_all.py --test-only
    python3 scripts/operations/deploy_all.py --skip-tests
"""

import sys
import subprocess
from pathlib import Path
import time
import argparse


def run_command(cmd: str, description: str) -> tuple[bool, str]:
    """
    Run a command and return success status + output
    
    Returns:
        (success: bool, output: str)
    """
    print(f"\n{'='*80}")
    print(f"📋 {description}")
    print(f"{'='*80}")
    print(f"💻 Command: {cmd}\n")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent
        )
        
        elapsed = time.time() - start_time
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        success = result.returncode == 0
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"\n{status} ({elapsed:.1f}s)")
        
        return success, result.stdout + result.stderr
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ ERROR: {e} ({elapsed:.1f}s)", file=sys.stderr)
        return False, str(e)


def export_all_domains():
    """Export all domains to frontmatter"""
    print("\n" + "="*80)
    print("🚀 STEP 1: EXPORTING ALL DOMAINS TO FRONTMATTER")
    print("="*80)
    
    domains = [
        ('materials', 'export.core.trivial_exporter', 'TrivialFrontmatterExporter'),
        ('settings', 'export.settings.trivial_exporter', 'TrivialSettingsExporter'),
        ('contaminants', 'export.contaminants.trivial_exporter', 'TrivialContaminantsExporter'),
        ('compounds', 'export.compounds.trivial_exporter', 'CompoundExporter'),
    ]
    
    all_success = True
    
    for domain, module, class_name in domains:
        cmd = f'python3 -c "from {module} import {class_name}; e = {class_name}(); e.export_all(); print(\\"\\\\n✅ {domain.title()} exported successfully\\")"'
        success, _ = run_command(cmd, f"Export {domain}")
        
        if not success:
            print(f"⚠️  WARNING: {domain} export failed")
            all_success = False
    
    return all_success


def extract_associations():
    """Re-extract domain associations from frontmatter"""
    print("\n" + "="*80)
    print("🔗 STEP 2: EXTRACTING DOMAIN ASSOCIATIONS")
    print("="*80)
    
    cmd = "python3 scripts/data/extract_existing_linkages.py"
    success, output = run_command(cmd, "Extract associations from frontmatter")
    
    if success:
        # Parse statistics from output
        for line in output.split('\n'):
            if 'Material ↔ Contaminant:' in line or 'Contaminant ↔ Compound:' in line or 'Total:' in line:
                print(f"  📊 {line.strip()}")
    
    return success


def copy_to_production():
    """Copy frontmatter files to production z-beam directory"""
    print("\n" + "="*80)
    print("📦 STEP 3: COPYING FRONTMATTER TO PRODUCTION")
    print("="*80)
    
    # Determine paths
    generator_path = Path(__file__).resolve().parents[2]
    production_path = generator_path.parent / "z-beam" / "frontmatter"
    
    # Check if production directory exists
    if not production_path.exists():
        print(f"⚠️  Production directory not found: {production_path}")
        print("   Skipping production copy (development environment)")
        return True
    
    cmd = f"cp -r {generator_path}/frontmatter/* {production_path}/"
    success, output = run_command(cmd, "Copy frontmatter to production")
    
    if success:
        print(f"  ✅ Copied frontmatter to: {production_path}")
        print(f"  📂 Domains: materials, contaminants, compounds, settings")
    
    return success


def run_tests():
    """Run centralized architecture test suite"""
    print("\n" + "="*80)
    print("🧪 STEP 4: RUNNING TEST SUITE")
    print("="*80)
    
    cmd = "python3 -m pytest tests/test_centralized_architecture.py -v --tb=line"
    success, output = run_command(cmd, "Test centralized architecture")
    
    # Parse test results
    if success:
        for line in output.split('\n'):
            if 'passed' in line.lower() or 'failed' in line.lower():
                print(f"  📊 {line.strip()}")
    
    return success


def main():
    parser = argparse.ArgumentParser(description='Deploy all frontmatter and validate')
    parser.add_argument('--test-only', action='store_true', help='Only run tests, skip export')
    parser.add_argument('--skip-tests', action='store_true', help='Skip test suite')
    parser.add_argument('--export-only', action='store_true', help='Only export, skip extraction and tests')
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("🎯 AUTOMATED DEPLOYMENT PIPELINE")
    print("="*80)
    print("\nThis script will:")
    if not args.test_only:
        print("  1. Export all domains to frontmatter (materials, contaminants, compounds)")
        print("  2. Re-extract domain associations from frontmatter")
        print("  3. Copy frontmatter to production (z-beam directory)")
    if not args.skip_tests:
        print("  4. Run comprehensive test suite (17 tests)")
    print("  5. Report final status\n")
    
    start_time = time.time()
    steps_passed = 0
    steps_total = 0
    
    # Step 1 & 2: Export and extract
    if not args.test_only:
        steps_total += 3  # Export, Extract, Copy to production
        
        if export_all_domains():
            steps_passed += 1
        
        if not args.export_only:
            if extract_associations():
                steps_passed += 1
            
            if copy_to_production():
                steps_passed += 1
    
    # Step 4: Tests
    if not args.skip_tests and not args.export_only:
        steps_total += 1
        if run_tests():
            steps_passed += 1
    
    # Final report
    elapsed = time.time() - start_time
    
    print("\n" + "="*80)
    print("📊 FINAL DEPLOYMENT REPORT")
    print("="*80)
    print(f"\n⏱️  Total time: {elapsed:.1f}s")
    print(f"✅ Steps passed: {steps_passed}/{steps_total}")
    
    if steps_passed == steps_total:
        print("\n🎉 DEPLOYMENT COMPLETE - ALL STEPS PASSED!")
        print("\n✅ System is ready for production")
        return 0
    else:
        print(f"\n⚠️  DEPLOYMENT INCOMPLETE - {steps_total - steps_passed} STEP(S) FAILED")
        print("\n❌ Review errors above and fix before deploying")
        return 1


if __name__ == '__main__':
    sys.exit(main())
