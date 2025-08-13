#!/usr/bin/env python3
"""
Centralized CLI for Validation, Fixing, and Recovery

This replaces all the scattered validation/recovery CLI tools with one unified interface.
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from validators.centralized_validator import CentralizedValidator

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Centralized validation, fix, and recovery system")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate materials')
    validate_parser.add_argument('subject', nargs='?', help='Material to validate (optional)')
    validate_parser.add_argument('--scan-all', action='store_true', help='Scan all materials')
    
    # Fix command  
    fix_parser = subparsers.add_parser('fix', help='Fix/recover materials')
    fix_parser.add_argument('subject', help='Material to fix')
    fix_parser.add_argument('--components', nargs='+', help='Specific components to fix')
    fix_parser.add_argument('--no-regenerate', action='store_true', help='Only apply predefined fixes, no regeneration')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan all materials and show summary')
    
    # Test command for enhanced workflow
    test_parser = subparsers.add_parser('test-enhanced', help='Test enhanced validation workflow')
    test_parser.add_argument('subject', help='Material to test enhanced workflow on')
    test_parser.add_argument('--component', help='Specific component to test')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize validator
    validator = CentralizedValidator()
    
    # Execute command
    if args.command == 'validate':
        if args.scan_all or not args.subject:
            validator.cli_scan_all_materials()
        else:
            validator.cli_validate_material(args.subject)
    
    elif args.command == 'fix':
        regenerate = not args.no_regenerate
        validator.cli_fix_material(args.subject, args.components, regenerate)
    
    elif args.command == 'scan':
        validator.cli_scan_all_materials()
    
    elif args.command == 'test-enhanced':
        # Test the enhanced validation workflow
        import logging
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
        
        print(f"🧪 Testing enhanced validation workflow on {args.subject}")
        
        if args.component:
            print(f"   Testing component: {args.component}")
            result = validator.validate_and_fix_component_immediately(
                args.subject, args.component, max_retries=2
            )
            status = "✅ SUCCESS" if result else "❌ FAILED"
            print(f"   Result: {status}")
        else:
            # Test all components
            results = validator.validate_material(args.subject)
            failed_components = [comp for comp, result in results.items() 
                               if result.status.value != 'success']
            
            print(f"   Found {len(failed_components)} components needing enhanced validation")
            
            for component in failed_components:
                print(f"\n   🧪 Testing enhanced validation for {component}...")
                result = validator.validate_and_fix_component_immediately(
                    args.subject, component, max_retries=2
                )
                status = "✅ SUCCESS" if result else "❌ FAILED"
                print(f"   {component}: {status}")

if __name__ == '__main__':
    main()
