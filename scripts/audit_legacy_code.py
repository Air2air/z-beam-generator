#!/usr/bin/env python3
"""
Comprehensive legacy code audit - find ALL duplicate functionality, orphaned modules, and dead code.
"""
import os
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

def analyze_python_files(root_dir: str) -> Dict:
    """Analyze all Python files for patterns, imports, and potential duplicates."""
    
    results = {
        'classes': defaultdict(list),  # class_name -> [file_paths]
        'functions': defaultdict(list),  # func_name -> [file_paths]
        'imports': defaultdict(set),  # file -> set of imported modules
        'api_clients': [],  # Files that implement API clients
        'config_loaders': [],  # Files that load configuration
        'generators': [],  # Files that generate content
        'validators': [],  # Files that validate data
        'managers': [],  # Files with Manager classes
        'services': [],  # Files with Service classes
        'orchestrators': [],  # Files that orchestrate processes
        'total_files': 0,
        'total_lines': 0
    }
    
    skip_dirs = {'.archive', '__pycache__', '.git', 'venv', 'env', '.pytest_cache'}
    
    for root, dirs, files in os.walk(root_dir):
        # Skip archive and cache directories
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if not file.endswith('.py'):
                continue
                
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, root_dir)
            
            results['total_files'] += 1
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    results['total_lines'] += len(lines)
                    
                    # Find class definitions
                    class_matches = re.finditer(r'^class\s+(\w+)', content, re.MULTILINE)
                    for match in class_matches:
                        class_name = match.group(1)
                        results['classes'][class_name].append(rel_path)
                    
                    # Find function definitions (top-level only)
                    func_matches = re.finditer(r'^def\s+(\w+)', content, re.MULTILINE)
                    for match in func_matches:
                        func_name = match.group(1)
                        results['functions'][func_name].append(rel_path)
                    
                    # Find imports
                    import_matches = re.finditer(r'^(?:from\s+([\w.]+)|import\s+([\w.]+))', content, re.MULTILINE)
                    for match in import_matches:
                        module = match.group(1) or match.group(2)
                        results['imports'][rel_path].add(module)
                    
                    # Categorize by patterns
                    lower_content = content.lower()
                    
                    if 'apiclient' in content or 'class.*client' in content.lower():
                        results['api_clients'].append(rel_path)
                    
                    if 'yaml.safe_load' in content or 'yaml.load' in content or 'load_config' in lower_content:
                        results['config_loaders'].append(rel_path)
                    
                    if 'generator' in file.lower() or 'class.*generator' in lower_content:
                        results['generators'].append(rel_path)
                    
                    if 'validator' in file.lower() or 'class.*validator' in lower_content:
                        results['validators'].append(rel_path)
                    
                    if 'manager' in file.lower() or 'class.*manager' in lower_content:
                        results['managers'].append(rel_path)
                    
                    if 'service' in file.lower() or 'class.*service' in lower_content:
                        results['services'].append(rel_path)
                    
                    if 'orchestrator' in file.lower() or 'class.*orchestrator' in lower_content:
                        results['orchestrators'].append(rel_path)
                        
            except Exception as e:
                print(f"Error reading {rel_path}: {e}")
    
    return results


def find_duplicates(results: Dict) -> Dict:
    """Find duplicate class and function names."""
    duplicates = {
        'classes': {},
        'functions': {}
    }
    
    for class_name, files in results['classes'].items():
        if len(files) > 1:
            duplicates['classes'][class_name] = files
    
    for func_name, files in results['functions'].items():
        if len(files) > 1 and not func_name.startswith('_'):  # Ignore private functions
            duplicates['functions'][func_name] = files
    
    return duplicates


def find_config_systems(root_dir: str) -> Dict:
    """Find all configuration systems (YAML + Python config objects)."""
    config_files = defaultdict(list)
    
    skip_dirs = {'.archive', '__pycache__', '.git', 'venv', 'env'}
    
    # Find all config-related files
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, root_dir)
            
            # YAML configs
            if file.endswith(('.yaml', '.yml')) and 'config' in file.lower():
                config_files['yaml_configs'].append(rel_path)
            
            # Python config modules
            if file.endswith('.py') and ('config' in file.lower() or 'settings' in file.lower()):
                config_files['python_configs'].append(rel_path)
    
    return config_files


def find_orphaned_modules(results: Dict) -> List[str]:
    """Find Python files that are never imported by other files."""
    all_files = set()
    imported_modules = set()
    
    for file in results['imports'].keys():
        all_files.add(file)
        
        # Convert imports to file paths
        for module in results['imports'][file]:
            # Simple heuristic: convert module.name to module/name.py or module.py
            module_parts = module.split('.')
            
            # Try direct file
            potential_file = f"{'/'.join(module_parts)}.py"
            imported_modules.add(potential_file)
            
            # Try as package
            potential_init = f"{'/'.join(module_parts)}/__init__.py"
            imported_modules.add(potential_init)
    
    # Files that exist but aren't imported (exclude __init__.py, conftest.py, run.py, test files)
    orphaned = []
    for file in all_files:
        basename = os.path.basename(file)
        if (file not in imported_modules and 
            basename not in ['__init__.py', 'conftest.py', 'run.py'] and
            not basename.startswith('test_')):
            orphaned.append(file)
    
    return orphaned


