#!/usr/bin/env python3
"""Comprehensive unused file detection using multiple strategies.

Combines 6 detection methods:
1. Import Analysis - Find unimported Python modules
2. Reference Scanning - Find unreferenced files
3. Execution Tracking - Find never-executed scripts
4. Size Analysis - Find large, old, suspicious files
5. Date-Based Cleanup - Archive old backups/logs
6. Dependency Graph - Find isolated modules

Usage:
    python3 scripts/tools/find_unused_files.py --strategy all
    python3 scripts/tools/find_unused_files.py --strategy imports
    python3 scripts/tools/find_unused_files.py --strategy backups --auto-archive
"""

import argparse
import ast
import glob
import os
import subprocess
from collections import defaultdict
from datetime import datetime


def find_unimported_modules():
    """Strategy 1: Find Python files never imported anywhere."""
    print('\n' + '='*80)
    print('📋 STRATEGY 1: Import Analysis (Python Modules)')
    print('='*80)
    
    # Collect all Python files
    python_files = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.archive', 'venv', '.venv', 'node_modules'}]
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f'📊 Analyzing {len(python_files)} Python files...')
    
    # Skip entry points and special files
    skip_files = {'__init__.py', 'conftest.py', 'run.py', 'setup.py'}
    
    # Find all imports across codebase
    imported_modules = set()
    for filepath in python_files:
        try:
            with open(filepath, 'r') as f:
                tree = ast.parse(f.read(), filepath)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_modules.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imported_modules.add(node.module)
        except Exception:
            pass
    
    # Check which files are never imported
    potentially_unused = []
    for filepath in python_files:
        filename = os.path.basename(filepath)
        
        # Skip special files
        if filename in skip_files:
            continue
        
        # Skip test files (run by pytest, not imported)
        if filename.startswith('test_') or filepath.startswith('./tests/'):
            continue
        
        # Convert path to module name
        module_path = filepath[2:].replace('/', '.').replace('.py', '')
        
        # Check if this module appears in any imports
        is_imported = any(module_path.startswith(imp) or imp.startswith(module_path) 
                          for imp in imported_modules)
        
        if not is_imported:
            potentially_unused.append(filepath)
    
    print(f'\n👻 Potentially unused (never imported): {len(potentially_unused)} files')
    print('⚠️  Note: Scripts in scripts/ are run directly, not imported')
    
    for file in potentially_unused[:20]:  # Show first 20
        print(f'  ❌ {file}')
    
    if len(potentially_unused) > 20:
        print(f'  ... and {len(potentially_unused) - 20} more')
    
    return potentially_unused


def find_unreferenced_files(files_to_check):
    """Strategy 2: Use grep to find files with zero references."""
    print('\n' + '='*80)
    print('🔍 STRATEGY 2: Reference Scanning (Grep Analysis)')
    print('='*80)
    
    unreferenced = []
    
    print(f'📊 Checking {len(files_to_check)} files for references...')
    
    for filepath in files_to_check:
        filename = os.path.basename(filepath)
        module_name = filename.replace('.py', '')
        
        # Search for references
        result = subprocess.run(
            ['grep', '-r', '--include=*.py', '--include=*.yaml', '--include=*.md', 
             '-l', module_name, '.'],
            capture_output=True,
            text=True
        )
        
        # Count references (excluding the file itself)
        references = [line for line in result.stdout.split('\n') 
                      if line and line != f'./{filepath}']
        
        if len(references) == 0:
            unreferenced.append(filepath)
            print(f'  ❌ ZERO REFERENCES: {filepath}')
        else:
            print(f'  ✅ {len(references)} references: {filepath}')
    
    print(f'\n📊 Unreferenced files: {len(unreferenced)}')
    return unreferenced


