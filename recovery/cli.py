#!/usr/bin/env python3
"""
CLI Module for Recovery System

Command-line interfaces for validation and recovery operations.
Provides both validation and recovery functionality through simple commands.
"""

import sys
import os
import logging
import argparse
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

from .recovery_system import MaterialRecoverySystem, print_validation_report
from .recovery_runner import DirectRecoveryRunner
from .validator import ComponentStatus

def _filter_empty_invalid_components(recovery_system, subject: str, failed_components: list) -> list:
    """Filter failed components to only include empty and invalid ones."""
    report = recovery_system._validate_material(subject)
    
    empty_invalid_components = []
    for comp_name in failed_components:
        if comp_name in report.components:
            result = report.components[comp_name]
            # Include components that are empty, invalid, or missing (but not just low quality)
            if result.status in [ComponentStatus.EMPTY, ComponentStatus.INVALID, ComponentStatus.MISSING]:
                empty_invalid_components.append(comp_name)
    
    return empty_invalid_components

def validate_material(subject: str = None, scan_all: bool = False, auto_recover: bool = False, 
                     empty_invalid_only: bool = False):
    """Validate materials and optionally run recovery."""
    recovery_system = MaterialRecoverySystem()
    
    if scan_all or subject is None:
        print("🔍 Scanning all materials...")
        reports = recovery_system.scan_materials()
        
        if auto_recover:
            # Run recovery for all materials with failures
            for subj, report in reports.items():
                if report.failed_components:
                    # Filter for empty/invalid only if requested
                    components_to_recover = report.failed_components
                    if empty_invalid_only:
                        components_to_recover = _filter_empty_invalid_components(
                            recovery_system, subj, report.failed_components
                        )
                        if not components_to_recover:
                            print(f"⏭️  {subj}: No empty/invalid components to recover")
                            continue
                    
                    print(f"\n🔄 Recovering {subj}...")
                    if empty_invalid_only:
                        print(f"   Targeting empty/invalid components only: {', '.join(components_to_recover)}")
                    
                    results = recovery_system.run_recovery(
                        subj, components_to_recover, timeout=45, retry_count=2
                    )
                    
                    success_count = sum(1 for success in results.values() if success)
                    total_count = len(results)
                    print(f"Recovery results: {success_count}/{total_count} succeeded")
        else:
            # Just show summary
            total_materials = len(reports)
            healthy_materials = sum(1 for r in reports.values() if r.overall_status.value == 'success')
            
            print(f"\n📈 Summary: {healthy_materials}/{total_materials} materials healthy")
            
            # Show problem materials
            problem_materials = [(subj, report) for subj, report in reports.items() 
                               if report.failed_components]
            
            if problem_materials:
                print(f"\n⚠️  Materials needing attention ({len(problem_materials)}):")
                for subj, report in problem_materials:
                    failed_list = ", ".join(report.failed_components)
                    print(f"  • {subj}: {failed_list}")
                
                if empty_invalid_only:
                    print("\n💡 Run with --auto-recover --empty-invalid-only to fix empty/invalid issues automatically")
                else:
                    print("\n💡 Run with --auto-recover to fix issues automatically")
            else:
                print("\n✅ All materials are healthy!")
    
    elif subject:
        print(f"🔍 Validating {subject}...")
        report = recovery_system._validate_material(subject)
        print_validation_report(report)
        
        # Show recovery commands if needed
        if report.failed_components:
            print("\n🔧 Recovery Commands:")
            
            if empty_invalid_only:
                # Show only empty/invalid components for recovery
                empty_invalid_components = _filter_empty_invalid_components(recovery_system, subject, report.failed_components)
                if empty_invalid_components:
                    commands = recovery_system.generate_recovery_commands(subject, empty_invalid_components)
                    print(f"Empty/Invalid components only: {', '.join(empty_invalid_components)}")
                    for cmd in commands:
                        print(f"  {cmd}")
                else:
                    print("  No empty/invalid components found - all failures are quality-related")
            else:
                commands = recovery_system.generate_recovery_commands(subject, report.failed_components)
                for cmd in commands:
                    print(f"  {cmd}")

