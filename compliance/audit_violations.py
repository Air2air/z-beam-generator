#!/usr/bin/env python3
"""
Audit violations against PROJECT_GUIDE.md
"""

import sys
from pathlib import Path
from validation_rules import ValidationRules

def print_header():
    """Print audit header"""
    print("🔍 PROJECT_GUIDE COMPLIANCE AUDIT")
    print("=" * 50)

def print_violations(violations: list, category: str):
    """Print violations for a specific category"""
    if violations:
        print(f"\n❌ {category}:")
        for violation in violations:
            print(f"  • {violation}")
    else:
        print(f"\n✅ {category}: NO VIOLATIONS")

def main():
    """Run comprehensive compliance audit"""
    print_header()
    
    # Get compliance score
    compliance_data = ValidationRules.get_compliance_score()
    
    # Run individual checks and display results
    file_violations = ValidationRules.check_file_structure()
    concept_violations = ValidationRules.check_forbidden_concepts()
    config_violations = ValidationRules.check_global_config_usage()
    simplicity_violations = ValidationRules.check_simplicity_violations()
    
    # Print results by category
    print_violations(file_violations, "FILE STRUCTURE VIOLATIONS")
    print_violations(concept_violations, "FORBIDDEN CONCEPT VIOLATIONS")
    print_violations(config_violations, "GLOBAL CONFIG VIOLATIONS")
    print_violations(simplicity_violations, "SIMPLICITY VIOLATIONS")
    
    # Print summary
    print(f"\n📊 COMPLIANCE SUMMARY")
    print("-" * 25)
    print(f"Total violations: {compliance_data['violation_count']}")
    print(f"Compliance score: {compliance_data['compliance_percentage']:.1f}%")
    print(f"Status: {compliance_data['status']}")
    
    # Exit with appropriate code
    if compliance_data['violation_count'] > 0:
        print(f"\n🚨 ACTION REQUIRED: Fix violations before proceeding")
        sys.exit(1)
    else:
        print(f"\n✅ PROJECT_GUIDE COMPLIANT: All checks passed")
        sys.exit(0)

if __name__ == "__main__":
    main()