#!/usr/bin/env python3
"""
Super-Batched Visual Appearance Research using OpenAI

Batches ALL 13 categories into a single API call per pattern.
Result: 100 API calls instead of 1,298 (92% reduction)

Usage:
    python3 scripts/research/batch_visual_openai.py --all
    python3 scripts/research/batch_visual_openai.py --pattern rust-oxidation
    python3 scripts/research/batch_visual_openai.py --all --dry-run
"""

import os
import sys
import json
import yaml
import time
import argparse
from pathlib import Path
from datetime import datetime
from openai import OpenAI

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load .env
env_file = project_root / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value.strip('"').strip("'")

# Categories to research
CATEGORIES = [
    'metal', 'wood', 'stone', 'glass', 'ceramic', 'plastic',
    'composite', 'rubber', 'fabric', 'concrete', 'mineral',
    'semiconductor', 'specialty'
]

# Category example materials for context
CATEGORY_EXAMPLES = {
    'metal': 'Aluminum, Steel, Copper, Brass',
    'wood': 'Oak, Pine, Maple, Walnut',
    'stone': 'Granite, Marble, Limestone, Slate',
    'glass': 'Soda-lime glass, Borosilicate, Crystal',
    'ceramic': 'Porcelain, Stoneware, Terracotta',
    'plastic': 'ABS, PVC, Polycarbonate, Acrylic',
    'composite': 'Fiberglass, Carbon fiber, Kevlar',
    'rubber': 'Natural rubber, Silicone, Neoprene',
    'fabric': 'Cotton, Polyester, Nylon, Canvas',
    'concrete': 'Portland cement, Reinforced concrete',
    'mineral': 'Calcium carbite, Silica, Ite minerals',
    'semiconductor': 'Silicon, Germanium, GaAs',
    'specialty': 'Aerogel, Graphene, Advanced alloys'
}

# Fields to research per category
FIELDS = [
    'description',
    'color_variations', 
    'texture_details',
    'common_patterns',
    'distribution_patterns',
    'coverage_ranges',
    'edge_center_behavior',
    'gravity_influence',
    'geometry_effects'
]


class SuperBatchResearcher:
    """Research visual appearance for ALL categories in one API call per pattern."""
    
    def __init__(self, rate_limit: int = 20):
        """Initialize with OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        self.client = OpenAI(api_key=api_key)
        self.rate_limit = rate_limit
        self.min_delay = 60.0 / rate_limit
        self.last_request_time = 0
        
        # Paths
        self.contaminants_file = project_root / 'data' / 'contaminants' / 'Contaminants.yaml'
        
        # Stats
        self.completed = 0
        self.failed = 0
        self.start_time = None
        
        print("🚀 Super-Batch Researcher initialized (OpenAI)")
        print(f"   Model: gpt-4o-mini")
        print(f"   Rate limit: {rate_limit} requests/minute")
        print(f"   Batching: ALL {len(CATEGORIES)} categories per request")
        print()
    
    def load_data(self) -> dict:
        """Load contaminants data."""
        print("📂 Loading data...")
        with open(self.contaminants_file) as f:
            return yaml.safe_load(f)
    
    def get_patterns_to_research(self, data: dict, pattern_filter: str = None) -> list:
        """Get list of patterns that need research."""
        patterns = []
        
        for pattern_id, pattern_data in data.get('contamination_patterns', {}).items():
            if pattern_filter and pattern_id != pattern_filter:
                continue
            
            pattern_name = pattern_data.get('name', pattern_id)
            
            # Check which categories need research
            visual = pattern_data.get('visual_characteristics', {})
            existing = visual.get('appearance_on_categories', {})
            
            missing_categories = [c for c in CATEGORIES if c not in existing or not existing.get(c)]
            
            if missing_categories:
                patterns.append({
                    'id': pattern_id,
                    'name': pattern_name,
                    'missing': missing_categories
                })
        
        return patterns
    
    def build_super_prompt(self, pattern_name: str, categories: list) -> str:
        """Build a prompt that researches ALL categories at once."""
        
        category_sections = []
        for cat in categories:
            examples = CATEGORY_EXAMPLES.get(cat, cat)
            category_sections.append(f'- **{cat}** (e.g., {examples})')
        
        prompt = f"""You are an expert in industrial contamination and material science.

Research how "{pattern_name}" contamination appears visually on different material categories.

For EACH of these {len(categories)} material categories:
{chr(10).join(category_sections)}

Provide these details:
1. **description**: Overall visual appearance (concise)
2. **color_variations**: Range of colors observed
3. **texture_details**: Surface texture when contaminated
4. **common_patterns**: Typical visual patterns (spots, streaks, films, etc.)
5. **distribution_patterns**: How it spreads across the surface
6. **coverage_ranges**: Light (<30%), moderate (30-60%), heavy (>60%)
7. **edge_center_behavior**: Does it prefer edges, centers, or uniform?
8. **gravity_influence**: How gravity affects distribution
9. **geometry_effects**: How surface geometry affects appearance

