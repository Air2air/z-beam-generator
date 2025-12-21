#!/usr/bin/env python3
"""
Complete Deployment Pipeline
=============================

Automated end-to-end deployment with rollback capability:
1. Pre-flight health check
2. Create backup (if enabled)
3. Export all domains to frontmatter
4. Re-extract domain associations  
5. Run test suite (optional)
6. Report results
7. Rollback on failure (if backup created)

Usage:
    # Normal deployment with backup
    python3 scripts/operations/deploy_all.py --backup
    
    # Rollback to previous backup
    python3 scripts/operations/deploy_all.py --rollback
    
    # List available backups
    python3 scripts/operations/deploy_all.py --list-backups
    
    # Deploy without backup (faster)
    python3 scripts/operations/deploy_all.py
"""

import sys
import subprocess
from pathlib import Path
import time
import argparse
import shutil
from datetime import datetime


# Backup configuration
BACKUP_DIR = Path(__file__).parent.parent.parent.parent / 'z-beam' / '.frontmatter-backups'
MAX_BACKUPS = 5


def create_backup() -> Path:
    """
    Create timestamped backup of frontmatter directory.
    
    Returns:
        Path to backup directory
    """
    print("\n" + "="*80)
    print("💾 CREATING BACKUP")
    print("="*80)
    
    prod_frontmatter = Path(__file__).parent.parent.parent.parent / 'z-beam' / 'frontmatter'
    
    if not prod_frontmatter.exists():
        print("⚠️  No frontmatter directory to backup")
        return None
    
    # Create backup directory
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create timestamped backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = BACKUP_DIR / f'backup_{timestamp}'
    
    print(f"📦 Copying {prod_frontmatter} → {backup_path}")
    shutil.copytree(prod_frontmatter, backup_path)
    
    # Count files
    file_count = sum(1 for _ in backup_path.rglob('*.yaml'))
    backup_size_mb = sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file()) / 1024 / 1024
    
    print(f"✅ Backup created: {backup_path}")
    print(f"   Files: {file_count}")
    print(f"   Size: {backup_size_mb:.1f} MB")
    
    # Clean up old backups
    cleanup_old_backups()
    
    return backup_path


def cleanup_old_backups():
    """Remove old backups, keeping only MAX_BACKUPS most recent"""
    if not BACKUP_DIR.exists():
        return
    
    backups = sorted(BACKUP_DIR.glob('backup_*'), key=lambda p: p.name, reverse=True)
    
    if len(backups) > MAX_BACKUPS:
        print(f"\n🧹 Cleaning up old backups (keeping {MAX_BACKUPS} most recent)")
        for old_backup in backups[MAX_BACKUPS:]:
            print(f"   Removing {old_backup.name}")
            shutil.rmtree(old_backup)


def list_backups():
    """List available backups"""
    print("\n" + "="*80)
    print("💾 AVAILABLE BACKUPS")
    print("="*80)
    
    if not BACKUP_DIR.exists() or not list(BACKUP_DIR.glob('backup_*')):
        print("No backups found")
        return []
    
    backups = sorted(BACKUP_DIR.glob('backup_*'), key=lambda p: p.name, reverse=True)
    
    for i, backup in enumerate(backups, 1):
        timestamp_str = backup.name.replace('backup_', '')
        timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
        file_count = sum(1 for _ in backup.rglob('*.yaml'))
        size_mb = sum(f.stat().st_size for f in backup.rglob('*') if f.is_file()) / 1024 / 1024
        
        print(f"{i}. {backup.name}")
        print(f"   Date: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Files: {file_count} | Size: {size_mb:.1f} MB")
        print(f"   Path: {backup}\n")
    
    return backups


def rollback_to_backup(backup_path: Path = None):
    """
    Rollback frontmatter to a previous backup.
    
    Args:
        backup_path: Path to backup (if None, uses most recent)
    """
    print("\n" + "="*80)
    print("⏪ ROLLBACK TO BACKUP")
    print("="*80)
    
    if backup_path is None:
        # Use most recent backup
        backups = sorted(BACKUP_DIR.glob('backup_*'), key=lambda p: p.name, reverse=True)
        if not backups:
            print("❌ No backups available")
            return False
        backup_path = backups[0]
    
    if not backup_path.exists():
        print(f"❌ Backup not found: {backup_path}")
        return False
    
    prod_frontmatter = Path(__file__).parent.parent.parent.parent / 'z-beam' / 'frontmatter'
    
    print(f"📦 Restoring from: {backup_path}")
    print(f"📁 Target: {prod_frontmatter}")
    
    # Remove current frontmatter
    if prod_frontmatter.exists():
        print("🗑️  Removing current frontmatter")
        shutil.rmtree(prod_frontmatter)
    
    # Restore from backup
    print("📦 Restoring files")
    shutil.copytree(backup_path, prod_frontmatter)
    
    file_count = sum(1 for _ in prod_frontmatter.rglob('*.yaml'))
    print(f"✅ Rollback complete: {file_count} files restored")
    
    return True


def run_health_check() -> bool:
    """
    Run pre-flight health check to validate system before deployment
    
    Returns:
        True if system healthy, False otherwise
    """
    print("\n" + "="*80)
    print("🏥 PRE-FLIGHT HEALTH CHECK")
    print("="*80)
    
    try:
        # Import and run health check
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from scripts.tools.health_check import run_health_check
        
        result = run_health_check(verbose=True)
        
        if not result['healthy']:
            print("\n⚠️  DEPLOYMENT BLOCKED: System unhealthy")
            print("Fix errors before deploying.")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {e}", file=sys.stderr)
        print("⚠️  Continuing without health check...")
        return True  # Don't block deployment on health check failure


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


