#!/usr/bin/env python3
"""
Z-Beam content generation system - SIMPLIFIED CONTROL

Two main operations for streamlined workflow:

USAGE:
    python3 run.py                          # Interactive generation with automatic validation
    python3 run.py --start-from "Copper"    # Start interactive mode from specific material
    python3 run.py --yaml                   # Validate and fix YAML errors across all files

INTERACTIVE GENERATION MODE:
- Step-by-step material processing with user prompts
- Automatic post-processing and validation after each component
- Real-time progress tracking and error detection
- Skip, pause, and resume capabilities
- Comprehensive error handling and recovery
- Session summaries and statistics

YAML VALIDATION MODE:
- Scans all component files for YAML formatting errors
- Automatically fixes common issues (multiple delimiters, empty objects)
- Provides detailed validation report
- Safe operation with backup-friendly processing
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_yaml_validation():
    """Run comprehensive YAML validation and fixing across all files."""
    script_dir = Path(__file__).parent
    
    print("🔍 YAML VALIDATION & FIXING MODE")
    print("=" * 50)
    print("Scanning all component files for YAML errors...")
    print("Automatically fixing common formatting issues...")
    print("=" * 50)
    
    # Use the correct post-processing method signature
    cmd = [sys.executable, "-c", """
from validators.centralized_validator import CentralizedValidator
from pathlib import Path
import os

print("🔄 Processing all component files...")

validator = CentralizedValidator()

# Get all component files
content_dir = Path("content/components")
total_files = 0
fixed_files = 0
error_files = []

for component_dir in content_dir.iterdir():
    if not component_dir.is_dir():
        continue
        
    component_type = component_dir.name
    print(f"\\n📁 Processing {component_type}...")
    
    for md_file in component_dir.glob("*.md"):
        total_files += 1
        
        try:
            # Use the correct method signature: file_path and component_type
            was_processed = validator.post_process_generated_content(str(md_file), component_type)
            
            if was_processed:
                fixed_files += 1
                print(f"   ✅ Fixed: {md_file.name}")
            else:
                print(f"   ⚪ OK: {md_file.name}")
                
        except Exception as e:
            error_files.append(f"{md_file.name}: {str(e)}")
            print(f"   ❌ Error: {md_file.name} - {e}")

print(f"\\n📊 YAML PROCESSING COMPLETE")
print(f"=" * 50)
print(f"📁 Total files processed: {total_files}")
print(f"✅ Files fixed: {fixed_files}")
print(f"❌ Files with errors: {len(error_files)}")

if error_files:
    print(f"\\n⚠️  Error Details:")
    for error in error_files[:10]:  # Show first 10 errors
        print(f"   {error}")
    if len(error_files) > 10:
        print(f"   ... and {len(error_files) - 10} more errors")

# Run validation check on a sample
print(f"\\n🔍 POST-PROCESSING VALIDATION CHECK")
print(f"=" * 30)

sample_materials = ['Porcelain', 'Copper', 'Steel']
total_components = 0
total_valid = 0

for material in sample_materials:
    try:
        results = validator.validate_material(material)
        valid_count = sum(1 for r in results.values() if r.status.name == 'SUCCESS')
        total_components += len(results)
        total_valid += valid_count
        print(f"{material}: {valid_count}/{len(results)} ({valid_count/len(results)*100:.0f}%)")
    except Exception as e:
        print(f"{material}: Error - {e}")

if total_components > 0:
    print(f"\\n📈 Overall validation rate: {total_valid}/{total_components} ({total_valid/total_components*100:.1f}%)")

print(f"\\n🎯 YAML validation and fixing complete!")
"""]
    
    return subprocess.run(cmd, cwd=script_dir)

def main():
    """Main entry point - simplified Z-Beam operations."""
    
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    generator_script = script_dir / "z_beam_generator.py"
    
    # Check if z_beam_generator.py exists
    if not generator_script.exists():
        print(f"❌ Error: {generator_script} not found")
        print("   Make sure z_beam_generator.py is in the same directory as run.py")
        sys.exit(1)
    
    # Parse command line arguments - simplified interface
    parser = argparse.ArgumentParser(
        description="Z-Beam Simplified Control",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
SIMPLIFIED COMMANDS:
  python3 run.py                          # Interactive generation with automatic validation
  python3 run.py --start-from "Copper"    # Start from specific material
  python3 run.py --yaml                   # Validate and fix YAML errors across all files

Interactive Mode Commands:
  Y/Yes     - Continue to next material (default)
  N/No      - Pause generation  
  S/Skip    - Skip current material
  Q/Quit    - Exit with summary
  List      - Show next 10 materials
        """
    )
    
    parser.add_argument("--yaml", action="store_true", help="Validate and fix YAML errors across all files")
    parser.add_argument("--start-from", help="Start interactive generation from specific material")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Route to appropriate operation
    try:
        if args.yaml:
            # YAML validation and fixing mode
            result = run_yaml_validation()
            
        else:
            # Interactive generation mode (default)
            cmd = [sys.executable, str(generator_script), "--interactive"]
            
            if args.start_from:
                cmd.extend(["--start-from", args.start_from])
            
            if args.verbose:
                cmd.append("--verbose")
                
            print("🎮 INTERACTIVE GENERATION MODE")
            print("=" * 50)
            print("Starting interactive material generation with automatic validation...")
            print("Use Ctrl+C at any time to safely exit.")
            print("=" * 50)
            
            result = subprocess.run(cmd, cwd=script_dir)
        
        sys.exit(result.returncode)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Operation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error running operation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
