#!/usr/bin/env python3
"""
Batch Caption Generation Script
=====================================

Processes all materials requiring caption generation with:
- Progress tracking and time estimates
- Error handling and retry logic  
- Performance metrics and reporting
- Clean workspace management

Usage:
    python3 scripts/batch_generate_all_captions.py [--dry-run] [--continue-from MATERIAL]
"""

import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class BatchCaptionProcessor:
    """Comprehensive batch processor for caption generation"""
    
    def __init__(self, dry_run: bool = False, continue_from: Optional[str] = None):
        self.dry_run = dry_run
        self.continue_from = continue_from
        self.project_root = Path(__file__).parent.parent
        self.stats = {
            'total_materials': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'total_time': 0,
            'average_time': 0,
            'start_time': None,
            'materials_processed': [],
            'errors': []
        }
        
    def get_materials_needing_captions(self) -> List[str]:
        """Extract materials needing captions from validation output"""
        print("🔍 Analyzing materials that need caption generation...")
        
        try:
            # Run validation to get current status
            result = subprocess.run([
                'python3', 'validation/caption_integration_validator.py'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            # Parse the validation output to extract material names
            materials = []
            in_error_section = False
            
            for line in result.stdout.split('\n'):
                if '❌ Files with errors:' in line:
                    in_error_section = True
                    continue
                    
                if in_error_section and line.strip().startswith('•'):
                    # Extract material name from error line
                    # Format: "  • Material Name: 1 errors"
                    material_part = line.split(':', 1)[0].strip('• ')
                    
                    # Skip file paths, keep only material names
                    if not material_part.startswith('content/components/frontmatter/'):
                        materials.append(material_part)
                    else:
                        # Extract material from file path
                        file_path = material_part
                        if 'laser-cleaning.yaml' in file_path:
                            material_name = file_path.split('/')[-1].replace('-laser-cleaning.yaml', '').replace('-', ' ').title()
                            materials.append(material_name)
                
                if '📋 Total errors:' in line:
                    break
                    
            # Remove duplicates and sort
            materials = sorted(list(set(materials)))
            
            print(f"📊 Found {len(materials)} materials needing caption generation")
            return materials
            
        except Exception as e:
            print(f"❌ Error getting materials list: {e}")
            return []
    
    def estimate_completion_time(self, materials: List[str], avg_time: float = 15.9) -> str:
        """Calculate estimated completion time"""
        total_seconds = len(materials) * avg_time
        completion_time = datetime.now() + timedelta(seconds=total_seconds)
        
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        
        time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        return f"{time_str} (estimated completion: {completion_time.strftime('%H:%M')})"
    
    def process_material(self, material: str) -> Dict[str, Any]:
        """Process a single material with error handling"""
        start_time = time.time()
        
        try:
            print(f"\n🎯 Processing: {material}")
            
            if self.dry_run:
                print(f"   [DRY RUN] Would generate caption for {material}")
                time.sleep(0.1)  # Simulate processing time
                return {
                    'material': material,
                    'success': True,
                    'time': 0.1,
                    'dry_run': True
                }
            
            # Run the caption generation
            result = subprocess.run([
                'python3', 'scripts/generate_caption_to_frontmatter.py',
                '--material', material
            ], cwd=self.project_root, capture_output=True, text=True)
            
            processing_time = time.time() - start_time
            
            if result.returncode == 0:
                print(f"   ✅ Success in {processing_time:.2f}s")
                return {
                    'material': material,
                    'success': True,
                    'time': processing_time,
                    'output': result.stdout
                }
            else:
                print(f"   ❌ Failed: {result.stderr}")
                return {
                    'material': material,
                    'success': False,
                    'time': processing_time,
                    'error': result.stderr,
                    'output': result.stdout
                }
                
        except Exception as e:
            processing_time = time.time() - start_time
            print(f"   ❌ Exception: {e}")
            return {
                'material': material,
                'success': False,
                'time': processing_time,
                'error': str(e)
            }
    
    def update_progress(self, current: int, total: int, material: str, time_taken: float):
        """Display progress with time estimates"""
        percentage = (current / total) * 100
        
        # Update running average
        if self.stats['processed'] > 0:
            self.stats['average_time'] = self.stats['total_time'] / self.stats['processed']
        
        remaining = total - current
        estimated_remaining_time = remaining * self.stats['average_time']
        
        hours = int(estimated_remaining_time // 3600)
        minutes = int((estimated_remaining_time % 3600) // 60)
        
        eta_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        
        print(f"📈 Progress: {current}/{total} ({percentage:.1f}%) | "
              f"Avg: {self.stats['average_time']:.1f}s | "
              f"ETA: {eta_str}")
    
    def save_progress_report(self):
        """Save detailed progress report"""
        report_path = self.project_root / 'logs' / f'batch_caption_generation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(self.stats, f, indent=2, default=str)
        
        print(f"📄 Progress report saved: {report_path}")
    
    def run(self):
        """Execute the batch processing"""
        print("🚀 Starting Batch Caption Generation")
        print("=" * 50)
        
        self.stats['start_time'] = datetime.now()
        
        # Get materials list
        materials = self.get_materials_needing_captions()
        
        if not materials:
            print("✅ No materials need caption generation!")
            return
        
        # Handle continue_from option
        if self.continue_from:
            try:
                start_index = materials.index(self.continue_from)
                materials = materials[start_index:]
                print(f"🔄 Continuing from: {self.continue_from}")
            except ValueError:
                print(f"⚠️  Material '{self.continue_from}' not found, processing all")
        
        self.stats['total_materials'] = len(materials)
        
        # Show initial estimate
        estimate = self.estimate_completion_time(materials)
        print(f"⏱️  Estimated processing time: {estimate}")
        
        if self.dry_run:
            print("🧪 DRY RUN MODE - No actual processing will occur")
        
        print(f"\n📋 Processing {len(materials)} materials...")
        
        # Process each material
        for i, material in enumerate(materials, 1):
            result = self.process_material(material)
            
            # Update statistics
            self.stats['processed'] += 1
            self.stats['total_time'] += result['time']
            self.stats['materials_processed'].append(result)
            
            if result['success']:
                self.stats['successful'] += 1
            else:
                self.stats['failed'] += 1
                self.stats['errors'].append({
                    'material': material,
                    'error': result.get('error', 'Unknown error')
                })
            
            # Show progress
            self.update_progress(i, len(materials), material, result['time'])
            
            # Small delay to prevent API rate limiting
            if not self.dry_run and i < len(materials):
                time.sleep(1)
        
        # Final report
        self.print_final_report()
        self.save_progress_report()
    
    def print_final_report(self):
        """Print comprehensive final report"""
        total_time = time.time() - self.stats['start_time'].timestamp()
        
        print("\n" + "=" * 50)
        print("📊 BATCH PROCESSING COMPLETE")
        print("=" * 50)
        print(f"📈 Total Materials: {self.stats['total_materials']}")
        print(f"✅ Successful: {self.stats['successful']}")
        print(f"❌ Failed: {self.stats['failed']}")
        print(f"⏱️  Total Time: {total_time/60:.1f} minutes")
        print(f"⚡ Average Time: {self.stats['average_time']:.1f}s per material")
        
        if self.stats['failed'] > 0:
            print("\n❌ Failed Materials:")
            for error in self.stats['errors']:
                print(f"   • {error['material']}: {error['error'][:100]}...")
        
        success_rate = (self.stats['successful'] / self.stats['total_materials']) * 100
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")


def main():
    parser = argparse.ArgumentParser(description='Batch generate captions for all materials')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be processed without actual generation')
    parser.add_argument('--continue-from', type=str,
                       help='Continue processing from a specific material')
    
    args = parser.parse_args()
    
    processor = BatchCaptionProcessor(
        dry_run=args.dry_run,
        continue_from=args.continue_from
    )
    
    try:
        processor.run()
    except KeyboardInterrupt:
        print("\n⏹️  Processing interrupted by user")
        processor.save_progress_report()
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        processor.save_progress_report()
        sys.exit(1)


if __name__ == '__main__':
    main()