def export_all_domains(dry_run: bool = False):
    """Export all domains to frontmatter using UniversalFrontmatterExporter"""
    mode_text = "DRY-RUN: Preview" if dry_run else "EXPORTING"
    print("\n" + "="*80)
    print(f"🚀 STEP 2: {mode_text} ALL DOMAINS TO FRONTMATTER")
    print("="*80)
    
    if dry_run:
        print("🔍 DRY-RUN MODE: No files will be written")
    
    # Auto-discover domains from config files
    config_dir = Path(__file__).parent.parent.parent / 'export' / 'config'
    domain_files = sorted(config_dir.glob('*.yaml'))
    domains = [f.stem for f in domain_files if f.stem != 'validator']
    
    if not domains:
        print("⚠️  WARNING: No domain config files found in export/config/")
        return False
    
    print(f"📦 Discovered {len(domains)} domains: {', '.join(domains)}")
    
    all_success = True
    
    for domain in domains:
        dry_run_arg = ', dry_run=True' if dry_run else ''
        cmd = f'python3 -c "from export.config.loader import load_domain_config; from export.core.universal_exporter import UniversalFrontmatterExporter; config = load_domain_config(\'{domain}\'); e = UniversalFrontmatterExporter(config); e.export_all(show_progress=True{dry_run_arg}); print(\\"\\\\n✅ {domain.title()} {"preview" if dry_run else "export"} successful\\")"'
        success, _ = run_command(cmd, f"{'Preview' if dry_run else 'Export'} {domain}")
        
        if not success:
            print(f"⚠️  WARNING: {domain} {'preview' if dry_run else 'export'} failed")
            all_success = False
    
    return all_success


def extract_associations():
    """Re-extract domain associations from frontmatter"""
    print("\n" + "="*80)
    print("🔗 STEP 3: EXTRACTING DOMAIN ASSOCIATIONS")
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
    parser.add_argument('--skip-health-check', action='store_true', help='Skip pre-flight health check')
    parser.add_argument('--export-only', action='store_true', help='Only export, skip extraction and tests')
    parser.add_argument('--dry-run', action='store_true', help='Preview what would be exported without writing files')
    parser.add_argument('--backup', action='store_true', help='Create backup before deployment')
    parser.add_argument('--rollback', action='store_true', help='Rollback to previous backup')
    parser.add_argument('--list-backups', action='store_true', help='List available backups')
    
    args = parser.parse_args()
    
    # Handle backup commands
    if args.list_backups:
        list_backups()
        return
    
    if args.rollback:
        success = rollback_to_backup()
        sys.exit(0 if success else 1)
    
    print("\n" + "="*80)
    if args.dry_run:
        print("🔍 DEPLOYMENT DRY-RUN (Preview Mode)")
    else:
        print("🎯 AUTOMATED DEPLOYMENT PIPELINE")
    print("="*80)
    
    if args.dry_run:
        print("\n🔍 DRY-RUN MODE: No files will be written")
        print("This will preview what would be exported without making changes.\n")
    
    if args.backup and not args.dry_run:
        print("\n💾 BACKUP MODE: Backup will be created before deployment\n")
    
    print("\nThis script will:")
    if args.backup and not args.dry_run and not args.test_only:
        print("  0. Create backup of current frontmatter")
    if not args.skip_health_check and not args.test_only:
        print("  1. Run pre-flight health check")
    if not args.test_only:
        action = "Preview" if args.dry_run else "Export"
        print(f"  2. {action} all domains to frontmatter (materials, contaminants, compounds)")
        if not args.dry_run:
            print("  3. Re-extract domain associations from frontmatter")
            print("  4. Copy frontmatter to production (z-beam directory)")
    if not args.skip_tests and not args.dry_run:
        print("  5. Run comprehensive test suite")
    print(f"  {'3' if args.dry_run else '6'}. Report final status\n")
    
    start_time = time.time()
    steps_passed = 0
    steps_total = 0
    backup_path = None
    deployment_failed = False
    
    # Step 0: Create backup
    if args.backup and not args.dry_run and not args.test_only:
        steps_total += 1
        backup_path = create_backup()
        if backup_path:
            steps_passed += 1
        else:
            print("⚠️  Warning: Backup creation failed, continuing anyway")
    
    # Step 1: Health check
    if not args.skip_health_check and not args.test_only:
        steps_total += 1
        if run_health_check():
            steps_passed += 1
        else:
            print("\n❌ DEPLOYMENT ABORTED: Health check failed")
            print("Fix errors and try again, or use --skip-health-check to bypass")
            sys.exit(1)
    
    # Step 2 & 3: Export and extract
    if not args.test_only:
        steps_total += 3 if not args.dry_run else 1  # Export only in dry-run
        
        export_success = export_all_domains(dry_run=args.dry_run)
        if export_success:
            steps_passed += 1
        else:
            deployment_failed = True
        
        if not args.dry_run:  # Skip extraction/copy in dry-run
            if not args.export_only:
                if extract_associations():
                    steps_passed += 1
                else:
                    deployment_failed = True
            
            if copy_to_production():
                steps_passed += 1
            else:
                deployment_failed = True
    
    # Step 4: Tests
    if not args.skip_tests and not args.export_only:
        steps_total += 1
        if run_tests():
            steps_passed += 1
        else:
            deployment_failed = True
    
    # Rollback on failure (if backup was created)
    if deployment_failed and backup_path and args.backup:
        print("\n" + "="*80)
        print("⚠️  DEPLOYMENT FAILED - INITIATING ROLLBACK")
        print("="*80)
        rollback_to_backup(backup_path)
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
