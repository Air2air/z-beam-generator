#!/usr/bin/env python3
"""
Winston AI Content Audit

Validates existing Materials.yaml content against Winston API.
Reports human scores and identifies content that needs regeneration.

Usage:
    python3 scripts/validation/winston_audit.py              # Audit all materials
    python3 scripts/validation/winston_audit.py --material "Aluminum"  # Specific material
    python3 scripts/validation/winston_audit.py --component caption   # Specific component
    python3 scripts/validation/winston_audit.py --threshold 50        # Custom threshold
"""

import argparse
import sys
import yaml
from pathlib import Path
from typing import Dict, List
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.api.client_factory import create_api_client


class WinstonAuditor:
    """Audit Materials.yaml content against Winston AI detection"""
    
    def __init__(self, threshold: float = 70.0):
        """
        Initialize auditor.
        
        Args:
            threshold: Minimum human score threshold (0-100)
        """
        self.threshold = threshold
        self.winston = create_api_client('winston')
        self.materials_file = Path(__file__).parent.parent.parent / 'data' / 'materials' / 'Materials.yaml'
        
    def load_materials(self) -> Dict:
        """Load Materials.yaml"""
        with open(self.materials_file, 'r') as f:
            return yaml.safe_load(f)
    
    def audit_material(self, material_name: str, material_data: Dict, components: List[str] = None) -> Dict:
        """
        Audit a single material's content.
        
        Args:
            material_name: Material name
            material_data: Material data from YAML
            components: List of components to audit (None = all)
            
        Returns:
            Audit results dict
        """
        results = {
            'material': material_name,
            'components': {},
            'total_checked': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'credits_used': 0
        }
        
        # Define which fields to check - ONLY TEXT FIELDS
        component_fields = {
            'subtitle': 'subtitle',
            'micro': 'micro',
            'faq': 'faq'  # Will check all FAQ entries
        }
        
        # Filter by requested components
        if components:
            component_fields = {k: v for k, v in component_fields.items() if k in components}
        
        for component_type, field_name in component_fields.items():
            if field_name not in material_data:
                continue
                
            content = material_data[field_name]
            
            # ONLY process if content is string or list (text-based)
            if not isinstance(content, (str, list)):
                results['skipped'] += 1
                continue
            
            # Handle FAQ (list of Q&A)
            if component_type == 'faq' and isinstance(content, list):
                for i, faq_item in enumerate(content):
                    # ONLY process text-based FAQ entries
                    if not isinstance(faq_item, dict):
                        results['skipped'] += 1
                        continue
                    
                    answer = faq_item.get('answer', '')
                    
                    # ONLY check if answer is a string
                    if not isinstance(answer, str):
                        results['skipped'] += 1
                        continue
                    
                    if len(answer) >= 300:  # Winston minimum
                        result = self._check_content(answer, f"{component_type}_{i+1}")
                        results['components'][f'faq_{i+1}'] = result
                        results['total_checked'] += 1
                        if result['passed']:
                            results['passed'] += 1
                        else:
                            results['failed'] += 1
                        results['credits_used'] += result.get('credits_used', 0)
                    else:
                        results['skipped'] += 1
                continue
            
            # Handle text content - ONLY strings
            if isinstance(content, str):
                if len(content) >= 300:  # Winston minimum
                    result = self._check_content(content, component_type)
                    results['components'][component_type] = result
                    results['total_checked'] += 1
                    if result['passed']:
                        results['passed'] += 1
                    else:
                        results['failed'] += 1
                    results['credits_used'] += result.get('credits_used', 0)
                else:
                    results['skipped'] += 1
            else:
                # Not a text field, skip it
                results['skipped'] += 1
        
        return results
    
    def _check_content(self, text: str, component_name: str) -> Dict:
        """
        Check single piece of content.
        
        Args:
            text: Content to check
            component_name: Component identifier
            
        Returns:
            Result dict with scores and pass/fail
        """
        print(f"  🔍 Checking {component_name} ({len(text)} chars)...")
        
        try:
            result = self.winston.detect_ai_content(text)
            
            if result['success']:
                human_score = result['human_score']
                passed = human_score >= self.threshold
                
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"    {status} - Human: {human_score:.1f}%, AI: {result['ai_score']:.3f}")
                
                return {
                    'passed': passed,
                    'human_score': human_score,
                    'ai_score': result['ai_score'],
                    'credits_used': result.get('credits_used', 0),
                    'text_preview': text[:100] + '...' if len(text) > 100 else text
                }
            else:
                print(f"    ⚠️ SKIP - {result['error']}")
                return {
                    'passed': None,
                    'error': result['error'],
                    'text_preview': text[:100] + '...' if len(text) > 100 else text
                }
        except Exception as e:
            print(f"    💥 ERROR - {str(e)}")
            return {
                'passed': None,
                'error': str(e),
                'text_preview': text[:100] + '...' if len(text) > 100 else text
            }
    
    def audit_all(self, material_filter: str = None, component_filter: List[str] = None) -> Dict:
        """
        Audit all materials or filtered subset.
        
        Args:
            material_filter: Single material name to audit
            component_filter: List of components to check
            
        Returns:
            Overall audit results
        """
        materials = self.load_materials()
        
        overall = {
            'materials_checked': 0,
            'total_components': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'credits_used': 0,
            'failures': []
        }
        
        for material_name, material_data in materials.items():
            # Skip if not matching filter
            if material_filter and material_name != material_filter:
                continue
            
            print(f"\n{'='*60}")
            print(f"📦 Material: {material_name}")
            print(f"{'='*60}")
            
            result = self.audit_material(material_name, material_data, component_filter)
            
            overall['materials_checked'] += 1
            overall['total_components'] += result['total_checked']
            overall['passed'] += result['passed']
            overall['failed'] += result['failed']
            overall['skipped'] += result['skipped']
            overall['credits_used'] += result['credits_used']
            
            # Track failures for regeneration recommendations
            for comp_name, comp_result in result['components'].items():
                if comp_result.get('passed') == False:
                    overall['failures'].append({
                        'material': material_name,
                        'component': comp_name,
                        'human_score': comp_result['human_score'],
                        'text_preview': comp_result['text_preview']
                    })
            
            # Rate limiting - small delay between materials
            if overall['materials_checked'] % 5 == 0:
                print("\n⏸️  Rate limiting pause (2s)...")
                time.sleep(2)
        
        return overall
    
    def print_report(self, results: Dict):
        """Print formatted audit report"""
        print("\n" + "="*60)
        print("📊 WINSTON AI AUDIT REPORT")
        print("="*60)
        print(f"\n📈 Summary:")
        print(f"  Materials Checked: {results['materials_checked']}")
        print(f"  Components Checked: {results['total_components']}")
        print(f"  Passed (≥{self.threshold}% human): {results['passed']}")
        print(f"  Failed (<{self.threshold}% human): {results['failed']}")
        print(f"  Skipped (too short): {results['skipped']}")
        print(f"  Credits Used: {results['credits_used']}")
        
        if results['passed'] + results['failed'] > 0:
            pass_rate = results['passed'] / (results['passed'] + results['failed']) * 100
            print(f"  Pass Rate: {pass_rate:.1f}%")
        
        if results['failures']:
            print(f"\n❌ Failed Content ({len(results['failures'])} items):")
            print(f"{'='*60}")
            for failure in results['failures']:
                print(f"\n  Material: {failure['material']}")
                print(f"  Component: {failure['component']}")
                print(f"  Human Score: {failure['human_score']:.1f}%")
                print(f"  Preview: {failure['text_preview']}")
                print(f"  → Recommend: python3 run.py --{failure['component']} \"{failure['material']}\"")
        else:
            print("\n✅ All content passed Winston AI detection!")


def main():
    parser = argparse.ArgumentParser(description='Audit Materials.yaml content with Winston AI')
    parser.add_argument('--material', help='Specific material to audit')
    parser.add_argument('--component', choices=['subtitle', 'micro', 'faq'], 
                       help='Specific component type to audit')
    parser.add_argument('--threshold', type=float, default=70.0,
                       help='Minimum human score threshold (0-100, default: 70)')
    args = parser.parse_args()
    
    print("🚀 Winston AI Content Auditor")
    print(f"Threshold: {args.threshold}% human score")
    if args.material:
        print(f"Filter: Material = {args.material}")
    if args.component:
        print(f"Filter: Component = {args.component}")
    
    auditor = WinstonAuditor(threshold=args.threshold)
    
    component_filter = [args.component] if args.component else None
    results = auditor.audit_all(material_filter=args.material, component_filter=component_filter)
    
    auditor.print_report(results)


if __name__ == '__main__':
    main()
