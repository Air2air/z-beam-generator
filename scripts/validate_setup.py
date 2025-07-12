#!/usr/bin/env python3
"""Validation script to check Z-Beam Generator setup."""

import os
import json
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

def validate_environment():
    """Validate environment variables."""
    console.print("🔍 Checking environment variables...", style="yellow")
    
    required_vars = ["XAI_API_KEY", "GEMINI_API_KEY", "DEEPSEEK_API_KEY", "OPENAI_API_KEY"]
    found_vars = []
    
    for var in required_vars:
        if os.getenv(var):
            found_vars.append(var)
    
    if found_vars:
        console.print(f"✅ Found API keys: {', '.join(found_vars)}", style="green")
        return True
    else:
        console.print("❌ No API keys found in environment", style="red")
        return False

def validate_schemas():
    """Validate schema files."""
    console.print("🔍 Checking schema files...", style="yellow")
    
    schema_dir = Path("schemas/definitions")
    if not schema_dir.exists():
        console.print("❌ Schema directory not found", style="red")
        return False
    
    expected_schemas = [
        "application_schema_definition.json",
        "material_schema_definition.json", 
        "region_schema_definition.json",
        "thesaurus_schema_definition.json"
    ]
    
    valid_schemas = []
    invalid_schemas = []
    
    for schema_file in expected_schemas:
        schema_path = schema_dir / schema_file
        if schema_path.exists():
            try:
                with open(schema_path, 'r') as f:
                    json.load(f)
                valid_schemas.append(schema_file)
            except json.JSONDecodeError:
                invalid_schemas.append(f"{schema_file} (invalid JSON)")
        else:
            invalid_schemas.append(f"{schema_file} (missing)")
    
    if valid_schemas:
        console.print(f"✅ Valid schemas: {len(valid_schemas)}", style="green")
    
    if invalid_schemas:
        console.print(f"❌ Invalid schemas: {', '.join(invalid_schemas)}", style="red")
        return False
    
    return True

def validate_directories():
    """Validate required directories."""
    console.print("🔍 Checking directories...", style="yellow")
    
    required_dirs = ["output", "authors", "schemas", "metadata", "tags", "jsonld", "utils"]
    missing_dirs = []
    
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        console.print(f"❌ Missing directories: {', '.join(missing_dirs)}", style="red")
        return False
    
    console.print("✅ All required directories found", style="green")
    return True

def main():
    """Run all validation checks."""
    console.print("🚀 Z-Beam Generator Setup Validation", style="bold blue")
    console.print("=" * 50)
    
    checks = [
        ("Environment Variables", validate_environment),
        ("Schema Files", validate_schemas),
        ("Directory Structure", validate_directories)
    ]
    
    results = []
    for check_name, check_func in checks:
        result = check_func()
        results.append((check_name, result))
        console.print()
    
    # Summary table
    table = Table(title="Validation Summary")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="magenta")
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        table.add_row(check_name, status)
    
    console.print(table)
    
    if all(result for _, result in results):
        console.print("\n🎉 All checks passed! Your setup is ready.", style="bold green")
        return 0
    else:
        console.print("\n⚠️  Some checks failed. Please fix the issues above.", style="bold red")
        return 1

if __name__ == "__main__":
    sys.exit(main())