def recover_components(subject: str, components: list, article_type: str = "material", 
                      category: str = None, author_id: int = 1, timeout: int = 60, 
                      retry_count: int = 3, verbose: bool = False):
    """Recover specific components for a subject."""
    
    # Configure logging
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Run recovery
    runner = DirectRecoveryRunner()
    results = runner.recover_components(
        subject=subject,
        failed_components=components,
        article_type=article_type,
        category=category,
        author_id=author_id,
        timeout=timeout,
        retry_count=retry_count
    )
    
    # Report results
    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    
    print(f"\n📊 Recovery Results: {success_count}/{total_count} succeeded")
    for component, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"  {component}: {status}")

def interactive_check_and_fix(timeout: int = 45, retry_count: int = 2, verbose: bool = False):
    """Interactive check for empty/invalid components within BATCH_CONFIG limits."""
    # Configure logging
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🔍 Interactive Check: Empty/Invalid Components within BATCH_CONFIG limits")
    print("="*70)
    
    # Load BATCH_CONFIG to get the same subjects that would be processed
    try:
        import sys
        import os
        sys.path.insert(0, os.path.abspath('.'))
        import run
        batch_config = run.BATCH_CONFIG
        
        # Get subjects that match current BATCH_CONFIG settings
        if batch_config["mode"] == "single":
            config = batch_config["single_subject"] 
            subjects_to_check = [config["subject"]]
            print(f"📋 Mode: Single subject - {config['subject']}")
        elif batch_config["mode"] == "multi":
            config = batch_config["multi_subject"]
            
            # Get all subjects with their categories and article types
            if config["subject_source"] == "lists":
                yaml_path = os.path.join("lists", "materials.yaml")
                if os.path.exists(yaml_path):
                    subjects_with_info = run.get_subjects_from_consolidated_yaml(yaml_path)
                else:
                    subjects_with_info = run.get_subjects_with_categories_from_directory("lists")
            else:
                subjects_with_info = []
            
            # Apply the same limit logic as generation
            limit = config.get("limit")
            if limit is not None:
                if isinstance(limit, list) and len(limit) == 2:
                    start_idx, end_idx = limit
                    subjects_to_validate = subjects_with_info[start_idx:end_idx+1]
                    print(f"📋 Mode: Multi subjects (indices {start_idx}-{end_idx}) - {len(subjects_to_validate)} subjects")
                else:
                    subjects_to_validate = subjects_with_info[:limit]
                    print(f"📋 Mode: Multi subjects (first {limit}) - {len(subjects_to_validate)} subjects")
            else:
                subjects_to_validate = subjects_with_info
                print(f"📋 Mode: Multi subjects (all) - {len(subjects_to_validate)} subjects")
            
            subjects_to_check = [s["subject"] for s in subjects_to_validate]
        else:
            print("❌ Invalid BATCH_CONFIG mode")
            return
            
    except Exception as e:
        print(f"❌ Failed to load BATCH_CONFIG: {e}")
        return
    
    # Initialize recovery system
    recovery_system = MaterialRecoverySystem()
    print(f"🎯 Enabled components: {', '.join(recovery_system.components)}")
    print("-" * 70)
    
    # Step 1: Scan for empty/invalid components
    print("🔍 Step 1: Scanning for empty/invalid components...")
    
    subjects_needing_fix = {}
    total_empty_invalid = 0
    
    for subject in subjects_to_check:
        report = recovery_system._validate_material(subject)
        
        if report.failed_components:
            # Filter for empty/invalid only
            empty_invalid_components = _filter_empty_invalid_components(
                recovery_system, subject, report.failed_components
            )
            
            if empty_invalid_components:
                subjects_needing_fix[subject] = empty_invalid_components
                total_empty_invalid += len(empty_invalid_components)
                
                # Show status for this subject
                success_rate = report.successful_components / report.total_components * 100
                status_emoji = "⚠️" if success_rate >= 50 else "❌"
                
                print(f"  {status_emoji} {subject}: {report.successful_components}/{report.total_components} "
                      f"({success_rate:.1f}% success)")
                print(f"      Empty/Invalid: {', '.join(empty_invalid_components)}")
    
    # Results of scan
    print("\n" + "="*70)
    print("📊 SCAN RESULTS")
    print("="*70)
    print(f"Total subjects scanned: {len(subjects_to_check)}")
    print(f"Subjects needing empty/invalid fixes: {len(subjects_needing_fix)}")
    print(f"Total empty/invalid components found: {total_empty_invalid}")
    
    if not subjects_needing_fix:
        print("\n✅ No empty/invalid components found! All components are either successful or have quality-only issues.")
        return
    
    # Step 2: Ask user if they want to generate
    print(f"\n🤔 Step 2: Do you want to generate the {total_empty_invalid} empty/invalid components?")
    print("This will target only the components that are completely missing or empty.")
    print("Quality-related issues will be ignored.")
    
    while True:
        user_input = input("\nProceed with generation? (y/n): ").lower().strip()
        if user_input in ['y', 'yes']:
            proceed = True
            break
        elif user_input in ['n', 'no']:
            proceed = False
            break
        else:
            print("Please enter 'y' or 'n'")
    
    if not proceed:
        print("\n⏭️ Generation cancelled by user.")
        return
    
    # Step 3: Generate the components
    print(f"\n🚀 Step 3: Generating {total_empty_invalid} empty/invalid components...")
    print("-" * 50)
    
    total_fixed = 0
    generation_results = {}
    
    for subject, empty_invalid_components in subjects_needing_fix.items():
        print(f"\n🔧 Fixing {subject}...")
        print(f"   Components: {', '.join(empty_invalid_components)}")
        
        results = recovery_system.run_recovery(
            subject, empty_invalid_components, timeout=timeout, retry_count=retry_count
        )
        
        success_count = sum(1 for success in results.values() if success)
        total_fixed += success_count
        generation_results[subject] = results
        
        print(f"   Results: {success_count}/{len(results)} generated successfully")
        
        # Show individual component results
        for component, success in results.items():
            status = "✅" if success else "❌"
            print(f"     {status} {component}")
    
    # Step 4: Final report
    print("\n" + "="*70)
    print("📊 FINAL REPORT")
    print("="*70)
    print(f"Subjects processed: {len(subjects_needing_fix)}")
    print(f"Components attempted: {total_empty_invalid}")
    print(f"Components successfully generated: {total_fixed}")
    print(f"Success rate: {total_fixed/total_empty_invalid*100:.1f}%")
    
    # Re-scan to show current status
    print("\n🔍 Current status after generation:")
    print("-" * 40)
    
    for subject in subjects_needing_fix.keys():
        report = recovery_system._validate_material(subject)
        success_rate = report.successful_components / report.total_components * 100
        status_emoji = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 50 else "❌"
        
        print(f"  {status_emoji} {subject}: {report.successful_components}/{report.total_components} "
              f"({success_rate:.1f}% success)")
        
        if report.failed_components:
            remaining_empty_invalid = _filter_empty_invalid_components(
                recovery_system, subject, report.failed_components
            )
            if remaining_empty_invalid:
                print(f"      Still empty/invalid: {', '.join(remaining_empty_invalid)}")
            else:
                print(f"      Remaining issues are quality-related: {', '.join(report.failed_components)}")
    
    print("\n✨ Interactive check completed!")