def print_report(results: Dict, duplicates: Dict, config_systems: Dict, orphaned: List[str]):
    """Print comprehensive audit report."""
    
    print("=" * 80)
    print("COMPREHENSIVE LEGACY CODE AUDIT")
    print("=" * 80)
    print()
    
    print(f"📊 OVERALL STATISTICS")
    print(f"  Total Python files: {results['total_files']}")
    print(f"  Total lines of code: {results['total_lines']:,}")
    print(f"  Unique classes: {len(results['classes'])}")
    print(f"  Unique functions: {len(results['functions'])}")
    print()
    
    print("=" * 80)
    print("🔍 DUPLICATE CLASS NAMES (Same class in multiple files)")
    print("=" * 80)
    if duplicates['classes']:
        for class_name, files in sorted(duplicates['classes'].items()):
            print(f"\n❌ {class_name} defined in {len(files)} files:")
            for f in sorted(files):
                print(f"    - {f}")
    else:
        print("✅ No duplicate class names found")
    print()
    
    print("=" * 80)
    print("🔍 DUPLICATE FUNCTION NAMES (Same function in multiple files)")
    print("=" * 80)
    if duplicates['functions']:
        # Limit to most suspicious duplicates
        suspicious = {k: v for k, v in duplicates['functions'].items() if len(v) > 2}
        if suspicious:
            for func_name, files in sorted(suspicious.items(), key=lambda x: len(x[1]), reverse=True)[:20]:
                print(f"\n❌ {func_name} defined in {len(files)} files:")
                for f in sorted(files):
                    print(f"    - {f}")
        else:
            print("✅ No highly suspicious function duplicates (>2 files)")
    else:
        print("✅ No duplicate function names found")
    print()
    
    print("=" * 80)
    print("⚙️  CONFIGURATION SYSTEMS (Potential duplication)")
    print("=" * 80)
    print(f"\n📄 YAML Config Files ({len(config_systems.get('yaml_configs', []))}):")
    for f in sorted(config_systems.get('yaml_configs', [])):
        print(f"  - {f}")
    
    print(f"\n🐍 Python Config Modules ({len(config_systems.get('python_configs', []))}):")
    for f in sorted(config_systems.get('python_configs', [])):
        print(f"  - {f}")
    print()
    
    print("=" * 80)
    print("🏗️  ARCHITECTURAL PATTERNS")
    print("=" * 80)
    print(f"\n🔌 API Clients ({len(results['api_clients'])}):")
    for f in sorted(results['api_clients'])[:10]:
        print(f"  - {f}")
    if len(results['api_clients']) > 10:
        print(f"  ... and {len(results['api_clients']) - 10} more")
    
    print(f"\n📝 Generators ({len(results['generators'])}):")
    for f in sorted(results['generators']):
        print(f"  - {f}")
    
    print(f"\n✅ Validators ({len(results['validators'])}):")
    for f in sorted(results['validators'])[:10]:
        print(f"  - {f}")
    if len(results['validators']) > 10:
        print(f"  ... and {len(results['validators']) - 10} more")
    
    print(f"\n🎛️  Managers ({len(results['managers'])}):")
    for f in sorted(results['managers']):
        print(f"  - {f}")
    
    print(f"\n🔧 Services ({len(results['services'])}):")
    for f in sorted(results['services']):
        print(f"  - {f}")
    
    print(f"\n🎭 Orchestrators ({len(results['orchestrators'])}):")
    for f in sorted(results['orchestrators']):
        print(f"  - {f}")
    print()
    
    print("=" * 80)
    print("👻 POTENTIALLY ORPHANED MODULES (Never imported)")
    print("=" * 80)
    if orphaned:
        print(f"Found {len(orphaned)} potentially orphaned files:")
        # Group by directory
        by_dir = defaultdict(list)
        for f in orphaned:
            dir_name = os.path.dirname(f) or 'root'
            by_dir[dir_name].append(os.path.basename(f))
        
        for dir_name in sorted(by_dir.keys()):
            print(f"\n📁 {dir_name}/")
            for basename in sorted(by_dir[dir_name]):
                print(f"    - {basename}")
    else:
        print("✅ No obviously orphaned modules found")
    print()
    
    print("=" * 80)
    print("🎯 CRITICAL FINDINGS")
    print("=" * 80)
    
    critical_findings = []
    
    # Check for multiple API client implementations
    if 'APIClient' in duplicates['classes']:
        critical_findings.append(f"❌ Multiple APIClient implementations: {duplicates['classes']['APIClient']}")
    
    # Check for multiple config loaders
    if len(config_systems.get('yaml_configs', [])) > 5:
        critical_findings.append(f"⚠️  Excessive YAML config files ({len(config_systems.get('yaml_configs', []))})")
    
    # Check for multiple orchestrators
    if len(results['orchestrators']) > 3:
        critical_findings.append(f"⚠️  Multiple orchestrators ({len(results['orchestrators'])}) - potential duplication")
    
    if critical_findings:
        for finding in critical_findings:
            print(f"  {finding}")
    else:
        print("  ✅ No critical duplication patterns detected")
    print()


if __name__ == '__main__':
    root_dir = '/Users/todddunning/Desktop/Z-Beam/z-beam-generator'
    
    print("Starting comprehensive legacy code audit...")
    print()
    
    results = analyze_python_files(root_dir)
    duplicates = find_duplicates(results)
    config_systems = find_config_systems(root_dir)
    orphaned = find_orphaned_modules(results)
    
    print_report(results, duplicates, config_systems, orphaned)
