#!/usr/bin/env python3
"""
Persist Contamination Feedback to Contaminants.yaml

Saves material-specific image generation feedback directly into the contaminant
data source, making it available for future prompt building.

This creates/updates an `image_generation_feedback` section under each contamination
pattern with material-specific notes for better image generation.

Usage:
    python3 persist_contamination_feedback.py --pattern copper-patina --material "Aluminum Bronze" \
        --feedback "NO thick/chunky buildup. Verdigris should be thin blue-green film, subtle patina"
    
    python3 persist_contamination_feedback.py --pattern rust-oxidation --material "Steel" \
        --feedback "Orange-brown streaks, flaky texture, heavy in marine contexts"

    python3 persist_contamination_feedback.py --list-patterns  # Show all patterns
    python3 persist_contamination_feedback.py --show copper-patina  # Show pattern's feedback

Author: AI Assistant
Date: November 30, 2025
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import yaml

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# Custom YAML representer for multiline strings
def str_representer(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)


class ContaminationFeedbackPersister:
    """Persists material-specific image generation feedback to Contaminants.yaml."""
    
    def __init__(self):
        self.contaminants_path = PROJECT_ROOT / 'data' / 'contaminants' / 'Contaminants.yaml'
        self._data = None
    
    @property
    def data(self) -> Dict[str, Any]:
        """Lazy-load contaminants data."""
        if self._data is None:
            with open(self.contaminants_path, 'r') as f:
                self._data = yaml.safe_load(f)
        return self._data
    
    def _save_data(self):
        """Save data back to YAML file."""
        yaml.add_representer(str, str_representer)
        with open(self.contaminants_path, 'w') as f:
            yaml.dump(self._data, f, default_flow_style=False, allow_unicode=True, 
                     sort_keys=False, width=120)
    
    def list_patterns(self) -> List[str]:
        """List all contamination pattern IDs."""
        patterns = self.data.get('contamination_patterns', {})
        return sorted(patterns.keys())
    
    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific contamination pattern."""
        patterns = self.data.get('contamination_patterns', {})
        return patterns.get(pattern_id)
    
    def get_feedback_for_pattern(self, pattern_id: str) -> Dict[str, Dict[str, str]]:
        """Get all material-specific feedback for a pattern."""
        pattern = self.get_pattern(pattern_id)
        if not pattern:
            return {}
        return pattern.get('image_generation_feedback', {})
    
    def add_feedback(
        self,
        pattern_id: str,
        material: str,
        feedback: str,
        category: str = 'general'
    ) -> bool:
        """
        Add material-specific image generation feedback to a contamination pattern.
        
        Args:
            pattern_id: The contamination pattern ID (e.g., 'copper-patina', 'rust-oxidation')
            material: The material name (e.g., 'Aluminum Bronze', 'Steel')
            feedback: The image generation feedback/notes
            category: Feedback category (appearance, thickness, color, distribution, general)
            
        Returns:
            True if feedback was added successfully
        """
        patterns = self.data.get('contamination_patterns', {})
        
        if pattern_id not in patterns:
            print(f"❌ Pattern '{pattern_id}' not found in Contaminants.yaml")
            print(f"   Available patterns: {', '.join(sorted(patterns.keys())[:10])}...")
            return False
        
        pattern = patterns[pattern_id]
        
        # Initialize feedback section if not exists
        if 'image_generation_feedback' not in pattern:
            pattern['image_generation_feedback'] = {}
        
        # Initialize material entry if not exists
        material_key = material.lower().replace(' ', '_')
        if material_key not in pattern['image_generation_feedback']:
            pattern['image_generation_feedback'][material_key] = {
                'material_name': material,
                'notes': {},
                'last_updated': None
            }
        
        # Add/update feedback
        mat_feedback = pattern['image_generation_feedback'][material_key]
        mat_feedback['notes'][category] = feedback
        mat_feedback['last_updated'] = datetime.utcnow().isoformat()
        
        # Save to file
        self._save_data()
        return True
    
    def get_combined_feedback(self, pattern_id: str, material: str) -> str:
        """Get all feedback for a pattern+material combination as a single string."""
        feedback_dict = self.get_feedback_for_pattern(pattern_id)
        material_key = material.lower().replace(' ', '_')
        
        if material_key not in feedback_dict:
            return ""
        
        mat_feedback = feedback_dict[material_key]
        notes = mat_feedback.get('notes', {})
        
        if not notes:
            return ""
        
        # Combine all notes into a single string
        parts = []
        for category, note in notes.items():
            if note:
                parts.append(f"[{category.upper()}] {note}")
        
        return " | ".join(parts)


