#!/usr/bin/env python3
"""
Batch Frontmatter Regeneration Script with Progress Tracking

Features:
- Progress tracking with ETA
- Resume capability (skip already-completed)
- Error handling with detailed logging
- Optional parallel execution
- Pre-flight validation
- Post-batch verification
"""

import subprocess
import time
import yaml
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import sys
import os

class BatchRegenerator:
    def __init__(self, output_dir: str = "content/components/frontmatter", resume: bool = True):
        self.output_dir = Path(output_dir)
        self.resume = resume
        self.log_file = Path(f"logs/batch_regen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.stats = {
            "total": 0,
            "completed": 0,
            "skipped": 0,
            "failed": 0,
            "start_time": None,
            "end_time": None
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Log message to both console and file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}"
        print(log_line)
        with open(self.log_file, 'a') as f:
            f.write(log_line + "\n")
    
    def get_all_materials(self) -> List[str]:
        """Get list of all materials from materials.yaml."""
        materials_file = Path("data/materials.yaml")
        with open(materials_file, 'r') as f:
            data = yaml.safe_load(f)
        
        materials = list(data.get('materials', {}).keys())
        materials.sort()  # Alphabetical order
        return materials
    
    def check_material_status(self, material_name: str) -> Dict[str, bool]:
        """Check if material has new format (camelCase caption + tags)."""
        filename = f"{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml"
        filepath = self.output_dir / filename
        
        if not filepath.exists():
            return {"exists": False, "new_format": False, "has_tags": False}
        
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            
            has_camelcase = 'caption' in data and 'beforeText' in data['caption']
            has_tags = 'tags' in data and isinstance(data['tags'], list) and len(data['tags']) >= 4
            has_string_apps = (
                'applications' in data and 
                isinstance(data['applications'], list) and
                len(data['applications']) > 0 and
                isinstance(data['applications'][0], str)
            )
            
            new_format = has_camelcase and has_tags and has_string_apps
            
            return {
                "exists": True,
                "new_format": new_format,
                "has_tags": has_tags,
                "has_camelcase": has_camelcase,
                "has_string_apps": has_string_apps
            }
        except Exception as e:
            self.log(f"Error checking {material_name}: {e}", "WARNING")
            return {"exists": True, "new_format": False, "has_tags": False}
    
    def generate_material(self, material_name: str, timeout: int = 300) -> Tuple[bool, str]:
        """Generate frontmatter for a single material."""
        try:
            self.log(f"Generating {material_name}...", "INFO")
            
            cmd = [
                "python3", "run.py",
                "--material", material_name,
                "--components", "frontmatter"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Path.cwd()
            )
            
            if result.returncode == 0:
                # Check if file was actually created
                status = self.check_material_status(material_name)
                if status['exists']:
                    return True, "Success"
                else:
                    return False, "File not created despite success code"
            else:
                error_msg = result.stderr[-500:] if result.stderr else "Unknown error"
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            return False, f"Timeout after {timeout}s"
        except Exception as e:
            return False, str(e)
    
    def estimate_time_remaining(self, completed: int, total: int, elapsed_seconds: float) -> str:
        """Estimate time remaining based on average time per material."""
        if completed == 0:
            return "calculating..."
        
        avg_time = elapsed_seconds / completed
        remaining = total - completed
        remaining_seconds = avg_time * remaining
        
        return str(timedelta(seconds=int(remaining_seconds)))
    
    def run_batch(self, materials: Optional[List[str]] = None, timeout: int = 300):
        """Run batch regeneration."""
        if materials is None:
            materials = self.get_all_materials()
        
        self.stats['total'] = len(materials)
        self.stats['start_time'] = datetime.now()
        
        self.log("="*70)
        self.log("BATCH FRONTMATTER REGENERATION")
        self.log("="*70)
        self.log(f"Total materials: {self.stats['total']}")
        self.log(f"Resume mode: {self.resume}")
        self.log(f"Timeout per material: {timeout}s")
        self.log(f"Log file: {self.log_file}")
        self.log("")
        
        # Pre-flight check
        if self.resume:
            self.log("Checking existing materials...", "INFO")
            needs_regen = []
            for material in materials:
                status = self.check_material_status(material)
                if not status['new_format']:
                    needs_regen.append(material)
                else:
                    self.stats['skipped'] += 1
            
            self.log(f"Found {len(needs_regen)} materials needing regeneration", "INFO")
            self.log(f"Skipping {self.stats['skipped']} already up-to-date materials", "INFO")
            self.log("")
            materials = needs_regen
        
        if not materials:
            self.log("✅ All materials already up to date!", "SUCCESS")
            return
        
        # Process each material
        for idx, material in enumerate(materials, 1):
            progress = f"[{idx}/{len(materials)}]"
            elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
            eta = self.estimate_time_remaining(self.stats['completed'], len(materials), elapsed)
            
            self.log("-" * 70)
            self.log(f"{progress} Processing: {material} (ETA: {eta})", "INFO")
            
            success, message = self.generate_material(material, timeout)
            
            if success:
                self.stats['completed'] += 1
                self.log(f"✅ {material} completed successfully", "SUCCESS")
                
                # Verify format
                status = self.check_material_status(material)
                if not status['new_format']:
                    self.log(f"⚠️  {material} generated but not in new format", "WARNING")
            else:
                self.stats['failed'] += 1
                self.log(f"❌ {material} failed: {message}", "ERROR")
        
        self.stats['end_time'] = datetime.now()
        self.print_summary()
    
    def print_summary(self):
        """Print final summary."""
        duration = self.stats['end_time'] - self.stats['start_time']
        
        self.log("")
        self.log("="*70)
        self.log("BATCH REGENERATION COMPLETE")
        self.log("="*70)
        self.log(f"Total materials: {self.stats['total']}")
        self.log(f"✅ Completed: {self.stats['completed']}")
        self.log(f"⏭️  Skipped: {self.stats['skipped']}")
        self.log(f"❌ Failed: {self.stats['failed']}")
        self.log(f"⏱️  Duration: {duration}")
        self.log(f"📊 Average time: {duration.total_seconds() / max(self.stats['completed'], 1):.1f}s per material")
        self.log("")
        self.log(f"📝 Full log: {self.log_file}")
        
        if self.stats['failed'] > 0:
            self.log("")
            self.log("❌ Some materials failed. Check log for details.", "WARNING")
            self.log("💡 To retry failed materials, run with --resume flag", "INFO")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Batch regenerate frontmatter for all materials',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--no-resume',
        action='store_true',
        help='Regenerate all materials (ignore existing files)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=300,
        help='Timeout per material in seconds (default: 300)'
    )
    parser.add_argument(
        '--materials',
        nargs='+',
        help='Specific materials to regenerate (default: all)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually doing it'
    )
    
    args = parser.parse_args()
    
    regenerator = BatchRegenerator(resume=not args.no_resume)
    
    if args.dry_run:
        materials = args.materials if args.materials else regenerator.get_all_materials()
        print(f"Would process {len(materials)} materials:")
        for material in materials[:10]:
            status = regenerator.check_material_status(material)
            status_str = "✅ up-to-date" if status['new_format'] else "⚠️ needs regen"
            print(f"  - {material}: {status_str}")
        if len(materials) > 10:
            print(f"  ... and {len(materials) - 10} more")
        sys.exit(0)
    
    try:
        regenerator.run_batch(materials=args.materials, timeout=args.timeout)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print(f"Progress saved. Run again with --resume to continue.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