def analyze_script_usage():
    """Strategy 3: Analyze scripts for execution patterns."""
    print('\n' + '='*80)
    print('🔧 STRATEGY 3: Script Execution Analysis')
    print('='*80)
    
    scripts_dir = 'scripts/'
    script_info = []
    
    for root, dirs, files in os.walk(scripts_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                with open(filepath, 'r') as f:
                    content = f.read()
                
                # Check for executable patterns
                has_main = '__name__' in content and '__main__' in content
                has_shebang = content.startswith('#!')
                has_argparse = 'argparse' in content
                
                script_info.append({
                    'path': filepath,
                    'executable': has_main or has_shebang,
                    'cli_interface': has_argparse,
                })
    
    print(f'📊 Found {len(script_info)} scripts')
    
    executable_count = sum(1 for s in script_info if s['executable'])
    cli_count = sum(1 for s in script_info if s['cli_interface'])
    
    print(f'  ✅ {executable_count} have __main__ blocks (executable)')
    print(f'  ✅ {cli_count} have CLI interfaces (argparse)')
    
    non_executable = [s for s in script_info if not s['executable']]
    if non_executable:
        print(f'\n  ⚠️  {len(non_executable)} scripts without __main__ blocks:')
        for s in non_executable[:10]:
            print(f'    {s["path"]}')
    
    return script_info


def find_suspicious_large_files():
    """Strategy 4: Find large files with few references."""
    print('\n' + '='*80)
    print('📏 STRATEGY 4: Size & Complexity Analysis')
    print('='*80)
    
    suspicious = []
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.archive', 'venv', '.venv'}]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                # Get file stats
                stats = os.stat(filepath)
                size = stats.st_size
                mod_time = datetime.fromtimestamp(stats.st_mtime)
                age_days = (datetime.now() - mod_time).days
                
                # Count lines
                with open(filepath, 'r') as f:
                    lines = sum(1 for _ in f)
                
                # Large, old, potentially unused
                if lines > 500 and age_days > 90:
                    suspicious.append({
                        'path': filepath,
                        'lines': lines,
                        'size_kb': size / 1024,
                        'age_days': age_days,
                    })
    
    suspicious = sorted(suspicious, key=lambda x: x['lines'], reverse=True)
    
    print(f'📊 Found {len(suspicious)} large files (>500 lines, >90 days old)')
    
    for file in suspicious[:10]:
        print(f'  ⚠️  {file["path"]}: {file["lines"]} lines, {file["age_days"]} days old, {file["size_kb"]:.1f} KB')
    
    return suspicious


def cleanup_dated_backups(dry_run=True):
    """Strategy 5: Archive old backup files, keeping N most recent."""
    print('\n' + '='*80)
    print('📁 STRATEGY 5: Date-Based Backup Cleanup')
    print('='*80)
    
    backup_patterns = {
        'data/Materials.backup_*.yaml': 10,
        'data/Categories.backup_*.yaml': 5,
        'audit_reports/*.txt': 20,
    }
    
    total_archived = 0
    total_space_saved = 0
    
    for pattern, keep_count in backup_patterns.items():
        files = sorted(glob.glob(pattern))
        
        if len(files) <= keep_count:
            print(f'\n✅ {pattern}: {len(files)} files (keeping all)')
            continue
        
        files_to_archive = files[:-keep_count]
        
        print(f'\n📊 {pattern}:')
        print(f'  Total: {len(files)} files')
        print(f'  Will keep: {keep_count} most recent')
        print(f'  Will archive: {len(files_to_archive)} files')
        
        # Calculate space
        space = sum(os.path.getsize(f) for f in files_to_archive)
        space_mb = space / (1024 * 1024)
        total_space_saved += space_mb
        
        print(f'  Space to organize: {space_mb:.1f} MB')
        
        if not dry_run:
            # Create archive directory
            timestamp = datetime.now().strftime('%Y%m%d')
            base_name = os.path.basename(pattern).replace('*', 'backups')
            archive_path = f'.archive/{base_name}_{timestamp}'
            os.makedirs(archive_path, exist_ok=True)
            
            # Move files
            for f in files_to_archive:
                dest = os.path.join(archive_path, os.path.basename(f))
                os.rename(f, dest)
            
            print(f'  ✅ Archived to {archive_path}/')
            total_archived += len(files_to_archive)
        else:
            print('  ⚠️  DRY RUN - use --auto-archive to execute')
    
    print(f'\n📊 TOTAL: {total_archived} files, {total_space_saved:.1f} MB')
    
    return total_archived, total_space_saved


def build_dependency_graph():
    """Strategy 6: Find isolated modules with no dependents."""
    print('\n' + '='*80)
    print('🕸️  STRATEGY 6: Dependency Graph Analysis')
    print('='*80)
    
    dependencies = defaultdict(set)  # module -> set of modules it imports
    dependents = defaultdict(set)     # module -> set of modules that import it
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.archive', 'venv', '.venv'}]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                module_name = filepath[2:].replace('/', '.').replace('.py', '')
                
                try:
                    with open(filepath, 'r') as f:
                        tree = ast.parse(f.read(), filepath)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ImportFrom) and node.module:
                            imported = node.module
                            dependencies[module_name].add(imported)
                            dependents[imported].add(module_name)
                except Exception:
                    pass
    
    # Find isolated modules (no dependents)
    isolated = []
    for module in dependencies.keys():
        if module not in dependents or len(dependents[module]) == 0:
            # Skip expected isolated modules
            if (module.startswith('tests.') or 
                module.startswith('scripts.') or 
                module == 'run' or
                module == 'setup'):
                continue
            isolated.append(module)
    
    print(f'📊 Analyzed {len(dependencies)} modules')
    print(f'👻 Found {len(isolated)} isolated modules (no dependents)')
    
    for module in isolated[:20]:
        print(f'  ❌ {module}')
    
    if len(isolated) > 20:
        print(f'  ... and {len(isolated) - 20} more')
    
    return isolated


