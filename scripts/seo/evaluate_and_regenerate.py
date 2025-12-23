#!/usr/bin/env python3
"""
Evaluate generated SEO metadata quality and regenerate if needed.
Runs as batch job without confirmations.

Quality Criteria:
- Title: 50-55 chars
- Description: 155-160 chars  
- Contains specific metrics (%, nm, W)
- No forbidden phrases ("optimized laser parameters", "effective cleaning")
- Material-specific (not generic)
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import re

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from export.generation.seo_metadata_generator import SEOMetadataGenerator


class SEOQualityEvaluator:
    """Evaluate and fix SEO metadata quality."""
    
    FORBIDDEN_PHRASES = [
        'optimized laser parameters',
        'effective cleaning',
        'complete guide',
        'comprehensive',
        'various applications',
        'industrial applications'
    ]
    
    def __init__(self):
        self.materials_path = project_root / "data" / "materials" / "Materials.yaml"
        self.issues_found = []
        self.regenerated = 0
        
    def evaluate_material(self, name: str, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Evaluate a single material's SEO metadata. Returns (passed, issues)."""
        issues = []
        
        title = data.get('page_title', '')
        desc = data.get('meta_description', '')
        
        # Check title length
        if len(title) < 50 or len(title) > 55:
            issues.append(f"Title length {len(title)} (need 50-55)")
        
        # Check description length
        if len(desc) < 155 or len(desc) > 160:
            issues.append(f"Description length {len(desc)} (need 155-160)")
        
        # Check for forbidden phrases
        desc_lower = desc.lower()
        for phrase in self.FORBIDDEN_PHRASES:
            if phrase in desc_lower:
                issues.append(f"Contains forbidden phrase: '{phrase}'")
        
        # Check for specific metrics
        has_metrics = False
        if re.search(r'\d+%', desc):  # percentage
            has_metrics = True
        if re.search(r'\d+nm', desc):  # wavelength
            has_metrics = True
        if re.search(r'\d+-\d+W', desc):  # power range
            has_metrics = True
        
        if not has_metrics and len(desc) > 100:
            issues.append("Missing specific metrics (%, nm, W)")
        
        return len(issues) == 0, issues
    
    def regenerate_with_prompts(self):
        """Regenerate all materials using AI prompts with actual data."""
        print("\n" + "="*80)
        print("🔄 REGENERATING SEO METADATA WITH AI PROMPTS")
        print("="*80)
        
        data = yaml.safe_load(open(self.materials_path))
        materials = data.get('materials', {})
        
        generator = SEOMetadataGenerator({'page_type': 'material'})
        
        total = len(materials)
        passed = 0
        failed = 0
        
        for i, (slug, material_data) in enumerate(materials.items(), 1):
            name = material_data.get('name', slug)
            
            # Extract properties for context
            props = material_data.get('properties', {})
            settings = material_data.get('machine_settings', {})
            
            # Build rich frontmatter
            frontmatter = {
                'name': name,
                'category': material_data.get('category'),
                'subcategory': material_data.get('subcategory'),
                'properties': props,
                'machine_settings': settings,
            }
            
            try:
                result = generator.generate(frontmatter)
                
                if 'page_title' in result and 'meta_description' in result:
                    material_data['page_title'] = result['page_title']
                    material_data['meta_description'] = result['meta_description']
                    
                    # Evaluate quality
                    is_passing, issues = self.evaluate_material(name, material_data)
                    
                    if is_passing:
                        passed += 1
                        status = "✅"
                    else:
                        failed += 1
                        status = "⚠️"
                        self.issues_found.append((name, issues))
                    
                    if i % 10 == 0 or not is_passing:
                        print(f"{status} [{i}/{total}] {name}: "
                              f"T:{len(result['page_title'])}c D:{len(result['meta_description'])}c")
                        if issues:
                            print(f"    Issues: {', '.join(issues[:2])}")
                
            except Exception as e:
                failed += 1
                print(f"❌ [{i}/{total}] {name}: Error - {e}")
        
        # Save
        yaml.dump(data, open(self.materials_path, 'w'), 
                  allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        print(f"\n📊 Results: {passed} passed, {failed} failed/warning out of {total}")
        
        return passed, failed
    
    def print_summary(self):
        """Print summary of issues found."""
        if not self.issues_found:
            print("\n✅ All SEO metadata meets quality standards!")
            return
        
        print(f"\n⚠️  Found {len(self.issues_found)} materials with issues:")
        print("\nTop 10 issues:")
        for name, issues in self.issues_found[:10]:
            print(f"\n  {name}:")
            for issue in issues:
                print(f"    - {issue}")


def main():
    print("\n" + "="*80)
    print("📊 SEO METADATA QUALITY EVALUATION & REGENERATION")
    print("="*80)
    
    evaluator = SEOQualityEvaluator()
    
    # Regenerate all with improved logic
    passed, failed = evaluator.regenerate_with_prompts()
    
    # Print summary
    evaluator.print_summary()
    
    print("\n" + "="*80)
    print(f"✅ COMPLETE: {passed} passed, {failed} need review")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
