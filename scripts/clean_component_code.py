"""
Script to clean up redundant or duplicated code in components.
"""

import os
import re
import ast
import argparse
from typing import List, Dict, Any, Set

def find_python_files(directory: str) -> List[str]:
    """Find all Python files in the given directory."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files

def remove_unused_imports(file_path: str, dry_run: bool = True) -> bool:
    """Remove unused imports from a Python file."""
    with open(file_path, "r") as f:
        content = f.read()
    
    # Parse the Python file
    try:
        tree = ast.parse(content)
    except SyntaxError:
        print(f"Syntax error in {file_path}, skipping...")
        return False
    
    # Find all imports
    imports = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports[name.asname or name.name] = (node, name)
        elif isinstance(node, ast.ImportFrom):
            for name in node.names:
                imports[name.asname or name.name] = (node, name)
    
    # Find all used names
    used_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            used_names.add(node.id)
        elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Load):
            if isinstance(node.value, ast.Name):
                used_names.add(node.value.id)
    
    # Find unused imports
    unused_imports = {}
    for name, (node, import_name) in imports.items():
        if name not in used_names and not import_name.name.startswith("__"):
            if node not in unused_imports:
                unused_imports[node] = []
            unused_imports[node].append(import_name.name)
    
    if not unused_imports:
        return False
    
    # Report or remove unused imports
    print(f"\nIn {file_path}:")
    
    lines = content.split("\n")
    
    # Sort nodes by line number (descending) to avoid line number shifting
    for node in sorted(unused_imports.keys(), key=lambda n: n.lineno, reverse=True):
        if isinstance(node, ast.Import):
            names = [n.name for n in node.names]
            unused = unused_imports[node]
            if set(names) == set(unused):
                # Remove the entire import statement
                print(f"  Removing: import {', '.join(names)}")
                if not dry_run:
                    lines.pop(node.lineno - 1)
            else:
                # Remove only unused names from import
                remaining = [n for n in names if n not in unused]
                print(f"  Changing: import {', '.join(names)} -> import {', '.join(remaining)}")
                if not dry_run:
                    lines[node.lineno - 1] = f"import {', '.join(remaining)}"
        
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = [n.name for n in node.names]
            unused = unused_imports[node]
            if set(names) == set(unused):
                # Remove the entire import statement
                print(f"  Removing: from {module} import {', '.join(names)}")
                if not dry_run:
                    lines.pop(node.lineno - 1)
            else:
                # Remove only unused names from import
                remaining = [n for n in names if n not in unused]
                print(f"  Changing: from {module} import {', '.join(names)} -> from {module} import {', '.join(remaining)}")
                if not dry_run:
                    lines[node.lineno - 1] = f"from {module} import {', '.join(remaining)}"
    
    if not dry_run:
        # Write back to file
        with open(file_path, "w") as f:
            f.write("\n".join(lines))
        print(f"  Updated {file_path}")
    
    return True

def find_redundant_component_code(file_paths: List[str], dry_run: bool = True) -> None:
    """Find and suggest fixes for redundant component code."""
    base_component_path = None
    component_files = []
    
    # Separate BaseComponent from other component files
    for file_path in file_paths:
        with open(file_path, "r") as f:
            content = f.read()
        
        if "class BaseComponent" in content:
            base_component_path = file_path
        elif "BaseComponent" in content:
            component_files.append(file_path)
    
    if not base_component_path:
        print("BaseComponent not found, skipping redundant code check...")
        return
    
    # Load BaseComponent methods
    with open(base_component_path, "r") as f:
        base_content = f.read()
    
    # Extract method names and signatures from BaseComponent
    base_methods = {}
    method_pattern = r"def\s+(\w+)\s*\(([^)]*)\):"
    for match in re.finditer(method_pattern, base_content):
        method_name = match.group(1)
        params = match.group(2).strip()
        base_methods[method_name] = params
    
    # Look for reimplemented methods in components
    for file_path in component_files:
        with open(file_path, "r") as f:
            content = f.read()
        
        # Find all method definitions
        redundant_methods = []
        for method_name, params in base_methods.items():
            if method_name.startswith("_") and f"def {method_name}" in content:
                # Check if the method has similar signature
                method_pattern = fr"def\s+{method_name}\s*\(([^)]*)\):"
                match = re.search(method_pattern, content)
                if match:
                    redundant_methods.append(method_name)
        
        if redundant_methods:
            print(f"\nIn {file_path}:")
            print(f"  Potentially redundant methods that could use BaseComponent:")
            for method in redundant_methods:
                print(f"    - {method}")

def remove_unused_methods(file_path: str, dry_run: bool = True) -> bool:
    """Find and remove methods that are never called."""
    with open(file_path, "r") as f:
        content = f.read()
    
    # Parse the Python file
    try:
        tree = ast.parse(content)
    except SyntaxError:
        print(f"Syntax error in {file_path}, skipping...")
        return False
    
    # Find all method definitions
    method_defs = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if not node.name.startswith("__"):  # Skip dunder methods
                method_defs[node.name] = node
    
    # Find all method calls
    method_calls = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                if node.func.value.id == "self":
                    method_calls.add(node.func.attr)
            elif isinstance(node.func, ast.Name):
                method_calls.add(node.func.id)
    
    # Find unused methods (excluding methods starting with test_ which might be tests)
    unused_methods = {}
    for name, node in method_defs.items():
        if name not in method_calls and not name.startswith("test_"):
            # Skip standard component methods that might be called externally
            if name in ("generate", "_prepare_data", "_format_prompt", "_call_api", "_post_process"):
                continue
            unused_methods[name] = node
    
    if not unused_methods:
        return False
    
    # Report or remove unused methods
    print(f"\nIn {file_path}:")
    print("  Potentially unused methods:")
    
    for name, node in unused_methods.items():
        print(f"    - {name}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Clean up component code")
    parser.add_argument("--dir", default="components", help="Directory to scan")
    parser.add_argument("--fix", action="store_true", help="Apply fixes (default is dry run)")
    args = parser.parse_args()
    
    python_files = find_python_files(args.dir)
    
    # Remove unused imports
    print("=== Checking for unused imports ===")
    fixed_imports = 0
    for file_path in python_files:
        if remove_unused_imports(file_path, dry_run=not args.fix):
            fixed_imports += 1
    
    print(f"\nFound issues in {fixed_imports} files")
    
    # Find redundant component code
    print("\n=== Checking for redundant component code ===")
    find_redundant_component_code(python_files, dry_run=not args.fix)
    
    # Find unused methods
    print("\n=== Checking for unused methods ===")
    unused_methods_count = 0
    for file_path in python_files:
        if remove_unused_methods(file_path, dry_run=not args.fix):
            unused_methods_count += 1
    
    print(f"\nFound issues in {unused_methods_count} files")

if __name__ == "__main__":
    main()