def quick_fix_empty_invalid(scan_all: bool = False, subject: str = None, 
                           timeout: int = 30, retry_count: int = 2, verbose: bool = False):
    """Quick fix for empty/invalid components only."""
    # Configure logging
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    recovery_system = MaterialRecoverySystem()
    
    if scan_all or subject is None:
        print("🚀 Quick-fix: Scanning for empty/invalid components only...")
        reports = recovery_system.scan_materials()
        
        total_materials = len(reports)
        materials_needing_fix = 0
        total_fixed = 0
        
        for subj, report in reports.items():
            if report.failed_components:
                # Filter for empty/invalid only
                empty_invalid_components = _filter_empty_invalid_components(
                    recovery_system, subj, report.failed_components
                )
                
                if empty_invalid_components:
                    materials_needing_fix += 1
                    print(f"\n🔧 Quick-fixing {subj}...")
                    print(f"   Empty/Invalid: {', '.join(empty_invalid_components)}")
                    
                    results = recovery_system.run_recovery(
                        subj, empty_invalid_components, timeout=timeout, retry_count=retry_count
                    )
                    
                    success_count = sum(1 for success in results.values() if success)
                    total_fixed += success_count
                    print(f"   Results: {success_count}/{len(results)} fixed")
        
        print("\n📊 Quick-Fix Summary:")
        print(f"   Materials processed: {total_materials}")
        print(f"   Materials needing empty/invalid fixes: {materials_needing_fix}")
        print(f"   Total components fixed: {total_fixed}")
        
    elif subject:
        print(f"🔧 Quick-fixing {subject} for empty/invalid components...")
        report = recovery_system._validate_material(subject)
        
        if report.failed_components:
            empty_invalid_components = _filter_empty_invalid_components(
                recovery_system, subject, report.failed_components
            )
            
            if empty_invalid_components:
                print(f"Empty/Invalid components: {', '.join(empty_invalid_components)}")
                
                results = recovery_system.run_recovery(
                    subject, empty_invalid_components, timeout=timeout, retry_count=retry_count
                )
                
                success_count = sum(1 for success in results.values() if success)
                print(f"Results: {success_count}/{len(results)} components fixed")
            else:
                print("✅ No empty/invalid components found - all failures are quality-related")
        else:
            print("✅ No failed components found")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Material Generation Recovery System")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate materials')
    validate_parser.add_argument('subject', nargs='?', help='Subject to validate (optional)')
    validate_parser.add_argument('--scan-all', action='store_true', help='Scan all materials')
    validate_parser.add_argument('--auto-recover', action='store_true', help='Automatically recover failures')
    validate_parser.add_argument('--empty-invalid-only', action='store_true', help='Only target empty/invalid components (not quality issues)')
    
    # Recover command  
    recover_parser = subparsers.add_parser('recover', help='Recover components')
    recover_parser.add_argument('subject', help='Subject to recover')
    recover_parser.add_argument('--components', nargs='+', required=True, 
                               help='Components to recover (e.g., frontmatter metatags)')
    recover_parser.add_argument('--article-type', default='material', 
                               help='Article type (default: material)')
    recover_parser.add_argument('--category', help='Category (auto-detected if not provided)')
    recover_parser.add_argument('--author-id', type=int, default=1, help='Author ID (default: 1)')
    recover_parser.add_argument('--timeout', type=int, default=60, help='Timeout per component')
    recover_parser.add_argument('--retry', type=int, default=3, help='Retry count')
    recover_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    # Quick recovery for empty/invalid only
    quick_parser = subparsers.add_parser('quick-fix', help='Quick fix for empty/invalid components only')
    quick_parser.add_argument('--scan-all', action='store_true', help='Scan and fix all materials')
    quick_parser.add_argument('subject', nargs='?', help='Specific subject to fix (optional with --scan-all)')
    quick_parser.add_argument('--timeout', type=int, default=30, help='Timeout per component (default: 30s)')
    quick_parser.add_argument('--retry', type=int, default=2, help='Retry count (default: 2)')
    quick_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    # Interactive check command
    check_parser = subparsers.add_parser('check', help='Interactive check for empty/invalid components within BATCH_CONFIG limits')
    check_parser.add_argument('--timeout', type=int, default=45, help='Timeout per component (default: 45s)')
    check_parser.add_argument('--retry', type=int, default=2, help='Retry count (default: 2)')
    check_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.command == 'validate':
        validate_material(
            subject=args.subject,
            scan_all=args.scan_all,
            auto_recover=args.auto_recover,
            empty_invalid_only=args.empty_invalid_only
        )
    elif args.command == 'recover':
        recover_components(
            subject=args.subject,
            components=args.components,
            article_type=args.article_type,
            category=args.category,
            author_id=args.author_id,
            timeout=args.timeout,
            retry_count=args.retry,
            verbose=args.verbose
        )
    elif args.command == 'quick-fix':
        quick_fix_empty_invalid(
            scan_all=args.scan_all,
            subject=args.subject,
            timeout=args.timeout,
            retry_count=args.retry,
            verbose=args.verbose
        )
    elif args.command == 'check':
        interactive_check_and_fix(
            timeout=args.timeout,
            retry_count=args.retry,
            verbose=args.verbose
        )
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
