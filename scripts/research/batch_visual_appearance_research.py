#!/usr/bin/env python3
"""
Batch Visual Appearance Research with Concurrent API Calls

Optimized version that:
1. Runs multiple API calls concurrently (3-5 parallel requests)
2. Batches multiple materials into single prompts where possible
3. Saves progress incrementally to avoid losing work
4. Can resume from where it left off

Usage:
    # Research all patterns, all materials (concurrent)
    python3 scripts/research/batch_visual_appearance_research.py --all
    
    # Research specific pattern with concurrency
    python3 scripts/research/batch_visual_appearance_research.py --pattern rust-oxidation --workers 5
    
    # Resume interrupted research
    python3 scripts/research/batch_visual_appearance_research.py --resume
    
    # Dry run (show what would be researched)
    python3 scripts/research/batch_visual_appearance_research.py --all --dry-run

Author: AI Assistant
Date: November 29, 2025
"""

import argparse
import argparse
import os
import sys
import yaml
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import threading

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(project_root / '.env')

import google.generativeai as genai

# Thread-safe lock for YAML file updates
yaml_lock = threading.Lock()


class BatchVisualAppearanceResearcher:
    """
    Batch researcher with rate-limited API calls.
    
    Optimizations:
    - Rate limiting (10 requests/minute for gemini-2.0-flash-exp)
    - Incremental saves (every N materials)
    - Progress tracking and resume capability
    - Automatic retry with exponential backoff on 429 errors
    """
    
    def __init__(self, max_workers: int = 1, save_interval: int = 10, requests_per_minute: int = 10):
        """
        Initialize batch researcher.
        
        Args:
            max_workers: Number of concurrent API calls (default 1 due to rate limits)
            save_interval: Save to YAML every N materials
            requests_per_minute: API rate limit (default 10 for gemini-2.0-flash-exp)
        """
        self.max_workers = min(max_workers, 1)  # Force single worker due to rate limits
        self.save_interval = save_interval
        self.requests_per_minute = requests_per_minute
        self.min_delay = 60.0 / requests_per_minute  # Seconds between requests
        self.last_request_time = 0
        
        # Initialize Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Progress tracking
        self.completed = 0
        self.failed = 0
        self.skipped = 0
        self.total = 0
        self.start_time = None
        
        # Paths
        self.contaminants_file = project_root / 'data' / 'contaminants' / 'Contaminants.yaml'
        self.materials_file = project_root / 'data' / 'materials' / 'Materials.yaml'
        self.progress_file = project_root / 'progress' / 'visual_research_progress.json'
        
        print(f"🚀 Batch researcher initialized")
        print(f"   Workers: {self.max_workers} concurrent")
        print(f"   Save interval: every {self.save_interval} materials")
    
    def load_data(self) -> Tuple[Dict, Dict]:
        """Load contaminants and materials data."""
        with open(self.contaminants_file, 'r', encoding='utf-8') as f:
            contam_data = yaml.safe_load(f)
        
        with open(self.materials_file, 'r', encoding='utf-8') as f:
            mat_data = yaml.safe_load(f)
        
        return contam_data, mat_data
    
    def save_contaminants(self, data: Dict):
        """Thread-safe save to Contaminants.yaml."""
        with yaml_lock:
            with open(self.contaminants_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, width=120)
    
    def get_research_tasks(
        self,
        contam_data: Dict,
        mat_data: Dict,
        patterns: Optional[List[str]] = None,
        force: bool = False,
        categories_only: bool = False
    ) -> List[Tuple[str, str, str]]:
        """
        Get list of (pattern_id, pattern_name, material_name) tuples to research.
        
        Args:
            contam_data: Contaminants.yaml data
            mat_data: Materials.yaml data
            patterns: Optional list of pattern IDs to research (None = all)
            force: If True, re-research existing data
            categories_only: If True, research categories instead of materials (92% reduction)
        
        Returns:
            List of (pattern_id, pattern_name, target_name) tuples
        """
        tasks = []
        
        all_patterns = contam_data.get('contamination_patterns', {})
        
        # Filter patterns if specified
        if patterns:
            pattern_items = [(pid, all_patterns[pid]) for pid in patterns if pid in all_patterns]
        else:
            pattern_items = list(all_patterns.items())
        
        if categories_only:
            # Category-level research: 13 categories instead of 159 materials
            categories = ['metal', 'wood', 'stone', 'glass', 'ceramic', 'plastic', 
                         'composite', 'rubber', 'fabric', 'concrete', 'mineral', 
                         'semiconductor', 'specialty']
            
            for pattern_id, pattern_data in pattern_items:
                pattern_name = pattern_data.get('name', pattern_id)
                
                # Get existing researched categories
                vis = pattern_data.get('visual_characteristics', {})
                existing = set(k.lower() for k in vis.get('appearance_on_categories', {}).keys())
                
                for category in categories:
                    # Skip if already researched (unless force)
                    if not force and category.lower() in existing:
                        continue
                    
                    tasks.append((pattern_id, pattern_name, f"[CATEGORY]{category}"))
        else:
            # Material-level research: all materials
            all_materials = list(mat_data.get('materials', {}).keys())
            
            for pattern_id, pattern_data in pattern_items:
                pattern_name = pattern_data.get('name', pattern_id)
                
                # Get existing researched materials
                vis = pattern_data.get('visual_characteristics', {})
                existing = set(k.lower() for k in vis.get('appearance_on_materials', {}).keys())
                
                for material_name in all_materials:
                    # Skip if already researched (unless force)
                    if not force and material_name.lower() in existing:
                        continue
                    
                    tasks.append((pattern_id, pattern_name, material_name))
        
        return tasks
    
    def research_single(
        self,
        pattern_id: str,
        pattern_name: str,
        material_name: str
    ) -> Optional[Dict[str, str]]:
        """
        Research a single material-contaminant combination with rate limiting.
        
        Returns:
            Dict of visual characteristics, or None if failed
        """
        # Rate limiting - wait if needed
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_delay:
            sleep_time = self.min_delay - elapsed
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        
        prompt = self._build_prompt(pattern_name, material_name)
        
        # Retry with exponential backoff on 429 errors
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0.2,
                        'top_p': 0.8,
                        'top_k': 40,
                        'max_output_tokens': 2048,
                    }
                )
                
                result = self._parse_response(response.text)
                return result
                
            except Exception as e:
                error_str = str(e)
                if '429' in error_str:
                    # Rate limit hit - wait longer
                    wait_time = (attempt + 1) * 10  # 10s, 20s, 30s
                    print(f"   ⏳ Rate limit hit, waiting {wait_time}s (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(wait_time)
                    self.last_request_time = time.time()
                else:
                    print(f"   ❌ Failed: {pattern_name} on {material_name}: {e}")
                    return None
        
        print(f"   ❌ Failed after {max_retries} retries: {pattern_name} on {material_name}")
        return None
    
    def _build_prompt(self, contaminant_name: str, target_name: str) -> str:
        """Build research prompt for Gemini."""
        # Check if this is a category-level or material-level request
        if target_name.startswith("[CATEGORY]"):
            category = target_name.replace("[CATEGORY]", "")
            return f"""You are a materials science expert. Provide PRECISE visual descriptions of {contaminant_name} on {category.upper()} surfaces (e.g., {self._get_category_examples(category)}).

ACCURACY: Use specific colors (hex codes), real measurements (micrometers), and industrial/scientific accuracy.
Focus on characteristics COMMON TO ALL {category.upper()} materials, not specific to one material.

Return ONLY this JSON (no other text):

{{
  "description": "2-3 sentence overall description with dominant colors and coverage patterns typical for {category}",
  "color_variations": "3-5 specific colors from fresh to aged (e.g., '#B7410E rust-orange')",
  "texture_details": "Detailed texture - smooth/rough/crystalline/powdery/sticky/crusty",
  "common_patterns": "Distribution patterns - uniform coating, localized spots, streaks, drip marks",
  "aged_appearance": "How it changes over time - fresh (hours/days) vs aged (months/years)",
  "lighting_effects": "Appearance under different lighting - sheen, gloss, matte, iridescence",
  "thickness_range": "Typical thickness with measurements (micrometers/millimeters)",
  "distribution_patterns": "Specific distribution types on {category} surfaces",
  "uniformity_assessment": "How uniform - perfectly uniform to highly variable",
  "concentration_variations": "Where heavy vs light - edges, corners, crevices, flat surfaces",
  "typical_formations": "Physical formations - drip marks, pools, films, crusts, patches",
  "geometry_effects": "How surface geometry affects distribution",
  "gravity_influence": "How gravity affects pattern - downward flow, pooling, vertical streaking",
  "coverage_ranges": "Coverage percentages - sparse (<10%), light (10-30%), moderate (30-60%), heavy (60-85%), extreme (>85%)",
  "edge_center_behavior": "Prefers edges, center, or uniform distribution",
  "buildup_progression": "How buildup progresses over time with timeframes"
}}"""
        else:
            return f"""You are a materials science expert. Provide PRECISE visual descriptions of {contaminant_name} on {target_name} surfaces.

ACCURACY: Use specific colors (hex codes), real measurements (micrometers), and industrial/scientific accuracy.

Return ONLY this JSON (no other text):

{{
  "description": "2-3 sentence overall description with dominant colors and coverage patterns",
  "color_variations": "3-5 specific colors from fresh to aged (e.g., '#B7410E rust-orange')",
  "texture_details": "Detailed texture - smooth/rough/crystalline/powdery/sticky/crusty",
  "common_patterns": "Distribution patterns - uniform coating, localized spots, streaks, drip marks",
  "aged_appearance": "How it changes over time - fresh (hours/days) vs aged (months/years)",
  "lighting_effects": "Appearance under different lighting - sheen, gloss, matte, iridescence",
  "thickness_range": "Typical thickness with measurements (micrometers/millimeters)",
  "distribution_patterns": "Specific distribution types on {target_name}",
  "uniformity_assessment": "How uniform - perfectly uniform to highly variable",
  "concentration_variations": "Where heavy vs light - edges, corners, crevices, flat surfaces",
  "typical_formations": "Physical formations - drip marks, pools, films, crusts, patches",
  "geometry_effects": "How surface geometry affects distribution",
  "gravity_influence": "How gravity affects pattern - downward flow, pooling, vertical streaking",
  "coverage_ranges": "Coverage percentages - sparse (<10%), light (10-30%), moderate (30-60%), heavy (60-85%), extreme (>85%)",
  "edge_center_behavior": "Prefers edges, center, or uniform distribution",
  "buildup_progression": "How buildup progresses over time with timeframes"
}}"""
    
    def _get_category_examples(self, category: str) -> str:
        """Get example materials for a category."""
        examples = {
            'metal': 'steel, aluminum, copper, brass',
            'wood': 'oak, pine, plywood, MDF',
            'stone': 'granite, marble, limestone, slate',
            'glass': 'window glass, tempered glass, borosilicate',
            'ceramic': 'porcelain, tiles, terracotta',
            'plastic': 'ABS, PVC, acrylic, polycarbonate',
            'composite': 'fiberglass, carbon fiber, Corian',
            'rubber': 'natural rubber, silicone, neoprene',
            'fabric': 'cotton, polyester, nylon, canvas',
            'concrete': 'concrete, mortar, cement board',
            'mineral': 'calcium carbite, calcium oxide',
            'semiconductor': 'silicon, germanium, gallium arsenide',
            'specialty': 'graphite, carbon, magnetic materials'
        }
        return examples.get(category.lower(), 'various materials')
    
    def _parse_response(self, response_text: str) -> Dict[str, str]:
        """Parse Gemini JSON response."""
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        return json.loads(text)
    
    def run_batch(
        self,
        patterns: Optional[List[str]] = None,
        force: bool = False,
        dry_run: bool = False,
        categories_only: bool = False
    ) -> Dict[str, int]:
        """
        Run batch research with concurrent workers.
        
        Args:
            patterns: Optional list of pattern IDs (None = all patterns)
            force: Re-research existing data
            dry_run: Just show what would be researched
            categories_only: Research at category level (13 vs 159 targets)
        
        Returns:
            Dict with counts: {'completed': N, 'failed': N, 'skipped': N}
        """
        self.start_time = time.time()
        self.categories_only = categories_only
        
        # Load data
        print("\n📂 Loading data...")
        contam_data, mat_data = self.load_data()
        
        # Get tasks
        tasks = self.get_research_tasks(contam_data, mat_data, patterns, force, categories_only)
        self.total = len(tasks)
        
        print("\n📊 Research Tasks:")
        print(f"   Total: {self.total} material-contaminant combinations")
        
        if dry_run:
            # Group by pattern for display
            by_pattern = {}
            for pid, pname, mat in tasks:
                if pid not in by_pattern:
                    by_pattern[pid] = []
                by_pattern[pid].append(mat)
            
            print("\n🔍 DRY RUN - Would research:")
            for pid, mats in sorted(by_pattern.items()):
                print(f"   {pid}: {len(mats)} materials")
            
            return {'completed': 0, 'failed': 0, 'skipped': self.total}
        
        if self.total == 0:
            print("✅ Nothing to research - all combinations already complete!")
            return {'completed': 0, 'failed': 0, 'skipped': 0}
        
        # With rate limiting at 10 RPM, estimated time is total * 6 seconds
        est_minutes = (self.total * self.min_delay) / 60
        print(f"   Rate limit: {self.requests_per_minute} requests/minute")
        print(f"   Estimated time: {est_minutes:.1f} minutes (~{est_minutes/60:.1f} hours)")
        print()
        
        # Process sequentially with rate limiting
        results_buffer = {}  # pattern_id -> {material -> result}
        save_counter = 0
        
        for pid, pname, mat in tasks:
            result = self.research_single(pid, pname, mat)
            
            if result:
                # Buffer result
                if pid not in results_buffer:
                    results_buffer[pid] = {}
                results_buffer[pid][mat.lower()] = result
                
                self.completed += 1
                save_counter += 1
                
                # Progress indicator
                elapsed = time.time() - self.start_time
                rate = self.completed / elapsed if elapsed > 0 else 0
                remaining = (self.total - self.completed - self.failed) / rate if rate > 0 else 0
                
                print(f"✅ [{self.completed}/{self.total}] {pname} on {mat} "
                      f"({rate:.2f}/s, ~{remaining/60:.0f}m remaining)")
                
                # Save periodically
                if save_counter >= self.save_interval:
                    self._save_buffered_results(contam_data, results_buffer)
                    results_buffer = {}
                    save_counter = 0
            else:
                self.failed += 1
        
        # Final save
        if results_buffer:
            self._save_buffered_results(contam_data, results_buffer)
        
        # Summary
        elapsed = time.time() - self.start_time
        print(f"\n{'='*60}")
        print("📊 BATCH RESEARCH COMPLETE")
        print(f"{'='*60}")
        print(f"   Completed: {self.completed}")
        print(f"   Failed: {self.failed}")
        print(f"   Time: {elapsed/60:.1f} minutes")
        if elapsed > 0:
            print(f"   Rate: {self.completed / elapsed:.2f} materials/second")
        
        return {
            'completed': self.completed,
            'failed': self.failed,
            'skipped': self.skipped
        }
    
    def _save_buffered_results(self, contam_data: Dict, results_buffer: Dict):
        """Save buffered results to Contaminants.yaml."""
        print(f"   💾 Saving {sum(len(v) for v in results_buffer.values())} results...")
        
        for pattern_id, targets in results_buffer.items():
            if pattern_id not in contam_data['contamination_patterns']:
                continue
            
            pattern = contam_data['contamination_patterns'][pattern_id]
            
            if 'visual_characteristics' not in pattern:
                pattern['visual_characteristics'] = {}
            
            # Determine if saving to categories or materials
            if hasattr(self, 'categories_only') and self.categories_only:
                storage_key = 'appearance_on_categories'
            else:
                storage_key = 'appearance_on_materials'
            
            if storage_key not in pattern['visual_characteristics']:
                pattern['visual_characteristics'][storage_key] = {}
            
            # Add results
            for target_key, result in targets.items():
                # Remove [CATEGORY] prefix if present
                clean_key = target_key.replace('[CATEGORY]', '').lower()
                pattern['visual_characteristics'][storage_key][clean_key] = result
        
        # Save
        self.save_contaminants(contam_data)
        print("   ✅ Saved to Contaminants.yaml")


def main():
    parser = argparse.ArgumentParser(
        description="Batch visual appearance research with concurrent API calls"
    )
    parser.add_argument('--pattern', '-p', help="Single pattern ID to research")
    parser.add_argument('--patterns', '-P', help="Comma-separated pattern IDs")
    parser.add_argument('--all', '-a', action='store_true', help="Research all patterns")
    parser.add_argument('--categories-only', '-c', action='store_true',
                       help="Research at category level only (13 categories vs 159 materials = 92%% reduction)")
    parser.add_argument('--workers', '-w', type=int, default=3, 
                       help="Number of concurrent workers (default: 3, max: 5)")
    parser.add_argument('--save-interval', '-s', type=int, default=10,
                       help="Save to YAML every N materials (default: 10)")
    parser.add_argument('--force', '-f', action='store_true',
                       help="Re-research existing data")
    parser.add_argument('--dry-run', '-d', action='store_true',
                       help="Show what would be researched without doing it")
    
    args = parser.parse_args()
    
    # Determine patterns to research
    patterns = None
    if args.pattern:
        patterns = [args.pattern]
    elif args.patterns:
        patterns = [p.strip() for p in args.patterns.split(',')]
    elif not args.all:
        parser.print_help()
        print("\n❌ Specify --pattern, --patterns, or --all")
        sys.exit(1)
    
    # Create researcher and run
    researcher = BatchVisualAppearanceResearcher(
        max_workers=args.workers,
        save_interval=args.save_interval
    )
    
    results = researcher.run_batch(
        patterns=patterns,
        force=args.force,
        dry_run=args.dry_run,
        categories_only=args.categories_only
    )
    
    sys.exit(0 if results['failed'] == 0 else 1)


if __name__ == '__main__':
    main()
