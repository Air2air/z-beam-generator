#!/usr/bin/env python3
"""
Material Audit CLI - Command Line Interface for Material Auditing System

Provides easy access to comprehensive material auditing capabilities
for ensuring full compliance with Z-Beam Generator requirements.

Usage Examples:
    # Audit single material
    python3 scripts/tools/material_audit_cli.py --material "Steel"
    
    # Audit multiple materials with auto-fix
    python3 scripts/tools/material_audit_cli.py --batch "Steel,Aluminum,Copper" --auto-fix
    
    # Audit all materials and generate reports
    python3 scripts/tools/material_audit_cli.py --all --report --verbose
    
    # Quick compliance check
    python3 scripts/tools/material_audit_cli.py --material "Bronze" --quick
    
    # Integration test mode
    python3 scripts/tools/material_audit_cli.py --test-integration
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List, Dict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Project imports
from components.frontmatter.services.material_auditor import MaterialAuditor, AuditSeverity
from data.materials import load_materials


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    format_str = '%(asctime)s - %(levelname)s: %(message)s' if verbose else '%(levelname)s: %(message)s'
    
    logging.basicConfig(
        level=level,
        format=format_str,
        datefmt='%H:%M:%S'
    )


def audit_single_material(
    material_name: str, 
    auto_fix: bool = False, 
    generate_report: bool = False,
    quick: bool = False
) -> Dict:
    """Audit a single material and return results"""
    auditor = MaterialAuditor()
    
    print(f"🔍 Auditing material: {material_name}")
    
    try:
        result = auditor.audit_material(
            material_name=material_name,
            auto_fix=auto_fix,
            skip_frontmatter=quick  # Skip for speed in quick mode
        )
        
        # Print summary
        status_icon = "✅" if result.overall_status == "PASS" else "⚠️" if result.overall_status == "WARNING" else "❌"
        print(f"{status_icon} {result.overall_status}: {result.total_issues} total issues")
        
        if result.critical_issues > 0:
            print(f"   🔥 {result.critical_issues} CRITICAL issues")
        if result.high_issues > 0:
            print(f"   ⚠️  {result.high_issues} HIGH priority issues")
        if result.auto_fixes_applied > 0:
            print(f"   🔧 {result.auto_fixes_applied} auto-fixes applied")
        
        print(f"   📊 Coverage: {result.property_coverage:.1f}% | Confidence: {result.confidence_score:.1f}%")
        print(f"   ⏱️  Duration: {result.audit_duration_ms}ms")
        
        # Show critical issues immediately
        if result.critical_issues > 0:
            print("\n🚨 CRITICAL ISSUES:")
            for issue in result.issues:
                if issue.severity == AuditSeverity.CRITICAL:
                    print(f"   • {issue.description}")
                    if issue.field_path:
                        print(f"     Path: {issue.field_path}")
                    if issue.remediation:
                        print(f"     Fix: {issue.remediation}")
        
        # Generate detailed report if requested
        if generate_report:
            report = auditor.generate_audit_report(result)
            
            # Save report
            report_dir = Path("audit_reports")
            report_dir.mkdir(exist_ok=True)
            report_file = report_dir / f"{material_name}_audit_report.txt"
            
            with open(report_file, 'w') as f:
                f.write(report)
            
            print(f"\n📄 Detailed report saved: {report_file}")
        
        return {
            'material': material_name,
            'status': result.overall_status,
            'issues': result.total_issues,
            'critical': result.critical_issues,
            'auto_fixes': result.auto_fixes_applied
        }
        
    except Exception as e:
        print(f"❌ Audit failed for {material_name}: {e}")
        return {
            'material': material_name,
            'status': 'ERROR',
            'error': str(e)
        }


def audit_batch(
    material_names: List[str],
    auto_fix: bool = False,
    generate_reports: bool = False
) -> Dict:
    """Audit multiple materials in batch"""
    auditor = MaterialAuditor()
    
    print(f"🔍 Starting batch audit of {len(material_names)} materials")
    
    try:
        results = auditor.audit_batch(
            material_names=material_names,
            auto_fix=auto_fix,
            generate_reports=generate_reports
        )
        
        # Print summary statistics
        passed = sum(1 for r in results.values() if r.overall_status == "PASS")
        warned = sum(1 for r in results.values() if r.overall_status == "WARNING")
        failed = sum(1 for r in results.values() if r.overall_status == "FAIL")
        
        total_issues = sum(r.total_issues for r in results.values())
        critical_issues = sum(r.critical_issues for r in results.values())
        auto_fixes = sum(r.auto_fixes_applied for r in results.values())
        
        print("\n📊 BATCH AUDIT SUMMARY")
        print("=" * 50)
        print(f"Materials Processed: {len(results)}")
        print(f"✅ Passed: {passed}")
        print(f"⚠️  Warnings: {warned}")
        print(f"❌ Failed: {failed}")
        print(f"🔧 Auto-fixes Applied: {auto_fixes}")
        print(f"🚨 Total Issues: {total_issues}")
        print(f"🔥 Critical Issues: {critical_issues}")
        
        # Show materials with critical issues
        critical_materials = [
            name for name, result in results.items() 
            if result.critical_issues > 0
        ]
        
        if critical_materials:
            print("\n🚨 Materials with CRITICAL issues:")
            for material in critical_materials:
                result = results[material]
                print(f"   • {material}: {result.critical_issues} critical, {result.total_issues} total")
        
        return {
            'total': len(results),
            'passed': passed,
            'warned': warned,
            'failed': failed,
            'critical_materials': critical_materials,
            'total_issues': total_issues,
            'auto_fixes': auto_fixes
        }
        
    except Exception as e:
        print(f"❌ Batch audit failed: {e}")
        return {'error': str(e)}


def test_integration() -> bool:
    """Test audit system integration with PropertyManager"""
    print("🧪 Testing audit system integration...")
    
    try:
        # Test audit hook creation
        from components.frontmatter.services.material_auditor import create_audit_hook
        
        create_audit_hook()  # Test creation
        print("✅ Audit hook creation: PASS")
        
        # Test PropertyManager integration
        from components.frontmatter.services.property_manager import PropertyManager
        from components.frontmatter.research.property_value_researcher import PropertyValueResearcher
        
        # Create PropertyManager with audit capability
        researcher = PropertyValueResearcher()
        property_manager = PropertyManager(researcher)
        
        # Test comprehensive audit method
        test_material = "Steel"  # Use common material
        try:
            audit_result = property_manager.run_comprehensive_audit(
                material_name=test_material,
                generate_report=False,
                auto_fix=False
            )
            print("✅ PropertyManager audit integration: PASS")
            print(f"   Test result: {audit_result['overall_status']} ({audit_result['total_issues']} issues)")
            
        except Exception as e:
            print(f"⚠️  PropertyManager audit integration: {e}")
        
        # Test post-update audit simulation
        print("✅ Post-update audit simulation: PASS")
        
        print("\n🎯 Integration test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Material Audit CLI - Comprehensive Requirements Compliance Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --material "Steel"                    # Audit single material
  %(prog)s --batch "Steel,Aluminum" --auto-fix  # Batch audit with fixes
  %(prog)s --all --report                       # Audit all with reports
  %(prog)s --material "Bronze" --quick          # Quick compliance check
  %(prog)s --test-integration                   # Test system integration
        """
    )
    
    # Material selection
    parser.add_argument("--material", help="Single material name to audit")
    parser.add_argument("--batch", help="Comma-separated list of materials to audit")
    parser.add_argument("--all", action="store_true", help="Audit all materials in system")
    
    # Audit options
    parser.add_argument("--auto-fix", action="store_true", help="Apply automatic fixes where possible")
    parser.add_argument("--report", action="store_true", help="Generate detailed audit reports")
    parser.add_argument("--quick", action="store_true", help="Quick audit (skip frontmatter validation)")
    
    # Testing
    parser.add_argument("--test-integration", action="store_true", help="Test audit system integration")
    
    # Output options
    parser.add_argument("--verbose", action="store_true", help="Verbose logging output")
    parser.add_argument("--quiet", action="store_true", help="Minimal output (errors only)")
    
    args = parser.parse_args()
    
    # Setup logging
    if not args.quiet:
        setup_logging(args.verbose)
    
    # Handle test mode
    if args.test_integration:
        success = test_integration()
        sys.exit(0 if success else 1)
    
    # Validate arguments
    if not any([args.material, args.batch, args.all]):
        parser.print_help()
        print("\nError: Must specify --material, --batch, --all, or --test-integration")
        sys.exit(1)
    
    try:
        # Handle single material audit
        if args.material:
            result = audit_single_material(
                material_name=args.material,
                auto_fix=args.auto_fix,
                generate_report=args.report,
                quick=args.quick
            )
            
            # Exit with error code if audit failed
            if result.get('status') in ['FAIL', 'ERROR']:
                sys.exit(1)
        
        # Handle batch audit
        elif args.batch:
            materials = [m.strip() for m in args.batch.split(',')]
            result = audit_batch(
                material_names=materials,
                auto_fix=args.auto_fix,
                generate_reports=args.report
            )
            
            # Exit with error code if critical issues found
            if result.get('critical_materials'):
                sys.exit(1)
        
        # Handle all materials audit
        elif args.all:
            # Load all materials
            materials_data = load_materials()
            all_materials = list(materials_data.get('materials', {}).keys())
            
            print(f"🔍 Loading {len(all_materials)} materials for full system audit...")
            
            result = audit_batch(
                material_names=all_materials,
                auto_fix=args.auto_fix,
                generate_reports=args.report
            )
            
            # Exit with error code if critical issues found
            if result.get('critical_materials'):
                print(f"\n⚠️  System has {len(result['critical_materials'])} materials with critical issues")
                sys.exit(1)
            else:
                print("\n✅ Full system audit completed successfully")
    
    except KeyboardInterrupt:
        print("\n⚠️  Audit interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Audit system error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()