def main():
    parser = argparse.ArgumentParser(
        description="Persist material-specific contamination feedback to Contaminants.yaml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Add feedback for copper patina on Aluminum Bronze:
    python3 persist_contamination_feedback.py --pattern copper-patina --material "Aluminum Bronze" \\
        --feedback "Thin blue-green verdigris film, NOT thick/chunky deposits"
        
  Add categorized feedback:
    python3 persist_contamination_feedback.py --pattern rust-oxidation --material Steel \\
        --category thickness --feedback "Heavy orange-brown flaky rust in marine contexts"
        
  List all patterns:
    python3 persist_contamination_feedback.py --list-patterns
    
  Show feedback for a pattern:
    python3 persist_contamination_feedback.py --show copper-patina

Feedback Categories: appearance, thickness, color, distribution, general
"""
    )
    
    # Action flags
    parser.add_argument('--list-patterns', action='store_true', 
                       help='List all contamination pattern IDs')
    parser.add_argument('--show', type=str, metavar='PATTERN',
                       help='Show all feedback for a specific pattern')
    
    # Feedback input
    parser.add_argument('--pattern', '-p', type=str,
                       help='Contamination pattern ID (e.g., copper-patina)')
    parser.add_argument('--material', '-m', type=str,
                       help='Material name (e.g., Aluminum Bronze)')
    parser.add_argument('--feedback', '-f', type=str,
                       help='Image generation feedback/notes')
    parser.add_argument('--category', '-c', type=str, default='general',
                       choices=['appearance', 'thickness', 'color', 'distribution', 'general'],
                       help='Feedback category (default: general)')
    
    args = parser.parse_args()
    
    persister = ContaminationFeedbackPersister()
    
    # Handle list patterns
    if args.list_patterns:
        patterns = persister.list_patterns()
        print(f"\n📋 CONTAMINATION PATTERNS ({len(patterns)} total)")
        print("=" * 70)
        for i, p in enumerate(patterns, 1):
            pattern_data = persister.get_pattern(p)
            name = pattern_data.get('name', p) if pattern_data else p
            feedback_count = len(persister.get_feedback_for_pattern(p))
            feedback_marker = f" 📝({feedback_count})" if feedback_count > 0 else ""
            print(f"  {i:3}. {p:<35} {name[:30]}{feedback_marker}")
        print("=" * 70)
        return
    
    # Handle show pattern feedback
    if args.show:
        pattern_id = args.show
        pattern = persister.get_pattern(pattern_id)
        
        if not pattern:
            print(f"❌ Pattern '{pattern_id}' not found")
            return
        
        feedback = persister.get_feedback_for_pattern(pattern_id)
        
        print(f"\n📋 FEEDBACK FOR: {pattern_id}")
        print(f"   Name: {pattern.get('name', 'N/A')}")
        print(f"   Valid Materials: {', '.join(pattern.get('valid_materials', []))}")
        print("=" * 70)
        
        if not feedback:
            print("\n   No material-specific feedback recorded yet.")
        else:
            for mat_key, mat_data in feedback.items():
                print(f"\n   🔹 {mat_data.get('material_name', mat_key)}")
                print(f"      Updated: {mat_data.get('last_updated', 'N/A')}")
                notes = mat_data.get('notes', {})
                for cat, note in notes.items():
                    print(f"      [{cat.upper()}] {note}")
        
        print("\n" + "=" * 70)
        return
    
    # Adding feedback requires pattern, material, and feedback
    if not all([args.pattern, args.material, args.feedback]):
        parser.error("--pattern, --material, and --feedback are required when adding feedback")
    
    # Add the feedback
    success = persister.add_feedback(
        pattern_id=args.pattern,
        material=args.material,
        feedback=args.feedback,
        category=args.category
    )
    
    if success:
        print("\n✅ FEEDBACK PERSISTED TO Contaminants.yaml")
        print("=" * 70)
        print(f"   Pattern: {args.pattern}")
        print(f"   Material: {args.material}")
        print(f"   Category: {args.category}")
        print(f"   Feedback: {args.feedback}")
        print("\n   This feedback will be available for future image generation.")
        print(f"   View with: python3 persist_contamination_feedback.py --show {args.pattern}")
        print("=" * 70)


if __name__ == "__main__":
    main()