def main():
    parser = argparse.ArgumentParser(
        description='Comprehensive unused file detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all strategies
  python3 scripts/tools/find_unused_files.py --strategy all
  
  # Just find unimported modules
  python3 scripts/tools/find_unused_files.py --strategy imports
  
  # Check for old backups and archive them
  python3 scripts/tools/find_unused_files.py --strategy backups --auto-archive
  
  # Find isolated modules
  python3 scripts/tools/find_unused_files.py --strategy graph
        """
    )
    
    parser.add_argument(
        '--strategy',
        choices=['imports', 'references', 'execution', 'size', 'backups', 'graph', 'all'],
        default='all',
        help='Detection strategy to use'
    )
    
    parser.add_argument(
        '--auto-archive',
        action='store_true',
        help='Automatically archive old backup files (only for --strategy backups)'
    )
    
    parser.add_argument(
        '--verify',
        nargs='+',
        metavar='FILE',
        help='Verify specific files with grep'
    )
    
    args = parser.parse_args()
    
    print('='*80)
    print('🔍 COMPREHENSIVE UNUSED FILE DETECTION')
    print('='*80)
    print(f'Strategy: {args.strategy}')
    print(f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    results = {}
    
    # Run selected strategies
    if args.strategy in ['imports', 'all']:
        results['unimported'] = find_unimported_modules()
    
    if args.strategy == 'references' or args.verify:
        files_to_check = args.verify if args.verify else results.get('unimported', [])
        if files_to_check:
            results['unreferenced'] = find_unreferenced_files(files_to_check)
    
    if args.strategy in ['execution', 'all']:
        results['scripts'] = analyze_script_usage()
    
    if args.strategy in ['size', 'all']:
        results['large_files'] = find_suspicious_large_files()
    
    if args.strategy in ['backups', 'all']:
        dry_run = not args.auto_archive
        results['backups'] = cleanup_dated_backups(dry_run=dry_run)
    
    if args.strategy in ['graph', 'all']:
        results['isolated'] = build_dependency_graph()
    
    # Summary
    print('\n' + '='*80)
    print('📊 SUMMARY')
    print('='*80)
    
    if 'unimported' in results:
        print(f'Unimported modules: {len(results["unimported"])}')
    
    if 'unreferenced' in results:
        print(f'Unreferenced files: {len(results["unreferenced"])}')
    
    if 'scripts' in results:
        print(f'Scripts analyzed: {len(results["scripts"])}')
    
    if 'large_files' in results:
        print(f'Large old files: {len(results["large_files"])}')
    
    if 'backups' in results:
        archived, space_mb = results['backups']
        print(f'Backups to archive: {archived} files ({space_mb:.1f} MB)')
    
    if 'isolated' in results:
        print(f'Isolated modules: {len(results["isolated"])}')
    
    print('\n✅ Analysis complete')
    print('='*80)


if __name__ == '__main__':
    main()