Return as JSON with this EXACT structure:
{{
  "category_name": {{
    "description": "...",
    "color_variations": "...",
    "texture_details": "...",
    "common_patterns": "...",
    "distribution_patterns": "...",
    "coverage_ranges": "...",
    "edge_center_behavior": "...",
    "gravity_influence": "...",
    "geometry_effects": "..."
  }},
  ... (repeat for each category)
}}

Be specific and technical. Focus on visual characteristics relevant to laser cleaning applications."""

        return prompt
    
    def research_pattern(self, pattern_id: str, pattern_name: str, categories: list) -> dict:
        """Research all categories for one pattern in a single API call."""
        
        # Rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        
        prompt = self.build_super_prompt(pattern_name, categories)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in material science and industrial contamination. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            self.last_request_time = time.time()
            
            # Parse response
            content = response.choices[0].message.content
            result = json.loads(content)
            
            return result
            
        except Exception as e:
            print(f"   ❌ API Error: {e}")
            return None
    
    def save_results(self, data: dict, pattern_id: str, results: dict):
        """Save results to Contaminants.yaml."""
        
        # Ensure structure exists
        if 'contamination_patterns' not in data:
            data['contamination_patterns'] = {}
        if pattern_id not in data['contamination_patterns']:
            data['contamination_patterns'][pattern_id] = {}
        
        pattern = data['contamination_patterns'][pattern_id]
        
        if 'visual_characteristics' not in pattern:
            pattern['visual_characteristics'] = {}
        if 'appearance_on_categories' not in pattern['visual_characteristics']:
            pattern['visual_characteristics']['appearance_on_categories'] = {}
        
        # Add results for each category
        for category, fields in results.items():
            if category.lower() in CATEGORIES:
                pattern['visual_characteristics']['appearance_on_categories'][category.lower()] = fields
        
        # Save atomically
        temp_file = self.contaminants_file.with_suffix('.yaml.tmp')
        with open(temp_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, width=120)
        temp_file.rename(self.contaminants_file)
    
    def run(self, pattern_filter: str = None, dry_run: bool = False):
        """Run the super-batch research."""
        
        data = self.load_data()
        patterns = self.get_patterns_to_research(data, pattern_filter)
        
        if not patterns:
            print("✅ All patterns already have complete category data!")
            return
        
        total_patterns = len(patterns)
        total_categories = sum(len(p['missing']) for p in patterns)
        
        print(f"\n📊 Research Tasks:")
        print(f"   Patterns to research: {total_patterns}")
        print(f"   Total categories: {total_categories}")
        print(f"   API calls needed: {total_patterns} (super-batched)")
        print(f"   Estimated time: {total_patterns * self.min_delay / 60:.1f} minutes")
        print()
        
        if dry_run:
            print("🔍 DRY RUN - Would research:")
            for p in patterns[:20]:
                print(f"   {p['id']}: {len(p['missing'])} categories ({', '.join(p['missing'][:3])}...)")
            if len(patterns) > 20:
                print(f"   ... and {len(patterns) - 20} more patterns")
            return
        
        self.start_time = time.time()
        
        for i, pattern in enumerate(patterns, 1):
            pattern_id = pattern['id']
            pattern_name = pattern['name']
            missing = pattern['missing']
            
            # Progress
            elapsed = time.time() - self.start_time
            rate = i / elapsed if elapsed > 0 else 0
            remaining = (total_patterns - i) / rate if rate > 0 else 0
            
            print(f"[{i}/{total_patterns}] {pattern_name} ({len(missing)} categories)")
            
            result = self.research_pattern(pattern_id, pattern_name, missing)
            
            if result:
                self.save_results(data, pattern_id, result)
                self.completed += 1
                categories_done = len([k for k in result.keys() if k.lower() in CATEGORIES])
                print(f"   ✅ Saved {categories_done} categories ({rate:.2f}/s, ~{remaining/60:.1f}m remaining)")
            else:
                self.failed += 1
                print(f"   ❌ Failed")
        
        # Summary
        elapsed = time.time() - self.start_time
        print()
        print("=" * 60)
        print(f"📊 COMPLETE")
        print(f"   Patterns processed: {self.completed}")
        print(f"   Failed: {self.failed}")
        print(f"   Total time: {elapsed/60:.1f} minutes")
        print(f"   Average rate: {self.completed/elapsed:.2f} patterns/second")


def main():
    parser = argparse.ArgumentParser(description='Super-Batch Visual Appearance Research (OpenAI)')
    parser.add_argument('--all', action='store_true', help='Research all patterns')
    parser.add_argument('--pattern', type=str, help='Research specific pattern ID')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be researched')
    parser.add_argument('--rate', type=int, default=20, help='Requests per minute (default: 20)')
    
    args = parser.parse_args()
    
    if not args.all and not args.pattern:
        parser.print_help()
        print("\nError: Must specify --all or --pattern")
        sys.exit(1)
    
    researcher = SuperBatchResearcher(rate_limit=args.rate)
    researcher.run(pattern_filter=args.pattern, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
