#!/usr/bin/env python3
"""
Quick validation script for material generation

Usage:
    python3 validate.py                    # Scan all materials
    python3 validate.py "Tempered Glass"   # Validate specific material
    python3 validate.py --recover          # Scan and auto-recover failures
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from recovery.recovery_system import MaterialRecoverySystem, print_validation_report

def main():
    recovery_system = MaterialRecoverySystem()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--recover':
            # Scan all and recover failures
            print("🔍 Scanning all materials for recovery...")
            reports = recovery_system.scan_materials()
            
            for subject, report in reports.items():
                if report.failed_components:
                    print(f"\n🔄 Recovering {subject}...")
                    results = recovery_system.run_recovery(
                        subject, report.failed_components, timeout=45, retry_count=2
                    )
                    
                    success_count = sum(1 for success in results.values() if success)
                    total_count = len(results)
                    print(f"Recovery results: {success_count}/{total_count} succeeded")
        else:
            # Validate specific material
            subject = sys.argv[1]
            print(f"🔍 Validating {subject}...")
            report = recovery_system._validate_material(subject)
            print_validation_report(report)
            
            # Show recovery commands if needed
            if report.failed_components:
                print("\n🔧 Recovery Commands:")
                commands = recovery_system.generate_recovery_commands(subject, report.failed_components)
                for cmd in commands:
                    print(f"  {cmd}")
    else:
        # Scan all materials
        print("🔍 Scanning all materials...")
        reports = recovery_system.scan_materials()
        
        # Summary
        total_materials = len(reports)
        healthy_materials = sum(1 for r in reports.values() if r.overall_status.value == 'success')
        
        print(f"\n📈 Summary: {healthy_materials}/{total_materials} materials healthy")
        
        # Show problem materials
        problem_materials = [(subject, report) for subject, report in reports.items() 
                           if report.failed_components]
        
        if problem_materials:
            print(f"\n⚠️  Materials needing attention ({len(problem_materials)}):")
            for subject, report in problem_materials:
                failed_list = ", ".join(report.failed_components)
                print(f"  • {subject}: {failed_list}")
            
            print("\n💡 Run 'python3 validate.py --recover' to auto-fix issues")
        else:
            print("\n✅ All materials are healthy!")

if __name__ == "__main__":
    main()
