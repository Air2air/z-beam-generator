#!/usr/bin/env python3
"""
Export System Health Check

Validates the export system before deployment to catch configuration
errors, missing dependencies, and other issues early.

Usage:
    python3 scripts/tools/health_check.py
    
    # Or import and use programmatically
    from scripts.tools.health_check import run_health_check
    report = run_health_check()

Created: Dec 20, 2025
"""

import sys
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from export.config.validator import validate_all_configs, check_config_health, ConfigurationError


def check_dependencies() -> Dict[str, Any]:
    """Check that all required dependencies are available"""
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Check critical imports
    critical_imports = [
        ('yaml', 'PyYAML'),
        ('pathlib', 'pathlib (stdlib)'),
    ]
    
    for module_name, package_name in critical_imports:
        try:
            __import__(module_name)
        except ImportError:
            result['valid'] = False
            result['errors'].append(f"Missing required package: {package_name}")
    
    # Check export system imports
    try:
        from export.core.universal_exporter import FrontmatterExporter
        from export.config.loader import load_domain_config
    except ImportError as e:
        result['valid'] = False
        result['errors'].append(f"Cannot import export system: {e}")
    
    return result


def check_data_files() -> Dict[str, Any]:
    """Check that all source data files exist"""
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'files_checked': 0
    }
    
    data_files = {
        'materials': PROJECT_ROOT / 'data' / 'materials' / 'Materials.yaml',
        'contaminants': PROJECT_ROOT / 'data' / 'contaminants' / 'Contaminants.yaml',
        'compounds': PROJECT_ROOT / 'data' / 'compounds' / 'Compounds.yaml',
        'settings': PROJECT_ROOT / 'data' / 'settings' / 'Settings.yaml',
    }
    
    for domain, file_path in data_files.items():
        if not file_path.exists():
            result['valid'] = False
            result['errors'].append(f"Missing source data file: {domain} ({file_path})")
        else:
            result['files_checked'] += 1
            
            # Check file is not empty
            if file_path.stat().st_size == 0:
                result['valid'] = False
                result['errors'].append(f"Source data file is empty: {domain}")
    
    return result


def check_output_directories() -> Dict[str, Any]:
    """Check that output directories are writable"""
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'dirs_checked': 0
    }
    
    # Check production frontmatter directory
    prod_frontmatter = PROJECT_ROOT.parent / 'z-beam' / 'frontmatter'
    
    if not prod_frontmatter.exists():
        result['warnings'].append(f"Production frontmatter directory doesn't exist yet: {prod_frontmatter}")
    elif not prod_frontmatter.is_dir():
        result['valid'] = False
        result['errors'].append(f"Production frontmatter path exists but is not a directory: {prod_frontmatter}")
    else:
        result['dirs_checked'] += 1
        
        # Check it's writable
        test_file = prod_frontmatter / '.write_test'
        try:
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Production frontmatter directory not writable: {e}")
    
    return result


def check_deployment_script() -> Dict[str, Any]:
    """Check that deployment script exists and is valid"""
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    deploy_script = PROJECT_ROOT / 'scripts' / 'operations' / 'deploy_all.py'
    
    if not deploy_script.exists():
        result['valid'] = False
        result['errors'].append(f"Deployment script not found: {deploy_script}")
    elif not deploy_script.is_file():
        result['valid'] = False
        result['errors'].append(f"Deployment script path is not a file: {deploy_script}")
    elif deploy_script.stat().st_size == 0:
        result['valid'] = False
        result['errors'].append("Deployment script is empty")
    
    return result


def run_health_check(verbose: bool = False) -> Dict[str, Any]:
    """
    Run complete health check on export system.
    
    Args:
        verbose: Print detailed progress
    
    Returns:
        Dict with overall status and detailed results
    """
    print("\n" + "="*80)
    print("📊 Z-BEAM GENERATOR HEALTH CHECK")
    print("="*80)
    
    overall_result = {
        'healthy': True,
        'checks_run': 0,
        'checks_passed': 0,
        'checks_failed': 0,
        'warnings': [],
        'errors': []
    }
    
    # Run all checks
    checks = [
        ("Dependencies", check_dependencies),
        ("Data Files", check_data_files),
        ("Export Configs", check_config_health),
        ("Output Directories", check_output_directories),
        ("Deployment Script", check_deployment_script),
    ]
    
    for check_name, check_func in checks:
        overall_result['checks_run'] += 1
        
        if verbose:
            print(f"\n🔍 Checking {check_name}...")
        
        try:
            result = check_func()
            
            if result['valid']:
                overall_result['checks_passed'] += 1
                print(f"✅ {check_name}: OK")
                
                if 'domains_checked' in result and verbose:
                    print(f"   ({result['domains_checked']} domains validated)")
                if 'files_checked' in result and verbose:
                    print(f"   ({result['files_checked']} files verified)")
            else:
                overall_result['checks_failed'] += 1
                overall_result['healthy'] = False
                print(f"❌ {check_name}: FAILED")
                
                for error in result.get('errors', []):
                    overall_result['errors'].append(f"{check_name}: {error}")
                    print(f"   - {error}")
            
            # Collect warnings
            for warning in result.get('warnings', []):
                overall_result['warnings'].append(f"{check_name}: {warning}")
                if verbose:
                    print(f"   ⚠️  {warning}")
                
        except Exception as e:
            overall_result['checks_failed'] += 1
            overall_result['healthy'] = False
            error_msg = f"{check_name} check crashed: {e}"
            overall_result['errors'].append(error_msg)
            print(f"❌ {check_name}: ERROR - {e}")
    
    # Print summary
    print("\n" + "="*80)
    print("📊 HEALTH CHECK SUMMARY")
    print("="*80)
    print(f"Checks Run: {overall_result['checks_run']}")
    print(f"✅ Passed: {overall_result['checks_passed']}")
    print(f"❌ Failed: {overall_result['checks_failed']}")
    
    if overall_result['warnings']:
        print(f"⚠️  Warnings: {len(overall_result['warnings'])}")
    
    if overall_result['healthy']:
        print("\n🎉 SYSTEM HEALTHY - Ready for deployment")
    else:
        print("\n⚠️  SYSTEM UNHEALTHY - Fix errors before deploying")
        print("\nErrors:")
        for error in overall_result['errors']:
            print(f"  - {error}")
    
    if overall_result['warnings'] and verbose:
        print("\nWarnings:")
        for warning in overall_result['warnings']:
            print(f"  - {warning}")
    
    print("="*80 + "\n")
    
    return overall_result


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Z-Beam export system health check')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    result = run_health_check(verbose=args.verbose)
    
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    
    # Exit with error code if unhealthy
    sys.exit(0 if result['healthy'] else 1)
