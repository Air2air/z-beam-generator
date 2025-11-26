#!/usr/bin/env python3
"""
Audit Command Handlers

Handles material auditing and compliance checking.
"""


def handle_material_audit(args):
    """Handle material auditing requests with comprehensive requirements compliance checking"""
    try:
        from pathlib import Path
        from shared.services.property.material_auditor import MaterialAuditor, AuditSeverity
        from domains.materials.materials_cache import load_materials
        
        print("🔍 MATERIAL AUDITING SYSTEM")
        print("=" * 70)
        
        # Initialize auditor
        auditor = MaterialAuditor()
        
        if args.audit:
            # Single material audit
            print(f"Auditing material: {args.audit}")
            
            result = auditor.audit_material(
                material_name=args.audit,
                auto_fix=args.audit_auto_fix,
                skip_frontmatter=args.audit_quick
            )
            
            # Print summary
            status_icon = "✅" if result.overall_status == "PASS" else "⚠️" if result.overall_status == "WARNING" else "❌"
            print(f"\n{status_icon} {result.overall_status}: {result.total_issues} total issues")
            
            if result.critical_issues > 0:
                print(f"   🔥 {result.critical_issues} CRITICAL issues")
            if result.high_issues > 0:
                print(f"   ⚠️  {result.high_issues} HIGH priority issues")
            if result.auto_fixes_applied > 0:
                print(f"   🔧 {result.auto_fixes_applied} auto-fixes applied")
            
            print(f"   📊 Property Coverage: {result.property_coverage:.1f}%")
            print(f"   📈 Confidence Score: {result.confidence_score:.1f}%")
            print(f"   ⏱️  Duration: {result.audit_duration_ms}ms")
            
            # Show critical issues
            if result.critical_issues > 0:
                print("\n🚨 CRITICAL ISSUES:")
                for issue in result.issues:
                    if issue.severity == AuditSeverity.CRITICAL:
                        print(f"   • {issue.description}")
                        if issue.field_path:
                            print(f"     Path: {issue.field_path}")
                        if issue.remediation:
                            print(f"     Fix: {issue.remediation}")
            
            # Generate report if requested
            if args.audit_report:
                report = auditor.generate_audit_report(result)
                
                # Save report
                report_dir = Path("audit_reports")
                report_dir.mkdir(exist_ok=True)
                report_file = report_dir / f"{args.audit}_audit_report.txt"
                
                with open(report_file, 'w') as f:
                    f.write(report)
                
                print(f"\n📄 Detailed report saved: {report_file}")
            
            # Return success/failure based on audit result
            return result.overall_status != "FAIL"
        
        elif args.audit_batch:
            # Batch material audit
            materials = [m.strip() for m in args.audit_batch.split(',')]
            print(f"Auditing {len(materials)} materials: {', '.join(materials)}")
            
            results = auditor.audit_batch(
                material_names=materials,
                auto_fix=args.audit_auto_fix,
                generate_reports=args.audit_report
            )
            
            # Print summary
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
            
            # Show critical materials
            critical_materials = [
                name for name, result in results.items() 
                if result.critical_issues > 0
            ]
            
            if critical_materials:
                print("\n🚨 Materials with CRITICAL issues:")
                for material in critical_materials:
                    result = results[material]
                    print(f"   • {material}: {result.critical_issues} critical, {result.total_issues} total")
            
            return len(critical_materials) == 0
            
        elif args.audit_all:
            # Audit all materials
            materials_data = load_materials()
            all_materials = list(materials_data.get('materials', {}).keys())
            
            print(f"Auditing ALL {len(all_materials)} materials in system...")
            
            results = auditor.audit_batch(
                material_names=all_materials,
                auto_fix=args.audit_auto_fix,
                generate_reports=args.audit_report
            )
            
            # Print comprehensive summary
            passed = sum(1 for r in results.values() if r.overall_status == "PASS")
            warned = sum(1 for r in results.values() if r.overall_status == "WARNING")
            failed = sum(1 for r in results.values() if r.overall_status == "FAIL")
            
            total_issues = sum(r.total_issues for r in results.values())
            critical_issues = sum(r.critical_issues for r in results.values())
            auto_fixes = sum(r.auto_fixes_applied for r in results.values())
            
            print("\n🎯 FULL SYSTEM AUDIT SUMMARY")
            print("=" * 70)
            print(f"Total Materials: {len(results)}")
            print(f"✅ Compliant: {passed} ({passed/len(results)*100:.1f}%)")
            print(f"⚠️  Warnings: {warned} ({warned/len(results)*100:.1f}%)")
            print(f"❌ Failed: {failed} ({failed/len(results)*100:.1f}%)")
            print(f"🔧 Auto-fixes Applied: {auto_fixes}")
            print(f"🚨 Total Issues Found: {total_issues}")
            print(f"🔥 Critical Issues: {critical_issues}")
            
            # Calculate compliance score
            compliance_score = (passed + warned * 0.5) / len(results) * 100
            print(f"📊 System Compliance Score: {compliance_score:.1f}%")
            
            # Show worst offenders
            critical_materials = [
                (name, result) for name, result in results.items() 
                if result.critical_issues > 0
            ]
            
            if critical_materials:
                print(f"\n🚨 {len(critical_materials)} materials with CRITICAL issues:")
                # Sort by number of critical issues (worst first)
                critical_materials.sort(key=lambda x: x[1].critical_issues, reverse=True)
                for material, result in critical_materials[:10]:  # Show top 10
                    print(f"   • {material}: {result.critical_issues} critical, {result.total_issues} total")
                
                if len(critical_materials) > 10:
                    print(f"   ... and {len(critical_materials) - 10} more materials")
            else:
                print("\n✅ No materials with critical issues - excellent compliance!")
            
            return len(critical_materials) == 0
        
        return True
        
    except ImportError as e:
        print(f"❌ Audit system not available: {e}")
        print("Please ensure material_auditor.py is properly installed")
        return False
    except Exception as e:
        print(f"❌ Audit failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# =================================================================================
# DATA COMPLETENESS REPORTING & ANALYSIS
# =================================================================================

